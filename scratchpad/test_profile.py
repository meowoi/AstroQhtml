# -*- coding: utf-8 -*-
"""
test_profile.py — kiểm thử ĐỘC LẬP /me/profile, /me/achievements, /me/progress.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_profile.py                 # http://localhost:5080
    python scratchpad/test_profile.py <base-url>       # bản thật trên AWS

Tự tạo tài khoản Firebase tạm để có ID token thật, tự tạo/xoá mọi bản ghi
DynamoDB của mình (kể cả PROGRESS và các dòng READ#), dọn sạch trong `finally`.

Trọng tâm: SERVER phải là nơi quyết XP/huy hiệu. Có kịch bản client cố gửi
xp/badges lên, gửi số âm, gửi điểm vô lý, đọc lại một bài để farm XP.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

import _fbtest  # token ĐÃ xác minh email — /me/* nay đòi email_verified

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
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
    req = urllib.request.Request(
        f"{IDP}:{action}?key={API_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def aws(*args):
    return subprocess.run(["aws"] + list(args), capture_output=True, text=True, timeout=60)


def put_profile(uid, email, name="Test Pilot"):
    item = {
        "PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
        "uid": {"S": uid}, "email": {"S": email}, "name": {"S": name},
        "createdAt": {"S": "2026-07-29T00:00:00.000Z"},
    }
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(item))
    return r.returncode == 0, r.stderr.strip()


def rows(uid):
    """Mọi bản ghi của uid — dùng cả để kiểm và để dọn."""
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": f"USER#{uid}"}}),
            "--consistent-read")
    if r.returncode != 0:
        return []
    return json.loads(r.stdout or "{}").get("Items", [])


def wipe(uid):
    n = 0
    for it in rows(uid):
        key = {"PK": it["PK"], "SK": it["SK"]}
        if aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps(key)).returncode == 0:
            n += 1
    return n


def main():
    print(f"=== /me/profile · /me/achievements · /me/progress @ {BASE} ===\n")

    st, d = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    print("\n[1] Khong co token / token rac")
    for m, p in (("GET", "/me/profile"), ("PUT", "/me/profile"),
                 ("GET", "/me/achievements"), ("POST", "/me/progress")):
        st, _ = call(m, p, body={} if m != "GET" else None)
        check(f"{m} {p} khong token -> 401", st == 401, f"status={st}")
    st, _ = call("GET", "/me/profile", token="khong-phai-jwt")
    check("GET /me/profile token rac -> 401", st == 401, f"status={st}")

    email = f"profile-test-{uuid.uuid4().hex[:10]}@astroq-test.invalid"
    print(f"\n[2] Tao tai khoan Firebase tam: {email}")
    # ⚠️ TOKEN ĐÃ XÁC MINH EMAIL. /me/* nay đòi email_verified=true (chặn tự-đăng-ký);
    #    token từ signUp trơn mang email_verified=false nên sẽ 403. Xem scratchpad/_fbtest.py.
    uid, token, _pw = _fbtest.make_verified(email)
    check("Firebase cap idToken + uid", bool(uid and token), f"uid={uid}")

    try:
        print("\n[3] Chua co ho so")
        st, d = call("GET", "/me/profile", token=token)
        check("GET /me/profile -> 404 no-profile",
              st == 404 and d.get("code") == "no-profile", f"status={st} data={d}")
        st, d = call("PUT", "/me/profile", token=token, body={"name": "X"})
        check("PUT /me/profile -> 404 no-profile",
              st == 404 and d.get("code") == "no-profile", f"status={st} data={d}")
        check("Khong tao ra ban ghi nao", len(rows(uid)) == 0)

        made, err = put_profile(uid, email)
        check("Tao ho so PROFILE bang aws CLI", made, err)

        print("\n[4] Ho so moi — moi thu bang 0")
        st, d = call("GET", "/me/profile", token=token)
        pr, lv, pg = d.get("profile", {}), d.get("level", {}), d.get("progress", {})
        check("GET tra 200", st == 200, f"status={st}")
        check("Cap 1, XP 0", lv.get("level") == 1 and lv.get("xp") == 0, str(lv))
        check("Moc len cap 2 la 100 XP", lv.get("xpForNext") == 100, str(lv.get("xpForNext")))
        check("Bo dem deu 0",
              all(pg.get(k) == 0 for k in ("quizTaken", "quizCorrect", "gamesPlayed",
                                           "lessonsRead", "meteorsEarned")), str(pg))
        check("Ten + email dung", pr.get("name") == "Test Pilot" and pr.get("email") == email,
              str(pr))
        st, d = call("GET", "/me/achievements", token=token)
        ach = d.get("achievements", {})
        check("Kho thanh tich: 0 huy hieu tren tong so",
              ach.get("summary", {}).get("earned") == 0
              and ach.get("summary", {}).get("total", 0) >= 20, str(ach.get("summary")))
        check("Moi huy hieu deu co goal + current + group",
              all({"id", "goal", "current", "earned", "group"} <= set(b)
                  for b in ach.get("badges", [])),
              f"{len(ach.get('badges', []))} huy hieu")

        print("\n[5] Sua ho so (ten + trang phuc)")
        st, d = call("PUT", "/me/profile", token=token,
                     body={"name": "Bi Bo", "character": "cu", "avatar": "ava/avacu.png"})
        check("PUT hop le -> 200", st == 200, f"status={st} {d}")
        check("Doi duoc ten + nhan vat + avatar",
              d.get("profile", {}).get("name") == "Bi Bo"
              and d.get("profile", {}).get("character") == "cu"
              and d.get("profile", {}).get("avatar") == "ava/avacu.png", str(d.get("profile")))
        st, d = call("PUT", "/me/profile", token=token, body={"name": " "})
        check("Ten rong -> 400", st == 400 and d.get("code") == "name-empty", f"{st} {d}")
        st, d = call("PUT", "/me/profile", token=token, body={"name": "x" * 25})
        check("Ten 25 ky tu -> 400", st == 400 and d.get("code") == "name-too-long", f"{st} {d}")
        st, d = call("PUT", "/me/profile", token=token,
                     body={"avatar": "https://ke-khac.example/anh.png"})
        check("Avatar tro ra ten mien khac -> 400",
              st == 400 and d.get("code") == "bad-avatar", f"{st} {d}")
        st, d = call("PUT", "/me/profile", token=token, body={"avatar": "../../etc/passwd"})
        check("Avatar duong dan la -> 400", st == 400 and d.get("code") == "bad-avatar", f"{st} {d}")
        st, d = call("PUT", "/me/profile", token=token, body={"character": "a b/c"})
        check("id nhan vat co ky tu la -> 400",
              st == 400 and d.get("code") == "bad-character", f"{st} {d}")
        st, d = call("PUT", "/me/profile", token=token, body={})
        check("Khong co truong nao -> 400",
              st == 400 and d.get("code") == "nothing-to-do", f"{st} {d}")
        st, d = call("GET", "/me/profile", token=token)
        check("Ten sai KHONG ghi de len ten dung truoc do",
              d.get("profile", {}).get("name") == "Bi Bo", str(d.get("profile", {}).get("name")))

        print("\n[6] Bao quiz — server tu tinh XP")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 4, "total": 5, "meteors": 40})
        # 4 dung x20 + 30 hoan thanh = 110 XP
        check("quiz 4/5 -> 110 XP, len cap 2",
              st == 200 and d.get("xpGained") == 110 and d["level"]["level"] == 2,
              f"xp={d.get('xpGained')} level={d.get('level')}")
        check("Mo huy hieu first-quiz", "first-quiz" in d.get("newBadges", []),
              str(d.get("newBadges")))
        check("Bo dem quiz dung", d["progress"]["quizTaken"] == 1
              and d["progress"]["quizCorrect"] == 4
              and d["progress"]["quizAnswered"] == 5, str(d["progress"]))
        check("Do chinh xac 80%", d["progress"]["quizAccuracy"] == 80,
              str(d["progress"]["quizAccuracy"]))
        check("tt cong don = 40", d["progress"]["meteorsEarned"] == 40)

        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 5, "total": 5})
        # 5x20 + 30 + 50 thuong tron diem = 180
        check("quiz 5/5 -> 180 XP (co thuong tron diem)", d.get("xpGained") == 180,
              str(d.get("xpGained")))
        check("Mo huy hieu quiz-perfect", "quiz-perfect" in d.get("newBadges", []),
              str(d.get("newBadges")))
        check("quizPerfect = 1", d["progress"]["quizPerfect"] == 1)

        print("\n[7] Client co gui XP / huy hieu len -> bi bo qua")
        before = call("GET", "/me/profile", token=token)[1]["level"]["xp"]
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 1, "total": 1,
                           "xp": 999999, "badges": ["level-20"], "level": 50})
        check("xp trong body bi bo qua (chi cong 20+30+50=100)",
              d.get("xpGained") == 100, str(d.get("xpGained")))
        check("XP tang dung 100, khong phai 999999",
              d["level"]["xp"] == before + 100, f"{before} -> {d['level']['xp']}")
        check("Khong mo huy hieu level-20 theo yeu cau cua client",
              "level-20" not in d.get("newBadges", []), str(d.get("newBadges")))

        print("\n[8] So vo ly bi kep")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 999, "total": 3})
        check("dung 999/3 -> kep con 3/3", d["progress"]["quizAnswered"] == 3 + 5 + 5 + 1,
              f"quizAnswered={d['progress']['quizAnswered']}")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "dodge", "score": -50, "meteors": -9})
        check("diem am -> kep ve 0, khong ghi so am",
              st == 200 and d["progress"]["bests"].get("dodge", 0) >= 0, str(d["progress"]["bests"]))
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "dodge", "score": 10 ** 9, "seconds": 10 ** 7})
        check("diem 1 ti -> kep con 1.000.000", d["progress"]["bests"]["dodge"] == 1_000_000,
              str(d["progress"]["bests"]))
        check("thoi gian 10 trieu giay -> kep con 21.600",
              d["progress"]["flightSeconds"] <= 21600 + 1, str(d["progress"]["flightSeconds"]))

        print("\n[9] Ky luc khong bao gio tut xuong")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "dodge", "score": 10})
        check("Nop diem 10 sau khi da co 1.000.000 -> ky luc giu nguyen",
              d["progress"]["bests"]["dodge"] == 1_000_000, str(d["progress"]["bests"]))
        check("Mo huy hieu dodge-300 (ky luc >= 300)",
              any(b["id"] == "dodge-300" and b["earned"]
                  for b in call("GET", "/me/achievements", token=token)[1]["achievements"]["badges"]))

        print("\n[10] Doc bai: mot bai chi tinh MOT lan")
        st, d = call("POST", "/me/progress", token=token, body={"type": "lesson", "id": "bai-01"})
        check("Lan dau -> counted=true, +25 XP",
              d.get("counted") is True and d.get("xpGained") == 25, str(d.get("xpGained")))
        read1 = d["progress"]["lessonsRead"]
        st, d = call("POST", "/me/progress", token=token, body={"type": "lesson", "id": "bai-01"})
        check("Doc lai cung bai -> counted=false", d.get("counted") is False, str(d.get("counted")))
        check("lessonsRead KHONG tang", d["progress"]["lessonsRead"] == read1,
              f"{read1} -> {d['progress']['lessonsRead']}")
        st, d = call("POST", "/me/progress", token=token, body={"type": "lesson", "id": "bai-02"})
        check("Bai khac -> tinh tiep", d["progress"]["lessonsRead"] == read1 + 1)

        print("\n[11] Hanh tinh: ghe lai khong tinh them")
        st, d = call("POST", "/me/progress", token=token, body={"type": "planet", "id": "mars"})
        check("Lan dau -> +40 XP", d.get("xpGained") == 40, str(d.get("xpGained")))
        check("planets co mars", "mars" in d["progress"]["planets"], str(d["progress"]["planets"]))
        st, d = call("POST", "/me/progress", token=token, body={"type": "planet", "id": "mars"})
        check("Ghe lai -> counted=false, khong cong XP", d.get("counted") is False, str(d))
        st, d = call("POST", "/me/progress", token=token, body={"type": "planet", "id": "venus"})
        check("Hanh tinh khac -> 2 hanh tinh", len(d["progress"]["planets"]) == 2,
              str(d["progress"]["planets"]))

        print("\n[12] type sai / thieu du lieu")
        for body, code in (({"type": "khong-co-that"}, "bad-type"),
                           ({}, "bad-type"),
                           ({"type": "quiz", "total": 0}, "bad-quiz"),
                           ({"type": "game"}, "bad-game"),
                           ({"type": "lesson"}, "bad-lesson"),
                           ({"type": "planet", "id": "sao hoa!"}, "bad-planet")):
            st, d = call("POST", "/me/progress", token=token, body=body)
            check(f"{json.dumps(body, ensure_ascii=False)} -> 400 {code}",
                  st == 400 and d.get("code") == code, f"{st} {d.get('code')}")

        print("\n[13] Huy hieu khong bao gio mat, khong mo hai lan")
        a1 = call("GET", "/me/achievements", token=token)[1]
        earned1 = {b["id"] for b in a1["achievements"]["badges"] if b["earned"]}
        a2 = call("GET", "/me/achievements", token=token)[1]
        earned2 = {b["id"] for b in a2["achievements"]["badges"] if b["earned"]}
        check("Goi 2 lan ra cung ket qua", earned1 == earned2 and len(earned1) > 0,
              f"{len(earned1)} huy hieu: {sorted(earned1)}")
        check("Lan 2 khong bao mo them huy hieu nao", a2.get("newBadges") == [],
              str(a2.get("newBadges")))
        check("summary.earned khop so huy hieu earned=true",
              a2["achievements"]["summary"]["earned"] == len(earned2),
              f"{a2['achievements']['summary']} vs {len(earned2)}")
        check("Moi huy hieu earned deu co earnedAt",
              all(b.get("earnedAt") for b in a2["achievements"]["badges"] if b["earned"]))
        check("current khong vuot qua goal",
              all(b["current"] <= b["goal"] for b in a2["achievements"]["badges"]))

        print("\n[14] Tran XP moi luot nop + cap do tinh dung theo moc")
        # Game chay o may nguoi dung nen diem la con so client tu khai. Diem kep
        # 1.000.000 -> 50.015 XP neu khong co tran => nhay 32 cap trong MOT loi goi.
        b4 = call("GET", "/me/profile", token=token)[1]["level"]["xp"]
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "game", "game": "dodge", "score": 10 ** 9})
        check("Diem bia 1 ti -> XP mot luot bi kep o 300",
              d.get("xpGained") == 300, str(d.get("xpGained")))
        check("XP tang dung 300", d["level"]["xp"] == b4 + 300, f"{b4} -> {d['level']['xp']}")

        xp = call("GET", "/me/profile", token=token)[1]["level"]
        # Cong thuc o Services/Achievements.cs: XP can de len cap n = 100*(n-1)*n/2
        need = lambda n: 100 * (n - 1) * n // 2
        expect = 1
        while expect < 50 and xp["xp"] >= need(expect + 1):
            expect += 1
        check(f"XP {xp['xp']} -> cap {expect}", xp["level"] == expect, str(xp))
        check("xpInLevel = XP tru moc cap hien tai",
              xp["xpInLevel"] == xp["xp"] - need(xp["level"]),
              f"{xp['xpInLevel']} vs {xp['xp'] - need(xp['level'])}")
        check("xpForNext = do rong cua cap hien tai",
              xp["xpForNext"] == need(xp["level"] + 1) - need(xp["level"]) or xp["level"] >= 50,
              str(xp["xpForNext"]))
        check("Phan tram trong 0..100", 0 <= xp["pct"] <= 100, str(xp["pct"]))

        print("\n[15] Khong doc/ghi duoc du lieu nguoi khac")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 1, "total": 1, "uid": "nguoi-khac"})
        check("uid trong body bi bo qua", st == 200, f"{st}")
        check("Chi ho so cua chinh minh doi",
              len([r for r in rows("nguoi-khac")]) == 0)

    finally:
        print("\n[don] Xoa du lieu test")
        n = wipe(uid)
        check("Xoa het ban ghi DynamoDB", n > 0, f"{n} dong")
        try:
            idp("delete", {"idToken": token})
            check("Xoa tai khoan Firebase tam", True)
        except Exception as e:
            check("Xoa tai khoan Firebase tam", False, str(e))
        check("Khong con ban ghi nao cua uid", len(rows(uid)) == 0)

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
