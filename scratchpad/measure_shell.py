# -*- coding: utf-8 -*-
"""
measure_shell.py — ĐO bố cục 3 trang vừa dọn CSS, để chứng minh giao diện KHÔNG đổi.

    python scratchpad/measure_shell.py before > scratchpad/m-before.json
    ... sửa CSS ...
    python scratchpad/measure_shell.py after                 # tự so với m-before.json

Vì sao đo thay vì so ảnh: ảnh bài viết của library.html tải từ NASA nên hai lần
chụp ra hai kết quả khác nhau (19% pixel lệch) dù bố cục y hệt — so ảnh báo hỏng
oan. Đo `getBoundingClientRect` của từng khối thì không phụ thuộc ảnh tải xong
hay chưa. Vẫn CHẶN mọi yêu cầu ra ngoài để chiều cao thẻ không lệch vì ảnh.
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "m-before.json")

# Mỗi trang: các selector đại diện cho khung + phần riêng
PAGES = {
    "games.html":   ["header", ".hero", ".hero h1", ".hero p", ".games",
                     ".gcard", ".currency", ".lang-switch", ".back-btn"],
    "learn.html":   ["header", ".hero", ".hero p", ".htitle", ".modes", ".mode",
                     ".currency", ".lang-switch", ".back-btn"],
    "library.html": ["header", ".layout", ".search", ".srcfilter", ".side",
                     ".feat", ".feat-body", ".acard", ".currency", ".lang-switch"],
}
VIEWS = [("desktop", 1440, 950), ("mobile", 390, 844)]
USER = {"name": "Bi Bo", "pilotName": "Bi Bo", "character": "m",
        "selectedCharacter": "m", "avatar": "ava/avam.png", "uid": "UID1234"}


def measure():
    out = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for page_name, sels in PAGES.items():
            for vname, w, h in VIEWS:
                ctx = b.new_context(viewport={"width": w, "height": h},
                                    device_scale_factor=1, locale="vi-VN")
                ctx.add_init_script(
                    f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
                    "localStorage.setItem('astroq-lang','vi');"
                    "localStorage.setItem('astroq-asteroids','41');"
                    "localStorage.setItem('astroq-tour-seen','1');")
                # Chặn MỌI thứ ra ngoài (ảnh NASA, SDK Firebase) — ảnh tải được hay
                # không sẽ đổi chiều cao thẻ và làm phép so vô nghĩa.
                ctx.route("**://**", lambda r: (r.continue_() if "127.0.0.1" in r.request.url
                                                or "localhost" in r.request.url else r.abort()))
                p = ctx.new_page()
                p.goto(BASE + page_name, wait_until="load")
                p.wait_for_timeout(1600)
                data = p.evaluate("""(sels) => {
                    const o = {
                      scrollW: document.documentElement.scrollWidth,
                      scrollH: document.documentElement.scrollHeight,
                      innerW: window.innerWidth
                    };
                    for (const s of sels) {
                      const e = document.querySelector(s);
                      if (!e) { o[s] = null; continue; }
                      const r = e.getBoundingClientRect();
                      o[s] = [Math.round(r.x), Math.round(r.y),
                              Math.round(r.width), Math.round(r.height)];
                    }
                    return o;
                }""", sels)
                out[f"{page_name}:{vname}"] = data
                ctx.close()
        b.close()
    return out


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "after"
    cur = measure()

    if tag == "before":
        with open(SNAP, "w", encoding="utf-8") as f:
            json.dump(cur, f, indent=1, ensure_ascii=False)
        print(f"Da luu moc do vao {SNAP}")
        return 0

    if not os.path.exists(SNAP):
        print("Chua co m-before.json — chay `measure_shell.py before` truoc.")
        return 1
    with open(SNAP, encoding="utf-8") as f:
        old = json.load(f)

    ok_n = bad_n = 0
    TOL = 2          # lệch ≤2px coi như không đổi (bo tròn subpixel)
    for key in sorted(cur):
        a, b = old.get(key, {}), cur[key]
        # Tràn ngang là lỗi NGHIÊM TRỌNG, kiểm riêng
        overflow = b["scrollW"] > b["innerW"] + 1
        if overflow:
            bad_n += 1
            print(f"  [HONG] {key}: TRAN NGANG scrollW={b['scrollW']} > innerW={b['innerW']}")
        for f_ in sorted(b):
            if f_ in ("innerW",):
                continue
            va, vb = a.get(f_), b[f_]
            if va is None and vb is None:
                continue
            if isinstance(vb, list) and isinstance(va, list):
                d = max(abs(x - y) for x, y in zip(va, vb))
                if d <= TOL:
                    ok_n += 1
                else:
                    bad_n += 1
                    print(f"  [HONG] {key} {f_}: {va} -> {vb} (lech {d}px)")
            elif isinstance(vb, (int, float)) and isinstance(va, (int, float)):
                d = abs(va - vb)
                if d <= TOL:
                    ok_n += 1
                else:
                    bad_n += 1
                    print(f"  [HONG] {key} {f_}: {va} -> {vb} (lech {d}px)")
            else:
                bad_n += 1
                print(f"  [HONG] {key} {f_}: {va} -> {vb}")

    print(f"\n=== KET QUA: {ok_n} khop / {bad_n} lech ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
