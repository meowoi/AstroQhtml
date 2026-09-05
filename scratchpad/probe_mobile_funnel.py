# -*- coding: utf-8 -*-
"""probe_mobile_funnel.py — DUONG DI CUA MOT LUOT BAM QUANG CAO, DO TREN DIEN THOAI THAT.

    python -m http.server 8123        # trong AstroQhtml/
    python scratchpad/probe_mobile_funnel.py

VI SAO CAN BO DO NAY (29/08/2026)
---------------------------------
Doc thang DynamoDB: **555 khach moi tu `facebook/paid/aug2026-ai-crit` -> 0 tai
khoan, 0 waitlist**. Ba ho so PROFILE duy nhat trong bang deu KHONG mang nhan
nguon (2 cai co tu truoc khi co UTM, 1 cai la tai khoan cua chinh chu du an).

Ti le 0/555 khong phai mot van de "cau chu chua hay". No lon hon the, va lu'u
luong Facebook phan lon la dien thoai — nen cho phai soi truoc tien la MAN HINH
DIEN THOAI, khong phai ban desktop ma nguoi lam vua nhin.

Bo do nay tra loi bang SO DO, khong bang cam giac:
  [1] Khach nhin thay GI trong man dau tien (390x844) — chu, nut, va thu bi che.
  [2] Nut hanh dong dau tien nam o pixel thu bao nhieu -> phai cuon bao nhieu man.
  [3] Dai "Trai nghiem tot nhat tren may tinh" che mat bao nhieu % man hinh.
  [4] Cac trang trong luong co vo bo cuc o 390px khong (tran ngang).

⚠️ DUNG VIEWPORT THAT qua Playwright, KHONG dung `--window-size` cua Chrome
   headless: da ghi trong so tay du an — `--window-size=390` thuc ra cho viewport
   ~500px, tuc do mot cai man hinh khong ai co.
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright  # noqa: E402

BASE = "http://127.0.0.1:8123"
# iPhone 14 / 15 — kho pho bien nhat trong lu'u luong quang cao Facebook o VN.
PHONE = {"width": 390, "height": 844}
SHOTS = "scratchpad/_mobile"

_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


def measure(pg, label):
    """Do man dau tien: cai gi nhin thay, nut dau tien o dau."""
    return pg.evaluate(
        """(vh) => {
      const vis = (el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' &&
               s.display !== 'none' && +s.opacity > 0.05;
      };
      // Nut/link hanh dong dau tien theo thu tu tren trang
      // ⚠️ PHAI KE DU CAC LOP NUT THAT: hero cua index.html dung `btn-primary` /
      //    `btn-ghost` (index.html:227-229), KHONG phai `.btn`. Bo sot chung thi
      //    bo do roi xuong `.wl-cta a` (duoi man 2) va bao "nut dau tien o man 2.9"
      //    — mot ket luan SAI ma anh chup bac bo ngay.
      const cands = [...document.querySelectorAll(
        'a.btn, a.btn-primary, a.btn-ghost, button.btn, .wl-cta a, #btn-try, .auth-submit')]
        .filter(vis)
        .map(el => ({ id: el.id || el.className,
                      text: (el.textContent || '').trim().slice(0, 34),
                      top: Math.round(el.getBoundingClientRect().top + scrollY) }))
        .sort((a, b) => a.top - b.top);
      // Chu nhin thay trong man dau
      const seen = [];
      document.querySelectorAll('h1,h2,h3,p,li,strong,.badge,.lede,.eyebrow').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.top < vh && r.bottom > 0 && vis(el)) {
          const t = (el.textContent || '').trim().replace(/\\s+/g, ' ');
          if (t && t.length > 2) seen.push(t.slice(0, 70));
        }
      });
      const mob = document.getElementById('mob-note');
      const mr = mob && !mob.hidden ? mob.getBoundingClientRect() : null;
      return {
        pageH: Math.round(document.documentElement.scrollHeight),
        overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
        scrollW: document.documentElement.scrollWidth,
        firstCta: cands[0] || null,
        ctas: cands.slice(0, 4),
        seen: seen.slice(0, 14),
        mobNote: mr ? { h: Math.round(mr.height), pct: Math.round(100 * mr.height / vh) } : null
      };
    }""",
        PHONE["height"],
    )


def run(pg, path, label, wait_ms=2600):
    print("\n" + "=" * 66)
    print("  " + label + "   (" + path + ")")
    print("=" * 66)
    pg.goto(BASE + path, wait_until="domcontentloaded")
    pg.wait_for_timeout(wait_ms)      # cho dai mob-note (hen 900ms) va anh
    m = measure(pg, label)
    pg.screenshot(path=SHOTS + "/" + label + ".png")

    print("  cao trang      : %d px  (= %.1f man hinh)" % (m["pageH"], m["pageH"] / PHONE["height"]))
    chk("khong tran ngang o 390px", not m["overflowX"], "scrollWidth=%d" % m["scrollW"])

    if m["firstCta"]:
        f = m["firstCta"]
        folds = f["top"] / PHONE["height"]
        print("  nut dau tien   : \"%s\"  o y=%d  (man thu %.1f)" % (f["text"], f["top"], folds + 1))
        chk("nut hanh dong o TRONG man dau tien", f["top"] < PHONE["height"],
            "y=%d / vh=%d" % (f["top"], PHONE["height"]))
    else:
        chk("co nut hanh dong nhin thay duoc", False, "khong tim thay nut nao")

    if m["mobNote"]:
        print("  dai 'may tinh' : cao %d px = **%d%% man hinh**" % (m["mobNote"]["h"], m["mobNote"]["pct"]))
        chk("dai khuyen dung may tinh KHONG chiem qua 15%% man hinh",
            m["mobNote"]["pct"] <= 15, "%d%%" % m["mobNote"]["pct"])

    print("\n  --- Chu khach doc duoc trong MAN DAU TIEN ---")
    for t in m["seen"]:
        print("    · " + t)

    ai = [t for t in m["seen"] if "AI" in t or "công nghệ" in t.lower() or "trí tuệ" in t.lower()]
    chk("man dau tien co nhac toi AI", bool(ai), ai[0][:50] if ai else "KHONG mot chu nao")
    return m


with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport=PHONE, device_scale_factor=2, is_mobile=True,
                         has_touch=True, locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))

    import os
    os.makedirs(SHOTS, exist_ok=True)

    run(pg, "/index.html?utm_source=facebook&utm_medium=paid&utm_campaign=aug2026-ai-crit",
        "1-trang-chu")
    run(pg, "/landing-app.html", "2-landing-app")

    print("\n" + "=" * 66)
    chk("0 loi JS trong ca luot", not errs, "; ".join(errs[:2]))
    br.close()

print("\nAnh luu o %s/" % SHOTS)
print("%d dat / %d dang luu y" % (_n["ok"], _n["ng"]))
