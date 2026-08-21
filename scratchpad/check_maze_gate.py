# -*- coding: utf-8 -*-
"""check_maze_gate.py — ME CUNG: thu xong vien cuoi thi co CHI DUONG ve cong.

VI SAO CO BO DO NAY (21/08/2026)
--------------------------------
Chu du an choi that roi bao: *"game me cung dang phai dieu khien nhan vat o tren
vong sang (vach dich) moi duoc tinh ve dich"*.

Do truoc, sua sau: bo do nay chung minh **luat khong hong** — thu het tinh the roi
buoc len cong thi luot ket thuc dung, ke ca khi truoc do da tung dung len cong luc
con khoa. Nen viec phai sua khong phai cai LUAT (chu du an chon giu: *"thu bang het
roi moi ra"*, chot 15/08/2026) ma la cho TRE BIET phai lam gi tiep: thu xong vien
cuoi thi hien mot **duong net dut mau ho phach chay tu cho dang dung toi cong**,
kem mot cau toast noi dung viec do.

Bon phep do:
  [1] Luc moi vao: CHUA co duong ve cong (con tinh the thi chua mo duong).
  [2] Dung len cong luc CON tinh the: khong ket thuc, van dang choi.
  [3] Thu xong vien CUOI: duong ve cong bat len, dai dung bang duong ngan nhat
      tu cho dang dung toi cong, va toast noi ra.
  [4] Buoc len cong: luot ket thuc (LUAT KHONG DOI).

  python scratchpad/check_maze_gate.py
"""
import pathlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "game-maze.html"

LOG = []


def ok(name, cond, extra=""):
    LOG.append(("PASS  " if cond else "FAIL  ") + name + ("  [%s]" % extra if extra else ""))


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 820})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script(
            "localStorage.clear();"
            "localStorage.setItem('astroq-asteroids','999');"
            "localStorage.setItem('astroq-lang','vi');")
        pg.goto(PAGE.as_uri())
        pg.wait_for_function("!!window.__maze", timeout=20000)
        pg.click("#start-btn")
        pg.wait_for_timeout(500)

        def walk(path):
            for d in path:
                pg.evaluate("__maze.snap()")
                pg.evaluate("__maze.move('%s')" % d)
            pg.evaluate("__maze.snap()")

        # [1] Moi vao: chua mo duong ve cong
        ok("[1] moi vao: chua co duong ve cong",
           pg.evaluate("__maze.gateGuide") is False and pg.evaluate("len = __maze.gatePath.length") == 0)

        # [2] Dung len cong luc con tinh the -> khong ket thuc
        walk(pg.evaluate("__maze.path()"))
        at_exit = pg.evaluate("__maze.pos.c===__maze.exit.c && __maze.pos.r===__maze.exit.r")
        ok("[2] dung dung tren o cong", at_exit)
        ok("[2] con tinh the -> KHONG ket thuc", pg.evaluate("__maze.state") == "play",
           "state=" + pg.evaluate("__maze.state"))
        ok("[2] van chua mo duong ve cong", pg.evaluate("__maze.gateGuide") is False)

        # [3] Thu xong vien cuoi -> duong ve cong bat len
        tour = pg.evaluate("__maze.tour()")
        for d in tour:
            walk([d])
            if pg.evaluate("__maze.mined") == pg.evaluate("__maze.gems"):
                break
        pg.wait_for_timeout(400)
        guide = pg.evaluate("__maze.gateGuide")
        plen = pg.evaluate("__maze.gatePath.length")
        want = pg.evaluate("__maze.path().length")
        toast = (pg.inner_text("#toast") or "").strip()
        ok("[3] thu xong vien cuoi -> duong ve cong SANG", guide is True)
        ok("[3] duong dai dung bang duong ngan nhat toi cong", plen == want and plen > 0,
           "gatePath=%d shortest=%d" % (plen, want))
        ok("[3] toast noi ra chuyen do", "cong" in toast.lower() or "cổng" in toast, toast)

        # [4] Buoc len cong -> ket thuc (luat khong doi)
        walk(pg.evaluate("__maze.path()"))
        pg.wait_for_timeout(400)
        ok("[4] buoc len cong -> ket thuc luot", pg.evaluate("__maze.state") == "over",
           "state=" + pg.evaluate("__maze.state"))

        for e in errs:
            LOG.append("FAIL  loi JS: " + e)
        b.close()

    for l in LOG:
        print("  " + l)
    bad = [l for l in LOG if l.startswith("FAIL")]
    print()
    print("=== KET QUA: %d dat / %d hong ===" % (len(LOG) - len(bad), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
