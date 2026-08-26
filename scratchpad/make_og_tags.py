# -*- coding: utf-8 -*-
"""
make_og_tags.py — GẮN THẺ CHIA SẺ (Open Graph + Twitter) vào `<head>` từng trang.

    python scratchpad/make_og_tags.py            # gắn / cập nhật
    python scratchpad/make_og_tags.py --check    # chỉ kiểm, không ghi gì

VÌ SAO
──────
Đăng link lên fanpage thì Facebook/Zalo đọc `og:*` để dựng thẻ xem trước. Trước
18/08/2026 chỉ **2/36 trang** có (`index.html`, `en/index.html`), nên đăng link
một trò chơi cho ra một ô xám không ảnh.

⚠️⚠️ TÊN VÀ MÔ TẢ ĐỌC TỪ `games.html`, TUYỆT ĐỐI KHÔNG GÕ LẠI Ở ĐÂY.
   Đây là bản sao thứ hai của cùng một chuỗi, mà dự án đã trả giá nhiều lần cho
   loại đó (thẻ Đường Đua từng hứa "1.200 m" trong khi game đã đổi thành 14.000).
   Gõ lại tên game vào thẻ chia sẻ còn tệ hơn: bên lệch là bên **người lạ nhìn
   thấy đầu tiên**, trước cả khi họ bấm vào.

⚠️ KHỐI ĐƯỢC BỌC GIỮA HAI MỐC `OG:BEGIN` / `OG:END` và script này **ghi đè** phần
   giữa. Nhờ vậy chạy lại bao nhiêu lần cũng ra cùng một file (idempotent) — đổi
   tên game thì chạy lại là xong, không phải đi sửa 15 chỗ bằng tay.
   ⛔ Đừng sửa tay phần giữa hai mốc: lần chạy sau mất.

⚠️ CÁC TRANG NÀY ĐANG `noindex,follow` VÀ ĐÓ LÀ CHỦ ĐÍCH — `noindex` chặn LẬP CHỈ
   MỤC của công cụ tìm kiếm, không liên quan tới thẻ xem trước.
   ⚠️ [Inference] Trình thu thập của Facebook/Zalo đọc `og:*` mà không xét thẻ
      robots — đây là hành vi tiêu chuẩn của chúng, nhưng tôi **không kiểm chứng
      được từ máy này**. Sau khi push thì dán một link vào Facebook Sharing
      Debugger để xác nhận, đừng cho là chắc chắn.

⚠️ `og:url` DÙNG ĐƯỜNG DẪN TUYỆT ĐỐI. Thẻ này được đọc trên máy chủ của
   Facebook, không có ngữ cảnh trang — đường dẫn tương đối là thẻ vô nghĩa.
"""
import io
import os
import re
import sys

# BAT BUOC — console Windows mac dinh cp1252. Nhan cua phep kiem thi khong dau,
#    nhung `detail` va ten trang lay tu chinh ma nguon (tieng Viet co dau), nen in ra
#    la UnicodeEncodeError nem GIUA LUC CHAY: bo do, khong in dong tong ket nao, va
#    trong y het nhu bi chan boi thu khac. Cung cai bay `smoke_locks.py` da ghi tu
#    truoc; ba file nay thieu no va da bi 26/08/2026. Sua o DAY chu khong bat nguoi
#    chay phai nho `PYTHONIOENCODING=utf-8`.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SITE = "https://astroq.org"

BEGIN = "<!-- OG:BEGIN — sinh bằng scratchpad/make_og_tags.py · ĐỪNG sửa tay phần dưới -->"
END = "<!-- OG:END -->"

# Trang ngoài mini-game. Mô tả viết ở đây vì chúng không có nguồn nào khác;
# tên game thì KHÔNG (đọc từ games.html).
EXTRA = {
    "mission-earth.html": dict(
        img="mission-earth",
        title="Nhiệm vụ 01: Hành Tinh Xanh",
        desc="Bảy chặng khám phá Trái Đất cùng Comet: quét bề mặt, đọc 4,54 tỷ năm lịch sử, "
             "tìm sự sống và đổi sang năng lượng sạch. Số liệu dẫn nguồn NASA.",
    ),
    "mission-orbit.html": dict(
        img="mission-orbit",
        title="Nhiệm vụ 02: Mắt Thần Trên Quỹ Đạo",
        desc="Vệ tinh nhìn thấy gì mà mắt người không thấy? Năm chặng học cách đọc một tấm ảnh "
             "vệ tinh, theo đúng năm mẹo NASA dạy.",
    ),
    "lab.html": dict(
        img="lab",
        title="Phòng Nghiên Cứu",
        desc="Thả một chiếc lông chim và một hòn đá trên Mặt Trăng xem cái nào chạm đất trước. "
             "Thí nghiệm trọng lực, cân nặng và ánh sáng cho trẻ 8–15.",
    ),
    "crew.html": dict(
        img="crew",
        title="Phi Hành Đoàn Đầu Tiên",
        desc="Bức tường 500 chỗ ngồi của những phi hành gia đầu tiên trên astroQ. "
             "Mỗi chỗ là một số hiệu và một nhân vật — không có tên thật của ai.",
    ),
    "games.html": dict(
        img="games",
        title="Khu Huấn Luyện",
        desc="Mười trò chơi rèn kỹ năng phi hành gia: phản xạ, định hướng, phân bổ tài nguyên "
             "và soi lỗi dữ liệu. Chơi bằng Thiên thạch tím kiếm được từ việc học.",
    ),
}


def games_from_source():
    s = io.open(os.path.join(ROOT, "games.html"), encoding="utf-8").read()
    blk = re.search(r"var GAMES\s*=\s*\[(.*?)\n\s*\];", s, re.S).group(1)
    out = {}
    for m in re.finditer(r"\{(.*?)\}\s*\}\s*,?", blk, re.S):
        b = m.group(1)
        file = re.search(r'file\s*:\s*"([^"]*)"', b)
        name = re.search(r'name\s*:\s*\{\s*vi\s*:\s*"([^"]*)"', b)
        desc = re.search(r'desc\s*:\s*\{\s*vi\s*:\s*"([^"]*)"', b)
        if file and name and desc:
            out[file.group(1)] = dict(
                img=file.group(1).replace(".html", ""),
                title=name.group(1),
                desc=desc.group(1),
            )
    return out


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def block(page, info):
    url = f"{SITE}/{page}"
    img = f"{SITE}/img/og/{info['img']}.jpg"
    title = f"{info['title']} · astroQ.org"
    desc = info["desc"]
    alt = f"Thẻ chia sẻ astroQ.org — {info['title']}"
    L = [BEGIN,
         '<meta property="og:type" content="website" />',
         '<meta property="og:site_name" content="astroQ.org" />',
         '<meta property="og:locale" content="vi_VN" />',
         f'<meta property="og:url" content="{url}" />',
         f'<meta property="og:title" content="{esc(title)}" />',
         f'<meta property="og:description" content="{esc(desc)}" />',
         f'<meta property="og:image" content="{img}" />',
         '<meta property="og:image:type" content="image/jpeg" />',
         '<meta property="og:image:width" content="1200" />',
         '<meta property="og:image:height" content="630" />',
         f'<meta property="og:image:alt" content="{esc(alt)}" />',
         '<meta name="twitter:card" content="summary_large_image" />',
         f'<meta name="twitter:title" content="{esc(title)}" />',
         f'<meta name="twitter:description" content="{esc(desc)}" />',
         f'<meta name="twitter:image" content="{img}" />',
         f'<meta name="twitter:image:alt" content="{esc(alt)}" />',
         END]
    return "\n".join(L)


def apply(page, info, check):
    path = os.path.join(ROOT, page)
    if not os.path.exists(path):
        return "THIEU-TRANG", False
    src = io.open(path, encoding="utf-8").read()
    blk = block(page, info)

    if BEGIN in src and END in src:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), blk, src, flags=re.S)
        what = "giu-nguyen" if new == src else "cap-nhat"
    else:
        # chèn ngay sau </title> — nơi mọi trang đều có, và thẻ og nên đứng gần
        # title để người đọc file thấy chúng cùng một chỗ
        m = re.search(r"</title>", src)
        if not m:
            return "KHONG-CO-TITLE", False
        new = src[:m.end()] + "\n" + blk + src[m.end():]
        what = "them-moi"

    if what != "giu-nguyen" and not check:
        io.open(path, "w", encoding="utf-8", newline="").write(new)
    return what, what != "giu-nguyen"


def main():
    check = "--check" in sys.argv
    pages = dict(games_from_source())
    pages.update(EXTRA)

    if len(pages) < 15:
        print(f"  [HONG] chi gom duoc {len(pages)} trang (cho >= 15)")
        return 1

    changed = 0
    print(f"{'trang':28} {'ket qua':12} anh")
    print("-" * 72)
    for page in sorted(pages):
        info = pages[page]
        img_rel = os.path.join("img", "og", info["img"] + ".jpg")
        has_img = os.path.exists(os.path.join(ROOT, img_rel))
        what, did = apply(page, info, check)
        changed += did
        flag = "" if has_img else "  [HONG] THIEU ANH"
        print(f"{page:28} {what:12} {img_rel}{flag}")
    print("-" * 72)
    print(f"  {len(pages)} trang · {changed} thay đổi" + ("  (--check: không ghi)" if check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
