# -*- coding: utf-8 -*-
"""Do vet lua NGAY TRONG TRANG o cac khung hinh lien tiep sau cu bay len
   (khong chup anh o giua nen khong bi tre nhip)."""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
from PIL import Image

URL = "http://127.0.0.1:8123/game-dodge.html"
OUT = os.path.dirname(os.path.abspath(__file__))
fails = []
def check(c, m):
    print(("   PASS  " if c else "   FAIL  ") + m)
    if not c: fails.append(m)

PROBE = r"""
() => new Promise(resolve => {
  const cv=document.getElementById('cv'), g=cv.getContext('2d');
  const sx=cv.width/800, sy=cv.height/500;
  function scan(){
    // tim than Byte: hang co nhieu pixel sang nhat trong dai x 150..270
    const x0=Math.round(150*sx), w=Math.round(120*sx);
    const d=g.getImageData(x0,0,w,cv.height).data;
    const cnt=new Int32Array(cv.height);
    for(let y=0;y<cv.height;y++){ let c=0;
      for(let x=0;x<w;x++){ const i=(y*w+x)*4;
        if(d[i]>170&&d[i+1]>195&&d[i+2]>210) c++; }
      cnt[y]=c; }
    let peak=0, py=0;
    for(let y=0;y<cv.height;y++) if(cnt[y]>peak){peak=cnt[y];py=y;}
    // dem pixel lua (vang/cam) chia theo ben trai / ben phai tam Byte (x ao = 200)
    let L=0,R=0, minx=1e9;
    for(let y=Math.max(0,py-Math.round(30*sy)); y<Math.min(cv.height,py+Math.round(30*sy)); y++){
      for(let x=0;x<w;x++){
        const i=(y*w+x)*4, r=d[i],gg=d[i+1],b=d[i+2];
        if(r>195 && gg>165 && b<205 && r-b>35){
          const vx=x/sx+150;
          if(vx<200) { L++; if(vx<minx) minx=vx; } else R++;
        }
      }
    }
    return { byteY:Math.round(py/sy), peak:peak, L:L, R:R, minx:minx<1e9?Math.round(minx):null };
  }
  const out=[];
  document.dispatchEvent(new KeyboardEvent('keydown',{key:' ',bubbles:true}));
  let n=0;
  function step(){
    out.push(scan()); n++;
    if(n===3) document.dispatchEvent(new KeyboardEvent('keyup',{key:' ',bubbles:true}));
    if(n<7) requestAnimationFrame(step); else resolve(out);
  }
  requestAnimationFrame(step);
})
"""

with sync_playwright() as pw:
    br = pw.chromium.launch()
    page = br.new_context(viewport={"width": 1280, "height": 800}).new_page()
    page.on("pageerror", lambda e: fails.append("pageerror: %s" % e))
    page.goto(URL, wait_until="load")
    page.evaluate("()=>{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-asteroids','60')}")
    page.reload(wait_until="load"); page.wait_for_timeout(800)
    page.click("#start-btn"); page.wait_for_timeout(250)

    rows = page.evaluate(PROBE)
    print("   khung | byteY | px sang | lua-trai | lua-phai | lua xa nhat (x ao)")
    for i, r in enumerate(rows):
        print("   %5d | %5d | %7d | %8d | %8d | %s" % (i, r["byteY"], r["peak"], r["L"], r["R"], r["minx"]))
    maxL = max(r["L"] for r in rows)
    maxR = max(r["R"] for r in rows)
    ys = [r["byteY"] for r in rows]
    check(maxL > 10, "co vet lua ben trai Byte (dinh %d pixel)" % maxL)
    check(maxL > maxR * 2, "lua tap trung ben trai (trai %d / phai %d)" % (maxL, maxR))
    check(min(ys) < ys[0] or ys[0] < 210, "Byte bay LEN sau cu bam (y: %s)" % ys)
    far = [r["minx"] for r in rows if r["minx"] is not None]
    if far: check(min(far) < 180, "lua vuot ra ngoai than Byte (x nho nhat %d < 180)" % min(far))

    # chup + phong to dung tam Byte cua khung cuoi
    byteY = rows[2]["byteY"]
    page.evaluate("()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:' ',bubbles:true}))")
    page.screenshot(path=os.path.join(OUT, "12-flame.png"))
    box = page.evaluate("""()=>{const c=document.getElementById('cv').getBoundingClientRect();
                               return {x:c.x,y:c.y,w:c.width,h:c.height};}""")
    cx = box["x"] + box["w"] * 0.25
    cy = box["y"] + box["h"] * (byteY / 500.0)
    Image.open(os.path.join(OUT, "12-flame.png")).crop(
        (int(cx - 80), int(cy - 55), int(cx + 55), int(cy + 55))).resize((540, 440), Image.NEAREST)\
        .save(os.path.join(OUT, "zoom-flame.png"))
    print("   anh -> zoom-flame.png (tam Byte y=%d)" % byteY)
    br.close()

print("=== %s ===" % ("TAT CA DAT" if not fails else "%d HONG" % len(fails)))
for f in fails: print("   -", f)
sys.exit(1 if fails else 0)
