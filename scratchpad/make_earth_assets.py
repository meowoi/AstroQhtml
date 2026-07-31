# -*- coding: utf-8 -*-
"""
make_earth_assets.py — tạo asset ảnh Trái Đất cho NHIỆM VỤ 01 bản 2D.

    cd AstroQhtml
    set PYTHONIOENCODING=utf-8 & python scratchpad/make_earth_assets.py

VÌ SAO HOST NỘI BỘ CHỨ KHÔNG NẠP TRỰC TIẾP TỪ NASA:
  · Bản đồ phẳng gốc là **2,45 MB** (5400×2700) — nạp thẳng là quá nặng cho một app
    dành cho trẻ dùng mạng yếu, và dự án đã trả giá để hạ kho ảnh 72 MB → 2,79 MB.
  · Thêm một tên miền ngoài là thêm DNS+TCP+TLS. Dự án đã tự host font để cắt đúng
    hai kết nối như vậy; không có lý gì mở lại một cái mới.
  · Ảnh trên CDN của NASA có thể đổi/biến mất; asset nội bộ thì kiểm được bằng
    `check_pages.py` như mọi asset khác.

ĐO ĐƯỢC (không phải đoán):
    bản đồ phẳng 5400×2700  2,45 MB  →  2048×1024  AVIF 180 KB / WebP 203 KB  (−92%)
    quả cầu       640×640     68 KB  →   640×640   AVIF  50 KB / WebP  64 KB  (−26%)

VÌ SAO 2048 CHỨ KHÔNG PHẢI 1600 HAY 2560:
  Bước `life` cho phóng tới 3×. Khung ảnh rộng ~700px trên desktop, nên ở zoom 3 nó
  hiển thị tương đương ~2100px — 2048 vừa đủ nét ở mức phóng lớn nhất mà không tốn
  thêm ~80 KB như 2560. 1600 thì mờ rõ khi phóng hết.

⚠️ BẢN ĐỒ PHẢI LÀ BẢN ĐỒ PHẲNG (equirectangular) CHO BƯỚC `life`.
   Ảnh quả cầu `GSFC_..._e001386` là ảnh CHỤP quả cầu tâm Bắc Mỹ — Amazon, Himalaya,
   Nam Cực, Great Barrier Reef đều ở nửa bên kia. Đặt 4 điểm mẫu vật theo lat/lon
   lên ảnh đó là **dạy sai địa lý** (đúng lỗi đã mắc ở bản 3D với nhiễu fBm). Chỉ
   bản đồ phẳng cho phép quy lat/lon → phần trăm bằng một phép chia.

⚠️ KHÔNG dùng `~thumb` của NASA làm ảnh nhỏ: đo cả 5 ảnh thì `~thumb` và `~small`
   trả về **đúng cùng số byte** — NASA phục vụ hai tên cho một file.
"""
import io
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "img", "earth"))

try:
    from PIL import Image
except ImportError:
    print("Thieu Pillow: pip install Pillow")
    sys.exit(1)

# URL nguồn — đã kiểm trả 200. Ghi lại để tái tạo được asset khi cần.
SRC = {
    "globe": ("https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e001386/"
              "GSFC_20171208_Archive_e001386~small.jpg"),
    "flat":  ("https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73580/"
              "world.topo.bathy.200401.3x5400x2700.jpg"),
}

# (ten, cỡ đích, chất lượng avif, chất lượng webp)
PLAN = [
    ("globe", (640, 640),   64, 82),
    ("flat",  (2048, 1024), 62, 80),
]


def fetch(url, path):
    if os.path.exists(path):
        print(f"  (da co) {os.path.basename(path)}")
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r, io.open(path, "wb") as f:
        f.write(r.read())
    print(f"  tai xong {os.path.basename(path)} "
          f"({os.path.getsize(path)/1048576:.2f} MB)")


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_src")
    os.makedirs(tmp, exist_ok=True)

    print("=== Tai anh goc tu NASA ===")
    for key, url in SRC.items():
        fetch(url, os.path.join(tmp, key + ".jpg"))

    print("\n=== Sinh asset ===")
    total_src = total_out = 0
    for key, size, q_avif, q_webp in PLAN:
        src = os.path.join(tmp, key + ".jpg")
        total_src += os.path.getsize(src)
        im = Image.open(src).convert("RGB")
        if im.size != size:
            im = im.resize(size, Image.LANCZOS)
        for ext, kw in (("avif", dict(quality=q_avif)),
                        ("webp", dict(quality=q_webp, method=6))):
            p = os.path.join(OUT, f"{key}-{size[0]}.{ext}")
            im.save(p, **kw)
            n = os.path.getsize(p)
            print(f"  {key}-{size[0]}.{ext:<5} {size[0]}x{size[1]:<6} {n/1024:>7.0f} KB")
            if ext == "avif":
                total_out += n

    print(f"\nAnh goc: {total_src/1048576:.2f} MB  ->  "
          f"asset (AVIF): {total_out/1024:.0f} KB  "
          f"(-{100 - total_out*100/total_src:.0f}%)")
    print(f"\nAnh goc giu o {tmp} — KHONG commit (.gitignore chan img/earth/_src/).")


if __name__ == "__main__":
    main()
