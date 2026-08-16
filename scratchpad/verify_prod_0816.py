# -*- coding: utf-8 -*-
"""Do tren BAN THAT sau khi Pages build — dot 16/08/2026.

    python scratchpad/verify_prod_0816.py

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC. Do truoc luc Pages build xong thi
   moi ket luan deu sai — 06/08/2026 ban that da tung dung o ban cu gan mot ngay.
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
WANT_VER = "2026.08.16.1"

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
    print(f"=== Do ban that {SITE} ===\n")

    # ---------- [1] So hieu ban dung — KIEM TRUOC MOI THU ----------
    print("[1] So hieu ban dung")
    _, _, uc = get("/js/ui-common.js")
    m = re.search(r'VERSION\s*=\s*"([\d.]+)"', uc)
    check(f"ban dung = {WANT_VER}", m and m.group(1) == WANT_VER,
          m.group(1) if m else "khong doc duoc")
    if not m or m.group(1) != WANT_VER:
        print("\n⚠️ Pages CHUA build xong — dung o day, moi phep do sau deu vo nghia.")
        return 1

    # ---------- [2] File moi tra 200 voi MIME dung ----------
    # ES module bi tu choi neu server tra text/plain, nen MIME la thu phai DO.
    print("\n[2] File moi tra 200 + MIME dung")
    for p, want in [("/game-recycle.html", "text/html"),
                    ("/game-comms.html", "text/html"),
                    ("/game-survival.html", "text/html"),
                    ("/css/game-recycle.css", "text/css"),
                    ("/css/game-comms.css", "text/css"),
                    ("/css/decision-game.css", "text/css"),
                    ("/js/game-run.js", "javascript")]:
        try:
            st, ct, _ = get(p)
        except Exception as e:
            st, ct = 0, str(e)
        check(f"{p}", st == 200 and want in ct, f"{st} · {ct}")

    # ---------- [3] Phi vao cua khop server ----------
    print("\n[3] Phi vao cua tren ban that")
    _, _, econ = get("/economy.js")
    _, _, rec = get("/game-recycle.html")
    fee = re.search(r"recycle\s*:\s*(\d+)", econ)
    cost = re.search(r"COST\s*:\s*(\d+)", rec)
    check("economy.js co phi recycle", bool(fee), fee.group(1) if fee else "-")
    check("CONFIG.COST khop economy.js",
          fee and cost and fee.group(1) == cost.group(1),
          f"{cost and cost.group(1)} vs {fee and fee.group(1)}")

    # ---------- [4] Mo chinh trang tren ban that ----------
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("\n[4] games.html — 9 the, 0 the khoa")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        errs, bad_assets = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad_assets.append(r.url) if r.status >= 400 else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(SITE + "/games.html", wait_until="networkidle")
        n = pg.locator(".gcard").count()
        soon = pg.locator(".gcard.soon, .gcard [disabled]").count()
        check("du 9 the game", n == 9, str(n))
        check("0 the khoa", soon == 0, str(soon))
        check("co the Tram Tuan Hoan", "Trạm Tuần Hoàn" in pg.inner_text("body"))
        check("0 loi trang", not errs, str(errs[:1])[:120])
        check("0 asset hong", not bad_assets, str(bad_assets[:2])[:160])
        ctx.close()

        print("\n[5] game-recycle.html — choi that mot ngay tren ban that")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        errs, bad_assets = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad_assets.append(r.url) if r.status >= 400 else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');"
                           "localStorage.setItem('astroq-asteroids','40');")
        pg.goto(SITE + "/game-recycle.html", wait_until="load")
        pg.wait_for_selector("#ov-start.show", timeout=15000)
        check("nhan MO PHONG hien ra", pg.is_visible("#sim"))
        pg.click("#start-btn")
        pg.wait_for_timeout(500)
        check("tru dung phi", pg.inner_text("#bal") == "36", pg.inner_text("#bal"))
        check("chua chia thi khong chay duoc",
              pg.get_attribute("#run", "disabled") is not None)
        for k, t in (("w", 2), ("a", 2), ("o", 1)):
            for _ in range(t):
                pg.locator('.rc-btn[data-k="%s"][data-d="1"]' % k).click()
                pg.wait_for_timeout(60)
        check("chia het dien thi chay duoc",
              pg.get_attribute("#run", "disabled") is None)
        pg.click("#run")
        pg.wait_for_timeout(700)
        log = pg.inner_text("#log")
        check("nhat ky noi ro may oxy ton nuoc", "nước" in log, log[:90])
        check("ba vach van hien", pg.locator(".rc-g").count() == 3)
        check("0 loi trang", not errs, str(errs[:1])[:120])
        check("0 asset hong", not bad_assets, str(bad_assets[:2])[:160])
        ctx.close()

        print("\n[6] Hoi quy: hai game lop B truoc van mo duoc")
        for f, tag in (("/game-survival.html", "Trạm Sinh Tồn"),
                       ("/game-comms.html", "Trạm Liên Lạc")):
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
