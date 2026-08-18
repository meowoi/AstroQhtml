# -*- coding: utf-8 -*-
"""
make_share_cards.py — SINH ẢNH THẺ CHIA SẺ 1200×630 cho từng trang (`img/og/*.jpg`).

    python scratchpad/make_share_cards.py            # sinh + in bảng cỡ file
    python scratchpad/make_share_cards.py --check    # chỉ kiểm, không ghi gì

VÌ SAO CẦN
──────────
Đăng một đường dẫn lên fanpage thì Facebook/Zalo đọc thẻ `og:image`. Trước
18/08/2026 chỉ `index.html` và `en/index.html` có thẻ đó (2/36 trang), nên đăng
link một trò chơi cụ thể cho ra **một ô xám không ảnh** — khác biệt lớn nhất giữa
một bài có người bấm và một bài không.

⚠️⚠️ FONT LẤY TỪ CHÍNH `fonts/` CỦA DỰ ÁN, KHÔNG TẢI FONT NGOÀI.
   Hai lý do: (1) thẻ chia sẻ là mặt tiền thương hiệu, dùng font khác là nó không
   còn đọc ra astroQ; (2) tải font lúc build là thêm một phụ thuộc mạng vào một
   việc vốn chạy offline được. Nhưng `fonts/*.woff2` là **subset** — đo được:
   `space-grotesk-latin` có chữ cơ bản mà **thiếu ăđơưạảấầệốớứỳ**, còn
   `space-grotesk-vietnamese` có dấu mà **thiếu cả chữ cái thường**. Nên phải
   GHÉP hai subset lại thành một TTF; chỉ dùng một cái là tên game tiếng Việt
   hiện ra thành một dãy ô vuông.
   ⚠️ TTF ghép ra là **artifact build**, ghi vào thư mục tạm và KHÔNG commit —
      nguồn sự thật vẫn là hai file `.woff2` đang phục vụ trang thật.

⚠️ NỀN LẤY `background/vanhdai-1536.webp` — 4 biến thể ảnh này commit từ
   16/08/2026 mà **`grep vanhdai` trong html/css/js ra 0 kết quả**, tức byte chết
   trong một repo deploy công khai (đã ghi ở nhật ký hôm đó là việc còn treo).
   Dùng nó ở đây vừa cho ảnh một công việc thật, vừa hợp bối cảnh.
   ⚠️ TÊN TỆP DỄ ĐỌC NHẦM: `vanhdai` KHÔNG phải một vành đai thiên thạch — mở ảnh
      ra xem thì đó là **buồng lái nhìn qua ô cửa ra một hành tinh có vành**. Đúng
      thứ cần: cả app đặt trẻ trong một con tàu (`dashboard.html` là buồng lái
      thật), nên thẻ chia sẻ mở ra cùng một khung cảnh đó.

⚠️ ẢNH RA LÀ **JPEG**, không phải PNG: nền là ảnh dạng photo, PNG cho ra file
   nặng gấp nhiều lần mà mắt không phân biệt được — đúng bài học đã ghi khi hạ
   `Khoangluna.png` 6,9 MB xuống 99 KB.

⚠️ ĐỪNG SINH THẺ CHO TRANG KHÔNG AI ĐĂNG. Mỗi ảnh là byte nằm vĩnh viễn trong
   repo công khai; danh sách dưới đây chỉ gồm trang **đáng đưa lên fanpage**.
"""
import io
import os
import re
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT_DIR = os.path.join(ROOT, "img", "og")

W, H = 1200, 630          # cỡ Facebook/Zalo khuyến nghị; nhỏ hơn là bị cắt xén
JPEG_Q = 78               # đo được (bảng ở cuối file): q78 + blur 3 cho 54 KB/thẻ
BG_BLUR = 3               # ⚠️ LÀM MỜ NỀN LÀ ĐỂ NÉN, KHÔNG PHẢI CHO ĐẸP — xem ghi chú ở `make_backdrop`

BG = os.path.join(ROOT, "background", "vanhdai-1536.webp")
LOGO = os.path.join(ROOT, "img", "astroq-logo.png")
MATE_DIR = os.path.join(ROOT, "img", "mate")

CYAN = (56, 189, 248)
SUN = (255, 207, 107)
PURPLE = (143, 123, 255)
WHITE = (240, 246, 255)
DIM = (150, 170, 200)


# ─────────────────────────── FONT ───────────────────────────
def build_font():
    """
    Ghép `space-grotesk-latin` + `space-grotesk-vietnamese` thành MỘT file TTF
    để Pillow đọc được. Trả về đường dẫn tệp tạm.

    ⚠️ Phải ghép, không được chọn một trong hai — xem khối cảnh báo ở đầu file.
    """
    from fontTools.merge import Merger
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    tmp = tempfile.mkdtemp(prefix="astroq-font-")
    parts = []
    for name in ("space-grotesk-latin", "space-grotesk-vietnamese"):
        src = os.path.join(ROOT, "fonts", f"{name}.woff2")
        f = TTFont(src)
        f.flavor = None                      # bỏ vỏ woff2 → TTF thuần
        # ⚠️ PHẢI "ĐÓNG BĂNG" TRỤC ĐỘ ĐẬM TRƯỚC KHI GHÉP. Hai file này là font
        #    BIẾN THIÊN (`wght 400..700`, chọn từ 26/07/2026 để một file lo mọi
        #    độ đậm), mà `Merger` không ghép được bảng `VarStore` — nó ném
        #    `AttributeError: 'VarStore' has no attribute 'mergeMap'`. Thẻ chia
        #    sẻ chỉ cần MỘT độ đậm, nên lấy tĩnh ở 700 rồi mới ghép.
        if "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": 700}, inplace=True)
        dst = os.path.join(tmp, f"{name}.ttf")
        f.save(dst)
        parts.append(dst)

    merged = os.path.join(tmp, "space-grotesk-merged.ttf")
    Merger().merge(parts).save(merged)
    return merged


def load_fonts(path):
    return {
        "title": ImageFont.truetype(path, 74),
        "title_sm": ImageFont.truetype(path, 60),
        "kicker": ImageFont.truetype(path, 26),
        "sub": ImageFont.truetype(path, 30),
    }


def fits(draw, text, font, limit):
    return draw.textlength(text, font=font) <= limit


# ─────────────────────────── NỀN ───────────────────────────
def make_backdrop():
    """
    Nền dùng chung cho mọi thẻ: vành đai thiên thạch, cắt về 1200×630, làm tối và
    phủ một lớp gradient để chữ trắng luôn đọc được.

    ⚠️ LÀM TỐI LÀ BẮT BUỘC, KHÔNG PHẢI CHO ĐẸP. Ảnh gốc có dải sáng; chữ trắng đặt
       thẳng lên đó thì mất chữ ở đúng chỗ sáng — và mỗi thẻ tên game một độ dài
       nên không thể né bằng cách đặt chữ tránh chỗ sáng.
    """
    im = Image.open(BG).convert("RGB")
    # cắt giữa theo tỉ lệ 1200:630
    tw, th = W / H, im.width / im.height
    if th > tw:
        nw = int(im.height * tw)
        im = im.crop(((im.width - nw) // 2, 0, (im.width + nw) // 2, im.height))
    else:
        nh = int(im.width / tw)
        im = im.crop((0, (im.height - nh) // 2, im.width, (im.height + nh) // 2))
    im = im.resize((W, H), Image.LANCZOS)

    # tối đều + đậm dần sang trái (nơi đặt chữ)
    dark = Image.new("RGB", (W, H), (6, 12, 34))
    im = Image.blend(im, dark, 0.58)

    grad = Image.new("L", (W, 1))
    for x in range(W):
        k = 1 - x / W
        grad.putpixel((x, 0), int(210 * (k ** 1.35)))
    grad = grad.resize((W, H))
    im = Image.composite(dark, im, grad)

    # ⚠️ LÀM MỜ NỀN LÀ MỘT PHÉP NÉN, và con số là đo được chứ không phải thẩm mỹ.
    #    Ảnh vành đai thiên thạch đầy chi tiết tần số cao — thứ JPEG tốn byte nhất.
    #    Đo trên cùng một thẻ: blur 0 → 67 KB · blur 3 → 54 KB · blur 6 → 49 KB
    #    (đều ở q78). Chọn 3 vì từ đó trở đi mắt đọc ra "hậu cảnh xa" chứ không ra
    #    "ảnh bị hỏng", mà vẫn cắt được 19%. Chữ và linh vật vẽ SAU nên vẫn nét.
    if BG_BLUR:
        im = im.filter(ImageFilter.GaussianBlur(BG_BLUR))
    return im


def paste_alpha(base, img, box):
    base.paste(img, box, img if img.mode == "RGBA" else None)


# ─────────────────────────── THẺ ───────────────────────────
def draw_card(backdrop, fonts, kicker, title, sub, mate, accent):
    im = backdrop.copy()
    d = ImageDraw.Draw(im, "RGBA")

    # ── linh vật bên phải, có quầng sáng cho tách khỏi nền
    if mate:
        m = Image.open(os.path.join(MATE_DIR, mate)).convert("RGBA")
        side = 330
        m = m.resize((side, side), Image.LANCZOS)
        glow = Image.new("RGBA", (side + 120, side + 120), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse(
            (30, 30, side + 90, side + 90), fill=accent + (46,))
        glow = glow.filter(ImageFilter.GaussianBlur(38))
        paste_alpha(im, glow, (W - side - 130, (H - side) // 2 - 60))
        paste_alpha(im, m, (W - side - 70, (H - side) // 2))

    # ── logo thương hiệu
    logo = Image.open(LOGO).convert("RGBA")
    lw = 236
    logo = logo.resize((lw, round(lw * logo.height / logo.width)), Image.LANCZOS)
    paste_alpha(im, logo, (64, 56))

    # ── chip mã hiệu
    if kicker:
        f = fonts["kicker"]
        tw = d.textlength(kicker, font=f)
        x, y = 64, 168
        d.rounded_rectangle((x, y, x + tw + 40, y + 48), 24,
                            fill=accent + (38,), outline=accent + (150,), width=2)
        d.text((x + 20, y + 9), kicker, font=f, fill=accent)

    # ── tiêu đề: hạ cỡ chữ khi tên dài, KHÔNG cắt bớt chữ
    #    ⚠️ Cắt bớt tên game trên thẻ chia sẻ là đăng một cái tên không có thật.
    limit = W - 64 - 420
    f = fonts["title"]
    if not fits(d, title, f, limit):
        f = fonts["title_sm"]
    y = 244
    if fits(d, title, f, limit):
        lines = [title]
    else:
        words, lines, cur = title.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if fits(d, t, f, limit) or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    for ln in lines[:2]:
        d.text((64, y), ln, font=f, fill=WHITE)
        y += f.size + 12

    # ── dòng phụ
    if sub:
        d.text((64, y + 10), sub, font=fonts["sub"], fill=DIM)

    # ── vạch nhấn dưới cùng
    d.rectangle((0, H - 8, W, H), fill=accent)
    return im


# ─────────────────────────── DANH SÁCH ───────────────────────────
def games_from_source():
    """Đọc tên game từ chính `games.html` — gõ lại là hai nơi nói hai tên."""
    s = io.open(os.path.join(ROOT, "games.html"), encoding="utf-8").read()
    blk = re.search(r"var GAMES\s*=\s*\[(.*?)\n\s*\];", s, re.S).group(1)
    out = []
    for m in re.finditer(r"\{(.*?)\}\s*(?:,|$)", blk, re.S):
        b = m.group(1)
        key = re.search(r'key\s*:\s*"([^"]*)"', b)
        code = re.search(r'code\s*:\s*"([^"]*)"', b)
        file = re.search(r'file\s*:\s*"([^"]*)"', b)
        vi = re.search(r'name\s*:\s*\{\s*vi\s*:\s*"([^"]*)"', b)
        if key and file and vi:
            out.append({"key": key.group(1), "code": code.group(1) if code else "",
                        "file": file.group(1), "title": vi.group(1)})
    return out


def mate_map():
    s = io.open(os.path.join(ROOT, "js", "game-shell.js"), encoding="utf-8").read()
    blk = re.search(r"var MATE\s*=\s*\{(.*?)\};", s, re.S).group(1)
    return {k: v for k, v in re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', blk)}


PAGES_EXTRA = [
    {"slug": "mission-earth", "kicker": "MISSION_01", "title": "Hành Tinh Xanh",
     "sub": "7 chặng khám phá Trái Đất", "mate": "comet-cheer.png", "accent": CYAN},
    {"slug": "mission-orbit", "kicker": "MISSION_02", "title": "Mắt Thần Trên Quỹ Đạo",
     "sub": "5 chặng · đọc ảnh vệ tinh", "mate": "byte-cheer.png", "accent": CYAN},
    {"slug": "lab", "kicker": "MOD-05", "title": "Phòng Nghiên Cứu",
     "sub": "Thí nghiệm trọng lực & ánh sáng", "mate": "byte-idle.png", "accent": PURPLE},
    {"slug": "crew", "kicker": "C3", "title": "Phi Hành Đoàn Đầu Tiên",
     "sub": "500 chỗ ngồi cho phi hành gia mới", "mate": "comet-idle.png", "accent": SUN},
    {"slug": "games", "kicker": "MOD-02", "title": "Khu Huấn Luyện",
     "sub": "10 trò chơi rèn kỹ năng phi hành gia", "mate": "comet-cheer.png", "accent": SUN},
]


def build():
    check = "--check" in sys.argv
    games = games_from_source()
    mates = mate_map()
    if len(games) < 10:
        print(f"  [HONG] chi doc duoc {len(games)} game tu games.html")
        return 1

    font_path = build_font()
    fonts = load_fonts(font_path)
    backdrop = make_backdrop()

    jobs = []
    for g in games:
        stem = g["file"].replace(".html", "")
        kind = mates.get(stem, "comet")
        jobs.append({
            "slug": stem, "kicker": g["code"], "title": g["title"],
            "sub": "Khu Huấn Luyện · astroQ.org",
            "mate": f"{kind}-cheer.png",
            "accent": CYAN if kind == "byte" else SUN,
        })
    jobs += PAGES_EXTRA

    if not check:
        os.makedirs(OUT_DIR, exist_ok=True)

    total = 0
    print(f"{'tep':34} {'KB':>6}  tieu de")
    print("-" * 78)
    for j in jobs:
        im = draw_card(backdrop, fonts, j["kicker"], j["title"], j["sub"],
                       j["mate"], j["accent"])
        path = os.path.join(OUT_DIR, j["slug"] + ".jpg")
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
        data = buf.getvalue()
        total += len(data)
        if not check:
            io.open(path, "wb").write(data)
        print(f"{'img/og/' + j['slug'] + '.jpg':34} {len(data)//1024:6}  {j['title']}")

    print("-" * 78)
    print(f"  {len(jobs)} thẻ · tổng {total/1024:.0f} KB · trung bình {total/len(jobs)/1024:.0f} KB")
    if check:
        print("  (--check: không ghi tệp nào)")
    return 0


if __name__ == "__main__":
    sys.exit(build())
