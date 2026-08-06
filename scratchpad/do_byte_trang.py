# -*- coding: utf-8 -*-
r"""Do byte JS that su tai ve cua tung trang — DOC THE <script src>, khong grep ten file.

⚠️ BAI HOC 06/08/2026: ban do dau tien cua toi tim ten file bang `in` tren ca trang,
   nen no dem ca ten file nam trong MOT DONG GHI CHU va bao rang `quiz.html` tai
   `codex-terms.js` (+17,9 KB). Sai. Quiz khong he nap file do — no chi nhac ten
   trong comment. Dung cai bay "dem bang grep mot tu roi ghi con so vao tai lieu"
   ma du an da ghi thanh luat.
"""
import gzip
import io
import os
import re

TRANG = ["quiz.html", "codex.html", "library.html", "learn.html",
         "dashboard.html", "index.html"]


def gz_file(p):
    if not os.path.exists(p):
        return None
    return len(gzip.compress(io.open(p, encoding="utf-8").read().encode("utf-8"), 9))


print("=== JS TAI VE THAT SU CUA TUNG TRANG (gzip) ===")
for p in TRANG:
    s = io.open(p, encoding="utf-8").read()
    # chi lay THE <script src=...>, va bo qua thu nam trong comment HTML
    sach = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    srcs = re.findall(r'<script[^>]*\ssrc="([^"]+)"', sach)
    noi = [x for x in srcs if not x.startswith(("http://", "https://", "//"))]
    tong = 0
    dong = []
    for x in noi:
        n = gz_file(x.lstrip("./"))
        if n is None:
            dong.append(f"{x}(?)")
            continue
        tong += n
        dong.append(f"{x} {n/1024:.1f}")
    ngoai = [x for x in srcs if x.startswith(("http", "//"))]
    print(f"\n  {p}  →  {tong/1024:5.1f} KB gzip" + (f"  + {len(ngoai)} script NGOAI" if ngoai else ""))
    for d in dong:
        print(f"      {d}")
    for x in ngoai:
        print(f"      [NGOAI] {x[:70]}")
