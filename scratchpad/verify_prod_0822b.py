# -*- coding: utf-8 -*-
"""Do tren BAN THAT (astroq.org) sau lan push 22/08/2026 (ban dung 2026.08.22.2).

Chay:  python scratchpad/verify_prod_0822b.py

⚠️⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC, va DUNG HAN neu lech. Pages build
   mat ~1-2 phut; do truoc luc build xong thi MOI KET LUAN SAU DO deu noi ve BAN
   CU. Ngay 06/08/2026 ban that dung o ban 04/08 gan mot ngay, va do chinh la ly
   do huy hieu ban dung ton tai.
"""
import io
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "https://astroq.org"
WANT_VER = "2026.08.22.2"
dat = hong = 0


def check(nhan, dieu_kien, chi_tiet=""):
    global dat, hong
    if dieu_kien:
        dat += 1
        print("  [OK]   " + nhan + (("  (" + chi_tiet + ")") if chi_tiet else ""))
    else:
        hong += 1
        print("  [HONG] " + nhan + (("  (" + chi_tiet + ")") if chi_tiet else ""))


def get(path):
    """Tra (status, body, content-type). Them tham so chong cache."""
    url = BASE + path + ("&" if "?" in path else "?") + "cb=v0822b"
    req = urllib.request.Request(url, headers={"User-Agent": "astroq-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            # ⚠️ Ha chu thuong moi khoa header: API Gateway/Pages tra khac kieu chu,
            #    va `dict(r.headers)` lam mat tinh khong-phan-biet-hoa-thuong cua
            #    `email.message.Message` — bai hoc 18/08/2026.
            hdr = {k.lower(): v for k, v in r.headers.items()}
            return r.status, raw, hdr.get("content-type", "")
    except urllib.error.HTTPError as e:
        return e.code, b"", ""
    except Exception as e:
        return 0, str(e).encode(), ""


# ══ [1] SO HIEU BAN DUNG — TRUOC MOI THU KHAC ═════════════════════════════════
print("\n=== [1] So hieu ban dung ===")
st, body, _ = get("/js/ui-common.js")
txt = body.decode("utf-8", "replace")
ver = ""
for ln in txt.splitlines():
    if "var VERSION" in ln:
        ver = ln.split('"')[1] if '"' in ln else ""
        break
check("js/ui-common.js tra 200", st == 200, str(st))
check("ban dung dung " + WANT_VER, ver == WANT_VER, "doc duoc: %r" % ver)
if ver != WANT_VER:
    print("\n⚠️ DUNG HAN: ban that chua build xong (hoac push chua len). Moi ket luan")
    print("   sau day se noi ve BAN CU — khong chay tiep.")
    sys.exit(1)

# ══ [2] File da doi/them: 200 + MIME dung ════════════════════════════════════
print("\n=== [2] File tra 200 va MIME dung ===")
FILES = [
    ("/js/characters.js", "javascript"),
    ("/js/constellations.js", "javascript"),
    ("/js/sfx.js", "javascript"),
    ("/js/game-shell.js", "javascript"),
    ("/js/progress.js", "javascript"),
    ("/js/firebase-auth.js", "javascript"),
    ("/js/auth-flow.js", "javascript"),
    ("/css/cockpit.css", "css"),
    ("/css/game-shell.css", "css"),
    ("/img/rock-gray.png", "image/png"),
]
for path, mime in FILES:
    st, body, ct = get(path)
    check("%s -> 200, MIME co %r" % (path, mime),
          st == 200 and mime in ct.lower(), "st=%s ct=%s len=%d" % (st, ct, len(body)))

# ⚠️ Anh CU phai 404: `git mv` doi ten nen duong dan cu khong duoc con song —
#    con song nghia la Pages dang phuc vu mot ban cu.
st, _, _ = get("/img/racer/rock.png")
check("duong dan anh CU (img/racer/rock.png) tra 404", st == 404, "st=%s" % st)

# ══ [3] Noi dung: 5 fix + cau noi nhan vat + nhan chip ═══════════════════════
print("\n=== [3] Noi dung tren ban that ===")

_, b, _ = get("/game-constellation.html")
s = b.decode("utf-8", "replace")
check("Ghep Chom Sao co `briefKey` (man brief giu loi hua)", "briefKey" in s)
check("khong con doc `astroq-constellation-best` truc tiep o trang game",
      "astroq-constellation-best" not in s)

_, b, _ = get("/js/constellations.js")
s = b.decode("utf-8", "replace")
check("js/constellations.js la cho DUY NHAT doc/ghi ky luc trong may",
      "localBests" in s and "saveLocalBest" in s)
check("ban ghi ky luc dong dau uid", '"uid"' in s or "uid" in s)

_, b, _ = get("/js/sfx.js")
s = b.decode("utf-8", "replace")
check("rumble() TU TAT sau ms (mac dinh 1200)", "1200" in s and "hush" in s)

for g, nhan in [("/game-racer.html", "racer"), ("/game-catch.html", "catch"),
                ("/game-maze.html", "maze")]:
    _, b, _ = get(g)
    check("%s chan auto-repeat (e.repeat) khi bat dau lai" % nhan,
          "e.repeat" in b.decode("utf-8", "replace"))

_, b, _ = get("/js/characters.js")
s = b.decode("utf-8", "replace")
for fn in ("absorb", "syncUp", "sync", "touch"):
    check("js/characters.js co `%s` (cau noi cache <-> server)" % fn, fn in s)

_, b, _ = get("/js/auth-flow.js")
s = b.decode("utf-8", "replace")
check("select.html: tre CU thay cau chu rieng (`returning()`)", "returning" in s)
check("3 khoa i18n cho tre cu", all(k in s for k in ("title_back", "subtitle_back", "start_back")))

_, b, _ = get("/css/game-shell.css")
s = b.decode("utf-8", "replace")
check("nhan chip HUD chiem ca mot hang (flex-wrap + flex:1 0 100%)",
      "flex-wrap:wrap" in s.replace(" ", "") and "flex:1 0 100%" in s.replace("  ", " "))

_, b, _ = get("/game-defender.html")
s = b.decode("utf-8", "replace")
check("Phong Thu: cau do lay tu kho chung (khong chi mang 8 cau)",
      "astroq-defender-asked" in s and "QUIZ_FALLBACK" in s)

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
