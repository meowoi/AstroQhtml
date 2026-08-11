# -*- coding: utf-8 -*-
"""
smoke_parent.py — do THAT tren Chromium: trang Bang theo doi cho bo me.

    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/smoke_parent.py

Gia lap `AstroQAuth` de khong phai dung tai khoan that — trang chi doc
`getReport()` / `sendReportEmail()` nen gia lap dung hai ham do la du.

Trong tam — thu de lam bao cao NOI SAI voi phu huynh:
  1. Chua dang nhap / mat mang -> moi con so hien "—", KHONG hien 0.
  2. Tuan RONG -> noi that "chua ghi duoc gi", KHONG ve mot loat so 0.
  3. `sent:false` co BA ly do khac nhau; gop thanh "gui that bai" la noi sai
     voi phu huynh trong 2/3 truong hop.
  4. Xu huong ("tang 8 diem") chi duoc noi khi CA HAI tuan deu co so.
"""
import json
import sys

from playwright.sync_api import sync_playwright

# ⚠️ Console Windows cp1252 — detail cua check() lay chu tu trang (co dau).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123").rstrip("/")
ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def week(empty=False, **kw):
    # ⚠️ `days`/`partial` la cua ban CAT TUAN DAU (09/08/2026). Mac dinh 7/False =
    #    tuan tron; muc [7] gieo 2/True va 0/True de thu hai nhanh con lai.
    d = dict(from_="2026-08-03T17:00:00.0000000Z", to="2026-08-10T17:00:00.0000000Z",
             activeDays=0, days=7, partial=False,
             terms=[], weakCount=0,
             quizRounds=0, quizAnswered=0, quizCorrect=0, accuracy=None,
             games=0, gameSeconds=0, lessons=0, planets=0,
             missionSteps=0, missionRefs=[], xp=0, meteors=0, empty=empty)
    d.update(kw)
    d["from"] = d.pop("from_")
    return d


def stub(ctx, report, mail=None):
    """
    ⚠️ GAN BANG `Object.defineProperty` CO SETTER NUOT LOI GAN — module ES that
       (js/firebase-auth.js) chay SAU script co dien va se ghi de `window.AstroQAuth`.
       Bai hoc da ghi o smoke_onboard/smoke_mission_earth.
    """
    ctx.add_init_script("""
      localStorage.setItem('astroq-user', JSON.stringify(
        {name:'Bin', pilotName:'Bin', uid:'u-test', character:'m', avatar:'ava/avam.png'}));
      localStorage.setItem('astroq-lang','vi');
      const FAKE = {
        getReport: () => Promise.resolve(__REPORT__),
        sendReportEmail: () => Promise.resolve(__MAIL__)
      };
      Object.defineProperty(window, 'AstroQAuth', {
        configurable: true, get: () => FAKE, set: () => {}
      });
    """.replace("__REPORT__", json.dumps(report))
       .replace("__MAIL__", json.dumps(mail or {"ok": True, "data": {"sent": True, "to": "bi***@gmail.com"}})))


def errs_of(page):
    bag = []
    page.on("pageerror", lambda e: bag.append(str(e)))
    page.on("console", lambda m: bag.append(m.text) if m.type == "error" else None)
    return bag


def open_page(br, report, mail=None, vw=(1440, 900)):
    ctx = br.new_context(viewport={"width": vw[0], "height": vw[1]})
    stub(ctx, report, mail)
    pg = ctx.new_page()
    errs = errs_of(pg)
    pg.goto(f"{BASE}/parent.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".hero h1", timeout=8000)
    pg.wait_for_timeout(700)
    return ctx, pg, errs


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ══════════ [1] Tuan co du lieu ══════════
        print("\n[1] Tuan CO du lieu")
        cur = week(activeDays=4, quizRounds=5, quizAnswered=25, quizCorrect=19,
                   accuracy=76, games=2, gameSeconds=420, lessons=1,
                   missionSteps=3, missionRefs=["earth:scan"], xp=430, meteors=140)
        prv = week(activeDays=2, quizRounds=2, quizAnswered=10, quizCorrect=6, accuracy=60)
        rep = {"ok": True, "data": {"week": 0, "child": "Bin", "current": cur,
                                    "previous": prv, "badges": ["rookie-astronaut"],
                                    "lifetime": {"xp": 900, "level": 4}}}
        ctx, pg, errs = open_page(br, rep)

        txt = pg.inner_text("#stats")
        check("Hien so ngay co hoc 4/7", "4/7" in txt, "")
        check("Hien do chinh xac 76%", "76%" in txt, "")
        check("Hien so cau 19/25", "19/25" in txt, "")
        check("Hien buoc nhiem vu", "3" in txt, "")
        check("Hien XP +430", "+430" in txt, "")
        check("Khoi 'tuan rong' AN", not pg.locator("#empty").is_visible())

        # ⚠️ Xu huong: 76 vs 60 -> "tang 16 diem"
        sub = pg.inner_text(".kv .cell .sub") if pg.locator(".kv .cell .sub").count() else ""
        check("Noi xu huong so voi tuan truoc", "tăng 16" in sub, sub.strip())
        check("Xu huong tang thi to xanh (class .up)",
              "up" in (pg.get_attribute(".kv .cell .sub", "class") or ""))

        check("Hien huy hieu mo trong tuan", pg.locator(".pt-badge").count() == 1,
              str(pg.locator(".pt-badge").count()))
        check("Ten huy hieu lay tu js/badges.js, khong in id tho",
              "rookie-astronaut" not in pg.inner_text("#badges"),
              pg.inner_text("#badges").strip())

        check("Dai nhac AN khi doc duoc du lieu",
              not pg.locator("#offline").is_visible())
        # ⚠️ Dong noi that ve moc bat dau ghi PHAI hien — khong co no thi tuan rong
        #    doc ra thanh "con khong hoc".
        check("Dong 'bat dau ghi tu ngay…' HIEN RA",
              pg.locator("#since").is_visible() and "09/08/2026" in pg.inner_text("#since"),
              pg.inner_text("#since")[:60])
        check("0 loi console/pageerror", not errs, str(errs[:2]))
        ctx.close()

        # ══════════ [2] Tuan RONG ══════════
        print("\n[2] Tuan RONG -> noi that, khong ve so 0")
        rep2 = {"ok": True, "data": {"week": 0, "child": "Bin",
                                     "current": week(empty=True), "previous": week(empty=True),
                                     "badges": [], "lifetime": {"xp": 0, "level": 1}}}
        ctx, pg, errs = open_page(br, rep2)
        check("Khoi 'tuan rong' HIEN RA", pg.locator("#empty").is_visible())
        check("Noi ro chua ghi duoc hoat dong nao",
              "chưa ghi được" in pg.inner_text("#empty"), pg.inner_text("#empty")[:50])
        # ⚠️ Phep kiem quan trong nhat cua muc nay
        check("KHONG ve mot loat o so 0", pg.locator(".kv .cell").count() == 0,
              str(pg.locator(".kv .cell").count()))
        check("Panel huy hieu AN khi khong co huy hieu",
              not pg.locator("#badge-panel").is_visible())
        check("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # ══════════ [3] Chua dang nhap ══════════
        print("\n[3] Chua dang nhap -> dau '—', KHONG phai 0")
        ctx, pg, errs = open_page(br, {"ok": False, "status": 401})
        check("Dai nhac HIEN RA", pg.locator("#offline").is_visible())
        check("Dai nhac noi ve dang nhap", "Đăng nhập" in pg.inner_text("#offline"),
              pg.inner_text("#offline")[:60])
        st = pg.inner_text("#stats")
        check("Moi o hien dau '—'", st.count("—") >= 6, f'{st.count("—")} dau')
        # ⚠️ Chot chan that: khong duoc co so 0 nao trong luoi
        vals = pg.eval_on_selector_all(".kv .cell .v", "es=>es.map(e=>e.textContent.trim())")
        check("KHONG o nao hien so 0", all(v != "0" and v != "0%" for v in vals), str(vals))
        check("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # ══════════ [4] Gui email — ba ly do khac nhau ══════════
        print("\n[4] Gui email: ba ly do `sent:false` phai noi ba cau khac nhau")
        cases = [
            ({"ok": True, "data": {"sent": True, "to": "bi***@gmail.com"}},
             "Đã gửi", "ok", "gui thanh cong"),
            ({"ok": True, "data": {"sent": False, "reason": "empty"}},
             "chưa có gì để gửi", "", "tuan rong"),
            ({"ok": True, "data": {"sent": False, "reason": "cooldown", "retryAfter": 540}},
             "thử lại sau 9 phút", "", "cooldown"),
            ({"ok": True, "data": {"sent": False, "reason": "mail-failed"}},
             "trục trặc", "bad", "SES hong"),
        ]
        for mail, want, cls, tag in cases:
            ctx, pg, errs = open_page(br, rep, mail)
            pg.click("#send")
            pg.wait_for_timeout(500)
            msg = pg.inner_text("#mail-msg")
            klass = pg.get_attribute("#mail-msg", "class") or ""
            check(f"[{tag}] cau tra loi dung", want in msg, msg.strip()[:60])
            if cls:
                check(f"[{tag}] mang class .{cls}", cls in klass, klass)
            else:
                # ⚠️ "tuan rong" va "vua gui roi" KHONG phai loi — to do chung la noi
                #    voi phu huynh rang co gi do hong trong khi he thong tra loi dung.
                check(f"[{tag}] KHONG bi to do (khong phai loi)", "bad" not in klass, klass)
            ctx.close()

        # ══════════ [5] Doi tuan ══════════
        print("\n[5] Chon tuan")
        ctx, pg, errs = open_page(br, rep)
        check("Co 3 nut chon tuan", pg.locator("#weeks button").count() == 3,
              str(pg.locator("#weeks button").count()))
        pg.click('#weeks button[data-w="1"]')
        pg.wait_for_timeout(400)
        check("Bam 'Tuan truoc' thi tieu de doi",
              "Tuần trước" in pg.inner_text("#sum-h"), pg.inner_text("#sum-h"))
        check("Nut duoc chon co aria-pressed=true",
              pg.get_attribute('#weeks button[data-w="1"]', "aria-pressed") == "true")
        ctx.close()

        # ══════════ [6] Ban EN + dien thoai ══════════
        print("\n[6] Ban EN + dien thoai 390px")
        ctx, pg, errs = open_page(br, rep)
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(400)
        check("Tieu de dich sang EN", "learned this week" in pg.inner_text("h1"),
              pg.inner_text("h1"))
        # ⚠️ Doc NHAN cua tung o (`.k`) chu khong doc ca khoi `#stats`: khoi do gom
        #    ca GIA TRI, va mot gia tri trung chu tieng Anh se lam phep kiem xanh oan.
        labels = pg.eval_on_selector_all(".kv .cell .k", "es=>es.map(e=>e.textContent.trim())")
        check("Nhan o so lieu dich sang EN", "Days active" in labels, str(labels[:3]))
        check("Xu huong dich sang EN", "up 16" in pg.inner_text(".kv .cell .sub"),
              pg.inner_text(".kv .cell .sub").strip())
        ctx.close()

        ctx, pg, errs = open_page(br, rep, vw=(390, 844))
        ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check("390px: khong tran ngang", ow <= 0, f"tran {ow}px")
        bb = pg.locator("#send").bounding_box()
        check("390px: nut gui >= 44px", bb and bb["height"] >= 44,
              f'{bb["height"]:.0f}px' if bb else "?")
        check("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # ══════════ [7] Tuan bi CAT tai ngay dang ky ══════════
        # ⚠️ Dang ky thu Bay thi tuan dau chi con 2 ngay. In "1/7" cho no la dua ra
        #    truoc mat phu huynh mot tuan luoi hoc — dung cach doc sai ma viec cat
        #    tuan sinh ra de tranh. Va tuan nam TRUOC ngay dang ky phai noi mot cau
        #    KHAC han "chua ghi duoc hoat dong nao".
        print("\n[7] Tuan bi cat tai ngay dang ky")
        curp = week(days=2, partial=True, activeDays=1, quizRounds=1, quizAnswered=5,
                    quizCorrect=4, accuracy=80, xp=110, meteors=60)
        repp = {"ok": True, "data": {"week": 0, "child": "Bin", "current": curp,
                                     "previous": week(empty=True), "badges": [],
                                     "lifetime": {"xp": 110, "level": 1}}}
        ctx, pg, errs = open_page(br, repp)
        rng = pg.inner_text("#range")
        check("Noi ra rang day la tuan dau bi cat",
              "tuần đầu" in rng and "2 ngày" in rng, rng.strip()[:70])
        stt = pg.inner_text("#stats")
        # ⚠️ Phep kiem quan trong nhat cua muc nay
        check("Mau so la SO NGAY CUA TUAN (1/2), khong phai 1/7",
              "1/2" in stt and "1/7" not in stt, "co 1/7" if "1/7" in stt else "1/2")
        check("Xu huong KHONG bia khi tuan truoc rong",
              pg.locator(".kv .cell .sub").count() == 0
              or "tăng" not in pg.inner_text(".kv .cell .sub"),
              pg.inner_text(".kv .cell .sub").strip() if pg.locator(".kv .cell .sub").count() else "-")
        check("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # Ca tuan nam TRUOC ngay dang ky -> `days == 0`
        curb = week(empty=True, partial=True, days=0)
        repb = {"ok": True, "data": {"week": 2, "child": "Bin", "current": curb,
                                     "previous": week(empty=True), "badges": [],
                                     "lifetime": {"xp": 0, "level": 1}}}
        ctx, pg, errs = open_page(br, repb)
        emp = pg.inner_text("#empty")
        check("Khoi 'tuan rong' HIEN RA", pg.locator("#empty").is_visible())
        check("Noi dung tuan nam TRUOC ngay dang ky",
              "trước ngày con đăng ký" in emp, emp.strip()[:70])
        # ⚠️ Noi nham cau la do cho dua tre mot tuan no chua ton tai
        check("KHONG dung cau 'chua ghi duoc hoat dong nao'",
              "chưa ghi được" not in emp, emp.strip()[:70])
        check("KHONG ve o so nao", pg.locator(".kv .cell").count() == 0,
              str(pg.locator(".kv .cell").count()))
        check("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # Ban EN cua hai nhanh tren
        ctx, pg, errs = open_page(br, repp)
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(400)
        check("EN: noi ra tuan dau bi cat",
              "first week" in pg.inner_text("#range"), pg.inner_text("#range").strip()[:70])
        ctx.close()
        ctx, pg, errs = open_page(br, repb)
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(400)
        check("EN: noi tuan nam truoc ngay dang ky",
              "before your child signed up" in pg.inner_text("#empty"),
              pg.inner_text("#empty").strip()[:70])
        ctx.close()

        # ══════════ [8] Chu de: vung / can luyen them ══════════
        # ⚠️ Server tra ve KHOA CAU (`black-hole`, `star-fusion`); TEN chu de song ngu
        #    nam o js/quiz-index.js. Muc nay do dung dieu do: trang phai goi TEN, va
        #    hai khoa cung mot the phai GOM lai lam mot dong.
        print("\n[8] Chu de: vung / can luyen them")
        curt = week(activeDays=3, quizRounds=3, quizAnswered=6, quizCorrect=3,
                    accuracy=50, xp=200, weakCount=2, terms=[
                        {"term": "black-hole",  "ok": 0, "wrong": 2},
                        {"term": "star",        "ok": 1, "wrong": 0},
                        {"term": "star-fusion", "ok": 0, "wrong": 1},
                        {"term": "comet-what",  "ok": 2, "wrong": 0}])
        rept = {"ok": True, "data": {"week": 0, "child": "Bin", "current": curt,
                                     "previous": week(empty=True), "badges": [],
                                     "lifetime": {"xp": 200, "level": 2}}}
        ctx, pg, errs = open_page(br, rept)
        check("Panel chu de HIEN RA", pg.locator("#topic-panel").is_visible())
        rowsn = pg.locator(".pt-topic").count()
        # 4 khoa -> 3 dong: `star` + `star-fusion` cung mot the
        check("Gom hai khoa cung mot the thanh MOT dong", rowsn == 3, f"{rowsn} dong")
        names = pg.eval_on_selector_all(".pt-topic .tn", "es=>es.map(e=>e.textContent.trim())")
        check("Goi TEN chu de, khong in khoa tho",
              "LỖ ĐEN" in names and "NGÔI SAO" in names, str(names))
        panel = pg.inner_text("#topic-panel")
        # ⚠️ Phep kiem quan trong nhat cua muc nay: khong duoc lo khoa ky thuat
        check("KHONG lo khoa ky thuat ra man hinh",
              "black-hole" not in panel and "star-fusion" not in panel, panel[:60])
        check("Chu de CAN LUYEN xep len tren cung", names[0] == "LỖ ĐEN", str(names[:2]))
        cnt = pg.eval_on_selector_all(".pt-topic .tc", "es=>es.map(e=>e.textContent.trim())")
        check("Dem gop dung sau khi gom (NGOI SAO = 1/2)", "1/2" in cnt, str(cnt))
        check("The 'vung' co it nhat mot dong", pg.locator(".pt-topic.solid").count() == 1,
              str(pg.locator(".pt-topic.solid").count()))
        check("The 'can luyen them' dung 2 dong", pg.locator(".pt-topic.weak").count() == 2,
              str(pg.locator(".pt-topic.weak").count()))
        # ⚠️ HO PHACH, KHONG PHAI DO — day la bao cao hoc tap cua mot dua tre.
        col = pg.eval_on_selector(".pt-topic.weak .tg", "e=>getComputedStyle(e).color")
        check("Nhan 'can luyen them' to ho phach, khong to do", col == "rgb(255, 207, 107)", col)
        check("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # Ban EN
        ctx, pg, errs = open_page(br, rept)
        pg.click('.lang-switch button[data-lang="en"]')
        pg.wait_for_timeout(400)
        panel = pg.inner_text("#topic-panel")
        check("EN: ten chu de dich theo", "BLACK HOLE" in panel, panel[:70])
        check("EN: nhan trang thai dich theo",
              "needs work" in panel and "solid" in panel, panel[-70:])
        ctx.close()

        # Tuan chua co du lieu chu de -> AN han panel, khong ve mot khoi rong
        ctx, pg, errs = open_page(br, rep)      # rep cua muc [1]: terms = []
        check("Khong co du lieu chu de -> panel AN",
              not pg.locator("#topic-panel").is_visible())
        ctx.close()
        ctx, pg, errs = open_page(br, {"ok": False, "status": 401})
        check("Chua dang nhap -> panel chu de AN",
              not pg.locator("#topic-panel").is_visible())
        ctx.close()

        # ══════════ [9] Duong vao tu dashboard ══════════
        print("\n[9] Duong vao tu dashboard")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script("""
          localStorage.setItem('astroq-user', JSON.stringify(
            {name:'Bin', uid:'u-test', character:'m', avatar:'ava/avam.png'}));
          localStorage.setItem('astroq-tour-seen','1');
          localStorage.setItem('astroq-map01-seen','1');
        """)
        pg = ctx.new_page()
        pg.goto(f"{BASE}/dashboard.html", wait_until="domcontentloaded")
        pg.wait_for_selector(".ptiles", timeout=8000)
        link = pg.locator(".pt-parent")
        check("Dashboard co link sang trang phu huynh", link.count() == 1)
        check("Link tro dung parent.html",
              (link.get_attribute("href") or "") == "parent.html", link.get_attribute("href"))
        check("Link NAM NGOAI luoi 3 o cua tre",
              pg.eval_on_selector(".pt-parent", "e=>!e.closest('.ptiles')"))
        bb = link.bounding_box()
        check("Vung cham link >= 44px", bb and bb["height"] >= 44,
              f'{bb["height"]:.0f}px' if bb else "?")
        check("Luoi 3 o cua tre VAN dung 3 o",
              pg.locator(".ptiles .ptile").count() == 3,
              str(pg.locator(".ptiles .ptile").count()))
        ctx.close()

        br.close()

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
