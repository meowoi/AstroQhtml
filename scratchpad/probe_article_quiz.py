# -*- coding: utf-8 -*-
"""Do DAU-CUOI: bam "LAM QUIZ BAI NAY" o cuoi mot bai doc thi co ra dung cau cua
bai do khong.

VI SAO CAN MOT BO RIENG: `smoke_library_featured.py` da canh `terms` phai tro vao
mot file cau CO THAT — nhung do la kiem DU LIEU. No khong tra loi duoc cau "tre
bam nut thi co gap dung cau khong": duong di con qua `library.html` (doc
`curArt.terms`), qua `quiz.html?terms=` (co the LUI VE de ngau nhien khi khoa sai
het — luat o `quiz.html` dong ~345), roi qua `byTerms`. Bo nay di het duong do.

⚠️⚠️ SUA 23/08/2026 — DONG NAY TRUOC DAY GHI SAI: "TU 22/08/2026 KHONG CON BAI
   NAO THIEU `terms` (67/67 da noi)". SO DO THAT: **24/67 bai khai `terms: []`**,
   tuc RONG. Muc [2] bao xanh oan vi no tim `terms\\s*:\\s*\\[` — mau do KHOP CA
   `terms: []`, nen no do "CO KHAI `terms`" chu khong do "co tu nao trong do".
   Hau qua that o library.html:442 (`curArt.terms.length` = 0 -> `t = null`):
   nut "LAM QUIZ BAI NAY" mo DE NGAU NHIEN — dung cai loi ma cac muc nhat ky cu
   tuong da sua xong. Nay muc [2] doi `terms` KHONG RONG, va 24 bai kia nam trong
   `MIEN_TERMS` — mot danh sach CHI DUOC TEO LAI (cung ky luat voi `LEGACY_SRC`
   cua smoke_library_featured.py va "khong the nao co `src` rong" cua check_pages).

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
    # ⚠️ Nam bai Dot 1 noi 22/08/2026. ⚠️⚠️ CAU "day la nam bai CUOI cung con
    #    thieu `terms`, tu day 67/67 bai doc deu co duong sang dung bo cau" TRUOC
    #    DAY GHI O DAY LA SAI — do lai 23/08/2026 thi con 24 bai `terms: []`
    #    (nhanh AI / robot / sieu may tinh / luong tu, them tu 11/08).
    #    ⚠️ 24 bai do NAY DA NOI HET (23/08/2026) — xem khoi ⚠️⚠️ ngay duoi.
    #    Giu doan nay lam LICH SU: no ghi lai mot cau khang dinh SAI da tung
    #    song trong file nay, va cach no song duoc (phep kiem cung sai).
    ("jwst", ["webb-sees-infrared", "webb-looks-back-13-billion"]),
    ("lib-saturn", ["saturn-rings-ice-and-rock", "cassini-13-years-at-saturn"]),
    ("lib-andromeda", ["earth-in-milky-way", "andromeda-nearest-large-galaxy"]),
    ("lib-gaia", ["gaia-3d-map-of-galaxy", "gaia-measures-position-and-motion"]),
    ("lib-mars", ["perseverance-seeks-ancient-life", "moxie-oxygen-from-mars-air"]),
    # ⚠️ Hai bai noi 23/08/2026, moi bai mot nhanh (AI · robot) — hai nhanh
    #    vua viet 20 cau moi, nen bo do dau-cuoi phai cham vao chung.
    ("art-ai-counts-storm-damage", ["ai-counts-tarps"]),               # AI
    ("art-canadarm2-robot-arm", ["canadarm2-two-hands"]),              # robot
]
# ⚠️⚠️ TU 23/08/2026: 67/67 BAI DOC DEU CO `terms` KHONG RONG — `MIEN_TERMS` RONG.
#    Truoc do 24 bai (nhanh AI · robot · sieu may tinh · luong tu, them tu
#    11/08) khai `terms: []` va mo DE NGAU NHIEN khi tre bam "LAM QUIZ BAI
#    NAY" (library.html:442). Cho ra la mot LO HONG NOI DUNG chu khong phai
#    loi ma: bank khong co cau nao cho bon nhanh do, nen phai VIET 20 cau co
#    nguon (+ 4 bai noi vao cau da co). Da lam, nen danh sach mien tru rong.
# ⚠️ GIU CAI KHUNG RONG NAY, dung xoa: no la cho mien tru mot bai MOI them ma
#    chua kip viet cau. Phep kiem "chi duoc TEO LAI" o muc [2] van con rang —
#    them slug vao day thi phai ghi ly do va phai co ke hoach xoa.
MIEN_TERMS = {
}



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

    print("\n=== [2] Bat bien: MOI bai doc co `terms` KHONG RONG ===")
    # ⚠️ Doc THANG tu dia, khong doc qua trang: day la mot bat bien ve DU LIEU,
    #    va doc qua trinh duyet thi mot bai loi cu phap se doc ra "khong co terms".
    # ⚠️⚠️ PHAI DOI KHONG RONG, khong chi "co khai". Ban cu tim `terms\s*:\s*\[`
    #    nen `terms: []` cung khop -> bao xanh cho 24 bai dang mo de ngau nhien.
    arts = sorted((ROOT / "js" / "article").glob("*.js"))

    def _terms_cua(p):
        """Khoa trong `terms` cua mot bai. None = khong khai; [] = khai ma rong."""
        s = io.open(p, encoding="utf-8").read()
        m = re.search(r"terms\s*:\s*\[(.*?)\]", s, re.S)
        if not m:
            return None
        return re.findall(r'"([^"]+)"', m.group(1))

    _map = dict((p.stem, _terms_cua(p)) for p in arts)
    khong_khai = sorted(k for k, v in _map.items() if v is None)
    rong = sorted(k for k, v in _map.items() if v == [])
    day_du = len(arts) - len(khong_khai) - len(rong)
    check("moi bai doc deu KHAI `terms` (%d bai)" % len(arts),
          not khong_khai and len(arts) > 0, "khong khai: %s" % khong_khai[:6])
    # Bat bien THAT: bai nao khong nam trong danh sach mien tru thi `terms` phai
    # co it nhat mot khoa. Day la cho bat mot bai MOI them ma quen noi.
    ngoai_ds = [k for k in rong if k not in MIEN_TERMS]
    check("moi bai NGOAI `MIEN_TERMS` co `terms` khong rong",
          not ngoai_ds, "rong ma khong duoc mien: %s" % ngoai_ds[:6])
    # Ky luat teo lai: noi `terms` roi thi phai xoa slug khoi `MIEN_TERMS`.
    da_noi = sorted(k for k in MIEN_TERMS if _map.get(k))
    check("`MIEN_TERMS` con DUNG (noi roi thi phai xoa khoi ds)",
          not da_noi, "da co terms, xoa khoi MIEN_TERMS: %s" % da_noi[:6])
    thua = sorted(k for k in MIEN_TERMS if k not in _map)
    check("`MIEN_TERMS` khong chua slug khong ton tai", not thua, str(thua[:6]))
    print("  ... %d/%d bai co `terms` khong rong · %d bai con mo DE NGAU NHIEN"
          % (day_du, len(arts), len(rong)))

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
