# -*- coding: utf-8 -*-
"""probe_register_now.py -- DANG KY XONG LA CHOI DUOC NGAY CHUA, DO BANG SO.

    python scratchpad/probe_register_now.py                # chay tren API prod
    python scratchpad/probe_register_now.py --api local
    python scratchpad/probe_register_now.py --keep         # khong don tai khoan thu

VIEC 2 CUA BAN PHAN TICH 04/09/2026
-----------------------------------
Doc CloudWatch 14 ngay ra 3 luot dang ky bang email that cua nguoi ngoai, va
**2 trong 3 khong bao gio bam link kich hoat**. Luong cu chi dung tai khoan DUNG
LUC bam link, nen hai nguoi do roi di voi con so 0: khong tai khoan, khong tien
do, khong dau vet nao de moi quay lai. Viec 2 doi luat: tai khoan ra doi ngay luc
dang ky, xac minh de sau.

Bo do nay hoi dung nhung cau ma doi luat do phai tra loi duoc:
  [1] `/auth/register` co tao ra tai khoan DANG NHAP DUOC ngay khong.
  [2] Token cua tai khoan CHUA xac minh co vao duoc `/me` khong (phai VAO DUOC).
  [3] Ho so co that su mang co `emailVerified=false` khong.
  [4] Cong muon con dung khong: `/me/report/email` va `/me/billing` phai TU CHOI.
  [5] Qua khoi dau **chua** duoc cap (chi cap sau khi bam link).
  [6] Dang ky lai cung email -> `email-already-in-use`, khong tao tai khoan thu hai.
  [7] Tai khoan tu `signUp` bang apiKey CONG KHAI -> KHONG vao duoc `/me`.

⚠️ [7] LA PHEP KIEM QUAN TRONG NHAT VA DE BO SOT NHAT. No la ly do cong `/me` doi
   sang "co ho so do server tao" thay vi bo han. Thieu no thi bo do nay bao xanh
   trong khi `/me` da mo toang cho bat ky ai co apiKey -- ma apiKey thi nam san
   trong ma client.
⚠️ BO DO TU DON: tai khoan thu bi xoa o cuoi (Firebase + DynamoDB + cho giu email).
   Bai hoc 16/08/2026 -- `e2e_certificate` tung de lai tai khoan that trong DB.
⚠️ `aws` CLI cung la Python: khong dat PYTHONIOENCODING thi CHINH NO chet o chu
   Viet va tra ve JSON CUT GIUA CHUNG. Bai hoc da ghi o `scratchpad/read_logs.py`.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROD_API  = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
LOCAL_API = "http://localhost:5080"
# apiKey Web cua Firebase la CONG KHAI theo thiet ke (xem js/firebase-config.js).
# Chinh viec no cong khai la dieu phep kiem [8] duoi day do.
FB_KEY    = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
FB_BASE   = "https://identitytoolkit.googleapis.com/v1/accounts:"
TABLE     = "astroq-main"

_n = {"ok": 0, "ng": 0}
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


def http(url, body=None, token=None):
    """Goi HTTP, tra ve (ma trang thai, than da phan tich JSON hoac chuoi tho)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw, code = r.read().decode("utf-8", "replace"), r.status
    except urllib.error.HTTPError as e:
        raw, code = e.read().decode("utf-8", "replace"), e.code
    except Exception as e:
        return 0, str(e)
    try:
        return code, json.loads(raw)
    except Exception:
        return code, raw


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
    # ⚠️⚠️ DUNG MAILBOX SIMULATOR CUA SES, KHONG DUNG `@example.com` (sua 04/09/2026).
    #    Ban dau bo do nay dung `example.com` (RFC 2606, khong ai so huu) va GHI NHAN
    #    rang SES se tra `bounce`, coi do la gia phai tra. Do la mot gia KHONG can tra:
    #    `/auth/register` GOI SES THAT o ca ban local (doc duoc trong log: "Da gui email
    #    kich hoat toi probe-...@example.com"), nen moi luot chay bo do la mot bounce
    #    that cong vao ti le bounce cua CA tai khoan AWS -- ma ti le do cao thi AWS khoa
    #    quyen gui, tuc lam chet dung duong thu kich hoat ma bo do nay dang canh.
    #    `@simulator.amazonses.com` la hop thu gia CUA CHINH AWS: `success+<nhan>` duoc
    #    nhan thanh cong, KHONG tinh vao bounce, va nhan sau dau `+` bi bo qua nen moi
    #    luot chay van co mot dia chi RIENG (dieu `/auth/register` doi).
    #    ⚠️ VAN KHONG doc duoc thu -- do la co y: bo do nay khong can noi dung thu, va
    #       mot dia chi doc duoc nghia la co nguoi that nhan spam moi luot chay.
    email = "success+astroq-reg-" + stamp + "@simulator.amazonses.com"
    pwd   = "Probe!" + stamp
    print("\n[0] TAI KHOAN THU: " + email)
    print("      API: " + api)

    print("\n[1] DANG KY -> CO TAI KHOAN NGAY CHUA")
    code, body = http(api + "/auth/register",
                      {"name": "Probe", "email": email, "password": pwd, "src": "probe/local"})
    chk("`/auth/register` tra 202", code == 202, "ma " + str(code))
    if not isinstance(body, dict):
        print("      than tra ve khong phai JSON -> dung: " + str(body)[:200])
        sys.exit(1)
    chk("noi ro DA CO tai khoan (`account`)", body.get("account") is True, body.get("account"))
    chk("khong con bao `pending`", body.get("pending") is False, body.get("pending"))
    chk("noi ro CHUA xac minh", body.get("emailVerified") is False)
    print("      loi nhan: " + str(body.get("message"))[:120])

    print("\n[2] DANG NHAP NGAY BANG MAT KHAU VUA GO")
    code, sess = http(FB_BASE + "signInWithPassword?key=" + FB_KEY,
                      {"email": email, "password": pwd, "returnSecureToken": True})
    ok_login = code == 200 and isinstance(sess, dict) and sess.get("idToken")
    chk("Firebase cho dang nhap ngay", bool(ok_login), "" if ok_login else str(sess)[:200])
    if not ok_login:
        print("\n===== %d OK - %d HONG =====" % (_n["ok"], _n["ng"]))
        sys.exit(1)
    tok, uid = sess["idToken"], sess["localId"]
    chk("Firebase xac nhan email CHUA verify",
        str(sess.get("emailVerified", False)).lower() == "false")

    print("\n[3] TOKEN CHUA XAC MINH CO VAO DUOC `/me` KHONG (PHAI VAO DUOC)")
    code, prof = http(api + "/me/profile", token=tok)
    chk("`GET /me/profile` cho vao", code == 200, "ma " + str(code))
    if code == 200 and isinstance(prof, dict):
        pf = prof.get("profile") or {}
        chk("ho so mang dung email", pf.get("email") == email)
        # ⚠️ HAI TRUONG NAY NUOI DAI MOI BAM LINK O DASHBOARD. Qua chi cap sau khi bam
        #    link nen vi la 0 tt: khong co hai truong nay thi tre gap "khong du Thien
        #    thach tim" o Khu Huan Luyen ma khong co cho nao noi tien nam o dau.
        chk("`/me/profile` noi ro CHUA xac minh", pf.get("emailVerified") is False,
            str(pf.get("emailVerified")))
        # ⚠️ MUC QUA DO SERVER QUYET: 500 tt cho nguoi da ghi danh WAITLIST#, 100 tt cho
        #    nguoi con lai (Wallet.StarterBonusFor). Email thu nghiem khong ghi danh nen
        #    phai la 100 — do "> 0" thi bo do van xanh khi server tra 0 va dai bien mat.
        chk("`/me/profile` noi muc qua dang cho", pf.get("starterBonus") == 100,
            str(pf.get("starterBonus")))
    code, _ = http(api + "/me/missions", token=tok)
    chk("`GET /me/missions` cho vao", code == 200, "ma " + str(code))

    print("\n[4] HO SO TRONG DYNAMODB")
    it = item("USER#" + uid, "PROFILE")
    chk("co ho so USER#/PROFILE", it is not None)
    if it:
        chk("mang co emailVerified=false",
            it.get("emailVerified", {}).get("BOOL") is False, it.get("emailVerified"))
        chk("giu nhan chien dich da gui",
            (it.get("src") or {}).get("S") == "probe/local", (it.get("src") or {}).get("S"))
    pend = item("PENDING#" + email, "SIGNUP")
    chk("ban ghi cho mang uid cua tai khoan",
        bool(pend) and (pend.get("uid") or {}).get("S") == uid)

    print("\n[5] CONG MUON VAN PHAI DONG")
    code, r1 = http(api + "/me/report/email", {}, token=tok)
    chk("`/me/report/email` bi tu choi 403", code == 403, "ma " + str(code))
    chk("va noi dung ly do `email-unverified`",
        isinstance(r1, dict) and r1.get("code") == "email-unverified", str(r1)[:120])
    # ⚠️ DOI CA `code`, KHONG CHI DOI 403. Truoc 04/09/2026 nhom nay gac bang policy doc
    #    claim, va 403 cua policy la 403 RONG — client khong co gi de noi cho dung, nen
    #    trang thanh toan chi biet bao mot cau loi chung chung. Nay la bo loc doc
    #    DynamoDB nen no tra kem `email-unverified`; do them dong nay de khong ai lui
    #    ve policy cu ma bo do van xanh.
    code, r2 = http(api + "/me/billing/orders", token=tok)
    chk("`/me/billing/*` khong cho vao", code == 403, "ma " + str(code))
    chk("va noi dung ly do `email-unverified`",
        isinstance(r2, dict) and r2.get("code") == "email-unverified", str(r2)[:120])

    print("\n[6] QUA KHOI DAU CHUA DUOC CAP")
    chk("chua co dau BONUS# (qua chi cap sau khi bam link)",
        item("BONUS#" + email, "STARTER") is None)
    w = item("USER#" + uid, "WALLET")
    bal = int(((w or {}).get("meteors") or {}).get("N", "0"))
    chk("vi van dang la 0 tt", bal == 0, str(bal) + " tt")

    print("\n[7] DANG KY LAI CUNG EMAIL")
    code, dup = http(api + "/auth/register",
                     {"name": "Probe 2", "email": email, "password": pwd + "x"})
    chk("bi tu choi 409", code == 409, "ma " + str(code))
    chk("ma loi `email-already-in-use`",
        isinstance(dup, dict) and dup.get("code") == "email-already-in-use", str(dup)[:120])

    print("\n[8] KHE HO apiKey CONG KHAI -- TU signUp THI KHONG DUOC VAO `/me`")
    # ⚠️ Dia chi nay KHONG di qua SES (tu `signUp` truc tiep vao Firebase, khong co thu
    #    nao duoc gui), nen `example.com` o day vo hai -- khac han dia chi dang ky tren.
    intruder = "probe-intruder-" + stamp + "@example.com"
    code, isess = http(FB_BASE + "signUp?key=" + FB_KEY,
                       {"email": intruder, "password": pwd, "returnSecureToken": True})
    if code == 200 and isinstance(isess, dict) and isess.get("idToken"):
        icode, ibody = http(api + "/me/profile", token=isess["idToken"])
        chk("tai khoan tu signUp bi chan khoi `/me`", icode == 403, "ma " + str(icode))
        chk("va noi dung ly do `no-profile`",
            isinstance(ibody, dict) and ibody.get("code") == "no-profile", str(ibody)[:120])
        http(FB_BASE + "delete?key=" + FB_KEY, {"idToken": isess["idToken"]})
    else:
        print("  [..]   khong tu signUp duoc (co the da tat) -> bo qua phep kiem nay")

    if keep:
        print("\n[9] --keep: giu lai " + email + " (uid " + uid + ")")
    else:
        print("\n[9] DON DEP")
        code, _ = http(FB_BASE + "delete?key=" + FB_KEY, {"idToken": tok})
        chk("da xoa tai khoan Firebase thu", code == 200, "ma " + str(code))
        for pk, sk in (("USER#" + uid, "PROFILE"), ("USER#" + uid, "WALLET"),
                       ("EMAIL#" + email, "ACCOUNT"), ("PENDING#" + email, "SIGNUP")):
            drop(pk, sk)
        chk("da xoa ho so trong DynamoDB", item("USER#" + uid, "PROFILE") is None)
        chk("da nha cho giu email", item("EMAIL#" + email, "ACCOUNT") is None)

    print("\n===== %d OK - %d HONG =====" % (_n["ok"], _n["ng"]))
    sys.exit(1 if _n["ng"] else 0)


if __name__ == "__main__":
    main()
