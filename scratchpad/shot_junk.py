# -*- coding: utf-8 -*-
"""Chụp CẬN từng biến thể rác vũ trụ để soi bằng mắt.

Số đo nói bốn biến thể khác màu và nằm trong vùng va chạm — nhưng nó KHÔNG nói
được "hình này đọc ra là cái gì". Dự án đã trả giá nhiều lần cho đúng chỗ đó
(sao chổi đọc thành cái thìa / chùm xúc xích; hai nét gãy đọc thành chữ số 17;
vành khí quyển đọc thành cái vòng rời). Nên phải chụp rồi nhìn.
"""
import io
import os
import re
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.dirname(os.path.abspath(__file__))
RAD = 40.0


def names():
    src = io.open(os.path.join(ROOT, "game-defender.html"),
                  encoding="utf-8", newline=None).read()
    i = src.find("var JUNK = [")
    return re.findall(r's:"([a-z]+)"', src[i:src.find("];", i)])


with sync_playwright() as p:
    br = p.chromium.launch()
    NM = names()
    ctx = br.new_context(viewport={"width": 1440, "height": 900},
                         device_scale_factor=3, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','300');")
    pg = ctx.new_page()
    pg.goto(BASE + "/game-defender.html", wait_until="load", timeout=30000)
    pg.wait_for_timeout(900)
    if pg.locator(".ov.rot.show").count():
        pg.locator(".ov.rot.show .rot-ok").click()
    pg.click("#start-btn")
    pg.wait_for_timeout(400)

    done = {}
    for _ in range(70):
        if len(done) >= len(NM):
            break
        if pg.evaluate("() => window.__dbg.state") != "play":
            pg.wait_for_timeout(900)
            if pg.locator("#again-btn").is_visible():
                pg.click("#again-btn"); pg.wait_for_timeout(400)
            continue
        pg.evaluate("() => window.__dbg.spawn(1, 'junk')")
        pg.wait_for_timeout(40)
        junk = [f for f in pg.evaluate("() => window.__dbg.list")
                if f["key"] == "junk"]
        if not junk:
            continue
        tgt = max(junk, key=lambda f: f["n"])
        jv = tgt.get("jv")
        if jv is None or jv in done:
            continue
        cur = None
        for _w in range(45):
            cur = pg.evaluate("(n) => (window.__dbg.list || [])"
                              ".find(o => o.n === n) || null", tgt["n"])
            if not cur:
                break
            if (RAD + 3 <= cur["x"] <= 600 - RAD - 3
                    and RAD + 3 <= cur["y"] <= 600 - RAD - 3):
                break
            pg.wait_for_timeout(90)
        if not cur:
            continue
        box = pg.evaluate("""(a) => {
            const cv = document.querySelector('canvas');
            const b  = cv.getBoundingClientRect();
            return {x: b.left + (a.x - a.r) / 600 * b.width,
                    y: b.top  + (a.y - a.r) / 600 * b.height,
                    width:  a.r * 2 / 600 * b.width,
                    height: a.r * 2 / 600 * b.height};
        }""", {"x": cur["x"], "y": cur["y"], "r": RAD})
        f = os.path.join(OUT, "junk-can-%s.png" % NM[jv])
        pg.screenshot(path=f, clip=box)
        done[jv] = f
        print("  %-6s -> %s" % (NM[jv], os.path.basename(f)))
    ctx.close()
    br.close()
print("da chup %d/%d bien the" % (len(done), len(NM)))
