/* ============================================================================
   js/warp-stars-worker.js — VỆT SAO CỦA MÀN WARP, VẼ TRONG WEB WORKER.
   Thêm 03/08/2026. Người gọi duy nhất: `explorer.html` (`startWarp`/`stopWarp`).

   ⚠️⚠️ VÌ SAO PHẢI LÀ WORKER — ĐÂY LÀ SỐ ĐO, KHÔNG PHẢI SỞ THÍCH KIẾN TRÚC.
   Chủ dự án chơi thật và báo: *"sau màn select, chuyển cảnh bay vào hệ mặt trời bị
   giật, tìm hiểu lý do"*. Lý do đo được bằng `PerformanceObserver('longtask')` trên
   chính `explorer.html?onboard=1` (bộ đo: `scratchpad/probe_warp_longtask.py`):

     máy thường  : màn warp sống 2.142 ms · long task chồng lên nó **1.908 ms (89%)**
                   — hai khối liền nhau 788 ms và 765 ms
     CPU chậm x4 : màn warp sống 3.788 ms · long task **3.687 ms (97%)**
                   — MỘT khối duy nhất dài **2.879 ms**

   Nghĩa là: trong lúc màn warp đang chạy, main thread gần như KHÔNG rảnh một nhịp
   nào. Nó đang tải 13 module three.js từ `unpkg.com` rồi dựng cả cảnh Hệ Mặt Trời
   (geometry, texture, biên dịch shader của EffectComposer + UnrealBloomPass). Vòng
   `requestAnimationFrame` của vệt sao xếp hàng SAU những việc đó, nên ở máy chậm nó
   chỉ nhận được **2 khung hình trong 3,8 giây** — trẻ thấy hình đứng cứng rồi giật
   một cái, đúng như báo.

   ⛔ KHÔNG CÓ CÁCH NÀO CHỮA ĐƯỢC TRÊN MAIN THREAD. Vẽ ít sao hơn, gộp lời `stroke`,
      hạ độ phân giải canvas — tất cả đều làm khung vẽ RẺ hơn, nhưng vấn đề không phải
      khung vẽ đắt: nó là **không được chạy**. Một khối 2.879 ms thì dù khung vẽ tốn
      0 ms cũng vẫn đứng 2,9 giây.
   ⛔ VÀ KHÔNG CHỮA BẰNG CÁCH BỎ MÀN WARP hay chờ cảnh 3D xong mới hiện nó: màn warp
      tồn tại ĐÚNG ĐỂ che quãng dựng cảnh đó. Bỏ nó là trẻ ngồi nhìn màn hình trống.

   Nên phần VẼ dời sang worker: worker có luồng riêng, khối 2,9 giây của main thread
   không chạm tới nó. `OffscreenCanvas` cho phép worker vẽ thẳng vào đúng thẻ
   `<canvas>` đang hiện trên trang (`transferControlToOffscreen`).

   ⚠️ CHUYỂN ĐỘNG TÍNH THEO THỜI GIAN THẬT, KHÔNG THEO SỐ KHUNG. Bản trên main thread
      dùng `z -= 14` mỗi khung, tức tốc độ phụ thuộc máy chạy được bao nhiêu FPS. Ở
      worker thì nhịp vẽ có thể là `requestAnimationFrame` (Chrome/Firefox có trong
      dedicated worker) HOẶC `setTimeout` 16 ms ở nơi không có — hai nhịp khác nhau mà
      cùng một hằng số mỗi khung là hai tốc độ khác nhau. Nhân với `dt` thì cả hai ra
      cùng một cảnh. 840 = 14 × 60, tức giữ nguyên đúng tốc độ bản cũ ở 60 FPS.

   ⚠️ GỘP LỜI `stroke` THEO NHÓM ĐỘ SÁNG. Bản cũ gọi `beginPath`+`stroke` cho TỪNG
      ngôi sao: 420 lời vẽ + 420 lần đổi `strokeStyle`/`lineWidth` mỗi khung. Ở đây
      chia 7 nhóm theo độ sáng nên còn 7 lời vẽ. Không phải để chữa cái giật (xem
      trên — không chữa được bằng cách này), mà vì worker cũng phải nhường CPU cho
      chính main thread đang dựng cảnh: khung vẽ rẻ thì nó không góp thêm vào cơn
      tắc.

   Giao thức (main → worker):
     {type:'init',  canvas, w, h}   canvas là OffscreenCanvas, gửi kèm transfer list
     {type:'resize', w, h}
     {type:'start'}                 dựng lại đám sao rồi chạy
     {type:'stop'}                  dừng và xoá sạch canvas
   Worker → main:
     {type:'ready'}                 đã nhận canvas, đang vẽ được — main thread dựa vào
                                    tin này để biết KHÔNG phải lùi về bản vẽ chính nó.
   ============================================================================ */
"use strict";

var cv = null, ctx = null, W = 0, H = 0;
var stars = [], raf = null, running = false, last = 0;

var COUNT = 420;              // giữ nguyên con số của bản cũ — cùng mật độ, cùng cảnh
var SPEED = 840;              // đơn vị z mỗi GIÂY (= 14 mỗi khung × 60 FPS)
var BUCKETS = 7;              // số nhóm độ sáng khi gộp lời vẽ

function newStar(spread) {
  return {
    x: (Math.random() * 2 - 1) * W,
    y: (Math.random() * 2 - 1) * H,
    z: spread ? Math.random() * W : W
  };
}

function makeStars() {
  stars = [];
  for (var i = 0; i < COUNT; i++) stars.push(newStar(true));
}

function frame(now) {
  if (!running || !ctx) return;
  /* Khung đầu tiên chưa có mốc trước → coi như một khung 60 FPS. Không có dòng này
     thì `dt` bằng chính `now` (hàng nghìn ms) và cả đám sao bay vọt qua trong một
     khung. */
  var dt = last ? Math.min((now - last) / 1000, 0.05) : 1 / 60;
  last = now;
  var dz = SPEED * dt;

  // Vệt cũ mờ dần thay vì xoá hẳn — chính lớp mờ này tạo cảm giác vệt sáng kéo dài.
  ctx.fillStyle = "rgba(8,12,30,0.35)";
  ctx.fillRect(0, 0, W, H);

  var cx = W / 2, cy = H / 2;
  var i, b;
  // Một đường gộp cho mỗi nhóm độ sáng — xem lý do ở khối chú thích đầu file.
  var paths = [];
  for (b = 0; b < BUCKETS; b++) paths.push(null);

  for (i = 0; i < stars.length; i++) {
    var s = stars[i];
    s.z -= dz;
    if (s.z < 1) { stars[i] = newStar(false); continue; }
    var k = 128 / s.z, sx = cx + s.x * k, sy = cy + s.y * k;
    var pk = 128 / (s.z + dz), px = cx + s.x * pk, py = cy + s.y * pk;
    var a = Math.min(1, (W - s.z) / W + 0.15);
    b = Math.min(BUCKETS - 1, Math.floor(a * BUCKETS));
    if (!paths[b]) paths[b] = new Path2D();
    paths[b].moveTo(px, py);
    paths[b].lineTo(sx, sy);
  }

  for (b = 0; b < BUCKETS; b++) {
    if (!paths[b]) continue;
    var mid = (b + 0.5) / BUCKETS;                 // độ sáng đại diện của nhóm
    ctx.strokeStyle = "rgba(180,215,255," + mid.toFixed(3) + ")";
    ctx.lineWidth = Math.max(0.6, mid * 2.2);
    ctx.stroke(paths[b]);
  }

  schedule();
}

/* `requestAnimationFrame` CÓ trong dedicated worker ở Chrome/Firefox (mixin
   `AnimationFrameProvider` của HTML spec), nhưng [Chưa kiểm chứng] không phải nơi nào
   cũng có. Thiếu thì lùi về `setTimeout` — chuyển động đã tính theo `dt` nên hai nhịp
   cho ra cùng một tốc độ, chỉ khác độ mượt. */
function schedule() {
  if (!running) return;
  if (typeof requestAnimationFrame === "function") raf = requestAnimationFrame(frame);
  else raf = setTimeout(function () { frame(Date.now()); }, 16);
}

function unschedule() {
  if (raf === null) return;
  if (typeof cancelAnimationFrame === "function") cancelAnimationFrame(raf);
  clearTimeout(raf);
  raf = null;
}

function resize(w, h) {
  W = Math.max(1, w | 0);
  H = Math.max(1, h | 0);
  if (cv) { cv.width = W; cv.height = H; }
}

self.onmessage = function (ev) {
  var m = ev.data || {};
  if (m.type === "init") {
    cv = m.canvas;
    resize(m.w, m.h);
    ctx = cv.getContext("2d");
    self.postMessage({ type: "ready" });
    return;
  }
  if (!cv) return;
  if (m.type === "resize") { resize(m.w, m.h); return; }
  if (m.type === "start") {
    resize(m.w, m.h);
    makeStars();
    last = 0;
    running = true;
    unschedule();
    schedule();
    return;
  }
  if (m.type === "stop") {
    running = false;
    unschedule();
    if (ctx) ctx.clearRect(0, 0, W, H);
  }
};
