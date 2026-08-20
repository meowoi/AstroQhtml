# -*- coding: utf-8 -*-
"""
make_og.py — sinh lại ẢNH THẺ CHIA SẺ CỦA TRANG CHỦ (`img/og-cover-v2.jpg`).

    python scratchpad/make_og.py

⚠️⚠️ VÌ SAO PHẢI SINH LẠI (20/08/2026 — ngày mở cửa). Bản `img/og-cover.jpg` mang
   HAI thứ nay đều sai: chip `PRE-LAUNCH · 08/2026` (đã mở cửa) và huy hiệu
   `500 PURPLE METEORS` (mức mới cho tài khoản đăng ký sau mở cửa là 100 —
   `Wallet.StarterBonus`). Đây là **mặt tiền** mà người lạ nhìn thấy đầu tiên khi
   một link astroq.org được dán lên Facebook/Zalo.

⚠️⚠️ TÊN FILE MỚI, KHÔNG GHI ĐÈ — và đây là chỗ dễ làm sai nhất. Facebook cache
   `og:image` **theo URL**; ghi nội dung mới lên cùng một URL thì bản cache cũ vẫn
   sống và bài đăng vẫn hiện chữ `PRE-LAUNCH · 500`. Đổi tên là cách chắc chắn duy
   nhất để phá cache. Cùng luật đã chốt 18/08: *bề mặt bị bên thứ ba cache không được
   mang một lời hứa sẽ hết hạn*.

⚠️⚠️ ẢNH MỚI CỐ Ý KHÔNG MANG SỐ VÀ KHÔNG MANG NGÀY. Bản cũ sai đúng vì nó mang cả
   hai. Một con số quà (100) là thứ sẽ đổi, một cột mốc thời gian là thứ sẽ qua —
   in chúng lên một bề mặt không un-cache được là tự hẹn ngày phải đổi tên file lần
   nữa. Nên huy hiệu chỉ ghi `QUÀ KHỞI ĐẦU · PURPLE METEORS`, con số nằm ở trang chủ
   (nơi `check_pages` mục [32] đối chiếu được với hằng số server).

⚠️ FONT VÀ NỀN LẤY TỪ CHÍNH DỰ ÁN, dùng lại `build_font()`/`make_backdrop()` của
   `make_share_cards.py` — không tải font ngoài, và không dựng bộ ghép font thứ hai
   (bản subset trong `fonts/` là woff2 nên Pillow không đọc được trực tiếp; chi tiết
   ở chú thích của `build_font`). Bản `make_og.py` gốc (26/07/2026) đã MẤT khỏi máy
   cùng cảnh `gen_wiki_data*.py`; đây là bản dựng lại.
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import make_share_cards as SC          # noqa: E402  (dùng lại font + nền + bố cục)

OUT = os.path.join(ROOT, "img", "og-cover-v2.jpg")
OLD = "img/og-cover.jpg"
NEW = "img/og-cover-v2.jpg"

# Tông tím thương hiệu (khớp `--purple` ở css/common.css của dự án).
ACCENT = (168, 85, 247)

ok = bad = 0


def check(label, cond, detail=""):
    global ok, bad
    if cond:
        ok += 1
        print("  [OK]   " + label + (("  " + str(detail)) if detail else ""))
    else:
        bad += 1
        print("  [HONG] " + label + "  " + str(detail))


print("\n  SINH LAI ANH THE CHIA SE CUA TRANG CHU")
print("=" * 60)

font_path = SC.build_font()
fonts = SC.load_fonts(font_path)
backdrop = SC.make_backdrop()

im = SC.draw_card(
    backdrop, fonts,
    kicker="QUÀ KHỞI ĐẦU · PURPLE METEORS",
    title="Khám Phá Ngân Hà Tri Thức",
    # ⚠️ DÒNG PHỤ PHẢI NGẮN: `draw_card` kẹp bề rộng cho TIÊU ĐỀ nhưng KHÔNG
    #    kẹp cho dòng phụ, nên câu dài chạy thẳng xuống dưới linh vật và mất
    #    chữ ở đúng mặt tiền thương hiệu. Đo được: cột chữ rộng 716px.
    sub="Vũ trụ · AI · Vật lý Lượng tử",
    mate="comet-cheer.png" if os.path.exists(
        os.path.join(SC.MATE_DIR, "comet-cheer.png")) else None,
    accent=ACCENT,
)
im.save(OUT, "JPEG", quality=78, optimize=True, progressive=True)
size = os.path.getsize(OUT)
print("\n  da ghi: %s (%s byte)\n" % (NEW, f"{size:,}"))

# ── phép kiểm ────────────────────────────────────────────────────────────
from PIL import Image                                        # noqa: E402
w, h = Image.open(OUT).size
check("dung co 1200x630 (nho hon la Facebook cat xen)", (w, h) == (1200, 630),
      "%dx%d" % (w, h))
check("duoi 200 KB (the chia se tai truoc khi ai kip doc)", size < 200_000,
      "%s byte" % f"{size:,}")

# Hai bản trang chủ phải trỏ ảnh MỚI, và không còn dấu vết ảnh cũ.
for rel in ("index.html", os.path.join("en", "index.html")):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    check("%s tro og:image sang ban MOI" % rel, NEW in s)
    check("%s khong con tro ban cu (Facebook cache theo URL)" % rel, OLD not in s)
    n_alt = len(re.findall(r'(?:og:image:alt|twitter:image:alt)', s))
    check("%s con du 2 the alt cho anh" % rel, n_alt == 2, n_alt)

# Ảnh mới KHÔNG được mang con số hay ngày — đó là cả lý do nó tồn tại. Không đọc
# được chữ trong JPEG nên kiểm ở NGUỒN: chuỗi truyền vào draw_card.
src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
# ⚠️ CẮT HẸP VÀ BÓC CHÚ THÍCH. Lát rộng hơn thì nó bắt cả `quality=78`, `"=" * 60`
#    và con số trong chính lời giải thích ("cột chữ rộng 716px") rồi báo hỏng oan —
#    đúng lỗi "đếm cả chữ trong ghi chú của chính mình" mà dự án đã trả giá nhiều lần.
_args = src.split("im = SC.draw_card(")[1].split("\n)\n")[0]
_args = re.sub(r"#[^\n]*", "", _args)          # bỏ chú thích, giữ chuỗi
check("anh moi khong mang con so nao", not re.search(r"\d", _args),
      re.findall(r"\d+", _args)[:4])
check("anh moi khong mang moc thoi gian nao",
      not re.search(r"PRE-LAUNCH|20\d\d|sap ra mat|coming soon", _args, re.I))

print("\n" + "-" * 60)
print("  KET QUA: %d dat / %d hong" % (ok, bad))
print("-" * 60 + "\n")
sys.exit(1 if bad else 0)
