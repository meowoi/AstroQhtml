# -*- coding: utf-8 -*-
"""check_specimen_art.py — 21 MAU VAT VE BANG SVG, moi may hien y het nhau.

VI SAO CO BO DO NAY (21/08/2026)
--------------------------------
Chu du an choi tren Mac roi choi tren PC Windows va gui hai anh chup cung mot
trang: *"vi sao co su khac biet giua hinh anh cac mau vat?"* + *"Vi du Tinh the
bang do sao lai mau xanh?"*

Nguyen nhan: `js/specimens.js` khai moi mau vat bang MOT KY TU EMOJI, ma emoji
KHONG phai mot hinh — no la mot ky tu, va **moi he dieu hanh ve no bang phong
chu cua rieng minh** (Apple Color Emoji / Segoe UI Emoji / Noto Color Emoji).
Khong tuy chon CSS nao chua duoc. Emoji con noi SAI noi dung: mau `mars-red-ice`
dung 💎 (kim cuong XANH) cho bang H2O nhuom bui oxit sat (phai DO HONG).

Cach chua: tu ve 21 buc SVG (`js/specimen-art.js`). Bo do nay canh ba chuyen ma
`grep` khong tra loi duoc:

  [1] MOI mau vat trong `js/specimens.js` deu co tranh, va khong co tranh du.
  [2] Tranh la SVG THAT tren TRANG THAT (khong con emoji tho o o hien thi),
      va no do cO theo `font-size` cua o chua o ca ba co: 19px / 46px / 96px.
  [3] KHONG chuoi `<svg>` nao bi in ra thanh CHU (`esc()` nham la loi im lang:
      trang van chay, chi hien mot dong markup cho tre doc).
  [4] Duong lui con nguyen: chua nap `js/specimen-art.js` thi `icon()` tra emoji.

  python -m http.server 8123    (trong AstroQhtml/)
  python scratchpad/check_specimen_art.py
"""
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"

LOG = []


def ok(name, cond, extra=""):
    """Ghi MOT phep kiem, VA IN NGAY.

    CANH BAO (quy tac 6 muc 6 cua CLAUDE.md): dung don log de in o cuoi. Ban dau
    cua bo do nay in het o cuoi `main()`, nen mot ngoai le giua duong (mot phep
    `wait_for_selector` het han) lam MAT SACH moi phep kiem da chay - va phep thu
    pha hoai doc ra thanh "0 hong", tuc y nhu mot phep kiem mu. Dem ca so PASS
    thi phan biet duoc "dat" voi "khong chay".
    """
    line = ("PASS  " if cond else "FAIL  ") + name + ("  [%s]" % extra if extra else "")
    LOG.append(line)
    print("  " + line, flush=True)


# ── Khung do: mot trang tam nap dung hai file that, khong ban sao ──────────
HARNESS = """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="/css/common.css">
<script src="/js/specimens.js"></script>
<script src="/js/specimen-art.js"></script>
<div id="s19"></div><div id="s46"></div><div id="s96"></div><div id="dup"></div>
<style>#s19{font-size:19px}#s46{font-size:46px}#s96{font-size:96px}</style>
<script>
window.__ids = AstroQSpecimenArt.ids();
["19","46","96"].forEach(function(px){
  document.getElementById("s"+px).innerHTML = window.__ids.map(function(id){
    return '<span class="sp">' + AstroQSpecimens.icon(id) + '</span>';
  }).join("");
});
/* Ve CUNG MOT mau vat HAI LAN: day moi la canh that (mot ban o khoang + mot ban
   o man soi), va la canh DUY NHAT lam id gradient trung nhau. Ve 21 mau vat khac
   nhau thi id van duy nhat du hau to bi ghim, vi moi mau dung mot tien to rieng
   (`sw`/`co`/`ic`...) - do la ly do phep kiem dau cua bo do nay bo lot phep pha. */
document.getElementById("dup").innerHTML =
  AstroQSpecimens.icon("mars-red-ice") + AstroQSpecimens.icon("mars-red-ice");
</script>"""

# Khung do duong lui: CO Y khong nap js/specimen-art.js
HARNESS_NOART = """<!doctype html><meta charset="utf-8">
<script src="/js/specimens.js"></script>
<script>window.__ico = AstroQSpecimens.icon("mars-red-ice");</script>"""


def no_comments(js):
    """Boc chu thich JS, GIU nguyen chuoi.

    CANH BAO: moi phep kiem dang "KHONG duoc chua X" phai chay tren ban da boc
    chu thich. Lan chay dau cua bo do nay hong dung 2 phep kiem, va thu pham la
    chinh loi canh bao o dau `js/specimen-art.js` ("KHONG CO FILTER", "KHONG
    style= trong SVG") - loi "dem ca chu trong ghi chu cua chinh minh" ma
    CLAUDE.md da ghi nhieu lan.
    """
    out, i, n = [], 0, len(js)
    while i < n:
        c = js[i]
        if c in "\"'":
            q = c
            out.append(c)
            i += 1
            while i < n:
                if js[i] == "\\":
                    out.append(js[i:i + 2])
                    i += 2
                    continue
                out.append(js[i])
                if js[i] == q:
                    i += 1
                    break
                i += 1
            continue
        if js.startswith("/*", i):
            i = js.find("*/", i + 2)
            i = n if i < 0 else i + 2
            continue
        if js.startswith("//", i):
            i = js.find(chr(10), i)
            i = n if i < 0 else i
            continue
        out.append(c)
        i += 1
    return "".join(out)


def main():
    art = (ROOT / "js" / "specimen-art.js").read_text(encoding="utf-8")
    spec = (ROOT / "js" / "specimens.js").read_text(encoding="utf-8")

    # ── [1] Phu du 21 mau vat, khong thua khong thieu ──────────────────────
    # `S` cua specimens.js va `ORIGINS` dung CUNG khuon `"id": { ic: "..."`, nen
    # phai cat lay dung khoi `var S = {` chu khong quet ca file.
    i = spec.index("var S = {")
    j = spec.index("\n  };", i)
    sp_ids = set(re.findall(r'"([a-z0-9-]+)":\s*\{\s*\n?\s*ic:', spec[i:j]))
    art_ids = set(re.findall(r'"([a-z0-9-]+)":\s*\{\s*\n\s*defs:', art))
    ok("[1] doc duoc danh muc mau vat", len(sp_ids) > 0, "n=%d" % len(sp_ids))
    ok("[1] moi mau vat deu co tranh", sp_ids <= art_ids, "thieu=%s" % sorted(sp_ids - art_ids))
    ok("[1] khong co tranh du", art_ids <= sp_ids, "du=%s" % sorted(art_ids - sp_ids))

    # ── [1b] Rang buoc cua chinh bo tranh ─────────────────────────────────
    ok("[1b] khung viewBox 0 0 64 64", 'viewBox="0 0 64 64"' in art)
    ok("[1b] co dau `{n}` cho id gradient", "{n}" in art and "replace(/\\{n\\}/g" in art)
    # Moi gradient khai id phai mang `{n}` — id trung thi ban sau "an" gradient
    # cua ban truoc va ca luoi doi mau theo (bai hoc o js/sticker-icons.js).
    gids = re.findall(r'<(?:linear|radial)Gradient id="([^"]+)"', art)
    ok("[1b] moi id gradient deu co `{n}`",
       all("{n}" in g for g in gids), "thieu=%s" % [g for g in gids if "{n}" not in g])
    # Khong filter: 21 khoang x filter = 21 lan rasterize them moi khung hinh,
    # ma `.pod .sp` dang co animation chay lien tuc.
    code = no_comments(art)
    ok("[1b] KHONG dung filter SVG", "feGaussianBlur" not in code and "<filter" not in code)
    # Quy tac 2 muc 1 cua CLAUDE.md: khong style inline.
    ok("[1b] KHONG style= inline trong SVG", 'style="' not in code)

    # ── Do tren trinh duyet ────────────────────────────────────────────────
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("**/__art_probe.html", lambda r: r.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=HARNESS))
        pg.goto(BASE + "/__art_probe.html")
        pg.wait_for_timeout(700)

        n = len(sp_ids)
        for px in ("19", "46", "96"):
            got = pg.eval_on_selector_all("#s%s svg.spart" % px, "e=>e.length")
            ok("[2] co %d tranh SVG o %spx" % (n, px), got == n, "got=%d" % got)
            box = pg.evaluate(
                "(function(){var e=document.querySelector('#s%s svg');var r=e.getBoundingClientRect();"
                "return [Math.round(r.width),Math.round(r.height)];})()" % px)
            ok("[2] tranh %spx do co theo font-size" % px,
               box == [int(px), int(px)], "box=%s" % box)

        # Khong con emoji tho o o hien thi: moi `.sp` phai chua dung mot <svg>
        bare = pg.evaluate(
            "Array.from(document.querySelectorAll('#s46 .sp'))"
            ".filter(function(e){return !e.querySelector('svg');}).length")
        ok("[2] 0 o con emoji tho", bare == 0, "bare=%d" % bare)

        # [3] Khong chuoi <svg> nao bi in thanh CHU
        txt = pg.evaluate("document.getElementById('s46').textContent")
        ok("[3] 0 chuoi `<svg` bi in ra thanh chu", "<svg" not in txt)

        # id gradient duy nhat KHI CUNG MOT MAU VAT VE HAI LAN — xem ghi chu
        # trong HARNESS ve vi sao khong do tren #s46.
        ids = pg.evaluate(
            "Array.from(document.querySelectorAll('#dup linearGradient,#dup radialGradient'))"
            ".map(function(e){return e.id;})")
        ok("[3] cung mot mau vat ve 2 lan -> id gradient KHAC nhau",
           len(ids) > 0 and len(ids) == len(set(ids)),
           "n=%d uniq=%d" % (len(ids), len(set(ids))))
        # Va gradient phai duoc TRO TOI thuc su: `fill="url(#...)"` khop dung id
        # trong CHINH ban do. Trung id thi ban thu hai tro vao gradient cua ban
        # dau — trang khong bao loi, chi hien sai mau.
        linked = pg.evaluate(
            "(function(){var out=[];"
            "Array.from(document.querySelectorAll('#dup svg')).forEach(function(sv){"
            "  var own={}; Array.from(sv.querySelectorAll('[id]')).forEach(function(e){own[e.id]=1;});"
            "  Array.from(sv.querySelectorAll('[fill^=\"url(#\"],[stroke^=\"url(#\"]')).forEach(function(e){"
            "    ['fill','stroke'].forEach(function(k){var v=e.getAttribute(k)||'';"
            r"      var m=v.match(/^url\(#(.+)\)$/); if(m) out.push(!!own[m[1]]);});});});"
            "return out;})()")
        ok("[3] moi `url(#...)` tro vao gradient CUA CHINH ban do",
           len(linked) > 0 and all(linked), "n=%d, sai=%d" % (len(linked), linked.count(False)))
        ok("[3] con dau `{n}` chua thay trong DOM",
           not any("{n}" in i for i in ids))

        ok("[2] 0 loi trang o khung do", not errs, "; ".join(errs[:2]))

        # ── [4] Duong lui: chua nap specimen-art.js thi tra ve emoji ───────
        pg2 = b.new_page()
        e2 = []
        pg2.on("pageerror", lambda e: e2.append(str(e)))
        pg2.route("**/__noart.html", lambda r: r.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=HARNESS_NOART))
        pg2.goto(BASE + "/__noart.html")
        pg2.wait_for_timeout(300)
        ico = pg2.evaluate("window.__ico")
        ok("[4] thieu specimen-art.js -> lui ve emoji, khong vo",
           ico == "\U0001F48E", "ico=%r" % ico)
        ok("[4] 0 loi trang o duong lui", not e2, "; ".join(e2[:2]))

        # ── [5] TRANG THAT: kho mau vat ────────────────────────────────────
        ctx = b.new_context(viewport={"width": 1400, "height": 1000})
        pg3 = ctx.new_page()
        e3 = []
        pg3.on("pageerror", lambda e: e3.append(str(e)))
        pg3.add_init_script("""
          localStorage.clear(); localStorage.setItem('astroq-lang','vi');
          localStorage.setItem('astroq-user', JSON.stringify({uid:'u1',name:'Bin'}));
          Object.defineProperty(window,'AstroQAuth',{configurable:true,
            get:function(){ return {
              postProgress:function(){return Promise.resolve({ok:true,data:{}});},
              getSpecimens:function(){
                var ids = window.AstroQSpecimens.ids();
                var items = ids.map(function(id){ return {id:id, unlocked:true, current:5,
                  goal:5, category:'', rarity:'common', origin:'', metric:'', equipped:false}; });
                return Promise.resolve({ok:true,data:{specimens:{specimens:items,
                  summary:{collected:ids.length,total:ids.length,rare:6,rareTotal:6,deskSlots:3},
                  desk:[], deskHooks:[]}}});
              },
              setSpecimenDesk:function(){return Promise.resolve({ok:true,data:{}});}
            };}, set:function(){}});
        """)
        pg3.goto(BASE + "/specimen-vault.html")
        pg3.wait_for_selector("#pods .pod", timeout=20000)
        pg3.wait_for_timeout(900)
        got = pg3.eval_on_selector_all("#pods .pod .sp svg.spart", "e=>e.length")
        ok("[5] kho mau vat: %d khoang deu co tranh" % n, got == n, "got=%d" % got)
        bare3 = pg3.evaluate(
            "Array.from(document.querySelectorAll('#pods .pod .sp'))"
            ".filter(function(e){return !e.querySelector('svg');}).length")
        ok("[5] kho mau vat: 0 khoang con emoji tho", bare3 == 0, "bare=%d" % bare3)
        pg3.locator("#pods .pod.on").first.click()
        pg3.wait_for_timeout(800)
        sbox = pg3.evaluate(
            "(function(){var e=document.querySelector('.scope .sp svg');if(!e)return null;"
            "var r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)];})()")
        ok("[5] man soi: tranh do co 96px", sbox == [96, 96], "box=%s" % sbox)
        # Tranh nam NGAY TRONG <h2> canh ten -> `inline-block`, ten khong duoc
        # roi xuong dong duoi (do la ly do khong dung display:block).
        same = pg3.evaluate(
            "(function(){var h=document.querySelector('.insp-name');if(!h)return null;"
            "var s=h.querySelector('svg');if(!s)return 'khong co tranh trong h2';"
            "var a=s.getBoundingClientRect();"
            "return Math.abs(a.top - h.getBoundingClientRect().top) < a.height;})()")
        ok("[5] man soi: tranh trong <h2> cung hang voi ten", same is True, "%s" % same)
        ok("[5] 0 loi trang o kho mau vat", not e3, "; ".join(e3[:2]))

        b.close()

    return 0


def summary():
    bad = [l for l in LOG if l.startswith("FAIL")]
    print()
    print("=== KET QUA: %d dat / %d hong ===" % (len(LOG) - len(bad), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as e:
        # HONG GIUA DUONG VAN PHAI TU KHAI: im lang o day la lan sau doc ra
        # thanh "phep kiem mu" (xem ghi chu o `ok`).
        print("  FAIL  bo do HONG GIUA DUONG: %s" % e)
        LOG.append("FAIL  bo do hong giua duong")
        code = 1
    sys.exit(summary() or code)
