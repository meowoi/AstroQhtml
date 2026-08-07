# -*- coding: utf-8 -*-
"""
smoke_home_en.py — TRANG CHỦ HAI NGÔN NGỮ: `/` (tiếng Việt) và `/en/` (tiếng Anh).

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/smoke_home_en.py

VÌ SAO CÓ BỘ NÀY
----------------
Trước 07/08/2026 một URL phục vụ cả hai ngôn ngữ bằng JS. Đo được: `<title>` và
chữ hiển thị đổi sang tiếng Anh, nhưng **cả 2 khối JSON-LD mãi là tiếng Việt** —
Google thấy dữ liệu có cấu trúc lệch nội dung, trên đúng trang DUY NHẤT được lập
chỉ mục. Và `index.html` có **0 thẻ hreflang** trong khi cả 22 trang `wiki/` đều
có đủ 3.

⚠️ PHÉP KIỂM ĐÁNG GIÁ NHẤT Ở ĐÂY LÀ **JSON-LD FAQ KHỚP 1-1 VỚI FAQ HIỆN THỊ**,
   đo trên trình duyệt: đọc `mainEntity[].name` từ khối JSON-LD rồi so với chính
   chữ trong các `<summary>`. Đó là luật CLAUDE.md đã ghi, và là thứ đã âm thầm
   sai suốt thời gian một URL phục vụ hai ngôn ngữ. `grep` không bắt được vì hai
   bên nằm ở hai chỗ khác nhau và đều "đúng cú pháp".

⚠️ Sinh lại bản EN: `python scratchpad/gen_home_en.py` (idempotent, chạy lại
   bao nhiêu lần cũng ra cùng kết quả). ĐỪNG sửa tay `en/index.html`.

⚠️ Windows: đặt PYTHONIOENCODING=utf-8.
"""

import json
import sys

BASE = "http://127.0.0.1:8123"
VIET = "àáâãèéêìíòóôõùúýăđơưạảấầậắằẻẽếềểệỉịọỏốồổộớờởợụủứừửữựỳỵỷỹ"

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


def has_viet(s):
    return any(c in VIET for c in (s or "").lower())


PROBE = """() => {
  const ld = [...document.querySelectorAll('script[type="application/ld+json"]')]
               .map(s => JSON.parse(s.textContent));
  const faq = ld.find(x => x['@type'] === 'FAQPage') || {mainEntity: []};
  const app = ld.find(x => x['@type'] === 'EducationalApplication') || {};
  return {
    lang: document.documentElement.lang,
    title: document.title,
    h1: document.querySelector('h1').textContent.trim(),
    n_ld: ld.length,
    app_url: app.url || null,
    app_desc: app.description || '',
    canon: (document.querySelector('link[rel=canonical]') || {}).href,
    og_url: (document.querySelector('meta[property="og:url"]') || {}).content,
    og_locale: (document.querySelector('meta[property="og:locale"]') || {}).content,
    desc: (document.querySelector('meta[name=description]') || {}).content,
    hl: [...document.querySelectorAll('link[rel=alternate][hreflang]')]
          .map(l => l.hreflang + '|' + l.href),
    faq_q: faq.mainEntity.map(m => m.name),
    faq_a: faq.mainEntity.map(m => m.acceptedAnswer.text),
    shown_q: [...document.querySelectorAll('details summary[data-i18n^="q"]')]
               .map(e => e.textContent.trim()),
    shown_a: [...document.querySelectorAll('details p[data-i18n^="a"]')]
               .map(e => e.textContent.trim()),
    sw: [...document.querySelectorAll('.lang-switch [data-lang]')]
          .map(a => a.tagName + ':' + a.dataset.lang + ':' +
                    (a.getAttribute('href') || '') +
                    (a.classList.contains('active') ? ':ACTIVE' : ''))
  };
}"""


def audit(ctx, path, lang, other_url):
    print("\n" + "=" * 68)
    print("  %s  (mong doi tieng %s)" % (path, "ANH" if lang == "en" else "VIET"))
    print("=" * 68)
    errs, bad404 = [], []
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    pg.on("response", lambda r: bad404.append(r.url) if r.status >= 400 else None)
    pg.goto(BASE + path, wait_until="networkidle", timeout=30000)
    pg.wait_for_timeout(900)
    d = pg.evaluate(PROBE)

    url_self = "https://astroq.org/" + ("en/" if lang == "en" else "")
    check(d["lang"] == lang, "<html lang> = %s" % lang, repr(d["lang"]))
    check(d["n_ld"] == 2, "co dung 2 khoi JSON-LD", str(d["n_ld"]))
    check(d["canon"] == url_self, "canonical -> %s" % url_self, str(d["canon"]))
    check(d["og_url"] == url_self, "og:url -> %s" % url_self, str(d["og_url"]))
    check(d["og_locale"] == ("en_US" if lang == "en" else "vi_VN"),
          "og:locale khop ngon ngu trang", str(d["og_locale"]))
    check(d["app_url"] == url_self, "EducationalApplication.url -> %s" % url_self,
          str(d["app_url"]))

    # --- hreflang: 3 the, va CA HAI ban phai khai GIONG HET NHAU ---
    want = {"vi|https://astroq.org/", "en|https://astroq.org/en/",
            "x-default|https://astroq.org/"}
    check(set(d["hl"]) == want, "3 the hreflang tro cheo dung", str(sorted(d["hl"])))

    # --- ⚠️ PHEP KIEM QUAN TRONG NHAT: JSON-LD khop 1-1 voi FAQ hien thi ---
    check(len(d["faq_q"]) == 5 and d["faq_q"] == d["shown_q"],
          "JSON-LD FAQ: CAU HOI khop 1-1 voi phan hien thi",
          json.dumps({"ld": d["faq_q"][:1], "shown": d["shown_q"][:1]}, ensure_ascii=False))
    check(d["faq_a"] == d["shown_a"],
          "JSON-LD FAQ: CAU TRA LOI khop 1-1 voi phan hien thi",
          json.dumps({"ld": d["faq_a"][:1], "shown": d["shown_a"][:1]}, ensure_ascii=False))

    # --- ngon ngu: khong duoc lan ---
    blob = " ".join(d["faq_q"] + d["faq_a"] + [d["title"], d["h1"], d["desc"], d["app_desc"]])
    check(has_viet(blob) == (lang == "vi"),
          "chu + JSON-LD deu la tieng %s (khong lan)" % ("Anh" if lang == "en" else "Viet"),
          repr(d["title"][:60]))

    # --- nut chuyen ngu la LINK that ---
    check(all(s.startswith("A:") for s in d["sw"]) and len(d["sw"]) == 2,
          "nut chuyen ngu la <a> (crawler di duoc) — nua con lai cua hreflang",
          str(d["sw"]))
    check(any(s.endswith(":ACTIVE") and (":" + lang + ":") in s for s in d["sw"]),
          "danh dau dung ban dang xem (%s)" % lang, str(d["sw"]))

    check(not bad404, "0 asset 404", str(bad404[:3]))
    check(not errs, "0 loi trang", str(errs[:2]))

    # --- bam sang ban kia thi DIEU HUONG THAT ---
    with pg.expect_navigation(wait_until="load"):
        pg.click('.lang-switch [data-lang="%s"]' % ("vi" if lang == "en" else "en"))
    pg.wait_for_timeout(400)
    check(pg.evaluate("()=>document.documentElement.lang") != lang,
          "bam sang ban kia -> DIEU HUONG that su doi trang", pg.url)
    pg.close()


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Thieu playwright: pip install playwright && playwright install chromium")
        return 2

    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900},
                             locale="en-US", timezone_id="America/New_York")
        audit(ctx, "/index.html", "vi", "/en/")
        audit(ctx, "/en/index.html", "en", "/")
        ctx.close()
        br.close()

    print("\n" + "-" * 68)
    print("  KET QUA: %d dat / %d hong" % (_ok, _bad))
    print("-" * 68)
    return 1 if _bad else 0


if __name__ == "__main__":
    sys.exit(main())
