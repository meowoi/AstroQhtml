# -*- coding: utf-8 -*-
"""
verify_prod_0818.py - do BAN THAT sau khi push 18/08/2026.

⚠️⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC, va DUNG HAN neu sai. Do truoc luc
   Pages build xong thi moi ket luan phia sau deu sai — va 06/08/2026 ban that da
   tung dung o ban cu gan mot ngay ma khong ai biet.
"""
import json
import re
import sys
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
WANT_VER = "2026.08.18.1"
OK = FAIL = 0


def check(label, cond, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(extra)) if extra else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(extra))


def get(path):
    req = urllib.request.Request(SITE + path, headers={"User-Agent": "astroq-verify"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), b""


print("=== BAN THAT %s ===" % SITE)

# ---------------------------------------------------------- [0] so hieu ban dung
print("")
print("[0] So hieu ban dung")
st, _, body = get("/js/ui-common.js")
m = re.search(r'var VERSION\s*=\s*"([^"]+)"', body.decode("utf-8", "replace"))
got = m.group(1) if m else "?"
check("js/ui-common.js tra 200", st == 200, st)
check("ban dung dung %s" % WANT_VER, got == WANT_VER, got)
if got != WANT_VER:
    print("")
    print("  DUNG LAI: Pages chua build xong. Doi ~1 phut roi chay lai.")
    sys.exit(1)

# ------------------------------------------------------- [1] file moi + MIME
print("")
print("[1] File moi tra 200 va dung MIME")
# ⚠️ MIME phai DO chu khong duoc gia dinh: ES module bi tu choi neu server tra
#    text/plain, va anh sai MIME thi Facebook co the bo qua the og:image.
for path, want_mime in (("/js/utm.js", "javascript"),
                        ("/img/og/game-dodge.jpg", "image/jpeg"),
                        ("/img/og/crew.jpg", "image/jpeg"),
                        ("/img/og/mission-orbit.jpg", "image/jpeg")):
    st, ctype, raw = get(path)
    check("%-28s 200" % path, st == 200, st)
    check("%-28s MIME co '%s'" % (path, want_mime), want_mime in ctype, ctype)

# ------------------------------------------- [2] be mat bi cache DA SACH
print("")
print("[2] Be mat bi cache: khong con loi hua het han")
BAD = ["Sắp Ra Mắt", "sắp ra mắt", "dự kiến ra mắt", "vé mời sớm", "đăng ký sớm",
       "trước ngày ra mắt", "thông báo ra mắt", "PRE-LAUNCH", "Launching",
       "scheduled to launch", "early-access", "early access", "Early Access"]
for path in ("/", "/en/"):
    st, _, raw = get(path)
    html = raw.decode("utf-8", "replace")
    check("%-6s tra 200" % path, st == 200, st)
    head = html[:html.index("</head>")] if "</head>" in html else html
    hits = sorted({b for b in BAD if b in head})
    check("%-6s <head> SACH" % path, not hits, hits)
    hits2 = sorted({b for b in BAD if b in html})
    check("%-6s ca trang SACH" % path, not hits2, hits2)
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    print("        title = " + (t.group(1).strip() if t else "?"))

# ⚠️ Ngay ra mat PHAI CON o FAQ — bo khung thoi gian khong phai bo ngay.
st, _, raw = get("/")
html = raw.decode("utf-8", "replace")
check("ngay 20/08/2026 VAN con o FAQ (2 cho: JSON-LD + doan hien ra)",
      html.count("20/08/2026") == 2, html.count("20/08/2026"))

# --------------------------------------------- [3] the chia se tro vao anh CO THAT
print("")
print("[3] The chia se: moi og:image tro vao anh CO THAT")
PAGES = ["games.html", "lab.html", "crew.html", "mission-earth.html", "mission-orbit.html",
         "game-dodge.html", "game-defender.html", "game-constellation.html",
         "game-racer.html", "game-maze.html", "game-catch.html", "game-survival.html",
         "game-comms.html", "game-recycle.html", "game-units.html"]
missing, noblock = [], []
for pg in PAGES:
    st, _, raw = get("/" + pg)
    h = raw.decode("utf-8", "replace")
    if "<!-- OG:BEGIN" not in h:
        noblock.append(pg)
        continue
    m = re.search(r'property="og:image" content="(https://astroq\.org/[^"]+)"', h)
    if not m:
        missing.append(pg + " (thieu the)")
        continue
    ist, ictype, _ = get(m.group(1)[len(SITE):])
    if ist != 200:
        missing.append("%s -> %s (%s)" % (pg, m.group(1), ist))
check("ca 15 trang co khoi OG", not noblock, noblock)
# ⚠️ Phep kiem dang gia nhat: thieu anh thi Facebook hien the RONG ma KHONG co gi
#    bao loi — trang van mo, console sach, chi nguoi la thay mot o xam.
check("moi og:image tai ve duoc 200", not missing, missing[:3])

# --------------------------------------------------- [4] mo trang that tren Chromium
print("")
print("[4] Mo tren Chromium that")
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh",
                         viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    pg = ctx.new_page()
    errs, bad404 = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad404.append(r.url) if r.status >= 400 else None)

    # ⚠️ Vao bang link CO NHAN CHIEN DICH — do dung thu se dan len fanpage.
    pg.goto(SITE + "/?utm_source=fb&utm_medium=post&utm_campaign=ra-mat-20-08",
            wait_until="domcontentloaded")
    pg.wait_for_timeout(1200)
    check("trang chu: 0 loi trang", not errs, errs[:2])
    check("trang chu: 0 asset hong", not bad404, bad404[:3])
    check("AstroQUtm co mat tren ban that", pg.evaluate("() => !!window.AstroQUtm"))
    check("bat dung nhan chien dich",
          pg.evaluate("() => AstroQUtm.get()") == "fb/post/ra-mat-20-08",
          pg.evaluate("() => AstroQUtm.get()"))
    check("CTA da doi sang loi van khong het han",
          "500 Purple Meteors" in pg.inner_text("#hero-wl"), pg.inner_text("#hero-wl"))
    # ⚠️ Dong ho phai CON DEM — bo chu "sap ra mat" khong duoc lam hong co che mo cua.
    d = pg.inner_text("#cd-d") if pg.query_selector("#cd-d") else "?"
    check("dong ho dem nguoc van chay", d.strip().isdigit(), "con %s ngay" % d.strip())

    # Giu luot cham dau tien khi vao lai bang link khac
    pg.goto(SITE + "/?utm_source=zalo&utm_campaign=bai-khac", wait_until="domcontentloaded")
    pg.wait_for_timeout(600)
    check("giu LUOT CHAM DAU TIEN tren ban that",
          pg.evaluate("() => AstroQUtm.get()") == "fb/post/ra-mat-20-08",
          pg.evaluate("() => AstroQUtm.get()"))

    # Mot trang game: the OG + khong loi
    errs.clear(); bad404.clear()
    pg.goto(SITE + "/game-dodge.html", wait_until="domcontentloaded")
    pg.wait_for_timeout(900)
    check("game-dodge: 0 loi trang", not errs, errs[:2])
    og = pg.get_attribute('meta[property="og:image"]', "content")
    check("game-dodge co og:image tuyet doi", (og or "").startswith("https://"), og)

    # lab.html: da mo free
    errs.clear()
    pg.goto(SITE + "/lab.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".lcard", timeout=15000)
    check("lab: KHONG the nao mang nhan tra phi",
          pg.locator(".lcard .lc-tag.pro").count() == 0,
          pg.locator(".lcard .lc-tag.pro").count())
    check("lab: 0 duong dan sang pricing.html",
          pg.locator("a[href$='pricing.html']").count() == 0)
    check("huy hieu ban dung hien dung so", WANT_VER in pg.inner_text(".ver-badge"),
          pg.inner_text(".ver-badge"))
    br.close()

print("")
print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
