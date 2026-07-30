# -*- coding: utf-8 -*-
"""Kiem RIENG duong di cua Thien thach tim trong trinh duyet that:
   an vien -> +10 diem + 1 vao vi tam -> ket luot onFinishGame() cong vao vi chinh.
   Autopilot uu tien lao vao vien tt khi no sap toi tam Byte."""
import os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8123/game-dodge.html"
OUT = os.path.dirname(os.path.abspath(__file__))

AUTOPILOT = r"""
() => {
  const cv=document.getElementById('cv'), g=cv.getContext('2d');
  const SX=()=>cv.width/800, SY=()=>cv.height/500;
  const isRock=(r,gg,b)=>r>46&&gg>52&&Math.abs(r-gg)<32&&b>=gg-14;

  function byteY(){
    const sx=SX(), sy=SY(), x0=Math.max(0,Math.round(180*sx)), w=Math.round(46*sx);
    const d=g.getImageData(x0,0,w,cv.height).data, cnt=new Int32Array(cv.height);
    for(let y=0;y<cv.height;y++){ let c=0;
      for(let x=0;x<w;x++){ const i=(y*w+x)*4; if(d[i]>165&&d[i+1]>185&&d[i+2]>205) c++; }
      cnt[y]=c; }
    let peak=0,py=-1;
    for(let y=0;y<cnt.length;y++) if(cnt[y]>peak){peak=cnt[y];py=y;}
    if(peak<6) return null;
    let s=0,n=0; const rad=Math.round(22*sy);
    for(let y=Math.max(0,py-rad);y<Math.min(cnt.length,py+rad);y++){ s+=y*cnt[y]; n+=cnt[y]; }
    return (s/n)/sy;
  }
  function gapAt(vx){
    const sx=SX(), sy=SY(), x0=Math.round(vx*sx), w=Math.max(2,Math.round(7*sx));
    if(x0+w>cv.width) return null;
    const d=g.getImageData(x0,0,w,cv.height).data, rock=[];
    for(let y=0;y<cv.height;y++){ let h=0;
      for(let x=0;x<w;x++){ const i=(y*w+x)*4; if(isRock(d[i],d[i+1],d[i+2])) h++; }
      rock.push(h>w/2); }
    if(!rock.some(Boolean)) return null;
    let best=null,s=-1;
    for(let y=0;y<rock.length;y++){
      if(!rock[y]){ if(s<0) s=y; } else { if(s>=0&&(!best||y-s>best[1]-best[0])) best=[s,y]; s=-1; } }
    if(s>=0&&(!best||rock.length-s>best[1]-best[0])) best=[s,rock.length];
    if(!best||best[1]-best[0]<40) return null;
    return ((best[0]+best[1])/2)/sy;
  }
  function gems(){                        // TAT CA vien tt dang tren san
    const sx=SX(), sy=SY(), d=g.getImageData(0,0,cv.width,cv.height).data, w=cv.width;
    const found=[];
    for(let y=0;y<cv.height;y+=3) for(let x=0;x<w;x+=3){
      const i=(y*w+x)*4, r=d[i],gg=d[i+1],b=d[i+2];
      if(b>215&&r>140&&r<235&&gg<150&&b-gg>80){
        let m=null;
        for(const f of found) if(Math.abs(f.x-x)<26*sx&&Math.abs(f.y-y)<26*sy){ m=f; break; }
        if(m){ m.x=(m.x*m.n+x)/(m.n+1); m.y=(m.y*m.n+y)/(m.n+1); m.n++; }
        else found.push({x:x,y:y,n:1});
      }
    }
    return found.filter(f=>f.n>3).map(f=>({x:f.x/sx, y:f.y/sy})).sort((a,b)=>a.x-b.x);
  }

  const st={target:250,taps:0,frames:0,gemLock:0,src:"mid",latch:0};
  window.__auto=st;
  const key=t=>document.dispatchEvent(new KeyboardEvent(t,{key:' ',bubbles:true}));
  let holdUntil=0;
  function tick(){
    st.frames++; const now=performance.now();
    let gap=null,gapX=null;
    for(let vx=248;vx<=760;vx+=26){ const r=gapAt(vx); if(r!=null){ gap=r; gapX=vx; break; } }
    const gs=gems();
    // Uu tien vien tt sap den tam Byte (x 200) — day moi la luc an duoc
    const soon=gs.find(v=>v.x>185&&v.x<430);
    if(soon){ st.target=soon.y; st.src="gem"; st.gemLock++; st.latch=now+900; }
    else if(gap!=null){ st.target=gap; st.src="gap"; st.latch=now+1200; }
    else if(now>st.latch){ st.target=250; st.src="mid"; }

    const y=byteY(); st.y=y;
    if(y!=null){
      if(st.py!=null&&st.pt) st.vy=(y-st.py)/Math.max(0.008,(now-st.pt)/1000);
      st.py=y; st.pt=now;
      if(y+(st.vy||0)*0.10 > st.target+4 && now>holdUntil){ key('keydown'); st.taps++; holdUntil=now+28; }
    }
    if(now>holdUntil) key('keyup');
    if(window.__autoOn) requestAnimationFrame(tick); else key('keyup');
  }
  window.__autoOn=true; requestAnimationFrame(tick); return true;
}
"""

ATTEMPTS = 8
with sync_playwright() as pw:
    br = pw.chromium.launch()
    page = br.new_context(viewport={"width": 1280, "height": 800}).new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append("console.error: " + m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="load")
    page.evaluate("()=>{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-asteroids','200')}")
    page.reload(wait_until="load"); page.wait_for_timeout(900)

    won = None
    for a in range(ATTEMPTS):
        bal0 = int(page.evaluate("()=>document.getElementById('bal').textContent"))
        page.click("#start-btn" if a == 0 else "#again-btn")
        page.wait_for_timeout(120)
        page.evaluate(AUTOPILOT)
        t0 = time.time(); mid_shot = False
        while time.time() - t0 < 25:
            page.wait_for_timeout(200)
            live = page.evaluate("""()=>({m:+document.getElementById('mined').textContent,
                                         s:+document.getElementById('score').textContent,
                                         d:+document.getElementById('dist').textContent,
                                         over:document.getElementById('ov-over').classList.contains('show')})""")
            if live["m"] > 0 and not mid_shot:      # chup ngay khi vua an duoc vien dau
                mid_shot = True
                page.screenshot(path=os.path.join(OUT, "10-gem-collected.png"))
                print("   lan %d: AN DUOC vien tt -> diem %d, quang duong %d (%d + 10x%d = %d)"
                      % (a + 1, live["s"], live["d"], live["d"], live["m"], live["d"] + 10 * live["m"]))
                assert live["s"] == live["d"] + 10 * live["m"], "diem phai = quang duong + 10/vien"
            if live["over"]: break
        page.evaluate("()=>{window.__autoOn=false}")
        page.wait_for_selector("#ov-over.show", timeout=15000)
        toast = page.evaluate("""()=>{const t=document.getElementById('toast');
            return {show:t.classList.contains('show'), txt:t.textContent.trim(), html:t.innerHTML};}""")
        page.wait_for_timeout(900)
        r = page.evaluate("""()=>({mined:+document.getElementById('r-mined').textContent,
                                   score:+document.getElementById('r-score').textContent,
                                   dist:+document.getElementById('r-dist').textContent,
                                   bal:+document.getElementById('bal').textContent,
                                   paidHtml:document.getElementById('paid').innerHTML,
                                   paidTxt:document.getElementById('paid').textContent.trim(),
                                   none:document.getElementById('paid').classList.contains('none')})""")
        auto = page.evaluate("()=>window.__auto")
        print("lan %d: %ds | diem %d | thu %d tt | vi %d -> %d | bat %d | thay gem %d frame"
              % (a + 1, r["dist"], r["score"], r["mined"], bal0 - 5, r["bal"], auto["taps"], auto["gemLock"]))
        assert r["bal"] == bal0 - 5 + r["mined"], \
            "vi sai: %d != %d - 5 + %d" % (r["bal"], bal0, r["mined"])
        assert r["score"] == r["dist"] + 10 * r["mined"], "diem sai o bang ket qua"
        print("        toast luc ket luot: show=%s %r" % (toast["show"], toast["txt"]))
        if r["mined"] > 0:
            # toast phai bao "+n tt vao vi" (bug cu: bien `paid` trung id phan tu -> toast chet lang)
            assert toast["show"] and str(r["mined"]) in toast["txt"], \
                "thieu toast thuong: %r" % toast["txt"]
            won = r
            page.screenshot(path=os.path.join(OUT, "11-over-with-gems.png"))
            break

    print()
    if won:
        print("=== DAT: duong tt chay dung tu dau den cuoi ===")
        print("   thu %d vien -> diem %d = %dm + 10x%d" % (won["mined"], won["score"], won["dist"], won["mined"]))
        print("   vi chinh cong dung %d vien luc ket luot (onFinishGame)" % won["mined"])
        print("   dong thong bao: %r | class none = %s" % (won["paidTxt"], won["none"]))
        ok = ("<b>%d</b>" % won["mined"]) in won["paidHtml"] and not won["none"]
        print("   in dung so vien + KHONG dung mau xam:", ok)
    else:
        print("=== KHONG DAT: %d lan thu deu 0 vien ===" % ATTEMPTS)
    print("loi console/JS:", len(errs))
    for e in errs[:5]: print("   !", e)
    page.evaluate("()=>localStorage.setItem('astroq-asteroids','50')")
    br.close()
sys.exit(0 if won and not errs else 1)
