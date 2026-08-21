# -*- coding: utf-8 -*-
"""Do DO DAI `tour()` (ghe het tinh the roi ra cong) o TUNG CAP me cung.

⚠️ VI SAO CAN: `play_maze.py` muc [4] choi 30 luot lien tiep trong CUNG mot
   context, nen `astroq-maze-tier` tang dan va 26/30 luot cuoi chay o me cung
   TO NHAT. No di theo `tour()` voi `cap=600`. Neu tour o cap 4 doi khi dai hon
   600 buoc thi bot khong toi cong -> khong co bang ket qua -> het han cho, va
   doc ra y nhu san pham hong. Day la phep do phan biet "cap qua nho" voi
   "loi that cua game".
"""
import sys, io, statistics
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
URL = "http://127.0.0.1:8123/game-maze.html"

with sync_playwright() as p:
    br = p.chromium.launch()
    for tier in range(4):
        ctx = br.new_context(viewport={"width": 1440, "height": 900},
                             locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
        ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                           "localStorage.setItem('astroq-asteroids','9999');"
                           "localStorage.setItem('astroq-maze-tier','%d');" % tier)
        pg = ctx.new_page()
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(350)
        lens, cols, rows = [], 0, 0
        for i in range(25):
            pg.evaluate("() => localStorage.setItem('astroq-asteroids','9999')")
            # ghim tier: xong luot la game tu tang cap, nen dat lai truoc moi luot
            pg.evaluate("(t) => localStorage.setItem('astroq-maze-tier', String(t))", tier)
            btn = "#again-btn" if pg.is_visible("#ov-over") else "#start-btn"
            pg.click(btn); pg.wait_for_timeout(70)
            if pg.evaluate("() => window.__maze.state") != "play":
                break
            m = pg.evaluate("() => ({t: window.__maze.tour().length,"
                            " c: window.__maze.cols, r: window.__maze.rows})")
            lens.append(m["t"]); cols, rows = m["c"], m["r"]
            # di het tour de ket thuc luot (cap that su lon)
            pg.evaluate("""() => {
                const d = window.__maze.tour();
                for (const x of d){ window.__maze.snap();
                  if(!window.__maze.move(x)) {} if(window.__maze.state!=='play') break; }
                window.__maze.snap();
            }""")
            pg.wait_for_selector("#ov-over.show", timeout=15000)
        print("cap %d (%dx%d): n=%d  min=%d  TB=%.0f  max=%d  | vuot 600: %d/%d"
              % (tier + 1, cols, rows, len(lens), min(lens),
                 statistics.mean(lens), max(lens),
                 sum(1 for x in lens if x > 600), len(lens)), flush=True)
        ctx.close()
    br.close()
