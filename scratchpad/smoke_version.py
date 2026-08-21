# -*- coding: utf-8 -*-
r"""Kiem huy hieu so hieu ban dung (`.ver-badge`) tren MOI trang nap ui-common.js.

⚠️ Phep kiem quan trong nhat o day la [3]: huy hieu KHONG DUOC AN MOT CU CHAM NAO.
   No neo co dinh o goc duoi-phai cua moi trang, ke ca 3 mini-game va man nhiem vu
   noi ca khung hinh la vung cham. Du an da tra gia dung loai loi nay hai lan:
   `#loader` cua explorer nuot moi cu bam trong 0,8 giay, va the `.me-card` bi bang
   day de khien nut "Da hieu!" — duong ra DUY NHAT — bam khong duoc.
   Do bang `elementFromPoint` chu khong doc CSS: co `pointer-events:none` trong file
   khong chung minh duoc nguoi dung cham xuyen qua duoc.

Chay: python scratchpad/smoke_version.py     (can `python -m http.server 8123`)
"""
import io
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
OK = FAIL = 0


def check(cond, label, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"  [OK]   {label} {extra}")
    else:
        FAIL += 1
        print(f"  [HONG] {label} {extra}")


def main():
    src = io.open("js/ui-common.js", encoding="utf-8").read()
    m = re.search(r'var VERSION = "(\d{4}\.\d{2}\.\d{2}\.\d+)";', src)
    if not m:
        print("*** khong doc duoc VERSION tu js/ui-common.js")
        sys.exit(1)
    ver = m.group(1)
    print(f"=== VERSION khai trong ui-common.js: {ver} ===")

    # Trang nao NAP ui-common.js thi phai co huy hieu — suy ra tu chinh markup,
    # khong gan cung danh sach (them trang moi la phep kiem tu dung).
    trang = sorted(f for f in __import__("os").listdir(".")
                   if f.endswith(".html") and "js/ui-common.js" in io.open(f, encoding="utf-8").read())
    print(f"    {len(trang)} trang nap ui-common.js\n")

    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("=== [1] MOI TRANG DEU CO HUY HIEU, DUNG SO ===")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:100]))
        pg.on("console", lambda mm: errs.append(mm.text[:100])
              if mm.type == "error" and "Failed to load resource" not in mm.text else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
        # ⚠️ CHAN `/billing/catalog` VA TRA PHAN HOI CO DINH — bo do nay quet CA 18
        #    trang, trong do `checkout.html`/`lab.html`/`pricing.html` goi route cong
        #    khai do ngay khi mo trang. Bo do chay o cong 8123, KHONG nam trong
        #    `ALLOWED_ORIGINS`, nen CORS chan va trinh duyet TU ghi mot dong do vao
        #    console — khong `catch` nao chan duoc → phep kiem "0 loi console" bao
        #    hong oan (do duoc: 1 phep kiem do lien tuc, ke ca tren ban HEAD).
        # ⚠️ CO Y KHONG them cong 8123 vao `ALLOWED_ORIGINS`: do la cau hinh SAN XUAT,
        #    mo them mot origin that chi de lam xanh mot phep kiem la doi thu khong
        #    thuoc san xuat. `audit_viewports.py` va `smoke_lang_switch.py` da chan
        #    theo dung loi nay tu 11/08/2026; bo do nay bi bo sot.
        # ⚠️ Mot phep kiem hay bao oan thi som muon nguoi ta bo qua no — do moi la
        #    cai gia that (luat 10 muc 6 CLAUDE.md).
        pg.route("**/billing/catalog*", lambda r: r.fulfill(
            status=200, content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body='{"ok":true,"saleOpen":false,"provider":"none","currency":"VND",'
                 '"trialDays":14,"graceDays":7,"offers":[]}'))
        # ⚠️ `crew.html` hoi `GET /crew` ngay khi mo trang — CUNG mot ly do.
        #    Bo do nay tu tim danh sach trang, nen `crew.html` (them 16/08/2026)
        #    di vao danh sach ma khong ai them route chan. Hong CHAP CHON vi no
        #    la mot cuoc dua: trang chuyen di truoc khi loi kip ghi thi khong co
        #    dong nao (do duoc: lan 1 sach 16/0, lan 2 hong 15/1).
        # ⚠️ REGEX NEO CUOI CHUOI, KHONG dung glob `**/crew*` — glob do khop CA
        #    `/crew.html`, tuc chan luon chinh TAI LIEU va tra JSON thay cho trang.
        pg.route(re.compile(r".*/crew(\?.*)?$"), lambda r: r.fulfill(
            status=200, content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body='{"cap":500,"taken":3,"seats":[{"no":1,"ch":"cho"},{"no":2,"ch":null},{"no":3,"ch":"m"}]}'))
        thieu, sai = [], []
        for t in trang:
            pg.goto(BASE + t, wait_until="domcontentloaded")
            pg.wait_for_timeout(500)
            r = pg.evaluate("""() => { const e=document.querySelector('.ver-badge');
                return e ? {txt:e.textContent, aria:e.getAttribute('aria-label')} : null; }""")
            if not r:
                thieu.append(t)
            elif r["txt"] != "v" + ver:
                sai.append(f"{t}:{r['txt']}")
        check(not thieu, f"ca {len(trang)} trang deu dung huy hieu", f"thieu: {thieu}")
        check(not sai, "so hieu tren man khop VERSION khai trong file", f"{sai}")

        print("\n=== [2] SONG NGU ===")
        pg.goto(BASE + "codex.html", wait_until="load")
        pg.wait_for_timeout(1200)
        vi = pg.eval_on_selector(".ver-badge", "e => e.getAttribute('aria-label')")
        check(vi and vi.startswith("Phiên bản"), "VI: aria-label 'Phiên bản …'", repr(vi))
        # Doi ngon ngu bang chinh nut cua trang — duong nguoi dung that di.
        pg.eval_on_selector_all(".lang-switch button", "e => e.find(x=>x.dataset.lang==='en').click()")
        pg.wait_for_timeout(600)
        en = pg.eval_on_selector(".ver-badge", "e => e.getAttribute('aria-label')")
        check(en and en.startswith("Version"), "EN: aria-label doi theo ngon ngu", repr(en))
        check(pg.eval_on_selector(".ver-badge", "e => e.textContent") == "v" + ver,
              "so hieu KHONG doi theo ngon ngu (no la so, khong phai chu)")

        print("\n=== [3] KHONG AN CU CHAM NAO (elementFromPoint) ===")
        # ⚠️ Do o 3 trang co ca khung hinh la vung cham.
        for t in ("game-dodge.html", "mission-earth.html", "explorer.html", "quiz.html"):
            pg.goto(BASE + t, wait_until="domcontentloaded")
            pg.wait_for_timeout(900)
            r = pg.evaluate("""() => {
                const b=document.querySelector('.ver-badge');
                if(!b) return {no:true};
                const r=b.getBoundingClientRect();
                const el=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2);
                return { xuyen: el !== b, la: el ? (el.id||el.className||el.tagName) : null,
                         pe: getComputedStyle(b).pointerEvents }; }""")
            check(r.get("no") or (r["xuyen"] and r["pe"] == "none"),
                  f"{t}: cham xuyen qua huy hieu", f"cham vao `{str(r.get('la'))[:34]}`")

        print("\n=== [4] KHONG CHONG `.env-badge`, KHONG TRAN NGANG ===")
        for w, h in ((1440, 900), (390, 844)):
            c2 = br.new_context(viewport={"width": w, "height": h})
            p2 = c2.new_page()
            p2.add_init_script("localStorage.setItem('astroq-lang','vi')")
            # ⚠️ PHAI DUNG `landing-app.html` — DO LA TRANG DUY NHAT NAP
            #    `js/firebase-auth-ui.js`, tuc trang duy nhat dung `.env-badge`.
            #    Ban dau toi do tren `dashboard.html?api=local` va no bao "khong chong
            #    0px²" — DAT RONG: khong co huy hieu nao de ma chong. Mot phep kiem
            #    do khoang cach giua HAI phan tu ma mot phan tu khong ton tai thi no
            #    luon xanh, va no se van xanh ca khi hai cai that su de len nhau.
            p2.goto(BASE + "landing-app.html?api=local", wait_until="domcontentloaded")
            p2.wait_for_timeout(2200)
            r = p2.evaluate("""() => {
                const v=document.querySelector('.ver-badge'), e=document.querySelector('.env-badge');
                const tran = document.documentElement.scrollWidth - window.innerWidth;
                if(!v) return {no:true, tran};
                const a=v.getBoundingClientRect();
                if(!e) return {tran, chong:0, co_env:false};
                const b=e.getBoundingClientRect();
                const ox=Math.max(0, Math.min(a.right,b.right)-Math.max(a.left,b.left));
                const oy=Math.max(0, Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top));
                return {tran, chong:ox*oy, co_env:true}; }""")
            # ⚠️ DOI HUY HIEU MOI TRUONG PHAI CO THAT roi moi do chong lan — khong
            #    thi phep kiem duoi day dat mot cach rong (xem ghi chu o tren).
            check(r.get("co_env") is True, f"{w}px: `.env-badge` co dung len that",
                  f"(neu False thi phep kiem chong lan la vo nghia)")
            check(r.get("chong", 0) == 0, f"{w}px: khong chong `.env-badge`",
                  f"chong {r.get('chong')}px²")
            check(r["tran"] <= 0, f"{w}px: khong tran ngang", f"{r['tran']}px")
            c2.close()

        check(not errs, "0 loi console tren moi trang", str(errs[:2]))
        br.close()

    print(f"\n===== {OK} dat / {FAIL} hong =====")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
