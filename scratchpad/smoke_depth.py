"""smoke_depth.py — HAI DO SAU LOI GIAI THICH do tren Chromium THAT.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/smoke_depth.py

Do 5 thu ma doc code KHONG chung minh duoc:
  [1] select.html hoi tuoi, CHAN khi chua chon, va luu dung BAC (khong luu tuoi)
  [2] select.html ban EN
  [3] lab.html: junior thi phan sau GAP, senior thi MO SAN — va nut con o CA HAI bac
  [4] profile.html: doi bac goi API DUNG MOT LAN, bam lai o dang chon thi KHONG goi
  [5] dashboard.html: hai chieu (day len khi may nay vua khai · keo ve khi chua khai)

⚠️ Ghim `astroq-lang`: Chromium mac dinh locale en-US va mui gio khong phai Viet Nam,
   nen khong ghim thi phan "tieng Viet" cua bo do lang le chay bang tieng Anh (bai hoc
   12/08/2026).
⚠️ `Object.defineProperty` co setter NUOT loi gan — `js/firebase-auth.js` la ES module
   nen no chay SAU script co dien va se ghi de ban gia neu gan thuong.
⚠️ Ban gia ghi lich su goi vao `sessionStorage`, KHONG vao mot bien window:
   `add_init_script` gieo lai sau MOI lan dieu huong.
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
    # Chan /billing/catalog: cong 8123 khong nam trong ALLOWED_ORIGINS nen CORS chan
    # va TRINH DUYET tu ghi mot dong do vao console (bai hoc 11/08/2026).
    ctx.route("**/billing/catalog", lambda r: r.fulfill(
        status=200, content_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
        body='{"ok":true,"saleOpen":false,"provider":"none"}'))
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    return ctx, pg


def seed_user(ctx, depth=None, uid="u-test"):
    """Ho so trong may. `depth=None` = tre CHUA khai bao gio."""
    u = {"name": "Nhi", "pilotName": "Nhi", "uid": uid,
         "character": "m", "avatar": "ava/avam.png"}
    if depth:
        u["depth"] = depth
    ctx.add_init_script(
        "localStorage.setItem('astroq-user', JSON.stringify(%s));" % json.dumps(u))


def stub_auth(ctx, server_depth="", ach=None):
    """Ban gia AstroQAuth: tra `depth` cua server + ghi lai moi loi goi updateProfile."""
    payload = {
        "depth": server_depth,
        "level": {"level": 3, "xp": 355, "xpInLevel": 55, "xpForNext": 300, "pct": 18},
        "progress": {"quizCorrect": 4, "quizAnswered": 5, "gamesPlayed": 1,
                     "planets": [], "flightSeconds": 0, "meteorsEarned": 20,
                     "bests": {}, "terms": []},
        "achievements": {"summary": {"total": 22, "earned": 1}, "badges": []},
        "wallet": {"meteors": 40}
    }
    if ach:
        payload.update(ach)
    ctx.add_init_script("""(() => {
      const A = %s;
      const push = b => {
        let a = [];
        try { a = JSON.parse(sessionStorage.getItem('__put') || '[]'); } catch(e){}
        a.push(b);
        try { sessionStorage.setItem('__put', JSON.stringify(a)); } catch(e){}
      };
      const fake = {
        getAchievements: () => Promise.resolve({ ok:true, data:A }),
        getProfile:      () => Promise.resolve({ ok:true, data:{
                             profile:{ uid:'u-test', name:'Nhi', character:'m',
                                       avatar:'ava/avam.png', depth:A.depth, email:'' },
                             level:A.level, progress:A.progress, wallet:A.wallet } }),
        updateProfile:   p => { push(p); return Promise.resolve({ ok:true, data:{ profile:p } }); },
        getMissions:     () => Promise.resolve({ ok:false, reason:'auth' }),
        getOnboarding:   () => Promise.resolve({ ok:true, tourSeen:true, intro01Seen:true,
                                                 earth1Greeted:true, map01Seen:true }),
        setOnboarding:   () => Promise.resolve({ ok:true }),
        postProgress:    () => Promise.resolve({ ok:true, data:{} })
      };
      let v = fake;
      Object.defineProperty(window, 'AstroQAuth', {
        configurable: true, get: () => v, set: () => {}
      });
    })();""" % json.dumps(payload))


def puts(pg):
    return pg.evaluate("() => { try { return JSON.parse(sessionStorage.getItem('__put')||'[]'); } catch(e){ return []; } }")


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ═════════════════════════════════════════ [1] select.html — hoi tuoi (VI)
    print("\n[1] select.html: hoi tuoi, chan khi chua chon, luu BAC")
    ctx, pg = mk(br)
    pg.goto(BASE + "/select.html", wait_until="load")
    pg.wait_for_timeout(350)

    check("cau hoi tuoi hien ra", "bao nhiêu tuổi" in pg.inner_text("#age-label").casefold(),
          pg.inner_text("#age-label"))
    check("co dung 2 o tuoi", len(pg.query_selector_all(".age-btn")) == 2)
    check("nhan o tuoi la khoang tuoi", "8–10" in pg.inner_text("#age-junior")
          and "11" in pg.inner_text("#age-senior"),
          pg.inner_text("#age-junior") + " | " + pg.inner_text("#age-senior"))
    # ⚠️ Cau phu phai noi bac doi CAI GI — ten bac mot minh khong du de tre hieu.
    note0 = pg.inner_text("#age-note")
    check("cau phu noi ro doi lai duoc luc nao cung duoc",
          "lúc nào cũng được" in note0.casefold(), note0[:70])

    # Vung cham >= 48px (44 la moc TOI THIEU cua WCAG 2.5.5 — quy tac 10 muc 6)
    box = pg.eval_on_selector_all(
        ".age-btn", "els => els.map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })")
    check("vung cham o tuoi >= 48px", all(h >= 48 for _, h in box), str(box))

    # Chua chon tuoi -> KHONG duoc di dau ca
    pg.fill("#pilot-name", "Nhi")
    pg.click("#start-journey")
    pg.wait_for_timeout(900)
    check("chua chon tuoi thi KHONG dieu huong", "select.html" in pg.url, pg.url)
    check("chua chon tuoi thi hien loi nhac",
          "tuổi" in pg.inner_text("#sel-toast").casefold(), pg.inner_text("#sel-toast")[:60])
    check("chua chon tuoi thi CHUA ghi gi vao ho so",
          pg.evaluate("() => { const u = JSON.parse(localStorage.getItem('astroq-user')||'{}'); return u.depth || ''; }") == "")

    # Chon 11+ -> luu BAC (khong luu tuoi)
    pg.click("#age-senior")
    pg.wait_for_timeout(150)
    check("o dang chon duoc to sang", "active" in (pg.get_attribute("#age-senior", "class") or ""))
    note1 = pg.inner_text("#age-note")
    check("cau phu doi theo bac vua chon", note1 != note0 and len(note1) > 10, note1[:70])

    pg.click("#start-journey")
    pg.wait_for_timeout(1600)
    saved = pg.evaluate("() => JSON.parse(localStorage.getItem('astroq-user')||'{}')")
    check("luu dung bac 'senior'", saved.get("depth") == "senior", str(saved.get("depth")))
    # ⚠️ CHI luu bac, KHONG luu tuoi — du lieu ca nhan cua tre thi lay dung phan dung toi.
    check("KHONG luu tuoi/ngay sinh nao trong ho so",
          not any(k in saved for k in ("age", "birth", "birthday", "dob", "tuoi")),
          str(sorted(saved.keys())))
    check("chon roi thi di tiep duoc", "select.html" not in pg.url, pg.url)
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═════════════════════════════════════════════ [2] select.html ban EN
    print("\n[2] select.html: ban tieng Anh")
    ctx, pg = mk(br, "en")
    pg.goto(BASE + "/select.html", wait_until="load")
    pg.wait_for_timeout(350)
    check("cau hoi dich sang EN", "how old" in pg.inner_text("#age-label").casefold(),
          pg.inner_text("#age-label"))
    check("nhan o tuoi dich sang EN", "older" in pg.inner_text("#age-senior").casefold()
          or "11" in pg.inner_text("#age-senior"), pg.inner_text("#age-senior"))
    pg.fill("#pilot-name", "Nhi")
    pg.click("#start-journey")
    pg.wait_for_timeout(600)
    check("EN: chua chon tuoi thi nhac bang tieng Anh",
          "how old" in pg.inner_text("#sel-toast").casefold(),
          pg.inner_text("#sel-toast")[:60])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═════════════════════════════ [3] lab.html — bac quyet CAI MAC DINH
    print("\n[3] lab.html: junior GAP, senior MO SAN, nut con o ca hai bac")

    def run_lab(depth):
        ctx, pg = mk(br)
        seed_user(ctx, depth)
        pg.goto(BASE + "/lab.html", wait_until="load")
        pg.wait_for_timeout(400)
        pg.wait_for_selector(".lcard", timeout=8000)
        pg.click(".lcard[data-card='tower']")
        pg.wait_for_timeout(500)
        pg.click("#guess button:nth-child(2)")     # doan (sai cung khong sao)
        pg.wait_for_timeout(200)
        pg.click("#run")
        pg.wait_for_selector("#finding:not([hidden])", timeout=8000)
        pg.wait_for_timeout(200)
        return ctx, pg

    ctx, pg = run_lab("junior")
    check("junior: nut 'Tim hieu them' CO hien", pg.is_visible("#more-btn"))
    check("junior: phan sau GAP lai", not pg.is_visible("#more-box"))
    check("junior: nhan nut la 'Tim hieu them'",
          "Tìm hiểu thêm" in pg.inner_text("#more-btn"), pg.inner_text("#more-btn"))
    pg.click("#more-btn")
    pg.wait_for_timeout(200)
    check("junior: bam thi mo ra duoc (bac KHONG khoa gi)", pg.is_visible("#more-box"))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    ctx, pg = run_lab("senior")
    check("senior: phan sau MO SAN", pg.is_visible("#more-box"))
    check("senior: nut van CON (de gap lai)", pg.is_visible("#more-btn"))
    check("senior: nhan nut la 'Thu lai'",
          "Thu lại" in pg.inner_text("#more-btn"), pg.inner_text("#more-btn"))
    more = pg.inner_text("#more-box")
    check("senior: doc duoc noi dung sau (David Scott)", "David Scott" in more, more[:50])
    pg.click("#more-btn")
    pg.wait_for_timeout(200)
    check("senior: gap lai duoc", not pg.is_visible("#more-box"))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # Chua khai bao gio -> phai lui ve junior (noi don gian con hon noi kho)
    ctx, pg = run_lab(None)
    check("chua khai bac: lui ve junior (phan sau GAP)", not pg.is_visible("#more-box"))
    ctx.close()

    # ═════════════════════════ [4] profile.html — doi bac, goi API dung 1 lan
    print("\n[4] profile.html: doi bac goi API dung MOT lan")
    ctx, pg = mk(br)
    seed_user(ctx, "senior")
    stub_auth(ctx, "senior")
    pg.goto(BASE + "/profile.html", wait_until="load")
    pg.wait_for_timeout(700)

    btns = pg.query_selector_all(".depth-btn")
    check("co dung 2 o do sau", len(btns) == 2, str(len(btns)))
    check("o dang dung duoc to sang dung bac",
          "active" in (pg.get_attribute('.depth-btn[data-band="senior"]', "class") or ""),
          pg.get_attribute('.depth-btn[data-band="senior"]', "class"))
    check("moi o noi ca TEN BAC va KHOANG TUOI",
          pg.query_selector('.depth-btn[data-band="junior"] .db-nm') is not None
          and pg.query_selector('.depth-btn[data-band="junior"] .db-age') is not None)
    bx = pg.eval_on_selector_all(
        ".depth-btn", "els => els.map(e => Math.round(e.getBoundingClientRect().height))")
    check("vung cham o do sau >= 48px", all(h >= 48 for h in bx), str(bx))

    # Bam lai o DANG chon -> KHONG goi API (bai hoc doi trang phuc 29/07)
    pg.click('.depth-btn[data-band="senior"]')
    pg.wait_for_timeout(400)
    check("bam lai o dang chon: KHONG goi API", len(puts(pg)) == 0, str(puts(pg)))

    # Doi sang junior -> dung MOT loi goi, dung mot truong
    pg.click('.depth-btn[data-band="junior"]')
    pg.wait_for_timeout(600)
    p = puts(pg)
    check("doi bac: goi API dung 1 lan", len(p) == 1, str(p))
    check("goi API mang dung { depth }", p and p[0] == {"depth": "junior"}, str(p[:1]))
    check("cache trong may doi theo ngay",
          pg.evaluate("() => (JSON.parse(localStorage.getItem('astroq-user')||'{}')).depth") == "junior")
    check("o to sang doi theo ngay",
          "active" in (pg.get_attribute('.depth-btn[data-band="junior"]', "class") or ""))
    note = pg.inner_text("#depth-note")
    check("cau phu doi theo bac", len(note) > 10, note[:60])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════ [5] dashboard.html — cau noi hai chieu
    print("\n[5] dashboard.html: day len khi vua khai · keo ve khi chua khai")

    # (a) May nay vua khai (select.html ghi cache) -> DAY len server, mot lan/uid
    ctx, pg = mk(br)
    seed_user(ctx, "senior")
    stub_auth(ctx, "")                     # server chua co bac nao
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(1200)
    p = puts(pg)
    check("vua khai o may nay: DAY bac len server",
          any(x == {"depth": "senior"} for x in p), str(p))
    n1 = len(p)
    pg.reload(wait_until="load")
    pg.wait_for_timeout(1200)
    check("mo lai trang: KHONG day lai lan nua (dong dau uid)",
          len(puts(pg)) == n1, "%d -> %d" % (n1, len(puts(pg))))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # (b) May nay chua khai gi -> KEO bac cua server ve cache, KHONG day len
    ctx, pg = mk(br)
    seed_user(ctx, None)
    stub_auth(ctx, "senior")
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(1200)
    check("chua khai o may nay: KEO bac server ve cache",
          pg.evaluate("() => (JSON.parse(localStorage.getItem('astroq-user')||'{}')).depth") == "senior")
    # ⚠️ DOI PHAT BIEU 22/08/2026, KHONG NOI LONG: truoc day phep kiem nay doi
    #    "0 loi goi PUT" de do "khong day BAC len". Tu khi co cau noi NHAN VAT
    #    (`AstroQChars.sync`) thi dashboard con mot PUT hop le nua cho
    #    `character`/`avatar`/`name` — nen dem so loi goi la bao hong dung luc
    #    san pham lam dung. Dieu can bao ve khong doi: KHONG duoc gui `depth`.
    check("chua khai o may nay: KHONG day BAC len",
          all("depth" not in x for x in puts(pg)), str(puts(pg)))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(0 if hong == 0 else 1)
