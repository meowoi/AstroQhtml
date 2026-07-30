# -*- coding: utf-8 -*-
"""
regress_auth_pages.py — kiểm không hồi quy sau khi sửa js/api.js + js/firebase-auth.js.

Hai file đó nằm trên đường đăng ký/đăng nhập, nên đổi chúng là phải soi lại
landing-app + select + luồng đi tới dashboard, không chỉ trang có tính năng mới.

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/regress_auth_pages.py
"""
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        for page_name in ("landing-app.html", "select.html", "dashboard.html",
                          "learn.html", "games.html", "quiz.html", "library.html",
                          "profile.html", "achievements.html",
                          "game-dodge.html", "game-defender.html",
                          "game-constellation.html", "explorer.html",
                          "specimen-vault.html", "mission-earth.html"):
            errs = []
            ctx = browser.new_context(viewport={"width": 1280, "height": 860})
            p = ctx.new_page()
            p.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            p.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
            p.goto(BASE + page_name, wait_until="load")
            p.wait_for_timeout(2600)     # đủ để module ES + SDK Firebase nạp xong
            real = [e for e in errs if "favicon" not in e]
            check(f"{page_name}: 0 loi console", len(real) == 0,
                  "; ".join(real)[:240] if real else "")
            ctx.close()

        # ---- Popup đăng ký/đăng nhập ở landing-app vẫn mở và vẫn nhận input ----
        errs = []
        ctx = browser.new_context(viewport={"width": 1280, "height": 860})
        p = ctx.new_page()
        p.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        p.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        p.goto(BASE + "landing-app.html", wait_until="load")
        p.wait_for_timeout(2200)
        opened = False
        for sel in ("#btn-try", ".btn-primary"):
            if p.locator(sel).count():
                p.locator(sel).first.click()
                opened = True
                break
        p.wait_for_timeout(900)
        check("landing-app: bam nut chinh khong sinh loi", opened and not errs,
              "; ".join(errs)[:200] if errs else ("khong tim thay nut" if not opened else ""))
        has_form = p.evaluate(
            "() => !!document.querySelector('input[type=email], input[type=password]')")
        check("landing-app: popup dang ky/dang nhap co o nhap", has_form)
        check("AstroQAuth co ham moi (idToken/getOnboarding/setOnboarding)",
              p.evaluate("() => !!(window.AstroQAuth && AstroQAuth.idToken"
                         " && AstroQAuth.getOnboarding && AstroQAuth.setOnboarding)"))
        # Chưa đăng nhập → phải trả { ok:false, reason:'auth' }, KHÔNG ném lỗi
        r = p.evaluate("async () => { try { return await AstroQAuth.getOnboarding(); }"
                       "catch(e){ return { threw: String(e) }; } }")
        check("Chua dang nhap: getOnboarding tra ok:false chu khong nem loi",
              isinstance(r, dict) and r.get("ok") is False and "threw" not in r, str(r))
        ctx.close()

        browser.close()

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
