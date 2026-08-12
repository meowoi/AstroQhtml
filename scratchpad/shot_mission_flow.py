# -*- coding: utf-8 -*-
"""
shot_mission_flow.py — chụp bốn tầng của khu nhiệm vụ để SOI BẰNG MẮT.

    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/shot_mission_flow.py

⚠️ Bộ đo tự động trả lời được "có đè nhau không, có tràn không". Nó KHÔNG trả lời
   được "nhìn có ra một con đường không", "cái đĩa 11px có đọc ra là Sao Thuỷ không".
   Dự án đã nhiều lần chỉ tìm ra lỗi hình khi soi ảnh chụp (vệt lửa dày như tia sét ·
   vòng khí quyển rời khỏi hành tinh · bong bóng phủ kín chặng trên). Ảnh ghi vào
   scratchpad/ và KHÔNG commit (.gitignore chặn *.png).
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
OUT = os.path.dirname(os.path.abspath(__file__))
UID = "u-shot"
STEPS = ["scan", "timeline", "sun", "life", "energy", "eco", "core"]


def seed(pg, done, lang="vi", unlocked=("earth",)):
    gate = {"open": list(unlocked), "route": ["earth", "moon"],
            "gate": 5, "done": len(done), "total": len(STEPS)}
    pg.add_init_script("""
      localStorage.setItem('astroq-lang', %s);
      localStorage.setItem('astroq-user', JSON.stringify({uid:%s, name:'Shot'}));
      localStorage.setItem('astroq-mission-steps', JSON.stringify(
        {uid:%s, m:{earth:{done:%s,total:%d,complete:false}}}));
      localStorage.setItem('astroq-route-gate', JSON.stringify(%s));
      var __auth = {
        postProgress: async function(){ return {ok:true, data:{}}; },
        missionStep:  async function(){ return {ok:true, data:{}}; },
        getMissions:  async function(){
          return { ok:true, status:200, data:{ missions:{ earth:{
            steps:%s, doneSteps:%s, done:false, codex:['a','b'], codexTotal:8,
            gate:5, gateMet:%s } }, route:['earth','moon'], unlockedPlaces:%s } };
        }
      };
      Object.defineProperty(window, 'AstroQAuth', {
        configurable:true, get:function(){ return __auth; }, set:function(){}
      });
    """ % (json.dumps(lang), json.dumps(UID), json.dumps(UID), json.dumps(done),
           len(STEPS), json.dumps(gate), json.dumps(STEPS), json.dumps(done),
           "true" if len(done) >= 5 else "false", json.dumps(list(unlocked))))


SHOTS = [
    ("hub",    "/missions.html",              "#resume:not([hidden])"),
    ("map",    "/mission-map.html",           ".body.open"),
    ("tree",   "/mission-tree.html?m=earth",  ".node.now"),
    ("planet", "/mission-planet.html?w=earth", ".node"),
]


def main():
    done = STEPS[:3]
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for name, path, sel in SHOTS:
            for tag, vp in (("desktop", {"width": 1440, "height": 900}),
                            ("mobile", {"width": 390, "height": 844})):
                ctx = br.new_context(viewport=vp,
                                     device_scale_factor=2 if tag == "mobile" else 1,
                                     is_mobile=(tag == "mobile"),
                                     has_touch=(tag == "mobile"))
                pg = ctx.new_page()
                seed(pg, done)
                pg.goto(BASE + path, wait_until="load")
                pg.wait_for_selector(sel, timeout=15000)
                pg.wait_for_timeout(500)
                f = os.path.join(OUT, f"shot-mf-{name}-{tag}.png")
                pg.screenshot(path=f, full_page=True)
                print("  ", os.path.basename(f))
                ctx.close()

        # Bảng chi tiết của cây chặng + bảng "chưa có nhiệm vụ" của bản đồ
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page(); seed(pg, done)
        pg.goto(BASE + "/mission-tree.html?m=earth", wait_until="load")
        pg.wait_for_selector(".node.now", timeout=15000)
        pg.click(".node.now .node-btn")
        pg.wait_for_selector("#sheet:not([hidden])", timeout=8000)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, "shot-mf-tree-sheet.png"))
        print("   shot-mf-tree-sheet.png")
        ctx.close()

        ctx = br.new_context(viewport={"width": 390, "height": 844},
                             device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = ctx.new_page(); seed(pg, done)
        pg.goto(BASE + "/mission-map.html", wait_until="load")
        pg.wait_for_selector(".body.open", timeout=15000)
        pg.click('.body[data-id="moon"]')
        pg.wait_for_selector("#sheet:not([hidden])", timeout=8000)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, "shot-mf-map-sheet-mobile.png"))
        print("   shot-mf-map-sheet-mobile.png")
        ctx.close()
        br.close()
    print("xong")


if __name__ == "__main__":
    main()
