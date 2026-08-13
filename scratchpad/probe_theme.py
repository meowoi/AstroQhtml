# -*- coding: utf-8 -*-
"""Do MAU TINH TOAN THAT tren dashboard o ca 5 tong den.

Cau hoi: doi tong den thi nhung be mat nao THAT SU doi mau? Doc CSS khong tra loi
duoc — phai `getComputedStyle`. Truoc lan sua nay, hai nut ("Bat dau luyen",
"Mo ban do") va toan bo vien/goc neon dung yen o mau cyan.
"""
import re
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
THEMES = ["cockpit-cyan", "cockpit-amber", "cockpit-violet", "cockpit-mint", "cockpit-rose"]

JS = """
() => {
  const g = (sel, prop) => {
    const e = document.querySelector(sel);
    return e ? getComputedStyle(e)[prop] : '(khong co ' + sel + ')';
  };
  return {
    nut_game: g('.card--game .jelly-btn', 'backgroundImage'),
    nut_map:  g('.card--map .jelly-btn', 'backgroundImage'),
    nut_quiz: g('.card--quiz .jelly-btn', 'backgroundImage'),
    vien_stats: g('.stats-hud', 'borderColor'),
    vien_card:  g('.hud', 'borderColor'),
    icon_game:  getComputedStyle(document.querySelector('.card--game')).getPropertyValue('--ic-bg').trim()
  };
}
"""


def rgbs(s):
    """Boc moi bo ba mau ra khoi chuoi gradient/mau."""
    return re.findall(r'rgba?\(([\d.\s,]+)\)', s)


def seed(theme):
    return ("localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1');"
            "localStorage.setItem('astroq-user', JSON.stringify({name:'T',pilotName:'T',"
            "uid:'u',equipped:{theme:'%s',frame:'frame-steel',decal:'decal-none'},"
            "ship:'Luna'}));" % theme)


def main():
    seen = {}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for th in THEMES:
            ctx = br.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            pg.add_init_script(seed(th))
            pg.goto(BASE + "/dashboard.html", wait_until="load")
            pg.wait_for_selector(".stats-hud", timeout=9000)
            pg.wait_for_timeout(600)
            d = pg.evaluate(JS)
            seen[th] = d
            print(f"\n=== {th} ===")
            for k in ["nut_game", "nut_map", "nut_quiz"]:
                print(f"  {k:11s}: {' | '.join(rgbs(d[k])) or d[k][:60]}")
            print(f"  vien_stats : {d['vien_stats']}")
            print(f"  vien_card  : {d['vien_card']}")
            print(f"  icon_game  : {d['icon_game']}")
            ctx.close()
        br.close()

    print("\n" + "=" * 60)
    ok = bad = 0

    def chk(name, cond, extra=""):
        nonlocal ok, bad
        if cond:
            ok += 1; print(f"  [OK]   {name}" + (f"  ({extra})" if extra else ""))
        else:
            bad += 1; print(f"  [HONG] {name}" + (f"  ({extra})" if extra else ""))

    base = seen["cockpit-cyan"]
    for th in THEMES[1:]:
        d = seen[th]
        # Ba nut phai DOI so voi tong mac dinh...
        for k, label in [("nut_game", "nut 'Bat dau luyen'"),
                         ("nut_map", "nut 'Mo ban do'"),
                         ("nut_quiz", "nut 'Kham pha ngay'")]:
            chk(f"{th}: {label} DOI mau", d[k] != base[k])
        # ...va ba nut phai GIONG NHAU trong cung mot tong (khong con bang mau thu hai)
        chk(f"{th}: 3 nut cung mot bang mau",
            d["nut_game"] == d["nut_map"] == d["nut_quiz"])
        # Vien/goc neon cung phai doi
        chk(f"{th}: vien bang Thong Ke DOI mau", d["vien_stats"] != base["vien_stats"],
            d["vien_stats"])
        chk(f"{th}: vien card HUD DOI mau", d["vien_card"] != base["vien_card"],
            d["vien_card"])
        # Ban sac tung khu KHONG duoc mat: o icon giu tong rieng
        chk(f"{th}: o icon khu Huan Luyen GIU tong rieng",
            d["icon_game"] == base["icon_game"], d["icon_game"])

    print(f"\nKET QUA: {ok} dat / {bad} hong")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
