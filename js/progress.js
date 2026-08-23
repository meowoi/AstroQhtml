/* ============================================================
   progress.js — BÁO VIỆC ĐÃ LÀM lên server, và giữ một bản sao trong máy.

   Trang nào cũng nạp được (nhẹ, không phụ thuộc gì ngoài js/ui-common.js):
     <script src="js/progress.js"></script>

   Báo một việc đã làm — gọi ở đúng chỗ đã có sẵn "chốt lượt" của từng trang:
     AstroQProgress.quiz({ correct:4, total:5, meteors:40 });
     AstroQProgress.game({ game:"dodge", score:120, seconds:38, meteors:3 });
     AstroQProgress.lesson("ten-bai");
     AstroQProgress.planet("mars");

   Đọc lại để vẽ trang:
     AstroQProgress.load()   → Promise<{ ok, source:"server"|"local", data }>
     AstroQProgress.local()  → bản sao trong máy, đọc ngay không chờ mạng

   BỐN ĐIỀU QUAN TRỌNG
   ─────────────────────────────────────────────────────────────
   1. **Client KHÔNG tính XP, KHÔNG tự mở huy hiệu, KHÔNG quyết số tiền.** Chỉ gửi
      "đã làm gì"; server (Services/Achievements.cs, Services/Wallet.cs) quyết cộng
      bao nhiêu XP, mở huy hiệu nào, trừ phí bao nhiêu. Bản sao trong máy vì thế
      chỉ có BỘ ĐẾM THÔ, không có xp/badges tự tính.
   2. **Không bao giờ ném lỗi và không bao giờ chặn giao diện.** Game đang chạy
      thì việc nộp kết quả không được phép làm treo màn hình kết thúc lượt —
      gọi rồi đi tiếp, mạng hỏng thì thôi.
   3. **Mất mạng / chưa đăng nhập → xếp hàng chờ** trong localStorage; lần sau
      mở trang có phiên đăng nhập thì tự gửi lại (`flush()` chạy khi nạp file này).
   4. **Mỗi việc có `opId` riêng.** Gửi lại từ hàng chờ mà server đã xử lý xong
      (phản hồi mất giữa đường) thì không được cộng tiền / trừ phí lần hai — server
      dedupe theo `opId`. **Sinh opId MỘT LẦN lúc tạo việc**, không phải lúc gửi:
      sinh lúc gửi thì mỗi lần thử lại là một op mới và mất hết ý nghĩa.

   Số dư ví trả về từ mọi lời gọi được đẩy thẳng vào `Economy.setFromServer()` —
   đó là chỗ duy nhất chữa lại sai lệch giữa cache và ví thật.
   ============================================================ */
(function (global) {
  "use strict";

  var LS_LOCAL = "astroq-progress";        // bản sao bộ đếm để vẽ khi offline
  var LS_QUEUE = "astroq-progress-queue";  // việc chưa gửi được
  var MAX_QUEUE = 40;                      // đủ cho vài ngày offline, không phình vô hạn

  /* ⚠️⚠️ SỐ VIỆC ĐÃ BỊ HÀNG CHỜ VỨT ĐI (thêm 13/08/2026).
     `enqueue()` cắt bớt việc CŨ NHẤT khi vượt `MAX_QUEUE` — cần thiết (localStorage
     có hạn, và một hàng chờ phình vô hạn thì lần gửi lại nào cũng chậm hơn lần
     trước), nhưng trước hôm nay nó cắt **trong im lặng**: trẻ chơi 60 lượt lúc mất
     phiên thì 20 lượt đầu biến mất mà không một chỗ nào trong app nói ra.
     Đếm lại được thì `dashboard.html` mới nói thật được là *bao nhiêu* việc đã mất.
     ⚠️ ĐỪNG "chữa" bằng cách bỏ trần: cái mất khi đó là **việc MỚI** (ghi
        localStorage hỏng vì đầy) — tức mất theo hướng tệ hơn, và cũng im lặng. */
  var LS_DROP = "astroq-progress-dropped";

  /* ⚠️ DANH SÁCH BƯỚC ĐÃ XONG — CHỈ ĐỂ BIẾT VÀO CHƠI TIẾP TỪ ĐÂU, KHÔNG PHẢI THƯỞNG.
     Điều 1 ở đầu file vẫn nguyên: ở đây **không** lưu meteors/xp/huy hiệu nào, chỉ
     lưu id bước + tổng số bước + cờ "xong cả nhiệm vụ", và chỉ ghi từ CÂU TRẢ LỜI
     CỦA SERVER (không bao giờ ghi từ việc còn nằm trong hàng chờ). Nên nó không thể
     làm trang hiện một phần thưởng chưa có thật — đúng lý do khiến `bumpLocal()` cố
     ý bỏ qua `type:"mission"`.

     ⚠️ VÌ SAO PHẢI CÓ, KHÔNG PHẢI TỐI ƯU: `mission-earth.html` **cố ý không nạp**
     `js/firebase-auth.js` (check_pages mục [4]) nên tự nó KHÔNG có token để hỏi
     `GET /me/missions` — mà không hỏi được thì nó luôn mở lại từ bước 1, kể cả khi
     `missions.html` vừa hiện đúng chữ "Tiếp tục nhiệm vụ". Cầu nối: trang CÓ token
     (dashboard, missions) ghi cache; trang nhiệm vụ đọc. Đúng khuôn `astroq-route-gate`
     đã dùng cho `explorer.html`. */
  var LS_MSTEPS = "astroq-mission-steps";

  /* Tiến độ Trung Tâm Đào Tạo (thêm 14/08/2026).
     ⚠️ CẦU NỐI BẮT BUỘC, cùng lý do với LS_MSTEPS ở trên: `games.html` **cố ý
     không nạp** `js/firebase-auth.js` (SDK 64 KB gzip — trang này phải mượt vì
     nó là cửa vào 6 mini-game), nên tự nó KHÔNG có token để hỏi
     `GET /me/achievements`. Trang CÓ token (dashboard · profile · achievements)
     ghi cache, Sảnh đọc.
     ⚠️ CHỈ CHỨA trạng thái ĐẠT/CHƯA và số hiện tại — **không một con số mốc nào
     do client tự nghĩ ra**: `goal` cũng là số server trả về. Server giữ MỐC,
     client giữ TÊN (js/training.js).
     ⚠️ ĐÓNG DẤU `uid` — hai đứa trẻ dùng chung máy thì chứng chỉ của đứa trước
     không được hiện cho đứa sau. */
  var LS_TRAIN = "astroq-training";

  /* Cấp độ câu hỏi Quiz nên rút (thêm 19/08/2026 — "vai ②", độ khó tự điều chỉnh).
     ⚠️ CẦU NỐI BẮT BUỘC, cùng lý do với LS_MSTEPS và LS_TRAIN ở trên: `quiz.html`
        **cố ý không nạp** `js/firebase-auth.js` nên tự nó KHÔNG có token để hỏi
        `GET /me/profile`. Trang CÓ token (dashboard · profile · library) ghi cache,
        Quiz đọc.
     ⚠️ CHỈ CHỨA con số server trả về. **Client không được tự tính cấp độ** từ
        `quizAccuracy` — luật + các mốc nằm ở `Services/Adapt.cs` phía server, và
        có hai nơi tính là có hai câu trả lời khác nhau cho cùng một đứa trẻ (đúng
        cái giá `js/depth.js` đã trả).
     ⚠️ ĐÓNG DẤU `uid`: hai đứa trẻ dùng chung máy thì cấp độ của đứa trước không
        được quyết đề bài của đứa sau. Chưa đăng nhập (`uid` rỗng) cũng là một danh
        tính hợp lệ — trẻ chơi thử vẫn có cấp độ 1 và vẫn làm được bài.
     ⚠️ KHÔNG PHẢI HÀNG RÀO: sửa localStorage chỉ đổi ĐỘ KHÓ đề bài của chính mình,
        không mở khoá gì và không sinh thưởng — thưởng do server kẹp trần
        (`Wallet.AwardQuiz`). Nên ở đây không cần chống giả mạo. */
  var LS_QUIZLV = "astroq-quiz-lv";

  /* Số lượt Quiz còn lại HÔM NAY (thêm 19/08/2026 — hạn mức 5 lượt/ngày).
     ⚠️ CẦU NỐI BẮT BUỘC, cùng lý do với LS_QUIZLV ngay trên: `quiz.html` không có
        token nên không tự hỏi `/me/daily` được. Không có cache này thì trẻ chơi xong
        lượt thứ 6 mới phát hiện nó không được tính — mà lúc đó đã muộn.
     ⚠️ CHỈ CHỨA con số server trả về (`quizRoundsLeft`/`quizRoundsPerDay`). Client
        KHÔNG tự đếm: đếm ở hai nơi là hai câu trả lời khác nhau, và nơi sai sẽ là nơi
        nói với trẻ. Luật + con số ở `Services/QuizAccess.cs`.
     ⚠️ ĐÓNG DẤU `uid` + NGÀY. Hai đứa trẻ dùng chung máy thì hạn mức không được dùng
        chung; và cache của hôm qua phải tự hết hiệu lực, không thì sáng ra trẻ vẫn
        thấy "hết lượt". Ngày lấy theo giờ máy — chỉ để BỎ cache cũ, không phải để
        quyết hạn mức (server mới quyết, và nó dùng giờ Việt Nam).
     ⚠️ KHÔNG PHẢI HÀNG RÀO: xoá localStorage là chơi tiếp được. Hàng rào thật ở
        server — nó không tính, không thưởng, không ghi nhật ký. */
  var LS_QUIZLEFT = "astroq-quiz-left";

  /* Cấp độ + XP + bàn điều khiển của LƯỢT ĐỌC GẦN NHẤT (thêm 23/08/2026).
     ⚠️ ĐÂY LÀ CACHE ĐỂ VẼ SỚM, KHÔNG PHẢI CẦU NỐI GIỮA HAI TRANG như LS_MSTEPS /
        LS_TRAIN / LS_QUIZLV ở trên. Nó tồn tại vì một con số ĐO ĐƯỢC, không phải
        vì gọn code: trên đường 4G, `#xp-bar` và `#desk-float` của dashboard chỉ
        có số thật ở giây thứ **1,48**; vừa chơi game xong (hàng chờ 5 việc) thì
        **2,58**; 3G thì **2,60** (scratchpad/perf_dash_slow.py). Suốt khoảng đó
        thanh XP đứng ở 0% và vách khoang lái trống trơn — rồi nhảy một cái sang
        71%. Chuỗi gây ra nó là 5 chặng NỐI TIẾP nhau, không chặng nào bỏ được:
        parse xong 20 script → module `firebase-auth.js` chạy → tải SDK →
        `accounts:lookup` (Firebase xác thực phiên, 258ms) → `GET /me/achievements`
        (534ms). Không cache thì trẻ luôn phải xem hết cả 5 chặng đó.
     ⚠️ ĐÂY KHÔNG PHẢI SỐ BỊA — và đó là toàn bộ lý do nó được phép tồn tại cạnh
        khối chú thích "KHÔNG đoán, không bịa" ở dashboard.html. Nó là CHÍNH câu
        trả lời của server ở lượt vào trước, của CHÍNH đứa trẻ này (`uid` đóng dấu).
        Cùng khuôn `AstroQCos.absorb` đã dùng cho tông đèn buồng lái: *"áp tông từ
        cache LÚC NẠP nên buồng lái không nhấp một cái từ tông mặc định sang tông
        của trẻ"*. Chưa từng đọc được server → `known:false` → trang vẽ y như cũ
        (0% + vách trống), KHÔNG đoán một cấp nào.
     ⚠️ CÂU TRẢ LỜI CỦA SERVER LUÔN THẮNG. `renderStats()` chạy lại khi
        `achievements()` về, nên cache sai lệch (trẻ chơi ở máy khác) sống đúng
        một nhịp mạng rồi bị ghi đè — không có nhánh nào tin cache lâu hơn thế.
     ⚠️ ĐÓNG DẤU `uid`: hai đứa trẻ dùng chung máy thì cấp độ và mẫu vật của đứa
        trước không được hiện lên cho đứa sau, kể cả trong một nhịp mạng.
     ⚠️ KHÔNG PHẢI HÀNG RÀO: sửa localStorage chỉ đổi con số trẻ tự nhìn thấy
        trong ~1 giây; không mở khoá gì, không sinh thưởng, và nhịp mạng kế tiếp
        xoá sạch. Mẫu vật cũng vậy — `paintDesk` chỉ VẼ, điều kiện mở khoá do
        server giữ (Services/Specimens.cs). */
  var LS_HUD = "astroq-hud";

  /** Mã lượt duy nhất, sinh MỘT LẦN lúc tạo việc (xem điều 4 ở đầu file). */
  function newOpId() {
    try {
      if (global.crypto && global.crypto.randomUUID) return global.crypto.randomUUID();
    } catch (e) {}
    return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }

  /* ---------------- Bước nhiệm vụ đã xong (xem LS_MSTEPS) ---------------- */

  /** Ai đang dùng máy này. Rỗng = chưa đăng nhập. */
  function uidNow() {
    try {
      var u = global.AstroQ && global.AstroQ.getUser ? global.AstroQ.getUser() : null;
      return u && u.uid ? String(u.uid) : "";
    } catch (e) { return ""; }
  }

  /**
   * Rót khối `missions` của một câu trả lời server vào cache. Trả true nếu ghi được.
   * Gọi ở MỌI chỗ nhận được `data.missions` (`missions()`, báo bước xong, gửi lại
   * hàng chờ) — thiếu một chỗ là cache cũ hơn server và trẻ phải chơi lại một bước
   * nó vừa làm.
   *
   * ⚠️ GỘP theo từng nhiệm vụ, không ghi đè cả bảng: `POST /me/missions/step` chỉ
   *    trả về khối của nhiệm vụ vừa báo, ghi đè cả bảng là xoá tiến độ nhiệm vụ khác.
   * ⚠️ ĐÓNG DẤU `uid`: hai đứa trẻ dùng chung một máy thì tiến độ của đứa trước không
   *    được đưa đứa sau vào chơi tiếp giữa nhiệm vụ.
   */
  function absorbMissions(data) {
    var ms = data && data.missions;
    if (!ms || typeof ms !== "object") return false;
    var uid = uidNow();
    var box = read(LS_MSTEPS, null);
    if (!box || typeof box !== "object" || box.uid !== uid || typeof box.m !== "object") {
      box = { uid: uid, m: {} };
    }
    var got = false;
    for (var k in ms) {
      if (!Object.prototype.hasOwnProperty.call(ms, k)) continue;
      var m = ms[k];
      // Đòi `steps` là mảng: server cũ (hoặc dữ liệu cắt cụt) thì thà không ghi gì
      // còn hơn ghi `total:0` rồi trang nhiệm vụ tưởng nhiệm vụ không có bước nào.
      if (!m || !Array.isArray(m.steps)) continue;
      box.m[k] = {
        done: (Array.isArray(m.doneSteps) ? m.doneSteps : []).map(String),
        total: m.steps.length,
        complete: !!m.done
      };
      got = true;
    }
    if (got) write(LS_MSTEPS, box);
    return got;
  }

  /**
   * Rót khối `training` của một câu trả lời server vào cache. Trả true nếu ghi được.
   *
   * ⚠️ GHI ĐÈ CẢ BẢNG (khác `absorbMissions` gộp theo từng nhiệm vụ): server luôn
   *    trả về **toàn bộ** danh sách chương trình, nên gộp thì một chương trình bị
   *    gỡ khỏi `Training.All` sẽ sống mãi trong cache của trẻ.
   * ⚠️ Đòi `programs` là MẢNG: server cũ chưa có khối này thì thà không ghi gì còn
   *    hơn ghi `total:0` rồi Sảnh hiện "đã đạt 0/0 chương trình" — một câu SAI.
   */
  function absorbTraining(data) {
    var t = data && data.training;
    if (!t || typeof t !== "object" || !Array.isArray(t.programs)) return false;
    write(LS_TRAIN, {
      uid: uidNow(),
      levels: t.levels | 0,
      maxLevels: t.maxLevels | 0,
      total: t.total | 0,
      programs: t.programs.map(function (p) {
        return {
          key: String(p.key || ""),
          level: p.level | 0,
          maxLevel: p.maxLevel | 0,
          courses: (Array.isArray(p.courses) ? p.courses : []).map(function (c) {
            return {
              game: String(c.game || ""),
              level: c.level | 0,
              maxLevel: c.maxLevel | 0,
              current: c.current | 0,
              // `next` = null nghia la DA TOI DA. Giu nguyen null, dung quy ve 0:
              // 0 thi giao dien ve "con 0 nua len cap sau" cho mot cap khong co.
              next: (c.next === null || c.next === undefined) ? null : (c.next | 0),
              best: c.best | 0
            };
          })
        };
      })
    });
    return true;
  }

  /**
   * Đọc tiến độ huấn luyện từ cache.
   * `known:false` = **chưa biết**, khác hẳn "chưa đạt gì" — nơi gọi phải hiện dấu
   * `—` chứ không hiện 0/5 (cùng luật với missions.html và specimen-vault.html:
   * "0/5 chương trình" là một lời khẳng định SAI về tiến độ của trẻ).
   */
  function trainingCache() {
    var box = read(LS_TRAIN, null);
    if (!box || typeof box !== "object" || box.uid !== uidNow() ||
        !Array.isArray(box.programs)) {
      return { known: false, levels: 0, maxLevels: 0, total: 0, programs: [] };
    }
    return {
      known: true,
      levels: box.levels | 0,
      maxLevels: box.maxLevels | 0,
      total: box.total | 0,
      programs: box.programs.slice()
    };
  }

  /**
   * Rót `progress.quizLv` của một câu trả lời server vào cache. Trả true nếu ghi được.
   *
   * ⚠️ ĐÒI MỘT SỐ NGUYÊN TRONG KHOẢNG HỢP LỆ, không `| 0` cho xong: server cũ chưa
   *    có trường này thì `undefined | 0` = 0, mà 0 không phải một cấp độ — nó sẽ
   *    lặng lẽ ghi đè cấp độ thật bằng một con số vô nghĩa. Thà không ghi gì.
   * ⚠️ TRẦN 3 khớp `Adapt.MaxQuizLevel`. Lệch thì Quiz đi tìm một cấp không tồn tại;
   *    `nearest()` có đường lùi nên không vỡ, nhưng cấp 4 chỉ là tên khác của cấp 3.
   */
  function absorbQuizLv(data) {
    var pr = data && data.progress;
    var lv = pr ? pr.quizLv : null;
    if (typeof lv !== "number" || !isFinite(lv)) return false;
    lv = Math.round(lv);
    if (lv < 1 || lv > 3) return false;
    write(LS_QUIZLV, { uid: uidNow(), lv: lv });
    return true;
  }

  /**
   * Cấp độ câu hỏi nên rút cho người đang dùng máy này.
   *
   * `known:false` = **chưa biết** (chưa đăng nhập, hoặc chưa lần nào đọc được
   * server, hoặc cache của một đứa trẻ khác). Nơi gọi phải rút đề như trước —
   * KHÔNG được tự đoán cấp: một cấp đoán sai làm trẻ mới gặp toàn câu giải thích
   * cơ chế, còn tệ hơn là không lọc gì.
   */
  function quizLvCache() {
    var box = read(LS_QUIZLV, null);
    if (!box || typeof box !== "object" || box.uid !== uidNow() ||
        typeof box.lv !== "number" || box.lv < 1 || box.lv > 3) {
      return { known: false, lv: 0 };
    }
    return { known: true, lv: box.lv | 0 };
  }

  /** Hôm nay là ngày nào theo giờ máy — chỉ dùng để bỏ cache của ngày cũ. */
  function todayKey() {
    try {
      var d = new Date();
      return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
    } catch (e) { return ""; }
  }

  /**
   * Rót `quizRoundsLeft` của một câu trả lời server vào cache. true nếu ghi được.
   *
   * ⚠️ ĐÒI SỐ NGUYÊN HỢP LỆ, không `| 0` cho xong: server cũ chưa có trường này thì
   *    `undefined | 0` = 0 — tức lặng lẽ nói với trẻ là đã hết lượt.
   */
  function absorbQuizLeft(data) {
    if (!data) return false;
    var left = data.quizRoundsLeft, per = data.quizRoundsPerDay;
    if (typeof left !== "number" || !isFinite(left) || left < 0) return false;
    var box = { uid: uidNow(), day: todayKey(), left: Math.round(left) };
    if (typeof per === "number" && isFinite(per) && per > 0) box.per = Math.round(per);
    write(LS_QUIZLEFT, box);
    return true;
  }

  /**
   * Còn mấy lượt Quiz hôm nay.
   * `known:false` = **chưa biết** (chưa đăng nhập / chưa đọc được server / cache của
   * ngày khác hoặc của trẻ khác). Nơi gọi phải cho chơi bình thường — KHÔNG được
   * đoán là hết lượt. Đoán sai theo hướng đó là chặn một đứa trẻ chưa chơi gì.
   */
  function quizLeftCache() {
    var box = read(LS_QUIZLEFT, null);
    if (!box || typeof box !== "object" || box.uid !== uidNow() ||
        box.day !== todayKey() || typeof box.left !== "number" || box.left < 0) {
      return { known: false, left: 0, per: 0 };
    }
    return { known: true, left: box.left | 0, per: box.per | 0 };
  }

  /**
   * Rót cấp/XP + bàn điều khiển của một câu trả lời server vào cache. Trả true nếu ghi.
   *
   * ⚠️ ĐÒI `level.level` LÀ SỐ HỢP LỆ, không `| 0` cho xong: server cũ / câu trả lời
   *    thiếu khối `level` thì `undefined | 0` = 0, mà cấp 0 không tồn tại — ghi nó
   *    xuống là lần vào trang sau thanh XP hiện một con số vô nghĩa. Thà không ghi.
   * ⚠️ NHẬN CẢ HAI HÌNH DẠNG bàn điều khiển (`deskHooks` mới, `desk` mảng id trần
   *    cũ) — đúng lý do server còn trả cả hai, xem Services/Specimens.cs.
   * ⚠️ `desk` RỖNG LÀ MỘT CÂU TRẢ LỜI THẬT ("trẻ chưa trưng gì"), không phải thiếu
   *    dữ liệu — nên vẫn ghi, và `paintDesk` sẽ vẽ đúng một móc nét đứt mời đặt.
   */
  function absorbHud(data) {
    var lv = data && data.level;
    if (!lv || typeof lv.level !== "number" || !isFinite(lv.level) || lv.level < 1) return false;
    var p = (data && data.progress) || {};
    var desk = [];
    if (Object.prototype.toString.call(p.deskHooks) === "[object Array]") {
      desk = p.deskHooks
        .filter(function (x) { return x && typeof x.id === "string" && x.id; })
        .map(function (x) { return { hook: String(x.hook || ""), id: x.id }; });
    } else if (Object.prototype.toString.call(p.desk) === "[object Array]") {
      desk = p.desk
        .filter(function (x) { return typeof x === "string" && x; })
        .map(function (id) { return { hook: "", id: id }; });
    }
    write(LS_HUD, {
      uid: uidNow(),
      level: Math.round(lv.level),
      xp: (typeof lv.xp === "number" && isFinite(lv.xp)) ? Math.round(lv.xp) : 0,
      pct: (typeof lv.pct === "number" && isFinite(lv.pct)) ? Math.round(lv.pct) : 0,
      desk: desk
    });
    return true;
  }

  /**
   * Cấp/XP + bàn điều khiển đã đọc được lần gần nhất, để vẽ NGAY khi mở trang.
   *
   * `known:false` = **chưa biết** (chưa đăng nhập · chưa lần nào đọc được server ·
   * cache của một đứa trẻ khác). Nơi gọi phải vẽ y như khi chưa có dữ liệu — thanh
   * XP 0%, vách khoang lái ẩn hẳn — **KHÔNG đoán cấp 1**: "Cấp 1" cạnh một trang
   * Hồ sơ đang hiện cấp 6 là hai câu trả lời khác nhau cho cùng một đứa trẻ.
   */
  function hudCache() {
    var box = read(LS_HUD, null);
    if (!box || typeof box !== "object" || box.uid !== uidNow() ||
        typeof box.level !== "number" || box.level < 1) {
      return { known: false, level: 0, xp: 0, pct: 0, desk: [] };
    }
    return {
      known: true,
      level: box.level | 0,
      xp: box.xp | 0,
      pct: Math.max(0, Math.min(100, box.pct | 0)),
      desk: Object.prototype.toString.call(box.desk) === "[object Array]" ? box.desk.slice() : []
    };
  }

  /** Số dư ví thật từ server → ghi đè cache của economy.js. */
  function syncWallet(data) {
    if (!data || !data.wallet || !global.Economy || !global.Economy.setFromServer) return;
    global.Economy.setFromServer(data.wallet.meteors);
  }

  /* ---------------- NHÂN VẬT: cầu nối hai chiều ----------------
     Luật nằm HẾT ở `js/characters.js` (`AstroQChars.sync`) — ở đây chỉ nối dây,
     đúng phân công đã dùng cho ví (`Economy`), bậc (`AstroQDepth`) và tông đèn
     (`AstroQCos`): file này biết "khi nào", file kia biết "như thế nào".

     ⚠️ ĐẶT Ở ĐÂY chứ không nhét vào từng trang: `dashboard.html`, `codex.html`,
        `achievements.html`, `profile.html`, `certificate.html` đều gọi vào hai
        hàm dưới, nên một chỗ nối là cả năm trang có. Chép điều kiện sang từng
        trang là đúng anti-pattern `js/badges.js` / `js/route-gate.js` đã trả giá.
     ⚠️ KHÔNG await: đây là việc nền, chậm mạng thì lượt mở trang sau thử lại.
        Chặn giao diện vì một lời gọi chỉ để đồng bộ là đi ngược hợp đồng đầu file. */
  function syncIdentity(auth, data) {
    try {
      if (!global.AstroQChars || !global.AstroQChars.sync || !data) return;
      /* Hai route trả hai hình dạng: `/me/achievements` đặt phẳng ở gốc,
         `/me/profile` bọc trong `profile`. Nhận cả hai để nối được ở cả hai chỗ. */
      var p = data.profile || data;
      global.AstroQChars.sync(auth, uidNow(), p.character || "", p.avatar || "");
    } catch (e) {}
  }

  function read(key, fallback) {
    try {
      var v = localStorage.getItem(key);
      return v === null ? fallback : JSON.parse(v);
    } catch (e) { return fallback; }
  }
  function write(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {}
  }

  /* ---------------- Bản sao bộ đếm trong máy ---------------- */
  function emptyLocal() {
    return {
      quizTaken: 0, quizAnswered: 0, quizCorrect: 0, quizPerfect: 0,
      gamesPlayed: 0, lessonsRead: 0, flightSeconds: 0, meteorsEarned: 0,
      planets: [], bests: {}, lessons: []
    };
  }
  function localData() {
    var d = read(LS_LOCAL, null);
    if (!d || typeof d !== "object") return emptyLocal();
    var base = emptyLocal();
    for (var k in base) if (base.hasOwnProperty(k) && d[k] != null) base[k] = d[k];
    return base;
  }

  /** Cộng bản sao trong máy theo cùng sự kiện vừa gửi lên server. */
  function bumpLocal(ev) {
    var d = localData();
    if (ev.meteors > 0) d.meteorsEarned += ev.meteors;

    if (ev.type === "quiz") {
      d.quizTaken++;
      d.quizAnswered += ev.total || 0;
      d.quizCorrect  += ev.correct || 0;
      if ((ev.total || 0) > 0 && ev.correct === ev.total) d.quizPerfect++;
    } else if (ev.type === "game") {
      d.gamesPlayed++;
      d.flightSeconds += ev.seconds || 0;
      var g = ev.game || "?";
      if (!(d.bests[g] >= (ev.score || 0))) d.bests[g] = ev.score || 0;
    } else if (ev.type === "lesson") {
      // Chống đếm trùng giống server: một bài chỉ tính một lần
      if (d.lessons.indexOf(ev.id) === -1) { d.lessons.push(ev.id); d.lessonsRead++; }
    } else if (ev.type === "planet") {
      if (d.planets.indexOf(ev.id) === -1) d.planets.push(ev.id);
    }
    // type "mission": KHÔNG có bản sao trong máy. Bước nào đã xong, thưởng bao nhiêu
    // đều do server giữ — đoán ở client thì lúc mất mạng sẽ hiện thưởng chưa có thật.
    
    write(LS_LOCAL, d);
    return d;
  }

  /* ---------------- Hàng chờ ---------------- */
  function queue() { var q = read(LS_QUEUE, []); return Array.isArray(q) ? q : []; }

  /** Số việc đã bị vứt vì hàng chờ đầy. Không tự về 0 — chỉ `clearDropped()` xoá. */
  function dropped() { var n = read(LS_DROP, 0); return typeof n === "number" && n > 0 ? n : 0; }
  function clearDropped() { write(LS_DROP, 0); }

  function enqueue(ev) {
    var q = queue();
    q.push(ev);
    // Bỏ những việc CŨ NHẤT khi tràn: việc mới phản ánh trạng thái gần đây hơn
    if (q.length > MAX_QUEUE) {
      // GHI LẠI SỐ BỊ VỨT rồi mới cắt — xem lý do ở khối `LS_DROP` đầu file.
      write(LS_DROP, dropped() + (q.length - MAX_QUEUE));
      q = q.slice(q.length - MAX_QUEUE);
    }
    write(LS_QUEUE, q);
  }

  /** Khoá nhận dạng một việc trong hàng chờ. `opId` là khoá thật; `raw:` chỉ để
      nhận ra việc CŨ do bản trước 21/08/2026 xếp vào mà chưa có `opId`. */
  function keyOf(it) {
    return (it && it.opId) ? "id:" + it.opId : "raw:" + JSON.stringify(it);
  }

  /**
   * Bỏ khỏi hàng chờ những việc ĐÃ GỬI XONG — và CHỈ chúng.
   *
   * ⚠️ KHÔNG ĐƯỢC GHI `[]` HAY `q.slice(i)` (lỗi thật, sửa 21/08/2026): `flush()`
   *    chụp danh sách `q` lúc bắt đầu rồi gửi lần lượt qua nhiều nhịp mạng. Việc
   *    trẻ làm TRONG lúc đó (`report()` nay xếp hàng NGAY) nằm ở cuối hàng chờ mà
   *    không có trong `q` — ghi đè cả hàng chờ bằng ảnh chụp cũ là xoá thẳng việc
   *    vừa xếp. Đây là dữ liệu duy nhất của lượt chơi đó, mất là mất hẳn.
   */
  function dequeue(sent) {
    var gone = {};
    (sent || []).forEach(function (it) {
      var k = keyOf(it);
      gone[k] = (gone[k] || 0) + 1;
    });
    write(LS_QUEUE, queue().filter(function (it) {
      var k = keyOf(it);
      if (gone[k] > 0) { gone[k]--; return false; }
      return true;
    }));
  }

  /** Có phiên đăng nhập + có API hay không. */
  function auth() {
    return global.AstroQAuth && global.AstroQAuth.postProgress ? global.AstroQAuth : null;
  }

  /** Gửi một việc trong hàng chờ tới đúng route của nó. */
  function send(a, item) {
    if (item && item.kind === "spend") {
      return a.spendWallet({ reason: "game", game: item.game, opId: item.opId });
    }
    if (item && item.type === "mission") {
      return a.missionStep({ mission: item.mission, step: item.step, opId: item.opId });
    }
    return a.postProgress(item);
  }

  /* Module ES js/firebase-auth.js chạy SAU các script cổ điển, nên lúc file này
     nạp xong thì AstroQAuth có thể chưa tồn tại. Chờ có hạn rồi mới kết luận. */
  function waitAuth(ms) {
    if (auth()) return Promise.resolve(auth());
    return new Promise(function (resolve) {
      var t0 = Date.now();
      var timer = setInterval(function () {
        if (auth() || Date.now() - t0 > ms) { clearInterval(timer); resolve(auth()); }
      }, 60);
    });
  }

  /* ⚠️ GIỮ CHÍNH LỜI HỨA ĐANG CHẠY, KHÔNG PHẢI MỘT CỜ BOOLEAN — sửa 21/08/2026.
     Trước đó `flush()` gọi lần hai lúc đang chạy thì trả về `Promise.resolve(false)`
     NGAY, tức nơi gọi tưởng "hàng chờ đã xong" trong khi việc vẫn đang bay. Mà
     `flush()` LUÔN đang chạy sẵn ở mọi trang có hàng chờ (dòng cuối file gọi nó lúc
     nạp), nên `readAuth()` bên dưới sẽ không bao giờ chờ được gì nếu chỉ có cờ.
     Xem `readAuth()` để biết vì sao việc chờ đó là bắt buộc. */
  var flushing = null;

  /* ⚠️ SỐ VIỆC VỪA GỬI XONG — để trang nói được "đã lưu xong n việc".
     Vì sao không để trang tự đếm: `flush()` chạy ngay khi file này nạp, và với một
     phiên đăng nhập còn tốt thì nó xong TRƯỚC cả lúc script của trang chạy tới —
     đo được như vậy ở `smoke_session_note.py` mục [5]. Trang tự đếm thì luôn thấy
     hàng chờ đã rỗng và **lời báo không bao giờ hiện ra**, tức trẻ đăng nhập lại
     xong vẫn không biết việc của mình có được cứu hay không.
     Chỉ sống trong lượt tải trang này (không ghi localStorage), nên F5 không báo
     lại một chuyện đã báo. */
  var lastFlush = 0;

  /** Số việc của lần gửi lại gần nhất, 0 nếu chưa có. Gọi `ackFlush()` sau khi đã nói. */
  function flushed() { return lastFlush; }
  function ackFlush() { lastFlush = 0; }

  /**
   * Gửi lại những việc đang xếp hàng.
   * → Promise<boolean> — `true` = hàng chờ đã RỖNG khi lời hứa này xong.
   *
   * Gọi được nhiều lần: đang chạy thì trả về CHÍNH lời hứa đang chạy, nên nơi gọi
   * thứ hai vẫn chờ đúng lúc việc gửi xong (xem khối chú thích ở `flushing`).
   */
  function flush() {
    if (flushing) return flushing;
    var q = queue();
    if (q.length === 0) return Promise.resolve(true);
    var n0 = q.length;

    flushing = waitAuth(2500).then(function (a) {
      if (!a) return false;

      // Gửi lần lượt: server chống trùng theo từng việc, nhưng thứ tự vẫn nên
      // giữ đúng để kỷ lục và bộ đếm ra cùng kết quả như lúc chơi.
      var i = 0;
      function step() {
        if (i >= q.length) {
          dequeue(q);                // bỏ ĐÚNG những việc vừa gửi — xem `dequeue()`
          lastFlush += n0;           // gửi HẾT rồi mới ghi nhận — xem ghi chú ở `lastFlush`
          return true;
        }
        return send(a, q[i]).then(function (r) {
          if (!r || !r.ok) {
            // Vẫn hỏng → chỉ bỏ phần ĐÃ gửi, phần còn lại để lần sau thử tiếp
            dequeue(q.slice(0, i));
            return false;
          }
          syncWallet(r.data);
          /* Bước nhiệm vụ chơi lúc mất mạng / ở trang không có token được gửi ở ĐÂY,
             nên cache "đã xong bước nào" cũng phải cập nhật ở đây. Chỉ dựa vào
             `missions()` thì có một khe: dashboard vừa gọi `/me/missions` xong TRƯỚC
             khi hàng chờ gửi hết → cache thiếu đúng mấy bước trẻ vừa chơi. */
          absorbMissions(r.data);
          /* Cap do Quiz cung phai cap nhat o DAY, khong chi o `profile()`.
             ⚠️ Do duoc 19/08/2026 (`e2e_quizlv_login.py`): dang nhap that roi vao
                THANG `quiz.html` thi cache khong bao gio duoc ghi, vi chi 3 trang
                goi `profile()`/`achievements()`. Tre vao bang duong khac se lam de
                cua cap 1 mai. Day la CUNG mot khe da mo ta cho `absorbMissions`
                ngay tren — nen bit bang cung mot cach. */
          absorbQuizLv(r.data);
          absorbQuizLeft(r.data);   // hạn mức lượt Quiz — xem LS_QUIZLEFT
          i++;
          return step();
        });
      }
      return step();
    }).catch(function () { return false; })
      /* MỞ CHỐT Ở ĐÚNG MỘT CHỖ, chạy trên MỌI đường ra (xong hết · gửi hỏng · không
         có token · ngoại lệ). Rải `flushing = null` vào từng nhánh là kiểu chốt sớm
         muộn có một nhánh quên mở, mà quên mở thì hàng chờ đứng im vĩnh viễn. */
      .then(function (ok) { flushing = null; return ok; });
    return flushing;
  }

  /**
   * CHỜ TOKEN, RỒI GỬI NỐT HÀNG CHỜ, RỒI MỚI CHO ĐỌC. Dùng cho mọi route CHỈ ĐỌC
   * (`load` · `missions` · `achievements` · `daily` · `specimens` · `syncWallet`).
   *
   * ⚠️ VÌ SAO BẮT BUỘC (lỗi thật, sửa 21/08/2026): các trang chơi **cố ý không nạp**
   *    `js/firebase-auth.js` (`mission-earth.html`, `quiz.html`, các trang game), nên
   *    MỌI việc chúng làm đều rơi vào hàng chờ. Trẻ chơi xong rồi sang trang CÓ token
   *    thì ở đó có HAI lời gọi cùng chạy: `flush()` (POST việc vừa chơi) và route đọc
   *    (GET tiến độ). GET thường về TRƯỚC POST → trang vẽ đúng trạng thái **trước khi
   *    chơi**, và vẽ xong thì không vẽ lại nữa. Đo được ở hai chỗ trẻ thấy ngay:
   *      · cây chặng: xong chặng ① mà nút ① vẫn không có dấu ✓;
   *      · số dư: xong Quiz, đầu trang đã +thưởng, sang dashboard tụt về số cũ.
   *    Bịt ở ĐÂY (một chỗ) chứ không ở từng trang: mỗi trang tự nhớ là sớm muộn có
   *    một trang quên, đúng cái giá `absorbMissions` đã trả khi chỉ vá `flush()`.
   *
   * ⚠️ KHÔNG chờ khi hàng chờ RỖNG hoặc chưa đăng nhập → đường đọc thường ngày
   *    không dài thêm một nhịp mạng nào.
   * ⚠️ Hàng chờ gửi hỏng cũng ĐỌC TIẾP (`catch`): mất mạng giữa đường không được
   *    biến một trang chỉ-đọc thành trang trắng.
   */
  function readAuth() {
    return waitAuth(2500).then(function (a) {
      if (!a || queue().length === 0) return a;
      return flush().catch(function () { return false; }).then(function () { return a; });
    });
  }

  /**
   * Gửi một việc. Luôn trả Promise, không bao giờ reject.
   *
   * ⚠️⚠️ XẾP HÀNG CHỜ **NGAY**, RỒI MỚI GỬI — không phải ngược lại (lỗi thật, sửa
   *      21/08/2026). Bản trước chỉ `enqueue()` SAU khi `waitAuth(2500)` trả về
   *      tay không, tức việc chỉ được ghi xuống localStorage ở giây thứ 2,5.
   *      Nhưng `quiz.html`, `games.html` và các trang game **cố ý không nạp**
   *      `js/firebase-auth.js`, nên ở đó `waitAuth` LUÔN chạy hết 2,5 giây. Trẻ
   *      xem màn tổng kết rồi bấm "Chơi lại" / "Về" trong khoảng đó là trang unload
   *      trước khi hẹn giờ nổ ⇒ **cả lượt chơi biến mất**: không thiên thạch, không
   *      XP, không thuật ngữ được giải mã. Mà `Economy.addAsteroids()` đã cộng lạc
   *      quan trên đầu trang rồi, nên trang sau `setFromServer()` sẽ kéo số dư tụt
   *      lại — đúng cái trẻ thấy là "chơi xong không được cộng".
   *      Ghi trước thì cùng lắm là gửi lại một việc server đã xử lý, mà điều đó vô
   *      hại: server dedupe theo `opId` (điều 4 ở đầu file).
   */
  function report(ev) {
    ev.opId = ev.opId || newOpId();
    bumpLocal(ev);
    enqueue(ev);
    return waitAuth(2500).then(function (a) {
      if (!a) return { ok: false, reason: "auth", queued: true };
      return send(a, ev).then(function (r) {
        if (!r || !r.ok) return { ok: false, reason: (r && r.reason) || "http", queued: true };
        dequeue([ev]);            // gửi được rồi thì không để hàng chờ gửi lần hai
        syncWallet(r.data);
        absorbMissions(r.data);   // chỉ có tác dụng với ev.type === "mission"
        /* Sau MỖI lượt quiz được ghi nhận, cấp độ được server tính lại ngay —
           đúng thứ cần cho một tính năng gọi là "tự điều chỉnh". Xem khối chú
           thích ở `flush()` để biết vì sao phải có ở CẢ HAI đường. */
        absorbQuizLv(r.data);
        absorbQuizLeft(r.data);
        return r;
      });
    }).catch(function () {
      return { ok: false, reason: "error", queued: true };
    });
  }

  /**
   * Trừ phí một lượt chơi. Gọi từ `Economy.spend(game)` — đừng gọi trực tiếp,
   * không thì cache và ví lệch nhau.
   *
   * Chỉ gửi TÊN GAME; server tra bảng phí của nó. Mất mạng → xếp hàng chờ kèm
   * `opId` nên gửi lại không bị trừ hai lần.
   *
   * ⚠️ XẾP HÀNG CHỜ NGAY rồi mới gửi, cùng lý do với `report()` ở trên: các trang
   *    game không có token nên `waitAuth` luôn chạy hết 2,5 giây, mà trẻ bấm vào
   *    game rồi thoát ngay trong khoảng đó thì phí không bao giờ được ghi.
   */
  function spendReport(game) {
    var item = { kind: "spend", game: String(game || ""), opId: newOpId() };
    enqueue(item);
    return waitAuth(2500).then(function (a) {
      if (!a) return { ok: false, reason: "auth", queued: true };
      return a.spendWallet({ reason: "game", game: item.game, opId: item.opId })
        .then(function (r) {
          if (!r || !r.ok) {
            // 409 "insufficient" KHÔNG xếp hàng chờ: server đã trả lời rõ là không
            // đủ tiền, gửi lại chỉ nhận đúng câu đó. Chỉ xếp lại khi lỗi mạng.
            if (r && r.reason === "http" && r.code === "insufficient") {
              dequeue([item]);
              if (r.meteors != null && global.Economy) Economy.setFromServer(r.meteors);
              return r;
            }
            return { ok: false, reason: (r && r.reason) || "http", queued: true };
          }
          dequeue([item]);
          syncWallet(r.data);
          return r;
        });
    }).catch(function () {
      return { ok: false, reason: "error", queued: true };
    });
  }

  var AstroQProgress = {
    /**
     * Xong một lượt Quiz.
     * @param {{correct:number,total:number,meteors:number,terms?:string[],wrong?:string[]}} o
     *   `terms` = khoá thuật ngữ ĐÃ TRẢ LỜI ĐÚNG (khoá `term` của
     *   js/quiz-index.js). Đây là DÂY NỐI để Sổ Tay Thuật Ngữ biết thẻ nào đã
     *   giải mã — thiếu nó thì mọi thẻ khoá vĩnh viễn, đúng tình trạng trước
     *   30/07/2026.
     *
     *   `wrong` = khoá đã TRẢ LỜI SAI. ⚠️ HAI TRƯỜNG NÀY ĐI HAI ĐƯỜNG KHÁC NHAU ở
     *   server: `terms` vào `PROGRESS.terms` (mở Sổ Tay) **và** vào nhật ký; `wrong`
     *   CHỈ vào nhật ký. Gộp chúng lại là giải mã một thẻ bằng một câu trả lời sai.
     */
    quiz: function (o) {
      o = o || {};
      var ev = { type: "quiz", correct: o.correct | 0, total: o.total | 0,
                 meteors: o.meteors | 0 };
      /* ⚠️ CHỈ GỬI KHI CÓ. `terms: []` là tập rỗng, mà string set của DynamoDB
         KHÔNG nhận tập rỗng — server đã chặn nhưng gửi thừa một trường rỗng trong
         mỗi lượt là mời lỗi. */
      if (o.terms && o.terms.length) ev.terms = o.terms.slice();
      if (o.wrong && o.wrong.length) ev.wrong = o.wrong.slice();
      return report(ev);
    },
    /** Xong một lượt game. `game` là khoá kỷ lục: "dodge" | "defender" | "constellation". */
    game: function (o) {
      o = o || {};
      var ev = { type: "game", game: String(o.game || ""), score: o.score | 0,
                 seconds: o.seconds | 0, meteors: o.meteors | 0 };
      /* ⚠⚠ `id` PHẢI ĐI KÈM, và việc bỏ nó đã làm Ghép Chòm Sao KHÔNG BAO GIỜ
         LÊN CẤP (lỗi im lặng, sửa 21/08/2026). Chuỗi đầy đủ như sau:
         `game-constellation.html` gửi `id: consKey` → server `MeEndpoints` nhánh
         `case "game"` đọc `req.Id` khi `game == "constellation"` → ghi vào
         `PROGRESS.consts` → `Training.cs` chia cấp chương trình Quan Sát Thiên Văn
         bằng `consts` (**số chòm sao KHÁC NHAU**, không phải số lượt chơi).
         Hàm này tức là mắt nối DUY NHẤT của cả chuỗi đó, mà nó lặng lẽ vớt
         `id` đi nên trẻ ghép xong 4 chòm vẫn ở Cấp 0 — không lỗi, không cảnh báo.
         ⚠ Chỉ gửi khi CÓ: server `Clean()` nó riêng cho constellation, nhưng mọi
           game khác đính thêm một trường rỗng là làm payload nói một thứ vô nghĩa. */
      var id = String(o.id || "").trim();
      if (id) ev.id = id;
      return report(ev);
    },
    /** Đọc xong một bài. Gọi bao nhiêu lần cũng chỉ tính một. */
    lesson: function (id) { return report({ type: "lesson", id: String(id || "") }); },
    /** Ghé một hành tinh. Ghé lại không tính thêm. */
    planet: function (id) { return report({ type: "planet", id: String(id || "") }); },

    /** Trừ phí một lượt. Gọi qua `Economy.spend(game)`, không gọi trực tiếp. */
    spend: spendReport,

    /**
     * Báo XONG MỘT BƯỚC nhiệm vụ. Chỉ gửi `{mission, step}` — **không gửi con số
     * thưởng nào**; server tra Services/Missions.cs rồi cộng (đây là chỗ thưởng
     * không thể bịa, khác điểm game). Mất mạng → xếp hàng chờ kèm `opId`.
     */
    missionStep: function (mission, step) {
      return report({ type: "mission", mission: String(mission || ""),
                      step: String(step || "") });
    },

    /** Bản sao bộ đếm trong máy — đọc ngay, không chờ mạng. */
    local: localData,

    /** Số việc đang xếp hàng chờ gửi. */
    pending: function () { return queue().length; },

    /**
     * Số việc đã bị hàng chờ VỨT ĐI vì đầy (trần `MAX_QUEUE`). Trang nào nói với
     * trẻ về hàng chờ thì phải nói cả con số này — bỏ qua nó là im lặng đúng chỗ
     * dữ liệu THẬT SỰ mất, và im lặng ở đó thì trẻ chỉ thấy tt tự nhiên hụt đi.
     */
    dropped: dropped,
    /** Xoá bộ đếm trên, gọi SAU khi đã nói với người dùng. */
    clearDropped: clearDropped,

    /** Số việc vừa gửi lại xong trong lượt tải trang này (0 = chưa có). */
    flushed: flushed,
    /** Xoá con số trên, gọi SAU khi đã báo với người dùng. */
    ackFlush: ackFlush,

    /**
     * Lấy hồ sơ + tiến độ để vẽ trang.
     * → { ok, source:"server"|"local", data, reason? }
     * Server không trả lời được thì trả bộ đếm trong máy, kèm `source:"local"`
     * để trang tự hiện lời nhắc — hiện số cũ mà không nói gì là đánh lừa người dùng.
     */
    load: function () {
      return readAuth().then(function (a) {
        if (!a || !a.getProfile) return { ok: false, source: "local", reason: "auth", data: localData() };
        return a.getProfile().then(function (r) {
          if (!r || !r.ok) {
            return { ok: false, source: "local", reason: (r && r.reason) || "http", data: localData() };
          }
          syncWallet(r.data);        // số dư thật → ghi đè cache của economy.js
          absorbQuizLv(r.data);      // cấp độ Quiz → cache cho quiz.html (xem LS_QUIZLV)
          syncIdentity(a, r.data);   // nhân vật: kéo về, hoặc đẩy lên nếu server rỗng
          return { ok: true, source: "server", data: r.data };
        });
      }).catch(function () {
        return { ok: false, source: "local", reason: "error", data: localData() };
      });
    },

    /** Lấy kho thành tích (server là nơi quyết huy hiệu nào đã mở). */
    achievements: function () {
      return readAuth().then(function (a) {
        if (!a || !a.getAchievements) return { ok: false, reason: "auth" };
        return a.getAchievements().then(function (r) {
          if (r && r.ok) {
            syncWallet(r.data); absorbTraining(r.data); absorbQuizLv(r.data);
            /* Cấp/XP + bàn điều khiển → cache để lượt vào trang SAU vẽ được ngay,
               khỏi phải xem hết 5 chặng nối tiếp mới thấy số của mình (xem LS_HUD). */
            absorbHud(r.data);
            syncIdentity(a, r.data);
          }
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Lấy trạng thái NHIỆM VỤ (bước nào đã xong, mẫu Codex nào đã có, xong cả
     * nhiệm vụ chưa). Dùng cho Sảnh Nhiệm Vụ `missions.html`.
     *
     * Nhẹ hơn `achievements()` vì `GET /me/missions` chỉ trả đúng khối nhiệm vụ,
     * không kéo theo cả bộ huy hiệu — trang Sảnh không cần huy hiệu.
     *
     * Trả `{ ok:false, reason }` khi chưa đăng nhập / mất mạng; trang gọi phải
     * hiện dấu `—` chứ **không đoán số bước đã xong**, y như achievements.html.
     */
    missions: function () {
      return readAuth().then(function (a) {
        if (!a || !a.getMissions) return { ok: false, reason: "auth" };
        return a.getMissions().then(function (r) {
          /* Ghi cache "đã xong bước nào" cho trang nhiệm vụ đọc — nó không có token
             nên không tự hỏi được. Xem khối chú thích ở `LS_MSTEPS`. */
          if (r && r.ok) absorbMissions(r.data);
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * VIỆC HÔM NAY + CHUỖI NGÀY (`GET /me/daily`).
     *
     * ⚠️ SERVER LÀ NGUỒN SỰ THẬT DUY NHẤT, và cố ý KHÔNG có bản sao trong máy.
     *    Tiến độ ba việc suy ra từ nhật ký ở server (xem Services/Daily.cs), nên đoán
     *    ở client thì lúc mất mạng sẽ hiện một cái dấu ✅ cho việc chưa được ghi nhận —
     *    tức khoe một phần thưởng chưa có thật. Cùng lý do `bumpLocal()` bỏ qua
     *    `type:"mission"`. Mất mạng → `{ok:false}` → bảng hiện dấu "—".
     *
     * ⚠️ Route này CÓ TÁC DỤNG PHỤ ở server (tự cấp bù việc đã xong mà chưa trả
     *    thưởng), nên nó cũng trả về `wallet` — đẩy thẳng vào cache ví như mọi route
     *    khác, không thì số dư trên đầu trang thấp hơn số thật.
     */
    daily: function () {
      return readAuth().then(function (a) {
        if (!a || !a.getDaily) return { ok: false, reason: "auth" };
        return a.getDaily().then(function (r) {
          if (r && r.ok) { syncWallet(r.data); absorbQuizLeft(r.data); }
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Bước nào của một nhiệm vụ đã xong, theo lần cuối SERVER trả lời.
     * → { known, done:string[], total:number, complete:boolean }
     *
     * `known:false` = chưa từng đọc được server (chưa đăng nhập / máy sạch) → trang
     * gọi phải mở nhiệm vụ **từ bước đầu**, đừng đoán. Đây là bản sao chỉ-đọc dùng để
     * biết vào chơi tiếp từ đâu; nguồn sự thật vẫn là DynamoDB.
     */
    /**
     * Tiến độ Trung Tâm Đào Tạo, đọc từ cache do trang CÓ token vừa ghi.
     * ⚠️ `known:false` = CHƯA BIẾT, khác "chưa đạt gì" — nơi gọi phải hiện `—`.
     */
    training: function () { return trainingCache(); },
    /** Cấp độ câu hỏi Quiz server đã tính → `{known, lv}`. Xem LS_QUIZLV. */
    quizLv: function () { return quizLvCache(); },
    /** Còn mấy lượt Quiz hôm nay → `{known, left, per}`. Xem LS_QUIZLEFT. */
    quizLeft: function () { return quizLeftCache(); },

    /**
     * Cấp/XP + bàn điều khiển của lượt đọc gần nhất → `{known, level, xp, pct, desk}`.
     * Để vẽ NGAY khi mở trang, thay vì để thanh XP đứng 0% và vách khoang lái trống
     * suốt 1,5–2,6 giây (số đo ở LS_HUD).
     * ⚠️ `known:false` = CHƯA BIẾT → vẽ y như khi không có dữ liệu, đừng đoán cấp 1.
     * ⚠️ Câu trả lời của server LUÔN thắng: vẽ lại khi `achievements()` về.
     */
    hud: function () { return hudCache(); },

    missionSteps: function (mission) {
      var box = read(LS_MSTEPS, null);
      // Cache của người khác (hoặc của lượt chưa đăng nhập) thì coi như không có.
      if (!box || typeof box !== "object" || box.uid !== uidNow() || !box.m) {
        return { known: false, done: [], total: 0, complete: false };
      }
      var m = box.m[String(mission || "")];
      if (!m || !Array.isArray(m.done) || !(m.total > 0)) {
        return { known: false, done: [], total: 0, complete: false };
      }
      return { known: true, done: m.done.slice(), total: m.total | 0, complete: !!m.complete };
    },

    /**
     * Lấy Kho Mẫu Vật (server là nơi quyết mẫu nào đã thu thập — suy ra từ bộ đếm
     * tiến độ, không có đường ghi riêng).
     */
    specimens: function () {
      return readAuth().then(function (a) {
        if (!a || !a.getSpecimens) return { ok: false, reason: "auth" };
        return a.getSpecimens().then(function (r) {
          if (r && r.ok) syncWallet(r.data);
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Treo mẫu vật lên móc ở vách khoang lái (tối đa 3). `items` = mảng
     * `{hook, id}`. Đây là thứ DUY NHẤT của kho mẫu vật mà client được quyết —
     * nhưng server vẫn kiểm từng id phải có thật, đã mở khoá, và móc phải hợp lệ.
     *
     * KHÔNG xếp hàng chờ như các việc khác: đây là lựa chọn trang trí, gửi lại
     * sau nhiều giờ thì có thể ghi đè lựa chọn mới hơn ở máy khác.
     */
    setDesk: function (items) {
      return waitAuth(2500).then(function (a) {
        if (!a || !a.setSpecimenDesk) return { ok: false, reason: "auth" };
        return a.setSpecimenDesk(items);
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Lấy số dư ví thật rồi ghi đè cache. Dùng cho trang chỉ HIỆN số dư mà không
     * cần hồ sơ (games.html, các trang game) — nhẹ hơn gọi cả `/me/profile`.
     */
    syncWallet: function () {
      return readAuth().then(function (a) {
        if (!a || !a.getWallet) return { ok: false, reason: "auth" };
        return a.getWallet().then(function (r) {
          if (r && r.ok) syncWallet(r.data);
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    flush: flush

    /* ⚠️ `clearLocal()` ĐÃ BỎ 20/08/2026 — nó có ĐÚNG 0 người gọi kể từ lúc được
       viết, kể cả lúc Đăng xuất (CLAUDE.md đã ghi đúng điều đó). Nên đo được trên
       bản thật: sau khi đăng xuất còn 7 khoá `astroq-*` của trẻ vừa dùng. Việc này
       nay là `AstroQ.clearAccountData()` ở js/ui-common.js — dọn theo TIỀN TỐ với
       một danh sách giữ lại ngắn, nên khoá per-trẻ thêm sau này TỰ được dọn. Bản ở
       đây còn thiếu hẳn `astroq-route-gate`, `astroq-asteroids`, kỷ lục game và hai
       cờ onboarding. Tra lại: `git log -S clearLocal`. */
  };

  global.AstroQProgress = AstroQProgress;

  // Có việc đang chờ thì thử gửi lại ngay khi mở trang, và mỗi khi có mạng lại.
  if (queue().length > 0) flush();
  global.addEventListener("online", function () { flush(); });
})(window);
