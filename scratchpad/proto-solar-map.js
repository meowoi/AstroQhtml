/* ==========================================================
   proto-solar-map.js — BẢN ĐỒ NHIỆM VỤ vẽ trên canvas 2D.

   PORT TỪ `img/solar-system-simulation.html` (856 dòng, có sẵn trong dự án từ
   21/07/2026). Giữ phần ĐÁNG GIÁ của nó — toán quỹ đạo ellipse, cách vẽ Mặt Trời /
   hành tinh / vành Sao Thổ / Mặt Trăng, nền sao, hit-test theo bán kính, xử lý DPR —
   và bỏ phần vỏ: sidebar, bảng thông tin, danh sách hành tinh, play/pause/tốc độ.

   ⚠️ VÌ SAO PORT CHỨ KHÔNG NHÚNG `<iframe>` file gốc:
      · File đó là một TRANG độc lập (có `<html>`, CSS riêng, sidebar riêng) và đang
        nằm trong `img/` — thư mục ảnh.
      · Nhúng iframe là hai bộ CSS, hai vòng `requestAnimationFrame`, không đọc được
        `js/planets.js`, không đổi ngôn ngữ theo trang cha, và mỗi cú chạm phải đi qua
        `postMessage` mới ra được ngoài. Đắt hơn port, và sinh nợ.

   NĂM CHỖ ĐÃ SỬA SO VỚI BẢN GỐC — mỗi chỗ là một luật của dự án:

   ① TÊN LẤY TỪ `js/planets.js`, không gõ cứng tiếng Anh. Bản gốc ghi `name:"Mercury"`
      rồi `fillText` thẳng lên canvas. May là nó vẽ bằng `fillText` chứ không nướng
      chữ vào ảnh — nên song ngữ chỉ là đổi một biến. (Đây đúng là thứ một tấm ảnh
      stock có sẵn chữ KHÔNG làm được.)
   ② MÀU cũng lấy từ `js/planets.js`. Bản gốc tự khai màu riêng (Trái Đất `#3d84f7`
      trong khi dự án dùng `#2f74d6`) — để nguyên là dự án có NGUỒN THỨ BA khai hành
      tinh, sau `js/planets.js` và `explorer.html`. Chỉ giữ lại `radius`/
      `orbitFraction`/`ellipseRatio`/`angle`: đó là BỐ CỤC của riêng bản đồ này.
   ③ BỎ HẾT `fact` tiếng Anh. Bảng thông tin nay là bảng NHIỆM VỤ; nội dung khoa học
      đã có chỗ của nó (`explorer.html`, sổ tay thuật ngữ), đừng sinh bản thứ hai
      không dẫn nguồn.
   ④ MẶC ĐỊNH ĐỨNG YÊN. Đây là một cái MENU, không phải đồ chơi — bắt trẻ chạm vào
      một hành tinh đang bay là làm khó nó ở đúng chỗ nó chỉ muốn chọn. Có nút bật
      chuyển động cho ai muốn xem. `prefers-reduced-motion` thì khoá luôn nút đó.
      (Dự án đã trả giá vì mục tiêu di chuyển: một phép kiểm chập chờn do Sao Hoả bay
      ra ngoài khung, phải đổi sang "hỏi trang xem cái nào đang bấm được".)
   ⑤ BA TRẠNG THÁI vẽ bằng `globalAlpha` + vòng sáng. ⛔ KHÔNG dùng grayscale — bài
      học đã ghi ba lần: trên nền sáng nó cho ra khối xám SÁNG HƠN, tức hút mắt vào
      đúng cái không dùng được.

   Dữ liệu tiến độ ở bản mẫu này là GIẢ. Trang thật đọc `GET /me/missions`.
   ========================================================== */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  /* ───────── BỐ CỤC (giữ từ bản gốc) ─────────
     `orbitFraction` là phần của bán kính lớn nhất, nên bản đồ tự vừa mọi cỡ khung.
     ⚠️ Đây KHÔNG phải khoảng cách thật — bản gốc cũng ghi rõ điều đó. Bản đồ này để
        điều hướng, đừng để bước nào dạy tỉ lệ dựa trên nó. */
  var LAYOUT = {
    mercury:{ r:5,  of:0.13, er:0.82, a:0.3,  sp:0.0240 },
    venus:  { r:8,  of:0.19, er:0.85, a:2.1,  sp:0.0180 },
    earth:  { r:9,  of:0.26, er:0.88, a:4.0,  sp:0.0140, moon:true },
    mars:   { r:7,  of:0.33, er:0.86, a:5.4,  sp:0.0110 },
    jupiter:{ r:20, of:0.45, er:0.90, a:1.1,  sp:0.0060 },
    saturn: { r:17, of:0.57, er:0.90, a:3.3,  sp:0.0045, rings:true },
    uranus: { r:13, of:0.69, er:0.92, a:5.9,  sp:0.0030 },
    neptune:{ r:13, of:0.81, er:0.93, a:0.8,  sp:0.0024 }
  };

  /* Mặt Trăng: vệ tinh của Trái Đất. Khai riêng vì `js/planets.js` có ĐÚNG 8 hành
     tinh — trang thật sẽ phải tách world-id khỏi planet-id, vì trường `Planet` của
     nhiệm vụ đang dùng để ghi "đã ghé hành tinh nào" cho hồ sơ và huy hiệu. */
  var MOON = { id:"moon", vi:"Mặt Trăng", en:"Moon", c:"#e6e2d8", c2:"#74706a",
               r:3.4, dist:22, er:0.6, a:0, sp:0.09 };

  var LANG = "vi";
  var bodies = [];            // {id, nm, c, c2, layout, angle, x, y, rr, state}
  var doneCount = 0;          // chặng đã xong ở Trái Đất — 0 · 5 · 7
  var playing = false;        // ④ mặc định ĐỨNG YÊN
  var picked = null;
  var stars = [];
  var W = 0, H = 0, raf = 0;

  var reduced = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var canvas = $("sky");
  var ctx = canvas.getContext("2d");

  /* ───────── Trạng thái ─────────
     open — có nhiệm vụ, chơi được   ·  soon — tới được, nhiệm vụ chưa tồn tại
     lock — chưa có nhiệm vụ nào ở đây
     ⚠️ `lock` ở ĐÂY khác cổng của `js/route-gate.js`: cổng kia khoá ĐIỂM ĐẾN nên
        mặc định TẮT (bật vĩnh viễn là khoá chết 7 mẫu vật + 2 huy hiệu). Ở đây chỉ
        khoá VIỆC CHƠI NHIỆM VỤ — không phần thưởng nào phụ thuộc. Đừng chung một cờ. */
  function stateOf(id) {
    if (id === "earth") return "open";
    if (id === "moon")  return doneCount >= 5 ? "soon" : "lock";
    return "lock";
  }

  /* ───────── Dựng danh sách thiên thể ───────── */
  function build() {
    bodies = [];
    window.AstroQPlanets.all().forEach(function (p) {
      var L = LAYOUT[p.id];
      if (!L) return;
      bodies.push({ id:p.id, vi:p.vi, en:p.en, c:p.c, c2:p.c2, L:L, angle:L.a });
    });
    /* ⚠️ Mặt Trăng xuất phát ở phía XA MẶT TRỜI so với Trái Đất (cùng hướng với
       Trái Đất nhìn từ tâm). Không phải để đẹp: đặt nó ở góc 0 (bên phải Trái Đất)
       thì trên màn 390px nó rơi cách Sao Hoả **16px** — hai đích chạm dính vào nhau.
       Phía ngoài luôn là phía rộng chỗ nhất. Lấy thẳng góc của Trái Đất để hai con
       số không bao giờ lệch nhau. */
    bodies.push({ id:"moon", vi:MOON.vi, en:MOON.en, c:MOON.c, c2:MOON.c2,
                  L:{ r:MOON.r }, angle:LAYOUT.earth.a, isMoon:true });
  }
  function nameOf(b) { return LANG === "en" ? b.en : b.vi; }
  function get(id) { for (var i=0;i<bodies.length;i++) if (bodies[i].id===id) return bodies[i]; }

  /* ───────── Khung vẽ ───────── */
  function resize() {
    var box = canvas.parentElement.getBoundingClientRect();
    var dpr = window.devicePixelRatio || 1;
    W = box.width; H = box.height;
    canvas.width  = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    makeStars();
    draw();
  }
  function makeStars() {
    stars = [];
    var n = Math.floor(W * H / 2200);
    for (var i = 0; i < n; i++) {
      stars.push({ x:Math.random()*W, y:Math.random()*H, r:Math.random()*1.3+0.2,
                   ph:Math.random()*Math.PI*2, sp:0.01+Math.random()*0.02 });
    }
  }

  /* ⚠️ BÁN KÍNH QUỸ ĐẠO TÍNH RIÊNG THEO HAI TRỤC. Bản gốc dùng `min(W,H)` cho cả hai
     vì nó chạy toàn màn hình (gần vuông). Đặt vào một khối `.panel` rộng hơn cao thì
     `min` = chiều CAO, nên cả hệ co lại thành một cụm nhỏ giữa khung: đo trên ảnh
     chụp, Sao Thuỷ chỉ cách tâm 40px trong khi riêng đĩa Mặt Trời đã 31px — nhãn
     "Sao Thuỷ" và "Sao Kim" bị chính Mặt Trời nuốt. Tách hai trục thì hệ trải hết bề
     ngang và các hành tinh trong giãn ra. */
  function rx()    { return W * 0.44; }
  function ry()    { return H * 0.44; }
  function sunR()  { return Math.max(18, Math.min(W, H) * 0.038); }
  /* Đĩa to dần theo khung để trên màn nhỏ vẫn chạm được; mốc chạm của dự án là 48px
     nên bán kính vẽ nhỏ vẫn phải có vùng chạm rộng (xem `hitR`). */
  function sizeK() { return Math.max(0.75, Math.min(W, H) / 620); }

  /* ⚠️ MẶT TRĂNG PHẢI ĐỦ XA TRÁI ĐẤT ĐỂ CÒN CHẠM ĐƯỢC — đo được, không phải thẩm mỹ.
     Trên 390×844 thì `sizeK()` ≈ 0,49 nên khoảng cách gốc (22 đơn vị) co còn ~11px,
     trong khi vùng chạm tối thiểu là 24px bán kính: ngón tay nhắm vào Mặt Trăng sẽ
     rơi vào Trái Đất. Nên đặt SÀN 34px. Bản đồ này vốn đã không theo tỉ lệ thật —
     chính file gốc cũng ghi rõ — nên nới khoảng cách không nói sai điều gì. */
  function moonDist() { return Math.max(MOON.dist * sizeK(), 34); }

  function posOf(b) {
    if (b.isMoon) {
      var e = get("earth"), ep = posOf(e), d = moonDist();
      return { x: ep.x + Math.cos(b.angle) * d,
               y: ep.y + Math.sin(b.angle) * d * MOON.er };
    }
    var a = b.L.of * rx(), bb = b.L.of * ry() * b.L.er;
    return { x: W/2 + Math.cos(b.angle) * a, y: H/2 + Math.sin(b.angle) * bb, a:a, b:bb };
  }

  /* ───────── Vẽ ───────── */
  var t0 = 0;
  function draw(time) {
    t0 = time || t0;
    ctx.clearRect(0, 0, W, H);
    bg(t0 * 0.001);
    bodies.forEach(function (b) { if (!b.isMoon) orbit(b); });
    sun();
    bodies.forEach(function (b) { if (!b.isMoon) planet(b); });
    planet(get("moon"));
  }

  function bg(tt) {
    var g = ctx.createRadialGradient(W/2, H/2, 0, W/2, H/2, Math.max(W,H)*0.7);
    g.addColorStop(0, "#141d45"); g.addColorStop(.5, "#0a1030"); g.addColorStop(1, "#050818");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.save();
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      /* Sao chỉ nhấp nháy khi đang cho chuyển động — nền động sau lưng một cái menu
         đứng yên là thứ gây rối mắt mà không nói thêm điều gì. */
      ctx.globalAlpha = playing ? 0.55 + 0.45 * Math.sin(tt * s.sp + s.ph) : 0.7;
      ctx.fillStyle = "#fff";
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2); ctx.fill();
    }
    ctx.restore();
  }

  function orbit(b) {
    var p = posOf(b), on = stateOf(b.id) === "open";
    ctx.save();
    ctx.strokeStyle = on ? "rgba(56,189,248,.42)" : "rgba(146,180,255,.16)";
    ctx.lineWidth = 1; ctx.setLineDash(on ? [] : [2, 5]);
    ctx.beginPath(); ctx.ellipse(W/2, H/2, p.a, p.b, 0, 0, Math.PI*2); ctx.stroke();
    ctx.restore();
  }

  function sun() {
    var cx = W/2, cy = H/2, R = sunR();
    var glow = ctx.createRadialGradient(cx, cy, R*0.3, cx, cy, R*3.2);
    glow.addColorStop(0, "rgba(255,207,107,.5)"); glow.addColorStop(1, "rgba(255,207,107,0)");
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(cx, cy, R*3.2, 0, Math.PI*2); ctx.fill();

    var g = ctx.createRadialGradient(cx-R*.3, cy-R*.3, R*.1, cx, cy, R);
    g.addColorStop(0, "#fff6d0"); g.addColorStop(.5, "#ffd93d"); g.addColorStop(1, "#f59e0b");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI*2); ctx.fill();

    label(LANG === "en" ? "Sun" : "Mặt Trời", cx, cy + R + 15, "rgba(233,241,255,.72)", 1);
  }

  function planet(b) {
    var p = posOf(b), st = stateOf(b.id), L = b.L;
    var R = L.r * sizeK();
    b.x = p.x; b.y = p.y; b.rr = R;

    ctx.save();
    if (st === "lock") ctx.globalAlpha = 0.34;      // ⑤ mờ bằng alpha, KHÔNG grayscale

    if (L.rings) rings(p.x, p.y, R, false);

    if (st === "open") {                            // vòng sáng "có nhiệm vụ"
      var ha = ctx.createRadialGradient(p.x, p.y, R, p.x, p.y, R*2.6);
      ha.addColorStop(0, "rgba(56,189,248,.5)"); ha.addColorStop(1, "rgba(56,189,248,0)");
      ctx.fillStyle = ha; ctx.beginPath(); ctx.arc(p.x, p.y, R*2.6, 0, Math.PI*2); ctx.fill();
    } else if (st === "soon") {
      ctx.strokeStyle = "rgba(251,146,60,.75)"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(p.x, p.y, R + 5, 0, Math.PI*2); ctx.stroke();
    }

    var g = ctx.createRadialGradient(p.x-R*.35, p.y-R*.35, R*.15, p.x, p.y, R);
    g.addColorStop(0, b.c); g.addColorStop(1, b.c2);
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, R, 0, Math.PI*2); ctx.fill();

    if (L.rings) rings(p.x, p.y, R, true);
    ctx.restore();

    /* Nhãn: trên màn hẹp chỉ ghi tên nơi BẤM ĐƯỢC — đo được ở bản trước, chín nhãn
       trong khung ~330px thì chắc chắn đè nhau, và thu nhỏ chữ không cứu được.
       ⚠️ Nhãn Mặt Trăng đặt DƯỚI đĩa, mọi nhãn khác đặt TRÊN: Mặt Trăng chỉ cách
          Trái Đất 34px nên hai nhãn cùng nằm trên là chồng chữ lên nhau (thấy trên
          ảnh chụp: "Mặt Trăng" đè "Trái Đất"). */
    b.lb = null;
    var narrow = W < 420;
    if (narrow && st === "lock") return;

    /* ⚠️ NHÃN TRÁI ĐẤT ĐẶT XUỐNG DƯỚI, NHÃN MẶT TRĂNG LÊN TRÊN — hai nhãn đẩy về hai
       phía ngược nhau. Mặt Trăng chỉ cách Trái Đất 34px, mà một khối nhãn cao ~26px:
       để cả hai cùng phía (hay cùng đặt sang bên) thì chúng đè nhau, đã đo đủ ba cách
       trước khi chốt cách này. Đây cũng là lý do luật viết theo "có vệ tinh hay
       không" chứ không gán cứng cho Trái Đất — hành tinh nào có vệ tinh cũng đúng.
       ⚠️ Chỉ đúng khi bản đồ ĐỨNG YÊN (mặc định). Bật chuyển động thì Mặt Trăng quay
          quanh Trái Đất và có lúc rơi xuống dưới; lúc đó hai nhãn có thể chạm nhau
          trong chốc lát — chấp nhận được vì đó là chế độ người dùng tự bật. */
    var down = !!(b.L && b.L.moon);
    var lx = p.x;
    var ly = down ? p.y + R + 20 : p.y - R - 9;
    var al = "center";
    var nm = nameOf(b);

    label(nm, lx, ly,
          st === "open" ? "#fff" : st === "soon" ? "#ffd9ae" : "rgba(233,241,255,.62)",
          st === "lock" ? 0.34 : 1, 0, al);
    if (!narrow) {
      label(st === "open" ? "CÓ NHIỆM VỤ" : st === "soon" ? "SẮP RA MẮT" : "CHƯA CÓ",
            lx, ly + 12,
            st === "open" ? "#38bdf8" : st === "soon" ? "#fb923c" : "rgba(127,141,196,.9)",
            st === "lock" ? 0.34 : 1, 9, al);
    }
    /* Ghi lại khung chữ để phép kiểm hỏi được "có nhãn nào đè nhãn nào không" —
       canvas không có DOM để đo. */
    ctx.save();
    ctx.font = 'bold 12px "Space Grotesk", sans-serif';
    var w = ctx.measureText(nm).width;
    ctx.restore();
    b.lb = { x: lx - w/2, y: ly - 11, w: w, h: narrow ? 14 : 26 };
  }

  function rings(x, y, R, front) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.35); ctx.scale(1, 0.38);
    var cols = ["#d9c290", "#c9ae77", "#e8dcb8", "#b89f68"];
    var inner = R * 1.4, outer = R * 2.3;
    for (var i = 0; i < cols.length; i++) {
      var r = inner + (outer - inner) * (i / (cols.length - 1));
      ctx.beginPath();
      ctx.arc(0, 0, r, front ? 0 : Math.PI, front ? Math.PI : Math.PI*2);
      ctx.strokeStyle = cols[i];
      ctx.lineWidth = (outer - inner) / cols.length + 1.2;
      ctx.stroke();
    }
    ctx.restore();
  }

  function label(txt, x, y, color, alpha, size, align) {
    ctx.save();
    ctx.globalAlpha = alpha == null ? 1 : alpha;
    ctx.fillStyle = color;
    ctx.font = (size ? "" : "bold ") + (size || 12) + "px " +
               (size ? '"Share Tech Mono", monospace' : '"Space Grotesk", sans-serif');
    ctx.textAlign = align || "center";
    ctx.shadowColor = "rgba(0,0,0,.92)"; ctx.shadowBlur = 4;
    ctx.fillText(txt, x, y);
    ctx.restore();
  }

  /* ───────── Vòng chạy ─────────
     Dừng hẳn khi tab bị ẩn: một vòng rAF chạy nền trên MỘT CÁI MENU là tiêu pin của
     máy tính bảng mà không ai nhìn. */
  function loop(time) {
    if (playing) {
      bodies.forEach(function (b) {
        b.angle += (b.isMoon ? MOON.sp : b.L.sp) * 0.6;
      });
    }
    draw(time);
    raf = requestAnimationFrame(loop);
  }
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { cancelAnimationFrame(raf); raf = 0; }
    else if (!raf) raf = requestAnimationFrame(loop);
  });

  /* ───────── Chạm ─────────
     Vùng chạm phải rộng hơn đĩa: Sao Thuỷ vẽ ra chỉ ~7px, mà mốc của dự án là 48px.
     Bản gốc đệm cứng 8px — không đủ cho ngón tay trẻ. */
  function hitR(b) { return Math.max(b.rr + 10, 24); }

  function pick(mx, my) {
    var best = null, bd = Infinity;
    for (var i = 0; i < bodies.length; i++) {
      var b = bodies[i];
      if (b.x === undefined) continue;
      var d = Math.hypot(mx - b.x, my - b.y);
      if (d <= hitR(b) && d < bd) { bd = d; best = b; }
    }
    return best;
  }

  canvas.addEventListener("click", function (e) {
    var r = canvas.getBoundingClientRect();
    var b = pick(e.clientX - r.left, e.clientY - r.top);
    if (b) openSheet(b.id);        // ← thay `openInfoPanel` của bản gốc
  });
  canvas.addEventListener("mousemove", function (e) {
    var r = canvas.getBoundingClientRect();
    canvas.style.cursor = pick(e.clientX - r.left, e.clientY - r.top) ? "pointer" : "default";
  });

  /* ───────── Bảng nhiệm vụ (thay bảng thông tin của bản gốc) ───────── */
  function openSheet(id) {
    picked = id;
    var b = get(id), st = stateOf(id);
    $("sh-orb").style.background =
      "radial-gradient(circle at 36% 30%, " + b.c + ", " + b.c2 + " 78%)";
    $("sh-tag").textContent = st === "open" ? "CÓ NHIỆM VỤ"
                            : st === "soon" ? "SẮP RA MẮT" : "CHƯA CÓ NHIỆM VỤ";
    $("sh-h").textContent = nameOf(b);

    if (st === "open") {
      $("sh-p").textContent = "Nhiệm vụ 01 “Hành Tinh Xanh” — 7 chặng. "
        + (doneCount === 0 ? "Bạn chưa bắt đầu."
           : doneCount === 7 ? "Bạn đã đi hết cả bảy chặng."
           : "Bạn đang ở chặng 0" + (doneCount + 1) + ".");
      note(""); btn("Xem cây nhiệm vụ", true);
    } else if (st === "soon") {
      $("sh-p").textContent = "Bạn đã mở được điểm đến này. Nhiệm vụ Mặt Trăng đang "
        + "được làm — chưa chơi được.";
      note("Đây là lời nói thật, không phải lời hứa: nhiệm vụ này chưa tồn tại.");
      btn("Nhiệm vụ đang được làm", false);
    } else if (id === "moon") {
      $("sh-p").textContent = "Xong 5 trong 7 chặng ở Trái Đất là mở được điểm đến Mặt Trăng.";
      note(""); btn("Chưa mở", false);
    } else {
      /* Nói THẬT: 6 hành tinh này chưa có nhiệm vụ, và cũng KHÔNG bị cấm tới — Bản Đồ
         Thiên Hà vẫn bay tới được. Viết "chưa mở khoá" ở đây là nói sai. */
      $("sh-p").textContent = "Chưa có nhiệm vụ nào ở đây. Nhưng bạn vẫn ghé thăm và "
        + "đọc bảng thông tin của nơi này trên Bản Đồ Thiên Hà.";
      note("Chưa có nhiệm vụ ở đây không có nghĩa là bị cấm tới — hai chuyện khác nhau.");
      btn("Mở Bản Đồ Thiên Hà", true);
    }
    $("sheet").hidden = false;
  }
  function note(t) { var e = $("sh-note"); e.textContent = t; e.hidden = !t; }
  function btn(l, on) { var b = $("sh-go"); b.textContent = l; b.disabled = !on; }

  /* ───────── Lối tắt "đang dở" ───────── */
  var STEP_NM = ["Bề mặt hành tinh xanh", "Lần theo dòng thời gian",
                 "Mặt Trời và ba vùng khí hậu", "Sự sống ở khắp nơi",
                 "Kích hoạt năng lượng sạch", "Eco-Hero: nên hay không nên?",
                 "Đóng dấu Hồ Sơ Trái Đất"];
  function paintSide() {
    var on = doneCount > 0 && doneCount < 7;
    $("resume").hidden = !on;
    if (on) {
      $("r-nm").textContent = STEP_NM[doneCount];
      $("r-sub").textContent = "Trái Đất · chặng 0" + (doneCount + 1) + " / 07";
    }
    var tt = [0, 0, 20, 20, 20, 25, 30, 20], sum = 0;
    for (var i = 1; i <= doneCount; i++) sum += tt[i];
    if (doneCount === 7) sum += 100;
    $("bal").textContent = sum;
  }

  /* ───────── Sự kiện ───────── */
  $("sh-x").addEventListener("click", function () { $("sheet").hidden = true; });
  $("sheet").addEventListener("click", function (e) {
    if (e.target === $("sheet")) $("sheet").hidden = true;
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !$("sheet").hidden) $("sheet").hidden = true;
  });
  $("sh-go").addEventListener("click", function () {
    if (picked === "earth") { location.href = "proto-mission-tree.html?done=" + doneCount; return; }
    $("sheet").hidden = true;
  });

  $("play").addEventListener("click", function () {
    playing = !playing;
    this.textContent = playing ? "⏸ Dừng chuyển động" : "▶ Cho hành tinh chuyển động";
    this.setAttribute("aria-pressed", playing ? "true" : "false");
  });

  $("seg").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("on", x === b);
    });
    doneCount = parseInt(b.dataset.case, 10);
    $("sheet").hidden = true;
    paintSide(); draw();
  });

  $("lang").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("active", x === b);
    });
    LANG = b.dataset.lang;
    draw();
  });

  /* ⚠️ `prefers-reduced-motion`: khoá hẳn nút chuyển động. Một cái nút bấm vào không
     có gì xảy ra còn tệ hơn không có nút. */
  if (reduced) {
    $("play").disabled = true;
    $("play").textContent = "Chuyển động đã tắt theo cài đặt máy";
  }

  /* Bề mặt điều khiển cho phép kiểm — canvas không có DOM để hỏi, nên phải mở ra
     đúng thứ cần đo. Cùng khuôn `window.__mission` của trang nhiệm vụ. */
  window.__map = {
    get bodies() {
      return bodies.map(function (b) {
        return { id:b.id, x:b.x, y:b.y, r:b.rr, hit:hitR(b), lb:b.lb,
                 nm:nameOf(b), state:stateOf(b.id) };
      });
    },
    get playing() { return playing; },
    click: function (id) { openSheet(id); return true; }
  };

  build();
  resize();
  paintSide();
  window.addEventListener("resize", resize);
  raf = requestAnimationFrame(loop);
})();
