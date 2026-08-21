# -*- coding: utf-8 -*-
r"""Ví của ARCADE-02 sau khi kết lượt: số dư THẬT vs số trên HUD.

⚠️ VÌ SAO CẦN MỘT PHÉP ĐO RIÊNG: `shoot_defender` báo `onFinishGame cong dung:
   120 + 4 = 120` — nhưng nó đọc `#bal` trên HUD, nên một mình con số đó KHÔNG
   phân biệt được hai chuyện khác hẳn nhau:
     ① ví THẬT không cộng          → lỗi kinh tế, trẻ mất tiền đã kiếm;
     ② ví cộng nhưng `#bal` không vẽ lại → lỗi hiển thị (cùng họ ca `shop.html`
        13/08: mua xong số dư trên HUD không trừ).
   Bộ này đọc CẢ HAI: `#bal` và `localStorage["astroq-asteroids"]`.
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright  # noqa: E402

URL = "http://127.0.0.1:8123/game-defender.html"
START = 200
ok_n = bad_n = 0


def chk(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""))
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""))


def snap(pg):
    return pg.evaluate("""() => ({
      hud: (document.getElementById('bal')||{}).textContent,
      ls:  localStorage.getItem('astroq-asteroids'),
      eco: (window.Economy && Economy.getAsteroids) ? Economy.getAsteroids() : null,
      state: window.__dbg ? window.__dbg.state : null,
      mined: (document.getElementById('r-mined')||{}).textContent
    })""")


with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','vi');"
        "localStorage.setItem('astroq-sfx','off');"
        "localStorage.setItem('astroq-asteroids','%d');" % START)
    pg = ctx.new_page()
    perr = []
    pg.on("pageerror", lambda e: perr.append(str(e)))
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)

    b0 = snap(pg)
    chk(b0["hud"] == str(START) and b0["ls"] == str(START),
        "man brief: HUD va localStorage khop nhau", json.dumps(b0))

    pg.click("#start-btn")
    pg.wait_for_timeout(600)
    b1 = snap(pg)
    # Phi doc TU TRANG, dung ghim so: dot 15/08 doi phi defender 5 -> 4 theo luat
    # do kho (`Wallet.Diff` = medium). Ghim 5 la bao oan mot hanh vi DUNG.
    fee = pg.evaluate("() => window.__dbg && window.__dbg.cost")
    if not fee:
        fee = START - int(b1["ls"])
        print("     (trang khong mo `cost`, suy tu so du: %d tt)" % fee)
    chk(int(b1["ls"]) == START - fee,
        "vao luot: localStorage tru dung phi vao cua (%s tt)" % fee, b1["ls"])
    chk(b1["hud"] == b1["ls"], "vao luot: HUD khop localStorage",
        "%s vs %s" % (b1["hud"], b1["ls"]))

    # ⚠️ PHAI CO `mined` > 0, khong thi phep kiem vi DAT MOT CACH RONG (luot dau
    #   cua bo nay do duoc `mined = 0` va van bao "cong dung 0 vien" — vo nghia).
    #   Gieo thach TIM roi GIU CHUOT ban va quet quanh tam de ha chung.
    box = pg.query_selector("canvas").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    rr = min(box["width"], box["height"]) * 0.32
    pg.mouse.move(cx + rr, cy)
    pg.mouse.down()
    import math
    for i in range(90):
        if i % 12 == 0:
            pg.evaluate("() => window.__dbg.spawn(3,'purple')")
        a = i / 90.0 * math.pi * 4
        pg.mouse.move(cx + math.cos(a) * rr, cy + math.sin(a) * rr)
        pg.wait_for_timeout(70)
        if pg.evaluate("() => window.__dbg.state") == "over":
            break
    pg.mouse.up()
    live = pg.evaluate("""() => ({m: +(document.getElementById('mtr')||{}).textContent,
                                 b: +(document.getElementById('bal')||{}).textContent})""")
    print("     luc dang choi: vi tam = %s | HUD bal = %s" % (live["m"], live["b"]))
    # Roi de Tram vo
    pg.evaluate("() => window.__dbg.spawn(16,'grey')")
    for _ in range(150):
        pg.wait_for_timeout(300)
        if pg.evaluate("() => window.__dbg.state") == "over":
            break

    b2 = snap(pg)
    chk(b2["state"] == "over", "Tram vo -> bang ket qua", str(b2["state"]))
    mined = int(b2["mined"] or 0)
    chk(mined > 0, "luot nay co thu duoc tt (khong thi phep kiem vi la RONG)",
        str(mined))
    print("     mined = %d | HUD = %s | localStorage = %s | Economy = %s"
          % (mined, b2["hud"], b2["ls"], b2["eco"]))

    # ĐÂY LÀ PHÉP ĐO PHÂN BIỆT: ví thật vs HUD
    chk(int(b2["ls"]) == int(b1["ls"]) + mined,
        "VI THAT (localStorage) cong dung so vien",
        "%s + %d = %s" % (b1["ls"], mined, b2["ls"]))
    chk(b2["hud"] == b2["ls"],
        "HUD hien dung so du that (khong dung yen)",
        "HUD %s vs vi %s" % (b2["hud"], b2["ls"]))
    chk(not perr, "0 loi trang", str(perr[:1]))
    ctx.close()
    br.close()

print("\n" + "=" * 52)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
