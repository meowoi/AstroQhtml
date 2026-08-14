# -*- coding: utf-8 -*-
"""Do do NHAY CUA THANH HUD khi con so doi do dai.

Tre choi thi diem chay 0 → 9 → 99 → 999 → 9999 lien tuc. Neu chip doi CHIEU CAO
hay doi BE RONG theo do dai con so thi ca cot HUD nhay lien tuc trong luc dang
choi — vua kho doc vua trong nhu loi.

  python -m http.server 8123     (trong AstroQhtml/)
  py -3 scratchpad/probe_hud_jitter.py
"""
import sys
from playwright.sync_api import sync_playwright

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

BASE = "http://127.0.0.1:8123"
ok = bad = 0
def ck(n, c, d=""):
    global ok, bad
    if c: ok += 1; print(f"  [OK]   {n}" + (f"  ({d})" if d else ""))
    else: bad += 1; print(f"  [HONG] {n}  {d}")

# Con so tang dan do dai.
# ⚠️ TACH LAM HAI: `CORE` la dai tre GAP THUONG XUYEN (toi 4 chu so) — cho nay
#    doi hoi ON DINH TUYET DOI o moi kho man. `EXTREME` (5 chu so) chi doi hoi
#    on dinh o CONSOLE DOC; tren man hep no CO Y duoc phep doi mot lan, vi dat
#    truoc be rong de tri no se lam catch va racer mat han mot hang o MOI luot
#    (so do ghi trong css/game-shell.css). In ra so lieu chu khong im lang.
CORE    = ["0", "7", "42", "371", "2371"]
EXTREME = ["13820"]

GAMES = [
    ("game-dodge.html",       ["score", "dist", "gem", "best"]),
    ("game-defender.html",    ["score", "gem", "best"]),
    ("game-racer.html",       ["score", "gem", "best"]),
    ("game-catch.html",       ["score", "gem", "best"]),
]

with sync_playwright() as p:
    br = p.chromium.launch()
    for page, ids in GAMES:
        print(f"\n=== {page}")
        for vp, label in [({"width":1440,"height":900}, "desktop"),
                          ({"width":390,"height":844},  "dien thoai")]:
            ctx = br.new_context(viewport=vp)
            ctx.add_init_script(
                "localStorage.setItem('astroq-lang','vi');"
                "localStorage.setItem('astroq-asteroids','999');")
            pg = ctx.new_page()
            pg.goto(f"{BASE}/{page}", wait_until="domcontentloaded")
            try:
                pg.wait_for_selector(".chip", timeout=8000)
            except Exception:
                print(f"  (bo qua {label}: khong thay .chip)"); ctx.close(); continue

            # Tim cac o gia tri co that tren trang nay
            live = [i for i in ids if pg.locator(f"#{i}").count() == 1]
            if not live:
                print(f"  (bo qua {label}: khong thay o gia tri nao)"); ctx.close(); continue

            steps = CORE + (EXTREME if label == "desktop" else [])
            hs, ws, hud_h = [], [], []
            for v in steps:
                pg.evaluate(
                    """(a)=>{ a.ids.forEach(i=>{const e=document.getElementById(i);
                              if(e) e.textContent = a.v;}); }""",
                    {"ids": live, "v": v})
                pg.wait_for_timeout(60)
                box = pg.evaluate("""()=>{
                  const cs=[...document.querySelectorAll('.chip')];
                  const hud=document.querySelector('.hud');
                  return { h: cs.map(c=>Math.round(c.getBoundingClientRect().height)),
                           w: cs.map(c=>Math.round(c.getBoundingClientRect().width)),
                           hh: hud?Math.round(hud.getBoundingClientRect().height):0 };
                }""")
                hs.append(box["h"]); ws.append(box["w"]); hud_h.append(box["hh"])

            # ⚠️ SO CUNG MOT CHIP QUA CAC BUOC, khong so chip nay voi chip kia.
            #    Ban dau toi lay max(max(h)) - min(min(h)) — no so chieu cao chip A
            #    voi chip B (vd chip co anh tt cao hon chip chi co chu) va bao hong
            #    OAN o 4/6 truong hop, trong khi so lieu that cho thay chieu cao
            #    KHONG he doi theo do dai con so. Phep do sai, khong phai san pham sai.
            dh = max(max(col) - min(col) for col in zip(*hs)) if hs and hs[0] else 0
            dhud = max(hud_h) - min(hud_h)
            dw = max(max(col) - min(col) for col in zip(*ws)) if ws and ws[0] else 0

            ck(f"{label}: chieu cao chip KHONG doi theo do dai so", dh == 0, f"lech {dh}px · {hs}")
            ck(f"{label}: chieu cao ca thanh HUD KHONG doi", dhud == 0, f"lech {dhud}px · {hud_h}")
            # ⚠️ BE RONG: DOI HOI CHAT o console doc, GHI NHAN o thanh ngang hep.
            #    Da do het cac phuong an cho man 390px va KHONG cai nao vua giu
            #    duoc mot hang vua on dinh (so lieu day du trong css/game-shell.css):
            #    dat truoc 3ch → racer mat mot hang · 4ch → catch va racer mat mot
            #    hang · an chip Ky luc + 4ch → dodge van lech 14px vi o quang duong
            #    con kem chu "m". Doi lay san choi to hon o MOI luot la dung.
            #    Ghi nhan bang SO chu khong im lang — de lan sau khong ai do lai.
            if label == "desktop":
                ck(f"{label}: be rong tung chip KHONG doi", dw == 0, f"lech {dw}px")
            else:
                print(f"  [ghi nhan] {label}: be rong chip lech {dw}px trong dai thuong gap"
                      + ("  — da on dinh" if dw == 0 else "  — danh doi co y, xem CSS"))

            # Man hep: KHONG doi hoi, nhung PHAI IN RA — mot danh doi im lang thi
            # lan sau khong ai biet no la danh doi hay la lo.
            if label != "desktop":
                base = hud_h[0]
                for v in EXTREME:
                    pg.evaluate(
                        """(a)=>{ a.ids.forEach(i=>{const e=document.getElementById(i);
                                  if(e) e.textContent = a.v;}); }""",
                        {"ids": live, "v": v})
                    pg.wait_for_timeout(60)
                    hh = pg.evaluate("()=>{const h=document.querySelector('.hud');"
                                     "return h?Math.round(h.getBoundingClientRect().height):0;}")
                    print(f"         (ghi nhan) {v} → thanh HUD {base}px → {hh}px"
                          + ("  — khong doi" if hh == base else "  — doi mot lan, CO Y"))
            ctx.close()
    br.close()

print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
