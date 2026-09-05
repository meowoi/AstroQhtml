# -*- coding: utf-8 -*-
"""Phep thu pha hoai cho probe_bar_height.py. Sao luu/khoi phuc bang BYTES."""
import io, subprocess, sys
ROOT = r"c:\Users\ADMIN\OneDrive\Desktop\astroq\AstroQhtml"
CASES = [
    ("A. bo display:block cua .rc-bar",  ROOT + r"\css\game-recycle.css",
     ".rc-bar{display:block;height:7px;", ".rc-bar{height:7px;"),
    ("B. bo display:block cua .cm-bar",  ROOT + r"\css\game-comms.css",
     ".cm-bar{display:block;position:relative;", ".cm-bar{position:relative;"),
    ("C. them mot thanh moi ma quen khai vao bang BARS", ROOT + r"\css\game-units.css",
     ".uc-flag{", ".uc-newbar{height:5px;}\n.uc-flag{"),
]
orig = {}
for _, p, _, _ in CASES:
    orig[p] = io.open(p, "rb").read()

def run():
    r = subprocess.run([sys.executable, "scratchpad/probe_bar_height.py"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = [l for l in (r.stdout or "").splitlines() if "dat /" in l]
    return (tail[-1] if tail else "(khong doc duoc)"), r.returncode

print("=== moc: chua pha ===")
print("   ", run()[0])
for name, p, old, new in CASES:
    cur = io.open(p, "rb").read().decode("utf-8")
    if cur.count(old) != 1:
        print("\n%s\n    BO QUA: moc khop %d lan" % (name, cur.count(old))); continue
    io.open(p, "wb").write(cur.replace(old, new, 1).encode("utf-8"))
    line, code = run()
    print("\n%s\n    -> %s  (exit %d)  %s" % (name, line, code, "BAT DUOC" if code != 0 else "!! LOT !!"))
    io.open(p, "wb").write(orig[p])

same = all(io.open(p, "rb").read() == orig[p] for p in orig)
print("\nkhoi phuc byte-dung-byte: %s" % same)
