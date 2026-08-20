# -*- coding: utf-8 -*-
"""test_login_hash.py — MẬT KHẨU ĐẶT LÚC ĐĂNG KÝ CÓ ĐĂNG NHẬP ĐƯỢC KHÔNG?

    python scratchpad/test_login_hash.py        # đo bản THẬT trên AWS

⚠️⚠️ VÌ SAO BỘ NÀY TỒN TẠI (20/08/2026). Ngày mở cửa, một người dùng thật báo
   "đã kích hoạt xong mà đăng nhập cứ báo sai email hoặc mật khẩu". Không có bản
   ghi nào để tra, vì ĐĂNG NHẬP KHÔNG ĐI QUA LAMBDA: `js/firebase-auth.js` gọi
   thẳng `signInWithEmailAndPassword` tới Google, nên CloudWatch trắng trơn và
   không ai biết Firebase đã trả lỗi gì.

   Phải phân biệt hai khả năng, vì hậu quả khác nhau một trời một vực:
     (a) người đó gõ sai mật khẩu → một ca hỗ trợ, sửa bằng "Quên mật khẩu?";
     (b) `FirebaseService.ImportVerifiedUserAsync` đẩy hash PBKDF2 lên SAI (số
         vòng, độ dài khoá, hay salt) nên KHÔNG tài khoản nào đăng nhập được →
         mở cửa mà cửa khoá, và mọi người đăng ký hôm nay đều mất tài khoản.

   Bộ này trả lời bằng cách đi ĐÚNG luồng thật — POST /auth/register → GET
   /auth/activate → `signInWithPassword` bằng chính mật khẩu vừa đặt. Đăng nhập
   được là loại bỏ (b).

⚠️ KHÔNG đo bằng lời khai của API: `uid` đọc THẲNG từ DynamoDB (`EMAIL#…/ACCOUNT`)
   rồi đối chiếu với `localId` mà Firebase trả về. Hai nguồn khớp nhau mới là
   "cùng một tài khoản", chứ không phải "cả hai đều trả 200".

⚠️ Dùng địa chỉ giả lập của SES (`success+…@simulator.amazonses.com`): gửi vào
   địa chỉ không tồn tại là sinh bounce, mà bounce nhiều thì AWS khoá quyền gửi
   của CẢ tài khoản. Cùng luật đã ghi ở `test_waitlist_bonus.py`.

⚠️ MỌI THỨ TẠO RA ĐỀU ĐƯỢC DỌN trong `finally`, kể cả khi phép đo hỏng giữa
   đường — nếu không thì mỗi lần chạy để lại một tài khoản thật trong Firebase.
"""
import base64
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
TABLE = "astroq-main"
# apiKey Web — CÔNG KHAI theo thiết kế, xem `js/firebase-config.js`.
APIKEY = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
IDP = "https://identitytoolkit.googleapis.com/v1/accounts"
PW = "Astroq!2026-kiemtra"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + label + (("  " + str(detail)) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] " + label + "  " + str(detail))


def aws(*a):
    return subprocess.run(("aws",) + a, capture_output=True, text=True, encoding="utf-8")


def item(pk, sk):
    r = aws("dynamodb", "get-item", "--table-name", TABLE,
            "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}}))
    if r.returncode:
        return None
    return (json.loads(r.stdout) or {}).get("Item")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Chặn việc tự đi theo 302 — đích là trang tĩnh, không phải thứ cần đo."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def activate(email, tok):
    op = urllib.request.build_opener(NoRedirect)
    url = BASE + "/auth/activate?e=%s&t=%s" % (urllib.parse.quote(email), tok)
    try:
        with op.open(urllib.request.Request(url), timeout=45) as r:
            return r.status, r.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "")


def put_token(email, tok):
    """Đổi `tokenHash` của bản ghi chờ sang băm của token do mình sinh.

    Thư kích hoạt đi vào hộp giả lập nên không đọc lại được, và bản ghi chờ chỉ
    lưu băm. `PasswordHasher.HashToken` = base64(SHA256(utf8(token))) — dựng lại
    được y nguyên, nên vẫn đi qua ĐÚNG endpoint thật, không giả lập bước nào.
    """
    it = item("PENDING#%s" % email, "SIGNUP")
    if it is None:
        return False
    it["tokenHash"] = {"S": base64.b64encode(
        hashlib.sha256(tok.encode("utf-8")).digest()).decode()}
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


def signin(email, pw):
    """(thanh_cong, uid-hoac-ma-loi). KHÔNG ném lỗi — lỗi ở đây CHÍNH LÀ số liệu."""
    body = json.dumps({"email": email, "password": pw, "returnSecureToken": True}).encode()
    req = urllib.request.Request("%s:signInWithPassword?key=%s" % (IDP, APIKEY),
                                 data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
            return True, d
    except urllib.error.HTTPError as e:
        d = json.loads(e.read().decode() or "{}")
        return False, (d.get("error") or {}).get("message", "?")


email = "success+login-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
uid = None

try:
    print("\n=== [1] Đăng ký + kích hoạt qua ĐÚNG endpoint thật ===")
    st, _ = call("POST", "/auth/register",
                 {"email": email, "password": PW, "name": "Kiem Tra"})
    check("/auth/register nhận 202", st == 202, st)

    tok = uuid.uuid4().hex + uuid.uuid4().hex
    check("đặt được token kích hoạt vào bản ghi chờ", put_token(email, tok))

    st, loc = activate(email, tok)
    check("/auth/activate báo kích hoạt THÀNH CÔNG",
          "activated=1&reason=ok" in loc, "%s -> %s" % (st, loc[:70]))

    it = item("EMAIL#%s" % email, "ACCOUNT")
    uid = None if it is None else it.get("uid", {}).get("S")
    check("tài khoản đã được tạo (tra uid từ EMAIL#)", bool(uid), uid)

    print("\n=== [2] Đăng nhập bằng CHÍNH mật khẩu đã đặt lúc đăng ký ===")
    print("      Đây là phép đo quyết định: hash PBKDF2 mà")
    print("      `ImportVerifiedUserAsync` đẩy lên có xác thực được không.")
    ok, info = signin(email, PW)
    check("signInWithPassword THÀNH CÔNG với mật khẩu đúng", ok,
          info if not ok else "")
    check("và trả về ĐÚNG uid backend đã tạo",
          ok and info.get("localId") == uid,
          "" if not ok else "%s vs %s" % (info.get("localId"), uid))
    # ⚠️ ĐỌC TRONG ID TOKEN, KHÔNG đọc ở thân phản hồi. `signInWithPassword`
    #    KHÔNG trả trường `emailVerified` ở cấp ngoài (lần chạy đầu bộ này báo
    #    [HONG] chỉ vì tôi tìm sai chỗ). Cờ nằm trong claim của JWT — và đó cũng
    #    là chỗ DUY NHẤT có ý nghĩa, vì `Program.cs` (policy "verified") xét
    #    claim của token, không xét JSON của Google.
    claims = {}
    if ok:
        seg = info["idToken"].split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4)))
    check("ID token mang claim `email_verified` = true",
          claims.get("email_verified") is True,
          str(claims.get("email_verified")))

    print("\n=== [3] Đối chứng: mật khẩu SAI phải bị từ chối ===")
    ok2, info2 = signin(email, PW + "-sai")
    check("mật khẩu sai bị từ chối", not ok2, info2 if not ok2 else "VAO DUOC?!")

finally:
    print("\n=== [4] Dọn dữ liệu test ===")
    for pk, sk in (("EMAIL#%s" % email, "ACCOUNT"),
                   ("PENDING#%s" % email, "SIGNUP")):
        aws("dynamodb", "delete-item", "--table-name", TABLE,
            "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}}))
    if uid:
        r = aws("dynamodb", "query", "--table-name", TABLE,
                "--key-condition-expression", "PK = :p",
                "--expression-attribute-values", json.dumps({":p": {"S": "USER#%s" % uid}}),
                "--projection-expression", "SK")
        if r.returncode == 0:
            for row in (json.loads(r.stdout) or {}).get("Items", []):
                aws("dynamodb", "delete-item", "--table-name", TABLE, "--key",
                    json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": row["SK"]}))
        # Xoá tài khoản Firebase bằng idToken của CHÍNH NÓ — không cần service
        # account, và cũng không xoá được tài khoản của ai khác.
        ok, d = signin(email, PW)
        if ok:
            try:
                rq = urllib.request.Request(
                    "%s:delete?key=%s" % (IDP, APIKEY),
                    data=json.dumps({"idToken": d["idToken"]}).encode(), method="POST")
                rq.add_header("Content-Type", "application/json")
                urllib.request.urlopen(rq, timeout=30).read()
                print("      đã xoá tài khoản Firebase", email)
            except Exception as ex:
                print("      ⚠️ XOÁ TAY tài khoản Firebase %s — %s" % (email, ex))
        else:
            print("      ⚠️ XOÁ TAY tài khoản Firebase %s (không đăng nhập được để xoá)" % email)

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
    sys.exit(1 if bad_n else 0)
