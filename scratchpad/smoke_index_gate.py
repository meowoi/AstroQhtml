# -*- coding: utf-8 -*-
"""
smoke_index_gate.py — CONG DAY NGUOI DA DANG NHAP tu trang chu sang cua vao app.

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       PYTHONIOENCODING=utf-8 python scratchpad/smoke_index_gate.py

⚠️ Phep kiem QUAN TRONG NHAT khong phai "nguoi da dang nhap co bi day khong"
   ma la 4 nhanh O LAI: khach la · crawler (khong co uid) · neo #hash ·
   den tu chinh site. Nhanh day thi de dung; chinh 4 nhanh kia moi la thu
   giu cho `/` con la trang duy nhat duoc lap chi muc.
"""
import sys, io, re, pathlib
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "http://127.0.0.1:8123"
ROOT = pathlib.Path(__file__).resolve().parent.parent

dat = hong = 0
def chk(name, ok, info=""):
    global dat, hong
    if ok: dat += 1; print(f"  [OK]   {name}" + (f"  ({info})" if info else ""))
    else:  hong += 1; print(f"  [HONG] {name}" + (f"  ({info})" if info else ""))

USER_REAL  = '{"name":"Bin","uid":"u-abc123","email":"a@b.c","character":"sirius"}'
USER_DEMO  = '{"name":"Bin","email":"a@b.c"}'          # thoi demo: KHONG co uid

def seed(ctx, user=None, extra=""):
    """Gieo localStorage TRUOC khi trang chay (init script chay o moi lan dieu huong)."""
    js = 'try{localStorage.setItem("astroq-lang","vi");'
    if user: js += f'localStorage.setItem("astroq-user",{user!r});'
    else:    js += 'localStorage.removeItem("astroq-user");'
    js += extra + '}catch(e){}'
    ctx.add_init_script(js)

def go(pg, url, referer=None):
    """⚠️ Dat Referer bang THAM SO cua goto(), KHONG bang set_extra_http_headers:
       cach kia lam Chromium huy ca lenh dieu huong (chrome-error://chromewebdata/)
       va doc ra y het mot loi san pham."""
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    opt = {"wait_until": "load"}
    if referer: opt["referer"] = referer
    pg.goto(url, **opt)
    pg.wait_for_timeout(500)
    return errs

with sync_playwright() as p:
    br = p.chromium.launch()

    # ---------------------------------------------------------------- [1]
    print("\n[1] KHACH LA (chua dang nhap) -> O LAI trang chu")
    ctx = br.new_context(); seed(ctx, None); pg = ctx.new_page()
    errs = go(pg, BASE + "/index.html")
    chk("o lai `/`", pg.url.rstrip("/").endswith("index.html") or pg.url.rstrip("/") == BASE,
        pg.url)
    chk("0 loi trang", not errs, "; ".join(errs[:2]))
    chk("van thay khoi FAQ (noi dung tiep thi)", pg.locator("#what-is").count() > 0)
    ctx.close()

    # ---------------------------------------------------------------- [2]
    print("\n[2] HO SO THOI DEMO (khong co uid) -> O LAI")
    ctx = br.new_context(); seed(ctx, USER_DEMO); pg = ctx.new_page()
    errs = go(pg, BASE + "/index.html")
    chk("khong bi day", "landing-app" not in pg.url, pg.url)
    chk("0 loi trang", not errs, "; ".join(errs[:2]))
    ctx.close()

    # ---------------------------------------------------------------- [3]
    print("\n[3] DA DANG NHAP THAT (co uid) -> DAY sang landing-app.html")
    ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
    errs = go(pg, BASE + "/index.html")
    chk("da sang landing-app.html", pg.url.endswith("/landing-app.html"), pg.url)
    chk("0 loi trang", not errs, "; ".join(errs[:2]))
    ctx.close()

    # ---------------------------------------------------------------- [4]
    print("\n[4] DA DANG NHAP + neo #hash -> O LAI (link nguoi khac gui)")
    for h in ("#waitlist", "#what-is"):
        ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
        go(pg, BASE + "/index.html" + h)
        chk(f"o lai voi {h}", "landing-app" not in pg.url, pg.url)
        ctx.close()

    # ---------------------------------------------------------------- [5]
    print("\n[5] DA DANG NHAP + ?stay -> O LAI (cua thoat thu cong)")
    ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
    go(pg, BASE + "/index.html?stay")
    chk("o lai voi ?stay", "landing-app" not in pg.url, pg.url)
    ctx.close()
    ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
    go(pg, BASE + "/index.html?utm_source=fb&stay=1")
    chk("o lai voi ?utm_source=fb&stay=1", "landing-app" not in pg.url, pg.url)
    ctx.close()

    # ---------------------------------------------------------------- [6]
    print("\n[6] DA DANG NHAP + den tu CHINH SITE -> O LAI")
    ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
    go(pg, BASE + "/index.html", referer=BASE + "/pricing.html")
    chk("referer cung host -> o lai", "landing-app" not in pg.url, pg.url)
    ctx.close()

    print("\n[6b] DA DANG NHAP + den tu NGOAI (google) -> DAY")
    ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
    go(pg, BASE + "/index.html", referer="https://www.google.com/")
    chk("referer ngoai -> day", pg.url.endswith("/landing-app.html"), pg.url)
    ctx.close()

    # ---------------------------------------------------------------- [7]
    print("\n[7] KHONG BAY LICH SU (location.replace, khong phai href)")
    ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
    pg.goto(BASE + "/pricing.html", wait_until="load")
    pg.goto(BASE + "/index.html", wait_until="load")   # referer rong -> bi day
    pg.wait_for_timeout(600)
    chk("da bi day", pg.url.endswith("/landing-app.html"), pg.url)
    pg.go_back(); pg.wait_for_timeout(600)
    # ⚠️ DO DUOC 20/08/2026: phep kiem nay KHONG phan biet duoc `replace` voi
    #    `href` — Chrome coi cu dieu huong phat ra khi trang con dang tai la mot
    #    phep thay the, nen ca hai deu cho `history.length` 3 va Quay-lai ve dung
    #    `pricing.html`. Giu lai vi no van canh dung dieu can canh (khong co bay
    #    lich su), chi dung tuong no la phep thu cho `replace` — cho do la muc
    #    [10]. Doi DUNG `pricing.html` chu khong chi "khong phai index.html".
    chk("Quay-lai ve dung trang truoc do (khong bay)",
        pg.url.endswith("/pricing.html"), pg.url)
    ctx.close()

    # ---------------------------------------------------------------- [8]
    print("\n[8] BAN /en/ — day ve `/landing-app.html`, KHONG phai /en/landing-app.html")
    ctx = br.new_context(); seed(ctx, USER_REAL); pg = ctx.new_page()
    errs = go(pg, BASE + "/en/index.html", referer="https://www.google.com/")
    chk("day dung goc site", pg.url.endswith("/landing-app.html"), pg.url)
    chk("KHONG roi vao /en/landing-app.html", "/en/landing-app" not in pg.url, pg.url)
    ctx.close()

    # ---------------------------------------------------------------- [9]
    print("\n[9] localStorage bi khoa -> KHONG duoc lam chet trang")
    ctx = br.new_context()
    ctx.add_init_script("""
      try{ Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}}); }catch(e){}
    """)
    pg = ctx.new_page()
    errs = go(pg, BASE + "/index.html")
    chk("o lai `/`", "landing-app" not in pg.url, pg.url)
    chk("dong ho dem nguoc van chay", pg.locator("#cd-d").count() > 0)
    ctx.close()

    # --------------------------------------------------------------- [10]
    print("\n[10] KIEM MA NGUON — nhung dieu grep tra loi duoc")
    gate = (ROOT / "js" / "index-gate.js").read_text(encoding="utf-8")
    idx  = (ROOT / "index.html").read_text(encoding="utf-8")
    en   = (ROOT / "en" / "index.html").read_text(encoding="utf-8")
    # bo comment de khong dem chu trong chinh ghi chu cua minh
    code = re.sub(r"/\*.*?\*/", "", gate, flags=re.S)
    code = re.sub(r"^\s*//.*$", "", code, flags=re.M)

    chk("dung location.replace (khong phai href=)",
        "location.replace(" in code and "location.href" not in code)
    chk("KHONG go cung 'landing-app.html' truc tiep",
        not re.search(r'["\']landing-app\.html["\']', code),
        "phai suy tu currentScript")
    chk("suy duong dan tu document.currentScript", "document.currentScript" in code)
    chk("doi uid (khong nhan ho so thoi demo)", "u.uid" in code)
    chk("bo qua khi co location.hash", "location.hash" in code)
    chk("co cua thoat ?stay", "stay" in code)
    chk("bo qua khi referer cung host", "location.host" in code)
    chk("boc try/catch (khong lam chet trang chu)", code.count("try") >= 1 and "catch" in code)
    chk("`/` nap gate SAU ui-common.js",
        idx.index("js/index-gate.js") > idx.index("js/ui-common.js"))
    chk("`/` nap gate SAU utm.js (kip ghi nguon chien dich)",
        idx.index("js/index-gate.js") > idx.index("js/utm.js"))
    chk("`/en/` co gate voi duong dan ../js/", '../js/index-gate.js' in en)
    chk("`/` va `/en/` deu chi nap DUNG 1 lan",
        idx.count("index-gate.js") == 1 and en.count("index-gate.js") == 1)

    br.close()

print(f"\n{'='*56}\nKET QUA: {dat} dat / {hong} hong\n{'='*56}")
sys.exit(1 if hong else 0)
