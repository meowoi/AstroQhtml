# -*- coding: utf-8 -*-
"""Do luot "tra no noi dung + vai (2)" tren BAN THAT (astroq.org).

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC va DUNG HAN neu sai — do truoc luc
   Pages build xong thi moi ket luan deu sai (06/08/2026 ban that tung dung o ban
   cu gan mot ngay).

⚠️ Bo do nay CO Y KHONG doi `progress.quizLv` co tren API: backend chua deploy
   duoc (quyen bi chan). Nen no do dieu PHAI dung ngay hom nay: ban that rut duoc
   de theo cap khi CO cache, va roi ve "chua biet cap" mot cach an toan khi KHONG.
"""
import io
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

PROD = "https://astroq.org"
WANT = "2026.08.19.2"
dat = hong = 0


def chk(cond, nhan, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))


def get(path):
    req = urllib.request.Request(PROD + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")


print("\n=== [0] So hieu ban dung ===")
_, _, ui = get("/js/ui-common.js")
have = ui.split('var VERSION = "')[1].split('"')[0] if 'var VERSION = "' in ui else "?"
chk(have == WANT, "ban that dang o ban dung %s" % WANT, have)
if have != WANT:
    print("\n>>> DUNG HAN: Pages chua build xong. Cho roi chay lai.")
    sys.exit(1)

print("\n=== [1] Muc luc va cau moi co tren Pages ===")
st, ct, ix = get("/js/quiz-index.js")
chk(st == 200 and "javascript" in ct, "js/quiz-index.js 200 + MIME dung", ct)
chk("function pickKeys(n, lv)" in ix, "muc luc nhan tham so cap do")
chk("function nearest(ks, lv)" in ix, "co duong lui noi sang cap lan can")
_nlv = ix.split("var LV = {")[1].split("};")[0].count(":")
chk(_nlv == 126, "bang LV co du 126 cau", "%d cau" % _nlv)

for k in ("star-mass-life", "bh-not-hole", "sensor-why-autonomous",
          "meteoroid-daily-mass", "ml-trained-by-hubble"):
    try:
        st, _, body = get("/js/quiz/%s.js" % k)
        chk(st == 200 and "srcQuote" in body, "cau moi %s tra 200 + co srcQuote" % k)
    except Exception as e:
        chk(False, "cau moi %s tra 200" % k, str(e))

st, _, pg_ = get("/js/progress.js")
chk("astroq-quiz-lv" in pg_, "js/progress.js co cache cap do")
chk("removeItem(LS_QUIZLV)" in pg_, "dang xuat co don cache cap do")
st, _, qz = get("/quiz.html")
chk("AstroQProgress.quizLv" in qz, "quiz.html doc cap do qua AstroQProgress")
chk("round(ROUND_SIZE, lv)" in qz, "quiz.html truyen cap do vao luot rut")

print("\n=== [2] Mo THAT tren Chromium (ban that) ===")
with sync_playwright() as p:
    b = p.chromium.launch()

    def do(seed, n):
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx.add_init_script(
            "try{localStorage.setItem('astroq-lang','vi');" +
            (("localStorage.setItem('astroq-quiz-lv',%s);" % seed) if seed
             else "localStorage.removeItem('astroq-quiz-lv');") + "}catch(e){}")
        pg = ctx.new_page()
        keys, errs, bad = [], [], []
        pg.on("request", lambda r: keys.append(r.url.rsplit("/", 1)[-1][:-3])
              if "/js/quiz/" in r.url else None)
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad.append("%s %s" % (r.status, r.url))
              if r.status >= 400 else None)
        for _ in range(n):
            pg.goto(PROD + "/quiz.html", wait_until="load")
            pg.wait_for_selector(".q-text", timeout=20000)
        lv = pg.evaluate("() => AstroQQuestions.LV")
        ctx.close()
        return keys, errs, bad, lv

    def dist(keys, lv_of):
        d = {1: 0, 2: 0, 3: 0, 0: 0}
        for k in keys:
            d[lv_of.get(k) or 0] += 1
        return d, (sum(d.values()) or 1)

    # Chua co cache (dung tinh trang HIEN NAY vi backend chua deploy)
    k0, e0, b0, LV = do(None, 8)
    chk(len(k0) == 40 and not e0, "may sach: van rut du de, 0 loi trang",
        "%d cau; %s" % (len(k0), e0[:1]))
    chk(not b0, "0 asset hong", "; ".join(b0[:2]))

    got = {}
    for lv in (1, 2, 3):
        ks, es, bs, _ = do("JSON.stringify({uid:'',lv:%d})" % lv, 20)
        d, t = dist(ks, LV)
        got[lv] = (d, t)
        print("      cap %d -> lv1 %5.1f%%  lv2 %5.1f%%  lv3 %5.1f%%  (%d cau)"
              % (lv, 100.0 * d[1] / t, 100.0 * d[2] / t, 100.0 * d[3] / t, t))
        chk(t == 100 and not es and not bs, "cap %d: du 100 cau, 0 loi, 0 asset hong"
            % lv, "%d cau; %s; %s" % (t, es[:1], bs[:1]))

    # Sau khi lap 20 cho thieu thi duong lui `nearest` khong con phai chay -> DUNG
    # TUYET DOI. Do la ket qua do duoc o may; ban that phai giong.
    for lv in (1, 2, 3):
        d, t = got[lv]
        chk(d[lv] == t, "cap %d: 100%% cau dung cap (khong con phai noi cap)" % lv,
            "%d/%d" % (d[lv], t))

    b.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
