"""Chung minh phep kiem MOI o muc [10] smoke_waitlist co rang — do TRUC TIEP.

Khong pha duoc qua bo day du: moi phep pha lam an #wl-done deu giet bo do o muc TRUOC,
vi nut "Dang ky lai" (#wl-again) nam BEN TRONG the do, nen pg.click() het han va nem loi.
Nen do thang ba phep kiem tren hai trang thai, khong sua file nguon nao, khong goi API.

Cau hoi: phep kiem nao PHAN BIET duoc "the hien ra" voi "the co chu nhung khong ai thay"?
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8000/index.html"
TXT = "Kiểm tra hòm thư"


def three(pg):
    """Ba phep kiem cua muc [10], theo dung thu tu trong bo do."""
    return {
        "hidden is None  (kieu CU)": pg.get_attribute("#wl-done", "hidden") is None,
        "inner_text co chu  (kieu CU)": TXT in pg.inner_text("#wl-done"),
        "is_visible  (MOI)": pg.is_visible("#wl-done"),
    }


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg.goto(URL, wait_until="load")

    print("=== [1] TRANG THAI BINH THUONG: the con AN (chua gui form) ===")
    a = three(pg)
    for k, v in a.items():
        print("      %-30s -> %s" % (k, v))

    print("\n=== [2] THE HIEN RA DUNG CACH (nhu paintDone lam) ===")
    pg.evaluate("() => { document.getElementById('wl-done').hidden = false; }")
    bb = three(pg)
    for k, v in bb.items():
        print("      %-30s -> %s" % (k, v))

    print("\n=== [3] LOI CO Y: bo hidden NHUNG khong ai nhin thay ===")
    pg.evaluate("() => { const d=document.getElementById('wl-done');"
                " d.hidden=false; d.style.display='none'; }")
    c = three(pg)
    for k, v in c.items():
        print("      %-30s -> %s" % (k, v))
    b.close()

print("\n" + "-" * 66)
dat = hong = 0


def check(ok, label):
    global dat, hong
    if ok:
        dat += 1
        print("  [OK]   " + label)
    else:
        hong += 1
        print("  [HONG] " + label)


# Dieu can chung minh: hai phep kiem kieu CU khong phan biet duoc [2] voi [3].
check(a["inner_text co chu  (kieu CU)"],
      "phep kiem 'doc chu' DAT NGAY KHI FORM CHUA GUI -> no la phep kiem RONG")
check(bb["hidden is None  (kieu CU)"] and c["hidden is None  (kieu CU)"],
      "phep kiem 'hidden is None' KHONG phan biet duoc [2] voi [3] -> mu voi loi nay")
check(bb["inner_text co chu  (kieu CU)"] and c["inner_text co chu  (kieu CU)"],
      "phep kiem 'doc chu' KHONG phan biet duoc [2] voi [3] -> mu voi loi nay")
check(bb["is_visible  (MOI)"] and not c["is_visible  (MOI)"],
      "phep kiem MOI 'is_visible' BAT DUOC loi [3] va van dat o [2] -> CO RANG")
print("-" * 66)
print("  KET QUA: %d dat / %d hong" % (dat, hong))
sys.exit(1 if hong else 0)
