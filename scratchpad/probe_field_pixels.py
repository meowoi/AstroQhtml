# -*- coding: utf-8 -*-
"""probe_field_pixels.py — sân to ra thì canvas phải tô bao nhiêu pixel?

⚠️⚠️ ĐỌC TRƯỚC KHI ĐỊNH VIẾT MỘT PHÉP ĐO FPS Ở ĐÂY: KHÔNG ĐO ĐƯỢC FPS BẰNG
   CHROMIUM HEADLESS. Nó vẽ bằng SwiftShader (không GPU) nên bỏ khung ở MỌI cỡ sân.
   Bản đo fps đầu tiên (12/08/2026) cho ra sân cũ 66,6ms mà sân mới 50,1ms — sân TO
   HƠN lại NHANH HƠN, chuyện bất khả thi nếu đang bị giới hạn bởi số pixel; và mọi
   con số đều là bội số đúng của 16,67ms. Đó là nhịp của headless, không phải của
   game. Script đó đã bỏ. Muốn số fps thật thì mở trên máy/tablet thật.

   Thứ ĐO ĐƯỢC và cũng là nguyên nhân thật: **vùng vẽ của canvas** (`cv.width ×
   cv.height`). `js/game-shell.js` giữ nó dưới trần 2,4 triệu pixel bằng cách hạ DPR.
   Script này kiểm cái trần đó có thật sự có hiệu lực, ở mọi khổ máy.

Chạy: python -m http.server 8123 trong AstroQhtml/ rồi
      python scratchpad/probe_field_pixels.py
"""
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123/"
CAP = 2_400_000            # phai khop PX_CAP trong js/game-shell.js
OLD = 1600 * 1000          # san cu 800x500 o DPR 2 — moc da chay muot tu 27/07/2026

GAMES = ["game-dodge.html", "game-defender.html", "game-constellation.html"]
VIEWS = [("Win-FullHD  DPR1", 1920, 1080, 1), ("Win-FullHD  DPR2", 1920, 1080, 2),
         ("MacBook-Air DPR2", 1470, 956, 2), ("iPad-Pro-ngang DPR2", 1366, 1024, 2),
         ("iPad-mini-ngang DPR2", 1133, 744, 2), ("iPhone-doc DPR3", 390, 844, 3)]

MEASURE = """() => {
  const cv = document.querySelector('canvas');
  const r = cv.getBoundingClientRect();
  return {bw: cv.width, bh: cv.height, cw: Math.round(r.width), ch: Math.round(r.height)};
}"""

bad = 0
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for game in GAMES:
        print("\n=== %s ===" % game)
        print("  %-21s %-13s %-15s %-10s %s"
              % ("khung nhin", "san (css px)", "vung ve canvas", "trieu px", "so voi san cu"))
        for name, w, h, dpr in VIEWS:
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=dpr)
            pg.goto(BASE + game)
            pg.wait_for_selector("canvas")
            pg.wait_for_timeout(450)
            m = pg.evaluate(MEASURE)
            px = m["bw"] * m["bh"]
            flag = "" if px <= CAP * 1.02 else "  <-- VUOT TRAN"
            if px > CAP * 1.02:
                bad += 1
            print("  %-21s %5d x %-5d %6d x %-6d %8.2f %8.2fx%s"
                  % (name, m["cw"], m["ch"], m["bw"], m["bh"], px / 1e6, px / OLD, flag))
            pg.close()
    b.close()

print("\ntran PX_CAP = %.1f trieu px | moc san cu (800x500 @DPR2) = %.1f trieu px"
      % (CAP / 1e6, OLD / 1e6))
print("KET QUA: %s" % ("khong co cau hinh nao vuot tran" if not bad
                       else "%d cau hinh VUOT TRAN" % bad))
sys.exit(1 if bad else 0)
