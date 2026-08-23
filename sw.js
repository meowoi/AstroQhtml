/* SINH RA bởi `python scratchpad/gen_sw.py` — ĐỪNG SỬA TAY, lần sinh sau mất.
   Lý do tồn tại + 4 quyết định thiết kế: xem khối chú thích ở đầu gen_sw.py.

   ⚠️ MẠNG-TRƯỚC CHO MỌI THỨ. Cache chỉ là đường lùi khi host hỏng. File này
      KHÔNG làm app nhanh hơn — nó làm app không vỡ khi GitHub trả 5xx.
   ⚠️ Xoá file này khỏi repo = trình duyệt tự gỡ đăng ký (công tắc tắt). */
var VERSION = "2026.08.23.7";
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
