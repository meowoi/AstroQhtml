# -*- coding: utf-8 -*-
r"""Do: cau do thach vang co DOI CAU va co DAO THU TU DAP AN.

Chu du an choi that roi bao: *"quiz cua thien thach vang dang khong dao cau khac
nhau va ko dao thu tu dap an"*. Hai loi rieng biet nen do rieng.

⚠ CACH DO PHAI KHONG CHAP CHON — bai hoc `play_maze` (21/08): mot hien tuong
  ~30% ma do bang 3 mau thi 34% lan chay se "sach" chi do may man.
  · DOI CAU: tui da xao la mot tinh chat TAT DINH — 8 cau dau phai la 8 cau KHAC
    NHAU, 8 cau sau cung vay. Khong phai phep thu xac suat.
  · DAO DAP AN: doc THU TU 4 CHUOI dap an cua CUNG mot cau qua 4 lan gap. Khong
    xao thi 4 lan giong het nhau tuyet doi; co xao thi xac suat 4 lan trung nhau
    la (1/24)^3 ≈ 0,007%. Do bang THU TU CHU chu khong doc `q.a` (bien private) —
    khong phai doan cai gi.
    ⚠ TU 22/08/2026 cau do lay tu KHO CHUNG nen 20 luot KHONG cau nao gap lai —
      cach do cu (doi mot cau xuat hien >=3 lan) thanh bat kha thi. Nay so THU TU
      TREN MAN HINH voi THU TU KHAI TRONG FILE (`__dbg.quiz.optsRaw`): khong xao
      thi hai ben giong nhau o MOI luot.
    ⚠ DA THU va DA BAC cach "chan het file cau tru MOT cai": be chua rong thi
      `nextQuiz()` roi sang DUONG LUI, nen 4 luot ra 4 cau KHAC NHAU — phep do
      khong buoc gap duoc mot cau.

⚠ Moi luot cau do deu di qua duong THAT: gieo thach vang -> ngam -> ban bang dan
  thuong -> `killFoe(..., byWave falsy)` -> `openQuiz`. Khong goi ham noi bo.
"""
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123"
VW = 600.0
ROUNDS = 24          # du dai de thay 'khong lap lai' tren mot kho lon
ok_n = bad_n = 0


def open_one_quiz(pg):
    """Gieo mot thach vang roi BAN THAT cho toi khi cau do mo ra.

    Tra ve {text, opts} cua cau dang hien, hoac None neu khong mo duoc.
    ⚠ Di qua dung duong cua tre: `killFoe(..., byWave falsy)` -> `openQuiz`.
      Goi thang ham noi bo thi phep do bo qua chinh doan can do.
    """
    for _ in range(3):
        st = pg.evaluate("() => window.__dbg.state")
        if st == "play":
            break
        if st in ("over", "dying"):
            pg.wait_for_timeout(900)
            if pg.locator("#again-btn").is_visible():
                pg.click("#again-btn")
                pg.wait_for_timeout(500)
        else:
            pg.wait_for_timeout(400)
    if pg.evaluate("() => window.__dbg.state") != "play":
        return None
    pg.evaluate("() => window.__dbg.spawn(1, 'gold')")
    pg.wait_for_timeout(60)
    opened = False
    for _ in range(60):
        g = pg.evaluate("() => window.__dbg.list.filter(f => f.key === 'gold')")
        if pg.evaluate("() => window.__dbg.state") == "quiz":
            opened = True
            break
        if not g:
            break
        sc = pg.evaluate("""(q) => {
            const cv = document.querySelector('canvas');
            const b  = cv.getBoundingClientRect();
            return {x: b.left + q.x / %f * b.width, y: b.top + q.y / %f * b.height};
        }""" % (VW, VW), {"x": g[0]["x"], "y": g[0]["y"]})
        pg.mouse.move(sc["x"], sc["y"])
        pg.mouse.down(); pg.wait_for_timeout(70); pg.mouse.up()
    if not opened:
        return None
    q = pg.evaluate("""() => ({
        text: document.getElementById('q-text').textContent.trim(),
        opts: [...document.getElementById('q-opts').children].map(b => b.textContent.trim()),
        /* Thu tu 4 dap an NHU KHAI TRONG FILE — de so voi thu tu tren man hinh.
           Cau cua DUONG LUI khong co (`optsRaw` chi co o cau tu kho chung). */
        raw:  (window.__dbg.quiz && window.__dbg.quiz.optsRaw) || null
    })""")
    pg.evaluate("() => { const b = document.getElementById('q-opts').children[0];"
                "        if (b && !b.disabled) b.click(); }")
    pg.wait_for_timeout(1500)
    return q


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""), flush=True)
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""), flush=True)


with sync_playwright() as p:
    br = p.chromium.launch()
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

    n_quiz = int(pg.evaluate("() => window.__dbg ? 1 : 0"))
    check(n_quiz == 1, "co be mat __dbg de gieo thach vang")

    seq = []            # thu tu cau hoi qua tung luot
    orders = {}         # cau hoi -> danh sach tuple thu tu dap an
    pairs = []          # (thu tu tren MAN HINH, thu tu KHAI TRONG FILE)
    for r in range(ROUNDS):
        q = open_one_quiz(pg)
        if q is None:
            continue
        seq.append(q["text"])
        orders.setdefault(q["text"], []).append(tuple(q["opts"]))
        if q.get("raw"):
            pairs.append((tuple(q["opts"]), tuple(q["raw"])))

    print("\n  do duoc %d luot cau do, %d cau hoi khac nhau" % (len(seq), len(orders)))
    check(len(seq) >= 16, "mo duoc it nhat 16 luot cau do", "%d luot" % len(seq))

    # --- (a) DOI CAU: tui da xao => moi 8 luot lien tiep la 8 cau KHAC NHAU
    bag = 8
    bad_bags = []
    for i in range(0, len(seq) - bag + 1, bag):
        blk = seq[i:i + bag]
        if len(set(blk)) != bag:
            bad_bags.append(i // bag + 1)
    check(len(seq) >= bag and not bad_bags,
          "moi 8 luot lien tiep la 8 cau KHAC NHAU (tui da xao)",
          "tui hong: %s" % bad_bags)
    rep = [i for i in range(1, len(seq)) if seq[i] == seq[i - 1]]
    check(not rep, "khong luot nao lap lai NGAY cau vua hoi",
          "lap o luot %s" % rep)
    # ⚠ Khong con doi "phu het bo cau hoi": bo cau nay la CA KHO, phu
    #   het trong 20 luot la bat kha thi. Dieu dang do la mot luot choi hoi duoc
    #   NHIEU cau khac nhau — va tot hon the: khong cau nao lap.
    check(len(orders) == len(seq) and len(orders) >= 16,
          "moi luot mot cau KHAC NHAU (khong cau nao lap trong ca luot choi)",
          "%d cau / %d luot" % (len(orders), len(seq)))

    check(not errs, "0 loi trang", "; ".join(errs[:1])[:80])
    ctx.close()

    # --- (b) DAO DAP AN -------------------------------------------------
    # ⚠ So thu tu tren MAN HINH voi thu tu KHAI TRONG FILE. Khong xao thi hai
    #   ben trung nhau o MOI luot — nen phep kiem tat dinh o CHIEU HONG.
    print("\n  --- (b) dao thu tu dap an ---")
    check(len(pairs) >= 12, "doc duoc thu tu goc cua >=12 cau",
          "%d cau tu kho chung" % len(pairs))
    same = [1 for shown, raw in pairs if shown == raw]
    check(bool(pairs) and len(same) < len(pairs),
          "thu tu dap an KHONG dung nguyen thu tu khai trong file",
          "%d/%d luot trung y nguyen" % (len(same), len(pairs)))
    # doi chung: bo dap an phai GIU NGUYEN (xao chu khong doi noi dung)
    check(bool(pairs) and all(set(shown) == set(raw) for shown, raw in pairs),
          "xao thu tu chu KHONG doi noi dung 4 dap an")
    br.close()

print("\n" + "=" * 56)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
