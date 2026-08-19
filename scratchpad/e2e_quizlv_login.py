# -*- coding: utf-8 -*-
"""e2e_quizlv_login.py — MAT XICH CUOI: `absorbQuizLv` co THAT SU chay khi tre dang nhap.

Ba bo do khac nhau da chung minh ba doan:
  `lvtest`             luat `Adapt.QuizLevel` (C# that)                     22/0
  `test_quizlv`        server tra `progress.quizLv` tren AWS (HTTP that)    26/0
  `smoke_quiz_lv`      `quiz.html` doc cache roi rut de theo cap            19/0

Con MOT doan chua ai do: **tu cau tra loi cua server VAO cache**. `absorbQuizLv`
duoc goi trong `getProfile()`/`getAchievements()` cua `js/progress.js`, va no doc
`data.progress.quizLv`. Doc code thi thay dung, nhung "doc code thay dung" khong
phai mot phep do — dung loai lo hong da de lai `boardSay` 19/08 sang nay.

CACH DO: tao tai khoan that (Firebase + ban ghi PROFILE), nop 4 luot quiz 5/5 qua
API de server tinh ra **cap 3**, roi DANG NHAP THAT tren astroq.org va doc
localStorage. Neu cache mang cap 3 thi ca day da lien mach — vi 3 la con so KHONG
THE doan ra: mac dinh cua moi duong lui deu la "chua biet" hoac cap 1.

⚠️ Tu don: xoa moi dong DynamoDB va tai khoan Firebase trong `finally`.

  python scratchpad/e2e_quizlv_login.py
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, "scratchpad")
import _fbtest

from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
API = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
TABLE = "astroq-main"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True)


def rows(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :p",
            "--expression-attribute-values", json.dumps({":p": {"S": "USER#%s" % uid}}),
            "--consistent-read", "--output", "json")
    if r.returncode != 0:
        return []
    return json.loads(r.stdout or "{}").get("Items", [])


uid = tok = None
email = "e2elv-test-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
try:
    print("\n=== [1] Dung mot dua tre CO tien do that ===")
    uid, tok, pw = _fbtest.make_verified(email)
    check("co tai khoan + token da xac minh email", bool(uid and tok), uid)
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item",
            json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": {"S": "PROFILE"},
                        "uid": {"S": uid}, "email": {"S": email},
                        "name": {"S": "Test Pilot"},
                        "createdAt": {"S": "2026-08-19T00:00:00.000Z"}}))
    check("tao ban ghi PROFILE", r.returncode == 0, r.stderr.strip()[:80])

    for _ in range(4):
        st, _d = call("POST", "/me/progress", tok,
                      {"type": "quiz", "correct": 5, "total": 5, "meteors": 0,
                       "opId": str(uuid.uuid4())})
    st, d = call("GET", "/me/profile", tok)
    server_lv = ((d or {}).get("progress") or {}).get("quizLv")
    check("server da tinh ra cap 3 cho tai khoan nay", server_lv == 3,
          "cap %s" % server_lv)
    if server_lv != 3:
        print("\n>>> DUNG HAN: chua dung duoc mot tai khoan cap 3 de do.")
        sys.exit(1)

    print("\n=== [2] DANG NHAP THAT tren astroq.org roi doc cache ===")
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                            "localStorage.setItem('astroq-tour-seen','1')}catch(e){}")
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad.append("%s %s" % (r.status, r.url))
              if r.status >= 400 else None)

        pg.goto(SITE + "/landing-app.html", wait_until="load")
        # ⚠️ Form dang nhap nam trong MOT OVERLAY, mac dinh dong. Lan chay dau
        #    `wait_for_selector("#login-email")` het gio 25 giay voi thong bao
        #    "locator resolved to hidden" — o ay khong phai loi san pham, la toi
        #    quen mot cu bam. Phai mo overlay bang `#btn-try` truoc.
        pg.wait_for_selector("#btn-try", timeout=25000)
        pg.click("#btn-try")
        # ⚠️ `#btn-try` ("Dung thu") mo overlay o pane DANG KY, khong phai dang nhap
        #    — do duoc: sau cu bam, overlay co class `show` nhung `#auth-login.hidden`
        #    van `true`. Phai bam `#to-login` de doi pane. Hai lan het gio truoc do
        #    la vi toi doan thay vi do.
        pg.wait_for_selector("#to-login", state="visible", timeout=25000)
        pg.click("#to-login")
        pg.wait_for_selector("#login-email", state="visible", timeout=25000)
        # ⚠️ Cache PHAI trong truoc khi dang nhap — neu khong thi "co cache" khong
        #    chung minh duoc dieu gi.
        before = pg.evaluate("() => localStorage.getItem('astroq-quiz-lv')")
        check("truoc khi dang nhap: CHUA co cache cap do", before is None, str(before))

        pg.fill("#login-email", email)
        pg.fill("#login-pass", pw)
        pg.click("#auth-login button.auth-submit")
        # Dang nhap xong trang tu chuyen sang buong lai; cho tan khi co cache HOAC
        # het 30 giay (het gio thi bao hong, khong im lang bo qua).
        # ⚠️ DANG NHAP XONG LA TRANG TU CHUYEN sang buong lai, nen `evaluate` giua
        #    luc dieu huong nem "Execution context was destroyed" — bo do chet giua
        #    duong chu khong bao hong. Nen: bo qua loi do va thu lai.
        for _ in range(40):
            try:
                if pg.evaluate("() => !!(window.AstroQ && AstroQ.getUser && "
                               "AstroQ.getUser())"):
                    break
            except Exception:
                pass
            pg.wait_for_timeout(500)
        print("      url sau khi dang nhap: %s" % pg.url)
        check("dang nhap that thanh cong (co phien)",
              pg.evaluate("() => !!(AstroQ.getUser && AstroQ.getUser())"), pg.url)

        # ⚠️ NGAY SAU DANG NHAP, CACHE CHUA CO — va do la DUNG, khong phai loi:
        #    trang dich sau dang nhap (`select.html`) khong doc ho so. Ghi lai bang
        #    mot phep kiem de ngay nao co ai them mot loi goi o day thi bo do noi ra,
        #    thay vi de con so nay troi khong ai biet.
        ngay_sau = pg.evaluate("() => localStorage.getItem('astroq-quiz-lv')")
        print("      cache ngay sau khi dang nhap: %s" % ngay_sau)

        print("\n=== [3] DUONG A — di qua buong lai (duong binh thuong) ===")
        pg.goto(SITE + "/dashboard.html", wait_until="load")
        got = None
        for _ in range(40):
            got = pg.evaluate("() => localStorage.getItem('astroq-quiz-lv')")
            if got:
                break
            pg.wait_for_timeout(500)
        check("mo buong lai -> cache `astroq-quiz-lv` duoc ghi", bool(got), str(got))
        if got:
            box = json.loads(got)
            check("cache mang DUNG cap 3 (con so KHONG the doan ra: moi duong lui"
                  " deu ra 'chua biet' hoac cap 1)", box.get("lv") == 3,
                  json.dumps(box))
            check("cache dong dau DUNG uid cua tai khoan nay",
                  box.get("uid") == uid, "%s vs %s" % (box.get("uid"), uid))
            seen = pg.evaluate("() => window.AstroQProgress "
                               "? AstroQProgress.quizLv() : null")
            check("doc qua chinh ham san pham: `quizLv()` bao biet cap va bang 3",
                  bool(seen) and seen.get("known") is True and seen.get("lv") == 3,
                  json.dumps(seen))

        print("\n=== [4] Vao Quiz: de PHAI la de cap 3 ===")
        keys = []
        pg.on("request", lambda r: keys.append(r.url.rsplit("/", 1)[-1][:-3])
              if "/js/quiz/" in r.url else None)
        for _ in range(6):
            pg.goto(SITE + "/quiz.html", wait_until="load")
            pg.wait_for_selector(".q-text", timeout=20000)
        LV = pg.evaluate("() => AstroQQuestions.LV")
        d3 = sum(1 for k in keys if LV.get(k) == 3)
        check("30 cau rut ra deu la cau cap 3", len(keys) == 30 and d3 == 30,
              "%d/%d cau lv3" % (d3, len(keys)))
        ctx.close()

        print("\n=== [5] DUONG B — vao THANG quiz.html (tre luu dau trang) ===")
        # ⚠️ KHE CON LAI, DA BIET: chua tung mo trang nao doc ho so thi Quiz khong
        #    biet cap. Dieu PHAI dung o day la no roi ve "chua biet" mot cach an
        #    toan — rut du de, 0 loi — chu KHONG phai doan mot cap nao.
        ctx2 = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx2.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
        p2 = ctx2.new_page()
        e2, k2 = [], []
        p2.on("console", lambda m: e2.append(m.text) if m.type == "error" else None)
        p2.on("pageerror", lambda e: e2.append(str(e)))
        p2.on("request", lambda r: k2.append(r.url.rsplit("/", 1)[-1][:-3])
              if "/js/quiz/" in r.url else None)
        for _ in range(4):
            p2.goto(SITE + "/quiz.html", wait_until="load")
            p2.wait_for_selector(".q-text", timeout=20000)
        check("may sach vao thang Quiz: van rut du 20 cau, 0 loi",
              len(k2) == 20 and not e2, "%d cau; %s" % (len(k2), e2[:1]))
        LV2 = p2.evaluate("() => AstroQQuestions.LV")
        d = {1: 0, 2: 0, 3: 0}
        for k in k2:
            d[LV2.get(k) or 1] += 1
        print("      phan bo khi CHUA biet cap: lv1 %d  lv2 %d  lv3 %d"
              % (d[1], d[2], d[3]))
        check("chua biet cap thi KHONG loc (de tron ca ba cap)",
              sum(1 for v in d.values() if v > 0) >= 2, str(d))
        ctx2.close()

        print("\n=== [6] DUONG C — viec gui tu HANG CHO cung phai cap nhat cap ===")
        # ⚠️ DAY LA NHANH VUA DUOC BIT 19/08/2026, nen phai do rieng.
        #    `quiz.html` CO Y khong nap SDK Firebase, nen `report()` khong co token
        #    va xep viec vao hang cho; viec do duoc gui o mot trang CO token. Neu
        #    `flush()` khong absorb thi cap do chi doi khi tre tinh co mo dung
        #    dashboard / achievements / codex.
        #
        #    Tach nhanh nay bang `missions.html`: trang do CO token nhung chi goi
        #    `daily()` va `missions()` — KHONG goi `profile()`/`achievements()`, nen
        #    cache xuat hien o day thi chi co the do `flush()` ghi.
        ctx3 = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx3.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
        p3 = ctx3.new_page()
        e3 = []
        p3.on("console", lambda m: e3.append(m.text) if m.type == "error" else None)
        p3.on("pageerror", lambda e: e3.append(str(e)))

        # Dang nhap lai trong ngu canh sach nay.
        p3.goto(SITE + "/landing-app.html", wait_until="load")
        p3.wait_for_selector("#btn-try", timeout=25000)
        p3.click("#btn-try")
        p3.wait_for_selector("#to-login", state="visible", timeout=25000)
        p3.click("#to-login")
        p3.wait_for_selector("#login-email", state="visible", timeout=25000)
        p3.fill("#login-email", email)
        p3.fill("#login-pass", pw)
        p3.click("#auth-login button.auth-submit")
        for _ in range(40):
            try:
                if p3.evaluate("() => !!(window.AstroQ && AstroQ.getUser "
                               "&& AstroQ.getUser())"):
                    break
            except Exception:
                pass
            p3.wait_for_timeout(500)
        check("[C] dang nhap lai trong ngu canh sach",
              p3.evaluate("() => !!(AstroQ.getUser && AstroQ.getUser())"), p3.url)

        # Xoa cache roi dat MOT viec quiz vao hang cho, y nhu `quiz.html` lam khi
        # khong co token. Viec nay la 0/5 nen no HA ti le dung -> cap phai TUT.
        p3.evaluate("""() => {
            localStorage.removeItem('astroq-quiz-lv');
            localStorage.setItem('astroq-progress-queue', JSON.stringify([
              { type:'quiz', correct:0, total:5, meteors:0,
                opId:'e2e-'+Math.random().toString(36).slice(2,12) }
            ]));
        }""")
        check("[C] da xoa cache va dat mot luot 0/5 vao hang cho",
              p3.evaluate("() => !localStorage.getItem('astroq-quiz-lv') && "
                          "JSON.parse(localStorage.getItem('astroq-progress-queue')"
                          "||'[]').length === 1"))

        # Mo `missions.html`: `progress.js` tu goi `flush()` khi hang cho khong rong.
        p3.goto(SITE + "/missions.html", wait_until="load")
        cache3 = None
        for _ in range(50):
            cache3 = p3.evaluate("() => localStorage.getItem('astroq-quiz-lv')")
            if cache3:
                break
            p3.wait_for_timeout(500)
        check("[C] `flush()` ghi cache cap do (nhanh vua bit)", bool(cache3),
              str(cache3))
        left3 = p3.evaluate("() => JSON.parse("
                            "localStorage.getItem('astroq-progress-queue')||'[]').length")
        check("[C] hang cho da gui het", left3 == 0, "con %s viec" % left3)
        if cache3:
            box3 = json.loads(cache3)
            # 4 luot 5/5 (=20/20) + 1 luot 0/5 => 20/25 = 80% -> van cap 3.
            # Doi chieu voi CHINH server thay vi tu tinh.
            st, dd = call("GET", "/me/profile", tok)
            sv = ((dd or {}).get("progress") or {}).get("quizLv")
            a2 = ((dd or {}).get("progress") or {}).get("quizAnswered")
            c2 = ((dd or {}).get("progress") or {}).get("quizCorrect")
            print("      server: %s/%s dung -> cap %s ; cache: %s"
                  % (c2, a2, sv, json.dumps(box3)))
            check("[C] cache khop DUNG cap do server dang bao", box3.get("lv") == sv,
                  "cache %s vs server %s" % (box3.get("lv"), sv))
            check("[C] server DA nhan luot 0/5 tu hang cho (25 cau da tra loi)",
                  a2 == 25, "%s cau" % a2)
        check("[C] 0 loi console / pageerror", not e3, str(e3[:2]))
        ctx3.close()

        # ⚠️ Chot "0 loi" o CUOI, sau khi da di het luong — chot som la bo qua moi
        #    thu xay ra sau do.
        check("0 loi console / pageerror suot ca luong", not errs, str(errs[:2]))
        _bad = [x for x in bad if "/me/" not in x]
        check("0 asset hong", not _bad, "; ".join(_bad[:2]))

        b.close()

finally:
    if uid:
        print("\n=== [4] Don du lieu test ===")
        n = 0
        for it in rows(uid):
            aws("dynamodb", "delete-item", "--table-name", TABLE,
                "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
            n += 1
        left = len(rows(uid))
        print("      da xoa %d dong, con lai %d" % (n, left))
        if left:
            print("      ⚠️ CON SOT %d dong" % left)
        try:
            _fbtest.delete(tok)
            print("      da xoa tai khoan Firebase tam")
        except Exception as e:
            print("      ⚠️ chua xoa duoc tai khoan tam: %s" % e)

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
