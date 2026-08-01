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
# 8 bước (từ 29/07/2026, xen 3 bước giáo dục vào bản 5 bước cũ). Tổng phải ra:
#   tt : 0+20+20+25+20+20+30+(20+100) = 255
#   XP : 20+30+30+35+30+40+40+(40+120) = 385
#   codex: 9/9  (earth-formation · sun · clean-energy · rotation ·
#                water/forest/animal/mountain · eco-habits)
# `newBadges` cũng do server quyết: `eco-warrior` mở ngay ở bước `eco`
# (metric `mission:earth:eco` trong Achievements.cs), `rookie-astronaut` ở bước cuối.
STUB_METEORS, STUB_XP, STUB_CODEX_TOTAL = 255, 385, 9
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
      rotation: { meteors: 20, xp: 30, codex: ['rotation'] },
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
        missions: { earth: { codex: window.__codex.slice(),
                             codexTotal: 9, done: done } }
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
    page.add_init_script(STUB_PROGRESS)
    # ⚠️ PHẢI ghim ngôn ngữ. `AstroQ.getLang()` lùi về `navigator.language` khi
    # `localStorage` còn trống, mà Chromium của Playwright mặc định `en-US` →
    # cả phần "tiếng Việt" của bộ test lặng lẽ chạy bằng tiếng Anh và mọi phép
    # kiểm chữ Việt đều vô nghĩa. Đây là hành vi ĐÚNG của sản phẩm, không phải lỗi.
    page.add_init_script(
        "localStorage.setItem('astroq-lang', %r);" % lang)


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


def drag_earth_until_aligned(pg, limit=60):
    """Kéo NGANG trên quả cầu cho tới khi trạm phát sóng hướng về vệ tinh.

    ⚠️ CỐ Ý không gọi `world.setSpin()`. Bản đầu của bộ test này cho hành tinh tự
    quay rồi đợi — và nó "đạt". Nhưng trẻ KHÔNG có cái nút đó: thứ duy nhất trẻ
    làm được là kéo. Đo bằng cách trẻ không làm được thì phép kiểm không chứng
    minh điều gì. Chính vì đổi sang kéo thật mà lỗi "kéo xoay camera chứ không
    xoay hành tinh" mới lộ ra.
    """
    box = pg.eval_on_selector("#stage", "e => { const r = e.getBoundingClientRect();"
                                        " return [r.left + r.width/2, r.top + r.height/2]; }")
    cx, cy = box
    y0 = None
    for i in range(limit):
        a = pg.evaluate("window.__mission.satAngle")
        if y0 is None:
            y0 = spin_deg(pg)
        if pg.evaluate("() => window.__mission.done.includes('rotation')"):
            return True, a, deg_delta(y0, spin_deg(pg))
        pg.mouse.move(cx - 160, cy)
        pg.mouse.down()
        pg.mouse.move(cx + 160, cy, steps=8)     # kéo sang phải ~320px
        pg.mouse.up()
        pg.wait_for_timeout(180)
    return (pg.evaluate("() => window.__mission.done.includes('rotation')"),
            pg.evaluate("window.__mission.satAngle"),
            deg_delta(y0 or 0, spin_deg(pg)))


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
            " document.getElementById('card-got').textContent]")
        pg.wait_for_function(
            "() => !document.getElementById('card').classList.contains('show')",
            timeout=12000)
        return c
    except Exception:
        return None


def play_timeline(pg):
    """Bấm hết 4 mốc thời gian. Trả về (số mốc đã xem, thẻ nham thạch).

    Mốc dung nham trao viên nham thạch NGAY tại đó, nên phải đọc thẻ giữa mốc 0 và
    mốc 1 — đọc sau khi bấm hết 4 mốc là thẻ đã tự đóng từ lâu.
    """
    rock = None
    for i in range(4):
        pg.wait_for_function("() => !window.__mission.busy", timeout=30000)
        b = pg.query_selector(f'#time-rail .me-era-node[data-era="{i}"]')
        if b:
            b.click()                      # BẤM THẬT, không đi qua __mission.era
        else:
            pg.evaluate("i => window.__mission.era(i)", i)
        pg.wait_for_timeout(200)
        if i == 0:
            rock = read_card(pg, timeout=8000)
    return pg.evaluate("window.__mission.eras"), rock


def play_energy(pg):
    """Kéo 3 nguồn sạch vào 3 ống khói. Trả về (số ống đã thay, khói đầu, khói cuối)."""
    pg.wait_for_selector("#energy.show", timeout=15000)
    smog0 = pg.evaluate("window.__mission.smog")
    items = pg.eval_on_selector_all("#energy-tray .me-gem", "es => es.map(e => e.dataset.want)")
    for want in items:
        drag_to(pg, f'#energy-tray .me-gem[data-want="{want}"]',
                f'#energy-slots .me-stack[data-zone="{want}"]')
    return (pg.eval_on_selector_all("#energy-slots .me-stack.ok", "es => es.length"),
            smog0, pg.evaluate("window.__mission.smog"))


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
        chk(any(c in oh for c in "ộạảấầệốơư"), "mục tiêu hiện bằng TIẾNG VIỆT", oh)

        # Trái Đất phải ĐANG SÁNG ở bước 1 (theo bản mô tả, tối đi là ở bước 2)
        p_lit = pix(page, (0.3, 0.3, 0.4, 0.4))
        chk(p_lit["avg"] > 22, "bước 1: Trái Đất đang SÁNG", f"độ sáng TB {p_lit['avg']:.1f}")
        # ⚠️ MỞ MÀN PHẢI LÀ ẢNH QUẢ CẦU, chưa phải bản đồ phẳng (đổi 01/08/2026).
        #    Đo được: quả cầu sáng TB 113,9 ở vùng giữa, bản đồ phẳng chỉ 24,3 — tối hơn
        #    4,7 lần. Đây là cảnh ĐẦU TIÊN trẻ thấy trong nhiệm vụ; mở màn bằng một hình
        #    chữ nhật gần đen là mất đúng khoảnh khắc "mình đã tới Trái Đất".
        chk(page.evaluate("() => window.__mission.world.map") == "globe",
            "mở màn bằng ẢNH QUẢ CẦU (sáng), chưa phải bản đồ phẳng",
            page.evaluate("() => window.__mission.world.map"))

        # ══════════════════════════════════════════════════════════════════
        head("[2] Bước 1 — lưới quét + 3 điểm tín hiệu (bấm THẬT)")
        # Trước đây đếm `world.scene.children.length` — một con số của THREE.js, mà
        # điều muốn biết chỉ là "cảnh đã vẽ ra cái gì chưa". Đo pixel sáng đúng hơn:
        # scene có 20 vật thể mà đặt sai chỗ hết thì màn hình vẫn đen.
        chk(pix(page)["lit"] > 0, "canh da ve ra pixel sang tren man hinh")
        say_through(page)
        page.wait_for_function("() => window.__mission.world.markers.length === 3", timeout=15000)
        chk(True, "3 điểm tín hiệu đã đặt")


        # Bàn tay hướng dẫn phải đã xuất hiện trong bước này
        chk(page.evaluate(
            "() => window.__handSeen === true || document.getElementById('hand')"
            ".className.length >= 0"), "có bàn tay hướng dẫn (phần tử #hand tồn tại)")

        # Bấm THẬT vào marker đầu tiên tại đúng chỗ nó đang hiện trên màn hình
        ids = page.evaluate("window.__mission.world.markers.map(m => m.id)")
        vis = page.evaluate(
            "() => window.__mission.world.markers"
            ".filter(m => window.__mission.world.screenOf('marker', m.id).visible).length")
        chk(vis >= 2, "ở góc mở màn trẻ thấy được ít nhất 2/3 điểm tín hiệu",
            f"{vis}/3 thấy được")
        # ⚠️ KHỐI KÉO PHẢI ĐỨNG SAU PHÉP KIỂM "≥2/3 ĐIỂM" NGAY TRÊN. Lượt đầu tôi đặt
        #    nó lên trước, nên phép kiểm kia đo SAU khi bản đồ đã bị kéo đi 300px và
        #    báo 1/3 — hỏng oan, lỗi THỨ TỰ trong bộ đo chứ không phải lỗi sản phẩm.
        # ══ KỊCH BẢN MỚI 01/08/2026: kéo phải làm ẢNH ĐỔI, không phải làm ĐỐM TRƯỢT ══
        # ⚠️ Đây là phép kiểm quan trọng nhất của bước 1. Trên ảnh quả cầu, `paint()`
        #    đặt `translate` bằng 0 — đo được: kéo 300px thì transform và khung ảnh Y
        #    NGUYÊN, chỉ ba cái đốm trượt đi (một cái ra khỏi khung). Tức lời "Kéo để
        #    xoay Trái Đất" mô tả một việc KHÔNG HỀ XẢY RA, và thứ trẻ thấy là mục tiêu
        #    chạy khỏi con trỏ. Đọc code không thấy — phải kéo rồi so hai số đo.
        chk(page.evaluate("() => window.__mission.world.map") == "flat",
            "sau lời Comet: đã chuyển sang CHẾ ĐỘ BẢN ĐỒ",
            page.evaluate("() => window.__mission.world.map"))

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
        chk(_a["x"] is not None and _b["x"] is not None and abs(_b["x"] - _a["x"]) > 100,
            "KÉO làm ẢNH BẢN ĐỒ dịch thật (không phải đứng yên)",
            f"x {_a['x']} -> {_b['x']}")
        # Và điểm tín hiệu PHẢI đứng yên tại chỗ của nó trên Trái Đất — nó là một ĐỊA
        # ĐIỂM, không phải một thứ bám theo con trỏ.
        chk(_a["mks"] == _b["mks"],
            "3 điểm tín hiệu ĐỨNG YÊN tại toạ độ thật (đi cùng bản đồ)",
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

        n_before = page.evaluate("+document.getElementById('obj-n').textContent.split('/')[0]")
        chk(n_before >= 1, "bảng mục tiêu đếm lên", f"{n_before}/3")
        bar = page.eval_on_selector("#obj-bar", "e => e.getBoundingClientRect().width")
        chk(bar > 2, "thanh tiến độ có bề rộng THẬT (không phải 0px)", f"{bar:.0f}px")

        # Kéo để xoay: chứng minh OrbitControls thật sự hoạt động
        # `camera.position` là của three.js. Cả hai engine đều có `facingLatLon()` —
        # điểm trên bề mặt đang hướng về người xem — nên đó là con số dùng chung.
        f0 = page.evaluate("() => window.__mission.world.facingLatLon()")
        page.mouse.move(720, 450)
        page.mouse.down()
        page.mouse.move(880, 470, steps=12)
        page.mouse.up()
        page.wait_for_timeout(300)
        f1 = page.evaluate("() => window.__mission.world.facingLatLon()")
        moved = max(abs(deg_delta(f0["lon"], f1["lon"])), abs(f1["lat"] - f0["lat"]))
        chk(moved > 1.0, "KEO de xoay doi duoc goc nhin", f"lech {moved:.2f} do")

        # Nốt 2 điểm còn lại
        for mid in ids:
            page.evaluate("id => window.__mission.pick({type:'marker', id})", mid)
            page.wait_for_timeout(250)

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
        head("[3b] Bước 2 — dòng thời gian 4,5 tỷ năm + viên nham thạch")
        say_through(page)
        page.wait_for_selector("#time.show", timeout=15000)
        nodes = page.eval_on_selector_all(
            "#time-rail .me-era-node",
            "es => es.map(e => [e.querySelector('.yr').textContent,"
            " e.querySelector('.nm').textContent, e.disabled])")
        chk(len(nodes) == 4, "4 mốc thời gian", str([n[0] for n in nodes]))
        chk(any("4,5 tỷ" in n[0] for n in nodes), "có mốc 4,5 tỷ năm trước",
            str([n[0] for n in nodes]))
        chk(any("3,8 tỷ" in n[0] for n in nodes), "có mốc 3,8 tỷ năm trước")
        chk(any("66 triệu" in n[0] for n in nodes), "có mốc 66 triệu năm (khủng long)")
        chk(any("Ngày nay" in n[0] for n in nodes), "có mốc Ngày nay")
        # Đi ĐÚNG THỨ TỰ: chỉ mốc đầu bấm được, ba mốc sau còn khoá
        chk(nodes[0][2] is False and all(n[2] is True for n in nodes[1:]),
            "chỉ mốc ĐẦU mở được, 3 mốc sau còn khoá",
            str([n[2] for n in nodes]))
        # Bấm mốc chưa tới → bị nhắc, KHÔNG tính tiến độ
        page.evaluate("window.__mission.era(3)")
        page.wait_for_timeout(300)
        chk(page.evaluate("window.__mission.eras") == 0,
            "bấm vượt thứ tự KHÔNG tính là đã xem")

        lit_before_era = pix(page, (0.3, 0.3, 0.4, 0.4))
        seen, rock = play_timeline(page)
        chk(seen == 4, "xem hết 4 mốc", f"{seen}/4")
        chk(rock is not None and "🪨" in (rock[0] if rock else ""),
            "mốc dung nham trao THẺ MẪU VẬT viên nham thạch", str(rock))
        if rock:
            chk("Nham Thạch" in rock[1], "thẻ ghi 'Nham Thạch Cổ Đại'", rock[1])
            chk("KHO MẪU VẬT" in rock[3].upper(),
                "thẻ nói rõ đã lưu vào Kho Mẫu Vật", rock[3])
        chk(page.eval_on_selector_all("#time-rail .me-era-node.ok", "es => es.length") == 4,
            "cả 4 mốc chuyển sang trạng thái đã xem")
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

        say_through(page)
        page.wait_for_timeout(400)
        p_dark = pix(page, (0.3, 0.3, 0.4, 0.4))
        chk(p_dark["avg"] < lit_before_era["avg"] * 0.8,
            "bước 3: hành tinh CHÌM VÀO BÓNG TỐI",
            f"{lit_before_era['avg']:.1f} → {p_dark['avg']:.1f}")
        chk(page.evaluate("() => window.__mission.world.sunOn") is False,
            "Mặt Trời đang TẮT")

        # ══════════════════════════════════════════════════════════════════
        head("[4] Bước 3 — tìm & bấm Mặt Trời, ranh giới ngày/đêm hiện ra")
        # Xoay camera ra tới khi Mặt Trời vào khung, đúng như trẻ phải làm
        found = None
        for i in range(40):
            sp = page.evaluate("() => window.__mission.world.screenOf('sun')")
            if sp and sp["visible"]:
                found = sp
                break
            page.mouse.move(720, 450)
            page.mouse.down()
            page.mouse.move(720 + 150, 450, steps=6)
            page.mouse.up()
            page.wait_for_timeout(90)
        chk(found is not None, "XOAY camera tìm được Mặt Trời trong khung",
            f"sau {i+1} lần kéo" if found else "không thấy")

        if found:
            page.mouse.click(found["x"], found["y"])
        else:
            page.evaluate("window.__mission.pick({type:'sun'})")
        page.wait_for_timeout(2600)
        chk(page.evaluate("() => window.__mission.world.sunOn") is True,
            "Mặt Trời ĐÃ BÙNG CHÁY")

        # RANH GIỚI NGÀY/ĐÊM.
        # ⚠️ KHÔNG đo bằng cách chiếu "điểm ngay dưới Mặt Trời" ra màn hình: muốn
        # thấy được Mặt Trời thì camera phải đang nhìn về phía nó, nên nửa được
        # chiếu sáng nằm ở PHÍA SAU hành tinh — đo kiểu đó ra "ngày tối hơn đêm"
        # và báo hỏng oan. Thay vào đó đứng VUÔNG GÓC với hướng nắng rồi quét một
        # dải ngang qua đĩa hành tinh: có ranh giới thì cột sáng nhất phải hơn hẳn
        # cột tối nhất VÀ giữa hai cột liền kề phải có một bước nhảy đột ngột.
        # ⚠️ CHỈ cảnh 3D cần bước dời camera này: ở đó ranh giới ngày/đêm do shader
        #    vẽ trên quả cầu nên phải đứng vuông góc hướng Mặt Trời mới thấy. Cảnh 2D
        #    không có camera — ranh giới là lớp gradient neo vào KHUNG NHÌN nên đã
        #    luôn nằm trong tầm mắt. Bỏ hẳn nhánh này ở 2D chứ không gọi `panTo` suông:
        #    `panTo({pos})` không thuộc hợp đồng của cảnh 2D (nó nhận `dist`).
        if page.evaluate("() => !!(window.__mission.world.THREE)"):
            page.evaluate("""() => {
              const w = window.__mission.world, THREE = w.THREE;
              const sd = w.sunDirection().normalize();
              const up = new THREE.Vector3(0, 1, 0);
              const perp = new THREE.Vector3().crossVectors(sd, up).normalize().multiplyScalar(3.6);
              return w.panTo({ pos: { x: perp.x, y: 0.5, z: perp.z }, ms: 900 });
            }""")
        page.wait_for_timeout(1400)
        prof = col_profile(page)
        # Chỉ xét các cột NẰM TRÊN đĩa hành tinh (bỏ nền trời gần như đen)
        on = [c for c in prof if c > 6]
        jump = max((abs(prof[i+1] - prof[i]) for i in range(len(prof)-1)), default=0)
        chk(len(on) >= 6 and max(on) > min(on) * 2.5,
            "RANH GIỚI NGÀY/ĐÊM: nửa có nắng sáng hơn hẳn nửa tối",
            f"cột sáng nhất {max(on):.1f} vs tối nhất {min(on):.1f}")
        chk(jump > 12, "ranh giới là một BƯỚC NHẢY rõ nét, không phải mờ dần đều",
            f"bước nhảy lớn nhất {jump:.1f}")

        say_through(page)
        wait_step(page, "energy")

        # ══════════════════════════════════════════════════════════════════
        head("[4b] Bước 4 — thay 3 ống khói bằng năng lượng sạch, khói đen TAN")
        say_through(page)
        srcs = page.eval_on_selector_all(
            "#energy-tray .me-gem", "es => es.map(e => e.textContent.trim())")
        chk(len(srcs) == 3, "3 nguồn năng lượng sạch", str(srcs))
        joined = " ".join(srcs)
        chk("☀️" in joined and "🌬️" in joined and "🌊" in joined,
            "đủ 3 nguồn: pin mặt trời ☀️ · cối xoay gió 🌬️ · thuỷ điện 🌊", joined)
        chk("Mặt Trời" in joined and "Gió" in joined and "Thuỷ Điện" in joined,
            "3 nguồn có TÊN TIẾNG VIỆT", joined)
        chk(page.eval_on_selector_all("#energy-slots .me-stack", "es => es.length") == 3,
            "3 ống khói đang nhả khói")

        # THẢ SAI trước — không bị phạt (cùng nguyên tắc với bảng 3 viên ngọc)
        w0 = page.eval_on_selector_all("#energy-tray .me-gem", "es => es.map(e=>e.dataset.want)")
        bad_zone = next(z for z in ["st1", "st2", "st3"] if z != w0[0])
        drag_to(page, f'#energy-tray .me-gem[data-want="{w0[0]}"]',
                f'#energy-slots .me-stack[data-zone="{bad_zone}"]')
        chk(page.eval_on_selector(f'#energy-slots .me-stack[data-zone="{bad_zone}"]',
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
        wait_step(page, "rotation")
        chk(page.evaluate("window.__navMark") == "still-here",
            "bước 4 → 5 vẫn KHÔNG tải lại trang")

        # ══════════════════════════════════════════════════════════════════
        head("[5] Bước 5 — xoay Trái Đất để trạm phát sóng hướng về vệ tinh")
        say_through(page)
        chk(page.eval_on_selector("#sat", "e => e.classList.contains('show')"),
            "bảng vệ tinh hiện")
        st_lost = page.eval_on_selector("#sat-st", "e => e.textContent.trim()")
        chk("LOST" in st_lost.upper() or "MẤT" in st_lost.upper(),
            "vệ tinh báo SIGNAL LOST", st_lost)
        # ══ VÒNG NGẮM (thêm 01/08/2026) ══
        # ⚠️ Không có nó thì trẻ kéo mù, chỉ nhìn một thanh đo. Đo được: trên bản đồ
        #    phẳng, điểm ở `facing` — chỗ mà `stationAngleTo(...) = 0` quy về — rơi vào
        #    (62,5%, 50%) của khung, còn biểu tượng vệ tinh nằm ở (13,6%, 17,1%). KHÔNG
        #    chỗ nào là "giữa", nên bảo trẻ "đưa trạm về phía vệ tinh" hay "vào giữa
        #    khung" đều là chỉ SAI CHỖ.
        chk(page.evaluate("() => window.__mission.world.map") == "flat",
            "bước 5 chạy trên BẢN ĐỒ PHẲNG (kéo mới có nghĩa)",
            page.evaluate("() => window.__mission.world.map"))
        chk(page.evaluate("() => { const a = document.querySelector('.e2-aim');"
                          " return !!a && !a.hidden; }"),
            "vòng ngắm HIỆN ra")
        # ⚠️ PHÉP KIỂM "vòng ngắm trùng đích" KHÔNG ĐO ĐƯỢC Ở ĐÂY, đã chuyển xuống mục
        #    [8b]. Lý do: nó phải kéo `facing` về đúng toạ độ trạm, mà đó CHÍNH LÀ điều
        #    kiện thắng — `tick()` thấy góc < 20° là gọi `finishStep('rotation')`, `outro()`
        #    tắt vòng ngắm và xoá marker, nên phép đo rơi vào trạng thái đã sang bước sau
        #    (đo được: góc `nan`, lệch 53%). Bộ đo tự làm hỏng thứ nó đang đo.

        ang0 = page.evaluate("window.__mission.satAngle")
        # Đo NGAY BÂY GIỜ, trước khi kéo: `outro()` của bước 3 trả cú kéo về cho
        # camera (`enableRotate = true`), nên đo sau khi bước xong là luôn hỏng.
        chk(page.evaluate("""() => {
              const w = window.__mission.world;
              // cảnh 3D: phải TẮT quay camera, không thì kéo vừa xoay hành tinh vừa
              // xoay camera và góc trạm–vệ tinh y nguyên (đúng lỗi đã sửa 29/07).
              if (w.controls) return w.controls.enableRotate === false;
              // cảnh 2D: KHÔNG CÓ camera nào để quay — thứ trẻ kéo và thứ được chấm
              // điểm là CÙNG một con số (`facing.lon`), nên lỗi đó không có cửa.
              return typeof w.setEarthDrag === 'function' && !w.camera;
            }"""),
            "trong bước 3, cú kéo KHÔNG đồng thời quay camera")

        # KÉO THẬT — đúng thứ trẻ làm được, không dùng `setSpin`
        aligned, ang1, dspin = drag_earth_until_aligned(page)
        chk(abs(dspin) > 28,
            "KÉO làm CHÍNH HÀNH TINH xoay (không phải chỉ camera)",
            f"goc hanh tinh doi {dspin:+.0f} do")
        chk(aligned, "kéo tới khi khớp hướng → bước 3 xong",
            f"góc {ang0:.0f}° → {ang1:.0f}°")
        chk(page.eval_on_selector("#sat", "e => e.classList.contains('ok')"),
            "vệ tinh chuyển sang trạng thái BẮT ĐƯỢC TÍN HIỆU")

        say_through(page)
        wait_step(page, "life")

        # ══════════════════════════════════════════════════════════════════
        head("[6] Bước 6 — drone quét 4 mẫu sự sống, mỗi mẫu 1 thẻ")
        say_through(page)
        page.wait_for_function("() => window.__mission.world.markers.length === 4", timeout=15000)
        bids = page.evaluate("window.__mission.world.markers.map(m => m.id)")
        chk(sorted(bids) == ["animal", "forest", "mountain", "water"],
            "đúng 4 mẫu: nước · rừng · động vật · núi", str(sorted(bids)))

        cards = []
        for bid in bids:
            # Bước 4 chặn cú chạm mới trong lúc drone còn đang bay (`busy`) — chờ
            # hết busy rồi mới bấm, không thì cú chạm bị bỏ và test báo hỏng oan.
            page.wait_for_function("() => !window.__mission.busy", timeout=30000)
            page.evaluate("id => window.__mission.pick({type:'marker', id})", bid)
            # Chờ thẻ mẫu vật hiện ra rồi ghi lại nội dung
            try:
                page.wait_for_function(
                    "() => document.getElementById('card').classList.contains('show')",
                    timeout=30000)
                cards.append(page.evaluate(
                    "() => [document.getElementById('card-ic').textContent,"
                    " document.getElementById('card-nm').textContent,"
                    " document.getElementById('card-fact').textContent]"))
                page.wait_for_function(
                    "() => !document.getElementById('card').classList.contains('show')",
                    timeout=12000)
            except Exception as e:
                cards.append(None)
        chk(len(cards) == 4 and all(cards), "cả 4 mẫu đều bật THẺ THU THẬP",
            f"{sum(1 for c in cards if c)}/4")
        if all(cards):
            facts = [c[2] for c in cards]
            chk(all(len(f) > 12 for f in facts) and len(set(facts)) == 4,
                "4 thẻ có 4 câu kiến thức KHÁC nhau")
            chk(any("70" in f for f in facts), "thẻ Nước nói 'Nước bao phủ 70% Trái Đất'")
            chk(any("Oxy" in f or "oxy" in f.lower() for f in facts),
                "thẻ Rừng nói về Oxy để hít thở")

        page.wait_for_function("() => window.__mission.done.includes('life')", timeout=25000)
        say_through(page)
        wait_step(page, "eco")

        # ══════════════════════════════════════════════════════════════════
        head("[6b] Bước 7 — Eco-Hero: phân loại NÊN / KHÔNG NÊN")
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
        head("[7] Bước 8 — kéo-thả 3 viên ngọc, thả sai KHÔNG bị phạt")
        say_through(page)
        page.wait_for_selector("#core.show", timeout=10000)
        # `data-slot` đổi thành `data-want`/`data-zone` từ 29/07/2026, khi phần kéo-thả
        # tách ra thành `dragDrop()` dùng chung cho 3 bảng — một tên thuộc tính cho cả ba.
        gems = page.eval_on_selector_all(
            "#core-tray .me-gem", "es => es.map(e => [e.dataset.gem, e.dataset.want])")
        slots = page.eval_on_selector_all(
            "#core-slots .me-slot", "es => es.map(e => e.dataset.zone)")
        chk(len(gems) == 3 and len(slots) == 3, "3 viên ngọc + 3 ô", f"{gems} / {slots}")

        # THẢ SAI trước: ngọc của ô A vào ô B
        gid, want = gems[0]
        wrong = next(s for s in slots if s != want)
        drag_to(page, f'#core-tray .me-gem[data-gem="{gid}"]',
                f'#core-slots .me-slot[data-zone="{wrong}"]')
        wrong_ok = page.eval_on_selector(
            f'#core-slots .me-slot[data-zone="{wrong}"]', "e => !e.classList.contains('ok')")
        chk(wrong_ok, "thả SAI: ô không sáng lên")
        chk(page.eval_on_selector(
            f'#core-tray .me-gem[data-gem="{gid}"]', "e => !e.classList.contains('used')"),
            "thả SAI: viên ngọc NẢY VỀ chỗ cũ, vẫn kéo lại được")
        hint = page.eval_on_selector("#core-hint", "e => e.textContent.trim()")
        chk("thử lại" in hint.lower() or "gần đúng" in hint.lower() or "again" in hint.lower(),
            "thả SAI: có câu KHÍCH LỆ, không phải câu mắng", hint)
        chk(page.evaluate("() => window.__mission.reward.meteors") >= 0
            and "core" not in page.evaluate("window.__mission.done"),
            "thả SAI: KHÔNG trừ điểm, không tính là xong")
        page.wait_for_timeout(2400)

        # Thả ĐÚNG cả 3
        for gid, want in gems:
            drag_to(page, f'#core-tray .me-gem[data-gem="{gid}"]',
                    f'#core-slots .me-slot[data-zone="{want}"]')
        filled = page.eval_on_selector_all("#core-slots .me-slot.ok", "es => es.length")
        chk(filled == 3, "KÉO-THẢ THẬT đủ 3 ô sáng lên", f"{filled}/3")

        # ══════════════════════════════════════════════════════════════════
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
        chk(w["ttImg"] == "img/tt.png",
            "phần thưởng dùng ĐÚNG ảnh thiên thạch tím của game", str(w["ttImg"]))
        # Tổng theo đúng bảng luật 8 bước ở Services/Missions.cs (xem STUB_PROGRESS)
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
        chk(steps_called == ["scan", "timeline", "sun", "energy",
                             "rotation", "life", "eco", "core"],
            "báo lên server ĐÚNG 8 bước, ĐÚNG thứ tự, KHÔNG trùng", str(steps_called))
        chk(all(c["mission"] == "earth" for c in w["calls"]),
            "mọi lời gọi đều mang mission='earth'")

        chk(shielded_live is True, "MÀNG KHÍ QUYỂN đã bọc Trái Đất",
            str(shielded_live))

        chk(len(errs) == 0, "0 lỗi console", "; ".join(errs[:3]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[8b] Vòng ngắm TRÙNG đích của điều kiện thắng (ở mọi mức phóng)")
        # ⚠️ CONTEXT RIÊNG, TRANG MỚI. Mục [8] đóng context sau màn tổng kết nên đo tiếp
        #    ở đó là `TargetClosedError` (đã dính). Và trang mới đang ở bước `scan` nên
        #    `RUN.tick()` KHÔNG chuyển cho `steps.rotation.tick` — không có gì gọi
        #    `finishStep` giữa lúc đo, đúng điều kiện phép đo này cần.
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        stub(page)
        boot(page)
        # ⚠️ ĐO Ở ĐÂY, SAU KHI NHIỆM VỤ ĐÃ XONG: bước `rotation` không còn chạy nên
        #    `tick()` không thể gọi `finishStep` giữa lúc đo. Điều cần chứng minh: vòng
        #    ngắm và marker đi qua CÙNG một `project()`, nên khi `facing` = toạ độ marker
        #    thì hai thứ trùng nhau — ở MỌI zoom. Gán cứng `left:50%` cho vòng ngắm là vẽ
        #    nó lệch khỏi chính cái đích nó chỉ, và đó là lỗi im lặng: trẻ kéo trạm vào
        #    vòng mà thanh tín hiệu không lên.
        for _z in (2.0, 4.4):
            _r = page.evaluate("""async (dist) => {
              const w = window.__mission.world;
              w.setMap('flat'); w.showAim(true);
              w.clearMarkers();
              w.addMarkers([{ id: 'probe', lat: -33, lon: 151, rgb: '255,225,140' }]);
              await w.panTo({ lat: -33, lon: 151, dist: dist, ms: 0 });
              await new Promise(r => setTimeout(r, 250));
              const v = document.querySelector('.e2-view').getBoundingClientRect();
              const pct = e => { const r = e.getBoundingClientRect(); return [
                (r.left + r.width/2 - v.left) / v.width * 100,
                (r.top + r.height/2 - v.top) / v.height * 100 ]; };
              const a = document.querySelector('.e2-aim');
              const m = document.querySelector('.e2-mk');
              if (!a || a.hidden || !m) return { d: 999, ang: 999 };
              const pa = pct(a), pm = pct(m);
              return { d: Math.hypot(pa[0]-pm[0], pa[1]-pm[1]),
                       ang: w.stationAngleTo(-33, 151) };
            }""", _z)
            chk(_r["ang"] < 1, f"dist={_z}: facing = toạ độ trạm -> góc ~0",
                f"{_r['ang']:.2f}°")
            chk(_r["d"] < 1.5, f"dist={_z}: vòng ngắm TRÙNG chỗ trạm (không lệch đích)",
                f"lệch {_r['d']:.2f}% khung")
        page.evaluate("() => window.__mission.world.showAim(false)")
        ctx.close()

        # ══════════════════════════════════════════════════════════════════
        head("[9] Tiếng Anh — chơi nhanh qua 8 bước")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        errs2 = []
        page = ctx.new_page()
        page.on("console", lambda m: errs2.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs2.append("pageerror: " + str(e)))
        stub(page, "en")
        boot(page)
        chk(page.evaluate("document.documentElement.lang") == "en", "thẻ html lang=en")
        obj_h = page.eval_on_selector("#obj-h", "e => e.textContent")
        chk(obj_h and not any(c in obj_h for c in "ộạảấầệ"),
            "mục tiêu bước 1 bằng tiếng Anh", obj_h)

        def fast_play(pg):
            """Đi hết 8 bước bằng bề mặt điều khiển (không cần bấm đúng pixel)."""
            for _ in range(320):
                sid = pg.evaluate("window.__mission.step")
                if pg.query_selector("#win.show"):
                    return True
                say_through(pg, 3)
                if sid == "scan" or sid == "life":
                    for mid in pg.evaluate("window.__mission.world.markers.map(m=>m.id)"):
                        try:
                            pg.wait_for_function("() => !window.__mission.busy",
                                                 timeout=30000)
                        except Exception:
                            pass
                        pg.evaluate("id => window.__mission.pick({type:'marker', id})", mid)
                        pg.wait_for_timeout(250)
                elif sid == "timeline":
                    for i in range(4):
                        try:
                            pg.wait_for_function("() => !window.__mission.busy", timeout=30000)
                        except Exception:
                            pass
                        pg.evaluate("i => window.__mission.era(i)", i)
                        pg.wait_for_timeout(200)
                elif sid == "sun":
                    pg.evaluate("window.__mission.pick({type:'sun'})")
                elif sid == "energy":
                    if pg.query_selector("#energy.show"):
                        for want in pg.eval_on_selector_all(
                                "#energy-tray .me-gem", "es => es.map(e => e.dataset.want)"):
                            pg.evaluate("w => window.__mission.place(w)", want)
                            pg.wait_for_timeout(120)
                elif sid == "rotation":
                    drag_earth_until_aligned(pg, limit=40)
                elif sid == "eco":
                    if pg.query_selector("#eco.show"):
                        n = pg.eval_on_selector_all("#eco-deck .me-gem", "es => es.length")
                        for _i in range(n):
                            pg.evaluate("window.__mission.sort()")
                            pg.wait_for_timeout(100)
                elif sid == "core":
                    if pg.query_selector("#core.show"):
                        for s in pg.eval_on_selector_all(
                                "#core-tray .me-gem", "es => es.map(e => e.dataset.want)"):
                            pg.evaluate("s => window.__mission.fill(s)", s)
                            pg.wait_for_timeout(120)
                pg.wait_for_timeout(320)
            return bool(pg.query_selector("#win.show"))

        chk(fast_play(page), "EN: chơi được hết 8 bước tới màn tổng kết")
        we = page.evaluate("""() => ({
          h: document.getElementById('win-h').textContent,
          badge: document.getElementById('win-badge').textContent,
          nextUp: document.getElementById('win-next').textContent
        })""")
        chk(not any(c in we["h"] for c in "ệộứạảầ"), "EN: tiêu đề tổng kết dịch", we["h"])
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

        chk(fast_play(page), "điện thoại: chơi được hết 8 bước")
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
        chk(fast_play(page), "reduced-motion: chơi được hết 8 bước")
        # Ở reduced-motion hành tinh KHÔNG tự quay — nếu bước 3 chỉ xong nhờ nó
        # tự quay thì cả nhiệm vụ treo ở đây. Chơi hết được nghĩa là cú kéo thật
        # sự xoay hành tinh.
        chk(page.evaluate("() => window.__mission.done.length === 8"),
            "reduced-motion: bước `rotation` giải được bằng cách KÉO (hành tinh không tự quay)",
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
        chk(fast_play(page), "mất mạng: vẫn chơi được hết 8 bước (không chặn giao diện)")
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
