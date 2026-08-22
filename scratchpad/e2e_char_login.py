# -*- coding: utf-8 -*-
"""e2e_char_login.py — DANG NHAP THAT roi xem `go()` dua di dau.

VI SAO CAN BO DO NAY
--------------------
Ba bo do khac deu xanh ma van khong tra loi duoc cau chu du an hoi
("dang nhap lai van phai chon nhan vat"), vi khong bo nao di qua doan
"tu cau tra loi cua server VAO cache" bang mot lan DANG NHAP THAT:
  - `check_char_sync.py`  : gia lap `auth`, khong qua Firebase.
  - `probe_char_e2e.py`   : do API, khong qua trinh duyet.
  - `smoke_*`             : gia lap CHINH `AstroQAuth`, tuc do mot lop
                            KHONG phai lop dang chay that.
Bo nay: tao tai khoan Firebase that + gieo `character` vao DynamoDB, roi mo
`landing-app.html?api=local`, dien form, va do dung hai thu tre thay:
`astroq-user.character` va trang dich.

Can:  backend chay o may (cong 5080) + may chu tinh o cong 8000
      (8000 nam trong ALLOWED_ORIGINS, 8123 thi KHONG -> CORS chan).

  python -m http.server 8000        # trong AstroQhtml/
  dotnet run                        # trong AstroqSV/src/AstroqSV.Api
  python scratchpad/e2e_char_login.py
"""
import json
import pathlib
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
import _fbtest  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

BASE = "http://127.0.0.1:8000"

# `--prod` -> tro API len ban that thay vi backend o may. Dung truoc khi push
# client: no do dung cap **client MOI + server MOI**.
# ⚠️ Trang van mo tu may chu tinh o may (client chua push), chi doi dich API.
API_MODE = "prod" if "--prod" in sys.argv else "local"
LANDING = "/landing-app.html?api=" + API_MODE
TABLE = "astroq-main"
_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [HONG] ") + name
          + (("  [" + str(extra) + "]") if extra else ""))


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True, timeout=60)


def read_char(uid):
    """Doc THANG tu DynamoDB — khong tin loi khai cua API."""
    r = aws("dynamodb", "get-item", "--table-name", TABLE, "--consistent-read",
            "--key", json.dumps({"PK": {"S": "USER#" + uid}, "SK": {"S": "PROFILE"}}),
            "--projection-expression", "#c,#a,#n",
            "--expression-attribute-names", json.dumps({"#c": "character", "#a": "avatar",
                                                        "#n": "name"}))
    if r.returncode != 0:
        return {}
    it = json.loads(r.stdout or "{}").get("Item", {})
    return {k: v.get("S") for k, v in it.items()}


def put_profile(uid, email, char, name, old_kid=False):
    item = {
        "PK": {"S": "USER#" + uid}, "SK": {"S": "PROFILE"},
        "uid": {"S": uid}, "email": {"S": email}, "name": {"S": name},
        "depth": {"S": "senior"},
        "createdAt": {"S": "2026-08-22T00:00:00.000Z"},
    }
    if char:
        item["character"] = {"S": char}
        item["avatar"] = {"S": "ava/avacua.png"}
    if old_kid:
        # Tre CU: da di qua man dan duong, da xem tour.
        item["map01Seen"] = {"BOOL": True}
        item["tourSeen"] = {"BOOL": True}
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(item))
    return r.returncode == 0, r.stderr.strip()


def purge(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": "USER#" + uid}}),
            "--projection-expression", "PK,SK", "--consistent-read")
    if r.returncode != 0:
        return 0
    items = json.loads(r.stdout or "{}").get("Items", [])
    for it in items:
        aws("dynamodb", "delete-item", "--table-name", TABLE,
            "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
    return len(items)


def do_login(pg, email, pw):
    """Dang nhap roi CHO ROI trang landing-app.

    ⚠️ Han cho 60s, khong phai 30s: `login()` nay `await hydrateProfile` (toi
       HYDRATE_MS = 5s) roi `go()` con hen 900ms nua, cong lai voi mot chang
       mang cham la vuot 30s — do duoc chap chon ~1/3 luot voi han cu.
    ⚠️ Het han thi TU KHAI TRANG THAI (quy tac 6 muc 6): mot `TimeoutError`
       tran doc ra y nhu san pham hong."""
    pg.click("#btn-try")
    pg.wait_for_timeout(300)
    pg.click("#to-login")
    pg.wait_for_selector("#login-email", state="visible", timeout=10000)
    pg.fill("#login-email", email)
    pg.fill("#login-pass", pw)
    pg.click("#auth-login button.auth-submit")
    try:
        pg.wait_for_url(lambda u: "landing-app.html" not in u, timeout=60000)
    except Exception:
        print("     [!] khong roi landing-app trong 60s")
        print("         url   : " + pg.url)
        try:
            print("         toast : " + (pg.inner_text("#auth-toast") or "").strip()[:160])
        except Exception:
            pass
        try:
            print("         nut   : " + (pg.inner_text("#auth-login .auth-submit") or "").strip())
        except Exception:
            pass
        raise
    pg.wait_for_load_state("load")


def main():
    t = int(time.time())
    email = "charlogin-%d@simulator.amazonses.com" % t
    email2 = "charnew-%d@simulator.amazonses.com" % t
    email3 = "charold-%d@simulator.amazonses.com" % t
    uid, _tok, pw = _fbtest.make_verified(email)
    uid2, _tok2, pw2 = _fbtest.make_verified(email2)
    uid3, _tok3, pw3 = _fbtest.make_verified(email3)
    print("uid  = " + uid + "   (da co nhan vat tren server)")
    print("uid2 = " + uid2 + "   (chua co nhan vat)")
    print("uid3 = " + uid3 + "   (tre CU, ho so THIEU nhan vat)")
    print("")
    print("[1] tre CU: dang nhap lai co con phai chon nhan vat khong?")
    made, err = put_profile(uid, email, "cua", "Bin")
    chk("gieo ho so co nhan vat 'cua' + bac 'senior'", made, err)

    try:
        with sync_playwright() as p:
            br = p.chromium.launch()
            ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
            # ⚠️ Gieo hai cờ onboarding: tài khoản MỚI thì `mapFirst()` đẩy thẳng
            #    sang `explorer.html?onboard=1` — hành vi ĐÚNG của sản phẩm, nhưng
            #    nó rời dashboard trước khi cầu nối chạy xong, tức sai chỗ để đo.
            ctx.add_init_script(
                "localStorage.setItem('astroq-lang','vi');"
                "localStorage.setItem('astroq-map01-seen','1');"
                "localStorage.setItem('astroq-tour-seen','1');")
            pg = ctx.new_page()
            perr = []
            pg.on("pageerror", lambda e: perr.append(str(e)))

            # ?api=local -> js/api.js nho lua chon vao localStorage["astroq-api"]
            pg.goto(BASE + LANDING, wait_until="load")
            pg.wait_for_timeout(400)
            chk("truoc khi dang nhap: cache KHONG co nhan vat",
                pg.evaluate("() => { var u=JSON.parse(localStorage.getItem('astroq-user')"
                            "||'null'); return !u || !u.character; }"))

            do_login(pg, email, pw)
            url = pg.url
            chk("dang nhap xong -> vao DASHBOARD (khong phai select.html)",
                url.endswith("dashboard.html"), url)

            u = pg.evaluate("() => JSON.parse(localStorage.getItem('astroq-user')||'null')")
            chk("cache co nhan vat tu server", (u or {}).get("character") == "cua",
                (u or {}).get("character"))
            chk("cache co alias selectedCharacter",
                (u or {}).get("selectedCharacter") == "cua")
            chk("cache co avatar tu server", (u or {}).get("avatar") == "ava/avacua.png",
                (u or {}).get("avatar"))
            chk("cache co ten tu server", (u or {}).get("name") == "Bin", (u or {}).get("name"))
            chk("cache co BAC tu server (lab.html doc duoc)",
                (u or {}).get("depth") == "senior", (u or {}).get("depth"))
            # zoom la luat cua characters.js, server khong luu -> khong duoc doan o day
            chk("hydrate KHONG doan avatarZoom", "avatarZoom" not in (u or {}))
            chk("0 loi trang", not perr, "; ".join(perr[:2]))

            # Dashboard chay cau noi -> hai ben da khop nen phai DONG DAU, khong PUT lai
            pg.wait_for_timeout(3000)
            print("     url sau 3s: " + pg.url)
            print("     stamp     : "
                  + repr(pg.evaluate("() => localStorage.getItem('astroq-char-synced')")))
            print("     map01     : "
                  + repr(pg.evaluate("() => localStorage.getItem('astroq-map01-seen')")))
            chk("hai ben khop -> dashboard dong dau (khoi PUT vo nghia)",
                pg.evaluate("() => localStorage.getItem('astroq-char-synced')") == uid,
                pg.evaluate("() => localStorage.getItem('astroq-char-synced')"))
            ctx.close()

            # ══════════════════════════════════════════════════════════════
            # KICH BAN 2 — CHIEU CON LAI (lo hong [A]): tre MOI chon nhan vat
            # o select.html (trang KHONG co token) thi server co nhan duoc khong.
            # ══════════════════════════════════════════════════════════════
            print("")
            print("[2] tre MOI: select.html -> server co nhan duoc nhan vat?")
            purge(uid2)
            made2, err2 = put_profile(uid2, email2, "", "Chua dat")
            chk("gieo ho so KHONG co nhan vat", made2, err2)
            chk("truoc: DynamoDB chua co nhan vat", not read_char(uid2).get("character"),
                read_char(uid2))

            # ⚠️ KHONG gieo `astroq-map01-seen` o kich ban nay: day la tre MOI, va
            #    co do CHINH LA thu `returning()` doc de biet cu hay moi. Gieo vao
            #    la phep do tu noi sai ve thu no dang do (do duoc: dich den ra
            #    dashboard.html thay vi explorer.html?onboard=1).
            ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
            ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
            pg = ctx.new_page()
            perr2 = []
            pg.on("pageerror", lambda e: perr2.append(str(e)))

            pg.goto(BASE + LANDING, wait_until="load")
            do_login(pg, email2, pw2)
            chk("server chua co nhan vat -> dua ve SELECT (dung, khong bia)",
                pg.url.endswith("select.html"), pg.url)

            # Chon nhan vat + dat ten nhu tre lam
            pg.wait_for_selector('.char[data-id="cua"]', timeout=8000)
            pg.click('.char[data-id="cua"]')
            pg.fill("#pilot-name", "Bin")
            pg.click("#age-senior")
            # ⚠️ Gieo mot dau GIA truoc khi bam: khong gieo thi dau von da rong,
            #    va phep kiem "touch() co xoa dau khong" dat mot cach RONG.
            pg.evaluate("() => localStorage.setItem('astroq-char-synced','dau-cu')")
            pg.click("#start-journey")
            pg.wait_for_timeout(400)          # start-journey doi 1150ms moi dieu huong
            chk("select.html: chon xong thi XOA dau 'da gui' (AstroQChars.touch)",
                pg.evaluate("() => localStorage.getItem('astroq-char-synced')") is None,
                pg.evaluate("() => localStorage.getItem('astroq-char-synced')"))
            pg.wait_for_url("**/explorer.html*", timeout=30000)
            chk("tre MOI van di dung duong onboarding cu (returning() khong ban bua)",
                "onboard=1" in pg.url, pg.url)

            # Ve dashboard (trang CO token) -> cau noi phai DAY len.
            # Gieo co onboarding NGAY BAY GIO de `mapFirst()` khong day tro lai
            # explorer — den day thi thu can do khong con la dich den nua.
            pg.evaluate("() => { localStorage.setItem('astroq-map01-seen','1');"
                        "localStorage.setItem('astroq-tour-seen','1'); }")
            pg.goto(BASE + "/dashboard.html", wait_until="load")
            pg.wait_for_timeout(3500)
            got = read_char(uid2)
            chk("DynamoDB NAY DA CO nhan vat (lo hong [A] da bit)",
                got.get("character") == "cua", got)
            chk("server nhan ca avatar", got.get("avatar") == "ava/avacua.png", got.get("avatar"))
            chk("server nhan ca ten tre tu dat", got.get("name") == "Bin", got.get("name"))
            chk("day xong thi dong dau (khong day lai luot sau)",
                pg.evaluate("() => localStorage.getItem('astroq-char-synced')") == uid2,
                pg.evaluate("() => localStorage.getItem('astroq-char-synced')"))
            chk("0 loi trang (kich ban 2)", not perr2, "; ".join(perr2[:2]))
            ctx.close()

            # ══════════════════════════════════════════════════════════════
            # KICH BAN 3 — TRE CU ma ho so tren server THIEU `character`
            # (moi tre dang ky truoc 22/08/2026 chua vao profile.html lan nao).
            # Buoc chon lai la KHONG TRANH DUOC (du lieu khong con o dau ca),
            # nhung KHONG duoc nem no lai vao man onboarding, va khong duoc
            # goi day la "cap the ID moi".
            # ══════════════════════════════════════════════════════════════
            print("")
            print("[3] tre CU thieu nhan vat: co bi bat bat dau lai tu dau khong?")
            purge(uid3)
            made3, err3 = put_profile(uid3, email3, "", "Nhi", old_kid=True)
            chk("gieo ho so tre CU: co ten + bac + map01Seen, KHONG co nhan vat", made3, err3)

            # KHONG gieo co onboarding vao localStorage — phai do dung viec
            # `hydrateProfile()` co keo co tu server ve hay khong.
            ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
            ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
            pg = ctx.new_page()
            perr3 = []
            pg.on("pageerror", lambda e: perr3.append(str(e)))

            pg.goto(BASE + LANDING, wait_until="load")
            do_login(pg, email3, pw3)
            chk("server thieu nhan vat -> qua select.html (khong bia mot con)",
                pg.url.endswith("select.html"), pg.url)
            pg.wait_for_selector('.char[data-id="cua"]', timeout=8000)
            pg.wait_for_timeout(400)

            chk("hydrate keo co onboarding ve cache",
                pg.evaluate("() => localStorage.getItem('astroq-map01-seen')") == "1",
                pg.evaluate("() => localStorage.getItem('astroq-map01-seen')"))
            chk("TEN dien san tu server (khong phai go lai)",
                pg.input_value("#pilot-name") == "Nhi", pg.input_value("#pilot-name"))
            chk("BAC TUOI chon san tu server (khong phai khai lai)",
                pg.eval_on_selector("#age-senior", "e => e.classList.contains('active')"))
            chk("cau chu KHONG goi day la cap the ID moi",
                "CẤP THẺ ID" not in pg.inner_text('[data-i18n="title"]'),
                pg.inner_text('[data-i18n="title"]'))
            chk("cau chu noi dung viec: chon LAI nhan vat",
                "LẠI" in pg.inner_text('[data-i18n="title"]').upper(),
                pg.inner_text('[data-i18n="title"]'))
            chk("nut noi TIEP TUC, khong phai BAT DAU",
                "TIẾP TỤC" in pg.inner_text("#start-journey").upper(),
                pg.inner_text("#start-journey"))

            pg.click('.char[data-id="cua"]')
            pg.click("#start-journey")
            pg.wait_for_url(lambda u: "select.html" not in u, timeout=30000)
            chk("tre CU ve THANG khoang lai, KHONG bi nem lai vao man dan duong",
                pg.url.endswith("dashboard.html"), pg.url)
            pg.wait_for_timeout(3500)
            got3 = read_char(uid3)
            chk("va nhan vat vua chon DA len server (khong hoi lan thu ba)",
                got3.get("character") == "cua", got3)
            chk("0 loi trang (kich ban 3)", not perr3, "; ".join(perr3[:2]))
            br.close()
    finally:
        for u in (uid, uid2, uid3):
            try:
                print("  (don %d dong DynamoDB cho %s)" % (purge(u), u[:8]))
            except Exception as e:
                print("  (!) " + str(e))
        for em, p_ in ((email, pw), (email2, pw2), (email3, pw3)):
            try:
                _fbtest.delete(_fbtest.signin(em, p_))
            except Exception:
                pass

    print("\n=== KET QUA: %d dat / %d hong ===" % (_n["ok"], _n["ng"]))
    return 1 if _n["ng"] else 0


if __name__ == "__main__":
    sys.exit(main())
