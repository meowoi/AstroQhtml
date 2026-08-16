# -*- coding: utf-8 -*-
"""Do C2 tren BAN THAT sau khi Pages build."""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SITE = "https://astroq.org"
WANT = "2026.08.16.4"
ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def get(p):
    r = urllib.request.Request(SITE + p, headers={"User-Agent": "astroq-verify"})
    with urllib.request.urlopen(r, timeout=30) as x:
        return x.status, x.headers.get("Content-Type", ""), x.read()


print(f"=== C2 tren {SITE} ===\n[1] So hieu ban dung")
_, _, uc = get("/js/ui-common.js")
m = re.search(r'VERSION\s*=\s*"([\d.]+)"', uc.decode("utf-8", "replace"))
check(f"ban dung = {WANT}", m and m.group(1) == WANT, m.group(1) if m else "?")
if not m or m.group(1) != WANT:
    print("\n⚠️ Pages CHUA build xong — dung o day.")
    sys.exit(1)

print("\n[2] 6 anh linh vat tra 200")
tot = 0
for f in ("byte-idle", "byte-cheer", "byte-oops",
          "comet-idle", "comet-cheer", "comet-oops"):
    try:
        st, ct, body = get(f"/img/mate/{f}.png")
    except Exception as e:
        st, ct, body = 0, str(e), b""
    tot += len(body)
    check(f"/img/mate/{f}.png", st == 200 and "image/png" in ct,
          f"{st} · {len(body):,} byte")
check("tong bo anh nho gon", tot < 120_000, f"{tot:,} byte")

GAMES = ["game-dodge", "game-defender", "game-constellation", "game-racer",
         "game-maze", "game-catch", "game-survival", "game-comms",
         "game-recycle", "game-units"]

with sync_playwright() as pw:
    br = pw.chromium.launch()

    print("\n[3] Ca 10 game tren ban that deu co ban dong hanh")
    for g in GAMES:
        ctx = br.new_context(viewport={"width": 1500, "height": 950})
        pg = ctx.new_page()
        errs, bad_as = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad_as.append(r.url) if r.status >= 400 else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');"
                           "localStorage.setItem('astroq-asteroids','60');")
        pg.goto(f"{SITE}/{g}.html", wait_until="load")
        pg.wait_for_timeout(900)
        s = pg.evaluate("""() => {
          const el = document.querySelector('.gs-mate');
          if (!el) return null;
          const i = el.querySelector('img');
          return { src:(i.currentSrc||i.src).split('/').pop(),
                   w: Math.round(i.getBoundingClientRect().width) }; }""")
        check(f"{g}: co linh vat", bool(s) and s["w"] == 104, str(s))
        check(f"{g}: 0 loi trang / 0 asset hong", not errs and not bad_as,
              str((errs[:1], bad_as[:1]))[:110])
        ctx.close()

    print("\n[4] Choi that tren ban that — Tram Doi Chieu")
    ctx = br.new_context(viewport={"width": 1500, "height": 950})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("localStorage.setItem('astroq-lang','vi');"
                       "localStorage.setItem('astroq-asteroids','60');")
    pg.goto(f"{SITE}/game-units.html", wait_until="load")
    pg.wait_for_selector("#ov-start.show", timeout=15000)
    pg.click("#start-btn"); pg.wait_for_timeout(500)
    bad = pg.evaluate("() => window.__dbg.bad()")
    for i, x in enumerate(bad):
        if x:
            pg.locator('.uc-row[data-i="%d"]' % i).click(); pg.wait_for_timeout(60)
    pg.click("#ok"); pg.wait_for_timeout(250)
    src = pg.evaluate("""() => { const i=document.querySelector('.gs-mate img');
      return (i.currentSrc||i.src).split('/').pop(); }""")
    check("duyet DUNG -> Byte mung", src == "byte-cheer.png", src)
    check("0 loi trang", not errs, str(errs[:1])[:110])
    ctx.close()
    br.close()

print("\n" + "=" * 54)
print(f"KET QUA: {ok_n} dat / {bad_n} hong")
sys.exit(0 if bad_n == 0 else 1)
