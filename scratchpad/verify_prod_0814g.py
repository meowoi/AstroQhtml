# -*- coding: utf-8 -*-
import sys, re, time, json, urllib.request
from playwright.sync_api import sync_playwright
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25)
    return r.status, r.read().decode("utf-8","replace")
ok=bad=0
def ck(n,c,d=""):
    global ok,bad
    if c: ok+=1; print(f"  [OK]   {n}"+(f"  ({d})" if d else ""))
    else: bad+=1; print(f"  [HONG] {n}  {d}")

WANT = re.search(r'VERSION\s*=\s*"([\d.]+)"',
                 open("js/ui-common.js",encoding="utf-8").read()).group(1)
ver=None
for i in range(24):
    try:
        _,t=get("https://astroq.org/js/ui-common.js?cb=%d"%time.time())
        m=re.search(r'VERSION\s*=\s*"([\d.]+)"',t); ver=m.group(1) if m else None
        if ver==WANT: break
    except Exception: pass
    time.sleep(10)
ck(f"ban dung tren Pages = {WANT}", ver==WANT, f"doc ra {ver}")
if ver!=WANT:
    print("\n>>> Pages CHUA build xong — dung do."); sys.exit(1)

UID="u-prod-check"
FAKE={"uid":UID,"levels":9,"maxLevels":21,"total":5,"programs":[
  {"key":"reaction","level":4,"maxLevel":4,"courses":[
     {"game":"dodge","level":4,"maxLevel":4,"current":1350,"next":None,"best":1600},
     {"game":"catch","level":4,"maxLevel":4,"current":850,"next":None,"best":900}]},
  {"key":"spatial","level":2,"maxLevel":4,"courses":[
     {"game":"defender","level":2,"maxLevel":4,"current":640,"next":800,"best":640}]},
  {"key":"navigation","level":3,"maxLevel":4,"courses":[
     {"game":"maze","level":3,"maxLevel":4,"current":4,"next":5,"best":4}]},
  {"key":"resource","level":0,"maxLevel":4,"courses":[
     {"game":"racer","level":0,"maxLevel":4,"current":900,"next":3500,"best":900}]},
  {"key":"observation","level":0,"maxLevel":4,"courses":[
     {"game":"constellation","level":0,"maxLevel":4,"current":0,"next":1,"best":0}]}]}

with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":1440,"height":900})
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','vi');"
        "localStorage.setItem('astroq-user',%s);"
        "localStorage.setItem('astroq-training',%s);"
        % (json.dumps(json.dumps({"uid":UID,"name":"T","character":"raica"})),
           json.dumps(json.dumps(FAKE))))
    pg=ctx.new_page(); errs=[]; b4=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: b4.append(r.url) if r.status>=400 else None)
    pg.goto("https://astroq.org/games.html", wait_until="networkidle"); pg.wait_for_timeout(1500)

    certs=pg.eval_on_selector_all(".gcard .cert","e=>e.map(x=>x.textContent.trim())")
    ck("KHONG con huy hieu 'DA DAT'", not any("ĐÃ ĐẠT" in c for c in certs), str(certs))
    ck("moi the hien mot CAP", all("cấp" in c.casefold() for c in certs), str(certs))
    goals=pg.eval_on_selector_all(".gcard .nextgoal","e=>e.map(x=>x.textContent.trim())")
    ck("moi the noi ra viec tiep theo", len(goals)==6, str(len(goals)))
    ck("the chua toi da noi 'Con ... nua len Cap'",
       any("Còn" in g and "lên Cấp" in g for g in goals), str(goals[:2]))
    ck("the toi da MOI PHA KY LUC", any("phá kỷ lục" in g for g in goals), str(goals))
    ck("ho so hien dung so server (9/21)",
       "9" in pg.inner_text("#rec-n") and "21" in pg.inner_text("#rec-n"),
       pg.inner_text("#rec-n"))
    bars=pg.eval_on_selector_all(".gcard .lvbar i","e=>e.map(x=>x.style.width)")
    ck("thanh tien do khong vuot 100%",
       all(int((x or '0%').replace('%',''))<=100 for x in bars), str(bars))
    ck("0 loi trang", not errs, str(errs[:2]))
    ck("0 asset hong", not b4, str(b4[:3]))

    # So tren HUD: console doc phai ON DINH o moi do dai
    pg.goto("https://astroq.org/game-dodge.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".chip", timeout=10000)
    ws=[]
    for v in ["0","371","2371","13820"]:
        pg.evaluate("(v)=>{['score','dist','gem','best'].forEach(i=>{const e=document.getElementById(i); if(e) e.textContent=v;});}", v)
        pg.wait_for_timeout(60)
        ws.append(pg.eval_on_selector_all(".chip","e=>e.map(c=>Math.round(c.getBoundingClientRect().width))"))
    dw=max(max(c)-min(c) for c in zip(*ws)) if ws and ws[0] else 0
    ck("console doc: be rong chip KHONG doi theo do dai so", dw==0, f"lech {dw}px")
    b.close()
print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
