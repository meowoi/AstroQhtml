# -*- coding: utf-8 -*-
"""
smoke_mission_resume.py — VÀO CHƠI TIẾP nhiệm vụ từ bước còn dở, đo trên Chromium.

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/smoke_mission_resume.py

VÌ SAO CÓ BỘ NÀY (08/08/2026)
─────────────────────────────
Chủ dự án chơi thật: *"vào từ bảng nhiệm vụ vẫn thấy đi từ đầu"*. `missions.html`
hiện đúng chữ "Tiếp tục nhiệm vụ" và đúng "3/7 bước" — nhưng bấm vào thì
`mission-earth.html` mở lại từ bước ①, vì nó **không có token** (cố ý không nạp SDK
Firebase) nên tự nó không hỏi được `GET /me/missions`.

⚠️ ĐO TRÊN TRANG, KHÔNG ĐỌC CODE. Điều phải chứng minh là *trẻ mở ra thấy bước nào*,
   và `smoke_mission_earth.py` không hỏi tới câu đó (máy nó luôn sạch nên luôn ra
   bước ① — tức là bộ đo cũ MÙ với đúng lỗi này).

⚠️ KHÔNG GIEO `AstroQProgress` GIẢ. Bộ này phải đi qua CHÍNH `js/progress.js` thật:
   thứ đang kiểm là cầu nối cache giữa trang-có-token và trang-nhiệm-vụ, gieo bản giả
   là kiểm một cầu nối do chính mình dựng ra.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
URL = BASE + "/mission-earth.html"

# ⚠️ ĐỌC TỪ mission-earth.html, ĐỪNG GÁN CỨNG. Thứ tự bước đã đổi một lần
#    (03/08/2026, `life` lên trước `energy`) và bài học "gán cứng con số mà nơi khác
#    mới là nguồn sự thật" đã lặp lại đủ nhiều lần trong dự án này.
import io
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
_me = io.open(os.path.join(ROOT, "mission-earth.html"), encoding="utf-8").read()
_m = re.search(r"const STEP_IDS = \[([^\]]+)\]", _me)
assert _m, "khong doc duoc STEP_IDS trong mission-earth.html"
STEPS = re.findall(r"'([a-z0-9-]+)'", _m.group(1))
assert len(STEPS) >= 5, "STEP_IDS doc ra qua ngan: %r" % (STEPS,)

UID = "u-smoke-resume"
CACHE_KEY = "astroq-mission-steps"

ok = fail = 0
FAILS = []


def chk(cond, name, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  [ok]   {name}" + (f"  {extra}" if extra else ""))
    else:
        fail += 1
        FAILS.append(name)
        print(f"  [FAIL] {name}" + (f"  {extra}" if extra else ""))


def head(t):
    print(f"\n=== {t} ===")


def seed(page, done, complete=False, uid=UID, lang="vi", total=None):
    """Gieo cache 'đã xong bước nào' đúng hình dạng js/progress.js ghi ra."""
    box = {"uid": uid, "m": {"earth": {
        "done": done,
        "total": len(STEPS) if total is None else total,
        "complete": complete
    }}}
    page.add_init_script(
        "localStorage.setItem('astroq-lang', %s);"
        "localStorage.setItem('astroq-user', %s);"
        % (json.dumps(lang), json.dumps(json.dumps({"uid": UID, "name": "Smoke"})))
    )
    if done is not None:
        page.add_init_script(
            "localStorage.setItem(%s, %s);"
            % (json.dumps(CACHE_KEY), json.dumps(json.dumps(box))))


def boot(page):
    """Mở trang, chờ `__mission` có mặt. KHÔNG chờ #obj.show: bước mở ra có thể là
    bước bất kỳ, và `objective()` của mỗi bước gọi ở thời điểm khác nhau."""
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_function("() => !!window.__mission", timeout=40000)
    return errs


def state(page):
    return page.evaluate("""() => ({
      step: window.__mission.step,
      done: window.__mission.done,
      dotsOk: document.querySelectorAll('#steps .s.ok').length,
      dotsNow: document.querySelectorAll('#steps .s.now').length,
      toast: (document.getElementById('toast') || {}).textContent || '',
      toastShown: !!document.querySelector('#toast.show')
    })""")


def run(pw):
    br = pw.chromium.launch()

    # ── [1] Vào từ Sảnh Nhiệm Vụ giữa chừng: mở ĐÚNG bước còn dở ──────────────
    head("[1] Da xong 3 buoc -> mo tu buoc thu 4")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    seed(pg, STEPS[:3])
    errs = boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[3], "mo dung buoc con do",
        f"{st['step']} (can {STEPS[3]})")
    chk(sorted(st["done"]) == sorted(STEPS[:3]),
        "3 buoc truoc duoc ghi la da xong", str(st["done"]))
    chk(st["dotsOk"] == 3, "day cham to sang dung 3 cham", str(st["dotsOk"]))
    chk(st["dotsNow"] == 1, "co dung 1 cham 'dang lam'", str(st["dotsNow"]))
    # ⚠️ Phải NÓI RA rằng đang chơi tiếp — mở ra thấy bước 4 mà im lặng thì trẻ
    #    tưởng mình bị bỏ mất mấy bước đầu.
    chk(st["toastShown"], "co loi nhac dang choi tiep")
    chk(("4/%d" % len(STEPS)) in st["toast"],
        "loi nhac ghi dung buoc thu may", repr(st["toast"]))
    chk(not errs, "0 loi trang", str(errs[:2]))
    ctx.close()

    # ── [2] `?restart=1` bỏ qua việc chơi tiếp ────────────────────────────────
    head("[2] ?restart=1 -> choi lai tu buoc dau")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    seed(pg, STEPS[:3])
    pg.on("pageerror", lambda e: None)
    pg.goto(URL + "?restart=1", wait_until="domcontentloaded")
    pg.wait_for_function("() => !!window.__mission", timeout=40000)
    st = state(pg)
    chk(st["step"] == STEPS[0], "mo tu buoc dau", st["step"])
    chk(st["done"] == [], "khong danh dau buoc nao da xong", str(st["done"]))
    ctx.close()

    # ── [3] Xong cả nhiệm vụ -> lượt CHƠI LẠI, không phải chơi tiếp ───────────
    head("[3] Xong ca nhiem vu -> choi lai tu buoc dau, day cham trang")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    seed(pg, STEPS[:], complete=True)
    boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[0], "mo tu buoc dau", st["step"])
    chk(st["dotsOk"] == 0, "day cham TRANG (khong phai man tong ket)",
        str(st["dotsOk"]))
    chk(not st["toastShown"] or "1/" not in st["toast"],
        "khong noi 'choi tiep' cho luot choi lai")
    ctx.close()

    # ── [4] Cache của TÀI KHOẢN KHÁC thì bỏ qua ───────────────────────────────
    head("[4] Cache cua tai khoan khac -> khong dung")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    # ⚠️ Hai đứa trẻ dùng chung một máy: tiến độ của đứa trước KHÔNG được đưa đứa
    #    sau vào giữa nhiệm vụ — nó sẽ bỏ mất mấy bước đầu mà không hiểu vì sao.
    seed(pg, STEPS[:4], uid="u-nguoi-khac")
    boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[0], "mo tu buoc dau", st["step"])
    ctx.close()

    # ── [5] Máy sạch (chưa từng đọc được server) -> bước đầu ──────────────────
    head("[5] May sach -> mo tu buoc dau")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    seed(pg, None)
    boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[0], "mo tu buoc dau", st["step"])
    chk(not st["toastShown"], "khong noi gi ve chuyen choi tiep")
    ctx.close()

    # ── [6] LỖ giữa danh sách: mở ở LỖ, và KHÔNG đánh dấu bước phía sau ───────
    head("[6] Danh sach da xong bi ho o giua -> mo dung cho ho")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    # `finish(id)` thoát ngay nếu id đã nằm trong `done` -> KHÔNG gọi `next()`.
    # Nên đánh dấu một bước NẰM SAU bước đang chơi là nhiệm vụ kẹt cứng ở đó.
    seed(pg, [STEPS[0], STEPS[2]])
    boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[1], "mo dung cho ho", f"{st['step']} (can {STEPS[1]})")
    chk(st["done"] == [STEPS[0]],
        "KHONG danh dau buoc nam sau buoc dang choi (chong ket cung)",
        str(st["done"]))
    ctx.close()

    # ── [7] Chơi tiếp tới hết: bước cuối vẫn chốt được nhiệm vụ ───────────────
    head("[7] Mo o buoc cuoi -> van chot duoc nhiem vu")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    seed(pg, STEPS[:-1])
    errs = boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[-1], "mo dung buoc cuoi", st["step"])
    # Bước cuối mở bằng một câu thoại chờ trẻ bấm "Tiếp tục" -> bấm như trẻ.
    pg.wait_for_selector("#say.show", timeout=20000)
    for _ in range(6):
        if pg.locator("#core.show").count():
            break
        if pg.locator("#say-next:not(.hide)").count():
            pg.click("#say-next")
        pg.wait_for_timeout(400)
    chk(pg.locator("#core.show").count() == 1, "bang ho so buoc cuoi da mo")
    pg.evaluate("() => window.__mission.stamp()")
    # `outro()` của bước cuối cũng kết bằng một câu thoại CHỜ trẻ bấm "Tiếp tục" —
    # bấm như trẻ, đừng chờ màn tổng kết tự hiện.
    for _ in range(20):
        if pg.locator("#win.show").count():
            break
        if pg.locator("#say-next:not(.hide)").count():
            pg.click("#say-next")
        pg.wait_for_timeout(500)
    chk(pg.locator("#win.show").count() == 1, "man tong ket hien ra")
    chk(not errs, "0 loi trang", str(errs[:2]))
    ctx.close()

    # ── [8] Cầu nối: `AstroQProgress.missions()` GHI cache ────────────────────
    head("[8] Trang co token goi missions() -> ghi cache cho trang nhiem vu doc")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    # Gieo `AstroQAuth` giả (bản thật là ES module, trang này không nạp) để đo ĐÚNG
    # đường ghi cache trong `js/progress.js` chứ không phải một bản giả của nó.
    pg.add_init_script("""
      localStorage.setItem('astroq-user', JSON.stringify({uid:%s, name:'Smoke'}));
      var __auth = {
        postProgress: async function(){ return {ok:true, data:{}}; },
        missionStep:  async function(){ return {ok:true, data:{}}; },
        getMissions:  async function(){
          return { ok:true, status:200, data:{ missions:{ earth:{
            steps: %s, doneSteps: %s, done:false, codex:[], codexTotal:8 } } } };
        }
      };
      Object.defineProperty(window, 'AstroQAuth', {
        configurable:true, get:function(){ return __auth; }, set:function(){}
      });
    """ % (json.dumps(UID), json.dumps(STEPS), json.dumps(STEPS[:2])))
    pg.goto(BASE + "/missions.html", wait_until="domcontentloaded")
    pg.wait_for_function(
        "() => { const b = JSON.parse(localStorage.getItem(%s) || 'null');"
        "        return !!(b && b.m && b.m.earth); }" % json.dumps(CACHE_KEY),
        timeout=20000)
    box = pg.evaluate("() => JSON.parse(localStorage.getItem(%s))" % json.dumps(CACHE_KEY))
    chk(box["uid"] == UID, "cache dong dau uid", str(box.get("uid")))
    chk(box["m"]["earth"]["done"] == STEPS[:2],
        "cache ghi dung danh sach buoc da xong", str(box["m"]["earth"]["done"]))
    chk(box["m"]["earth"]["total"] == len(STEPS),
        "cache ghi dung tong so buoc", str(box["m"]["earth"]["total"]))
    # ⚠️ Cache chỉ được chứa ID BƯỚC — không một con số thưởng nào. Đó là điều kiện
    #    để nó không phá luật "server quyết thưởng" (xem js/progress.js, LS_MSTEPS).
    raw = json.dumps(box)
    chk(not any(k in raw for k in ("meteors", "xp", "badges", "awarded")),
        "cache KHONG chua so thuong nao", raw[:120])
    # Nút trên thẻ nhiệm vụ phải nói "Tiếp tục" — chữ và hành vi phải khớp nhau.
    lbl = pg.locator("#missions .play-btn").first.inner_text()
    chk("iếp tục" in lbl or "Resume" in lbl, "nut o Sanh noi 'Tiep tuc'", repr(lbl))
    ctx.close()

    # ── [9] Bản EN: lời nhắc cũng phải dịch ───────────────────────────────────
    head("[9] Ban EN")
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    seed(pg, STEPS[:2], lang="en")
    boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[2], "mo dung buoc con do", st["step"])
    chk("step 3/%d" % len(STEPS) in st["toast"],
        "loi nhac bang tieng Anh", repr(st["toast"]))
    ctx.close()

    # ── [10] Điện thoại dọc: chơi tiếp cũng phải mở được ─────────────────────
    head("[10] Dien thoai 390x844")
    ctx = br.new_context(viewport={"width": 390, "height": 844},
                         is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    seed(pg, STEPS[:4])
    errs = boot(pg)
    st = state(pg)
    chk(st["step"] == STEPS[4], "mo dung buoc con do", st["step"])
    chk(not errs, "0 loi trang", str(errs[:2]))
    ctx.close()

    br.close()


with sync_playwright() as pw:
    run(pw)

print(f"\n=== KET QUA: {ok} dat / {fail} hong ===")
if FAILS:
    for f in FAILS:
        print("  - " + f)
sys.exit(1 if fail else 0)
