# -*- coding: utf-8 -*-
"""
pha_guest_claim.py — PHÉP THỬ PHÁ HOẠI cho `smoke_guest_claim.py`.

Gây từng lỗi cố ý vào mã SẢN PHẨM rồi chạy bộ đo, đòi nó phải ĐỎ. Một bộ đo
không đỏ với lỗi mà nó sinh ra để bắt thì nó chỉ đang xác nhận chính nó.

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/pha_guest_claim.py

⚠️ SAO LƯU/KHÔI PHỤC BẰNG **BYTES**, không bằng văn bản. Đọc rồi ghi lại bằng
   text mode trên Windows biến LF thành CRLF — khôi phục "thành công" mà file
   vẫn đổi. Bài học đã trả giá ngày 22/08/2026 (`pha_gate.py`).
⚠️ Mốc tìm-thay phải DUY NHẤT: đếm trước, không thì `replace(..., 1)` sửa nhầm
   chỗ và phép phá không phá đúng thứ định phá (bài học 29/08/2026).
"""
import hashlib
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "scratchpad", "smoke_guest_claim.py")

CASES = [
    (
        "A. `afterStep` thoi goi `claimIfDue()` — the khong bao gio bat len",
        os.path.join(ROOT, "js", "mission-stage.js"),
        "      var claim = claimIfDue();",
        "      var claim = null;",
        1,
    ),
    (
        "B. `queuedSteps` dem SO PHAN TU thay vi so CHANG khac nhau",
        os.path.join(ROOT, "js", "progress.js"),
        "        if (!k || seen[k]) return;",
        "        if (!k) return;",
        1,
    ),
    (
        "C. Nhanh khong-co-phien muon cau 'da luu xong'",
        os.path.join(ROOT, "js", "guest-claim.js"),
        '          say(r.message || T("ok_acc"), "ok");',
        '          say(T("ok_0"), "ok");',
        1,
    ),
]


def sha(path):
    with io.open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_smoke():
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, "-u", SMOKE], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    hong = [l.strip() for l in (p.stdout or "").splitlines() if "[FAIL]" in l]
    return p.returncode, hong


def main():
    bat = 0
    for name, path, old, new, want in CASES:
        print("\n" + "=" * 72)
        print(name)
        with io.open(path, "rb") as f:
            raw = f.read()
        before = sha(path)
        txt = raw.decode("utf-8")
        n = txt.count(old)
        if n != want:
            print(f"  [BO QUA] moc xuat hien {n} lan, doi {want} — khong pha dung cho.")
            continue
        try:
            with io.open(path, "wb") as f:
                f.write(txt.replace(old, new, 1).encode("utf-8"))
            code, hong = run_smoke()
            if code != 0 and hong:
                bat += 1
                print(f"  [BAT DUOC] bo do bao {len(hong)} phep kiem hong:")
                for h in hong[:4]:
                    print("      " + h)
            else:
                print(f"  [LOT] bo do KHONG bao hong (exit={code}) — phep kiem MU.")
        finally:
            with io.open(path, "wb") as f:
                f.write(raw)
            assert sha(path) == before, "KHOI PHUC HONG: " + path
            print("  [khoi phuc] khop SHA-256")

    print("\n" + "=" * 72)
    print(f"=== {bat}/{len(CASES)} loi co y deu bi bat ===")
    sys.exit(0 if bat == len(CASES) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
