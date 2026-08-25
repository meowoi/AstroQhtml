# -*- coding: utf-8 -*-
"""CLS: chi ra DUNG phan tu nao nhay, o giay thu bao nhieu."""
import http.server,socketserver,threading,sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8127
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
PROBE="""
window.__S=[];
try{new PerformanceObserver(l=>{for(const e of l.getEntries()){ if(e.hadRecentInput) continue;
  window.__S.push({t:Math.round(e.startTime), v:Math.round(e.value*1000)/1000,
    src:(e.sources||[]).map(s=>{const n=s.node; if(!n) return '?';
      const id=n.id?('#'+n.id):''; const cl=(n.className&&typeof n.className==='string')?('.'+n.className.trim().split(/\s+/).slice(0,2).join('.')):'';
      return (n.tagName||'?').toLowerCase()+id+cl+' ['+Math.round(s.previousRect.y)+'->'+Math.round(s.currentRect.y)+']';})});
}}).observe({type:'layout-shift',buffered:true});}catch(e){}
"""
NET=(9*1024*1024/8,3*1024*1024/8,150)
PAGES=["profile.html","achievements.html","game-defender.html","library.html","index.html","game-racer.html","game-dodge.html","missions.html"]
with sync_playwright() as p:
    b=p.chromium.launch()
    for pgname in PAGES:
        ctx=b.new_context(viewport={"width":500,"height":844},device_scale_factor=2,locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-tour-seen','1');localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
        pg=ctx.new_page(); pg.add_init_script(PROBE)
        cdp=ctx.new_cdp_session(pg); cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions",{"offline":False,"downloadThroughput":NET[0],"uploadThroughput":NET[1],"latency":NET[2]})
        cdp.send("Emulation.setCPUThrottlingRate",{"rate":4})
        try:
            pg.goto("http://localhost:%d/%s"%(PORT,pgname),wait_until="load",timeout=60000)
            pg.wait_for_timeout(5000)
            s=pg.evaluate("()=>window.__S||[]")
        except Exception as e:
            print("[bo qua] %s %s"%(pgname,str(e)[:50])); ctx.close(); continue
        tot=sum(x["v"] for x in s)
        print("\n== %s  CLS=%.3f  (%d cu nhay) =="%(pgname,tot,len(s)))
        for x in sorted(s,key=lambda x:-x["v"])[:5]:
            print("   %6dms  +%.3f  %s"%(x["t"],x["v"],"; ".join(x["src"])[:150]))
        ctx.close()
    b.close()
h.shutdown()
