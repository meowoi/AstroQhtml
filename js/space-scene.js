/* ============================================================
   space-scene.js — BỘ VẼ CẢNH KHÔNG GIAN dùng chung: sao, Trái Đất, phi thuyền Luna.

   Trước 29/07/2026 toàn bộ phần này nằm trong js/warp-screen.js. Tách ra vì màn
   mở đầu Nhiệm Vụ 01 (js/mission-intro.js) cũng cần đúng Trái Đất và đúng con tàu
   đó — vẽ lần thứ hai là chắc chắn có ngày hai cảnh trông khác nhau, mà người chơi
   đi từ cảnh này sang cảnh kia chỉ trong vài giây.

   Ở đây CHỈ có phần VẼ. **Nhịp phim (cái gì xảy ra ở giây thứ mấy) thuộc về từng
   màn**, không để chung: warp-screen là "tăng tốc rồi dừng", mission-intro là "vòng
   vào quỹ đạo" — nhồi cả hai vào một file thì mỗi lần sửa một màn lại sợ hỏng màn kia.

     <script src="js/space-scene.js"></script>

     var sc = AstroQSpace.create(canvasEl, { stars:200, stillStars:110 });
     sc.resize();                       // gọi lại mỗi khi cửa sổ đổi cỡ
     sc.clear();
     sc.stars(t, dt, speed, {x,y});     // vệt sao toả ra từ điểm tụ
     sc.earth(t, cx, cy, R);
     sc.ship({ x, y, w, h, rot, thrust });
     sc.shipRatio                        // tỉ lệ ảnh Luna (rộng/cao) để tính w từ h

   KHÔNG dùng `shadowBlur` ở bất cứ đâu — blur trên canvas mỗi khung hình đắt gấp
   nhiều lần; hào quang làm bằng gradient toả và lớp chồng `"lighter"`, giống cách
   làm ở game-dodge / game-constellation.
   ============================================================ */
(function (global) {
  "use strict";

  var SHIP_SRC = "img/luna-side.png";   // Luna nằm ngang, mũi chỉ SANG PHẢI

  /* Hình dáng lục địa. Toạ độ/bán kính theo bán kính Trái Đất (đơn vị -1..1),
     `k` = bán kính lệch ở từng đỉnh. Mảng CỐ ĐỊNH (không random) nên hành tinh
     trông y như nhau ở mọi lượt chạy — mỗi lần một hình khác thì trông như lỗi.

     rx/ry khác nhau để lục địa DÀI theo một chiều: Á-Âu là dải ngang, châu Phi
     và châu Mỹ là dải dọc. Cùng một bán kính cho cả hai chiều thì ra mấy khối
     tròn đều nhau, nhìn như hoa văn quả bóng chứ không phải đất liền. */
  var LAND = [
    { x: -0.22, y: -0.46, rx: 0.66, ry: 0.26,                       // Á – Âu
      k: [1, .82, 1.12, .74, 1.05, .86, 1.18, .78, .94, 1.08, .8, 1.14] },
    { x: -0.06, y:  0.26, rx: 0.27, ry: 0.44,                       // châu Phi
      k: [.92, 1.14, .78, 1.06, .84, 1.2, .72, .98, 1.1, .8, 1.02, .88] },
    { x:  0.66, y:  0.02, rx: 0.24, ry: 0.56,                       // châu Mỹ ở rìa
      k: [1.08, .78, 1, 1.16, .74, 1.04, .86, 1.12, .8, .96, 1.06, .82] },
    { x:  0.34, y:  0.62, rx: 0.22, ry: 0.14,                       // châu Úc
      k: [.96, 1.12, .78, 1.04, .86, 1.16, .74, 1, .9, 1.1, .8, 1.02] },
    { x: -0.72, y:  0.34, rx: 0.16, ry: 0.12,                       // đảo nhỏ
      k: [1, .86, 1.1, .8, 1.04, .9, 1.14, .82, .96, 1.06, .84, 1.08] }
  ];
  /* Mây: vẽ bằng gradient toả (mờ dần ra rìa) chứ không phải khối đặc — khối đặc
     thì thành mấy miếng trắng cạnh rõ, đúng là hoa văn quả bóng. */
  var CLOUD = [
    { x: -0.52, y: -0.30, r: 0.30, a: 0.30 }, { x: 0.06, y: -0.66, r: 0.26, a: 0.26 },
    { x:  0.54, y:  0.34, r: 0.28, a: 0.28 }, { x: -0.34, y: 0.62, r: 0.24, a: 0.24 },
    { x: -0.86, y: -0.04, r: 0.22, a: 0.22 }, { x: 0.88, y: -0.36, r: 0.22, a: 0.24 },
    { x:  0.22, y: -0.06, r: 0.20, a: 0.20 }
  ];

  /* Ảnh Luna tải MỘT LẦN cho cả trang: hai màn (warp + mission-intro) dùng chung
     một đối tượng Image nên chuyển màn không phải tải lại và không nhấp nháy. */
  var shipImg = null, shipOk = false, shipRatio = 1.88;
  function loadShip() {
    if (shipImg) return;
    shipImg = new global.Image();
    shipImg.onload = function () {
      shipOk = true;
      if (shipImg.naturalHeight) shipRatio = shipImg.naturalWidth / shipImg.naturalHeight;
    };
    shipImg.onerror = function () { shipOk = false; };   // lùi về bản vẽ vector
    shipImg.src = SHIP_SRC;
  }

  function isReduced() {
    try { return global.matchMedia("(prefers-reduced-motion: reduce)").matches; }
    catch (e) { return false; }
  }

  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }

  /**
   * Tạo một cảnh gắn với một <canvas>.
   * @param {HTMLCanvasElement} canvas
   * @param {{stars?:number, stillStars?:number, warpSpeed?:number}} [opt]
   */
  function create(canvas, opt) {
    opt = opt || {};
    var nStars = opt.stars != null ? opt.stars : 200;
    var nStill = opt.stillStars != null ? opt.stillStars : 110;
    var warpSpeed = opt.warpSpeed != null ? opt.warpSpeed : 13;

    var ctx = canvas.getContext("2d");
    var W = 0, H = 0, dpr = 1;
    var moving = [], still = [];
    var reduced = isReduced();

    loadShip();

    function resize() {
      dpr = Math.min(global.devicePixelRatio || 1, 2);   // >2 chỉ tốn pixel, mắt không thấy khác
      W = global.innerWidth; H = global.innerHeight;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      reduced = isReduced();
      seed();
      scene.W = W; scene.H = H; scene.dpr = dpr; scene.reduced = reduced;
    }

    function seed() {
      moving = [];
      var maxR = Math.hypot(W, H);
      for (var i = 0; i < nStars; i++) {
        moving.push({
          a: Math.random() * Math.PI * 2,
          r: Math.random() * maxR,
          s: 0.45 + Math.random() * 0.9,          // sao gần thì chạy nhanh hơn
          c: Math.random() < 0.14                  // 14% sao ngả tím cho khớp tông
        });
      }
      /* Lớp sao nền ĐỨNG YÊN, rải đều khắp khung.
         Vì sao cần: sao chạy luôn sinh lại SÁT điểm tụ rồi toả ra, nên lúc tàu
         dừng hẳn thì gần như cả đám đang tụ quanh Trái Đất — nửa bên kia trời
         trống trơn (đo được chỉ 26 px sáng). Lớp nền này giữ cho bầu trời lúc
         nào cũng có sao, và vì không di chuyển nên không phá cảm giác warp. */
      still = [];
      for (var j = 0; j < nStill; j++) {
        still.push({
          x: Math.random() * W, y: Math.random() * H,
          r: 0.4 + Math.random() * 0.9,
          al: 0.18 + Math.random() * 0.34,
          c: Math.random() < 0.12
        });
      }
    }

    function clear(color) {
      ctx.fillStyle = color || "#03050f";
      ctx.fillRect(0, 0, W, H);
    }

    /**
     * Sao. `sp` = 0 (đứng, nhấp nháy) … 1 (vệt warp dài). `focus` = điểm tụ,
     * mặc định là tâm khung.
     */
    function stars(t, dt, sp, focus) {
      var p = focus || { x: W / 2, y: H / 2 };
      var maxR = Math.hypot(W, H) * 0.75;

      // Lớp nền đứng yên vẽ TRƯỚC để vệt sao chạy nằm trên
      for (var k = 0; k < still.length; k++) {
        var q = still[k];
        var tw2 = reduced ? 1 : 0.7 + 0.3 * Math.sin(t * 1.6 + k * 0.7);
        ctx.fillStyle = q.c ? "rgba(192,132,252," + (q.al * tw2).toFixed(3) + ")"
                            : "rgba(226,240,255," + (q.al * tw2).toFixed(3) + ")";
        ctx.beginPath(); ctx.arc(q.x, q.y, q.r, 0, Math.PI * 2); ctx.fill();
      }

      ctx.lineCap = "round";
      for (var i = 0; i < moving.length; i++) {
        var s = moving[i];
        // Càng xa điểm tụ càng chạy nhanh — đó là phối cảnh, không phải hiệu ứng thêm.
        var v = sp * warpSpeed * s.s * (0.35 + s.r / maxR * 1.5) * (dt * 60);
        var r0 = s.r;
        s.r += v;
        if (s.r > maxR) { s.r = Math.random() * 30 + 4; s.a = Math.random() * Math.PI * 2; r0 = s.r; }

        var cos = Math.cos(s.a), sin = Math.sin(s.a);
        var x1 = p.x + cos * r0, y1 = p.y + sin * r0;
        var x2 = p.x + cos * s.r, y2 = p.y + sin * s.r;
        var near = clamp01(s.r / maxR);
        var al = 0.22 + near * 0.72;

        if (v > 1.4) {                                     // đang lao nhanh → vệt dài
          ctx.strokeStyle = s.c ? "rgba(192,132,252," + al.toFixed(3) + ")"
                                : "rgba(226,240,255," + al.toFixed(3) + ")";
          ctx.lineWidth = 0.6 + near * 1.5;
          ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
        } else {                                           // đã dừng → sao đứng, nhấp nháy nhẹ
          var tw = reduced ? 1 : 0.72 + 0.28 * Math.sin(t * 2.2 + i);
          ctx.fillStyle = s.c ? "rgba(192,132,252," + (al * tw).toFixed(3) + ")"
                              : "rgba(226,240,255," + (al * tw).toFixed(3) + ")";
          var rr = 0.5 + near * 1.1;
          ctx.beginPath(); ctx.arc(x2, y2, rr, 0, Math.PI * 2); ctx.fill();
        }
      }
    }

    /**
     * Mảng bờ cong MỀM: 12 đỉnh trên một hình ellipse với bán kính lệch theo `k`,
     * nối bằng đường cong bậc hai đi qua TRUNG ĐIỂM hai đỉnh liền nhau.
     *
     * Vì sao không nối thẳng bằng lineTo: 12 đoạn thẳng ra một khối đa giác cạnh
     * rõ — nhìn đúng như hoa văn khâu trên quả bóng, không ra bờ biển. Cho đỉnh
     * làm điểm điều khiển và trung điểm làm điểm neo thì được đường kín trơn.
     */
    function blob(cx, cy, rx, ry, k, rot) {
      var n = k.length, px = [], py = [], i, a, kk;
      for (i = 0; i < n; i++) {
        a = i / n * Math.PI * 2 + (rot || 0);
        kk = k[i];
        px.push(cx + Math.cos(a) * rx * kk);
        py.push(cy + Math.sin(a) * ry * kk);
      }
      ctx.beginPath();
      ctx.moveTo((px[n - 1] + px[0]) / 2, (py[n - 1] + py[0]) / 2);
      for (i = 0; i < n; i++) {
        var j = (i + 1) % n;
        ctx.quadraticCurveTo(px[i], py[i], (px[i] + px[j]) / 2, (py[i] + py[j]) / 2);
      }
      ctx.closePath();
    }

    /** Đốm mờ dần ra rìa — dùng cho mây và mũ băng. */
    function softBlob(cx, cy, r, alpha) {
      var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0, "rgba(255,255,255," + alpha.toFixed(3) + ")");
      g.addColorStop(0.55, "rgba(255,255,255," + (alpha * 0.62).toFixed(3) + ")");
      g.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
    }

    /**
     * Trái Đất vẽ bằng code (kho `img/` chưa có ảnh Trái Đất, và hình cầu gradient
     * + vài mảng lục địa nhẹ hơn mọi tấm PNG).
     * @param t giây kể từ đầu màn — chỉ dùng để cho mây trôi
     */
    function earth(t, cx, cy, R) {
      if (R < 0.6) return;

      // Khí quyển: vành sáng lam nhạt ra ngoài mép cầu
      var atm = ctx.createRadialGradient(cx, cy, R * 0.9, cx, cy, R * 1.5);
      atm.addColorStop(0, "rgba(95,190,255,.34)");
      atm.addColorStop(0.45, "rgba(70,150,255,.12)");
      atm.addColorStop(1, "rgba(70,150,255,0)");
      ctx.fillStyle = atm;
      ctx.beginPath(); ctx.arc(cx, cy, R * 1.5, 0, Math.PI * 2); ctx.fill();

      // Đại dương: nguồn sáng ở trên-trái (cùng phía với vành sáng khí quyển)
      var sea = ctx.createRadialGradient(cx - R * 0.36, cy - R * 0.40, R * 0.06, cx, cy, R * 1.06);
      sea.addColorStop(0, "#8fe0ff");
      sea.addColorStop(0.30, "#3d9ce0");
      sea.addColorStop(0.66, "#1a5fa8");
      sea.addColorStop(1, "#0f2f56");
      ctx.fillStyle = sea;
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();

      ctx.save();
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.clip();

      // Lục địa: nền xanh lá + một mảng nhạt bên trong cho khỏi phẳng
      for (var i = 0; i < LAND.length; i++) {
        var L = LAND[i];
        var lx = cx + L.x * R, ly = cy + L.y * R;
        ctx.fillStyle = i % 2 ? "#3d9159" : "#469c62";
        blob(lx, ly, L.rx * R, L.ry * R, L.k, 0); ctx.fill();
        ctx.fillStyle = "rgba(150,196,120,.34)";          // đồng bằng / sa mạc bên trong
        blob(lx - L.rx * R * 0.10, ly - L.ry * R * 0.12,
             L.rx * R * 0.52, L.ry * R * 0.52, L.k, 1.1); ctx.fill();
      }

      // Mũ băng hai cực — đốm mờ dẹt, không phải khối trắng cạnh rõ
      ctx.save();
      ctx.translate(cx, cy - R * 0.92); ctx.scale(1, 0.42);
      softBlob(0, 0, R * 0.62, 0.80); ctx.restore();
      ctx.save();
      ctx.translate(cx, cy + R * 0.94); ctx.scale(1, 0.42);
      softBlob(0, 0, R * 0.55, 0.72); ctx.restore();

      // Mây: TRÔI NGANG rồi lặp lại → ảo giác hành tinh đang quay, mà không phải
      // dựng phép chiếu 3D. Vẽ 2 lượt lệch nhau 2R để không hở chỗ lúc lặp.
      var drift = reduced ? 0 : (t * 0.055 % 2);
      for (var pass = 0; pass < 2; pass++) {
        var off = (drift + pass * 2) * R - R;
        for (var c = 0; c < CLOUD.length; c++) {
          var C = CLOUD[c];
          softBlob(cx + C.x * R + off, cy + C.y * R, C.r * R, C.a);
        }
      }

      // Vùng tối phía đối diện nguồn sáng (dưới-phải)
      var term = ctx.createRadialGradient(cx - R * 0.30, cy - R * 0.34, R * 0.30, cx, cy, R * 1.16);
      term.addColorStop(0, "rgba(0,0,0,0)");
      term.addColorStop(0.62, "rgba(2,6,20,.16)");
      term.addColorStop(1, "rgba(2,6,20,.78)");
      ctx.fillStyle = term;
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();

      /* Vành khí quyển sáng bám MÉP TRONG của hình cầu. Vẽ bằng gradient toả bên
         trong vùng clip, không phải nét stroke: một cung nét dày trông như cái
         vòng rời nằm lơ lửng cạnh hành tinh (đã thấy trên ảnh chụp lần đầu). */
      var rim = ctx.createRadialGradient(cx, cy, R * 0.86, cx, cy, R);
      rim.addColorStop(0, "rgba(150,215,255,0)");
      rim.addColorStop(0.72, "rgba(150,215,255,.13)");
      rim.addColorStop(1, "rgba(190,235,255,.42)");
      ctx.fillStyle = rim;
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }

    /** Luồng lửa tím ở ống đẩy + vệt sáng kéo dài về sau. */
    function thrust(s) {
      if (s.thrust <= 0.02) return;
      var back = s.x - s.w * 0.46, y = s.y;
      /* Vệt vừa phải và thót nhanh. Bản đầu để dài 3,1× thân + alpha 0,72 → trên
         ảnh chụp nó thành một MẢNG tím đặc kéo hết ra ngoài khung, nhìn như lỗi
         vẽ chứ không như luồng khí đang tan (đúng bài học ở ARCADE-01). */
      var len = s.w * (0.35 + s.thrust * 1.7);
      ctx.save();
      ctx.globalCompositeOperation = "lighter";
      var g = ctx.createLinearGradient(back, y, back - len, y);
      g.addColorStop(0, "rgba(214,180,255," + (0.50 * s.thrust).toFixed(3) + ")");
      g.addColorStop(0.30, "rgba(168,85,247," + (0.24 * s.thrust).toFixed(3) + ")");
      g.addColorStop(1, "rgba(143,123,255,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.moveTo(back, y - s.h * 0.18);
      ctx.lineTo(back - len, y - s.h * 0.03);
      ctx.lineTo(back - len, y + s.h * 0.03);
      ctx.lineTo(back, y + s.h * 0.18);
      ctx.closePath(); ctx.fill();
      // Lõi sáng trắng-tím ngay miệng ống
      var g2 = ctx.createLinearGradient(back, y, back - s.w * 0.34, y);
      g2.addColorStop(0, "rgba(255,255,255," + (0.70 * s.thrust).toFixed(3) + ")");
      g2.addColorStop(1, "rgba(192,132,252,0)");
      ctx.fillStyle = g2;
      ctx.beginPath();
      ctx.moveTo(back, y - s.h * 0.085);
      ctx.lineTo(back - s.w * 0.34, y);
      ctx.lineTo(back, y + s.h * 0.085);
      ctx.closePath(); ctx.fill();
      ctx.restore();
    }

    /** @param s {x,y,w,h,rot,thrust} — mũi tàu chỉ sang phải khi rot = 0. */
    function ship(s) {
      thrust(s);
      ctx.save();
      ctx.translate(s.x, s.y);
      ctx.rotate(s.rot || 0);
      if (shipOk) {
        ctx.drawImage(shipImg, -s.w / 2, -s.h / 2, s.w, s.h);
      } else {
        // Đường lùi khi ảnh lỗi: thân thoi + buồng kính, mũi vẫn chỉ sang phải
        ctx.fillStyle = "#dbe7ff";
        ctx.beginPath();
        ctx.moveTo(s.w * 0.5, 0);
        ctx.lineTo(-s.w * 0.30, -s.h * 0.40);
        ctx.lineTo(-s.w * 0.46, 0);
        ctx.lineTo(-s.w * 0.30, s.h * 0.40);
        ctx.closePath(); ctx.fill();
        ctx.fillStyle = "#5fd3ff";
        ctx.beginPath(); ctx.arc(s.w * 0.16, 0, s.h * 0.19, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();
    }

    var scene = {
      ctx: ctx,
      W: 0, H: 0, dpr: 1, reduced: reduced,
      resize: resize, clear: clear,
      stars: stars, earth: earth, ship: ship,
      blob: blob, softBlob: softBlob,
      /** Tỉ lệ rộng/cao của ảnh Luna — dùng để tính w từ h. */
      get shipRatio() { return shipRatio; },
      /** Ảnh Luna đã tải được chưa (test dùng để biết đang vẽ sprite hay vector). */
      get shipLoaded() { return shipOk; }
    };
    return scene;
  }

  global.AstroQSpace = {
    create: create,
    isReduced: isReduced,
    clamp01: clamp01,
    easeOut: function (x) { return 1 - Math.pow(1 - x, 3); },
    easeInOut: function (x) { return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; },
    SHIP_SRC: SHIP_SRC
  };
})(window);
