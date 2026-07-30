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
        check(f"[{label}] 10 the 'chua giai ma' + 5 the 'sap co'", nlock==10 and nsoon==5, f"lock={nlock} soon={nsoon}")
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
    check("so tay dang cho 20 khoa bank", r["keys"]==20, f"{r['keys']}")
    check("moi khoa bank tra ra dung mot the trong so tay", not r["unmapped"], f"{r['unmapped']}")
    check("tra loi dung ca luot -> giai ma duoc the that",
          r["opened"]>0, f"mo {r['opened']} the: {r['sample']}")
    check("[day noi] 0 loi console", not errs, str(errs[:2]))
    ctx.close(); b.close()
print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
