# -*- coding: utf-8 -*-
"""Chup + do BAN C cua cay chang (duong uon giua man, khong nhan chu).

Ban C sinh ra tu MOT loi chu du an bao: "nhiem vu se bi can het ve phia trai,
trong het ben phai". Nen phep kiem quan trong nhat cua bo nay la DO CAI DO:
  [A] khoang trong hai ben CUA CA BA BAN, dat canh nhau, cung mot du lieu
  [B] ban C khong con nhan chu nao canh nut
  [C] bong bong ten chi o chang dang mo, va no chi dung vao nut
  [D] giu nguyen co che cua B: tu cuon, nut nhay, thanh dinh mang tien do

Chay: python -m http.server 8123 (trong AstroQhtml/) roi python scratchpad/shot_proto_tree_c.py
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/scratchpad/"
URL = BASE + "proto-mission-tree-c.html"
OK = FAIL = 0

# Do khoang trong hai ben cua CUM NOI DUNG trong khung kinh.
# `.node > *` = vong tron + (o ban A/B) nhan chu. Bong bong cua ban C khong tinh:
# no la lop noi ben tren, khong phai mot cot noi dung.
EXTENT = """() => {
  const p = document.querySelector('#tree').closest('.panel');
  const pr = p.getBoundingClientRect();
  let l = Infinity, r = -Infinity;
  document.querySelectorAll('#tree .node > *').forEach(el => {
    if (el.classList.contains('bub')) return;
    const b = el.getBoundingClientRect();
    if (b.width === 0) return;
    l = Math.min(l, b.left); r = Math.max(r, b.right);
  });
  return { left: Math.round(l - pr.left), right: Math.round(pr.right - r),
           pw: Math.round(pr.width) };
}"""


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

    # ═══ [A] BA BAN, CUNG DU LIEU (done=0), DAT CANH NHAU ═══
    # Chon done=0 vi o do ban A va ban B ve GIONG HET nhau (chua co dai gap nao),
    # nen chenh lech do duoc la chenh lech cua CACH VE, khong phai cua co che.
    print("\n  === [A] KHOANG TRONG HAI BEN — 1440x960, da xong 0 chang ===")
    ctx = br.new_context(viewport={"width": 1440, "height": 960}, device_scale_factor=2)
    pg = ctx.new_page()
    ext = {}
    for tag, f in [("A (gap)", "proto-mission-tree.html"),
                   ("B (nhan)", "proto-mission-tree-b.html"),
                   ("C (uon)", "proto-mission-tree-c.html")]:
        pg.goto(BASE + f + "?done=0", wait_until="networkidle")
        pg.wait_for_timeout(350)
        e = pg.evaluate(EXTENT)
        ext[tag] = e
        print(f"    [ĐO]   {tag:10s} trong trai {e['left']:4d}px · "
              f"trong phai {e['right']:4d}px · lech {abs(e['right']-e['left']):4d}px "
              f"(khung {e['pw']}px)")

    # Ban C phai can giua: lech hai ben khong qua 24px.
    c = ext["C (uon)"]
    check(abs(c["right"] - c["left"]) <= 24,
          "ban C: cum noi dung CAN GIUA khung", f"(lech {abs(c['right']-c['left'])}px)")
    # Va no phai do HON HAN ban B — neu khong thi ban C khong giai quyet gi.
    b = ext["B (nhan)"]
    check(abs(c["right"] - c["left"]) < abs(b["right"] - b["left"]) / 2,
          "ban C lech it hon MOT NUA so voi ban B")
    ctx.close()

    # ═══ [B]–[D] SOI KY BAN C ═══
    for vp, tag in [({"width": 1440, "height": 960}, "desktop"),
                    ({"width": 390, "height": 844}, "mobile")]:
        ctx = br.new_context(viewport=vp, device_scale_factor=2)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

        for case in ["0", "5", "7"]:
            pg.goto(URL + "?done=" + case, wait_until="networkidle")
            pg.wait_for_timeout(400)
            d = int(case)
            print(f"\n  --- {tag} / da xong {case} chang ---")

            check(pg.locator(".node").count() == 7, "du 7 hang")
            # [B] Khong con nhan chu nao canh nut — day la thay doi cua ban C
            check(pg.locator(".node-lb").count() == 0, "khong co nhan chu nao canh nut")

            # ⚠️ Doan noi doc cua ban A phai TAT han. No neo `left:38px` (dung cho mot
            #    cot thang) trong khi nut da doi cho bang `translateX` -> o lai thanh
            #    may vach mo lo lung khong noi vao dau. Anh chup moi thay.
            conn = pg.evaluate("""() => getComputedStyle(
              document.querySelectorAll('#tree .node')[1], '::before').display""")
            check(conn == "none", "khong con doan noi doc cua ban A", conn)

            # Cot van can giua o moi tinh huong
            e = pg.evaluate(EXTENT)
            check(abs(e["right"] - e["left"]) <= 24, "cot van can giua",
                  f"(trai {e['left']} · phai {e['right']})")

            # [C] Bong bong: dung MOT cai, dung o chang dang mo
            nb = pg.locator(".bub").count()
            if d < 7:
                check(nb == 1, "dung MOT bong bong ten", str(nb))
                check(pg.locator(".node.now .bub").count() == 1,
                      "bong bong nam o chang DANG MO")
                # ⚠️ Bong bong canh giua COT, con mui nhon chay theo NUT. Phep kiem
                #    that su can: tam nut phai nam TRONG be ngang bong bong — khong
                #    thi mui nhon chi ra ngoai bong bong, tro thanh mot tam giac roi.
                ins = pg.evaluate("""() => {
                  const n = document.querySelector('.node.now');
                  const btn = n.querySelector('.node-btn').getBoundingClientRect();
                  const bub = n.querySelector('.bub').getBoundingClientRect();
                  const cx = btn.left + btn.width / 2;
                  return { inside: cx > bub.left + 6 && cx < bub.right - 6,
                           gap: Math.round(bub.bottom - n.getBoundingClientRect().top) };
                }""")
                check(ins["inside"], "tam nut nam trong be ngang bong bong (mui nhon chi dung cho)")
                check(pg.locator(".node.now .bub").is_visible(), "bong bong nhin thay duoc")

                # ⚠️ LOI THAT, CHI ANH CHUP MOI THAY (04/08/2026): bong bong cao ~68px
                #    ma khoang cach hang chi 86px -> no PHU KIN chang ngay phia tren,
                #    tre mat luon mot dau ✓ vua kiem duoc. Do bang dien tich chong lan.
                ov = pg.evaluate("""() => {
                  const b = document.querySelector('.node.now .bub').getBoundingClientRect();
                  let worst = 0, who = '';
                  document.querySelectorAll('.node-btn').forEach((el, i) => {
                    const r = el.getBoundingClientRect();
                    const w = Math.max(0, Math.min(b.right, r.right) - Math.max(b.left, r.left));
                    const h = Math.max(0, Math.min(b.bottom, r.bottom) - Math.max(b.top, r.top));
                    if (w * h > worst) { worst = w * h; who = 'nut ' + (i + 1); }
                  });
                  return { area: Math.round(worst), who: who };
                }""")
                check(ov["area"] == 0, "bong bong KHONG de len nut nao",
                      f"({ov['area']}px² {ov['who']})")
            else:
                check(nb == 0, "xong het thi khong con bong bong nao", str(nb))
                check(not pg.locator("#finish").is_hidden(), "hien the ket")

            # [D] Co che cua ban B con nguyen
            if d < 7:
                check(pg.evaluate("() => window.__treeC.curInView()"),
                      "mo trang la da dung san o chang dang mo")
                check(not pg.evaluate("() => window.__treeC.jumpVisible"),
                      "chua can nut nhay vi dang nhin thay chang do")
            mb = pg.locator("#mbar").bounding_box()
            check(mb is not None and mb["y"] >= -1, "thanh dinh nam trong khung",
                  str(round(mb["y"])))
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

            # ⚠️ Chup KHUNG NHIN, khong chup ca trang: trang tu cuon khi mo, ma anh
            #    `full_page` thi thanh dinh bi ve o dung cho no dang dinh.
            pg.screenshot(path=f"scratchpad/proto-treec-{tag}-{case}.png")

        # Nut nhay
        pg.goto(URL + "?done=5", wait_until="networkidle")
        pg.wait_for_timeout(400)
        pg.evaluate("() => window.scrollTo(0, 0)")
        pg.wait_for_timeout(500)
        still = pg.evaluate("() => window.__treeC.curInView()")
        if still:
            check(not pg.evaluate("() => window.__treeC.jumpVisible"),
                  "man du cao nen khong can nut nhay — nut an dung")
        else:
            check(pg.evaluate("() => window.__treeC.jumpVisible"),
                  "cuon di xa thi hien nut 'Ve cho dang choi'")
            pg.click("#jump")
            pg.wait_for_timeout(900)
            check(pg.evaluate("() => window.__treeC.curInView()"), "bam nut thi ve dung cho")
        pg.screenshot(path=f"scratchpad/proto-treec-{tag}-jump.png")

        h = pg.evaluate("() => document.getElementById('tree').getBoundingClientRect().height")
        print(f"    [ĐO]   chieu cao duong ban C = {round(h)}px")

        # Bang chi tiet van chay
        pg.locator('.node[data-i="1"] .node-btn').click()
        pg.wait_for_timeout(300)
        check(pg.locator("#sheet").is_visible(), "bang chi tiet mo duoc")
        check("Lần theo dòng thời gian" in pg.locator("#sh-h").inner_text(),
              "bang chi tiet mang TEN chang — cho nhan chu chuyen ve day")
        check("không nhận thêm" in pg.locator("#sh-note").inner_text(),
              "chang da xong van noi ro khong them thuong")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(220)

        # ═══ [E] CHANG CHUA MO: CHAN HAN, NHUNG VAN NOI RA LY DO ═══
        pg.goto(URL + "?done=5", wait_until="networkidle")
        pg.wait_for_timeout(350)
        lock = pg.locator(".node.lock").first
        check(lock.locator(".node-btn").is_disabled(),
              "nut cua chang chua mo bi TAT han (khong chi chan bang JS)")
        # ⚠️ Bam vao ca HANG chu khong vao nut — nut da `disabled` nen Playwright se
        #    ngoi cho no bat len roi het han. Cai can do la: cham vao do thi KHONG co
        #    gi mo ra.
        lock.click()
        pg.wait_for_timeout(300)
        check(not pg.locator("#sheet").is_visible(),
              "cham chang chua mo thi KHONG mo bang nao")
        # ⚠️ PHEP KIEM QUAN TRONG NHAT CUA MUC NAY. Chan han la lay di cho DUY NHAT
        #    noi ra dieu kien mo (bai hoc js/route-gate.js). Nen dieu kien phai doc
        #    duoc MA KHONG PHAI CHAM VAO DAU.
        check(pg.locator("#rule").is_visible(), "dieu kien mo van doc duoc, khong can cham")
        check("xong chặng đang sáng" in pg.locator("#rule").inner_text(),
              "cau do noi dung luat", pg.locator("#rule").inner_text()[:44])

        # ═══ [F] XONG MOT CHANG: HOI TIEP HAY DUNG ═══
        pg.locator(".node.now .node-btn").click()
        pg.wait_for_timeout(300)
        pg.click("#sh-go")
        pg.wait_for_timeout(400)
        check(pg.evaluate("() => window.__treeC.afterOpen"), "xong chang thi HOI, khong tu quyet")
        check(pg.locator("#m-ct").inner_text() == "6 / 7", "tien do tang dung 1",
              pg.locator("#m-ct").inner_text())
        check(pg.locator("#af-next").is_visible() and pg.locator("#af-stop").is_visible(),
              "co du HAI lua chon: tiep va dung")
        # ⚠️ done=5 -> chang DANG MO la chang 06; choi xong no thi chang sau la 07.
        #    Ban dau toi doi "06" — do la mot lech mot don vi trong chinh phep kiem.
        check("07" in pg.locator("#af-next").inner_text(),
              "nut tiep goi dung ten chang sau", pg.locator("#af-next").inner_text())
        check("chặng 06" in pg.locator("#af-tag").inner_text().lower() or
              "6 / 7" in pg.locator("#af-tag").inner_text(),
              "hop noi dung chang VUA XONG", pg.locator("#af-tag").inner_text())
        pg.screenshot(path=f"scratchpad/proto-treec-{tag}-after.png")
        pg.click("#af-next")
        pg.wait_for_timeout(700)
        check(not pg.evaluate("() => window.__treeC.afterOpen"), "chon 'tiep' thi hop dong")
        check(pg.evaluate("() => window.__treeC.curInView()"), "va dua toi chang moi")

        # Chang CUOI: khong con gi de hoi tiep
        pg.goto(URL + "?done=6", wait_until="networkidle")
        pg.wait_for_timeout(350)
        pg.locator(".node.now .node-btn").click()
        pg.wait_for_timeout(300)
        pg.click("#sh-go")
        pg.wait_for_timeout(400)
        check(pg.locator("#af-next").is_hidden(),
              "chang cuoi: khong hoi 'choi tiep' vi khong con chang nao")
        check("bản đồ" in pg.locator("#af-stop").inner_text(),
              "chang cuoi: duong ra la ve ban do", pg.locator("#af-stop").inner_text())

        # ⚠️ CHOI LAI mot chang cu thi KHONG hoi — khong co chang nao vua mo ra de di
        #    tiep, va tien do khong nhuc nhich. Hoi o do la hoi mot cau vo nghia.
        pg.goto(URL + "?done=5", wait_until="networkidle")
        pg.wait_for_timeout(350)
        pg.locator('.node[data-i="1"] .node-btn').click()
        pg.wait_for_timeout(300)
        pg.click("#sh-go")
        pg.wait_for_timeout(400)
        check(not pg.evaluate("() => window.__treeC.afterOpen"), "choi LAI thi khong hoi")
        check(pg.locator("#m-ct").inner_text() == "5 / 7", "choi lai KHONG lam tang tien do",
              pg.locator("#m-ct").inner_text())

        # ═══ HAI DUONG RA — ban do bo qua man hanh tinh nen phai kiem ca hai ═══
        pg.goto(URL + "?done=5", wait_until="networkidle")
        pg.wait_for_timeout(300)
        pg.click(".back-btn")
        pg.wait_for_load_state("networkidle")
        check("proto-mission-map.html" in pg.url,
              "nut quay lai ve dung BAN DO (cho tre vua roi khoi)", pg.url.split("/")[-1])

        pg.goto(URL + "?done=5", wait_until="networkidle")
        pg.wait_for_timeout(300)
        mr = pg.locator("#more").bounding_box()
        check(mr is not None and mr["height"] >= 48, "loi phu van du cao de bam",
              str(round(mr["height"]) if mr else "?"))
        pg.click("#more")
        pg.wait_for_load_state("networkidle")
        check("proto-planet.html" in pg.url,
              "van toi duoc danh sach nhiem vu o Trai Dat", pg.url.split("/")[-1])

        check(not errs, "0 loi console", str(errs[:2]))
        ctx.close()
    br.close()


with sync_playwright() as pw:
    run(pw)

print(f"\n=== KET QUA: {OK} dat / {FAIL} hong ===")
sys.exit(1 if FAIL else 0)
