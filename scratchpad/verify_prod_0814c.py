# -*- coding: utf-8 -*-
"""Do tren BAN THAT (astroq.org) rang khoi "Mo rong" + nhanh LIFE SCIENCE
   that su toi tay tre — khong chi tin `curl 200`.

   MIME dung la dieu kien SONG CON o day: `js/article/*.js` la ES module, va
   trinh duyet TU CHOI mot module duoc phuc vu bang `text/plain`. Da kiem bang
   curl; nhung "file tai ve duoc" van chua chung minh "tre doc duoc bai", nen
   bo nay mo trang that roi doc DOM."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

BASE = "https://astroq.org"
WITH_MORE = "art-body-in-space-changes"
OK = FAIL = 0


def chk(cond, label, info=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"  [OK]   {label}" + (f"  ({info})" if info else ""))
    else:
        FAIL += 1
        print(f"  [HONG] {label}" + (f"  ({info})" if info else ""))


def ctx_for(br, band, lang="vi"):
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','%s');"
        "localStorage.setItem('astroq-user', JSON.stringify({depth:'%s'}));" % (lang, band))
    return ctx


with sync_playwright() as p:
    br = p.chromium.launch()
    errs, bad = [], []

    for band, want_open in (("junior", False), ("senior", True)):
        print(f"\n=== Bac {band} tren ban that ===")
        ctx = ctx_for(br, band)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)

        pg.goto(f"{BASE}/library.html", wait_until="load", timeout=60000)
        pg.wait_for_selector(".card", timeout=30000)

        if band == "junior":
            n = pg.evaluate("() => AstroQArticles.all().length")
            chk(n >= 54, "muc luc tren ban that co du 54 bai", str(n))
            chips = pg.eval_on_selector_all(
                ".cat", "els=>els.map(e=>e.dataset.cat)")
            chk("life" in chips, "chip chu de `life` co tren sidebar", str(chips))
            nlife = pg.evaluate(
                "() => AstroQArticles.all().filter(a=>a.cat==='life').length")
            chk(nlife == 5, "co dung 5 bai LIFE SCIENCE", str(nlife))

        # Mo bai bang chinh duong tre di
        pg.evaluate("id=>{const c=document.querySelector(`[data-id='${id}']`); if(c)c.click();}",
                    WITH_MORE)
        pg.wait_for_selector("#reader.show", timeout=30000)
        pg.wait_for_function(
            "() => document.querySelector('#r-body')"
            "   && document.querySelector('#r-body').children.length > 0", timeout=30000)
        pg.wait_for_timeout(300)

        s = pg.evaluate("""() => {
          const h=document.getElementById('r-more');
          const b=h&&h.querySelector('.mb-body'), t=h&&h.querySelector('.mb-btn');
          return { hidden: !h||h.hidden,
                   visible: !!(b && getComputedStyle(b).display!=='none'),
                   btn: !!(t && t.offsetWidth>0), label: t?t.textContent.trim():'',
                   paras: b?b.querySelectorAll('p').length:0,
                   body: (document.getElementById('r-body')||{}).textContent||'' };
        }""")
        chk(not s["hidden"], f"[{band}] khoi Mo rong hien ra")
        chk(s["visible"] is want_open,
            f"[{band}] trang thai mac dinh dung ({'mo san' if want_open else 'gap lai'})")
        chk(s["btn"], f"[{band}] nut bam CO (bac khong khoa gi)", s["label"])
        chk(s["paras"] >= 3, f"[{band}] du doan van Mo rong", str(s["paras"]))

        if band == "junior":
            # Con so cua NASA phai toi duoc tre, dung ban dich cho gon
            chk("1%" in s["body"] and "1,5%" in s["body"],
                "than bai giu nguyen con so NASA (1% den 1,5%)")
            chk("chịu lực" in s["body"],
                "giu chu 'xuong CHIU LUC' — khong noi rong hon trang nguon")
        ctx.close()

    chk(not errs, "0 loi console / pageerror", str(errs[:3]))
    chk(not bad, "0 asset hong", str(bad[:3]))
    br.close()

print(f"\n===== {OK} dat / {FAIL} hong =====")
sys.exit(1 if FAIL else 0)
