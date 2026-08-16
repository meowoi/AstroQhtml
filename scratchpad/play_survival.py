# -*- coding: utf-8 -*-
"""
play_survival.py — CHƠI THẬT Trạm Sinh Tồn (ARCADE-07) trên Chromium.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/play_survival.py

Đây là game LỚP QUYẾT ĐỊNH đầu tiên của dự án, nên bộ đo này hỏi những câu mà 6 bộ
đo game cũ không hỏi tới:

  · Nội dung có ĐÚNG SỐ không — mỗi tình huống phải có ít nhất `need` lựa chọn đúng,
    không thì tình huống đó bất khả thi và không phép kiểm nào khác nói ra.
  · Chốt xong thì hộp "vì sao" có NHÌN THẤY ĐƯỢC không (không chỉ "có trong DOM").
    Trên điện thoại dọc nó từng nằm hẳn dưới mép sân — đúng thứ game này tồn tại
    để dạy mà trẻ không đọc được.
  · Chơi hoàn hảo có cho ĐÚNG số điểm tối đa không, và ví có cộng đúng bấy nhiêu.
  · Trừ phí ĐÚNG MỘT LẦN (bẫy Enter/Space bấm hai lần đã trả giá ở ARCADE-01).
  · Thiếu tiền thì KHÔNG trừ gì cả.

⚠️ Bộ đo ĐỌC DỮ LIỆU TÌNH HUỐNG TỪ CHÍNH TRANG (`__dbg`), không chép lại đáp án ở
   đây: chép là hai nơi giữ một sự thật, và bên lệch sẽ là bộ đo báo hỏng oan.
"""
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-survival.html"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def seed(lang="vi", tt=40):
    return ("localStorage.setItem('astroq-lang','%s');"
            "localStorage.setItem('astroq-asteroids','%d');"
            "localStorage.removeItem('astroq-survival-best');" % (lang, tt))


def open_page(br, lang="vi", tt=40, w=1440, h=900):
    ctx = br.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    pg.add_init_script(seed(lang, tt))
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#ov-start.show", timeout=8000)
    return ctx, pg, errs


def rounds_of(pg):
    """Dữ liệu 4 tình huống, đọc THẲNG từ trang."""
    return pg.evaluate("() => window.__dbg.rounds()")


def play_perfect(pg, rounds):
    """Chơi hết lượt, mỗi tình huống chọn ĐÚNG hết."""
    for r_i, r in enumerate(rounds):
        right = [i for i, it in enumerate(r["items"]) if it["ok"]][: r["need"]]
        for i in right:
            pg.locator(".dg-card").nth(i).click()
            pg.wait_for_timeout(60)
        pg.click("#confirm")
        pg.wait_for_timeout(280)
        if r_i < len(rounds) - 1:
            pg.click("#next")
            pg.wait_for_timeout(220)
    pg.click("#next")            # nút cuối = "Xem kết quả"
    pg.wait_for_selector("#ov-over.show", timeout=6000)


def main():
    print(f"=== Tram Sinh Ton (ARCADE-07) @ {URL} ===")
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ---------- [1] Nội dung: có chơi được không ----------
        print("\n[1] Du lieu 4 tinh huong")
        ctx, pg, errs = open_page(br)
        rounds = rounds_of(pg)
        check("Doc duoc du lieu tinh huong tu trang", len(rounds) > 0, f"{len(rounds)} tinh huong")
        check("Co it nhat 3 tinh huong", len(rounds) >= 3, str(len(rounds)))
        for i, r in enumerate(rounds, 1):
            n_ok = sum(1 for it in r["items"] if it["ok"])
            # ⚠️ Thieu dap an dung thi tinh huong do BAT KHA THI — tre chon du so
            #    ma van khong bao gio dat diem toi da, va khong gi bao loi.
            check(f"Tinh huong {i}: du dap an dung ({r['need']} can)",
                  n_ok >= r["need"], f"{n_ok} dung / can {r['need']}")
            check(f"Tinh huong {i}: co ca moi nhu (khong phai cai nao cung dung)",
                  n_ok < len(r["items"]), f"{n_ok}/{len(r['items'])}")
            # Moi the phai co loi giai thich — ke ca the SAI. Bo trong mot cai la
            # tre chon vao do roi khong duoc giai thich gi, dung o cho no can nhat.
            miss = [j for j, it in enumerate(r["items"]) if not it["why"]]
            check(f"Tinh huong {i}: MOI the deu co loi giai thich", not miss, str(miss))

        maxp = pg.evaluate("() => window.__dbg.maxScore()")
        check("Diem toi da = tong so dap an dung",
              maxp == sum(sum(1 for it in r["items"] if it["ok"]) for r in rounds), str(maxp))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [2] Vòng đời một lượt ----------
        print("\n[2] Vong doi mot luot: phi · choi · thuong")
        ctx, pg, errs = open_page(br, tt=40)
        check("Chua bat dau thi vi nguyen 40", pg.inner_text("#bal") == "40", pg.inner_text("#bal"))
        pg.click("#start-btn")
        pg.wait_for_timeout(400)
        check("Bat dau -> tru dung 3 tt MOT LAN", pg.inner_text("#bal") == "37",
              pg.inner_text("#bal"))
        check("Man brief da dong", not pg.is_visible("#ov-start.show"))
        check("Nut chot dang bi vo hieu (chua chon gi)",
              pg.get_attribute("#confirm", "disabled") is not None)

        # Bam "Bat dau" lan nua trong luc dang choi KHONG duoc tru them.
        pg.evaluate("() => window.__dbg.start()")
        pg.wait_for_timeout(200)
        check("Goi start() lan hai trong luc dang choi KHONG tru them",
              pg.inner_text("#bal") == "37", pg.inner_text("#bal"))

        rounds = rounds_of(pg)
        play_perfect(pg, rounds)
        check("Choi hoan hao -> diem = toi da",
              pg.inner_text("#r-score") == str(maxp), pg.inner_text("#r-score"))
        check("O 'tren tong so' dung bang diem toi da",
              pg.inner_text("#r-max") == str(maxp), pg.inner_text("#r-max"))
        check("Thuong tt = so cau dung",
              pg.inner_text("#r-mtr") == str(maxp), pg.inner_text("#r-mtr"))
        check("Vi = 37 + thuong", pg.inner_text("#bal") == str(37 + maxp), pg.inner_text("#bal"))
        check("Ky luc moi = diem", pg.inner_text("#r-best") == str(maxp),
              pg.inner_text("#r-best"))
        paid = pg.inner_text("#paid")
        check("Dong 'da cong n tt' co hien", str(maxp) in paid, paid[:60])
        check("Co duong sang bai doc (noi Khu Huan Luyen voi Tram Tri Thuc)",
              pg.is_visible("#read-link")
              and "library.html?a=" in (pg.get_attribute("#read-link", "href") or ""),
              str(pg.get_attribute("#read-link", "href")))
        check("0 loi trang sau ca luot", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [3] Chọn sai vẫn được giải thích, không ai thua ----------
        print("\n[3] Chon sai: van duoc giai thich, khong co man THUA")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(300)
        rounds = rounds_of(pg)
        wrong = [i for i, it in enumerate(rounds[0]["items"]) if not it["ok"]][: rounds[0]["need"]]
        for i in wrong:
            pg.locator(".dg-card").nth(i).click(); pg.wait_for_timeout(60)
        pg.click("#confirm"); pg.wait_for_timeout(350)
        check("Chon sai het -> diem van 0", pg.inner_text("#hb-score") == "0",
              pg.inner_text("#hb-score"))
        check("Hop 'vi sao' HIEN RA THAT", pg.is_visible("#why"))
        # ⚠️ Do bang khung bao thuc te chu khong bang `hidden`: tren dien thoai hop
        #    nay tung nam han duoi mep san (do duoc, 16/08) — co trong DOM ma tre
        #    khong doc duoc thi coi nhu khong co.
        seen = pg.evaluate("""() => {
          const b=document.querySelector('.dg-body'), w=document.getElementById('why');
          const rb=b.getBoundingClientRect(), rw=w.getBoundingClientRect();
          return rw.top < rb.bottom - 4 && rw.bottom > rb.top + 4;
        }""")
        check("Hop 'vi sao' nam TRONG tam nhin, khong bi day xuong duoi mep", seen)
        check("Van co the di tiep (khong co man THUA)", pg.is_visible("#next"))
        check("Khong con nut 'chot' sau khi da chot", not pg.is_visible("#confirm"))
        check("The da chon SAI duoc danh dau rieng", pg.locator(".dg-card.no").count() > 0,
              str(pg.locator(".dg-card.no").count()))
        check("The DUNG luon hien ra du tre khong chon",
              pg.locator(".dg-card.ok").count() == rounds[0]["need"],
              str(pg.locator(".dg-card.ok").count()))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [4] Không chọn quá số cho phép ----------
        print("\n[4] Chon qua so cho phep: bo cai chon som nhat, khong chan im lang")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn"); pg.wait_for_timeout(300)
        need = rounds_of(pg)[0]["need"]
        for i in range(need + 1):
            pg.locator(".dg-card").nth(i).click(); pg.wait_for_timeout(60)
        check(f"Bam {need+1} the -> van chi giu {need}",
              pg.locator(".dg-card.picked").count() == need,
              str(pg.locator(".dg-card.picked").count()))
        check("The bam SAU CUNG chac chan dang duoc chon",
              "picked" in (pg.locator(".dg-card").nth(need).get_attribute("class") or ""))
        check("Nut chot mo ra khi du so", pg.get_attribute("#confirm", "disabled") is None)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [5] Thiếu tiền ----------
        print("\n[5] Thieu Thien thach tim")
        ctx, pg, errs = open_page(br, tt=1)
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        check("Hien man 'chua du tt'", pg.is_visible("#ov-need.show"))
        check("KHONG tru tien", pg.inner_text("#bal") == "1", pg.inner_text("#bal"))
        body = pg.inner_text("#need-body")
        check("Noi ro can bao nhieu / dang co bao nhieu",
              "3" in body and "1" in body, body[:70])
        check("Co duong di toi Quiz", pg.is_visible("#need-quiz"))
        ctx.close()

        # ---------- [6] Tiếng Anh ----------
        print("\n[6] Ban tieng Anh")
        ctx, pg, errs = open_page(br, lang="en")
        check("Tieu de trang doi sang EN", "Survival Station" in pg.title(), pg.title())
        check("Nhan game o header dich", "SURVIVAL" in pg.inner_text("#gtag").upper(),
              pg.inner_text("#gtag"))
        pg.click("#start-btn"); pg.wait_for_timeout(350)
        brief = pg.inner_text("#brief")
        check("De bai dich sang EN, khong con dau tieng Viet",
              not re.search(r"[ăâđêôơưÁÀẢÃẠăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ]",
                            brief),
              brief[:60])
        # Doi ngon ngu GIUA luc dang choi: de bai va nut phai dich theo, khong mat
        # trang thai da chon (bai hoc `paintPaid` cua ARCADE-01).
        pg.locator(".dg-card").nth(0).click(); pg.wait_for_timeout(80)
        pg.click('.lang-switch button[data-lang="vi"]'); pg.wait_for_timeout(350)
        check("Doi sang VI giua luc choi: de bai dich theo",
              re.search(r"[ăâđêôơư]", pg.inner_text("#brief")) is not None,
              pg.inner_text("#brief")[:50])
        check("Doi ngon ngu KHONG lam mat the dang chon",
              pg.locator(".dg-card.picked").count() == 1,
              str(pg.locator(".dg-card.picked").count()))
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        # ---------- [7] Điện thoại dọc ----------
        print("\n[7] Dien thoai 390x844")
        ctx, pg, errs = open_page(br, w=390, h=844)
        check("KHONG nhac xoay ngang (game chu, xoay ngang lam te hon)",
              not pg.is_visible(".ov.rot.show"))
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        d = pg.evaluate("""() => ({
          ovf: document.documentElement.scrollWidth - innerWidth,
          cards: [...document.querySelectorAll('.dg-card')]
                   .every(e => e.getBoundingClientRect().height >= 47.5),
          btn: document.getElementById('confirm').getBoundingClientRect().height
        })""")
        check("Khong tran ngang", d["ovf"] <= 1, f"{d['ovf']}px")
        check("Moi the lua chon >=48px (WCAG 2.5.5 + bien an toan)", d["cards"])
        check("Nut chot >=48px", d["btn"] >= 47.5, f"{d['btn']:.0f}px")
        rounds = rounds_of(pg)
        right = [i for i, it in enumerate(rounds[0]["items"]) if it["ok"]][: rounds[0]["need"]]
        for i in right:
            pg.locator(".dg-card").nth(i).click(); pg.wait_for_timeout(60)
        pg.click("#confirm"); pg.wait_for_timeout(400)
        seen = pg.evaluate("""() => {
          const b=document.querySelector('.dg-body'), w=document.getElementById('why');
          const rb=b.getBoundingClientRect(), rw=w.getBoundingClientRect();
          return rw.top < rb.bottom - 4 && rw.bottom > rb.top + 4;
        }""")
        check("Hop 'vi sao' TU CUON VAO TAM NHIN tren man doc", seen)
        check("0 loi trang", not errs, str(errs[:1])[:100])
        ctx.close()

        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
