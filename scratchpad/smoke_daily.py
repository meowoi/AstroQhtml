# -*- coding: utf-8 -*-
"""
smoke_daily.py — do bang "Viec hom nay" + chuoi ngay TREN CHROMIUM THAT.

    python -m http.server 8123        # trong AstroQhtml/
    python scratchpad/smoke_daily.py

Vi sao can du da co test_daily.py: bo kia chung minh SERVER tinh dung. Bo nay chung
minh nhung dieu chi do duoc tren trang —

  · so tren bang la SO SERVER GIEO (khong phai so gan cung o client);
  · viec chua xong la MOT DUONG DI toi noi lam duoc no, va bam duoc that;
  · ③ khong co dong ho dem nguoc nao tren man hinh;
  · ⑤ luat NHIN THAY DUOC (khong chi "co trong DOM");
  · ② ky luc hien ra va khong mat khi chuoi ve 1;
  · chua doc duoc thi hien dau "—", KHONG hien 0.

⚠️ BAN GIA `AstroQAuth` PHAI DAT BANG `Object.defineProperty` CO SETTER NUOT LOI GAN:
   `js/firebase-auth.js` la module ES nen no chay SAU script co dien va se ghi de mot
   phep gan thuong. Bay nay CLAUDE.md da ghi.
⚠️ BAN GIA PHAI CO `postProgress`: `waitAuth()` cua js/progress.js tim DUNG ham do de
   biet "da co AstroQAuth chua". Thieu no thi no cho het 2,5 giay roi ket luan chua
   dang nhap — bang hien dau "—" va bo do bao hong OAN.
"""
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
ok_n, bad_n = 0, 0
FAILS = []


def chk(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [ok]   {name}" + (f"  ({extra})" if extra else ""))
    else:
        bad_n += 1
        FAILS.append(name)
        print(f"  [HONG] {name}" + (f"  ({extra})" if extra else ""))


def head(t):
    print(f"\n=== {t} ===")


# ⚠️ SO GIEO LECH HAN moi con so mac dinh cua server (moc 5 -> 7, thuong 6/8/5 ->
#    41/42/43, an han 2 -> 4). Day la phep do DUY NHAT phan biet duoc "doc server" voi
#    "gan cung o client" — cung loi `smoke_ladder` gieo bang moc XP ×3 va `smoke_shop`
#    gieo gia 777.
SEED = {
    "day": "2026-08-12",
    "tasks": [
        {"id": "quiz",    "current": 1, "goal": 1, "tt": 41, "done": True,  "paid": True},
        {"id": "play",    "current": 0, "goal": 2, "tt": 42, "done": False, "paid": False},
        {"id": "correct", "current": 3, "goal": 7, "tt": 43, "done": False, "paid": False},
    ],
    "totalTt": 126,
    "gotTt": 41,
    "streak": {"cur": 6, "best": 19, "todayIn": True, "grace": 4, "graceLeft": 3},
}

STUB = """
(function(){
  var seed = __SEED__;
  var mode = localStorage.getItem('smoke-daily-mode') || 'ok';
  var A = {
    postProgress: function(){ return Promise.resolve({ok:true, data:{}}); },
    getDaily: function(){
      if(mode === 'fail') return Promise.resolve({ok:false, status:0, netError:true});
      return Promise.resolve({ok:true, data:{
        daily: JSON.parse(localStorage.getItem('smoke-daily-seed') || 'null') || seed,
        dailyPaid: 0, wallet: {meteors: 123}
      }});
    },
    getMissions: function(){
      return Promise.resolve({ok:true, data:{missions:{}, route:['earth'],
        unlockedPlaces:['earth'], gate:5, gateMet:false}});
    }
  };
  Object.defineProperty(window, 'AstroQAuth', {
    configurable: true, get: function(){ return A; }, set: function(){}
  });
})();
"""


def newpage(ctx, lang="vi", mode="ok", seed=None):
    errs = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    js = ("localStorage.setItem('astroq-lang', %r);" % lang
          + "localStorage.setItem('smoke-daily-mode', %r);" % mode
          + "localStorage.setItem('astroq-tour-seen','1');")
    if seed is not None:
        import json as _j
        js += "localStorage.setItem('smoke-daily-seed', %r);" % _j.dumps(seed)
    pg.add_init_script(js)
    pg.add_init_script(STUB.replace("__SEED__", __import__("json").dumps(SEED)))
    return pg, errs


def rows(pg):
    return pg.eval_on_selector_all(
        "#daily .dl-row",
        "es => es.map(e => ({tag:e.tagName, href:e.getAttribute('href'),"
        " txt:e.innerText, done:e.classList.contains('is-done'),"
        " h:e.getBoundingClientRect().height}))")


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ══════════════════════════════════════════════════════════════
        head("[1] Bang ve ra du, va MOI CON SO LA SO SERVER GIEO")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector("#daily .dl-row", timeout=15000)

        rs = rows(pg)
        chk(len(rs) == 3, "ve dung 3 hang viec", str(len(rs)))
        body = pg.eval_on_selector("#daily", "e => e.innerText")
        chk("41" in body and "42" in body and "43" in body,
            "phan thuong hien dung so SERVER gieo (41/42/43)",
            re.sub(r"\s+", " ", body)[:90])
        chk("0/2" in body and "3/7" in body,
            "moc hien dung so SERVER gieo (goal 2 va 7, khong phai 1 va 5)")
        chk("6" in body and "19" in body, "chuoi 6 + ky luc 19 hien ra")
        chk("126" in body and "41" in body, "tong thuong mot ngay = 126 (server gieo)")

        # ⚠️ Ten viec phai NOI SO MOC cua server, khong gan cung "5 cau".
        third = rs[2]["txt"]
        chk("7" in third, "ten viec noi dung moc server (7 cau, khong phai 5)",
            re.sub(r"\s+", " ", third)[:70])

        # ── ② Ky luc ──
        chk(pg.locator("#daily .dl-best").count() == 1, "② co o ky luc")
        chk("19" in pg.eval_on_selector("#daily .dl-best", "e => e.innerText"),
            "② ky luc hien dung 19")

        # ── ⑤ Luat NHIN THAY DUOC, va noi dung so an han cua server ──
        chk(pg.locator("#daily .dl-rule").is_visible(), "⑤ dong luat nhin thay duoc")
        rule = pg.eval_on_selector("#daily .dl-rule", "e => e.innerText")
        chk("4" in rule, "⑤ luat noi dung so ngay an han server gieo (4)",
            re.sub(r"\s+", " ", rule)[:100])
        chk("kỷ lục" in rule.lower() or "best" in rule.lower(),
            "⑤ luat noi ro ky luc duoc giu nguyen")
        grace_line = pg.eval_on_selector("#daily .dl-sub", "e => e.innerText")
        chk("3" in grace_line, "con 3 ngay an han (server gieo graceLeft=3)",
            re.sub(r"\s+", " ", grace_line)[:90])

        # ══════════════════════════════════════════════════════════════
        head("[2] ③ KHONG CO DONG HO DEM NGUOC")
        # Quet ca chu tren man hinh VA ma nguon cua bang: mot dong ho dem nguoc thi
        # hoac hien chu ("con 4 gio"), hoac phai co setInterval dem thoi gian.
        page_txt = pg.eval_on_selector("#daily-panel", "e => e.innerText").lower()
        banned_txt = ["còn 0", "giờ nữa", "hết hạn", "nửa đêm", "expires", "left today",
                      "hours left", "reset"]
        hit = [b for b in banned_txt if b in page_txt]
        chk(not hit, "③ khong co chu nao mang nghia 'sap het gio'", str(hit))
        src = pg.evaluate(
            "fetch('js/daily.js').then(r=>r.text())")
        chk("setInterval" not in src and "setTimeout" not in src,
            "③ js/daily.js khong dung dong ho nao")
        for bad in ["expiresAt", "countdown", "deadline", "midnight"]:
            chk(bad not in src, f"③ js/daily.js khong nhac '{bad}'")

        # ══════════════════════════════════════════════════════════════
        head("[3] Viec chua xong la MOT DUONG DI; viec da xong thi khong")
        chk(rs[0]["done"] and rs[0]["tag"] == "DIV",
            "viec da xong: khong phai link (khong dan di dau ca)", rs[0]["tag"])
        chk(not rs[1]["done"] and rs[1]["tag"] == "A" and rs[1]["href"],
            "viec chua xong: la link co dich", str(rs[1]["href"]))
        chk(rs[1]["href"] == "games.html", "viec 'play' dan sang Khu Huan Luyen",
            str(rs[1]["href"]))
        chk(rs[2]["href"] == "quiz.html", "viec 'correct' dan sang Quiz",
            str(rs[2]["href"]))

        # ⚠️ Do bang elementFromPoint: co the `href` dung ma van bi mot lop khac phu.
        hit_ok = pg.evaluate("""() => {
          const a = document.querySelectorAll('#daily a.dl-row')[0];
          const r = a.getBoundingClientRect();
          const el = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);
          return !!(el && a.contains(el));
        }""")
        chk(hit_ok, "hang viec chua xong THAT SU nhan duoc cu bam")

        # Vung cham >= 48px (KHONG phai 44 — xem ghi chu o css/daily.css)
        lo = min(r["h"] for r in rs)
        chk(lo >= 48, "moi hang cao >= 48px", f"thap nhat {lo:.1f}px")

        # ── Bam that -> di dung noi ──
        pg.click("#daily a.dl-row")
        pg.wait_for_url("**/games.html", timeout=15000)
        chk(pg.url.endswith("games.html"), "bam vao viec chua xong -> mo dung trang",
            pg.url)
        chk(len(errs) == 0, "0 loi console", "; ".join(errs[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[4] Khong to do / khong nhap nhay o hang chua xong")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector("#daily .dl-row", timeout=15000)
        st = pg.evaluate("""() => {
          const e = document.querySelectorAll('#daily .dl-row')[1];
          const c = getComputedStyle(e);
          return {bd: c.borderTopColor, bg: c.backgroundColor, an: c.animationName,
                  col: c.color};
        }""")
        def reddish(css):
            m = re.findall(r"[\\d.]+", css or "")
            if len(m) < 3:
                return False
            r, g, b = float(m[0]), float(m[1]), float(m[2])
            return r > 120 and r > g * 1.8 and r > b * 1.8
        chk(not reddish(st["bd"]) and not reddish(st["bg"]) and not reddish(st["col"]),
            "hang chua xong KHONG to do", str(st))
        chk(st["an"] in ("none", ""), "hang chua xong khong nhap nhay", str(st["an"]))

        # ══════════════════════════════════════════════════════════════
        head("[5] ② Chuoi ve 1 thi KY LUC VAN CON")
        broke = dict(SEED)
        broke["streak"] = {"cur": 1, "best": 30, "todayIn": True,
                           "grace": 4, "graceLeft": 4}
        ctx2 = br.new_context(viewport={"width": 1440, "height": 900})
        pg2, errs2 = newpage(ctx2, seed=broke)
        pg2.goto(BASE + "/missions.html", wait_until="load")
        pg2.wait_for_selector("#daily .dl-best", timeout=15000)
        txt = pg2.eval_on_selector("#daily", "e => e.innerText")
        chk("30" in txt, "② ky luc 30 van hien khi chuoi ve 1", txt[:70])
        chk("1" in pg2.eval_on_selector("#daily .dl-cur", "e => e.innerText"),
            "chuoi hien dung 1")
        ctx2.close()

        # ══════════════════════════════════════════════════════════════
        head("[6] Chua doc duoc -> dau '—', KHONG hien 0")
        ctx3 = br.new_context(viewport={"width": 1440, "height": 900})
        pg3, errs3 = newpage(ctx3, mode="fail")
        pg3.goto(BASE + "/missions.html", wait_until="load")
        pg3.wait_for_selector("#daily .dl-note", timeout=15000)
        t3 = pg3.eval_on_selector("#daily", "e => e.innerText")
        chk("—" in t3, "hien dau gach ngang", re.sub(r"\s+", " ", t3)[:70])
        chk("0/" not in t3, "KHONG hien tien do 0/n cho mot ngay chua doc duoc",
            re.sub(r"\s+", " ", t3)[:70])
        chk(pg3.locator("#daily .dl-note").is_visible(),
            "cau noi ro ly do NHIN THAY DUOC")
        chk(pg3.locator("#daily .dl-row").count() == 0,
            "khong ve hang viec nao khi chua co so")
        chk(len(errs3) == 0, "0 loi console o nhanh mat mang", "; ".join(errs3[:3]))
        ctx3.close()

        # ══════════════════════════════════════════════════════════════
        head("[7] Ban EN + doi ngon ngu o TAB KHAC")
        ctx4 = br.new_context(viewport={"width": 1440, "height": 900})
        pg4, errs4 = newpage(ctx4, lang="en")
        pg4.goto(BASE + "/missions.html", wait_until="load")
        pg4.wait_for_selector("#daily .dl-row", timeout=15000)
        en = pg4.eval_on_selector("#daily-panel", "e => e.innerText")
        chk("streak" in en.lower(), "ban EN dich phan chuoi", en[:60])
        chk("Chuỗi" not in en and "Kỷ lục" not in en and "Tuần" not in en,
            "ban EN khong con chu tieng Viet nao", en[:80])
        chk("Today" in en or "today" in en, "nhan bang dich sang EN")

        # Doi sang VI o mot tab khac -> bang phai dich theo (su kien `storage`)
        other = ctx4.new_page()
        other.goto(BASE + "/games.html", wait_until="load")
        other.evaluate("localStorage.setItem('astroq-lang','vi');"
                       "window.dispatchEvent(new StorageEvent('storage',"
                       "{key:'astroq-lang', newValue:'vi'}))")
        pg4.wait_for_function(
            "() => document.querySelector('#daily').innerText.includes('Chuỗi')",
            timeout=8000)
        vi = pg4.eval_on_selector("#daily-panel", "e => e.innerText")
        chk("Chuỗi" in vi, "doi VI o tab khac -> bang dich theo", vi[:60])
        chk("4" in pg4.eval_on_selector("#daily .dl-rule", "e => e.innerText"),
            "luat sau khi dich VAN noi dung so an han cua server")
        chk(len(errs4) == 0, "0 loi console", "; ".join(errs4[:3]))
        ctx4.close()

        # ══════════════════════════════════════════════════════════════
        head("[8] Dien thoai 390x844")
        ctx5 = br.new_context(viewport={"width": 390, "height": 844},
                              is_mobile=True, has_touch=True)
        pg5, errs5 = newpage(ctx5)
        pg5.goto(BASE + "/missions.html", wait_until="load")
        pg5.wait_for_selector("#daily .dl-row", timeout=15000)
        chk(pg5.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"),
            "khong tran ngang")
        cut = pg5.eval_on_selector_all(
            "#daily .dl-txt b, #daily .dl-rule, #daily .dl-sub",
            "es => es.filter(e => e.scrollWidth > e.clientWidth + 1)"
            ".map(e => e.innerText.slice(0,28))")
        chk(not cut, "khong chu nao bi cat", str(cut))
        rs5 = rows(pg5)
        lo5 = min(r["h"] for r in rs5)
        chk(lo5 >= 48, "vung cham >= 48px tren dien thoai", f"{lo5:.1f}px")
        chk(len(errs5) == 0, "0 loi console", "; ".join(errs5[:3]))
        ctx5.close()

        br.close()

    print("\n" + "=" * 58)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    if FAILS:
        for f in FAILS:
            print("  - " + f)
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
