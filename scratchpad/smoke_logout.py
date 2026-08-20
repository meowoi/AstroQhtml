# -*- coding: utf-8 -*-
"""
smoke_logout.py — do DUONG DANG XUAT tren Chromium that.

    python -m http.server 8123      # trong AstroQhtml/
    python scratchpad/smoke_logout.py
    python scratchpad/smoke_logout.py --prod     # do tren astroq.org

⚠️⚠️ BO DO NAY SINH RA TU MOT LOI THAT (20/08/2026): chu du an bao "ko dang xuat
   duoc". Tai hien duoc bang cach lam CHAM duong tai SDK Firebase — ban cu la
   `await boot()` roi `await signOut()`, tuc ca duong dang xuat treo tren MOT lan
   `import()` qua mang. Import HONG thi nem loi -> bat duoc -> van dieu huong;
   import TREO thi `logout()` khong bao gio resolve, `.then(done, done)` khong bao
   gio chay -> BAM MA KHONG CO GI XAY RA, khong mot loi nao.
   ⇒ Phep kiem quan trong nhat o day KHONG phai "dang xuat co chay khong" ma la
     "dang xuat co chay khi MANG CHAM khong". Ca binh thuong luon xanh; chinh ca
     cham moi la ca da hong.

⚠️ Do the CACHE nao con lai: tren mot may dung chung (trong nha, phong may truong
   hoc — dung nhom nguoi dung cua trang nay) thi cache cua tre TRUOC hien ra cho
   tre SAU. Nhung TUY CHON CUA THIET BI (ngon ngu, tat tieng, giam cau hinh) thi
   PHAI GIU — xoa chung khi dang xuat la doi ngon ngu cua trang mot cach vo co.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

PROD = "--prod" in sys.argv
BASE = "https://astroq.org" if PROD else "http://127.0.0.1:8123"
OK = FAIL = 0

# Khoa cua TRE — phai biet mat sau khi dang xuat.
PER_CHILD = ["astroq-user", "astroq-asteroids", "astroq-progress",
             "astroq-mission-steps", "astroq-training", "astroq-quiz-lv",
             "astroq-route-gate", "astroq-tour-seen", "astroq-map01-seen",
             "astroq-read", "astroq-dodge-best-v2"]
# Tuy chon cua THIET BI — phai con nguyen.
DEVICE = ["astroq-lang", "astroq-sfx", "astroq-perf"]

SEED = """
  if (!sessionStorage.getItem('__s')) {
    localStorage.setItem('astroq-user', JSON.stringify(
      {name:'tran thu trang', pilotName:'tran thu trang', character:'raica',
       selectedCharacter:'raica', avatar:'ava/raica.png',
       email:'x@y.z', uid:'probe-uid'}));
    ['astroq-asteroids','astroq-progress','astroq-mission-steps',
     'astroq-training','astroq-quiz-lv','astroq-route-gate',
     'astroq-read','astroq-dodge-best-v2'].forEach(k =>
        localStorage.setItem(k, '1'));
    localStorage.setItem('astroq-tour-seen','1');
    localStorage.setItem('astroq-map01-seen','1');
    localStorage.setItem('astroq-lang','vi');
    localStorage.setItem('astroq-sfx','off');
    localStorage.setItem('astroq-perf','1');
    sessionStorage.setItem('__s','1');
  }
"""


def check(label, cond, detail=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(detail)) if detail else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(detail))


def open_logout(pg):
    """Mo menu tha roi tra ve locator cua nut Dang xuat.

    `#btn-try`-style: dashboard co HAI nut `[data-menu-btn]` (avatar va ngon ngu),
    nen phai tim dung nut mo ra menu CHUA Dang xuat — lay cai dau tien la bam nham
    nut ngon ngu roi bao "khong thay Dang xuat".
    """
    btns = pg.locator("[data-menu-btn]")
    for i in range(btns.count()):
        btns.nth(i).click()
        pg.wait_for_timeout(300)
        if pg.locator("#logout").is_visible():
            return True
    return False


def run(br, label, sdk):
    """sdk: 'ok' | 'block' (mat mang) | 'slow' (tai cham)."""
    ctx = br.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script(SEED)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))

    if sdk != "ok":
        def handler(route):
            if sdk == "slow":
                pg.wait_for_timeout(25000)   # >> han cho 2,5s, du de tai hien
            route.abort()
        pg.route("**/vendor/firebase/**", handler)

    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(2200)
    print("")
    print("=== " + label + " ===")
    check("mo duoc menu chua Dang xuat", open_logout(pg))

    before = pg.url
    pg.locator("#logout").click()
    # 6 giay: han cho trong `logout()` la 2,5s, cong cho trang kip doi.
    pg.wait_for_timeout(6000)

    check("da dieu huong khoi dashboard", pg.url != before, pg.url)
    check("ve landing-app.html", "landing-app" in pg.url, pg.url)

    left = pg.evaluate(
        "() => Object.keys(localStorage).filter(k => k.indexOf('astroq-') === 0).sort()")
    still = [k for k in PER_CHILD if k in left]
    check("da don HET cache cua tre (%d khoa)" % len(PER_CHILD),
          not still, "con: " + str(still))
    gone = [k for k in DEVICE if k not in left]
    check("GIU nguyen tuy chon cua thiet bi (ngon ngu, tat tieng, giam cau hinh)",
          not gone, "mat: " + str(gone))
    check("ngon ngu khong bi doi", pg.evaluate(
        "() => localStorage.getItem('astroq-lang')") == "vi")
    check("0 loi trang", not errs, str(errs[:2]))

    # Mo lai dashboard: KHONG duoc tu dang nhap lai.
    # `js/admin-link.js` goi `verifyAdmin()` o NEN o day, va `verifyAdmin` tung
    # goi `syncProfile` vo dieu kien — tuc no HOI SINH `astroq-user` tu phien
    # Firebase con song. Mot tac dung phu khong ai doc ten ham ma doan ra duoc.
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(3000)
    check("mo lai dashboard: KHONG tu dang nhap lai", pg.evaluate(
        "() => !localStorage.getItem('astroq-user')"),
        pg.evaluate("() => localStorage.getItem('astroq-user')"))
    # ⚠️ Don route TRUOC khi dong: handler "cham" con dang ngu, va mot route con
    #    bay lam ca bo do chet o buoc SAU (`new_context` nem TargetClosedError) —
    #    doc ra y nhu san pham hong.
    try:
        pg.unroute_all(behavior="ignoreErrors")
    except Exception:
        pass
    ctx.close()


def run_double_click(br):
    """Bam hai lan lien tiep: lan hai khong duoc lam gi la, va khong duoc de
    tre tuong nut khong an."""
    ctx = br.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script(SEED)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(2200)
    print("")
    print("=== bam Dang xuat HAI LAN ===")
    open_logout(pg)
    btn = pg.locator("#logout")
    btn.click()
    pg.wait_for_timeout(120)
    dis = pg.evaluate("() => { const b = document.getElementById('logout');"
                      " return b ? b.disabled : 'mat context'; }")
    check("nut bi vo hieu ngay sau cu bam dau (chan bam hai lan)",
          dis is True or dis == "mat context", str(dis))
    pg.wait_for_timeout(6000)
    check("van ve landing-app.html", "landing-app" in pg.url, pg.url)
    check("0 loi trang", not errs, str(errs[:2]))
    ctx.close()


def main():
    print("")
    print("  DO DUONG DANG XUAT — " + BASE)
    print("=" * 66)
    with sync_playwright() as p:
        br = p.chromium.launch()
        run(br, "SDK binh thuong", "ok")
        run(br, "SDK bi CHAN han (mat mang)", "block")
        run(br, "SDK tai CHAM — DAY LA CA DA HONG", "slow")
        run_double_click(br)
        br.close()
    print("")
    print("-" * 66)
    print("  KET QUA: %d dat / %d hong" % (OK, FAIL))
    print("-" * 66)
    print("")
    sys.exit(1 if FAIL else 0)


main()
