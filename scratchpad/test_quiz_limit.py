# -*- coding: utf-8 -*-
"""test_quiz_limit.py — HẠN MỨC 5 LƯỢT QUIZ/NGÀY: server có ÁP THẬT không.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_quiz_limit.py                # http://localhost:5080
    python scratchpad/test_quiz_limit.py --prod         # bản thật trên AWS

⚠️⚠️ VÌ SAO BỘ NÀY TỒN TẠI. Trang giá quảng cáo "3 lượt/ngày" cho bản miễn phí trong
   khi server **không giới hạn gì** — bản miễn phí thật ra chơi không hạn chế. Đây là
   lời-nói-không-khớp-hành-vi thứ HAI tìm ra ngày 19/08/2026 (cái đầu: 500 Purple
   Meteors hứa mà không cấp). Chủ dự án chốt: 5 lượt/ngày, chặn ở server.

⚠️⚠️ VÀ VÌ SAO BẢN CŨ 21/21 VẪN KHÔNG CHỨNG MINH ĐƯỢC GÌ. Nó chỉ bắn TUẦN TỰ, nên
   một chốt kiểu đọc-rồi-so-rồi-ghi vẫn xanh — mà đó chính là bản đã hỏng: đo được
   20/08/2026 **12 lượt SONG SONG ghi được 9 dòng trong khi trần là 5**. Mục [2b] là
   phép đo duy nhất phân biệt được hai bản. Ca tuần tự luôn xanh; ca song song mới là
   ca chết người. ⛔ Đừng bỏ nó đi vì 'đã có mục [3] chặn lượt thứ 6'.

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
    # ⚠️⚠️ CHI LAY `PK,SK`. Ban dau khong khai projection nen `aws` phai in ca truong
    #    `name` — va voi mot cai ten tieng Viet ("Tran Khanh Linh") thi CLI chet o
    #    cp1252: `'charmap' codec can't encode character '\u1ea7'`. Khi do phep dem
    #    duoi day tra [] va phan don in ra "da xoa 0 dong, con lai 0" — tuc BAO THANH
    #    CONG trong khi bon tai khoan test nam lai trong bang that (do duoc 19/08/2026).
    #    Dat PYTHONIOENCODING cho tien trinh con KHONG cuu duoc; bo truong do ra thi cuu.
    r = aws("dynamodb", "query", "--table-name", TABLE, "--consistent-read",
            "--key-condition-expression", "PK = :p",
            "--expression-attribute-values", json.dumps({":p": {"S": pk}}),
            # `type` la TU KHOA DU TRU cua DynamoDB nen phai di qua `#t`. Giu lai
            # truong nay vi phep kiem nhat ky dem theo no; con `name` (cho co dau
            # tieng Viet lam `aws` chet o cp1252) thi KHONG lay.
            "--projection-expression", "PK,SK,#t",
            "--expression-attribute-names", json.dumps({"#t": "type"}),
            "--output", "json")
    if r.returncode != 0:
        # ⚠️ NOI RA, dung tra [] cho xong. Mot phep do noi doi theo huong an tam la
        #    thu te nhat trong ca bo do.
        print("      ⚠️ TRUY VAN HONG cho %s: %s" % (pk, (r.stderr or "").strip()[:120]))
        raise RuntimeError("khong doc duoc bang de don du lieu test")
    if not r.stdout.strip():
        return []
    return json.loads(r.stdout).get("Items", [])


def day_vn():
    """Khoa ngay giờ VN (UTC+7) — đúng `Daily.DayKey` của server."""
    import datetime as dt
    return (dt.datetime.now(dt.timezone.utc)
            + dt.timedelta(hours=7)).strftime('%Y-%m-%d')


def counter(uid):
    """So suat quiz da dung — doc THANG tu ban ghi DAILY#, thu quyet dinh cong.

    ⚠️ KHONG di qua `rows()`: ham do CO Y chi lay `PK,SK,type` (bo `name` de `aws`
       CLI khong chet o cp1252), nen `quizRounds` khong bao gio ve va phep dem se
       LUON doc ra 0 — tuc mot phep kiem bao hong oan trong khi cong chay dung.
       Lay dung mot truong so nen khong co chu tieng Viet nao de ma chet.
    """
    r = aws("dynamodb", "get-item", "--table-name", TABLE, "--consistent-read",
            "--key", json.dumps({"PK": {"S": "USER#%s" % uid},
                                 "SK": {"S": "DAILY#" + day_vn()}}),
            "--projection-expression", "quizRounds", "--output", "json")
    if r.returncode != 0:
        raise RuntimeError("khong doc duoc bo dem: " + (r.stderr or "")[:120])
    it = (json.loads(r.stdout or "{}") or {}).get("Item") or {}
    return int(it.get("quizRounds", {}).get("N", 0))


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

    print("\n=== [2b] Bộ đếm trên bảng khớp số lượt đã chơi ===")
    check("`DAILY#<ngày>` có `quizRounds` = %d" % LIMIT, counter(uid) == LIMIT,
          "doc duoc %s" % counter(uid))

    print("\n=== [2c] GỌI SONG SONG — ca duy nhất phân biệt được cổng nguyên tử ===")
    # Don sach de bat dau lai tu 0 suat: xoa dong nhat ky VA bo dem.
    _fbtest.reset_quiz_day(uid, TABLE)
    check("da don sach bo dem truoc khi do", counter(uid) == 0, str(counter(uid)))

    # ⚠️ Ban N luot CUNG LUC. Chot doc-roi-so-roi-ghi se cho HON `LIMIT` cai thanh
    #    cong (do duoc 9/12 trong ban cu); chot bang phep ghi CO DIEU KIEN thi dung
    #    `LIMIT` cai. Day la phep do duy nhat trong ca bo phan biet duoc hai ban.
    import concurrent.futures as _cf
    N = LIMIT + 7
    with _cf.ThreadPoolExecutor(max_workers=N) as ex:
        res = list(ex.map(lambda _: quiz(tok), range(N)))
    okc = sum(1 for st, d in res if st == 200 and d.get("counted") is True)
    blk = sum(1 for st, d in res if st == 200 and d.get("reason") == "quiz-daily-limit")
    check("%d lời gọi song song → ĐÚNG %d lượt được tính" % (N, LIMIT),
          okc == LIMIT, "duoc tinh %d luot" % okc)
    check("%d lượt còn lại đều bị chặn với reason đúng" % (N - LIMIT),
          blk == N - LIMIT, "bi chan %d luot" % blk)
    check("bộ đếm trên bảng KHÔNG vượt trần", counter(uid) == LIMIT,
          "quizRounds = %s" % counter(uid))
    hp = [i for i in rows("USER#%s" % uid)
          if i.get("SK", {}).get("S", "").startswith("HIST#")
          and i.get("type", {}).get("S") == "quiz"]
    check("nhật ký có ĐÚNG %d dòng quiz (đây là con số bản cũ ghi 9)" % LIMIT,
          len(hp) == LIMIT, "%d dong" % len(hp))
    # Moi luot duoc tinh phai noi dung suat thu may CUA NO — khong duoc trung nhau.
    lefts = sorted(d.get("quizRoundsLeft") for st, d in res
                   if d.get("counted") is True)
    check("mỗi lượt được tính nói đúng suất của nó (%s)" % lefts,
          lefts == list(range(LIMIT)), str(lefts))

    print("\n=== [2d] Lời gọi RÁC không được tiêu mất một suất ===")
    _fbtest.reset_quiz_day(uid, TABLE)
    st, d = call("POST", "/me/progress", token=tok,
                 body={"type": "quiz", "correct": 0, "total": 0, "meteors": 0,
                       "opId": str(uuid.uuid4())})
    check("`total = 0` trả 400 (không phải 200 counted:false)", st == 400, str(st))
    check("và KHÔNG tiêu suất nào — bộ đếm vẫn 0", counter(uid) == 0,
          "quizRounds = %s" % counter(uid))

    # Bo dem ve 0 roi choi lai du LIMIT luot de cac muc sau chay dung nhu cu.
    for _ in range(LIMIT):
        quiz(tok)
    st, d = call("GET", "/me/profile", token=tok)
    answered_at_limit = ((d or {}).get("progress") or {}).get("quizAnswered")
    _st, _w = call("GET", "/me/wallet", token=tok)
    bal_at_limit = (_w or {}).get("meteors")
    quiz_taken_now = ((d or {}).get("progress") or {}).get("quizTaken")
    check("bộ đếm lại đầy sau %d lượt" % LIMIT, counter(uid) == LIMIT,
          str(counter(uid)))
    # ⚠️ Moc so dong NHAT KY phai doc lai o day, KHONG dung `quizTaken`: bo dem do
    #    la TONG CA DOI (15 luc nay) con nhat ky vua bi `reset_quiz_day` xoa bot.
    hist_now = len([i for i in rows("USER#%s" % uid)
                    if i.get("SK", {}).get("S", "").startswith("HIST#")
                    and i.get("type", {}).get("S") == "quiz"])

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
    check("`quizTaken` KHÔNG tăng", pr2.get("quizTaken") == quiz_taken_now,
          "%s -> %s" % (quiz_taken_now, pr2.get("quizTaken")))
    check("`quizAnswered` KHÔNG tăng", pr2.get("quizAnswered") == answered_at_limit,
          "%s -> %s" % (answered_at_limit, pr2.get("quizAnswered")))
    _st, _w = call("GET", "/me/wallet", token=tok)
    check("ví KHÔNG tăng", (_w or {}).get("meteors") == bal_at_limit,
          "%s -> %s" % (bal_at_limit, (_w or {}).get("meteors")))
    # Nhật ký: đúng LIMIT dòng quiz, không phải LIMIT+1.
    hist = [i for i in rows("USER#%s" % uid)
            if i.get("SK", {}).get("S", "").startswith("HIST#")
            and i.get("type", {}).get("S") == "quiz"]
    check("nhật ký KHÔNG có thêm dòng quiz nào (lượt bị chặn không ghi)",
          len(hist) == hist_now, "%d -> %d dòng" % (hist_now, len(hist)))

    print("\n=== [5] Gửi thêm 3 lượt nữa: vẫn chặn, vẫn không đổi gì ===")
    for i in range(3):
        st, d = quiz(tok)
        if d.get("counted") is not False:
            check("lượt thừa %d vẫn bị chặn" % (i + 1), False, str(d.get("counted")))
            break
    else:
        check("3 lượt thừa nữa đều bị chặn", True)
    st, d = call("GET", "/me/profile", token=tok)
    check("bộ đếm vẫn dừng ở %s" % quiz_taken_now,
          ((d or {}).get("progress") or {}).get("quizTaken") == quiz_taken_now,
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
    # `rows()` da lay het moi SK cua USER#<uid>, ke ca DAILY# — nen bo dem cung
    # bien theo. Kiem lai bang chinh phep dem duoi day.
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
