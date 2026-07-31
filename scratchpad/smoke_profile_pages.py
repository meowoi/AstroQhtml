# -*- coding: utf-8 -*-
"""
smoke_profile_pages.py — chơi THẬT trang Hồ sơ + Kho Thành Tích trên Chromium.

    python -m http.server 8123      (trong AstroQhtml/)
    python scratchpad/smoke_profile_pages.py

Không đăng nhập Firebase thật (API đã có bộ test riêng: test_profile.py). Ở đây
thay `window.AstroQAuth` bằng bản giả để kiểm ĐÚNG phần giao diện: vẽ đúng số
server trả về, đổi tên/trang phục gửi đúng patch lên API, mất mạng thì hiện dải
nhắc chứ không bịa số, và các điểm sinh dữ liệu gửi đúng sự kiện.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123/"
ok_n, bad_n = 0, 0
errors = []

USER = {"name": "Bi Bo", "pilotName": "Bi Bo", "character": "m",
        "selectedCharacter": "m", "avatar": "ava/avam.png",
        "email": "bibo@astroq-test.invalid", "uid": "UID1234ABCD5678"}

# Dữ liệu server giả — cố ý dùng số "lạ" để phân biệt với số bịa cũ của dashboard
SERVER = {
    "profile": {"uid": "UID1234ABCD5678", "name": "Bi Bo", "email": USER["email"],
                "character": "cu", "avatar": "ava/avacu.png",
                "createdAt": "2026-03-14T08:00:00.000Z", "tourSeen": True},
    "wallet": {"meteors": 41},
    "level": {"level": 7, "xp": 2340, "xpInLevel": 240, "xpForNext": 700, "pct": 34},
    "progress": {"xp": 2340, "quizTaken": 9, "quizAnswered": 45, "quizCorrect": 39,
                 "quizPerfect": 2, "quizAccuracy": 87, "gamesPlayed": 13,
                 "lessonsRead": 6, "flightSeconds": 4620, "meteorsEarned": 233,
                 "planets": ["earth", "mars", "venus"],
                 "bests": {"dodge": 412, "defender": 655, "constellation": 1},
                 "badgesEarned": 8, "updatedAt": "2026-07-29T05:00:00.000Z"},
}
BADGES = [
    {"id": "first-quiz", "group": "learn", "goal": 1, "current": 1, "earned": True,
     "earnedAt": "2026-07-20T10:00:00.000Z"},
    {"id": "quiz-correct-10", "group": "learn", "goal": 10, "current": 10, "earned": True,
     "earnedAt": "2026-07-22T10:00:00.000Z"},
    {"id": "quiz-correct-50", "group": "learn", "goal": 50, "current": 39, "earned": False,
     "earnedAt": None},
    {"id": "first-game", "group": "train", "goal": 1, "current": 1, "earned": True,
     "earnedAt": "2026-07-21T10:00:00.000Z"},
    {"id": "game-50", "group": "train", "goal": 50, "current": 13, "earned": False,
     "earnedAt": None},
    {"id": "dodge-300", "group": "train", "goal": 300, "current": 300, "earned": True,
     "earnedAt": "2026-07-28T10:00:00.000Z"},
    {"id": "planet-3", "group": "explore", "goal": 3, "current": 3, "earned": True,
     "earnedAt": "2026-07-29T04:00:00.000Z"},
    {"id": "planet-8", "group": "explore", "goal": 8, "current": 3, "earned": False,
     "earnedAt": None},
    {"id": "level-5", "group": "level", "goal": 5, "current": 5, "earned": True,
     "earnedAt": "2026-07-27T10:00:00.000Z"},
    {"id": "level-20", "group": "level", "goal": 20, "current": 7, "earned": False,
     "earnedAt": None},
]
ACH = {"level": SERVER["level"], "progress": SERVER["progress"], "newBadges": [],
       "achievements": {"summary": {"earned": 6, "total": len(BADGES)}, "badges": BADGES}}


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def stub(mode="ok"):
    """Bản giả của window.AstroQAuth.

    Cài bằng getter/setter, KHÔNG gán thẳng: js/firebase-auth.js là ES module nên
    chạy SAU script cổ điển và sẽ đè mất bản giả (đã dính đúng bẫy này ở
    smoke_onboard.py). Setter nuốt lời gán nên module strict mode không ném lỗi.
    """
    fail = "{ ok:false, reason:'%s' }" % ("auth" if mode == "auth" else "net")
    body = f"""
      window.__calls = [];
      const OK = {json.dumps(mode == "ok")};
      const stub = {{
        idToken: async () => OK ? "tok" : null,
        getOnboarding: async () => ({{ ok:true, tourSeen:true }}),
        setOnboarding: async () => ({{ ok:true, tourSeen:true }}),
        getProfile: async () => {{ window.__calls.push("getProfile");
          return OK ? {{ ok:true, data:{json.dumps(SERVER)} }} : {fail}; }},
        getAchievements: async () => {{ window.__calls.push("getAchievements");
          return OK ? {{ ok:true, data:{json.dumps(ACH)} }} : {fail}; }},
        updateProfile: async (p) => {{ window.__calls.push("updateProfile:" + JSON.stringify(p));
          return OK ? {{ ok:true, data:{{ profile:p }} }} : {fail}; }},
        postProgress: async (e) => {{ window.__calls.push("postProgress:" + JSON.stringify(e));
          return OK ? {{ ok:true, data:{{ counted:true }} }} : {fail}; }}
      }};
      Object.defineProperty(window, "AstroQAuth",
        {{ get: () => stub, set: () => {{}}, configurable: true }});
    """
    return body


def new_page(browser, lang="vi", mode="ok", mobile=False, reduced=False, extra=""):
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
        "localStorage.removeItem('astroq-progress');"
        "localStorage.removeItem('astroq-progress-queue');"
        + extra + stub(mode)
    )
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    return ctx, page


def txt(page, sel):
    return page.inner_text(sel).strip()


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ══════════════ 1. profile.html — số của server ══════════════
        print("\n[1] profile.html — ve dung so server tra ve")
        ctx, page = new_page(browser)
        page.goto(BASE + "profile.html", wait_until="load")
        page.wait_for_function("() => (window.__calls||[]).includes('getProfile')", timeout=8000)
        page.wait_for_timeout(500)

        check("Ten phi hanh gia", txt(page, "#pilot-name") == "Bi Bo", txt(page, "#pilot-name"))
        check("Cap do tu server (7)", txt(page, "#lv-num") == "7", txt(page, "#lv-num"))
        check("XP trong cap 240/700",
              txt(page, "#xp-in") == "240" and txt(page, "#xp-span") == "700",
              txt(page, "#xp-in") + "/" + txt(page, "#xp-span"))
        check("Con 460 XP nua len cap 8", "460" in txt(page, "#xp-next") and "8" in txt(page, "#xp-next"),
              txt(page, "#xp-next"))
        w = page.evaluate("() => document.querySelector('#xp-bar').style.width")
        check("Thanh XP dung 34%", w == "34%", w)
        # Vòng cấp độ: chu vi 2π·45 = 282.7 → offset = 282.7·(1−0.34)
        off = page.evaluate("() => +document.querySelector('#lv-ring').getAttribute('stroke-dashoffset')")
        check("Vong cap do ve dung 34%", abs(off - 282.7 * 0.66) < 2, f"offset={off}")

        # Nhân vật lấy theo server ("cu" = Moros), KHÔNG phải theo localStorage ("m")
        check("Nhan vat theo SERVER (cu/Moros), khong theo may (m/Comet)",
              "cu3d" in page.get_attribute("#pilot-model", "src"),
              page.get_attribute("#pilot-model", "src"))
        check("Chuc vu doc tu js/characters.js", "thiên văn" in txt(page, "#pilot-role").lower(),
              txt(page, "#pilot-role"))
        check("Ngay gia nhap dinh dang vi", txt(page, "#joined-at") == "14/03/2026",
              txt(page, "#joined-at"))
        check("Ma ho so tu uid", txt(page, "#pilot-id") == "AQ-UID1-234A", txt(page, "#pilot-id"))

        stats = txt(page, "#stats")
        # 4620 giay = 1,3 gio. Ca profile.html va dashboard.html deu doi sang GIO
        # khi >= 1 gio, chi duoi 1 gio moi hien phut.
        for want in ("1.3", "9", "87%", "13", "6", "233", "8", "3/8"):
            check(f"Thong ke co '{want}'", want in stats)
        check("Thoi gian bay >= 1 gio thi hien GIO", "giờ" in stats.lower(),
              stats.replace("\n", " · "))

        check("Hanh trinh: 3/8 hanh tinh", txt(page, "#route-count") == "3/8",
              txt(page, "#route-count"))
        on = page.eval_on_selector_all(".stop.on .nm", "e => e.map(x => x.textContent)")
        check("Dung 3 hanh tinh sang: Trai Dat, Sao Hoa, Sao Kim",
              set(on) == {"Trái Đất", "Sao Hoả", "Sao Kim"}, str(on))
        recs = txt(page, "#recs")
        check("Ky luc tu server (412 / 655 / 1)",
              "412" in recs and "655" in recs and "1" in recs, recs.replace("\n", " · "))
        check("Khong hien dai nhac khi co server",
              not page.is_visible("#offline.show"))
        # Nhãn ô thống kê không được cắt đuôi. `minmax(148px,1fr)` ban đầu cho 4 cột
        # trên desktop và cắt mất "LƯỢT HUẤN LUY…", "HÀNH TINH ĐÃ …" — nhìn ảnh mới thấy.
        cut = page.evaluate("""() => [...document.querySelectorAll('.kv .cell .k')]
            .filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.textContent)""")
        check("Nhan o thong ke khong bi cat duoi", cut == [], str(cut))
        page.screenshot(path="scratchpad/p01-profile.png", full_page=True)

        # ---- Đổi trang phục ----
        print("\n[2] profile.html — doi trang phuc + doi ten")
        page.click('.suit[data-id="chim"]')
        page.wait_for_timeout(500)
        calls = page.evaluate("() => window.__calls")
        put = [c for c in calls if c.startswith("updateProfile:")]
        check("Bam trang phuc -> goi PUT /me/profile", len(put) == 1, str(put))
        check("Patch chi gui character + avatar",
              put and json.loads(put[0].split(":", 1)[1]) == {"character": "chim",
                                                              "avatar": "ava/avachim.png"},
              put[0] if put else "")
        check("Anh 3D doi ngay khong cho mang",
              "chim3D" in page.get_attribute("#pilot-model", "src"),
              page.get_attribute("#pilot-model", "src"))
        check("O trang phuc duoc danh dau chon",
              page.eval_on_selector_all(".suit.on", "e => e.length") == 1)
        check("Luu ca vao may (astroq-user)",
              page.evaluate("() => JSON.parse(localStorage.getItem('astroq-user')).character") == "chim")
        check("Bam lai chinh o dang chon -> KHONG goi API lan nua",
              (page.click('.suit[data-id="chim"]'), page.wait_for_timeout(300),
               len([c for c in page.evaluate("() => window.__calls") if c.startswith("updateProfile")]))[2] == 1)

        page.fill("#new-name", "Bi Bo Bo")
        page.click("#save-name")
        page.wait_for_timeout(400)
        put2 = [c for c in page.evaluate("() => window.__calls") if c.startswith("updateProfile:")]
        check("Doi ten -> goi PUT voi dung mot truong name",
              len(put2) == 2 and json.loads(put2[1].split(":", 1)[1]) == {"name": "Bi Bo Bo"},
              str(put2[-1:]))
        check("Ten tren the doi ngay", txt(page, "#pilot-name") == "Bi Bo Bo")
        page.fill("#new-name", "   ")
        page.click("#save-name")
        page.wait_for_timeout(300)
        check("Ten rong -> khong goi API, hien toast",
              len([c for c in page.evaluate("() => window.__calls") if c.startswith("updateProfile")]) == 2
              and page.is_visible("#toast.show"))
        ctx.close()

        # ══════════════ 3. achievements.html ══════════════
        print("\n[3] achievements.html — huy hieu")
        ctx, page = new_page(browser)
        page.goto(BASE + "achievements.html", wait_until="load")
        page.wait_for_function("() => (window.__calls||[]).includes('getAchievements')", timeout=8000)
        page.wait_for_timeout(500)

        check("Vong tong quan 6/10 = 60%", txt(page, "#aw-pct") == "60%", txt(page, "#aw-pct"))
        check("Dong tom tat 6/10", "6" in txt(page, "#ov-h") and "10" in txt(page, "#ov-h"),
              txt(page, "#ov-h"))
        check("Con 4 huy hieu dang cho", "4" in txt(page, "#ov-p"), txt(page, "#ov-p"))
        check("Ve dung 10 the huy hieu",
              page.eval_on_selector_all(".badge", "e => e.length") == 10)
        check("6 the da mo", page.eval_on_selector_all(".badge.on", "e => e.length") == 6)
        check("4 the chua mo", page.eval_on_selector_all(".badge.off", "e => e.length") == 4)
        check("Ten huy hieu doc tu js/badges.js (khong hien id tho)",
              "Tân Binh Hiếu Học" in txt(page, "#badges") and "first-quiz" not in txt(page, "#badges"))
        check("The chua mo hien tien do dang 39 / 50", "39 / 50" in txt(page, "#badges"),
              [t for t in txt(page, "#badges").split("\n") if "/" in t][:4])
        pw_ = page.evaluate("""() => {
            const b = [...document.querySelectorAll('.badge')].find(
                x => x.textContent.includes('Bộ Não Thiên Hà'));
            return b ? b.querySelector('.prog .bar i').style.width : null; }""")
        check("Thanh tien do 39/50 = 78%", pw_ == "78%", str(pw_))
        # ĐO CHIỀU CAO THẬT, không chỉ đọc style: .prog/.bar là <span> nên nếu
        # thiếu `display:block` thì height:6px bị bỏ qua và thanh biến mất khỏi
        # thẻ — style vẫn ghi "78%" nhưng mắt không thấy gì. Đã dính đúng lỗi này.
        box = page.evaluate("""() => {
            const b = [...document.querySelectorAll('.badge')].find(
                x => x.textContent.includes('Bộ Não Thiên Hà'));
            if(!b) return null;
            const bar = b.querySelector('.prog .bar'), fill = bar && bar.querySelector('i');
            return bar ? { h: bar.getBoundingClientRect().height,
                           w: bar.getBoundingClientRect().width,
                           fh: fill ? fill.getBoundingClientRect().height : 0,
                           fw: fill ? fill.getBoundingClientRect().width : 0 } : null; }""")
        check("Thanh tien do CO chieu cao that (>= 4px)",
              box and box["h"] >= 4, str(box))
        check("Phan da to mau rong ~78% thanh", box and box["w"] > 0
              and abs(box["fw"] / box["w"] - 0.78) < 0.03, str(box))
        check("Phan da to mau cung co chieu cao", box and box["fh"] >= 4, str(box))
        check("The da mo hien ngay mo", "20/07/2026" in txt(page, "#badges"))
        check("Da mo len TRUOC the chua mo",
              page.evaluate("""() => { const l=[...document.querySelectorAll('.badge')];
                  const lastOn = l.findLastIndex(x=>x.classList.contains('on'));
                  const firstOff = l.findIndex(x=>x.classList.contains('off'));
                  return lastOn < firstOff; }"""))
        groups = txt(page, "#groups")
        check("Chip nhom dem dung (Hoc tap 2/3)", "2/3" in groups, groups.replace("\n", " · "))
        page.screenshot(path="scratchpad/p02-awards.png", full_page=True)

        # ---- Bộ lọc ----
        print("\n[4] achievements.html — bo loc")
        page.click('#f-state button[data-v="on"]')
        page.wait_for_timeout(300)
        check("Loc 'Da mo' -> con 6 the",
              page.eval_on_selector_all(".badge", "e => e.length") == 6)
        check("Loc 'Da mo' -> khong con the .off",
              page.eval_on_selector_all(".badge.off", "e => e.length") == 0)
        page.click('#f-state button[data-v="off"]')
        page.wait_for_timeout(300)
        check("Loc 'Chua mo' -> con 4 the",
              page.eval_on_selector_all(".badge", "e => e.length") == 4)
        page.click('#f-group button[data-v="level"]')
        page.wait_for_timeout(300)
        check("Loc chua mo + nhom Cap do -> 1 the (level-20)",
              page.eval_on_selector_all(".badge", "e => e.length") == 1
              and "Thuyền Trưởng Luna" in txt(page, "#badges"), txt(page, "#badges"))
        page.click('#f-group button[data-v="learn"]')
        page.wait_for_timeout(300)
        check("Chua mo + Hoc tap -> 1 the", page.eval_on_selector_all(".badge", "e => e.length") == 1)
        page.click('#f-state button[data-v="on"]')
        page.click('#f-group button[data-v="explore"]')
        page.wait_for_timeout(300)
        check("Da mo + Kham pha -> 1 the (planet-3)",
              "Lữ Khách" in txt(page, "#badges"), txt(page, "#badges"))
        # tổ hợp không có gì
        page.click('#f-state button[data-v="off"]')
        page.click('#f-group button[data-v="level"]')
        page.click('#f-state button[data-v="on"]')
        page.wait_for_timeout(300)
        check("Da mo + Cap do -> 1 the (level-5)", "Phi Hành Gia Cấp 5" in txt(page, "#badges"))

        # ---- Bộ sưu tập ----
        print("\n[5] achievements.html — bo suu tap")
        check("Hanh tinh 3/8", txt(page, "#pl-count") == "3/8", txt(page, "#pl-count"))
        check("3 chip hanh tinh sang",
              page.eval_on_selector_all("#planets .chip.on", "e => e.length") == 3)
        check("Chua ghep chom sao -> hien o rong",
              page.is_visible("#consts-empty"))
        ctx.close()

        # ══════════════ 6. Chòm sao: khoa THAT + server uu tien ══════════════
        # ⚠️ Khoá là id trong mảng SKY của game ("ursa-major", "orion"…), KHÔNG phải
        # tên tiếng Việt. Bản đầu cả TRANG và TEST đều dùng tên tiếng Việt nên bộ sưu
        # tập luôn 0/4 với người chơi thật mà test không bắt được. Bài học: dữ liệu
        # dùng chung giữa 2 trang thì đọc lại chỗ GHI, đừng đoán theo giao diện.
        print("\n[6] Chom sao — doc tu ky luc trong may (khoa THAT)")
        ctx, page = new_page(browser, mode="net", extra=(
            "localStorage.setItem('astroq-constellation-best',"
            " JSON.stringify({'ursa-major':34,'orion':52}));"))
        page.goto(BASE + "achievements.html", wait_until="load")
        page.wait_for_timeout(2000)
        check("Hien 2/4 chom sao", txt(page, "#cs-count") == "2/4", txt(page, "#cs-count"))
        check("2 chip chom sao sang",
              page.eval_on_selector_all("#consts .chip.on", "e => e.length") == 2)
        check("Hien thoi gian ky luc 0:34", "0:34" in txt(page, "#consts"),
              txt(page, "#consts").replace("\n", " "))
        check("Hien TEN TIENG VIET (Dai Hung) nhung khoa la ursa-major",
              "Đại Hùng" in txt(page, "#consts"))
        check("Khong hien o rong nua", not page.is_visible("#consts-empty"))
        ctx.close()

        print("\n[6b] Chom sao — du lieu SERVER uu tien hon ky luc trong may")
        ctx, page = new_page(browser, extra=(
            # Máy chỉ có 1 chòm, server có 3 → phải lấy của server
            "localStorage.setItem('astroq-constellation-best',"
            " JSON.stringify({'ursa-major':99}));"))
        page.add_init_script("""
          const d = %s;
          d.progress.consts = { 'orion':21, 'scorpius':45, 'cassiopeia':60 };
          d.progress.constsDone = 3;
          const s = { idToken: async()=>"t",
            getOnboarding: async()=>({ok:true,tourSeen:true}), setOnboarding: async()=>({ok:true}),
            getAchievements: async()=>({ok:true,data:d}),
            getProfile: async()=>({ok:true,data:d}),
            getWallet: async()=>({ok:true,data:{meteors:41}}),
            updateProfile: async()=>({ok:true}), postProgress: async()=>({ok:true}),
            spendWallet: async()=>({ok:true,data:{meteors:36,spent:5}}) };
          Object.defineProperty(window,"AstroQAuth",{get:()=>s,set:()=>{},configurable:true});
        """ % json.dumps(ACH))
        page.goto(BASE + "achievements.html", wait_until="load")
        page.wait_for_timeout(2000)
        check("Lay 3 chom cua SERVER, khong phai 1 chom trong may",
              txt(page, "#cs-count") == "3/4", txt(page, "#cs-count"))
        check("Chom chi co trong may (Dai Hung) KHONG sang",
              page.evaluate("""() => { const c=[...document.querySelectorAll('#consts .chip')]
                  .find(x=>x.textContent.includes('Đại Hùng'));
                  return !!c && !c.classList.contains('on'); }"""))
        page.goto(BASE + "profile.html", wait_until="load")
        page.wait_for_timeout(1800)
        recs = txt(page, "#recs").replace("\n", " ")
        check("profile: ky luc Ghep Chom Sao = 3 chom (tu constsDone)",
              "Ghép Chòm Sao" in recs and " 3 " in recs.split("Ghép Chòm Sao")[-1] + " ",
              recs[-80:])
        ctx.close()

        # ══════════════ 6c. Vi: PHI do server quyet ══════════════
        print("\n[6c] Vi — Economy.spend chi gui TEN GAME len server")
        ctx, page = new_page(browser)
        page.goto(BASE + "game-dodge.html", wait_until="load")
        page.wait_for_timeout(1200)
        b0 = page.evaluate("() => Economy.getAsteroids()")
        page.evaluate("() => Economy.spend('dodge')")
        page.wait_for_timeout(600)
        b1 = page.evaluate("() => Economy.getAsteroids()")
        check("Cache tru ngay 5 tt (khong cho mang)", b1 == b0 - 5, f"{b0} -> {b1}")
        q = page.evaluate("() => JSON.parse(localStorage.getItem('astroq-progress-queue')||'[]')")
        check("Game khong co phien dang nhap -> xep hang cho, kem opId",
              len(q) == 1 and q[0].get("kind") == "spend" and q[0].get("game") == "dodge"
              and bool(q[0].get("opId")), str(q))
        check("Hang cho KHONG chua so tien (phi do server quyet)",
              q and not any(k in q[0] for k in ("amount", "fee", "cost", "meteors")), str(q[0]))
        check("Bang phi o client khop server (dodge=5, constellation=3)",
              page.evaluate("() => [Economy.feeFor('dodge'), Economy.feeFor('constellation')]")
              == [5, 3])
        page.evaluate("() => Economy.setFromServer(123)")
        check("setFromServer ghi de cache", page.evaluate("() => Economy.getAsteroids()") == 123)
        page.evaluate("() => Economy.setFromServer(-9)")
        check("setFromServer bo qua so rac (am)",
              page.evaluate("() => Economy.getAsteroids()") == 123)
        ctx.close()

        # ══════════════ 7. Mất mạng / chưa đăng nhập ══════════════
        for mode, label in (("net", "mat mang"), ("auth", "chua dang nhap")):
            print(f"\n[7.{mode}] {label} — hien dai nhac, KHONG bia so")
            ctx, page = new_page(browser, mode=mode)
            page.goto(BASE + "profile.html", wait_until="load")
            page.wait_for_timeout(2000)
            check(f"[{mode}] profile: hien dai nhac", page.is_visible("#offline.show"))
            check(f"[{mode}] profile: KHONG bia cap do (van la 1)",
                  txt(page, "#lv-num") == "1", txt(page, "#lv-num"))
            check(f"[{mode}] profile: van ve duoc the (ten tu may)",
                  txt(page, "#pilot-name") == "Bi Bo", txt(page, "#pilot-name"))
            check(f"[{mode}] profile: thong ke ve 0", "0%" in txt(page, "#stats"))
            if mode == "auth":
                check("[auth] dai nhac moi dang nhap", "Đăng nhập" in txt(page, "#offline"),
                      txt(page, "#offline"))
            else:
                check("[net] dai nhac noi khong ket noi duoc",
                      "máy chủ" in txt(page, "#offline"), txt(page, "#offline"))
            page.goto(BASE + "achievements.html", wait_until="load")
            page.wait_for_timeout(2000)
            check(f"[{mode}] awards: hien dai nhac", page.is_visible("#offline.show"))
            check(f"[{mode}] awards: KHONG hien the huy hieu nao (khong tu doan)",
                  page.eval_on_selector_all(".badge", "e => e.length") == 0)
            check(f"[{mode}] awards: bo suu tap hanh tinh van ve duoc",
                  page.eval_on_selector_all("#planets .chip", "e => e.length") == 8)
            ctx.close()

        # ══════════════ 8. Đổi ngôn ngữ ══════════════
        print("\n[8] Doi ngon ngu EN")
        ctx, page = new_page(browser, lang="en")
        page.goto(BASE + "achievements.html", wait_until="load")
        page.wait_for_timeout(1500)
        check("EN: tieu de trang", "Trophy Hold" in page.title(), page.title())
        check("EN: ten huy hieu dich", "Eager Rookie" in txt(page, "#badges"))
        check("EN: nhom dich", "Learning" in txt(page, "#groups"), txt(page, "#groups"))
        page.click('.lang-switch button[data-lang="vi"]')
        page.wait_for_timeout(400)
        check("Doi sang VI: ten huy hieu dich lai",
              "Tân Binh Hiếu Học" in txt(page, "#badges"))
        check("Doi ngon ngu KHONG lam mat bo loc dang chon",
              page.eval_on_selector_all("#f-state button.on", "e => e.length") == 1)
        page.goto(BASE + "profile.html", wait_until="load")
        page.wait_for_timeout(1500)
        page.click('.lang-switch button[data-lang="en"]')
        page.wait_for_timeout(400)
        check("EN: hanh tinh dich (Mars)", "Mars" in txt(page, "#route"), txt(page, "#route")[:80])
        # Nhãn `.kv .cell .k` có `text-transform:uppercase` nên innerText trả về
        # CHỮ HOA → phải so không phân biệt hoa/thường, không thì báo hỏng oan.
        check("EN: thong ke dich",
              "flight time" in txt(page, "#stats").lower(),
              txt(page, "#stats").replace("\n", " ")[:80])
        ctx.close()

        # ══════════════ 9. Điện thoại ══════════════
        print("\n[9] Dien thoai 390x844")
        for pg in ("profile.html", "achievements.html"):
            ctx, page = new_page(browser, mobile=True)
            page.goto(BASE + pg, wait_until="load")
            page.wait_for_timeout(1600)
            check(f"[dt] {pg}: khong tran ngang",
                  page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1"),
                  str(page.evaluate("() => document.documentElement.scrollWidth")))
            wide = page.evaluate("""() => [...document.querySelectorAll('.panel, .badge, .cell, .stop, .suit')]
                .filter(e => e.getBoundingClientRect().right > window.innerWidth + 1).length""")
            check(f"[dt] {pg}: khong khoi nao chia ra ngoai man hinh", wide == 0, f"{wide} khoi")
            page.screenshot(path=f"scratchpad/p03-{pg.replace('.html','')}-mobile.png", full_page=True)
            ctx.close()

        # ══════════════ 10. Dashboard dùng số thật ══════════════
        print("\n[10] dashboard.html — so that, khong con so bia")
        ctx, page = new_page(browser)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_function("() => (window.__calls||[]).includes('getAchievements')", timeout=8000)
        page.wait_for_timeout(600)
        check("XP tren header = 2340", txt(page, "#xp-val") == "2340", txt(page, "#xp-val"))
        check("Cap do = 7", txt(page, "#planet-level") == "7", txt(page, "#planet-level"))
        # ⚠️ TRUOC 31/07/2026 phep kiem nay doi nhan canh cap do la TEN HANH TINH vua
        #    ghe ("Sao Kim"). Nhan do da doi thanh TEN BAC huan luyen phi hanh gia,
        #    nen phep kiem cu dang BAO VE HANH VI CU — cung loai loi da giu nut Mat
        #    Trang song va da doi ten "Tri Thuc" bao hong. Nay doi dung bat bien moi:
        #    cap 7 nam trong khoang 6-10 => bac Cadet (js/ranks.js chia 5 cap/bac).
        check("Nhan canh cap do = TEN BAC, khong phai ten hanh tinh",
              txt(page, "#planet-name") == "Học Viên (Cadet)", txt(page, "#planet-name"))
        # Phep kiem thu hai: ten bac phai SUY RA TU CAP DO dang hien, khong phai mot
        # chuoi gan cung o dau do. Doc lai qua chinh js/ranks.js trong trang.
        check("ten bac khop dung cap do dang hien tren trang",
              page.evaluate("() => document.getElementById('planet-name').textContent"
                            " === AstroQRanks.name(+document.getElementById('planet-level')"
                            ".textContent, 'vi')"))
        check("Kham pha 3/8", txt(page, "#gx-unlocked") == "3", txt(page, "#gx-unlocked"))
        check("Pip sang dung 3", page.eval_on_selector_all("#gx-pips span.on", "e=>e.length") == 3)
        tiles = txt(page, "#stat-tiles")
        check("O thong ke: 1.3 gio / 87% / 6-10",
              "1.3" in tiles and "87%" in tiles and "6/10" in tiles,
              tiles.replace("\n", " · "))
        # Cùng một con số thì hai trang phải hiện CÙNG một chữ — bắt được thật:
        # profile.html ghi "1.3 giờ" còn dashboard.html ghi "1.3 Giờ".
        check("Dashboard va profile dung cung don vi thoi gian",
              "giờ" in tiles and "Giờ" not in tiles, tiles.replace("\n", " · "))
        check("Chuc vu duoi ten = Cap 7", "7" in txt(page, "#user-role"), txt(page, "#user-role"))
        log = txt(page, "#log-list")
        check("Nhat ky dung huy hieu THAT (Lu Khach mo gan nhat)", "Lữ Khách" in log,
              log.replace("\n", " · ")[:140])
        check("Nhat ky KHONG con dong bia 'Nha Du Hanh'", "Nhà Du Hành" not in log)
        check("Nhat ky co 4 dong", page.eval_on_selector_all(".log-item", "e=>e.length") == 4)
        check("Bam avatar -> profile.html",
              page.get_attribute(".user", "href") == "profile.html")
        check("Co nut mo Kho Thanh Tich",
              page.get_attribute(".sh-link", "href") == "achievements.html")
        check("The MOD-02 doi ten thanh Khu Huan Luyen",
              "Khu Huấn Luyện" in txt(page, ".card--game"), txt(page, ".card--game")[:60])
        page.screenshot(path="scratchpad/p04-dashboard.png", full_page=True)

        # Nhật ký rỗng khi chưa mở huy hiệu nào
        ctx.close()
        ctx, page = new_page(browser, extra="window.__noBadges = 1;")
        page.add_init_script("""
          const empty = { level:{level:1,xp:0,xpInLevel:0,xpForNext:100,pct:0},
            progress:{xp:0,quizAccuracy:0,gamesPlayed:0,lessonsRead:0,flightSeconds:0,
                      meteorsEarned:0,planets:[],bests:{},badgesEarned:0},
            newBadges:[], achievements:{ summary:{earned:0,total:20}, badges:[] } };
          const s = { idToken: async()=>"t", getOnboarding: async()=>({ok:true,tourSeen:true}),
            setOnboarding: async()=>({ok:true}),
            getAchievements: async()=>({ok:true,data:empty}),
            getProfile: async()=>({ok:true,data:{profile:{name:"Bi Bo"},level:empty.level,
                                                progress:empty.progress}}),
            updateProfile: async()=>({ok:true}), postProgress: async()=>({ok:true}) };
          Object.defineProperty(window,"AstroQAuth",{get:()=>s,set:()=>{},configurable:true});
        """)
        page.goto(BASE + "dashboard.html", wait_until="load")
        page.wait_for_timeout(2000)
        check("Chua mo huy hieu nao -> nhat ky hien o rong, khong bia dong nao",
              page.eval_on_selector_all(".log-empty", "e=>e.length") == 1
              and page.eval_on_selector_all(".log-item", "e=>e.length") == 0,
              txt(page, "#log-list"))
        ctx.close()

        # ══════════════ 11. Điểm sinh dữ liệu gửi đúng sự kiện ══════════════
        print("\n[11] Diem sinh du lieu gui dung su kien")
        # Quiz: trả lời hết một lượt thì báo type=quiz
        ctx, page = new_page(browser)
        page.goto(BASE + "quiz.html", wait_until="load")
        page.wait_for_timeout(1200)
        # Luong that cua quiz.html: chon dap an -> #engage (KICH HOAT) -> bang giai
        # thich #sheet -> #next-btn -> cau tiep. Lap den khi hien #summary.
        for i in range(40):
            if page.is_visible("#summary.show"):
                break
            try:
                if page.is_visible("#sheet.show"):
                    page.click("#next-btn", timeout=2000)
                elif not page.is_disabled("#engage"):
                    page.click("#engage", timeout=2000)
                else:
                    page.click("#q-options button:not([disabled])", timeout=2000)
            except Exception:
                pass
            page.wait_for_timeout(450)
        check("Quiz: den duoc bang tong ket", page.is_visible("#summary.show"))
        qcalls = [c for c in page.evaluate("() => window.__calls || []") if "postProgress" in c]
        check("Quiz: goi postProgress dung MOT lan", len(qcalls) == 1, str(qcalls))
        if qcalls:
            ev = json.loads(qcalls[0].split(":", 1)[1])
            check("Quiz: su kien type=quiz + co total", ev.get("type") == "quiz" and ev.get("total", 0) > 0,
                  str(ev))
            check("Quiz: KHONG gui xp/level/badges len",
                  not any(k in ev for k in ("xp", "level", "badges")), str(ev))
        ctx.close()

        # Bài học: đọc xong 1 bài
        ctx, page = new_page(browser)
        page.goto(BASE + "learn.html", wait_until="load")
        page.wait_for_timeout(1200)
        opened = page.locator("#articles .art").count() > 0
        if opened:
            page.locator("#articles .art").first.click()
        page.wait_for_timeout(9500)          # READ_SECS = 6s + du
        try:
            page.click("#reader-claim", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(700)
        lcalls = [c for c in page.evaluate("() => window.__calls || []") if "postProgress" in c]
        check("Bai hoc: mo duoc bai", opened)
        check("Bai hoc: goi postProgress type=lesson",
              len(lcalls) >= 1 and json.loads(lcalls[0].split(":", 1)[1]).get("type") == "lesson",
              str(lcalls[:1]))
        ctx.close()

        # Hàng chờ: không có AstroQAuth thì việc phải nằm lại trong localStorage
        print("\n[12] Khong co phien dang nhap -> viec xep hang cho")
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        ctx.add_init_script(
            f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
            "localStorage.setItem('astroq-asteroids','200');"
            "localStorage.removeItem('astroq-progress-queue');"
            # KHÔNG cài AstroQAuth → progress.js phải xếp hàng chờ
        )
        p2 = ctx.new_page()
        p2.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        p2.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
        p2.goto(BASE + "profile.html", wait_until="load")
        p2.wait_for_timeout(1000)
        p2.evaluate("() => AstroQProgress.game({game:'dodge', score:120, seconds:30, meteors:3})")
        p2.wait_for_timeout(3200)
        q = p2.evaluate("() => JSON.parse(localStorage.getItem('astroq-progress-queue')||'[]')")
        check("Viec duoc xep vao hang cho", len(q) == 1, str(q))
        check("Hang cho giu dung noi dung su kien",
              q and q[0].get("game") == "dodge" and q[0].get("score") == 120, str(q))
        loc = p2.evaluate("() => AstroQProgress.local()")
        check("Ban sao trong may cong dung ky luc + luot choi",
              loc["gamesPlayed"] == 1 and loc["bests"]["dodge"] == 120, str(loc["bests"]))
        p2.evaluate("() => AstroQProgress.lesson('bai-x')")
        p2.evaluate("() => AstroQProgress.lesson('bai-x')")
        p2.wait_for_timeout(3200)
        loc = p2.evaluate("() => AstroQProgress.local()")
        check("Ban sao trong may KHONG dem trung mot bai",
              loc["lessonsRead"] == 1, f"lessonsRead={loc['lessonsRead']}")
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
