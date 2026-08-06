# -*- coding: utf-8 -*-
"""Chup anh ban mau cay nhiem vu o 3 tinh huong x 2 co man, va do vai thu de bat loi bo cuc.
Chay: python -m http.server 8123 (trong AstroQhtml/) roi python scratchpad/shot_proto_tree.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8123/scratchpad/proto-mission-tree.html"
OK = FAIL = 0


def check(cond, label, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"    [OK]   {label} {extra}")
    else:
        FAIL += 1
        print(f"    [HONG] {label} {extra}")


def run(pw):
    br = pw.chromium.launch()
    for vp, tag in [({"width": 1440, "height": 960}, "desktop"),
                    ({"width": 390, "height": 844}, "mobile")]:
        ctx = br.new_context(viewport=vp, device_scale_factor=2)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(URL, wait_until="networkidle")

        for case in ["0", "5", "7"]:
            pg.click(f'#seg button[data-case="{case}"]')
            pg.wait_for_timeout(320)
            print(f"\n  --- {tag} / da xong {case} chang ---")

            d = int(case)
            want_now = 1 if d < 7 else 0
            folded = d >= 2
            check(pg.locator(".node.now").count() == want_now,
                  "so chang lam duoc ngay", str(want_now))
            check(pg.locator(".node.lock").count() == 7 - d - want_now,
                  "so chang chua mo", str(pg.locator(".node.lock").count()))
            # ⚠️ Da xong >= 2 thi GAP lai thanh mot dai; duoi 2 thi hien nguyen hang.
            check(pg.locator(".fold").count() == (1 if folded else 0),
                  "gap phan da xong dung luc", str(folded))
            check(pg.locator(".node.done").count() == (0 if folded else d),
                  "hang 'da xong' an khi dang gap")

            # ⚠️ MAT TRANG KHONG DUOC NAM TRONG CAY CUA TRAI DAT — sai tang.
            check("Mặt Trăng" not in pg.locator("#tree").inner_text(),
                  "khong co Mat Trang trong cay cua Trai Dat")

            # The ket chi hien khi xong het, va no tro NGUOC VE BAN DO
            check(pg.locator("#finish").is_visible() == (d == 7),
                  "the ket hien dung luc", str(d == 7))
            if d == 7:
                href = pg.eval_on_selector("#finish .pbtn", "e => e.getAttribute('href')")
                check("proto-planet.html" in href, "the ket tro ve danh sach nhiem vu", href)

            # ⚠️ CHIEU CAO CAY — day la thu chu du an bao "dai ngoang".
            h = pg.evaluate("() => document.getElementById('tree').getBoundingClientRect().height")
            check(h < 620, "cay khong dai ngoang", f"({round(h)}px)")

            # Khong tran ngang
            ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(ow <= 0, "khong tran ngang", f"(du {ow}px)")

            # Vung cham >= 48px.
            # ⚠️ CHI do component CUA BAN MAU. `.seg` la nut loc DUNG CHUNG cua
            #    page-shell.css: du an co y de 32px tren chuot va chi nang len 48px
            #    trong `@media (pointer:coarse)` — do o day la bao hong oan.
            small = pg.evaluate("""() => {
              const bad = [];
              document.querySelectorAll('.node-btn, .pbtn, .sh-x').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width && (r.width < 48 || r.height < 48))
                  bad.push(el.className + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
              });
              return bad;
            }""")
            check(not small, "moi vung cham >= 48px", str(small[:3]))

            # Nhan khong bi cat duoi
            clipped = pg.evaluate("""() => {
              const bad = [];
              document.querySelectorAll('.node-lb b').forEach(el => {
                if (el.scrollHeight > el.clientHeight + 2) bad.push(el.textContent.trim());
              });
              return bad;
            }""")
            check(not clipped, "ten chang khong bi cat", str(clipped[:2]))

            # ⚠️ BAN 2: cay chi duoc co TEN (+ 1 dong phu khi that su can noi).
            #    Do bang so PHAN TU chu, khong do bang mat.
            lines = pg.evaluate("""() => {
              const bad = [];
              document.querySelectorAll('.node').forEach(n => {
                const lb = n.querySelector('.node-lb');
                const k = lb.querySelectorAll('b, .sub').length;
                if (k > 2) bad.push(lb.textContent.trim().slice(0, 24) + ' = ' + k);
              });
              return bad;
            }""")
            check(not lines, "moi chang toi da 2 dong chu tren cay", str(lines[:2]))

            # Mot cot: moi vong tron phai cung mot toa do x
            xs = pg.evaluate("() => [...document.querySelectorAll('.node-btn')]"
                             ".map(e => Math.round(e.getBoundingClientRect().left))")
            # ⚠️ Vong tron cua hang NHO le trai it hon (54px vs 76px) nen tam khong
            #    trung; do MEP TRAI phai bang nhau moi la mot cot.
            check(len(set(xs)) <= 1, "cay mot cot (moi vong tron cung mot cot)",
                  str(sorted(set(xs))))

            pg.screenshot(path=f"scratchpad/proto-tree-{tag}-{case}.png", full_page=True)

        # Bang chi tiet: 3 truong hop
        pg.click('#seg button[data-case="5"]')
        pg.wait_for_timeout(250)
        # ⚠️ 5 chang da xong nay bi GAP lai, nen phai mo dai ra roi moi bam duoc vao
        #    mot chang cu. Khong mo truoc thi `.node[data-i="1"]` khong ton tai va
        #    phep do cho het 30s roi nem loi — trong y het "san pham treo".
        pg.click(".fold-btn")
        pg.wait_for_timeout(280)
        # Voi 5/7 chang da xong: chang 5 (0-based) la "lam duoc ngay", 6 la "chua mo".
        for idx, name in [(1, "da-xong"), (5, "lam-duoc"), (6, "chua-mo")]:
            pg.locator(f'.node[data-i="{idx}"] .node-btn').click()
            pg.wait_for_timeout(320)
            vis = pg.locator("#sheet").is_visible()
            check(vis, f"bang chi tiet mo duoc ({name})")
            if vis:
                pg.screenshot(path=f"scratchpad/proto-tree-{tag}-sheet-{name}.png")
                if name == "da-xong":
                    # ⚠️ So bang CHINH CHUOI TIENG VIET co dau. Go mot nhum ky tu
                    #    khong dau la lam phep kiem bao hong oan — du an da tra gia
                    #    ba lan cho dung loi nay (quy tac 8, muc 6 CLAUDE.md).
                    txt = pg.locator("#sh-note").inner_text()
                    check("không nhận thêm" in txt, "chang da xong noi ro khong them thuong")
                    check(not pg.locator("#sh-go").is_disabled(), "van choi lai duoc")
                if name == "chua-mo":
                    check(pg.locator("#sh-go").is_disabled(), "chang chua mo thi nut tat")
                pg.keyboard.press("Escape")
                pg.wait_for_timeout(220)
                check(not pg.locator("#sheet").is_visible(), f"Escape dong duoc bang ({name})")

        # Dai gap phai MO RA duoc — choi lai mot chang cu la viec co that
        pg.click('#seg button[data-case="5"]')
        pg.wait_for_timeout(280)
        pg.click(".fold-btn")
        pg.wait_for_timeout(280)
        check(pg.locator(".node.done").count() == 5, "bam dai gap thi hien du 5 hang da xong")
        check(pg.locator(".fold.up").count() == 1, "co nut thu gon lai")
        pg.locator('.node[data-i="1"] .node-btn').click()
        pg.wait_for_timeout(280)
        check(pg.locator("#sheet").is_visible(), "mo lai duoc mot chang da xong")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(200)

        check(not errs, "0 loi console", str(errs[:2]))
        ctx.close()
    br.close()


with sync_playwright() as pw:
    run(pw)

print(f"\n=== KET QUA: {OK} dat / {FAIL} hong ===")
sys.exit(1 if FAIL else 0)
