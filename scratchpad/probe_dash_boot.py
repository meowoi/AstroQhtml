# -*- coding: utf-8 -*-
r"""probe_dash_boot.py — do THOI DIEM KHOI DONG cua `dashboard.html`: FCP,
DOMContentLoaded, load, va thoi diem thanh HUD dau tien co chu.

    python scratchpad/probe_dash_boot.py             # 1440px, tieng Viet
    python scratchpad/probe_dash_boot.py 390         # khung nhin khac
    python scratchpad/probe_dash_boot.py 1440 en     # tre chon tieng Anh

⚠️⚠️ TIET CHE MANG PHAI CO, va day la bai hoc tra gia o `probe_cls.py` cung ngay:
   cung mot trang, khong tiet che mang thi moi con so tot len va moi cu nhay bien
   mat. Do o may nhanh roi ket luan "trang nhanh" la mot ket luan RONG.
   Quy uoc: 4G 9 Mbps / RTT 150ms + CPU ×4 — cung mot bo so voi `perf_ab.py`.

⚠️ `dashboard.html` co **20 file script chan parser (361 KB)** + mot khoi noi tuyen
   1.052 dong. Do la viec (8) cua ban ra soat 23/08. Bo do nay la de biet sua co an
   gi khong, nen no phai chay TRUOC va SAU khi sua, tren cung mot may.

⚠️ TRUNG VI cua nhieu luot, khong lay mot luot. Bien dong giua cac luot o day tinh
   bang tram ms; mot luot don le khong noi len gi.
"""
import http.server
import os
import statistics
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = 8148
LAPS = 5

# ⚠️⚠️ FCP MOT MINH LA CON SO GAY NHAM LAN O TRANG NAY, va do la ly do co
#    `main_vis`. Voi tre chon EN, `<main>` bi che (lop `lang-wait`) cho tới khi
#    `applyLang` chay xong — nen FCP chi noi "nen da son", khong noi "doc duoc gi".
#    `main_vis` = thoi diem `<main>` THUC SU hien, tuc thoi diem tre doc duoc chu
#    DUNG NGON NGU CUA NO. Do la thuoc do phai so sanh truoc/sau, khong phai FCP.
T = """() => {
  const nav = performance.getEntriesByType('navigation')[0] || {};
  const fcp = performance.getEntriesByName('first-contentful-paint')[0];
  const lcp = window.__lcp || -1;
  return {
    fcp: fcp ? Math.round(fcp.startTime) : -1,
    dcl: Math.round(nav.domContentLoadedEventEnd || -1),
    load: Math.round(nav.loadEventEnd || -1),
    lcp: Math.round(lcp),
    main_vis: Math.round(window.__mainVis || -1),
    js: Math.round(performance.getEntriesByType('resource')
          .filter(r => r.initiatorType === 'script')
          .reduce((a, r) => a + (r.encodedBodySize || 0), 0) / 1024)
  };
}"""

INIT = """
window.__lcp = -1; window.__mainVis = -1;
try {
  const seen = () => {
    const m = document.querySelector('main');
    if (!m) return false;
    if (getComputedStyle(m).visibility !== 'visible') return false;
    window.__mainVis = performance.now();
    return true;
  };
  const iv = setInterval(() => { if (seen()) clearInterval(iv); }, 40);
  setTimeout(() => clearInterval(iv), 20000);
} catch (e) {}
try { new PerformanceObserver((l) => {
  for (const e of l.getEntries()) window.__lcp = e.startTime;
}).observe({type: 'largest-contentful-paint', buffered: true}); } catch (e) {}
"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 1440
    lang = sys.argv[2] if len(sys.argv) > 2 else "vi"
    h = 844 if w < 500 else 900

    http.server.ThreadingHTTPServer.allow_reuse_address = True
    httpd = http.server.ThreadingHTTPServer(("", PORT), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    rows = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
            for i in range(LAPS):
                ctx = b.new_context(viewport={"width": w, "height": h},
                                    locale="vi-VN", is_mobile=(w < 500),
                                    has_touch=(w < 500))
                ctx.add_init_script(
                    "try{localStorage.setItem('astroq-lang','%s');"
                    "localStorage.setItem('astroq-map01-seen','1')}catch(e){}" % lang)
                ctx.add_init_script(INIT)
                pg = ctx.new_page()
                errs = []
                pg.on("pageerror", lambda e: errs.append(str(e)[:90]))
                cdp = ctx.new_cdp_session(pg)
                cdp.send("Network.enable", {})
                cdp.send("Network.emulateNetworkConditions", {
                    "offline": False, "latency": 150,
                    "downloadThroughput": 9 * 1024 * 1024 / 8,
                    "uploadThroughput": 9 * 1024 * 1024 / 8})
                cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
                pg.goto("http://localhost:%d/dashboard.html" % PORT,
                        wait_until="load", timeout=120000)
                pg.wait_for_timeout(2200)
                d = pg.evaluate(T)
                d["errs"] = errs
                rows.append(d)
                print("  luot %d: FCP %5d | main hien %5d | DCL %5d | load %5d | JS %4d KB%s"
                      % (i + 1, d["fcp"], d["main_vis"], d["dcl"], d["load"], d["js"],
                         ("  LOI: " + errs[0]) if errs else ""))
                ctx.close()
            b.close()
    finally:
        httpd.shutdown()

    print("\n=== TRUNG VI %d luot @ %dpx (4G + CPU x4) ===" % (LAPS, w))
    for k, lbl in (("fcp", "FCP"), ("main_vis", "<main> hien ra"),
                   ("dcl", "DOMContentLoaded"),
                   ("load", "load"), ("lcp", "LCP"), ("js", "JS tai ve (KB)")):
        print("  %-18s %6.0f" % (lbl, statistics.median(r[k] for r in rows)))
    nerr = sum(1 for r in rows if r["errs"])
    print("  luot co loi trang  %6d / %d" % (nerr, LAPS))
    return 1 if nerr else 0


if __name__ == "__main__":
    sys.exit(main())
