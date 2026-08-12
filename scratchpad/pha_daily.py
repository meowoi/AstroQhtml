# -*- coding: utf-8 -*-
"""
pha_daily.py — PHEP THU PHA HOAI cho viec hang ngay + chuoi ngay.

Gay LOI CO Y vao ma nguon server roi doi `test_daily.py` bao hong. Mot phep kiem
khong bat duoc loi la mot phep kiem da chet — chay bo nay moi biet bo do co rang.

    cd AstroQhtml && python scratchpad/pha_daily.py

⚠️ KHOI PHUC TRONG CUNG MOT TIEN TRINH (bai hoc 02/08/2026: sao luu bang shell roi
   khoi phuc bang Python la hai cho khac nhau, va khoi phuc hut thi de lai repo o
   trang thai da pha). Khoi `finally` tra lai nguyen van moi file da sua.
"""
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]              # AstroQhtml
API = ROOT.parent / "AstroqSV" / "src" / "AstroqSV.Api"
DAILY_CS = API / "Services" / "Daily.cs"
CTX_CS = API / "Data" / "DynamoContext.Daily.cs"

# (nhan, file, chuoi cu, chuoi moi, so phep kiem toi thieu phai do)
CASES = [
    ("Bo an han: moi khoang nghi deu lam dut chuoi",
     DAILY_CS,
     "if (++missed > GraceDaysPerWeek) { broken = true; break; }",
     "if (++missed > 0) { broken = true; break; }",
     1),
    ("Cho ky luc BI HA xuong bang chuoi hien tai",
     DAILY_CS,
     "return new Streak(cur, Math.Max(s.Best, cur), todayKey, wk, broken ? 0 : missed);",
     "return new Streak(cur, cur, todayKey, wk, broken ? 0 : missed);",
     1),
    # ⚠️ PHAI GIU `:id` DUOC DUNG TRONG DIEU KIEN. Lan dau toi XOA HAN dong
    #    ConditionExpression, va DynamoDB tra 500 ("ExpressionAttributeValues unused")
    #    — bo do bao hong that, nhung hong vi mot loi CU PHAP, khong phai vi tra thuong
    #    hai lan. Tuc phep pha do KHONG chung minh duoc dieu can chung minh. Dieu kien
    #    duoi day LUON DUNG ma van dung `:id`, nen no tao ra dung canh tra hai lan.
    ("Bo chot chong tra thuong hai lan (dieu kien luon dung)",
     CTX_CS,
     'ConditionExpression = "attribute_not_exists(paid) OR NOT contains(paid, :id)",',
     'ConditionExpression = "attribute_not_exists(paid) OR contains(paid, :id)'
     ' OR NOT contains(paid, :id)",',
     1),
    ("Them mot moc HET HAN vao du lieu tra ve (dieu ③)",
     DAILY_CS,
     "graceLeft = GraceLeft(s, today)",
     "graceLeft = GraceLeft(s, today),\n        expiresAt = today.AddDays(1).ToString(\"o\")",
     1),
]


def kill_api():
    subprocess.run(["taskkill", "/IM", "AstroqSV.Api.exe", "/F"],
                   capture_output=True, text=True)
    time.sleep(2)


def build():
    r = subprocess.run(["dotnet", "build", "-v", "q", "--nologo"],
                       cwd=API, capture_output=True, text=True, timeout=300)
    return "Build succeeded" in r.stdout, r.stdout[-1500:]


def start_api():
    log = open(ROOT / "scratchpad" / ".pha_api.log", "w", encoding="utf-8")
    p = subprocess.Popen(["dotnet", "run", "--no-build"], cwd=API,
                         stdout=log, stderr=subprocess.STDOUT)
    for _ in range(40):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://localhost:5080/health", timeout=3) as r:
                if r.status == 200:
                    return p
        except Exception:
            pass
    return p


def run_tests():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-u", "scratchpad/test_daily.py"],
                       cwd=ROOT, capture_output=True, text=True, env=env, timeout=600)
    out = r.stdout + r.stderr
    bad = [l.strip() for l in out.splitlines() if l.strip().startswith("[HONG]")]
    return bad, out


def main():
    orig = {DAILY_CS: DAILY_CS.read_text(encoding="utf-8"),
            CTX_CS: CTX_CS.read_text(encoding="utf-8")}
    caught = 0
    try:
        for label, path, old, new, need in CASES:
            print("=" * 70)
            print(f"PHA: {label}")
            src = orig[path]
            if old not in src:
                print("  [!] KHONG TIM THAY MOC — phep pha nay khong chay duoc, BO QUA")
                print("      (moc phai la chuoi DUY NHAT; dem lai truoc khi ket luan"
                      " phep kiem mu)")
                continue
            if src.count(old) != 1:
                print(f"  [!] MOC XUAT HIEN {src.count(old)} LAN — bo qua de khong sua"
                      " nham cho khac")
                continue

            kill_api()
            path.write_text(src.replace(old, new, 1), encoding="utf-8")
            okb, log = build()
            if not okb:
                print("  [!] Build hong — coi nhu KHONG do duoc")
                print(log[-600:])
                path.write_text(src, encoding="utf-8")
                continue
            start_api()
            bad, _ = run_tests()
            print(f"  -> {len(bad)} phep kiem bao hong")
            for b in bad[:6]:
                print("     " + b)
            if len(bad) >= need:
                caught += 1
                print("  KET LUAN: bo do BAT DUOC loi nay.")
            else:
                print("  KET LUAN: ⚠️ LOT — phep kiem mu, phai siet lai.")
            path.write_text(src, encoding="utf-8")
    finally:
        kill_api()
        for p, s in orig.items():
            p.write_text(s, encoding="utf-8")
        print("\n[khoi phuc] Da tra lai nguyen van ma nguon.")
        okb, log = build()
        print(f"[khoi phuc] Build lai: {'OK' if okb else 'HONG'}")
        if not okb:
            print(log[-800:])

    print(f"\n=== {caught}/{len(CASES)} phep pha bi BAT ===")
    return 0 if caught == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
