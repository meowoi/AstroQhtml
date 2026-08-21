# -*- coding: utf-8 -*-
"""Tim bien/ham dung nhung chua khai bao trong script inline (bat loi go sai ten)."""
import re, io, sys

import os
_here = os.path.dirname(os.path.abspath(__file__))
p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_here, "..", "game-dodge.html")
src = io.open(p, encoding="utf-8").read()
js = re.findall(r"<script>(.*?)</script>", src, re.S)[0]

# bo chuoi + comment
def strip_js(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == "/" and i + 1 < n and s[i+1] == "*":
            j = s.find("*/", i + 2); i = (j + 2) if j >= 0 else n; continue
        if c == "/" and i + 1 < n and s[i+1] == "/":
            j = s.find("\n", i); i = j if j >= 0 else n; continue
        if c in "\"'":
            q = c; i += 1
            while i < n and s[i] != q:
                if s[i] == "\\": i += 1
                i += 1
            i += 1; out.append(' "" '); continue
        out.append(c); i += 1
    return "".join(out)

clean = strip_js(js)

declared = set()
declared |= set(re.findall(r"\bvar\s+([\w$]+)", clean))
# CANH BAO: `var a, b;` VA `var a = f(x), b = g(y);` — phai lay HET ten khai bao.
#   Ban cu dung `var\s+([^;]+);` roi tach theo dau phay, va no bo sot 2 kieu:
#     (1) `var px, py;`  — mau `(?:^|,)...(?:,|$)` an mat dau phay nen `py` lot;
#     (2) `var xs = st.map(function(s){ return s.x; }), ys = ...;`  — `[^;]+`
#         dung o dau `;` NAM TRONG than ham, nen `ys` khong bao gio thay.
#   Ca hai lam bo do bao "ten tu do" OAN (21/08/2026: py o game-maze,
#   ys o game-constellation). Mot phep kiem hay bao oan thi som muon bi bo qua,
#   nen sua o BO DO. Nay quet co biet long ngoac.
def _var_names(code):
    """Ten khai bao trong moi cau `var`, biet long ngoac ()[]{}."""
    out = set()
    for m in re.finditer(r"\bvar\s", code):
        i, d, seg = m.end(), 0, []
        while i < len(code):
            c = code[i]
            if c in "([{": d += 1
            elif c in ")]}":
                if d == 0: break
                d -= 1
            elif d == 0 and c == ";": break
            seg.append(c); i += 1
        parts, part, d = [], [], 0
        for c in "".join(seg):
            if c in "([{": d += 1
            elif c in ")]}": d -= 1
            if c == "," and d == 0:
                parts.append("".join(part)); part = []
            else:
                part.append(c)
        parts.append("".join(part))
        for p in parts:
            g = re.match(r"\s*([A-Za-z_$][\w$]*)", p)
            if g: out.add(g.group(1))
    return out

declared |= _var_names(clean)
declared |= set(re.findall(r"\bfunction\s+([\w$]+)", clean))
for params in re.findall(r"function\s*[\w$]*\s*\(([^)]*)\)", clean):
    declared |= set(x.strip() for x in params.split(",") if x.strip())
declared |= set(re.findall(r"\bcatch\s*\(\s*([\w$]+)", clean))

# CANH BAO: danh sach nay phai gom moi global do cac file DUNG CHUNG mo ra.
# Thieu mot ten la bo do bao "ten tu do" OAN, va mot phep kiem hay bao oan
# thi som muon nguoi ta bo qua no. Ngay 21/08/2026 no bao oan 3 ten:
#   $ (js/ui-common.js) - AstroQGameShell (js/game-shell.js)
#   AstroQProgress (js/progress.js)
# Ba file do ra doi SAU lan cap nhat danh sach cuoi, nen no lac hau am tham.
# Them mot file dung chung mo global moi thi THEM TEN VAO DAY.
GLOBALS = set("""window document localStorage Math JSON Image Date console this true false null undefined
NaN Infinity typeof new delete in instanceof void return if else for while do break continue switch case
default function var let const try catch finally throw arguments requestAnimationFrame setTimeout
clearTimeout setInterval clearInterval AudioContext webkitAudioContext ResizeObserver navigator
Economy AstroQ CustomEvent
$ AstroQGameShell AstroQProgress AstroQSfx AstroQCos AstroQBrag AstroQSpecimens AstroQSpecimenArt Number String Boolean Array Object parseInt parseFloat isNaN encodeURIComponent
decodeURIComponent alert matchMedia performance Element HTMLElement location history screen""".split())

# ten thuoc tinh sau dau '.' hoac truoc ':' trong object literal thi bo qua,
# va ca ten cua getter/setter (`get cols(){...}`) - do cung la ten THUOC TINH.
no_prop = re.sub(r"(?:get|set)\s+[\w$]+\s*\(", "(", clean)
no_prop = re.sub(r"\.\s*[\w$]+", ".", no_prop)
no_prop = re.sub(r"[{,]\s*[\w$]+\s*:", "{", no_prop)

# CANH BAO: `strip_js` boc CHUOI va CHU THICH nhung KHONG boc REGEX LITERAL
#   (phan biet `/` chia voi `/` mo regex la viec khong lam bang mot vong quet
#   don gian). Nen day escape trong regex ro ra thanh "ten bien": ngay
#   21/08/2026 `/\B(?=(\d{3})+(?!\d))/g` o game-racer.html lam bo do bao oan
#   mot ten tu do la `B`. Bo moi `\<chu cai>` truoc khi doc ten la du —
#   sau khi da boc chuoi thi day escape chi con den tu regex literal.
#   (Cung ho voi diem mu cua `_no_comments()` da ghi o CLAUDE.md.)
no_prop = re.sub(r"\\[A-Za-z]", "", no_prop)
used = set(re.findall(r"(?<![\w$.])([A-Za-z_$][\w$]*)(?![\w$]*\s*:)", no_prop))
free = sorted(u for u in used if u not in declared and u not in GLOBALS)

print("Bien/ham da khai bao:", len(declared))
print("Ten tu do (khong khai bao, khong phai global quen biet):")
if free:
    for f in free: print("   ?", f)
else:
    print("   (khong co)")
sys.exit(1 if free else 0)
