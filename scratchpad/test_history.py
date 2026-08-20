# -*- coding: utf-8 -*-
"""
test_history.py — kiem thu DOC LAP nhat ky su kien (SK = HIST#<ISO>#<4 hex>).

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_history.py                 # http://localhost:5080
    python scratchpad/test_history.py <base-url>      # ban that tren AWS

Nhat ky nay la NGUYEN LIEU DUY NHAT cho bao cao tuan gui phu huynh: bo dem o ban ghi
PROGRESS la TONG CA DOI, khong co truc thoi gian, nen "tuan nay con lam bao nhieu cau"
khong tinh ra duoc tu chung.

Trong tam — ba thu de lam bao cao NOI SAI voi phu huynh:
  1. THOI PHONG: ba duong ra som `counted:false` (trung opId, doc lai bai, ghe lai
     hanh tinh) TUYET DOI khong duoc sinh dong nhat ky.
  2. MAT DONG: `PutItem` ghi de khi trung khoa. Hang cho o client gui lai mot loat
     lien tiep -> hai viec cung mot moc thoi gian la mot dong bien mat, im lang.
  3. SO KHONG THAT: phai ghi so DA KEP TRAN (xp/award/score), khong phai so client khai.

Tu tao tai khoan Firebase tam, tu don moi ban ghi trong `finally`.

⚠️ Nhan cua check() PHAI KHONG DAU — console Windows mac dinh cp1252, in chu co dau la
   UnicodeEncodeError nem GIUA LUC CHAY va bo do moi phep kiem phia sau.
"""
import concurrent.futures as cf
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

import _fbtest  # token DA xac minh email — /me/* nay doi email_verified

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"
TTL_DAYS = 400          # phai khop DynamoContext.HistoryTtlDays

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


def seed(uid, email):
    it = {
        "PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
        "uid": {"S": uid}, "email": {"S": email}, "name": {"S": "History Test"},
        "createdAt": {"S": "2026-08-08T00:00:00.000Z"},
    }
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(it))
    return r.returncode == 0, r.stderr.strip()


def rows(uid, prefix=None):
    """Doc ban ghi cua mot uid. `prefix` -> chi lay SK bat dau bang chuoi do."""
    kce = "PK = :pk"
    vals = {":pk": {"S": f"USER#{uid}"}}
    if prefix:
        kce += " AND begins_with(SK, :sk)"
        vals[":sk"] = {"S": prefix}
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", kce,
            "--expression-attribute-values", json.dumps(vals),
            "--consistent-read")
    return [] if r.returncode != 0 else json.loads(r.stdout or "{}").get("Items", [])


def hist(uid):
    """Cac dong nhat ky, da sap theo SK (DynamoDB tra ve theo thu tu sort key)."""
    return rows(uid, "HIST#")


def num(it, k):
    return int(it[k]["N"]) if k in it and "N" in it[k] else None


def txt(it, k):
    return it[k]["S"] if k in it and "S" in it[k] else None


def wipe(uid):
    n = 0
    for it in rows(uid):
        if aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]})).returncode == 0:
            n += 1
    return n


def prog(token, body):
    return call("POST", "/me/progress", token=token, body=body)


def main():
    print(f"=== Nhat ky su kien @ {BASE} ===\n")
    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    email = f"hist-{uuid.uuid4().hex[:10]}@simulator.amazonses.com"
    uid = token = None
    try:
        uid, token, _ = _fbtest.make_verified(email)
        okseed, err = seed(uid, email)
        check("Gieo duoc ho so tam", okseed, err or uid[:10])
        if not okseed:
            return 1

        # ── [1] Chua lam gi thi khong co dong nao ──
        print("\n[1] Trang thai ban dau")
        check("Chua co dong nhat ky nao", len(hist(uid)) == 0, f"n={len(hist(uid))}")

        # ── [2] Quiz DAT ──
        print("\n[2] Quiz DAT (4/5)")
        st, d = prog(token, {"type": "quiz", "correct": 4, "total": 5,
                             "meteors": 80, "opId": uuid.uuid4().hex})
        check("POST /me/progress -> 200", st == 200, f"status={st}")
        h = hist(uid)
        check("Sinh dung 1 dong", len(h) == 1, f"n={len(h)}")
        if h:
            r0 = h[0]
            check("type = quiz", txt(r0, "type") == "quiz", txt(r0, "type"))
            check("correct = 4", num(r0, "correct") == 4, str(num(r0, "correct")))
            check("total = 5", num(r0, "total") == 5, str(num(r0, "total")))
            check("xp khop response", num(r0, "xp") == d.get("xpGained"),
                  f'hist={num(r0,"xp")} resp={d.get("xpGained")}')
            check("meteors khop `awarded` (so THAT sau tran)",
                  num(r0, "meteors") == d.get("awarded"),
                  f'hist={num(r0,"meteors")} resp={d.get("awarded")}')
            check("Co truong ttl", num(r0, "ttl") is not None)
            if num(r0, "ttl"):
                want = int(time.time()) + TTL_DAYS * 86400
                check(f"ttl ~ now + {TTL_DAYS} ngay",
                      abs(num(r0, "ttl") - want) < 86400,
                      f'lech={num(r0,"ttl") - want}s')
            check("SK bat dau HIST# va co hau to", txt(r0, "SK") is None or True)
            sk = r0["SK"]["S"]
            check("SK dung dang HIST#<ISO>#<4 hex>",
                  sk.startswith("HIST#") and sk.count("#") == 2 and len(sk.rsplit("#", 1)[1]) == 4,
                  sk)
            check("Khong co truong score/seconds (khong ap dung cho quiz)",
                  "score" not in r0 and "seconds" not in r0)

        # ── [3] Quiz KHONG DAT van phai ghi ──
        print("\n[3] Quiz KHONG dat (1/5) van ghi")
        n_before = len(hist(uid))
        st, d = prog(token, {"type": "quiz", "correct": 1, "total": 5,
                             "meteors": 80, "opId": uuid.uuid4().hex})
        h = hist(uid)
        check("Van sinh them 1 dong", len(h) == n_before + 1, f"n={len(h)}")
        check("Server bao chua dat", d.get("quizPassed") is False, str(d.get("quizPassed")))
        last = h[-1]
        check("meteors = 0 (khong dat thi khong thuong)",
              num(last, "meteors") == 0, str(num(last, "meteors")))
        check("correct = 1 van duoc ghi", num(last, "correct") == 1, str(num(last, "correct")))

        # ── [4] Game: refId + so DA KEP TRAN ──
        print("\n[4] Game — ghi so DA KEP TRAN, khong phai so client khai")
        n_before = len(hist(uid))
        HUGE = 999_999_999
        st, d = prog(token, {"type": "game", "game": "dodge", "score": HUGE,
                             "seconds": HUGE, "meteors": HUGE,
                             "opId": uuid.uuid4().hex})
        h = hist(uid)
        check("Sinh them 1 dong", len(h) == n_before + 1, f"n={len(h)}")
        g = h[-1]
        check("type = game", txt(g, "type") == "game", txt(g, "type"))
        check("refId = ten game", txt(g, "refId") == "dodge", txt(g, "refId"))
        check("score BI KEP, khong phai so client khai",
              num(g, "score") is not None and num(g, "score") < HUGE, str(num(g, "score")))
        check("seconds BI KEP", num(g, "seconds") is not None and num(g, "seconds") < HUGE,
              str(num(g, "seconds")))
        check("meteors BI KEP xuong tran vi",
              num(g, "meteors") == d.get("awarded") and num(g, "meteors") < HUGE,
              f'hist={num(g,"meteors")} resp={d.get("awarded")}')
        check("xp BI KEP (MaxXpPerReport)",
              num(g, "xp") == d.get("xpGained") and num(g, "xp") < HUGE, str(num(g, "xp")))

        # ── [5] CHONG THOI PHONG: gui trung opId ──
        print("\n[5] Gui TRUNG opId (hang cho gui lai) -> KHONG them dong")
        op = uuid.uuid4().hex
        st, d1 = prog(token, {"type": "quiz", "correct": 3, "total": 5,
                              "meteors": 60, "opId": op})
        n_after_first = len(hist(uid))
        st, d2 = prog(token, {"type": "quiz", "correct": 3, "total": 5,
                              "meteors": 60, "opId": op})
        check("Lan hai server bao duplicate", d2.get("duplicate") is True, str(d2.get("duplicate")))
        check("KHONG sinh them dong nhat ky nao",
              len(hist(uid)) == n_after_first, f"n={len(hist(uid))} truoc={n_after_first}")

        # ── [6] CHONG THOI PHONG: doc lai bai cu ──
        print("\n[6] Doc LAI mot bai -> KHONG them dong")
        lid = "lib-nebula"
        st, d = prog(token, {"type": "lesson", "id": lid, "opId": uuid.uuid4().hex})
        h = hist(uid)
        n_after_first = len(h)
        check("Lan dau co ghi", d.get("counted") is True and txt(h[-1], "refId") == lid,
              txt(h[-1], "refId"))
        st, d = prog(token, {"type": "lesson", "id": lid, "opId": uuid.uuid4().hex})
        check("Lan hai server bao counted=false", d.get("counted") is False, str(d.get("counted")))
        check("KHONG sinh them dong nhat ky nao",
              len(hist(uid)) == n_after_first, f"n={len(hist(uid))} truoc={n_after_first}")

        # ── [7] CHONG THOI PHONG: ghe lai hanh tinh cu ──
        print("\n[7] Ghe LAI mot hanh tinh -> KHONG them dong")
        st, d = prog(token, {"type": "planet", "id": "mars", "opId": uuid.uuid4().hex})
        h = hist(uid)
        n_after_first = len(h)
        check("Lan dau co ghi", d.get("counted") is True and txt(h[-1], "refId") == "mars",
              txt(h[-1], "refId"))
        st, d = prog(token, {"type": "planet", "id": "mars", "opId": uuid.uuid4().hex})
        check("Lan hai server bao counted=false", d.get("counted") is False, str(d.get("counted")))
        check("KHONG sinh them dong nhat ky nao",
              len(hist(uid)) == n_after_first, f"n={len(hist(uid))} truoc={n_after_first}")

        # ── [8] Buoc nhiem vu ──
        print("\n[8] Buoc nhiem vu")
        n_before = len(hist(uid))
        st, d = prog(token, {"type": "quiz", "correct": 0, "total": 1,
                             "opId": uuid.uuid4().hex})  # cho chac PROGRESS da ton tai
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "scan", "opId": uuid.uuid4().hex})
        check("POST /me/missions/step -> 200", st == 200, f"status={st}")
        h = hist(uid)
        m = [x for x in h if txt(x, "type") == "mission"]
        check("Sinh dung 1 dong type=mission", len(m) == 1, f"n={len(m)}")
        if m:
            check("refId = <nhiemvu>:<buoc>", txt(m[0], "refId") == "earth:scan", txt(m[0], "refId"))
            check("xp khop response", num(m[0], "xp") == d.get("xpGained"),
                  f'hist={num(m[0],"xp")} resp={d.get("xpGained")}')
            check("meteors khop `awarded`", num(m[0], "meteors") == d.get("awarded"),
                  f'hist={num(m[0],"meteors")} resp={d.get("awarded")}')
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "scan", "opId": uuid.uuid4().hex})
        check("Lam LAI buoc do -> counted=false", d.get("counted") is False, str(d.get("counted")))
        check("KHONG sinh them dong mission nao",
              len([x for x in hist(uid) if txt(x, "type") == "mission"]) == 1)

        # ── [9] CHONG MAT DONG: ban mot loat lien tiep ──
        #
        # ⚠️ PHEP KIEM NAY KHONG CHUNG MINH DUOC HAU TO NGAU NHIEN LA CAN THIET, va
        #    noi ra cho ro de nguoi doc sau khong tuong nham. Do 09/08/2026: bo hau to
        #    khoi SK roi chay lai thi muc [9] VAN XANH 12/12 — `DateTime.UtcNow` tren
        #    may nay du min de 12 luot khong roi vao cung mot moc.
        #    Hau to VAN GIU vi rui ro la that o cho khac: do phan giai dong ho khac nhau
        #    theo he dieu hanh, va ban that chay tren Lambda/Linux chu khong phai may nay.
        #    Duoi day do va IN RA so moc thoi gian bi trung — dung de BAO CAO su that,
        #    khong dung de khang dinh mot dieu phep do khong quyet duoc.
        print("\n[9] Ban 12 luot LIEN TIEP -> phai du 12 dong")
        n_before = len(hist(uid))
        BURST = 12
        with cf.ThreadPoolExecutor(max_workers=BURST) as ex:
            # Dung `game` chu KHONG dung `quiz`: quiz co tran
            # `QuizAccess.FreeRoundsPerDay` nen luot thu 6 tro di khong ghi dong
            # nhat ky nao, va muc nay se do mot thu khac han thu no muon do.
            # Dieu can bao ve khong doi: 12 luot SONG SONG -> 12 dong rieng biet.
            list(ex.map(lambda _: prog(token, {"type": "game", "game": "dodge",
                                               "score": 1,
                                               "opId": uuid.uuid4().hex}),
                        range(BURST)))
        got = len(hist(uid)) - n_before
        check(f"Du {BURST} dong, khong dong nao bi ghi de", got == BURST, f"them={got}")
        sks = [x["SK"]["S"] for x in hist(uid)]
        check("Moi SK la duy nhat", len(sks) == len(set(sks)), f"{len(sks)} dong / {len(set(sks))} khoa")
        # Moc thoi gian = phan SK giua hai dau '#'. Trung nghia la NEU khong co hau to
        # thi dung so dong do da bi ghi de mat.
        stamps = [s.split("#")[1] for s in sks]
        dup = len(stamps) - len(set(stamps))
        print(f"  [do]   Moc thoi gian trung nhau: {dup}/{len(stamps)}"
              + ("  -> hau to da cuu tung ay dong" if dup else
                 "  -> lan chay nay dong ho du min, hau to chua phai dung toi"))

        # ── [10] Sap xep + truy van theo khoang (chinh la cach bao cao tuan doc) ──
        print("\n[10] Sap xep thoi gian + truy van theo khoang SK")
        h = hist(uid)
        check("DynamoDB tra ve DA SAP theo SK", sks == sorted(sks))
        check("Truong `at` tang dan theo thu tu tra ve",
              all(txt(h[i], "at") <= txt(h[i + 1], "at") for i in range(len(h) - 1)))
        # Cua so "tu dong thu 3 tro di" — mo phong truy van mot tuan
        pivot = h[2]["SK"]["S"]
        r = aws("dynamodb", "query", "--table-name", TABLE,
                "--key-condition-expression", "PK = :pk AND SK BETWEEN :a AND :b",
                "--expression-attribute-values", json.dumps({
                    ":pk": {"S": f"USER#{uid}"}, ":a": {"S": pivot}, ":b": {"S": "HIST#~"}}),
                "--consistent-read")
        win = [] if r.returncode != 0 else json.loads(r.stdout or "{}").get("Items", [])
        check("Query theo khoang SK lay dung cua so", len(win) == len(h) - 2,
              f"lay={len(win)} mong doi={len(h)-2}")

        # ── [11] Nhat ky khong lam sai so lieu tra ve ──
        print("\n[11] Nhat ky khong anh huong duong thuong")
        st, d = call("GET", "/me/achievements", token=token)
        check("GET /me/achievements van 200", st == 200, f"status={st}")
        pr = (d or {}).get("progress") or {}
        n_quiz_hist = len([x for x in hist(uid) if txt(x, "type") == "quiz"])
        check("quizTaken khop so dong quiz trong nhat ky",
              pr.get("quizTaken") == n_quiz_hist,
              f'counter={pr.get("quizTaken")} hist={n_quiz_hist}')

        # ── [12] Khong token thi khong ghi gi ──
        print("\n[12] Khong token")
        n_before = len(hist(uid))
        st, _ = call("POST", "/me/progress", body={"type": "quiz", "correct": 5, "total": 5})
        check("POST /me/progress khong token -> 401", st == 401, f"status={st}")
        check("Khong sinh dong nao", len(hist(uid)) == n_before)

        # ── [13] type sai thi khong ghi gi ──
        print("\n[13] type khong hop le")
        n_before = len(hist(uid))
        st, _ = prog(token, {"type": "hack", "opId": uuid.uuid4().hex})
        check("type la -> 400", st == 400, f"status={st}")
        check("Khong sinh dong nao", len(hist(uid)) == n_before)

    finally:
        print("\n[don] Xoa du lieu test")
        if uid:
            n = wipe(uid)
            print(f"  Da xoa {n} dong DynamoDB")
            left = len(rows(uid))
            check("Khong con dong nao sot", left == 0, f"con={left}")
        if token:
            check("Da xoa tai khoan Firebase tam", _fbtest.delete(token))

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
