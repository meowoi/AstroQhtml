# -*- coding: utf-8 -*-
r"""sync_font_preload.py — CHÈN/CẬP NHẬT khối `rel="preload"` cho 5 phông tự host
vào MỌI trang có nạp `css/fonts.css`. ⚠️ ĐỪNG SỬA TAY khối giữa hai mốc
`<!-- FONT-PRELOAD:BEGIN -->` … `<!-- FONT-PRELOAD:END -->` — lần chạy sau mất.

    python scratchpad/sync_font_preload.py            # ghi
    python scratchpad/sync_font_preload.py --xem      # chỉ in, không ghi

⚠️⚠️ VÌ SAO CẦN — SỐ ĐO, KHÔNG PHẢI PHỎNG ĐOÁN (đo 25/08/2026, 4G RTT 150ms +
   CPU ×4, `scratchpad/_font_chain.py`):
     · `index.html`     FCP 1.852 ms → phông bắt đầu tải **1.539 ms**, xong 2.479 ms
     · `dashboard.html` FCP 3.728 ms → phông bắt đầu tải **3.475 ms**, xong **4.783 ms**
   Tức `inter-vietnamese.woff2` về **hơn một giây SAU lần vẽ đầu**. `font-display:swap`
   nghĩa là chữ Việt được vẽ bằng phông dự phòng rồi mới đổi ⇒ **chữ nhảy trước mắt
   trẻ**, mỗi lượt vào.
   Nguyên nhân: `css/fonts.css` xong ở ~750 ms, nhưng phông chỉ được YÊU CẦU khi bố
   cục thật sự cần một glyph — tức sau khi parse xong đám script chặn parser. Chuỗi
   phát hiện là **HTML → fonts.css → woff2**, ba chặng nối đuôi.

⚠️⚠️ PRELOAD **KHÔNG THÊM MỘT BYTE NÀO** — đây là chỗ dễ tưởng là đánh đổi mà không
   phải. `preload` bỏ qua `unicode-range`, nên nó tải vô điều kiện; nhưng đo trên
   Chromium (`scratchpad/_font_usage.py`, 37 trang × 2 ngôn ngữ) thì **cả 5 file DÙ SAO
   CŨNG ĐƯỢC TẢI**:
     · `inter-latin` · `inter-vietnamese` · `space-grotesk-latin`
       · `space-grotesk-vietnamese` → **37/37 trang**
     · `share-tech-mono-latin` → **35/37 trang**
   ⇒ Preload chỉ DỊCH chúng lên song song với CSS, không thêm lượt tải nào.

⚠️⚠️ BA TRANG **KHÔNG** PRELOAD SHARE TECH MONO — `explorer.html` ·
   `landing-app.html` · `offline.html` (`NO_MONO`). Đo được bằng
   `scratchpad/probe_font_mono.py` (render 38 trang × 2 ngôn ngữ, đếm phần tử THẬT SỰ
   vẽ chữ bằng phông đó): chúng là **3/38 trang có 0 phần tử**, tức preload ở đó là
   13,5 KB thuần thừa. Nhưng cái giá KHÔNG phải byte mà là **FCP** — A/B trên cùng mã nguồn
   (`_font_ab.py`, 4G RTT150 + CPU ×4, trung vị 3 lượt, đo *"thời điểm chữ ĐÚNG PHÔNG
   hiện xong"*):

     trang              không preload   preload 4 phông   preload cả 5
     landing-app.html        1.913 ms      **1.624 ms**       1.932 ms
     explorer.html           2.256 ms      **2.116 ms**       2.280 ms
     dashboard.html          4.380 ms        4.259 ms       **4.152 ms**
     index.html              2.306 ms      **1.831 ms**       2.020 ms

   ⇒ ở hai trang đó, preload cả 5 còn **TỆ HƠN không preload gì** (+19 / +24 ms),
   trong khi bỏ mono ra thì lợi **289 / 140 ms**. Ở dashboard thì ngược lại: bỏ mono
   là còn một cú đổi phông sau FCP (+171 ms), nên nó GIỮ cả 5.

⚠️ **CÁI GIÁ CỦA DANH SÁCH RIÊNG, và vì sao chấp nhận được.** Danh sách preload khác
   nhau theo trang thì phụ thuộc **nội dung** — một trang bắt đầu dùng nhãn mono là
   `NO_MONO` nói sai. Nhưng nó **canh được**: `scratchpad/probe_font_mono.py` đọc
   `NO_MONO` thẳng từ đây rồi đối chiếu với phép đo render, và báo hỏng theo **cả hai
   chiều** — chạy lại nó sau mỗi đợt sửa nội dung hoặc sửa `--font-mono` ở CSS.
   ⚠️ `_font_usage.py` KHÔNG canh được việc này nữa (nó đếm file tải về, mà preload
      bỏ qua `unicode-range` nên trang nào cũng tải đủ 5) — lý do đầy đủ ở đầu
      `probe_font_mono.py`.
   Và **hai chiều lệch đều HỎNG MỀM**: trang trong `NO_MONO` mà lại dùng mono ⇒ nhãn
   HUD đổi phông muộn một lần; trang ngoài `NO_MONO` mà thôi dùng ⇒ tải thừa 13,5 KB.
   Không ca nào làm vỡ trang.

⚠️ `crossorigin` LÀ BẮT BUỘC, kể cả cùng origin. Lượt tải phông luôn ở chế độ CORS;
   preload không mang cờ đó thì trình duyệt coi là một lượt KHÁC và **tải lại lần
   hai** — tức làm chậm đi đúng thứ đang đi sửa.

⚠️ ĐƯỜNG DẪN SUY TỪ CHÍNH THẺ `fonts.css` CỦA TỪNG TRANG, không gõ cứng `fonts/`.
   Ba dạng đang tồn tại: `css/fonts.css` (trang gốc) · `../css/fonts.css` (`en/`,
   `wiki/`) · `/css/fonts.css` (`offline.html` — service worker trả trang đó mà KHÔNG
   đổi URL, nên mọi đường dẫn ở đó phải TUYỆT ĐỐI; xem `check_pages` mục [37]).

⚠️ ĐẶT KHỐI NGAY TRƯỚC THẺ `fonts.css`. Preload càng sớm càng tốt, và đứng cạnh
   chính cái stylesheet khai `@font-face` thì người đọc sau thấy ngay hai thứ đi đôi.

⚠️ `wiki/` CŨNG ĐƯỢC CHÈN. Mục 2 của CLAUDE.md ghi *"đừng sửa tay wiki, phải sửa
   generator"* — nhưng `scratchpad/gen_wiki_data*.py` **không còn trên máy từ
   27/07/2026**, nên sửa tay là đường duy nhất và đã có tiền lệ (đợt đổi 90 link
   `href="/"`, đợt bỏ mệnh đề ngày mở cửa). ⚠️ Khôi phục generator thì phải mang khối
   này vào template TRƯỚC khi sinh lại.
"""
import glob
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

BEGIN = "<!-- FONT-PRELOAD:BEGIN -->"
END = "<!-- FONT-PRELOAD:END -->"

# ⚠️ THỨ TỰ CÓ Ý NGHĨA: phông THÂN BÀI trước (chữ nhiều nhất, nhảy chữ dễ thấy
#    nhất), rồi phông TIÊU ĐỀ, cuối cùng là mono của nhãn HUD.
FONTS = [
    "inter-vietnamese.woff2",
    "inter-latin.woff2",
    "space-grotesk-vietnamese.woff2",
    "space-grotesk-latin.woff2",
    "share-tech-mono-latin.woff2",   # <- rieng font nay co the bi loai, xem NO_MONO
]

# ⚠️⚠️ BA TRANG KHÔNG PRELOAD MONO — danh sách ĐO ĐƯỢC, không suy từ CSS.
#    `--font-mono` được KHAI ở 8 file CSS, nhưng KHAI không có nghĩa là DÙNG.
#    `scratchpad/probe_font_mono.py` render cả 38 trang × 2 ngôn ngữ rồi đếm phần tử
#    THẬT SỰ vẽ chữ bằng Share Tech Mono: **đúng 3/38 trang có 0 phần tử**.
#    ⚠️ ĐỪNG dùng `_font_usage.py` để canh danh sách này — nó đếm file .woff2 TẢI VỀ,
#       mà `preload` bỏ qua `unicode-range` nên nay trang nào cũng tải đủ 5; tức nó chỉ
#       còn đo được CHÍNH cái preload của mình. Đo `fontFamily` mới độc lập.
#    Số đo FCP + hai chiều hỏng mềm: xem đầu script.
#    ⚠️ GÕ SAI TÊN Ở ĐÂY LÀ MỘT LỖI IM LẶNG (nó chỉ đơn giản không khớp trang nào,
#       đọc ra y như "đã loại mono thành công") — hàng rào cuối script báo ngay ca đó.
NO_MONO = {"explorer.html", "landing-app.html", "offline.html"}


def fonts_for(page):
    """Danh sách phông preload của MỘT trang."""
    if page.replace("\\", "/") in NO_MONO:
        return [f for f in FONTS if "share-tech-mono" not in f]
    return FONTS

NOTE = (
    "<!-- ĐỪNG SỬA TAY khối này — sinh bởi `python scratchpad/sync_font_preload.py`.\n"
    "     Vì sao preload (kèm số đo) + vì sao BẮT BUỘC có `crossorigin`: xem đầu script đó. -->"
)

LINK_RE = re.compile(
    r'[ \t]*<link[^>]+rel="stylesheet"[^>]+href="([^"]*?)css/fonts\.css"[^>]*>[ \t]*\r?\n?'
)
BLOCK_RE = re.compile(
    re.escape(BEGIN) + r".*?" + re.escape(END) + r"[ \t]*\r?\n?", re.S
)


def build(prefix, nl, fonts):
    """prefix = phần đứng trước `css/` ở chính trang đó ('', '../', '/')."""
    lines = [BEGIN, NOTE]
    for f in fonts:
        lines.append(
            '<link rel="preload" as="font" type="font/woff2" crossorigin '
            'href="%sfonts/%s" />' % (prefix, f)
        )
    lines.append(END)
    return nl.join(lines) + nl


def main():
    xem = "--xem" in sys.argv
    pages = sorted(
        glob.glob("*.html") + glob.glob("en/*.html") + glob.glob("wiki/*.html")
        + glob.glob("wiki/en/*.html")
    )
    done = skip = 0
    for p in pages:
        raw = io.open(p, encoding="utf-8", newline="").read()
        m = LINK_RE.search(raw)
        if not m:
            skip += 1
            continue
        # Giữ đúng ký tự xuống dòng của FILE — nhiều file dùng CRLF; ghi lẫn LF vào
        # là git báo cả file đổi và mọi phép so chuỗi sau này đều lệch.
        nl = "\r\n" if "\r\n" in raw else "\n"
        prefix = m.group(1)
        fonts = fonts_for(p)
        block = build(prefix, nl, fonts)

        out = BLOCK_RE.sub("", raw)          # bỏ khối cũ (nếu có) → idempotent
        m2 = LINK_RE.search(out)
        assert m2, p
        out = out[: m2.start()] + block + out[m2.start():]

        if out == raw:
            print("  = %s (đã đúng)" % p)
            continue
        if not xem:
            io.open(p, "w", encoding="utf-8", newline="").write(out)
        done += 1
        print("  %s %-28s prefix=%-6r nl=%-4s %d phong%s" % (
            "[xem]" if xem else "ghi", p, prefix,
            "CRLF" if nl == "\r\n" else "LF", len(fonts),
            "  (bo mono)" if len(fonts) != len(FONTS) else ""))

    print("\n%d trang cập nhật · %d trang không nạp fonts.css (bỏ qua)" % (done, skip))
    if not xem:
        # Hàng rào: mọi trang có fonts.css phải có ĐÚNG MỘT khối, và 5 dòng preload.
        bad = []
        seen = set()
        for p in pages:
            s = io.open(p, encoding="utf-8").read()
            if "css/fonts.css" not in s:
                continue
            seen.add(p.replace("\\", "/"))
            want = fonts_for(p)
            block = s.split(BEGIN, 1)[1].split(END, 1)[0] if BEGIN in s and END in s else ""
            if s.count(BEGIN) != 1 or s.count(END) != 1:
                bad.append((p, "khối không phải đúng 1"))
            elif s.count('rel="preload" as="font"') != len(want):
                bad.append((p, "không đủ %d dòng preload" % len(want)))
            elif ("share-tech-mono" in block) != (len(want) == len(FONTS)):
                bad.append((p, "dòng mono lệch với NO_MONO"))
        # ⚠️ Gõ nhầm tên trong NO_MONO thì KHÔNG có phép kiểm nào ở trên báo — nó chỉ
        #    đơn giản không khớp trang nào, và đọc ra y như "đã loại mono thành công".
        for q in sorted(NO_MONO - seen):
            bad.append((q, "có trong NO_MONO nhưng KHÔNG là trang nạp fonts.css"))
        if bad:
            for p, why in bad:
                print("  [HONG] %s — %s" % (p, why))
            sys.exit("hàng rào KHÔNG đạt — đọc lại script")
        print("hàng rào: %d trang đúng 1 khối · %d trang đủ %d dòng · %d trang bỏ mono."
              % (len(seen), len(seen) - len(NO_MONO), len(FONTS), len(NO_MONO)))


if __name__ == "__main__":
    main()
