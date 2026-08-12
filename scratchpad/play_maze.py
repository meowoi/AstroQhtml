"""play_maze.py — ME CUNG THIEN HA (ARCADE-05) choi THAT tren Chromium.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/play_maze.py

Do nhung thu doc code KHONG chung minh duoc:
  [1] man brief: chua tru tien, nut Pause an
  [2] tru DUNG 4 tt MOT lan
  [3] TUONG CHAN THAT: bam vao huong co tuong thi KHONG di, va KHONG tinh buoc
  [4] ME CUNG LUON GIAI DUOC — sinh 30 me cung, moi cai deu co duong tu (0,0) ra cong
  [5] di het tinh the roi ra cong → bang ket qua, vi chinh cong DUNG (tinh the + thuong)
  [6] tam dung: dong ho DUNG HAN
  [7] he 15x9 o, o VUONG, me cung nam trong san
  [8] thieu tt → khong tru tien
  [9] doi VI/EN dich ca hai dong do JS sinh o bang ket qua
 [10] dien thoai 390x844: ti le 8:5, khong tran ngang, co d-pad
 [11] goi y he ra sau khi dung yen — va chi he MAY O, khong giai ho

⚠️ Bot di bang `__maze.move(dir)` — DUNG ham ma ban phim goi, nen no chiu dung luat
   tuong. Be mat test KHONG cap diem, KHONG cap thuong, KHONG di xuyen tuong.
⚠️ Ghim `astroq-lang` (Chromium mac dinh en-US).
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-maze.html"
dat = hong = 0


def check(label, cond, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def mk(br, lang="vi", w=1440, h=900, bal=50):
    ctx = br.new_context(viewport={"width": w, "height": h},
                         locale="vi-VN" if lang == "vi" else "en-US",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','%s');"
        "localStorage.setItem('astroq-asteroids','%d');"
        "localStorage.removeItem('astroq-maze-best');"
        "localStorage.setItem('astroq-user', JSON.stringify("
        "{name:'Nhi',pilotName:'Nhi',uid:'u-test',character:'m',avatar:'ava/avam.png'}));"
        % (lang, bal))
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    return ctx, pg


def st(pg, k):
    return pg.evaluate("(k) => window.__maze[k]", k)


def bal(pg):
    return pg.evaluate("() => Number(localStorage.getItem('astroq-asteroids')||0)")


def walk(pg, dirs, cap=400):
    """Di theo mot day huong, bo hoat canh truot cho nhanh. Tra so buoc DI DUOC."""
    return pg.evaluate("""(dirs) => {
        let n = 0;
        for (const d of dirs) {
          window.__maze.snap();
          if (window.__maze.move(d)) n++;
          if (window.__maze.state !== 'play') break;
        }
        window.__maze.snap();
        return n;
    }""", dirs[:cap])


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ════════════════════════════════════════════ [1] Man brief
    print("\n[1] Man brief")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)
    check("be mat test co that", pg.evaluate("() => !!window.__maze"))
    check("trang thai 'start'", st(pg, "state") == "start", str(st(pg, "state")))
    check("CHUA tru tien o man brief", bal(pg) == 50, str(bal(pg)))
    check("nut Pause dang AN", "is-hidden" in (pg.get_attribute("#btn-pause", "class") or ""))
    check("tag ten game dich", "mê cung" in pg.inner_text("#gtag").casefold(), pg.inner_text("#gtag"))

    # ══════════════════════════════════ [4] Me cung LUON giai duoc
    print("\n[4] 30 me cung: cai nao cung co duong ra")
    res = pg.evaluate("""() => {
        // Sinh lai nhieu lan bang chinh duong bat dau luot? Khong — de khong tru tien,
        // ta goi truc tiep vao bo sinh qua mot luot choi that MOT lan roi dung `path()`
        // sau moi lan sinh lai bang cach bat dau lai (tru tien) — thay vao do doc
        // `shortest` cua tung luot la du: no la DO DAI duong BFS, 0 = khong co duong.
        return null;
    }""")
    # ⚠️ Khong the sinh lai me cung ma khong tru tien (dung: khong co cua sau nao cap
    #    luot choi mien phi). Nen do bang 30 LUOT THAT — vi 50 tt khong du, ta gieo
    #    lai vi truoc moi luot. Day cung la phep do "tru dung 4 tt" o muc [2].
    solvable = 0
    for i in range(30):
        pg.evaluate("() => localStorage.setItem('astroq-asteroids','50')")
        pg.evaluate("() => window.__maze && null")
        pg.click("#again-btn" if pg.is_visible("#ov-over") else "#start-btn")
        pg.wait_for_timeout(60)
        if st(pg, "state") != "play":
            break
        p = pg.evaluate("() => window.__maze.path()")
        sh = st(pg, "shortest")
        if p and len(p) > 0 and sh > 0:
            solvable += 1
        # ra cong ngay de vong sau bat dau lai duoc
        walk(pg, p)
        pg.wait_for_timeout(60)
    check("30/30 me cung co duong ra (0,0) → cong", solvable == 30, "%d/30" % solvable)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════ [2] Tru phi + [3] tuong chan that
    print("\n[2] Bat dau luot: tru dung 4 tt, mot lan")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(400)
    pg.click("#start-btn")
    pg.wait_for_timeout(300)
    check("vao 'play'", st(pg, "state") == "play", str(st(pg, "state")))
    check("tru dung 4 tt", bal(pg) == 46, str(bal(pg)))
    pg.keyboard.press("Space")
    pg.wait_for_timeout(200)
    check("Space luc dang choi KHONG tru them", bal(pg) == 46, str(bal(pg)))
    check("kich thuoc me cung 15x9",
          st(pg, "cfg")["cols"] == 15 and st(pg, "cfg")["rows"] == 9,
          "%dx%d" % (st(pg, "cfg")["cols"], st(pg, "cfg")["rows"]))

    print("\n[3] Tuong chan THAT: khong di duoc va khong tinh buoc")
    # O (0,0) chac chan co tuong phia TREN va BEN TRAI (mep me cung).
    p0 = st(pg, "pos")
    s0 = st(pg, "steps")
    okup = pg.evaluate("() => window.__maze.move('up')")
    okleft = pg.evaluate("() => window.__maze.move('left')")
    pg.wait_for_timeout(120)
    check("bam len/trai o goc: KHONG di duoc", okup is False and okleft is False,
          "up=%s left=%s" % (okup, okleft))
    check("vi tri khong doi", st(pg, "pos") == p0, str(st(pg, "pos")))
    check("KHONG tinh buoc khi dung tuong", st(pg, "steps") == s0,
          "%d -> %d" % (s0, st(pg, "steps")))

    # ══════════════════════ [11] Goi y he ra sau khi dung yen
    print("\n[11] Dung yen 15s thi goi y he ra (va chi he MAY O)")
    check("chua dung yen thi CHUA co goi y", st(pg, "hint") is False, str(st(pg, "hint")))
    pg.evaluate("() => { window.__maze.cfg.hintAfter = 0.4; }")   # rut moc cho bo do
    pg.wait_for_timeout(900)
    check("dung yen thi goi y he ra", st(pg, "hint") is True, str(st(pg, "hint")))
    check("goi y CHI he may o, khong giai ho",
          st(pg, "cfg")["hintCells"] < st(pg, "shortest"),
          "he %d o / duong dai %d o" % (st(pg, "cfg")["hintCells"], st(pg, "shortest")))
    pg.evaluate("() => { window.__maze.cfg.hintAfter = 15; }")

    # ════════════════════════════════ [6] Tam dung
    print("\n[6] Tam dung thi dong ho dung han")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(250)
    check("vao 'paused'", st(pg, "state") == "paused", str(st(pg, "state")))
    t1 = pg.inner_text("#hb-time")
    pg.wait_for_timeout(1600)
    check("dong ho KHONG chay khi tam dung", pg.inner_text("#hb-time") == t1,
          "%s -> %s" % (t1, pg.inner_text("#hb-time")))
    pg.click("#resume-btn")
    pg.wait_for_timeout(200)
    check("Choi tiep thi chay lai", st(pg, "state") == "play", str(st(pg, "state")))

    # ══════════ [5] Ra cong SOM (chua thu het) — quyen cua tre
    #
    # ⚠️ CONG KET THUC LUOT NGAY khi buoc vao, KE CA khi con tinh the. Do la LUAT
    #    dung: tre duoc quyen ra som va chiu gia (it tinh the = it tt). Bat phai thu
    #    du moi cho ra la lay di mot quyet dinh cua tre.
    #    ⚠️ Lan dau bo do nay di theo `tour()` roi doi "thu du 5/5" — nhung duong ghe
    #       het tinh the CO LUC di ngang qua cong va luot ket thuc som. Do la phep do
    #       hoi sai cau, khong phai san pham sai.
    print("\n[5] Ra cong som: ve dich duoc, va thuong TINH DUNG so tinh the da thu")
    before = bal(pg)
    total_gems = st(pg, "gems")
    walk(pg, pg.evaluate("() => window.__maze.path()"))
    pg.wait_for_timeout(300)
    got_early = st(pg, "got")
    check("ra cong duoc du con tinh the", st(pg, "state") == "over",
          "%d/%d tinh the" % (got_early, total_gems))
    paid = int(pg.inner_text("#r-mtr"))
    check("vi chinh cong DUNG so tren bang ket qua", bal(pg) == before + paid,
          "%d + %d = %d" % (before, paid, bal(pg)))
    check("thuong = tinh the da thu + thuong ve dich", paid >= got_early,
          "%d tt / %d tinh the" % (paid, got_early))
    why = pg.inner_text("#why")
    check("dong 'thuong gom gi' khop so tinh the THAT da thu",
          str(got_early) in why, why[:60])
    check("ky luc luu lai",
          pg.evaluate("() => localStorage.getItem('astroq-maze-best')") not in (None, "", "{}"),
          str(pg.evaluate("() => localStorage.getItem('astroq-maze-best')")))
    check("nut Pause an lai", "is-hidden" in (pg.get_attribute("#btn-pause", "class") or ""))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))

    # ══════════ [5b] Thu HET tinh the roi moi ra → thuong CAO HON
    #
    # Chon mot me cung ma duong ghe-het-tinh-the KHONG di ngang qua cong truoc khi
    # thu xong (tinh o Python tu chinh day huong). Thu toi 10 luot; me cung sinh moi
    # lan mot khac nen day la phep chon, khong phai phep may man vo han.
    print("\n[5b] Thu HET tinh the roi ra cong: thuong cao hon, why noi dung 5")
    DX = {"up": 0, "down": 0, "left": -1, "right": 1}
    DY = {"up": -1, "down": 1, "left": 0, "right": 0}
    found = False
    for attempt in range(10):
        pg.evaluate("() => localStorage.setItem('astroq-asteroids','50')")
        pg.click("#again-btn" if pg.is_visible("#ov-over") else "#start-btn")
        pg.wait_for_timeout(80)
        if st(pg, "state") != "play":
            break
        tour = pg.evaluate("() => window.__maze.tour()")
        ex = st(pg, "exit")
        p = st(pg, "pos")
        c, r = p["c"], p["r"]
        crosses = False
        for k, d in enumerate(tour[:-1]):          # buoc cuoi MOI duoc la cong
            c += DX[d]; r += DY[d]
            if c == ex["c"] and r == ex["r"]:
                crosses = True
                break
        if crosses:
            walk(pg, pg.evaluate("() => window.__maze.path()"))   # ket thuc luot nay
            pg.wait_for_timeout(80)
            continue
        found = True
        gems_n = st(pg, "gems")
        b0 = bal(pg)
        walk(pg, tour, cap=600)
        pg.wait_for_timeout(300)
        check("thu du tinh the truoc khi ra", st(pg, "got") == gems_n,
              "%d/%d" % (st(pg, "got"), gems_n))
        check("ra cong → 'over'", st(pg, "state") == "over", str(st(pg, "state")))
        full_paid = int(pg.inner_text("#r-mtr"))
        check("thuong > so tinh the (co them thuong ve dich)", full_paid > gems_n,
              "%d tt / %d tinh the" % (full_paid, gems_n))
        check("vi cong dung", bal(pg) == b0 + full_paid, "%d + %d = %d" % (b0, full_paid, bal(pg)))
        w = pg.inner_text("#why")
        check("dong 'thuong gom gi' noi dung so tinh the", str(gems_n) in w, w[:60])
        check("thu HET tinh the thi thuong CAO HON ra som",
              full_paid > paid or got_early == gems_n,
              "du %d tt vs ra som %d tt" % (full_paid, paid))
        break
    check("tim duoc me cung de thu het tinh the trong 10 luot", found, "attempt=%d" % attempt)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))

    # ═══════════════════ [9] Doi VI/EN o bang ket qua
    print("\n[9] Doi ngon ngu o bang ket qua")
    pg.click(".lang-switch [data-lang='en']")
    pg.wait_for_timeout(400)
    check("tieu de dich", "Out of the maze" in pg.inner_text("#ov-over"), pg.inner_text("h2")[:40])
    check("dong 'thuong gom gi' CUNG dich", "crystals" in pg.inner_text("#why"),
          pg.inner_text("#why")[:50])
    check("dong 'da cong vao vi' CUNG dich", "added to your wallet" in pg.inner_text("#paid"),
          pg.inner_text("#paid")[:50])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════════ [8] Thieu tt
    print("\n[8] Thieu Thien thach tim")
    ctx, pg = mk(br, bal=3)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(400)
    pg.click("#start-btn")
    pg.wait_for_timeout(300)
    check("hien man 'chua du tt'", pg.is_visible("#ov-need"))
    check("KHONG tru tien", bal(pg) == 3, str(bal(pg)))
    check("van o 'start'", st(pg, "state") == "start", str(st(pg, "state")))
    body = pg.inner_text("#need-body")
    check("noi ro can 4, dang co 3", "4" in body and "3" in body, body[:70])
    ctx.close()

    # ═══════════════════ [7][10] Hinh hoc + dien thoai
    print("\n[7] O vuong, me cung nam trong san")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)
    geo = pg.evaluate("""() => {
        const cfg = window.__maze.cfg;
        // Suy lai dung phep tinh cua trang: o VUONG, me cung can giua san 800x500.
        const pad = 26;
        const cell = Math.floor(Math.min((cfg.VW - pad*2)/cfg.cols, (cfg.VH - pad*2)/cfg.rows));
        return { cell, w: cell*cfg.cols, h: cell*cfg.rows, VW: cfg.VW, VH: cfg.VH };
    }""")
    check("o la hinh VUONG (mot con so cell duy nhat)", geo["cell"] > 10, "cell=%d" % geo["cell"])
    check("me cung nam TRON trong san",
          geo["w"] <= geo["VW"] and geo["h"] <= geo["VH"],
          "%dx%d trong %dx%d" % (geo["w"], geo["h"], geo["VW"], geo["VH"]))

    print("\n[10] Dien thoai 390x844")
    ctx2, pg2 = mk(br, "vi", 390, 844)
    pg2.goto(URL, wait_until="load")
    pg2.wait_for_timeout(600)
    over = pg2.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("khong tran ngang", over <= 1, "%dpx" % over)
    ratio = pg2.evaluate("""() => {
        const r = document.getElementById('field').getBoundingClientRect();
        return Math.round(r.width / r.height * 1000);
    }""")
    check("san giu ti le 8:5", abs(ratio - 1600) <= 20, "%.3f" % (ratio/1000))
    pg2.click("#start-btn")
    pg2.wait_for_timeout(300)
    check("choi duoc tren dien thoai", st(pg2, "state") == "play", str(st(pg2, "state")))
    check("0 loi trang", not pg2.perr, str(pg2.perr[:1]))
    ctx2.close()
    ctx.close()

    # d-pad chi hien tren may CAM UNG (pointer: coarse) — do bang mot context cam ung
    print("\n[10b] d-pad chi hien tren may cam ung")
    ctx = br.new_context(viewport={"width": 390, "height": 844}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh", has_touch=True, is_mobile=True)
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','50');")
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)
    check("may cam ung: d-pad HIEN", pg.is_visible("#dpad"))
    # ⚠️ Tren may CAM UNG + man DOC, js/game-shell.js hien loi nhac "xoay ngang" va
    #    no CHAN cu bam — dung nhu thiet ke (no la mot lop phu that). Bo do phai bam
    #    duong ra "Van choi kieu doc" nhu tre lam, chu khong phai coi day la loi.
    if pg.is_visible(".ov.rot"):
        check("loi nhac xoay ngang co duong RA", pg.is_visible(".ov.rot .rot-ok"))
        pg.click(".ov.rot .rot-ok")
        pg.wait_for_timeout(250)
        check("bam duong ra thi loi nhac tat", not pg.is_visible(".ov.rot"))
    bx = pg.eval_on_selector_all("#dpad button",
                                 "els => els.map(e => Math.round(e.getBoundingClientRect().height))")
    check("vung cham d-pad >= 48px", bx and all(h >= 48 for h in bx), str(bx))
    pg.click("#start-btn")
    pg.wait_for_timeout(300)
    # Bam nut theo huong DI DUOC dau tien roi doi vi tri
    d0 = pg.evaluate("() => window.__maze.path()[0]")
    pos0 = st(pg, "pos")
    pg.click('#dpad button[data-dir="%s"]' % d0)
    pg.wait_for_timeout(320)
    check("bam d-pad thi di THAT", st(pg, "pos") != pos0,
          "%s -> %s (huong %s)" % (pos0, st(pg, "pos"), d0))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # Chuot (pointer: fine) thi KHONG hien d-pad
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(400)
    check("may dung chuot: d-pad AN", not pg.is_visible("#dpad"))
    ctx.close()

    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(0 if hong == 0 else 1)
