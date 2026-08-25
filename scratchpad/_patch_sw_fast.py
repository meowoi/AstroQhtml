# -*- coding: utf-8 -*-
r"""Vá `scratchpad/gen_sw.py`: thêm quyết định ⑤ (cache-trước cho đường BẤT BIẾN).

⚠️ VIẾT THÀNH FILE, KHÔNG CHẠY QUA HEREDOC — heredoc của shell ăn mất dấu `\`
   trong regex. Bài học đã ghi ở CLAUDE.md và ở đầu stamp_version.py.

Chạy một lần rồi xoá được; giữ lại để đọc lại chính xác đã sửa những gì.
    python scratchpad/_patch_sw_fast.py
"""
import io
import sys

P = "scratchpad/gen_sw.py"
s = io.open(P, encoding="utf-8").read()

if "var FAST" in s:
    sys.exit("gen_sw.py da co FAST — khong va lai")

# ── 1. Quyết định ⑤ trong khối chú thích đầu file ────────────────────────────
DOC_ANCHOR = "⚠️ CÔNG TẮC TẮT: xoá `sw.js` khỏi repo."
DOC_NEW = r"""⑤ CACHE-TRƯỚC CHỈ CHO ĐƯỜNG **BẤT BIẾN** (`fonts/` · `vendor/<gói>/<phiên-bản>/`).
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

⚠️ CÔNG TẮC TẮT: xoá `sw.js` khỏi repo."""
assert DOC_ANCHOR in s, "khong thay cau CONG TAC TAT trong gen_sw.py"
s = s.replace(DOC_ANCHOR, DOC_NEW, 1)

# ── 2. Khai `FAST` trong TPL, ngay sau `SHELL` ───────────────────────────────
# ⚠️ TPL là chuỗi KHÔNG-raw có %-format, nên mỗi `\` mà sw.js cần phải viết `\\`
#    ở đây. Dùng raw-string cho khối vá này để `\\` đúng là hai dấu.
A2 = "var SHELL = %(shell)s;\n"
B2 = r"""var SHELL = %(shell)s;

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
"""
assert A2 in s, "khong thay dong SHELL trong TPL"
s = s.replace(A2, B2, 1)

# ── 3. `fast()` + `fastFirst()` ─────────────────────────────────────────────
A3 = """function skip(url) {
  for (var i = 0; i < NEVER.length; i++) if (NEVER[i].test(url.pathname)) return true;
  return false;
}
"""
B3 = r"""function skip(url) {
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
"""
assert A3 in s, "khong thay skip() trong TPL"
s = s.replace(A3, B3, 1)

# ── 4. Cắm nhánh vào `fetch` — SAU `skip()`, TRƯỚC nhánh mạng-trước ─────────
A4 = """  if (skip(url)) return;

  e.respondWith("""
B4 = """  if (skip(url)) return;

  /* ⚠️ SAU `skip()`: đường `/me/` `/auth/` `/admin/` `/visit` không bao giờ được
     cache, và thứ tự này là thứ giữ điều đó đúng kể cả khi `FAST` được nới. */
  if (fast(url)) return e.respondWith(fastFirst(req));      /* quyết định ⑤ */

  e.respondWith("""
assert A4 in s, "khong thay diem cam nhanh trong fetch listener"
s = s.replace(A4, B4, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("gen_sw.py: da them quyet dinh (5) + FAST + fastFirst()")
