# -*- coding: utf-8 -*-
r"""verify_prod_0826.py — ĐO TRÊN BẢN THẬT `astroq.org` sau lượt push 26/08/2026
(dàn nhãn explorer · khung xương chống nhảy bố cục · ảnh landing-app · defer dashboard).

    python scratchpad/verify_prod_0826.py

⚠️⚠️ KIỂM SỐ HIỆU BẢN DỰNG TRƯỚC MỌI THỨ KHÁC, VÀ DỪNG HẲN NẾU LỆCH. Pages build
   mất 1–2 phút; đo trước lúc đó thì mọi phép kiểm phía sau đang nói về **BẢN CŨ**
   và chúng sẽ "đạt" một cách RỖNG. Ngày 06/08/2026 bản thật đứng ở bản cũ gần một
   ngày — đúng loại tình huống mà một con số sai dẫn người đi sửa sai chỗ.

⚠️ TẦNG MẠNG CHỈ CHỨNG MINH FILE CÓ MẶT, KHÔNG chứng minh trang dùng đúng thứ đó.
   Bộ này là tầng mạng; tầng trình duyệt ở `verify_prod_0826_ui.py`.

⚠️ MIME LÀ THỨ PHẢI ĐO, KHÔNG ĐƯỢC GIẢ ĐỊNH — trình duyệt **từ chối** một service
   worker phục vụ dưới `text/plain`, và `<source type="image/avif">` mà server trả
   sai kiểu thì `<picture>` sẽ lặng lẽ rơi về PNG, tức mất trọn phần vừa cắt được
   mà không có lỗi nào.
"""
import re
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SITE = "https://astroq.org"
WANT = "2026.08.26.1"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))


def get(path, binary=False):
    req = urllib.request.Request(SITE + path)
    req.add_header("User-Agent", UA)
    req.add_header("Cache-Control", "no-cache")
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
        return (r.status, r.headers.get("Content-Type", ""),
                raw if binary else raw.decode("utf-8", "replace"))


# ── [0] SỐ HIỆU BẢN DỰNG — chốt chặn ────────────────────────────────────────
print("=== [0] So hieu ban dung ===")
st, _, uic = get("/js/ui-common.js")
m = re.search(r'var VERSION = "([0-9.]+)"', uic)
got = m.group(1) if m else "?"
print("     ui-common.js: %s  (doi %s)" % (got, WANT))
if got != WANT:
    sys.exit("!! Pages CHUA dung xong ban moi — DUNG HAN. Cho roi chay lai.")
check("[0] ban that dang o dung so hieu vua push", True, got)

st, ct, sw = get("/sw.js")
check("[0] /sw.js tra 200 + MIME javascript",
      st == 200 and "javascript" in ct.lower(), "%s %s" % (st, ct))
m2 = re.search(r'var VERSION = "([0-9.]+)"', sw)
check("[0] VERSION cua sw.js KHOP ui-common.js",
      bool(m2) and m2.group(1) == WANT, m2.group(1) if m2 else "?")

# ── [1] Dàn nhãn ở explorer ─────────────────────────────────────────────────
print("\n=== [1] explorer: lop dan nhan ===")
_, _, exp = get("/explorer.html")
check("[1] co ham _declutterLabels", "_declutterLabels()" in exp)
check("[1] duoc goi trong vong ve, NGAY SAU labelRenderer.render",
      re.search(r"labelRenderer\.render\(this\.scene, this\.camera\);\s*\n\s*"
                r"this\._declutterLabels\(\);", exp) is not None)
check("[1] day bang marginTop (KHONG bang transform — CSS2DRenderer ghi de)",
      "el.style.marginTop" in exp and "el.style.transform" not in exp)
check("[1] xen ke len/xuong (khong chi day len)", "dy=(k%2)?-step:step" in exp)

# ── [2] Khung xương chống nhảy bố cục ───────────────────────────────────────
print("\n=== [2] Khung xuong chong nhay bo cuc ===")
_, _, ach = get("/css/achievements.css")
check("[2] achievements: .ranks co --rk-n va min-height tinh tu no",
      "--rk-n:10" in ach.replace(" ", "")
      and "min-height:calc(var(--rk-n)" in ach.replace(" ", ""))
check("[2] achievements: .groups co 3 muc theo media query",
      ach.count("--gc-h") >= 1 and ach.count("@media (max-width:940px)") == 1
      and ach.count("@media (max-width:500px)") == 1)

_, _, libc = get("/css/library.css")
check("[2] library: #cats min-height tinh tu --cat-n",
      "--cat-n:10" in libc.replace(" ", "")
      and "min-height:calc(var(--cat-n)" in libc.replace(" ", ""))
# ⚠️ REGEX, KHONG SO CHUOI SAU `replace(" ","")`: bo dau cach van con dau `;`
#    cuoi khai bao, va lan dau viet o day toi so chuoi khong co `;` nen phep kiem
#    BAO HONG OAN trong khi san pham dung. Cung ho voi loi `.lang-waitmain` da ghi
#    o `check_pages` muc [40] — CSS khong phai chuoi de so bang `in`.
check("[2] library: #feat-lead dat truoc 8 dong bang em",
      re.search(r"#feat-lead\s*\{[^}]*min-height\s*:\s*calc\(\s*8\s*\*\s*1\.55em\s*\)",
                libc) is not None)
check("[2] library: #hero-wrap co SAN, va co loi thoat .is-empty",
      "--feat-min:370px" in libc.replace(" ", "")
      and re.search(r"#hero-wrap\.is-empty\s*\{\s*min-height\s*:\s*0", libc) is not None)

_, _, libh = get("/library.html")
check("[2] library.html: renderFeatured gan/go lop is-empty",
      'box.classList.add("is-empty")' in libh
      and 'box.classList.remove("is-empty")' in libh)

_, _, misc = get("/css/missions.css")
check("[2] missions: #daily va #ov co san",
      re.search(r"#daily\s*\{[^}]*min-height\s*:\s*54px", misc) is not None
      and re.search(r"#ov\s*\{[^}]*min-height\s*:\s*58px", misc) is not None)

# ── [3] index: đồng hồ mặc định là ĐÃ MỞ CỬA ───────────────────────────────
print("\n=== [3] index: mac dinh #countdown ===")
for path in ("/index.html", "/en/index.html"):
    _, _, ix = get(path)
    check("[3] %-16s #countdown mac dinh co class live" % path,
          'class="countdown live"' in ix)
    check("[3] %-16s cd-label dung khoa cd_live" % path,
          'id="cd-label" data-i18n="cd_live"' in ix)
    check("[3] %-16s nut 'Vao choi ngay' KHONG con hidden" % path,
          re.search(r'id="hero-live"[^>]*\shidden', ix) is None)
_, _, ijs = get("/js/index.js")
check("[3] js/index.js co closeDoor() cho chieu nguoc lai",
      "function closeDoor()" in ijs and "closeDoor();" in ijs)

# ── [4] landing-app: ảnh ────────────────────────────────────────────────────
print("\n=== [4] landing-app: anh ===")
_, _, la = get("/landing-app.html")
n_lazy = la.count('<img loading="lazy" src="img/')
check("[4] du 9 anh trang tri mang loading=lazy", n_lazy == 9, "%d anh" % n_lazy)
n_avif = la.count('type="image/avif"')
n_webp = la.count('type="image/webp"')
check("[4] du 9 <source> AVIF va 9 <source> WebP",
      n_avif == 9 and n_webp == 9, "avif=%d webp=%d" % (n_avif, n_webp))
_, _, lac = get("/css/landing-app.css")
check("[4] CSS khai `picture` la block",
      re.search(r"\.floaty\s+picture\s*,\s*\.ic\s+picture\s*\{[^}]*display\s*:\s*block",
                lac) is not None)

ASSETS = [("img/raica1-480.avif", "avif"), ("img/raica1-480.webp", "webp"),
          ("img/3qok-384.avif", "avif"), ("img/b1-336.webp", "webp"),
          ("img/m1-248.avif", "avif")]
tot = 0
for path, kind in ASSETS:
    stt, ctt, raw = get("/" + path, binary=True)
    tot += len(raw)
    check("[4] %-22s 200 + MIME image/%s" % (path, kind),
          stt == 200 and kind in ctt.lower(), "%s %s %d B" % (stt, ctt, len(raw)))
print("     (5 asset mau: %.1f KB)" % (tot / 1024.0))

# ── [5] dashboard: defer + lang-wait ────────────────────────────────────────
print("\n=== [5] dashboard: defer + lang-wait ===")
_, _, dash = get("/dashboard.html")
tags = re.findall(r"<script\b([^>]*\bsrc=\"[^\"]+\"[^>]*)>", dash)
eager = [re.search(r'src="([^"]+)"', t).group(1) for t in tags
         if 'type="module"' not in t and " defer" not in t and " async" not in t]
deferred = [t for t in tags if " defer" in t and 'type="module"' not in t]
check("[5] dung 2 script co dien chay som, va la ui-common + cosmetics",
      eager == ["js/ui-common.js", "js/cosmetics.js"], str(eager))
check("[5] >= 15 thu vien mang defer", len(deferred) >= 15, "%d file" % len(deferred))
check("[5] khoi noi tuyen boc trong DOMContentLoaded",
      'document.addEventListener("DOMContentLoaded", function(){' in dash
      and "})();\n});" in dash)
check("[5] lang-wait: dat lop khi astroq-lang la 'en'",
      'localStorage.getItem("astroq-lang") === "en"' in dash
      and 'classList.add("lang-wait")' in dash)
check("[5] lang-wait: co duong cuu setTimeout (chong trang trang)",
      re.search(r'setTimeout\(function\(\)\{\s*r\.classList\.remove\("lang-wait"\)', dash)
      is not None)
check("[5] lang-wait: bo lop sau applyLang(LANG)",
      'classList.remove("lang-wait")' in dash)
_, _, dcss = get("/css/dashboard.css")
check("[5] lang-wait: CSS che `main` bang visibility",
      re.search(r"\.lang-wait\s+main\s*\{[^}]*visibility\s*:\s*hidden", dcss) is not None)
check("[5] lang-wait: KHONG dung display:none",
      re.search(r"\.lang-wait\s+main\s*\{[^}]*display\s*:\s*none", dcss) is None)

print("\n=== KET QUA (tang mang): %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(0 if bad_n == 0 else 1)
