# -*- coding: utf-8 -*-
"""probe_decal_match.py — O XEM TRUOC o cua hang phai VE Y HET hinh dan tren tau.

Chu du an gui hai anh cat va noi chung khac nhau (22/08/2026). Nguyen nhan la DO
UU TIEN CSS: rule nen `.cos-sw[class*="cos-sw--decal-"]::after` (0,2,1) thang
rule rieng `.cos-sw--decal-comet::after` (0,1,1), nen `transform` rieng cua TUNG
hinh dan bi bo o o xem truoc. Ba trong bon hinh dan co `transform` rieng.

⚠️ PHEP DO PHAI CHUAN HOA THEO `--d`. `--d` la 32px tren tau va 44px o o xem
   truoc, nen so `px` tho voi nhau se bao hong OAN o moi hinh dan. Thu can biet
   la HINH DANG: moi do dai chia cho `--d` phai bang nhau, va phan XOAY cua
   `transform` phai bang nhau (phan dich chuyen thi khong — no theo co).

⚠️ KHONG doc file CSS. Hai rule doc ra deu hop le; chi `getComputedStyle` tren
   trang that moi noi ai thang ai.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/probe_decal_match.py
"""
import math
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shot_decal_cmp import SHOP_STUB, seed          # noqa: E402  (dung chung ban gia)

from playwright.sync_api import sync_playwright     # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"
CSS = (ROOT / "css" / "cockpit.css").read_text(encoding="utf-8")

dat = 0
hong = 0


def chk(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   " + name + (("  (" + str(info) + ")") if info else ""))
    else:
        hong += 1
        print("  [HONG] " + name + (("  -> " + str(info)) if info else ""))


# Danh sach hinh dan doc TU CSS, khong go cung: them hinh moi la bo do tu phu.
DECALS = sorted(set(re.findall(r"cos-sw--decal-([a-z0-9-]+)\b", CSS)))

READ = """(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const cs = getComputedStyle(el);
  const d  = parseFloat(cs.getPropertyValue('--d')) || 0;
  const one = (ps) => {
    const s = getComputedStyle(el, ps);
    return { w:s.width, h:s.height, ml:s.marginLeft, mt:s.marginTop,
             tf:s.transform, sh:s.boxShadow, fi:s.filter,
             bw:s.borderTopWidth, br:s.borderTopLeftRadius, cp:s.clipPath,
             bg:s.backgroundImage };
  };
  return { d:d, tf:cs.transform, disp:cs.display,
           before:one('::before'), after:one('::after') };
}"""


def nums(txt):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", txt or "")]


def rot_of(tf):
    """Goc xoay (do) trich tu `matrix(a,b,c,d,e,f)`. Bo phan dich chuyen."""
    if not tf or tf == "none":
        return 0.0
    v = nums(tf)
    if len(v) < 4:
        return 0.0
    return round(math.degrees(math.atan2(v[1], v[0])), 2)


NO_COLOR = re.compile(r"(rgba?|hsla?)\([^)]*\)")


def lens(txt):
    """Chi lay phan DO DAI cua mot chuoi CSS.

    ⚠️ PHAI BOC MAU RA TRUOC. `box-shadow: rgba(56,189,248,.95) 0 0 7.68px -.96px`
       co bon con so cua MAU; chia chung cho `--d` thi 56/32 khong bao gio bang
       56/44 va phep kiem bao hong oan o moi hinh dan.
    """
    return nums(NO_COLOR.sub(" ", txt or ""))


REF = 44.0     # quy cả hai bên về cùng một cỡ rồi mới so


def same_len(a, da, b, db, tol=0.2):
    """Hai chuoi do dai co cung HINH DANG khong (sau khi quy ve cung co)?

    ⚠️ Phan tram thi so THO: chia mot phan tram cho `--d` la vo nghia.
    ⚠️ Dung sai MAC DINH RAT CHAT (0,2px). Chi `border-width` duoc noi len 1px, va
       chi vi trinh duyet LAM TRON be rong vien ve pixel thiet bi (1,5px thanh 1px
       o co 32 nhung 1,98px thanh 2px o co 44) — do la lam tron cua trinh duyet,
       khong phai lech cua CSS. Noi dung sai cho MOI truong thi mot do dai `px`
       tuyet doi (thu ma khoi nay cam) se LOT: phep thu pha hoai da chung minh
       dung dieu do.
    """
    a = a or ""
    b = b or ""
    if "%" in a or "%" in b:
        return a == b, "%r vs %r" % (a, b)
    va, vb = lens(a), lens(b)
    if len(va) != len(vb):
        return False, "%r vs %r" % (a, b)
    if da <= 0 or db <= 0:
        return False, "khong doc duoc --d"
    worst = 0.0
    for x, y in zip(va, vb):
        worst = max(worst, abs(x / da * REF - y / db * REF))
    return worst <= tol, "lech toi da %.2fpx (quy ve co %gpx)" % (worst, REF)


def main():
    print("doc duoc %d hinh dan tu css/cockpit.css: %s"
          % (len(DECALS), " · ".join(DECALS)))
    with sync_playwright() as p:
        br = p.chromium.launch()

        # ── (1) tren tau: doc tung hinh dan bang cach doi `data-decal` ──
        ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh",
                            viewport={"width": 1440, "height": 900})
        seed(ctx)
        ctx.route("**/me/**", lambda r: r.fulfill(status=200, body="{}"))
        pg = ctx.new_page()
        perr = []
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.goto(BASE + "/dashboard.html", wait_until="load")
        pg.wait_for_timeout(1000)
        ship = {}
        for k in DECALS:
            pg.evaluate("(v) => document.documentElement.setAttribute('data-decal', v)",
                        "decal-" + k)
            pg.wait_for_timeout(60)
            ship[k] = pg.evaluate(READ, ".decal")
        chk("doc duoc hinh dan tren tau", all(ship[k] for k in DECALS))
        chk("0 loi trang (dashboard)", not perr, "; ".join(perr[:2]))
        ctx.close()

        # ── (2) o xem truoc o cua hang ──
        ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh",
                            viewport={"width": 1440, "height": 900})
        seed(ctx)
        ctx.add_init_script(SHOP_STUB)
        ctx.route("**/billing/catalog", lambda r: r.fulfill(
            status=200, content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body='{"ok":true,"saleOpen":false,"provider":"none"}'))
        pg = ctx.new_page()
        perr2 = []
        pg.on("pageerror", lambda e: perr2.append(str(e)))
        pg.goto(BASE + "/shop.html", wait_until="load")
        pg.wait_for_timeout(1200)
        # ⚠ Ban gia chi khai 2 hinh dan; de do DU 4 hinh thi gan them o gia vao
        #   DUNG cay DOM cua cua hang (khong dung mot the roi: `.cos-sw` la
        #   `<span>`, dat ngoai luoi thi `display:inline` va width/height bi bo).
        pg.evaluate("""(keys) => {
          const host = document.querySelector('#kinds') || document.body;
          const box = document.createElement('div');
          box.id = '__probe';
          box.style.cssText = 'display:grid;grid-template-columns:repeat(4,120px);gap:8px';
          box.innerHTML = keys.map(k =>
            '<span class="cos-sw cos-sw--decal-' + k + '" style="display:block"></span>'
          ).join('');
          host.appendChild(box);
        }""", DECALS)
        pg.wait_for_timeout(200)
        shop = {}
        for k in DECALS:
            shop[k] = pg.evaluate(READ, "#__probe .cos-sw--decal-" + k)
        chk("doc duoc o xem truoc", all(shop[k] for k in DECALS))
        chk("0 loi trang (shop)", not perr2, "; ".join(perr2[:2]))
        ctx.close()
        br.close()

    # ── So sanh: chuan hoa theo `--d` ──
    print("\n=== HAI CHO PHAI VE CUNG MOT HINH ===")
    FIELDS = ("w", "h", "ml", "mt", "bw", "br", "sh", "fi")
    for k in DECALS:
        a, b = ship.get(k), shop.get(k)
        if not a or not b:
            chk("%s: doc duoc ca hai ben" % k, False)
            continue
        chk("%s: goc dat ca sticker giong nhau" % k,
            rot_of(a["tf"]) == rot_of(b["tf"]),
            "tau %s° vs shop %s°" % (rot_of(a["tf"]), rot_of(b["tf"])))
        if k == "none":
            # ⚠ "Chua dan gi" CO Y khac nhau: tren tau thi `.decal` bi
            #   `display:none` (khong dan gi thi khong hien mot hop rong), con o
            #   cua hang thi phai NOI RA la trong — o net dut. So kich co o day
            #   la so `auto` voi `0px`, tuc do mot thu khong ton tai.
            chk("none: tren tau thi KHONG hien (khong ve mot hop rong)",
                a["before"]["w"] == "auto" or a["disp"] == "none",
                "w=%r disp=%r" % (a["before"]["w"], a.get("disp")))
            continue
        for ps in ("before", "after"):
            pa, pb = a[ps], b[ps]
            bad = []
            for f in FIELDS:
                # `border-width`: noi dung sai 1px cho phan lam tron cua trinh duyet.
                ok, why = same_len(pa[f], a["d"], pb[f], b["d"],
                                   tol=(1.05 if f == "bw" else 0.2))
                if not ok:
                    bad.append("%s: %s" % (f, why))
            chk("%s ::%s: moi do dai khop nhau (quy ve cung co)" % (k, ps),
                not bad, " | ".join(bad[:3]))
            chk("%s ::%s: goc xoay khop nhau" % (k, ps),
                rot_of(pa["tf"]) == rot_of(pb["tf"]),
                "tau %s° vs shop %s°" % (rot_of(pa["tf"]), rot_of(pb["tf"])))
            chk("%s ::%s: cung mot hinh (clip-path) va cung mot nen" % (k, ps),
                pa["cp"] == pb["cp"] and pa["bg"] == pb["bg"],
                "clip %r/%r" % (pa["cp"][:24], pb["cp"][:24]))

    print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
    sys.exit(1 if hong else 0)


if __name__ == "__main__":
    main()
