# -*- coding: utf-8 -*-
"""Do tren BAN THAT rang ban va `esc()` khong lam hong 4 trang dang goi no
   BEN TRONG THUOC TINH (title / alt / aria-label).

   Cau hoi that su can tra loi khong phai "file da len chua" (curl da tra loi),
   ma la: thuoc tinh do co con doc duoc khong. Thoat du o ngu canh CHU la vo hai,
   nhung neu co cho nao doc `esc()` ra roi dem so chuoi thi no se hong o day."""
import sys
from playwright.sync_api import sync_playwright

BASE = "https://astroq.org"
dat = hong = 0


def check(label, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print(f"  [OK]   {label}  {info}")
    else:
        hong += 1
        print(f"  [HONG] {label}  {info}")


with sync_playwright() as p:
    br = p.chromium.launch()
    for page_name, sel, attr in [
        ("specimen-vault.html", "#f-cat button[title]", "title"),
        ("pricing.html", "[aria-label]", "aria-label"),
        ("explorer.html", "#deck [aria-label], #labels [aria-label]", "aria-label"),
        ("dashboard.html", "[aria-label]", "aria-label"),
    ]:
        ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
        ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(f"{BASE}/{page_name}", wait_until="load", timeout=60000)
        pg.wait_for_timeout(6000)

        check(f"{page_name}: 0 loi trang", not errs, str(errs[:2]))

        vals = pg.eval_on_selector_all(
            sel, "(els,a)=>els.slice(0,6).map(e=>e.getAttribute(a))", attr
        )
        vals = [v for v in vals if v]
        check(f"{page_name}: co thuoc tinh {attr} de do", len(vals) > 0, f"({len(vals)} cai)")
        # Thoat DU thi trinh duyet tra ve KY TU GOC, khong tra ve chuoi thuc the.
        # Thay `&quot;` / `&amp;` / `&#39;` trong gia tri doc ra = da thoat HAI LAN.
        bad = [v for v in vals if "&quot;" in v or "&amp;" in v or "&#39;" in v or "&lt;" in v]
        check(f"{page_name}: khong thuoc tinh nao bi thoat HAI LAN", not bad, str(bad[:2]))
        if vals:
            print(f"         vi du: {vals[0][:60]!r}")
        ctx.close()
    br.close()

print(f"\n===== {dat} dat / {hong} hong =====")
sys.exit(1 if hong else 0)
