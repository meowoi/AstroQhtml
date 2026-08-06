# -*- coding: utf-8 -*-
"""Chup + do BAN B cua cay chang (duong lien mach, kieu Duolingo).

Ba thu B phai chung minh duoc, vi day la ly do ton tai cua no:
  ① mo trang la DA DUNG SAN o chang dang mo (tu cuon)
  ② cuon di xa thi hien nut "Ve cho dang choi", bam la ve dung cho
  ③ thanh dinh luon nhin thay, va no mang TIEN DO chu khong chi mang cai ten

Chay: python -m http.server 8123 (trong AstroQhtml/) roi python scratchpad/shot_proto_tree_b.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8123/scratchpad/proto-mission-tree-b.html"
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

        for case in ["0", "5", "7"]:
            # ⚠️ TAI LAI TRANG cho tung truong hop — phep kiem quan trong nhat cua ban B
            #    la "MO TRANG la da dung san o cho can lam", ma bam nut chuyen tinh
            #    huong thi khong con la luc MO TRANG nua.
            pg.goto(URL + "?done=" + case, wait_until="networkidle")
            pg.wait_for_timeout(400)
            d = int(case)
            print(f"\n  --- {tag} / da xong {case} chang ---")

            # KHONG GAP: du 7 hang luc nao cung co
            check(pg.locator(".node").count() == 7, "du 7 hang, khong gap gi",
                  str(pg.locator(".node").count()))
            check(pg.locator(".fold").count() == 0, "khong co dai gap nao (day la ban B)")

            # ① Tu cuon: chang dang mo phai nam TRONG khung nhin ngay khi mo trang
            if d < 7:
                check(pg.evaluate("() => window.__treeB.curInView()"),
                      "mo trang la da dung san o chang dang mo")
                check(not pg.evaluate("() => window.__treeB.jumpVisible"),
                      "chua can nut nhay vi dang nhin thay chang do")

            # ③ Thanh dinh luon nhin thay + mang tien do
            mb = pg.locator("#mbar").bounding_box()
            check(mb is not None and mb["y"] >= -1, "thanh dinh nam trong khung", str(round(mb["y"])))
            check(pg.locator("#m-ct").inner_text() == f"{d} / 7",
                  "thanh dinh mang TIEN DO", pg.locator("#m-ct").inner_text())

            ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(ow <= 0, "khong tran ngang", f"(du {ow}px)")

            small = pg.evaluate("""() => {
              const bad = [];
              document.querySelectorAll('.node-btn, .pbtn, .jump, .sh-x').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width && (r.width < 48 || r.height < 44))
                  bad.push(el.className + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
              });
              return bad;
            }""")
            check(not small, "vung cham du lon", str(small[:3]))

            # ⚠️ CHUP KHUNG NHIN, khong chup ca trang. Ban B TU CUON khi mo, ma anh
            #    `full_page` thi thanh dinh bi ve o dung cho no dang dinh — ra mot
            #    tam anh co header nam giua trang, trong y nhu loi bo cuc. Thu can
            #    xem la thu TRE THAY, tuc dung mot khung nhin.
            pg.screenshot(path=f"scratchpad/proto-treeb-{tag}-{case}.png")

        # ② Nut nhay: cuon len dau thi phai hien, bam la ve dung cho
        pg.goto(URL + "?done=5", wait_until="networkidle")
        pg.wait_for_timeout(400)
        pg.evaluate("() => window.scrollTo(0, 0)")
        pg.wait_for_timeout(500)
        # ⚠️ Tren man cao (desktop 960px) va chi 7 chang thi cuon len dau van CON
        #    NHIN THAY chang dang mo — luc do nut PHAI an, va do moi la dung. Doi nut
        #    hien o moi co man la bat san pham hien mot nut bam vao khong doi gi.
        still = pg.evaluate("() => window.__treeB.curInView()")
        if still:
            check(not pg.evaluate("() => window.__treeB.jumpVisible"),
                  "man du cao nen khong can nut nhay — nut an dung")
        else:
            check(pg.evaluate("() => window.__treeB.jumpVisible"),
                  "cuon di xa thi hien nut 'Ve cho dang choi'")
            check(pg.eval_on_selector("#jump .j-ar", "e => e.textContent") == "↓",
                  "mui ten chi DUNG huong phai cuon")
            pg.click("#jump")
            pg.wait_for_timeout(900)
            check(pg.evaluate("() => window.__treeB.curInView()"), "bam nut thi ve dung cho")
            check(not pg.evaluate("() => window.__treeB.jumpVisible"), "ve toi noi thi nut tu an")
        pg.screenshot(path="scratchpad/proto-treeb-jump.png")

        # Chieu cao cay — day la CAI GIA cua ban B, do ra de dat canh ban A
        h = pg.evaluate("() => document.getElementById('tree').getBoundingClientRect().height")
        print(f"    [ĐO]   chieu cao cay ban B = {round(h)}px")

        # Bang chi tiet van chay (giong ban A)
        pg.locator('.node[data-i="1"] .node-btn').click()
        pg.wait_for_timeout(300)
        check(pg.locator("#sheet").is_visible(), "bang chi tiet mo duoc")
        # ⚠️ So bang chinh chuoi tieng Viet co dau (quy tac 8, muc 6 CLAUDE.md)
        check("không nhận thêm" in pg.locator("#sh-note").inner_text(),
              "chang da xong van noi ro khong them thuong")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(220)

        check(not errs, "0 loi console", str(errs[:2]))
        ctx.close()
    br.close()


with sync_playwright() as pw:
    run(pw)

print(f"\n=== KET QUA: {OK} dat / {FAIL} hong ===")
sys.exit(1 if FAIL else 0)
