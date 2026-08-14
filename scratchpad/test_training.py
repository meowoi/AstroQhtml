# -*- coding: utf-8 -*-
"""Kiem tra API tien do Trung Tam Dao Tao (`training` trong GET /me/achievements).

CHAY DOC LAP TRUOC KHI NOI VAO GIAO DIEN (quy tac 4 muc 6 cua CLAUDE.md).

  py -3 scratchpad/test_training.py                 # backend o may (localhost:5080)
  py -3 scratchpad/test_training.py --prod          # ban that tren AWS

⚠️ LUAT DOC THANG TU `Services/Training.cs`, khong go tay lai o day. Test go
   cung con so thi no khang dinh mot trang thai CU va se bao hong dung luc ai do
   chinh moc cho dung — day la lop loi da mac 6 lan trong du an.

⚠️⚠️ TU 14/08/2026 MOI KHOA HOC CO MOT **THANG MOC** chu khong phai mot moc.
   Ly do doi: mot huy hieu "DA DAT" la mot dau cham het, trong khi ca khu sinh ra
   de tre LUYEN LAI qua nhieu cap. Bo test nay vi the phai chung minh duoc:
     · len cap dung theo tung moc, khong nhay coc
     · cap cua CHUONG TRINH = cap THAP NHAT trong cac khoa hoc
     · o cap cao nhat thi `next` la null (khong bao gio hua mot cap khong co)
     · client khong tu dat cap duoc
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
print("\n[1] Doc thang moc thang tu Services/Training.cs")
src = open(SRC, encoding="utf-8").read()
nc = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)     # bo comment khoi
nc = re.sub(r"//[^\n]*", " ", nc)                    # bo comment dong

blocks = re.findall(r'new\("([a-z]+)",\s*new\[\]\s*\{(.*?)\n        \}\)', nc, re.S)
LAW = {}
for key, body in blocks:
    cs = re.findall(r'new Course\("([a-z-]+)",\s*"([^"]+)",\s*new long\[\]\s*\{([^}]*)\}\)', body)
    LAW[key] = [(g, m, [int(x) for x in re.findall(r"\d+", goals)]) for g, m, goals in cs]

ck("boc duoc chuong trinh tu Training.cs", len(LAW) > 0, str(list(LAW)))
if not LAW:
    print("\n>>> Khong doc duoc luat — DUNG, moi phep kiem sau deu vo nghia.")
    sys.exit(1)
print("       " + ", ".join(f"{k}[{'+'.join(g for g,_,_ in v)}]" for k, v in LAW.items()))

ck("moi chuong trinh co it nhat 1 khoa hoc", all(len(v) >= 1 for v in LAW.values()))
ck("moi khoa hoc co NHIEU moc (thang cap, khong phai dat/chua)",
   all(len(goals) >= 2 for v in LAW.values() for _, _, goals in v),
   str({k: [len(g) for _, _, g in v] for k, v in LAW.items()}))
ck("moc trong moi thang TANG DAN",
   all(goals == sorted(goals) and len(set(goals)) == len(goals)
       for v in LAW.values() for _, _, goals in v))
ck("moc deu > 0", all(g > 0 for v in LAW.values() for _, _, goals in v for g in goals))
# Moi chuong trinh cung so cap thi cap moi so sanh duoc voi nhau
lv_counts = {k: min(len(g) for _, _, g in v) for k, v in LAW.items()}
ck("moi chuong trinh cung so cap", len(set(lv_counts.values())) == 1, str(lv_counts))
MAXLV = list(lv_counts.values())[0]
games = [g for v in LAW.values() for g, _, _ in v]
ck("khong game nao thuoc 2 chuong trinh", len(games) == len(set(games)), str(games))

# ─────────────────── [2] Tai khoan moi ───────────────────
print("\n[2] Tai khoan moi — chua co cap nao")
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
    ck("chua co cap nao", tr and tr.get("levels") == 0, str(tr and tr.get("levels")))
    ck("maxLevels = so chuong trinh x so cap",
       tr and tr.get("maxLevels") == len(LAW) * MAXLV,
       f'{tr and tr.get("maxLevels")} vs {len(LAW)*MAXLV}')

    # ⚠️ TRUONG `passed` PHAI BIEN MAT. Con no la giao dien co the ve lai huy hieu
    #    "DA DAT" — dung cai dau cham het ma lan sua nay di bo.
    ck("KHONG con truong `passed` o chuong trinh",
       all("passed" not in p for p in tr["programs"]),
       str([p for p in tr["programs"] if "passed" in p][:1]))

    progs = {p["key"]: p for p in tr["programs"]}
    ck("du ten chuong trinh", set(progs) == set(LAW), f"{set(progs)} vs {set(LAW)}")
    ck("moi chuong trinh level=0", all(p["level"] == 0 for p in progs.values()))
    ck("moc KE TIEP la moc dau tien cua thang",
       all(c["next"] == dict((g, gs) for g, _, gs in LAW[k])[c["game"]][0]
           for k, p in progs.items() for c in p["courses"]),
       str([(k, c["game"], c["next"]) for k, p in progs.items() for c in p["courses"]][:3]))

    # ⚠️ CHUONG TRINH QUAN SAT DUNG CHI SO `consts` (so chom sao KHAC NHAU), khong
    #    phai `best:constellation` — game do bao `score:1` cung va co mot huy hieu
    #    dua vao no nen khong doi duoc. Nghia la bao diem THOI KHONG DU: phai gui
    #    kem `id` cua chom sao, va moi lan mot chom KHAC.
    #    (Lan dau viet bo test toi quen chuyen nay va no bao hong 3 phep kiem —
    #     loi cua phep do, khong phai cua san pham.)
    SKY = ["ursa-major", "cassiopeia", "orion", "scorpius"]
    _cn = [0]

    def report(game, score, extra=None):
        b = {"type": "game", "game": game, "score": score, "seconds": 5,
             "meteors": 0, "opId": f"op-{game}-{score}-{int(time.time()*1000000)}"}
        if game == "constellation":
            # Moi lan mot chom KHAC → `consts` moi tang. Gui trung id thi no dung yen,
            # va do chinh la dieu chi so nay muon do: da NGAM DUOC BAO NHIEU CHOM.
            b["id"] = SKY[min(_cn[0], len(SKY) - 1)]; _cn[0] += 1
        if extra: b.update(extra)
        return call("POST", "/me/progress", token, b)

    def training():
        _, rr = call("GET", "/me/achievements", token)
        t = rr["training"]
        return t, {p["key"]: p for p in t["programs"]}

    # ─────────── [3] Len cap TUNG BUOC, khong nhay coc ───────────
    print("\n[3] Len cap tung buoc theo thang moc")
    k1 = [k for k, v in LAW.items() if len(v) == 1][0]     # chuong trinh 1 khoa
    g1, _, goals1 = LAW[k1][0]
    for i, goal in enumerate(goals1):
        report(g1, goal)
        _, progs = training()
        got = progs[k1]["level"]
        ck(f"{g1}={goal} → Cap {i+1}", got == i + 1, f"ra Cap {got}")

    # ─────────── [4] Cap cao nhat: `next` phai la null ───────────
    print("\n[4] Cap cao nhat → khong hua mot cap khong ton tai")
    _, progs = training()
    ck(f"{k1} da toi da ({MAXLV})", progs[k1]["level"] == MAXLV, str(progs[k1]["level"]))
    ck("`next` = null o cap cao nhat",
       all(c["next"] is None for c in progs[k1]["courses"]),
       str([c["next"] for c in progs[k1]["courses"]]))
    ck("`maxLevel` van tra ve dung", progs[k1]["maxLevel"] == MAXLV)

    # ─────────── [5] Diem DUOI moc thi khong len cap ───────────
    print("\n[5] Diem duoi moc thi khong len cap")
    k2 = [k for k in LAW if k != k1 and len(LAW[k]) == 1][0]
    g2, _, goals2 = LAW[k2][0]
    if goals2[0] > 1:
        report(g2, goals2[0] - 1)
        _, progs = training()
        ck(f"{g2}={goals2[0]-1} (thieu 1) → van Cap 0", progs[k2]["level"] == 0,
           str(progs[k2]["level"]))
        ck("current hien dung so that", progs[k2]["courses"][0]["current"] == goals2[0] - 1,
           str(progs[k2]["courses"][0]["current"]))
    else:
        ck(f"(bo qua: moc dau cua {g2} = 1)", True)

    # ─────────── [6] Cap CHUONG TRINH = cap THAP NHAT cua cac khoa ───────────
    print("\n[6] Chuong trinh nhieu khoa: lay cap THAP NHAT")
    km = [k for k, v in LAW.items() if len(v) >= 2][0]
    ga, _, goalsa = LAW[km][0]
    gb, _, goalsb = LAW[km][1]
    report(ga, goalsa[-1])                       # khoa A len cap toi da
    _, progs = training()
    ck(f"{ga} toi da nhung chuong trinh {km} VAN Cap 0",
       progs[km]["level"] == 0, str(progs[km]["level"]))
    ck("khoa A that su da toi da",
       progs[km]["courses"][0]["level"] == len(goalsa), str(progs[km]["courses"][0]["level"]))
    report(gb, goalsb[0])                        # khoa B len cap 1
    _, progs = training()
    ck(f"{gb} len Cap 1 → chuong trinh {km} len Cap 1",
       progs[km]["level"] == 1, str(progs[km]["level"]))

    # ─────────── [7] `current` bi KEP, ky luc tho van co ───────────
    print("\n[7] `current` kep ve moc ke tiep, `best` giu ky luc tho")
    report(g2, 999999)
    _, progs = training()
    c = progs[k2]["courses"][0]
    ck("best giu nguyen so tho", c["best"] == 999999, str(c["best"]))
    ck("current KHONG vuot moc cuoi", c["current"] <= goals2[-1], f'{c["current"]}')
    ck("va da len cap toi da", progs[k2]["level"] == MAXLV, str(progs[k2]["level"]))

    # ─────────── [8] Ky luc khong TUT ───────────
    print("\n[8] Bao diem thap hon khong lam TUT cap")
    report(g2, 0)
    _, progs = training()
    ck(f"{k2} van o cap toi da", progs[k2]["level"] == MAXLV, str(progs[k2]["level"]))

    # ─────────── [9] Client KHONG tu len cap duoc ───────────
    print("\n[9] Client gui `training` / `bests` len → BI BO QUA")
    k3 = [k for k in LAW if progs[k]["level"] == 0][0]
    st, _ = call("POST", "/me/progress", token, {
        "type": "game", "game": "dodge", "score": 1, "seconds": 1, "meteors": 0,
        "opId": f"op-fake-{int(time.time()*1000)}",
        "training": {"levels": 99, "programs": [{"key": k3, "level": 4}]},
        "bests": {g: 999999 for g in games},
    })
    ck("van 200 (truong la bi bo qua)", st == 200, str(st))
    _, progs = training()
    ck(f"chuong trinh {k3} VAN Cap 0", progs[k3]["level"] == 0, str(progs[k3]["level"]))

    # ─────────── [10] Dat het moi cap ───────────
    print("\n[10] Dat het → levels == maxLevels")
    for k, v in LAW.items():
        for g, _, goals in v:
            if g == "constellation":
                # `consts` tang theo SO CHOM KHAC NHAU, khong theo diem — bao mot
                # lan cho moi chom moi len duoc cap toi da.
                for _ in range(goals[-1]): report(g, 1)
            else:
                report(g, goals[-1])
    t, progs = training()
    ck("moi chuong trinh o cap toi da",
       all(p["level"] == p["maxLevel"] for p in progs.values()),
       str({k: p["level"] for k, p in progs.items()}))
    ck("levels == maxLevels", t["levels"] == t["maxLevels"] == len(LAW) * MAXLV,
       f'{t["levels"]}/{t["maxLevels"]}')
    ck("moi `next` deu null", all(c["next"] is None for p in progs.values() for c in p["courses"]))

    # ─────────── [11] Khong co duong GHI rieng ───────────
    print("\n[11] Khong ton tai route ghi `training`")
    for m in ("POST", "PUT", "PATCH", "GET"):
        st, _ = call(m, "/me/training", token, {"levels": 20} if m != "GET" else None)
        ck(f"{m} /me/training khong ton tai ({st})", st in (404, 405), str(st))

    # ─────────── [12] Khong token ───────────
    print("\n[12] Khong token → 401")
    st, _ = call("GET", "/me/achievements")
    ck("GET /me/achievements khong token → 401", st == 401, str(st))

finally:
    print("\n[don] xoa du lieu test")
    try:
        print(f"       xoa {wipe(uid)} dong DynamoDB")
    except Exception as e:
        print(f"       ⚠️ con dong DynamoDB: {e}")
    try:
        _fbtest.delete(token); print("       xoa tai khoan Firebase tam")
    except Exception as e:
        print(f"       ⚠️ con tai khoan Firebase: {e}")

print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
