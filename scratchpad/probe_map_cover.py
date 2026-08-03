# -*- coding: utf-8 -*-
"""
PROBE A — bản đồ phẳng có phủ kín khung không?

Sinh ra từ ảnh chụp chủ dự án gửi 02/08/2026: bước ⑤ `rotation`, bản đồ chỉ phủ
tới x≈1243 trên khung ~1900px, bên phải đen thuần.

⚠️ KHÔNG kết luận từ đọc code. Probe này đo `getBoundingClientRect()` THẬT của
`.e2-img` (đã tính transform) so với `.e2-view`, ở nhiều tỉ lệ màn × nhiều
`facing.lon` × nhiều mức zoom.

Giả thuyết đang kiểm (từ css/mission-earth.css:550 + js/earth2d.js:213):
  .e2.e2-flat .e2-layer{width:max(100vw,200vh);height:max(50vw,100vh);}
  → lớp được cỡ để phủ khung KHI translate = 0.
  paint(): px = -wrapLon(facing.lon)/360*100   → dịch tới ±50% BỀ RỘNG CHÍNH NÓ.
  → mọi lon != 0 đều đẩy lớp ra khỏi khung; zoom > 1 che bớt, zoom = 1 thì hở.

Chạy:  python -m http.server 8123   (trong AstroQhtml/)
       PYTHONIOENCODING=utf-8 python scratchpad/probe_map_cover.py

Nhãn print KHONG DAU — console Windows mặc định cp1252, in chữ có dấu là
UnicodeEncodeError ném giữa lúc chạy và bỏ dở mọi phép đo phía sau.
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
PASS = 0
FAIL = 0
ROWS = []


def check(label, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("   [OK]   " + label + ("  " + detail if detail else ""))
    else:
        FAIL += 1
        print("   [HONG] " + label + ("  " + detail if detail else ""))


# (nhan, w, h) — gom ca khung rong-ma-thap giong anh chu du an gui
VIEWPORTS = [
    ("anh-chu-du-an ~1900x985", 1900, 985),
    ("laptop 1440x900",         1440, 900),
    ("FullHD 1920x1080",        1920, 1080),
    ("MacBook14 1512x982",      1512, 982),
    ("ultrawide 2560x1080",     2560, 1080),
    ("iPad ngang 1180x820",     1180, 820),
    ("dien thoai 390x844",       390, 844),
]

# facing.lon dung that trong nhiem vu: 20 (dau buoc rotation) · 95 (FACE_OPEN)
# · 108 (tram phat song) · 0 · -95 (mac dinh cu)
LONS = [0, 20, 95, 108, 180, -95]

# dist -> zoom = clamp(4.4/dist, 0.8, 3): 4.4->1.0 · 2.5->1.76 · 5.2->0.85
DISTS = [4.4, 2.5, 5.2]

# 8 BUOC THAT — (nhan, lat, lon, dist) boc tu mission-earth.html.
# FACE_OPEN = (30, 95). Buoc nao khong khai lai lat/lon thi THUA HUONG buoc truoc,
# nen o day ghi dung gia tri thua huong that.
STEP_ROWS = []
REAL_STEPS = [
    ("1 scan     :871",  30,  95, 2.6),   # {...FACE_OPEN, dist:2.6}
    ("2 timeline :951",  30,  95, 3.4),   # dist only  -> thua huong (30,95)
    ("3 sun     :1012",  30,  95, 5.2),   # {...FACE_OPEN, dist:5.2}
    ("4 energy  :1066",  30,  95, 3.8),   # thua huong
    ("5 rotation:1136",  10,  20, 4.4),   # panTo(lat:10,lon:20) roi dist:4.4
    ("5 rot+keo :1136",  10, 108, 4.4),   # sau khi tre keo tram vao vong ngam
    ("6 life    :1193",  10,  20, 3.1),   # thua huong
    ("7 eco     :1244",  10,  20, 4.0),   # thua huong
    ("8 core    :1284",  10,  20, 3.6),   # thua huong
]

MEASURE = """
() => {
  const view = document.querySelector('.e2-view');
  const layer= document.querySelector('.e2-layer');
  // ⚠️ PHAI LAY HOP CUA MOI BAN ANH, khong phai querySelector('.e2-img') don le.
  //    Tu 02/08/2026 ban do phang co BA ban lat theo kinh tuyen; do mot ban thi
  //    bao "van ho 602px" trong khi hai ban sao da lap kin — probe nay da bao
  //    hong oan dung mot luot vi the.
  const imgs = [...document.querySelectorAll('.e2-img')]
                 .filter(e => e.offsetParent !== null || e.getClientRects().length);
  if (!view || !layer || !imgs.length) return null;
  const v = view.getBoundingClientRect();
  const rs = imgs.map(e => e.getBoundingClientRect());
  const i = {
    left:   Math.min(...rs.map(r => r.left)),
    right:  Math.max(...rs.map(r => r.right)),
    top:    Math.min(...rs.map(r => r.top)),
    bottom: Math.max(...rs.map(r => r.bottom)),
  };
  i.width = i.right - i.left; i.height = i.bottom - i.top;
  const l = layer.getBoundingClientRect();
  // ⚠️ ĐỌC `facing` THẬT, khong tin con so vua truyen vao panTo: tween mo man cua
  //    trang co the con dang chay va ghi de. Lan chay dau probe nay bao so KHONG
  //    DON DIEU (lon=95 ho 535px nhung lon=108 ho 0) — dau hieu dung cua cuoc dua do.
  const f = window.__mission.world.facingLatLon();
  return {
    facingLat: f.lat, facingLon: f.lon,
    view:  {x: v.left, y: v.top, w: v.width, h: v.height},
    img:   {x: i.left, y: i.top, w: i.width, h: i.height},
    layer: {x: l.left, y: l.top, w: l.width, h: l.height},
    // ho ra bao nhieu px o tung phia (so 0 = phu kin)
    gapL: Math.max(0, i.left - v.left),
    gapR: Math.max(0, v.right - i.right),
    gapT: Math.max(0, i.top - v.top),
    gapB: Math.max(0, v.bottom - i.bottom),
    transform: getComputedStyle(layer).transform,
    flat: document.getElementById('stage').classList.contains('e2-flat'),
  };
}
"""


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        for vname, vw, vh in VIEWPORTS:
            ctx = br.new_context(viewport={"width": vw, "height": vh})
            # Ghim tieng Viet — AstroQ.getLang() lui ve navigator.language, ma
            # Chromium cua Playwright mac dinh en-US.
            ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(BASE + "/mission-earth.html", wait_until="domcontentloaded")
            pg.wait_for_function("() => window.__mission && window.__mission.world", timeout=20000)
            # ⚠️ CHO TWEEN MO MAN DUNG YEN. Buoc ① goi panTo voi ms mac dinh; do
            #    ngay la do giua luc no dang bay, va moi con so sau do vo nghia.
            pg.wait_for_function(
                """() => {
                     const f = window.__mission.world.facingLatLon();
                     const k = f.lat.toFixed(2) + ',' + f.lon.toFixed(2);
                     if (window.__probeLast === k) { return (window.__probeN = (window.__probeN|0) + 1) > 6; }
                     window.__probeLast = k; window.__probeN = 0; return false;
                   }""", timeout=20000)

            print("\n== " + vname + " ==")
            base = pg.evaluate(MEASURE)
            if base is None:
                check(vname + ": tim thay .e2-view/.e2-img", False, "khong co phan tu")
                ctx.close()
                continue
            check("che do ban do phang (.e2-flat)", base["flat"] is True)
            print("      view %dx%d | layer %.0fx%.0f | img %.0fx%.0f"
                  % (base["view"]["w"], base["view"]["h"],
                     base["layer"]["w"], base["layer"]["h"],
                     base["img"]["w"], base["img"]["h"]))

            for dist in DISTS:
                for lon in LONS:
                    pg.evaluate(
                        "([lon,dist]) => window.__mission.world.panTo("
                        "{lat:0, lon:lon, dist:dist, ms:0})", [lon, dist])
                    m = pg.evaluate(MEASURE)
                    # Doi chieu con so THAT voi con so vua truyen vao. Lech nghia la
                    # co tween khac dang chay -> bo qua mau nay chu KHONG ghi vao bang.
                    got = m["facingLon"]
                    drift = abs(((got - lon + 540) % 360) - 180)
                    if drift > 0.5:
                        check("dist=%.1f lon=%4d : mau dung duoc" % (dist, lon),
                              False, "facing.lon that = %.1f (lech %.1f) -> BO MAU"
                              % (got, drift))
                        continue
                    gaps = (m["gapL"], m["gapR"], m["gapT"], m["gapB"])
                    worst = max(gaps)
                    pct = worst / m["view"]["w"] * 100.0
                    ROWS.append((vname, dist, lon, m["gapL"], m["gapR"],
                                 m["gapT"], m["gapB"], pct))
                    check("dist=%.1f lon=%4d : phu kin khung" % (dist, lon),
                          worst < 1.0,
                          "ho L%.0f R%.0f T%.0f B%.0f px (%.1f%% be rong)"
                          % (m["gapL"], m["gapR"], m["gapT"], m["gapB"], pct))

            # ============ 8 BUOC THAT ============
            # (lon, dist) boc tu chinh mission-earth.html. FACE_OPEN = (30, 95).
            # lon THUA HUONG khi buoc khong khai lai -> ghi dung gia tri thua huong.
            print("      --- 8 buoc that ---")
            for sname, slat, slon, sdist in REAL_STEPS:
                pg.evaluate(
                    "([la,lo,d]) => window.__mission.world.panTo("
                    "{lat:la, lon:lo, dist:d, ms:0})", [slat, slon, sdist])
                m = pg.evaluate(MEASURE)
                worst = max(m["gapL"], m["gapR"], m["gapT"], m["gapB"])
                pct = worst / m["view"]["w"] * 100.0
                STEP_ROWS.append((vname, sname, pct, m["gapL"], m["gapR"],
                                  m["gapT"], m["gapB"]))
                check("%-22s (lon=%3d dist=%.1f) phu kin" % (sname, slon, sdist),
                      worst < 1.0,
                      "ho L%.0f R%.0f T%.0f B%.0f px (%.1f%%)"
                      % (m["gapL"], m["gapR"], m["gapT"], m["gapB"], pct))

            check(vname + ": 0 loi console/pageerror", len(errs) == 0,
                  "; ".join(errs[:2]))
            ctx.close()
        br.close()

    print("\n" + "=" * 74)
    print("BANG TONG HOP — cac cau hinh HO ra nhieu nhat")
    print("=" * 74)
    bad = sorted([r for r in ROWS if r[7] >= 1.0], key=lambda r: -r[7])
    if not bad:
        print("  khong co cau hinh nao ho.")
    for r in bad[:20]:
        print("  %-24s dist=%.1f lon=%4d  ho toi da %5.1f%%  (L%.0f R%.0f T%.0f B%.0f)"
              % (r[0], r[1], r[2], r[7], r[3], r[4], r[5], r[6]))
    print("\n" + "=" * 74)
    print("8 BUOC THAT — buoc nao ho ra vung den (day moi la con so quyet dinh)")
    print("=" * 74)
    for vn in dict.fromkeys([r[0] for r in STEP_ROWS]):
        rs = [r for r in STEP_ROWS if r[0] == vn]
        nbad = len([r for r in rs if r[2] >= 1.0])
        print("  %-24s %d/%d buoc ho" % (vn, nbad, len(rs)))
        for r in sorted(rs, key=lambda r: -r[2]):
            if r[2] >= 1.0:
                print("      %-20s %5.1f%%  L%.0f R%.0f T%.0f B%.0f"
                      % (r[1], r[2], r[3], r[4], r[5], r[6]))
    print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
