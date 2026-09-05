# -*- coding: utf-8 -*-
"""Doi chieu tung `srcQuote` cua bank cau hoi voi TRANG NGUON THAT.

⚠️⚠️ VI SAO CAN BO NAY — no tu dong hoa mot viec da phai lam bang tay 06/08/2026.
Ra soat Dot 1 cua Gemini tim ra ba muc do sai khac nhau, va CHI muc dau la bat duoc
bang mat thuong:
  ① cau trich KHONG CO tren trang        -> dien giai duoc dat trong ngoac kep
  ② cau trich CO that nhung THUA/THIEU chu (vi du "the Moon and the Sun" trong khi
    trang viet "the Moon and Sun")
  ③ cau trich CO that nhung KHONG chung minh dieu cau hoi khang dinh
     -> bo nay KHONG bat duoc muc ③; do la viec cua nguoi doc. Nhung ① va ② thi
        may lam duoc, va chung la phan ton thoi gian nhat.

⚠️ BAI HOC DO LUONG, tra gia 06/08/2026: lan quet dau tien toi tim chuoi "375" tren
   trang nhat thuc va thay CO -> suyt ket luan con so do co nguon. Hoa ra do la CSS
   `375em`. **Phai boc <script> va <style> TRUOC khi tim**, khong thi moi chuoi so
   deu "co nguon". Trang do chi con 17.103 ky tu van ban that.

⚠️ Chuan hoa dau nhay CONG cong: trang NASA dung dau nhay cong (U+2019) con file JS
   dung dau nhay thang. Khong chuan hoa thi moi cau trich co chu "Earth's" deu bao
   hong oan — va mot phep kiem hay bao oan thi som muon bi bo qua.

Chay: python scratchpad/check_srcquote.py            (kiem bank that)
      python scratchpad/check_srcquote.py --demo     (tu chung minh no co rang)
"""
import io
import re
import sys
import unicodedata
import urllib.request

import os

# ⚠️ NGAN HANG CAU HOI NAY LA NHIEU FILE (doi 07/08/2026): bang nguon `S` o
#    `js/quiz-index.js`, con MOI CAU mot file trong `js/quiz/`. Truoc do ca bank
#    nam trong `js/quiz-questions.js`.
INDEX = "js/quiz-index.js"
QDIR = "js/quiz"
OK = FAIL = 0
_cache = {}


def check(cond, label, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"    [OK]   {label} {extra}")
    else:
        FAIL += 1
        print(f"    [HONG] {label} {extra}")


def norm(t):
    """Ve mot dang so sanh duoc: bo dau nhay cong, gach dai, khoang trang thua."""
    t = unicodedata.normalize("NFKC", t)
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), (" ", " ")]:
        t = t.replace(a, b)
    # ⚠️ QUY MOI DAU GACH NGANG VE HYPHEN — bay lan thu hai, 06/08/2026.
    #    Bang tren ban dau chi co – (U+2013) va — (U+2014). Trang NASA `moon/eclipses/`
    #    lai dung ― (U+2015 HORIZONTAL BAR): "Colors with shorter wavelengths ― the
    #    blues and violets ― scatter more easily…". Cau trich DUNG se bao HONG.
    #    ⚠️ `unicodedata.normalize("NFKC")` **KHONG** quy dau gach ve hyphen — dung
    #       tuong no lo giup. Cung ho voi ca `Boötes`: mot ky tu la trong nguon lam
    #       phep kiem to oan cho mot cau CO THAT, va do la loi te nhat no co the mac.
    for _d in "‐‑‒–—―−":
        t = t.replace(_d, "-")
    t = re.sub(r"\s+", " ", t)
    # ⚠️ BOC THE HTML DE LAI KHOANG TRANG TRUOC DAU CAU. Trang nhat thuc cho ra
    #    "…full moon phase ." vi dau cham nam trong mot the rieng — nen cau trich
    #    DUNG "…full moon phase." bao hong OAN. Do la loi te nhat mot phep kiem co
    #    the mac (bai hoc da ghi: phep kiem hay bao oan thi som muon bi bo qua).
    t = re.sub(r"\s+([.,;:!?])", r"\1", t)
    return t.strip().lower()


def page_text(url):
    """Tai trang, BOC <script>/<style> roi tra ve van ban da chuan hoa."""
    if url in _cache:
        return _cache[url]
    # ⚠️ USER-AGENT PHAI LA CHUOI CHROME DAY DU. Do 06/08/2026: exploratorium.edu tra
    #    403 voi "Mozilla/5.0 AstroQ-check" va voi ca "Mozilla/5.0" tron, nhung tra 200
    #    voi chuoi Chrome day du. De chuoi ngan thi bo kiem bao 4 cau CO THAT la "khong
    #    mo duoc trang" — bao oan, va mot phep kiem hay bao oan thi som muon bi bo qua.
    #    ⚠️ Cung mot loi nay co O HAI FILE: da sua `check_quiz_bank.py` truoc, roi quen
    #       ban sao o day. Sua mot loi thi di tim het cac ban sao cua no.
    # ⚠️⚠️ KHONG GHIM MOT USER-AGENT — do 05/09/2026 thi KHONG CO chuoi nao
    #    dung cho moi ten mien nguon, va HAI CHIEU DEU CO THAT CUNG LUC:
    #      · exploratorium.edu : UA tron -> 403 · chuoi Chrome day du -> 200
    #      · ai4k12.org       : UA tron -> 200 · chuoi Chrome day du -> 403
    #    Ghi chu cu (23/08/2026) viet 'ai4k12 tra 403 voi bo tai tu dong nhung 200
    #    voi UA Chrome day du' — NAY DA NGUOC LAI; trang doi bo loc bot, va mot ghi
    #    chu noi sai ve mang con te hon khong co ghi chu. [Suy luan] 'Chrome/120' nay
    #    da qua cu nen chinh no thanh dau hieu bot gia mao.
    # ⚠️ Day KHONG phai noi long: dieu can bao dam (URL nguon con SONG) giu nguyen,
    #    chi thoi ghim MOT cach goi. Bao hong khi va chi khi MOI cach deu that bai.
    _UAS = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "curl/8.4.0",
    )
    raw = None
    _err = None
    for _ua in _UAS:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": _ua, "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode("utf-8", "replace")
            break
        except Exception as e:  # noqa: BLE001
            _err = e
    if raw is None:
        raise _err
    # ⚠️ Boc script/style TRUOC — day la ca "375em" da lam toi doc sai mot lan.
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    import html as _h
    txt = norm(_h.unescape(raw))
    _cache[url] = txt
    return txt


def source_table(path=INDEX):
    """Bang nguon `S` o muc luc: khoa -> url. Cau hoi tro vao day bang KHOA
    (`src: "star"`), KHONG viet URL — 870 cau viet URL thang la ~870 ban sao cua
    ~40 dia chi, va ngay NASA doi mot duong dan thi phai sua hang tram file."""
    s = io.open(path, encoding="utf-8").read()
    # ⚠️ DOC CA HAI DANG KHAI, giu tu ban truoc: bang goc dung `khoa: { …url… }`,
    #    con Dot 1 THEM khoa bang `S.khoa = { …url… };`. Chi doc dang dau thi 20
    #    khoa cua Dot 1 bien mat va bo kiem bao 65 cau "co srcQuote nhung KHONG co
    #    src" — bao oan tron mot dot noi dung.
    tbl = dict(re.findall(r'(\w+):\s*\{[^}]*url:\s*"([^"]+)"', s))
    tbl.update(dict(re.findall(r'S\.(\w+)\s*=\s*\{[^}]*url:\s*"([^"]+)"', s)))
    return tbl


def read_bank(qdir=QDIR, index=INDEX):
    """Tra ve [(term, url, quote)] cho moi cau CO `srcQuote`.
    Doc MOT FILE MOI CAU trong `js/quiz/` — ten file la khoa cau."""
    tbl = source_table(index)
    out = []
    if not os.path.isdir(qdir):
        return out
    for fn in sorted(f for f in os.listdir(qdir) if f.endswith(".js")):
        blk = io.open(os.path.join(qdir, fn), encoding="utf-8").read()
        q = re.search(r'srcQuote:\s*"([^"]*)"', blk)
        if not q:
            continue
        term = os.path.splitext(fn)[0]      # ten file LA khoa cau
        # `src: "khoa"` la dang chuan; van cho phep URL thang de bo kiem con bat
        # duoc ca truong hop ai do viet sai luat (check_pages [12] bao hong rieng).
        k = re.search(r'\bsrc:\s*"([^"]+)"', blk)
        raw = k.group(1) if k else None
        url = None
        if raw:
            url = raw if raw.startswith("http") else tbl.get(raw)
        out.append((term, url, q.group(1)))
    return out


def verify(rows):
    if not rows:
        print("  (bank chua co cau nao mang `srcQuote` — chua co gi de doi chieu)")
        print("  Chay `--demo` de xem bo nay co rang hay khong.")
        return
    for term, url, quote in rows:
        if not url:
            check(False, f"{term}: co `srcQuote` nhung KHONG co `src`")
            continue
        if not quote.strip():
            check(False, f"{term}: `srcQuote` rong")
            continue
        try:
            txt = page_text(url)
        except Exception as e:
            check(False, f"{term}: khong mo duoc {url}", str(e)[:60])
            continue
        check(norm(quote) in txt, f"{term}: cau trich CO tren trang",
              "" if norm(quote) in txt else f'"{quote[:58]}…"')


def demo():
    """Tu chung minh: hai cau trich THAT cua Gemini, mot dung mot dien giai."""
    print("\n=== DEMO — hai cau trich co that tu Dot 1 cua Gemini ===")
    url = "https://science.nasa.gov/moon/eclipses/"
    thuc = "Lunar eclipses occur at the full Moon phase."
    dien_giai = "The remaining light reflects onto the Moon's surface with a red glow"
    try:
        txt = page_text(url)
    except Exception as e:
        print("  khong mo duoc trang:", e)
        return
    check(norm(thuc) in txt, "cau trich THAT -> phep kiem noi CO")
    check(norm(dien_giai) not in txt,
          "cau DIEN GIAI (eclipse-05) -> phep kiem noi KHONG CO  ← day la cai no bat")


if __name__ == "__main__":
    print("=== DOI CHIEU srcQuote VOI TRANG NGUON ===")
    verify(read_bank())
    if "--demo" in sys.argv:
        demo()
    print(f"\n=== KET QUA: {OK} dat / {FAIL} hong ===")
    sys.exit(1 if FAIL else 0)
