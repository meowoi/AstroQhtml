# -*- coding: utf-8 -*-
r"""verify_prod_0826_route.py — DO TREN BAN THAT `astroq.org` sau luot push 26/08/2026
thu HAI (mo 4 game lop quyet dinh + ARCADE-11 Tram Dan Tuyen).

    python scratchpad/verify_prod_0826_route.py

Do dung thu mot dua tre gap: mo Khu Huan Luyen, thay 11 the va KHONG the nao khoa,
roi vao ARCADE-11 choi thang mot ban va doc duoc cau kien thuc.

⚠️ HAI BO `verify_prod_0826*` KIA LA CUA LUOT PUSH KHAC trong cung ngay
   (`verify_prod_0826.py` = tang mang · `verify_prod_0826_ui.py` = tang trinh duyet,
   cho dot lam dan nhan explorer). ⚠️⚠️ **DUNG GHI DE CHUNG** — ngay 26/08/2026 chinh
   file nay tung duoc `cp` de len `verify_prod_0826.py` va **xoa mat 187 dong da
   commit** cua phien song song; phai lay lai tu `git show`. Ten file trong
   `scratchpad/` la khong gian ten dung chung: them hau to viec, dung tram ngay.

⚠️ Bo `verify_*` KHONG duoc dua vao cong push (`run_gate.py` liet ke ly do): no do
   tren ban that nen chi chay SAU khi GitHub Pages xay xong (~1-2 phut).
⚠️ No KHONG tao du lieu nguoi dung nao — chi doc trang tinh va choi mot ban trong
   trinh duyet, khong dang nhap, khong goi API co token.
⚠️ Chay CA HAI ngon ngu: mot loi chi hien o mot ngon ngu la ca da lot hai lan o lop
   game quyet dinh.
"""
import sys
from playwright.sync_api import sync_playwright
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
SITE="https://astroq.org"
ok=bad=0
def ck(l,c,d=""):
    global ok,bad
    if c: ok+=1; print(f"  [OK]   {l}"+(f"  ({d})" if d else ""))
    else: bad+=1; print(f"  [HONG] {l}"+(f"  ({d})" if d else ""))
with sync_playwright() as pw:
    br=pw.chromium.launch()
    for lang,w,h in (("vi",1440,900),("en",390,844)):
        ctx=br.new_context(viewport={"width":w,"height":h}); pg=ctx.new_page()
        errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.on("console",lambda m: errs.append("console:"+m.text) if m.type=="error" else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','%s');localStorage.setItem('astroq-asteroids','40');"%lang)
        pg.goto(SITE+"/games.html",wait_until="load"); pg.wait_for_selector(".gcard")
        n=pg.locator(".gcard").count(); nsoon=pg.locator(".gcard.soon").count()
        ck(f"[{lang}] games.html co 11 the, 0 the khoa", n==11 and nsoon==0, f"{n} the, {nsoon} soon")
        pg.goto(SITE+"/game-route.html",wait_until="load")
        pg.wait_for_selector("#ov-start.show",timeout=15000)
        pg.click("#start-btn"); pg.wait_for_timeout(900)
        cells=pg.locator(".rt-c").count()
        ck(f"[{lang}] ban ve ra tren ban that", cells>=16, f"{cells} o")
        g=pg.evaluate("() => window.__dbg.grid()")
        ck(f"[{lang}] co pa-no va thiet bi", len(g["srcs"])>=1 and len(g["dsts"])>=1)
        pg.evaluate("() => window.__dbg.solve()"); pg.wait_for_timeout(250)
        pg.click("#go"); pg.wait_for_timeout(700)
        ck(f"[{lang}] cap dien xong thi duoc diem", pg.inner_text("#hb-score")=="1", pg.inner_text("#hb-score"))
        ck(f"[{lang}] hop kien thuc hien ra", pg.is_visible("#why"), pg.inner_text("#why")[:60])
        ck(f"[{lang}] 0 loi trang", not errs, str(errs[:1])[:120])
        ctx.close()
    br.close()
print(f"\n=== {ok} dat / {bad} hong ===")
sys.exit(1 if bad else 0)
