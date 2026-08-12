# -*- coding: utf-8 -*-
"""
smoke_locks.py — do THAT tren Chromium: huy hieu khoa + modal "vi sao khoa" +
trang Goi & Uu dai (pricing.html).

    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/smoke_locks.py

Trong tam — thu de lam hong niem tin nhat:
  1. KHONG duoc gan nhan "TRA PHI" cho thu CHUA CO NOI DUNG. Phong Nghien Cuu va
     Nhiem vu Mat Trang deu chua dung xong -> huy hieu phai la "SAP RA MAT", va
     modal TUYET DOI khong duoc co nut "Mo khoa ngay".
  2. Ba mini-game chua dung se MIEN PHI khi ra mat -> modal cua chung khong duoc
     co bat ky loi moi mua nao.
  3. Trang gia phai noi ro muc nao DA CO, muc nao DANG PHAT TRIEN.

⚠️ Nhan cua check() PHAI KHONG DAU — console Windows mac dinh cp1252.
"""
import re
import sys

from playwright.sync_api import sync_playwright

# ⚠️ BAT BUOC — console Windows mac dinh cp1252. Nhan cua check() deu khong dau,
#    NHUNG phan `detail` la chu lay tu chinh trang (vd "SAP RA MAT" co dau), nen
#    in ra la UnicodeEncodeError nem GIUA LUC CHAY va bo do moi phep kiem phia sau.
#    Da tung mat mot luot thu pha hoai vi dung chuyen nay: bo do chet sau 1 phep
#    kiem, dem ra "0 hong" va trong y het nhu san pham dung.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123").rstrip("/")
ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def seed(ctx):
    """Ho so trong may — de dashboard khong day sang luong onboarding."""
    ctx.add_init_script("""
      localStorage.setItem('astroq-user', JSON.stringify(
        {name:'Test', pilotName:'Test', uid:'u-test', character:'m', avatar:'ava/avam.png'}));
      localStorage.setItem('astroq-lang','vi');
      localStorage.setItem('astroq-tour-seen','1');
      localStorage.setItem('astroq-map01-seen','1');
      localStorage.setItem('astroq-mission01-intro-seen','1');
    """)


def errors(page):
    bag = []
    page.on("pageerror", lambda e: bag.append(str(e)))       # ngoai le chua bat
    page.on("console", lambda m: bag.append(m.text) if m.type == "error" else None)
    return bag


def open_modal(page, sel):
    page.click(sel)
    page.wait_for_selector("#aq-lock.show", timeout=6000)
    return page


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ══════════════ [1] lab.html — THE hoat dong bi khoa ══════════════
        # ⚠️⚠️ DOI DICH 12/08/2026: truoc day muc nay do card MOD-05 o dashboard.
        #    MOD-05 nay DA MO KHOA (lab.html co that) nen khoa chuyen xuong TUNG THE
        #    ben trong lab. Moi phep kiem duoi day giu nguyen DIEU CAN BAO VE, chi
        #    doi cho do — va nhan them bien the MOI: `pro` KHI CHUA MO BAN.
        print("\n[1] lab.html — the hoat dong bi khoa")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        seed(ctx)
        pg = ctx.new_page(); errs = errors(pg)
        # ⚠️ Chan /billing/catalog: cong 8123 khong nam trong ALLOWED_ORIGINS nen
        #    CORS chan va TRINH DUYET tu ghi mot dong do vao console. Chan o bo do
        #    thi phep do thoi phu thuoc vao viec Lambda co song hay khong.
        ctx.route("**/billing/catalog", lambda r: r.fulfill(
                status=200, content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"},
                body='{"ok":true,"saleOpen":false,"provider":"none"}'))
        pg.goto(f"{BASE}/lab.html", wait_until="domcontentloaded")
        pg.wait_for_selector(".lcard", timeout=8000)

        badge = pg.locator(".lcard[data-card='float'] .lc-tag")
        check("Co nhan trang thai tren the bi khoa", badge.count() == 1)
        check("Nhan noi thu nay THUOC GOI nao (khong phai 'sap ra mat')",
              "PHI HÀNH GIA" in badge.inner_text().upper(), badge.inner_text().strip())
        check("Nhan mang class `pro`, khong phai `soon`",
              "pro" in (badge.get_attribute("class") or ""))
        # ⚠️ Nhan phai KHOP trang thai khai trong js/locks.js — bam theo hang so thoi
        #    la phep kiem van xanh khi ai do doi state ma quen sua cho ve nhan.
        st = pg.evaluate("AstroQLocks.state('lab:float')")
        check("Class nhan KHOP state khai trong locks.js",
              st in (badge.get_attribute("class") or ""), f"state={st}")
        # Va mot the CHUA DUNG XONG phai mang nhan KHAC — hai loai, hai cach noi.
        check("The chua dung xong mang nhan `soon`",
              "soon" in (pg.locator(".lcard[data-card='mix'] .lc-tag")
                           .get_attribute("class") or ""))

        btn = pg.locator(".lcard[data-card='float']")
        check("The BAM DUOC (khong disabled)", not btn.is_disabled())
        bb = btn.bounding_box()
        check("Vung cham the >= 44px", bb and bb["height"] >= 44,
              f'{bb["height"]:.0f}px' if bb else "?")

        open_modal(pg, ".lcard[data-card='float']")
        title = pg.inner_text("#lk-title")
        body = pg.inner_text("#lk-body")
        check("Modal mo ra", pg.locator("#aq-lock.show").count() == 1)
        # ⚠️ So bang casefold(): tieu de co the mo dau bang cum nay (chu HOA) hoac
        #    dat no giua cau. Ghim dung mot cach viet hoa la phep kiem bao hong oan
        #    ngay lan doi cau chu dau tien — du an da tra gia BA lan vi loai loi nay
        #    (xem quy tac 8 muc 6 cua CLAUDE.md).
        # ⚠️ DOI PHAT BIEU 12/08/2026: bien the "chua mo ban" da bo (chu du an chot coi
        #    nhu da mo ban). Dieu can bao ve van nguyen: hop khoa noi that thu nay
        #    thuoc goi nao, va KHONG noi kieu "khoa vi chua tra tien".
        check("Tieu de KHONG noi 'da khoa vi chua tra tien'",
              "chưa trả" not in title.casefold(), title)
        check("Tieu de noi ro thuoc goi nao", "Phi Hành Gia" in title, title)
        check("Than bai KHONG con noi 'chua mo ban'",
              "chưa mở bán" not in body.casefold(), body[:80])
        check("Than bai KHONG noi 'dang duoc xay' (thu nay DA lam xong)",
              "đang được xây" not in body.casefold(), body[:80])
        check("Than bai nhac ten goi", "Phi Hành Gia" in body, body[:70])
        # ⚠️ Phep kiem quan trong nhat ca bo
        low = (title + " " + body + " " + pg.inner_text("#lk-go")).lower()
        check("KHONG co chu 'mo khoa ngay' / 'mua ngay' / 'nang cap ngay'",
              not any(w in low for w in ["mở khoá ngay", "mở khóa ngay", "mua ngay", "nâng cấp ngay"]),
              low[:80])
        check("Co danh sach quyen loi", pg.locator("#lk-feats li").count() >= 3,
              str(pg.locator("#lk-feats li").count()))
        # ⚠️ The tra phi phai co MOT DUONG DI THAT: nut dan sang pricing.html. Mot hop
        #    khoa khong co duong ra nao la mot ngo cut — te hon ca mot nut `disabled`.
        go = pg.locator("#lk-go")
        check("CO nut dan sang trang gia", go.is_visible())
        check("nut do tro dung pricing.html",
              (go.get_attribute("href") or "").endswith("pricing.html"),
              go.get_attribute("href"))
        check("Co cau nho bo me xem giup (khong hoi thuc tre)",
              "bố mẹ" in pg.inner_text("#lk-note"), pg.inner_text("#lk-note")[:60])

        # Escape dong + tra tieu diem
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(250)
        check("Escape dong modal", pg.locator("#aq-lock.show").count() == 0)
        check("Tieu diem tra ve dung the vua bam",
              pg.evaluate("""document.activeElement
                             && document.activeElement.getAttribute('data-card')""") == "float")

        # Doi ngon ngu -> nhan va modal dich theo
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(350)
        check("Nhan the dich sang EN",
              "ASTRONAUT" in pg.inner_text(".lcard[data-card='float'] .lc-tag").upper(),
              pg.inner_text(".lcard[data-card='float'] .lc-tag").strip())
        open_modal(pg, ".lcard[data-card='float']")
        check("Modal dich sang EN", "plan" in pg.inner_text("#lk-body").casefold(),
              pg.inner_text("#lk-body")[:70])
        pg.keyboard.press("Escape")
        check("0 loi console/pageerror o lab.html", not errs, str(errs[:2]))
        ctx.close()

        # ══════════════ [2] mission-map.html — diem den Mat Trang ══════════════
        # ⚠️ DOI CHO 12/08/2026 (`docs/decisions/008`): Mat Trang khong con la mot THE
        #    o `missions.html` ma la mot DIEM DEN tren ban do nhiem vu. Dieu muc nay
        #    bao ve KHONG doi: noi "sap ra mat" phai NOI RO no dang duoc xay va thuoc
        #    goi nao, bang dung mot cai hop (`js/locks.js`) ma dashboard va Khu Huan
        #    Luyen dang dung — mot cau tra loi, mot kieu hop.
        #    ⚠️ Phai gieo tien do DU CONG (5/7 chang) thi Mat Trang moi la "sap co";
        #       chua du thi no la "chua mo duong toi", mot cau tra loi KHAC.
        print("\n[2] mission-map.html — diem den Mat Trang")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        seed(ctx)
        pg = ctx.new_page(); errs = errors(pg)
        pg.add_init_script("""
          localStorage.setItem('astroq-route-gate', JSON.stringify({
            open:['earth','moon'], route:['earth','moon'],
            gate:5, done:5, total:7 }));
        """)
        pg.goto(f"{BASE}/mission-map.html", wait_until="domcontentloaded")
        pg.wait_for_selector('.body[data-id="moon"].soon', timeout=8000)

        moon = pg.locator('.body[data-id="moon"]')
        check("Mat Trang o trang thai 'sap co nhiem vu'",
              "soon" in (moon.get_attribute("class") or ""))
        st = moon.locator(".st").inner_text()
        # ⚠️ SO BANG casefold(): `.body .st` co `text-transform:uppercase` nen
        #    `inner_text()` tra ve "SẮP CÓ". Day la LAN THU NAM du an mac dung loi
        #    "ghim mot cach viet hoa" (quy tac 8 muc 6 CLAUDE.md) — moi phep kiem dang
        #    "chu nay phai co mat" deu phai case-fold truoc.
        check("Nhan trang thai noi 'sap co'", "sắp có" in st.casefold(), st.strip())

        open_modal(pg, '.body[data-id="moon"]')
        body = pg.inner_text("#lk-body")
        check("Modal nhiem vu mo ra", pg.locator("#aq-lock.show").count() == 1)
        check("Noi dang xay + ten goi", "Phi Hành Gia" in body, body[:70])
        check("Co nut dan sang trang gia", pg.locator("#lk-go").is_visible())
        check("KHONG mo them bang thu hai", pg.locator("#sheet[hidden]").count() == 1)
        pg.keyboard.press("Escape")
        check("0 loi console/pageerror o ban do", not errs, str(errs[:2]))
        ctx.close()

        # ══════════════ [3] games.html — tro MIEN PHI sap ra mat ══════════════
        print("\n[3] games.html — 3 tro sap ra mat (se MIEN PHI)")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        seed(ctx)
        pg = ctx.new_page(); errs = errors(pg)
        pg.goto(f"{BASE}/games.html", wait_until="domcontentloaded")
        pg.wait_for_selector(".gcard.soon", timeout=8000)

        check("Co 3 the game sap ra mat", pg.locator(".gcard.soon").count() == 3,
              str(pg.locator(".gcard.soon").count()))
        open_modal(pg, ".gcard.soon .play-btn")
        body = pg.inner_text("#lk-body")
        check("Modal noi SE MIEN PHI", "không mất phí" in body, body[:80])
        # ⚠️ Day la cho de sai nhat: nhet loi moi mua vao mot thu se mien phi
        check("KHONG co nut dan sang trang gia", not pg.locator("#lk-go").is_visible())
        check("KHONG co ghi chu ve tien", not pg.locator("#lk-note").is_visible())
        check("KHONG co danh sach quyen loi goi", not pg.locator("#lk-feats").is_visible())
        pg.keyboard.press("Escape")
        check("0 loi console/pageerror o games", not errs, str(errs[:2]))
        ctx.close()

        # ══════════════ [4] pricing.html ══════════════
        print("\n[4] pricing.html — Goi & Uu dai")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        seed(ctx)
        pg = ctx.new_page(); errs = errors(pg)
        # ⚠️ CHAN /billing/catalog VA TRA PHAN HOI CO DINH — cung viec ma
        #    `audit_viewports.py` va `smoke_lang_switch.py` da lam tu 11/08/2026.
        #    `pricing.html` hoi route CONG KHAI do ngay khi mo trang, ma bo do chay o
        #    cong 8123 — khong nam trong ALLOWED_ORIGINS — nen loi goi bi CORS chan va
        #    TRINH DUYET TU ghi mot dong do vao console; khong `catch` nao chan duoc,
        #    va phep kiem "0 loi console" bao hong OAN.
        #    ⚠️ Co y KHONG them 8123 vao ALLOWED_ORIGINS: do la cong cua bo kiem thu,
        #       mo them mot origin tren API THAT chi de lam xanh mot phep kiem la doi
        #       cau hinh san xuat vi mot ly do khong thuoc san xuat.
        pg.route("**/billing/catalog*", lambda r: r.fulfill(
            status=200, content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body='{"ok":true,"saleOpen":false,"provider":"none","currency":"VND",'
                 '"trialDays":14,"graceDays":7,"offers":['
                 '{"plan":"astro","cycle":"month","currency":"VND","amount":99000},'
                 '{"plan":"astro","cycle":"year","currency":"VND","amount":790000},'
                 '{"plan":"crew","cycle":"month","currency":"VND","amount":169000},'
                 '{"plan":"crew","cycle":"year","currency":"VND","amount":1290000},'
                 '{"plan":"found","cycle":"once","currency":"VND","amount":1490000}]}'))
        pg.goto(f"{BASE}/pricing.html", wait_until="domcontentloaded")
        pg.wait_for_selector(".plan", timeout=8000)

        check("Ve du 4 goi", pg.locator(".plan").count() == 4,
              str(pg.locator(".plan").count()))
        txt = pg.inner_text("#plans")
        check("Gia VND dung bang 009 (99.000 / 790.000)",
              "99.000₫" in txt and "790.000₫" in txt)
        check("Gia goi 4 tre (169.000 / 1.290.000)",
              "169.000₫" in txt and "1.290.000₫" in txt)
        check("Ve Sang Lap 1.490.000₫", "1.490.000₫" in txt)
        check("Co tinh % giam gia goi nam", "%" in txt, "")

        # ⚠️ Chua chot cong thanh toan -> khong duoc co nut mua
        hrefs = pg.eval_on_selector_all(".p-cta", "els=>els.map(e=>e.getAttribute('href'))")
        check("KHONG nut goi nao dan toi thanh toan",
              all(h in (None, "/") for h in hrefs), str(hrefs))

        # Bang so sanh: phai noi ro muc nao dang phat trien
        check("Bang so sanh co du 12 dong", pg.locator(".cmp-row").count() == 12,
              str(pg.locator(".cmp-row").count()))
        check("Co nhan 'dang phat trien'", pg.locator(".st.soon").count() >= 6,
              str(pg.locator(".st.soon").count()))
        check("Co nhan 'da co'", pg.locator(".st.have").count() >= 6,
              str(pg.locator(".st.have").count()))

        check("Co cot 'Con nhan duoc' va 'Bo me nhan duoc'",
              pg.locator(".who-col").count() == 2)
        check("Co 8 uu dai", pg.locator(".perk").count() == 8,
              str(pg.locator(".perk").count()))
        check("Co 5 cau hoi dap", pg.locator(".fq").count() == 5,
              str(pg.locator(".fq").count()))
        # ⚠️⚠️ ĐO `is_visible()` TRƯỚC, RỒI MỚI ĐO CHỮ. `.banner` cua page-shell.css
        #    khai `display:none` va chi hien khi JS gan `.show` — dai nay quen chot
        #    nen CHUA BAO GIO HIEN RA, ma phep kiem cu van xanh: `innerText` cua
        #    Chrome roi ve `textContent` voi phan tu khong duoc ve. Doc duoc chu
        #    KHONG chung minh nguoi dung nhin thay chu.
        check("Dai nhac PHAI HIEN RA THAT (khong bi display:none)",
              pg.locator("#pr-note-closed").is_visible())
        check("Dai nhac 'danh cho bo me' + 'chua mo ban'",
              "bố mẹ" in pg.inner_text("#pr-note-closed")
              and "chưa mở bán" in pg.inner_text("#pr-note-closed"))

        # ⚠️ GIA DA CHOT 09/08/2026 (docs/decisions/009 -> `da chot`), NHUNG CHOT GIA
        #    va MO BAN la HAI viec. Trang phai bo chu "du kien" MA VAN noi ro chua ban
        #    — chua chon cong thanh toan, va ba dieu kien bat Pha 1 chua dat.
        #    Hai phep kiem nay di doi: bo mot cai la trang hoac noi sai gia, hoac hua
        #    ban mot thu chua ban duoc.
        body_txt = pg.inner_text("body")
        check("KHONG con noi gia la 'du kien'", "dự kiến" not in body_txt)
        check("Dai noi ro gia DA CHOT", "đã chốt" in pg.inner_text("#pr-note-closed"))
        # ⚠️ Dai cua trang thai DA MO BAN phai dang AN o ban that — hai dai cung hien
        #    la hai cau noi nguoc nhau tren cung mot trang.
        check("dai 'da mo ban' dang AN", not pg.locator("#pr-note-open").is_visible())
        check("dai XEM TRUOC dang AN (khong co co)",
              not pg.locator("#pr-preview").is_visible())
        check("VAN noi ro CHUA MO BAN", "chưa mở bán" in body_txt)

        # FAQ mo ra doc duoc
        pg.click(".fq summary")
        pg.wait_for_timeout(200)
        check("Bam FAQ thi mo ra", pg.locator(".fq[open]").count() == 1)

        # Khong con khoa i18n tho lot ra man hinh
        page_txt = pg.inner_text("body")
        raw = re.findall(r"\b(?:cta_[a-z]+|pl_[a-z]+_[nd]|c_[a-z0-9]+|w_[kp][0-9]|q_[a-z]+|st_[a-z]+)\b", page_txt)
        check("Khong lot khoa i18n tho ra man hinh", not raw, str(raw[:5]))

        # Ban EN -> doi sang USD
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(350)
        txt_en = pg.inner_text("#plans")
        check("Ban EN hien USD", "$4.99" in txt_en and "$39.99" in txt_en, "")
        check("Ban EN KHONG con VND", "₫" not in txt_en)
        check("Bang so sanh dich sang EN", "in development" in pg.inner_text("#cmp"))
        en_txt = pg.inner_text("body")
        check("Ban EN: gia la 'final', khong con 'planned prices'",
              "final" in en_txt and "planned price" not in en_txt.lower())
        check("Ban EN: van noi 'not on sale yet'", "not on sale yet" in en_txt)

        # ══════════ pricing.html o trang thai DA MO BAN (co `?sale=1`) ══════════
        # ⚠️ Loi van nay se hien ra o ban that NGAY BAT CO `SALE_OPEN` o server, nen no
        #    phai duoc gac tu bay gio. Khong co phep kiem thi no la loi van khong ai
        #    kiem duoc — dung lo hong da gap voi LAB-02/03.
        print("\n[5b] pricing.html — loi van DA MO BAN (`?sale=1`)")
        pg.goto(f"{BASE}/pricing.html?sale=1", wait_until="domcontentloaded")
        pg.wait_for_selector(".plan", timeout=8000)
        pg.wait_for_timeout(400)
        check("dai 'da mo ban' HIEN", pg.locator("#pr-note-open").is_visible())
        check("dai 'chua mo ban' AN", not pg.locator("#pr-note-closed").is_visible())
        # ⚠️ Dai XEM TRUOC phai THAY DUOC: mot trang thai khac ban that ma khong noi ra
        #    thi chinh nguoi xem se ket luan sai ve san pham.
        check("dai XEM TRUOC hien ra", pg.locator("#pr-preview").is_visible())
        _open_note = pg.inner_text("#pr-note-open")
        check("noi ro THE do CONG THANH TOAN giu (astroQ khong luu so the)",
              "cổng thanh toán" in _open_note and "không lưu" in _open_note,
              _open_note[:80])
        # Nut cua tung goi phai dan sang checkout kem GOI + CHU KY
        _ctas = pg.eval_on_selector_all(
            ".p-cta", "els => els.map(e => e.getAttribute('href') || '')")
        _buy = [h for h in _ctas if "checkout.html" in h]
        check("moi goi tra phi dan sang checkout.html kem plan + cycle",
              len(_buy) >= 3 and all("plan=" in h and "cycle=" in h for h in _buy),
              " | ".join(_buy))
        # ⚠️ Goi mien phi KHONG duoc co nut mua — khong co gi de mua.
        check("goi mien phi khong dan sang checkout",
              not any("plan=free" in h for h in _ctas), " | ".join(_ctas))
        check("nut CTA duoi trang doi CA CHU LAN DICH",
              pg.eval_on_selector("#cta-btn", "e => e.getAttribute('href')") == "#plans"
              and "gói" in pg.inner_text("#cta-btn").casefold(),
              pg.inner_text("#cta-btn"))
        # ⚠️ Van la trang cho BO ME, nen van khong duoc hoi thuc kieu "mua ngay".
        _pl = pg.inner_text("body").casefold()
        check("KHONG hoi thuc 'mua ngay' / 'chi con hom nay'",
              "mua ngay" not in _pl and "chỉ còn hôm nay" not in _pl)
        pg.goto(f"{BASE}/pricing.html?sale=0", wait_until="domcontentloaded")
        pg.wait_for_timeout(400)
        check("`?sale=0` tra lai loi van chua-mo-ban",
              pg.locator("#pr-note-closed").is_visible()
              and not pg.locator("#pr-note-open").is_visible())

        # Dien thoai
        ctx2 = br.new_context(viewport={"width": 390, "height": 844})
        seed(ctx2)
        pg2 = ctx2.new_page()
        pg2.goto(f"{BASE}/pricing.html", wait_until="domcontentloaded")
        pg2.wait_for_selector(".plan", timeout=8000)
        ow = pg2.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check("Dien thoai 390px: khong tran ngang", ow <= 0, f"tran {ow}px")
        ctx2.close()

        check("0 loi console/pageerror o pricing", not errs, str(errs[:2]))
        ctx.close()
        br.close()

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
