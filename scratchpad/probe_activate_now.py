# -*- coding: utf-8 -*-
"""probe_activate_now.py -- BAM LINK KICH HOAT O LUONG MOI, DO BANG SO.

    python scratchpad/probe_activate_now.py --api local
    python scratchpad/probe_activate_now.py                # API prod
    python scratchpad/probe_activate_now.py --keep         # khong don tai khoan thu

BO DO NAY LA NUA CON LAI CUA `probe_register_now.py`
----------------------------------------------------
Bo do kia dung o cho "dang ky xong choi duoc ngay, va cong muon van dong". Con
lai mot nhanh CHUA AI DO, va no la nhanh KHO NHAT cua ca viec 2: nhanh
"tai khoan DA CO SAN" trong `/auth/activate` (them 04/09/2026). Truoc hom do
`/auth/activate` chi co mot viec -- TAO tai khoan; nay tai khoan da ra doi tu luc
dang ky, nen no chuyen sang hai viec khac: bat co da xac minh, va tra mon qua.

⚠️⚠️ CAI BAY MA BO DO NAY CANH. Nhanh moi KHONG duoc goi `ClaimEmailAsync`: cho
   email da giu tu luc dang ky, nen loi goi do chac chan tra FALSE va luong re vao
   nhanh "already" -- tuc MOI luot kich hoat hop le bi hieu nham thanh bam link
   lan hai, va **khong ai nhan duoc qua**. Trieu chung duy nhat la mot dong log
   "da co nguoi giu cho" giua hang nghin dong, con nguoi dung thi thay
   `activated=1` va tuong da xong. Doc luot doan `/auth/activate` roi chep lai
   la vap dung vao day.

⚠️⚠️ VA MOT LOI TRA LOI SAI DA SUA TRONG CUNG NGAY: cong muon phai mo NGAY sau khi
   bam link, khong doi token moi. Ban dau `/me/billing` gac bang policy doc claim
   `email_verified` -- ma claim nam trong ID token DA PHAT nen no con noi "chua"
   toi ca gio nua. Phep kiem [6] dung DUNG CAI TOKEN CU (phat truoc khi kich hoat)
   de do dieu do; lay token moi thi phep kiem nay "dat" ma khong kiem gi ca.

CACH LAY TOKEN KICH HOAT -- DOC TRUOC KHI SUA
---------------------------------------------
Token that chi nam trong LA THU, va ban ghi cho chi luu `tokenHash`, nen bo do
khong doc lai duoc. Nen no lam dung mot viec: GHI DE `tokenHash` bang bam cua mot
token do chinh no chon (`sha256(token)` roi base64 -- cung khuon
`PasswordHasher.HashToken`). Moi thu khac di qua duong THAT: dung endpoint that,
dung ban ghi that, dung thu tu that.
⚠️ Doi lai, phep kiem nay KHONG chung minh duoc "token trong thu la token dung".
   Do la viec cua `probe_register_now.py` (no do duoc rang thu DA gui) va cua bo
   `e2e` chay tren ban that.

⚠️ BO DO TU DON: tai khoan thu bi xoa o cuoi (Firebase + DynamoDB + cho giu email
   + dau qua). Bai hoc 16/08/2026 -- `e2e_certificate` tung de lai tai khoan that.
⚠️ DIA CHI DUNG MAILBOX SIMULATOR CUA SES, khong dung `@example.com`: `/register`
   goi SES THAT nen moi luot chay bang mot bounce that cong vao ti le bounce cua
   ca tai khoan AWS. Ly do day du ghi o `probe_register_now.py`.
"""
import base64
import hashlib
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
FB_KEY    = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
FB_BASE   = "https://identitytoolkit.googleapis.com/v1/accounts:"
TABLE     = "astroq-main"
# Muc qua cho tai khoan KHONG ghi danh danh sach cho -- `Wallet.StarterBonus`.
# ⚠️ Go cung o day la CO Y: bo do phai biet truoc con so de bat duoc ca ca "cap
#    sai muc", chu khong phai doc lai chinh cai no dang do.
BONUS_PLAIN = 100

_n = {"ok": 0, "ng": 0}
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


def http(url, body=None, token=None, follow=True):
    """Goi HTTP -> (ma trang thai, than JSON/tho, dich chuyen huong hoac None).

    ⚠️ `follow=False` la BAT BUOC cho `/auth/activate`: no ket thuc bang 302 ve
       trang landing, va thu can do nam trong `Location` (`activated=1&reason=ok`).
       De urllib tu di theo thi doc duoc mot trang HTML, con ly do thi mat.
    """
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)

    opener = urllib.request.build_opener()
    if not follow:
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=30) as r:
            raw, code, loc = r.read().decode("utf-8", "replace"), r.status, r.headers.get("Location")
    except urllib.error.HTTPError as e:
        raw, code, loc = e.read().decode("utf-8", "replace"), e.code, e.headers.get("Location")
    except Exception as e:
        return 0, str(e), None
    try:
        return code, json.loads(raw), loc
    except Exception:
        return code, raw, loc


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


def put(it):
    """Ghi mot item. -> True khi `aws` tra ve ma 0.

    ⚠️ KHONG dung `aws()` o day: `put-item` THANH CONG thi in ra RONG, ma `aws()`
       coi stdout rong la that bai (dung cho `get-item`, sai cho `put-item`). Ban
       dau bo do nay bao "[!!] ghi de tokenHash" trong khi lenh chay tot va ca
       phan sau deu xanh -- mot phep kiem noi doi theo huong bao dong gia.
    """
    p = subprocess.run(["aws", "dynamodb", "put-item", "--table-name", TABLE,
                        "--item", json.dumps(it), "--no-cli-pager"],
                       capture_output=True, text=False, shell=True, env=ENV)
    if p.returncode != 0:
        print("         " + p.stderr.decode("utf-8", "replace").strip()[:300])
    return p.returncode == 0


def drop(pk, sk):
    aws(["dynamodb", "delete-item", "--table-name", TABLE,
         "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}})], allow_fail=True)


def jwt_claim(tok, name):
    """Doc mot claim trong phan than cua ID token (KHONG kiem chu ky).

    ⚠️ KHONG kiem chu ky la CO Y va an toan o day: bo do tu vua lay token nay tu
       Google xong, va thu can biet la "server se doc thay gi", chu khong phai
       "token nay co that khong".
    """
    try:
        body = tok.split(".")[1]
        body += "=" * (-len(body) % 4)
        return json.loads(base64.urlsafe_b64decode(body).decode("utf-8")).get(name)
    except Exception:
        return None


def hash_token(tok):
    """Cung khuon `PasswordHasher.HashToken`: base64(sha256(utf8(token)))."""
    return base64.b64encode(hashlib.sha256(tok.encode("utf-8")).digest()).decode("ascii")


def main():
    api = PROD_API
    if "--api" in sys.argv:
        v = sys.argv[sys.argv.index("--api") + 1]
        api = LOCAL_API if v == "local" else (PROD_API if v == "prod" else v)
    keep = "--keep" in sys.argv

    stamp = str(int(time.time()))
    email = "success+astroq-act-" + stamp + "@simulator.amazonses.com"
    pwd   = "Probe!" + stamp
    print("\n[0] TAI KHOAN THU: " + email)
    print("      API: " + api)

    # ── [1] Dang ky binh thuong ─────────────────────────────────────────────
    print("\n[1] DANG KY (duong that)")
    code, reg, _ = http(api + "/auth/register",
                        {"name": "Probe Act", "email": email, "password": pwd,
                         "src": "probe/activate"})
    chk("`/auth/register` tra 202", code == 202, "ma " + str(code))
    chk("noi ro DA CO tai khoan", isinstance(reg, dict) and reg.get("account") is True,
        str(reg)[:100])
    if not (isinstance(reg, dict) and reg.get("account") is True):
        print("\n[!!] khong tao duoc tai khoan -> dung")
        sys.exit(1)

    # ── [2] Dang nhap de lay TOKEN CU (phat TRUOC khi kich hoat) ────────────
    print("\n[2] TOKEN CU -- PHAT TRUOC KHI KICH HOAT")
    code, sess, _ = http(FB_BASE + "signInWithPassword?key=" + FB_KEY,
                         {"email": email, "password": pwd, "returnSecureToken": True})
    chk("dang nhap duoc ngay", code == 200 and isinstance(sess, dict) and sess.get("idToken"),
        "ma " + str(code))
    if not (code == 200 and isinstance(sess, dict) and sess.get("idToken")):
        sys.exit(1)
    tok_old, uid = sess["idToken"], sess["localId"]
    # ⚠️ CAI TOKEN NAY LA CA PHEP KIEM [6]. Giu nguyen, dung lay lai token moi.
    # ⚠️ DOC CLAIM TRONG CHINH ID TOKEN, khong doc `sess["emailVerified"]`: Firebase
    #    BO HAN truong do khoi than tra loi khi no la false, nen `in (False, None)` se
    #    "dat" ca khi tai khoan DA xac minh -- tuc phep kiem [6] mat het y nghia ma
    #    khong ai thay. Claim trong token la thu ma server that su doc.
    chk("token cu mang email_verified=false", jwt_claim(tok_old, "email_verified") is not True,
        str(jwt_claim(tok_old, "email_verified")))
    code, r, _ = http(api + "/me/billing/orders", token=tok_old)
    chk("truoc kich hoat: `/me/billing` DONG", code == 403, "ma " + str(code))

    # ── [3] Ghi de tokenHash bang token minh chon ──────────────────────────
    print("\n[3] DAT TOKEN KICH HOAT (thay cho viec doc thu)")
    pend = item("PENDING#" + email, "SIGNUP")
    chk("co ban ghi cho PENDING#/SIGNUP", pend is not None)
    if pend is None:
        sys.exit(1)
    chk("ban ghi cho mang uid cua tai khoan",
        (pend.get("uid") or {}).get("S") == uid, (pend.get("uid") or {}).get("S"))
    act_tok = "probe" + stamp + "f" * 20
    pend["tokenHash"] = {"S": hash_token(act_tok)}
    chk("ghi de tokenHash thanh cong", put(pend))

    # ── [4] Bam link ───────────────────────────────────────────────────────
    print("\n[4] BAM LINK KICH HOAT")
    url = (api + "/auth/activate?e=" + urllib.parse.quote(email, safe="")
           + "&t=" + act_tok)
    code, _, loc = http(url, follow=False)
    chk("tra 302 (chuyen huong ve landing)", code in (301, 302, 303, 307), "ma " + str(code))
    chk("noi KICH HOAT THANH CONG", bool(loc) and "activated=1" in loc, str(loc)[:140])
    # ⚠️ PHAI LA `reason=ok`, KHONG PHAI `already`. `already` o day chinh la cai bay
    #    ClaimEmailAsync ghi o dau file: nguoi dung van thay "kich hoat 1" nhung
    #    KHONG duoc cap qua. Do thieu dong nay la bo do xanh trong khi qua bien mat.
    chk("ly do la `ok`, KHONG phai `already`", bool(loc) and "reason=ok" in loc,
        str(loc)[:140])

    # ── [5] DynamoDB: co da bat, qua da cap, ban ghi cho da xoa ────────────
    print("\n[5] DYNAMODB SAU KHI KICH HOAT")
    prof = item("USER#" + uid, "PROFILE")
    chk("ho so mang emailVerified=true",
        bool(prof) and (prof.get("emailVerified") or {}).get("BOOL") is True,
        str((prof or {}).get("emailVerified")))
    chk("da co dau BONUS#/STARTER (qua da cap)", item("BONUS#" + email, "STARTER") is not None)
    w = item("USER#" + uid, "WALLET")
    bal = int(((w or {}).get("meteors") or {}).get("N", "0"))
    chk("vi = %d tt (muc cua nguoi khong ghi danh)" % BONUS_PLAIN, bal == BONUS_PLAIN,
        str(bal) + " tt")
    chk("ban ghi cho da bi xoa", item("PENDING#" + email, "SIGNUP") is None)

    # ── [6] CONG MUON MO NGAY, VOI CHINH TOKEN CU ──────────────────────────
    print("\n[6] CONG MUON MO NGAY -- DUNG TOKEN CU, KHONG LAY TOKEN MOI")
    # ⚠️ DAY LA PHEP KIEM QUAN TRONG NHAT CUA CA BO DO. Token nay mang
    #    `email_verified=false` va con mang no toi ca gio nua. Cong doc DynamoDB thi
    #    mo ngay; cong doc claim thi con dong -- tuc "kich hoat xong, mua goi ngay,
    #    an 403 suot gan mot tieng".
    code, prof2, _ = http(api + "/me/profile", token=tok_old)
    chk("`/me/profile` cho vao", code == 200, "ma " + str(code))
    pf = (prof2 or {}).get("profile") or {} if isinstance(prof2, dict) else {}
    chk("`/me/profile` noi DA xac minh", pf.get("emailVerified") is True,
        str(pf.get("emailVerified")))
    # ⚠️ VE 0 la dieu dai moi bam link o dashboard doc de TU AN. Con so khac 0 o day
    #    nghia la dai do o lai vinh vien voi mot viec da lam xong.
    chk("`/me/profile` bao khong con qua dang cho", pf.get("starterBonus") == 0,
        str(pf.get("starterBonus")))
    code, r6, _ = http(api + "/me/billing/orders", token=tok_old)
    chk("`/me/billing` DA MO voi token cu", code == 200, "ma " + str(code) + " " + str(r6)[:80])
    # ⚠️ `/me/report/email` KHONG con tra `email-unverified`. Tuan nay rong nen no tra
    #    200 kem `sent:false, reason:"empty"` -- do la cau tra loi THAT, khong phai loi.
    code, r7, _ = http(api + "/me/report/email", {}, token=tok_old)
    chk("`/me/report/email` khong con bi cong muon chan", code == 200, "ma " + str(code))
    chk("va khong con ma `email-unverified`",
        not (isinstance(r7, dict) and r7.get("code") == "email-unverified"), str(r7)[:120])

    # ── [7] Bam link lan hai ───────────────────────────────────────────────
    print("\n[7] BAM LINK LAN HAI (ban ghi cho da mat)")
    code, _, loc2 = http(url, follow=False)
    chk("van tra 302", code in (301, 302, 303, 307), "ma " + str(code))
    # ⚠️ LAN NAY `already` MOI LA DUNG: ban ghi cho da xoa o luot dau nen luong bat o
    #    nhanh `p is null`. Noi "khong tim thay dang ky" thi nguoi ta se di dang ky lai
    #    va an `email-already-in-use` -- mot ngo cut.
    chk("noi `already`, khong noi `notfound`",
        bool(loc2) and "activated=1" in loc2 and "reason=already" in loc2, str(loc2)[:140])
    # ⚠️ VA KHONG DUOC CAP QUA LAN HAI. `ClaimStarterBonusAsync` ghi co dieu kien nen
    #    mot email nhan dung mot lan, vinh vien -- do lai o day de khong ai bo no.
    w2 = item("USER#" + uid, "WALLET")
    bal2 = int(((w2 or {}).get("meteors") or {}).get("N", "0"))
    chk("vi KHONG bi cong lan hai", bal2 == BONUS_PLAIN, str(bal2) + " tt")

    # ── [8] Don dep ────────────────────────────────────────────────────────
    if keep:
        print("\n[8] --keep: giu lai " + email + " (uid " + uid + ")")
    else:
        print("\n[8] DON DEP")
        code, _, _ = http(FB_BASE + "delete?key=" + FB_KEY, {"idToken": tok_old})
        chk("da xoa tai khoan Firebase thu", code == 200, "ma " + str(code))
        for pk, sk in (("USER#" + uid, "PROFILE"), ("USER#" + uid, "WALLET"),
                       ("USER#" + uid, "PROGRESS"),
                       ("EMAIL#" + email, "ACCOUNT"), ("PENDING#" + email, "SIGNUP"),
                       ("BONUS#" + email, "STARTER")):
            drop(pk, sk)
        chk("da xoa ho so trong DynamoDB", item("USER#" + uid, "PROFILE") is None)
        chk("da nha cho giu email", item("EMAIL#" + email, "ACCOUNT") is None)
        chk("da xoa dau qua khoi dau", item("BONUS#" + email, "STARTER") is None)

    print("\n===== %d OK - %d HONG =====" % (_n["ok"], _n["ng"]))
    sys.exit(1 if _n["ng"] else 0)


if __name__ == "__main__":
    import urllib.parse  # dat o day cho gan cho dung, khoi ai tuong no la thu vien chinh
    main()
