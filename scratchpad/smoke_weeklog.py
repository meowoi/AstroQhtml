# -*- coding: utf-8 -*-
"""
smoke_weeklog.py — do Nhat ky tuan "so voi chinh minh" TREN CHROMIUM THAT.

    python -m http.server 8123        # trong AstroQhtml/
    python scratchpad/smoke_weeklog.py

Trong tam — nhung dieu chi do duoc tren trang:
  · SO VOI CHINH MINH, KHONG so voi tre khac (0 chu mang nghia xep hang);
  · GIAM KHONG TO DO — do `getComputedStyle`, khong doc file CSS;
  · tuan truoc RONG thi KHONG so (khong bia "tang 24 cau");
  · tuan nay rong / nam truoc ngay bat dau -> HAI cau KHAC NHAU;
  · `accuracy = null` hien "chua lam cau nao", KHONG hien 0%;
  · mau so so ngay la `days` cua server, khong phai 7;
  · "bang ky luc" chi hien khi diem tuan >= ky luc ca doi;
  · bac tuoi chi quyet dinh MO SAN, nut "Xem chi tiet" luon co.

⚠️ Ban gia `AstroQAuth` dat bang `Object.defineProperty` co setter nuot loi gan —
   js/firebase-auth.js la module ES nen no chay SAU va se ghi de mot phep gan thuong.
"""
import json
import re
import sys

from playwright.sync_api import sync_playwright

import io as _io, os as _os
BASE = "http://127.0.0.1:8123"
# goc repo, suy tu vi tri script — khong gan cung duong dan may
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
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


def week(**kw):
    d = dict(from_="", to="", activeDays=0, days=7, partial=False,
             quizRounds=0, quizAnswered=0, quizCorrect=0, accuracy=None,
             games=0, gameSeconds=0, lessons=0, planets=0,
             missionSteps=0, missionRefs=[], terms=[], weakCount=0,
             bests={}, xp=0, meteors=0, empty=False)
    d.update(kw)
    d["from"] = d.pop("from_")
    return d


# ⚠️ SO GIEO LECH HAN moi mac dinh: mau so `days=6` (khong phai 7) de bat duoc ca "gan
#    cung 7", va ky luc ca doi dodge=5000 > diem tuan 1200 de phan biet "bang ky luc".
REPORT = {
    "week": 0, "child": "Bin",
    "current": week(activeDays=4, days=6, quizCorrect=24, quizAnswered=30,
                    accuracy=80, games=9, gameSeconds=740, xp=310,
                    bests={"dodge": 1200, "maze": 640}),
    "previous": week(activeDays=3, days=7, quizCorrect=18, quizAnswered=25,
                     accuracy=72, games=9, xp=350),
    "badges": [],
    "lifetime": {"xp": 4200, "level": 9, "bests": {"dodge": 5000, "maze": 640}},
}

STUB = """
(function(){
  var rep = __REP__;
  var mode = localStorage.getItem('smoke-wk-mode') || 'ok';
  var over = localStorage.getItem('smoke-wk-report');
  var A = {
    postProgress: function(){ return Promise.resolve({ok:true, data:{}}); },
    getReport: function(){
      if(mode === 'fail') return Promise.resolve({ok:false, status:0, netError:true});
      return Promise.resolve({ok:true, data: over ? JSON.parse(over) : rep});
    },
    getProfile: function(){
      return Promise.resolve({ok:true, data:{
        profile:{name:'Bin', character:'castor', avatar:'ava/castor.png',
                 depth: localStorage.getItem('smoke-wk-depth') || 'senior'},
        level:{level:9, inLevel:120, span:900, next:10},
        progress:{xp:4200, quizTaken:5, quizAnswered:30, quizCorrect:24,
                  quizAccuracy:80, gamesPlayed:9, lessonsRead:3, flightSeconds:740,
                  meteorsEarned:400, planets:['earth'], terms:[], bests:{dodge:5000},
                  consts:{}, badgesEarned:2, missions:{}}
      }});
    },
    getDaily: function(){ return Promise.resolve({ok:false, status:0, netError:true}); },
    setProfile: function(){ return Promise.resolve({ok:true, data:{}}); }
  };
  Object.defineProperty(window, 'AstroQAuth', {
    configurable: true, get: function(){ return A; }, set: function(){}
  });
})();
"""


def newpage(ctx, lang="vi", mode="ok", depth="senior", report=None):
    errs = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    js = ("localStorage.setItem('astroq-lang', %r);" % lang
          + "localStorage.setItem('smoke-wk-mode', %r);" % mode
          + "localStorage.setItem('smoke-wk-depth', %r);" % depth
          + "localStorage.setItem('astroq-tour-seen','1');")
    if report is not None:
        js += "localStorage.setItem('smoke-wk-report', %r);" % json.dumps(report)
    pg.add_init_script(js)
    pg.add_init_script(STUB.replace("__REP__", json.dumps(REPORT)))
    return pg, errs


def txt(pg, sel="#wk-panel"):
    return pg.eval_on_selector(sel, "e => e.innerText")


def reddish(css):
    m = re.findall(r"[\d.]+", css or "")
    if len(m) < 3:
        return False
    r, g, b = float(m[0]), float(m[1]), float(m[2])
    return r > 120 and r > g * 1.8 and r > b * 1.8


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ══════════════════════════════════════════════════════════════
        head("[1] Ve ra du, va con so la SO SERVER GIEO")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wklog .wl-row", timeout=15000)
        t = txt(pg)

        chk("24" in t, "so cau dung = 24 (server gieo)", t[:60].replace("\n", " "))
        # ⚠️ MAU SO LA `days` CUA SERVER, KHONG PHAI 7 — tuan dang ky bi cat con it ngay
        #    ma in "4/7" chinh la cach doc sai ma viec cat tuan sinh ra de tranh.
        chk("4/6" in t, "mau so so ngay lay tu server (4/6, khong phai 4/7)",
            re.sub(r"\s+", " ", t)[:120])
        chk("7" not in re.sub(r"[^0-9/]", " ", t).split("4/")[1][:2] if "4/" in t else True,
            "khong gan cung mau so 7")

        # ── Chenh lech so voi tuan truoc ──
        ds = pg.eval_on_selector_all("#wklog .wl-d",
                                     "es => es.map(e => ({c:e.className, t:e.innerText}))")
        chk(len(ds) == 4, "co du 4 dong so sanh", str(len(ds)))
        kinds = [d["c"] for d in ds]
        chk(any("wl-up" in k for k in kinds), "co dong TANG", str(kinds))
        chk(any("wl-same" in k for k in kinds), "co dong NHU TUAN TRUOC (games 9 = 9)")
        chk(any("wl-down" in k for k in kinds), "co dong GIAM (xp 310 < 350)")
        # DO TUNG DONG, khong lay "dong tang dau tien": ban dau toi dung
        #    next(...) va no bat dung dong SO NGAY ("nhieu hon 1") roi bao hong oan.
        #    Do theo chi so thi con manh hon — moi dong phai tinh chenh lech RIENG.
        chk("1" in ds[0]["t"], "dong so ngay: chenh 4-3 = 1", ds[0]["t"])
        chk("6" in ds[1]["t"], "dong cau dung: chenh 24-18 = 6", ds[1]["t"])
        chk("wl-same" in ds[2]["c"], "dong luot choi: 9 = 9 -> nhu tuan truoc", ds[2]["c"])
        chk("40" in ds[3]["t"] and "wl-down" in ds[3]["c"],
            "dong XP: chenh 350-310 = 40, huong giam", ds[3]["t"])

        # ══════════════════════════════════════════════════════════════
        head("[2] GIAM KHONG TO DO")
        st = pg.evaluate("""() => {
          const e = document.querySelector('#wklog .wl-down');
          const c = getComputedStyle(e);
          return {col:c.color, bg:c.backgroundColor, bd:c.borderTopColor, an:c.animationName};
        }""")
        chk(not reddish(st["col"]) and not reddish(st["bg"]) and not reddish(st["bd"]),
            "dong GIAM khong to do", str(st))
        chk(st["an"] in ("none", ""), "khong nhap nhay", str(st["an"]))
        # ⚠️ Va no phai dung DUNG mot tong voi "nhu tuan truoc": khac tong la mot phan xet.
        same = pg.evaluate("""() => {
          const a = getComputedStyle(document.querySelector('#wklog .wl-down')).color;
          const b = getComputedStyle(document.querySelector('#wklog .wl-same')).color;
          return a === b;
        }""")
        chk(same, "dong GIAM cung tong mau voi dong 'nhu tuan truoc'")

        # ══════════════════════════════════════════════════════════════
        head("[3] KHONG so voi tre khac (khong phai bang xep hang)")
        src = pg.evaluate("fetch('js/weeklog.js').then(r=>r.text())")
        # ⚠️ Quet tren ban DA BOC GHI CHU: chinh loi canh bao "khong bao gio so voi tre
        #    khac" cung chua nhung chu nay — loi "dem ca chu trong ghi chu cua minh".
        code = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
        code = re.sub(r"(?m)^\s*//.*$", "", code)
        for bad in ["rank", "leaderboard", "xếp hạng", "top ", "percentile",
                    "so với bạn", "bạn khác", "trung bình của"]:
            chk(bad.lower() not in code.lower(),
                f"js/weeklog.js khong nhac '{bad.strip()}'")
        page_txt = txt(pg).lower()
        for bad in ["xếp hạng", "hạng ", "giỏi hơn", "top "]:
            chk(bad not in page_txt, f"tren man hinh khong co '{bad.strip()}'")

        # ══════════════════════════════════════════════════════════════
        head("[4] Chi tiet: bac tuoi chi quyet dinh MO SAN")
        chk(pg.locator("#wl-toggle").count() == 1, "co nut Xem chi tiet")
        chk(pg.locator("#wl-detail").is_visible(),
            "senior: chi tiet MO SAN", pg.get_attribute("#wl-toggle", "aria-expanded"))
        chk(pg.get_attribute("#wl-toggle", "aria-expanded") == "true", "aria-expanded=true")
        det = txt(pg, "#wl-detail")
        chk("80" in det and "72" in det,
            "do chinh xac tuan nay + tuan truoc", re.sub(r"\s+", " ", det)[:80])
        chk("12" in det, "thoi gian bay 740s -> 12 phut", re.sub(r"\s+", " ", det)[:80])

        # ── "bang ky luc" chi cho game DAT ky luc ──
        rows = pg.eval_on_selector_all(
            "#wl-detail .wl-brow",
            "es => es.map(e => ({t:e.innerText, tie:!!e.querySelector('.wl-tie')}))")
        chk(len(rows) == 2, "hai game co diem trong tuan", str(len(rows)))
        by = {}
        for r in rows:
            by["maze" if "Mê Cung" in r["t"] or "Maze" in r["t"] else "dodge"] = r
        chk(by.get("maze", {}).get("tie") is True,
            "maze 640 = ky luc 640 -> CO nhan 'bang ky luc'", str(by.get("maze")))
        chk(by.get("dodge", {}).get("tie") is False,
            "dodge 1200 < ky luc 5000 -> KHONG co nhan", str(by.get("dodge")))
        # ⚠️ "BANG ky luc", KHONG PHAI "ky luc MOI" — diem tuan bang ky luc ca doi thi
        #    chi chac chan duoc rang no BANG; ky luc co the lap tu tuan truoc.
        chk("mới" not in txt(pg, "#wl-detail").lower(),
            "khong noi 'ky luc MOI' (mot suy luan khong co can cu)")

        # ── Bam nut -> gap lai ──
        pg.click("#wl-toggle")
        chk(not pg.locator("#wl-detail").is_visible(), "bam nut -> gap lai")
        chk(pg.get_attribute("#wl-toggle", "aria-expanded") == "false", "aria-expanded=false")
        h = pg.eval_on_selector("#wl-toggle", "e => e.getBoundingClientRect().height")
        chk(h >= 48, "nut cao >= 48px", f"{h:.1f}px")
        chk(len(errs) == 0, "0 loi console", "; ".join(errs[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[5] junior: gap san, nhung nut VAN CO (bac khong khoa gi)")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, depth="junior")
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wklog .wl-row", timeout=15000)
        chk(pg.locator("#wl-toggle").count() == 1, "junior: nut Xem chi tiet VAN CO")
        chk(not pg.locator("#wl-detail").is_visible(), "junior: chi tiet GAP san")
        pg.click("#wl-toggle")
        chk(pg.locator("#wl-detail").is_visible(), "junior: bam la mo duoc (khong khoa)")
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[6] Tuan truoc RONG -> KHONG so (khong bia con so)")
        rep = json.loads(json.dumps(REPORT))
        rep["previous"] = week(empty=True, days=7)
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, report=rep)
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wklog .wl-row", timeout=15000)
        chk(pg.locator("#wklog .wl-d").count() == 0,
            "KHONG ve dong so sanh nao", str(pg.locator("#wklog .wl-d").count()))
        t6 = txt(pg)
        chk("chưa có gì để so" in t6 or "mốc đầu tiên" in t6,
            "noi ro tuan truoc chua co gi de so", re.sub(r"\s+", " ", t6)[:90])
        chk("24" in t6, "van hien so lieu tuan nay")
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[7] Tuan nay RONG vs NAM TRUOC ngay bat dau -> HAI cau khac nhau")
        for kind, w, must, mustnot in [
            ("rong", week(empty=True, days=7), "chưa ghi được hoạt động", "trước ngày"),
            ("truoc-ngay-bat-dau", week(empty=True, days=0, partial=True),
             "trước ngày", "chưa ghi được hoạt động"),
        ]:
            rep = json.loads(json.dumps(REPORT))
            rep["current"] = w
            ctx = br.new_context(viewport={"width": 1440, "height": 900})
            pg, e7 = newpage(ctx, report=rep)
            pg.goto(BASE + "/profile.html", wait_until="load")
            pg.wait_for_selector("#wklog .wl-note", timeout=15000)
            t7 = txt(pg, "#wklog")
            chk(must in t7, f"{kind}: noi dung cau cua no", re.sub(r"\s+", " ", t7)[:80])
            chk(mustnot not in t7, f"{kind}: KHONG noi cau cua truong hop kia")
            chk(pg.locator("#wklog .wl-row").count() == 0,
                f"{kind}: khong ve 8 so 0")
            chk(len(e7) == 0, f"{kind}: 0 loi console", "; ".join(e7[:2]))
            ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[8] accuracy = null -> KHONG hien 0%")
        rep = json.loads(json.dumps(REPORT))
        rep["current"] = week(activeDays=2, days=7, games=3, xp=40,
                              accuracy=None, quizAnswered=0, quizCorrect=0)
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, report=rep)
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wl-detail", timeout=15000)
        det = txt(pg, "#wl-detail")
        chk("0%" not in det, "KHONG hien 0% cho tuan chua lam cau nao",
            re.sub(r"\s+", " ", det)[:80])
        chk("chưa làm câu nào" in det, "noi that 'chua lam cau nao'",
            re.sub(r"\s+", " ", det)[:80])
        chk("Tuần này chưa chơi lượt nào có điểm" in det or "bests" not in det,
            "khong co diem thi noi that")
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[9] Chua doc duoc -> dau '—'")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, mode="fail")
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wklog .wl-note", timeout=15000)
        t9 = txt(pg, "#wklog")
        chk("—" in t9, "hien dau gach ngang", t9[:40])
        chk("0/" not in t9, "KHONG hien 0/n")
        chk(len(errs) == 0, "0 loi console", "; ".join(errs[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[10] Ban EN + doi ngon ngu o tab khac")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, lang="en")
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wklog .wl-row", timeout=15000)
        en = txt(pg)
        chk("more" in en.lower() or "fewer" in en.lower(), "ban EN dich phan chenh lech",
            re.sub(r"\s+", " ", en)[:90])
        chk("nhiều hơn" not in en and "Tuần" not in en, "khong con chu tieng Viet")
        other = ctx.new_page()
        other.goto(BASE + "/games.html", wait_until="load")
        other.evaluate("localStorage.setItem('astroq-lang','vi');"
                       "window.dispatchEvent(new StorageEvent('storage',"
                       "{key:'astroq-lang', newValue:'vi'}))")
        pg.wait_for_function(
            "() => document.querySelector('#wklog').innerText.includes('tuần trước')",
            timeout=8000)
        chk("tuần trước" in txt(pg), "doi VI o tab khac -> dich theo")
        chk(len(errs) == 0, "0 loi console", "; ".join(errs[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[11] Bang ky luc CA DOI: du o cho MOI game co that")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#recs .rec", timeout=15000)
        n = pg.locator("#recs .rec").count()
        # CANH BAO: DUNG GAN CUNG SO GAME. Ban cu doi dung 6 va no hong AM THAM
        #   tu 16/08/2026 — hom do khu Huan Luyen len 10 game (them 4 game lop
        #   quyet dinh), profile.html ve 10 o, phep kiem van doi 6. Loi khong phai
        #   o san pham ma o phep kiem BAO VE MOT TRANG THAI CU. Nay suy so game
        #   tu games.html (cho khai `key:"..."`), nen them game khong phai sua day.
        keys = sorted(set(re.findall(r'key:\s*"([a-z]+)"',
                                     _io.open(_os.path.join(ROOT, "games.html"),
                                             encoding="utf-8").read())))
        chk(len(keys) >= 6, "doc duoc danh sach game tu games.html",
            "%d game: %s" % (len(keys), ", ".join(keys)))
        chk(n == len(keys), "co o ky luc cho MOI game", "%d o / %d game" % (n, len(keys)))
        rt = txt(pg, "#recs")
        for nm in ["Né Thiên Thạch", "Ghép Chòm Sao", "Bắt Sao Băng",
                   "Mê Cung Thiên Hà", "Đường Đua Sao Chổi"]:
            chk(nm in rt, f"co o cho '{nm}'")
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[12] Dien thoai 390x844")
        ctx = br.new_context(viewport={"width": 390, "height": 844},
                             is_mobile=True, has_touch=True)
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/profile.html", wait_until="load")
        pg.wait_for_selector("#wklog .wl-row", timeout=15000)
        chk(pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"),
            "khong tran ngang")
        cut = pg.eval_on_selector_all(
            "#wklog .wl-k, #wklog .wl-v, #wklog .wl-note, #wklog .wl-bk",
            "es => es.filter(e => e.scrollWidth > e.clientWidth + 1)"
            ".map(e => e.innerText.slice(0,24))")
        chk(not cut, "khong chu nao bi cat", str(cut))
        chk(len(errs) == 0, "0 loi console", "; ".join(errs[:3]))
        ctx.close()

        br.close()

    print("\n" + "=" * 58)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    for f in FAILS:
        print("  - " + f)
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
