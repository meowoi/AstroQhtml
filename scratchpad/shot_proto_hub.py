# -*- coding: utf-8 -*-
"""Chup + do BAN MAU TRUNG TAM NHIEM VU (phuong an A: cua truoc).

Cau hoi sinh ra trang nay: "nhiem vu hang ngay va su kien de o dau?".
Nen bo kiem nay phai chung minh bang so DUNG BON dieu:
  [A] ba nhom dung THU TU: chinh tuyen -> hang ngay -> su kien
  [B] loi tat "Choi tiep" dua toi CHO DANG CHOI DO trong 1 cu cham
  [C] dong ho hang ngay DEM LUI THAT, va KHONG doc dong ho may
  [D] khong co su kien thi AN CA KHOI, khong hien mot khoi rong

Chay: python -m http.server 8123 (trong AstroQhtml/) roi python scratchpad/shot_proto_hub.py
"""
import io
import re
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8123/scratchpad/proto-hub.html"
OK = FAIL = 0


def check(cond, label, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"    [OK]   {label} {extra}")
    else:
        FAIL += 1
        print(f"    [HONG] {label} {extra}")


# ═══ [C-1] PHEP KIEM DOC TREN MA NGUON, KHONG CAN TRINH DUYET ═══
# ⚠️ Day la BAT BIEN cua tinh nang, khong phai chi tiet cai dat: neu "con 7 gio" tinh
#    bang gio cua MAY thi doi gio he thong la lam moi viec hang ngay. Server gui
#    `secondsLeft`, client chi tru dan.
print("\n  === [C-1] DONG HO KHONG DOC DONG HO MAY (quet ma nguon) ===")
_src = io.open("scratchpad/proto-hub.js", encoding="utf-8").read()
_code = re.sub(r"/\*.*?\*/", "", _src, flags=re.S)          # bo comment truoc khi tim
_code = re.sub(r"(?m)^\s*//.*$", "", _code)
for bad in ["Date.now(", "new Date(", "toLocaleTimeString", "getHours("]:
    check(bad not in _code, f"khong dung `{bad}`")


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
        pg.wait_for_timeout(400)
        print(f"\n  --- {tag} ---")

        # ═══ [A] BA NHOM, DUNG THU TU ═══
        order = pg.evaluate("""() => Array.from(document.querySelectorAll('.sec-t'))
                                        .map(e => e.textContent.trim())""")
        check(order == ["Chính tuyến", "Hàng ngày", "Sự kiện"],
              "ba nhom dung thu tu: chinh tuyen -> hang ngay -> su kien", str(order))

        # Nhom chinh tuyen co DUNG MOT loi di, va no dan sang ban do
        check(pg.locator(".big").count() == 1, "chinh tuyen chi co DUNG MOT loi di")
        check("proto-mission-map.html" in pg.locator(".big").get_attribute("href"),
              "loi do dan sang BAN DO")

        # ═══ [D] SU KIEN: co thi hien, khong co thi AN CA KHOI ═══
        check(pg.evaluate("() => window.__hub.eventOn"), "dang co su kien thi hien khoi")
        check(pg.locator("#events .task").count() >= 1, "su kien co it nhat mot hang")
        pg.click('#seg-ev button[data-ev="0"]')
        pg.wait_for_timeout(250)
        check(not pg.evaluate("() => window.__hub.eventOn"),
              "khong co su kien thi AN CA KHOI, khong hien khoi rong")
        # ⚠️ An khoi thi 2 nhom con lai phai lien mach, khong de lai khoang trong
        gap = pg.evaluate("""() => {
          const p = Array.from(document.querySelectorAll('.panel'))
                         .filter(e => !e.hidden);
          const last = p[p.length - 1].getBoundingClientRect();
          const warn = document.querySelector('.warn').getBoundingClientRect();
          return Math.round(warn.top - last.bottom);
        }""")
        check(0 <= gap <= 40, "an khoi khong de lai khoang trong", f"({gap}px)")
        pg.click('#seg-ev button[data-ev="1"]')
        pg.wait_for_timeout(250)

        # ═══ [B] LOI TAT "CHOI TIEP" ═══
        # ⚠️ Chua bat dau thi CHUA CO gi de "tiep"; xong het roi thi no tro vao mot
        #    chang khong ton tai. Ca hai truong hop phai AN.
        for case, want in [("0", False), ("6", True), ("7", False)]:
            pg.click(f'#seg button[data-case="{case}"]')
            pg.wait_for_timeout(250)
            check(pg.evaluate("() => window.__hub.resumeOn") == want,
                  f"loi tat hien dung luc (da xong {case} chang)", str(want))

        pg.click('#seg button[data-case="6"]')
        pg.wait_for_timeout(250)
        check("chặng 07 / 7" in pg.locator("#r-sub").inner_text(),
              "loi tat noi dung chang dang do", pg.locator("#r-sub").inner_text())
        pg.screenshot(path=f"scratchpad/proto-hub-{tag}.png", full_page=True)

        # ═══ [C-2] DONG HO DEM LUI THAT ═══
        t1 = pg.evaluate("() => window.__hub.daySec")
        txt1 = pg.locator("#day-m").inner_text()
        pg.wait_for_timeout(2200)
        t2 = pg.evaluate("() => window.__hub.daySec")
        check(t2 < t1, "dong ho hang ngay dem lui THAT", f"({t1} -> {t2})")
        check(re.match(r"^còn \d+:\d\d:\d\d$", txt1) is not None,
              "duoi mot ngay thi dem tung giay", txt1)
        # ⚠️ Tren mot ngay thi noi ngay-gio: mot day so nhay lien tuc cho mot moc hai
        #    ngay nua thi khong ai dung de lam gi.
        check("ngày" in pg.locator("#ev-m").inner_text(),
              "tren mot ngay thi noi ngay-gio", pg.locator("#ev-m").inner_text())

        # ═══ VIEC HANG NGAY: KHONG BAO GIO KHOA ═══
        # ⚠️ Viec hang ngay ma khoa theo tien do thi voi tre moi no khoa VINH VIEN o
        #    dung ngay dau tien (cung loai loi 7 mau vat `planet:*` suyt mac).
        pg.click('#seg button[data-case="0"]')
        pg.wait_for_timeout(250)
        locked = pg.evaluate("""() => Array.from(document.querySelectorAll('#daily .task'))
          .filter(li => li.className.includes('lock')).length""")
        check(locked == 0, "khong viec hang ngay nao bi khoa theo tien do", str(locked))
        # Hang DA XONG thi tat nut va noi ro da nhan thuong
        ok_rows = pg.locator("#daily .task.ok")
        check(ok_rows.count() >= 1, "co hang 'da xong' de doi chieu")
        check(ok_rows.first.locator(".task-btn").is_disabled(),
              "hang da xong thi tat nut, khong cho bam lai")
        check("đã nhận" in ok_rows.first.inner_text(),
              "hang da xong noi ro DA NHAN thuong, khong de tre tu phat hien")

        # ═══ NOI THAT: hai nhom nay chua co backend ═══
        w = pg.locator(".warn").inner_text()
        check(pg.locator(".warn").is_visible(), "co dai nhac 'du lieu gia'")
        check("dữ liệu giả" in w and "400" in w,
              "dai nhac noi thang ca hai: du lieu gia VA backend chua do")

        # ═══ KHUNG: khong tran ngang, vung cham du lon, 0 loi ═══
        ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check(ow <= 0, "khong tran ngang", f"(du {ow}px)")
        # ⚠️ KHONG DO `.seg button` — VA DAY LA LAN THU HAI TOI MAC DUNG LOI NAY.
        #    `.seg` la component DUNG CHUNG cua `css/page-shell.css`, va moc 44px cua
        #    no CO Y gan vao `@media (pointer: coarse)`: CLAUDE.md ghi ro "giao dien
        #    desktop khong doi mot pixel". Context mac dinh cua Playwright khong phai
        #    coarse, nen do o day la bao hong oan cho MOI trang dung `.seg` — va mot
        #    phep kiem hay bao oan thi som muon bi bo qua, do moi la cai gia that.
        #    Vung cham cua `.seg` da co `audit_viewports.py` do dung dieu kien coarse.
        small = pg.evaluate("""() => {
          const bad = [];
          document.querySelectorAll('.task-btn, .pbtn, .big').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width && (r.width < 48 || r.height < 44))
              bad.push(el.className + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
          });
          return bad;
        }""")
        check(not small, "vung cham du lon", str(small[:3]))

        # Duong noi: loi tat -> cay chang, dung cho dang do
        pg.click('#seg button[data-case="6"]')
        pg.wait_for_timeout(250)
        pg.click("#r-go")
        pg.wait_for_load_state("networkidle")
        check("proto-mission-tree-c.html" in pg.url and "done=6" in pg.url,
              "loi tat dan thang vao cay chang, mang theo tien do", pg.url.split("/")[-1])
        check(pg.evaluate("() => window.__treeC.curInView()"),
              "va dung san o chang dang do — 2 cu cham tu dashboard")

        check(not errs, "0 loi console", str(errs[:2]))
        ctx.close()
    br.close()


with sync_playwright() as pw:
    run(pw)

print(f"\n=== KET QUA: {OK} dat / {FAIL} hong ===")
sys.exit(1 if FAIL else 0)
