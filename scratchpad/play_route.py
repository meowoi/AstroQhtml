# -*- coding: utf-8 -*-
"""
play_route.py — CHƠI THẬT Trạm Dẫn Tuyến (ARCADE-11) trên Chromium.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/play_route.py

Khuôn XOAY ĐOẠN DẪN CHO MỘT TUYẾN LIỀN MẠCH, nên bộ đo hỏi những câu bốn game
lớp quyết định kia không có:

  · ⚠️⚠️ **BÀN NÀO CŨNG PHẢI GIẢI ĐƯỢC.** Bàn sinh ra ngẫu nhiên, nên đây là câu
    hỏi đắt nhất của cả bộ: mục [2] gieo lại nhiều lượt × 5 bàn và đòi lời giải
    tồn tại ở TỪNG bàn. Một bàn vô nghiệm lọt ra tay trẻ là nó ngồi xoay mãi.
  · ⚠️⚠️ **KHÔNG Ô NÀO ĐƯỢC ĐÚNG SẴN.** Ô đúng từ đầu là ô trẻ không hiểu vì sao
    mình không phải làm gì với nó — và với đoạn THẲNG thì lệch 2 nhịp = không
    lệch, nên phép kiểm này bắt đúng loại lỗi mà đọc mã rất khó thấy.
  · ⚠️⚠️ **THIẾT BỊ SAI PHẢI ĐI TỚI ĐƯỢC.** Nếu không có đường nào dẫn tới nó thì
    cổng kiến thức của bàn 4 là đồ trang trí: trẻ không thể chọn sai, nên nó
    không phải chọn. Bản đầu của game đúng như vậy và mục [2] bắt được.
  · Không có ngã tư (4 miệng): ngã tư đối xứng hoàn toàn nên xoay kiểu gì cũng
    "đúng" — một ô không có việc gì để làm mà vẫn chiếm chỗ.
  · Bàn KHÔNG tự thắng lúc mở ra, và nút Cấp điện TẮT khi tuyến chưa liền.
  · Chơi được bằng BÀN PHÍM (lưới nút + mũi tên + Enter) — `docs/decisions/002`
    đã bác một khuôn nối-dây vì đúng lý do này, nên nó phải được đo.
  · Bàn chơi KHÔNG bị tràn/cắt ở cả bốn khổ màn: cỡ bàn do JS đo (`fitBoard`),
    và `aspect-ratio` một mình từng cho sân **1086×2px** ở lớp game này.
"""
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-route.html"

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
                       "localStorage.removeItem('astroq-route-best');" % (lang, tt))
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#ov-start.show", timeout=8000)
    return ctx, pg, errs


def bits(m):
    return bin(m & 15).count("1")


def main():
    print(f"=== Tram Dan Tuyen (ARCADE-11) @ {URL} ===")
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ══════════ [1] Cấu hình ══════════
        print("\n[1] Cau hinh")
        ctx, pg, errs = open_page(br)
        cfg = pg.evaluate("() => window.__dbg.cfg()")
        maxp = pg.evaluate("() => window.__dbg.maxScore()")
        check("Doc duoc cau hinh", bool(cfg), str(cfg))
        check("Diem toi da = so ban", maxp == cfg["boards"], str(maxp))
        # Phi vao cua 3 tt: mot luot hoan hao phai duoc HON HAN, khong thi choi
        # gioi het muc van gan nhu khong duoc gi (bai hoc TT_PER_SHEET cua ARCADE-10).
        check("Thuong mot luot hoan hao LON HON han phi vao cua",
              maxp * cfg["ttPerBoard"] >= cfg["cost"] * 3,
              f'{maxp * cfg["ttPerBoard"]} tt vs phi {cfg["cost"]}')
        check("Phi khop bang phi cua server (easy = 3)", cfg["cost"] == 3, str(cfg["cost"]))
        check("Nhan SO DO MOT LOP / MO PHONG hien ra", pg.is_visible("#sim"),
              pg.inner_text("#sim"))
        check("0 loi trang", not errs, str(errs[:1])[:120])
        ctx.close()

        # ══════════ [2] Bộ sinh bàn — câu hỏi đắt nhất của cả bộ ══════════
        print("\n[2] Bo sinh ban — gieo lai nhieu luot x 5 ban")
        ROUNDS = 4          # so luot gieo lai (moi luot 5 ban) — 20 ban moi lan chay
        n_solvable = n_pre = n_selfwon = n_cross = 0
        n_boards = 0
        n_trap_ok = n_trap_total = 0
        seen_dsts, seen_srcs, seen_burnt, seen_n = [], [], [], []
        for r in range(ROUNDS):
            ctx, pg, errs = open_page(br, tt=99)
            pg.click("#start-btn")
            pg.wait_for_timeout(220)
            for b in range(maxp):
                g = pg.evaluate("() => window.__dbg.grid()")
                n_boards += 1
                seen_n.append(g["n"])
                seen_dsts.append(len(g["dsts"]))
                seen_srcs.append(len(g["srcs"]))
                seen_burnt.append(sum(1 for c in g["cells"] if c["k"] == "burnt"))

                if pg.evaluate("() => window.__dbg.prealigned()") == 0:
                    n_pre += 1
                if not pg.evaluate("() => window.__dbg.solved()"):
                    n_selfwon += 1
                if not any(bits(c["sol"]) >= 4 for c in g["cells"]):
                    n_cross += 1

                # ⚠️ MOI THIET BI SAI PHAI CO IT NHAT MOT DOAN DAN KE NO. Khong co
                #    thi khong duong nao dan dien tra sai duoc -> cong kien thuc rong.
                for d in g["dsts"]:
                    if d == g["goal"]:
                        continue
                    n_trap_total += 1
                    n = g["n"]
                    row, col = divmod(d, n)
                    nbs = []
                    for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                        rr, cc = row + dr, col + dc
                        if 0 <= rr < n and 0 <= cc < n:
                            nbs.append(g["cells"][rr * n + cc]["k"])
                    if "pipe" in nbs:
                        n_trap_ok += 1

                if pg.evaluate("() => window.__dbg.solve()"):
                    n_solvable += 1
                pg.evaluate("() => window.__dbg.send()")
                pg.wait_for_timeout(90)
                if b < maxp - 1:
                    pg.evaluate("() => window.__dbg.next()")
                    pg.wait_for_timeout(140)
            ctx.close()

        check("Do du " + str(ROUNDS * maxp) + " ban", n_boards == ROUNDS * maxp, str(n_boards))
        # ⚠️⚠️ BON PHEP KIEM QUAN TRONG NHAT CUA CA BO.
        check("MOI ban deu giai duoc", n_solvable == n_boards, f"{n_solvable}/{n_boards}")
        check("MOI ban: 0 o dung san", n_pre == n_boards, f"{n_pre}/{n_boards}")
        check("MOI ban KHONG tu thang luc mo", n_selfwon == n_boards, f"{n_selfwon}/{n_boards}")
        check("MOI ban: khong o nao co 4 mieng (nga tu)", n_cross == n_boards,
              f"{n_cross}/{n_boards}")
        check("MOI thiet bi sai deu co duong dan toi (bay co that)",
              n_trap_total > 0 and n_trap_ok == n_trap_total,
              f"{n_trap_ok}/{n_trap_total}")
        # Bo de len do kho that: co ban 3 thiet bi, co ban 2 pa-no, co ban co o chay.
        check("Co ban nhieu thiet bi (cong kien thuc)", max(seen_dsts) >= 3, str(sorted(set(seen_dsts))))
        check("Co ban hai pa-no (chu 'them vao')", max(seen_srcs) >= 2, str(sorted(set(seen_srcs))))
        check("Co ban co o chay", max(seen_burnt) >= 1, str(sorted(set(seen_burnt))))
        check("Luoi lon dan, va khong lon hon 6x6", min(seen_n) == 4 and max(seen_n) == 6,
              str(sorted(set(seen_n))))

        # ⚠️⚠️ TI LE DUNG DUOC CUA BO SINH, do truc tiep 60 lan moi ban. `makeGrid`
        #    thu lai toi 200 lan nen ti le nay chi can DU CAO; nhung neu no ve 0 thi
        #    ban do LUON roi vao ban lui (bo o chay, bo nhanh cut) va khong ai biet.
        #    Da xay ra that 26/08/2026: dieu kien neo nhanh bay hoi `k === "pipe"`
        #    trong khi loai o chua duoc gan ⇒ ban 4 dung that bai 200/200.
        ctx, pg, errs = open_page(br)
        rates = [pg.evaluate("k => window.__dbg.tryBuild(k, 60)", k) for k in range(maxp)]
        ctx.close()
        worst = min(r["ok"] for r in rates)
        check("Bo sinh dung duoc o MOI ban (>=50% moi lan gieo)", worst >= 30,
              str([r["ok"] for r in rates]))

        # ══════════ [3] Chơi thắng một bàn ══════════
        print("\n[3] Choi thang mot ban")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn")
        pg.wait_for_timeout(250)
        check("Tru dung 3 tt", pg.inner_text("#bal") == "37", pg.inner_text("#bal"))
        check("Nut Cap dien TAT khi tuyen chua lien",
              pg.get_attribute("#go", "disabled") is not None or pg.is_disabled("#go"),
              pg.inner_text("#hint"))
        hint0 = pg.inner_text("#hint")
        pg.evaluate("() => window.__dbg.solve()")
        pg.wait_for_timeout(120)
        check("Noi lien roi thi dong trang thai DOI", pg.inner_text("#hint") != hint0,
              pg.inner_text("#hint"))
        check("Nut Cap dien BAT khi tuyen da lien", not pg.is_disabled("#go"))
        pg.click("#go")
        pg.wait_for_timeout(320)
        check("Duoc diem", pg.inner_text("#hb-score") == "1", pg.inner_text("#hb-score"))
        check("Cong tt dung", int(pg.inner_text("#hb-mtr")) == cfg["ttPerBoard"],
              pg.inner_text("#hb-mtr"))
        why = pg.inner_text("#why")
        check("Hop giai thich hien ra", pg.is_visible("#why"), why[:70])
        # ⚠️ CAU KIEN THUC LA THU GAME NAY TON TAI DE DAY — no phai co that trong
        #    hop do, khong chi mot dong "dung roi".
        check("Hop giai thich mang CAU KIEN THUC (>40 ky tu)", len(why) > 40, str(len(why)))
        check("Vet sang chay tren tuyen", pg.locator(".rt-c.live").count() >= 3,
              str(pg.locator(".rt-c.live").count()))
        check("Khong xoay duoc nua sau khi chot",
              pg.locator(".rt-c:not([disabled])").count() == 0,
              str(pg.locator(".rt-c:not([disabled])").count()))
        check("0 loi trang", not errs, str(errs[:1])[:120])
        ctx.close()

        # ══════════ [4] Bàn phím ══════════
        # `docs/decisions/002` bac khuon `relationship_map` vi *"noi day la dang kho
        # lam ban phim nhat, ma du an khong co ha tang ban phim nao"*. Nay co
        # `js/pick-place.js`, va khuon nay phai tra loi duoc cau do bang so do.
        print("\n[4] Choi bang BAN PHIM")
        ctx, pg, errs = open_page(br)
        pg.click("#start-btn")
        pg.wait_for_timeout(250)
        first = pg.locator('.rt-c:not([disabled])').first
        first.focus()
        idx = int(first.get_attribute("data-i"))
        t0 = pg.evaluate("() => window.__dbg.grid().cells[%d].turns" % idx)
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(120)
        t1 = pg.evaluate("() => window.__dbg.grid().cells[%d].turns" % idx)
        check("Enter tren mot o thi o do XOAY", t0 != t1, f"{t0} -> {t1}")
        moved = pg.evaluate("""() => {
            const a = document.activeElement.getAttribute('data-i');
            return a; }""")
        # ⚠️ THU CA BON HUONG, va doi IT NHAT MOT huong doi duoc o. O dau tien co the
        #    nam sat mep hoac bi vay boi o chay/o trong, nen doi dung mot huong la
        #    phep kiem CHAP CHON theo ban gieo ra — kieu bao oan te nhat.
        moves = []
        for key in ("ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp"):
            pg.keyboard.press(key)
            pg.wait_for_timeout(70)
            moves.append(pg.evaluate("() => document.activeElement.getAttribute('data-i')"))
        check("Mui tien doi o dang chon", any(m != moved for m in moves),
              f"{moved} -> {moves}")
        # Mui tien phai NHAY QUA ca mot dai o chay/o trong, khong dung lai truoc no.
        check("Tieu diem luon dung tren mot o bam duoc",
              pg.evaluate("() => { const a = document.activeElement;"
                          " return a.classList.contains('rt-c') && !a.disabled; }"))
        check("Moi o la mot <button> (Tab toi duoc)",
              pg.evaluate("() => [...document.querySelectorAll('.rt-c')]"
                          ".every(e => e.tagName === 'BUTTON')"))
        check("O nao cung co aria-label",
              pg.evaluate("() => [...document.querySelectorAll('.rt-c')]"
                          ".every(e => (e.getAttribute('aria-label')||'').length > 2)"))
        # Voi nguoi dung ban phim thi vet sang khong noi duoc gi -> dong trang thai
        # la cho DUY NHAT noi ra "da lien hay chua".
        check("Dong trang thai la role=status",
              pg.get_attribute("#hint", "role") == "status")
        check("0 loi trang", not errs, str(errs[:1])[:120])
        ctx.close()

        # ══════════ [5] Cả lượt 5 bàn ══════════
        print("\n[5] Ca luot 5 ban")
        ctx, pg, errs = open_page(br, tt=40)
        pg.click("#start-btn")
        pg.wait_for_timeout(250)
        for b in range(maxp):
            pg.evaluate("() => window.__dbg.solve()")
            pg.wait_for_timeout(90)
            pg.click("#go")
            pg.wait_for_timeout(200)
            pg.click("#next")
            pg.wait_for_timeout(200)
        pg.wait_for_selector("#ov-over.show", timeout=6000)
        check("Bang ket qua hien ra", pg.is_visible("#ov-over"))
        check("Diem = so ban", pg.inner_text("#r-score") == str(maxp), pg.inner_text("#r-score"))
        check("Tren tong so = so ban", pg.inner_text("#r-max") == str(maxp))
        check("tt = so ban x moi ban", pg.inner_text("#r-mtr") == str(maxp * cfg["ttPerBoard"]),
              pg.inner_text("#r-mtr"))
        check("Ky luc duoc ghi", pg.inner_text("#r-best") == str(maxp), pg.inner_text("#r-best"))
        check("Dong 'da cong n tt' hien ra", pg.is_visible("#paid"), pg.inner_text("#paid"))
        check("Co dai dan sang bai doc", pg.is_visible("#read-link"),
              pg.get_attribute("#read-link", "href"))
        check("Dai doc dan dung bai NGUON cua game",
              pg.get_attribute("#read-link", "href")
              == "library.html?a=art-sunlight-into-electricity")
        check("Vi da cong tt", pg.inner_text("#bal") == str(40 - cfg["cost"]
                                                           + maxp * cfg["ttPerBoard"]),
              pg.inner_text("#bal"))
        check("0 loi trang", not errs, str(errs[:1])[:120])
        ctx.close()

        # ══════════ [6] Bố cục bốn khổ màn ══════════
        # ⚠️ Co ban do bang JS. `aspect-ratio` mot minh tung cho san 1086x2px o lop
        #    game nay (ghi o css/decision-game.css) — nen phai do KHUNG BAO THAT.
        print("\n[6] Bo cuc — ban khong tran, khong bi cat")
        for w, h in ((1440, 900), (1024, 768), (768, 1024), (390, 844)):
            ctx, pg, errs = open_page(br, w=w, h=h)
            pg.click("#start-btn")
            pg.wait_for_timeout(400)
            bx = pg.evaluate("""() => {
                const b = document.getElementById('board').getBoundingClientRect();
                const f = document.getElementById('field').getBoundingClientRect();
                const c = document.querySelector('.rt-c').getBoundingClientRect();
                const doc = document.documentElement;
                return { bw:b.width, bh:b.height, bt:b.top, bb:b.bottom, bl:b.left, br:b.right,
                         ft:f.top, fb:f.bottom, fl:f.left, fr:f.right,
                         cw:c.width, ch:c.height,
                         ovf: doc.scrollWidth - doc.clientWidth }; }""")
            tag = f"{w}x{h}"
            check(f"[{tag}] ban co that (>=132px)", bx["bw"] >= 132 and bx["bh"] >= 132,
                  f'{round(bx["bw"])}x{round(bx["bh"])}')
            check(f"[{tag}] ban VUONG", abs(bx["bw"] - bx["bh"]) <= 2,
                  f'{round(bx["bw"])}x{round(bx["bh"])}')
            check(f"[{tag}] ban nam TRON trong san",
                  bx["bt"] >= bx["ft"] - 1 and bx["bb"] <= bx["fb"] + 1
                  and bx["bl"] >= bx["fl"] - 1 and bx["br"] <= bx["fr"] + 1,
                  f'ban {round(bx["bt"])}..{round(bx["bb"])} san {round(bx["ft"])}..{round(bx["fb"])}')
            # ⚠️ O PHAI VUONG — hang cua luoi tung la `auto` va cho o 137x36px.
            check(f"[{tag}] o VUONG", abs(bx["cw"] - bx["ch"]) <= 1.5,
                  f'{round(bx["cw"],1)}x{round(bx["ch"],1)}')
            # ⚠️ MOC VUNG CHAM PHU THUOC LOAI CON TRO, va do la tien le CO SAN trong
            #    du an: moc 44px cua `.seg` duoc CO Y gan vao `@media (pointer: coarse)`,
            #    va `check_pages` da mot lan bao oan vi khong xet dieu do (quy tac 10
            #    muc 6 + hai loi trong phep kiem, 14/08/2026). WCAG 2.5.5 noi ve muc
            #    tieu CHAM; tren man rong dung chuot thi o 36px van bam trung.
            floor = 47.5 if w <= 900 else 36.0
            check(f"[{tag}] o bam >= {floor:.0f}px ({'cham' if w <= 900 else 'chuot'})",
                  min(bx["cw"], bx["ch"]) >= floor,
                  f'{round(bx["cw"],1)}x{round(bx["ch"],1)}')
            # ⚠️ BIEN 1px, DUNG BANG `audit_viewports.py` (`sw <= cw + 1`). Do lai
            #    26/08/2026: **ca nam** game lop quyet dinh deu bao 391/390 o kho
            #    390px, ke ca truoc khi bam Bat dau ⇒ do la 1px cua KHUNG DUNG CHUNG,
            #    khong phai cua trang nao. Dat moc 0 o day la mot phep kiem bao oan
            #    cho moi game moi — va mot phep kiem hay bao oan thi som muon bi bo qua.
            check(f"[{tag}] khong tran ngang", bx["ovf"] <= 1, f'tran {bx["ovf"]}px')
            check(f"[{tag}] nhan MO PHONG van hien", pg.is_visible("#sim"))
            check(f"[{tag}] 0 loi trang", not errs, str(errs[:1])[:100])
            ctx.close()

        # ══════════ [7] Đổi ngôn ngữ giữa lượt ══════════
        print("\n[7] Doi ngon ngu giua luot")
        ctx, pg, errs = open_page(br, lang="vi")
        pg.click("#start-btn")
        pg.wait_for_timeout(250)
        vi_brief = pg.inner_text("#brief")
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(250)
        en_brief = pg.inner_text("#brief")
        check("Loi brief doi tieng", vi_brief != en_brief and len(en_brief) > 30,
              en_brief[:60])
        check("Ban choi con nguyen sau khi doi tieng",
              pg.locator(".rt-c").count() > 8, str(pg.locator(".rt-c").count()))
        check("Nhan MO PHONG cung doi tieng", "SIMULATED" in pg.inner_text("#sim"),
              pg.inner_text("#sim"))
        # `inner_text` tra ve chu DA QUA `text-transform` cua CSS (header in HOA),
        # nen phai so khong phan biet chu hoa — bai hoc "nhum ky tu co dau" cua quy
        # tac 8 muc 6: phep kiem chu chi dung khi no doi dung thu trang THAT SU in ra.
        check("Ten game tren header doi tieng", "route" in pg.inner_text("#gtag").lower(),
              pg.inner_text("#gtag"))
        check("0 loi trang", not errs, str(errs[:1])[:120])
        ctx.close()

        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 1 if bad_n else 0


if __name__ == "__main__":
    sys.exit(main())
