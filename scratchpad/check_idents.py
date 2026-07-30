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
for grp in re.findall(r"\bvar\s+([^;]+);", clean):           # var a=1, b=2
    declared |= set(re.findall(r"([\w$]+)\s*=", grp)) | set(re.findall(r"(?:^|,)\s*([\w$]+)\s*(?:,|$)", grp))
declared |= set(re.findall(r"\bfunction\s+([\w$]+)", clean))
for params in re.findall(r"function\s*[\w$]*\s*\(([^)]*)\)", clean):
    declared |= set(x.strip() for x in params.split(",") if x.strip())
declared |= set(re.findall(r"\bcatch\s*\(\s*([\w$]+)", clean))

GLOBALS = set("""window document localStorage Math JSON Image Date console this true false null undefined
NaN Infinity typeof new delete in instanceof void return if else for while do break continue switch case
default function var let const try catch finally throw arguments requestAnimationFrame setTimeout
clearTimeout setInterval clearInterval AudioContext webkitAudioContext ResizeObserver navigator
Economy AstroQ CustomEvent Number String Boolean Array Object parseInt parseFloat isNaN encodeURIComponent
decodeURIComponent alert matchMedia performance Element HTMLElement""".split())

# ten thuoc tinh sau dau '.' hoac truoc ':' trong object literal thi bo qua
no_prop = re.sub(r"\.\s*[\w$]+", ".", clean)
no_prop = re.sub(r"[{,]\s*[\w$]+\s*:", "{", no_prop)

used = set(re.findall(r"(?<![\w$.])([A-Za-z_$][\w$]*)(?![\w$]*\s*:)", no_prop))
free = sorted(u for u in used if u not in declared and u not in GLOBALS)

print("Bien/ham da khai bao:", len(declared))
print("Ten tu do (khong khai bao, khong phai global quen biet):")
if free:
    for f in free: print("   ?", f)
else:
    print("   (khong co)")
sys.exit(1 if free else 0)
