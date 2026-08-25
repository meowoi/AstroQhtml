# -*- coding: utf-8 -*-
"""Tran tren cua viec `defer`: chan HET script co dien roi do FCP/LCP.
Trang HONG khi chan — day KHONG phai ban de dung, chi de biet FCP toi da doi duoc bao nhieu."""
import http.server,socketserver,threading,sys,re
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8129
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
NET=(9*1024*1024/8,3*1024*1024/8,150)
def blocking_scripts(page):
    s=open(page,encoding="utf-8",errors="ignore").read()
    out=[]
    for m in re.finditer(r'<script\b([^>]*)>',s):
        a=m.group(1); sr=re.search(r'src="([^"]+)"',a)
        if sr and 'type="module"' not in a and ' defer' not in a and ' async' not in a:
            out.append(sr.group(1).split('?')[0].lstrip('/'))
    return out
def measure(b,page,block):
    ctx=b.new_context(viewport={"width":500,"height":844},locale="vi-VN")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-tour-seen','1')}catch(e){}")
    pg=ctx.new_page()
    if block:
        pg.route(re.compile(r".*"), lambda r: r.abort() if any(r.request.url.endswith("/"+p) for p in block) else r.continue_())
    cdp=ctx.new_cdp_session(pg); cdp.send("Network.enable")
    cdp.send("Network.emulateNetworkConditions",{"offline":False,"downloadThroughput":NET[0],"uploadThroughput":NET[1],"latency":NET[2]})
    cdp.send("Emulation.setCPUThrottlingRate",{"rate":4})
    try: pg.goto("http://localhost:%d/%s"%(PORT,page),wait_until="commit",timeout=60000)
    except Exception: pass
    pg.wait_for_timeout(7000)
    fcp=pg.evaluate("()=>Math.round((performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime||0)")
    ctx.close(); return fcp
with sync_playwright() as p:
    b=p.chromium.launch()
    for page in ["dashboard.html","achievements.html","games.html","library.html","explorer.html"]:
        bl=blocking_scripts(page)
        a=measure(b,page,None); c=measure(b,page,bl)
        print("%-22s FCP hien tai %5d ms  |  chan %2d script co dien: %5d ms  ->  toi da bot %4d ms (%.0f%%)"%(
            page,a,len(bl),c,a-c,100*(a-c)/a if a else 0))
    b.close()
h.shutdown()
