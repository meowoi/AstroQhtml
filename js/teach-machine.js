/* DẠY MÁY MỘT KHÁI NIỆM — bộ phân loại đồ chơi + kho "ảnh quét", dùng chung.
   ────────────────────────────────────────────────────────────────────────────
   Người dùng: `game-classify.html` (ARCADE-12, Đợt 1) và — theo `docs/proposals/
   2026-09-05-trend-ai-va-cua-truoc-astroq.md` — chặng ② của nhiệm vụ "Mắt Máy"
   (Đợt 2). Tách ra NGAY từ đầu chính vì lý do đó: đề xuất nói rõ chặng ② "dùng
   lại engine của Đợt 1", mà chép một bộ phân loại sang trang thứ hai là hai bản
   sẽ trôi khỏi nhau (quy tắc 2 mục 6).

   ⚠️⚠️ KHÔNG TENSORFLOW, KHÔNG MỘT BYTE MẠNG NÀO. Một bộ k-NN trên 2 đặc trưng
      số là ĐỦ để dạy *dữ liệu huấn luyện → mô hình → thiên lệch*. Kéo một thư
      viện ML về là hoàn tác đúng đợt gỡ `unpkg`/`gstatic` ngày 07/08/2026 và
      đóng lại đường PWA (service worker không cache đàng hoàng được phản hồi
      cross-origin không CORS).

   ⚠️⚠️ VÌ SAO k-NN CHỨ KHÔNG PHẢI PERCEPTRON — và đây là quyết định về NỘI DUNG
      chứ không phải về code. k-NN quyết định bằng "mẫu này giống những mẫu con
      đã dạy nào nhất", nên câu giải thích cho trẻ *"tớ chưa từng thấy cái nào
      giống thế này"* là MÔ TẢ ĐÚNG cách nó chạy, không phải một phép ví von
      dựng thêm. Perceptron thì phải nói về trọng số và đường ranh giới — khó
      hơn, và câu giải thích sẽ là một lớp ẩn dụ phủ lên thứ khác.

   ⚠️ MỌI CON SỐ Ở ĐÂY LÀ MÔ PHỎNG. Ba đặc trưng (dài · cong · sáng) là bộ số
      dựng ra để chơi; NASA không công bố bộ đặc trưng nào như thế. Trang phải
      mang nhãn "MÔ PHỎNG" thường trực — cùng luật đã áp cho `game-recycle`,
      `game-units` và `mission-orbit`. ⛔ Đừng bỏ nhãn đó cho gọn.

   NGUỒN (ba bài đọc ĐÃ CÓ trong kho, đã trích nguyên văn, URL đã kiểm 200):
     · `art-ai-finds-asteroids-hubble` — tiểu hành tinh bay ngang khung hình để
       lại một VỆT CONG; 30.000 ảnh Hubble → 1.031 tiểu hành tinh mới; và con số
       đáng nhớ hơn: đó là AI **cộng với** ~11.000 tình nguyện viên.
     · `art-ai-found-binary-stars` — "AI *giúp* họ": máy lọc bớt phần khổng lồ để
       người chỉ phải xem phần đáng xem.
     · `art-ai-tags-nasa-data` — "cho nó xem càng nhiều ví dụ đúng, nó càng đề
       xuất giỏi. Dữ liệu không phải thứ phụ — **dữ liệu chính là bài học**."
       (bản mới: 430 → hơn 3.200 từ khoá, 2.000 → hơn 43.000 bản ghi.)
   ⛔ ĐỪNG viết rằng NASA phân loại ảnh bằng "độ dài và độ cong của vệt" — không
      trang nào nói thế. Thứ có nguồn là *vệt cong là manh mối*, còn bộ đặc trưng
      là của trò chơi này.
*/
(function (global) {
  "use strict";

  /* ── Ba loại vật thể. `truth` là nhãn ĐÚNG, chỉ dùng để chấm điểm và để dựng
        đề — bộ phân loại KHÔNG bao giờ đọc nó. ─────────────────────────────── */
  var AST = "ast";      /* vệt của tiểu hành tinh — thứ đáng giữ  */
  var NOISE = "noise";  /* mọi thứ khác: tia vũ trụ, sao, nhiễu    */

  /* ── ĐẶC TRƯNG ─────────────────────────────────────────────────────────────
     len   0..1  vệt dài bao nhiêu (0 = một chấm)
     curve 0..1  vệt cong bao nhiêu (0 = thẳng băng)
     bright 0..1 sáng bao nhiêu
     ⚠️ Bộ phân loại CHỈ dùng `len` và `curve`. `bright` cố ý KHÔNG đưa vào —
        nó là một đặc trưng GÂY NHIỄU có chủ đích: tia vũ trụ rất sáng, nên trẻ
        nào gán nhãn theo độ sáng sẽ dạy máy một luật sai. Đó là bài học của
        vòng ③, và nó chỉ dựng được nếu đặc trưng gây nhiễu có mặt trên màn
        hình mà không nằm trong phép tính.                                     */
  var FEAT = ["len", "curve"];

  function mk(id, len, curve, bright, truth, why) {
    return { id: id, len: len, curve: curve, bright: bright,
             truth: truth, why: why || null };
  }

  /* ── KHO MẪU ───────────────────────────────────────────────────────────────
     Chia theo VÙNG chứ không xếp ngẫu nhiên, vì cả bài học thiên lệch dựa vào
     việc một vùng bị BỎ TRỐNG trong bộ dạy. Xem `ROUNDS` ở game để biết vòng
     nào đưa vùng nào vào.                                                      */
  var POOL = {
    /* Vệt cong RÕ — tiểu hành tinh dễ nhận. Vùng "dạy" của vòng ①.            */
    curved_bright: [
      mk("cb1", 0.72, 0.78, 0.86, AST),
      mk("cb2", 0.80, 0.71, 0.80, AST),
      mk("cb3", 0.66, 0.85, 0.90, AST),
      mk("cb4", 0.77, 0.66, 0.83, AST)
    ],
    /* Chấm sáng — sao nền. Vùng "dạy" của vòng ①.                             */
    dots: [
      mk("d1", 0.06, 0.10, 0.92, NOISE),
      mk("d2", 0.10, 0.05, 0.78, NOISE),
      mk("d3", 0.04, 0.14, 0.85, NOISE),
      mk("d4", 0.12, 0.08, 0.70, NOISE)
    ],
    /* ⚠️ VỆT CONG MỜ — VÙNG BỊ BỎ TRỐNG Ở VÒNG ①. Cùng hình dạng với
       `curved_bright` (dài + cong) nhưng mờ. Vì bộ phân loại không đọc `bright`
       nên nó vẫn đoán ĐÚNG mấy mẫu này — và đó KHÔNG phải chỗ thiên lệch nằm.
       Chỗ thiên lệch nằm ở `curved_short` ngay dưới.                          */
    curved_faint: [
      mk("cf1", 0.70, 0.74, 0.30, AST),
      mk("cf2", 0.63, 0.80, 0.22, AST),
      mk("cf3", 0.75, 0.69, 0.34, AST)
    ],
    /* ⚠️⚠️ VỆT CONG NGẮN — ĐÂY LÀ VÙNG TRỐNG THẬT SỰ CỦA VÒNG ①, VÀ BỘ SỐ CỦA
       NÓ PHẢI ĐO CHỨ KHÔNG ĐOÁN. Một tiểu hành tinh nhỏ chỉ lướt qua góc khung
       thì vệt vừa NGẮN vừa cong ÍT hơn — cung ngắn thì độ cong nhìn thấy nhỏ đi,
       đó là chuyện có thật chứ không phải bịa cho vừa bài học.
       ⚠️⚠️ BẢN ĐẦU ĐẶT (0.30, 0.72) VÀ THIÊN LỆCH KHÔNG XẢY RA — bộ đo bắt được.
       Lý do là hình học: hai cụm đã dạy nằm ở hai đầu đường chéo (chấm ~(0.08,
       0.09) và cong-dài ~(0.74, 0.75)), nên ranh giới của k-NN xấp xỉ đường
       `len + curve ≈ 0.83`. Điểm (0.30, 0.72) có tổng 1.02 ⇒ vẫn rơi về phía
       "tiểu hành tinh" và máy đoán ĐÚNG. Muốn máy SAI thì vùng trống phải nằm
       DƯỚI ranh giới đó: (0.26, 0.40) có tổng 0.66 ⇒ ba láng giềng gần nhất đều
       là mấy cái chấm ⇒ máy đoán NHIỄU. Máy sai vì bộ dạy thiếu, không phải vì
       thuật toán tồi — đúng bài học cần.
       ⛔ ĐỔI BỘ SỐ NÀY (hoặc đổi `curved_bright`/`dots`) THÌ CHẠY LẠI
          `scratchpad/check_teach_engine.py` TRƯỚC — ranh giới dịch một chút là
          cả vòng ① mất bài học mà màn hình vẫn trông y hệt.                    */
    curved_short: [
      mk("cs1", 0.26, 0.40, 0.64, AST, "short"),
      mk("cs2", 0.22, 0.34, 0.58, AST, "short"),
      mk("cs3", 0.30, 0.44, 0.70, AST, "short")
    ],
    /* Tia vũ trụ: THẲNG, rất sáng, dài vừa. Bẫy của vòng ③ — trẻ gán nhãn theo
       "sáng thì chắc là tiểu hành tinh" sẽ dạy sai.                            */
    rays: [
      mk("r1", 0.58, 0.06, 0.97, NOISE, "ray"),
      mk("r2", 0.64, 0.03, 0.94, NOISE, "ray"),
      mk("r3", 0.52, 0.09, 0.99, NOISE, "ray"),
      mk("r4", 0.70, 0.05, 0.92, NOISE, "ray")
    ],
    /* Vệt dài cong vừa — mẫu kiểm "dễ", để mẻ kiểm nào cũng có cái máy làm đúng.
       Một mẻ mà máy sai hết thì trẻ đọc ra là "máy hỏng", không ra "dữ liệu thiếu". */
    curved_mid: [
      mk("cm1", 0.55, 0.58, 0.66, AST),
      mk("cm2", 0.61, 0.52, 0.74, AST),
      mk("cm3", 0.49, 0.63, 0.60, AST)
    ]
  };

  function pool(name) {
    var a = POOL[name] || [];
    return a.map(function (s) { return s; });
  }

  /* ── BỘ PHÂN LOẠI ──────────────────────────────────────────────────────────
     k-NN, k = 3 (hoặc nhỏ hơn nếu bộ dạy ít hơn 3 mẫu). Khoảng cách Euclid trên
     hai đặc trưng đã nằm sẵn trong [0,1] nên không cần chuẩn hoá thêm.
     ⚠️ TẤT ĐỊNH: không có `Math.random()` ở đâu trong đây. Hai lượt cùng bộ dạy
        và cùng mẫu kiểm PHẢI cho ra cùng một kết quả — không thì bộ đo thành
        chập chờn và cả phần "vì sao máy sai" không giải thích được.
        Hoà phiếu thì xử theo láng giềng GẦN NHẤT (đã sắp theo khoảng cách).   */
  function dist(a, b) {
    var s = 0, i, d;
    for (i = 0; i < FEAT.length; i++) { d = a[FEAT[i]] - b[FEAT[i]]; s += d * d; }
    return Math.sqrt(s);
  }

  function train(labeled) {
    /* `labeled` = [{ sample, label }]. Nhãn do TRẺ đặt, có thể sai — đó là
       chuyện bình thường và chính là thứ trò chơi muốn cho thấy. */
    var pts = [];
    for (var i = 0; i < labeled.length; i++) {
      var L = labeled[i];
      if (!L || !L.sample || (L.label !== AST && L.label !== NOISE)) continue;
      pts.push({ s: L.sample, label: L.label });
    }
    return { pts: pts, k: Math.min(3, pts.length || 1) };
  }

  function predict(model, sample) {
    if (!model || !model.pts.length) return null;
    var near = model.pts.map(function (p) {
      return { label: p.label, s: p.s, d: dist(p.s, sample) };
    }).sort(function (a, b) { return a.d - b.d; });

    var k = Math.min(model.k, near.length);
    var votes = {}, i;
    votes[AST] = 0; votes[NOISE] = 0;
    for (i = 0; i < k; i++) votes[near[i].label]++;

    var label = votes[AST] === votes[NOISE] ? near[0].label
              : (votes[AST] > votes[NOISE] ? AST : NOISE);

    return {
      label: label,
      /* Số phiếu — dùng để nói "3/3 hàng xóm nói vậy" chứ không phải một con số
         phần trăm bịa ra. Đừng gọi nó là "độ tự tin %": k-NN không cho ra xác
         suất, và in một con số nghe như xác suất là dạy sai. */
      votes: votes[label], of: k,
      /* Láng giềng gần nhất + khoảng cách tới nó. Đây là thứ dựng câu giải
         thích trung thực: máy quyết theo mấy mẫu này, và nếu chúng đều XA thì
         nghĩa là bộ dạy chưa có gì giống mẫu đang xét. */
      nearest: near[0].s, gap: near[0].d,
      neighbors: near.slice(0, k)
    };
  }

  /* Mẫu kiểm có nằm ngoài vùng đã dạy không — chỉ dùng để CHỌN CÂU CHỮ, không
     dùng để phân loại, nên sai ngưỡng thì lời giải thích kém sắc chứ không làm
     máy đoán khác.
     ⚠️ NGƯỠNG 0,15 LÀ SỐ ĐO, KHÔNG PHẢI SỐ ĐOÁN. Bản đầu tôi đặt 0,28 theo phỏng
        đoán "chấm ↔ cong-ngắn ≈ 0,3–0,4"; đo thật khoảng cách tới láng giềng gần
        nhất (bộ dạy = cong-dài + chấm) thì ra: đã dạy 0,000 · cong-mờ 0,036–0,058
        · cong-vừa 0,213–0,275 · cong-ngắn 0,269–0,397 · tia vũ trụ 0,400–0,581.
        Khoảng trống DUY NHẤT là 0,058 → 0,213, nên ngưỡng phải nằm trong đó.
     ⚠️⚠️ VÀ NÓ ĐÁNH DẤU CẢ `curved_mid` — VÙNG MÀ MÁY ĐOÁN ĐÚNG. Đó KHÔNG phải
        lỗi ngưỡng: ở vòng ① thì cong-vừa cũng là thứ máy chưa từng được dạy.
        Tức cờ này nói *"tớ chưa từng thấy cái nào giống thế này"*, **không** nói
        *"tớ đoán sai"* — và máy thì không có cách nào biết mình sai. ⛔ Đừng
        "sửa" bằng cách nâng ngưỡng cho `curved_mid` khỏi bị đánh dấu: làm thế là
        dạy trẻ rằng máy tự biết lúc nào nó sai, một điều không đúng.
     ⛔ Đổi bộ số của `POOL` thì đo lại phân bố này TRƯỚC khi chỉnh ngưỡng.      */
  function isFar(res) { return !!res && res.gap > 0.15; }

  /* ── VẼ MỘT "ẢNH QUÉT" ────────────────────────────────────────────────────
     Trả về chuỗi SVG. Vẽ bằng code nên 0 file ảnh, 0 byte tải thêm — cùng lối
     `js/specimen-art.js` (21 bức) và `js/sticker-icons.js` đã dùng.
     ⚠️ ID gradient mang HẬU TỐ ĐẾM: một mẻ vẽ 6–8 ảnh cùng lúc trên một trang,
        id trùng thì bản sau "ăn" gradient của bản trước và cả lưới đổi màu —
        bài học đã ghi ở `js/sticker-icons.js` và `js/specimen-art.js`.        */
  var seq = 0;

  function svg(s, opt) {
    opt = opt || {};
    var n = ++seq;
    var W = 100, H = 100, cx = 50, cy = 50;
    /* Độ dài vẽ ra: một chấm vẫn phải thấy được, nên có sàn. */
    var L = 10 + s.len * 62;
    var bend = s.curve * 26;
    var a = -28;                       /* nghiêng cố định cho cả mẻ trông cùng một kiểu quét */
    var rad = a * Math.PI / 180;
    var dx = Math.cos(rad) * L / 2, dy = Math.sin(rad) * L / 2;
    /* Điểm điều khiển lệch theo PHÁP TUYẾN của đường, không lệch theo trục Y —
       lệch theo Y thì vệt nghiêng sẽ phình ở chỗ dốc (bài học vệt sáng của
       ARCADE-01 và vệt đuôi tàu 21/08/2026). */
    var nx = -Math.sin(rad) * bend, ny = Math.cos(rad) * bend;
    var x1 = cx - dx, y1 = cy - dy, x2 = cx + dx, y2 = cy + dy;
    var qx = cx + nx, qy = cy + ny;
    var op = 0.25 + s.bright * 0.75;
    var w = 2.4 + s.bright * 2.2;

    var stars = "";
    /* Sao nền TẤT ĐỊNH theo id mẫu — hai lần vẽ cùng một mẫu phải ra cùng một
       bức. Random thật thì ảnh nhảy mỗi lần vẽ lại (đổi ngôn ngữ cũng vẽ lại). */
    var h = 0, i;
    for (i = 0; i < s.id.length; i++) h = (h * 31 + s.id.charCodeAt(i)) % 9973;
    for (i = 0; i < 7; i++) {
      h = (h * 1103515245 + 12345) % 2147483648;
      var sx = 6 + (h % 88), sy = 6 + ((h >> 7) % 88), sr = 0.5 + ((h >> 14) % 3) * 0.35;
      stars += '<circle cx="' + sx + '" cy="' + sy + '" r="' + sr.toFixed(2) +
               '" fill="#cfe3ff" opacity="' + (0.18 + ((h >> 3) % 30) / 100).toFixed(2) + '"/>';
    }

    return '' +
      '<svg class="tm-shot" viewBox="0 0 ' + W + ' ' + H + '" role="img" ' +
        'aria-label="' + (opt.alt || "") + '">' +
        '<defs><linearGradient id="tmg' + n + '" x1="' + x1 + '" y1="' + y1 +
          '" x2="' + x2 + '" y2="' + y2 + '" gradientUnits="userSpaceOnUse">' +
          '<stop offset="0" stop-color="#9fd8ff" stop-opacity="' + (op * 0.35).toFixed(2) + '"/>' +
          '<stop offset=".5" stop-color="#eaf4ff" stop-opacity="' + op.toFixed(2) + '"/>' +
          '<stop offset="1" stop-color="#9fd8ff" stop-opacity="' + (op * 0.35).toFixed(2) + '"/>' +
        '</linearGradient></defs>' +
        '<rect width="' + W + '" height="' + H + '" fill="#070c1c"/>' + stars +
        (s.len < 0.16
          /* Chấm: vẽ hẳn một chấm tròn có quầng. Vẽ một đoạn cực ngắn thì ở cỡ
             nhỏ nó đọc ra thành một vết bẩn, không ra một ngôi sao. */
          ? '<circle cx="' + cx + '" cy="' + cy + '" r="' + (3.2 + s.bright * 2.4).toFixed(1) +
              '" fill="#eaf4ff" opacity="' + op.toFixed(2) + '"/>' +
            '<circle cx="' + cx + '" cy="' + cy + '" r="' + (7 + s.bright * 4).toFixed(1) +
              '" fill="#9fd8ff" opacity="' + (op * 0.18).toFixed(2) + '"/>'
          : '<path d="M' + x1.toFixed(1) + ' ' + y1.toFixed(1) +
              ' Q' + qx.toFixed(1) + ' ' + qy.toFixed(1) +
              ' ' + x2.toFixed(1) + ' ' + y2.toFixed(1) + '" fill="none" ' +
              'stroke="url(#tmg' + n + ')" stroke-width="' + w.toFixed(1) +
              '" stroke-linecap="round"/>') +
      '</svg>';
  }

  global.AstroQTeach = {
    AST: AST, NOISE: NOISE, FEAT: FEAT,
    pool: pool, train: train, predict: predict, isFar: isFar, svg: svg,
    dist: dist,
    /* Mở cho bộ đo: nó phải duyệt HẾT kho mẫu để chứng minh cân bằng, y như
       `play_recycle` duyệt 21 tổ hợp chia điện và `play_units` duyệt 5 bảng. */
    POOL: POOL
  };
})(window);
