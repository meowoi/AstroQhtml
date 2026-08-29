# -*- coding: utf-8 -*-
"""
smoke_utm.py - do NHAN CHIEN DICH tren Chromium THAT.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/smoke_utm.py

⚠️ VI SAO CAN BO NAY DU DA CO test_utm.py: bo kia do PHIA SERVER (chuoi gui len duoc
   loc va luu dung cho). No khong tra loi duoc ba cau thuoc ve phia trinh duyet:
     - nhan co duoc GIU khi tre quay lai bang mot link khac khong (luot cham dau tien)
     - nhan co SONG QUA cu dieu huong `/` -> `landing-app.html` va THAT SU di kem
       luot dang ky tai khoan khong
     - localStorage bi chan (che do rieng tu) thi trang co vo khong
   Ca ba chi do duoc bang cach mo trang that roi bat request that.

⚠️ CHAN MOI LOI GOI RA API THAT. Bo do chay o cong 8123 - khong nam trong
   ALLOWED_ORIGINS - nen trinh duyet TU ghi mot dong do vao console va phep kiem
   "0 loi trang" bao hong oan. Tra phan hoi gia thi vua sach console vua di qua
   dung nhanh code that. (Cung cach smoke_lang_switch / audit_viewports da lam.)
"""
import json
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
API = re.compile(r"https://ueqp4gjr0l\.execute-api[^\s]*")

OK = FAIL = 0


def check(label, cond, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(extra)) if extra else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(extra))


def stub_api(ctx, seen):
    """Chan moi loi goi API va ghi lai than request."""
    def handler(route):
        req = route.request
        try:
            body = json.loads(req.post_data or "{}")
        except Exception:
            body = {"raw": req.post_data}
        seen.append({"url": req.url, "body": body})
        route.fulfill(status=202, content_type="application/json",
                      body=json.dumps({"ok": True, "dup": False, "mailSent": True,
                                       "pending": True, "email": body.get("email", ""),
                                       "expiresInMinutes": 10}))
    ctx.route(re.compile(r".*execute-api.*"), handler)


def new_ctx(pw_browser, lang="vi"):
    ctx = pw_browser.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    # Ghim ngon ngu: getLang() lui ve navigator.language, ma Chromium mac dinh en-US
    # -> nua bo do lang le chay bang tieng Anh (bai hoc 07/08/2026).
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','%s')}catch(e){}" % lang)
    return ctx


def utm_of(pg):
    return pg.evaluate("() => window.AstroQUtm ? AstroQUtm.get() : null")


def raw_of(pg):
    return pg.evaluate("() => window.AstroQUtm ? AstroQUtm.raw() : null")


print("=== NHAN CHIEN DICH (UTM) ===")
with sync_playwright() as p:
    br = p.chromium.launch()

    # ---------------------------------------------------------------- [1] bat nhan
    print("")
    print("[1] Bat nhan tu dia chi")
    ctx = new_ctx(br)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/index.html?utm_source=fb&utm_medium=post&utm_campaign=ra-mat-20-08",
            wait_until="domcontentloaded")
    check("AstroQUtm co mat", pg.evaluate("() => !!window.AstroQUtm"))
    check("ghep dung chuoi gui len", utm_of(pg) == "fb/post/ra-mat-20-08", utm_of(pg))
    r = raw_of(pg)
    check("giu du ba phan", r and r["source"] == "fb" and r["medium"] == "post"
          and r["campaign"] == "ra-mat-20-08", r)
    check("co dong moc thoi gian", bool(r and r.get("at")), r and r.get("at"))
    check("0 loi trang", not errs, errs[:2])

    # ⚠️ Phai chay NGAY LUC NAP FILE, khong doi DOM: tre co the bam nut dang ky truoc
    #    khi trang ve xong, va luc do nhan phai da nam san trong may.
    pg2 = ctx.new_page()
    pg2.goto(BASE + "/index.html?utm_source=zalo", wait_until="commit")
    check("da luu truoc khi DOM san sang",
          pg2.evaluate("() => { try { return !!localStorage.getItem('astroq-utm'); }"
                       "catch(e){ return 'loi'; } }") is True)
    pg2.close()

    # ------------------------------------------------------- [2] giu luot cham dau
    # ⚠️ MUC QUAN TRONG NHAT. Cau hoi la "cai gi mang nguoi nay toi" - do la lan DAU.
    #    Ghi de theo luot cuoi thi tre vao tu bai Facebook hom nay, ba hom sau tu go
    #    dia chi roi moi dang ky se duoc quy cho "khong ro", va bai dang trong nhu vo dung.
    print("")
    print("[2] Giu LUOT CHAM DAU TIEN")
    pg.goto(BASE + "/index.html?utm_source=zalo&utm_campaign=bai-hai",
            wait_until="domcontentloaded")
    check("quay lai bang link KHAC van giu nhan dau",
          utm_of(pg) == "fb/post/ra-mat-20-08", utm_of(pg))
    pg.goto(BASE + "/index.html", wait_until="domcontentloaded")
    check("vao thang khong co tham so van giu nhan dau",
          utm_of(pg) == "fb/post/ra-mat-20-08", utm_of(pg))
    ctx.close()

    # ------------------------------------------------------------------ [3] loc
    print("")
    print("[3] Loc chuoi ngay tai client")
    cases = [
        ("khong co tham so",          "",                                        ""),
        ("thieu utm_source -> bo",    "?utm_campaign=abc&utm_medium=post",       ""),
        ("chi co nguon",              "?utm_source=fb",                          "fb"),
        ("HOA thanh thuong",          "?utm_source=FB&utm_medium=POST",          "fb/post"),
        ("bo ky tu la",               "?utm_source=fb%3Cscript%3E",              "fbscript"),
        ("cat con 24 ky tu",          "?utm_source=" + "f" * 40,                 "f" * 24),
        ("giu chu so va . _ -",       "?utm_source=fb_2&utm_campaign=x-1.a",     "fb_2/x-1.a"),
        ("nguon toan ky tu la -> bo", "?utm_source=%21%21%21&utm_medium=post",   ""),
    ]
    for label, qs, want in cases:
        c = new_ctx(br)
        q = c.new_page()
        q.goto(BASE + "/index.html" + qs, wait_until="domcontentloaded")
        got = utm_of(q)
        check("loc: " + label, got == want, "%r -> %r (cho %r)" % (qs, got, want))
        c.close()

    # ------------------------------------------------------------------ [4] han
    # ⚠️ Khong co han thi mot cu bam tu thang truoc van duoc tinh cong cho mot luot
    #    dang ky hom nay - con so dep nhung SAI.
    print("")
    print("[4] Han 60 ngay")
    for days, expect, note in ((59, "fb", "chua qua han thi con"),
                               (61, "", "qua han thi coi nhu khong co"),
                               (-3, "", "dong ho may chay lui thi cung bo")):
        c = new_ctx(br)
        c.add_init_script(
            "try{localStorage.setItem('astroq-utm', JSON.stringify("
            "{source:'fb',medium:'',campaign:'',at: Date.now() - %d*86400000}))}catch(e){}"
            % days)
        q = c.new_page()
        q.goto(BASE + "/index.html", wait_until="domcontentloaded")
        got = utm_of(q)
        check("han: " + note, got == expect, "%d ngay -> %r" % (days, got))
        c.close()

    # ----------------------------------------------------- [5] localStorage bi chan
    # ⚠️ Che do rieng tu cua mot so trinh duyet nem loi ngay khi doc localStorage.
    #    Mot nhan chien dich khong duoc phep lam vo trang chu cua mot dua tre.
    print("")
    print("[5] localStorage bi chan (che do rieng tu)")
    c = new_ctx(br)
    c.add_init_script(
        "Object.defineProperty(window,'localStorage',{configurable:true,"
        "get(){ throw new Error('bi chan'); }});")
    q = c.new_page()
    e2 = []
    q.on("pageerror", lambda e: e2.append(str(e)))
    q.goto(BASE + "/index.html?utm_source=fb", wait_until="domcontentloaded")
    check("trang van dung, AstroQUtm van co", q.evaluate("() => !!window.AstroQUtm"))
    check("get() tra chuoi rong chu khong nem loi", utm_of(q) == "", utm_of(q))
    check("0 loi trang", not e2, e2[:2])
    c.close()

    # -------------------------------------- [6] nhan di kem luot DANG KY TAI KHOAN
    # ⚠️ MUC NAY DA DOI PHAT BIEU (20/08/2026), KHONG phai noi long.
    #    Truoc day no dien `#wl-email` roi bam `#wl-form` de do duong `/waitlist`.
    #    Form waitlist DA BI GO HAN cung ngay (thay bang mot CTA `<a>` sang
    #    landing-app.html), nen bo do khang dinh mot thu khong con ton tai va
    #    treo o `Page.fill` — doc ra y het mot loi san pham.
    #
    #    Duong THAT bay gio dai hon va vi the phep kiem MANH HON ban cu:
    #      `/?utm_*`  ->  bam CTA  ->  landing-app.html (URL KHONG con tham so)
    #      ->  popup Dang ky  ->  POST /auth/register  { ..., src }
    #    Tuc no do luon mot dieu ban cu khong hoi toi: nhan phai SONG QUA mot cu
    #    DIEU HUONG. Ban cu gui form ngay tren chinh trang vua bat nhan, nen no
    #    xanh ca khi localStorage khong he duoc dung toi.
    #
    #    Van la phep kiem chung minh day noi CHAY THAT: no bat than request that
    #    chu khong doc ma nguon.
    print("")
    print("[6] Nhan di kem luot DANG KY TAI KHOAN (qua mot cu dieu huong)")

    def dang_ky(ctx, page, mail):
        """Mo popup Dang ky roi gui form.

        ⚠️ TU KHAI TRANG THAI KHI HET HAN CHO (quy tac 6 muc 6). Mot
           `wait_for_selector` tran chi noi "co cai gi do treo" roi giet ca bo do
           giua chung — doc ra y het mot loi san pham. Phep thu pha hoai
           'CTA tro sai dich' da roi vao dung ca do."""
        try:
            # `js/firebase-auth-ui.js` la module ES nen no chay SAU script co dien;
            # bam truoc khi no gan handler thi form khong gui di dau ca.
            page.wait_for_function("() => !!window.AstroQAuth", timeout=15000)
            # ⚠️ CHI BAM `#btn-try` KHI POPUP CHUA MO. CTA cua khoi waitlist tro vao
            #    `landing-app.html#dangky`, va tu 26/08/2026 cai neo do TU MO SAN o
            #    dung pane Dang ky (roi `replaceState` don neo khoi URL). Ban cu bam
            #    `#btn-try` vo dieu kien nen no bam vao mot nut DANG BI CHINH LOP PHU
            #    CHE -> Playwright cho het 30s roi bao "gui duoc form dang ky: HONG".
            #    Doc ra y het mot loi san pham, trong khi san pham dang lam DUNG cai
            #    viec no duoc sua de lam. Da soi bang `elementFromPoint`: thang chen
            #    con tro la `#reg-email` cua chinh popup.
            if not page.locator("#auth-overlay.show").count():
                page.click("#btn-try")
            page.wait_for_selector("#auth-register:not([hidden])", timeout=15000)
            page.fill("#reg-name", "Bin")
            page.fill("#reg-email", mail)
            page.fill("#reg-pass", "matkhau123")
            page.click("#auth-register button[type=submit]")
            page.wait_for_selector("#auth-verify:not([hidden])", timeout=25000)
        except Exception as ex:
            check("gui duoc form dang ky", False,
                  "url=%s | co #btn-try=%s | co #auth-register=%s | %s"
                  % (page.url,
                     page.locator("#btn-try").count(),
                     page.locator("#auth-register").count(),
                     str(ex).splitlines()[0][:90]))
            return False
        return True

    c = new_ctx(br)
    seen = []
    stub_api(c, seen)
    q = c.new_page()
    e3 = []
    q.on("pageerror", lambda e: e3.append(str(e)))
    q.goto(BASE + "/index.html?utm_source=fb&utm_medium=post&utm_campaign=bai-a",
           wait_until="domcontentloaded")
    # Bam dung CTA that o khoi waitlist cua trang chu.
    with q.expect_navigation(wait_until="domcontentloaded", timeout=20000):
        q.click(".wl-cta a")
    check("CTA dua sang landing-app.html", q.url.endswith("/landing-app.html"), q.url)
    # ⚠️ Phep kiem nay la CHOT CHAN cua ca muc: URL dich KHONG mang tham so utm,
    #    nen nhan doc duoc o day chi co the den tu localStorage. Thieu no thi
    #    phep kiem `src` phia duoi van xanh ke ca khi nhan duoc bat lai tu URL.
    check("URL dich KHONG con tham so utm", "utm_" not in q.url, q.url)
    check("nhan song qua cu dieu huong", utm_of(q) == "fb/post/bai-a", utm_of(q))
    dang_ky(c, q, "success+smoke@simulator.amazonses.com")
    rg = [x for x in seen if "/auth/register" in x["url"]]
    check("da goi POST /auth/register", len(rg) == 1, len(rg))
    if rg:
        check("than request mang truong src", "src" in rg[0]["body"], list(rg[0]["body"]))
        check("src dung nhan da bat", rg[0]["body"].get("src") == "fb/post/bai-a",
              rg[0]["body"].get("src"))
    check("0 loi trang", not e3, e3[:2])
    c.close()

    # Khong co nhan thi van gui, chi la chuoi rong - khong duoc vo hay bo qua truong.
    c = new_ctx(br)
    seen = []
    stub_api(c, seen)
    q = c.new_page()
    q.goto(BASE + "/landing-app.html", wait_until="domcontentloaded")
    dang_ky(c, q, "success+smoke2@simulator.amazonses.com")
    rg = [x for x in seen if "/auth/register" in x["url"]]
    check("khong co nhan -> van gui, src rong",
          len(rg) == 1 and rg[0]["body"].get("src") == "",
          rg and rg[0]["body"].get("src"))
    c.close()

    # ------------------------------------- [7] link fanpage tro THANG landing-app
    # ⚠️ Khac muc [6]: o day nhan den tu CHINH URL cua landing-app, khong qua trang
    #    chu. Do la duong that khi bai dang tro thang vao cua dang ky, nen `js/utm.js`
    #    phai duoc nap o CA HAI trang chu khong rieng `/`.
    print("")
    print("[7] Link tro THANG landing-app cung bat duoc nhan")
    c = new_ctx(br)
    seen = []
    stub_api(c, seen)
    q = c.new_page()
    e4 = []
    q.on("pageerror", lambda e: e4.append(str(e)))
    q.goto(BASE + "/landing-app.html?utm_source=fb&utm_medium=post&utm_campaign=bai-b",
           wait_until="domcontentloaded")
    check("landing-app cung bat duoc nhan", utm_of(q) == "fb/post/bai-b", utm_of(q))
    check("0 loi trang", not e4, e4[:2])
    c.close()

    # ------------------------------------------------- [5] fbclid: luoi do + duong CAPI
    #
    # ⚠️⚠️ MUC NAY THEM 26/08/2026, VA TRUOC DO BO NAY KHONG CO MOT CHU `fbclid` NAO —
    #    tuc nhanh luoi do (`js/utm.js`: khong co utm_source thi doc `fbclid`) chua
    #    tung duoc kiem luc CHAY, du no da song tu 23/08. Cung luot nay them viec giu
    #    `fbclid` THO cho duong Conversions API (server-side, xem
    #    `AstroqSV/.../Services/MetaCapi.cs`), nen day la cho phai canh ca hai.
    print("")
    print("[5] fbclid: luoi do, va gia tri THO cho Conversions API")
    c = new_ctx(br)
    seen5 = []
    stub_api(c, seen5)
    q = c.new_page()
    e5 = []
    q.on("pageerror", lambda e: e5.append(str(e)))

    # (a) Chi co fbclid, khong co nhan -> roi vao luoi do
    q.goto(BASE + "/index.html?fbclid=IwAR_TEST_abc123", wait_until="domcontentloaded")
    check("[5a] chi co fbclid -> nhan la `facebook/fbclid`",
          utm_of(q) == "facebook/fbclid", utm_of(q))
    click = q.evaluate("() => window.AstroQUtm ? AstroQUtm.click() : null")
    check("[5a] click() tra ve dung fbclid THO",
          click and click.get("fbclid") == "IwAR_TEST_abc123", click)
    check("[5a] click() kem moc thoi gian cham dau tien (ms)",
          click and isinstance(click.get("at"), (int, float)) and click["at"] > 1e12,
          click.get("at") if click else None)
    # ⚠️ Client KHONG duoc tu dung khuon `fb.1.` — luat do thuoc server.
    check("[5a] click() tra THO, khong dung khuon `fb.1.`",
          click and not str(click.get("fbclid", "")).startswith("fb.1."), click)

    # (b) ⚠️⚠️ CO CA NHAN LAN fbclid — DAY LA TRUONG HOP QUAN TRONG NHAT, va la cho
    #     ban dau de sai: link quang cao gan nhan DUNG thi Meta VAN them `fbclid` vao.
    #     Neu chi giu fbclid o nhanh luoi do thi ta chi do duoc dung nhung link minh
    #     QUEN gan nhan — nguoc han y muon.
    c2 = new_ctx(br)
    seen5b = []
    stub_api(c2, seen5b)
    q2 = c2.new_page()
    q2.on("pageerror", lambda e: e5.append(str(e)))
    q2.goto(BASE + "/index.html?utm_source=facebook&utm_medium=paid&utm_campaign=aug2026"
                   "&fbclid=IwAR_TEST_xyz789", wait_until="domcontentloaded")
    check("[5b] nhan tu dat duoc uu tien tuyet doi",
          utm_of(q2) == "facebook/paid/aug2026", utm_of(q2))
    cl2 = q2.evaluate("() => window.AstroQUtm ? AstroQUtm.click() : null")
    check("[5b] VAN giu duoc fbclid tho khi da co nhan",
          cl2 and cl2.get("fbclid") == "IwAR_TEST_xyz789", cl2)

    # (c) Khong co fbclid -> click() tra null, va khong bia ra gi
    c3 = new_ctx(br)
    stub_api(c3, [])
    q3 = c3.new_page()
    q3.on("pageerror", lambda e: e5.append(str(e)))
    q3.goto(BASE + "/index.html?utm_source=zalo&utm_medium=post&utm_campaign=x",
            wait_until="domcontentloaded")
    check("[5c] khong tu link Meta -> click() tra null",
          q3.evaluate("() => window.AstroQUtm ? AstroQUtm.click() : 'khong co AstroQUtm'")
          is None)

    # (d) ⚠️⚠️ BAT BIEN RIENG TU: `POST /visit` KHONG duoc mang fbclid. Route do co loi
    #     hua "khong luu gi ve nguoi ghe"; `fbclid` chi duoc di theo luc NGUOI DUNG chu
    #     dong tao tai khoan. Day la phep kiem luc CHAY cho loi hua do.
    q.wait_for_timeout(1200)
    visits = [x for x in seen5 if "/visit" in x["url"]]
    check("[5d] co goi POST /visit (co nhan nen phai goi)", len(visits) >= 1,
          "%d loi goi" % len(visits))
    # ⚠️ SOI TEN TRUONG VA GIA TRI, KHONG SOI CHUOI CON. Ban dau phep kiem nay tim
    #    chu "fbclid" o bat ky dau trong than request va bao hong vi `src` la
    #    `facebook/fbclid` — mot NHAN hoan toan hop le theo thiet ke (luoi do cua
    #    js/utm.js). Bat oan mot thu dung la cach nhanh nhat de phep kiem bi bo qua.
    bad = [v for v in visits
           if "fbclid" in [k.lower() for k in (v["body"] or {}).keys()]
           or "IwAR_TEST_abc123" in json.dumps(v["body"])]
    check("[5d]⚠️ than request /visit KHONG mang truong fbclid, KHONG mang gia tri do",
          not bad, bad[:1])
    check("[5d] /visit chi mang dung truong `src`",
          sorted((visits[0]["body"] or {}).keys()) == ["src"] if visits else False,
          sorted((visits[0]["body"] or {}).keys()) if visits else None)

    check("[5] 0 loi trang", not e5, e5[:2])
    c.close(); c2.close(); c3.close()

    br.close()

print("")
print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
