# -*- coding: utf-8 -*-
"""perf_ab.py — A/B tren CUNG mot may chu, CUNG mot ho so mang.

`dash-before.html` duoc SINH RA tu `dashboard.html` bang cach go dung ba thay doi
23/08/2026 (preconnect+modulepreload · module o head · paintCachedHud), nen hai ban
chi khac nhau o dung nhung thu dang do. Cung server tinh (localhost) nen chenh lech
khong den tu CDN.

  python scratchpad/perf_ab.py
"""
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import threading
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

PORT = 8000
API = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
TABLE = "astroq-main"
NET = (9 * 1024 * 1024 / 8, 3 * 1024 * 1024 / 8, 150)   # 4G, RTT 150ms


# ── sinh ban "truoc" ─────────────────────────────────────────────────────────
def build_before():
    src = open("dashboard.html", encoding="utf-8").read()
    out = src

    # 1. bo khoi preconnect + modulepreload
    out = re.sub(r"<!-- =+ BẮT TAY TRƯỚC.*?firebase-auth\.js\" />\n\n",
                 "", out, flags=re.S)
    # 2. tra the module ve cuoi body
    out = re.sub(r"<!-- ⚠️ NẰM Ở HEAD.*?<script type=\"module\" src=\"js/firebase-auth\.js\"></script>\n",
                 "", out, flags=re.S)
    out = re.sub(r"<!-- `js/firebase-auth\.js` đã chuyển lên <head>.*?-->\n</body>",
                 "<script type=\"module\" src=\"js/firebase-auth.js\"></script>\n</body>",
                 out, flags=re.S)
    # 3. bo loi goi ve-tu-cache
    out = re.sub(r"  /\* ⚠️ THỨ TỰ BẮT BUỘC.*?\n  paintCachedHud\(\);\n", "", out, flags=re.S)

    checks = [
        ("bo preconnect", "rel=\"preconnect\"" not in out),
        ("bo modulepreload", "modulepreload" not in out),
        ("module ve cuoi body", out.rstrip().endswith("</html>")
         and out.index("js/firebase-auth.js") > out.index("<body>")),
        ("chi con MOT the module firebase-auth", out.count("src=\"js/firebase-auth.js\"") == 1),
        ("bo loi goi paintCachedHud", "\n  paintCachedHud();" not in out),
        ("van con dinh nghia paintCachedHud", "function paintCachedHud()" in out),
    ]
    for label, ok in checks:
        print("  [%s] %s" % ("OK  " if ok else "HONG", label))
    if not all(c[1] for c in checks):
        sys.exit("KHONG sinh duoc ban 'truoc' dung — dung han.")
    open("dash-before.html", "w", encoding="utf-8").write(out)
    return "dash-before.html"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


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
    if (window.AstroQAuth) stamp('sdk');
    if (window.__M.xp != null && window.__M.desk != null) clearInterval(iv);
  }, 16);
})();
"""

SITE = "http://localhost:%d" % PORT


def login(b, email, pw):
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-tour-seen','1');"
                        "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(SITE + "/landing-app.html", wait_until="load")
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
    return ctx, pg


def measure(ctx, pg, page, label, warm_first):
    cdp = ctx.new_cdp_session(pg)
    cdp.send("Network.enable")
    if warm_first:
        # Mot luot "lam nong" de cache HUD co du lieu — dung canh tre QUAY LAI.
        pg.goto(SITE + "/" + page, wait_until="load")
        pg.wait_for_timeout(3000)
    cdp.send("Network.emulateNetworkConditions", {
        "offline": False, "downloadThroughput": NET[0],
        "uploadThroughput": NET[1], "latency": NET[2]})
    pg.add_init_script(PROBE)
    pg.goto(SITE + "/" + page, wait_until="commit")
    for _ in range(150):
        m = pg.evaluate("() => window.__M || {}")
        if m.get("xp") is not None and m.get("desk") is not None:
            break
        pg.wait_for_timeout(100)
    m = pg.evaluate("() => window.__M || {}")
    st = pg.evaluate("""() => {
      const b = document.getElementById('xp-bar');
      const f = document.getElementById('desk-float');
      return { w: b ? b.style.width : '?', k: f ? f.childElementCount : -1 };
    }""")
    cdp.send("Network.emulateNetworkConditions", {
        "offline": False, "downloadThroughput": -1, "uploadThroughput": -1, "latency": 0})
    print("  %-34s XP %6s ms   MAU VAT %6s ms   (SDK %5s ms)  ket qua %s / %d moc"
          % (label, m.get("xp", "-"), m.get("desk", "-"), m.get("sdk", "-"),
             st["w"], st["k"]))
    return m


uid = tok = None
email = "perfab-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
httpd = None
try:
    print("=== [0] Sinh ban 'truoc' tu dashboard.html ===")
    before = build_before()
    httpd = serve()
    print("  may chu tinh: %s" % SITE)

    print("\n=== [1] Tai khoan co tien do that ===")
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
    call("GET", "/me/achievements", tok)          # tra no cap huy hieu truoc khi do
    print("  xong (%d mau vat treo)" % len(unl))

    print("\n=== [2] Do, 4G RTT 150ms ===")
    with sync_playwright() as p:
        b = p.chromium.launch()

        ctx, pg = login(b, email, pw)
        measure(ctx, pg, before, "TRUOC  (lan dau)", warm_first=False)
        measure(ctx, pg, before, "TRUOC  (quay lai)", warm_first=True)
        ctx.close()

        ctx, pg = login(b, email, pw)
        measure(ctx, pg, "dashboard.html", "SAU    (lan dau)", warm_first=False)
        measure(ctx, pg, "dashboard.html", "SAU    (quay lai)", warm_first=True)
        ctx.close()
        b.close()
finally:
    print("\n=== [3] Tu don ===")
    if httpd:
        httpd.shutdown()
    try:
        os.remove("dash-before.html")
        print("  da xoa dash-before.html")
    except Exception:
        pass
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
