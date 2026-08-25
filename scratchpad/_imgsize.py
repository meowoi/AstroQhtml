# -*- coding: utf-8 -*-
import http.server,socketserver,threading,sys,json
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8124
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
JS="""() => [...document.querySelectorAll('img')].filter(i=>i.currentSrc).map(i=>{
  const r=i.getBoundingClientRect();
  return {src:i.currentSrc.split('/').slice(-1)[0], nw:i.naturalWidth, nh:i.naturalHeight,
          rw:Math.round(r.width), rh:Math.round(r.height), attr: i.hasAttribute('width')};
})"""
PAGES=["landing-app.html","index.html","dashboard.html","games.html","library.html","select.html"]
with sync_playwright() as p:
    b=p.chromium.launch()
    for vp,lbl in [({"width":1440,"height":900},"desktop"),({"width":500,"height":844},"mobile390")]:
        for pg_ in PAGES:
            ctx=b.new_context(viewport=vp,device_scale_factor=2,locale="vi-VN")
            ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-tour-seen','1')}catch(e){}")
            pg=ctx.new_page()
            try:
                pg.goto("http://localhost:%d/%s"%(PORT,pg_),wait_until="load",timeout=45000)
                pg.wait_for_timeout(2500)
                d=pg.evaluate(JS)
            except Exception as e:
                print("  [bo qua] %s %s"%(pg_,str(e)[:50])); ctx.close(); continue
            waste=[x for x in d if x["rw"]>0 and x["nw"] > x["rw"]*2*1.6]
            if waste:
                print("== %s / %s =="%(pg_,lbl))
                for x in sorted(waste,key=lambda x:-(x["nw"]*x["nh"])):
                    print("   %-26s that %4dx%-4d  ve %3dx%-3d (DPR2 can %dpx) ty le %.1fx  width-attr=%s"%(
                        x["src"],x["nw"],x["nh"],x["rw"],x["rh"],x["rw"]*2,x["nw"]/(x["rw"]*2),x["attr"]))
            ctx.close()
    b.close()
h.shutdown()
