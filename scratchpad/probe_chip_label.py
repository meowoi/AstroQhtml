# -*- coding: utf-8 -*-
"""probe_chip_label.py — NHAN CHIP HUD CO BI CAT CHU KHONG.

Chu du an chup duoc console doc hien `NHI…` (Nhien lieu) va `CÒN L…` (Con lai)
o Duong Dua Sao Choi. Do la loi CO SAN o `css/game-shell.css` — file dung chung
cua CA 10 GAME — nen phai do truoc/sau tren du 10 game, khong sua bua.

Do ba thu:
  1. `.chip .k` nao bi CAT (`scrollWidth > clientWidth`) — chu bi cat la mat
     ten cua con so, ma "Nhien lieu" la thu quyet dinh luot choi.
  1b. `.chip .k` nao TRAN khoi khung chip. ⚠️ Phai do CA HAI: phep thu pha hoai
     22/08/2026 chi ra rang bo hang rao chinh ma giu `overflow:visible` thi
     `scrollWidth == clientWidth` (khong co gi "bi cat") trong khi chu tran han
     ra ngoai chip — xau hon ca cat, va ban dau bo do IM LANG voi ca ca do.
  2. CHIEU CAO cua `.hud` va `.stage` — de biet cai gia cua ban sua. Console doc
     co cho theo chieu doc, nhung "rong ma THAP" (1600x720) la ca da tung lam
     5 moc treo tran khoi man; phai do lai chinh o do.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/probe_chip_label.py            # do va in bang
  python scratchpad/probe_chip_label.py --json     # kem JSON de so truoc/sau
"""
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"

# 10 game doc THANG tu mang GAMES cua games.html — them game khong phai sua
# bo do (bai hoc `_GAME_FILE` gan cung, 15/08/2026).
GH = (ROOT / "games.html").read_text(encoding="utf-8")
GAMES = re.findall(r'file:\s*"(game-[a-z]+\.html)"', GH)

VIEWS = [
    ("desktop-1440x900", 1440, 900),
    ("rong-ma-THAP-1600x720", 1600, 720),
    ("laptop-1280x800", 1280, 800),
    ("dien-thoai-390x844", 390, 844),
]

MEASURE = """() => {
  const st = document.querySelector('.stage');
  const hud = document.querySelector('.hud');
  const ks = [...document.querySelectorAll('.chip .k')].map(e => {
    const chip = e.closest('.chip');
    const a = e.getBoundingClientRect(), b = chip.getBoundingClientRect();
    const cs = getComputedStyle(chip);
    // ⚠️ Nhan bi `display:none` (man <=560px an nhan) cho khung 0x0 tai goc toa
    //    do, nen moi phep so bien-chip deu lech han. Bo qua no chu khong bao
    //    hong — bai hoc 03/08/2026 (`<line>` thang dung co bbox rong 0).
    if (getComputedStyle(e).display === 'none')
      return {txt: (e.textContent || '').trim(), sw: 0, cw: 0,
              cut: false, over: false, overPx: 0, hidden: true};
    // Tran = vuot qua VUNG NOI DUNG cua chip (tru padding), khong phai vuot
    // qua vien — mot chu dinh sat vien da la loi bo cuc.
    const padL = parseFloat(cs.paddingLeft) || 0;
    const padR = parseFloat(cs.paddingRight) || 0;
    const over = Math.max(0, Math.round((b.left + padL) - a.left),
                             Math.round(a.right - (b.right - padR)));
    return {
      txt: (e.textContent || '').trim(),
      sw: e.scrollWidth, cw: e.clientWidth,
      cut: e.scrollWidth > e.clientWidth + 1,
      over: over > 1, overPx: over
    };
  });
  const chips = [...document.querySelectorAll('.hud .chip')].map(e => {
    const r = e.getBoundingClientRect(); return {w: Math.round(r.width), h: Math.round(r.height)};
  });
  const r = el => el ? Math.round(el.getBoundingClientRect().height) : 0;
  return {
    stageH: r(st), hudH: r(hud),
    hudSW: hud ? hud.scrollHeight : 0, hudCH: hud ? hud.clientHeight : 0,
    ks, chips,
    // Tran ngang cua CA TRANG — ban sua khong duoc lam trang tran.
    docW: document.documentElement.scrollWidth,
    winW: window.innerWidth
  };
}"""


def main():
    out = {}
    cut_total = 0
    with sync_playwright() as p:
        br = p.chromium.launch()
        for vname, w, h in VIEWS:
            ctx = br.new_context(viewport={"width": w, "height": h}, locale="vi-VN",
                                 timezone_id="Asia/Ho_Chi_Minh")
            # ⚠️ Ghim ngon ngu: Chromium mac dinh en-US nen nhan tieng Anh ngan hon
            #    va cho cat chu KHONG BAO GIO lo ra (bai hoc 31/07/2026).
            ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
            pg = ctx.new_page()
            for g in GAMES:
                pg.goto(f"{BASE}/{g}", wait_until="load", timeout=30000)
                pg.wait_for_timeout(300)
                m = pg.evaluate(MEASURE)
                out.setdefault(vname, {})[g] = m
                cut = [k for k in m["ks"] if k["cut"]]
                over = [k for k in m["ks"] if k["over"]]
                bad = cut + [k for k in over if not k["cut"]]
                cut_total += len(bad)
                flag = ("  << CAT CHU" if cut else "") + ("  << TRAN CHIP" if over else "")
                print(f"[{vname}] {g:24s} stage={m['stageH']:4d} hud={m['hudH']:4d} "
                      f"chip={len(m['chips'])} nhan-loi={len(bad)}{flag}")
                for k in cut:
                    print(f"        · CAT  \"{k['txt']}\"  sw={k['sw']} > cw={k['cw']}")
                for k in over:
                    if not k["cut"]:
                        print(f"        · TRAN \"{k['txt']}\"  vuot {k['overPx']}px "
                              f"khoi vung noi dung cua chip")
                if m["docW"] > m["winW"] + 1:
                    print(f"        !! TRAN NGANG {m['docW']} > {m['winW']}")
            ctx.close()
        br.close()

    print(f"\n=== TONG SO NHAN BI CAT/TRAN: {cut_total} ===")
    if "--json" in sys.argv:
        pathlib.Path(sys.argv[sys.argv.index("--json") + 1]).write_text(
            json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print("(da ghi JSON)")


if __name__ == "__main__":
    main()
