# -*- coding: utf-8 -*-
"""
probe_flat_framing.py — chon KHUNG NHIN mo man cho buoc 1, va do xem ha bot
gradient vung toi duoc bao nhieu.

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/probe_flat_framing.py

Tiep noi `probe_flat_dark.py`, bo do do da chung minh:
  · asset KHONG toi (flat-2048 sang TB 73,6 / qua cau 115,6 — do tren chinh file anh)
  · thu quyet dinh do sang tren man hinh la KHUNG NHIN: 28,1 (giua Thai Binh Duong)
    -> 88,2 (Chau A). Bien do 3,1 lan, chi vi tam khung roi vao nuoc hay vao dat.
  · gradient `.e2-view::after` an them 30 diem tren qua cau, 6-15 tren phang.

=> Khong can sinh lai asset. Chi can (a) dat khung mo man vao vung nhieu dat,
   (b) ha gradient mac dinh roi de buoc 3 tang len.

Moc phai dat: >= 87,0 — do la do sang thuc te cua ANH QUA CAU NHU DANG CHAY
(co gradient). Bang no la khong ai thay canh mo man toi di.

⚠️ Khung mo man con phai THOA MOT DIEU KIEN NUA, khong chi do sang: buoc 1 noi ve
   khi quyen / dai duong / luc dia, nen trong khung phai thay CA DAT CA NUOC. Mot
   khung sang ruc toan luc dia thi cai dom "dai duong" khong co gi de tro vao.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from smoke_mission_earth import BASE, boot, pix, say_through  # noqa: E402

MID = (0.3, 0.3, 0.4, 0.4)
NO_SHADE = ".e2-view::after{display:none !important;}"
SOFT = (".e2-view::after{background:linear-gradient(100deg,"
        "rgba(2,6,20,0) 40%,rgba(2,6,20,.16) 70%,rgba(2,6,20,.30) 100%)"
        " !important;}")

# Ung vien: (ten, lat, lon) — nham vung co CA dat CA nuoc trong khung
CANDS = [
    ("mac dinh hien tai",        None, None),
    ("Chau A (Himalaya+AD)",       30,   95),
    ("An Do + AD Duong",           20,   80),
    ("Trung Dong + Bien Do",       25,   50),
    ("Chau Phi + DTD",             10,   20),
    ("DNA + Thai Binh Duong",      12,  110),
    ("Bac My + DTD",               40,  -95),
]


def avg(page):
    return pix(page, MID)["avg"]


def set_facing(page, lat, lon):
    if lat is None:
        return
    page.evaluate("([la,lo])=>window.__mission.world.panTo({lat:la,lon:lo,ms:0})",
                  [lat, lon])
    page.wait_for_timeout(240)


def main():
    from playwright.sync_api import sync_playwright

    print("=" * 72)
    print("CHON KHUNG NHIN MO MAN — moc can dat: >= 87,0 (qua cau nhu dang chay)")
    print("=" * 72)
    print(f"{'khung nhin':<26} {'gradient GOC':>13} {'gradient NHE':>13}")
    print("-" * 72)

    best = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1440, "height": 900})
        boot(page, lang="vi")
        say_through(page)
        page.wait_for_timeout(400)
        page.evaluate("()=>window.__mission.world.setMap('flat')")
        page.wait_for_timeout(400)

        for nm, la, lo in CANDS:
            set_facing(page, la, lo)
            a_goc = avg(page)
            tag = page.add_style_tag(content=SOFT)
            page.wait_for_timeout(180)
            a_nhe = avg(page)
            page.evaluate("""() => { for (const s of document.querySelectorAll('style'))
                if (s.textContent.includes('rgba(2,6,20,.16)')) s.remove(); }""")
            page.wait_for_timeout(180)
            flag = "  <= DAT MOC" if a_nhe >= 87.0 else ""
            print(f"{nm:<26} {a_goc:>13.1f} {a_nhe:>13.1f}{flag}")
            best.append((a_nhe, nm, la, lo))

        # Chup 2 ung vien sang nhat de SOI MAT, khong chi tin con so
        best.sort(reverse=True)
        for i, (v, nm, la, lo) in enumerate(best[:2]):
            if la is None:
                continue
            set_facing(page, la, lo)
            page.add_style_tag(content=SOFT)
            page.wait_for_timeout(300)
            p = os.path.join(HERE, f"framing-{i+1}.png")
            page.screenshot(path=p)
            print(f"\nanh: {os.path.basename(p)}  ({nm}, sang {v:.1f})")

        b.close()


if __name__ == "__main__":
    main()
