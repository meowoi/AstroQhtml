# -*- coding: utf-8 -*-
"""test_quizlv.py — `progress.quizLv` TREN BAN THAT: server co tinh dung cap do khong.

    python scratchpad/test_quizlv.py                     # http://localhost:5080
    python scratchpad/test_quizlv.py <base-url>          # ban that tren AWS

Tu tao tai khoan Firebase tam de co ID token that, tu nop cac luot quiz THAT qua
`POST /me/progress`, roi doc `quizLv` server tra ve. Don sach moi ban ghi DynamoDB
cua minh trong `finally`.

⚠️ VI SAO KHONG DO BANG `Adapt.QuizLevel` O MAY: bo `lvtest` da lam viec do (22/0).
   Dieu bo NAY do la khac han va khong suy ra duoc tu bo kia: **cai chay tren AWS co
   phai ban vua deploy khong**, va `quizLv` co di duoc tu bang PROGRESS ra tan JSON
   ma client doc khong. Mot ham dung o may nhung khong duoc goi trong `Snapshot()`
   thi bo kia van 22/0.

⚠️ MOC TRONG BO NAY LA BAN SAO DE DOI CHIEU, KHONG PHAI NGUON SU THAT. Nguon su that
   la `Services/Adapt.cs`. Doi moc o do thi bo nay bao hong — do la Y MUON: no bat
   nguoi doi phai doi ca hai va nghi mot lan nua.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

import _fbtest

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"

# Ban sao cua Services/Adapt.cs — xem canh bao o dau file.
WARMUP = 20
R2 = 0.60
R3 = 0.75

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def ddel(pk, sk):
    subprocess.run(
        ["aws", "dynamodb", "delete-item", "--table-name", TABLE,
         "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}})],
        capture_output=True)


def rows_of(pk):
    """Moi SK dang co duoi mot PK — de don SACH, khong don theo phong doan."""
    r = subprocess.run(
        ["aws", "dynamodb", "query", "--table-name", TABLE,
         "--key-condition-expression", "PK = :p",
         "--expression-attribute-values", json.dumps({":p": {"S": pk}}),
         "--projection-expression", "SK", "--output", "json"],
        capture_output=True, text=True)
    if r.returncode != 0:
        return []
    try:
        return [i["SK"]["S"] for i in json.loads(r.stdout).get("Items", [])]
    except Exception:
        return []


def expect_lv(answered, correct):
    """Ban sao luat — chi de DOI CHIEU."""
    if answered <= 0 or correct < 0 or correct > answered:
        return 1
    if answered < WARMUP:
        return 1
    ratio = correct / answered
    if ratio >= R3:
        return 3
    if ratio >= R2:
        return 2
    return 1


uid = None
# ⚠️ `.invalid` (dung nhu test_profile.py), KHONG dung dia chi gia lap SES: bo nay
#    KHONG goi `/auth/register` nen khong co thu nao duoc gui. Dia chi gia lap chi
#    can khi co duong gui thu that.
email = "quizlv-test-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
try:
    print("\n=== [0] Server nao dang chay ===")
    st, h = call("GET", "/health")
    check("/health 200", st == 200, json.dumps(h)[:80])

    uid, tok, _pw = _fbtest.make_verified(email)
    check("co ID token that (tai khoan tam da xac minh email)", bool(tok), uid)

    # ⚠️ PHAI TAO BAN GHI PROFILE TRUOC. Lan chay dau tren ban that tra **404**
    #    (`no-profile`), khong phai 401 — server co y KHONG tu tao ho so tu mot token
    #    hop le (chan tu-dang-ky). `test_profile.py` cung lam dung buoc nay.
    print("\n=== [1] Nguoi moi -> cap 1, va truong PHAI TON TAI ===")
    st, d = call("GET", "/me/profile", tok)
    check("chua co ho so -> 404 no-profile (server khong tu tao)",
          st == 404 and (d or {}).get("code") == "no-profile", "%s %s" % (st, d))
    made = subprocess.run(
        ["aws", "dynamodb", "put-item", "--table-name", TABLE, "--item",
         json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": {"S": "PROFILE"},
                     "uid": {"S": uid}, "email": {"S": email},
                     "name": {"S": "Test Pilot"},
                     "createdAt": {"S": "2026-08-19T00:00:00.000Z"}})],
        capture_output=True, text=True)
    check("tao ho so PROFILE bang aws CLI", made.returncode == 0,
          made.stderr.strip()[:90])
    st, d = call("GET", "/me/profile", tok)
    check("/me/profile 200", st == 200, str(st))
    pr = (d or {}).get("progress") or {}
    # ⚠️ PHEP KIEM QUAN TRONG NHAT CUA CA BO: `quizLv` co mat nghia la ban tren AWS
    #    DUNG la ban vua deploy. Thieu no thi moi phep kiem sau vo nghia.
    check("progress CO truong `quizLv` (=> ban that la ban vua deploy)",
          "quizLv" in pr, "cac truong: %s" % ",".join(sorted(pr.keys()))[:120])
    if "quizLv" not in pr:
        print("\n>>> DUNG HAN: ban tren AWS chua co `quizLv`.")
        sys.exit(1)
    check("nguoi chua lam gi -> cap 1", pr.get("quizLv") == 1, str(pr.get("quizLv")))
    check("quizAnswered = 0", pr.get("quizAnswered") == 0, str(pr.get("quizAnswered")))

    print("\n=== [2] Nop cac luot quiz THAT, doi chieu tung buoc ===")
    # Ba luot 5/5 = 15 cau dung het. VAN phai o cap 1 vi chua du WarmUp = 20 cau.
    for i in range(3):
        st, d = call("POST", "/me/progress", tok,
                     {"type": "quiz", "correct": 5, "total": 5, "meteors": 0,
                      "opId": str(uuid.uuid4())})
        if st != 200:
            check("nop luot %d thanh cong" % (i + 1), False, "%s %s" % (st, json.dumps(d)[:90]))
            break
    st, d = call("GET", "/me/profile", tok)
    pr = (d or {}).get("progress") or {}
    a, c, lv = pr.get("quizAnswered"), pr.get("quizCorrect"), pr.get("quizLv")
    print("      sau 3 luot 5/5: da tra loi %s, dung %s -> cap %s" % (a, c, lv))
    check("server dem dung 15 cau da tra loi", a == 15, str(a))
    check("15/15 dung het VAN o cap 1 (chua du WarmUp 20 cau)", lv == 1,
          "cap %s" % lv)
    check("khop ban sao luat", lv == expect_lv(a or 0, c or 0),
          "server %s vs ban sao %s" % (lv, expect_lv(a or 0, c or 0)))

    # Luot thu tu -> 20 cau, dung 20/20 = 100% -> phai len cap 3.
    st, d = call("POST", "/me/progress", tok,
                 {"type": "quiz", "correct": 5, "total": 5, "meteors": 0,
                  "opId": str(uuid.uuid4())})
    check("nop luot thu tu thanh cong", st == 200, str(st))
    st, d = call("GET", "/me/profile", tok)
    pr = (d or {}).get("progress") or {}
    a, c, lv = pr.get("quizAnswered"), pr.get("quizCorrect"), pr.get("quizLv")
    print("      sau 4 luot 5/5: da tra loi %s, dung %s -> cap %s" % (a, c, lv))
    check("du 20 cau (dung mep WarmUp)", a == 20, str(a))
    check("20/20 dung het -> len cap 3", lv == 3, "cap %s" % lv)
    check("khop ban sao luat", lv == expect_lv(a or 0, c or 0),
          "server %s vs ban sao %s" % (lv, expect_lv(a or 0, c or 0)))

    # Nop tiep 4 luot 0/5 -> 40 cau, dung 20 = 50% -> tut ve cap 1.
    for i in range(4):
        call("POST", "/me/progress", tok,
             {"type": "quiz", "correct": 0, "total": 5, "meteors": 0,
              "opId": str(uuid.uuid4())})
    st, d = call("GET", "/me/profile", tok)
    pr = (d or {}).get("progress") or {}
    a, c, lv = pr.get("quizAnswered"), pr.get("quizCorrect"), pr.get("quizLv")
    print("      sau 4 luot 0/5 nua: da tra loi %s, dung %s (%.0f%%) -> cap %s"
          % (a, c, 100.0 * (c or 0) / (a or 1), lv))
    check("50%% dung -> ve cap 1", lv == 1, "cap %s" % lv)
    check("khop ban sao luat", lv == expect_lv(a or 0, c or 0),
          "server %s vs ban sao %s" % (lv, expect_lv(a or 0, c or 0)))

    # Nop 2 luot 5/5 -> 50 cau, dung 30 = 60% -> dung MEP cap 2.
    for i in range(2):
        call("POST", "/me/progress", tok,
             {"type": "quiz", "correct": 5, "total": 5, "meteors": 0,
              "opId": str(uuid.uuid4())})
    st, d = call("GET", "/me/profile", tok)
    pr = (d or {}).get("progress") or {}
    a, c, lv = pr.get("quizAnswered"), pr.get("quizCorrect"), pr.get("quizLv")
    print("      sau 2 luot 5/5: da tra loi %s, dung %s (%.0f%%) -> cap %s"
          % (a, c, 100.0 * (c or 0) / (a or 1), lv))
    check("dung mep 60%% -> cap 2 (moc nay la Wallet.QuizPassRatio)", lv == 2,
          "%s/%s -> cap %s" % (c, a, lv))
    check("khop ban sao luat", lv == expect_lv(a or 0, c or 0),
          "server %s vs ban sao %s" % (lv, expect_lv(a or 0, c or 0)))

    print("\n=== [3] `quizLv` phai ra o CA HAI duong client doc ===")
    # js/progress.js goi absorbQuizLv o ca `getProfile` va `getAchievements`.
    st, d = call("GET", "/me/achievements", tok)
    pr2 = (d or {}).get("progress") or {}
    check("/me/achievements 200", st == 200, str(st))
    check("/me/achievements cung tra `quizLv`", "quizLv" in pr2,
          str(pr2.get("quizLv")))
    check("hai duong cho CUNG mot cap do", pr2.get("quizLv") == lv,
          "profile %s vs achievements %s" % (lv, pr2.get("quizLv")))

    print("\n=== [4] Client KHONG the tu khai cap do ===")
    # Gui `quizLv` len trong body: server phai bo qua hoan toan.
    before = lv
    st, d = call("POST", "/me/progress", tok,
                 {"type": "quiz", "correct": 5, "total": 5, "meteors": 0,
                  "quizLv": 3, "progress": {"quizLv": 3}, "opId": str(uuid.uuid4())})
    check("server nhan luot du body co `quizLv` la (bo qua, khong 500)",
          st == 200, str(st))
    st, d = call("GET", "/me/profile", tok)
    pr = (d or {}).get("progress") or {}
    a, c, lv2 = pr.get("quizAnswered"), pr.get("quizCorrect"), pr.get("quizLv")
    check("cap do KHONG bi client dat, van do server tinh",
          lv2 == expect_lv(a or 0, c or 0),
          "server %s (%s/%s) — ban sao %s" % (lv2, c, a, expect_lv(a or 0, c or 0)))
    check("cap do KHONG nhay len 3 theo loi khai cua client", lv2 != 3 or (c / a) >= R3,
          "cap %s voi %s/%s" % (lv2, c, a))

    print("\n=== [5] Cap do luon trong khoang [1,3] ===")
    check("cap do nam trong [1,3]", lv2 in (1, 2, 3), str(lv2))

finally:
    if uid:
        print("\n=== [6] Don du lieu test ===")
        # ⚠️ CHI CO MOT PK. Ban ghi tien do la `SK=PROGRESS` **duoi** `PK=USER#<uid>`
        #    (xem DynamoContext.ReadProgress) — khong ton tai PK `PROGRESS#<uid>`.
        #    Ban dau toi don ca hai, nen dong "da xoa 0 dong" doc ra nhu la khong con
        #    gi trong khi that ra tay do quet mot PK khong bao gio ton tai.
        pks = ["USER#%s" % uid]
        n = 0
        for pk in pks:
            for sk in rows_of(pk):
                ddel(pk, sk)
                n += 1
        left = sum(len(rows_of(pk)) for pk in pks)
        print("      da xoa %d dong, con lai %d" % (n, left))
        try:
            _fbtest.delete(tok)
            print("      da xoa tai khoan Firebase tam")
        except Exception as e:
            print("      ⚠️ chua xoa duoc tai khoan tam: %s" % e)
        if left:
            print("      ⚠️ CON SOT %d dong — kiem lai bang tay" % left)

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
