# -*- coding: utf-8 -*-
"""
smoke_utm.py - do NHAN CHIEN DICH tren Chromium THAT.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/smoke_utm.py

⚠️ VI SAO CAN BO NAY DU DA CO test_utm.py: bo kia do PHIA SERVER (chuoi gui len duoc
   loc va luu dung cho). No khong tra loi duoc ba cau thuoc ve phia trinh duyet:
     - nhan co duoc GIU khi tre quay lai bang mot link khac khong (luot cham dau tien)
     - nhan co THAT SU di kem luot gui form khong
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

    # ------------------------------------------------- [6] gui kem luot dang ky cho
    # ⚠️ Day la phep kiem chung minh day noi CHAY THAT: no bat than request that
    #    chu khong doc ma nguon.
    print("")
    print("[6] Nhan di kem luot vao hang cho")
    c = new_ctx(br)
    seen = []
    stub_api(c, seen)
    q = c.new_page()
    e3 = []
    q.on("pageerror", lambda e: e3.append(str(e)))
    q.goto(BASE + "/index.html?utm_source=fb&utm_medium=post&utm_campaign=bai-a",
           wait_until="domcontentloaded")
    q.fill("#wl-email", "success+smoke@simulator.amazonses.com")
    q.click("#wl-form button[type=submit]")
    q.wait_for_selector("#wl-done:not([hidden])", timeout=25000)
    wl = [x for x in seen if "/waitlist" in x["url"]]
    check("da goi POST /waitlist", len(wl) == 1, len(wl))
    if wl:
        check("than request mang truong src", "src" in wl[0]["body"], list(wl[0]["body"]))
        check("src dung nhan da bat", wl[0]["body"].get("src") == "fb/post/bai-a",
              wl[0]["body"].get("src"))
    check("0 loi trang", not e3, e3[:2])
    c.close()

    # Khong co nhan thi van gui, chi la chuoi rong - khong duoc vo hay bo qua truong.
    c = new_ctx(br)
    seen = []
    stub_api(c, seen)
    q = c.new_page()
    q.goto(BASE + "/index.html", wait_until="domcontentloaded")
    q.fill("#wl-email", "success+smoke2@simulator.amazonses.com")
    q.click("#wl-form button[type=submit]")
    q.wait_for_selector("#wl-done:not([hidden])", timeout=25000)
    wl = [x for x in seen if "/waitlist" in x["url"]]
    check("khong co nhan -> van gui, src rong",
          len(wl) == 1 and wl[0]["body"].get("src") == "",
          wl and wl[0]["body"].get("src"))
    c.close()

    # ------------------------------------------------- [7] gui kem luot dang ky that
    print("")
    print("[7] Nhan di kem luot dang ky tai khoan")
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

    br.close()

print("")
print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
