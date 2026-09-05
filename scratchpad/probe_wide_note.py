# -*- coding: utf-8 -*-
"""probe_wide_note.py — DOI CHO LOI KHUYEN "DUNG MAY TINH": bo o trang chu, dat o ban do 3D.

    python -m http.server 8123        # trong AstroQhtml/
    python scratchpad/probe_wide_note.py

VI SAO (29/08/2026)
-------------------
Chu du an chot: *"bo, loi khuyen trai nghiem tot nhat tren may tinh se de o phan
can no nhat"*. Bo do nay canh CA HAI VE — chi kiem mot ve thi hoac loi khuyen bien
mat hoan toan, hoac no van con o trang chu.

⚠️ DO TREN TRINH DUYET THAT, KHONG doc file. Mot rule CSS con trong file KHONG
   chung minh nguoi dung thay gi (bai hoc `.prog` cao 0px vi la <span> inline).
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright  # noqa: E402

BASE = "http://127.0.0.1:8123"
PHONE = {"width": 390, "height": 844}
DESKTOP = {"width": 1440, "height": 900}

_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


def phone_ctx(br, **kw):
    ctx = br.new_context(viewport=PHONE, device_scale_factor=2, is_mobile=True,
                         has_touch=True, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh", **kw)
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    # Cong 8123 khong nam trong ALLOWED_ORIGINS -> CORS chan va trinh duyet TU ghi
    # mot dong do vao console. Chan route de phep kiem "0 loi trang" khong bao oan.
    ctx.route("**://*.amazonaws.com/**",
              lambda r: r.fulfill(status=204, headers={"access-control-allow-origin": "*"}, body=""))
    return ctx


def band(pg):
    return pg.evaluate(
        """() => {
      const b = document.getElementById('perf-note');
      if (!b) return { has:false };
      const r = b.getBoundingClientRect();
      const go = document.getElementById('perf-note-go');
      const x  = document.getElementById('perf-note-x');
      const cs = go ? getComputedStyle(go) : null;
      return { has:true, hidden:b.hidden,
               vis: !b.hidden && r.width>0 && r.height>0,
               h: Math.round(r.height),
               txt: (document.getElementById('perf-note-txt')||{}).textContent || '',
               goHidden: go ? go.hidden : null,
               goDisplay: cs ? cs.display : null,
               xLabel: x ? x.getAttribute('aria-label') : null,
               xH: x ? Math.round(x.getBoundingClientRect().height) : 0 };
    }"""
    )


with sync_playwright() as p:
    br = p.chromium.launch()

    # ==================================================================
    #  [1] TRANG CHU — dai phai BIEN MAT
    # ==================================================================
    print("\n" + "=" * 66)
    print("  [1] TRANG CHU tren dien thoai — dai phai BIEN MAT")
    print("=" * 66)

    ctx = phone_ctx(br)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/index.html?utm_source=facebook&utm_medium=paid&utm_campaign=aug2026-ai-crit",
            wait_until="domcontentloaded")
    pg.wait_for_timeout(3000)   # dai cu hien sau 900ms — cho du lau de no kip lo ra

    gone = pg.evaluate(
        """() => {
      const el = document.getElementById('mob-note');
      const css = [...document.styleSheets].some(s => {
        try { return [...s.cssRules].some(r => (r.selectorText||'').includes('mob-note')); }
        catch(e){ return false; }
      });
      const txt = (document.body.innerText || '');
      return { el: !!el, css,
               chu: txt.includes('Trải nghiệm tốt nhất trên máy tính'),
               laptop: txt.includes('laptop hoặc PC') };
    }"""
    )
    chk("0 phan tu #mob-note trong DOM", not gone["el"])
    chk("0 rule CSS .mob-note con lai", not gone["css"])
    chk("0 chu 'Trai nghiem tot nhat tren may tinh'", not gone["chu"])
    chk("0 chu 'laptop hoac PC'", not gone["laptop"])

    # Dai moi ngon ngu van neo dung day (khong bi --ln-lift bo di lam hong)
    ln = pg.evaluate(
        """() => {
      const b = document.querySelector('.lang-note');
      if (!b) return null;
      const r = b.getBoundingClientRect();
      return { h: Math.round(r.height), bottom: Math.round(window.innerHeight - r.bottom) };
    }"""
    )
    print("  .lang-note: %s" % ln)
    chk("0 loi JS o trang chu", not errs, "; ".join(errs[:2]))

    # ==================================================================
    #  [2] BAN DO 3D tren dien thoai — dai phai HIEN
    # ==================================================================
    print("\n" + "=" * 66)
    print("  [2] explorer.html tren dien thoai — dai phai HIEN")
    print("=" * 66)

    pg2 = ctx.new_page()
    e2 = []
    pg2.on("pageerror", lambda e: e2.append(str(e)))
    pg2.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
    pg2.wait_for_timeout(6000)   # cho canh 3D dung xong + moc cho 1600ms

    b = band(pg2)
    print("  dai: hien=%s cao=%spx" % (b.get("vis"), b.get("h")))
    print("  chu: %s" % (b.get("txt") or "")[:90])
    chk("dai HIEN tren dien thoai", b.get("vis") is True)
    chk("noi ve BAN DO nay, khong noi chung chung",
        "bản đồ" in (b.get("txt") or "").lower())
    chk("van khuyen dung laptop/PC",
        "laptop" in (b.get("txt") or "").lower())
    chk("kind `wide` KHONG co nut hanh dong",
        b.get("goHidden") is True and b.get("goDisplay") == "none",
        "hidden=%s display=%s" % (b.get("goHidden"), b.get("goDisplay")))
    chk("nut dong co that va >=44px", (b.get("xH") or 0) >= 44, "%spx" % b.get("xH"))
    chk("nhan nut dong dich dung", (b.get("xLabel") or "") == "Đã hiểu", b.get("xLabel"))

    # bam X -> dai bien mat va KHONG nhac lai
    # ⚠️ BOC try: dai khong hien thi cu bam nay NEM va bo do CHET GIUA DUONG —
    #    khong in dong tong ket nao, doc ra y nhu "bo do khong chay" chu khong
    #    phai "san pham hong". Quy tac 6 muc 6: phep cho that bai phai TU KHAI.
    #    (Phep thu pha hoai 29/08 gap dung ca nay.)
    try:
        pg2.click("#perf-note-x", timeout=4000)
        pg2.wait_for_timeout(400)
        chk("bam X thi dai bien mat", band(pg2).get("vis") is not True)
    except Exception as e:
        chk("bam X thi dai bien mat", False,
            "khong bam duoc nut dong — dai co hien khong? vis=%s | %s"
            % (band(pg2).get("vis"), str(e).splitlines()[0][:70]))

    keys = pg2.evaluate(
        """() => ({ wide: localStorage.getItem('astroq-wide-note'),
                    perf: localStorage.getItem('astroq-perf-note') })"""
    )
    print("  localStorage: %s" % keys)
    chk("bo qua ghi KHOA RIENG `astroq-wide-note`", keys["wide"] == "1")
    chk("KHONG dong luon loi moi giam cau hinh (`astroq-perf-note` con trong)",
        keys["perf"] is None, keys["perf"])

    pg3 = ctx.new_page()
    pg3.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
    pg3.wait_for_timeout(6000)
    chk("mo lai thi KHONG nhac lai", band(pg3).get("vis") is not True)
    chk("0 loi JS o ban do 3D", not e2, "; ".join(e2[:2]))
    ctx.close()

    # ==================================================================
    #  [3] MAY TINH — dai KHONG duoc hien
    # ==================================================================
    print("\n" + "=" * 66)
    print("  [3] explorer.html tren MAY TINH — dai KHONG duoc hien")
    print("=" * 66)

    ctx2 = br.new_context(viewport=DESKTOP, locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx2.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    ctx2.route("**://*.amazonaws.com/**",
               lambda r: r.fulfill(status=204, headers={"access-control-allow-origin": "*"}, body=""))
    pg4 = ctx2.new_page()
    pg4.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
    pg4.wait_for_timeout(6000)
    chk("may tinh (chuot) thi KHONG nhac", band(pg4).get("vis") is not True)
    ctx2.close()

    # ==================================================================
    #  [4] CUA SO HEP TREN LAPTOP — van KHONG duoc nhac
    # ==================================================================
    print("\n" + "=" * 66)
    print("  [4] Cua so HEP tren laptop (chuot) — van KHONG duoc nhac")
    print("=" * 66)
    print("  ⚠️ Day la ca ma phep nhan dien CHI-XET-BE-RONG se bao oan:")
    print("     bop hep cua so Chrome tren laptop van la CHUOT, bao 'hay dung laptop'")
    print("     la vo nghia va lam nguoi dung mat tin.")

    ctx3 = br.new_context(viewport={"width": 700, "height": 800},
                          locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx3.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    ctx3.route("**://*.amazonaws.com/**",
               lambda r: r.fulfill(status=204, headers={"access-control-allow-origin": "*"}, body=""))
    pg5 = ctx3.new_page()
    pg5.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
    pg5.wait_for_timeout(6000)
    chk("cua so hep + chuot thi KHONG nhac", band(pg5).get("vis") is not True)
    ctx3.close()

    # ==================================================================
    #  [5] MAN COMET DAN DUONG — KHONG duoc chen ngang
    # ==================================================================
    print("\n" + "=" * 66)
    print("  [5] `?onboard=1` — KHONG duoc chen ngang man Comet dan duong")
    print("=" * 66)

    ctx4 = phone_ctx(br)
    pg6 = ctx4.new_page()
    pg6.goto(BASE + "/explorer.html?onboard=1", wait_until="domcontentloaded")
    pg6.wait_for_timeout(6000)
    chk("dang onboarding thi KHONG nhac", band(pg6).get("vis") is not True)
    ctx4.close()

    # ==================================================================
    #  [6] BAN EN
    # ==================================================================
    print("\n" + "=" * 66)
    print("  [6] Ban tieng Anh")
    print("=" * 66)

    ctx5 = br.new_context(viewport=PHONE, device_scale_factor=2, is_mobile=True,
                          has_touch=True, locale="en-US")
    ctx5.add_init_script("try{localStorage.setItem('astroq-lang','en')}catch(e){}")
    ctx5.route("**://*.amazonaws.com/**",
               lambda r: r.fulfill(status=204, headers={"access-control-allow-origin": "*"}, body=""))
    pg7 = ctx5.new_page()
    pg7.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
    pg7.wait_for_timeout(6000)
    b7 = band(pg7)
    print("  chu EN: %s" % (b7.get("txt") or "")[:90])
    chk("ban EN cung hien", b7.get("vis") is True)
    # ⚠️ ĐỪNG ghim nguyên văn một cụm chữ ("galaxy map"): rút gọn câu chữ — việc
    #    hoàn toàn binh thuong — la phep kiem bao hong trong khi san pham dung.
    #    Hoi dieu THAT SU muon biet: no la tieng Anh, va no van khuyen dung may tinh.
    en_txt = b7.get("txt") or ""
    co_dau = any(c in en_txt for c in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệ"
                                      "ìíỉĩịòóỏõọôồốổỗộơờớởỡợ"
                                      "ùúủũụưừứửữựỳýỷỹỵđ")
    chk("ban EN khong con ky tu co dau tieng Viet", not co_dau)
    chk("ban EN van khuyen dung laptop/PC",
        "laptop" in en_txt.lower() and "pc" in en_txt.lower())
    chk("nhan nut dong EN dich that", (b7.get("xLabel") or "") == "Got it", b7.get("xLabel"))
    ctx5.close()

    br.close()

print("\n%d dat / %d dang luu y" % (_n["ok"], _n["ng"]))
sys.exit(1 if _n["ng"] else 0)
