# -*- coding: utf-8 -*-
"""Do service worker tren BAN THAT astroq.org.

⚠️⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC, va DUNG HAN neu lech —
   Pages build mat 1-2 phut; do truoc luc build xong thi moi ket luan sau
   do deu noi ve BAN CU (06/08/2026 ban that da tung dung o ban cu gan mot
   ngay). Day la ly do huy hieu so hieu ban dung ton tai.
"""
import re
import sys
import urllib.request

WANT = "2026.08.23.7"
BASE = "https://astroq.org"

ok_n = 0
bad_n = 0


def check(label, cond, info=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % info) if info else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % info) if info else ""))


def get(path):
    req = urllib.request.Request(BASE + path, headers={
        "User-Agent": "Mozilla/5.0 astroq-verify",
        "Cache-Control": "no-cache",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, dict((k.lower(), v) for k, v in r.headers.items()), r.read()


print("=== [0] So hieu ban dung (kiem TRUOC moi thu khac) ===")
st, hdr, body = get("/js/ui-common.js?cb=%s" % WANT)
txt = body.decode("utf-8", "replace")
m = re.search(r'var VERSION = "([0-9.]+)"', txt)
got = m.group(1) if m else "?"
check("ui-common.js tra 200", st == 200, str(st))
check("VERSION = %s" % WANT, got == WANT, "doc duoc: %s" % got)
if got != WANT:
    print("\n!!! Pages CHUA build xong (ban that con o %s). DUNG — moi ket luan"
          " sau day se noi ve BAN CU. Cho roi chay lai.\n" % got)
    sys.exit(2)

print("\n=== [1] 3 file moi tra 200 voi MIME dung ===")
# ⚠️ MIME phai dung: service worker bi tu choi neu server tra text/plain.
for path, want_mime in [("/sw.js", "javascript"),
                        ("/offline.html", "text/html"),
                        ("/css/offline.css", "text/css")]:
    try:
        st, hdr, body = get(path)
    except Exception as e:
        check("%s tra 200" % path, False, str(e)[:60])
        continue
    ct = hdr.get("content-type", "")
    check("%s tra 200" % path, st == 200, str(st))
    check("%s MIME chua '%s'" % (path, want_mime), want_mime in ct, ct)

print("\n=== [2] sw.js tren ban that mang dung luat ===")
st, hdr, sw = get("/sw.js")
sw = sw.decode("utf-8", "replace")
# ⚠ Boc chu thich TRUOC khi tim: moi phep kiem dang "khong duoc chua X"
#    phai chay tren ma da bo comment, khong thi chinh loi canh bao
#    "KHONG dung cache.addAll" bi tinh la vi pham (loi "dem ca chu trong
#    ghi chu cua chinh minh" — da lap rat nhieu lan trong du an).
sw_nc = re.sub(r"/\*.*?\*/", " ", sw, flags=re.S)
m = re.search(r'var VERSION = "([0-9.]+)"', sw)
check("sw.js VERSION khop ui-common", bool(m) and m.group(1) == WANT,
      m.group(1) if m else "?")
check("ten cache mang so hieu ban dung", 'var CACHE = "astroq-" + VERSION' in sw)
check("xet `status >= 500` (5xx la phan hoi THANH CONG o tang mang)",
      "status >= 500" in sw)
check("KHONG lui ve cache o 4xx (trang da xoa phai 404 that)",
      "status >= 400" not in sw)
check("chi xu ly same-origin", "url.origin !== self.location.origin" in sw)
check("chi xu ly GET", 'req.method !== "GET"' in sw)
check("activate xoa cache ban dung khac", "caches.delete(k)" in sw)
check("skipWaiting + clients.claim", "skipWaiting()" in sw and "clients.claim()" in sw)
check("KHONG dung cache.addAll", "addAll" not in sw_nc)
check("khong cache duong /me/ /auth/ /admin/", "NEVER" in sw and "visit" in sw)

print("\n=== [3] offline.html: duong dan TUYET DOI ===")
st, hdr, off = get("/offline.html")
off = off.decode("utf-8", "replace")
rel = [u for u in re.findall(r'(?:href|src)="([^"]+)"', off)
       if not u.startswith(("http", "#", "/", "mailto:", "data:"))]
# ⚠️ SW tra trang nay MA KHONG doi URL: tre dang o /wiki/x.html thi duong
#    tuong doi phan giai thanh /wiki/css/... -> 404 -> trang loi khong co
#    kieu dang, dung luc can nhat.
check("0 duong dan tuong doi", not rel, "con: %s" % rel)
check("noindex,nofollow", 'content="noindex,nofollow"' in off)

print("\n=== [4] js/ui-common.js tren ban that dang ky service worker ===")
check("co ham regSW", "function regSW" in txt)
check("dang ky o su kien `load`", 'addEventListener("load", regSW)' in txt)
check("nap /sw.js bang duong TUYET DOI", 'register("/sw.js")' in txt)
check("xet isSecureContext", "isSecureContext" in txt)
check("co cua thoat ?nosw=1", "nosw=1" in txt)

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
