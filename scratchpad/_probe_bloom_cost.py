# -*- coding: utf-8 -*-
r"""_probe_bloom_cost.py — bloom (`EffectComposer` + `UnrealBloomPass`) lam chậm luc
mo `explorer.html` bao nhieu? Do THOI DIEM `__solarReady` va khung dau, co/khong bloom.

⚠️ SO SANH BANG CACH SUA FILE ROI KHOI PHUC, va khoi phuc trong `finally` — mot bo do
   chet giua duong khong duoc de lai cay ma nguon o trang thai da cat mot phan.

⚠️ Bloom ton hai thu KHAC NHAU, va phai tach ra: (a) TAI 27 KB module postprocessing,
   (b) BIEN DICH shader luc dung canh. (b) moi la thu dang ke, va no khong hien ra
   trong bat ky con so "byte" nao — nen phai do thoi gian, khong do dung luong.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = "explorer.html"
PORT = 8147
LAPS = 3

OFF = """    // [DO THU] bloom bi bo de do gia cua no
    this.composer=null; this.lowQuality=true;
"""
ON = """    // Bloom for the Sun's warm glow (subtle).
    this.composer=new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    this.bloom=new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.85, 0.5, 0.82);
    this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());
"""


def measure(pw, tag, port):
    import statistics
    out = []
    b = pw.chromium.launch(args=["--enable-unsafe-swiftshader"])
    for i in range(LAPS):
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
        pg = ctx.new_page()
        cdp = ctx.new_cdp_session(pg)
        cdp.send("Network.enable", {})
        cdp.send("Network.emulateNetworkConditions", {
            "offline": False, "latency": 150,
            "downloadThroughput": 9 * 1024 * 1024 / 8,
            "uploadThroughput": 9 * 1024 * 1024 / 8})
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        pg.goto("http://localhost:%d/explorer.html" % port, wait_until="commit",
                timeout=120000)
        try:
            pg.wait_for_function("() => window.__solarReady === true", timeout=90000)
        except Exception:
            out.append(None)
            ctx.close()
            continue
        t = pg.evaluate("""() => {
            const nav = performance.getEntriesByType('navigation')[0];
            const fcp = performance.getEntriesByName('first-contentful-paint')[0];
            return {ready: Math.round(performance.now()),
                    dcl: nav ? Math.round(nav.domContentLoadedEventEnd) : -1,
                    fcp: fcp ? Math.round(fcp.startTime) : -1};
        }""")
        out.append(t)
        ctx.close()
    b.close()
    good = [x for x in out if x]
    if not good:
        print("  %-14s KHONG DO DUOC (%d/%d luot chet)" % (tag, LAPS, LAPS))
        return None
    med = lambda k: statistics.median(x[k] for x in good)
    print("  %-14s __solarReady %5.0f ms | FCP %5.0f ms | DCL %5.0f ms   (%d luot)"
          % (tag, med("ready"), med("fcp"), med("dcl"), len(good)))
    return med("ready")


def main():
    import http.server
    import threading
    from playwright.sync_api import sync_playwright

    orig = io.open(SRC, encoding="utf-8").read()
    if ON not in orig:
        print("[HONG] khong tim thay khoi dung bloom trong %s — bo do da lac hau" % SRC)
        return 1

    http.server.ThreadingHTTPServer.allow_reuse_address = True
    httpd = http.server.ThreadingHTTPServer(("", PORT), _Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            a = measure(pw, "CO bloom", PORT)
            io.open(SRC, "w", encoding="utf-8", newline="\n").write(
                orig.replace(ON, OFF))
            bb = measure(pw, "KHONG bloom", PORT)
    finally:
        io.open(SRC, "w", encoding="utf-8", newline="\n").write(orig)
        httpd.shutdown()
        print("  (da khoi phuc %s)" % SRC)
    if a and bb:
        print("\n  => bloom ton %.0f ms cho toi luc canh hien ra (%.0f%%)"
              % (a - bb, 100.0 * (a - bb) / bb))
    return 0


class _Quiet:
    pass


if __name__ == "__main__":
    import http.server as _hs

    class _Q(_hs.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    _Quiet = _Q
    sys.exit(main())
