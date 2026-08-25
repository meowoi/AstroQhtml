# -*- coding: utf-8 -*-
r"""Vá `scratchpad/gen_home_en.py`: thêm `fonts/` vào phép lùi một cấp + phép kiểm.

⚠️ VIẾT THÀNH FILE, KHÔNG QUA HEREDOC — heredoc ăn mất `\` trong regex.
    python scratchpad/_patch_genen_fonts.py
"""
import io
import sys

P = "scratchpad/gen_home_en.py"
s = io.open(P, encoding="utf-8").read()

if "css/|js/|img/|fonts/" in s:
    sys.exit("gen_home_en.py da co fonts/ — khong va lai")

# ── 1. Phép thay đường dẫn tài nguyên ───────────────────────────────────────
A1 = r"""    h = re.sub(r'(\b(?:href|src|srcset)=")(css/|js/|img/)', r"\g<1>../\g<2>", h)"""
B1 = r"""    # ⚠️⚠️ `fonts/` THÊM 25/08/2026 — LẶP LẠI ĐÚNG LỖI `srcset` Ở TRÊN. Khối
    #    `rel="preload" as="font"` (xem scratchpad/sync_font_preload.py) mang
    #    `href="fonts/…"`; thiếu `fonts/` ở đây thì bản EN trỏ `/en/fonts/*.woff2`
    #    → **404 cả 5 phông**. Và nó hỏng IM LẶNG y như lần trước: preload 404 thì
    #    trình duyệt vẫn tải phông theo đường CSS bình thường, nên **chữ vẫn đúng
    #    phông** — chỉ mất toàn bộ tác dụng của preload, cộng 5 lượt 404. Phép kiểm
    #    cũ ở `build_en` chỉ đếm `css/|js/|img/` nên nó MÙ với chuyện này.
    h = re.sub(r'(\b(?:href|src|srcset)=")(css/|js/|img/|fonts/)', r"\g<1>../\g<2>", h)"""
assert A1 in s, "khong thay phep thay duong dan tai nguyen"
s = s.replace(A1, B1, 1)

# ── 2. Phép kiểm: nới cả hai vế cho `fonts/` ─────────────────────────────────
A2 = '''    check("../css/" in out and "../js/" in out and "../img/" in out, "duong dan tai nguyen da lui mot cap")
    leftover = re.findall(r'\\b(?:href|src|srcset)="(?:css/|js/|img/)[^"]*"', out)'''
B2 = '''    check("../css/" in out and "../js/" in out and "../img/" in out
          and "../fonts/" in out, "duong dan tai nguyen da lui mot cap")
    leftover = re.findall(r'\\b(?:href|src|srcset)="(?:css/|js/|img/|fonts/)[^"]*"', out)'''
assert A2 in s, "khong thay phep kiem duong dan tai nguyen"
s = s.replace(A2, B2, 1)

# ── 3. Phép kiểm mới: đủ 5 dòng preload và tất cả đều lùi một cấp ────────────
A3 = '''    check("../wiki/en/" in out, "link wiki tro sang ban tieng Anh")'''
B3 = '''    check("../wiki/en/" in out, "link wiki tro sang ban tieng Anh")
    # ⚠️ Dem DUNG so dong preload, khong chi hoi "co fonts/ khong": mot dong lot
    #    ra ngoai la mot phong 404 ma trang van trong nhu binh thuong.
    pre = re.findall(r'<link rel="preload" as="font"[^>]*href="([^"]+)"', out)
    check(len(pre) == 5, "ban EN co dung 5 dong preload phong", str(len(pre)))
    check(all(u.startswith("../fonts/") for u in pre),
          "moi dong preload deu tro ../fonts/",
          str([u for u in pre if not u.startswith("../fonts/")]))'''
assert A3 in s, "khong thay diem chen phep kiem moi"
s = s.replace(A3, B3, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("gen_home_en.py: da them fonts/ vao phep thay + 2 phep kiem moi")
