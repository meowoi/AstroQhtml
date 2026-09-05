# -*- coding: utf-8 -*-
"""Do ARCADE-12 tren BAN THAT (astroq.org) sau khi push.

  py -3 scratchpad/verify_prod_0906.py

⚠️⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC, va DUNG HAN neu lech. Pages
   build mat 1-2 phut; do truoc luc build xong thi moi phep kiem sau do noi ve
   BAN CU va "dat" mot cach RONG. 06/08/2026 ban that tung dung o ban cu gan
   mot ngay ma khong ai biet.

⚠️ File moi la ES module / CSS: Pages tra `text/plain` thi trinh duyet TU CHOI
   — nen phai do MIME chu khong duoc gia dinh.
"""
import sys, io, re, urllib.request

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

SITE = "https://astroq.org"
WANT = "2026.09.06.1"

ok = bad = 0
def ck(name, cond, detail=""):
    global ok, bad
    if cond: ok += 1; print(f"  [OK]   {name}")
    else:    bad += 1; print(f"  [HONG] {name}   {detail}")

def get(path):
    req = urllib.request.Request(SITE + path, headers={"User-Agent": "astroq-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")

# ── [0] So hieu ban dung — CHOT CHAN ─────────────────────────────
print("[0] So hieu ban dung")
try:
    st, _, ui = get("/js/ui-common.js")
    m = re.search(r'var VERSION\s*=\s*"([^"]+)"', ui)
    got = m.group(1) if m else "?"
except Exception as e:
    print(f"  [DUNG] khong doc duoc js/ui-common.js: {e}")
    sys.exit(2)
if got != WANT:
    print(f"  [DUNG] ban that dang o {got}, doi {WANT} — Pages chua build xong.")
    sys.exit(2)
ck(f"ban dung = {WANT}", True)

# ── [1] File moi tra 200 voi MIME dung ───────────────────────────
print("\n[1] File moi tren Pages")
for path, want_mime in (("/game-classify.html", "text/html"),
                        ("/css/game-classify.css", "text/css"),
                        ("/js/teach-machine.js", "javascript"),
                        ("/img/og/game-classify.jpg", "image/jpeg")):
    try:
        st, mime, _ = get(path)
        ck(f"{path} 200 + MIME dung", st == 200 and want_mime in mime, f"{st} {mime}")
    except Exception as e:
        ck(f"{path} 200 + MIME dung", False, str(e))

# ── [2] Nhan nut suy tu CONFIG.COST (loi vua sua o cong) ─────────
print("\n[2] Nhan nut Choi lai")
_, _, page = get("/game-classify.html")
ck("nhan nut la GETTER suy tu CONFIG.COST",
   page.count("get again_btn()") == 2 and page.count("CONFIG.COST") >= 2,
   f'getter={page.count("get again_btn()")}')
ck("KHONG con go cung so trong nhan nut",
   "Chơi lại · <b>3</b> <img" not in page and "Play again · <b>3</b> <img" not in page)

# ── [3] Bo phan loai: 0 thu vien ML, 0 byte mang ─────────────────
print("\n[3] js/teach-machine.js")
_, _, tm = get("/js/teach-machine.js")
ck("FEAT chi gom len + curve (bright bi bo qua)",
   re.search(r'var FEAT\s*=\s*\[\s*"len"\s*,\s*"curve"\s*\]', tm) is not None)

# ⚠️ QUET TREN BAN DA BOC CHU THICH. Lan chay dau bao hong `Math.random`, thu
#    pham la chinh doan ghi chu GIAI THICH vi sao khong dung no — loi "dem ca
#    chu trong ghi chu cua chinh minh", da lap rat nhieu lan trong du an. Sua o
#    BO KIEM, dung viet lai ghi chu de ne.
code = re.sub(r'/\*.*?\*/', '', tm, flags=re.S)
code = re.sub(r'^\s*//.*$', '', code, flags=re.M)
ck("0 loi goi mang", not any(s in code for s in ("fetch(", "XMLHttpRequest", "import(")))
ck("0 Math.random (bo phan loai TAT DINH)", "Math.random" not in code)

# ── [4] Da mo het, 12 the game ───────────────────────────────────
print("\n[4] Khu Huan Luyen")
_, _, hub = get("/games.html")
files = re.findall(r'file:"(game-[a-z-]+\.html)"', hub)
ck("12 the game", len(files) == 12, str(len(files)))
ck("co the classify", "game-classify.html" in files)
ck("0 the khoa", hub.count('status:"soon"') == 0, str(hub.count('status:"soon"')))

print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
