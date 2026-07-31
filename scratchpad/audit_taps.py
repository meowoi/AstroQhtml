# -*- coding: utf-8 -*-
"""
audit_taps.py — liệt kê ĐẦY ĐỦ mọi vùng chạm nhỏ hơn 44x44 trên iPad, gom theo
selector để biết phải sửa ở đâu (chứ không sửa từng trang một).

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/audit_taps.py

MỐC 44x44 Ở ĐÂU RA: WCAG 2.5.5 Target Size (Enhanced) và Apple HIG. Với app cho
trẻ 8-15 dùng máy tính bảng thì đây không phải chuyện hình thức — ngón tay trẻ
lớn tương đối so với nút, và bấm trượt nút "Về Trung Tâm Điều Hướng" nghĩa là mắc
kẹt trong trang.

⚠️ WCAG CÓ NGOẠI LỆ, PHẢI TÔN TRỌNG — không thì ta đi phóng to những thứ không
   nên phóng:
   · "inline": link nằm GIỮA MỘT CÂU (như chữ "Đăng nhập" trong dải nhắc). Phóng
     to nó là phá nhịp dòng chữ. Script tự nhận diện bằng cách xem thẻ cha có
     chữ khác ngoài chính nó hay không.
   · phần tử BỊ CHE / cố tình ẩn: honeypot chống bot `.hp` ở form waitlist phải
     nhỏ và vô hình, đó là mục đích của nó.
"""
import json
from collections import defaultdict

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
USER = {"name": "Bi", "pilotName": "Bi", "character": "raica",
        "avatar": "ava/avaraica.png", "uid": "audit-uid",
        "selectedCharacter": "raica"}

DEVICES = [("iPad-mini-doc", 768, 1024), ("iPad-Pro-doc", 1024, 1366)]
PAGES = ["index.html", "landing-app.html", "select.html", "dashboard.html",
         "learn.html", "library.html", "codex.html", "quiz.html",
         "games.html", "missions.html", "profile.html", "achievements.html",
         "specimen-vault.html",
         "game-dodge.html", "game-defender.html", "game-constellation.html",
         "explorer.html", "mission-earth.html"]

PROBE = """
() => {
  const out = [];
  for (const e of document.querySelectorAll('button, a, input, select, [role=button]')) {
    const r = e.getBoundingClientRect();
    const cs = getComputedStyle(e);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (r.width < 2 || r.height < 2) continue;
    if (r.width >= 44 && r.height >= 44) continue;

    // Ngoai le "inline" cua WCAG 2.5.5: phan tu nam GIUA MOT CAU.
    // ⚠️ Phai doi the cha co CHU TRUC TIEP (nodeType 3) quanh no. Ban dau toi
    // chi so do dai textContent cua cha voi cua con — dieu kien do coi mot dai
    // nut VI|EN la "inline" (vi <button> mac dinh la inline-block va cha chua
    // ca hai chu), tuc la mien tru dung cai dang can sua nhat.
    const p = e.parentElement;
    let inline = false;
    if (p && cs.display.indexOf('inline') === 0) {
      inline = [...p.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    }
    // Phan tu co y an (honeypot, off-screen)
    const hidden = cs.opacity === '0' || r.top < -200 || r.left < -200 ||
                   cs.clipPath === 'inset(50%)' ||
                   e.getAttribute('aria-hidden') === 'true' ||
                   e.tabIndex === -1 && r.width < 12;

    out.push({
      tag: e.tagName.toLowerCase(),
      id: e.id || '',
      cls: (e.className || '').toString(),
      t: (e.textContent || e.getAttribute('aria-label') || e.getAttribute('placeholder') || '').trim().slice(0, 30),
      w: Math.round(r.width), h: Math.round(r.height),
      inline, hidden
    });
  }
  return out;
}
"""

# key -> (min w, min h, so trang, vi du chu)
groups = defaultdict(lambda: [999, 999, set(), "", False, False])

with sync_playwright() as p:
    br = p.chromium.launch()
    for name, w, h in DEVICES:
        ctx = br.new_context(viewport={"width": w, "height": h}, has_touch=True,
                             locale="vi-VN", device_scale_factor=2)
        ctx.add_init_script(
            f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
            "localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-mission01-intro-seen','1');"
            "localStorage.setItem('astroq-mob-note','1');")
        for page in PAGES:
            pg = ctx.new_page()
            pg.goto(f"{BASE}/{page}", wait_until="load", timeout=25000)
            pg.wait_for_timeout(1200)
            for it in pg.evaluate(PROBE):
                sel = it["tag"] + (("." + ".".join(it["cls"].split())) if it["cls"]
                                   else ("#" + it["id"] if it["id"] else ""))
                g = groups[sel]
                g[0] = min(g[0], it["w"]); g[1] = min(g[1], it["h"])
                g[2].add(page)
                if not g[3]:
                    g[3] = it["t"]
                g[4] = g[4] or it["inline"]
                g[5] = g[5] or it["hidden"]
            pg.close()
        ctx.close()
    br.close()

real = {k: v for k, v in groups.items() if not v[4] and not v[5]}
skip = {k: v for k, v in groups.items() if v[4] or v[5]}

print(f"=== {len(real)} nhom CAN SUA (khong thuoc ngoai le WCAG) ===")
for sel, (w, h, pages, txt, _i, _hd) in sorted(real.items(), key=lambda kv: kv[1][1]):
    print(f"  {w:>4}x{h:<4} {sel:<42} {len(pages):>2} trang   {txt!r}")

print(f"\n=== {len(skip)} nhom BO QUA (inline trong cau / co y an) ===")
for sel, (w, h, pages, txt, i, hd) in sorted(skip.items(), key=lambda kv: kv[1][1]):
    why = "inline" if i else "an"
    print(f"  {w:>4}x{h:<4} {sel:<42} [{why}]  {txt!r}")
