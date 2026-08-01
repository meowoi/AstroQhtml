# -*- coding: utf-8 -*-
"""
smoke_map_warp.py — ĐO TRÊN TRANG: chuyển cảnh dashboard → Bản Đồ Thiên Hà bằng màn
loading Luna (việc MỚI của js/warp-screen.js, chốt 01/08/2026).

    python -m http.server 8123        (trong AstroQhtml/)
    set PYTHONIOENCODING=utf-8
    python scratchpad/smoke_map_warp.py

Bộ này canh đúng những thứ ĐỌC CODE KHÔNG THẤY ĐƯỢC:
  · bấm "Mở bản đồ" thì màn loading có hiện THẬT không, và có ĐI TỚI explorer.html không;
  · lời phủ riêng có ăn không (bộ mặc định nói "Đã vào quỹ đạo Trái Đất" — sai đích
    cho cú mở bản đồ), và bộ mặc định có bị hỏng theo không;
  · nút "Bỏ qua ›" có đi tiếp NGAY không (bỏ màn phim ≠ bỏ chuyến đi);
  · **Ctrl-click vẫn mở tab mới** — chặn hết cách mở của trình duyệt là lấy đi một
    hành vi người dùng không hiểu vì sao mất;
  · `prefers-reduced-motion` vẫn tới được bản đồ.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
USER = '{"name":"Bi","pilotName":"Bi","character":"raica",' \
       '"avatar":"ava/avaraica.png","uid":"test-uid"}'

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


def dash(br, lang="vi", reduced=False):
    """Mở dashboard ở trạng thái "đã qua hết onboarding" để không màn nào che.

    ⚠️ Phải gieo `astroq-map01-seen`: từ 01/08/2026 dashboard đẩy trẻ sang
       `explorer.html?onboard=1` khi chưa đi qua bản đồ (docs/decisions/003) — không
       gieo thì trang điều hướng đi và không còn thẻ nào để bấm.
    """
    kw = {"locale": "vi-VN", "viewport": {"width": 1440, "height": 950}}
    if reduced:
        kw["reduced_motion"] = "reduce"
    ctx = br.new_context(**kw)
    ctx.add_init_script(
        "localStorage.setItem('astroq-user', %s);" % json.dumps(USER)
        + f"localStorage.setItem('astroq-lang','{lang}');"
        "localStorage.setItem('astroq-asteroids','41');"
        "localStorage.setItem('astroq-tour-seen','1');"
        "localStorage.setItem('astroq-map01-seen','1');"
        "localStorage.setItem('astroq-mission01-intro-seen','1');"
    )
    errs = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.goto(f"{BASE}/dashboard.html", wait_until="load")
    pg.wait_for_timeout(1200)
    return ctx, pg, errs


def cap(pg):
    """⚠️ `#warp` được dựng LƯỜI — `js/warp-screen.js` chỉ gọi `build()` bên trong
    `play()`, nên trước cú bấm đầu tiên phần tử đó KHÔNG TỒN TẠI. Đọc thẳng
    `.classList` là `TypeError` và bộ đo chết giữa lúc chạy (đã dính)."""
    return pg.evaluate("""() => {
      const w = document.querySelector('#warp');
      const g = (s) => { const e = document.querySelector(s);
                         return e ? (e.textContent || '') : ''; };
      return {
        exists: !!w,
        shown: !!w && w.classList.contains('show'),
        lead: g('.warp-cap .lead'), sub: g('.warp-cap .sub'), skip: g('.warp-skip')
      };
    }""")


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()

        # ─────────────────────────────────────────────────────────────
        head("[1] Bam 'Mo ban do' -> man loading Luna hien ra")
        ctx, pg, errs = dash(br)
        chk(pg.evaluate(
                """() => !!document.querySelector('.card--map a[href="explorer.html"]')"""),
            "tim thay nut 'Mo ban do' o the MOD-03")
        chk(not cap(pg)["shown"], "chua bam thi KHONG hien man loading")

        pg.click('.card--map a[href="explorer.html"]')
        pg.wait_for_selector("#warp.show", timeout=5000)
        c = cap(pg)
        chk(c["shown"], "man loading hien ra")
        chk("Trung Tâm Điều Hướng" in c["lead"],
            "loi PHU rieng: noi dung roi Trung Tam Dieu Huong", c["lead"])
        chk("Luna" in c["sub"], "dong duoi noi ve Luna", c["sub"])
        chk(c["skip"].strip().startswith("Bỏ qua"),
            "nut 'Bo qua' KHONG rong (loi phu theo TUNG khoa)", repr(c["skip"]))
        # ⚠️ Bộ mặc định là lời của lượt ĐẦU TIÊN đi tới Trái Đất — dùng lại nguyên
        #    văn cho cú mở bản đồ là nói sai đích và nói sai lần thứ mấy.
        chk("quỹ đạo Trái Đất" not in c["lead"] and "quỹ đạo Trái Đất" not in c["sub"],
            "KHONG dung lai loi mac dinh 'Da vao quy dao Trai Dat'",
            f"{c['lead']} / {c['sub']}")
        chk(not errs, "0 loi console", str(errs[:3]))

        # Phải THẬT SỰ tới được bản đồ, không chỉ hiện màn phim
        pg.wait_for_url("**/explorer.html", timeout=15000)
        chk("explorer.html" in pg.url, "man loading xong -> sang explorer.html",
            pg.url.split("/")[-1])
        ctx.close()

        # ─────────────────────────────────────────────────────────────
        head("[2] Nut 'Bo qua' -> di tiep NGAY (bo man phim, khong bo chuyen di)")
        ctx, pg, errs = dash(br)
        pg.click('.card--map a[href="explorer.html"]')
        pg.wait_for_selector("#warp.show", timeout=5000)
        pg.wait_for_timeout(400)
        pg.click(".warp-skip")
        pg.wait_for_url("**/explorer.html", timeout=8000)
        chk("explorer.html" in pg.url, "bam Bo qua -> sang ngay explorer.html",
            pg.url.split("/")[-1])
        # ⚠️ Và KHÔNG kèm ?onboard=1 — đây là lượt vào bản đồ bình thường, cổng phải TẮT.
        chk("onboard" not in pg.url, "KHONG bat cong lo trinh o luot vao binh thuong",
            pg.url)
        chk(not errs, "0 loi console", str(errs[:3]))
        ctx.close()

        # ─────────────────────────────────────────────────────────────
        head("[3] Ctrl-click VAN mo tab moi (khong lay di hanh vi trinh duyet)")
        ctx, pg, errs = dash(br)
        before = len(ctx.pages)
        with ctx.expect_page(timeout=8000) as newpg:
            pg.click('.card--map a[href="explorer.html"]',
                     modifiers=["ControlOrMeta"])
        tab = newpg.value
        chk(len(ctx.pages) == before + 1, "co tab moi mo ra",
            f"{before} -> {len(ctx.pages)}")
        # ⚠️ CHỜ TAB MỚI NẠP XONG. Lúc `expect_page` trả về, tab còn ở `about:blank` —
        #    đo URL ngay là đo một thứ chưa xảy ra (đã dính: báo `about:blank`).
        try:
            tab.wait_for_url("**/explorer.html", timeout=15000)
        except Exception:
            pass
        chk("explorer.html" in tab.url, "tab moi la explorer.html", tab.url)
        chk(not cap(pg)["shown"],
            "Ctrl-click KHONG chay man loading o tab cu (khong chan hanh vi)")
        chk("dashboard.html" in pg.url, "tab cu O LAI dashboard", pg.url.split("/")[-1])
        tab.close()
        chk(not errs, "0 loi console", str(errs[:3]))
        ctx.close()

        # ─────────────────────────────────────────────────────────────
        head("[4] Ban tieng Anh")
        ctx, pg, errs = dash(br, "en")
        pg.click('.card--map a[href="explorer.html"]')
        pg.wait_for_selector("#warp.show", timeout=5000)
        c = cap(pg)
        chk("Navigation Hub" in c["lead"], "loi phu dich sang EN", c["lead"])
        chk("Luna" in c["sub"], "dong duoi EN noi ve Luna", c["sub"])
        chk(c["skip"].strip().startswith("Skip"), "nut Bo qua dich sang EN",
            repr(c["skip"]))
        chk("Earth orbit" not in c["lead"], "KHONG dung lai loi mac dinh EN", c["lead"])
        chk(not errs, "0 loi console", str(errs[:3]))
        ctx.close()

        # ─────────────────────────────────────────────────────────────
        head("[5] Giam chuyen dong — van toi duoc ban do")
        ctx, pg, errs = dash(br, reduced=True)
        pg.click('.card--map a[href="explorer.html"]')
        pg.wait_for_selector("#warp.show", timeout=5000)
        pg.wait_for_url("**/explorer.html", timeout=12000)
        chk("explorer.html" in pg.url, "giam chuyen dong: van sang duoc ban do",
            pg.url.split("/")[-1])
        chk(not errs, "0 loi console", str(errs[:3]))
        ctx.close()

        # ─────────────────────────────────────────────────────────────
        head("[6] Bo mac dinh KHONG bi loi phu lam hong (goi play() tran)")
        ctx, pg, errs = dash(br)
        # ⚠️ Lời phủ đặt lại MỖI lượt; không đặt lại thì lượt sau dính lời của lượt trước.
        pg.evaluate("() => AstroQWarp.play({ lang:'vi' })")
        pg.wait_for_selector("#warp.show", timeout=5000)
        c = cap(pg)
        chk("khởi động động cơ" in c["lead"].lower(),
            "goi play() tran -> LAI dung bo mac dinh", c["lead"])
        chk("Trung Tâm" not in c["lead"], "loi phu cua luot truoc KHONG dinh sang",
            c["lead"])
        chk(not errs, "0 loi console", str(errs[:3]))
        ctx.close()

        br.close()

    print(f"\n=== KET QUA: {ok} dat / {fail} hong ===")
    if FAILS:
        print("Hong:")
        for f in FAILS:
            print("  - " + f)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
