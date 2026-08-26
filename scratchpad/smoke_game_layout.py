# -*- coding: utf-8 -*-
"""smoke_game_layout.py — đo trên Chromium THẬT hai thứ thêm ngày 12/08/2026:
     ① sân chiếm hết chỗ còn lại (`--field-w`), tỉ lệ KHÔNG vỡ
     ② lời nhắc xoay ngang chỉ hiện đúng lúc, và luôn có đường ra

Chạy: python -m http.server 8123 trong AstroQhtml/ rồi
      python scratchpad/smoke_game_layout.py

⚠️ Nhãn của check() phải KHÔNG DẤU — console Windows mặc định cp1252, in chữ có dấu
   là UnicodeEncodeError ném GIỮA LÚC CHẠY và bỏ dở mọi phép kiểm phía sau (bài học
   29/07/2026). Chữ có dấu chỉ được nằm trong ĐIỀU KIỆN.
"""
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123/"
GAMES = [("game-dodge.html", 1.6), ("game-defender.html", 1.0),
         ("game-constellation.html", 1.6),
         # ARCADE-06 them 12/08/2026 — cung khung game-shell, ti le 8:5.
         ("game-catch.html", 1.6),
         # ARCADE-05 them 12/08/2026 — cung khung game-shell, ti le 8:5.
         ("game-maze.html", 1.6),
         # ARCADE-03 them 12/08/2026 — ca SAU mini-game nay cung mot khung.
         ("game-racer.html", 1.6),
         # ARCADE-07 them 16/08/2026 — game LOP QUYET DINH dau tien. Cung khung
         # `game-shell` nhung ti le 2.05 (rong-va-thap) chu khong phai 8:5: noi
         # dung la CHU DE DOC, khong phai san canvas. Xem `css/decision-game.css`.
         # ⚠️ CAP (rong, hep): day la game DUY NHAT doi ti le theo kho man —
         #    noi dung la CHU DE DOC nen man hep phai cho hop CAO, khong phai
         #    hop thap-ma-rong. Sau game kia dung mot ti le o moi kho.
         ("game-survival.html", (2.05, 0.72)),
         # ARCADE-08 — cung lop QUYET DINH, cung `css/decision-game.css` nen
         # cung cap ti le. Khuon choi thi khac han (xep thu tu).
         ("game-comms.html", (2.05, 0.72)),
         ("game-recycle.html", (2.05, 0.72)),
         ("game-units.html", (2.05, 0.72)),
         # ⚠️ ARCADE-11 LA GAME DUY NHAT CUA LOP NAY DOI TI LE MAN HEP: 0.62 chu
         # khong phai 0.72. Bon game kia chua CHU, con day chua mot BAN VUONG, va
         # ban bi kep boi chieu cao con lai sau loi brief — do duoc voi 0.72 thi o
         # 6x6 chi con 36px (duoi moc 48px). San hep lai mot chut nhung CAO hon thi
         # o len ~49px. Ti le man rong GIU nguyen 2.05 (o do san chia hai cot).
         # Ly do day du + so do ghi o dau `css/game-route.css`.
         ("game-route.html", (2.05, 0.62))]

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


BOX = """() => {
  const f = document.querySelector('.field'), p = document.querySelector('.play'),
        h = document.querySelector('.hud');
  const fr = f.getBoundingClientRect(), pr = p.getBoundingClientRect(),
        hr = h.getBoundingClientRect();
  const cs = getComputedStyle(p);
  return {fw:fr.width, fh:fr.height, fl:fr.left, fr_:fr.right,
          pw:pr.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight),
          ph:pr.height - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom),
          pl:pr.left, pt:pr.top, pb:pr.bottom, hw:hr.width,
          docW: document.documentElement.scrollWidth,
          winW: window.innerWidth};
}"""


def new(b, w, h, touch=False, dpr=2):
    return b.new_page(viewport={"width": w, "height": h}, device_scale_factor=dpr,
                      has_touch=touch, is_mobile=touch)


with sync_playwright() as pw:
    b = pw.chromium.launch()

    # ══════════════════════════════════════════════════════════════════════
    print("=== [1] San chiem het cho, ti le KHONG vo ===")
    for game, ar_spec in GAMES:
        for name, w, h in [("FullHD", 1920, 1080), ("MacBook-Air", 1470, 956),
                           ("Win-1366", 1366, 768), ("iPhone-doc", 390, 844)]:
            # ⚠️ Moc doi ti le la 900px, khai o `css/decision-game.css`. Game nao
            #    chi co MOT ti le thi cap nay la mot so — giu nguyen cach cu.
            ar = ar_spec if not isinstance(ar_spec, tuple) else (
                 ar_spec[0] if w > 900 else ar_spec[1])
            pg = new(b, w, h, dpr=1)
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(BASE + game)
            pg.wait_for_selector(".field")
            pg.wait_for_timeout(450)
            m = pg.evaluate(BOX)
            tag = "%s %s" % (game.replace("game-", "").replace(".html", ""), name)

            got = m["fw"] / m["fh"] if m["fh"] else 0
            check("[1] %s: ti le san dung %.2f" % (tag, ar), abs(got - ar) < 0.02,
                  "do duoc %.3f" % got)
            # Vua khit MOT trong hai chieu — khong con cho bo khong
            fits = (abs(m["fw"] - min(m["pw"], m["ph"] * ar)) < 2)
            check("[1] %s: san vua khit o chua" % tag, fits,
                  "san %.0f / vua duoc %.0f" % (m["fw"], min(m["pw"], m["ph"] * ar)))
            # KHONG duoc tran ra ngoai o .play (ca ngang lan doc)
            check("[1] %s: san nam gon trong o .play" % tag,
                  m["fw"] <= m["pw"] + 1 and m["fh"] <= m["ph"] + 1,
                  "%.0fx%.0f trong %.0fx%.0f" % (m["fw"], m["fh"], m["pw"], m["ph"]))
            check("[1] %s: khong tran ngang ca trang" % tag,
                  m["docW"] <= m["winW"] + 1, "doc %.0f / win %.0f" % (m["docW"], m["winW"]))
            # ⚠️ PHEP KIEM NAY DA DOI PHAT BIEU (12/08/2026). Ban cu doi "HUD >= 800px",
            #    tuc doi dung cai THANH NGANG ma bo cuc o-cua da thay bang CONSOLE DOC
            #    150px — nen no bao hong dung luc san pham lam dung. Thu no THAT SU bao
            #    ve la "chip khong bi cat chu"; nay do thang chuyen do, o CA hai bo cuc.
            cut = pg.evaluate('''() => [...document.querySelectorAll('.hud .chip')]
                 .filter(c => c.scrollWidth > c.clientWidth + 1)
                 .map(c => c.textContent.trim())''')
            check("[1] %s: khong chip nao bi cat chu" % tag, not cut, str(cut))
            if w > 900:
                # Man rong: HUD la CONSOLE DOC, va nhan `.k` phai con (cot co cho)
                col = pg.eval_on_selector(".hud", "el => getComputedStyle(el).flexDirection")
                kvis = pg.evaluate('''() => [...document.querySelectorAll('.hud .chip .k')]
                       .every(k => getComputedStyle(k).display !== 'none')''')
                check("[1] %s: HUD la console DOC" % tag, col == "column", col)
                check("[1] %s: nhan chip con hien (cot co cho)" % tag, kvis)
            else:
                floor = min(m["pw"], 800)
                check("[1] %s: man hep: HUD khong hep hon ban cu" % tag,
                      m["hw"] >= floor - 1, "HUD %.0f / san cu %.0f" % (m["hw"], floor))
            check("[1] %s: 0 loi trang" % tag, not errs, str(errs[:1]))
            pg.close()

    # ══════════════════════════════════════════════════════════════════════
    print("\n=== [2] San to ra THAT SU so voi ban cu (moc 800/600px) ===")
    for game, old in [("game-dodge.html", 800), ("game-defender.html", 600),
                      ("game-constellation.html", 800), ("game-catch.html", 800),
                      ("game-maze.html", 800), ("game-racer.html", 800)]:
        pg = new(b, 1920, 1080, dpr=1)
        pg.goto(BASE + game)
        pg.wait_for_selector(".field")
        pg.wait_for_timeout(450)
        m = pg.evaluate(BOX)
        check("[2] %s: san rong hon moc cu %dpx" % (game, old), m["fw"] > old * 1.15,
              "%.0fpx = %.2f lan" % (m["fw"], m["fw"] / old))
        pg.close()

    # ══════════════════════════════════════════════════════════════════════
    print("\n=== [3] Loi nhac xoay ngang ===")
    G = "game-dodge.html"

    # (a) may cam ung, de DOC -> hien
    # ⚠️ PHAI GHIM `astroq-lang`: Chromium cua Playwright mac dinh `en-US` va mui gio
    #    khong phai Viet Nam, nen `guessLang()` tra ve `en` — dung theo thiet ke tu
    #    07/08/2026. Khong ghim thi phan "tieng Viet" cua bo do lang le chay bang
    #    tieng Anh va phep kiem bao hong OAN (da xay ra dung o day mot lan).
    pg = new(b, 390, 844, touch=True)
    pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg.goto(BASE + G); pg.wait_for_timeout(700)
    check("[3a] cam ung + doc: loi nhac HIEN",
          pg.locator(".rot.show").count() == 1)
    check("[3a] co duong ra (nut 'van choi doc')",
          pg.locator(".rot-ok").count() == 1 and pg.locator(".rot-ok").is_visible())
    box = pg.locator(".rot-ok").bounding_box()
    check("[3a] vung cham cua duong ra >= 44px", box and box["height"] >= 44,
          "%.0fpx" % (box["height"] if box else 0))
    # Nut "Ve Khu Huan Luyen" o header PHAI con bam duoc — tre khong bao gio ket
    hit = pg.evaluate("""() => {
      const a = document.querySelector('.back-btn'); const r = a.getBoundingClientRect();
      const el = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);
      return !!(el && (el === a || a.contains(el)));
    }""")
    check("[3a] nut ve Khu Huan Luyen VAN bam duoc (khong ket)", hit)
    txt = pg.locator(".rot-h").inner_text()
    check("[3a] loi nhac bang tieng Viet", "Xoay" in txt, txt)

    # (b) bam duong ra -> tat, va tat luon o lan tai lai trong CUNG phien
    pg.locator(".rot-ok").click(); pg.wait_for_timeout(350)
    check("[3b] bam duong ra thi loi nhac TAT", pg.locator(".rot.show").count() == 0)
    pg.reload(); pg.wait_for_timeout(700)
    check("[3b] tai lai trong cung phien: KHONG nhac lai",
          pg.locator(".rot.show").count() == 0)
    pg.close()

    # (c) may cam ung de NGANG -> khong hien
    pg = new(b, 844, 390, touch=True)
    pg.goto(BASE + G); pg.wait_for_timeout(700)
    check("[3c] cam ung + ngang: KHONG nhac", pg.locator(".rot.show").count() == 0)
    pg.close()

    # (d) laptop bop hep (con tro CHUOT, khung doc) -> khong hien
    # ⚠️ Day la ly do dieu kien phai co `pointer: coarse`: bop hep cua so Chrome
    #    tren laptop cung ra khung doc, ma o do "xoay may" la vo nghia.
    pg = new(b, 420, 900, touch=False, dpr=1)
    pg.goto(BASE + G); pg.wait_for_timeout(700)
    check("[3d] laptop bop hep (chuot): KHONG nhac",
          pg.locator(".rot.show").count() == 0)
    pg.close()

    # (e) dang CHOI thi khong duoc cat ngang
    pg = new(b, 844, 390, touch=True)
    # ⚠️ PHAI GIEO VI: moi luot dodge tru 5 tt, vi trong khong thi game hien overlay
    #    "chua du tt" va KHONG BAO GIO vao man choi — luc do phep kiem duoi day "dat"
    #    mot cach RONG (no bo qua chinh minh). Da xay ra dung the o luot chay dau.
    pg.add_init_script("localStorage.setItem('astroq-asteroids','999');"
                       "localStorage.setItem('astroq-lang','vi')")
    pg.goto(BASE + G); pg.wait_for_timeout(600)
    pg.evaluate("""() => {
      const b = document.querySelector('.ov.show button');
      if (b) b.click();
    }""")
    pg.wait_for_timeout(600)
    running = pg.evaluate("""() => ![].slice.call(document.querySelectorAll('.ov.show'))
                                 .some(o => !o.classList.contains('rot'))""")
    if running:
        pg.set_viewport_size({"width": 390, "height": 844})
        pg.evaluate("() => AstroQGameShell.refreshRotate()")
        pg.wait_for_timeout(300)
        check("[3e] dang choi thi KHONG cat ngang bang loi nhac",
              pg.locator(".rot.show").count() == 0)
    else:
        # ⚠️ KHONG bao "dat" khi phep kiem tu bo qua chinh minh — mot phep kiem dat
        #    mot cach rong con te hon khong co phep kiem nao.
        check("[3e] vao duoc man choi de kiem (vi da gieo tt)", False,
              "khong vao duoc man choi — xem lai vi/overlay")
    pg.close()

    # (f) doi ngon ngu -> loi nhac dich theo
    pg = new(b, 390, 844, touch=True)
    pg.add_init_script("localStorage.setItem('astroq-lang','en')")
    pg.goto(BASE + G); pg.wait_for_timeout(700)
    t_en = pg.locator(".rot-h").inner_text()
    check("[3f] ban EN: loi nhac dich theo", "sideways" in t_en.lower(), t_en)
    pg.locator('.lang-switch button[data-lang="vi"]').click()
    pg.wait_for_timeout(300)
    t_vi = pg.locator(".rot-h").inner_text()
    check("[3f] bam VI: dich lai ngay (khong phai tai lai trang)",
          "Xoay" in t_vi, t_vi)
    pg.close()

    # (g) Loi nhac o file DUNG CHUNG nen moi game deu nhan duoc — TRU game tu khai
    #     `data-rotate="off"`.
    #     ⚠️ PHAT BIEU DOI 16/08/2026, VA MANH LEN. Ban cu doi MOI game phai co loi
    #        nhac; ARCADE-07 la game CHU DE DOC, o do xoay ngang lam hop chu thap
    #        di va kho doc hon — nhac xoay la bao tre lam cho trai nghiem te di.
    #        Nay kiem CA HAI CHIEU: khong khai co thi PHAI co loi nhac, khai co thi
    #        PHAI khong co. Chieu thu hai la thu ban cu khong hoi toi, nen day la
    #        siet chat chu khong phai noi long.
    for game, _ in GAMES:
        pg = new(b, 390, 844, touch=True)
        pg.goto(BASE + game); pg.wait_for_timeout(700)
        off = pg.evaluate("() => document.querySelector('.stage')"
                          ".getAttribute('data-rotate') === 'off'")
        n = pg.locator(".rot.show").count()
        if off:
            check("[3g] %s: CO Y khong nhac xoay (game chu)" % game, n == 0, str(n))
        else:
            check("[3g] %s: co loi nhac (dung chung, khong chep nhieu ban)" % game,
                  n == 1, str(n))
        pg.close()

    b.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(0 if bad_n == 0 else 1)
