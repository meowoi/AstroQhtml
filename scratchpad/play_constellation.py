# -*- coding: utf-8 -*-
"""play_constellation.py — CHOI THAT "Ghep Chom Sao" (ARCADE-04) tren Chromium.

⚠️ Bo do cua game nay DA MAT khoi may (`check_constellation.py` +
   `play_constellation.py`, ghi chu 28/07/2026), nen truoc lan sua 22/08/2026 no
   la game DUY NHAT trong 10 game khong co bo do luat choi nao gac. Day la ban
   dung lai.

Do ba dieu:
  [1] MAN BRIEF NOI DUNG CHOM SAO SE CHOI. Truoc 22/08 man brief boc mot chom
      lam hinh nen VA dat ten no len chip HUD, roi `startRound()` boc mot chom
      KHAC — chip noi "Lap Ho" ma tre choi "Bo Cap".
  [2] Ghep xong thi LUU NGAY, khong phai tai lai trang moi luu.
  [3] Kỷ luc / thuong / bo suu tap ghi dung.

⚠️ Toa do sao doc THANG tu `game-constellation.html` (mang `SKY`) nen bo do
   khong phai doan gi. Nhung PHAI hoi trang xem dang choi chom NAO — `startRound`
   boc ngau nhien.
⚠️ Phai bam theo CAP (1,2) (2,3) (3,4)... `onUp` dat `sel=-1` sau moi duong noi,
   nen bam tuan tu 1,2,3,4 se ra link(1,2) roi CHON sao 3 → sai cap.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/play_constellation.py
"""
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"
SRC = (ROOT / "game-constellation.html").read_text(encoding="utf-8")

dat = 0
hong = 0


def chk(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   " + name + (("  (" + str(info) + ")") if info else ""))
    else:
        hong += 1
        print("  [HONG] " + name + (("  -> " + str(info)) if info else ""))


# ── Doc `SKY` tu chinh trang: key + toa do sao ───────────────────────
def read_sky():
    i = SRC.index("var SKY = [")
    j = SRC.index("\n  ];", i)
    blob = SRC[i:j]
    out = {}
    # Cat theo tung `key:"..."` de khong tron sao cua hai chom
    parts = re.split(r'\n    \{\n\s*key:"', blob)
    for pt in parts[1:]:
        key = pt.split('"', 1)[0]
        st = pt.split("stars:[", 1)[1].split("]", 1)[0]
        stars = [(int(a), int(b), int(c)) for a, b, c in
                 re.findall(r"\{id:(\d+),\s*x:(\d+),\s*y:(\d+)\}", st)]
        out[key] = sorted(stars, key=lambda s: s[0])
    return out


SKY = read_sky()
COST = int(re.search(r"COST:\s*(\d+)", SRC).group(1))
VW = int(re.search(r"VW:\s*(\d+)", SRC).group(1))
VH = int(re.search(r"VH:\s*(\d+)", SRC).group(1))


def newctx(br, lang="vi", w=1440, h=900):
    ctx = br.new_context(
        viewport={"width": w, "height": h},
        locale="vi-VN" if lang == "vi" else "en-US",
        timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','%s');"
        "localStorage.setItem('astroq-asteroids','300');" % lang)
    return ctx


def open_page(ctx):
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.goto(BASE + "/game-constellation.html", wait_until="load", timeout=30000)
    pg.wait_for_selector("#start-btn", timeout=8000)
    pg.wait_for_timeout(500)
    if pg.locator(".ov.rot.show").count():
        pg.locator(".ov.rot.show .rot-ok").click()
    return pg


def chip(pg):
    return (pg.inner_text("#hb-name").strip(), pg.inner_text("#hb-sub").strip())


def key_of(pg):
    """Suy KHOA chom sao dang hien tu chip HUD (chip la thu tre doc duoc)."""
    nm = pg.inner_text("#hb-name").strip().casefold()
    for k in SKY:
        m = re.search(r'key:"' + k + r'",\s*\n\s*name:\{vi:"([^"]+)"', SRC)
        if m and m.group(1).strip().casefold() == nm:
            return k
    return None


def click_star(pg, box, x, y):
    pg.mouse.move(box["x"] + x / VW * box["width"],
                  box["y"] + y / VH * box["height"])
    pg.mouse.down()
    pg.wait_for_timeout(45)
    pg.mouse.up()
    pg.wait_for_timeout(45)


def solve(pg, key):
    """Noi het cac duong cua chom `key`. Bam theo CAP, khong bam tuan tu."""
    box = pg.query_selector("canvas").bounding_box()
    st = SKY[key]
    for i in range(len(st) - 1):
        a, b = st[i], st[i + 1]
        click_star(pg, box, a[1], a[2])
        click_star(pg, box, b[1], b[2])
    pg.wait_for_timeout(300)


def main():
    print("doc duoc %d chom sao tu SKY · phi %d tt · san %dx%d"
          % (len(SKY), COST, VW, VH))
    with sync_playwright() as p:
        br = p.chromium.launch()

        # ═════════ [1] Man brief noi dung chom sao se choi ═════════
        print("\n=== [1] MAN BRIEF NOI DUNG CHOM SAO SE CHOI ===")
        for lap in range(4):
            ctx = newctx(br)
            pg = open_page(ctx)
            before = chip(pg)
            pg.click("#start-btn")
            pg.wait_for_timeout(400)
            after = chip(pg)
            chk("luot %d: chip truoc khi bam = chip sau khi bam" % (lap + 1),
                before == after, "%r -> %r" % (before[0], after[0]))
            ctx.close()

        # ═════════ [2] Ghep xong thi LUU NGAY ═════════
        print("\n=== [2] GHEP XONG THI LUU NGAY (khong phai tai lai trang) ===")
        ctx = newctx(br)
        pg = open_page(ctx)
        pg.click("#start-btn")
        pg.wait_for_timeout(400)
        k = key_of(pg)
        chk("suy duoc khoa chom sao dang choi", k is not None, k)
        if k:
            bal0 = int(pg.inner_text("#bal"))
            solve(pg, k)
            pg.wait_for_timeout(900)
            # ⚠ Bang thong tin thien van tu bat SAU 1,35 giay (thiet ke) — do o
            #   moc 0,9s la do mot thu chua xay ra. Cho tin hieu that.
            try:
                pg.wait_for_selector("#ov-fact.show", timeout=6000)
            except Exception:
                pass
            snap = pg.evaluate("""() => ({
              best:  localStorage.getItem('astroq-constellation-best'),
              queue: localStorage.getItem('astroq-progress-queue'),
              local: localStorage.getItem('astroq-progress'),
              bal:   localStorage.getItem('astroq-asteroids'),
              ovFact: !!document.querySelector('#ov-fact.show')
            })""")
            print("   best  :", snap["best"])
            print("   queue :", (snap["queue"] or "")[:220])
            print("   local :", (snap["local"] or "")[:220])
            # ⚠ Hinh dang tu 22/08/2026: `{uid, best:{...}}` — dong dau uid de o
            #   may dung chung, bo suu tap cua dua truoc khong lan sang dua sau.
            #   Ban ghi CU la object phang, van doc duoc (xem js/constellations.js).
            raw = json.loads(snap["best"] or "{}")
            best = raw.get("best", raw)
            chk("kỷ luc chom vua ghep duoc ghi NGAY vao localStorage",
                k in best, "%r" % raw)
            q = json.loads(snap["queue"] or "[]")
            games = [e for e in q if e.get("type") == "game"]
            chk("viec 'da choi mot luot' vao hang cho NGAY",
                len(games) >= 1, "%d viec game / %d viec" % (len(games), len(q)))
            chk("viec ghi dung ten game + id chom sao",
                bool(games) and games[0].get("game") == "constellation"
                and games[0].get("id") == k,
                games[0] if games else None)
            loc = json.loads(snap["local"] or "{}")
            chk("ban sao trong may tang so luot choi NGAY",
                (loc.get("gamesPlayed") or 0) >= 1, loc.get("gamesPlayed"))
            chk("vi da cong thuong (khong phai doi tai lai trang)",
                int(snap["bal"] or 0) > bal0 - COST,
                "truoc %d, sau %s" % (bal0, snap["bal"]))
            chk("bang thong tin thien van tu bat", snap["ovFact"])

            # Bang ket qua: ky luc phai la con so VUA luu, khong phai "—"
            pg.click("#fact-btn")
            pg.wait_for_timeout(400)
            rb = pg.inner_text("#r-best").strip()
            chk("bang ket qua hien kỷ luc vua lap, khong phai dau '—'",
                rb not in ("", "—"), rb)
            chk("0 loi trang", not pg.perr, "; ".join(pg.perr[:2]))
        ctx.close()

        br.close()

    print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
    sys.exit(1 if hong else 0)


if __name__ == "__main__":
    main()
