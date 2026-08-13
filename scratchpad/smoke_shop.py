"""smoke_shop.py — KHO TRANG TRI do tren Chromium THAT.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/smoke_shop.py

Do nhung thu doc code KHONG chung minh duoc:
  [1] chua dang nhap: noi that, va KHONG goi API mua nao
  [2] GIA hien ra la gia cua SERVER — gieo gia LECH HAN bang so 777 roi doi trang
      phai hien 777. Day la phep do DUY NHAT phan biet "doc server" voi "gan cung".
  [3] mua: goi API dung 1 lan, KHONG gui so tien, mua roi DEO LUON, tong den doi that
  [4] khong du tien: CHAN o client, noi ro con thieu bao nhieu, KHONG goi API
  [5] deo mon: doi ngay tren giao dien
  [6] ten phi thuyen: luu duoc, dashboard hien — chua dat thi AN
  [7] vung cham >= 48px, dien thoai 390px khong tran ngang

⚠️ Ghim `astroq-lang` (Chromium mac dinh en-US).
⚠️ `Object.defineProperty` co setter NUOT loi gan — firebase-auth.js la ES module,
   chay SAU script co dien, se ghi de ban gia neu gan thuong.
⚠️ Ban gia ghi lich su goi vao `sessionStorage` (add_init_script gieo lai moi lan
   dieu huong).
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
dat = hong = 0

# GIA GIEO LECH HAN bang bang gia thuc (Cosmetics.cs: 40..150). Neu trang gan cung
# gia thi con so 777 se khong bao gio hien ra.
FAKE_PRICE = 777

ITEMS = [
    {"id": "cockpit-cyan",   "kind": "theme", "price": 0},
    {"id": "cockpit-amber",  "kind": "theme", "price": FAKE_PRICE},
    {"id": "cockpit-violet", "kind": "theme", "price": 90},
    {"id": "frame-steel",    "kind": "frame", "price": 0},
    {"id": "frame-gold",     "kind": "frame", "price": 40},
    # Loai mon thu ba (them 13/08/2026). Co mat o day de bo do khong con gieo mot
    # cua hang chi hai loai — mot ban gia mo ta trang thai da loi thoi thi no dang do
    # mot thu khong con ton tai (bai hoc ban gia `ACH` thieu `levels`).
    {"id": "decal-none",     "kind": "decal", "price": 0},
    {"id": "decal-comet",    "kind": "decal", "price": 40},
]

KINDS = ["theme", "frame", "decal"]
DEFAULTS = {"theme": "cockpit-cyan", "frame": "frame-steel", "decal": "decal-none"}


def check(label, cond, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def mk(br, lang="vi", w=1440, h=900):
    ctx = br.new_context(viewport={"width": w, "height": h},
                         locale="vi-VN" if lang == "vi" else "en-US",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','%s')" % lang)
    ctx.route("**/billing/catalog", lambda r: r.fulfill(
        status=200, content_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
        body='{"ok":true,"saleOpen":false,"provider":"none"}'))
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    return ctx, pg


def seed_user(ctx, meteors=200, ship="", equipped=None):
    u = {"name": "Nhi", "pilotName": "Nhi", "uid": "u-test",
         "character": "m", "avatar": "ava/avam.png", "depth": "junior"}
    if ship:
        u["ship"] = ship
    if equipped:
        u["equipped"] = equipped
    ctx.add_init_script(
        "localStorage.setItem('astroq-user', JSON.stringify(%s));"
        "localStorage.setItem('astroq-asteroids','%d');" % (json.dumps(u), meteors))


def stub(ctx, meteors=200, owned=None, equipped=None, ship="", buy_ok=True, late=False):
    """Gieo ban gia `AstroQAuth`.

    `late=True` gieo no trong mot `<script type="module">` THAT SU, tuc chay sau khi
    tai lieu parse xong — dung nhip cua `js/firebase-auth.js`. Dung cho muc [10];
    xem ly do day du o do. Cung mot ban gia cho ca hai nhip, khong chep hai ban.
    """
    shop = {"items": ITEMS, "kinds": KINDS, "defaults": DEFAULTS,
            "owned": owned or [], "equipped": equipped or {}, "ship": ship,
            "wallet": {"meteors": meteors}}
    body = """(() => {
      const SHOP = %s, BUY_OK = %s;
      const push = (k, b) => {
        let a = [];
        try { a = JSON.parse(sessionStorage.getItem(k) || '[]'); } catch(e){}
        a.push(b);
        try { sessionStorage.setItem(k, JSON.stringify(a)); } catch(e){}
      };
      const fake = {
        getShop: () => Promise.resolve({ ok:true, data:JSON.parse(JSON.stringify(SHOP)) }),
        buyCosmetic: (itemId, opId) => {
          push('__buy', { itemId, opId });
          if (!BUY_OK) return Promise.resolve({ ok:false, data:{ code:'insufficient' } });
          const it = SHOP.items.find(i => i.id === itemId) || { kind:'theme', price:0 };
          SHOP.owned = SHOP.owned.concat([itemId]);
          SHOP.equipped = Object.assign({}, SHOP.equipped, { [it.kind]: itemId });
          SHOP.wallet = { meteors: SHOP.wallet.meteors - it.price };
          return Promise.resolve({ ok:true, data:{ ok:true, bought:true, item:itemId,
                     kind:it.kind, price:it.price, meteors:SHOP.wallet.meteors,
                     owned:SHOP.owned, equipped:SHOP.equipped } });
        },
        equipCosmetic: itemId => {
          push('__equip', { itemId });
          const it = SHOP.items.find(i => i.id === itemId) || { kind:'theme' };
          SHOP.equipped = Object.assign({}, SHOP.equipped, { [it.kind]: itemId });
          return Promise.resolve({ ok:true, data:{ ok:true, item:itemId, kind:it.kind,
                     owned:SHOP.owned, equipped:SHOP.equipped } });
        },
        updateProfile: p => { push('__put', p); return Promise.resolve({ ok:true, data:{ profile:p } }); },
        getAchievements: () => Promise.resolve({ ok:true, data:{
            depth:'junior', ship:SHOP.ship, equipped:SHOP.equipped,
            level:{ level:3, xp:355, xpInLevel:55, xpForNext:300, pct:18 },
            progress:{ quizCorrect:4, quizAnswered:5, gamesPlayed:1, planets:[],
                       flightSeconds:0, meteorsEarned:20, bests:{}, terms:[] },
            achievements:{ summary:{ total:22, earned:1 }, badges:[] },
            wallet:SHOP.wallet } }),
        getMissions:   () => Promise.resolve({ ok:false, reason:'auth' }),
        getOnboarding: () => Promise.resolve({ ok:true, tourSeen:true, intro01Seen:true,
                                               earth1Greeted:true, map01Seen:true }),
        setOnboarding: () => Promise.resolve({ ok:true }),
        postProgress:  () => Promise.resolve({ ok:true, data:{} })
      };
      let v = fake;
      Object.defineProperty(window, 'AstroQAuth', {
        configurable: true, get: () => v, set: () => {}
      });
    })();""" % (json.dumps(shop), "true" if buy_ok else "false")

    if not late:
        ctx.add_init_script(body)
        return

    ctx.add_init_script("""(() => {
      const s = document.createElement('script');
      s.type = 'module';
      s.textContent = %s;
      document.addEventListener('readystatechange', () => {
        if (document.readyState === 'interactive' && !window.__lateInj) {
          window.__lateInj = true;
          document.head.appendChild(s);
        }
      });
    })();""" % json.dumps(body))


def calls(pg, key):
    return pg.evaluate("(k) => { try { return JSON.parse(sessionStorage.getItem(k)||'[]'); } catch(e){ return []; } }", key)


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ═══════════════════════════════════ [1] Chua dang nhap: noi that
    print("\n[1] Chua dang nhap thi noi that, khong goi API")
    ctx, pg = mk(br)
    seed_user(ctx)
    pg.goto(BASE + "/shop.html", wait_until="load")
    pg.wait_for_timeout(700)
    check("hien dai nhac dang nhap", pg.is_visible("#offline"))
    txt = pg.inner_text("#offline")
    check("dai nhac noi ro phai dang nhap", "đăng nhập" in txt.casefold(), txt[:60])
    check("van hien luat 'chi co do trang tri'",
          "trang trí" in pg.inner_text(".shop-rule").casefold())
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═══════════════════════════ [2] GIA la gia cua SERVER (777)
    print("\n[2] GIA hien ra la gia SERVER tra, khong phai so gan cung")
    ctx, pg = mk(br)
    seed_user(ctx)
    stub(ctx)
    pg.goto(BASE + "/shop.html", wait_until="load")
    pg.wait_for_timeout(800)
    check("khong con dai nhac", not pg.is_visible("#offline"))
    n = len(pg.query_selector_all(".citem"))
    check("ve du so mon server tra", n == len(ITEMS), "%d mon" % n)
    body = pg.inner_text("#kinds")
    check("hien DUNG gia gieo lech (777)", "777" in body, body[:80].replace("\n", " · "))
    check("mon gia 0 hien 'Co san'", "Có sẵn" in body)
    # ⚠️ Suy tu `KINDS` da gieo, dung ghim con so. Ban dau dong nay ghim `== 2` nen
    #    them loai mon thu ba la no bao hong dung luc trang ve dung — loai loi "phep
    #    kiem bao ve trang thai cu" da lap nhieu lan trong du an.
    check("moi loai mon mot khoi",
          len(pg.query_selector_all("#kinds .panel")) == len(KINDS),
          "%d khoi / %d loai" % (len(pg.query_selector_all("#kinds .panel")), len(KINDS)))
    # Mon dang deo: nut bi vo hieu (khong bam duoc de mua/deo lai)
    cur = pg.query_selector('.citem.on .cbtn')
    check("mon dang dung co nut vo hieu", cur is not None and cur.get_attribute("disabled") is not None)
    bx = pg.eval_on_selector_all(".cbtn", "els => els.map(e => Math.round(e.getBoundingClientRect().height))")
    check("vung cham nut >= 48px", all(h >= 48 for h in bx), str(bx))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))

    # ═══════════════════════════════════════════ [3] Mua mot mon
    print("\n[3] Mua: goi API 1 lan, khong gui so tien, deo luon")
    root_before = pg.get_attribute("html", "data-cockpit")
    pg.click('.citem .cbtn[data-item="cockpit-violet"]')
    pg.wait_for_timeout(700)
    b = calls(pg, "__buy")
    check("goi buyCosmetic dung 1 lan", len(b) == 1, str(b))
    check("chi gui itemId + opId (KHONG gui gia)",
          b and sorted(b[0].keys()) == ["itemId", "opId"] and b[0]["itemId"] == "cockpit-violet",
          str(b[:1]))
    check("opId co that (chong tru hai lan)", b and bool(b[0]["opId"]), str(b[:1]))
    check("mua roi DEO LUON: <html data-cockpit> doi",
          pg.get_attribute("html", "data-cockpit") == "cockpit-violet",
          "%s -> %s" % (root_before, pg.get_attribute("html", "data-cockpit")))
    check("cache trong may ghi mon dang deo",
          pg.evaluate("() => ((JSON.parse(localStorage.getItem('astroq-user')||'{}')).equipped||{}).theme") == "cockpit-violet")
    check("so du tren HUD tru theo gia server",
          pg.inner_text("#bal") == "110", pg.inner_text("#bal"))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═════════════════════ [4] Khong du tien: CHAN o client, noi ro
    print("\n[4] Khong du tien: chan o client, noi con thieu bao nhieu")
    ctx, pg = mk(br)
    seed_user(ctx, meteors=5)
    stub(ctx, meteors=5)
    pg.goto(BASE + "/shop.html", wait_until="load")
    pg.wait_for_timeout(800)
    pg.click('.citem .cbtn[data-item="frame-gold"]')
    pg.wait_for_timeout(500)
    check("KHONG goi API khi biet chac thieu tien", len(calls(pg, "__buy")) == 0,
          str(calls(pg, "__buy")))
    ts = pg.inner_text("#toast")
    check("noi ro con THIEU bao nhieu", "35" in ts, ts[:60])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═══════════════════════════════════════ [5] Deo mon da co
    print("\n[5] Deo mon da co: doi ngay tren giao dien")
    ctx, pg = mk(br)
    seed_user(ctx)
    stub(ctx, owned=["frame-gold"], equipped={"theme": "cockpit-cyan", "frame": "frame-steel"})
    pg.goto(BASE + "/shop.html", wait_until="load")
    pg.wait_for_timeout(800)
    body = pg.inner_text("#kinds")
    check("mon da mua hien 'Da co'", "Đã có" in body, body[:70].replace("\n", " · "))
    pg.click('.citem .cbtn[data-item="frame-gold"]')
    pg.wait_for_timeout(600)
    e = calls(pg, "__equip")
    check("goi equipCosmetic dung 1 lan", len(e) == 1, str(e))
    check("KHONG goi buyCosmetic khi da co mon", len(calls(pg, "__buy")) == 0)
    check("<html data-frame> doi that",
          pg.get_attribute("html", "data-frame") == "frame-gold",
          str(pg.get_attribute("html", "data-frame")))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))

    # ═══════════════════════════════════ [6] Ten phi thuyen
    print("\n[6] Ten phi thuyen: luu duoc")
    pg.fill("#ship-in", "Luna Mot")
    pg.click("#ship-save")
    pg.wait_for_timeout(500)
    p = calls(pg, "__put")
    check("goi updateProfile voi { ship }", p and p[-1] == {"ship": "Luna Mot"}, str(p[-1:]))
    check("cache ghi ten tau",
          pg.evaluate("() => (JSON.parse(localStorage.getItem('astroq-user')||'{}')).ship") == "Luna Mot")
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═════════════════ [7] dashboard: tong den + ten tau
    print("\n[7] dashboard: tong den ap tu cache, ten tau hien/an dung")
    ctx, pg = mk(br)
    seed_user(ctx, ship="Luna Mot", equipped={"theme": "cockpit-rose", "frame": "frame-ice"})
    stub(ctx, ship="Luna Mot", equipped={"theme": "cockpit-rose", "frame": "frame-ice"})
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(1200)
    check("tong den ap tu cache NGAY (khong cho mang)",
          pg.get_attribute("html", "data-cockpit") == "cockpit-rose",
          str(pg.get_attribute("html", "data-cockpit")))
    check("ten tau hien o buong lai", pg.is_visible("#ship-nm")
          and "LUNA MOT" in pg.inner_text("#ship-nm").upper(), pg.inner_text("#ship-nm"))
    check("co duong vao Kho Trang Tri", pg.is_visible(".pt-shop"))
    check("duong vao tro dung shop.html", pg.get_attribute(".pt-shop", "href") == "shop.html")
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # Chua dat ten tau -> AN HAN khoi do (mot nhan trong doc ra nhu cho bi loi)
    ctx, pg = mk(br)
    seed_user(ctx)
    stub(ctx)
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(1200)
    check("chua dat ten tau thi AN khoi do", not pg.is_visible("#ship-nm"))
    check("chua mua gi thi tong den la mac dinh",
          pg.get_attribute("html", "data-cockpit") == "cockpit-cyan",
          str(pg.get_attribute("html", "data-cockpit")))
    ctx.close()

    # ═══════════════════════════════ [8] Dien thoai 390x844
    print("\n[8] Dien thoai 390x844")
    ctx, pg = mk(br, "vi", 390, 844)
    seed_user(ctx)
    stub(ctx)
    pg.goto(BASE + "/shop.html", wait_until="load")
    pg.wait_for_timeout(800)
    over = pg.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("khong tran ngang", over <= 1, "%dpx" % over)
    cols = pg.evaluate("""() => {
        const g = document.querySelector('.cgrid');
        return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : 0;
    }""")
    check("luoi mon >= 2 cot tren dien thoai", cols >= 2, "%d cot" % cols)
    ship_ov = pg.evaluate("""() => {
        const i = document.getElementById('ship-in');
        return i ? Math.round(i.scrollWidth - i.clientWidth) : -1;
    }""")
    check("o nhap ten tau khong tran", ship_ov <= 1, "%dpx" % ship_ov)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════════════════ [9] Ban EN
    print("\n[9] Ban tieng Anh")
    ctx, pg = mk(br, "en")
    seed_user(ctx)
    stub(ctx)
    pg.goto(BASE + "/shop.html", wait_until="load")
    pg.wait_for_timeout(800)
    check("tieu de dich", "Decoration" in pg.inner_text("h1"), pg.inner_text("h1"))
    check("luat dich", "Decorations only" in pg.inner_text(".shop-rule"),
          pg.inner_text(".shop-rule")[:50])
    check("nhan nut dich", "Buy" in pg.inner_text("#kinds"), "")
    check("ten mon dich", "Cyan Lights" in pg.inner_text("#kinds"))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════════════════ [10] SDK NAP MUON
    # ⚠️⚠️ PHEP KIEM NAY SINH RA TU MOT LOI THAT DA SONG TREN BAN THAT: cua hang
    # hien 0 mon voi MOI nguoi da dang nhap. `js/firebase-auth.js` la `type="module"`
    # nen luon chay SAU khoi script co dien cua trang; ban dau trang goi `load()`
    # thang o cuoi file → `window.AstroQAuth` chua ton tai → nhanh "chua dang nhap"
    # → 0 mon, va KHONG BAO GIO hoi lai. Nguoi dung thay dai "Ban can dang nhap"
    # ngay canh so du THAT cua chinh minh.
    #
    # ⚠️ VA CHINH BO NAY DA MU VOI NO: 9 muc tren deu gieo ban gia bang
    #    `add_init_script`, tuc `AstroQAuth` co san TRUOC khi trang chay — mot thu tu
    #    KHONG BAO GIO xay ra o ban that. Muc nay gieo MUON (trong mot
    #    `<script type="module">` that su) de do dung nhip that.
    print("\n[10] SDK nap MUON (nhip that cua module ES) — cua hang van phai hien mon")
    ctx, pg = mk(br)
    seed_user(ctx)
    stub(ctx, late=True)
    pg.goto(BASE + "/shop.html", wait_until="load")
    # ⚠️ BOC PHEP CHO — quy tac 6 muc 6 CLAUDE.md. Dung `wait_for_selector` tran thi
    #    khi loi quay lai, bo do NEM NGOAI LE va dung han: in ra "0 hong" va khong co
    #    dong ket qua nao, doc y het "phep kiem mu". Da gap dung canh do luc thu pha
    #    hoai muc nay.
    try:
        pg.wait_for_selector("#kinds .citem", timeout=9000)
    except Exception:
        st = pg.evaluate("() => ({auth: !!window.AstroQAuth,"
                         " banner: (document.getElementById('offline')||{}).className || '',"
                         " txt: ((document.getElementById('offline-txt')||{}).textContent||'').slice(0,50)})")
        check("SDK nap muon van hien du mon", False,
              "0 mon sau 9s · AstroQAuth=%s · dai nhac=%r" % (st["auth"], st["txt"]))
        check("KHONG con dai 'can dang nhap'", False, "dai nhac: " + str(st["banner"]))
        check("0 loi trang", not pg.perr, str(pg.perr[:1]))
        ctx.close()
        br.close()
        print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
        sys.exit(1)
    pg.wait_for_timeout(400)
    n_late = pg.locator("#kinds .citem").count()
    check("SDK nap muon van hien du mon", n_late == len(ITEMS),
          "%d / %d mon" % (n_late, len(ITEMS)))
    check("KHONG con dai 'can dang nhap'", not pg.locator("#offline").is_visible(),
          pg.inner_text("#offline")[:60])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(0 if hong == 0 else 1)
