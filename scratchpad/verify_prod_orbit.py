# -*- coding: utf-8 -*-
"""Do TREN BAN THAT (astroq.org) sau khi Pages build xong.

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC. Do truoc luc Pages build xong thi moi
   ket luan deu sai — 06/08/2026 ban that da tung dung o ban cu gan mot ngay, va do
   chinh la ly do huy hieu ban dung ton tai.
"""
import io, re, sys, time, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

SITE = "https://astroq.org/"
WANT = "2026.08.15.2"
dat = hong = 0
loi = []


def chk(dk, nhan, ct=""):
    global dat, hong
    if dk:
        dat += 1
        print("  [ok]   " + nhan + (("  " + ct) if ct else ""))
    else:
        hong += 1
        loi.append(nhan)
        print("  [FAIL] " + nhan + (("  " + ct) if ct else ""))


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, timeout=timeout)
    return r.status, r.headers.get("Content-Type", ""), r.read()


# ── [0] Cho Pages build xong ──
print("=== [0] Cho Pages build (kiem so hieu ban dung) ===")
ver = None
for i in range(30):
    try:
        _, _, b = get(SITE + "js/ui-common.js?cb=%d" % time.time())
        m = re.search(r'var VERSION = "([\d.]+)"', b.decode("utf-8", "replace"))
        ver = m.group(1) if m else None
        if ver == WANT:
            break
    except Exception as e:
        ver = "loi: %s" % type(e).__name__
    print("    ... dang la %s, cho 15s (lan %d)" % (ver, i + 1))
    time.sleep(15)
chk(ver == WANT, "ban dung tren bank that dung %s" % WANT, str(ver))
if ver != WANT:
    print("\n⚠️ DUNG LAI: Pages chua build xong, moi phep do sau day se sai.")
    sys.exit(1)

# ── [1] File moi tra 200 + MIME dung ──
print("\n=== [1] File moi tren Pages ===")
for path, mime in [
    ("js/mission-stage.js", "javascript"),
    ("css/mission-stage.css", "text/css"),
    ("css/earth2d.css", "text/css"),
    ("css/mission-orbit.css", "text/css"),
    ("mission-orbit.html", "text/html"),
    ("learningdata/astronomy/orbit_codex.json", "json"),
]:
    try:
        st, ct, body = get(SITE + path)
        # ⚠️ MIME phai DUNG, khong chi 200: ES module bi tu choi neu server tra
        #    text/plain, nen day la thu phai DO chu khong duoc gia dinh.
        chk(st == 200 and mime in ct, "%s -> %d %s" % (path, st, ct.split(";")[0]),
            "%d byte" % len(body))
    except Exception as e:
        chk(False, path, type(e).__name__)

# ── [2] Trang nhiem vu 02 chay that tren ban that ──
print("\n=== [2] mission-orbit.html tren astroq.org ===")
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg = ctx.new_page()
    errs, bad = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: bad.append("%d %s" % (r.status, r.url))
          if r.status >= 400 else None)

    pg.goto(SITE + "mission-orbit.html", wait_until="load")
    pg.wait_for_function("() => window.__mission !== undefined", timeout=40000)
    chk(not errs, "0 loi trang / console", "; ".join(errs[:2]))
    chk(not bad, "0 tai nguyen hong", "; ".join(bad[:2]))
    chk(pg.evaluate("() => document.getElementById('load').classList.contains('gone')"),
        "canh dung xong (man cho da tat)")
    tag = pg.inner_text("#tag").strip()
    chk("MISSION_02" in tag, "header goi dung ten nhiem vu 02", tag)
    chk(pg.evaluate("() => window.__mission.step") == "eyes", "mo tu chang ①")
    # Choi mot chang: bam qua loi thoai roi cham du 3 vet quet
    for _ in range(30):
        pg.evaluate("() => window.__mission.say()")
        if pg.is_visible("#scan.show"):
            break
        pg.wait_for_timeout(400)
    chk(pg.is_visible("#scan.show"), "bang chang ① hien ra sau loi thoai")
    n = pg.eval_on_selector_all(".mo-swath", "e => e.length")
    chk(n == 3, "ve du 3 vet quet tren ban do", str(n))

    # ── [3] Trai Dat co HAI nhiem vu -> man hanh tinh ──
    print("\n=== [3] Ban do: Trai Dat co HAI nhiem vu ===")
    pg2 = ctx.new_page()
    pg2.goto(SITE + "mission-map.html", wait_until="load")
    pg2.wait_for_timeout(1200)
    nm = pg2.evaluate("() => AstroQCatalog.byWorld('earth').length")
    chk(nm == 2, "danh muc tren ban that co 2 nhiem vu o Trai Dat", str(nm))

    pg3 = ctx.new_page()
    pg3.goto(SITE + "mission-planet.html?w=earth", wait_until="load")
    pg3.wait_for_selector(".node", timeout=20000)
    rows = pg3.eval_on_selector_all("#list .node .node-lb b",
                                    "es => es.map(e => e.textContent.trim())")
    chk(len(rows) == 2 and "Mắt Thần" in " ".join(rows),
        "man hanh tinh liet ke ca hai nhiem vu", str(rows))

    # ── [4] Cay chang cua nhiem vu 02 ──
    pg4 = ctx.new_page()
    pg4.goto(SITE + "mission-tree.html?m=orbit", wait_until="load")
    pg4.wait_for_selector(".node", timeout=20000)
    chk(pg4.locator(".node").count() == 5, "cay chang nhiem vu 02 co 5 chang",
        str(pg4.locator(".node").count()))

    # ── [5] Nhiem vu 01 KHONG hong sau khi tach vo ──
    print("\n=== [5] Nhiem vu 01 van chay (hoi quy tren ban that) ===")
    pg5 = ctx.new_page()
    errs5 = []
    pg5.on("pageerror", lambda e: errs5.append(str(e)))
    pg5.goto(SITE + "mission-earth.html", wait_until="load")
    pg5.wait_for_function("() => window.__mission !== undefined", timeout=40000)
    chk(not errs5, "mission-earth: 0 loi trang", "; ".join(errs5[:2]))
    chk(pg5.evaluate("() => window.__mission.step") == "scan", "mission-earth mo tu buoc ①")
    chk(pg5.inner_text("#back").strip().startswith("<"), "vo dung ra header")

    b.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
if loi:
    print("Hong:")
    for x in loi:
        print("  - " + x)
sys.exit(1 if hong else 0)
