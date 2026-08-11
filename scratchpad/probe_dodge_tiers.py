# -*- coding: utf-8 -*-
"""probe_dodge_tiers.py — SOI MẮT các cấp cao của Né Thiên Thạch.

Cách chạy:  python -m http.server 8123   rồi   python scratchpad/probe_dodge_tiers.py

⚠️ VÌ SAO PHẢI RÚT NGẮN MỐC CẤP BẰNG `route`: cấp 3 bắt đầu ở giây 52 và cấp 5 ở
   giây 120, mà autopilot sống ~10–16 giây. Không có cách nào chụp được cấp 4–5 bằng
   cách chơi thẳng. `route` chặn chính file HTML rồi đổi các mốc `at:` — KHÔNG sửa
   file trên đĩa, nên không có nguy cơ để lại bản đã phá (bài học 02/08).

Đo hai thứ mắt phải thấy: (a) đá LỚN có thật và nằm gọn trong 2 làn, (b) lời báo
lên cấp hiện ra đúng chữ.
"""
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-dodge.html"
FAST = {"at:24": "at:4", "at:52": "at:8", "at:84": "at:12", "at:120": "at:16"}

# Autopilot rút gọn: chỉ cần tàu sống, không cần ăn tt.
AUTO = r"""
() => {
  const cv=document.getElementById('cv'), g=cv.getContext('2d');
  const SX=()=>cv.width/800, SY=()=>cv.height/500;
  const isRock=(r,gg,b)=> r>46&&gg>52&&Math.abs(r-gg)<32&&b>=gg-14&&Math.max(r,gg,b)<200;
  function byteY(){
    const sx=SX(), sy=SY(), x0=Math.max(0,Math.round(180*sx)), w=Math.round(46*sx);
    const d=g.getImageData(x0,0,w,cv.height).data, cnt=new Int32Array(cv.height);
    for(let y=0;y<cv.height;y++){ let c=0;
      for(let x=0;x<w;x++){ const i=(y*w+x)*4; if(d[i]>165&&d[i+1]>185&&d[i+2]>205) c++; }
      cnt[y]=c; }
    let peak=0,py=-1; for(let y=0;y<cnt.length;y++) if(cnt[y]>peak){peak=cnt[y];py=y;}
    if(peak<6) return null;
    let s=0,n=0; const rad=Math.round(22*sy);
    for(let y=Math.max(0,py-rad);y<Math.min(cnt.length,py+rad);y++){ s+=y*cnt[y]; n+=cnt[y]; }
    return (s/n)/sy;
  }
  function band(v0,v1){
    const sx=SX(), sy=SY();
    const x0=Math.max(0,Math.round(v0*sx)), x1=Math.min(cv.width,Math.round(v1*sx));
    if(x1-x0<2) return null;
    const w=x1-x0, d=g.getImageData(x0,0,w,cv.height).data, rock=new Uint8Array(cv.height);
    let any=false, st=Math.max(1,Math.round(3*sx));
    for(let y=0;y<cv.height;y++){ let n=0;
      for(let x=0;x<w;x+=st){ const i=(y*w+x)*4;
        if(isRock(d[i],d[i+1],d[i+2])){ if(++n>=3){ rock[y]=1; any=true; break; } } } }
    if(!any) return null;
    let best=null,s=-1;
    for(let y=0;y<rock.length;y++){
      if(!rock[y]){ if(s<0) s=y; }
      else { if(s>=0&&(!best||y-s>best[1]-best[0])) best=[s,y]; s=-1; } }
    if(s>=0&&(!best||rock.length-s>best[1]-best[0])) best=[s,rock.length];
    if(!best||(best[1]-best[0])/sy<34) return null;
    return ((best[0]+best[1])/2)/sy;
  }
  function nextX(){
    const sx=SX();
    for(let v=232;v<=770;v+=14){
      const x0=Math.round(v*sx), w=Math.max(2,Math.round(6*sx));
      if(x0+w>cv.width) break;
      const d=g.getImageData(x0,0,w,cv.height).data; let n=0;
      for(let k=0;k<d.length;k+=4) if(isRock(d[k],d[k+1],d[k+2]) && ++n>=14) return v;
    }
    return null;
  }
  const st={target:250}; window.__auto=st;
  const key=t=>document.dispatchEvent(new KeyboardEvent(t,{key:' ',bubbles:true}));
  let hold=0;
  (function tick(){
    const now=performance.now(), rx=nextX();
    if(rx!=null){ const c=band(rx-12,rx+120); if(c!=null) st.target=c; }
    const y=byteY();
    if(y!=null){
      if(st.py!=null&&st.pt) st.vy=(y-st.py)/Math.max(0.008,(now-st.pt)/1000);
      st.py=y; st.pt=now;
      if(y>st.target+6 && (st.vy||0)>-80 && now>hold){ key('keydown'); hold=now+30; }
    }
    if(now>hold) key('keyup');
    if(window.__on) requestAnimationFrame(tick); else key('keyup');
  })();
}
"""


def main():
    out = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": 1280, "height": 800})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        def patch(route):
            r = route.fetch()
            b = r.text()
            for k, v in FAST.items():
                assert k in b, "khong khop moc cap %s" % k
                b = b.replace(k, v)
            route.fulfill(response=r, body=b)

        pg.route("**/game-dodge.html", patch)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');"
                           "localStorage.setItem('astroq-asteroids','60');")
        pg.goto(URL, wait_until="load")
        pg.wait_for_selector("#ov-start.show")
        pg.click("#start-btn")
        pg.evaluate("() => { window.__on = true; }")
        pg.evaluate(AUTO)

        # chụp quanh từng mốc lên cấp; hồi sinh bằng cách bấm "Chơi lại" nếu chết
        for label, at in (("cap2", 4.6), ("cap3", 8.6), ("cap4", 12.6), ("cap5", 16.6)):
            while True:
                st = pg.evaluate("""() => ({
                  over: !!document.querySelector('#ov-over.show'),
                  lvl: (document.getElementById('lvl')||{}).textContent,
                  dist: (document.getElementById('dist')||{}).textContent,
                  toast: (document.getElementById('toast')||{}).textContent,
                  toastOn: !!document.querySelector('#toast.show')
                })""")
                if st["over"]:
                    pg.click("#again-btn")
                    pg.wait_for_timeout(200)
                    continue
                break
            pg.wait_for_timeout(400)
            st = pg.evaluate("""() => ({
              lvl: (document.getElementById('lvl')||{}).textContent,
              toast: (document.getElementById('toast')||{}).textContent,
              toastOn: !!document.querySelector('#toast.show')
            })""")
            p = "scratchpad/tier-%s.png" % label
            pg.screenshot(path=p)
            out.append((label, st["lvl"], st["toast"] if st["toastOn"] else "", p))
            print("  %-6s chip=%-8r toast=%r -> %s"
                  % (label, st["lvl"], st["toast"] if st["toastOn"] else "", p))
            # chờ tới mốc kế
            pg.wait_for_timeout(3600)
        pg.evaluate("() => { window.__on = false; }")
        print("\n  loi trang: %d %s" % (len(errs), errs[:2]))
        br.close()
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
