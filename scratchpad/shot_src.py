# -*- coding: utf-8 -*-
"""
shot_src.py - render THAT bang nguon o admin-report.html roi chup anh de soi mat.

Chay:  python -m http.server 8123   roi   python scratchpad/shot_src.py

⚠️ VI SAO CAN: du an da nhieu lan gap loi bo cuc ma doc CSS khong thay - nhan bi cat,
   thanh dai bang mot dai dac, hai khoi de nhau. Bang nay co nhan DAI (mot chien dich
   ba phan la toi 74 ky tu) trong mot bieu do thanh ngang, tuc dung cho lop loi do.

⚠️ Gieo so LECH HAN so that de biet trang doc SERVER chu khong tu tinh.
"""
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
OUT = os.path.dirname(os.path.abspath(__file__))
OK = FAIL = 0

SOURCES = [
    {"src": "fb/post/ra-mat-20-08", "waitlist": 41, "signups": 17, "active7": 11, "earthDone": 6},
    {"src": "fb/post/gioi-thieu-comet-va-byte", "waitlist": 63, "signups": 9, "active7": 2, "earthDone": 0},
    {"src": "zalo/oa/thang-8", "waitlist": 12, "signups": 5, "active7": 4, "earthDone": 3},
    {"src": "", "waitlist": 28, "signups": 6, "active7": 3, "earthDone": 1},
    {"src": "fb/story/test", "waitlist": 4, "signups": 0, "active7": 0, "earthDone": 0},
]

REPORT = {
    "generatedAt": "2026-08-18T10:00:00Z", "logSince": "2026-08-09", "windowDays": 90,
    "truncated": False, "scannedItems": 120, "histRows": 40,
    "totalUsers": 37, "adminAccounts": 1, "pending": 2, "waitlist": 148, "emailClaims": 37,
    "newD1": 1, "newD7": 6, "newD30": 20, "silent": 3,
    "dau": 4, "wau": 20, "mau": 33, "stickiness": 12,
    "active7": 20, "active30": 33, "churn": 13,
    "quizAnswered": 400, "quizCorrect": 300, "accuracy": 75,
    "meteorsEarned": 5000, "meteorsBalance": 1800, "spentPct": 64, "gameSeconds": 9000,
    "days": [], "funnel": [], "retention": [], "hours": [0] * 24, "weekdays": [0] * 7,
    "accuracyDist": [], "levelDist": [], "badgeDist": [], "weakTerms": [],
    "topContent": {}, "rareBadges": [], "missions": [],
    "sources": SOURCES, "userTable": [],
}


def check(label, cond, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(extra)) if extra else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(extra))


print("=== BANG NGUON tren admin-report.html ===")
with sync_playwright() as p:
    br = p.chromium.launch()
    for wname, w, h in (("desktop", 1440, 900), ("dienthoai", 390, 844)):
        ctx = br.new_context(viewport={"width": w, "height": h},
                             locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
        # Gia lap ca phien dang nhap admin lan phan hoi /admin/stats.
        # ⚠️ Gia lap dung ham trang GOI (`getAdminStats`), khong chan HTTP: trang khong
        #    bao gio goi mang neu chua co phien Firebase that (bai hoc smoke_checkout).
        ctx.add_init_script(
            "window.__REP = " + json.dumps({"ok": True, "cached": False,
                                            "generatedAt": REPORT["generatedAt"],
                                            "report": REPORT}) + ";"
            "Object.defineProperty(window,'AstroQAuth',{configurable:true,"
            "get(){return {getAdminStats:function(){"
            "  return Promise.resolve({ok:true, status:200, data:window.__REP});"
            "}, idToken:async()=>'tok'};}, set(){}});")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(BASE + "/admin-report.html", wait_until="domcontentloaded")
        try:
            pg.wait_for_selector("#p-src svg, #p-src table", timeout=15000)
        except Exception:
            check(wname + ": bang nguon ve ra", False, "khong thay #p-src co noi dung")
            print("     " + (pg.inner_text("#p-src")[:160] if pg.query_selector("#p-src") else "(khong co #p-src)"))
            ctx.close()
            continue

        check(wname + ": 0 loi trang", not errs, errs[:2])
        txt = pg.inner_text("#p-src")
        check(wname + ": hien nhan chien dich that", "fb/post/ra-mat-20-08" in txt)
        check(wname + ": nhan rong doi ra chu", "không rõ nguồn" in txt, txt[:80].replace("\n", " | "))
        # ⚠️ Cot dang doc nhat phai NHIN THAY DUOC, khong nam trong tooltip: tren
        #    dien thoai khong re chuot duoc.
        check(wname + ": ve hang \"con hoat dong\" thay duoc",
              txt.count("còn hoạt động") == 4, txt.count("còn hoạt động"))
        check(wname + ": hai con so cua mot nguon deu hien", "17" in txt and "11" in txt)
        # ⚠️ Nguon chua ra tai khoan nao thi KHONG ve hang thu hai - mot thanh 0 kem
        #    chu "con hoat dong" doc ra thanh mot loi phan xet, trong khi chua co gi de do.
        check(wname + ": nguon 0 tai khoan KHONG co hang thu hai",
              txt.count("còn hoạt động") == len([x for x in SOURCES if x["signups"] > 0]),
              txt.count("còn hoạt động"))
        # ⚠️ Don vi la MOT CHU thi hbars noi thang vao sau so ("17tai khoan") va tran
        #    ra ngoai o giu cho 52px. Do bang chinh trieu chung do.
        check(wname + ": khong dinh don vi vao sau so",
              "tài khoản" not in txt,
              [l for l in txt.split(chr(10)) if "tài khoản" in l][:2])

        # ⚠️ Nhan dai la ca ly do bo do nay ton tai: mot chien dich ba phan dai toi 74
        #    ky tu, ma bieu do thanh ma nhan dai hon thanh thi khong con la bieu do.
        box = pg.evaluate("""() => {
            const b = document.querySelector('#p-src');
            const r = b.getBoundingClientRect();
            const bars = [...b.querySelectorAll('svg *')].map(n => n.getBoundingClientRect());
            return { w: r.width, tran: bars.some(x => x.right > r.right + 1 || x.left < r.left - 1) };
        }""")
        check(wname + ": khong co gi tran ra ngoai khung", box["tran"] is False, box)

        pg.locator("[data-card=sources]").scroll_into_view_if_needed()
        pg.wait_for_timeout(350)
        f = os.path.join(OUT, "src-%s.png" % wname)
        pg.locator("[data-card=sources]").screenshot(path=f)
        print("     anh: " + f)

        # Nut "Bang so" phai doi duoc sang bang, va bang phai co du 5 cot.
        pg.click("[data-card=sources] .swap")
        pg.wait_for_timeout(300)
        tbl = pg.inner_text("#p-src")
        check(wname + ": doi duoc sang bang so", "còn hoạt động" in tbl.casefold(), tbl[:90].replace("\n", " | "))
        pg.locator("[data-card=sources]").screenshot(path=os.path.join(OUT, "src-%s-bang.png" % wname))
        ctx.close()
    br.close()

print("")
print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
