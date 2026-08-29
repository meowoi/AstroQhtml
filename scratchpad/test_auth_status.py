# -*- coding: utf-8 -*-
"""test_auth_status.py — CHƯA KÍCH HOẠT THÌ CÓ ĐƯỢC BÁO ĐÚNG KHÔNG?

    python scratchpad/test_auth_status.py            # đo API chạy ở máy (localhost:5080)
    python scratchpad/test_auth_status.py --prod     # đo bản THẬT trên AWS

⚠️⚠️ VÌ SAO BỘ NÀY TỒN TẠI (29/08/2026). Kiến trúc đăng ký 2 giai đoạn để tài
   khoản CHƯA kích hoạt nằm ở DynamoDB (`PENDING#email`) và **chưa hề tồn tại
   trên Firebase**. Nên người đăng ký xong, chưa bấm link, quay lại gõ ĐÚNG email
   + ĐÚNG mật khẩu của mình thì Firebase trả `auth/invalid-credential` và trang
   nói **"Email hoặc mật khẩu không đúng."** — một câu SAI, đẩy người ta đi sửa
   đúng cái đang không hỏng. `POST /auth/status` là chỗ trả lời cho đúng.

⚠️ ĐÂY LÀ ROUTE TIẾT LỘ THÔNG TIN, nên nửa số phép đo dưới đây là đo phần KHÔNG
   được tiết lộ: sai mật khẩu, hay email của người khác, đều phải nhận `none` —
   nếu không thì nó thành máy dò "ai vừa đăng ký astroQ".

⚠️ Dùng địa chỉ giả lập của SES (`success+…@simulator.amazonses.com`): gửi vào
   địa chỉ không tồn tại là sinh bounce, mà bounce nhiều thì AWS khoá quyền gửi
   của CẢ tài khoản. Cùng luật đã ghi ở `test_login_hash.py`.

⚠️ MỌI THỨ TẠO RA ĐỀU ĐƯỢC DỌN trong `finally`, kể cả khi phép đo hỏng giữa đường.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROD = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
BASE = PROD if "--prod" in sys.argv else "http://localhost:5080"
TABLE = "astroq-main"
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
    """(status, dict). KHÔNG ném lỗi — mã lỗi ở đây chính là số liệu."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read().decode()
            st = r.status
    except urllib.error.HTTPError as e:
        raw, st = e.read().decode(), e.code
    try:
        return st, json.loads(raw or "{}")
    except ValueError:
        return st, {"_raw": raw}


def status(email, password):
    return call("POST", "/auth/status", {"email": email, "password": password})


def expire_pending(email):
    """Kéo `expiresAt` của bản ghi chờ về quá khứ, đo được nhánh `expired` thật.

    Không có cách nào khác ngoài chờ 10 phút. Sửa ĐÚNG một trường trên bản ghi
    THẬT rồi vẫn gọi ĐÚNG endpoint thật — không giả lập bước nào của route.
    """
    it = item("PENDING#%s" % email, "SIGNUP")
    if it is None:
        return False
    it["expiresAt"] = {"N": "1000000000"}      # 2001, chắc chắn đã qua
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


mine = "success+status-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
other = "success+status-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]

print("API: " + BASE)

try:
    print("\n=== [1] Chưa đăng ký gì → không được nói gì cả ===")
    st, d = status(mine, PW)
    check("email lạ trả 200", st == 200, st)
    check("và state = none", d.get("state") == "none", d)

    print("\n=== [2] Đăng ký xong, CHƯA bấm link → phải nói là ĐANG CHỜ ===")
    st, _ = call("POST", "/auth/register",
                 {"email": mine, "password": PW, "name": "Kiem Tra"})
    check("/auth/register nhận 202", st == 202, st)
    check("bản ghi chờ có thật trong DynamoDB",
          item("PENDING#%s" % mine, "SIGNUP") is not None)

    st, d = status(mine, PW)
    check("state = pending", d.get("state") == "pending", d)
    check("trả kèm email đã chuẩn hoá", d.get("email") == mine, d.get("email"))
    check("trả kèm số phút của link", d.get("expiresInMinutes") == 10,
          d.get("expiresInMinutes"))

    print("\n=== [3] KHÔNG ĐƯỢC làm máy dò ===")
    print("      Ba nhánh này mà rò là ai cũng gõ được email người lạ để biết")
    print("      người ta vừa đăng ký astroQ.")
    st, d = status(mine, PW + "-sai")
    check("sai mật khẩu → none (không phải 'sai mật khẩu')",
          d.get("state") == "none", d)
    st, d = status(mine, "")
    check("mật khẩu rỗng → none", d.get("state") == "none", d)
    st, d = status(other, PW)
    check("email khác chưa hề đăng ký → none", d.get("state") == "none", d)
    check("không nhánh nào lộ tên người đăng ký",
          "Kiem Tra" not in json.dumps(d, ensure_ascii=False), d)

    print("\n=== [4] Email hỏng định dạng ===")
    st, d = status("khong-phai-email", PW)
    check("trả 400", st == 400, st)
    check("kèm mã invalid-email", d.get("code") == "invalid-email", d)

    print("\n=== [5] Link hết hạn phải TÁCH khỏi 'đang chờ' ===")
    print("      Việc cần làm khác nhau: pending thì thư đang nằm trong hòm,")
    print("      expired thì phải bấm 'Gửi lại' mới có link sống.")
    check("kéo được expiresAt về quá khứ", expire_pending(mine))
    st, d = status(mine, PW)
    check("state = expired", d.get("state") == "expired", d)
    st, d = status(mine, PW + "-sai")
    check("bản ghi hết hạn vẫn không rò với mật khẩu sai",
          d.get("state") == "none", d)

    print("\n=== [6] Kích hoạt xong thì hết 'đang chờ' ===")
    print("      Bản ghi chờ bị xoá lúc kích hoạt, nên route phải im lại —")
    print("      lúc đó Firebase mới là nơi trả lời, và nó trả lời đúng.")
    aws("dynamodb", "delete-item", "--table-name", TABLE, "--key",
        json.dumps({"PK": {"S": "PENDING#%s" % mine}, "SK": {"S": "SIGNUP"}}))
    st, d = status(mine, PW)
    check("state = none sau khi bản ghi chờ biến mất",
          d.get("state") == "none", d)

finally:
    print("\n=== [7] Dọn dữ liệu test ===")
    for e in (mine, other):
        for pk, sk in (("PENDING#%s" % e, "SIGNUP"), ("EMAIL#%s" % e, "ACCOUNT")):
            aws("dynamodb", "delete-item", "--table-name", TABLE,
                "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}}))
    print("      xong")

print("\n%d/%d dat" % (ok_n, ok_n + bad_n))
sys.exit(1 if bad_n else 0)
