# -*- coding: utf-8 -*-
"""
smoke_route_gate.py — ĐO TRÊN TRANG: cổng lộ trình ở Bản Đồ Thiên Hà
(explorer.html + js/route-gate.js · docs/decisions/003).

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    set PYTHONIOENCODING=utf-8        (Windows — không thì print chữ Việt là lỗi)
    python scratchpad/smoke_route_gate.py

Bộ này canh đúng những thứ ĐỌC CODE KHÔNG THẤY ĐƯỢC:
  · bấm vào hành tinh còn khoá thì bảng thông tin có mở ra hay không (thứ trẻ thật
    sự nhìn thấy), chứ không phải "hàm có return sớm hay không";
  · cổng bịt ĐỦ SÁU đường vào `selectBody` — raycast, danh sách bảng trái (đường
    BÀN PHÍM), Prev/Next. Chặn một đường mà tưởng đã xong là bệnh chính của việc này;
  · bấm vào chỗ khoá phải NÓI GÌ ĐÓ (không im lặng → trẻ tưởng mình bấm trượt);
  · chưa đọc được tiến độ thì nói ĐÚNG lý do, KHÔNG bịa "còn 6 bước nữa";
  · cổng TẮT (vào bản đồ bình thường từ dashboard) thì mọi thứ mở y như trước —
    nếu không thì 7 mẫu vật `planet:*` sẽ khoá vĩnh viễn.

⚠️ KHÔNG ĐO BẰNG CÁCH GỌI `AstroQGate.canVisit()` RỒI TIN NÓ. Đó là đo lại chính
   cái hàm mình vừa viết. Phép đo thật là: BẤM, rồi xem `#info` có mở không.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"

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


def newpage(ctx, lang="vi", cache=None):
    """Mở tab, ghim ngôn ngữ, và gieo cache cổng lộ trình.

    ⚠️ `add_init_script` chạy lại sau MỖI lần điều hướng (bài học đã ghi 4 lần trong
       dự án). Ở đây đó là điều mình MUỐN — cache phải có sẵn trước khi trang dựng
       cảnh. Nhưng nghĩa là không thể dùng cùng một page để thử "xoá cache rồi F5";
       muốn ca đó thì mở page khác với cache=None.
    """
    errs = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    js = "localStorage.setItem('astroq-lang', %s);" % json.dumps(lang)
    if cache is None:
        js += "localStorage.removeItem('astroq-route-gate');"
    else:
        js += "localStorage.setItem('astroq-route-gate', %s);" % json.dumps(
            json.dumps(cache))
    pg.add_init_script(js)
    return pg, errs


def openmap(pg, onboard):
    """Mở bản đồ và chờ cảnh 3D dựng xong (`#loader` biến mất)."""
    pg.goto(BASE + "/explorer.html" + ("?onboard=1" if onboard else ""),
            wait_until="domcontentloaded")
    # ⚠️ Chờ `window.solarApp` chứ không chờ `#loader.hidden`: lớp chờ nạp mờ dần
    #    trong 0,8s và trong lúc đó nó NUỐT MỌI CÚ BẤM (lỗi thật đã ghi 31/07/2026).
    pg.wait_for_function("() => !!window.solarApp && !!window.solarApp.system", timeout=30000)
    pg.wait_for_timeout(1200)          # để `#loader` tan hẳn + pointer-events:none


def info_open(pg):
    return pg.evaluate("() => document.getElementById('info').classList.contains('open')")


def modal_open(pg):
    return pg.evaluate("() => document.getElementById('nm-modal').classList.contains('show')")


def modal_text(pg):
    return pg.evaluate("""() => {
      const m = document.getElementById('nm-modal');
      return {
        title: document.getElementById('nm-modal-title').textContent.trim(),
        msg:   document.getElementById('nm-modal-msg').textContent.trim(),
        yes:   document.getElementById('nm-modal-yes').textContent.trim(),
        no:    document.getElementById('nm-modal-no').textContent.trim(),
        shown: m.classList.contains('show')
      };
    }""")


def close_all(pg):
    pg.evaluate("""() => {
      const m = document.getElementById('nm-modal');
      if (m) { m.classList.remove('show'); }
      const i = document.getElementById('info');
      if (i) { i.classList.remove('open'); }
    }""")


JS_HIT = """(pid) => {
    const app = window.solarApp; if (!app) return null;
    const b = app.system.bodyById(pid); if (!b) return null;
    const p = b.mesh.getWorldPosition(b.mesh.position.clone());
    p.project(app.camera);
    if (p.z > 1) return null;                       // sau lưng camera
    const cv = app.renderer.domElement;
    const r = cv.getBoundingClientRect();
    const x = r.left + (p.x * 0.5 + 0.5) * r.width;
    const y = r.top + (-p.y * 0.5 + 0.5) * r.height;
    if (x < 4 || y < 4 || x > r.right - 4 || y > r.bottom - 4) return null;
    const top = document.elementFromPoint(x, y);
    if (top !== cv) return { blocked: (top && (top.id || top.className)) || '?' };
    return { x, y };
  }"""


def set_deck(pg, open_):
    """Mở / thu gọn bảng điều khiển bên trái bằng CHÍNH hai cái nút của trang.

    ⚠️ Cần cho phép đo raycast: bảng trái rộng ~296px và `#deck.collapsed` đặt
       `pointer-events:none`, nên thu gọn nó là cách DUY NHẤT chắc chắn để cả canvas
       nhận được chuột. Chờ mãi cho hành tinh bay ra khỏi vùng bị che thì chập chờn —
       chu kỳ quỹ đạo của Sao Hoả trong cảnh dài hơn thời gian chờ, đo được: 2 trong
       6 lượt chạy báo "ngoài khung" trong khi sản phẩm không đổi một dòng.
       Đây là thao tác một đứa trẻ cũng làm được, không phải mẹo giả lập.
    """
    pg.evaluate("""(want) => {
      const d = document.getElementById('deck');
      const isOpen = !d.classList.contains('collapsed');
      if (isOpen === want) return;
      document.getElementById(want ? 'deck-reopen' : 'deck-collapse').click();
    }""", open_)
    pg.wait_for_timeout(500)          # transform 0,35s + lề an toàn


def click_planet_3d(pg, pid):
    """Bấm ĐÚNG vào quả cầu trên canvas — đường raycast, thứ trẻ thật sự làm.

    Chiếu tâm hành tinh ra toạ độ màn hình bằng camera của CHÍNH TRANG, không đoán
    pixel. Trả False nếu hành tinh ở sau lưng camera, ngoài khung, HOẶC đang bị một
    phần tử khác phủ lên.

    ⚠️ PHẢI KIỂM `elementFromPoint`. Bảng điều khiển bên trái rộng ~296px phủ hẳn
       một phần canvas: chiếu ra được toạ độ KHÔNG có nghĩa là bấm vào đó sẽ tới
       quả cầu. Lượt chạy đầu của bộ này báo "Trái Đất không mở bảng thông tin" vì
       cú bấm rơi vào bảng trái, tức là một PHÉP ĐO SAI chứ không phải lỗi sản phẩm.
       Cùng bài học với lỗi `#loader` nuốt cú bấm (31/07/2026).
    """
    set_deck(pg, False)          # dọn bảng trái khỏi canvas — xem set_deck()
    pt = pg.evaluate(JS_HIT, pid)
    if not pt or "x" not in pt:
        return False
    pg.mouse.click(pt["x"], pt["y"])
    pg.wait_for_timeout(450)
    return True


LOCKED_CANDIDATES = ["mars", "jupiter", "saturn", "venus",
                     "mercury", "uranus", "neptune"]


def pick_clickable_3d(pg, ids):
    """Trả về id đầu tiên trong `ids` mà lúc NÀY thật sự bấm được trên canvas.

    ⚠️ ĐỪNG GHIM MỘT HÀNH TINH CỐ ĐỊNH. Các hành tinh đang BAY TRÊN QUỸ ĐẠO, nên
       Sao Hoả có lượt nằm ngoài khung nhìn hoặc sau bảng trái. Đo được: ghim Sao Hoả
       thì **2 trong 4 lượt chạy báo hỏng** trong khi sản phẩm không đổi một dòng —
       một phép kiểm chập chờn còn tệ hơn không có, vì người ta sẽ học cách bỏ qua nó.
       Chờ lâu hơn cũng không chữa được: chu kỳ quỹ đạo trong cảnh dài hơn mọi mốc
       chờ hợp lý. Nên: hỏi trang xem cái nào đang bấm được, rồi bấm ĐÚNG cái đó.
       Vẫn là phép đo raycast thật, chỉ không phụ thuộc vào thời điểm chạy.
    """
    set_deck(pg, False)
    for pid in ids:
        pt = pg.evaluate(JS_HIT, pid)
        if pt and "x" in pt:
            return pid
    return None


def click_deck(pg, pid):
    """Bấm vào mục hành tinh ở bảng trái — ĐƯỜNG BÀN PHÍM (chúng là `<button>`).

    ⚠️ SELECTOR ĐÚNG LÀ `.loc-item`, KHÔNG PHẢI `.planet-item`. `.planet-item` do
       `_renderList()` dựng và chính mã nguồn ghi *"legacy; null in merged layout"*
       (`explorer.html:1519`) — nó là MÃ CHẾT, không bao giờ có trong DOM. Lượt chạy
       đầu của bộ này dùng selector đó nên 8 phép đo báo hỏng oan.
    """
    set_deck(pg, True)           # phải MỞ thật: `#deck.collapsed` có pointer-events:none
    n = pg.evaluate("""(pid) => {
      let b = document.querySelector('.loc-item[data-id="' + pid + '"]');
      if (!b) {   // nhóm vùng đang gập → mở ra rồi tìm lại
        const h = document.querySelector('.reg-group.current .reg-head');
        if (h) h.click();
        b = document.querySelector('.loc-item[data-id="' + pid + '"]');
      }
      if (!b) return 0;
      b.scrollIntoView({block:'center'});
      b.click();
      return 1;
    }""", pid)
    pg.wait_for_timeout(500)
    return n == 1


def main():
    OPEN_EARTH = {"route": ["earth", "moon"], "open": ["earth"],
                  "gate": 6, "done": 2, "total": 8}
    OPEN_BOTH = {"route": ["earth", "moon"], "open": ["earth", "moon"],
                 "gate": 6, "done": 6, "total": 8}

    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900})

        # ─────────────────────────────────────────────────────────────
        head("[1] Cong TAT (vao ban do binh thuong) — moi thu mo nhu truoc")
        pg, errs = newpage(ctx, "vi", OPEN_EARTH)
        openmap(pg, onboard=False)
        chk(pg.evaluate("() => window.AstroQGate.active() === false"),
            "khong co ?onboard=1 -> cong TAT")
        pid = pick_clickable_3d(pg, LOCKED_CANDIDATES)
        chk(bool(pid), "tim duoc mot hanh tinh dang bam duoc tren canvas", str(pid))
        if pid:
            chk(click_planet_3d(pg, pid), f"bam duoc vao '{pid}'")
            chk(info_open(pg), f"cong TAT: bam '{pid}' VAN mo bang thong tin")
            chk(not modal_open(pg), "cong TAT: khong hien modal khoa")
        # ⚠️ Day la phep kiem bao ve 7 mau vat `planet:*` va 2 huy hieu planet-3/8.
        chk(pg.evaluate("() => window.AstroQGate.canVisit('neptune')"),
            "cong TAT: Sao Hai Vuong cung mo (khong khoa vinh vien mau vat)")
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[2] Cong BAT, chi mo Trai Dat — bam hanh tinh khac phai bi chan")
        pg, errs = newpage(ctx, "vi", OPEN_EARTH)
        openmap(pg, onboard=True)
        chk(pg.evaluate("() => window.AstroQGate.active() === true"),
            "?onboard=1 -> cong BAT")

        # (a) duong RAYCAST
        pid = pick_clickable_3d(pg, LOCKED_CANDIDATES)
        chk(bool(pid), "tim duoc mot hanh tinh KHOA dang bam duoc", str(pid))
        got = bool(pid) and click_planet_3d(pg, pid)
        if got:
            chk(not info_open(pg),
                f"raycast: bam '{pid}' (dang khoa) KHONG mo bang thong tin")
            chk(modal_open(pg), "raycast: co modal giai thich (khong im lang)")
            t = modal_text(pg)
            chk("Trái Đất" in t["msg"] and "6" in t["msg"] and "8" in t["msg"],
                "loi nhac dem bang BUOC, co con so that", t["msg"][:70])
            chk("2" in t["msg"], "noi ro da xong bao nhieu buoc", t["msg"][:70])
            chk(t["yes"] and "nhiệm vụ" in t["yes"].lower(),
                "co nut di tiep den noi lam duoc viec do", t["yes"])
            chk(t["no"] == "Để sau", "co duong rut lui", t["no"])
        close_all(pg)

        # (b) duong DANH SACH BANG TRAI = duong BAN PHIM
        ok_deck = click_deck(pg, "jupiter")
        chk(ok_deck, "tim thay muc Sao Moc o bang trai")
        if ok_deck:
            chk(not info_open(pg),
                "danh sach (ban phim): bam Sao Moc KHONG mo bang thong tin")
            chk(modal_open(pg), "danh sach (ban phim): van co modal giai thich")
        close_all(pg)

        # (c) TRAI DAT PHAI MO DUOC — khoa ca diem den dau la tre ket cung
        got = click_planet_3d(pg, "earth")
        if not got:
            got = click_deck(pg, "earth")
        chk(got, "bam duoc vao Trai Dat")
        chk(info_open(pg), "Trai Dat MO bang thong tin binh thuong")
        chk(not modal_open(pg), "Trai Dat khong bi modal khoa")

        # (d) Prev/Next cung phai bi chan
        close_all(pg)
        pg.evaluate("() => document.getElementById('nav-next').click()")
        pg.wait_for_timeout(500)
        cur = pg.evaluate("""() => (window.solarApp.selected &&
                                    window.solarApp.selected.cfg.id) || null""")
        chk(cur in (None, "earth"),
            "nut Next KHONG nhay sang hanh tinh dang khoa", f"selected={cur}")

        # (e) Nut "Fly to Sun" — Mat Troi khong nam trong lo trinh nen cung khoa
        close_all(pg)
        pg.evaluate("() => document.getElementById('nav-sun').click()")
        pg.wait_for_timeout(500)
        chk(not info_open(pg), "nut Fly to Sun cung bi cong chan")

        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[3] Dat cong 6/8 -> Mat Trang mo, hanh tinh ngoai lo trinh VAN khoa")
        pg, errs = newpage(ctx, "vi", OPEN_BOTH)
        openmap(pg, onboard=True)
        got = click_planet_3d(pg, "moon") or click_deck(pg, "moon")
        chk(got, "bam duoc vao Mat Trang")
        chk(info_open(pg), "Mat Trang DA MO sau khi dat cong")
        chk(not modal_open(pg), "Mat Trang khong con modal khoa")
        close_all(pg)
        ok_deck = click_deck(pg, "saturn")
        chk(ok_deck and not info_open(pg),
            "Sao Tho VAN khoa (ngoai lo trinh)")
        chk(modal_open(pg), "Sao Tho: van co modal giai thich")
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[4] KHONG doc duoc tien do -> noi DUNG ly do, KHONG bia con so")
        # Chưa đăng nhập + máy sạch: explorer không có token (cố ý không nạp SDK
        # Firebase) nên `st.live` = false. Fail-closed: chỉ mở điểm đến đầu tiên.
        pg, errs = newpage(ctx, "vi", cache=None)
        openmap(pg, onboard=True)
        g = pg.evaluate("() => window.AstroQGate.info()")
        chk(g["known"] is False,
            "khong co so tien do nao -> known=false", str(g["known"]))
        chk(g["open"] == ["earth"],
            "fail-closed: chi mo dung diem den dau tien", str(g["open"]))
        ok_deck = click_deck(pg, "mars")
        chk(ok_deck and not info_open(pg), "Sao Hoa bi chan")
        t = modal_text(pg)
        chk("mất mạng" in t["msg"] or "đăng nhập" in t["msg"],
            "noi DUNG ly do (mat mang / chua dang nhap)", t["msg"][:80])
        # ⚠️ Đây là phép kiểm chống BỊA: lúc này `gate` = 0 vì chưa hỏi được server,
        #    nên câu "còn 6 bước nữa" sẽ là một con số dựng ra từ hư không.
        chk("6/8" not in t["msg"] and "0" not in t["msg"],
            "KHONG bia con so buoc khi chua doc duoc tien do", t["msg"][:80])
        close_all(pg)
        got = click_planet_3d(pg, "earth") or click_deck(pg, "earth")
        chk(got and info_open(pg),
            "Trai Dat VAN mo duoc (khong khoa het -> tre khong ket cung)")
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[5] Ban tieng Anh dich du loi nhac cua cong")
        pg, errs = newpage(ctx, "en", OPEN_EARTH)
        openmap(pg, onboard=True)
        click_deck(pg, "mars")
        t = modal_text(pg)
        chk("locked" in t["title"].lower(), "tieu de modal dich sang EN", t["title"])
        chk("Earth mission" in t["msg"], "loi nhac dich sang EN", t["msg"][:70])
        chk(t["no"] == "Later", "nut rut lui dich sang EN", t["no"])
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()

        # ─────────────────────────────────────────────────────────────
        head("[6] Dien thoai 390x844 — modal khoa khong tran ngang")
        m = br.new_context(viewport={"width": 390, "height": 844},
                           is_mobile=True, has_touch=True)
        pg, errs = newpage(m, "vi", OPEN_EARTH)
        openmap(pg, onboard=True)
        click_deck(pg, "mars")
        chk(modal_open(pg), "modal hien tren dien thoai")
        ov = pg.evaluate("""() => {
          const c = document.querySelector('#nm-modal .nm-modal-card');
          const r = c.getBoundingClientRect();
          return { over: Math.max(0, Math.ceil(r.right - innerWidth)) +
                          Math.max(0, Math.ceil(-r.left)),
                   body: document.documentElement.scrollWidth - innerWidth };
        }""")
        chk(ov["over"] == 0, "the modal khong chia ra ngoai man hinh",
            f"{ov['over']}px")
        chk(ov["body"] <= 0, "trang khong tran ngang", f"{ov['body']}px")
        chk(not errs, "0 loi console", str(errs[:3]))
        pg.close()
        m.close()

        # ─────────────────────────────────────────────────────────────
        head("[7] Nut 'Toi nhiem vu Trai Dat' dan di dau")
        pg, errs = newpage(ctx, "vi", OPEN_EARTH)
        openmap(pg, onboard=True)
        click_deck(pg, "mars")
        chk(modal_open(pg), "modal dang mo truoc khi bam")
        pg.evaluate("() => document.getElementById('nm-modal-yes').click()")
        pg.wait_for_load_state("domcontentloaded")
        pg.wait_for_timeout(700)
        chk("mission-earth.html" in pg.url,
            "bam nut -> sang trang nhiem vu Trai Dat", pg.url.split("/")[-1])
        pg.close()

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
