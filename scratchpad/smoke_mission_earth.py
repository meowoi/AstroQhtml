# -*- coding: utf-8 -*-
"""
smoke_mission_earth.py — CHƠI THẬT Nhiệm Vụ 01 "Hành Tinh Xanh" trên Chromium.

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/smoke_mission_earth.py

Nguyên tắc của bộ này (giống các bộ trước):
  · ĐO TRÊN TRANG, không đọc code. Hiệu ứng sống 0,9–1,7s nên `page.screenshot()`
    (~200ms) quá chậm — đọc pixel bằng `readPixels` trong chính khung vẽ.
  · Bấm THẬT vào toạ độ marker (`world.screenOf`) ở ít nhất một chỗ, để raycast
    và vùng chạm được kiểm; các marker còn lại đi qua `__mission.pick` cho nhanh.
  · Chứng minh CHUYỂN CẢNH bằng camera, KHÔNG tải lại trang: ghi lại
    `performance.navigation`-style mốc thời gian + biến canh trong `window`.
  · Không gieo sẵn phần thưởng — server quyết. Trang chạy không đăng nhập nên
    `reportStep` trả rỗng; phần thưởng hiện 0 là ĐÚNG, và có mục kiểm riêng cho
    trường hợp có server (gieo `AstroQProgress.missionStep` giả).
"""
import json
import sys
import time

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
# ⚠️ Co `--scene 2d|3d` da BO ngay 31/07/2026, cung luc three.js bi xoa. Giu lai
#    mot cai co chi con MOT lua chon thi `--scene 3d` se am tham chay 2D — mot cai
#    co noi doi con te hon khong co co nao.
URL = BASE + "/mission-earth.html"

ok = fail = 0
FAILS = []


# ⚠️⚠️ ĐỪNG GÕ MỘT NHÚM KÝ TỰ CÓ DẤU ĐỂ HỎI "ĐÃ DỊCH CHƯA" — dự án đã trả giá BA LẦN.
#    Lần 1: một tiêu đề tiếng Việt không chứa ký tự nào trong nhúm 9 ký tự → báo hỏng oan.
#    Lần 2: nhúm chỉ có chữ THƯỜNG, mà "SỨ MỆNH TRÁI ĐẤT HOÀN THÀNH!" toàn chữ HOA →
#           phép kiểm **ĐẠT trong khi sản phẩm sai**, tệ hơn báo hỏng oan.
#    Cách đúng là hỏi điều muốn biết: chuỗi này có ký tự có dấu tiếng Việt nào không.
_VN_MARKS = "ăâđêôơư" + "áàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩị" \
            + "óòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
_VN_SET = set(_VN_MARKS) | set(_VN_MARKS.upper())


def co_dau_viet(s):
    """True nếu chuỗi có ít nhất một ký tự có dấu tiếng Việt (KỂ CẢ chữ hoa)."""
    return any(c in _VN_SET for c in (s or ""))


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


# ─────────────────────────────────────────────────────────────────────────────
# Bản giả AstroQProgress. Số liệu KHÔNG bịa: chép đúng bảng luật ở
# AstroqSV/src/AstroqSV.Api/Services/Missions.cs và hình dạng phản hồi của
# POST /me/missions/step trong Endpoints/MeEndpoints.cs — bước cuối cộng thêm
# bó hoàn thành (DoneMeteors 100 / DoneXp 120) vào chính `awarded`/`xpGained`.
#
# 7 bước (bỏ `rotation` 02/08/2026, `docs/decisions/005`). Tổng phải ra:
#   tt : 0+20+20+25+20+30+(20+100) = 235
#   XP : 20+30+30+35+40+40+(40+120) = 355
#   codex: 8/8  (earth-formation · sun · clean-energy ·
#                water/forest/animal/mountain · eco-habits)
# `newBadges` cũng do server quyết: `eco-warrior` mở ngay ở bước `eco`
# (metric `mission:earth:eco` trong Achievements.cs), `rookie-astronaut` ở bước cuối.
STUB_METEORS, STUB_XP, STUB_CODEX_TOTAL = 235, 355, 8
STUB_PROGRESS = r"""
window.__calls = [];
/* ⚠️ Cài bằng `Object.defineProperty` có SETTER NUỐT lời gán. `js/progress.js`
   chạy SAU init script và làm `global.AstroQProgress = …`, nên gán thẳng
   `window.AstroQProgress = {…}` là bị bản thật ghi đè và bản giả không bao giờ
   được gọi — đúng cái bẫy đã gặp với `AstroQAuth` (ghi trong CLAUDE.md 29/07). */
var __stub = {
  missionStep: async function (mission, step) {
    window.__calls.push({ mission: mission, step: step });
    var TBL = {
      scan:     { meteors: 0,  xp: 20, codex: [] },
      timeline: { meteors: 20, xp: 30, codex: ['earth-formation'] },
      sun:      { meteors: 20, xp: 30, codex: ['sun'] },
      energy:   { meteors: 25, xp: 35, codex: ['clean-energy'] },
      life:     { meteors: 20, xp: 40, codex: ['water','forest','animal','mountain'] },
      eco:      { meteors: 30, xp: 40, codex: ['eco-habits'], badges: ['eco-warrior'] },
      core:     { meteors: 20, xp: 40, codex: [] }
    };
    var r = TBL[step] || { meteors: 0, xp: 0, codex: [] };
    var done = step === 'core';
    window.__codex = (window.__codex || []).concat(r.codex);
    var badges = (r.badges || []).concat(done ? ['rookie-astronaut'] : []);
    return {
      ok: true, status: 200,
      data: {
        awarded:  r.meteors + (done ? 100 : 0),
        xpGained: r.xp      + (done ? 120 : 0),
        newBadges: badges,
        missionDone: done,
        unlocks: done ? 'moon' : null,
        counted: true,
        wallet: { meteors: 999 },
        /* ⚠️ ĐỌC TỪ `STUB_CODEX_TOTAL`, KHÔNG GÁN CỨNG. Ngày 02/08/2026 dòng này
           ghi cứng `codexTotal: 9` trong khi phép kiểm đối chiếu `STUB_CODEX_TOTAL`
           đã về 8 — nên bộ smoke báo màn tổng kết ghi "8/9 mẫu dữ liệu" và tôi
           tưởng SẢN PHẨM hỏng, đi sửa `mission-earth.html`. Thật ra BẢN GIẢ nói
           sai: server thật trả 8 (đã đo bằng `test_missions` 101/101).
           Bản giả gán cứng một con số mà nơi khác là nguồn sự thật thì nó sẽ tố
           cáo oan sản phẩm — đúng loại lỗi tệ nhất mà một bộ đo có thể mắc. */
        missions: { earth: { codex: window.__codex.slice(),
                             codexTotal: __STUB_CODEX_TOTAL__, done: done } }
      }
    };
  },
  quiz: function () {}, game: function () {}, lesson: function () {},
  planet: function () {}, spend: function () {}, flush: function () {}
};
Object.defineProperty(window, 'AstroQProgress', {
  configurable: true,
  get: function () { return __stub; },
  set: function () { /* nuốt: không cho bản thật ghi đè bản giả */ }
});
"""


def stub(page, lang="vi"):
    # Nội suy con số vào bản giả — MỘT nguồn sự thật cho cả bản giả và phép kiểm.
    assert "__STUB_CODEX_TOTAL__" in STUB_PROGRESS, "ban gia mat cho noi suy codexTotal"
    page.add_init_script(
        STUB_PROGRESS.replace("__STUB_CODEX_TOTAL__", str(STUB_CODEX_TOTAL)))
    # ⚠️ PHẢI ghim ngôn ngữ. `AstroQ.getLang()` lùi về `navigator.language` khi
    # `localStorage` còn trống, mà Chromium của Playwright mặc định `en-US` →
    # cả phần "tiếng Việt" của bộ test lặng lẽ chạy bằng tiếng Anh và mọi phép
    # kiểm chữ Việt đều vô nghĩa. Đây là hành vi ĐÚNG của sản phẩm, không phải lỗi.
    page.add_init_script(
        "localStorage.setItem('astroq-lang', %r);" % lang)
    # ⚠️ GHI LAI TUNG TRANG THAI CUA BAN TAY HUONG DAN KEM CHE DO BAN DO.
    #    Ban tay 'drag' chi song ~1,4s roi bi 'tap' ghi de, nen doc mot lan bang
    #    `evaluate` la do mot khoanh khac ngau nhien. Muon biet "co bao gio day tre
    #    KEO trong luc con o anh qua cau khong" thi phai theo doi lien tuc.
    #    Chi push khi mau DOI, khong thi mot luot ~10 phut sinh hang chuc nghin dong.
    page.add_init_script("""
      window.__handLog = [];
      setInterval(function () {
        var h = document.getElementById('hand');
        if (!h) return;
        var m = (window.__mission && window.__mission.world
                 && window.__mission.world.map) || '?';
        var s = h.className + '|' + m;
        var L = window.__handLog;
        if (L[L.length - 1] !== s) L.push(s);
      }, 40);
    """)


def boot(page, lang="vi", reduced=False):
    """Mở trang, chờ cảnh 3D dựng xong và __mission có mặt."""
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_function("() => !!window.__mission", timeout=40000)
    # `objective()` chỉ được gọi SAU cú panTo mở màn (1,4s) — chờ nó hiện, đừng
    # đo ngay lúc `__mission` vừa có.
    page.wait_for_selector("#obj.show", timeout=20000)
    return page


def wait_step(page, sid, timeout=30000):
    """Cho toi khi nhiem vu sang buoc `sid`.

    ⚠️ IN RA TRANG THAI KHI HET HAN. Mot phep cho that bai ma khong noi gi thi chi
       bao "co cai gi do treo" — con treo o dau thi phai doan, ma moi luot chay lai
       mat ~10 phut. Ban dau ham nay im lang va da dot mat hai luot vi the; chinh
       ban chan doan nay moi chi ra `finish('sun')` chua tung duoc goi.
    """
    try:
        page.wait_for_function(f"() => window.__mission.step === '{sid}'", timeout=timeout)
    except Exception:
        st = page.evaluate("""() => {
          const m = window.__mission || {};
          const say = document.getElementById('say');
          const nx  = document.getElementById('say-next');
          return {
            step: m.step, done: m.done, busy: m.busy,
            sunOn: m.world && m.world.sunOn,
            sayCls: say && say.className, nextCls: nx && nx.className,
            objH: (document.getElementById('obj-h') || {}).textContent,
            openOverlays: [...document.querySelectorAll('.show')]
                            .map(e => e.id || e.className).slice(0, 6)
          };
        }""")
        print(f"  [!] wait_step('{sid}') het han. Trang thai luc do:")
        for k, v in st.items():
            print(f"        {k} = {v!r}")
        raise


def say_through(page, limit=6):
    """Bấm 'Tiếp tục' cho tới khi box thoại tắt (mỗi bước có 1–2 câu)."""
    for _ in range(limit):
        try:
            page.wait_for_function(
                "() => { const b=document.getElementById('say-next');"
                " return b && !b.classList.contains('hide') &&"
                " document.getElementById('say').classList.contains('show'); }",
                timeout=4000)
        except Exception:
            return
        page.evaluate("document.getElementById('say-next').click()")
        page.wait_for_timeout(120)


def close_card(pg, timeout=6000):
    """Bấm 'Đã hiểu!' nếu thẻ nội dung đang mở. Trả True nếu vừa đóng một thẻ.

    ⚠️⚠️ BẮT BUỘC SAU MỌI CÚ `pick()` MỞ THẺ. Thẻ **không còn tự đóng sau 3,4 giây**
    (bỏ 02/08/2026 — chủ dự án chơi thật: *"không đủ thời gian đọc cho trẻ"*). Không
    bấm thì `showCard` không bao giờ resolve → cờ `busy` kẹt ở true → phép chờ
    `!busy` ở lượt sau hết hạn, và triệu chứng đọc ra y hệt **sản phẩm treo**.
    Đây là lỗi CÓ SẴN của bộ đo, lộ ra ở lần chạy đầu tiên sau lượt sửa đó.
    """
    try:
        if pg.evaluate("() => document.getElementById('card').classList.contains('show')"):
            pg.click("#card-ok", timeout=timeout)
            pg.wait_for_function(
                "() => !document.getElementById('card').classList.contains('show')",
                timeout=timeout)
            return True
    except Exception:
        pass
    return False


def read_card(pg, timeout=30000):
    """Chờ thẻ 'vừa nhận được' hiện, ghi nội dung, chờ nó đóng. None nếu không hiện."""
    try:
        pg.wait_for_function(
            "() => document.getElementById('card').classList.contains('show')",
            timeout=timeout)
        c = pg.evaluate(
            "() => [document.getElementById('card-ic').textContent,"
            " document.getElementById('card-nm').textContent,"
            " document.getElementById('card-fact').textContent,"
            " document.getElementById('card-got').textContent,"
            " document.getElementById('card-sub').textContent]")
        # ⚠️⚠️ PHẢI BẤM "Đã hiểu!" — THẺ KHÔNG CÒN TỰ ĐÓNG. Bỏ mốc tự đóng 3,4 giây là
        #    một thay đổi CỦA SẢN PHẨM (chủ dự án chơi thật: "không đủ thời gian đọc"),
        #    nhưng hàm này vẫn ngồi chờ thẻ tự biến mất → hết hạn 12s rồi trả `None`,
        #    và triệu chứng đọc ra y như "chạm châu lục không hiện thẻ". Nó còn kéo theo
        #    `busy` kẹt mãi ở true vì `showCard` chưa resolve.
        #    ⚠️ Đây là lỗi CÓ SẴN của bộ đo, lộ ra ở lần chạy đầu tiên sau lượt sửa đó —
        #    tức bộ smoke đã đỏ từ trước lượt việc hôm nay, không ai biết. Bài học: đổi
        #    một component DÙNG CHUNG (`showCard` phục vụ bước ①③⑤) thì phải chạy lại
        #    bộ smoke ngay, đừng để dồn.
        ok = pg.query_selector("#card-ok")
        if ok:
            ok.click()
        pg.wait_for_function(
            "() => !document.getElementById('card').classList.contains('show')",
            timeout=12000)
        return c
    except Exception:
        return None


def play_timeline(pg):
    """Bấm hết các mốc thời gian. Trả về (số mốc đã xem, thẻ nham thạch).

    Mốc dung nham trao viên nham thạch NGAY tại đó, nên phải đọc thẻ giữa mốc 0 và
    mốc 1 — đọc sau khi bấm hết là thẻ đã tự đóng từ lâu.
    """
    rock = None
    n = pg.evaluate("window.__mission.eraTotal")     # ĐỌC từ trang, đừng gán cứng
    for i in range(n):
        pg.wait_for_function("() => !window.__mission.busy", timeout=30000)
        b = pg.query_selector(f'#time-rail .me-era-node[data-era="{i}"]')
        if b:
            b.click()                      # BẤM THẬT, không đi qua __mission.era
        else:
            pg.evaluate("i => window.__mission.era(i)", i)
        pg.wait_for_timeout(200)
        if i == 0:
            rock = read_card(pg, timeout=8000)
    eras = pg.evaluate("window.__mission.eras")
    # Trạng thái NGAY TRƯỚC cú bấm — sau đó bảng đã đóng thật rồi, không đo được nữa.
    last = pg.evaluate("""() => {
      const ok = document.getElementById('time-ok');
      return { boardShown: document.getElementById('time').classList.contains('show'),
               body: (document.getElementById('time-p').textContent || '').length,
               okShown: !!ok && !ok.hidden,
               okLabel: ok ? ok.textContent.trim() : null,
               okH: ok ? Math.round(ok.getBoundingClientRect().height) : 0,
               focused: document.activeElement === ok,
               figHidden: document.getElementById('time-fig').hidden,
               cur: (document.getElementById('time-img').currentSrc || '').split('/').pop(),
               boardH: Math.round(document.getElementById('time').getBoundingClientRect().height),
               map: Math.round(document.getElementById('time').getBoundingClientRect().top
                             - document.querySelector('.me-top').getBoundingClientRect().bottom),
               done: window.__mission.done.includes('timeline') };
    }""")
    # ⚠️ MỐC CUỐI KHÔNG CÒN TỰ CHỐT BƯỚC (sửa 02/08/2026). Trước đây `openEra` gọi
    #    `finishStep` ngay sau khi ghi chữ ra, nên `outro()` gỡ luôn cả bảng và **trẻ
    #    không đọc được một chữ nào của mốc cuối** — chủ dự án chơi thật và báo là "bị
    #    cắt luôn phần lý giải, nhìn như lỗi giật giật". Nay phải BẤM như trẻ.
    ok = pg.query_selector("#time-ok:not([hidden])")
    if ok:
        ok.click()                         # BẤM THẬT, không đi qua __mission.eraDone
    else:
        pg.evaluate("window.__mission.eraDone()")
    pg.wait_for_timeout(250)
    return eras, rock, last


def play_energy(pg):
    """Kéo 3 nguồn sạch vào 3 ống khói. Trả về (số ống đã thay, khói đầu, khói cuối)."""
    pg.wait_for_selector("#energy.show", timeout=15000)
    smog0 = pg.evaluate("window.__mission.smog")
    items = pg.eval_on_selector_all("#energy-tray .me-gem", "es => es.map(e => e.dataset.want)")
    # ⚠️ ĐẾM NGAY SAU TỪNG CÚ THẢ, ĐỪNG ĐẾM Ở CUỐI. Ống khói nay là MARKER CỦA CẢNH, và
    #    cú thả thứ ba chốt bước → `outro()` gọi `world.clearMarkers()` → cả ba ống biến
    #    khỏi DOM. Đếm ở cuối thì ra **0/3** trong khi cả ba đã thay xong và khói đã tan
    #    hết — một phép đo đọc ra y như "kéo-thả không hoạt động". Hồi ống khói còn nằm
    #    trong bảng `#energy-slots` thì đếm ở cuối vẫn đúng, nên đây là hệ quả của việc
    #    dời chúng lên bản đồ, không phải lỗi mới của kéo-thả.
    # ⚠️ ĐO BẰNG ĐỘ DÀY KHÓI, KHÔNG ĐẾM CLASS `.ok`. Cú thả THỨ BA chốt bước → `outro()`
    #    gọi `world.clearMarkers()`, nên ống thứ ba biến khỏi DOM trước khi đọc kịp class
    #    của nó: đếm class thì mãi mãi ra 2/3 dù cả ba đã thay xong. Không phải lỗi sản
    #    phẩm — chỉ là ống khói nay là MARKER CỦA CẢNH, có tuổi thọ bằng bước.
    #    `--smog` thì tồn tại độc lập với marker, và nó ĐÚNG là thứ trẻ nhìn thấy: CLAUDE.md
    #    ghi rõ "khói mỏng đi theo TỪNG nguồn" là hành vi được thiết kế.
    ok, prev = 0, smog0
    for want in items:
        drag_to(pg, f'#energy-tray .me-gem[data-want="{want}"]',
                f'.e2-mk.e2-stack[data-zone="{want}"]')
        cur = pg.evaluate("window.__mission.smog")
        if cur < prev - 0.05:
            ok += 1
        prev = cur
    return (ok, smog0, pg.evaluate("window.__mission.smog"))


def play_eco(pg):
    """Kéo 7 thẻ Eco-Hero vào đúng rổ. Trả về số thẻ đã xếp."""
    pg.wait_for_selector("#eco.show", timeout=15000)
    cards = pg.eval_on_selector_all(
        "#eco-deck .me-gem", "es => es.map(e => [e.dataset.card, e.dataset.want])")
    for cid, want in cards:
        drag_to(pg, f'#eco-deck .me-gem[data-card="{cid}"]',
                f'#eco .me-bucket[data-zone="{want}"]')
    return pg.evaluate("window.__mission.sorted")


def drag_to(pg, from_sel, to_sel):
    """Kéo-thả THẬT bằng chuột (Pointer Events) — dùng chung cho 3 bảng kéo-thả."""
    f = pg.query_selector(from_sel)
    tgt = pg.query_selector(to_sel)
    if not f or not tgt:
        return False
    a, b = f.bounding_box(), tgt.bounding_box()
    pg.mouse.move(a["x"] + a["width"] / 2, a["y"] + a["height"] / 2)
    pg.mouse.down()
    pg.mouse.move(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2, steps=10)
    pg.mouse.up()
    pg.wait_for_timeout(300)
    return True


def spin_deg(page):
    """Hành tinh đã quay bao nhiêu ĐỘ — dùng được cho cả hai engine.

    Cảnh 3D trả `earthSpinY` bằng RADIAN, cảnh 2D thì con số tương đương là
    `facingLatLon().lon` bằng ĐỘ. Quy về độ ở một chỗ để mọi phép so ngưỡng phía
    sau chỉ phải biết MỘT đơn vị.
    """
    return page.evaluate("""() => {
      const w = window.__mission.world;
      if (typeof w.earthSpinY === 'number') return w.earthSpinY * 180 / Math.PI;
      return w.facingLatLon().lon;
    }""")


def deg_delta(a, b):
    """Chênh lệch góc có xử lý VÒNG QUA ±180.

    Kéo 320px ở 0,42°/px là ~134°, nên phép trừ thẳng rất dễ nhảy qua mốc ±180 và
    ra một con số vô nghĩa (vd 170 -> -175 thành -345 thay vì +15).
    """
    d = (b - a + 180) % 360 - 180
    return d


def grid_hidden(page):
    """Lưới Chẩn Đoán đã tắt chưa. None = không tìm thấy lưới.

    Hai engine dựng lưới bằng hai cách khác nhau về BẢN CHẤT (Mesh wireframe trong
    WebGL vs một lớp gradient CSS), nên đây là chỗ buộc phải rẽ nhánh — nhưng câu
    hỏi thì vẫn là một: người chơi CÒN THẤY lưới không.
    """
    return page.evaluate("""() => {
      const w = window.__mission.world;
      if (w.scene && w.scene.traverse) {              // cảnh 3D
        // ⚠️ Từ 31/07/2026 lưới là các `THREE.Line` (kinh tuyến / vĩ tuyến / xích
        //    đạo) trong một Group, KHÔNG còn là `Mesh` có `material.wireframe`.
        //    Tìm theo tiêu chí cũ thì trả về null và phép kiểm "tìm thấy lưới" đỏ.
        //    Nhận diện theo ĐÚNG THỨ NÓ LÀ: mọi con đều là Line và đều mờ dần cùng nhau.
        let g = null;
        w.scene.traverse(o => {
          if (o.isGroup && o.children.length >= 8 &&
              o.children.every(c => c.isLine)) g = o;
        });
        if (!g) return null;
        const ops = g.children.map(c => c.material.opacity);
        return g.visible === false || Math.max.apply(null, ops) < 0.02;
      }
      const e = document.querySelector('.e2-grid');   // cảnh 2D
      if (!e) return null;
      const cs = getComputedStyle(e);
      return cs.display === 'none' || parseFloat(cs.opacity) < 0.02;
    }""")


def _has_gl(page):
    """LUON tra False tu 31/07/2026 — canh 3D da bi xoa.

    ⚠️ CO Y GIU nhanh WebGL trong `pix()`/`col_profile()` thay vi cat bo: no duoc
       canh bang chinh ham nay (`w.renderer && ...`), nen khong bao gio chay va
       khong the hong. Mot lan toi thu cat no bang tay da xoa nham ca
       `col_profile()` va lam mat 842 dong — cai gia cua viec don dep khong can
       thiet cao hon cai gia cua vai chuc dong ma chet co ghi chu ro rang.
    """
    """Canh 3D co WebGL; canh 2D thi khong."""
    return page.evaluate(
        "()=>{const w=window.__mission&&window.__mission.world;"
        "return !!(w&&w.renderer&&w.renderer.getContext);}")


def _stage_shot(page, region):
    """Chup mot vung cua #stage roi tra ve anh PIL.

    ⚠️ LAT TRUC Y. `gl.readPixels` lay goc toa do o DAY-TRAI cua buffer, con anh
       chup thi o DINH-TRAI. Moi cho goi `pix()` deu viet region theo he cua GL
       (vi bo test nay sinh ra cho canh 3D), nen nhanh 2D phai lat:
           y_dinh = 1 - (ry + rh)
       Bo dong nay thi moi phep do "nua tren / nua duoi" se lang le doi cho nhau
       ma van ra so — dung loai loi kho thay nhat.
    """
    from PIL import Image
    import io as _io
    rx, ry, rw, rh = region
    b = page.evaluate(
        "()=>{const s=document.getElementById('stage');const r=s.getBoundingClientRect();"
        "return [r.x,r.y,r.width,r.height];}")
    x0, y0, W, H = b
    clip = {"x": x0 + rx * W, "y": y0 + (1 - ry - rh) * H,
            "width": max(1.0, rw * W), "height": max(1.0, rh * H)}
    return Image.open(_io.BytesIO(page.screenshot(clip=clip))).convert("RGB")


def _stats(im):
    """Dung 5 con so nhu nhanh WebGL, dung dung nguong mau."""
    px = list(im.getdata())
    n = len(px)
    lit = warm = cyan = 0
    total = 0
    for R, G, B in px:
        l = R + G + B
        total += l
        if l > 90:
            lit += 1
        if R > 150 and G > 110 and B < 130:
            warm += 1
        if B > 120 and G > 110 and R < 130:
            cyan += 1
    return {"n": n, "lit": lit, "warm": warm, "cyan": cyan, "avg": total / (n * 3)}


def pix(page, region=None):
    """Doc pixel cua canh — CHAY DUOC TREN CA HAI ENGINE.

    · canh 3D: doc thang buffer WebGL trong chinh khung ve (nhanh, ~0ms) — hieu ung
      chi song 0,9-1,7s nen `page.screenshot()` (~200ms) qua cham de lay theo tung
      khung; giu nhanh nay de khong lam yeu di phep do da co.
    · canh 2D: khong co WebGL, nen chup vung tuong ung cua #stage roi dem pixel.
      Cung 5 con so, cung nguong, nen moi phep kiem phia sau khong phai sua.
    """
    r = region or (0, 0, 1, 1)
    if not _has_gl(page):
        return _stats(_stage_shot(page, r))
    return page.evaluate(
        """([rx, ry, rw, rh]) => new Promise(res => {
      const w = window.__mission.world;
      const gl = w.renderer.getContext();
      requestAnimationFrame(() => {
        const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
        const x = Math.floor(rx * W), y = Math.floor(ry * H);
        const ww = Math.max(1, Math.floor(rw * W)), hh = Math.max(1, Math.floor(rh * H));
        const buf = new Uint8Array(ww * hh * 4);
        gl.readPixels(x, y, ww, hh, gl.RGBA, gl.UNSIGNED_BYTE, buf);
        let lit = 0, sum = 0, warm = 0, cyan = 0;
        for (let i = 0; i < buf.length; i += 4) {
          const R = buf[i], G = buf[i+1], B = buf[i+2];
          const l = R + G + B;
          sum += l;
          if (l > 90) lit++;
          if (R > 150 && G > 110 && B < 130) warm++;
          if (B > 120 && G > 110 && R < 130) cyan++;
        }
        res({ n: ww*hh, lit, warm, cyan, avg: sum / (ww*hh*3) });
      });
    })""", [r[0], r[1], r[2], r[3]])


def col_profile(page, ncols=32, band=40):
    """Do sang trung binh theo `ncols` cot, tren mot dai ngang qua TAM canh.

    Dung cho phep do ranh gioi ngay/dem: do 2 diem thi khong phan biet duoc "toi
    dan deu" voi "co ranh gioi", nen phai co ca mot duong cong.
    Chay duoc tren ca hai engine, cung ly do nhu `pix()`.
    """
    if not _has_gl(page):
        b = page.evaluate(
            "()=>{const s=document.getElementById('stage');const r=s.getBoundingClientRect();"
            "return [r.x,r.y,r.width,r.height];}")
        x0, y0, W, H = b
        from PIL import Image
        import io as _io
        clip = {"x": x0, "y": y0 + H / 2 - band / 2, "width": W, "height": float(band)}
        im = Image.open(_io.BytesIO(page.screenshot(clip=clip))).convert("RGB")
        iw, ih = im.size
        cw = max(1, iw // ncols)
        cols = []
        for c in range(ncols):
            box = im.crop((c * cw, 0, min(iw, (c + 1) * cw), ih))
            d = list(box.getdata())
            cols.append(sum(R + G + B for R, G, B in d) / (len(d) * 3))
        return cols
    return page.evaluate(
        """([NC, hh]) => new Promise(res => {
      const w = window.__mission.world;
      const gl = w.renderer.getContext();
      requestAnimationFrame(() => {
        const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
        const y = Math.floor(H/2 - hh/2);
        const buf = new Uint8Array(W * hh * 4);
        gl.readPixels(0, y, W, hh, gl.RGBA, gl.UNSIGNED_BYTE, buf);
        const cw = Math.floor(W / NC), cols = [];
        for (let c = 0; c < NC; c++) {
          let sum = 0, n = 0;
          for (let yy = 0; yy < hh; yy++) {
            for (let xx = c*cw; xx < (c+1)*cw; xx++) {
              const i = (yy*W + xx) * 4;
              sum += buf[i] + buf[i+1] + buf[i+2]; n++;
            }
          }
          cols.push(sum / (n*3));
        }
        res(cols);
      });
    })""", [ncols, band])


# Màng khí quyển bảo bọc. Dùng thẳng `world.shieldOn` chứ KHÔNG quét uniform tên
# `strength`: vành khí quyển thường (atmo) cũng có uniform trùng tên và giá trị tới
# 0,9 — quét theo tên thì báo "đã bọc" ngay cả khi chưa bọc.
SHIELD_JS = "() => window.__mission.world.shieldOn === true"


# Đếm số dao động WebAudio mà một lời gọi âm thanh dựng ra. Chromium headless
# không cho nghe tiếng, nhưng đếm node thì chứng minh được "đã tắt là im".
SFX_COUNT_JS = """() => {
  const c = AstroQSfx.ctx();
  if (!c) return 'no-ctx';
  let n = 0;
  const orig = c.createOscillator.bind(c);
  c.createOscillator = function () { n++; return orig(); };
  %s
  c.createOscillator = orig;
  return n;
}"""


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--use-gl=angle", "--enable-unsafe-swiftshader"])

        # ══════════════════════════════════════════════════════════════════
        head("[1] Trang mở được, cảnh 3D dựng xong")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        errs = []
        page = ctx.new_page()
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        stub(page)
        t0 = time.time()
        boot(page)
        chk(True, "cảnh 3D dựng xong", f"{time.time()-t0:.1f}s")
        chk(page.eval_on_selector("#load", "e => e.classList.contains('gone')"),
            "màn chờ đã tắt")
        cv = page.eval_on_selector("#stage", "e => [e.clientWidth, e.clientHeight]")
        chk(cv[0] > 1000 and cv[1] > 600, "canvas phủ màn hình", str(cv))
        chk(page.eval_on_selector("#obj", "e => e.classList.contains('show')"),
            "bảng mục tiêu hiện")
        chk(page.evaluate("window.__mission.step") == "scan", "bắt đầu ở bước scan")
        oh = page.eval_on_selector("#obj-h", "e => e.textContent")
        # ⚠️ NỚI BỘ KÝ TỰ 02/08/2026 — và đây là LỖI CỦA PHÉP KIỂM, không phải nới lỏng.
        #    Bản cũ chỉ dò 9 ký tự "ộạảấầệốơư"; tiêu đề mới "Bề mặt hành tinh xanh"
        #    không chứa cái nào trong số đó nên nó báo hỏng một câu tiếng Việt hoàn
        #    toàn đúng. Điều muốn biết là "có dấu tiếng Việt không", nên phải hỏi đúng
        #    câu đó thay vì gán cứng một nhúm ký tự.
        VN_MARKS = "ăâđêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
        chk(any(c in VN_MARKS for c in oh.lower()),
            "mục tiêu hiện bằng TIẾNG VIỆT", oh)

        # Trái Đất phải ĐANG SÁNG ở bước 1 (theo bản mô tả, tối đi là ở bước 2)
        p_lit = pix(page, (0.3, 0.3, 0.4, 0.4))
        # ⚠️ NGƯỠNG SIẾT TỪ 22 LÊN 70 (02/08/2026, `docs/decisions/004`).
        #    Mốc 22 sinh ra khi bước 1 mở màn bằng ảnh quả cầu rồi mới đổi sang bản đồ,
        #    và nó lỏng tới mức vô nghĩa. Nay cả nhiệm vụ chạy một hình duy nhất, độ sáng
        #    do KHUNG NHÌN quyết (`FACE_OPEN`): đo được 82,7 so với 87,0 của ảnh quả cầu
        #    như nó từng chạy. Đặt sàn 70 để lùi khung nhìn về vùng đại dương (26,8) là
        #    báo hỏng ngay — đó chính là lỗi mà 004 sinh ra để chặn.
        chk(p_lit["avg"] > 70, "bước 1: Trái Đất đang SÁNG", f"độ sáng TB {p_lit['avg']:.1f}")
        # ⚠️ ĐẢO CHIỀU 02/08/2026 — trước đây phép kiểm này ĐÒI ảnh quả cầu.
        #    Nó bảo vệ đúng cái hành vi mà chủ dự án báo là lỗi ("hình lúc tròn lúc méo"):
        #    3 lần đổi hình, tệ nhất là cú đổi NGAY GIỮA bước 1. Lý do cũ ("phẳng tối hơn
        #    4,7 lần") đã đo lại và sai địa chỉ — xem `FACE_OPEN` trong mission-earth.html.
        #    Điều phép kiểm này bảo vệ (cảnh mở màn không được tối) nay do mốc 70 ở trên lo.
        chk(page.evaluate("() => window.__mission.world.map") == "flat",
            "mở màn ĐÃ LÀ bản đồ phẳng (0 lần đổi hình trong cả nhiệm vụ)",
            page.evaluate("() => window.__mission.world.map"))

        # ══════════════════════════════════════════════════════════════════
        head("[2] Bước 1 — lưới quét + 7 CHÂU LỤC + câu đố biển/đất (bấm THẬT)")
        # Trước đây đếm `world.scene.children.length` — một con số của THREE.js, mà
        # điều muốn biết chỉ là "cảnh đã vẽ ra cái gì chưa". Đo pixel sáng đúng hơn:
        # scene có 20 vật thể mà đặt sai chỗ hết thì màn hình vẫn đen.
        chk(pix(page)["lit"] > 0, "canh da ve ra pixel sang tren man hinh")
        say_through(page)
        page.wait_for_function("() => window.__mission.world.markers.length === 7", timeout=15000)
        chk(True, "7 châu lục đã đặt")


        # Bàn tay hướng dẫn phải đã xuất hiện trong bước này
        chk(page.evaluate(
            "() => window.__handSeen === true || document.getElementById('hand')"
            ".className.length >= 0"), "có bàn tay hướng dẫn (phần tử #hand tồn tại)")

        # Bấm THẬT vào marker đầu tiên tại đúng chỗ nó đang hiện trên màn hình
        ids = page.evaluate("window.__mission.world.markers.map(m => m.id)")
        vis = page.evaluate(
            "() => window.__mission.world.markers"
            ".filter(m => window.__mission.world.screenOf('marker', m.id).visible).length")
        # ⚠️ VIẾT LẠI 02/08/2026 (`docs/decisions/005`). Bản trước đòi "CẢ BA đốm trong
        #    khung ngay lúc vào bước". Với 7 CHÂU LỤC thì điều đó **bất khả thi trên
        #    điện thoại dọc**, và đây là một con số chứ không phải một cảm giác:
        #      bề ngang nhìn thấy = 360° × vpW / max(vpW, 2·vpH)  ở sàn phóng zoom 1
        #        · 1440×900  → 288°  (đủ cả 7 — nên trên desktop vẫn đòi ĐỦ, xem dưới)
        #        · 390×844   → 83°   (7 châu lục trải ~234°, không đời nào đủ)
        #    Cái phải bảo vệ KHÔNG phải "mọi marker luôn trong khung" mà là "trẻ không
        #    bao giờ kẹt": châu lục kế tiếp phải luôn tới được. `focusMarker()` lo việc
        #    đó bằng cách lướt bản đồ tới nó — và mục [9] (điện thoại) kiểm đúng chuyện
        #    đó ở đúng cỡ màn không nhìn hết được.
        chk(vis == 7, "desktop 1440x900: ĐỦ CẢ 7 châu lục trong khung ngay lúc vào bước",
            f"{vis}/7 thấy được")
        # ⚠️ KHỐI KÉO PHẢI ĐỨNG SAU PHÉP KIỂM "≥2/3 ĐIỂM" NGAY TRÊN. Lượt đầu tôi đặt
        #    nó lên trước, nên phép kiểm kia đo SAU khi bản đồ đã bị kéo đi 300px và
        #    báo 1/3 — hỏng oan, lỗi THỨ TỰ trong bộ đo chứ không phải lỗi sản phẩm.
        # ══ KỊCH BẢN MỚI 01/08/2026: kéo phải làm ẢNH ĐỔI, không phải làm ĐỐM TRƯỢT ══
        # ⚠️ Đây là phép kiểm quan trọng nhất của bước 1. Trên ảnh quả cầu, `paint()`
        #    đặt `translate` bằng 0 — đo được: kéo 300px thì transform và khung ảnh Y
        #    NGUYÊN, chỉ ba cái đốm trượt đi (một cái ra khỏi khung). Tức lời "Kéo để
        #    xoay Trái Đất" mô tả một việc KHÔNG HỀ XẢY RA, và thứ trẻ thấy là mục tiêu
        #    chạy khỏi con trỏ. Đọc code không thấy — phải kéo rồi so hai số đo.
        # ⚠️ BA PHÉP KIỂM CŨ ĐÃ BỎ Ở ĐÂY (02/08/2026, `004`) — ghi lại để lần sau
        #    không ai tưởng bộ kiểm bị nới:
        #      · "sau lời Comet: đã chuyển sang CHẾ ĐỘ BẢN ĐỒ" — không còn cú đổi nào
        #        để mà kiểm; phép kiểm ở mục [1] nay đòi 'flat' NGAY TỪ ĐẦU, chặt hơn.
        #      · "KHÔNG dạy KÉO trong lúc còn ở ảnh quả cầu" — bước 1 không dạy kéo nữa,
        #        nên điều nó bảo vệ được bảo vệ TỐT HƠN bằng cách không có cú kéo nào.
        #      · "bàn tay KÉO CÓ hiện sau khi đã sang bản đồ" — bàn tay giờ chỉ CHỈ TRỎ.
        #    Thay bằng ba phép kiểm dưới, đòi đúng thứ `004` hứa.
        hlog = page.evaluate("() => window.__handLog || []")
        chk(not any("drag" in x for x in hlog),
            "KHONG con ban tay KEO o bat ky luc nao",
            str([x for x in hlog if "drag" in x][:3]))
        chk(not any("zoom" in x for x in hlog),
            "KHONG con ban tay ZOOM o bat ky luc nao",
            str([x for x in hlog if "zoom" in x][:3]))
        chk(any("tap" in x for x in hlog),
            "CO ban tay CHI TRO vao dom (khong mat phan chi duong)",
            str([x for x in hlog if "tap" in x][:2]))

        # ══ BAN TAY PHAI DI THEO TRE, KHONG THEO THU TU KHAI BAO ═════════════════
        # Loi THAT 03/08/2026 (`docs/decisions/007`): chu du an bao *"click sang diem sang
        # khac roi ma ban tay van o cho cu"*. Nguyen nhan la HAI LUAT DEU DUNG nhung NGUOC
        # NHAU: `004` chot "cham dom nao truoc cung duoc", nhung `nextLeft` lai tra ve dom
        # chua cham DAU TIEN THEO THU TU KHAI BAO. Tre cham tu giua ra thi dom so 0
        # (`namerica`) cu chua cham mai -> tay dung nguyen mot cho suot nhieu cu cham lien.
        # Tai hien duoc truoc khi sua: 5 cu cham lien, tay o (340,233) khong nhich 1 pixel.
        #
        # ⚠️ PHAI CHAM THEO THU TU KHAC HAN THU TU KHAI BAO — cham dung thu tu khai bao thi
        #    ban CU cung "dung", nen phep kiem se xanh o ca trang thai hong.
        # ⚠️ Va phai doi HAI dieu, khong chi mot: tay DOI CHO (khong dung nguyen) VA tay
        #    chi vao dung mot dom co that (`handTarget`) dang o trong khung. "Co ban tay"
        #    thi ban hong cung dat.
        _hand_ids = page.evaluate("window.__mission.world.markers.map(m=>m.id)")
        _scramble = _hand_ids[2:] + _hand_ids[1:2]      # bat dau tu GIUA, ket o dom so 1
        _hpos, _stuck_hand, _bad_target = [], [], []
        for _mid in _scramble:
            page.wait_for_function("() => !window.__mission.busy", timeout=30000)
            page.evaluate("id => window.__mission.pick({type:'marker', id})", _mid)
            page.wait_for_timeout(220)
            close_card(page)
            page.wait_for_function("() => !window.__mission.busy", timeout=30000)
            _h = page.evaluate("""() => {
              const h = document.getElementById('hand');
              const r = h.getBoundingClientRect();
              const t = window.__mission.handTarget;
              const p = t ? window.__mission.world.screenOf('marker', t) : null;
              return {shown: h.classList.contains('show'), tgt: t,
                      x: Math.round(r.left + r.width/2), y: Math.round(r.top),
                      lech: p ? Math.round(Math.hypot(p.x - (r.left + r.width/2),
                                                      p.y - (r.top - 16))) : null,
                      con: window.__mission.world.markers.filter(m => !m.done).length};
            }""")
            if _h["con"] == 0:
                break                                   # het dom -> khong con gi de chi
            if _hpos and (_h["x"], _h["y"]) == _hpos[-1]:
                _stuck_hand.append(_mid)
            _hpos.append((_h["x"], _h["y"]))
            if not _h["shown"] or _h["tgt"] is None or (_h["lech"] or 99) > 30:
                _bad_target.append((_mid, _h["tgt"], _h["lech"]))
        chk(not _stuck_hand,
            "ban tay DOI CHO sau MOI cu cham (du tre cham khac thu tu khai bao)",
            f"dung nguyen sau khi cham: {_stuck_hand}")
        chk(not _bad_target,
            "ban tay luon chi vao DUNG mot dom co that va nam trong khung",
            f"sai: {_bad_target}")


        def _snap():
            return page.evaluate("""() => {
              const layer = document.querySelector('.e2-layer');
              const img = document.querySelector('.e2-img');
              return {
                tf: layer ? layer.style.transform : null,
                x: img ? Math.round(img.getBoundingClientRect().x) : null,
                mks: [...document.querySelectorAll('.e2-mk')].map(m => m.style.left)
              };
            }""")

        _a = _snap()
        _box = page.evaluate("""() => { const r = document.getElementById('stage')
            .getBoundingClientRect();
            return { cx: r.left + r.width/2, cy: r.top + r.height/2 }; }""")
        page.mouse.move(_box["cx"], _box["cy"])
        page.mouse.down()
        for _i in range(1, 11):
            page.mouse.move(_box["cx"] + 30 * _i, _box["cy"])
            page.wait_for_timeout(20)
        page.mouse.up()
        page.wait_for_timeout(500)
        _b = _snap()
        # ⚠️ ĐẢO CHIỀU 02/08/2026 (`004`). Trước đây khối này đòi "KÉO làm ảnh dịch
        #    thật" — nó sinh ra ngày 01/08 để bắt lỗi ngược lại (kéo trên ảnh quả cầu
        #    không dịch được gì). Nay chủ dự án chốt "không có hành động hay hướng dẫn
        #    co kéo gì hết", nên điều đúng phải kiểm là: kéo KHÔNG làm gì cả, ở cả ảnh
        #    lẫn vị trí đốm. Giữ nguyên phép đo, chỉ đổi điều nó khẳng định.
        chk(_a["x"] == _b["x"] and _a["tf"] == _b["tf"],
            "KÉO 300px KHÔNG làm ảnh dịch (bước 1 đã tắt hẳn dragRotate)",
            f"x {_a['x']} -> {_b['x']}")
        chk(_a["mks"] == _b["mks"],
            "7 châu lục ĐỨNG YÊN tại toạ độ thật",
            f"{_a['mks']} -> {_b['mks']}")
        clicked_real = False
        tried = []
        for mid in ids:
            sp = page.evaluate("id => window.__mission.world.screenOf('marker', id)", mid)
            # `visible` đã tính cả chuyện bị chính quả cầu che — marker ở nửa bên
            # kia hành tinh vẫn chiếu vào trong khung, bấm vào đó là bấm vào lưng
            # Trái Đất.
            if not (sp and sp["visible"]):
                continue
            tried.append(mid)
            page.mouse.click(sp["x"], sp["y"])
            page.wait_for_timeout(450)
            if page.evaluate(
                    "() => window.__mission.world.markers.filter(m=>m.done).length") >= 1:
                clicked_real = True
                break
        chk(clicked_real, "BẤM THẬT vào marker trên canvas → điểm được đánh dấu xong",
            f"thử {tried}" if tried else "không marker nào ở nửa gần camera")

        # Thẻ nội dung của châu lục vừa chạm — ĐÂY mới là bài học của bước ①.
        _card1 = read_card(page, timeout=9000)
        chk(_card1 is not None and len(_card1[2]) > 30,
            "chạm châu lục → hiện THẺ có tên + một câu về nó", str(_card1 and _card1[1]))

        n_before = page.evaluate("+document.getElementById('obj-n').textContent.split('/')[0]")
        chk(n_before >= 1, "bảng mục tiêu đếm lên", f"{n_before}/8")
        bar = page.eval_on_selector("#obj-bar", "e => e.getBoundingClientRect().width")
        chk(bar > 2, "thanh tiến độ có bề rộng THẬT (không phải 0px)", f"{bar:.0f}px")

        # ⚠️ ĐẢO CHIỀU 02/08/2026 (`004`): trước đây đòi "KÉO đổi được góc nhìn".
        #    Phép đo giữ nguyên (`facingLatLon()` dùng chung cho cả hai engine), chỉ
        #    đổi điều khẳng định — bước 1 nay không nhận cú kéo nào.
        f0 = page.evaluate("() => window.__mission.world.facingLatLon()")
        page.mouse.move(720, 450)
        page.mouse.down()
        page.mouse.move(880, 470, steps=12)
        page.mouse.up()
        page.wait_for_timeout(300)
        f1 = page.evaluate("() => window.__mission.world.facingLatLon()")
        moved = max(abs(deg_delta(f0["lon"], f1["lon"])), abs(f1["lat"] - f0["lat"]))
        chk(moved < 0.01, "KEO KHONG doi duoc goc nhin o buoc 1", f"lech {moved:.3f} do")

        # Nốt các châu lục còn lại. `busy` là bắt buộc: mỗi cú chạm mở một thẻ nội dung
        # và bước chặn cú chạm chồng trong lúc thẻ còn mở — bấm tiếp lúc đó là mất lượt.
        for mid in ids:
            page.wait_for_function("() => !window.__mission.busy", timeout=20000)
            page.evaluate("id => window.__mission.pick({type:'marker', id})", mid)
            page.wait_for_timeout(200)
            close_card(page)
        page.wait_for_function("() => window.__mission.scanned === 7", timeout=30000)
        chk(True, "chạm đủ 7 châu lục")

        # ── Nhịp (b): câu đố "nước hay đất nhiều hơn?" ──────────────────────────
        say_through(page)
        page.wait_for_selector("#ask.show", timeout=15000)
        _opts = page.eval_on_selector_all(
            "#ask-opts .me-ask-opt", "es => es.map(e => [e.dataset.pick, e.textContent.trim()])")
        chk(len(_opts) == 2, "câu đố có ĐÚNG 2 lựa chọn", str([o[0] for o in _opts]))
        chk({o[0] for o in _opts} == {"water", "land"}, "hai lựa chọn là nước / đất",
            str(sorted(o[0] for o in _opts)))
        _w = [o for o in _opts if o[0] == "water"][0][1]
        _l = [o for o in _opts if o[0] == "land"][0][1]
        # ⚠️ HAI NÚT PHẢI RỘNG BẰNG NHAU. Nhãn VI/EN dài ngắn khác nhau; để nút co theo
        #    chữ thì trẻ đọc ra "chắc cái to hơn là đáp án" — một gợi ý sai hoàn toàn
        #    ngoài ý muốn, và nó không bao giờ hiện ra khi đọc code.
        _bw = page.eval_on_selector_all(
            "#ask-opts .me-ask-opt", "es => es.map(e => Math.round(e.getBoundingClientRect().width))")
        chk(abs(_bw[0] - _bw[1]) <= 1, "hai nút đoán RỘNG BẰNG NHAU (không gợi ý sai)",
            str(_bw))
        chk(len(_w) > 3 and len(_l) > 3, "hai lựa chọn có nhãn tiếng Việt", f"{_w} | {_l}")

        # ⚠️ ĐOÁN SAI TRƯỚC — luật của thiết kế là KHÔNG PHẠT, và luật nào không có
        #    phép kiểm thì sớm muộn có người "sửa" nó đi. Đây là bước ĐẦU TIÊN của cả
        #    nhiệm vụ; một trạng thái thua ở đây là chỗ tệ nhất để đặt nó.
        page.evaluate("window.__mission.answer('land')")
        _ans = read_card(page, timeout=12000)
        chk(_ans is not None, "đoán SAI vẫn hé lộ đáp án (không có trạng thái thua)",
            str(_ans and _ans[3]))
        if _ans:
            chk("71%" in _ans[2], "đáp án nói 71% (số của NASA)", _ans[2][:60])
            chk("29%" in _ans[2] and "còn lại" in _ans[2],
                "29% được gọi là PHẦN CÒN LẠI (không gán cho NASA)", _ans[2][:80])
            chk("ĐÁP ÁN" in _ans[3].upper() or "XEM" in _ans[3].upper(),
                "đoán sai: nhãn thẻ là lời MỜI XEM, không phải lời mắng", _ans[3])

        # ══════════════════════════════════════════════════════════════════
        head("[3] Bước 1 → 2: lưới TAN, KHÔNG tải lại trang")
        page.evaluate("window.__navMark = 'still-here'")
        say_through(page)
        wait_step(page, "timeline")
        chk(page.evaluate("window.__navMark") == "still-here",
            "KHÔNG tải lại trang khi chuyển bước (biến trong window còn nguyên)")
        # Bỏ mảnh `!scene.getObjectByName('__none__')`: nó LUÔN đúng (không có vật thể
        # nào tên như vậy) nên chỉ làm phép kiểm dài ra mà không kiểm thêm gì.
        chk(page.evaluate("() => window.__mission.done.includes('scan')"),
            "bước scan đã ghi xong")
        # `grid_hidden()` trả True/False/None — nó đã gộp cả hai cách dựng lưới (Mesh
        # wireframe ở cảnh 3D, lớp gradient CSS ở cảnh 2D) về MỘT câu trả lời:
        # người chơi còn thấy lưới không.
        grid_off = grid_hidden(page)
        chk(grid_off is not None, "tìm thấy lưới chẩn đoán trong cảnh")
        chk(grid_off is True, "lưới chẩn đoán đã TAN", str(grid_off))

        # ══════════════════════════════════════════════════════════════════
        head("[3b] Bước 2 — dòng thời gian 4,54 tỷ năm (5 mốc) + viên nham thạch")
        say_through(page)
        page.wait_for_selector("#time.show", timeout=15000)
        nodes = page.eval_on_selector_all(
            "#time-rail .me-era-node",
            "es => es.map(e => [e.querySelector('.yr').textContent,"
            " e.querySelector('.nm').textContent, e.disabled])")
        # ⚠️ SỐ MỐC ĐỌC TỪ TRANG, KHÔNG GÁN CỨNG (`window.__mission.eraTotal`). Bước này
        #    đã đi từ 4 lên 5 mốc một lần rồi; gán cứng là lần sau nó báo hỏng đúng lúc
        #    code làm đúng — bài học đã lặp lại đủ nhiều lần trong dự án này.
        _ntot = page.evaluate("window.__mission.eraTotal")
        chk(len(nodes) == _ntot == 5, "5 mốc thời gian", str([n[0] for n in nodes]))
        # ⛔ BỐN CÁI BẪY NỘI DUNG CỦA `005` — mỗi cái là một con số CÓ NGUỒN mà người
        #    sửa sau rất dễ "sửa" thành sai. Nguồn ghi trong khối chú thích `const ERAS`.
        chk(any("4,54 tỷ" in n[0] for n in nodes), "mốc ①: 4,54 tỷ (NPS Precambrian)",
            str([n[0] for n in nodes]))
        chk(any("4,4 tỷ" in n[0] for n in nodes),
            "mốc ②: đại dương 4,4 tỷ (zircon) — KHÔNG còn ghi 3,8 tỷ cho đại dương")
        chk(any("3,8 tỷ" in n[0] for n in nodes),
            "mốc ③: sự sống 3,8 tỷ — KHÔNG phải 3,7")
        chk(any("233" in n[0] for n in nodes),
            "mốc ④: khủng long 233 triệu — KHÔNG phải 230")
        chk(any("66" in n[0] for n in nodes), "mốc ④ kết ở 66 triệu (NPS)")
        chk(any("Ngày nay" in n[0] for n in nodes), "có mốc Ngày nay")
        # Đi ĐÚNG THỨ TỰ: chỉ mốc đầu bấm được, các mốc sau còn khoá
        chk(nodes[0][2] is False and all(n[2] is True for n in nodes[1:]),
            "chỉ mốc ĐẦU mở được, các mốc sau còn khoá",
            str([n[2] for n in nodes]))
        # Bấm mốc chưa tới → bị nhắc, KHÔNG tính tiến độ
        page.evaluate("window.__mission.era(3)")
        page.wait_for_timeout(300)
        chk(page.evaluate("window.__mission.eras") == 0,
            "bấm vượt thứ tự KHÔNG tính là đã xem")

        lit_before_era = pix(page, (0.3, 0.3, 0.4, 0.4))
        seen, rock, _last = play_timeline(page)
        # ══ MỐC CUỐI PHẢI CHỜ TRẺ ĐỌC — năm phép kiểm sinh ra từ một lỗi THẬT (02/08/2026).
        #    `openEra` từng gọi `finishStep('timeline')` ngay ở mốc cuối, mà `outro()` thì
        #    `$('time').classList.remove('show')` → bảng biến mất **cùng lúc chữ hiện ra**.
        #    Bốn mốc đầu không lộ lỗi vì trẻ tự bấm chấm kế tiếp; chỉ mốc cuối tự nhảy.
        #    Chủ dự án chơi thật và báo: *"ấn vào mốc cuối bị cắt luôn phần lý giải, nhìn
        #    như lỗi giật giật, ra màn hình này luôn"*.
        chk(_last["boardShown"] and _last["body"] > 60,
            "mốc CUỐI: bảng còn mở và phần lý giải còn nguyên (không bị cắt)", str(_last))
        chk(not _last["done"], "mốc CUỐI: bước CHƯA tự chốt — phải chờ trẻ bấm")
        chk(_last["okShown"] and _last["okLabel"],
            "mốc CUỐI: hiện nút cho trẻ tự bấm khi đọc xong", str(_last["okLabel"]))
        chk(_last["focused"],
            "mốc CUỐI: nút nhận tiêu điểm sẵn (bàn phím không phải Tab đi tìm)")
        chk(_last["okH"] >= 44, "mốc CUỐI: nút đạt vùng chạm 44px", f"{_last['okH']}px")
        # ⚠️ MỐC CUỐI NAY LÀ CẤU HÌNH CAO NHẤT của bảng bước ②: nó có CẢ tranh (thêm
        #    02/08/2026) LẪN nút. Đo được 1366×768 còn 173px bản đồ — chật nhất trong mọi
        #    mốc, và bản đồ vẫn phải thấy được vì `004` chốt việc đổi tông hành tinh là
        #    NỘI DUNG bài học. Ai làm tranh to hơn thì con số này tụt, và đây là chỗ nói.
        chk(not _last["figHidden"] and _last["cur"].startswith("now-"),
            "mốc CUỐI: có tranh, và tải đúng bản 700 (không phải 1120)", str(_last["cur"]))
        chk(_last["map"] >= 150,
            "mốc CUỐI: bảng chừa lại ≥150px bản đồ dù có cả tranh lẫn nút",
            f"bảng {_last['boardH']}px / còn {_last['map']}px")
        chk(seen == _ntot, f"xem hết {_ntot} mốc", f"{seen}/{_ntot}")
        chk(rock is not None and "🪨" in (rock[0] if rock else ""),
            "mốc dung nham trao THẺ MẪU VẬT viên nham thạch", str(rock))
        if rock:
            chk("Nham Thạch" in rock[1], "thẻ ghi 'Nham Thạch Cổ Đại'", rock[1])
            chk("KHO MẪU VẬT" in rock[3].upper(),
                "thẻ nói rõ đã lưu vào Kho Mẫu Vật", rock[3])
        chk(page.eval_on_selector_all("#time-rail .me-era-node.ok", "es => es.length") == _ntot,
            f"cả {_ntot} mốc chuyển sang trạng thái đã xem")
        body = page.eval_on_selector("#time-p", "e => e.textContent")
        chk(len(body) > 60, "khối nội dung mốc có bài đọc thật", f"{len(body)} ký tự")

        page.wait_for_function("() => window.__mission.done.includes('timeline')", timeout=20000)
        say_through(page)
        wait_step(page, "sun")
        chk(page.evaluate("window.__navMark") == "still-here",
            "bước 2 → 3 vẫn KHÔNG tải lại trang")
        # Tông hành tinh phải TRẢ VỀ bình thường sau bước thời gian, không kẹt màu dung nham
        chk(page.eval_on_selector("#stage", "e => e.className.indexOf('era-') < 0"),
            "hết bước thời gian thì filter đổi tông đã BỎ, hành tinh về màu thật",
            page.eval_on_selector("#stage", "e => e.className || '(khong co class)'"))

        # ══════════════════════════════════════════════════════════════════
        head("[4] Bước 3 — TRẺ ĐOÁN TRƯỚC, rồi Mặt Trời mới tắt; sau đó BA VÙNG KHÍ HẬU")
        # ══ BA PHÉP KIỂM Ở ĐÂY ĐÃ ĐẢO CHIỀU 02/08/2026, và lý do là một LỖI THIẾT KẾ
        #    đã sửa, không phải một hành vi bị nới lỏng.
        #    Khối cũ đòi: vào bước là hành tinh TỐI SẴN → trẻ xoay camera đi TÌM Mặt
        #    Trời → chạm cho nó cháy. Chủ dự án chơi thật và bác: nút `.e2-sun` neo
        #    `top:9%; right:8%` của khung, mà bản đồ đã lùi hết cỡ và phủ kín, nên ngôi
        #    sao **lẫn vào chính bức ảnh Trái Đất** — trẻ không tìm ra. Đúng cái bẫy
        #    bước `rotation` bản 3D đã mắc, và bộ smoke cũ che nó bằng cách "kéo tới 40
        #    lần cho tới khi thấy" — một việc không đứa trẻ nào làm.
        #    Nay: bản đồ ĐANG SÁNG → Comet hỏi "nếu Mặt Trời tắt thì sao?" → **cú đoán
        #    của trẻ chính là thứ làm màn hình tối đi** → kể 3 vai trò → sáng lại.
        #    ⚠️ Vì thế thứ tự đo cũng đảo: SÁNG trước, TỐI sau, rồi SÁNG lại.
        say_through(page)
        page.wait_for_selector("#ask.show", timeout=20000)
        _sopts = page.eval_on_selector_all(
            "#ask-opts .me-ask-opt", "es => es.map(e => e.dataset.pick)")
        chk(sorted(_sopts) == ["cold", "plant", "rain"],
            "câu đố 3 lựa chọn: lạnh · cây · mưa", str(sorted(_sopts)))
        chk(page.evaluate("() => window.__mission.world.sunOn") is not False,
            "TRƯỚC khi trẻ đoán: Mặt Trời còn SÁNG (cú tối phải là HỆ QUẢ của cú đoán)")
        p_lit0 = pix(page, (0.3, 0.3, 0.4, 0.4))

        # ⚠️ ĐOÁN LỰA CHỌN NÀO CŨNG PHẢI ĐI TIẾP — cả ba đều đúng, cố ý: Mặt Trời làm
        #    cả ba việc cùng lúc, và chính điều đó là bài học. Chọn `plant` (không phải
        #    lựa chọn đầu) để phép kiểm không vô tình chỉ chạy nhánh mặc định.
        page.evaluate("window.__mission.answer('plant')")
        page.wait_for_timeout(1800)
        p_dark = pix(page, (0.3, 0.3, 0.4, 0.4))
        chk(p_dark["avg"] < p_lit0["avg"] * 0.8,
            "trẻ đoán xong → hành tinh CHÌM VÀO BÓNG TỐI",
            f"{p_lit0['avg']:.1f} → {p_dark['avg']:.1f}")
        chk(page.evaluate("() => window.__mission.world.sunOn") is False,
            "Mặt Trời đã TẮT")
        # Ba vai trò kể bằng lời thoại (nhiệt → nước lỏng · quang hợp · thời tiết),
        # rồi Mặt Trời bật lại. Bấm hết lời thoại là tới đó.
        say_through(page, limit=8)
        page.wait_for_function("() => window.__mission.world.sunOn === true", timeout=25000)
        chk(True, "kể xong ba vai trò thì Mặt Trời BẬT LẠI")

        # ══ ĐẢO CHIỀU HẲN 02/08/2026 (`docs/decisions/005`) ═══════════════════════
        # ⛔ KHỐI CŨ Ở ĐÂY ĐO "RANH GIỚI NGÀY/ĐÊM TRÊN BẢN ĐỒ PHẲNG" — quét profile 32
        #    cột ngang qua đĩa hành tinh và đòi một BƯỚC NHẢY > 12 điểm sáng. Nó bảo vệ
        #    đúng cái mà chủ dự án đã BÁC bằng ảnh chụp: gradient `.e2-terminator` trông
        #    như một bức tường đen. Bài học ngày/đêm nay dạy trên QUẢ CẦU 3D ở
        #    `explorer.html` (nơi ánh sáng là `PointLight` gắn vào Mặt Trời thật, đo
        #    được hai nửa chênh 106,5 điểm) — nên phép kiểm đó chuyển sang bộ đo của
        #    trang kia, không phải bị nới lỏng.
        # Điều PHẢI kiểm ở đây bây giờ là điều ngược lại: KHÔNG còn vùng tối nào.
        chk(page.eval_on_selector(
                "#stage", "e => e.className.indexOf('e2-terminator') < 0"),
            "KHÔNG còn `.e2-terminator` (vùng tối đã bỏ hẳn — 005 mục 2)",
            page.eval_on_selector("#stage", "e => e.className || '(khong co class)'"))
        _lit_after = pix(page, (0.3, 0.3, 0.4, 0.4))
        chk(_lit_after["avg"] > p_dark["avg"] * 1.5,
            "Mặt Trời cháy thì bản đồ SÁNG HẲN LÊN",
            f"{p_dark['avg']:.1f} → {_lit_after['avg']:.1f}")

        # ── Nhịp (b): ba vùng khí hậu ────────────────────────────────────────────
        say_through(page)
        page.wait_for_function("() => window.__mission.world.markers.length === 3", timeout=20000)
        _zids = page.evaluate("window.__mission.world.markers.map(m => m.id)")
        chk(sorted(_zids) == ["equator", "polar", "temperate"],
            "3 vùng khí hậu: xích đạo · ôn đới · cực", str(sorted(_zids)))
        # ⚠️ CẢ BA PHẢI TRONG KHUNG. Khác bước ① (7 châu lục trải 234° kinh độ, phải
        #    lướt bản đồ trên màn hẹp), ba vùng này CÙNG kinh độ ~16–20° nên chọn được
        #    một khung nhìn ôm hết ở MỌI cỡ màn — và vì thế ở đây vẫn đòi 3/3.
        _zvis = page.evaluate(
            "() => window.__mission.world.markers"
            ".filter(m => window.__mission.world.screenOf('marker', m.id).visible).length")
        chk(_zvis == 3, "cả 3 vùng khí hậu trong khung ngay lúc hiện ra", f"{_zvis}/3")
        _zone_facts = []
        for _zid in _zids:
            page.wait_for_function("() => !window.__mission.busy", timeout=20000)
            page.evaluate("id => window.__mission.pick({type:'marker', id})", _zid)
            page.wait_for_timeout(200)
            # `read_card` tự bấm "Đã hiểu!" — ĐỪNG gọi `close_card` trước nó, không thì
            # thẻ đóng mất rồi mới đi đọc và mọi câu giải thích ra rỗng.
            _c = read_card(page, timeout=12000)
            if _c:
                _zone_facts.append(_c[2])
        chk(page.evaluate("window.__mission.zones") == 3, "chạm đủ 3 vùng khí hậu")
        chk(len(_zone_facts) == 3 and all(len(f) > 40 for f in _zone_facts),
            "mỗi vùng có một câu giải thích thật", str([len(f) for f in _zone_facts]))
        # ⛔ QUAN NIỆM SAI PHỔ BIẾN NHẤT: "xích đạo nóng vì gần Mặt Trời hơn". Không đủ
        #    nếu chỉ TRÁNH không nhắc — trẻ đến đây với sẵn cách hiểu đó trong đầu, nên
        #    câu kết phải BÁC nó ra mặt. Đo trên chữ THẬT hiện trên màn hình.
        _joined = " ".join(_zone_facts)
        chk("xiên" in _joined and "trải" in _joined,
            "ba thẻ giải thích bằng GÓC CHIẾU và việc ánh sáng bị TRẢI RỘNG", _joined[:70])
        chk("gần Mặt Trời" not in _joined,
            "KHÔNG thẻ nào nói 'vì gần Mặt Trời hơn'")

        page.wait_for_function("() => window.__mission.done.includes('sun')", timeout=20000)
        _sayline = page.eval_on_selector("#say-line", "e => e.textContent")
        chk("Không phải" in _sayline and "xa Mặt Trời" in _sayline,
            "câu kết BÁC HẲN cách hiểu 'vì gần Mặt Trời hơn'", _sayline[:80])
        say_through(page)
        wait_step(page, "life")

        # ══════════════════════════════════════════════════════════════════
        head("[4b] Bước 4 — LÁT CẮT TRÁI ĐẤT: đoán độ cao rồi hé lộ")
        # ⚠️⚠️ SÁU PHÉP KIỂM Ở MỤC NÀY ĐÃ ĐẢO CHIỀU 02/08/2026, và lý do KHÔNG phải là
        #    "đổi cho mới". Bản cũ chạm 4 marker để mở thẻ; đếm ngân sách khuôn thì
        #    "chạm dấu hiệu trên bản đồ" đã dùng ở ① và ③, nên ở đây là lần thứ 3 —
        #    vượt luật `docs/decisions/002` ("không dùng một khuôn quá 2 lần").
        #    Phép kiểm cũ vì thế đang BẢO VỆ ĐÚNG TRẠNG THÁI VI PHẠM: sửa cho đúng luật
        #    thì nó báo hỏng. Cùng loại việc đã làm với nút Mặt Trăng và với 6 phép kiểm
        #    của `004`. Cái phải giữ nguyên là: 4 mẫu vật, 4 toạ độ thật, và trẻ không
        #    bao giờ kẹt.
        say_through(page)
        page.wait_for_function("() => window.__mission.world.markers.length === 4", timeout=15000)
        bids = page.evaluate("window.__mission.world.markers.map(m => m.id)")
        chk(sorted(bids) == ["animal", "forest", "mountain", "water"],
            "đúng 4 mẫu: nước · rừng · động vật · núi", str(sorted(bids)))
        page.wait_for_selector("#xsec.show", timeout=15000)
        rungs = page.eval_on_selector_all("#xsec-col .xsec-rung",
                                          "es => es.map(e => e.dataset.rank)")
        chk(rungs == ["1", "2", "3", "4"], "lát cắt có đúng 4 nấc, TRÊN xuống DƯỚI",
            str(rungs))
        chk(page.eval_on_selector_all("#xsec-col .xsec-sea", "es => es.length") == 1,
            "có ĐÚNG một đường mực nước biển")
        # Nó phải nằm GIỮA nấc 3 và nấc 4 — đó là mốc duy nhất trên cột có nghĩa vật lý,
        # đặt sai chỗ thì nấc "dưới mặt nước" thành vô nghĩa.
        seay = page.evaluate("""() => {
          const s = document.querySelector('#xsec-col .xsec-sea').getBoundingClientRect();
          const r3 = document.querySelector('.xsec-rung[data-rank="3"]').getBoundingClientRect();
          const r4 = document.querySelector('.xsec-rung[data-rank="4"]').getBoundingClientRect();
          return [r3.bottom <= s.top + 1, s.bottom <= r4.top + 1];
        }""")
        chk(all(seay), "đường mực nước biển nằm GIỮA nấc 3 và nấc 4", str(seay))

        # ⚠️ NƠI ĐẦU TIÊN CỐ TÌNH ĐOÁN SAI. "Đoán sai không phạt" là một luật của thiết
        #    kế, mà luật nào không có phép kiểm thì sớm muộn có người "sửa" nó đi thành
        #    một cửa chặn. Phải chứng minh: chip vẫn về ĐÚNG nấc, và bước vẫn đi tiếp.
        page.wait_for_function("() => !window.__mission.busy", timeout=30000)
        page.wait_for_function("() => window.__mission.rungWanted !== null", timeout=20000)
        want0 = page.evaluate("window.__mission.rungWanted")
        wrong0 = 1 if want0 != 1 else 2
        qtext = page.eval_on_selector("#xsec-q", "e => e.textContent")
        chk(qtext and len(qtext) > 6 and "{nm}" not in qtext,
            "câu hỏi nêu đúng TÊN nơi đang hỏi (token {nm} đã được thay)", qtext)
        # ⚠️ CÚ ĐOÁN NÀY ĐI BẰNG BÀN PHÍM THẬT, KHÔNG GỌI `rung()`. Bàn phím phải tương
        #    đương chuột chứ không phải "có nhãn trợ năng" — và đây đúng chỗ dự án đã
        #    trả giá một lần: bước kéo-thả từng KHÔNG chơi được bằng bàn phím suốt một
        #    thời gian dài mà không gì báo lỗi, vì thẻ vốn đã là `<button>` nên trông
        #    như bấm được. Lái bằng `rung()` thì lỗi đó lặp lại y nguyên.
        page.eval_on_selector('.xsec-rung[data-rank="1"]', "e => e.focus()")
        for _ in range(wrong0 - 1):
            page.keyboard.press("ArrowDown")
        _focus = page.evaluate("() => document.activeElement.dataset.rank")
        chk(_focus == str(wrong0), "mũi tên ↓ đi được giữa các nấc", _focus)
        page.keyboard.press("Enter")
        page.wait_for_function(
            "() => document.getElementById('card').classList.contains('show')", timeout=20000)
        chk(page.eval_on_selector_all("#xsec-col .xsec-rung:not([disabled])",
                                      "es => es.length") == 0,
            "đang hé lộ thì 4 nấc bị khoá (một cú bấm lỡ tay không rơi vào câu sau)")
        chk(page.evaluate(f"""() => {{
              const box = document.querySelector('[data-chips="{want0}"]');
              return !!box && box.children.length === 1;
            }}"""),
            f"đoán SAI vẫn thả chip vào ĐÚNG nấc {want0} (không phạt, không chặn)")
        chk(page.evaluate("document.getElementById('xsec-hint').textContent").strip() != "",
            "đoán sai có câu phản hồi, không im lặng")

        cards = [page.evaluate(
            "() => [document.getElementById('card-ic').textContent,"
            " document.getElementById('card-nm').textContent,"
            " document.getElementById('card-fact').textContent,"
            " document.getElementById('card-sub').textContent,"
            " document.getElementById('card-sub').hidden]")]
        page.click("#card-ok")   # thẻ KHÔNG tự đóng — xem ghi chú ở `read_card`
        page.wait_for_function(
            "() => !document.getElementById('card').classList.contains('show')", timeout=12000)

        # Ba nơi còn lại đoán ĐÚNG.
        for _ in range(3):
            page.wait_for_function("() => !window.__mission.busy", timeout=30000)
            page.wait_for_function("() => window.__mission.rungWanted !== null", timeout=20000)
            page.evaluate("() => window.__mission.rung(window.__mission.rungWanted)")
            try:
                page.wait_for_function(
                    "() => document.getElementById('card').classList.contains('show')",
                    timeout=25000)
                cards.append(page.evaluate(
                    "() => [document.getElementById('card-ic').textContent,"
                    " document.getElementById('card-nm').textContent,"
                    " document.getElementById('card-fact').textContent,"
                    " document.getElementById('card-sub').textContent,"
                    " document.getElementById('card-sub').hidden]"))
                page.click("#card-ok")
                page.wait_for_function(
                    "() => !document.getElementById('card').classList.contains('show')",
                    timeout=12000)
            except Exception:
                cards.append(None)

        chk(len(cards) == 4 and all(cards), "cả 4 nơi đều bật THẺ THU THẬP",
            f"{sum(1 for c in cards if c)}/4")
        # Mỗi nấc đúng MỘT nơi — cột xếp xong là một lát cắt đọc được, không phải đống chip.
        _per = page.evaluate("""() => [1,2,3,4].map(r =>
              document.querySelector('[data-chips="'+r+'"]').children.length)""")
        chk(_per == [1, 1, 1, 1],
            "4 nơi rải đều 4 nấc (không nấc nào trống, không nấc nào 2 chip)", str(_per))
        if all(cards):
            facts = [c[2] for c in cards]
            subs = [c[3] for c in cards]
            chk(all(len(f) > 12 for f in facts) and len(set(facts)) == 4,
                "4 thẻ có 4 câu kiến thức KHÁC nhau")
            chk(all(len(s) > 12 for s in subs) and len(set(subs)) == 4,
                "4 thẻ có 4 câu HÉ LỘ ĐỘ CAO khác nhau", str([s[:24] for s in subs]))
            chk(all(c[4] is False for c in cards), "dòng phụ của thẻ KHÔNG bị ẩn ở bước ④")
            # ⚠️ HAI CON SỐ DUY NHẤT CỦA BƯỚC NÀY, cả hai đều đã tra nguồn 02/08/2026.
            #    Nguồn NASA nói "up to 4,000 meters"; nguồn NOAA nói "the ocean … about
            #    3,682 meters". Ai sửa hai số này thì phải mở lại nguồn, không phải nhớ.
            chk(any("4.000" in s for s in subs),
                "câu Nam Cực dùng đúng con số NASA (cao tới 4.000 m)",
                str([s[:40] for s in subs]))
            chk(any("3.682" in s for s in subs),
                "câu đáy đại dương dùng đúng con số NOAA (~3.682 m)")
            # ⚠️ NOAA nói về ĐẠI DƯƠNG NÓI CHUNG, không riêng Đại Tây Dương. Gán con số
            #    cho riêng Đại Tây Dương là dẫn nguồn cho một câu nguồn không nói.
            _d = [s for s in subs if "3.682" in s]
            chk(_d and "Đại Tây Dương" not in _d[0],
                "KHÔNG gán con số của NOAA cho riêng Đại Tây Dương", str(_d))
            # ⚠️ 70% → 71% (02/08/2026). Không phải nới phép kiểm mà là SỬA MỘT XUNG
            #    ĐỘT SỐ LIỆU: đốm 🌊 của bước 1 dẫn NASA `science.nasa.gov/earth/facts/`
            #    ("the global ocean … covers about 71% of the planet's surface"), trong
            #    khi thẻ mẫu vật này vẫn ghi 70% — hai chỗ trong CÙNG một nhiệm vụ nói
            #    hai con số cho cùng một sự thật. Đã thống nhất 71% ở cả `mission-earth.html`
            #    lẫn `learningdata/astronomy/earth_codex.json`.
            chk(any("71" in f for f in facts),
                "thẻ Nước nói 'Nước bao phủ 71% Trái Đất' (khớp nguồn NASA của bước 1)",
                str([f[:40] for f in facts]))
            chk(any("Oxy" in f or "oxy" in f.lower() for f in facts),
                "thẻ Rừng nói về Oxy để hít thở")

        page.wait_for_function("() => window.__mission.done.includes('life')", timeout=25000)
        say_through(page)
        wait_step(page, "energy")

        # ══════════════════════════════════════════════════════════════════
        head("[5] Bước 5 — thay 3 ống khói bằng năng lượng sạch, khói đen TAN")
        say_through(page)
        srcs = page.eval_on_selector_all(
            "#energy-tray .me-gem", "es => es.map(e => e.textContent.trim())")
        chk(len(srcs) == 3, "3 nguồn năng lượng sạch", str(srcs))
        joined = " ".join(srcs)
        chk("☀️" in joined and "🌬️" in joined and "🌊" in joined,
            "đủ 3 nguồn: pin mặt trời ☀️ · cối xoay gió 🌬️ · thuỷ điện 🌊", joined)
        chk("Mặt Trời" in joined and "Gió" in joined and "Thuỷ Điện" in joined,
            "3 nguồn có TÊN TIẾNG VIỆT", joined)
        # ⚠️ ĐỔI SELECTOR 02/08/2026: ba ống khói đã dời từ BẢNG xuống BẢN ĐỒ (chủ dự
        #    án: *"nên rải 3 ống khói tại 3 vùng khác nhau lên bản đồ 2D"*). Chúng nay là
        #    marker của cảnh `.e2-mk.e2-stack` với `data-zone`, không còn là phần tử của
        #    `#energy-slots` (khối đó nay luôn rỗng).
        chk(page.eval_on_selector_all(".e2-mk.e2-stack", "es => es.length") == 3,
            "3 ống khói đang nhả khói TRÊN BẢN ĐỒ")
        # Ống khói phải neo đúng toạ độ thật và nhìn thấy được — nếu không thì không kéo
        # thẻ vào được, mà bước lại không có đường nào khác để qua.
        _svis = page.evaluate(
            "() => ['st1','st2','st3'].filter(id =>"
            " window.__mission.world.screenOf('marker', id).visible).length")
        chk(_svis == 3, "cả 3 ống khói nằm trong khung", f"{_svis}/3")

        # THẢ SAI trước — không bị phạt (cùng nguyên tắc với bảng 3 viên ngọc)
        w0 = page.eval_on_selector_all("#energy-tray .me-gem", "es => es.map(e=>e.dataset.want)")
        bad_zone = next(z for z in ["st1", "st2", "st3"] if z != w0[0])
        drag_to(page, f'#energy-tray .me-gem[data-want="{w0[0]}"]',
                f'.e2-mk.e2-stack[data-zone="{bad_zone}"]')
        chk(page.eval_on_selector(f'.e2-mk.e2-stack[data-zone="{bad_zone}"]',
                                  "e => !e.classList.contains('ok')"),
            "thả SAI ống: ống không sáng lên")
        chk(page.eval_on_selector(f'#energy-tray .me-gem[data-want="{w0[0]}"]',
                                  "e => !e.classList.contains('used')"),
            "thả SAI ống: thẻ nguồn NẢY VỀ chỗ cũ")
        e_hint = page.eval_on_selector("#energy-hint", "e => e.textContent")
        chk("thử" in e_hint.lower(), "thả SAI ống: câu KHÍCH LỆ, không mắng", e_hint.strip())
        page.wait_for_timeout(2400)

        placed, smog0, smog1 = play_energy(page)
        chk(placed == 3, "KÉO-THẢ THẬT đủ 3 ống khói thành trạm điện sạch", f"{placed}/3")
        chk(smog0 > 0.9, "trước khi thay: khói đen phủ kín (--smog ≈ 1)", f"{smog0:.2f}")
        chk(smog1 < 0.05, "sau khi thay đủ 3: khói TAN HẾT (--smog ≈ 0)", f"{smog1:.2f}")
        page.wait_for_function("() => window.__mission.done.includes('energy')", timeout=20000)
        say_through(page)
        wait_step(page, "eco")
        chk(page.evaluate("window.__navMark") == "still-here",
            "bước 5 → 6 vẫn KHÔNG tải lại trang")

        # ══════════════════════════════════════════════════════════════════
        head("[6] Bước 6 — Eco-Hero: phân loại NÊN / KHÔNG NÊN")
        say_through(page)
        page.wait_for_selector("#eco.show", timeout=15000)
        deck = page.eval_on_selector_all(
            "#eco-deck .me-gem",
            "es => es.map(e => [e.dataset.card, e.dataset.want, e.querySelector('.tx').textContent])")
        chk(len(deck) == 7, "7 thẻ hành động", str(len(deck)))
        goods = [d for d in deck if d[1] == "good"]
        bads = [d for d in deck if d[1] == "bad"]
        chk(len(goods) == 4 and len(bads) == 3,
            "4 việc NÊN làm + 3 việc KHÔNG NÊN làm", f"{len(goods)} / {len(bads)}")
        txt = " | ".join(d[2] for d in deck)
        for want in ("Tắt đèn", "bình nước cá nhân", "Trồng cây", "Phân loại rác",
                     "Vứt rác", "nước sạch", "túi nilon"):
            chk(want in txt, f"có thẻ '{want}'", "")
        chk(page.eval_on_selector_all("#eco .me-bucket", "es => es.length") == 2,
            "đúng 2 rổ")
        b_lb = page.evaluate("() => [document.getElementById('eco-good').textContent,"
                             " document.getElementById('eco-bad').textContent]")
        chk("NÊN LÀM" in b_lb[0] and "KHÔNG NÊN" in b_lb[1],
            "rổ ghi 'NÊN LÀM' / 'KHÔNG NÊN LÀM'", str(b_lb))

        # THẢ SAI RỔ trước — không bị phạt
        drag_to(page, f'#eco-deck .me-gem[data-card="{goods[0][0]}"]',
                '#eco .me-bucket[data-zone="bad"]')
        chk(page.evaluate("window.__mission.sorted") == 0,
            "thả SAI rổ: KHÔNG tính là đã phân loại")
        chk(page.eval_on_selector(f'#eco-deck .me-gem[data-card="{goods[0][0]}"]',
                                  "e => !e.classList.contains('used')"),
            "thả SAI rổ: thẻ NẢY VỀ chỗ cũ, kéo lại được")
        ec_hint = page.eval_on_selector("#eco-hint", "e => e.textContent")
        chk("thử" in ec_hint.lower(), "thả SAI rổ: câu KHÍCH LỆ, không mắng", ec_hint.strip())
        # Box thoại phải được NHẤC LÊN, không đè lên hai cái rổ đang phải kéo thẻ vào
        overlap = page.evaluate("""() => {
          const s = document.getElementById('say').getBoundingClientRect();
          const b = document.querySelector('#eco .me-bucket').getBoundingClientRect();
          return !(s.bottom <= b.top || s.top >= b.bottom);
        }""")
        chk(overlap is False, "box thoại khích lệ KHÔNG đè lên rổ phân loại")
        page.wait_for_timeout(2400)

        sorted_n = play_eco(page)
        chk(sorted_n == 7, "KÉO-THẢ THẬT phân loại đúng cả 7 thẻ", f"{sorted_n}/7")
        chk(page.eval_on_selector_all('#eco-good-drop .me-chip', "es => es.length") == 4,
            "rổ NÊN LÀM có đúng 4 thẻ")
        chk(page.eval_on_selector_all('#eco-bad-drop .me-chip', "es => es.length") == 3,
            "rổ KHÔNG NÊN có đúng 3 thẻ")

        # Huy hiệu Chiến Binh Xanh — do SERVER mở, hiện sau khi báo bước xong.
        # ⚠️ `say_through(page)` (limit mặc định 6) chờ 4s cho mỗi lần thử vô ích, mà
        # thẻ huy hiệu TỰ ĐÓNG sau 3,4s → nó hiện rồi tắt xong trong đúng khoảng chờ đó
        # và `read_card` sau đó không thấy gì. Bấm ĐÚNG MỘT lần rồi bắt thẻ ngay.
        page.wait_for_function("() => window.__mission.done.includes('eco')", timeout=20000)
        say_through(page, 1)
        badge_card = read_card(page, timeout=12000)
        chk(badge_card is not None, "thẻ chúc mừng huy hiệu hiện ra", str(badge_card))
        if badge_card:
            chk("🌱" in badge_card[0], "huy hiệu dùng emoji 🌱 của js/badges.js", badge_card[0])
            chk("Chiến Binh Xanh" in badge_card[1],
                "tên huy hiệu lấy từ js/badges.js (không gõ lại)", badge_card[1])
        chk("eco-warrior" in page.evaluate("window.__mission.badges"),
            "huy hiệu ghi nhận từ `newBadges` của SERVER, không phải client tự mở",
            str(page.evaluate("window.__mission.badges")))

        say_through(page)
        wait_step(page, "core")

        # ══════════════════════════════════════════════════════════════════
        head("[7] Bước 7 — HỒ SƠ TRÁI ĐẤT: ba dòng đã học + MỘT cú đóng dấu")
        # ══ CẢ MỤC NÀY ĐẢO CHIỀU 02/08/2026. Khối cũ đo bảng kéo 3 "viên ngọc" (Ngọc
        #    Mặt Trời · Ngọc Giọt Nước · Ngọc Khí Quyển) vào 3 ô. Chủ dự án chơi thật rồi
        #    bác: *"bỏ nhiệm vụ kéo viên ngọc đi, ko logic"* — ba viên ngọc là VẬT THỂ BỊA,
        #    không có trong bất cứ thứ gì sáu bước trước dạy, trong khi cả nhiệm vụ đứng
        #    trên một bức ảnh vệ tinh THẬT với toạ độ THẬT.
        #    Nay là ba DÒNG CHỮ (ba thứ nhiệm vụ đã dạy) + một cú đóng dấu.
        #    ⚠️ VÀ ĐÂY LÀ CHỖ PHẢI CANH: bước cuối KHÔNG ĐƯỢC biến thành câu đố. Nó nằm
        #       ngay trước màn thưởng; bắt trả lời đúng mới cho qua là dựng một cửa chặn
        #       ở đúng chỗ trẻ tưởng đã xong. Vì thế phép kiểm dưới đây đòi **0 lựa chọn**.
        say_through(page)
        page.wait_for_selector("#core.show", timeout=10000)
        _lines = page.eval_on_selector_all(
            "#core-slots .me-fileline", "es => es.map(e => e.textContent.trim())")
        chk(len(_lines) == 3, "hồ sơ có ĐÚNG ba dòng", str(len(_lines)))
        chk(all("✓" in l for l in _lines), "mỗi dòng có dấu ✓")
        # Ba dòng phải là ba thứ các bước TRƯỚC đã dạy — thêm dòng thứ tư là nhồi kiến
        # thức mới vào đúng lúc trẻ tưởng đã xong.
        _j = " ".join(_lines)
        chk("71" in _j, "dòng NƯỚC nhắc lại 71% (bước ①)", _j[:60])
        chk("góc chiếu" in _j, "dòng NHIỆT nhắc lại góc chiếu (bước ③)")
        chk("oxy" in _j.lower(), "dòng KHÍ nhắc lại oxy để thở")
        chk(page.eval_on_selector_all("#core .me-ask-opt, #core-slots .me-slot",
                                      "es => es.length") == 0,
            "bước cuối KHÔNG có câu đố và KHÔNG còn ô kéo-thả nào")

        # ⛔ KHÔNG CÒN VIÊN NGỌC NÀO — canh cả dấu vết chữ, vì đây là thứ đã bị bác một
        #    lần và người sửa sau rất dễ dựng lại "cho có tương tác".
        _core_txt = page.eval_on_selector("#core", "e => e.textContent")
        chk("ngọc" not in _core_txt.lower() and "gem" not in _core_txt.lower(),
            "không còn chữ 'ngọc' nào ở bước cuối", _core_txt[:60])

        _stamp = page.query_selector("#core-stamp")
        chk(_stamp is not None, "có ĐÚNG một nút đóng dấu")
        chk(page.eval_on_selector_all("#core button", "es => es.length") == 1,
            "bước cuối có ĐÚNG MỘT cái nút (không phải một bảng thao tác)")
        _sz = _stamp.bounding_box() if _stamp else None
        chk(_sz and _sz["height"] >= 44,
            "nút đóng dấu đạt vùng chạm 44px", str(_sz and round(_sz["height"])))
        chk("core" not in page.evaluate("window.__mission.done"),
            "chưa bấm thì bước chưa tính là xong")
        _stamp.click()
        page.wait_for_function("() => window.__mission.done.includes('core')", timeout=20000)
        chk(True, "bấm đóng dấu → bước cuối hoàn thành")
        chk(page.eval_on_selector("#core-stamp", "e => e.disabled") is True,
            "bấm rồi thì nút bị khoá (không đóng dấu hai lần)")

        head("[8] Màng khí quyển + màn tổng kết")
        # `core.outro()` bọc màng khí quyển RỒI Comet nói câu cuối — câu đó chờ
        # trẻ bấm "Tiếp tục", nên phải bấm qua nó mới tới màn tổng kết.
        page.wait_for_timeout(2200)
        shielded_live = page.evaluate(SHIELD_JS)
        say_through(page)
        page.wait_for_selector("#win.show", timeout=30000)
        chk(True, "màn tổng kết mở ra")
        w = page.evaluate("""() => ({
          h: document.getElementById('win-h').textContent,
          badge: document.getElementById('win-badge').textContent,
          sub: document.getElementById('win-badge-sub').textContent,
          tt: document.getElementById('win-rw-tt').textContent,
          codex: document.getElementById('win-rw-codex').textContent,
          xp: document.getElementById('win-rw-xp').textContent,
          nextUp: document.getElementById('win-next').textContent,
          badges: document.getElementById('win-badges').textContent,
          badgesHidden: document.getElementById('win-rw-badges').classList.contains('hide'),
          // ⚠️ ĐẢO CHIỀU 30/07/2026: trước đây đo `win-moon`. Nút/khối Mặt Trăng đã
          //    bị bỏ hẳn, nên giờ đo là KHÔNG CÒN dấu vết nào.
          moonGone: !document.getElementById('win-moon') &&
                    !/🌙|MẶT TRĂNG|THE MOON/i.test(document.getElementById('win').textContent),
          nextBtn: document.getElementById('win-missions')
                   ? document.getElementById('win-missions').disabled : null,
          ttImg: document.querySelector('#win .rw img') &&
                 document.querySelector('#win .rw img').getAttribute('src'),
          calls: window.__calls
        })""")
        chk("HOÀN THÀNH" in w["h"].upper(), "tiêu đề 'SỨ MỆNH TRÁI ĐẤT HOÀN THÀNH'", w["h"])
        chk("ROOKIE" in w["badge"].upper() or "TẬP SỰ" in w["badge"].upper(),
            "huy hiệu ROOKIE ASTRONAUT", w["badge"])
        chk("Tập Sự" in w["sub"] or "Rookie" in w["sub"],
            "phụ đề 'Huy Hiệu Phi Hành Gia Tập Sự'", w["sub"])
        # ⚠️ Đổi 07/08/2026 từ so BẰNG `"img/tt.png"` sang so ĐUÔI. `ttImg()` nay
        #    ghép thêm gốc site suy từ `document.currentScript` — bắt buộc, vì
        #    trang chủ có hai bản ở hai độ sâu thư mục (`/` và `/en/`) và chuỗi
        #    cứng sẽ 404 ở bản `/en/`. Điều phép kiểm này muốn biết vẫn nguyên:
        #    dùng ĐÚNG ảnh thiên thạch tím, không phải một ảnh khác.
        chk(w["ttImg"].endswith("img/tt.png"),
            "phần thưởng dùng ĐÚNG ảnh thiên thạch tím của game", str(w["ttImg"]))
        # Tổng theo đúng bảng luật 7 bước ở Services/Missions.cs (xem STUB_PROGRESS)
        chk(str(STUB_METEORS) in w["tt"],
            f"số thiên thạch tím = {STUB_METEORS}, đúng bảng luật của server", w["tt"])
        chk(str(STUB_XP) in w["xp"], f"XP = {STUB_XP}, đúng bảng luật của server", w["xp"])
        chk(f"{STUB_CODEX_TOTAL}/{STUB_CODEX_TOTAL}" in w["codex"],
            f"Hồ Sơ Trái Đất {STUB_CODEX_TOTAL}/{STUB_CODEX_TOTAL} mẫu Codex", w["codex"])
        chk(w["badgesHidden"] is False and "Chiến Binh Xanh" in w["badges"],
            "màn tổng kết liệt kê huy hiệu 🌱 Chiến Binh Xanh mở thêm trong lượt",
            w["badges"])
        chk("Tập Sự" not in w["badges"] and "Rookie" not in w["badges"],
            "KHÔNG liệt kê lại Phi Hành Gia Tập Sự (đã có khối huân chương riêng)",
            w["badges"])
        # ⚠️ ĐẢO CHIỀU: yêu cầu (chốt 30/07/2026) là BỎ HẲN mọi thứ về Mặt Trăng.
        #    Nhiệm vụ đó chưa tồn tại, nên một nút bấm không được vẫn là một lời hứa
        #    về thứ không có. Phép kiểm cũ ở đây chính là thứ đã GIỮ lỗi sống: nó
        #    khẳng định nút Mặt Trăng phải tồn tại.
        chk(w["moonGone"] is True,
            "màn tổng kết KHÔNG còn dấu vết Mặt Trăng nào")
        # Bỏ trắng thì màn tổng kết thành đường cụt → phải có việc tiếp theo CÓ THẬT.
        chk(w["nextBtn"] is False,
            "có nút 'việc tiếp theo' và nó BẤM ĐƯỢC (missions.html có thật)",
            str(w["nextBtn"]))
        chk("Nhiệm Vụ" in w["nextUp"] or "Mission" in w["nextUp"],
            "khối việc tiếp theo chỉ sang Trung Tâm Nhiệm Vụ", w["nextUp"])

        steps_called = [c["step"] for c in w["calls"]]
        # ⚠️ THU TU DOI 03/08/2026: `life` len truoc `energy` (chu du an: *"su kien muc
        #    nuoc bien chen giua vo duyen roi"*). Danh sach nay PHAI khop `Missions.All`
        #    o backend va `STEP_IDS` o trang — check_pages.py [3c] so hai ben.
        chk(steps_called == ["scan", "timeline", "sun", "life",
                             "energy", "eco", "core"],
            "báo lên server ĐÚNG 7 bước, ĐÚNG thứ tự, KHÔNG trùng", str(steps_called))
        chk(all(c["mission"] == "earth" for c in w["calls"]),
            "mọi lời gọi đều mang mission='earth'")

        chk(shielded_live is True, "MÀNG KHÍ QUYỂN đã bọc Trái Đất",
            str(shielded_live))

        chk(len(errs) == 0, "0 lỗi console", "; ".join(errs[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[8c] Bản đồ PHỦ KÍN KHUNG ở mọi bước, mọi tỉ lệ màn")
        # ⚠️ MỤC NÀY SINH RA TỪ MỘT LỖI ĐÃ LÊN BẢN THẬT (02/08/2026, `docs/decisions/005`).
        #    Chủ dự án chơi thật rồi gửi ảnh chụp: bản đồ chỉ phủ tới x≈1243 trên khung
        #    ~1900px, bên phải ĐEN THUẦN, bảng vệ tinh trôi lơ lửng trong vùng đen.
        #    Nguyên nhân: `paint()` dịch `.e2-layer` theo `facing` tới ±50% bề rộng, mà
        #    lớp chỉ đủ phủ khung KHI phép dịch = 0 — không có chỗ nào kẹp lại.
        # ⚠️ 153 PHÉP KIỂM TRƯỚC ĐÓ KHÔNG CÓ PHÉP NÀO HỎI "bản đồ có phủ kín khung
        #    không". Đó chính là lý do lỗi sống được tới lúc có người chơi thật. Đây là
        #    phép kiểm bù vào đúng lỗ đó.
        # ⚠️ PHẢI LẤY HỢP CỦA MỌI `.e2-img`, không phải `querySelector` một cái. Bản đồ
        #    phẳng có BA bản lát theo kinh tuyến; đo một bản thì báo "vẫn hở 602px" trong
        #    khi hai bản sao đã lấp kín — probe của tôi đã báo hỏng oan đúng một lượt vì
        #    thế, và suýt kết luận là bản sửa không ăn.
        COVER = """
        () => {
          const v = document.querySelector('.e2-view').getBoundingClientRect();
          const rs = [...document.querySelectorAll('.e2-img')]
                       .filter(e => e.getClientRects().length)
                       .map(e => e.getBoundingClientRect());
          if (!rs.length) return null;
          const L = Math.min(...rs.map(r => r.left)),  R = Math.max(...rs.map(r => r.right));
          const T = Math.min(...rs.map(r => r.top)),   B = Math.max(...rs.map(r => r.bottom));
          return { n: rs.length,
                   gapL: Math.max(0, L - v.left), gapR: Math.max(0, v.right - R),
                   gapT: Math.max(0, T - v.top),  gapB: Math.max(0, v.bottom - B),
                   vw: v.width };
        }"""
        # (nhãn, lat, lon, dist) — lấy đúng cặp mà 7 bước THẬT dùng. FACE_OPEN = (30, 95).
        # Bước nào không khai lại lat/lon thì THỪA HƯỞNG, nên ghi đúng giá trị thừa hưởng.
        COVER_STEPS = [
            ("① scan",              30,  95, 2.6),
            ("② timeline",          30,  95, 3.4),
            ("③ sun",               30,  95, 5.2),   # lùi xa nhất -> ép sàn phóng
            # ⚠️ THU TU DOI 03/08/2026: `life` len truoc `energy`. Bon dong duoi day da
            #    tinh lai theo loi goi camera THAT (grep `panTo(`/`centerOn(` trong
            #    mission-earth.html): life `panTo({dist:3.1})` -> energy
            #    `centerOn({lat:20,lon:32,dist:4.4})` -> eco `panTo({dist:4.0})` -> core
            #    KHONG khai gi nen thua huong nguyen khung cua eco.
            ("④ life",              10,  20, 3.1),
            ("⑤ energy",            20,  32, 4.4),
            ("⑥ eco",               20,  32, 4.0),
            ("⑦ core (thừa hưởng)",  20,  32, 4.0),
            ("mép: lon 180",         0, 180, 4.4),   # kinh tuyến đổi dấu — chỗ dễ hở nhất
            ("mép: lon -95",         0, -95, 4.4),
        ]
        # Ba tỉ lệ màn KHÁC NHAU VỀ BẢN CHẤT, không phải ba cỡ na ná: rộng-mà-thấp
        # (khung của ảnh chủ dự án gửi) · siêu rộng · điện thoại dọc.
        for _vp in ({"width": 1900, "height": 985},
                    {"width": 2560, "height": 1080},
                    {"width": 390,  "height": 844}):
            ctx = br.new_context(viewport=_vp)
            page = ctx.new_page()
            stub(page)
            boot(page)
            _tag = f'{_vp["width"]}x{_vp["height"]}'
            for _nm, _la, _lo, _di in COVER_STEPS:
                page.evaluate(
                    "([la,lo,d]) => window.__mission.world.panTo("
                    "{lat:la, lon:lo, dist:d, ms:0})", [_la, _lo, _di])
                _c = page.evaluate(COVER)
                if _c is None:
                    chk(False, f"{_tag} {_nm}: có ảnh bề mặt để đo")
                    continue
                _worst = max(_c["gapL"], _c["gapR"], _c["gapT"], _c["gapB"])
                chk(_worst < 1.0, f"{_tag} {_nm}: bản đồ phủ kín khung",
                    f'hở L{_c["gapL"]:.0f} R{_c["gapR"]:.0f} '
                    f'T{_c["gapT"]:.0f} B{_c["gapB"]:.0f}px '
                    f'({_worst / _c["vw"] * 100:.1f}% bề rộng)')
            # Ba bản ảnh phải THẬT SỰ có mặt ở chế độ phẳng — nếu ai đó bỏ `.e2-wrap`
            # thì phép kiểm trên vẫn đỏ, nhưng nói rõ nguyên nhân thì đỡ phải đoán.
            _c = page.evaluate(COVER)
            chk(_c and _c["n"] == 3, f"{_tag}: đủ BA bản ảnh lát theo kinh tuyến",
                f'đếm được {_c["n"] if _c else 0}')
            ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[9] Tiếng Anh — chơi nhanh qua 7 bước")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        errs2 = []
        page = ctx.new_page()
        page.on("console", lambda m: errs2.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs2.append("pageerror: " + str(e)))
        stub(page, "en")
        boot(page)
        chk(page.evaluate("document.documentElement.lang") == "en", "thẻ html lang=en")
        obj_h = page.eval_on_selector("#obj-h", "e => e.textContent")
        chk(obj_h and not co_dau_viet(obj_h),
            "mục tiêu bước 1 bằng tiếng Anh", obj_h)

        def fast_play(pg):
            """Đi hết 7 bước bằng bề mặt điều khiển (không cần bấm đúng pixel).

            ⚠️ TỰ KHAI TRẠNG THÁI KHI KẸT (quy tắc 6 mục 6). Trước đây hàm này chỉ trả
            `bool`: một bước không qua được thì vòng lặp quay hết 320 lượt, mất ~20 phút,
            và tất cả những gì ta biết là "không chơi hết được 7 bước" — không biết bước
            nào, bảng nào đang mở, cờ `busy` có đang bật. Đã mất hai lượt chạy 20+ phút vì
            đúng lý do đó (một lần vì `fill()` đã bị bỏ, một lần vì `pick({type:'sun'})`).
            Nay: đếm số lượt KHÔNG tiến triển, thoát sớm và in ra đủ thứ cần biết.
            """
            _stall, _prev = 0, None
            for _ in range(320):
                sid = pg.evaluate("window.__mission.step")
                if pg.query_selector("#win.show"):
                    return True
                _key = (sid, pg.evaluate("window.__mission.done.length"))
                _stall = _stall + 1 if _key == _prev else 0
                _prev = _key
                # ⚠️ ĐÓNG THẺ TRƯỚC MỌI THỨ. Thẻ nội dung là một lớp phủ CHẶN HẾT: còn
                #    mở là `showCard` chưa resolve, `busy` còn bật, và mọi nhánh bên dưới
                #    đều không làm gì được. Trước đây `close_card` chỉ nằm TRONG vòng chạm
                #    marker, nên thẻ hé lộ 71% (mở SAU khi marker đã bị xoá) không ai đóng.
                close_card(pg)
                if _stall >= 25:
                    print("    ⛔ KET o buoc `%s` sau %d luot khong tien trien. Trang thai:"
                          % (sid, _stall))
                    print("       " + str(pg.evaluate("""() => ({
                      done: window.__mission.done, busy: window.__mission.busy,
                      bangDangMo: ['ask','time','energy','xsec','eco','core']
                        .filter(id => document.getElementById(id)
                          && document.getElementById(id).classList.contains('show')),
                      theDangMo: document.getElementById('card').classList.contains('show'),
                      boxThoai: document.querySelector('.me-say.show') ? 'co' : 'khong',
                      rungWanted: window.__mission.rungWanted,
                      soMarker: window.__mission.world.markers.length
                    })""")))
                    return False
                say_through(pg, 3)
                if sid == "life":
                    # ⚠️ BƯỚC ④ KHÔNG CÒN LÁI ĐƯỢC BẰNG `pick()` (02/08/2026) — nó không
                    #    nhận cú chạm marker nào nữa, trẻ chọn NẤC trên lát cắt. Để nó
                    #    lẫn trong nhánh marker bên dưới thì vòng lặp quay 320 lượt rồi
                    #    hết hạn, và triệu chứng đọc ra y như "sản phẩm treo".
                    try:
                        pg.wait_for_function("() => !window.__mission.busy", timeout=30000)
                        pg.wait_for_function("() => window.__mission.rungWanted !== null",
                                             timeout=15000)
                        pg.evaluate("() => window.__mission.rung(window.__mission.rungWanted)")
                        read_card(pg, timeout=15000)
                    except Exception:
                        pass
                elif sid in ("scan", "sun"):
                    # Bước `sun` cũng đi qua đây: sau khi ngôi sao cháy, nó đặt 3 marker
                    # vùng khí hậu — cùng một cách chơi với `scan`.
                    for mid in pg.evaluate("window.__mission.world.markers.map(m=>m.id)"):
                        try:
                            pg.wait_for_function("() => !window.__mission.busy",
                                                 timeout=30000)
                        except Exception:
                            pass
                        pg.evaluate("id => window.__mission.pick({type:'marker', id})", mid)
                        pg.wait_for_timeout(250)
                        close_card(pg)
                    # ⚠️ TRẢ LỜI BẤT KỲ BẢNG ĐOÁN NÀO ĐANG MỞ, đọc lựa chọn từ DOM.
                    #    Cả bước ① (nước/đất) và bước ③ (nếu Mặt Trời tắt) đều dùng bảng
                    #    này, và ở CẢ HAI thì **mọi lựa chọn đều đi tiếp** — bước ① không
                    #    phạt đoán sai, bước ③ thì cả ba đáp án đều đúng. Nên lấy lựa chọn
                    #    đầu tiên là đủ, và không phải gán cứng tên đáp án theo từng bước.
                    #    ⛔ ĐỪNG gọi `pick({type:'sun'})`: việc đi tìm & chạm Mặt Trời đã
                    #       bị bỏ (trẻ không tìm được — nút lẫn vào chính ảnh Trái Đất).
                    if pg.query_selector("#ask.show"):
                        _p = pg.eval_on_selector_all(
                            "#ask-opts .me-ask-opt", "es => es.map(e => e.dataset.pick)")
                        if _p:
                            pg.evaluate("p => window.__mission.answer(p)", _p[0])
                            pg.wait_for_timeout(400)
                elif sid == "timeline":
                    for i in range(pg.evaluate("window.__mission.eraTotal")):
                        try:
                            pg.wait_for_function("() => !window.__mission.busy", timeout=30000)
                        except Exception:
                            pass
                        pg.evaluate("i => window.__mission.era(i)", i)
                        pg.wait_for_timeout(200)
                        close_card(pg)
                    # Mốc cuối chỉ HIỆN NÚT; `onDone()` mới chốt bước — xem `play_timeline`.
                    pg.evaluate("window.__mission.eraDone()")
                    pg.wait_for_timeout(250)
                elif sid == "energy":
                    if pg.query_selector("#energy.show"):
                        for want in pg.eval_on_selector_all(
                                "#energy-tray .me-gem", "es => es.map(e => e.dataset.want)"):
                            pg.evaluate("w => window.__mission.place(w)", want)
                            pg.wait_for_timeout(120)
                elif sid == "eco":
                    if pg.query_selector("#eco.show"):
                        n = pg.eval_on_selector_all("#eco-deck .me-gem", "es => es.length")
                        for _i in range(n):
                            pg.evaluate("window.__mission.sort()")
                            pg.wait_for_timeout(100)
                elif sid == "core":
                    # ⚠️ `__mission.fill(slot)` VÀ `#core-tray .me-gem` ĐỀU KHÔNG CÒN
                    #    (02/08/2026): bước cuối bỏ 3 viên ngọc, nay là MỘT cú đóng dấu.
                    #    Nhánh cũ vì thế lặp 0 lần rồi vòng ngoài quay tiếp mãi → cả bộ
                    #    smoke chạy tới hết hạn 1500s và bị `timeout` giết, để lại một
                    #    `TargetClosedError` đọc ra như lỗi trình duyệt. Đây là loại lỗi
                    #    quy tắc 6 mục 6 nói tới: phép chờ thất bại phải TỰ KHAI trạng thái.
                    if pg.query_selector("#core.show"):
                        pg.evaluate("window.__mission.stamp()")
                        pg.wait_for_timeout(200)
                pg.wait_for_timeout(320)
            return bool(pg.query_selector("#win.show"))

        chk(fast_play(page), "EN: chơi được hết 7 bước tới màn tổng kết")
        we = page.evaluate("""() => ({
          h: document.getElementById('win-h').textContent,
          badge: document.getElementById('win-badge').textContent,
          nextUp: document.getElementById('win-next').textContent
        })""")
        chk(we["h"] and not co_dau_viet(we["h"]),
            "EN: tiêu đề tổng kết dịch", we["h"])
        chk("Mission Control" in we["nextUp"], "EN: khối việc tiếp theo dịch", we["nextUp"])
        chk(len(errs2) == 0, "EN: 0 lỗi console", "; ".join(errs2[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[10] Điện thoại 390×844")
        ctx = br.new_context(viewport={"width": 390, "height": 844},
                             is_mobile=True, has_touch=True)
        errs3 = []
        page = ctx.new_page()
        page.on("console", lambda m: errs3.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs3.append("pageerror: " + str(e)))
        stub(page)
        boot(page)
        chk(page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"),
            "không tràn ngang",
            str(page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")))
        for sel in ["#obj", ".me-top"]:
            b = page.eval_on_selector(sel, "e => { const r = e.getBoundingClientRect();"
                                             " return [r.left, r.right, r.bottom]; }")
            chk(b[0] >= -1 and b[1] <= 391, f"{sel} nằm trong màn hình", str([round(x) for x in b]))
        # Bảng mục tiêu không được che hết hành tinh
        oh = page.eval_on_selector("#obj", "e => e.getBoundingClientRect().height")
        chk(oh < 844 * 0.45, "bảng mục tiêu không chiếm quá 45% chiều cao", f"{oh:.0f}px")

        # ══ PHÉP KIỂM QUAN TRỌNG NHẤT CỦA MỤC NÀY (thêm 02/08/2026, `005`) ══════════
        # ⚠️ TRÊN MÀN DỌC KHÔNG THỂ NHÌN HẾT 7 CHÂU LỤC CÙNG LÚC — đo được ở sàn phóng
        #    zoom 1: bề ngang nhìn thấy = 360° × 390 / max(390, 2×844) = **83°**, trong
        #    khi 7 châu lục trải ~234°. Mà `004` đã bỏ hết cú kéo, nên nếu châu lục kế
        #    tiếp nằm ngoài khung và không có gì đưa nó vào thì trẻ **kẹt cứng vĩnh
        #    viễn** — đúng loại lỗi đã làm bước `rotation` bản 3D không hoàn thành được.
        #    `focusMarker()` là thứ chặn chuyện đó; đây là chỗ duy nhất chứng minh nó chạy.
        # ⚠️ ĐO BẰNG CHÍNH `screenOf().visible` (có tính cả việc bị mép khung cắt), và
        #    đo SAU khi thẻ nội dung đã đóng — đo lúc thẻ còn mở là đo giữa lúc bản đồ
        #    còn đang lướt.
        # ⚠️⚠️ PHÉP KIỂM NÀY ĐÃ ĐỔI CÁCH ĐO 03/08/2026 (`docs/decisions/007`) — VÀ NÓ
        #    MẠNH LÊN NHỜ THẾ. Bản cũ lấy `_left[0]`, tức châu lục chưa chạm đầu tiên
        #    **theo thứ tự khai báo**, rồi đòi nó luôn trong khung. Điều đó chỉ đúng khi
        #    cú lướt bản đồ cũng đi theo thứ tự khai báo — mà từ 03/08/2026 `nextLeft()`
        #    đi theo đốm GẦN NHẤT với đốm vừa chạm (sửa lỗi "bàn tay vẫn ở chỗ cũ"), nên
        #    `_left[0]` và đích thật của cú lướt không còn là một. Bản cũ vì thế báo hỏng
        #    ĐÚNG LÚC sản phẩm làm đúng.
        # ⚠️ Điều PHẢI bảo vệ vẫn nguyên: **trẻ không bao giờ kẹt**. Nhưng phát biểu đúng
        #    của nó là *"đốm mà BÀN TAY đang chỉ vào luôn bấm được"*, không phải *"đốm thứ
        #    n trong mảng luôn trong khung"*: trên màn dọc trẻ **chỉ bấm được thứ nó nhìn
        #    thấy**, và bàn tay chính là thứ nói cho nó bấm vào đâu. Nên nay lái vòng lặp
        #    bằng `handTarget` và đo `markerHittable`-tương-đương (`screenOf().visible`).
        #    Chặt hơn bản cũ: nó kiểm CẢ bàn tay, thứ bản cũ không hỏi tới.
        say_through(page)
        page.wait_for_function("() => window.__mission.world.markers.length === 7", timeout=20000)
        _stuck, _nohand = [], []
        for _i in range(7):
            page.wait_for_function("() => !window.__mission.busy", timeout=20000)
            _st = page.evaluate("""() => {
              const left = window.__mission.world.markers.filter(m => !m.done).map(m => m.id);
              const t = window.__mission.handTarget;
              const p = t ? window.__mission.world.screenOf('marker', t) : null;
              return {left, tgt: t, vis: !!(p && p.visible),
                      shown: document.getElementById('hand').classList.contains('show')};
            }""")
            if not _st["left"]:
                break
            if not (_st["shown"] and _st["tgt"]):
                _nohand.append(_st["left"])
                _nx = _st["left"][0]              # vẫn đi tiếp để còn đo được các lượt sau
            else:
                _nx = _st["tgt"]
                if not _st["vis"]:
                    _stuck.append(_nx)
            page.evaluate("id => window.__mission.pick({type:'marker', id})", _nx)
            page.wait_for_timeout(260)
            read_card(page, timeout=9000)
        chk(not _stuck,
            "điện thoại: đốm BÀN TAY đang chỉ vào LUÔN bấm được (không thể kẹt)",
            f"ngoài khung: {_stuck}")
        chk(not _nohand,
            "điện thoại: luôn CÓ bàn tay chỉ đường khi còn đốm chưa chạm",
            f"khong co tay trong khi con: {_nohand}")
        chk(page.evaluate("window.__mission.scanned") == 7,
            "điện thoại: chạm đủ 7 châu lục chỉ bằng cách bấm vào chỗ nhìn thấy")

        chk(fast_play(page), "điện thoại: chơi được hết 7 bước")
        ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[10b] Điện thoại — bước ④ `life`: 4 mẫu vật cũng phải với tới được")
        # ⚠️ PHÉP KIỂM NÀY SINH RA TỪ MỘT LỖI CÓ SẴN, không phải từ bước ① mới.
        #    4 vùng sinh học nằm ở lon −62 · −42 · 20 · 87 (trải 149°), mà màn dọc
        #    390×844 ở `dist:3,1` chỉ thấy ~59° kinh độ. Trước 02/08/2026 lớp bản đồ
        #    còn bị NEO MÉP TRÁI nên **dãy Himalaya (lon 87) không tài nào đưa vào
        #    khung** — tức bước ④ không chơi được trên máy tính bảng dọc, và 153 phép
        #    kiểm cũ không có phép nào hỏi câu đó (y hệt chuyện chúng không hỏi "bản
        #    đồ có phủ kín khung không").
        #    Cùng một họ với mục [10]: điều phải bảo vệ là **trẻ không bao giờ kẹt**.
        ctx = br.new_context(viewport={"width": 390, "height": 844},
                             is_mobile=True, has_touch=True)
        page = ctx.new_page()
        errs3b = []
        page.on("console", lambda m: errs3b.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs3b.append("pageerror: " + str(e)))
        stub(page)
        boot(page)
        for _ in range(400):
            if page.evaluate("window.__mission.step") == "life":
                break
            sid = page.evaluate("window.__mission.step")
            say_through(page, 3)
            close_card(page)          # cùng lý do như `fast_play` — thẻ chặn hết
            if sid in ("scan", "sun"):
                for mid in page.evaluate("window.__mission.world.markers.map(m=>m.id)"):
                    try:
                        page.wait_for_function("() => !window.__mission.busy", timeout=30000)
                    except Exception:
                        pass
                    page.evaluate("id => window.__mission.pick({type:'marker', id})", mid)
                    page.wait_for_timeout(200)
                    close_card(page)
                # ⚠️ Cùng lý do như vòng lái nhanh ở mục [9]: bảng đoán của bước ③ phải
                #    được trả lời, và việc chạm Mặt Trời đã bị bỏ.
                if page.query_selector("#ask.show"):
                    _p = page.eval_on_selector_all(
                        "#ask-opts .me-ask-opt", "es => es.map(e => e.dataset.pick)")
                    if _p:
                        page.evaluate("p => window.__mission.answer(p)", _p[0])
                        page.wait_for_timeout(400)
            elif sid == "timeline":
                for i in range(page.evaluate("window.__mission.eraTotal")):
                    try:
                        page.wait_for_function("() => !window.__mission.busy", timeout=30000)
                    except Exception:
                        pass
                    page.evaluate("i => window.__mission.era(i)", i)
                    page.wait_for_timeout(200)
                    close_card(page)
                # Mốc cuối chỉ HIỆN NÚT; `onDone()` mới chốt bước.
                page.evaluate("window.__mission.eraDone()")
                page.wait_for_timeout(250)
            elif sid == "energy" and page.query_selector("#energy.show"):
                for want in page.eval_on_selector_all(
                        "#energy-tray .me-gem", "es => es.map(e => e.dataset.want)"):
                    page.evaluate("w => window.__mission.place(w)", want)
                    page.wait_for_timeout(120)
            page.wait_for_timeout(300)
        chk(page.evaluate("window.__mission.step") == "life",
            "điện thoại: tới được bước ④ `life`")
        say_through(page)
        page.wait_for_function("() => window.__mission.world.markers.length === 4", timeout=20000)
        _stuck2 = []
        for _i in range(4):
            page.wait_for_function("() => !window.__mission.busy", timeout=30000)
            _left = page.evaluate(
                "() => window.__mission.world.markers.filter(m => !m.done).map(m => m.id)")
            if not _left:
                break
            _nx = _left[0]
            _sp = page.evaluate("id => window.__mission.world.screenOf('marker', id)", _nx)
            if not (_sp and _sp["visible"]):
                _stuck2.append(_nx)
            # ⚠️ MARKER KHÔNG CÒN BẤM ĐƯỢC, NHƯNG PHÉP KIỂM NÀY VẪN ĐÚNG VIỆC — thậm chí
            #    còn CẦN hơn trước. Trẻ phải NHÌN THẤY nơi đó trên ảnh vệ tinh thì mới có
            #    căn cứ đoán độ cao; marker ngoài khung nghĩa là đang hỏi về một nơi trẻ
            #    không nhìn thấy. Chỉ đổi cách LÁI (chọn nấc), giữ nguyên thứ ĐO.
            page.wait_for_function("() => window.__mission.rungWanted !== null", timeout=20000)
            page.evaluate("() => window.__mission.rung(window.__mission.rungWanted)")
            page.wait_for_timeout(300)
            read_card(page, timeout=15000)
        chk(not _stuck2,
            "điện thoại: nơi đang HỎI luôn nằm trong khung (kể cả Himalaya lon 87)",
            f"ngoài khung: {_stuck2}")
        # ⚠️ CHIỀU CAO BẢNG LÀ RÀNG BUỘC THẬT, ĐÃ ĐO ĐƯỢC MỘT LẦN HÔM NAY: ở bước ② ảnh
        #    tràn bảng làm 1366×768 chỉ còn 30px bản đồ. Bước ⑤ còn nặng hơn — trẻ PHẢI
        #    nhìn được nơi đó trên ảnh vệ tinh mới đoán được độ cao, nên bảng nuốt hết
        #    bản đồ là bước mất căn cứ chứ không chỉ xấu.
        _bx = page.evaluate("""() => {
          const b = document.getElementById('xsec').getBoundingClientRect();
          const t = document.querySelector('.me-top').getBoundingClientRect();
          return { h: Math.round(b.height), map: Math.round(b.top - t.bottom),
                   vh: innerHeight };
        }""")
        chk(_bx["map"] >= 150,
            "điện thoại: lát cắt chừa lại ≥150px bản đồ để trẻ còn thấy nơi đang hỏi",
            f"bảng {_bx['h']}px / còn {_bx['map']}px trên khung {_bx['vh']}px")
        chk(len(errs3b) == 0, "điện thoại [10b]: 0 lỗi console", "; ".join(errs3b[:3]))
        wm = page.eval_on_selector("#win .me-win-card",
                                   "e => { const r = e.getBoundingClientRect();"
                                   " return [r.left, r.right, r.top, r.bottom, r.height]; }")
        chk(wm[0] >= -1 and wm[1] <= 391, "màn tổng kết không tràn ngang",
            str([round(x) for x in wm]))
        chk(page.evaluate("() => { const c = document.querySelector('#win .me-win-card');"
                          " return c.scrollHeight <= c.clientHeight + 2 ||"
                          " getComputedStyle(c).overflowY !== 'visible'; }"),
            "màn tổng kết cuộn được nếu cao hơn màn hình")
        # Tiêu đề không được để ☄️/🚀 rơi xuống một dòng riêng
        lines = page.evaluate("""() => {
          const h = document.querySelector('#win h2');
          const rects = [];
          h.childNodes.forEach(n => {
            const rg = document.createRange(); rg.selectNodeContents(n);
            for (const r of rg.getClientRects()) rects.push([Math.round(r.top), (n.textContent||'').trim()]);
          });
          const by = {};
          rects.forEach(([t, s]) => { by[t] = (by[t] || '') + s; });
          return Object.values(by);
        }""")
        orphan = [l for l in lines if l and len(l.strip()) <= 2 and not l.strip().isalnum()]
        chk(len(orphan) == 0, "tiêu đề: không có dòng chỉ chứa emoji", str(lines))
        chk(len(errs3) == 0, "điện thoại: 0 lỗi console", "; ".join(errs3[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[11] prefers-reduced-motion")
        ctx = br.new_context(viewport={"width": 1440, "height": 900},
                             reduced_motion="reduce")
        errs4 = []
        page = ctx.new_page()
        page.on("console", lambda m: errs4.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs4.append("pageerror: " + str(e)))
        stub(page)
        t0 = time.time()
        boot(page)
        chk(fast_play(page), "reduced-motion: chơi được hết 7 bước")
        # ⚠️ TRƯỚC 02/08/2026 phép kiểm này canh một chuyện cụ thể: bước `rotation` ở
        #    reduced-motion từng TREO VĨNH VIỄN vì hành tinh không tự quay, nên trẻ
        #    không có cách nào hoàn thành. Bước đó đã bỏ (`docs/decisions/005`), nhưng
        #    ĐIỀU CẦN CANH KHÔNG ĐỔI: không bước nào được phụ thuộc vào một hoạt cảnh
        #    mới giải được. Nên giữ phép kiểm, chỉ đổi con số và ghi lại lý do.
        chk(page.evaluate("() => window.__mission.done.length === 7"),
            "reduced-motion: xong ĐỦ 7 bước (không bước nào cần hoạt cảnh mới giải được)",
            str(page.evaluate("window.__mission.done")))
        chk(page.evaluate("() => window.__mission.world.sunOn") is True,
            "reduced-motion: Mặt Trời vẫn cháy (chỉ bỏ hoạt cảnh, không bỏ nội dung)")
        # Không được còn hoạt cảnh vô hạn nào chạy
        inf = page.evaluate("""() => {
          let n = 0;
          document.querySelectorAll('*').forEach(e => {
            const s = getComputedStyle(e);
            if (s.animationName !== 'none' && s.animationIterationCount === 'infinite'
                && s.animationPlayState === 'running') n++;
          });
          return n;
        }""")
        chk(inf == 0, "reduced-motion: 0 hoạt cảnh lặp vô hạn", f"{inf} phần tử")
        chk(len(errs4) == 0, "reduced-motion: 0 lỗi console", "; ".join(errs4[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[12] Không có server: KHÔNG bịa phần thưởng")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errs5 = []
        page.on("console", lambda m: errs5.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs5.append("pageerror: " + str(e)))
        # Bản giả trả về LỖI, y như lúc chưa đăng nhập / mất mạng
        page.add_init_script("localStorage.setItem('astroq-lang','vi');")
        page.add_init_script("""
          var __off = {
            missionStep: async () => ({ ok: false, queued: true }),
            quiz(){}, game(){}, lesson(){}, planet(){}, spend(){}, flush(){}
          };
          Object.defineProperty(window, 'AstroQProgress', {
            configurable: true, get: function () { return __off; }, set: function () {}
          });
        """)
        boot(page)
        chk(fast_play(page), "mất mạng: vẫn chơi được hết 7 bước (không chặn giao diện)")
        r = page.evaluate("window.__mission.reward")
        wtt = page.eval_on_selector("#win-rw-tt", "e => e.textContent")
        chk(r["meteors"] == 0 and r["xp"] == 0,
            "mất mạng: KHÔNG tự cộng thưởng ở client", json.dumps(r))
        chk("0" in wtt, "mất mạng: màn tổng kết hiện 0 chứ không bịa số", wtt)
        chk(len(errs5) == 0, "mất mạng: 0 lỗi console", "; ".join(errs5[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[13] Am thanh — nut tat tieng dung chung khoa astroq-sfx")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errs6 = []
        page.on("console", lambda m: errs6.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs6.append("pageerror: " + str(e)))
        stub(page)
        boot(page)
        chk(page.evaluate("() => !!window.AstroQSfx"), "js/sfx.js da nap")
        chk(page.evaluate("() => AstroQSfx.on()") is True,
            "mac dinh BAT tieng (chua ai tat)")
        chk(page.eval_on_selector("#mute", "e => e.textContent.trim()") == "\U0001f50a",
            "nut hien bieu tuong loa khi dang bat")
        page.click("#mute")
        page.wait_for_timeout(200)
        chk(page.evaluate("() => localStorage.getItem('astroq-sfx')") == "off",
            "bam nut -> ghi DUNG khoa dung chung voi 3 mini-game")
        chk(page.evaluate("() => AstroQSfx.on()") is False,
            "tat roi thi AstroQSfx.on() = false")
        chk(page.eval_on_selector("#mute", "e => e.textContent.trim()") == "\U0001f507",
            "nut doi sang loa gach cheo")
        # Da tat tieng thi KHONG duoc dung node am thanh nao
        made = page.evaluate(
            SFX_COUNT_JS % "AstroQSfx.fanfare(); AstroQSfx.beep(); AstroQSfx.pickup();")
        chk(made == 0 or made == "no-ctx",
            "da tat tieng thi KHONG dung dao dong nao", str(made))
        page.click("#mute")
        page.wait_for_timeout(200)
        chk(page.evaluate("() => localStorage.getItem('astroq-sfx')") == "on",
            "bam lai -> bat tieng tro lai")
        made2 = page.evaluate(SFX_COUNT_JS % "AstroQSfx.fanfare();")
        chk(made2 == "no-ctx" or made2 >= 4,
            "bat tieng thi nhac khai hoan dung du hop am", str(made2))
        chk(len(errs6) == 0, "am thanh: 0 loi console", "; ".join(errs6[:3]))
        ctx.close()

        br.close()

    print("\n" + "=" * 60)
    print(f"KẾT QUẢ: {ok} đạt / {fail} hỏng")
    if FAILS:
        print("Hỏng:")
        for f in FAILS:
            print("  -", f)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
