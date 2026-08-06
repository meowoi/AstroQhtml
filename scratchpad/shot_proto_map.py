# -*- coding: utf-8 -*-
"""Chup + do ban mau BAN DO NHIEM VU 2D (ban ve bang CSS).

⚠️ Ban canvas (proto-solar-map.js) DA BI BAC 04/08/2026 — kho nhin hon ban nay.
   File do con tren dia nhung khong trang nao nap.

Chay: python -m http.server 8123 (trong AstroQhtml/) roi python scratchpad/shot_proto_map.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8123/scratchpad/proto-mission-map.html"
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
            print(f"\n  --- {tag} / da xong {case} chang o Trai Dat ---")

            names = pg.eval_on_selector_all(".body .nm", "els => els.map(e => e.textContent)")
            src = pg.evaluate("() => AstroQPlanets.all().map(p => p.vi)")
            check(all(n in names for n in src) or tag == "mobile",
                  "ten hanh tinh lay tu planets.js", f"({len(src)} ten)")
            check("Mặt Trăng" in names, "co Mat Trang (khai rieng, khong nam trong planets.js)")

            check(pg.locator(".body.open").count() == 1, "dung 1 noi co nhiem vu")
            want_soon = 1 if int(case) >= 5 else 0
            check(pg.locator(".body.soon").count() == want_soon,
                  "Mat Trang 'sap ra mat' khi dat cong 5/7", str(want_soon))

            # Deco (Mat Troi) phai bam khong duoc.
            # ⚠️ Dung `dispatch_event`, KHONG dung `.click()`: Mat Troi mang
            #    `aria-disabled="true"` nen Playwright cho het 30s roi nem loi —
            #    trong y het "san pham treo" trong khi san pham dang lam DUNG.
            pg.locator(".body.deco").first.dispatch_event("click")
            pg.wait_for_timeout(200)
            check(not pg.locator("#sheet").is_visible(), "bam Mat Troi khong mo bang")

            # Dia hanh tinh phai TRON, khong bau duc
            oval = pg.evaluate("""() => {
              const bad = [];
              document.querySelectorAll('.body .orb').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width && Math.abs(r.width - r.height) > 1.5)
                  bad.push(Math.round(r.width) + 'x' + Math.round(r.height));
              });
              return bad;
            }""")
            check(not oval, "dia hanh tinh tron", str(oval[:3]))

            # Hanh tinh phai NAM TREN quy dao cua no (cung phep tinh ellipse)
            off = pg.evaluate("""() => {
              const map = document.getElementById('map').getBoundingClientRect();
              const VW = 1000, VH = 760, cx = 55, cy = 715, RY = 0.82;
              const R = {mercury:175,venus:285,earth:400,mars:520,
                         jupiter:645,saturn:760,uranus:880,neptune:985};
              const bad = [];
              document.querySelectorAll('.body').forEach(b => {
                const id = b.dataset.id; if (!R[id]) return;
                const r = b.getBoundingClientRect();
                const x = (r.left + r.width/2 - map.left) / map.width * VW;
                const y = (r.top + r.height/2 - map.top) / map.height * VH;
                const d = Math.hypot((x-cx)/R[id], (y-cy)/(R[id]*RY));
                if (Math.abs(d - 1) > 0.06) bad.push(id + ' ' + d.toFixed(3));
              });
              return bad;
            }""")
            check(not off, "moi hanh tinh nam tren quy dao cua no", str(off[:3]))

            # ⚠️ Do CHINH CAI NHAN, khong do cai nut. Mat Troi CO Y bi mep ban do cat
            #    bot (nhu ban ve tham chieu) nen do nut la bao hong oan.
            spill = pg.evaluate("""() => {
              const map = document.getElementById('map').getBoundingClientRect();
              const bad = [];
              document.querySelectorAll('.body .lb').forEach(l => {
                const r = l.getBoundingClientRect();
                const id = l.closest('.body').dataset.id;
                if (r.left < map.left - 1 || r.right > map.right + 1 ||
                    r.top < map.top - 1 || r.bottom > map.bottom + 1) bad.push(id);
              });
              return bad;
            }""")
            check(not spill, "nhan doc duoc, khong bi ban do cat", str(spill[:3]))

            # Hai nhan khong duoc de nhau — chi anh chup moi thay
            hit = pg.evaluate("""() => {
              const bad = [];
              const els = [...document.querySelectorAll('.body .nm')]
                .filter(e => e.getBoundingClientRect().width > 0);
              for (let i = 0; i < els.length; i++)
                for (let j = i + 1; j < els.length; j++) {
                  const a = els[i].getBoundingClientRect(), b = els[j].getBoundingClientRect();
                  if (a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom)
                    bad.push(els[i].textContent + ' × ' + els[j].textContent);
                }
              return bad;
            }""")
            check(not hit, "khong co hai nhan nao de nhau", str(hit[:3]))

            ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(ow <= 0, "khong tran ngang", f"(du {ow}px)")

            want_resume = 0 < int(case) < 7
            check(pg.locator("#resume").is_visible() == want_resume,
                  "loi tat 'dang do' hien dung luc", str(want_resume))

            pg.screenshot(path=f"scratchpad/proto-map-{tag}-{case}.png", full_page=True)

        # ⚠️⚠️ BA PHEP KIEM CU DAO CHIEU (04/08/2026) — chung dang KHANG DINH DUNG
        #    TRANG THAI CU: "Trai Dat mo bang chi tiet" va "Trai Dat dan sang man
        #    DANH SACH NHIEM VU (khong nhay thang vao cay chang)". Chu du an doi luat:
        #    noi CO nhiem vu thi vao thang, noi CHUA co thi moi mo bang noi vi sao.
        #    Nen chung bao hong dung luc san pham lam dung — cung loai loi da ghi o
        #    nut Mat Trang. Dieu can bao ve KHONG doi: mot cu cham phai dan toi mot
        #    cho CU THE, va cho chua mo phai noi ra ly do.
        pg.click('#seg button[data-case="5"]')
        pg.wait_for_timeout(250)

        # Noi CHUA co nhiem vu: van mo bang, va bang van la cho DUY NHAT noi ly do
        for bid, name in [("moon", "sap-ra-mat"), ("mars", "chua-co")]:
            pg.locator(f'.body[data-id="{bid}"]').click()
            pg.wait_for_timeout(300)
            vis = pg.locator("#sheet").is_visible()
            check(vis, f"noi chua co nhiem vu: van mo bang ({name})")
            if vis:
                check(pg.locator("#sh-h").inner_text() ==
                      {"moon": "Mặt Trăng", "mars": "Sao Hoả"}[bid],
                      f"bang mo dung thien the ({name})")
                pg.screenshot(path=f"scratchpad/proto-map-{tag}-sheet-{name}.png")
                if bid == "moon":
                    check(pg.locator("#sh-go").is_disabled(), "Mat Trang: nut tat vi chua co nhiem vu")
                if bid == "mars":
                    # ⚠️ So bang chinh chuoi tieng Viet co dau (quy tac 8, muc 6 CLAUDE.md)
                    check("vẫn ghé thăm" in pg.locator("#sh-p").inner_text(),
                          "noi ro 'chua co nhiem vu' KHAC 'bi cam toi'")
                pg.keyboard.press("Escape")
                pg.wait_for_timeout(220)

        # Noi CO nhiem vu: KHONG mo bang nua, vao thang cay chang tai cho dang do
        pg.locator('.body[data-id="earth"]').click()
        pg.wait_for_timeout(400)
        check(not pg.locator("#sheet").is_visible() or "proto-mission-tree-c" in pg.url,
              "bam Trai Dat KHONG con mo bang trung gian")
        pg.wait_for_load_state("networkidle")
        check("proto-mission-tree-c.html" in pg.url,
              "vao THANG cay chang cua Nhiem vu 01", pg.url.split("/")[-1])
        check("done=5" in pg.url, "mang theo dung tien do", pg.url.split("?")[-1])
        # ⚠️ Day moi la dieu chu du an yeu cau: "tai diem dang dung do LUON".
        #    Toi dung URL thi chua du — phai chung minh MAN HINH dang o dung cho do.
        check(pg.evaluate("() => window.__treeC.curInView()"),
              "va dung san o CHO DANG CHOI DO, khong phai dau danh sach")
        check(pg.locator(".node.now .bub").count() == 1, "chang dang mo co ten hien ra")

        # Danh sach nhiem vu KHONG duoc bien mat — Trai Dat se co nhiem vu 02, 03...
        pg.click("#more")
        pg.wait_for_load_state("networkidle")
        check("proto-planet.html" in pg.url,
              "van toi duoc danh sach nhiem vu tu cuoi duong", pg.url.split("/")[-1])
        check(pg.locator("#list > li").count() > 0, "man hanh tinh ve duoc danh sach")

        # Loi tat "Choi tiep" phai dan toi CUNG mot cho — hai duong vao cho mot viec
        # thi som muon lech nhau.
        pg.goto(URL, wait_until="networkidle")
        pg.click('#seg button[data-case="5"]')
        pg.wait_for_timeout(250)
        pg.click("#r-go")
        pg.wait_for_load_state("networkidle")
        check("proto-mission-tree-c.html" in pg.url and "done=5" in pg.url,
              "loi tat 'Choi tiep' dan cung mot cho voi cu cham tren ban do",
              pg.url.split("/")[-1])
        pg.goto(URL, wait_until="networkidle")

        check(not errs, "0 loi console", str(errs[:2]))
        ctx.close()
    br.close()


with sync_playwright() as pw:
    run(pw)

print(f"\n=== KET QUA: {OK} dat / {FAIL} hong ===")
sys.exit(1 if FAIL else 0)
