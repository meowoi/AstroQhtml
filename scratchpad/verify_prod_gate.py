# -*- coding: utf-8 -*-
"""
verify_prod_gate.py — do CONG DAY NGUOI DA DANG NHAP tren BAN THAT astroq.org.

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC va DUNG HAN neu sai: Pages build mat
   ~1 phut, va 06/08/2026 ban that da tung dung o ban cu gan mot ngay. Do truoc
   luc build xong thi moi ket luan deu sai.
"""
import sys, io, re, urllib.request
from playwright.sync_api import sync_playwright

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SITE = "https://astroq.org"
WANT = "2026.08.20.5"
USER = '{"name":"Bin","uid":"u-abc123","email":"a@b.c","character":"sirius"}'
DEMO = '{"name":"Bin","email":"a@b.c"}'

dat = hong = 0
def chk(n, ok, info=""):
    global dat, hong
    if ok: dat += 1; print(f"  [OK]   {n}" + (f"  ({info})" if info else ""))
    else:  hong += 1; print(f"  [HONG] {n}" + (f"  ({info})" if info else ""))

def get(url):
    r = urllib.request.urlopen(urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}), timeout=25)
    return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")

print("[0] SO HIEU BAN DUNG (kiem TRUOC moi thu khac)")
_, _, ui = get(SITE + "/js/ui-common.js")
have = ui.split('var VERSION = "')[1].split('"')[0] if 'var VERSION = "' in ui else "??"
if have != WANT:
    print(f"  [HONG] ban dung {have}, doi {WANT} — Pages CHUA build xong. DUNG.")
    sys.exit(1)
chk("ban dung dung " + WANT, True)

print("\n[1] FILE MOI tra 200 + MIME dung")
st, ct, gate = get(SITE + "/js/index-gate.js")
chk("js/index-gate.js: 200", st == 200, str(st))
# ⚠️ MIME phai la javascript that. Server tra `text/plain` thi trinh duyet van
#    chay duoc script co dien, nhung day la thu phai DO chu khong duoc gia dinh.
chk("js/index-gate.js: MIME javascript", "javascript" in ct, ct)
# ⚠️ BOC CHU THICH TRUOC KHI TIM. Chinh khoi ghi chu cua file do viet
#    'KHONG DUOC GO CUNG "landing-app.html"', nen quet tren van ban tho la bao
#    vi pham oan — loi "dem ca chu trong ghi chu cua chinh minh", da lap rat
#    nhieu lan trong du an. `check_pages` muc [36] da bóc comment tu dau.
_gc = re.sub(r"/\*.*?\*/", "", gate, flags=re.S)
_gc = re.sub(r"^\s*//.*$", "", _gc, flags=re.M)
chk("gate: KHONG go cung landing-app.html",
    not re.search(r'["\']landing-app\.html["\']', _gc))
chk("gate: suy tu currentScript", "document.currentScript" in _gc)
chk("gate: doi uid", "u.uid" in _gc)

print("\n[2] HAI BAN TRANG CHU nap gate dung do sau")
for path, pre in (("/", "js/"), ("/en/", "../js/")):
    _, _, html = get(SITE + path)
    chk(f"{path}: nap {pre}index-gate.js", f'{pre}index-gate.js' in html)
    chk(f"{path}: dung 1 lan", html.count("index-gate.js") == 1)

print("\n[3] CHAY THAT tren astroq.org")
with sync_playwright() as p:
    br = p.chromium.launch()

    def open_(user, url, referer=None, extra=""):
        ctx = br.new_context()
        js = 'try{localStorage.setItem("astroq-lang","vi");'
        js += (f'localStorage.setItem("astroq-user",{user!r});' if user
               else 'localStorage.removeItem("astroq-user");') + extra + '}catch(e){}'
        ctx.add_init_script(js)
        pg = ctx.new_page(); errs = []; bad = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad.append(f"{r.status} {r.url}")
              if r.status >= 400 else None)
        opt = {"wait_until": "load", "timeout": 45000}
        if referer: opt["referer"] = referer
        pg.goto(url, **opt); pg.wait_for_timeout(1200)
        return ctx, pg, errs, bad

    # -- khach la: o lai, va trang chu con nguyen noi dung tiep thi
    ctx, pg, errs, bad = open_(None, SITE + "/")
    chk("khach la: o lai trang chu", "landing-app" not in pg.url, pg.url)
    chk("khach la: 0 loi trang", not errs, "; ".join(errs[:2]))
    chk("khach la: 0 asset hong", not bad, "; ".join(bad[:2]))
    chk("khach la: van thay khoi AEO", pg.locator("#what-is").count() > 0)
    ctx.close()

    # -- ho so thoi demo (khong uid): o lai
    ctx, pg, _, _ = open_(DEMO, SITE + "/")
    chk("ho so demo: KHONG bi day", "landing-app" not in pg.url, pg.url)
    ctx.close()

    # -- da dang nhap, den tu ngoai: bi day
    ctx, pg, errs, _ = open_(USER, SITE + "/", referer="https://www.google.com/")
    chk("da dang nhap: day sang /landing-app.html",
        pg.url.rstrip("/").endswith("astroq.org/landing-app.html"), pg.url)
    chk("da dang nhap: 0 loi trang", not errs, "; ".join(errs[:2]))
    ctx.close()

    # -- BAN /en/: phai ve GOC site, khong phai /en/landing-app.html (404)
    ctx, pg, _, bad = open_(USER, SITE + "/en/", referer="https://www.google.com/")
    chk("/en/: day ve goc site",
        pg.url.rstrip("/").endswith("astroq.org/landing-app.html"), pg.url)
    chk("/en/: KHONG roi vao /en/landing-app.html", "/en/landing-app" not in pg.url)
    chk("/en/: 0 asset hong (khong 404)", not bad, "; ".join(bad[:2]))
    ctx.close()

    # -- ba nhanh O LAI con lai
    for tag, url, ref in (("#waitlist", SITE + "/#waitlist", None),
                          ("?stay",     SITE + "/?stay",     None),
                          ("referer cung site", SITE + "/", SITE + "/pricing.html")):
        ctx, pg, _, _ = open_(USER, url, referer=ref)
        chk(f"o lai voi {tag}", "landing-app" not in pg.url, pg.url)
        ctx.close()

    br.close()

print(f"\n{'='*56}\nKET QUA: {dat} dat / {hong} hong\n{'='*56}")
sys.exit(1 if hong else 0)
