# -*- coding: utf-8 -*-
"""probe_public.py — TRANG NÀO KHÁCH VÀO ĐƯỢC KHI CHƯA ĐĂNG NHẬP.

Chủ dự án hỏi *"gửi lại link thực tế khách sẽ vào để tôi test, ko cần đăng nhập"*.
Bộ này đo thật trên astroq.org bằng Chromium **ngữ cảnh sạch** (không localStorage,
không phiên), rồi xếp từng trang vào một trong bốn loại:

  MO       mở được và dùng được ngay
  TUONG    mở ra nhưng bị chặn / đòi đăng nhập
  CHUYEN   tự chuyển sang trang khác
  HONG     lỗi trang hoặc không tải được

⚠️ ĐO CHỨ KHÔNG ĐOÁN. Nhiều trang `noindex` nhưng vẫn dùng được khi chưa đăng nhập
   (quiz rơi về "chưa biết cấp", ví đọc từ localStorage) — `noindex` nói về việc
   Google có lập chỉ mục hay không, KHÔNG nói về việc khách có vào được hay không.
   Hai chuyện đó bị lẫn thì gửi cho khách một danh sách link sai.

  python scratchpad/probe_public.py
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"

# Thứ tự = hành trình khách đi, không phải thứ tự chữ cái.
PAGES = [
    ("/",                              "Trang chủ (VI) — đăng ký danh sách chờ"),
    ("/en/",                           "Trang chủ (EN)"),
    ("/wiki/",                         "Mục lục Wiki (VI)"),
    ("/wiki/en/",                      "Mục lục Wiki (EN)"),
    ("/wiki/purple-meteors-hoat-dong.html", "Wiki — bài về Purple Meteors"),
    ("/landing-app.html",              "Màn đăng nhập / đăng ký"),
    ("/pricing.html",                  "Bảng giá"),
    ("/select.html",                   "Chọn phi hành gia"),
    ("/dashboard.html",                "Buồng lái (bàn điều khiển)"),
    ("/quiz.html",                     "Đấu Trường Kiến Thức"),
    ("/library.html",                  "Góc Khám Phá (bài đọc)"),
    ("/learn.html",                     "Trang một bài đọc"),
    ("/codex.html",                    "Sổ Tay Thuật Ngữ"),
    ("/games.html",                    "Trạm Huấn Luyện (10 game)"),
    ("/game-dodge.html",               "Game — Né Thiên Thạch"),
    ("/game-racer.html",               "Game — Đường Đua Sao Chổi"),
    ("/game-constellation.html",       "Game — Ghép Chòm Sao"),
    ("/game-maze.html",                "Game — Mê Cung Thiên Hà"),
    ("/explorer.html",                 "Trình khám phá 3D"),
    ("/missions.html",                 "Sảnh Nhiệm Vụ"),
    ("/mission-earth.html",            "Nhiệm vụ 01 — Trái Đất"),
    ("/mission-orbit.html",            "Nhiệm vụ 02 — Mắt Thần Trên Quỹ Đạo"),
    ("/lab.html",                      "Phòng Nghiên Cứu"),
    ("/achievements.html",             "Kho Thành Tích"),
    ("/crew.html",                     "Phi Hành Đoàn"),
    ("/shop.html",                     "Cửa hàng trang trí"),
    ("/profile.html",                  "Hồ sơ"),
    ("/parent.html",                   "Góc phụ huynh"),
    ("/specimen-vault.html",           "Kho Mẫu Vật"),
    ("/mission-map.html",              "Bản đồ nhiệm vụ"),
]

rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for path, ten in PAGES:
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                            timezone_id="Asia/Ho_Chi_Minh")
        # ⚠️ Ngữ cảnh SẠCH mỗi trang: không gieo gì cả. Gieo `astroq-user` là biến bộ
        #    đo thành "đã đăng nhập" và trả lời sai đúng câu đang hỏi.
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        loai = ghi_chu = ""
        try:
            pg.goto(SITE + path, wait_until="load", timeout=45000)
            pg.wait_for_timeout(3000)
            url = pg.url
            if url.rstrip("/").split("astroq.org")[-1].rstrip("/") != path.rstrip("/"):
                loai = "CHUYEN"
                ghi_chu = "-> " + url.replace(SITE, "")
            else:
                # Có tường đăng nhập không? Dò cả overlay và dải nhắc.
                wall = pg.evaluate("""() => {
                    const vis = e => { if(!e) return false;
                        const s = getComputedStyle(e), r = e.getBoundingClientRect();
                        return s.display!=='none' && s.visibility!=='hidden' && r.height>4; };
                    const ov = document.querySelector('.auth-overlay.show, .lk-modal.show');
                    if (vis(ov)) return 'hop dang nhap/khoa dang mo';
                    const t = (document.body.innerText||'').toLowerCase();
                    for (const s of ['đăng nhập để', 'vui lòng đăng nhập', 'please sign in',
                                     'sign in to'])
                        if (t.includes(s)) return 'co dai nhac dang nhap';
                    return '';
                }""")
                body = pg.evaluate("() => (document.body.innerText||'').trim().length")
                if body < 40:
                    loai, ghi_chu = "TUONG", "trang gan nhu trong (%d ky tu)" % body
                elif wall:
                    loai, ghi_chu = "TUONG", wall
                else:
                    loai = "MO"
                    ghi_chu = "%d ky tu chu" % body
        except Exception as e:
            loai, ghi_chu = "HONG", type(e).__name__
        if errs and loai == "MO":
            ghi_chu += " · %d loi trang" % len(errs)
        rows.append((loai, path, ten, ghi_chu))
        ctx.close()
    b.close()

order = {"MO": 0, "TUONG": 1, "CHUYEN": 2, "HONG": 3}
rows.sort(key=lambda r: (order[r[0]], r[1]))
print("\n%-7s %-34s %-38s %s" % ("LOAI", "DUONG DAN", "TEN", "GHI CHU"))
print("-" * 118)
for loai, path, ten, gc in rows:
    print("%-7s %-34s %-38s %s" % (loai, path, ten[:37], gc[:44]))

from collections import Counter
c = Counter(r[0] for r in rows)
print("\n=== %d trang: %s ===" % (len(rows), ", ".join("%s %d" % (k, v) for k, v in c.items())))
print("\nLINK MO DUOC NGAY (khong can dang nhap):")
for loai, path, ten, gc in rows:
    if loai == "MO":
        print("  %s%s" % (SITE, path))
