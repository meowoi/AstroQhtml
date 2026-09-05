# -*- coding: utf-8 -*-
"""
test_wallet.py — kiểm thử ĐỘC LẬP ví Thiên thạch tím + chòm sao + chống trùng opId.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_wallet.py                 # http://localhost:5080
    python scratchpad/test_wallet.py <base-url>       # bản thật trên AWS

Trọng tâm — ba thứ dễ mất tiền nhất:
  1. PHÍ do server quyết: client gửi số tiền lên thì bị BỎ QUA hoàn toàn.
  2. Không bao giờ âm ví, không trừ được hai lần khi gọi song song.
  3. Gửi lại (mất mạng → hàng chờ) KHÔNG cộng/trừ lần hai — nhờ opId.

Tự tạo tài khoản Firebase tạm, tự dọn mọi bản ghi trong `finally`.
"""
import concurrent.futures as cf
import json
import re
import os
import io
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

import _fbtest  # token ĐÃ xác minh email — /me/* nay đòi email_verified

# ⚠️ TRAN THUONG QUIZ DOC TU `Wallet.cs`, KHONG GHIM SO. Ngay 15/08/2026 no doi
#    220 -> 60 (can doi ti le hoc/choi) va bo do nay bao hong DUNG LUC san pham lam
#    dung — lop loi "phep kiem bao ve trang thai cu" da lap nhieu lan trong du an.
_WAL = io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "..", "AstroqSV", "src", "AstroqSV.Api", "Services", "Wallet.cs"),
               encoding="utf-8").read()
MAX_QUIZ = int(re.search(r"MaxPerQuiz\s*=\s*(\d+)", _WAL).group(1))

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
API_KEY = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
IDP = "https://identitytoolkit.googleapis.com/v1/accounts"
TABLE = "astroq-main"

# Tran luot quiz moi ngay — DOC tu server, khong go tay: doi o `QuizAccess.cs`
# thi bo do tu dung theo. Tach bang split chu khong regex (chuoi thoat trong
# script va la mot cai bay da tra gia nhieu lan).
_qa = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                          "AstroqSV", "src", "AstroqSV.Api", "Services",
                          "QuizAccess.cs"), encoding="utf-8").read()
QUIZ_PER_DAY = int(_qa.split("FreeRoundsPerDay")[1].split("=")[1].split(";")[0].strip())

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
    except Exception as e:
        return 0, {"_err": str(e)}


def idp(action, payload):
    req = urllib.request.Request(f"{IDP}:{action}?key={API_KEY}",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def aws(*args):
    return subprocess.run(["aws"] + list(args), capture_output=True, text=True, timeout=60)


def seed(uid, email, meteors=None):
    items = [{
        "PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
        "uid": {"S": uid}, "email": {"S": email}, "name": {"S": "Wallet Test"},
        "createdAt": {"S": "2026-07-29T00:00:00.000Z"},
    }]
    if meteors is not None:
        items.append({"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
                      "meteors": {"N": str(meteors)}, "diamonds": {"N": "0"}})
    for it in items:
        r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(it))
        if r.returncode != 0:
            return False, r.stderr.strip()
    return True, ""


def rows(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": f"USER#{uid}"}}),
            "--consistent-read")
    return [] if r.returncode != 0 else json.loads(r.stdout or "{}").get("Items", [])


def wipe(uid):
    n = 0
    for it in rows(uid):
        if aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]})).returncode == 0:
            n += 1
    return n


def reset_quiz_day(uid, verify=True):
    """Tra bo dem luot quiz/ngay ve 0 (phan xoa o `_fbtest`, dung chung 3 bo do)."""
    gone = _fbtest.reset_quiz_day(uid, TABLE)
    if verify:
        left = [i for i in rows(uid) if i.get("SK", {}).get("S", "") in gone]
        check("da don het dong nhat ky quiz cua hom nay (%d dong)" % len(gone),
              len(left) == 0 and len(gone) > 0, "con %d dong" % len(left))
    return len(gone)


def bal(token):
    return call("GET", "/me/wallet", token=token)[1].get("meteors")


# ⚠️ Doc bang thuong viec hang ngay TU MA NGUON, khong gan cung: tu 12/08/2026
#    `POST /me/progress` cong ca thuong viec ngay, nen vi tang `awarded + dailyPaid`.
#    Gan cung 6/8/5 o day la mot qua min hen gio — doi bang viec la test do oan.
def daily_tts():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "AstroqSV", "src", "AstroqSV.Api", "Services", "Daily.cs")
    try:
        src = io.open(p, encoding="utf-8").read()
    except OSError:
        return None
    return [int(m.group(1)) for m in re.finditer(r'new\("[a-z]+",\s*\d+,\s*(\d+)\)', src)]


def legit_daily(paid, tts):
    """`paid` co phai mot TONG HOP LE cua bang thuong viec ngay khong (0 = khong tra)."""
    if paid == 0:
        return True
    if not tts:
        return paid > 0            # khong doc duoc bang thi chi doi "co tra mot khoan"
    ok = {0}
    for v in tts:
        ok |= {x + v for x in ok}
    return paid in ok


def main():
    print(f"=== Vi + chom sao + chong trung @ {BASE} ===\n")
    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    print("\n[1] Khong co token")
    for m, p in (("GET", "/me/wallet"), ("POST", "/me/wallet/spend")):
        st, _ = call(m, p, body={} if m == "POST" else None)
        check(f"{m} {p} -> 401", st == 401, f"status={st}")

    email = f"wallet-test-{uuid.uuid4().hex[:10]}@astroq-test.invalid"
    print(f"\n[2] Tao tai khoan tam: {email}")
    # ⚠️ TOKEN ĐÃ XÁC MINH EMAIL. /me/* nay đòi email_verified=true (chặn tự-đăng-ký);
    #    token từ signUp trơn mang email_verified=false nên sẽ 403. Xem scratchpad/_fbtest.py.
    uid, token, _pw = _fbtest.make_verified(email)
    # ⚠️ Nhom `/me` doi CO HO SO tu 05/09/2026 (`AccountGate.RequireProfile`).
    _fbtest.seed_profile(uid, email)
    check("Co idToken + uid", bool(uid and token), f"uid={uid}")

    try:
        print("\n[3] Chua co vi")
        ok, err = seed(uid, email)      # chỉ PROFILE, KHÔNG có WALLET
        check("Tao ho so (khong tao vi)", ok, err)
        check("GET /me/wallet -> 0 chu khong loi", bal(token) == 0, str(bal(token)))
        st, d = call("POST", "/me/wallet/spend", token=token,
                     body={"reason": "game", "game": "dodge"})
        check("Tru phi khi chua co vi -> 409 insufficient",
              st == 409 and d.get("code") == "insufficient", f"{st} {d}")
        check("Bao dung so tien can (5)", d.get("need") == 5, str(d.get("need")))
        check("Khong sinh ra vi am",
              not any(r["SK"]["S"] == "WALLET" for r in rows(uid)))

        print("\n[4] Phi do SERVER quyet — client gui so tien len thi bi bo qua")
        ok, err = seed(uid, email, meteors=100)
        check("Nap vi 100 tt", ok and bal(token) == 100, str(bal(token)))

        st, d = call("POST", "/me/wallet/spend", token=token,
                     body={"reason": "game", "game": "dodge", "amount": 0, "fee": 0,
                           "cost": 0, "meteors": 9999})
        check("Gui amount/fee/cost = 0 -> van tru dung 5",
              st == 200 and d.get("spent") == 5 and d.get("meteors") == 95, str(d))
        st, d = call("POST", "/me/wallet/spend", token=token,
                     body={"reason": "game", "game": "constellation"})
        check("Ghep Chom Sao tru 3 (khong phai 5)",
              d.get("spent") == 3 and d.get("meteors") == 92, str(d))
        st, d = call("POST", "/me/wallet/spend", token=token,
                     body={"reason": "game", "game": "khong-co-that"})
        check("Game khong co bang phi -> 400", st == 400 and d.get("code") == "bad-game",
              f"{st} {d}")
        st, d = call("POST", "/me/wallet/spend", token=token,
                     body={"reason": "mua-hang", "game": "dodge"})
        check("reason la -> 400", st == 400 and d.get("code") == "bad-reason", f"{st} {d}")
        check("Sau 2 lan tru hop le + 2 lan loi: vi con 92", bal(token) == 92, str(bal(token)))

        print("\n[5] Khong bao gio am vi")
        # tiêu cho gần hết
        for _ in range(18):
            call("POST", "/me/wallet/spend", token=token, body={"reason": "game", "game": "dodge"})
        b = bal(token)
        check(f"Con {b} tt (< 5)", b < 5, str(b))
        st, d = call("POST", "/me/wallet/spend", token=token,
                     body={"reason": "game", "game": "dodge"})
        check("Khong du -> 409, KHONG tru", st == 409 and bal(token) == b, f"{st} con {bal(token)}")
        check("So du khong am", bal(token) >= 0, str(bal(token)))

        print("\n[6] Goi SONG SONG khong tru duoc hai lan (dieu kien nguyen tu)")
        aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(
            {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
             "meteors": {"N": "5"}, "diamonds": {"N": "0"}}))
        check("Dat vi = 5 (du dung MOT luot)", bal(token) == 5, str(bal(token)))
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            futs = [ex.submit(call, "POST", "/me/wallet/spend", token,
                              {"reason": "game", "game": "dodge"}) for _ in range(6)]
            res = [f.result() for f in futs]
        got200 = [d for st_, d in res if st_ == 200 and d.get("spent") == 5]
        got409 = [d for st_, d in res if st_ == 409]
        check("Dung 1 loi goi thanh cong, 5 loi bi tu choi",
              len(got200) == 1 and len(got409) == 5,
              f"{len(got200)} thanh cong / {len(got409)} tu choi")
        check("Vi ve 0, khong am", bal(token) == 0, str(bal(token)))

        print("\n[7] opId — gui lai KHONG tru phi lan hai")
        aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(
            {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
             "meteors": {"N": "50"}, "diamonds": {"N": "0"}}))
        op = "op-" + uuid.uuid4().hex[:12]
        st, d1 = call("POST", "/me/wallet/spend", token=token,
                      body={"reason": "game", "game": "dodge", "opId": op})
        check("Lan 1: tru 5, con 45", d1.get("spent") == 5 and d1.get("meteors") == 45, str(d1))
        st, d2 = call("POST", "/me/wallet/spend", token=token,
                      body={"reason": "game", "game": "dodge", "opId": op})
        check("Gui lai CUNG opId: counted=false, KHONG tru them",
              d2.get("counted") is False and d2.get("duplicate") is True
              and d2.get("meteors") == 45, str(d2))
        check("Vi van 45", bal(token) == 45, str(bal(token)))
        st, d3 = call("POST", "/me/wallet/spend", token=token,
                      body={"reason": "game", "game": "dodge", "opId": op + "-khac"})
        check("opId KHAC thi tru binh thuong", d3.get("meteors") == 40, str(d3))

        print("\n[8] Thuong: server cong vi + KEP ve tran")
        b0 = bal(token)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 3, "total": 5, "meteors": 60})
        _dtts = daily_tts()
        _dp = d.get("dailyPaid", 0)
        check("Quiz 60 tt -> cong dung 60 (+ thuong viec ngay)",
              d.get("awarded") == 60 and d["wallet"]["meteors"] == b0 + 60 + _dp,
              f"awarded={d.get('awarded')} dailyPaid={_dp} {d.get('wallet')}")
        check("Phan cong THEM chi den tu bang viec ngay cua server",
              legit_daily(_dp, _dtts), f"dailyPaid={_dp} bang={_dtts}")
        b0 = d["wallet"]["meteors"]
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 5, "total": 5, "meteors": 999999})
        _dp = d.get("dailyPaid", 0)
        check(f"Quiz doi 999999 tt -> kep con {MAX_QUIZ} (tran quiz)",
              d.get("awarded") == MAX_QUIZ
              and d["wallet"]["meteors"] == b0 + MAX_QUIZ + _dp,
              f"awarded={d.get('awarded')} dailyPaid={_dp}")
        check("Phan cong THEM chi den tu bang viec ngay cua server (2)",
              legit_daily(_dp, _dtts), f"dailyPaid={_dp} bang={_dtts}")
        b0 = d["wallet"]["meteors"]
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "dodge", "score": 100, "meteors": 999})
        check("Game doi 999 tt -> kep con 60 (tran game)", d.get("awarded") == 60,
              f"awarded={d.get('awarded')}")
        # ─── LUAT MOI 30/07/2026: DOC BAI KHONG THUONG THIEN THACH TIM ───
        # Tran `Wallet.MaxPerLesson = 0`, nen client khai bao nhieu cung khong duoc
        # cong. Day la CHO CHAN THAT — bo phan cong o client thoi thi ai mo DevTools
        # cung gui duoc `{type:"lesson", meteors:9999}`.
        b0 = bal(token)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "lesson", "id": "bai-tran", "meteors": 999})
        check("Doc bai doi 999 tt -> KHONG duoc cong dong nao",
              d.get("awarded") == 0 and d["wallet"]["meteors"] == b0,
              f"awarded={d.get('awarded')} vi={d['wallet']['meteors']}")
        check("Doc bai VAN duoc ghi tien do (lessonsRead tang)",
              d["progress"]["lessonsRead"] >= 1, f"{d['progress']['lessonsRead']}")
        # `meteorsEarned` phai cong bang so THAT (0), khong phai so client khai (999)
        me_after = d["progress"]["meteorsEarned"]
        st, d2 = call("POST", "/me/progress", token=token,
                     body={"type": "lesson", "id": "bai-tran-2", "meteors": 999})
        check("Doc bai KHONG lam phong `meteorsEarned` (huy hieu khong mo bang tien ao)",
              d2["progress"]["meteorsEarned"] == me_after,
              f"{me_after} -> {d2['progress']['meteorsEarned']}")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "lesson", "id": "bai-tran", "meteors": 8})
        check("Doc lai bai cu -> counted=false va KHONG cong tien",
              d.get("counted") is False and d.get("awarded", 0) in (0, None), str(d.get("counted")))

        reset_quiz_day(uid)
        # ─── LUAT MOI: QUIZ PHAI DAT (>= 60%) MOI CO THUONG ───
        # Nguong nam o server (`Wallet.QuizPassRatio`), nen client gui `meteors` bao
        # nhieu cung vo nghia khi ti le dung chua toi.
        b0 = bal(token)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 1, "total": 5, "meteors": 200})
        check("Quiz 1/5 (20%) -> CHUA DAT, khong duoc dong nao",
              d.get("awarded") == 0 and d["wallet"]["meteors"] == b0 and d.get("quizPassed") is False,
              f"awarded={d.get('awarded')} passed={d.get('quizPassed')}")
        check("Quiz chua dat VAN duoc ghi bo dem + XP",
              d.get("xpGained", 0) > 0 and d["progress"]["quizTaken"] >= 1,
              f"xp={d.get('xpGained')}")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 2, "total": 5, "meteors": 200})
        check("Quiz 2/5 (40%) -> vua duoi nguong, van 0",
              d.get("awarded") == 0 and d.get("quizPassed") is False, f"awarded={d.get('awarded')}")
        b0 = d["wallet"]["meteors"]
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 3, "total": 5, "meteors": 60})
        check("Quiz 3/5 (60%) -> DUNG nguong, duoc cong 60",
              d.get("awarded") == 60 and d["wallet"]["meteors"] == b0 + 60
              and d.get("quizPassed") is True, f"awarded={d.get('awarded')}")
        check("Server tra ve nguong dat de client khoi tu tinh", d.get("quizPassMark") == 0.60,
              f"{d.get('quizPassMark')}")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 5, "total": 5, "meteors": 100})
        # Client doi 100 nhung tran la MAX_QUIZ -> lay so nho hon. Doi phat bieu chu
        # khong noi long: van doi server KEP, chi thoi ghim con so cu.
        check(f"Quiz 5/5 -> dat, cong dung min(100, {MAX_QUIZ})",
              d.get("awarded") == min(100, MAX_QUIZ), f"{d.get('awarded')}")
        # total=0 la du lieu rac -> phai 400, khong duoc chia cho 0
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 3, "total": 0, "meteors": 50})
        check("Quiz total=0 -> 400, khong chia cho 0", st == 400, f"{st}")

        # ─── DAY NOI SO TAY THUAT NGU (them 30/07/2026) ───
        # `terms` = khoa thuat ngu tra loi DUNG. Truoc do client khong gui truong nay
        # nen server khong biet tre dung thuat ngu nao va so tay khoa vinh vien.
        print("")
        print("[8b] terms - day noi So Tay Thuat Ngu")
        reset_quiz_day(uid)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 2, "total": 5, "meteors": 0,
                           "terms": ["star", "comet-tail"]})
        got = set(d["progress"].get("terms") or [])
        check("Ghi duoc 2 khoa thuat ngu", {"star", "comet-tail"} <= got, f"{sorted(got)}")
        check("terms tra ve trong snapshot", "terms" in d["progress"])
        check("termsDone dem dung", d["progress"].get("termsDone") == len(got),
              f"{d['progress'].get('termsDone')} vs {len(got)}")
        # ⚠️ Gui terms KE CA khi CHUA DAT: cong "dat" chi chi phoi THIEN THACH TIM.
        #    Tre dung mot thuat ngu la da hieu thuat ngu do.
        check("CHUA DAT (2/5) van giai ma duoc thuat ngu da tra loi dung",
              d.get("quizPassed") is False and "star" in got, f"passed={d.get('quizPassed')}")

        # ADD tren string set = phep HOP: gui lai khoa cu khong ghi trung
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 3, "total": 5, "meteors": 0,
                           "terms": ["star", "moon"]})
        got2 = set(d["progress"].get("terms") or [])
        check("Gui lai khoa cu -> khong ghi trung, chi them khoa moi",
              got2 == got | {"moon"}, f"{sorted(got2)}")

        # ⚠️ KEP theo so cau DUNG: 1 cau dung khong duoc mo ca so tay
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 1, "total": 5, "meteors": 0,
                           "terms": ["asteroid-what", "comet-what", "dwarf", "planet",
                                     "meteor", "meteorite", "exoplanet"]})
        got3 = set(d["progress"].get("terms") or [])
        check("1 cau dung -> chi nhan THEM 1 khoa, khong mo ca so tay",
              len(got3 - got2) == 1, f"them {len(got3 - got2)} khoa: {sorted(got3 - got2)}")

        # Khoa rac phai bi loc, khong lot vao string set
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 2, "total": 5, "meteors": 0,
                           "terms": ["  ", "khoa co dau cach", "qua-dai-" + "x" * 60]})
        got4 = set(d["progress"].get("terms") or [])
        check("Khoa rac bi loc het, khong ghi vao DB", got4 == got3, f"{sorted(got4 - got3)}")

        # type != quiz thi bo qua terms (doc bai khong giai ma thuat ngu)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "lesson", "id": "bai-terms", "terms": ["qubit"]})
        got5 = set(d["progress"].get("terms") or [])
        check("type=lesson thi BO QUA terms", "qubit" not in got5, f"{sorted(got5)}")

        reset_quiz_day(uid)
        # terms rong / null khong lam vo loi goi (SS cua DynamoDB khong nhan tap rong)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 3, "total": 5, "meteors": 0, "terms": []})
        check("terms rong -> 200, khong loi ValidationException", st == 200, f"{st}")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 3, "total": 5, "meteors": 0})
        check("thieu truong terms -> 200 (client cu khong vo)", st == 200, f"{st}")
        b1 = bal(token)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "dodge", "score": 1, "meteors": -50})
        check("tt am -> khong cong, khong tru", d.get("awarded") == 0 and bal(token) == b1,
              f"awarded={d.get('awarded')}")

        print("\n[9] opId cho /me/progress — gui lai khong cong tien lan hai")
        reset_quiz_day(uid)
        b2 = bal(token)
        op2 = "pg-" + uuid.uuid4().hex[:12]
        st, e1 = call("POST", "/me/progress", token=token,
                      body={"type": "quiz", "correct": 2, "total": 2, "meteors": 40, "opId": op2})
        check("Lan 1: cong 40", e1.get("awarded") == 40 and e1["wallet"]["meteors"] == b2 + 40,
              str(e1.get("wallet")))
        xp1 = e1["level"]["xp"]
        st, e2 = call("POST", "/me/progress", token=token,
                      body={"type": "quiz", "correct": 2, "total": 2, "meteors": 40, "opId": op2})
        check("Gui lai CUNG opId: counted=false, duplicate=true",
              e2.get("counted") is False and e2.get("duplicate") is True, str(e2.get("counted")))
        check("Vi KHONG cong lan hai", e2["wallet"]["meteors"] == b2 + 40,
              str(e2["wallet"]))
        check("XP KHONG cong lan hai", e2["level"]["xp"] == xp1,
              f"{xp1} -> {e2['level']['xp']}")
        check("Bo dem quiz KHONG tang lan hai",
              e2["progress"]["quizTaken"] == e1["progress"]["quizTaken"],
              f"{e1['progress']['quizTaken']} -> {e2['progress']['quizTaken']}")

        print("\n[10] Chom sao: ghi id + thoi gian NHANH NHAT")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "constellation", "id": "orion",
                           "seconds": 52, "score": 1, "meteors": 12})
        check("Ghep Lap Ho -> consts co orion",
              d["progress"]["consts"].get("orion") == 52, str(d["progress"]["consts"]))
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "constellation", "id": "orion",
                           "seconds": 34, "score": 1})
        check("Ghep lai nhanh hon (34s) -> ky luc cap nhat",
              d["progress"]["consts"]["orion"] == 34, str(d["progress"]["consts"]))
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "constellation", "id": "orion",
                           "seconds": 90, "score": 1})
        check("Ghep lai CHAM hon -> ky luc GIU NGUYEN 34",
              d["progress"]["consts"]["orion"] == 34, str(d["progress"]["consts"]))
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "constellation", "id": "ursa-major",
                           "seconds": 41, "score": 1})
        check("Chom khac -> 2 chom trong bo suu tap",
              d["progress"]["constsDone"] == 2 and set(d["progress"]["consts"]) ==
              {"orion", "ursa-major"}, str(d["progress"]["consts"]))
        check("Mo huy hieu constellation-1",
              any(b["id"] == "constellation-1" and b["earned"]
                  for b in call("GET", "/me/achievements", token=token)[1]
                  ["achievements"]["badges"]))
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "constellation", "id": "chom sao la!",
                           "seconds": 10, "score": 1})
        check("id chom sao co ky tu la -> bo qua, khong ghi rac",
              set(d["progress"]["consts"]) == {"orion", "ursa-major"},
              str(d["progress"]["consts"]))
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "dodge", "id": "orion", "score": 5})
        check("game khac gui id thi KHONG ghi vao consts",
              set(d["progress"]["consts"]) == {"orion", "ursa-major"},
              str(d["progress"]["consts"]))

        print("\n[11] Vi tra ve o moi route co lien quan")
        st, d = call("GET", "/me/profile", token=token)
        check("/me/profile co wallet.meteors", isinstance(d.get("wallet", {}).get("meteors"), int),
              str(d.get("wallet")))
        st, a = call("GET", "/me/achievements", token=token)
        check("/me/achievements co wallet.meteors",
              isinstance(a.get("wallet", {}).get("meteors"), int), str(a.get("wallet")))
        check("Ba route bao cung mot so du",
              d["wallet"]["meteors"] == a["wallet"]["meteors"] == bal(token),
              f"{d['wallet']['meteors']} / {a['wallet']['meteors']} / {bal(token)}")
        check("/me/profile va /me/achievements deu co consts",
              d["progress"]["constsDone"] == 2 and a["progress"]["constsDone"] == 2)

    finally:
        print("\n[don] Xoa du lieu test")
        n = wipe(uid)
        check("Xoa het ban ghi DynamoDB", n > 0, f"{n} dong")
        try:
            idp("delete", {"idToken": token})
            check("Xoa tai khoan Firebase tam", True)
        except Exception as e:
            check("Xoa tai khoan Firebase tam", False, str(e))
        check("Khong con ban ghi nao", len(rows(uid)) == 0)

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
