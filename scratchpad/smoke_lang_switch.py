# -*- coding: utf-8 -*-
"""
smoke_lang_switch.py — đo NÚT ĐỔI NGÔN NGỮ trên Chromium thật, cho MỌI trang có nó.

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/smoke_lang_switch.py

VÌ SAO CẦN BỘ NÀY, dù `check_pages.py` mục [14] đã canh tĩnh:
  `explorer.html` từng có ĐỦ 3 rule CSS `.lang-btn` và ĐỦ lệnh
  `initLang(applyLanguage, '.lang-btn')` — chỉ thiếu markup. Mục [14] bắt được ca
  đó. Nhưng mục [14] soi văn bản, nên nó KHÔNG chứng minh được bốn điều dưới đây,
  vốn là những gì người dùng thật sự trải nghiệm:
    1. nút có NHÌN THẤY và BẤM ĐƯỢC (không bị lớp khác phủ lên)
    2. bấm vào thì chữ trên trang ĐỔI THẬT
    3. lựa chọn được LƯU và trang khác đọc được
    4. thuộc tính `<html lang>` khớp ngôn ngữ đang hiển thị

⚠️ Nhãn của check() PHẢI KHÔNG DẤU — console Windows mặc định cp1252, in chữ có
   dấu là UnicodeEncodeError ném GIỮA LÚC CHẠY, bỏ dở mọi phép kiểm phía sau.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
USER = {"name": "Bi", "pilotName": "Bi", "character": "raica",
        "avatar": "ava/avaraica.png", "uid": "lang-uid", "selectedCharacter": "raica"}

# Trang · cho de doc chu doi theo ngon ngu · doan chu tieng Viet phai bien mat
# ⚠️ TRANG CHU DUNG LINK, KHONG DUNG NUT — doi 07/08/2026.
#    `/` va `/en/` la HAI URL TINH (xem scratchpad/gen_home_en.py). Nut doi ngon
#    ngu o do phai la <a href> that de Googlebot di duoc sang ban kia — do la nua
#    con lai cua hreflang. Bam vao la DIEU HUONG chu khong doi chu tai cho, va
#    KHONG ghi `astroq-lang` (ngon ngu do URL quyet, khong phai lua chon da luu).
LINK_PAGES = {"index.html", "en/index.html"}

PAGES = [
    ("index.html",         "h1",              None),
    ("select.html",        None,              None),
    ("dashboard.html",     None,              None),
    ("learn.html",         ".htitle",         None),
    ("library.html",       None,              None),
    ("codex.html",         "h1",              None),
    ("quiz.html",          None,              None),
    ("games.html",         "h1",              None),
    ("missions.html",      "h1",              None),
    ("profile.html",       "h1",              None),
    ("achievements.html",  "h1",              None),
    # pricing.html them 09/08/2026 — trang Goi & Uu dai
    ("pricing.html",       "h1",              None),
    # parent.html them 09/08/2026 — bang theo doi cho bo me
    ("parent.html",        "h1",              None),
    # checkout.html them 11/08/2026 — trang thanh toan. Do `h2` chu khong phai `h1`:
    # trang nay khong co h1, tieu de lon nhat la ten buoc dang mo.
    ("checkout.html",      ".co-card:not([hidden]) h2", None),
    ("specimen-vault.html", "h1",             None),
    # shop.html them 12/08/2026 — Kho Trang Tri (buong lai cua con). TEN MON do
    # js/cosmetics.js sinh nen chung phai dich theo, khong chi cac nhan tinh.
    ("shop.html",          "h1",              None),
    ("game-dodge.html",    None,              None),
    ("game-defender.html", None,              None),
    ("game-constellation.html", None,         None),
    # ARCADE-06 them 12/08/2026
    ("game-catch.html",    None,              None),
    ("game-maze.html",     None,              None),
    ("game-racer.html",    None,              None),
    ("explorer.html",      "#deck-title",     None),
    ("mission-earth.html", None,              None),
]

ok_n = bad_n = 0


def check(cond, label, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def seed(ctx, lang="vi"):
    ctx.add_init_script(
        f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
        f"localStorage.setItem('astroq-lang','{lang}');"
        "localStorage.setItem('astroq-asteroids','120');"
        "localStorage.setItem('astroq-tour-seen','1');"
        "localStorage.setItem('astroq-mission01-intro-seen','1');"
        "localStorage.setItem('astroq-mob-note','1');")


with sync_playwright() as p:
    br = p.chromium.launch()
    print(f"=== Do {len(PAGES)} trang: nut VI/EN co that su bam duoc va doi chu? ===")
    for page, title_sel, _ in PAGES:
        ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        seed(ctx, "vi")
        pg = ctx.new_page()
        # ⚠️ CHAN /billing/catalog VA TRA MOT PHAN HOI CO DINH.
        #    `pricing.html` va `checkout.html` hoi route CONG KHAI nay ngay khi mo
        #    trang. Bo do chay o cong 8123 — KHONG nam trong ALLOWED_ORIGINS — nen
        #    loi goi that bi CORS chan va TRINH DUYET TU GHI mot dong do vao
        #    console; khong `catch` nao chan duoc, va phep kiem "0 loi console" bao
        #    hong oan.
        #    ⚠️ CO Y KHONG them 8123 vao ALLOWED_ORIGINS: do la cong cua bo kiem
        #       thu, mo them mot origin tren API THAT chi de lam xanh mot phep kiem
        #       la doi cau hinh san xuat vi mot ly do khong thuoc san xuat.
        #    `saleOpen:false` la trang thai THAT cua hom nay.
        pg.route("**/billing/catalog*", lambda r: r.fulfill(
            status=200, content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body='{"ok":true,"saleOpen":false,"provider":"none","currency":"VND",'
                 '"trialDays":14,"graceDays":7,"offers":[]}'))
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(f"{BASE}/{page}", wait_until="load", timeout=30000)
        pg.wait_for_timeout(1600)
        # explorer co man cho nap voi `transition:visibility .8s`; cho no thuc su
        # bien han thay vi ngu mot khoang co dinh (xem ghi chu o css/explorer.css).
        if page == "explorer.html":
            pg.wait_for_function(
                "()=>{const l=document.getElementById('loader');"
                "return !l || getComputedStyle(l).visibility==='hidden';}",
                timeout=15000)

        # (1) Nut co ton tai, NHIN THAY va la phan tu tren cung tai diem giua no
        info = pg.evaluate("""() => {
          const btns = [...document.querySelectorAll('.lang-switch [data-lang]')];
          if (btns.length < 2) return {n: btns.length};
          const en = btns.find(b => b.dataset.lang === 'en');
          const r = en.getBoundingClientRect();
          const cx = r.x + r.width / 2, cy = r.y + r.height / 2;
          const top = document.elementFromPoint(cx, cy);
          return {n: btns.length, w: Math.round(r.width), h: Math.round(r.height),
                  onTop: en === top || en.contains(top),
                  inView: r.top >= 0 && r.bottom <= innerHeight &&
                          r.left >= 0 && r.right <= innerWidth,
                  activeLang: (btns.find(b => b.classList.contains('active'))
                               || {dataset: {}}).dataset.lang || null,
                  docLang: document.documentElement.lang};
        }""")
        check(info.get("n") == 2, f"{page}: co dung 2 nut VI/EN", json.dumps(info))
        if info.get("n") != 2:
            pg.close(); ctx.close(); continue
        check(info["inView"], f"{page}: nut nam TRONG khung nhin",
              json.dumps(info))
        check(info["onTop"], f"{page}: nut KHONG bi lop khac phu len",
              json.dumps(info))
        check(info["activeLang"] == "vi", f"{page}: nut VI dang sang (dung ngon ngu luu)",
              str(info["activeLang"]))
        check(info["docLang"] == "vi", f"{page}: <html lang> = vi",
              repr(info["docLang"]))

        before = pg.evaluate("() => document.body.innerText")
        t_before = pg.evaluate("(s)=>{const e=s?document.querySelector(s):null;"
                              "return e?e.innerText.trim():null}", title_sel)

        # (2) Bam that vao nut EN
        if page in LINK_PAGES:
            with pg.expect_navigation(wait_until="load"):
                pg.click(".lang-switch [data-lang='en']")
            pg.wait_for_timeout(500)
            check(pg.url.rstrip("/").endswith("/en"),
                  f"{page}: bam EN thi DIEU HUONG sang /en/", pg.url)
        else:
            pg.click(".lang-switch [data-lang='en']")
            pg.wait_for_timeout(900)
        after = pg.evaluate("() => document.body.innerText")
        check(after != before, f"{page}: bam EN thi CHU TREN TRANG doi that")
        if title_sel:
            t_after = pg.evaluate("(s)=>{const e=document.querySelector(s);"
                                  "return e?e.innerText.trim():null}", title_sel)
            check(t_before and t_after and t_before != t_after,
                  f"{page}: tieu de doi theo", f"{t_before!r} -> {t_after!r}")

        st = pg.evaluate("""() => ({
          saved: localStorage.getItem('astroq-lang'),
          docLang: document.documentElement.lang,
          activeLang: ([...document.querySelectorAll('.lang-switch [data-lang]')]
                        .find(b => b.classList.contains('active')) || {dataset:{}}).dataset.lang
        })""")
        if page in LINK_PAGES:
            # Ngon ngu do URL quyet, KHONG do localStorage. Bo do gieo san
            # `astroq-lang='vi'` (xem seed()), nen dieu can chung minh la trang
            # KHONG GHI DE len no khi nguoi dung bam EN — chu khong phai "trong".
            check(st["saved"] == "vi",
                  f"{page}: KHONG ghi de astroq-lang (ngon ngu do URL, khong do localStorage)",
                  str(st["saved"]))
        else:
            check(st["saved"] == "en", f"{page}: luu lai lua chon 'en'", str(st["saved"]))
        check(st["docLang"] == "en", f"{page}: <html lang> doi sang en", repr(st["docLang"]))
        check(st["activeLang"] == "en", f"{page}: nut EN sang len", str(st["activeLang"]))
        check(not errs, f"{page}: 0 loi console", str(errs[:1])[:90])
        pg.close()
        ctx.close()

    # --- Dong bo giua hai TAB (su kien storage) ---
    print("\n=== Doi ngon ngu o tab khac thi trang nay co dich theo? ===")
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    seed(ctx, "vi")
    a = ctx.new_page()
    a.goto(f"{BASE}/explorer.html", wait_until="load", timeout=30000)
    a.wait_for_timeout(2500)
    t1 = a.evaluate("()=>document.querySelector('#deck-title').innerText.trim()")
    b = ctx.new_page()
    b.goto(f"{BASE}/learn.html", wait_until="load", timeout=30000)
    b.wait_for_timeout(1200)
    b.click(".lang-switch [data-lang='en']")
    b.wait_for_timeout(1200)
    a.bring_to_front()
    a.wait_for_timeout(1200)
    t2 = a.evaluate("()=>document.querySelector('#deck-title').innerText.trim()")
    check(t1 != t2, "explorer dich theo khi tab khac doi ngon ngu", f"{t1!r} -> {t2!r}")
    check(a.evaluate("()=>document.documentElement.lang") == "en",
          "explorer: <html lang> cung doi theo tab khac")
    ctx.close()
    br.close()

print(f"\n===== {ok_n} dat / {bad_n} hong =====")
sys.exit(1 if bad_n else 0)
