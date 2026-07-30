# -*- coding: utf-8 -*-
"""
shot_mission.py — chụp ảnh từng bước Nhiệm Vụ 01 để SOI MẮT.

Bộ smoke đo được con số, nhưng những lỗi kiểu "vệt sáng dày thành dải", "lưới
quá dày", "thẻ đè lên hành tinh" thì chỉ nhìn ảnh mới thấy — đã gặp nhiều lần
(ARCADE-01, warp-screen, specimen-vault).

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/shot_mission.py
"""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))

STUB = r"""
localStorage.setItem('astroq-lang', 'vi');
/* defineProperty + setter nuốt: js/progress.js chạy sau và gán thẳng
   window.AstroQProgress, gán thường là bị ghi đè. */
var __stub = {
  missionStep: async function (mission, step) {
    var TBL = { scan:{m:0,x:20,c:[]}, sun:{m:20,x:30,c:['sun']},
                rotation:{m:20,x:30,c:['rotation']},
                life:{m:20,x:40,c:['water','forest','animal','mountain']},
                core:{m:20,x:40,c:[]} };
    var r = TBL[step], done = step === 'core';
    window.__cx = (window.__cx || []).concat(r.c);
    return { ok:true, data:{ awarded:r.m+(done?100:0), xpGained:r.x+(done?120:0),
      missionDone:done, unlocks:done?'moon':null, wallet:{meteors:999},
      missions:{ earth:{ codex:window.__cx.slice(), codexTotal:6, done:done } } } };
  },
  quiz(){}, game(){}, lesson(){}, planet(){}, spend(){}, flush(){}
};
Object.defineProperty(window, 'AstroQProgress', {
  configurable: true, get: function () { return __stub; }, set: function () {}
});
"""


def say_through(pg, limit=6):
    for _ in range(limit):
        try:
            pg.wait_for_function(
                "() => { const b=document.getElementById('say-next');"
                " return b && !b.classList.contains('hide') &&"
                " document.getElementById('say').classList.contains('show'); }",
                timeout=3500)
        except Exception:
            return
        pg.evaluate("document.getElementById('say-next').click()")
        pg.wait_for_timeout(150)


def shot(pg, name):
    path = os.path.join(OUT, f"me-{name}.png")
    pg.screenshot(path=path)
    print("  ->", os.path.basename(path))


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])
        for tag, vp, mobile in (("d", {"width": 1440, "height": 900}, False),
                                ("m", {"width": 390, "height": 844}, True)):
            ctx = br.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile)
            pg = ctx.new_page()
            pg.add_init_script(STUB)
            pg.goto(BASE + "/mission-earth.html", wait_until="domcontentloaded")
            pg.wait_for_function("() => !!window.__mission", timeout=40000)
            pg.wait_for_timeout(700)

            # Bước 1: lưới quét + bàn tay + box thoại Comet
            shot(pg, f"{tag}1-scan-say")
            say_through(pg)
            pg.wait_for_function(
                "() => window.__mission.world.markers.length === 3", timeout=20000)
            pg.wait_for_timeout(500)
            shot(pg, f"{tag}1-scan-markers")
            for mid in pg.evaluate("window.__mission.world.markers.map(m=>m.id)"):
                pg.evaluate("id => window.__mission.pick({type:'marker', id})", mid)
                pg.wait_for_timeout(220)
            pg.wait_for_timeout(900)
            shot(pg, f"{tag}1-scan-done")

            # Bước 2: tối om → bấm Mặt Trời → ranh giới ngày/đêm
            say_through(pg)
            pg.wait_for_function("() => window.__mission.step === 'sun'", timeout=25000)
            say_through(pg)
            pg.wait_for_timeout(1600)
            shot(pg, f"{tag}2-dark")
            pg.evaluate("window.__mission.pick({type:'sun'})")
            pg.wait_for_timeout(2400)
            shot(pg, f"{tag}2-sun-lit")

            # Bước 3: vệ tinh
            say_through(pg)
            pg.wait_for_function("() => window.__mission.step === 'rotation'", timeout=25000)
            say_through(pg)
            pg.wait_for_timeout(700)
            shot(pg, f"{tag}3-sat-lost")
            # Kéo THẬT như trẻ: bước 3 xoay CHÍNH hành tinh, `setSpin` không còn
            # là đường đi được (và vốn không phải thứ trẻ có).
            box = pg.eval_on_selector(
                "#stage", "e => { const r = e.getBoundingClientRect();"
                          " return [r.left + r.width/2, r.top + r.height/2]; }")
            for _ in range(60):
                if pg.evaluate("() => window.__mission.done.includes('rotation')"):
                    break
                pg.mouse.move(box[0] - 160, box[1])
                pg.mouse.down()
                pg.mouse.move(box[0] + 160, box[1], steps=8)
                pg.mouse.up()
                pg.wait_for_timeout(170)
            pg.wait_for_timeout(600)
            shot(pg, f"{tag}3-sat-ok")

            # Bước 4: drone + thẻ mẫu vật
            say_through(pg)
            pg.wait_for_function("() => window.__mission.step === 'life'", timeout=25000)
            say_through(pg)
            pg.wait_for_function(
                "() => window.__mission.world.markers.length === 4", timeout=20000)
            pg.wait_for_timeout(500)
            shot(pg, f"{tag}4-biomes")
            ids = pg.evaluate("window.__mission.world.markers.map(m=>m.id)")
            for k, bid in enumerate(ids):
                pg.wait_for_function("() => !window.__mission.busy", timeout=30000)
                pg.evaluate("id => window.__mission.pick({type:'marker', id})", bid)
                if k == 0:
                    # Bắt đúng lúc tia laser sáng NHẤT. Nhịp: pan camera 800ms →
                    # drone bay 900ms → quét 1100ms với độ mờ theo sin(k·π), tức
                    # đỉnh ở ~2250ms. Chụp ở 1500ms là chụp lúc drone CÒN ĐANG BAY
                    # và tia chưa hiện — ảnh ra "không có tia quét".
                    pg.wait_for_timeout(2300)
                    shot(pg, f"{tag}4-drone-scan")
                try:
                    pg.wait_for_function(
                        "() => document.getElementById('card').classList.contains('show')",
                        timeout=20000)
                    if k == 0:
                        pg.wait_for_timeout(350)
                        shot(pg, f"{tag}4-card")
                    pg.wait_for_function(
                        "() => !document.getElementById('card').classList.contains('show')",
                        timeout=12000)
                except Exception:
                    pass

            # Bước 5: bảng 3 ô ngọc
            pg.wait_for_function("() => window.__mission.done.includes('life')", timeout=30000)
            say_through(pg)
            pg.wait_for_function("() => window.__mission.step === 'core'", timeout=25000)
            say_through(pg)
            pg.wait_for_selector("#core.show", timeout=15000)
            pg.wait_for_timeout(500)
            shot(pg, f"{tag}5-core")
            for s in pg.eval_on_selector_all("#core-tray .me-gem",
                                             "es => es.map(e => e.dataset.slot)"):
                pg.evaluate("s => window.__mission.fill(s)", s)
                pg.wait_for_timeout(200)
            # Màng khí quyển đang bọc hành tinh
            pg.wait_for_timeout(1400)
            shot(pg, f"{tag}5-shield")

            # Màn tổng kết — `core.outro()` bọc màng khí quyển RỒI Comet nói câu
            # cuối, câu đó chờ bấm "Tiếp tục".
            say_through(pg)
            pg.wait_for_selector("#win.show", timeout=30000)
            pg.wait_for_timeout(900)
            shot(pg, f"{tag}6-win")
            ctx.close()
        br.close()
    print("Xong.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
