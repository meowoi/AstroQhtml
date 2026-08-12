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

  /* Ai là bạn đồng hành của game nào — khai MỘT chỗ.
     ⚠️ Ảnh lấy từ `ava/` đã có; KHÔNG có biểu cảm thay thế, nên console này chỉ có
        nhịp trôi. Muốn Byte/Comet phản ứng theo việc trẻ làm thì cần ẢNH GỐC. */
  var MATE = { "game-dodge": ["ava/avab.png", "BYTE"],
               "game-defender": ["ava/avab.png", "BYTE"],
               "game-constellation": ["ava/avam.png", "COMET"] };

  function mountSide() {
    var stage = doc.querySelector(".stage");
    if (!stage || doc.querySelector(".gs-side")) return;
    var key = (location.pathname.split("/").pop() || "").replace(".html", "");
    var m = MATE[key];
    if (!m) return;                       /* game mới chưa khai thì thôi, không vỡ */
    var side = doc.createElement("aside");
    side.className = "gs-side";
    side.setAttribute("aria-hidden", "true");   /* trang trí — trình đọc màn hình bỏ qua */
    side.innerHTML = '<div class="gs-mate"><img src="' + m[0] + '" alt="">' +
                     '<span class="nm">' + m[1] + "</span></div>";
    stage.appendChild(side);
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

  function refresh() {
    if (!mqPortrait) return;
    if (!mqPortrait.matches || skipped()) { hide(); return; }
    if (playing()) return;          /* đừng cắt ngang một lượt đang chơi */
    mount();
    if (el) el.classList.add("show");
  }

  /* ── Nối dây ───────────────────────────────────────────────────────── */

  function boot() {
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
                             dpr: dprFor, setLevel: setLevel };
})(window);
