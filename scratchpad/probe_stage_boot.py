# -*- coding: utf-8 -*-
"""Soi nhanh: trang nhiem vu con DUNG DUOC sau khi tach vo hay khong.

Nhanh hon `smoke_mission_earth.py` (10 phut) rat nhieu — dung de bat loi vo ngay,
khong thay the bo smoke.

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/probe_stage_boot.py [ten-trang.html]
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else "mission-earth.html"
BASE = "http://127.0.0.1:8123/"
dat = hong = 0


def check(nhan, dieu_kien, chi_tiet=""):
    global dat, hong
    if dieu_kien:
        dat += 1
        print("  [OK]   " + nhan + (("  (" + chi_tiet + ")") if chi_tiet else ""))
    else:
        hong += 1
        print("  [HONG] " + nhan + (("  (" + chi_tiet + ")") if chi_tiet else ""))


with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    # WARN Ghim ngon ngu: `AstroQ.getLang()` lui ve `navigator.language`, ma Chromium
    #   cua Playwright mac dinh `en-US` -> phan "tieng Viet" cua bo do lang le chay
    #   bang tieng Anh va moi phep kiem chu Viet thanh vo nghia.
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg = ctx.new_page()
    errs, bad = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: bad.append("%s %s" % (r.status, r.url))
          if r.status >= 400 else None)

    pg.goto(BASE + PAGE, wait_until="load")
    pg.wait_for_function("window.__mission !== undefined", timeout=25000)

    print("\n=== %s: vo dung duoc chua ===" % PAGE)
    check("0 loi trang / console", not errs, "; ".join(errs[:3]))
    check("0 tai nguyen hong", not bad, "; ".join(bad[:3]))

    # Vo da dung ra du markup chua
    for i in ("back", "tag", "steps", "bal", "mute", "obj", "say", "card",
              "win", "after", "toast", "load"):
        check("vo dung ra #%s" % i,
              pg.evaluate("!!document.getElementById(%r)" % i))

    check("man cho da tat (canh dung xong)",
          pg.evaluate("document.getElementById('load').classList.contains('gone')"))
    check("nut VI/EN co that va bam duoc",
          pg.locator('.lang-switch button[data-lang="en"]').is_visible())

    # Chu cua VO phai la tieng Viet, va TAG phai lay tu tu dien TRANG
    back = pg.locator("#back").inner_text().strip()
    check("nut Ve dich sang tieng Viet", "Về" in back, back)
    tag = pg.locator("#tag").inner_text().strip()
    check("tag lay tu tu dien cua TRANG (khong phai cua vo)",
          "MISSION" in tag.upper(), tag)

    # Doi ngon ngu: ca vo lan trang phai doi theo
    pg.locator('.lang-switch button[data-lang="en"]').click()
    pg.wait_for_timeout(350)
    back_en = pg.locator("#back").inner_text().strip()
    check("doi EN thi chu cua VO doi theo", "Back" in back_en, back_en)
    pg.locator('.lang-switch button[data-lang="vi"]').click()
    pg.wait_for_timeout(250)

    # Man tong ket mo duoc va dem gio chay
    pg.evaluate("window.__mission.win()")
    pg.wait_for_timeout(400)
    check("man tong ket mo duoc",
          pg.evaluate("document.getElementById('win').classList.contains('show')"))
    check("duong ve tu dong dang dem", pg.evaluate("window.__mission.autoLeft") is not None,
          str(pg.evaluate("window.__mission.autoLeft")))
    # Tuong tac -> TAT dem han
    pg.mouse.move(720, 450)
    pg.wait_for_timeout(200)
    check("tuong tac TAT dem han", pg.evaluate("window.__mission.autoLeft") is None)

    print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
    b.close()
sys.exit(1 if hong else 0)
