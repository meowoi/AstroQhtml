# -*- coding: utf-8 -*-
r"""Đo nút "chơi lại" ở bảng kết quả của CẢ 10 mini-game.

⚠️ VÌ SAO CẦN: chủ dự án chơi thật rồi báo hai chỗ ở bảng kết quả mê cung —
   *"nút Mê cung khác đang bị xuống dòng và thiếu hình thiên thạch sau số 3"*.
   Rà ra thì đó KHÔNG phải lỗi của một trang: **7/10 game** thiếu ảnh Thiên thạch
   tím trong nhãn nút, VÀ gán cứng con số phí (`<b>3</b>`) trong khi phí là thứ
   SERVER quyết (`Wallet.Fees`) và **đã đổi ngày 15/08/2026** (defender 5→4 ·
   catch 3→4 · maze 4→3 · racer 5→4). Hôm nay bảy con số đó tình cờ còn đúng,
   nhưng chúng sẽ nói SAI vào lần đổi phí tiếp theo — và `check_pages` mục [9]
   chỉ đối chiếu `CONFIG.COST` với chuỗi *"Mỗi lượt: n"* ở `games.html`, KHÔNG
   canh nhãn nút này.

⚠️ ĐO CHỨ KHÔNG ĐỌC CSS: "nút bị xuống dòng" là chuyện của bố cục thật. `.ov`
   dùng `opacity`/`visibility` (không phải `display:none`) nên bảng kết quả GIỮ
   BỐ CỤC kể cả khi đang ẩn — đo được mà không phải chơi hết lượt.
   Số dòng suy từ `clientHeight / lineHeight`, và đo ở CẢ khổ rộng lẫn khổ hẹp.
"""
import re
import sys
import glob
import os

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8123"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VIEWPORTS = (("rong  1440x900", {"width": 1440, "height": 900}),
             ("hep    390x844", {"width": 390, "height": 844}))

ok_n = bad_n = 0


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""), flush=True)
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""), flush=True)


def games():
    """Danh sach game suy tu chinh thu muc, khong gan cung — them game khong phai
    sua bo do (bai hoc `_GAME_FILE` gan cung o check_pages, 14/08/2026)."""
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "game-*.html"))):
        src = open(p, encoding="utf-8").read()
        if "again-btn" not in src:
            continue
        m = re.search(r"COST:\s*(\d+)", src)
        out.append((os.path.basename(p), int(m.group(1)) if m else None, src))
    return out


MEASURE = """() => {
  const b = document.getElementById('again-btn');
  if (!b) return null;
  const cs = getComputedStyle(b);
  const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
  // chieu cao phan CHU (tru padding + vien) -> so dong
  const inner = b.clientHeight
              - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  const img = b.querySelector('img');
  return {w: Math.round(b.getBoundingClientRect().width),
          lines: Math.max(1, Math.round(inner / lh)),
          txt: (b.textContent || '').trim(),
          img: !!img,
          imgW: img ? Math.round(img.getBoundingClientRect().width) : 0,
          nowrap: cs.whiteSpace.indexOf('nowrap') >= 0
                  || (b.querySelector('.btn-fee')
                      && getComputedStyle(b.querySelector('.btn-fee'))
                         .whiteSpace.indexOf('nowrap') >= 0)};
}"""

with sync_playwright() as p:
    br = p.chromium.launch()
    for fname, cost, src in games():
        print("\n=== %s (COST %s) ===" % (fname, cost))
        # nhan phai suy tu CONFIG.COST, khong gan cung con so
        # CANH BAO: nhan khai theo HAI dang, phai nhan ca hai —
        #   `again_btn:"..."`  (7 game co CONFIG khai TRUOC tu dien), va
        #   `get again_btn(){ return "..."; }`  (4 game lop quyet dinh: o do
        #   CONFIG khai SAU tu dien, nen noi suy luc dung tu dien la
        #   `Cannot read properties of undefined (reading 'COST')` — GIET ca chuoi
        #   khoi dong. Getter thi luc DOC moi noi suy, va luc do CONFIG da co.
        #   Tien le: 4 khoa `kb_*` cua js/pick-place.js (31/07/2026).
        m = re.search(r'(?:get\s+)?again_btn\s*(?::|\(\)\s*\{\s*return)\s*(.+?);?\s*(?:\},|,\s*to_hub|$)',
                      src, re.S)
        lab = m
        lab = lab.group(1) if lab else ""
        check("CONFIG.COST" in lab, "nhan nut suy tu CONFIG.COST (khong gan cung)",
              lab.strip()[:52])
        check("tt.png" in lab, "nhan nut co anh Thien thach tim")

        for tag, vw in VIEWPORTS:
            ctx = br.new_context(viewport=vw, locale="vi-VN",
                                 timezone_id="Asia/Ho_Chi_Minh")
            ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                                "localStorage.setItem('astroq-asteroids','300');")
            pg = ctx.new_page()
            pg.goto("%s/%s" % (BASE, fname), wait_until="load", timeout=30000)
            pg.wait_for_timeout(900)
            d = pg.evaluate(MEASURE)
            if d is None:
                check(False, "%s: tim thay nut #again-btn" % tag)
                ctx.close()
                continue
            print("      %s  rong=%dpx  dong=%d  anh=%s(%dpx)  %r"
                  % (tag, d["w"], d["lines"], d["img"], d["imgW"], d["txt"][:34]))
            check(d["lines"] == 1, "%s: nhan nut nam TRON MOT DONG" % tag,
                  "%d dong" % d["lines"])
            check(d["img"] and d["imgW"] >= 10,
                  "%s: anh tt HIEN RA THAT (khong phai the img 0px)" % tag,
                  "%dpx" % d["imgW"])
            if cost is not None:
                check(str(cost) in d["txt"],
                      "%s: nhan nut noi dung con so phi cua game" % tag,
                      "phi %d, nhan %r" % (cost, d["txt"][:30]))
            ctx.close()
    br.close()

print("\n" + "=" * 56)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
