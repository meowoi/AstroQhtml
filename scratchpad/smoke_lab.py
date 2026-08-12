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
    cards = pg.query_selector_all(".lcard")
    check("co dung 6 the", len(cards) == 6, str(len(cards)))
    codes = pg.eval_on_selector_all(".lc-code", "els => els.map(e => e.textContent)")
    check("6 ma LAB-01..06 dung thu tu", codes == ["LAB-0%d" % i for i in range(1, 7)],
          ",".join(codes))
    tags = pg.eval_on_selector_all(".lc-tag", "els => els.map(e => e.className)")
    check("LAB-01 la the MIEN PHI", "free" in tags[0], tags[0])
    check("LAB-02 va LAB-03 la the tra phi", "pro" in tags[1] and "pro" in tags[2],
          "%s | %s" % (tags[1], tags[2]))
    check("LAB-04..06 la 'sap ra mat'", all("soon" in t for t in tags[3:]),
          " | ".join(tags[3:]))
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
