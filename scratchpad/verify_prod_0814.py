# -*- coding: utf-8 -*-
"""Do TREN BAN THAT (astroq.org) sau khi push — hai viec cua ngay 14/08/2026.

⚠️ Ghi ra FILE roi chay, khong qua `python -c` trong shell: noi dung co dau
   nháy ngược và `===` cua JS lam shell/parse hong (bay da vap 2 lan hom nay).
"""
import json
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

dat = hong = 0


def ck(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (name, ("  · " + info) if info else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (name, ("  · " + info) if info else ""))


SEED = (
    "localStorage.setItem('astroq-lang','vi');"
    "localStorage.setItem('astroq-user', JSON.stringify({name:'Tre',uid:'u1',character:'castor'}));"
    "localStorage.setItem('astroq-tour-seen','1');"
    "localStorage.setItem('astroq-map01-seen','1');"
    "localStorage.setItem('astroq-progress-queue', "
    + json.dumps(json.dumps([{"type": "quiz", "correct": 3, "total": 5,
                              "meteors": 6, "opId": "o1"}]))
    + ");"
)

STUB = """
window.__A = {
  postProgress:    function(){ return Promise.resolve({ok:false, reason:'auth'}); },
  getAchievements: function(){ return Promise.resolve({ok:false, reason:'auth'}); },
  getMissions:     function(){ return Promise.resolve({ok:false, reason:'auth'}); },
  getOnboarding:   function(){ return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,
                                                       earth1Greeted:true,map01Seen:true}); }
};
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return window.__A;},set:function(){}});
"""

JS_SESS = """() => {
  const el = document.getElementById('sess');
  const tx = document.getElementById('sess-tx');
  const go = document.getElementById('sess-go');
  if(!el) return null;
  const b = el.getBoundingClientRect();
  const v = document.querySelector('.ver-badge');
  return { vis: !el.hasAttribute('hidden') && b.height > 0,
           txt: tx ? tx.innerText : '',
           go:  go ? !go.hasAttribute('hidden') : false,
           ver: v ? v.textContent : '' };
}"""

JS_VIZ = r"""() => {
  let worst = 0, who = '';
  document.querySelectorAll('svg.viz').forEach(sv => {
    const b = sv.getBoundingClientRect();
    sv.querySelectorAll('path,circle,rect').forEach(e => {
      const q = e.getBoundingClientRect();
      const o = Math.max(q.bottom-b.bottom, b.top-q.top, q.right-b.right, b.left-q.left);
      if(o > worst){ worst = o; who = e.getAttribute('class') || e.tagName; }
    });
  });
  const first = document.querySelector('svg.viz');
  const ov = first ? getComputedStyle(first).overflow : '(khong co svg.viz)';
  // Dau van tay cua loi cu: hai con so dinh nhau trong duong `d` (vd "M40,16440,164")
  const bad = [...document.querySelectorAll('path.viz-area')]
      .filter(p => /\d,\d{5,}/.test(p.getAttribute('d') || '')).length;
  const n = document.querySelectorAll('svg.viz').length;
  return { vuot: Math.round(worst), who, ov, bad, n };
}"""


def admin_stub():
    days = ([{"day": "2026-07-%02d" % x, "xp": 0, "meteors": 0, "events": 0, "users": 0,
              "seconds": 0, "game": 0, "quiz": 0, "lesson": 0, "planet": 0} for x in range(15, 32)]
            + [{"day": "2026-08-%02d" % x, "xp": 0, "meteors": 0, "events": 0, "users": 0,
                "seconds": 0, "game": 0, "quiz": 0, "lesson": 0, "planet": 0} for x in range(1, 14)]
            + [{"day": "2026-08-14", "xp": 2137, "meteors": -613, "events": 32, "users": 1,
                "seconds": 660, "game": 6, "quiz": 0, "lesson": 0, "planet": 8}])
    rep = {"generatedAt": "2026-08-14T00:00:00Z", "logSince": "2026-08-12", "days": days,
           "totalUsers": 1, "adminAccounts": 1, "pending": 0, "waitlist": 1, "silent": 0,
           "churn": 0, "meteorsEarned": 247, "meteorsBalance": 308, "spentPct": 0,
           "quizAnswered": 0, "quizCorrect": 0, "accuracy": None, "dau": 1, "wau": 1,
           "mau": 1, "stickiness": 100, "newD": 0, "truncated": False, "scannedItems": 33,
           "funnel": {"signup": 1, "firstEvent": 1, "firstQuiz": 0, "firstGame": 1},
           "retention": {"d1": 0, "d7": 0, "d30": 0}, "hours": [0]*24, "weekdays": [0]*7,
           "levelDist": {"7": 1}, "badgeDist": {"8": 1}, "accuracyDist": {}, "rareBadges": [],
           "topContent": [], "weakTerms": [], "missions": {}, "userTable": []}
    return ("window.__A={getAdminStats:function(){return Promise.resolve({ok:true,data:"
            + json.dumps({"report": rep})
            + "});},getOnboarding:function(){return Promise.resolve({ok:true,tourSeen:true});},"
            "getAchievements:function(){return Promise.resolve({ok:false,reason:'auth'});}};"
            "Object.defineProperty(window,'AstroQAuth',{configurable:true,"
            "get:function(){return window.__A;},set:function(){}});")


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("=== [1] BAN THAT: dai nhac mat phien o dashboard ===")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script(SEED)
        pg.add_init_script(STUB)
        pg.goto("https://astroq.org/dashboard.html", wait_until="load")
        pg.wait_for_timeout(3200)
        r = pg.evaluate(JS_SESS)
        ck("dai nhac hien ra tren ban that", bool(r and r["vis"]))
        ck("noi so viec dang cho", bool(r and "1" in r["txt"]), repr((r or {}).get("txt", "")[:80]))
        ck("co nut dang nhap lai (nhanh mat phien)", bool(r and r["go"]))
        ck("huy hieu ban dung dung", bool(r and "2026.08.14.1" in (r.get("ver") or "")),
           (r or {}).get("ver"))
        ck("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        print("\n=== [2] BAN THAT: bao cao suc khoe khong con vach tim tran ===")
        ctx = br.new_context(viewport={"width": 996, "height": 1000})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script(SEED)
        pg.add_init_script(admin_stub())
        pg.goto("https://astroq.org/admin-report.html", wait_until="load")
        pg.wait_for_timeout(3200)
        v = pg.evaluate(JS_VIZ)
        ck("co bieu do de ma do (neu 0 thi phep kiem la rong)", v["n"] > 0, "%d svg.viz" % v["n"])
        ck("khong hinh nao vuot khung SVG", v["vuot"] == 0,
           "vuot %dpx (%s)" % (v["vuot"], v["who"]))
        ck("`.viz` cat phan ve lo", v["ov"] == "hidden", v["ov"])
        ck("khong duong `d` nao con toa do dinh nhau", v["bad"] == 0, "%d path hong" % v["bad"])
        ck("0 loi trang", not errs, str(errs[:1]))
        ctx.close()
        br.close()

    print("\n%s\nBAN THAT: %d dat / %d hong\n%s" % ("=" * 52, dat, hong, "=" * 52))
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
