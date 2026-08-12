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

  /* ⚠️⚠️ VẾT ĐÈN NHÁY (ghost strobe) — THỨ LÀM BÀI HỌC HIỆN RA, KHÔNG PHẢI TRANG TRÍ.
     Cứ mỗi `STROBE_MS` để lại một bản mờ của từng vật. Vì nhịp đó CỐ ĐỊNH, khoảng
     cách giữa các bậc chính là bằng chứng của gia tốc: trên Mặt Trăng hai cái thang
     ghost xếp ĐÚNG TỪNG BẬC ⇒ *"rơi nhanh như nhau"* thành một thứ NHÌN THẤY thay vì
     một câu người lớn nói. Trên Trái Đất thang của lông chim thưa và ngắn hơn hẳn.
     ⚠️ Nó KHÔNG phát biểu một con số thời gian nào, nên không phạm luật ③ của
        js/lab-catalog.js (không hiện thời gian rơi tuyệt đối). Đừng thêm đồng hồ. */
  var STROBE_MS = 110;
  var GHOST_MAX = 40;       // trần số bản mờ MỖI VẬT (vạch mảnh nên 40 vẫn đọc ra bậc)
  var SLOW = 0.35;          // hệ số "Xem chậm"; không đổi kết quả, chỉ đổi nhịp xem

  var GROUND_Y = 430;       // mặt đất trong hệ ảo
  var TOP_Y = 96;           // độ cao thả

  /* Viết số cho người Việt đọc (dấu phẩy thập phân). ⚠️ Ở tầm MODULE chứ không khai
     cục bộ trong từng cảnh: bản đầu khai trong `drawWeight` rồi `drawDrops` cũng gọi
     → `num is not defined` giết cả cảnh. Một cách viết số cho cả file. */
  function num(v) { return String(v).replace(".", ","); }

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
    var slow = false;                 // "Xem chậm"
    var ghosts = [];                  // [{x,y,kind}] các bản mờ đã để lại
    var nGh = { h: 0, f: 0 };         // đếm theo TỪNG vật, không đếm tổng
    var nextStrobe = 0;
    var landed = { h: 0, f: 0 };      // mốc thời gian chạm đất của từng vật (0 = chưa)
    var puffs = [];                   // [{x,t}] bụi bung khi chạm đất
    var sfxDone = false;

    function sfx(name, arg) {
      /* Dùng chung `js/sfx.js` nên nó tôn trọng ĐÚNG một lựa chọn tắt tiếng
         `astroq-sfx` của cả app. Không có file thì im lặng, không vỡ. */
      try {
        var S = global.AstroQSfx;
        if (S && typeof S[name] === "function") S[name](arg);
      } catch (e) {}
    }

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
      /* ⚠️ Sao Mộc KHÔNG có mặt đất thật (NASA Jupiter Facts) — vẽ nó thành dải mây
         cuộn, đừng vẽ thành đất. Một mảng nâu ở đáy khung đọc ra thành "mặt đất",
         tức dạy một điều sai ngay ở phần hình. */
      else if (place === "jupiter") { g.addColorStop(0, "#d8b48a"); g.addColorStop(1, "#8a6440"); }
      else { g.addColorStop(0, "#3f7a4a"); g.addColorStop(1, "#20402a"); }
      ctx.fillStyle = g;
      ctx.fillRect(0, GROUND_Y, VW, VH - GROUND_Y);
      if (place === "jupiter") {
        // Dải mây: các vạch ngang mờ, KHÔNG có đường ranh giới "mặt đất" cứng.
        for (var bi = 0; bi < 5; bi++) {
          ctx.fillStyle = bi % 2 ? "rgba(255,240,215,.16)" : "rgba(90,55,30,.22)";
          ctx.fillRect(0, GROUND_Y + bi * 14, VW, 14);
        }
      } else {
        ctx.strokeStyle = "rgba(234,241,255,.28)";
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(0, GROUND_Y); ctx.lineTo(VW, GROUND_Y); ctx.stroke();
      }
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

    /* Vạch đích ở mặt đất — trẻ cần một MỐC để nói "cái nào tới trước". */
    function finishLine(flash) {
      ctx.save();
      ctx.setLineDash([9, 7]);
      ctx.lineWidth = flash ? 4 : 2;
      ctx.strokeStyle = flash ? "rgba(134,239,172,.95)" : "rgba(234,241,255,.34)";
      ctx.beginPath(); ctx.moveTo(0, GROUND_Y); ctx.lineTo(VW, GROUND_Y); ctx.stroke();
      ctx.restore();
    }

    /* Bụi bung lúc chạm đất — vẽ bằng cung mờ dần, KHÔNG dùng shadowBlur. */
    function puff(x, age) {
      var k = Math.min(1, age / 420);
      if (k >= 1) return;
      ctx.save();
      ctx.globalAlpha = (1 - k) * 0.5;
      ctx.strokeStyle = "#eaf1ff"; ctx.lineWidth = 2.4;
      for (var i = 0; i < 3; i++) {
        var rr = 8 + k * (26 + i * 9);
        ctx.beginPath(); ctx.arc(x, GROUND_Y - 2, rr, Math.PI * 1.08, Math.PI * 1.92);
        ctx.stroke();
      }
      ctx.restore();
    }

    /* Huy hiệu thứ tự chạm đất. `same` → cả hai đều mang dấu "=" thay vì 1st/2nd:
       trên Mặt Trăng KHÔNG có ai thắng, và đó chính là bài học. */
    function orderTag(x, txt, tone) {
      ctx.save();
      ctx.font = "800 20px 'Space Grotesk', Inter, sans-serif";
      ctx.textAlign = "center";
      /* ⚠️ ĐẶT TRÊN ĐẦU VẬT, KHÔNG ĐẶT Ở `GROUND_Y - 26`. Vật hạ cánh với tâm ở
         `GROUND_Y - 22`, mà búa vẽ từ `y-18` tới `y+38` ⇒ mốc cũ rơi ĐÚNG VÀO
         giữa cái búa; ảnh chụp cho thấy chữ "1" và "=" nằm đè lên vật, đọc ra như
         lỗi vẽ. Chỉ soi ảnh mới thấy — đọc code thì hai con số đều "hợp lý". */
      var ty = GROUND_Y - 62;
      ctx.lineWidth = 5; ctx.strokeStyle = "rgba(5,8,18,.9)";
      ctx.strokeText(txt, x, ty);
      ctx.fillStyle = tone;
      ctx.fillText(txt, x, ty);
      ctx.restore();
    }

    function drawDrop(now) {
      var place = opt.place || "earth";
      var r = global.AstroQLab ? AstroQLab.ratio(place) : 1;
      var L = (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
      var tx = function (k) { return global.AstroQLab ? AstroQLab.text(k, L) : k; };

      sky(place); ground(place);

      var span = GROUND_Y - TOP_Y - 22;
      var mul = slow ? (1 / SLOW) : 1;
      // t ∝ 1/√g  ⇒  cú rơi ở nơi có g nhỏ hơn thì lâu hơn đúng √(1/r) lần.
      var msH = BASE_MS / Math.sqrt(r) * mul;
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
      var xH = VW * 0.36, xF = VW * 0.62;

      /* ── ghi VẾT ĐÈN NHÁY theo nhịp CỐ ĐỊNH ──
         Nhịp cố định là cả điểm: khoảng cách giữa hai bậc kề nhau = quãng đường vật
         đi trong cùng một lượng thời gian, nên hai cái thang xếp trùng bậc là bằng
         chứng "rơi nhanh như nhau". Nhịp đo theo thời gian THẬT, không theo `mul`,
         nên "Xem chậm" cho ra NHIỀU bậc hơn chứ không đổi hình dạng thang. */
      if (running && el >= nextStrobe) {
        // ⚠️ Trần đếm THEO TỪNG VẬT. Trần tính trên TỔNG thì thang của lông chim
        //    (cần ~29 bậc ở chế độ xem chậm) bị cắt giữa đường — đọc ra như lỗi vẽ.
        if (kH < 1 && nGh.h < GHOST_MAX) { ghosts.push({ x: xH, y: yH, kind: "h" }); nGh.h++; }
        if (kF < 1 && nGh.f < GHOST_MAX) { ghosts.push({ x: xF, y: yF, kind: "f" }); nGh.f++; }
        nextStrobe = el + STROBE_MS * mul;
      }
      /* ⚠️⚠️ BẢN MỜ VẼ BẰNG VẠCH NGANG, KHÔNG VẼ LẠI HÌNH VẬT — và đây là một lỗi
         hình THẬT đã sửa sau khi soi ảnh chụp. Bản đầu vẽ lại chính cái búa / cái
         lông chim ở mỗi bậc: búa thì ra thang bậc rõ ràng, nhưng LÔNG CHIM rơi
         chậm nên các bản mờ chồng lên nhau và HÀN THÀNH MỘT DẢI LIỀN — mất hẳn
         nghĩa "từng bậc", tức mất luôn bằng chứng. Đúng ràng buộc hình học đã trả
         giá ở bộ icon sticker: hai hình cách nhau dưới ngưỡng thì mắt gom lại
         thành một khối khác.
         ⚠️ Và CỐ Ý KHÔNG chữa bằng cách "chỉ ghi bản mờ khi vật đã đi đủ xa" —
         làm thế thì khoảng cách giữa các bậc thôi mã hoá THỜI GIAN, mà chính cái
         đó mới là bằng chứng. Vạch mảnh giữ được nhịp thời gian VÀ không hàn. */
      for (var i = 0; i < ghosts.length; i++) {
        var g = ghosts[i];
        ctx.save();
        ctx.globalAlpha = 0.34;
        ctx.strokeStyle = (g.kind === "h") ? "#cfd7ea" : "#f2e6a8";
        ctx.lineWidth = 2.6;
        ctx.beginPath();
        ctx.moveTo(g.x - 13, g.y); ctx.lineTo(g.x + 13, g.y);
        ctx.stroke();
        ctx.restore();
      }

      /* ── chạm đất: ghi mốc, bung bụi, kêu một tiếng ── */
      if (running && kH >= 1 && !landed.h) { landed.h = el; puffs.push({ x: xH, t: el }); sfx("beep", 240); }
      if (running && kF >= 1 && !landed.f) { landed.f = el; puffs.push({ x: xF, t: el }); sfx("beep", 200); }

      var bothDown = (kH >= 1 && kF >= 1);
      finishLine(bothDown);
      for (var j = 0; j < puffs.length; j++) puff(puffs[j].x, el - puffs[j].t);

      hammer(xH, yH);
      feather(xF, yF, Math.sin(el / 220) * (hasAir ? 0.35 : 0.06));
      label(xH, GROUND_Y + 34, tx("o_hammer"));
      label(xF, GROUND_Y + 34, tx("o_feather"));

      if (bothDown) {
        if (hasAir) {
          orderTag(xH, "1", "#ffcf6b");
          orderTag(xF, "2", "rgba(234,241,255,.8)");
        } else {
          // Không ai thắng — dấu "=" ở CẢ HAI, đó là kết quả của thí nghiệm.
          orderTag(xH, "=", "#86efac");
          orderTag(xF, "=", "#86efac");
        }
      }

      if (running && bothDown) {
        if (!sfxDone) { sfxDone = true; sfx(hasAir ? "nope" : "ready"); }
        running = false; done = true;
        if (doneCb) doneCb({ same: !hasAir, place: place });
      }
      // Còn bụi đang tan thì vẫn vẽ tiếp vài khung nữa.
      return running || (done && (el - Math.max(landed.h, landed.f)) < 480);
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
      ctx.fillText("🍎", 46, 20 + bob);
      ctx.restore();

      label(sx, sy + 96, tx("o_apple"));
      return !reduced();
    }

    /* ── LAB-03: cái cân ────────────────────────────────────────────────── */
    /* ── NGƯỜI ĐỨNG (vector, có thân và CHÂN) ──────────────────────────────
       ⚠️ Cố ý KHÔNG dùng emoji 🧒: nó chỉ là MỘT CÁI ĐẦU, nên "đứng trên cân"
       không đọc ra được gì — chính chỗ chủ dự án hỏi *"phần trống trắng dưới cái
       đầu để làm gì?"*. Vẽ vector thì có chân, và chân đặt đúng lên mặt cân.
       `suit` = nơi không có khí quyển thở được → thêm mũ phi hành gia. Đó là một
       chi tiết MANG NGHĨA (không mặc thì không sống được), không phải trang trí. */
    function person(x, footY, h, suit) {
      var s = h / 100;                       // h = chiều cao toàn thân
      var headR = 15 * s;
      var hipY = footY - 42 * s;
      var shY = footY - 74 * s;              // vai
      var headY = shY - headR - 3 * s;

      ctx.save();
      ctx.lineCap = "round"; ctx.lineJoin = "round";
      ctx.strokeStyle = "#0b1020"; ctx.lineWidth = 3 * s;

      // hai chân
      ctx.beginPath();
      ctx.moveTo(x - 9 * s, footY); ctx.lineTo(x - 5 * s, hipY);
      ctx.moveTo(x + 9 * s, footY); ctx.lineTo(x + 5 * s, hipY);
      ctx.strokeStyle = "#5f7fc7"; ctx.lineWidth = 9 * s; ctx.stroke();

      // thân
      ctx.beginPath();
      ctx.moveTo(x, hipY); ctx.lineTo(x, shY);
      ctx.strokeStyle = suit ? "#dfe7f7" : "#7fd3ff"; ctx.lineWidth = 20 * s; ctx.stroke();

      // hai tay
      ctx.beginPath();
      ctx.moveTo(x - 10 * s, shY + 4 * s); ctx.lineTo(x - 20 * s, hipY + 6 * s);
      ctx.moveTo(x + 10 * s, shY + 4 * s); ctx.lineTo(x + 20 * s, hipY + 6 * s);
      ctx.strokeStyle = suit ? "#dfe7f7" : "#7fd3ff"; ctx.lineWidth = 8 * s; ctx.stroke();

      // đầu
      ctx.beginPath(); ctx.arc(x, headY, headR, 0, Math.PI * 2);
      ctx.fillStyle = "#f2c9a0"; ctx.fill();
      ctx.strokeStyle = "#0b1020"; ctx.lineWidth = 2.4 * s; ctx.stroke();

      if (suit) {
        // Mũ phi hành gia: vòng kính trong + vành trắng
        ctx.beginPath(); ctx.arc(x, headY, headR + 6 * s, 0, Math.PI * 2);
        ctx.strokeStyle = "#dfe7f7"; ctx.lineWidth = 5 * s; ctx.stroke();
        ctx.beginPath(); ctx.arc(x, headY, headR + 6 * s, Math.PI * 1.05, Math.PI * 1.75);
        ctx.strokeStyle = "rgba(143,215,255,.85)"; ctx.lineWidth = 5 * s; ctx.stroke();
      }
      ctx.restore();
    }

    function drawWeight() {
      var place = opt.place || "earth";
      var L = (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
      var tx = function (k) { return global.AstroQLab ? AstroQLab.text(k, L) : k; };
      var base = opt.kg || 30;                          // cân nặng ở Trái Đất, trẻ tự nhập
      var r = global.AstroQLab ? AstroQLab.ratio(place) : 1;
      var kg = global.AstroQLab ? AstroQLab.weighAt(place, base) : base;
      sky(place); ground(place);

      /* ⚠️⚠️ SAO MỘC KHÔNG CÓ MẶT ĐẤT ĐỂ ĐỨNG, nên KHÔNG vẽ người đứng trên "đất"
         Sao Mộc — đó là dạy một điều sai. Nguồn: NASA Jupiter Facts, nguyên văn
         *"As a gas giant, Jupiter doesn't have a true surface. The planet is mostly
         swirling gases and liquids."* ⇒ Sao Mộc vẽ thành DẢI MÂY và người LƠ LỬNG,
         kèm một câu nói thẳng rằng đây là thí nghiệm TƯỞNG TƯỢNG. Chính nguồn Space
         Place cũng viết ở thể điều kiện: *"If ... you were on heavy Jupiter"*. */
      var noGround = (place === "jupiter");
      /* Nơi không có khí quyển thở được thì người mang mũ phi hành gia — một chi
         tiết MANG NGHĨA. Trái Đất thì không. */
      var suit = (place !== "earth");

      /* ⚠️ BỐ CỤC TÍNH TỪ DƯỚI LÊN, KHÔNG GÕ MỐC RỜI. Bản đầu vẽ số ở
         `GROUND_Y - 128` trong khi hình người chiếm ~272..356 ⇒ SỐ ĐÈ LÊN HÌNH.
         Nay mỗi tầng suy ra từ tầng dưới nó, nên đổi cỡ chữ hay cỡ hình thì bố cục
         tự giãn theo. */
      /* ⚠️ Cân cao 62px tính TỪ `plateY`, nên `GROUND_Y - 16` làm nó chạm tới
         `GROUND_Y + 46` và ĐÈ LÊN tên nơi ở `GROUND_Y + 36` — ảnh chụp cho thấy
         "Trái Đất" và "Mặt Trăng" bị che một nửa. Nhấc lên để đáy cân đúng bằng
         mặt đất. */
      var plateY = noGround ? GROUND_Y - 96 : GROUND_Y - 62;   // mặt cân
      var H = 150;                                            // chiều cao người
      var footY = plateY - 15;                                // chân đứng trên cân
      var headTop = footY - H;
      var workY = headTop - 22;                               // dòng phép tính
      var bigY = workY - 40;                                  // số to

      person(VW * 0.5, footY, H, suit);

      /* ── CÁI CÂN, VÀ SỐ NẰM TRONG NÓ ──
         ⚠️ Bản đầu là một hình chữ nhật sáng RỖNG với số nằm ở tít trên, nên nó đọc
         ra thành "phần trống trắng" — đúng như chủ dự án hỏi. Đặt số VÀO ô hiển thị
         của cân thì cái ô đó có việc, và nó giống một cái cân thật. */
      ctx.save(); ctx.translate(VW * 0.5, plateY);
      ctx.fillStyle = "#b9c4dc"; ctx.strokeStyle = "#0b1020"; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.roundRect(-118, -13, 236, 62, 12); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#0d1426";                              // ô hiển thị
      ctx.beginPath(); ctx.roundRect(-84, 6, 168, 34, 8); ctx.fill();
      ctx.strokeStyle = "rgba(143,215,255,.5)"; ctx.lineWidth = 2; ctx.stroke();
      ctx.font = "800 25px 'Space Grotesk', ui-monospace, monospace";
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillStyle = "#7fe3a0";
      ctx.fillText(num(kg) + " kg", 0, 24);
      ctx.textBaseline = "alphabetic";
      ctx.restore();

      // Số to phía trên — cùng con số, đọc được từ xa
      ctx.save();
      ctx.font = "800 50px 'Space Grotesk', Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.lineWidth = 6; ctx.strokeStyle = "rgba(5,8,18,.9)";
      var s = num(kg) + " kg";
      ctx.strokeText(s, VW * 0.5, bigY);
      ctx.fillStyle = "#ffcf6b";
      ctx.fillText(s, VW * 0.5, bigY);
      ctx.restore();

      /* PHÉP TÍNH HIỆN RA — đây là chỗ công thức thành thứ trẻ KIỂM CHỨNG ĐƯỢC,
         không phải một câu phải tin. Ở Trái Đất thì `× 1` là vô nghĩa nên bỏ dòng
         này đi: một phép tính không nói thêm điều gì chỉ làm màn hình rối. */
      if (place !== "earth") {
        ctx.save();
        ctx.font = "600 22px ui-monospace, 'Space Grotesk', monospace";
        ctx.textAlign = "center";
        /* ⚠️ Tỉ lệ lấy từ `ratioLabel`, KHÔNG làm tròn `ratio`: xem cảnh báo ở
           PLACES của js/lab-catalog.js — làm tròn thì "30 × 0,17 = 5" là một phép
           tính SAI hiện trên màn hình. */
        var rl = global.AstroQLab ? AstroQLab.ratioLabel(place, L) : "1";
        var w = num(base) + " × " + rl + " = " + num(kg);
        ctx.lineWidth = 5; ctx.strokeStyle = "rgba(5,8,18,.9)";
        ctx.strokeText(w, VW * 0.5, workY);
        ctx.fillStyle = "#8fd7ff";
        ctx.fillText(w, VW * 0.5, workY);
        ctx.restore();
      }

      // Khối lượng: KHÔNG đổi — vẽ cạnh nhau mới thấy được điều đó
      label(VW * 0.5, 40, tx("ui_mass") + " " + num(base) + " kg — " + tx("ui_unchanged"));
      // Tên nơi, dưới chân — để "ở đâu" luôn đọc được ngay trên cảnh
      label(VW * 0.5, GROUND_Y + 30, tx("p_" + place));
      /* ⚠️ Dòng "không có mặt đất" đặt TRÊN mặt đất, không đặt dưới tên nơi: ở
         `GROUND_Y + 62` = 492 nó sát mép khung 500px và bị cắt trên màn thấp. Với
         Sao Mộc thì cân nhấc lên tận `GROUND_Y - 96` nên khoảng dưới nó đang trống. */
      if (noGround) label(VW * 0.5, GROUND_Y - 8, tx("ui_no_ground"));
      return false;                                     // cảnh tĩnh
    }

    /* Dọn dấu vết của LƯỢT TRƯỚC. ⚠️ Thiếu hàm này thì vết đèn nháy của lượt cũ
       nằm lại trên cảnh và trẻ đọc ra thành một cú rơi khác — một lỗi im lặng. */
    function clearRun() {
      ghosts = []; nGh = { h: 0, f: 0 }; puffs = []; nextStrobe = 0;
      landed = { h: 0, f: 0 }; sfxDone = false;
    }

    /* ══ LAB-07: vì sao trời xanh ══════════════════════════════════════════
       Trẻ hạ Mặt Trời xuống dần và TỰ TẠO RA ráng chiều. Ba nấc rời rạc, không
       thanh trượt liên tục — cùng lý do đã ghi ở mục 10 của đề xuất: một thanh
       trượt khẳng định CẢ MỘT DẢI, trong khi nguồn chỉ chống lưng cho ba câu.
       Màu trời suy từ ĐÚNG điều nguồn nói: càng thấp thì ánh sáng đi qua càng
       nhiều khí quyển ⇒ xanh bị tán xạ đi càng nhiều ⇒ còn lại đỏ/vàng. */
    function drawSky() {
      var step = opt.place || "noon";
      var L = (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
      var tx = function (k) { return global.AstroQLab ? AstroQLab.text(k, L) : k; };

      // k = 0 giữa trưa · 1 sát chân trời
      var k = (step === "horizon") ? 1 : (step === "evening") ? 0.55 : 0;
      var sunY = 120 + k * (GROUND_Y - 150);
      var sunX = VW * (0.5 + k * 0.28);

      // Trời: xanh đậm trên, và càng thấp Mặt Trời thì mép trời càng ngả đỏ.
      var g = ctx.createLinearGradient(0, 0, 0, GROUND_Y);
      g.addColorStop(0, k < 0.3 ? "#1f6fd0" : k < 0.8 ? "#2a4a86" : "#241a3e");
      g.addColorStop(0.62, k < 0.3 ? "#63b3f2" : k < 0.8 ? "#b3733f" : "#8c3a2e");
      g.addColorStop(1, k < 0.3 ? "#bfe3ff" : k < 0.8 ? "#f0a35a" : "#e5613a");
      ctx.fillStyle = g; ctx.fillRect(0, 0, VW, GROUND_Y);

      // Mặt Trời: hào quang bằng gradient toả, KHÔNG dùng shadowBlur.
      var hal = ctx.createRadialGradient(sunX, sunY, 6, sunX, sunY, 120);
      hal.addColorStop(0, k < 0.3 ? "rgba(255,250,220,.95)" : "rgba(255,190,120,.95)");
      hal.addColorStop(1, "rgba(255,190,120,0)");
      ctx.fillStyle = hal;
      ctx.beginPath(); ctx.arc(sunX, sunY, 120, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = k < 0.3 ? "#fffbe6" : "#ffcf6b";
      ctx.beginPath(); ctx.arc(sunX, sunY, 26, 0, Math.PI * 2); ctx.fill();

      /* Đường ánh sáng đi qua khí quyển — thứ MANG bài học: nó dài ra khi Mặt Trời
         xuống thấp, và chính độ dài đó là lý do màu xanh bị tán xạ hết. */
      ctx.save();
      ctx.setLineDash([7, 6]); ctx.lineWidth = 2;
      ctx.strokeStyle = "rgba(255,255,255,.55)";
      ctx.beginPath(); ctx.moveTo(sunX, sunY); ctx.lineTo(VW * 0.16, GROUND_Y - 26); ctx.stroke();
      ctx.restore();

      // Mặt đất + một người nhìn lên (để "tới mắt em" có chỗ neo)
      ctx.fillStyle = "#16281c"; ctx.fillRect(0, GROUND_Y, VW, VH - GROUND_Y);
      ctx.font = "42px system-ui, sans-serif"; ctx.textAlign = "center";
      ctx.fillText("🧒", VW * 0.16, GROUND_Y - 4);

      label(VW * 0.16, GROUND_Y + 34, tx("p_" + step));
      return false;                                   // cảnh tĩnh
    }

    /* ══ LAB-08: 100 giọt nước ══════════════════════════════════════════════
       Bốn nấc, mỗi nấc tô lại đúng số giọt mà NGUỒN nói. 100 giọt là một cách
       ĐỌC con số phần trăm, không phải một con số mới — nên nó không cần nguồn
       riêng, chỉ cần đúng tỉ lệ. */
    function drawDrops() {
      var step = opt.place || "all";
      var L = (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
      var tx = function (k) { return global.AstroQLab ? AstroQLab.text(k, L) : k; };

      var g = ctx.createLinearGradient(0, 0, 0, VH);
      g.addColorStop(0, "#071026"); g.addColorStop(1, "#0d1b3a");
      ctx.fillStyle = g; ctx.fillRect(0, 0, VW, VH);

      var W = global.AstroQLab ? AstroQLab.waterStep(step)
                               : { a: 0, b: 100, n: 100, kind: "all" };
      var TONE = { all: "#5fd3ff", salt: "#8f7bff", fresh: "#86efac", ice: "#eaf1ff" };
      var tone = TONE[W.kind] || TONE.all;

      var cols = 20, gap = 30, R = 9;
      var x0 = (VW - (cols - 1) * gap) / 2, y0 = 176;
      for (var i = 0; i < 100; i++) {
        var cx = x0 + (i % cols) * gap, cy = y0 + Math.floor(i / cols) * gap;

        /* ⚠️⚠️ VẼ CẢ GIỌT LẺ. Bản đầu làm tròn ngầm (bật sáng 96 hoặc 4 giọt) nên cái
           HÌNH không bao giờ khớp con SỐ — chính chỗ sinh ra cảm giác "vô lý". Phần
           phủ của giọt thứ i là độ chồng giữa [i, i+1) và đoạn [a, b) của nấc, nên
           96,5 ra đúng 96 giọt đầy + MỘT NỬA giọt. */
        var f = Math.max(0, Math.min(W.b, i + 1) - Math.max(W.a, i));

        // Giọt "tắt" vẽ trước, luôn đủ 100 giọt để mắt còn thấy MẪU SỐ.
        ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(143,182,255,.14)"; ctx.fill();

        if (f > 0.001) {
          ctx.save();
          if (f < 0.999) {               // giọt LẺ: chỉ tô phần bên trái theo tỉ lệ
            ctx.beginPath();
            ctx.rect(cx - R, cy - R, 2 * R * f, 2 * R);
            ctx.clip();
          }
          ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2);
          ctx.fillStyle = tone; ctx.fill();
          ctx.restore();
        }
        ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(5,8,18,.55)"; ctx.lineWidth = 1.5; ctx.stroke();
      }

      /* ⚠️⚠️ SỐ TO PHẢI CÙNG ĐƠN VỊ VỚI CÁI HÌNH — SỐ GIỌT, không phải phần trăm.
         Bản đầu in "68%" trên một cái hình 100 giọt có 2 giọt sáng: 68% là của NƯỚC
         NGỌT (3,5 giọt) chứ không phải của 100 giọt, nên số và hình nói hai điều khác
         nhau (2/100 mới là 2%). Chủ dự án bắt được ngay ở ảnh chụp. */
      ctx.save();
      ctx.font = "800 44px 'Space Grotesk', Inter, sans-serif"; ctx.textAlign = "center";
      ctx.lineWidth = 6; ctx.strokeStyle = "rgba(5,8,18,.9)";
      var big = num(W.n) + " " + tx("ui_drops_unit");
      ctx.strokeText(big, VW / 2, 94); ctx.fillStyle = "#ffcf6b";
      ctx.fillText(big, VW / 2, 94);
      ctx.restore();

      /* Dòng phép tính cho nấc "băng" — cùng khuôn với "50 × 2,53 = 126,5" của
         LAB-03, và đây là chỗ con số 68% được NÓI RÕ là 68% CỦA CÁI GÌ. */
      if (W.kind === "ice" && global.AstroQLab) {
        ctx.save();
        ctx.font = "600 21px ui-monospace, 'Space Grotesk', monospace";
        ctx.textAlign = "center";
        var line = AstroQLab.WATER.iceOfFresh + "% × " + num(AstroQLab.WATER.fresh) +
                   " = " + num(W.n) + " " + tx("ui_drops_unit");
        ctx.lineWidth = 5; ctx.strokeStyle = "rgba(5,8,18,.9)";
        ctx.strokeText(line, VW / 2, 128); ctx.fillStyle = "#8fd7ff";
        ctx.fillText(line, VW / 2, 128);
        ctx.restore();
      }

      // Nhãn nấc + MẪU SỐ nói ra bằng chữ, để "trên 100" không phải suy từ hình.
      label(VW / 2, 372, tx("p_" + step) + " — " + tx("ui_of_100"));
      return false;
    }

    function frame(now) {
      raf = 0;
      var keep = false;
      if (scene === "drop") keep = drawDrop(now);
      else if (scene === "float") keep = drawFloat(now);
      else if (scene === "weight") keep = drawWeight(now);
      else if (scene === "sky") keep = drawSky();
      else if (scene === "drops") keep = drawDrops();
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
        clearRun(); running = false; done = false;
        fit(); paint();
      },
      setPlace: function (id) {
        opt.place = id;
        clearRun(); running = false; done = false;
        fit(); paint();
      },
      /* Cân nặng ở Trái Đất do trẻ tự nhập. Kẹp ở tầng này NỮA (trang cũng kẹp) —
         một giá trị vô lý lọt vào đây thì cảnh vẽ ra một con số vô nghĩa. */
      setKg: function (v) {
        var n = parseFloat(v);
        if (!isFinite(n) || n <= 0) n = 30;
        opt.kg = Math.min(200, Math.max(1, n));
        paint();
        return opt.kg;
      },
      drop: function () {
        if (scene !== "drop" || running) return;
        // reduced-motion: KHÔNG bỏ cú rơi (nó là nội dung bài học, không phải
        // trang trí) — chỉ đi nhanh hơn. Cùng cách `005` xử phần đổi tông màu.
        clearRun();
        running = true; done = false;
        t0 = (global.performance ? performance.now() : Date.now());
        if (reduced()) t0 -= BASE_MS * 0.55;
        paint();
      },
      /* "Xem chậm" — chỉ đổi nhịp XEM, không đổi kết quả nào. Trả về trạng thái
         mới để trang tự đổi nhãn nút. */
      toggleSlow: function () { slow = !slow; clearRun(); paint(); return slow; },
      isSlow: function () { return slow; },
      reset: function () { clearRun(); running = false; done = false; paint(); },
      onDone: function (cb) { doneCb = cb; },
      resize: function () { fit(); paint(); },
      isRunning: function () { return running; },
      isDone: function () { return done; }
    };
  }

  global.AstroQLabDrop = { create: create, VW: VW, VH: VH };
})(window);
