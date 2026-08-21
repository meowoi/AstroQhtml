# -*- coding: utf-8 -*-
"""
smoke_touch_only.py — CHƠI ĐƯỢC BẰNG NGÓN TAY KHÔNG? (máy tính bảng, không bàn phím)

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/smoke_touch_only.py

VÌ SAO CẦN BỘ RIÊNG:
  `audit_viewports.py` đã chứng minh bố cục vừa màn iPad và vùng chạm đủ 44px.
  Nhưng "nhìn vừa màn" KHÔNG có nghĩa là "chơi được". Câu hỏi ở đây khác hẳn:
  một đứa trẻ chỉ có ngón tay — không chuột, không bàn phím — có bấm được nút,
  bắn được, nối được sao, chạm được điểm tín hiệu hay không.

⚠️ CHỈ DÙNG `page.touchscreen.tap()`, TUYỆT ĐỐI KHÔNG `page.mouse`. Chuột và chạm
   đi qua hai đường sự kiện khác nhau: `mousemove` không bao giờ xảy ra trên máy
   tính bảng, và `setPointerCapture` chặn `click` theo cách mà chuột cũng dính
   nhưng chỉ lộ ra khi thử đúng kiểu người dùng thật. Dùng `mouse` ở đây là tự
   trả lời một câu hỏi khác.

⚠️ Nhãn của check() PHẢI KHÔNG DẤU — console Windows mặc định cp1252.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
USER = {"name": "Bi", "pilotName": "Bi", "character": "raica",
        "avatar": "ava/avaraica.png", "uid": "touch-uid", "selectedCharacter": "raica"}

ok_n = bad_n = 0


import io as _io, os as _os, re
# goc repo, suy tu vi tri script — khong gan cung duong dan may
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def check(cond, label, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [ok]   {label}" + (f"  {detail}" if detail else ""))
    else:
        bad_n += 1
        print(f"  [FAIL] {label}  {detail}")


def ipad(br):
    """iPad mini dọc, CÓ cảm ứng và KHÔNG có chuột."""
    ctx = br.new_context(viewport={"width": 768, "height": 1024}, has_touch=True,
                         is_mobile=True, device_scale_factor=2, locale="vi-VN")
    ctx.add_init_script(
        f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
        "localStorage.setItem('astroq-lang','vi');"
        "localStorage.setItem('astroq-asteroids','300');"
        "localStorage.setItem('astroq-tour-seen','1');"
        "localStorage.setItem('astroq-mission01-intro-seen','1');"
        "localStorage.setItem('astroq-mob-note','1');")
    return ctx


def tap_el(pg, sel):
    """Chạm vào một phần tử bằng màn cảm ứng.

    ⚠️ DÙNG `locator.tap()`, KHÔNG tự đo toạ độ rồi `touchscreen.tap()`.
       Bản đầu của tôi đọc `getBoundingClientRect()` rồi chạm vào con số đó, và nó
       BÁO OAN game Né Thiên Thạch là "không bấm được nút Bắt đầu trên máy tính
       bảng". Thật ra bố cục lúc đó còn đang dịch (font `css/fonts.css` chưa tải
       xong), nên toạ độ đo được đã cũ khi cú chạm tới nơi. `locator.tap()` tự chờ
       phần tử hiện ra, ĐỨNG YÊN và bấm được rồi mới chạm — đúng bài học
       `wait_stable()` đã ghi cho `smoke_onboard.py`.
       Vẫn dùng `touchscreen.tap(x, y)` cho những chỗ CHỈ có toạ độ (mặt canvas,
       điểm tín hiệu trong cảnh) — ở đó không có phần tử nào để chờ.
    """
    loc = pg.locator(sel).first
    try:
        loc.tap(timeout=5000)
        return True
    except Exception:
        return False


def dismiss_rotate(pg):
    """Bo qua loi nhac "xoay ngang" — DUNG NHU MOT DUA TRE LAM.

    ⚠️ VI SAO CAN: bo do nay chay o iPad DOC 768x1024 + has_touch, tuc khop dung
       `(orientation: portrait) and (pointer: coarse)` — dieu kien lam
       `js/game-shell.js` dung lop phu `.ov.rot`. Lop do duoc THEM SAU vao `.play`
       nen no nam TREN nut "Bat dau", va `locator.tap()` cho mai vi phan tu khong
       nhan duoc cu cham. Ket qua: bo do bao "cham nut Bat dau -> khong vao duoc
       luot choi" va "canvas nhan 0 cu cham" — doc ra Y NHU MOT LOI SAN PHAM NANG
       o dung thiet bi app nham toi. That ra do la HANH VI DUNG cua san pham (lop
       phu that, va no CO duong ra), chi la bo do khong bam duong ra. Dung lop loi
       da ghi o CLAUDE.md ngay 12/08/2026 cho `play_maze`. Bo do nay hong AM THAM
       tu 16/08/2026 (luc them cua `data-rotate`).

    Nhan do kiem luon: duong ra PHAI CO THAT. Mot loi nhac khong co duong ra la
    tre dang bat khoa xoay se KET CUNG — dieu kien da chot 12/08/2026.
    """
    if pg.locator(".ov.rot.show").count() == 0:
        return None                      # game khai data-rotate="off"
    ok = pg.locator(".ov.rot.show .rot-ok")
    check(ok.count() == 1, "loi nhac xoay ngang CO duong ra", str(ok.count()))
    lbl = (ok.inner_text() or "").strip()
    check(len(lbl) > 0, "duong ra co nhan chu", lbl)
    ok.tap()
    pg.wait_for_timeout(150)
    check(pg.locator(".ov.rot.show").count() == 0,
          "bam duong ra thi loi nhac tat han")
    return lbl

with sync_playwright() as p:
    br = p.chromium.launch()

    # ───────────────── QUIZ ─────────────────
    print("=== [1] Quiz: chon dap an va xac nhan bang NGON TAY ===")
    ctx = ipad(br)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/quiz.html", wait_until="load", timeout=30000)
    pg.wait_for_timeout(1200)
    check(pg.evaluate("()=>document.getElementById('engage').disabled") is True,
          "chua chon thi nut KICH HOAT dang khoa")
    check(tap_el(pg, ".opt"), "cham duoc vao mot dap an")
    pg.wait_for_timeout(350)
    check(pg.evaluate("()=>document.getElementById('engage').disabled") is False,
          "cham dap an -> nut KICH HOAT mo khoa")
    check(pg.evaluate("()=>!!document.querySelector('.opt.sel')"),
          "dap an vua cham duoc to sang")
    tap_el(pg, "#engage")
    pg.wait_for_timeout(900)
    check(pg.evaluate("()=>document.getElementById('sheet').classList.contains('show')"),
          "cham KICH HOAT -> popup giai thich mo ra")
    check(not errs, "0 loi trang", str(errs[:1])[:70])
    ctx.close()

    # ───────────────── NE THIEN THACH ─────────────────
    print("\n=== [2] Ne Thien Thach: bat dau va bay len bang NGON TAY ===")
    ctx = ipad(br)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/game-dodge.html", wait_until="load", timeout=30000)
    pg.wait_for_timeout(1200)
    dismiss_rotate(pg)
    n_ov = pg.evaluate("()=>document.querySelectorAll('.ov.show').length")
    check(n_ov >= 1, "man gioi thieu dang mo", str(n_ov))
    # Nut bat dau nam trong overlay
    started = False
    for sel in (".ov.show .acts button", ".ov.show button"):
        if tap_el(pg, sel):
            started = True
            break
    # ⚠️ CHỜ NGẮN THÔI. Chờ 1,5s thì tàu đã đâm cột và `ov-over` PHỦ LÊN canvas
    #    (đúng thiết kế: overlay nằm trên để nút bấm không bị tính là vỗ cánh),
    #    nên mọi cú chạm sau đó không tới canvas và phép đo ra 0 — báo oan lần thứ ba.
    pg.wait_for_timeout(200)
    # ⚠️ ĐO ĐƯỜNG VÀO CỦA CÚ CHẠM, KHÔNG ĐO KỸ NĂNG CHƠI.
    #    Hai phép kiểm cũ ở đây ("overlay đóng sau 1,5s" và "quãng đường phải tăng")
    #    đã BÁO OAN game là hỏng trên máy tính bảng. Thật ra tàu chết sau ~2 giây vì
    #    ĐÂM VÀO CỘT: một "người chơi" chạm bừa vào giữa sân, không lách khe, thì
    #    chết là đúng — trên máy tính bảng hay máy bàn cũng vậy. `shoot_dodge.py`
    #    sống lâu được là vì nó có autopilot đọc pixel để nhắm khe.
    #    Câu hỏi ở ĐÂY là "ngón tay có điều khiển được không", nên phải đo đúng cái
    #    đó: cú chạm có tới canvas và có biến thành nhịp vỗ cánh hay không.
    check(pg.evaluate("()=>+document.getElementById('bal').textContent") < 300,
          "cham nut Bat dau -> vao luot choi (da tru phi 5 tt)",
          pg.evaluate("()=>document.getElementById('bal').textContent"))
    pg.evaluate("()=>{window.__taps=0; document.getElementById('cv')"
                ".addEventListener('touchstart', function(){ window.__taps++; });}")
    fb = pg.evaluate("()=>{const r=document.querySelector('.field').getBoundingClientRect();"
                     "return [r.x+r.width*0.5, r.y+r.height*0.5];}")
    for _ in range(3):
        pg.touchscreen.tap(fb[0], fb[1])
        pg.wait_for_timeout(150)
    check(pg.evaluate("()=>window.__taps") == 3,
          "cham vao san -> canvas nhan du 3 cu cham (duong dieu khien thong)",
          str(pg.evaluate("()=>window.__taps")))
    check(not errs, "0 loi trang", str(errs[:1])[:70])
    ctx.close()

    # ───────────────── SPACE DEFENDER ─────────────────
    print("\n=== [3] Space Defender: ngam va ban bang NGON TAY (khong co con tro) ===")
    ctx = ipad(br)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/game-defender.html", wait_until="load", timeout=30000)
    pg.wait_for_timeout(1200)
    dismiss_rotate(pg)
    for sel in (".ov.show .acts button", ".ov.show button"):
        if tap_el(pg, sel):
            break
    pg.wait_for_timeout(1200)
    check(pg.evaluate("()=>document.querySelectorAll('.ov.show').length") == 0,
          "cham nut -> vao man choi")
    # Cham GOC TREN-TRAI san: neu ngam theo cham thi nong phao phai quay ve huong do
    fb = pg.evaluate("()=>{const e=document.querySelector('.field');const r=e.getBoundingClientRect();"
                     "return [r.x, r.y, r.width, r.height];}")
    pg.touchscreen.tap(fb[0] + fb[2] * 0.22, fb[1] + fb[3] * 0.22)
    pg.wait_for_timeout(500)
    lit = pg.evaluate("""()=>{
      const c=document.getElementById('cv'), g=c.getContext('2d');
      // dem pixel sang o goc tren-trai san (noi vua cham) — co dan/lua thi sang len
      const d=g.getImageData(0,0,Math.floor(c.width*0.45),Math.floor(c.height*0.45)).data;
      let n=0; for(let i=0;i<d.length;i+=4){ if(d[i]+d[i+1]+d[i+2] > 260) n++; }
      return n;}""")
    check(lit > 0, "cham vao san -> co hinh sang o huong vua cham (dan/nong phao)",
          f"{lit} pixel sang")
    check(not errs, "0 loi trang", str(errs[:1])[:70])
    ctx.close()

    # ───────────────── NHIEM VU 01 (canh 2D) ─────────────────
    print("\n=== [4] Nhiem Vu 01 canh 2D: cham diem tin hieu bang NGON TAY ===")
    ctx = ipad(br)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/mission-earth.html?scene=2d", wait_until="load", timeout=45000)
    pg.wait_for_timeout(4000)
    dismiss_rotate(pg)
    # CANH BAO: MOC CHO 3000ms O DAY LA QUA NGAN — loi Comet GO TUNG CHU (22ms/
    #   ky tu), va Chrome HAM `setInterval` o tab khong co tieu diem: quy tac 9
    #   muc 6 do duoc ~124ms/ky tu, cham 5,6 lan. Mot cau 170 ky tu vi the co the
    #   mat hon 20 giay. Het han -> `break` -> KHONG bam nut nao -> marker khong
    #   bao gio hien -> phep cho ben duoi het han va doc ra nhu san pham hong.
    #   `smoke_mission_earth.py` da phai noi moc nay len 90 giay vi dung ly do do.
    for _ in range(8):
        try:
            pg.wait_for_function(
                "()=>{const b=document.getElementById('say-next');"
                " return b && !b.classList.contains('hide') &&"
                " document.getElementById('say').classList.contains('show');}",
                timeout=90000)
        except Exception:
            break
        tap_el(pg, "#say-next")
        pg.wait_for_timeout(400)
        if pg.evaluate("()=>((window.__mission.world.markers)||[]).length") > 0:
            break
    # CANH BAO: DUNG GAN CUNG SO DIEM. Ban cu doi dung 3 — do la ban buoc ① thang
    #   01/08/2026 (ba dom air/sea/land). `docs/decisions/005` ngay 02/08/2026 doi
    #   sang 7 CHAU LUC, nen phep kiem nay bao ve mot trang thai KHONG CON TON TAI
    #   va hong am tham tu hom do. Nay suy so diem tu chinh `CONTINENTS` trong
    #   mission-earth.html — them/bo mot chau luc khong phai sua day.
    # ⚠️ PHAI CAT DUNG KHOI `CONTINENTS`. Quet ca file thi mau `{ id: '..', lat:`
    #   bat luon mang `BIOMES` cua buoc ⑤ (cung hinh dang) -> dem ra 14 thay vi 7,
    #   va phep cho ben duoi het han. Cung bai hoc "gioi han pham vi dung bang khoi
    #   chua no" da ghi o CLAUDE.md.
    _src = _io.open(_os.path.join(_ROOT, "mission-earth.html"), encoding="utf-8").read()
    _blk = _src[_src.index("const CONTINENTS = ["):]
    _blk = _blk[:_blk.index("];")]
    want = len(re.findall(r"\{\s*id:\s*'[a-z]+'\s*,\s*lat:", _blk))
    check(want >= 3, "doc duoc so diem quet tu mission-earth.html", str(want))
    pg.wait_for_function("(n)=>window.__mission.world.markers.length===n",
                         arg=want, timeout=30000)
    check(pg.evaluate("()=>document.querySelectorAll('.e2-mk').length") == want,
          "so marker VE RA khop so diem khai", str(want))
    ids = pg.evaluate("()=>window.__mission.world.markers.map(m=>m.id)")
    hit = 0
    for mid in ids:
        sp = pg.evaluate("id=>window.__mission.world.screenOf('marker', id)", mid)
        if not (sp and sp["visible"]):
            continue
        pg.touchscreen.tap(sp["x"], sp["y"])
        pg.wait_for_timeout(500)
        hit = pg.evaluate("()=>window.__mission.world.markers.filter(m=>m.done).length")
        if hit:
            break
    check(hit >= 1, "CHAM THAT vao diem tin hieu -> duoc danh dau xong",
          f"{hit}/{want} diem")
    check(not errs, "0 loi trang", str(errs[:1])[:70])
    ctx.close()
    br.close()

print(f"\n===== {ok_n} dat / {bad_n} hong =====")
sys.exit(1 if bad_n else 0)
