# -*- coding: utf-8 -*-
"""probe_rock_art.py — anh thien thach xam DUNG CHUNG o ba game.

VI SAO CO BO DO NAY (22/08/2026)
--------------------------------
Chu du an: *"thay tat ca hinh anh thien thach xam trong cac game dang co bang
hinh anh thien thach xam moi thay cua duong dua sao chom"*.

Truoc do: `game-racer.html` dung art (`img/racer/rock.png`), con `game-dodge.html`
va `game-defender.html` VE BANG CODE (gradient #8291b0 + da giac gồ ghề). Anh
nay chuyen sang `img/rock-gray.png` va ca ba game dung chung.

HAI DIEU PHAI DO, va `grep` mu voi ca hai:
  [A] Anh co THAT SU duoc ve khong — `loadArt` chi bat `ok` khi anh decode xong,
      nen anh 404 thi game lui ve ban vector KHONG LOI KHONG CANH BAO. Do bang
      cach dem pixel trong mot cua so quanh vien da, roi so voi luot CHAN anh.
  [B] Co doi do kho khong — hop ve phai giu quan he "hinh ve <-> vong va cham"
      nhu ban vector. Do bang chinh hang so trong file.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/probe_rock_art.py
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

# So do tren img/rock-gray.png (248x256) — ban kinh silhouette / canh dai.
# Sinh lai bang khoi do o dau script nay (xem README cua muc nhat ky).
R_MIN, R_MED, R_MAX = 0.4062, 0.4570, 0.5117

_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [HONG] ") + name
          + (("  [" + str(extra) + "]") if extra else ""))


def num(src, pat):
    m = re.search(pat, src)
    return float(m.group(1)) if m else None


# ══════════════════════════════════════════════════════════════════════
def static_checks():
    print("=== [1] MOT ANH, BA GAME — va no khong con nam trong thu muc cua racer ===")
    chk("img/rock-gray.png ton tai", (ROOT / "img" / "rock-gray.png").exists())
    chk("img/racer/rock.png da doi cho", not (ROOT / "img" / "racer" / "rock.png").exists())
    for g in ("game-racer.html", "game-dodge.html", "game-defender.html"):
        src = (ROOT / g).read_text(encoding="utf-8")
        chk(g + ": tro dung img/rock-gray.png", "img/rock-gray.png" in src)
        chk(g + ": khong con tro img/racer/rock.png", "img/racer/rock.png" not in src)
    bd = (ROOT / "scratchpad" / "bundle_racer.py").read_text(encoding="utf-8")
    chk("bundle_racer.py doi duong dan o CA hai danh sach (ASSETS + INLINE)",
        bd.count('"img/rock-gray.png"') == 2 and "img/racer/rock.png" not in bd,
        bd.count('"img/rock-gray.png"'))

    print("\n=== [2] BO NAP ART DUNG CHUNG, khong ba ban sao ===")
    gs = (ROOT / "js" / "game-shell.js").read_text(encoding="utf-8")
    chk("game-shell.js co loadArt", "function loadArt(" in gs)
    chk("game-shell.js co drawArt", "function drawArt(" in gs)
    chk("drawArt nhan ctx lam tham so (file dung chung, khong co canvas rieng)",
        "function drawArt(ctx," in gs)
    chk("xuat ca hai qua AstroQGameShell",
        "loadArt: loadArt" in gs and "drawArt: drawArt" in gs)
    rc = (ROOT / "game-racer.html").read_text(encoding="utf-8")
    chk("racer KHONG con ban sao loadArt rieng",
        "var box={ img:null, ok:false, ar:1 };" not in rc)
    chk("racer goi bo nap dung chung", "AstroQGameShell.loadArt(path)" in rc)

    print("\n=== [3] DOI ART, KHONG DOI DO KHO ===")
    # dodge: hop = rockBox * rc ; ban vector: 0,84..1,08 * r, va rc = rockHit * r
    dg = (ROOT / "game-dodge.html").read_text(encoding="utf-8")
    box_d = num(dg, r"rockBox:\s*([\d.]+)")
    hit_d = num(dg, r"rockHit:\s*([\d.]+)")
    chk("dodge: doc duoc rockBox + rockHit", box_d is not None and hit_d is not None,
        "%s / %s" % (box_d, hit_d))
    if box_d and hit_d:
        art_lo, art_hi = R_MIN * box_d, R_MAX * box_d          # theo don vi rc
        vec_lo, vec_hi = 0.84 / hit_d, 1.08 / hit_d            # ban vector, theo rc
        chk("dodge: dai hinh ve gan trung ban vector (lech <8%)",
            abs(art_lo - vec_lo) < 0.08 and abs(art_hi - vec_hi) < 0.08,
            "art %.3f-%.3f vs vector %.3f-%.3f (x rc)" % (art_lo, art_hi, vec_lo, vec_hi))
        # Va cham la VONG TRON: hinh phai PHU vong do, khong duoc nam sau ben trong.
        chk("dodge: hinh PHU vong va cham (min >= 0,95 rc)", art_lo >= 0.95,
            "min = %.3f rc" % art_lo)
    # defender: hop = ROCK_BOX * r ; ban vector 0,82..1,18 * r
    df = (ROOT / "game-defender.html").read_text(encoding="utf-8")
    box_f = num(df, r"var ROCK_BOX\s*=\s*([\d.]+)")
    chk("defender: doc duoc ROCK_BOX", box_f is not None, box_f)
    if box_f:
        a_lo, a_hi = R_MIN * box_f, R_MAX * box_f
        chk("defender: trung binh dai hinh ve gan ban vector (lech <8%)",
            abs((a_lo + a_hi) / 2 - 1.0) < 0.08,
            "art %.3f-%.3f vs vector 0.820-1.180 (x r)" % (a_lo, a_hi))
    chk("KHONG doi mot hang so va cham nao",
        hit_d == 0.86 and "r:20," in df, "rockHit=%s" % hit_d)

    print("\n=== [4] DUONG LUI PHAI CON (anh 404 -> van co da tren san) ===")
    for g, mark in (("game-dodge.html", "createRadialGradient(-a.r*0.32"),
                    ("game-defender.html", "createRadialGradient(-f.r*0.32")):
        chk(g + ": con ban ve vector lam duong lui",
            mark in (ROOT / g).read_text(encoding="utf-8"))
    chk("defender: vet nut ve SAU ca hai nhanh (tin hieu 'sap vo' khong bi mat)",
        df.find("ART_ROCK.ok") < df.find("if(f.hp===1)"))


# ══════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════
# ⚠️ VA `drawImage` DE DEM, KHONG DOAN THEO MAU PIXEL.
#    Ca anh moi va ban vector cu deu la khoi xam-lam, nen khong co dai mau nao
#    tach bach duoc hai duong ve. Dem loi goi ve anh thi tra loi truc tiep:
#      - co bao nhieu vien da duoc ve BANG ANH,
#      - va ve o co bao nhieu (de doi chieu voi hop mong doi).
HOOK = """
window.__rock = { n:0, sizes:[] };
(function(){
  var proto = CanvasRenderingContext2D.prototype;
  var orig = proto.drawImage;
  proto.drawImage = function(img){
    try{
      var src = (img && img.src) || "";
      if (src.indexOf("rock-gray.png") >= 0 && arguments.length >= 5) {
        window.__rock.n++;
        if (window.__rock.sizes.length < 400)
          window.__rock.sizes.push(Math.max(arguments[3], arguments[4]));
      }
    }catch(e){}
    return orig.apply(this, arguments);
  };
})();
"""

# Dem pixel KHONG-phai-nen tren ca canvas — de chung minh duong lui co ve gi.
INK = """() => {
  const cv = document.querySelector('canvas');
  const d = cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
  let n = 0;
  for (let i = 0; i < d.length; i += 4) {
    if (d[i] > 60 && d[i+1] > 60 && d[i+2] > 60) n++;
  }
  return n;
}"""


def run_game(br, game, block):
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh",
                         viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','99');")
    ctx.add_init_script(HOOK)
    if block:
        # ⚠️ Tra 404 chu KHONG `abort()`: abort lam trinh duyet TU ghi mot dong do
        #    vao console, va phep kiem "0 loi trang" se bao oan.
        ctx.route("**/rock-gray.png", lambda r: r.fulfill(status=404, body=""))
    pg = ctx.new_page()
    perr = []
    pg.on("pageerror", lambda e: perr.append(str(e)))
    pg.goto(BASE + "/" + game, wait_until="load")
    pg.wait_for_selector("#start-btn", timeout=8000)
    pg.click("#start-btn")
    pg.wait_for_timeout(3500)          # du de vai vien da vao san
    out = {
        "n": pg.evaluate("() => window.__rock.n"),
        "sizes": pg.evaluate("() => window.__rock.sizes.slice(0,200)"),
        "ink": pg.evaluate(INK),
        "perr": perr[:],
    }
    ctx.close()
    return out


def browser_checks():
    print("\n=== [5] ANH CO THAT SU DUOC VE KHONG (va `drawImage`, khong doan mau) ===")
    exp = {"game-dodge.html": None, "game-defender.html": None}
    dg = (ROOT / "game-dodge.html").read_text(encoding="utf-8")
    df = (ROOT / "game-defender.html").read_text(encoding="utf-8")
    box_d, hit_d = num(dg, r"rockBox:\s*([\d.]+)"), num(dg, r"rockHit:\s*([\d.]+)")
    rr_d = [float(x) for x in re.search(r"rockR:\s*\[(\d+),\s*(\d+)\]", dg).groups()]
    bg_d = [float(x) for x in re.search(r"bigR:\s*\[(\d+),\s*(\d+)\]", dg).groups()]
    box_f = num(df, r"var ROCK_BOX\s*=\s*([\d.]+)")
    r_f = num(df, r"gray\s*:\s*\{\s*hp:2,\s*r:(\d+)")
    # Canh hop mong doi (contain vao hop vuong -> canh DAI = canh hop).
    exp["game-dodge.html"] = (rr_d[0] * hit_d * box_d, bg_d[1] * hit_d * box_d)
    exp["game-defender.html"] = (r_f * box_f, r_f * box_f)

    with sync_playwright() as p:
        br = p.chromium.launch()
        for game in ("game-dodge.html", "game-defender.html"):
            a = run_game(br, game, False)
            b = run_game(br, game, True)
            chk(game + ": ANH duoc ve that (dem loi goi drawImage)", a["n"] > 0, a["n"])
            chk(game + ": chan anh -> 0 loi goi ve anh (duong lui da chay)",
                b["n"] == 0, b["n"])
            chk(game + ": chan anh -> san VAN co vat the (duong lui ve gi do)",
                b["ink"] > 2000, b["ink"])
            lo, hi = exp[game]
            if a["sizes"]:
                mn, mx = min(a["sizes"]), max(a["sizes"])
                chk(game + ": co ve nam trong dai mong doi",
                    mn >= lo * 0.92 and mx <= hi * 1.08,
                    "ve %.0f-%.0f px, mong doi %.0f-%.0f" % (mn, mx, lo, hi))
            else:
                chk(game + ": co ve nam trong dai mong doi", False, "0 mau")
            chk(game + ": 0 loi trang (co anh)", not a["perr"], "; ".join(a["perr"][:2]))
            chk(game + ": 0 loi trang (chan anh)", not b["perr"], "; ".join(b["perr"][:2]))
        br.close()


def main():
    static_checks()
    browser_checks()
    print("\n=== KET QUA: %d dat / %d hong ===" % (_n["ok"], _n["ng"]))
    return 1 if _n["ng"] else 0


if __name__ == "__main__":
    sys.exit(main())
