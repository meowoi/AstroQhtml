# -*- coding: utf-8 -*-
"""perf_prod_return.py — DO LUOT QUAY LAI tren BAN THAT (astroq.org).

perf_dash_slow.py do luot vao LAN DAU cua mot tai khoan MOI: `astroq-hud` rong
nen paintCachedHud thoat som (known:false) — dung luot ma cache khong giup duoc.
Bo nay do luot THUONG GAP NHAT: mo dashboard lan 1 (server ghi cache), roi mo
lan 2 trong CUNG mot context (cache + cache trinh duyet con nguyen).

  python scratchpad/perf_prod_return.py

⚠️ Phai dung CUNG mot browser context cho ca hai luot. Context moi la cache
   trinh duyet rong VA localStorage rong -> do ra hai luot "lan dau".
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

# 4G: 9 Mbps down, 3 Mbps up, RTT 150ms
NET = (9 * 1024 * 1024 / 8, 3 * 1024 * 1024 / 8, 150)


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


PROBE = """
window.__M = {};
(function(){
  var stamp = function(k){ if (window.__M[k] == null) window.__M[k] = Math.round(performance.now()); };
  var iv = setInterval(function(){
    var b = document.getElementById('xp-bar');
    if (b && b.style.width && b.style.width !== '0%') stamp('xp');
    var f = document.getElementById('desk-float');
    if (f && f.childElementCount > 0) stamp('desk');
    if (window.__M.xp != null && window.__M.desk != null) clearInterval(iv);
  }, 16);
})();
"""

HUD_JS = """() => { try { return localStorage.getItem('astroq-hud'); } catch(e){ return null; } }"""


def wait_marks(pg, tries=150):
    for _ in range(tries):
        m = pg.evaluate("() => window.__M || {}")
        if m.get("xp") is not None and m.get("desk") is not None:
            return m
        pg.wait_for_timeout(200)
    return pg.evaluate("() => window.__M || {}")


uid = tok = None
email = "perfret-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
try:
    print("=== [1] Tao tai khoan co tien do that ===")
    uid, tok, pw = _fbtest.make_verified(email)
    aws("dynamodb", "put-item", "--table-name", TABLE, "--item",
        json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": {"S": "PROFILE"},
                    "uid": {"S": uid}, "email": {"S": email},
                    "name": {"S": "Perf Pilot"},
                    "createdAt": {"S": "2026-08-01T00:00:00.000Z"}}))
    for i in range(8):
        call("POST", "/me/progress", tok, {"type": "quiz", "correct": 5, "total": 5,
                                           "meteors": 20, "opId": str(uuid.uuid4())})
    for i in range(12):
        call("POST", "/me/progress", tok, {"type": "game", "game": "catch", "score": 900,
                                           "seconds": 120, "meteors": 15,
                                           "opId": str(uuid.uuid4())})
    for i in range(6):
        call("POST", "/me/progress", tok, {"type": "lesson", "id": "L%d" % i,
                                           "meteors": 5, "opId": str(uuid.uuid4())})
    for pid in ["earth", "mars", "venus", "jupiter"]:
        call("POST", "/me/progress", tok, {"type": "planet", "id": pid,
                                           "meteors": 10, "opId": str(uuid.uuid4())})
    st, sp = call("GET", "/me/specimens", tok)
    unl = [s["id"] for s in ((sp.get("specimens") or {}).get("specimens") or [])
           if s.get("unlocked")][:3]
    call("PUT", "/me/specimens/desk", tok,
         {"desk": [{"hook": h, "id": i} for h, i in zip(["L1", "R1", "L3"], unl)]})
    # tra no cap huy hieu TRUOC khi bam gio (bai hoc 23/08: lan dau /me/achievements
    # ghi 2 luot DynamoDB nen cham 2.9s, khong phai hoi quy)
    call("GET", "/me/achievements", tok)
    print("  xong: %s mau vat treo, huy hieu da tra no" % len(unl))

    print("\n=== [2] Do tren %s, 4G (9 Mbps, RTT 150ms) ===" % SITE)
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                            "localStorage.setItem('astroq-tour-seen','1');"
                            "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
        ctx.set_default_timeout(60000)
        ctx.set_default_navigation_timeout(60000)
        pg = ctx.new_page()

        # Dang nhap o toc do day du — chi tinh gio LUOT MO DASHBOARD.
        pg.goto(SITE + "/landing-app.html", wait_until="domcontentloaded")
        pg.wait_for_selector("#btn-try", timeout=30000)
        pg.click("#btn-try")
        pg.wait_for_selector("#to-login", state="visible", timeout=30000)
        pg.click("#to-login")
        pg.wait_for_selector("#login-email", state="visible", timeout=30000)
        pg.fill("#login-email", email)
        pg.fill("#login-pass", pw)
        pg.click("#auth-login button.auth-submit")
        for _ in range(60):
            try:
                if pg.evaluate("() => !!(window.AstroQ && AstroQ.getUser && AstroQ.getUser())"):
                    break
            except Exception:
                pass
            pg.wait_for_timeout(500)

        cdp = ctx.new_cdp_session(pg)
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", {
            "offline": False, "downloadThroughput": NET[0],
            "uploadThroughput": NET[1], "latency": NET[2]})
        pg.add_init_script(PROBE)

        # --- LUOT 1: cache rong (astroq-hud chua duoc ghi lan nao) ---
        hud0 = pg.evaluate(HUD_JS)
        pg.goto(SITE + "/dashboard.html", wait_until="commit")
        m1 = wait_marks(pg)
        hud1 = pg.evaluate(HUD_JS)

        # --- LUOT 2: CUNG context -> cache HUD + cache trinh duyet con nguyen ---
        pg.goto(SITE + "/dashboard.html", wait_until="commit")
        m2 = wait_marks(pg)

        print("\n  %-28s %10s %10s" % ("", "LUOT 1", "LUOT 2"))
        print("  %-28s %10s %10s" % ("THANH XP hien so THAT",
                                     m1.get("xp", "-"), m2.get("xp", "-")))
        print("  %-28s %10s %10s" % ("MAU VAT hien",
                                     m1.get("desk", "-"), m2.get("desk", "-")))
        print("\n  astroq-hud truoc luot 1: %s" % ("(rong)" if not hud0 else hud0[:70]))
        print("  astroq-hud sau  luot 1: %s" % ("(rong)" if not hud1 else hud1[:70]))

        xp1, xp2 = m1.get("xp"), m2.get("xp")
        if isinstance(xp1, int) and isinstance(xp2, int) and xp1 > 0:
            print("\n  >> XP: %d ms -> %d ms  (%+.0f%%)" % (xp1, xp2, (xp2 - xp1) * 100.0 / xp1))
        if not hud1:
            print("\n  ⚠️ CACHE KHONG DUOC GHI o luot 1 -> luot 2 khong the nhanh hon.")
        ctx.close()
        b.close()
finally:
    print("\n=== [3] Tu don ===")
    if uid:
        r = aws("dynamodb", "query", "--table-name", TABLE,
                "--key-condition-expression", "PK = :p",
                "--expression-attribute-values", json.dumps({":p": {"S": "USER#%s" % uid}}),
                "--output", "json")
        if r.returncode == 0:
            for it in json.loads(r.stdout or "{}").get("Items", []):
                aws("dynamodb", "delete-item", "--table-name", TABLE, "--key",
                    json.dumps({"PK": it["PK"], "SK": it["SK"]}))
            print("  da xoa dong DynamoDB")
    if tok:
        print("  xoa tai khoan Firebase: %s" % _fbtest.delete(tok))
