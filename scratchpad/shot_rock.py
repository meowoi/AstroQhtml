# -*- coding: utf-8 -*-
"""shot_rock.py — chup san 3 game de SOI MAT anh thien thach xam dung chung.

So do noi CO, khong noi hinh doc ra la cai gi. Bo nay chup:
  - dodge  : san thuong + san o cap 3 (co da LON chiem hai lan)
  - defender: san 360 do
  - racer  : de doi chieu (game da dung art tu 21/08)
va mot luot CHAN anh de xem duong lui.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/shot_rock.py
"""
import pathlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
BASE = "http://127.0.0.1:8123"


def shot(br, name, game, block=False, wait=3500, seed=None, fly=False):
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh",
                         viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','999');")
    if block:
        ctx.route("**/rock-gray.png", lambda r: r.fulfill(status=404, body=""))
    pg = ctx.new_page()
    pg.goto(BASE + "/" + game, wait_until="load")
    pg.wait_for_selector("#start-btn", timeout=8000)
    if seed:
        pg.evaluate(seed)
    pg.click("#start-btn")
    box = pg.query_selector(".play") or pg.query_selector("canvas")

    if fly:
        # ⚠️ KHONG co ai choi thi tau roi (hoac bay len dung mep) va CHET — anh chup
        #    ra bang ket qua chu khong ra san. Cung khong lai duoc bang cach ban
        #    phim theo nhip: `holding` chi nha khi co `keyup`, va nhip nao cung
        #    hoac dam tran hoac dam day.
        #    Nen: RINH khung cuoi TRUOC khi chet — cu thay lop phu ket qua chua bat
        #    thi chup de len anh truoc. Ket thuc vong lap la co khung san moi nhat.
        pg.evaluate("""() => { window.__flap = setInterval(() => {
             document.dispatchEvent(new KeyboardEvent('keydown', {key:' '}));
             setTimeout(() => document.dispatchEvent(
               new KeyboardEvent('keyup', {key:' '})), 60);
           }, 190); }""")
        got = False
        for _ in range(int(wait / 150)):
            pg.wait_for_timeout(150)
            over = pg.evaluate("() => { const o=document.getElementById('ov-over');"
                               "return !!(o && o.classList.contains('show')); }")
            if not over:
                box.screenshot(path=str(HERE / name))
                got = True
            elif got:
                break
            else:
                pg.click("#again-btn")     # chet truoc khi chup duoc -> choi lai
        pg.evaluate("() => clearInterval(window.__flap)")
        print("  " + name + ("" if got else "   [!] khong chup duoc khung san"))
        ctx.close()
        return

    pg.wait_for_timeout(wait)
    if seed:
        pg.evaluate(seed)
        pg.wait_for_timeout(500)
    box.screenshot(path=str(HERE / name))
    print("  " + name)
    ctx.close()


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        print("chup:")
        shot(br, "rock-01-dodge.png", "game-dodge.html", fly=True)
        # Da LON chi xuat hien tu cap 3 — bo dong ho tien len de chup duoc no.
        shot(br, "rock-02-dodge-big.png", "game-dodge.html", wait=6000, fly=True,
             seed="() => { if (window.__dbg && __dbg.setTime) __dbg.setTime(70); }")
        shot(br, "rock-03-dodge-fallback.png", "game-dodge.html", block=True, fly=True)
        shot(br, "rock-04-defender.png", "game-defender.html")
        shot(br, "rock-05-defender-fallback.png", "game-defender.html", block=True)
        shot(br, "rock-06-racer.png", "game-racer.html", wait=4500, fly=True)
        br.close()


if __name__ == "__main__":
    main()
