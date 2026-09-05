/* SINH RA bởi `python scratchpad/gen_sw.py` — ĐỪNG SỬA TAY, lần sinh sau mất.
   Lý do tồn tại + 5 quyết định thiết kế: xem khối chú thích ở đầu gen_sw.py.

   ⚠️ MẠNG-TRƯỚC CHO MỌI THỨ, TRỪ `FAST` (quyết định ⑤). Với mọi đường còn lại
      cache chỉ là đường lùi khi host hỏng, và ở đó file này KHÔNG làm app nhanh
      hơn — nó làm app không vỡ khi GitHub trả 5xx. Riêng `fonts/` và
      `vendor/<gói>/<phiên-bản>/` là cache-trước, vì đường dẫn của chúng BẤT BIẾN
      nên không dựng nổi cảnh lệch phiên bản mà ① cấm. ⛔ Đừng nới `FAST`.
   ⚠️ Xoá file này khỏi repo = trình duyệt tự gỡ đăng ký (công tắc tắt). */
var VERSION = "2026.09.06.1";
var CACHE = "astroq-" + VERSION;
var OFFLINE = "offline.html";
var SHELL = [
  "offline.html",
  "css/common.css",
  "css/fonts.css",
  "css/offline.css",
  "js/ui-common.js",
  "img/astroq-logo.png",
  "fonts/inter-latin.woff2",
  "fonts/inter-vietnamese.woff2",
  "fonts/share-tech-mono-latin.woff2",
  "fonts/space-grotesk-latin.woff2",
  "fonts/space-grotesk-vietnamese.woff2"
];

/* ⚠️ CACHE-TRƯỚC — CHỈ hai đường BẤT BIẾN này, và lý do là CẤU TRÚC chứ không
   phải "chắc là ổn". Vì sao nó KHÔNG phá quyết định ① (chống lệch phiên bản):
   xem quyết định ⑤ ở đầu `scratchpad/gen_sw.py`.
     · `fonts/` — nằm trong SHELL, `install` tải lại ở mỗi bản dựng.
     · `vendor/<gói>/<phiên-bản>/…` — phiên bản NẰM TRONG đường dẫn.
   ⛔ Đừng thêm `css/`, `js/`, `*.html`: tên đứng yên mà nội dung đổi — đó đúng
      là chỗ ① cấm. ⛔ Đừng bỏ hai segment `[^\/]+\/[^\/]+\/` của mẫu `vendor`:
      chúng ĐÒI có số phiên bản, không có thì rơi về mạng-trước, và như thế mới
      đúng. */
var FAST = [/^\/fonts\//, /^\/vendor\/[^\/]+\/[^\/]+\/.+/];

/* ⚠️ Đường same-origin KHÔNG được cache. Hôm nay API nằm ở origin khác nên
   nhánh này chưa chạy, nhưng ngày ai đó đưa API về sau cùng một tên miền thì
   trả một bản ví CŨ là nói SAI với trẻ về số dư của nó. */
var NEVER = [/^\/me\//, /^\/auth\//, /^\/admin\//, /^\/visit$/];

self.addEventListener("install", function (e) {
  /* ⚠️ KHÔNG dùng cache.addAll: một URL hỏng là addAll từ chối và service
     worker KHÔNG BAO GIỜ activate — tức mất sạch lớp đệm vì một file lẻ. */
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return Promise.all(SHELL.map(function (u) {
        return fetch(u, { cache: "reload" }).then(function (r) {
          if (r && r.ok) return c.put(u, r);
        }).catch(function () { /* thiếu một file vỏ thì vẫn cài tiếp */ });
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (ks) {
      return Promise.all(ks.map(function (k) {
        /* Xoá mọi cache của bản dựng KHÁC — chống phình và chống ghim bản cũ. */
        if (k !== CACHE && k.indexOf("astroq-") === 0) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

function skip(url) {
  for (var i = 0; i < NEVER.length; i++) if (NEVER[i].test(url.pathname)) return true;
  return false;
}

function fast(url) {
  for (var i = 0; i < FAST.length; i++) if (FAST[i].test(url.pathname)) return true;
  return false;
}

/* Cache-trước cho đường bất biến: có trong cache thì trả NGAY (0 vòng mạng),
   hụt thì đi mạng rồi ghi lại.
   ⚠️ KHÔNG dùng `ignoreSearch` ở đây, và đó là chỗ khác `fallback()` một cách
      CỐ Ý. `fallback` bỏ qua query vì `?api=local`/`?onboard=1` là cờ của TRANG,
      không đổi nội dung file. Ở đây thì ngược lại: ngày nào ai đó phá cache một
      file vendor bằng `?v=2` thì query CHÍNH LÀ thứ phải làm hụt cache — bỏ qua
      nó là vô hiệu hoá đúng cú phá cache đó.
   ⚠️ KHÔNG làm mới ngầm phía sau (stale-while-revalidate): thêm một lượt mạng
      cho một URL bất biến là trả lại đúng cái giá vừa đi cắt. Đường bất biến
      không cần làm mới — bản dựng mới là URL mới, hoặc là cache mới. */
function fastFirst(req) {
  return caches.match(req).then(function (hit) {
    if (hit) return hit;
    return fetch(req).then(function (res) {
      if (res && res.status >= 500) return fallback(req, res);
      if (res && res.ok && res.type === "basic") {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) { c.put(req, copy); }).catch(function () {});
      }
      return res;
    }).catch(function () { return fallback(req, null); });
  });
}

function fallback(req, res) {
  /* ignoreSearch: `?api=local`, `?cb=…`, `?onboard=1` không được làm hụt cache. */
  return caches.match(req, { ignoreSearch: true }).then(function (hit) {
    if (hit) return hit;
    if (req.mode === "navigate") {
      return caches.match(OFFLINE).then(function (off) {
        return off || res || Response.error();
      });
    }
    return res || Response.error();
  });
}

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;                       /* POST/PUT: để nguyên */
  var url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== self.location.origin) return;        /* API + Firebase: để nguyên */
  if (skip(url)) return;

  /* ⚠️ SAU `skip()`: đường `/me/` `/auth/` `/admin/` `/visit` không bao giờ được
     cache, và thứ tự này là thứ giữ điều đó đúng kể cả khi `FAST` được nới. */
  if (fast(url)) return e.respondWith(fastFirst(req));      /* quyết định ⑤ */

  e.respondWith(
    fetch(req).then(function (res) {
      /* ⚠️ 5xx là phản hồi THÀNH CÔNG ở tầng mạng — GitHub trả 503 kèm HTML
         con kỳ lân. Không xét status ở đây là trả nguyên con kỳ lân cho trẻ.
         ⚠️ 404 thì KHÔNG lùi cache: trang đã xoá phải 404 thật. */
      if (res && res.status >= 500) return fallback(req, res);
      if (res && res.ok && res.type === "basic") {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) { c.put(req, copy); }).catch(function () {});
      }
      return res;
    }).catch(function () { return fallback(req, null); })
  );
});
