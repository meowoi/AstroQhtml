# -*- coding: utf-8 -*-
"""Tìm THỦ PHẠM làm màn warp giật: liệt kê mọi long task (>50ms) trong lúc
màn "bay vào Hệ Mặt Trời" đang chạy, kèm mốc thời gian của từng giai đoạn
(module three.js về · scene dựng · khung vẽ đầu tiên · warp tắt).
"""
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8123"

PROBE = """
window.__lt = [];
window.__mk = [];
try{
  new PerformanceObserver(function(l){
    l.getEntries().forEach(function(e){ window.__lt.push({s:e.startTime, d:e.duration, n:e.name}); });
  }).observe({entryTypes:['longtask']});
}catch(e){}
window.__mark = function(n){ window.__mk.push({n:n, t:performance.now()}); };
(function(){
  var iv = setInterval(function(){
    var w = document.getElementById('nm-warp');
    var seen = window.__mk.map(function(m){return m.n;});
    if (w && w.classList.contains('show') && seen.indexOf('warpOn')<0) window.__mark('warpOn');
    if (window.__solarReady === true && seen.indexOf('ready')<0) window.__mark('ready');
    if (window.solarApp && seen.indexOf('appExists')<0) window.__mark('appExists');
    if (w && seen.indexOf('warpOn')>=0 && !w.classList.contains('show') && seen.indexOf('warpOff')<0){
      window.__mark('warpOff'); clearInterval(iv);
    }
  }, 8);
})();
"""


def run(rate):
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.add_init_script(PROBE)
        pg.add_init_script("try{localStorage.removeItem('astroq-map01-seen');}catch(e){}")
        if rate > 1:
            ctx.new_cdp_session(pg).send("Emulation.setCPUThrottlingRate", {"rate": rate})
        pg.goto(f"{BASE}/explorer.html?onboard=1", wait_until="commit")
        try:
            pg.wait_for_function(
                "window.__mk.some(m=>m.n==='warpOff')", timeout=30000)
        except Exception:
            print("  (warp chưa tắt)")
        pg.wait_for_timeout(400)
        lt = pg.evaluate("window.__lt")
        mk = pg.evaluate("window.__mk")
        res = pg.evaluate("""performance.getEntriesByType('resource')
            .filter(r=>/unpkg|three|jsm/.test(r.name))
            .map(r=>({n:r.name.split('/').slice(-1)[0], s:r.startTime, e:r.responseEnd}))""")
        br.close()
    print(f"=== CPU x{rate} ===")
    for m in mk:
        print(f"  mốc {m['n']:<10} {m['t']:8.0f} ms")
    if res:
        print("  tải three.js:")
        for r in res:
            print(f"    {r['n'][:40]:<42} {r['s']:6.0f} → {r['e']:6.0f} ms")
    on = next((m["t"] for m in mk if m["n"] == "warpOn"), 0)
    off = next((m["t"] for m in mk if m["n"] == "warpOff"), 1e9)
    seg = [x for x in lt if x["s"] < off and x["s"] + x["d"] > on]
    seg.sort(key=lambda x: -x["d"])
    print(f"  long task (>50ms) chồng lên màn warp: {len(seg)}, tổng "
          f"{sum(x['d'] for x in seg):.0f} ms trong khoảng warp {off-on:.0f} ms")
    for x in seg[:12]:
        print(f"    {x['s']:8.0f} → {x['s']+x['d']:8.0f}  ({x['d']:6.0f} ms)")


run(1)
print()
run(4)
