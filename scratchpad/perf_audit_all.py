# -*- coding: utf-8 -*-
"""perf_audit_all.py — DO CAC THONG SO HIEU NANG CUA MOI TRANG, tren CUNG mot may
chu tinh (localhost) + CUNG mot ho so mang/CPU. Khong doan, chi do.

  python scratchpad/perf_audit_all.py            # 4G + CPU x4
  python scratchpad/perf_audit_all.py fast       # khong tiet che
"""
import http.server, json, socketserver, sys, threading, re, os

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from playwright.sync_api import sync_playwright

PORT = 8123
SITE = "http://localhost:%d" % PORT
THROTTLE = "fast" not in sys.argv
NET = (9*1024*1024/8, 3*1024*1024/8, 150)     # 4G, RTT 150ms
CPU = 4

PAGES = ["index.html", "landing-app.html", "select.html", "games.html",
         "learn.html", "library.html", "quiz.html", "missions.html",
         "explorer.html", "dashboard.html", "mission-earth.html",
         "game-defender.html", "game-racer.html", "game-dodge.html",
         "shop.html", "profile.html", "achievements.html", "pricing.html"]

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

PROBE = """
window.__P = {lt:[], cls:0, res:[]};
try{ new PerformanceObserver(l=>{for(const e of l.getEntries())
      window.__P.lt.push([Math.round(e.startTime), Math.round(e.duration)]);})
    .observe({type:'longtask', buffered:true}); }catch(e){}
try{ new PerformanceObserver(l=>{for(const e of l.getEntries())
      if(!e.hadRecentInput) window.__P.cls += e.value;})
    .observe({type:'layout-shift', buffered:true}); }catch(e){}
try{ new PerformanceObserver(l=>{const e=l.getEntries();
      window.__P.lcp = Math.round(e[e.length-1].startTime);
      window.__P.lcpEl = (e[e.length-1].element||{}).tagName || '?';})
    .observe({type:'largest-contentful-paint', buffered:true}); }catch(e){}
"""

COLLECT = """() => {
  const p = window.__P || {};
  const nav = performance.getEntriesByType('navigation')[0] || {};
  const fcp = (performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime;
  const res = performance.getEntriesByType('resource');
  const by = {};
  let bytes = 0;
  for (const r of res) {
    const k = (r.name.split('?')[0].split('.').pop()||'?').toLowerCase();
    by[k] = by[k] || {n:0, b:0};
    by[k].n++; by[k].b += (r.transferSize||0); bytes += (r.transferSize||0);
  }
  const lt = p.lt || [];
  return {
    url: location.pathname,
    fcp: fcp ? Math.round(fcp) : null,
    lcp: p.lcp || null, lcpEl: p.lcpEl || null,
    dcl: Math.round(nav.domContentLoadedEventEnd||0),
    load: Math.round(nav.loadEventEnd||0),
    ttfb: Math.round(nav.responseStart||0),
    docBytes: nav.transferSize||0,
    resBytes: bytes, reqs: res.length, by,
    cls: Math.round((p.cls||0)*1000)/1000,
    ltN: lt.length,
    ltSum: lt.reduce((a,b)=>a+b[1],0),
    ltMax: lt.reduce((a,b)=>Math.max(a,b[1]),0),
    dom: document.getElementsByTagName('*').length,
    css: performance.getEntriesByType('resource').filter(r=>r.name.endsWith('.css')).length
  };
}"""

FRAMES = """() => new Promise(res => {
  let n = 0, worst = 0, last = performance.now(), t0 = last;
  function tick(now){ const d = now - last; last = now; if (n) worst = Math.max(worst, d); n++;
    if (now - t0 < 2500) requestAnimationFrame(tick);
    else res({fps: Math.round(n/((now-t0)/1000)), worst: Math.round(worst)}); }
  requestAnimationFrame(tick);
})"""

socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", PORT), Quiet)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for page in PAGES:
        ctx = b.new_context(viewport={"width":1440,"height":900}, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
        pg = ctx.new_page()
        pg.add_init_script(PROBE)
        cdp = ctx.new_cdp_session(pg)
        cdp.send("Network.enable")
        if THROTTLE:
            cdp.send("Network.emulateNetworkConditions", {"offline":False,
                "downloadThroughput":NET[0],"uploadThroughput":NET[1],"latency":NET[2]})
            cdp.send("Emulation.setCPUThrottlingRate", {"rate":CPU})
        try:
            pg.goto(SITE + "/" + page, wait_until="load", timeout=90000)
        except Exception as e:
            print("  [BO QUA] %s — %s" % (page, str(e)[:60])); ctx.close(); continue
        pg.wait_for_timeout(4000)
        try: m = pg.evaluate(COLLECT)
        except Exception as e:
            print("  [BO QUA] %s — %s" % (page, str(e)[:60])); ctx.close(); continue
        try: f = pg.evaluate(FRAMES)
        except Exception: f = {"fps":None,"worst":None}
        m["fps"] = f["fps"]; m["worst"] = f["worst"]; m["page"] = page
        rows.append(m)
        print("  do xong %s" % page)
        ctx.close()
    b.close()
httpd.shutdown()

json.dump(rows, open("scratchpad/_perf_audit.json","w",encoding="utf-8"), indent=1)

hdr = ("%-22s %6s %6s %6s %7s %8s %5s %6s %7s %6s %6s %5s %6s" %
       ("TRANG","FCP","LCP","DCL","LOAD","BYTES","REQ","DOM","LT_SUM","LT_MAX","CLS","FPS","WORST"))
print("\n" + ("=== 4G RTT150 + CPU x%d ===" % CPU if THROTTLE else "=== KHONG TIET CHE ==="))
print(hdr); print("-"*len(hdr))
for r in sorted(rows, key=lambda r: -(r["lcp"] or 0)):
    print("%-22s %6s %6s %6s %7s %7.0fK %5s %6s %7s %6s %6s %5s %6s" % (
        r["page"], r["fcp"], r["lcp"], r["dcl"], r["load"],
        (r["docBytes"]+r["resBytes"])/1024, r["reqs"], r["dom"],
        r["ltSum"], r["ltMax"], r["cls"], r["fps"], r["worst"]))
print("\nchi tiet byte theo duoi file: scratchpad/_perf_audit.json")
