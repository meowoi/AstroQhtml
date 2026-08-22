# -*- coding: utf-8 -*-
"""probe_collections_union.py — BO SUU TAP KHONG DUOC BO ROI THU TRE VUA LAM.

Chu du an bao (22/08/2026): *"sua tai ghep chom sao: phai load lai moi luu viec"*.
Do tren trang thi GAME luu ngay (xem `play_constellation.py` 13/0) — cho noi dung
la `achievements.html`:

    var done = VIEW.consts;                       // server
    if(!done || !Object.keys(done).length){ ... } // chi lui ve may khi server RONG

Nen dung ca hay xay ra nhat lai sai: tre vua ghep xong mot chom MOI (may da ghi
ngay, viec con nam trong hang cho), server thi tra danh sach CU — **non rong** —
nen nhanh lui khong chay va chom vua ghep KHONG hien ra cho toi khi tai lai trang.

Bo do gieo dung canh do: server 1 chom, may 2 chom.

⚠️ Phai gieo `AstroQAuth` bang `Object.defineProperty` co setter nuot loi gan —
   `js/firebase-auth.js` la module ES nen no chay SAU va se ghi de mot loi gan
   thuong.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/probe_collections_union.py
"""
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"
CONS = (ROOT / "js" / "constellations.js").read_text(encoding="utf-8")
N_CONS = len(re.findall(r'key:\s*"', CONS))

dat = 0
hong = 0


def chk(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   " + name + (("  (" + str(info) + ")") if info else ""))
    else:
        hong += 1
        print("  [HONG] " + name + (("  -> " + str(info)) if info else ""))


def stub(ctx, consts, planets):
    ctx.add_init_script("""(() => {
      const SRV = %s;
      const fake = {
        getAchievements: () => Promise.resolve({ ok:true, data:{
          level:{ level:3, xp:355, xpInLevel:55, xpForNext:300, pct:18 },
          levels:{ xp:[0,100,300,600] },
          progress:{ quizCorrect:4, quizAnswered:5, gamesPlayed:2, flightSeconds:60,
                     meteorsEarned:30, bests:{}, terms:[],
                     planets:SRV.planets, consts:SRV.consts },
          achievements:{ summary:{ total:22, earned:1 }, badges:[] },
          wallet:{ meteors:120 } } }),
        getMissions:   () => Promise.resolve({ ok:false, reason:'auth' }),
        getOnboarding: () => Promise.resolve({ ok:true, tourSeen:true, intro01Seen:true,
                                               earth1Greeted:true, map01Seen:true }),
        setOnboarding: () => Promise.resolve({ ok:true }),
        postProgress:  () => Promise.resolve({ ok:true, data:{} }),
        updateProfile: p => Promise.resolve({ ok:true, data:{ profile:p } })
      };
      let v = fake;
      Object.defineProperty(window, 'AstroQAuth', {
        configurable:true, get:() => v, set:() => {}
      });
    })();""" % json.dumps({"consts": consts, "planets": planets}))


def seed_local(ctx, best, planets):
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','vi');"
        # ⚠ Ky luc trong may DONG DAU uid tu 22/08/2026 — gieo hinh dang phang
        #   la `localBests()` van doc duoc (duong lui cho ban ghi cu), nhung o day
        #   ta gieo dung hinh dang MOI de do dung thu san pham dang ghi.
        "localStorage.setItem('astroq-constellation-best', %s);"
        "localStorage.setItem('astroq-progress', %s);"
        "localStorage.setItem('astroq-user', %s);"
        % (json.dumps(json.dumps({"uid": "u-1", "best": best})),
           json.dumps(json.dumps({
               "quizTaken": 0, "quizAnswered": 0, "quizCorrect": 0, "quizPerfect": 0,
               "gamesPlayed": 2, "lessonsRead": 0, "flightSeconds": 60,
               "meteorsEarned": 30, "planets": planets, "bests": {}, "lessons": []})),
           json.dumps(json.dumps({"uid": "u-1", "name": "Bin", "character": "q",
                                  "avatar": "ava/q.png"}))))


def open_ach(br, consts, planets_srv, best_loc, planets_loc):
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    seed_local(ctx, best_loc, planets_loc)
    stub(ctx, consts, planets_srv)
    pg = ctx.new_page()
    perr = []
    pg.on("pageerror", lambda e: perr.append(str(e)))
    pg.goto(BASE + "/achievements.html", wait_until="load", timeout=30000)
    pg.wait_for_selector("#consts .chip", timeout=8000)
    pg.wait_for_timeout(300)
    return ctx, pg, perr


def read(pg):
    return pg.evaluate("""() => ({
      cs:  document.getElementById('cs-count').textContent.trim(),
      pl:  document.getElementById('pl-count').textContent.trim(),
      on:  [...document.querySelectorAll('#consts .chip.on')]
             .map(e => e.textContent.replace(/\\s+/g,' ').trim()),
      plOn:[...document.querySelectorAll('#planets .chip.on')]
             .map(e => e.textContent.replace(/\\s+/g,' ').trim())
    })""")


def main():
    print("js/constellations.js khai %d chom sao" % N_CONS)
    with sync_playwright() as p:
        br = p.chromium.launch()

        # ═══ [1] Server con danh sach CU, may da co chom MOI ═══
        print("\n=== [1] SERVER CON DANH SACH CU, MAY DA CO CHOM MOI ===")
        ctx, pg, perr = open_ach(
            br,
            consts={"ursa-major": 12},                       # server: 1 chom
            planets_srv=["earth"],                            # server: 1 hanh tinh
            best_loc={"ursa-major": 12, "scorpius": 8},        # may: 2 chom
            planets_loc=["earth", "mars"])                     # may: 2 hanh tinh
        r = read(pg)
        chk("dem chom sao = 2 (khong bo roi chom vua ghep)",
            r["cs"] == "2/%d" % N_CONS, r["cs"])
        chk("chom vua ghep hien ra that (co the doc ten tren man hinh)",
            len(r["on"]) == 2, " · ".join(r["on"]))
        chk("dem hanh tinh = 2 (cung mot ly do)",
            r["pl"].startswith("2/"), r["pl"])
        chk("0 loi trang", not perr, "; ".join(perr[:2]))
        ctx.close()

        # ═══ [2] Server DI TRUOC may (doi may) ═══
        print("\n=== [2] SERVER DI TRUOC MAY (tre vua doi may) ===")
        ctx, pg, perr = open_ach(
            br,
            consts={"ursa-major": 12, "orion": 20, "cassiopeia": 9},
            planets_srv=["earth", "mars", "venus"],
            best_loc={},                                       # may sach
            planets_loc=[])
        r = read(pg)
        chk("dem chom sao = 3 (lay tu server)",
            r["cs"] == "3/%d" % N_CONS, r["cs"])
        chk("dem hanh tinh = 3", r["pl"].startswith("3/"), r["pl"])
        chk("0 loi trang", not perr, "; ".join(perr[:2]))
        ctx.close()

        # ═══ [3] Ky luc: lay so NHANH HON cua hai ben ═══
        print("\n=== [3] KY LUC LAY SO NHANH HON CUA HAI BEN ===")
        ctx, pg, perr = open_ach(
            br,
            consts={"ursa-major": 30},          # server: 30 giay
            planets_srv=[],
            best_loc={"ursa-major": 9},          # may: 9 giay (nhanh hon)
            planets_loc=[])
        r = read(pg)
        chk("hien ky luc 0:09, khong phai 0:30",
            any("0:09" in x for x in r["on"]), " · ".join(r["on"]))
        chk("0 loi trang", not perr, "; ".join(perr[:2]))
        ctx.close()

        br.close()

    print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
    sys.exit(1 if hong else 0)


if __name__ == "__main__":
    main()
