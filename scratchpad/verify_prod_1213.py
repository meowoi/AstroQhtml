# -*- coding: utf-8 -*-
"""
verify_prod_1213.py — DO TREN BAN THAT sau khi push dot 6 muc (12–13/08/2026).

    python scratchpad/verify_prod_1213.py

Vi sao can du da co ~30 bo kiem chay o may: chung chay tren `127.0.0.1:8123`, tuc
tren THU MUC LAM VIEC. Bo nay tra loi mot cau khac han — **nguoi dung that co nhan
duoc khong**: file da len Pages chua, MIME co dung khong, va trang co dung duoc
khong khi mo tu chinh astroq.org.

⚠️ Do TRUOC khi Pages build xong thi moi ket luan deu sai (06/08/2026 ban that dung
   o ban cu gan mot ngay). Script tu kiem so hieu ban dung truoc, khong doan.
"""
import sys
import urllib.request

from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
WANT_VER = "2026.08.13.1"
ok_n, bad_n = 0, 0
FAILS = []


def chk(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [ok]   {name}" + (f"  ({extra})" if extra else ""))
    else:
        bad_n += 1
        FAILS.append(name)
        print(f"  [HONG] {name}" + (f"  ({extra})" if extra else ""))


def head(t):
    print(f"\n=== {t} ===")


def fetch(path):
    req = urllib.request.Request(SITE + path, method="GET")
    req.add_header("User-Agent", "astroq-verify/1.0")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), b""
    except Exception as e:
        return 0, str(e), b""


def main():
    head("[1] So hieu ban dung — do TRUOC moi thu khac")
    st, _, body = fetch("/js/ui-common.js")
    ver = ""
    if st == 200:
        import re
        m = re.search(rb'var VERSION = "([^"]+)"', body)
        ver = m.group(1).decode() if m else ""
    chk(ver == WANT_VER, f"ban that dang o ban dung {WANT_VER}", ver or f"status={st}")
    if ver != WANT_VER:
        print("\n  Pages CHUA build xong — dung lai, moi ket luan sau day deu vo nghia.")
        return 1

    head("[2] File MOI co that tren Pages")
    news = [
        "/js/depth.js", "/js/cosmetics.js", "/js/brag.js", "/js/daily.js",
        "/js/weeklog.js", "/css/cockpit.css", "/css/brag.css", "/css/daily.css",
        "/css/weeklog.css", "/css/shop.css",
        "/css/game-catch.css", "/css/game-maze.css", "/css/game-racer.css",
        "/shop.html", "/game-catch.html", "/game-maze.html", "/game-racer.html",
    ]
    for p in news:
        st, ct, _ = fetch(p)
        chk(st == 200, f"{p} tra 200", f"status={st}")
        # ⚠️ MIME phai dung: ES module bi tu choi neu server tra text/plain. Day la
        #    dieu PHAI DO chu khong duoc gia dinh (bai hoc 09/08/2026 voi js/quiz/).
        if p.endswith(".js"):
            chk("javascript" in ct.lower(), f"{p} MIME la javascript", ct)
        if p.endswith(".css"):
            chk("css" in ct.lower(), f"{p} MIME la css", ct)

    head("[3] Trang mo duoc, 0 loi, 0 asset hong")
    pages = ["/missions.html", "/profile.html", "/shop.html", "/games.html",
             "/game-catch.html", "/game-maze.html", "/game-racer.html",
             "/achievements.html", "/dashboard.html"]
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for p in pages:
            ctx = br.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            errs, bad404 = [], []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
            pg.on("response", lambda r: bad404.append(r.url) if r.status >= 400 else None)
            pg.add_init_script("localStorage.setItem('astroq-lang','vi');"
                               "localStorage.setItem('astroq-tour-seen','1');"
                               "localStorage.setItem('astroq-mission01-intro-seen','1');"
                               "localStorage.setItem('astroq-map01-seen','1');")
            pg.goto(SITE + p, wait_until="load")
            pg.wait_for_timeout(2500)
            chk(not errs, f"{p}: 0 loi console", "; ".join(errs[:2])[:120])
            chk(not bad404, f"{p}: 0 asset hong", "; ".join(bad404[:2])[:120])
            ctx.close()

        head("[4] Bang viec hom nay co that o Trung Tam Nhiem Vu")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(SITE + "/missions.html", wait_until="load")
        pg.wait_for_selector("#daily-panel", timeout=20000)
        chk(pg.locator("#daily-panel").count() == 1, "panel 'Viec hom nay' co tren trang")
        # ⚠️ Chua dang nhap -> phai hien dau "—", KHONG hien 0/n. Do chinh chuyen do
        #    tren ban that, vi day la thu nguoi dung chua dang nhap se thay dau tien.
        pg.wait_for_selector("#daily .dl-note", timeout=20000)
        t = pg.eval_on_selector("#daily", "e => e.innerText")
        chk("—" in t, "chua dang nhap: hien dau gach ngang", t[:50].replace("\n", " "))
        chk("0/" not in t, "KHONG hien tien do 0/n")
        ctx.close()

        head("[5] Nhat ky tuan co that o Ho so")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(SITE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wk-panel", timeout=20000)
        chk(pg.locator("#wk-panel").count() == 1, "panel 'Tuan nay' co tren trang")
        n = pg.locator("#recs .rec").count()
        chk(n == 6, "bang ky luc hien du 6 mini-game", f"{n} o")
        rt = pg.eval_on_selector("#recs", "e => e.innerText")
        for nm in ["Bắt Sao Băng", "Mê Cung Thiên Hà", "Đường Đua Sao Chổi"]:
            chk(nm in rt, f"co o ky luc '{nm}'")
        ctx.close()

        head("[6] Khu Huan Luyen: 6 game, khong con the khoa")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(SITE + "/games.html", wait_until="load")
        pg.wait_for_selector(".gcard", timeout=20000)
        tot = pg.locator(".gcard").count()
        soon = pg.locator(".gcard button[disabled]").count()
        chk(tot >= 6, "co it nhat 6 the game", f"{tot} the")
        chk(soon == 0, "KHONG con the nao bi khoa", f"{soon} the khoa")
        ctx.close()

        head("[7] Cua hang: khong lo gia nao o client")
        st, _, shop_js = fetch("/js/cosmetics.js")
        chk(st == 200 and b"price" not in shop_js.lower().replace(b"prices", b""),
            "js/cosmetics.js khong chua bang gia", f"status={st}")
        br.close()

    print("\n" + "=" * 58)
    print(f"KET QUA TREN BAN THAT: {ok_n} dat / {bad_n} hong")
    for f in FAILS:
        print("  - " + f)
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
