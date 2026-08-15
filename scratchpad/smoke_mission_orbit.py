# -*- coding: utf-8 -*-
"""SMOKE — NHIEM VU 02 "Mat Than Tren Quy Dao" + nhanh MOT NOI CO HAI NHIEM VU.

Choi that ca 5 chang tren Chromium, va kiem dung cai nhanh re vua doi hanh vi:
tu 15/08/2026 Trai Dat co HAI nhiem vu, nen `mission-map.html` khong con vao thang
cay chang ma phai mo MAN HANH TINH (`goWorld()` — luc do "choi cai nao" moi la mot
cau hoi that).

Chay:  python -m http.server 8123      (trong AstroQhtml/)
       python scratchpad/smoke_mission_orbit.py
"""
import io, json, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
UID = "u-smoke-orbit"
STEPS = ["eyes", "bands", "night", "read", "report"]
EARTH_STEPS = ["scan", "timeline", "sun", "life", "energy", "eco", "core"]

dat = hong = 0
loi = []


def chk(dk, nhan, chi_tiet=""):
    global dat, hong
    if dk:
        dat += 1
        print("  [ok]   " + nhan + (("  " + chi_tiet) if chi_tiet else ""))
    else:
        hong += 1
        loi.append(nhan)
        print("  [FAIL] " + nhan + (("  " + chi_tiet) if chi_tiet else ""))


def seed(pg, done, lang="vi", complete=False, earth_done=None):
    """Phien dang nhap gia + cache tien do cho CA HAI nhiem vu.

    WARN `AstroQAuth` gieo bang `defineProperty` co setter NUOT loi gan: module ES
      that (`js/firebase-auth.js`) chay SAU script co dien va se ghi de mot loi gan
      thuong. Bai hoc da ghi o `smoke_onboard.py`.
    WARN Ghim `astroq-lang`: `AstroQ.getLang()` lui ve `navigator.language`, ma
      Chromium mac dinh `en-US` — khong ghim thi phan "tieng Viet" cua bo do lang le
      chay bang tieng Anh va moi phep kiem chu Viet thanh vo nghia.
    """
    ed = earth_done if earth_done is not None else EARTH_STEPS
    ms = {"uid": UID, "m": {
        "earth": {"done": ed, "total": len(EARTH_STEPS), "complete": len(ed) == len(EARTH_STEPS)},
        "orbit": {"done": done, "total": len(STEPS), "complete": complete},
    }}
    gate = {"open": ["earth", "moon"], "route": ["earth", "moon"],
            "gate": 5, "done": len(ed), "total": len(EARTH_STEPS)}
    pg.add_init_script("""
      localStorage.setItem('astroq-lang', %s);
      localStorage.setItem('astroq-user', JSON.stringify({uid:%s, name:'Smoke'}));
      localStorage.setItem('astroq-mission-steps', %s);
      localStorage.setItem('astroq-route-gate', %s);
      localStorage.setItem('astroq-asteroids', '80');
      var __auth = {
        postProgress: async function(){ return {ok:true, data:{}}; },
        missionStep:  async function(){ return {ok:true, data:{}}; },
        getMissions:  async function(){ return {ok:true, status:200, data:{
          missions:{}, route:["earth","moon"], unlockedPlaces:["earth","moon"] }}; }
      };
      Object.defineProperty(window, 'AstroQAuth', {
        configurable:true, get:function(){ return __auth; }, set:function(){}
      });
    """ % (json.dumps(lang), json.dumps(UID),
           json.dumps(json.dumps(ms)), json.dumps(json.dumps(gate))))


def newpage(ctx, done, lang="vi", **kw):
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: kw.setdefault("errs", []).append(str(e)))
    seed(pg, done, lang, **{k: v for k, v in kw.items() if k != "errs"})
    return pg


def wait_board(pg, sel, timeout=20000):
    """Cho mot bang dieu khien hien ra. Nhip cua `enter()` la: Comet noi -> MOI mo
    bang, nen bo do phai dong loi thoai roi cho TIN HIEU that, dung ngu mot khoang
    co dinh (bai hoc quy tac 6 muc 6: phep cho phai tu khai trang thai)."""
    for _ in range(40):
        pg.evaluate("() => window.__mission.say()")
        try:
            pg.wait_for_selector(sel, timeout=500)
            return True
        except Exception:
            continue
    print("      ↳ bang %s khong hien ra" % sel)
    return False


def wait_step(pg, sid, timeout=25000):
    """Cho toi dung mot chang. WARN Phep cho that bai phai TU KHAI TRANG THAI —
    `wait_for_function` het han chi noi 'co cai gi do treo'."""
    try:
        # WARN NOI THANG `sid` VAO BIEU THUC. `wait_for_function(expr, arg)` truyen
        #   theo VI TRI nem `TypeError` o ban Playwright nay — va vi `wait_step` bat
        #   moi ngoai le de tu khai trang thai, loi cua BO DO doc ra y het mot loi cua
        #   SAN PHAM ("het han cho chang 'eyes'" trong khi step DUNG la 'eyes').
        pg.wait_for_function(
            "() => window.__mission && window.__mission.step === %s" % json.dumps(sid),
            timeout=timeout)
        return True
    except Exception:
        st = pg.evaluate("() => window.__mission ? "
                         "{step:__mission.step, busy:__mission.busy, done:__mission.done} : null")
        print("      ↳ het han cho chang '%s'; trang thai = %s" % (sid, st))
        return False


def play_all(pg, errs):
    """Choi het 5 chang. Tra ve True neu toi duoc man tong ket."""
    # ① ba vet quet
    if not wait_step(pg, "eyes"):
        return False
    if not wait_board(pg, "#scan.show"):
        return False
    for sid in ("wide", "above", "pixel"):
        pg.wait_for_function("() => !window.__mission.busy", timeout=15000)
        pg.evaluate("id => window.__mission.pick({type:'marker', id})", sid)
        pg.wait_for_timeout(260)
        # the noi dung phai duoc DONG bang cach bam, khong tu dong dong
        try:
            pg.wait_for_selector("#card.show", timeout=6000)
            pg.click("#card-ok")
        except Exception:
            pass
        pg.wait_for_timeout(200)
    chk(pg.evaluate("() => window.__mission.scanned") == 3,
        "① cham du 3 vet quet",
        str(pg.evaluate("() => window.__mission.scanned")))
    pg.wait_for_timeout(400)
    pg.evaluate("() => window.__mission.say()")
    pg.wait_for_timeout(300)
    if pg.evaluate("() => window.__mission.askOpen"):
        pg.evaluate("() => window.__mission.askNext()")

    # ② bang song
    if not wait_step(pg, "bands"):
        return False
    if not wait_board(pg, "#band.show"):
        return False
    # gat sang MAU THAT truoc: khong duoc di tiep, phai gat sang MAU GIA
    pg.evaluate("() => window.__mission.band('true')")
    pg.wait_for_timeout(300)
    chk(pg.evaluate("() => window.__mission.step") == "bands",
        "② gat 'mau that' KHONG chot chang (phai gat sang mau gia)")
    pg.evaluate("() => window.__mission.band('false')")
    pg.wait_for_timeout(500)
    chk(pg.evaluate("() => document.getElementById('sim').classList.contains('show')"),
        "② nhan MO PHONG hien ra (khong de tre tuong day la anh hong ngoai that)")
    pg.evaluate("() => window.__mission.say()")
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#ask.show", timeout=10000)
    pg.evaluate("() => window.__mission.answer('nir')")
    for _ in range(3):
        pg.wait_for_timeout(400)
        pg.evaluate("() => window.__mission.say()")
    try:
        pg.wait_for_selector("#card.show", timeout=8000)
        pg.click("#card-ok")
    except Exception:
        pass
    pg.wait_for_timeout(300)
    if pg.evaluate("() => window.__mission.askOpen"):
        pg.evaluate("() => window.__mission.askNext()")

    # ③ bon dom sang
    if not wait_step(pg, "night"):
        return False
    if not wait_board(pg, "#night.show"):
        return False
    chk(pg.evaluate("() => document.getElementById('stage').classList.contains('mo-dark')"),
        "③ canh chuyen sang ban dem")
    # keo tung nhan vao dung dom bang BAN PHIM (duong nao cung phai choi duoc)
    for gid in ("city", "aurora", "fire", "moon"):
        pg.focus('#night-tray .me-gem[data-want="%s"]' % gid)
        pg.keyboard.press("Enter")          # cam len
        pg.wait_for_timeout(140)
        pg.focus('.mo-glow[data-id="%s"]' % gid)
        pg.keyboard.press("Enter")          # dat xuong
        pg.wait_for_timeout(220)
    chk(pg.evaluate("() => window.__mission.placed") == 4,
        "③ nhan dang du 4 dom sang (choi duoc bang ban phim)",
        str(pg.evaluate("() => window.__mission.placed")))
    for _ in range(2):
        pg.wait_for_timeout(400)
        try:
            if pg.is_visible("#card.show"):
                pg.click("#card-ok")
        except Exception:
            pass
        pg.evaluate("() => window.__mission.say()")
    pg.wait_for_timeout(300)
    if pg.evaluate("() => window.__mission.askOpen"):
        pg.evaluate("() => window.__mission.askNext()")

    # ④ nam meo
    if not wait_step(pg, "read"):
        return False
    if not wait_board(pg, "#tips.show"):
        return False
    # bam SAI thu tu truoc: meo 3 phai khong an
    pg.evaluate("() => window.__mission.tip(2)")
    pg.wait_for_timeout(200)
    chk(pg.evaluate("() => window.__mission.tips") == 0,
        "④ bam sai thu tu KHONG an (nam meo la mot TRINH TU)",
        str(pg.evaluate("() => window.__mission.tips")))
    n = pg.evaluate("() => window.__mission.tipTotal")
    for i in range(n):
        pg.evaluate("i => window.__mission.tip(i)", i)
        pg.wait_for_timeout(240)
    chk(pg.evaluate("() => window.__mission.tips") == n,
        "④ di het %d meo" % n, str(pg.evaluate("() => window.__mission.tips")))
    for _ in range(2):
        pg.wait_for_timeout(400)
        try:
            if pg.is_visible("#card.show"):
                pg.click("#card-ok")
        except Exception:
            pass
        pg.evaluate("() => window.__mission.say()")
    pg.wait_for_timeout(300)
    if pg.evaluate("() => window.__mission.askOpen"):
        pg.evaluate("() => window.__mission.askNext()")

    # ⑤ bao cao
    if not wait_step(pg, "report"):
        return False
    if not wait_board(pg, "#report.show"):
        return False
    pg.evaluate("() => window.__mission.send()")
    pg.wait_for_timeout(400)
    pg.evaluate("() => window.__mission.say()")
    try:
        pg.wait_for_selector("#win.show", timeout=15000)
        return True
    except Exception:
        print("      ↳ khong toi duoc man tong ket; chang =",
              pg.evaluate("() => window.__mission.step"))
        return False


with sync_playwright() as pw:
    b = pw.chromium.launch()

    # ═══════════ [1] MOT NOI CO HAI NHIEM VU ═══════════
    print("\n=== [1] Trai Dat co HAI nhiem vu: ban do khong vao thang cay chang ===")
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = newpage(ctx, [])
    pg.goto(BASE + "mission-map.html", wait_until="load")
    pg.wait_for_timeout(900)
    # WARN Cham vao TAM dia Trai Dat: vung cham la `.body::after` trong suot ≥48px,
    #   khong phai chinh cai dia (dia chi ve ra 17px tren dien thoai).
    pg.click('.body[data-id="earth"]')
    pg.wait_for_load_state("load")
    pg.wait_for_timeout(600)
    url = pg.url
    chk("mission-planet.html" in url and "w=earth" in url,
        "cham Trai Dat → MAN HANH TINH (khong vao thang cay chang)", url)

    rows = pg.eval_on_selector_all("#list .node .node-lb b", "els => els.map(e => e.textContent.trim())")
    chk(len(rows) == 2, "man hanh tinh liet ke CA HAI nhiem vu", str(rows))

    txt = pg.inner_text("body")
    chk("Hành Tinh Xanh" in txt and "Mắt Thần Trên Quỹ Đạo" in txt,
        "hien dung TEN ca hai nhiem vu (lay tu danh muc)")
    ctx.close()

    # ═══════════ [2] CAY CHANG CUA NHIEM VU 02 ═══════════
    print("\n=== [2] Cay chang cua nhiem vu 02 ===")
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = newpage(ctx, [])
    pg.goto(BASE + "mission-tree.html?m=orbit", wait_until="load")
    pg.wait_for_timeout(700)
    n = pg.eval_on_selector_all(".node, .step, button[data-step]", "els => els.length")
    chk(n >= 5, "cay chang ve du 5 chang", str(n))
    chk("Mắt Thần Trên Quỹ Đạo" in pg.inner_text("body"),
        "cay chang goi dung ten nhiem vu 02")
    ctx.close()

    # ═══════════ [3] CHOI THAT CA 5 CHANG ═══════════
    print("\n=== [3] Choi that ca 5 chang (desktop, tieng Viet) ===")
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    errs = []
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    seed(pg, [])
    pg.goto(BASE + "mission-orbit.html", wait_until="load")
    pg.wait_for_function("() => window.__mission !== undefined", timeout=25000)
    won = play_all(pg, errs)
    chk(won, "toi duoc man tong ket sau 5 chang")
    if won:
        done = pg.evaluate("() => window.__mission.done")
        chk(sorted(done) == sorted(STEPS), "da chot du 5 chang", str(done))
        title = pg.inner_text("#win-h")
        chk("QUAN SÁT" in title.upper(), "tieu de man tong ket la cua nhiem vu 02", title)
        chk(pg.inner_text("#win-badge").strip() != "—",
            "me day co ten that (khong con cho giu '—')",
            pg.inner_text("#win-badge"))
    chk(len(errs) == 0, "0 loi trang / console", "; ".join(errs[:3]))
    ctx.close()

    # ═══════════ [4] KHONG CO SERVER: KHONG BIA THUONG ═══════════
    print("\n=== [4] Mat mang: khong bia phan thuong ===")
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
    pg.route("**/me/**", lambda r: r.abort())
    pg.goto(BASE + "mission-orbit.html", wait_until="load")
    pg.wait_for_function("() => window.__mission !== undefined", timeout=25000)
    pg.evaluate("() => window.__mission.win()")
    pg.wait_for_timeout(400)
    tt = pg.inner_text("#win-rw-tt")
    chk("0" in tt, "chua doc duoc server thi hien +0, KHONG bia mot con so nao", tt)
    ctx.close()

    # ═══════════ [5] TIENG ANH ═══════════
    print("\n=== [5] Tieng Anh ===")
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = newpage(ctx, [], lang="en")
    pg.goto(BASE + "mission-orbit.html", wait_until="load")
    pg.wait_for_function("() => window.__mission !== undefined", timeout=25000)
    pg.wait_for_timeout(500)
    chk(pg.eval_on_selector("html", "e => e.lang") == "en", "the html lang=en")
    obj = pg.inner_text("#obj-h")
    chk("eyes" in obj.lower() or "ship" in obj.lower(),
        "muc tieu chang ① bang tieng Anh", obj)
    ctx.close()

    # ═══════════ [6] DIEN THOAI 390x844 ═══════════
    print("\n=== [6] Dien thoai 390x844 ===")
    ctx = b.new_context(viewport={"width": 390, "height": 844},
                        has_touch=True, is_mobile=True)
    errs6 = []
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs6.append(str(e)))
    seed(pg, [])
    pg.goto(BASE + "mission-orbit.html", wait_until="load")
    pg.wait_for_function("() => window.__mission !== undefined", timeout=25000)
    # WARN Marker chi duoc them SAU loi thoai mo man — phai dong loi thoai roi moi do,
    #   khong thi phep kiem doc ra 0 vet quet va bao hong OAN.
    wait_board(pg, "#scan.show")
    pg.wait_for_timeout(400)
    chk(pg.evaluate("() => document.documentElement.scrollWidth <= innerWidth + 1"),
        "khong tran ngang")
    # Ca ba vet quet phai NHIN THAY DUOC — bai hoc "7 chau luc khong the cung nam
    # trong khung tren dien thoai doc" cua Nhiem vu 01.
    vis = pg.evaluate("""() => {
      const out = [];
      document.querySelectorAll('.mo-swath').forEach(m => {
        const r = m.getBoundingClientRect();
        out.push([m.dataset.id, r.left > -8 && r.right < innerWidth + 8
                              && r.top > 0 && r.bottom < innerHeight]);
      });
      return out;
    }""")
    chk(len(vis) == 3 and all(v[1] for v in vis),
        "ca 3 vet quet nam trong khung o dien thoai doc", str(vis))
    chk(len(errs6) == 0, "dien thoai: 0 loi trang", "; ".join(errs6[:3]))
    ctx.close()

    b.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
if loi:
    print("Hong:")
    for x in loi:
        print("  - " + x)
sys.exit(1 if hong else 0)
