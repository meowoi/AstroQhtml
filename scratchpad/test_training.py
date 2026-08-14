# -*- coding: utf-8 -*-
"""Kiem tra API tien do Trung Tam Dao Tao (`training` trong GET /me/achievements).

CHAY DOC LAP TRUOC KHI NOI VAO GIAO DIEN (quy tac 4 muc 6 cua CLAUDE.md).

  py -3 scratchpad/test_training.py                 # backend o may (localhost:5080)
  py -3 scratchpad/test_training.py --prod          # ban that tren AWS

⚠️ LUAT DOC THANG TU `Services/Training.cs`, khong go tay lai o day. Test go
   cung con so thi no khang dinh mot trang thai CU va se bao hong dung luc ai do
   chinh mocs cho dung — day la lop loi da mac 6 lan trong du an (14 icon · 14
   thuat ngu · 25 cau · 20 mau vat · 5 buoc · 2 loai mon).
"""
import sys, os, re, json, time, subprocess, urllib.request, urllib.error
# Console Windows mac dinh cp1252 — in chu co dau la UnicodeEncodeError GIUA bai
# test, mat luon phan don du lieu o `finally`. Bai hoc da ghi trong CLAUDE.md.
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _fbtest

TABLE = "astroq-main"

def aws(*a):
    return subprocess.run(("aws",) + a, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")

def wipe(uid):
    """Xoa moi ban ghi cua uid trong bang. Tra ve so dong da xoa."""
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": f"USER#{uid}"}}),
            "--consistent-read")
    if r.returncode != 0: return 0
    n = 0
    for it in json.loads(r.stdout or "{}").get("Items", []):
        if aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]})).returncode == 0:
            n += 1
    return n

PROD = "--prod" in sys.argv
BASE = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com" if PROD else "http://localhost:5080"
SRC  = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "AstroqSV", "src", "AstroqSV.Api", "Services", "Training.cs")

ok = bad = 0
def ck(name, cond, detail=""):
    global ok, bad
    if cond: ok += 1; print(f"  [OK]   {name}")
    else:    bad += 1; print(f"  [HONG] {name}   {detail}")

def call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token: req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try: return e.code, json.loads(raw)
        except Exception: return e.code, {"_raw": raw[:200]}

# ─────────────────── [1] Doc luat tu Training.cs ───────────────────
print("\n[1] Doc luat thang tu Services/Training.cs")
src = open(SRC, encoding="utf-8").read()
# Bo comment de khong dem nham vi du trong ghi chu
nc = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
nc = re.sub(r"//[^\n]*", " ", nc)

blocks = re.findall(r'new\("([a-z]+)",\s*new\[\]\s*\{(.*?)\}\)', nc, re.S)
LAW = {}
for key, body in blocks:
    courses = re.findall(r'new Course\("([a-z-]+)",\s*"([^"]+)",\s*(\d+)\)', body)
    LAW[key] = [(g, m, int(goal)) for g, m, goal in courses]

ck("boc duoc chuong trinh tu Training.cs", len(LAW) > 0, str(LAW))
if not LAW:
    print("\n>>> Khong doc duoc luat — DUNG, moi phep kiem sau deu vo nghia.")
    sys.exit(1)
print(f"       {len(LAW)} chuong trinh: " + ", ".join(f"{k}({len(v)})" for k, v in LAW.items()))
ck("moi chuong trinh co it nhat 1 khoa hoc", all(len(v) >= 1 for v in LAW.values()))
ck("moi khoa hoc dung metric best:<game>",
   all(m == f"best:{g}" for v in LAW.values() for g, m, _ in v),
   str([(g, m) for v in LAW.values() for g, m, _ in v]))
ck("moc deu > 0", all(goal > 0 for v in LAW.values() for _, _, goal in v))
# Khong game nao thuoc hai chuong trinh (mot game hai cho = hai noi noi hai dieu)
games = [g for v in LAW.values() for g, _, _ in v]
ck("khong game nao thuoc 2 chuong trinh", len(games) == len(set(games)), str(games))

# ─────────────────── [2] Tai khoan moi ───────────────────
print("\n[2] Tai khoan moi — chua dat chuong trinh nao")
mail = f"trn-{int(time.time())}@simulator.amazonses.com"
uid, token, _pw = _fbtest.make_verified(mail)
print(f"       uid={uid}")

try:
    st, r = call("GET", "/me/achievements", token)
    ck("GET /me/achievements 200", st == 200, str(st))
    tr = r.get("training")
    ck("response CO khoi `training`", tr is not None, str(list(r.keys())))
    ck("total khop so chuong trinh khai o server", tr and tr.get("total") == len(LAW),
       f'{tr and tr.get("total")} vs {len(LAW)}')
    ck("chua dat chuong trinh nao", tr and tr.get("passed") == 0, str(tr and tr.get("passed")))
    progs = {p["key"]: p for p in (tr or {}).get("programs", [])}
    ck("du ten chuong trinh", set(progs) == set(LAW), f"{set(progs)} vs {set(LAW)}")
    ck("moi khoa hoc current=0, passed=false",
       all(c["current"] == 0 and c["passed"] is False for p in progs.values() for c in p["courses"]))
    ck("moc goal tra ve khop Training.cs",
       all(c["goal"] == dict((g, gl) for g, _, gl in LAW[k])[c["game"]]
           for k, p in progs.items() for c in p["courses"]))

    def report(game, score, extra=None):
        b = {"type": "game", "game": game, "score": score, "seconds": 5,
             "meteors": 0, "opId": f"op-{game}-{score}-{int(time.time()*1000)}"}
        if extra: b.update(extra)
        return call("POST", "/me/progress", token, b)

    def training():
        _, rr = call("GET", "/me/achievements", token)
        t = rr["training"]
        return t, {p["key"]: p for p in t["programs"]}

    # ─────────── [3] Mot khoa dat KHONG lam ca chuong trinh dat ───────────
    print("\n[3] Chuong trinh nhieu khoa: dat 1 khoa thi CHUA dat chuong trinh")
    multi = [k for k, v in LAW.items() if len(v) >= 2]
    if not multi:
        ck("co it nhat 1 chuong trinh nhieu khoa de thu", False, "khong co")
    else:
        k = multi[0]
        g0, _, goal0 = LAW[k][0]
        st, _ = report(g0, goal0)
        ck(f"bao diem {g0}={goal0} → 200", st == 200, str(st))
        t, progs = training()
        ck(f"khoa {g0} da dat", progs[k]["courses"][0]["passed"] is True)
        ck(f"chuong trinh {k} CHUA dat (con khoa khac)", progs[k]["passed"] is False)
        ck(f"{k} hien done=1/{len(LAW[k])}", progs[k]["done"] == 1)
        ck("tong passed van = 0", t["passed"] == 0, str(t["passed"]))

        # ─────────── [4] Dat not khoa con lai ───────────
        print("\n[4] Dat not khoa con lai → chuong trinh DAT")
        for g, _, goal in LAW[k][1:]:
            report(g, goal)
        t, progs = training()
        ck(f"chuong trinh {k} DA dat", progs[k]["passed"] is True)
        ck("tong passed = 1", t["passed"] == 1, str(t["passed"]))

    # ─────────── [5] Diem duoi moc thi khong dat ───────────
    print("\n[5] Diem DUOI moc thi khong dat")
    rest = [k for k in LAW if k not in (multi[:1] if multi else [])]
    k1 = rest[0]; g1, _, goal1 = LAW[k1][0]
    if goal1 > 1:
        report(g1, goal1 - 1)
        _, progs = training()
        ck(f"{g1}={goal1-1} (thieu 1) → CHUA dat", progs[k1]["passed"] is False)
        ck("current hien dung so that", progs[k1]["courses"][0]["current"] == goal1 - 1,
           str(progs[k1]["courses"][0]["current"]))
    else:
        ck(f"(bo qua: moc cua {g1} = 1, khong co so duoi moc)", True)

    # ─────────── [6] KEP current ve goal ───────────
    print("\n[6] `current` bi KEP ve goal — khong hien 999999/150")
    report(g1, 999999)
    _, progs = training()
    c = progs[k1]["courses"][0]
    ck("current khong vuot goal", c["current"] == c["goal"], f'{c["current"]} vs {c["goal"]}')
    ck("va da dat", c["passed"] is True)

    # ─────────── [7] Ky luc khong bao gio TUT ───────────
    print("\n[7] Bao diem THAP hon ky luc khong lam mat chuong trinh")
    report(g1, 0)
    _, progs = training()
    ck(f"{k1} van dat sau khi bao diem 0", progs[k1]["passed"] is True)

    # ─────────── [8] Client KHONG tu dat duoc chuong trinh ───────────
    print("\n[8] Client gui `training` len → BI BO QUA")
    k2 = [k for k in LAW if k not in (multi[:1] if multi else []) and k != k1][0]
    st, _ = call("POST", "/me/progress", token, {
        "type": "game", "game": "dodge", "score": 1, "seconds": 1, "meteors": 0,
        "opId": f"op-fake-{int(time.time()*1000)}",
        "training": {"passed": 99, "programs": [{"key": k2, "passed": True}]},
        "bests": {g: 999999 for g in games},
    })
    ck("van 200 (truong la bi bo qua, khong bao loi)", st == 200, str(st))
    _, progs = training()
    ck(f"chuong trinh {k2} VAN chua dat", progs[k2]["passed"] is False)
    ck("khong chuong trinh nao dat bang cach gui bests",
       sum(1 for p in progs.values() if p["passed"]) <= 2, str({k: p["passed"] for k, p in progs.items()}))

    # ─────────── [9] Dat het moi chuong trinh ───────────
    print("\n[9] Dat het → passed == total")
    for k, v in LAW.items():
        for g, _, goal in v: report(g, goal)
    t, progs = training()
    ck("moi chuong trinh dat", all(p["passed"] for p in progs.values()),
       str({k: p["passed"] for k, p in progs.items()}))
    ck("passed == total", t["passed"] == t["total"] == len(LAW), f'{t["passed"]}/{t["total"]}')

    # ─────────── [10] Khong co duong GHI rieng ───────────
    print("\n[10] Khong ton tai route ghi `training`")
    for m in ("POST", "PUT", "PATCH"):
        st, _ = call(m, "/me/training", token, {"passed": 5})
        ck(f"{m} /me/training khong ton tai ({st})", st in (404, 405), str(st))
    st, _ = call("GET", "/me/training", token)
    ck(f"GET /me/training cung khong ton tai ({st})", st in (404, 405), str(st))

    # ─────────── [11] Khong token ───────────
    print("\n[11] Khong token → 401")
    st, _ = call("GET", "/me/achievements")
    ck("GET /me/achievements khong token → 401", st == 401, str(st))

finally:
    print("\n[don] xoa du lieu test")
    try:
        n = wipe(uid)
        print(f"       xoa {n} dong DynamoDB")
    except Exception as e:
        print(f"       ⚠️ con dong DynamoDB: {e}")
    try:
        _fbtest.delete(token)
        print("       xoa tai khoan Firebase tam")
    except Exception as e:
        print(f"       ⚠️ con tai khoan Firebase: {e}")

print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
