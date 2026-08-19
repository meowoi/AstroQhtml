# -*- coding: utf-8 -*-
"""Ghep Chom Sao — GIAI THAT xong mot chom roi do modal thong tin.

⚠️ Khong the goi `paintFact()` tu ngoai: script cua trang nam trong IIFE. Ma mo
   modal bang cach gan class `.show` thi `#fact-art` con RONG — tuc phep do se bao
   "khong co hinh" trong khi san pham dung. Nen o day noi THAT cac ngoi sao: doc
   `SKY` tu chinh file HTML, quy toa do ao 800x500 ra toa do canvas, roi bam.
"""
import io
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
SRC = io.open("game-constellation.html", encoding="utf-8").read()
dat = hong = 0


def chk(cond, nhan, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))


def parse_sky():
    """Doc `SKY` tu file: {ten tieng Viet: [(x,y), ...] theo dung thu tu id}."""
    out = {}
    for m in re.finditer(r'key:"([a-z-]+)",\s*\n\s*name:\{vi:"([^"]+)"', SRC):
        key, nm = m.group(1), m.group(2)
        seg = SRC[m.end():]
        stars_blk = re.search(r'stars:\[(.*?)\]', seg, re.S)
        if not stars_blk:
            continue
        pts = re.findall(r'\{id:\s*(\d+),\s*x:\s*([\d.]+),\s*y:\s*([\d.]+)\}',
                         stars_blk.group(1))
        if pts:
            pts = sorted(pts, key=lambda t: int(t[0]))
            out[nm] = [(float(x), float(y)) for _, x, y in pts]
    return out


SKY = parse_sky()
print("doc duoc %d chom sao tu file: %s" % (len(SKY), list(SKY)))
if not SKY:
    sys.exit("KHONG doc duoc SKY — phep do se 'dat' mot cach RONG, dung de no chay tiep")

with sync_playwright() as p:
    br = p.chromium.launch()
    for W in (1440, 390):
        print("\n=== Giai that mot chom @ %dpx ===" % W)
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
        pg.wait_for_timeout(400)

        nm = pg.eval_on_selector(".chip.cons .v", "e=>e.innerText").strip()
        stars = SKY.get(nm)
        chk(stars is not None, "nhan ra chom dang choi tu chip", "%r" % nm)
        if not stars:
            ctx.close()
            continue

        box = pg.locator(".play canvas").first.bounding_box()
        sx, sy = box["width"] / 800.0, box["height"] / 500.0
        # ⚠️ BAM THEO CAP, khong bam tuan tu: `onUp` dat `sel=-1` sau moi duong noi
        #    (xem game-constellation.html), nen bam lien tuc 1,2,3,4 se ra
        #    link(1,2) roi CHON sao 3 roi link(3,4) — sai cap va tinh la noi sai.
        for k in range(len(stars) - 1):
            for (vx, vy) in (stars[k], stars[k + 1]):
                pg.mouse.click(box["x"] + vx * sx, box["y"] + vy * sy)
                pg.wait_for_timeout(70)
        pg.wait_for_selector("#ov-fact.show", timeout=8000)
        chk(True, "ghep xong ca chom -> modal thong tin TU BAT")

        chk("🔭" not in pg.eval_on_selector("#ov-fact", "e=>e.innerText"),
            "modal khong con emoji kinh thien van")
        art = pg.eval_on_selector("#fact-art", """e=>{
            const svg=e.querySelector('svg'); if(!svg) return null;
            const r=svg.getBoundingClientRect();
            return {w:Math.round(r.width), h:Math.round(r.height),
                    lines:svg.querySelectorAll('polyline').length,
                    stars:svg.querySelectorAll('circle').length};}""")
        chk(art is not None, "modal ve SVG hinh chom sao", str(art))
        if art:
            chk(art["stars"] == len(stars),
                "so diem sao KHOP dung so sao cua chom vua ghep",
                "%d vs %d" % (art["stars"], len(stars)))
            chk(art["lines"] == 1, "co dung mot duong noi lien mach", str(art["lines"]))
            chk(art["w"] > 60 and art["h"] > 40, "hinh du to de nhin lai",
                "%dx%d" % (art["w"], art["h"]))
            # Hinh phai NAM TRON trong the, khong chia ra ngoai
            ov = pg.eval_on_selector("#fact-art svg", """e=>{
                const r=e.getBoundingClientRect();
                const c=e.closest('.ov-card').getBoundingClientRect();
                return {l:Math.round(c.left-r.left), rr:Math.round(r.right-c.right)};}""")
            chk(ov["l"] <= 0 and ov["rr"] <= 0, "hinh nam tron trong the",
                "trai %+d · phai %+d" % (ov["l"], ov["rr"]))
        chk(not loi, "0 loi trang", "; ".join(loi[:2]))
        if W == 1440:
            pg.locator("#ov-fact .ov-card").screenshot(path="scratchpad/shot-fact-art.png")
        ctx.close()
    br.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
