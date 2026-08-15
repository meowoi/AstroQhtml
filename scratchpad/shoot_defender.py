# -*- coding: utf-8 -*-
"""Kiem game-defender.html (ARCADE-02) tren Chromium that:
   autopilot doc pixel canvas de ngam & ban, chup anh tung man,
   kiem giap / diem / vi tien / quiz vang / song ngu / dien thoai.
   Chay: python -m http.server 8123  (trong AstroQhtml/) roi python scratchpad/shoot_defender.py
"""
import io, os, re, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8123/game-defender.html"

# CANH BAO: PHI DOC TU CHINH FILE GAME, KHONG GHIM SO. Phi doi theo luat do kho
#    (15/08/2026); ghim con so o day thi bo do bao hong dung luc san pham lam dung.
COST = int(re.search(r"COST:\s*(\d+)", io.open(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game-defender.html"),
    encoding="utf-8").read()).group(1))

OUT = os.path.dirname(os.path.abspath(__file__))
errors, fails = [], []

def check(c, m):
    print(("   PASS  " if c else "   FAIL  ") + m)
    if not c: fails.append(m)

def shot(pg, name):
    pg.screenshot(path=os.path.join(OUT, name)); print("   anh ->", name)

def answer_quiz_if_open(pg):
    """Quiz mo ra la game DUNG han cho tra loi (dung y do). Trong luc test phai tu
       tra loi, khong thi vong lap doi game-over se treo mai."""
    if pg.evaluate("()=>document.getElementById('ov-quiz').classList.contains('show')"):
        pg.evaluate("()=>{const b=document.getElementById('q-opts').children[0]; if(b&&!b.disabled) b.click();}")
        pg.wait_for_timeout(1700)
        return True
    return False

# ---- Autopilot trong trang: tim vat the theo mau, ngam vao no roi giu ban ----
AUTOPILOT = r"""
() => {
  const cv=document.getElementById('cv'), g=cv.getContext('2d');
  const SX=()=>cv.width/800*(800/600), SY=()=>cv.height/600;   // san vuong 600x600
  const st={frames:0, aimed:0, kinds:{}, target:null};
  window.__auto=st;

  function scan(){
    const sx=cv.width/600, sy=cv.height/600;
    const d=g.getImageData(0,0,cv.width,cv.height).data, w=cv.width;
    const cx=cv.width/2, cy=cv.height/2;
    const blobs=[];
    for(let y=0;y<cv.height;y+=3) for(let x=0;x<w;x+=3){
      // bo qua vung quanh Tram: than tram, vong khien, dau nong deu lot vao bo mau
      const ddx=x-cx, ddy=y-cy;
      if(ddx*ddx+ddy*ddy < (75*sx)*(75*sx)) continue;
      const i=(y*w+x)*4, r=d[i], gg=d[i+1], b=d[i+2];
      let k=null;
      if(b>215 && r>140 && r<235 && gg<150 && b-gg>80) k='purple';
      else if(r>225 && gg>165 && gg<230 && b<135)      k='gold';
      else if(r>165 && gg<95 && b<95)                  k='junk';
      else if(r>60 && r<155 && Math.abs(r-gg)<28 && b>gg && gg>62) k='gray';
      if(!k) continue;
      let m=null;
      for(const bl of blobs) if(bl.k===k && Math.abs(bl.x-x)<32*sx && Math.abs(bl.y-y)<32*sy){ m=bl; break; }
      if(m){ m.x=(m.x*m.n+x)/(m.n+1); m.y=(m.y*m.n+y)/(m.n+1); m.n++; }
      else blobs.push({k:k, x:x, y:y, n:1});
    }
    // nguong so pixel: dan laser + hat no nho hon vat the that nen bi loc bo
    const MIN={purple:20, gold:20, junk:12, gray:20};
    return blobs.filter(b=>b.n>=MIN[b.k]).map(b=>({k:b.k, x:b.x/sx, y:b.y/sy,
      d:Math.hypot(b.x/sx-300, b.y/sy-300)}));
  }

  function aimAt(vx,vy){
    const r=cv.getBoundingClientRect();
    const cxp=r.left + vx/600*r.width, cyp=r.top + vy/600*r.height;
    cv.dispatchEvent(new MouseEvent('mousemove',{clientX:cxp, clientY:cyp, bubbles:true}));
    return {cxp:cxp, cyp:cyp};
  }
  function fire(vx,vy){
    const p=aimAt(vx,vy);
    cv.dispatchEvent(new MouseEvent('mousedown',{button:0, clientX:p.cxp, clientY:p.cyp, bubbles:true}));
  }

  let holdT=0;
  function tick(){
    st.frames++;
    const fs=scan();
    st.seen=fs.length;
    // uu tien: vang (mo quiz) > tim (an tien) > gan tam nhat (nguy hiem nhat)
    let tgt=null;
    if(window.__wantGold){ tgt=fs.find(f=>f.k==='gold') || null; }
    if(!tgt) tgt=fs.find(f=>f.k==='gold');
    if(!tgt) tgt=fs.find(f=>f.k==='purple');
    if(!tgt && fs.length) tgt=fs.reduce((a,b)=>a.d<b.d?a:b);
    if(tgt){
      st.target=tgt; st.aimed++;
      st.kinds[tgt.k]=(st.kinds[tgt.k]||0)+1;
      if(window.__hold===false) aimAt(tgt.x,tgt.y); else fire(tgt.x,tgt.y);
    }
    if(window.__autoOn) requestAnimationFrame(tick);
  }
  window.__autoOn=true; window.__hold=true; requestAnimationFrame(tick);
  return true;
}
"""

def state(pg):
    return pg.evaluate("""() => ({
      score:+document.getElementById('score').textContent,
      mined:+document.getElementById('mined').textContent,
      hull:document.getElementById('hull-pct').textContent,
      hullW:document.getElementById('hull-fill').style.width,
      barCls:document.getElementById('hullbar').className,
      bal:+document.getElementById('bal').textContent,
      ovs:[...document.querySelectorAll('.ov')].filter(o=>o.classList.contains('show')).map(o=>o.id),
      pauseHidden:document.getElementById('btn-pause').classList.contains('is-hidden'),
      sfxOff:document.getElementById('btn-sfx').classList.contains('off'),
      gun:(document.getElementById('gunlvl')||{}).textContent,
      empW:(document.getElementById('emp-fill')||{style:{}}).style.width,
      empReady:document.getElementById('btn-emp').classList.contains('ready'),
      empOff:document.getElementById('btn-emp').disabled,
      empHidden:document.getElementById('btn-emp').classList.contains('is-hidden'),
      foes:(window.__dbg&&window.__dbg.foes)||-1
    })""")

with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1280, "height": 860})
    page = ctx.new_page()
    page.on("console", lambda m: errors.append("console.%s: %s" % (m.type, m.text)) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: %s" % e))

    print("== 1. Man brief (mac dinh tieng Viet) ==")
    page.goto(URL, wait_until="load")
    page.evaluate("()=>{localStorage.setItem('astroq-lang','vi');localStorage.setItem('astroq-asteroids','120')}")
    page.reload(wait_until="load"); page.wait_for_timeout(1200)
    vi = page.evaluate("""()=>({title:document.title, tag:document.getElementById('gtag').textContent,
        hull:document.querySelector('.hullwrap .k').textContent,
        how:[...document.querySelectorAll('.how span')].length})""")
    print("  ", vi, state(page))
    # ⚠️ Ten game co ban TIENG VIET tu 08/08/2026 (chu du an: "Space defender doi
    #    thanh tieng Viet khi sang che do tieng Viet"). Phep kiem cu ghim nguyen van
    #    "Space Defender" nen no bao hong dung luc san pham lam dung.
    check("Phòng Thủ Không Gian" in vi["title"], "tieu de tieng Viet dung")
    check(vi["hull"] == "Giáp trạm", "nhan thanh giap tieng Viet")
    # 6 -> 8 dong: them Xung kich EMP + Nang cap phao (08/08/2026)
    check(vi["how"] == 8, "co 8 dong huong dan (%s)" % vi["how"])
    check(state(page)["ovs"] == ["ov-start"], "chi overlay brief hien")
    check(state(page)["hull"] == "100%", "giap bat dau 100%")
    check(state(page)["pauseHidden"], "nut Pause an o man brief")
    page.click("#btn-sfx"); page.wait_for_timeout(150)
    check(state(page)["sfxOff"], "tat tieng duoc khi overlay brief hien")
    page.click("#btn-sfx"); page.wait_for_timeout(150)
    shot(page, "d01-brief.png")

    print("== 2. Bat dau: tru phi + Pause hien ==")
    page.click("#start-btn"); page.wait_for_timeout(200)
    s = state(page)
    check(s["bal"] == 120 - COST, "tru dung %d tt mot lan (bal=%s)" % (COST, s["bal"]))
    check(not s["pauseHidden"], "nut Pause hien khi dang choi")

    print("== 3. KHONG ban -> vat the dam vao Tram, giap phai TUT ==")
    page.wait_for_timeout(7000)
    s = state(page)
    print("   giap sau 7s khong ban:", s["hull"], "| class:", s["barCls"])
    hull_no_fire = int(s["hull"].rstrip("%"))
    check(hull_no_fire < 100, "giap giam khi de vat the dam vao Tram (%d%%)" % hull_no_fire)
    shot(page, "d02-hit.png")

    print("== 4. Bat autopilot: ngam & ban 360 ==")
    page.evaluate(AUTOPILOT)
    t0 = time.time(); quiz_seen = False; quiz_info = None; shots = set()
    while time.time() - t0 < 60:
        page.wait_for_timeout(220)
        s = state(page)
        el = time.time() - t0
        if "ov-quiz" in s["ovs"] and not quiz_seen:
            quiz_seen = True
            page.evaluate("()=>{window.__hold=false}")     # ngung ban khi dang doi quiz
            q = page.evaluate("""()=>({
              text:document.getElementById('q-text').textContent,
              opts:[...document.getElementById('q-opts').children].map(b=>b.textContent),
              reward:document.getElementById('q-reward').textContent.trim(),
              hull:document.getElementById('hull-pct').textContent,
              score:+document.getElementById('score').textContent,
              mined:+document.getElementById('mined').textContent})""")
            print("   QUIZ mo ra:", q["text"], "|", len(q["opts"]), "dap an | giap", q["hull"])
            shot(page, "d03-quiz.png")
            check(len(q["opts"]) == 4, "quiz co 4 dap an")
            check(q["text"] != "…" and len(q["text"]) > 8, "quiz co noi dung cau hoi")
            # game phai DUNG lai khi quiz mo
            page.wait_for_timeout(1500)
            s2 = state(page)
            check(s2["score"] == q["score"], "diem DUNG lai khi quiz dang mo (%s vs %s)" % (s2["score"], q["score"]))
            # tra loi DUNG: tim dap an dung bang cach bam lan luot? -> doc dap an dung tu QUIZ khong duoc
            # (bien private). Bam dap an dau roi doc ket qua thuc te.
            hull_before = int(q["hull"].rstrip("%")); mined_before = q["mined"]
            page.evaluate("()=>document.getElementById('q-opts').children[0].click()")
            page.wait_for_timeout(1600)
            s3 = state(page)
            hull_after = int(s3["hull"].rstrip("%"))
            correct = s3["mined"] == mined_before + 5
            quiz_info = {"correct": correct, "hull_before": hull_before, "hull_after": hull_after,
                         "mined_before": mined_before, "mined_after": s3["mined"]}
            print("   sau khi tra loi:", quiz_info)
            if correct:
                check(hull_after >= min(100, hull_before + 20), "tra loi DUNG: giap +20%% (%d -> %d)" % (hull_before, hull_after))
                check(s3["mined"] == mined_before + 5, "tra loi DUNG: +5 tt vao vi tam")
            else:
                check(s3["mined"] == mined_before, "tra loi SAI: khong duoc thuong tt")
                check(hull_after <= hull_before, "tra loi SAI: khong hoi giap")
            check("ov-quiz" not in state(page)["ovs"], "quiz dong lai sau khi tra loi")
            check(state(page)["ovs"] == [], "game chay tiep sau quiz")
            page.evaluate("()=>{window.__hold=true}")
        if el > 6 and 6 not in shots and not s["ovs"]:
            shots.add(6); print("   t=%.0fs %s" % (el, s)); shot(page, "d04-play.png")
        if quiz_seen and "ov-quiz" in s["ovs"]:
            answer_quiz_if_open(page)      # quiz thu 2 tro di: tra loi cho qua
        if "ov-over" in s["ovs"]: break
        if quiz_seen and s["score"] > 250: break   # da du du lieu, sang phan pause
    auto = page.evaluate("()=>window.__auto")
    s = state(page)
    print("   autopilot: %d frames, ngam %d lan, loai da ngam: %s" % (auto["frames"], auto["aimed"], auto["kinds"]))
    print("   trang thai:", s)
    check(auto["aimed"] > 50, "autopilot nhan dien duoc vat the (%d lan ngam)" % auto["aimed"])
    check(s["score"] > 0, "ban ha duoc vat the -> co diem (%s)" % s["score"])
    check(quiz_seen, "gap va kiem duoc thien thach VANG (quiz)")
    check(s["mined"] > 0, "thu duoc Thien thach tim trong luot (%s)" % s["mined"])

    print("== 4b. XUNG KICH EMP + NANG CAP PHAO (them 08/08/2026) ==")
    # ⚠️ Lai bang `window.__dbg` chu khong ngoi ban ha 14 vat the bang autopilot: cai
    #    can do la *no roi thi san co sach khong*, khong phai *co ban trung khong*
    #    (phan do da co o muc 4). Bam nut thi VAN BAM THAT nhu tre.
    page.evaluate("()=>{window.__autoOn=false}")
    answer_quiz_if_open(page)
    if not state(page)["ovs"]:
        s = state(page)
        check(not s["empHidden"], "nut EMP hien khi dang choi")
        # --- chua nap day thi nut phai VO HIEU (mot nut bam khong an la nut noi doi) ---
        page.evaluate("()=>{window.__dbg.setScore(0)}")
        emp0 = page.evaluate("()=>window.__dbg.emp")
        if emp0 < 14:
            check(state(page)["empOff"], "chua nap day -> nut EMP vo hieu")
            check(not state(page)["empReady"], "chua nap day -> khong sang 'ready'")
        # --- nap day + gieo vat the roi BAM NUT ---
        page.evaluate("()=>{window.__dbg.chargeEmp(); window.__dbg.spawn(9)}")
        page.wait_for_timeout(120)
        s = state(page)
        check(s["empW"] == "100%", "thanh nap EMP day 100%% (%s)" % s["empW"])
        check(s["empReady"] and not s["empOff"], "nap day -> nut EMP sang va bam duoc")
        # ⚠️ HOI BANG SO HIEU, KHONG HOI BANG SO LUONG. Bo sinh van chay trong 0,5 giay
        #    song lan, nen luon co vat the MOI — ban dau toi doi `foes == 0` va phep
        #    kiem bao hong (11 -> 1) trong khi cu no da lam dung viec cua no. Cai can
        #    do la "moi vat the DANG O TRONG SAN luc no deu bien mat".
        before = page.evaluate("()=>window.__dbg.serials")
        check(len(before) >= 6, "co %d vat the trong san truoc khi no" % len(before))
        shot(page, "d04b-emp-ready.png")
        page.click("#btn-emp")
        # ⚠️ Doc `emp` NGAY sau cu bam, khong doc sau 900ms: dan ban truoc do van con
        #    bay va co the ha mot vat the MOI -> nap them 1, va phep kiem "EMP khong tu
        #    nap lai" bao hong oan (loi cua phep do, khong phai cua game).
        check(page.evaluate("()=>window.__dbg.emp") == 0, "cu no TIEU HET thanh nap")
        page.wait_for_timeout(90)
        check(page.evaluate("()=>window.__dbg.wave") > 0, "vong song EMP dang lan ra")
        shot(page, "d04c-emp-wave.png")
        page.wait_for_timeout(900)          # song lan 900px/s, phu het san trong ~0,5s
        after = page.evaluate("()=>window.__dbg.serials")
        left = [n for n in before if n in after]
        print("   vat the luc no: %d | con sot: %s | wave=%s"
              % (len(before), left, page.evaluate("()=>window.__dbg.wave")))
        check(not left, "EMP no SACH moi vat the dang o trong san (sot %s)" % left)
        check(page.evaluate("()=>window.__dbg.wave") < 0, "vong song tat khi lan het san")
        # --- nang cap phao theo diem ---
        page.evaluate("()=>{window.__dbg.setScore(0)}")
        page.wait_for_timeout(120)
        check(state(page)["gun"] == "Pháo 1", "diem 0 -> Phao 1 (%r)" % state(page)["gun"])
        page.evaluate("()=>{window.__dbg.setScore(160)}")
        page.wait_for_timeout(260)
        s = state(page)
        check(s["gun"] == "Pháo 2", "160 diem -> Phao 2 (%r)" % s["gun"])
        check(page.evaluate("()=>window.__dbg.gun") == 1, "cap phao trong ma = 1")
        page.evaluate("()=>{window.__dbg.setScore(420)}")
        page.wait_for_timeout(260)
        s = state(page)
        check(s["gun"] == "Pháo 3", "420 diem -> Phao 3 (%r)" % s["gun"])
        toast_txt = page.evaluate("()=>document.getElementById('toast').textContent")
        check("PHÁO CẤP 3" in toast_txt, "co loi bao len cap phao (%r)" % toast_txt)
        shot(page, "d04d-gun3.png")
        page.evaluate("()=>{window.__dbg.setScore(0)}")
        page.evaluate(AUTOPILOT)

    print("== 5. Tam dung ==")
    answer_quiz_if_open(page)
    if not state(page)["ovs"]:
        page.evaluate("()=>{window.__autoOn=false}")
        page.click("#btn-pause"); page.wait_for_timeout(500)
        s = state(page); sc = s["score"]
        check("ov-pause" in s["ovs"], "overlay tam dung hien")
        check(not s["pauseHidden"], "nut Pause con hien khi dang dung")
        page.wait_for_timeout(1200)
        check(state(page)["score"] == sc, "diem DUNG hoan toan khi pause")
        shot(page, "d05-pause.png")
        page.click("#resume-btn"); page.wait_for_timeout(300)
        check(state(page)["ovs"] == [], "Choi tiep: dong overlay")
        page.evaluate(AUTOPILOT)

    print("== 6. De thua -> bang ket qua + cong vi ==")
    page.evaluate("()=>{window.__autoOn=false}")   # ngung ban, de vat the pha Tram
    answer_quiz_if_open(page)
    bal_before = state(page)["bal"]; mined_before = state(page)["mined"]
    t1 = time.time(); live_mined = mined_before
    while time.time() - t1 < 120:
        page.wait_for_timeout(300)
        if answer_quiz_if_open(page): continue
        s0 = state(page)
        # quiz tra loi dung trong luc doi se cong them 5 tt -> phai lay so LIVE lam moc,
        # khong thi so sanh voi moc cu roi bao sai
        if not s0["ovs"]: live_mined = s0["mined"]
        if "ov-over" in s0["ovs"]: break
    check("ov-over" in state(page)["ovs"], "thua khi giap ve 0 -> hien bang ket qua")
    page.wait_for_timeout(1200)
    s = state(page)
    res = page.evaluate("""()=>({score:+document.getElementById('r-score').textContent,
      time:+document.getElementById('r-time').textContent, best:+document.getElementById('r-best').textContent,
      mined:+document.getElementById('r-mined').textContent,
      paid:document.getElementById('paid').textContent.trim(),
      paidHtml:document.getElementById('paid').innerHTML,
      none:document.getElementById('paid').classList.contains('none')})""")
    print("   ket qua:", res); print("   hull:", s["hull"], "| bal:", s["bal"])
    shot(page, "d06-over.png")
    check(s["ovs"] == ["ov-over"], "chi overlay ket qua hien")
    check(s["hull"] == "0%", "giap ve 0% khi thua")
    check(s["pauseHidden"], "nut Pause an tren bang ket qua")
    check(res["mined"] == live_mined,
          "so tt o bang ket qua = so tren HUD luc chet (%s = %s)" % (res["mined"], live_mined))
    check(s["bal"] == bal_before + res["mined"],
          "onFinishGame cong dung: %s + %s = %s" % (bal_before, res["mined"], s["bal"]))
    check(res["best"] == res["score"], "ky luc = diem lan dau")
    check(res["time"] > 0, "co ghi so giay tru duoc (%s)" % res["time"])
    if res["mined"] > 0:
        check(("<b>%d</b>" % res["mined"]) in res["paidHtml"] and not res["none"],
              "dong 'da cong vao vi' in dung so vien")

    print("== 7. Doi ngon ngu EN ==")
    page.click(".lang-switch button[data-lang='en']"); page.wait_for_timeout(500)
    en = page.evaluate("""()=>({title:document.title, hull:document.querySelector('.hullwrap .k').textContent,
      rl:[...document.querySelectorAll('.res .rl')].map(e=>e.textContent),
      paid:document.getElementById('paid').textContent.trim(),
      gun:(document.getElementById('gunlvl')||{}).textContent,
      hub:document.getElementById('hub-btn').textContent})""")
    print("  ", en); shot(page, "d07-over-en.png")
    check(en["hull"] == "Hull", "nhan giap doi sang EN")
    check("Collected" in en["rl"] and "Held for" in en["rl"], "nhan bang ket qua doi sang EN")
    check(not any(ch in en["paid"] for ch in "ạợđếươ"), "dong thuong doi sang EN: %r" % en["paid"])
    # ⚠️ Ten khu doi 08/08/2026: "Arcade Bay" -> "Training Simulator".
    check(en["hub"] == "Back to Training Simulator", "nut hub doi sang EN")
    # Ten game o EN VAN la "Space Defender" — doi ten chi ap cho ban tieng Viet
    check("Space Defender" in en["title"], "ban EN giu ten Space Defender")
    check(en["gun"] == "Gun 1", "chip cap phao doi sang EN (%r)" % en["gun"])

    print("== 8. Thieu tt ==")
    page.click(".lang-switch button[data-lang='vi']"); page.wait_for_timeout(200)
    page.evaluate("()=>localStorage.setItem('astroq-asteroids','3')")
    page.reload(wait_until="load"); page.wait_for_timeout(800)
    page.click("#start-btn"); page.wait_for_timeout(400)
    s = state(page)
    check("ov-need" in s["ovs"] and "ov-start" not in s["ovs"], "chi overlay 'thieu tt' hien")
    check(s["bal"] == 3, "KHONG tru tt khi khong du")
    shot(page, "d08-need.png")

    print("== 9. Dien thoai 390x844 ==")
    m = ctx.new_page(); m.set_viewport_size({"width": 390, "height": 844})
    m.goto(URL, wait_until="load"); m.wait_for_timeout(900)
    box = m.evaluate("""()=>{const f=document.getElementById('field').getBoundingClientRect();
      const c=document.querySelector('.ov-card').getBoundingClientRect();
      const s=document.getElementById('stage').getBoundingClientRect();
      const h=document.getElementById('hud').getBoundingClientRect();
      return {field:[Math.round(f.width),Math.round(f.height)], ratio:+(f.width/f.height).toFixed(3),
              hudBottom:Math.round(h.bottom), fieldTop:Math.round(f.top),
              cardBottom:Math.round(c.bottom), stageBottom:Math.round(s.bottom),
              scrollW:document.body.scrollWidth, winW:innerWidth};}""")
    print("  ", box); shot(m, "d09-mobile.png")
    check(abs(box["ratio"] - 1.0) < 0.02, "san giu VUONG tren dien thoai (%.3f)" % box["ratio"])
    check(box["scrollW"] <= box["winW"] + 1, "khong tran ngang")
    check(box["cardBottom"] <= box["stageBottom"] + 2, "the brief khong bi cat")
    check(box["hudBottom"] <= box["fieldTop"] + 1, "thanh HUD nam TREN san, khong de len")

    page.evaluate("()=>localStorage.setItem('astroq-asteroids','50')")
    br.close()

print("\n=== LOI CONSOLE / JS: %d ===" % len(errors))
for e in errors: print("   !", e)
print("=== %s ===" % ("TAT CA KIEM TRA DAT" if not fails and not errors else "%d HONG" % (len(fails) + len(errors))))
for f in fails: print("   -", f)
sys.exit(1 if (fails or errors) else 0)
