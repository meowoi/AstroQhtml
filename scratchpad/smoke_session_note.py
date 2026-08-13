# -*- coding: utf-8 -*-
"""Dai nhac MAT PHIEN DANG NHAP o dashboard (them 13/08/2026).

Vi sao co bo do nay: 13/08/2026 do duoc vi that cua mot tai khoan la 21 tt trong khi
HUD hien 866 — lech 845. `Economy` cong LAC QUAN vao cache moi luot quiz/game roi cho
`setFromServer()` ghi de, nen hai so lech nhau nghia la moi loi goi `/me/*` da tra
`auth` tu lau: tre van choi, van thay tt tang, ma KHONG THU GI len toi server. App im
lang suot quang do.

Do TREN TRANG, khong doc code:
  [1] chua co viec cho          -> dai nhac AN HAN
  [2] mat phien + 12 viec       -> hien, noi dung 12, CO nut dang nhap lai
  [3] mat MANG + 3 viec         -> hien, KHONG co nut dang nhap (khong bao di sua
                                    mot thu khong hong)
  [4] hang cho day (bi vut viec)-> noi ra so viec da mat
  [5] gui xong                  -> dai nhac bien mat + co loi bao "da luu xong"
  [6] ban EN
  [7] dien thoai 390x844: khong tran ngang, vung cham nut >= 48px
  [8] `[hidden]` that su an duoc (bay [hidden] lan thu chin)
"""
import io
import os
import re
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:8123"
dat = hong = 0


def check(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("   [OK]   %s%s" % (name, ("  · " + info) if info else ""))
    else:
        hong += 1
        print("   [HONG] %s%s" % (name, ("  · " + info) if info else ""))


SEED = (
    "localStorage.setItem('astroq-lang','%s');"
    "localStorage.setItem('astroq-user', JSON.stringify({name:'Tre',pilotName:'Tre',"
    "uid:'u-test',character:'castor'}));"
    "localStorage.setItem('astroq-tour-seen','1');"
    "localStorage.setItem('astroq-map01-seen','1');"
    "localStorage.setItem('astroq-progress-queue', %s);"
    "localStorage.setItem('astroq-progress-dropped', '%d');"
)

# Ban gia AstroQAuth. `reason` quyet dinh CAU NOI: "auth" = mat phien, con lai = mang.
# Phai co `postProgress` — `waitAuth()` cua js/progress.js tim dung ham do de biet
# "da co AstroQAuth chua"; thieu no thi no cho het 2,5s (bay da ghi trong CLAUDE.md).
STUB = """
window.__A = {
  postProgress: function(){ return Promise.resolve({ok:%(ok)s, reason:'%(reason)s'}); },
  spendWallet:  function(){ return Promise.resolve({ok:%(ok)s, reason:'%(reason)s'}); },
  missionStep:  function(){ return Promise.resolve({ok:%(ok)s, reason:'%(reason)s'}); },
  getAchievements: function(){ return Promise.resolve({ok:%(ok)s, reason:'%(reason)s',
      data:{level:{level:3,pct:20},progress:{},achievements:{summary:{earned:1,total:22},badges:[]}}}); },
  getMissions:  function(){ return Promise.resolve({ok:false, reason:'%(reason)s'}); },
  getOnboarding:function(){ return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,
                                                    earth1Greeted:true,map01Seen:true}); }
};
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return window.__A;},set:function(){}});
"""


def q(n):
    """n viec dang xep hang cho, dang that ma js/progress.js ghi."""
    items = ",".join(
        '{"type":"quiz","correct":3,"total":5,"meteors":6,"opId":"op%d"}' % i
        for i in range(n)
    )
    return "'[%s]'" % items


def open_dash(br, lang="vi", pend=0, drop=0, ok=False, reason="auth",
              viewport=None):
    ctx = br.new_context(viewport=viewport or {"width": 1440, "height": 900})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(SEED % (lang, q(pend), drop))
    pg.add_init_script(STUB % {"ok": "true" if ok else "false", "reason": reason})
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_timeout(1800)
    return ctx, pg, errs


def read_sess(pg):
    return pg.evaluate("""() => {
      const el = document.getElementById('sess');
      const tx = document.getElementById('sess-tx');
      const go = document.getElementById('sess-go');
      const ok = document.getElementById('sess-ok');
      if(!el) return null;
      const r = el.getBoundingClientRect();
      const gr = go ? go.getBoundingClientRect() : null;
      return {
        vis: !el.hasAttribute('hidden') && r.height > 0,
        h: Math.round(r.height),
        right: Math.round(r.right),
        txt: tx ? tx.innerText : '',
        goVis: go ? (!go.hasAttribute('hidden') && gr.height > 0) : false,
        goH: gr ? Math.round(gr.height) : 0,
        goW: gr ? Math.round(gr.width) : 0,
        okVis: ok ? !ok.hasAttribute('hidden') : false,
        lost: !!el.querySelector('.lost')
      };
    }""")


def main():
    global dat, hong
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ── [1] Khong co viec cho -> AN HAN ────────────────────────────────
        print("\n[1] Khong co viec nao dang cho")
        ctx, pg, errs = open_dash(br, pend=0, ok=True, reason="")
        s = read_sess(pg)
        check("dai nhac an han khi hang cho rong", s and not s["vis"],
              "cao %dpx" % (s["h"] if s else -1))
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ── [2] Mat phien + 12 viec ───────────────────────────────────────
        print("\n[2] Mat phien dang nhap, 12 viec dang cho")
        ctx, pg, errs = open_dash(br, pend=12, reason="auth")
        s = read_sess(pg)
        check("dai nhac hien ra", s and s["vis"], "cao %dpx" % (s["h"] if s else -1))
        check("noi dung so viec THAT (12)", s and "12" in s["txt"], repr(s["txt"][:70]))
        check("co nut dang nhap lai", s and s["goVis"])
        check("KHONG co nut 'da hieu'", s and not s["okVis"])
        check("khong noi ve viec da mat", s and not s["lost"])
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ── [3] Mat MANG -> khong duoc bao di dang nhap lai ────────────────
        print("\n[3] Mat mang (phien van con), 3 viec dang cho")
        ctx, pg, errs = open_dash(br, pend=3, reason="http")
        s = read_sess(pg)
        check("dai nhac hien ra", s and s["vis"])
        check("noi dung so viec THAT (3)", s and "3" in s["txt"], repr(s["txt"][:70]))
        check("KHONG co nut dang nhap lai (khong noi sai nguyen nhan)",
              s and not s["goVis"])
        cau = (s["txt"] if s else "").lower()
        check("cau chu khong bao dang nhap lai",
              "đăng nhập" not in cau and "log back in" not in cau, repr(cau[:70]))
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ── [4] Hang cho day -> phai NOI RA so viec da mat ─────────────────
        print("\n[4] Hang cho day: 40 viec cho + 7 viec da bi vut")
        ctx, pg, errs = open_dash(br, pend=40, drop=7, reason="auth")
        s = read_sess(pg)
        check("co cau ve viec da mat", s and s["lost"], repr(s["txt"][:110]))
        check("noi dung so viec da mat (7)", s and "7" in s["txt"])
        check("van noi so viec dang cho (40)", s and "40" in s["txt"])
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ── [4b] Tran hang cho CO THAT: enqueue qua 40 thi dem duoc so bi vut
        # ⚠️ PHAI dung ban gia HONG (`ok=False`): gui duoc thi khong co gi vao hang
        #    cho ca, va phep kiem "dem dung so bi vut" se do mot thu chua xay ra.
        # ⚠️ `report()` la BAT DONG BO (`waitAuth` -> `send`), nen phai `await`;
        #    doc ngay la doc truoc khi viec kip vao hang cho.
        print("\n[4b] js/progress.js dem duoc so viec bi vut khi tran")
        ctx, pg, errs = open_dash(br, pend=0, reason="auth")
        r = pg.evaluate("""async () => {
          localStorage.setItem('astroq-progress-dropped','0');
          localStorage.setItem('astroq-progress-queue','[]');
          const before = AstroQProgress.dropped();
          // 45 viec, tran la 40 -> phai vut 5
          for(let i=0;i<45;i++) await AstroQProgress.lesson('bai-'+i);
          return {before, pend: AstroQProgress.pending(), drop: AstroQProgress.dropped()};
        }""")
        check("truoc do chua vut viec nao", r["before"] == 0, str(r["before"]))
        check("hang cho dung bang tran (40)", r["pend"] == 40, str(r["pend"]))
        check("dem dung so viec bi vut (5)", r["drop"] == 5, str(r["drop"]))
        r2 = pg.evaluate("() => { AstroQProgress.clearDropped(); return AstroQProgress.dropped(); }")
        check("clearDropped() xoa duoc bo dem", r2 == 0, str(r2))
        ctx.close()

        # ── [5] Gui xong -> dai nhac bien mat + co loi bao ─────────────────
        print("\n[5] Gui xong hang cho")
        ctx, pg, errs = open_dash(br, pend=5, ok=True, reason="")
        s0 = read_sess(pg)
        # ⚠️ TOAST CHI SONG 3,2 GIAY. Doi mot khoang co dinh roi moi doc la doc SAU
        #    khi no da tat — lan dau tôi lam thế và no bao "khong co loi bao" oan.
        #    Phai RINH: doc lien tuc roi giu lai lan xuat hien dau tien.
        tst = None
        for _ in range(40):
            cur = pg.evaluate("""() => {
              const el = document.getElementById('toast');
              return el ? {show: el.classList.contains('show'), txt: el.innerText} : null;
            }""")
            if cur and cur["show"] and cur["txt"].strip():
                tst = cur
                break
            pg.wait_for_timeout(150)
        s1 = read_sess(pg)
        pend = pg.evaluate("() => AstroQProgress.pending()")
        check("hang cho da rong", pend == 0, str(pend))
        check("dai nhac da bien mat", s1 and not s1["vis"])
        check("co loi bao 'da luu xong'", tst and tst["show"], repr((tst or {}).get("txt", "")[:60]))
        check("loi bao noi dung so viec (5)", tst and "5" in (tst["txt"] or ""))
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ── [6] Ban EN ────────────────────────────────────────────────────
        print("\n[6] Ban tieng Anh")
        ctx, pg, errs = open_dash(br, lang="en", pend=9, reason="auth")
        s = read_sess(pg)
        txt = (s["txt"] if s else "")
        check("dai nhac hien ra", s and s["vis"])
        check("da dich sang tieng Anh", "mothership" in txt.lower(), repr(txt[:70]))
        check("khong con chu tieng Viet", "tàu mẹ" not in txt)
        check("nhan nut dich theo",
              "log back in" in pg.inner_text("#sess-go").lower(),
              pg.inner_text("#sess-go"))
        # Doi ngon ngu o tab khac -> phai dich theo ma khong mat con so
        pg.evaluate("""() => {
          localStorage.setItem('astroq-lang','vi');
          window.dispatchEvent(new StorageEvent('storage',{key:'astroq-lang',newValue:'vi'}));
        }""")
        pg.wait_for_timeout(400)
        s2 = read_sess(pg)
        check("doi ngon ngu o tab khac thi dich theo",
              s2 and "tàu mẹ" in s2["txt"], repr((s2 or {}).get("txt", "")[:70]))
        check("van giu dung con so sau khi doi ngon ngu", s2 and "9" in s2["txt"])
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ── [7] Dien thoai 390x844 ────────────────────────────────────────
        print("\n[7] Dien thoai 390x844")
        ctx, pg, errs = open_dash(br, pend=12, reason="auth",
                                  viewport={"width": 390, "height": 844})
        s = read_sess(pg)
        over = pg.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
        check("dai nhac hien ra", s and s["vis"])
        check("khong tran ngang", over <= 0, "%dpx" % over)
        check("vung cham nut >= 48px (luat 10 muc 6)", s and s["goH"] >= 48,
              "%dx%d" % ((s or {}).get("goW", 0), (s or {}).get("goH", 0)))
        check("nut nam trong khung nhin", s and s["right"] <= 390, str((s or {}).get("right")))
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ── [8] Bay [hidden] — lan thu chin ───────────────────────────────
        print("\n[8] `[hidden]` that su an duoc")
        ctx, pg, errs = open_dash(br, pend=0, ok=True, reason="")
        r = pg.evaluate("""() => {
          const el = document.getElementById('sess');
          const go = document.getElementById('sess-go');
          const ok = document.getElementById('sess-ok');
          const d = n => getComputedStyle(n).display;
          return {sess: d(el), go: d(go), ok: d(ok)};
        }""")
        check(".sess[hidden] -> display:none", r["sess"] == "none", r["sess"])
        check(".sess .go[hidden] -> display:none (nut link)", r["go"] == "none", r["go"])
        check(".sess .go[hidden] -> display:none (nut bam)", r["ok"] == "none", r["ok"])
        ctx.close()

        # ── [8b] Nut "Da hieu" xoa duoc tin viec da mat ────────────────────
        print("\n[8b] Nut 'Da hieu' khi chi con tin viec da mat")
        ctx, pg, errs = open_dash(br, pend=0, drop=4, ok=True, reason="")
        s = read_sess(pg)
        check("dai nhac van hien (con tin viec da mat)", s and s["vis"])
        check("noi so viec da mat (4)", s and "4" in s["txt"], repr((s or {}).get("txt", "")[:80]))
        check("hien nut 'Da hieu'", s and s["okVis"])
        check("KHONG hien nut dang nhap lai", s and not s["goVis"])
        pg.click("#sess-ok")
        pg.wait_for_timeout(300)
        s2 = read_sess(pg)
        drop = pg.evaluate("() => AstroQProgress.dropped()")
        check("bam xong thi dai nhac an", s2 and not s2["vis"])
        check("bo dem viec da mat ve 0", drop == 0, str(drop))
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        br.close()

    # ── [9] Doc ma nguon: khoa i18n va cac luat da chot ───────────────────
    print("\n[9] Ma nguon")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dash = io.open(os.path.join(root, "dashboard.html"), encoding="utf-8").read()
    css = io.open(os.path.join(root, "css", "dashboard.css"), encoding="utf-8").read()
    prog = io.open(os.path.join(root, "js", "progress.js"), encoding="utf-8").read()

    KEYS = ["sess_auth", "sess_auth1", "sess_net", "sess_net1", "sess_lost",
            "sess_done", "sess_btn", "sess_ok", "sess_unit", "sess_unit1"]
    for k in KEYS:
        n = len(re.findall(r"\b%s\s*:" % k, dash))
        check("khoa i18n `%s` co o CA vi va en" % k, n == 2, "%d lan khai" % n)

    # ⚠️ QUET TREN CODE DA BOC CHU THICH — lan chay dau phep kiem nay bao vi pham,
    #    thu pham la chinh doan ghi chu GIAI THICH vi sao khong ghep dong. Loi "dem
    #    ca chu trong ghi chu cua chinh minh" da lap lai qua nhieu lan de con quen.
    code = re.sub(r"/\*.*?\*/", " ", dash, flags=re.S)
    code = re.sub(r"(?m)^\s*//.*$", " ", code)
    code = re.sub(r"<!--.*?-->", " ", code, flags=re.S)
    # Khoa ghep dong la khoa vo hinh voi bo kiem i18n (bai hoc s1_hit1/2/3)
    check("khong ghep dong t(\"sess_\"+...)",
          'sess_"+' not in code and "sess_'+" not in code)

    # Khong duoc dem nguoc / nhap nhay: day la loi nhac, khong phai han chot
    m = re.search(r"\.sess\{[^}]*\}", css)
    check("`.sess` khong co animation", m and "animation" not in m.group(0))
    check("`.sess[hidden]` co khai lai display:none", ".sess[hidden]{display:none;}" in css)
    check("`.sess .go[hidden]` co khai lai display:none",
          ".sess .go[hidden]{display:none;}" in css)

    # Tong ho phach, khong do
    blk = css[css.find("/* ══ DẢI NHẮC MẤT PHIÊN"):]
    blk = blk[:blk.find(".stat-tile")] if ".stat-tile" in blk else blk
    reds = re.findall(r"#(?:e|f)[0-9a-f]{2}[0-4][0-9a-f]{3}\b", blk, re.I)
    check("khong dung mau do trong khoi `.sess`", not reds, str(reds[:3]))

    # progress.js: tran hang cho khong con vut viec trong IM LANG
    check("js/progress.js dem so viec bi vut", "LS_DROP" in prog and "dropped()" in prog)
    check("`dropped`/`clearDropped` duoc export",
          re.search(r"dropped\s*:\s*dropped", prog) is not None and
          re.search(r"clearDropped\s*:\s*clearDropped", prog) is not None)

    print("\n%s\nKET QUA: %d dat / %d hong\n%s" % ("=" * 58, dat, hong, "=" * 58))
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
