# -*- coding: utf-8 -*-
"""Do muoi viec cua 19/08/2026 tren BAN THAT (astroq.org), sau khi Pages build.

⚠️ KIEM SO HIEU BAN DUNG TRUOC MOI THU KHAC va DUNG HAN neu sai: do truoc luc
   Pages build xong thi moi ket luan deu sai, va 06/08/2026 ban that tung dung o
   ban cu gan mot ngay.
"""
import io
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

PROD = "https://astroq.org"
WANT = "2026.08.19.1"
dat = hong = 0


def chk(cond, nhan, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (nhan, ("  (%s)" % detail) if detail else ""))


def get(path):
    req = urllib.request.Request(PROD + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")


# ═════════ [0] So hieu ban dung ═════════
print("\n=== [0] So hieu ban dung ===")
st, _, ui = get("/js/ui-common.js")
have = ui.split('var VERSION = "')[1].split('"')[0] if 'var VERSION = "' in ui else "?"
chk(have == WANT, "ban that dang o ban dung %s" % WANT, have)
if have != WANT:
    print("\n>>> DUNG HAN: Pages chua build xong. Cho roi chay lai.")
    sys.exit(1)

# ═════════ [1] Cac file da sua tra ve dung noi dung ═════════
print("\n=== [1] Noi dung file tren Pages ===")
st, ct, ms = get("/js/mission-stage.js")
chk(st == 200 and "javascript" in ct, "js/mission-stage.js 200 + MIME dung", ct)
chk("liftAboveBoards(el)" in ms, "say() tu nhac box len khoi bang day")
chk("function boardSay" not in ms, "boardSay da bo")

st, _, dl = get("/js/daily.js")
chk('rule:' not in dl and 'todayIn' not in dl,
    "js/daily.js khong con hai dong giai thich luat")

st, _, lk = get("/js/locks.js")
for k in ("game:survival", "game:comms", "game:recycle", "game:units", '"lab"'):
    chk(k in lk, "js/locks.js co muc khoa %s" % k)

st, _, gm = get("/games.html")
chk(gm.count('status:"soon"') == 4, "games.html co dung 4 the khoa",
    "%d the" % gm.count('status:"soon"'))
chk("Lái tàu Luna" in gm, "mo ta Ne Thien Thach noi dung nhan vat (Luna)")
chk("Dẫn Comet" in gm, "mo ta Me Cung noi dung nhan vat (Comet)")
chk("hồi giáp" in gm, "mo ta Phong Thu noi dung phan thuong Quiz (hoi giap)")

st, _, dcss = get("/css/dashboard.css")
chk(".hud-line .led{display:inline-block" in dcss, "den `.led` co display:inline-block")
st, _, gcss = get("/css/games.css")
chk(".led.standby{background:var(--amber)" in gcss, "the game khoa co den ho phach")

st, _, lib = get("/library.html")
chk("Tổng bài viết (đang update)" in lib, "nhan o thong ke co '(dang update)'")

st, _, gr = get("/game-racer.html")
chk('spritePath: "img/luna-side.png"' in gr, "Duong Dua khai anh Luna")
st, _, gz = get("/game-maze.html")
chk('heroSprite: "img/mate/comet-idle.png"' in gz and 'gemSprite:  "img/tt.png"' in gz,
    "Me Cung khai anh Comet + Thien thach tim")
st, _, gc = get("/game-constellation.html")
chk("factArtSvg" in gc and "🔭" not in gc.split("ov-fact")[1][:400],
    "modal chom sao ve hinh, khong con emoji")

for p in ("/img/luna-side.png", "/img/mate/comet-idle.png", "/img/tt.png"):
    try:
        req = urllib.request.Request(PROD + p, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            chk(r.status == 200, "anh %s tra 200" % p, r.headers.get("Content-Type", ""))
    except Exception as e:
        chk(False, "anh %s tra 200" % p, str(e))

# ═════════ [2] Mo that tren Chromium ═════════
print("\n=== [2] Mo tren Chromium (ban that) ===")
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-tour-seen','1');"
                        "localStorage.setItem('astroq-map01-seen','1');"
                        "localStorage.setItem('astroq-asteroids','99')}catch(e){}")
    pg = ctx.new_page()
    loi, bad = [], []
    pg.on("pageerror", lambda e: loi.append(str(e)))
    pg.on("response", lambda r: bad.append("%s %s" % (r.status, r.url))
          if r.status >= 400 else None)

    # Khu Huan Luyen
    pg.goto(PROD + "/games.html", wait_until="load")
    pg.wait_for_selector(".gcard", timeout=20000)
    soon = pg.eval_on_selector_all(".gcard.soon h3", "es=>es.map(e=>e.innerText)")
    chk(len(soon) == 4, "4 the khoa hien ra", str(soon))
    chk(pg.locator(".gcard:not(.soon)").count() == 6, "6 the mo")
    ov = pg.eval_on_selector_all(".gcard.soon", """es=>es.map(e=>{
        const b=e.querySelector('.lk-badge'), s=e.querySelector('.hud-line.top .soon');
        if(!b) return -1; if(!s) return 0;
        const rb=b.getBoundingClientRect(), rs=s.getBoundingClientRect();
        const x=Math.max(0,Math.min(rb.right,rs.right)-Math.max(rb.left,rs.left));
        const y=Math.max(0,Math.min(rb.bottom,rs.bottom)-Math.max(rb.top,rs.top));
        return Math.round(x*y);})""")
    chk(all(v == 0 for v in ov), "huy hieu KHONG de len chu trang thai", str(ov))
    led = pg.eval_on_selector(".gcard.soon .hud-line.top .led",
                             "e=>{const c=getComputedStyle(e),r=e.getBoundingClientRect();"
                             "return [Math.round(r.width),c.backgroundColor,c.animationName];}")
    chk(led[0] == 8 and "251" in led[1] and led[2] == "none",
        "den the khoa: hien ra, ho phach, dung yen", str(led))

    # Dashboard: MOD-05 khoa
    pg.goto(PROD + "/dashboard.html", wait_until="load")
    pg.wait_for_selector(".card--lab", timeout=20000)
    pg.wait_for_timeout(700)
    chk(pg.locator(".card--lab.soon").count() == 1, "MOD-05 o trang thai 'soon'")
    chk((pg.locator("#lab-badge").inner_text() or "").strip() != "",
        "huy hieu MOD-05 co chu", repr(pg.locator("#lab-badge").inner_text()))
    pg.click("#lab-btn")
    pg.wait_for_selector(".lk-card", timeout=10000)
    mt = pg.eval_on_selector(".lk-card", "e=>e.innerText").lower()
    chk("xây" in mt or "dựng" in mt, "bam MOD-05 mo modal noi dang duoc xay", mt[:60])
    pg.keyboard.press("Escape")

    chk(not loi, "0 loi trang", "; ".join(loi[:2]))
    chk(not bad, "0 asset hong", "; ".join(bad[:3]))
    ctx.close()
    br.close()

print("\n===== %d dat / %d hong =====" % (dat, hong))
sys.exit(1 if hong else 0)
