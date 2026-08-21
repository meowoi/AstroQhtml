# -*- coding: utf-8 -*-
r"""Do cờ `map01Seen`: nó phải được GHI lên server và ĐỌC lại được.

Chủ dự án báo: *"tài khoản khách thỉnh thoảng bị lỗi, đã log in out ra vào mấy lần
rồi vẫn bị yêu cầu chạy lại luồng nhiệm vụ hành tinh xanh ban đầu"*.

⚠️⚠️ ĐO ĐƯỢC NGUYÊN NHÂN, KHÔNG SUY ĐOÁN: `js/firebase-auth.js` là `type="module"`
nên nó chạy SAU khối script cổ điển của dashboard. Đo trên trang thật: lúc
`mapFirst()` chạy thì `typeof window.AstroQAuth === "undefined"`, và cả lượt tải
trang có **0** lời gọi `/me/onboarding`. Tức cờ chưa bao giờ được ghi lẫn đọc; mà
từ 20/08/2026 đăng xuất dọn `astroq-map01-seen` (đúng — đó là dữ liệu của MỘT đứa
trẻ), nên app không còn chỗ nào nhớ.

⚠️ BỘ ĐO PHẢI GIEO `AstroQAuth` MUỘN. Gieo bằng `add_init_script` là gieo TRƯỚC mọi
script của trang — một thứ tự KHÔNG BAO GIỜ xảy ra ở bản thật, và đó đúng là điểm
mù đã để lọt lỗi `shop.html` 13/08 (bộ đo 46/0 trong khi cửa hàng hiện 0 món).
Ở đây stub được gắn vào `DOMContentLoaded` — đúng lúc module ES thật chạy.
"""
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123"
ok_n = bad_n = 0


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""), flush=True)
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""), flush=True)


PROFILE = ('{"name":"Bin","pilotName":"Bin","character":"sirius",'
           '"selectedCharacter":"sirius","avatar":"ava/sirius.png",'
           '"email":"bin@example.com","uid":"u-test-1"}')


def boot(br, cache, server_seen, late=True):
    """`cache` = gia tri astroq-map01-seen · `server_seen` = co server tra ve
       (None = khong gieo AstroQAuth chut nao -> mo phong SDK khong nap duoc)."""
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    seed = ("localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-user'," + repr(PROFILE) + ");")
    if cache is not None:
        seed += "localStorage.setItem('astroq-map01-seen'," + repr(cache) + ");"
    stub = ""
    if server_seen is not None:
        stub = ("""
        window.__calls = [];
        var install = function(){
          window.AstroQAuth = {
            getOnboarding: function(){
              window.__calls.push("get");
              return Promise.resolve({ok:true, tourSeen:true, intro01Seen:true,
                                      earth1Greeted:true, map01Seen:%s});
            },
            setOnboarding: function(o){
              window.__calls.push("set:" + JSON.stringify(o));
              return Promise.resolve({ok:true});
            },
            getMissions: function(){ return Promise.resolve({ok:false}); },
            postProgress: function(){ return Promise.resolve({ok:false}); },
            idToken: function(){ return Promise.resolve(null); }
          };
        };
        %s
        """ % ("true" if server_seen else "false",
               "document.addEventListener('DOMContentLoaded', install);"
               if late else "install();"))
    ctx.add_init_script(seed + stub)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/dashboard.html", wait_until="load", timeout=30000)
    pg.wait_for_timeout(3200)
    return ctx, pg, errs


with sync_playwright() as p:
    br = p.chromium.launch()

    print("=== (1) Da xem o may nay -> PHAI day co len server ===")
    ctx, pg, errs = boot(br, "1", False)
    calls = pg.evaluate("() => window.__calls || []")
    check(any(c.startswith("set:") and "map01Seen" in c for c in calls),
          "co day co map01Seen len server", str(calls))
    check("explorer.html" not in pg.url, "KHONG bi day lai ra ban do", pg.url)
    check(not errs, "0 loi trang", "; ".join(errs[:1])[:80])
    ctx.close()

    print("\n=== (2) May sach + server noi DA xem -> khong dan lai, ghi lai cache ===")
    ctx, pg, errs = boot(br, None, True)
    calls = pg.evaluate("() => window.__calls || []")
    check("get" in calls, "co HOI server", str(calls))
    check("explorer.html" not in pg.url, "KHONG bi day lai ra ban do", pg.url)
    check(pg.evaluate("() => localStorage.getItem('astroq-map01-seen')") == "1",
          "ghi lai cache de lan sau khoi hoi mang")
    check(not errs, "0 loi trang", "; ".join(errs[:1])[:80])
    ctx.close()

    print("\n=== (3) May sach + server noi CHUA xem -> dan qua ban do (dung y do) ===")
    ctx, pg, errs = boot(br, None, False)
    check("explorer.html" in pg.url and "onboard=1" in pg.url,
          "duoc dan qua ban do", pg.url)
    ctx.close()

    print("\n=== (4) SDK khong nap duoc -> TUYET DOI khong dan lai (fail-safe) ===")
    ctx, pg, errs = boot(br, None, None)
    check("explorer.html" not in pg.url,
          "khong doc duoc co thi KHONG nem tre ve man gioi thieu", pg.url)
    check(not errs, "0 loi trang", "; ".join(errs[:1])[:80])
    ctx.close()
    br.close()

print("\n" + "=" * 58)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
