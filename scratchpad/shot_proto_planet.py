# -*- coding: utf-8 -*-
"""Chup + do ban mau MAN HANH TINH (11 nhiem vu).

Cau hoi can tra loi bang so: "them 10 nhiem vu nua thi bo cuc thanh gi?"
=> Phep kiem quan trong nhat o day la CHIEU CAO KHONG TANG THEO SO NHIEM VU.

Chay: python -m http.server 8123 (trong AstroQhtml/) roi python scratchpad/shot_proto_planet.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8123/scratchpad/proto-planet.html"
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

        heights = {}
        for case in ["0", "1", "4", "11"]:
            pg.click(f'#seg button[data-case="{case}"]')
            pg.wait_for_timeout(300)
            d = int(case)
            print(f"\n  --- {tag} / da xong {case} nhiem vu ---")

            # ⚠️ PHEP KIEM QUAN TRONG NHAT: so HANG khong tang theo so nhiem vu.
            rows = pg.locator("#list > li").count()
            check(rows <= 6, "toi da 6 hang du co 11 nhiem vu", f"({rows} hang)")

            h = pg.evaluate("() => document.getElementById('list').getBoundingClientRect().height")
            heights[case] = round(h)
            check(h < 640, "danh sach khong dai ngoang", f"({round(h)}px)")

            check(pg.locator(".node.now").count() == (1 if d < 11 else 0),
                  "dung 1 nhiem vu dang choi", str(pg.locator(".node.now").count()))
            check(pg.locator("#finish").is_visible() == (d == 11),
                  "the ket hien dung luc", str(d == 11))

            ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(ow <= 0, "khong tran ngang", f"(du {ow}px)")

            small = pg.evaluate("""() => {
              const bad = [];
              document.querySelectorAll('.node-btn, .fold-btn, .pbtn').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width && (r.width < 48 || r.height < 44))
                  bad.push(el.className + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
              });
              return bad;
            }""")
            check(not small, "vung cham du lon", str(small[:3]))

            # ⚠️ CUNG MOT LOI voi cay chang: "can het ve trai, trong het ben phai".
            #    O day khong bo duoc nhan chu (11 nhiem vu khac nhau, phai doc ten moi
            #    chon duoc) nen chua bang HANG THE TRAI HET BE RONG. Phep kiem: hang
            #    phai rong gan bang cot, va mui chi phai neo o mep phai.
            fill = pg.evaluate("""() => {
              const ul = document.getElementById('list');
              const uw = ul.getBoundingClientRect().width;
              let worst = 1, gap = 0;
              document.querySelectorAll('#list .node').forEach(n => {
                const r = n.getBoundingClientRect();
                worst = Math.min(worst, r.width / uw);
                const c = n.querySelector('.chev');
                if (c) gap = Math.max(gap, r.right - c.getBoundingClientRect().right);
              });
              return { worst: Math.round(worst * 100), gap: Math.round(gap) };
            }""")
            check(fill["worst"] >= 99, "hang nhiem vu trai het be rong cot",
                  f"({fill['worst']}%)")
            check(fill["gap"] <= 16, "mui chi neo sat mep phai", f"({fill['gap']}px)")

            pg.screenshot(path=f"scratchpad/proto-planet-{tag}-{case}.png", full_page=True)

        # ⚠️ Day la CAU TRA LOI cho "them 10 nhiem vu thi sao".
        #    BO truong hop "xong het" ra khoi phep so: luc do danh sach chi con MOT
        #    dai gap (57px) nen no keo bien do rong ra ma khong noi len dieu gi —
        #    do la mot TRANG THAI khac, khong phai mot muc tien do.
        act = {k: v for k, v in heights.items() if k != "11"}
        spread = max(act.values()) - min(act.values())
        check(spread < 150, "chieu cao gan nhu khong doi theo tien do", f"({act})")

        # Dai gap "con N nhiem vu nua" phai mo ra duoc — giau han la lay di duong di
        pg.click('#seg button[data-case="4"]')
        pg.wait_for_timeout(280)
        check(pg.locator("#fold-rest").count() == 1, "co dai 'con N nhiem vu nua'")
        before = pg.locator(".node").count()
        pg.click("#fold-rest .fold-btn")
        pg.wait_for_timeout(280)
        check(pg.locator(".node").count() > before, "bam ra thi hien ca hanh trinh",
              f"({before} -> {pg.locator('.node').count()})")

        # Nhiem vu THAT thi dan sang cay chang; ten gia thi noi that
        pg.click('#seg button[data-case="4"]')
        pg.wait_for_timeout(280)
        pg.click("#fold-done .fold-btn")          # mo phan da xong
        pg.wait_for_timeout(280)
        pg.locator('.node[data-i="0"] .node-btn').click()
        pg.wait_for_load_state("networkidle")
        # ⚠️ Doi sang ban C 04/08/2026: hai duong vao cung MOT nhiem vu (tu ban do va
        #    tu danh sach nay) phai dan toi CUNG mot man, khong thi tre tuong la hai
        #    nhiem vu khac nhau.
        check("proto-mission-tree-c.html" in pg.url, "nhiem vu 01 dan sang cay chang ban C",
              pg.url.split("/")[-1])
        pg.go_back()
        pg.wait_for_load_state("networkidle")
        pg.click('#seg button[data-case="0"]')
        pg.wait_for_timeout(280)
        pg.locator('.node[data-i="1"] .node-btn').click()   # ten gia
        pg.wait_for_timeout(300)
        # ⚠️ So bang chinh chuoi tieng Viet co dau (quy tac 8, muc 6 CLAUDE.md)
        check("chưa có nội dung" in pg.locator("#toast").inner_text(),
              "ten gia thi noi that, khong dan di dau")

        check(not errs, "0 loi console", str(errs[:2]))
        ctx.close()
    br.close()


with sync_playwright() as pw:
    run(pw)

print(f"\n=== KET QUA: {OK} dat / {FAIL} hong ===")
sys.exit(1 if FAIL else 0)
