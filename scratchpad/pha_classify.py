# -*- coding: utf-8 -*-
"""pha_classify.py — PHÉP THỬ PHÁ HOẠI cho `play_classify.py`.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/pha_classify.py

Gây lỗi cố ý rồi đòi bộ đo BÁO HỎNG. Một bộ đo chưa bao giờ đỏ thì không ai
biết nó đang gác thật hay chỉ đang chạy.

⚠️ SAO LƯU VÀ KHÔI PHỤC TRONG CÙNG MỘT TIẾN TRÌNH, ĐỌC/GHI BYTES, SO SHA-256.
   Bài học 02/08/2026: `/tmp` của Git Bash và của Python là hai chỗ khác nhau,
   khôi phục hụt là để lại repo ở trạng thái ĐÃ BỊ PHÁ. Và so sánh bằng VĂN BẢN
   thì mù với dấu xuống dòng.

⚠️ MỌI MỐC TÌM-THAY LÀ ASCII THUẦN (bài học 16/08/2026): mốc có dấu tiếng Việt
   thì `count()` ra 0 trong khi mắt đọc thấy y hệt.
"""
import hashlib
import io
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "scratchpad", "play_classify.py")

TM = os.path.join(ROOT, "js", "teach-machine.js")
PG = os.path.join(ROOT, "game-classify.html")
CSS = os.path.join(ROOT, "css", "game-classify.css")

# (nhãn, file, mốc, thay bằng, số lần khớp phải bằng)
CASES = [
    ("[A] tra vung curved_short ve cho cu -> THIEN LECH BIEN MAT",
     TM, 'mk("cs1", 0.26, 0.40', 'mk("cs1", 0.30, 0.72', 1),

    ("[B] bo phan loai doc luon `bright` -> bay tia vu tru hong",
     TM, 'var FEAT = ["len", "curve"];', 'var FEAT = ["len", "curve", "bright"];', 1),

    ("[C] am tham DUNG nhan sai thay vi bat sua -> mat bai hoc",
     PG, "if(bad.length){", "if(false){", 1),

    ("[D] tinh diem ca vong da gan sai -> thuong noi len",
     PG, "if(clean){ score++;", "if(true){ score++;", 1),

    ("[E] bo kep be rong luoi -> nut nhan thu hai roi ra ngoai tam nhin",
     CSS, "@media (min-width:901px){ .cl-grid{--cl-max:704px;} }", "", 1),

    ("[F] khoa nut Huan luyen thay vi noi ra -> lai im lang nhu cu",
     PG, 'var miss = picks.indexOf(null);', 'var miss = -1;', 1),
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


orig = {f: io.open(f, "rb").read() for f in {TM, PG, CSS}}
caught = 0
try:
    base_ok, base_bad = run_gate()
    print("Moc: %d dat / %d hong (phai la 0 hong)" % (base_ok, base_bad))
    if base_bad != 0 or base_ok <= 0:
        print("  [DUNG] bo do dang khong sach, khong the thu pha hoai.")
        sys.exit(2)

    for label, f, old, new, want in CASES:
        text = orig[f].decode("utf-8")
        n = text.count(old)
        if n != want:
            print("  [BO QUA] %s -- moc khop %d lan, doi %d" % (label, n, want))
            continue
        io.open(f, "wb").write(text.replace(old, new, want).encode("utf-8"))
        ok, bad = run_gate()
        if bad > 0:
            caught += 1
            print("  [BAT DUOC] %s -> %d dat / %d hong" % (label, ok, bad))
        else:
            print("  [LOT]      %s -> %d dat / %d hong" % (label, ok, bad))
        io.open(f, "wb").write(orig[f])
finally:
    for f, b in orig.items():
        io.open(f, "wb").write(b)

same = all(hashlib.sha256(io.open(f, "rb").read()).hexdigest()
           == hashlib.sha256(b).hexdigest() for f, b in orig.items())
print("\nKhoi phuc khop SHA-256: %s" % ("OK" if same else "HONG"))
print("=== %d/%d loi co y bi bat ===" % (caught, len(CASES)))
sys.exit(0 if (caught == len(CASES) and same) else 1)
