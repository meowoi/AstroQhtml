# -*- coding: utf-8 -*-
r"""_font_ab.py — A/B preload phông trên CÙNG máy chủ, CÙNG hồ sơ mạng.

Bốn cấu hình, mỗi cấu hình 3 lượt, lấy TRUNG VỊ (một lượt 4G rất ồn):
  none  — chặn hết dòng preload (đúng hành vi TRƯỚC lượt sửa)
  2     — chỉ preload 2 phông thân bài (inter latin + vietnamese, 58 KB)
  4     — 4 phông dùng ở 37/37 trang (87 KB)
  5     — cả 5 (100 KB, bản đang chạy)

⚠️ CHẶN BẰNG `route`, KHÔNG sửa file — sửa 61 file cho mỗi cấu hình là 4 lượt
   sửa-rồi-khôi-phục, tức 4 cơ hội để lại repo ở trạng thái đã phá.
⚠️ Không thể "chặn một thẻ link" ở tầng mạng, nên cấu hình `none`/`2`/`4` được
   dựng bằng cách VÁ HTML trên đường truyền (`route` + `fulfill`) — trang trả về
   giống hệt bản thật trừ đúng những dòng preload bị bỏ.
"""
import http.server
import re
import socketserver
import statistics
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from playwright.sync_api import sync_playwright

PORT = 8133
SITE = "http://localhost:%d" % PORT
NET = (9 * 1024 * 1024 / 8, 3 * 1024 * 1024 / 8, 150)
CPU = 4
RUNS = 3
PAGES = ["dashboard.html", "index.html", "landing-app.html", "explorer.html"]

KEEP = {
    "none": [],
    "2": ["inter-vietnamese", "inter-latin"],
    "4": ["inter-vietnamese", "inter-latin",
          "space-grotesk-vietnamese", "space-grotesk-latin"],
    "5": None,          # None = giữ nguyên, không vá gì
}

PRELOAD_RE = re.compile(
    r'[ \t]*<link rel="preload" as="font"[^>]*href="[^"]*?fonts/([a-z0-9-]+)\.woff2"[^>]*>[ \t]*\r?\n?'
)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


COLLECT = """() => {
  const nav = performance.getEntriesByType('navigation')[0] || {};
  const fcp = (performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime;
  const f = performance.getEntriesByType('resource')
              .filter(r => /\\.woff2$/.test(r.name));
  return {
    fcp: fcp ? Math.round(fcp) : null,
    load: Math.round(nav.loadEventEnd || 0),
    nFont: f.length,
    fontStart: f.length ? Math.round(Math.min(...f.map(r => r.startTime))) : null,
    fontEnd:   f.length ? Math.round(Math.max(...f.map(r => r.responseEnd))) : null,
    fontKB: Math.round(f.reduce((a, r) => a + (r.transferSize || r.decodedBodySize || 0), 0) / 1024)
  };
}"""

socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", PORT), Quiet)
threading.Thread(target=httpd.serve_forever, daemon=True).start()


def patcher(keep):
    def handle(route):
        r = route.fetch()
        body = r.text()
        body = PRELOAD_RE.sub(
            lambda m: m.group(0) if m.group(1) in keep else "", body)
        route.fulfill(response=r, body=body)
    return handle


def once(b, page, cfg):
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-tour-seen','1');"
                        "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
    pg = ctx.new_page()
    keep = KEEP[cfg]
    if keep is not None:
        pg.route(SITE + "/" + page, patcher(set(keep)))
    cdp = ctx.new_cdp_session(pg)
    cdp.send("Network.enable")
    cdp.send("Network.emulateNetworkConditions", {
        "offline": False, "downloadThroughput": NET[0],
        "uploadThroughput": NET[1], "latency": NET[2]})
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": CPU})
    try:
        pg.goto(SITE + "/" + page, wait_until="load", timeout=90000)
        pg.wait_for_timeout(3500)
        m = pg.evaluate(COLLECT)
    except Exception as e:
        m = None
        print("   [bo qua] %s/%s %s" % (page, cfg, str(e)[:60]))
    ctx.close()
    return m


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs)) if xs else None


with sync_playwright() as p:
    b = p.chromium.launch()
    for page in PAGES:
        print("\n=== %s  (4G RTT150 + CPU x%d, trung vi %d luot) ===" % (page, CPU, RUNS))
        print("%-6s %6s %7s %8s %8s %8s %7s" %
              ("cfg", "FCP", "LOAD", "font_bd", "font_xong", "vs_FCP", "font_KB"))
        base = None
        for cfg in ("none", "2", "4", "5"):
            rows = [once(b, page, cfg) for _ in range(RUNS)]
            fcp = med([r["fcp"] for r in rows if r])
            load = med([r["load"] for r in rows if r])
            fs = med([r["fontStart"] for r in rows if r])
            fe = med([r["fontEnd"] for r in rows if r])
            kb = med([r["fontKB"] for r in rows if r])
            # vs_FCP < 0  ⇒ phông về TRƯỚC lần vẽ đầu  ⇒ KHÔNG có cú nhảy chữ.
            vs = (fe - fcp) if (fe is not None and fcp is not None) else None
            if cfg == "none":
                base = fcp
            d = "" if base is None or fcp is None else " (%+d)" % (fcp - base)
            print("%-6s %6s%-6s %7s %8s %8s %+8s %7s" %
                  (cfg, fcp, d, load, fs, fe, vs, kb))
    b.close()
httpd.shutdown()
print("\nvs_FCP am = phong ve TRUOC lan ve dau = khong co cu nhay chu.")
