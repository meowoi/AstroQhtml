# -*- coding: utf-8 -*-
"""Do tren BAN THAT (astroq.org) sau luot push 22/08/2026 lan hai.

Luot nay mang bon viec: ghim co ba tau doi thu theo DIEN TICH · noi `terms` cho
5 bai doc · cong push thoi bao oan · hai bo do nay do duoc (chi la file test,
khong len ban that).

⚠️⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC, VA DUNG HAN NEU LECH. Pages build
   ~45 giay; do truoc luc build xong thi moi ket luan sau do noi ve BAN CU. Ngay
   06/08/2026 ban that dung o ban 04/08 gan mot ngay.

⚠️ HA CHU THUONG MOI KHOA HEADER truoc khi doc (bai hoc 18/08: API Gateway ha
   chu thuong moi ten header, `dict(r.headers)` lam mat tinh khong-phan-biet-hoa-thuong).

Chay:  python scratchpad/verify_prod_0822c.py
"""
import io
import re
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
WANT_VER = "2026.08.22.3"
dat = hong = 0


def check(nhan, dk, ct=""):
    global dat, hong
    if dk:
        dat += 1
        print("  [OK]   " + nhan + (("  (" + ct + ")") if ct else ""))
    else:
        hong += 1
        print("  [HONG] " + nhan + (("  (" + ct + ")") if ct else ""))


def get(path):
    """Tra (ma, than, headers-chu-thuong). Khong nem loi ra ngoai."""
    req = urllib.request.Request(SITE + path, headers={"User-Agent": "astroq-verify"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            hdr = {k.lower(): v for k, v in r.headers.items()}
            return r.status, r.read().decode("utf-8", "replace"), hdr
    except Exception as e:
        return getattr(e, "code", 0), "", {}


# ════════════════════════════════════════════════════════════════════════════
print("\n=== [0] SO HIEU BAN DUNG (dung han neu lech) ===")
code, body, _ = get("/js/ui-common.js")
m = re.search(r'var VERSION = "([^"]+)"', body)
got = m.group(1) if m else "?"
print("   ban that: %s   mong: %s" % (got, WANT_VER))
if got != WANT_VER:
    print("\n⛔ SO HIEU LECH — Pages chua build xong hoac push chua len.")
    print("   DUNG HAN: moi phep do sau day se noi ve BAN CU.")
    sys.exit(2)
check("so hieu ban dung dung " + WANT_VER, True)

# ── [1] Cong thuc ghim co: dien tich, khong phai chieu dai ───────────────────
print("\n=== [1] game-racer.html: ghim theo DIEN TICH ===")
code, racer, hdr = get("/game-racer.html")
check("game-racer.html tra 200", code == 200, "ma %s" % code)
check("co cong thuc ghim DIEN TICH", "Math.sqrt(A0*sp.ar)" in racer)
check("co hang so moc A0 = shipW*shipH",
      "var A0=CONFIG.shipW*CONFIG.shipH" in racer)
# ⚠️ Cong thuc CU phai bien han — con no nghia la Pages phuc vu ban cu.
check("KHONG con cong thuc ghim CHIEU DAI",
      "bw=useArt?CONFIG.shipW" not in racer)
# ⚠️ Moc PHAI la hang so, KHONG duoc la SPR (phu thuoc anh Luna da tai xong chua).
# ⚠️⚠️ QUET TREN BAN DA BOC CHU THICH. Ban dau phep kiem nay quet van ban THO
#   nen no bat trung chinh khoi ⚠️ giai thich VI SAO khong duoc dung SPR —
#   bao hong trong khi ma nguon hoan toan dung. Loi "dem ca chu trong ghi chu
#   cua chinh minh" da lap ~20 lan trong du an; moi phep kiem dang "khong
#   duoc chua X" phai bo chu thich truoc.
racer_code = re.sub(r"/\*.*?\*/", " ", racer, flags=re.S)
check("moc KHONG dung SPR.w*SPR.h", "SPR.w*SPR.h" not in racer_code)

# ── [2] Nam file bai mang `terms` len ban that ────────────────────────────────
print("\n=== [2] Nam bai doc mang `terms` ===")
LOADING = "Đang tải câu hỏi"   # ⚠️ chuoi giu cho cua quiz.html


def chuan(x):
    """Bo the HTML + gom khoang trang, de so chu tren man voi chu trong file."""
    x = re.sub(r"<[^>]+>", "", x or "")
    return re.sub(r"\s+", " ", x).strip()


def cau_hoi_cua(key):
    """Doc CHU cua cau hoi (vi + en) THANG tu js/quiz/<khoa>.js tren ban that.

    ⚠️ Doc tu file thay vi doc bien trong trang: `quiz.html` giu `QUESTIONS`
       trong IIFE nen ngoai khong voi toi (gioi han da ghi cho shot_sprites.py).
    """
    _c, src, _h = get("/js/quiz/%s.js" % key)
    m = re.search(r"q:\s*\{(.*?)\}", src, re.S)
    if not m:
        return set()
    return {chuan(x) for x in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))}


NOI = {
    "lib-blackhole": ["black-hole-light"],
    "lib-exoplanet": ["exoplanet", "exoplanet-transit"],
    "lib-nebula": ["nebula"],
    "art-microgravity-is-falling": ["gravity-distance"],
    "art-code-written-before-launch": ["sequence"],
}
for slug, keys in NOI.items():
    code, src, hdr = get("/js/article/%s.js" % slug)
    ok = code == 200
    # ⚠️ ES module bi tu choi neu server tra text/plain — phai DO chu khong gia dinh.
    mime = hdr.get("content-type", "")
    check("%s: 200 + MIME javascript" % slug,
          ok and "javascript" in mime, "ma %s, mime %s" % (code, mime[:34]))
    if ok:
        m2 = re.search(r"terms:\s*\[([^\]]*)\]", src)
        got_keys = re.findall(r'"([^"]+)"', m2.group(1)) if m2 else []
        check("%s: terms = %s" % (slug, keys), got_keys == keys, "thay %s" % got_keys)

# ⚠️ Muc luc KHONG chua `terms` — noi `terms` thi khong phai sinh lai muc luc.
code, idx, _ = get("/js/articles-index.js")
check("muc luc tra 200", code == 200, "ma %s" % code)

# ── [3] Do THAT tren trinh duyet ─────────────────────────────────────────────
VA = """
window.__sz = {};
const orig = CanvasRenderingContext2D.prototype.drawImage;
CanvasRenderingContext2D.prototype.drawImage = function(img, dx, dy, dw, dh){
  try {
    const s = (img && (img.currentSrc || img.src)) || '';
    const m = s.match(/\\/(rival-[a-z]+|luna-side)\\.png/);
    if (m && typeof dw === 'number' && typeof dh === 'number') {
      window.__sz[m[1]] = { w: +dw.toFixed(2), h: +dh.toFixed(2) };
    }
  } catch(e) {}
  return orig.apply(this, arguments);
};
"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','999');")
    errs, bad = [], []
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: bad.append("%s %s" % (r.status, r.url))
          if r.status >= 400 else None)
    pg.add_init_script(VA)

    print("\n=== [3] Co ba tau doi thu TREN BAN THAT ===")
    pg.goto(SITE + "/game-racer.html", wait_until="load")
    pg.wait_for_timeout(700)
    pg.click("#start-btn")
    pg.wait_for_timeout(2600)
    sz = pg.evaluate("() => window.__sz")
    for k in sorted(sz):
        d = sz[k]
        print("   %-14s %6.2f x %-6.2f  ti le %.3f  dien tich %7.1f"
              % (k, d["w"], d["h"], d["w"] / d["h"], d["w"] * d["h"]))
    check("do duoc ca 3 doi thu + Luna",
          len([k for k in sz if k.startswith("rival-")]) == 3 and "luna-side" in sz,
          "thay %s" % sorted(sz))
    if "luna-side" in sz and len([k for k in sz if k.startswith("rival-")]) == 3:
        a0 = sz["luna-side"]["w"] * sz["luna-side"]["h"]
        for k in sorted(k for k in sz if k.startswith("rival-")):
            d = sz[k]
            ti = (d["w"] * d["h"]) / a0
            check("%s: ~ bang dien tich Luna" % k, 0.92 <= ti <= 1.08,
                  "%.0f%%" % (ti * 100))
            check("%s: khong dai qua 1,35x Luna" % k,
                  d["w"] <= sz["luna-side"]["w"] * 1.35,
                  "dai %.1f / %.1f" % (d["w"], sz["luna-side"]["w"]))
    check("0 loi trang o game-racer", not errs, "; ".join(errs[:2]))
    check("0 tai nguyen hong o game-racer", not bad, "; ".join(bad[:2]))

    # ── [4] Nut "Lam Quiz bai nay" dan sang dung cau ─────────────────────────
    print("\n=== [4] Nut quiz cua bai doc dan dung cau (ban that) ===")
    for slug, keys in [("lib-exoplanet", ["exoplanet", "exoplanet-transit"]),
                       ("art-code-written-before-launch", ["sequence"])]:
        errs.clear()
        bad.clear()
        pg.goto(SITE + "/library.html?a=" + slug, wait_until="load")
        pg.wait_for_timeout(1100)
        try:
            pg.wait_for_selector("#r-quiz", state="visible", timeout=12000)
        except Exception:
            check("%s: nut quiz hien ra" % slug, False, "url=%s" % pg.url)
            continue
        with pg.expect_navigation(timeout=20000):
            pg.click("#r-quiz")
        url = pg.url
        check("%s: URL mang dung terms" % slug,
              "terms=" in url and all(k in url for k in keys),
              url.split("?")[-1][:70])
        pg.wait_for_selector("#q-text", timeout=20000)
        # ⚠️⚠️ CHO CHU KHAC CHUOI GIU CHO. Ban dau phep kiem chi doi len>12 nen
        #   no NHAN "Dang tai cau hoi…" lam bang chung cau hoi da hien — mot
        #   phep kiem dat mot cach RONG. Cau hoi tai bang import() nen phai cho
        #   tin hieu THAT, dung ngu mot khoang co dinh.
        try:
            pg.wait_for_function(
                "ph => { const e = document.getElementById('q-text');"
                " return e && e.textContent.trim().length > 12"
                " && e.textContent.indexOf(ph) < 0; }",
                arg=LOADING, timeout=20000)
        except Exception:
            pass
        txt = chuan(pg.eval_on_selector("#q-text", "e => e.innerHTML"))
        check("%s: cau hoi KHONG con la chuoi giu cho" % slug,
              len(txt) > 12 and LOADING not in txt, txt[:56])
        mong = set()
        for k in keys:
            mong |= cau_hoi_cua(k)
        # ⚠️ Chi doi "cau dang hien nam trong bo cau cua bai" — luot co the bat
        #    dau tu BAT KY cau nao trong `terms`, dung ghim mot cau cu the.
        check("%s: cau dang hien thuoc dung bo terms" % slug,
              bool(mong) and txt in mong, "hien=%r" % txt[:52])
        check("%s: 0 loi trang" % slug, not errs, "; ".join(errs[:2]))

    # ── [5] Bai CHUA co terms van mo quiz THUONG ──────────────────────────────
    errs.clear()
    pg.goto(SITE + "/library.html?a=jwst", wait_until="load")
    pg.wait_for_timeout(1100)
    pg.wait_for_selector("#r-quiz", state="visible", timeout=12000)
    with pg.expect_navigation(timeout=20000):
        pg.click("#r-quiz")
    check("bai chua co terms: mo quiz THUONG, khong bi chan",
          "quiz.html" in pg.url and "terms=" not in pg.url,
          pg.url.split("/")[-1][:56])
    check("0 loi trang o duong quiz thuong", not errs, "; ".join(errs[:2]))

    ctx.close()
    b.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
