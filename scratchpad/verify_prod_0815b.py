# -*- coding: utf-8 -*-
"""Mo CHINH astroq.org tren Chromium: 0 loi trang, 0 asset hong, menu tha bam duoc,
me cung vao duoc man choi. Nhan print KHONG DAU."""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
dat = hong = 0


def check(name, ok, info=""):
    global dat, hong
    if ok:
        dat += 1
        print("  [OK]   %s  %s" % (name, info))
    else:
        hong += 1
        print("  [HONG] %s  %s" % (name, info))


def mk(br):
    ctx = br.new_context(viewport={"width": 1440, "height": 900},
                         locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    # ⚠️ Gieo co "da xem tour" + "da qua man ban do": context moi la mot khach MOI,
    #    nen `.tour-block` chan moi cu bam va `mapFirst()` day sang explorer — dung
    #    hanh vi cua san pham, nhung sai chỗ de do menu tha.
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','50');"
                        "localStorage.setItem('astroq-tour-seen','1');"
                        "localStorage.setItem('astroq-map01-seen','1');")
    pg = ctx.new_page()
    pg.perr, pg.bad = [], []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.on("response", lambda r: pg.bad.append("%s %s" % (r.status, r.url))
          if r.status >= 400 else None)
    return ctx, pg


with sync_playwright() as p:
    br = p.chromium.launch()

    print("[1] games.html tren ban that")
    ctx, pg = mk(br)
    pg.goto(SITE + "/games.html", wait_until="load")
    pg.wait_for_timeout(1200)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    check("0 asset hong", not pg.bad, str(pg.bad[:2]))
    n = pg.locator(".gcard").count()
    check("ve du 6 the game", n == 6, str(n))
    heads = pg.locator(".gcard .gc-head").count()
    check("6 the deu co nhan canh icon", heads == 6, str(heads))
    # Nhan phan loai phai NAM CUNG HANG voi icon, khong nam duoi.
    ic = pg.locator(".gcard:first-child .gc-head .ic").bounding_box()
    tg = pg.locator(".gcard:first-child .gc-head .tag.prog").bounding_box()
    check("nhan nam CANH icon (khong nam duoi)",
          tg["x"] > ic["x"] + ic["width"] - 4 and abs(tg["y"] - ic["y"]) < ic["height"],
          "icon x=%.0f w=%.0f | nhan x=%.0f y lech=%.0f"
          % (ic["x"], ic["width"], tg["x"], tg["y"] - ic["y"]))
    check("khong con dong 'doc them'",
          "đọc thêm" not in pg.inner_text("body").lower(), "")
    ctx.close()

    print("\n[2] Me cung: vao duoc man choi, cong khoa noi ro ly do")
    ctx, pg = mk(br)
    pg.goto(SITE + "/game-maze.html", wait_until="load")
    pg.wait_for_timeout(1200)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    check("0 asset hong", not pg.bad, str(pg.bad[:2]))
    bal0 = pg.evaluate("() => Number(localStorage.getItem('astroq-asteroids')||0)")
    pg.click("#start-btn")
    pg.wait_for_timeout(500)
    bal1 = pg.evaluate("() => Number(localStorage.getItem('astroq-asteroids')||0)")
    check("tru dung 3 tt (phi moi cua muc De)", bal0 - bal1 == 3,
          "%d -> %d" % (bal0, bal1))
    st = pg.evaluate("() => window.__maze && window.__maze.state")
    check("vao duoc man choi", st == "play", str(st))
    ctx.close()

    print("\n[3] Dashboard: menu tha sau avatar bam duoc")
    ctx, pg = mk(br)
    pg.goto(SITE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(1500)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    btn = pg.locator(".user-menu [data-menu-btn]")
    check("co nut menu sau avatar", btn.count() == 1, str(btn.count()))
    btn.first.click()
    pg.wait_for_timeout(400)
    pop = pg.locator(".user-menu [data-menu-pop]")
    check("menu mo ra that", pop.first.is_visible())
    items = pop.first.locator(".um-item").count()
    check("co du cac muc ben trong", items >= 5, str(items))
    ctx.close()

    br.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
