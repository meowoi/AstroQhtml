# -*- coding: utf-8 -*-
r"""Đo trên BẢN THẬT sau khi push ngày 21/08/2026.

⚠️ KIỂM SỐ HIỆU BẢN DỰNG TRƯỚC MỌI THỨ KHÁC, và DỪNG HẲN nếu chưa khớp.
   GitHub Pages build ~1–2 phút, và ngày 06/08/2026 bản thật từng đứng ở bản cũ
   gần một ngày do deploy hết giờ hai lần liên tiếp. Đo trước lúc build xong thì
   mọi kết luận sau đó đều sai — đó chính là lý do huy hiệu `.ver-badge` tồn tại.

Ba thứ đo, theo đúng thứ tự đáng tin cậy:
  [1] số hiệu bản dựng  → chắc đang đo bản mới
  [2] file mới trả 200 + MIME đúng → `js/specimen-art.js` là script cổ điển,
      nhưng MIME sai vẫn là thứ phải ĐO chứ không được giả định
  [3] mở CHÍNH trang thật trên Chromium → tranh SVG hiện ra THẬT, 0 emoji thô,
      0 chuỗi `<svg` bị in thành chữ, 0 lỗi trang, 0 asset hỏng
"""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
SITE = "https://astroq.org"
WANT = "2026.08.21.1"

ok_n = bad_n = 0


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""), flush=True)
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""), flush=True)


def get(url):
    rq = urllib.request.Request(url, headers={"User-Agent": "astroq-verify"})
    with urllib.request.urlopen(rq, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")


print("=== [1] So hieu ban dung (kiem TRUOC moi thu khac) ===")
st, _, ui = get(SITE + "/js/ui-common.js?cb=1")
m = re.search(r'var VERSION = "([^"]+)"', ui)
got = m.group(1) if m else "?"
check(st == 200, "js/ui-common.js tra 200", str(st))
check(got == WANT, "ban dung tren Pages dung la ban vua push", "%s (doi %s)" % (got, WANT))
if got != WANT:
    print("\n⚠️ Pages CHUA build xong (hoac deploy hong). DUNG — moi ket luan sau day")
    print("   se noi ve BAN CU. Doi mot phut roi chay lai script nay.")
    sys.exit(1)

print("\n=== [2] File moi: 200 + MIME dung ===")
st, ct, art = get(SITE + "/js/specimen-art.js")
check(st == 200, "js/specimen-art.js tra 200", str(st))
check("javascript" in ct.lower(), "MIME la javascript", ct)
check("AstroQSpecimenArt" in art, "co mo global AstroQSpecimenArt")
check(art.count('viewBox="0 0 64 64"') >= 1 or "0 0 64 64" in art, "co viewBox 64x64")
# CANH BAO: phai BOC CHU THICH truoc khi tim. Ban dau cua phep kiem nay quet ca
#   file va no bao HONG vi chinh loi canh bao "KHONG CO FILTER (feGaussianBlur...)"
#   o dau js/specimen-art.js — loi "dem ca chu trong ghi chu cua chinh minh",
#   da lap rat nhieu lan trong du an. Do la ghi chu NEN CO, nen sua o PHEP KIEM.
#   `check_specimen_art.py` muc [1b] von da quet tren ma da boc chu thich.
_art = re.sub(r"/\*.*?\*/", "", art, flags=re.S)
_art = re.sub(r"^\s*//.*$", "", _art, flags=re.M)
check("feGaussianBlur" not in _art and "<filter" not in _art,
      "KHONG dung filter SVG (21 khoang x filter moi khung hinh)")
check(len(re.findall(r"\{n\}", art)) >= 20, "con dau {n} tren id gradient",
      str(len(re.findall(r"\{n\}", art))))

st, ct, css = get(SITE + "/css/common.css")
check(st == 200 and ".spart" in css, "css/common.css co rule .spart", str(st))
check("width:1em" in css.replace(" ", "") and "inline-block" in css,
      "co theo font-size (1em) va la inline-block")

print("\n=== [3] Mo CHINH trang that tren Chromium ===")
with sync_playwright() as p:
    br = p.chromium.launch()
    for tag, vw in (("desktop", {"width": 1440, "height": 900}),
                    ("dien thoai", {"width": 390, "height": 844})):
        print("\n-- %s --" % tag)
        ctx = br.new_context(viewport=vw, locale="vi-VN",
                             timezone_id="Asia/Ho_Chi_Minh")
        ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg = ctx.new_page()
        errs, dead = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: dead.append("%d %s" % (r.status, r.url))
              if r.status >= 400 else None)
        pg.goto(SITE + "/specimen-vault.html", wait_until="load", timeout=45000)
        pg.wait_for_timeout(1800)

        d = pg.evaluate("""() => {
            const pods = [...document.querySelectorAll('.pod')];
            const sp   = [...document.querySelectorAll('.pod .sp')];
            const svg  = sp.filter(e => e.querySelector('svg.spart')).length;
            // emoji tho: o .sp con chu ma KHONG co svg
            const raw  = sp.filter(e => !e.querySelector('svg.spart')
                                        && (e.textContent||'').trim().length).length;
            // chuoi '<svg' bi in ra THANH CHU o bat ky dau
            const leak = (document.body.innerText||'').includes('<svg');
            const box  = svg ? sp.find(e=>e.querySelector('svg.spart'))
                                 .getBoundingClientRect() : null;
            return {pods: pods.length, sp: sp.length, svg, raw, leak,
                    w: box ? Math.round(box.width) : 0,
                    h: box ? Math.round(box.height) : 0};
        }""")
        check(d["pods"] >= 21, "ve du khoang mau vat", "%d khoang" % d["pods"])
        check(d["svg"] == d["sp"] and d["svg"] > 0,
              "MOI o mau vat la SVG that", "%d/%d" % (d["svg"], d["sp"]))
        check(d["raw"] == 0, "0 emoji tho con lai", str(d["raw"]))
        check(not d["leak"], "0 chuoi '<svg' bi in ra thanh CHU")
        check(d["w"] > 0 and abs(d["w"] - d["h"]) <= 1,
              "tranh vuong va co that", "%dx%d" % (d["w"], d["h"]))
        check(not errs, "0 loi trang", "; ".join(errs[:2])[:90])
        check(not [x for x in dead if "/js/" in x or "/css/" in x or "/img/" in x],
              "0 asset hong", "; ".join(dead[:2])[:90])

        # huy hieu ban dung hien dung so
        v = pg.evaluate("() => {const e=document.querySelector('.ver-badge');"
                        " return e ? e.textContent.trim() : '';}")
        check(WANT in v, "huy hieu ban dung hien dung so", v)
        ctx.close()

    # dashboard: moc treo mau vat cung phai la SVG
    print("\n-- buong lai (dashboard) --")
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','vi');"
        "localStorage.setItem('astroq-tour-seen','1');"
        "localStorage.setItem('astroq-map01-seen','1');")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(SITE + "/dashboard.html", wait_until="load", timeout=45000)
    pg.wait_for_timeout(1500)
    leak = pg.evaluate("() => (document.body.innerText||'').includes('<svg')")
    check(not leak, "dashboard: 0 chuoi '<svg' in ra thanh chu")
    check(not errs, "dashboard: 0 loi trang", "; ".join(errs[:2])[:90])
    ctx.close()
    br.close()

print("\n" + "=" * 56)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
