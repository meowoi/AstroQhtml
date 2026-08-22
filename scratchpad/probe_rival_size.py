# -*- coding: utf-8 -*-
"""Do CO VE THAT cua ba tau doi thu va so voi tau Luna cua tre.

VI SAO CAN: doi cach ghim co (22/08/2026: theo CHIEU DAI -> theo DIEN TICH) la
doi mot thu tre NHIN THAY. Doc cong thuc thi khong biet no ra bao nhieu tren man;
bo nay VA `drawImage` de ghi lai cỡ THAT tung anh duoc ve, roi so voi Luna.

⚠️ Do bang cach dem loi goi `drawImage`, khong doan theo mau pixel: ca ba art va
   Luna deu la khoi mau sang tren nen toi, khong co dai mau nao tach bach duoc.

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/probe_rival_size.py
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
dat = hong = 0


def check(nhan, dk, ct=""):
    global dat, hong
    if dk:
        dat += 1
        print("  [OK]   " + nhan + (("  (" + ct + ")") if ct else ""))
    else:
        hong += 1
        print("  [HONG] " + nhan + (("  (" + ct + ")") if ct else ""))


VA = """
window.__sz = {};
const orig = CanvasRenderingContext2D.prototype.drawImage;
CanvasRenderingContext2D.prototype.drawImage = function(img, dx, dy, dw, dh){
  try {
    const s = (img && (img.currentSrc || img.src)) || '';
    const m = s.match(/\\/(rival-[a-z]+|luna-side)\\.png/);
    // ⚠️ Chi ghi khi co CA `dw`/`dh`: dang goi 5 tham so thi day la (sx,sy,sw,sh).
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
    # ⚠️ Ghim ngon ngu + nap vi: khong co tt thi khong vao duoc luot choi.
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','999');")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.add_init_script(VA)

    pg.goto(BASE + "/game-racer.html", wait_until="load")
    pg.wait_for_timeout(600)
    pg.click("#start-btn")
    pg.wait_for_timeout(2600)

    sz = pg.evaluate("() => window.__sz")
    print("\n=== Co ve that (don vi ao) ===")
    for k in sorted(sz):
        d = sz[k]
        print("   %-14s %6.2f x %-6.2f  ti le %.3f  dien tich %7.1f"
              % (k, d["w"], d["h"], d["w"] / d["h"], d["w"] * d["h"]))

    check("do duoc ca 3 doi thu", len([k for k in sz if k.startswith("rival-")]) == 3,
          "thay: %s" % sorted(sz))
    check("do duoc tau Luna cua tre", "luna-side" in sz, "thay: %s" % sorted(sz))

    if "luna-side" in sz and len([k for k in sz if k.startswith("rival-")]) == 3:
        a_luna = sz["luna-side"]["w"] * sz["luna-side"]["h"]
        for k in sorted(k for k in sz if k.startswith("rival-")):
            d = sz[k]
            a = d["w"] * d["h"]
            ti = a / a_luna
            # ⚠️ Dung sai 8%: `SPR.h` cua Luna la `min(shipH, shipW/ar)` nen dien
            #    tich that cua no hoi lech khoi hang so `shipW*shipH` dung lam moc.
            check("%s: trong luong thi giac ~ bang Luna" % k, 0.92 <= ti <= 1.08,
                  "%.0f%% dien tich Luna" % (ti * 100))
            # Dieu chu du an chot 21/08 van phai duoc ton trong: khong tau nao dai
            # gap ruoi Luna (do la ly do (b) bi bac — no che vat pham tren lan).
            check("%s: khong dai qua 1,35x Luna" % k,
                  d["w"] <= sz["luna-side"]["w"] * 1.35,
                  "dai %.1f so voi Luna %.1f" % (d["w"], sz["luna-side"]["w"]))
            # Lan cao 84: tau phai nam gon trong lan.
            check("%s: cao nho hon nua chieu cao lan (84)" % k, d["h"] < 42,
                  "cao %.1f" % d["h"])

    pg.screenshot(path="scratchpad/rival-size.png")
    print("   anh -> scratchpad/rival-size.png")
    check("0 loi trang / console", not errs, "; ".join(errs[:3]))
    ctx.close()
    b.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
