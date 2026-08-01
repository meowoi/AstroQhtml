# -*- coding: utf-8 -*-
"""
test_missions.py — kiểm thử ĐỘC LẬP /me/missions và /me/missions/step.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_missions.py                 # http://localhost:5080
    python scratchpad/test_missions.py <base-url>      # bản thật trên AWS

Trọng tâm — nhiệm vụ là chỗ thưởng KHÔNG THỂ BỊA:
  1. Client chỉ gửi {mission, step}; gửi kèm số tiền/XP thì bị BỎ QUA hoàn toàn.
  2. Mỗi bước chỉ tính MỘT LẦN, kể cả khi gọi song song.
  3. Xong bước cuối mới chốt nhiệm vụ: thưởng bó, mở huy hiệu, tính là đã ghé Trái Đất.
  4. Gửi lại (hàng chờ khi mất mạng) không cộng thưởng lần hai — nhờ opId.
  5. CỔNG LỘ TRÌNH (docs/decisions/003): 70% bước → mở điểm đến kế tiếp. Client không
     tự tính, và không lách được bằng cách làm lại MỘT bước nhiều lần.

⚠️ MỌI CON SỐ ĐỀU ĐỌC TỪ `Services/Missions.cs` + `Services/Wallet.cs`, KHÔNG GÁN CỨNG.
   Bản trước của file này gán cứng "5 bước" và "codexTotal = 6" từ thời nhiệm vụ còn 5
   bước; ngày 29/07/2026 nhiệm vụ lên 8 bước và bộ test này **hỏng lặng lẽ** — nó khẳng
   định đúng một trạng thái không còn tồn tại. Đây là lần thứ SÁU dự án gặp lỗi "gán cứng
   con số mà nơi khác mới là nguồn sự thật" (14 icon · 14 thuật ngữ · 25 câu · 20 mẫu vật
   · 5 bước). Cách sửa đúng là hỏi ĐIỀU MÌNH MUỐN BIẾT, đọc từ nguồn sự thật.
"""
import concurrent.futures as cf
import json
import math
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
API_KEY = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
IDP = "https://identitytoolkit.googleapis.com/v1/accounts"
TABLE = "astroq-main"

HERE = os.path.dirname(os.path.abspath(__file__))
SV = os.path.normpath(os.path.join(HERE, "..", "..", "AstroqSV", "src", "AstroqSV.Api"))

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


# ═════════════════ ĐỌC LUẬT TỪ SERVER (nguồn sự thật duy nhất) ═════════════════

def read(*parts):
    with open(os.path.join(SV, *parts), encoding="utf-8") as f:
        return f.read()


def parse_rules():
    """Bóc luật nhiệm vụ ra khỏi Services/Missions.cs + Services/Wallet.cs."""
    src = read("Services", "Missions.cs")

    # Bước: new("scan", 0, 20, null) — đòi 2 SỐ ở giữa nên KHÔNG khớp dòng khai nhiệm vụ
    # `new("earth", "earth",` (đối số thứ hai là chuỗi).
    steps = re.findall(r'new\("(\w+)",\s*(\d+),\s*(\d+),\s*(null|"[^"]*")\)', src)
    if not steps:
        print("KHONG doc duoc buoc nao tu Missions.cs — dung lai"
              " (khong de test 'dat' mot cach rong).")
        sys.exit(1)

    r = {
        "steps": [s[0] for s in steps],
        "reward": {s[0]: (int(s[1]), int(s[2])) for s in steps},
        "codex": {s[0]: ([] if s[3] == "null"
                         else [c.strip() for c in s[3].strip('"').split(",") if c.strip()])
                  for s in steps},
    }
    r["codex_total"] = sum(len(v) for v in r["codex"].values())

    def one(pat, where=None, cast=int):
        m = re.search(pat, src if where is None else where)
        if not m:
            print(f"KHONG doc duoc {pat!r} — dung lai.")
            sys.exit(1)
        return cast(m.group(1))

    r["done_meteors"] = one(r"DoneMeteors:\s*(\d+)")
    r["done_xp"] = one(r"DoneXp:\s*(\d+)")
    r["unlocks"] = one(r'Unlocks:\s*"(\w+)"', cast=str)
    r["ratio"] = one(r"UnlockRatio\s*=\s*([\d.]+)", cast=float)

    route = re.search(r"Route\s*=\s*\[([^\]]*)\]", src)
    if not route:
        print("KHONG doc duoc Missions.Route — dung lai.")
        sys.exit(1)
    r["route"] = re.findall(r'"(\w+)"', route.group(1))

    # Cổng suy ra ĐÚNG như server: ceil(số bước × tỉ lệ).
    r["gate"] = math.ceil(len(r["steps"]) * r["ratio"])
    r["cap_step"] = one(r"MaxPerMissionStep\s*=\s*(\d+)",
                        read("Services", "Wallet.cs"))
    return r


R = parse_rules()
STEPS = R["steps"]
GATE = R["gate"]


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


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True, timeout=60)


def seed(uid, email, meteors=0):
    for it in (
        {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"}, "uid": {"S": uid},
         "email": {"S": email}, "name": {"S": "Mission Test"},
         "createdAt": {"S": "2026-07-29T00:00:00.000Z"}},
        {"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
         "meteors": {"N": str(meteors)}, "diamonds": {"N": "0"}},
    ):
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


def bal(token):
    return call("GET", "/me/wallet", token=token)[1].get("meteors")


def full(token):
    """Cả khối /me/missions — `route`/`unlockedPlaces` nằm ở cấp GỐC, không trong `missions`."""
    return call("GET", "/me/missions", token=token)[1]


def mis(token):
    return full(token).get("missions", {}).get("earth", {})


def step(token, sid, **extra):
    body = {"mission": "earth", "step": sid}
    body.update(extra)
    return call("POST", "/me/missions/step", token=token, body=body)


def main():
    print(f"=== Nhiem vu 01 @ {BASE} ===")
    print(f"    Luat doc tu Missions.cs: {len(STEPS)} buoc {STEPS}")
    print(f"    Cong lo trinh: ceil({len(STEPS)} x {R['ratio']}) = {GATE} buoc"
          f" · lo trinh {R['route']}")
    print(f"    Mau du lieu: {R['codex_total']} · chot nhiem vu:"
          f" +{R['done_meteors']} tt / +{R['done_xp']} XP\n")

    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    print("\n[1] Khong co token")
    for m, p in (("GET", "/me/missions"), ("POST", "/me/missions/step")):
        st, _ = call(m, p, body={} if m == "POST" else None)
        check(f"{m} {p} -> 401", st == 401, f"status={st}")
    st, _ = call("GET", "/me/missions", token="khong-phai-jwt")
    check("token rac -> 401", st == 401, f"status={st}")

    email = f"mission-test-{uuid.uuid4().hex[:10]}@astroq-test.invalid"
    print(f"\n[2] Tao tai khoan tam: {email}")
    acc = idp("signUp", {"email": email, "password": "Test" + uuid.uuid4().hex[:8],
                         "returnSecureToken": True})
    uid, token = acc["localId"], acc["idToken"]
    check("Co idToken + uid", bool(uid and token), f"uid={uid}")

    try:
        ok, err = seed(uid, email)
        check("Tao ho so + vi rong", ok, err)

        print("\n[3] Trang thai ban dau")
        f = full(token)
        m = f.get("missions", {}).get("earth", {})
        check("Co nhiem vu 'earth'", bool(m), str(list(f.get("missions", {}))))
        check("Bo buoc khop Missions.cs, DUNG THU TU",
              m.get("steps") == STEPS, str(m.get("steps")))
        check("Chua xong buoc nao", m.get("doneSteps") == [], str(m.get("doneSteps")))
        check("Chua hoan thanh", m.get("done") is False, str(m.get("done")))
        check("Chua co mau du lieu nao", m.get("codex") == [], str(m.get("codex")))
        check(f"Tong so mau du lieu = {R['codex_total']}",
              m.get("codexTotal") == R["codex_total"], str(m.get("codexTotal")))
        check(f"Bao truoc mo khoa '{R['unlocks']}'",
              m.get("unlocks") == R["unlocks"], str(m.get("unlocks")))
        check("Vi van 0", bal(token) == 0, str(bal(token)))

        print("\n[3b] CONG LO TRINH — trang thai ban dau (docs/decisions/003)")
        check(f"gate = {GATE} (server tu suy tu so buoc, khong gan cung)",
              m.get("gate") == GATE, f"gate={m.get('gate')}")
        check("gateMet = false khi chua lam gi", m.get("gateMet") is False,
              str(m.get("gateMet")))
        check(f"route = {R['route']} (khop Missions.Route)",
              f.get("route") == R["route"], str(f.get("route")))
        check(f"Chi mo diem den dau tien ['{R['route'][0]}']",
              f.get("unlockedPlaces") == [R["route"][0]], str(f.get("unlockedPlaces")))
        check(f"Diem den thu hai '{R['route'][1]}' CHUA mo",
              R["route"][1] not in (f.get("unlockedPlaces") or []),
              str(f.get("unlockedPlaces")))

        print("\n[4] Du lieu vao sai")
        for body, code in (({"mission": "khong-co-that", "step": STEPS[0]}, "bad-mission"),
                           ({"step": STEPS[0]}, "bad-mission"),
                           ({"mission": "earth", "step": "khong-co-that"}, "bad-step"),
                           ({"mission": "earth"}, "bad-step"),
                           ({"mission": "earth", "step": "sc an"}, "bad-step")):
            st, d = call("POST", "/me/missions/step", token=token, body=body)
            check(f"{json.dumps(body)} -> 400 {code}",
                  st == 400 and d.get("code") == code, f"{st} {d.get('code')}")
        check("Sai du lieu vao thi KHONG ghi gi", mis(token).get("doneSteps") == [])

        print("\n[5] Client gui so tien/XP/cong len -> BI BO QUA")
        s0 = STEPS[0]
        want_tt, want_xp = R["reward"][s0]
        st, d = step(token, s0, meteors=99999, xp=99999, awarded=99999,
                     missionDone=True, badges=["level-20"],
                     gate=0, gateMet=True, unlockedPlaces=["earth", "moon", "mars"])
        check(f"Buoc '{s0}' -> 200", st == 200, f"{st}")
        check(f"Thuong dung bang SERVER ({s0} = {want_tt} tt)",
              d.get("awarded") == want_tt, f"awarded={d.get('awarded')}")
        check(f"XP dung bang SERVER ({s0} = {want_xp} XP)",
              d.get("xpGained") == want_xp, f"xp={d.get('xpGained')}")
        check("Vi khong nhan 99999", d["wallet"]["meteors"] == want_tt, str(d["wallet"]))
        check("KHONG chot nhiem vu theo yeu cau cua client",
              d.get("missionDone") is False and d["missions"]["earth"]["done"] is False,
              str(d.get("missionDone")))
        check("KHONG mo huy hieu level-20", "level-20" not in d.get("newBadges", []),
              str(d.get("newBadges")))
        f = full(token)
        check("Client gui gate=0 -> server VAN giu gate cua minh",
              f["missions"]["earth"]["gate"] == GATE,
              str(f["missions"]["earth"]["gate"]))
        check("Client gui gateMet=true -> BI BO QUA",
              f["missions"]["earth"]["gateMet"] is False,
              str(f["missions"]["earth"]["gateMet"]))
        check("Client gui unlockedPlaces -> BI BO QUA",
              f.get("unlockedPlaces") == [R["route"][0]], str(f.get("unlockedPlaces")))

        print("\n[6] Moi buoc chi tinh MOT lan")
        b0, xp0 = bal(token), d["level"]["xp"]
        st, d2 = step(token, s0)
        check(f"Lam lai '{s0}' -> counted=false", d2.get("counted") is False,
              str(d2.get("counted")))
        check("Khong cong tien", d2["wallet"]["meteors"] == b0, str(d2["wallet"]))
        check("Khong cong XP", d2["level"]["xp"] == xp0, f"{xp0} -> {d2['level']['xp']}")
        check("doneSteps van dung 1 buoc",
              d2["missions"]["earth"]["doneSteps"] == [s0],
              str(d2["missions"]["earth"]["doneSteps"]))

        print(f"\n[6b] KHONG LACH CONG DUOC BANG CACH LAM LAI MOT BUOC {GATE + 2} lan")
        for _ in range(GATE + 2):
            step(token, s0)
        f = full(token)
        check(f"Lam lai '{s0}' {GATE + 2} lan -> gateMet VAN false",
              f["missions"]["earth"]["gateMet"] is False,
              str(f["missions"]["earth"]["gateMet"]))
        check("doneSteps van dung 1 buoc", f["missions"]["earth"]["doneSteps"] == [s0],
              str(f["missions"]["earth"]["doneSteps"]))
        check("Diem den thu hai van khoa",
              f.get("unlockedPlaces") == [R["route"][0]], str(f.get("unlockedPlaces")))

        print("\n[7] Choi lan luot tung buoc — thuong khop bang cua server")
        wipe(uid)
        ok, _ = seed(uid, email)
        tt_run = 0
        gate_seen_at = None
        for i, sid in enumerate(STEPS, start=1):
            want_tt, want_xp = R["reward"][sid]
            last = (i == len(STEPS))
            st, d = step(token, sid)
            exp_tt = want_tt + (R["done_meteors"] if last else 0)
            exp_xp = want_xp + (R["done_xp"] if last else 0)
            tt_run += min(exp_tt, R["cap_step"])
            check(f"buoc {i}/{len(STEPS)} '{sid}': +{exp_tt} tt / +{exp_xp} XP",
                  d.get("awarded") == exp_tt and d.get("xpGained") == exp_xp,
                  f"awarded={d.get('awarded')} xp={d.get('xpGained')}")
            me = d["missions"]["earth"]
            check(f"  doneSteps = {i} buoc", len(me["doneSteps"]) == i,
                  str(me["doneSteps"]))
            for c in R["codex"][sid]:
                check(f"  codex nhan '{c}'", c in me["codex"], str(me["codex"]))
            if me["gateMet"] and gate_seen_at is None:
                gate_seen_at = i
            check(f"  gateMet = {i >= GATE}", me["gateMet"] is (i >= GATE),
                  f"i={i} gate={GATE} gateMet={me['gateMet']}")

        check(f"gateMet bat len DUNG o buoc thu {GATE}", gate_seen_at == GATE,
              f"bat o buoc {gate_seen_at}")
        check(f"Vi cong dung tong {tt_run} tt", bal(token) == tt_run, str(bal(token)))
        m = mis(token)
        check(f"Du {R['codex_total']} mau du lieu = 100%",
              len(m["codex"]) == R["codex_total"],
              f"{len(m['codex'])}/{R['codex_total']}")
        check("done = true + co doneAt",
              m.get("done") is True and bool(m.get("doneAt")), str(m.get("doneAt")))
        check("doneSteps du bo buoc", sorted(m.get("doneSteps", [])) == sorted(STEPS),
              str(m.get("doneSteps")))
        check("'done' KHONG bi tinh la mot buoc", "done" not in m.get("doneSteps", []))
        check("Hoan thanh nhiem vu = da ghe Trai Dat",
              "earth" in call("GET", "/me/profile", token=token)[1]
              .get("progress", {}).get("planets", []))
        check("Mo huy hieu rookie-astronaut",
              any(b["id"] == "rookie-astronaut" and b["earned"]
                  for b in call("GET", "/me/achievements", token=token)[1]
                  ["achievements"]["badges"]))

        print("\n[7b] CONG LO TRINH sau khi xong het")
        f = full(token)
        check(f"Mo dung {len(R['route'])} diem den {R['route']}",
              f.get("unlockedPlaces") == R["route"], str(f.get("unlockedPlaces")))
        check("KHONG mo qua lo trinh (Route la tran)",
              len(f.get("unlockedPlaces") or []) == len(R["route"]),
              str(f.get("unlockedPlaces")))
        check("Dung lai o diem den CHUA CO nhiem vu"
              " (khong hua nhiem vu chua ton tai)",
              (f.get("unlockedPlaces") or [None])[-1] == R["route"][-1],
              str(f.get("unlockedPlaces")))

        print("\n[8] Xong roi lam lai -> khong cong them gi")
        b1 = bal(token)
        st, d = step(token, STEPS[-1])
        check("counted=false", d.get("counted") is False, str(d.get("counted")))
        check("Vi khong doi", bal(token) == b1, f"{b1} -> {bal(token)}")
        check("missionDone khong bao lai", d.get("missionDone") is False,
              str(d.get("missionDone")))

        print("\n[9] opId — gui lai KHONG cong thuong lan hai")
        wipe(uid)
        ok, err = seed(uid, email)
        check("Reset tai khoan de thu opId", ok, err)
        paid = next(s for s in STEPS if R["reward"][s][0] > 0)   # bước CÓ thưởng tt
        want_tt = R["reward"][paid][0]
        op = "m-" + uuid.uuid4().hex[:12]
        st, e1 = step(token, paid, opId=op)
        check(f"Lan 1: +{want_tt} tt",
              e1.get("awarded") == want_tt and e1["wallet"]["meteors"] == want_tt,
              str(e1["wallet"]))
        st, e2 = step(token, paid, opId=op)
        check("Gui lai cung opId -> duplicate, khong cong",
              e2.get("duplicate") is True and e2["wallet"]["meteors"] == want_tt, str(e2))
        st, e3 = step(token, paid, opId=op + "-khac")
        check("opId khac, cung buoc -> van khong cong (buoc da xong)",
              e3.get("counted") is False and e3["wallet"]["meteors"] == want_tt,
              str(e3["wallet"]))

        print("\n[10] Goi SONG SONG cung mot buoc -> chi 1 lan duoc thuong")
        wipe(uid)
        ok, _ = seed(uid, email)
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            futs = [ex.submit(step, token, paid) for _ in range(6)]
            res = [f_.result() for f_ in futs]
        counted = [d for st_, d in res if st_ == 200 and d.get("counted") is True]
        check("Dung 1 loi goi duoc tinh", len(counted) == 1,
              f"{len(counted)} loi goi counted=true")
        check(f"Vi chi cong {want_tt} mot lan", bal(token) == want_tt, str(bal(token)))
        check(f"doneSteps chi co '{paid}'", mis(token).get("doneSteps") == [paid],
              str(mis(token).get("doneSteps")))

        print("\n[11] uid trong body/query bi bo qua")
        st, d = call("POST", "/me/missions/step?uid=nguoi-khac", token=token,
                     body={"mission": "earth", "step": STEPS[0], "uid": "nguoi-khac"})
        check("Van ghi vao ho so CUA MINH", st == 200
              and STEPS[0] in d["missions"]["earth"]["doneSteps"], str(d.get("missions")))
        check("Khong tao ban ghi cho uid la", len(rows("nguoi-khac")) == 0)

        print("\n[12] Nhiem vu xuat hien o /me/profile va /me/achievements")
        st, prof = call("GET", "/me/profile", token=token)
        check("/me/profile co progress.missions.earth",
              "earth" in (prof.get("progress", {}).get("missions") or {}),
              str(list((prof.get("progress", {}).get("missions") or {}))))
        st, ach = call("GET", "/me/achievements", token=token)
        rook = [b for b in ach["achievements"]["badges"] if b["id"] == "rookie-astronaut"]
        check("Huy hieu rookie-astronaut co trong danh sach", len(rook) == 1, str(rook))
        check("Nhom huy hieu la 'mission'", bool(rook) and rook[0]["group"] == "mission",
              str(rook[0]["group"]) if rook else "")
        check("Chua xong nhiem vu -> current 0/1",
              bool(rook) and rook[0]["current"] == 0 and rook[0]["goal"] == 1, str(rook))

        print("\n[13] Method khong ho tro")
        st, _ = call("DELETE", "/me/missions/step", token=token)
        check("DELETE -> 404/405", st in (404, 405), f"status={st}")

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
