# -*- coding: utf-8 -*-
r"""_patch_thumb.py — thêm trường `thumb` (ảnh NASA bản `~small`) vào 6 file bài
có ảnh, và khai nó vào `LIGHT`/`ORDER` của `scratchpad/split_articles.py`.

    python scratchpad/_patch_thumb.py

⚠️ VIẾT THÀNH FILE, KHÔNG QUA HEREDOC — heredoc ăn mất `\` trong regex.

⚠️⚠️ VÌ SAO — SỐ ĐO (25/08/2026, `scratchpad/_imgsize.py` + `_hero_size.py`):
   `library.html` kéo **1,3 MB** ảnh từ `images-assets.nasa.gov` để vẽ trong thẻ
   **219×130** (cần 438 px ở DPR2). Tỉ lệ dư 2,9×–6,7×. Bản `~small` (640 px) đủ cho
   438 px và tổng chỉ **229 KB** ⇒ **−83%**.
   ⚠️ ẢNH HERO THÌ GIỮ NGUYÊN `img`: thẻ lớn vẽ ở **598×210** (cần 1196 px ở DPR2),
      nên `~large` 1920 px là 1,6× — đúng mức. Hạ hero xuống 640 px là ảnh mờ.

⚠️⚠️ MỞ TỪNG URL RỒI MỚI VIẾT, KHÔNG SUY THEO MẪU. `js/articles-index.js` đã ghi
   cảnh báo *"⛔ đừng đoán đường dẫn ảnh NASA theo mẫu — `~large` KHÔNG tồn tại với
   mọi ảnh"*, và đo lại 25/08 thì đúng: `~medium`/`~large` trả **403** ở 3/6 ảnh.
   Riêng `~small` thì **6/6 trả 200**, đều **640 px bề rộng** — đã tải về đo bằng PIL,
   không đọc thẻ khai. Bộ đo giữ lại ở `scratchpad/probe_nasa_thumb.py`.

⚠️ `thumb` VÀO CẢ `LIGHT` (mục lục) LẪN `ORDER` (file bài). Mục lục là thứ `library.html`
   vẽ lưới thẻ; thiếu nó ở đó thì thẻ vẫn dùng `img` và cả lượt sửa này vô tác dụng.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# id bài → (URL đang dùng cho hero, URL `~small` cho thẻ lưới)
THUMB = {
    "lib-nebula":    "https://images-assets.nasa.gov/image/PIA25433/PIA25433~small.jpg",
    "lib-saturn":    "https://images-assets.nasa.gov/image/PIA22766/PIA22766~small.jpg",
    "lib-mars":      "https://images-assets.nasa.gov/image/PIA21496/PIA21496~small.jpg",
    "lib-andromeda": "https://images-assets.nasa.gov/image/PIA04921/PIA04921~small.jpg",
    "lib-exoplanet": "https://images-assets.nasa.gov/image/PIA22082/PIA22082~small.jpg",
    "lib-blackhole": "https://images-assets.nasa.gov/image/PIA23122/PIA23122~small.jpg",
}

NOTE = (
    "  /* Anh cho THE LUOI (219x130 => can 438px o DPR2). Ban `~small` la 640px.\n"
    "     ⚠️ `img` o tren GIU nguyen ban lon: the HERO ve o 598x210 (can 1196px).\n"
    "     ⚠️ URL da mo va kiem 200 ngay 25/08/2026 — dung doan `~small`/`~medium`\n"
    "        theo mau, `~medium` tra 403 o 3/6 anh nay. */\n"
)

n = 0
for aid, thumb in THUMB.items():
    p = os.path.join("js", "article", aid + ".js")
    s = io.open(p, encoding="utf-8", newline="").read()
    if "thumb:" in s:
        print("  = %s (da co thumb)" % p)
        continue
    m = re.search(r'^([ \t]*)img:\s*"[^"]+",[ \t]*\r?\n', s, re.M)
    assert m, "khong thay dong img: o " + p
    nl = "\r\n" if "\r\n" in s else "\n"
    block = NOTE.replace("\n", nl) + '  thumb: "%s",%s' % (thumb, nl)
    s = s[:m.end()] + block + s[m.end():]
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    n += 1
    print("  ghi %s" % p)

# ── split_articles.py: khai `thumb` vào cả hai danh sách ────────────────────
P = "scratchpad/split_articles.py"
sp = io.open(P, encoding="utf-8").read()
if '"thumb"' not in sp:
    A = 'LIGHT = ("ord", "id", "src", "cat", "em", "c", "img", "title")'
    B = ('# ⚠️ `thumb` (anh ban `~small` cho THE LUOI) PHAI o ca hai danh sach: muc luc\n'
         '#    la thu `library.html` ve luoi the, thieu no o do thi the van dung `img`\n'
         '#    va ca luot toi uu thanh vo tac dung. Ly do + so do: xem\n'
         '#    scratchpad/_patch_thumb.py.\n'
         'LIGHT = ("ord", "id", "src", "cat", "em", "c", "img", "thumb", "title")')
    assert A in sp, "khong thay LIGHT"
    sp = sp.replace(A, B, 1)

    A2 = 'ORDER = ("ord", "id", "src", "cat", "em", "c", "img", "credit", "url",'
    B2 = 'ORDER = ("ord", "id", "src", "cat", "em", "c", "img", "thumb", "credit", "url",'
    assert A2 in sp, "khong thay ORDER"
    sp = sp.replace(A2, B2, 1)
    io.open(P, "w", encoding="utf-8", newline="\n").write(sp)
    print("  ghi %s (LIGHT + ORDER)" % P)
else:
    print("  = %s (da co thumb)" % P)

print("\n%d file bai cap nhat. Chay tiep:" % n)
print("  python -m http.server 8123   (trong AstroQhtml/)")
print("  python scratchpad/split_articles.py   # sinh lai muc luc")
