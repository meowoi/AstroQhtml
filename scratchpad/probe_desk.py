# -*- coding: utf-8 -*-
"""Do hang "mau vat trung o ban dieu khien" tren dashboard.

Cau hoi chinh: tre chon mau vat o specimen-vault roi thi buong lai co VE RA khong.
Truoc lan sua nay dashboard co 0 cho nhac `desk` — tuc app hua mot cho trung bay roi
khong trung gi ca.
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
DESK = ["ancient-seawater", "mars-red-ice", "amazon-leaf"]

ok = bad = 0


def chk(name, cond, extra=""):
    global ok, bad
    if cond:
        ok += 1; print(f"  [OK]   {name}" + (f"  ({extra})" if extra else ""))
    else:
        bad += 1; print(f"  [HONG] {name}" + (f"  ({extra})" if extra else ""))


def stub(desk, lang="vi"):
    import json
    return """
window.__A = {
  getAchievements: function(){ return Promise.resolve({ ok:true, data:{
    depth:'junior', ship:'LUNA MOT',
    equipped:{theme:'cockpit-cyan',frame:'frame-steel',decal:'decal-none'},
    level:{level:7,xp:1355,xpInLevel:155,xpForNext:700,pct:22},
    progress:{quizCorrect:24,quizAnswered:30,gamesPlayed:6,planets:[],
              flightSeconds:4800,meteorsEarned:100,bests:{},terms:[],
              desk: %s},
    achievements:{summary:{total:22,earned:6},badges:[]},
    wallet:{meteors:1021} }}); },
  getMissions:function(){ return Promise.resolve({ok:false,reason:'auth'}); },
  getOnboarding:function(){ return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,
                                                    earth1Greeted:true,map01Seen:true}); },
  setOnboarding:function(){ return Promise.resolve({ok:true}); },
  postProgress:function(){ return Promise.resolve({ok:true,data:{}}); },
  getShop:function(){ return Promise.resolve({ok:false,reason:'auth'}); }
};
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return window.__A;},set:function(){}});
""" % json.dumps(desk)


def seed(lang="vi"):
    return ("localStorage.setItem('astroq-lang','%s');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1');"
            "localStorage.setItem('astroq-user', JSON.stringify({name:'Bin',pilotName:'Bin',"
            "uid:'u',equipped:{theme:'cockpit-cyan',frame:'frame-steel',decal:'decal-none'},"
            "ship:'LUNA MOT'}));" % lang)


JS = """
() => {
  const row = document.getElementById('deskrow');
  if (!row) return {err:'khong co #deskrow'};
  const cs = getComputedStyle(row);
  const chips = [...document.querySelectorAll('#dk-list .dchip')];
  const r = row.getBoundingClientRect();
  // Chong lan voi moi phan tu co chu rieng trong bang Thong Ke
  let worst = 0, who = '';
  document.querySelectorAll('.stats-hud *').forEach(e => {
    if (e === row || row.contains(e) || e.contains(row)) return;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const q = e.getBoundingClientRect();
    const w = Math.max(0, Math.min(r.right,q.right) - Math.max(r.left,q.left));
    const h = Math.max(0, Math.min(r.bottom,q.bottom) - Math.max(r.top,q.top));
    if (w*h > worst) { worst = w*h; who = e.className || e.tagName; }
  });
  return {
    display: cs.display, hidden: row.hasAttribute('hidden'),
    h: Math.round(r.height),
    n: chips.length,
    names: chips.map(c => c.textContent.trim()),
    tag: (document.querySelector('.dk-tag')||{}).textContent || '',
    clickable: chips.some(c => c.closest('a')),
    overlap: Math.round(worst), who: String(who).slice(0,30),
    overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth)
  };
}
"""


def run(br, tag, desk, lang="vi", w=1440, h=900):
    ctx = br.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(seed(lang))
    pg.add_init_script(stub(desk, lang))
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_selector(".stats-hud", timeout=9000)
    pg.wait_for_timeout(1100)
    d = pg.evaluate(JS)
    d["errs"] = errs
    if desk and d.get("n"):
        pg.screenshot(path="desk-%s.png" % tag,
                      clip={"x": 240, "y": max(0, 0), "width": 960, "height": 700})
    ctx.close()
    return d


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("=== [1] Co 3 mau vat trung — phai VE RA (day la loi da bao) ===")
        d = run(br, "3mon", DESK)
        chk("hang hien ra", not d["hidden"] and d["display"] != "none",
            "display=%s hidden=%s" % (d["display"], d["hidden"]))
        chk("ve dung 3 chip", d["n"] == 3, "%d chip" % d["n"])
        chk("hien TEN mau vat (khong phai id tho)",
            all("-" not in n.split(" ")[-1] for n in d["names"]) and
            not any(x in " ".join(d["names"]) for x in DESK),
            " · ".join(d["names"]))
        chk("co nhan hang", "BÀN ĐIỀU KHIỂN" in d["tag"].upper(), d["tag"])
        chk("chip KHONG bam duoc (cho trung bay, khong phai duong di)", not d["clickable"])
        chk("khong che chu nao trong bang Thong Ke", d["overlap"] == 0,
            "che %dpx2 boi %s" % (d["overlap"], d["who"]))
        chk("trang khong tran ngang", d["overflow"] == 0, "%dpx" % d["overflow"])
        chk("0 loi trang", not d["errs"], str(d["errs"][:1])[:90])

        print("\n=== [2] CHUA trung gi — phai an HAN, khong hien nhan rong ===")
        d0 = run(br, "0mon", [])
        chk("hang bi an", d0["display"] == "none" or d0["hidden"],
            "display=%s hidden=%s" % (d0["display"], d0["hidden"]))
        chk("KHONG chiem chieu cao nao", d0["h"] == 0, "%dpx" % d0["h"])
        chk("0 loi trang", not d0["errs"], str(d0["errs"][:1])[:90])

        print("\n=== [3] Ban EN — ten mau vat phai dich ===")
        de = run(br, "en", DESK, lang="en")
        chk("ve du 3 chip", de["n"] == 3, "%d" % de["n"])
        chk("nhan hang dich", "CONSOLE" in de["tag"].upper(), de["tag"])
        chk("ten mau vat KHAC ban tieng Viet", de["names"] != d["names"],
            " · ".join(de["names"]))

        print("\n=== [4] Dien thoai 390x844 ===")
        dm = run(br, "mobile", DESK, w=390, h=844)
        chk("ve du 3 chip", dm["n"] == 3, "%d" % dm["n"])
        chk("khong tran ngang", dm["overflow"] == 0, "%dpx" % dm["overflow"])
        chk("khong che chu nao", dm["overlap"] == 0,
            "che %dpx2 boi %s" % (dm["overlap"], dm["who"]))

        print("\n=== [5] Mau vat la id la (server co, client chua co ten) ===")
        dx = run(br, "idla", ["mau-vat-khong-ton-tai"])
        chk("van ve ra (khong an mat thu tre da chon)", dx["n"] == 1, "%d chip" % dx["n"])
        chk("0 loi trang", not dx["errs"], str(dx["errs"][:1])[:90])

        br.close()

    print("\n" + "=" * 58)
    print(f"KET QUA: {ok} dat / {bad} hong")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
