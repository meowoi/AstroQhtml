# -*- coding: utf-8 -*-
r"""Phep thu pha hoai cho `smoke_version.py` — chung minh no CO RANG.

⚠️ Sao luu va khoi phuc lam TRONG CUNG MOT tien trinh Python. Bai hoc 02/08/2026:
   `/tmp` cua Git Bash va `/tmp` cua Python la hai cho khac nhau, khoi phuc hut la
   de lai repo o trang thai da bi pha.
"""
import io
import subprocess
import sys

FILES = ["js/ui-common.js", "css/common.css"]
GOC = {p: io.open(p, encoding="utf-8").read() for p in FILES}


def hong():
    r = subprocess.run([sys.executable, "scratchpad/smoke_version.py"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [l.strip()[7:100] for l in r.stdout.splitlines() if l.strip().startswith("[HONG]")]


THU = [
    ("bo `pointer-events:none` — huy hieu an mat cu cham",
     "css/common.css", "pointer-events:none;user-select:none;", "user-select:none;"),
    ("doi huy hieu sang goc duoi-TRAI — de len `.env-badge`",
     "css/common.css", "position:fixed;right:10px;bottom:8px;",
     "position:fixed;left:12px;bottom:12px;"),
    ("bo lenh dung huy hieu — khong trang nao co no",
     "js/ui-common.js", '  } else { mountVersion(); }', "  } else { /* pha */ }"),
    ("aria-label khong doi theo ngon ngu (ghim tieng Viet)",
     "js/ui-common.js", 'var l = VER_LBL[lang === "en" ? "en" : "vi"];',
     'var l = VER_LBL.vi;'),
    ("so hieu tren man lech VERSION khai trong file",
     "js/ui-common.js", 'el.textContent = "v" + VERSION;',
     'el.textContent = "v0.0.0.0";'),
]

try:
    for nhan, f, cu, moi in THU:
        assert cu in GOC[f], f"khong tim thay chuoi de pha: {nhan}"
        io.open(f, "w", encoding="utf-8").write(GOC[f].replace(cu, moi, 1))
        h = hong()
        print(f"  {'[BAT DUOC]' if h else '[LOT   ] '} {nhan}")
        for x in h[:2]:
            print(f"              -> {x}")
        io.open(f, "w", encoding="utf-8").write(GOC[f])
finally:
    for p in FILES:
        io.open(p, "w", encoding="utf-8").write(GOC[p])
    print(f"\n  khoi phuc: {len(hong())} dong hong (phai la 0)")
