# -*- coding: utf-8 -*-
"""gap_lv.py — CHO NAO CON THIEU: liet ke tung the con thieu cap do nao.

Vi sao dung cai nay lam BAN DO TRA NO NOI DUNG (chot 19/08/2026): tu khi
`pickKeys(n, lv)` doc `lv` thi mot the thieu cap la mot the phai lay cau gan cap
nhat — nghia la o cap do ay dua tre nhan mot cau khong dung suc minh. "Them cau
cho du" khong noi ro phai them cau NAO; bang nay noi ro.

Doc `js/quiz-index.js` (SINH RA) — khong doc lai 106 file.

  python scratchpad/gap_lv.py
"""
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IX = io.open(os.path.join(ROOT, "js", "quiz-index.js"), encoding="utf-8").read()

LV = dict((m.group(1), int(m.group(2)))
          for m in re.finditer(r'"([^"]+)":\s*(\d+)',
                               IX.split("var LV = {")[1].split("};")[0]))

# Bang G: moi nhom { c: "term_x", t: "...", q: [khoa...] }
gblock = IX.split("var G = [")[1]
gblock = gblock[:gblock.index("\n  ];")]
groups = []
# ⚠️ KHONG dung mot regex `\{ c: ... q: \[...\]`: khoi `t: { vi:…, en:… }` nam GIUA
#    hai truong nen moi lop `[^}]*?` deu dung som o dau dong `en:`. Cat theo bien
#    `{ c: "` roi doc `q:` trong tung manh — do duoc, khong doan.
for chunk in gblock.split('{ c: "')[1:]:
    card = chunk.split('"', 1)[0]
    qs = re.search(r"q:\s*\[([^\]]*)\]", chunk, re.S)
    if not qs:
        sys.exit("the %s khong tim thay `q:`" % card)
    groups.append((card, re.findall(r'"([^"]+)"', qs.group(1))))

print("=== %d the / %d cau ===\n" % (len(groups), len(LV)))
gaps = []
for card, keys in groups:
    have = {}
    for k in keys:
        have.setdefault(LV.get(k, 0), []).append(k)
    thieu = [lv for lv in (1, 2, 3) if lv not in have]
    mark = "  " if not thieu else "!!"
    print("%s %-26s %d cau  cap co: %s%s"
          % (mark, card, len(keys), sorted(have.keys()),
             ("   THIEU cap %s" % thieu) if thieu else ""))
    for lv in thieu:
        gaps.append({"card": card, "lv": lv, "has": sorted(have.keys()),
                     "keys": keys})

print("\n=== TONG: %d cho thieu tren %d the ==="
      % (len(gaps), len(set(g["card"] for g in gaps))))
by = {}
for g in gaps:
    by.setdefault(g["lv"], []).append(g["card"])
for lv in (1, 2, 3):
    c = by.get(lv, [])
    print("  thieu cap %d: %d the  %s" % (lv, len(c), ", ".join(c)))

out = os.path.join(ROOT, "scratchpad", "gap_lv.json")
io.open(out, "w", encoding="utf-8", newline="").write(
    json.dumps(gaps, ensure_ascii=False, indent=1))
print("\nda ghi %s" % out)
