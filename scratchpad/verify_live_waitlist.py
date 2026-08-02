# -*- coding: utf-8 -*-
"""
verify_live_waitlist.py — do form waitlist tren BAN THAT https://astroq.org.

Khong gia lap gi ca: trinh duyet that -> Lambda that -> DynamoDB that -> SES that.
Day la phep do duy nhat chung minh nguoi dung that su dang ky duoc.

⚠️ Dung dia chi gia lap cua SES; gui vao dia chi khong ton tai la sinh bounce.
Test tu don ban ghi minh tao ra.
"""
import json, subprocess, sys, time
from playwright.sync_api import sync_playwright

SITE = "https://astroq.org/"
MAIL = "success+live%d@simulator.amazonses.com" % int(time.time())
TABLE = "astroq-main"
OK = FAIL = 0


def check(label, cond, extra=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(extra)) if extra else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(extra))


def ddb(cmd, email):
    key = json.dumps({"PK": {"S": "WAITLIST#" + email}, "SK": {"S": "SIGNUP"}})
    r = subprocess.run(["aws", "dynamodb", cmd, "--table-name", TABLE, "--key", key,
                        "--output", "json"], capture_output=True, text=True)
    return (json.loads(r.stdout or "{}") or {}).get("Item") if cmd == "get-item" else None


print("=== BAN THAT: %s ===" % SITE)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        perr, cerr, calls = [], [], []
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.on("console", lambda m: cerr.append(m.text) if m.type == "error" else None)
        pg.on("response", lambda r: calls.append((r.url, r.status)) if "/waitlist" in r.url else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi')")
        pg.goto(SITE, wait_until="networkidle")
        pg.eval_on_selector("#waitlist", "e=>e.scrollIntoView({block:'center'})")
        pg.wait_for_timeout(500)

        # --- bo trong roi bam nut ---
        pg.click("#wl-submit")
        pg.wait_for_timeout(500)
        check("bo trong -> co loi JS?  (phai KHONG)", perr == [], perr)
        check("bo trong -> hien loi ngay duoi o email",
              pg.get_attribute("#wl-err", "hidden") is None)
        check("cau bao loi dung tieng Viet", "Nhập email" in pg.inner_text("#wl-err"),
              repr(pg.inner_text("#wl-err").strip()))
        eb = pg.query_selector("#wl-err").bounding_box()
        check("loi nam trong khung nhin", eb and 0 <= eb["y"] <= 900, eb)

        # --- gui that ---
        pg.fill("#wl-email", MAIL)
        pg.click("#wl-submit")
        pg.wait_for_timeout(6000)
        check("da goi POST /waitlist", len(calls) == 1, calls)
        check("server tra 202", calls and calls[0][1] == 202, calls)
        check("the 'da dang ky' hien ra", pg.get_attribute("#wl-done", "hidden") is None)
        done = pg.inner_text("#wl-done")
        check("bao thanh cong + nhac dung email", "thành công" in done and MAIL in done,
              repr(done[:90]))
        check("bao 'kiem tra hom thu' (SES that su da nhan thu)", "Kiểm tra hòm thư" in done)
        check("khong loi JS", perr == [], perr)
        check("khong loi console (khong bi CORS chan)", cerr == [], cerr)
        b.close()

    # --- da vao DynamoDB that chua ---
    it = ddb("get-item", MAIL)
    check("ban ghi da nam trong DynamoDB", it is not None)
    if it:
        check("luu dung email", it["email"]["S"] == MAIL)
        check("danh dau da gui thu", it["welcomed"]["BOOL"] is True)
        check("ghi origin la astroq.org", it["source"]["S"] == "https://astroq.org", it["source"])
        check("KHONG dat ttl", "ttl" not in it, list(it.keys()))
finally:
    ddb("delete-item", MAIL)
    check("da don ban ghi test", ddb("get-item", MAIL) is None)

print("\n================ KET QUA: %d dat / %d hong ================" % (OK, FAIL))
sys.exit(1 if FAIL else 0)
