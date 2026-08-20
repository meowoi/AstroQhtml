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


def reset_quiz_day(uid, table="astroq-main", hours=48):
    """Xoa dong nhat ky quiz gan day cua `uid`, tra ve danh sach SK da xoa.

    VI SAO CAN: `QuizAccess.FreeRoundsPerDay` chan 5 luot quiz moi ngay mot tai
    khoan. Nhieu bo do co y ban nhieu luot hon the de di het cac nhanh khac
    (cong "dat", tran thuong, `terms`, cap do thich ung), nen phai tra bo dem ve
    0 giua cac nhom — dung thu xay ra khi sang ngay moi. Cung khuon
    `test_auth_pending` (lui `lastSentAt` thang trong bang thay vi sleep 61s).

    CHI xoa dong trong `hours` gio gan nhat. Xoa bua la an luon nhung dong nhat
    ky cua tuan truoc ma bo do co y gieo (`test_report` muc [5]) — mot ham don
    dep khong duoc pha du lieu cua phep kiem khac. Server dem luot theo NGAY
    VIET NAM (`Daily.DayRange`) nen cua so trai qua hai ngay UTC.

    ⚠️⚠️ TU 20/08/2026 XOA DONG NHAT KY THOI LA KHONG DU. Chot han muc nay la BO
    DEM `quizRounds` tren ban ghi `DAILY#<ngay>` (phep ghi co dieu kien, xem
    `DynamoContext.TryClaimQuizRoundAsync`) — xoa nhat ky ma khong xoa bo dem thi
    luot thu 6 van bi chan, va moi phep kiem phia sau bao hong mot cach BI AN.

    KHONG xoa ca ban ghi `DAILY#<ngay>`: string set `paid` o do la chot chong tra
    thuong viec hang ngay HAI LAN. Xoa no la bo do tu tao ra tien.

    Nguoi goi PHAI tu khang dinh ket qua (`len(...) > 0` va doc lai bang) — mot
    ham reset hong am tham se lam moi phep kiem phia sau "dat" mot cach RONG.
    """
    import datetime as _dt
    cut = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=hours)).isoformat()
    q = subprocess.run(
        ["aws", "dynamodb", "query", "--table-name", table,
         "--key-condition-expression", "PK = :p",
         "--expression-attribute-values",
         json.dumps({":p": {"S": "USER#" + uid}}),
         "--output", "json"],
        capture_output=True, text=True, timeout=60)
    if q.returncode != 0:
        return []
    done = []
    for it in (json.loads(q.stdout or "{}").get("Items") or []):
        sk = it.get("SK", {}).get("S", "")
        if not sk.startswith("HIST#") or it.get("type", {}).get("S") != "quiz":
            continue
        stamp = sk.split("#")[1] if sk.count("#") >= 1 else ""
        if stamp < cut[:len(stamp)]:
            continue
        r = subprocess.run(
            ["aws", "dynamodb", "delete-item", "--table-name", table,
             "--key", json.dumps({"PK": {"S": "USER#" + uid}, "SK": {"S": sk}})],
            capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            done.append(sk)

    # ── Bo dem suat quiz cua ngay ──
    # ⚠️ CHI xoa THUOC TINH `quizRounds`, KHONG xoa ban ghi: `paid` o do la chot
    #    chong tra thuong viec hang ngay HAI LAN, xoa no la bo do tu tao ra tien.
    # ⚠️ Khoa ngay la NGAY VIET NAM (UTC+7) — dung ngay UTC thi ngay dau tien cua
    #    cua so bi bo qua trong 7 gio moi ngay, va loi do chi hien ra theo gio.
    vn = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=7)
    days = int(hours // 24) + 2
    for k in range(days):
        day = (vn - _dt.timedelta(days=k)).strftime('%Y-%m-%d')
        r = subprocess.run(
            ['aws', 'dynamodb', 'update-item', '--table-name', table,
             '--key', json.dumps({'PK': {'S': 'USER#' + uid},
                                  'SK': {'S': 'DAILY#' + day}}),
             '--update-expression', 'REMOVE quizRounds',
             '--condition-expression', 'attribute_exists(quizRounds)'],
            capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            done.append('DAILY#' + day + '/quizRounds')
    return done
