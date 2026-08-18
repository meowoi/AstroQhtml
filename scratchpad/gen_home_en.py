# -*- coding: utf-8 -*-
"""
gen_home_en.py — SINH `en/index.html` (trang chủ bản tiếng Anh) TỪ `index.html`
                  + từ điển `en` trong `js/index.js`, và vá `hreflang` vào cả hai.

    python scratchpad/gen_home_en.py            # sinh + vá
    python scratchpad/gen_home_en.py --check    # chỉ kiểm, không ghi gì

VÌ SAO SINH CHỨ KHÔNG GÕ TAY
----------------------------
Trang chủ có **55 điểm i18n** và **2 khối JSON-LD**, mà CLAUDE.md ghi rõ luật:
*"nội dung FAQ khớp 1-1 với khối JSON-LD — sửa 1 bên phải sửa bên kia"*. Gõ tay
bản thứ hai là dựng ngay một cặp sẽ trôi khỏi nhau ở lần sửa chữ đầu tiên. Sinh
thì **hai bản khớp theo cấu tạo**: cùng đọc một từ điển, cùng một khuôn markup.

VÌ SAO PHẢI CÓ URL RIÊNG (`/en/`) CHỨ KHÔNG PHẢI ĐỔI CHỮ BẰNG JS
----------------------------------------------------------------
Trước 07/08/2026 một URL `/` phục vụ cả hai ngôn ngữ bằng JS. Hậu quả đo được:
`<title>` và chữ hiển thị đổi sang tiếng Anh, nhưng **cả 2 khối JSON-LD mãi là
tiếng Việt** — tức Google thấy dữ liệu có cấu trúc lệch với nội dung, trên đúng
trang DUY NHẤT đang được lập chỉ mục. Và `index.html` có **0 thẻ hreflang**
trong khi cả 22 trang `wiki/` đều có đủ 3. Nay theo **đúng khuôn `wiki/`**:
mỗi ngôn ngữ một URL tĩnh, nội dung + JSON-LD + canonical + og: đều cùng một
thứ tiếng, và 3 thẻ hreflang trỏ chéo.

⚠️ KHÔNG TỰ CHUYỂN HƯỚNG `/` → `/en/` (chủ dự án chốt 07/08/2026). hreflang đã
   lo phần lưu lượng từ Google; khách gõ thẳng URL thì thấy một **dải mời** đóng
   được. Tự chuyển hướng thì [Chưa kiểm chứng] Googlebot render JS ở locale
   en-US và không ở múi giờ Việt Nam nên nhiều khả năng cũng bị chuyển, khiến
   `/` không được lập chỉ mục đúng như bản tiếng Việt.
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_HTML = os.path.join(ROOT, "index.html")
SRC_JS = os.path.join(ROOT, "js", "index.js")
OUT_DIR = os.path.join(ROOT, "en")
OUT_HTML = os.path.join(OUT_DIR, "index.html")

U_VI = "https://astroq.org/"
U_EN = "https://astroq.org/en/"

# ---------------------------------------------------------------------------
# CHỖ DUY NHẤT CÓ CHỮ TIẾNG ANH GÕ TAY.
# Mọi chữ hiện ra cho người đọc đều lấy từ từ điển `en` của js/index.js; riêng
# các thẻ <meta> và khối EducationalApplication thì KHÔNG có trong từ điển (chúng
# không phải nội dung hiển thị), nên phải khai ở đây — một chỗ, dễ rà.
# ⚠️ Ngày ra mắt xuất hiện ở đây: CLAUDE.md liệt kê 7 chỗ phải sửa cùng lúc, nay
#    là 8 (thêm bản EN). Có phép kiểm đối chiếu với `LAUNCH_AT` bên dưới.
# ---------------------------------------------------------------------------
EN_META = {
    "description": "astroQ.org is an interactive 3D STEM learning platform about "
                   "Space, AI and Quantum Physics for children and beginners. Sign up "
                   "by email to get 500 starter Purple Meteors.",
    "og_title": "astroQ.org — Explore the Galaxy of Knowledge",
    "og_description": "An interactive learning platform on Space, AI & Quantum Physics "
                      "for young explorers. Sign up by email for 500 starter Purple Meteors.",
    "tw_title": "astroQ.org — Explore the Galaxy of Knowledge",
    "tw_description": "Learn Astronomy, AI & Quantum Physics through cosmic missions. "
                      "Sign up for 500 starter Purple Meteors.",
    "img_alt": "astroQ.org — Explore the Galaxy of Knowledge. Comet the cat and Byte "
               "the robot, with 500 starter Purple Meteors for new sign-ups.",
}

EN_APP_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "EducationalApplication",
  "name": "astroQ.org",
  "alternateName": "astroQ",
  "url": "https://astroq.org/en/",
  "applicationCategory": "EducationalApplication",
  "applicationSubCategory": "STEM Learning Game",
  "operatingSystem": "Web (any modern browser)",
  "browserRequirements": "Requires a browser with HTML5 and WebGL support",
  "inLanguage": ["en", "vi"],
  "datePublished": "2026-08-20",
  "description": "astroQ.org is an interactive 3D gamified STEM education platform that helps children and beginners learn Astronomy, Quantum Physics, AI and Robotics through a spaceship-cockpit interface and galaxy exploration missions.",
  "educationalUse": ["Self-study", "Game-based learning", "STEM curriculum supplement"],
  "learningResourceType": ["Interactive Simulation", "Quiz", "Educational Game", "3D Explorer"],
  "teaches": ["Astronomy", "The Solar System", "Quantum Physics", "Artificial Intelligence (AI)", "Robotics"],
  "audience": {
    "@type": "EducationalAudience",
    "educationalRole": "student",
    "audienceType": "Children and beginners"
  },
  "featureList": [
    "3D map of the Solar System and the stellar neighbourhood",
    "Level-based diagnostic quizzes",
    "Science reading library sourced from NASA/ESA",
    "Mini-games for reflexes and reasoning",
    "Purple Meteors reward system"
  ],
  "author": { "@type": "Organization", "name": "astroQ.org", "url": "https://astroq.org/" },
  "publisher": { "@type": "Organization", "name": "astroQ.org", "url": "https://astroq.org/" }
}"""

HREFLANG = ('<link rel="alternate" hreflang="vi" href="%s" />\n'
            '<link rel="alternate" hreflang="en" href="%s" />\n'
            '<link rel="alternate" hreflang="x-default" href="%s" />' % (U_VI, U_EN, U_VI))

_ok = _bad = 0


def check(cond, label, extra=""):
    global _ok, _bad
    if cond:
        _ok += 1
        print("  [OK]   %s" % label)
    else:
        _bad += 1
        print("  [HONG] %s %s" % (label, extra))
    return bool(cond)


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


# ---------------------------------------------------------------------------
def parse_dict(js, lang):
    """Bóc từ điển `vi:{…}` / `en:{…}` trong js/index.js.

    ⚠️ HAI CÁI BẪY, cả hai đều làm script báo "từ điển thiếu khoá" OAN:
       ① ĐỪNG quét theo dòng — nhiều khoá nằm CHUNG một dòng
          (`cd_d:"days", cd_h:"hours", …`); bản đầu quét `^\\s{6}(\\w+):` nên bỏ
          sót 11 khoá.
       ② PHẢI nhận CẢ nháy đơn. Những chuỗi có `<b id="…">` bên trong được khai
          bằng `'…'` cho khỏi phải thoát dấu nháy (`done_body`, `done_body_nomail`,
          `ok_short`…). Chỉ khớp `"…"` là bỏ sót đúng chúng.
    """
    m = re.search(r"\n    %s:\{(.*?)\n    \}" % lang, js, re.S)
    if not m:
        return {}
    body = m.group(1)
    out = {}
    for k, q, v in re.findall(
            r"""(\w+)\s*:\s*(["'])((?:[^\\]|\\.)*?)\2""", body):
        out[k] = (v.replace("\\" + q, q).replace("\\\\", "\\")
                   .replace("\\n", "\n").replace("\\t", "\t"))
    return out


def esc_attr(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


SLOT = re.compile(r'(<(\w+)\b[^>]*\bdata-i18n(-html)?="(\w+)"[^>]*>)(.*?)(</\2>)', re.S)
ATTR = {"ph": "placeholder", "title": "title", "aria": "aria-label", "alt": "alt"}


def fill_slots(html, d):
    """Đổ chữ vào mọi điểm data-i18n*.

    `data-i18n`      → nội dung thẻ, THOÁT `<` và `&`
    `data-i18n-html` → nội dung thẻ NGUYÊN VĂN (chuỗi có `<b>`)
    `-ph/-title/-aria/-alt` → thuộc tính tương ứng

    ⚠️ Vẫn GIỮ NGUYÊN các thuộc tính `data-i18n*` trong bản sinh ra, cố ý: khi
       trang chạy, `AstroQ.applyTexts` sẽ đổ lại đúng những chuỗi đó từ từ điển
       — tức một phép kiểm chéo miễn phí, và nếu JS hỏng thì trang vẫn đọc được
       vì chữ đã nằm sẵn trong HTML tĩnh (đó mới là thứ Google đọc).
    """
    def txt(m):
        open_tag, _tag, is_html, key, _inner, close = m.groups()
        if key not in d:
            return m.group(0)
        val = d[key]
        if not is_html:
            val = val.replace("&", "&amp;").replace("<", "&lt;")
        return open_tag + val + close

    html = SLOT.sub(txt, html)

    for sel, attr in ATTR.items():
        # ⚠️⚠️ `\balt=` KHỚP CẢ `alt=` NẰM TRONG `data-i18n-alt=` — dấu `-` cũng
        #    là ranh giới từ của `\b`. Bản đầu của script này vì thế ghi chuỗi
        #    tiếng Anh đè lên chính KHOÁ (`data-i18n-alt="Comet the cat — …"`)
        #    rồi để nguyên `alt="Mèo Comet — …"` tiếng Việt. Lỗi im lặng: HTML
        #    vẫn hợp lệ, trang vẫn chạy, chỉ có nội dung trình đọc màn hình sai
        #    ngôn ngữ. Phải chặn ký tự `-` và chữ ngay trước tên thuộc tính.
        RE = r'(?<![-\w])%s="[^"]*"' % re.escape(attr)

        def rep(m, attr=attr, RE=RE):
            tag, key = m.group(0), m.group(1)
            if key not in d:
                return tag
            new = '%s="%s"' % (attr, esc_attr(d[key]))
            if re.search(RE, tag):
                return re.sub(RE, new, tag, count=1)
            return tag[:-1].rstrip() + " " + new + ">"
        html = re.sub(r'<[^>]*\bdata-i18n-%s="(\w+)"[^>]*>' % sel, rep, html)
    return html


def faq_jsonld(d, url):
    """Dựng FAQPage TỪ CHÍNH từ điển đang vẽ ra phần FAQ hiển thị.

    ⚠️ ĐÂY LÀ ĐIỂM CỐT LÕI CỦA CẢ SCRIPT. Luật ở CLAUDE.md là *"nội dung FAQ
       khớp 1-1 với khối JSON-LD"*, và bản tiếng Việt đang giữ luật đó bằng
       cách người viết NHỚ sửa hai chỗ. Bản tiếng Anh thì khớp **theo cấu tạo**:
       cùng đọc `q1..q5`/`a1..a5`, nên không có cách nào lệch.
    """
    import json
    items = []
    for i in range(1, 6):
        q, a = d.get("q%d" % i), d.get("a%d" % i)
        if not q or not a:
            return None
        items.append({"@type": "Question", "name": q,
                      "acceptedAnswer": {"@type": "Answer", "text": a}})
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": items}, ensure_ascii=False, indent=2)


def lang_switch(active):
    """Nút VI/EN thành LINK THẬT, không phải nút JS.

    ⚠️ Phải là `<a href>` để Googlebot đi được sang bản kia — đó là nửa còn lại
       của hreflang, và là đúng cách `wiki/` đã làm (`<a class="top-link">`).
       Một `<button>` gọi JS thì crawler không theo được, và trang chủ nay là
       trang TĨNH theo từng ngôn ngữ nên cũng chẳng còn gì để JS đổi.
    """
    a = lambda code, href, label: (
        '<a href="%s" data-lang="%s" hreflang="%s"%s>%s</a>'
        % (href, code, code, ' class="active" aria-current="true"' if code == active else "", label))
    return (a("vi", "/", "VI"), a("en", "/en/", "EN"))


# ⚠️⚠️ IDEMPOTENT LÀ BẮT BUỘC, KHÔNG PHẢI CHO ĐẸP — LỖI THẬT ĐÃ SỬA 07/08/2026.
#    Script này VÁ CHÍNH FILE NGUỒN của nó (`index.html`), nên lần chạy thứ hai
#    thấy một markup khác lần đầu. Bản đầu chỉ khớp `<button type="button"
#    data-lang="vi">`; chạy lần hai thì không khớp gì cả, phép thay LẶNG LẼ
#    KHÔNG LÀM GÌ, và bản EN thừa hưởng nguyên dấu `class="active"` của bản VI —
#    tức trang tiếng Anh tô sáng nút "VI". Không lỗi, không cảnh báo, chỉ sai.
#    Nay khớp CẢ HAI dạng, và có phép kiểm đòi phép thay phải thật sự xảy ra.
SWITCH_RE = re.compile(
    r'<(?:button type="button"|a [^>]*?)\s*data-lang="vi"[^>]*>VI</(?:button|a)>\s*'
    r'<(?:button type="button"|a [^>]*?)\s*data-lang="en"[^>]*>EN</(?:button|a)>',
    re.S)


def set_switch(html, active):
    vi_a, en_a = lang_switch(active)
    # `subn` (không phải `sub`) để biết phép thay CÓ XẢY RA hay không — im lặng
    # không thay chính là lỗi idempotent tả ở trên.
    return SWITCH_RE.subn(vi_a + "\n        " + en_a, html, count=1)


# ---------------------------------------------------------------------------
def build_en(html, en, vi):
    """index.html (tiếng Việt) -> en/index.html (tiếng Anh)."""
    h = html

    # --- <html lang> ---
    h = h.replace('<html lang="vi">', '<html lang="en">', 1)

    # --- thẻ head ngôn ngữ + URL ---
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % en["title"], h, count=1, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + esc_attr(EN_META["description"]) + m.group(2), h, count=1)
    h = h.replace('<link rel="canonical" href="%s" />' % U_VI,
                  '<link rel="canonical" href="%s" />' % U_EN, 1)
    h = h.replace('<meta property="og:locale" content="vi_VN" />',
                  '<meta property="og:locale" content="en_US" />', 1)
    h = h.replace('<meta property="og:locale:alternate" content="en_US" />',
                  '<meta property="og:locale:alternate" content="vi_VN" />', 1)
    h = h.replace('<meta property="og:url" content="%s" />' % U_VI,
                  '<meta property="og:url" content="%s" />' % U_EN, 1)
    for prop, key in (("og:title", "og_title"), ("og:description", "og_description"),
                      ("og:image:alt", "img_alt")):
        h = re.sub(r'(<meta property="%s" content=")[^"]*(")' % re.escape(prop),
                   lambda m, k=key: m.group(1) + esc_attr(EN_META[k]) + m.group(2), h, count=1)
    for name, key in (("twitter:title", "tw_title"), ("twitter:description", "tw_description"),
                      ("twitter:image:alt", "img_alt")):
        h = re.sub(r'(<meta name="%s" content=")[^"]*(")' % re.escape(name),
                   lambda m, k=key: m.group(1) + esc_attr(EN_META[k]) + m.group(2), h, count=1)

    # --- hai khối JSON-LD ---
    blocks = re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', h, re.S)
    if len(blocks) != 2:
        return None, "index.html phai co dung 2 khoi JSON-LD, dang co %d" % len(blocks)
    faq = faq_jsonld(en, U_EN)
    if faq is None:
        return None, "tu dien `en` thieu khoa q1..q5 / a1..a5"
    h = h.replace(blocks[0], EN_APP_JSONLD, 1)
    h = h.replace(blocks[1], faq, 1)

    # --- chữ hiển thị ---
    h = fill_slots(h, en)

    # --- đường dẫn tài nguyên: trang nằm sâu thêm một cấp ---
    # ⚠️ Chỉ đổi thẻ TĨNH trong HTML. Đường dẫn do JS sinh thì phải tự suy từ
    #    `document.currentScript` (xem JS_DIR trong js/index.js) — trang chủ có
    #    hai bản ở hai độ sâu, một hằng chuỗi cứng sẽ 404 ở đúng một trong hai.
    # ⚠️ PHẢI CÓ `srcset` — lỗi thật đã sửa 07/08/2026. Bản đầu chỉ bắt
    #    `href|src` nên hai thẻ <source srcset="img/m1-320.webp"> trong <picture>
    #    của Comet & Byte trỏ sang `/en/img/…` và **404**. Trình duyệt lặng lẽ
    #    lùi về thẻ <img> nên trang trông vẫn ĐÚNG — chỉ console và tab Network
    #    mới nói ra. Có phép kiểm đếm ngay dưới `build_en`.
    h = re.sub(r'(\b(?:href|src|srcset)=")(css/|js/|img/)', r"\g<1>../\g<2>", h)
    h = h.replace('href="wiki/"', 'href="../wiki/en/"')

    # --- nút chuyển ngữ thành LINK ---
    h, nsw = set_switch(h, "en")
    if nsw != 1:
        return None, "khong thay duoc nut chuyen ngu o ban EN (khop %d lan)" % nsw

    # --- hreflang ---
    h = add_hreflang(h)
    return h, None


def add_hreflang(h):
    """Chèn 3 thẻ hreflang ngay sau canonical. Idempotent."""
    if 'hreflang="x-default"' in h:
        h = re.sub(r'\n?<link rel="alternate" hreflang="[^"]*" href="[^"]*" />', "", h)
    return re.sub(r'(<link rel="canonical" href="[^"]*" />)',
                  r"\1\n" + HREFLANG, h, count=1)


# ---------------------------------------------------------------------------
def main():
    write = "--check" not in sys.argv
    print("=" * 68)
    print("  SINH TRANG CHU BAN TIENG ANH  (%s)" % ("GHI FILE" if write else "CHI KIEM"))
    print("=" * 68)

    html, js = rd(SRC_HTML), rd(SRC_JS)
    vi, en = parse_dict(js, "vi"), parse_dict(js, "en")

    # --- kiem tu dien truoc khi sinh ---
    keys = set(re.findall(r'data-i18n(?:-html|-ph|-title|-aria|-alt)?="([^"]+)"', html))
    check(len(vi) > 40 and len(en) > 40, "boc duoc 2 tu dien", "vi=%d en=%d" % (len(vi), len(en)))
    check(not (keys - set(vi)), "moi khoa trong markup co o `vi`", str(sorted(keys - set(vi))))
    check(not (keys - set(en)), "moi khoa trong markup co o `en`", str(sorted(keys - set(en))))
    check(set(vi) == set(en), "hai tu dien cung bo khoa",
          str(sorted(set(vi) ^ set(en))))

    # --- BAT BIEN CU: JSON-LD tieng Viet phai khop FAQ hien thi ---
    # Day la luat CLAUDE.md da ghi; script sinh ban EN thi tien the canh luon
    # ban VI, vi ban VI van gu bang cach NGUOI VIET NHO sua hai cho.
    vi_faq = faq_jsonld(vi, U_VI)
    blocks = re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', html, re.S)
    if len(blocks) == 2:
        import json
        try:
            got = json.loads(blocks[1])
            want = json.loads(vi_faq)
            check(got == want, "JSON-LD FAQ tieng Viet KHOP tu dien `vi` (luat 1-1)",
                  "lech - xem index.html khoi FAQPage")
        except Exception as e:
            check(False, "doc duoc JSON-LD FAQ tieng Viet", str(e))

    # --- ngay ra mat phai khop LAUNCH_AT ---
    m = re.search(r'LAUNCH_AT\s*=\s*new Date\("(\d{4})-(\d{2})-(\d{2})', js)
    if m:
        y, mo, dd = m.groups()
        # ⚠️ Doc o `en["a5"]` — tu 18/08/2026 do la cho DUY NHAT con mang ngay ra mat
        #    trong tu dien EN (title + description da bo, xem scratchpad/set_launch_copy.py).
        #    Va no cung la doan dung de dung khoi FAQPage ban EN, nen sai o day la sai ca
        #    phan hien ra lan phan du lieu co cau truc.
        check("%s August %s" % (str(int(dd)), y) in en.get("a5", ""),
              "ngay ra mat ban EN khop LAUNCH_AT (doc o en.a5)",
              "LAUNCH_AT=%s-%s-%s — sua a5 trong tu dien `en` cua js/index.js"
              % (y, mo, dd))

    if _bad:
        print("\n  DUNG LAI: tu dien chua san sang, khong sinh gi.")
        return 1

    out, err = build_en(html, en, vi)
    if err:
        check(False, "dung duoc ban EN", err)
        return 1

    # --- kiem ban vua sinh ---
    check('<html lang="en">' in out, "ban EN co <html lang=en>")
    # Dem DUNG the <link rel=alternate>. Nut chuyen ngu cung mang hreflang=
    # (dung, va nen co) nen dem tho se ra 5 — bao hong OAN.
    nlink = lambda s: len(re.findall(r'<link rel="alternate" hreflang=', s))
    check(nlink(out) == 3, "ban EN co dung 3 the <link> hreflang", str(nlink(out)))
    check('href="%s"' % U_EN in out, "canonical tro ve /en/")
    check("../css/" in out and "../js/" in out and "../img/" in out, "duong dan tai nguyen da lui mot cap")
    leftover = re.findall(r'\b(?:href|src|srcset)="(?:css/|js/|img/)[^"]*"', out)
    check(not leftover, "0 duong dan tai nguyen con o goc (se 404 tu /en/)", str(leftover[:3]))
    check("../wiki/en/" in out, "link wiki tro sang ban tieng Anh")
    check('<a href="/" data-lang="vi"' in out and '<a href="/en/" data-lang="en"' in out,
          "nut chuyen ngu la LINK that")
    # ⚠️ BO COMMENT HTML TRUOC KHI DEM. Markup cua du an co rat nhieu ghi chu
    #    tieng Viet (giai thich vi sao tung cho lam nhu vay) — chung KHONG hien
    #    ra va CO Y giu nguyen tieng Viet, vi doi ngu doc chung la nguoi Viet.
    #    Dem ca comment thi bao hong oan 280 ky tu.
    body = re.sub(r"<!--.*?-->", "", out, flags=re.S)
    viet = len(re.findall(r"[àáâãèéêìíòóôõùúýăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", body))
    check(viet == 0, "0 chu tieng Viet trong phan HIEN RA cua ban EN", "con %d ky tu co dau" % viet)

    vi_out = add_hreflang(html)
    vi_a, en_a = lang_switch("vi")
    vi_out = re.sub(r'<button type="button" data-lang="vi">VI</button>\s*<button type="button" data-lang="en">EN</button>',
                    vi_a + "\n        " + en_a, vi_out, count=1)
    check(nlink(vi_out) == 3, "ban VI co dung 3 the <link> hreflang", str(nlink(vi_out)))
    check('<a href="/" data-lang="vi" hreflang="vi" class="active"' in vi_out,
          "ban VI danh dau VI dang hoat dong")
    check('<a href="/en/" data-lang="en" hreflang="en" class="active"' in out
          and 'data-lang="vi" hreflang="vi">' in out,
          "ban EN danh dau EN dang hoat dong (KHONG thua huong dau cua ban VI)")

    if write and not _bad:
        wr(OUT_HTML, out)
        wr(SRC_HTML, vi_out)
        print("\n  da ghi: en/index.html (%s byte) + va hreflang vao index.html" % f"{len(out):,}")

    print("\n" + "-" * 68)
    print("  KET QUA: %d dat / %d hong" % (_ok, _bad))
    print("-" * 68)
    return 1 if _bad else 0


if __name__ == "__main__":
    sys.exit(main())
