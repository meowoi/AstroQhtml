# -*- coding: utf-8 -*-
"""PHEP THU PHA HOAI — chung minh cac phep kiem MOI cua nhiem vu 02 co RANG.

Gay tung loi co y roi doi `check_pages.py` phai bao hong. Phep kiem khong bat duoc
loi nao la mot phep kiem dat MOT CACH RONG — du an nay da co vai lan nhu the, va
lan nao cung chi lo ra khi co ai do thu pha.

Chay:  python scratchpad/pha_mission_orbit.py
"""
import io, os, re, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SV = os.path.abspath(os.path.join(ROOT, "..", "AstroqSV"))


def rd(p):
    return io.open(os.path.join(ROOT, p) if not os.path.isabs(p) else p,
                   encoding="utf-8").read()


def wr(p, s):
    io.open(os.path.join(ROOT, p) if not os.path.isabs(p) else p, "w",
            encoding="utf-8", newline="\n").write(s)


def run_checks():
    """So phep kiem HONG cua check_pages."""
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scratchpad", "check_pages.py")],
                       cwd=ROOT, capture_output=True,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    out = r.stdout.decode("utf-8", "replace")
    m = re.search(r"KET QUA: (\d+) dat / (\d+) hong", out)
    if not m:
        return -1, out[-500:]
    return int(m.group(2)), ""


CASES = [
    # (nhan, duong dan, ham pha)
    ("dao thu tu 2 chang trong STEP_IDS cua trang choi",
     "mission-orbit.html",
     lambda s: s.replace("const STEP_IDS = ['eyes', 'bands', 'night', 'read', 'report'];",
                         "const STEP_IDS = ['eyes', 'night', 'bands', 'read', 'report'];")),

    ("xoa object xu ly cua mot chang",
     "mission-orbit.html",
     lambda s: s.replace("\n  report: {\n", "\n  reportXX: {\n")),

    ("cho nhiem vu 02 co 6 chang (pha luat '5 chang tu nhiem vu 02')",
     os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"),
     lambda s: s.replace('new("report", 20, 30, null)\n',
                         'new("report", 20, 30, null),\n            new("extra", 5, 5, null)\n')),

    ("doi mot id mau codex o server (bai doc thanh mo coi)",
     os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"),
     lambda s: s.replace('"night-lights"', '"night-lightz"')),

    ("lech `codexTotal` du phong o trang choi",
     "mission-orbit.html",
     lambda s: s.replace("codexTotal: 4,", "codexTotal: 9,")),

    ("bo mot chang khoi danh muc client",
     "js/mission-catalog.js",
     lambda s: s.replace("""        { id: "read", ic: "🔎",""",
                         """        { id: "readXX", ic: "🔎",""")),
]

base, err = run_checks()
print("Moc: %d phep kiem hong khi CHUA pha\n" % base)
if base != 0:
    print("  ⚠️ Moc khac 0 — sua het truoc da roi hay chay phep thu pha hoai.")
    print(err)
    sys.exit(1)

bat, lot = 0, []
for nhan, path, pha in CASES:
    goc = rd(path)
    try:
        wr(path, pha(goc))
        n, _ = run_checks()
        if n > 0:
            bat += 1
            print("  [BAT]  %-58s → %d phep kiem hong" % (nhan, n))
        else:
            lot.append(nhan)
            print("  [LOT]  %-58s → 0 hong (PHEP KIEM MU)" % nhan)
    finally:
        wr(path, goc)          # khoi phuc DU co ngoai le giua chung

n, _ = run_checks()
print("\nSau khi khoi phuc: %d hong (phai la 0)" % n)
print("=== KET QUA: %d/%d loi co y bi bat ===" % (bat, len(CASES)))
sys.exit(0 if (bat == len(CASES) and n == 0) else 1)
