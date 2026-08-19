# -*- coding: utf-8 -*-
"""test_quiz_limit.py — HẠN MỨC 5 LƯỢT QUIZ/NGÀY: server có ÁP THẬT không.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_quiz_limit.py                # http://localhost:5080
    python scratchpad/test_quiz_limit.py --prod         # bản thật trên AWS

⚠️⚠️ VÌ SAO BỘ NÀY TỒN TẠI. Trang giá quảng cáo "3 lượt/ngày" cho bản miễn phí trong
   khi server **không giới hạn gì** — bản miễn phí thật ra chơi không hạn chế. Đây là
   lời-nói-không-khớp-hành-vi thứ HAI tìm ra ngày 19/08/2026 (cái đầu: 500 Purple
   Meteors hứa mà không cấp). Chủ dự án chốt: 5 lượt/ngày, chặn ở server.

⚠️ ĐO BẰNG SỐ DƯ VÀ BỘ ĐẾM, KHÔNG BẰNG LỜI KHAI. Cờ `counted` có thể đúng trong khi
   `quizAnswered` vẫn tăng — mà bộ đếm mới là thứ quyết huy hiệu và cấp độ.

⚠️ Tự dọn: xoá mọi dòng DynamoDB + tài khoản Firebase tạm trong `finally`.
"""
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, "scratchpad")
import _fbtest

PROD = "--prod" in sys.argv
BASE = ("https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com" if PROD
        else "http://localhost:5080")
TABLE = "astroq-main"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True)


def rows(pk):
    r = aws("dynamodb", "query", "--table-name", TABLE, "--consistent-read",
            "--key-condition-expression", "PK = :p",
            "--expression-attribute-values", json.dumps({":p": {"S": pk}}),
            "--output", "json")
    if r.returncode != 0 or not r.stdout.strip():
        return []
    return json.loads(r.stdout).get("Items", [])


def quiz(tok, correct=5, total=5):
    return call("POST", "/me/progress", token=tok,
                body={"type": "quiz", "correct": correct, "total": total,
                      "meteors": 0, "opId": str(uuid.uuid4())})


uid = tok = None
email = "quizlim-test-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
try:
    print("\n=== [0] Hằng số server ===")
    qp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "..", "AstroqSV", "src", "AstroqSV.Api", "Services", "QuizAccess.cs")
    m = re.search(r"FreeRoundsPerDay\s*=\s*(\d+)", io.open(qp, encoding="utf-8").read())
    check("đọc được FreeRoundsPerDay", bool(m), str(m and m.group(1)))
    LIMIT = int(m.group(1)) if m else 5
    check("hạn mức là 5 (chủ dự án chốt 19/08/2026)", LIMIT == 5, str(LIMIT))

    st, h = call("GET", "/health")
    check("/health 200", st == 200, json.dumps(h)[:60])

    uid, tok, _pw = _fbtest.make_verified(email)
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item",
            json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": {"S": "PROFILE"},
                        "uid": {"S": uid}, "email": {"S": email},
                        "name": {"S": "Test Pilot"},
                        "createdAt": {"S": "2026-08-19T00:00:00.000Z"}}))
    check("dựng được tài khoản test", r.returncode == 0, r.stderr.strip()[:70])

    print("\n=== [1] Trước khi chơi: /me/daily nói còn đủ %d lượt ===" % LIMIT)
    st, d = call("GET", "/me/daily", token=tok)
    check("/me/daily 200", st == 200, str(st))
    check("trả `quizRoundsPerDay` = %d" % LIMIT, d.get("quizRoundsPerDay") == LIMIT,
          str(d.get("quizRoundsPerDay")))
    check("trả `quizRoundsLeft` = %d (chưa chơi gì)" % LIMIT,
          d.get("quizRoundsLeft") == LIMIT, str(d.get("quizRoundsLeft")))

    print("\n=== [2] Năm lượt đầu: ĐƯỢC tính, và đếm ngược đúng ===")
    for i in range(1, LIMIT + 1):
        st, d = call("POST", "/me/progress", token=tok,
                     body={"type": "quiz", "correct": 5, "total": 5, "meteors": 0,
                           "opId": str(uuid.uuid4())})
        left = d.get("quizRoundsLeft")
        want = LIMIT - i
        check("lượt %d: counted=true, còn lại %d" % (i, want),
              st == 200 and d.get("counted") is True and left == want,
              "st=%s counted=%s left=%s" % (st, d.get("counted"), left))

    st, d = call("GET", "/me/profile", token=tok)
    pr = (d or {}).get("progress") or {}
    check("server đếm đúng %d lượt (quizTaken)" % LIMIT,
          pr.get("quizTaken") == LIMIT, str(pr.get("quizTaken")))
    answered_at_limit = pr.get("quizAnswered")
    bal_at_limit = ((d or {}).get("wallet") or {}).get("meteors")
    if bal_at_limit is None:
        _st, _w = call("GET", "/me/wallet", token=tok)
        bal_at_limit = (_w or {}).get("meteors")
    print("      sau %d lượt: đã trả lời %s câu, ví %s tt"
          % (LIMIT, answered_at_limit, bal_at_limit))

    print("\n=== [3] Lượt thứ %d: BỊ CHẶN ===" % (LIMIT + 1))
    st, d = quiz(tok)
    check("vẫn trả 200 (không phải 4xx — hàng chờ không được thử lại mãi)", st == 200,
          str(st))
    check("counted=false", d.get("counted") is False, str(d.get("counted")))
    check("reason='quiz-daily-limit' (nói rõ chuyện gì, không đọc như lỗi mạng)",
          d.get("reason") == "quiz-daily-limit", str(d.get("reason")))
    check("quizRoundsLeft=0", d.get("quizRoundsLeft") == 0, str(d.get("quizRoundsLeft")))
    check("awarded=0 và xpGained=0",
          d.get("awarded") == 0 and d.get("xpGained") == 0,
          "awarded=%s xp=%s" % (d.get("awarded"), d.get("xpGained")))

    print("\n=== [4] Lượt bị chặn KHÔNG được để lại dấu vết nào ===")
    st, d = call("GET", "/me/profile", token=tok)
    pr2 = (d or {}).get("progress") or {}
    check("`quizTaken` KHÔNG tăng", pr2.get("quizTaken") == LIMIT,
          "%s -> %s" % (LIMIT, pr2.get("quizTaken")))
    check("`quizAnswered` KHÔNG tăng", pr2.get("quizAnswered") == answered_at_limit,
          "%s -> %s" % (answered_at_limit, pr2.get("quizAnswered")))
    _st, _w = call("GET", "/me/wallet", token=tok)
    check("ví KHÔNG tăng", (_w or {}).get("meteors") == bal_at_limit,
          "%s -> %s" % (bal_at_limit, (_w or {}).get("meteors")))
    # Nhật ký: đúng LIMIT dòng quiz, không phải LIMIT+1.
    hist = [i for i in rows("USER#%s" % uid)
            if i.get("SK", {}).get("S", "").startswith("HIST#")
            and i.get("type", {}).get("S") == "quiz"]
    check("nhật ký có ĐÚNG %d dòng quiz (lượt bị chặn không ghi)" % LIMIT,
          len(hist) == LIMIT, "%d dòng" % len(hist))

    print("\n=== [5] Gửi thêm 3 lượt nữa: vẫn chặn, vẫn không đổi gì ===")
    for i in range(3):
        st, d = quiz(tok)
        if d.get("counted") is not False:
            check("lượt thừa %d vẫn bị chặn" % (i + 1), False, str(d.get("counted")))
            break
    else:
        check("3 lượt thừa nữa đều bị chặn", True)
    st, d = call("GET", "/me/profile", token=tok)
    check("bộ đếm vẫn dừng ở %d" % LIMIT,
          ((d or {}).get("progress") or {}).get("quizTaken") == LIMIT,
          str(((d or {}).get("progress") or {}).get("quizTaken")))

    print("\n=== [6] Hạn mức KHÔNG chặn các loại việc khác ===")
    st, d = call("POST", "/me/progress", token=tok,
                 body={"type": "game", "game": "dodge", "score": 10, "seconds": 30,
                       "meteors": 0, "opId": str(uuid.uuid4())})
    check("nộp lượt game vẫn được tính", st == 200 and d.get("counted") is True,
          "st=%s counted=%s" % (st, d.get("counted")))
    check("phản hồi việc game KHÔNG mang `quizRoundsLeft` (null)",
          d.get("quizRoundsLeft") is None, str(d.get("quizRoundsLeft")))

    print("\n=== [7] /me/daily nói còn 0 lượt ===")
    st, d = call("GET", "/me/daily", token=tok)
    check("`quizRoundsLeft` = 0", d.get("quizRoundsLeft") == 0,
          str(d.get("quizRoundsLeft")))

finally:
    print("\n=== [8] Dọn dữ liệu test ===")
    n = 0
    if uid:
        for it in rows("USER#%s" % uid):
            aws("dynamodb", "delete-item", "--table-name", TABLE,
                "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
            n += 1
    for pk in ("EMAIL#%s" % email, "PENDING#%s" % email):
        for it in rows(pk):
            aws("dynamodb", "delete-item", "--table-name", TABLE,
                "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
            n += 1
    left = len(rows("USER#%s" % uid)) if uid else 0
    print("      đã xoá %d dòng, còn lại %d" % (n, left))
    try:
        if tok:
            _fbtest.delete(tok)
            print("      đã xoá tài khoản Firebase tạm")
    except Exception as e:
        print("      ⚠️ chưa xoá được tài khoản tạm: %s" % str(e)[:60])

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
