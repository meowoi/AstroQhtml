# -*- coding: utf-8 -*-
"""probe_field_space.py — ĐO chỗ trống quanh sân của 3 mini-game.

Câu hỏi: sân (.field) đang to bao nhiêu, và ô chứa nó (.play) còn dư bao nhiêu?
Chạy: python -m http.server 8123 trong AstroQhtml/ rồi `python scratchpad/probe_field_space.py`

⚠️ Phóng to sân KHÔNG đổi độ khó: `fit()` của cả 3 game đặt
   `ctx.setTransform(cv.width/VW, 0, 0, cv.height/VH, 0, 0)`, tức cả thế giới ảo
   (800×500 hoặc 600×600) được scale ra đúng kích cỡ phần tử. Thứ duy nhất đổi là
   số pixel phải tô — nên phần cuối script đo luôn nhịp khung hình.
"""
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123/"
GAMES = [("game-dodge.html", 8 / 5), ("game-defender.html", 1.0),
         ("game-constellation.html", 8 / 5)]
VIEWS = [("Win-FullHD", 1920, 1080), ("MacBook-Air-13", 1470, 956),
         ("Win-1366x768", 1366, 768), ("iPad-Pro-ngang", 1366, 1024),
         ("iPad-mini-ngang", 1133, 744), ("iPad-mini-doc", 744, 1133),
         ("iPhone-doc", 390, 844)]

MEASURE = """() => {
  const f = document.querySelector('.field'), p = document.querySelector('.play');
  const fr = f.getBoundingClientRect(), pr = p.getBoundingClientRect();
  const cs = getComputedStyle(p);
  return {
    fw: Math.round(fr.width), fh: Math.round(fr.height),
    pw: Math.round(pr.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)),
    ph: Math.round(pr.height - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom))
  };
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for game, ar in GAMES:
        print("\n=== %s  (ti le %.2f) ===" % (game, ar))
        print("  %-17s %-13s %-13s %-13s %s" %
              ("khung nhin", "san dang co", "cho con dung duoc", "co the to", "bo khong"))
        for name, w, h in VIEWS:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(BASE + game)
            pg.wait_for_selector(".field")
            pg.wait_for_timeout(350)
            m = pg.evaluate(MEASURE)
            # Co lon nhat con giu dung ti le trong o .play
            fit_w = min(m["pw"], m["ph"] * ar)
            fit_h = fit_w / ar
            grow = fit_w / m["fw"] if m["fw"] else 0
            waste = 1 - (m["fw"] * m["fh"]) / (fit_w * fit_h) if fit_w else 0
            print("  %-17s %5d x %-5d %5d x %-5d %5d x %-5d %5.0f%% dien tich"
                  % (name, m["fw"], m["fh"], m["pw"], m["ph"],
                     round(fit_w), round(fit_h), waste * 100))
            pg.close()
    b.close()
