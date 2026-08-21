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


# ⚠️ BO DO NAY DUNG CHO GIAI DOAN TRUOC MO CUA, va no TU THANH LAC HAU vao dung
#   ngay mo cua. Ngay 21/08/2026 no bao 5 hong: dong ho dung o "00 00 00 00" va
#   so ngay = 00 — nhung do la TRANG THAI DUNG cua san pham sau 20/08 (openDoor()
#   gan `.live`, an `.cd-grid`, nang chu "DA MO CUA" thanh huy hieu). Tuc no bao
#   ve mot trang thai KHONG CON TON TAI, cung ho voi `smoke_parent` (cho `.ptiles`
#   da bo) va `smoke_weeklog` (gan cung 6 game).
#   Nay no RE NHANH theo chinh LAUNCH_AT doc tu js/index.js, nen giu duoc rang o
#   CA HAI thoi ky va khong bao gio phai sua tay nua:
#     · moc con o TUONG LAI -> doi dong ho DEM THAT, so ngay khop moc, o giay song
#     · moc DA QUA        -> doi `.live`, o dong ho DA AN, huy hieu "da mo cua" hien
import datetime as _dt, os as _os, re as _re
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_js = io.open(_os.path.join(_ROOT, "js/index.js"), encoding="utf-8").read()
_m = _re.search(r'LAUNCH_AT = new Date\("([^"]+)"\)', _js)
assert _m, "khong doc duoc LAUNCH_AT tu js/index.js"
LAUNCH = _dt.datetime.fromisoformat(_m.group(1))
NOW = _dt.datetime.now(_dt.timezone.utc).astimezone(LAUNCH.tzinfo)
PAST = NOW >= LAUNCH
DAYS_LEFT = (LAUNCH - NOW).days
print("LAUNCH_AT = %s | bay gio = %s | %s"
      % (LAUNCH.isoformat(), NOW.isoformat(),
         "DA QUA MOC -> kiem trang thai DA MO CUA" if PAST
         else "con %d ngay -> kiem dong ho DEM" % DAYS_LEFT))

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
        # ⚠️ O NGAY co the QUA 2 chu so — moc con 136 ngay thi no in "136", va ban
        #   cu doi dung 2 chu so nen bao oan voi mot cau hinh hoan toan hop le.
        #   Gio/phut/giay thi luon 2 chu so (co dem 0).
        check(all(n.isdigit() for n in nums)
              and len(box["d"]) >= 2
              and all(len(box[k]) == 2 for k in ("h", "m", "s")),
              "4 o dong ho deu la so (gio/phut/giay du 2 chu so)", " ".join(nums))
        if PAST:
            st = pg.evaluate("""() => {
                const c = document.getElementById('countdown');
                const g = c && c.querySelector('.cd-grid');
                const l = document.getElementById('cd-label');
                const vis = e => { if (!e) return false;
                  const s = getComputedStyle(e);
                  return s.display !== 'none' && s.visibility !== 'hidden'
                         && e.getClientRects().length > 0; };
                return {live: !!(c && c.classList.contains('live')),
                        gridVis: vis(g), lbl: (l && l.textContent || '').trim(),
                        lblVis: vis(l)};
            }""")
            check(st["live"], "moc da qua -> #countdown mang class .live")
            check(not st["gridVis"], "4 o dong ho DA AN (khong con 00 00 00 00)")
            check(st["lblVis"] and len(st["lbl"]) > 0,
                  "huy hieu 'da mo cua' HIEN RA THAT", st["lbl"])
        else:
            # Moc quan trong nhat: dong ho phai CON CHAY, khong phai 00 00 00 00
            check(not all(n == "00" for n in nums),
                  "dong ho CON DEM (khong phai 00:00:00:00 cua nhanh het gio)")
            # so ngay suy TU LAUNCH_AT, khong gan cung mot ngay lich
            check(box["d"] in ("%02d" % DAYS_LEFT, "%02d" % (DAYS_LEFT + 1)),
                  "so ngay con lai khop moc LAUNCH_AT",
                  "d=%s, tinh ra %d" % (box["d"], DAYS_LEFT))
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
    if PAST:
        # Sau mo cua thi dong ho DUNG YEN la DUNG — doi no "song" la doi mot thu
        # san pham co y khong lam nua.
        check(a == b, "moc da qua -> o giay dung yen (dung thiet ke)",
              "%s -> %s" % (a, b))
    else:
        check(a != b, "o giay doi sau 2,2s (dong ho song)", "%s -> %s" % (a, b))
    ctx.close()
    br.close()

print("\n" + "-" * 60)
print("  KET QUA: %d dat / %d hong" % (dat, hong))
print("-" * 60)
sys.exit(1 if hong else 0)
