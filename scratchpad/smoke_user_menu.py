# -*- coding: utf-8 -*-
"""
smoke_user_menu.py — MENU THẢ SAU AVATAR + BỘ CHỌN NGÔN NGỮ, đo trên Chromium thật.

Vì sao cần một bộ riêng: `check_pages` chỉ soi VĂN BẢN (có markup, có khai i18n),
mà cả lượt việc 15/08/2026 đã chứng minh hai lần rằng văn bản không nói được gì về
thứ người dùng thật sự làm được:
  · tấm thả từng neo vào ĐÁY HEADER thay vì đáy màn hình (`backdrop-filter` của
    header biến nó thành khối chứa của con `position:fixed`) — CSS đọc ra hoàn
    toàn hợp lệ, chỉ ảnh chụp mới thấy;
  · tấm thả từng thò ra ngoài mép trái màn 390px (x = −78) vì nó neo mép phải của
    một cái nút không nằm sát mép phải.
Nên bộ này đo BẰNG TOẠ ĐỘ THẬT: mở được không · có nằm trong khung nhìn không ·
có bị lớp khác phủ không · bấm vào có tới đúng trang không.

Chạy:  python -m http.server 8123   (trong AstroQhtml/)
       PYTHONIOENCODING=utf-8 python scratchpad/smoke_user_menu.py

⚠️ Nhãn print KHÔNG DẤU (console Windows cp1252 — quy tắc đã ghi ở CLAUDE.md).
"""
import sys
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/dashboard.html"

# ⚠️ Bản giả `AstroQAuth` KHÔNG gán thẳng `window.AstroQAuth`: module ES thật chạy
#    SAU script thường và sẽ ghi đè. Dùng defineProperty có setter nuốt lời gán —
#    đúng cách các bộ smoke khác của dự án đã làm.
def stub(admin=False):
    return """
localStorage.setItem('astroq-lang','vi');
localStorage.setItem('astroq-asteroids','120');
localStorage.setItem('astroq-user', JSON.stringify({name:'Bi Bo',uid:'u-test',avatar:'ava/avab.png'}));
localStorage.setItem('astroq-tour-seen','1');
localStorage.setItem('astroq-map01-seen','1');
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return {
    idToken:function(){return Promise.resolve(null);},
    getOnboarding:function(){return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,earth1Greeted:true,map01Seen:true});},
    setOnboarding:function(){return Promise.resolve({ok:true});},
    getAchievements:function(){return Promise.resolve({ok:false,reason:'net'});},
    getMissions:function(){return Promise.resolve({ok:false,reason:'net'});},
    postProgress:function(){return Promise.resolve({ok:false});},
    verifyAdmin:function(){return Promise.resolve(%s);},
    logout:function(){window.__loggedOut=1;return Promise.resolve();}
  };},
  set:function(){}});
""" % ("true" if admin else "false")

ok_n = bad_n = 0


def chk(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


BOX = """(s) => { const e = document.querySelector(s); if(!e) return null;
  const b = e.getBoundingClientRect();
  return {x:b.x, y:b.y, w:b.width, h:b.height,
          inView: b.left >= 0 && b.top >= 0 && b.right <= innerWidth && b.bottom <= innerHeight}; }"""


def new_page(br, w=1440, h=900, admin=False):
    ctx = br.new_context(viewport={"width": w, "height": h}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script(stub(admin))
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(1200)
    return ctx, pg, errs


def open_menu(pg, sel):
    pg.click(f"{sel} [data-menu-btn]")
    pg.wait_for_selector(f"{sel} [data-menu-pop]:not([hidden])", timeout=5000)
    pg.wait_for_timeout(260)          # cho animation umDrop dung han roi moi do


def main():
    with sync_playwright() as br_p:
        br = br_p.chromium.launch()

        # ══════════ 1. Mac dinh: menu DONG ══════════
        print("\n[1] Mac dinh menu phai DONG (bay `[hidden]` lan thu 12)")
        ctx, pg, errs = new_page(br)
        for sel in (".user-menu", ".lang-pick"):
            chk(f"{sel}: tam tha dang an",
                pg.evaluate("(s)=>document.querySelector(s+' [data-menu-pop]').hidden", sel))
            chk(f"{sel}: an THAT (display:none, khong chi la thuoc tinh)",
                pg.evaluate("(s)=>getComputedStyle(document.querySelector"
                            "(s+' [data-menu-pop]')).display === 'none'", sel))
            chk(f"{sel}: aria-expanded=false",
                pg.get_attribute(f"{sel} [data-menu-btn]", "aria-expanded") == "false")

        # ══════════ 2. Menu cua toi: mo ra, du 6 duong vao ══════════
        print("\n[2] Menu cua toi: mo ra va co du duong vao")
        open_menu(pg, ".user-menu")
        chk("aria-expanded=true sau khi bam",
            pg.get_attribute(".user-menu [data-menu-btn]", "aria-expanded") == "true")
        b = pg.evaluate(BOX, ".user-menu [data-menu-pop]")
        chk("tam tha nam TRON trong khung nhin", b and b["inView"], str(b))
        links = pg.eval_on_selector_all(
            ".user-menu [data-menu-pop] a[href]", "es => es.map(e => e.getAttribute('href'))")
        for want in ("profile.html", "achievements.html", "specimen-vault.html",
                     "shop.html", "parent.html"):
            chk(f"co duong vao {want}", want in links, str(links))
        chk("co nut Dang xuat", pg.is_visible(".um-item.um-out"))
        # ⚠️ Do TREN CUNG tai tam tung muc: mot cai link nam duoi lop khac thi bam
        #    khong an, ma doc DOM khong bao gio thay dieu do.
        top = pg.evaluate("""() => {
          const out = [];
          document.querySelectorAll('.user-menu [data-menu-pop] a,.user-menu [data-menu-pop] button')
            .forEach(e => { const r = e.getBoundingClientRect();
              const t = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
              out.push(!!t && (e === t || e.contains(t))); });
          return out; }""")
        chk("moi muc deu la phan tu TREN CUNG tai tam no", all(top), str(top))
        # Vung cham >= 48px (44 la moc TOI THIEU cua WCAG 2.5.5)
        small = pg.eval_on_selector_all(
            ".user-menu [data-menu-pop] a,.user-menu [data-menu-pop] button",
            "es => es.filter(e => e.getBoundingClientRect().height < 48)"
            ".map(e => e.className + ':' + Math.round(e.getBoundingClientRect().height))")
        chk("moi muc cao >= 48px", not small, str(small))

        # ══════════ 3. Dong bang Escape + tra tieu diem ══════════
        print("\n[3] Escape dong menu va TRA tieu diem ve nut")
        pg.focus(".um-item.um-profile")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(250)
        chk("Escape dong tam tha",
            pg.evaluate("()=>document.querySelector('.user-menu [data-menu-pop]').hidden"))
        chk("tieu diem tro ve nut mo menu",
            pg.evaluate("()=>document.activeElement === "
                        "document.querySelector('.user-menu [data-menu-btn]')"))

        # ══════════ 4. Bam ra ngoai thi dong ══════════
        print("\n[4] Bam ra ngoai thi dong")
        open_menu(pg, ".user-menu")
        pg.mouse.click(30, 500)
        pg.wait_for_timeout(250)
        chk("bam ra ngoai -> dong",
            pg.evaluate("()=>document.querySelector('.user-menu [data-menu-pop]').hidden"))

        # ══════════ 5. Mo cai nay thi cai kia dong ══════════
        print("\n[5] Chi MOT menu mo tai mot thoi diem")
        open_menu(pg, ".user-menu")
        open_menu(pg, ".lang-pick")
        chk("mo bo chon ngon ngu thi menu avatar dong lai",
            pg.evaluate("()=>document.querySelector('.user-menu [data-menu-pop]').hidden"))

        # ══════════ 6. Bo chon ngon ngu ══════════
        print("\n[6] Bo chon ngon ngu: 2 ngon ngu that + phan 'sap co'")
        b = pg.evaluate(BOX, ".lang-pick [data-menu-pop]")
        chk("tam tha ngon ngu nam TRON trong khung nhin", b and b["inView"], str(b))
        ready = pg.eval_on_selector_all(".lang-pick .lang-switch [data-lang]",
                                        "es => es.map(e => e.dataset.lang)")
        chk("dung 2 ngon ngu da co noi dung (vi, en)", ready == ["vi", "en"], str(ready))
        soon = pg.eval_on_selector_all("[data-lang-soon]", "es => es.map(e => e.dataset.langSoon)")
        chk("co danh sach ngon ngu 'sap co'", len(soon) >= 4, str(soon))
        # ⚠️ Ngon ngu chua co noi dung TUYET DOI khong duoc mang `data-lang`:
        #    `initLang` gan su kien cho MOI `.lang-switch button`, nen no se ghi mot
        #    ma khong ton tai vao `astroq-lang` va tu do trang lang le ve tieng Viet.
        chk("muc 'sap co' KHONG mang data-lang",
            pg.eval_on_selector_all("[data-lang-soon]",
                                    "es => es.every(e => !e.hasAttribute('data-lang'))"))
        chk("muc 'sap co' nam NGOAI .lang-switch",
            pg.eval_on_selector_all("[data-lang-soon]",
                                    "es => es.every(e => !e.closest('.lang-switch'))"))
        chk("nut thu gon hien ma ngon ngu dang dung",
            pg.inner_text("[data-lang-code]").strip() == "VI",
            pg.inner_text("[data-lang-code]").strip())
        chk("muc dang chon co dau tich (class active)",
            pg.eval_on_selector(".lang-pick [data-lang='vi']",
                                "e => e.classList.contains('active')"))

        # Bam mot ngon ngu CHUA co noi dung -> phai co loi nhan, khong im lang
        pg.click("[data-lang-soon='ja']")
        pg.wait_for_timeout(300)
        toast = pg.inner_text("#toast") if pg.is_visible("#toast") else ""
        chk("bam ngon ngu 'sap co' -> CO loi nhan (khong im lang)",
            "日本語" in toast, toast.replace("\n", " ")[:70])
        chk("bam ngon ngu 'sap co' KHONG ghi de astroq-lang",
            pg.evaluate("()=>localStorage.getItem('astroq-lang')") == "vi")
        chk("menu VAN MO sau khi bam muc 'sap co'",
            not pg.evaluate("()=>document.querySelector('.lang-pick [data-menu-pop]').hidden"))

        # Bam EN -> doi that
        before = pg.inner_text(".hero h1")
        pg.click(".lang-pick [data-lang='en']")
        pg.wait_for_timeout(700)
        chk("bam EN -> chu tren trang doi that",
            pg.inner_text(".hero h1") != before,
            f"{before!r} -> {pg.inner_text('.hero h1')!r}")
        chk("bam EN -> luu lua chon",
            pg.evaluate("()=>localStorage.getItem('astroq-lang')") == "en")
        chk("bam EN -> nut thu gon doi theo",
            pg.inner_text("[data-lang-code]").strip() == "EN")
        chk("chon xong thi menu tu dong",
            pg.evaluate("()=>document.querySelector('.lang-pick [data-menu-pop]').hidden"))
        open_menu(pg, ".user-menu")
        chk("EN: nhan trong menu cung dich",
            "Profile" in pg.inner_text(".um-item.um-profile"),
            pg.inner_text(".um-item.um-profile").replace("\n", " "))
        pg.keyboard.press("Escape")

        chk("0 loi console", not errs, str(errs[:1])[:110])
        ctx.close()

        # ══════════ 7. Bam that vao mot muc -> toi dung trang ══════════
        print("\n[7] Bam mot muc -> toi dung trang")
        ctx, pg, errs = new_page(br)
        open_menu(pg, ".user-menu")
        with pg.expect_navigation(wait_until="load"):
            pg.click(".um-item.um-awards")
        chk("bam 'Thanh tich' -> achievements.html",
            pg.url.endswith("/achievements.html"), pg.url)
        ctx.close()

        # ══════════ 8. Dang xuat van chay ══════════
        print("\n[8] Nut Dang xuat van goi AstroQAuth.logout()")
        ctx, pg, errs = new_page(br)
        open_menu(pg, ".user-menu")
        # ⚠️ Bam Dang xuat thi trang DIEU HUONG ngay sau khi logout() resolve, nen
        #    doc `window.__loggedOut` sau do la doc tren TRANG MOI (luon undefined).
        #    Do bang chinh cai dich den — do la thu nguoi dung thay.
        with pg.expect_navigation(wait_until="load"):
            pg.click(".um-item.um-out")
        chk("bam Dang xuat -> ve landing-app.html", pg.url.endswith("/landing-app.html"), pg.url)
        ctx.close()

        # ══════════ 9. O admin: chi hien voi admin ══════════
        print("\n[9] Duong vao bao cao he thong: chi hien voi admin")
        ctx, pg, errs = new_page(br, admin=False)
        open_menu(pg, ".user-menu")
        chk("KHONG phai admin -> khong co muc bao cao he thong",
            pg.eval_on_selector_all(".um-pop .admin-link", "es => es.length") == 0)
        ctx.close()
        ctx, pg, errs = new_page(br, admin=True)
        open_menu(pg, ".user-menu")
        chk("la admin -> co muc bao cao he thong",
            pg.eval_on_selector_all(".um-pop .admin-link", "es => es.length") == 1)
        ab = pg.evaluate(BOX, ".um-pop .admin-link")
        chk("muc admin nam TRON trong tam tha, khong tran ra ngoai",
            ab and ab["inView"], str(ab))
        ctx.close()

        # ══════════ 10. Dien thoai 390x844 ══════════
        print("\n[10] Dien thoai 390x844")
        ctx, pg, errs = new_page(br, 390, 844)
        for sel in (".user-menu", ".lang-pick"):
            open_menu(pg, sel)
            b = pg.evaluate(BOX, f"{sel} [data-menu-pop]")
            # ⚠️ Day la phep kiem sinh ra tu mot loi THAT: tam tha tung tho ra
            #    ngoai mep trai (x = -78) vi no neo mep phai cua mot cai nut khong
            #    nam sat mep phai. Do bang TOA DO, khong doc CSS.
            chk(f"{sel}: khong tho ra ngoai mep trai", b and b["x"] >= 0, str(b))
            chk(f"{sel}: khong tho ra ngoai mep phai",
                b and b["x"] + b["w"] <= 390 + 1, str(b))
            chk(f"{sel}: nam trong chieu cao man hinh",
                b and b["y"] >= 0 and b["y"] + b["h"] <= 844 + 1, str(b))
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(200)
        chk("dien thoai: trang khong tran ngang",
            pg.evaluate("()=>document.documentElement.scrollWidth <= innerWidth + 1"))
        chk("0 loi console (dien thoai)", not errs, str(errs[:1])[:110])
        ctx.close()

        br.close()

    print("\n" + "=" * 58)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    print("=" * 58)
    return 1 if bad_n else 0


if __name__ == "__main__":
    sys.exit(main())
