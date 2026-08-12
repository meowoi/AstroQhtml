"""play_catch.py — BAT SAO BANG (ARCADE-06) choi THAT tren Chromium.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/play_catch.py

Do nhung thu doc code KHONG chung minh duoc:
  [1] man brief: chua tru tien, nut Pause an, sfx bam duoc
  [2] tru DUNG 3 tt MOT lan (khong hai lan khi bam Space)
  [3] hung sao vang → diem tang · sao tim → +1 tt vao VI TAM (chua vao vi chinh)
  [4] cham sao chua lua → mat 1 mang, chuoi ve 0
  [5] het 3 mang → bang ket qua, vi chinh MOI cong tt
  [6] tam dung: dong ho + vat the DUNG HAN
  [7] thieu tt → KHONG tru tien, dan sang Quiz
  [8] doi VI/EN dich ca dong thuong do JS sinh
  [9] dien thoai 390x844: giu ti le 8:5, khong tran ngang
 [10] he toa do ao: doi co man KHONG doi luat choi (vi tri gio quy ve 800x500)

⚠️ Ghim `astroq-lang` (Chromium mac dinh en-US, mui gio khong phai VN).
⚠️ Bo do lai game qua `window.__catch` — be mat CHI doc trang thai va gieo vat the
   o vi tri xac dinh. No KHONG cap diem, KHONG cap thuong (bai hoc `__dbg` cua
   ARCADE-02): mot be mat test cap thuong duoc thi phep kiem "thuong dung" vo nghia.
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-catch.html"
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
        "localStorage.setItem('astroq-catch-best','0');"
        "localStorage.setItem('astroq-user', JSON.stringify("
        "{name:'Nhi',pilotName:'Nhi',uid:'u-test',character:'m',avatar:'ava/avam.png'}));"
        % (lang, bal))
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    return ctx, pg


def st(pg, k):
    return pg.evaluate("(k) => window.__catch[k]", k)


def bal(pg):
    return pg.evaluate("() => Number(localStorage.getItem('astroq-asteroids')||0)")


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ═══════════════════════════════════════════ [1] Man brief
    print("\n[1] Man brief")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)
    check("be mat test co that", pg.evaluate("() => !!window.__catch"))
    check("trang thai la 'start'", st(pg, "state") == "start", str(st(pg, "state")))
    check("CHUA tru tien o man brief", bal(pg) == 50, str(bal(pg)))
    check("nut Pause dang AN (bam luc nay vo nghia)",
          "is-hidden" in (pg.get_attribute("#btn-pause", "class") or ""))
    check("nut am thanh bam duoc (khong bi overlay che)",
          pg.evaluate("""() => {
            const b = document.getElementById('btn-sfx');
            const r = b.getBoundingClientRect();
            const el = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);
            return !!(el && (el === b || b.contains(el)));
          }"""))
    check("tag ten game dich theo ngon ngu",
          "bắt sao băng" in pg.inner_text("#gtag").casefold(), pg.inner_text("#gtag"))

    # ═══════════════════════════════════ [2] Tru phi DUNG MOT lan
    print("\n[2] Bat dau luot: tru dung 3 tt, mot lan")
    pg.click("#start-btn")
    pg.wait_for_timeout(400)
    check("vao trang thai 'play'", st(pg, "state") == "play", str(st(pg, "state")))
    check("tru dung 3 tt", bal(pg) == 47, str(bal(pg)))
    check("nut Pause hien ra", "is-hidden" not in (pg.get_attribute("#btn-pause", "class") or ""))
    # Space khi dang choi KHONG duoc tru them lan nua
    pg.keyboard.press("Space")
    pg.wait_for_timeout(250)
    check("Space luc dang choi KHONG tru them", bal(pg) == 47, str(bal(pg)))

    # ═════════════════════════ [3] Hung sao vang / sao tim
    print("\n[3] Hung sao: diem tang, sao tim cho tt vao VI TAM")
    pg.evaluate("() => window.__catch.clear()")
    sc0 = st(pg, "score")
    pg.evaluate("() => window.__catch.drop('star', 0)")
    pg.wait_for_timeout(700)
    check("hung sao vang thi DIEM tang", st(pg, "score") > sc0,
          "%d -> %d" % (sc0, st(pg, "score")))
    check("chuoi tang len 1", st(pg, "combo") >= 1, str(st(pg, "combo")))

    m0, b0 = st(pg, "mined"), bal(pg)
    pg.evaluate("() => window.__catch.drop('gem', 0)")
    pg.wait_for_timeout(700)
    check("hung sao tim thi +1 tt vao vi TAM", st(pg, "mined") == m0 + 1,
          "%d -> %d" % (m0, st(pg, "mined")))
    check("vi CHINH chua doi trong luot (chot mot lan cuoi luot)", bal(pg) == b0,
          "%d -> %d" % (b0, bal(pg)))
    check("HUD hien so tt dang thu", pg.inner_text("#hb-mtr") == str(st(pg, "mined")),
          pg.inner_text("#hb-mtr"))

    # ═══════════════════════════ [4] Sao chua lua: mat mang
    print("\n[4] Cham sao chua lua: mat 1 mang, chuoi ve 0")
    lv0 = st(pg, "lives")
    pg.evaluate("() => window.__catch.drop('bad', 0)")
    pg.wait_for_timeout(700)
    check("mat dung 1 mang", st(pg, "lives") == lv0 - 1, "%d -> %d" % (lv0, st(pg, "lives")))
    check("chuoi ve 0", st(pg, "combo") == 0, str(st(pg, "combo")))
    hearts = pg.evaluate("() => document.querySelectorAll('#hb-lives i.on').length")
    check("HUD ve dung so trai tim con lai", hearts == st(pg, "lives"),
          "%d trai tim / %d mang" % (hearts, st(pg, "lives")))
    total_hearts = pg.evaluate("() => document.querySelectorAll('#hb-lives i').length")
    check("mat mang thi trai tim MO DI, khong bien mat (HUD khong nhay cho)",
          total_hearts == 3, "%d trai tim tren HUD" % total_hearts)

    # ═════════════════════ [6] Tam dung: moi thu DUNG HAN
    print("\n[6] Tam dung thi vat the dung han")
    pg.evaluate("() => window.__catch.clear()")
    pg.evaluate("() => window.__catch.drop('star', 200)")
    pg.wait_for_timeout(120)
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(300)
    check("vao trang thai 'paused'", st(pg, "state") == "paused", str(st(pg, "state")))
    n1 = st(pg, "drops")
    sc1 = st(pg, "score")
    pg.wait_for_timeout(1200)
    check("so vat the KHONG doi khi tam dung", st(pg, "drops") == n1,
          "%d -> %d" % (n1, st(pg, "drops")))
    check("diem KHONG doi khi tam dung", st(pg, "score") == sc1)
    pg.click("#resume-btn")
    pg.wait_for_timeout(250)
    check("bam Choi tiep thi chay lai", st(pg, "state") == "play", str(st(pg, "state")))

    # ═══════════════ [5] Het mang → bang ket qua + cong vi
    print("\n[5] Het 3 mang: bang ket qua, vi chinh moi cong tt")
    mined = st(pg, "mined")
    before = bal(pg)
    while st(pg, "lives") > 0 and st(pg, "state") == "play":
        pg.evaluate("() => { window.__catch.clear(); window.__catch.drop('bad', 0); }")
        pg.wait_for_timeout(650)
    pg.wait_for_timeout(500)
    check("het mang → trang thai 'over'", st(pg, "state") == "over", str(st(pg, "state")))
    check("bang ket qua hien ra", pg.is_visible("#ov-over"))
    check("vi chinh cong DUNG so tt da thu", bal(pg) == before + mined,
          "%d + %d = %d" % (before, mined, bal(pg)))
    check("bang ket qua ghi dung so tt", pg.inner_text("#r-mtr") == str(mined),
          pg.inner_text("#r-mtr"))
    check("nut Pause an lai o bang ket qua",
          "is-hidden" in (pg.get_attribute("#btn-pause", "class") or ""))
    if mined > 0:
        check("co dong 'da cong n tt vao vi'", pg.is_visible("#paid")
              and str(mined) in pg.inner_text("#paid"), pg.inner_text("#paid")[:60])
    check("ky luc luu lai",
          pg.evaluate("() => Number(localStorage.getItem('astroq-catch-best')||0)") > 0)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))

    # ═══════════════════════ [8] Doi VI/EN o bang ket qua
    print("\n[8] Doi ngon ngu o bang ket qua")
    pg.click(".lang-switch [data-lang='en']")
    pg.wait_for_timeout(400)
    check("tieu de bang ket qua dich", "Run over" in pg.inner_text("#ov-over"),
          pg.inner_text("h2")[:40])
    if mined > 0:
        check("dong thuong (do JS sinh) CUNG dich",
              "added to your wallet" in pg.inner_text("#paid"), pg.inner_text("#paid")[:60])
    check("tag ten game dich", "star catcher" in pg.inner_text("#gtag").casefold(),
          pg.inner_text("#gtag"))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═══════════════════════════════ [7] Thieu tt
    print("\n[7] Thieu Thien thach tim")
    ctx, pg = mk(br, bal=2)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(400)
    pg.click("#start-btn")
    pg.wait_for_timeout(400)
    check("hien man 'chua du tt'", pg.is_visible("#ov-need"))
    check("KHONG tru tien khi khong du", bal(pg) == 2, str(bal(pg)))
    check("van o trang thai 'start'", st(pg, "state") == "start", str(st(pg, "state")))
    body = pg.inner_text("#need-body")
    check("noi ro can bao nhieu va dang co bao nhieu", "3" in body and "2" in body, body[:70])
    check("co duong sang Quiz", pg.is_visible("#need-quiz"))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════ [9][10] Dien thoai + he toa do ao
    print("\n[9] Dien thoai 390x844")
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
    pg.wait_for_timeout(400)
    check("choi duoc tren dien thoai", st(pg, "state") == "play", str(st(pg, "state")))

    print("\n[10] He toa do ao: luat choi KHONG doi theo co man")
    # Gio nam trong he 800x500 → vi tri KHONG phu thuoc so pixel that cua canvas.
    pg.evaluate("() => window.__catch.moveTo(400)")
    pg.wait_for_timeout(120)
    x_mobile = st(pg, "shipX")
    w_mobile = pg.evaluate("() => document.getElementById('cv').getBoundingClientRect().width")
    cfg_vw = pg.evaluate("() => window.__catch.cfg.VW")
    check("he toa do ao la 800", cfg_vw == 800, str(cfg_vw))
    check("gio dat dung 400 trong he ao (khong theo pixel man)", abs(x_mobile - 400) < 1,
          "shipX=%.1f, canvas rong %.0fpx" % (x_mobile, w_mobile))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(0 if hong == 0 else 1)
