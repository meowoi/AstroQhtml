# -*- coding: utf-8 -*-
"""Kiem API PHI HANH DOAN DAU TIEN (`GET /crew` · `GET /me/crew`).

    py -3 scratchpad/test_crew.py                 # backend o may (localhost:5080)
    py -3 scratchpad/test_crew.py --prod          # ban that tren AWS

CHAY DOC LAP TRUOC KHI NOI VAO GIAO DIEN (quy tac 4 muc 6 cua CLAUDE.md).

⚠️⚠️ PHEP KIEM QUAN TRONG NHAT KHONG PHAI "co tra ve danh sach khong" MA LA
   "**co ro mot mau du lieu ca nhan nao khong**". Route nay CONG KHAI, khong token,
   va nguoi dung la TRE EM. Muc [3] gieo mot email that vao waitlist roi doi ca
   response KHONG chua email do, khong chua ten, khong chua ngay gio dang ky.

⚠️ `Cap`/`joinedAt`/thu tu doc THANG tu `Services/Crew.cs`, khong go tay lai o day
   — test go cung con so thi no khang dinh mot trang thai CU va bao hong dung luc
   ai do chinh moc cho dung (lop loi da mac 6 lan trong du an).
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _fbtest  # noqa: E402

TABLE = "astroq-main"
PROD = "--prod" in sys.argv
BASE = ("https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com" if PROD
        else "http://localhost:5080")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "AstroqSV", "src", "AstroqSV.Api", "Services", "Crew.cs")

ok_n = bad_n = 0


def ck(name, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {name}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {name}" + (f"  ({detail})" if detail else ""))


def aws(*a):
    return subprocess.run(("aws",) + a, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def call(method, path, token=None, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode() or "{}"
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:200]}


def put_waitlist(email, joined_ms):
    it = {"PK": {"S": f"WAITLIST#{email}"}, "SK": {"S": "SIGNUP"},
          "email": {"S": email}, "lang": {"S": "vi"},
          "joinedAt": {"N": str(joined_ms)}, "lastSentAt": {"N": "0"},
          "welcomed": {"BOOL": True}, "source": {"S": "test"}}
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


def del_waitlist(email):
    return aws("dynamodb", "delete-item", "--table-name", TABLE, "--key",
               json.dumps({"PK": {"S": f"WAITLIST#{email}"},
                           "SK": {"S": "SIGNUP"}})).returncode == 0


def wipe_user(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": f"USER#{uid}"}}),
            "--consistent-read")
    if r.returncode != 0:
        return 0
    n = 0
    for it in json.loads(r.stdout or "{}").get("Items", []):
        if aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]})).returncode == 0:
            n += 1
    return n


# ── [1] Luat doc THANG tu Crew.cs ─────────────────────────────────────────
print("[1] Doc luat tu Services/Crew.cs")
cs = open(SRC, encoding="utf-8").read()
m = re.search(r"public const int Cap = (\d+);", cs)
CAP = int(m.group(1)) if m else 0
ck("boc duoc so cho toi da", CAP > 0, str(CAP))
if not CAP:
    sys.exit(1)
# ⚠️ HANG RAO CHONG "them mot truong cho than thien" o lan sua sau: mot cho ngoi
#    chi duoc mang DUNG hai thu, va ca hai deu KHONG do tre go ra.
#    ⚠️ Ban dau phep kiem nay do `"name" not in code` — bao oan ngay, vi chinh chu
#       `namespace` cung chua no. Do DUNG HINH DANG cua record thay vi quet chu.
seat = re.search(r"record Seat\(([^)]*)\)", cs)
ck("`Crew.Seat` chi co dung 2 truong",
   seat and len([x for x in seat.group(1).split(",") if x.strip()]) == 2,
   seat.group(1) if seat else "khong tim thay")
ck("`Crew.Seat` khong mang ten hay email",
   seat and not re.search(r"(?i)\b(name|email)\b", seat.group(1)),
   seat.group(1) if seat else "-")

emails, uid, token = [], None, None
try:
    # ── [2] Route cong khai, khong can token ──────────────────────────────
    print("\n[2] Route CONG KHAI")
    st, d = call("GET", "/crew")
    ck("GET /crew tra 200 khi KHONG co token", st == 200, str(st))
    ck("tra ve so cho toi da khop Crew.cs", d.get("cap") == CAP,
       f'{d.get("cap")} vs {CAP}')
    ck("co `taken` va `seats`", isinstance(d.get("taken"), int)
       and isinstance(d.get("seats"), list), str(list(d))[:80])
    base_taken = d.get("taken", 0)

    # ── [3] KHONG RO MOT MAU DU LIEU CA NHAN NAO ──────────────────────────
    print("\n[3] Khong ro du lieu ca nhan — phep kiem quan trong nhat")
    now = int(time.time() * 1000)
    e1 = f"crew-{uuid.uuid4().hex[:10]}@simulator.amazonses.com"
    e2 = f"crew-{uuid.uuid4().hex[:10]}@simulator.amazonses.com"
    emails = [e1, e2]
    ck("gieo duoc 2 ban ghi waitlist", put_waitlist(e1, now - 5000)
       and put_waitlist(e2, now - 1000))
    time.sleep(1)
    st, d = call("GET", "/crew?nocache=" + uuid.uuid4().hex)
    raw = json.dumps(d)
    # Cache 60s trong Lambda co the giu ban cu — chap nhan, chi doi khi da thay.
    if d.get("taken", 0) < base_taken + 2:
        print("       (cache 60s con giu ban cu — cho roi thu lai)")
        time.sleep(62)
        st, d = call("GET", "/crew")
        raw = json.dumps(d)
    ck("da thay ca 2 nguoi moi", d.get("taken") == base_taken + 2,
       f'{d.get("taken")} vs {base_taken + 2}')
    ck("KHONG ro email nao", e1 not in raw and e2 not in raw and "@" not in raw,
       raw[:120])
    ck("KHONG co truong `email`/`name`/`joinedAt` trong response",
       not re.search(r'"(email|name|joinedAt|lang|source)"', raw), raw[:120])
    ck("moi cho chi co dung 2 truong `no` va `ch`",
       all(set(s) == {"no", "ch"} for s in d["seats"]),
       str(d["seats"][:2]))

    # ── [4] So hieu: som nhat la #1, va TAT DINH ──────────────────────────
    print("\n[4] So hieu — som nhat la #1, va khong doi giua hai lan goi")
    nos = [s["no"] for s in d["seats"]]
    ck("so hieu chay 1..n lien tuc", nos == list(range(1, len(nos) + 1)),
       str(nos[:6]))
    st, d2 = call("GET", "/crew")
    ck("goi lai cho ra DUNG cung mot danh sach", d2["seats"] == d["seats"])
    # Nguoi gieo som hon phai co so hieu nho hon — do bang chinh hai ban ghi vua gieo.
    ck("khong vuot qua so cho toi da", d["taken"] <= CAP, str(d["taken"]))

    # ── [5] /me/crew — cho cua CHINH minh ─────────────────────────────────
    print("\n[5] /me/crew — cho cua chinh minh")
    st, _ = call("GET", "/me/crew")
    ck("thieu token -> 401", st == 401, str(st))
    st, _ = call("GET", "/me/crew", token="rac.rac.rac")
    ck("token rac -> 401", st == 401, str(st))

    uid, token, _ = _fbtest.make_verified(e1)
    # Ho so co email = e1 (nguoi da nam trong phi hanh doan)
    prof = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
            "uid": {"S": uid}, "email": {"S": e1}, "name": {"S": "Bin"},
            "character": {"S": "sirius"}, "avatar": {"S": "ava/avam.png"},
            "createdAt": {"S": "2026-08-01T00:00:00Z"}}
    ck("gieo duoc ho so", aws("dynamodb", "put-item", "--table-name", TABLE,
                              "--item", json.dumps(prof)).returncode == 0)
    time.sleep(62)          # cho cache 60s het han de thay nhan vat vua gan
    st, mine = call("GET", "/me/crew", token=token)
    ck("tra 200 khi co token", st == 200, str(st))
    ck("noi dung so hieu cua chinh minh", isinstance(mine.get("no"), int),
       str(mine))
    ck("va nhan vat lay tu ho so", mine.get("ch") == "sirius", str(mine.get("ch")))
    ck("KHONG ro email trong /me/crew", "@" not in json.dumps(mine), str(mine))

    # Nhan vat cua nguoi do cung phai hien ra o danh sach chung — day la cho
    # chung minh phep noi email->uid->nhan vat chay that.
    st, d3 = call("GET", "/crew")
    mine_seat = [s for s in d3["seats"] if s["no"] == mine["no"]]
    ck("cho do o danh sach chung cung mang dung nhan vat",
       mine_seat and mine_seat[0]["ch"] == "sirius", str(mine_seat))

    # ── [6] Nguoi KHONG nam trong phi hanh doan ───────────────────────────
    print("\n[6] Nguoi khong co trong waitlist")
    e3 = f"nocrew-{uuid.uuid4().hex[:8]}@simulator.amazonses.com"
    uid3, token3, _ = _fbtest.make_verified(e3)
    prof3 = {"PK": {"S": f"USER#{uid3}"}, "SK": {"S": "PROFILE"},
             "uid": {"S": uid3}, "email": {"S": e3}, "name": {"S": "Bo"},
             "character": {"S": "umbra"}}
    aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(prof3))
    st, d4 = call("GET", "/me/crew", token=token3)
    # ⚠️ `no = null` chu KHONG phai 0 — 0 doc ra nhu mot so hieu.
    ck("khong trong doan -> no = null (KHONG phai 0)",
       st == 200 and d4.get("no") is None, str(d4))
    wipe_user(uid3)
    _fbtest.delete(token3)

    # ── [7] Client khong tu dat so hieu duoc ──────────────────────────────
    print("\n[7] Client khong tu dat duoc gi")
    st, d5 = call("GET", "/me/crew?no=1&uid=nguoi-khac", token=token)
    ck("uid/no trong query bi bo qua", st == 200 and d5.get("no") == mine.get("no"),
       str(d5))
    st, _ = call("POST", "/crew", body={"no": 1})
    ck("POST /crew -> 404/405 (khong co duong ghi)", st in (404, 405), str(st))

finally:
    print("\n[don] Xoa du lieu test")
    n = 0
    for e in emails:
        if del_waitlist(e):
            n += 1
    print(f"  Da xoa {n} ban ghi waitlist")
    if uid:
        print(f"  Da xoa {wipe_user(uid)} dong ho so")
    if token:
        ck("Da xoa tai khoan Firebase tam", _fbtest.delete(token))

# ⚠️ Luoi an toan cuoi cung — do lai SAU khi ca khoi try/finally da chay xong.
#    Bai hoc 16/08: phep kiem nam TRONG `finally` khong bat duoc "them mot muc
#    kiem vao duoi phan don".
left = [e for e in emails
        if aws("dynamodb", "get-item", "--table-name", TABLE, "--key",
               json.dumps({"PK": {"S": f"WAITLIST#{e}"}, "SK": {"S": "SIGNUP"}})
               ).stdout.strip() not in ("", "{}")]
ck("[don] Do lai sau cung: 0 ban ghi sot", not left, str(left))

print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
sys.exit(0 if bad_n == 0 else 1)
