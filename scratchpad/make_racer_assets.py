# -*- coding: utf-8 -*-
r"""Tách `img/asset.png` (5 vật trong một ảnh) thành 5 asset dùng được cho ARCADE-03.

Chủ dự án đặt art vào `img/asset.png` (1536×1024, ĐÃ có alpha thật). Bộ này:
  ① tách 5 vật bằng vùng liên thông trên kênh alpha (không có numpy/scipy trên
     máy này, nên dùng flood-fill hàng-đoạn tự viết);
  ② XÁC MINH danh tính từng vật bằng MÀU CHỦ ĐẠO, không chỉ theo vị trí;
  ③ cắt bbox → hạ cỡ LANCZOS → nén palette 256 màu.

⚠️⚠️ CHỐT TỈ LỆ (chủ dự án chốt 21/08): **chiều DÀI ba tàu đối thủ = chiều dài
   Luna** (`CONFIG.shipW` = 56 đơn vị ảo). Ba tàu mới dài 2,7–3,2 : 1 trong khi
   `luna-side.png` là 1,88 : 1, nên chuẩn hoá theo chiều dài thì chúng MỎNG hơn
   Luna (cao ~17–21 thay vì 30). Đường kia — chuẩn hoá theo chiều CAO — cho tàu
   cam dài 95 đơn vị ảo, tức to gần gấp đôi tàu của trẻ và bắt đầu che vật thể
   trên làn. Đã chốt đường thứ nhất.

⚠️ ĐỘ PHÂN GIẢI ĐÍCH ≈ 1,8× cỡ hiển thị LỚN NHẤT (đo trên Chromium: 1 đơn vị ảo
   = 2,45 pixel thật ở Full HD/DPR 2 ⇒ tàu 137 px · đá 142 px · thùng 49×78 px).
   Cùng khuôn `luna-side.png` (192×102 ≈ 1,4× của 137×74).

⚠️ NÉN BẰNG `quantize(FASTOCTREE)`, KHÔNG `convert("P", palette=ADAPTIVE)`:
   nhánh sau làm phẳng alpha thành trong-suốt-nhị-phân, chặt hết viền mềm quanh
   hình (bài học 30/07 khi làm `img/astroq-logo.png`).
"""
import io
import os
import sys
from collections import deque

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

SRC = os.path.join("img", "asset.png")
OUT = os.path.join("img", "racer")
A_MIN = 40            # alpha coi là "có hình"
MIN_AREA = 3000       # bỏ mảnh vụn (bụi alpha lẻ quanh hình)

# Đích: (tên file, cạnh chuẩn hoá, chuẩn theo chiều nào)
#   "w" = ép chiều RỘNG (ba tàu — chốt "dài bằng Luna")
#   "box" = ép cạnh dài nhất (đá, thùng)
TARGET = {
    "blaze": ("rival-blaze.png", 256, "w"),
    "ember": ("rival-ember.png", 256, "w"),
    "dust":  ("rival-dust.png",  256, "w"),
    "rock":  ("rock.png",        256, "box"),
    "can":   ("fuel-can.png",    224, "box"),
}

# Màu để XÁC MINH danh tính. Không tin thứ tự trên ảnh: gán sai thì tàu "Sao Băng"
# nhận hình vàng và cái dấu của nó trên dải đua lệch màu — một lỗi IM LẶNG.
# ⚠️ Đây là màu để NHẬN DẠNG (đo từ art), không phải màu của game. Mỗi tên có thể
#    khai nhiều màu (lấy khoảng cách NHỎ NHẤT) vì vỏ và ô phát sáng của thùng
#    nhiên liệu là hai tông lá rất khác nhau.
IDENT = {
    "blaze": [(255, 138, 92)],                  # cam  #FF8A5C
    "ember": [(255, 209, 102)],                 # vàng #FFD166
    "dust":  [(125, 211, 252)],                 # lam  #7DD3FC
    "rock":  [(130, 145, 176), (75, 85, 112)],  # xám  #8291B0 / #4B5570
    "can":   [(99, 230, 168), (16, 110, 40)],   # lá   #63E6A8 / vỏ đậm
}


def components(mask, w, h):
    """Vùng liên thông 4 hướng. Flood-fill theo ĐOẠN HÀNG để chịu được 1,5 triệu
       pixel bằng Python thuần (đẩy từng pixel vào deque thì chậm gấp nhiều lần)."""
    seen = bytearray(w * h)
    out = []
    for y0 in range(h):
        base = y0 * w
        for x0 in range(w):
            if not mask[base + x0] or seen[base + x0]:
                continue
            q = deque([(x0, y0)])
            seen[base + x0] = 1
            px = []
            while q:
                x, y = q.popleft()
                r = y * w
                lo = x
                while lo > 0 and mask[r + lo - 1] and not seen[r + lo - 1]:
                    lo -= 1
                    seen[r + lo] = 1
                hi = x
                while hi + 1 < w and mask[r + hi + 1] and not seen[r + hi + 1]:
                    hi += 1
                    seen[r + hi] = 1
                for xx in range(lo, hi + 1):
                    px.append((xx, y))
                    for ny in (y - 1, y + 1):
                        if 0 <= ny < h:
                            i = ny * w + xx
                            if mask[i] and not seen[i]:
                                seen[i] = 1
                                q.append((xx, ny))
            if len(px) >= MIN_AREA:
                xs = [p[0] for p in px]
                ys = [p[1] for p in px]
                out.append({"n": len(px), "box": (min(xs), min(ys),
                                                  max(xs) + 1, max(ys) + 1)})
    return out


def dominant(im):
    """Màu chủ đạo BỎ QUA trắng/navy: cả 5 vật đều có mảng trắng và viền navy
       đậm, nên chúng không phân biệt được gì — thứ phân biệt là màu vỏ."""
    small = im.convert("RGBA").resize((64, 64), Image.LANCZOS)
    tally = {}
    for r, g, b, a in small.getdata():
        if a < 200:
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        if mx > 225 and mx - mn < 30:      # trắng
            continue
        if mx < 90:                        # navy/đen
            continue
        key = (r // 24, g // 24, b // 24)
        t = tally.setdefault(key, [0, 0, 0, 0])
        t[0] += r; t[1] += g; t[2] += b; t[3] += 1
    if not tally:
        return (0, 0, 0)
    k = max(tally, key=lambda k: tally[k][3])
    t = tally[k]
    return (t[0] // t[3], t[1] // t[3], t[2] // t[3])


def d2(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3))


im = Image.open(SRC).convert("RGBA")
W, H = im.size
alpha = im.getchannel("A").tobytes()
mask = bytearray(1 if v >= A_MIN else 0 for v in alpha)
print("=== %s  %d×%d ===" % (SRC, W, H))

comps = sorted(components(mask, W, H), key=lambda c: -c["n"])
print("  vung lien thong (>=%d px): %d" % (MIN_AREA, len(comps)))
assert len(comps) >= 5, "chi tach duoc %d vat — kiem lai alpha/A_MIN" % len(comps)
comps = comps[:5]

# ⚠️⚠️ GÁN DANH TÍNH BẰNG PHÉP HOÁN VỊ TỐI ƯU TOÀN CỤC, KHÔNG GÁN THAM LAM.
#    Bản đầu duyệt tên theo bảng chữ cái rồi cho mỗi tên chọn vùng gần màu nhất
#    còn lại — và nó gán SAI 3/5: `can` (xét thứ hai) vớ lấy TÀU LAM vì lệch
#    9.021 < 49.945 của thùng lá, kéo theo `dust` nhận ĐÁ và `rock` nhận THÙNG.
#    Không có phép xác minh màu thì cả ba lỗi đó đi thẳng vào game trong im lặng.
#    5 vật ⇒ 120 hoán vị, thử hết là xong.
import itertools  # noqa: E402

pairs = []
for c in comps:
    crop = im.crop(c["box"])
    pairs.append((c, crop, dominant(crop)))

NAMES = ("blaze", "ember", "dust", "rock", "can")


def cost(dom, name):
    return min(d2(dom, ref) for ref in IDENT[name])


best_perm, best_sum = None, None
for perm in itertools.permutations(NAMES):
    s = sum(cost(pairs[i][2], perm[i]) for i in range(5))
    if best_sum is None or s < best_sum:
        best_sum, best_perm = s, perm

named = {}
for i, name in enumerate(best_perm):
    c, crop, dom = pairs[i]
    named[name] = (cost(dom, name), c, crop, dom)
    print("  %-6s <- vung %4dx%-4d  mau chu dao #%02x%02x%02x  lech %d"
          % (name, c["box"][2] - c["box"][0], c["box"][3] - c["box"][1],
             dom[0], dom[1], dom[2], named[name][0]))
print("  tong lech cua hoan vi tot nhat: %d" % best_sum)

assert len(named) == 5, "gan danh tinh khong du 5"
# Hàng rào: một cặp lệch quá xa nghĩa là art đổi màu hoặc thứ tự vật đổi — dừng
# lại để người sửa xem, đừng lặng lẽ xuất 5 file gán sai tên.
for name in NAMES:
    assert named[name][0] < 30000, \
        "%s lech mau %d — kiem lai IDENT/art" % (name, named[name][0])

os.makedirs(OUT, exist_ok=True)
print("\n=== xuat ===")
tot = 0
for name in ("blaze", "ember", "dust", "rock", "can"):
    _, c, crop, _ = named[name]
    fn, side, how = TARGET[name]
    w0, h0 = crop.size
    ar = w0 / float(h0)
    if how == "w":
        tw, th = side, max(1, int(round(side / ar)))
    else:
        tw, th = (side, max(1, int(round(side / ar)))) if ar >= 1 \
            else (max(1, int(round(side * ar))), side)
    sm = crop.resize((tw, th), Image.LANCZOS)
    q = sm.quantize(colors=256, method=Image.FASTOCTREE)
    p = os.path.join(OUT, fn)
    q.save(p, optimize=True)
    n = os.path.getsize(p)
    tot += n
    # Đo lại alpha sau khi nén: >2 mức nghĩa là viền mềm còn sống.
    lv = len(set(q.convert("RGBA").getchannel("A").getdata()))
    print("  %-16s %4dx%-4d  ti le %.2f:1  %6.1f KB  %3d muc alpha"
          % (fn, tw, th, ar, n / 1024.0, lv))
    assert lv > 2, "%s bi lam phang alpha (con %d muc)" % (fn, lv)

print("\n  tong %.1f KB  (goc %.1f KB)" % (tot / 1024.0,
                                           os.path.getsize(SRC) / 1024.0))
print("  -> %s" % OUT)
