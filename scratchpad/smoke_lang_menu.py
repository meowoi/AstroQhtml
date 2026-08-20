# -*- coding: utf-8 -*-
"""Do MENU THA ngon ngu vua mang sang landing-app.html va select.html."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
OK = FAIL = 0


def check(label, cond, detail=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(detail)) if detail else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(detail))


def run(br, page, w=1280, h=900):
    ctx = br.new_context(viewport={"width": w, "height": h})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.removeItem('astroq-user');")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/" + page, wait_until="load")
    pg.wait_for_timeout(1500)
    print("")
    print("=== " + page + " (" + str(w) + "x" + str(h) + ") ===")

    check("khong con day nut VI|EN trai ngang",
          pg.locator(".lang-switch:not(.um-pop .lang-switch)").count() == 0
          or pg.locator("[data-menu-btn]").count() >= 1)
    btn = pg.locator(".lang-pick [data-menu-btn]")
    check("co nut thu gon", btn.count() == 1, str(btn.count()))
    check("nut hien ma ngon ngu dang dung",
          pg.locator(".lang-pick [data-lang-code]").inner_text().strip().upper() == "VI",
          pg.locator(".lang-pick [data-lang-code]").inner_text())
    pop = pg.locator(".lang-pick [data-menu-pop]")
    check("tam tha dang DONG luc mo trang", not pop.is_visible())

    btn.click()
    pg.wait_for_timeout(350)
    check("bam thi tam tha MO", pop.is_visible())
    ready = pg.locator(".lang-pick [data-lang-list] button")
    soon = pg.locator(".lang-pick [data-lang-soon-list] button")
    check("dung 2 ngon ngu chon duoc", ready.count() == 2, str(ready.count()))
    check("co ngon ngu 'sap co'", soon.count() >= 1, str(soon.count()))
    check("ngon ngu sap co KHONG mang data-lang (khong ghi de astroq-lang)",
          pg.locator(".lang-pick [data-lang-soon-list] button[data-lang]").count() == 0)
    # `.um-head` co `text-transform:uppercase` nen inner_text tra "NGÔN NGỮ" —
    # ghim mot cach viet hoa la bay da tra gia nhieu lan (quy tac 8 muc 6).
    check("tieu de tam tha da dich",
          "ngôn ngữ" in pop.inner_text().casefold(),
          pop.inner_text()[:40].replace(chr(10), " | "))

    # tam tha khong tran khoi khung nhin
    bb = pop.bounding_box()
    check("tam tha nam trong khung nhin",
          bb["x"] >= -1 and bb["x"] + bb["width"] <= w + 1
          and bb["y"] >= -1 and bb["y"] + bb["height"] <= h + 1,
          "x %.0f..%.0f  y %.0f..%.0f" % (bb["x"], bb["x"] + bb["width"],
                                          bb["y"], bb["y"] + bb["height"]))

    # bam ngon ngu chua co -> PHAI co loi nhan, va KHONG duoc ghi astroq-lang
    soon.first.click()
    pg.wait_for_timeout(600)
    shown = pg.evaluate(
        "() => Array.from(document.querySelectorAll('.toast,.auth-toast,.sel-toast'))"
        " .filter(e => e.className.indexOf('show') >= 0 || e.textContent.trim())"
        " .map(e => e.textContent.trim())")
    check("ngon ngu 'sap co' co LOI NHAN (khong im lang)",
          any("sắp ra mắt" in x.lower() or "coming" in x.lower() for x in shown),
          str(shown[:2]))
    check("ngon ngu 'sap co' KHONG ghi de astroq-lang",
          pg.evaluate("() => localStorage.getItem('astroq-lang')") == "vi")

    # doi sang EN that
    if not pop.is_visible():
        btn.click()
        pg.wait_for_timeout(300)
    pg.locator('.lang-pick [data-lang-list] button[data-lang="en"]').click()
    pg.wait_for_timeout(700)
    check("bam EN -> luu astroq-lang",
          pg.evaluate("() => localStorage.getItem('astroq-lang')") == "en")
    check("bam EN -> <html lang> doi",
          pg.evaluate("() => document.documentElement.lang") == "en")
    check("bam EN -> chip doi sang EN",
          pg.locator(".lang-pick [data-lang-code]").inner_text().strip().upper() == "EN")
    body = pg.locator("body").inner_text()
    check("bam EN -> chu tren trang doi thanh tieng Anh",
          "Ngôn ngữ" not in body, body[:60].replace(chr(10), " | "))
    check("0 loi trang", not errs, str(errs[:2]))
    ctx.close()


with sync_playwright() as p:
    br = p.chromium.launch()
    for pageName in ("landing-app.html", "select.html"):
        run(br, pageName)
        run(br, pageName, 390, 844)
    br.close()

print("")
print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
