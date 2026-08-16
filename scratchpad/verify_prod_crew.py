# -*- coding: utf-8 -*-
"""
verify_prod_crew.py — do TRANG PHI HANH DOAN tren BAN THAT astroq.org.

    python scratchpad/verify_prod_crew.py

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC. Do truoc luc Pages build xong thi
   moi ket luan deu sai — 06/08/2026 ban that tung dung o ban cu gan mot ngay.
⚠️ Do tren CHINH astroq.org, khong do o may: thu can biet la "tre that co dung
   duoc khong", ma dieu do phu thuoc ca Pages lan Lambda.
"""
import json
import sys
import urllib.request

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SITE = "https://astroq.org"
API = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
WANT_VER = "2026.08.16.5"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "astroq-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def main():
    print(f"=== Do ban that {SITE} ===\n")

    # ---------- [1] So hieu ban dung — KIEM TRUOC MOI THU ----------
    print("[1] So hieu ban dung (kiem TRUOC moi thu khac)")
    st, _, body = fetch(f"{SITE}/js/ui-common.js")
    src = body.decode("utf-8", "replace")
    check("js/ui-common.js tra 200", st == 200, str(st))
    check(f"ban dung dung {WANT_VER}", f'"{WANT_VER}"' in src,
          "Pages co the CHUA build xong — cho roi chay lai")
    if f'"{WANT_VER}"' not in src:
        print("\n  ⚠️ DUNG LAI: moi ket luan sau day se do mot ban CU.")
        return 1

    # ---------- [2] File moi tra 200 va DUNG MIME ----------
    # ⚠️ MIME phai DO chu khong duoc gia dinh.
    print("\n[2] File moi tra 200, dung MIME")
    for path, want_mime in (("/crew.html", "text/html"),
                            ("/css/crew.css", "text/css")):
        st, ct, _ = fetch(SITE + path)
        check(f"{path} tra 200", st == 200, str(st))
        check(f"{path} MIME dung", want_mime in ct, ct)

    # ---------- [3] Route /crew tren ban that ----------
    print("\n[3] Route /crew (CONG KHAI) tren ban that")
    st, ct, body = fetch(f"{API}/crew")
    check("GET /crew tra 200", st == 200, str(st))
    data = json.loads(body.decode("utf-8"))
    check("co du cap/taken/seats",
          all(k in data for k in ("cap", "taken", "seats")), str(list(data)))
    check("cap = 500", data.get("cap") == 500, str(data.get("cap")))
    # ⚠️ PHEP KIEM QUAN TRONG NHAT: khong ro mot mau du lieu ca nhan nao.
    raw = body.decode("utf-8")
    check("KHONG co ky tu @ trong phan hoi", "@" not in raw, raw[:120])
    for k in ("email", "name", "joinedAt"):
        check(f"KHONG co truong '{k}'", k not in raw)
    check("moi ghe dung {no, ch}",
          all(set(s) == {"no", "ch"} for s in data["seats"]),
          str(data["seats"][:2]))

    # ---------- [4] Mo CHINH astroq.org/crew.html ----------
    print("\n[4] Mo chinh astroq.org/crew.html tren Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": 1280, "height": 1000})
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("response",
              lambda r: bad.append(f"{r.status} {r.url.split('/')[-1]}")
              if r.status >= 400 else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(f"{SITE}/crew.html", wait_until="load", timeout=40000)
        pg.wait_for_timeout(2500)

        check("0 loi trang", not errs, str(errs[:2])[:160])
        check("0 asset hong", not bad, str(bad[:3]))

        taken = pg.inner_text("#taken")
        check("dem KHONG con dau — (tuc da doc duoc server)", taken != "—", taken)
        check("dem la mot con so", taken.isdigit(), taken)

        seats = pg.locator(".cw-seat").count()
        check("so ghe ve ra khop 'taken'", str(seats) == taken,
              f"ve {seats} · taken {taken}")
        check("KHONG ve du 500 o rong", seats < 500, str(seats))

        # ⚠️ Do tren MAN HINH, khong doc ma: khong mot chu nao cua rieng ai.
        body_txt = pg.inner_text("body")
        check("KHONG co ky tu @ tren man hinh", "@" not in body_txt)

        check("KHONG hien dai 'chua doc duoc'",
              not pg.is_visible("#banner"))
        check("chua dang nhap: KHONG hien dong 'cho cua ban'",
              not pg.is_visible("#you"))
        check("co nut ghi ten vao danh sach", pg.is_visible("#join"))

        # Dien thoai
        ctx2 = br.new_context(viewport={"width": 390, "height": 844})
        pg2 = ctx2.new_page()
        e2 = []
        pg2.on("pageerror", lambda e: e2.append(str(e)))
        pg2.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg2.goto(f"{SITE}/crew.html", wait_until="load", timeout=40000)
        pg2.wait_for_timeout(2000)
        ovf = pg2.evaluate("() => document.documentElement.scrollWidth - innerWidth")
        check("dien thoai 390: khong tran ngang", ovf <= 1, f"{ovf}px")
        cols = pg2.evaluate(
            "() => getComputedStyle(document.getElementById('grid'))"
            ".gridTemplateColumns.split(' ').length")
        check("dien thoai: luoi KHONG rot ve 1 cot", cols >= 4, f"{cols} cot")
        check("dien thoai: 0 loi trang", not e2, str(e2[:1])[:120])

        # ---------- [5] Duong vao tu menu tha o dashboard ----------
        print("\n[5] Duong vao tu menu tha sau avatar o dashboard")
        ctx3 = br.new_context(viewport={"width": 1280, "height": 1000})
        # ⚠️ Phai gieo co onboarding: khach MOI thi man Comet dan tham quan
        #    chay va `.tour-block` chan moi cu bam — dung hanh vi san pham,
        #    sai cho de do menu.
        ctx3.add_init_script(
            "localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1');")
        pg3 = ctx3.new_page()
        pg3.goto(f"{SITE}/dashboard.html", wait_until="load", timeout=40000)
        pg3.wait_for_timeout(1800)
        # ⚠️ Dashboard co HAI nut `data-menu-btn` (avatar va ngon ngu). Lay
        #    `.first` la bam nham cai ngon ngu roi bao "muc crew khong nhin
        #    thay duoc" — loi cua PHEP DO, khong phai cua trang. Phai tim dung
        #    khoi `[data-menu]` CO CHUA muc crew roi bam nut cua chinh no.
        btn = pg3.locator("[data-menu]:has(.um-item.um-crew) [data-menu-btn]")
        check("dashboard co nut mo dung menu chua muc crew", btn.count() == 1,
              str(btn.count()))
        if btn.count() == 1:
            btn.click()
            pg3.wait_for_timeout(400)
            crew_item = pg3.locator(".um-item.um-crew")
            check("menu co muc Phi Hanh Doan", crew_item.count() == 1,
                  str(crew_item.count()))
            if crew_item.count() == 1:
                check("muc do NHIN THAY duoc", crew_item.is_visible())
                with pg3.expect_navigation(timeout=20000):
                    crew_item.click()
                check("bam vao thi toi dung crew.html",
                      pg3.url.endswith("crew.html"), pg3.url)
        br.close()

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
