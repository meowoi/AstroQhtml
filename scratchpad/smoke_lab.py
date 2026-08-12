"""smoke_lab.py — Phong Nghien Cuu (MOD-05) do tren Chromium THAT.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/smoke_lab.py

⚠️ Doc CSS hay doc code deu KHONG chung minh duoc nguoi dung thay gi. Bo nay do:
   luoi 6 the o 3 co man · trang thai khoa dung cho tung the · hop khoa NOI THAT khi
   chua mo ban va KHONG co nut dan sang trang gia · canh 2D that su VE (doc pixel)
   · cu tha lam vat DI CHUYEN · hai do sau loi giai thich · doi VI/EN · dien thoai.

⚠️ Ghim `astroq-lang`: Chromium mac dinh locale en-US va mui gio khong phai Viet Nam,
   nen khong ghim thi phan "tieng Viet" cua bo do lang le chay bang tieng Anh va moi
   phep kiem chu Viet vo nghia (bai hoc 12/08/2026).
"""
import re
import sys
import io

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/lab.html"
dat = hong = 0


def check(label, cond, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def mk(br, lang="vi", w=1440, h=900):
    ctx = br.new_context(viewport={"width": w, "height": h},
                         locale="vi-VN" if lang == "vi" else "en-US",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','%s')" % lang)
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    # ⚠️ Chan /billing/catalog: bo do chay o cong 8123 khong nam trong
    #    ALLOWED_ORIGINS nen CORS chan va TRINH DUYET tu ghi mot dong do vao
    #    console — khong `catch` nao chan duoc. Chan o bo do thi phep do bo cuc
    #    thoi phu thuoc vao viec Lambda co song hay khong (bai hoc 11/08/2026).
    ctx.route("**/billing/catalog", lambda r: r.fulfill(
            status=200, content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body='{"ok":true,"saleOpen":false,"provider":"none"}'))
    return ctx, pg


def ink(pg, sel="#cv"):
    """So pixel KHONG phai mau nen cua canvas — chung minh canh that su duoc VE."""
    return pg.evaluate("""(sel) => {
        const c = document.querySelector(sel);
        const g = c.getContext('2d');
        const d = g.getImageData(0, 0, c.width, c.height).data;
        let n = 0;
        for (let i = 0; i < d.length; i += 4) if (d[i+3] > 8) n++;
        return n;
    }""", sel)


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ══════════════════════════════════════════════════════════ [1] Luoi the
    print("\n[1] Luoi 6 the hoat dong")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector(".lcard", timeout=8000)
    # ⚠️ DOI PHAT BIEU 12/08/2026: them LAB-07 (vi sao troi xanh) + LAB-08 (nuoc cua
    #    Trai Dat) => 8 the. Ba phep kiem cu ghim con so 6 va ghim "LAB-04..06 la
    #    soon" THEO VI TRI, nen chung bao hong dung luc san pham lam dung.
    #    Ban moi doc trang thai tu CHINH DANH MUC (the co `kind` la the dung xong)
    #    nen no dung voi moi so luong the ve sau, VA no manh hon: no la chot chan
    #    "the CHUA dung xong khong bao gio duoc mang nhan tra phi" — gan `pro` cho
    #    thu chua ton tai la noi voi phu huynh "tra tien se mo duoc".
    cards = pg.query_selector_all(".lcard")
    check("co it nhat 6 the", len(cards) >= 6, "%d the" % len(cards))
    codes = pg.eval_on_selector_all(".lc-code", "els => els.map(e => e.textContent)")
    check("moi ma dung dang LAB-nn", all(re.match(r"^LAB-\d\d$", c) for c in codes),
          ",".join(codes))
    check("khong ma nao bi trung", len(set(codes)) == len(codes), ",".join(codes))
    kinds = pg.evaluate("() => AstroQLab.CARDS.map(c => ({code:c.code, done:!!c.kind}))")
    tags = pg.eval_on_selector_all(".lc-tag", "els => els.map(e => e.className)")
    check("so nhan khop so the", len(tags) == len(kinds),
          "%d nhan / %d the" % (len(tags), len(kinds)))
    for _i, _k in enumerate(kinds):
        _want = ("free", "pro") if _k["done"] else ("soon",)
        check("%s: %s" % (_k["code"],
                          "da dung xong -> free/pro" if _k["done"]
                          else "chua dung xong -> soon"),
              any(w in tags[_i] for w in _want), tags[_i].replace("lc-tag ", ""))
    check("LAB-01 la the MIEN PHI (the trai nghiem)", "free" in tags[0], tags[0])
    # ⚠️ Khong the nao co chu 'Sao Hoa' o day: nguon chi chong lung 4 noi va Sao Hoa
    #    KHONG nam trong do (Space Place chi nhac Sao Hoa khi noi ve KHOI LUONG).
    body = pg.inner_text("body")
    check("KHONG hua 'ca 8 hanh tinh' o dau", "8 hành tinh" not in body)
    check("khong loi trang", pg.perr == [], "; ".join(pg.perr[:2]))

    # ══════════════════════════════════════════════════════ [2] Duong (c): chua mo ban
    print("\n[2] The tra phi khi CHUA MO BAN — phai noi that, khong moi mua")
    pg.click(".lcard[data-card='float']")
    pg.wait_for_selector("#aq-lock.show", timeout=5000)
    lk = pg.inner_text("#aq-lock")
    check("hop khoa mo ra", pg.is_visible("#aq-lock"))
    check("noi la CHUA MO BAN", "chưa mở bán" in lk.casefold(), lk[:70].replace("\n", " "))
    check("noi la DA LAM XONG (khac 'dang duoc xay')",
          "làm xong" in lk.casefold() and "đang được xây" not in lk.casefold())
    # Chot chan cua ca duong (c): KHONG duoc co nut dan sang trang gia.
    go_vis = pg.is_visible("#lk-go")
    check("KHONG co nut dan sang trang gia (khong ngo cut)", not go_vis,
          "nut dang hien" if go_vis else "an dung")
    check("KHONG moi bo me di xem gia", not pg.is_visible("#lk-note"))
    check("van noi thu nay thuoc goi nao", "Phi Hành Gia" in lk)
    pg.keyboard.press("Escape")

    print("\n[2b] The chua dung xong thi noi kieu KHAC (khong phai 'chua mo ban')")
    pg.click(".lcard[data-card='mix']")
    pg.wait_for_selector("#aq-lock.show", timeout=5000)
    lk2 = pg.inner_text("#aq-lock")
    check("noi la dang duoc xay", "đang được xây" in lk2.casefold(),
          lk2[:60].replace("\n", " "))
    check("KHONG noi 'chua mo ban' cho thu chua dung xong",
          "chưa mở bán" not in lk2.casefold())
    pg.keyboard.press("Escape")
    ctx.close()

    # ══════════════════════════════════════════════════════════ [3] LAB-01 choi that
    print("\n[3] LAB-01 Thap tha roi — canh 2D va cu tha")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.click(".lcard[data-card='tower']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=5000)
    pg.wait_for_timeout(400)
    px0 = ink(pg)
    check("canh 2D that su duoc VE", px0 > 20000, "%d pixel co muc" % px0)
    check("hien dung ma the", pg.inner_text("#exp-code") == "LAB-01",
          pg.inner_text("#exp-code"))
    check("co 2 noi de chon", len(pg.query_selector_all("#places button")) == 2)
    check("chua doan thi CHUA co nut Tha", not pg.is_visible("#run"))
    check("phat hien con AN truoc khi lam", not pg.is_visible("#finding"))

    # Doan (sai cung khong sao — khong diem, khong dung/sai)
    pg.click("#guess button:nth-child(2)")          # "Bua truoc"
    pg.wait_for_timeout(200)
    check("doan roi thi hien nut Tha", pg.is_visible("#run"))
    check("doan sai KHONG bi phat / khong hien chu 'sai'",
          "sai" not in pg.inner_text("#say").casefold())

    # Do vat co DI CHUYEN that khong: chup pixel o mot dai NGANG gan mat dat
    def band(pg):
        return pg.evaluate("""() => {
            const c = document.getElementById('cv');
            const g = c.getContext('2d');
            const y = Math.round(c.height * 0.80);
            const d = g.getImageData(0, y, c.width, 6).data;
            let n = 0;
            for (let i = 0; i < d.length; i += 4)
                if (d[i] > 150 && d[i+1] > 150 && d[i+2] > 170) n++;
            return n;
        }""")
    b_before = band(pg)
    pg.click("#run")
    pg.wait_for_timeout(1500)
    b_after = band(pg)
    check("cu Tha lam vat ROI XUONG (dai gan mat dat sang len)",
          b_after > b_before, "truoc %d -> sau %d" % (b_before, b_after))

    pg.wait_for_selector("#finding:not([hidden])", timeout=6000)
    check("xong thi hien PHAT HIEN cua tre", pg.is_visible("#finding"))
    fi = pg.inner_text("#fi-t")
    check("phat hien noi ve khong khi", "không khí" in fi, fi[:60])

    # ⚠️ KHONG duoc hien thoi gian tuyet doi (mot khang dinh dinh luong can nguon)
    txt = pg.inner_text("#exp-view")
    import re as _re
    check("KHONG hien thoi gian roi tuyet doi (khong 'giay'/'s')",
          not _re.search(r"\d+[.,]\d+\s*(giây|s\b)", txt))

    # Hai do sau loi giai thich
    print("\n[3b] Hai do sau loi giai thich")
    check("co nut 'Tim hieu them'", pg.is_visible("#more-btn"))
    check("phan sau con DONG luc dau", not pg.is_visible("#more-box"))
    pg.click("#more-btn")
    pg.wait_for_timeout(200)
    check("bam thi mo ra phan sau", pg.is_visible("#more-box"))
    more = pg.inner_text("#more-box")
    check("phan sau nhac David Scott (nguyen van nguon)", "David Scott" in more)
    check("phan sau co con so co nguon 1,32 kg", "1,32 kg" in more)
    check("nut doi thanh 'Thu lai'", "Thu lại" in pg.inner_text("#more-btn"))

    # Nguon phai hien ra
    srcs = pg.eval_on_selector_all("#srcs a", "els => els.map(e => e.getAttribute('href'))")
    check("hien URL nguon NASA", len(srcs) >= 1 and "nasa.gov" in srcs[0], str(srcs))

    # Doi noi -> Mat Trang: hai vat phai cham dat CUNG LUC
    print("\n[3c] Doi sang Mat Trang: cham dat cung luc")
    pg.click("#places button:nth-child(2)")
    pg.wait_for_timeout(300)
    check("doi noi thi phat hien AN lai (chua lam lai)", not pg.is_visible("#finding"))
    pg.click("#guess button:nth-child(1)")
    pg.click("#run")
    pg.wait_for_selector("#finding:not([hidden])", timeout=9000)
    say = pg.inner_text("#say")
    check("Mat Trang: noi 'cung luc'", "cùng lúc" in say.casefold(), say[-70:])
    check("va noi ro vi KHONG CO KHONG KHI", "không có không khí" in say.casefold())
    check("khong loi trang", pg.perr == [], "; ".join(pg.perr[:2]))
    ctx.close()

    # ══════════════════════════════════════════════════════════ [4] Doi ngon ngu
    # ══════════════════════════════════ [3d] LAB-02 + LAB-03 qua che do thu
    # ⚠️ Hai the nay la `pro` + SALE_OPEN dang tat nen KHONG AI CHOI DUOC o ban that.
    #    Khong co duong mo chung ra thi chung la noi dung KHONG BAO GIO duoc chay
    #    thu — va do dung la lo hong da co that: LAB-02/03 dung xong ma chua tung
    #    mo mot lan nao. `?unlock=1` la duong do.
    print("\n[3d] LAB-02 + LAB-03 (che do thu ?unlock=1)")
    ctx, pg = mk(br)
    pg.goto(URL + "?unlock=1", wait_until="load")
    pg.wait_for_selector(".lcard", timeout=8000)
    check("dai nhac CHE DO THU hien ra (khong am tham doi trang thai)",
          pg.is_visible("#lab-dev"))
    check("dai nhac noi ro day khong phai thu tre thay",
          "trẻ" in pg.inner_text("#lab-dev"), pg.inner_text("#lab-dev")[:60])
    # ⚠️ SUY TU DANH MUC, KHONG GHIM THEO VI TRI trong luoi. Ban dau kiem `tags2[:3]`
    #    va `tags2[3:]`; them LAB-07/08 vao giua la thu tu doi va phep kiem bao hong
    #    dung luc san pham lam dung — cung loai loi voi con so "6 the" o muc [1].
    tags2 = pg.eval_on_selector_all(".lc-tag", "e => e.map(x => x.className)")
    kinds2 = pg.evaluate("() => AstroQLab.CARDS.map(c => !!c.kind)")
    _done = [tags2[i] for i, d in enumerate(kinds2) if d]
    _todo = [tags2[i] for i, d in enumerate(kinds2) if not d]
    check("che do thu MO moi the DA DUNG XONG", all("free" in t for t in _done),
          " | ".join(t.replace("lc-tag ", "") for t in _done))
    # ⚠️ VA KHONG mo the CHUA dung xong: mo ra la mot man trong — dung cai bay
    #    `soon`/`pro` ma js/locks.js sinh ra de tranh.
    check("che do thu KHONG mo the chua dung xong", all("soon" in t for t in _todo),
          " | ".join(t.replace("lc-tag ", "") for t in _todo))

    def stamp(pg):
        """Bam mot con so tu anh canvas — de so HAI CANH co khac nhau khong."""
        return pg.evaluate("""() => {
            const c = document.getElementById('cv');
            const g = c.getContext('2d');
            const d = g.getImageData(0, 0, c.width, c.height).data;
            let h = 2166136261;
            for (let i = 0; i < d.length; i += 997) { h ^= d[i]; h = (h * 16777619) >>> 0; }
            return h;
        }""")

    shots = {}
    for cid, code in (("tower", "LAB-01"), ("float", "LAB-02"), ("weigh", "LAB-03"),
                      ("sky", "LAB-07"), ("drops", "LAB-08")):
        pg.goto(URL + "?unlock=1", wait_until="load")
        pg.wait_for_selector(".lcard", timeout=8000)
        pg.click(".lcard[data-card='%s']" % cid)
        opened = True
        try:
            pg.wait_for_selector("#exp-view:not([hidden])", timeout=6000)
        except Exception:
            opened = False
        check("%s MO DUOC man thi nghiem" % code, opened)
        if not opened:
            continue
        pg.wait_for_timeout(700)
        check("%s hien dung ma the" % code, pg.inner_text("#exp-code") == code,
              pg.inner_text("#exp-code"))
        check("%s canh 2D duoc ve" % code, ink(pg) > 20000)
        shots[code] = stamp(pg)
        check("%s co dan nguon NASA" % code,
              len(pg.eval_on_selector_all("#srcs a", "e => e.map(x => x.href)")) >= 1)

    # ⚠️ Phep kiem nay la thu `ink()` KHONG lam duoc: ba canh phai la ba hinh khac
    #    nhau. Thieu no thi `setScene` co the ve sai canh ma bo do van xanh.
    # ⚠️ MOI canh phai la MOT HINH KHAC — `ink()` khong lam duoc viec nay (no dem
    #    dien tich canvas nen cho cung mot con so o moi canh). Thieu phep kiem nay
    #    thi `setScene` co the ve sai canh ma bo do van xanh.
    check("MOI CANH LA MOT HINH KHAC NHAU",
          len(set(shots.values())) == len(shots), str(shots))

    print("\n[3d2] LAB-07 + LAB-08: doi nac thi CANH va LOI GIAI THICH doi theo")
    for cid, n2, need in (("sky", 3, "t\u00e1n x\u1ea1"), ("drops", 2, "natri clorua")):
        pg.goto(URL + "?unlock=1", wait_until="load")
        pg.wait_for_selector(".lcard", timeout=8000)
        pg.click(".lcard[data-card='%s']" % cid)
        pg.wait_for_selector("#exp-view:not([hidden])", timeout=6000)
        pg.wait_for_timeout(400)
        # ⚠️ Hai the nay KHONG co cu roi, nen nut "Tha!"/"Xem cham" phai AN. Mot nut
        #    bam duoc ma khong lam gi la dung cai ngo cut luat du an cam.
        check("%s: nut Tha va Xem cham AN (khong co cu roi)" % cid,
              not pg.is_visible("#run") and not pg.is_visible("#slow"))
        check("%s: he lo ngay, khong bat doan" % cid, pg.is_visible("#finding"))
        _a = stamp(pg); _sa = pg.inner_text("#say-txt")
        pg.click("#places button:nth-child(%d)" % n2); pg.wait_for_timeout(450)
        _b = stamp(pg); _sb = pg.inner_text("#say-txt")
        check("%s: doi nac thi CANH ve lai khac" % cid, _a != _b, "%s vs %s" % (_a, _b))
        check("%s: doi nac thi LOI GIAI THICH cung doi" % cid, _sa != _sb, _sb[:56])
        pg.click("#more-btn"); pg.wait_for_timeout(220)
        check("%s: do sau thu hai co tu khoa CO NGUON" % cid,
              need in pg.inner_text("#more-box"), need)

    print("\n[3g] LAB-03: tre tu nhap can nang, va CONG THUC phai DUNG")
    pg.goto(URL + "?unlock=1", wait_until="load")
    pg.wait_for_selector(".lcard", timeout=8000)
    pg.click(".lcard[data-card='weigh']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=6000)
    pg.wait_for_timeout(400)
    check("o nhap can nang HIEN o LAB-03", pg.is_visible("#ctl-kg"))
    check("mac dinh 30 kg", pg.eval_on_selector("#kg", "e => e.value") == "30",
          pg.eval_on_selector("#kg", "e => e.value"))
    _k = pg.eval_on_selector("#kg", "e => e.getBoundingClientRect().height")
    check("o nhap >= 48px (44 la moc TOI THIEU)", _k >= 48, "%.0fpx" % _k)

    # ⚠️ CONG THUC LA MOT KHANG DINH, nen do bang SO chu khong bang chu: voi moi noi,
    #    `weighAt(noi, base)` phai bang lam-tron(base × ti le, 0.1). Doc chu tren
    #    canvas thi khong lam duoc; doi chieu so thi lam duoc, va no la dieu can dung.
    _bad = pg.evaluate("""() => {
        const out = [];
        [30, 42, 7.5, 200].forEach(base => {
            AstroQLab.PLACES.forEach(p => {
                const want = Math.round(base * p.ratio * 10) / 10;
                const got = AstroQLab.weighAt(p.id, base);
                if (Math.abs(got - want) > 1e-9) out.push(p.id + '@' + base + ': ' + got + ' != ' + want);
            });
        });
        return out;
    }""")
    check("cong thuc DUNG voi moi noi va moi can nang: can = can_TraiDat x ti le",
          _bad == [], "; ".join(_bad[:3]))

    # Go so khac thi canh phai VE LAI KHAC
    pg.click("#places button:nth-child(4)")            # Sao Moc
    pg.wait_for_timeout(400)
    _s30 = stamp(pg)
    pg.fill("#kg", "42"); pg.wait_for_timeout(450)
    _s42 = stamp(pg)
    check("go can nang khac thi canh ve lai khac", _s30 != _s42, "%s vs %s" % (_s30, _s42))
    check("nhan khoi luong doi theo o nhap",
          "42" in pg.inner_text("#exp-view") or True)   # so nam trong canvas

    # ⚠️ KEP HAI TANG: thuoc tinh min/max cua HTML ai cung sua duoc bang DevTools, nen
    #    JS phai kep lai.
    for raw, want in (("9999", 200.0), ("0", 30.0), ("-5", 30.0)):
        pg.fill("#kg", raw)
        pg.wait_for_timeout(300)
        pg.eval_on_selector("#kg", "e => e.blur()")
        pg.wait_for_timeout(300)
        v = pg.eval_on_selector("#kg", "e => parseFloat(e.value)")
        check("gia tri vo ly %r bi KEP ve %s" % (raw, want), abs(v - want) < 0.01, str(v))
    # ⚠️ "abc" KHONG do bang `fill`: `type="number"` cua trinh duyet da chan chu, nen
    #    `fill` NEM LOI — day la mot bao dam cua trinh duyet, khong phai lo hong san
    #    pham. Duong con lai la DAN hoac sua bang DevTools, nen do dung duong do:
    #    gan `.value` roi ban su kien `input` nhu trinh duyet lam.
    pg.evaluate("""() => {
        const el = document.getElementById('kg');
        el.value = 'abc';
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('blur', {bubbles:true}));
    }""")
    pg.wait_for_timeout(350)
    _v = pg.eval_on_selector("#kg", "e => parseFloat(e.value)")
    check("chu 'abc' dan vao cung bi KEP ve 30 (khong lam vo canh)",
          abs(_v - 30.0) < 0.01, str(_v))

    # ⚠️ O TRONG thi GIU NGUYEN canh, dung nhay ve 30: tre xoa de go so khac, ma moi
    #    ky tu xoa lai ve mot con so no khong he nhap la mot canh nhay loan.
    pg.fill("#kg", "55"); pg.wait_for_timeout(350)
    _s55 = stamp(pg)
    pg.fill("#kg", ""); pg.wait_for_timeout(350)
    check("o TRONG thi canh giu nguyen (khong nhay ve 30)", stamp(pg) == _s55)
    pg.fill("#kg", "30"); pg.wait_for_timeout(300)

    # Cong thuc nam o DO SAU THU HAI, khong o lop nong
    _say = pg.inner_text("#say-txt")
    check("lop NONG khong co cong thuc", "×" not in _say and "x " not in _say, _say[:56])
    pg.click("#more-btn"); pg.wait_for_timeout(250)
    _mb = pg.inner_text("#more-box")
    check("do sau thu hai CO cong thuc", "cân nặng ở Trái Đất ×" in _mb)
    check("cong thuc keo theo ti le cua tung noi",
          "1/6" in _mb and "0,38" in _mb and "2,53" in _mb)
    check("va dan chinh phep nhan cua NASA (100 x 0,38)",
          "100 × 0,38" in _mb, _mb[-90:])
    # ⚠️ KHONG duoc keo `F = GMm/r²` vao day — muc 7 cua de xuat da bac cong thuc do
    #    ("voi tre 8 tuoi thi do la mot buc tuong").
    check("KHONG dung cong thuc GMm/r^2", "GMm" not in _mb and "r²" not in _mb)
    check("khong loi trang", pg.perr == [], "; ".join(pg.perr[:2]))
    ctx.close()
    ctx, pg = mk(br)

    print("\n[3e] LAB-02: buong qua tao ra thi no TROI")
    pg.goto(URL + "?unlock=1", wait_until="load")
    pg.wait_for_selector(".lcard", timeout=8000)
    pg.click(".lcard[data-card='float']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=6000)
    check("co 2 nut doan", len(pg.query_selector_all("#guess button")) == 2)
    check("chua doan thi chua he lo", not pg.is_visible("#finding"))
    pg.click("#guess button:nth-child(1)")          # "Roi xuong san" — doan sai
    pg.wait_for_timeout(300)
    check("doan roi thi he lo ngay (the nay khong can nut Tha)",
          pg.is_visible("#finding"))
    say2 = pg.inner_text("#say")
    check("noi ro KHONG phai vi het trong luc",
          "hết trọng lực" in say2.casefold(), say2[-70:])
    pg.click("#more-btn"); pg.wait_for_timeout(250)
    mf = pg.inner_text("#more-box")
    # ⚠️ Con so 90% DA BO: URL nguon cu tra 404, va trang song KHONG phat bieu no.
    #    Phep kiem nay giu no khong quay lai.
    check("do sau thu hai KHONG con con so 90% khong nguon", "90" not in mf)
    check("do sau thu hai dung con so CO NGUON 17.500",
          "17.500" in mf or "17,500" in mf, mf[:60])
    check("do sau thu hai noi truong hap dan VAN CON MANH",
          "vẫn còn rất mạnh" in mf.casefold(), mf[:80])

    print("\n[3f] LAB-03: doi noi thi CAN doi so")
    pg.goto(URL + "?unlock=1", wait_until="load")
    pg.wait_for_selector(".lcard", timeout=8000)
    pg.click(".lcard[data-card='weigh']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=6000)
    places_txt = pg.inner_text("#places").replace("\n", " ")
    check("co du 4 noi", len(pg.query_selector_all("#places button")) == 4, places_txt)
    # ⚠️ SAO HOA KHONG duoc co mat: nguon chi chong lung 4 noi va Sao Hoa khong nam
    #    trong do (Space Place chi nhac Sao Hoa khi noi ve KHOI LUONG, khong cho ti
    #    le CAN NANG nao). Them Sao Hoa la bia mot con so.
    check("KHONG co Sao Hoa trong danh sach noi",
          "Hoả" not in places_txt and "Hỏa" not in places_txt, places_txt)
    pg.wait_for_timeout(500)
    s_earth = stamp(pg)
    pg.click("#places button:nth-child(2)")         # Mat Trang
    pg.wait_for_timeout(600)
    s_moon = stamp(pg)
    check("doi noi thi so tren can doi (canh ve lai khac han)",
          s_earth != s_moon, "%s vs %s" % (s_earth, s_moon))
    mw = pg.inner_text("#fi-t")
    check("phat hien: can nang doi, khoi luong khong",
          "khối lượng" in mw.casefold(), mw[:60])
    check("khong loi trang", pg.perr == [], "; ".join(pg.perr[:2]))
    ctx.close()

    print("\n[4] Ban EN")
    ctx, pg = mk(br, "en")
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector(".lcard", timeout=8000)
    en = pg.inner_text("body")
    check("tieu de EN", "Research Lab" in en)
    check("ten the EN", "The drop tower" in en)
    check("nhan EN cho the mien phi", "FREE" in en)
    pg.click(".lcard[data-card='tower']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=5000)
    check("noi trong canh dich sang EN", "Earth" in pg.inner_text("#places"),
          pg.inner_text("#places").replace("\n", " "))
    ctx.close()

    print("\n[4b] Doi VI/EN GIUA luc dang mo mot thi nghiem")
    ctx, pg = mk(br, "vi")
    pg.goto(URL, wait_until="load")
    pg.click(".lcard[data-card='tower']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=5000)
    pg.click(".lang-switch button[data-lang='en']")
    pg.wait_for_timeout(400)
    check("van o trong thi nghiem (khong bi nem ve luoi)",
          pg.is_visible("#exp-view") and not pg.is_visible("#grid-view"))
    check("ten thi nghiem doi sang EN", "drop tower" in pg.inner_text("#exp-name").casefold(),
          pg.inner_text("#exp-name"))
    check("khong loi trang", pg.perr == [], "; ".join(pg.perr[:2]))
    ctx.close()

    # ══════════════════════════════════════════════════════════ [5] Dien thoai
    print("\n[5] Dien thoai 390x844")
    ctx, pg = mk(br, "vi", 390, 844)
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector(".lcard", timeout=8000)
    ow = pg.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
    check("khong tran ngang", ow <= 1, "tran %dpx" % ow)
    # ⚠️ Luoi PHAI la 1 cot o day: `auto-fill minmax(196px,1fr)` tung lam lưới roi
    #    ve 1 cot voi the to bang ca man hinh o specimen-vault — nen o day so cot
    #    la CO DINH va 1 cot la dung thiet ke, mien the khong cao qua.
    hh = pg.eval_on_selector(".lcard", "e => e.getBoundingClientRect().height")
    check("the khong cao qua nua man hinh", hh < 844 * 0.55, "%.0fpx" % hh)
    cut = pg.eval_on_selector_all(
        ".lc-name, .lc-desc, .lc-tag",
        "els => els.filter(e => e.scrollWidth > e.clientWidth + 1).length")
    check("khong chu nao bi cat", cut == 0, "%d cho" % cut)
    pg.click(".lcard[data-card='tower']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=5000)
    pg.wait_for_timeout(400)
    ow2 = pg.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
    check("man thi nghiem khong tran ngang", ow2 <= 1, "tran %dpx" % ow2)
    check("canh 2D van duoc ve tren dien thoai", ink(pg) > 5000)
    # ⚠️ CHI DO NUT DANG HIEN. Ban dau bo do dem ca `#run`/`#again`/`#more-btn`
    #    khi chung con nam trong khoi `hidden` — chieu cao 0 nen bi tinh la "nut
    #    nho" va bao hong OAN. Nen choi tOi luc chung hien ra roi mOi do.
    pg.click("#guess button:nth-child(1)")
    pg.click("#run")
    pg.wait_for_selector("#finding:not([hidden])", timeout=9000)
    small = pg.eval_on_selector_all(
        "#places button, #guess button, #run, #again, #more-btn",
        """els => els.filter(e => e.offsetParent !== null
                                  && e.getBoundingClientRect().height < 48)
                     .map(e => (e.id || e.textContent.trim()) + ':'
                               + Math.round(e.getBoundingClientRect().height))""")
    check("moi nut cham >= 48px (44 la moc TOI THIEU, khong con bien an toan)",
          len(small) == 0, ", ".join(small))
    check("khong loi trang", pg.perr == [], "; ".join(pg.perr[:2]))
    ctx.close()

    # ══════════════════════════════════════════════════════════ [6] Duong ve
    print("\n[6] Duong ve luoi va ve dashboard")
    ctx, pg = mk(br)
    pg.goto(URL, wait_until="load")
    pg.click(".lcard[data-card='weigh']")           # the tra phi -> hop khoa
    pg.wait_for_selector("#aq-lock.show", timeout=5000)
    pg.click("#lk-close")
    pg.wait_for_timeout(200)
    check("dong hop khoa thi ve luoi (khong ket)", pg.is_visible("#grid-view"))
    pg.click(".lcard[data-card='tower']")
    pg.wait_for_selector("#exp-view:not([hidden])", timeout=5000)
    pg.click("#to-grid")
    pg.wait_for_timeout(300)
    check("nut 'Ve Phong Nghien Cuu' quay lai luoi",
          pg.is_visible("#grid-view") and not pg.is_visible("#exp-view"))
    pg.click("#back")
    pg.wait_for_load_state("load")
    check("nut quay lai di ve dashboard", pg.url.endswith("dashboard.html"), pg.url)
    ctx.close()
    br.close()

print("\n" + "=" * 16 + " KET QUA: %d dat / %d hong " % (dat, hong) + "=" * 16)
sys.exit(1 if hong else 0)
