# -*- coding: utf-8 -*-
"""Do CHIEU QUET cua radar ky nang (`RADAR_SKILL_SCAN` o dashboard.html) tren Chromium.

Cau hoi bo do nay tra loi — do TREN TRANG, khong doc code:
  · THANH DAM co DI TRUOC va duoi mo co THEO SAU khong?
  · quat co that su quay THEO CHIEU KIM DONG HO khong (doc DOMMatrix dang chay)?
  · duoi co MO DAN that khong, hay chi la mot mieng quat duc?
  · `prefers-reduced-motion` thi quat co dung yen ma VAN dung hinh hoc?

⚠️ VI SAO CAN: 09/08/2026 chu du an nhin ra loi bang mat — quat quay ma "thanh dam bi
   keo theo sau". Ban cu dat dinh duoi o `polar(...,+0.5,...)` = -54 deg trong khi thanh
   sang o -90 deg; `rotate(0->360deg)` trong SVG la quay theo chieu kim dong ho (truc y
   huong xuong) nen canh DI TRUOC la canh goc LON HON => mep mo dan dau. Doc code thi
   moi dong deu "dung"; chi khi ghep CHIEU QUAY voi DAU cua dinh duoi moi thay sai.

⚠️⚠️ HAI THU DINH NHAU: chieu quay trong `@keyframes radarSweep` va DAU cua dinh duoi
   trong `buildRadar`. Doi mot cai ma khong doi cai kia la loi quay tro lai y nguyen —
   nen bo do nay do CA HAI trong cung mot luot, va `check_pages` muc [18] canh cap do
   bang van ban.

⚠️ BAY DO LUONG: thanh sang la mot `<line>` THANG DUNG luc dung yen o 0 deg => bounding
   box rong 0 => Playwright bao phan tu "hidden" va `wait_for_selector` het han. Phai cho
   `state="attached"`. Day KHONG phai loi san pham.

⚠️ Nhan cua chk() PHAI KHONG DAU (console Windows cp1252). Chay:
     python -m http.server 8123     (trong AstroQhtml/)
     PYTHONIOENCODING=utf-8 python scratchpad/smoke_radar.py
"""
import math
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/dashboard.html"
OK = FAIL = 0

# Gieo de dashboard khong day sang explorer (xem `mapFirst()` + muc 4 CLAUDE.md).
SEED = ("localStorage.setItem('astroq-lang','vi');"
        "localStorage.setItem('astroq-map01-seen','1');"
        "localStorage.setItem('astroq-tour-seen','1');"
        "localStorage.setItem('astroq-user',JSON.stringify("
        "{uid:'u-test',name:'Test',pilotName:'Test',"
        "character:'castor',avatar:'ava/raica1.png'}));")

MATRIX_DEG = """e => {
  const m = new DOMMatrix(getComputedStyle(e).transform);
  return Math.round(Math.atan2(m.b, m.a) * 180 / Math.PI);
}"""


def chk(cond, label, info=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"  [OK]   {label}" + (f"  ({info})" if info else ""))
    else:
        FAIL += 1
        print(f"  [HONG] {label}" + (f"  ({info})" if info else ""))


def bearing(pt, cx=100.0, cy=100.0):
    """Goc theo CHIEU KIM DONG HO tinh tu huong 12h, 0..360 — cung he voi rotate()."""
    return (math.degrees(math.atan2(pt[0] - cx, cy - pt[1])) + 360) % 360


def do_one(br, nhan, motion):
    ctx = br.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion=motion)
    ctx.add_init_script(SEED)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL, wait_until="load")
    # ⚠️ attached, KHONG visible — xem bay do luong o docstring.
    pg.wait_for_selector(".rr-sweep", state="attached", timeout=15000)
    pg.wait_for_timeout(500)

    # Toa do GOC (chua quay), doc thang tu thuoc tinh SVG.
    lead = pg.eval_on_selector(
        ".rr-sweep", "e=>[+e.getAttribute('x2'), +e.getAttribute('y2')]")
    wedge = pg.eval_on_selector(
        ".rr-wedge",
        "e=>e.getAttribute('points').trim().split(/\\s+/)"
        ".map(s=>s.split(',').map(Number))")
    chk(len(wedge) == 3, f"[{nhan}] quat la tam giac", str(wedge))

    tail = [w for w in wedge
            if not (abs(w[0] - 100) < .5 and abs(w[1] - 100) < .5)
            and not (abs(w[0] - lead[0]) < .5 and abs(w[1] - lead[1]) < .5)]
    chk(len(tail) == 1, f"[{nhan}] tach duoc dinh DUOI khoi tam va dinh thanh sang")
    if not tail:
        ctx.close()
        return
    a_lead, a_tail = bearing(lead), bearing(tail[0])

    # PHEP KIEM CHINH: quay theo chieu kim dong ho => canh di truoc co goc LON HON.
    delta = (a_lead - a_tail + 360) % 360
    chk(0 < delta < 180,
        f"[{nhan}] THANH DAM di truoc, duoi mo theo sau (lech {delta:.0f} deg)",
        f"thanh {a_lead:.0f} deg / duoi {a_tail:.0f} deg")
    chk(min(a_lead, 360 - a_lead) < 1,
        f"[{nhan}] thanh dam xuat phat o 12h", f"{a_lead:.0f} deg")

    # CHIEU QUAY THAT — doc matrix dang chay, khong doc keyframes.
    d1 = pg.eval_on_selector(".rr-sweep-g", MATRIX_DEG)
    pg.wait_for_timeout(700)
    d2 = pg.eval_on_selector(".rr-sweep-g", MATRIX_DEG)
    moved = (d2 - d1 + 360) % 360
    if motion == "reduce":
        chk(moved == 0, f"[{nhan}] quat DUNG YEN", f"{d1} -> {d2}")
    else:
        chk(0 < moved < 180, f"[{nhan}] quay THEO chieu kim dong ho",
            f"{d1} -> {d2} deg (+{moved})")

    # Duoi phai MO DAN, khong phai mau phang.
    fill = pg.eval_on_selector(".rr-wedge", "e=>getComputedStyle(e).fill")
    chk("url(" in fill and "rr-tail" in fill, f"[{nhan}] duoi dung gradient", fill)
    stops = pg.eval_on_selector_all(
        "#rr-tail stop", "e=>e.map(s=>+(s.getAttribute('stop-opacity')))")
    chk(len(stops) == 2 and stops[0] < stops[1],
        f"[{nhan}] gradient: dau duoi trong suot -> gan thanh dam nhat", str(stops))
    # ⚠️ Them 09/08/2026 — lo hong tu khai o luot truoc: bo do CHUA do HUONG cua gradient,
    #    nen doi x1/y1/x2/y2 cua #rr-tail sang cho khac thi khong bo nao bat. Truc gradient
    #    PHAI chay tu dinh DUOI -> dinh DAN DAU, khong thi vet mo dam o dau nguoc lai.
    gax = pg.eval_on_selector("#rr-tail", "e=>['x1','y1','x2','y2'].map(k=>+e.getAttribute(k))")
    chk(abs(gax[0] - tail[0][0]) < .6 and abs(gax[1] - tail[0][1]) < .6,
        f"[{nhan}] truc gradient BAT DAU o dinh duoi", f"{gax[:2]} vs {tail[0]}")
    chk(abs(gax[2] - lead[0]) < .6 and abs(gax[3] - lead[1]) < .6,
        f"[{nhan}] truc gradient KET THUC o dinh dan dau", f"{gax[2:]} vs {lead}")

    chk(not errs, f"[{nhan}] 0 pageerror", str(errs[:2]))
    ctx.close()


with sync_playwright() as br_ctx:
    br = br_ctx.chromium.launch()
    print("\n=== Chieu quet cua radar ky nang ===")
    do_one(br, "binh thuong", None)
    do_one(br, "reduced-motion", "reduce")
    br.close()

print(f"\n===== {OK} dat / {FAIL} hong =====")
sys.exit(1 if FAIL else 0)
