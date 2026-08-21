# -*- coding: utf-8 -*-
r"""Đo BẢN GỘP `scratchpad/racer-test-build.html` trên Chromium thật.

⚠️⚠️ ĐÂY MỚI LÀ BẰNG CHỨNG, KHÔNG PHẢI PHÉP QUÉT REGEX Ở `bundle_racer.py`.
   Hàng rào tĩnh của bộ gộp chỉ soi được MARKUP của tài liệu; nó không trả lời
   được câu duy nhất đáng hỏi: *bản gộp có xin một byte nào từ bên ngoài không*.
   Artifact chạy dưới CSP chặn mọi host lạ (chỉ Google Fonts được), nên một lời
   gọi mạng còn sót là một thứ HỎNG CÂM trên máy người khác — ở máy tôi thì file
   vẫn nằm cạnh đó nên không bao giờ lộ. Bộ này đếm request thật.

⚠️ PHẢI BỌC `<!doctype>/<head>/<body>` RỒI PHỤC VỤ QUA HTTP, đừng mở `file://`:
   Artifact bọc y như vậy lúc publish, và `localStorage` trên `file://` không
   phải cùng một origin ổn định — mà cả bản thử dựa vào ví nạp sẵn trong đó.
"""
import http.server
import io
import os
import socketserver
import sys
import tempfile
import threading

sys.stdout.reconfigure(encoding="utf-8")

SRC = os.path.join("scratchpad", "racer-test-build.html")
PORT = 8231
ok_n = bad_n = 0


def chk(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""))
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""))


body = io.open(SRC, encoding="utf-8", newline=None).read()
tmp = tempfile.mkdtemp(prefix="racerwrap")
io.open(os.path.join(tmp, "index.html"), "w", encoding="utf-8",
        newline="\n").write(
    '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    "</head><body>\n" + body + "\n</body></html>")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=tmp, **k)

    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", PORT), Quiet)
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:%d/index.html" % PORT
print("=== BAN GOP: %s (%.0f KB) ===" % (SRC, len(body) / 1024))

from playwright.sync_api import sync_playwright  # noqa: E402

try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900},
                             locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
        pg = ctx.new_page()
        reqs, perr, cerr, failed = [], [], [], []
        pg.on("request", lambda r: reqs.append(r.url))
        pg.on("requestfailed", lambda r: failed.append(r.url))
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.on("console", lambda m: cerr.append(m.text)
              if m.type == "error" else None)

        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1200)

        # ── [1] Tự chứa: 0 lời gọi ra ngoài ─────────────────────────
        out = [u for u in reqs
               if not u.startswith("data:") and not u.startswith(URL)
               and "favicon" not in u]
        chk(not out, "0 request ra ngoai (ngoai trang va data:)",
            str(out[:3]) if out else "%d request, tat ca data:/trang" % len(reqs))
        chk(not failed, "0 asset tai hong", str(failed[:3]))
        chk(not perr, "0 loi trang", str(perr[:2]))
        chk(not cerr, "0 loi console", str(cerr[:2]))

        # ── [2] Phông ĐÃ nhúng và ĐÃ dùng thật ──────────────────────
        fam = pg.evaluate(
            "() => getComputedStyle(document.querySelector('.top .tag')"
            " || document.body).fontFamily")
        chk("Grotesk" in fam or "Mono" in fam,
            "phong cua du an co hieu luc (khong roi ve phong he thong)", fam[:60])
        nfaces = pg.evaluate("() => document.fonts.size")
        chk(nfaces >= 5, "khai du @font-face", str(nfaces))

        # ── [3] Ví nạp sẵn ──────────────────────────────────────────
        bal = pg.inner_text("#bal")
        chk(bal.strip() == "240", "vi nap san 240 tt", bal)

        # ── [4] Chơi được thật ──────────────────────────────────────
        chk(pg.is_visible("#start-btn"), "man brief hien ra")
        pg.click("#start-btn")
        pg.wait_for_timeout(900)
        st = pg.evaluate("() => window.__racer && window.__racer.state")
        chk(st == "play", "vao duoc luot choi", str(st))
        chk(int(pg.inner_text("#bal")) == 236, "tru dung 4 tt",
            pg.inner_text("#bal"))
        # Tên tàu: bản gộp không có `astroq-user` nên phải ra tên mặc định.
        chk(pg.evaluate("() => window.__racer.shipLabel") == "Luna",
            "ten tau mac dinh hien 'Luna'",
            str(pg.evaluate("() => window.__racer.shipLabel")))
        rv = pg.evaluate("() => window.__racer.rivals")
        chk(len(rv) == 3, "co 3 doi thu cung dua", str(len(rv)))
        chk("/4" in pg.inner_text("#hb-place"), "chip Hang hien n/4",
            pg.inner_text("#hb-place"))
        d0 = pg.evaluate("() => window.__racer.dist")
        pg.wait_for_timeout(700)
        chk(pg.evaluate("() => window.__racer.dist") > d0, "tau chay that")

        # Skill tăng tốc: nạp đầy rồi bấm
        pg.evaluate("() => window.__racer.fillBoost()")
        pg.wait_for_timeout(120)
        chk(pg.get_attribute("#btn-boost", "disabled") is None,
            "nap day thi nut tang toc bam duoc")
        pg.click("#btn-boost")
        pg.wait_for_timeout(150)
        chk(pg.evaluate("() => window.__racer.boosting") is True,
            "bam thi DANG tang toc")

        # Linh vật: ảnh phải là data URI (không phải 404)
        pg.evaluate("() => window.AstroQGameShell.mate('cheer')")
        pg.wait_for_timeout(200)
        mate = pg.evaluate(
            "() => { var i = document.querySelector('.gs-mate img,"
            " .mate-mini img'); return i ? [i.currentSrc.slice(0,5),"
            " i.naturalWidth] : null; }")
        chk(mate and mate[0] == "data:" and mate[1] > 0,
            "anh linh vat la data URI va giai ma duoc", str(mate))

        # ── [5] Nút đi sang trang khác bị chặn và NÓI RA ─────────────
        # ⚠️ BẤM VÀO NÚT ĐANG NHÌN THẤY ĐƯỢC. Lượt đầu tôi bấm `#hub-btn` với
        #   `force=True` — nút đó nằm trong lớp phủ KẾT QUẢ nên lúc đang chơi nó
        #   đang ẩn; cú bấm rơi vào chỗ khác, không handler nào chạy, và toast còn
        #   giữ câu "⚡ Tăng tốc!" của phép đo trước → báo hỏng oan. `#back` ở
        #   header thì lúc nào cũng hiện.
        before = pg.url
        pg.evaluate("() => { var t=document.getElementById('toast');"
                    " if(t){ t.textContent=''; t.className='toast'; } }")
        pg.click("#back")
        pg.wait_for_timeout(400)
        chk(pg.url == before, "bam nut dieu huong KHONG roi trang", pg.url[-24:])
        tx = pg.inner_text("#toast")
        # ⚠️ Khớp cụm CÓ DẤU. Bản đầu tìm chuỗi không dấu "thu" trong khi câu là
        #   "Bản thử …" → báo hỏng oan; đúng bài học quy tắc 8 mục 6.
        chk("bản thử" in tx.casefold(), "co noi RA ly do (khong im lang)", tx[:70])

        # ── [6] Dải nhãn BẢN THỬ ────────────────────────────────────
        note = pg.query_selector(".tb-note")
        chk(note is not None and note.is_visible(), "dai nhan BAN THU hien ra")
        ntx = pg.inner_text(".tb-note") if note else ""
        chk("không phải" in ntx or "khong phai" in ntx.casefold(),
            "dai nhan noi ro day KHONG phai ban that", ntx[:70])
        bb = note.bounding_box() if note else None
        pb = pg.evaluate("() => { var f = document.querySelector('.field');"
                         " if(!f) return null; var r = f.getBoundingClientRect();"
                         " return {x:r.x,y:r.y,w:r.width,h:r.height}; }")
        if bb and pb:
            ov = (max(0, min(bb["x"] + bb["width"], pb["x"] + pb["w"])
                      - max(bb["x"], pb["x"]))
                  * max(0, min(bb["y"] + bb["height"], pb["y"] + pb["h"])
                        - max(bb["y"], pb["y"])))
            chk(ov == 0, "dai nhan KHONG de len san choi", "%.0f px2" % ov)
        chk(pg.evaluate("() => getComputedStyle(document.querySelector"
                        "('.tb-note')).pointerEvents") == "none",
            "dai nhan khong nuot cu bam")

        # ── [7] Không tràn ngang + điện thoại 390×844 ───────────────
        chk(pg.evaluate("() => document.documentElement.scrollWidth <= "
                        "window.innerWidth + 1"), "desktop khong tran ngang")
        pg.screenshot(path=os.path.join(tmp, "desktop.png"))

        ctx2 = br.new_context(viewport={"width": 390, "height": 844},
                              locale="vi-VN", has_touch=True, is_mobile=True)
        pg2 = ctx2.new_page()
        p2err = []
        pg2.on("pageerror", lambda e: p2err.append(str(e)))
        pg2.goto(URL, wait_until="load")
        pg2.wait_for_timeout(1000)
        chk(pg2.evaluate("() => document.documentElement.scrollWidth <= "
                         "window.innerWidth + 1"), "390px khong tran ngang")
        chk(not p2err, "390px 0 loi trang", str(p2err[:1]))
        pg2.screenshot(path=os.path.join(tmp, "mobile.png"))
        print("\n  anh chup: %s" % tmp)
        ctx2.close()
        ctx.close()
        br.close()
finally:
    srv.shutdown()

print("\n" + "=" * 56)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
