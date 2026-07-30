# -*- coding: utf-8 -*-
"""Kiem phi thuyen Luna lam nhan vat dieu khien trong Space Defender:
   - anh img/luna2.png co thuc su duoc ve (khong lui ve ban vector)
   - CA TAU QUAY theo huong ngam: luong lua hong o duoi tau phai luon nam
     NGUOC huong ngam (do bang tam khoi pixel hong quanh tam san)
   - dan bay ra tu MUI tau, khong phai tu tam
"""
import os, sys, math
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
from PIL import Image

URL = "http://127.0.0.1:8123/game-defender.html"
OUT = os.path.dirname(os.path.abspath(__file__))
fails, errors = [], []
def check(c, m):
    print(("   PASS  " if c else "   FAIL  ") + m)
    if not c: fails.append(m)

# Tam khoi pixel HONG RUC (luong lua o duoi tau) trong ban kinh quanh tam san.
# Ban kinh nho de dan/thien thach tim khong lot vao.
FLAME = r"""
(rad) => {
  const cv=document.getElementById('cv'), g=cv.getContext('2d');
  const sx=cv.width/600, sy=cv.height/600;
  const cx=cv.width/2, cy=cv.height/2, R=Math.round(rad*sx);
  const d=g.getImageData(cx-R,cy-R,R*2,R*2).data, w=R*2;
  let mx=0,my=0,n=0;
  for(let y=0;y<w;y++) for(let x=0;x<w;x++){
    const i=(y*w+x)*4, r=d[i],gg=d[i+1],b=d[i+2];
    if(r>185 && b>185 && gg<145){ mx+=x; my+=y; n++; }
  }
  if(!n) return null;
  return { n:n, dx:(mx/n-R)/sx, dy:(my/n-R)/sy };   // lech so voi tam, don vi ao
}
"""

def aim_to(page, ang):
    """Ngam theo goc ang (radian, 0 = phai) bang cach dua con tro ra xa theo huong do."""
    page.evaluate("""(a) => {
      const cv=document.getElementById('cv'), r=cv.getBoundingClientRect();
      const vx=300+Math.cos(a)*200, vy=300+Math.sin(a)*200;
      cv.dispatchEvent(new MouseEvent('mousemove',{
        clientX:r.left+vx/600*r.width, clientY:r.top+vy/600*r.height, bubbles:true}));
    }""", ang)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    page = br.new_context(viewport={"width": 1280, "height": 860}).new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console.error: " + m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="load")
    page.evaluate("()=>{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-asteroids','60')}")
    page.reload(wait_until="load"); page.wait_for_timeout(1400)

    print("== 1. Anh phi thuyen co tai duoc va duoc dung khong? ==")
    img = page.evaluate("""()=>{
      const im=[...document.images].find(i=>i.src.indexOf('luna2')>=0);
      return { inDom:!!im, w:0 };
    }""")
    # anh duoc tai bang new Image() nen khong nam trong document.images -> kiem bang mang
    reqs = []
    page.on("response", lambda r: reqs.append(r.url))
    page.reload(wait_until="load"); page.wait_for_timeout(1200)
    luna = [u for u in reqs if "luna2.png" in u]
    print("   request luna2.png:", luna)
    check(len(luna) > 0, "trang co tai img/luna2.png")

    page.click("#start-btn"); page.wait_for_timeout(400)

    print("== 2. Ca tau QUAY theo huong ngam? (luong lua phai nguoc huong ngam) ==")
    print("   goc ngam | lech luong lua (dx,dy) | goc lua | lech so voi 'nguoc huong ngam'")
    worst = 0
    for deg in (0, 90, 180, 270, 45):
        ang = math.radians(deg)
        aim_to(page, ang)
        page.wait_for_timeout(320)
        f = page.evaluate(FLAME, 46)
        if not f or f["n"] < 40:
            check(False, "goc %d: khong thay luong lua (n=%s)" % (deg, f and f["n"]))
            continue
        fang = math.degrees(math.atan2(f["dy"], f["dx"])) % 360
        expect = (deg + 180) % 360
        diff = abs((fang - expect + 180) % 360 - 180)
        worst = max(worst, diff)
        print("   %8d | (%6.1f,%6.1f) n=%4d | %6.1f | lech %.1f do" % (deg, f["dx"], f["dy"], f["n"], fang, diff))
    check(worst < 25, "luong lua luon nguoc huong ngam (lech lon nhat %.1f do) -> ca tau quay 360" % worst)

    print("== 3. Dan bay ra tu MUI tau, khong phai tu tam ==")
    for deg, name in ((0, "phai"), (180, "trai"), (270, "len")):
        ang = math.radians(deg)
        aim_to(page, ang)
        page.wait_for_timeout(200)
        # ban 1 loat roi do vi tri dan ngay sau do
        r = page.evaluate("""(a) => new Promise(res=>{
          const cv=document.getElementById('cv'), rc=cv.getBoundingClientRect();
          const vx=300+Math.cos(a)*200, vy=300+Math.sin(a)*200;
          const cx=rc.left+vx/600*rc.width, cy=rc.top+vy/600*rc.height;
          cv.dispatchEvent(new MouseEvent('mousedown',{button:0,clientX:cx,clientY:cy,bubbles:true}));
          setTimeout(()=>{
            window.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}));
            const g=cv.getContext('2d'), sx=cv.width/600, sy=cv.height/600;
            const d=g.getImageData(0,0,cv.width,cv.height).data, w=cv.width;
            // dan = vet sang trang-tim, tim pixel gan trang nam ngoai than tau
            let best=null;
            for(let y=0;y<cv.height;y+=2) for(let x=0;x<w;x+=2){
              const i=(y*w+x)*4;
              if(d[i]>235&&d[i+1]>225&&d[i+2]>245){
                const vx2=x/sx-300, vy2=y/sy-300, dist=Math.hypot(vx2,vy2);
                if(dist>40 && dist<200 && (!best||dist>best.dist)) best={vx:vx2,vy:vy2,dist:dist};
              }
            }
            res(best);
          },150);
        })""", ang)
        if not r:
            check(False, "ngam %s: khong thay dan bay ra" % name); continue
        bang = math.degrees(math.atan2(r["vy"], r["vx"])) % 360
        diff = abs((bang - deg + 180) % 360 - 180)
        print("   ngam %-5s (%3d do): dan o goc %6.1f, cach tam %5.1f px -> lech %.1f do"
              % (name, deg, bang, r["dist"], diff))
        check(diff < 20, "dan bay dung huong ngam %s (lech %.1f do)" % (name, diff))
    page.wait_for_timeout(200)

    print("== 4. Chup anh phi thuyen o 4 huong ==")
    box = page.evaluate("""()=>{const c=document.getElementById('cv').getBoundingClientRect();
      return {x:c.x,y:c.y,w:c.width,h:c.height};}""")
    tiles = []
    for deg in (0, 90, 180, 270):
        aim_to(page, math.radians(deg)); page.wait_for_timeout(280)
        page.screenshot(path=os.path.join(OUT, "_luna_tmp.png"))
        cx = box["x"] + box["w"] / 2; cy = box["y"] + box["h"] / 2
        im = Image.open(os.path.join(OUT, "_luna_tmp.png")).crop(
            (int(cx - 60), int(cy - 60), int(cx + 60), int(cy + 60))).resize((240, 240), Image.NEAREST)
        tiles.append(im)
    sheet = Image.new("RGB", (240 * 4, 240))
    for i, im in enumerate(tiles): sheet.paste(im, (i * 240, 0))
    sheet.save(os.path.join(OUT, "d10-luna-4huong.png"))
    os.remove(os.path.join(OUT, "_luna_tmp.png"))
    print("   anh -> d10-luna-4huong.png (ngam: phai · duoi · trai · len)")
    page.screenshot(path=os.path.join(OUT, "d11-luna-play.png"))
    print("   anh -> d11-luna-play.png")
    br.close()

print("\n=== loi console/JS: %d ===" % len(errors))
for e in errors[:5]: print("   !", e)
print("=== %s ===" % ("TAT CA DAT" if not fails and not errors else "%d HONG" % (len(fails) + len(errors))))
for f in fails: print("   -", f)
sys.exit(1 if (fails or errors) else 0)
