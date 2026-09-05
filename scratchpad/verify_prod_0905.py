# -*- coding: utf-8 -*-
"""verify_prod_0905.py — ĐO TRÊN CHÍNH astroq.org sau lượt push 05/09/2026.

    python scratchpad/verify_prod_0905.py

⚠️⚠️ SỐ HIỆU BẢN DỰNG ĐƯỢC KIỂM **TRƯỚC MỌI THỨ KHÁC**, và script `sys.exit`
   nếu lệch. GitHub Pages xây mất 1–2 phút; đo trước lúc nó xong thì mọi phép
   kiểm phía sau nói về BẢN CŨ và "đạt" một cách RỖNG. Dự án đã có một ca bản
   thật đứng ở bản cũ gần một ngày (06/08/2026).

⚠️ Các file mới đều được nạp ĐỘNG hoặc là CSS, nên một file thiếu **không làm
   trang đỏ** — nó chỉ làm thẻ không bật lên. Vì thế phải đo CẢ HAI tầng:
   tầng mạng (200 + MIME đúng — Pages trả `text/plain` là ES module bị từ chối
   IM LẶNG) và tầng trang (mở ra, bấm thật, thẻ có hiện không).
"""
import re
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "https://astroq.org"
WANT = "2026.09.05.1"

_ok = _bad = 0


def check(cond, label, extra=""):
    global _ok, _bad
    if cond:
        _ok += 1
        print("  [OK]   %s" % label)
    else:
        _bad += 1
        print("  [HONG] %s %s" % (label, extra))
    return bool(cond)


def get(path, timeout=30):
    req = urllib.request.Request(
        BASE + path,
        headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, dict((k.lower(), v) for k, v in r.headers.items()), \
            r.read().decode("utf-8", "replace")


# ══════════════ [0] BẢN DỰNG — kiểm trước, lệch thì DỪNG ══════════════
print("\n=== [0] So hieu ban dung (kiem TRUOC moi thu khac) ===")
try:
    st, _, uic = get("/js/ui-common.js")
except Exception as e:
    print("  [HONG] khong tai duoc js/ui-common.js: %s" % e)
    sys.exit(2)

m = re.search(r'var\s+VERSION\s*=\s*"([^"]+)"', uic)
got = m.group(1) if m else "(khong doc duoc)"
if got != WANT:
    print("  [HONG] ban dung tren Pages la %s, doi %s" % (got, WANT))
    print("         => Pages CHUA xay xong. Doi ~1 phut roi chay lai.")
    sys.exit(2)
check(True, "ban dung dung %s" % WANT)

# ══════════════ [1] File mới: 200 + MIME đúng ══════════════
print("\n=== [1] File moi tra 200 voi MIME dung ===")
for path, want_mime in (("/js/guest-claim.js", "javascript"),
                        ("/css/guest-claim.css", "text/css"),
                        ("/js/game-shell.js", "javascript"),
                        ("/js/progress.js", "javascript"),
                        ("/js/mission-stage.js", "javascript")):
    try:
        st, hd, body = get(path)
    except Exception as e:
        check(False, "%s tra 200" % path, str(e))
        continue
    ct = hd.get("content-type", "")
    check(st == 200 and want_mime in ct, "%s -> %d (%s)" % (path, st, ct))

# ══════════════ [2] Mã trên Pages mang đúng cơ chế vừa dựng ══════════════
print("\n=== [2] Ma tren Pages mang dung co che ===")
_, _, gs = get("/js/game-shell.js")
check("LEAVE_IDS" in gs, "game-shell.js co bang LEAVE_IDS")
check("wireClaim" in gs, "game-shell.js co wireClaim()")
check("queuedGames" in gs, "game-shell.js goi queuedGames()")
# Chặn cú bấm rồi PHÁT LẠI — cờ replaying là chốt chống hỏi hai lần.
check("replaying" in gs, "giu co `replaying` (phat lai cu bam, khong tu dieu huong)")

_, _, pr = get("/js/progress.js")
check("queuedGames" in pr, "progress.js xuat queuedGames()")
check("queuedSteps" in pr, "progress.js van xuat queuedSteps() (hai phep dem KHAC nhau)")

_, _, gc = get("/js/guest-claim.js")
check("signedIn" in gc, "guest-claim doc `signedIn` (khong doc `ok`)")
check("sub_game" in gc, "guest-claim co cau chu rieng cho khu game (`sub_game`)")

# ══════════════ [3] Mở trang thật trên Chromium ══════════════
print("\n=== [3] Mo chinh astroq.org tren Chromium ===")
try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    print("  [BO QUA] khong co Playwright: %s" % e)
    print("\n=== KET QUA: %d dat / %d hong ===" % (_ok, _bad))
    sys.exit(1 if _bad else 0)

SEED = """
try {
  localStorage.setItem('astroq-lang','vi');
  localStorage.removeItem('astroq-user');
  localStorage.removeItem('astroq-claim-snooze');
  var q = [];
  for (var i = 0; i < 3; i++) q.push({
    type:'game', game:'dodge', score:10, seconds:5, meteors:1,
    opId:'zz-prod-' + i
  });
  localStorage.setItem('astroq-progress-queue', JSON.stringify(q));
} catch (e) {}
"""

with sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(SEED)
    pg = ctx.new_page()
    errs, bad_assets = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text)
          if m.type == "error" else None)
    pg.on("response", lambda r: bad_assets.append("%d %s" % (r.status, r.url))
          if r.status >= 400 else None)

    pg.goto(BASE + "/game-dodge.html", wait_until="load", timeout=60000)
    pg.wait_for_timeout(1500)

    check(not errs, "0 loi trang", str(errs[:2]))
    check(not bad_assets, "0 asset hong", str(bad_assets[:2]))

    n_q = pg.evaluate(
        "() => (window.AstroQProgress && AstroQProgress.queuedGames) "
        "? AstroQProgress.queuedGames() : -1")
    check(n_q == 3, "queuedGames() doc dung 3 luot trong hang cho", "(%s)" % n_q)

    # Đối chứng: cùng hàng chờ đó, queuedSteps('earth') PHẢI ra 0. Hai con số
    # bằng nhau nghĩa là một trong hai hàm đang đếm bừa.
    n_s = pg.evaluate(
        "() => (window.AstroQProgress && AstroQProgress.queuedSteps) "
        "? AstroQProgress.queuedSteps('earth') : -1")
    check(n_s == 0, "doi chung: queuedSteps('earth') = 0", "(%s)" % n_s)

    has_mod = pg.evaluate("() => !!window.AstroQGuestClaim")
    check(has_mod, "trang game co nap module guest-claim")

    # Bấm THẬT nút rời trang. Ở màn brief (chưa vào lượt) nên `playing()` false.
    opened = True
    try:
        pg.click("#back", timeout=5000)
        pg.wait_for_selector(".gc.show", timeout=8000)
    except Exception:
        opened = False
    check(opened, "bam nut ROI TRANG -> the bat len",
          "" if opened else "url=%s" % pg.url)

    if opened:
        txt = pg.inner_text(".gc")
        check("lượt" in txt.lower(), "cau chu goi la LUOT (khong phai chang)",
              txt[:80].replace("\n", " "))
        check("3" in txt, "cau chu neu dung so 3", txt[:80].replace("\n", " "))
        check("chặng" not in txt.lower(), "khong dung chu 'chang' o khu game")

        # Bấm "Để sau" thì phải đi tiếp về games.html như trẻ vừa yêu cầu.
        try:
            pg.click("#gc-skip", timeout=5000)
            pg.wait_for_url("**/games.html", timeout=10000)
            check(True, "bam 'De sau' -> di tiep ve games.html")
        except Exception as e:
            check(False, "bam 'De sau' -> di tiep ve games.html",
                  "url=%s %s" % (pg.url, e))

    # ── trang nhiệm vụ vẫn mở được, 0 lỗi ──
    pg2 = ctx.new_page()
    e2, a2 = [], []
    pg2.on("pageerror", lambda e: e2.append(str(e)))
    pg2.on("console", lambda m: e2.append("console: " + m.text)
           if m.type == "error" else None)
    pg2.on("response", lambda r: a2.append("%d %s" % (r.status, r.url))
           if r.status >= 400 else None)
    pg2.goto(BASE + "/mission-earth.html", wait_until="load", timeout=60000)
    pg2.wait_for_timeout(1500)
    check(not e2, "mission-earth.html: 0 loi trang", str(e2[:2]))
    check(not a2, "mission-earth.html: 0 asset hong", str(a2[:2]))
    check(pg2.evaluate("() => !!window.AstroQGuestClaim"),
          "mission-earth.html co nap module guest-claim")

    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (_ok, _bad))
sys.exit(1 if _bad else 0)
