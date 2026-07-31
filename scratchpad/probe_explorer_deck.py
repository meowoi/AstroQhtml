# -*- coding: utf-8 -*-
"""probe_explorer_deck.py — soi kỹ chỗ chữ bị cắt ở bảng bên trái của explorer
trên iPad mini 768px, để biết đó là ellipsis CÓ Ý hay chữ bị chặt ngang.

    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/probe_explorer_deck.py
"""
import json

from playwright.sync_api import sync_playwright

PROBE = """
() => {
  const out = [];
  for (const e of document.querySelectorAll('.reg-title,.loc-ds,.loc-nm,.deck,.deck-head')) {
    const r = e.getBoundingClientRect();
    const cs = getComputedStyle(e);
    out.push({
      cls: (e.className||'').toString(),
      t: (e.textContent||'').trim().slice(0,40),
      w: Math.round(r.width), sw: e.scrollWidth, cw: e.clientWidth,
      ovx: cs.overflowX, te: cs.textOverflow, ws: cs.whiteSpace,
      cut: e.scrollWidth > e.clientWidth + 1
    });
  }
  return out;
}
"""

with sync_playwright() as p:
    br = p.chromium.launch()
    for w, h in ((768, 1024), (1024, 1366), (1440, 900)):
        ctx = br.new_context(viewport={"width": w, "height": h}, locale="vi-VN")
        ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg = ctx.new_page()
        pg.goto("http://127.0.0.1:8123/explorer.html", wait_until="load")
        pg.wait_for_timeout(2000)
        print(f"\n=== {w}x{h} ===")
        for it in pg.evaluate(PROBE):
            if it["cls"] in ("deck", "deck-head") or it["cut"]:
                print("  " + json.dumps(it, ensure_ascii=False))
        ctx.close()
    br.close()
