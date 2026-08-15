# -*- coding: utf-8 -*-
"""
smoke_onboard.py — chơi THẬT màn Comet dẫn tham quan + màn loading Luna→Trái Đất
trên Chromium (Playwright), không đọc code mà đo trên trang.

Chạy:
    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/smoke_onboard.py
"""
import math
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/dashboard.html"
ok_n, bad_n = 0, 0
errors = []

USER = {
    "name": "Bi Bo",
    "pilotName": "Bi Bo",
    "character": "m",
    "selectedCharacter": "m",
    "avatar": "ava/avam.png",
    "email": "bibo@astroq-test.invalid",
    "purpleAsteroids": 0,
}

# Thứ tự khu vực đúng như lời Comet dẫn tham quan.
# ⚠️ ĐỔI PHÁT BIỂU 15/08/2026: 7 → 6 bước. Bước "awards" (Kho Thành Tích) đã
#    GỘP vào bước "profile", vì cả sáu đường vào "xem lại mình" nay nằm trong
#    MỘT menu thả sau ảnh đại diện — hai bước liên tiếp chiếu vào cùng một cái
#    nút là nói lại một điều hai lần. Điều bộ này bảo vệ KHÔNG đổi: ô sáng phải
#    trùm đúng khu vực, và khu vực phải nằm trong khung nhìn.
ORDER = ["hello", "map", "learn", "train", "profile", "ready"]
TARGET = {
    "map": '[data-tour="map"]',
    "learn": '[data-tour="learn"]',
    "train": '[data-tour="train"]',
    "profile": '[data-tour="profile"]',
}


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def new_page(browser, lang="vi", mobile=False, reduced=False, seen=False, touch_seen=True):
    kw = {"locale": "vi-VN"}
    if mobile:
        kw["viewport"] = {"width": 390, "height": 844}
        kw["is_mobile"] = True
        kw["has_touch"] = True
        kw["device_scale_factor"] = 2
    else:
        kw["viewport"] = {"width": 1440, "height": 900}
    if reduced:
        kw["reduced_motion"] = "reduce"
    ctx = browser.new_context(**kw)
    ctx.add_init_script(
        "localStorage.setItem('astroq-user', %r);"
        "localStorage.setItem('astroq-lang', '%s');"
        "localStorage.setItem('astroq-asteroids','0');"
        # Bộ test NÀY chỉ lo tour + màn loading.
        # ⚠️ PHẢI GIEO `astroq-map01-seen` = ĐÃ ĐI QUA BẢN ĐỒ. Từ 01/08/2026
        #    `dashboard.html` đẩy trẻ sang `explorer.html?onboard=1` khi chưa đi qua
        #    (docs/decisions/003) — không gieo thì trang ĐIỀU HƯỚNG ĐI và mọi phép đo
        #    tour ở đây hỏng sạch (đã đo: 4 phép kiểm hỏng, `GET /me/onboarding` không
        #    được gọi vì trang đã rời). Màn bản đồ có bộ riêng: smoke_map_onboard.py.
        # ⚠️ `astroq-mission01-intro-seen` giữ lại dù `js/mission-intro.js` đã nghỉ hưu:
        #    khoá cũ nằm trong máy người dùng thật, gieo nó là mô phỏng đúng hiện trạng.
        "localStorage.setItem('astroq-map01-seen','1');"
        "localStorage.setItem('astroq-mission01-intro-seen','1');"
        "%s"
        % (
            __import__("json").dumps(USER),
            lang,
            # touch_seen=False: KHÔNG đụng tới cờ, để test tự đặt/xoá rồi F5 mà
            # không bị init script ghi lại đè lên (đã dính đúng bẫy này).
            "" if not touch_seen else
            ("localStorage.setItem('astroq-tour-seen','1');" if seen else
             "localStorage.removeItem('astroq-tour-seen');"),
        )
    )
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    return ctx, page


def wait_stable(page, sel=".tour-hole", tries=60, need=3, min_wait=280):
    """Chờ ô sáng đứng yên hẳn.

    Ô sáng vừa CUỘN theo trang (scrollIntoView mượt) vừa TRƯỢT bằng CSS
    transition 0,5s, nên đo bằng một khoảng chờ cố định là đo giữa lúc nó còn
    đang bay — báo lệch vài pixel dù mã hoàn toàn đúng.

    ⚠️ Hai chi tiết bắt buộc, học được sau khi test báo hỏng oan:
      · `min_wait` — không chờ chút đã đo thì 2 mẫu đầu còn là vị trí của BƯỚC
        TRƯỚC (transition chưa kịp nhích), tưởng "đã dừng" rồi đo cả bài lệch
        đúng một bước.
      · `need` mẫu giống nhau liên tiếp, không phải 1 — cuộn mượt có lúc nghỉ
        giữa hai khung.
    """
    page.wait_for_timeout(min_wait)
    prev, same = None, 0
    for _ in range(tries):
        cur = box(page, sel)
        if prev and cur and all(abs(cur[k] - prev[k]) < 0.5 for k in ("x", "y", "w", "h")):
            same += 1
            if same >= need:
                return cur
        else:
            same = 0
        prev = cur
        page.wait_for_timeout(70)
    return prev


def left_lit(page):
    """Số pixel sáng ở 40% BÊN TRÁI khung — vùng chỉ có sao, không có gì khác.

    Hai lần chỉnh mới ra phép đo dùng được, ghi lại để khỏi lặp:
      · Ngưỡng tuyệt đối ở dải rìa hẹp (18%) DAO ĐỘNG rất mạnh — 189 px ở lượt
        này, 3.000 px ở lượt khác. Sao sinh lại gần điểm tụ và tốc độ tỉ lệ với
        bán kính, nên số sao đang ở vùng ngoài cùng vốn ít và đổi từng khung.
      · Nới ra nửa khung (50%) thì lại LỌT vành khí quyển Trái Đất và cả Luna
        đang đậu → nền cố định ~3.350 px, làm hai trạng thái gần bằng nhau.
    40% (x < 576px ở khung 1440) nằm trọn bên trái cả hai thứ đó.
    """
    return page.evaluate("""() => {
        const cv = document.querySelector('#warp canvas');
        const g = cv.getContext('2d');
        const d = g.getImageData(0, 0, Math.round(cv.width*0.4), cv.height).data;
        let lit = 0;
        for(let i=0;i<d.length;i+=4){ if(d[i]+d[i+1]+d[i+2] > 200) lit++; }
        return lit;
    }""")


def box(page, sel):
    return page.evaluate(
        """s => { const e = document.querySelector(s); if(!e) return null;
                  const r = e.getBoundingClientRect();
                  return {x:r.x, y:r.y, w:r.width, h:r.height}; }""",
        sel,
    )


def play_warp(page):
    """Bật màn loading Luna BẰNG CÁCH GỌI THẲNG `AstroQWarp.play()`.

    ⚠️ Trước 01/08/2026 màn này tự hiện khi tour kết thúc (`onFinish` của
       `AstroQTour.autoStart`). Từ khi tour **dời xuống sau nhiệm vụ 1**
       (docs/decisions/003) thì `onFinish` không còn dẫn đi đâu.
       **Việc MỚI của `AstroQWarp` là chuyển cảnh dashboard → Bản Đồ Thiên Hà** (thẻ
       MOD-03), có bộ đo riêng ở `scratchpad/smoke_map_warp.py`.
       Bộ này vẫn giữ đủ 18 phép kiểm cho bản thân màn phim (vệt sao là VỆT không phải
       đốm, Trái Đất phần lớn xanh-lam, Luna đậu bên trái, thanh tiến trình, nút Bỏ qua,
       bản EN, `prefers-reduced-motion`), và gọi thẳng `play()` để đo **bộ lời MẶC
       ĐỊNH** — `smoke_map_warp.py` đo bộ lời PHỦ. Hai bộ đo hai thứ khác nhau.
       Đo bằng cách gọi thẳng là trung thực hơn giả vờ tour vẫn dẫn tới nó.
    """
    # ⚠️ ĐỌC NGÔN NGỮ TỪ localStorage, KHÔNG DÙNG `window.LANG`. `dashboard.html` giữ
    #    `LANG` trong một IIFE nên `window.LANG` là `undefined` → `AstroQWarp` rơi về
    #    tiếng Việt và phép kiểm bản EN báo hỏng oan (đã đo: "ĐANG KHỞI ĐỘNG ĐỘNG CƠ…").
    page.evaluate("""() => {
      if (!window.AstroQWarp) return;
      var l = null;
      try { l = localStorage.getItem('astroq-lang'); } catch (e) {}
      AstroQWarp.play({ lang: l === 'en' ? 'en' : 'vi' });
    }""")
    page.wait_for_selector("#warp.show", timeout=4000)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ══════════════ 1. Lần đầu vào dashboard, tiếng Việt ══════════════
        print("\n[1] Lan dau vao dashboard (vi) — Comet dan tham quan")
        ctx, page = new_page(browser, "vi")
        page.goto(BASE, wait_until="load")
        page.wait_for_selector("#tour.show", timeout=8000)
        check("Box thoai Comet tu hien", page.is_visible("#tour.show"))
        check("Anh Comet hien (img/m1.png)",
              page.evaluate("() => { const i=document.querySelector('.tour-bubble .aq-ava img');"
                            "return !!i && i.complete && i.naturalWidth>0; }"))

        title = page.inner_text(".tour-title")
        body = page.inner_text(".tour-body")
        check("Buoc 1 chao dung ten nguoi choi", "Bi Bo" in title, title.replace("\n", " "))
        check("Buoc 1 nhac Doi Biet Kich Vu Tru", "Biệt Kích Vũ Trụ" in body)
        check("Buoc 1 nhac tau Luna", "Luna" in body)
        check("So cham buoc khop so buoc that",
              page.eval_on_selector_all(".tour-dots span", "e=>e.length") == len(ORDER),
              str(page.eval_on_selector_all(".tour-dots span", "e=>e.length")))
        check("Buoc mo dau khong tro vao dau (hole.blank)",
              page.evaluate("() => document.querySelector('.tour-hole').classList.contains('blank')"))

        # Không bấm xuyên qua được lớp phủ
        # Đo ở GIỮA KHUNG NHÌN, không đo ở một cái nút cụ thể: nút có thể nằm dưới
        # mép dưới (dashboard dài ra mỗi lần thêm đường vào mới) và khi đó
        # elementFromPoint trả null → báo hỏng oan, chứ lớp phủ vẫn tốt.
        clicked = page.evaluate("""() => {
            // 4 điểm rải khắp khung nhìn: điểm nào cũng phải rơi vào LỚP CỦA TOUR
            // (tour-block chặn bấm, hoặc chính box thoại) — nghĩa là không có chỗ
            // nào bấm xuống được trang phía dưới.
            const pts = [[innerWidth*.5, innerHeight*.5], [40, 40],
                         [innerWidth-40, 40], [innerWidth-40, innerHeight-40]];
            const cls = pts.map(([x,y]) => {
              const e = document.elementFromPoint(x, y);
              if(!e) return "null";
              return e.closest('[class*="tour-"]') ? "tour-layer" : String(e.className);
            });
            return { topClass: cls.every(c => c === "tour-layer") ? "tour-layer" : cls.join("|") };
        }""")
        check("Lop phu chan bam vao trang phia duoi (4 diem)",
              clicked["topClass"] == "tour-layer", str(clicked["topClass"]))
        page.screenshot(path="scratchpad/t01-hello.png")

        # ---- Đi hết 5 khu vực, mỗi bước kiểm ô sáng trùng khu vực ----
        expect_vi = {
            "map": ("Bản đồ Thiên Hà", "chọn hành tinh để khám phá"),
            # "Trạm Tri Thức" → "Tri Thức" (đổi tên khu 29/07/2026)
            "learn": ("Tri Thức", "vũ trụ, robot và AI"),
            "train": ("Khu Huấn Luyện", "mini game"),
            # Bước gộp: giới thiệu CÁI CỬA (menu sau ảnh đại diện), không phải
            # từng ngăn tủ bên trong — mục bên trong đang `hidden` nên ô sáng
            # tính theo `getBoundingClientRect()` sẽ ra khung 0×0.
            "profile": ("Mọi thứ của riêng bạn", "hồ sơ, huy hiệu"),
        }
        for i, key in enumerate(ORDER[1:-1], start=1):
            page.click(".tour-next")
            wait_stable(page)      # chờ cuộn mượt + transition ô sáng dừng hẳn
            t, b = page.inner_text(".tour-title"), page.inner_text(".tour-body")
            exp_t, exp_b = expect_vi[key]
            check(f"[{key}] tieu de dung", exp_t in t, t.replace("\n", " "))
            check(f"[{key}] noi dung dung", exp_b in b)
            check(f"[{key}] cham buoc thu {i+1} sang",
                  page.evaluate("i => [...document.querySelectorAll('.tour-dots span')]"
                                ".findIndex(s=>s.classList.contains('on')) === i", i))
            tb, hb = box(page, TARGET[key]), box(page, ".tour-hole")
            near = (tb and hb
                    and abs((tb["x"] - 8) - hb["x"]) <= 2
                    and abs((tb["y"] - 8) - hb["y"]) <= 2
                    and abs((tb["w"] + 16) - hb["w"]) <= 2
                    and abs((tb["h"] + 16) - hb["h"]) <= 2)
            check(f"[{key}] o sang trum dung khu vuc", near,
                  f"target={tb} hole={hb}")
            check(f"[{key}] khu vuc nam trong khung nhin",
                  tb and tb["y"] >= -1 and tb["y"] + tb["h"] <= 902, str(tb))
            bub = box(page, ".tour-bubble")
            check(f"[{key}] box thoai khong tran ra ngoai man hinh",
                  bub and bub["x"] >= 8 and bub["x"] + bub["w"] <= 1432
                  and bub["y"] >= 8 and bub["y"] + bub["h"] <= 894, str(bub))
            # Box thoại không được đè lên chính khu vực đang chỉ
            overlap = (bub and tb
                       and bub["x"] < tb["x"] + tb["w"] and tb["x"] < bub["x"] + bub["w"]
                       and bub["y"] < tb["y"] + tb["h"] and tb["y"] < bub["y"] + bub["h"])
            check(f"[{key}] box thoai khong de len khu vuc", not overlap)
            page.screenshot(path=f"scratchpad/t02-{key}.png")

        # ---- Bước cuối ----
        page.click(".tour-next")
        page.wait_for_timeout(400)
        # ⚠️ Nhãn nút đổi 01/08/2026 cùng lúc lời thoại bước cuối đổi (docs/decisions/003).
        check("Buoc cuoi: nut huong ve viec TIEP THEO",
              "Khám phá" in page.inner_text(".tour-next")
              and "động cơ" not in page.inner_text(".tour-next"),
              page.inner_text(".tour-next"))
        check("Buoc cuoi: an nut Bo qua",
              page.evaluate("() => getComputedStyle(document.querySelector('.tour-skip')).display === 'none'"))
        # ⚠️ ĐỔI 01/08/2026 cùng lúc tour dời xuống SAU nhiệm vụ 1: câu cũ
        #    "hãy khởi động động cơ thôi!" nói một việc đã xảy ra từ lâu.
        check("Buoc cuoi: huong ve viec TIEP THEO (khong con 'khoi dong dong co')",
              "khám phá" in page.inner_text(".tour-body").lower()
              and "khởi động động cơ" not in page.inner_text(".tour-body").lower(),
              page.inner_text(".tour-body").replace("\n", " ")[:70])

        # ══════════════ 2. Màn loading Luna → Trái Đất ══════════════
        print("\n[2] Man loading Luna bay vao khong gian, dung o Trai Dat")
        page.click(".tour-next")
        page.wait_for_timeout(700)
        check("Tour da dong", not page.is_visible("#tour.show"))
        # ⚠️ Tour KHÔNG còn tự dẫn sang màn loading — nó đã dời xuống sau nhiệm vụ 1.
        check("Xong tour thi O LAI dashboard (khong tu bay di dau)",
              not page.is_visible("#warp.show"))
        play_warp(page)
        check("Man loading hien ra khi duoc goi", page.is_visible("#warp.show"))
        check("Da ghi cache 'da xem'",
              page.evaluate("() => localStorage.getItem('astroq-tour-seen') === '1'"))

        # Đoạn tăng tốc: đếm pixel vệt sao ở vùng RÌA màn hình (xa điểm tụ)
        page.wait_for_timeout(1500)
        lead1 = page.inner_text(".warp-cap .lead")
        check("Chu bao dang khoi dong dong co", "khởi động động cơ" in lead1.lower(), lead1)
        streaks = left_lit(page)
        page.screenshot(path="scratchpad/w01-warp.png")

        # Đợi tới lúc dừng ở Trái Đất
        page.wait_for_timeout(2600)
        lead2 = page.inner_text(".warp-cap .lead")
        check("Chu doi thanh 'da vao quy dao Trai Dat'",
              "quỹ đạo trái đất" in lead2.lower(), lead2)
        bar = page.evaluate("() => document.querySelector('.warp-bar i').style.width")
        check("Thanh tien trinh day 100%", bar == "100%", bar)

        stopped = left_lit(page)
        check("Luc tang toc sang hon han luc da dung (vet sao la vet, khong phai dom)",
              streaks > stopped * 2, f"tang toc {streaks} px vs da dung {stopped} px")

        # Trái Đất: đo pixel xanh-lam quanh điểm tụ
        earth = page.evaluate("""() => {
            const cv = document.querySelector('#warp canvas');
            const g = cv.getContext('2d');
            const dpr = cv.width / window.innerWidth;
            const portrait = window.innerHeight > window.innerWidth;
            const cx = window.innerWidth * (portrait ? .58 : .70) * dpr;
            const cy = window.innerHeight * (portrait ? .40 : .48) * dpr;
            const R  = Math.min(window.innerWidth, window.innerHeight) * (portrait ? .30 : .26) * dpr;
            const rd = Math.round(R*0.8);
            const d = g.getImageData(Math.round(cx-rd), Math.round(cy-rd), rd*2, rd*2).data;
            let blue = 0, green = 0, tot = 0;
            for(let i=0;i<d.length;i+=4){
              const r=d[i], gg=d[i+1], b=d[i+2]; tot++;
              if(b > 70 && b > r + 25) blue++;
              if(gg > 80 && gg > b + 10 && gg > r + 20) green++;
            }
            return { blue, green, tot, R: Math.round(R/dpr) };
        }""")
        check("Trai Dat: phan lon la dai duong xanh-lam",
              earth["blue"] > earth["tot"] * 0.45,
              f"{earth['blue']}/{earth['tot']} px lam, R={earth['R']}px")
        check("Trai Dat: co luc dia mau xanh la", earth["green"] > 400,
              f"{earth['green']} px")

        # Luna đậu cạnh Trái Đất, phía BÊN TRÁI hành tinh
        luna = page.evaluate("""() => {
            const cv = document.querySelector('#warp canvas');
            const g = cv.getContext('2d');
            const dpr = cv.width / window.innerWidth;
            const portrait = window.innerHeight > window.innerWidth;
            const cx = window.innerWidth * (portrait ? .58 : .70) * dpr;
            const cy = window.innerHeight * (portrait ? .40 : .48) * dpr;
            const R  = Math.min(window.innerWidth, window.innerHeight) * (portrait ? .30 : .26) * dpr;
            // o vuong ben trai hanh tinh, ngang tam noi Luna dau
            const x0 = Math.max(0, Math.round(cx - R - 190*dpr));
            const y0 = Math.round(cy + R*0.42 - 60*dpr);
            const w = Math.round(190*dpr), h = Math.round(120*dpr);
            const d = g.getImageData(x0, y0, w, h).data;
            let lit = 0;
            for(let i=0;i<d.length;i+=4){ if(d[i]+d[i+1]+d[i+2] > 330) lit++; }
            return { lit, px: w*h };
        }""")
        check("Luna dau ben trai Trai Dat (co khoi pixel sang)",
              luna["lit"] > 300, f"{luna['lit']} px sang / {luna['px']}")
        page.screenshot(path="scratchpad/w02-earth.png")

        # Tự tắt và trả lại dashboard
        page.wait_for_timeout(1600)
        check("Man loading tu tat", not page.is_visible("#warp.show"))
        # Ý của phép kiểm này là "màn loading tắt xong thì dashboard còn nguyên", nên
        # đếm > 0 chứ ĐỪNG gán cứng số card: dashboard lên 6 card ngày 29/07/2026 và
        # con số 3 làm nó báo hỏng trong khi trang vẫn đúng. Số card đã có phép kiểm
        # riêng ở check_pages.py mục [7b].
        n_cards = page.eval_on_selector_all(".cards .hud", "e=>e.length")
        check("Dashboard dung nguyen ven (cac card HUD con day)",
              n_cards >= 3, f"{n_cards} card")
        ctx.close()

        # ══════════════ 3. Vào lại thì KHÔNG dẫn tham quan nữa ══════════════
        print("\n[3] Vao lai (da xem) — khong dan tham quan nua")
        ctx, page = new_page(browser, "vi", seen=True)
        page.goto(BASE, wait_until="load")
        page.wait_for_timeout(2500)
        check("Khong hien box thoai", not page.is_visible("#tour.show"))
        check("Khong hien man loading", not page.is_visible("#warp.show"))
        # scrollIntoView trước khi đo: elementFromPoint tính theo KHUNG NHÌN, mà nút
        # này nằm dưới mép dưới ở màn 900px kể từ khi cột stat có thêm đường vào
        # Kho Mẫu Vật (29/07/2026).
        check("Bam duoc nut tren dashboard",
              page.evaluate("""() => { const b=document.getElementById('btn-game');
                       b.scrollIntoView({block:'center'});
                       const r=b.getBoundingClientRect();
                       const t=document.elementFromPoint(r.x+r.width/2, r.y+r.height/2);
                       return b.contains(t) || b === t; }"""))
        ctx.close()

        # ══════════════ 4. Tiếng Anh + đổi ngôn ngữ giữa tour ══════════════
        print("\n[4] Tieng Anh + doi ngon ngu giua tour")
        ctx, page = new_page(browser, "en")
        page.goto(BASE, wait_until="load")
        page.wait_for_selector("#tour.show", timeout=8000)
        check("EN: loi chao dich", "Welcome" in page.inner_text(".tour-title"),
              page.inner_text(".tour-title").replace("\n", " "))
        check("EN: nut 'Start the tour'", "Start the tour" in page.inner_text(".tour-next"),
              page.inner_text(".tour-next"))
        page.click(".tour-next"); page.wait_for_timeout(650)
        check("EN: buoc Galaxy Map", "Galaxy Map" in page.inner_text(".tour-title"),
              page.inner_text(".tour-title").replace("\n", " "))

        # Nút VI/EN của trang bị CHẶN trong lúc tour mở (cố ý: bấm ra ngoài là
        # mất mạch giới thiệu). Kiểm đúng điều đó, rồi thử đường đồng bộ THẬT:
        # đổi ngôn ngữ ở TAB KHÁC → event `storage` → applyLang → tour vẽ lại.
        # ⚠️ ĐO Ở NÚT THU GỌN (`[data-menu-btn]`), khong o nut VI/EN nua: tu
        #    15/08/2026 hai nut do nam TRONG tam tha dang `hidden`, ma phan tu an
        #    cho ra khung 0x0 -> `elementFromPoint` do o goc man hinh, tuc phep do
        #    khong con noi gi ve cai nut that. Cai tre bam duoc la nut thu gon.
        blocked = page.evaluate("""() => {
            const b = document.querySelector('.lang-pick [data-menu-btn]');
            const r = b.getBoundingClientRect();
            const top = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
            return top ? top.className : null; }""")
        check("Nut VI/EN bi chan trong luc tour mo (co y)",
              "tour-block" in (blocked or ""), str(blocked))

        tab2 = ctx.new_page()
        tab2.goto("http://127.0.0.1:8123/dashboard.html", wait_until="load")
        # Tab thứ hai cũng tự mở tour (cùng localStorage) — chờ nó mở XONG rồi dẹp
        # lớp phủ của NÓ đi, để chỉ còn kiểm đúng một thứ: đường đồng bộ ngôn ngữ
        # giữa 2 tab. (Dẹp trước khi nó mở thì #tour còn chưa tồn tại.)
        tab2.wait_for_selector("#tour.show", timeout=8000)
        tab2.evaluate("() => { document.getElementById('tour').style.display='none'; }")
        tab2.click('.lang-pick [data-menu-btn]')   # mo tam tha truoc
        tab2.wait_for_selector('.lang-pick [data-menu-pop]:not([hidden])')
        tab2.click('.lang-switch button[data-lang="vi"]')
        page.wait_for_timeout(600)
        check("Tab khac doi sang VI: box thoai dich theo ngay",
              "Bản đồ Thiên Hà" in page.inner_text(".tour-title"),
              page.inner_text(".tour-title").replace("\n", " "))
        check("Doi ngon ngu KHONG lam mat buoc dang xem",
              page.evaluate("() => [...document.querySelectorAll('.tour-dots span')]"
                            ".findIndex(s=>s.classList.contains('on')) === 1"))
        tab2.click('.lang-pick [data-menu-btn]')
        tab2.wait_for_selector('.lang-pick [data-menu-pop]:not([hidden])')
        tab2.click('.lang-switch button[data-lang="en"]')
        page.wait_for_timeout(600)
        check("Doi lai EN: box thoai dich theo",
              "Galaxy Map" in page.inner_text(".tour-title"),
              page.inner_text(".tour-title").replace("\n", " "))
        tab2.close()
        # Bỏ qua giữa tour → vẫn sang màn loading, và chữ màn loading là EN
        page.click(".tour-skip")
        page.wait_for_timeout(600)
        check("Bo qua giua tour thi dong tour", not page.is_visible("#tour.show"))
        play_warp(page)
        check("EN: chu man loading dich",
              "engines" in page.inner_text(".warp-cap .lead").lower(),
              page.inner_text(".warp-cap .lead"))
        check("Bo qua cung ghi 'da xem'",
              page.evaluate("() => localStorage.getItem('astroq-tour-seen') === '1'"))
        # Nút "Bỏ qua ›" của màn loading
        page.click(".warp-skip")
        page.wait_for_timeout(900)
        check("Nut Bo qua tat man loading ngay", not page.is_visible("#warp.show"))
        ctx.close()

        # ══════════════ 5. Điện thoại 390×844 ══════════════
        print("\n[5] Dien thoai 390x844")
        ctx, page = new_page(browser, "vi", mobile=True)
        page.goto(BASE, wait_until="load")
        page.wait_for_selector("#tour.show", timeout=8000)
        for key in ORDER[1:-1]:   # bo buoc chao va buoc cuoi (ca hai khong tro vao dau)
            page.click(".tour-next")
            wait_stable(page)
            bub = box(page, ".tour-bubble")
            check(f"[dt/{key}] box thoai nam trong man hinh",
                  bub and bub["x"] >= 4 and bub["x"] + bub["w"] <= 386
                  and bub["y"] >= 4 and bub["y"] + bub["h"] <= 840,
                  str(bub))
            tb, hb = box(page, TARGET[key]), box(page, ".tour-hole")
            check(f"[dt/{key}] o sang trum dung khu vuc",
                  tb and hb and abs((tb["y"] - 8) - hb["y"]) <= 2
                  and abs((tb["h"] + 16) - hb["h"]) <= 2,
                  f"target={tb} hole={hb}")
        check("Khong tran ngang",
              page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1"),
              str(page.evaluate("() => document.documentElement.scrollWidth")))
        page.screenshot(path="scratchpad/w03-mobile.png")
        page.click(".tour-next")
        page.wait_for_timeout(400)
        play_warp(page)          # tour không còn tự dẫn sang màn loading — xem play_warp()
        page.wait_for_timeout(4200)
        m = page.evaluate("""() => {
            const cv = document.querySelector('#warp canvas');
            const g = cv.getContext('2d');
            const dpr = cv.width / window.innerWidth;
            const cx = window.innerWidth * .58 * dpr, cy = window.innerHeight * .40 * dpr;
            const R = Math.min(window.innerWidth, window.innerHeight) * .30 * dpr;
            const rd = Math.round(R*0.8);
            const d = g.getImageData(Math.round(cx-rd), Math.round(cy-rd), rd*2, rd*2).data;
            let blue=0, tot=0;
            for(let i=0;i<d.length;i+=4){ tot++; if(d[i+2] > 70 && d[i+2] > d[i]+25) blue++; }
            const capTop = document.querySelector('.warp-cap').getBoundingClientRect().top;
            return { blue, tot, capTop, earthBottom: (cy+R)/dpr };
        }""")
        check("[dt] Trai Dat van hien du", m["blue"] > m["tot"] * 0.45,
              f"{m['blue']}/{m['tot']}")
        check("[dt] Chu o day KHONG de len Trai Dat", m["capTop"] > m["earthBottom"],
              f"capTop={round(m['capTop'])} earthBottom={round(m['earthBottom'])}")
        page.screenshot(path="scratchpad/w04-mobile-earth.png")
        ctx.close()

        # ══════════════ 6. prefers-reduced-motion ══════════════
        print("\n[6] prefers-reduced-motion")
        ctx, page = new_page(browser, "vi", reduced=True)
        page.goto(BASE, wait_until="load")
        page.wait_for_selector("#tour.show", timeout=8000)
        # 7 bước → 6 lần bấm để tới bước cuối, cộng 1 lần nữa mới rời tour
        for _ in range(len(ORDER)):
            page.click(".tour-next")
            page.wait_for_timeout(220)
        play_warp(page)
        check("[rm] Van di het tour va bat duoc man loading", page.is_visible("#warp.show"))
        page.wait_for_timeout(400)
        rm = page.evaluate("""() => {
            const cv = document.querySelector('#warp canvas');
            const g = cv.getContext('2d');
            const dpr = cv.width / window.innerWidth;
            const cx = window.innerWidth * .70 * dpr, cy = window.innerHeight * .48 * dpr;
            const R = Math.min(window.innerWidth, window.innerHeight) * .26 * dpr;
            const rd = Math.round(R*0.8);
            const d = g.getImageData(Math.round(cx-rd), Math.round(cy-rd), rd*2, rd*2).data;
            let blue=0, tot=0;
            for(let i=0;i<d.length;i+=4){ tot++; if(d[i+2] > 70 && d[i+2] > d[i]+25) blue++; }
            // 40% ben trai: khong duoc co vet sao dai (chi con dom sao dung yen)
            const e = g.getImageData(0,0,Math.round(cv.width*0.4),cv.height).data;
            let lit=0; for(let i=0;i<e.length;i+=4){ if(e[i]+e[i+1]+e[i+2] > 200) lit++; }
            return { blue, tot, edge: lit };
        }""")
        check("[rm] Trai Dat hien NGAY o co that (khong co doan phong to)",
              rm["blue"] > rm["tot"] * 0.45, f"{rm['blue']}/{rm['tot']}")
        # So với chính lượt bình thường (cùng khung 1440×900, cùng cửa sổ đo)
        # thay vì một ngưỡng tự đặt: chứng minh được "ít sáng hơn hẳn vì không có vệt".
        check("[rm] Khong co vet sao warp (it sang hon han luc tang toc)",
              rm["edge"] < streaks * 0.4, f"{rm['edge']} px vs tang toc {streaks} px")
        page.wait_for_timeout(1800)
        check("[rm] Man loading ket thuc som", not page.is_visible("#warp.show"))
        ctx.close()

        # ══════════════ 7. AstroQTour.reset() để xem lai ══════════════
        print("\n[7] AstroQTour.reset() de xem lai")
        ctx, page = new_page(browser, "vi", touch_seen=False)
        page.goto(BASE, wait_until="load")
        page.wait_for_selector("#tour.show", timeout=8000)
        check("Chua co co thi tour hien", page.is_visible("#tour.show"))
        # Xem hết một lượt → cờ được ghi → F5 thì không hiện nữa
        page.evaluate("() => { for(let i=0;i<12;i++){ const b=document.querySelector('.tour-next');"
                      " if(!b) break; b.click(); } }")   # so buoc doi thi khong phai sua so o day
        page.wait_for_timeout(400)
        page.evaluate("() => AstroQWarp.stop()")
        page.reload(wait_until="load")
        page.wait_for_timeout(1500)
        check("Xem xong roi F5 thi khong hien lai", not page.is_visible("#tour.show"))
        page.evaluate("() => AstroQTour.reset()")
        page.wait_for_timeout(600)
        check("reset() xoa cache trong may",
              page.evaluate("() => localStorage.getItem('astroq-tour-seen') === null"))
        page.reload(wait_until="load")
        page.wait_for_selector("#tour.show", timeout=8000)
        check("Sau reset + F5 thi tour hien lai", page.is_visible("#tour.show"))
        ctx.close()

        # ══════════════ 8. Cờ tourSeen lấy từ SERVER (đổi máy) ══════════════
        # Đây là lý do tồn tại của /me/onboarding: máy mới thì cache trong máy
        # rỗng, nếu chỉ tin localStorage thì người đã xem sẽ phải xem lại.
        # Thay AstroQAuth bằng bản giả để kiểm đúng nhánh quyết định, không phải
        # đăng nhập Firebase thật (API đã có bộ test riêng: test_onboarding.py).
        print("\n[8] Co tourSeen lay tu server (may moi, cache rong)")
        for seen_on_server, expect_tour in ((True, False), (False, True)):
            ctx, page = new_page(browser, "vi", touch_seen=False)
            page.add_init_script(
                # Cài bằng getter/setter, KHÔNG gán thẳng: js/firebase-auth.js là
                # ES module nên chạy SAU và `window.AstroQAuth = …` của nó sẽ đè
                # mất bản giả (đúng bẫy đã dính — PUT đi vào module thật, không
                # phải bản giả). Setter nuốt lời gán đó, và vì có setter nên
                # module ở strict mode không bị ném TypeError.
                "localStorage.removeItem('astroq-tour-seen');"
                "window.__calls = [];"
                # ⚠️ BẢN GIẢ PHẢI ĐỦ `postProgress` VÀ `getMissions`. Từ 01/08/2026
                #    dashboard đi qua `earthDoneGuide()` trước khi mở tour, mà hàm đó gọi
                #    `AstroQProgress.missions()` → `waitAuth(2500)` tìm
                #    `AstroQAuth.postProgress`. Bản giả thiếu nó thì waitAuth **chờ hết
                #    2,5 giây** rồi mới trả null, tour hiện ra SAU mốc đo 2,2s và phép
                #    kiểm báo hỏng oan. Đây là lỗi của BẢN GIẢ, không phải của sản phẩm —
                #    cùng loại bẫy đã ghi 3 lần với bản giả `AstroQAuth`/`AstroQProgress`.
                # ⚠️ `map01Seen:true` để `mapFirst()` không đẩy sang bản đồ; bộ này đo tour.
                "const __stub = {"
                "  postProgress: async () => ({ ok:false, reason:'stub' }),"
                "  getMissions: async () => ({ ok:false, reason:'stub' }),"
                "  getOnboarding: async () => { window.__calls.push('get');"
                "    return { ok:true, tourSeen:%s, map01Seen:true, earth1Greeted:true }; },"
                "  setOnboarding: async (v) => { window.__calls.push('set:'+v);"
                "    return { ok:true, tourSeen:v }; }"
                "};"
                "Object.defineProperty(window, 'AstroQAuth', {"
                "  get: () => __stub, set: () => {}, configurable: true });"
                % ("true" if seen_on_server else "false")
            )
            page.goto(BASE, wait_until="load")
            page.wait_for_timeout(2200)
            shown = page.is_visible("#tour.show")
            check(f"server tourSeen={seen_on_server} -> {'hien' if expect_tour else 'KHONG hien'} tour",
                  shown == expect_tour, f"hien={shown}")
            check(f"server tourSeen={seen_on_server} -> co goi GET /me/onboarding",
                  "get" in page.evaluate("() => window.__calls"),
                  str(page.evaluate("() => window.__calls")))
            if seen_on_server:
                check("Server noi da xem -> ghi cache vao may cho lan sau",
                      page.evaluate("() => localStorage.getItem('astroq-tour-seen') === '1'"))
            else:
                # Xem hết → phải ĐẨY cờ lên server, không chỉ ghi vào máy
                page.evaluate("() => { for(let i=0;i<12;i++){ const b=document.querySelector('.tour-next');"
                      " if(!b) break; b.click(); } }")   # so buoc doi thi khong phai sua so o day
                page.wait_for_timeout(700)
                check("Xem xong -> PUT co len server",
                      "set:true" in page.evaluate("() => window.__calls"),
                      str(page.evaluate("() => window.__calls")))
            ctx.close()

        browser.close()

    # Lỗi console — bỏ qua tiếng ồn không phải của mình
    noise = ("favicon", "net::ERR_INTERNET_DISCONNECTED")
    real = [e for e in errors if not any(n in e for n in noise)]
    print(f"\n[console] {len(real)} loi")
    for e in real[:12]:
        print("   -", e[:220])
    check("0 loi console", len(real) == 0, f"{len(real)} loi")

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
