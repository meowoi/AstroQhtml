# -*- coding: utf-8 -*-
"""
test_daily.py — kiểm thử ĐỘC LẬP việc hằng ngày + chuỗi ngày CÓ ÂN HẠN.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_daily.py                 # http://localhost:5080
    python scratchpad/test_daily.py <base-url>      # ban that tren AWS

Trong tam — nam dieu kien da chot TRUOC khi viet dong nao (xem Services/Daily.cs):
  ① 2 ngay an han moi tuan       ② chuoi KHONG ve 0 (ky luc giu vinh vien)
  ③ KHONG dem nguoc               ④ KHONG giuc
  ⑤ noi truoc luat (server tra `grace`/`graceLeft`/`goal`)

Cong them ba thu de mat tien / de noi sai nhat:
  · thuong tra dung MOT LAN moi ngay (goi lai bao nhieu lan cung khong cong them)
  · client KHONG tu khai duoc mot viec da xong
  · chuoi tinh theo ngay CO LAM VIEC, khong phai ngay mo app

⚠️ MOI PHEP KIEM VE CHUOI PHAI KHONG PHU THUOC HOM NAY LA THU MAY. Mot khoang nghi
   3 ngay co the nam tron trong mot tuan (=> dut chuoi) hoac trai qua hai tuan
   (=> con nguyen), nen ghim "gap 3 = dut" la mot qua min hen gio theo lich —
   dung cai bay `test_report.py` da mac voi `createdAt` gan cung. Cach lam o day:
   chi dung nhung khoang CHAC CHAN mot chieu, va nhung ca con lai thi TINH tuan
   bang phep so ngay roi in ra nhanh nao vua duoc do.

Tu tao tai khoan Firebase tam, tu don moi ban ghi trong `finally`.
"""
import concurrent.futures as cf
import datetime as dt
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

import _fbtest

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"
SV = Path(__file__).resolve().parents[2] / "AstroqSV" / "src" / "AstroqSV.Api"

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


def aws(*args):
    return subprocess.run(["aws"] + list(args), capture_output=True, text=True, timeout=60)


# ── doc LUAT tu ma nguon, khong gan cung ─────────────────────────────
# Cung loi `test_missions.py` da dung: phep kiem gan cung con so thi no bao hong
# dung luc san pham duoc doi cho dung. Doc tu nguon su that thi doi bang viec la
# phep kiem tu theo.

def law():
    src = (SV / "Services" / "Daily.cs").read_text(encoding="utf-8")
    grace = int(re.search(r"GraceDaysPerWeek\s*=\s*(\d+)", src).group(1))
    tasks = [(m.group(1), int(m.group(2)), int(m.group(3)))
             for m in re.finditer(r'new\("([a-z]+)",\s*(\d+),\s*(\d+)\)', src)]
    wsrc = (SV / "Services" / "Wallet.cs").read_text(encoding="utf-8")
    fees = {m.group(1): int(m.group(2))
            for m in re.finditer(r'\["([a-z]+)"\]\s*=\s*(\d+)', wsrc)}
    cap = int(re.search(r"MaxPerDailyAll\s*=\s*(\d+)", wsrc).group(1))
    return grace, tasks, fees, cap


# ── ban ghi ──────────────────────────────────────────────────────────

def seed_profile(uid, email):
    it = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
          "uid": {"S": uid}, "email": {"S": email}, "name": {"S": "Daily Test"},
          "createdAt": {"S": "2026-07-29T00:00:00.000Z"}}
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


def seed_wallet(uid, meteors):
    it = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
          "meteors": {"N": str(meteors)}, "diamonds": {"N": "0"}}
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


def seed_streak(uid, cur, best, last_day, week_key, missed):
    it = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "STREAK"},
          "cur": {"N": str(cur)}, "best": {"N": str(best)},
          "lastDay": {"S": last_day}, "weekKey": {"S": week_key},
          "missed": {"N": str(missed)}}
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


def rows(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": f"USER#{uid}"}}),
            "--consistent-read")
    return [] if r.returncode != 0 else json.loads(r.stdout or "{}").get("Items", [])


def sk_set(uid):
    return {r["SK"]["S"] for r in rows(uid)}


def del_sk(uid, sk):
    return aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps({"PK": {"S": f"USER#{uid}"},
                                    "SK": {"S": sk}})).returncode == 0


def wipe(uid):
    n = 0
    for it in rows(uid):
        if aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]})).returncode == 0:
            n += 1
    return n


# ── tro giup ─────────────────────────────────────────────────────────

def vn_today():
    """Ngay hom nay theo gio Viet Nam — cung dinh nghia Report.TzOffsetHours."""
    return (dt.datetime.utcnow() + dt.timedelta(hours=7)).date()


def monday_of(d):
    return d - dt.timedelta(days=d.weekday())


def daily(token):
    st, d = call("GET", "/me/daily", token=token)
    return st, d.get("daily", {}), d


def tmap(snap):
    return {t["id"]: t for t in snap.get("tasks", [])}


def bal(token):
    return call("GET", "/me/wallet", token=token)[1].get("meteors")


def do_quiz(token, correct, total, meteors=60):
    return call("POST", "/me/progress", token=token,
                body={"type": "quiz", "correct": correct, "total": total,
                      "meteors": meteors, "opId": uuid.uuid4().hex})


def do_game(token, game="dodge", score=100, seconds=30, meteors=5):
    return call("POST", "/me/progress", token=token,
                body={"type": "game", "game": game, "score": score,
                      "seconds": seconds, "meteors": meteors,
                      "opId": uuid.uuid4().hex})


# ── kich ban ─────────────────────────────────────────────────────────

def main():
    grace, tasks, fees, cap = law()
    goals = {t[0]: t[1] for t in tasks}
    tts = {t[0]: t[2] for t in tasks}
    total_tt = sum(tts.values())
    today = vn_today()

    print(f"=== Viec hang ngay + chuoi @ {BASE} ===")
    print(f"    Luat doc tu ma nguon: an han {grace} ngay/tuan · "
          f"viec {tasks} · tong {total_tt} tt · tran {cap}")
    print(f"    Hom nay (gio VN): {today} ({today.strftime('%a')})\n")

    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    # ── [0] Hang rao cua chinh BANG VIEC ──
    print("\n[0] Hang rao cua bang viec (khong can mang)")
    check("Bang viec khong rong", len(tasks) >= 3, f"{len(tasks)} viec")
    check("Tong thuong mot ngay KHONG vuot tran Wallet",
          total_tt <= cap, f"{total_tt} <= {cap}")
    # ⚠️ Thuong phai LON HON phi vao cua cua game dat nhat, khong thi "viec hang
    #    ngay" la mot viec LAM MAT TIEN.
    max_fee = max(fees.values()) if fees else 0
    check("Viec 'play' thuong NHIEU HON phi game dat nhat",
          tts.get("play", 0) > max_fee, f"{tts.get('play')} > {max_fee}")
    # ⚠️ MOI VIEC PHAI LAM LAI DUOC VO HAN. `lesson`/`planet`/`mission` chi tinh
    #    LAN DAU (49 bai, 8 hanh tinh, 7 chang) nen chung se can — mot viec hang
    #    ngay khong bao gio hoan thanh duoc nua la mot loi hua vinh vien khong giu.
    check("Khong viec nao dua tren su kien CHI TINH LAN DAU",
          not ({"lesson", "planet", "mission"} & set(goals)),
          f"ids={sorted(goals)}")

    print("\n[1] Khong co token")
    st, _ = call("GET", "/me/daily")
    check("GET /me/daily -> 401", st == 401, f"status={st}")

    email = f"daily-test-{uuid.uuid4().hex[:10]}@astroq-test.invalid"
    print(f"\n[2] Tao tai khoan tam: {email}")
    uid, token, _pw = _fbtest.make_verified(email)
    check("Co idToken + uid", bool(uid and token), f"uid={uid}")

    try:
        seed_profile(uid, email)
        seed_wallet(uid, 0)

        # ── [3] Chua lam gi hom nay ──
        print("\n[3] Chua lam gi hom nay — khong bia so, khong sinh ban ghi rong")
        st, snap, _ = daily(token)
        check("GET /me/daily -> 200", st == 200, f"status={st}")
        check("Ngay la hom nay (gio VN)", snap.get("day") == today.isoformat(),
              f"{snap.get('day')} vs {today.isoformat()}")
        tm = tmap(snap)
        check("Tra ve du bang viec", set(tm) == set(goals), f"{sorted(tm)}")
        check("Moi viec: current = 0, chua xong, chua tra thuong",
              all(t["current"] == 0 and not t["done"] and not t["paid"]
                  for t in tm.values()))
        check("Moc cua tung viec dung bang bang o server",
              all(tm[i]["goal"] == goals[i] for i in goals))
        check("gotTt = 0", snap.get("gotTt") == 0, str(snap.get("gotTt")))
        stk = snap.get("streak", {})
        check("Chuoi = 0 va hom nay CHUA duoc tinh",
              stk.get("cur") == 0 and stk.get("todayIn") is False, str(stk))
        check("⑤ Noi truoc luat: tra ve `grace` dung bang server",
              stk.get("grace") == grace, str(stk.get("grace")))
        check("Con nguyen an han cua tuan", stk.get("graceLeft") == grace,
              str(stk.get("graceLeft")))
        sks = sk_set(uid)
        check("KHONG sinh ban ghi DAILY# rong",
              not any(s.startswith("DAILY#") for s in sks), str(sorted(sks)))
        check("KHONG sinh ban ghi STREAK rong", "STREAK" not in sks, str(sorted(sks)))

        # ── [4] ③ Khong dem nguoc ──
        print("\n[4] ③ KHONG DEM NGUOC — khong tra ve bat ky moc het han nao")
        _, _, full = daily(token)
        blob = json.dumps(full).lower()
        banned = ["expiresat", "resetat", "secondsleft", "deadline", "endsat",
                  "timeleft", "expiresin", "countdown"]
        hit = [b for b in banned if b in blob]
        check("Khong co truong nao mang nghia 'het han'", not hit, str(hit))

        # ── [5] Mot luot quiz DAT ──
        print("\n[5] Mot luot quiz DAT -> xong viec 'quiz', tra thuong dung mot lan")
        b0 = bal(token)
        st, d = do_quiz(token, correct=3, total=5)
        check("POST /me/progress -> 200", st == 200, f"status={st}")
        snap = d.get("daily", {})
        tm = tmap(snap)
        check("Viec 'quiz' xong ngay trong lan nop do",
              tm["quiz"]["done"] and tm["quiz"]["paid"], str(tm.get("quiz")))
        check("dailyPaid = dung thuong cua viec 'quiz'",
              d.get("dailyPaid") == tts["quiz"], f"{d.get('dailyPaid')} vs {tts['quiz']}")
        b1 = bal(token)
        check("Vi cong dung (thuong quiz + thuong viec ngay)",
              b1 - b0 == d.get("awarded", 0) + tts["quiz"],
              f"{b0}->{b1}, awarded={d.get('awarded')}, daily={d.get('dailyPaid')}")
        check("Viec 'correct' chay theo so cau dung",
              tm["correct"]["current"] == 3, str(tm["correct"]))
        check("Viec 'correct' CHUA xong (3 < moc)",
              not tm["correct"]["done"] or goals["correct"] <= 3, str(tm["correct"]))
        stk = snap.get("streak", {})
        check("Chuoi len 1 va hom nay DA duoc tinh",
              stk.get("cur") == 1 and stk.get("todayIn") is True, str(stk))
        check("Ky luc it nhat bang chuoi hien tai", stk.get("best") >= 1, str(stk))

        print("\n[6] Goi lai nhieu lan -> KHONG cong thuong lan hai")
        b2 = bal(token)
        for _ in range(3):
            daily(token)
        check("Ba lan GET /me/daily: vi khong doi", bal(token) == b2, str(bal(token)))
        _, snap, dd = daily(token)
        check("dailyPaid = 0 khi khong con viec nao moi xong",
              dd.get("dailyPaid") == 0, str(dd.get("dailyPaid")))
        check("gotTt bang dung thuong da nhan",
              snap.get("gotTt") == tts["quiz"], str(snap.get("gotTt")))

        print("\n[7] Mo bang nhieu lan KHONG day chuoi (chuoi theo ngay CO LAM VIEC)")
        _, snap, _ = daily(token)
        check("Chuoi van la 1 sau 5 lan mo bang", snap["streak"]["cur"] == 1,
              str(snap["streak"]))

        # ── [8] Quiz KHONG dat ──
        print("\n[8] Quiz KHONG dat -> khong tinh viec 'quiz', nhung cau dung van dem")
        cur_correct = tmap(snap)["correct"]["current"]
        st, d = do_quiz(token, correct=1, total=5)
        tm = tmap(d.get("daily", {}))
        check("So cau dung cong don qua cac luot",
              tm["correct"]["current"] == cur_correct + 1,
              f"{cur_correct} -> {tm['correct']['current']}")
        check("Khong tra thuong lan hai cho viec 'quiz'",
              d.get("dailyPaid") == 0, str(d.get("dailyPaid")))

        # ── [9] Choi game ──
        print("\n[9] Choi mot luot mini-game -> xong viec 'play'")
        b3 = bal(token)
        st, d = do_game(token)
        tm = tmap(d.get("daily", {}))
        check("Viec 'play' xong", tm["play"]["done"] and tm["play"]["paid"], str(tm["play"]))
        check("dailyPaid = thuong viec 'play'", d.get("dailyPaid") == tts["play"],
              str(d.get("dailyPaid")))
        check("Vi cong dung", bal(token) - b3 == d.get("awarded", 0) + tts["play"],
              f"{b3}->{bal(token)}")

        # ── [10] Du so cau dung ──
        print("\n[10] Lam den khi du so cau dung -> xong ca ba viec")
        for _ in range(4):
            st, d = do_quiz(token, correct=3, total=5)
            if tmap(d.get("daily", {}))["correct"]["done"]:
                break
        snap = d.get("daily", {})
        tm = tmap(snap)
        check("Ca ba viec da xong", all(t["done"] for t in tm.values()),
              str({i: t["current"] for i, t in tm.items()}))
        check("gotTt = tong thuong mot ngay", snap.get("gotTt") == total_tt,
              f"{snap.get('gotTt')} vs {total_tt}")
        check("totalTt server bao dung bang tong bang viec",
              snap.get("totalTt") == total_tt, str(snap.get("totalTt")))
        # ⚠️ Xong het roi thi lam THEM mot luot nua khong duoc cong thuong viec ngay:
        #    so vi phai tang DUNG BANG thuong quiz, khong hon mot tt nao.
        b4 = bal(token)
        _, dq = do_quiz(token, correct=3, total=5)
        check("Xong het roi thi khong con thuong viec ngay nao",
              bal(token) - b4 == dq.get("awarded", 0) and dq.get("dailyPaid") == 0,
              f"{b4} -> {bal(token)}, awarded={dq.get('awarded')}, "
              f"dailyPaid={dq.get('dailyPaid')}")
        _, _, dd = daily(token)
        check("dailyPaid = 0 sau khi xong het", dd.get("dailyPaid") == 0,
              str(dd.get("dailyPaid")))

        # ── [11] GET /me/daily tu cap bu ──
        print("\n[11] Tu cap bu: viec da xong ma ban ghi tra thuong bi mat")
        b5 = bal(token)
        check("Xoa ban ghi DAILY# cua hom nay",
              del_sk(uid, f"DAILY#{today.isoformat()}"))
        _, snap, dd = daily(token)
        check("GET /me/daily tra bu dung tong thuong mot ngay",
              dd.get("dailyPaid") == total_tt, str(dd.get("dailyPaid")))
        check("Vi cong dung phan bu", bal(token) - b5 == total_tt,
              f"{b5} -> {bal(token)}")
        _, _, dd = daily(token)
        check("Cap bu roi thi khong cap bu lan hai", dd.get("dailyPaid") == 0,
              str(dd.get("dailyPaid")))

        # ── [12] Client khong tu khai duoc ──
        print("\n[12] Client KHONG tu khai duoc mot viec da xong")
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "daily", "meteors": 999})
        check("type='daily' -> 400 bad-type", st == 400 and d.get("code") == "bad-type",
              f"{st} {d.get('code')}")
        b6 = bal(token)
        st, d = call("POST", "/me/progress", token=token,
                     body={"type": "quiz", "correct": 3, "total": 5, "meteors": 1,
                           "opId": uuid.uuid4().hex,
                           "daily": {"tasks": [{"id": "quiz", "done": True}], "gotTt": 999},
                           "streak": {"cur": 500, "best": 999},
                           "dailyPaid": 999, "gotTt": 999})
        tm = tmap(d.get("daily", {}))
        check("Gui kem `daily`/`streak`/`dailyPaid` -> bi bo qua",
              d.get("dailyPaid") == 0 and d["daily"]["streak"]["cur"] == 1
              and d["daily"]["gotTt"] == total_tt, str(d.get("daily", {}).get("streak")))
        check("Vi chi cong thuong quiz that", bal(token) - b6 == d.get("awarded", 0),
              f"{b6} -> {bal(token)}, awarded={d.get('awarded')}")

        # ══════════════ CHUOI NGAY ══════════════
        print("\n[13] Chuoi: hom qua co hoc -> cong tiep (khong nghi ngay nao)")
        y = today - dt.timedelta(days=1)
        seed_streak(uid, 5, 9, y.isoformat(), monday_of(y).isoformat(), 0)
        st, d = do_quiz(token, correct=3, total=5)
        stk = d["daily"]["streak"]
        check("Chuoi 5 -> 6", stk["cur"] == 6, str(stk))
        check("Ky luc 9 giu nguyen (chua vuot)", stk["best"] == 9, str(stk))

        print("\n[14] Chuoi: goi lai trong CUNG ngay -> khong day len")
        st, d = do_quiz(token, correct=3, total=5)
        check("Van la 6 sau lan nop thu hai trong ngay",
              d["daily"]["streak"]["cur"] == 6, str(d["daily"]["streak"]))

        print("\n[15] Ky luc: vuot moc cu thi ky luc theo len")
        seed_streak(uid, 9, 9, y.isoformat(), monday_of(y).isoformat(), 0)
        st, d = do_quiz(token, correct=3, total=5)
        stk = d["daily"]["streak"]
        check("Chuoi 10 va ky luc len 10", stk["cur"] == 10 and stk["best"] == 10, str(stk))

        print(f"\n[16] ① An han: nghi dung {grace} ngay -> chuoi CON NGUYEN")
        # ⚠️ Khoang nghi = grace ngay thi CHAC CHAN mot chieu: te nhat la ca `grace`
        #    ngay nam tron trong mot tuan, van khong VUOT an han. Khong phu thuoc
        #    hom nay la thu may.
        prev = today - dt.timedelta(days=grace + 1)
        seed_streak(uid, 4, 12, prev.isoformat(), monday_of(prev).isoformat(), 0)
        st, d = do_quiz(token, correct=3, total=5)
        stk = d["daily"]["streak"]
        check(f"Nghi {grace} ngay: chuoi 4 -> 5 (khong dut)", stk["cur"] == 5, str(stk))
        check("Ky luc 12 khong bi ha", stk["best"] == 12, str(stk))

        print("\n[17] ② Nghi rat lau -> chuoi bat dau lai tu 1, KY LUC GIU NGUYEN")
        # 30 ngay trai qua ~4 tuan; moi tuan chi duoc nghi `grace` ngay nen chac chan
        # co tuan vuot — khong phu thuoc thu trong tuan.
        old = today - dt.timedelta(days=30)
        seed_streak(uid, 20, 25, old.isoformat(), monday_of(old).isoformat(), 0)
        st, d = do_quiz(token, correct=3, total=5)
        stk = d["daily"]["streak"]
        check("Chuoi ve 1 — KHONG ve 0", stk["cur"] == 1, str(stk))
        check("② Ky luc 25 GIU NGUYEN sau khi dut chuoi", stk["best"] == 25, str(stk))
        check("An han cua tuan nay day lai", stk["graceLeft"] == grace, str(stk))

        print("\n[18] An han da dung het trong tuan -> nghi them mot ngay la dut")
        # Dat `missed` = grace cho TUAN NAY roi cho nghi dung MOT ngay nua.
        # Ngay nghi la `today - 1`. Neu no cung tuan voi hom nay thi an han da het
        # => dut; neu no thuoc tuan truoc thi an han day lai => con nguyen.
        # Ca hai nhanh deu duoc kiem, va script IN RA nhanh nao vua chay.
        y1 = today - dt.timedelta(days=1)
        prev2 = today - dt.timedelta(days=2)
        same_week = monday_of(y1) == monday_of(today)
        seed_streak(uid, 8, 30, prev2.isoformat(), monday_of(today).isoformat(), grace)
        st, d = do_quiz(token, correct=3, total=5)
        stk = d["daily"]["streak"]
        if same_week:
            check("Het an han + nghi them 1 ngay -> chuoi ve 1",
                  stk["cur"] == 1, f"{stk} (ngay nghi {y1} cung tuan)")
        else:
            check("Ngay nghi thuoc tuan truoc -> an han day lai, chuoi con nguyen",
                  stk["cur"] == 9, f"{stk} (ngay nghi {y1} khac tuan)")
        check("② Ky luc 30 giu nguyen o ca hai nhanh", stk["best"] == 30, str(stk))

        print("\n[19] Khong bao gio di lui (dong ho may sai / gui lai tu hang cho)")
        tomorrow = today + dt.timedelta(days=1)
        seed_streak(uid, 15, 40, tomorrow.isoformat(), monday_of(tomorrow).isoformat(), 0)
        st, d = do_quiz(token, correct=3, total=5)
        stk = d["daily"]["streak"]
        check("lastDay o TUONG LAI -> khong ha chuoi",
              stk["cur"] == 15 and stk["best"] == 40, str(stk))

        print("\n[20] graceLeft phan anh dung so ngay da nghi trong tuan")
        seed_streak(uid, 3, 40, (today - dt.timedelta(days=1)).isoformat(),
                    monday_of(today).isoformat(), 1)
        _, snap, _ = daily(token)
        check("Da nghi 1 ngay tuan nay -> con grace-1",
              snap["streak"]["graceLeft"] == grace - 1, str(snap["streak"]))

        print("\n[21] Ban ghi STREAK KHONG co ttl (ky luc khong duoc bi don rac)")
        srow = next((r for r in rows(uid) if r["SK"]["S"] == "STREAK"), None)
        check("Co ban ghi STREAK", srow is not None)
        check("STREAK khong co truong ttl", srow is not None and "ttl" not in srow,
              str(sorted(srow.keys())) if srow else "")
        drow = next((r for r in rows(uid) if r["SK"]["S"].startswith("DAILY#")), None)
        check("Ban ghi DAILY# CO ttl (don duoc)", drow is not None and "ttl" in drow,
              str(sorted(drow.keys())) if drow else "")

        print("\n[22] GOI SONG SONG -> chi tra thuong dung MOT lan")
        # ⚠️⚠️ PHEP KIEM NAY DUOC THEM SAU KHI PHEP THU PHA HOAI LOT (pha_daily.py):
        #    doi `ConditionExpression` cua TryPayDailyAsync thanh mot dieu kien LUON
        #    DUNG thi ca 21 muc tren van xanh. Ly do: chot `!t.Paid` o tang ung dung
        #    da chan duong TUAN TU, nen dieu kien cua DynamoDB chi thuc su gac o ca
        #    GOI SONG SONG — hai lan doc cung thay "chua tra". Khong co muc nay thi
        #    chot nguyen tu that su khong duoc do boi bat ky phep kiem nao.
        seed_streak(uid, 1, 40, today.isoformat(), monday_of(today).isoformat(), 0)
        del_sk(uid, f"DAILY#{today.isoformat()}")     # ba viec: da xong, chua tra thuong
        b7 = bal(token)
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            res = [f.result() for f in [ex.submit(daily, token) for _ in range(6)]]
        got = sum(r[2].get("dailyPaid", 0) for r in res)
        check("Tong dailyPaid cua 6 loi goi = dung mot ngay thuong",
              got == total_tt, f"{got} vs {total_tt}")
        check("Vi cong dung mot lan", bal(token) - b7 == total_tt,
              f"{b7} -> {bal(token)} (ky vong +{total_tt})")
        drow = next((r for r in rows(uid) if r["SK"]["S"] == f"DAILY#{today.isoformat()}"), None)
        paid_ss = sorted(drow.get("paid", {}).get("SS", [])) if drow else []
        check("Moi viec nam dung mot lan trong `paid`",
              paid_ss == sorted(goals), str(paid_ss))

        print("\n[23] Route chi nhan GET")
        for m in ("POST", "PUT", "DELETE"):
            st, _ = call(m, "/me/daily", token=token, body={} if m != "DELETE" else None)
            check(f"{m} /me/daily -> 405", st == 405, f"status={st}")

    finally:
        print("\n[don] Xoa du lieu test")
        n = wipe(uid)
        print(f"  Da xoa {n} dong DynamoDB")
        try:
            _fbtest.delete(_fbtest.signin(email, _pw))
            print("  Da xoa tai khoan Firebase tam")
        except Exception as e:
            print(f"  [!] Khong xoa duoc tai khoan tam: {e}")
        left = [r["SK"]["S"] for r in rows(uid)]
        print(f"  Con sot: {left if left else 'khong con dong nao'}")

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
