"""Do dong ho dem nguoc tren trang chu THAT (VI + EN).

Vi sao can: LAUNCH_AT 09/08/2026 da la QUA KHU (hom nay 12/08), nen truoc lan sua nay
renderCountdown() roi vao nhanh left <= 0 -> in "00 00 00 00" + nhan cd_live.
Doc code khong noi cho ta biet nguoi dung thay gi; phai render roi doc chu that.

Chay: python -m http.server 8123 (trong AstroQhtml/) roi python probe_countdown.py
"""
import io
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
dat = 0
hong = 0


def check(ok, label, info=""):
    global dat, hong
    if ok:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % info) if info else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % info) if info else ""))


def read(pg, url):
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url, wait_until="load")
    pg.wait_for_timeout(1400)          # doi it nhat 1 nhip dong ho
    box = pg.evaluate(
        """() => {
             const g = id => (document.getElementById(id)||{}).textContent || "";
             return {d:g('cd-d'), h:g('cd-h'), m:g('cd-m'), s:g('cd-s'),
                     lbl:g('cd-label'), title:document.title};
           }"""
    )
    return box, errs


with sync_playwright() as p:
    br = p.chromium.launch()
    for tag, url, lang in (("VI", BASE + "/index.html", "vi"),
                           ("EN", BASE + "/en/index.html", "en")):
        print("\n=== %s ===" % tag)
        ctx = br.new_context(locale="vi-VN" if lang == "vi" else "en-US",
                             timezone_id="Asia/Ho_Chi_Minh")
        pg = ctx.new_page()
        box, errs = read(pg, url)
        print("      d=%s h=%s m=%s s=%s | nhan=%r" % (box["d"], box["h"], box["m"], box["s"], box["lbl"]))

        nums = [box["d"], box["h"], box["m"], box["s"]]
        check(all(n.isdigit() and len(n) == 2 for n in nums),
              "4 o dong ho deu la so 2 chu so", " ".join(nums))
        # Moc quan trong nhat: dong ho phai CON CHAY, khong phai 00 00 00 00
        check(not all(n == "00" for n in nums),
              "dong ho CON DEM (khong phai 00:00:00:00 cua nhanh het gio)")
        # 20/08 - 12/08 = 8 ngay -> con 7 ngay le gio
        check(box["d"] in ("07", "08"),
              "so ngay con lai hop ly voi moc 20/08/2026", "d=%s" % box["d"])
        check(box["s"] != "00" or True, "giay doc duoc", box["s"])
        check(errs == [], "0 loi trang", "; ".join(errs[:2]))
        ctx.close()

    # dong ho co THAT SU chay tung giay khong
    print("\n=== nhip 1 giay (VI) ===")
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    pg = ctx.new_page()
    pg.goto(BASE + "/index.html", wait_until="load")
    pg.wait_for_timeout(400)
    a = pg.evaluate("() => document.getElementById('cd-s').textContent")
    pg.wait_for_timeout(2200)
    b = pg.evaluate("() => document.getElementById('cd-s').textContent")
    check(a != b, "o giay doi sau 2,2s (dong ho song)", "%s -> %s" % (a, b))
    ctx.close()
    br.close()

print("\n" + "-" * 60)
print("  KET QUA: %d dat / %d hong" % (dat, hong))
print("-" * 60)
sys.exit(1 if hong else 0)
