# -*- coding: utf-8 -*-
"""
smoke_map_onboard.py — ĐO TRÊN TRANG: nhịp phim Comet dẫn đường ở Bản Đồ Thiên Hà
(bước ①–④ của `docs/decisions/003` · `js/map-onboard.js`).

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    set PYTHONIOENCODING=utf-8
    python scratchpad/smoke_map_onboard.py

Bộ này canh đúng những thứ ĐỌC CODE KHÔNG THẤY ĐƯỢC:
  · màn warp có in ĐÚNG ba dòng trong ảnh chủ dự án gửi — đặc biệt là
    **"ĐANG DU HÀNH TỚI"**, không phải "Đang tới" (`travelTo` sẽ chọn sai nhánh vì
    lúc trang vừa nạp `currentRegion` đã là solar-system);
  · vệt sao có THẬT SỰ chạy hay chỉ là một lớp phủ đen (đếm pixel sáng);
  · box thoại Comet có nằm ở ĐÁY và **không đè lên bảng thông tin hành tinh**;
  · cỡ chữ có đạt mức chủ dự án yêu cầu ("chữ to, rõ ràng, dễ đọc");
  · **10 giây là SÀN, không phải hạn**: câu hỏi hiện ra mà bảng thông tin VẪN MỞ, và
    đồng hồ chỉ chạy SAU khi bảng mở (không đếm trong lúc camera còn đang bay);
  · nhãn Trái Đất được tô sáng + có chữ "Bắt đầu từ đây", nhãn hành tinh khoá bị làm mờ
    **mà KHÔNG dùng `filter:grayscale()`**;
  · bấm OK thì đi tới `mission-earth.html`.

⚠️ Rút `READ_MS` xuống bằng `AstroQMapOnboard._setReadMs()` cho bộ test chạy nhanh,
   NHƯNG có một phép kiểm riêng đọc `READ_MS` mặc định để chắc sản phẩm thật vẫn là
   10 giây — rút mốc chờ mà quên kiểm giá trị thật là cách để một bộ test xanh trong
   khi sản phẩm sai.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
CACHE = {"route": ["earth", "moon"], "open": ["earth"],
         "gate": 6, "done": 2, "total": 8}

ok = fail = 0
FAILS = []


def chk(cond, name, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  [ok]   {name}" + (f"  {extra}" if extra else ""))
    else:
        fail += 1
        FAILS.append(name)
        print(f"  [FAIL] {name}" + (f"  {extra}" if extra else ""))


def head(t):
    print(f"\n=== {t} ===")


def newpage(ctx, lang="vi", read_ms=900):
    errs = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.add_init_script(
        "localStorage.setItem('astroq-lang', %s);"
        "localStorage.setItem('astroq-route-gate', %s);"
        % (json.dumps(lang), json.dumps(json.dumps(CACHE)))
    )
    # Rút mốc chờ NGAY khi module vừa nạp, trước lúc nhịp phim tới bước đọc.
    pg.add_init_script(
        "Object.defineProperty(window,'__readMs',{value:%d});"
        "addEventListener('DOMContentLoaded',function(){"
        "  if(window.AstroQMapOnboard) AstroQMapOnboard._setReadMs(%d);"
        "});" % (read_ms, read_ms)
    )
    return pg, errs


def diag(pg):
    """Ảnh chụp trạng thái để phép chờ hết hạn KHÔNG chỉ nói "có cái gì đó treo".

    ⚠️ Quy tắc 6 mục 6 của CLAUDE.md. Lượt chạy đầu của bộ này hết hạn ở phép chờ màn
       warp và chỉ in ra một `TimeoutError` trần — phải mở trang bằng tay mới biết
       sản phẩm CHẠY ĐÚNG, chỉ là phép chờ thua cuộc đua.
    """
    try:
        return pg.evaluate("""() => ({
          gate: window.AstroQGate ? AstroQGate.active() : null,
          onboard: window.AstroQMapOnboard ? AstroQMapOnboard._state() : null,
          warp: document.getElementById('nm-warp').classList.contains('show'),
          say: document.getElementById('mo-say').classList.contains('show'),
          info: document.getElementById('info').classList.contains('open'),
          ready: window.__solarReady === true
        })""")
    except Exception as e:
        return {"_err": str(e)[:90]}


def wait_js(pg, expr, label, timeout=20000):
    """`wait_for_function` CÓ tự khai trạng thái. Trả True/False, không ném ra ngoài."""
    try:
        pg.wait_for_function(expr, timeout=timeout)
        return True
    except Exception:
        chk(False, label + " (het han cho)", str(diag(pg)))
        return False


def open_map(pg):
    """Mở bản đồ ở chế độ onboarding.

    ⚠️ GIỮ `window.__solarReady` LẠI TRƯỚC KHI VÀO. Màn warp chỉ sống ~1,8s rồi tự nhả
       khi cảnh 3D dựng xong, mà `goto()` + khởi động trang tốn xấp xỉ đúng khoảng đó —
       nên phép chờ của test bắt đầu SAU khi warp đã tắt, rồi chờ mãi một thứ đã xảy ra
       xong. Lượt chạy đầu tôi tưởng sản phẩm hỏng; mở trang bằng tay mới thấy nó chạy
       đúng và trạng thái đã sang `intro`. Đây là lỗi ĐO.
       Giữ cảnh lại cho tới khi đo xong màn warp, rồi `release()` để nhả.
    """
    pg.add_init_script("""
      (function () {
        var v = false;
        Object.defineProperty(window, '__solarReady', {
          configurable: true,
          get: function () { return window.__testHold ? false : v; },
          set: function (x) { v = x; }
        });
        window.__testHold = true;
      })();
    """)
    pg.goto(BASE + "/explorer.html?onboard=1", wait_until="domcontentloaded")


def release(pg):
    """Nhả cảnh 3D ra để màn warp tắt và nhịp phim đi tiếp."""
    pg.evaluate("() => { window.__testHold = false; }")


def wait_typed(pg, label):
    """Chờ Comet gõ XONG câu đang nói.

    ⚠️ ĐỪNG NGỦ MỘT KHOẢNG CỐ ĐỊNH. Câu dài ~70 ký tự × 22ms ≈ 1,5s, mà lượt chạy
       trước tôi ngủ 1,4s rồi đọc — ra "Đây là Hệ Mặt T" và **6 phép kiểm báo hỏng
       oan**. Tín hiệu THẬT là thẻ `<b>` được dựng lại, việc chỉ xảy ra ở dòng cuối
       của `say()` trong `js/map-onboard.js`.
    """
    return wait_js(pg, "() => document.getElementById('mo-line')"
                       ".innerHTML.indexOf('<b>') >= 0", label)


def wait_btn(pg, label):
    """Chờ nút hiện ra — nút chỉ hiện SAU khi gõ xong, nên cũng là tín hiệu "nói xong"."""
    return wait_js(pg, "() => !document.getElementById('mo-next')"
                       ".classList.contains('hide')", label)


def say(pg):
    return pg.evaluate("""() => {
      const s = document.getElementById('mo-say');
      const l = document.getElementById('mo-line');
      const b = document.getElementById('mo-next');
      const r = s.getBoundingClientRect();
      return {
        shown: s.classList.contains('show'),
        text: (l.textContent || '').trim(),
        html: l.innerHTML,
        btn: b.classList.contains('hide') ? null : (b.textContent || '').trim(),
        rect: {t: Math.round(r.top), b: Math.round(r.bottom),
               l: Math.round(r.left), r: Math.round(r.right)},
        fontPx: parseFloat(getComputedStyle(l).fontSize),
        state: window.AstroQMapOnboard ? AstroQMapOnboard._state() : '?'
      };
    }""")


def warp_state(pg):
    return pg.evaluate("""() => {
      const w = document.getElementById('nm-warp');
      return {
        shown: w.classList.contains('show'),
        k: document.getElementById('nm-warp-k').textContent.trim(),
        n: document.getElementById('nm-warp-n').textContent.trim(),
        sub: document.getElementById('nm-warp-sub').textContent.trim()
      };
    }""")


def warp_pixels(pg):
    """Đếm pixel sáng trên canvas warp — chứng minh vệt sao CHẠY THẬT.

    ⚠️ Đọc pixel NGAY TRONG TRANG. `page.screenshot()` mất ~200ms, mà mỗi vệt sao
       chỉ sống vài khung — chụp rồi đọc là đo một thứ đã thay đổi. Cùng bài học đã
       ghi ở `verify_flame2.py` và `smoke_mission_earth.py`.
    """
    return pg.evaluate("""() => {
      const cv = document.getElementById('nm-warp-cv');
      if (!cv || !cv.width) return -1;
      const g = cv.getContext('2d');
      const d = g.getImageData(0, 0, cv.width, cv.height).data;
      let n = 0;
      for (let i = 0; i < d.length; i += 4) {
        if (d[i] > 120 && d[i+1] > 140 && d[i+2] > 160) n++;
      }
      return n;
    }""")


def labels(pg):
    return pg.evaluate("""() => {
      const out = {};
      document.querySelectorAll('#labels [data-body-id]').forEach(el => {
        const cs = getComputedStyle(el);
        const hint = el.querySelector('.gate-hint');
        out[el.dataset.bodyId] = {
          start: el.classList.contains('gate-start'),
          locked: el.classList.contains('gate-locked'),
          hint: hint ? hint.textContent.trim() : null,
          opacity: parseFloat(cs.opacity),
          filter: cs.filter,
          shadow: cs.boxShadow
        };
      });
      return out;
    }""")


def click_earth(pg):
    """Mở Trái Đất qua danh sách bảng trái — đường ổn định, không phụ thuộc quỹ đạo."""
    n = pg.evaluate("""() => {
      let b = document.querySelector('.loc-item[data-id="earth"]');
      if (!b) {
        const h = document.querySelector('.reg-group.current .reg-head');
        if (h) h.click();
        b = document.querySelector('.loc-item[data-id="earth"]');
      }
      if (!b) return 0;
      b.click();
      return 1;
    }""")
    pg.wait_for_timeout(500)
    return n == 1


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900})

        # ─────────────────────────────────────────────────────────────
        head("[1] ① Man warp lúc vào trang — ĐUNG ba dòng trong anh yeu cau")
        pg, errs = newpage(ctx)
        open_map(pg)
        wait_js(pg, "() => document.getElementById('nm-warp')"
                    ".classList.contains('show')", "man warp hien ra")
        w = warp_state(pg)
        chk(w["shown"], "man warp hien NGAY luc vao trang")
        # ⚠️ Phép kiểm quan trọng nhất của mục này.
        chk(w["k"] == "Đang du hành tới",
            "dong dau la 'Dang du hanh toi' (KHONG phai 'Dang toi')", w["k"])
        chk(w["n"] == "Hệ Mặt Trời", "ten vung la 'He Mat Troi'", w["n"])
        chk(w["sub"] == "Đang tiến vào vùng", "dong duoi la 'Dang tien vao vung'",
            w["sub"])
        px = warp_pixels(pg)
        chk(px > 400, "vet sao CHAY THAT (dem pixel sang tren canvas)", f"{px} px")
        chk(pg.evaluate("() => getComputedStyle(document.getElementById"
                        "('nm-warp-k')).textTransform") == "uppercase",
            "chu in hoa do CSS lo, khong phai go hoa tay")

        # Warp phải tự nhả ra khi cảnh dựng xong
        chk(pg.evaluate("() => window.__solarReady === false"),
            "dang GIU canh 3D lai nen warp con song (xem open_map)")
        release(pg)
        chk(wait_js(pg, "() => !document.getElementById('nm-warp')"
                        ".classList.contains('show')",
                    "man warp tu nha ra sau khi canh 3D dung xong"),
            "man warp tu nha ra sau khi canh 3D dung xong")
        chk(pg.evaluate("() => window.__solarReady === true"),
            "canh 3D that su da dung xong truoc khi nha")
        chk(not errs, "0 loi console", str(errs[:3]))

        # ─────────────────────────────────────────────────────────────
        head("[2] ③ Comet gioi thieu o DAY man hinh")
        wait_js(pg, "() => document.getElementById('mo-say')"
                    ".classList.contains('show')", "box thoai Comet hien ra")
        wait_typed(pg, "Comet go xong cau 1")
        wait_btn(pg, "nut hien ra sau khi go xong")
        s = say(pg)
        chk(s["shown"], "box thoai hien")
        chk("Hệ Mặt Trời" in s["text"], "cau 1 noi ve He Mat Troi", s["text"][:60])
        chk("khám phá" in s["text"], "cau 1 co 'nhieu thu de kham pha'",
            s["text"][:60])
        vh = pg.evaluate("() => innerHeight")
        chk(s["rect"]["b"] > vh * 0.7,
            "box neo o DAY man hinh (dung yeu cau 'goc duoi')",
            f"bottom={s['rect']['b']} / {vh}")
        # "chữ to, rõ ràng, dễ đọc" — to hơn hai màn thoại kia (14 / 14,5px)
        chk(s["fontPx"] >= 16.5, "co chu >= 16,5px (to hon mission-intro 14,5px)",
            f"{s['fontPx']}px")
        chk(s["btn"] and "Tiếp tục" in s["btn"], "co nut 'Tiep tuc'", str(s["btn"]))

        pg.evaluate("() => document.getElementById('mo-next').click()")
        wait_js(pg, "() => AstroQMapOnboard._state() === 'waitEarth'",
                "Comet noi xong cau 2 -> cho tre bam Trai Dat")
        s = say(pg)
        chk("Trái Đất" in s["text"], "cau 2 bao bat dau tu Trai Dat", s["text"][:70])
        chk("xanh" in s["text"], "cau 2 goi Trai Dat la 'hanh tinh xanh'",
            s["text"][:70])
        chk("<b>" in s["html"], "the <b> duoc dung lai sau khi go xong (khong lo '<b')",
            s["html"][:60])
        chk(s["btn"] is None, "an nut sau cau 2 — gio den luot TRE bam Trai Dat",
            str(s["btn"]))
        chk(s["state"] == "waitEarth", "trang thai = cho tre bam Trai Dat", s["state"])
        chk(not errs, "0 loi console", str(errs[:3]))

        # ─────────────────────────────────────────────────────────────
        head("[3] ② Nhan Trai Dat duoc to sang, hanh tinh khoa bi lam mo")
        lb = labels(pg)
        e = lb.get("earth") or {}
        chk(e.get("start") is True, "nhan Trai Dat co class gate-start", str(e))
        chk(e.get("hint") == "Bắt đầu từ đây",
            "co chu 'Bat dau tu day' duoi nhan", str(e.get("hint")))
        chk("rgb" in (e.get("shadow") or ""),
            "nhan Trai Dat co vong sang (con lai khi tat animation)",
            str(e.get("shadow"))[:50])
        others = {k: v for k, v in lb.items() if k not in ("earth",)}
        locked = [k for k, v in others.items() if v["locked"]]
        chk(len(locked) >= 3, "nhan hanh tinh khoa bi lam mo", f"{len(locked)}: {locked}")
        chk(all(others[k]["opacity"] < 0.6 for k in locked),
            "do mo that su duoi 0,6", str({k: others[k]["opacity"] for k in locked}))
        # ⚠️ Bài học đã ghi 3 lần trong dự án.
        chk(all(others[k]["filter"] in ("none", "") for k in locked),
            "KHONG dung filter:grayscale() de lam mo",
            str({k: others[k]["filter"] for k in locked}))
        chk(not lb.get("mars", {}).get("start"),
            "chi Trai Dat duoc to sang, khong to bua hanh tinh khac")

        # ─────────────────────────────────────────────────────────────
        head("[4] ④ Bam Trai Dat -> bang thong tin -> SAN 10s -> Comet hoi")
        chk(click_earth(pg), "bam duoc vao Trai Dat")
        wait_js(pg, "() => document.getElementById('info')"
                    ".classList.contains('open')", "bang thong tin mo ra")
        chk(True, "bang thong tin MO ra de doc")
        st = pg.evaluate("() => AstroQMapOnboard._state()")
        chk(st == "reading", "dong ho SAN bat dau dem SAU khi bang mo", st)
        chk(not say(pg)["shown"],
            "box thoai TAM AN de nhuong cho tre doc bang thong tin")

        wait_js(pg, "() => AstroQMapOnboard._state() === 'ask'",
                "Comet chuyen sang cau hoi")
        wait_typed(pg, "Comet go xong cau hoi")
        wait_btn(pg, "nut OK hien ra")
        s = say(pg)
        chk(s["shown"], "Comet hien lai de hoi")
        chk("sẵn sàng" in s["text"] and "nhiệm vụ đầu tiên" in s["text"],
            "cau hoi dung y: 'san sang bat dau nhiem vu dau tien'", s["text"][:80])
        # ⚠️ 10 GIÂY LÀ SÀN, KHÔNG PHẢI HẠN — bảng thông tin PHẢI còn mở.
        chk(pg.evaluate("() => document.getElementById('info')"
                        ".classList.contains('open')"),
            "bang thong tin VAN MO khi Comet hoi (10s la SAN, khong phai han)")
        chk(s["btn"] and "OK" in s["btn"], "co nut OK", str(s["btn"]))
        # Box thoại ở đáy, bảng thông tin ở mép phải — không được đè nhau
        ov = pg.evaluate("""() => {
          const a = document.getElementById('mo-say').getBoundingClientRect();
          const b = document.getElementById('info').getBoundingClientRect();
          const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
          const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
          return (w > 0 && h > 0) ? Math.round(w * h) : 0;
        }""")
        chk(ov == 0, "box thoai KHONG de len bang thong tin", f"{ov}px²")
        chk(not errs, "0 loi console", str(errs[:3]))

        # Mốc thật của sản phẩm phải là 10 giây, không phải mốc test rút ngắn
        chk(pg.evaluate("() => AstroQMapOnboard.READ_MS") == 10000,
            "san doc mac dinh cua SAN PHAM la 10 giay",
            str(pg.evaluate("() => AstroQMapOnboard.READ_MS")))

        head("[5] Bam OK -> vao nhiem vu Trai Dat")
        pg.evaluate("() => document.getElementById('mo-next').click()")
        pg.wait_for_load_state("domcontentloaded")
        pg.wait_for_timeout(800)
        chk("mission-earth.html" in pg.url, "sang trang nhiem vu",
            pg.url.split("/")[-1])
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[6] Vao ban do BINH THUONG (khong ?onboard=1) -> khong co gi doi")
        pg, errs = newpage(ctx)
        pg.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
        wait_js(pg, "() => window.__solarReady === true", "canh 3D dung xong")
        pg.wait_for_timeout(1500)
        chk(not warp_state(pg)["shown"], "KHONG chay man warp")
        chk(not say(pg)["shown"], "KHONG hien box thoai Comet")
        lb = labels(pg)
        chk(not any(v["start"] or v["locked"] for v in lb.values()),
            "khong to/lam mo nhan nao", str({k: v["start"] for k, v in lb.items()}))
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[7] Ban tieng Anh")
        pg, errs = newpage(ctx, "en")
        open_map(pg)
        wait_js(pg, "() => document.getElementById('nm-warp')"
                    ".classList.contains('show')", "man warp EN hien ra")
        w = warp_state(pg)
        chk(w["k"] == "Traveling to", "man warp dich sang EN", w["k"])
        chk(w["n"] == "Solar System", "ten vung dich sang EN", w["n"])
        release(pg)
        wait_js(pg, "() => document.getElementById('mo-say')"
                    ".classList.contains('show')", "box thoai EN hien ra")
        wait_typed(pg, "Comet go xong cau 1 (EN)")
        wait_btn(pg, "nut EN hien ra")
        s = say(pg)
        chk("Solar System" in s["text"], "loi Comet dich sang EN", s["text"][:60])
        chk(s["btn"] and "Next" in s["btn"], "nut dich sang EN", str(s["btn"]))
        lb = labels(pg)
        chk((lb.get("earth") or {}).get("hint") == "Start here",
            "chu chi duong dich sang EN", str((lb.get("earth") or {}).get("hint")))
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[8] Dien thoai 390x844")
        m = br.new_context(viewport={"width": 390, "height": 844},
                           is_mobile=True, has_touch=True)
        pg, errs = newpage(m)
        open_map(pg)
        release(pg)
        wait_js(pg, "() => document.getElementById('mo-say')"
                    ".classList.contains('show')", "box thoai dien thoai hien ra")
        wait_typed(pg, "Comet go xong cau 1 (dien thoai)")
        s = say(pg)
        chk(s["rect"]["l"] >= 0 and s["rect"]["r"] <= 390,
            "box thoai khong chia ra ngoai man hinh", str(s["rect"]))
        chk(s["fontPx"] >= 15, "chu tren dien thoai van >= 15px", f"{s['fontPx']}px")
        chk(pg.evaluate("() => document.documentElement.scrollWidth <= innerWidth"),
            "trang khong tran ngang")
        btn = pg.evaluate("""() => {
          const b = document.getElementById('mo-next');
          const r = b.getBoundingClientRect();
          return {w: Math.round(r.width), h: Math.round(r.height)};
        }""")
        chk(btn["h"] >= 44, "vung cham nut >= 44px (WCAG 2.5.5)", str(btn))

        # ⚠️ CÁI BẪY: trên điện thoại `#info` neo ĐÁY và cao 74vh — đúng chỗ box thoại.
        #    Bản đầu tôi ẩn box đi ở ca này, tức là câu hỏi "sẵn sàng chưa?" và nút OK
        #    biến mất và TRẺ KẸT CỨNG. Phép kiểm này canh đúng chuyện đó.
        # Phải cho Comet nói hết đã — nhịp phim chỉ chuyển sang `waitEarth` sau câu 2.
        # (Lượt trước tôi bấm Trái Đất ngay nên trạng thái đứng ở `intro` và phép chờ
        #  hết hạn — lỗi thứ tự trong test, không phải lỗi sản phẩm.)
        wait_btn(pg, "dien thoai: nut 'Tiep tuc' hien ra")
        pg.evaluate("() => document.getElementById('mo-next').click()")
        wait_js(pg, "() => AstroQMapOnboard._state() === 'waitEarth'",
                "dien thoai: Comet noi xong cau 2")
        chk(click_earth(pg), "dien thoai: bam duoc Trai Dat")
        wait_js(pg, "() => document.getElementById('info').classList.contains('open')",
                "dien thoai: bang thong tin mo ra")
        wait_js(pg, "() => AstroQMapOnboard._state() === 'ask'",
                "dien thoai: Comet chuyen sang cau hoi")
        wait_btn(pg, "dien thoai: nut OK hien ra")
        m2 = pg.evaluate("""() => {
          const s = document.getElementById('mo-say');
          const b = document.getElementById('mo-next');
          const rs = s.getBoundingClientRect(), rb = b.getBoundingClientRect();
          const cs = getComputedStyle(s);
          const mid = document.elementFromPoint(
            Math.round(rb.left + rb.width / 2), Math.round(rb.top + rb.height / 2));
          return {
            vis: cs.visibility, op: parseFloat(cs.opacity),
            inView: rs.top >= 0 && rs.bottom <= innerHeight,
            hitsBtn: !!(mid && (mid.id === 'mo-next' || mid.closest('#mo-next'))),
            top: Math.round(rs.top), bottom: Math.round(rs.bottom)
          };
        }""")
        chk(m2["vis"] == "visible" and m2["op"] > 0.9,
            "dien thoai: box thoai VAN HIEN khi bang thong tin mo", str(m2))
        chk(m2["inView"], "dien thoai: box nam TRON trong khung nhin", str(m2))
        # elementFromPoint là phép đo THẬT "bấm được", không phải "có CSS".
        chk(m2["hitsBtn"], "dien thoai: nut OK that su bam duoc (khong bi bang de len)",
            str(m2))
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()
        m.close()

        # ─────────────────────────────────────────────────────────────
        head("[9] Giam chuyen dong (prefers-reduced-motion)")
        r = br.new_context(viewport={"width": 1440, "height": 900},
                           reduced_motion="reduce")
        pg, errs = newpage(r)
        open_map(pg)
        release(pg)
        wait_js(pg, "() => document.getElementById('mo-say')"
                    ".classList.contains('show')", "box thoai reduced-motion hien ra")
        s = say(pg)
        chk("Hệ Mặt Trời" in s["text"],
            "giam chuyen dong: hien DU chu ngay, khong go tung ky tu", s["text"][:50])
        lb = labels(pg)
        e = lb.get("earth") or {}
        # ⚠️ Tắt animation nhưng PHẢI còn thứ chỉ đường.
        chk("rgb" in (e.get("shadow") or ""),
            "tat animation nhung VAN con vong sang chi duong",
            str(e.get("shadow"))[:50])
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()
        r.close()

        ctx.close()
        br.close()

    print(f"\n=== KET QUA: {ok} dat / {fail} hong ===")
    if FAILS:
        print("Hong:")
        for f in FAILS:
            print("  - " + f)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
