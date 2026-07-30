# -*- coding: utf-8 -*-
"""
smoke_missions.py — ĐO TRÊN TRANG: Sảnh Nhiệm Vụ (missions.html) + Trung Tâm Điều
Hướng 6 card (dashboard.html).

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    set PYTHONIOENCODING=utf-8        (Windows — không thì print chữ Việt là lỗi)
    python scratchpad/smoke_missions.py

Bộ này canh đúng những thứ đọc code KHÔNG thấy được:
  · tên khu mới có tràn header trên màn 390px không ("Về Trung Tâm Điều Hướng" dài
    hơn "Về Khoang Lái" 10 ký tự — đó là cả một dòng trên điện thoại);
  · 6 card có xếp thành lưới tử tế không, hay card thứ 6 mồ côi một hàng;
  · CHƯA ĐĂNG NHẬP thì tiến độ nhiệm vụ phải hiện dấu "—", KHÔNG hiện 0/8 —
    "0/8 bước" là một lời khẳng định SAI về tiến độ người chơi;
  · hai card "Sắp ra mắt" thật sự KHÔNG bấm được (nút disabled), không chỉ mờ đi.
"""
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"

ok = fail = 0
FAILS = []


def chk(cond, name, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  [ok]   {name}" + (f"  {extra}" if extra else ""))
    else:
        fail += 1
        FAILS.append(name)
        print(f"  [FAIL] {name}" + (f"  {extra}" if extra else ""))


def head(t):
    print(f"\n=== {t} ===")


def newpage(ctx, lang="vi"):
    """Mở tab mới, ghim ngôn ngữ, và TẮT hai màn chỉ-chạy-lần-đầu.

    ⚠️ Bắt buộc phải gieo `astroq-tour-seen` + `astroq-mission01-intro-seen` (đúng
    lối `shot_pages.py`/`measure_shell.py` đã dùng): trên dashboard, màn Comet dẫn
    tham quan phủ một lớp `.tour-block` chắn hết chuột, nên mọi cú bấm (ví dụ nút
    EN) bị nó ăn và Playwright thử lại tới khi hết giờ. Bộ test này từng "đạt" vì
    bấm KỊP trước lúc tour hiện — tức là nó phụ thuộc vào thời gian chạy, thêm vài
    phép đo phía trước là hỏng. Tắt hẳn thì phép kiểm mới ổn định; màn tour đã có
    bộ test riêng ở `smoke_onboard.py`.
    """
    errs = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.add_init_script(
        "localStorage.setItem('astroq-lang', %r);" % lang
        + "localStorage.setItem('astroq-tour-seen','1');"
        + "localStorage.setItem('astroq-mission01-intro-seen','1');")
    return pg, errs


def no_overflow(pg):
    return pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ══════════════════════════════════════════════════════════════
        head("[1] missions.html — 2 nhiem vu, tien do THAT")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector(".mcard", timeout=15000)

        cards = pg.eval_on_selector_all(
            ".mcard",
            """es => es.map(e => ({
                 code: e.querySelector('.hud-line.top span').textContent.trim(),
                 name: e.querySelector('h3').textContent.trim(),
                 soon: e.classList.contains('soon'),
                 btn:  e.querySelector('.play-btn').textContent.trim(),
                 locked: e.querySelector('.play-btn').classList.contains('locked'),
                 prog: e.querySelector('.mprog .n') ? e.querySelector('.mprog .n').textContent.trim() : null
               }))""")
        chk(len(cards) == 2, "co dung 2 the nhiem vu", str([c["code"] for c in cards]))
        earth = next((c for c in cards if "MISSION-01" in c["code"]), None)
        moon = next((c for c in cards if "MISSION-02" in c["code"]), None)
        chk(earth is not None, "co MISSION-01")
        chk(moon is not None, "co MISSION-02")
        if earth:
            chk("Hành Tinh Xanh" in earth["name"], "MISSION-01 ten 'Hanh Tinh Xanh'", earth["name"])
            chk(earth["soon"] is False and earth["locked"] is False,
                "MISSION-01 bam duoc", earth["btn"])
        if moon:
            chk(moon["soon"] is True and moon["locked"] is True,
                "MISSION-02 dang 'Sap ra mat', nut khoa", moon["btn"])
            chk(moon["prog"] is None,
                "MISSION-02 KHONG ve thanh tien do (chua co nhiem vu thi khong co tien do)")

        # Ready truoc, soon sau — dung thu tu hien thi cua games.html
        chk("MISSION-01" in cards[0]["code"],
            "nhiem vu san sang xep TRUOC nhiem vu sap ra mat", cards[0]["code"])

        # ── CHUA DANG NHAP: phai hien dau "—", khong hien so 0 ──
        pg.wait_for_selector("#offline.show", timeout=15000)
        chk(True, "co dai nhac 'chua doc duoc tien do'")
        banner = pg.eval_on_selector("#offline-msg", "e => e.textContent")
        chk("—" in banner or "—" in banner, "dai nhac noi ro dang hien dau gach ngang",
            banner[:60])
        ov = pg.eval_on_selector_all("#ov .cell .v", "es => es.map(e => e.textContent.trim())")
        chk(len(ov) == 3, "bang dieu phoi co 3 o", str(ov))
        chk(all(v == "—" for v in ov),
            "chua dang nhap: ca 3 o hien dau '—', KHONG hien 0", str(ov))
        if earth:
            chk(earth["prog"].startswith("—"),
                "MISSION-01: thanh tien do hien '—/8', khong phai '0/8'", earth["prog"])
        barw = pg.eval_on_selector(".mcard .mprog .bar i", "e => e.getBoundingClientRect().width")
        chk(barw < 1, "thanh tien do rong 0px khi chua biet tien do", f"{barw:.1f}px")

        chk(len(errs) == 0, "missions.html: 0 loi console", "; ".join(errs[:3]))

        # ── Bam MISSION-01 → mission-earth.html ──
        pg.click('.mcard:not(.soon) .play-btn')
        pg.wait_for_url("**/mission-earth.html", timeout=15000)
        chk(pg.url.endswith("mission-earth.html"), "bam MISSION-01 dan sang mission-earth.html",
            pg.url)
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[2] missions.html — tieng Anh")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs2 = newpage(ctx, "en")
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector(".mcard", timeout=15000)
        chk(pg.evaluate("document.documentElement.lang") == "en", "the html lang=en")
        h1 = pg.eval_on_selector("h1", "e => e.textContent")
        chk(not any(c in h1 for c in "ệộứạảầ"), "tieu de dich sang tieng Anh", h1)
        back = pg.eval_on_selector("#back", "e => e.textContent")
        chk("Navigation Hub" in back, "nut quay lai: 'Back to Navigation Hub'", back.strip())
        soon_btn = pg.eval_on_selector(".mcard.soon .play-btn", "e => e.textContent.trim()")
        chk(soon_btn == "Coming soon", "EN: nut 'Coming soon'", soon_btn)
        chk(len(errs2) == 0, "EN: 0 loi console", "; ".join(errs2[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[3] dashboard.html — 6 card, ten khu moi")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs3 = newpage(ctx)
        pg.goto(BASE + "/dashboard.html", wait_until="load")
        pg.wait_for_selector(".cards .hud", timeout=15000)

        hud = pg.eval_on_selector_all(
            ".cards .hud",
            """es => es.map(e => ({
                 mod: e.querySelector('.hud-line.top span').textContent.trim(),
                 name: e.querySelector('h3').textContent.trim(),
                 soon: e.classList.contains('soon'),
                 btn: e.querySelector('.jelly-btn').textContent.trim(),
                 disabled: !!e.querySelector('.jelly-btn[disabled]'),
                 href: e.querySelector('a.jelly-btn') ? e.querySelector('a.jelly-btn').getAttribute('href') : null,
                 top: Math.round(e.getBoundingClientRect().top)
               }))""")
        chk(len(hud) == 6, "co dung 6 card HUD", str(len(hud)))
        names = [h["name"] for h in hud]
        for want in ("Trung Tâm Nhiệm Vụ", "Tri Thức", "Khu Huấn Luyện",
                     "Bản Đồ Thiên Hà", "Phòng Nghiên Cứu", "Thư Viện Thiên Văn"):
            chk(want in names, f"co card '{want}'", "")
        mods = [h["mod"] for h in hud]
        chk(all(any(m in x for x in mods) for m in
                ("MOD-01", "MOD-02", "MOD-03", "MOD-04", "MOD-05", "MOD-06")),
            "du so hieu MOD-01..MOD-06", str(mods))
        # Trung Tam Nhiem Vu len DAU (duong di chinh cua tre)
        chk("Trung Tâm Nhiệm Vụ" in hud[0]["name"],
            "Trung Tam Nhiem Vu xep dau tien", hud[0]["name"])
        mission_card = next(h for h in hud if "Nhiệm Vụ" in h["name"])
        chk(mission_card["href"] == "missions.html",
            "card Mission Control dan sang missions.html", str(mission_card["href"]))
        # Hai card chua co trang: nut PHAI disabled
        soons = [h for h in hud if h["soon"]]
        chk(len(soons) == 2, "co dung 2 card 'Sap ra mat'", str([h["name"] for h in soons]))
        chk(all(h["disabled"] for h in soons),
            "ca 2 card 'Sap ra mat' co nut disabled (bam khong duoc)")
        chk(all(h["href"] is None for h in soons),
            "card 'Sap ra mat' KHONG dan sang trang nao")
        # Hai card do phai xuong CUOI luoi (ready truoc, soon sau)
        chk(min(h["top"] for h in soons) >= max(h["top"] for h in hud if not h["soon"]),
            "2 card 'Sap ra mat' nam o hang duoi cung")
        # Den bao: xanh = dang chay, ho phach = standby. Khong duoc de xanh o card khoa.
        led = pg.eval_on_selector_all(
            ".cards .hud.soon .hud-line .led",
            "es => es.map(e => getComputedStyle(e).animationName)")
        chk(all(a == "none" for a in led),
            "den bao cua card khoa NGUNG nhap nhay", str(led))
        # ---- Badge phi da bo khoi card Khu Huan Luyen (30/07/2026) ----
        # Phi VAN bi tru trong tung game (Economy.spend), chi la khong quang cao con
        # so o day nua. Dashboard chi co MOT con so nen bao gio cung sai voi Ghep Chom
        # Sao (3 tt/luot chu khong phai 5) — badge phi dung cho o games.html.
        chk(pg.eval_on_selector_all(".cards .cost", "es => es.length") == 0,
            "card HUD khong con badge phi '5 tt / luot'")
        chk(pg.eval_on_selector_all(".cards .hud img", "es => es.length") == 0,
            "khong con anh thien thach tim tren card HUD")
        # Bo badge KHONG duoc lam le not: `.hud p{flex:1}` neo nut xuong day the, nen
        # trong CUNG MOT HANG moi nut phai o cung mot cao do. (Da tung lech 3px vi nut
        # disabled co vien 1px dashed lam nut cao them 2px — xem ghi chu o .jelly-btn.)
        btns = pg.eval_on_selector_all(".cards .hud .jelly-btn", """es => es.map(e => ({
              h: +e.getBoundingClientRect().height.toFixed(2),
              top: +e.getBoundingClientRect().top.toFixed(2)
            }))""")
        chk(len({b["h"] for b in btns}) == 1,
            "moi nut card cao bang nhau (ke ca nut disabled)",
            str(sorted({b["h"] for b in btns})))
        rows = {}
        for b in btns:
            rows.setdefault(round(b["top"] / 50), []).append(b["top"])
        chk(all(len(set(v)) == 1 for v in rows.values()),
            "nut trong cung mot hang thang hang tuyet doi",
            str({k: sorted(set(v)) for k, v in rows.items()}))

        eyebrow = pg.eval_on_selector(".hero .eyebrow", "e => e.textContent")
        chk("Trung Tâm Điều Hướng" in eyebrow,
            "dashboard tu goi minh la 'Trung Tam Dieu Huong'", eyebrow.strip())
        chk(pg.evaluate("document.title").find("Trung Tâm Điều Hướng") >= 0,
            "the <title> doi theo", pg.evaluate("document.title"))
        chk(no_overflow(pg), "1440px: khong tran ngang")
        chk(len(errs3) == 0, "dashboard: 0 loi console", "; ".join(errs3[:3]))

        # EN
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(400)
        en_names = pg.eval_on_selector_all(".cards .hud h3", "es => es.map(e => e.textContent.trim())")
        for want in ("Mission Control", "Knowledge Station", "Training Simulator",
                     "Galaxy Map", "Research Lab", "Star Archive"):
            chk(want in en_names, f"EN: co card '{want}'", "")
        chk("Navigation Hub" in pg.eval_on_selector(".hero .eyebrow", "e => e.textContent"),
            "EN: hero eyebrow 'Navigation Hub'")
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[4] Dien thoai 390x844 — ten khu dai hon co lam tran header?")
        for page in ("missions.html", "dashboard.html", "games.html", "learn.html",
                     "profile.html", "achievements.html", "specimen-vault.html"):
            ctx = br.new_context(viewport={"width": 390, "height": 844},
                                 is_mobile=True, has_touch=True)
            pg, e4 = newpage(ctx)
            pg.goto(BASE + "/" + page, wait_until="load")
            pg.wait_for_timeout(700)
            chk(no_overflow(pg), f"{page}: khong tran ngang",
                str(pg.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")))
            # Nut quay lai phai nam GON trong man hinh va doc duoc het chu
            sel = "#back"
            if pg.query_selector(sel):
                b = pg.eval_on_selector(sel, """e => {
                  const r = e.getBoundingClientRect();
                  return [Math.round(r.left), Math.round(r.right), e.scrollWidth, e.clientWidth];
                }""")
                chk(b[0] >= -1 and b[1] <= 391, f"{page}: nut quay lai trong man hinh", str(b[:2]))
                chk(b[2] <= b[3] + 1, f"{page}: chu tren nut quay lai KHONG bi cat", str(b[2:]))
            ctx.close()

        # 6 card tren dien thoai: phai xep 1 cot, khong card nao bi bop
        ctx = br.new_context(viewport={"width": 390, "height": 844},
                             is_mobile=True, has_touch=True)
        pg, e5 = newpage(ctx)
        pg.goto(BASE + "/dashboard.html", wait_until="load")
        pg.wait_for_selector(".cards .hud", timeout=15000)
        w = pg.eval_on_selector_all(".cards .hud",
                                    "es => es.map(e => Math.round(e.getBoundingClientRect().width))")
        chk(len(set(w)) == 1, "390px: 6 card cung be rong (xep 1 cot)", str(w))
        chk(w and w[0] <= 390, "390px: card khong rong hon man hinh", str(w[:1]))
        h3 = pg.eval_on_selector_all(".cards .hud h3",
                                     "es => es.map(e => e.scrollWidth <= e.clientWidth + 1)")
        chk(all(h3), "390px: tieu de card nao cung du cho, khong bi cat", str(h3))
        chk(len(e5) == 0, "390px dashboard: 0 loi console", "; ".join(e5[:3]))
        ctx.close()

        br.close()

    print("\n" + "=" * 60)
    print(f"KẾT QUẢ: {ok} đạt / {fail} hỏng")
    if FAILS:
        for f in FAILS:
            print("  · " + f)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
