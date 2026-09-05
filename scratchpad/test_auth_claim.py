# -*- coding: utf-8 -*-
"""test_auth_claim.py -- NHAN TIEN DO BANG DUNG MOT O EMAIL, DO BANG SO.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_auth_claim.py --api local
    python scratchpad/test_auth_claim.py                # API prod
    python scratchpad/test_auth_claim.py --keep         # khong don tai khoan thu

VIEC 3 CUA BAN DUYET 04/09/2026
-------------------------------
Duong choi thu khong can dang nhap: tre choi 3 chang, tien do nam trong
`astroq-progress-queue` o may, roi cuoi duong moi "Luu tien do cua con" va CHI
hoi mot o email. Route `/auth/claim` la nua server cua buoc do.

⚠️⚠️ PHEP KIEM QUAN TRONG NHAT LA [2] VA [8], VA CHUNG DO HAI NUA CUA CUNG MOT
   QUYET DINH. Khong co mat khau thi khong co gi de `signInWithPassword`, ma
   khong co phien thi `flush()` khong gui duoc hang cho -- tuc dung cai thu vua
   hua cuu ("Luu tien do cua con") la thu mat. Duong vao phien o day la
   **custom token**. [2] doi no phai DOI DUOC lay phien that; [8] doi mat khau
   ngau nhien server tu sinh phai KHONG BAO GIO ve tay client duoi bat ky dang
   nao -- tra no ve la bien mot o trong co khoa thanh mot bi mat bi ro ri.

⚠️ [6] LA CHO DE BO SOT NHAT: qua khoi dau 100 tt VAN chi cap sau khi bam link
   (luat cua viec 2, khong duoc noi long o day). Tre choi thu xong nhan duoc
   TIEN DO, khong phai QUA. Do "> 0" thi bo do van xanh khi server phat qua som.

⚠️ NHAN TEST `zzclaim*` + hom thu gia `@simulator.amazonses.com` cua chinh AWS:
   `success+<nhan>` duoc nhan thanh cong, KHONG tinh vao bounce. Dung
   `@example.com` la moi luot chay cong mot bounce that vao ti le cua CA tai
   khoan AWS -- ma ti le do cao thi AWS khoa quyen gui, tuc lam chet dung duong
   thu ma bo do nay dang canh. Bai hoc da ghi o `probe_register_now.py`.

⚠️ BO DO TU DON: tai khoan thu bi xoa o cuoi (Firebase + DynamoDB + cho giu
   email + dau qua). Bai hoc 16/08/2026 -- `e2e_certificate` tung de lai tai
   khoan that trong DB.

⚠️ `aws` CLI cung la Python: khong dat PYTHONIOENCODING thi CHINH NO chet o chu
   Viet va tra ve JSON CUT GIUA CHUNG.
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROD_API  = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
LOCAL_API = "http://localhost:5080"
FB_KEY    = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
FB_BASE   = "https://identitytoolkit.googleapis.com/v1/accounts:"
TABLE     = "astroq-main"

_n = {"ok": 0, "ng": 0}
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


def uid_from_token(id_token):
    """uid doc tu chinh payload cua ID token.

    ⚠⚠ KHONG DOC `localId` cua `signInWithCustomToken`: endpoint do
       tra ve DUNG `idToken`/`refreshToken`/`expiresIn`/`isNewUser` -- khong he
       co `localId` (chi `signInWithPassword` moi co). Doc nham thi uid ra
       RONG, va cai gia khong phai la mot phep kiem do: moi phep tra DynamoDB
       sau do hoi `USER#` (khong co gi) nen 4 phep bao hong OAN con 2 phep cua
       muc [6] thi DAT MOT CACH RONG -- chung "chung minh" qua chua duoc cap
       bang cach nhin vao mot khoa khong ton tai.
    """
    try:
        p = id_token.split(".")[1]
        p += "=" * (-len(p) % 4)
        d = json.loads(base64.urlsafe_b64decode(p).decode("utf-8", "replace"))
        return d.get("user_id") or d.get("sub") or ""
    except Exception:
        return ""


def http(url, body=None, token=None, method=None, redirect=True):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data,
                                 method=method or ("POST" if data is not None else "GET"))
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)

    opener = urllib.request.build_opener()
    if not redirect:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=30) as r:
            raw, code, hdr = r.read().decode("utf-8", "replace"), r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        raw, code, hdr = e.read().decode("utf-8", "replace"), e.code, dict(e.headers)
    except Exception as e:
        return 0, str(e), {}
    try:
        return code, json.loads(raw), hdr
    except Exception:
        return code, raw, hdr


def aws(args, allow_fail=False):
    p = subprocess.run(["aws"] + args + ["--output", "json", "--no-cli-pager"],
                       capture_output=True, text=False, shell=True, env=ENV)
    raw = p.stdout.decode("utf-8", "replace").strip()
    if p.returncode != 0 or not raw:
        if not allow_fail:
            print("  [..]   lenh aws that bai: " + " ".join(args[:3]))
            print("         " + p.stderr.decode("utf-8", "replace").strip()[:300])
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def item(pk, sk):
    r = aws(["dynamodb", "get-item", "--table-name", TABLE,
             "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}})], allow_fail=True)
    return (r or {}).get("Item")


def drop(pk, sk):
    aws(["dynamodb", "delete-item", "--table-name", TABLE,
         "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}})], allow_fail=True)


def main():
    api = PROD_API
    if "--api" in sys.argv:
        v = sys.argv[sys.argv.index("--api") + 1]
        api = LOCAL_API if v == "local" else (PROD_API if v == "prod" else v)
    keep = "--keep" in sys.argv

    stamp = str(int(time.time()))
    email = "success+zzclaim-" + stamp + "@simulator.amazonses.com"
    uid   = ""
    tok   = ""

    print("\n[0] TAI KHOAN THU: " + email)
    print("      API: " + api)

    try:
        # ═══════════════════════════════════════════════════════════════════
        print("\n[1] CHI MOT O EMAIL -> CO TAI KHOAN")
        code, body, _ = http(api + "/auth/claim",
                             {"email": email, "name": "Khach Thu", "src": "zzclaim/probe"})
        chk("`/auth/claim` tra 200", code == 200, "ma " + str(code))
        if not isinstance(body, dict):
            print("      than tra ve khong phai JSON -> dung: " + str(body)[:200])
            sys.exit(1)
        chk("noi ro DA CO tai khoan (`account`)", body.get("account") is True, body.get("account"))
        chk("noi ro CHUA xac minh", body.get("emailVerified") is False, body.get("emailVerified"))
        chk("co `customToken` de doi lay phien", bool(body.get("customToken")))
        print("      loi nhan: " + str(body.get("message"))[:120])

        # ═══════════════════════════════════════════════════════════════════
        print("\n[2] CUSTOM TOKEN DOI DUOC LAY PHIEN THAT")
        ct = body.get("customToken") or ""
        code, sess, _ = http(FB_BASE + "signInWithCustomToken?key=" + FB_KEY,
                             {"token": ct, "returnSecureToken": True})
        ok_sess = code == 200 and isinstance(sess, dict) and sess.get("idToken")
        chk("`signInWithCustomToken` tra ve idToken", bool(ok_sess),
            "" if ok_sess else str(sess)[:200])
        if not ok_sess:
            print("\n===== %d OK - %d HONG =====" % (_n["ok"], _n["ng"]))
            sys.exit(1)
        tok = sess["idToken"]
        print("      truong sess tra ve: " + ", ".join(sorted(sess.keys())))
        uid = uid_from_token(tok)
        chk("phien mang dung uid do server tao", uid.startswith("aq"), uid)

        # ═══════════════════════════════════════════════════════════════════
        print("\n[3] PHIEN DO VAO DUOC `/me` (day la ca ly do route ton tai)")
        code, prof, _ = http(api + "/me/profile", token=tok)
        chk("`GET /me/profile` cho vao", code == 200, "ma " + str(code))
        if code == 200 and isinstance(prof, dict):
            pf = prof.get("profile") or {}
            chk("ho so mang dung email", pf.get("email") == email, pf.get("email"))
            chk("`/me/profile` noi ro CHUA xac minh", pf.get("emailVerified") is False,
                str(pf.get("emailVerified")))
            chk("`/me/profile` noi muc qua DANG CHO", pf.get("starterBonus") == 100,
                str(pf.get("starterBonus")))
        # Day moi la duong that ma `flush()` di: hang cho gui viec qua nhom /me.
        code, _, _ = http(api + "/me/missions", token=tok)
        chk("`GET /me/missions` cho vao (duong cua `flush()`)", code == 200, "ma " + str(code))

        # ═══════════════════════════════════════════════════════════════════
        print("\n[4] HO SO TRONG DYNAMODB")
        it = item("USER#" + uid, "PROFILE")
        chk("co ho so USER#/PROFILE", it is not None)
        if it:
            chk("mang co emailVerified=false", it.get("emailVerified") == {"BOOL": False},
                str(it.get("emailVerified")))
            chk("giu nhan chien dich da gui", (it.get("src") or {}).get("S") == "zzclaim/probe",
                str((it.get("src") or {}).get("S")))
        chk("co ban ghi cho PENDING#/SIGNUP (link trong thu)",
            item("PENDING#" + email, "SIGNUP") is not None)

        # ═══════════════════════════════════════════════════════════════════
        print("\n[5] CONG MUON VAN PHAI DONG (chua xac minh thi chua gui thu duoc)")
        code, rep, _ = http(api + "/me/report/email", {}, token=tok)
        chk("`/me/report/email` bi tu choi 403", code == 403, "ma " + str(code))
        if isinstance(rep, dict):
            chk("va noi dung ly do `email-unverified`", rep.get("code") == "email-unverified", rep)
        # ⚠ Phai goi mot route CO THAT duoi /me/billing. `/me/billing` tran
        #    khong duoc khai (chi /checkout, /order/{id}, /orders) nen no tra 404 vi
        #    KHONG TIM THAY -- mot phep kiem do no thi khong noi gi ve cai cong ca.
        code, bil, _ = http(api + "/me/billing/orders", token=tok)
        chk("`/me/billing/orders` khong cho vao", code == 403, "ma " + str(code))

        # ═══════════════════════════════════════════════════════════════════
        print("\n[6] QUA KHOI DAU CHUA DUOC CAP (chi cap sau khi bam link)")
        # ⚠⚠ DAU QUA THEO EMAIL, KHONG THEO uid (`DynamoContext.BonusPk`) -- no
        #    song lau hon ca tai khoan de chan "xoa roi dang ky lai lay them qua".
        #    Tra nham `USER#<uid>` thi phep kiem nay DAT MOT CACH RONG: no doc mot
        #    khoa khong bao gio ton tai roi ket luan "chua cap".
        chk("chua co dau BONUS#<email>/STARTER", item("BONUS#" + email, "STARTER") is None)
        w = item("USER#" + uid, "WALLET")
        bal = int(((w or {}).get("meteors") or {}).get("N", "0"))
        chk("vi van dang la 0 tt", bal == 0, str(bal) + " tt")

        # ═══════════════════════════════════════════════════════════════════
        print("\n[7] CLAIM LAI CUNG EMAIL -> KHONG TAO TAI KHOAN THU HAI")
        code, again, _ = http(api + "/auth/claim", {"email": email, "name": "Ke Chen"})
        chk("bi tu choi 409", code == 409, "ma " + str(code))
        if isinstance(again, dict):
            chk("ma loi `email-already-in-use`", again.get("code") == "email-already-in-use", again)

        # ═══════════════════════════════════════════════════════════════════
        print("\n[8] MAT KHAU NGAU NHIEN KHONG BAO GIO VE TAY CLIENT")
        flat = json.dumps(body).lower()
        chk("than tra ve khong co truong mat khau nao",
            ("password" not in flat) and ("matkhau" not in flat))
        # Doan mat khau la vo vong theo thiet ke -- do bang mot lan thu that.
        code, bad, _ = http(FB_BASE + "signInWithPassword?key=" + FB_KEY,
                            {"email": email, "password": "Probe!" + stamp, "returnSecureToken": True})
        chk("khong dang nhap duoc bang mat khau doan", code != 200, "ma " + str(code))

        # ═══════════════════════════════════════════════════════════════════
        print("\n[9] EMAIL SAI DINH DANG -> TU CHOI TRUOC KHI DUNG DEN FIREBASE")
        code, bad2, _ = http(api + "/auth/claim", {"email": "khong-phai-email"})
        chk("tra 400", code == 400, "ma " + str(code))
        if isinstance(bad2, dict):
            chk("ma loi `invalid-email`", bad2.get("code") == "invalid-email", bad2)

        # ═══════════════════════════════════════════════════════════════════
        print("\n[10] BAM LINK TRONG THU -> XAC MINH + CAP QUA (duong quay lai)")
        # ⚠️ Dat tokenHash bang tay thay cho viec doc thu -- dung cach cua
        #    `probe_activate_now.py`. Token that nam trong thu, bo do khong doc thu.
        tok_plain = "zzclaimtok" + stamp
        th = hashlib.sha256(tok_plain.encode("utf-8")).digest()
        aws(["dynamodb", "update-item", "--table-name", TABLE,
             "--key", json.dumps({"PK": {"S": "PENDING#" + email}, "SK": {"S": "SIGNUP"}}),
             "--update-expression", "SET tokenHash = :h",
             "--expression-attribute-values",
             json.dumps({":h": {"S": base64.b64encode(th).decode()}})], allow_fail=True)

        code, _, hdr = http(api + "/auth/activate?e=" + urllib.parse.quote(email)
                            + "&t=" + tok_plain, redirect=False)
        chk("tra 302 (chuyen huong ve landing)", code == 302, "ma " + str(code))
        loc = hdr.get("Location") or hdr.get("location") or ""
        chk("noi KICH HOAT THANH CONG, ly do `ok`", "activated=1" in loc and "reason=ok" in loc, loc[:120])

        it2 = item("USER#" + uid, "PROFILE")
        chk("ho so nay mang emailVerified=true", (it2 or {}).get("emailVerified") == {"BOOL": True},
            str((it2 or {}).get("emailVerified")))
        chk("da co dau BONUS#<email>/STARTER (qua cap DUNG luc bam link)",
            item("BONUS#" + email, "STARTER") is not None)
        w2 = item("USER#" + uid, "WALLET")
        bal2 = int(((w2 or {}).get("meteors") or {}).get("N", "0"))
        chk("vi = 100 tt", bal2 == 100, str(bal2) + " tt")

    finally:
        # ═══════════════════════════════════════════════════════════════════
        print("\n[11] DON DEP")
        if keep:
            print("      --keep: giu lai tai khoan thu " + email + " (uid " + uid + ")")
        else:
            # ⚠️ XOA FIREBASE BANG CHINH idToken CUA PHIEN VUA LAP -- cung cach
            #    `probe_register_now.py` dung. `tok` chi ton tai khi [2] da qua;
            #    hong som hon thi khong co gi de xoa, va noi ra thay vi im lang.
            if uid and tok:
                code, _, _ = http(FB_BASE + "delete?key=" + FB_KEY, {"idToken": tok})
                chk("da xoa tai khoan Firebase thu", code == 200, "ma " + str(code))
            else:
                print("      [..]   chua lap duoc phien -> khong co tai khoan Firebase de xoa")
            # ⚠ `BONUS#<email>` phai co trong danh sach nay: no KHONG CO TTL, nen
            #    xoa nham khoa la moi luot chay de lai mot dong VINH VIEN trong bang.
            for pk, sk in (("USER#" + uid, "PROFILE"), ("USER#" + uid, "WALLET"),
                           ("USER#" + uid, "PROGRESS"),
                           ("BONUS#" + email, "STARTER"),
                           ("EMAIL#" + email, "ACCOUNT"), ("PENDING#" + email, "SIGNUP")):
                if uid or not pk.startswith("USER#"):
                    drop(pk, sk)
            if uid:
                chk("da xoa ho so trong DynamoDB", item("USER#" + uid, "PROFILE") is None)
            chk("da xoa dau qua khoi dau", item("BONUS#" + email, "STARTER") is None)
            chk("da nha cho giu email", item("EMAIL#" + email, "ACCOUNT") is None)

        print("\n===== %d OK - %d HONG =====" % (_n["ok"], _n["ng"]))
        sys.exit(1 if _n["ng"] else 0)


if __name__ == "__main__":
    main()
