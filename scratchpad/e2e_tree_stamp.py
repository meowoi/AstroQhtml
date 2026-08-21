# -*- coding: utf-8 -*-
"""e2e_tree_stamp.py — DAU ✓ tren cay chang co hien ngay sau khi choi xong chang do.

LOI THAT, chu du an choi roi bao (21/08/2026): *"choi xong chang thu 1 khong thay
dong dau chang 1 du da xong"*.

Nguyen nhan: `mission-earth.html` CO Y khong nap `js/firebase-auth.js`, nen moi
chang no choi deu roi vao HANG CHO. Ve `mission-tree.html` thi o day co HAI loi goi
song song — `flush()` (POST chang vua choi) va `AstroQProgress.missions()` (GET tien
do). GET nhanh hon POST nen tra ve trang thai TRUOC khi choi, va cay chang ve xong
thi khong ve lai nua. Sua o `js/progress.js`: moi route CHI DOC nay cho hang cho gui
het truoc (xem `readAuth()`).

Bo do gia lap dung thu tu do: POST cham 300ms, GET nhanh 20ms. Truoc khi sua thi bo
do nay ra "0 / 7" va khong co dau ✓ — tuc no do dung cai bug.

  python scratchpad/e2e_tree_stamp.py
"""
import pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("c:/Users/ADMIN/OneDrive/Desktop/astroq/AstroQhtml")
URL = (ROOT / "mission-tree.html").resolve().as_uri() + "?m=earth"

INIT = """
localStorage.clear();
localStorage.setItem("astroq-user", JSON.stringify({uid:"u1", name:"Test"}));
localStorage.setItem("astroq-lang","vi");
/* Hang cho: chang DAU TIEN vua choi xong o mission-earth.html (trang khong co token). */
localStorage.setItem("astroq-progress-queue", JSON.stringify(
  [{type:"mission",mission:"earth",step:"__STEP__",opId:"op-1"}]));
var serverDone = [];
window.AstroQAuth = {
  postProgress:function(){ return Promise.resolve({ok:true,data:{}}); },
  missionStep:function(ev){
    return new Promise(function(r){ setTimeout(function(){
      serverDone = [ev.step];
      r({ok:true,data:{missions:{earth:{steps:__STEPS__,doneSteps:serverDone.slice(),done:false}}}});
    }, 300); });
  },
  getMissions:function(){
    return new Promise(function(r){ setTimeout(function(){
      r({ok:true,data:{missions:{earth:{steps:__STEPS__,doneSteps:serverDone.slice(),done:false}}}});
    }, 20); });
  }
};
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("pageerror", lambda e: print("  JS ERROR:", e))
    # doc thu tu chang tu js/mission-catalog.js
    pg.goto((ROOT/"mission-tree.html").resolve().as_uri())
    steps = pg.evaluate("AstroQCatalog.find('earth').steps.map(function(s){return s.id;})")
    print("  chang:", steps)
    pg.close()

    pg = b.new_page()
    pg.on("pageerror", lambda e: print("  JS ERROR:", e))
    pg.add_init_script(INIT.replace("__STEP__", steps[0]).replace("__STEPS__", str([{"id":s} for s in steps]).replace("'", '"')))
    pg.goto(URL)
    pg.wait_for_timeout(2500)
    got = pg.evaluate("""() => Array.from(document.querySelectorAll('#tree .node')).map(function(n){
        return n.className + '|' + (n.querySelector('.bdg') ? n.querySelector('.bdg').textContent : '-'); })""")
    ct = pg.inner_text("#m-ct")
    for i, g in enumerate(got): print("   nut", i+1, g)
    print("  bo dem:", ct)
    ok = got[0].startswith("node done") and "✓" in got[0]
    print("\n  " + ("PASS" if ok else "FAIL") + "  chang 1 co dau ✓ sau khi choi xong")
    b.close()
    sys.exit(0 if ok else 1)
