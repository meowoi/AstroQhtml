# -*- coding: utf-8 -*-
"""KHOI "MO RONG" trong trinh doc bai — do tren Chromium that.

⚠️ VI SAO CAN BO DO RIENG: `smoke_library_featured.py` muc [8] chi doc DU LIEU
   (bai co `more` du song ngu khong). No khong tra loi duoc bon cau ma nguoi dung
   that su gap:
     · bac `junior` co GAP LAI khong · bac `senior` co MO SAN khong
     · nut bam co O CA HAI BAC khong  ← luat cua js/depth.js, de mat nhat
     · bai KHONG co `more` co AN HAN khoi do khong
   Ba trong bon cau do chi tra loi duoc bang cach mo trang ra roi do.

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/smoke_more_box.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
WITH_MORE = "art-body-in-space-changes"     # bai co `more`
NO_MORE = "jwst"                            # bai KHONG co `more`
OK = FAIL = 0


def chk(cond, label, info=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"  [OK]   {label}" + (f"  ({info})" if info else ""))
    else:
        FAIL += 1
        print(f"  [HONG] {label}" + (f"  ({info})" if info else ""))


def open_reader(pg, art_id):
    """Mo mot bai bang chinh duong nguoi dung di (bam vao the), roi cho than bai ve."""
    pg.evaluate(
        "id => { document.getElementById('q').value = ''; "
        "        const c = document.querySelector(`[data-id='${id}']`); if (c) c.click(); }",
        art_id)
    pg.wait_for_selector("#reader.show", timeout=15000)
    pg.wait_for_function(
        "() => document.querySelector('#r-body') && "
        "      document.querySelector('#r-body').children.length > 0", timeout=15000)
    pg.wait_for_timeout(250)


def state(pg):
    return pg.evaluate("""() => {
      const h = document.getElementById('r-more');
      const btn = h && h.querySelector('.mb-btn');
      const body = h && h.querySelector('.mb-body');
      return {
        hostHidden: !h || h.hidden,
        // `hidden` mot minh KHONG du: `display` cua tac gia thang `[hidden]`.
        // Do CA HAI, roi doi chieu — do la cach duy nhat bat duoc bay do.
        bodyAttrHidden: !!(body && body.hidden),
        bodyVisible: !!(body && getComputedStyle(body).display !== 'none'),
        btnExists: !!btn,
        btnVisible: !!(btn && getComputedStyle(btn).display !== 'none'
                       && btn.offsetWidth > 0),
        btnText: btn ? btn.textContent.trim() : '',
        aria: btn ? btn.getAttribute('aria-expanded') : '',
        paras: body ? body.querySelectorAll('p').length : 0,
        rawTag: body ? /<b>|&lt;b&gt;/.test(body.innerHTML) : false
      };
    }""")


def ctx_for(br, band, lang="vi"):
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang', '%s');"
        "localStorage.setItem('astroq-user', JSON.stringify({depth:'%s'}));" % (lang, band))
    return ctx


with sync_playwright() as p:
    br = p.chromium.launch()
    errs = []

    # ── [1] Bac JUNIOR: gap lai, nhung nut VAN CO ───────────────────────────
    print("\n=== [1] Bac junior (8-10) ===")
    ctx = ctx_for(br, "junior")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(f"{BASE}/library.html", wait_until="load")
    pg.wait_for_selector(".card", timeout=15000)
    open_reader(pg, WITH_MORE)
    s = state(pg)
    chk(not s["hostHidden"], "khoi Mo rong HIEN ra voi bai co `more`")
    chk(s["btnExists"] and s["btnVisible"],
        "junior VAN CO nut bam (bac chi quyet mac dinh, khong khoa gi)", s["btnText"])
    chk(not s["bodyVisible"], "junior: phan dao sau GAP LAI san")
    chk(s["aria"] == "false", "aria-expanded=false khi dang gap", s["aria"])

    # Bam -> phai mo ra THAT (do computed style, khong doc thuoc tinh)
    pg.click("#r-more .mb-btn")
    pg.wait_for_timeout(200)
    s2 = state(pg)
    chk(s2["bodyVisible"], "bam nut -> mo ra that")
    chk(s2["aria"] == "true", "aria-expanded=true sau khi mo", s2["aria"])
    chk(s2["paras"] >= 3, "co du doan van cua phan Mo rong", str(s2["paras"]))
    chk(not s2["rawTag"], "phan Mo rong khong lot the HTML tho")
    chk(s2["btnText"] != s["btnText"], "nhan nut doi theo trang thai",
        f"{s['btnText']} -> {s2['btnText']}")

    # Bam lan nua -> gap lai
    pg.click("#r-more .mb-btn")
    pg.wait_for_timeout(200)
    chk(not state(pg)["bodyVisible"], "bam lan nua -> gap lai")

    # ── [2] Bai KHONG co `more` -> an HAN ───────────────────────────────────
    print("\n=== [2] Bai khong co `more` ===")
    pg.click("#r-close")
    pg.wait_for_timeout(200)
    open_reader(pg, NO_MORE)
    s3 = state(pg)
    chk(s3["hostHidden"],
        "bai khong co `more` thi AN HAN khoi (tieu de tro doc ra nhu cho bi loi)")
    ctx.close()

    # ── [3] Bac SENIOR: mo san ──────────────────────────────────────────────
    print("\n=== [3] Bac senior (11+) ===")
    ctx = ctx_for(br, "senior")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/library.html", wait_until="load")
    pg.wait_for_selector(".card", timeout=15000)
    open_reader(pg, WITH_MORE)
    s4 = state(pg)
    chk(s4["bodyVisible"], "senior: phan dao sau MO SAN")
    chk(s4["aria"] == "true", "aria-expanded=true ngay khi mo bai", s4["aria"])
    chk(s4["btnExists"] and s4["btnVisible"],
        "senior VAN CO nut (de thu gon lai neu muon)", s4["btnText"])
    ctx.close()

    # ── [4] Ban EN dich duoc nhan ───────────────────────────────────────────
    print("\n=== [4] Ban tieng Anh ===")
    ctx = ctx_for(br, "junior", lang="en")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/library.html", wait_until="load")
    pg.wait_for_selector(".card", timeout=15000)
    open_reader(pg, WITH_MORE)
    en = pg.evaluate("""() => ({
        h: (document.querySelector('#r-more .mb-h')||{}).textContent || '',
        b: (document.querySelector('#r-more .mb-btn')||{}).textContent || '' })""")
    chk("Go deeper" in en["h"], "tieu de dich sang EN", en["h"])
    chk("Learn more" in en["b"], "nhan nut dich sang EN", en["b"])
    ctx.close()

    # ── [5] Trinh doc thu HAI (learn.html) cung co khoi do ──────────────────
    print("\n=== [5] learn.html — trinh doc thu hai ===")
    ctx = ctx_for(br, "senior")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/learn.html", wait_until="load")
    pg.wait_for_timeout(1200)
    n = pg.evaluate("() => !!document.getElementById('reader-more')")
    chk(n, "learn.html co khoi Mo rong (khong phai chi library.html moi co)")
    ctx.close()

    chk(not errs, "0 loi console / pageerror", str(errs[:3]))
    br.close()

print(f"\n===== {OK} dat / {FAIL} hong =====")
sys.exit(1 if FAIL else 0)
