/* ============================================================
   game-shell.js — PHẦN JS DÙNG CHUNG CỦA MỌI MINI-GAME, đi kèm `css/game-shell.css`.
   Nạp ở cả 3 game, SAU `js/ui-common.js`. Làm đúng hai việc:

     ① SÂN CHIẾM HẾT CHỖ CÒN LẠI  (`--field-w`)
     ② NHẮC XOAY NGANG trên máy cảm ứng đang để dọc

   ── ① VÌ SAO CẦN, VÀ VÌ SAO KHÔNG LÀM ĐƯỢC BẰNG CSS THUẦN ─────────────────
   Trước 12/08/2026 mỗi game khai `.field{max-width:800px}` (defender 600px) — tức
   ĐỘ PHÂN GIẢI ẢO bị rò vào bố cục thành một cái chặn bằng pixel. Đo bằng
   `scratchpad/probe_field_space.py`:

     Full HD 1920×1080   sân 800×500   vừa được 1530×956   → bỏ không 73% diện tích
     MacBook Air 13"     sân 800×500   vừa được 1331×832   → bỏ không 64%
     iPad Pro ngang      sân 800×500   vừa được 1318×824   → bỏ không 63%
     iPhone dọc          sân 366×229   vừa được 366×229    → bỏ không 0%

   ⚠️ PHÓNG TO SÂN KHÔNG ĐỔI ĐỘ KHÓ MỘT CHÚT NÀO — đây là điều kiện tiên quyết, đã
      đối chiếu mã: `fit()` của cả 3 game đặt
      `ctx.setTransform(cv.width/VW, 0, 0, cv.height/VH, 0, 0)`, nên toàn bộ thế
      giới ảo (800×500 · 600×600) được scale ra đúng cỡ phần tử. Mọi phép va chạm,
      mọi hằng số vật lý đều tính trong hệ ảo. Thứ duy nhất đổi là số pixel phải tô.
   ⚠️ CSS thuần KHÔNG làm được vừa-khít-hai-chiều: `width:100%` + `aspect-ratio` +
      `max-height:100%` thì khi chiều cao bị kẹp, bề rộng KHÔNG tự co theo (bề rộng
      đã là giá trị xác định), nên tỉ lệ vỡ — canvas bị kéo méo và `setTransform`
      nhận hai hệ số scale khác nhau. Đường `min(100cqw, 100cqh * ar)` thì cần
      `container-type:size`, mà cái đó áp *size containment* lên `.play` — nơi đang
      chứa mọi lớp phủ `.ov`. Đo một con số rồi gán vào biến là đường ít rủi ro nhất.

   ── ② VÌ SAO NHẮC XOAY, VÀ VÌ SAO KHÔNG CHẶN CỨNG ─────────────────────────
   Cũng số đo trên: iPad mini để DỌC cho sân 699×437, để NGANG cho 992×620 — hơn
   gấp đôi diện tích. Trên điện thoại còn chênh hơn nữa. Nên nhắc là đáng.
   ⚠️ NHƯNG PHẢI CÓ ĐƯỜNG RA (`Vẫn chơi kiểu dọc`): rất nhiều máy đang BẬT KHOÁ
      XOAY, và người dùng đó xoay máy thì màn hình không xoay. Chặn cứng là trẻ
      kẹt trước một câu lệnh nó không thi hành được — đúng loại lỗi dự án đã trả
      giá nhiều lần ("im lặng thì trẻ chỉ tưởng mình bấm trượt").
   ⚠️ KHÔNG BAO GIỜ hiện lời nhắc KHI ĐANG CHƠI. Nhận biết bằng chính hợp đồng của
      khung dùng chung: lúc game chạy thì MỌI lớp phủ đều tắt, nên `.ov.show` không
      tồn tại. Hiện lời nhắc giữa lượt chơi là lấy mất một lượt của trẻ.
   ============================================================ */
(function (global) {
  "use strict";

  var doc = global.document;
  if (!doc) return;

  /* ── ① Sân chiếm hết chỗ ────────────────────────────────────────────── */

  /* Tỉ lệ sân đọc từ `--ar` mà từng `css/<game>.css` khai trên `.field` — cùng một
     chỗ đã khai `aspect-ratio`, nên hai giá trị không thể lệch nhau mà không thấy. */
  function ratioOf(field) {
    var v = parseFloat(getComputedStyle(field).getPropertyValue("--ar"));
    return (v > 0.1 && v < 10) ? v : 8 / 5;
  }

  var lastW = -1;

  /* ⚠️ TRẦN BỀ RỘNG SÂN — "sân vừa phải trong một khung có trang trí" (chủ dự án chốt
     12/08/2026 sau khi soi `scratchpad/proto-game-frame.html`). 1120px = **1,4 lần** hệ
     ảo 800×500, nên sprite vẫn thu-nhỏ chứ không phóng-to (ảnh `luna-side.png` rộng
     192px được vẽ ở 158px), và còn chỗ cho console hai bên.
     ⚠️ Trần này KHÔNG áp cho màn hẹp: ở đó không có console nào để chừa chỗ, mà thu
        sân nhỏ lại là lấy đi thứ duy nhất trẻ đang nhìn. */
  var PORT_MAX = 1120;

  function sizeField() {
    var stage = doc.querySelector(".stage"),
        play  = doc.querySelector(".play"),
        field = doc.querySelector(".field");
    if (!stage || !play || !field) return;

    var cs = getComputedStyle(play);
    var w = play.clientWidth  - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    var h = play.clientHeight - parseFloat(cs.paddingTop)  - parseFloat(cs.paddingBottom);
    if (!(w > 0) || !(h > 0)) return;

    var wide = global.matchMedia ? global.matchMedia("(min-width: 901px)").matches : w > 900;
    if (wide) w = Math.min(w, PORT_MAX);

    var fw = Math.floor(Math.min(w, h * ratioOf(field)));
    /* ⚠️ Chỉ ghi khi lệch >0,5px. Đặt `--field-w` làm thanh HUD rộng ra → HUD bớt
       xuống dòng → `.play` cao hơn → sân rộng hơn nữa; vòng đó tự dừng sau 1–2 nhịp
       (bề rộng bị `w` kẹp), nhưng không có phép so này thì ResizeObserver kêu mãi. */
    if (Math.abs(fw - lastW) < 0.5) return;
    lastW = fw;
    stage.style.setProperty("--field-w", fw + "px");
    /* `--fh` để CSS neo bốn góc kim loại vào MÉP SÂN. Neo vào `.play` thì góc trôi ra
       xa cả trăm pixel, vì `.play` cao hơn sân (nó canh giữa sân theo trục dọc). */
    stage.style.setProperty("--fh", Math.round(fw / ratioOf(field)) + "px");
  }

  /* ── ①c Console phải + thanh tiến độ cấp ───────────────────────────────
     Dựng bằng JS để markup 3 game không phải sửa một dòng nào. */

  /* ── Bạn đồng hành: ai đi với game nào, và ba biểu cảm ──────────────────
     ⚠️⚠️ TRƯỚC 16/08/2026 CHỖ NÀY CHỈ CÓ 3 GAME và một chân dung TĨNH, kèm ghi
        chú "mỗi linh vật chỉ có MỘT ảnh nên không phản ứng được". Ghi chú đó SAI:
        art biểu cảm đã nằm trong `img/` từ đợt tối ưu 26/07 (m2/m4 · b3/b4), nằm
        đúng trong danh sách "11 ảnh chưa ai dùng". Nay `img/mate/` là bản đã đưa
        về cùng khung; xem `scratchpad/make_mate_assets.py`.
     ⚠️ KHAI ĐỦ CẢ 10 GAME. Bỏ trống 7 game như trước thì bảy màn chơi không có ai
        bên cạnh — mà "trẻ chơi một mình" chính là chỗ tính năng này sinh ra để
        chữa. Thêm game mới thì thêm một dòng ở đây.
     ⚠️ CHỌN AI ĐI VỚI GAME NÀO THEO NỘI DUNG, không rải cho đều: Byte (robot) đi
        với thứ máy móc/dữ liệu, Comet đi với thứ bầu trời/sinh tồn/khám phá. */
  var MASCOT = {
    byte:  { nm: "BYTE",  dir: "img/mate/byte-"  },
    comet: { nm: "COMET", dir: "img/mate/comet-" }
  };
  var MATE = { "game-dodge":         "byte",
               "game-defender":      "byte",
               "game-constellation": "comet",
               "game-racer":         "comet",
               "game-maze":          "byte",
               "game-catch":         "comet",
               "game-survival":      "comet",   /* sinh tồn — chọn thứ cần để sống */
               "game-comms":         "byte",    /* dãy lệnh gửi lên tàu */
               "game-recycle":       "byte",    /* ba hệ thống của trạm */
               "game-units":         "byte",   /* soi bảng số liệu */
               "game-route":         "byte",   /* mạng điện của trạm */
               "game-classify":      "byte" }; /* dạy máy phân loại — và `role`
                  của Byte trong js/characters.js đúng là "Kỹ sư hệ thống" */

  var mateEl = null, mateImg = null, mateSrc = null, mateTimer = 0;

  function mateUrl(kind, state) { return MASCOT[kind].dir + state + ".png"; }

  function mountSide() {
    var stage = doc.querySelector(".stage");
    if (!stage || doc.querySelector(".gs-side")) return;
    var key = (location.pathname.split("/").pop() || "").replace(".html", "");
    var kind = MATE[key];
    if (!kind) return;                    /* game mới chưa khai thì thôi, không vỡ */
    var side = doc.createElement("aside");
    side.className = "gs-side";
    side.setAttribute("aria-hidden", "true");   /* trang trí — trình đọc màn hình bỏ qua */
    side.innerHTML = '<div class="gs-mate"><img src="' + mateUrl(kind, "idle") +
                     '" alt=""><span class="nm">' + MASCOT[kind].nm + "</span></div>";
    stage.appendChild(side);
    mateEl = side.querySelector(".gs-mate");
    mateImg = mateEl.querySelector("img");
    mateSrc = "idle";

    /* ⚠️ TẢI TRƯỚC HAI ẢNH PHẢN ỨNG. Không tải trước thì lần đầu trẻ làm đúng,
       trình duyệt mới bắt đầu kéo ảnh về — và trong lúc chờ nó **vẫn vẽ khung ảnh
       CŨ**, tức linh vật "phản ứng" bằng đúng khuôn mặt bình thường rồi mới đổi
       muộn. Đó chính là lỗi ảnh mốc thời gian của Nhiệm vụ 01 (03/08). */
    ["cheer", "oops"].forEach(function (s) {
      var p = new Image(); p.src = mateUrl(kind, s);
    });
  }

  /* Game gọi: AstroQGameShell.mate("cheer" | "oops")  → đổi biểu cảm rồi tự về
     bình thường sau `MATE_MS`. Gọi `mate(null)` để về ngay (lúc bắt đầu lượt mới).
     ⚠️ TUYỆT ĐỐI KHÔNG GỌI TỪ VÒNG VẼ. Nó ghi `src` + `className`, tức ép trình
        duyệt tính lại bố cục; gọi 60 lần/giây là đúng cái lỗi `setLevel` đã mắc và
        đã phải chữa bằng `barCache`. Chỉ gọi ở đúng lúc có KẾT QUẢ. */
  var MATE_MS = 1500;      /* giữ biểu cảm bao lâu rồi tự về bình thường */
  /* ⚠️⚠️ VAN CHẶN GHI DOM DỒN DẬP — BẮT BUỘC, VÀ ĐÂY LÀ SỐ ĐO CHỨ KHÔNG PHẢI ĐỀ
     PHÒNG SUÔNG. Ở 4 game canvas, lời gọi nằm trong nhánh `if` của `update()` —
     tức không chạy mỗi khung hình, NHƯNG một loạt viên thiên thạch nhặt liên tiếp
     (hoặc mấy hòn đá đâm vào Trạm trong cùng một giây) thì gọi nhiều lần/giây, mà
     mỗi lần lại `classList.remove` + đọc `offsetWidth` = **ép trình duyệt tính lại
     bố cục NGAY TRONG vòng vẽ game**. Đúng cái lỗi `setLevel` đã mắc và đã phải
     chữa bằng `barCache`.
     400ms chọn để hai thứ cùng đúng: một loạt sự kiện trong cùng một giây chỉ ghi
     DOM một lần, còn ba câu trả lời đúng cách nhau vài giây thì VẪN chạy lại hoạt
     cảnh từng lần (không thì lần thứ hai trông như không có gì xảy ra). */
  var MATE_MIN_MS = 400;
  var mateAt = 0;

  function mate(state) {
    if (!mateEl) return;                  /* màn hẹp không dựng console — bỏ qua */
    var want = (state === "cheer" || state === "oops") ? state : "idle";
    var now = Date.now();

    if (want === mateSrc) {
      if (want === "idle") return;
      /* Cùng biểu cảm lần nữa: chỉ chạy lại hoạt cảnh nếu đã đủ xa lần trước —
         còn không thì chỉ gia hạn đồng hồ, KHÔNG đụng DOM. */
      if (mateTimer) { clearTimeout(mateTimer); }
      if (now - mateAt >= MATE_MIN_MS) {
        mateEl.classList.remove(want);
        void mateEl.offsetWidth;          /* ép trình duyệt nhận lại animation */
        mateEl.classList.add(want);
        mateAt = now;
      }
      mateTimer = setTimeout(function () { mate(null); }, MATE_MS);
      return;
    }

    if (mateTimer) { clearTimeout(mateTimer); mateTimer = 0; }
    var key = (location.pathname.split("/").pop() || "").replace(".html", "");
    mateImg.src = mateUrl(MATE[key], want);
    mateEl.classList.remove("cheer", "oops");
    if (want !== "idle") {
      mateEl.classList.add(want);
      mateAt = now;
      mateTimer = setTimeout(function () { mate(null); }, MATE_MS);
    }
    mateSrc = want;
  }

  /* Hai góc còn lại của vành kim loại. `.play` chỉ có `::before`/`::after` = 2 góc, mà
     BỐN góc mới đọc ra là một cái vành — bản mẫu đã chứng minh: hai góc chéo nhau đọc
     như hai vệt lỗi. Nên thêm một phần tử để có thêm hai pseudo.
     ⚠️ Phải `position:absolute` (khai ở CSS): `.play` là grid có `place-items:center`,
        một con thường sẽ chen vào ô grid và đẩy sân lệch. */
  function mountCorners() {
    var play = doc.querySelector(".play");
    if (!play || play.querySelector(".gs-cnr")) return;
    var i = doc.createElement("i");
    i.className = "gs-cnr";
    i.setAttribute("aria-hidden", "true");
    play.appendChild(i);
  }

  var bar = null;

  function mountBar() {
    var stage = doc.querySelector(".stage");
    if (!stage || bar) return;
    bar = doc.createElement("div");
    bar.className = "gs-bar";
    bar.innerHTML = '<div class="gs-track"><i></i></div><div class="gs-cap"></div>';
    stage.appendChild(bar);
  }

  /* Game gọi: setLevel({pct: 0..1, caption: "CẤP 1 · còn 18 giây nữa lên CẤP 2"})
     Gọi `setLevel(null)` để ẩn hẳn (lúc chưa chơi).
     ⚠️ Ẩn hẳn chứ không hiện 0% — một thanh rỗng nói rằng trẻ chưa làm được gì, trong
        khi thật ra lượt chơi còn chưa bắt đầu. Cùng nguyên tắc dấu `—` của `missions`. */
  /* ⚠️ NHỚ GIÁ TRỊ CŨ — BẮT BUỘC, KHÔNG PHẢI TỐI ƯU CHO ĐẸP. Cả 3 game gọi hàm này từ
     `paintHud()`, mà `paintHud` chạy MỖI KHUNG HÌNH; ghi `style.width` + `textContent`
     60 lần/giây là ép trình duyệt tính lại bố cục 60 lần/giây ngay trong vòng vẽ game.
     Đúng khuôn `hudCache` mà chính `paintHud` đang dùng cho các chip. */
  var barCache = { p: -1, c: null, on: null };

  function setLevel(o) {
    mountBar();
    if (!bar) return;
    /* ⚠️ ẨN khi có lớp phủ đang mở (brief / tạm dừng / kết quả) — tức khi CHƯA chơi.
       Một thanh 0% đứng đó nói rằng trẻ chưa làm được gì, trong khi lượt chơi còn chưa
       bắt đầu; đúng nguyên tắc dấu `—` thay cho số 0 của `missions.html`. Dùng lại
       chính tín hiệu `.ov.show` mà lời nhắc xoay ngang đã dùng, không thêm cờ mới. */
    if (o && !playing()) o = null;
    if (!o) {
      if (barCache.on !== false) { bar.classList.remove("on"); barCache.on = false; }
      return;
    }
    var pct = Math.round(Math.max(0, Math.min(1, +o.pct || 0)) * 1000) / 10;  /* 0,1% là đủ mịn */
    var cap = o.caption || "";
    if (pct !== barCache.p) { bar.querySelector("i").style.width = pct + "%"; barCache.p = pct; }
    if (cap !== barCache.c) { bar.querySelector(".gs-cap").textContent = cap; barCache.c = cap; }
    if (barCache.on !== true) { bar.classList.add("on"); barCache.on = true; }
  }

  /* ── ①b Ngân sách pixel của canvas ─────────────────────────────────────
     Sân to ra thì số pixel phải tô tăng theo BÌNH PHƯƠNG. Đo được: dodge trên Full HD
     đi từ 800×500 lên 1529×956, tức **3,65 lần diện tích**.

     ⚠️⚠️ TÔI KHÔNG ĐO ĐƯỢC FPS THẬT, và đừng tin script nào bảo là đo được: Chromium
        headless vẽ bằng SwiftShader (không GPU) nên nó bỏ khung ở CẢ hai cỡ sân —
        phép đo đầu tiên của tôi cho ra sân cũ 66,6ms mà sân mới 50,1ms, tức sân TO
        HƠN lại NHANH HƠN, chuyện bất khả thi nếu đang bị giới hạn bởi số pixel. Đó là
        dấu hiệu phép đo đang đo nhịp của headless, không đo game. Muốn số thật thì
        phải mở trên máy/tablet thật.
     ⇒ Nên thay vì ĐOÁN hiệu năng, CHẶN CỨNG nguyên nhân: giữ vùng vẽ của canvas dưới
       một trần, bằng cách hạ DPR khi sân lớn. Trần 2,4 triệu pixel chọn theo mốc có
       thật: sân cũ ở DPR 2 là 1600×1000 = 1,6 triệu, và iPad mini để ngang với sân mới
       là 1984×1240 = 2,46 triệu — tức trần này giữ mọi cấu hình trong khoảng 1–1,5 lần
       so với thứ đã chạy mượt từ 27/07/2026, chứ không phải 3,65 lần.
     ⚠️ SÀN DPR 1: hạ xuống dưới 1 là ảnh mờ hơn cả màn hình, mất nhiều hơn được.
     ⚠️ Hạ DPR KHÔNG đổi độ khó (`fit()` scale theo `cv.width/VW`), chỉ đổi độ nét. */
  var PX_CAP = 2400000;

  function dprFor(w, h) {
    var d = Math.min(2, global.devicePixelRatio || 1);
    /* Chế độ giảm cấu hình dùng chung (`astroq-perf`) thì thôi nhân đôi hẳn. */
    try { if (global.AstroQ && AstroQ.getPerf && AstroQ.getPerf()) d = 1; } catch (e) {}
    var px = Math.max(1, w * h);
    return Math.max(1, Math.min(d, Math.sqrt(PX_CAP / px)));
  }

  /* ── ①b BỘ NẠP ART DÙNG CHUNG ────────────────────────────────────────
     `loadArt(path)` → hộp `{img, ok, ar}` mà phần vẽ hỏi NGAY trong vòng vẽ;
     `drawArt(ctx, box, cx, cy, boxW, boxH)` vẽ ôm trọn trong hộp (contain) rồi
     canh giữa.

     ⚠️ `ok` chỉ bật khi ảnh đã **decode xong** — nên khung hình đầu tiên (ảnh
        chưa về) vẫn vẽ bằng code chứ không để một ô trống, và ảnh 404 thì game
        lùi về bản vẽ vector **không lỗi không cảnh báo**. Đó là lỗi IM LẶNG, nên
        đường lùi phải có phép kiểm riêng (xem `probe_rock_art.py`).
     ⚠️ ĐẶT Ở ĐÂY, KHÔNG CHÉP VÀO TỪNG GAME: từ 22/08/2026 có **ba** game cần
        (racer · dodge · defender) vì cả ba dùng chung ảnh `img/rock-gray.png`.
        Ba bản sao của cùng 12 dòng là đúng thứ quy tắc 2 mục 6 cấm — `game-racer.html`
        vốn giữ một bản riêng và đã chuyển sang dùng bản này.
     ⚠️ `drawArt` NHẬN `ctx` LÀM THAM SỐ, không bắt qua closure như bản cũ ở racer:
        đây là file dùng chung, không có canvas nào của riêng nó. */
  function loadArt(path) {
    var box = { img: null, ok: false, ar: 1 };
    if (!path) return box;
    var im = new Image();
    im.onload = function () {
      box.ar = (im.naturalWidth || 1) / (im.naturalHeight || 1);
      box.ok = true;
    };
    im.onerror = function () { box.ok = false; };
    im.src = path;
    box.img = im;
    return box;
  }

  function drawArt(ctx, box, cx, cy, boxW, boxH) {
    var h = Math.min(boxH, boxW / box.ar), w = h * box.ar;
    ctx.drawImage(box.img, cx - w / 2, cy - h / 2, w, h);
  }

  /* ── ② Nhắc xoay ngang ──────────────────────────────────────────────── */

  var TXT = {
    vi: { h: "Xoay ngang máy nhé!",
          p: "Xoay máy sang ngang thì sân chơi rộng hơn gấp đôi — nhìn rõ hơn và dễ né hơn nhiều.",
          ok: "Vẫn chơi kiểu dọc" },
    en: { h: "Turn your device sideways",
          p: "In landscape the play area is more than twice as big — easier to see and much easier to dodge.",
          ok: "Play in portrait anyway" }
  };

  /* ⚠️ `pointer: coarse` chứ không phải chỉ bề rộng: bóp hẹp cửa sổ Chrome trên
     laptop cũng ra màn hình dọc, mà ở đó lời nhắc "xoay máy" là vô nghĩa. Cùng
     lý do đã ghi cho dải `.mob-note` ở trang chủ. */
  var mqPortrait = null;
  try { mqPortrait = global.matchMedia("(orientation: portrait) and (pointer: coarse)"); }
  catch (e) { mqPortrait = null; }

  /* Bỏ qua chỉ trong PHIÊN này (sessionStorage), không phải vĩnh viễn: người dùng
     bỏ qua vì lúc đó đang bật khoá xoay, chứ không phải vì không bao giờ muốn xoay. */
  var SKIP = "astroq-rot-skip";
  function skipped() {
    try { return global.sessionStorage.getItem(SKIP) === "1"; } catch (e) { return false; }
  }

  var el = null;

  function paint() {
    if (!el) return;
    var t = TXT[(global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi"];
    el.querySelector(".rot-h").textContent  = t.h;
    el.querySelector(".rot-p").textContent  = t.p;
    el.querySelector(".rot-ok").textContent = t.ok;
  }

  function mount() {
    var play = doc.querySelector(".play");
    if (!play || el) return;
    el = doc.createElement("div");
    el.className = "ov rot";
    el.setAttribute("role", "region");
    el.innerHTML =
      '<div class="ov-card rot-card">' +
        '<div class="rot-ic" aria-hidden="true"><span>▭</span></div>' +
        '<h2 class="rot-h"></h2><p class="rot-p"></p>' +
        '<button type="button" class="rot-ok"></button>' +
      "</div>";
    el.querySelector(".rot-ok").addEventListener("click", function () {
      try { global.sessionStorage.setItem(SKIP, "1"); } catch (e) {}
      hide();
    });
    play.appendChild(el);
    paint();
  }

  function hide() { if (el) el.classList.remove("show"); }

  /* Game đang chạy thì mọi lớp phủ đều tắt — xem ghi chú đầu file. */
  function playing() {
    var ovs = doc.querySelectorAll(".ov.show");
    for (var i = 0; i < ovs.length; i++) if (ovs[i] !== el) return false;
    return true;
  }

  /* ⚠️ GAME NÀO CŨNG NHẮC "XOAY NGANG" LÀ SAI — thêm cửa TẮT 16/08/2026.
     Lời nhắc này sinh ra cho game canvas: ở đó nằm ngang cho sân rộng gấp đôi
     (đo được trên iPad mini: 699×437 dọc vs 992×620 ngang). Nhưng game **quyết
     định** thì ngược hẳn — nó là chữ để ĐỌC, và một hộp chữ thấp-mà-rộng khó đọc
     hơn hộp cao-mà-hẹp. Nhắc xoay ở đó là bảo trẻ làm cho trải nghiệm của nó tệ đi.
     ⇒ Trang tự khai `data-rotate="off"` trên `.stage`. Mặc định VẪN BẬT, nên 6
       game canvas không phải sửa một dòng nào. */
  function rotateOff() {
    var stage = doc.querySelector(".stage");
    return !!(stage && stage.getAttribute("data-rotate") === "off");
  }

  function refresh() {
    if (!mqPortrait || rotateOff()) { hide(); return; }
    if (!mqPortrait.matches || skipped()) { hide(); return; }
    if (playing()) return;          /* đừng cắt ngang một lượt đang chơi */
    mount();
    if (el) el.classList.add("show");
  }

  /* ═════ THẺ "LƯU TIẾN ĐỘ CỦA CON" Ở KHU HUẤN LUYỆN (việc 3, 05/09/2026) ═════
     Trang game **cố ý không nạp** SDK Firebase (để màn chơi mượt), nên mọi lượt
     chơi của một đứa trẻ chưa đăng nhập rơi vào `astroq-progress-queue` — đúng
     cái hàng chờ mà `js/guest-claim.js` sinh ra để cứu. Trước lượt này thẻ chỉ
     móc ở vỏ màn chơi NHIỆM VỤ, nên trẻ vào thẳng Khu Huấn Luyện chơi rồi bỏ đi
     thì **không có gì mời nó lưu**.

     ⚠️⚠️ MÓC Ở VỎ, KHÔNG CHÉP VÀO 11 GAME. `js/game-shell.js` nạp ở cả 11 trang
        game; `js/game-run.js` thì chỉ 5 game lớp quyết định dùng (6 game canvas
        cũ cố ý chưa chuyển sang), nên nó KHÔNG phủ đủ. Game thứ 12 tự có.

     ⚠️⚠️ CHẶN Ở ĐƯỜNG RỜI TRANG, KHÔNG BẬT LÚC KẾT LƯỢT — quyết định chính của
        cả lượt. Bảng kết quả mang phần thưởng (điểm, sao, kỷ lục, số tt vừa
        nhận); phủ một hộp hỏi email lên đó là **cướp mất đúng khoảnh khắc trẻ
        vừa làm được một việc**. Còn "Chơi lại" thì tuyệt đối không chặn — trẻ
        đang muốn chơi tiếp. Lúc nó bấm một đường RỜI TRANG là lúc nó đã tự
        quyết định dừng: một chỗ yên tĩnh, không cắt ngang gì.

     ⚠️⚠️ ĐỪNG VIẾT "ĐÂY LÀ KHOẢNH KHẮC CUỐI CÙNG CÒN CỨU ĐƯỢC" — bản nháp đầu
        của khối này ghi đúng câu đó và nó **SAI**: hàng chờ nằm trong
        `localStorage`, nên rời sang `games.html` hay `dashboard.html` KHÔNG làm
        mất gì. Thứ thật sự làm mất là ① trẻ đóng tab rồi không quay lại, hoặc
        ② hàng chờ vượt 40 việc — `enqueue()` khi đó **vứt việc CŨ NHẤT**. Đây là
        chỗ tốt nhất để HỎI, không phải chỗ cuối cùng để cứu.

     ⚠️ KHÔNG cứu được ca trẻ đóng thẳng tab (`beforeunload` không mở được hộp
        thoại), và ca rời trang bằng phím Escape ở game lớp quyết định
        (`location.href` thẳng trong handler bàn phím). Ghi ra để không ai tưởng
        chỗ này phủ kín. */

  /* ⚠️⚠️ CẢ 11 TRANG GAME CÓ **0 THẺ `<a href>`** — mọi đường rời trang là một
     `<button>` gọi `location.href` trong closure của trang. Đo được trước khi
     viết; bản nháp đầu bắt `a[href]` nên nó **bắt trượt hoàn toàn**, và không có
     gì báo lỗi cả. Sáu id dưới đây trùng khớp ở CẢ 11 game — `check_pages` mục
     [4b] đối chiếu hai chiều, nên game thứ 12 thêm một nút rời trang tên khác là
     nó báo ngay thay vì lặng lẽ bỏ sót. */
  var LEAVE_IDS = { "back": 1, "hub-btn": 1, "home-btn": 1,
                    "need-hub": 1, "need-quiz": 1, "pause-hub": 1 };

  function claimSteps() {
    var G = global.AstroQGuestClaim, P = global.AstroQProgress;
    if (!G || !G.due || !G.open) return 0;
    if (!P || !P.queuedGames) return 0;
    var n = P.queuedGames();
    return G.due(n) ? n : 0;
  }

  function claimOpen(n) {
    return global.AstroQGuestClaim.open({
      steps: n, kind: "game",
      lang: (global.AstroQ && AstroQ.getLang && AstroQ.getLang()) || "vi"
    })["catch"](function () {});   /* thẻ hỏng thì nuốt: nó là lời mời, không phải chốt chặn */
  }

  /* Đang phát lại cú bấm của chính mình — cho nó đi qua, không hỏi lần hai. */
  var replaying = false;

  function wireClaim() {
    doc.addEventListener("click", function (ev) {
      if (replaying) return;
      /* ⚠️ TÔN TRỌNG MỌI CÁCH MỞ CỦA TRÌNH DUYỆT — Ctrl/Cmd-click, Shift-click,
         chuột giữa. `preventDefault` bừa là lấy đi một hành vi người dùng không
         hiểu vì sao mất (bài học `js/index-gate.js`, 01/08/2026). */
      if (ev.defaultPrevented || ev.button !== 0) return;
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
      var t = ev.target;
      var b = t && t.closest ? t.closest("button[id]") : null;
      if (!b || !LEAVE_IDS[b.id]) return;
      /* ⚠️ `playing()` TRẢ TRUE KHI KHÔNG LỚP PHỦ NÀO ĐANG MỞ, tức đang giữa lượt
         chơi. Không cắt ngang ở đó — lượt đó đã trừ phí vào cửa rồi. */
      if (playing()) return;
      var n = claimSteps();
      if (!n) return;

      /* ⚠️⚠️ CHẶN Ở PHA **CAPTURE** RỒI PHÁT LẠI CÚ BẤM, thay vì tự điều hướng.
         Vỏ này KHÔNG biết nút nào đi đâu — đích nằm trong closure của từng trang.
         Ghim một bảng "id → trang đích" ở đây là dựng bản sao thứ hai của một sự
         thật đã có, và nó sẽ nói sai vào đúng ngày ai đó đổi đích ở trang. Phát
         lại thì chính trang lo việc đi đâu. */
      ev.preventDefault();
      ev.stopPropagation();
      claimOpen(n).then(function () {
        replaying = true;
        try { b.click(); } finally {
          /* Nhả cờ sau một nhịp: nếu vì lý do nào đó cú điều hướng không xảy ra
             thì trang không bị kẹt ở trạng thái "bỏ qua mọi lời hỏi". */
          global.setTimeout(function () { replaying = false; }, 1200);
        }
      });
    }, true);
  }

  /* ── Nối dây ───────────────────────────────────────────────────────── */

  function boot() {
    wireClaim();
    mountSide();
    mountCorners();
    sizeField();
    refresh();
    if (global.ResizeObserver) {
      var ro = new ResizeObserver(function () { sizeField(); });
      var play = doc.querySelector(".play");
      if (play) ro.observe(play);
    } else {
      global.addEventListener("resize", sizeField);
    }
    global.addEventListener("orientationchange", function () {
      /* Chờ một nhịp: lúc sự kiện bắn ra thì bố cục chưa xoay xong. */
      global.setTimeout(function () { sizeField(); refresh(); }, 220);
    });
    if (mqPortrait && mqPortrait.addEventListener) {
      mqPortrait.addEventListener("change", function () { sizeField(); refresh(); });
    }
    if (global.AstroQ && AstroQ.onLang) AstroQ.onLang(paint);
  }

  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", boot);
  else boot();

  global.AstroQGameShell = { sizeField: sizeField, refreshRotate: refresh,
                             dpr: dprFor, setLevel: setLevel, mate: mate,
                             loadArt: loadArt, drawArt: drawArt };
})(window);
