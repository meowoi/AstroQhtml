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

        # ══════════════ [1] Dashboard — MOD-05 Phong Nghien Cuu ══════════════
        print("\n[1] dashboard.html — the MOD-05")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        seed(ctx)
        pg = ctx.new_page(); errs = errors(pg)
        pg.goto(f"{BASE}/dashboard.html", wait_until="domcontentloaded")
        pg.wait_for_selector(".card--lab", timeout=8000)

        badge = pg.locator("#lab-badge")
        check("Co huy hieu khoa tren the", badge.count() == 1)
        check("Huy hieu la SAP RA MAT, KHONG phai TRA PHI",
              "SẮP RA MẮT" in badge.inner_text(), badge.inner_text().strip())
        check("Huy hieu mang class `soon` (ho phach), khong phai `pro`",
              "soon" in (badge.get_attribute("class") or ""))
        # ⚠️ Huy hieu phai KHOP trang thai khai trong js/locks.js. Bam theo hang so
        #    "soon" thoi la phep kiem van xanh khi ai do bat co sang `pro` ma quen
        #    sua cho ve huy hieu — do dung cai lo ra o phep thu pha hoai.
        st = pg.evaluate("AstroQLocks.state('lab')")
        check("Class huy hieu KHOP state khai trong locks.js",
              st in (badge.get_attribute("class") or ""), f"state={st}")

        btn = pg.locator("#lab-btn")
        check("Nut BAM DUOC (khong con disabled)", not btn.is_disabled())
        # Vung cham: 48px la san du an da chot, 44 la muc toi thieu WCAG
        bb = btn.bounding_box()
        check("Vung cham nut >= 44px", bb and bb["height"] >= 44, f'{bb["height"]:.0f}px' if bb else "?")

        open_modal(pg, "#lab-btn")
        title = pg.inner_text("#lk-title")
        body = pg.inner_text("#lk-body")
        check("Modal mo ra", pg.locator("#aq-lock.show").count() == 1)
        check("Tieu de noi DANG XAY, khong noi 'da khoa vi chua tra tien'",
              "đang được xây" in title, title)
        check("Than bai nhac ten goi", "Phi Hành Gia" in body, body[:70])
        # ⚠️ Phep kiem quan trong nhat ca bo
        low = (title + " " + body + " " + pg.inner_text("#lk-go")).lower()
        check("KHONG co chu 'mo khoa ngay' / 'mua ngay' / 'nang cap ngay'",
              not any(w in low for w in ["mở khoá ngay", "mở khóa ngay", "mua ngay", "nâng cấp ngay"]),
              low[:80])
        check("Co danh sach quyen loi", pg.locator("#lk-feats li").count() >= 3,
              str(pg.locator("#lk-feats li").count()))
        note = pg.inner_text("#lk-note")
        check("Co cau nho bo me xem giup (khong hoi thuc tre)",
              "bố mẹ" in note, note[:60])
        go = pg.locator("#lk-go")
        check("Nut chinh dan sang pricing.html",
              (go.get_attribute("href") or "").endswith("pricing.html"),
              go.get_attribute("href"))

        # Escape dong + tra tieu diem
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(250)
        check("Escape dong modal", pg.locator("#aq-lock.show").count() == 0)
        check("Tieu diem tra ve dung nut vua bam",
              pg.evaluate("document.activeElement && document.activeElement.id") == "lab-btn")

        # Doi ngon ngu -> huy hieu va modal dich theo
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(350)
        check("Huy hieu dich sang EN", "COMING SOON" in pg.inner_text("#lab-badge"),
              pg.inner_text("#lab-badge").strip())
        open_modal(pg, "#lab-btn")
        check("Modal dich sang EN", "being built" in pg.inner_text("#lk-title"),
              pg.inner_text("#lk-title"))
        pg.keyboard.press("Escape")
        check("0 loi console/pageerror o dashboard", not errs, str(errs[:2]))
        ctx.close()

        # ══════════════ [2] missions.html — MISSION-02 Mat Trang ══════════════
        print("\n[2] missions.html — the MISSION-02")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        seed(ctx)
        pg = ctx.new_page(); errs = errors(pg)
        pg.goto(f"{BASE}/missions.html", wait_until="domcontentloaded")
        pg.wait_for_selector(".mcard.soon", timeout=8000)

        card = pg.locator(".mcard.soon").first
        check("The Mat Trang co huy hieu khoa", card.locator(".lk-badge").count() == 1)
        check("Huy hieu la SAP RA MAT", "SẮP RA MẮT" in card.locator(".lk-badge").inner_text())
        lbl = card.locator(".play-btn").inner_text()
        check("Nhan nut moi bam (khong lap lai 'Sap ra mat')",
              "Vì sao" in lbl, lbl.strip())

        open_modal(pg, ".mcard.soon .play-btn")
        body = pg.inner_text("#lk-body")
        check("Modal nhiem vu mo ra", pg.locator("#aq-lock.show").count() == 1)
        check("Noi dang xay + ten goi", "Phi Hành Gia" in body, body[:70])
        check("Co nut dan sang trang gia", pg.locator("#lk-go").is_visible())
        pg.keyboard.press("Escape")
        check("0 loi console/pageerror o missions", not errs, str(errs[:2]))
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
              pg.locator(".pr-note").is_visible())
        check("Dai nhac 'danh cho bo me' + 'chua mo ban'",
              "bố mẹ" in pg.inner_text(".pr-note") and "chưa mở bán" in pg.inner_text(".pr-note"))

        # ⚠️ GIA DA CHOT 09/08/2026 (docs/decisions/009 -> `da chot`), NHUNG CHOT GIA
        #    va MO BAN la HAI viec. Trang phai bo chu "du kien" MA VAN noi ro chua ban
        #    — chua chon cong thanh toan, va ba dieu kien bat Pha 1 chua dat.
        #    Hai phep kiem nay di doi: bo mot cai la trang hoac noi sai gia, hoac hua
        #    ban mot thu chua ban duoc.
        body_txt = pg.inner_text("body")
        check("KHONG con noi gia la 'du kien'", "dự kiến" not in body_txt)
        check("Dai noi ro gia DA CHOT", "đã chốt" in pg.inner_text(".pr-note"))
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
