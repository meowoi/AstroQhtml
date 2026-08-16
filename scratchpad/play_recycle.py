# -*- coding: utf-8 -*-
"""
play_recycle.py — CHƠI THẬT Trạm Tuần Hoàn (ARCADE-09) trên Chromium.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/play_recycle.py

Khuôn CHIA NGÂN SÁCH, nên bộ đo hỏi những câu hai game lớp quyết định kia không có:

  · ⚠️⚠️ **CÂN BẰNG LÀ MỘT TÍNH CHẤT PHẢI ĐO, KHÔNG PHẢI MỘT LỜI HỨA.** Cả bài
    tập chỉ tồn tại nếu **không tổ hợp chia điện nào giữ được cả ba vạch đứng
    yên** trong một ngày — có một tổ hợp "an toàn tuyệt đối" là trẻ tìm ra rồi
    lặp lại năm lần, và game hết ý nghĩa. Mục [2] duyệt HẾT mọi tổ hợp bằng
    chính bộ số của game.
  · Dây nối có nguồn (máy oxy TỐN NƯỚC) có thật sự chạy không, và có bị "máy nước
    bù lại ngay trong cùng ngày" không — đó là thứ hàm huỷ cả bài học.
  · Bắt chia HẾT điện mới cho chạy: còn thừa mà chạy được thì trẻ bấm bừa cho
    xong và không bao giờ gặp phải sự đánh đổi.
  · Một vạch chạm 0 thì lượt DỪNG, và màn kết nói đúng vạch nào đã cạn.
"""
import itertools
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-recycle.html"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def open_page(br, lang="vi", tt=40, w=1440, h=900):
    ctx = br.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    pg.add_init_script("localStorage.setItem('astroq-lang','%s');"
                       "localStorage.setItem('astroq-asteroids','%d');"
                       "localStorage.removeItem('astroq-recycle-best');" % (lang, tt))
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#ov-start.show", timeout=8000)
    return ctx, pg, errs


def give(pg, k, n):
    for _ in range(n):
        pg.locator('.rc-btn[data-k="%s"][data-d="1"]' % k).click()
        pg.wait_for_timeout(55)


def spend_all(pg, w, a, o):
    give(pg, "w", w); give(pg, "a", a); give(pg, "o", o)


def main():
    print(f"=== Tram Tuan Hoan (ARCADE-09) @ {URL} ===")
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ---------- [1] Cấu hình ----------
        print("\n[1] Cau hinh mo phong")
        ctx, pg, errs = open_page(br)
        cfg = pg.evaluate("() => window.__dbg.cfg()")
        maxp = pg.evaluate("() => window.__dbg.maxScore()")
        check("Doc duoc cau hinh", bool(cfg), str(cfg))
        check("Diem toi da = 3 vach x so ngay", maxp == cfg["days"] * 3, str(maxp))
        check("May oxy CO ton nuoc (day noi co nguon)", cfg["oxyWater"] > 0,
              str(cfg["oxyWater"]))
        check("Nhan MO PHONG hien ra", pg.is_visible("#sim"))
        check("0 loi trang", not errs, str(errs[:1])[:100])

        # ---------- [2] Cân bằng: KHÔNG có tổ hợp nào giữ cả ba đứng yên ----------
        print("\n[2] Can bang — do bang chinh bo so cua game")
        P, D, G, OW = cfg["power"], cfg["drain"], cfg["gain"], cfg["oxyWater"]
        combos, allpos = [], []
        for w in range(P + 1):
            for a in range(P + 1 - w):
                o = P - w - a
                dw = -D["w"] - o * OW + w * G["w"]
                da = -D["a"] + a * G["a"]
                do = -D["o"] + o * G["o"]
                combos.append(((w, a, o), dw, da, do))
                if dw >= 0 and da >= 0 and do >= 0:
                    allpos.append((w, a, o))
        # ⚠️ DAY LA PHEP KIEM QUAN TRONG NHAT CUA CA BO. Co mot to hop "an toan
        #    tuyet doi" thi tre tim ra roi lap lai nam lan — het bai tap.
        check("KHONG to hop nao giu duoc CA BA vach khong tut",
              not allpos, "to hop an toan: " + str(allpos))
        # …nhung phai co it nhat mot to hop giu duoc HAI vach, khong thi vo vong.
        two_ok = [c[0] for c in combos if sum(1 for d in c[1:] if d >= 0) >= 2]
        check("Van co to hop giu duoc HAI vach (khong be tac)", len(two_ok) > 0,
              str(two_ok[:4]))
        check("Bo dat co the choi het 5 ngay (khong to hop nao lam chet ngay)",
              all(min(c[1:]) > -cfg["start"] for c in combos))
        ctx.close()

        # ---------- [3] Chia điện + dây nối oxy→nước ----------
        print("\n[3] Chia dien va day noi oxy -> nuoc")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        check("Tru dung 4 tt", pg.inner_text("#bal") == "36", pg.inner_text("#bal"))
        check("Chua chia thi KHONG chay duoc",
              pg.get_attribute("#run", "disabled") is not None)
        give(pg, "w", 1)
        check("Chia mot phan roi van chua chay duoc (con thua dien)",
              pg.get_attribute("#run", "disabled") is not None)
        give(pg, "w", 1); give(pg, "a", 2); give(pg, "o", 1)
        check("Chia HET dien thi moi chay duoc",
              pg.get_attribute("#run", "disabled") is None)
        check("Het dien thi nut + bi vo hieu",
              pg.locator('.rc-btn[data-d="1"]:not([disabled])').count() == 0)

        before = pg.evaluate("() => window.__dbg.levels()")
        pg.click("#run"); pg.wait_for_timeout(450)
        after = pg.evaluate("() => window.__dbg.levels()")
        # 2/2/1: nuoc = -12 - 1*5 + 2*8 = -1 · khi = -14 + 2*9 = +4 · oxy = -13 + 9 = -4
        exp_w = -D["w"] - 1 * OW + 2 * G["w"]
        check("Nuoc doi dung theo cong thuc (DA tru phan may oxy dung)",
              round(after["w"] - before["w"]) == exp_w,
              f'{round(after["w"]-before["w"])} vs {exp_w}')
        check("Khi sach doi dung", round(after["a"] - before["a"]) == -D["a"] + 2 * G["a"])
        check("Oxy doi dung", round(after["o"] - before["o"]) == -D["o"] + G["o"])
        check("Nhat ky noi ro may oxy da dung bao nhieu nuoc",
              str(OW) in pg.inner_text("#log"), pg.inner_text("#log")[:90])
        check("Hop giai thich CAI VONG hien ra", pg.is_visible("#why"))
        check("Cong diem = so vach an toan", pg.inner_text("#hb-score") == "3",
              pg.inner_text("#hb-score"))
        check("Chay roi thi bang chia dien bien mat",
              pg.locator(".rc-row").count() == 0)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [4] Dồn hết cho oxy → nước tụt mạnh ----------
        print("\n[4] Don HET dien cho oxy -> nuoc tut manh (day noi co that)")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        b = pg.evaluate("() => window.__dbg.levels()")
        spend_all(pg, 0, 0, P)
        pg.click("#run"); pg.wait_for_timeout(450)
        a2 = pg.evaluate("() => window.__dbg.levels()")
        exp = -D["w"] - P * OW
        check("Don het cho oxy: nuoc tut dung %d" % exp,
              round(a2["w"] - b["w"]) == exp, str(round(a2["w"] - b["w"])))
        check("…va oxy thi len", a2["o"] > b["o"], f'{b["o"]} -> {a2["o"]}')
        check("…con khi sach thi tut", a2["a"] < b["a"], f'{b["a"]} -> {a2["a"]}')
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [5] Một vạch cạn → lượt dừng ----------
        print("\n[5] Mot vach cham 0 -> luot DUNG, noi dung vach nao")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        # Gieo nuoc gan cạn roi don het cho oxy — chac chan nuoc ve 0
        pg.evaluate("() => window.__dbg.setLevels(10, 80, 80)")
        spend_all(pg, 0, 0, P)
        pg.click("#run"); pg.wait_for_timeout(450)
        check("Ghi nhan vach NUOC da can",
              pg.evaluate("() => window.__dbg.dead()") == "w",
              str(pg.evaluate("() => window.__dbg.dead()")))
        check("Nut cuoi doi thanh 'xem ket qua'",
              "kết quả" in pg.inner_text("#next").lower(), pg.inner_text("#next"))
        pg.click("#next"); pg.wait_for_timeout(400)
        check("Man ket hien ra", pg.is_visible("#ov-over.show"))
        over = pg.inner_text("#over-p")
        check("Man ket goi DUNG TEN vach da can", "ước" in over, over[:80])
        check("Tieu de doi thanh 'so tan'", "tán" in pg.inner_text("#over-h").lower(),
              pg.inner_text("#over-h"))
        check("Van duoc thuong phan da lam duoc (khong phat ve 0)",
              int(pg.inner_text("#r-mtr")) > 0, pg.inner_text("#r-mtr"))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [6] Chơi trọn 5 ngày ----------
        print("\n[6] Choi tron 5 ngay")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        # Luan phien de giu ca ba song — day chinh la loi giai ma game doi hoi
        plan = [(2, 2, 1), (3, 1, 1), (2, 1, 2), (2, 2, 1), (3, 1, 1)]
        for i, (w, a, o) in enumerate(plan):
            spend_all(pg, w, a, o)
            pg.click("#run"); pg.wait_for_timeout(420)
            pg.click("#next"); pg.wait_for_timeout(320)
        pg.wait_for_selector("#ov-over.show", timeout=6000)
        check("Song het 5 ngay (khong so tan)",
              pg.evaluate("() => window.__dbg.dead()") == "", "")
        sc = int(pg.inner_text("#r-score"))
        check("Diem nam trong khoang hop le", 0 < sc <= maxp, f"{sc}/{maxp}")
        check("O 'tren tong so' dung", pg.inner_text("#r-max") == str(maxp))
        check("Thuong tt = diem", pg.inner_text("#r-mtr") == str(sc))
        check("Vi = 36 + thuong", pg.inner_text("#bal") == str(36 + sc), pg.inner_text("#bal"))
        check("Ky luc moi", pg.inner_text("#r-best") == str(sc))
        check("Co duong sang bai doc",
              "library.html?a=" in (pg.get_attribute("#read-link", "href") or ""))
        check("0 loi trang ca luot", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [7] Thiếu tiền + EN + điện thoại ----------
        print("\n[7] Thieu tien · tieng Anh · dien thoai")
        ctx, pg, errs = open_page(br, tt=1)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        check("Hien man 'chua du tt'", pg.is_visible("#ov-need.show"))
        check("KHONG tru tien", pg.inner_text("#bal") == "1")
        ctx.close()

        ctx, pg, errs = open_page(br, lang="en")
        check("Tieu de EN", "Recycling Station" in pg.title(), pg.title())
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        check("Ten he thong dich sang EN",
              not re.search(r"[ăâđêôơư]", pg.inner_text("#rows")),
              pg.inner_text("#rows")[:60].replace("\n", " "))
        check("Nhan MO PHONG dich sang EN",
              not re.search(r"[ăâđêôơư]", pg.inner_text("#sim")), pg.inner_text("#sim"))
        ctx.close()

        ctx, pg, errs = open_page(br, w=390, h=844)
        check("KHONG nhac xoay ngang", not pg.is_visible(".ov.rot.show"))
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        d = pg.evaluate("""() => ({
          ovf: document.documentElement.scrollWidth - innerWidth,
          btns: [...document.querySelectorAll('.rc-btn')]
                  .every(e => e.getBoundingClientRect().height >= 47.5),
          gauges: document.querySelectorAll('.rc-g').length,
          seen: [...document.querySelectorAll('.rc-g')].every(e => {
            const r = e.getBoundingClientRect();
            return r.top >= 0 && r.bottom <= innerHeight;
          })
        })""")
        check("Khong tran ngang", d["ovf"] <= 1, f"{d['ovf']}px")
        check("Nut +/- >=48px", d["btns"])
        check("Du 3 vach", d["gauges"] == 3, str(d["gauges"]))
        # Ba vach phai luon NHIN THAY DUOC: chung nam NGOAI vung cuon, vi cuon mat
        # chung di thi tre chia dien ma khong biet minh dang chia cho cai gi.
        check("Ba vach luon trong khung nhin (khong bi cuon mat)", d["seen"])
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
