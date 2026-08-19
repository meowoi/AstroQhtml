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
        head("[1] missions.html — cua truoc, khong con luoi the nhiem vu")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector("#ov .cell", timeout=15000)

        # ⚠️ DOI PHAT BIEU 12/08/2026 (`docs/decisions/008`). Truoc do muc nay soi mot
        #    LUOI THE NHIEM VU (`.mcard`) va doi dung 2 the (earth + moon). Luoi do da
        #    chuyen xuong dung tang cua no (`mission-planet.html`), con trang nay thanh
        #    CUA TRUOC dan sang ban do. Giu luoi o day nua la HAI DUONG VAO cho cung
        #    mot nhiem vu — dung loi da tra gia o So Tay Thuat Ngu (04/08/2026).
        #    Luong 4 tang co bo rieng: `scratchpad/smoke_mission_flow.py`.
        chk(pg.locator(".mcard").count() == 0,
            "KHONG con luoi the nhiem vu (mot duong vao, khong hai)")
        chk(pg.locator('a[href="mission-map.html"]').count() == 1,
            "co dung MOT duong sang ban do nhiem vu")

        # ── CHUA DANG NHAP: phai hien dau "—", khong hien so 0 ──
        pg.wait_for_selector("#offline.show", timeout=15000)
        banner = pg.eval_on_selector("#offline-msg", "e => e.textContent")
        chk("—" in banner, "dai nhac noi ro dang hien dau gach ngang", banner[:60])
        ov = pg.eval_on_selector_all("#ov .cell .v", "es => es.map(e => e.textContent.trim())")
        chk(len(ov) == 3, "bang dieu phoi co 3 o", str(ov))
        chk(all(v == "—" for v in ov),
            "chua dang nhap: ca 3 o hien dau '—', KHONG hien 0", str(ov))
        chk(pg.locator("#resume[hidden]").count() == 1,
            "chua biet tien do thi AN dong 'Choi tiep'")
        chk(len(errs) == 0, "missions.html: 0 loi console", "; ".join(errs[:3]))

        # ── Bam the lon -> ban do ──
        pg.click('a[href="mission-map.html"]')
        pg.wait_for_url("**/mission-map.html", timeout=15000)
        chk(pg.url.endswith("mission-map.html"), "the lon dan sang ban do", pg.url)
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[2] missions.html — tieng Anh")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs2 = newpage(ctx, "en")
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector("#ov .cell", timeout=15000)
        chk(pg.evaluate("document.documentElement.lang") == "en", "the html lang=en")
        h1 = pg.eval_on_selector("h1", "e => e.textContent")
        chk(not any(c in h1 for c in "ệộứạảầ"), "tieu de dich sang tieng Anh", h1)
        back = pg.eval_on_selector("#back", "e => e.textContent")
        chk("Navigation Hub" in back, "nut quay lai: 'Back to Navigation Hub'", back.strip())
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
        # "Trạm Tri Thức" — tên chốt lại ngày 31/07/2026 (trước đó là "Tri Thức"
        # trơn). Phép kiểm này từng đòi tên CŨ nên nó báo hỏng đúng lúc trang đã
        # sửa đúng — cùng loại lỗi "bộ kiểm bảo vệ trạng thái cũ" đã ghi ở nút
        # Mặt Trăng. So khớp CHÍNH XÁC cả chữ "Trạm" để đổi tên nửa vời cũng bị bắt.
        # "Sổ Tay Thuật Ngữ" thay "Thư Viện Thiên Văn" ở MOD-06 (04/08/2026) — khu
        # cũ chưa có trang, khu mới thì codex.html đã chạy thật.
        for want in ("Trung Tâm Nhiệm Vụ", "Trạm Tri Thức", "Khu Huấn Luyện",
                     "Bản Đồ Thiên Hà", "Phòng Nghiên Cứu", "Sổ Tay Thuật Ngữ"):
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
        # ⚠️ DOI PHAT BIEU 12/08/2026: tu 04/08 chi con MOT card khoa (Phong Nghien
        #    Cuu), va tu 12/08 thi con SO KHONG — MOD-05 da co trang that (lab.html).
        #    Con so 1 cu bao hong dung luc san pham lam dung. Dieu can bao ve doi
        #    thanh mot cau manh hon: MOI card MOD phai dan sang mot trang CO THAT,
        #    tuc khong card nao la ngo cut. `check_pages` muc [7b] doi chieu tren dia.
        soons = [h for h in hud if h["soon"]]
        # ⚠️⚠️ DOI PHAT BIEU 19/08/2026 — chu du an chot khoa lai Phong Nghien Cuu,
        #    nen con so 0 khang dinh dung trang thai CU. Dieu can bao ve khong doi
        #    (*dashboard noi that ve khu nao chua vao duoc*), chi doi con so; va no
        #    van CO RANG theo hai chieu nho `check_pages` [7b] doi chieu tren dia.
        chk(len(soons) == 1, "dung 1 card 'Sap ra mat' (Phong Nghien Cuu)",
            str([h["name"] for h in soons]))
        # ⚠️ KHONG them mot phep kiem "moi card co duong di" o day: ban dau toi viet
        #    `chk(... or True, ...)` — mot TAUTOLOGY khong bao gio do duoc, tuc mot
        #    phep kiem DAT MOT CACH RONG. Viec do da co cho lam that: `check_pages`
        #    muc [7b] doi chieu TUNG dich voi file tren dia.
        # ⚠️ DOI PHAT BIEU 09/08/2026 — nguyen tac KHONG bi noi long.
        #    Luat cu: "nut bam duoc thi phai co gi do xay ra", nen nut cua khu chua
        #    co trang phai `disabled`. Nay nut do MO MODAL noi vi sao khoa + khi mo
        #    se duoc gi, tuc co xay ra that; con `disabled` moi la ngo cut (tre bam
        #    khong an va chi tuong minh bam truot). Phep kiem nay giau HON ban cu:
        #    no doi nut phai bam duoc VA phai that su mo duoc modal.
        chk(not any(h["disabled"] for h in soons),
            "card 'Sap ra mat': nut BAM DUOC (khong con disabled)")
        # ⚠️⚠️ DOI PHAT BIEU 12/08/2026: MOD-05 DA MO KHOA (lab.html co that), nen ba
        #    phep kiem cu ("bam nut mo modal" · "modal noi dang xay" · "the co huy hieu
        #    khoa") khang dinh dung trang thai CU. Dieu can bao ve doi thanh: nut do
        #    phai dan sang MOT TRANG CO THAT, khong phai vao ngo cut.
        #    Khoa nay chuyen xuong tung THE trong lab.html — smoke_lab.py va
        #    smoke_locks.py muc [1] do phan do.
        # ⚠️⚠️ DOI PHAT BIEU 19/08/2026 — MOD-05 KHOA LAI. Ba phep kiem cu ("dan sang
        #    lab.html" · "khong con soon" · "khong con huy hieu") khang dinh dung
        #    trang thai CU. Ban moi do THU MANH HON ban 12/08: nut phai that su MO
        #    DUOC MODAL (khong phai chi "bam duoc"), va huy hieu phai CO CHU — mot
        #    huy hieu rong nam tren the la chinh cai loi 12/08 da phai go bo.
        chk(pg.locator(".card--lab.soon").count() == 1,
            "card MOD-05 o trang thai 'soon'")
        badge = pg.locator("#lab-badge")
        chk(badge.count() == 1, "card MOD-05 co huy hieu khoa")
        chk((badge.inner_text() or "").strip() != "",
            "huy hieu khoa CO CHU (khong dung rong)", repr(badge.inner_text()))
        pg.click(".card--lab .jelly-btn")
        pg.wait_for_selector(".lk-card", timeout=8000)
        chk(pg.locator(".lk-card").is_visible(), "bam MOD-05 thi MO MODAL giai thich")
        # Khu chua dung xong thi KHONG mo mua ban: modal cua no khong co nut dan sang
        # trang gia (`plan` cua muc `lab` la "astronaut" nen co, nhung `SALE_OPEN`
        # dang tat -> bien the loi van thu tu; chi doi modal noi ro dang duoc xay).
        mtxt = pg.eval_on_selector(".lk-card", "e => e.innerText").lower()
        chk("xây" in mtxt or "dựng" in mtxt or "sắp" in mtxt,
            "modal noi ro khu nay dang duoc xay", mtxt[:70])
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(250)
        # ⚠️ DUA CHUOT RA KHOI NUT truoc khi do bo cuc phia duoi. Cu `pg.click` o tren
        #    de lai con tro DUNG TREN nut, ma `.jelly-btn:hover` co `translateY(-2px)`
        #    — phep do "nut trong cung mot hang thang hang tuyet doi" se doc ra lech
        #    2px va to cao oan san pham. Do mot phan tu DANG HOVER la do mot trang
        #    thai nguoi dung khong o trong luc doc bo cuc.
        pg.mouse.move(2, 2)
        pg.wait_for_timeout(350)          # transform co transition .3s
        # ⚠️ Hai phep kiem duoi day chi co nghia KHI CON card khoa. Dashboard hien
        #    khong con card nao — de nguyen la chung chay tren mot danh sach RONG va
        #    "dat" mot cach rong (all([]) la True, min([]) thi nem loi).
        if soons:
            chk(all(h["href"] is None for h in soons),
                "card 'Sap ra mat' KHONG dan sang trang nao")
            chk(min(h["top"] for h in soons) >= max(h["top"] for h in hud if not h["soon"]),
                "card 'Sap ra mat' nam o hang duoi cung")
        else:
            chk(True, "dashboard 0 card 'Sap ra mat' (moi khu deu co trang that)")
        # MOD-06 la duong vao THAT: co the bam, dan sang codex.html
        codex_card = next((h for h in hud if "Sổ Tay" in h["name"]), None)
        chk(codex_card is not None and codex_card["href"] == "codex.html",
            "card So Tay Thuat Ngu dan sang codex.html",
            str(codex_card and codex_card["href"]))
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
        # ⚠️ Nut VI/EN cua dashboard nam trong menu tha tu 15/08/2026 — phai MO ra
        #    truoc khi bam. Cac trang khac van la day nut trai ngang.
        pg.click('.lang-pick [data-menu-btn]')
        pg.wait_for_selector('.lang-pick [data-menu-pop]:not([hidden])')
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(400)
        en_names = pg.eval_on_selector_all(".cards .hud h3", "es => es.map(e => e.textContent.trim())")
        for want in ("Mission Control", "Knowledge Station", "Training Simulator",
                     "Galaxy Map", "Research Lab", "Terminology Codex"):
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
