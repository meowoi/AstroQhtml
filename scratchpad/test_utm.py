# -*- coding: utf-8 -*-
"""
test_utm.py - kiem thu DUONG QUY NGUON (UTM) DOC LAP (quy tac 4 muc 6 CLAUDE.md).

Chay o may:    dotnet run  trong AstroqSV/src/AstroqSV.Api   roi   python test_utm.py
Chay ban that: python test_utm.py --prod

Do CA HAI cua vao: POST /waitlist  va  POST /auth/register -> GET /auth/activate.

⚠️⚠️ MOI PHEP KIEM COT TU DOC THANG BAN GHI TRONG DYNAMODB, khong do bang loi khai
   cua API. API tra 202 nghia la no NHAN duoc request - no khong chung minh duoc rang
   nhan chien dich da duoc LOC dung va LUU dung cho. Bai hoc lay tu test_auth_pending.py:
   co passwordKept co the dung trong khi ban ghi van bi ghi de.

⚠️ DUNG DIA CHI GIA LAP CUA SES (success@simulator.amazonses.com). Gui vao dia chi
   khong ton tai la sinh bounce, ma ty le bounce cao thi AWS khoa quyen gui cua CA
   TAI KHOAN - hong luon duong email kich hoat that.

⚠️ MUC [5] GIEO THANG MOT BAN GHI PENDING voi token BIET TRUOC roi goi /activate.
   Token that chi di qua email nen test khong doc duoc; nhung
   tokenHash = base64(sha256(utf8(token)))  (xem PasswordHasher.HashToken) nen gieo
   duoc. Day la cach DUY NHAT do duoc rang nhan chien dich CHAY HET duong tu luc
   dang ky toi ban ghi ho so.
"""
import argparse, base64, hashlib, json, os, subprocess, sys, time
import urllib.error, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("--prod", action="store_true", help="do tren ban that AWS")
ap.add_argument("--base", default=None)
args = ap.parse_args()

PROD = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
BASE = args.base or (PROD if args.prod else "http://localhost:5080")
TABLE = "astroq-main"
ORIGIN = "https://astroq.org"

OK = FAIL = 0
wait_made = []      # email waitlist da tao
pend_made = []      # email pending da tao
uid_made = []       # uid ho so da tao


def check(label, cond, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(extra)) if extra else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(extra))


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST",
                                 headers={"Content-Type": "application/json",
                                          "Origin": ORIGIN})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw or "{}")
        except Exception:
            return e.code, {"raw": raw}


class _NoRedir(urllib.request.HTTPRedirectHandler):
    """/auth/activate tra ve 302 - phai doc chinh cu chuyen huong, khong di theo."""
    def redirect_request(self, *a, **k):
        return None


def get_nofollow(path):
    """
    ⚠️ HA CHU THUONG MOI TEN HEADER. API Gateway HTTP API tra ve `location` (chu
       thuong), con Kestrel o may tra `Location`. `dict(r.headers)` giu nguyen chu
       goc nen mot phep kiem doc `hdr["Location"]` DAT o may va HONG tren ban that —
       vi mot ly do khong lien quan gi toi san pham. Da gap that 18/08/2026.
    """
    op = urllib.request.build_opener(_NoRedir)
    try:
        with op.open(BASE + path, timeout=40) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}


def ddb(argv):
    out = subprocess.run(["aws", "dynamodb"] + argv + ["--output", "json"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return json.loads(out.stdout or "{}") or {}


def item_of(pk, sk):
    key = json.dumps({"PK": {"S": pk}, "SK": {"S": sk}})
    return (ddb(["get-item", "--table-name", TABLE, "--key", key]) or {}).get("Item")


def del_item(pk, sk):
    key = json.dumps({"PK": {"S": pk}, "SK": {"S": sk}})
    ddb(["delete-item", "--table-name", TABLE, "--key", key])


def set_attr(pk, sk, name, av):
    """Doi mot thuoc tinh cua ban ghi - dung de lui cooldown / gieo tokenHash."""
    ddb(["update-item", "--table-name", TABLE,
         "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}}),
         "--update-expression", "SET #a = :v",
         "--expression-attribute-names", json.dumps({"#a": name}),
         "--expression-attribute-values", json.dumps({":v": av})])


def src_of(item):
    """Doc truong src. Thieu truong = chuoi rong (ban ghi cu)."""
    if item is None:
        return None
    return item.get("src", {}).get("S", "")


def addr(tag):
    return "success+%s%d@simulator.amazonses.com" % (tag, int(time.time() * 1000) % 10 ** 9)


def wl(tag):
    e = addr(tag)
    wait_made.append(e)
    return e


print("=== DUONG QUY NGUON (UTM) @ %s ===" % BASE)
try:
    # ============ [1] WAITLIST: nhan di vao ban ghi ============
    print("")
    print("[1] Waitlist ghi dung nhan chien dich")
    e = wl("src")
    st, r = post("/waitlist", {"email": e, "lang": "vi", "src": "fb/post/ra-mat-20-08"})
    check("tra 202", st == 202, st)
    it = item_of("WAITLIST#" + e, "SIGNUP")
    check("ban ghi co that", it is not None)
    check("luu dung nhan", src_of(it) == "fb/post/ra-mat-20-08", src_of(it))
    # ⚠️ `source` (header Origin) la TRUONG KHAC va phai con nguyen. Ghi de no la vua
    #    mat du lieu cu vua tron hai nghia vao mot cho.
    check("source (Origin) van giu nguyen, KHONG bi ghi de",
          it is not None and it.get("source", {}).get("S") == ORIGIN,
          it is not None and it.get("source"))

    # ============ [2] SERVER LOC LAI, khong tin client ============
    # ⚠️ MUC QUAN TRONG NHAT CUA CA BO. Chuoi nay do CLIENT gui - ai cung sua duoc bang
    #    DevTools - ma no di thang vao DynamoDB roi hien ra o trang bao cao admin.
    print("")
    print("[2] Server loc lai chuoi client gui len")
    cases = [
        ("HOA thanh thuong",           "FB/Post/Ra-Mat",           "fb/post/ra-mat"),
        ("bo ky tu la",                "fb<script>/po st/@#$camp", "fbscript/post/camp"),
        ("cat con 24 ky tu moi phan",  "f" * 40 + "/b",            "f" * 24 + "/b"),
        ("bo phan rong",               "fb//post",                 "fb/post"),
        ("chi giu 3 phan dau",         "a/b/c/d/e",                "a/b/c"),
        ("chuoi rac -> rong",          "!!!/???",                  ""),
        ("khoang trang -> rong",       "   ",                      ""),
        ("giu chu so va . _ -",        "fb_2/po.st/x-1",           "fb_2/po.st/x-1"),
    ]
    for label, sent, want in cases:
        e2 = wl("f")
        post("/waitlist", {"email": e2, "lang": "vi", "src": sent})
        got = src_of(item_of("WAITLIST#" + e2, "SIGNUP"))
        check("loc: " + label, got == want,
              "gui=%r -> luu=%r (cho %r)" % (sent, got, want))

    e3 = wl("nosrc")
    post("/waitlist", {"email": e3, "lang": "vi"})
    got3 = src_of(item_of("WAITLIST#" + e3, "SIGNUP"))
    check("khong gui src -> luu chuoi rong (khong vo)", got3 == "", got3)

    st, _ = post("/waitlist", {"email": wl("num"), "lang": "vi", "src": 12345})
    check("src sai kieu -> API khong vo", st in (202, 400), st)

    # ============ [3] GIU LUOT CHAM DAU TIEN ============
    # ⚠️ Cau hoi la "cai gi mang nguoi nay toi" - do la LAN DAU. Ghi de theo luot cuoi
    #    thi cong cua bai dang bien mat va moi bai deu trong nhu vo dung.
    print("")
    print("[3] Dang ky lai KHONG ghi de nguon cua luot dau")
    e4 = wl("first")
    post("/waitlist", {"email": e4, "lang": "vi", "src": "fb/post/bai-mot"})
    post("/waitlist", {"email": e4, "lang": "en", "src": "zalo/post/bai-hai"})
    it4 = item_of("WAITLIST#" + e4, "SIGNUP")
    check("giu nhan cua luot DAU", src_of(it4) == "fb/post/bai-mot", src_of(it4))
    check("nhung ngon ngu VAN cap nhat (khong dong bang ca ban ghi)",
          it4 is not None and it4["lang"]["S"] == "en",
          it4 is not None and it4.get("lang"))

    # Chieu nguoc lai: luot dau khong co nhan thi luot sau duoc nhan.
    e5 = wl("late")
    post("/waitlist", {"email": e5, "lang": "vi"})
    post("/waitlist", {"email": e5, "lang": "vi", "src": "fb/post/muon"})
    got5 = src_of(item_of("WAITLIST#" + e5, "SIGNUP"))
    check("luot dau KHONG co nhan -> nhan lan sau duoc ghi", got5 == "fb/post/muon", got5)

    # ============ [4] DANG KY TAI KHOAN ============
    print("")
    print("[4] /auth/register ghi nhan vao ban ghi cho")
    e6 = addr("reg")
    pend_made.append(e6)
    st, r = post("/auth/register", {"name": "Bin", "email": e6,
                                    "password": "matkhau123", "src": "FB/Post/Bai-A"})
    check("tra 202", st == 202, st)
    p6 = item_of("PENDING#" + e6, "SIGNUP")
    check("ban ghi cho co that", p6 is not None)
    check("nhan da duoc loc va luu", src_of(p6) == "fb/post/bai-a", src_of(p6))

    # ⚠️ Dang ky de len mot dia chi DANG CHO khong duoc viet lai nguon cua nan nhan -
    #    cung luat da dung cho mat khau va ten (vet 18/08/2026).
    # Lui lastSentAt de vuot cooldown 60s ma khong phai ngu 61 giay.
    set_attr("PENDING#" + e6, "SIGNUP", "lastSentAt", {"N": "0"})
    post("/auth/register", {"name": "Ke khac", "email": e6,
                            "password": "matkhaukhac", "src": "evil/post/cuop-nguon"})
    got6 = src_of(item_of("PENDING#" + e6, "SIGNUP"))
    check("dang ky lai KHONG viet lai nguon cua luot dau", got6 == "fb/post/bai-a", got6)

    e7 = addr("regno")
    pend_made.append(e7)
    post("/auth/register", {"name": "Bin", "email": e7, "password": "matkhau123"})
    got7 = src_of(item_of("PENDING#" + e7, "SIGNUP"))
    check("dang ky khong gui src -> rong, khong vo", got7 == "", got7)

    # ============ [5] NHAN CHAY HET DUONG TOI HO SO ============
    # ⚠️ Phep kiem dat gia nhat cua ca bo: no chung minh nhan DI DUOC tu luc dang ky
    #    toi ban ghi PROFILE. Cac muc tren chi chung minh no vao toi ban ghi cho.
    print("")
    print("[5] Kich hoat -> nhan sang ho so (gieo token biet truoc)")
    e8 = addr("act")
    pend_made.append(e8)
    post("/auth/register", {"name": "Bin", "email": e8,
                            "password": "matkhau123", "src": "fb/post/den-cung"})
    token = "a" * 64
    thash = base64.b64encode(hashlib.sha256(token.encode("utf-8")).digest()).decode()
    set_attr("PENDING#" + e8, "SIGNUP", "tokenHash", {"S": thash})

    st, hdr = get_nofollow("/auth/activate?e=%s&t=%s"
                           % (urllib.parse.quote(e8), token))
    check("kich hoat tra ve mot cu chuyen huong", st in (301, 302, 303, 307), st)
    loc = hdr.get("location", "")
    check("chuyen huong bao kich hoat thanh cong", "activated=1" in loc, loc[:120])

    em = item_of("EMAIL#" + e8, "ACCOUNT")
    uid = em.get("uid", {}).get("S", "") if em else ""
    check("da tao ban ghi giu cho email", bool(uid), em and list(em.keys()))
    if uid:
        uid_made.append(uid)
        prof = item_of("USER#" + uid, "PROFILE")
        check("da tao ho so", prof is not None)
        check("HO SO MANG DUNG NHAN CHIEN DICH",
              src_of(prof) == "fb/post/den-cung", src_of(prof))
        check("ban ghi cho da bi don", item_of("PENDING#" + e8, "SIGNUP") is None)

finally:
    print("")
    print("[don] xoa du lieu test")
    for e in wait_made:
        del_item("WAITLIST#" + e, "SIGNUP")
    for e in pend_made:
        del_item("PENDING#" + e, "SIGNUP")
        del_item("EMAIL#" + e, "ACCOUNT")
    for uid in uid_made:
        del_item("USER#" + uid, "PROFILE")
        del_item("USER#" + uid, "WALLET")
    if uid_made:
        try:
            import _fbtest
            tok = _fbtest._access_token()
            url = ("https://identitytoolkit.googleapis.com/v1/projects/"
                   "astroq-782f7/accounts:delete")
            for uid in uid_made:
                req = urllib.request.Request(
                    url, data=json.dumps({"localId": uid}).encode(), method="POST",
                    headers={"Content-Type": "application/json",
                             "Authorization": "Bearer " + tok})
                urllib.request.urlopen(req, timeout=30).read()
                print("  da xoa tai khoan Firebase " + uid)
        except Exception as ex:
            print("  [!] chua xoa duoc tai khoan Firebase: " + str(ex))

print("")
print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
