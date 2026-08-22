# -*- coding: utf-8 -*-
"""pha_defender_bank.py — PHEP THU PHA HOAI cho `probe_defender_bank.py`.

Gay 4 loi CO Y roi doi phep kiem phai BAO HONG. Mot bo do khong do duoc
khi san pham sai thi no khong chung minh gi.

⚠️ Sao luu va khoi phuc lam TRONG CUNG MOT tien trinh Python (khoi `finally`) —
   `/tmp` cua Git Bash va cua Python la hai cho khac nhau, khoi phuc hut la de
   lai repo o trang thai da bi pha.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/pha_defender_bank.py
"""
import io
import pathlib
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEF = ROOT / "game-defender.html"
PROBE = ROOT / "scratchpad" / "probe_defender_bank.py"

# (ten loi, chuoi cu, chuoi moi)
PHA = [
    ("bo qua `quizPool` -> luon dung duong lui",
     "    if(quizPool.length){",
     "    if(false && quizPool.length){"),

    ("thoi dong dau cau da hien -> hoi lai cau cu",
     "      askedAdd(quizQ.term);",
     "      /* pha: */ void 0;"),

    ("thoi hien ten linh vuc -> nhan quay ve chuoi co dinh",
     '    if(tag) tag.textContent = "[ " + (q.topic ? L(q.topic) : t("quiz_tag")) + " ]";',
     "    if(tag) void 0;"),

    ("dong dau KHONG theo uid -> tre sau bo qua cau cua tre truoc",
     "      if(!b || b.uid!==uidNow() || !(b.k instanceof Array)) return [];",
     "      if(!b || !(b.k instanceof Array)) return [];"),
]


def run():
    r = subprocess.run([sys.executable, "-u", str(PROBE)],
                       capture_output=True, cwd=str(ROOT))
    out = (r.stdout or b"").decode("utf-8", "replace")
    n = len(re.findall(r"^\s+\[HONG\]", out, re.M))
    m = re.search(r"KET QUA: (\d+) dat / (\d+) hong", out)
    return n, (m.group(0) if m else "khong doc duoc dong ket qua"), out


def main():
    goc = io.open(DEF, encoding="utf-8").read()
    bat = 0
    try:
        for ten, old, new in PHA:
            if goc.count(old) != 1:
                print("  [HONG] moc pha khong duy nhat: " + ten)
                continue
            io.open(DEF, "w", encoding="utf-8").write(goc.replace(old, new, 1))
            n, tong, out = run()
            if n > 0:
                bat += 1
                print("  [BAT]  %-58s -> %d phep kiem bao hong  (%s)" % (ten, n, tong))
            else:
                print("  [LOT]  %-58s -> KHONG phep kiem nao bao hong (%s)" % (ten, tong))
                print("\n".join(out.splitlines()[-6:]))
            io.open(DEF, "w", encoding="utf-8").write(goc)
    finally:
        io.open(DEF, "w", encoding="utf-8").write(goc)
        print("\n(da khoi phuc game-defender.html)")

    print("\n=== %d/%d loi co y bi BAT ===" % (bat, len(PHA)))
    sys.exit(0 if bat == len(PHA) else 1)


if __name__ == "__main__":
    main()
