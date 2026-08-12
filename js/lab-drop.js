/* ══════════════════════════════════════════════════════════════════════════
   AstroQLabDrop — cảnh 2D dùng chung cho BA thẻ đầu của Phòng Nghiên Cứu.
   Dùng bởi lab.html. Nạp SAU js/lab-catalog.js.

   ⚠️⚠️ HỆ TOẠ ĐỘ ẢO CỐ ĐỊNH 800×500 rồi `setTransform` ra cỡ phần tử — đúng lối
      cả 3 mini-game đã dùng. Nhờ vậy cảnh trông y hệt trên mọi cỡ màn, và phóng
      to canvas KHÔNG đổi một con số nào của cảnh.

   ⚠️⚠️ KHÔNG DÙNG `shadowBlur` ở bất cứ đâu — blur mỗi khung hình rất đắt; hào
      quang làm bằng gradient + lớp chồng "lighter", đúng luật đã ghi cho
      ARCADE-01/04 và js/warp-screen.js.

   ⚠️⚠️ THỜI GIAN RƠI: CHỈ TỈ LỆ CÓ NGUỒN, KHÔNG CON SỐ TUYỆT ĐỐI NÀO HIỆN RA.
      Rơi tự do cho `t = √(2h/g)`, nên với cùng độ cao thì `t ∝ 1/√g`. Mặt Trăng
      có `g` bằng 1/6 Trái Đất (nguồn: NASA Moon Facts, nguyên văn "one-sixth")
      ⇒ cú rơi trên Mặt Trăng lâu hơn **√6 ≈ 2,45 lần**. Đó là con số DUY NHẤT
      quyết định nhịp cảnh, và nó suy từ chính nguồn.
      `BASE_MS` là bề dày thời gian chọn cho DỄ NHÌN, và nó KHÔNG BAO GIỜ hiện ra
      dưới dạng giây — bài học của TN-01 là CÁI NÀO CHẠM ĐẤT TRƯỚC, không phải
      "hết bao nhiêu giây". Đừng thêm đồng hồ bấm giây vào đây mà chưa tra nguồn
      cho `g` tuyệt đối.

   ⚠️ LÔNG CHIM TRÊN TRÁI ĐẤT LÀ HÌNH MINH HOẠ ĐỊNH TÍNH, KHÔNG PHẢI MÔ PHỎNG.
      Lực cản không khí thật phụ thuộc hình dạng, diện tích, hệ số cản — dự án
      không có nguồn nào cho nó. Nên lông chim chỉ rơi CHẬM HƠN RÕ RỆT, và câu
      chữ đi kèm chỉ khẳng định đúng điều NASA nói: trong chân không hai vật rơi
      như nhau, trong không khí thì lông chim chậm hơn. `AIR_SLOW` vì thế là một
      con số cho DỄ ĐỌC, không phải một phép đo — có ghi chú ngay tại chỗ khai.
   ══════════════════════════════════════════════════════════════════════════ */
(function (global) {
  "use strict";

  var VW = 800, VH = 500;
  var BASE_MS = 950;        // nhịp cú rơi trên Trái Đất — chỉ để dễ nhìn (xem trên)
  var AIR_SLOW = 3.4;       // lông chim trong không khí chậm hơn bấy nhiêu lần — ĐỊNH TÍNH
  var PX_CAP = 1600000;     // trần pixel vùng vẽ, cùng lối js/game-shell.js

  var GROUND_Y = 430;       // mặt đất trong hệ ảo
  var TOP_Y = 96;           // độ cao thả

  function reduced() {
    try {
      return global.matchMedia &&
             global.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (e) { return false; }
  }

  function create(cv) {
    var ctx = cv.getContext("2d");
    var scene = null;          // "drop" | "float" | "weight"
    var opt = {};
    var raf = 0, t0 = 0, running = false, done = false;
    var doneCb = null;
    var floatT = 0;

    function dprFor(w, h) {
      var d = Math.min(2, global.devicePixelRatio || 1);
      while (d > 1 && w * d * h * d > PX_CAP) d -= 0.25;
      return Math.max(1, d);
    }

    function fit() {
      var r = cv.getBoundingClientRect();
      var w = Math.max(1, Math.round(r.width));
      var h = Math.max(1, Math.round(r.height));
      var d = dprFor(w, h);
      cv.width = Math.round(w * d);
      cv.height = Math.round(h * d);
      // Cả thế giới ảo được scale ra cỡ phần tử — mọi con số dưới đây là hệ ảo.
      ctx.setTransform(cv.width / VW, 0, 0, cv.height / VH, 0, 0);
    }

    /* ── nền: trời + đất, tông theo nơi ─────────────────────────────────── */
    function sky(place) {
      var g = ctx.createLinearGradient(0, 0, 0, VH);
      if (place === "moon") {
        g.addColorStop(0, "#05070f"); g.addColorStop(1, "#131a2e");
      } else if (place === "mercury") {
        g.addColorStop(0, "#0b0a12"); g.addColorStop(1, "#2a2030");
      } else if (place === "jupiter") {
        g.addColorStop(0, "#1a1024"); g.addColorStop(1, "#3a2340");
      } else {
        g.addColorStop(0, "#0a1330"); g.addColorStop(1, "#16346b");
      }
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, VW, VH);

      // Sao: chỉ ở nơi không có khí quyển dày — một chi tiết mang nghĩa, không trang trí
      if (place === "moon" || place === "mercury") {
        ctx.fillStyle = "rgba(234,241,255,.75)";
        for (var i = 0; i < 46; i++) {
          var x = (i * 137.5) % VW, y = (i * 61.7) % (GROUND_Y - 60);
          var s = (i % 4 === 0) ? 1.8 : 1.1;
          ctx.fillRect(x, y, s, s);
        }
      }
    }

    function ground(place) {
      var g = ctx.createLinearGradient(0, GROUND_Y, 0, VH);
      if (place === "moon") { g.addColorStop(0, "#6b7288"); g.addColorStop(1, "#3a3f4f"); }
      else if (place === "mercury") { g.addColorStop(0, "#7a6f78"); g.addColorStop(1, "#413a41"); }
      else if (place === "jupiter") { g.addColorStop(0, "#b08a5a"); g.addColorStop(1, "#5d452c"); }
      else { g.addColorStop(0, "#3f7a4a"); g.addColorStop(1, "#20402a"); }
      ctx.fillStyle = g;
      ctx.fillRect(0, GROUND_Y, VW, VH - GROUND_Y);
      ctx.strokeStyle = "rgba(234,241,255,.28)";
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(0, GROUND_Y); ctx.lineTo(VW, GROUND_Y); ctx.stroke();
    }

    /* ── hai vật của LAB-01 ─────────────────────────────────────────────── */
    function hammer(x, y) {
      ctx.save(); ctx.translate(x, y);
      ctx.fillStyle = "#9aa4bd";                       // cán
      ctx.fillRect(-3.5, -4, 7, 42);
      ctx.fillStyle = "#cfd7ea";                       // đầu búa
      ctx.fillRect(-19, -18, 38, 17);
      ctx.strokeStyle = "#0b1020"; ctx.lineWidth = 2.4;
      ctx.strokeRect(-19, -18, 38, 17);
      ctx.strokeRect(-3.5, -4, 7, 42);
      ctx.restore();
    }

    function feather(x, y, tilt) {
      ctx.save(); ctx.translate(x, y); ctx.rotate(tilt || 0);
      // Một đường bao kín hình giọt, không ghép nhiều mảnh — bài học của icon `comet`:
      // nhiều mảnh rời cách nhau vài đơn vị thì mắt gom lại thành đồ vật khác.
      ctx.beginPath();
      ctx.moveTo(0, -20);
      ctx.bezierCurveTo(12, -6, 10, 12, 0, 22);
      ctx.bezierCurveTo(-10, 12, -12, -6, 0, -20);
      ctx.closePath();
      ctx.fillStyle = "#f2e6a8";
      ctx.fill();
      ctx.strokeStyle = "#0b1020"; ctx.lineWidth = 2.2; ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, -18); ctx.lineTo(0, 20);
      ctx.strokeStyle = "rgba(11,16,32,.55)"; ctx.lineWidth = 1.6; ctx.stroke();
      ctx.restore();
    }

    /* Nhãn dưới mỗi vật — chữ là phần tử của CẢNH nên phải dịch theo ngôn ngữ,
       không nướng sẵn vào hình (bài học nhãn hành tinh của mission-map). */
    function label(x, y, s) {
      ctx.save();
      ctx.font = "600 17px Inter, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.lineWidth = 4; ctx.strokeStyle = "rgba(5,8,18,.85)";
      ctx.strokeText(s, x, y);
      ctx.fillStyle = "#eaf1ff";
      ctx.fillText(s, x, y);
      ctx.restore();
    }

    function drawDrop(now) {
      var place = opt.place || "earth";
      var r = global.AstroQLab ? AstroQLab.ratio(place) : 1;
      var L = (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
      var tx = function (k) { return global.AstroQLab ? AstroQLab.text(k, L) : k; };

      sky(place); ground(place);

      var span = GROUND_Y - TOP_Y - 22;
      // t ∝ 1/√g  ⇒  cú rơi ở nơi có g nhỏ hơn thì lâu hơn đúng √(1/r) lần.
      var msH = BASE_MS / Math.sqrt(r);
      // Không khí chỉ tồn tại ở nơi có khí quyển dày. Bốn nơi trong danh mục thì
      // chỉ Trái Đất có — Mặt Trăng "essentially in a vacuum" (nguyên văn NASA).
      var hasAir = (place === "earth");
      var msF = hasAir ? msH * AIR_SLOW : msH;

      var el = running ? (now - t0) : (done ? 1e9 : 0);
      var kH = Math.min(1, el / msH);
      var kF = Math.min(1, el / msF);
      // Rơi tự do: quãng đường theo t², nên vật tăng tốc dần chứ không đi đều.
      var yH = TOP_Y + span * kH * kH;
      var yF = hasAir
             // Trong không khí lông chim đạt tốc độ gần như đều rất sớm → gần tuyến tính.
             ? TOP_Y + span * kF
             : TOP_Y + span * kF * kF;

      hammer(VW * 0.36, yH);
      feather(VW * 0.62, yF, Math.sin(el / 220) * (hasAir ? 0.35 : 0.06));
      label(VW * 0.36, GROUND_Y + 34, tx("o_hammer"));
      label(VW * 0.62, GROUND_Y + 34, tx("o_feather"));

      if (running && kH >= 1 && kF >= 1) {
        running = false; done = true;
        if (doneCb) doneCb({ same: !hasAir, place: place });
      }
      return running;
    }

    /* ── LAB-02: trong trạm, mọi thứ rơi CÙNG NHAU ──────────────────────── */
    function drawFloat(now) {
      var L = (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
      var tx = function (k) { return global.AstroQLab ? AstroQLab.text(k, L) : k; };

      var g = ctx.createLinearGradient(0, 0, 0, VH);
      g.addColorStop(0, "#04060e"); g.addColorStop(1, "#0a1230");
      ctx.fillStyle = g; ctx.fillRect(0, 0, VW, VH);
      ctx.fillStyle = "rgba(234,241,255,.7)";
      for (var i = 0; i < 60; i++) ctx.fillRect((i * 149.3) % VW, (i * 83.1) % VH, 1.2, 1.2);

      // Trái Đất ở dưới: cái mà cả trạm đang rơi VỀ PHÍA
      var cx = VW / 2, cy = VH + 260, R = 330;
      var eg = ctx.createRadialGradient(cx - 90, cy - 150, 40, cx, cy, R);
      eg.addColorStop(0, "#7fd3ff"); eg.addColorStop(.55, "#2a6fc9"); eg.addColorStop(1, "#0d2450");
      ctx.fillStyle = eg;
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();

      // Trạm: trôi theo một cung — "rơi về phía Trái Đất mà cứ đi vòng quanh"
      floatT = reduced() ? 0 : (now / 1000);
      var sx = cx + Math.sin(floatT * 0.42) * 120;
      var sy = 200 + Math.cos(floatT * 0.42) * 16;

      ctx.save(); ctx.translate(sx, sy);
      ctx.fillStyle = "#1a2340"; ctx.strokeStyle = "#8fb6ff"; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.roundRect(-140, -66, 280, 132, 26); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#0a1024";
      for (var p = -1; p <= 1; p++) {                    // cửa sổ
        ctx.beginPath(); ctx.arc(p * 76, -18, 15, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = "rgba(143,182,255,.7)"; ctx.lineWidth = 2; ctx.stroke();
      }
      // Phi hành gia + cây bút: KHÔNG chuyển động tương đối với nhau — đó là cả
      // bài học. Chỉ dập dềnh rất nhẹ cho thấy không có gì "đứng trên sàn".
      var bob = reduced() ? 0 : Math.sin(floatT * 1.6) * 4;
      ctx.font = "44px system-ui, sans-serif"; ctx.textAlign = "center";
      ctx.fillText("🧑‍🚀", -34, 26 + bob);
      ctx.fillText("🖊️", 46, 20 + bob);
      ctx.restore();

      label(sx, sy + 96, tx("o_pen"));
      return !reduced();
    }

    /* ── LAB-03: cái cân ────────────────────────────────────────────────── */
    function drawWeight() {
      var place = opt.place || "earth";
      var L = (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
      var tx = function (k) { return global.AstroQLab ? AstroQLab.text(k, L) : k; };
      var kg = global.AstroQLab ? AstroQLab.weighAt(place, 30) : 30;

      sky(place); ground(place);

      // Đứa trẻ đứng trên cân
      ctx.font = "84px system-ui, sans-serif"; ctx.textAlign = "center";
      ctx.fillText("🧒", VW * 0.5, GROUND_Y - 74);

      // Mặt cân
      ctx.save(); ctx.translate(VW * 0.5, GROUND_Y - 30);
      ctx.fillStyle = "#cfd7ea"; ctx.strokeStyle = "#0b1020"; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.roundRect(-96, -14, 192, 30, 8); ctx.fill(); ctx.stroke();
      ctx.restore();

      // Số trên cân — thứ ĐỔI theo nơi
      ctx.save();
      ctx.font = "800 58px 'Space Grotesk', Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.lineWidth = 6; ctx.strokeStyle = "rgba(5,8,18,.9)";
      var s = kg.toFixed(1).replace(".", ",") + " kg";
      ctx.strokeText(s, VW * 0.5, GROUND_Y - 128);
      ctx.fillStyle = "#ffcf6b";
      ctx.fillText(s, VW * 0.5, GROUND_Y - 128);
      ctx.restore();

      // Khối lượng: KHÔNG đổi — vẽ cạnh nhau mới thấy được điều đó
      label(VW * 0.5, 60, tx("ui_mass") + " 30 kg — " + tx("ui_unchanged"));
      return false;                                     // cảnh tĩnh
    }

    function frame(now) {
      raf = 0;
      var keep = false;
      if (scene === "drop") keep = drawDrop(now);
      else if (scene === "float") keep = drawFloat(now);
      else if (scene === "weight") keep = drawWeight(now);
      if (keep) raf = global.requestAnimationFrame(frame);
    }

    function paint() {
      if (raf) global.cancelAnimationFrame(raf);
      raf = global.requestAnimationFrame(frame);
    }

    return {
      /* kind: "drop"|"float"|"weight"  ·  o: {place} */
      setScene: function (kind, o) {
        scene = kind; opt = o || {};
        running = false; done = false;
        fit(); paint();
      },
      setPlace: function (id) {
        opt.place = id;
        running = false; done = false;
        fit(); paint();
      },
      drop: function () {
        if (scene !== "drop" || running) return;
        // reduced-motion: KHÔNG bỏ cú rơi (nó là nội dung bài học, không phải
        // trang trí) — chỉ đi nhanh hơn. Cùng cách `005` xử phần đổi tông màu.
        running = true; done = false;
        t0 = (global.performance ? performance.now() : Date.now());
        if (reduced()) t0 -= BASE_MS * 0.55;
        paint();
      },
      reset: function () { running = false; done = false; paint(); },
      onDone: function (cb) { doneCb = cb; },
      resize: function () { fit(); paint(); },
      isRunning: function () { return running; },
      isDone: function () { return done; }
    };
  }

  global.AstroQLabDrop = { create: create, VW: VW, VH: VH };
})(window);
