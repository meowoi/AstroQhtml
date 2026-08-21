# -*- coding: utf-8 -*-
r"""Đo viên Thiên thạch tím ở Đường Đua Sao Chổi (ARCADE-03).

⚠️ VÌ SAO CẦN: chủ dự án chơi thật rồi hỏi *"sao lại sử dụng hình thoi màu tím
   để thay thế?"*. Trước 21/08/2026 `drawItems()` vẽ một HÌNH THOI 4 điểm — không
   phải Thiên thạch tím. Cả app hiện đồng tiền đó bằng ảnh `img/tt.png` (luật
   25/07/2026), và ngay trên thanh HUD của chính trang này cũng là ảnh đó, nên hai
   hình cho một thứ khiến trẻ không nối được viên nó vừa hứng với con số trên HUD.

⚠️ ĐO BẰNG A/B TRÊN CÙNG MÃ NGUỒN, không đọc code: `CONFIG` nằm trong IIFE nên
   ngoài không với tới (bài học `shot_sprites.py` 19/08 — `ReferenceError`). Lượt
   ①: mạng bình thường → ảnh phải hiện ra. Lượt ②: cho `img/tt.png` trả **404** →
   phải lùi về bản vẽ vector, KHÔNG để ô trống. Hai ảnh chụp phải KHÁC nhau.
   ⚠️ Trả 404 chứ KHÔNG `abort()`: abort làm trình duyệt tự ghi một dòng đỏ
      `ERR_FAILED` và phép kiểm "0 lỗi trang" báo oan (bài học 19/08).
"""
import sys
import os

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123"
OUT = os.path.dirname(os.path.abspath(__file__))
ok_n = bad_n = 0


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""), flush=True)
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""), flush=True)


# Đếm pixel tím trong một cửa sổ quanh viên vừa gieo. `put()` là bề mặt test đã có.
COUNT = """(win) => {
  const cv = document.querySelector('canvas');
  const g  = cv.getContext('2d');
  const d  = g.getImageData(win.x, win.y, win.w, win.h).data;
  let tim = 0, sang = 0;
  for (let i = 0; i < d.length; i += 4) {
    const r = d[i], gg = d[i+1], b = d[i+2];
    if (b > 120 && r > 90 && b > gg + 30) tim++;
    if (r + gg + b > 210) sang++;
  }
  return {tim, sang};
}"""


def run(br, block_img):
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','300');")
    if block_img:
        ctx.route("**/img/tt.png",
                  lambda r: r.fulfill(status=404, content_type="text/plain", body="x"))
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/game-racer.html", wait_until="load", timeout=30000)
    pg.wait_for_timeout(900)
    # bỏ lời nhắc xoay ngang nếu có (desktop thì không có)
    if pg.locator(".ov.rot.show").count():
        pg.locator(".ov.rot.show .rot-ok").click()
    pg.click("#start-btn")
    pg.wait_for_timeout(500)
    st = pg.evaluate("() => window.__racer && window.__racer.state")
    if st != "play":
        ctx.close()
        return None, errs, st
    # gieo MỘT viên ngay trước mũi tàu rồi đo đúng chỗ đó
    pg.evaluate("() => window.__racer.clear()")
    pg.evaluate("() => window.__racer.put('gem', 90)")
    pg.wait_for_timeout(60)
    box = pg.evaluate("""() => {
        const cv = document.querySelector('canvas');
        const b  = cv.getBoundingClientRect();
        // hệ ảo -> pixel canvas: dùng đúng tỉ lệ mà fit() đặt
        const sx = cv.width / 800, sy = cv.height / 500;
        const r  = window.__racer.cfg;
        return {sx, sy, shipX: r.shipX, w: cv.width, h: cv.height};
    }""")
    # cửa sổ 90px ảo phía trước mũi tàu, cao hết làn
    x = int((box["shipX"] + 90 - 34) * box["sx"])
    win = {"x": max(0, x), "y": 0, "w": int(68 * box["sx"]), "h": box["h"]}
    d = pg.evaluate(COUNT, win)
    pg.screenshot(path=os.path.join(
        OUT, "racer-gem-%s.png" % ("vector" if block_img else "anh")))
    ctx.close()
    return d, errs, st


with sync_playwright() as p:
    br = p.chromium.launch()
    print("=== ① mang binh thuong: phai la ANH tt.png ===")
    d1, e1, s1 = run(br, False)
    check(d1 is not None, "vao duoc luot choi", str(s1))
    if d1:
        print("      tim=%d  sang=%d" % (d1["tim"], d1["sang"]))
        check(d1["tim"] > 200, "co khoi pixel tim o cho vua gieo vien",
              "%d px" % d1["tim"])
        # ⚠️ ĐỪNG đo bằng "phần sáng": cửa sổ đo cao hết làn nên nó lấn vào sao nền
        #    và vệt đuôi tàu — đo được 2093 vs 2111, tức hai bản gần BẰNG nhau và
        #    phép kiểm không phân biệt được gì (đúng bẫy đã ghi ở verify_luna_trail:
        #    cửa sổ đo phải nằm ngoài thứ khác đang sáng). Thứ phân biệt THẬT là
        #    DIỆN TÍCH TÍM: ảnh tt phủ rộng hơn hình thoi 4 điểm.
        check(not e1, "0 loi trang", "; ".join(e1[:1])[:80])

    print("\n=== ② anh tra 404: phai lui ve ban ve vector, KHONG de o trong ===")
    d2, e2, s2 = run(br, True)
    check(d2 is not None, "vao duoc luot choi", str(s2))
    if d1 and d2:
        print("      tim=%d  sang=%d" % (d2["tim"], d2["sang"]))
        check(d2["tim"] > 100, "duong lui vector VAN ve ra vien", "%d px" % d2["tim"])
        check(d1["tim"] > d2["tim"] * 1.2,
              "hai ban KHAC nhau (anh phu rong hon hinh thoi vector)",
              "tim: anh %d vs vector %d" % (d1["tim"], d2["tim"]))
        check(not e2, "0 loi trang o nhanh 404", "; ".join(e2[:1])[:80])
    br.close()

print("\n" + "=" * 52)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
