# -*- coding: utf-8 -*-
r"""probe_nasa_thumb.py — KIỂM ảnh NASA của kho bài đọc: bản `~small` có THẬT,
đủ nét cho thẻ lưới, và `library.html` chỉ kéo bản nhỏ ở lưới còn bản lớn ở thẻ hero.

    python scratchpad/probe_nasa_thumb.py            # đủ (có gọi mạng NASA)
    python scratchpad/probe_nasa_thumb.py --offline  # bỏ phần gọi mạng

⚠️⚠️ ĐO Ở TẦNG MẠNG, KHÔNG ĐỌC THẺ KHAI. `js/articles-index.js` đã ghi cảnh báo
   *"⛔ đừng đoán đường dẫn ảnh NASA theo mẫu — `~large` KHÔNG tồn tại với mọi ảnh"*.
   Đo lại 25/08/2026 thì đúng thế: `~medium`/`~large` trả **403** ở 3/6 ảnh này.
   Nên mọi URL phải TẢI VỀ và đo bằng PIL; đọc `content-length` một mình thì không
   biết ảnh rộng bao nhiêu pixel.

⚠️ MỐC BỀ RỘNG SUY TỪ CHỖ VẼ, không gõ cứng: thẻ lưới `.card .imgbox` cao 130px và
   rộng ~219px ⇒ ở DPR2 cần **438px**. Bản `~small` là 640px ⇒ dư 1,46× — vừa đủ,
   không phải dư 6,7× như `~orig`.

⚠️ PHÉP KIỂM QUAN TRỌNG NHẤT LÀ MỤC [3]: nó mở CHÍNH `library.html` trên Chromium
   rồi ĐẾM BYTE THẬT theo từng URL. Đọc mã nguồn thì chỉ chứng minh `imgboxHtml`
   nhận tham số; nó KHÔNG chứng minh trình duyệt đã tải bản nhỏ — `loading="lazy"`,
   `srcset`, hay một lời gọi `imgboxHtml(a)` còn sót ở đâu đó đều làm lệch.
"""
import http.server
import io
import json
import os
import re
import socketserver
import sys
import threading
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OFFLINE = "--offline" in sys.argv
PORT = 8134
SITE = "http://localhost:%d" % PORT
NEED_W = 438            # bề rộng thẻ lưới × DPR2
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))


def fetch(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


# ── [1] Đọc danh mục: bài nào có ảnh thì phải có `thumb` ────────────────────
print("=== [1] Mục lục: mọi bài có `img` đều phải có `thumb` ===")
idx = io.open("js/articles-index.js", encoding="utf-8").read()
rows = re.findall(r"\{ ord: .*?\}", idx)
check("[1] đọc được mục lục", len(rows) > 50, "%d bài" % len(rows))
if len(rows) <= 50:
    sys.exit("khong doc duoc muc luc — dung han (moi phep kiem sau se dat RONG)")

with_img, with_thumb, missing = [], [], []
for r in rows:
    aid = re.search(r'id: "([^"]+)"', r).group(1)
    im = re.search(r'img: "([^"]+)"', r)
    th = re.search(r'thumb: "([^"]+)"', r)
    if im:
        with_img.append((aid, im.group(1)))
        if th:
            with_thumb.append((aid, th.group(1)))
        else:
            missing.append(aid)

check("[1] có bài mang ảnh", len(with_img) > 0, "%d bài" % len(with_img))
check("[1] MỌI bài có ảnh đều khai `thumb`", not missing, "thiếu: %s" % missing)
check("[1] `thumb` KHÁC `img` ở mọi bài",
      all(t != dict(with_img)[a] for a, t in with_thumb),
      "%d cặp" % len(with_thumb))
# Bản nhỏ phải là `~small` — không phải một tên biến thể đoán bừa.
check("[1] mọi `thumb` là bản `~small`",
      all("~small" in t for _, t in with_thumb),
      str([t for _, t in with_thumb if "~small" not in t])[:80])

# ── [2] Mạng: `~small` có thật, đủ nét, và nhẹ hơn hẳn ─────────────────────
if OFFLINE:
    print("\n=== [2] BỎ QUA phần gọi mạng (--offline) ===")
else:
    print("\n=== [2] Tải thật từ images-assets.nasa.gov ===")
    try:
        from PIL import Image
    except Exception:
        Image = None
        print("  [!] khong co Pillow — bo qua phep do kich thuoc")
    big_tot = small_tot = 0
    all_ok = True
    for aid, thumb in with_thumb:
        img = dict(with_img)[aid]
        try:
            db, ds = fetch(img), fetch(thumb)
        except Exception as e:
            all_ok = False
            print("     %-15s LOI %s" % (aid, str(e)[:50]))
            continue
        big_tot += len(db)
        small_tot += len(ds)
        w = h = "?"
        if Image:
            im = Image.open(io.BytesIO(ds))
            w, h = im.width, im.height
            if w < NEED_W:
                all_ok = False
        print("     %-15s hero %7.0fKB   thumb %6.0fKB  %sx%s" %
              (aid, len(db) / 1024, len(ds) / 1024, w, h))
    check("[2] mọi URL tải được (hero + thumb)", all_ok)
    check("[2] mọi `thumb` rộng >= %dpx (đủ nét cho thẻ lưới)" % NEED_W, all_ok)
    check("[2] bản nhỏ cắt được >= 60%% byte", small_tot < big_tot * 0.4,
          "%.0fKB -> %.0fKB (-%.0f%%)" % (big_tot / 1024, small_tot / 1024,
                                          100 - 100.0 * small_tot / big_tot))

# ── [3] Trên TRANG THẬT: lưới kéo bản nhỏ, hero kéo bản lớn ────────────────
print("\n=== [3] Mở library.html trên Chromium, đếm byte theo URL ===")
from playwright.sync_api import sync_playwright


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", PORT), Quiet)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        # ⚠️⚠️ PHẢI GHIM BÀI NÀO LÀM THẺ HERO, KHÔNG ĐO Ở TRẠNG THÁI MẶC ĐỊNH.
        #    `featured()` chọn "bài CHƯA ĐỌC đầu tiên theo thứ tự mục lục", mà bài
        #    `ord` nhỏ nhất là `art-moons-891-and-counting` với `img: null` ⇒ máy sạch
        #    thì thẻ hero KHÔNG CÓ ẢNH và phép đo "hero kéo bản lớn" đạt/hỏng tuỳ
        #    lịch sử đọc của máy chạy test. Gieo `astroq-read` = mọi bài TRỪ
        #    `lib-nebula` để nó chắc chắn thành hero.
        #    (Đây cũng là số đo đáng ghi: ở trạng thái MẶC ĐỊNH thì library.html
        #     kéo ĐÚNG 6 ảnh bản nhỏ = 229 KB, 0 ảnh bản lớn.)
        hero_id = "lib-nebula"
        read = [a for a, _ in with_img if a != hero_id]
        read += [re.search(r'id: "([^"]+)"', r).group(1) for r in rows
                 if re.search(r'id: "([^"]+)"', r).group(1) not in dict(with_img)]
        ctx = b.new_context(viewport={"width": 1440, "height": 900},
                            device_scale_factor=2, locale="vi-VN")
        ctx.add_init_script(
            "try{localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-read'," + json.dumps(json.dumps(read)) + ")}catch(e){}")
        pg = ctx.new_page()
        seen = {}

        def on_resp(r):
            if "images-assets.nasa.gov" in r.url:
                seen.setdefault(r.url, r.status)

        pg.on("response", on_resp)
        pg.goto(SITE + "/library.html", wait_until="load", timeout=60000)
        # Cuộn hết trang: ảnh thẻ có `loading="lazy"`, không cuộn thì không tải.
        for _ in range(12):
            pg.mouse.wheel(0, 1400)
            pg.wait_for_timeout(220)
        pg.wait_for_timeout(1500)

        small = [u for u in seen if "~small" in u]
        big = [u for u in seen if "~small" not in u]
        bad_status = {u: s for u, s in seen.items() if s != 200}
        print("     bản nhỏ tải về: %d · bản lớn tải về: %d" % (len(small), len(big)))
        for u in sorted(seen):
            print("       %s  HTTP %s" % (u.split("/")[-1], seen[u]))

        check("[3] 0 ảnh NASA nào trả mã lỗi", not bad_status, str(bad_status)[:90])
        # Thẻ lưới nhiều hơn hero, nên bản nhỏ phải nhiều hơn bản lớn.
        check("[3] lưới kéo bản `~small`", len(small) >= 4, "%d ảnh" % len(small))
        # ⚠️ Hero LÀ chỗ duy nhất được kéo bản lớn — 0 là hỏng (thẻ lớn mất ảnh),
        #    nhiều hơn 1 cũng hỏng (một lời gọi imgboxHtml còn sót không truyền `big`).
        check("[3] ĐÚNG MỘT ảnh bản lớn (chỉ thẻ hero)", len(big) == 1,
              str([u.split("/")[-1] for u in big]))

        # Ảnh của thẻ hero phải to hơn ảnh của thẻ lưới — đo bề rộng THẬT trên DOM.
        sizes = pg.evaluate("""() => [...document.querySelectorAll('.imgbox img')]
            .filter(i=>i.currentSrc && /images-assets/.test(i.currentSrc))
            .map(i=>({small:/~small/.test(i.currentSrc), nw:i.naturalWidth,
                      rw:Math.round(i.getBoundingClientRect().width)}))""")
        feat = [s for s in sizes if not s["small"]]
        grid = [s for s in sizes if s["small"]]
        check("[3] ảnh hero ĐỦ NÉT (>= 2x bề rộng vẽ)",
              bool(feat) and all(s["nw"] >= s["rw"] * 2 for s in feat),
              str(feat)[:110])
        check("[3] ảnh thẻ lưới ĐỦ NÉT (>= 2x bề rộng vẽ)",
              bool(grid) and all(s["nw"] >= s["rw"] * 2 for s in grid),
              "%d thẻ, ví dụ %s" % (len(grid), grid[0] if grid else "-"))
        # Và KHÔNG dư quá tay — đây là chính lỗi vừa đi sửa.
        check("[3] ảnh thẻ lưới KHÔNG dư quá 2,5x",
              bool(grid) and all(s["nw"] <= s["rw"] * 2 * 2.5 for s in grid),
              str([s for s in grid if s["nw"] > s["rw"] * 5])[:90])

        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.reload(wait_until="load")
        pg.wait_for_timeout(1200)
        check("[3] 0 lỗi trang", not errs, str(errs[:2])[:90])
        ctx.close()
        b.close()
finally:
    httpd.shutdown()

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(0 if bad_n == 0 else 1)
