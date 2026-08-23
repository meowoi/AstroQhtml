# -*- coding: utf-8 -*-
"""perf_dash_slow.py — DO tren duong truyen THAT cua tre, ba canh:

  A. mang 4G binh thuong, khong co viec ton dong
  B. mang 4G, vua choi game xong -> 5 viec nam trong `astroq-progress-queue`
  C. mang 3G cham

Bam gio dung hai thu chu du an noi la cham: `#xp-bar` va `#desk-float`.

  python scratchpad/perf_dash_slow.py
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

# Ho so mang: (ten, down bytes/s, up bytes/s, latency ms)
NETS = [
    ("4G  (9 Mbps, RTT 150ms)", 9 * 1024 * 1024 / 8, 3 * 1024 * 1024 / 8, 150),
    ("3G  (1.6 Mbps, RTT 300ms)", 1600 * 1024 / 8, 750 * 1024 / 8, 300),
]


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
    if (document.querySelector('.xp-bar')) stamp('shell');
    if (window.AstroQAuth) stamp('sdk');
    if (window.__M.xp != null && window.__M.desk != null) clearInterval(iv);
  }, 16);
})();
"""

RES_JS = """() => performance.getEntriesByType('resource')
  .filter(r => /vendor|progress[.]js|specimen|achievements|amazonaws|identitytoolkit|onboarding|missions/.test(r.name))
  .map(r => ({ n: r.name.split('/').slice(-1)[0].slice(0, 40),
               s: Math.round(r.startTime), e: Math.round(r.responseEnd) }))
  .sort((a, b) => a.s - b.s)"""


def queue_script(n):
    """5 viec ton dong nhu vua choi game xong o trang khong co token."""
    items = [{"type": "game", "game": "catch", "score": 100 + i, "seconds": 60,
              "meteors": 5, "opId": str(uuid.uuid4())} for i in range(n)]
    return ("try{localStorage.setItem('astroq-progress-queue',%s)}catch(e){}"
            % json.dumps(json.dumps(items)))


def run_case(b, label, net, email, pw, queued=0):
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-tour-seen','1');"
                        "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
    pg = ctx.new_page()
    # Dang nhap o toc do day du — chi tinh gio LUOT MO DASHBOARD.
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

    if queued:
        pg.evaluate("s => eval(s)", queue_script(queued))

    cdp = ctx.new_cdp_session(pg)
    cdp.send("Network.enable")
    cdp.send("Network.emulateNetworkConditions", {
        "offline": False, "downloadThroughput": net[1],
        "uploadThroughput": net[2], "latency": net[3]})
    pg.add_init_script(PROBE)

    pg.goto(SITE + "/dashboard.html", wait_until="commit")
    for _ in range(150):
        m = pg.evaluate("() => window.__M || {}")
        if m.get("xp") is not None and m.get("desk") is not None:
            break
        pg.wait_for_timeout(200)
    m = pg.evaluate("() => window.__M || {}")
    print("\n  === %s ===" % label)
    print("     khung .xp-bar co o      %6s ms   (tre thay o trong)"
          % m.get("shell", "-"))
    print("     AstroQAuth san sang o   %6s ms" % m.get("sdk", "-"))
    print("  >> THANH XP hien so THAT   %6s ms" % m.get("xp", "KHONG HIEN"))
    print("  >> MAU VAT hien            %6s ms" % m.get("desk", "KHONG HIEN"))
    print("     %-42s %7s %7s" % ("resource", "start", "end"))
    for r0 in pg.evaluate(RES_JS):
        print("     %-42s %7d %7d" % (r0["n"], r0["s"], r0["e"]))
    ctx.close()


uid = tok = None
email = "perfslow-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
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
    # Goi truoc mot lan de "tra no" cap huy hieu -> khong lan vao phep do
    call("GET", "/me/achievements", tok)
    print("  xong: %s mau vat treo, huy hieu da tra no" % len(unl))

    print("\n=== [2] Do dashboard ===")
    with sync_playwright() as p:
        b = p.chromium.launch()
        run_case(b, "A. 4G, khong co viec ton dong", NETS[0], email, pw)
        run_case(b, "B. 4G, vua choi xong (5 viec ton dong)", NETS[0], email, pw, queued=5)
        run_case(b, "C. 3G cham, khong ton dong", NETS[1], email, pw)
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
