# -*- coding: utf-8 -*-
"""
test_report.py — kiem thu DOC LAP bao cao tuan cho phu huynh.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_report.py                 # http://localhost:5080
    python scratchpad/test_report.py <base-url>      # ban that tren AWS

    GET  /me/report?week=n     -> { current, previous, badges, lifetime }
    POST /me/report/email?week=n

Trong tam — thu de lam bao cao NOI SAI voi phu huynh:
  1. TUAN TINH THEO GIO VIET NAM. Lay tuan theo UTC thi buoi hoc toi Chu nhat o VN
     roi sang tuan sau, va phu huynh doc bao cao thay thieu dung buoi cuoi tuan.
  2. `accuracy = null` KHAC `0`. null = "chua lam cau nao"; 0 = "lam ma sai het".
     Tra ve 0 cho dua tre khong lam bai nao la mot loi khang dinh SAI.
  3. TUAN RONG THI KHONG GUI THU. Mot email "con ban hoc 0 phut" la cach nhanh
     nhat de bi bam Spam, ma ti le spam cao thi AWS khoa quyen gui CA tai khoan.
  4. Bo dem o PROGRESS la tong ca doi — bao cao TUAN khong duoc lay tu do.

Tu tao tai khoan Firebase tam, tu don moi ban ghi trong `finally`.

⚠️ Nhan cua check() PHAI KHONG DAU (console Windows cp1252).
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

import _fbtest

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"
VN = timezone(timedelta(hours=7))

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
        with urllib.request.urlopen(req, timeout=40) as r:
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


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True, timeout=90)


def seed_profile(uid, email, created=None):
    """⚠️ `createdAt` MAC DINH DAT TRUOC 3 TUAN, khong gan cung mot ngay lich.
    Bao cao cat cua so tuan tai ngay dang ky, nen moc dang ky nam trong khoang
    dang do la moi phep kiem "tuan tron" o cac muc duoi deu lech — ma lech theo
    kieu im lang: so lieu van tra ve, chi la thieu may dong."""
    c = created or (monday_vn(3) + timedelta(hours=3))
    it = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
          "uid": {"S": uid}, "email": {"S": email}, "name": {"S": "Bin"},
          "createdAt": {"S": c.strftime('%Y-%m-%dT%H:%M:%S.%f0Z')}}
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


def put_hist(uid, at_utc, typ, **kw):
    """Gieo THANG mot dong nhat ky vao thoi diem mong muon — khong the dat lai
    dong ho cua server, ma bao cao tuan thi phai thu duoc ca tuan truoc."""
    sk = f"HIST#{at_utc.strftime('%Y-%m-%dT%H:%M:%S.%f0Z')}#{uuid.uuid4().hex[:4]}"
    it = {"PK": {"S": f"USER#{uid}"}, "SK": {"S": sk},
          "type": {"S": typ}, "refId": {"S": kw.get("ref", "")},
          "at": {"S": at_utc.strftime('%Y-%m-%dT%H:%M:%S.%f0Z')},
          "xp": {"N": str(kw.get("xp", 0))}, "meteors": {"N": str(kw.get("meteors", 0))}}
    for k in ("correct", "total", "score", "seconds"):
        if kw.get(k) is not None:
            it[k] = {"N": str(kw[k])}
    return aws("dynamodb", "put-item", "--table-name", TABLE,
               "--item", json.dumps(it)).returncode == 0


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


def monday_vn(weeks_ago=0):
    """00:00 thu Hai gio VN cua tuan thu `weeks_ago`, tra ve o UTC."""
    now_vn = datetime.now(VN)
    back = (now_vn.weekday()) + 7 * weeks_ago          # weekday(): thu Hai = 0
    m = (now_vn - timedelta(days=back)).replace(hour=0, minute=0, second=0, microsecond=0)
    return m.astimezone(timezone.utc).replace(tzinfo=None)


def main():
    print(f"=== Bao cao tuan cho phu huynh @ {BASE} ===\n")
    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    email = f"rep-{uuid.uuid4().hex[:10]}@simulator.amazonses.com"
    uid = token = None
    try:
        uid, token, _ = _fbtest.make_verified(email)
        check("Gieo duoc ho so tam", seed_profile(uid, email), uid[:10])

        # ── [1] Khong token ──
        print("\n[1] Khong token")
        for m, p in (("GET", "/me/report"), ("POST", "/me/report/email")):
            st, _ = call(m, p, body={} if m == "POST" else None)
            check(f"{m} {p} -> 401", st == 401, f"status={st}")

        # ── [2] Chua co nhat ky -> tuan RONG, khong phai toan so 0 ──
        print("\n[2] Chua co nhat ky nao")
        st, d = call("GET", "/me/report", token=token)
        check("GET /me/report -> 200", st == 200, f"status={st}")
        cur = (d or {}).get("current") or {}
        check("current.empty = true", cur.get("empty") is True, str(cur.get("empty")))
        # ⚠️ Phep kiem quan trong nhat cua muc nay
        check("accuracy = null (KHONG phai 0)", cur.get("accuracy") is None,
              repr(cur.get("accuracy")))
        check("activeDays = 0", cur.get("activeDays") == 0, str(cur.get("activeDays")))
        check("Tra ve ten con", d.get("child") == "Bin", str(d.get("child")))

        # ── [3] Gieo tuan NAY ──
        print("\n[3] Gieo hoat dong tuan NAY")
        mon = monday_vn(0)
        # 3 ngay khac nhau, trong do 2 lan cung mot ngay -> activeDays phai la 3
        put_hist(uid, mon + timedelta(hours=9),  "quiz", correct=4, total=5, xp=110, meteors=80)
        put_hist(uid, mon + timedelta(hours=11), "quiz", correct=2, total=5, xp=50)
        put_hist(uid, mon + timedelta(days=1, hours=10), "quiz", correct=5, total=5, xp=140)
        put_hist(uid, mon + timedelta(days=3, hours=15), "game", ref="dodge",
                 score=900, seconds=300, xp=40, meteors=12)
        put_hist(uid, mon + timedelta(days=3, hours=16), "lesson", ref="lib-nebula", xp=15)
        put_hist(uid, mon + timedelta(days=3, hours=17), "mission", ref="earth:scan", xp=20)
        time.sleep(1)

        st, d = call("GET", "/me/report", token=token)
        cur = d["current"]
        check("empty = false", cur["empty"] is False)
        check("activeDays = 3 (2 luot cung ngay chi tinh 1)", cur["activeDays"] == 3,
              str(cur["activeDays"]))
        check("quizRounds = 3", cur["quizRounds"] == 3, str(cur["quizRounds"]))
        check("quizAnswered = 15", cur["quizAnswered"] == 15, str(cur["quizAnswered"]))
        check("quizCorrect = 11", cur["quizCorrect"] == 11, str(cur["quizCorrect"]))
        check("accuracy = 73 (11/15 lam tron)", cur["accuracy"] == 73, str(cur["accuracy"]))
        check("games = 1, gameSeconds = 300",
              cur["games"] == 1 and cur["gameSeconds"] == 300,
              f'{cur["games"]}/{cur["gameSeconds"]}')
        check("lessons = 1", cur["lessons"] == 1, str(cur["lessons"]))
        check("missionSteps = 1", cur["missionSteps"] == 1, str(cur["missionSteps"]))
        check("missionRefs co 'earth:scan'", "earth:scan" in cur["missionRefs"],
              str(cur["missionRefs"]))
        check("xp cong dung = 375", cur["xp"] == 375, str(cur["xp"]))
        check("meteors cong dung = 92", cur["meteors"] == 92, str(cur["meteors"]))
        check("previous van rong", d["previous"]["empty"] is True)

        # ── [4] Bien tuan theo GIO VIET NAM ──
        print("\n[4] Bien tuan tinh theo gio Viet Nam (+07), khong phai UTC")
        # 23:30 Chu nhat gio VN = 16:30 UTC CN -> VAN thuoc tuan nay
        sun_late = mon + timedelta(days=6, hours=23, minutes=30)
        put_hist(uid, sun_late, "lesson", ref="late-sunday", xp=15)
        # 00:30 thu Hai gio VN cua tuan SAU -> KHONG duoc rot vao tuan nay
        next_mon = mon + timedelta(days=7, minutes=30)
        put_hist(uid, next_mon, "lesson", ref="next-week", xp=15)
        time.sleep(1)
        st, d = call("GET", "/me/report", token=token)
        check("Buoi toi Chu nhat (gio VN) VAN thuoc tuan nay",
              d["current"]["lessons"] == 2, str(d["current"]["lessons"]))
        check("Viec cua thu Hai tuan sau KHONG lot vao tuan nay",
              d["current"]["lessons"] == 2 and d["current"]["activeDays"] == 4,
              f'lessons={d["current"]["lessons"]} days={d["current"]["activeDays"]}')

        # ── [5] Tuan TRUOC + so sanh ──
        print("\n[5] Tuan truoc va phep so sanh")
        pmon = monday_vn(1)
        put_hist(uid, pmon + timedelta(days=2, hours=9), "quiz", correct=3, total=5, xp=80)
        time.sleep(1)
        st, d = call("GET", "/me/report", token=token)
        check("previous khong con rong", d["previous"]["empty"] is False)
        check("previous.accuracy = 60", d["previous"]["accuracy"] == 60,
              str(d["previous"]["accuracy"]))
        st, d1 = call("GET", "/me/report?week=1", token=token)
        check("?week=1 -> current CHINH LA tuan truoc",
              d1["current"]["accuracy"] == 60, str(d1["current"]["accuracy"]))
        check("?week=1 -> previous la 2 tuan truoc, van rong",
              d1["previous"]["empty"] is True)

        # ── [6] Chan tham so vo ly ──
        print("\n[6] Tham so vo ly")
        st, dz = call("GET", "/me/report?week=99999", token=token)
        check("week=99999 -> 200, bi kep", st == 200 and dz["week"] <= 52,
              f'week={dz.get("week")}')
        st, dz = call("GET", "/me/report?week=-5", token=token)
        check("week=-5 -> kep ve 0", st == 200 and dz["week"] == 0, f'week={dz.get("week")}')

        # ── [7] Bao cao KHONG lay tu bo dem ca doi ──
        print("\n[7] Bao cao tuan doc NHAT KY, khong doc bo dem ca doi")
        # Nem mot loat viec qua /me/progress: bo dem ca doi tang, nhung chung nam o
        # TUAN NAY nen chi so tuan nay tang — tuan TRUOC phai giu nguyen.
        prev_before = d["previous"]["quizRounds"]
        for _ in range(2):
            call("POST", "/me/progress", token=token,
                 body={"type": "quiz", "correct": 1, "total": 5, "opId": uuid.uuid4().hex})
        time.sleep(1)
        st, d2 = call("GET", "/me/report", token=token)
        check("Tuan nay tang them 2 luot", d2["current"]["quizRounds"] == 5,
              str(d2["current"]["quizRounds"]))
        check("Tuan TRUOC khong bi anh huong",
              d2["previous"]["quizRounds"] == prev_before,
              f'{d2["previous"]["quizRounds"]} vs {prev_before}')

        # ── [8] Gui email ──
        print("\n[8] Gui bao cao qua email (dia chi gia lap SES)")
        st, m1 = call("POST", "/me/report/email", token=token, body={})
        check("POST /me/report/email -> 200", st == 200, f"status={st}")
        check("sent = true", m1.get("sent") is True, json.dumps(m1)[:90])
        check("Dia chi tra ve bi CHE", m1.get("to", "").count("*") >= 3, str(m1.get("to")))

        # Cooldown: bam lan hai KHONG gui them thu
        st, m2 = call("POST", "/me/report/email", token=token, body={})
        check("Bam lan hai -> sent=false, reason=cooldown",
              m2.get("sent") is False and m2.get("reason") == "cooldown",
              json.dumps(m2)[:90])
        check("Co retryAfter de giao dien noi con bao lau",
              isinstance(m2.get("retryAfter"), int) and m2["retryAfter"] > 0,
              str(m2.get("retryAfter")))

        # ⚠️ Tuan RONG thi KHONG gui thu — phep kiem quan trong nhat cua muc nay
        st, m3 = call("POST", "/me/report/email?week=40", token=token, body={})
        check("Tuan RONG -> sent=false, reason=empty",
              m3.get("sent") is False and m3.get("reason") == "empty",
              json.dumps(m3)[:90])

        # ── [9] uid trong body/query bi bo qua ──
        print("\n[9] Khong doc uid tu client")
        st, dz = call("GET", "/me/report?uid=nguoi-khac", token=token)
        check("uid trong query bi bo qua", st == 200 and dz.get("child") == "Bin",
              str(dz.get("child")))

        # ── [11] Cau SAI -> cot "con vuong chu de nao" ──
        # ⚠️ Truoc 09/08/2026 cau sai KHONG duoc luu o dau ca: `PROGRESS.terms` chi
        #    nhan cau DUNG (no la chia khoa mo So Tay), con bo dem thi chi co tong so.
        print("\n[11] Cau tra loi SAI -> bao cao chu de")
        st, pr0 = call("GET", "/me/achievements", token=token)
        terms_before = set((pr0.get("progress") or {}).get("terms") or [])

        st, _ = call("POST", "/me/progress", token=token, body={
            "type": "quiz", "correct": 2, "total": 5, "opId": uuid.uuid4().hex,
            "terms": ["star", "comet-what"],
            "wrong": ["black-hole", "gravity", "nebula"]})
        check("POST /me/progress nhan `wrong` -> 200", st == 200, f"status={st}")
        time.sleep(1)

        st, d = call("GET", "/me/report", token=token)
        tm = {x["term"]: x for x in (d["current"].get("terms") or [])}
        check("Bao cao co day du 5 khoa cua luot vua roi",
              all(k in tm for k in ("star", "comet-what", "black-hole", "gravity", "nebula")),
              str(sorted(tm.keys()))[:110])
        check("Khoa DUNG dem vao `ok`", tm.get("star", {}).get("ok") == 1
              and tm.get("star", {}).get("wrong") == 0, json.dumps(tm.get("star")))
        check("Khoa SAI dem vao `wrong`", tm.get("gravity", {}).get("wrong") == 1
              and tm.get("gravity", {}).get("ok") == 0, json.dumps(tm.get("gravity")))
        check("weakCount = 3", d["current"]["weakCount"] == 3, str(d["current"]["weakCount"]))
        # Chu de sai nhieu nhat len truoc — do la thu phu huynh mo bao cao de tim
        first = (d["current"].get("terms") or [{}])[0]
        check("Chu de CAN LUYEN xep len truoc", first.get("wrong", 0) > 0,
              json.dumps(first))

        # ⚠️⚠️ PHEP KIEM QUAN TRONG NHAT CUA MUC NAY
        st, pr1 = call("GET", "/me/achievements", token=token)
        terms_after = set((pr1.get("progress") or {}).get("terms") or [])
        check("Cau SAI KHONG mo the So Tay (khong vao PROGRESS.terms)",
              not ({"black-hole", "gravity", "nebula"} & terms_after),
              str(sorted(terms_after - terms_before)))
        check("Cau DUNG VAN mo the So Tay", {"star", "comet-what"} <= terms_after,
              str(sorted(terms_after - terms_before)))

        # SS that su duoc ghi xuong DynamoDB, khong chi song trong bo nho
        hist = [r for r in rows(uid) if r["SK"]["S"].startswith("HIST#")
                and "wrong" in r]
        check("Dong nhat ky co string set `wrong`", len(hist) >= 1, f"{len(hist)} dong")
        if hist:
            ss = set(hist[-1]["wrong"]["SS"])
            check("SS `wrong` dung noi dung", ss == {"black-hole", "gravity", "nebula"},
                  str(sorted(ss)))

        # ⚠️ KEP theo `total - correct`: dung het thi khong the co cau sai nao
        st, _ = call("POST", "/me/progress", token=token, body={
            "type": "quiz", "correct": 5, "total": 5, "opId": uuid.uuid4().hex,
            "wrong": ["supernova", "cmb", "exoplanet", "meteor", "asteroid-what"]})
        time.sleep(1)
        st, d = call("GET", "/me/report", token=token)
        tm2 = {x["term"]: x for x in (d["current"].get("terms") or [])}
        check("Dung het ma khai co cau sai -> BI BO QUA",
              "supernova" not in tm2 and d["current"]["weakCount"] == 3,
              f'weak={d["current"]["weakCount"]}')

        # Mot cau khong the vua dung vua sai trong cung mot luot
        st, _ = call("POST", "/me/progress", token=token, body={
            "type": "quiz", "correct": 1, "total": 2, "opId": uuid.uuid4().hex,
            "terms": ["meteor"], "wrong": ["meteor", "meteorite"]})
        time.sleep(1)
        st, d = call("GET", "/me/report", token=token)
        tm3 = {x["term"]: x for x in (d["current"].get("terms") or [])}
        check("Khoa gui o CA HAI ben chi tinh la DUNG",
              tm3.get("meteor", {}).get("ok") == 1 and tm3.get("meteor", {}).get("wrong") == 0,
              json.dumps(tm3.get("meteor")))
        check("Khoa sai con lai van duoc ghi", tm3.get("meteorite", {}).get("wrong") == 1,
              json.dumps(tm3.get("meteorite")))

        # Khoa rac / khoang trang bi loai, khong lam hong ca dong nhat ky
        st, dz = call("POST", "/me/progress", token=token, body={
            "type": "quiz", "correct": 0, "total": 2, "opId": uuid.uuid4().hex,
            "wrong": ["   ", "", "x" * 200]})
        check("Khoa rac -> van 200, khong lam hong lo ghi nhat ky",
              dz.get("counted") is True, f"status={st}")

        # ── [10] Cat tuan dau tai ngay dang ky ──
        # ⚠️ Tuan lich van la don vi (T2–CN gio VN), NHUNG tuan dang ky bi cat tai
        #    ngay tao tai khoan. Khong cat thi phu huynh doc "1/7" cho mot tuan chi
        #    dai 2 ngay va hieu la con luoi hoc — dung cach doc sai ma viec cat sinh
        #    ra de tranh. Do tren TUAN TRUOC vi no chi co dung MOT dong nhat ky
        #    (gieo o muc [5]) nen ket qua khong phu thuoc hom nay la thu may.
        print("\n[10] Cat cua so tuan tai ngay dang ky")
        pmon = monday_vn(1)
        st, d = call("GET", "/me/report", token=token)
        check("Moc dang ky cu -> tuan nay KHONG bi cat",
              d["current"]["partial"] is False and d["current"]["days"] == 7,
              f'partial={d["current"]["partial"]} days={d["current"]["days"]}')

        # a) Dang ky thu Ba tuan truoc -> cat con 6 ngay, viec thu Tu VAN duoc tinh
        seed_profile(uid, email, created=pmon + timedelta(days=1))
        st, d = call("GET", "/me/report?week=1", token=token)
        c1 = d["current"]
        check("Dang ky giua tuan -> partial = true", c1["partial"] is True, str(c1["partial"]))
        check("days = 6 (thu Ba -> het Chu nhat)", c1["days"] == 6, str(c1["days"]))
        check("Viec SAU ngay dang ky van duoc tinh",
              c1["empty"] is False and c1["accuracy"] == 60,
              f'empty={c1["empty"]} acc={c1["accuracy"]}')

        # b) Dang ky thu Nam -> viec thu Tu (TRUOC ngay dang ky) bi loai khoi cua so
        seed_profile(uid, email, created=pmon + timedelta(days=3))
        st, d = call("GET", "/me/report?week=1", token=token)
        c2 = d["current"]
        check("days = 4 (thu Nam -> het Chu nhat)", c2["days"] == 4, str(c2["days"]))
        check("Viec TRUOC ngay dang ky bi loai khoi cua so", c2["empty"] is True,
              f'empty={c2["empty"]} rounds={c2["quizRounds"]}')
        # ⚠️ Khong lam bai nao thi accuracy phai la null, khong phai 0
        check("accuracy van la null (khong phai 0)", c2["accuracy"] is None,
              repr(c2["accuracy"]))

        # c) Dang ky dau tuan NAY -> ca tuan truoc nam TRUOC ngay dang ky
        mon0 = monday_vn(0)
        seed_profile(uid, email, created=mon0)
        st, d = call("GET", "/me/report?week=1", token=token)
        c3 = d["current"]
        check("Ca tuan nam truoc ngay dang ky -> days = 0", c3["days"] == 0, str(c3["days"]))
        check("... va partial = true (khac han 'chua ghi duoc gi')",
              c3["partial"] is True, str(c3["partial"]))
        check("... va empty = true", c3["empty"] is True, str(c3["empty"]))
        # Dang ky DUNG dau tuan nay -> bien tren khong tinh la cat
        st, d0 = call("GET", "/me/report", token=token)
        c0 = d0["current"]
        check("Dang ky dung dau tuan -> tuan nay tron 7 ngay, khong cat",
              c0["days"] == 7 and c0["partial"] is False,
              f'days={c0["days"]} partial={c0["partial"]}')

        # d) Tuan nam truoc ngay dang ky thi KHONG gui thu
        st, m4 = call("POST", "/me/report/email?week=1", token=token, body={})
        check("Tuan truoc ngay dang ky -> sent=false, reason=empty",
              m4.get("sent") is False and m4.get("reason") == "empty",
              json.dumps(m4)[:90])

    finally:
        print("\n[don] Xoa du lieu test")
        if uid:
            n = wipe(uid)
            print(f"  Da xoa {n} dong DynamoDB")
            check("Khong con dong nao sot", len(rows(uid)) == 0)
        if token:
            check("Da xoa tai khoan Firebase tam", _fbtest.delete(token))

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
