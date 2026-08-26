# -*- coding: utf-8 -*-
r"""make_landing_assets.py — sinh ban AVIF + WebP DA HA CO cho 9 anh trang tri cua
`landing-app.html`. Chay lai bat cu luc nao; no ghi de va tu in ra so byte.

    python scratchpad/make_landing_assets.py

⚠️⚠️ BE RONG LAY TU CSS, KHONG DOAN. `css/landing-app.css` chan be rong tung anh bang
   `clamp(min, ..vw, MAX)`; con so duoi day la MAX × 2 (cho man retina dpr 2). Do
   duoc 25/08/2026: anh goc dang lon gap ~4 lan o hien thi (vd `raica1.png` 960×479
   cho mot o 242×125), va ca trang tai **525,2 KB PNG**.
   ⚠️ Doi `clamp(...)` trong CSS thi PHAI chay lai bo nay. `scratchpad/check_pages.py`
      muc [39] doi chieu hai con so de quen la thay.

⚠️ GIU NGUYEN PNG GOC lam duong lui trong `<picture>`: trinh duyet khong doc duoc
   AVIF thi con WebP, khong doc duoc WebP thi con PNG. Va PNG goc con dung o cho
   khac (`index.html` dung `m1.png`/`b1.png`), nen KHONG duoc xoa.

⚠️ KHONG ep AVIF phai nho hon WebP o TUNG anh. Voi anh nho, phan dau (header) cua
   AVIF co the lan hon ca phan tiet kiem; bo nay in ca hai con so va NOI RA anh nao
   nguoc, de nguoi doc quyet chu khong de bo sinh tu quyet.
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

# ten anh -> be rong dich (= MAX trong `clamp()` cua css/landing-app.css × 2)
WANT = {
    "raica1": 480,   # .f-raica1  clamp(158px, 17vw, 240px)
    "b1":     336,   # .f-b1      clamp(112px, 12vw, 168px)
    "luna1":  248,   # .floaty    clamp(82px,  9vw, 124px)
    "cho1":   248,
    "m1":     248,
    "qg1":    248,   # .ic-qg1    clamp(82px,  9vw, 124px)
    "qb1":    248,
    "q1":     248,
    "3qok":   384,   # .ic-3qok   clamp(120px, 14vw, 192px)
}

AVIF_Q = 62      # do o cuoi file: 62 la muc chua thay khac biet o co nay
WEBP_Q = 82


def kb(n):
    return "%.1f KB" % (n / 1024.0)


def main():
    rows = []
    tot_png = tot_avif = tot_webp = 0
    for name, w in sorted(WANT.items()):
        src = "img/%s.png" % name
        if not os.path.exists(src):
            print("  [HONG] khong thay %s" % src)
            return 1
        im = Image.open(src).convert("RGBA")
        ow, oh = im.size
        h = max(1, round(oh * w / float(ow)))
        # ⚠️ LANCZOS cho phep ha co: nhan vat co vien manh, BILINEAR lam nhoe vien.
        small = im.resize((w, h), Image.LANCZOS)

        a_path = "img/%s-%d.avif" % (name, w)
        w_path = "img/%s-%d.webp" % (name, w)
        small.save(a_path, quality=AVIF_Q)
        small.save(w_path, quality=WEBP_Q, method=6)

        p_sz = os.path.getsize(src)
        a_sz = os.path.getsize(a_path)
        w_sz = os.path.getsize(w_path)
        tot_png += p_sz
        tot_avif += a_sz
        tot_webp += w_sz
        rows.append((name, ow, oh, w, h, p_sz, a_sz, w_sz))

    print("=== Da sinh %d cap AVIF + WebP ===" % len(rows))
    print("  %-8s %-13s %-12s %10s %10s %10s" %
          ("ten", "goc", "moi", "PNG", "AVIF", "WebP"))
    for name, ow, oh, w, h, p, a, wb in rows:
        flag = ""
        if a >= wb:
            flag = "  <- AVIF KHONG nho hon WebP"
        print("  %-8s %-13s %-12s %10s %10s %10s%s"
              % (name, "%dx%d" % (ow, oh), "%dx%d" % (w, h),
                 kb(p), kb(a), kb(wb), flag))
    print("  %-8s %-13s %-12s %10s %10s %10s"
          % ("TONG", "", "", kb(tot_png), kb(tot_avif), kb(tot_webp)))
    print("\n  AVIF tiet kiem %s (%.0f%%) so voi PNG"
          % (kb(tot_png - tot_avif), 100.0 * (tot_png - tot_avif) / tot_png))
    print("  WebP tiet kiem %s (%.0f%%)"
          % (kb(tot_png - tot_webp), 100.0 * (tot_png - tot_webp) / tot_png))
    return 0


if __name__ == "__main__":
    sys.exit(main())
