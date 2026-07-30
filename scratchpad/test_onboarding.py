# -*- coding: utf-8 -*-
"""
test_onboarding.py — kiểm thử ĐỘC LẬP endpoint /me/onboarding (chưa nối vào giao diện).

Cách chạy:
    # 1) bật backend ở máy
    cd AstroqSV/src/AstroqSV.Api && dotnet run
    # 2) chạy test
    python scratchpad/test_onboarding.py                # mặc định http://localhost:5080
    python scratchpad/test_onboarding.py <base-url>     # ví dụ bản thật trên AWS

Test tự lo trọn vòng đời dữ liệu của mình:
  · tạo một tài khoản Firebase tạm (REST signUp bằng web apiKey) để có ID token thật
  · tự tạo / xoá bản ghi PROFILE trong DynamoDB bằng aws CLI
  · CUỐI CÙNG xoá cả hai, không để lại rác (kể cả khi test hỏng giữa chừng)

Bao gồm cả nhánh hỏng: không token, token rác, token của uid chưa có hồ sơ.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")

# apiKey web của Firebase — công khai theo thiết kế (xem js/firebase-config.js)
API_KEY = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
IDP = "https://identitytoolkit.googleapis.com/v1/accounts"
TABLE = "astroq-main"

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def call(method, path, token=None, body=None):
    """Trả (status, dict). Không bao giờ ném lỗi — cùng nguyên tắc với js/api.js."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode() or "{}"
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, {"_raw": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode() or "{}"
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw}
    except Exception as e:  # mất mạng / backend chưa bật
        return 0, {"_err": str(e)}


def idp(action, payload):
    req = urllib.request.Request(
        f"{IDP}:{action}?key={API_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print("Firebase REST loi:", e.read().decode()[:400])
        raise


def aws(*args):
    return subprocess.run(
        ["aws"] + list(args), capture_output=True, text=True, timeout=60
    )


def put_profile(uid, email):
    item = {
        "PK": {"S": f"USER#{uid}"},
        "SK": {"S": "PROFILE"},
        "uid": {"S": uid},
        "email": {"S": email},
        "name": {"S": "Test Onboarding"},
    }
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(item))
    return r.returncode == 0, r.stderr.strip()


def del_profile(uid):
    key = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"}}
    return aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps(key)).returncode == 0


def read_profile(uid):
    key = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"}}
    r = aws("dynamodb", "get-item", "--table-name", TABLE, "--key", json.dumps(key),
            "--consistent-read")
    if r.returncode != 0:
        return None
    return json.loads(r.stdout or "{}").get("Item")


def main():
    print(f"=== /me/onboarding @ {BASE} ===\n")

    st, d = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st} {d.get('service','')}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    # ---- 1. Chua co token ----
    print("\n[1] Khong co token")
    st, _ = call("GET", "/me/onboarding")
    check("GET khong token -> 401", st == 401, f"status={st}")
    st, _ = call("PUT", "/me/onboarding", body={"tourSeen": True})
    check("PUT khong token -> 401", st == 401, f"status={st}")

    print("\n[2] Token rac")
    st, _ = call("GET", "/me/onboarding", token="khong-phai-jwt")
    check("GET token rac -> 401", st == 401, f"status={st}")

    # ---- 3. Tài khoản Firebase tạm ----
    email = f"onboard-test-{uuid.uuid4().hex[:10]}@astroq-test.invalid"
    print(f"\n[3] Tao tai khoan Firebase tam: {email}")
    acc = idp("signUp", {"email": email, "password": "Test" + uuid.uuid4().hex[:8],
                         "returnSecureToken": True})
    uid, token = acc["localId"], acc["idToken"]
    check("Firebase cap idToken + uid", bool(uid and token), f"uid={uid}")

    try:
        # ---- 4. uid CHƯA có hồ sơ ----
        print("\n[4] uid chua co ho so trong DynamoDB")
        st, d = call("GET", "/me/onboarding", token=token)
        check("GET -> 200 va tourSeen=false", st == 200 and d.get("tourSeen") is False,
              f"status={st} data={d}")
        st, d = call("PUT", "/me/onboarding", token=token, body={"tourSeen": True})
        check("PUT -> 404 no-profile", st == 404 and d.get("code") == "no-profile",
              f"status={st} data={d}")
        check("PUT khong tao ra ho so rong", read_profile(uid) is None)

        # ---- 5. Có hồ sơ ----
        print("\n[5] Da co ho so")
        made, err = put_profile(uid, email)
        check("Tao ho so PROFILE bang aws CLI", made, err)

        st, d = call("GET", "/me/onboarding", token=token)
        check("GET ho so moi -> tourSeen=false", st == 200 and d.get("tourSeen") is False,
              f"status={st} data={d}")

        st, d = call("PUT", "/me/onboarding", token=token, body={"tourSeen": True})
        check("PUT true -> 200 tourSeen=true", st == 200 and d.get("tourSeen") is True,
              f"status={st} data={d}")
        check("PUT tra ve tourSeenAt", bool(d.get("tourSeenAt")), str(d.get("tourSeenAt")))

        item = read_profile(uid)
        check("DynamoDB co tourSeen=true (doc that)",
              bool(item) and item.get("tourSeen", {}).get("BOOL") is True,
              str(item.get("tourSeen") if item else None))
        check("DynamoDB giu nguyen email/name cua ho so",
              bool(item) and item.get("email", {}).get("S") == email
              and item.get("name", {}).get("S") == "Test Onboarding")

        st, d = call("GET", "/me/onboarding", token=token)
        check("GET sau PUT -> tourSeen=true", st == 200 and d.get("tourSeen") is True,
              f"data={d}")

        # PUT không có body → mặc định true (client chỉ cần gọi PUT rỗng)
        st, d = call("PUT", "/me/onboarding", token=token, body={})
        check("PUT body rong -> mac dinh true", st == 200 and d.get("tourSeen") is True,
              f"data={d}")

        st, d = call("PUT", "/me/onboarding", token=token, body={"tourSeen": False})
        check("PUT false -> tourSeen=false (de test lai duoc)",
              st == 200 and d.get("tourSeen") is False, f"data={d}")
        item = read_profile(uid)
        check("DynamoDB co tourSeen=false",
              bool(item) and item.get("tourSeen", {}).get("BOOL") is False)

        # ---- 6. Không đọc được dữ liệu người khác ----
        print("\n[6] Khong the doc/ghi ho so nguoi khac")
        st, d = call("GET", "/me/onboarding?uid=USER%23khac", token=token)
        check("Query string uid bi bo qua (uid lay tu token)",
              st == 200 and d.get("tourSeen") is False, f"data={d}")
        st, d = call("PUT", "/me/onboarding", token=token,
                     body={"tourSeen": True, "uid": "uid-nguoi-khac"})
        check("uid trong body bi bo qua", st == 200 and d.get("tourSeen") is True,
              f"data={d}")
        item = read_profile(uid)
        check("Chi ho so cua CHINH minh bi doi",
              bool(item) and item.get("tourSeen", {}).get("BOOL") is True)

        # ---- 6b. Cờ intro01Seen (màn mở đầu Nhiệm Vụ 01) ----
        # Hai cờ phải ĐỘC LẬP: xem màn nào thì chỉ ghi cờ màn đó. Gộp chung thì
        # xem cutscene nhiệm vụ sẽ xoá dấu "đã xem tour" và Comet dẫn lại từ đầu.
        print("\n[6b] Co intro01Seen — doc lap voi tourSeen")
        st, d = call("PUT", "/me/onboarding", token=token, body={"tourSeen": True})
        check("Dat tourSeen=true", d.get("tourSeen") is True, str(d))
        check("intro01Seen mac dinh false", d.get("intro01Seen") is False, str(d))

        st, d = call("PUT", "/me/onboarding", token=token, body={"intro01Seen": True})
        check("Ghi intro01Seen=true -> 200", st == 200 and d.get("intro01Seen") is True, f"{st} {d}")
        check("KHONG lam mat tourSeen", d.get("tourSeen") is True, str(d))
        check("Co intro01SeenAt", bool(d.get("intro01SeenAt")), str(d.get("intro01SeenAt")))

        st, d = call("GET", "/me/onboarding", token=token)
        check("GET tra ve ca 2 co", d.get("tourSeen") is True and d.get("intro01Seen") is True,
              str(d))

        st, d = call("PUT", "/me/onboarding", token=token, body={"tourSeen": False})
        check("Doi rieng tourSeen -> intro01Seen GIU NGUYEN",
              d.get("tourSeen") is False and d.get("intro01Seen") is True, str(d))

        st, d = call("PUT", "/me/onboarding", token=token, body={"intro01Seen": False})
        check("Doi rieng intro01Seen ve false", d.get("intro01Seen") is False, str(d))
        item = read_profile(uid)
        check("DynamoDB co intro01Seen (doc that)",
              bool(item) and "intro01Seen" in item, str(list(item or {})))

        st, d = call("PUT", "/me/onboarding", token=token,
                     body={"tourSeen": True, "intro01Seen": True})
        check("Gui ca 2 co mot luot -> ca 2 = true",
              d.get("tourSeen") is True and d.get("intro01Seen") is True, str(d))
        # Body rỗng vẫn phải giữ hành vi cũ (client trước đây gọi PUT rỗng)
        st, d = call("PUT", "/me/onboarding", token=token, body={})
        check("Body rong -> tourSeen=true, KHONG doi intro01Seen",
              d.get("tourSeen") is True and d.get("intro01Seen") is True, str(d))

        # ---- 7. Method khác ----
        print("\n[7] Method khong ho tro")
        st, _ = call("DELETE", "/me/onboarding", token=token)
        check("DELETE -> 404/405", st in (404, 405), f"status={st}")

    finally:
        print("\n[don] Xoa du lieu test")
        check("Xoa ho so DynamoDB", del_profile(uid))
        try:
            idp("delete", {"idToken": token})
            check("Xoa tai khoan Firebase tam", True)
        except Exception as e:
            check("Xoa tai khoan Firebase tam", False, str(e))
        check("Ho so da bien khoi DynamoDB", read_profile(uid) is None)

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
