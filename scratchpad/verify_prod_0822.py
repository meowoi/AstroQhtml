# -*- coding: utf-8 -*-
r"""Đo trên BẢN THẬT sau khi push ngày 22/08/2026.

⚠️ KIỂM SỐ HIỆU BẢN DỰNG TRƯỚC MỌI THỨ KHÁC, và DỪNG HẲN nếu chưa khớp.
   GitHub Pages build ~1–2 phút, và ngày 06/08/2026 bản thật từng đứng ở bản cũ
   gần một ngày do deploy hết giờ hai lần liên tiếp. Đo trước lúc build xong thì
   mọi kết luận sau đó đều sai — đó chính là lý do huy hiệu `.ver-badge` tồn tại.

Bốn thứ đo, theo đúng thứ tự đáng tin cậy:
  [1] số hiệu bản dựng  → chắc đang đo bản mới
  [2] 5 file art mới trả 200 + MIME ảnh đúng — thiếu một file thì trò chơi VẪN
      chạy (nó lùi về bản vẽ vector) nên đây là lỗi IM LẶNG, phải ĐO
  [3] mở CHÍNH `game-racer.html` trên bản thật → art decode được, 3 đối thủ có
      tên, tên tàu của trẻ hiện ra, nút tăng tốc có thật, 0 lỗi trang
  [4] ba trang còn lại của đợt: 6 móc treo · nút "Chơi lại" hiện ảnh tt ·
      lời nhắc rút gọn tên ở Kho Trang Trí
"""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
SITE = "https://astroq.org"
WANT = "2026.08.22.1"

ok_n = bad_n = 0


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""), flush=True)
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""), flush=True)


def get(url):
    rq = urllib.request.Request(url, headers={"User-Agent": "astroq-verify"})
    with urllib.request.urlopen(rq, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")


print("=== [1] So hieu ban dung (kiem TRUOC moi thu khac) ===")
st, _, ui = get(SITE + "/js/ui-common.js?cb=1")
m = re.search(r'var VERSION = "([^"]+)"', ui)
got = m.group(1) if m else "?"
check(st == 200, "js/ui-common.js tra 200", str(st))
check(got == WANT, "ban dung tren Pages dung la ban vua push", "%s (doi %s)" % (got, WANT))
if got != WANT:
    print("\n⚠️ Pages CHUA build xong (hoac deploy hong). DUNG — moi ket luan sau day")
    print("   se noi ve BAN CU. Doi mot phut roi chay lai script nay.")
    sys.exit(1)

print("\n=== [2] 5 file art moi: 200 + MIME anh ===")
# ⚠️ Thieu mot file thi `loadArt()` de `ok=false` va game LUI VE ban ve vector —
#    khong loi, khong canh bao. Do la ly do phai do tung file chu khong doan.
import urllib.error
for f in ["rival-blaze", "rival-ember", "rival-dust", "rock", "fuel-can"]:
    u = SITE + "/img/racer/%s.png" % f
    try:
        rq = urllib.request.Request(u, headers={"User-Agent": "astroq-verify"})
        with urllib.request.urlopen(rq, timeout=30) as r:
            st, ct, n = r.status, r.headers.get("Content-Type", ""), len(r.read())
    except urllib.error.HTTPError as e:
        st, ct, n = e.code, "", 0
    check(st == 200 and n > 0, "img/racer/%s.png tra 200" % f, "%s, %d byte" % (st, n))
    check("image/png" in ct.lower(), "  MIME la image/png", ct)

print("\n=== [3] Mo CHINH game-racer.html tren ban that ===")
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN")
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-sfx','off');"
                        "localStorage.setItem('astroq-asteroids','240');")
    pg = ctx.new_page()
    errs, bad = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
    pg.on("console", lambda m: errs.append(m.text[:120]) if m.type == "error" else None)
    pg.on("response", lambda r: bad.append("%s %s" % (r.status, r.url.split("/")[-1]))
          if r.status >= 400 else None)
    pg.goto(SITE + "/game-racer.html", wait_until="load")
    pg.wait_for_timeout(1200)

    check(pg.eval_on_selector(".ver-badge", "e => e.textContent") == "v" + WANT,
          "huy hieu ban dung tren chinh trang game", WANT)
    # ⚠️ Do `ok` cua tung anh — `ok` chi bat khi anh DECODE xong, nen day la phep
    #    do duy nhat phan biet "anh tra 200" voi "game that su ve bang art".
    art = pg.evaluate("() => { var A = window.__racer && window.__racer.art; return null; }")
    # ⚠️ PHAI VAO LUOT CHOI TRUOC KHI DEM DOI THU. `rivals` chi duoc dung o
    #    `startRound()`, nen o man brief no dung la RONG — do o day roi bao
    #    "0 doi thu" la mot phep do sai, khong phai mot loi san pham.
    # ⚠️ Va id nut la `btn-boost`, khong phai `boost-btn` — lan dau toi doan ten
    #    roi bao hong oan. Doc id tu trang, dung doan.
    pre = pg.evaluate("() => window.__racer ? window.__racer.rivals.length : -1")
    check(pre == 0, "man brief: chua co doi thu nao (dung nhu thiet ke)", str(pre))
    pg.click("#start-btn")
    pg.wait_for_timeout(900)
    ready = pg.evaluate("""() => {
      var b = document.getElementById('btn-boost');
      return { canvas: document.querySelectorAll('canvas').length,
               label: window.__racer ? window.__racer.shipLabel : null,
               rivals: window.__racer ? window.__racer.rivals.length : -1,
               names: window.__racer ? window.__racer.rivals.map(r => r.id) : [],
               boost: !!b, boostShown: !!b && !b.classList.contains('is-hidden'),
               state: window.__racer ? window.__racer.state : null };
    }""")
    check(ready["canvas"] >= 1, "co canvas san dua", str(ready["canvas"]))
    check(ready["label"] == "Luna", "ten tau mac dinh hien 'Luna'", repr(ready["label"]))
    check(ready["rivals"] == 3, "dung 3 doi thu khi vao luot", str(ready["names"]))
    check(ready["boost"] and ready["boostShown"],
          "nut tang toc hien ra that khi dang choi", str(ready["boostShown"]))

    # Art co decode duoc khong: do bang chinh the <img> ma `loadArt` dung
    px = pg.evaluate("""async () => {
      const src = ['rival-blaze','rival-ember','rival-dust','rock','fuel-can'];
      const out = [];
      for (const s of src) {
        const im = new Image();
        im.src = 'img/racer/' + s + '.png';
        try { await im.decode(); out.push([s, im.naturalWidth, im.naturalHeight]); }
        catch (e) { out.push([s, 0, 0]); }
      }
      return out;
    }""")
    for s, w, h in px:
        check(w > 0 and h > 0, "%s decode duoc" % s, "%dx%d" % (w, h))

    check(not errs, "0 loi trang", str(errs[:2]))
    check(not bad, "0 asset hong", str(bad[:3]))

    print("\n=== [4] Ba trang con lai cua dot ===")
    # 6 moc treo o ban do vach khoang lai
    pg.goto(SITE + "/specimen-vault.html", wait_until="load")
    pg.wait_for_timeout(700)
    hooks = pg.evaluate("() => window.AstroQSpecimens.hooks().length")
    check(hooks == 6, "Kho Mau Vat: client khai dung 6 moc", str(hooks))

    # Nut "Choi lai" hien ANH tt, khong con chu "tt" tran
    pg.goto(SITE + "/game-catch.html", wait_until="load")
    pg.wait_for_timeout(700)
    again = pg.evaluate("""() => {
      // ⚠️ id la `again-btn`. Fallback `.acts .primary` la SAI: man brief cung co
      //    mot nut `.primary` ("Bat dau"), nen no bat nham va bao hong oan.
      const b = document.getElementById('again-btn');
      return b ? { html: b.innerHTML, img: b.querySelectorAll('img').length } : null;
    }""")
    check(again and again["img"] >= 1, "game-catch: nut Choi lai co ANH tt",
          str(again and again["img"]))
    check(again and ">tt<" not in again["html"], "  khong con chu 'tt' tran")

    # Loi nhac rut gon ten o Kho Trang Tri
    pg.goto(SITE + "/shop.html", wait_until="load")
    pg.wait_for_timeout(700)
    hint = pg.evaluate("""() => {
      const e = document.querySelector('[data-i18n="ship_hint"]');
      return e ? e.textContent : null;
    }""")
    check(hint and "sân" in hint and "rút gọn" in hint,
          "shop.html: noi ra rang ten dai bi rut gon tren san", repr(hint))

    ctx.close()
    br.close()

print("\n" + "=" * 52)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
