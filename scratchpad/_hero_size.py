# -*- coding: utf-8 -*-
"""Anh hero trong trinh doc bai ve o co bao nhieu — de biet `img` co can ha cap khong."""
import http.server,socketserver,threading,sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8131
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch()
    for vp,lbl in [({"width":500,"height":844},"dienthoai 390"),({"width":1440,"height":900},"laptop")]:
        for aid in ["lib-nebula","lib-andromeda","lib-saturn"]:
            ctx=b.new_context(viewport=vp,device_scale_factor=2,locale="vi-VN")
            ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
            pg=ctx.new_page()
            pg.goto("http://localhost:%d/library.html?a=%s"%(PORT,aid),wait_until="load",timeout=45000)
            pg.wait_for_timeout(3500)
            d=pg.evaluate("""() => [...document.querySelectorAll('img')]
               .filter(i=>/images-assets/.test(i.currentSrc||''))
               .map(i=>{const r=i.getBoundingClientRect();
                 return {s:i.currentSrc.split('/').pop(),nw:i.naturalWidth,nh:i.naturalHeight,
                         rw:Math.round(r.width),rh:Math.round(r.height)};})""")
            for x in d:
                need=x["rw"]*2
                print("  %-12s %-14s %-22s that %4dx%-4d ve %3dx%-3d (DPR2 can %dpx) ty le %.1fx"%(
                    lbl,aid,x["s"],x["nw"],x["nh"],x["rw"],x["rh"],need,x["nw"]/need if need else 0))
            if not d: print("  %-12s %-14s khong thay anh NASA nao"%(lbl,aid))
            ctx.close()
    b.close()
h.shutdown()
