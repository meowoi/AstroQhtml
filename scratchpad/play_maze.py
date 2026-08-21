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
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-maze.html"

# ⚠️ PHI DOC TU CHINH FILE GAME, KHONG GHIM SO. Phi thay doi theo luat do kho
#    (15/08/2026: me cung 4 -> doc dong); ghim con so o day thi bo do bao hong
#    dung luc san pham lam dung — loi da lap nhieu lan trong du an.
COST = int(re.search(r"COST:\s*(\d+)",
                     io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game-maze.html"), encoding="utf-8").read()).group(1))

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


# CANH BAO: `cap` la BIEN AN TOAN, khong phai mot con so cho vui. Do ngay
#   21/08/2026 bang scratchpad/probe_maze_tour.py tren 100 me cung 27x15
#   (cap 4, co to nhat): `tour()` dai TB 396 buoc, MAX 584. Ban cu ghim
#   cap=600 -> bien chi ~3%. Muc [4] choi 30 luot, nen mot luot tour dai hon
#   600 la bot khong toi cong -> `#ov-over.show` het han cho, va no doc ra Y
#   NHU SAN PHAM HONG. Voi p~1%/luot thi ~26% moi lan chay bo bi hong — khop
#   dung ti le chap chon quan sat duoc (2/3 luot), va la chap chon CO SAN tu
#   14/08/2026 luc me cung len 4 cap, khong phai loi cua ban co duong ve cong.
#   Nay cap = 1600 (~2,7x max do duoc). ⚠️ Doi CONFIG.tiers cho me cung to hon
#   thi DO LAI bang probe_maze_tour.py TRUOC, dung doan.
def walk(pg, dirs, cap=1600):
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
        # ⚠️ Phai di theo `tour()` (ghe het tinh the roi ra cong), khong phai
        #    `path()`: tu 15/08/2026 cong CHI mo khi da thu het tinh the, nen
        #    di thang ra cong la luot khong bao gio ket thuc va bo do treo o
        #    `#start-btn` cua vong sau.
        walk(pg, pg.evaluate("() => window.__maze.tour()"))
        # ⚠️ CHO TIN HIEU THAT, dung ngu mot khoang co dinh: `.ov` co
        #    `transition: visibility .3s`, nen 60ms sau khi thang thi `#ov-over`
        #    van co the dang `visibility:hidden` -> vong sau bam nham `#start-btn`
        #    (dang an) va bo do treo 30 giay. Loi chap chon, kho lan ra.
        pg.wait_for_selector("#ov-over.show", timeout=6000)
    check("30/30 me cung co duong ra (0,0) → cong", solvable == 30, "%d/30" % solvable)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════ [2] Tru phi + [3] tuong chan that
    print("\n[2] Bat dau luot: tru dung %d tt, mot lan" % COST)
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(400)
    pg.click("#start-btn")
    pg.wait_for_timeout(300)
    check("vao 'play'", st(pg, "state") == "play", str(st(pg, "state")))
    check("tru dung dung phi mot lan", bal(pg) == 50 - COST,
          "%d (phi %d)" % (bal(pg), COST))
    pg.keyboard.press("Space")
    pg.wait_for_timeout(200)
    check("Space luc dang choi KHONG tru them", bal(pg) == 50 - COST, str(bal(pg)))
    # ⚠️ DOI PHAT BIEU 15/08/2026: me cung khong con MOT co co dinh ma co 4 cap
    #    (`CONFIG.tiers`). Cap dau van la 15x9; dieu can canh la "vao game o cap
    #    dang luu, dung co cua cap do" chu khong phai mot con so go cung.
    _t0 = st(pg, "tier")
    _cfg = st(pg, "cfg")["tiers"][_t0]
    check("vao dung co cua cap dang luu",
          st(pg, "cols") == _cfg["cols"] and st(pg, "rows") == _cfg["rows"],
          "cap %d -> %dx%d" % (_t0 + 1, st(pg, "cols"), st(pg, "rows")))
    check("cap dau tien la 15x9",
          st(pg, "cfg")["tiers"][0]["cols"] == 15 and st(pg, "cfg")["tiers"][0]["rows"] == 9,
          "%dx%d" % (st(pg, "cfg")["tiers"][0]["cols"], st(pg, "cfg")["tiers"][0]["rows"]))

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

    # ══════════════════════ [12] GIU PHIM = DI LIEN TUC (chua "giat cuc")
    #
    # ⚠️ PHEP DO NAY PHAN BIET DUOC BAN CU VOI BAN MOI, do la ly do no ton tai.
    #    Playwright KHONG gia lap nhip lap phim cua he dieu hanh: `keyboard.down`
    #    gui DUNG MOT `keydown`. Ban cu goi `tryMove` thang tu `keydown` nen giu
    #    phim = **dung 1 buoc**. Ban moi ghi huong dang giu roi vong lap game tu
    #    phat buoc ke tiep khi o truoc truot xong => nhieu buoc.
    #    (Voi nguoi that, nhip lap phim ~30ms khong khop nhip truot 108ms — do
    #     chinh la cam giac giat cuc chu du an bao.)
    print("\n[12] Giu phim thi di lien tuc, khong khung tung o")
    KEYMAP = {"up": "ArrowUp", "down": "ArrowDown", "left": "ArrowLeft", "right": "ArrowRight"}

    def find_corridor(pg, need=3, tries=30):
        """Di doc duong ra cho toi khi dung o cho co hanh lang thang >= `need` o.
        ⚠️ O goc xuat phat gan nhu khong bao gio co hanh lang dai — do ngay tai do
           la phep do TU BO QUA CHINH NO (lan dau chay ra {up:0,down:1,left:0,
           right:0} va bao hong oan). Me cung sinh ngau nhien nen phai DI TIM."""
        for _ in range(tries):
            runs = {d: pg.evaluate("(d) => window.__maze.freeRun(d)", d) for d in KEYMAP}
            d = max(runs, key=lambda k: runs[k])
            if runs[d] >= need:
                return d, runs
            nxt = pg.evaluate("() => window.__maze.path()[0]")
            if not nxt:
                return None, runs
            pg.evaluate("(d) => { window.__maze.snap(); window.__maze.move(d); "
                        "window.__maze.snap(); }", nxt)
        return None, runs

    d_best, runs = find_corridor(pg)
    check("tim duoc hanh lang >= 3 o de do", d_best is not None, str(runs))
    if d_best is None:
        d_best = "right"
    if d_best:
        s0 = st(pg, "steps")
        pg.keyboard.down(KEYMAP[d_best])
        pg.wait_for_timeout(420)          # 420ms / 108ms mot buoc => ~3-4 buoc
        pg.keyboard.up(KEYMAP[d_best])
        pg.wait_for_timeout(150)
        moved = st(pg, "steps") - s0
        check("giu phim 420ms thi di >= 3 o (ban cu chi 1)", moved >= 3,
              "%d o theo huong %s (hanh lang %d o)" % (moved, d_best, runs[d_best]))
        s1 = st(pg, "steps")
        pg.wait_for_timeout(300)
        check("nha phim thi DUNG han", st(pg, "steps") == s1,
              "%d -> %d" % (s1, st(pg, "steps")))
    # Mat tieu diem giua luc dang giu: khong nha het thi phi hanh gia chay mai
    pg.keyboard.down(KEYMAP[d_best])
    pg.evaluate("() => window.dispatchEvent(new Event('blur'))")
    pg.wait_for_timeout(250)
    s2 = st(pg, "steps")
    pg.wait_for_timeout(300)
    check("mat tieu diem thi nha het phim (khong chay mai)", st(pg, "steps") == s2,
          "%d -> %d" % (s2, st(pg, "steps")))
    pg.keyboard.up(KEYMAP[d_best])

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

    # ══════════ [5] CONG KHOA khi chua thu het tinh the
    #
    # ⚠️ DOI PHAT BIEU 15/08/2026 (chu du an chot). Truoc do cong ket thuc luot NGAY
    #    khi buoc vao, ke ca con tinh the — va do la luat co chu dich ("tre duoc
    #    quyen ra som va chiu gia"). Nay nhiem vu cua me cung la **thu bang het**
    #    roi moi ra. Dieu bo do bao ve doi theo: khong con la "ra som duoc khong"
    #    ma la "dung len cong khoa thi co bi bo mac im lang khong".
    print("\n[5] Cong KHOA: buoc vao khi chua du tinh the thi KHONG ket thuc")
    before = bal(pg)
    total_gems = st(pg, "gems")
    walk(pg, pg.evaluate("() => window.__maze.path()"))
    pg.wait_for_timeout(300)
    got_early = st(pg, "got")
    check("dung len cong khoa: luot VAN chay", st(pg, "state") == "play",
          "%d/%d tinh the · state=%s" % (got_early, total_gems, st(pg, "state")))
    check("chua thu du tinh the (phep do co nghia)", got_early < total_gems,
          "%d/%d" % (got_early, total_gems))
    check("vi KHONG bi tru/cong them gi", bal(pg) == before, str(bal(pg)))
    # ⚠️ Im lang o day la dung cai bay `#loader`: tre tuong game hong. Phai NOI ra
    #    con thieu may vien.
    check("co loi nhac noi ro con thieu may vien",
          pg.is_visible("#toast") and str(total_gems - got_early) in pg.inner_text("#toast"),
          pg.inner_text("#toast") if pg.is_visible("#toast") else "(khong co toast)")

    # ══════════ [5b] Thu HET tinh the roi moi ra → thuong CAO HON
    #
    # ⚠️ TRUOC 15/08/2026 khoi nay phai DI TIM mot me cung ma duong ghe-het-tinh-the
    #    khong di ngang qua cong — vi di ngang qua la luot ket thuc som. Nay cong
    #    khoa toi khi du tinh the nen di ngang qua no khong con nghia gi, va ca doan
    #    chon me cung da bo. Mot luat ro rang lam bo do ngan di.
    print("\n[5b] Thu HET tinh the roi ra cong: ve dich + len cap")
    gems_n = st(pg, "gems")
    tier0 = int(pg.evaluate("() => localStorage.getItem('astroq-maze-tier') || 0"))
    b0 = bal(pg)
    walk(pg, pg.evaluate("() => window.__maze.tour()"))
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

    # ── [5c] LEN CAP: giai xong thi lan sau me cung TO HON ──
    # ⚠️ Day la thu giu cho ho so huan luyen con nghia. Tu khi bat buoc thu het tinh
    #    the, so tinh the la HANG SO, nen thang cap phai dua vao CO me cung. Neu phep
    #    kiem nay do thi `Services/Training.cs` dang do mot thu khong bao gio doi.
    print("\n[5c] Giai xong thi len cap: me cung sau TO HON")
    tier1 = int(pg.evaluate("() => localStorage.getItem('astroq-maze-tier') || 0"))
    check("cap tang sau khi giai", tier1 == tier0 + 1, "%d -> %d" % (tier0, tier1))
    cols0 = pg.evaluate("() => window.__maze.cfg.tiers[%d].cols" % tier0)
    pg.evaluate("() => localStorage.setItem('astroq-asteroids','50')")
    pg.click("#again-btn")
    pg.wait_for_timeout(200)
    check("me cung moi RONG hon me cung vua giai",
          st(pg, "cols") > cols0, "%d -> %d o ngang" % (cols0, st(pg, "cols")))
    check("so tinh the cung tang theo cap", st(pg, "gems") > gems_n,
          "%d -> %d" % (gems_n, st(pg, "gems")))
    # Ket thuc luot vua mo de khoi [9] doc duoc bang ket qua (khoi do doi chu tren
    # chinh bang do — dang choi thi khong co gi de doc).
    walk(pg, pg.evaluate("() => window.__maze.tour()"))
    pg.wait_for_selector("#ov-over.show", timeout=6000)
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
    ctx, pg = mk(br, bal=COST - 1)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(400)
    pg.click("#start-btn")
    pg.wait_for_timeout(300)
    check("hien man 'chua du tt'", pg.is_visible("#ov-need"))
    check("KHONG tru tien", bal(pg) == COST - 1, str(bal(pg)))
    check("van o 'start'", st(pg, "state") == "start", str(st(pg, "state")))
    body = pg.inner_text("#need-body")
    check("noi ro can bao nhieu va dang co bao nhieu",
          str(COST) in body and str(COST - 1) in body, body[:70])
    ctx.close()

    # ═══════════════════ [7][10] Hinh hoc + dien thoai
    print("\n[7] O vuong, me cung nam trong san")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)
    geo = pg.evaluate("""() => {
        const cfg = window.__maze.cfg;
        // Suy lai dung phep tinh cua trang: o VUONG, me cung can giua san 800x500.
        // ⚠️ Do o CAP TO NHAT — do la ca kho nhat: o nho nhat va me cung rong nhat.
        //    Cap nao cung phai nam tron trong san, khong chi cap dau.
        const T = cfg.tiers[cfg.tiers.length - 1];
        const pad = 26;
        const cell = Math.floor(Math.min((cfg.VW - pad*2)/T.cols, (cfg.VH - pad*2)/T.rows));
        return { cell, w: cell*T.cols, h: cell*T.rows, VW: cfg.VW, VH: cfg.VH };
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
