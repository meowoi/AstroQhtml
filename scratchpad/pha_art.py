# -*- coding: utf-8 -*-
"""Phep thu pha hoai: gay 4 loi co y roi do xem bo kiem co bat duoc khong."""
import io, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

FILES = ["js/specimens.js", "js/specimen-art.js", "css/common.css", "dashboard.html"]
BAK = {f: io.open(f, encoding="utf-8", newline="").read() for f in FILES}

def run():
    r = subprocess.run([sys.executable, "scratchpad/check_specimen_art.py"],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    out = (r.stdout or "") + (r.stderr or "")
    bad = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    good = [l for l in out.splitlines() if l.strip().startswith("PASS")]
    # MOT BO DO TU CHET ROI DEM RA "0 hong" doc ra y nhu "phep kiem mu".
    # Dem ca so PASS: 0 PASS nghia la no khong chay, khong phai no dat.
    return len(bad), bad, len(good)

def put(f, s):
    io.open(f, "w", encoding="utf-8", newline="").write(s)

try:
    cases = []

    # 1. icon() quay ve emoji tho (bo lop SVG)
    s = BAK["js/specimens.js"].replace(
        'var art = global.AstroQSpecimenArt ? global.AstroQSpecimenArt.svg(id) : "";',
        'var art = "";')
    put("js/specimens.js", s)
    cases.append(("icon() quay ve emoji tho", run()))
    put("js/specimens.js", BAK["js/specimens.js"])

    # 2. .spart mat width/height -> khong do co theo font-size
    s = BAK["css/common.css"].replace(
        ".spart{width:1em;height:1em;display:inline-block;vertical-align:-0.14em;flex:none;}",
        ".spart{display:inline-block;vertical-align:-0.14em;flex:none;}")
    put("css/common.css", s)
    cases.append((".spart mat width/height", run()))
    put("css/common.css", BAK["css/common.css"])

    # 3. bo hau to {n} -> id gradient trung nhau
    s = BAK["js/specimen-art.js"].replace("var k = ++n;", "var k = 1;")
    put("js/specimen-art.js", s)
    cases.append(("id gradient trung nhau", run()))
    put("js/specimen-art.js", BAK["js/specimen-art.js"])

    # 4. xoa mot muc tranh -> thieu phu
    s = BAK["js/specimen-art.js"]
    i = s.index('"orion-stardust": {')
    j = s.index("\n  };", i)
    put("js/specimen-art.js", s[:i] + '"__bo__": { defs:"", body:"" }' + s[j:])
    cases.append(("xoa tranh cua mot mau vat", run()))
    put("js/specimen-art.js", BAK["js/specimen-art.js"])

    for name, (nbad, bad, ngood) in cases:
        flag = "" if ngood else "   <-- BO DO KHONG CHAY (0 PASS)"
        print("  %-34s -> %d HONG / %d dat%s" % (name, nbad, ngood, flag))
        for b in bad[:3]:
            print("       " + b)
finally:
    for f, s in BAK.items():
        put(f, s)
    print("\n  da khoi phuc %d file" % len(BAK))
