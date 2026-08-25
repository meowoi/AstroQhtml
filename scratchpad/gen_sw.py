# -*- coding: utf-8 -*-
r"""gen_sw.py — SINH `sw.js`. ĐỪNG SỬA TAY `sw.js`, lần sinh sau mất.

    python scratchpad/gen_sw.py

⚠️⚠️ VÌ SAO CÓ SERVICE WORKER — CÓ MỘT LỖI THẬT ĐỨNG SAU, KHÔNG PHẢI "LÀM PWA
   CHO ĐẸP". Ngày 23/08/2026 chủ dự án bấm vào thẻ *"Bản đồ Hệ Mặt Trời · Chọn
   một nơi để tới"* và nhận **trang lỗi 5xx của chính GitHub** (con kỳ lân
   *"The Unicorns have taken over"*) ở `astroq.org/mission-map.html`. Đo lại:
   file có thật, trả 200, 12/12 lượt sạch; GitHub Status không khai sự cố nào.
   Nó rơi đúng cửa sổ GitHub Pages tráo bản dựng sau cú push lúc 16:45 (ảnh
   chụp lúc 16:54). Dự án đã có tiền lệ ghi ở CLAUDE.md: 06/08/2026 hai lượt
   deploy Pages **hết giờ ở bước "Deploy to GitHub Pages" (611s và 610s)**.
   ⇒ Không sửa được từ mã của mình. Thứ chặn được là một lớp đệm ở trình duyệt.

⚠️ VÀ TRANG LỖI RIÊNG (404.html) KHÔNG CHỮA ĐƯỢC CA NÀY: Pages chỉ dùng
   `404.html` cho lỗi 404; lỗi 5xx do **biên của GitHub** trả TRƯỚC khi tới nội
   dung của mình, nên không chen được một trang của astroQ vào đó. Service
   worker thì nằm TRONG trình duyệt, tức đứng trước cả biên đó.

═════════════ NĂM QUYẾT ĐỊNH, MỖI CÁI CHỐNG MỘT RỦI RO THẬT ═════════════

① MẠNG-TRƯỚC CHO MỌI THỨ, cache CHỈ là đường lùi.
   Cache-first nhanh hơn, nhưng nó chính là cách ghim một bản cũ — và dự án ĐÃ
   trả giá cho chuyện phiên bản đứng yên (06/08/2026 bản thật đứng ở bản cũ gần
   một ngày). Nặng hơn: HTML mới + JS cũ trong cùng một lượt là **lệch phiên
   bản**, đúng lớp lỗi vừa mất một giờ hôm nay (`dashboard.html` gọi `P.hud()`
   trong khi `js/progress.js` trên origin chưa có `hud`). ⇒ Service worker này
   **không bao giờ làm app nhanh hơn**; nó chỉ làm app KHÔNG VỠ khi host hỏng.
   ⛔ Đừng "tối ưu" nó thành cache-first.

② 5xx PHẢI BỊ COI LÀ HỎNG, không chỉ bắt `catch`.
   GitHub trả **503 kèm HTML con kỳ lân** — đó là một phản hồi THÀNH CÔNG ở
   tầng mạng. Chỉ bọc `try/catch` là service worker trả nguyên con kỳ lân cho
   trẻ. Nên phải xét `status >= 500`. ⚠️ Và **404 thì KHÔNG lùi về cache** —
   một trang đã bị xoá thì phải 404 thật, không thì trang chết sống mãi trong
   cache của trẻ.

③ PRECACHE CHỈ CÁI VỎ, không precache cả app.
   Đo 23/08/2026: 37 trang HTML = 1.586 KB, cộng `css/` 670 KB + `js/` 1.002 KB
   là **3,26 MB** — mà `stamp_version.py` chạy trước MỖI lần push nên tên cache
   đổi theo, tức tải lại toàn bộ mỗi lần push. Đi ngược mọi đợt cắt byte của dự
   án (font 621→101 KB · ảnh 72 MB→2,79 MB · chia bank vì 43 KB).
   ⚠️ Luật "precache trang dưới 40 KB" đã thử rồi BÁC: nó loại đúng
   `dashboard.html` (102 KB), tức loại chính cái hub trẻ quay về.
   ⇒ Precache cái vỏ (~155 KB), còn lại **cache lúc chạy**: trang nào trẻ ghé
   qua thì có đủ HTML + CSS + JS trong cache. Trang CHƯA ghé thì hiện
   `offline.html`. Đó là giới hạn thật và nó vẫn hơn con kỳ lân.

④ TÊN CACHE = SỐ HIỆU BẢN DỰNG, và `activate` XOÁ MỌI CACHE KHÁC.
   Đây là thứ giữ cho cache không phình và không ghim bản cũ. `skipWaiting` +
   `clients.claim()` để bản mới nắm quyền NGAY — an toàn vì đã mạng-trước.

⑤ CACHE-TRƯỚC CHỈ CHO ĐƯỜNG **BẤT BIẾN** (`fonts/` · `vendor/<gói>/<phiên-bản>/`).
   ⚠️⚠️ ĐÂY KHÔNG PHẢI NỚI QUYẾT ĐỊNH ①. ① cấm cache-first vì **lệch phiên bản**:
   HTML mới + JS cũ trong cùng một lượt. Lập luận đó chỉ đúng với URL **không có
   dấu vân tay** — `css/*.css`, `js/*.js`, `*.html`: tên đứng yên, nội dung đổi.
   Hai đường dưới đây không thuộc loại đó, và lý do là CẤU TRÚC chứ không phải
   "chắc là ổn":
     · `vendor/three/0.160.0/…` · `vendor/firebase/12.16.0/…` — **phiên bản NẰM
       TRONG đường dẫn**, nên bản mới là URL mới. Lệch phiên bản không dựng nổi.
     · `fonts/*.woff2` — nằm trong `SHELL`, tức được `fetch(u,{cache:"reload"})`
       lại ở MỖI lần `install`; mà `stamp_version.py` chạy trước MỖI lần push nên
       tên cache đổi ⇒ `activate` xoá sạch cache của bản dựng cũ. Bản trong cache
       LUÔN là bản của bản dựng đang chạy.

   SỐ ĐO ĐỨNG SAU (24/08/2026 — `scratchpad/perf_audit_all.py`, `_font_chain.py`,
   và header thật của astroq.org, không phải suy đoán):
     · GitHub Pages trả `Cache-Control: max-age=600` cho MỌI file. Sau 10 phút là
       tải lại từ đầu — kể cả 655 KB three.js và 100 KB font.
     · Hai đường này cộng lại **326 KB gzip** (`vendor/` 226 KB + `fonts/` 100 KB).
     · Trên 4G RTT 150ms + CPU ×4, `fonts/` ở `dashboard.html` bắt đầu tải ở
       **3.475 ms** và xong ở **4.783 ms**, trong khi FCP là **3.728 ms** — tức
       chữ Việt vẽ lại HƠN MỘT GIÂY sau lần vẽ đầu, mỗi lượt vào.

   ⛔ ĐỪNG thêm `css/`, `js/` hay `*.html` vào `FAST`. Đó ĐÚNG là chỗ ① nói tới,
      và nó đã tốn của dự án một giờ ngày 23/08 (`dashboard.html` gọi `P.hud()`
      trong khi `js/progress.js` trên origin chưa có `hud`).
   ⛔ ĐỪNG rút gọn mẫu `vendor` thành `/^\/vendor\//`. Hai segment `[^\/]+` ở giữa
      là thứ ĐÒI phải có số phiên bản trong đường dẫn; bỏ chúng đi là cấp
      cache-trước cho cả `vendor/foo.js` — một đường KHÔNG bất biến, tức tự tay
      dựng lại đúng cái bẫy ① cấm.

⚠️ CÔNG TẮC TẮT: xoá `sw.js` khỏi repo. Trình duyệt gặp 404 ở script service
   worker lúc kiểm cập nhật thì **tự gỡ đăng ký**. Không cần deploy gì thêm.
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Cái VỎ: đủ để `offline.html` tự dựng được mà không cần mạng ──────────────
# ⚠️ Giữ danh sách này NGẮN. Thêm một file vào đây là thêm byte cho MỌI trẻ ở
#    MỖI lần đổi bản dựng. Thứ chỉ một trang dùng thì để cache lúc chạy lo.
SHELL = [
    "offline.html",
    "css/common.css",
    "css/fonts.css",
    "css/offline.css",
    "js/ui-common.js",
    "img/astroq-logo.png",
]

TPL = '''/* SINH RA bởi `python scratchpad/gen_sw.py` — ĐỪNG SỬA TAY, lần sinh sau mất.
   Lý do tồn tại + 5 quyết định thiết kế: xem khối chú thích ở đầu gen_sw.py.

   ⚠️ MẠNG-TRƯỚC CHO MỌI THỨ, TRỪ `FAST` (quyết định ⑤). Với mọi đường còn lại
      cache chỉ là đường lùi khi host hỏng, và ở đó file này KHÔNG làm app nhanh
      hơn — nó làm app không vỡ khi GitHub trả 5xx. Riêng `fonts/` và
      `vendor/<gói>/<phiên-bản>/` là cache-trước, vì đường dẫn của chúng BẤT BIẾN
      nên không dựng nổi cảnh lệch phiên bản mà ① cấm. ⛔ Đừng nới `FAST`.
   ⚠️ Xoá file này khỏi repo = trình duyệt tự gỡ đăng ký (công tắc tắt). */
var VERSION = "%(version)s";
var CACHE = "astroq-" + VERSION;
var OFFLINE = "offline.html";
var SHELL = %(shell)s;

/* ⚠️ CACHE-TRƯỚC — CHỈ hai đường BẤT BIẾN này, và lý do là CẤU TRÚC chứ không
   phải "chắc là ổn". Vì sao nó KHÔNG phá quyết định ① (chống lệch phiên bản):
   xem quyết định ⑤ ở đầu `scratchpad/gen_sw.py`.
     · `fonts/` — nằm trong SHELL, `install` tải lại ở mỗi bản dựng.
     · `vendor/<gói>/<phiên-bản>/…` — phiên bản NẰM TRONG đường dẫn.
   ⛔ Đừng thêm `css/`, `js/`, `*.html`: tên đứng yên mà nội dung đổi — đó đúng
      là chỗ ① cấm. ⛔ Đừng bỏ hai segment `[^\\/]+\\/[^\\/]+\\/` của mẫu `vendor`:
      chúng ĐÒI có số phiên bản, không có thì rơi về mạng-trước, và như thế mới
      đúng. */
var FAST = [/^\\/fonts\\//, /^\\/vendor\\/[^\\/]+\\/[^\\/]+\\/.+/];

/* ⚠️ Đường same-origin KHÔNG được cache. Hôm nay API nằm ở origin khác nên
   nhánh này chưa chạy, nhưng ngày ai đó đưa API về sau cùng một tên miền thì
   trả một bản ví CŨ là nói SAI với trẻ về số dư của nó. */
var NEVER = [/^\\/me\\//, /^\\/auth\\//, /^\\/admin\\//, /^\\/visit$/];

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
'''


def read_version():
    p = os.path.join(ROOT, "js", "ui-common.js")
    s = io.open(p, encoding="utf-8", newline="").read()
    m = re.search(r'var\s+VERSION\s*=\s*"([0-9.]+)"', s)
    if not m:
        sys.exit("khong doc duoc VERSION o js/ui-common.js")
    return m.group(1)


def main():
    ver = read_version()

    missing = [u for u in SHELL if not os.path.isfile(os.path.join(ROOT, u))]
    if missing:
        sys.exit("thieu file vo tren dia: %s" % missing)

    total = sum(os.path.getsize(os.path.join(ROOT, u)) for u in SHELL)
    fonts = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "fonts", "*.woff2")))
    if not fonts:
        sys.exit("khong thay font nao trong fonts/ — cai vo se ra chu he thong")
    shell = SHELL + ["fonts/" + f for f in fonts]
    total += sum(os.path.getsize(os.path.join(ROOT, "fonts", f)) for f in fonts)

    # ⚠️ Hang rao: precache phinh len la moi tre tai lai o MOI lan doi ban dung.
    cap = 320 * 1024
    if total > cap:
        sys.exit("cai vo %d KB > tran %d KB — doc lai quyet dinh ③ o gen_sw.py"
                 % (total / 1024, cap / 1024))

    body = TPL % {
        "version": ver,
        "shell": "[\n  " + ",\n  ".join('"%s"' % u for u in shell) + "\n]",
    }
    out = os.path.join(ROOT, "sw.js")
    io.open(out, "w", encoding="utf-8", newline="\n").write(body)

    print("sw.js: ban dung %s | %d file vo | %.0f KB" % (ver, len(shell), total / 1024.0))
    for u in shell:
        print("    %s" % u)


if __name__ == "__main__":
    main()
