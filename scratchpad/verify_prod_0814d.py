# -*- coding: utf-8 -*-
"""Do tren BAN THAT (astroq.org) hai nhanh vua giao: LAP TRINH + MATHEMATICS.

   Phep kiem dang gia nhat o day KHONG phai "file tai ve duoc" (curl da tra loi),
   ma la hai thu chi doc chu tren trang moi biet:
     · con so NASA co toi duoc tre nguyen ven khong (1,2 met · 17,5 do · 9,46
       nghin ti · 24 nghin ti dam)
     · ranh gioi "loi NASA" vs "loi astroQ" co con nguyen khong — ba cho suy luan
       cua astroQ phai TU KHAI la cua astroQ
   Ba cho suyt bia cua ca dot (CHNOPS · don vi dam/gio · "170 km") deu la kieu loi
   ma chi mot phep kiem doc thang chu moi chan duoc duong quay lai."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

BASE = "https://astroq.org"
OK = FAIL = 0


def chk(cond, label, info=""):
    global OK, FAIL
    if cond:
        OK += 1
        print(f"  [OK]   {label}" + (f"  ({info})" if info else ""))
    else:
        FAIL += 1
        print(f"  [HONG] {label}" + (f"  ({info})" if info else ""))


def read(pg, art_id):
    """Mo mot bai bang chinh duong tre di, roi tra ve than bai + phan Mo rong."""
    pg.evaluate("id=>{const c=document.querySelector(`[data-id='${id}']`); if(c)c.click();}", art_id)
    pg.wait_for_selector("#reader.show", timeout=30000)
    pg.wait_for_function(
        "()=>document.querySelector('#r-body')&&document.querySelector('#r-body').children.length>0",
        timeout=30000)
    pg.wait_for_timeout(250)
    btn = pg.query_selector("#r-more .mb-btn")
    if btn and pg.eval_on_selector("#r-more .mb-body", "e=>getComputedStyle(e).display==='none'"):
        btn.click(); pg.wait_for_timeout(200)
    return pg.evaluate("""()=>({
        body:(document.getElementById('r-body')||{}).textContent||'',
        more:(document.querySelector('#r-more .mb-body')||{}).textContent||''})""")


with sync_playwright() as p:
    br = p.chromium.launch()
    errs, bad = [], []
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-user',JSON.stringify({depth:'junior'}));")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)

    pg.goto(f"{BASE}/library.html", wait_until="load", timeout=60000)
    pg.wait_for_selector(".card", timeout=30000)

    print("\n=== Kho bai doc tren ban that ===")
    n = pg.evaluate("()=>AstroQArticles.all().length")
    chk(n >= 60, "muc luc co du 60 bai", str(n))
    chips = pg.eval_on_selector_all(".cat", "els=>els.map(e=>e.dataset.cat)")
    chk("math" in chips and "life" in chips, "co chip `math` va `life`", str(chips))
    cnt = pg.evaluate("()=>{const a=AstroQArticles.all();return{math:a.filter(x=>x.cat==='math').length,"
                      "it:a.filter(x=>x.cat==='it').length,life:a.filter(x=>x.cat==='life').length}}")
    chk(cnt["math"] == 4 and cnt["it"] == 7 and cnt["life"] == 5, "so bai tung chu de dung", str(cnt))

    print("\n=== Nhanh LAP TRINH: con so + ranh gioi ===")
    a = read(pg, "art-loop-you-can-see-on-mars")
    chk("1,2" in a["body"] and "17,5" in a["body"], "than bai giu nguyen 1,2 met va 17,5 do")
    chk("VÒNG LẶP" in a["more"], "phan Mo rong day khai niem vong lap")
    chk("3 tinh thể" in a["more"], "Mo rong dung DUNG vi du cua cau quiz `loop`")
    chk("không phải chữ NASA dùng" in a["more"], "TU KHAI: chu 'vong lap' la cua astroQ")
    pg.click("#r-close"); pg.wait_for_timeout(200)

    print("\n=== Nhanh MATHEMATICS: con so + ranh gioi ===")
    a = read(pg, "art-units-lost-a-spacecraft")
    chk("23 tháng 9 năm 1999" in a["body"], "giu nguyen ngay lien lac cuoi")
    chk("170" not in a["body"] and "170" not in a["more"],
        "KHONG dung con so 170 km ma trang nguon khong noi")

    pg.click("#r-close"); pg.wait_for_timeout(200)
    a = read(pg, "art-light-year-is-a-distance")
    chk("9,46" in a["body"], "giu nguyen 9,46 nghin ti km")
    chk("24 nghìn tỉ dặm" in a["body"], "giu DON VI NASA cho con so 24 nghin ti")
    chk("phép chia của astroQ" in a["more"], "TU KHAI: phep chia 260.000 la cua astroQ")

    pg.click("#r-close"); pg.wait_for_timeout(200)
    a = read(pg, "art-measuring-stars-with-angles")
    chk("cách astroQ giải thích" in a["more"], "TU KHAI: phep vi ngon tay la cua astroQ")

    pg.click("#r-close"); pg.wait_for_timeout(200)
    a = read(pg, "art-orbit-is-a-balance")
    chk("elip" in a["body"].lower(), "than bai noi quy dao la hinh elip")
    chk("cách astroQ diễn đạt lại" in a["more"], "TU KHAI: lap luan hinh bau duc la cua astroQ")

    print("\n=== Day noi `loop` dau-cuoi ===")
    pg.click("#r-close"); pg.wait_for_timeout(200)
    pg.evaluate("id=>document.querySelector(`[data-id='${id}']`).click()", "art-loop-you-can-see-on-mars")
    pg.wait_for_function("()=>document.querySelector('#r-body').children.length>0", timeout=30000)
    with pg.expect_navigation(wait_until="load", timeout=30000):
        pg.click("#r-quiz")
    chk("terms=loop" in pg.url, "nut Quiz dan sang dung cau `loop`", pg.url.split("/")[-1])
    pg.wait_for_timeout(3000)
    q = pg.evaluate("()=>{const e=document.querySelector('#q-text');return e?e.textContent:''}")
    chk("tinh thể" in q, "quiz mo ra DUNG cau ve vong lap", q[:48])

    chk(not errs, "0 loi console / pageerror", str(errs[:3]))
    chk(not bad, "0 asset hong", str(bad[:3]))
    ctx.close(); br.close()

print(f"\n===== {OK} dat / {FAIL} hong =====")
sys.exit(1 if FAIL else 0)
