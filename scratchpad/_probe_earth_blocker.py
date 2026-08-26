# -*- coding: utf-8 -*-
r"""_probe_earth_blocker.py — CAI GI dang nam tren nhan Trai Dat? So TRE MOI (chua
co `astroq-map01-seen`) voi TRE CU. Bo do MOT LAN, khong nam trong cong day du.

⚠️ `probe_label_overlap.py` (dat co `map01-seen=1`) noi khong con nhan de nhan, ma
   `probe_globe_daynight.py` (KHONG dat co) van phai di duong lui 3/3. Hai bo do
   khong the cung dung ve cung mot thu, nen phai tim ra CHO KHAC NHAU truoc khi
   ket luan bat cu dieu gi.
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
PORT = 8141

JS = r"""() => {
  const who = (e) => {
    if (!e) return "(khong co gi)";
    const id = e.id ? '#' + e.id : '';
    const cl = (e.className && typeof e.className === 'string')
      ? '.' + e.className.trim().split(/\s+/).join('.') : '';
    return e.tagName.toLowerCase() + id + cl;
  };
  const l = document.querySelector('#labels [data-body-id="earth"]');
  if (!l) return {err: "khong thay nhan earth"};
  const r = l.getBoundingClientRect();
  const cx = Math.round(r.left + r.width / 2), cy = Math.round(r.top + r.height / 2);
  const stack = document.elementsFromPoint(cx, cy).slice(0, 5).map(who);
  return {
    x: cx, y: cy, w: Math.round(r.width), h: Math.round(r.height),
    vis: getComputedStyle(l).visibility,
    cls: l.className,
    top: who(document.elementFromPoint(cx, cy)),
    stack: stack
  };
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for tag, seen in (("TRE MOI (khong co map01-seen)", False),
                              ("TRE CU (map01-seen=1)", True)):
                print("\n=== %s ===" % tag)
                for rd in range(3):
                    ctx = b.new_context(viewport={"width": 1440, "height": 900},
                                        locale="vi-VN")
                    js = "try{localStorage.setItem('astroq-lang','vi');"
                    if seen:
                        js += "localStorage.setItem('astroq-map01-seen','1');"
                    js += "}catch(e){}"
                    ctx.add_init_script(js)
                    pg = ctx.new_page()
                    pg.goto("http://localhost:%d/explorer.html" % PORT,
                            wait_until="load", timeout=60000)
                    try:
                        pg.wait_for_function("() => window.__solarReady === true",
                                             timeout=30000)
                    except Exception:
                        pass
                    pg.wait_for_timeout(3400)
                    d = pg.evaluate(JS)
                    print("  luot %d: tam (%s,%s) %sx%s vis=%s class=%r"
                          % (rd + 1, d.get("x"), d.get("y"), d.get("w"),
                             d.get("h"), d.get("vis"), d.get("cls")))
                    print("           TREN CUNG: %s" % d.get("top"))
                    print("           chong lop: %s" % " | ".join(d.get("stack") or []))
                    ctx.close()
            b.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
