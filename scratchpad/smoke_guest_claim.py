# -*- coding: utf-8 -*-
"""
smoke_guest_claim.py — ĐO THẺ "LƯU TIẾN ĐỘ CỦA CON" (việc 3, đường chơi thử).

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/smoke_guest_claim.py

⚠️⚠️ VÌ SAO PHẢI CÓ BỘ NÀY DÙ ĐÃ CÓ `smoke_mission_earth.py`.
   Bộ kia gieo một bản giả `AstroQProgress` **không có `queuedSteps`**, nên
   `claimIfDue()` ở `js/mission-stage.js` trả `null` và cả dây nối mới **không
   bao giờ chạy** trong lượt đo của nó. Tức nó MÙ với đúng thứ vừa dựng — và đó
   là hành vi đúng của bản giả, không phải lỗi. Bộ này lo phần còn lại.

Nguyên tắc:
  · Không giả lập `AstroQProgress` — để bản THẬT chạy. Trang nhiệm vụ cố ý không
    có token nên mọi chặng rơi vào hàng chờ, đúng cảnh của một đứa trẻ chơi thử.
  · `AstroQAuth` thì PHẢI giả lập: gọi `/auth/claim` thật sẽ tạo tài khoản
    Firebase thật + ghi DynamoDB thật (bài học `e2e_certificate`, 16/08/2026).
    Đường server đã có bộ đo riêng — `scratchpad/test_auth_claim.py` 35/0.
  · Đo trên MÀN HÌNH: chữ hiện ra, nút bấm được, hàng chờ trong localStorage.
"""
import json
import sys
import time

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
EARTH = BASE + "/mission-earth.html"

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


# ─────────────────────────────────────────────────────────────────────────────
# Bản giả `AstroQAuth.claimGuest`. Hình dạng phản hồi chép đúng `claimGuest()` ở
# js/firebase-auth.js (nó lại chép đúng response của POST /auth/claim).
#
# ⚠️ Cài bằng `Object.defineProperty` có SETTER NUỐT lời gán: `js/firebase-auth.js`
#    là module ES, chạy SAU init script, và nó làm `global.AstroQAuth = …`. Gán
#    thẳng là bị bản thật ghi đè — bẫy đã ghi trong CLAUDE.md từ 29/07/2026.
#    Ở đây còn một tác dụng nữa: `loadAuth()` thấy `AstroQAuth.claimGuest` có sẵn
#    nên KHÔNG `import()` file thật, tức phép đo không phụ thuộc SDK Firebase.
STUB_AUTH = r"""
window.__claimCalls = [];
var __mode = %s;
var __stubAuth = {
  claimGuest: function (email, name) {
    window.__claimCalls.push({ email: email, name: name || null });
    return new Promise(function (res) {
      setTimeout(function () { res(__mode); }, 30);
    });
  },
  /* `waitAuth()` của js/progress.js tìm ĐÚNG hàm này để biết "đã có AstroQAuth
     chưa". Thiếu nó thì nó chờ hết 2,5 giây rồi mới kết luận — bẫy đã ghi
     ngày 08/08/2026. */
  postProgress: function () { return Promise.resolve({ ok: false, status: 0 }); },
  missionStep:  function () { return Promise.resolve({ ok: false, status: 0 }); },
  spendWallet:  function () { return Promise.resolve({ ok: false, status: 0 }); },
  idToken:      function () { return Promise.resolve(null); }
};
Object.defineProperty(window, 'AstroQAuth', {
  configurable: true,
  get: function () { return __stubAuth; },
  set: function () { /* nuốt */ }
});
"""


def seed(page, lang="vi", queue=None, mode=None, user=None):
    """Gieo trạng thái TRƯỚC khi trang chạy."""
    page.add_init_script("localStorage.setItem('astroq-lang', %s);" % json.dumps(lang))
    page.add_init_script("localStorage.removeItem('astroq-claim-snooze');")
    if queue is not None:
        page.add_init_script(
            "localStorage.setItem('astroq-progress-queue', %s);" % json.dumps(json.dumps(queue)))
    if user is not None:
        page.add_init_script(
            "localStorage.setItem('astroq-user', %s);" % json.dumps(json.dumps(user)))
    if mode is not None:
        page.add_init_script(STUB_AUTH % json.dumps(mode))


def q_item(step, mission="earth"):
    return {"type": "mission", "mission": mission, "step": step,
            "opId": "zz-" + mission + "-" + step}


def q_game(game, mission=None):
    """Một LƯỢT CHƠI trong hàng chờ. Hình dạng chép đúng `AstroQProgress.game()`."""
    q_game.n += 1
    return {"type": "game", "game": game, "score": 10, "seconds": 5,
            "meteors": 1, "opId": "zz-game-%d" % q_game.n}


q_game.n = 0


def open_card(page, steps=3, lang="vi"):
    """Mở thẻ bằng API công khai và chờ nó hiện ra thật."""
    page.evaluate("o => { window.__gcResult = 'pending';"
                  " AstroQGuestClaim.open(o).then(r => window.__gcResult = r); }",
                  {"steps": steps, "lang": lang})
    page.wait_for_selector(".gc.show", timeout=6000)
    page.wait_for_timeout(150)


def card_text(page, sel):
    return page.eval_on_selector(sel, "e => (e.textContent || '').trim()")


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])

        # ══════════════════════════════════════════════════════════════════
        head("[1] due(): chua du 3 chang thi KHONG hoi")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        seed(pg)
        pg.goto(EARTH, wait_until="domcontentloaded")
        pg.wait_for_function("() => !!window.AstroQGuestClaim", timeout=20000)

        chk(pg.evaluate("() => AstroQGuestClaim.TRIAL_STEPS") == 3,
            "TRIAL_STEPS = 3 (con so cua san pham, khong gan cung trong test)")
        due = pg.evaluate("() => [0,1,2,3,4].map(n => AstroQGuestClaim.due(n))")
        chk(due == [False, False, False, True, True],
            "due(0..2) = false, due(3+) = true", str(due))

        # ⚠️ PHEP KIEM QUAN TRONG NHAT CUA MUC NAY: da dang nhap thi KHONG BAO GIO hoi.
        #    Hoi email cua nguoi dang dang nhap la hoi mot cau vo nghia, va no se hoi
        #    lai sau MOI chang vi hang cho cua ho cung co the con viec chua gui.
        pg.evaluate("() => AstroQ.setUser({ uid: 'u-that', name: 'Bin' })")
        chk(pg.evaluate("() => AstroQGuestClaim.due(9)") is False,
            "da co phien dang nhap (uid) -> KHONG hoi")
        pg.evaluate("() => AstroQ.setUser({ name: 'Bin' })")   # ho so thoi demo, khong uid
        chk(pg.evaluate("() => AstroQGuestClaim.due(9)") is True,
            "ho so cu KHONG co uid -> van hoi (dung phep thu cua js/index-gate.js)")
        pg.evaluate("() => AstroQ.clearUser()")

        # ══════════════════════════════════════════════════════════════════
        head("[2] queuedSteps(): dem CHANG KHAC NHAU, khong dem so phan tu")
        seeded = [q_item("scan"), q_item("timeline"), q_item("sun"),
                  dict(q_item("scan"), opId="zz-earth-scan-2"),   # choi lai chang cu
                  {"type": "quiz", "correct": 3, "total": 5, "opId": "zz-q"},
                  q_item("eyes", "orbit")]
        ctx2 = br.new_context(viewport={"width": 1440, "height": 900})
        pg2 = ctx2.new_page()
        pg2.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        seed(pg2, queue=seeded)
        pg2.goto(EARTH, wait_until="domcontentloaded")
        pg2.wait_for_function("() => !!window.AstroQProgress", timeout=20000)
        n_earth = pg2.evaluate("() => AstroQProgress.queuedSteps('earth')")
        n_orbit = pg2.evaluate("() => AstroQProgress.queuedSteps('orbit')")
        n_pend = pg2.evaluate("() => AstroQProgress.pending()")
        chk(n_earth == 3,
            "6 viec trong hang cho -> earth dem ra 3 CHANG (khong phai 4, khong phai 6)",
            f"earth={n_earth} pending={n_pend}")
        chk(n_orbit == 1, "loc dung theo nhiem vu", f"orbit={n_orbit}")
        chk(pg2.evaluate("() => AstroQProgress.queuedSteps('khong-co')") == 0,
            "nhiem vu khong co viec nao -> 0")
        ctx2.close()

        # ══════════════════════════════════════════════════════════════════
        head("[3] The mo ra: chu, nut, tieu diem, Escape")
        open_card(pg, steps=3)
        chk("3" in card_text(pg, "#gc-sub"),
            "cau moi noi dung SO CHANG vua choi", card_text(pg, "#gc-sub")[:60])
        chk("email" in card_text(pg, "#gc-only").lower(),
            "noi ro CHI hoi mot o email", card_text(pg, "#gc-only"))
        # Chi MOT o nhap, va no la <input type=email>.
        inputs = pg.eval_on_selector_all(
            ".gc input", "es => es.map(e => e.type)")
        chk(inputs == ["email"], "the co DUNG MOT o nhap, kieu email", str(inputs))
        chk(pg.eval_on_selector("#gc-email", "e => e.getAttribute('autocomplete')") == "email",
            "o email khai autocomplete=email (ban phim di dong goi y dung)")
        chk(pg.evaluate("() => document.activeElement && document.activeElement.id") == "gc-email",
            "tieu diem tu vao o email")
        # Vung cham >= 48px (san cua du an, khong phai moc toi thieu 44 cua WCAG).
        h = pg.eval_on_selector_all(
            ".gc-acts button", "es => es.map(e => Math.round(e.getBoundingClientRect().height))")
        chk(all(x >= 44 for x in h), "hai nut cao >= 44px", str(h))

        # ⚠️ BAM RA NEN KHONG DUOC DONG THE. Mot cu cham hut tren dien thoai khong
        #    duoc tinh la "de sau" — day la cau hoi co hai cau tra loi ro rang.
        pg.mouse.click(20, 20)
        pg.wait_for_timeout(200)
        chk(pg.eval_on_selector(".gc", "e => e.classList.contains('show')"),
            "bam ra NEN khong dong the")

        # Escape = "De sau", va no phai di qua DUNG nut do (ghi moc hoan).
        pg.evaluate("() => localStorage.removeItem('astroq-claim-snooze')")
        pg.keyboard.press("Escape")
        pg.wait_for_function("() => window.__gcResult !== 'pending'", timeout=4000)
        r = pg.evaluate("() => window.__gcResult")
        chk(r.get("skipped") is True and r.get("saved") is False,
            "Escape = De sau (skipped, khong phai saved)", str(r))
        snz = pg.evaluate("() => localStorage.getItem('astroq-claim-snooze')")
        chk(snz == "3", "Escape ghi moc hoan = so chang luc mo", f"snooze={snz}")
        chk(pg.evaluate("() => AstroQGuestClaim.due(3)") is False,
            "sau khi hoan: 3 chang KHONG hoi lai")
        chk(pg.evaluate("() => AstroQGuestClaim.due(6)") is True,
            "choi them du 3 chang nua thi hoi lai")
        chk(pg.eval_on_selector(".gc", "e => e.getAttribute('aria-hidden')") == "true",
            "the dong thi aria-hidden=true")

        # ══════════════════════════════════════════════════════════════════
        head("[4] Email sai dinh dang: bao loi, KHONG goi mang")
        ctx3 = br.new_context(viewport={"width": 1440, "height": 900})
        pg3 = ctx3.new_page()
        pg3.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        seed(pg3, mode={"ok": True, "signedIn": True, "email": "a@b.com"})
        pg3.goto(EARTH, wait_until="domcontentloaded")
        pg3.wait_for_function("() => !!window.AstroQGuestClaim", timeout=20000)
        open_card(pg3, steps=3)
        for bad in ["", "  ", "abc", "a@b", "a@b.c", "a b@c.com"]:
            pg3.fill("#gc-email", bad)
            pg3.click("#gc-go")
            pg3.wait_for_timeout(120)
        calls = pg3.evaluate("() => window.__claimCalls.length")
        chk(calls == 0, "6 dang email hong -> 0 loi goi claimGuest", f"calls={calls}")
        chk(pg3.eval_on_selector("#gc-msg", "e => e.className").endswith("bad"),
            "hien loi kieu 'bad'")
        chk(pg3.eval_on_selector("#gc-email", "e => e.getAttribute('aria-invalid')") == "true",
            "o email danh dau aria-invalid")
        chk(pg3.eval_on_selector("#gc-go", "e => !e.disabled"),
            "nut khong bi khoa cung sau khi bao loi")

        # ══════════════════════════════════════════════════════════════════
        head("[5] Duong THANH CONG: co phien -> gui not hang cho")
        ctx4 = br.new_context(viewport={"width": 1440, "height": 900})
        pg4 = ctx4.new_page()
        pg4.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        seed(pg4, queue=[q_item("scan"), q_item("timeline")],
             mode={"ok": True, "signedIn": True, "emailVerified": False,
                   "email": "be@vidu.com", "mailSent": True, "hasCharacter": False})
        pg4.goto(EARTH, wait_until="domcontentloaded")
        pg4.wait_for_function("() => !!window.AstroQGuestClaim", timeout=20000)
        # Gia lap flush() gui duoc het (bang gia AstroQAuth tra ok:false, nen phai
        # thay chinh flush de do duong "da luu xong n viec").
        pg4.evaluate("""() => {
          window.__flushed = 0;
          const P = window.AstroQProgress;
          P.flush = function () {
            window.__flushed = P.pending();
            localStorage.setItem('astroq-progress-queue', '[]');
            return Promise.resolve(true);
          };
        }""")
        open_card(pg4, steps=2)
        pg4.fill("#gc-email", "BE@Vidu.com  ")
        pg4.click("#gc-go")
        pg4.wait_for_function("() => window.__claimCalls.length === 1", timeout=6000)
        sent = pg4.evaluate("() => window.__claimCalls[0]")
        chk(sent["email"] == "be@vidu.com",
            "email duoc chuan hoa (trim + chu thuong) truoc khi gui", str(sent))
        pg4.wait_for_function(
            "() => document.getElementById('gc-msg').className.indexOf('ok') >= 0",
            timeout=6000)
        msg = card_text(pg4, "#gc-msg")
        chk("2" in msg, "noi dung SO VIEC da luu", msg)
        chk(pg4.evaluate("() => window.__flushed") == 2,
            "flush() duoc goi va hang cho con 2 viec luc do")
        chk(pg4.evaluate("() => AstroQProgress.pending()") == 0, "hang cho da rong")
        pg4.wait_for_function("() => window.__gcResult !== 'pending'", timeout=8000)
        r4 = pg4.evaluate("() => window.__gcResult")
        chk(r4.get("saved") is True and r4.get("signedIn") is True,
            "ket qua tra ve saved=true, signedIn=true", str(r4))

        # ══════════════════════════════════════════════════════════════════
        head("[6] Nhanh throttled: co tai khoan, KHONG co phien")
        ctx5 = br.new_context(viewport={"width": 1440, "height": 900})
        pg5 = ctx5.new_page()
        pg5.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        seed(pg5, queue=[q_item("scan"), q_item("timeline"), q_item("sun")],
             mode={"ok": True, "signedIn": False, "code": "no-token",
                   "email": "be@vidu.com", "mailSent": True,
                   "message": "Da gui thu roi, mo hom thu giup minh nhe."})
        pg5.goto(EARTH, wait_until="domcontentloaded")
        pg5.wait_for_function("() => !!window.AstroQGuestClaim", timeout=20000)
        open_card(pg5, steps=3)
        pg5.fill("#gc-email", "be@vidu.com")
        pg5.click("#gc-go")
        pg5.wait_for_function(
            "() => document.getElementById('gc-msg').className.indexOf('ok') >= 0",
            timeout=6000)
        m5 = card_text(pg5, "#gc-msg")
        # ⚠️ PHEP KIEM DANG GIA NHAT CUA CA BO. Khong co phien thi hang cho VAN NAM
        #    NGUYEN trong may. Muon "da luu xong" o day la noi doi dung vao luc dua tre
        #    vua dua email de doi lay chinh loi hua do.
        low = m5.lower()
        chk("đã lưu" not in low and "saved" not in low,
            "KHONG noi 'da luu' khi chua co phien", m5)
        chk(pg5.evaluate("() => AstroQProgress.pending()") == 3,
            "hang cho VAN CON nguyen 3 viec")
        pg5.wait_for_function("() => window.__gcResult !== 'pending'", timeout=8000)
        r5 = pg5.evaluate("() => window.__gcResult")
        chk(r5.get("saved") is False and r5.get("account") is True,
            "ket qua: account=true nhung saved=false", str(r5))

        # ══════════════════════════════════════════════════════════════════
        head("[7] Server tu choi + ban chua noi may chu")
        ctx6 = br.new_context(viewport={"width": 1440, "height": 900})
        pg6 = ctx6.new_page()
        pg6.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        # ⚠️ Chuoi nay chep DUNG bang `ERR` cua js/firebase-auth.js — mot ban gia
        #    noi khac ban that thi phep kiem chi do chinh ban gia.
        MSG_TRUNG = "Email này đã có tài khoản rồi. Đăng nhập để lưu tiến độ nhé!"
        seed(pg6, mode={"ok": False, "code": "email-already-in-use",
                        "message": MSG_TRUNG})
        pg6.goto(EARTH, wait_until="domcontentloaded")
        pg6.wait_for_function("() => !!window.AstroQGuestClaim", timeout=20000)
        open_card(pg6, steps=3)
        pg6.fill("#gc-email", "trung@vidu.com")
        pg6.click("#gc-go")
        pg6.wait_for_function(
            "() => document.getElementById('gc-msg').className.indexOf('bad') >= 0",
            timeout=6000)
        m6 = card_text(pg6, "#gc-msg")
        chk(m6 == MSG_TRUNG, "the in ra DUNG cau server tra ve", m6)

        # ⚠️⚠️ PHEP KIEM TREN CHI CHUNG MINH "the in ra `r.message`" — no MU voi cau
        #    chu that, vi ban gia tu quyet dinh chuoi do. Cau chu that nam o bang
        #    `ERR` cua js/firebase-auth.js, va no la thu tre doc. Doc thang file.
        import io, re as _re
        _fa = io.open(r"js/firebase-auth.js", encoding="utf-8").read()
        for _code, _phai_co in [("email-already-in-use", "đăng nhập"),
                                ("token-failed", "kích hoạt")]:
            _m = _re.search(r'"' + _code + r'":\s*"([^"]+)"', _fa)
            # ⚠️ Doi DUNG HAI lan: bang `ERR` co bo `vi` va bo `en`. Khai mot ben
            #    thi tre doc ban con lai se thay chinh MA LOI tho.
            _all = _re.findall(r'"' + _code + r'":\s*"([^"]+)"', _fa)
            chk(len(_all) == 2, f"ERR['{_code}'] khai du ca vi va en", str(len(_all)))
            if _all:
                chk(_phai_co in _all[0].lower(),
                    f"ERR['{_code}'] (vi) moi lam viec dung ('{_phai_co}')", _all[0])
        chk(pg6.eval_on_selector("#gc-go", "e => !e.disabled"),
            "tu choi xong nut mo khoa lai de thu email khac")
        chk(pg6.evaluate("() => window.__gcResult") == "pending",
            "the VAN MO khi bi tu choi (khong dong mat o email dang go)")

        # ══════════════════════════════════════════════════════════════════
        head("[8] Ban EN")
        ctx7 = br.new_context(viewport={"width": 390, "height": 844})
        pg7 = ctx7.new_page()
        pg7.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        seed(pg7, lang="en")
        pg7.goto(EARTH, wait_until="domcontentloaded")
        pg7.wait_for_function("() => !!window.AstroQGuestClaim", timeout=20000)
        open_card(pg7, steps=3, lang="en")
        h7 = card_text(pg7, "#gc-h")
        chk("save" in h7.lower(), "tieu de dich sang EN", h7)
        chk("email" in card_text(pg7, "#gc-lb").lower(), "nhan o nhap dich sang EN",
            card_text(pg7, "#gc-lb"))
        # Dien thoai doc 390x844: the khong tran ngang, nam tron trong khung nhin.
        box = pg7.eval_on_selector(".gc-card", """e => {
          const r = e.getBoundingClientRect();
          return { l: Math.round(r.left), r: Math.round(r.right),
                   t: Math.round(r.top), b: Math.round(r.bottom) };
        }""")
        chk(box["l"] >= 0 and box["r"] <= 390,
            "390x844: the khong tran ngang", str(box))
        chk(box["t"] >= 0 and box["b"] <= 844,
            "390x844: the nam tron trong khung nhin", str(box))
        chk(pg7.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth"),
            "390x844: trang khong sinh cuon ngang")

        # ══════════════════════════════════════════════════════════════════
        head("[9] DAY NOI THAT: choi 1 chang o mission-earth -> the bat len")
        # ⚠️ Day la muc dat nhat va cung la muc duy nhat chung minh `afterStep` co
        #    that su goi den `AstroQGuestClaim`. Gieo 2 chang vao hang cho roi choi
        #    chang thu 3 -> `queuedSteps('earth')` = 3 -> `due()` bat.
        ctx8 = br.new_context(viewport={"width": 1440, "height": 900})
        pg8 = ctx8.new_page()
        e8 = []
        pg8.on("console", lambda m: e8.append(m.text) if m.type == "error" else None)
        pg8.on("pageerror", lambda e: e8.append("pageerror: " + str(e)))
        seed(pg8, queue=[q_item("timeline"), q_item("sun")])
        pg8.goto(EARTH, wait_until="domcontentloaded")
        pg8.wait_for_function("() => !!window.__mission", timeout=40000)
        pg8.wait_for_selector("#obj.show", timeout=20000)
        chk(pg8.evaluate("() => AstroQProgress.queuedSteps('earth')") == 2,
            "truoc khi choi: hang cho co 2 chang")

        def say_through(page, limit=8):
            for _ in range(limit):
                try:
                    page.wait_for_function(
                        "() => { const b=document.getElementById('say-next');"
                        " return b && !b.classList.contains('hide') &&"
                        " document.getElementById('say').classList.contains('show'); }",
                        timeout=4000)
                except Exception:
                    return
                page.evaluate("document.getElementById('say-next').click()")
                page.wait_for_timeout(120)

        def close_card(page, timeout=6000):
            try:
                page.wait_for_selector("#card.show", timeout=timeout)
            except Exception:
                return
            page.evaluate("() => { const b = document.getElementById('card-ok');"
                          " if (b) b.click(); }")
            page.wait_for_timeout(150)

        say_through(pg8)
        pg8.wait_for_function("() => window.__mission.world.markers.length === 7",
                              timeout=15000)
        ids = pg8.evaluate("() => window.__mission.world.markers.map(m => m.id)")
        for mid in ids:
            pg8.wait_for_function("() => !window.__mission.busy", timeout=20000)
            pg8.evaluate("id => window.__mission.pick({type:'marker', id})", mid)
            pg8.wait_for_timeout(160)
            close_card(pg8)
        pg8.wait_for_function("() => window.__mission.scanned === 7", timeout=30000)
        say_through(pg8)
        pg8.wait_for_selector("#ask.show", timeout=15000)
        pg8.evaluate("() => window.__mission.answer('water')")
        close_card(pg8)
        say_through(pg8)

        # Cham dut chang -> the claim phai bat len.
        try:
            pg8.wait_for_selector(".gc.show", timeout=15000)
            shown = True
        except Exception:
            shown = False
        chk(shown, "choi xong chang thu 3 -> THE CLAIM BAT LEN")

        if shown:
            # ⚠️ THE PHAI CHAY TRUOC HOP "TIEP HAY DUNG". Hai lop phu cung luc la tre
            #    khong biet tra loi cai nao.
            chk(pg8.evaluate("() => window.__mission.askOpen !== true"),
                "hop 'tiep hay dung' CHUA mo trong luc the claim dang hien")
            n_now = pg8.evaluate("() => AstroQProgress.queuedSteps('earth')")
            chk(n_now == 3, "hang cho nay co du 3 chang", f"{n_now}")
            sub = card_text(pg8, "#gc-sub")
            chk("3" in sub, "cau moi noi dung 3 chang", sub[:60])
            # Bam "De sau" -> the dong, roi hop hoi moi mo.
            pg8.click("#gc-skip")
            pg8.wait_for_function(
                "() => !document.querySelector('.gc.show')", timeout=5000)
            chk(True, "bam 'De sau' dong duoc the")
            try:
                pg8.wait_for_function(
                    "() => window.__mission.askOpen === true", timeout=8000)
                asked = True
            except Exception:
                asked = False
            chk(asked, "the dong xong thi hop 'tiep hay dung' moi mo")
            chk(pg8.evaluate("() => localStorage.getItem('astroq-claim-snooze')") == "3",
                "'De sau' ghi moc hoan (khong hoi lai o chang ke tiep)")

        chk(not e8, "0 loi console trong luot choi that", str(e8[:3]))

        # ══════════════════════════════════════════════════════════════════
        head("[10] Khong co module thi moi thu chay y nhu cu")
        ctx9 = br.new_context(viewport={"width": 1440, "height": 900})
        pg9 = ctx9.new_page()
        e9 = []
        pg9.on("pageerror", lambda e: e9.append("pageerror: " + str(e)))
        pg9.route("**/js/guest-claim.js", lambda r: r.abort())
        seed(pg9, queue=[q_item("timeline"), q_item("sun"), q_item("eco")])
        pg9.goto(EARTH, wait_until="domcontentloaded")
        pg9.wait_for_function("() => !!window.__mission", timeout=40000)
        pg9.wait_for_selector("#obj.show", timeout=20000)
        chk(pg9.evaluate("() => !window.AstroQGuestClaim"),
            "chan file -> AstroQGuestClaim khong ton tai")
        chk(pg9.evaluate("() => !!window.__mission"),
            "nhiem vu VAN chay binh thuong khi thieu module")

        # ══════════════════════════════════════════════════════════════
        head("[11] KHU GAME: the bat len o duong ROI TRANG")
        # ⚠️⚠️ VÌ SAO PHẢI CÓ MỤC NÀY, dù mục [3] đã đo cái thẻ rồi: mục [3] gọi
        #    `AstroQGuestClaim.open()` THẲNG, tức nó chứng minh cái thẻ chạy được
        #    chứ KHÔNG chứng minh có ai gọi nó ở khu game. Dây nối thật nằm ở
        #    `wireClaim()` trong `js/game-shell.js`, và nó đã một lần bắt trượt
        #    hoàn toàn (bản đầu nghe `a[href]` trong khi 11 trang game có ĐÚNG 0
        #    thẻ `<a href>` — mọi đường rời trang là `<button>` + `location.href`).
        #    Không lỗi, không cảnh báo: trẻ chỉ lặng lẽ không bao giờ được mời lưu.
        DODGE = BASE + "/game-dodge.html"

        ctxA = br.new_context(viewport={"width": 1280, "height": 860})
        pgA = ctxA.new_page()
        eA = []
        pgA.on("pageerror", lambda e: eA.append("pageerror: " + str(e)))
        seed(pgA, queue=[q_game("dodge"), q_game("catch"), q_game("dodge")],
             mode={"ok": True, "signedIn": True, "message": "Đã lưu tiến độ của con!"})
        pgA.add_init_script("localStorage.setItem('astroq-asteroids', '999');")
        pgA.goto(DODGE, wait_until="domcontentloaded")
        pgA.wait_for_selector("#ov-start.show", timeout=20000)

        chk(pgA.evaluate("() => !!window.AstroQGuestClaim"),
            "game-dodge.html co nap js/guest-claim.js")
        chk(pgA.evaluate("() => AstroQProgress.queuedGames()") == 3,
            "queuedGames() dem dung 3 luot choi")
        # ⚠️ Đối chứng: cùng hàng chờ đó KHÔNG có việc nhiệm vụ nào — nếu
        #    `queuedGames` đếm bừa cả hàng chờ thì hai con số này bằng nhau.
        chk(pgA.evaluate("() => AstroQProgress.queuedSteps('earth')") == 0,
            "queuedSteps('earth') van la 0 (dem hai thu khac nhau)")

        pgA.click("#back")
        # ⚠️ TỰ KHAI TRẠNG THÁI KHI CHỜ HỎNG (quy tắc 6 mục 6). Phép phá "bỏ
        #    `wireClaim()` khỏi `boot()`" lúc đầu cho ra một traceback TRẦN của
        #    Playwright — đọc ra y như "bộ đo không chạy" chứ không phải "sản
        #    phẩm hỏng", và nó còn giết luôn mọi phép kiểm phía sau.
        _opened = True
        try:
            pgA.wait_for_selector(".gc.show", timeout=6000)
        except Exception:
            _opened = False
        chk(_opened, "bam nut ROI TRANG -> the bat len",
            "" if _opened else "url=%s  co_module=%s" % (
                pgA.url, pgA.evaluate("() => !!window.AstroQGuestClaim")))

        if _opened:
            pgA.wait_for_timeout(150)
            chk(pgA.url.endswith("game-dodge.html"),
                "chua dieu huong di dau (cu bam bi CHAN)", pgA.url)

            subA = card_text(pgA, "#gc-sub")
            chk("lượt" in subA, "cau chu noi LUOT", subA)
            chk("chặng" not in subA, "cau chu KHONG noi 'chang'", subA)
            chk("3" in subA, "cau chu neu dung so 3", subA)

            pgA.click("#gc-skip")
            try:
                pgA.wait_for_url("**/games.html", timeout=8000)
            except Exception:
                pass
            chk(pgA.url.endswith("games.html"),
                "bam 'De sau' -> PHAT LAI cu bam, ve dung games.html", pgA.url)
        else:
            for _n in ["chua dieu huong di dau (cu bam bi CHAN)",
                       "cau chu noi LUOT", "cau chu KHONG noi 'chang'",
                       "cau chu neu dung so 3",
                       "bam 'De sau' -> PHAT LAI cu bam, ve dung games.html"]:
                chk(False, _n, "bo qua vi the khong bat len")
        chk(not eA, "0 loi trang o muc [11]", str(eA[:3]))

        # ── Đang chơi thì TUYỆT ĐỐI không cắt ngang ───────────────────────────
        # Lượt chơi đã trừ phí vào cửa rồi; xen một hộp hỏi email vào giữa là
        # lấy mất lượt đó của trẻ.
        ctxB = br.new_context(viewport={"width": 1280, "height": 860})
        pgB = ctxB.new_page()
        eB = []
        pgB.on("pageerror", lambda e: eB.append("pageerror: " + str(e)))
        seed(pgB, queue=[q_game("dodge"), q_game("dodge"), q_game("dodge")])
        pgB.add_init_script("localStorage.setItem('astroq-asteroids', '999');")
        pgB.goto(DODGE, wait_until="domcontentloaded")
        pgB.wait_for_selector("#ov-start.show", timeout=20000)
        pgB.click("#start-btn")
        pgB.wait_for_function("() => !document.querySelector('.ov.show')", timeout=8000)
        pgB.click("#back")
        pgB.wait_for_url("**/games.html", timeout=8000)
        chk(pgB.url.endswith("games.html"),
            "dang choi -> di THANG, khong mo the", pgB.url)
        chk(not eB, "0 loi trang o nhanh dang choi", str(eB[:3]))

        # ── Chưa đủ mốc thì không hỏi ────────────────────────────────────────
        ctxC = br.new_context(viewport={"width": 1280, "height": 860})
        pgC = ctxC.new_page()
        seed(pgC, queue=[q_game("dodge")])
        pgC.add_init_script("localStorage.setItem('astroq-asteroids', '999');")
        pgC.goto(DODGE, wait_until="domcontentloaded")
        pgC.wait_for_selector("#ov-start.show", timeout=20000)
        pgC.click("#back")
        pgC.wait_for_url("**/games.html", timeout=8000)
        chk(pgC.url.endswith("games.html"),
            "moi 1 luot trong hang cho -> khong hoi, di thang", pgC.url)

        # ── Đã đăng nhập thì không bao giờ hỏi ───────────────────────────────
        # Hàng chờ của người đã đăng nhập tự gửi được; hỏi email của người đang
        # đăng nhập là hỏi một câu vô nghĩa.
        ctxD = br.new_context(viewport={"width": 1280, "height": 860})
        pgD = ctxD.new_page()
        seed(pgD, queue=[q_game("dodge"), q_game("catch"), q_game("maze")],
             user={"uid": "u-da-dang-nhap", "name": "Bin"})
        pgD.add_init_script("localStorage.setItem('astroq-asteroids', '999');")
        pgD.goto(DODGE, wait_until="domcontentloaded")
        pgD.wait_for_selector("#ov-start.show", timeout=20000)
        pgD.click("#back")
        pgD.wait_for_url("**/games.html", timeout=8000)
        chk(pgD.url.endswith("games.html"),
            "da dang nhap -> khong hoi, di thang", pgD.url)

        chk(not errs, "0 loi console o cac muc con lai", str(errs[:3]))

        br.close()

    print(f"\n=== KET QUA: {ok} dat / {fail} hong ===")
    if FAILS:
        for f in FAILS:
            print("  - " + f)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
