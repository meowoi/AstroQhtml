# -*- coding: utf-8 -*-
"""smoke_sw.py — service worker CO THAT SU chan duoc con ky lan cua GitHub?

    python scratchpad/smoke_sw.py

⚠️⚠️ DUNG MAY CHU RIENG CO CONG TAC 503, KHONG dung `route()` cua Playwright.
   Hai ly do:
   ① Cai can do la nhanh `status >= 500` cua sw.js. GitHub tra **503 kem HTML
     con ky lan** — do la mot phan hoi THANH CONG o tang mang, nen mot bo do
     chi `abort()` request thi khong bao gio chay qua nhanh do.
   ② [Chua kiem chung] Playwright co chan duoc request do CHINH service worker
     phat ra hay khong con tuy ban; dung mot may chu that thi khong phu thuoc
     vao chuyen do.

⚠️ localhost la NGU CANH AN TOAN nen service worker chay duoc o day. Tren mot
   ten mien that qua http thi khong — do la ly do `regSW()` xet
   `isSecureContext` chu khong xet `location.hostname`.

⚠️ CONG 8127, KHONG 8123. 8123 la cong ma ~100 bo kiem khac dung; mot service
   worker cai o day se ngoi giua chung va moi phep do cua chung.
   ⚠️ 8127 KHONG nam trong ALLOWED_ORIGINS (co y) nen loi goi API bi CORS chan
   va trinh duyet TU ghi mot dong do vao console. Vi the bo nay chan san
   origin API chu khong doi "0 loi console" mot cach mu quang.
"""
import functools
import http.server
import io
import json
import os
import re
import socketserver
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8127
BASE = "http://127.0.0.1:%d" % PORT
API_RE = re.compile(r".*execute-api.*")

# Dung nguyen van chuoi cua trang loi GitHub — de bo do bat duoc dung thu that.
UNICORN = ("<html><body><h1>We&#39;re having a really bad day.</h1>"
           "<p>The Unicorns have taken over.</p></body></html>")

MODE = {"v": "ok"}          # "ok" | "503" | "404"
ok = 0
bad = 0


def chk(name, cond, info=""):
    global ok, bad
    if cond:
        ok += 1
        print("  [OK]   %s%s" % (name, ("  (%s)" % info) if info else ""))
    else:
        bad += 1
        print("  [HONG] %s%s" % (name, ("  (%s)" % info) if info else ""))


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _fake(self, code, body, ctype="text/html; charset=utf-8"):
        raw = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        m = MODE["v"]
        # ⚠️ `sw.js` PHAI luon phuc vu that, ke ca o che do 503: tra 404 cho no
        #    la trinh duyet TU GO DANG KY (dung cong tac tat cua san pham) va
        #    bo do se do mot the gioi khong co service worker.
        if m != "ok" and not self.path.startswith("/sw.js"):
            if m == "503":
                return self._fake(503, UNICORN)
            if m == "404":
                return self._fake(404, "<html><body>not found</body></html>")
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


class Srv(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def sw_version():
    s = io.open(os.path.join(ROOT, "js", "ui-common.js"), encoding="utf-8").read()
    return re.search(r'var\s+VERSION\s*=\s*"([0-9.]+)"', s).group(1)


JS_READY = """async () => {
  const r = await navigator.serviceWorker.ready;
  return !!(r && r.active);
}"""

JS_KEYS = """async () => {
  const names = await caches.keys();
  const out = {};
  for (const n of names) {
    const c = await caches.open(n);
    out[n] = (await c.keys()).map(r => r.url);
  }
  return out;
}"""


def main():
    global ok, bad
    ver = sw_version()
    srv = Srv(("127.0.0.1", PORT), functools.partial(H, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 860}, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
        # Chan API: cong 8127 khong nam trong ALLOWED_ORIGINS nen loi goi that
        # se bi CORS chan va trinh duyet tu ghi mot dong do vao console.
        ctx.route(API_RE, lambda r: r.fulfill(status=200, content_type="application/json",
                                              body="{}"))
        # ⚠️ Do THAT thoi diem `register()` duoc goi. Ban dau toi doc
        #    `performance.getEntriesByType('resource')` tim `/sw.js` va no tra ve
        #    None — script service worker do CHINH tang service worker cua trinh
        #    duyet keo ve, KHONG nam trong resource timing cua trang. Mot phep do
        #    khong nhin thay duoc thu can do thi no khong chung minh gi.
        ctx.add_init_script("""
          (function(){
            window.__swAt = null;
            try{
              var sw = navigator.serviceWorker;
              if(!sw || !sw.register) return;
              var real = sw.register.bind(sw);
              sw.register = function(){
                window.__swAt = document.readyState;
                return real.apply(null, arguments);
              };
            }catch(e){}
          })();
        """)
        errs = []
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.set_default_timeout(30000)

        # ═══ [1] Dang ky + kich hoat, va dang ky o `load` chu khong som hon ═══
        print("\n=== [1] Cai dat ===")
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_function("() => !!navigator.serviceWorker.controller", timeout=30000)
        chk("service worker nam quyen dieu khien trang", True)

        at = pg.evaluate("() => window.__swAt")
        # ⚠️ `register()` phai duoc goi khi readyState DA la "complete" — tuc sau
        #    su kien load. Dot cat duong tai dashboard 23/08 vua ha luot quay lai
        #    1.372 -> 29 ms; dat viec cai service worker vao duong tai do la tu
        #    tay tra lai phan vua cat duoc.
        chk("register() duoc goi SAU su kien load", at == "complete", "readyState=%s" % at)

        keys = pg.evaluate(JS_KEYS)
        names = list(keys.keys())
        chk("dung MOT cache, ten mang so hieu ban dung",
            names == ["astroq-" + ver], str(names))
        urls = keys.get("astroq-" + ver, [])
        chk("vo da vao cache", len([u for u in urls if "/css/offline.css" in u]) == 1)
        chk("offline.html da vao cache", any(u.endswith("/offline.html") for u in urls))
        chk("co phong trong vo", len([u for u in urls if "/fonts/" in u]) >= 5,
            "%d font" % len([u for u in urls if "/fonts/" in u]))
        chk("KHONG cache gi tu origin khac (API/Firebase)",
            not any("execute-api" in u or "googleapis" in u for u in urls))

        # ═══ [2] Con ky lan: trang DA GHE QUA -> tra ban that tu cache ═══
        print("\n=== [2] GitHub tra 503: trang da ghe qua ===")
        # ⚠️⚠️ PHAI GHE LAI MOT LUOT NUA, va day la mot tinh chat THAT cua san
        #    pham chu khong phai mot buoc cho dep: o luot nap DAU TIEN chua co
        #    service worker nao dieu khien trang, nen `fetch` handler KHONG chay
        #    va trang do KHONG vao cache. Ban dau bo do thieu buoc nay va bao
        #    hong — doc ra y nhu "cache khong lam viec", trong khi that ra trang
        #    chua bao gio duoc cache.
        #    => Voi tre: trang DAU TIEN cua phien chua duoc cache trong chinh
        #    luot do; moi trang no di qua SAU khi service worker kich hoat thi co.
        pg.goto(BASE + "/missions.html", wait_until="load")
        cached = pg.evaluate("""async () => {
          const c = await caches.open('astroq-%s');
          const hit = await c.match('/missions.html', { ignoreSearch: true });
          return !!hit;
        }""" % ver)
        chk("trang da vao cache sau luot ghe thu hai", cached)

        MODE["v"] = "503"
        pg.goto(BASE + "/missions.html", wait_until="domcontentloaded")
        html = pg.content()
        chk("KHONG hien con ky lan", "Unicorns have taken over" not in html)
        chk("hien dung trang that", "mission-map.html" in html)
        chk("van con the dan sang ban do", pg.locator('a.big[href="mission-map.html"]').count() == 1)

        # ═══ [3] Con ky lan: trang CHUA GHE -> trang loi cua astroQ ═══
        print("\n=== [3] GitHub tra 503: trang CHUA ghe bao gio ===")
        pg.goto(BASE + "/codex.html", wait_until="domcontentloaded")
        html = pg.content()
        chk("KHONG hien con ky lan", "Unicorns have taken over" not in html)
        chk("hien trang loi cua astroQ", pg.locator("#retry").count() == 1)
        chk("dia chi GIU NGUYEN trang tre dinh xem",
            pg.url.endswith("/codex.html"), pg.url)
        # ⚠️ Trang loi phai co KIEU DANG: do la ly do vo phai nam trong precache.
        #    Doc CSS trong file khong chung minh duoc trinh duyet ap duoc no.
        # ⚠️ MOI PHEP DO O DAY PHAI CHIU DUOC VIEC PHAN TU KHONG TON TAI. Luc
        #    phep thu pha hoai cho con ky lan lot qua thi `#retry` la null va
        #    `.getBoundingClientRect()` NEM — bo do chet giua duong thay vi bao
        #    hong, doc ra y nhu "phep kiem mu" (quy tac 6 muc 6 cua CLAUDE.md).
        st = pg.evaluate("""() => {
          const b = getComputedStyle(document.body);
          const btn = document.getElementById('retry');
          const p = document.querySelector('.off-card p');
          return { bg: b.backgroundColor, img: b.backgroundImage.slice(0, 22),
                   btn: btn ? Math.round(btn.getBoundingClientRect().height) : null,
                   p: p ? (p.innerText || "") : null };
        }""")
        chk("trang loi CO kieu dang (nen toi, khong phai trang trang)",
            st["img"].startswith("radial-gradient")
            or st["bg"] not in ("rgba(0, 0, 0, 0)", "rgb(255, 255, 255)"),
            "bg=%s img=%s" % (st["bg"], st["img"]))
        chk("nut Thu lai cao >= 48px (moc WCAG + bien an toan)",
            st["btn"] is not None and st["btn"] >= 48,
            "khong co nut" if st["btn"] is None else "%dpx" % st["btn"])
        low = (st["p"] or "").casefold()
        chk("noi dung noi ra nguyen nhan, khong bat tre di kiem wifi",
            "máy chủ".casefold() in low,
            "khong co doan van" if st["p"] is None else st["p"][:48])

        # ═══ [4] 404 KHONG duoc lui ve cache ═══
        print("\n=== [4] 404 thi phai 404 that ===")
        MODE["v"] = "404"
        pg.goto(BASE + "/missions.html", wait_until="domcontentloaded")
        html = pg.content()
        chk("trang da xoa KHONG song lai tu cache",
            "not found" in html and 'a.big' not in html,
            html[:60].replace("\n", " "))
        chk("cung KHONG hien trang loi offline", pg.locator("#retry").count() == 0)

        # ═══ [5] Cache ban dung CU bi xoa ═══
        print("\n=== [5] Doi ban dung thi cache cu bi xoa ===")
        MODE["v"] = "ok"
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.evaluate("""async () => {
          const c = await caches.open('astroq-0.0.0-cu');
          await c.put('/gia-lap-ban-cu', new Response('cu'));
        }""")
        before = pg.evaluate("async () => (await caches.keys()).length")
        # Buoc service worker chay lai vong activate: unregister roi nap lai.
        pg.evaluate("""async () => {
          const r = await navigator.serviceWorker.getRegistration();
          if (r) await r.unregister();
        }""")
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_function("() => !!navigator.serviceWorker.controller", timeout=30000)
        after = pg.evaluate("async () => await caches.keys()")
        chk("cache cua ban dung khac da bi xoa",
            "astroq-0.0.0-cu" not in after and before >= 2, str(after))

        # ═══ [6] `?nosw=1` bo qua dang ky ═══
        print("\n=== [6] Cua thoat ?nosw=1 ===")
        ctx2 = b.new_context(viewport={"width": 1280, "height": 860}, locale="vi-VN")
        ctx2.route(API_RE, lambda r: r.fulfill(status=200, content_type="application/json",
                                               body="{}"))
        pg2 = ctx2.new_page()
        pg2.goto(BASE + "/missions.html?nosw=1", wait_until="load")
        pg2.wait_for_timeout(1200)
        n = pg2.evaluate("async () => (await navigator.serviceWorker.getRegistrations()).length")
        chk("KHONG dang ky service worker nao", n == 0, "%d ban dang ky" % n)
        ctx2.close()

        # ═══ [7] 0 loi trang ═══
        print("\n=== [7] Loi trang ===")
        chk("0 loi trang trong ca luot do", len(errs) == 0, str(errs[:2]))

        ctx.close()
        b.close()

    srv.shutdown()
    print("\n=== KET QUA: %d dat / %d hong ===" % (ok, bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
