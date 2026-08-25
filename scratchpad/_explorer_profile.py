# -*- coding: utf-8 -*-
"""Ho so CPU that cua luot vao explorer.html — ai chiem khoi 2,8 giay."""
import http.server,socketserver,threading,sys,json,collections
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8126
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
    ctx=b.new_context(viewport={"width":1440,"height":900},locale="vi-VN")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-tour-seen','1');localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
    pg=ctx.new_page()
    cdp=ctx.new_cdp_session(pg)
    cdp.send("Profiler.enable"); cdp.send("Profiler.setSamplingInterval",{"interval":200})
    cdp.send("Profiler.start")
    pg.goto("http://localhost:%d/explorer.html"%PORT,wait_until="load",timeout=120000)
    pg.wait_for_timeout(9000)
    prof=cdp.send("Profiler.stop")["profile"]
    nodes={n["id"]:n for n in prof["nodes"]}
    self_t=collections.Counter()
    # tong thoi gian tu (self time) theo node
    total=0
    if prof.get("timeDeltas") and prof.get("samples"):
        for sid,dt in zip(prof["samples"],prof["timeDeltas"]):
            self_t[sid]+=max(0,dt); total+=max(0,dt)
    print("tong mau: %.0f ms\n"%(total/1000))
    # gop theo file
    byfile=collections.Counter(); byfn=collections.Counter()
    for nid,us in self_t.items():
        cf=nodes.get(nid,{}).get("callFrame",{})
        url=(cf.get("url") or "(khong ro)").split("/")[-1] or "(inline)"
        fn=cf.get("functionName") or "(anon)"
        byfile[url]+=us; byfn["%s @ %s:%s"%(fn,url,cf.get("lineNumber"))]+=us
    print("=== 12 FILE ton CPU nhat ===")
    for u,us in byfile.most_common(12): print("  %8.0f ms  %s"%(us/1000,u))
    print("\n=== 15 HAM ton CPU nhat ===")
    for f,us in byfn.most_common(15): print("  %8.0f ms  %s"%(us/1000,f))
    ctx.close(); b.close()
h.shutdown()
