# -*- coding: utf-8 -*-
"""
probe_flat_dark.py — TACH BACH xem "ban do phang toi" den TU DAU.

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/probe_flat_dark.py

⚠️ VI SAO CO BO DO NAY. `scratchpad/probe_earth_flat.py` do CHINH FILE ANH va ra:
   asset `flat-2048` sang TB **73,6**, anh qua cau **115,6** — chi toi hon 1,57 lan.
   Nhung ho so du an ghi "qua cau 113,9 vs ban do phang 24,3 — toi hon 4,7 lan", va
   con so 24,3 do la CO SO cho quyet dinh "mo man bang qua cau roi moi doi sang ban do"
   (01/08/2026). Hai phep do lech nhau 3 lan => mot trong hai dang do sai thu.

   Con so 24,3 duoc do TREN MAN HINH o vung giua (region 0.3,0.3,0.4,0.4). Giua asset
   va man hinh co it nhat 3 thu chen vao:
       (a) `.e2-view::after` — gradient vung toi LUON BAT, toi toi 82% o mep phai
       (b) khung nhin dang chi ra DAI DUONG hay LUC DIA (nuoc do duoc 13,8 / dat 101,1)
       (c) muc zoom
   Bo do nay tat tung thu mot de biet moi thu gop bao nhieu.

Dung dung `pix()` + region cua `smoke_mission_earth.py` => con so SO SANH DUOC voi
24,3 va 113,9 da ghi trong ho so. Do bang cach khac la khong doi chieu duoc.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from smoke_mission_earth import BASE, boot, pix, say_through  # noqa: E402

MID = (0.3, 0.3, 0.4, 0.4)          # dung region cua phep kiem cu
NO_SHADE = ".e2-view::after{display:none !important;}"


def avg(page, note=""):
    v = pix(page, MID)["avg"]
    if note:
        print(f"    {note:<52} {v:6.1f}")
    return v


def set_facing(page, lat, lon):
    page.evaluate(
        """([la, lo]) => { const w = window.__mission.world;
             w.panTo({ lat: la, lon: lo, ms: 0 }); }""", [lat, lon])
    page.wait_for_timeout(260)


def main():
    from playwright.sync_api import sync_playwright

    print("=" * 68)
    print("TACH BACH DO SANG — buoc 1, vung giua (region 0.3,0.3,0.4,0.4)")
    print("=" * 68)

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", lambda m: None)
        boot(page, lang="vi")
        say_through(page)                      # qua cau lop thoai dau
        page.wait_for_timeout(400)

        cur_map = page.evaluate("() => window.__mission.world.map")
        print(f"\n[0] Trang thai that luc vao buoc 1: map = {cur_map!r}")

        # ---------- QUA CAU ----------
        print("\n[1] ANH QUA CAU (moc doi chieu 113,9)")
        page.evaluate("() => window.__mission.world.setMap('globe')")
        page.wait_for_timeout(500)
        g_on = avg(page, "qua cau + gradient vung toi (nhu dang chay)")
        page.add_style_tag(content=NO_SHADE)
        page.wait_for_timeout(200)
        g_off = avg(page, "qua cau, TAT gradient vung toi")

        # ---------- BAN DO PHANG ----------
        print("\n[2] BAN DO PHANG — gradient vung toi da TAT tu buoc tren")
        page.evaluate("() => window.__mission.world.setMap('flat')")
        page.wait_for_timeout(500)
        f_off_default = avg(page, "phang, TAT gradient, khung nhin MAC DINH")

        print("\n    doi khung nhin (facing) — xem no gop bao nhieu:")
        for nm, la, lo in [("giua Thai Binh Duong", 0, -150),
                           ("Chau Phi + Chau Au", 10, 20),
                           ("Bac My", 40, -100),
                           ("Chau A", 30, 95)]:
            set_facing(page, la, lo)
            avg(page, f"phang, TAT gradient, nhin {nm}")

        # ---------- BAT LAI GRADIENT ----------
        print("\n[3] BAT LAI gradient vung toi (bo <style> vua chen)")
        page.evaluate(
            """() => { for (const s of document.querySelectorAll('style'))
                 if (s.textContent.includes('e2-view::after')) s.remove(); }""")
        page.wait_for_timeout(250)
        for nm, la, lo in [("giua Thai Binh Duong", 0, -150),
                           ("Chau Phi + Chau Au", 10, 20)]:
            set_facing(page, la, lo)
            avg(page, f"phang, CO gradient, nhin {nm}")

        print("\n" + "=" * 68)
        print("KET LUAN")
        print("=" * 68)
        print(f"  gradient vung toi lam qua cau tut : {g_off:.1f} -> {g_on:.1f}"
              f"  (mat {g_off - g_on:.1f})")
        print(f"  qua cau (tat gradient)            : {g_off:.1f}")
        print(f"  phang  (tat gradient, mac dinh)   : {f_off_default:.1f}")
        b.close()


if __name__ == "__main__":
    main()
