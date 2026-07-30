# -*- coding: utf-8 -*-
"""
shot_pages.py — chụp ảnh 3 trang trước/sau khi dọn CSS trùng lặp, rồi SO PIXEL.

    python scratchpad/shot_pages.py before
    ... sửa CSS ...
    python scratchpad/shot_pages.py after      # tự so với bản before và in % khác

Vì sao cần: chuyển games.css / learn.css / library.css sang dùng css/page-shell.css
là việc dọn dẹp — **giao diện phải KHÔNG đổi**. Đọc CSS bằng mắt không thấy được
chỗ nào lệch vài pixel; so ảnh thì thấy.
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = ["games.html", "learn.html", "library.html"]
VIEWS = [("desktop", 1440, 950), ("mobile", 390, 844)]

USER = {"name": "Bi Bo", "pilotName": "Bi Bo", "character": "m",
        "selectedCharacter": "m", "avatar": "ava/avam.png", "uid": "UID1234"}


def shots(tag):
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for page_name in PAGES:
            for vname, w, h in VIEWS:
                ctx = b.new_context(viewport={"width": w, "height": h},
                                    device_scale_factor=1, locale="vi-VN")
                ctx.add_init_script(
                    f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
                    "localStorage.setItem('astroq-lang','vi');"
                    "localStorage.setItem('astroq-asteroids','41');"
                    "localStorage.setItem('astroq-tour-seen','1');")
                # CHẶN mọi yêu cầu ra ngoài. Ảnh bài viết của library.html tải từ
                # NASA nên hai lần chụp ra hai kết quả khác nhau (đo được 19% pixel
                # lệch) dù bố cục y hệt — so ảnh sẽ báo hỏng oan.
                ctx.route("**://**", lambda r: (r.continue_()
                          if ("127.0.0.1" in r.request.url or "localhost" in r.request.url)
                          else r.abort()))
                p = ctx.new_page()
                p.goto(BASE + page_name, wait_until="load")
                p.wait_for_timeout(1800)
                # Tắt mọi animation để 2 lần chụp không lệch vì sao đang nhấp nháy
                p.add_style_tag(content="*{animation:none !important;transition:none !important}")
                p.wait_for_timeout(250)
                sw = p.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
                if sw[0] > sw[1] + 1:
                    print(f"  [!] {page_name} {vname}: TRAN NGANG scrollW={sw[0]} > {sw[1]}")
                name = f"{tag}-{page_name.replace('.html','')}-{vname}.png"
                p.screenshot(path=os.path.join(HERE, name), full_page=True)
                out.append(name)
                ctx.close()
        b.close()
    return out


def diff(a, b):
    """% pixel khác nhau giữa 2 ảnh PNG (dùng Pillow — đã có sẵn cho việc nén ảnh)."""
    from PIL import Image, ImageChops
    ia = Image.open(os.path.join(HERE, a)).convert("RGB")
    ib = Image.open(os.path.join(HERE, b)).convert("RGB")
    if ia.size != ib.size:
        return None, f"KHAC CO ANH {ia.size} vs {ib.size}"
    d = ImageChops.difference(ia, ib)
    # Đếm pixel lệch rõ (>8/255 mỗi kênh) — bỏ qua nhiễu nén
    bad = sum(1 for px in d.getdata() if px[0] > 8 or px[1] > 8 or px[2] > 8)
    tot = ia.size[0] * ia.size[1]
    return bad / tot * 100, f"{bad}/{tot} px"


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "before"
    names = shots(tag)
    print(f"Da chup {len(names)} anh voi tag '{tag}'")
    if tag != "after":
        return 0

    print("\n=== SO ANH before vs after ===")
    worst = 0.0
    for n in names:
        b4 = n.replace("after-", "before-", 1)
        if not os.path.exists(os.path.join(HERE, b4)):
            print(f"  [BO QUA] {n} — chua co ban before")
            continue
        pct, detail = diff(b4, n)
        if pct is None:
            print(f"  [KHAC CO] {n} — {detail}")
            worst = 100.0
            continue
        worst = max(worst, pct)
        flag = "[OK]  " if pct < 0.5 else "[XEM ]"
        print(f"  {flag} {n}: lech {pct:.3f}%  ({detail})")
    print(f"\nLech lon nhat: {worst:.3f}%")
    print("Duoi 0.5% = coi nhu khong doi giao dien." if worst < 0.5
          else "TREN 0.5% — mo anh ra soi truoc khi chot.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
