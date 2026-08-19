# -*- coding: utf-8 -*-
"""Do bon thay doi HINH cua 19/08/2026, tren Chromium that.

⚠️ KHONG doc `CONFIG`/`spriteReady` tu ngoai: script cua tung trang game nam trong
   IIFE nen chung khong phai bien toan cuc — hoi thang la `ReferenceError`, va mot
   phep do "khong doc duoc" de bi doc thanh "san pham hong".
   Cach do dung la A/B tren CUNG mot ma nguon: mot luot cho anh tra 404 (trang lui
   ve ban ve vector), mot luot binh thuong; hai anh chup PHAI KHAC NHAU. Do chung
   minh anh THAT SU DUOC VE, khong chi "duong dan co khai".
⚠️ Tra 404 chu khong `abort()`: abort lam trinh duyet tu ghi mot dong do
   `ERR_FAILED` vao console, va phep kiem "0 loi trang" se bao oan (bai hoc 12/08).
"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
dat = hong = 0


def chk(cond, nhan, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))


def diff_px(a, b):
    """So hai anh chup: tra ve so pixel khac nhau (bo qua lech nho duoi nguong)."""
    ia = Image.open(io.BytesIO(a)).convert("RGB")
    ib = Image.open(io.BytesIO(b)).convert("RGB")
    if ia.size != ib.size:
        return -1
    pa, pb = ia.load(), ib.load()
    n = 0
    for y in range(0, ia.size[1], 2):
        for x in range(0, ia.size[0], 2):
            ca, cb = pa[x, y], pb[x, y]
            if abs(ca[0]-cb[0]) + abs(ca[1]-cb[1]) + abs(ca[2]-cb[2]) > 24:
                n += 1
    return n


def shot_field(br, page_url, block=None, w=1440, h=900, start=True, wait=900,
               keys=None, out=None):
    """Mo mot game, (tuy chon) cho mot anh tra 404, bat dau luot roi chup san."""
    ctx = br.new_context(viewport={"width": w, "height": h}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','99')}catch(e){}")
    pg = ctx.new_page()
    loi = []
    pg.on("pageerror", lambda e: loi.append(str(e)))
    if block:
        pg.route("**/" + block, lambda r: r.fulfill(status=404, body=""))
    pg.goto(BASE + page_url, wait_until="load")
    pg.wait_for_selector("#gtag", timeout=15000)
    if start:
        pg.click("#start-btn")
        pg.wait_for_timeout(wait)
    for k in (keys or []):
        pg.keyboard.press(k)
        pg.wait_for_timeout(120)
    png = pg.locator(".play").screenshot()
    if out:
        io.open(out, "wb").write(png)
    ctx.close()
    return png, loi


with sync_playwright() as p:
    br = p.chromium.launch()

    # ═══════════ [1] Duong Dua Sao Choi: anh Luna ═══════════
    print("\n=== [1] game-racer: nhan vat dieu khien la ANH Luna ===")
    a, loi_a = shot_field(br, "/game-racer.html", block="luna-side.png")
    b, loi_b = shot_field(br, "/game-racer.html", out="scratchpad/shot-racer-luna.png")
    d = diff_px(a, b)
    chk(d > 40, "chan anh Luna thi san VE KHAC => anh that su duoc ve",
        "%d diem khac" % d)
    chk(not loi_a, "lui ve ban ve vector: 0 loi trang", "; ".join(loi_a[:2]))
    chk(not loi_b, "ban co anh: 0 loi trang", "; ".join(loi_b[:2]))

    # ═══════════ [2] Me Cung: Comet + Thien thach tim ═══════════
    print("\n=== [2] game-maze: hero la Comet, tinh the la anh Thien thach tim ===")
    base, loi_m = shot_field(br, "/game-maze.html", wait=700,
                             out="scratchpad/shot-maze-comet.png")
    for f, nhan in (("comet-idle.png", "hero Comet"), ("tt.png", "tinh the Thien thach tim")):
        cut, _ = shot_field(br, "/game-maze.html", block=f, wait=700)
        d = diff_px(base, cut)
        chk(d > 20, "chan %s thi san VE KHAC => anh duoc ve" % f, "%d diem khac" % d)
    chk(not loi_m, "0 loi trang", "; ".join(loi_m[:2]))
    # Huong dan phai goi ten Comet
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(BASE + "/game-maze.html", wait_until="load")
    pg.wait_for_selector("#ov-start", timeout=15000)
    txt = pg.eval_on_selector("#ov-start", "e=>e.innerText")
    chk("Comet" in txt and "phi hành gia" not in txt.lower(),
        "huong dan goi ten Comet, khong con 'phi hanh gia'")
    ctx.close()

    # ═══════════ [3]+[4] Ghep Chom Sao ═══════════
    for W in (1366, 1440, 390):
        print("\n=== [3][4] game-constellation @ %dpx ===" % W)
        ctx = br.new_context(viewport={"width": W, "height": 900}, locale="vi-VN",
                             timezone_id="Asia/Ho_Chi_Minh")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                            "localStorage.setItem('astroq-asteroids','99')}catch(e){}")
        pg = ctx.new_page()
        loi = []
        pg.on("pageerror", lambda e: loi.append(str(e)))
        pg.goto(BASE + "/game-constellation.html", wait_until="load")
        pg.wait_for_selector("#gtag", timeout=15000)
        pg.click("#start-btn")
        pg.wait_for_timeout(500)

        # ── Chip ten chom sao ──
        if pg.locator(".chip.cons").count():
            m = pg.eval_on_selector(".chip.cons .v", """e=>{
                const c=getComputedStyle(e), r=e.getBoundingClientRect();
                const p=e.closest('.chip').getBoundingClientRect();
                return {ta:c.textAlign, sw:e.scrollWidth, cw:e.clientWidth,
                        outR:Math.round(r.right-p.right), outB:Math.round(r.bottom-p.bottom),
                        txt:e.innerText};}""")
            if W >= 901:
                chk(m["ta"] == "left", "ten chom sao can LE TRAI", m["ta"])
            chk(m["sw"] <= m["cw"] + 1, "ten chom sao khong bi cat ngang",
                "%d/%d" % (m["sw"], m["cw"]))
            chk(m["outR"] <= 0 and m["outB"] <= 0,
                "ten chom sao KHONG chen ra ngoai khung chip",
                "phai %+dpx · duoi %+dpx · %r" % (m["outR"], m["outB"], m["txt"][:28]))
        chk(pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"),
            "khong tran ngang")

        # ── Modal thong tin ──
        # ⚠️ CHI kiem "khong con emoji" o day. Phan HINH chom sao do `shot_fact_art.py`
        #    lo, vi no phai GIAI THAT xong mot chom: mo modal bang cach gan class
        #    `.show` thi `#fact-art` con RONG (paintFact nam trong IIFE, khong goi tu
        #    ngoai duoc) — mot phep kiem nhu the se bao hong mai du san pham dung, ma
        #    phep kiem hay bao oan thi som muon bi bo qua.
        pg.evaluate("() => document.getElementById('ov-fact').classList.add('show')")
        pg.wait_for_timeout(120)
        chk("🔭" not in pg.eval_on_selector("#ov-fact", "e=>e.innerText"),
            "modal khong con emoji kinh thien van")
        if W == 1440:
            pg.locator(".chip.cons").screenshot(path="scratchpad/shot-chip-cons.png")
        chk(len(loi) == 0, "0 loi trang", "; ".join(loi[:2]))
        ctx.close()

    br.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
