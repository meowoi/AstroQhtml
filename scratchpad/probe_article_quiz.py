# -*- coding: utf-8 -*-
"""Do DAU-CUOI: bam "LAM QUIZ BAI NAY" o cuoi mot bai doc thi co ra dung cau cua
bai do khong.

VI SAO CAN MOT BO RIENG: `smoke_library_featured.py` da canh `terms` phai tro vao
mot file cau CO THAT — nhung do la kiem DU LIEU. No khong tra loi duoc cau "tre
bam nut thi co gap dung cau khong": duong di con qua `library.html` (doc
`curArt.terms`), qua `quiz.html?terms=` (co the LUI VE de ngau nhien khi khoa sai
het — luat o `quiz.html` dong ~345), roi qua `byTerms`. Bo nay di het duong do.

⚠️⚠️ TU 22/08/2026 KHONG CON BAI NAO THIEU `terms` (67/67 da noi). Nhom "chua
   co terms" vi the RONG, va muc [2] doi sang hai phat bieu MANH HON: mot bat bien
   "moi bai doc phai co `terms`" (ghim lai de them bai moi ma quen noi la bao ngay),
   cong chieu do cu "quiz mo BINH THUONG khi khong co tham so `terms`" — nay do bang
   cach mo thang `quiz.html`, khong con phu thuoc viec phai co mot bai trong.

⚠️ Doi chieu bang CHU CUA CAU HOI doc THANG tu `js/quiz/<khoa>.js` (bang Python),
   khong doc bien trong trang: `quiz.html` giu `QUESTIONS` trong IIFE nen ngoai
   khong voi toi — cung gioi han da ghi cho `shot_sprites.py`.

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/probe_article_quiz.py
"""
import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"
dat = hong = 0

# Bai vua noi 22/08/2026 + mot bai da noi tu truoc lam doi chung.
CO_TERMS = [
    ("lib-blackhole", ["black-hole-light"]),
    ("lib-exoplanet", ["exoplanet", "exoplanet-transit"]),
    ("lib-nebula", ["nebula"]),
    ("art-microgravity-is-falling", ["gravity-distance"]),
    ("art-code-written-before-launch", ["sequence"]),
    ("art-loop-you-can-see-on-mars", ["loop"]),          # doi chung: noi tu 14/08
    # ⚠️ Bon bai duoi day noi 22/08/2026 — moi nhanh mot bai, de bo do phu ca bon
    #    (life · math · physics · engineering) chu khong chi phu thien van.
    ("art-what-life-needs", ["life-needs-atmosphere"]),               # life
    ("art-units-lost-a-spacecraft", ["units-lost-an-orbiter"]),       # math
    ("art-newtons-three-laws", ["newton-first-law-inertia"]),         # physics
    ("art-life-support-recycles-water",
     ["eclss-three-systems", "oxygen-from-electrolysis"]),            # engineering
    # ⚠️ Nam bai Dot 1 noi 22/08/2026 — day la nam bai CUOI cung con thieu
    #    `terms`, nen tu day 67/67 bai doc deu co duong sang dung bo cau cua no.
    ("jwst", ["webb-sees-infrared", "webb-looks-back-13-billion"]),
    ("lib-saturn", ["saturn-rings-ice-and-rock", "cassini-13-years-at-saturn"]),
    ("lib-andromeda", ["earth-in-milky-way", "andromeda-nearest-large-galaxy"]),
    ("lib-gaia", ["gaia-3d-map-of-galaxy", "gaia-measures-position-and-motion"]),
    ("lib-mars", ["perseverance-seeks-ancient-life", "moxie-oxygen-from-mars-air"]),
]
# ⚠️ `KHONG_TERMS` DA BO 22/08/2026: 67/67 bai deu co `terms` nen danh sach do
#    tat yeu rong. Chieu do thu hai chuyen sang muc [2] duoi day.


def check(nhan, dk, ct=""):
    global dat, hong
    if dk:
        dat += 1
        print("  [OK]   " + nhan + (("  (" + ct + ")") if ct else ""))
    else:
        hong += 1
        print("  [HONG] " + nhan + (("  (" + ct + ")") if ct else ""))


def chuan(s):
    """Bo the HTML + gom khoang trang, de so chu tren man voi chu trong file."""
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def cau_hoi_cua(key):
    """Doc CHU cua cau hoi (vi + en) thang tu `js/quiz/<key>.js`."""
    p = ROOT / "js" / "quiz" / (key + ".js")
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"q:\s*\{(.*?)\}", s, re.S)
    assert m, "%s: khong doc duoc truong `q`" % key
    return {chuan(x) for x in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))}


with sync_playwright() as pw:
    b = pw.chromium.launch()
    # ⚠️ Ghim ngon ngu: `AstroQ.getLang()` lui ve `navigator.language`, ma Chromium
    #    cua Playwright mac dinh `en-US` -> phan "tieng Viet" cua bo do lang le
    #    chay bang tieng Anh (bai hoc da ghi nhieu lan).
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

    print("\n=== [1] Bai CO `terms`: nut dan sang dung cau cua bai ===")
    for slug, keys in CO_TERMS:
        mong = set()
        for k in keys:
            mong |= cau_hoi_cua(k)
        pg.goto(BASE + "/library.html?a=" + slug, wait_until="load")
        pg.wait_for_timeout(900)
        try:
            pg.wait_for_selector("#r-quiz", state="visible", timeout=8000)
        except Exception:
            check("%s: nut 'LAM QUIZ BAI NAY' hien ra" % slug, False,
                  "trinh doc khong mo? url=%s" % pg.url)
            continue
        with pg.expect_navigation(timeout=15000):
            pg.click("#r-quiz")
        url = pg.url
        check("%s: URL mang dung `terms`" % slug,
              "terms=" in url and all(k in url for k in keys),
              url.split("?")[-1][:78])
        pg.wait_for_selector("#q-text", timeout=15000)
        pg.wait_for_timeout(400)
        hien = chuan(pg.eval_on_selector("#q-text", "e => e.innerHTML"))
        # ⚠️ De co the bat dau tu BAT KY cau nao trong `terms`, nen chi doi "cau
        #    dang hien nam trong bo cau cua bai" — dung ghim mot cau cu the.
        check("%s: cau dang hien thuoc dung bo `terms`" % slug, hien in mong,
              "hien=%r" % hien[:66])

    print("\n=== [2] Bat bien: MOI bai doc deu co `terms` ===")
    # ⚠️ Doc THANG tu dia, khong doc qua trang: day la mot bat bien ve DU LIEU,
    #    va doc qua trinh duyet thi mot bai loi cu phap se doc ra "khong co terms".
    arts = sorted((ROOT / "js" / "article").glob("*.js"))
    thieu = [p.stem for p in arts
             if not re.search(r"terms\s*:\s*\[", io.open(p, encoding="utf-8").read())]
    check("moi bai doc deu khai `terms` (%d bai)" % len(arts),
          not thieu and len(arts) > 0, "thieu: %s" % thieu[:6])

    print("\n=== [2b] Khong co tham so `terms`: quiz mo BINH THUONG ===")
    # ⚠️ Chieu do thu hai. Truoc 22/08/2026 no do bang mot bai chua noi `terms`;
    #    nay khong con bai nao nhu vay nen do thang tren `quiz.html`. Dieu can bao
    #    ve KHONG doi: thieu `terms` thi quiz van rut duoc de, khong chan duong.
    pg.goto(BASE + "/quiz.html", wait_until="load")
    check("URL khong mang `terms`", "terms=" not in pg.url, pg.url.split("/")[-1])
    pg.wait_for_selector("#q-text", timeout=15000)
    pg.wait_for_timeout(400)
    n = pg.evaluate("() => document.querySelectorAll('#q-options .opt').length")
    check("van rut duoc de (4 lua chon)", n == 4, "%d lua chon" % n)
    tong = pg.inner_text("#q-total").strip()
    check("badge tong so cau = 5", tong == "5", tong)

    check("0 loi trang / console trong suot bai kiem", not errs, "; ".join(errs[:3]))
    ctx.close()
    b.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
