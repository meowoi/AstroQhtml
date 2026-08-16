# -*- coding: utf-8 -*-
"""
play_comms.py — CHƠI THẬT Trạm Liên Lạc (ARCADE-08) trên Chromium.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/play_comms.py

Khuôn của game này là XẾP THỨ TỰ rồi PHÁT ĐI KHÔNG SỬA ĐƯỢC, nên bộ đo hỏi những
câu mà `play_survival.py` (khuôn chọn thẻ) không hỏi tới:

  · Chấm theo ĐOẠN ĐẦU ĐÚNG (prefix), không phải "đếm ô đặt đúng chỗ". Sai ở lệnh
    thứ hai của dãy 4 lệnh phải cho 1 điểm — kể cả khi ba lệnh sau tình cờ đúng chỗ.
  · Phát rồi thì KHÔNG sửa được: kho lệnh biến mất, ô trong dãy hoá `disabled`.
  · Nhịp chờ tín hiệu có THẬT SỰ chạy không, và trong lúc chờ có chặn bấm không.
  · Ba trạng thái ô sau khi phát phải KHÁC nhau: đúng · lệnh sai đầu tiên · phần
    không bao giờ chạy tới. Gộp hai cái sau là nói với trẻ nó sai 4 lệnh trong khi
    thực ra nó sai đúng 1.

⚠️ Thứ tự ĐÚNG là chỉ số 0,1,2,… của mảng `seq`; kho lệnh hiện ra theo thứ tự XÁO
   (tất định). Bộ đo bấm theo `data-ci` nên không phụ thuộc chỗ nút nằm.
"""
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-comms.html"

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
                       "localStorage.removeItem('astroq-comms-best');" % (lang, tt))
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#ov-start.show", timeout=8000)
    return ctx, pg, errs


def queue(pg, seq):
    """Xep day theo danh sach chi so lenh."""
    for ci in seq:
        pg.locator('#pool .dg-card[data-ci="%d"]' % ci).click()
        pg.wait_for_timeout(70)


def transmit(pg):
    """Bam phat roi CHO het ba nhip. Cho theo tin hieu that (`busy`), khong ngu
    mot khoang co dinh — ngu co dinh la phep do phu thuoc toc do may."""
    pg.click("#send")
    pg.wait_for_function("() => window.__dbg.busy() === false", timeout=15000)
    pg.wait_for_timeout(150)


def main():
    print(f"=== Tram Lien Lac (ARCADE-08) @ {URL} ===")
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ---------- [1] Dữ liệu ----------
        print("\n[1] Du lieu 4 nhiem vu")
        ctx, pg, errs = open_page(br)
        rounds = pg.evaluate("() => window.__dbg.rounds()")
        maxp = pg.evaluate("() => window.__dbg.maxScore()")
        check("Doc duoc du lieu tu trang", len(rounds) >= 3, f"{len(rounds)} nhiem vu")
        check("Moi nhiem vu co it nhat 4 lenh",
              all(r["n"] >= 4 for r in rounds), str([r["n"] for r in rounds]))
        check("Diem toi da = tong so lenh",
              maxp == sum(r["n"] for r in rounds), str(maxp))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [2] Xếp đúng cả dãy ----------
        print("\n[2] Xep dung ca day")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        check("Tru dung 4 tt", pg.inner_text("#bal") == "36", pg.inner_text("#bal"))
        n0 = rounds[0]["n"]
        check("Chua xep gi -> nut phat bi vo hieu",
              pg.get_attribute("#send", "disabled") is not None)
        check("Dai lenh rong co noi ro phai lam gi",
              pg.locator(".cm-empty").count() == 1)
        # Kho lenh hien theo thu tu XAO — day la thu lam bai tap co that
        pool = pg.evaluate("() => window.__dbg.poolOrder()")
        check("Kho lenh hien theo thu tu XAO (khong phai 0,1,2,…)",
              pool != sorted(pool), str(pool))
        queue(pg, list(range(n0)))
        check("Xep du thi nut phat mo ra",
              pg.get_attribute("#send", "disabled") is None)
        check("Day hien dung so lenh", pg.locator(".cm-slot").count() == n0,
              str(pg.locator(".cm-slot").count()))
        transmit(pg)
        check("Ca day dung -> diem = so lenh", pg.inner_text("#hb-score") == str(n0),
              pg.inner_text("#hb-score"))
        check("Moi o deu xanh", pg.locator(".cm-slot.ok").count() == n0,
              str(pg.locator(".cm-slot.ok").count()))
        check("0 o do", pg.locator(".cm-slot.bad").count() == 0)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [3] Chấm theo ĐOẠN ĐẦU, không theo từng ô ----------
        print("\n[3] Cham theo DOAN DAU DUNG (prefix), khong theo tung o")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        n0 = rounds[0]["n"]
        # Day: 0, 2, 1, 3… → dung o vi tri 0, sai tu vi tri 1.
        # ⚠️ Cho nay la ca ly do phep kiem ton tai: neu cham RO'I tung o thi day nay
        #    duoc 2 diem (vi tri 0 va vi tri 3 tinh co dung cho). Cham theo doan dau
        #    thi dung 1 — va do moi la thu xay ra ngoai doi: mot day lenh gui len tau
        #    chay TUAN TU, lenh sai dau tien la cho moi thu dung lai.
        seq = [0, 2, 1] + list(range(3, n0))
        queue(pg, seq)
        transmit(pg)
        check("Sai o lenh thu 2 -> chi duoc 1 diem", pg.inner_text("#hb-score") == "1",
              pg.inner_text("#hb-score"))
        check("Dung 1 o xanh", pg.locator(".cm-slot.ok").count() == 1,
              str(pg.locator(".cm-slot.ok").count()))
        check("Dung 1 o do (chi lenh SAI DAU TIEN)",
              pg.locator(".cm-slot.bad").count() == 1,
              str(pg.locator(".cm-slot.bad").count()))
        check("Phan con lai la 'khong chay toi', KHONG phai 'sai'",
              pg.locator(".cm-slot.skip").count() == n0 - 2,
              str(pg.locator(".cm-slot.skip").count()))
        why = pg.inner_text("#why")
        check("Noi ro le ra lenh so may phai la gi", "2" in why and len(why) > 40, why[:80])
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [4] Phát rồi KHÔNG sửa được ----------
        print("\n[4] Phat roi thi KHONG sua duoc nua")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        n0 = rounds[0]["n"]
        queue(pg, list(range(n0)))
        # Truoc khi phat: bo mot lenh ra duoc
        pg.locator(".cm-slot").first.click(); pg.wait_for_timeout(150)
        check("TRUOC khi phat: bam vao day thi bo lenh do ra",
              pg.locator(".cm-slot").count() == n0 - 1,
              str(pg.locator(".cm-slot").count()))
        queue(pg, [0])          # xep lai
        transmit(pg)
        check("SAU khi phat: moi o trong day bi vo hieu",
              pg.locator(".cm-slot:not([disabled])").count() == 0,
              str(pg.locator(".cm-slot:not([disabled])").count()))
        check("SAU khi phat: kho lenh bien mat", pg.locator("#pool .dg-card").count() == 0)
        check("SAU khi phat: nut phat bien mat", not pg.is_visible("#send"))
        check("Co cau noi ro khong goi lai duoc",
              "gọi lại" in pg.inner_text("#note").lower(), pg.inner_text("#note"))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [5] Nhịp chờ tín hiệu ----------
        print("\n[5] Nhip cho tin hieu — bai hoc, khong phai hieu ung")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        queue(pg, list(range(rounds[0]["n"])))
        pg.click("#send")
        pg.wait_for_timeout(200)
        check("Dang cho: hop tin hieu hien ra", pg.is_visible("#wait"))
        check("Dang cho: noi ro 7 phut", "7" in pg.inner_text("#wait-txt"),
              pg.inner_text("#wait-txt"))
        check("Dang cho: KHONG cho di tiep (chan bam)", not pg.is_visible("#next"))
        check("Dang cho: chua cong diem", pg.inner_text("#hb-score") == "0",
              pg.inner_text("#hb-score"))
        pg.wait_for_function("() => window.__dbg.busy() === false", timeout=15000)
        pg.wait_for_timeout(150)
        check("Cho xong: hop tin hieu tat", not pg.is_visible("#wait"))
        check("Cho xong: moi di tiep duoc", pg.is_visible("#next"))
        check("Cho xong: da cong diem", pg.inner_text("#hb-score") != "0",
              pg.inner_text("#hb-score"))
        # Nhip cho phai DAI THAT — rut ve 0 la mat bai hoc cua ca game
        check("Tong nhip cho >= 1,5 giay", pg.evaluate("() => window.__dbg.waitMs()") >= 1500,
              str(pg.evaluate("() => window.__dbg.waitMs()")) + "ms")
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [6] Chơi trọn lượt + thưởng ----------
        print("\n[6] Choi tron luot hoan hao")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        for i, r in enumerate(rounds):
            queue(pg, list(range(r["n"])))
            transmit(pg)
            pg.click("#next")
            pg.wait_for_timeout(260)
        pg.wait_for_selector("#ov-over.show", timeout=6000)
        check("Diem = toi da", pg.inner_text("#r-score") == str(maxp), pg.inner_text("#r-score"))
        check("O 'tren tong so' dung", pg.inner_text("#r-max") == str(maxp))
        check("Thuong tt = so lenh dung", pg.inner_text("#r-mtr") == str(maxp))
        check("Vi = 36 + thuong", pg.inner_text("#bal") == str(36 + maxp), pg.inner_text("#bal"))
        check("Ky luc moi", pg.inner_text("#r-best") == str(maxp))
        check("Co duong sang bai doc",
              "library.html?a=" in (pg.get_attribute("#read-link", "href") or ""))
        check("0 loi trang ca luot", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [7] Thiếu tiền ----------
        print("\n[7] Thieu Thien thach tim")
        ctx, pg, errs = open_page(br, tt=2)
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        check("Hien man 'chua du tt'", pg.is_visible("#ov-need.show"))
        check("KHONG tru tien", pg.inner_text("#bal") == "2", pg.inner_text("#bal"))
        check("Noi ro can 4", "4" in pg.inner_text("#need-body"), pg.inner_text("#need-body")[:60])
        ctx.close()

        # ---------- [8] Tiếng Anh + điện thoại ----------
        print("\n[8] Tieng Anh + dien thoai 390x844")
        ctx, pg, errs = open_page(br, lang="en")
        check("Tieu de EN", "Comms Station" in pg.title(), pg.title())
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        check("De bai dich sang EN",
              not re.search(r"[ăâđêôơư]", pg.inner_text("#brief")),
              pg.inner_text("#brief")[:50])
        check("Kho lenh dich sang EN",
              not re.search(r"[ăâđêôơư]", pg.inner_text("#pool")),
              pg.inner_text("#pool")[:50])
        ctx.close()

        ctx, pg, errs = open_page(br, w=390, h=844)
        check("KHONG nhac xoay ngang", not pg.is_visible(".ov.rot.show"))
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        d = pg.evaluate("""() => ({
          ovf: document.documentElement.scrollWidth - innerWidth,
          pool: [...document.querySelectorAll('#pool .dg-card')]
                  .every(e => e.getBoundingClientRect().height >= 47.5),
          send: document.getElementById('send').getBoundingClientRect().height
        })""")
        check("Khong tran ngang", d["ovf"] <= 1, f"{d['ovf']}px")
        check("Moi lenh trong kho >=48px", d["pool"])
        check("Nut phat >=48px", d["send"] >= 47.5, f"{d['send']:.0f}px")
        queue(pg, list(range(rounds[0]["n"])))
        transmit(pg)
        seen = pg.evaluate("""() => {
          const b=document.querySelector('.dg-body'), w=document.getElementById('why');
          const rb=b.getBoundingClientRect(), rw=w.getBoundingClientRect();
          return rw.top < rb.bottom - 4 && rw.bottom > rb.top + 4;
        }""")
        check("Hop giai thich TU CUON VAO TAM NHIN tren man doc", seen)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
