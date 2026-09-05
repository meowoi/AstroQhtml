# -*- coding: utf-8 -*-
"""
smoke_vendor.py — CHỨNG MINH TRÊN CHROMIUM THẬT rằng app không còn gọi ra
unpkg.com / gstatic.com, và vẫn chạy đúng sau khi tự host.

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/smoke_vendor.py

VÌ SAO PHẢI ĐO TRÊN TRÌNH DUYỆT
-------------------------------
`grep` chỉ chứng minh **chuỗi văn bản** biến mất khỏi mã nguồn. Nó KHÔNG chứng
minh được điều ta thật sự cần: rằng trình duyệt **không phát ra request nào**
tới hai tên miền đó. Ba đường lọt mà grep mù hoàn toàn:
  · file vendor tự nó import ra ngoài (đúng cái bẫy `firebase-auth.js` đã có)
  · importmap sai đường dẫn → 404 → cảnh không dựng được, mà trang vẫn "trắng
    tinh không lỗi" nếu ai đó nuốt exception
  · một addon kéo theo file thứ 13 chưa được tải về

Nên phép kiểm mạnh nhất ở đây là **CHẶN THẲNG hai tên miền** (`route.abort()`)
rồi đòi app vẫn chạy đủ. Đó là phép thử phá hoại có sẵn trong thiết kế: nếu còn
sót một lời gọi ra ngoài, nó hỏng ngay chứ không lặng lẽ đi qua.

⚠️ Trên Windows phải đặt PYTHONIOENCODING=utf-8, không thì `print` chữ Việt là
   UnicodeEncodeError ngay dòng tiêu đề (bài học đã ghi ở CLAUDE.md mục 6).
"""

import re
import sys

BASE = "http://127.0.0.1:8123"
BLOCK = ("unpkg.com", "gstatic.com", "cdn.jsdelivr.net", "fonts.googleapis.com")

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


def watch(page, out):
    """Ghi lại MỌI request ra ngoài và MỌI lỗi trang."""
    page.on("request", lambda r: out["req"].append(r.url))
    page.on("pageerror", lambda e: out["err"].append(str(e)))
    # `console.on("error")` KHÔNG bắt được ngoại lệ chưa bắt — chúng đi qua
    # `pageerror`. Bài học đã trả giá ngày 02/08/2026 với form waitlist.
    page.on("console", lambda m: out["err"].append("console: " + m.text)
            if m.type == "error" else None)


def outside(reqs):
    return [u for u in reqs if any(d in u for d in BLOCK)]


def run(pw, blocked):
    """blocked=True: chặn thẳng 4 tên miền ngoài rồi đòi app vẫn chạy đủ."""
    tag = "CHAN TEN MIEN NGOAI" if blocked else "mang binh thuong"
    print("\n" + "=" * 66)
    print("  [%s]" % tag)
    print("=" * 66)

    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    if blocked:
        for d in BLOCK:
            ctx.route("**://*%s/**" % d, lambda r: r.abort())

    # KHONG PHAI LOI SAN PHAM: bo do chay o cong 8123, ma cong do CO Y khong
    # nam trong ALLOWED_ORIGINS cua backend (day la cau hinh SAN XUAT — mo them
    # mot origin that chi de lam xanh mot phep kiem la doi thu khong thuoc san
    # xuat). Nen preflight bi CORS chan va TRINH DUYET TU ghi mot dong do
    # `net::ERR_FAILED` — khong `catch` nao chan duoc.
    # `login()` hoi `/auth/status` khi Firebase tu choi bang `invalid-credential`
    # (them 29/08/2026), tuc dung duong ma probe nay di qua. Tra mot phan hoi
    # co dinh thay vi chan: no vua sach console vua di qua dung nhanh code that.
    # Cung cach da lam cho `/billing/catalog` (11/08) va `/crew` (16/08).
    # Neo cuoi chuoi, KHONG dung glob `**/auth/status*` — bai hoc `**/crew*`
    # khop ca `/crew.html` (16/08). Dang ky SAU khoi chan o tren: Playwright
    # khop nguoc, luat hep phai dung sau luat rong (bai hoc 29/08/2026).
    ctx.route(re.compile(r".*/auth/status(\?.*)?$"), lambda r: r.fulfill(
        status=200, content_type="application/json", body='{"state":"none"}'))

    # ---------- explorer.html: cảnh 3D three.js ----------
    print("\n[1] explorer.html — canh 3D three.js")
    out = {"req": [], "err": []}
    pg = ctx.new_page()
    watch(pg, out)
    pg.goto(BASE + "/explorer.html", wait_until="load")
    ready = False
    try:
        pg.wait_for_function("() => window.__solarReady === true", timeout=30000)
        ready = True
    except Exception:
        pass

    check(ready, "canh Solar System dung xong (__solarReady)")
    check(not outside(out["req"]), "0 request ra ten mien ngoai",
          str(outside(out["req"])[:3]))
    check(not out["err"], "0 loi trang", str(out["err"][:2]))

    # Không chỉ hỏi "có cờ ready" — hỏi cảnh có VẬT THỂ THẬT không. Một cảnh
    # rỗng vẫn đặt được cờ; thứ chứng minh three.js chạy là canvas WebGL có
    # thật và có nhãn hành tinh do CSS2DRenderer sinh ra.
    n_canvas = pg.evaluate("() => document.querySelectorAll('canvas').length")
    n_label = pg.evaluate(
        "() => document.querySelectorAll('#labels [data-body-id]').length")
    check(n_canvas >= 1, "co canvas WebGL", "(%d)" % n_canvas)
    check(n_label >= 8, "CSS2DRenderer ve du nhan thien the", "(%d)" % n_label)

    # Bloom = EffectComposer + RenderPass + UnrealBloomPass + OutputPass, tức
    # 4 addon kéo theo 6 file phụ. Cảnh dựng được nghĩa là cả 12 file đã về.
    vendor_hits = [u for u in out["req"] if "/vendor/three/" in u]
    check(len(vendor_hits) >= 7,
          "tai three.js tu vendor/ (core + addons)", "(%d file)" % len(vendor_hits))
    pg.close()

    # ---------- landing-app.html: SDK Firebase ----------
    print("\n[2] landing-app.html — SDK Firebase")
    out = {"req": [], "err": []}
    pg = ctx.new_page()
    watch(pg, out)
    pg.goto(BASE + "/landing-app.html", wait_until="load")

    # SDK nạp ĐỘNG: chưa bấm gì thì không được tải byte nào.
    check(not [u for u in out["req"] if "/vendor/firebase/" in u],
          "chua bam gi -> KHONG tai SDK (import dong con nguyen)")

    # ⚠️⚠️ ÉP boot() CHẠY THẬT — VÀ ĐÒI NÓ CHẠY, KHÔNG CHO IM LẶNG BỎ QUA.
    #    Bản đầu của phép kiểm này gọi `m.getOnboarding()`, nhưng module chỉ có
    #    `export default` nên `m.getOnboarding` là undefined → TypeError → rơi
    #    vào try/catch → **0 file nào được tải mà phép kiểm vẫn xanh**, kèm một
    #    dòng ghi chú tôi tự bịa ("chưa điền config") trong khi config ĐÃ điền.
    #    Đúng loại "đạt rỗng" CLAUDE.md đã ghi hai lần. Nay: gọi qua `.default`,
    #    và nếu 0 file SDK được tải thì BÁO HỎNG chứ không giải thích hộ.
    booted = pg.evaluate("""async () => {
      const M = (await import('./js/firebase-auth.js')).default;
      if (!M || typeof M.login !== 'function') return 'khong tim thay M.login';
      // login() gọi boot() ở dòng đầu. Mật khẩu sai với email không tồn tại là
      // probe an toàn — KHÔNG tạo tài khoản nào (dự án đã dùng đúng cách này
      // ngày 26/07/2026 để kiểm apiKey). Trả về lỗi là bình thường.
      try { await M.login('smoke-vendor@astroq.invalid', 'x'.repeat(12)); } catch (e) {}
      return 'ok';
    }""")
    pg.wait_for_timeout(1500)

    fb = [u for u in out["req"] if "/vendor/firebase/" in u]
    check(booted == "ok", "goi duoc AstroQAuth.login()", "(%s)" % booted)
    check(not outside(out["req"]), "0 request ra ten mien ngoai",
          str(outside(out["req"])[:3]))

    # Chặn "đạt rỗng": không tải file nào = phép kiểm dưới vô nghĩa.
    check(len(fb) >= 2, "boot() THAT SU tai SDK", "(%d file)" % len(fb))

    # ⚠️ PHÉP KIỂM QUAN TRỌNG NHẤT CỦA CẢ SCRIPT. `firebase-auth.js` nhúng URL
    #    TUYỆT ĐỐI tới gstatic bên trong nó. Nếu script vendor không viết lại,
    #    ta sẽ thấy firebase-auth.js nằm trong vendor/ mà firebase-app.js thì
    #    ĐI RA gstatic — tức phụ thuộc chưa hề bị gỡ, và grep trên mã dự án mù
    #    hoàn toàn với chuyện đó.
    check(any(u.endswith("/firebase-app.js") for u in fb),
          "firebase-app.js tai TU VENDOR (URL nhung ben trong da duoc viet lai)")
    check(any(u.endswith("/firebase-auth.js") for u in fb),
          "firebase-auth.js tai tu vendor")

    # Lỗi đăng nhập là kết quả MONG ĐỢI của probe — đừng tính nó là lỗi trang.
    real_err = [e for e in out["err"]
                if "auth/" not in e and "400" not in e and "identitytoolkit" not in e]
    check(not real_err, "0 loi trang (bo qua loi dang nhap cua probe)",
          str(real_err[:2]))
    pg.close()

    # ---------- quét cả 18 trang: không trang nào còn gọi ra ngoài ----------
    print("\n[3] Quet 18 trang — khong trang nao goi ra ten mien ngoai")
    import glob, os
    pages = sorted(os.path.basename(p) for p in
                   glob.glob(os.path.join(os.path.dirname(
                       os.path.dirname(os.path.abspath(__file__))), "*.html")))
    dirty = []
    for name in pages:
        out = {"req": [], "err": []}
        pg = ctx.new_page()
        watch(pg, out)
        try:
            pg.goto(BASE + "/" + name, wait_until="load", timeout=25000)
            pg.wait_for_timeout(400)
        except Exception:
            pass
        bad = outside(out["req"])
        if bad:
            dirty.append((name, bad[:2]))
        pg.close()
    check(not dirty, "18/18 trang sach", str(dirty[:3]))
    print("       da quet: %s" % ", ".join(pages))

    ctx.close()
    br.close()


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Thieu playwright: pip install playwright && playwright install chromium")
        return 2

    with sync_playwright() as pw:
        run(pw, blocked=False)
        run(pw, blocked=True)   # phép thử phá hoại: chặn hẳn 4 tên miền ngoài

    print("\n" + "-" * 66)
    print("  KET QUA: %d dat / %d hong" % (_ok, _bad))
    print("-" * 66)
    return 1 if _bad else 0


if __name__ == "__main__":
    sys.exit(main())
