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


# ⚠️⚠️ TRUONG THU TU LA SO LAN MOC XUAT HIEN, VA NO PHAI KHOP CHINH XAC.
#    Tu 25/08/2026 (quyet dinh ⑤) phep xet 5xx nam o CA HAI nhanh — `fastFirst()`
#    va nhanh mang-truoc — nen moc `status >= 500` xuat hien 2 lan. Ban cu doi moc
#    DUY NHAT roi `[BO QUA]`, tuc 2/3 phep pha hoai LANG LE KHONG CHAY: mot phep
#    thu pha hoai bi bo qua thi cung nhu da chet. Nay doi dung so lan va thay CA
#    HAI — vi bo phep xet 5xx o BAT KY nhanh nao cung la mot duong ro con ky lan.
#    ⚠️ Moc khong khop so lan la HONG, khong phai BO QUA.
CASES = [
    # (ten, chuoi cu, chuoi moi, so lan xuat hien)
    ("bo phep xet 5xx (chi bat loi mang)",
     "if (res && res.status >= 500) return fallback(req, res);",
     "/* pha hoai: bo phep xet 5xx */", 2),
    ("cho 404 lui ve cache (trang da xoa song lai)",
     "if (res && res.status >= 500) return fallback(req, res);",
     "if (res && res.status >= 400) return fallback(req, res);", 2),
    ("bo buoc xoa cache cua ban dung cu",
     'if (k !== CACHE && k.indexOf("astroq-") === 0) return caches.delete(k);',
     "/* pha hoai: khong xoa cache cu */", 1),
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
    for name, old, new, n in CASES:
        got_n = base.count(old)
        if got_n != n:
            # ⚠️ HONG, khong phai BO QUA: mot phep thu pha hoai khong chay duoc thi
            #    khong chung minh duoc gi, ma no lai doc ra nhu "da kiem".
            print("=== %s ===" % name)
            print("  [HONG] moc xuat hien %d lan, doi %d — SUA LAI CASES" % (got_n, n))
            print("")
            continue
        io.open(SW, "w", encoding="utf-8", newline="\n").write(base.replace(old, new))
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
