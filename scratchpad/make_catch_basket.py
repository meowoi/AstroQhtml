# -*- coding: utf-8 -*-
"""Sinh asset DE HUNG SAO cua Bat Sao Bang tu anh goc chu du an dat vao.

    Vao : img/catch-basket.png        (anh goc, DA XOA NEN, khong commit)
    Ra  : img/catch-basket-<W>.png    (ban dung that, commit)

⚠️⚠️ NO KHONG CHI THU NHO ANH — no DO ra hai con so ma luat choi phu thuoc:
   `trayTop` / `trayBot` = mep TREN va mep DUOI cua MAT KHAY, tinh theo ti le
   chieu cao anh. Vung hung cua game la MAT TREN cua de (ghi ngay o CONFIG:
   "gio hung: RONG va DET — vung hung la mat tren"), ma tam bien pha le co
   CANH XOE CAO HON mat khay. Lay mep tren cua CA ANH lam mep hitbox thi sao roi
   trung vao canh cung duoc tinh la hung, du mat thay no con lo lung phia tren.
   Do la dung lop loi hitbox da tra gia o ARCADE-01 (46x34 -> 50x30) va o
   `rock-gray.png` ("CO VE PHAI DO TU CHINH FILE ANH, dung doan").

⚠️ Cach do mep khay: voi TUNG hang pixel, dem do phu alpha trong 50% GIUA be rong.
   Canh pha le nam o HAI DAU nen chung khong lam nhieu vung giua; mat khay thi
   trai gan het be rong o giua. Nguong 0.80 => hang do la mat khay.

⚠️ NEN BANG `quantize(FASTOCTREE)`, KHONG `convert("P", ADAPTIVE)` \u2014 nhanh sau
   lam phang alpha thanh trong-suot-nhi-phan, tuc chat het vien mem va quang sang
   (bai hoc 26/07/2026, va lap lai o make_racer_assets.py).

⚠️ ANH GOC PHAI VAO .gitignore neu > ~300KB: repo nay deploy CONG KHAI qua Pages.
"""
import io, os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "img", "catch-basket.png")

# Co ve lon nhat: shipW=96 don vi ao, san rong toi da 1120px tren he ao 800
#   => 96 * (1120/800) = 134px that; nhan DPR 2 = 269px. Lay 288 cho tron, ~2x.
OUT_W = 288

if not os.path.exists(SRC):
    sys.exit("DUNG: chua co %s\n"
             "   Chu du an luu ban goc (DA XOA NEN) vao dung duong dan do roi chay lai." % SRC)

im = Image.open(SRC).convert("RGBA")
print("anh goc          : %dx%d  (%.0f KB)" % (im.width, im.height, os.path.getsize(SRC)/1024))

a = im.split()[3]
bbox = a.getbbox()
if not bbox: sys.exit("DUNG: anh trong suot hoan toan — co dung la ban DA XOA NEN khong?")
im = im.crop(bbox)
print("sau khi cat vien  : %dx%d  (bo %.0f%% khung trong suot)"
      % (im.width, im.height, 100 - 100.0*im.width*im.height/((bbox[2]-bbox[0]+1)*(bbox[3]-bbox[1]+1)) if False else
         100 - 100.0*(im.width*im.height)/(Image.open(SRC).width*Image.open(SRC).height)))

# ---- do mep mat khay -------------------------------------------------------
px = im.load()
W, H = im.size
x0, x1 = int(W*0.25), int(W*0.75)          # 50% GIUA, tranh canh pha le hai dau
rows = []
for y in range(H):
    n = sum(1 for x in range(x0, x1) if px[x, y][3] > 40)
    rows.append(n / float(x1 - x0))
solid = [y for y, f in enumerate(rows) if f >= 0.80]
if not solid: sys.exit("DUNG: khong tim thay hang nao phu >=80%% o vung giua — do lai bang tay.")
tray_top, tray_bot = solid[0], solid[-1]
print("mat khay (50%% giua): hang %d -> %d  = %.4f -> %.4f theo chieu cao anh"
      % (tray_top, tray_bot, tray_top/float(H), tray_bot/float(H)))
print("canh pha le xoe cao hon mat khay: %d px (%.1f%% chieu cao)"
      % (tray_top, 100.0*tray_top/H))
print("ti le CA ANH      : %.3f : 1" % (W/float(H)))
print("ti le MAT KHAY    : %.3f : 1" % (W/float(max(1, tray_bot-tray_top))))

# ---- xuat ------------------------------------------------------------------
out_h = max(1, int(round(OUT_W * H / float(W))))
small = im.resize((OUT_W, out_h), Image.LANCZOS)
q = small.quantize(method=Image.FASTOCTREE, colors=256)
dst = os.path.join(ROOT, "img", "catch-basket-%d.png" % OUT_W)
q.save(dst, optimize=True)
lv = len(set(small.split()[3].getdata()))
print("\nxuat             : %s  %dx%d  %.1f KB" % (os.path.basename(dst), OUT_W, out_h,
                                                   os.path.getsize(dst)/1024.0))
print("muc alpha giu lai : %d  (>2 = vien mem con nguyen)" % lv)
if lv <= 2: sys.exit("DUNG: alpha bi lam phang — nen sai nhanh.")

print("\n--- DAN VAO game-catch.html CONFIG ---")
print("    basketSprite: 'img/catch-basket-%d.png'," % OUT_W)
print("    basketAR:     %.4f,   // rong/cao cua CA ANH" % (W/float(H)))
print("    trayTop:      %.4f,   // mep tren MAT KHAY, theo chieu cao anh" % (tray_top/float(H)))
print("    trayBot:      %.4f,   // mep duoi MAT KHAY" % (tray_bot/float(H)))
