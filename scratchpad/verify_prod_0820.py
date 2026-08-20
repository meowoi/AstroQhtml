# -*- coding: utf-8 -*-
"""
verify_prod_0820.py — do BAN THAT tren astroq.org sau lan push 20/08/2026.

    python scratchpad/verify_prod_0820.py

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC, va DUNG HAN neu sai: do truoc luc
   Pages build xong thi moi ket luan deu sai, va ngay 06/08/2026 ban that da tung
   dung o ban cu gan mot ngay.
⚠️ Do MIME cua file .js: ES module bi tu choi neu server tra `text/plain`, nen
   day la thu phai DO chu khong duoc gia dinh.
"""
import io
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
WANT_VER = "2026.08.20.1"
OK = FAIL = 0


def check(label, cond, detail=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(detail)) if detail else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(detail))


def get(path):
    req = urllib.request.Request(SITE + path,
                                 headers={"User-Agent": "astroq-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")


print("")
print("  DO BAN THAT " + SITE)
print("=" * 66)

# ── [0] so hieu ban dung — chan cung ─────────────────────────────────────
st, _, ui = get("/js/ui-common.js")
have = ui.split('var VERSION = "')[1].split('"')[0] if 'var VERSION = "' in ui else "?"
check("so hieu ban dung dung " + WANT_VER, have == WANT_VER, have)
if have != WANT_VER:
    print("")
    print("  ⚠️ Pages CHUA build xong. Dung han — do tiep la ket luan sai.")
    sys.exit(1)

# ── [1] file moi tra 200 voi MIME dung ───────────────────────────────────
print("")
print("[1] file moi")
st, ct, js = get("/js/pw-toggle.js")
check("js/pw-toggle.js tra 200", st == 200, str(st))
check("MIME la javascript (ES module bi tu choi neu text/plain)",
      "javascript" in ct, ct)
# Quet tren MA DA BOC CHU THICH: khoi chu thich cua file co y minh hoa
# markup (co ca hai nhan) — dem ca chu trong ghi chu cua chinh minh la
# cai bay CLAUDE.md da ghi rat nhieu lan.
import re as _re
_code = _re.sub(r"/\*.*?\*/", "", js, flags=_re.S)
_code = _re.sub(r"//[^\n]*", "", _code)
check("khong lo mot chuoi VI/EN nao trong MA (chu thich khong tinh)",
      ("Hiện" not in _code) and ("Show password" not in _code)
      and ("Ẩn" not in _code) and ("Hide password" not in _code))
req = urllib.request.Request(SITE + "/img/og-cover-v2.jpg",
                             headers={"User-Agent": "astroq-verify"})
with urllib.request.urlopen(req, timeout=30) as r:
    n = len(r.read())
    check("img/og-cover-v2.jpg tra 200", r.status == 200, "%d byte" % n)
    check("anh duoi 200 KB", n < 200000, "%d byte" % n)
# anh cu GIU tren dia de bai da chia se khong 404
try:
    with urllib.request.urlopen(
            urllib.request.Request(SITE + "/img/og-cover.jpg",
                                   headers={"User-Agent": "astroq-verify"}),
            timeout=30) as r:
        check("anh OG CU van con (bai da chia se khong 404)", r.status == 200)
except Exception as ex:
    check("anh OG CU van con (bai da chia se khong 404)", False, str(ex))

# ── [2] trang chu ban VI ─────────────────────────────────────────────────
print("")
print("[2] trang chu ban VI")
st, _, vi = get("/")
check("wl_tag noi dung muc qua moi",
      "QUÀ KHỞI ĐẦU · 100 PURPLE METEORS" in vi, "")
check("khong con chu 500 PURPLE METEORS", "500 PURPLE METEORS" not in vi)
check("khong con the <form> nao", "<form" not in vi.lower())
check("khong con bay bot honeypot", "wl-gotcha" not in vi)
check("og:image tro ban v2", "og-cover-v2.jpg" in vi)
check("khong con tro og-cover.jpg (Facebook cache theo URL)",
      'content="https://astroq.org/img/og-cover.jpg"' not in vi)
check("CTA la <a> chu khong <button>",
      'href="landing-app.html"' in vi)

st, _, ijs = get("/js/index.js")
check("openDoor gan .live vao dong ho", 'classList.add("live")' in ijs)
check("da bo submitWaitlist", "submitWaitlist" not in ijs)

# ── [3] trang chu ban EN ─────────────────────────────────────────────────
print("")
print("[3] trang chu ban EN")
st, _, en = get("/en/")
check("nut Play now tro dung ../landing-app.html",
      'href="../landing-app.html"' in en)
check("khong con duong dan TRANG con o goc (se 404 tu /en/)",
      'href="landing-app.html"' not in en)
check("og:image tro ban v2", "og-cover-v2.jpg" in en)
check("khong con the <form> nao", "<form" not in en.lower())

# ── [4] wiki noi dung muc moi ────────────────────────────────────────────
print("")
print("[4] wiki")
st, _, w = get("/wiki/purple-meteors-hoat-dong.html")
check("wiki noi 100 Purple Meteors", "100 Purple Meteors" in w)
check("wiki khong con nhac muc 500", "500 Purple Meteors" not in w)
check("wiki tro anh OG v2", "og-cover-v2.jpg" in w)

# ── [5] mo THAT tren Chromium ────────────────────────────────────────────
print("")
print("[5] mo that tren Chromium")
with sync_playwright() as p:
    br = p.chromium.launch()
    for path, label in (("/", "trang chu VI"), ("/en/", "trang chu EN")):
        ctx = br.new_context(viewport={"width": 1280, "height": 900})
        pg = ctx.new_page()
        errs, bad, ext = [], [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad.append(r.url) if r.status >= 400 else None)
        pg.on("request", lambda r: ext.append(r.url)
              if ("astroq.org" not in r.url and not r.url.startswith("data:")
                  and "fonts.g" not in r.url) else None)
        pg.goto(SITE + path, wait_until="load")
        pg.wait_for_timeout(1200)
        print("  --- " + label + " ---")
        check("0 loi trang", not errs, str(errs[:2]))
        check("0 asset hong", not bad, str(bad[:2]))
        # Trang chu la trang DUY NHAT duoc lap chi muc va co y khong goi mang.
        check("0 loi goi ra ten mien ngoai", not ext, str(ext[:2]))
        check("dong ho da o trang thai DA MO CUA (.countdown.live)",
              pg.locator(".countdown.live").count() == 1)
        check("khong con o nhap email nao",
              pg.locator('input[type="email"]').count() == 0)
        ctx.close()

    # nut an/hien mat khau tren BAN THAT
    ctx = br.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(SITE + "/landing-app.html", wait_until="load")
    print("  --- landing-app.html (nut an/hien mat khau) ---")
    pg.click("#btn-try")
    pg.wait_for_selector("#auth-overlay.show", timeout=10000)
    inp = pg.locator("#reg-pass")
    btn = pg.locator('[data-pw-toggle="reg-pass"]')
    inp.fill("vycatcute")
    check("khoi dau type=password", inp.get_attribute("type") == "password")
    pr = inp.evaluate("el => parseFloat(getComputedStyle(el).paddingRight)")
    bb = btn.bounding_box()
    check("chu KHONG chay duoi nut (padding-right >= be rong nut)",
          pr >= bb["width"] - 1, "padding %.0f vs nut %.0f" % (pr, bb["width"]))
    btn.click()
    check("bam -> hien mat khau", inp.get_attribute("type") == "text")
    check("gia tri khong bi mat", inp.input_value() == "vycatcute")
    check("aria-pressed lat", btn.get_attribute("aria-pressed") == "true")
    check("lop phu con mo (nut khong submit bieu mau)",
          pg.locator("#auth-overlay.show").count() == 1)
    check("0 loi trang", not errs, str(errs[:2]))
    ctx.close()
    br.close()

print("")
print("-" * 66)
print("  KET QUA: %d dat / %d hong" % (OK, FAIL))
print("-" * 66)
print("")
sys.exit(1 if FAIL else 0)
