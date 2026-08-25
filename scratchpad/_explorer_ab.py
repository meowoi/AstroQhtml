# -*- coding: utf-8 -*-
"""Explorer: co/khong 'Giam cau hinh' — long task co giam khong?"""
import http.server,socketserver,threading,sys,json
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8125
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
PROBE="""
window.__P={lt:[]};
try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__P.lt.push([Math.round(e.startTime),Math.round(e.duration)]);}).observe({type:'longtask',buffered:true});}catch(e){}
"""
COLLECT="""() => {
  const lt=(window.__P||{}).lt||[];
  const res=performance.getEntriesByType('resource');
  const three=res.filter(r=>/vendor\/three/.test(r.name));
  return {
    ltSum: lt.reduce((a,b)=>a+b[1],0), ltMax: lt.reduce((a,b)=>Math.max(a,b[1]),0),
    ltN: lt.length, top: lt.sort((a,b)=>b[1]-a[1]).slice(0,5),
    ready: !!window.__solarReady,
    threeN: three.length,
    threeKB: Math.round(three.reduce((a,r)=>a+(r.transferSize||r.decodedBodySize||0),0)/1024),
    post: res.filter(r=>/postprocessing/.test(r.name)).map(r=>[r.name.split('/').pop(), Math.round(r.duration)])
  };
}"""
FR="""() => new Promise(res=>{let n=0,w=0,l=performance.now(),t0=l;
 function t(now){const d=now-l;l=now;if(n)w=Math.max(w,d);n++;
  if(now-t0<3000)requestAnimationFrame(t);else res({fps:Math.round(n/((now-t0)/1000)),worst:Math.round(w)});}
 requestAnimationFrame(t);})"""
NET=(9*1024*1024/8,3*1024*1024/8,150)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
    for perf,lbl in [("0","BINH THUONG      "),("1","GIAM CAU HINH ON ")]:
        ctx=b.new_context(viewport={"width":1440,"height":900},locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
          "localStorage.setItem('astroq-tour-seen','1');localStorage.setItem('astroq-map01-seen','1');"
          + ("localStorage.setItem('astroq-perf','1');" if perf=="1" else "") + "}catch(e){}")
        pg=ctx.new_page(); pg.add_init_script(PROBE)
        cdp=ctx.new_cdp_session(pg); cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions",{"offline":False,"downloadThroughput":NET[0],
          "uploadThroughput":NET[1],"latency":NET[2]})
        cdp.send("Emulation.setCPUThrottlingRate",{"rate":4})
        pg.goto("http://localhost:%d/explorer.html"%PORT,wait_until="load",timeout=120000)
        pg.wait_for_timeout(9000)
        m=pg.evaluate(COLLECT)
        try: f=pg.evaluate(FR)
        except Exception: f={"fps":None,"worst":None}
        print("%s ltSum=%-6d ltMax=%-5d n=%-3d fps=%-3s worst=%-4s canh-san-sang=%s three=%d file/%dKB"%(
            lbl,m["ltSum"],m["ltMax"],m["ltN"],f["fps"],f["worst"],m["ready"],m["threeN"],m["threeKB"]))
        print("     5 long task dai nhat (batdau,dai): %s"%m["top"])
        print("     module postprocessing tai ve: %s"%m["post"])
        ctx.close()
    b.close()
h.shutdown()
