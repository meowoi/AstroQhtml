# -*- coding: utf-8 -*-
"""perf_dashboard.py — DO THAT: sau khi dang nhap, thanh XP va mau vat hien luc nao.

Cach do: tao tai khoan that co tien do that (XP > 0 + 3 mau vat treo o ban dieu
khien), dang nhap tren astroq.org, roi F5 dashboard va bam gio hai moc:
  · `#xp-bar` co width khac 0%   -> thanh tien do XP da ve so THAT
  · `#desk-float` co con         -> hang mau vat da hien
Kem timeline resource cua nhung file nam tren duong toi hai moc do.

  python scratchpad/perf_dashboard.py
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
    var h = document.getElementById('hud-xp') || document.querySelector('.xp-bar');
    if (h) stamp('shell');
    if (window.__M.xp != null && window.__M.desk != null) clearInterval(iv);
  }, 16);
})();
"""

STATE_JS = """() => {
  const b = document.getElementById('xp-bar');
  const f = document.getElementById('desk-float');
  return { xpWidth: b ? b.style.width : '(no #xp-bar)',
           deskKids: f ? f.childElementCount : -1,
           deskHidden: f ? f.hidden : null,
           url: location.pathname };
}"""

RES_JS = """() => performance.getEntriesByType('resource')
  .filter(r => /firebase|progress[.]js|specimen|achievements|amazonaws|securetoken|identitytoolkit|onboarding/.test(r.name))
  .map(r => ({ n: r.name.split('/').slice(-1)[0].slice(0, 42),
               s: Math.round(r.startTime), e: Math.round(r.responseEnd),
               kb: Math.round((r.transferSize || r.encodedBodySize || 0) / 1024) }))
  .sort((a, b) => a.s - b.s)"""

NAV_JS = """() => {
  const n = performance.getEntriesByType('navigation')[0] || {};
  return { di: n.domInteractive, dcl: n.domContentLoadedEventEnd,
           load: n.loadEventEnd, resp: n.responseEnd };
}"""

uid = tok = None
email = "perf-dash-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
try:
    print("\n=== [1] Tao mot dua tre CO tien do that ===")
    uid, tok, pw = _fbtest.make_verified(email)
    print("  uid = %s" % uid)
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item",
            json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": {"S": "PROFILE"},
                        "uid": {"S": uid}, "email": {"S": email},
                        "name": {"S": "Perf Pilot"},
                        "createdAt": {"S": "2026-08-01T00:00:00.000Z"}}))
    print("  PROFILE: rc=%s %s" % (r.returncode, r.stderr.strip()[:120]))

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

    st, d = call("GET", "/me/achievements", tok)
    lv = (d or {}).get("level") or {}
    print("  level=%s xp=%s pct=%s" % (lv.get("level"), lv.get("xp"), lv.get("pct")))

    st, sp = call("GET", "/me/specimens", tok)
    box = (sp.get("specimens") or {})
    unlocked = [s["id"] for s in (box.get("specimens") or []) if s.get("unlocked")][:3]
    print("  mau vat da mo khoa: %s" % unlocked)
    if unlocked:
        hooks = ["L1", "R1", "L3"][:len(unlocked)]
        st, dd = call("PUT", "/me/specimens/desk", tok,
                      {"desk": [{"hook": h, "id": i} for h, i in zip(hooks, unlocked)]})
        print("  treo len ban dieu khien: %s %s" % (st, json.dumps(dd)[:160]))

    print("\n=== [2] Dang nhap that roi do dashboard ===")
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                            "localStorage.setItem('astroq-tour-seen','1');"
                            "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
        pg = ctx.new_page()
        pg.goto(SITE + "/landing-app.html", wait_until="load")
        pg.wait_for_selector("#btn-try", timeout=25000)
        pg.click("#btn-try")
        pg.wait_for_selector("#to-login", state="visible", timeout=25000)
        pg.click("#to-login")
        pg.wait_for_selector("#login-email", state="visible", timeout=25000)
        pg.fill("#login-email", email)
        pg.fill("#login-pass", pw)
        pg.click("#auth-login button.auth-submit")
        for _ in range(40):
            try:
                if pg.evaluate("() => !!(window.AstroQ && AstroQ.getUser && AstroQ.getUser())"):
                    break
            except Exception:
                pass
            pg.wait_for_timeout(500)
        print("  da dang nhap, url = %s" % pg.url)

        pg.add_init_script(PROBE)
        for run in (1, 2, 3):
            pg.goto(SITE + "/dashboard.html", wait_until="commit")
            for _ in range(80):
                m = pg.evaluate("() => window.__M || {}")
                if m.get("xp") is not None and m.get("desk") is not None:
                    break
                pg.wait_for_timeout(200)
            m = pg.evaluate("() => window.__M || {}")
            nav = pg.evaluate(NAV_JS)
            print("\n  --- luot %d ---" % run)
            print("  responseEnd %6.0f  domInteractive %6.0f  DCL %6.0f  load %6.0f (ms)"
                  % (nav.get("resp") or 0, nav.get("di") or 0,
                     nav.get("dcl") or 0, nav.get("load") or 0))
            print("  >> KHUNG (.xp-bar) co o %5.0f ms" % (m.get("shell") if m.get("shell") is not None else -1))
            print("  >> THANH XP hien o   %7.0f ms" % (m.get("xp") if m.get("xp") is not None else -1))
            print("  >> MAU VAT hien o    %7.0f ms" % (m.get("desk") if m.get("desk") is not None else -1))
            print("  >> trang thai cuoi: %s" % json.dumps(pg.evaluate(STATE_JS)))
            print("  %-44s %8s %8s %6s" % ("resource", "start", "end", "KB"))
            for r0 in pg.evaluate(RES_JS):
                print("  %-44s %8d %8d %6d" % (r0["n"], r0["s"], r0["e"], r0["kb"]))
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
        else:
            print("  KHONG query duoc DynamoDB: %s" % r.stderr.strip()[:120])
    if tok:
        print("  xoa tai khoan Firebase: %s" % _fbtest.delete(tok))
