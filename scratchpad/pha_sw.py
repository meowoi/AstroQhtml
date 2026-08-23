# -*- coding: utf-8 -*-
"""pha_sw.py — PHEP THU PHA HOAI cho smoke_sw.py.

Gay tung loi co y vao `sw.js` roi chay lai bo do. `sw.js` la file SINH RA nen
khoi phuc = chay lai `scratchpad/gen_sw.py`, khong can sao luu.

    python scratchpad/pha_sw.py
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SW = os.path.join(ROOT, "sw.js")


def regen():
    subprocess.run([sys.executable, os.path.join(ROOT, "scratchpad", "gen_sw.py")],
                   cwd=ROOT, capture_output=True)


def run_suite():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "scratchpad", "smoke_sw.py")],
                       cwd=ROOT, capture_output=True, text=True, env=env, errors="replace")
    out = r.stdout or ""
    m = re.search(r"(\d+) dat / (\d+) hong", out)
    hong = int(m.group(2)) if m else -1
    dat = int(m.group(1)) if m else -1
    names = re.findall(r"^\s+\[HONG\]\s+(.+)$", out, re.M)
    return dat, hong, names


CASES = [
    # (ten, chuoi cu, chuoi moi)
    ("bo phep xet 5xx (chi bat loi mang)",
     "if (res && res.status >= 500) return fallback(req, res);",
     "/* pha hoai: bo phep xet 5xx */"),
    ("cho 404 lui ve cache (trang da xoa song lai)",
     "if (res && res.status >= 500) return fallback(req, res);",
     "if (res && res.status >= 400) return fallback(req, res);"),
    ("bo buoc xoa cache cua ban dung cu",
     'if (k !== CACHE && k.indexOf("astroq-") === 0) return caches.delete(k);',
     "/* pha hoai: khong xoa cache cu */"),
]


def main():
    regen()
    base = io.open(SW, encoding="utf-8", newline="").read()

    print("=== moc: ban dung ===")
    d, h, _ = run_suite()
    print("  %d dat / %d hong\n" % (d, h))
    if h != 0:
        sys.exit("ban dung da hong san, dung pha them")

    caught = 0
    for name, old, new in CASES:
        if base.count(old) != 1:
            print("  [BO QUA] %s — moc khong duy nhat (%d)" % (name, base.count(old)))
            continue
        io.open(SW, "w", encoding="utf-8", newline="\n").write(base.replace(old, new, 1))
        d, h, names = run_suite()
        got = h > 0
        caught += 1 if got else 0
        print("=== %s ===" % name)
        print("  %s  (%d dat / %d hong)" % ("BAT DUOC" if got else "LOT", d, h))
        for n in names[:4]:
            print("      - %s" % n)
        print("")
        regen()

    print("=== %d/%d loi co y bi bat ===" % (caught, len(CASES)))
    ok = io.open(SW, encoding="utf-8", newline="").read() == base
    print("da khoi phuc sw.js: %s" % ok)
    sys.exit(0 if (caught == len(CASES) and ok) else 1)


if __name__ == "__main__":
    main()
