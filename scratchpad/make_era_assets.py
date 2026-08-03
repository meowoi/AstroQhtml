# -*- coding: utf-8 -*-
"""Sinh asset 4 ảnh minh hoạ mốc thời gian của bước ② (`docs/decisions/005` mục ⑩).

    python scratchpad/make_era_assets.py

Đọc bản gốc `img/era/<id>.png` (1536×1024, 1,9–2,6 MB mỗi cái) và xuất
`img/era/<id>-{700,1120}.{avif,webp}`.

⚠️ BẢN GỐC KHÔNG COMMIT — `.gitignore` chặn `img/era/*.png`. Repo này deploy công khai
   qua GitHub Pages nên mọi thứ commit là thứ người khác phải tải khi clone; 9,4 MB ảnh
   không ai dùng là đúng loại rác mà đợt dọn 30/07 đã phải đi gỡ. Muốn sinh lại asset
   thì chạy lại script này với bản gốc trong tay.

⚠️ ĐO RỒI MỚI CHỌN ĐỊNH DẠNG, ĐỪNG CHÉP KẾT LUẬN CŨ. Với `img/astroq-logo.png` thì
   PNG-256 thắng cả AVIF lẫn WebP — nhưng đó là ảnh PHẲNG, ít màu. Bốn bức này là tranh
   vẽ có gradient (44k–223k màu), đo được (`probe_era_img.py`) PNG-256 **thua gấp 3 lần**:
       ở 700px · dino → AVIF q60 49 KB · WebP q72 50 KB · PNG-256 159 KB
   Nên ở đây là AVIF + WebP, không có nhánh PNG.

⚠️ HAI CỠ, KHÔNG PHẢI MỘT. Cỡ hiển thị thật ~700px (bảng `.me-time` rộng
   `min(760px, 100vw-24px)` trừ padding). Bản 700 cho máy thường và mạng yếu; bản 1120
   cho màn DPR2. Trình duyệt tự chọn qua `srcset` — cùng lối đã dùng cho
   `background/Khoangluna`.
"""
import os
import sys

from PIL import Image

# ⚠️ ĐỌC TỪ THƯ MỤC, ĐỪNG GÁN CỨNG. Trước 02/08/2026 đây là một tuple bốn tên; chủ dự án
#    đặt bức thứ năm (`now.png`) vào thì script chạy xong mà không sinh asset nào cho nó,
#    và báo cáo vẫn in "cả 4 mốc" như thể không thiếu gì — im lặng hoàn toàn.
#    Quét thư mục thì thêm bức thứ sáu cũng không phải sửa dòng nào.
def _sources(d):
    import glob
    return tuple(sorted(
        os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(d, "*.png"))
        # bỏ chính các asset đã sinh (chúng là .avif/.webp, nhưng lọc cho chắc)
        if "-" not in os.path.basename(f)))
WIDTHS = (700, 1120)
SRC_DIR = "img/era"

# Chất lượng đã đo: đủ nhẹ mà lệch so với bản resize chỉ ~2-3% (RMSE 5-7 / 255).
AVIF_Q = 60
WEBP_Q = 72


def main():
    if not os.path.isdir(SRC_DIR):
        sys.exit("Khong thay %s" % SRC_DIR)
    ERAS = _sources(SRC_DIR)
    if not ERAS:
        sys.exit("Khong thay anh goc .png nao trong %s" % SRC_DIR)
    print("nguon doc duoc: %s" % ", ".join(ERAS))
    total_src = total_out = 0
    print("%-7s %5s | %9s %9s" % ("anh", "rong", "avif", "webp"))
    print("-" * 38)
    for name in ERAS:
        src_path = os.path.join(SRC_DIR, name + ".png")
        if not os.path.exists(src_path):
            sys.exit("THIEU BAN GOC: %s" % src_path)
        src = Image.open(src_path).convert("RGB")
        total_src += os.path.getsize(src_path)
        for w in WIDTHS:
            h = round(src.height * w / src.width)
            im = src.resize((w, h), Image.LANCZOS)
            a = os.path.join(SRC_DIR, "%s-%d.avif" % (name, w))
            b = os.path.join(SRC_DIR, "%s-%d.webp" % (name, w))
            im.save(a, "AVIF", quality=AVIF_Q)
            im.save(b, "WEBP", quality=WEBP_Q, method=6)
            total_out += os.path.getsize(a) + os.path.getsize(b)
            print("%-7s %5d | %7.1fKB %7.1fKB"
                  % (name, w, os.path.getsize(a) / 1024, os.path.getsize(b) / 1024))
    print("-" * 38)
    print("ban goc  %6.2f MB  (KHONG commit)" % (total_src / 1048576))
    print("asset    %6.1f KB  (%d file)" % (total_out / 1024, len(ERAS) * len(WIDTHS) * 2))
    # Con so that su quan trong: mot luot choi chi tai MOT anh moi moc, ban 700.
    one = sum(os.path.getsize(os.path.join(SRC_DIR, "%s-700.avif" % n)) for n in ERAS)
    print("tai ve thuc te: %.1f KB cho ca %d moc (ban 700 avif, nap luoi tung cai)"
          % (one / 1024, len(ERAS)))


if __name__ == "__main__":
    main()
