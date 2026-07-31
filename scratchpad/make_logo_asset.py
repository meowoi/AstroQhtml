# -*- coding: utf-8 -*-
"""
make_logo_asset.py — sinh `img/astroq-logo.png` từ bản gốc người dùng đặt vào.

    cd AstroQhtml
    set PYTHONIOENCODING=utf-8 & python scratchpad/make_logo_asset.py

NGUỒN: `img/AstroQ logo1.png` (2162×1080, RGBA, 467 KB) — người dùng đặt vào ngày
31/07/2026. Bản gốc **KHÔNG commit** (`.gitignore` chặn), như mọi ảnh gốc khác của
dự án; chỉ asset đã tối ưu mới vào repo.

BA VIỆC SCRIPT LÀM, VÀ VÌ SAO:
  1. **CẮT VIỀN TRONG SUỐT.** Ảnh gốc 2162×1080 nhưng nội dung thật chỉ
     1736×505 — tức **68% khung là khoảng trong suốt**. Không cắt thì logo hiển
     thị nhỏ hơn hẳn khung của nó và mọi phép canh lề đều lệch, lại còn tốn byte
     để mã hoá khoảng trống.
  2. **HẠ CỠ VỀ CAO 114px.** Chỗ dùng lớn nhất cao 38px (bảng explorer), nên
     114 = 3× cho màn hình DPR3. Giữ nguyên cỡ gốc là tải 467 KB cho một thứ vẽ
     ra 38px — đúng lỗi mà dự án đã trả giá để sửa (kho ảnh 72 MB → 2,79 MB).
  3. **NÉN PNG 256 MÀU (FASTOCTREE).**

⚠️ ĐÃ ĐO 4 CÁCH NÉN Ở CỠ HIỂN THỊ THẬT (117×34, so với bản gốc 1736×505 hạ thẳng
   xuống cùng cỡ) — PNG 256 màu thắng cả hai mặt:
       PNG RGBA      29,7 KB   lệch TB 0,26/255
       PNG 256 màu    6,4 KB   lệch TB 0,52/255   <-- chọn
       WebP q80      14,2 KB   lệch TB 0,52/255   (nặng gấp 2,2× mà không nét hơn)
       AVIF q72       8,7 KB   lệch TB 0,63/255   (vừa nặng hơn vừa xấu hơn)
   Lệch 0,52/255 là 0,2% — mắt không thấy. Vì PNG thắng nên **dùng MỘT file cho
   mọi nơi, không cần `<picture>` với AVIF/WebP** — cùng lý do đã chọn PNG cho
   `img/luna-side.png`.

⚠️ ĐỪNG DÙNG `Image.convert("P", palette=ADAPTIVE)` — nhánh đó **làm phẳng alpha
   thành trong-suốt-nhị-phân** ở nhiều phiên bản Pillow, tức chặt hết viền mềm và
   vầng sáng quanh chữ Q. Phải dùng `quantize(method=FASTOCTREE)`, nó giữ alpha
   theo từng ô bảng màu (đo được: 136 mức alpha trung gian còn lại trên 254).
"""
import os
import sys

SRC = os.path.join("img", "AstroQ logo1.png")
OUT = os.path.join("img", "astroq-logo.png")
TARGET_H = 114          # 3× chỗ dùng cao nhất (38px ở bảng explorer)
COLORS = 256

try:
    from PIL import Image
except ImportError:
    print("Thieu Pillow: pip install Pillow")
    sys.exit(1)


def main():
    if not os.path.exists(SRC):
        print(f"Khong thay ban goc: {SRC}")
        sys.exit(1)

    src_kb = os.path.getsize(SRC) / 1024
    im = Image.open(SRC).convert("RGBA")
    box = im.split()[3].getbbox()          # (1) cat vien trong suot
    if box is None:
        print("Anh khong co pixel nao khong trong suot?")
        sys.exit(1)
    im = im.crop(box)
    w0, h0 = im.size

    w = round(w0 * TARGET_H / h0)           # (2) ha co, giu ti le
    im = im.resize((w, TARGET_H), Image.LANCZOS)
    im = im.quantize(colors=COLORS, method=Image.FASTOCTREE)   # (3) nen
    im.save(OUT, optimize=True)

    out_kb = os.path.getsize(OUT) / 1024
    print(f"nguon   {SRC}  {src_kb:.0f} KB")
    print(f"        khung goc 2162x1080 -> noi dung thuc {w0}x{h0}")
    print(f"asset   {OUT}  {w}x{TARGET_H}  {out_kb:.1f} KB  "
          f"(-{100 - out_kb * 100 / src_kb:.0f}%)")
    print(f"\nTi le {w / TARGET_H:.2f}:1 — cao 32px thi rong {round(32 * w / TARGET_H)}px.")


if __name__ == "__main__":
    main()
