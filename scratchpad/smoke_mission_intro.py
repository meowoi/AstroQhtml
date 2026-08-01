# -*- coding: utf-8 -*-
# ⚠️⚠️ BỘ NÀY ĐÃ NGHỈ HƯU 01/08/2026 — nó đo `js/mission-intro.js`, mà màn cutscene
#      đó không còn trang nào nạp (docs/decisions/003 bước ⑦). Chạy nó bây giờ sẽ
#      HỎNG, và hỏng đó KHÔNG phải lỗi sản phẩm.
#      Màn thay thế có bộ đo riêng: `scratchpad/smoke_map_onboard.py`.
#      Giữ file để tra lại 4 phép đo đã trả giá (tàu bay ĐÚNG quỹ đạo: khoảng cách
#      tới tâm 1,47–1,49 R trong khi GÓC đổi; box thoại không đè Trái Đất).

"""
smoke_mission_intro.py — chơi THẬT màn mở đầu Nhiệm Vụ 01 trên Chromium.

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/smoke_mission_intro.py

Đo trên trang, không đọc code: tàu có THẬT SỰ bay vòng quanh Trái Đất hay không
(đo khoảng cách tới tâm hành tinh qua nhiều khung), lời Comet đúng từng chữ theo
bản mô tả, pop-up đúng chữ trong ảnh yêu cầu, và cờ `intro01Seen` độc lập với
`tourSeen`.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
ok_n, bad_n = 0, 0
errors = []

USER = {"name": "Bi Bo", "pilotName": "Bi Bo", "character": "m",
        "selectedCharacter": "m", "avatar": "ava/avam.png", "uid": "UID1234ABCD"}

# Câu thoại phải khớp bản mô tả người dùng đưa
LINE_VI_BITS = ["Đây là", "Trái Đất", "ngôi nhà của chúng ta",
                "Đội Biệt Kích", "Vũ Trụ", "nhiệm vụ đầu tiên"]
POP_VI = "MISSION 01: HÀNH TINH XANH"
GO_VI = "NHẤN ĐỂ KÍCH HOẠT SỨ MỆNH"


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def stub(tour_seen=True, intro_seen=False):
    """AstroQAuth giả, trạng thái LƯU TRONG localStorage nên sống qua F5.

    ⚠️ Bản đầu giữ trạng thái trong biến `window.__ob` → init script gieo lại mỗi
    lần tải trang, nên test `reset() + F5` không bao giờ đúng (cùng đúng cái bẫy đã
    gặp ở smoke_onboard.py). Chỉ GIEO khi khoá còn trống.

    Cài bằng getter/setter vì js/firebase-auth.js là ES module nên chạy SAU script
    cổ điển và sẽ đè mất bản giả nếu gán thẳng.
    """
    return f"""
      const OBK = "__test-onboarding";
      function obLoad() {{
        try {{ return JSON.parse(localStorage.getItem(OBK)) || null; }} catch (e) {{ return null; }}
      }}
      function obSave(o) {{ try {{ localStorage.setItem(OBK, JSON.stringify(o)); }} catch (e) {{}} }}
      if (!obLoad()) obSave({{ tourSeen:{json.dumps(tour_seen)},
                               intro01Seen:{json.dumps(intro_seen)} }});
      window.__calls = [];
      /* Ghi kèm vào localStorage: nút kích hoạt điều hướng sang trang khác,
         `window.__calls` chết theo trang cũ. Muốn chứng minh PUT đã kịp gửi
         TRƯỚC lúc rời trang thì phải để lại dấu vết sống qua điều hướng.
         (Khối này nằm trong f-string của Python nên mọi dấu ngoặc nhọn phải nhân đôi.) */
      function logCall(x) {{
        window.__calls.push(x);
        try {{
          const k = "__test-calls";
          const a = JSON.parse(localStorage.getItem(k) || "[]");
          a.push(x); localStorage.setItem(k, JSON.stringify(a));
        }} catch (e) {{}}
      }}
      const s = {{
        idToken: async () => "tok",
        getOnboarding: async () => {{ logCall("getOnboarding");
          const o = obLoad(); return {{ ok:true, tourSeen:o.tourSeen, intro01Seen:o.intro01Seen }}; }},
        setOnboarding: async (p) => {{ logCall("setOnboarding:" + JSON.stringify(p));
          const o = obLoad();
          if (p === true || p === false) o.tourSeen = (p !== false);
          else if (p && typeof p === "object") {{
            if ("tourSeen" in p) o.tourSeen = !!p.tourSeen;
            if ("intro01Seen" in p) o.intro01Seen = !!p.intro01Seen;
          }}
          obSave(o);
          return {{ ok:true, tourSeen:o.tourSeen, intro01Seen:o.intro01Seen }}; }},
        getProfile: async () => ({{ ok:false, reason:"net" }}),
        getAchievements: async () => ({{ ok:false, reason:"net" }}),
        getWallet: async () => ({{ ok:true, data:{{ meteors:41 }} }}),
        updateProfile: async () => ({{ ok:false, reason:"net" }}),
        postProgress: async () => ({{ ok:false, reason:"net" }}),
        spendWallet: async () => ({{ ok:false, reason:"net" }})
      }};
      Object.defineProperty(window, "AstroQAuth",
        {{ get: () => s, set: () => {{}}, configurable: true }});
    """


def new_page(browser, lang="vi", mobile=False, reduced=False,
             tour_seen=True, intro_seen=False, local_intro=False, touch_local=True):
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
        + ("localStorage.setItem('astroq-tour-seen','1');" if tour_seen
           else "localStorage.removeItem('astroq-tour-seen');")
        # touch_local=False: KHÔNG đụng cờ trong máy, để test `reset() + F5` không bị
        # init script gieo lại đè lên (đúng bẫy đã gặp ở smoke_onboard.py).
        + ("" if not touch_local else
           ("localStorage.setItem('astroq-mission01-intro-seen','1');" if local_intro
            else "localStorage.removeItem('astroq-mission01-intro-seen');"))
        + "localStorage.setItem('astroq-sfx','off');"     # test thì tắt tiếng
        + stub(tour_seen, intro_seen)
    )
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    return ctx, page


def txt(page, sel):
    return page.inner_text(sel).strip()


def ship_orbit(page, n=6, gap=260):
    """Khoảng cách tàu → tâm Trái Đất, đo qua n khung.

    Đo bằng chính hàm shipAt/earthAt của trang (qua AstroQMissionIntro.CONFIG là
    không đủ — cần vị trí thật). Dùng pixel thì không tách được tàu khỏi hành tinh,
    nên đo bằng toạ độ: tàu vẽ ở đâu là do JS quyết, đọc thẳng ra đáng tin hơn.
    """
    out = []
    for _ in range(n):
        d = page.evaluate("""() => {
            const cv = document.querySelector('#mission-intro canvas');
            if (!cv) return null;
            // Tìm khối pixel SÁNG bên NGOÀI đĩa hành tinh = con tàu
            const g = cv.getContext('2d');
            const dpr = cv.width / window.innerWidth;
            const portrait = window.innerHeight > window.innerWidth;
            const cx = window.innerWidth * (portrait ? .60 : .70);
            const cy = window.innerHeight * (portrait ? .34 : .42);
            const R  = Math.min(window.innerWidth, window.innerHeight) * (portrait ? .28 : .25);
            const d = g.getImageData(0, 0, cv.width, cv.height).data;
            let sx = 0, sy = 0, n = 0;
            const step = 3;
            for (let py = 0; py < cv.height; py += step) {
              for (let px = 0; px < cv.width; px += step) {
                const i = (py * cv.width + px) * 4;
                const r = d[i], gg = d[i+1], b = d[i+2];
                if (r + gg + b < 330) continue;                  // không đủ sáng
                const X = px / dpr, Y = py / dpr;
                const dist = Math.hypot(X - cx, Y - cy);
                if (dist < R * 1.14) continue;                   // trong hành tinh/khí quyển
                if (dist > R * 2.6) continue;                    // quá xa → sao nền
                sx += X; sy += Y; n++;
              }
            }
            if (n < 12) return null;
            const mx = sx / n, my = sy / n;
            return { d: Math.hypot(mx - cx, my - cy) / R, n: n,
                     ang: Math.atan2(my - cy, mx - cx) };
        }""")
        if d:
            out.append(d)
        page.wait_for_timeout(gap)
    return out


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ══════════════ 1. Luồng đầy đủ: tour → warp → cutscene ══════════════
        print("\n[1] Luong day du: tour -> man loading -> cutscene Nhiem Vu 01")
        ctx, page = new_page(browser, tour_seen=False)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#tour.show", timeout=9000)
        check("Comet dan tham quan hien truoc", page.is_visible("#tour.show"))
        for _ in range(7):
            page.click(".tour-next")
            page.wait_for_timeout(220)
        page.wait_for_selector("#warp.show", timeout=5000)
        check("Man loading Luna hien sau tour", page.is_visible("#warp.show"))
        page.click(".warp-skip")
        page.wait_for_selector("#mission-intro.show", timeout=6000)
        check("Cutscene Nhiem Vu 01 hien SAU man loading",
              page.is_visible("#mission-intro.show"))
        check("Man loading da dong", not page.is_visible("#warp.show"))
        ctx.close()

        # ══════════════ 2. Nội dung thoại + pop-up ══════════════
        print("\n[2] Loi Comet + pop-up sư menh")
        ctx, page = new_page(browser)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        check("Da xem tour roi -> cutscene tu chay", page.is_visible("#mission-intro.show"))
        check("Anh Comet hien (img/m1.png)",
              page.evaluate("() => { const i=document.querySelector('.mi-say .aq-ava img');"
                            "return !!i && i.complete && i.naturalWidth>0; }"))
        check("Ten linh vat la Comet", txt(page, ".mi-who .aq-nm") == "Comet",
              txt(page, ".mi-who .aq-nm"))

        # Chờ gõ xong (câu ~200 ký tự × 26ms ≈ 5,2s + 2,2s chờ)
        page.wait_for_selector(".mi-next:not(.hide)", timeout=15000)
        line = txt(page, ".mi-line")
        for bit in LINE_VI_BITS:
            check(f"Thoai co '{bit}'", bit in line)
        check("Thoai KHONG lot the HTML ra ngoai", "<b>" not in line, line[:60])
        check("Con tro nhap nhay da tat khi go xong", "▌" not in line)
        check("Pop-up CHUA hien khi Comet dang noi", not page.is_visible(".mi-pop.show"))

        page.click(".mi-next")
        page.wait_for_timeout(700)
        check("Bam Tiep tuc -> pop-up hien", page.is_visible(".mi-pop.show"))
        check("Pop-up dung tieu de yeu cau", POP_VI in txt(page, ".mi-pop h2").upper(),
              txt(page, ".mi-pop h2").replace("\n", " "))
        check("Pop-up co 2 ngoi sao bang ☄️",
              txt(page, ".mi-pop h2").count("☄️") == 2, txt(page, ".mi-pop h2"))
        check("Nut dung chu yeu cau", GO_VI in txt(page, ".mi-go").upper(), txt(page, ".mi-go"))
        check("Nut kich hoat trong ngoac vuong kieu terminal",
              txt(page, ".mi-go").startswith("[") and txt(page, ".mi-go").endswith("]"),
              txt(page, ".mi-go"))
        check("Nut Bo qua an di khi da tới pop-up",
              page.evaluate("() => getComputedStyle(document.querySelector('.mi-skip')).display")
              == "none")
        page.screenshot(path="scratchpad/mi02-pop.png")
        ctx.close()

        # ══════════════ 3. Cảnh: Trái Đất + tàu BAY VÒNG quanh ══════════════
        print("\n[3] Canh khong gian: Trai Dat + tau bay VONG quanh quy dao")
        ctx, page = new_page(browser)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        page.wait_for_timeout(1200)
        earth = page.evaluate("""() => {
            const cv = document.querySelector('#mission-intro canvas');
            const g = cv.getContext('2d');
            const dpr = cv.width / window.innerWidth;
            const portrait = window.innerHeight > window.innerWidth;
            const cx = window.innerWidth * (portrait ? .60 : .70) * dpr;
            const cy = window.innerHeight * (portrait ? .34 : .42) * dpr;
            const R = Math.min(window.innerWidth, window.innerHeight) * (portrait ? .28 : .25) * dpr;
            const rd = Math.round(R * 0.8);
            const d = g.getImageData(Math.round(cx-rd), Math.round(cy-rd), rd*2, rd*2).data;
            let blue = 0, green = 0, tot = 0;
            for (let i = 0; i < d.length; i += 4) {
              const r=d[i], gg=d[i+1], b=d[i+2]; tot++;
              if (b > 70 && b > r + 25) blue++;
              if (gg > 80 && gg > b + 10 && gg > r + 20) green++;
            }
            return { blue, green, tot };
        }""")
        check("Trai Dat: phan lon la dai duong xanh-lam",
              earth["blue"] > earth["tot"] * 0.45,
              f"{earth['blue']}/{earth['tot']} px lam")
        check("Trai Dat: co luc dia xanh la", earth["green"] > 400, f"{earth['green']} px")

        # Chờ tàu vào quỹ đạo hẳn (CONFIG.tOrbitEnd = 6,4s) rồi đo nhiều khung
        page.wait_for_timeout(6200)
        obs = ship_orbit(page, n=6, gap=300)
        check("Do duoc vi tri tau qua >= 5 khung", len(obs) >= 5, f"{len(obs)} khung")
        if len(obs) >= 5:
            ds = [o["d"] for o in obs]
            spread = max(ds) - min(ds)
            check("Tau o NGOAI hanh tinh, gan quy dao (1,1–2,0 R)",
                  all(1.05 < d < 2.0 for d in ds),
                  "d/R = " + ", ".join(f"{d:.2f}" for d in ds))
            check("Khoang cach toi tam GIU gan nhu khong doi -> dang bay VONG",
                  spread < 0.18, f"bien do {spread:.3f} R")
            angs = [o["ang"] for o in obs]
            moved = max(abs(angs[i+1] - angs[i]) for i in range(len(angs)-1))
            check("Goc CO doi -> tau dang di chuyen chu khong dung im",
                  moved > 0.01, f"buoc goc lon nhat {moved:.3f} rad")
        page.screenshot(path="scratchpad/mi01-orbit.png")
        ctx.close()

        # ══════════════ 4. Kích hoạt + cờ đã xem ══════════════
        print("\n[4] Kich hoat su menh + co da xem")
        # touch_local=False: nút kích hoạt ĐIỀU HƯỚNG sang mission-earth.html, mà
        # `add_init_script` chạy lại ở MỌI lần tải trang — để mặc định thì nó
        # `removeItem('astroq-mission01-intro-seen')` và xoá đúng cái cờ vừa ghi,
        # test báo hỏng oan. Đây là lần thứ TƯ gặp cùng một bẫy (smoke_onboard,
        # smoke_profile_pages, ghi chú ở stub() phía trên): init script KHÔNG phải
        # "gieo một lần", nó gieo lại sau mỗi điều hướng.
        ctx, page = new_page(browser, touch_local=False)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        page.click(".mi-skip")
        page.wait_for_timeout(600)
        check("Bam Bo qua -> nhay thang tới pop-up", page.is_visible(".mi-pop.show"))
        page.click(".mi-go")
        # Nút kích hoạt DẪN SANG trang nhiệm vụ (dashboard.html -> onActivate).
        # Trước đây nó chỉ hiện toast rồi ở lại dashboard; các phép kiểm toast /
        # "dashboard còn 3 card" đã lỗi thời nên bỏ, thay bằng phép kiểm điều hướng.
        page.wait_for_url("**/mission-earth.html", timeout=15000)
        check("Kich hoat -> di sang trang nhiem vu", "mission-earth.html" in page.url,
              page.url)
        check("Ghi cache 'da xem' trong may",
              page.evaluate("() => localStorage.getItem('astroq-mission01-intro-seen') === '1'"))
        # ⚠️ Đọc từ localStorage, không đọc `window.__calls`: điều hướng xoá sạch
        # biến trong window. Đây cũng chính là phép kiểm cho lỗi vừa sửa — bản đầu
        # bắn PUT rồi 500ms sau `location.href`, điều hướng huỷ request đang bay
        # nên cờ `intro01Seen` không bao giờ tới DynamoDB.
        calls = page.evaluate(
            "() => { try { return JSON.parse(localStorage.getItem('__test-calls')"
            " || '[]'); } catch (e) { return []; } }")
        sets = [c for c in calls if c.startswith("setOnboarding:")]
        check("PUT /me/onboarding voi intro01Seen KIP GUI truoc khi roi trang",
              any('"intro01Seen":true' in c for c in sets), str(sets))
        check("KHONG gui tourSeen kem theo (2 co doc lap)",
              all("tourSeen" not in c for c in sets if "intro01Seen" in c), str(sets))
        ctx.close()

        # ══════════════ 5. Vào lại thì không chạy nữa ══════════════
        print("\n[5] Vao lai — khong chay lai cutscene")
        ctx, page = new_page(browser, local_intro=True)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_timeout(2600)
        check("Cache noi da xem -> khong hien", not page.is_visible("#mission-intro.show"))
        ctx.close()

        print("\n[5b] Server noi da xem (may moi, cache rong) -> khong hien")
        ctx, page = new_page(browser, intro_seen=True)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_timeout(2800)
        check("Khong hien cutscene", not page.is_visible("#mission-intro.show"))
        check("Co goi GET /me/onboarding",
              "getOnboarding" in page.evaluate("() => window.__calls"))
        check("Ghi cache lai cho lan sau",
              page.evaluate("() => localStorage.getItem('astroq-mission01-intro-seen') === '1'"))
        ctx.close()

        print("\n[5c] tourSeen=true nhung intro01Seen=false -> CHI cutscene chay")
        ctx, page = new_page(browser, tour_seen=True, intro_seen=False)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        check("Cutscene chay", page.is_visible("#mission-intro.show"))
        check("Tour KHONG chay lai", not page.is_visible("#tour.show"))
        check("Man loading KHONG chay lai", not page.is_visible("#warp.show"))
        ctx.close()

        # ══════════════ 6. Tiếng Anh ══════════════
        print("\n[6] Tieng Anh")
        ctx, page = new_page(browser, lang="en")
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        page.click(".mi-skip")
        page.wait_for_timeout(700)
        check("EN: thoai dich", "This is" in txt(page, ".mi-line")
              and "home" in txt(page, ".mi-line"), txt(page, ".mi-line")[:70])
        check("EN: tieu de nhiem vu dich",
              "BLUE PLANET" in txt(page, ".mi-pop h2").upper(), txt(page, ".mi-pop h2"))
        check("EN: nut kich hoat dich",
              "ACTIVATE" in txt(page, ".mi-go").upper(), txt(page, ".mi-go"))
        ctx.close()

        # ══════════════ 7. Điện thoại ══════════════
        print("\n[7] Dien thoai 390x844")
        ctx, page = new_page(browser, mobile=True)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        page.wait_for_timeout(1400)
        m = page.evaluate("""() => {
            const say = document.querySelector('.mi-say').getBoundingClientRect();
            const portrait = window.innerHeight > window.innerWidth;
            const cy = window.innerHeight * (portrait ? .34 : .42);
            const R = Math.min(window.innerWidth, window.innerHeight) * (portrait ? .28 : .25);
            return { sayTop: say.top, sayLeft: say.left, sayRight: say.right,
                     earthBottom: cy + R, vw: window.innerWidth,
                     scrollW: document.documentElement.scrollWidth };
        }""")
        check("[dt] Box thoai khong tran ngang",
              m["sayLeft"] >= 4 and m["sayRight"] <= m["vw"] - 4, str(m))
        check("[dt] Box thoai KHONG de len Trai Dat", m["sayTop"] > m["earthBottom"],
              f"sayTop={round(m['sayTop'])} earthBottom={round(m['earthBottom'])}")
        check("[dt] Trang khong tran ngang", m["scrollW"] <= m["vw"] + 1, str(m["scrollW"]))
        page.click(".mi-skip")
        page.wait_for_timeout(700)
        pop = page.evaluate("""() => { const r=document.querySelector('.mi-pop').getBoundingClientRect();
            return { l:r.left, r:r.right, t:r.top, b:r.bottom,
                     vw:window.innerWidth, vh:window.innerHeight }; }""")
        # Không được có dòng nào CHỈ chứa ngôi sao ☄️ — đo bằng số dòng text thật
        # của h2 (bản đầu dùng flex-wrap nên ngôi sao thứ hai rơi xuống dòng riêng).
        orphan = page.evaluate("""() => {
            const h = document.querySelector('.mi-pop h2');
            const r = document.createRange();
            const lines = [];
            for (const n of h.childNodes) {
              if (n.nodeType === 1 && n.classList.contains('cm')) {
                lines.push({ cm:true, top: Math.round(n.getBoundingClientRect().top) });
              } else if (n.nodeType === 1) {
                r.selectNodeContents(n);
                for (const b of r.getClientRects()) lines.push({ cm:false, top: Math.round(b.top) });
              }
            }
            // Dòng nào có ngôi sao mà KHÔNG có chữ nào cùng dòng = ngôi sao mồ côi
            const tops = new Set(lines.filter(l => !l.cm).map(l => l.top));
            return lines.filter(l => l.cm && ![...tops].some(t => Math.abs(t - l.top) < 14)).length;
        }""")
        check("[dt] Khong co ngoi sao ☄️ dung mot dong rieng", orphan == 0,
              f"{orphan} ngoi sao mo coi")
        check("[dt] Pop-up nam trong man hinh",
              pop["l"] >= 4 and pop["r"] <= pop["vw"] - 4 and pop["t"] >= 0
              and pop["b"] <= pop["vh"], str(pop))
        page.screenshot(path="scratchpad/mi03-mobile.png")
        ctx.close()

        # ══════════════ 8. prefers-reduced-motion ══════════════
        print("\n[8] prefers-reduced-motion")
        ctx, page = new_page(browser, reduced=True)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        page.wait_for_timeout(900)
        check("[rm] Thoai hien NGAY, khong go tung chu",
              "nhiệm vụ đầu tiên" in txt(page, ".mi-line"), txt(page, ".mi-line")[-40:])
        check("[rm] Nut Tiep tuc hien ngay",
              page.evaluate("() => !document.querySelector('.mi-next').classList.contains('hide')"))
        rm = page.evaluate("""() => {
            const cv = document.querySelector('#mission-intro canvas');
            const g = cv.getContext('2d');
            const dpr = cv.width / window.innerWidth;
            const cx = window.innerWidth * .70 * dpr, cy = window.innerHeight * .42 * dpr;
            const R = Math.min(window.innerWidth, window.innerHeight) * .25 * dpr;
            const rd = Math.round(R*0.8);
            const d = g.getImageData(Math.round(cx-rd), Math.round(cy-rd), rd*2, rd*2).data;
            let blue=0, tot=0;
            for(let i=0;i<d.length;i+=4){ tot++; if(d[i+2] > 70 && d[i+2] > d[i]+25) blue++; }
            return { blue, tot };
        }""")
        check("[rm] Trai Dat van hien du", rm["blue"] > rm["tot"] * 0.45,
              f"{rm['blue']}/{rm['tot']}")
        page.click(".mi-next")
        page.wait_for_timeout(500)
        check("[rm] Van tới duoc pop-up", page.is_visible(".mi-pop.show"))
        ctx.close()

        # ══════════════ 9. reset() để xem lại ══════════════
        print("\n[9] AstroQMissionIntro.reset() de xem lai")
        ctx, page = new_page(browser, intro_seen=True, touch_local=False)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_timeout(2200)
        check("Chua reset -> khong hien", not page.is_visible("#mission-intro.show"))
        page.evaluate("() => AstroQMissionIntro.reset()")
        page.wait_for_timeout(700)
        check("reset() xoa cache trong may",
              page.evaluate("() => localStorage.getItem('astroq-mission01-intro-seen') === null"))
        check("reset() cung ghi intro01Seen=false len server",
              any('"intro01Seen":false' in c
                  for c in page.evaluate("() => window.__calls")),
              str(page.evaluate("() => window.__calls")))
        page.reload(wait_until="load")
        page.wait_for_selector("#mission-intro.show", timeout=9000)
        check("Sau reset + F5 -> cutscene hien lai", page.is_visible("#mission-intro.show"))
        ctx.close()

        browser.close()

    noise = ("favicon", "ERR_INTERNET_DISCONNECTED")
    real = [e for e in errors if not any(n in e for n in noise)]
    print(f"\n[console] {len(real)} loi")
    for e in real[:12]:
        print("   -", e[:200])
    check("0 loi console", len(real) == 0, f"{len(real)} loi")

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
