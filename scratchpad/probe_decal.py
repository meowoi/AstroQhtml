# -*- coding: utf-8 -*-
"""Do hinh dan tren BAN VE THAT.

[1] shop.html — gieo AstroQAuth MUON (dung nhip module ES) => phai hien du 3 khoi va
    14 mon. Day la phep do chung minh loi "cua hang rong" da het.
[2] dashboard.html — moi hinh dan x 7 kho man: hien ra THAT (co pixel ve), khong che
    chu nao, khong nuot cu bam, khong lam trang tran ngang; va 'chua dan gi' thi
    KHONG an mot pixel bo cuc nao.
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
DECALS = ["decal-none", "decal-comet", "decal-orbit", "decal-ringed", "decal-stars"]

VIEWS = [
    ("desktop-1440", 1440, 900),
    ("laptop-1280", 1280, 800),
    ("ipad-ngang", 1180, 820),
    ("ipad-doc", 820, 1180),
    ("mobile-390", 390, 844),
    ("mobile-360", 360, 740),
    ("fullhd", 1920, 1080),
]

ITEMS = """[
  {id:"cockpit-cyan",kind:"theme",price:0},{id:"cockpit-amber",kind:"theme",price:60},
  {id:"cockpit-violet",kind:"theme",price:90},{id:"cockpit-mint",kind:"theme",price:120},
  {id:"cockpit-rose",kind:"theme",price:150},
  {id:"frame-steel",kind:"frame",price:0},{id:"frame-gold",kind:"frame",price:40},
  {id:"frame-nebula",kind:"frame",price:70},{id:"frame-ice",kind:"frame",price:100},
  {id:"decal-none",kind:"decal",price:0},{id:"decal-comet",kind:"decal",price:40},
  {id:"decal-orbit",kind:"decal",price:60},{id:"decal-ringed",kind:"decal",price:80},
  {id:"decal-stars",kind:"decal",price:110}
]"""

LATE_STUB = """
window.__A = {
  getShop: function(){ return Promise.resolve({ ok:true, data:{
    kinds:["theme","frame","decal"], items: %s, owned:["decal-comet"],
    equipped:{theme:"cockpit-cyan",frame:"frame-steel",decal:"decal-none"}, ship:"",
    wallet:{meteors:636} }}); },
  buyCosmetic:function(){return Promise.resolve({ok:false});},
  equipCosmetic:function(){return Promise.resolve({ok:false});},
  updateProfile:function(){return Promise.resolve({ok:false});}
};
var s=document.createElement('script'); s.type='module';
s.textContent="Object.defineProperty(window,'AstroQAuth',{configurable:true,get:function(){return window.__A;},set:function(){}});";
document.addEventListener('readystatechange',function(){
  if(document.readyState==='interactive' && !window.__inj){ window.__inj=true; document.head.appendChild(s); }
});
""" % ITEMS

MEASURE = """
() => {
  const d = document.querySelector('.decal');
  if (!d) return {err:'khong co .decal'};
  const cs = getComputedStyle(d);
  const r  = d.getBoundingClientRect();
  const px = s => parseFloat(s) || 0;
  const b = getComputedStyle(d,'::before'), a = getComputedStyle(d,'::after');
  // Chong lan voi moi phan tu CO CHU RIENG trong header + trang
  let worst = 0, who = '';
  document.querySelectorAll('.statusbar *, .hero *, .stats-hud *, .hud *').forEach(e => {
    if (e === d || d.contains(e) || e.contains(d)) return;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const q = e.getBoundingClientRect();
    if (!q.width || !q.height) return;
    const w = Math.max(0, Math.min(r.right,q.right) - Math.max(r.left,q.left));
    const h = Math.max(0, Math.min(r.bottom,q.bottom) - Math.max(r.top,q.top));
    if (w*h > worst) { worst = w*h; who = (e.className||e.tagName)+' '+e.textContent.trim().slice(0,18); }
  });
  const hit = r.width ? document.elementFromPoint(r.left+r.width/2, r.top+r.height/2) : null;
  const sb = document.querySelector('.statusbar').getBoundingClientRect();
  return {
    display: cs.display,
    w: Math.round(r.width), h: Math.round(r.height),
    drawn: Math.round(px(b.width)*px(b.height) + px(a.width)*px(a.height)),
    inView: r.width ? (r.top >= 0 && r.left >= 0 && r.right <= innerWidth) : true,
    overlap: Math.round(worst), who: String(who).slice(0,40),
    hitIsDecal: !!(hit && hit.classList && hit.classList.contains('decal')),
    sbH: Math.round(sb.height),
    docOverflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
    shipIdW: Math.round(document.querySelector('.ship-id').getBoundingClientRect().width)
  };
}
"""

ok = bad = 0


def chk(name, cond, extra=""):
    global ok, bad
    if cond:
        ok += 1
        print(f"  [OK]   {name}" + (f"  ({extra})" if extra else ""))
    else:
        bad += 1
        print(f"  [HONG] {name}" + (f"  ({extra})" if extra else ""))


def seed(decal):
    return ("localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-asteroids','636');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1');"
            "localStorage.setItem('astroq-user', JSON.stringify({"
            "  name:'Test', pilotName:'Test', uid:'u-test',"
            "  equipped:{theme:'cockpit-cyan',frame:'frame-steel',decal:'%s'},"
            "  ship:'Luna Mot'}));" % decal)


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("=== [1] shop.html — gieo AstroQAuth MUON (nhip that cua module ES) ===")
        ctx = br.new_context(viewport={"width": 1440, "height": 1000})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.add_init_script(LATE_STUB)
        pg.goto(BASE + "/shop.html", wait_until="load")
        pg.wait_for_selector("#kinds .citem", timeout=9000)
        pg.wait_for_timeout(500)
        n_it = pg.locator("#kinds .citem").count()
        chk("gieo MUON van hien du mon (loi cua hang rong da het)", n_it == 14, f"{n_it} mon")
        chk("du 3 khoi loai mon", pg.locator("#kinds section").count() == 3)
        chk("KHONG con dai 'can dang nhap'", not pg.locator("#offline").is_visible())
        names = pg.eval_on_selector_all("#kinds .cnm", "e=>e.map(x=>x.textContent)")
        chk("co ten 5 hinh dan tieng Viet",
            all(x in names for x in ["Chưa dán gì", "Sao Chổi Bay", "Vòng Quỹ Đạo",
                                     "Hành Tinh Có Vành", "Chùm Sao Nhỏ"]),
            " · ".join(names[9:]))
        drawn = pg.evaluate("""() => {
          const out = {};
          document.querySelectorAll('[class*="cos-sw--decal-"]').forEach(el => {
            const id = [...el.classList].find(c => c.startsWith('cos-sw--decal-'));
            const px = s => parseFloat(s)||0;
            const b = getComputedStyle(el,'::before'), a = getComputedStyle(el,'::after');
            const r = el.getBoundingClientRect();
            out[id] = {area: Math.round(px(b.width)*px(b.height) + px(a.width)*px(a.height)),
                       fits: px(b.width) <= r.width && px(a.width) <= r.width};
          });
          return out;
        }""")
        for k, v in sorted(drawn.items()):
            if k.endswith("decal-none"):
                chk("o xem truoc 'chua dan gi' de TRONG", v["area"] == 0, f"{v['area']} px2")
            else:
                chk(f"o xem truoc {k[8:]}: co hinh va KHONG tran o",
                    v["area"] > 200 and v["fits"], str(v))
        chk("0 loi trang", not errs, "; ".join(errs[:2])[:110])
        pg.screenshot(path="shop-fixed.png", full_page=True)
        ctx.close()

        print("\n=== [2] dashboard.html — 5 hinh dan x 7 kho man ===")
        base_sb = {}
        for dec in DECALS:
            for vname, w, h in VIEWS:
                ctx = br.new_context(viewport={"width": w, "height": h})
                pg = ctx.new_page()
                pg.add_init_script(seed(dec))
                pg.goto(BASE + "/dashboard.html", wait_until="load")
                pg.wait_for_selector(".statusbar", timeout=9000)
                pg.wait_for_timeout(700)
                r = pg.evaluate(MEASURE)
                tag = f"{dec} @ {vname}"
                if r.get("err"):
                    chk(tag, False, r["err"]); ctx.close(); continue

                if dec == "decal-none":
                    base_sb[vname] = (r["sbH"], r["shipIdW"])
                    chk(f"{tag}: KHONG chiem cho nao", r["display"] == "none" and r["w"] == 0,
                        f"display={r['display']} w={r['w']}")
                else:
                    chk(f"{tag}: hien ra + co ve hinh",
                        r["display"] != "none" and r["w"] >= 20 and r["drawn"] > 100,
                        f"{r['w']}x{r['h']} · ve {r['drawn']}px2")
                    chk(f"{tag}: nam trong khung nhin", r["inView"])
                    # Header cao them bao nhieu so voi 'chua dan gi'
                    b = base_sb.get(vname)
                    if b:
                        chk(f"{tag}: header KHONG cao them", r["sbH"] == b[0],
                            f"{b[0]}px -> {r['sbH']}px")
                chk(f"{tag}: khong che chu nao", r["overlap"] == 0,
                    f"che {r['overlap']}px2 boi {r['who']}")
                chk(f"{tag}: khong nuot cu bam", not r["hitIsDecal"])
                chk(f"{tag}: trang khong tran ngang", r["docOverflow"] == 0,
                    f"tran {r['docOverflow']}px")
                if vname == "desktop-1440" and dec != "decal-none":
                    pg.screenshot(path=f"dash-{dec}.png",
                                  clip={"x": 0, "y": 0, "width": 700, "height": 90})
                ctx.close()

        br.close()

    print("\n" + "=" * 62)
    print(f"KET QUA: {ok} dat / {bad} hong")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
