# -*- coding: utf-8 -*-
r"""Chụp PHÓNG TO ba tàu đối thủ của ARCADE-03 để SOI MẮT.

⚠️ VÌ SAO PHẢI CHỤP: số đo nói được "ba dấu khác màu", nhưng không nói được hình
   đọc ra là cái gì. Dự án đã trả giá bốn lần cho đúng chuyện đó — buồng lái to
   quá thành CÁI NƠ, đuôi sao chổi thành CÁI THÌA, thanh giàn thành CHÌA KHOÁ,
   san hô hai nhánh thành CHỮ Y. Ba tàu mới cũng phải qua cửa này.

Chạy: `python -m http.server 8123` trong AstroQhtml/ rồi chạy file này.
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright  # noqa: E402

URL = "http://127.0.0.1:8123/game-racer.html"
OUT = os.environ.get("SHOT_DIR") or os.path.join("scratchpad", "_shots")
os.makedirs(OUT, exist_ok=True)


def seed(ctx, bal=60):
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','vi');"
        "localStorage.setItem('astroq-asteroids','%d');"
        "localStorage.setItem('astroq-sfx','off');" % bal)


with sync_playwright() as p:
    br = p.chromium.launch()
    for dsf, tag in ((3, "x3"), (1, "x1")):
        ctx = br.new_context(viewport={"width": 1440, "height": 900},
                             device_scale_factor=dsf, locale="vi-VN")
        seed(ctx)
        pg = ctx.new_page()
        perr = []
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(500)
        pg.click("#start-btn")
        pg.wait_for_timeout(450)

        box = pg.query_selector(".field").bounding_box()
        # Cửa sổ quanh chỗ ba đối thủ xuất phát (hệ ảo 800×500 → tỉ lệ theo khung)
        sc = box["width"] / 800.0
        clip = {"x": box["x"] + 60 * sc, "y": box["y"] + 120 * sc,
                "width": 340 * sc, "height": 360 * sc}
        pg.screenshot(path=os.path.join(OUT, "rivals-%s.png" % tag), clip=clip)

        # Lượt thứ hai: cả ba ĐANG TĂNG TỐC (miệng ống đẩy rực + vệt dài)
        pg.evaluate("() => { var r = window.__racer; if (r && r.boostRivals)"
                    " r.boostRivals(); }")
        pg.wait_for_timeout(120)
        pg.screenshot(path=os.path.join(OUT, "rivals-boost-%s.png" % tag),
                      clip=clip)
        print("  %s: 0 loi trang = %s" % (tag, not perr))
        ctx.close()

    # Bản 390×844 — đọc được ở cỡ nhỏ nhất không?
    ctx = br.new_context(viewport={"width": 390, "height": 844},
                         device_scale_factor=3, locale="vi-VN",
                         has_touch=True, is_mobile=True)
    seed(ctx)
    pg = ctx.new_page()
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(500)
    b = pg.query_selector(".rot-ok")
    if b:
        b.click()                      # bỏ qua lời nhắc xoay ngang
        pg.wait_for_timeout(250)
    pg.click("#start-btn")
    pg.wait_for_timeout(450)
    box = pg.query_selector(".field").bounding_box()
    pg.screenshot(path=os.path.join(OUT, "rivals-390.png"), clip=box)
    ctx.close()
    br.close()

print("  -> %s" % os.path.abspath(OUT))
