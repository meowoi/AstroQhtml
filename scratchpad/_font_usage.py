# -*- coding: utf-8 -*-
"""Trang nao TAI THAT font nao — de biet nen preload cai gi, khong doan."""
import http.server,socketserver,threading,sys,glob,collections
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
PORT=8130
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
h=socketserver.TCPServer(("",PORT),Q); threading.Thread(target=h.serve_forever,daemon=True).start()
JS="""() => performance.getEntriesByType('resource').filter(r=>/\.woff2$/.test(r.name))
        .map(r=>r.name.split('/').pop())"""
PAGES=sorted(p for p in glob.glob("*.html") if p!="offline.html")
cnt=collections.Counter(); per={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for page in PAGES:
        for lang in ("vi","en"):
            ctx=b.new_context(viewport={"width":500,"height":844},locale=lang)
            ctx.add_init_script("try{localStorage.setItem('astroq-lang','%s');localStorage.setItem('astroq-tour-seen','1');localStorage.setItem('astroq-map01-seen','1')}catch(e){}"%lang)
            pg=ctx.new_page()
            try:
                pg.goto("http://localhost:%d/%s"%(PORT,page),wait_until="load",timeout=45000)
                pg.wait_for_timeout(2200)
                fs=set(pg.evaluate(JS))
            except Exception: fs=set()
            per.setdefault(page,set()).update(fs)
            ctx.close()
    b.close()
h.shutdown()
for page in PAGES:
    for f in per[page]: cnt[f]+=1
print("=== font tai tren BAO NHIEU / %d trang ==="%len(PAGES))
for f,n in cnt.most_common(): print("  %-34s %2d/%d"%(f,n,len(PAGES)))
print("\n=== trang THIEU mot font nao ===")
allf=set(cnt)
for page in PAGES:
    m=allf-per[page]
    if m: print("  %-24s khong tai: %s"%(page,sorted(x.replace('.woff2','') for x in m)))
