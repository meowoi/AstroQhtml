# -*- coding: utf-8 -*-
"""play_orbit_say.py — CHOI THAT chang (1) cua nhiem vu 02 de do MOT viec:
BOX THOAI KHONG DUOC DE BANG DAY DE LEN (loi 19/08/2026, chu du an gui anh).

Do nhung thu doc code KHONG chung minh duoc:
  [1] sau khi cham du 3 vet quet, box thoai `s1_done` KHONG giao voi bang #scan
  [2] box thoai co class `lift` va van NAM TRON trong khung nhin (khong troi len tren)
  [3] the "vua nhan duoc" cung khong bi bang de (ban sua 03/08/2026 con nguyen)
  [4] ca hai khung: desktop 1440x900 va dien thoai 390x844

Chu ky moi cua `nudge` do phep kiem tinh [30] trong `check_pages.py` lo — script cua
trang la `type="module"` nen `ST` khong voi tay tu ngoai vao duoc.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi
       python scratchpad/play_orbit_say.py
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/mission-orbit.html?restart=1"
SWATHS = ["wide", "above", "pixel"]

dat = hong = 0


def check(label, cond, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def gap(a, b):
    """Khoang trong doc giua hai hop; am = DE NHAU bao nhieu px."""
    return max(a["y"], b["y"]) - min(a["y"] + a["height"], b["y"] + b["height"])


def overlap(a, b):
    """Hai hop co giao nhau khong (ca hai truc)."""
    return not (a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"]
                or a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"])


def play(br, w, h, nhan):
    print("\n=== %s (%dx%d) ===" % (nhan, w, h))
    ctx = br.new_context(viewport={"width": w, "height": h},
                         locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    # Chromium mac dinh en-US → ghim tieng Viet cho khop khoa i18n dang do.
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    pg = ctx.new_page()
    loi = []
    pg.on("pageerror", lambda e: loi.append(str(e)))
    pg.goto(URL, wait_until="load")

    say, scan, card = pg.locator("#say"), pg.locator("#scan"), pg.locator("#card")

    # Comet noi cau mo chang → bam OK
    pg.wait_for_selector("#say.show", timeout=15000)
    pg.click("#say-next")
    pg.wait_for_selector("#scan.show", timeout=15000)
    check("bang HE THONG QUAN SAT mo ra", True)

    for i, sid in enumerate(SWATHS, 1):
        pg.click('button.e2-mk[data-id="%s"]' % sid)
        pg.wait_for_selector("#card.show", timeout=15000)
        bc, bs = card.bounding_box(), scan.bounding_box()
        check("the vet %d KHONG bi bang #scan de" % i, not overlap(bc, bs),
              "the y=%.0f..%.0f · bang y=%.0f" % (bc["y"], bc["y"] + bc["height"], bs["y"]))
        check("nut 'Da hieu!' cua the nam tron trong khung", bc["y"] >= 0,
              "top=%.0f" % bc["y"])
        pg.click("#card-ok")
        pg.wait_for_timeout(500)        # the co hoat canh dong 260ms + do tre

    # Cham du 3 → Byte noi `s1_done` trong luc bang #scan CON MO. Day la ca loi.
    pg.wait_for_selector("#say.show", timeout=15000)
    pg.wait_for_timeout(600)                       # cho hoat canh nhac box chay xong
    bsay, bscan = say.bounding_box(), scan.bounding_box()
    print("     box thoai y=%.0f..%.0f · bang y=%.0f..%.0f"
          % (bsay["y"], bsay["y"] + bsay["height"], bscan["y"], bscan["y"] + bscan["height"]))
    check("BOX THOAI `s1_done` KHONG DE LEN BANG #scan", not overlap(bsay, bscan),
          "khoang trong %.0fpx" % gap(bsay, bscan))
    check("box thoai co class `lift`",
          "lift" in (say.get_attribute("class") or ""))
    check("box thoai KHONG troi len khoi khung nhin", bsay["y"] >= 0,
          "top=%.0f" % bsay["y"])
    check("nut OK cua box thoai bam duoc (khong bi bang che)",
          not overlap(pg.locator("#say-next").bounding_box(), bscan))

    pg.screenshot(path="scratchpad/shot-orbit-say-%s.png" % nhan)
    check("khong loi JS nao trong ca luot choi", not loi, " | ".join(loi[:2]))
    ctx.close()


with sync_playwright() as p:
    br = p.chromium.launch()
    play(br, 1440, 900, "desktop")
    play(br, 390, 844, "mobile")
    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(1 if hong else 0)
