# -*- coding: utf-8 -*-
"""
test_auth_cooldown.py — kiểm cooldown gửi email chống dùng /auth/register + /auth/resend
làm máy phát spam (mục 3b của rà soát bảo mật 01/08/2026).

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_auth_cooldown.py                 # http://localhost:5080
    python scratchpad/test_auth_cooldown.py <base-url>      # bản thật trên AWS

⚠️ DÙNG ĐỊA CHỈ SES SIMULATOR (`success@simulator.amazonses.com`) — SES nhận và KHÔNG
   bounce, nên test không làm hại uy tín miền gửi. Địa chỉ này cố định nên test tự dọn
   bản ghi PENDING trước và sau.

Điều CẦN chứng minh (không quan sát được SES từ ngoài, nên đo bằng dấu vết DynamoDB):
  · lần register đầu → tạo bản ghi chờ, KHÔNG throttled;
  · register lại NGAY → throttled=true, và tokenHash + lastSentAt KHÔNG đổi
    (không cấp token mới = không gửi email mới);
  · resend ngay → cũng throttled.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"
EMAIL = "success@simulator.amazonses.com"   # SES nhận, không bounce

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e:
        return 0, {"_err": str(e)}


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True, timeout=60)


def pending_row():
    r = aws("dynamodb", "get-item", "--table-name", TABLE, "--consistent-read",
            "--key", json.dumps({"PK": {"S": f"PENDING#{EMAIL}"}, "SK": {"S": "SIGNUP"}}))
    return None if r.returncode != 0 else json.loads(r.stdout or "{}").get("Item")


def wipe_pending():
    aws("dynamodb", "delete-item", "--table-name", TABLE,
        "--key", json.dumps({"PK": {"S": f"PENDING#{EMAIL}"}, "SK": {"S": "SIGNUP"}}))


def main():
    print(f"=== Cooldown gui email @ {BASE} ===\n")
    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    wipe_pending()
    try:
        print("\n[1] Lan register DAU — gui that")
        st, d = call("POST", "/auth/register",
                     {"name": "Cooldown Test", "email": EMAIL, "password": "Test123456"})
        check("register -> 202", st == 202, f"status={st}")
        check("KHONG throttled o lan dau", d.get("throttled") is not True,
              str(d.get("throttled")))
        row1 = pending_row()
        check("Da tao ban ghi PENDING", row1 is not None)
        th1 = row1 and row1.get("tokenHash", {}).get("S")
        ls1 = row1 and row1.get("lastSentAt", {}).get("N")
        check("Ban ghi co lastSentAt > 0", bool(ls1) and int(ls1) > 0, str(ls1))

        print("\n[2] register LAI ngay -> throttled, KHONG cap token moi")
        st, d = call("POST", "/auth/register",
                     {"name": "Cooldown Test", "email": EMAIL, "password": "Test123456"})
        check("register lai -> 202", st == 202, f"status={st}")
        check("throttled = true", d.get("throttled") is True, str(d.get("throttled")))
        row2 = pending_row()
        th2 = row2 and row2.get("tokenHash", {}).get("S")
        ls2 = row2 and row2.get("lastSentAt", {}).get("N")
        # ⚠️ Cốt tử: token KHÔNG đổi = không gửi email mới, không churn bản ghi.
        check("tokenHash KHONG doi (khong cap token moi = khong gui email moi)",
              th1 == th2 and th1 is not None, f"{th1} vs {th2}")
        check("lastSentAt KHONG doi", ls1 == ls2, f"{ls1} vs {ls2}")

        print("\n[3] resend ngay -> cung throttled")
        st, d = call("POST", "/auth/resend", {"email": EMAIL})
        check("resend -> 200", st == 200, f"status={st}")
        check("resend throttled = true", d.get("throttled") is True,
              str(d.get("throttled")))
        row3 = pending_row()
        th3 = row3 and row3.get("tokenHash", {}).get("S")
        check("resend cung KHONG cap token moi", th3 == th1, f"{th1} vs {th3}")

        print("\n[4] Du lieu vao sai van bi chan truoc cooldown")
        st, d = call("POST", "/auth/register",
                     {"name": "x", "email": "khong-phai-email", "password": "Test123456"})
        check("email sai -> 400 invalid-email",
              st == 400 and d.get("code") == "invalid-email", f"{st} {d.get('code')}")

    finally:
        print("\n[don] Xoa ban ghi PENDING")
        wipe_pending()
        check("Da xoa PENDING", pending_row() is None)

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
