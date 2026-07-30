# -*- coding: utf-8 -*-
"""
test_missions.py — kiểm thử ĐỘC LẬP /me/missions và /me/missions/step.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_missions.py                 # http://localhost:5080
    python scratchpad/test_missions.py <base-url>      # bản thật trên AWS

Trọng tâm — nhiệm vụ là chỗ thưởng KHÔNG THỂ BỊA:
  1. Client chỉ gửi {mission, step}; gửi kèm số tiền/XP thì bị BỎ QUA hoàn toàn.
  2. Mỗi bước chỉ tính MỘT LẦN, kể cả khi gọi song song.
  3. Xong bước cuối mới chốt nhiệm vụ: +100 tt, mở huy hiệu, tính là đã ghé Trái Đất.
  4. Gửi lại (hàng chờ khi mất mạng) không cộng thưởng lần hai — nhờ opId.
"""
import concurrent.futures as cf
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
API_KEY = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
IDP = "https://identitytoolkit.googleapis.com/v1/accounts"
TABLE = "astroq-main"

STEPS = ["scan", "sun", "rotation", "life", "core"]
# Khớp Services/Missions.cs
REWARD = {"scan": (0, 20), "sun": (20, 30), "rotation": (20, 30),
          "life": (20, 40), "core": (20, 40)}
DONE_METEORS, DONE_XP = 100, 120

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


def mis(token):
    return call("GET", "/me/missions", token=token)[1].get("missions", {}).get("earth", {})


def main():
    print(f"=== Nhiem vu 01 @ {BASE} ===\n")
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
        m = mis(token)
        check("Co nhiem vu 'earth'", bool(m), str(list(m)))
        check("Du 5 buoc, dung thu tu", m.get("steps") == STEPS, str(m.get("steps")))
        check("Chua xong buoc nao", m.get("doneSteps") == [], str(m.get("doneSteps")))
        check("Chua hoan thanh", m.get("done") is False, str(m.get("done")))
        check("Chua co mau du lieu nao", m.get("codex") == [], str(m.get("codex")))
        check("Tong so mau du lieu = 6", m.get("codexTotal") == 6, str(m.get("codexTotal")))
        check("Bao truoc mo khoa 'moon'", m.get("unlocks") == "moon", str(m.get("unlocks")))
        check("Vi van 0", bal(token) == 0, str(bal(token)))

        print("\n[4] Du lieu vao sai")
        for body, code in (({"mission": "khong-co-that", "step": "scan"}, "bad-mission"),
                           ({"step": "scan"}, "bad-mission"),
                           ({"mission": "earth", "step": "khong-co-that"}, "bad-step"),
                           ({"mission": "earth"}, "bad-step"),
                           ({"mission": "earth", "step": "sc an"}, "bad-step")):
            st, d = call("POST", "/me/missions/step", token=token, body=body)
            check(f"{json.dumps(body)} -> 400 {code}",
                  st == 400 and d.get("code") == code, f"{st} {d.get('code')}")
        check("Sai du lieu vao thi KHONG ghi gi", mis(token).get("doneSteps") == [])

        print("\n[5] Client gui so tien/XP len -> BI BO QUA")
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "scan",
                           "meteors": 99999, "xp": 99999, "awarded": 99999,
                           "missionDone": True, "badges": ["level-20"]})
        check("Buoc 'scan' -> 200", st == 200, f"{st}")
        check("Thuong dung bang cua SERVER (scan = 0 tt)", d.get("awarded") == 0,
              f"awarded={d.get('awarded')}")
        check("XP dung bang cua SERVER (scan = 20 XP)", d.get("xpGained") == 20,
              f"xp={d.get('xpGained')}")
        check("Vi van 0 (khong cong 99999)", d["wallet"]["meteors"] == 0,
              str(d["wallet"]))
        check("KHONG chot nhiem vu theo yeu cau cua client",
              d.get("missionDone") is False and d["missions"]["earth"]["done"] is False,
              str(d.get("missionDone")))
        check("KHONG mo huy hieu level-20", "level-20" not in d.get("newBadges", []),
              str(d.get("newBadges")))

        print("\n[6] Moi buoc chi tinh MOT lan")
        b0 = bal(token)
        xp0 = d["level"]["xp"]
        st, d2 = call("POST", "/me/missions/step", token=token,
                      body={"mission": "earth", "step": "scan"})
        check("Lam lai 'scan' -> counted=false", d2.get("counted") is False,
              str(d2.get("counted")))
        check("Khong cong tien", d2["wallet"]["meteors"] == b0, str(d2["wallet"]))
        check("Khong cong XP", d2["level"]["xp"] == xp0, f"{xp0} -> {d2['level']['xp']}")
        check("doneSteps van dung 1 buoc", d2["missions"]["earth"]["doneSteps"] == ["scan"],
              str(d2["missions"]["earth"]["doneSteps"]))

        print("\n[7] Buoc 'sun' -> +20 tt + mau du lieu Mat Troi")
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "sun"})
        check("Thuong 20 tt", d.get("awarded") == 20, f"awarded={d.get('awarded')}")
        check("XP 30", d.get("xpGained") == 30, f"xp={d.get('xpGained')}")
        check("Vi = 20", d["wallet"]["meteors"] == 20, str(d["wallet"]))
        check("Codex co 'sun'", d["missions"]["earth"]["codex"] == ["sun"],
              str(d["missions"]["earth"]["codex"]))

        print("\n[8] Buoc 'rotation' + 'life' (life cho 4 mau mot luot)")
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "rotation"})
        check("rotation: +20 tt, codex co 'rotation'",
              d.get("awarded") == 20 and "rotation" in d["missions"]["earth"]["codex"],
              str(d["missions"]["earth"]["codex"]))
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "life"})
        codex = d["missions"]["earth"]["codex"]
        check("life: cho DU 4 the (water/forest/animal/mountain)",
              set(["water", "forest", "animal", "mountain"]).issubset(set(codex)), str(codex))
        check("Tong 6 mau du lieu = 100%", len(codex) == 6, f"{len(codex)}/6")
        check("Van CHUA hoan thanh (con buoc 'core')",
              d["missions"]["earth"]["done"] is False, str(d["missions"]["earth"]["done"]))
        check("Chua mo huy hieu rookie-astronaut",
              not any(b["id"] == "rookie-astronaut" and b["earned"]
                      for b in call("GET", "/me/achievements", token=token)[1]
                      ["achievements"]["badges"]))
        b_before = d["wallet"]["meteors"]
        xp_before = d["level"]["xp"]
        check("Vi = 60 sau 3 buoc co thuong", b_before == 60, str(b_before))

        print("\n[9] Buoc CUOI -> chot nhiem vu: +20+100 tt, huy hieu, ghe Trai Dat")
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "core"})
        check("missionDone = true", d.get("missionDone") is True, str(d.get("missionDone")))
        check("Thuong = 20 (buoc) + 100 (chot) = 120", d.get("awarded") == 120,
              f"awarded={d.get('awarded')}")
        check("XP = 40 + 120 = 160", d.get("xpGained") == 160, f"xp={d.get('xpGained')}")
        check("Vi = 60 + 120 = 180", d["wallet"]["meteors"] == b_before + 120,
              str(d["wallet"]))
        check("XP tang dung 160", d["level"]["xp"] == xp_before + 160,
              f"{xp_before} -> {d['level']['xp']}")
        check("Mo huy hieu rookie-astronaut",
              "rookie-astronaut" in d.get("newBadges", []), str(d.get("newBadges")))
        check("Bao mo khoa 'moon'", d.get("unlocks") == "moon", str(d.get("unlocks")))
        check("Hoan thanh nhiem vu = da ghe Trai Dat",
              "earth" in d["progress"]["planets"], str(d["progress"]["planets"]))
        check("Mo luon huy hieu planet-1 (ghe hanh tinh dau tien)",
              "planet-1" in d.get("newBadges", []), str(d.get("newBadges")))
        m = mis(token)
        check("done = true + co doneAt", m.get("done") is True and bool(m.get("doneAt")),
              str(m.get("doneAt")))
        check("doneSteps du 5 buoc", sorted(m.get("doneSteps", [])) == sorted(STEPS),
              str(m.get("doneSteps")))
        check("'done' KHONG bi tinh la mot buoc", "done" not in m.get("doneSteps", []))

        print("\n[10] Xong roi lam lai -> khong cong them gi")
        b1 = bal(token)
        st, d = call("POST", "/me/missions/step", token=token,
                     body={"mission": "earth", "step": "core"})
        check("counted=false", d.get("counted") is False, str(d.get("counted")))
        check("Vi khong doi", bal(token) == b1, f"{b1} -> {bal(token)}")
        check("missionDone khong bao lai", d.get("missionDone") is False,
              str(d.get("missionDone")))

        print("\n[11] opId — gui lai KHONG cong thuong lan hai")
        wipe(uid)
        ok, err = seed(uid, email)
        check("Reset tai khoan de thu opId", ok, err)
        op = "m-" + uuid.uuid4().hex[:12]
        st, e1 = call("POST", "/me/missions/step", token=token,
                      body={"mission": "earth", "step": "sun", "opId": op})
        check("Lan 1: +20 tt", e1.get("awarded") == 20 and e1["wallet"]["meteors"] == 20,
              str(e1["wallet"]))
        st, e2 = call("POST", "/me/missions/step", token=token,
                      body={"mission": "earth", "step": "sun", "opId": op})
        check("Gui lai cung opId -> duplicate, khong cong",
              e2.get("duplicate") is True and e2["wallet"]["meteors"] == 20, str(e2))
        st, e3 = call("POST", "/me/missions/step", token=token,
                      body={"mission": "earth", "step": "sun", "opId": op + "-khac"})
        check("opId khac, cung buoc -> van khong cong (buoc da xong)",
              e3.get("counted") is False and e3["wallet"]["meteors"] == 20, str(e3["wallet"]))

        print("\n[12] Goi SONG SONG cung mot buoc -> chi 1 lan duoc thuong")
        wipe(uid)
        ok, _ = seed(uid, email)
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            futs = [ex.submit(call, "POST", "/me/missions/step", token,
                              {"mission": "earth", "step": "rotation"}) for _ in range(6)]
            res = [f.result() for f in futs]
        counted = [d for st_, d in res if st_ == 200 and d.get("counted") is True]
        check("Dung 1 loi goi duoc tinh", len(counted) == 1,
              f"{len(counted)} loi goi counted=true")
        check("Vi chi cong 20 mot lan", bal(token) == 20, str(bal(token)))
        check("doneSteps chi co 'rotation'", mis(token).get("doneSteps") == ["rotation"],
              str(mis(token).get("doneSteps")))

        print("\n[13] uid trong body/query bi bo qua")
        st, d = call("POST", "/me/missions/step?uid=nguoi-khac", token=token,
                     body={"mission": "earth", "step": "scan", "uid": "nguoi-khac"})
        check("Van ghi vao ho so CUA MINH", st == 200
              and "scan" in d["missions"]["earth"]["doneSteps"], str(d.get("missions")))
        check("Khong tao ban ghi cho uid la", len(rows("nguoi-khac")) == 0)

        print("\n[14] Nhiem vu xuat hien o /me/profile va /me/achievements")
        st, prof = call("GET", "/me/profile", token=token)
        check("/me/profile co progress.missions.earth",
              "earth" in (prof.get("progress", {}).get("missions") or {}),
              str(list((prof.get("progress", {}).get("missions") or {}))))
        st, ach = call("GET", "/me/achievements", token=token)
        rook = [b for b in ach["achievements"]["badges"] if b["id"] == "rookie-astronaut"]
        check("Huy hieu rookie-astronaut co trong danh sach", len(rook) == 1, str(rook))
        check("Nhom huy hieu la 'mission'", rook and rook[0]["group"] == "mission",
              str(rook[0]["group"]) if rook else "")
        check("Chua xong nhiem vu -> current 0/1",
              rook and rook[0]["current"] == 0 and rook[0]["goal"] == 1, str(rook))

        print("\n[15] Method khong ho tro")
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
