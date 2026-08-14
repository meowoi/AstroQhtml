import sys, time, re, urllib.request
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25)
    return r.status, r.headers.get("Content-Type",""), r.read().decode("utf-8","replace")
ok=bad=0
def ck(n,c,d=""):
    global ok,bad
    if c: ok+=1; print(f"  [OK]   {n}")
    else: bad+=1; print(f"  [HONG] {n}  {d}")

# [1] SO HIEU BAN DUNG — kiem TRUOC moi thu khac
ver=None
for i in range(24):
    try:
        _,_,t=get("https://astroq.org/js/ui-common.js?cb=%d"%time.time())
        m=re.search(r'VERSION\s*=\s*"([\d.]+)"',t)
        ver=m.group(1) if m else None
        if ver=="2026.08.14.5": break
    except Exception: pass
    time.sleep(10)
ck("ban dung tren Pages = 2026.08.14.5", ver=="2026.08.14.5", f"doc ra {ver}")
if ver!="2026.08.14.5":
    print("\n>>> Pages CHUA build xong — dung do, moi ket luan sau deu sai.")
    sys.exit(1)

# [2] 7 file bai moi tra 200 + MIME dung
for f in ["art-four-forces-tug-of-war","art-newtons-three-laws","art-rockets-work-in-vacuum",
          "art-sunlight-into-electricity","art-rollout-solar-arrays",
          "art-solid-and-liquid-rocket-engines","art-life-support-recycles-water"]:
    st,ct,_=get(f"https://astroq.org/js/article/{f}.js")
    ck(f"{f}.js 200 + MIME js", st==200 and "javascript" in ct, f"{st} {ct}")

# [3] muc luc co du 67 bai + 2 bai da doi chu de
st,_,idx=get("https://astroq.org/js/articles-index.js")
ck("articles-index 200", st==200)
_n = len(re.findall(r'\bid:\s*"', idx))
ck("muc luc co 67 bai", _n == 67, str(_n))
ck("gravity da sang physics", 'id:"art-gravity-pulls-to-center",src:"NASA",cat:"physics"' in idx.replace(" ",""), "")
ck("light-shadow da sang physics", 'id:"art-light-and-shadow-space",src:"NASA",cat:"physics"' in idx.replace(" ",""), "")

# [4] Chromium tren CHINH astroq.org
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":1440,"height":900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg=ctx.new_page()
    errs=[]; b404=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: b404.append(r.url) if r.status>=400 else None)
    pg.goto("https://astroq.org/library.html", wait_until="networkidle"); pg.wait_for_timeout(2000)
    cats=pg.eval_on_selector_all("#cats .cat[data-cat]","e=>e.map(x=>x.dataset.cat)")
    ck("10 chip chu de", len(cats)==10, str(cats))
    ck("co chip physics + engineering", "physics" in cats and "engineering" in cats, str(cats))
    for c,n in [("physics",6),("engineering",3)]:
        pg.click(f"#cats .cat[data-cat='{c}']"); pg.wait_for_timeout(800)
        ids=pg.eval_on_selector_all("#grid .card","e=>e.map(x=>x.dataset.id)")
        ck(f"chip {c} ra dung {n} bai", len(ids)==n, str(ids))
    # mo bai ECLSS tren ban that
    pg.click("#cats .cat[data-cat='engineering']"); pg.wait_for_timeout(700)
    pg.click("#grid .card[data-id='art-life-support-recycles-water']"); pg.wait_for_timeout(2000)
    body=pg.inner_text("#r-body")
    ck("than bai ECLSS hien chu that", "ECLSS" in body and len(body)>400, body[:60])
    ck("KHONG lo con so 90% / Sabatier", "90%" not in body and "sabatier" not in body.lower())
    mb=pg.query_selector("#r-more")
    ck("khoi Mo rong hien tren ban that", mb is not None and mb.is_visible())
    ck("0 loi trang", not errs, str(errs[:2]))
    ck("0 asset hong", not b404, str(b404[:3]))
    b.close()
print(f"\n===== {ok} dat / {bad} hong =====")
