# -*- coding: utf-8 -*-
"""Soi codex.html tren Chromium that: khong loi console, luoi ve duoc, 3 trang thai."""
import io, sys
from playwright.sync_api import sync_playwright
ok=bad=0
def check(l,c,d=""):
    global ok,bad
    if c: ok+=1; print(f"  [OK]   {l}"+(f"  ({d})" if d else ""))
    else: bad+=1; print(f"  [HONG] {l}"+(f"  ({d})" if d else ""))
URL="http://127.0.0.1:8123/codex.html"
with sync_playwright() as p:
    b=p.chromium.launch()
    for label,vp in (("desktop",{"width":1440,"height":900}),("mobile",{"width":390,"height":844})):
        ctx=b.new_context(viewport=vp)
        pg=ctx.new_page()
        errs=[]
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        # ghim ngon ngu VI (navigator.language cua Chromium la en-US -> se chay ban EN)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(3600)
        n=pg.eval_on_selector_all(".cx-item","els=>els.length")
        check(f"[{label}] luoi ve du 15 the", n==15, f"{n}")
        nlock=pg.eval_on_selector_all(".cx-item.lock","e=>e.length")
        nsoon=pg.eval_on_selector_all(".cx-item.soon","e=>e.length")
        # ⚠️ SUY RA, KHONG GAN CUNG "10 lock + 5 soon". Tu 30/07/2026 ca 15 thuat ngu
        #    deu co cau hoi nen KHONG con the nao 'soon'. Gan cung con so cu la phep
        #    kiem khang dinh dung trang thai HONG (5 the khoa vinh vien) — dung loai
        #    loi da giu nut Mat Trang song o smoke_mission_earth.py.
        check(f"[{label}] chua dang nhap: moi the o trang thai chua giai ma",
              nlock + nsoon == n, f"lock={nlock} soon={nsoon} / {n} the")
        check(f"[{label}] KHONG con the 'sap co' (moi thuat ngu da co cau hoi)",
              nsoon == 0, f"soon={nsoon}")
        # chua dang nhap -> phai co dai nhac, va KHONG the nao co the 'done'
        ndone=pg.eval_on_selector_all(".cx-item.done","e=>e.length")
        check(f"[{label}] chua dang nhap: 0 the da giai ma (khong bia)", ndone==0, f"{ndone}")
        vis=pg.eval_on_selector("#banner","e=>!e.hidden")
        check(f"[{label}] co dai nhac noi ro ly do", vis)
        # bam mot the -> modal mo, va the CHUA giai ma van bam duoc
        pg.click(".cx-item")
        pg.wait_for_timeout(400)
        check(f"[{label}] the chua giai ma VAN bam duoc, modal mo", pg.eval_on_selector("#modal","e=>!e.hidden"))
        check(f"[{label}] modal an phan noi dung khi chua giai ma", pg.eval_on_selector("#m-body","e=>e.hidden"))
        check(f"[{label}] modal noi cach mo khoa", pg.eval_on_selector("#m-locked","e=>!e.hidden"))
        # Escape dong duoc
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        check(f"[{label}] Escape dong modal", pg.eval_on_selector("#modal","e=>e.hidden"))
        # thanh tien do phai CAO THAT (bai hoc span inline height:0)
        h=pg.eval_on_selector("#prog","e=>e.getBoundingClientRect().height")
        check(f"[{label}] thanh tien do cao that (khong bi 0px)", h>=6, f"{h:.1f}px")
        # khong tran ngang
        sw=pg.evaluate("document.documentElement.scrollWidth"); cw=pg.evaluate("document.documentElement.clientWidth")
        check(f"[{label}] khong tran ngang", sw<=cw+1, f"{sw} vs {cw}")
        # loc "Da giai ma" -> 0 the + hien dong 'khong co'
        pg.click('#seg-status button[data-v="done"]'); pg.wait_for_timeout(300)
        check(f"[{label}] loc 'Da giai ma' -> 0 the, hien dong giai thich",
              pg.eval_on_selector_all(".cx-item","e=>e.length")==0 and pg.eval_on_selector("#none","e=>!e.hidden"))
        check(f"[{label}] 0 loi console", not errs, str(errs[:2]))
        ctx.close()
    # ban EN
    ctx=b.new_context(viewport={"width":1440,"height":900}); pg=ctx.new_page()
    errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("localStorage.setItem('astroq-lang','en')")
    pg.goto(URL, wait_until="load"); pg.wait_for_timeout(3600)
    txt=pg.inner_text("body")
    check("[en] dich CA chu trong markup (h1) va chu do JS sinh (badge)",
          pg.inner_text("h1")=="Terminology Codex" and "Not decoded" in txt,
          "h1="+pg.inner_text("h1"))
    check("[en] 0 loi console", not errs, str(errs[:2]))
    ctx.close()

    # ─── DAY NOI: khoa cua ngan hang cau hoi -> the trong so tay ───
    # quiz.html day `it.term` cua tung cau tra loi DUNG len server; day la phep do
    # chung minh moi khoa do co the tra ra MOT the trong so tay. Doc trong trinh
    # duyet that vi ca hai ben deu la JS — doc chuoi trong file khong chung minh duoc.
    ctx=b.new_context(viewport={"width":1440,"height":900}); pg=ctx.new_page()
    errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL, wait_until="load")
    pg.add_script_tag(url="/js/quiz-questions.js")
    pg.wait_for_timeout(400)
    r=pg.evaluate("""(() => {
        const bank = AstroQQuestions.all ? AstroQQuestions.all() : null;
        const round = AstroQQuestions.pickRound(5);
        const noTerm = round.filter(q => !q.term).length;
        // moi khoa cua 20 cau thien van phai tra ra mot the trong so tay
        const keys = AstroQCodex.quizTerms();
        const unmapped = keys.filter(k => !AstroQCodex.idOfQuizTerm(k));
        // mo phong: tra loi dung ca luot -> nhung khoa nao duoc giai ma
        const decoded = new Set(round.map(q => q.term));
        const opened = AstroQCodex.all().filter(t => AstroQCodex.isDecoded(t, decoded));
        return { round: round.length, noTerm, keys: keys.length,
                 unmapped, opened: opened.length, sample: opened.map(t => t.id).slice(0,3) };
    })()""")
    check("moi cau trong mot luot quiz deu co khoa `term`", r["noTerm"]==0, f"{r['noTerm']} cau thieu")
    # ⚠️ SUY RA tu so thuat ngu (2 khoa/thuat ngu), khong gan cung 20.
    check("so tay cho dung 2 khoa bank cho moi thuat ngu",
          r["keys"] == 15 * 2, f"{r['keys']} khoa / 15 thuat ngu")
    check("moi khoa bank tra ra dung mot the trong so tay", not r["unmapped"], f"{r['unmapped']}")
    check("tra loi dung ca luot -> giai ma duoc the that",
          r["opened"]>0, f"mo {r['opened']} the: {r['sample']}")
    check("[day noi] 0 loi console", not errs, str(errs[:2]))

    # ─── 5 thuat ngu them 30/07/2026 phai giai ma duoc THAT ───
    # Truoc do chung o trang thai "sap co" (bank khong co cau nao ve chung), tuc la
    # 5/15 the khoa vinh vien. Day la phep do chung minh chuyen do da het.
    r2 = pg.evaluate("""(() => {
        const NEW = ['term_black_hole','term_gravity','term_nebula',
                     'term_supernova','term_cmb'];
        const bankTerms = new Set(AstroQQuestions.ALL.map(q => q.term));
        const dangling = [];
        NEW.forEach(id => { const t = AstroQCodex.get(id);
          t.q.forEach(k => { if (!bankTerms.has(k)) dangling.push(id + ' -> ' + k); }); });
        const done = new Set(NEW.flatMap(id => AstroQCodex.get(id).q));
        const opened = NEW.filter(id => AstroQCodex.isDecoded(AstroQCodex.get(id), done));
        const noPath = AstroQCodex.all().filter(t => !AstroQCodex.hasPath(t)).map(t => t.id);
        // Dung MOT khoa thi chi mo DUNG the cua no, khong "ro" sang the khac
        const one = new Set(['black-hole']);
        const bleed = AstroQCodex.all()
          .filter(t => AstroQCodex.isDecoded(t, one)).map(t => t.id);
        return { dangling, opened, noPath, bleed };
    })()""")
    check("moi khoa `q` cua 5 the moi tro vao cau CO THAT trong bank",
          not r2["dangling"], str(r2["dangling"]))
    check("tra loi dung -> CA 5 the moi giai ma duoc", len(r2["opened"]) == 5,
          f"{len(r2['opened'])}/5")
    check("KHONG con the nao o trang thai 'sap co'", not r2["noPath"], str(r2["noPath"]))
    check("dung MOT khoa chi mo DUNG the cua no (khong ro sang the khac)",
          r2["bleed"] == ["term_black_hole"], str(r2["bleed"]))
    ctx.close(); b.close()
print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
