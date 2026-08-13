# -*- coding: utf-8 -*-
"""Phep thu pha hoai: tra loi "cua hang rong" ve roi do xem muc [10] cua
smoke_shop.py co bat duoc khong. Neu no van xanh thi phep kiem la RONG.

⚠️ Sao luu va khoi phuc lam TRONG CUNG MOT tien trinh Python (bai hoc 02/08/2026:
   `/tmp` cua Git Bash va cua Python la hai cho khac nhau, khoi phuc hut la de lai
   repo o trang thai da bi pha).
"""
import io
import os
import re
import subprocess
import sys

ROOT = r"c:\Users\ADMIN\OneDrive\Desktop\astroq\AstroQhtml"
SHOP = os.path.join(ROOT, "shop.html")

# ⚠️ LAN PHA DAU TIEN CUA TOI KHONG CHUNG MINH DUOC GI, va loi o PHEP PHA: no thay
#    ca khoi `whenAuth(...)` bang mot IIFE va lam vo cu phap JS → ca trang chet →
#    bo do nem ngoai le o muc [1] va DUNG HAN, in ra "0 hong" + khong co dong ket
#    qua. Doc ra y het "phep kiem mu". Bai hoc da ghi nhieu lan: hoi "minh co pha
#    dung cho khong" TRUOC khi ket luan phep kiem mu.
#    Cach pha DUNG: giu nguyen cu phap, chi ha han cho ve 0 — tuc dung hanh vi cu
#    ("hoi mot lan roi ket luan ngay"), va no an toan ve cu phap.
#    ⚠️ LAN PHA THU HAI CUNG KHONG TAI HIEN DUOC: ha han cho ve 0 thi toi nhip dau
#       tien (60ms) module ES DA CHAY XONG, nen `whenAuth` van tim thay AstroQAuth.
#       Hanh vi cu khong phai "cho mot nhip roi ket luan" ma la "hoi DONG BO, khong
#       cho nhip nao". Pha dung chinh cho do:
GOOD = "    var t0 = Date.now();\n    var timer = setInterval("
BAD = "    cb(null); return;\n    var t0 = Date.now();\n    var timer = setInterval("

src = io.open(SHOP, encoding="utf-8").read()
assert GOOD in src, "khong khop moc — doc lai shop.html truoc khi pha"

broken = src.replace(GOOD, BAD, 1)
io.open(SHOP, "w", encoding="utf-8", newline="").write(broken)
print("da pha: whenAuth ket luan DONG BO, khong cho nhip nao\n")

try:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "scratchpad/smoke_shop.py"],
                       cwd=ROOT, env=env, capture_output=True, text=True,
                       encoding="utf-8", timeout=600)
    out = r.stdout
    hong = [l for l in out.splitlines() if re.match(r"^\s+\[HONG\]", l)]
    tail = [l for l in out.splitlines() if "KET QUA" in l]
    print("So phep kiem bao HONG: %d" % len(hong))
    for l in hong:
        print("  " + l.strip())
    print("  " + (tail[-1] if tail else "(khong doc duoc dong ket qua)"))
    if not tail:
        print("\n-- 6 dong cuoi cua stdout --")
        for l in out.splitlines()[-6:]:
            print("   " + l)
        print("-- stderr --")
        for l in (r.stderr or "").splitlines()[-6:]:
            print("   " + l)
finally:
    io.open(SHOP, "w", encoding="utf-8", newline="").write(src)
    back = io.open(SHOP, encoding="utf-8").read()
    print("\nda khoi phuc shop.html:", "DUNG" if back == src else "HONG — SUA TAY NGAY")
