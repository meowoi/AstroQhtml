# -*- coding: utf-8 -*-
"""Mo CHINH astroq.org/game-classify.html tren Chromium — tang trinh duyet.

  py -3 scratchpad/verify_prod_0906_ui.py

Tang mang (verify_prod_0906.py) chi chung minh FILE co mat va noi dung dung.
No khong tra loi duoc: tre bam vao thi co choi duoc khong, va thien lech co
that su hien ra khong. Do la viec cua bo nay.

⚠️ Chot so hieu ban dung TRUOC (script kia da lam) — o day gia dinh da dung ban.
"""
import sys
from playwright.sync_api import sync_playwright

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

URL = "https://astroq.org/game-classify.html"
ok = bad = 0
def ck(name, cond, detail=""):
    global ok, bad
    if cond: ok += 1; print(f"  [OK]   {name}")
    else:    bad += 1; print(f"  [HONG] {name}   {detail}")

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script("""
      localStorage.setItem('astroq-lang','vi');
      localStorage.setItem('astroq-asteroids','99');
      localStorage.setItem('astroq-user', JSON.stringify({uid:'u-prod-check', name:'Bin'}));
    """)
    pg = ctx.new_page()
    errs, dead = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: dead.append(f"{r.status} {r.url}") if r.status >= 400 else None)

    print("[1] Mo trang tren ban that")
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(1200)
    ck("0 loi trang", not errs, str(errs[:2]))
    ck("0 asset hong", not dead, str(dead[:3]))

    # Bat dau luot — nut o man brief
    pg.click("#start-btn")
    pg.wait_for_selector("#teach-grid .cl-cell", timeout=20000)
    n = pg.eval_on_selector_all("#teach-grid .cl-cell", "e=>e.length")
    ck("man day hien ra, co o mau", n > 0, f"{n} o")

    print("\n[2] Nut nhan THU HAI nam trong tam nhin (loi bo cuc da sua)")
    fit = pg.evaluate("""()=>{
        const body = document.querySelector('.dg-body');
        const cell = document.querySelector('#teach-grid .cl-cell');
        const btns = cell.querySelectorAll('.cl-lb');
        const b = body.getBoundingClientRect(), c = cell.getBoundingClientRect();
        const last = btns[btns.length-1].getBoundingClientRect();
        return {cellH: Math.round(c.height), viewH: Math.round(b.height),
                nBtn: btns.length,
                fits: c.top >= b.top - 1 && last.bottom <= b.bottom + 1};
    }""")
    ck("thay TRON o mau dau tien (ca hai nut)", fit["fits"],
       f'o {fit["cellH"]}px / vung nhin {fit["viewH"]}px')
    ck("moi o co 2 nut nhan", fit["nBtn"] == 2, str(fit["nBtn"]))

    print("\n[3] Bo phan loai chay that + THIEN LECH xay ra")
    r = pg.evaluate("""()=>{
        const T = window.AstroQTeach;
        if (!T) return {err: 'khong co AstroQTeach'};
        // Day dung nhu vong 1: hai cum xa nhau
        const lab = [];
        ['curved_bright','dots'].forEach(g =>
          T.pool(g).forEach(s => lab.push({sample: s, label: s.truth})));
        const model = T.train(lab);
        // Vet cong NGAN phai bi xep nham thanh "nhieu" — do la bai hoc
        const short = T.pool('curved_short').map(s => ({
            id: s.id, truth: s.truth, got: T.predict(model, s).label}));
        // `bright` phai bi bo qua hoan toan
        const s = T.pool('curved_mid')[0];
        const a = T.predict(model, Object.assign({}, s, {bright: 0.02}));
        const b = T.predict(model, Object.assign({}, s, {bright: 0.99}));
        return {short, sameIgnoringBright: a.label === b.label
                                          && Math.abs(a.gap - b.gap) < 1e-9};
    }""")
    ck("doc duoc AstroQTeach tu ban that", "err" not in r, str(r.get("err")))
    if "err" not in r:
        ck("THIEN LECH: moi vet cong ngan bi xep nham la NHIEU",
           len(r["short"]) > 0 and all(x["got"] == "noise" and x["truth"] == "ast"
                                       for x in r["short"]),
           str([(x["id"], x["got"]) for x in r["short"]]))
        ck("doi do sang thi ket qua KHONG DOI (`bright` bi bo qua)",
           r["sameIgnoringBright"])

    print("\n[4] Nut Huan luyen NOI RA khi chua gan het (khong khoa im lang)")
    st = pg.eval_on_selector("#train", "e=>({dis: e.disabled})")
    ck("nut Huan luyen BAM DUOC", st["dis"] is False, str(st))
    pg.click("#train")
    pg.wait_for_timeout(600)
    toast = pg.eval_on_selector(".toast", "e=>e.innerText").strip() if \
        pg.query_selector(".toast") else ""
    ck("co loi nhac ke ra so anh con thieu", any(c.isdigit() for c in toast), repr(toast))

    print("\n[5] Dien thoai 390x844")
    ctx2 = br.new_context(viewport={"width": 390, "height": 844}, locale="vi-VN",
                          has_touch=True)
    ctx2.add_init_script("""
      localStorage.setItem('astroq-lang','vi');
      localStorage.setItem('astroq-asteroids','99');
      localStorage.setItem('astroq-user', JSON.stringify({uid:'u-prod-check', name:'Bin'}));
    """)
    p2 = ctx2.new_page()
    e2 = []
    p2.on("pageerror", lambda e: e2.append(str(e)))
    p2.goto(URL, wait_until="networkidle", timeout=60000)
    p2.wait_for_timeout(1000)
    ov = p2.evaluate("()=>({sw: document.documentElement.scrollWidth,"
                     "        cw: document.documentElement.clientWidth})")
    # ⚠️ Nguong +1 la nguong cua bo chuan audit_viewports — ca 4 game lop quyet
    #    dinh deu ra 391/390 (lam tron sub-pixel cua khung dung chung).
    ck("khong tran ngang o dien thoai", ov["sw"] - ov["cw"] <= 1, str(ov))
    ck("0 loi trang o dien thoai", not e2, str(e2[:2]))

    br.close()

print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
