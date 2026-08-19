# -*- coding: utf-8 -*-
"""make_logo_dark.py — bản wordmark TỐI cho tờ chứng nhận in trên giấy trắng.

⚠️ SINH RA TỪ CHÍNH ẢNH GỐC CỦA CHỦ DỰ ÁN, không vẽ mới. `img/astroq-logo.png` là
   wordmark SÁNG (đo được: 192/255) vì nó thiết kế cho nền tối của app; đặt lên giấy
   trắng thì thành một vệt xám mờ (đã đo ở bản dựng chứng nhận đầu 19/08/2026).

CÁCH ĐỔI — chỉ đổi phần CHỮ, giữ nguyên phần CÓ MÀU:
  Đo được wordmark gồm hai loại điểm: chữ "astro" gần trắng/xám (độ bão hoà < 40) và
  điểm nhấn của chữ Q màu tím (96,64,224) + cyan (0,160,224). Đổi cả ảnh sang navy là
  mất luôn chữ Q có màu — thứ nhận ra thương hiệu. Nên chỉ ánh xạ nhóm KHÔNG MÀU.

  Độ sáng gốc → navy đậm nhạt theo cùng tỉ lệ, nhờ vậy nét mảnh và viền mờ (anti-alias)
  vẫn mượt thay vì thành răng cưa.

⚠️ `img/AstroQ logo.png` (bản tối 46/255) KHÔNG dùng được: đo ra nó là logo dạng KHỐI
   VUÔNG 940×953 (icon ứng dụng), không phải wordmark ngang.

  python scratchpad/make_logo_dark.py
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image

SRC = "img/astroq-logo.png"
OUT = "img/astroq-logo-dark.png"

# Navy của tờ chứng nhận — cùng token `--cert-ink` trong css/certificate.css.
INK = (13, 19, 48)


def main():
    if not os.path.exists(SRC):
        sys.exit("khong thay %s" % SRC)
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size
    px = im.load()
    doi = giu = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a <= 0:
                continue
            if max(r, g, b) - min(r, g, b) >= 40:      # có màu → giữ
                giu += 1
                continue
            lum = (r + g + b) / 3.0 / 255.0            # 0 = đen, 1 = trắng
            # Càng sáng thì càng đậm navy: chữ trắng thành navy đặc, nét mờ thành nhạt.
            px[x, y] = (int(INK[0] * lum + 0.5),
                        int(INK[1] * lum + 0.5),
                        int(INK[2] * lum + 0.5), a)
            doi += 1
    im.save(OUT, optimize=True)
    sz = os.path.getsize(OUT)
    print("da ghi %s  (%dx%d, %.1f KB)" % (OUT, w, h, sz / 1024.0))
    print("  doi %d diem chu, giu %d diem co mau" % (doi, giu))

    # Đo lại để chắc nó THẬT SỰ tối.
    im2 = Image.open(OUT).convert("RGBA")
    p2 = im2.load()
    tot = n = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = p2[x, y]
            if a > 40:
                tot += (r + g + b) / 3
                n += 1
    print("  do sang moi: %.0f/255 (goc 192) — %s"
          % (tot / max(1, n), "dung duoc tren giay trang"
             if tot / max(1, n) < 120 else "VAN CON SANG, xem lai"))


if __name__ == "__main__":
    main()
