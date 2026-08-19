# -*- coding: utf-8 -*-
"""check_wiki.py — GÁC 22 TRANG WIKI: nói đúng sự thật, và không mục liên kết.

⚠️⚠️ VÌ SAO BỘ NÀY TỒN TẠI (19/08/2026). Bộ `wiki/` sinh ra 27/07/2026 rồi **không ai
   soi lại 23 ngày**, vì `gen_wiki_data*.py` đã mất nên không còn generator nào assert
   gì cả. Chủ dự án hỏi *"kiểm tra nội dung wiki có cần update không?"* và đo ra ba
   chỗ sai — trong đó có một lời hứa hệ thống không giữ và một ngày đã qua nằm trên
   **cả 22 trang được lập chỉ mục**. Bộ này là hàng rào để chuyện đó không lặp lại.

⚠️ ĐÂY LÀ TRANG SEO/AEO: chúng là thứ Google và AI Search trích dẫn, và Google cache
   rất lâu. Một câu sai ở đây sống lâu hơn một câu sai trong app.

⚠️ SỬA WIKI LÀ SỬA TAY (generator đã mất). Nên bộ này phải bắt được cả lỗi "sửa 21
   trang, quên 1 trang" — vì thế mọi phép kiểm đều quét TOÀN BỘ 22 trang, không lấy
   mẫu.

Mục [4] gọi mạng thật (kiểm URL nguồn còn sống). Bỏ qua bằng `--offline`.

  python scratchpad/check_wiki.py
  python scratchpad/check_wiki.py --offline
"""
import io
import os
import re
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OFFLINE = "--offline" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SV = os.path.join(ROOT, "..", "AstroqSV")

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


PAGES = []
for d in ("wiki", "wiki/en"):
    for f in sorted(os.listdir(os.path.join(ROOT, d))):
        if f.endswith(".html"):
            PAGES.append((d, f))

RAW = {}
TXT = {}
for d, f in PAGES:
    s = io.open(os.path.join(ROOT, d, f), encoding="utf-8").read()
    RAW["%s/%s" % (d, f)] = s
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    TXT["%s/%s" % (d, f)] = re.sub(r"\s+", " ", t)

VI = [k for k in RAW if k.startswith("wiki/") and not k.startswith("wiki/en/")]
EN = [k for k in RAW if k.startswith("wiki/en/")]

print("\n=== [0] Bộ trang còn nguyên hình dạng ===")
check("có đúng 22 trang (11 VI + 11 EN)",
      len(PAGES) == 22 and len(VI) == 11 and len(EN) == 11,
      "%d trang: %d VI, %d EN" % (len(PAGES), len(VI), len(EN)))
check("mỗi bản có mục lục riêng",
      "wiki/index.html" in RAW and "wiki/en/index.html" in RAW)

print("\n=== [1] KHÔNG nêu ngày mở cửa ===")
# Chủ dự án chốt 19/08/2026: BỎ HẲN mệnh đề ngày. Lý do là số đo — mọi ngày cụ thể rồi
# cũng thành câu nói sai, mà Google cache wiki lâu hơn hẳn thời gian một mốc còn đúng.
_date = []
for k, t in TXT.items():
    # ⚠️ XOÁ RIÊNG cụm bản quyền, KHÔNG bỏ qua theo lân cận. Bản đầu của phép kiểm này
    #    bỏ qua mọi khớp có "©" trong 60 ký tự quanh nó — và bài kiểm-răng 19/08/2026
    #    cho thấy nó tạo một chỗ trú: chèn "mở cửa đầu tháng 8/2026." ngay trước
    #    "© 2026 astroQ" thì lọt sạch. Cắt đúng cụm cần bỏ mới là cách chặt.
    t2 = re.sub(r"©\s*20\d\d", " ", t)
    for m in re.finditer(r"(đầu tháng \d+|tháng \d+ năm 20\d\d|early [A-Z][a-z]+ 20\d\d|"
                         r"[A-Z][a-z]+ 20\d\d|\d{1,2}/\d{1,2}/20\d\d)", t2):
        _date.append("%s: %s" % (os.path.basename(k), m.group(0)))
check("không trang nào nêu ngày/tháng mở cửa", not _date, "; ".join(_date[:4]))

print("\n=== [2] LUẬT THƯỞNG phải khớp server ===")
_wallet = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Wallet.cs"),
                  encoding="utf-8").read()
m_les = re.search(r"MaxPerLesson\s*=\s*(\d+)", _wallet)
m_pass = re.search(r"QuizPassRatio\s*=\s*([\d.]+)", _wallet)
m_bon = re.search(r"WaitlistBonus\s*=\s*(\d+)", _wallet)
check("đọc được ba mốc ở server", bool(m_les and m_pass and m_bon),
      "lesson=%s pass=%s bonus=%s" % (m_les and m_les.group(1),
                                      m_pass and m_pass.group(1),
                                      m_bon and m_bon.group(1)))

# ⚠️ ĐỌC BÀI KHÔNG THƯỞNG (chốt 30/07/2026, tức SAU khi wiki sinh ra 27/07 — đó chính
#    là cách wiki lạc hậu mà không ai biết).
if m_les and int(m_les.group(1)) == 0:
    _earn = []
    for k, t in TXT.items():
        for pat in (r"Đọc xong một bài[^|]{0,40}Kiếm được",
                    r"Đọc[^.]{0,30}bài[^.]{0,40}(nhận thưởng|được thưởng)",
                    r"Finishing (a|an) [^|]{0,30}article[^|]{0,20}Earn",
                    r"Rewarded once per article"):
            if re.search(pat, t, re.I):
                _earn.append(os.path.basename(k))
                break
    # Thêm hai khuôn nữa: bài kiểm-răng cho thấy hai biểu thức trên KẸP KHOẢNG CÁCH
    # (`[^.]{0,30}`) nên "Mỗi bài chỉ nhận thưởng một lần" quay lại vẫn lọt.
    for k, t in TXT.items():
        if re.search(r"(Mỗi bài chỉ nhận thưởng|Rewarded once per article)", t, re.I):
            _earn.append(os.path.basename(k))
    check("không trang nào nói ĐỌC BÀI có thưởng (server: MaxPerLesson = 0)",
          not _earn, "; ".join(sorted(set(_earn))))

    # ⚠️ PHÉP KIỂM KHẲNG ĐỊNH, mạnh hơn hẳn các phép phủ định ở trên: ô "Loại" của
    #    hàng đọc bài PHẢI nói thẳng là không có thưởng. Phủ định thì lách được bằng
    #    cách viết lại câu; khẳng định thì không.
    _rows = [("wiki/purple-meteors-hoat-dong.html",
              r"Đọc xong một bài[^|]{0,40}?Không thưởng", "Không thưởng"),
             ("wiki/en/how-purple-meteors-work.html",
              r"Finishing an article[^|]{0,40}?No reward", "No reward")]
    for key, pat, want in _rows:
        t = TXT.get(key, "")
        check("%s: ô Loại của hàng đọc bài ghi '%s'" % (os.path.basename(key), want),
              bool(re.search(pat, t)), "không thấy")

# ⚠️ Thưởng quiz đòi ĐẠT CẢ LƯỢT, không phải mỗi câu đúng (`AwardQuiz` gọi `QuizPassed`).
_perq = [os.path.basename(k) for k, t in TXT.items()
         if re.search(r"Trả lời đúng câu quiz\s*\|?\s*Kiếm được", t)
         or re.search(r"Answering a quiz question correctly[^|]{0,10}Earn", t)]
check("không trang nào nói MỖI CÂU ĐÚNG là có thưởng", not _perq, "; ".join(_perq))
if m_pass:
    _pct = str(int(float(m_pass.group(1)) * 100))
    _has = [k for k, t in TXT.items() if _pct + "%" in t]
    check("trang nói về kinh tế có nêu mốc đạt %s%%" % _pct, len(_has) >= 2,
          "%d trang" % len(_has))

print("\n=== [3] QUÀ DANH SÁCH CHỜ: con số và điều kiện khớp server ===")
if m_bon:
    _b = m_bon.group(1)
    _wrong = []
    for k, t in TXT.items():
        for m in re.finditer(r"(\d[\d.,]*)\s*Purple Meteors", t):
            if m.group(1).replace(".", "").replace(",", "") != _b:
                _wrong.append("%s: %s" % (os.path.basename(k), m.group(1)))
    check("mọi con số 'N Purple Meteors' đều bằng Wallet.WaitlistBonus (%s)" % _b,
          not _wrong, "; ".join(_wrong[:4]))
    _n = sum(1 for t in TXT.values() if "Purple Meteors" in t)
    check("lời mời quà có mặt ở các trang (đếm được, không đoán)", _n >= 11,
          "%d/22 trang" % _n)

# ⚠️ Server KHÔNG kẹp mốc thời gian nào: `ClaimWaitlistBonusAsync` chỉ đòi CÓ bản ghi
#    `WAITLIST#`. Nên wiki không được thêm điều kiện "trước ngày mở cửa" — hứa chặt
#    hơn thực tế cũng là nói sai, và từ sau ngày mở cửa nó đọc ra như đã hết hạn.
_deadline = [os.path.basename(k) for k, t in TXT.items()
             if re.search(r"(trước ngày mở cửa|before opening day|before launch day)", t, re.I)]
check("không trang nào đặt điều kiện thời gian cho quà", not _deadline,
      "; ".join(_deadline))

print("\n=== [4] Liên kết ===")
# (a) Đường dẫn nội bộ phải trỏ vào file có thật.
_broken = []
for k, s in RAW.items():
    d = os.path.dirname(k)
    for h in re.findall(r'(?:href|src)="([^"#?]+)"', s):
        if h.startswith("http") or h in ("/", "/en/"):
            continue
        tgt = (os.path.join(ROOT, h.lstrip("/")) if h.startswith("/")
               else os.path.normpath(os.path.join(ROOT, d, h)))
        if h.endswith("/"):
            tgt = os.path.join(tgt, "index.html")
        if not os.path.exists(tgt):
            _broken.append("%s -> %s" % (os.path.basename(k), h))
check("0 đường dẫn nội bộ hỏng", not _broken, "; ".join(_broken[:4]))

# (b) Bản EN phải trỏ "home" về /en/, KHÔNG về / (trang tiếng Việt).
#     Đây là lỗi đã đo 19/08/2026: 45 chỗ ở 11 trang EN trỏ sai — người đọc bài tiếng
#     Anh bấm "home" thì rơi vào trang tiếng Việt.
_home = []
for k in EN:
    n_root = len(re.findall(r'href="/"', RAW[k]))
    if n_root:
        _home.append("%s: %d chỗ" % (os.path.basename(k), n_root))
check("bản EN không còn link nào về `/` (phải là `/en/`)", not _home,
      "; ".join(_home[:4]))
_en_home = sum(len(re.findall(r'href="/en/"', RAW[k])) for k in EN)
check("bản EN có link về `/en/`", _en_home >= 11, "%d chỗ" % _en_home)

# (c) hreflang + canonical.
for k in RAW:
    tags = sorted(set(re.findall(r'hreflang="([^"]+)"', RAW[k])))
    if tags != ["en", "vi", "x-default"]:
        check("%s: đủ 3 thẻ hreflang" % os.path.basename(k), False, str(tags))
_hl = all(sorted(set(re.findall(r'hreflang="([^"]+)"', s))) == ["en", "vi", "x-default"]
          for s in RAW.values())
check("cả 22 trang đều có đúng 3 thẻ hreflang (vi/en/x-default)", _hl)
_can = all(re.search(r'rel="canonical"', s) for s in RAW.values())
check("cả 22 trang đều khai canonical", _can)

# (d) sitemap phải liệt kê đủ 22 URL.
_sm = io.open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
_miss = []
for d, f in PAGES:
    url = ("https://astroq.org/%s/" % d) if f == "index.html" else \
          ("https://astroq.org/%s/%s" % (d, f))
    if url not in _sm:
        _miss.append(url)
check("sitemap.xml có đủ 22 URL wiki", not _miss, "; ".join(_miss[:3]))

print("\n=== [5] Khuôn Direct Answer Pattern còn nguyên ===")
_ans = []
for k in RAW:
    if k.endswith("index.html"):
        continue
    m = re.search(r'(?is)<(div|p|section)[^>]*class="[^"]*answer[^"]*"[^>]*>(.*?)</\1>', RAW[k])
    if not m:
        _ans.append("%s: KHÔNG có khối .answer" % os.path.basename(k))
        continue
    t = re.sub(r"(?s)<[^>]+>", " ", m.group(2))
    t = re.sub(r"^\s*(TRẢ LỜI NHANH|QUICK ANSWER)\s*", "", re.sub(r"\s+", " ", t).strip(),
               flags=re.I)
    n = len(t.split())
    # 40–60 từ là luật `gen_wiki.py` cũ tự assert. Generator mất rồi thì bộ này giữ.
    if not 40 <= n <= 60:
        _ans.append("%s: %d từ" % (os.path.basename(k), n))
check("cả 20 bài có khối trả lời nhanh trong 40–60 từ", not _ans, "; ".join(_ans[:4]))

print("\n=== [6] KHÔNG hứa tính năng đang khoá ===")
# `js/locks.js` là nơi duy nhất quyết cái gì đang khoá — đọc từ đó, đừng gõ tay danh sách.
_locks = io.open(os.path.join(ROOT, "js", "locks.js"), encoding="utf-8").read()
_soon_keys = re.findall(r'"(?:game|mission):([a-z]+)"\s*:\s*\{\s*state:\s*"soon"', _locks)
_names = {"survival": ("Trạm Sinh Tồn", "Survival Station"),
          "comms": ("Trạm Liên Lạc", "Comms Station"),
          "recycle": ("Trạm Tuần Hoàn", "Recycling Station"),
          "units": ("Trạm Đối Chiếu", "Units Station"),
          "moon": ("nhiệm vụ Mặt Trăng", "Moon mission")}
_promised = []
for k, t in TXT.items():
    for key in _soon_keys:
        for nm in _names.get(key, ()):
            if nm and nm in t:
                _promised.append("%s: %s" % (os.path.basename(k), nm))
check("không trang nào nhắc tính năng đang ở trạng thái 'soon'", not _promised,
      "; ".join(_promised[:4]))
print("      (đang khoá theo js/locks.js: %s)" % ", ".join(sorted(set(_soon_keys))))

print("\n=== [7] URL nguồn còn sống ===")
if OFFLINE:
    print("  [ ]    bỏ qua theo --offline")
else:
    _urls = set()
    for s in RAW.values():
        for h in re.findall(r'href="(https?://[^"]+)"', s):
            if "astroq.org" not in h:
                _urls.add(h)
    _dead = []
    for u in sorted(_urls):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status >= 400:
                    _dead.append("%s %s" % (r.status, u))
        except urllib.error.HTTPError as e:
            _dead.append("%s %s" % (e.code, u))
        except Exception as e:
            _dead.append("%s %s" % (type(e).__name__, u))
    check("cả %d URL nguồn đều còn sống" % len(_urls), not _dead, "; ".join(_dead[:3]))

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
