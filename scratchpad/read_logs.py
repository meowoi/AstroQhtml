# -*- coding: utf-8 -*-
"""Doc CloudWatch, ghep dong tieu de muc do voi dong NOI DUNG ngay sau no.

⚠️ Moi ban ghi cua ASP.NET la HAI su kien CloudWatch roi nhau:
   "warn: <Category>[id]" roi moi toi cau chu that. Loc theo `--filter-pattern`
   chi bat duoc dong tieu de, nen phai lay HET roi ghep theo thu tu.
⚠️ Khong doc bang PowerShell: console cp1252 chet o chu Viet giua chung.
"""
import json
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MINUTES = int(sys.argv[1]) if len(sys.argv) > 1 else 45
start = int((time.time() - MINUTES * 60) * 1000)

# ⚠️ `aws` CLI cung la Python: khong dat PYTHONIOENCODING thi CHINH NO chet o
#    chu Viet ("charmap codec can't encode") va tra ve JSON CUT GIUA CHUNG.
import os
env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
out = subprocess.run(
    ["aws", "logs", "filter-log-events",
     "--log-group-name", "/aws/lambda/AstroqSV",
     "--start-time", str(start), "--output", "json"],
    capture_output=True, text=False, shell=True, env=env)
data = json.loads(out.stdout.decode("utf-8", "replace"))
ev = [e["message"].rstrip("\n") for e in data["events"]]

print(f"=== {len(ev)} su kien trong {MINUTES} phut ===\n")

LEVELS = ("warn: ", "fail: ", "crit: ")
found = {}
for i, m in enumerate(ev):
    if m.startswith(LEVELS):
        body = ev[i + 1] if i + 1 < len(ev) else "(khong co dong sau)"
        key = (m, body)
        found[key] = found.get(key, 0) + 1

print("--- Canh bao / loi, gom theo noi dung ---")
for (hdr, body), n in sorted(found.items(), key=lambda kv: -kv[1]):
    print(f"  {n:>3}x  {hdr}\n         {body[:200]}")

hard = [m for m in ev if "Unhandled exception" in m or m.startswith("ERROR")]
print(f"\n--- Loi that (Unhandled / ERROR): {len(hard)} ---")
for m in hard[:10]:
    print("  " + m[:200])
