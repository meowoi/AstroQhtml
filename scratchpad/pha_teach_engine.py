# -*- coding: utf-8 -*-
"""pha_teach_engine.py — PHÉP THỬ PHÁ HOẠI cho `check_teach_engine.py`.

    python scratchpad/pha_teach_engine.py

Gây lỗi cố ý vào `js/teach-machine.js` rồi đòi bộ đo BÁO HỎNG. Một bộ đo chưa
bao giờ đỏ thì không ai biết nó đang gác thật hay chỉ đang chạy.

⚠️ SAO LƯU VÀ KHÔI PHỤC TRONG CÙNG MỘT TIẾN TRÌNH, VÀ SO BYTE-ĐÚNG-BYTE.
   Bài học 02/08/2026: `/tmp` của Git Bash và của Python là hai chỗ khác nhau,
   khôi phục hụt là để lại repo ở trạng thái ĐÃ BỊ PHÁ. Và bài học 22/08: so
   sánh bằng VĂN BẢN thì mù với dấu xuống dòng — đọc/ghi bytes.

⚠️ MỌI MỐC TÌM-THAY LÀ ASCII THUẦN (bài học 16/08/2026): mốc có dấu tiếng Việt
   thì `count()` ra 0 trong khi mắt đọc thấy y hệt.
"""
import io
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "js", "teach-machine.js")
GATE = os.path.join(ROOT, "scratchpad", "check_teach_engine.py")

# (nhãn, mốc, thay bằng, số lần khớp phải bằng)
CASES = [
    ("[A] tra vung trong ve cho cu (0.30,0.72) -> thien lech BIEN MAT",
     'mk("cs1", 0.26, 0.40', 'mk("cs1", 0.30, 0.72', 1),

    ("[B] isFar() luon true -> chieu doi chung phai bat",
     "return !!res && res.gap > 0.15;", "return !!res;", 1),

    ("[C] bo phan loai doc luon `bright` -> dac trung gay nhieu het gay nhieu",
     'var FEAT = ["len", "curve"];', 'var FEAT = ["len", "curve", "bright"];', 1),

    ("[D] ghim hau to id gradient -> hai anh cung me trung id",
     "var n = ++seq;", "var n = 1;", 1),
]


def run_gate():
    """Chạy bộ đo, trả về (số đạt, số hỏng)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    p = subprocess.run([sys.executable, GATE], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    ok = bad = -1
    for line in (p.stdout or "").splitlines():
        if "KET QUA" in line:
            try:
                parts = line.replace("=", " ").split()
                ok = int(parts[parts.index("dat") - 1])
                bad = int(parts[parts.index("hong") - 1])
            except Exception:
                pass
    return ok, bad


orig = io.open(SRC, "rb").read()
caught = 0
try:
    base_ok, base_bad = run_gate()
    print("Moc: %d dat / %d hong (phai la 0 hong)" % (base_ok, base_bad))
    if base_bad != 0 or base_ok <= 0:
        print("  [DUNG] bo do dang khong sach, khong the thu pha hoai.")
        sys.exit(2)

    for label, old, new, want in CASES:
        text = orig.decode("utf-8")
        n = text.count(old)
        if n != want:
            print("  [BO QUA] %s -- moc khop %d lan, doi %d" % (label, n, want))
            continue
        io.open(SRC, "wb").write(text.replace(old, new, want).encode("utf-8"))
        ok, bad = run_gate()
        if bad > 0:
            caught += 1
            print("  [BAT DUOC] %s -> %d dat / %d hong" % (label, ok, bad))
        else:
            print("  [LOT]      %s -> %d dat / %d hong" % (label, ok, bad))
        io.open(SRC, "wb").write(orig)
finally:
    io.open(SRC, "wb").write(orig)

same = io.open(SRC, "rb").read() == orig
print("\nKhoi phuc byte-dung-byte: %s" % ("OK" if same else "HONG"))
print("=== %d/%d loi co y bi bat ===" % (caught, len(CASES)))
sys.exit(0 if (caught == len(CASES) and same) else 1)
