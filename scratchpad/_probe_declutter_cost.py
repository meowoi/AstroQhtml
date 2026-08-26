# -*- coding: utf-8 -*-
r"""_probe_declutter_cost.py — lop dan nhan chay TRONG VONG VE, nen phai do xem no
an bao nhieu khung hinh. So `explorer.html` hien tai voi ban TAT lop dan (tat bang
cach ghi de `_declutterLabels` thanh ham rong TRUOC khi vong ve bat dau).

⚠️ TAT BANG CACH GHI DE HAM, KHONG BANG CACH SUA FILE. Sua file roi do roi sua lai
   thi neu bo do chet giua duong, cay ma nguon o lai trang thai da bi cat mot phan.

⚠️ DO FPS BANG DEM KHUNG HINH THAT (`requestAnimationFrame`), khong bang `dt` trong
   vong ve: `dt` la thoi gian GIUA hai khung, no khong biet khung do co bi bo hay
   khong. Va do o CPU THROTTLE ×4 — may cua tre khong phai may nay.
"""
import http.server
import os
import socketserver
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = 8142
SECS = 6

COUNT = """() => new Promise(res => {
  let n = 0; const t0 = performance.now();
  const f = () => { n++;
    if (performance.now() - t0 >= %d) res({n: n, ms: performance.now() - t0});
    else requestAnimationFrame(f); };
  requestAnimationFrame(f);
})""" % (SECS * 1000)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def run(b, off, throttle):
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script(
        "try{localStorage.setItem('astroq-lang','vi');"
        "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
    if off:
        # Ghi de NGAY khi tai liệu bat dau, truoc khi module explorer chay.
        ctx.add_init_script(
            "Object.defineProperty(window,'__noDeclutter',{value:true});")
    pg = ctx.new_page()
    cdp = ctx.new_cdp_session(pg)
    if throttle:
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    pg.goto("http://localhost:%d/explorer.html" % PORT, wait_until="load",
            timeout=90000)
    if off:
        pg.evaluate("() => { if (window.solarApp) window.solarApp._declutterLabels = () => {}; }")
    try:
        pg.wait_for_function("() => window.__solarReady === true", timeout=60000)
    except Exception:
        pass
    if off:
        n = pg.evaluate("""() => {
            const a = window.solarApp;
            if (!a) return 'KHONG THAY window.solarApp';
            a._declutterLabels = function(){};
            return 'da tat';
        }""")
    else:
        n = "bat"
    # ⚠️ FPS o headless bi SwiftShader chan quanh 8 fps nen KHONG DU PHAN GIAI de
    #    thay gia cua lop dan. Do THANG thoi gian cua chinh ham do: boc no lai, cong
    #    don `performance.now()` qua tung lan goi that trong vong ve.
    pg.evaluate("""() => {
        const a = window.solarApp; if (!a) return;
        const f = a._declutterLabels.bind(a);
        window.__dt = {n: 0, ms: 0, max: 0};
        a._declutterLabels = function(){
          const t = performance.now(); f();
          const d = performance.now() - t;
          window.__dt.n++; window.__dt.ms += d;
          if (d > window.__dt.max) window.__dt.max = d;
        };
    }""")
    pg.wait_for_timeout(2500)
    d = pg.evaluate(COUNT)
    t = pg.evaluate("() => window.__dt || null")
    ctx.close()
    return d["n"] / (d["ms"] / 1000.0), n, t


def main():
    from playwright.sync_api import sync_playwright
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
            for thr in (False, True):
                print("\n=== CPU throttle x%d ===" % (4 if thr else 1))
                for lap in range(2):
                    on_fps, _n1, t = run(b, False, thr)
                    off_fps, note, _t2 = run(b, True, thr)
                    print("  lap %d: BAT lop dan %.1f fps | TAT %.1f fps | "
                          "chenh %+.1f fps (%s)"
                          % (lap + 1, on_fps, off_fps, on_fps - off_fps, note))
                    if t and t.get("n"):
                        print("          ham lop dan: %d lan goi that, trung binh "
                              "%.2f ms, lan cham nhat %.2f ms"
                              % (t["n"], t["ms"] / t["n"], t["max"]))
            b.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
