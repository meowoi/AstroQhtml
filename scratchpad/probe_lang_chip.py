# -*- coding: utf-8 -*-
"""probe_lang_chip.py — THẺ NGÔN NGỮ Ở CÁC MÀN CÓ ĐỒNG NHẤT KHÔNG.

Chủ dự án 19/08/2026: *"thẻ ngôn ngữ ở các màn hình chưa đồng nhất"*. Bộ này đo
thật trên astroq.org: mỗi trang có bộ chọn ngôn ngữ dạng nào, và nó liệt kê bao
nhiêu thứ tiếng.

Đếm tĩnh (`grep`) cho thấy BA hình dạng: dashboard có menu 8 tiếng trong dropdown
avatar; `mission-earth` nạp `user-menu.js` nhưng KHÔNG khai chuỗi `lang_soon_*`;
31 trang còn lại chỉ có hai nút VI/EN. Bộ này xác nhận bằng cách mở trang thật.

  python scratchpad/probe_lang_chip.py
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
PAGES = ["/dashboard.html", "/mission-earth.html", "/games.html", "/quiz.html",
         "/library.html", "/pricing.html", "/lab.html", "/mission-orbit.html"]

JS_LIST = """() => {
  const out = [];
  document.querySelectorAll(".lang-switch, [class*='um-lang'], .um-menu").forEach(e => {
    const t = (e.innerText || "").trim();
    if (t) out.push(e.className + " :: " + t.split("\\n").join(" / "));
  });
  return out.slice(0, 6);
}"""

JS_COUNT = """() => {
  // Số THỨ TIẾNG mà màn này cho thấy — đếm theo nút/hàng có mã 2 chữ.
  const codes = new Set();
  document.querySelectorAll("[data-lang], .um-lang-row, .lang-switch a, .lang-switch button")
    .forEach(e => {
      const c = (e.getAttribute("data-lang") || e.textContent || "").trim().toLowerCase();
      if (/^(vi|en|zh|ja|ko|es|fr|th)$/.test(c)) codes.add(c);
    });
  return [...codes].sort();
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    rows = []
    for path in PAGES:
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx.add_init_script(
            "try{localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
        pg = ctx.new_page()
        pg.goto(SITE + path, wait_until="load", timeout=45000)
        pg.wait_for_timeout(3200)
        sw = pg.locator(".lang-switch").count()
        um = pg.locator(".um-btn, #um-btn").count()
        # Mở dropdown avatar nếu có, vì menu ngôn ngữ nằm trong đó.
        if um:
            try:
                pg.click(".um-btn, #um-btn")
                pg.wait_for_timeout(900)
            except Exception:
                pass
        codes = pg.evaluate(JS_COUNT)
        lists = pg.evaluate(JS_LIST)
        # Chuỗi i18n chưa khai thì hiện ra chính TÊN KHOÁ — dấu hiệu lệch rõ nhất.
        raw = pg.evaluate("""() => {
            const t = document.body.innerText || "";
            return ["lang_soon_h","lang_soon_tag","lang_head"].filter(k => t.includes(k));
        }""")
        rows.append((path, sw, um, codes, raw, lists))
        ctx.close()
    b.close()

print("\n%-24s %-4s %-4s %-28s %s" % ("TRANG", "sw", "um", "THU TIENG THAY DUOC", "KHOA CHUA DICH"))
print("-" * 104)
for path, sw, um, codes, raw, lists in rows:
    print("%-24s %-4d %-4d %-28s %s"
          % (path, sw, um, ",".join(codes) or "-", ",".join(raw) or "-"))

print("\n=== Chi tiet tung man ===")
for path, sw, um, codes, raw, lists in rows:
    print("\n### %s" % path)
    if not lists:
        print("   (khong tim thay bo chon ngon ngu nao)")
    for l in lists:
        print("   " + l[:150])
