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

⛔ `READ_MS` / `_setReadMs()` / state `reading` ĐÃ BỎ HẲN khỏi `js/map-onboard.js`
   (02/08/2026) — đừng dựng lại trong bộ test. Mốc SÀN 15 giây trước khi Comet hỏi đã
   bị bỏ vì chủ dự án chơi thật và bác: *"sau khi trẻ ngắm trái đất, ấn nút tiếp tục sẽ
   phải chuyển sang ngay phần tiếp, ko chờ"* — một cái nút ghi "Tiếp tục" mà bấm vào
   không tiếp tục thì nó là một cái nút nói dối.
   ⚠️ Ba phép kiểm ở đây từng BẢO VỆ đúng mốc chờ đó (kể cả một phép kiểm đòi
      `READ_MS === 15000`), nên sửa sản phẩm cho đúng là chúng báo hỏng — cùng loại việc
      đã làm với nút Mặt Trăng. Đã đảo chiều: nay đòi **không còn mốc chờ nào**.

⚠️⚠️ CHROME HÃM `setInterval` Ở TRANG KHÔNG HIỆN — ĐO ĐƯỢC ~124ms/ký tự thay vì 22ms
   (chậm 5,6 lần). Ban đầu tưởng chỉ xảy ra khi chạy SONG SONG với một bộ Playwright khác,
   nhưng 02/08/2026 đo lại: nó xảy ra **cả khi chạy một mình**, vì bộ này mở nhiều context
   và trong headless thì trang không phải trang đang hiện đều bị coi là ẩn. Vì thế
   `wait_typed` để mốc **90 giây** — xem bảng số đo trong docstring của nó. Thấy đúng mấy
   phép kiểm GÕ CHỮ đỏ mà mọi thứ khác xanh thì đó là mốc chờ, ĐỪNG đi sửa `js/map-onboard.js`.
   (Ghi chú cũ, giữ để đối chiếu: chạy cùng `smoke_mission_earth.py` thì hai phép kiểm nhịp
   0 báo hết hạn chờ, chạy một mình thì 68/68.) Nguyên nhân là hành vi của trình duyệt chứ không phải
   của sản phẩm: `say()` gõ từng chữ bằng `setInterval(…, 22)`, mà Chrome **hãm đồng hồ
   ở tab không có focus** xuống ~1 lần/giây — một câu 140 ký tự vì thế mất tới 140 giây,
   vượt xa mốc chờ 20 giây của `wait_js`. Thấy đúng hai phép kiểm gõ chữ đỏ mà mọi thứ
   khác xanh thì kiểm xem có bộ nào đang chạy cùng, ĐỪNG đi sửa `js/map-onboard.js`.
"""
import io
import json
import sys

from PIL import Image
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
    # ⛔ KHÔNG CÒN GÌ ĐỂ RÚT. `_setReadMs()` đã bị bỏ khỏi sản phẩm cùng lúc với mốc
    #    chờ; gọi nó là `TypeError` trong init script — mà lỗi ở init script thì im lặng
    #    với `pageerror` và triệu chứng chỉ hiện ra dưới dạng "nhịp phim không tới bước
    #    kế tiếp". Tham số `read_ms` giữ lại cho tương thích chỗ gọi, không dùng nữa.
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
          ready: window.__solarReady === true,
          /* ⚠️ THEM 02/08/2026: ba phep kiem `wait_typed` het han cho ma cau ngay sau
             lai DOC RA du chu — tuc go xong that, chi la `<b>` khong duoc dung lai.
             Khong co ba truong nay thi khong the phan biet "chua go xong" voi
             "go xong roi ma dau hieu bao xong khong bao gio den". */
          lineLen: (document.getElementById('mo-line').textContent || '').length,
          lineCoB: document.getElementById('mo-line').innerHTML.indexOf('<b>') >= 0,
          lineHtml: document.getElementById('mo-line').innerHTML.slice(0, 90)
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

    ⚠️⚠️ MỐC CHỜ 90 GIÂY, KHÔNG PHẢI 20 — VÀ ĐÂY LÀ CON SỐ ĐO ĐƯỢC, KHÔNG PHẢI NỚI
       LỎNG CHO QUA. Ngày 02/08/2026 ba phép kiểm gõ chữ của nhịp 0 báo hết hạn chờ.
       Chẩn đoán (nhờ thêm `lineLen`/`lineCoB` vào `diag`): lúc hết hạn `lineLen = 161`
       và ĐANG TĂNG — chữ vẫn đang gõ. 161 ký tự trong 20s = **124ms/ký tự**, trong khi
       `TYPE_MS = 22`. Chrome đang hãm `setInterval` khoảng **5,6 lần**.
       Đối chiếu độ dài 4 câu (đếm từ chính `js/map-onboard.js`):
           l3   172 ký tự →  3,8s @22ms  |  21,3s @124ms   ⛔ vượt mốc 20s
           l3b  244 ký tự →  5,4s @22ms  |  30,3s @124ms   ⛔
           l4   195 ký tự →  4,3s @22ms  |  24,2s @124ms   ⛔
           ask  101 ký tự →  2,2s @22ms  |  12,5s @124ms   ✅ dưới 20s
       ⇒ **Đúng ba câu dài nhất hỏng, câu ngắn nhất đạt.** Đó là dấu vân tay của một mốc
         chờ quá chặt — một lỗi sản phẩm thì không quan tâm độ dài câu.
       ⚠️ Ghi chú đầu file nói về chuyện hãm này NHƯNG chỉ cho trường hợp chạy SONG SONG
          với một bộ Playwright khác. Thực tế nó xảy ra cả khi chạy MỘT MÌNH: bộ này mở
          nhiều context, và trong headless thì trang nào không phải trang đang hiện đều
          bị coi là ẩn. Đã dọn sạch Chromium rồi chạy lại — vẫn hỏng đúng ba câu đó.
       90s = gấp ba câu dài nhất, vẫn đủ chặt để bắt treo thật.
    """
    return wait_js(pg, "() => document.getElementById('mo-line')"
                       ".innerHTML.indexOf('<b>') >= 0", label, timeout=90000)


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


def _bright(png):
    """Số pixel sáng (tông vệt sao xanh-trắng) trong một ảnh PNG."""
    im = Image.open(io.BytesIO(png)).convert("RGB")
    n = 0
    for r, g, b in im.getdata():
        if r > 120 and g > 140 and b > 160:
            n += 1
    return n, im.tobytes()


def warp_pixels(pg):
    """Đếm pixel sáng trên canvas warp — chứng minh vệt sao CHẠY THẬT.

    ⚠️⚠️ ĐỔI CÁCH ĐO 03/08/2026 — KHÔNG PHẢI DỌN DẸP, LÀ BẮT BUỘC.
       Bản cũ đọc pixel bằng `cv.getContext('2d').getImageData(...)` ngay trong trang.
       Từ lượt sửa cái giật của màn warp, quyền vẽ canvas đó đã chuyển sang Web Worker
       (`transferControlToOffscreen`, xem `js/warp-stars-worker.js`), nên `getContext`
       trên đó **ném `InvalidStateError`** — main thread không còn đọc được nó nữa. Đó
       là đúng ý muốn, không phải hồi quy.
       Nên đo bằng ẢNH CHỤP thẻ canvas — thứ trẻ thật sự nhìn thấy, và cũng là cách
       duy nhất còn lại. Chú thích cũ lo `page.screenshot()` chậm nên "đo một thứ đã
       thay đổi": đúng nếu muốn đo MỘT vệt sao cụ thể, nhưng ở đây chỉ hỏi "có vệt sao
       nào không", mà ảnh chụp là một khung hình THẬT nên câu trả lời không sai được.
    ⚠️ Trả về cả 'có ĐỔI giữa hai lần chụp' — phép kiểm mạnh hơn bản cũ: bản cũ chỉ
       chứng minh canvas có gì đó sáng, không chứng minh nó ĐANG CHẠY. Chính cái giật
       vừa sửa là "có hình mà không chạy", nên đây là chỗ phải hỏi câu đó.
    """
    loc = pg.locator("#nm-warp-cv")
    n1, b1 = _bright(loc.screenshot())
    pg.wait_for_timeout(120)
    n2, b2 = _bright(loc.screenshot())
    return max(n1, n2), (b1 != b2)


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
        px, moved = warp_pixels(pg)
        chk(px > 400, "vet sao CO THAT (dem pixel sang tren anh chup canvas)", f"{px} px")
        # ⚠️ Phép kiểm này sinh ra tu cai giat da sua 03/08/2026: canvas co the day
        #    sao ma van DUNG CUNG (main thread bi three.js chan 97% thoi gian). "Co
        #    hinh" khong bang "dang chay", nen phai hoi rieng.
        chk(moved, "vet sao CHAY THAT (hai anh chup cach 120ms KHAC nhau)")
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
        head("[4] ④ Bam Trai Dat -> NHIP 0 (khi quyen -> moi xoay) -> SAN -> Comet hoi")
        chk(click_earth(pg), "bam duoc vao Trai Dat")
        wait_js(pg, "() => document.getElementById('info')"
                    ".classList.contains('open')", "bang thong tin mo ra")
        chk(True, "bang thong tin MO ra de doc")

        # ══ NHIP 0 (them 02/08/2026, `docs/decisions/005` muc 1) ═══════════════════
        # Bai hoc ngay/dem CHUYEN tu ban do phang cua mission-earth.html sang QUA CAU
        # 3D o day — noi ranh gioi la THAT (`PointLight` gan vao Mat Troi cua canh),
        # con o kia no la mot gradient ma chu du an da bac bang anh chup.
        st = pg.evaluate("() => AstroQMapOnboard._state()")
        chk(st == "atmo", "vao NHIP 0 ngay sau khi bang thong tin mo", st)
        wait_typed(pg, "Comet go xong cau ve bau khi quyen")
        s0 = say(pg)
        chk("khí quyển" in s0["text"], "Comet chi vao BAU KHI QUYEN", s0["text"][:70])
        # ⚠️ Vanh khi quyen trong canh dang duoc ve DAY GAP ~2 LAN ban kinh hanh tinh.
        #    Chi vao do ma khong noi gi la DAY SAI MO HINH TU DUY — day la mot RANG
        #    BUOC cua `005`, khong phai mot cau van tuy y.
        wait_btn(pg, "co nut Tiep tuc sau cau khi quyen")
        pg.evaluate("() => document.getElementById('mo-next').click()")
        wait_typed(pg, "Comet go xong cau 'khi quyen mong hon the nhieu'")
        s0b = say(pg)
        chk("mỏng hơn" in s0b["text"],
            "Comet NOI THAT rang vanh dang duoc ve day qua", s0b["text"][:70])
        wait_btn(pg, "co nut Tiep tuc sau cau dinh chinh")
        pg.evaluate("() => document.getElementById('mo-next').click()")
        wait_typed(pg, "Comet go xong loi moi xoay")
        s0c = say(pg)
        chk(pg.evaluate("() => AstroQMapOnboard._state()") == "spin",
            "sang nhip MOI XOAY")
        chk("xoay" in s0c["text"] and "ban ngày" in s0c["text"] and "ban đêm" in s0c["text"],
            "moi tre XOAY de ngam nua ngay / nua dem", s0c["text"][:80])
        # ⛔ QUA CAU 3D KHONG BAO GIO DUOC MANG DIEU KIEN THANG. Day la cho QUAN SAT.
        #    Dieu kien thang do tren camera-orbit chinh la loi da lam buoc `rotation`
        #    ban 3D KHONG THE HOAN THANH va treo vinh vien o reduced-motion.
        chk(not pg.evaluate(
                "() => !!(window.AstroQMapOnboard && AstroQMapOnboard.win)"),
            "nhip 0 KHONG co dieu kien thang (chi la cho quan sat)")
        wait_btn(pg, "co nut Tiep tuc sau loi moi xoay")
        pg.evaluate("() => document.getElementById('mo-next').click()")

        # ⚠️ ĐẢO CHIỀU 02/08/2026: trước đây chỗ này chờ state `reading` (mốc SÀN 15
        #    giây) rồi mới sang `ask`. Nay **KHÔNG CÒN MỐC CHỜ NÀO** — bấm "Tiếp tục" là
        #    sang câu hỏi NGAY. Điều phải kiểm giờ là chính điều đó, và nó chặt hơn bản
        #    cũ: một cái nút ghi "Tiếp tục" thì phải tiếp tục.
        wait_js(pg, "() => AstroQMapOnboard._state() === 'ask'",
                "bam Tiep tuc la sang cau hoi NGAY, khong con moc cho nao")
        # ⚠️ HỎI ĐÚNG HAI THỨ ĐÃ BỊ BỎ KHỎI BỀ MẶT CÔNG KHAI. Bản đầu của phép kiểm này
        #    còn hỏi thêm `"reading" not in Object.keys(...)` — nhưng `reading()` là hàm
        #    NỘI BỘ, chưa bao giờ được export, nên điều kiện đó LUÔN đúng: một nửa phép
        #    kiểm rỗng, và nửa rỗng thì không bảo vệ gì mà vẫn làm người đọc yên tâm.
        _sur = pg.evaluate("() => ['READ_MS' in AstroQMapOnboard,"
                           " typeof AstroQMapOnboard._setReadMs]")
        chk(_sur[0] is False and _sur[1] == "undefined",
            "san pham KHONG con `READ_MS` va `_setReadMs` (moc cho da bo han)", str(_sur))
        wait_typed(pg, "Comet go xong cau hoi")
        wait_btn(pg, "nut OK hien ra")
        s = say(pg)
        chk(s["shown"], "Comet hien lai de hoi")
        chk("sẵn sàng" in s["text"] and "nhiệm vụ đầu tiên" in s["text"],
            "cau hoi dung y: 'san sang bat dau nhiem vu dau tien'", s["text"][:80])
        # ⚠️ MỐC ĐỌC LÀ SÀN, KHÔNG PHẢI HẠN — bảng thông tin PHẢI còn mở.
        chk(pg.evaluate("() => document.getElementById('info')"
                        ".classList.contains('open')"),
            "bang thong tin VAN MO khi Comet hoi (moc doc la SAN, khong phai han)")
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

        # ⛔ PHÉP KIỂM "san doc mac dinh la 15 giay" ĐÃ BỎ — nó khẳng định đúng một
        #    trạng thái không còn tồn tại. Thứ thay nó là phép kiểm ngay trên: sản phẩm
        #    KHÔNG còn `READ_MS`. Đó là bảo đảm mạnh hơn (0 mốc chờ) chứ không phải nới
        #    lỏng: mốc chờ nào quay lại cũng làm phép kiểm kia đỏ.

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
        # NHIP 0 (khi quyen -> dinh chinh -> moi xoay) chen vao truoc cau hoi tu
        # 02/08/2026. Ba cu bam "Tiep tuc" — cung dung cai nut se mang cau hoi sau do.
        for _i in range(3):
            wait_btn(pg, f"dien thoai: nut Tiep tuc cua nhip 0 ({_i+1}/3)")
            pg.evaluate("() => document.getElementById('mo-next').click()")
            pg.wait_for_timeout(150)
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
