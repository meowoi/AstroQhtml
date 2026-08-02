# -*- coding: utf-8 -*-
"""
probe_earth_flat.py — do do sang + do tuong phan dat/nuoc cua ban do phang.

    cd AstroQhtml
    set PYTHONIOENCODING=utf-8 & python scratchpad/probe_earth_flat.py

VI SAO CAN BO DO NAY (docs/decisions/004):
  Quyet dinh 004 bo anh qua cau, dung ban do phang cho ca 8 buoc. Do duoc o luot
  01/08: qua cau sang trung binh 113,9 o vung giua, ban do phang chi 24,3 — toi hon
  4,7 lan. Bo qua cau ma khong nang sang ban do la canh MO MAN cua nhiem vu thanh
  mot hinh chu nhat gan den.

  Nhung nang sang qua tay thi dat va bien nhoe vao nhau — ma buoc `life` doi tre
  nhan ra Amazon / Himalaya / Nam Cuc TREN CHINH buc anh do. Nen phai do HAI con so,
  khong chi mot:
      (1) do sang trung binh  -> phai TANG
      (2) tuong phan dat<->nuoc -> KHONG duoc giam

⚠️ Nguon toi (khong phai loi nen): anh goc la `world.topo.bathy` — ban "topo +
   bathymetry", tuc dai duong duoc ve ca dia hinh day bien nen no VON dam mau. Do la
   ly do ban do phang toi hon anh qua cau, khong phai vi nen JPEG.

⚠️ Diem mau lay o TRONG LONG luc dia / giua dai duong, khong lay sat bo bien: mot
   diem sat bo lech vai pixel la doi han phan loai, va con so tuong phan mat nghia.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
EARTH = os.path.join(ROOT, "img", "earth")

try:
    from PIL import Image
except ImportError:
    print("Thieu Pillow: pip install Pillow")
    sys.exit(1)

# (ten, lat, lon) — trong long luc dia
LAND = [
    ("Sahara",        23,   13),
    ("Amazon",        -4,  -62),
    ("Tibet",         32,   88),
    ("Siberia",       62,  100),
    ("Australia",    -25,  133),
    ("Congo",          0,   22),
    ("US-Midwest",    41,  -98),
]
# (ten, lat, lon) — giua dai duong, xa bo
OCEAN = [
    ("Pacific-TT",     0, -140),
    ("Atlantic-B",    35,  -45),
    ("Indian",       -20,   75),
    ("Pacific-N",    -40, -120),
    ("Atlantic-XD",   12,  -42),   # dung diem cua the mau vat `water`
]
PATCH = 4          # nua canh o mau -> o (2*4+1)^2 = 81 px


def lum(px):
    r, g, b = px[0], px[1], px[2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def sample(im, lat, lon):
    """lat/lon -> pixel tren anh equirectangular, roi lay trung binh o 9x9."""
    w, h = im.size
    x = int((lon + 180) / 360.0 * w)
    y = int((90 - lat) / 180.0 * h)
    vals = []
    for dy in range(-PATCH, PATCH + 1):
        for dx in range(-PATCH, PATCH + 1):
            xx = min(max(x + dx, 0), w - 1)
            yy = min(max(y + dy, 0), h - 1)
            vals.append(lum(im.getpixel((xx, yy))))
    return sum(vals) / len(vals)


def mean_all(im, step=7):
    """Do sang trung binh toan anh, lay mau thua cho nhanh."""
    w, h = im.size
    vals = []
    for y in range(0, h, step):
        for x in range(0, w, step):
            vals.append(lum(im.getpixel((x, y))))
    return sum(vals) / len(vals)


def report(name, im, verbose=True):
    avg = mean_all(im)
    ls = [(n, sample(im, la, lo)) for n, la, lo in LAND]
    os_ = [(n, sample(im, la, lo)) for n, la, lo in OCEAN]
    lm = sum(v for _, v in ls) / len(ls)
    om = sum(v for _, v in os_) / len(os_)
    print(f"\n--- {name}  ({im.size[0]}x{im.size[1]}) ---")
    print(f"  do sang TB toan anh : {avg:6.1f}")
    print(f"  dat  TB             : {lm:6.1f}")
    print(f"  nuoc TB             : {om:6.1f}")
    print(f"  TUONG PHAN dat-nuoc : {lm - om:6.1f}")
    if verbose:
        print("     dat :", "  ".join(f"{n}={v:.0f}" for n, v in ls))
        print("     nuoc:", "  ".join(f"{n}={v:.0f}" for n, v in os_))
    return dict(avg=avg, land=lm, ocean=om, contrast=lm - om)


def main():
    src = os.path.join(EARTH, "_src", "flat.jpg")
    cur = os.path.join(EARTH, "flat-2048.webp")
    globe = os.path.join(EARTH, "_src", "globe.jpg")

    print("=" * 62)
    print("BASELINE — truoc khi nang sang")
    print("=" * 62)

    if not os.path.exists(src):
        print(f"KHONG THAY {src} — chay scratchpad/make_earth_assets.py truoc.")
        sys.exit(1)

    base = report("_src/flat.jpg (goc NASA 5400x2700)",
                  Image.open(src).convert("RGB"))
    asset = report("flat-2048.webp (asset dang dung)",
                   Image.open(cur).convert("RGB"))

    # Anh qua cau: KHONG do bang lat/lon (no la anh CHUP qua cau, khong phai
    # equirectangular) — chi do do sang vung giua de co moc so sanh.
    if os.path.exists(globe):
        g = Image.open(globe).convert("RGB")
        w, h = g.size
        mid = g.crop((int(w * .3), int(h * .3), int(w * .7), int(h * .7)))
        print(f"\n--- _src/globe.jpg — CHI de doi chieu moc ---")
        print(f"  do sang TB vung giua: {mean_all(mid, 3):6.1f}")
        print("  (khong do dat/nuoc: anh chup qua cau, lat/lon KHONG quy ra"
              " phan tram duoc)")

    print("\n" + "=" * 62)
    print("MOC CAN DAT sau khi nang sang (theo 004)")
    print("=" * 62)
    print(f"  do sang TB   : > {asset['avg']:.1f}  (hien tai), nham >= 70")
    print(f"  tuong phan   : >= {asset['contrast']:.1f}  (KHONG duoc giam)")


if __name__ == "__main__":
    main()
