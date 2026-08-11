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
import os
import re
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    # ⚠️ HOI DU LIEU, DUNG GO SO. Truoc day cho nay gan cung "8" va no bao hong ngay
    #    khi hai mang ARTICLES duoc gop lai (thanh 9 bai) — tuc khang dinh dung mot
    #    trang thai khong con ton tai. Dieu can bao ve khong doi: KHONG SOT BAI NAO.
    N_ALL = pg.evaluate("() => AstroQArticles.all().length")
    chk(len(feat_all) + len(s["grid"]) == N_ALL,
        f"khoi noi bat + luoi = du {N_ALL} bai, khong sot bai nao",
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
    # Bai chua doc dau tien theo THU TU KHAI BAO — suy ra tu du lieu, khong go ten.
    want = pg.evaluate("(read) => AstroQArticles.all()"
                       ".filter(a => read.indexOf(a.id) < 0)[0].id", READ3)
    chk(s["feat"][0] == want,
        "the lon la bai CHUA DOC dau tien theo thu tu khai bao",
        f"{s['feat'][0]} (mong doi {want})")
    ctx.close()

    # ── [3] Da doc HET: van phai du 4, khong duoc hut ─────────────────────
    print("\n=== [3] Da doc het 8 bai ===")
    # Danh sach doc thang tu du lieu — them mot bai la bo kiem tu dung.
    _c = br.new_context(); _p = _c.new_page()
    _p.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    _p.goto(URL, wait_until="load")
    ALL8 = _p.evaluate("() => AstroQArticles.all().map(a => a.id)")
    _c.close()
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
    chk(len(s["grid"]) == len(ALL8) - 4, f"luoi giu {len(ALL8)-4} bai con lai",
        str(len(s["grid"])))

    # ── [4] Dang loc / dang tim: khoi noi bat an, luoi hien DU ────────────
    print("\n=== [4] Loc va tim kiem ===")
    pg.fill("#q", "Tinh vân")          # bai nay dang o khoi noi bat
    pg.wait_for_timeout(300)
    s = snap(pg)
    chk(not s["feat"] and not s["featCards"],
        "dang tim -> khoi noi bat AN", str(s["feat"] + s["featCards"]))
    chk("lib-nebula" in s["grid"] and not s["empty"],
        "tim dung ten bai DANG noi bat van ra ket qua", str(s["grid"]))

    # ── [4a] TIM KIEM TOAN VAN van chay sau khi CHIA KHO (09/08/2026) ─────
    # ⚠️ Truoc khi chia, `matches()` doc thang `a.body` vi ca kho nam trong trang. Nay
    #    than bai tai TRE, nen day la phep kiem duy nhat chung minh duong `primeSearch`
    #    -> `loadAll()` -> ve lai thuc su chay. Chon mot cum chi co trong THAN BAI va
    #    KHONG co trong bat ky tieu de nao — neu tim theo tieu de thi no phai ra 0.
    CUM = "khói của một chiếc xe"   # nam trong than bai `art-comet-tail-points-away`
    # ⚠️ Cum dau tien toi chon ("qua cau tuyet ban") KHONG CO trong bai nao — no o
    #    ghi chu cua ngan hang cau hoi. Phep kiem bao hong va suyt lam toi tuong
    #    duong tim kiem hong. `grep -rl` tren js/article/ la cach kiem 2 giay.
    _tit = pg.evaluate(
        "c => AstroQArticles.all().filter(a =>"
        " (a.title.vi + ' ' + a.title.en).toLowerCase().includes(c)).length",
        CUM.lower())
    chk(_tit == 0, f"cum thu '{CUM}' KHONG nam o tieu de nao (nen phep kiem co nghia)",
        str(_tit))
    pg.fill("#q", "")
    pg.wait_for_timeout(150)
    pg.click("#q")                     # `primeSearch` chay tu cu CHAM, som hon cu go
    pg.fill("#q", CUM)
    # cho `loadAll()` ve roi trang tu ve lai — khong ngu mot khoang co dinh
    try:
        pg.wait_for_function(
            "() => document.querySelectorAll('#grid .card').length === 1",
            timeout=8000)
    except Exception:
        pass
    s = snap(pg)
    chk(s["grid"] == ["art-comet-tail-points-away"],
        "tim TOAN VAN (cum chi co trong than bai) ra dung 1 bai", str(s["grid"]))
    pg.fill("#q", "")
    pg.wait_for_timeout(300)
    s = snap(pg)
    chk(len(s["feat"] + s["featCards"]) == 4,
        "xoa o tim -> khoi noi bat hien lai du 4", str(len(s['feat'] + s['featCards'])))

    pg.click('#cats .cat[data-cat="astronomy"]')
    pg.wait_for_timeout(300)
    s = snap(pg)
    chk(not s["feat"] and not s["featCards"], "dang loc chu de -> khoi noi bat AN")
    n_astro = pg.evaluate("() => AstroQArticles.all()"
                          ".filter(a => a.cat === 'astronomy').length")
    chk(len(s["grid"]) == n_astro,
        f"loc 'Thien van' ra du {n_astro} bai (ke ca bai dang noi bat)", str(s["grid"]))
    ctx.close()

    # ── [4b] LOI THAT MA VIEC GOP HAI MANG ARTICLES SINH RA DE SUA ───────
    # Truoc 05/08/2026 `learn.html` va `library.html` moi trang mot mang rieng, cung
    # mot bai lai mang HAI id (`gaia` vs `lib-gaia`). Ca hai ghi vao cung khoa
    # `astroq-read` theo id, nen:
    #   ① doc Gaia o Tram Tri Thuc -> sang Goc Kham Pha van bao CHUA DOC
    #   ② `AstroQProgress.lesson(id)` gui hai id khac nhau -> server dem HAI LAN cho
    #      cung mot noi dung (huy hieu doc sach mo bang cach doc mot bai o hai cho)
    # Phep kiem nay canh dung dieu do, va canh ca duong lui cho tre da doc id CU.
    print("\n=== [4b] Gop hai mang: id cu van duoc tinh la da doc ===")
    OLD_NEW = [("gaia", "lib-gaia"), ("eht", "lib-blackhole"),
               ("exo-ai", "lib-exoplanet")]
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    seed(ctx, [o for o, _ in OLD_NEW])          # tre chi tung doc o learn.html
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#hero-wrap .feat", timeout=15000)
    for old, new in OLD_NEW:
        chk(pg.evaluate("(id) => AstroQArticles.isRead(id)", new),
            f"doc '{old}' o trang cu -> '{new}' tinh la DA DOC")
    s = snap(pg)
    feat_all = s["feat"] + s["featCards"]
    chk(not (set(feat_all) & {n for _, n in OLD_NEW}),
        "bai da doc bang id cu KHONG chiem cho noi bat", str(feat_all))
    # Va khong con id nao trung nhau giua hai trang
    ids = pg.evaluate("() => AstroQArticles.all().map(a => a.id)")
    chk(len(ids) == len(set(ids)), "khong co id trung trong kho bai doc", str(ids))
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

    # ══════════════════════════════════════════════════════════════════════════
    print("\n=== [6] MO TUNG BAI MOT — phep kiem lo ra vi mot loi CO SAN ===")
    # ⚠️⚠️ VI SAO MUC NAY TON TAI. Ngay 06/08/2026 phat hien bai `jwst` — dang chay
    #    that tu dot gop 05/08 — KHONG MO DUOC o library.html: `openReader` doc
    #    `a.term.who` ma bai do khong khai `term`, nen no nem TypeError ngay TRUOC
    #    dong `classList.add("show")`. Tre bam vao the va khong co gi xay ra.
    #    Loi im lang hoan toan voi nguoi dung, va **khong bo kiem nao bat duoc vi
    #    khong bo nao MO TUNG BAI** — chung chi dem the, loc the, do bo cuc.
    #    ⇒ Tu nay: mo HET moi bai, doi trinh doc that su hien ra va 0 loi.
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    seed(ctx, [])
    pg = ctx.new_page()
    # ⚠️ CHI DEM NGOAI LE JS, KHONG DEM LOI TAI TAI NGUYEN. Chinh bo do nay chan anh
    #    NASA bang `route().abort()` de khoi phu thuoc mang, nen trinh duyet luon bao
    #    `Failed to load resource: net::ERR_FAILED` — do la pha hoai CUA TOI, khong
    #    phai loi san pham. Dem no vao la phep kiem bao oan 8 lan moi luot chay, ma
    #    mot phep kiem hay bao oan thi som muon bi bo qua.
    e6 = []
    pg.on("pageerror", lambda e: e6.append(str(e)[:110]))
    pg.on("console", lambda m: e6.append(m.text[:110])
          if m.type == "error" and "Failed to load resource" not in m.text else None)
    pg.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#hero-wrap .feat", timeout=15000)
    ids = pg.evaluate("() => Array.from(document.querySelectorAll('[data-id]')).map(e => e.dataset.id)")
    chk(len(ids) >= 14, f"trang co du bai de mo ({len(ids)})", str(len(ids)))
    hong = []
    for aid in ids:
        e6.clear()
        pg.evaluate("() => document.getElementById('reader').classList.remove('show')")
        pg.eval_on_selector(f'[data-id="{aid}"]', "e => e.scrollIntoView({block:'center'})")
        pg.wait_for_timeout(120)
        pg.click(f'[data-id="{aid}"]')
        pg.wait_for_timeout(380)
        if not pg.eval_on_selector("#reader", "e => e.classList.contains('show')") or e6:
            hong.append(f"{aid}{e6[:1]}")
    chk(not hong, f"ca {len(ids)} bai deu mo duoc trinh doc, 0 loi", str(hong[:3]))

    # ⚠️ Khoi linh vat la PHAN THEM: bai co `term` thi hien, khong co thi PHAI an han.
    #    `[hidden]` mot minh KHONG du — `.mascot` khai `display:flex` nen no thang
    #    `display:none` cua trinh duyet. Do la bai hoc `#time-ok` / `.pbtn` cua du an,
    #    nen o day do `display` THAT chu khong doc thuoc tinh `hidden`.
    r = pg.evaluate("""() => {
        const out = {co: null, khong: null};
        return out; }""")
    for aid, mong in (("lib-nebula", "flex"), ("jwst", "none")):
        pg.evaluate("() => document.getElementById('reader').classList.remove('show')")
        pg.eval_on_selector(f'[data-id="{aid}"]', "e => e.scrollIntoView({block:'center'})")
        pg.click(f'[data-id="{aid}"]')
        pg.wait_for_timeout(300)
        d = pg.eval_on_selector("#r-mascot", "e => getComputedStyle(e).display")
        chk(d == mong, f"{aid}: khoi linh vat display={mong}", d)

    # ⚠️ `credit` null (bai khong anh) thi KHONG duoc in ra chu "null" — ghi cong cho
    #    mot buc anh khong ton tai con te hon khong ghi gi.
    cr = pg.eval_on_selector("#r-credit", "e => e.textContent")
    chk("null" not in cr, "bai khong anh: dong credit khong in chu 'null'", repr(cr))
    ctx.close()

    # ══════════════════════════════════════════════════════════════════════════
    print("\n=== [7] `terms` -> quiz.html?terms= (day noi bai doc sang cau hoi) ===")
    # ⚠️ Truong `terms` cua bai doc tung la DU LIEU CHET — khong code nao doc no.
    #    Nay nut "Lam Quiz bai nay" gui no sang quiz.html. Muc nay canh ca hai dau:
    #    nut co truyen khong, va quiz co rut dung cau cua bai do khong.
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    seed(ctx, [])
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("https://images-assets.nasa.gov/**", lambda r: r.abort())
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#hero-wrap .feat", timeout=15000)
    AID = "art-blood-moon-lunar-eclipse"
    pg.eval_on_selector(f'[data-id="{AID}"]', "e => e.scrollIntoView({block:'center'})")
    pg.click(f'[data-id="{AID}"]')
    pg.wait_for_timeout(400)
    with pg.expect_navigation():
        pg.click("#r-quiz")
    chk("terms=" in pg.url, "nut Quiz truyen `terms` cua bai dang doc", pg.url[-70:])
    pg.wait_for_timeout(1600)
    chk(pg.eval_on_selector("#q-total", "e => e.textContent").strip() == "5",
        "luot van du 5 cau (khong de bai 4 khoa lam luot ngan lai)")
    # Choi het luot, dem so cau THUOC dung bai doc.
    thay = []
    for _ in range(9):
        thay.append(pg.eval_on_selector("#q-text", "e => e.textContent"))
        pg.eval_on_selector_all("#q-options .opt", "e => e[0].click()")
        pg.wait_for_timeout(200)
        pg.click("#engage")
        pg.wait_for_timeout(430)
        pg.click("#next-btn")
        pg.wait_for_timeout(430)
        if pg.eval_on_selector("#summary", "e => e.classList.contains('show')"):
            break
    trung = sum(1 for q in thay if "nguyệt thực" in q.lower() or "Mặt Trăng" in q)
    chk(trung >= 4, f"luot chua >= 4 cau dung chu de bai doc ({trung}/{len(thay)})",
        "; ".join(x[:36] for x in thay))
    # ⚠️ DUONG LUI: tham so thieu / rac KHONG duoc lam vo trang. Mot duong vao phu
    #    khong bao gio duoc phep pha duong vao chinh.
    for nhan, q in (("khong tham so", ""), ("tham so rong", "?terms="),
                    ("khoa rac", "?terms=abc,xyz"), ("phay rong", "?terms=,,,")):
        pg.goto(URL.replace("library.html", "quiz.html") + q, wait_until="load")
        pg.wait_for_timeout(1400)
        chk(pg.eval_on_selector("#q-total", "e => e.textContent").strip() == "5",
            f"duong lui '{nhan}': van rut du 5 cau")
    ctx.close()

    # ── [8] CAU TRUC KHO BAI DOC — hang rao dau tien cua `js/articles.js` ──────
    # ⚠️ VI SAO O DAY MA KHONG O check_pages.py: doc file bang regex thi phai doan
    #    ranh gioi tung object, ma file nay long nhieu muc va co chuoi chua dau `{`.
    #    O day trinh duyet DA PHAN TICH HO — `AstroQArticles.all()` tra ve object
    #    that. Phan doi chieu voi dia (khoa quiz co file khong) thi Python lo.
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.on("weberror", lambda e: errs.append(str(e)))
    pg = ctx.new_page()
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector(".card")
    # ⚠️ KHO DA CHIA 09/08/2026: `all()` nay tra ve MUC LUC (nhe), than bai nam o
    #    `js/article/<id>.js`. Nen phai HOP hai nua lai moi kiem duoc cau truc day du —
    #    `loadAll()` la duong CHINH THUC de lay het, dung cho tim kiem toan van.
    idx = pg.evaluate("() => AstroQArticles.all()")
    chk(len(idx) >= 19, f"doc duoc MUC LUC ({len(idx)} bai)")
    # ⚠️ QUET MOI DONG, KHONG chi `idx[0]`. Ban dau toi chi soi phan tu dau tien, va
    #    phep thu pha hoai (nhet `body` vao mot dong o GIUA muc luc) LOT — vi dong dau
    #    van sach. Mot phep kiem chi xem phan tu dau la mot phep kiem xem 1/39 du lieu.
    LIGHT_ONLY = ("body", "term", "terms", "url", "credit")
    _phinh = sorted({k for e in idx for k in LIGHT_ONLY if k in e})
    chk(not _phinh, "muc luc KHONG chua than bai (giu duong tai nhe)", str(_phinh))
    # ⚠️ THU TU MUC LUC LA THU TU CURATION: `featured()` lay "bai chua doc dau tien theo
    #    thu tu muc luc" lam THE LON. Che do SINH LAI cua bo chia doc file bang `glob`
    #    (a-b-c), va lan dau chay no da AM THAM doi thu tu — the lon nhay tu `jwst` sang
    #    `art-ai-already-around-you`. Khong phep kiem nao bat, vi tat ca deu SUY thu tu
    #    tu chinh du lieu. Nay `ord` nam trong file bai va muc luc phai sap theo no.
    _ords = [e.get("ord") for e in idx]
    chk(all(o is not None for o in _ords), "moi dong muc luc co `ord`",
        str([e["id"] for e in idx if e.get("ord") is None][:3]))
    chk(_ords == sorted(o for o in _ords if o is not None),
        "muc luc sap TANG theo `ord` (thu tu curation, khong phai a-b-c)",
        str(_ords[:6]))
    full = pg.evaluate("() => AstroQArticles.loadAll()")
    chk(len(full) == len(idx),
        f"loadAll() tai duoc DU than bai ({len(full)}/{len(idx)})")
    # hop muc luc + than bai -> object day du nhu truoc khi chia
    _by = {a["id"]: a for a in full}
    arts = [dict(e, **_by.get(e["id"], {})) for e in idx]

    # ⛔ Chan "dat rong": 0 bai thi moi vong lap duoi day deu di qua sach se.
    chk(len(arts) >= 19, f"hop duoc kho bai doc day du ({len(arts)} bai)")

    CATS = set(pg.evaluate(
        "() => Array.from(document.querySelectorAll('#cats .cat'))"
        ".map(b => b.dataset.cat).filter(c => c !== 'all')"))
    chk(len(CATS) == 4, "doc duoc bo loc chu de tu sidebar", str(sorted(CATS)))

    QUIZ = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(ROOT, "js", "quiz"))
            if f.endswith(".js")}
    chk(len(QUIZ) >= 100, f"doc duoc ngan hang cau hoi ({len(QUIZ)} khoa)")

    # ⚠️ `mit.edu` them 09/08/2026 — KHONG phai noi long chinh sach nguon, MIT DA LA nguon
    #    tin cay cua du an: bo `wiki/` dan `media.mit.edu` · `scratch.mit.edu` ·
    #    `appinventor.mit.edu`, va muc 2 CLAUDE.md ghi nguon wiki la "NASA/ESA/MIT".
    #    Can no vi NASA gan nhu khong co noi dung ve AI trong DOI SONG (thuat toan de
    #    xuat, thien lech, quyen rieng tu) — thu ma tre 8-15 gap moi ngay.
    OKDOM = ("nasa.gov", "esa.int", "noaa.gov", "usgs.gov", "nps.gov",
             "mit.edu", "exploratorium.edu", "lco.global", "ucar.edu")
    # ⚠️ GHIM MON NO, KHONG NOI RONG OKDOM — dung khuon `_KNOWN_CDN` cua check_pages:
    #    liet ke dung cai dang sai de them cai THU HAI la biet ngay, va danh sach tu
    #    that lai khi don xong. Noi rong OKDOM thi moi trang thuong mai deu lot.
    #    ✅ DA DON XONG 09/08/2026: `lib-qubit` tung dan `ibm.com/quantum` (trang san pham)
    #    trong khi credit ghi "MIT / IBM Research"; nay dan trang QuAIL cua NASA. Danh
    #    sach RONG, va phep kiem duoi day giu no rong — them mot nguon ngoai la bao ngay.
    LEGACY_SRC = set()
    ids, bad = set(), {}

    def flag(a, why):
        bad.setdefault(why, []).append(a.get("id", "?"))

    for a in arts:
        i = a.get("id", "")
        if i in ids:
            flag(a, "id trung")
        ids.add(i)
        if not re.fullmatch(r"[a-z0-9-]+", i):
            flag(a, "id sai dinh dang")
        if a.get("cat") not in CATS:
            flag(a, "cat khong co trong bo loc")
        # song ngu du — thieu mot ben la trang hien khoa tho hoac o trong
        for f in ("title", "body"):
            v = a.get(f) or {}
            if not v.get("vi") or not v.get("en"):
                flag(a, f"thieu song ngu o `{f}`")
        b = a.get("body") or {}
        # ⚠️ Lech SO DOAN thi ban EN va ban VI ke hai cau chuyen dai ngan khac nhau,
        #    va khong co gi bao — trang van ve binh thuong.
        if isinstance(b.get("vi"), list) and isinstance(b.get("en"), list) \
                and len(b["vi"]) != len(b["en"]):
            flag(a, f"body vi/en lech so doan ({len(b['vi'])} vs {len(b['en'])})")
        t = a.get("term")
        if t:
            if t.get("who") not in ("comet", "byte"):
                flag(a, "term.who khong phai linh vat")
            for f in ("word", "text"):
                v = t.get(f) or {}
                if not v.get("vi") or not v.get("en"):
                    flag(a, f"thieu song ngu o `term.{f}`")
        # ⚠️ `terms` la DAY NOI sang bank; sai mot chu la day dut IM LANG.
        for k in (a.get("terms") or []):
            if k not in QUIZ:
                flag(a, f"khoa quiz `{k}` khong co file")
        # ⚠️ CO Y KHONG doi `credit` phai null theo `img`: `credit` la credit NGUON
        #    DU LIEU, library.html:285 in no khong phu thuoc anh. Thu phai canh la
        #    `img` — chuoi rong thi moi cho dung `if (a.img)` deu coi nhu khong anh,
        #    tuc mot gia tri khong bao gio dung toi ma van doc ra nhu co anh.
        im = a.get("img")
        if im is not None and not (isinstance(im, str) and im.startswith("https://")):
            flag(a, "`img` khong phai null cung khong phai URL https")
        u = a.get("url") or ""
        if not u.startswith("https://") or (
                not any(d in u for d in OKDOM) and i not in LEGACY_SRC):
            flag(a, "url khong thuoc nguon tin cay")
        c = a.get("c") or []
        if len(c) != 3 or not all(re.fullmatch(r"#[0-9a-fA-F]{6}", x) for x in c):
            flag(a, "`c` khong phai 3 ma mau hex")
        # ⛔ Doc bai KHONG con thuong tu 30/07/2026 (`Wallet.MaxPerLesson = 0`).
        #    Hua sai la loi da phai di sua mot lan.
        blob = " ".join((b.get("vi") or []) + (b.get("en") or []))
        if "Thiên thạch tím" in blob or "Purple Meteor" in blob:
            flag(a, "hua thuong Thien thach tim trong than bai")

    for why in sorted(bad):
        chk(False, f"kho bai doc: {why}", ", ".join(bad[why][:4]))
    chk(not bad, "moi bai dung cau truc (id · song ngu · terms · nguon · mau)",
        f"{len(arts)} bai, 0 loi" if not bad else "")
    # Danh sach mien tru phai TU THAT LAI, khong duoc phinh ra. Nay da RONG.
    chk(not LEGACY_SRC,
        f"0 bai duoc mien tru khoi danh sach nguon tin cay ({len(LEGACY_SRC)})",
        ", ".join(sorted(LEGACY_SRC)))
    # ⛔ Khong bai nao duoc noi qubit "vua 0 vua 1" — NASA viet la "MOT CHONG CHAP cua ca
    #    hai gia tri", va hai bai luong tu trong kho tung noi hai kieu ve dung cho nay.
    # ⚠️⚠️ MIEN TRU PHAI THEO CUA SO QUANH TUNG CHO XUAT HIEN, KHONG theo ca bai.
    #    Ban dau toi mien tru theo ca bai, va `lib-qubit` co chu "khong phai" o doan 2
    #    (cau "Day khong phai chuyen bat be chu nghia") => mot chu do cap MIEN NHIEM cho
    #    TOAN BAI, nen phep pha (nhet "vua 0 vua 1" vao doan 1) LOT. Phep kiem rong.
    BAD = ("cả 0 và 1 cùng lúc", "vừa là 0 vừa là 1", "vừa 0 vừa 1",
           "both 0 and 1 at the same time", "both heads and tails until")
    NEG = ("không phải", "không viết", "nhưng nasa", "dẫn tới một ý sai", "nên tránh",
           "not what nasa", 'not "both', "leads to a worse idea", "worth avoiding")
    W = 200  # ky tu moi ben — du de phu mot cau giai thich, khong du de phu ca bai
    _sai = []
    for a in arts:
        b = a.get("body") or {}
        parts = (b.get("vi") or []) + (b.get("en") or [])
        t = ((a.get("term") or {}).get("text") or {})
        parts += [t.get("vi") or "", t.get("en") or ""]
        low = " ␟ ".join(parts).lower()   # dau ngan doan de cua so khong tran doan khac
        for cum in BAD:
            i = low.find(cum)
            while i >= 0:
                win = low[max(0, i - W): i + len(cum) + W]
                if not any(k in win for k in NEG):
                    _sai.append(f"{a['id']}: “{cum}” khong co chu bac ben canh")
                i = low.find(cum, i + 1)
    chk(not _sai, "khong bai nao noi qubit 'vua 0 vua 1' ma khong bac lai ngay canh",
        "; ".join(_sai[:3]))
    ctx.close()

    # ── [9] MO BANG `file://`: PHAI NOI DUNG LY DO ────────────────────────────
    # ⚠️ Chu du an gap that 09/08/2026: mo library.html tu o dia thi trinh doc hien
    #    "Khong tai duoc noi dung bai nay. Kiem tra ket noi roi thu lai nhe." — mot cau
    #    NOI SAI NGUYEN NHAN. Do duoc: `file://` chan `import()` module (CORS, origin
    #    'null'), mang khong lien quan gi, nen nguoi doc bi chi di sua mot thu khong hong.
    # ⚠️ Day la HE QUA cua viec chia kho cung ngay: truoc do ca kho nam trong mot script
    #    co dien nen xem bang file:// van doc duoc bai.
    _root = ROOT.replace("\\", "/")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
    pg = ctx.new_page()
    pg.goto("file:///" + _root + "/library.html", wait_until="load")
    pg.wait_for_selector(".card", timeout=15000)
    chk(pg.evaluate("()=>AstroQArticles.needsServer()") is True,
        "[file://] needsServer() nhan ra giao thuc")
    _n_idx = pg.evaluate("()=>AstroQArticles.all().length")
    chk(_n_idx >= 39, "[file://] MUC LUC van nap duoc (script co dien)", str(_n_idx))
    pg.click('.card[data-id="art-atmosphere-shield"]')
    pg.wait_for_timeout(1600)
    _t = pg.eval_on_selector("#r-body", "e=>e.textContent")
    chk("file://" in _t and "http.server" in _t,
        "[file://] noi ly do THAT (giao thuc) va chi cach sua", _t[:56])
    chk("Kiểm tra kết nối" not in _t,
        "[file://] KHONG bao 'kiem tra ket noi' (mang khong lien quan)")
    ctx.close()

    chk(not errs, "0 loi console / pageerror", str(errs[:3]))
    br.close()

print(f"\n===== {OK} dat / {FAIL} hong =====")
sys.exit(1 if FAIL else 0)
