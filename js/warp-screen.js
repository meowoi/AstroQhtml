/* ============================================================
   warp-screen.js — màn loading: phi thuyền Luna tăng tốc vào không gian
   rồi GIẢM TỐC và dừng lại ở Trái Đất.

   ⚠️ VIỆC HIỆN TẠI (đổi 01/08/2026, docs/decisions/003): **chuyển cảnh dashboard →
   Bản Đồ Thiên Hà** — bấm "Mở bản đồ" ở thẻ MOD-03. Trước đó nó chạy ngay sau khi
   Comet dẫn tham quan xong, lúc trẻ bấm "Khởi động động cơ"; tour đã dời xuống sau
   nhiệm vụ 1 nên `onFinish` không còn dẫn tới đây. Xem khối "CHUYỂN CẢNH" ở cuối
   script của `dashboard.html`.

     <link rel="stylesheet" href="css/warp-screen.css" />
     <script src="js/warp-screen.js"></script>

     AstroQWarp.play({ lang:"vi", onDone:function(){ … } });

   ⚠️ PHẦN VẼ (sao, Trái Đất, tàu Luna) nằm ở **js/space-scene.js** — nạp TRƯỚC
   file này. Tách ra từ 29/07/2026 vì màn mở đầu Nhiệm Vụ 01 (`js/mission-intro.js`,
   **đã xoá 01/08/2026**) dùng đúng Trái Đất và đúng con tàu đó; vẽ lần thứ hai là
   chắc chắn có ngày hai cảnh trông khác nhau, mà người chơi đi từ cảnh này sang cảnh
   kia chỉ trong vài giây. File này chỉ còn **NHỊP PHIM**: giây thứ mấy thì tàu ở đâu,
   sao chạy nhanh bao nhiêu, chữ nào hiện.

   ĐIỂM ĐÁNG BIẾT: vệt sao toả ra TỪ CHÍNH TÂM TRÁI ĐẤT (điểm tụ), không phải trôi
   ngang — Luna đang lao về phía Trái Đất, nên phối cảnh đúng là mọi ngôi sao chạy
   ra xa khỏi cái đích đó. Nhờ vậy chỉ cần hạ một biến `speed` về 0 là ra cảm giác
   giảm tốc, không phải điều khiển từng ngôi sao.
   ============================================================ */
(function (global) {
  "use strict";

  var CONFIG = {
    /* Ảnh tàu + cách vẽ sao/Trái Đất: js/space-scene.js */
    stars: 200,                  // sao chạy (tạo vệt warp)
    stillStars: 110,             // sao nền đứng yên — xem space-scene.js để biết vì sao cần

    /* Mốc thời gian (giây) — sửa ở đây là đổi được cả nhịp phim. */
    tCruise:  0.9,   // Luna vào tới vị trí bay hành trình
    tEarth:   1.15,  // Trái Đất bắt đầu hiện ra từ một điểm sáng
    tDecel:   2.5,   // bắt đầu giảm tốc
    tStop:    3.75,  // dừng hẳn, Luna đã đậu cạnh Trái Đất
    tEnd:     4.6,   // hết phim
    fadeOut:  0.45,

    warpSpeed: 13     // px/khung ở đoạn tăng tốc, tại bán kính tham chiếu
  };

  var TXT = {
    vi: {
      lead1: "Đang khởi động động cơ…", sub1: "Luna đang tăng tốc vào không gian",
      lead2: "Đã vào quỹ đạo Trái Đất", sub2: "Chuyến phiêu lưu của bạn bắt đầu từ đây",
      skip: "Bỏ qua ›"
    },
    en: {
      lead1: "Firing up the engines…", sub1: "Luna is accelerating into space",
      lead2: "Earth orbit reached",    sub2: "Your adventure begins right here",
      skip: "Skip ›"
    }
  };

  /* ------------------------------------------------------------ */
  var root = null, cv = null, els = null, scene = null;
  var raf = 0, t0 = 0, running = false, ended = false;
  var lang = "vi", onDone = null, reduced = false, tEnd = 0;
  var W = 0, H = 0;

  /* Lời phủ do phía gọi truyền vào cho MỘT lượt chạy (`play({texts:…})`).
     ⚠️ Vì sao cần: cùng một màn phim nhưng ĐÍCH ĐẾN khác nhau thì câu chữ khác nhau.
        Bộ mặc định ("Đã vào quỹ đạo Trái Đất · Chuyến phiêu lưu của bạn bắt đầu từ
        đây") là lời của lượt ĐẦU TIÊN đi tới Trái Đất; đem nguyên nó ra dùng cho cú
        chuyển cảnh sang Bản Đồ Thiên Hà là nói sai đích và nói sai lần thứ mấy.
     ⚠️ Phủ THEO TỪNG KHOÁ, không thay cả bảng: phía gọi chỉ muốn đổi `lead2/sub2`
        thì `skip` vẫn phải có, không thì nút "Bỏ qua ›" hiện ra rỗng. */
  var over = null;

  function txt(k) {
    if (over) {
      var o = over[lang] || over.vi;
      if (o && o[k] != null) return o[k];
    }
    return (TXT[lang] || TXT.vi)[k];
  }

  function build() {
    if (root) return;
    root = document.createElement("div");
    root.className = "warp";
    root.id = "warp";
    root.setAttribute("aria-hidden", "true");
    root.innerHTML =
      '<canvas></canvas>' +
      '<button type="button" class="warp-skip"></button>' +
      '<div class="warp-cap" role="status" aria-live="polite">' +
        '<span class="lead"></span><span class="sub"></span>' +
        '<span class="warp-bar"><i></i></span>' +
      '</div>';
    document.body.appendChild(root);

    cv = root.querySelector("canvas");
    scene = AstroQSpace.create(cv, { stars: CONFIG.stars, stillStars: CONFIG.stillStars,
                                     warpSpeed: CONFIG.warpSpeed });
    els = {
      lead: root.querySelector(".warp-cap .lead"),
      sub:  root.querySelector(".warp-cap .sub"),
      bar:  root.querySelector(".warp-bar i"),
      skip: root.querySelector(".warp-skip")
    };
    els.skip.addEventListener("click", function () { stop(); });

    global.addEventListener("resize", resize);
  }

  function resize() {
    if (!scene) return;
    scene.resize();
    W = scene.W; H = scene.H;
  }

  /* Điểm tụ = tâm Trái Đất. Màn dọc/điện thoại thì đưa lên cao hơn một chút
     để dòng chữ ở đáy không đè lên hành tinh. */
  function vp() {
    var portrait = H > W;
    return { x: W * (portrait ? 0.58 : 0.70), y: H * (portrait ? 0.40 : 0.48) };
  }
  function earthR() { return Math.min(W, H) * (H > W ? 0.30 : 0.26); }

  /* ---------------- Nhịp phim ---------------- */
  var easeOut = AstroQSpace.easeOut, easeInOut = AstroQSpace.easeInOut,
      clamp01 = AstroQSpace.clamp01;

  /** Hệ số tốc độ warp theo thời gian: 0 → 1 → 0. */
  function speedAt(t) {
    if (reduced) return 0;
    if (t < CONFIG.tCruise) return easeOut(clamp01(t / CONFIG.tCruise));
    if (t < CONFIG.tDecel) return 1;
    return 1 - easeInOut(clamp01((t - CONFIG.tDecel) / (CONFIG.tStop - CONFIG.tDecel)));
  }

  /** Bán kính Trái Đất đang hiện: từ một điểm sáng nở dần tới cỡ thật. */
  function earthAt(t) {
    if (reduced) return earthR();
    var k = clamp01((t - CONFIG.tEarth) / (CONFIG.tStop - CONFIG.tEarth));
    return earthR() * easeInOut(k);
  }

  /** Vị trí + độ nghiêng của Luna. */
  function shipAt(t) {
    var p = vp(), R = earthR();
    var h = Math.max(26, Math.min(W, H) * 0.075);       // chiều cao vẽ
    var w = h * scene.shipRatio;
    var cruiseX = W * 0.26, cruiseY = H * (H > W ? 0.62 : 0.56);
    var parkX = p.x - R - w * 0.85, parkY = p.y + R * 0.42;

    if (reduced) return { x: parkX, y: parkY, w: w, h: h, rot: 0, thrust: 0.15 };

    if (t < CONFIG.tCruise) {                            // bay vào từ ngoài khung
      var k = easeOut(clamp01(t / CONFIG.tCruise));
      return { x: -w + (cruiseX + w) * k, y: cruiseY, w: w, h: h, rot: 0, thrust: 1 };
    }
    if (t < CONFIG.tDecel) {
      // Đoạn hành trình: nhấp nhô rất nhẹ cho có sức sống, không phải bay lượn
      var wob = Math.sin((t - CONFIG.tCruise) * 2.4) * h * 0.09;
      return { x: cruiseX, y: cruiseY + wob, w: w, h: h, rot: wob / (h * 6), thrust: 1 };
    }
    // Ghé vào đậu cạnh Trái Đất
    var q = easeInOut(clamp01((t - CONFIG.tDecel) / (CONFIG.tStop - CONFIG.tDecel)));
    return {
      x: cruiseX + (parkX - cruiseX) * q,
      y: cruiseY + (parkY - cruiseY) * q,
      w: w, h: h,
      rot: -0.10 * Math.sin(q * Math.PI),                // chếch mũi lên khi vòng vào
      thrust: 1 - q * 0.82
    };
  }

  /* ---------------- Vòng lặp ---------------- */
  var lastT = 0;
  function frame(now) {
    if (!running) return;
    if (!t0) { t0 = now; lastT = now; }
    var t = (now - t0) / 1000;
    var dt = Math.min((now - lastT) / 1000, 0.05);   // tab bị treo lâu thì đừng nhảy cả đoạn
    lastT = now;

    scene.clear();
    var sp = speedAt(t);
    var p = vp();
    scene.stars(t, dt, sp, p);
    scene.earth(t, p.x, p.y, earthAt(t));
    scene.ship(shipAt(t));

    paintCaption(t);
    if (t >= tEnd) { stop(); return; }
    raf = global.requestAnimationFrame(frame);
  }

  /* Tách riêng để `play()` gọi được NGAY, không đợi khung hình đầu tiên:
     lúc màn loading vừa hiện mà dòng chữ còn rỗng thì nhìn như trang bị lỗi
     (và trình đọc màn hình đọc vào chỗ trống). Cũng dùng để dịch lại khi
     đổi ngôn ngữ giữa lúc đang chạy. */
  function paintCaption(t) {
    if (!els) return;
    var arrived = t >= CONFIG.tStop - 0.05;
    els.lead.textContent = arrived ? txt("lead2") : txt("lead1");
    els.sub.textContent  = arrived ? txt("sub2") : txt("sub1");
    els.bar.style.width = Math.round(clamp01(t / CONFIG.tStop) * 100) + "%";
  }

  function stop() {
    if (!running) return;
    running = false;
    if (raf) { global.cancelAnimationFrame(raf); raf = 0; }
    root.classList.remove("show");
    root.setAttribute("aria-hidden", "true");
    if (ended) return;
    ended = true;
    var cb = onDone; onDone = null;
    // Đợi tan hết mới gọi tiếp, để trang phía dưới không "nhảy" ra giữa lúc còn mờ
    setTimeout(function () { if (cb) cb(); }, CONFIG.fadeOut * 1000);
  }

  var AstroQWarp = {
    CONFIG: CONFIG,

    /**
     * Chạy màn loading.
     * opts: { lang, onDone, texts }
     *   texts — tuỳ chọn, phủ lời cho lượt này: `{ vi:{lead1,sub1,lead2,sub2}, en:{…} }`.
     *           Khoá nào không khai thì lấy bộ mặc định. Xem ghi chú ở `over`.
     */
    play: function (opts) {
      opts = opts || {};
      lang = opts.lang === "en" ? "en" : "vi";
      onDone = typeof opts.onDone === "function" ? opts.onDone : null;
      // Đặt lại MỖI lượt: không đặt lại thì lời phủ của lượt trước dính sang lượt sau.
      over = (opts.texts && typeof opts.texts === "object") ? opts.texts : null;
      reduced = AstroQSpace.isReduced();
      build();
      resize();
      els.skip.textContent = txt("skip");
      paintCaption(0);                  // có chữ ngay, không chờ khung hình đầu
      root.classList.add("show");
      root.setAttribute("aria-hidden", "false");

      // Bớt chuyển động: không có đoạn tăng tốc, chỉ hiện cảnh đã tới rồi đi tiếp.
      // Ghi vào biến riêng, KHÔNG sửa CONFIG — sửa vào đó là lượt chạy sau
      // (cùng một trang) cũng bị cắt ngắn theo, dù lúc ấy không còn reduced.
      tEnd = reduced ? 1.5 : CONFIG.tEnd;

      t0 = 0; lastT = 0; ended = false; running = true;
      raf = global.requestAnimationFrame(frame);
    },

    /** Đổi ngôn ngữ giữa lúc đang chạy. */
    setLang: function (l) {
      lang = l === "en" ? "en" : "vi";
      if (els) {
        els.skip.textContent = txt("skip");
        // Đã dừng ở Trái Đất thì khung hình không vẽ nữa → phải tự dịch lại chữ
        if (!running) paintCaption(CONFIG.tStop);
      }
    },

    /** Bỏ qua ngay (giống bấm nút "Bỏ qua"). */
    stop: stop,

    isPlaying: function () { return running; }
  };

  global.AstroQWarp = AstroQWarp;
})(window);
