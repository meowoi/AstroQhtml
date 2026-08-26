# -*- coding: utf-8 -*-
r"""verify_prod_0826_ui.py — TẦNG TRÌNH DUYỆT của lượt push 26/08/2026. Mở chính
`astroq.org` bằng Chromium rồi đọc lại từ DOM, từ mạng và từ thời gian.

    python scratchpad/verify_prod_0826_ui.py

⚠️⚠️ VÌ SAO CẦN TẦNG NÀY. `verify_prod_0826.py` (tầng mạng) chỉ chứng minh FILE CÓ
   MẶT và nội dung file đúng. Nó KHÔNG chứng minh trang dùng đúng thứ đó: một
   `<source type="image/avif">` vẫn có thể rơi về PNG, một `min-height` vẫn có thể
   bị rule khác thắng, và `lang-wait` vẫn có thể không bao giờ được gỡ.

⚠️ CHỐT SỐ HIỆU BẢN DỰNG TRƯỚC, y như tầng mạng — đo bản cũ thì mọi phép kiểm đạt
   một cách rỗng.

⚠️ `?nosw=1` Ở NHỮNG PHÉP ĐO MẠNG. Service worker của chính trang sẽ phục vụ lại
   từ lớp đệm và làm con số byte nói về LƯỢT QUAY LẠI chứ không phải lượt đầu —
   đúng cái bẫy đã làm `smoke_quiz_async` chập chờn 1/3 lượt (ghi 26/08).
"""
import re
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SITE = "https://astroq.org"
WANT = "2026.08.26.1"
ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))


def gate_version():
    req = urllib.request.Request(SITE + "/js/ui-common.js",
                                 headers={"Cache-Control": "no-cache"})
    s = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
    m = re.search(r'var VERSION = "([0-9.]+)"', s)
    got = m.group(1) if m else "?"
    print("=== [0] So hieu ban dung: %s (doi %s) ===" % (got, WANT))
    if got != WANT:
        sys.exit("!! Ban that chua o ban moi — DUNG HAN.")


LBL = r"""() => {
  const who = (e) => e && e.tagName
    ? e.tagName.toLowerCase() + (e.className && typeof e.className === 'string'
        ? '.' + e.className.trim().split(/\s+/)[0] : '') : '?';
  const out = [];
  for (const l of document.querySelectorAll('#labels [data-body-id]')) {
    const r = l.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    if (getComputedStyle(l).visibility === 'hidden') continue;
    const cx = Math.round(r.left + r.width / 2), cy = Math.round(r.top + r.height / 2);
    if (cx < 0 || cy < 0 || cx > innerWidth || cy > innerHeight) continue;
    const top = document.elementFromPoint(cx, cy);
    const owner = top ? top.closest('[data-body-id]') : null;
    out.push({id: l.getAttribute('data-body-id'),
              hit: owner ? owner.getAttribute('data-body-id') : null,
              topEl: who(top), dy: l.dataset.decl || '0'});
  }
  return out;
}"""


def main():
    from playwright.sync_api import sync_playwright
    gate_version()

    with sync_playwright() as p:
        b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])

        # ── [1] explorer: nhãn không đè nhãn ───────────────────────────────
        print("\n=== [1] explorer: nhan khong de nhan (2 luot) ===")
        onlbl = 0
        for lap in range(2):
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
            ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                                "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
            pg = ctx.new_page()
            pg.goto(SITE + "/explorer.html?nosw=1", wait_until="load", timeout=120000)
            try:
                pg.wait_for_function("() => window.__solarReady === true", timeout=60000)
            except Exception:
                pass
            pg.wait_for_timeout(3600)
            rows = pg.evaluate(LBL)
            bad = [r for r in rows if r["hit"] != r["id"] and ".body-lbl" in r["topEl"]]
            onlbl += len(bad)
            moved = [r["id"] for r in rows if r["dy"] not in ("0", "")]
            print("     luot %d: %d nhan hien, %d bi nhan khac de, %d nhan da bi day (%s)"
                  % (lap + 1, len(rows), len(bad), len(moved), ", ".join(moved) or "khong"))
            ctx.close()
        check("[1] KHONG nhan nao bi nhan khac de (2 luot)", onlbl == 0,
              "%d luot-nhan" % onlbl)

        # ── [2] index: cua vao hien NGAY, khong loe ngon ngu ──────────────
        print("\n=== [2] index: cua vao app ===")
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        pg = ctx.new_page()
        pg.goto(SITE + "/?nosw=1", wait_until="load", timeout=120000)
        pg.wait_for_timeout(1500)
        d = pg.evaluate("""() => {
            const cd = document.getElementById('countdown');
            const lv = document.getElementById('hero-live');
            const gr = document.querySelector('.cd-grid');
            return {live: cd.classList.contains('live'),
                    label: (document.getElementById('cd-label').textContent||'').trim(),
                    liveHidden: lv.hidden,
                    liveVis: getComputedStyle(lv).display !== 'none',
                    gridVis: gr ? getComputedStyle(gr).display !== 'none' : true,
                    cdH: Math.round(cd.getBoundingClientRect().height)};
        }""")
        check("[2] #countdown o trang thai da mo cua", d["live"], d["label"])
        check("[2] 4 o dong ho DA AN (khong con '00 00 00 00')", not d["gridVis"])
        check("[2] nut 'Vao choi ngay' HIEN", (not d["liveHidden"]) and d["liveVis"])
        check("[2] o dong ho thu gon (< 40px)", d["cdH"] < 40, "%dpx" % d["cdH"])
        ctx.close()

        # ── [3] landing-app: dien thoai khong tai anh bi an ───────────────
        print("\n=== [3] landing-app: byte anh thuc te ===")
        for w, h, mob, lbl in ((390, 844, True, "dien thoai"),
                               (1440, 900, False, "may tinh")):
            ctx = b.new_context(viewport={"width": w, "height": h}, locale="vi-VN",
                                is_mobile=mob, has_touch=mob)
            pg = ctx.new_page()
            got = []
            pg.on("response", lambda r, g=got: g.append(
                (r.url.split("/")[-1], int(r.headers.get("content-length") or 0)))
                if "image" in (r.headers.get("content-type") or "") else None)
            pg.goto(SITE + "/landing-app.html?nosw=1", wait_until="load", timeout=120000)
            pg.wait_for_timeout(5000)
            kb = sum(c for _f, c in got) / 1024.0
            navif = sum(1 for f, _c in got if f.endswith(".avif"))
            print("     %-11s %d anh, %.1f KB, %d ban AVIF" % (lbl, len(got), kb, navif))
            if mob:
                check("[3] dien thoai KHONG tai anh bi display:none (< 40 KB)",
                      kb < 40, "%.1f KB" % kb)
            else:
                check("[3] may tinh dung ban AVIF (>= 9 anh)", navif >= 9, str(navif))
                check("[3] may tinh duoi 200 KB anh (truoc la 525 KB)",
                      kb < 200, "%.1f KB" % kb)
            ctx.close()

        # ── [4] dashboard: VI thay chu som, EN khong doc phai chu Viet ────
        print("\n=== [4] dashboard: lang-wait ===")
        SNAP = """
          window.__s=[];
          const g=()=>{try{
            const m=document.querySelector('main');
            const h=document.getElementById('welcome');
            window.__s.push([Math.round(performance.now()),
              m?getComputedStyle(m).visibility:'?',
              h?(h.textContent||'').trim().slice(0,40):'']);
          }catch(e){}};
          const t=setInterval(g,100); setTimeout(()=>clearInterval(t),12000);
        """
        for lang in ("vi", "en"):
            ctx = b.new_context(viewport={"width": 1440, "height": 900},
                                locale="en-US" if lang == "en" else "vi-VN")
            ctx.add_init_script("try{localStorage.setItem('astroq-lang','%s');"
                                "localStorage.setItem('astroq-map01-seen','1')}catch(e){}" % lang)
            ctx.add_init_script(SNAP)
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:80]))
            pg.goto(SITE + "/dashboard.html?nosw=1", wait_until="load", timeout=120000)
            pg.wait_for_timeout(6000)
            snaps = pg.evaluate("() => window.__s")
            # Co luc nao `main` HIEN ma chu con sai ngon ngu khong?
            def viet(s):
                return any(c in "ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩị"
                           "òóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ" for c in s.lower())
            wrong = [t for t, vis, txt in snaps
                     if vis == "visible" and txt and (viet(txt) if lang == "en"
                                                      else not viet(txt))]
            vis_at = next((t for t, vis, txt in snaps if vis == "visible" and txt), -1)
            print("     lang=%s: <main> hien voi chu o %s ms, %d anh chup"
                  % (lang, vis_at, len(snaps)))
            check("[4] lang=%s: KHONG luc nao hien chu sai ngon ngu" % lang,
                  not wrong, "%d anh chup sai, som nhat %s ms"
                  % (len(wrong), wrong[0] if wrong else "-"))
            check("[4] lang=%s: cuoi cung <main> co hien" % lang, vis_at > 0, str(vis_at))
            check("[4] lang=%s: 0 loi trang" % lang, not errs, str(errs[:2]))
            ctx.close()

        b.close()

    print("\n=== KET QUA (tang trinh duyet): %d dat / %d hong ===" % (ok_n, bad_n))
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
