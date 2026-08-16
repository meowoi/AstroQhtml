# -*- coding: utf-8 -*-
"""
smoke_crew.py — PHI HÀNH ĐOÀN ĐẦU TIÊN trên Chromium thật.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/smoke_crew.py

⚠️⚠️ PHÉP KIỂM QUAN TRỌNG NHẤT: **trang không được hiện một mẩu dữ liệu cá nhân
   nào**. Người dùng là trẻ em và trang này ai cũng mở được. Bộ đo gieo một email
   và một cái TÊN vào phản hồi giả rồi đòi **không chữ nào trong hai thứ đó xuất
   hiện trên màn hình** — chứ không chỉ đọc mã nguồn.

⚠️ Gieo phản hồi bằng `route()` thay vì gọi API thật: bộ đo phải chạy được khi
   backend không bật, và phải dựng được những trạng thái không tồn tại trong dữ
   liệu thật (danh sách rỗng · đủ 500 chỗ · mất mạng).
"""
import json
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/crew.html"
ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def seats(n, chars=None):
    chars = chars or {}
    return [{"no": i + 1, "ch": chars.get(i + 1)} for i in range(n)]


def open_page(br, crew=None, mine=None, fail=False, lang="vi", w=1280, h=900,
              signed_in=False):
    ctx = br.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)

    pg.add_init_script("localStorage.setItem('astroq-lang','%s');" % lang)
    if signed_in:
        # ⚠️ Gieo bang `Object.defineProperty` co setter nuot loi gan: module ES
        #    that chay SAU script co dien va se ghi de mot phep gan thuong (bai hoc
        #    da ghi o smoke_mission_intro).
        pg.add_init_script("""
          const stub = { idToken: async () => "tok-gia" };
          Object.defineProperty(window, 'AstroQAuth',
            { get: () => stub, set: () => {}, configurable: true });
        """)

    def handle(route):
        if fail:
            route.fulfill(status=500, content_type="application/json", body="{}")
            return
        route.fulfill(status=200, content_type="application/json",
                      headers={"Access-Control-Allow-Origin": "*"},
                      body=json.dumps(crew))

    pg.route(re.compile(r".*/crew(\?.*)?$"), handle)
    pg.route(re.compile(r".*/me/crew.*"), lambda r: r.fulfill(
        status=200, content_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
        body=json.dumps(mine if mine is not None else {"no": None, "ch": None})))

    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(900)
    return ctx, pg, errs


def main():
    print(f"=== Phi hanh doan dau tien @ {URL} ===")
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ---------- [1] Danh sách bình thường ----------
        print("\n[1] Danh sach binh thuong")
        crew = {"cap": 500, "taken": 7,
                "seats": seats(7, {1: "cho", 2: "m", 4: "b"})}
        ctx, pg, errs = open_page(br, crew)
        check("dem dung so cho da co nguoi", pg.inner_text("#taken") == "7",
              pg.inner_text("#taken"))
        check("noi ro tren tong bao nhieu", "500" in pg.inner_text("#of"),
              pg.inner_text("#of"))
        check("ve du 7 cho", pg.locator(".cw-seat").count() == 7)
        check("so hieu dem tu #001", pg.locator(".cw-no").first.inner_text() == "#001",
              pg.locator(".cw-no").first.inner_text())
        # 3 nguoi da chon nhan vat -> 3 anh, 4 nguoi chua -> 4 mu chung.
        check("ai da chon nhan vat thi hien ANH", pg.locator(".cw-seat img").count() == 3,
              str(pg.locator(".cw-seat img").count()))
        check("ai chua chon thi hien mu chung, KHONG gan bua nhan vat",
              pg.locator(".cw-helm").count() == 4,
              str(pg.locator(".cw-helm").count()))
        check("thanh do dai dung ti le",
              pg.evaluate("() => document.getElementById('track').style.width") == "1.4%",
              pg.evaluate("() => document.getElementById('track').style.width"))
        check("KHONG ve du 500 o rong", pg.locator(".cw-seat").count() < 20)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [2] KHÔNG rò dữ liệu cá nhân ----------
        # ⚠️ MUC QUAN TRONG NHAT. Gieo ca email lan TEN vao phan hoi roi doi man
        #    hinh khong co chu nao trong hai thu do — do tren TRANG, khong doc ma.
        print("\n[2] Khong ro mot mau du lieu ca nhan nao")
        leak = {"cap": 500, "taken": 2, "seats": [
            {"no": 1, "ch": "cho", "email": "be-an@gmail.com", "name": "Nguyễn Bé An"},
            {"no": 2, "ch": None, "email": "me-cua-an@gmail.com", "name": "Trần Thị B"}]}
        ctx, pg, errs = open_page(br, leak)
        body = pg.inner_text("body")
        html = pg.content()
        for bad in ("be-an@gmail.com", "me-cua-an@gmail.com", "Nguyễn Bé An",
                    "Trần Thị B"):
            check(f"khong hien '{bad}'", bad not in body and bad not in html)
        check("khong co ky tu @ nao tren man hinh", "@" not in body, body[:80])
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [3] Chỗ của chính mình ----------
        print("\n[3] Cho cua chinh minh")
        ctx, pg, errs = open_page(br, crew, mine={"no": 4, "ch": "b"}, signed_in=True)
        check("hien dong 'cho cua ban'", pg.is_visible("#you"))
        check("noi dung so hieu", "#4" in pg.inner_text("#you"), pg.inner_text("#you"))
        check("to sang DUNG mot cho", pg.locator(".cw-seat.me").count() == 1)
        me_no = pg.locator(".cw-seat.me .cw-no").inner_text()
        check("to sang dung cho so 4", me_no == "#004", me_no)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # Nguoi da dang nhap nhung KHONG nam trong doan
        ctx, pg, errs = open_page(br, crew, mine={"no": None, "ch": None},
                                  signed_in=True)
        check("khong trong doan: noi that, khong to sang cho nao",
              pg.is_visible("#you") and pg.locator(".cw-seat.me").count() == 0,
              pg.inner_text("#you")[:70])
        ctx.close()

        # Chua dang nhap: van xem duoc danh sach, chi khong co dong "cho cua ban"
        ctx, pg, errs = open_page(br, crew)
        check("chua dang nhap: van ve du danh sach",
              pg.locator(".cw-seat").count() == 7)
        check("chua dang nhap: KHONG hien dong 'cho cua ban'",
              not pg.is_visible("#you"))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [4] Danh sách rỗng ----------
        print("\n[4] Chua co ai")
        ctx, pg, errs = open_page(br, {"cap": 500, "taken": 0, "seats": []})
        check("hien loi moi lam nguoi dau tien", pg.is_visible("#empty"))
        check("dem la 0, khong phai dau —", pg.inner_text("#taken") == "0",
              pg.inner_text("#taken"))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [5] Mất mạng: NÓI THẬT, không bịa số 0 ----------
        # ⚠️ "0 nguoi" la mot loi khang dinh SAI khi thuc ra la chua doc duoc.
        #    Cung nguyen tac dau `—` cua missions.html.
        print("\n[5] Chua doc duoc — noi that, khong bia so 0")
        ctx, pg, errs = open_page(br, fail=True)
        check("hien dai nhac", pg.is_visible("#banner"))
        check("dai nhac noi ro la chua doc duoc",
              "mạng" in pg.inner_text("#banner").lower(), pg.inner_text("#banner")[:70])
        check("dem hien dau — chu KHONG hien 0", pg.inner_text("#taken") == "—",
              pg.inner_text("#taken"))
        check("KHONG hien 'chua co ai' (do la mot cau khac han)",
              not pg.is_visible("#empty"))
        check("KHONG ve cho nao", pg.locator(".cw-seat").count() == 0)
        ctx.close()

        # ---------- [6] Đủ 500 chỗ ----------
        print("\n[6] Du 500 cho")
        full = {"cap": 500, "taken": 500, "seats": seats(500)}
        ctx, pg, errs = open_page(br, full)
        check("ve du 500 cho", pg.locator(".cw-seat").count() == 500)
        check("thanh do day 100%",
              pg.evaluate("() => document.getElementById('track').style.width") == "100%")
        check("so hieu cuoi la #500",
              pg.locator(".cw-no").last.inner_text() == "#500",
              pg.locator(".cw-no").last.inner_text())
        check("khong tran ngang",
              pg.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 1)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [7] Nhân vật lạ thì không được vỡ ----------
        print("\n[7] Nhan vat server tra ve ma client chua biet")
        odd = {"cap": 500, "taken": 2,
               "seats": [{"no": 1, "ch": "khong-co-nhan-vat-nay"}, {"no": 2, "ch": "m"}]}
        ctx, pg, errs = open_page(br, odd)
        check("van ve du 2 cho", pg.locator(".cw-seat").count() == 2)
        check("cho co nhan vat la thi lui ve mu chung",
              pg.locator(".cw-helm").count() == 1)
        check("0 loi trang, 0 anh hong", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [8] EN + điện thoại ----------
        print("\n[8] Tieng Anh · dien thoai")
        ctx, pg, errs = open_page(br, crew, lang="en")
        check("tieu de dich sang EN", "Founding Crew" in pg.title(), pg.title())
        check("chu tren trang khong con dau tieng Viet",
              not re.search(r"[ăâđêôơư]", pg.inner_text(".panel")),
              pg.inner_text(".panel")[:70].replace("\n", " "))
        ctx.close()

        ctx, pg, errs = open_page(br, crew, w=390, h=844)
        d = pg.evaluate("""() => ({
          ovf: document.documentElement.scrollWidth - innerWidth,
          cols: getComputedStyle(document.getElementById('grid'))
                  .gridTemplateColumns.split(' ').length,
          cut: [...document.querySelectorAll('.cw-no,.cw-count b,.cw-count span')]
                 .some(e => e.scrollWidth > e.clientWidth + 1)
        })""")
        check("khong tran ngang", d["ovf"] <= 1, f'{d["ovf"]}px')
        check("luoi KHONG rot ve 1 cot", d["cols"] >= 4, f'{d["cols"]} cot')
        check("khong chu nao bi cat", not d["cut"])
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
