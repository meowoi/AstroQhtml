# -*- coding: utf-8 -*-
r"""Do HAI CHIEU: EMP quet thach vang thi KHONG mo cau do; dan thuong thi CO.

VI SAO CO BO NAY du `CLAUDE.md` da ghi dung hanh vi do, va `game-defender.html`
doc ra cung dung (`if(!byWave) openQuiz();`): **ghi chu lac hau da gay thiet hai
that nhieu lan trong du an** (mot vong phoi hop voi ChatGPT/Gemini tieu phi vi doc
mot luat da chet; `js/ranks.js` ghi "co phep kiem doi chieu" trong khi grep ra 0
ket qua). Chu du an hoi lai chinh dieu nay ngay 21/08/2026, nen no can mot phep DO.

CHIEU THU HAI MOI LA CHIEU KHO BO SOT:
  (1) EMP quet thach vang  -> state VAN "play", KHONG co cau do
  (2) dan thuong ban thach vang -> state thanh "quiz"
Thieu (2) thi mot ban "khong bao gio mo cau do" cung DAT — tuc phan thuong cau do
chet han ma phep kiem van xanh.

VA MOT CHIEU THU BA, de dat MOT CACH RONG neu bo qua: phai chung minh EMP THAT SU
da pha thach vang. Chi doc `state == "play"` thi mot con song khong cham duoc hon
nao cung cho ket qua y het. Nen bo do ghi SO HIEU tung hon vang truoc khi no roi
doi chung bien het sau khi song lan xong.
"""
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123"
VW = 600.0
ok_n = bad_n = 0


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""), flush=True)
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""), flush=True)


def boot(br):
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','300');")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/game-defender.html", wait_until="load", timeout=30000)
    pg.wait_for_timeout(900)
    if pg.locator(".ov.rot.show").count():
        pg.locator(".ov.rot.show .rot-ok").click()
    pg.click("#start-btn")
    pg.wait_for_timeout(400)
    return ctx, pg, errs


def golds(pg):
    return pg.evaluate("() => window.__dbg.list.filter(f => f.key === 'gold')")


def to_screen(pg, x, y):
    return pg.evaluate("""(p) => {
        const cv = document.querySelector('canvas');
        const b  = cv.getBoundingClientRect();
        return {x: b.left + p.x / %f * b.width, y: b.top + p.y / %f * b.height};
    }""" % (VW, VW), {"x": x, "y": y})


with sync_playwright() as p:
    br = p.chromium.launch()

    print("=== (1) EMP quet thach vang: KHONG duoc mo cau do ===")
    ctx, pg, errs = boot(br)
    st0 = pg.evaluate("() => window.__dbg.state")
    check(st0 == "play", "vao duoc man choi", st0)

    # Gieo DUNG hai hon vang — mot cu EMP quet ca hai la ca xau nhat (stack cau do).
    pg.evaluate("() => window.__dbg.spawn(2, 'gold')")
    pg.wait_for_timeout(60)
    g0 = golds(pg)
    check(len(g0) >= 2, "gieo duoc >=2 thach vang", "%d hon" % len(g0))
    ser0 = sorted(f["n"] for f in g0)

    pg.evaluate("() => window.__dbg.chargeEmp()")
    pg.keyboard.press("e")
    pg.wait_for_timeout(120)          # doc NGAY: song moi lan mot phan
    check(pg.evaluate("() => window.__dbg.wave") >= 0,
          "song EMP that su dang lan", "r=%s" % pg.evaluate("() => window.__dbg.wave"))
    st1 = pg.evaluate("() => window.__dbg.state")
    check(st1 == "play", "giua luc song lan: state VAN 'play'", st1)

    pg.wait_for_timeout(700)          # empMax 470 / empSpeed 900 => ~0,49s
    st2 = pg.evaluate("() => window.__dbg.state")
    check(st2 == "play", "song lan xong: van 'play' (khong mo cau do tre)", st2)
    left = pg.evaluate("(ns) => window.__dbg.serials.filter(n => ns.includes(n))", ser0)
    check(not left, "EMP DA pha ca hai hon vang (so hieu bien het)",
          "con lai %s" % left)
    check(not pg.evaluate("() => !!document.querySelector('#ov-quiz.show')"),
          "khong lop phu cau do nao mo ra")
    check(not errs, "0 loi trang", "; ".join(errs[:1])[:80])
    ctx.close()

    print("\n=== (2) Dan THUONG ban thach vang: PHAI mo cau do ===")
    ctx, pg, errs = boot(br)
    pg.evaluate("() => window.__dbg.spawn(1, 'gold')")
    pg.wait_for_timeout(60)
    check(len(golds(pg)) >= 1, "gieo duoc thach vang")

    got = False
    for _ in range(120):
        g = golds(pg)
        if not g:
            break
        sc = to_screen(pg, g[0]["x"], g[0]["y"])
        pg.mouse.move(sc["x"], sc["y"])   # aim bam theo con tro moi khung hinh
        pg.mouse.down()
        pg.wait_for_timeout(70)
        pg.mouse.up()
        if pg.evaluate("() => window.__dbg.state") == "quiz":
            got = True
            break
    st3 = pg.evaluate("() => window.__dbg.state")
    check(got, "ban thach vang bang dan thuong -> state thanh 'quiz'", st3)
    check(pg.evaluate("() => !!document.querySelector('#ov-quiz.show')")
          if pg.locator("#ov-quiz").count() else got,
          "lop phu cau do hien ra that")
    check(not errs, "0 loi trang", "; ".join(errs[:1])[:80])
    ctx.close()
    br.close()

print("\n" + "=" * 54)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
