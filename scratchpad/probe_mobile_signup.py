# -*- coding: utf-8 -*-
"""probe_mobile_signup.py — DEM SO BUOC TU "BAM QUANG CAO" TOI "CO TAI KHOAN".

    python -m http.server 8123        # trong AstroQhtml/
    python scratchpad/probe_mobile_signup.py

VI SAO CAN BO DO NAY (29/08/2026)
---------------------------------
`probe_mobile_funnel.py` do MAN DAU TIEN va cho ra 8/0 — man hinh dau khong
hong. Nhung DynamoDB van doc ra **555 khach tu facebook/paid -> 0 tai khoan**.
=> Cho hong nam SAU man dau, tuc trong chinh duong dang ky.

Bo do nay tra loi bang SO DO:
  [1] Tu index.html toi o dang ky mat MAY CU CHAM? (di theo nut CHINH cua hero)
  [2] Duong tat `#dangky` co that su bo bot mot buoc khong?
  [3] O nhap va nut gui co dung co tren man 390px khong (>=44px, khong tran)?
  [4] Gui form xong thi trang NOI GI — co noi ra rang con phai mo hom thu khong?

⚠️ KHONG gui form len bang THAT. Moi loi goi mang ra ngoai deu bi chan;
   `/auth/register` duoc tra ve mot phan hoi gia (202 + pending) de di dung
   nhanh code that ma khong tao mot ban ghi PENDING# nao trong DynamoDB.
   (Bai hoc 16/08: bo do cham du lieu that thi phai tu don — o day chon
   duong khong cham gi ca.)

⚠️ DUNG VIEWPORT THAT qua Playwright, KHONG dung `--window-size` cua Chrome
   headless: `--window-size=390` thuc ra cho viewport ~500px.
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright  # noqa: E402

BASE = "http://127.0.0.1:8123"
PHONE = {"width": 390, "height": 844}
UTM = "?utm_source=facebook&utm_medium=paid&utm_campaign=aug2026-ai-crit"
SHOTS = "scratchpad/_mobile"

_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


def box(pg, sel):
    return pg.evaluate(
        """(s) => {
      const el = document.querySelector(s);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y),
               w: Math.round(r.width), h: Math.round(r.height),
               vis: r.width > 0 && r.height > 0 };
    }""",
        sel,
    )


def stub_api(ctx):
    """Chan moi loi goi ra ngoai; tra phan hoi gia cho /auth/register.

    ⚠️ THU TU DANG KY LA LUAT: Playwright khop route theo thu tu NGUOC —
       cai dang ky SAU thang. Dat luat rong (`*.amazonaws.com`) sau luat hep
       (`/auth/register`) thi luat rong an het, va man hinh hien ra
       "Khong ket noi duoc may chu" — doc ra y het mot loi san pham.
    """
    ctx.route("**://*.googleapis.com/**", lambda r: r.abort())
    ctx.route("**://*.gstatic.com/**", lambda r: r.abort())
    ctx.route("**://*.amazonaws.com/**", lambda r: r.abort())
    # ---- tu day tro xuong la luat HEP, phai dang ky SAU de thang ----
    ctx.route("**/visit", lambda r: r.fulfill(status=204, headers={"access-control-allow-origin": "*"}, body=""))
    ctx.route(
        "**/auth/register",
        lambda r: r.fulfill(
            status=202,
            content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body=json.dumps({"ok": True, "state": "pending", "mailSent": True}),
        ),
    )


def open_phone(br):
    ctx = br.new_context(viewport=PHONE, device_scale_factor=2, is_mobile=True,
                         has_touch=True, locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    stub_api(ctx)
    return ctx


def reg_open(pg):
    return pg.evaluate(
        """() => {
      const ov = document.getElementById('auth-overlay');
      const rg = document.getElementById('auth-register');
      return !!(ov && ov.classList.contains('show') && rg && !rg.hidden);
    }"""
    )


with sync_playwright() as p:
    br = p.chromium.launch()
    import os
    os.makedirs(SHOTS, exist_ok=True)

    # ================================================================
    #  [1] DUONG CHINH: bam nut chinh cua hero
    # ================================================================
    print("\n" + "=" * 66)
    print("  [1] DUONG CHINH — nut dau tien cua hero")
    print("=" * 66)

    ctx = open_phone(br)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))

    pg.goto(BASE + "/index.html" + UTM, wait_until="domcontentloaded")
    pg.wait_for_timeout(2600)

    taps = 0
    b = box(pg, "#hero-live")
    print("  nut hero       : #hero-live  y=%s  (%s)" % (b and b["y"], pg.eval_on_selector("#hero-live", "e=>e.textContent.trim()")))
    pg.click("#hero-live")
    taps += 1
    pg.wait_for_load_state("domcontentloaded")
    pg.wait_for_timeout(1800)
    print("  -> %s" % pg.url.replace(BASE, ""))
    chk("bam nut hero thi sang landing-app", "landing-app" in pg.url, pg.url.replace(BASE, ""))
    chk("nhung o dang ky CHUA mo", not reg_open(pg), "phai bam them")

    b = box(pg, "#btn-try")
    print("  nut tiep       : #btn-try  y=%s  (%s)" % (b and b["y"], pg.eval_on_selector("#btn-try", "e=>e.textContent.trim()")))
    pg.click("#btn-try")
    taps += 1
    pg.wait_for_timeout(900)
    open_now = reg_open(pg)
    print("  o dang ky mo   : %s" % open_now)
    pg.screenshot(path=SHOTS + "/3-dangky-duong-chinh.png")

    print("\n  >>> SO CU CHAM tu trang chu toi O DANG KY: %d" % (taps + (0 if open_now else 1)))
    chk("duong chinh toi o dang ky trong <=2 cu cham", taps <= 2 and open_now, "taps=%d open=%s" % (taps, open_now))

    # ================================================================
    #  [2] DUONG TAT: nut "Tao tai khoan" o khoi waitlist
    # ================================================================
    print("\n" + "=" * 66)
    print("  [2] DUONG TAT — nut 'Tao tai khoan' (#dangky)")
    print("=" * 66)

    pg2 = ctx.new_page()
    pg2.goto(BASE + "/index.html" + UTM, wait_until="domcontentloaded")
    pg2.wait_for_timeout(2600)

    b = box(pg2, ".wl-cta a")
    y = b["y"] + pg2.evaluate("scrollY") if b else -1
    print("  nut tat        : y=%d  (man thu %.1f)" % (y, y / PHONE["height"] + 1))
    chk("nut tat nam NGOAI man dau tien", y >= PHONE["height"],
        "y=%d — khach phai cuon %.1f man moi thay" % (y, y / PHONE["height"]))

    pg2.click(".wl-cta a")
    pg2.wait_for_load_state("domcontentloaded")
    pg2.wait_for_timeout(1500)
    open_tat = reg_open(pg2)
    print("  -> %s   o dang ky mo: %s" % (pg2.url.replace(BASE, ""), open_tat))
    chk("duong tat mo THANG o dang ky (1 cu cham)", open_tat)

    # ================================================================
    #  [3] O NHAP VA NUT GUI TREN MAN 390px
    # ================================================================
    print("\n" + "=" * 66)
    print("  [3] O NHAP / NUT GUI o 390px")
    print("=" * 66)

    pg2.screenshot(path=SHOTS + "/4-form-dangky.png")

    fields = pg2.evaluate(
        """() => {
      const rg = document.getElementById('auth-register');
      const out = [];
      rg.querySelectorAll('input, button[type=submit], button.auth-submit').forEach(el => {
        const r = el.getBoundingClientRect();
        out.push({ tag: el.tagName.toLowerCase(), type: el.type || '', id: el.id || '',
                   w: Math.round(r.width), h: Math.round(r.height),
                   ph: el.placeholder || (el.textContent || '').trim().slice(0, 24) });
      });
      return out;
    }"""
    )
    for f in fields:
        print("    %-8s %-14s %3dx%-3d  %s" % (f["tag"], f["id"], f["w"], f["h"], f["ph"]))

    # ⚠️ SAN LA 48px, KHONG PHAI 44. 44 la moc TOI THIEU cua WCAG 2.5.5; dat dung
    #    moc toi thieu la khong con bien an toan nao, va du an da co mot ca phep
    #    kiem chap chon that vi ly do do (xem `css/common.css`). Ha nguong ve 44
    #    o day la ghi mot cai bar SAI vao bo do.
    small = [f for f in fields if f["h"] < 48]
    chk("moi o nhap/nut cao >=48px (san cua du an)", not small,
        "; ".join("%s=%dpx" % (f["id"] or f["tag"], f["h"]) for f in small))

    ov = pg2.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
    chk("popup khong lam tran ngang", not ov)

    n_fields = len([f for f in fields if f["tag"] == "input"])
    print("\n  >>> SO O PHAI DIEN: %d" % n_fields)

    # ================================================================
    #  [4] GUI FORM XONG THI TRANG NOI GI
    # ================================================================
    print("\n" + "=" * 66)
    print("  [4] SAU KHI GUI — trang noi gi?")
    print("=" * 66)

    pg2.fill("#reg-name", "Bin")
    pg2.fill("#reg-email", "zztest-mobile@example.com")
    pg2.fill("#reg-pass", "matkhau123")
    pg2.click("#auth-register button[type=submit]")
    pg2.wait_for_timeout(2200)

    said = pg2.evaluate(
        """() => {
      const v = document.getElementById('auth-verify');
      const shown = v && !v.hidden;
      return { shown: !!shown,
               text: shown ? (v.innerText || '').replace(/\\s+/g, ' ').trim() : '' };
    }"""
    )
    pg2.screenshot(path=SHOTS + "/5-sau-khi-gui.png")
    print("  pane 'cho kich hoat' hien: %s" % said["shown"])
    if said["text"]:
        print("  --- chu khach doc duoc ---")
        for line in said["text"].split(". "):
            if line.strip():
                print("    · " + line.strip())

    chk("sau khi gui co man 'cho kich hoat'", said["shown"])
    low = said["text"].lower()
    chk("noi ro phai MO HOM THU", ("hòm thư" in low or "email" in low),
        "" if ("hòm thư" in low or "email" in low) else "KHONG nhac toi hom thu")

    print("\n" + "=" * 66)
    chk("0 loi JS trong ca luot", not errs, "; ".join(errs[:2]))
    br.close()

print("\nAnh luu o %s/" % SHOTS)
print("%d dat / %d dang luu y" % (_n["ok"], _n["ng"]))
