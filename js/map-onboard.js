/* ============================================================================
   js/map-onboard.js — COMET DẪN ĐƯỜNG Ở BẢN ĐỒ THIÊN HÀ, lượt onboarding.
   (bước ①–④ của `docs/decisions/003`)

   Nhịp: màn warp "ĐANG DU HÀNH TỚI · Hệ Mặt Trời" → Comet giới thiệu ở ĐÁY màn
   hình → trẻ chạm Trái Đất → bảng thông tin mở → **NHỊP 0** (Comet chỉ bầu khí
   quyển → nói thật rằng vành đang vẽ dày quá → mời trẻ XOAY để ngắm nửa ngày /
   nửa đêm) → **sau ít nhất 15 giây** Comet hỏi "sẵn sàng chưa?" → nút OK →
   `mission-earth.html`.

   ⚠️ NHỊP 0 THÊM 02/08/2026 (`docs/decisions/005`). Bài học ngày/đêm được CHUYỂN
      từ bản đồ phẳng của `mission-earth.html` sang đây, vì ở đây ranh giới là THẬT
      (`PointLight` gắn vào Mặt Trời của cảnh) còn ở đó nó là một gradient trông như
      bức tường đen. Chi tiết + số đo ghi ngay trên hàm `reading()`.

   ⚠️ FILE NÀY KHÔNG BIẾT GÌ VỀ three.js. Nó nhận đúng những gì cần qua `init()`
      (`warpShow` · `warpHide` · `ready` · `t` · `regionName` · `onGo`), nên `explorer.html`
      không phình thêm và bộ test lái được bằng cách gọi thẳng vào đây.

   ⛔ KHÔNG CÒN MỐC CHỜ NÀO. `READ_MS` (mốc SÀN 10 rồi 15 giây trước khi Comet hỏi
      "sẵn sàng chưa?") đã BỎ HẲN 02/08/2026 — trẻ bấm "Tiếp tục" là sang ngay. Lý do
      đầy đủ ghi ở chỗ khai `WARP_MIN_MS` và trong `reading()`. Đừng dựng lại.

   Xem lại để thử: mở `explorer.html?onboard=1`.
   ============================================================================ */
(function (global) {
  "use strict";

  var TXT = {
    vi: {
      nm: "Comet", tag: "HOA TIÊU",
      l1: "Đây là <b>Hệ Mặt Trời</b> của chúng ta — nơi có rất nhiều thứ để khám phá!",
      l2: "Hãy bắt đầu từ <b>Trái Đất</b>, hành tinh xanh của chúng ta nhé. " +
          "Chạm vào Trái Đất để xem thông tin!",
      /* NHỊP 0 — xem khối chú thích "NHỊP 0" ở đầu file.
         ⚠️ ĐỪNG VIẾT "nitơ và oxy — thứ mình đang thở". Chủ dự án chơi thật và bắt
            đúng chỗ này: câu đó đọc ra như thể cơ thể dùng CẢ HAI khí. Sự thật là
            không khí phần lớn là nitơ, nhưng thứ cơ thể LẤY khi hít vào là oxy —
            nitơ đi vào rồi lại đi ra. Tỉ lệ 78/21 lấy từ `science.nasa.gov/earth/facts/`. */
      l3: "Thấy lớp sáng mờ bọc quanh Trái Đất không? Đó là <b>bầu khí quyển</b>, làm bằng " +
          "nitơ và oxy. Không khí phần lớn là <b>nitơ</b>, nhưng thứ cơ thể mình thật sự " +
          "dùng khi hít vào lại là <b>oxy</b>.",
      l3b: "Thật ra khí quyển <b>mỏng hơn thế rất nhiều</b> — mỏng như lớp vỏ táo so với " +
           "quả táo. Mình đã <b>cố tình mô phỏng to hơn</b> cho bạn dễ nhìn thôi.",
      /* ⚠️ PHẢI NÓI RÕ BẤM GÌ ĐỂ ĐI TIẾP. Chủ dự án báo hai lần ở đúng chỗ này: lần
         đầu *"sau đó không hiện gì tiếp để biết là chờ hay làm gì?"*, lần sau *"ấn nút
         Tiếp tục sẽ phải chuyển sang ngay, không chờ"*. Nên câu này vừa mời ngắm
         thoải mái, vừa chỉ đúng cái nút sẽ đưa trẻ đi tiếp NGAY khi bấm. */
      l4: "Giờ thử <b>kéo để xoay quanh Trái Đất</b> xem: một nửa đang là <b>ban ngày</b>, " +
          "nửa kia là <b>ban đêm</b> — vì ánh sáng Mặt Trời chỉ chiếu tới được một phía. " +
          "Ngắm thoải mái nhé, xong thì bấm <b>Tiếp tục</b> là mình đi ngay!",
      ask: "Bạn đã sẵn sàng bắt đầu hành trình với <b>nhiệm vụ đầu tiên</b> tại Trái Đất chưa?",
      /* ⚠️ CHỈ CHỮ, KHÔNG CÓ DẤU "›" (bỏ 02/08/2026 theo chủ dự án). Mũi tên đó nói
         "sang trang/sang phần khác", trong khi cú bấm chỉ đưa sang câu thoại kế tiếp
         của cùng một nhân vật ở cùng một màn hình. Nó cũng là một ký tự trình đọc
         màn hình đọc thành tên riêng của dấu, thừa với người dùng khiếm thị. */
      next: "Tiếp tục", ok: "OK, bắt đầu! 🚀"
    },
    en: {
      nm: "Comet", tag: "NAVIGATOR",
      l1: "This is our <b>Solar System</b> — there is so much to explore here!",
      l2: "Let's start with <b>Earth</b>, our blue planet. Tap Earth to read about it!",
      l3: "See the soft glow wrapped around Earth? That is the <b>atmosphere</b>, made of " +
          "nitrogen and oxygen. Air is mostly <b>nitrogen</b>, but the part your body " +
          "actually uses when you breathe in is the <b>oxygen</b>.",
      l3b: "In reality the atmosphere is <b>far thinner</b> than that — thin like the skin on " +
           "an apple. We <b>deliberately show it larger</b> so it is easier for you to see.",
      l4: "Now <b>drag to spin around Earth</b>: one half is in <b>daylight</b> and the other " +
          "half is in <b>night</b> — sunlight can only reach one side at a time. Take all the " +
          "time you want, then hit <b>Next</b> and off we go!",
      ask: "Are you ready to begin your <b>first mission</b> here on Earth?",
      next: "Next", ok: "OK, let's go! 🚀"
    }
  };

  /* Mốc thời gian.
     ⛔ `READ_MS` ĐÃ BỎ HẲN 02/08/2026 — đừng dựng lại. Nó là mốc SÀN chờ trước khi
        Comet hỏi "sẵn sàng chưa?" (`003` chốt 10 giây, `005` nới lên 15). Cái sàn ấy
        sinh ra khi nhịp phim CHƯA có nhịp 0: Comet nói xong là box tự ẩn, không có
        nút nào, nên phải có đồng hồ mới biết khi nào hỏi tiếp. Nay nhịp 0 kết bằng
        một NÚT do trẻ chủ động bấm — bắt đợi thêm sau cú bấm đó là biến nút "Tiếp
        tục" thành nút không tiếp tục. Xem `reading()`.
     Trẻ vẫn ngắm bao lâu tuỳ ý: box thoại KHÔNG tự ẩn, nút cứ nằm đó chờ. */
  var WARP_MIN_MS = 1800;      // màn warp phải sống đủ lâu để đọc được tên vùng
  var WARP_MAX_MS = 12000;     // cảnh 3D không dựng được thì cũng phải nhả ra
  var TYPE_MS = 22;            // ms mỗi ký tự

  /* ⚠️ CACHE "ĐÃ ĐI QUA BẢN ĐỒ" — BẮT BUỘC, KHÔNG PHẢI TỐI ƯU.
     `explorer.html` **cố ý không nạp** `js/firebase-auth.js` (233 KB) nên nó KHÔNG có
     token để ghi cờ `map01Seen` lên server. Mà `dashboard.html` lại dựa vào cờ đó để
     quyết có đẩy trẻ sang bản đồ hay không. Thiếu cầu nối này thì:
        dashboard (cờ vẫn false) → bản đồ → nhiệm vụ → dashboard (cờ VẪN false) → …
     tức **trẻ bị đẩy lại bản đồ mỗi lần mở dashboard**. Nên: ở đây ghi cache trong máy,
     `dashboard.html` đọc cache trước rồi mới đẩy cờ thật lên server.
     Đúng khuôn `astroq-tour-seen` đã dùng cho `tourSeen`. */
  var SEEN_KEY = "astroq-map01-seen";

  function markSeen() {
    try { global.localStorage.setItem(SEEN_KEY, "1"); } catch (e) {}
  }

  var A = null;                // các hàm do explorer.html truyền vào
  var lang = "vi";
  var el = {};
  var reduced = false;
  var typing = null;
  // idle · warp · intro · waitEarth · atmo · spin · reading · ask · done · fallback
  var state = "idle";

  function t(k) { return (TXT[lang] || TXT.vi)[k]; }

  function $(id) { return global.document.getElementById(id); }

  function cache() {
    el.say = $("mo-say"); el.line = $("mo-line"); el.next = $("mo-next");
    el.nm = $("mo-nm"); el.tag = $("mo-tag");
    return !!(el.say && el.line && el.next);
  }

  function show(on) {
    if (!el.say) return;
    el.say.classList.toggle("show", on !== false);
    el.say.setAttribute("aria-hidden", on === false ? "true" : "false");
  }

  /* Gõ từng chữ. Chuỗi có thẻ `<b>` nên KHÔNG gõ theo ký tự của HTML thô —
     làm vậy thì giữa lúc gõ sẽ lộ ra chữ "<b" trên màn hình. Gõ theo VĂN BẢN rồi
     mới dựng lại thẻ ở cuối. */
  function say(html, done) {
    if (typing) { clearInterval(typing); typing = null; }
    if (!el.line) return;
    if (reduced) { el.line.innerHTML = html; if (done) done(); return; }
    var plain = html.replace(/<[^>]+>/g, "");
    var i = 0;
    el.line.textContent = "";
    typing = setInterval(function () {
      i++;
      el.line.textContent = plain.slice(0, i);
      if (i >= plain.length) {
        clearInterval(typing); typing = null;
        el.line.innerHTML = html;      // dựng lại <b> sau khi gõ xong
        if (done) done();
      }
    }, TYPE_MS);
  }

  function button(label, onClick) {
    if (!el.next) return;
    if (!label) { el.next.classList.add("hide"); el.next.onclick = null; return; }
    el.next.textContent = label;
    el.next.classList.remove("hide");
    el.next.onclick = onClick;
  }

  /* ─────────────────── ① màn warp lúc vào trang ─────────────────── */
  function warp() {
    state = "warp";
    A.warpShow();
    var t0 = Date.now ? Date.now() : new Date().getTime();
    var min = reduced ? 400 : WARP_MIN_MS;
    (function wait() {
      var dt = (Date.now ? Date.now() : new Date().getTime()) - t0;

      /* ⑧ ĐƯỜNG LÙI KHI CẢNH 3D KHÔNG DỰNG ĐƯỢC (docs/decisions/003).
         ⚠️ `explorer.html` giờ nằm trên luồng onboarding **BẮT BUỘC**, mà nó nạp
            three.js + OrbitControls + EffectComposer + UnrealBloomPass + CSS2DRenderer
            từ **`unpkg.com`** — một tên miền không ai trong dự án kiểm soát. Không có
            nhánh này thì mất mạng / CDN lỗi = phi hành gia mới **không đi qua được
            onboarding**, trong khi trước lượt đổi luồng họ vẫn tới được dashboard.
         Trẻ mất màn phim, KHÔNG mất nhiệm vụ: `mission-earth.html` đã là 2D
         (`js/earth2d.js`), không cần tên miền ngoài nào. */
      if (dt >= WARP_MAX_MS && !A.ready()) {
        state = "fallback";
        /* ⚠️ ĐÁNH DẤU ĐÃ ĐI QUA KỂ CẢ Ở ĐƯỜNG LÙI, dù trẻ chưa thật sự thấy bản đồ.
           Không đánh dấu thì mỗi lần mở dashboard nó lại bị đẩy sang đây, lại lỗi, lại
           rơi vào nhiệm vụ — tức là **không bao giờ dùng được dashboard** khi mạng yếu.
           Bản đồ vẫn tới được bất cứ lúc nào từ thẻ MOD-03. */
        markSeen();
        if (A.onSceneFail) { A.onSceneFail(); return; }
        // Không khai `onSceneFail` thì thà đi tiếp nhịp phim còn hơn treo mãi ở màn warp.
        A.warpHide(); intro(); return;
      }

      if (dt >= min && A.ready()) { A.warpHide(); intro(); return; }
      setTimeout(wait, 120);
    })();
  }

  /* ─────────────────── ② + ③ Comet giới thiệu ─────────────────── */
  function intro() {
    state = "intro";
    if (!cache()) return;
    el.nm.textContent = t("nm"); el.tag.textContent = t("tag");
    button(null);
    show(true);
    say(t("l1"), function () {
      button(t("next"), function () {
        button(null);
        say(t("l2"), function () { waitEarth(); });
      });
    });
  }

  /* ─────────────────── ④ chờ trẻ chạm Trái Đất ─────────────────── */
  function waitEarth() {
    state = "waitEarth";
    var info = $("info");
    if (!info) return;

    /* Nghe THAY ĐỔI CLASS của bảng thông tin thay vì móc vào `selectBody`.
       Nhờ vậy file này không phụ thuộc nội tạng của cảnh 3D, và mọi đường mở bảng
       (chạm quả cầu · bấm nhãn · danh sách bảng trái) đều được tính. */
    var mo = new global.MutationObserver(function () {
      if (state !== "waitEarth") return;
      if (!info.classList.contains("open")) return;
      if (A.selectedId() !== "earth") return;      // mở hành tinh khác thì chưa tính
      mo.disconnect();
      touched();
      reading();
    });
    mo.observe(info, { attributes: true, attributeFilter: ["class"] });

    // Đã mở sẵn từ trước (trẻ bấm nhanh hơn lời thoại) thì tính luôn.
    if (info.classList.contains("open") && A.selectedId() === "earth") {
      mo.disconnect(); touched(); reading();
    }
  }

  /* Trẻ ĐÃ chạm Trái Đất → tắt nhãn "Bắt đầu từ đây" (`explorer.html` đọc cờ này
     trong `paintGateLabels`). Nhãn đó là một LỜI MỜI; để nguyên sau khi trẻ đã làm
     theo thì nó đọc ra thành "em làm chưa đúng, làm lại đi". */
  function touched() {
    global._gateTouched = true;
    if (A && A.repaintLabels) A.repaintLabels();
  }

  /* ─────────────────── NHỊP 0: khí quyển → mời xoay → ngày/đêm ───────────────────
     Thêm 02/08/2026 (`docs/decisions/005` mục 1). Đây là **PHẦN THÊM, không phải bài
     học bắt buộc** (mục 5 của `005`): mọi thứ BẮT BUỘC phải nằm trong 7 bước của
     `mission-earth.html`, vì mạng kém thì đường lùi 12 giây bỏ qua hẳn cảnh 3D này.

     ⚠️ VÌ SAO DẠY NGÀY/ĐÊM Ở ĐÂY CHỨ KHÔNG Ở BẢN ĐỒ PHẲNG. `004` định dạy nó bằng
        gradient `.e2-terminator` trên bản đồ phẳng, với lý lẽ "chỗ phẳng tốt hơn quả
        cầu vì thấy cả hai nửa". Lý lẽ đó đúng về NỘI DUNG nhưng sai về HÌNH ẢNH: chủ
        dự án chơi thật và gửi ảnh chụp — nó trông như một bức tường đen. Quả cầu ở
        đây thì có ranh giới THẬT: `MeshStandardMaterial` + `PointLight` gắn vào chính
        Mặt Trời của cảnh. Đo được (`scratchpad/probe_globe_daynight.py`) hai nửa chênh
        **106,5 điểm độ sáng, tỉ số 2,94×** → KHÔNG cần chỉnh đèn.

     ⚠️ QUẢ CẦU KHÔNG BAO GIỜ ĐƯỢC MANG ĐIỀU KIỆN THẮNG. Đây là chỗ *quan sát*, không
        phải chỗ *giải*. Điều kiện thắng đo trên camera-orbit chính là lỗi đã làm bước
        `rotation` của bản 3D **không thể hoàn thành** và **treo vĩnh viễn** ở chế độ
        giảm chuyển động. Ở đây không có gì để đo sai, nên không có gì để treo.

     ⚠️ `l3b` NÓI THẲNG RẰNG VÀNH KHÍ QUYỂN ĐANG BỊ VẼ DÀY QUÁ. Đo trên ảnh chụp: vành
        to gấp ~2 lần bán kính hành tinh và trông đặc như bi thuỷ tinh, trong khi khí
        quyển thật là một lớp da rất mỏng. Chỉ vào đó mà không nói gì là **dạy sai mô
        hình tư duy** — đúng loại lỗi mà bước ③ đang cố tránh ("không phải vì gần Mặt
        Trời"). Nói thật rẻ hơn và trung thực hơn là đi sửa hình. */
  function reading() {
    state = "atmo";
    if (!cache()) { ask(); return; }
    show(true);
    button(null);
    say(t("l3"), function () {
      button(t("next"), function () {
        button(null);
        say(t("l3b"), function () {
          button(t("next"), function () {
            button(null);
            state = "spin";
            say(t("l4"), function () {
              /* ⚠️⚠️ BẤM "TIẾP TỤC" LÀ SANG NGAY — KHÔNG CÒN MỐC CHỜ (đổi 02/08/2026).
                 Chủ dự án chơi thật: *"sau khi trẻ ngắm Trái Đất, ấn nút Tiếp tục sẽ
                 phải chuyển sang ngay phần tiếp, không chờ."*
                 ⛔ ĐÂY LÀ ĐẢO MỘT QUYẾT ĐỊNH CŨ, ĐỪNG KHÔI PHỤC. `003` chốt "10 giây
                    là SÀN, không phải hạn" và `005` nới lên 15 — nhưng cái SÀN đó
                    sinh ra khi nhịp phim CHƯA có nhịp 0: lúc ấy Comet nói xong là
                    box tự ẩn, không có nút nào, nên phải có đồng hồ mới biết khi nào
                    hỏi tiếp. Nay nhịp 0 kết bằng một NÚT do trẻ chủ động bấm, mà một
                    cái nút tên "Tiếp tục" rồi bắt ngồi đợi thêm 15 giây trong im lặng
                    thì chính nó là lỗi — trẻ sẽ tưởng trang treo và bấm loạn.
                 Trẻ muốn ngắm bao lâu tuỳ ý: box thoại nay KHÔNG tự ẩn, nút cứ nằm
                 đó chờ. Quyền quyết định lúc nào đi tiếp trả về cho trẻ, đúng tinh
                 thần "SÀN chứ không phải HẠN" — chỉ là bỏ luôn cái đồng hồ. */
              button(t("next"), function () { button(null); ask(); });
            });
          });
        });
      });
    });
  }

  function ask() {
    state = "ask";
    if (!cache()) return;
    show(true);
    say(t("ask"), function () {
      button(t("ok"), function () {
        state = "done";
        button(null);
        markSeen();          // ghi cache TRƯỚC khi rời trang — xem SEEN_KEY ở trên
        A.onGo();
      });
    });
  }

  global.AstroQMapOnboard = {
    /** Nhịp phim chạy được thì trả true. Thiếu hàm nào là không chạy, không nửa vời. */
    init: function (api) {
      if (!api || !api.warpShow || !api.warpHide || !api.ready ||
          !api.selectedId || !api.onGo) return false;
      A = api;
      lang = api.lang === "en" ? "en" : "vi";
      try { reduced = global.matchMedia("(prefers-reduced-motion: reduce)").matches; }
      catch (e) { reduced = false; }
      if (!cache()) return false;
      warp();
      return true;
    },

    /** Đổi ngôn ngữ giữa chừng (tab khác bấm VI/EN) — dịch lại đúng câu đang hiện. */
    setLang: function (l) {
      lang = l === "en" ? "en" : "vi";
      if (!cache() || state === "idle" || state === "done") return;
      el.nm.textContent = t("nm"); el.tag.textContent = t("tag");
      if (state === "ask") { el.line.innerHTML = t("ask"); button(t("ok"), el.next.onclick); }
      else if (state === "atmo") { el.line.innerHTML = t("l3"); if (el.next && !el.next.classList.contains("hide")) el.next.textContent = t("next"); }
      else if (state === "spin") { el.line.innerHTML = t("l4"); if (el.next && !el.next.classList.contains("hide")) el.next.textContent = t("next"); }
      else if (state === "intro" || state === "waitEarth") { el.line.innerHTML = t("l2"); }
    },

    /** Bề mặt cho bộ test: đọc trạng thái + rút ngắn mốc chờ. */
    _state: function () { return state; },
    /** Rút hạn chờ cảnh 3D — để test đo được đường lùi mà không phải ngồi 12 giây. */
    _setWarpMaxMs: function (ms) { WARP_MAX_MS = Math.max(0, ms | 0); },
    WARP_MAX_MS: WARP_MAX_MS,

    /** Xem lại nhịp phim: Console gõ `AstroQMapOnboard.reset()` rồi mở
     *  `explorer.html?onboard=1`. Chỉ xoá CACHE trong máy — cờ thật ở server thì
     *  dùng `AstroQAuth.setOnboarding({ map01Seen:false })` trên một trang có token. */
    reset: function () {
      try { global.localStorage.removeItem(SEEN_KEY); } catch (e) {}
    },
    SEEN_KEY: SEEN_KEY
  };
})(window);
