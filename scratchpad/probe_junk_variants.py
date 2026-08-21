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
    for _ in range(70):
        if len(seen) >= len(VAR):
            break
        if pg.evaluate("() => window.__dbg.state") != "play":
            pg.wait_for_timeout(900)
            if pg.locator("#again-btn").is_visible():
                pg.click("#again-btn"); pg.wait_for_timeout(400)
            continue
        pg.evaluate("() => window.__dbg.spawn(1, 'junk')")
        pg.wait_for_timeout(40)
        lst = pg.evaluate("() => window.__dbg.list")
        junk = [f for f in lst if f["key"] == "junk"]
        if not junk:
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
            continue
        px = pg.evaluate(READ, {"n": tgt["n"], "rad": RAD})
        if not px:
            continue
        body = near(px, [rgb(c) for c in VAR[jv]["cols"][:2]])
        if len(body) < 40:
            continue
        mean = tuple(round(sum(q[i] for q in body) / len(body)) for i in range(3))
        far = max((abs(q[3]) for q in body), default=0)
        fary = max((abs(q[4]) for q in body), default=0)
        # den bao nhap nhay: doc tam qua vai khung cach nhau
        lums = []
        for _ in range(7):
            l = pg.evaluate(CENTER, {"n": tgt["n"]})
            if l >= 0: lums.append(l)
            pg.wait_for_timeout(70)
        if len(lums) < 4:
            continue        # manh rac vo giua luc do -> bo, gieo lai
        seen[jv] = {"s": VAR[jv]["s"], "mean": mean, "n": len(body),
                    "far": max(far, fary), "lum": (min(lums), max(lums))}
        print("   do duoc %-6s mean=%s px=%d chia-ra=%.1f den=%s"
              % (VAR[jv]["s"], mean, len(body), max(far, fary), seen[jv]["lum"]))
        pg.screenshot(path=os.path.join(OUT, "junk-%s.png" % VAR[jv]["s"]))

    print()
    check(len(seen) == len(VAR), "gieo ra du MOI bien the",
          "do duoc %d/%d" % (len(seen), len(VAR)))

    # (1) Bon bien the phai KHAC NHAU tren man hinh
    keys = sorted(seen)
    worst = None
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = seen[keys[i]]["mean"], seen[keys[j]]["mean"]
            d = sum(abs(a[k] - b[k]) for k in range(3))
            if worst is None or d < worst[0]:
                worst = (d, seen[keys[i]]["s"], seen[keys[j]]["s"])
    check(worst is not None and worst[0] >= 60,
          "bon bien the cho ra bon MAU KHAC NHAU tren man hinh",
          "cap gan nhat: %s vs %s lech %d" % (worst[1], worst[2], worst[0])
          if worst else "khong do duoc")

    # (2) Moi bien the VAN co den bao nhap nhay -> van doc ra la rac
    dim = [v["s"] for v in seen.values() if v["lum"][1] - v["lum"][0] < 60]
    check(bool(seen) and not dim,
          "moi bien the VAN co den bao nhap nhay (tin hieu 'day la rac')",
          "khong nhay: %s" % dim)

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
