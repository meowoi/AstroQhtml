# -*- coding: utf-8 -*-
"""
smoke_earth_done.py — soi LUỒNG HẬU-NHIỆM-VỤ trên Chromium thật:
  · mission-earth.html: đường về tự động 5 giây (đếm, tắt khi tương tác)
  · dashboard.html: Comet chúc mừng + chiếu sáng thẻ Trung Tâm Nhiệm Vụ

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/smoke_earth_done.py

⚠️ Nhãn của chk() PHẢI KHÔNG DẤU ở phần cố định — console Windows mặc định cp1252,
   in chữ có dấu là UnicodeEncodeError ném GIỮA LÚC CHẠY và bỏ dở mọi phép kiểm sau.
   (Chữ có dấu chỉ nằm trong phần `detail` lấy từ trang.)
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
USER = {"name": "Bi", "pilotName": "Bi", "character": "raica",
        "avatar": "ava/avaraica.png", "uid": "test-uid"}

ok_n = bad_n = 0


def chk(cond, label, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def head(t):
    print(f"\n{t}")


def stub(earth_done=True, greeted=False, ob_ok=True):
    """AstroQAuth + AstroQProgress giả.

    ⚠️ Cài bằng getter/setter, KHÔNG gán thẳng: js/firebase-auth.js là ES module nên
       chạy SAU script cổ điển và sẽ đè mất bản giả.
    ⚠️ Trạng thái lưu trong localStorage để sống qua F5 (bài học smoke_onboard.py:
       init script gieo lại mỗi lần tải trang, giữ trong biến window là test "ghi cờ
       rồi F5" không bao giờ đúng). Chỉ GIEO khi khoá còn trống.
    """
    return f"""
      const K = "__test-ob";
      function load() {{ try {{ return JSON.parse(localStorage.getItem(K)) || null; }}
                         catch (e) {{ return null; }} }}
      function save(o) {{ try {{ localStorage.setItem(K, JSON.stringify(o)); }} catch (e) {{}} }}
      if (!load()) save({{ tourSeen:true, intro01Seen:true, map01Seen:true,
                           earth1Greeted:{json.dumps(greeted)} }});
      window.__calls = [];
      const auth = {{
        idToken: async () => "tok",
        getOnboarding: async () => {{
          window.__calls.push("getOnboarding");
          if (!{json.dumps(ob_ok)}) return {{ ok:false, reason:"net" }};
          const o = load();
          return {{ ok:true, tourSeen:o.tourSeen, intro01Seen:o.intro01Seen,
                    earth1Greeted:o.earth1Greeted, map01Seen:o.map01Seen !== false }};
        }},
        setOnboarding: async (p) => {{
          window.__calls.push("setOnboarding:" + JSON.stringify(p));
          const o = load();
          if (p === true || p === false) o.tourSeen = (p !== false);
          else if (p && typeof p === "object") {{
            if ("tourSeen" in p) o.tourSeen = !!p.tourSeen;
            if ("intro01Seen" in p) o.intro01Seen = !!p.intro01Seen;
            if ("earth1Greeted" in p) o.earth1Greeted = !!p.earth1Greeted;
            if ("map01Seen" in p) o.map01Seen = !!p.map01Seen;
          }}
          save(o);
          return {{ ok:true, ...o }};
        }},
        getProfile: async () => ({{ ok:false, reason:"net" }}),
        getAchievements: async () => ({{ ok:false, reason:"net" }}),
        getWallet: async () => ({{ ok:true, data:{{ meteors:41 }} }}),
        updateProfile: async () => ({{ ok:false, reason:"net" }}),
        postProgress: async () => ({{ ok:false, reason:"net" }}),
        spendWallet: async () => ({{ ok:false, reason:"net" }})
      }};
      Object.defineProperty(window, "AstroQAuth",
        {{ get: () => auth, set: () => {{}}, configurable: true }});

      /* AstroQProgress giả — chỉ cần `missions()`. Cũng phải dùng defineProperty vì
         js/progress.js gán thẳng `window.AstroQProgress`. */
      const prog = {{
        missions: async () => {{
          window.__calls.push("missions");
          return {{ ok:true, data:{{ missions:{{ earth:{{
            done:{json.dumps(earth_done)}, doneSteps:[], steps:[] }} }} }} }};
        }},
        achievements: async () => ({{ ok:false, reason:"net" }}),
        quiz: () => {{}}, game: () => {{}}, lesson: () => {{}}, planet: () => {{}},
        spend: () => {{}}, missionStep: async () => ({{ ok:false }})
      }};
      Object.defineProperty(window, "AstroQProgress",
        {{ get: () => prog, set: () => {{}}, configurable: true }});
    """


def dash(browser, earth_done=True, greeted=False, ob_ok=True,
         lang="vi", mobile=False, reduced=False):
    kw = {"locale": "vi-VN"}
    kw["viewport"] = {"width": 390, "height": 844} if mobile else {"width": 1440, "height": 950}
    if mobile:
        kw.update(is_mobile=True, has_touch=True, device_scale_factor=2)
    if reduced:
        kw["reduced_motion"] = "reduce"
    ctx = browser.new_context(**kw)
    ctx.add_init_script(
        f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
        f"localStorage.setItem('astroq-lang', '{lang}');"
        "localStorage.setItem('astroq-asteroids','41');"
        "localStorage.setItem('astroq-tour-seen','1');"
        # ⚠️ PHẢI GIEO `astroq-map01-seen`. Từ 01/08/2026 `dashboard.html` đẩy trẻ sang
        #    `explorer.html?onboard=1` khi chưa đi qua bản đồ (docs/decisions/003) —
        #    không gieo thì trang ĐIỀU HƯỚNG ĐI, `.tour` không tồn tại và bộ này ném
        #    "Failed to find element matching selector .tour". Màn bản đồ có bộ riêng.
        "localStorage.setItem('astroq-map01-seen','1');"
        "localStorage.setItem('astroq-mission01-intro-seen','1');"
    )
    ctx.add_init_script(stub(earth_done, greeted, ob_ok))
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(f"{BASE}/dashboard.html", wait_until="load")
    pg.wait_for_timeout(3200)
    return ctx, pg, errs


with sync_playwright() as p:
    br = p.chromium.launch()

    # ══════════════════════════════════════════════════════════════
    head("[1] Comet CHUC MUNG khi vua xong chuoi + chua duoc chao")
    ctx, pg, errs = dash(br)
    chk(pg.eval_on_selector(".tour", "e => e.classList.contains('show')"),
        "man chi duong CO mo")
    body = pg.inner_text(".tour-bubble")
    chk("Xuất sắc" in body, "loi thoai dung nhu de bai", body[:60])
    chk("bảng nhiệm vụ" in body, "chi sang bang nhiem vu", "")
    # Ô sáng phải TRÙNG ô của thẻ MOD-04 — chiếu sáng sai chỗ thì trẻ chỉ thấy
    # trang tối đi mà không biết đang được chỉ vào đâu.
    # ⚠️ ĐO THEO ĐÚNG THIẾT KẾ, KHÔNG ĐO BẰNG MỘT NGƯỠNG LỎNG. Engine nới ô sáng
    #    `pad = 8px` MỖI BÊN cho đường bo song song với thẻ, nên top/left phải LỆCH
    #    -8 và width/height phải LỆCH +16. Bản đầu của phép kiểm này dùng "lệch tối
    #    đa ≤ 14px" và báo hỏng ở 16px — tức là báo hỏng đúng cái thiết kế đúng.
    PAD = 8
    box = pg.evaluate("""() => {
        const h = document.querySelector('.tour-hole').getBoundingClientRect();
        const c = document.querySelector('[data-tour="missions"]').getBoundingClientRect();
        return { h:[h.top,h.left,h.width,h.height], c:[c.top,c.left,c.width,c.height] };
    }""")
    want = [box["c"][0] - PAD, box["c"][1] - PAD,
            box["c"][2] + PAD * 2, box["c"][3] + PAD * 2]
    d = max(abs(box["h"][i] - want[i]) for i in range(4))
    chk(d <= 2, "o sang TRUM dung the Trung Tam Nhiem Vu (ke ca pad 8px)",
        f"lech toi da {d:.1f}px")
    chk(pg.eval_on_selector(".tour", "e => e.classList.contains('pulse')"),
        "co vong nhap nhay (pulse) de hut mat")
    # Một bước duy nhất thì KHÔNG vẽ chấm bước
    chk(pg.eval_on_selector_all(".tour-dots span", "e => e.length") == 0,
        "MOT buoc thi khong ve cham buoc")
    chk("missions" in str(pg.evaluate("window.__calls")),
        "co hoi server chuoi xong chua", str(pg.evaluate("window.__calls")))
    chk(not errs, "0 loi console", str(errs[:2]))
    ctx.close()

    # ══════════════════════════════════════════════════════════════
    head("[2] Ghi co dung — va ghi RIENG co earth1Greeted")
    ctx, pg, errs = dash(br)
    pg.click(".tour-next")
    pg.wait_for_timeout(600)
    calls = [c for c in pg.evaluate("window.__calls") if c.startswith("setOnboarding")]
    # ⚠️ LỌC RA ĐÚNG LỜI GỌI CỦA `earth1Greeted`, ĐỪNG ĐẾM TỔNG SỐ LỜI GỌI.
    #    Từ 01/08/2026 dashboard còn đồng bộ `{map01Seen:true}` lên server khi cache
    #    trong máy nói đã đi qua bản đồ (docs/decisions/003) — một lời gọi RIÊNG và
    #    hợp lệ. Bản trước đòi "đúng MỘT lời gọi setOnboarding" nên nó báo hỏng đúng
    #    lúc sản phẩm làm đúng. Điều cần bảo vệ vẫn nguyên: cờ `earth1Greeted` được
    #    ghi ĐÚNG MỘT LẦN và ghi RIÊNG, không kèm `tourSeen`.
    g_calls = [c for c in calls if "earth1Greeted" in c]
    chk(len(g_calls) == 1, "ghi co earth1Greeted dung MOT lan", str(calls))
    chk(bool(g_calls) and "tourSeen" not in g_calls[0],
        "ghi RIENG earth1Greeted, KHONG dung tourSeen", str(g_calls))
    ob = pg.evaluate("JSON.parse(localStorage.getItem('__test-ob'))")
    chk(ob.get("earth1Greeted") is True and ob.get("tourSeen") is True,
        "co earth1Greeted len true, tourSeen GIU NGUYEN", str(ob))
    chk(pg.eval_on_selector(".tour", "e => !e.classList.contains('show')"),
        "man chi duong da dong")
    ctx.close()

    # ══════════════════════════════════════════════════════════════
    head("[3] KHONG chao lai khi da chao roi")
    ctx, pg, errs = dash(br, greeted=True)
    chk(pg.eval_on_selector(".tour", "e => !e.classList.contains('show')")
        if pg.query_selector(".tour") else True,
        "da chao roi -> KHONG mo lai")
    # Và không gọi /me/missions LẶP LẠI để biết điều đó.
    # ⚠️ ĐỔI TỪ "0 lời gọi" SANG "ĐÚNG 1 lời gọi" ngày 01/08/2026, và đây là một
    #    thay đổi CÓ LÝ DO, không phải nới lỏng cho qua: từ khi có cổng lộ trình
    #    (docs/decisions/003), dashboard PHẢI hỏi `/me/missions` mỗi lượt tải để làm
    #    mới cache cho `explorer.html` — trang bản đồ không có token nên tự nó không
    #    hỏi được. Điều phép kiểm này bảo vệ vẫn nguyên: **không gọi hai lần cho cùng
    #    một câu trả lời** (hai chỗ dùng chung `missionsShared()` ở dashboard.html).
    _calls = [c for c in (pg.evaluate("window.__calls") or []) if "missions" in str(c)]
    chk(len(_calls) == 1,
        "da chao roi: goi /me/missions DUNG 1 lan (cong lo trinh dung chung, khong goi doi)",
        f"{len(_calls)} lan: {_calls}")
    ctx.close()

    # ══════════════════════════════════════════════════════════════
    head("[4] CHUA xong chuoi -> khong chao (khong chuc mung viec chua lam)")
    ctx, pg, errs = dash(br, earth_done=False)
    chk(pg.eval_on_selector(".tour", "e => !e.classList.contains('show')")
        if pg.query_selector(".tour") else True,
        "chua xong chuoi -> KHONG chao")
    ctx.close()

    # ══════════════════════════════════════════════════════════════
    head("[5] Khong doc duoc co (mat mang) -> KHONG chao")
    # ⚠️ Khác hẳn màn dẫn tham quan: ở đó "thà chào hai lần hơn không chào lần nào".
    #    Ở đây chào sai là chúc mừng một việc trẻ chưa làm.
    ctx, pg, errs = dash(br, ob_ok=False)
    chk(pg.eval_on_selector(".tour", "e => !e.classList.contains('show')")
        if pg.query_selector(".tour") else True,
        "mat mang -> KHONG chao (khong chuc mung buong)")
    chk(not errs, "mat mang: 0 loi console", str(errs[:2]))
    ctx.close()

    # ══════════════════════════════════════════════════════════════
    head("[6] Ban EN + dien thoai + giam chuyen dong")
    ctx, pg, errs = dash(br, lang="en")
    chk("Outstanding" in pg.inner_text(".tour-bubble"), "EN: loi thoai dich",
        pg.inner_text(".tour-bubble")[:50])
    chk(not errs, "EN: 0 loi console", str(errs[:2]))
    ctx.close()

    ctx, pg, errs = dash(br, mobile=True)
    chk(pg.eval_on_selector(".tour", "e => e.classList.contains('show')"),
        "dien thoai: man chi duong mo duoc")
    # Box thoại KHÔNG được đè lên thẻ đang giới thiệu (bài học đã trả giá)
    ov = pg.evaluate("""() => {
        const b = document.querySelector('.tour-bubble').getBoundingClientRect();
        const c = document.querySelector('[data-tour="missions"]').getBoundingClientRect();
        const x = Math.max(0, Math.min(b.right,c.right) - Math.max(b.left,c.left));
        const y = Math.max(0, Math.min(b.bottom,c.bottom) - Math.max(b.top,c.top));
        return { over: x*y, card: c.width*c.height };
    }""")
    chk(ov["over"] / max(1, ov["card"]) < 0.30,
        "dien thoai: box thoai KHONG de kin the dang gioi thieu",
        f"che {ov['over']/max(1,ov['card'])*100:.0f}%")
    sw = pg.evaluate("document.documentElement.scrollWidth")
    cw = pg.evaluate("document.documentElement.clientWidth")
    chk(sw <= cw + 1, "dien thoai: khong tran ngang", f"{sw} vs {cw}")
    chk(not errs, "dien thoai: 0 loi console", str(errs[:2]))
    ctx.close()

    ctx, pg, errs = dash(br, reduced=True)
    anim = pg.eval_on_selector(".tour-hole",
                               "e => getComputedStyle(e).animationName")
    chk(anim in ("none", ""), "giam chuyen dong: tat animation nhap nhay", str(anim))
    shadow = pg.eval_on_selector(".tour-hole", "e => getComputedStyle(e).boxShadow")
    chk("9999px" in shadow, "giam chuyen dong: VAN giu lop lam toi trang", shadow[:60])
    chk(not errs, "giam chuyen dong: 0 loi console", str(errs[:2]))
    ctx.close()

    # ══════════════════════════════════════════════════════════════
    head("[7] mission-earth.html: duong ve tu dong 5 giay")
    ctx = br.new_context(viewport={"width": 1440, "height": 950}, locale="vi-VN")
    ctx.add_init_script(
        f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
        "localStorage.setItem('astroq-lang','vi');"
    )
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/mission-earth.html", wait_until="load")
    pg.wait_for_timeout(1500)
    # Mở thẳng màn tổng kết qua bề mặt test của trang
    started = pg.evaluate("""() => {
        if (!window.__mission || !window.__mission.win) return false;
        window.__mission.win(); return true;
    }""")
    if not started:
        chk(False, "mo duoc man tong ket qua window.__mission.win()",
            "khong co be mat test — bo qua muc [7]")
    else:
        pg.wait_for_timeout(400)
        chk(pg.eval_on_selector("#win", "e => e.classList.contains('show')"),
            "man tong ket mo")
        n1 = pg.inner_text("#win-auto")
        chk(any(c.isdigit() for c in n1), "co dong dem gio", n1[:50])
        pg.wait_for_timeout(2200)
        n2 = pg.inner_text("#win-auto")
        chk(n1 != n2, "dong dem gio DEM XUONG that", f"{n1[:24]} -> {n2[:24]}")
        # Tương tác phải TẮT đếm, không phải tạm dừng
        pg.mouse.move(700, 500)
        pg.wait_for_timeout(1400)
        chk(pg.inner_text("#win-auto").strip() == "",
            "di chuot vao -> TAT dem han", pg.inner_text("#win-auto")[:40])
        chk("(" not in pg.inner_text("#win-home"),
            "nut chinh khong con so dem", pg.inner_text("#win-home"))
        # Và không tự điều hướng nữa
        url = pg.url
        pg.wait_for_timeout(4200)
        chk(pg.url == url, "da tat dem thi KHONG tu ve dashboard", pg.url[-30:])
    chk(not errs, "mission-earth: 0 loi console", str(errs[:2]))
    ctx.close()

    br.close()

print(f"\n===== {ok_n} dat / {bad_n} hong =====")
sys.exit(1 if bad_n else 0)
