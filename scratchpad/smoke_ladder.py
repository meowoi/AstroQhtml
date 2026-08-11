# -*- coding: utf-8 -*-
"""
smoke_ladder.py — do THAT khoi "Lo trinh huan luyen" o achievements.html tren Chromium.

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/smoke_ladder.py

Vi sao can bo rieng du `check_pages.py` muc [17] da soi tinh: soi tinh chi chung
minh CHUOI co trong file. No khong chung minh duoc 5 dieu nguoi xem thuc su thay:
  · bang co dung 10 hang, khoang cap lien tuc khong ho khong chong lan
  · dung MOT hang duoc danh dau la bac cua nguoi xem
  · moc XP hien ra la SO CUA SERVER, khong phai so client tu tinh  <-- quan trong nhat
  · server khong tra bang moc thi cot XP BIEN MAT (khong bia)
  · chua doc duoc cap do thi KHONG danh dau bac nao

⚠️ Nghe CA `pageerror` chu khong chi `console`: ngoai le chua bat di qua pageerror,
   va bai hoc 02/08/2026 la form waitlist chet cam suot 6 ngay vi bo do chi nghe
   `console` nen bao "khong co loi".
⚠️ Nhan `check()` phai KHONG DAU — console Windows mac dinh cp1252, in mot chu co
   dau la UnicodeEncodeError nem GIUA luc chay va bo do moi phep kiem phia sau.
"""
import json
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
ok_n, bad_n = 0, 0

USER = {"name": "Bi Bo", "pilotName": "Bi Bo", "character": "m",
        "selectedCharacter": "m", "avatar": "ava/avam.png",
        "email": "bibo@astroq-test.invalid", "uid": "UID-LADDER-TEST"}

# 10 bac x 5 cap — doc lai tu js/ranks.js chu khong go tay o day, xem RANKS ben duoi.
BADGES = [
    {"id": "first-quiz", "group": "learn", "goal": 1, "current": 1, "earned": True,
     "earnedAt": "2026-07-20T10:00:00.000Z"},
    {"id": "level-20", "group": "level", "goal": 20, "current": 7, "earned": False,
     "earnedAt": None},
]

# Moc XP THAT theo cong thuc server: 100*(n-1)*n/2
REAL_XP = [0 if n == 1 else 100 * (n - 1) * n // 2 for n in range(1, 51)]
# Moc XP GIEO LECH (x3) — dung de chung minh client KHONG tu tinh cong thuc.
# Neu trang tu tinh, no se hien so REAL; neu doc server, no hien so nay.
FAKE_XP = [v * 3 for v in REAL_XP]


def ach(level=7, xp_table=REAL_XP, max_level=50):
    d = {
        "level": {"level": level, "xp": REAL_XP[level - 1] + 40,
                  "xpInLevel": 40, "xpForNext": 700, "pct": 34},
        "progress": {"xp": REAL_XP[level - 1] + 40, "quizCorrect": 39, "gamesPlayed": 13,
                     "lessonsRead": 6, "planets": ["earth", "mars", "venus"],
                     "bests": {"dodge": 412}, "consts": {}},
        "newBadges": [],
        "wallet": {"meteors": 41},
        "achievements": {"summary": {"earned": 1, "total": len(BADGES)}, "badges": BADGES},
    }
    if xp_table is not None:
        d["levels"] = {"maxLevel": max_level, "xp": xp_table}
    return d


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def stub(mode="ok", data=None):
    """Ban gia window.AstroQAuth. Cai bang getter/setter, KHONG gan thang:
    js/firebase-auth.js la ES module nen chay SAU script co dien va se de mat ban
    gia (da dinh dung bay nay o smoke_onboard.py)."""
    fail = "{ ok:false, reason:'%s' }" % ("auth" if mode == "auth" else "net")
    payload = json.dumps(data if data is not None else ach())
    return f"""
      window.__calls = [];
      const OK = {json.dumps(mode == "ok")};
      const stub = {{
        idToken: async () => OK ? "tok" : null,
        getOnboarding: async () => ({{ ok:true, tourSeen:true, map01Seen:true,
                                       earth1Greeted:true }}),
        setOnboarding: async () => ({{ ok:true }}),
        getProfile: async () => OK ? {{ ok:true, data:{{}} }} : {fail},
        getAchievements: async () => {{ window.__calls.push("getAchievements");
          return OK ? {{ ok:true, data:{payload} }} : {fail}; }},
        getMissions: async () => OK ? {{ ok:true, data:{{ missions:{{}} }} }} : {fail},
        updateProfile: async () => OK ? {{ ok:true, data:{{}} }} : {fail},
        postProgress: async () => OK ? {{ ok:true, data:{{}} }} : {fail}
      }};
      Object.disableSuddenTermination;
      Object.defineProperty(window, "AstroQAuth",
        {{ get: () => stub, set: () => {{}}, configurable: true }});
    """


def open_page(browser, lang="vi", mode="ok", data=None, mobile=False):
    kw = {"locale": "vi-VN" if lang == "vi" else "en-GB",
          "viewport": {"width": 390, "height": 844} if mobile
                      else {"width": 1440, "height": 950}}
    if mobile:
        kw.update(is_mobile=True, has_touch=True, device_scale_factor=2)
    ctx = browser.new_context(**kw)
    ctx.add_init_script(
        f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
        f"localStorage.setItem('astroq-lang', '{lang}');"
        "localStorage.setItem('astroq-asteroids','41');"
        "localStorage.setItem('astroq-tour-seen','1');"
    )
    ctx.add_init_script(stub(mode, data))
    pg = ctx.new_page()
    errs = []
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror:" + str(e)))
    pg.goto(BASE + "achievements.html", wait_until="domcontentloaded")
    pg.wait_for_function("document.querySelectorAll('#ranks .rk').length > 0", timeout=15000)
    return ctx, pg, errs


def rows(pg):
    return pg.evaluate("""() => Array.from(document.querySelectorAll('#ranks .rk')).map(li => ({
        cls: li.className,
        nm: (li.querySelector('.nm')||{}).textContent || '',
        lv: (li.querySelector('.lv')||{}).textContent || '',
        xp: (li.querySelector('.xp')||{}).textContent || '',
        here: !!li.querySelector('.here'),
        hereTxt: (li.querySelector('.here')||{}).textContent || ''
      }))""")


def main():
    # Doc TEN BAC tu chinh js/ranks.js — go tay o day la ban sao thu hai cua bang ten.
    src = open("js/ranks.js", encoding="utf-8").read()
    RANKS = re.findall(r'\{\s*key:\s*"([a-z-]+)",\s*vi:\s*"([^"]+)",\s*en:\s*"([^"]+)"', src)
    MAXLV = int(re.search(r"var\s+MAX_LEVEL\s*=\s*(\d+)", src).group(1))
    PER = MAXLV // len(RANKS)
    print(f"  (doc tu js/ranks.js: {len(RANKS)} bac, {MAXLV} cap, {PER} cap/bac)")

    with sync_playwright() as p:
        br = p.chromium.launch()

        # ---------- [1] Cau truc bang ----------
        print("\n=== [1] Bang lo trinh: du 10 bac, khoang cap lien tuc ===")
        ctx, pg, errs = open_page(br)
        R = rows(pg)
        check("bang co dung so hang bang so bac khai o ranks.js",
              len(R) == len(RANKS), f"{len(R)} vs {len(RANKS)}")
        check("the bao boc la <ol> (danh sach CO THU TU)",
              pg.eval_on_selector("#ranks", "e => e.tagName") == "OL")
        check("ten bac hien theo dung THU TU thap -> cao",
              [r["nm"].split(" (")[0] for r in R] == [x[1] for x in RANKS],
              str([r["nm"] for r in R[:3]]))
        check("ban VI hien ca ten goc tieng Anh trong ngoac",
              all("(" in r["nm"] and ")" in r["nm"] for r in R),
              str([r["nm"] for r in R if "(" not in r["nm"]]))

        got = [tuple(int(x) for x in re.findall(r"\d+", r["lv"])) for r in R]
        check("moi hang doc ra dung mot khoang cap",
              all(len(g) == 2 for g in got), str(got[:3]))
        if all(len(g) == 2 for g in got):
            check("hang dau bat dau o cap 1", got[0][0] == 1, got[0][0])
            check(f"hang cuoi ket o cap {MAXLV}", got[-1][1] == MAXLV, got[-1][1])
            check("khoang cap LIEN TUC, khong ho khong chong lan",
                  all(got[i + 1][0] == got[i][1] + 1 for i in range(len(got) - 1)),
                  str(got))
            check(f"moi bac dung {PER} cap (chia deu)",
                  all(g[1] - g[0] + 1 == PER for g in got),
                  str([g for g in got if g[1] - g[0] + 1 != PER]))
        # ⚠️ So bang casefold: `.hub-tag` co `text-transform:uppercase` nen
        #    `inner_text` tra ve chu HOA ("10 BẬC · 50 CẤP") trong khi tu dien i18n
        #    viet chu thuong. So thang la bao hong oan — dung loi da ghi o CLAUDE.md
        #    quy tac 8 muc 6 (phep kiem chu Viet dung go chuoi co phan biet hoa/thuong).
        check("khoi lo trinh in dung so bac + so cap o nhan dem",
              pg.inner_text("#ld-count").strip().casefold() ==
              f"{len(RANKS)} bậc · {MAXLV} cấp".casefold(),
              pg.inner_text("#ld-count"))

        # ---------- [2] Danh dau bac hien tai ----------
        print("\n=== [2] Bac hien tai: dung MOT hang, dung hang chua cap do ===")
        now = [i for i, r in enumerate(R) if "now" in r["cls"].split()]
        done = [i for i, r in enumerate(R) if "done" in r["cls"].split()]
        off = [i for i, r in enumerate(R) if "off" in r["cls"].split()]
        check("co DUNG MOT hang duoc danh dau 'now'", len(now) == 1, str(now))
        # level 7 => bac thu 2 (cap 6-10) voi PER=5
        want = (7 - 1) // PER
        check("hang 'now' la dung bac chua cap 7", now == [want], f"{now} vs [{want}]")
        check("cac bac TRUOC do la 'done'", done == list(range(want)), str(done))
        check("cac bac SAU do la 'off'",
              off == list(range(want + 1, len(R))), str(off))
        check("nhan 'Ban dang o day' xuat hien dung MOT lan",
              sum(1 for r in R if r["here"]) == 1)
        check("nhan do nam o dung hang 'now'", R[want]["here"])
        check("dong nhac 'chua doc duoc cap do' KHONG hien khi da co cap do",
              pg.eval_on_selector("#ld-note", "e => getComputedStyle(e).display") == "none")

        # ---------- [3] Moc XP la SO CUA SERVER ----------
        print("\n=== [3] Moc XP: doc tu server, KHONG tu tinh cong thuc ===")
        # Hang nao cung phai hien dung REAL_XP[lo-1]
        want_xp = [REAL_XP[g[0] - 1] for g in got]
        seen_xp = [int(re.sub(r"\D", "", r["xp"]) or -1) for r in R]
        check("moi hang hien dung moc XP cua cap dau bac do",
              seen_xp == want_xp, f"thay {seen_xp[:4]} muon {want_xp[:4]}")
        check("so XP co dau phan cach nghin (ban VI dung dau cham)",
              any("." in r["xp"] for r in R), str([r["xp"] for r in R[-2:]]))
        ctx.close()

        # ⚠️ PHEP DO MANH NHAT CUA CA BO: gieo bang moc LECH HAN cong thuc (x3).
        #    Client tu tinh -> hien so cong thuc; client doc server -> hien so gieo.
        ctx2, pg2, errs2 = open_page(br, data=ach(xp_table=FAKE_XP))
        R2 = rows(pg2)
        got2 = [tuple(int(x) for x in re.findall(r"\d+", r["lv"])) for r in R2]
        seen2 = [int(re.sub(r"\D", "", r["xp"]) or -1) for r in R2]
        want2 = [FAKE_XP[g[0] - 1] for g in got2]
        check("gieo bang moc LECH cong thuc -> trang hien so CUA SERVER",
              seen2 == want2, f"thay {seen2[:4]} muon {want2[:4]}")
        check("... va KHONG hien so cua cong thuc (tuc khong tu tinh)",
              seen2 != [REAL_XP[g[0] - 1] for g in got2])
        errs2_all = list(errs2)
        ctx2.close()

        # ---------- [4] Server khong tra bang moc -> AN cot XP ----------
        print("\n=== [4] Server khong tra bang moc -> an cot XP, khong bia ===")
        ctx3, pg3, errs3 = open_page(br, data=ach(xp_table=None))
        R3 = rows(pg3)
        check("bang van du so hang", len(R3) == len(RANKS), len(R3))
        check("KHONG hang nao hien moc XP", all(r["xp"] == "" for r in R3),
              str([r["xp"] for r in R3 if r["xp"]]))
        check("khoang cap van hien binh thuong", all(r["lv"] for r in R3))
        check("bac hien tai van duoc danh dau",
              sum(1 for r in R3 if r["here"]) == 1)
        ctx3.close()

        # ---------- [5] Chua dang nhap / mat mang ----------
        print("\n=== [5] Chua doc duoc cap do -> KHONG danh dau bac nao ===")
        for mode, nhan in (("auth", "chua dang nhap"), ("net", "mat mang")):
            ctx4, pg4, errs4 = open_page(br, mode=mode)
            R4 = rows(pg4)
            check(f"[{nhan}] bang VAN ve du 10 bac (phu huynh xem duoc lo trinh)",
                  len(R4) == len(RANKS), len(R4))
            check(f"[{nhan}] KHONG hang nao la 'now'",
                  not any("now" in r["cls"].split() for r in R4))
            check(f"[{nhan}] KHONG co nhan 'Ban dang o day'",
                  not any(r["here"] for r in R4))
            check(f"[{nhan}] KHONG hang nao la 'done' (khong bia da qua bac nao)",
                  not any("done" in r["cls"].split() for r in R4))
            check(f"[{nhan}] co dong noi ro chua doc duoc cap do",
                  pg4.eval_on_selector("#ld-note", "e => getComputedStyle(e).display") != "none"
                  and len(pg4.inner_text("#ld-note").strip()) > 10,
                  pg4.inner_text("#ld-note")[:50])
            check(f"[{nhan}] dai nhac chung cua trang cung hien",
                  pg4.eval_on_selector("#offline", "e => e.classList.contains('show')"))
            ctx4.close()

        # ---------- [6] Cap toi da ----------
        print("\n=== [6] Cap toi da: bac cuoi la 'now', khong con bac 'off' ===")
        ctx5, pg5, errs5 = open_page(br, data=ach(level=MAXLV))
        R5 = rows(pg5)
        check("bac CUOI duoc danh dau 'now'", "now" in R5[-1]["cls"].split(), R5[-1]["cls"])
        check("khong con bac nao 'off'",
              not any("off" in r["cls"].split() for r in R5))
        check(f"{len(RANKS)-1} bac dau la 'done'",
              sum(1 for r in R5 if "done" in r["cls"].split()) == len(RANKS) - 1)
        ctx5.close()

        # ---------- [7] Ban tieng Anh ----------
        print("\n=== [7] Ban EN: ten bac chi tieng Anh, khong ngoac ===")
        ctx6, pg6, errs6 = open_page(br, lang="en")
        R6 = rows(pg6)
        check("ten bac EN KHONG co ngoac (chi 'Navigator')",
              all("(" not in r["nm"] for r in R6), str([r["nm"] for r in R6[:3]]))
        check("ten bac EN khop cot en cua ranks.js",
              [r["nm"] for r in R6] == [x[2] for x in RANKS], str([r["nm"] for r in R6[:3]]))
        check("khoang cap dich sang 'Level a-b'",
              all(r["lv"].lower().startswith("level") for r in R6), R6[0]["lv"])
        check("nhan 'You are here' da dich",
              any(r["hereTxt"].strip().lower() == "you are here" for r in R6),
              str([r["hereTxt"] for r in R6 if r["here"]]))
        check("tieu de khoi da dich sang tieng Anh",
              "training" in pg6.inner_text(".ladder h2").lower(),
              pg6.inner_text(".ladder h2"))
        check("nhan dem dung tu 'ranks'/'levels'",
              "rank" in pg6.inner_text("#ld-count").lower(), pg6.inner_text("#ld-count"))

        # ---------- [8] Doi ngon ngu o TAB KHAC ----------
        print("\n=== [8] Doi ngon ngu o tab khac -> bang dich theo ===")
        pg6.evaluate("""() => {
            localStorage.setItem('astroq-lang','vi');
            window.dispatchEvent(new StorageEvent('storage',
              { key:'astroq-lang', newValue:'vi' }));
        }""")
        pg6.wait_for_function(
            "() => { const n=document.querySelector('#ranks .rk .nm');"
            " return n && n.textContent.includes('('); }", timeout=6000)
        R6b = rows(pg6)
        check("bang chuyen sang ban VI ma khong mat hang nao",
              len(R6b) == len(RANKS) and all("(" in r["nm"] for r in R6b), len(R6b))
        check("bac hien tai VAN duoc danh dau sau khi doi ngon ngu",
              sum(1 for r in R6b if r["here"]) == 1)
        ctx6.close()

        # ---------- [9] Dien thoai ----------
        print("\n=== [9] Dien thoai 390x844 ===")
        ctx7, pg7, errs7 = open_page(br, mobile=True)
        check("trang KHONG tran ngang",
              pg7.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1"),
              pg7.evaluate("() => document.documentElement.scrollWidth"))
        box = pg7.eval_on_selector(
            "#ranks .rk.now",
            "e => { const r = e.getBoundingClientRect();"
            "       const h = e.querySelector('.here').getBoundingClientRect();"
            "       return { rw:r.width, hr:h.right, vw:window.innerWidth, hw:h.width }; }")
        check("nhan 'Ban dang o day' nam TRONG khung",
              box["hr"] <= box["vw"] + 1, json.dumps(box))
        check("hang 'now' khong bi bop mat chu (rong > 250px)",
              box["rw"] > 250, box["rw"])
        nm_cut = pg7.eval_on_selector_all(
            "#ranks .nm", "els => els.filter(e => e.scrollWidth > e.clientWidth + 1).length")
        check("khong ten bac nao bi cat duoi", nm_cut == 0, nm_cut)
        ctx7.close()

        # ---------- [10] Khong lam mo bang grayscale ----------
        print("\n=== [10] Bac chua toi: mo bang opacity, KHONG grayscale ===")
        ctx8, pg8, errs8 = open_page(br)
        filt = pg8.eval_on_selector_all(
            "#ranks .rk.off",
            "els => els.map(e => getComputedStyle(e).filter)")
        check("khong hang 'off' nao dung filter grayscale",
              all(f in ("none", "") for f in filt), str(set(filt)))
        # ⚠️ Chi so voi hang 'off'. Ban dau phep kiem nay so voi MOI hang khac va
        #    bao hong oan: hang 'done' co opacity 1 vi day la THANH TICH DA DAT —
        #    lam mo no la noi rang thu tre da lam duoc thi kem quan trong. Thu can
        #    do la "bac chua toi phai nhat hon bac dang o", khong phai "moi hang
        #    khac deu nhat hon".
        op_now = pg8.eval_on_selector("#ranks .rk.now",
                                      "e => +getComputedStyle(e).opacity")
        op_off = pg8.eval_on_selector_all("#ranks .rk.off",
                                         "els => els.map(e => +getComputedStyle(e).opacity)")
        op_done = pg8.eval_on_selector_all("#ranks .rk.done",
                                          "els => els.map(e => +getComputedStyle(e).opacity)")
        check("bac CHUA TOI nhat hon bac dang o",
              op_off and all(op_now > x for x in op_off),
              f"now={op_now} off={sorted(set(op_off))}")
        check("bac DA QUA khong bi lam mo (day la thanh tich, khong phai thu bi khoa)",
              all(x >= op_now for x in op_done), f"done={sorted(set(op_done))}")
        # ⚠️ Phep kiem nay sinh ra tu mot loi THAT tim duoc bang cach soi anh chup:
        #    hang `off` .62 nhan voi `.ic` .5 ra 0,31 va cac bieu tuong 🧭🗺️⚓👑 gan
        #    nhu khong nhin ra hinh gi. Do OPACITY HIEU DUNG (nhan don theo chuoi
        #    to tien), khong doc rieng tung rule — doc rieng thi khong thay cong don.
        eff = pg8.eval_on_selector_all("#ranks .rk.off .ic", """els => els.map(e => {
            let o = 1, n = e;
            while (n && n !== document.body) { o *= +getComputedStyle(n).opacity; n = n.parentElement; }
            return Math.round(o * 100) / 100;
        })""")
        check("bieu tuong bac chua toi VAN doc duoc (opacity hieu dung >= .5)",
              eff and all(x >= 0.5 for x in eff), f"min={min(eff) if eff else None}")
        # Khoi phai NAM TREN luoi huy hieu (thu tu doc: tong quan -> lo trinh -> huy hieu)
        pos = pg8.evaluate("""() => {
            const l = document.querySelector('.ladder').getBoundingClientRect().top;
            const o = document.querySelector('.overview').getBoundingClientRect().top;
            const b = document.querySelector('#badges').getBoundingClientRect().top;
            return { o, l, b };
        }""")
        check("khoi lo trinh nam GIUA tong quan va luoi huy hieu",
              pos["o"] < pos["l"] < pos["b"], json.dumps(pos))
        errs8_all = list(errs8)
        ctx8.close()

        # ---------- [11] profile.html: dich BAC ke tiep ----------
        # Truoc 08/08/2026 trang chi noi "Con n XP nua len cap 8" — con so, khong
        # phai CAI TEN. Do o 3 moc: con xa, con dung 1 cap, va bac cuoi.
        print("\n=== [11] Ho so: noi ro con may cap nua thanh bac gi ===")
        errs_pf = []
        for lvl, mode in ((7, "xa"), (10, "sat"), (MAXLV, "cuoi")):
            ctxp = br.new_context(locale="vi-VN", viewport={"width": 1440, "height": 950})
            ctxp.add_init_script(
                f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
                "localStorage.setItem('astroq-lang','vi');"
                "localStorage.setItem('astroq-asteroids','41');"
                "localStorage.setItem('astroq-tour-seen','1');")
            d = ach(level=lvl)
            d["profile"] = {"uid": USER["uid"], "name": "Bi Bo", "email": USER["email"],
                            "character": "m", "avatar": "ava/avam.png",
                            "createdAt": "2026-03-14T08:00:00.000Z", "tourSeen": True}
            ctxp.add_init_script(stub("ok", d).replace(
                "getProfile: async () => OK ? { ok:true, data:{} } : ",
                "getProfile: async () => OK ? { ok:true, data:%s } : " % json.dumps(d)))
            pgp = ctxp.new_page()
            pgp.on("pageerror", lambda e: errs_pf.append("pageerror:" + str(e)))
            pgp.on("console",
                   lambda m: errs_pf.append("console:" + m.text) if m.type == "error" else None)
            pgp.goto(BASE + "profile.html", wait_until="domcontentloaded")
            pgp.wait_for_function("() => document.getElementById('lv-num')"
                                  " && document.getElementById('lv-num').textContent !== '1'"
                                  " || false", timeout=12000) if lvl != 1 else None
            pgp.wait_for_timeout(400)
            vis = pgp.eval_on_selector("#rank-goal", "e => getComputedStyle(e).display") != "none"
            txt = pgp.inner_text("#rank-goal").strip()
            soon = pgp.eval_on_selector("#rank-goal", "e => e.classList.contains('soon')")
            if mode == "xa":
                # cap 7, PER=5 => bac ke tiep bat dau o cap 11 => con 4 cap
                check("[cap 7] co hien dong dich bac", vis, txt)
                check("[cap 7] noi dung SO CAP con lai", "4" in txt, txt)
                check("[cap 7] goi dung TEN bac ke tiep (Nha Tham Hiem)",
                      "Thám Hiểm" in txt and "Explorer" in txt, txt)
                check("[cap 7] KHONG dung to sang (con xa)", not soon)
            elif mode == "sat":
                # cap 10 => cap 11 la moc vao bac moi => cau "len cap 11 la thanh ..."
                check("[cap 10] co hien dong dich bac", vis, txt)
                check("[cap 10] doi sang cau 'len cap 11 la thanh ...'",
                      "11" in txt and "Thám Hiểm" in txt, txt)
                check("[cap 10] duoc to sang (khoanh khac lon)", soon, txt)
            else:
                check(f"[cap {MAXLV}] AN han dong dich (khong hua bac khong ton tai)",
                      not vis, txt)
            ctxp.close()

        # ---------- [12] Khong loi console ----------
        print("\n=== [12] Khong loi console / pageerror ===")
        allerr = errs + errs2_all + errs3 + errs5 + errs6 + errs7 + errs8_all + errs_pf
        check("0 loi console va 0 pageerror tren moi luot do",
              len(allerr) == 0, "; ".join(allerr[:3]))

        br.close()

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
