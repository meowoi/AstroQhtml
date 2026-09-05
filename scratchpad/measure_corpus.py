# -*- coding: utf-8 -*-
"""Đo kho ngữ liệu tiếng Việt đang có trong repo — nguyên liệu cho game Next Token."""
import glob
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Chuỗi dài trong mã nguồn = câu chữ cho trẻ đọc (bỏ khoá, id, class ngắn).
PAT = re.compile(r'"([^"\\]{25,})"')


def fmt(n):
    return f"{n:,}".replace(",", ".")


def scan(pattern):
    out, n = [], 0
    for f in glob.glob(pattern):
        n += 1
        t = io.open(f, encoding="utf-8", errors="ignore").read()
        for m in PAT.findall(t):
            out += m.split()
    return n, out


af, aw = scan("js/article/*.js")
print("bai doc     :", af, "file ·", fmt(len(aw)), "tu")

qf, qw = scan("js/quiz/*.js")
print("quiz        :", qf, "file ·", fmt(len(qw)), "tu")

lw = []
lf = 0
for f in glob.glob("learningdata/**/*.json", recursive=True):
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception:
        continue
    lf += 1
    lw += re.findall(r"\w+", json.dumps(d, ensure_ascii=False))
print("learningdata:", lf, "file ·", fmt(len(lw)), "tu")

allw = aw + qw + lw
print("TONG        :", fmt(len(allw)), "tu ·", fmt(len(set(allw))), "tu khac nhau")

# Bigram: bao nhieu cap tu KHAC NHAU -> quyet dinh co the ship mot mo hinh n-gram khong.
big = {}
for i in range(len(allw) - 1):
    k = allw[i]
    big.setdefault(k, {})
    big[k][allw[i + 1]] = big[k].get(allw[i + 1], 0) + 1
print("bigram      :", fmt(len(big)), "tu dung truoc ·",
      fmt(sum(len(v) for v in big.values())), "cap khac nhau")

# Nhung tu co nhieu lua chon tiep theo NHAT — chinh la nhung cho choi duoc.
rich = sorted(big.items(), key=lambda kv: -len(kv[1]))[:12]
print("\nTu co nhieu kha nang di sau nhat (cho choi duoc cua Next Token):")
for w, nxt in rich:
    top = sorted(nxt.items(), key=lambda kv: -kv[1])[:4]
    tot = sum(nxt.values())
    s = "  ".join("%s %d%%" % (t[0], round(100 * t[1] / tot)) for t in top)
    print("  %-14s (%3d kha nang)  ->  %s" % (w, len(nxt), s))
