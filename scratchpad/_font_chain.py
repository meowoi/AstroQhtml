# -*- coding: utf-8 -*-
import http.server,socketserver,threading,sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8128
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
JS="""() => performance.getEntriesByType('resource')
  .filter(r=>/\.(woff2|css)$/.test(r.name))
  .map(r=>[r.name.split('/').slice(-1)[0], Math.round(r.startTime), Math.round(r.responseEnd)])
  .sort((a,b)=>a[1]-b[1])"""
NET=(9*1024*1024/8,3*1024*1024/8,150)
with sync_playwright() as p:
    b=p.chromium.launch()
    for page in ["index.html","dashboard.html","landing-app.html"]:
        ctx=b.new_context(viewport={"width":500,"height":844},locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-tour-seen','1')}catch(e){}")
        pg=ctx.new_page()
        cdp=ctx.new_cdp_session(pg); cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions",{"offline":False,"downloadThroughput":NET[0],"uploadThroughput":NET[1],"latency":NET[2]})
        cdp.send("Emulation.setCPUThrottlingRate",{"rate":4})
        pg.goto("http://localhost:%d/%s"%(PORT,page),wait_until="load",timeout=60000)
        pg.wait_for_timeout(3500)
        fcp=pg.evaluate("()=>Math.round((performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime||0)")
        print("\n== %s  (FCP %d ms) =="%(page,fcp))
        for n,s,e in pg.evaluate(JS):
            print("   %-34s bat dau %5d ms  xong %5d ms"%(n,s,e))
        ctx.close()
    b.close()
h.shutdown()
