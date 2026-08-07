# -*- coding: utf-8 -*-
"""
smoke_geo_lang.py — ĐO THẬT: khách từ đâu thì thấy ngôn ngữ nào.

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/smoke_geo_lang.py

LUẬT ĐANG KIỂM (js/ui-common.js → guessLang):
    ① `astroq-lang` đã lưu   → LUÔN THẮNG
    ② múi giờ Việt Nam       → vi
    ③ ngôn ngữ trình duyệt vi → vi
    ④ còn lại                → en

VÌ SAO PHẢI CHẠY TRÌNH DUYỆT THẬT
---------------------------------
`Intl.DateTimeFormat().resolvedOptions().timeZone` là thứ CHỈ trình duyệt trả
lời được, và Playwright đặt được `timezone_id` + `locale` riêng cho từng
context — tức là mô phỏng được đúng "khách ngồi ở nước nào, máy đặt tiếng gì".
Đọc mã nguồn thì không chứng minh được gì ở đây.

⚠️ ĐO TRÊN TRANG THẬT, KHÔNG GỌI HÀM TRỰC TIẾP. Thứ cần biết là **chữ hiện ra
   trước mắt khách**, nên phép kiểm đọc `<html lang>` + H1 sau khi trang chạy
   xong `applyLang`. Gọi thẳng `AstroQ.guessLang()` thì bỏ sót cả chuỗi
   initLang → setDocLang → applyLang, mà đó mới là chỗ từng hỏng thật
   (`explorer.html` ghi cứng `<html lang="en">` suốt nhiều tháng).

⚠️ Windows: đặt PYTHONIOENCODING=utf-8.
"""

import sys

BASE = "http://127.0.0.1:8123"

# (nhãn, locale, timezone, ngôn ngữ MONG ĐỢI, lý do)
CASES = [
    ("VN · máy tiếng Việt",   "vi-VN", "Asia/Ho_Chi_Minh", "vi", "② múi giờ VN"),
    ("VN · máy tiếng Anh",    "en-US", "Asia/Ho_Chi_Minh", "vi", "② múi giờ VN thắng ngôn ngữ máy"),
    ("VN · bí danh Saigon",   "en-US", "Asia/Saigon",      "vi", "② bí danh múi giờ cũ"),
    ("Mỹ · máy tiếng Anh",    "en-US", "America/New_York", "en", "④ lưới an toàn quốc tế"),
    ("Mỹ · máy tiếng Việt",   "vi-VN", "America/New_York", "vi", "③ người Việt ở nước ngoài"),
    ("Nhật",                  "ja-JP", "Asia/Tokyo",       "en", "④ TRƯỚC ĐÂY RA TIẾNG VIỆT"),
    ("Pháp",                  "fr-FR", "Europe/Paris",     "en", "④ TRƯỚC ĐÂY RA TIẾNG VIỆT"),
    ("Hàn",                   "ko-KR", "Asia/Seoul",       "en", "④ TRƯỚC ĐÂY RA TIẾNG VIỆT"),
    ("Thái (cùng UTC+7!)",    "th-TH", "Asia/Bangkok",     "en", "④ UTC+7 nhưng KHÔNG phải VN"),
]

# ⚠️ TRANG CHỦ KHÔNG CÒN TRONG DANH SÁCH NÀY — đổi 07/08/2026 cùng lượt tách
#    `/` và `/en/`. Trang chủ nay là HAI trang TĨNH, mỗi bản một ngôn ngữ cố
#    định, nên `<html lang>` ở đó KHÔNG đổi theo phán đoán — và KHÔNG ĐƯỢC đổi:
#    đó chính là lỗi "JSON-LD tiếng Việt cạnh nội dung tiếng Anh" vừa sửa xong.
#    Ở trang chủ, phán đoán chỉ còn quyết định DẢI MỜI hiện hay không (mục [6]).
#    Hai trang dưới đây là trang app: `noindex`, một URL một trang, đổi chữ tại
#    chỗ như cũ.
PAGES = ["dashboard.html", "learn.html"]

_ok = _bad = 0


def check(cond, label, extra=""):
    global _ok, _bad
    if cond:
        _ok += 1
        print("  [OK]   %s" % label)
    else:
        _bad += 1
        print("  [HONG] %s %s" % (label, extra))
    return bool(cond)


def read_lang(ctx, page):
    pg = ctx.new_page()
    pg.goto(BASE + "/" + page, wait_until="load", timeout=30000)
    pg.wait_for_timeout(400)
    v = pg.evaluate("""() => ({
        html: document.documentElement.lang,
        guess: (window.AstroQ && AstroQ.guessLang) ? AstroQ.guessLang() : null,
        saved: localStorage.getItem('astroq-lang')
    })""")
    pg.close()
    return v


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Thieu playwright: pip install playwright && playwright install chromium")
        return 2

    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("=" * 70)
        print("  [1] Khach MOI (chua tung bam VI/EN) — 9 to hop x %d trang" % len(PAGES))
        print("=" * 70)
        for label, loc, tz, want, why in CASES:
            ctx = br.new_context(locale=loc, timezone_id=tz)
            got = []
            for p in PAGES:
                v = read_lang(ctx, p)
                got.append(v["html"])
            ctx.close()
            same = len(set(got)) == 1
            check(same and got[0] == want,
                  "%-22s %-6s %-18s -> %s   (%s)" % (label, loc, tz, got[0], why),
                  "mong doi %s, do duoc %s" % (want, got))
            if not same:
                check(False, "  ^ HAI TRANG LECH NHAU", str(dict(zip(PAGES, got))))

        # ------------------------------------------------------------------
        print("\n" + "=" * 70)
        print("  [2] Lua chon da luu PHAI THANG moi phep doan")
        print("=" * 70)
        # Khach Nhat tu bam "Tieng Viet" -> tu do luon thay tieng Viet.
        ctx = br.new_context(locale="ja-JP", timezone_id="Asia/Tokyo")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');}catch(e){}")
        v = read_lang(ctx, "dashboard.html")
        check(v["html"] == "vi",
              "khach Nhat da chon VI -> van la VI (khong bi doan de len)", str(v))
        ctx.close()

        # Nguoc lai: khach o VN tu bam "English".
        ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','en');}catch(e){}")
        v = read_lang(ctx, "dashboard.html")
        check(v["html"] == "en",
              "khach o VN da chon EN -> van la EN (mui gio KHONG de len)", str(v))
        ctx.close()

        # ------------------------------------------------------------------
        print("\n" + "=" * 70)
        print("  [3] Bam nut doi ngon ngu van ghi va van an")
        print("=" * 70)
        # ⚠️ Dung `learn.html`, KHONG dung `dashboard.html`: dashboard chay man
        #    Comet dan tham quan (`.tour-block` phu kin de chan bam ra ngoai),
        #    nen cu bam vao nut VI/EN bi chan va Playwright cho het gio. Do la
        #    hanh vi DUNG cua san pham, khong phai loi — chi la sai cho de do.
        ctx = br.new_context(locale="ja-JP", timezone_id="Asia/Tokyo")
        pg = ctx.new_page()
        pg.goto(BASE + "/learn.html", wait_until="load")
        pg.wait_for_timeout(300)
        before = pg.evaluate("()=>document.documentElement.lang")
        check(before == "en", "khach Nhat vao lan dau -> EN", before)
        pg.click('.lang-switch button[data-lang="vi"]')
        pg.wait_for_timeout(300)
        after = pg.evaluate("()=>document.documentElement.lang")
        saved = pg.evaluate("()=>localStorage.getItem('astroq-lang')")
        check(after == "vi", "bam VI -> doi sang VI ngay", after)
        check(saved == "vi", "ghi vao astroq-lang", str(saved))
        pg.reload(wait_until="load")
        pg.wait_for_timeout(300)
        check(pg.evaluate("()=>document.documentElement.lang") == "vi",
              "F5 van giu VI (khong bi doan lai)")
        pg.close()
        ctx.close()

        # ------------------------------------------------------------------
        print("\n" + "=" * 70)
        print("  [4] Khong co Intl / mui gio la -> phai lui ve ngon ngu may")
        print("=" * 70)
        # ⚠️ ĐỪNG GIẾT HẲN `window.Intl` — bản đầu của phép kiểm này làm thế và
        #    nó VỠ LUÔN `UtilityScript` nội bộ của Playwright, tức bộ đo tự
        #    giết mình rồi báo "sản phẩm hỏng". Chỉ bỏ đúng trường `timeZone`:
        #    đó chính là nhánh `if(tz && …)` cần thử, mà không đụng gì khác.
        #    (Nhánh resolvedOptions NÉM LỖI thì đã có try/catch trong sản phẩm
        #    bọc sẵn; thử nó ở đây cũng lại làm vỡ Playwright.)
        ctx = br.new_context(locale="vi-VN", timezone_id="America/New_York")
        ctx.add_init_script("""
            try{
              var orig = Intl.DateTimeFormat.prototype.resolvedOptions;
              Intl.DateTimeFormat.prototype.resolvedOptions = function(){
                var o = orig.call(this); delete o.timeZone; return o;
              };
            }catch(e){}
        """)
        err = []
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: err.append(str(e)))
        pg.goto(BASE + "/dashboard.html", wait_until="load")
        pg.wait_for_timeout(400)
        check(pg.evaluate("()=>document.documentElement.lang") == "vi",
              "khong doc duoc mui gio + may tieng Viet -> van ra VI (buoc ③ do)")
        check(not err, "khong doc duoc mui gio KHONG lam vo trang", str(err[:2]))
        pg.close()
        ctx.close()

        # ------------------------------------------------------------------
        print("\n" + "=" * 70)
        print("  [5] CHUA CHON thi KHONG trang nao duoc ghi astroq-lang")
        print("=" * 70)
        # ⚠️ LOI THAT DA SUA 07/08/2026: `landing-app.html` goi AstroQ.setLang()
        #    ngay TRONG applyLang, nen no GHI PHAN DOAN vao localStorage o luot
        #    tai dau — tuc dong bang mot lua chon nguoi dung chua he dua ra.
        #    17 trang kia khong ghi, nen cung mot khach bi doi xu khac nhau tuy
        #    trang ho dap xuong; va may dat sai gio / dang bat VPN luc vao lan
        #    dau thi sua xong van khong doi duoc (bac ① luon thang).
        #    Phep kiem nay giu cho no khong quay lai o bat ky trang nao.
        for page in ["landing-app.html", "dashboard.html", "learn.html"]:
            ctx = br.new_context(locale="ja-JP", timezone_id="Asia/Tokyo")
            v = read_lang(ctx, page)
            check(v["saved"] is None,
                  "%-20s chua chon -> KHONG ghi astroq-lang" % page, str(v["saved"]))
            ctx.close()

        # ------------------------------------------------------------------
        print("\n" + "=" * 70)
        print("  [6] TRANG CHU: ngon ngu do URL, phan doan chi quyet DAI MOI")
        print("=" * 70)
        # `/` luon tieng Viet, `/en/` luon tieng Anh — bat ke khach ngoi o dau.
        # Do la dieu kien de JSON-LD / canonical / og: cua tung trang khop noi
        # dung cua chinh no (loi cu: chu doi sang tieng Anh ma JSON-LD van tieng
        # Viet, tren dung trang DUY NHAT duoc lap chi muc).
        # Phan doan chi con MOT viec o day: co moi khach sang ban kia hay khong.
        VIET = "àáâãèéêìíòóôõùúýăđơưạảấầậắằẻẽếềểệỉịọỏốồổộớờởợụủứừửữựỳỵỷỹ"
        for url, loc, tz, other, want_note in [
            ("/",    "ja-JP", "Asia/Tokyo",       "en", True),   # khach Nhat tren ban VI -> moi
            ("/",    "vi-VN", "Asia/Ho_Chi_Minh", None, False),  # dung ban roi -> khong moi
            ("/en/", "vi-VN", "Asia/Ho_Chi_Minh", "vi", True),   # khach Viet tren ban EN -> moi
            ("/en/", "en-US", "America/New_York", None, False),  # dung ban roi -> khong moi
        ]:
            ctx = br.new_context(locale=loc, timezone_id=tz)
            pg = ctx.new_page()
            pg.goto(BASE + url, wait_until="load", timeout=30000)
            pg.wait_for_timeout(1900)          # dai moi hien sau 1200ms
            v = pg.evaluate("""() => {
              const b = document.getElementById('lang-note');
              const shown = !!b && !b.hidden;
              return {lang: document.documentElement.lang, shown: shown,
                      href: shown ? document.getElementById('ln-go').getAttribute('href') : null,
                      txt:  shown ? document.getElementById('ln-txt').textContent : null};
            }""")
            fixed = "en" if url == "/en/" else "vi"
            check(v["lang"] == fixed,
                  "%-5s may %-6s -> <html lang>=%s CO DINH theo URL" % (url, loc, fixed), str(v))
            check(v["shown"] == want_note,
                  "%-5s may %-6s -> dai moi: %s" % (url, loc, "CO" if want_note else "KHONG"), str(v))
            if want_note:
                dest = "/en/" if fixed == "vi" else "/"
                check(v["href"] == dest, "      ^ dai moi tro sang %s" % dest, str(v["href"]))
                # ⚠️ Chu trong dai phai la NGON NGU KIA. Moi mot nguoi Nhat sang
                #    ban tieng Anh bang mot cau tieng Viet thi dai vo dung dung
                #    voi nguoi no sinh ra de phuc vu.
                has_viet = any(c in VIET for c in (v["txt"] or "").lower())
                check(has_viet == (other == "vi"),
                      "      ^ chu trong dai viet bang ngon ngu KIA (%s)" % other, repr(v["txt"]))
            pg.close(); ctx.close()

        br.close()

    print("\n" + "-" * 70)
    print("  KET QUA: %d dat / %d hong" % (_ok, _bad))
    print("-" * 70)
    return 1 if _bad else 0


if __name__ == "__main__":
    sys.exit(main())
