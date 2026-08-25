# -*- coding: utf-8 -*-
r"""probe_font_mono.py — TRANG NÀO THẬT SỰ VẼ CHỮ BẰNG SHARE TECH MONO, và đối chiếu
với `NO_MONO` của `scratchpad/sync_font_preload.py`.

    python scratchpad/probe_font_mono.py

⚠️⚠️ VÌ SAO KHÔNG DÙNG LẠI `_font_usage.py`: BỘ ĐÓ NAY MÙ VỚI CÂU HỎI NÀY.
   Nó đếm file `.woff2` được TẢI VỀ. Nhưng từ 25/08/2026 mọi trang có khối
   `FONT-PRELOAD`, mà `preload` **bỏ qua `unicode-range`** nên nó tải vô điều kiện ⇒
   trang nào cũng báo đủ 5 font, kể cả trang không vẽ một chữ mono nào. Nghĩa là
   `_font_usage.py` chỉ còn đo được CHÍNH CÁI PRELOAD của mình — một phép đo tự khẳng
   định. Đúng cái bẫy "phép kiểm đạt một cách RỖNG" mà dự án đã trả giá nhiều lần.
   ⇒ Ở đây đo **`getComputedStyle().fontFamily`** của MỌI phần tử: đó là thứ duy nhất
     nói được trang có CHỮ nào vẽ bằng phông mono hay không, và nó **độc lập hoàn
     toàn** với việc file có được preload hay không.

⚠️ ĐO CẢ HAI NGÔN NGỮ. Nhãn HUD dịch theo VI/EN, và một trang có thể chỉ có phần tử
   mono ở một trong hai bản (chuỗi rỗng thì không có gì để vẽ).

⚠️ `--font-mono` ĐƯỢC KHAI Ở 8 FILE CSS, nhưng KHAI KHÔNG PHẢI LÀ DÙNG — đừng suy
   `NO_MONO` từ việc grep CSS. Đó là lý do bộ đo này render thật.

⚠️ HỎNG MỀM CẢ HAI CHIỀU (nên đây là phép kiểm nhắc việc, không phải cổng chặn):
   trang trong `NO_MONO` mà lại dùng mono ⇒ nhãn HUD đổi phông muộn một lần;
   trang ngoài `NO_MONO` mà thôi dùng ⇒ tải thừa 13,5 KB. Không ca nào làm vỡ trang.
"""
import glob
import http.server
import importlib.util
import os
import socketserver
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PORT = 8138
MONO = "share-tech-mono"

# Đọc NO_MONO THẲNG từ bộ sinh — chép sang đây là hai nơi giữ một danh sách, và bên
# lệch sẽ là bên nói với người đọc rằng mọi thứ đang khớp.
_spec = importlib.util.spec_from_file_location(
    "_sfp", os.path.join("scratchpad", "sync_font_preload.py"))
_sfp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sfp)
NO_MONO = set(_sfp.NO_MONO)

FAM = """() => {
  const out = [];
  for (const e of document.querySelectorAll('*')) {
    const f = getComputedStyle(e).fontFamily || '';
    if (!/Share Tech Mono/i.test(f)) continue;
    const t = (e.textContent || '').trim();
    if (!t) continue;                 // phần tử rỗng thì không vẽ chữ nào
    out.push(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '')
             + ' :: ' + t.slice(0, 24));
  }
  return out;
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright

    pages = sorted(glob.glob("*.html"))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    hits = {}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for page in pages:
                found = []
                for lang in ("vi", "en"):
                    ctx = b.new_context(viewport={"width": 500, "height": 844},
                                        locale=lang)
                    ctx.add_init_script(
                        "try{localStorage.setItem('astroq-lang','%s');"
                        "localStorage.setItem('astroq-tour-seen','1');"
                        "localStorage.setItem('astroq-map01-seen','1')}catch(e){}" % lang)
                    pg = ctx.new_page()
                    try:
                        pg.goto("http://localhost:%d/%s" % (PORT, page),
                                wait_until="load", timeout=45000)
                        pg.wait_for_timeout(1800)
                        found += pg.evaluate(FAM)
                    except Exception as e:
                        # ⚠️ Không im lặng bỏ qua: một trang mở hỏng mà bị tính là
                        #    "0 phần tử mono" chính là cách phép kiểm này đạt một cách
                        #    RỖNG rồi đề nghị thêm trang đó vào NO_MONO.
                        found.append("!!LOI!! %s" % str(e)[:70])
                    ctx.close()
                hits[page] = found
            b.close()
    finally:
        httpd.shutdown()

    err = [p for p, v in hits.items() if any(x.startswith("!!LOI!!") for x in v)]
    used = {p for p, v in hits.items() if v and p not in err}
    unused = {p for p, v in hits.items() if not v and p not in err}

    print("=== %d trang · %d dùng mono · %d KHÔNG dùng ===" % (len(pages), len(used),
                                                              len(unused)))
    for p in sorted(unused):
        print("  KHONG dung mono: %s" % p)
    for p in err:
        print("  [LOI] %s -> %s" % (p, hits[p][0]))

    ok = bad = 0

    def chk(label, cond, detail=""):
        nonlocal ok, bad
        if cond:
            ok += 1
            print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
        else:
            bad += 1
            print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))

    print("\n=== Đối chiếu với NO_MONO của sync_font_preload.py ===")
    chk("đọc được NO_MONO từ bộ sinh", len(NO_MONO) > 0, str(sorted(NO_MONO)))
    chk("mọi trang mở được (0 lỗi render)", not err, str(err))
    chk("tập trang KHÔNG dùng mono ĐÚNG BẰNG NO_MONO", unused == NO_MONO,
        "thừa trong NO_MONO=%s · thiếu=%s" % (sorted(NO_MONO - unused),
                                              sorted(unused - NO_MONO)))
    # Hai chiều, mỗi chiều một câu để đọc log biết ngay phải sửa hướng nào.
    chk("không trang nào trong NO_MONO mà lại VẼ chữ mono",
        not (NO_MONO & used), str(sorted(NO_MONO & used)))
    chk("không trang nào ngoài NO_MONO mà KHÔNG vẽ chữ mono",
        not (unused - NO_MONO), str(sorted(unused - NO_MONO)))

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok, bad))
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
