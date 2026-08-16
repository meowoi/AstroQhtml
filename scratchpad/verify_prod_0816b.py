# -*- coding: utf-8 -*-
"""Do ARCADE-10 tren BAN THAT sau khi Pages build.

    python scratchpad/verify_prod_0816b.py

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC — do truoc luc Pages build xong thi
   moi ket luan deu sai (06/08/2026 ban that da tung dung o ban cu gan mot ngay).
"""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SITE = "https://astroq.org"
WANT_VER = "2026.08.16.2"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def get(path):
    req = urllib.request.Request(SITE + path, headers={"User-Agent": "astroq-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")


def main():
    print(f"=== ARCADE-10 tren {SITE} ===\n")

    print("[1] So hieu ban dung")
    _, _, uc = get("/js/ui-common.js")
    m = re.search(r'VERSION\s*=\s*"([\d.]+)"', uc)
    check(f"ban dung = {WANT_VER}", m and m.group(1) == WANT_VER,
          m.group(1) if m else "khong doc duoc")
    if not m or m.group(1) != WANT_VER:
        print("\n⚠️ Pages CHUA build xong — dung o day.")
        return 1

    print("\n[2] File moi tra 200 + MIME dung")
    for p, want in [("/game-units.html", "text/html"),
                    ("/css/game-units.css", "text/css"),
                    ("/js/sticker-icons.js", "javascript")]:
        try:
            st, ct, _ = get(p)
        except Exception as e:
            st, ct = 0, str(e)
        check(p, st == 200 and want in ct, f"{st} · {ct}")

    print("\n[3] Phi vao cua khop giua client va the")
    _, _, econ = get("/economy.js")
    _, _, gp = get("/game-units.html")
    fee = re.search(r"units\s*:\s*(\d+)", econ)
    cost = re.search(r"COST\s*:\s*(\d+)", gp)
    check("economy.js co phi units", bool(fee), fee.group(1) if fee else "-")
    check("CONFIG.COST khop economy.js",
          fee and cost and fee.group(1) == cost.group(1),
          f"{cost and cost.group(1)} vs {fee and fee.group(1)}")

    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("\n[4] games.html — 10 the, 0 the khoa")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        errs, bad_assets = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad_assets.append(r.url) if r.status >= 400 else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(SITE + "/games.html", wait_until="networkidle")
        n = pg.locator(".gcard").count()
        check("du 10 the game", n == 10, str(n))
        check("0 the khoa", pg.locator(".gcard.soon, .gcard [disabled]").count() == 0)
        check("co the Tram Doi Chieu", "Trạm Đối Chiếu" in pg.inner_text("body"))
        # Icon sticker moi phai VE RA THAT, khong phai mot o SVG rong.
        drawn = pg.evaluate("""() => {
          const c = [...document.querySelectorAll('.gcard')]
            .find(e => e.textContent.includes('Trạm Đối Chiếu'));
          const s = c && c.querySelector('svg.sic');
          return s ? s.querySelectorAll('path,circle,rect,ellipse').length : 0;
        }""")
        check("icon `ruler` ve ra that", drawn >= 4, f"{drawn} hinh")
        check("0 loi trang", not errs, str(errs[:1])[:120])
        check("0 asset hong", not bad_assets, str(bad_assets[:2])[:160])
        ctx.close()

        print("\n[5] Choi that mot bang tren ban that")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        errs, bad_assets = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad_assets.append(r.url) if r.status >= 400 else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');"
                           "localStorage.setItem('astroq-asteroids','40');")
        pg.goto(SITE + "/game-units.html", wait_until="load")
        pg.wait_for_selector("#ov-start.show", timeout=15000)
        check("nhan MO PHONG hien ra", pg.is_visible("#sim"))
        pg.click("#start-btn")
        pg.wait_for_timeout(500)
        check("tru dung phi", pg.inner_text("#bal") == "36", pg.inner_text("#bal"))
        bad = pg.evaluate("() => window.__dbg.bad()")
        for i, x in enumerate(bad):
            if x:
                pg.locator('.uc-row[data-i="%d"]' % i).click()
                pg.wait_for_timeout(60)
        pg.click("#ok")
        pg.wait_for_timeout(500)
        check("duyet dung -> duoc diem", pg.inner_text("#hb-score") == "1",
              pg.inner_text("#hb-score"))
        check("MOI hang co loi giai thich",
              pg.locator(".uc-why").count() == len(bad),
              f'{pg.locator(".uc-why").count()}/{len(bad)}')
        check("0 loi trang", not errs, str(errs[:1])[:120])
        check("0 asset hong", not bad_assets, str(bad_assets[:2])[:160])
        ctx.close()

        print("\n[6] Hoi quy: ba game lop B truoc van mo duoc")
        for f, tag in (("/game-survival.html", "Trạm Sinh Tồn"),
                       ("/game-comms.html", "Trạm Liên Lạc"),
                       ("/game-recycle.html", "Trạm Tuần Hoàn")):
            ctx = br.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
            pg.goto(SITE + f, wait_until="load")
            pg.wait_for_selector("#ov-start.show", timeout=15000)
            check(f"{f} mo duoc, 0 loi", not errs, str(errs[:1])[:120])
            check(f"{f} dung ten", tag.casefold() in pg.inner_text("body").casefold())
            ctx.close()

        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
