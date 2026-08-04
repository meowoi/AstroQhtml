# -*- coding: utf-8 -*-
"""Màn warp có THẬT SỰ còn chạy trong lúc main thread bị chặn không?

`longtask` chỉ đo main thread, mà main thread thì luôn bị three.js chặn — nó không
trả lời được câu hỏi. Nên ở đây đo bằng `Page.startScreencast`: khung hình do
COMPOSITOR đẩy ra, tức thứ trẻ thật sự nhìn thấy. Đếm số khung KHÁC NHAU đến trong
lúc màn warp đang hiện.

A/B trên CÙNG một mã nguồn:
  · worker BẬT   — như bản thật
  · worker CHẶN  — `route` cho `warp-stars-worker.js` fail → `onerror` lùi về bản vẽ
                   main thread (đúng mã của bản 31/07/2026)
"""
import hashlib
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8123"


def run(block_worker):
    frames = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": 900, "height": 600})
        pg = ctx.new_page()
        pg.add_init_script("try{localStorage.removeItem('astroq-map01-seen');}catch(e){}")
        if block_worker:
            pg.route("**/warp-stars-worker.js", lambda r: r.abort())
        cdp = ctx.new_cdp_session(pg)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})

        def on_frame(ev):
            frames.append((ev["metadata"]["timestamp"],
                           hashlib.md5(ev["data"].encode()).hexdigest()))
            try:
                cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
            except Exception:
                pass

        cdp.on("Page.screencastFrame", on_frame)
        cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 40,
                                          "maxWidth": 450, "maxHeight": 300,
                                          "everyNthFrame": 1})
        pg.goto(f"{BASE}/explorer.html?onboard=1", wait_until="commit")
        try:
            pg.wait_for_function(
                "document.getElementById('nm-warp') && "
                "!document.getElementById('nm-warp').classList.contains('show') && "
                "window.__solarReady===true", timeout=30000)
        except Exception:
            pass
        pg.wait_for_timeout(300)
        try:
            cdp.send("Page.stopScreencast")
        except Exception:
            pass
        br.close()

    if not frames:
        print("  không nhận được khung nào")
        return
    t0 = frames[0][0]
    uniq, last = 0, None
    for _, h in frames:
        if h != last:
            uniq += 1
            last = h
    span = frames[-1][0] - t0
    # khoảng cách dài nhất giữa hai khung KHÁC NHAU = quãng hình đứng cứng lâu nhất
    prev_t, prev_h, worst, gaps = t0, None, 0.0, []
    for t, h in frames:
        if h != prev_h:
            if prev_h is not None:
                gaps.append(t - prev_t)
                worst = max(worst, t - prev_t)
            prev_t, prev_h = t, h
    label = "worker CHẶN (bản main thread cũ)" if block_worker else "worker BẬT (bản mới)"
    print(f"[{label}]")
    print(f"  {len(frames)} khung compositor · {uniq} khung KHÁC NHAU trong {span:.2f}s")
    print(f"  → {uniq/max(span,0.01):.1f} khung mới / giây")
    print(f"  quãng HÌNH ĐỨNG CỨNG dài nhất: {worst*1000:.0f} ms")
    if gaps:
        gaps.sort(reverse=True)
        print(f"  5 quãng đứng dài nhất (ms): {[round(g*1000) for g in gaps[:5]]}")


run(False)
print()
run(True)
