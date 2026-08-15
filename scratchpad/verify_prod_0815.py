# -*- coding: utf-8 -*-
"""Do tren BAN THAT sau khi Pages build. Nhan print KHONG DAU.
CANH BAO: KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC — do truoc luc build xong thi
moi ket luan deu sai (06/08/2026 ban that dung o ban cu gan mot ngay).
"""
import re, sys, urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SITE = "https://astroq.org"
WANT_VER = "2026.08.15.1"
dat = hong = 0


def check(name, ok, info=""):
    global dat, hong
    if ok:
        dat += 1
        print("  [OK]   %s  %s" % (name, info))
    else:
        hong += 1
        print("  [HONG] %s  %s" % (name, info))


def get(path):
    req = urllib.request.Request(SITE + path, headers={"User-Agent": "astroq-verify"})
    r = urllib.request.urlopen(req, timeout=30)
    return r.getcode(), r.read().decode("utf-8", "replace")


print("[1] So hieu ban dung (kiem TRUOC moi thu khac)")
code, ui = get("/js/ui-common.js")
m = re.search(r'var VERSION = "([\d.]+)"', ui)
check("ui-common.js tra 200", code == 200, str(code))
check("ban dung dung " + WANT_VER, m and m.group(1) == WANT_VER,
      m.group(1) if m else "khong doc duoc")
if not (m and m.group(1) == WANT_VER):
    print("\n=> Pages CHUA build xong. Dung lai, cho roi chay lai.")
    sys.exit(2)

print("\n[2] File moi cua dot menu tha")
for p, mime in [("/js/user-menu.js", "javascript"), ("/css/user-menu.css", "css")]:
    req = urllib.request.Request(SITE + p, headers={"User-Agent": "astroq-verify"})
    r = urllib.request.urlopen(req, timeout=30)
    ct = r.headers.get("Content-Type", "")
    check("%s: 200 + MIME dung" % p, r.getcode() == 200 and mime in ct, ct)

print("\n[3] Luat phi <-> do kho da toi tay tre")
_, eco = get("/economy.js")
mm = re.search(r"var FEES = \{([^}]*)\}", eco)
fees = dict((k, int(v)) for k, v in re.findall(r"(\w+):\s*(\d+)", mm.group(1)))
WANT = {"constellation": 3, "maze": 3, "catch": 4, "racer": 4, "defender": 4, "dodge": 5}
check("economy.js mang bang phi moi", fees == WANT, str(fees))

for f, want in [("game-maze.html", 3), ("game-catch.html", 4),
                ("game-racer.html", 4), ("game-defender.html", 4),
                ("game-dodge.html", 5)]:
    _, s = get("/" + f)
    c = re.search(r"COST:\s*(\d+)", s)
    check("%s: CONFIG.COST = %d" % (f, want), c and int(c.group(1)) == want,
          c.group(1) if c else "?")

print("\n[4] Bo phan doc them + nhan phan loai canh icon")
_, tr = get("/js/training.js")
check("js/training.js khong con khoi 'read'", "read:" not in tr and "read(" not in tr,
      "%d ky tu" % len(tr))
_, gh = get("/games.html")
check("games.html khong con khoa read_lb", "read_lb" not in gh)
check("games.html co .gc-head (nhan canh icon)", "gc-head" in gh)
_, gc = get("/css/games.css")
check("css/games.css co rule .gc-head", ".gc-head" in gc)

print("\n[5] Can doi thuong hoc")
_, q = get("/quiz.html")
a = re.search(r"var AWARD = (\d+)", q)
check("quiz.html AWARD = 6", a and int(a.group(1)) == 6, a.group(1) if a else "?")

print("\n[6] Me cung: cong khoa + 4 cap")
_, mz = get("/game-maze.html")
check("co khoa i18n gate_locked", "gate_locked" in mz)
check("co bang tiers (4 cap)", mz.count("cols:") >= 4, "%d muc cols:" % mz.count("cols:"))
check("luu cap o astroq-maze-tier", "astroq-maze-tier" in mz)

print("\n[7] Bat Sao Bang: nghe pointermove tren window")
_, ct2 = get("/game-catch.html")
check("window.addEventListener('pointermove')",
      re.search(r'window\.addEventListener\(\s*"pointermove"', ct2) is not None)

print("\n[8] API ban that con song")
import json
req = urllib.request.Request(
    "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com/health")
check("/health 200", urllib.request.urlopen(req, timeout=30).getcode() == 200)

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
