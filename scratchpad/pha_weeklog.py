# -*- coding: utf-8 -*-
"""
pha_weeklog.py — PHEP THU PHA HOAI cho Nhat ky tuan (muc [26] cua check_pages).

    cd AstroQhtml && python scratchpad/pha_weeklog.py

⚠️ KHOI PHUC TRONG CUNG MOT TIEN TRINH (bai hoc 02/08/2026: sao luu bang shell roi
   khoi phuc bang Python la hai cho khac nhau; khoi phuc hut la de lai repo da pha).
"""
import io
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WL_JS = ROOT / "js" / "weeklog.js"
WL_CSS = ROOT / "css" / "weeklog.css"
PROFILE = ROOT / "profile.html"

CASES = [
    # ② To do dong GIAM — bien mot phep do thanh mot loi phan xet.
    ("To do dong GIAM", WL_CSS,
     ".wl-down,\n.wl-same {\n  color: #9fb0d0;",
     ".wl-down {\n  color: #ff5555;\n}\n.wl-same {\n  color: #9fb0d0;"),
    # ① Len mot khai niem xep hang giua cac tre.
    ("Them mot dong xep hang giua cac tre", WL_JS,
     'best_tie: "bằng kỷ lục của bạn",',
     'best_tie: "bằng kỷ lục của bạn", rank: "Bạn giỏi hơn 70% bạn khác",'),
    # Noi "ky luc MOI" — mot suy luan khong co can cu trong du lieu.
    ("Doi 'bang ky luc' thanh 'ky luc MOI'", WL_JS,
     'best_tie: "bằng kỷ lục của bạn",',
     'best_tie: "kỷ lục mới của bạn",'),
    # Bay [hidden] — lan thu 8: bo dong khai lai thi chi tiet hien san.
    ("Bo `.wl-detail[hidden]{display:none}`", WL_CSS,
     ".wl-detail[hidden] { display: none; }", ""),
    # Khai ten game o weeklog -> ban thu ba cua mot bang ten.
    ("Khai ten game ngay trong js/weeklog.js", WL_JS,
     'best_h: "Điểm cao nhất tuần này",',
     'best_h: "Điểm cao nhất tuần này", g_dodge: "Né Thiên Thạch",'),
    # ⚠️ PHEP PHA QUAN TRONG NHAT: bo ba game moi khoi bang ky luc — dung loi CO THAT
    #    da ton tai truoc 12/08/2026 (ky luc that trong DB ma khong hien ra dau ca).
    ("Bo 3 game moi khoi bang ky luc o profile.html", PROFILE,
     '      { key:"catch",         ic:"🌟", nm:t("rec_catch"),         unit:t("rec_pts"), ls:"astroq-catch-best" },',
     ""),
]


def run_check():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-u", "scratchpad/check_pages.py"],
                       cwd=ROOT, capture_output=True, text=True, env=env, timeout=600,
                       encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    bad = [l.strip() for l in out.splitlines() if l.strip().startswith("[HONG]")]
    return bad


def main():
    orig = {p: p.read_text(encoding="utf-8") for p in {WL_JS, WL_CSS, PROFILE}}
    caught = 0
    try:
        for label, path, old, new in CASES:
            print("=" * 70)
            print("PHA: " + label)
            src = orig[path]
            n = src.count(old)
            if n != 1:
                print(f"  [!] MOC XUAT HIEN {n} LAN — bo qua de khong sua nham cho khac.")
                print("      (dem truoc khi ket luan phep kiem mu — bai hoc 30/07/2026)")
                continue
            path.write_text(src.replace(old, new, 1), encoding="utf-8")
            bad = run_check()
            print(f"  -> {len(bad)} phep kiem bao hong")
            for b in bad[:5]:
                print("     " + b)
            if bad:
                caught += 1
                print("  KET LUAN: bo do BAT DUOC loi nay.")
            else:
                print("  KET LUAN: ⚠️ LOT — phep kiem mu, phai siet lai.")
            path.write_text(src, encoding="utf-8")
    finally:
        for p, s in orig.items():
            p.write_text(s, encoding="utf-8")
        print("\n[khoi phuc] Da tra lai nguyen van 3 file.")
        bad = run_check()
        print("[khoi phuc] check_pages:", "sach" if not bad else f"CON {len(bad)} HONG")

    print(f"\n=== {caught}/{len(CASES)} phep pha bi BAT ===")
    return 0 if caught == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
