# -*- coding: utf-8 -*-
import sys, re, time, urllib.request
from playwright.sync_api import sync_playwright
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25)
    return r.status, r.headers.get("Content-Type",""), r.read().decode("utf-8","replace")
ok=bad=0
def ck(n,c,d=""):
    global ok,bad
    if c: ok+=1; print(f"  [OK]   {n}"+(f"  ({d})" if d else ""))
    else: bad+=1; print(f"  [HONG] {n}  {d}")

# [1] SO HIEU BAN DUNG — kiem TRUOC moi thu khac
ver=None
for i in range(24):
    try:
        _,_,t=get("https://astroq.org/js/ui-common.js?cb=%d"%time.time())
        m=re.search(r'VERSION\s*=\s*"([\d.]+)"',t); ver=m.group(1) if m else None
        if ver=="2026.08.14.6": break
    except Exception: pass
    time.sleep(10)
ck("ban dung tren Pages = 2026.08.14.6", ver=="2026.08.14.6", f"doc ra {ver}")
if ver!="2026.08.14.6":
    print("\n>>> Pages CHUA build xong — dung do."); sys.exit(1)

st,ct,tj=get("https://astroq.org/js/training.js")
ck("js/training.js 200 + MIME js", st==200 and "javascript" in ct, f"{st} {ct}")
ck("training.js KHONG lo con so moc nao cua server",
   not re.search(r"\b(200|120|150|14000)\b", re.sub(r"/\*.*?\*/"," ",tj,flags=re.S)), "")

with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":1440,"height":900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg=ctx.new_page(); errs=[]; b4=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: b4.append(r.url) if r.status>=400 else None)
    pg.goto("https://astroq.org/games.html", wait_until="networkidle"); pg.wait_for_timeout(1500)
    ck("hub-tag la TRAINING_CENTER", "TRAINING_CENTER" in pg.inner_text(".hub-tag"),
       pg.inner_text(".hub-tag"))
    tags=pg.eval_on_selector_all(".gcard .tag","e=>e.map(x=>x.textContent.trim())")
    ck("6 the deu mang ten chuong trinh", len(tags)==6 and all(t.strip() for t in tags),
       " | ".join(tags))
    ck("KHONG con nhan the loai kieu sanh game",
       not any(o in " | ".join(tags) for o in ["Giải đố","Đua tốc độ","Phòng thủ 360°"]),
       " | ".join(tags))
    ck("moi the co dong ky nang", pg.locator(".gcard .skill").count()==6)
    ck("moi the co duong doc bai", pg.locator(".gcard .readlink").count()==6)
    ck("bai doc KHONG khoa nut Choi ngay",
       not any(pg.eval_on_selector_all(".gcard .play-btn","e=>e.map(x=>x.disabled)")))
    ck("mo ta Duong Dua KHONG con con so 1.200 m",
       "1.200 m" not in pg.inner_text("#games") and "1,200 m" not in pg.inner_text("#games"))
    # chua dang nhap -> khoi ho so AN HAN, khong hien 0/5
    ck("chua dang nhap: khoi ho so an han", pg.locator("#record").count()==1
       and not pg.locator("#record").is_visible())
    ck("khong cho nao hien 0/5", not re.search(r"\b0\s*/\s*5\b", pg.inner_text("body")))
    ck("0 loi trang", not errs, str(errs[:2]))
    ck("0 asset hong", not b4, str(b4[:3]))
    # duong doc bai tro toi bai co that tren ban that
    href=pg.eval_on_selector(".gcard .readlink","e=>e.getAttribute('href')")
    with pg.expect_navigation(): pg.locator(".gcard .readlink").first.click()
    pg.wait_for_timeout(2500)
    ck("bam duong doc bai -> library.html mo dung bai", pg.locator("#reader.show").count()==1,
       pg.url)
    ck("than bai hien chu that", len(pg.inner_text("#r-body"))>200,
       f"{len(pg.inner_text('#r-body'))} ky tu")
    b.close()
print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
