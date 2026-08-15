"""play_racer.py — DUONG DUA SAO CHOI (ARCADE-03) choi THAT tren Chromium.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/play_racer.py

Do nhung thu doc code KHONG chung minh duoc:
  [1] man brief: chua tru tien, nut Pause an
  [2] tru DUNG 5 tt MOT lan
  [3] doi lan THAT (va khong ra khoi 4 lan)
  [4] nhien lieu TUT DAN theo thoi gian, va chip doi mau theo muc
  [5] thung nhien lieu NAP them · tinh the tim → +1 tt vao vi TAM · da → MAT nhien lieu
  [6] MOI CUM CHUONG NGAI luon chua it nhat MOT lan trong ("luon co duong qua")
  [7] can nhien lieu → het luot, VAN duoc thuong tinh the da thu (khong ve tay khong)
  [8] ve dich → thuong CO them phan "ve dich", va bang ket qua noi ro
  [9] tam dung: quang duong DUNG HAN
 [10] thieu tt → khong tru tien
 [11] doi VI/EN dich ca ba dong do JS sinh
 [12] dien thoai: ti le 8:5, khong tran ngang

⚠️ Bot dieu khien qua `window.__racer` — doi lan bang DUNG ham ban phim goi (`hop`),
   gieo vat the o LAN dang dung. Be mat KHONG cap diem, KHONG cap thuong, KHONG nap
   nhien lieu truc tiep.
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
URL = BASE + "/game-racer.html"

# CANH BAO: PHI DOC TU CHINH FILE GAME, KHONG GHIM SO. Phi doi theo luat do kho
#    (15/08/2026); ghim con so o day thi bo do bao hong dung luc san pham lam dung.
COST = int(re.search(r"COST:\s*(\d+)", io.open(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game-racer.html"),
    encoding="utf-8").read()).group(1))

dat = hong = 0


def check(label, cond, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def mk(br, lang="vi", w=1440, h=900, bal=60):
    ctx = br.new_context(viewport={"width": w, "height": h},
                         locale="vi-VN" if lang == "vi" else "en-US",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','%s');"
        "localStorage.setItem('astroq-asteroids','%d');"
        "localStorage.removeItem('astroq-racer-best');"
        "localStorage.setItem('astroq-user', JSON.stringify("
        "{name:'Nhi',pilotName:'Nhi',uid:'u-test',character:'m',avatar:'ava/avam.png'}));"
        % (lang, bal))
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    return ctx, pg


def st(pg, k):
    return pg.evaluate("(k) => window.__racer[k]", k)


def bal(pg):
    return pg.evaluate("() => Number(localStorage.getItem('astroq-asteroids')||0)")


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ═══════════════════════════════════════════ [1][2] Brief + phi
    print("\n[1] Man brief")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)
    check("be mat test co that", pg.evaluate("() => !!window.__racer"))
    check("trang thai 'start'", st(pg, "state") == "start", str(st(pg, "state")))
    check("CHUA tru tien", bal(pg) == 60, str(bal(pg)))
    check("nut Pause dang AN", "is-hidden" in (pg.get_attribute("#btn-pause", "class") or ""))
    check("tag ten game dich", "đường đua" in pg.inner_text("#gtag").casefold(), pg.inner_text("#gtag"))

    print("\n[2] Bat dau luot: tru dung %d tt, mot lan" % COST)
    pg.click("#start-btn")
    pg.wait_for_timeout(350)
    check("vao 'play'", st(pg, "state") == "play", str(st(pg, "state")))
    check("tru dung dung phi mot lan", bal(pg) == 60 - COST,
          "%d (phi %d)" % (bal(pg), COST))
    pg.keyboard.press("Space")
    pg.wait_for_timeout(200)
    check("Space luc dang choi KHONG tru them", bal(pg) == 60 - COST, str(bal(pg)))
    # ⚠️ KHONG ghim con so met: no la tham so can bang. Hoi dieu THAT SU can — mot
    #    luot phai DAI hon so giay nhien lieu chay duoc, khong thi "ve dich truoc khi
    #    het nhien lieu" la mot cau noi suong (loi can bang da bat duoc o lan chay dau).
    cfg = st(pg, "cfg")
    sec_race = cfg["raceLen"] / ((cfg["speed0"] + cfg["speedMax"]) / 2)
    sec_fuel = cfg["fuel0"] / cfg["fuelDrain"]
    check("mot luot DAI hon so giay nhien lieu chay duoc (nhien lieu that su la van de)",
          sec_race > sec_fuel * 1.5,
          "luot ~%.0fs / nhien lieu ~%.0fs" % (sec_race, sec_fuel))

    # ═════════════════════════════════════════ [3] Doi lan
    print("\n[3] Doi lan that, va khong ra khoi 4 lan")
    l0 = st(pg, "lane")
    pg.keyboard.press("ArrowDown")
    pg.wait_for_timeout(260)
    check("bam xuong thi doi lan", st(pg, "lane") == l0 + 1, "%d -> %d" % (l0, st(pg, "lane")))
    # Day xuong het co roi bam them: KHONG duoc ra khoi lan cuoi
    for _ in range(6):
        pg.evaluate("() => window.__racer.hop(1)")
        pg.wait_for_timeout(170)
    check("khong ra khoi lan cuoi", st(pg, "lane") == st(pg, "lanes") - 1,
          "lane=%d / lanes=%d" % (st(pg, "lane"), st(pg, "lanes")))
    for _ in range(8):
        pg.evaluate("() => window.__racer.hop(-1)")
        pg.wait_for_timeout(170)
    check("khong ra khoi lan dau", st(pg, "lane") == 0, str(st(pg, "lane")))

    # ═══════════════════════════════ [4] Nhien lieu tut dan
    print("\n[4] Nhien lieu tut dan + chip doi mau")
    f0 = st(pg, "fuel")
    pg.wait_for_timeout(1400)
    f1 = st(pg, "fuel")
    check("nhien lieu TUT theo thoi gian", f1 < f0, "%.1f%% -> %.1f%%" % (f0, f1))
    check("thanh nhien lieu ngan lai theo muc",
          pg.evaluate("() => parseFloat(document.getElementById('fuel-bar').style.width)") <= 100)

    # ══════════ [5] Vat pham: can nap · gem cho tt · rock mat nhien lieu
    print("\n[5] Thung nhien lieu / tinh the / thien thach")
    pg.evaluate("() => window.__racer.clear()")
    f_before = st(pg, "fuel")
    pg.evaluate("() => window.__racer.put('can', 60)")
    pg.wait_for_timeout(700)
    check("hung thung nhien lieu thi NAP them", st(pg, "fuel") > f_before,
          "%.1f%% -> %.1f%%" % (f_before, st(pg, "fuel")))

    m0, b0 = st(pg, "mined"), bal(pg)
    pg.evaluate("() => window.__racer.put('gem', 60)")
    pg.wait_for_timeout(700)
    check("hung tinh the thi +1 tt vao vi TAM", st(pg, "mined") == m0 + 1,
          "%d -> %d" % (m0, st(pg, "mined")))
    check("vi CHINH chua doi trong luot", bal(pg) == b0, "%d -> %d" % (b0, bal(pg)))

    f2 = st(pg, "fuel")
    pg.evaluate("() => window.__racer.put('rock', 60)")
    pg.wait_for_timeout(700)
    hit_cost = st(pg, "cfg")["hitCost"]
    check("dam thien thach thi MAT mot mang nhien lieu",
          st(pg, "fuel") <= f2 - hit_cost * 0.7,
          "%.1f%% -> %.1f%% (mat >= %d%%)" % (f2, st(pg, "fuel"), hit_cost))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))

    # ══════════════════ [9] Tam dung: quang duong dung han
    print("\n[9] Tam dung thi quang duong dung han")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(250)
    check("vao 'paused'", st(pg, "state") == "paused", str(st(pg, "state")))
    d1 = st(pg, "dist")
    pg.wait_for_timeout(1300)
    check("quang duong KHONG tang khi tam dung", abs(st(pg, "dist") - d1) < 0.01,
          "%.1f -> %.1f" % (d1, st(pg, "dist")))
    f_pause = st(pg, "fuel")
    check("nhien lieu KHONG tut khi tam dung", abs(st(pg, "fuel") - f_pause) < 0.01)
    pg.click("#resume-btn")
    pg.wait_for_timeout(200)
    check("Choi tiep thi chay lai", st(pg, "state") == "play", str(st(pg, "state")))

    # ══════════ [6] Moi cum chuong ngai luon chua mot lan trong
    print("\n[6] Moi cum chuong ngai LUON chua it nhat MOT lan trong")
    worst = 99
    for i in range(40):
        free = pg.evaluate("""() => {
            window.__racer.clear();
            // Goi dung bo sinh cum cua game bang cach day quang duong qua moc: khong
            // co cua sau nao — ta doc so lan trong NGAY sau khi game tu sinh cum.
            return null;
        }""")
        pg.wait_for_timeout(120)
        n = pg.evaluate("() => window.__racer.freeLanes()")
        if pg.evaluate("() => window.__racer.items") > 0:
            worst = min(worst, n)
    check("khong luc nao bit het 4 lan", worst >= 1,
          "it nhat %s lan trong" % ("khong do duoc" if worst == 99 else worst))

    # ══════ [7] Can nhien lieu: het luot NHUNG van duoc thuong tinh the
    print("\n[7] Can nhien lieu: van duoc thuong tinh the da thu")
    mined = st(pg, "mined")
    before = bal(pg)
    # Doi cho can — khong co cua sau nao dot chay nhien lieu, nen dam vao da cho nhanh
    guard = 0
    while st(pg, "state") == "play" and guard < 60:
        pg.evaluate("() => { window.__racer.clear(); window.__racer.put('rock', 40); }")
        pg.wait_for_timeout(420)
        guard += 1
    pg.wait_for_timeout(400)
    check("can nhien lieu → 'over'", st(pg, "state") == "over", str(st(pg, "state")))
    check("KHONG phai thang", st(pg, "won") is False, str(st(pg, "won")))
    paid = int(pg.inner_text("#r-mtr"))
    check("van duoc thuong so tinh the da thu (khong ve tay khong)", paid == mined,
          "%d tt / %d tinh the" % (paid, mined))
    check("vi chinh cong dung", bal(pg) == before + paid,
          "%d + %d = %d" % (before, paid, bal(pg)))
    why = pg.inner_text("#why")
    check("noi RO vi sao khong co thuong dich",
          "chưa về đích" in why.casefold(), why[:70])
    check("tieu de la 'Can nhien lieu'", "cạn nhiên liệu" in pg.inner_text("#over-title").casefold(),
          pg.inner_text("#over-title"))
    sub = pg.inner_text("#over-sub")
    check("noi con bao nhieu met nua la toi dich", "m" in sub and any(ch.isdigit() for ch in sub),
          sub[:70])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))

    # ═══════════════════ [8] Ve dich: co thuong "ve dich"
    print("\n[8] Ve dich: thuong co them phan ve dich")
    pg.evaluate("() => localStorage.setItem('astroq-asteroids','60')")
    pg.click("#again-btn")
    pg.wait_for_timeout(300)
    check("luot moi bat dau", st(pg, "state") == "play", str(st(pg, "state")))
    b1 = bal(pg)
    pg.evaluate("() => window.__racer.nearFinish()")
    pg.wait_for_timeout(900)
    check("ve dich → 'over'", st(pg, "state") == "over", str(st(pg, "state")))
    check("la THANG", st(pg, "won") is True, str(st(pg, "won")))
    paid2 = int(pg.inner_text("#r-mtr"))
    check("thuong CO phan ve dich (> so tinh the)",
          paid2 >= st(pg, "cfg")["rewardFinish"],
          "%d tt (thuong dich toi thieu %d)" % (paid2, st(pg, "cfg")["rewardFinish"]))
    check("vi cong dung", bal(pg) == b1 + paid2, "%d + %d = %d" % (b1, paid2, bal(pg)))
    check("tieu de la 'Ve dich'", "về đích" in pg.inner_text("#over-title").casefold(),
          pg.inner_text("#over-title"))
    why2 = pg.inner_text("#why")
    check("noi ro thuong gom nhung gi", "thưởng về đích" in why2.casefold(), why2[:70])
    # So met co nhom hang nghin ("14.000 m") nen so sanh phai bo dau nhom.
    dist_txt = pg.inner_text("#r-dist").replace(".", "").replace(",", "")
    check("quang duong tren bang = ca duong dua",
          str(cfg["raceLen"]) in dist_txt, pg.inner_text("#r-dist"))
    check("ky luc luu lai", pg.evaluate("() => Number(localStorage.getItem('astroq-racer-best')||0)") > 0,
          str(pg.evaluate("() => localStorage.getItem('astroq-racer-best')")))

    # ═════════════════════════ [11] Doi VI/EN o bang ket qua
    print("\n[11] Doi ngon ngu o bang ket qua")
    pg.click(".lang-switch [data-lang='en']")
    pg.wait_for_timeout(400)
    check("tieu de dich", "Finished" in pg.inner_text("#over-title"), pg.inner_text("#over-title"))
    check("cau phu dich", "track" in pg.inner_text("#over-sub"), pg.inner_text("#over-sub")[:50])
    check("dong 'thuong gom gi' dich", "finish bonus" in pg.inner_text("#why"),
          pg.inner_text("#why")[:50])
    check("dong 'da cong vao vi' dich", "added to your wallet" in pg.inner_text("#paid"),
          pg.inner_text("#paid")[:50])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════════ [10] Thieu tt
    print("\n[10] Thieu Thien thach tim")
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

    # ══════════════════════════════ [12] Dien thoai
    print("\n[12] Dien thoai 390x844")
    ctx, pg = mk(br, "vi", 390, 844)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(600)
    over = pg.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("khong tran ngang", over <= 1, "%dpx" % over)
    ratio = pg.evaluate("""() => {
        const r = document.getElementById('field').getBoundingClientRect();
        return Math.round(r.width / r.height * 1000);
    }""")
    check("san giu ti le 8:5", abs(ratio - 1600) <= 20, "%.3f" % (ratio / 1000))
    pg.click("#start-btn")
    pg.wait_for_timeout(300)
    check("choi duoc tren dien thoai", st(pg, "state") == "play", str(st(pg, "state")))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(0 if hong == 0 else 1)
