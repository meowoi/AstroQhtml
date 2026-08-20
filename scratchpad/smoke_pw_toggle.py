# -*- coding: utf-8 -*-
"""
smoke_pw_toggle.py — do NUT AN/HIEN MAT KHAU tren Chromium that.

    python -m http.server 8123      # trong AstroQhtml/
    python scratchpad/smoke_pw_toggle.py

VI SAO CAN BO DO NAY: tinh nang sinh ra tu mot ca ho tro THAT (mot nguoi dung go
mat khau vao o toan dau tron roi nhan dung mot cau "sai email hoac mat khau",
khong co cach nao biet minh go sai hay dang bat CapsLock). No mang BON cai bay da
tra gia, va ca bon deu hoi quy TRONG IM LANG neu khong co phep do:

  (1) TEN TRO NANG nam o CHU BEN TRONG nut, khong o `aria-label` — nen phai do
      bang `get_by_role(name=...)`, tuc phep tinh ten tro nang THAT.
      `inner_text` KHONG dung duoc: voi phan tu bi clip 1x1 no tra chuoi rong,
      con voi phan tu trong pane `hidden` no roi ve `textContent` va tra CA HAI
      nhan. Toi da suyt ket luan sai rang "ten tro nang rong o pane Dang ky".
  (2) DUNG MOT nhan co hieu luc, va nhan do phai an bang `clip-path` (con trong
      cay tro nang, khong hien thanh chu). `display:none` cho nhan KHONG co hieu
      luc la DUNG co che lat — bo no di thi ten tro nang doc CA HAI nhan.
      Ban dau toi viet phep kiem doi ca hai nhan khong duoc display:none, tuc doi
      mot thiet ke khac han thiet ke dang chay.
  (3) `type="button"` bat buoc: thieu no thi trong <form> day la nut submit, bam
      "xem mat khau" hoa ra gui luon bieu mau.
  (4) `reset()` luc DONG lop phu: mo lai ma mat khau van hien nguyen la de mat
      khau nguoi truoc tren man hinh cho nguoi sau (may chung trong nha, phong
      may truong hoc dung la nhom nguoi dung cua trang nay).

Do o CA HAI pane (Dang nhap + Dang ky) va CA HAI ngon ngu — bay (1) chi lo ra o
pane thu hai.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
OK = FAIL = 0


def check(label, cond, detail=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(detail)) if detail else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(detail))


def open_overlay(pg, pane):
    """Mo lop phu dang nhap/dang ky.

    `#btn-try` mo o pane DANG KY, nen muon pane dang nhap phai bam them
    `#to-login` — do bang tay moi biet, doc ma thi tuong mot cu bam la du.
    """
    pg.click("#btn-try")
    pg.wait_for_selector("#auth-overlay.show", timeout=8000)
    if pane == "login":
        pg.click("#to-login")
        pg.wait_for_selector("#auth-login:not([hidden])", timeout=8000)
    else:
        pg.wait_for_selector("#auth-register:not([hidden])", timeout=8000)


def sel(pid):
    return '[data-pw-toggle="' + pid + '"]'


def run_pane(br, lang, nm_show, nm_hide, pane, pid):
    global OK, FAIL
    ctx = br.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','" + lang + "');"
        "localStorage.removeItem('astroq-user');")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/landing-app.html", wait_until="load")
    print("")
    print("=== [" + lang + " / " + pane + "] ===")
    open_overlay(pg, pane)

    inp = pg.locator("#" + pid)
    btn = pg.locator(sel(pid))
    inp.fill("vycatcute")

    check("o mat khau khoi dau la type=password",
          inp.get_attribute("type") == "password", inp.get_attribute("type"))
    check("nut la type=button (khong submit bieu mau)",
          btn.get_attribute("type") == "button", btn.get_attribute("type"))
    check("aria-pressed khoi dau = false",
          btn.get_attribute("aria-pressed") == "false",
          btn.get_attribute("aria-pressed"))
    # (1) ten tro nang THAT, do bang role — khong doc inner_text
    check("ten tro nang la " + nm_show,
          pg.get_by_role("button", name=nm_show).count() >= 1)

    # nut nam TRONG o nhap, va o nhap chua cho san cho no
    bi = inp.bounding_box()
    bb = btn.bounding_box()
    check("nut nam trong o nhap",
          bb["x"] > bi["x"] and bb["x"] + bb["width"] <= bi["x"] + bi["width"] + 1,
          "o %.0f..%.0f | nut %.0f..%.0f"
          % (bi["x"], bi["x"] + bi["width"], bb["x"], bb["x"] + bb["width"]))
    pr = inp.evaluate("el => parseFloat(getComputedStyle(el).paddingRight)")
    check("o nhap chua cho cho nut (padding-right >= be rong nut)",
          pr >= bb["width"] - 1, "padding %.0f vs nut %.0f" % (pr, bb["width"]))

    # (2) DUNG MOT nhan co hieu luc, va nhan do bi CLIP (an khoi mat, con trong
    #     cay tro nang). `display:none` cho nhan KHONG co hieu luc la DUNG co che
    #     — bo no di thi ten tro nang doc CA HAI nhan ("Hien mat khau An mat
    #     khau"). Ban dau toi viet phep kiem doi ca hai nhan khong duoc
    #     display:none, tuc doi mot thiet ke khac han thiet ke dang chay.
    lbl = pg.eval_on_selector_all(
        sel(pid) + " .pw-lbl",
        "els => els.map(e => { const c = getComputedStyle(e); return "
        "{d: c.display, w: e.getBoundingClientRect().width, clip: c.clipPath}; })")
    live = [x for x in lbl if x["d"] != "none"]
    check("dung MOT nhan co hieu luc", len(lbl) == 2 and len(live) == 1,
          str([x["d"] for x in lbl]))
    if live:
        check("nhan co hieu luc bi clip (khong hien thanh chu)",
              live[0]["w"] <= 2 and "inset" in (live[0]["clip"] or ""),
              "rong %.1fpx clip=%s" % (live[0]["w"], live[0]["clip"]))

    # bam: lat sang text
    btn.click()
    check("bam -> type=text", inp.get_attribute("type") == "text",
          inp.get_attribute("type"))
    check("bam -> aria-pressed=true",
          btn.get_attribute("aria-pressed") == "true",
          btn.get_attribute("aria-pressed"))
    check("gia tri mat khau khong bi mat", inp.input_value() == "vycatcute",
          inp.input_value())
    # (1) ten tro nang phai LAT theo, va ten cu phai BIEN
    check("ten tro nang lat sang " + nm_hide,
          pg.get_by_role("button", name=nm_hide).count() >= 1)
    check("khong con ten " + nm_show,
          pg.get_by_role("button", name=nm_show).count() == 0)
    # (3) bam khong gui bieu mau -> lop phu con mo
    check("bam nut KHONG gui bieu mau (lop phu con mo)",
          pg.locator("#auth-overlay.show").count() == 1)

    # bam lai: ve password
    btn.click()
    check("bam lai -> ve type=password",
          inp.get_attribute("type") == "password", inp.get_attribute("type"))

    # (4) dong lop phu -> reset ve an
    btn.click()
    check("truoc khi dong: dang hien", inp.get_attribute("type") == "text")
    pg.click("#auth-close")
    pg.wait_for_timeout(350)
    open_overlay(pg, pane)
    check("mo lai -> mat khau ve AN (reset khi dong)",
          pg.locator("#" + pid).get_attribute("type") == "password",
          pg.locator("#" + pid).get_attribute("type"))
    check("mo lai -> aria-pressed ve false",
          pg.locator(sel(pid)).get_attribute("aria-pressed") == "false")

    check("0 loi trang", not errs, str(errs[:2]))
    ctx.close()


def run_mobile(br, pane, pid):
    ctx = br.new_context(viewport={"width": 390, "height": 844},
                         has_touch=True, is_mobile=True)
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
    pg = ctx.new_page()
    pg.goto(BASE + "/landing-app.html", wait_until="load")
    print("")
    print("=== [dien thoai 390x844 / " + pane + "] ===")
    open_overlay(pg, pane)
    bb = pg.locator(sel(pid)).bounding_box()
    # Vung cham noi bang pseudo-element TRONG SUOT, nen `bounding_box` cua nut
    # van la 30x30 — phai do bang `elementFromPoint` o cac diem quanh nut, dung
    # khuon da dung cho vung cham cua ban do nhiem vu. Doc CSS khong tra loi duoc
    # cau "ngon tay cham vao day co trung nut khong".
    cx = bb["x"] + bb["width"] / 2.0
    cy = bb["y"] + bb["height"] / 2.0
    R = 22.0   # nua cua 44px: moc toi thieu WCAG 2.5.5
    pts = [(cx - R, cy), (cx + R, cy), (cx, cy - R), (cx, cy + R)]
    hit = pg.evaluate(
        "pts => pts.map(p => { const el = document.elementFromPoint(p[0], p[1]);"
        " return el ? (el.closest('[data-pw-toggle]') ? 'nut' : el.tagName) : 'null'; })",
        [[x, y] for x, y in pts])
    check("vung cham phu du 44px (do bang elementFromPoint)",
          all(h == "nut" for h in hit), str(hit))
    check("nut ve ra van 30x30 (khong phong to, khong pha bo cuc)",
          abs(bb["width"] - 30) <= 1 and abs(bb["height"] - 30) <= 1,
          "%.0fx%.0f" % (bb["width"], bb["height"]))
    inp = pg.locator("#" + pid)
    inp.fill("abc")
    pg.locator(sel(pid)).click()
    check("cham -> hien mat khau", inp.get_attribute("type") == "text",
          inp.get_attribute("type"))
    bi = inp.bounding_box()
    check("khong tran ngang", bi["x"] + bi["width"] <= 391,
          "%.0f" % (bi["x"] + bi["width"]))
    ctx.close()


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        for lang, nm_show, nm_hide in (
                ("vi", "Hiện mật khẩu", "Ẩn mật khẩu"),
                ("en", "Show password", "Hide password")):
            for pane, pid in (("login", "login-pass"), ("register", "reg-pass")):
                run_pane(br, lang, nm_show, nm_hide, pane, pid)
        for pane, pid in (("login", "login-pass"), ("register", "reg-pass")):
            run_mobile(br, pane, pid)
        br.close()

    print("")
    print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
    sys.exit(1 if FAIL else 0)


main()
