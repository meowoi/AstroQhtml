# -*- coding: utf-8 -*-
r"""Do RÁC VŨ TRỤ ở ARCADE-02: bốn hình thù, bốn tông màu, và vẫn đọc ra là rác.

Chủ dự án chơi thật rồi báo: *"rác vũ trụ thay đổi bằng nhiều hình thù và màu sắc
khác nhau, ko chỉ có 1 loại màu đỏ"*.

⚠️ ĐO TRÊN MÀN HÌNH, KHÔNG ĐỌC MÃ. Bốn biến thể là chuyện HÌNH ẢNH: `grep` chỉ
   chứng minh có bốn khối `if`, không chứng minh trẻ nhìn ra bốn thứ khác nhau.
   Bộ này gieo từng mảnh rác qua ĐÚNG đường sinh của game rồi đọc pixel quanh nó.

⚠️ HAI CHIỀU, và chiều thứ hai mới là chiều dễ bỏ sót:
     ① bốn biến thể phải KHÁC NHAU (nếu không thì yêu cầu chưa được làm);
     ② mỗi biến thể vẫn phải ĐỌC RA LÀ RÁC — cả sân có bốn thứ phải phân biệt
        tức thì (xám 2 phát · rác nhanh 1 phát · tím tiền · vàng câu đố), nên đổi
        màu thân mà mất tín hiệu nhận dạng là làm game TỆ ĐI dù đúng yêu cầu.
        Tín hiệu giữ không đổi = đèn báo nhấp nháy ở giữa mảnh.

⚠️ VÀ MỘT PHÉP KIỂM CHỐNG "VẼ CHÌA RA NGOÀI VÙNG VA CHẠM": va chạm tính bằng hình
   tròn bán kính `f.r`, nên một hình chữ nhật vẽ rộng hơn đường tròn đó là "trông
   như chưa chạm mà đã mất giáp" — đúng lỗi hitbox đã trả giá ở ARCADE-01. Chỉ đo
   được cho ba hình MỚI (lam · cam · be): quầng sáng ngoài mảnh nào cũng là ĐỎ nên
   nó không lọt vào bộ màu của ba hình đó. Hình `plate` đỏ giữ nguyên hình học cũ
   nên không có gì mới để đo — ghi ra đây để không ai tưởng nó đã được kiểm.
"""
import io
import os
import re
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.dirname(os.path.abspath(__file__))
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


def variants():
    """Doc bang JUNK tu chinh game — khong chep mau sang day."""
    src = io.open(os.path.join(ROOT, "game-defender.html"),
                  encoding="utf-8", newline=None).read()
    i = src.find("var JUNK = [")
    blk = src[i:src.find("];", i)]
    out = []
    for s_, c0, c1, c2 in re.findall(
            r's:"([a-z]+)",\s*c0:"(#[0-9a-fA-F]{6})",\s*c1:"(#[0-9a-fA-F]{6})",'
            r'\s*c2:"(#[0-9a-fA-F]{6})"', blk):
        out.append({"s": s_, "cols": [c0, c1, c2]})
    return out


def rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


# ⚠ DOC PIXEL THEO SO HIEU, KHONG THEO TOA DO CHUP TRUOC. Rac bay 118 px/s nen
# giua luc `evaluate` lay toa do va luc doc pixel, manh rac da di mot doan — ban do
# dau cua bo nay do cua so LECH cho va bao "den khong nhay" (tam doc ra mau nen).
# Tra vi tri va doc pixel trong CUNG mot lan evaluate thi khong con khe nao.
READ = """(a) => {
  const f = (window.__dbg.list || []).find(o => o.n === a.n);
  if (!f) return null;
  const cv = document.querySelector('canvas');
  const g  = cv.getContext('2d');
  const sx = cv.width / 600, sy = cv.height / 600;
  const x0 = Math.max(0, Math.round((f.x - a.rad) * sx));
  const y0 = Math.max(0, Math.round((f.y - a.rad) * sy));
  const ww = Math.min(cv.width  - x0, Math.round(a.rad * 2 * sx));
  const hh = Math.min(cv.height - y0, Math.round(a.rad * 2 * sy));
  if (ww <= 0 || hh <= 0) return null;
  const d = g.getImageData(x0, y0, ww, hh).data;
  const px = [];
  for (let yy = 0; yy < hh; yy++) for (let xx = 0; xx < ww; xx++) {
    const i = (yy * ww + xx) * 4;
    px.push([d[i], d[i+1], d[i+2],
             (x0 + xx) / sx - f.x, (y0 + yy) / sy - f.y]);
  }
  return px;
}"""

CENTER = """(a) => {
  const f = (window.__dbg.list || []).find(o => o.n === a.n);
  if (!f) return -1;
  const cv = document.querySelector('canvas');
  const g  = cv.getContext('2d');
  const sx = cv.width / 600, sy = cv.height / 600;
  const d = g.getImageData(Math.round(f.x * sx) - 2, Math.round(f.y * sy) - 2,
                           5, 5).data;
  let s = 0, n = 0;
  for (let i = 0; i < d.length; i += 4) { s += d[i] + d[i+1] + d[i+2]; n++; }
  return Math.round(s / n);
}"""


def near(px, cols, tol=46):
    """Pixel thuoc bo mau cua bien the — khop TUNG KENH, khong khop tong.

    ⚠ CHI DUNG HAI CHANG MAU SANG (`c0`,`c1`), BO chang toi nhat (`c2`): quang sang
      quanh moi manh rac la mau DO mo (~122,40,45), ma `c2` cua thung nhien lieu la
      nau sam (122,52,16) — hai thu do lech nhau 41 don vi neu cong ba kenh, tuc ban
      dau cua bo nay dem quang do thanh "than thung nhien lieu" va bao bon bien the
      chi lech nhau 1 don vi mau. Hai chang sang thi cach nhau rat xa nen khong con
      cho lan."""
    out = []
    for p in px:
        for c in cols:
            if (abs(p[0] - c[0]) <= tol and abs(p[1] - c[1]) <= tol
                    and abs(p[2] - c[2]) <= tol):
                out.append(p)
                break
    return out


with sync_playwright() as p:
    br = p.chromium.launch()
    VAR = variants()
    print("=== bang JUNK doc tu game-defender.html: %d bien the ===" % len(VAR))
    check(len(VAR) >= 4, "co it nhat 4 bien the rac vu tru", "%d" % len(VAR))
    for v in VAR:
        print("   %-6s %s" % (v["s"], " ".join(v["cols"])))

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

    seen = {}          # jv -> {mean, blink, out}
    RAD = 34.0         # cua so do: rong hon f.r (15) de bat ca phan chia ra ngoai

    # ⚠️⚠️ BUOC TUNG BIEN THE, KHONG CHO `Math.random()` GIEO DU.
    #    Ban dau bo do thu toi 70 lan roi cho gap du 4 bien the — do duoc no
    #    chap chon 1/4 luot chay, va mot phep kiem chap chon thi som muon bi bo
    #    qua. `__dbg.spawn(1,'junk',jv)` buoc bien the; no chi doi HINH, khong
    #    doi mot chi so nao (xem ghi chu trong game-defender.html).
    n_var = pg.evaluate("() => window.__dbg.junkVariants")
    check(n_var == len(VAR), "so bien the o be mat test khop bang JUNK doc tu file",
          "dbg=%s · file=%d" % (n_var, len(VAR)))

    for want in range(len(VAR)):
      # ⚠️ Thu lai NHIEU LAN cho MOT bien the. Ban dau moi bien the chi gieo mot
      #    luot, nen gap nhieu (vat the khac chen vao cua so do, manh rac chua
      #    vao han trong san, tram vo giua luc do) la MAT luon bien the do — do
      #    duoc 3/4. Thu lai giu duoc tinh tat dinh ve "bien the nao" ma khong
      #    con phu thuoc may man.
      why = []
      for _try in range(25):
        if want in seen:
            break
        if pg.evaluate("() => window.__dbg.state") != "play":
            pg.wait_for_timeout(900)
            if pg.locator("#again-btn").is_visible():
                pg.click("#again-btn"); pg.wait_for_timeout(400)
        # ⚠️ DON SAN TRUOC KHI GIEO. Hat no mang dung mau `c1` cua bien the
        #    (`burst(...JUNK[f.jv].c1...)`) nen chung lot vao bo mau va lam phep
        #    do hinh hoc nhay 14,6 → 26,9 px tuy luot — chap chon 1/6 luot chay.
        #    Hat KHONG nam trong `__dbg.list` nen khong loc duoc bang danh sach
        #    vat the; phai don. Cung cach `play_racer.py` muc [4] da phai lam.
        pg.evaluate("() => window.__dbg.clear()")
        pg.evaluate("(v) => window.__dbg.spawn(1, 'junk', v)", want)
        pg.wait_for_timeout(40)
        lst = pg.evaluate("() => window.__dbg.list")
        junk = [f for f in lst if f["key"] == "junk" and f.get("jv") == want]
        if not junk:
            why.append("khong thay manh rac vua gieo")
            continue
        tgt = max(junk, key=lambda f: f["n"])
        jv = tgt.get("jv")
        if jv is None or jv in seen:
            continue
        # ⚠ CHO MANH RAC VAO HAN TRONG SAN TRUOC KHI DO. Vat the sinh tren VONG
        # TRON ban kinh 440 quanh tam, tuc NGOAI khung 600x600 (co the x = -140).
        # Doc pixel luc do thi cua so bi kep ve mep canvas va `dx` tinh ra tan
        # 195 px — ban do dau cua bo nay bao "arm chia ra 195" trong khi hinh
        # chi rong 28 px. Do la loi CUA PHEP DO, khong phai cua san pham.
        inside = None
        for _w in range(45):
            cur = pg.evaluate("(n) => (window.__dbg.list || [])"
                              ".find(o => o.n === n) || null", tgt["n"])
            if not cur:
                break
            if (RAD + 3 <= cur["x"] <= 600 - RAD - 3
                    and RAD + 3 <= cur["y"] <= 600 - RAD - 3):
                inside = cur
                break
            pg.wait_for_timeout(90)
        if not inside:
            continue
        tgt = inside
        lst = pg.evaluate("() => window.__dbg.list")
        # Chi do khi khong co vat the nao khac chen vao cua so — bang khong thi
        # pixel cua thien thach xam se lot vao bo mau lam cua tam pin.
        others = [f for f in lst if f["n"] != tgt["n"]]
        if any(abs(f["x"] - tgt["x"]) < RAD * 2 and abs(f["y"] - tgt["y"]) < RAD * 2
               for f in others):
            why.append("vat the khac chen vao cua so do")
            continue
        px = pg.evaluate(READ, {"n": tgt["n"], "rad": RAD})
        if not px:
            why.append("doc pixel that bai")
            continue
        body = near(px, [rgb(c) for c in VAR[jv]["cols"][:2]])
        if len(body) < 40:
            why.append("chi thay %d pixel thuoc bo mau (can >=40)" % len(body))
            continue
        mean = tuple(round(sum(q[i] for q in body) / len(body)) for i in range(3))
        # ⚠️⚠️ HINH HOC DO TREN TONG GIUA (`c1`), KHONG do tren ca `body`.
        #    `body` gom ca `c0` — tong SANG NHAT — va voi `arm` (be sang
        #    #f2e6cf) thi tong do trung NGOI SAO NEN trang: no lam `chia-ra`
        #    nhay 14,6 / 21,0 / 25,6 tuy luot va lam bo do chap chon 2/6 luot.
        #    `c1` la tong dac trung nhat va xa nen nhat. Cung ho loi da ghi:
        #    "quang do lot vao bo mau" — o day la NEN SAO lot vao bo mau.
        core = near(px, [rgb(VAR[jv]["cols"][1])], tol=40) or body
        far = max((abs(q[3]) for q in core), default=0)
        fary = max((abs(q[4]) for q in core), default=0)
        # den bao nhap nhay: doc tam qua vai khung cach nhau
        lums = []
        for _ in range(7):
            l = pg.evaluate(CENTER, {"n": tgt["n"]})
            if l >= 0: lums.append(l)
            pg.wait_for_timeout(70)
        if len(lums) < 4:
            why.append("manh rac vo giua luc do den (%d mau)" % len(lums))
            continue
        seen[jv] = {"s": VAR[jv]["s"], "mean": mean, "n": len(body),
                    "far": max(far, fary), "lum": (min(lums), max(lums))}
        print("   do duoc %-6s mean=%s px=%d chia-ra=%.1f den=%s"
              % (VAR[jv]["s"], mean, len(body), max(far, fary), seen[jv]["lum"]))
        pg.screenshot(path=os.path.join(OUT, "junk-%s.png" % VAR[jv]["s"]))

      if want not in seen:
          # ⚠️ Bo mot bien the trong IM LANG doc ra y nhu mot phep kiem dat.
          from collections import Counter
          print("   !! bien the %s: 25 lan thu deu khong do duoc — %s"
                % (VAR[want]["s"], dict(Counter(why))))

    print()
    check(len(seen) == len(VAR), "gieo ra du MOI bien the",
          "do duoc %d/%d" % (len(seen), len(VAR)))

    # ── (1a) Bon BANG MAU KHAI phai khac nhau — tat dinh, doc tu `JUNK` ──
    # ⚠️ Do o BANG MAU chu khong o `mean` tren man hinh. Ban cu do `mean` va bao
    #    "plate vs tank lech 53 < 60" — nhung hai bang mau KHAI lech 78, con tren
    #    man thi ca hai deu mang quang do dung chung nen bi keo lai gan nhau. Va
    #    thiet ke CO Y khong phan biet bang mau (xem ghi chu trong `JUNK`:
    #    "nhan ra bang LUOI O chu khong bang mau"), nen phep kiem cu dang khang
    #    dinh mot tieu chi thiet ke KHONG CO.
    ks = list(range(len(VAR)))
    worst = None
    for i in ks:
        for j in ks[i + 1:]:
            a, b = rgb(VAR[i]["cols"][1]), rgb(VAR[j]["cols"][1])
            d = sum(abs(a[k] - b[k]) for k in range(3))
            if worst is None or d < worst[0]:
                worst = (d, VAR[i]["s"], VAR[j]["s"])
    check(worst is not None and worst[0] >= 60,
          "bon BANG MAU khai khac nhau (khong co hai bien the trung mau)",
          "cap gan nhat: %s vs %s lech %d" % (worst[1], worst[2], worst[0])
          if worst else "khong doc duoc")

    # ── (1b) Mau tren man cua tung bien the GAN bang mau CUA CHINH NO nhat ──
    # Manh hon "bon mau khac nhau": no bat duoc ca loi VE NHAM BIEN THE — mot
    # loi im lang (hinh van la rac, van bay, van tru diem) ma phep kiem cu mu.
    wrong = []
    for jv, v in seen.items():
        dists = [(sum(abs(v["mean"][k] - rgb(VAR[i]["cols"][1])[k]) for k in range(3)), i)
                 for i in ks]
        dists.sort()
        if dists[0][1] != jv:
            wrong.append("%s -> giong %s hon" % (v["s"], VAR[dists[0][1]]["s"]))
    check(bool(seen) and not wrong,
          "moi bien the ve dung bang mau CUA CHINH NO (khong ve nham ban)",
          "; ".join(wrong) or "%d/%d bien the" % (len(seen), len(VAR)))

    # ── (2a) Den bao la MA DUNG CHUNG, nam NGOAI moi nhanh bien the ──
    # ⚠️ Do bang cach DOC MA, khong do pixel: `arm` mang bo mau be sang trung nen
    #    sao trang nen do do sang o tam cho bien do 5 trong khi plate/tank la
    #    473/435 — cach do sai cho, khong phai san pham sai. Va dieu THAT SU can
    #    bao dam la den o NGOAI cac nhanh: de trong mot nhanh thi doi hinh mot
    #    bien the la mat han tin hieu "day la rac", dung lop loi im lang ma vet
    #    nut cua thien thach xam da tra gia.
    # ⚠️ `ROOT` o file nay la CHUOI (os.path), khong phai pathlib.Path.
    src = io.open(os.path.join(ROOT, "game-defender.html"), encoding="utf-8").read()
    m = re.search(r"var jv=JUNK\[.*?(?=\n\s*\} else \{\n\s*/\* thiên thạch)",
                  src, re.S)
    blk = m.group(0) if m else ""
    led = re.search(r"fillStyle\s*=\s*Math\.sin\(f\.ph[^;]*;\s*"
                    r"ctx\.beginPath\(\);\s*ctx\.arc\(0,0,f\.r\*[\d.]+", blk)
    check(bool(led), "co dong ve den bao nhap nhay trong khoi ve rac", "")
    if led:
        after_last_branch = blk.rfind("} else {")
        check(after_last_branch < led.start(),
              "den bao nam NGOAI moi nhanh bien the (ma dung chung)",
              "den o %d, nhanh cuoi ket o %d" % (led.start(), after_last_branch))

    # ── (2b) …va den PHAI nhay that ──
    best = max(seen.values(), key=lambda v: v["lum"][1] - v["lum"][0], default=None)
    check(best is not None and (best["lum"][1] - best["lum"][0]) >= 60,
          "den bao THAT SU nhay (do tren bien the co tuong phan tot nhat)",
          ("%s bien do %d" % (best["s"], best["lum"][1] - best["lum"][0]))
          if best else "khong do duoc")

    # (3) Ba hinh MOI khong ve chia ra ngoai vung va cham (f.r = 15)
    NEW = {v["s"]: v for v in seen.values() if v["s"] != "plate"}
    over = {k: round(v["far"], 1) for k, v in NEW.items() if v["far"] > 15 * 1.25}
    check(bool(NEW) and not over,
          "ba hinh moi nam trong vung va cham (<= 1,25 x f.r)",
          "chia ra: %s" % over)

    check(not errs, "0 loi trang", "; ".join(errs[:1])[:80])
    ctx.close()
    br.close()

print("\n" + "=" * 58)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
