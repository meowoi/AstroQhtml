# -*- coding: utf-8 -*-
"""
_fbtest.py — helper dùng chung cho các test API cần TOKEN ĐÃ XÁC MINH EMAIL.

Vì sao cần (01/08/2026): nhóm route `/me/*` giờ đòi `email_verified == true`
(Program.cs → policy "verified"), để chặn tài khoản tự-đăng-ký bằng apiKey công khai.
Token lấy từ `accounts:signUp` mang `email_verified=false` nên **bị 403** — mọi test
chạm `/me/*` phải mint token đã xác minh.

Không thể xác minh email bằng apiKey công khai (đó là trường ĐẶC QUYỀN). Nên helper
này lấy SERVICE ACCOUNT của project từ AWS Secrets Manager (máy chạy test có quyền
admin), đổi lấy OAuth access token, rồi gọi `accounts:update` để đặt
`emailVerified=true` — đúng thứ `FirebaseService.ImportVerifiedUserAsync` làm ở luồng
thật. Sau đó đăng nhập LẠI để có token mới mang cờ đã xác minh.

    from _fbtest import make_verified, web_signup, delete
    uid, token, pw = make_verified(email)      # token ĐÃ xác minh → dùng cho /me/*
    uid2, tok_unverified = web_signup(email2)  # token CHƯA xác minh → để thử 403
"""
import json
import subprocess
import urllib.request
import uuid

# apiKey Web — công khai theo thiết kế (xem js/firebase-config.js)
API_KEY = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
IDP = "https://identitytoolkit.googleapis.com/v1/accounts"
SECRET_ID = "astroq/firebase-service-account"


def _post(url, payload, bearer=None):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if bearer:
        req.add_header("Authorization", "Bearer " + bearer)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _idp(action, payload):
    return _post(f"{IDP}:{action}?key={API_KEY}", payload)


# ── phần công khai: signUp / signIn / delete bằng apiKey ──

def web_signup(email, pw=None):
    """Tạo tài khoản qua REST công khai → (uid, idToken CHƯA xác minh)."""
    pw = pw or "Test" + uuid.uuid4().hex[:10]
    d = _idp("signUp", {"email": email, "password": pw, "returnSecureToken": True})
    return d["localId"], d["idToken"], pw


def signin(email, pw):
    d = _idp("signInWithPassword",
             {"email": email, "password": pw, "returnSecureToken": True})
    return d["idToken"]


def delete(id_token):
    try:
        _idp("delete", {"idToken": id_token})
        return True
    except Exception:
        return False


# ── phần đặc quyền: service account → đặt emailVerified ──

_cred = None


def _access_token():
    """OAuth access token của service account (lấy từ Secrets Manager, cache lại)."""
    global _cred
    if _cred is None:
        raw = subprocess.run(
            ["aws", "secretsmanager", "get-secret-value",
             "--secret-id", SECRET_ID, "--query", "SecretString", "--output", "text"],
            capture_output=True, text=True, timeout=60)
        if raw.returncode != 0:
            raise RuntimeError("Khong doc duoc service account: " + raw.stderr.strip())
        from google.oauth2 import service_account
        _cred = service_account.Credentials.from_service_account_info(
            json.loads(raw.stdout),
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
    from google.auth.transport.requests import Request
    _cred.refresh(Request())
    return _cred.token


def mark_verified(local_id):
    """Đặt emailVerified=true cho một uid (đặc quyền — cần service account)."""
    _post(f"{IDP}:update",
          {"localId": local_id, "emailVerified": True},
          bearer=_access_token())


def make_verified(email, pw=None):
    """
    signUp → đặt emailVerified=true → đăng nhập LẠI để có token mang cờ đã xác minh.
    Trả (uid, idToken ĐÃ xác minh, password).
    """
    uid, _, pw = web_signup(email, pw)
    mark_verified(uid)
    token = signin(email, pw)   # token mới phản ánh emailVerified=true
    return uid, token, pw
