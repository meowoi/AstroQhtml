# -*- coding: utf-8 -*-
"""
play_units.py — CHƠI THẬT Trạm Đối Chiếu (ARCADE-10) trên Chromium.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/play_units.py

Khuôn SOI LỖI TRONG BẢNG, nên bộ đo hỏi những câu ba game lớp B kia không có:

  · ⚠️⚠️ **KHÔNG CHIẾN LƯỢC MÙ NÀO THẮNG ĐƯỢC.** Cả bài tập chỉ tồn tại nếu
    "đánh dấu hết" và "không đánh dấu gì" đều hỏng — nếu một trong hai ăn được
    phần lớn số bảng thì trẻ tìm ra rồi lặp lại, và game hết ý nghĩa. Mục [2]
    duyệt HẾT năm bảng bằng chính dữ liệu của trang và đo cả hai chiến lược đó.
  · Mồi nhử ("khác đơn vị nhưng CÙNG một lượng") có thật, ở nhiều bảng — không
    có nó thì game tụt xuống thành "quét xem hai nhãn đơn vị có khác chữ nhau".
  · Có ít nhất một bảng KHÔNG có hàng sai nào: bảng nào cũng có lỗi thì trẻ học
    được một quy luật NGOÀI bài học và thôi phải nghĩ.
  · Chấm theo TẬP: bỏ sót một hàng thì cả bảng không tính, y như phát một dãy
    lệnh sai ở ARCADE-08 — chấm rời từng hàng là thưởng cho việc không làm gì.
  · Mọi hàng đều được giải thích, kể cả hàng đúng (bài học của ARCADE-07).
"""
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-units.html"

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
                       "localStorage.removeItem('astroq-units-best');" % (lang, tt))
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#ov-start.show", timeout=8000)
    return ctx, pg, errs


def flag(pg, i):
    pg.locator('.uc-row[data-i="%d"]' % i).click()
    pg.wait_for_timeout(50)


def play_sheet(pg, marks):
    """Đánh dấu đúng tập `marks` rồi duyệt bảng."""
    for i in marks:
        flag(pg, i)
    pg.click("#ok")
    pg.wait_for_timeout(350)


def main():
    print(f"=== Tram Doi Chieu (ARCADE-10) @ {URL} ===")
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ---------- [1] Cấu hình ----------
        print("\n[1] Cau hinh")
        ctx, pg, errs = open_page(br)
        cfg = pg.evaluate("() => window.__dbg.cfg()")
        maxp = pg.evaluate("() => window.__dbg.maxScore()")
        check("Doc duoc cau hinh", bool(cfg), str(cfg))
        check("Diem toi da = so bang", maxp == cfg["sheets"], str(maxp))
        # Phi vao cua 4 tt ma mot luot hoan hao chi tra 5 tt thi choi gioi het muc
        # van gan nhu khong duoc gi — thuong phai lon hon han phi.
        check("Thuong mot luot hoan hao LON HON han phi vao cua",
              maxp * cfg["ttPerSheet"] >= cfg["cost"] * 3,
              f'{maxp * cfg["ttPerSheet"]} tt vs phi {cfg["cost"]}')
        check("Nhan MO PHONG hien ra", pg.is_visible("#sim"))
        check("0 loi trang", not errs, str(errs[:1])[:100])

        # ---------- [2] Bộ đề: không chiến lược mù nào thắng ----------
        print("\n[2] Bo de — do bang chinh du lieu cua trang")
        bads = pg.evaluate("() => window.__dbg.badCounts()")
        decoys = pg.evaluate("() => window.__dbg.decoys()")
        pg.click("#start-btn")
        pg.wait_for_timeout(300)
        rows = []
        for s in range(maxp):
            rows.append(pg.evaluate("() => window.__dbg.bad()"))
            if s < maxp - 1:
                pg.click("#ok"); pg.wait_for_timeout(250)
                pg.click("#next"); pg.wait_for_timeout(250)
        ctx.close()

        n_rows = [len(r) for r in rows]
        # "khong danh dau gi" chi dat o bang KHONG co hang sai nao
        blind_none = sum(1 for r in rows if not any(r))
        # "danh dau het" chi dat o bang ma MOI hang deu sai
        blind_all = sum(1 for r in rows if all(r))
        check("Bo de doc duoc du " + str(maxp) + " bang", len(rows) == maxp, str(n_rows))
        check("So hang sai khop giua hai duong doc", bads == [sum(r) for r in rows],
              f"{bads} vs {[sum(r) for r in rows]}")
        # ⚠️ HAI PHEP KIEM QUAN TRONG NHAT CUA CA BO.
        check("Chien luoc mu 'KHONG danh dau gi' thua phan lon", blind_none <= 1,
              f"dat {blind_none}/{maxp} bang")
        check("Chien luoc mu 'danh dau HET' thua phan lon", blind_all <= 1,
              f"dat {blind_all}/{maxp} bang")
        check("CO it nhat mot bang KHONG co hang sai nao", blind_none >= 1,
              "so bang sach: " + str(blind_none))
        check("Phan lon bang CO hang sai", sum(1 for r in rows if any(r)) >= maxp - 1,
              str(bads))
        check("Moi nhu co that va rai o nhieu bang",
              sum(decoys) >= 4 and sum(1 for d in decoys if d) >= 3, str(decoys))
        check("Bang nao cung du hang de phai doc", all(n >= 4 for n in n_rows), str(n_rows))

        # ---------- [3] Duyệt một bảng ĐÚNG ----------
        print("\n[3] Duyet dung mot bang")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn"); pg.wait_for_timeout(300)
        check("Tru dung 4 tt", pg.inner_text("#bal") == "36", pg.inner_text("#bal"))
        b0 = pg.evaluate("() => window.__dbg.bad()")
        play_sheet(pg, [i for i, x in enumerate(b0) if x])
        check("Duoc diem", pg.inner_text("#hb-score") == "1", pg.inner_text("#hb-score"))
        check("Cong tt dung", int(pg.inner_text("#hb-mtr")) == cfg["ttPerSheet"],
              pg.inner_text("#hb-mtr"))
        v = pg.inner_text("#verdict")
        check("Loi phan noi la duyet DUNG", "đúng" in v.lower(), v[:80])
        check("Hop phan hien ra", pg.is_visible("#verdict"))
        n_hit = pg.locator(".uc-row.hit").count()
        check("Hang bat dung duoc danh dau 'hit'", n_hit == sum(b0), str(n_hit))
        # Moi hang deu co loi giai thich — ke ca hang dung.
        n_why = pg.locator(".uc-why").count()
        check("MOI hang co loi giai thich", n_why == len(b0), f"{n_why}/{len(b0)}")
        check("Duyet roi thi khong doi danh dau duoc nua",
              pg.locator(".uc-row:not([disabled])").count() == 0)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [4] Bỏ sót một hàng ----------
        print("\n[4] Bo sot mot hang sai")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(300)
        b0 = pg.evaluate("() => window.__dbg.bad()")
        play_sheet(pg, [])          # khong danh dau gi
        check("KHONG duoc diem", pg.inner_text("#hb-score") == "0", pg.inner_text("#hb-score"))
        check("KHONG cong tt", pg.inner_text("#hb-mtr") == "0", pg.inner_text("#hb-mtr"))
        v = pg.inner_text("#verdict")
        check("Loi phan noi ro la BO SOT", "sót" in v.lower(), v[:90])
        check("Hang bo sot duoc danh dau 'miss'",
              pg.locator(".uc-row.miss").count() == sum(b0),
              str(pg.locator(".uc-row.miss").count()))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [5] Báo nhầm một mồi nhử ----------
        print("\n[5] Bao nham mot hang KHONG sai")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(300)
        b0 = pg.evaluate("() => window.__dbg.bad()")
        good = [i for i, x in enumerate(b0) if not x]
        play_sheet(pg, [i for i, x in enumerate(b0) if x] + [good[0]])
        check("KHONG duoc diem", pg.inner_text("#hb-score") == "0", pg.inner_text("#hb-score"))
        v = pg.inner_text("#verdict")
        check("Loi phan noi ro la BAO NHAM", "nhầm" in v.lower(), v[:90])
        check("Hang bao nham duoc danh dau 'wrong'",
              pg.locator(".uc-row.wrong").count() == 1)
        # Chinh cai hang bi bao nham phai giai thich VI SAO no khong sai.
        why = pg.locator('.uc-row.wrong .uc-why').inner_text()
        check("Giai thich vi sao hang do KHONG sai",
              ("cùng một lượng" in why.lower() or "quy đổi đúng" in why.lower()
               or "khớp" in why.lower()), why[:90])
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [6] Bảng sạch: dám nói "không có lỗi" ----------
        print("\n[6] Bang KHONG co hang sai nao")
        clean = [i for i, r in enumerate(rows) if not any(r)]
        check("Tim duoc bang sach trong bo de", bool(clean), str(clean))
        if clean:
            ctx, pg, errs = open_page(br)
            pg.click("#start-btn"); pg.wait_for_timeout(300)
            for _ in range(clean[0]):          # đi tới bảng sạch
                pg.click("#ok"); pg.wait_for_timeout(250)
                pg.click("#next"); pg.wait_for_timeout(250)
            check("Dang o dung bang sach",
                  not any(pg.evaluate("() => window.__dbg.bad()")))
            n_dec = pg.evaluate("() => window.__dbg.decoys()")[clean[0]]
            check("Bang sach VAN co moi nhu (khong phai bang tam thuong)",
                  n_dec >= 2, str(n_dec))
            before = int(pg.inner_text("#hb-score"))
            play_sheet(pg, [])
            check("Khong danh dau gi -> DAT",
                  int(pg.inner_text("#hb-score")) == before + 1)
            v = pg.inner_text("#verdict")
            check("Loi phan dung cau RIENG cho bang sach",
                  "không có" in v.lower() and "sót" not in v.lower(), v[:100])
            check("0 loi trang", not errs, str(errs[:1])[:100])
            ctx.close()

        # ---------- [7] Chơi trọn 5 bảng, hoàn hảo ----------
        print("\n[7] Choi tron " + str(maxp) + " bang, hoan hao")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn"); pg.wait_for_timeout(300)
        for s in range(maxp):
            b = pg.evaluate("() => window.__dbg.bad()")
            play_sheet(pg, [i for i, x in enumerate(b) if x])
            pg.click("#next"); pg.wait_for_timeout(320)
        pg.wait_for_selector("#ov-over.show", timeout=6000)
        check("Diem tuyet doi", pg.inner_text("#r-score") == str(maxp), pg.inner_text("#r-score"))
        check("O 'tren tong so' dung", pg.inner_text("#r-max") == str(maxp))
        check("Thuong tt = so bang x moc",
              pg.inner_text("#r-mtr") == str(maxp * cfg["ttPerSheet"]), pg.inner_text("#r-mtr"))
        check("Vi = 36 + thuong",
              pg.inner_text("#bal") == str(36 + maxp * cfg["ttPerSheet"]), pg.inner_text("#bal"))
        check("Ky luc moi", pg.inner_text("#r-best") == str(maxp))
        check("Co duong sang bai doc",
              "library.html?a=art-units-lost-a-spacecraft"
              in (pg.get_attribute("#read-link", "href") or ""))
        check("0 loi trang ca luot", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [8] Thiếu tiền · EN · điện thoại ----------
        print("\n[8] Thieu tien · tieng Anh · dien thoai")
        ctx, pg, errs = open_page(br, tt=1)
        pg.click("#start-btn"); pg.wait_for_timeout(300)
        check("Hien man 'chua du tt'", pg.is_visible("#ov-need.show"))
        check("KHONG tru tien", pg.inner_text("#bal") == "1")
        ctx.close()

        ctx, pg, errs = open_page(br, lang="en")
        check("Tieu de EN", "Cross-Check Station" in pg.title(), pg.title())
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        check("Ten dai luong dich sang EN",
              not re.search(r"[ăâđêôơư]", pg.inner_text("#rows")),
              pg.inner_text("#rows")[:60].replace("\n", " "))
        check("Loi dan dich sang EN",
              not re.search(r"[ăâđêôơư]", pg.inner_text("#brief")),
              pg.inner_text("#brief")[:60])
        b = pg.evaluate("() => window.__dbg.bad()")
        play_sheet(pg, [i for i, x in enumerate(b) if x])
        check("Loi giai thich cung dich sang EN",
              not re.search(r"[ăâđêôơư]", pg.inner_text("#rows")),
              pg.inner_text(".uc-why")[:70])
        ctx.close()

        ctx, pg, errs = open_page(br, w=390, h=844)
        check("KHONG nhac xoay ngang", not pg.is_visible(".ov.rot.show"))
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        d = pg.evaluate("""() => {
          const r = document.querySelector('.uc-row');
          const v = r.querySelectorAll('.uc-v');
          const a = v[0].getBoundingClientRect(), b = v[1].getBoundingClientRect();
          return {
            ovf: document.documentElement.scrollWidth - innerWidth,
            tall: [...document.querySelectorAll('.uc-row')]
                    .every(e => e.getBoundingClientRect().height >= 47.5),
            // Hai gia tri phai NAM CANH NHAU: ca bai tap la SO HAI BEN. Xep chong
            // doc la mat cho dua de so.
            side: Math.abs(a.top - b.top) < 4 && b.left > a.left,
            cut: [...document.querySelectorAll('.uc-nm,.uc-v')]
                    .some(e => e.scrollWidth > e.clientWidth + 1)
          };
        }""")
        check("Khong tran ngang", d["ovf"] <= 1, f"{d['ovf']}px")
        check("Vung cham moi hang >=48px", d["tall"])
        check("Hai cot gia tri van CANH NHAU tren dien thoai", d["side"])
        check("Khong chu nao bi cat", not d["cut"])
        # ⚠️ HAI CA, VA CHUNG DOI HAI CHO CUON KHAC NHAU. Duyet sach thi thu can
        #    doc la hop phan; phan sai thi thu can doc la CHINH HANG DO — cuon
        #    xuong day o ca thu hai la day dung cai hang can doc ra khoi tam mat.
        b = pg.evaluate("() => window.__dbg.bad()")
        play_sheet(pg, [i for i, x in enumerate(b) if x])
        seen = pg.evaluate("""() => {
          const w = document.querySelector('#verdict').getBoundingClientRect();
          const f = document.querySelector('.field').getBoundingClientRect();
          return w.top >= f.top - 1 && w.bottom <= f.bottom + 1;
        }""")
        check("Duyet sach: hop phan nam trong tam mat", seen)
        ctx.close()

        ctx, pg, errs = open_page(br, w=390, h=844)
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        for _ in range(2):                       # toi bang 3 (5 hang, 2 hang sai)
            pg.click("#ok"); pg.wait_for_timeout(250)
            pg.click("#next"); pg.wait_for_timeout(250)
        b = pg.evaluate("() => window.__dbg.bad()")
        play_sheet(pg, [])                       # bo sot het -> hang dau tien 'miss'
        seen = pg.evaluate("""() => {
          const m = document.querySelector('.uc-row.miss');
          const f = document.querySelector('.field').getBoundingClientRect();
          const r = m.getBoundingClientRect();
          return r.top >= f.top - 1 && r.top < f.bottom;
        }""")
        check("Phan sai: cuon toi DUNG hang do", seen)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
