# -*- coding: utf-8 -*-
r"""verify_prod_0825.py — ĐO TRÊN BẢN THẬT `astroq.org` sau lượt push 25/08/2026
(preload phông · ảnh NASA `~small` · service worker cache-trước).

    python scratchpad/verify_prod_0825.py

⚠️⚠️ KIỂM SỐ HIỆU BẢN DỰNG TRƯỚC MỌI THỨ KHÁC, VÀ DỪNG HẲN NẾU LỆCH. Pages build
   mất 1–2 phút; đo trước lúc đó thì mọi phép kiểm phía sau đang nói về **BẢN CŨ**
   và chúng sẽ "đạt" một cách RỖNG. Ngày 06/08/2026 bản thật đứng ở bản cũ gần một
   ngày — đúng loại tình huống mà một con số sai dẫn người đi sửa sai chỗ.

⚠️ MIME LÀ THỨ PHẢI ĐO, KHÔNG ĐƯỢC GIẢ ĐỊNH. Trình duyệt **từ chối** một service
   worker phục vụ dưới `text/plain`, và `import()` cũng từ chối module như thế.

⚠️ ĐO CẢ HAI TẦNG. Tầng mạng (200 + MIME) chỉ chứng minh file có mặt; nó KHÔNG
   chứng minh trang dùng đúng thứ đó. Nên mục [3] mở CHÍNH `astroq.org` trên
   Chromium rồi đọc lại từ DOM và từ Cache Storage.
"""
import io
import re
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SITE = "https://astroq.org"
WANT = "2026.08.25.1"
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


def get(path):
    req = urllib.request.Request(SITE + path)
    req.add_header("User-Agent", UA)
    req.add_header("Cache-Control", "no-cache")
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")


# ── [0] SỐ HIỆU BẢN DỰNG — chốt chặn, dừng hẳn nếu lệch ─────────────────────
print("=== [0] So hieu ban dung ===")
st, _, uic = get("/js/ui-common.js")
m = re.search(r'var VERSION = "([0-9.]+)"', uic)
got = m.group(1) if m else "?"
print("     ui-common.js: %s  (doi %s)" % (got, WANT))
if got != WANT:
    sys.exit("!! Pages CHUA dung xong ban moi — DUNG HAN. Cho roi chay lai.")
check("[0] ban that dang o dung so hieu vua push", True, got)

# ── [1] Service worker trên Pages ───────────────────────────────────────────
print("\n=== [1] sw.js tren Pages ===")
st, ct, sw = get("/sw.js")
check("[1] /sw.js tra 200", st == 200, str(st))
check("[1] MIME la javascript (trinh duyet TU CHOI text/plain)",
      "javascript" in ct.lower(), ct)
m2 = re.search(r'var VERSION = "([0-9.]+)"', sw)
check("[1] VERSION cua sw.js KHOP ui-common.js", bool(m2) and m2.group(1) == WANT,
      m2.group(1) if m2 else "?")
check("[1] ten cache mang so hieu ban dung",
      'var CACHE = "astroq-" + VERSION' in sw)
check("[1] co FAST (quyet dinh 5)", "var FAST = [" in sw)
check("[1] FAST phu fonts/ va vendor co VERSION trong duong",
      "/^\\/fonts\\//" in sw and "vendor" in sw)
check("[1] FAST KHONG phu css/ hay js/",
      "/^\\/css\\//" not in sw and "/^\\/js\\//" not in sw)
_h = sw[sw.find('addEventListener("fetch"'):]
check("[1] `fast(url)` dung SAU `skip(url)` trong handler",
      0 <= _h.find("skip(url)") < _h.find("fast(url)"),
      "skip@%d fast@%d" % (_h.find("skip(url)"), _h.find("fast(url)")))
check("[1] nhanh CHINH van mang-truoc (`fetch(req)`)",
      re.search(r"respondWith\(\s*fetch\(req\)", sw) is not None)

# ── [2] Khối preload theo từng trang ────────────────────────────────────────
print("\n=== [2] Khoi FONT-PRELOAD tren tung trang ===")
PAGES = {"/index.html": (5, ""), "/dashboard.html": (5, ""),
         "/explorer.html": (4, ""), "/landing-app.html": (4, ""),
         "/offline.html": (4, "/"), "/en/index.html": (5, "../"),
         "/library.html": (5, "")}
for path, (n, pref) in PAGES.items():
    st, _, html = get(path)
    links = re.findall(r'<link rel="preload" as="font"[^>]*href="([^"]+)"', html)
    check("[2] %-22s dung %d dong preload" % (path, n), len(links) == n,
          "%d dong" % len(links))
    check("[2] %-22s mono %s" % (path, "CO" if n == 5 else "KHONG"),
          any("share-tech-mono" in u for u in links) == (n == 5))
    if pref:
        check("[2] %-22s duong dan tien to %r" % (path, pref),
              all(u.startswith(pref + "fonts/") for u in links),
              str([u for u in links if not u.startswith(pref + "fonts/")])[:60])
    check("[2] %-22s moi dong co crossorigin" % path,
          html.count('rel="preload" as="font" type="font/woff2" crossorigin') == n)

# ── [3] Ảnh NASA bản nhỏ ở mục lục bài đọc ─────────────────────────────────
print("\n=== [3] Muc luc bai doc: truong `thumb` ===")
st, ct, idx = get("/js/articles-index.js")
check("[3] /js/articles-index.js tra 200", st == 200, str(st))
check("[3] MIME la javascript", "javascript" in ct.lower(), ct)
thumbs = re.findall(r'thumb: "([^"]+)"', idx)
check("[3] co 6 dong thumb", len(thumbs) == 6, "%d dong" % len(thumbs))
check("[3] moi thumb la ban ~small", all("~small" in t for t in thumbs),
      str([t for t in thumbs if "~small" not in t])[:70])
st, ct2, art = get("/js/article/lib-nebula.js")
check("[3] file bai tra 200 + MIME javascript",
      st == 200 and "javascript" in ct2.lower(), "%s %s" % (st, ct2))
check("[3] file bai mang ca `img` (hero) lan `thumb`",
      'img: "' in art and 'thumb: "' in art)

print("\n=== KET QUA (tang mang): %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(0 if bad_n == 0 else 1)
