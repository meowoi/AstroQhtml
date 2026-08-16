# -*- coding: utf-8 -*-
"""make_bg_assets.py — SINH ẢNH NỀN cho Trung Tâm Điều Hướng từ một ảnh gốc.

    python scratchpad/make_bg_assets.py background/originals/quydao-saohoa.png marsorbit
    python scratchpad/make_bg_assets.py --do background/Khoangluna-1920.webp   (chỉ ĐO, không ghi)

Sinh đúng 4 biến thể vào `background/<slug>-{1280,1920}.{avif,webp}`, cùng khuôn
`Khoangluna-*` đang chạy — nhờ vậy `<picture>` ở dashboard chỉ cần đổi tên file.

⚠️ VÌ SAO CÓ SCRIPT NÀY, KHÔNG LÀM TAY: ảnh nền là thứ NẶNG NHẤT của dashboard. Bản
   gốc `Khoangluna.png` từng là **6,9 MB** (PNG cho một ảnh dạng photo — sai định
   dạng, không có alpha) và đã cắt xuống **99 KB avif (−98,6%)**. Làm tay là sớm muộn
   có một nền lọt vào ở cỡ 2 MB, mà nó nằm trên đường tải đầu của trang trẻ mở nhiều
   nhất. Script ép đúng bộ biến thể và **ĐO rồi báo** thay vì để người làm tự tin.

⚠️ ĐO ĐỘ SÁNG VÙNG GIỮA, KHÔNG CHỈ ĐO CỠ FILE. Hero ("Chào mừng trở lại, …") là chữ
   TRẮNG nằm giữa khung; lớp phủ tối của `.bg-photo::after` chỉ là
   `rgba(6,12,34, .45→.28→.55)`, tức nó KHÔNG cứu được một ảnh sáng ở giữa. Dự án đã
   trả giá đúng loại lỗi này hai lần với bản đồ Trái Đất: "bản đồ phẳng tối hơn 4,7
   lần" là một con số đo SAI ĐỊA CHỈ, và thứ quyết định độ đọc được là KHUNG NHÌN
   chứ không phải cỡ file. Nên script in ra độ sáng dải giữa và cảnh báo nếu quá sáng.

⚠️ TỈ LỆ PHẢI GẦN 1,53 (= 1920/1253 của ảnh đang chạy). `.bg-photo img` dùng
   `object-fit:cover`, nên ảnh vuông (ví dụ `img/tramvutru.png` 1080×1080) sẽ bị cắt
   mất 44% chiều cao trên màn 16:9 — và phần bị cắt luôn là phần trên/dưới, tức mất
   đúng vành khoang tàu. Script từ chối ảnh lệch tỉ lệ quá xa.
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "background")

# Tỉ lệ khớp ảnh đang chạy: 1920×1253 → 1,532.
TARGET_RATIO = 1920 / 1253
RATIO_TOL = 0.18          # lệch quá mức này thì cover sẽ cắt mất một mảng lớn

# ⚠️ BỀ RỘNG HẠ TỪ 1920 XUỐNG 1536 (16/08/2026) — CÓ CHỦ ĐÍCH, KHÔNG PHẢI NỚI TAY.
#    Ảnh nền do chủ dự án sinh bằng ChatGPT ra cỡ 1536×1024. Ba hướng đã cân:
#    ① đòi ≥1920 → công cụ không cho, phải upscale = pixel BỊA;
#    ② phóng 1536→1920 bằng LANCZOS → đo được: nhoè sẵn rồi mới nén nên hỏng KÉP,
#       phải hạ tới q35 mới vừa trần và lúc đó mất hẳn một lớp sao mờ (đã so 1:1);
#    ③ sinh biến thể ĐÚNG bề rộng gốc → không byte nào là pixel bịa; màn 1920 để
#       trình duyệt tự phóng 1,25×, cùng độ nét mà không phải tải thêm.
#    Chọn ③. Đổi bộ này thì `<picture>` ở dashboard.html phải đổi srcset theo.
WIDTHS = (1536, 1024)
MIN_SRC_W = 1536          # nhỏ hơn thì phóng to = nhoè, đừng nhận

# Trần cỡ file giữ nguyên theo VAI TRÒ biến thể (lớn/nhỏ), lấy từ bộ đang chạy
# (avif 101,7 KB · webp 152,6 KB ở bản lớn). Đây là ngân sách BYTE trên đường
# truyền, không phải ngân sách theo pixel — nên hạ bề rộng KHÔNG được nới trần.
BUDGET = {("avif", 1536): 130_000, ("webp", 1536): 200_000,
          ("avif", 1024): 80_000,  ("webp", 1024): 120_000}

# Độ sáng dải giữa (nơi chữ hero nằm). Ảnh đang chạy đo được ~46 → mốc cảnh báo 96.
MID_BRIGHT_WARN = 96


def mid_brightness(im):
    """Độ sáng TB của dải giữa theo chiều dọc — chỗ chữ hero thật sự nằm."""
    g = im.convert("L")
    w, h = g.size
    band = g.crop((int(w * 0.18), int(h * 0.22), int(w * 0.82), int(h * 0.62)))
    px = list(band.getdata())
    return sum(px) / len(px)


def measure(path):
    im = Image.open(path)
    print("  %-34s %s %dx%d  ti le %.3f  %.0f KB  sang giua %.1f"
          % (os.path.basename(path), im.mode, im.width, im.height,
             im.width / im.height, os.path.getsize(path) / 1024, mid_brightness(im)))
    return im


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only_measure = "--do" in sys.argv

    if not args:
        print(__doc__)
        print("Anh nen dang chay:")
        for f in sorted(os.listdir(OUT_DIR)):
            measure(os.path.join(OUT_DIR, f))
        return 0

    src = args[0]
    if only_measure:
        measure(src)
        return 0

    if len(args) < 2:
        print("Thieu <slug>. Vi du: ... quydao-saohoa.png marsorbit")
        return 1
    slug = args[1]
    if not slug.replace("-", "").isalnum():
        print("slug chi duoc gom chu, so va dau gach ngang: " + slug)
        return 1

    im = Image.open(src)
    print("Anh goc:")
    measure(src)

    # ── Ba hang rao TRUOC khi ghi file nao ──
    bad = []
    if im.width < MIN_SRC_W:
        bad.append("rong %dpx < %d (phong to se nhoe)" % (im.width, MIN_SRC_W))
    ratio = im.width / im.height
    if abs(ratio - TARGET_RATIO) > RATIO_TOL:
        bad.append("ti le %.2f lech qua xa %.2f — `object-fit:cover` se cat mat mot mang lon"
                   % (ratio, TARGET_RATIO))
    if bad:
        print("\nTU CHOI, khong ghi file nao:")
        for b in bad:
            print("  - " + b)
        print("\nSua anh goc roi chay lai. Xem phan spec o dau file.")
        return 1

    mid = mid_brightness(im)
    if mid > MID_BRIGHT_WARN:
        print("\n⚠️ CANH BAO: dai giua sang %.1f (moc %d). Chu hero la chu TRANG va lop"
              % (mid, MID_BRIGHT_WARN))
        print("   phu toi cua .bg-photo::after KHONG du de cuu — hay kiem tra bang mat")
        print("   sau khi gan vao, hoac chon anh co vung giua toi hon.")

    # ── Sinh 4 bien the ──
    print("\nSinh bien the:")
    made = []
    for w in WIDTHS:
        h = round(w / TARGET_RATIO)
        # Cat theo tam roi thu ve dung khung — khong keo gian anh.
        base = im.convert("RGB")
        sr = base.width / base.height
        if sr > TARGET_RATIO:                       # rong hon: cat hai ben
            nw = round(base.height * TARGET_RATIO)
            x = (base.width - nw) // 2
            base = base.crop((x, 0, x + nw, base.height))
        elif sr < TARGET_RATIO:                     # cao hon: cat tren duoi
            nh = round(base.width / TARGET_RATIO)
            y = (base.height - nh) // 2
            base = base.crop((0, y, base.width, y + nh))
        base = base.resize((w, h), Image.LANCZOS)

        for fmt, q in (("avif", 62), ("webp", 82)):
            out = os.path.join(OUT_DIR, "%s-%d.%s" % (slug, w, fmt))
            try:
                base.save(out, quality=q, method=6) if fmt == "webp" else base.save(out, quality=q)
            except Exception as e:
                print("  [HONG] %s: %s" % (os.path.basename(out), e))
                continue
            size = os.path.getsize(out)
            cap = BUDGET[(fmt, w)]
            flag = "ok" if size <= cap else "VUOT TRAN"
            print("  [%s] %-28s %6.1f KB (tran %.0f KB)"
                  % (flag, os.path.basename(out), size / 1024, cap / 1024))
            made.append(out)

    print("\nDa sinh %d file vao background/." % len(made))
    print("Buoc tiep (3 cho, xem CLAUDE.md muc Kho Trang Tri):")
    print("  1. Cosmetics.cs  — them new(\"bg-%s\", \"bg\", <gia>)" % slug)
    print("  2. js/cosmetics.js — them TEN o ca vi va en")
    print("  3. css/cockpit.css — them lop nen cho :root[data-bg=\"bg-%s\"]" % slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
