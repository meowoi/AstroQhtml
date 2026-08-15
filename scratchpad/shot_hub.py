# -*- coding: utf-8 -*-
"""shot_hub.py — chup Trung Tam Dieu Huong de SOI MAT (bo cuc + hai menu tha).

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/shot_hub.py
Anh ra scratchpad/hub-*.png  (.gitignore da chan scratchpad/*.png).
"""
import sys
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

URL = "http://127.0.0.1:8123/dashboard.html"
STUB = """
localStorage.setItem('astroq-lang','vi');
localStorage.setItem('astroq-user', JSON.stringify({name:'Bi',uid:'u-test',avatar:'ava/luna.png'}));
localStorage.setItem('astroq-tour-seen','1');
localStorage.setItem('astroq-map01-seen','1');
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return {
    idToken:function(){return Promise.resolve(null);},
    getOnboarding:function(){return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,earth1Greeted:true,map01Seen:true});},
    setOnboarding:function(){return Promise.resolve({ok:true});},
    getAchievements:function(){return Promise.resolve({ok:true,level:{level:7,xp:1520,pct:42},
      progress:{quizAccuracy:88,flightSeconds:4600,quizCorrect:31,quizAnswered:35,gamesPlayed:9,
                lessonsRead:4,planets:['earth','mars','venus'],bests:{dodge:820}},
      badges:[{id:'rookie-astronaut',earnedAt:'2026-08-14T10:00:00Z'}],
      total:22, levels:{xp:[]}});},
    getMissions:function(){return Promise.resolve({ok:false,reason:'net'});},
    postProgress:function(){return Promise.resolve({ok:false});},
    verifyAdmin:function(){return Promise.resolve(false);},
    logout:function(){return Promise.resolve();}
  };},
  set:function(){}});
"""

SHOTS = [("desktop", 1440, 900), ("dt-390", 390, 844)]


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name, w, h in SHOTS:
            ctx = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=2,
                                 locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
            ctx.add_init_script(STUB)
            pg = ctx.new_page()
            pg.goto(URL, wait_until="load")
            pg.wait_for_timeout(1400)
            pg.screenshot(path=f"scratchpad/hub-{name}-fold.png")
            pg.screenshot(path=f"scratchpad/hub-{name}-full.png", full_page=True)

            # menu avatar
            pg.click(".user-menu [data-menu-btn]")
            pg.wait_for_timeout(400)
            pg.screenshot(path=f"scratchpad/hub-{name}-menu.png")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(250)

            # bo chon ngon ngu
            pg.click(".lang-pick [data-menu-btn]")
            pg.wait_for_timeout(400)
            pg.screenshot(path=f"scratchpad/hub-{name}-lang.png")
            print("xong", name)
            ctx.close()
        br.close()


if __name__ == "__main__":
    main()
