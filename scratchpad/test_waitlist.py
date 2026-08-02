# -*- coding: utf-8 -*-
"""
test_waitlist.py — kiem thu API POST /waitlist DOC LAP (quy tac 4 muc 6 CLAUDE.md).

Chay o may:   dotnet run  trong AstroqSV/src/AstroqSV.Api   roi   python test_waitlist.py
Chay ban that: python test_waitlist.py --prod

⚠️ DUNG DIA CHI GIA LAP CUA SES (`success@simulator.amazonses.com`) cho moi luot gui.
Gui vao dia chi khong ton tai la sinh bounce, ma ty le bounce cao thi AWS khoa quyen
gui cua ca tai khoan — hong luon duong email kich hoat tai khoan that.

Test tu don sach moi ban ghi WAITLIST minh tao ra trong `finally`.
"""
import argparse, json, subprocess, sys, time, urllib.error, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--prod", action="store_true", help="do tren ban that AWS")
ap.add_argument("--base", default=None)
args = ap.parse_args()

PROD = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
BASE = args.base or (PROD if args.prod else "http://localhost:5080")
TABLE = "astroq-main"
ORIGIN = "https://astroq.org"

OK = FAIL = 0
made = []          # email da tao ban ghi -> don trong finally


def check(label, cond, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(extra)) if extra else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(extra))


def post(path, body, origin=ORIGIN):
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST",
                                 headers={"Content-Type": "application/json", "Origin": origin})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw or "{}")
        except Exception:
            return e.code, {"raw": raw}


def ddb_get(email):
    key = json.dumps({"PK": {"S": "WAITLIST#" + email}, "SK": {"S": "SIGNUP"}})
    out = subprocess.run(["aws", "dynamodb", "get-item", "--table-name", TABLE,
                          "--key", key, "--output", "json"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return (json.loads(out.stdout or "{}") or {}).get("Item")


def ddb_del(email):
    key = json.dumps({"PK": {"S": "WAITLIST#" + email}, "SK": {"S": "SIGNUP"}})
    subprocess.run(["aws", "dynamodb", "delete-item", "--table-name", TABLE, "--key", key],
                   capture_output=True, text=True)


def addr(tag):
    e = "success+%s%d@simulator.amazonses.com" % (tag, int(time.time()))
    made.append(e)
    return e


print("=== POST /waitlist @ %s ===" % BASE)
try:
    # ------------------------------------------------------------ [1] duong chinh
    print("\n[1] Dang ky lan dau")
    e1 = addr("new")
    st, r = post("/waitlist", {"email": e1, "lang": "vi"})
    check("tra 202", st == 202, st)
    check("ok = true", r.get("ok") is True, r)
    check("dup = false (chua tung dang ky)", r.get("dup") is False, r)
    check("mailSent = true (SES da nhan)", r.get("mailSent") is True, r)
    it = ddb_get(e1)
    check("da ghi ban ghi WAITLIST vao DynamoDB", it is not None)
    if it:
        check("luu dung email", it["email"]["S"] == e1)
        check("luu dung ngon ngu", it["lang"]["S"] == "vi", it.get("lang"))
        check("co moc joinedAt", int(it["joinedAt"]["N"]) > 0)
        check("danh dau da gui thu", it["welcomed"]["BOOL"] is True)
        check("ghi lai origin de tra cuu", it["source"]["S"] == ORIGIN, it.get("source"))
        check("KHONG dat ttl (waitlist phai song toi ngay ra mat)", "ttl" not in it, list(it.keys()))
        check("KHONG luu mat khau/token gi", not any(k in it for k in ("pwdHash", "tokenHash", "pwdSalt")))

    # ------------------------------------------------------------ [2] dang ky lai
    print("\n[2] Dang ky lai cung dia chi")
    joined0 = int(it["joinedAt"]["N"]) if it else 0
    st, r = post("/waitlist", {"email": e1, "lang": "en"})
    check("tra 202", st == 202, st)
    check("bao dup = true", r.get("dup") is True, r)
    check("van bao mailSent = true (thu cu da toi)", r.get("mailSent") is True, r)
    it2 = ddb_get(e1)
    check("GIU NGUYEN moc dang ky dau tien", it2 and int(it2["joinedAt"]["N"]) == joined0,
          "%s -> %s" % (joined0, it2 and it2["joinedAt"]["N"]))
    check("cap nhat ngon ngu moi nhat", it2 and it2["lang"]["S"] == "en", it2 and it2.get("lang"))
    check("KHONG sinh ban ghi thu hai", it2 is not None)

    # ------------------------------------------------------------ [3] cooldown
    print("\n[3] Cooldown chan bom thu (60s cho CUNG mot dia chi)")
    sent_before = int(it2["lastSentAt"]["N"]) if it2 else 0
    for i in range(3):
        post("/waitlist", {"email": e1, "lang": "vi"})
    it3 = ddb_get(e1)
    check("3 luot lien tiep KHONG lam doi moc gui thu",
          it3 and int(it3["lastSentAt"]["N"]) == sent_before,
          "%s -> %s" % (sent_before, it3 and it3["lastSentAt"]["N"]))
    check("nguoi dung van thay ket qua thanh cong", post("/waitlist", {"email": e1})[1].get("ok") is True)

    # ------------------------------------------------------------ [4] email hong
    print("\n[4] Email khong hop le")
    for bad, why in [("", "rong"), ("khongcoa", "khong co @"), ("a@b", "khong co ten mien"),
                     ("a b@c.com", "co khoang trang"), ("@no.com", "thieu phan dau"),
                     ("x" * 250 + "@dai.com", "dai qua 254 ky tu")]:
        st, r = post("/waitlist", {"email": bad, "lang": "vi"})
        check("tu choi email %s -> 400" % why, st == 400 and r.get("code") == "invalid-email", (st, r))
    st, r = post("/waitlist", {"lang": "vi"})
    check("thieu han truong email -> 400", st == 400, (st, r))
    st, r = post("/waitlist", {"email": None, "lang": None})
    check("email = null -> 400", st == 400, (st, r))

    # ------------------------------------------------------------ [5] bay bot
    print("\n[5] Bay bot")
    e5 = addr("bot")
    st, r = post("/waitlist", {"email": e5, "lang": "vi", "hp": "http://spam.example"})
    check("tra 202 nhu binh thuong (khong lo cho bot biet)", st == 202, st)
    check("ok = true", r.get("ok") is True, r)
    check("KHONG ghi ban ghi nao", ddb_get(e5) is None)

    # ------------------------------------------------------------ [6] chuan hoa dau vao
    print("\n[6] Chuan hoa dau vao")
    e6 = addr("case")
    st, r = post("/waitlist", {"email": "  " + e6.upper() + "  ", "lang": "VI"})
    check("cat khoang trang + ha chu thuong", st == 202 and ddb_get(e6) is not None, st)
    e7 = addr("lang")
    post("/waitlist", {"email": e7, "lang": "tieng-sao-hoa"})
    i7 = ddb_get(e7)
    check("ngon ngu la -> ve mac dinh 'vi'", i7 and i7["lang"]["S"] == "vi", i7 and i7.get("lang"))

    # ------------------------------------------------------------ [7] khong dung cham luong tai khoan
    print("\n[7] Khong dung cham luong dang ky tai khoan")
    e8 = addr("iso")
    post("/waitlist", {"email": e8, "lang": "vi"})
    check("KHONG tao ban ghi giu cho EMAIL#", subprocess.run(
        ["aws", "dynamodb", "get-item", "--table-name", TABLE, "--key",
         json.dumps({"PK": {"S": "EMAIL#" + e8}, "SK": {"S": "ACCOUNT"}}), "--output", "json"],
        capture_output=True, text=True).stdout.strip() in ("", "{}"))
    check("KHONG tao ban ghi PENDING#", subprocess.run(
        ["aws", "dynamodb", "get-item", "--table-name", TABLE, "--key",
         json.dumps({"PK": {"S": "PENDING#" + e8}, "SK": {"S": "SIGNUP"}}), "--output", "json"],
        capture_output=True, text=True).stdout.strip() in ("", "{}"))
    st, r = post("/auth/resend", {"email": e8})
    check("dang ky waitlist KHONG cho phep goi /auth/resend", st == 404 and r.get("code") == "no-pending", (st, r))

    # ------------------------------------------------------------ [8] phuong thuc & CORS
    print("\n[8] Phuong thuc va CORS")
    req = urllib.request.Request(BASE + "/waitlist", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as rr:
            st = rr.status
    except urllib.error.HTTPError as ex:
        st = ex.code
    check("GET /waitlist -> 405", st == 405, st)
    st, r = post("/waitlist", {"email": addr("origin")}, origin="https://astroq.org.evil.co")
    check("origin gia mao van khong lam vo server", st in (202, 400), (st, r))

finally:
    print("\n--- Don du lieu test ---")
    for e in made:
        ddb_del(e)
    left = [e for e in made if ddb_get(e) is not None]
    check("da xoa het ban ghi test", not left, left)

print("\n================ KET QUA: %d dat / %d hong ================" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
