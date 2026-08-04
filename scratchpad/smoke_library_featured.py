# -*- coding: utf-8 -*-
"""Soi khoi "Bai viet noi bat" cua Goc Kham Pha (library.html) tren Chromium that.

Cau hoi bo do nay tra loi — do TREN TRANG, khong doc code:
  · luon dung 4 the noi bat, ke ca khi tre da doc het moi bai;
  · bai CHUA DOC duoc day len truoc (gieo `astroq-read` roi tai lai trang);
  · 4 bai do KHONG hien lai trong luoi ben duoi (khong nhin doi);
  · 3 the nho cua khoi noi bat BAM DUOC (chung khong phai `.feat`, de sot);
  · dang loc / dang tim thi khoi noi bat AN va luoi hien DU ket qua khop —
    ban cu giu bai `hero` ngoai luoi nen tim dung ten bai do lai ra "khong
    tim thay", tuc bai co that ma may bao khong co.

⚠️ Nhan cua chk() PHAI KHONG DAU (console Windows cp1252). Chay:
     python -m http.server 8123     (trong AstroQhtml/)
     PYTHONIOENCODING=utf-8 python scratchpad/smoke_library_featured.py
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/library.html"
OK = FAIL = 0


def chk(cond, label, info=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"  [OK]   {label}" + (f"  ({info})" if info else ""))
    else:
        FAIL += 1
        print(f"  [HONG] {label}" + (f"  ({info})" if info else ""))


def seed(ctx, read_ids, lang="vi"):
    """Gieo trang thai TRUOC khi trang chay — `astroq-read` la thu quyet dinh
    bai nao duoc day len noi bat, doc sau khi trang ve la do sai thoi diem."""
    ctx.add_init_script(
        "localStorage.setItem('astroq-read', JSON.stringify(%s));"
        "localStorage.setItem('astroq-lang', '%s');" % (list(read_ids), lang))


def snap(pg):
    return pg.evaluate("""() => ({
        feat: [...document.querySelectorAll('#hero-wrap .feat')].map(e => e.dataset.id),
        featCards: [...document.querySelectorAll('#hero-wrap .feat-row .card')].map(e => e.dataset.id),
        grid: [...document.querySelectorAll('#grid .card')].map(e => e.dataset.id),
        empty: !!document.querySelector('#grid .empty'),
        eyebrow: (document.querySelector('.feat-eyebrow')||{}).textContent || ''
      })""")


with sync_playwright() as p:
    br = p.chromium.launch()

    # ── [1] Chua doc bai nao: 4 the noi bat, khong trung voi luoi ──────────
    print("\n=== [1] Chua doc bai nao ===")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    seed(ctx, [])
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    # ⚠️ BO QUA `net::ERR_FAILED`: chinh bo do nay chan anh NASA (pg.route abort) cho
    # nhanh va cho on dinh, nen lo do la TIENG ON CUA PHEP DO, khong phai loi trang.
    pg.on("console", lambda m: errs.append(m.text)
          if m.type == "error" and "ERR_FAILED" not in m.text else None)
    pg.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#hero-wrap .feat", timeout=15000)
    s = snap(pg)
    feat_all = s["feat"] + s["featCards"]
    chk(len(feat_all) == 4, "dung 4 bai noi bat", str(feat_all))
    chk(len(s["feat"]) == 1 and len(s["featCards"]) == 3,
        "1 the lon + 3 the nho", f"{len(s['feat'])}+{len(s['featCards'])}")
    chk(not (set(feat_all) & set(s["grid"])),
        "bai noi bat KHONG hien lai o luoi", str(sorted(set(feat_all) & set(s['grid']))))
    chk(len(feat_all) + len(s["grid"]) == 8,
        "khoi noi bat + luoi = du 8 bai, khong sot bai nao",
        f"{len(feat_all)}+{len(s['grid'])}")
    chk("nổi bật" in s["eyebrow"].lower(), "co nhan 'Bai viet noi bat'", s["eyebrow"])

    # 3 the nho phai BAM DUOC (chung la `.card`, khong phai `.feat`)
    small = s["featCards"][0]
    pg.click(f'#hero-wrap .feat-row .card[data-id="{small}"]')
    pg.wait_for_timeout(400)
    opened = pg.evaluate("() => document.getElementById('reader').classList.contains('show')")
    chk(opened, "the nho cua khoi noi bat bam duoc (mo trinh doc)", small)
    pg.keyboard.press("Escape")
    ctx.close()

    # ── [2] Da doc 3 bai dau: chung bi day xuong, chua doc len truoc ───────
    print("\n=== [2] Da doc 3 bai -> uu tien bai chua doc ===")
    READ3 = ["lib-nebula", "lib-andromeda", "lib-mars"]
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    seed(ctx, READ3)
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#hero-wrap .feat", timeout=15000)
    s = snap(pg)
    feat_all = s["feat"] + s["featCards"]
    chk(len(feat_all) == 4, "van dung 4 bai noi bat", str(feat_all))
    chk(not (set(feat_all) & set(READ3)),
        "khong bai DA DOC nao chiem cho noi bat",
        str(sorted(set(feat_all) & set(READ3))))
    chk(s["feat"][0] == "lib-blackhole",
        "the lon la bai CHUA DOC dau tien theo thu tu khai bao", s["feat"][0])
    ctx.close()

    # ── [3] Da doc HET: van phai du 4, khong duoc hut ─────────────────────
    print("\n=== [3] Da doc het 8 bai ===")
    ALL8 = ["lib-nebula", "lib-andromeda", "lib-mars", "lib-blackhole",
            "lib-exoplanet", "lib-saturn", "lib-gaia", "lib-qubit"]
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    seed(ctx, ALL8)
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#hero-wrap .feat", timeout=15000)
    s = snap(pg)
    feat_all = s["feat"] + s["featCards"]
    chk(len(feat_all) == 4, "doc het roi VAN du 4 bai noi bat", str(len(feat_all)))
    chk(len(s["grid"]) == 4, "luoi giu 4 bai con lai", str(len(s["grid"])))

    # ── [4] Dang loc / dang tim: khoi noi bat an, luoi hien DU ────────────
    print("\n=== [4] Loc va tim kiem ===")
    pg.fill("#q", "Tinh vân")          # bai nay dang o khoi noi bat
    pg.wait_for_timeout(300)
    s = snap(pg)
    chk(not s["feat"] and not s["featCards"],
        "dang tim -> khoi noi bat AN", str(s["feat"] + s["featCards"]))
    chk("lib-nebula" in s["grid"] and not s["empty"],
        "tim dung ten bai DANG noi bat van ra ket qua", str(s["grid"]))
    pg.fill("#q", "")
    pg.wait_for_timeout(300)
    s = snap(pg)
    chk(len(s["feat"] + s["featCards"]) == 4,
        "xoa o tim -> khoi noi bat hien lai du 4", str(len(s['feat'] + s['featCards'])))

    pg.click('#cats .cat[data-cat="astronomy"]')
    pg.wait_for_timeout(300)
    s = snap(pg)
    chk(not s["feat"] and not s["featCards"], "dang loc chu de -> khoi noi bat AN")
    chk(len(s["grid"]) == 4,
        "loc 'Thien van' ra du 4 bai (ke ca bai dang noi bat)", str(s["grid"]))
    ctx.close()

    # ── [5] EN + dien thoai doc ──────────────────────────────────────────
    print("\n=== [5] EN + dien thoai 390x844 ===")
    ctx = br.new_context(viewport={"width": 390, "height": 844})
    seed(ctx, [], lang="en")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#hero-wrap .feat", timeout=15000)
    s = snap(pg)
    chk(len(s["feat"] + s["featCards"]) == 4, "390px: van du 4 bai noi bat")
    chk("Featured" in s["eyebrow"], "EN: nhan 'Featured articles'", s["eyebrow"])
    ov = pg.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1")
    chk(ov, "390px: khong tran ngang")
    title = pg.title()
    chk("Discovery Corner" in title, "EN: tieu de trang 'Discovery Corner'", title)
    ctx.close()

    chk(not errs, "0 loi console / pageerror", str(errs[:3]))
    br.close()

print(f"\n===== {OK} dat / {FAIL} hong =====")
sys.exit(1 if FAIL else 0)
