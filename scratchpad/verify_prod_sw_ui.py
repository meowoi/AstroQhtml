# -*- coding: utf-8 -*-
"""Mo CHINH astroq.org tren Chromium: service worker co THAT SU dang ky
va cache duoc khong.

⚠️⚠️ File nam tren may chu KHONG chung minh no bao ve duoc mot dua tre.
   `verify_prod_sw.py` chi doc noi dung file; bo nay do HANH VI: SW co
   activate, cache co ten dung so hieu ban dung, cai vo co nam trong cache,
   va trang gay ra su co (`mission-map.html`) co mo duoc khong.
"""
import sys

from playwright.sync_api import sync_playwright

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


def main():
    global bad_n
    with sync_playwright() as p:
        br = p.chromium.launch()
        # ⚠️ Ghim `astroq-lang` — Chromium mac dinh en-US va khong o mui gio
        #    Viet Nam, nen khong ghim thi phan "tieng Viet" cua bo do lang le
        #    chay bang tieng Anh (bai hoc da ghi 29/07).
        ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
        ctx.add_init_script(
            "try{localStorage.setItem('astroq-lang','vi');}catch(e){}")
        pg = ctx.new_page()

        errs = []
        bad_req = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
        pg.on("console",
              lambda m: errs.append(m.text[:120]) if m.type == "error" else None)
        pg.on("response",
              lambda r: bad_req.append("%s %s" % (r.status, r.url[:70]))
              if r.status >= 400 else None)

        print("=== [1] Mo astroq.org: service worker co dang ky that ===")
        pg.goto(BASE + "/", wait_until="load", timeout=60000)
        # SW dang ky o su kien `load` nen phai cho no activate.
        state = pg.evaluate("""async () => {
          if (!('serviceWorker' in navigator)) return {sw:'khong ho tro'};
          const reg = await navigator.serviceWorker.getRegistration('/');
          if (!reg) return {sw:'chua dang ky'};
          const r = await navigator.serviceWorker.ready;
          // ⚠ `ready` resolve khi DA co worker active, nhung worker do
          //    co the con o `activating` dung khoanh khac ay — cho tin hieu
          //    THAT (`statechange`) chu dung doc trang thai ngay, khong thi
          //    phep do bao hong mot san pham dang chay dung.
          const w = r.active;
          if (w && w.state === 'activating') {
            await new Promise(function (res) {
              const t = setTimeout(res, 5000);
              w.addEventListener('statechange', function () {
                if (w.state === 'activated') { clearTimeout(t); res(); }
              });
            });
          }
          return {
            sw: 'ok',
            scope: r.scope,
            script: (r.active && r.active.scriptURL) || '',
            state: (r.active && r.active.state) || ''
          };
        }""")
        check("service worker DA dang ky va activate",
              state.get("sw") == "ok" and state.get("state") == "activated",
              str(state)[:110])
        check("pham vi phu ca app (scope = goc)",
              state.get("scope", "").rstrip("/") == BASE,
              state.get("scope", ""))
        check("script la /sw.js cua chinh astroq.org",
              state.get("script", "").endswith("/sw.js")
              and BASE in state.get("script", ""),
              state.get("script", ""))

        print("\n=== [2] Cache mang dung so hieu ban dung ===")
        cinfo = pg.evaluate("""async () => {
          const keys = await caches.keys();
          const mine = keys.filter(k => k.indexOf('astroq-') === 0);
          const out = {keys: keys, mine: mine, urls: []};
          if (mine.length === 1) {
            const c = await caches.open(mine[0]);
            out.urls = (await c.keys()).map(r => new URL(r.url).pathname);
          }
          return out;
        }""")
        check("dung MOT cache astroq-* (khong phinh theo ban dung)",
              len(cinfo["mine"]) == 1, str(cinfo["mine"]))
        check("ten cache = astroq-%s" % WANT,
              cinfo["mine"] == ["astroq-" + WANT], str(cinfo["mine"]))
        urls = cinfo["urls"]
        for need in ["/offline.html", "/css/offline.css", "/css/common.css",
                     "/js/ui-common.js", "/img/astroq-logo.png"]:
            check("cai vo co %s" % need, need in urls)
        fonts = [u for u in urls if u.startswith("/fonts/")]
        check("cai vo co >=5 phong", len(fonts) >= 5, "%d phong" % len(fonts))
        # ⚠️ Khong duoc cache cross-origin: SW chi nhan phan hoi opaque,
        #    khong doc duoc status nen khong biet no la 200 hay 503.
        check("0 duong cross-origin trong cache",
              all(u.startswith("/") for u in urls), str(urls[:3]))

        print("\n=== [3] Trang GAY RA su co mo duoc, 0 loi ===")
        errs.clear()
        bad_req.clear()
        pg.goto(BASE + "/mission-map.html", wait_until="load", timeout=60000)
        pg.wait_for_timeout(1500)
        body = pg.inner_text("body")[:4000]
        # ⚠️ Doi chieu CHU tren man hinh, khong chi doi chieu status: con ky lan
        #    den kem HTTP 503 (mot phan hoi THANH CONG o tang mang), nen mot
        #    phep kiem chi hoi status se khong bao gio thay no.
        low = body.casefold()
        check("KHONG hien con ky lan cua GitHub",
              "unicorn" not in low and "really bad day" not in low)
        check("KHONG hien trang loi cua minh (day la trang THAT)",
              "không mở được" not in low, low[:60])
        check("ban do nhiem vu ve ra that (co the hien tren man)",
              pg.locator(".body").count() >= 5,
              "%d thien the" % pg.locator(".body").count())
        check("0 loi trang / console", not errs, str(errs[:2]))
        check("0 tai nguyen hong", not bad_req, str(bad_req[:2]))

        print("\n=== [4] mission-map.html DA nam trong cache sau khi ghe ===")
        # ⚠️ Luot ghe DAU TIEN khong co SW nao dieu khien trang nen trang do
        #    KHONG duoc cache — day la tinh chat SAN PHAM. Tu luot dieu huong
        #    sau khi activate thi moi co.
        cached = pg.evaluate("""async () => {
          const keys = (await caches.keys()).filter(k => k.indexOf('astroq-')===0);
          if (!keys.length) return [];
          const c = await caches.open(keys[0]);
          return (await c.keys()).map(r => new URL(r.url).pathname);
        }""")
        check("mission-map.html da vao cache", "/mission-map.html" in cached,
              "%d muc trong cache" % len(cached))

        print("\n=== [5] Cua thoat ?nosw=1 ===")
        ctx2 = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
        pg2 = ctx2.new_page()
        pg2.goto(BASE + "/?nosw=1", wait_until="load", timeout=60000)
        pg2.wait_for_timeout(2500)
        n = pg2.evaluate("""async () => {
          const rs = await navigator.serviceWorker.getRegistrations();
          return rs.length;
        }""")
        check("?nosw=1 khong dang ky service worker nao", n == 0, "%d dang ky" % n)
        ctx2.close()

        ctx.close()
        br.close()

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
    return 1 if bad_n else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # ⚠️ Quy tac 6 muc 6: phep cho that bai phai TU KHAI trang thai,
        #    dung chet giua duong voi mot TimeoutError tran.
        print("\n!!! BO DO CHET GIUA DUONG: %s" % str(e)[:300])
        print("=== KET QUA: %d dat / %d hong (chua chay het) ===" % (ok_n, bad_n))
        sys.exit(1)
