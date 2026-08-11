# -*- coding: utf-8 -*-
"""Mo game-dodge.html bang Chromium that: autopilot doc pixel canvas de bay,
   chup anh tung man, kiem vi tien + overlay + song ngu, bat moi loi console."""
import os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
URL = "http://127.0.0.1:8123/game-dodge.html"
errors, logs = [], []

# ---- Autopilot chay NGAY TRONG TRANG: do pixel canvas -> ban Space that ----
AUTOPILOT = r"""
() => {
  const cv = document.getElementById('cv'), g = cv.getContext('2d');
  const SX = () => cv.width/800, SY = () => cv.height/500;
  /* ⚠️ PHAI CHAN NGOI SAO NEN. Sao gan trang (#eaf1ff -> 234,241,255) va sao xa
     (#c7d6ff) THOA het dieu kien mau cua da (xam-lam nhat). Ban cu song sot voi
     chuyen do vi `gapAt` doi HON NUA hang la da; ban gop dai cua toi chi doi MOT
     pixel nen moi ngoi sao chan mot hang -> bot tuong ca man hinh la da, nham vao
     cho khong ton tai va chet trong 1,8s. Da sang nhat trong gradient la #8291b0
     (max 176), nen chan o 200 la du rong ma vua loai het sao. */
  const isRock = (r,gg,b) => r>46 && gg>52 && Math.abs(r-gg)<32 && b>=gg-14
                             && Math.max(r,gg,b) < 200;

  function byteY(){    // tim Byte = HANG co nhieu pixel sang nhat (sao nen chi 1-3 px/hang,
                       // than Byte 20-40 px/hang) -> khong bi sao keo lech nhu khi lay trung binh
    const sx=SX(), sy=SY();
    const x0=Math.max(0,Math.round(180*sx)), w=Math.round(46*sx);
    const d=g.getImageData(x0,0,w,cv.height).data;
    const cnt=new Int32Array(cv.height);
    for(let y=0;y<cv.height;y++){
      let c=0;
      for(let x=0;x<w;x++){ const i=(y*w+x)*4; if(d[i]>165&&d[i+1]>185&&d[i+2]>205) c++; }
      cnt[y]=c;
    }
    let peak=0, py=-1;
    for(let y=0;y<cnt.length;y++) if(cnt[y]>peak){ peak=cnt[y]; py=y; }
    if(peak<6) return null;
    let sum=0,n=0;                                  // trung binh quanh dinh (+-22px ao)
    const rad=Math.round(22*sy);
    for(let y=Math.max(0,py-rad); y<Math.min(cnt.length,py+rad); y++){ sum+=y*cnt[y]; n+=cnt[y]; }
    return (sum/n)/sy;
  }
  /* Khoang trong DOC rong nhat trong CA MOT DAI x [vx0,vx1] (toa do ao).
     ⚠️ BAN CU DO TREN MOT LAT x DAY 7px, va do la cach dung cho VAT CAN HINH COT.
        Tu 08/08/2026 vat can la DA ROI rai lech nhau theo x trong cung mot dot, nen
        mot lat mong thuong chi cat qua MOT hon da -> no bao "cho nay trong" trong khi
        lan do bi mot hon khac cua CUNG DOT chan o x lech 40px. Bot vi the nham vao
        cho khong di qua duoc va song sot chi 3,9-11,2s that thuong. Nay gop ca dai:
        chieu doc nao bi da chan o BAT KY x nao trong dai thi coi la bi chan. */
  function gapBand(vx0, vx1){
    const sx=SX(), sy=SY();
    const x0=Math.max(0,Math.round(vx0*sx)), x1=Math.min(cv.width,Math.round(vx1*sx));
    if(x1-x0 < 2) return null;
    const w=x1-x0;
    const d=g.getImageData(x0,0,w,cv.height).data;
    const rock=new Uint8Array(cv.height);
    let any=false;
    const stepX=Math.max(1,Math.round(3*sx));
    for(let y=0;y<cv.height;y++){
      // Doi >=3 pixel da tren hang: mot pixel don le van co the la sao/nhieu nen,
      // ma da thi rong 30-78px nen o buoc 3px luon cho hang chuc pixel.
      let n=0;
      for(let x=0;x<w;x+=stepX){
        const i=(y*w+x)*4;
        if(isRock(d[i],d[i+1],d[i+2])){ if(++n>=3){ rock[y]=1; any=true; break; } }
      }
    }
    if(!any) return null;
    let best=null, s=-1;
    for(let y=0;y<rock.length;y++){
      if(!rock[y]){ if(s<0) s=y; }
      else { if(s>=0 && (!best || y-s>best[1]-best[0])) best=[s,y]; s=-1; }
    }
    if(s>=0 && (!best || rock.length-s>best[1]-best[0])) best=[s,rock.length];
    if(!best || (best[1]-best[0])/sy < 34) return null;   // hep hon tau thi bo
    return ((best[0]+best[1])/2)/sy;
  }
  /** x ao cua hon da gan nhat con o phia truoc mui tau (null = truoc mat trong tron). */
  function nextRockX(){
    const sx=SX();
    for(let vx=232; vx<=770; vx+=14){
      const x0=Math.round(vx*sx), w=Math.max(2,Math.round(6*sx));
      if(x0+w>cv.width) break;
      const d=g.getImageData(x0,0,w,cv.height).data;
      let n=0;
      for(let k=0;k<d.length;k+=4){
        if(isRock(d[k],d[k+1],d[k+2]) && ++n>=14) return vx;   // 14 px: khong phai nhieu nen
      }
    }
    return null;
  }

  function gemAhead(){          // tim vien Thien thach tim gan nhat o phia truoc
    const sx=SX(), sy=SY();
    const x0=Math.round(230*sx);
    const d=g.getImageData(x0,0,cv.width-x0,cv.height).data;
    const w=cv.width-x0;
    let bx=1e9, by=0, n=0;
    for(let y=0;y<cv.height;y+=2) for(let x=0;x<w;x+=2){
      const i=(y*w+x)*4, r=d[i],gg=d[i+1],b=d[i+2];
      if(b>215 && r>140 && r<235 && gg<150 && b-gg>80){        // tim ruc cua vien tt
        if(x<bx-6){ bx=x; by=y; n=1; } else if(Math.abs(x-bx)<40){ by=(by*n+y)/(n+1); n++; }
      }
    }
    return n>4 ? { x:(bx+x0)/sx, y:by/sy } : null;
  }

  const st = { target:250, latch:0, taps:0, frames:0, lostByte:0, gemSeen:0, src:"mid" };
  window.__auto = st;
  function key(type){ document.dispatchEvent(new KeyboardEvent(type,{key:' ',bubbles:true})); }

  let holdUntil=0;
  function tick(){
    st.frames++;
    const now=performance.now();
    // DOT DA GAN NHAT truoc mat moi la thu phai ne: tim hon da dau tien roi do
    // khoang trong tren CA DAI rong 120px cua dot do (mot dot rai ~110px theo x).
    let gap=null, gapX=null;
    const rx=nextRockX();
    if(rx!=null){ gapX=rx; gap=gapBand(rx-12, rx+120); }
    const gem=gemAhead();
    // Chi nham vien tt neu no thuoc DUNG cot gan nhat, khong thi lai lao vao cot truoc no
    if(gem && gapX!=null && Math.abs(gem.x-gapX)<90){ st.target=gem.y; st.gemSeen++; st.src="gem"; st.latch=now+1400; }
    else if(gap!=null){ st.target=gap; st.latch=now+1400; st.src="gap"; }
    else if(gem && gapX==null){ st.target=gem.y; st.src="gem-far"; st.latch=now+900; }
    else if(now>st.latch){ st.target=250; st.src="mid"; }

    const y=byteY();
    st.y=y;
    if(y==null){ st.lostByte++; }
    else {
      // Bo dieu khien du bao: uoc luong van toc roi doan vi tri 0.22s toi.
      // Chi dung vi tri hien tai thi bat luon tre nhip -> dam cot.
      if(st.py!=null && st.pt) st.vy = (y-st.py)/Math.max(0.008,(now-st.pt)/1000);
      st.py=y; st.pt=now;
      // Nhin truoc 0.10s + le 6px: nhin xa hon (0.22s) thi bot luon thay "sap vuot qua"
      // nen khong bao gio ha xuong tram, treo lo lung tren muc tieu ~150px.
      // Giu phim 30ms = mot cu "cham nhe" (~55px), giu lau hon se bay vut ~140px.
      /* ⚠️ CHI BAM KHI DANG THAT SU TUT XUONG DUOI DICH, VA CHUA BAY LEN.
         Ban cu bam theo VI TRI DU DOAN (y + vy*0.10) nen no bam ca khi tau dang o
         TREN dich ma roi nhanh -> cu bam cong don thanh cu vot ~77px, du de len dung
         mep tren. `sim_dodge2.py` do duoc dung loi nay: song sot 4,3s -> 19,7s sau
         khi doi sang luat duoi day. Mot cu bat nhac tau 53px (flapV²/2·gravity). */
      if(y > st.target+6 && (st.vy||0) > -80 && now>holdUntil){
        key('keydown'); st.taps++; holdUntil=now+30;
      }
    }
    if(now>holdUntil) key('keyup');
    if(window.__autoOn) requestAnimationFrame(tick);
    else key('keyup');
  }
  window.__autoOn = true;
  requestAnimationFrame(tick);
  return true;
}
"""


def shot(page, name):
    page.screenshot(path=os.path.join(OUT, name))
    print("   anh ->", name)


def canvas_stats(page):
    return page.evaluate("""() => {
      const cv=document.getElementById('cv'), g=cv.getContext('2d');
      const d=g.getImageData(0,0,cv.width,cv.height).data;
      let n=0,purple=0,bright=0,rock=0,cyan=0; const s=[0,0,0];
      for(let i=0;i<d.length;i+=4){
        const r=d[i],gr=d[i+1],b=d[i+2];
        s[0]+=r;s[1]+=gr;s[2]+=b;n++;
        if(b>150&&r>120&&r<225&&gr<135) purple++;
        if(r>210&&gr>225&&b>235) bright++;
        if(r>46&&gr>52&&Math.abs(r-gr)<32&&b>=gr-14) rock++;
        if(b>190&&gr>150&&r<140) cyan++;
      }
      return { size:cv.width+'x'+cv.height, avg:[0,1,2].map(k=>Math.round(s[k]/n)),
               tim:+(purple/n*100).toFixed(2), sang:+(bright/n*100).toFixed(2),
               da:+(rock/n*100).toFixed(2), cyan:+(cyan/n*100).toFixed(2) };
    }""")


def state(page):
    return page.evaluate("""() => ({
      score:document.getElementById('score').textContent,
      dist:document.getElementById('dist').textContent,
      mined:document.getElementById('mined').textContent,
      best:document.getElementById('best').textContent,
      bal:document.getElementById('bal').textContent,
      ovs:[...document.querySelectorAll('.ov')].filter(o=>o.classList.contains('show')).map(o=>o.id),
      pauseOff:document.getElementById('btn-pause').classList.contains('off'),
      sfxOff:document.getElementById('btn-sfx').classList.contains('off')
    })""")


fails = []
def check(cond, msg):
    print(("   PASS  " if cond else "   FAIL  ") + msg)
    if not cond: fails.append(msg)


with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()
    page.on("console", lambda m: (logs.append((m.type, m.text)),
            errors.append("console.%s: %s" % (m.type, m.text)) if m.type == "error" else None))
    page.on("pageerror", lambda e: errors.append("pageerror: %s" % e))

    print("== 1. Man brief (mac dinh tieng Viet) ==")
    page.goto(URL, wait_until="load")
    # Chromium that bao navigator.language=en-US nen getLang() tra "en";
    # ep VI de kiem dung ban mac dinh cua nguoi dung Viet.
    page.evaluate("() => { localStorage.setItem('astroq-lang','vi'); localStorage.setItem('astroq-asteroids','50'); }")
    page.reload(wait_until="load"); page.wait_for_timeout(1300)
    vi = page.evaluate("""() => ({ title:document.title, tag:document.getElementById('gtag').textContent,
        k:[...document.querySelectorAll('.chip .k')].map(e=>e.textContent),
        how:document.querySelector('.how span').textContent })""")
    print("   VI:", vi)
    check("Né Thiên Thạch" in vi["title"], "mac dinh hien tieng Viet")

    print("== 1b. Nut Am thanh phai bam duoc NGAY o man brief (co overlay) ==")
    page.click("#btn-sfx"); page.wait_for_timeout(200)
    check(state(page)["sfxOff"], "tat tieng duoc khi overlay brief dang hien")
    page.click("#btn-sfx"); page.wait_for_timeout(200)
    check(not state(page)["sfxOff"], "bat lai duoc")
    check(page.evaluate("()=>document.getElementById('btn-pause').classList.contains('is-hidden')"),
          "nut Pause AN o man brief (bam vao vo nghia)")
    print("  ", state(page)); print("   canvas:", canvas_stats(page))
    shot(page, "01-brief.png")
    check(state(page)["ovs"] == ["ov-start"], "chi overlay brief hien luc vao trang")
    check(state(page)["bal"] == "50", "chua tru tt truoc khi bam Bat dau")

    print("== 2. Bat dau + autopilot bay ==")
    page.click("#start-btn"); page.wait_for_timeout(150)
    check(state(page)["bal"] == "45", "tru dung 5 tt mot lan (bal=%s)" % state(page)["bal"])
    check(not page.evaluate("()=>document.getElementById('btn-pause').classList.contains('is-hidden')"),
          "nut Pause HIEN khi dang choi")
    page.evaluate(AUTOPILOT)

    best_run = {"t": 0}
    t0 = time.time(); shots = set()
    while time.time() - t0 < 16 and not state(page)["ovs"]:
        page.wait_for_timeout(250)
        el = time.time() - t0
        for mark, name in [(4.2, "02-play.png"), (7.0, "03-play2.png"), (10.0, "04-play3.png")]:
            if el > mark and mark not in shots:
                shots.add(mark); st = state(page)
                print("   t=%.1fs %s" % (el, st)); shot(page, name)
                if mark == 7.0: print("   canvas:", canvas_stats(page))
        best_run["t"] = el
    auto = page.evaluate("() => window.__auto")
    st = state(page)
    print("   autopilot: %d frames, %d cu bat, thay gem %d frame, mat dau Byte %d frame"
          % (auto["frames"], auto["taps"], auto["gemSeen"], auto["lostByte"]))
    print("   song sot %.1fs | diem %s | thu duoc %s tt" % (best_run["t"], st["score"], st["mined"]))
    check(best_run["t"] > 4.0, "autopilot bay duoc > 4s (thuc te %.1fs) -> khe hep voi toi duoc" % best_run["t"])
    check(int(st["score"]) > 0 and int(st["dist"]) > 0, "diem + quang duong tang khi bay")
    # Diem = quang duong + 10/vien: kiem cong thuc bang so that
    check(int(st["score"]) == int(st["dist"]) + 10 * int(st["mined"]),
          "diem = quang duong + 10 x so vien (%s = %s + 10x%s)" % (st["score"], st["dist"], st["mined"]))
    gems_run = int(st["mined"])

    print("== 3. Tam dung ==")
    if not state(page)["ovs"]:
        page.click("#btn-pause"); page.wait_for_timeout(600)
        st = state(page); print("  ", st); shot(page, "05-pause.png")
        check("ov-pause" in st["ovs"], "overlay tam dung hien")
        check(st["pauseOff"], "icon nut doi sang ▶ khi dang dung")
        d1 = st["dist"]; page.wait_for_timeout(900)
        check(state(page)["dist"] == d1, "quang duong DUNG hoan toan khi pause")
        page.click("#resume-btn"); page.wait_for_timeout(400)
        check(not state(page)["ovs"] and not state(page)["pauseOff"], "Choi tiep: dong overlay + icon ve ⏸")

    print("== 4. Chet -> bang ket qua ==")
    page.evaluate("() => { window.__autoOn=false; }")     # tha phim cho roi
    page.wait_for_selector("#ov-over.show", timeout=20000)
    page.wait_for_timeout(1500)
    st = state(page)
    res = page.evaluate("""() => ({
      score:document.getElementById('r-score').textContent, dist:document.getElementById('r-dist').textContent,
      best:document.getElementById('r-best').textContent, mined:document.getElementById('r-mined').textContent,
      paid:document.getElementById('paid').textContent.trim(),
      stars:[...document.getElementById('stars').children].filter(s=>s.classList.contains('on')).length,
      againHtml:document.getElementById('again-btn').innerHTML.slice(0,80)
    })""")
    print("  ", st); print("   ket qua:", res); shot(page, "06-over.png")
    check(st["ovs"] == ["ov-over"], "chi overlay ket qua hien")
    check(int(st["bal"]) == 45 + int(res["mined"]),
          "onFinishGame cong dung: vi = 45 + %s = %s" % (res["mined"], st["bal"]))
    check(res["best"] == res["score"], "ky luc = diem lan dau choi")
    check("btn-fee" in res["againHtml"], "nut Choi lai co badge phi (img tt)")
    # Duong di cua vien tt (an vien -> +10 diem -> vi) do verify_gem.py kiem rieng
    # (no thu nhieu lan); o day bot chi bay 1 luot nen co the khong an duoc vien nao.
    print("   [ghi chu] luot nay thu duoc %s vien tt — xem verify_gem.py de kiem duong tt" % res["mined"])
    if int(res["mined"]) > 0:
        check("<b>%s</b>" % res["mined"] in page.evaluate("()=>document.getElementById('paid').innerHTML"),
              "dong 'da cong vao vi' in dung so vien")

    print("== 5. Nut am thanh + Pause tren bang ket qua ==")
    page.click("#btn-sfx"); page.wait_for_timeout(200)
    check(state(page)["sfxOff"], "van tat tieng duoc khi bang ket qua dang hien")
    page.click("#btn-sfx"); page.wait_for_timeout(200)
    check(not state(page)["sfxOff"], "bat lai duoc")
    check(page.evaluate("()=>document.getElementById('btn-pause').classList.contains('is-hidden')"),
          "nut Pause AN tren bang ket qua")

    print("== 6. Doi ngon ngu EN ==")
    page.click(".lang-switch button[data-lang='en']"); page.wait_for_timeout(600)
    en = page.evaluate("""() => ({
      title:document.title, tag:document.getElementById('gtag').textContent,
      k:[...document.querySelectorAll('.chip .k')].map(e=>e.textContent),
      rl:[...document.querySelectorAll('.res .rl')].map(e=>e.textContent),
      unit:[...document.querySelectorAll('#dist ~ small, .rv small')].map(e=>e.textContent),
      paid:document.getElementById('paid').textContent.trim(),
      hub:document.getElementById('hub-btn').textContent
    })""")
    print("  ", en); shot(page, "07-over-en.png")
    check("Asteroid Dodge" in en["title"] and "ASTEROID DODGE" in en["tag"].upper(), "tieu de + tag doi sang EN")
    check("Score" in en["k"] and "Distance" in en["k"], "nhan HUD doi sang EN")
    # ⚠️ Ten khu doi 08/08/2026: "Arcade Bay" -> "Training Simulator" (khop the MOD-02
    #    o dashboard va bang ten chinh thuc o CLAUDE.md muc 2). Phep kiem cu ghim
    #    nguyen van "Back to Arcade" nen no bao hong dung luc san pham lam dung —
    #    cung loai loi "phep kiem bao ve trang thai cu" da ghi nhieu lan trong du an.
    check(en["hub"] == "Back to Training Simulator", "nut hub doi sang EN")
    # dong thuong do JS sinh -> phai duoc dich lai khi doi ngon ngu giua bang ket qua
    check(not any(ch in en["paid"] for ch in "ạợđếươ") and en["paid"] != "",
          "dong 'da cong vao vi' cung doi sang EN: %r" % en["paid"])

    print("== 7. Ban tieng Viet lai + kiem overlay thieu tt ==")
    page.click(".lang-switch button[data-lang='vi']"); page.wait_for_timeout(300)
    page.evaluate("() => localStorage.setItem('astroq-asteroids','2')")
    page.reload(wait_until="load"); page.wait_for_timeout(800)
    page.click("#start-btn"); page.wait_for_timeout(500)
    st = state(page); print("  ", st); shot(page, "08-need.png")
    check("ov-need" in st["ovs"], "overlay 'chua du tt' hien")
    check(st["bal"] == "2", "KHONG tru tt khi khong du (bal=%s)" % st["bal"])

    print("== 8. Man hinh dien thoai 390x844 (letterbox) ==")
    m = ctx.new_page()
    m.set_viewport_size({"width": 390, "height": 844})
    m.goto(URL, wait_until="load"); m.wait_for_timeout(900)
    box = m.evaluate("""() => {
      const f=document.getElementById('field').getBoundingClientRect();
      const c=document.querySelector('.ov-card').getBoundingClientRect();
      const s=document.getElementById('stage').getBoundingClientRect();
      return { field:[Math.round(f.width),Math.round(f.height)], ratio:+(f.width/f.height).toFixed(3),
               cardBottom:Math.round(c.bottom), stageBottom:Math.round(s.bottom),
               bodyScrollW:document.body.scrollWidth, winW:innerWidth };
    }""")
    print("  ", box); shot(m, "09-mobile.png")
    check(abs(box["ratio"] - 1.6) < 0.02, "khung san giu ti le 8:5 tren dien thoai (%.3f)" % box["ratio"])
    check(box["bodyScrollW"] <= box["winW"] + 1, "khong tran ngang tren dien thoai")
    check(box["cardBottom"] <= box["stageBottom"] + 2, "the brief nam gon trong khung, khong bi cat")

    page.evaluate("() => localStorage.setItem('astroq-asteroids','50')")   # tra lai so du
    br.close()

print("\n=== LOI CONSOLE / JS: %d ===" % len(errors))
for e in errors: print("   !", e)
print("=== KET LUAN: %d dat, %d hong ===" % (0, len(fails)) if fails else "=== TAT CA KIEM TRA DAT ===")
for f in fails: print("   - " + f)
sys.exit(1 if (fails or errors) else 0)
