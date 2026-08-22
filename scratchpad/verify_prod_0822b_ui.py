# -*- coding: utf-8 -*-
"""Mo CHINH astroq.org tren Chromium sau lan push 22/08/2026 va do HANH VI.

`verify_prod_0822b.py` chi hoi "file co len khong / chuoi co trong file khong" —
no khong tra loi duoc cau "tre THAT co thay dung khong". Bo nay mo trang that.

Chay:  python scratchpad/verify_prod_0822b_ui.py
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

BASE = "https://astroq.org"
dat = hong = 0


def check(nhan, dk, ct=""):
    global dat, hong
    if dk:
        dat += 1
        print("  [OK]   " + nhan + (("  (" + ct + ")") if ct else ""))
    else:
        hong += 1
        print("  [HONG] " + nhan + (("  (" + ct + ")") if ct else ""))


with sync_playwright() as pw:
    b = pw.chromium.launch()

    def newpage(w=1440, h=900):
        """Trang moi + ghim ngon ngu + gom loi.

        ⚠️ Ghim `astroq-lang`: `AstroQ.getLang()` lui ve `navigator.language`, ma
           Chromium cua Playwright mac dinh `en-US` -> phan "tieng Viet" cua bo do
           lang le chay bang tieng Anh (bai hoc da ghi nhieu lan).
        """
        ctx = b.new_context(viewport={"width": w, "height": h})
        ctx.add_init_script(
            "localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-asteroids','999');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1');"
        )
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("response", lambda r: bad.append("%s %s" % (r.status, r.url))
              if r.status >= 400 else None)
        return ctx, pg, errs, bad

    # ══ [1] GHEP CHOM SAO: man brief GIU LOI HUA ═════════════════════════════
    # Day la loi chu du an gui anh chup: chip HUD ghi "Chom sao Lap Ho", bam Bat
    # dau thi ra "Bo Cap". Do duoc 3/4 luot lech truoc khi sua.
    print("\n=== [1] Ghep Chom Sao: chom o man brief == chom duoc choi ===")
    ctx, pg, errs, bad = newpage()
    lech = []
    for i in range(6):
        pg.goto(BASE + "/game-constellation.html", wait_until="load")
        pg.wait_for_timeout(700)
        brief = pg.eval_on_selector("#hb-name", "e => e.textContent.trim()")
        pg.click("#start-btn")
        pg.wait_for_timeout(700)
        played = pg.eval_on_selector("#hb-name", "e => e.textContent.trim()")
        if brief != played:
            lech.append("luot %d: brief=%r choi=%r" % (i + 1, brief, played))
    check("6/6 luot: ten chom o man brief KHOP chom duoc choi", not lech,
          "; ".join(lech[:3]) if lech else "0 luot lech")
    check("0 loi trang o Ghep Chom Sao", not errs, "; ".join(errs[:2]))
    check("0 tai nguyen hong o Ghep Chom Sao", not bad, "; ".join(bad[:2]))
    ctx.close()

    # ══ [2] PHONG THU: cau do den TU KHO CHUNG, khong tu duong lui ═══════════
    # ⚠️ Phai hoi `__dbg.quiz.from === "bank"`, KHONG hoi "co cau do khong":
    #    duong lui CUNG cho ra mot cau do, nen mot phep do chi hoi cau sau se DAT
    #    ca khi kho chung chua bao gio chay.
    print("\n=== [2] Phong Thu Khong Gian: cau do tu KHO CHUNG ===")
    ctx, pg, errs, bad = newpage()
    pg.goto(BASE + "/game-defender.html", wait_until="load")
    pg.wait_for_timeout(600)
    pg.click("#start-btn")
    pg.wait_for_timeout(600)
    # ⚠️⚠️ GIEO THOI LA CHUA DU — PHAI BAN TRUNG. Ban dau cua bo do nay chi
    #   goi `spawn(1,'gold')` roi cho, va bao hong sau 20s: quiz chi mo khi DAN bay
    #   trung thach vang. Do la loi CUA PHEP DO. Nay doc vi tri hon vang tu
    #   `__dbg.list`, quy ra toa do man hinh (he ao 600x600 -> khung that) roi
    #   ngam va giu chuot — dung viec tre lam.
    pg.evaluate("() => window.__dbg.spawn(1,'gold')")
    seen = None
    down = False
    chan_doan = {"vong": 0, "thay_gold": 0, "trong_san": 0, "cuoi": None}
    for _ in range(150):
        chan_doan["vong"] += 1
        # ⚠️⚠️ CHI NGAM KHI HON VANG DA VAO HAN TRONG SAN. Vat the sinh tren vong
        #   tron r=440 quanh tam, tuc NGOAI khung 600x600 (x co the -140); ngam
        #   luc do la cu bam roi RA NGOAI canvas va khong handler nao chay.
        #   Bai hoc nay CLAUDE.md da ghi ngay 21/08/2026.
        info = pg.evaluate("""() => {
          const l = (window.__dbg.list || []).filter(f => f.key === 'gold');
          const cv = document.querySelector('.field canvas') || document.querySelector('canvas');
          if (!cv) return { canvas: false };
          const r = cv.getBoundingClientRect();
          if (!l.length) return { canvas: true, gold: 0 };
          const g = l[0];
          const trong = g.x > 20 && g.x < 580 && g.y > 20 && g.y < 580;
          return { canvas: true, gold: l.length, vx: g.x, vy: g.y, trong: trong,
                   x: r.left + g.x / 600 * r.width, y: r.top + g.y / 600 * r.height };
        }""")
        chan_doan["cuoi"] = info
        if info.get("gold"):
            chan_doan["thay_gold"] += 1
        if info.get("trong"):
            chan_doan["trong_san"] += 1
            pg.mouse.move(info["x"], info["y"])
            if not down:
                pg.mouse.down()
                down = True
        pg.wait_for_timeout(120)
        q = pg.evaluate("() => window.__dbg.quiz || null")
        if q:
            seen = q
            break
        if not info.get("gold"):
            pg.evaluate("() => window.__dbg.spawn(1,'gold')")
    if down:
        pg.mouse.up()
    # ⚠️ Phep cho TU KHAI TRANG THAI khi het gio (quy tac 6 muc 6): ban cu chi noi
    #    "khong mo ra sau 20s" nen khong biet no THAY gi.
    if not seen:
        print("       chan doan: %r" % (chan_doan,))
    check("mo duoc cau do bang cach gieo thach vang", seen is not None,
          "" if seen else "khong mo ra sau 20s")
    if seen:
        check("cau do den TU KHO CHUNG (from == 'bank')", seen.get("from") == "bank",
              "from=%r" % seen.get("from"))
        check("cau do co nhan LINH VUC (khong phai ASTRO_QUIZ tron)",
              bool(pg.eval_on_selector("#q-tag", "e => e.textContent.trim()")),
              pg.eval_on_selector("#q-tag", "e => e.textContent.trim()"))
    check("0 loi trang o Phong Thu", not errs, "; ".join(errs[:2]))
    check("0 tai nguyen hong o Phong Thu", not bad, "; ".join(bad[:2]))
    ctx.close()

    # ══ [3] ART THIEN THACH XAM: DEM loi goi ve anh ══════════════════════════
    # ⚠️ Khong doan theo mau pixel: ca art moi va ban vector cu deu la khoi
    #    xam-lam. Va `drawImage` de DEM.
    print("\n=== [3] Art thien thach xam: 3 game deu VE ANH ===")
    for path, nhan in [("/game-dodge.html", "Ne Thien Thach"),
                       ("/game-defender.html", "Phong Thu"),
                       ("/game-racer.html", "Duong Dua")]:
        ctx, pg, errs, bad = newpage()
        pg.add_init_script("""
          window.__drawn = 0;
          const orig = CanvasRenderingContext2D.prototype.drawImage;
          CanvasRenderingContext2D.prototype.drawImage = function(img){
            try { const s = (img && (img.currentSrc || img.src)) || '';
                  if (s.indexOf('rock-gray') >= 0) window.__drawn++; } catch(e){}
            return orig.apply(this, arguments);
          };
        """)
        pg.goto(BASE + path, wait_until="load")
        pg.wait_for_timeout(500)
        pg.click("#start-btn")
        pg.wait_for_timeout(2500)
        n = pg.evaluate("() => window.__drawn")
        check("%s: ve anh rock-gray.png (dem loi goi drawImage)" % nhan, n > 0, "%d loi goi" % n)
        check("%s: 0 loi trang" % nhan, not errs, "; ".join(errs[:2]))
        check("%s: 0 tai nguyen hong" % nhan, not bad, "; ".join(bad[:2]))
        ctx.close()

    # ══ [4] NHAN CHIP HUD khong bi cat tren ban that ════════════════════════
    print("\n=== [4] Nhan chip HUD: 0 nhan bi cat ===")
    for w, h, ten in [(1440, 900, "desktop-1440"), (1366, 768, "laptop-1366")]:
        ctx, pg, errs, bad = newpage(w, h)
        loi = []
        for g in ("game-dodge", "game-racer", "game-defender", "game-constellation"):
            pg.goto(BASE + "/%s.html" % g, wait_until="load")
            pg.wait_for_timeout(500)
            # ⚠️ Bo qua nhan dang `display:none` — khung 0x0 tai goc toa do lam
            #    phep do bao oan (bai hoc 22/08).
            n = pg.evaluate("""() => {
              let bad = 0;
              document.querySelectorAll('.hud .chip .k').forEach(e => {
                if (getComputedStyle(e).display === 'none') return;
                if (e.scrollWidth > e.clientWidth + 1) bad++;
              });
              return bad;
            }""")
            if n:
                loi.append("%s: %d nhan" % (g, n))
        check("%s: 0 nhan chip bi cat tren 4 game" % ten, not loi, "; ".join(loi) or "0")
        ctx.close()

    # ══ [5] Cau noi nhan vat: trang co token KHONG vo ═══════════════════════
    print("\n=== [5] Cau noi nhan vat: 5 trang nap `js/characters.js` khong vo ===")
    for path in ("/dashboard.html", "/achievements.html", "/codex.html",
                 "/certificate.html", "/profile.html"):
        ctx, pg, errs, bad = newpage()
        pg.goto(BASE + path, wait_until="load")
        pg.wait_for_timeout(1400)
        ok = pg.evaluate("() => !!(window.AstroQChars && window.AstroQChars.sync)")
        check("%s: AstroQChars.sync co that" % path, ok)
        check("%s: 0 loi trang" % path, not errs, "; ".join(errs[:2]))
        check("%s: 0 tai nguyen hong" % path, not bad, "; ".join(bad[:2]))
        ctx.close()

    b.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
