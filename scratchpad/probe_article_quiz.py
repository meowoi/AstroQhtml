# -*- coding: utf-8 -*-
"""Do DAU-CUOI: bam "LAM QUIZ BAI NAY" o cuoi mot bai doc thi co ra dung cau cua
bai do khong.

VI SAO CAN MOT BO RIENG: `smoke_library_featured.py` da canh `terms` phai tro vao
mot file cau CO THAT — nhung do la kiem DU LIEU. No khong tra loi duoc cau "tre
bam nut thi co gap dung cau khong": duong di con qua `library.html` (doc
`curArt.terms`), qua `quiz.html?terms=` (co the LUI VE de ngau nhien khi khoa sai
het — luat o `quiz.html` dong ~345), roi qua `byTerms`. Bo nay di het duong do.

⚠️ Bai KHONG khai `terms` thi phai mo quiz THUONG, khong duoc chan duong di — do
   ca chieu do (20/67 bai hien nay vẫn chua co `terms`).

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
]
# Bai CHUA co `terms` — phai mo quiz THUONG chu khong chan duong.
KHONG_TERMS = ["art-newtons-three-laws", "jwst"]


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

    print("\n=== [2] Bai CHUA co `terms`: mo quiz THUONG, khong chan duong ===")
    for slug in KHONG_TERMS:
        pg.goto(BASE + "/library.html?a=" + slug, wait_until="load")
        pg.wait_for_timeout(900)
        pg.wait_for_selector("#r-quiz", state="visible", timeout=8000)
        with pg.expect_navigation(timeout=15000):
            pg.click("#r-quiz")
        url = pg.url
        check("%s: mo quiz thuong (khong co `terms`)" % slug,
              "quiz.html" in url and "terms=" not in url, url.split("/")[-1][:60])
        pg.wait_for_selector("#q-text", timeout=15000)
        pg.wait_for_timeout(300)
        n = pg.evaluate("() => document.querySelectorAll('#q-options .opt').length")
        check("%s: van rut duoc de (4 lua chon)" % slug, n == 4, "%d lua chon" % n)

    check("0 loi trang / console trong suot bai kiem", not errs, "; ".join(errs[:3]))
    ctx.close()
    b.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
