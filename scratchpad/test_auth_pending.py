# -*- coding: utf-8 -*-
"""
test_auth_pending.py — chốt chặn CHIẾM QUYỀN MỘT ĐĂNG KÝ CHƯA KÍCH HOẠT
(rà soát bảo mật 18/08/2026).

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_auth_pending.py                 # http://localhost:5080
    python scratchpad/test_auth_pending.py <base-url>      # bản thật trên AWS

ĐƯỜNG TẤN CÔNG ĐANG ĐO
──────────────────────
`/auth/register` trước đây ghi đè bản ghi PENDING vô điều kiện, gồm cả `pwdHash`. Ai
biết email của người khác chỉ cần đợi qua cooldown 60 giây rồi gọi lại `/register` với
MẬT KHẨU CỦA MÌNH: bản ghi chờ mang hash của hắn, token cũ chết, và nạn nhân bấm link
mới nhất trong hộp thư của CHÍNH MÌNH sẽ tạo ra một tài khoản mang mật khẩu kẻ tấn công.

Luật phải giữ: **người đăng ký ĐẦU TIÊN giữ mật khẩu cho tới khi link hết hạn.**

⚠️ ĐO BẰNG DẤU VẾT DynamoDB, KHÔNG ĐO BẰNG LỜI KHAI CỦA API. Cờ `passwordKept` trong
   response là thứ có thể đúng trong khi bản ghi vẫn bị ghi đè — mà bản ghi mới là thứ
   quyết định mật khẩu của tài khoản. Nên mọi mục cốt tử ở đây đều so `pwdHash`/`pwdSalt`
   đọc thẳng từ bảng.

⚠️ DÙNG ĐỊA CHỈ SES SIMULATOR (`success@simulator.amazonses.com`) — SES nhận và KHÔNG
   bounce, nên test không làm hại uy tín miền gửi. Cùng địa chỉ với `test_auth_cooldown.py`
   nên ĐỪNG chạy hai bộ cùng lúc.

⚠️ KHÔNG `sleep(61)` ĐỂ CHỜ HẾT COOLDOWN. Cooldown là 60 giây và bộ này cần vượt qua nó
   ba lần — ngồi chờ là 3 phút cho một phép kiểm chạy trong 5 giây. Thay vào đó lùi
   `lastSentAt` thẳng trong bảng, đúng thứ mà đồng hồ thật sẽ làm sau một phút.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"
EMAIL = "success@simulator.amazonses.com"   # SES nhận, không bounce

PW_FIRST  = "MatKhauCuaNguoiThat1"          # mật khẩu của người đăng ký ĐẦU
PW_ATTACK = "MatKhauCuaKeTanCong9"          # mật khẩu kẻ tấn công cố nhét vào
PW_LATER  = "MatKhauSauKhiHetHan5"          # dùng cho mục [5], bản ghi đã hết hạn

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


KEY = json.dumps({"PK": {"S": f"PENDING#{EMAIL}"}, "SK": {"S": "SIGNUP"}})


def row():
    r = aws("dynamodb", "get-item", "--table-name", TABLE, "--consistent-read", "--key", KEY)
    return None if r.returncode != 0 else json.loads(r.stdout or "{}").get("Item")


def wipe():
    aws("dynamodb", "delete-item", "--table-name", TABLE, "--key", KEY)


def creds(it):
    """Bộ ba quyết định mật khẩu của tài khoản sẽ ra đời."""
    if not it:
        return None
    return (it.get("pwdHash", {}).get("S"),
            it.get("pwdSalt", {}).get("S"),
            it.get("rounds", {}).get("N"))


def field(it, k, kind="S"):
    return None if not it else it.get(k, {}).get(kind)


def age_out(seconds_ago=120, expire=False):
    """
    Lùi `lastSentAt` để qua cooldown mà không phải ngồi chờ; `expire=True` thì lùi cả
    `expiresAt` để bản ghi thành ĐÃ HẾT HẠN.
    """
    it = row()
    if not it:
        return
    now = int(field(it, "lastSentAt", "N") or 0)
    upd = {":ls": {"N": str(max(0, now - seconds_ago))}}
    expr = "SET lastSentAt = :ls"
    if expire:
        expr += ", expiresAt = :ex"
        upd[":ex"] = {"N": str(int(field(it, "expiresAt", "N")) - 3600)}
    aws("dynamodb", "update-item", "--table-name", TABLE, "--key", KEY,
        "--update-expression", expr,
        "--expression-attribute-values", json.dumps(upd))


def register(name, pw):
    return call("POST", "/auth/register", {"name": name, "email": EMAIL, "password": pw})


def main():
    print(f"=== Chiem quyen dang ky chua kich hoat @ {BASE} ===\n")
    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    wipe()
    try:
        # ── [1] Nguoi that dang ky ────────────────────────────────────────────
        print("\n[1] Nguoi that dang ky lan dau")
        st, d = register("Nguoi That", PW_FIRST)
        check("register -> 202", st == 202, f"status={st}")
        check("KHONG passwordKept o lan dau", d.get("passwordKept") is not True,
              str(d.get("passwordKept")))
        check("resent = false (chua co ban ghi nao truoc do)", d.get("resent") is False,
              str(d.get("resent")))
        it1 = row()
        check("Da tao ban ghi PENDING", it1 is not None)
        c1, tok1 = creds(it1), field(it1, "tokenHash")
        check("Ban ghi co du pwdHash/pwdSalt/rounds", all(c1), str(c1 and c1[2]))
        check("Ten ghi dung", field(it1, "name") == "Nguoi That", str(field(it1, "name")))

        # ── [2] COT TU: ke tan cong dang ky de len, mat khau KHAC ─────────────
        print("\n[2] COT TU — ke tan cong dang ky de len bang mat khau KHAC")
        age_out()                       # qua cooldown, dung nhu sau 60 giay that
        st, d = register("Ke Tan Cong", PW_ATTACK)
        check("register -> 202 (van gui lai link cho nguoi that)", st == 202, f"status={st}")
        check("passwordKept = true (server NOI RA la da bo qua mat khau moi)",
              d.get("passwordKept") is True, str(d.get("passwordKept")))
        it2 = row()
        c2, tok2 = creds(it2), field(it2, "tokenHash")
        # Ba dong duoi day LA phep kiem. Ca ba deu do tren bang, khong do tren response.
        check("pwdHash KHONG doi  <<< chot chan chiem quyen",
              c1[0] == c2[0] and c1[0] is not None, "doi!" if c1[0] != c2[0] else "giu nguyen")
        check("pwdSalt KHONG doi", c1[1] == c2[1], "doi!" if c1[1] != c2[1] else "giu nguyen")
        check("rounds KHONG doi", c1[2] == c2[2], f"{c1[2]} vs {c2[2]}")
        check("TEN cung KHONG bi ghi de (ten di vao loi chao cua email)",
              field(it2, "name") == "Nguoi That", str(field(it2, "name")))
        # Nhung link thi VAN duoc cap lai — nguoi that bam Dang ky lai la vi chua thay email.
        check("tokenHash CO doi (van gui link moi cho nguoi that)",
              tok1 != tok2 and tok2 is not None, "giu nguyen!" if tok1 == tok2 else "da cap moi")
        check("expiresAt duoc gia han",
              int(field(it2, "expiresAt", "N")) >= int(field(it1, "expiresAt", "N")),
              f"{field(it1,'expiresAt','N')} -> {field(it2,'expiresAt','N')}")

        # ── [3] Nguoi that bam Dang ky lai bang DUNG mat khau cua minh ────────
        print("\n[3] Nguoi that dang ky lai bang DUNG mat khau cua minh")
        age_out()
        st, d = register("Nguoi That", PW_FIRST)
        check("register -> 202", st == 202, f"status={st}")
        check("passwordKept = false (nhan ra cung mot nguoi)",
              d.get("passwordKept") is False, str(d.get("passwordKept")))
        check("resent = true", d.get("resent") is True, str(d.get("resent")))
        it3 = row()
        check("pwdHash van la cua nguoi that", creds(it3)[0] == c1[0])
        check("tokenHash lai doi (link moi)", field(it3, "tokenHash") != tok2)

        # ── [4] Cooldown van con nguyen ───────────────────────────────────────
        print("\n[4] Bam lai NGAY -> cooldown chan, khong ghi gi")
        st, d = register("Ke Tan Cong", PW_ATTACK)
        check("register -> 202", st == 202, f"status={st}")
        check("throttled = true", d.get("throttled") is True, str(d.get("throttled")))
        check("passwordKept = true (nhanh throttled cung noi that)",
              d.get("passwordKept") is True, str(d.get("passwordKept")))
        it4 = row()
        check("tokenHash KHONG doi (khong cap token = khong gui email)",
              field(it4, "tokenHash") == field(it3, "tokenHash"))
        check("pwdHash KHONG doi", creds(it4)[0] == c1[0])

        # ── [5] Ban ghi HET HAN thi mat khau moi PHAI thang ───────────────────
        print("\n[5] Ban ghi HET HAN -> dang ky moi, mat khau moi THANG")
        age_out(expire=True)
        st, d = register("Nguoi Moi", PW_LATER)
        check("register -> 202", st == 202, f"status={st}")
        check("passwordKept = false (ban ghi cu da chet)",
              d.get("passwordKept") is False, str(d.get("passwordKept")))
        check("resent = false", d.get("resent") is False, str(d.get("resent")))
        it5 = row()
        # ⚠️ Muc nay quan trong ngang muc [2]: giu mat khau cu MAI MAI se bien mot lan
        #    go nham thanh mot dia chi bi khoa cho toi khi TTL don (hạn + 1 ngay).
        check("pwdHash DA DOI  <<< khong khoa cung dia chi sau mot lan go nham",
              creds(it5)[0] != c1[0] and creds(it5)[0] is not None,
              "van giu ban cu!" if creds(it5)[0] == c1[0] else "da nhan mat khau moi")
        check("TEN cung duoc cap nhat", field(it5, "name") == "Nguoi Moi",
              str(field(it5, "name")))

        # ── [6] Du lieu vao sai van bi chan truoc moi thu ─────────────────────
        print("\n[6] Kiem dau vao van chay truoc")
        st, d = call("POST", "/auth/register",
                     {"name": "x", "email": EMAIL, "password": "123"})
        check("mat khau ngan -> 400 weak-password",
              st == 400 and d.get("code") == "weak-password", f"{st} {d.get('code')}")
        it6 = row()
        check("ban ghi KHONG bi dung toi", field(it6, "tokenHash") == field(it5, "tokenHash"))

    finally:
        print("\n[don] Xoa ban ghi PENDING")
        wipe()
        check("Da xoa PENDING", row() is None)

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
