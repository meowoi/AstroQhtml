# -*- coding: utf-8 -*-
"""
smoke_waitlist.py — do THAT tren Chromium form waitlist o index.html.

Ba trieu chung chu du an bao (02/08/2026), deu tu MOT goc: submit handler nem
TypeError ngay sau preventDefault vi honeypot sai id.
  1. bo trong roi bam nut -> khong co gi noi phai go email
  2. nhap email roi gui   -> khong co thong bao da dang ky thanh cong
  3. khong co email nao toi -> vi khong he co loi goi mang nao duoc ban di

Muc [1]-[8] gia lap phan hoi cua server nen chay doc lap, khong can backend.
Muc [10] goi THAT vao backend (ban that AWS, hoac backend o may neu dang bat) — phai chay
may chu tinh o CONG 8000, vi ALLOWED_ORIGINS khong co 8123 va CORS se chan.

Chay:  python -m http.server 8000  (trong AstroQhtml/)  roi  python smoke_waitlist.py
"""
import json
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"
URL = BASE_URL + "/index.html"
# ⚠️ Trang chu tach lam HAI URL TINH tu 07/08/2026 (xem scratchpad/gen_home_en.py).
#    Ban tieng Anh KHONG con lay duoc bang cach dat `astroq-lang='en'` roi doi chu
#    tai cho — phai mo dung URL cua no. Va bam nut VI/EN gio la DIEU HUONG, khong
#    phai doi chu tai cho, nen moi phep kiem "doi ngon ngu giua chung" phai doi
#    cach do theo.
URL_EN = BASE_URL + "/en/index.html"
OK = FAIL = 0


def check(label, cond, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(extra)) if extra else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(extra))


def new_page(pw, lang="vi", width=1440, height=900):
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": width, "height": height})
    pg.perr = []
    pg.cerr = []
    pg.posts = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.on("console", lambda m: pg.cerr.append(m.text) if m.type == "error" else None)
    pg.route("**/waitlist", lambda r: (
        pg.posts.append(r.request.post_data or ""),
        r.fulfill(status=202, content_type="application/json",
                  body='{"ok":true,"dup":false,"mailSent":true}')))
    pg.add_init_script("localStorage.setItem('astroq-lang','%s')" % lang)
    pg.goto(URL_EN if lang == "en" else URL, wait_until="networkidle")
    pg.eval_on_selector("#waitlist", "e=>e.scrollIntoView({block:'center'})")
    pg.wait_for_timeout(300)
    return b, pg


with sync_playwright() as pw:
    # ---------------------------------------------------------------- [1] bo trong
    print("\n[1] Bam nut khi CHUA nhap email (vi)")
    b, pg = new_page(pw)
    pg.click("#wl-submit")
    pg.wait_for_timeout(450)   # .toast co transition .3s — do som hon la do giua luc no dang hien
    err = pg.query_selector("#wl-err")
    txt = (err.inner_text() or "").strip()
    box = err.bounding_box()
    inp = pg.query_selector("#wl-email").bounding_box()
    check("khong con loi JS nem ra", pg.perr == [], pg.perr)
    check("hop bao loi hien ra", err.get_attribute("hidden") is None)
    check("cau bao loi dung ban VI", "Nhập email" in txt, repr(txt))
    check("hop bao loi NAM TRONG khung nhin", box and 0 <= box["y"] <= 900, box)
    check("nam ngay duoi o email (<120px)", box and 0 < box["y"] - (inp["y"] + inp["height"]) < 120,
          "%.0f px" % (box["y"] - (inp["y"] + inp["height"])) if box else "-")
    check("o email doi vien do", "invalid" in (pg.get_attribute("#wl-email", "class") or ""))
    check("o email co aria-invalid", pg.get_attribute("#wl-email", "aria-invalid") == "true")
    check("con tro nhay vao o email", pg.evaluate("document.activeElement.id") == "wl-email")
    check("toast van chay song song", pg.eval_on_selector("#toast", "e=>getComputedStyle(e).opacity") == "1")
    check("KHONG gui gi len server", pg.posts == [], pg.posts)
    # go mot chu -> loi bien mat
    pg.fill("#wl-email", "a")
    pg.wait_for_timeout(120)
    check("go chu vao thi loi tu an", pg.get_attribute("#wl-err", "hidden") is not None)
    check("bo aria-invalid theo", pg.get_attribute("#wl-email", "aria-invalid") is None)
    b.close()

    # ---------------------------------------------------------------- [2] sai dinh dang
    print("\n[2] Email sai dinh dang")
    b, pg = new_page(pw)
    pg.fill("#wl-email", "khongphaiemail")
    pg.click("#wl-submit")
    pg.wait_for_timeout(250)
    t2 = (pg.inner_text("#wl-err") or "").strip()
    check("hop bao loi hien ra", pg.get_attribute("#wl-err", "hidden") is None)
    check("dung cau 'chua dung dinh dang'", "định dạng" in t2, repr(t2))
    check("KHONG gui gi len server", pg.posts == [], pg.posts)
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()

    # ---------------------------------------------------------------- [3] gui that
    print("\n[3] Nhap email hop le roi gui")
    b, pg = new_page(pw)
    pg.fill("#wl-email", "phihanhgia@astroq.org")
    pg.click("#wl-submit")
    pg.wait_for_timeout(900)
    check("da BAN loi goi len POST /waitlist", len(pg.posts) == 1, pg.posts)
    # payload la JSON (js/api.js dung apiPost)
    body = json.loads(pg.posts[0]) if pg.posts else {}
    check("payload mang dung email", body.get("email") == "phihanhgia@astroq.org", body)
    check("payload mang ngon ngu", body.get("lang") == "vi", body)
    check("payload mang bay bot (server loc lai)", body.get("hp") == "", body)
    check("payload KHONG con truong cua dich vu form cu",
          not any(k.startswith("_") for k in body), body)
    check("the 'da dang ky' HIEN RA", pg.get_attribute("#wl-done", "hidden") is None)
    check("form da an di", pg.get_attribute("#wl-form", "hidden") is not None)
    done = (pg.inner_text("#wl-done") or "")
    check("the ghi ro da thanh cong", "thành công" in done, repr(done[:70]))
    check("the nhac lai dung email", "phihanhgia@astroq.org" in done)
    check("the nam trong khung nhin", 0 <= pg.eval_on_selector("#wl-done", "e=>e.getBoundingClientRect().top") <= 900)
    check("toast bao thanh cong", pg.eval_on_selector("#toast", "e=>getComputedStyle(e).opacity") == "1")
    check("icon toast la loai 'ok'", pg.query_selector("#toast .toast-ic.ok") is not None)
    ls = pg.evaluate("localStorage.getItem('astroq-waitlist')")
    check("da luu ban sao du phong", ls and "phihanhgia@astroq.org" in ls and '"sent":true' in ls, ls)
    check("khong loi JS", pg.perr == [], pg.perr)
    # dang ky email khac
    pg.click("#wl-again")
    pg.wait_for_timeout(200)
    check("nut 'dang ky email khac' mo lai form", pg.get_attribute("#wl-form", "hidden") is None)
    check("o email da rong", pg.input_value("#wl-email") == "")
    b.close()

    # ---------------------------------------------------------------- [4] server tu choi
    print("\n[4] Server tu choi (400 invalid-email)")
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.route("**/waitlist", lambda r: r.fulfill(
        status=400, content_type="application/json",
        body='{"code":"invalid-email","message":"Email chua dung dinh dang."}'))
    pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg.goto(URL, wait_until="networkidle")
    pg.eval_on_selector("#waitlist", "e=>e.scrollIntoView({block:'center'})")
    pg.fill("#wl-email", "ai@do.com")
    pg.click("#wl-submit")
    pg.wait_for_timeout(800)
    t4 = (pg.inner_text("#wl-err") or "").strip()
    check("bao loi bang TIENG VIET, khong lo ma loi cua server", "Trạm mặt đất" in t4 and "invalid-email" not in t4, repr(t4))
    check("KHONG hien the 'da dang ky'", pg.get_attribute("#wl-done", "hidden") is not None)
    check("nut tro lai binh thuong", pg.eval_on_selector("#wl-submit", "e=>e.disabled") is False)
    ls4 = pg.evaluate("localStorage.getItem('astroq-waitlist')")
    check("van giu lead tren may (sent=false)", ls4 and '"sent":false' in ls4)
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()

    # ---------------------------------------------------------------- [5] mat mang
    print("\n[5] Mat ket noi")
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.route("**/waitlist", lambda r: r.abort())
    pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg.goto(URL, wait_until="networkidle")
    pg.eval_on_selector("#waitlist", "e=>e.scrollIntoView({block:'center'})")
    pg.fill("#wl-email", "mat@mang.vn")
    pg.click("#wl-submit")
    pg.wait_for_timeout(900)
    t5 = (pg.inner_text("#wl-err") or "").strip()
    check("bao mat ket noi", "Mất kết nối" in t5, repr(t5))
    check("nut khong ket o trang thai 'Dang gui...'",
          pg.eval_on_selector("#wl-submit", "e=>e.disabled") is False)
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()

    # ---------------------------------------------------------------- [6] EN + doi ngon ngu
    print("\n[6] Ban EN va doi ngon ngu giua chung")
    b, pg = new_page(pw, lang="en")
    pg.click("#wl-submit")
    pg.wait_for_timeout(250)
    t6 = (pg.inner_text("#wl-err") or "").strip()
    check("loi hien bang tieng Anh", "Enter your email" in t6, repr(t6))
    # Bam VI = DIEU HUONG sang `/` (link that, crawler di duoc). Trang moi khong
    # con loi cu — dieu can chung minh nay la: sang dung ban tieng Viet.
    with pg.expect_navigation(wait_until="load"):
        pg.click('.lang-switch [data-lang="vi"]')
    pg.wait_for_timeout(300)
    check("bam VI o ban EN thi DIEU HUONG sang ban tieng Viet",
          pg.evaluate("()=>document.documentElement.lang") == "vi", pg.url)
    pg.click("#wl-submit")
    pg.wait_for_timeout(250)
    t6b = (pg.inner_text("#wl-err") or "").strip()
    check("cau loi o ban VI la tieng Viet", "Nhập email" in t6b, repr(t6b))
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()

    # ---------------------------------------------------------------- [7] dien thoai
    print("\n[7] Dien thoai 390x844")
    b, pg = new_page(pw, width=390, height=844)
    pg.click("#wl-submit")
    pg.wait_for_timeout(250)
    eb = pg.query_selector("#wl-err").bounding_box()
    check("hop bao loi khong tran ngang", eb and eb["x"] >= 0 and eb["x"] + eb["width"] <= 390, eb)
    check("nam trong khung nhin", eb and 0 <= eb["y"] <= 844, eb)
    check("trang khong cuon ngang",
          pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
    pg.fill("#wl-email", "mobile@astroq.org")
    pg.click("#wl-submit")
    pg.wait_for_timeout(900)
    check("the 'da dang ky' hien tren dien thoai", pg.get_attribute("#wl-done", "hidden") is None)
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()

    # ---------------------------------------------------------------- [8] bay bot
    print("\n[8] Bay bot van con tac dung")
    b, pg = new_page(pw)
    pg.evaluate("document.getElementById('wl-gotcha').value='bot'")
    pg.fill("#wl-email", "bot@spam.io")
    pg.click("#wl-submit")
    pg.wait_for_timeout(600)
    check("bot dien bay -> KHONG gui gi", pg.posts == [], pg.posts)
    check("bot dien bay -> khong hien the thanh cong", pg.get_attribute("#wl-done", "hidden") is not None)
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()

    # ---------------------------------------------------------------- [9] server nhan nhung SES hong
    print("\n[9] Server nhan duoc nhung SES chua gui duoc thu (mailSent:false)")
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.route("**/waitlist", lambda r: r.fulfill(
        status=202, content_type="application/json",
        body='{"ok":true,"dup":false,"mailSent":false}'))
    pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg.goto(URL, wait_until="networkidle")
    pg.eval_on_selector("#waitlist", "e=>e.scrollIntoView({block:'center'})")
    pg.fill("#wl-email", "sesloi@astroq.org")
    pg.click("#wl-submit")
    pg.wait_for_timeout(900)
    d9 = pg.inner_text("#wl-done")
    check("van bao da giu cho", pg.get_attribute("#wl-done", "hidden") is None)
    check("KHONG bao 'kiem tra hom thu' ve mot la thu chua di", "Kiểm tra hòm thư" not in d9, repr(d9[:110]))
    check("noi that la thu dang truc trac", "trục trặc" in d9, repr(d9[:110]))
    check("van nhac dung email", "sesloi@astroq.org" in d9)
    # Bam EN = DIEU HUONG sang `/en/`. The "da dang ky" duoc dung lai tu
    # localStorage nen phai con nguyen cau "thu dang truc trac" o ban tieng Anh.
    with pg.expect_navigation(wait_until="load"):
        pg.click('.lang-switch [data-lang="en"]')
    pg.wait_for_timeout(700)
    d9b = pg.inner_text("#wl-done")
    check("doi sang EN van giu dung cau 'chua gui duoc'",
          "snag" in d9b and "Check your inbox" not in d9b, repr(d9b[:110]))
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()

    # ---------------------------------------------------------------- [10] goi THAT vao backend
    # Mac dinh danh vao BAN THAT tren AWS (do la duong nguoi dung that di). Backend
    # o may dang chay thi uu tien no de khoi ghi rac len ban that.
    print("\n[10] Goi THAT vao backend (khong gia lap phan hoi)")
    import urllib.request, urllib.error
    local_live = False
    try:
        with urllib.request.urlopen("http://localhost:5080/health", timeout=4) as r:
            local_live = r.status == 200
    except Exception:
        local_live = False
    api_q = "?api=local" if local_live else "?api=prod"
    print("  (dung %s)" % ("backend o may" if local_live else "BAN THAT tren AWS"))
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.perr = []
    pg.cerr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.on("console", lambda m: pg.cerr.append(m.text) if m.type == "error" else None)
    pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
    # ⚠️ Dia chi gia lap cua SES: gui vao dia chi khong ton tai la sinh bounce,
    #    ty le bounce cao thi AWS khoa quyen gui cua CA tai khoan.
    mail = "success+smoke@simulator.amazonses.com"
    pg.goto(URL + api_q, wait_until="networkidle")
    pg.eval_on_selector("#waitlist", "e=>e.scrollIntoView({block:'center'})")
    pg.fill("#wl-email", mail)
    pg.click("#wl-submit")
    pg.wait_for_timeout(4000)
    check("khong bi CORS chan (khong loi console)", pg.cerr == [], pg.cerr)
    check("the 'da dang ky' hien ra tu phan hoi THAT",
          pg.get_attribute("#wl-done", "hidden") is None)
    check("bao 'kiem tra hom thu' (SES that su da nhan thu)",
          "Kiểm tra hòm thư" in pg.inner_text("#wl-done"))
    check("khong loi JS", pg.perr == [], pg.perr)
    b.close()
    # don ban ghi vua tao
    import subprocess as _sp
    _sp.run(["aws", "dynamodb", "delete-item", "--table-name", "astroq-main", "--key",
             json.dumps({"PK": {"S": "WAITLIST#" + mail}, "SK": {"S": "SIGNUP"}})],
            capture_output=True, text=True)
    left = _sp.run(["aws", "dynamodb", "get-item", "--table-name", "astroq-main", "--key",
                    json.dumps({"PK": {"S": "WAITLIST#" + mail}, "SK": {"S": "SIGNUP"}}),
                    "--output", "json"], capture_output=True, text=True).stdout.strip()
    check("da don ban ghi test khoi DynamoDB", left in ("", "{}"), left[:80])

print("\n================ KET QUA: %d dat / %d hong ================" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
