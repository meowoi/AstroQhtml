# -*- coding: utf-8 -*-
r"""verify_prod_0825_ui.py — MỞ CHÍNH `astroq.org` TRÊN CHROMIUM sau lượt push
25/08/2026. Đo HÀNH VI, không đọc thẻ khai.

    python scratchpad/verify_prod_0825_ui.py

⚠️ Vì sao cần dù `verify_prod_0825.py` đã 39/0: bộ kia chỉ chứng minh **file có
   mặt và đúng MIME**. Nó KHÔNG trả lời được ba câu người dùng thật gặp:
     · thẻ lưới có THẬT SỰ kéo bản `~small` không (còn `loading="lazy"`, `srcset`,
       hay một lời gọi `imgboxHtml` sót thì đều làm lệch)
     · service worker có activate thật và có giữ `fonts/` + `vendor/` không
     · phông có về TRƯỚC lần vẽ đầu không

⚠️ CHỜ TÍN HIỆU THẬT, ĐỪNG ĐỌC NGAY SAU `ready`. `navigator.serviceWorker.ready`
   resolve khi ĐÃ có worker active, nhưng worker đó có thể còn ở `activating` đúng
   khoảnh khắc ấy — bài học 23/08/2026, đã từng báo hỏng một sản phẩm chạy đúng.
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SITE = "https://astroq.org"
WANT = "2026.08.25.1"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))


def main():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()

        # ── [1] library.html: thẻ lưới kéo bản nhỏ, hero kéo bản lớn ────────
        print("=== [1] library.html tren ban that: dem byte anh NASA theo URL ===")
        # ⚠️⚠️ PHAI GHIM BAI NAO LAM THE HERO, khong do o trang thai MAC DINH.
        #    `featured()` chon "bai CHUA DOC dau tien theo thu tu muc luc", ma bai
        #    `ord` nho nhat co `img: null` => may sach thi the hero KHONG CO ANH va
        #    phep do "hero keo ban lon" hong OAN. Ban dau cua bo nay da vap dung day,
        #    dung cai bay ma `probe_nasa_thumb.py` da ghi san.
        #    Doc danh sach id THANG tu muc luc tren BAN THAT, khong go cung.
        import re as _re
        import urllib.request as _u
        _rq = _u.Request(SITE + "/js/articles-index.js")
        _rq.add_header("User-Agent", "Mozilla/5.0 Chrome/120.0")
        with _u.urlopen(_rq, timeout=40) as _r:
            _idx = _r.read().decode("utf-8", "replace")
        _ids = _re.findall(r'id: "([^"]+)"', _idx)
        HERO = "lib-nebula"
        _read = [i for i in _ids if i != HERO]
        print("     ghim hero = %s (danh dau %d/%d bai la da doc)"
              % (HERO, len(_read), len(_ids)))
        ctx = b.new_context(viewport={"width": 1440, "height": 900},
                            device_scale_factor=2, locale="vi-VN")
        ctx.add_init_script(
            "try{localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-read'," + repr(__import__("json").dumps(_read))
            + ")}catch(e){}")
        pg = ctx.new_page()
        errs, broke, nasa = [], [], {}
        pg.on("pageerror", lambda e: errs.append(str(e)[:90]))
        pg.on("response", lambda r: (
            nasa.setdefault(r.url, r.status) if "images-assets.nasa.gov" in r.url else None,
            broke.append("%s %s" % (r.status, r.url[-48:]))
            if r.status >= 400 and "astroq.org" in r.url else None))
        pg.goto(SITE + "/library.html", wait_until="load", timeout=60000)
        for _ in range(12):
            pg.mouse.wheel(0, 1400)
            pg.wait_for_timeout(220)
        pg.wait_for_timeout(1800)
        small = [u for u in nasa if "~small" in u]
        big = [u for u in nasa if "~small" not in u]
        print("     ban nho: %d · ban lon: %d" % (len(small), len(big)))
        check("[1] 0 loi trang", not errs, str(errs[:2])[:90])
        check("[1] 0 asset cua astroq.org bi hong", not broke, str(broke[:2])[:90])
        check("[1] luoi keo ban ~small (>= 4 anh)", len(small) >= 4, "%d anh" % len(small))
        check("[1] DUNG MOT anh ban lon (chi the hero)", len(big) == 1,
              str([u.split("/")[-1] for u in big])[:70])
        check("[1] 0 anh NASA nao tra ma loi",
              all(s == 200 for s in nasa.values()),
              str({u.split("/")[-1]: s for u, s in nasa.items() if s != 200})[:70])
        sizes = pg.evaluate("""() => [...document.querySelectorAll('.imgbox img')]
            .filter(i=>i.currentSrc && /images-assets/.test(i.currentSrc))
            .map(i=>({small:/~small/.test(i.currentSrc), nw:i.naturalWidth,
                      rw:Math.round(i.getBoundingClientRect().width)}))""")
        grid = [s for s in sizes if s["small"]]
        feat = [s for s in sizes if not s["small"]]
        check("[1] anh the luoi DU NET (>= 2x be rong ve)",
              bool(grid) and all(s["nw"] >= s["rw"] * 2 for s in grid),
              "%d the, vi du %s" % (len(grid), grid[0] if grid else "-"))
        check("[1] anh the luoi KHONG du qua 2,5x (chinh loi vua sua)",
              bool(grid) and all(s["nw"] <= s["rw"] * 5 for s in grid),
              str([s for s in grid if s["nw"] > s["rw"] * 5])[:70])
        check("[1] anh hero DU NET", bool(feat) and all(s["nw"] >= s["rw"] * 2 for s in feat),
              str(feat)[:70])
        ctx.close()

        # ⚠️ Va do luon TRANG THAI MAC DINH — day la thu tre GAP THAT o luot dau,
        #    va no la ca TOT NHAT: the hero khong co anh nen 0 anh ban lon.
        print("\n=== [1b] library.html o trang thai MAC DINH (may sach) ===")
        ctx = b.new_context(viewport={"width": 1440, "height": 900},
                            device_scale_factor=2, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
        pg = ctx.new_page()
        n2 = {}
        pg.on("response", lambda r: n2.setdefault(r.url, r.status)
              if "images-assets.nasa.gov" in r.url else None)
        pg.goto(SITE + "/library.html", wait_until="load", timeout=60000)
        for _ in range(12):
            pg.mouse.wheel(0, 1400)
            pg.wait_for_timeout(200)
        pg.wait_for_timeout(1500)
        s2 = [u for u in n2 if "~small" in u]
        b2 = [u for u in n2 if "~small" not in u]
        print("     ban nho: %d · ban lon: %d" % (len(s2), len(b2)))
        check("[1b] may sach: keo dung 6 anh ban nho", len(s2) == 6, "%d anh" % len(s2))
        check("[1b] may sach: 0 anh ban lon (the hero khong co anh)", len(b2) == 0,
              str([u.split("/")[-1] for u in b2])[:70])
        ctx.close()

        # ── [2] Khối preload trong DOM thật + phông về trước lần vẽ đầu ─────
        print("\n=== [2] explorer.html: 4 dong preload, KHONG co mono ===")
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        pg = ctx.new_page()
        e2 = []
        pg.on("pageerror", lambda e: e2.append(str(e)[:90]))
        pg.goto(SITE + "/explorer.html", wait_until="load", timeout=60000)
        pg.wait_for_timeout(2500)
        pre = pg.evaluate("""() => [...document.querySelectorAll(
            'link[rel=preload][as=font]')].map(l=>l.getAttribute('href'))""")
        check("[2] explorer co dung 4 dong preload", len(pre) == 4, str(len(pre)))
        check("[2] explorer KHONG preload mono",
              not any("share-tech-mono" in u for u in pre), str(pre)[:80])
        mono_used = pg.evaluate("""() => [...document.querySelectorAll('*')]
            .filter(e=>/Share Tech Mono/i.test(getComputedStyle(e).fontFamily)
                       && (e.textContent||'').trim()).length""")
        check("[2] explorer thuc su KHONG ve chu bang mono (0 phan tu)",
              mono_used == 0, "%d phan tu" % mono_used)
        check("[2] 0 loi trang o explorer", not e2, str(e2[:2])[:90])
        ctx.close()

        print("\n=== [2b] index.html: phong xong TRUOC lan ve dau? ===")
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        pg = ctx.new_page()
        pg.goto(SITE + "/", wait_until="load", timeout=60000)
        pg.wait_for_timeout(2500)
        t = pg.evaluate("""() => {
            const f = performance.getEntriesByType('resource')
                .filter(r=>/\\.woff2$/.test(r.name));
            const fcp = performance.getEntriesByType('paint')
                .find(e=>e.name==='first-contentful-paint');
            return {n: f.length,
                    start: f.length ? Math.round(Math.min(...f.map(r=>r.startTime))) : -1,
                    end:   f.length ? Math.round(Math.max(...f.map(r=>r.responseEnd))) : -1,
                    fcp: fcp ? Math.round(fcp.startTime) : -1};
        }""")
        print("     phong: %d file · bat dau %d ms · xong %d ms · FCP %d ms"
              % (t["n"], t["start"], t["end"], t["fcp"]))
        check("[2b] co tai phong", t["n"] >= 4, "%d file" % t["n"])
        # ⚠️ Day la CHINH dieu preload sinh ra de lam: phong duoc YEU CAU gan nhu
        #    ngay lap tuc, khong phai cho parse xong dam script chan parser.
        check("[2b] phong duoc YEU CAU rat som (< 700 ms)", 0 <= t["start"] < 700,
              "%d ms" % t["start"])
        ctx.close()

        # ── [3] Service worker trên bản thật ────────────────────────────────
        print("\n=== [3] Service worker tren astroq.org ===")
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        pg = ctx.new_page()
        e3 = []
        pg.on("pageerror", lambda e: e3.append(str(e)[:90]))
        pg.goto(SITE + "/", wait_until="load", timeout=60000)
        state = pg.evaluate("""async () => {
            if (!('serviceWorker' in navigator)) return 'khong-ho-tro';
            const r = await navigator.serviceWorker.ready;
            const w = r.active;
            if (!w) return 'khong-co-active';
            if (w.state === 'activated') return 'activated';
            await new Promise(res => {
                const f = () => { if (w.state === 'activated') { w.removeEventListener('statechange', f); res(); } };
                w.addEventListener('statechange', f);
                setTimeout(res, 8000);
            });
            return w.state;
        }""")
        check("[3] service worker ACTIVATE that tren ban that", state == "activated", state)
        keys = pg.evaluate("() => caches.keys()")
        check("[3] ten cache mang dung so hieu ban dung",
              keys == ["astroq-" + WANT], str(keys))
        urls = pg.evaluate("""async () => {
            const c = await caches.open('astroq-%s');
            return (await c.keys()).map(r => new URL(r.url).pathname);
        }""" % WANT)
        fonts = [u for u in urls if u.startswith("/fonts/")]
        check("[3] cai vo giu du 5 phong", len(fonts) == 5, "%d phong" % len(fonts))
        check("[3] cai vo giu offline.html", "/offline.html" in urls)
        check("[3] 0 duong cross-origin trong cache",
              all(u.startswith("/") for u in urls))

        # Lượt thứ hai: sang explorer (đã được SW điều khiển) rồi hỏi cache
        pg.goto(SITE + "/explorer.html", wait_until="load", timeout=60000)
        pg.wait_for_timeout(4000)
        ctrl = pg.evaluate("() => !!navigator.serviceWorker.controller")
        check("[3] trang duoc SW dieu khien o luot thu hai", ctrl)
        cached = pg.evaluate("""async () => {
            const c = await caches.open('astroq-%s');
            const all = (await c.keys()).map(r => new URL(r.url).pathname);
            return {vendor: all.filter(u=>u.startsWith('/vendor/')).length,
                    css: all.filter(u=>u.startsWith('/css/')).length,
                    js: all.filter(u=>u.startsWith('/js/')).length};
        }""" % WANT)
        print("     trong cache: vendor=%d · css=%d · js=%d"
              % (cached["vendor"], cached["css"], cached["js"]))
        # ⚠️ `vendor/` la duong CACHE-TRUOC (quyet dinh 5) nen phai co trong cache.
        check("[3] `vendor/` da vao cache (quyet dinh 5)", cached["vendor"] >= 1,
              "%d muc" % cached["vendor"])
        check("[3] 0 loi trang", not e3, str(e3[:2])[:90])
        ctx.close()

        # ⚠️ Cua thoat `?nosw=1` phai con tac dung — no la thu tach bach duoc
        #    "loi cua lop dem" khoi "loi cua trang".
        print("\n=== [4] Cua thoat ?nosw=1 ===")
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        pg = ctx.new_page()
        pg.goto(SITE + "/?nosw=1", wait_until="load", timeout=60000)
        pg.wait_for_timeout(2500)
        n = pg.evaluate("async () => (await navigator.serviceWorker.getRegistrations()).length")
        check("[4] ?nosw=1 KHONG dang ky service worker nao", n == 0, "%d dang ky" % n)
        ctx.close()

        b.close()

    print("\n=== KET QUA (tang trinh duyet): %d dat / %d hong ===" % (ok_n, bad_n))
    sys.exit(0 if bad_n == 0 else 1)


if __name__ == "__main__":
    main()
