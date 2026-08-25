# -*- coding: utf-8 -*-
r"""probe_sw_fast.py — KIỂM quyết định ⑤ của `gen_sw.py`: cache-trước cho
`fonts/` và `vendor/<gói>/<phiên-bản>/`, và CHỈ cho hai đường đó.

    python scratchpad/probe_sw_fast.py

⚠️⚠️ ĐO Ở PHÍA MÁY CHỦ, KHÔNG ĐO Ở PHÍA TRÌNH DUYỆT. `transferSize` và
   `page.on("request")` đều vẫn thấy lượt do service worker trả từ cache, nên đo
   bằng chúng là đo cái mình muốn thấy. Ở đây máy chủ tĩnh tự đếm từng đường dẫn
   nó ĐƯỢC HỎI: 0 lượt hỏ�i = byte thật KHÔNG rời máy chủ. Đó là bằng chứng duy
   nhất không mơ hồ.

⚠️ Lượt 304 VẪN được tính là một lượt hỏi, và đó là CỐ Ý: mục tiêu của ⑤ là bỏ
   hẳn vòng mạng, không phải đổi 200 thành 304. Một vòng RTT 150ms vẫn là 150ms.

BỐN PHÉP KIỂM:
  [1] lượt QUAY LẠI: `fonts/*.woff2` + `vendor/…` = 0 lượt hỏi máy chủ.
      ⚠️ `fonts/` ra 0 lượt NGAY TỪ LƯỢT LÀM NÓNG, và đó không phải lỗi phép đo:
      chúng nằm trong `SHELL` nên `install` đã tải xong trước khi đếm bắt đầu.
      Đúng bằng chứng cho nửa "font" của quyết định ⑤.
  [2] PHẠM VI: `css/*.css` và `js/*.js` VẪN hỏi máy chủ mỗi lượt (mạng-trước) —
      nếu chúng cũng về 0 thì `FAST` đã bị nới quá và quyết định ① bị phá.
  [3] `vendor/khong-phien-ban.js` (2 segment) KHÔNG được cache-trước.
  [4] KHOÁ CACHE TÍNH CẢ QUERY (`fastFirst` cố ý không `ignoreSearch`): một query
      CHƯA TỪNG thấy phải đi mạng thật, dù URL gốc đã nằm trong cache. Kiểm bằng
      lượt thứ BA với `?v=3` — kiểm ở lượt hai thì `?v=2` đã tự vào cache ở lượt
      làm nóng nên phép kiểm sẽ nói ngược lại sự thật.
"""
import collections
import http.server
import io
import os
import socketserver
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PORT = 8132
SITE = "http://localhost:%d" % PORT

HITS = collections.Counter()
COUNTING = {"on": False}

# File mồi cho phép kiểm [3]: `vendor/<file>.js` — CHỈ 2 segment, KHÔNG có
# segment phiên bản, nên mẫu `FAST` phải bỏ qua nó.
BAIT = os.path.join(ROOT, "vendor", "_probe-noversion.js")

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))


class Counting(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if COUNTING["on"]:
            HITS[self.path] += 1
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def hits(pred):
    return sum(n for p, n in HITS.items() if pred(p))


REG = """() => navigator.serviceWorker.ready.then(r => !!r.active)"""

# Trang mồi: nạp đúng những URL cần cho phép kiểm, không phụ thuộc trang thật.
BAIT_PAGE = """<!doctype html><meta charset=utf-8><title>probe</title>
<script>
window.__done = (async () => {
  const urls = %s;
  const out = {};
  for (const u of urls) {
    try { const r = await fetch(u, {cache: 'no-store'}); out[u] = r.status; }
    catch (e) { out[u] = 'loi'; }
  }
  return out;
})();
</script>
"""

URLS = [
    "/fonts/inter-latin.woff2",
    "/fonts/space-grotesk-latin.woff2",
    "/vendor/three/0.160.0/three.module.min.js",
    "/vendor/firebase/12.16.0/firebase-app.js",
    "/css/common.css",
    "/js/ui-common.js",
    "/vendor/_probe-noversion.js",
    "/vendor/three/0.160.0/three.module.min.js?v=2",
]

socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", PORT), Counting)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

io.open(BAIT, "w", encoding="utf-8", newline="\n").write(
    "/* file moi cua scratchpad/probe_sw_fast.py — xoa sau khi chay. */\n")
io.open(os.path.join(ROOT, "_probe_sw.html"), "w", encoding="utf-8",
        newline="\n").write(BAIT_PAGE % repr(URLS).replace("'", '"'))

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        # ⚠️ MỘT context cho cả hai lượt: service worker + cache của nó sống theo
        #    origin TRONG context. Context mới là hai lượt "lần đầu".
        ctx = b.new_context(viewport={"width": 500, "height": 844}, locale="vi-VN")
        pg = ctx.new_page()

        print("=== [0] Đăng ký service worker + chờ activate ===")
        pg.goto(SITE + "/index.html", wait_until="load")
        try:
            act = pg.evaluate(REG)
        except Exception as e:
            act = False
            print("  loi cho SW:", str(e)[:80])
        check("[0] service worker đã activate", bool(act))

        print("\n=== [1] Lượt LÀM NÓNG (mọi URL phải hỏi máy chủ) ===")
        COUNTING["on"] = True
        pg.goto(SITE + "/_probe_sw.html", wait_until="load")
        r1 = pg.evaluate("() => window.__done")
        warm = dict(HITS)
        for u in URLS:
            n = warm.get(u, 0)
            print("     %-50s %d lượt · HTTP %s" % (u, n, r1.get(u)))
        # ⚠️ Font PHẢI ra 0 ngay ở lượt này: `install` (chạy ở bước [0]) đã tải
        #    chúng qua `SHELL` trước khi bộ đếm bật. Nếu ở đây > 0 thì nghĩa là
        #    `fonts/` KHÔNG được precache — nửa "font" của ⑤ mất chỗ dựa.
        check("[1] `fonts/` đã sẵn trong cache ngay từ lượt đầu (nhờ precache)",
              hits(lambda p: p.startswith("/fonts/")) == 0,
              "%d lượt" % hits(lambda p: p.startswith("/fonts/")))
        check("[1] lượt làm nóng: vendor có phiên bản hỏi máy chủ ĐÚNG MỘT LẦN",
              warm.get("/vendor/three/0.160.0/three.module.min.js", 0) == 1,
              "%d lượt" % warm.get("/vendor/three/0.160.0/three.module.min.js", 0))
        # Khoá cache tính cả query: `?v=2` là một khoá KHÁC, nên nó cũng phải đi
        # mạng ở lượt này dù URL gốc vừa được hỏi ngay bên trên.
        check("[4a] `?v=2` là khoá cache RIÊNG (đi mạng ở lượt làm nóng)",
              warm.get("/vendor/three/0.160.0/three.module.min.js?v=2", 0) == 1,
              "%d lượt" % warm.get("/vendor/three/0.160.0/three.module.min.js?v=2", 0))

        print("\n=== [2] Lượt QUAY LẠI (đây là phép đo) ===")
        HITS.clear()
        pg.goto(SITE + "/_probe_sw.html", wait_until="load")
        r2 = pg.evaluate("() => window.__done")
        for u in URLS:
            print("     %-50s %d lượt · HTTP %s" % (u, HITS.get(u, 0), r2.get(u)))

        n_font = hits(lambda p: p.startswith("/fonts/"))
        n_vend = (HITS.get("/vendor/three/0.160.0/three.module.min.js", 0)
                  + HITS.get("/vendor/firebase/12.16.0/firebase-app.js", 0))
        n_css = HITS.get("/css/common.css", 0)
        n_js = HITS.get("/js/ui-common.js", 0)
        n_bait = HITS.get("/vendor/_probe-noversion.js", 0)
        n_q = HITS.get("/vendor/three/0.160.0/three.module.min.js?v=2", 0)

        check("[1] `fonts/` KHÔNG rời máy chủ ở lượt quay lại", n_font == 0,
              "%d lượt" % n_font)
        check("[1] `vendor/<gói>/<phiên-bản>/` KHÔNG rời máy chủ", n_vend == 0,
              "%d lượt" % n_vend)
        check("[1] cả hai vẫn trả 200 cho trang", r2.get(URLS[0]) == 200
              and r2.get(URLS[2]) == 200,
              "font %s · three %s" % (r2.get(URLS[0]), r2.get(URLS[2])))

        # ⚠️ Phép kiểm QUAN TRỌNG NHẤT của bộ này. Nếu css/js cũng về 0 thì `FAST`
        #    đã bị nới sang đường KHÔNG có dấu vân tay — tức quyết định ① bị phá và
        #    lớp lỗi "HTML mới + JS cũ" quay lại.
        check("[2] PHẠM VI: `css/common.css` VẪN hỏi máy chủ (mạng-trước)",
              n_css >= 1, "%d lượt" % n_css)
        check("[2] PHẠM VI: `js/ui-common.js` VẪN hỏi máy chủ (mạng-trước)",
              n_js >= 1, "%d lượt" % n_js)

        check("[3] `vendor/` KHÔNG có segment phiên bản thì KHÔNG cache-trước",
              n_bait >= 1, "%d lượt" % n_bait)
        # ⚠️ `?v=2` ở lượt HAI là cache TRÚNG, và đó mới là đúng: nó đã tự vào
        #    cache ở lượt làm nóng. Thứ cần chứng minh là một query CHƯA TỪNG
        #    thấy vẫn phá được cache — nên phải hỏi bằng một query MỚI.
        check("[4b] `?v=2` đã vào cache ở lượt làm nóng nên lượt hai trúng",
              n_q == 0, "%d lượt" % n_q)

        print("\n=== [3] Lượt thứ BA — query CHƯA TỪNG thấy (`?v=3`) ===")
        HITS.clear()
        NEW = "/vendor/three/0.160.0/three.module.min.js?v=3"
        st = pg.evaluate("u => fetch(u,{cache:'no-store'}).then(r=>r.status)", SITE + NEW)
        print("     %-50s %d lượt · HTTP %s" % (NEW, HITS.get(NEW, 0), st))
        check("[4c] query CHƯA TỪNG thấy thì cache HỤT, đi mạng thật",
              HITS.get(NEW, 0) == 1 and st == 200,
              "%d lượt · HTTP %s" % (HITS.get(NEW, 0), st))

        ctx.close()
        b.close()
finally:
    httpd.shutdown()
    for f in (BAIT, os.path.join(ROOT, "_probe_sw.html")):
        try:
            os.remove(f)
        except OSError:
            pass
    print("\n  đã xoá file mồi")

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(0 if bad_n == 0 else 1)
