# -*- coding: utf-8 -*-
"""
PROBE B — quả cầu Trái Đất ở explorer.html có ranh giới ngày/đêm ĐỌC ĐƯỢC không?

`005` chốt dạy ngày/đêm trên quả cầu 3D. Mã cho thấy cơ chế ĐÚNG:
  · MeshStandardMaterial (explorer.html:1138) -> an sang that
  · PointLight(0xfff0d0, 3.4, 0, 0.12) gan VAO chinh this.sun (:1322)
Nhung cung co nhieu anh sang NEN:
  · AmbientLight(0x8090c0, 0.55)   (:1323)
  · HemisphereLight(0x9fb8ff, 0x101838, 0.35)  (:1324)
=> Gia thuyet phai kiem: nen ~0,9 lam SANG CA NUA TOI, ranh gioi nhat, va cau
   "em thay nua toi chua?" thanh loi hua suong.

Do gi: quet mot dai ngang qua dia hanh tinh, tim bien dia, roi so do sang nua
sang vs nua toi. KHONG doc code roi ket luan.

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       PYTHONIOENCODING=utf-8 python scratchpad/probe_globe_daynight.py

Nhan print KHONG DAU (console Windows cp1252).
"""
import io
import sys
from playwright.sync_api import sync_playwright
from PIL import Image

BASE = "http://127.0.0.1:8123"
PASS = 0
FAIL = 0


def check(label, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("   [OK]   " + label + ("  " + detail if detail else ""))
    else:
        FAIL += 1
        print("   [HONG] " + label + ("  " + detail if detail else ""))


def lum(px):
    return 0.2126 * px[0] + 0.7152 * px[1] + 0.0722 * px[2]


def find_disc(im, box, thr=55.0):
    """
    Tim dia HANH TINH bang cach quet CA VUNG, khong quet mot hang.

    ⚠️ Ban dau probe nay quet DUNG MOT hang ngang qua vi tri nhan ten, ra "dia"
       rong 759px voi moi gia tri 12-54 — tuc no do NEN TROI, khong do hanh tinh.
       Nhan ten nam PHIA TREN hanh tinh, va nguong 12 thi sao nen cung vuot.
       Chi nhin anh chup moi thay. Nen: nguong 55 + tim vung lien thong.

    Tra ve (cx, cy, r, diem[]) — diem la list (x, y, lum) ben trong dia.
    """
    x0, y0, x1, y1 = box
    pts = []
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            L = lum(im.getpixel((x, y)))
            if L >= thr:
                pts.append((x, y, L))
    if len(pts) < 200:
        return None
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    # ban kinh = phan vi 92% khoang cach toi tam (bo duoi cac diem le nhu nhan/mat trang)
    d = sorted(((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5 for p in pts)
    r = d[int(len(d) * 0.92)]
    inside = [p for p in pts
              if ((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5 <= r * 0.93]
    return (cx, cy, r, inside)


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900},
                             device_scale_factor=1)
        ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        print("\n== nap explorer.html (three.js tu unpkg — can mang) ==")
        pg.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
        try:
            pg.wait_for_function("() => window.__solarReady === true", timeout=45000)
        except Exception as e:
            check("canh 3D dung xong (__solarReady)", False,
                  "het han 45s — kiem mang / unpkg.com. " + str(e)[:120])
            print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
            return 1
        check("canh 3D dung xong (__solarReady)", True)

        # ⚠️ #loader co transition .8s va tung NUOT CU BAM (bai hoc 31/07/2026).
        #    Cho no thuc su khong con nhan chuot.
        pg.wait_for_timeout(3200)

        # Chon Trai Dat bang chinh nhan tren ban do — dung duong nguoi dung di.
        lbl = pg.query_selector('#labels [data-body-id="earth"]')
        check("tim thay nhan Trai Dat tren ban do", lbl is not None)
        if lbl is None:
            print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
            return 1
        lbl.click()
        # Camera bay ~1,6s roi bang thong tin moi mo (map-onboard.js ghi vay).
        pg.wait_for_timeout(3000)

        pos = pg.evaluate("""() => {
            const l = document.querySelector('#labels [data-body-id="earth"]');
            const r = l.getBoundingClientRect();
            return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};
        }""")
        print("      nhan Trai Dat o (%d, %d)" % (pos["x"], pos["y"]))

        shot = pg.screenshot()
        im = Image.open(io.BytesIO(shot)).convert("RGB")
        im.save("scratchpad/globe-daynight-1440.png")
        print("      da luu scratchpad/globe-daynight-1440.png")

        # Chi do vung GIUA: bang trai (~x<380) va bang thong tin (~x>1010) khong
        # phai canh 3D. Doc be rong that tu DOM chu khong gan cung.
        bounds = pg.evaluate("""() => {
            const deck = document.getElementById('deck');
            const info = document.getElementById('info');
            const dr = deck ? deck.getBoundingClientRect().right : 0;
            const il = info ? info.getBoundingClientRect().left : window.innerWidth;
            return {left: Math.round(dr) + 12, right: Math.round(il) - 12,
                    h: window.innerHeight};
        }""")
        box = (max(0, bounds["left"]), 60,
               min(im.size[0], bounds["right"]), min(im.size[1], bounds["h"] - 80))
        print("      vung do canh 3D: x %d..%d  y %d..%d"
              % (box[0], box[2], box[1], box[3]))

        disc = find_disc(im, box)
        if disc is None:
            check("tim thay dia hanh tinh tren anh chup", False,
                  "khong du diem sang >= 55 trong vung canh 3D")
            print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
            return 1
        cx, cy, r, inside = disc
        check("tim thay dia hanh tinh tren anh chup", r >= 25,
              "tam (%.0f, %.0f)  ban kinh %.0f px  %d diem do"
              % (cx, cy, r, len(inside)))

        vals = sorted(p[2] for p in inside)
        n = len(vals)
        mean_all = sum(vals) / n
        vmax, vmin = vals[-1], vals[0]
        # Decile: 10% sang nhat vs 10% toi nhat — ben vung hon max/min don le
        d_hi = sum(vals[int(n * 0.9):]) / max(1, n - int(n * 0.9))
        d_lo = sum(vals[:max(1, int(n * 0.1))]) / max(1, int(n * 0.1))
        contrast = d_hi - d_lo
        ratio = (d_hi / d_lo) if d_lo > 0.5 else 999.0

        print("      dia: TB %.1f | max %.1f | min %.1f" % (mean_all, vmax, vmin))
        print("      decile sang nhat %.1f  vs  decile toi nhat %.1f  -> chenh %.1f"
              % (d_hi, d_lo, contrast))

        # 8 khu vuc quanh tam -> lo ra HUONG cua ranh gioi ngay/dem
        import math
        print("      do sang theo 8 huong quanh tam (lo ra huong ranh gioi):")
        for k in range(8):
            a0, a1 = k * math.pi / 4, (k + 1) * math.pi / 4
            seg = [p[2] for p in inside
                   if a0 <= (math.atan2(p[1] - cy, p[0] - cx) % (2 * math.pi)) < a1]
            if seg:
                print("        huong %d (%3d-%3d do): TB %.1f  (%d diem)"
                      % (k + 1, int(math.degrees(a0)), int(math.degrees(a1)),
                         sum(seg) / len(seg), len(seg)))

        # NGUONG: hai nua phai chenh du de MAT tre nhan ra. Lay 25 diem do sang
        # (~10% thang 255) lam moc "nhin thay ro". Duoi 12 diem la khong doc duoc.
        check("hai nua dia chenh >= 25 diem do sang (ranh gioi doc duoc)",
              contrast >= 25.0, "chenh do duoc %.1f" % contrast)
        check("hai nua dia chenh >= 12 diem (toi thieu nhan ra duoc)",
              contrast >= 12.0, "chenh do duoc %.1f" % contrast)
        check("co diem toi thuc su tren dia (min < 40)", vmin < 40.0,
              "min do duoc %.1f — nen sang thi nua toi khong bao gio xuong thap"
              % vmin)
        print("      ti so max/min = %.2f" % ratio)

        check("0 loi console/pageerror", len(errs) == 0, "; ".join(errs[:2]))
        ctx.close()
        br.close()

    print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
