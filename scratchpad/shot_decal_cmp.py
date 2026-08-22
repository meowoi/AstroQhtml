# -*- coding: utf-8 -*-
"""shot_decal_cmp.py — HINH DAN TREN TAU co GIONG O XEM TRUOC o cua hang khong?

Chu du an gui hai anh cat va noi chung khac nhau. `css/cockpit.css` khai CHUNG
mot bo rule cho ca hai cho, nen neu chung khac nhau thi khac o phan NGU CANH:
`--d` (32px vs 44px) · `transform:rotate(-8deg)` chi co o `.decal` · `overflow:
hidden` chi co o o xem truoc · va nhung do dai tinh bang `px` TUYET DOI (khong
theo `--d`) — chung khong co gian theo co.

Bo do chup TUNG cho roi phong ve cung mot khung 176x176 de so pixel. Khong doc
CSS: hai rule doc ra giong nhau van co the ra hai hinh khac nhau.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/shot_decal_cmp.py
"""
import pathlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
BASE = "http://127.0.0.1:8123"
BOX = 176


def seed(ctx, decal="decal-comet"):
    ctx.add_init_script("""(function(){
      localStorage.setItem('astroq-lang','vi');
      localStorage.setItem('astroq-asteroids','999');
      localStorage.setItem('astroq-tour-seen','1');
      localStorage.setItem('astroq-map01-seen','1');
      localStorage.setItem('astroq-user', JSON.stringify({
        uid:'u-decal', name:'Bin', pilotName:'Bin',
        character:'q', selectedCharacter:'q', avatar:'ava/q.png',
        equipped:{ cockpit:'cockpit-cyan', frame:'frame-steel', decal:'%s' },
        ship:'Luna'
      }));
    })();""" % decal)


SHOP_STUB = """(() => {
  /* Ban gia toi thieu de `shop.html` ve duoc luoi mon. ⚠️ Phai gieo bang
     `Object.defineProperty` co setter nuot loi gan — `js/firebase-auth.js` la
     module ES nen no chay SAU va se ghi de mot lời gán thường. */
  const ITEMS = [
    { id:'decal-none',   kind:'decal', price:0  },
    { id:'decal-comet',  kind:'decal', price:40 },
    { id:'cockpit-cyan', kind:'theme', price:0  },
    { id:'frame-steel',  kind:'frame', price:0  }
  ];
  const SHOP = { items:ITEMS, kinds:['theme','frame','decal'],
    defaults:{ theme:'cockpit-cyan', frame:'frame-steel', decal:'decal-none' },
    owned:['decal-comet'],
    equipped:{ theme:'cockpit-cyan', frame:'frame-steel', decal:'decal-comet' },
    ship:'Luna', wallet:{ meteors:999 } };
  const fake = {
    getShop: () => Promise.resolve({ ok:true, data:JSON.parse(JSON.stringify(SHOP)) }),
    getAchievements: () => Promise.resolve({ ok:true, data:{
        depth:'junior', ship:SHOP.ship, equipped:SHOP.equipped,
        level:{ level:3, xp:355, xpInLevel:55, xpForNext:300, pct:18 },
        progress:{ quizCorrect:0, quizAnswered:0, gamesPlayed:0, planets:[],
                   flightSeconds:0, meteorsEarned:0, bests:{}, terms:[] },
        achievements:{ summary:{ total:22, earned:0 }, badges:[] },
        wallet:SHOP.wallet } }),
    getMissions:   () => Promise.resolve({ ok:false, reason:'auth' }),
    getOnboarding: () => Promise.resolve({ ok:true, tourSeen:true, intro01Seen:true,
                                           earth1Greeted:true, map01Seen:true }),
    setOnboarding: () => Promise.resolve({ ok:true }),
    postProgress:  () => Promise.resolve({ ok:true, data:{} }),
    updateProfile: p => Promise.resolve({ ok:true, data:{ profile:p } }),
    equipCosmetic: () => Promise.resolve({ ok:true, data:{} }),
    buyCosmetic:   () => Promise.resolve({ ok:true, data:{} })
  };
  let v = fake;
  Object.defineProperty(window, 'AstroQAuth', {
    configurable:true, get:() => v, set:() => {}
  });
})();"""


def crop_shot(pg, sel, out):
    """Chup dung phan tu roi phong len BOX x BOX (NEAREST de nhin ro pixel)."""
    el = pg.query_selector(sel)
    if el is None:
        print("  [!] khong thay " + sel)
        return None
    # ⚠ Phai cuon vao khung nhin TRUOC khi chup: `page.screenshot(clip=...)` chi
    #   chup phan trong khung, nen phan tu nam duoi mep se bao "clipped area is
    #   empty" — doc ra y nhu phan tu khong ton tai.
    el.scroll_into_view_if_needed()
    pg.wait_for_timeout(250)
    b = el.bounding_box()
    # ⚠ Cat mot o VUONG quanh TAM phan tu roi moi phong len. Cat theo khung bao
    #   thi o xem truoc (132x72) bi bop vao khung vuong 176x176 va trong ra rong
    #   gap doi — mot phep so sanh tu bop meo thu no dang so.
    side = max(b["width"], b["height"]) + 22
    cx, cy = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
    pg.screenshot(path=str(out), clip={
        "x": max(0, cx - side / 2), "y": max(0, cy - side / 2),
        "width": side, "height": side})
    im = Image.open(out).convert("RGB")
    big = im.resize((BOX, BOX), Image.NEAREST)
    big.save(str(out).replace(".png", "-zoom.png"))
    print("  %-34s %dx%d -> %s" % (sel, im.width, im.height, out.name))
    return big


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()

        # ── (1) tren tau: dashboard, canh bang ten tau ──
        ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh",
                             viewport={"width": 1440, "height": 900})
        seed(ctx)
        # Chan API: khong co token thi trang van dung, va console khong co dong do.
        ctx.route("**/me/**", lambda r: r.fulfill(status=200, body="{}"))
        pg = ctx.new_page()
        pg.goto(BASE + "/dashboard.html", wait_until="load")
        pg.wait_for_timeout(1200)
        a = crop_shot(pg, ".decal", HERE / "decal-01-tau.png")
        info = pg.evaluate("""() => {
          const d = document.querySelector('.decal');
          if(!d) return null;
          const cs = getComputedStyle(d);
          const bf = getComputedStyle(d,'::before'), af = getComputedStyle(d,'::after');
          return { d: cs.getPropertyValue('--d').trim(), tf: cs.transform,
                   ov: cs.overflow,
                   head: [bf.width, bf.height, bf.boxShadow, bf.marginLeft],
                   tail: [af.width, af.height, af.transform, af.marginLeft] };
        }""")
        print("  tau :", info)
        ctx.close()

        # ── (2) o xem truoc o cua hang ──
        ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh",
                             viewport={"width": 1440, "height": 900})
        seed(ctx)
        ctx.add_init_script(SHOP_STUB)
        ctx.route("**/billing/catalog", lambda r: r.fulfill(
            status=200, content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            body='{"ok":true,"saleOpen":false,"provider":"none"}'))
        pg = ctx.new_page()
        pg.goto(BASE + "/shop.html", wait_until="load")
        pg.wait_for_timeout(1200)
        sel = ".cos-sw--decal-comet"
        assert pg.query_selector(sel) is not None, (
            "khong thay o xem truoc — ban gia AstroQAuth chua chay?")
        b = crop_shot(pg, sel, HERE / "decal-02-shop.png")
        info2 = pg.evaluate("""() => {
          const d = document.querySelector('.cos-sw--decal-comet');
          if(!d) return null;
          const cs = getComputedStyle(d);
          const bf = getComputedStyle(d,'::before'), af = getComputedStyle(d,'::after');
          return { d: cs.getPropertyValue('--d').trim(), tf: cs.transform,
                   ov: cs.overflow,
                   head: [bf.width, bf.height, bf.boxShadow, bf.marginLeft],
                   tail: [af.width, af.height, af.transform, af.marginLeft] };
        }""")
        print("  shop:", info2)
        ctx.close()
        br.close()

    if a is not None and b is not None:
        both = Image.new("RGB", (BOX * 2 + 8, BOX), (10, 14, 30))
        both.paste(a, (0, 0)); both.paste(b, (BOX + 8, 0))
        both.save(HERE / "decal-03-canh-nhau.png")
        print("  -> decal-03-canh-nhau.png  (trai = tren tau, phai = cua hang)")


if __name__ == "__main__":
    main()
