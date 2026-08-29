# -*- coding: utf-8 -*-
"""e2e_login_notactivated.py — CHUA KICH HOAT MA DANG NHAP THI TRANG NOI GI?

    python -m http.server 8000        # trong AstroQhtml/
    dotnet run                        # trong AstroqSV/src/AstroqSV.Api
    python scratchpad/e2e_login_notactivated.py
    python scratchpad/e2e_login_notactivated.py --prod   # doi dich API len ban that

VI SAO CAN BO DO NAY (29/08/2026)
---------------------------------
`test_auth_status.py` do ENDPOINT, va no xanh. Nhung cau hoi cua du an la mot
cau ve MAN HINH: "khach chua verify qua email thi khi dang nhap co duoc bao
dung khong". Giua endpoint va man hinh con ba lop nua co the nuot mat cau tra
loi — `CRED_CODES` co khop ma Firebase that su tra ve khong, `pendingState` co
duoc goi khong, toast co hien khong. Bo nay di qua ca ba: trinh duyet that,
Firebase that, backend that.

DOI CHUNG LA PHAN QUAN TRONG NHAT. Ca "sai mat khau that" PHAI van nhan cau
"Email hoac mat khau khong dung." — neu khong thi ban va nay chi doi mot cau
sai lay mot cau sai khac, va lan nay no sai voi nguoi go nham mat khau.

⚠️ Dung dia chi gia lap cua SES (`success+…@simulator.amazonses.com`) — gui vao
   dia chi khong ton tai la sinh bounce, ma bounce nhieu thi AWS khoa quyen gui
   cua CA tai khoan. Cung luat da ghi o `test_login_hash.py`.
⚠️ KHONG bam link kich hoat — do la chinh cai trang thai dang do.
⚠️ Ban ghi cho duoc DON trong `finally`, ke ca khi phep do hong giua duong.
"""
import json
import subprocess
import sys
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright  # noqa: E402

BASE = "http://127.0.0.1:8000"
API_MODE = "prod" if "--prod" in sys.argv else "local"
LANDING = "/landing-app.html?api=" + API_MODE
TABLE = "astroq-main"
PW = "Astroq!2026-kiemtra"

_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [HONG] ") + name
          + (("  [" + str(extra) + "]") if extra else ""))


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True, timeout=60)


def pane_text(pg):
    """Ba thu tre thay: tieu de + mo ta cua pane, va cau toast."""
    return {
        "visible": pg.is_visible("#auth-verify"),
        "title": (pg.inner_text("#auth-verify .auth-title") or "").strip(),
        "sub": (pg.inner_text("#auth-verify .auth-sub") or "").strip(),
        "mail": (pg.inner_text("#verify-mail") or "").strip(),
        "toast": (pg.inner_text("#auth-toast") or "").strip(),
    }


def expire_pending(email):
    """Keo `expiresAt` cua ban ghi cho ve qua khu — khong thi phai cho 10 phut.

    Sua DUNG mot truong tren ban ghi THAT roi van di qua DUNG luong that; khong
    gia lap buoc nao cua client lan cua route. Cung thu doan voi
    `test_auth_status.py` muc [5]."""
    r = aws("dynamodb", "get-item", "--table-name", TABLE, "--consistent-read",
            "--key", json.dumps({"PK": {"S": "PENDING#%s" % email},
                                 "SK": {"S": "SIGNUP"}}))
    if r.returncode:
        return False
    it = (json.loads(r.stdout or "{}") or {}).get("Item")
    if not it:
        return False
    it["expiresAt"] = {"N": "1000000000"}      # 2001, chac chan da qua
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


def open_login(pg):
    """`#btn-try` mo pane DANG KY khi may chua co ho so nao — phai bam them
    `#to-login` moi sang duoc o dang nhap (xem landing-app.html)."""
    pg.click("#btn-try")
    pg.wait_for_timeout(300)
    pg.click("#to-login")
    pg.wait_for_selector("#login-email", state="visible", timeout=10000)


def try_login(pg, email, pw):
    """Bam Dang nhap roi CHO THEO TIN HIEU THAT, khong theo dong ho.

    ⚠️ BAN DAU BO NAY NGU 9 GIAY CO DINH, va no XANH o may nhung DO tren prod
       (29/08/2026): duong nay di Firebase (that bai) ROI moi hoi `/auth/status`
       — hai vong mang, va vong thu hai co the roi vao mot Lambda nguoi. Cho
       bang dong ho thi bo do dang bao "trang khong noi gi" trong khi that ra
       no chua noi KIP. Tin hieu that la nut submit duoc mo khoa lai
       (`busy(form,false)` trong js/firebase-auth-ui.js), tuc `login()` da tra ve."""
    open_login(pg)
    pg.fill("#login-email", email)
    pg.fill("#login-pass", pw)
    pg.click("#auth-login button.auth-submit")
    # ⚠️ CHO TIN HIEU DUONG (co chu trong toast, hoac pane cho kich hoat hien ra),
    #    KHONG cho "nut submit duoc mo khoa lai". Ban truoc cho theo nut va no DO
    #    chap chon tren prod: `busy(form,true)` chay trong chinh trinh xu ly submit,
    #    nen co luot `wait_for_function` do TRUOC khi nut kip khoa -> dieu kien
    #    "khong disabled" dung NGAY, bo do doc man hinh luc chua co gi va bao
    #    "trang khong noi gi". Cho mot thu XUAT HIEN thi khong co cua dua nao.
    #    ⚠️ Moi buoc deu `pg.goto` lai truoc khi goi ham nay, nen toast chac chan
    #       rong luc bat dau — khong co chuyen an nham cau cua buoc truoc.
    pg.wait_for_function(
        "() => { const t = document.querySelector('#auth-toast');"
        "        const v = document.querySelector('#auth-verify');"
        "        return !!((t && t.textContent.trim()) || (v && !v.hidden)); }",
        timeout=60000)
    pg.wait_for_timeout(400)      # de ca toast LAN pane cung kip ve DOM
    return pane_text(pg)


email = "success+e2e-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
print("API: %s   ·   email: %s" % (API_MODE, email))

try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        # ⚠️ EP TIENG VIET. Bo do nay doi tung cau chu, ma `guessLang` (js/ui-common.js)
        #    doc `navigator.language` khi chua co lua chon nao luu — Chromium headless
        #    tra "en-US", nen khong ep thi ca bo do xanh/do theo locale cua may chay
        #    no, chu khong theo ma nguon.
        pg.add_init_script(
            "try{ localStorage.setItem('astroq-lang','vi'); }catch(e){}")
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        print("\n=== [1] Dang ky, va CO Y KHONG bam link kich hoat ===")
        pg.goto(BASE + LANDING, wait_until="domcontentloaded")
        pg.click("#btn-try")          # may sach -> mo thang pane DANG KY
        pg.wait_for_selector("#reg-email", state="visible", timeout=10000)
        pg.fill("#reg-name", "Kiem Tra")
        pg.fill("#reg-email", email)
        pg.fill("#reg-pass", PW)
        pg.click("#auth-register button.auth-submit")
        pg.wait_for_selector("#auth-verify", state="visible", timeout=30000)
        v = pane_text(pg)
        chk("dang ky xong hien pane cho kich hoat", v["visible"])
        chk("pane giu nguyen chu MAC DINH cua ca 'vua gui thu'",
            "vừa gửi" in v["sub"], v["sub"][:60])
        chk("va hien dung email vua dang ky", v["mail"] == email, v["mail"])

        print("\n=== [2] MO LAI TRANG roi dang nhap bang DUNG mat khau ===")
        print("      Day la ca that: tai khoan chua ton tai tren Firebase, nen")
        print("      `signInWithEmailAndPassword` se tra `auth/invalid-credential`.")
        pg.goto(BASE + LANDING, wait_until="domcontentloaded")
        v = try_login(pg, email, PW)
        chk("KHONG noi 'Email hoac mat khau khong dung'",
            "không đúng" not in v["toast"], v["toast"][:70])
        chk("noi ro la CHUA KICH HOAT (toast)",
            "chưa kích hoạt" in v["toast"], v["toast"][:70])
        chk("va noi ro mat khau KHONG sai",
            "không sai" in v["toast"], v["toast"][:70])
        chk("dua sang pane cho kich hoat", v["visible"])
        chk("tieu de pane doi thanh 'Tai khoan chua kich hoat'",
            v["title"] == "Tài khoản chưa kích hoạt", v["title"])
        chk("mo ta pane KHONG con cau 'vua gui thu' cua ca dang ky",
            "vừa gửi" not in v["sub"], v["sub"][:60])
        chk("dien san email de bam 'Gui lai link' duoc", v["mail"] == email, v["mail"])
        chk("khong vao duoc app (van o landing-app)",
            "landing-app" in pg.url, pg.url)

        print("\n=== [2b] HOI QUY: dang ky NGAY SAU do phai lay lai chu MAC DINH ===")
        print("      `showVerify` go `data-i18n` khoi hai the de dat chu rieng.")
        print("      Khong tra lai tu te thi ca dang ky ke tiep se doc mot cau")
        print("      cua ca dang nhap — va no chi lo ra o dung thu tu nay.")
        pg.click("#verify-back")
        pg.wait_for_selector("#login-email", state="visible", timeout=10000)
        pg.click("#to-register")
        pg.wait_for_selector("#reg-email", state="visible", timeout=10000)
        pg.fill("#reg-name", "Kiem Tra")
        pg.fill("#reg-email", email)
        pg.fill("#reg-pass", PW)
        pg.click("#auth-register button.auth-submit")
        pg.wait_for_selector("#auth-verify", state="visible", timeout=60000)
        v = pane_text(pg)
        chk("tieu de tro lai mac dinh",
            v["title"] == "Kiểm tra hòm thư của bạn", v["title"])
        chk("mo ta tro lai cau 'vua gui thu'",
            "vừa gửi" in v["sub"], v["sub"][:60])
        chk("khong con sot cau cua ca dang nhap",
            "Mật khẩu của bạn đúng rồi" not in v["sub"], v["sub"][:60])

        print("\n=== [3] LINK HET HAN phai noi mot cau KHAC ===")
        print("      Viec can lam khac nhau: con han thi thu dang nam trong hom,")
        print("      het han thi phai bam 'Gui lai link' moi co link song.")
        chk("keo duoc expiresAt ve qua khu", expire_pending(email))
        pg.goto(BASE + LANDING, wait_until="domcontentloaded")
        v = try_login(pg, email, PW)
        chk("van khong noi 'Email hoac mat khau khong dung'",
            "không đúng" not in v["toast"], v["toast"][:70])
        chk("noi ro LINK DA HET HAN", "hết hạn" in v["toast"], v["toast"][:70])
        chk("va moi bam 'Gui lai link'", "Gửi lại link" in v["toast"], v["toast"][:70])
        chk("mo ta pane cung la cau cua ca het han",
            "hết hạn" in v["sub"], v["sub"][:60])
        chk("nut 'Gui lai link' co that de bam", pg.is_visible("#verify-resend"))

        print("\n=== [4] DOI CHUNG: sai mat khau THAT van phai bao sai ===")
        print("      Ca nay ma cung bao 'chua kich hoat' thi ban va chi doi")
        print("      mot cau sai lay mot cau sai khac.")
        pg.goto(BASE + LANDING, wait_until="domcontentloaded")
        v = try_login(pg, email, PW + "-sai")
        chk("van bao 'Email hoac mat khau khong dung'",
            "không đúng" in v["toast"], v["toast"][:70])
        chk("KHONG dua sang pane cho kich hoat", not v["visible"], v["toast"][:50])

        print("\n=== [5] DOI CHUNG: email chua he dang ky ===")
        pg.goto(BASE + LANDING, wait_until="domcontentloaded")
        v = try_login(pg, "success+khongton-%s@simulator.amazonses.com"
                      % uuid.uuid4().hex[:8], PW)
        chk("van bao 'Email hoac mat khau khong dung'",
            "không đúng" in v["toast"], v["toast"][:70])
        chk("KHONG dua sang pane cho kich hoat", not v["visible"], v["toast"][:50])

        print("\n=== [6] Khong co loi JS nao trong ca luot do ===")
        chk("console sach", not errs, "; ".join(errs[:2]))

        br.close()

finally:
    print("\n=== [7] Don du lieu test ===")
    aws("dynamodb", "delete-item", "--table-name", TABLE, "--key",
        json.dumps({"PK": {"S": "PENDING#%s" % email}, "SK": {"S": "SIGNUP"}}))
    print("      xong")

print("\n%d/%d dat" % (_n["ok"], _n["ok"] + _n["ng"]))
sys.exit(1 if _n["ng"] else 0)
