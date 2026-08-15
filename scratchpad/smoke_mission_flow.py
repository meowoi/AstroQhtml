# -*- coding: utf-8 -*-
"""
smoke_mission_flow.py — ĐO TRÊN CHROMIUM THẬT: bốn tầng của khu nhiệm vụ.

    Trung Tâm Nhiệm Vụ → bản đồ → (hành tinh) → cây chặng → màn chơi

Cách chạy:
    python -m http.server 8123        (trong AstroQhtml/)
    set PYTHONIOENCODING=utf-8        (Windows — không thì print chữ Việt là lỗi)
    python scratchpad/smoke_mission_flow.py

⚠️ VÌ SAO CẦN BỘ NÀY, KHI `check_pages` ĐÃ CÓ MỤC [20]. Mục [20] soi VĂN BẢN: nó
   chứng minh danh mục khớp server và các dây nối có tồn tại. Nó KHÔNG chứng minh
   được bốn thứ mà chỉ trình duyệt mới trả lời:
     · bấm vào Trái Đất trên bản đồ có THẬT SỰ tới cây chặng không;
     · chặng chưa mở có thật sự bấm KHÔNG ĂN không (`disabled` ở chính cái nút);
     · lối tắt "Chơi tiếp" có nhảy đúng vào chặng đang dở không;
     · bong bóng tên chặng có ĐÈ lên chặng ngay phía trên không (lỗi đã có ở bản
       mẫu, và đọc CSS không thấy — phải đo diện tích chồng lấn).

⚠️ GIEO `AstroQAuth` GIẢ chứ không chặn HTTP: `AstroQProgress` đi qua `waitAuth()`,
   và không có `AstroQAuth` thì nó KHÔNG hề gọi mạng — chặn HTTP là đo một lời gọi
   không bao giờ xảy ra, tức mọi phép kiểm "đạt" một cách RỖNG (bài học
   `smoke_checkout.py` 11/08/2026).
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
UID = "u-flow-test"
STEPS = ["scan", "timeline", "sun", "life", "energy", "eco", "core"]
CACHE_MS = "astroq-mission-steps"
CACHE_GATE = "astroq-route-gate"

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


def seed(pg, done, lang="vi", complete=False, unlocked=None):
    """Gieo phiên đăng nhập giả + cache tiến độ, TRƯỚC khi trang chạy.

    `AstroQAuth` gieo bằng `defineProperty` có setter nuốt lời gán: module ES thật
    (`js/firebase-auth.js`) chạy SAU script cổ điển và sẽ ghi đè một lời gán thường
    — bài học đã ghi ở `smoke_onboard.py`.
    """
    gate = {
        "open": unlocked if unlocked is not None else ["earth"],
        "route": ["earth", "moon"],
        "gate": 5, "done": len(done), "total": len(STEPS),
    }
    pg.add_init_script("""
      localStorage.setItem('astroq-lang', %s);
      localStorage.setItem('astroq-user', JSON.stringify({uid:%s, name:'Smoke'}));
      localStorage.setItem(%s, JSON.stringify({uid:%s, m:{earth:{done:%s,total:%d,complete:%s}}}));
      localStorage.setItem(%s, JSON.stringify(%s));
      var __auth = {
        postProgress: async function(){ return {ok:true, data:{}}; },
        missionStep:  async function(){ return {ok:true, data:{}}; },
        getMissions:  async function(){
          return { ok:true, status:200, data:{ missions:{ earth:{
            steps: %s, doneSteps: %s, done: %s, codex:[], codexTotal:8,
            gate:5, gateMet:%s } }, route:["earth","moon"], unlockedPlaces: %s } };
        }
      };
      Object.defineProperty(window, 'AstroQAuth', {
        configurable:true, get:function(){ return __auth; }, set:function(){}
      });
    """ % (json.dumps(lang), json.dumps(UID),
           json.dumps(CACHE_MS), json.dumps(UID), json.dumps(done), len(STEPS),
           "true" if complete else "false",
           json.dumps(CACHE_GATE), json.dumps(gate),
           json.dumps(STEPS), json.dumps(done),
           "true" if complete else "false",
           "true" if len(done) >= 5 else "false",
           json.dumps(gate["open"])))


def newpage(ctx, done, lang="vi", **kw):
    errs = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    seed(pg, done, lang, **kw)
    return pg, errs


def overlap(pg, a, b):
    """Diện tích chồng lấn (px²) giữa hai phần tử — 0 là không đè nhau."""
    return pg.evaluate("""([sa, sb]) => {
        const A = document.querySelector(sa), B = document.querySelector(sb);
        if (!A || !B) return -1;
        const a = A.getBoundingClientRect(), b = B.getBoundingClientRect();
        const w = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
        const h = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
        return Math.round(w * h);
    }""", [a, b])


def no_overflow(pg):
    return pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ══════════════════════════════════════════════════════════════
        head("[1] missions.html — cua truoc: loi tat + duong sang ban do")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector("#resume:not([hidden])", timeout=15000)

        chk(pg.locator(".mcard").count() == 0,
            "KHONG con luoi the nhiem vu (mot duong vao, khong hai)")
        nm = pg.inner_text("#r-nm")
        chk("Sự sống" in nm, "dong 'Choi tiep' goi dung ten chang dang do", nm)
        sub = pg.inner_text("#r-sub")
        chk("04 / 07" in sub, "dong phu noi dung chang thu may", sub)
        ov = pg.eval_on_selector_all("#ov .cell .v", "es => es.map(e => e.textContent.trim())")
        # WARN KHONG GAN CUNG SO NHIEM VU. Truoc 15/08/2026 dong nay ghim `"0/1"`, va khi
        #   Trai Dat co nhiem vu thu hai thi no bao hong DUNG LUC san pham lam dung — cung
        #   mot ho voi loi "gan cung con so ma noi khac moi la nguon su that" da lap nhieu
        #   lan trong du an. Nguon su that la `js/mission-catalog.js`.
        _nmis = pg.evaluate("() => AstroQCatalog.missions().length")
        chk(ov == ["0/%d" % _nmis, "3/7", "0/8"],
            "bang dieu phoi lay so THAT tu server", "%s (danh muc co %d nhiem vu)" % (ov, _nmis))
        chk(pg.locator("#offline.show").count() == 0,
            "doc duoc tien do -> khong hien dai nhac")

        # Loi tat phai nhay THANG vao chang dang do
        pg.click("#r-go")
        pg.wait_for_url("**/mission-earth.html?step=life", timeout=15000)
        chk("step=life" in pg.url, "loi tat mo dung chang dang do", pg.url)
        chk(not errs, "0 loi trang o Trung Tam Nhiem Vu", str(errs[:2]))
        ctx.close()

        # ── Chua doc duoc tien do -> dau "—", KHONG hien 0 ──
        head("[1b] missions.html — chua dang nhap thi hien dau '—'")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(BASE + "/missions.html", wait_until="load")
        pg.wait_for_selector("#offline.show", timeout=15000)
        ov = pg.eval_on_selector_all("#ov .cell .v", "es => es.map(e => e.textContent.trim())")
        chk(all(v == "—" for v in ov), "ca 3 o hien '—', KHONG hien 0", str(ov))
        chk(pg.locator("#resume[hidden]").count() == 1,
            "chua biet tien do thi AN dong 'Choi tiep' (khong hua mot cho khong co)")
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[2] mission-map.html — 3 trang thai, cham noi CO nhiem vu la vao thang")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-map.html", wait_until="load")
        pg.wait_for_selector(".body.open", timeout=15000)

        st = pg.evaluate("""() => {
            const o = {};
            document.querySelectorAll('.body').forEach(b => {
              o[b.dataset.id] = b.className.replace('body ', '').trim();
            });
            return o;
        }""")
        chk(st.get("earth") == "open", "Trai Dat: co nhiem vu, dang sang", str(st.get("earth")))
        chk(st.get("moon") == "lock", "Mat Trang: chua du 5/7 chang -> chua mo",
            str(st.get("moon")))
        chk(st.get("mars") == "none", "Sao Hoa: chua co nhiem vu (khac 'chua mo')",
            str(st.get("mars")))
        chk(st.get("sun") == "deco sun", "Mat Troi la trang tri", str(st.get("sun")))

        # Đĩa phải nằm ĐÚNG trên đường quỹ đạo của nó — cùng một phép tính ellipse.
        d = pg.evaluate("""() => {
            const map = document.getElementById('map').getBoundingClientRect();
            const b = document.querySelector('.body[data-id="earth"]').getBoundingClientRect();
            const os = [...document.querySelectorAll('.orbit')].map(o => {
              const r = o.getBoundingClientRect();
              return { cx: r.left + r.width/2, cy: r.top + r.height/2,
                       rx: r.width/2, ry: r.height/2 };
            });
            const cx = b.left + b.width/2, cy = b.top + b.height/2;
            // khoang cach chuan hoa toi ellipse gan nhat (1 = nam dung tren duong)
            const best = Math.min(...os.map(o =>
              Math.abs(Math.hypot((cx-o.cx)/o.rx, (cy-o.cy)/o.ry) - 1)));
            return { best, mapw: map.width };
        }""")
        chk(d["best"] < 0.02, "dia Trai Dat nam DUNG tren duong quy dao cua no",
            f"lech {d['best']:.4f}")

        # WARN HANH VI DA DOI 15/08/2026 — VA DOI DUNG NHU THIET KE DU TRU. `goWorld()`
        #   bo qua man hanh tinh khi mot noi chi co MOT nhiem vu; tu khi Trai Dat co HAI
        #   nhiem vu thi cau "choi cai nao" moi la mot cau hoi that, nen man hanh tinh
        #   thanh CUA CHINH. Phep kiem cu ghim `mission-tree.html?m=earth` nen no bao
        #   hong dung luc san pham lam dung. Phat bieu lai theo SO NHIEM VU that.
        _ms = pg.evaluate("() => AstroQCatalog.byWorld('earth').length")
        pg.click('.body[data-id="earth"]')
        if _ms == 1:
            pg.wait_for_url("**/mission-tree.html?m=earth", timeout=15000)
            chk("mission-tree.html?m=earth" in pg.url,
                "noi co DUNG 1 nhiem vu -> vao THANG cay chang", pg.url)
        else:
            pg.wait_for_url("**/mission-planet.html*", timeout=15000)
            chk("mission-planet.html?w=earth" in pg.url,
                "noi co NHIEU nhiem vu -> mo man hanh tinh de chon",
                "%s (%d nhiem vu)" % (pg.url, _ms))
        chk(not errs, "0 loi trang o ban do", str(errs[:2]))
        ctx.close()

        # ── Nơi chưa có nhiệm vụ / chưa mở: PHẢI nói vì sao ──
        head("[2b] mission-map.html — noi khong vao duoc phai NOI VI SAO")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-map.html", wait_until="load")
        pg.wait_for_selector(".body.open", timeout=15000)

        pg.click('.body[data-id="mars"]')
        pg.wait_for_selector("#sheet:not([hidden])", timeout=8000)
        body = pg.inner_text("#sh-p")
        chk("Chưa có nhiệm vụ" in body, "Sao Hoa: noi 'chua co nhiem vu'", body[:60])
        note = pg.inner_text("#sh-note")
        chk("không có nghĩa là bị cấm tới" in note,
            "phan biet 'chua co noi dung' voi 'bi cam toi'", note[:70])
        chk(pg.inner_text("#sh-go").strip().startswith("Mở Bản Đồ"),
            "co mot duong di CO THAT", pg.inner_text("#sh-go"))
        pg.keyboard.press("Escape")
        chk(pg.locator("#sheet[hidden]").count() == 1, "Escape dong bang")

        pg.click('.body[data-id="moon"]')
        pg.wait_for_selector("#sheet:not([hidden])", timeout=8000)
        body = pg.inner_text("#sh-p")
        chk("2 chặng nữa" in body, "Mat Trang: noi CON BAO NHIEU CHANG nua", body[:70])
        chk(pg.locator("#sh-tag").inner_text().strip() != "",
            "co nhan trang thai o bang")
        chk(not errs, "0 loi trang", str(errs[:2]))
        ctx.close()

        # ── Đủ cổng: Mặt Trăng chuyển sang "sắp có" và đi qua js/locks.js ──
        head("[2c] Du 5/7 chang -> Mat Trang 'sap co', mo hop locks.js")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:5], unlocked=["earth", "moon"])
        pg.goto(BASE + "/mission-map.html", wait_until="load")
        pg.wait_for_selector(".body.soon", timeout=15000)
        cls = pg.get_attribute('.body[data-id="moon"]', "class")
        chk("soon" in cls, "Mat Trang doi sang 'sap co nhiem vu'", cls)
        pg.click('.body[data-id="moon"]')
        pg.wait_for_selector("#aq-lock.show", timeout=8000)
        lk = pg.inner_text("#lk-body")
        chk("Phi Hành Gia" in lk, "hop locks.js noi ten goi", lk[:70])
        chk(pg.locator("#sheet[hidden]").count() == 1,
            "KHONG mo them bang thu hai (mot cau tra loi, mot cai hop)")
        chk(not errs, "0 loi trang", str(errs[:2]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[3] mission-tree.html — duong uon, chan hAN chang chua mo")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-tree.html?m=earth", wait_until="load")
        pg.wait_for_selector(".node.now", timeout=15000)

        sts = pg.eval_on_selector_all(
            ".node", "es => es.map(e => e.className.replace('node ','').trim())")
        chk(sts == ["done", "done", "done", "now", "lock", "lock", "lock"],
            "3 chang xong · chang 4 dang mo · con lai khoa", str(sts))
        chk(pg.inner_text("#m-ct").strip() == "3 / 7", "thanh dinh noi dung tien do",
            pg.inner_text("#m-ct"))

        # ⚠️ TRONG BEN PHAI: do lech giua le trai va le phai cua cot duong di.
        gap = pg.evaluate("""() => {
            const p = document.getElementById('tree').getBoundingClientRect();
            const bs = [...document.querySelectorAll('.node-btn')].map(b => b.getBoundingClientRect());
            const l = Math.min(...bs.map(b => b.left)) - p.left;
            const r = p.right - Math.max(...bs.map(b => b.right));
            return { l: Math.round(l), r: Math.round(r) };
        }""")
        chk(abs(gap["l"] - gap["r"]) <= 2,
            "cot duong di CAN GIUA (khong trong ben phai)", str(gap))

        # ⚠️ Bong bóng tên KHÔNG được đè lên chặng ngay phía trên — lỗi thật của bản mẫu.
        ov2 = pg.evaluate("""() => {
            const bub = document.querySelector('.bub');
            const nodes = [...document.querySelectorAll('.node')];
            const now = document.querySelector('.node.now');
            const prev = nodes[nodes.indexOf(now) - 1];
            if (!bub || !prev) return -1;
            const a = bub.getBoundingClientRect(), b = prev.getBoundingClientRect();
            const w = Math.max(0, Math.min(a.right,b.right) - Math.max(a.left,b.left));
            const h = Math.max(0, Math.min(a.bottom,b.bottom) - Math.max(a.top,b.top));
            return Math.round(w*h);
        }""")
        chk(ov2 == 0, "bong bong ten KHONG de len chang ngay phia tren", f"{ov2}px²")

        # Chặn HẲN ở chính cái nút, không phải bằng một câu `if`
        chk(pg.locator(".node.lock .node-btn[disabled]").count() == 3,
            "chang chua mo bi `disabled` (chan ca cho ban phim)")
        pg.click(".node.lock .node-btn", force=True)
        chk(pg.locator("#sheet[hidden]").count() == 1,
            "bam chang khoa: KHONG mo bang gi ca")
        chk(pg.locator("#rule:not([hidden])").count() == 1,
            "nhung dieu kien mo van doc duoc ma khong phai cham vao dau")

        # Bảng chi tiết của chặng đang mở
        pg.click(".node.now .node-btn")
        pg.wait_for_selector("#sheet:not([hidden])", timeout=8000)
        chk("Sự sống" in pg.inner_text("#sh-h"), "bang goi dung ten chang",
            pg.inner_text("#sh-h"))
        chk(pg.locator("#sh-note[hidden]").count() == 1,
            "chang chua choi: khong co cau 'khong them thuong'")
        # ⚠️ Bang chi tiet KHONG duoc ve con so thuong nao (server giu MOC).
        sheet_txt = pg.inner_text(".sheet-in")
        chk(not any(w in sheet_txt for w in ("XP", "Thiên thạch", "+20", "+30")),
            "bang KHONG ve con so thuong nao", sheet_txt[:80])
        pg.click("#sh-go")
        pg.wait_for_url("**/mission-earth.html?step=life", timeout=15000)
        chk("step=life" in pg.url, "vao dung chang tu cay chang", pg.url)
        chk(not errs, "0 loi trang o cay chang", str(errs[:2]))
        ctx.close()

        # ── Chơi lại một chặng cũ: bảng phải NÓI TRƯỚC là không có thưởng ──
        head("[3b] Choi lai mot chang cu — noi TRUOC khi bam")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-tree.html?m=earth", wait_until="load")
        pg.wait_for_selector(".node.done", timeout=15000)
        pg.click(".node.done .node-btn")
        pg.wait_for_selector("#sheet:not([hidden])", timeout=8000)
        chk(pg.locator("#sh-note:not([hidden])").count() == 1,
            "co cau noi that ve viec choi lai")
        chk("không nhận thêm" in pg.inner_text("#sh-note"),
            "noi ro khong nhan them thuong", pg.inner_text("#sh-note")[:60])
        chk("Chơi lại" in pg.inner_text("#sh-go"), "nhan nut noi dung viec se lam",
            pg.inner_text("#sh-go"))
        ctx.close()

        # ── Xong hết: thẻ kết + không còn chặng "đang mở" ──
        head("[3c] Xong het 7 chang")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS, complete=True)
        pg.goto(BASE + "/mission-tree.html?m=earth", wait_until="load")
        pg.wait_for_selector("#finish:not([hidden])", timeout=15000)
        chk(pg.locator(".node.now").count() == 0, "khong con chang 'dang mo'")
        chk(pg.locator(".node.done").count() == 7, "ca 7 chang deu la 'da xong'")
        chk(pg.locator("#rule[hidden]").count() == 1,
            "AN cau dieu kien mo (khong con chang nao khoa de ma noi)")
        chk(pg.locator("#jump[hidden]").count() == 1,
            "AN nut 've cho dang choi' (khong con cho nao de ve)")
        chk(not errs, "0 loi trang", str(errs[:2]))
        ctx.close()

        # ── Chưa đọc được tiến độ: mở từ chặng 1 + nói rõ lý do ──
        head("[3d] Chua doc duoc tien do -> mo tu chang 1, noi ro ly do")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(BASE + "/mission-tree.html?m=earth", wait_until="load")
        pg.wait_for_selector("#offline.show", timeout=15000)
        idx = pg.evaluate("() => [...document.querySelectorAll('.node')]"
                          ".findIndex(n => n.classList.contains('now'))")
        chk(idx == 0, "mo tu chang 1 (KHONG doan bang ban sao trong may)", str(idx))
        chk(pg.locator(".node.done").count() == 0, "khong nhan bua chang nao la da xong")
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[4] mission-planet.html — danh sach nhiem vu o mot noi")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-planet.html?w=earth", wait_until="load")
        pg.wait_for_selector(".node", timeout=15000)
        # WARN KHONG GAN CUNG SO NHIEM VU (sua 15/08/2026, luc Trai Dat co cai thu hai).
        #   Dieu phep kiem nay MUON BIET la "man hanh tinh liet ke DUNG nhung nhiem vu
        #   danh muc khai o noi nay", khong phai "co dung mot cai".
        _nw = pg.evaluate("() => AstroQCatalog.byWorld('earth').length")
        chk(pg.locator(".node").count() == _nw,
            "man hanh tinh liet ke DUNG so nhiem vu danh muc khai o Trai Dat",
            "%d node / %d nhiem vu" % (pg.locator(".node").count(), _nw))
        chk("Hành Tinh Xanh" in pg.inner_text(".node-lb b"), "goi dung ten nhiem vu",
            pg.inner_text(".node-lb b"))
        chk("chặng 4/7" in pg.inner_text(".node .sub"), "noi dung chang dang do",
            pg.inner_text(".node .sub"))
        pg.click(".node .node-btn")
        pg.wait_for_url("**/mission-tree.html?m=earth", timeout=15000)
        chk("m=earth" in pg.url, "bam nhiem vu -> cay chang cua no", pg.url)
        chk(not errs, "0 loi trang o man hanh tinh", str(errs[:2]))
        ctx.close()

        head("[4b] Noi chua co nhiem vu: noi that mot cau")
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-planet.html?w=mars", wait_until="load")
        pg.wait_for_selector("#empty:not([hidden])", timeout=15000)
        chk(pg.locator(".node").count() == 0, "khong ve mot danh sach rong")
        chk("chưa có nhiệm vụ nào" in pg.inner_text("#lead").lower(),
            "cau dan noi that", pg.inner_text("#lead"))
        chk(not errs, "0 loi trang", str(errs[:2]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[5] Ban EN — moi tang deu dich")
        for path, sel in (("/missions.html", "#resume:not([hidden])"),
                          ("/mission-map.html", ".body.open"),
                          ("/mission-tree.html?m=earth", ".node.now"),
                          ("/mission-planet.html?w=earth", ".node")):
            ctx = br.new_context(viewport={"width": 1440, "height": 900})
            pg, errs = newpage(ctx, STEPS[:3], lang="en")
            pg.goto(BASE + path, wait_until="load")
            pg.wait_for_selector(sel, timeout=15000)
            chk(pg.evaluate("document.documentElement.lang") == "en",
                f"{path}: the html lang=en")
            txt = pg.inner_text(".wrap")
            # ⚠️ DO BANG BANG CHU CO DAU DAY DU, khong go mot nhum ky tu: du an da
            #    tra gia BA LAN vi mot nhum thieu (co lan phep kiem DAT trong khi san
            #    pham sai). Xem quy tac 8 muc 6 CLAUDE.md.
            viet = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
            viet += viet.upper()
            bad = sorted({c for c in txt if c in viet})
            chk(not bad, f"{path}: khong con chu tieng Viet", str(bad[:8]))
            chk(not errs, f"{path}: 0 loi trang", str(errs[:2]))
            ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[6] Dien thoai 390x844 — khong tran ngang, chu khong bi cat")
        for path, sel in (("/missions.html", "#resume:not([hidden])"),
                          ("/mission-map.html", ".body.open"),
                          ("/mission-tree.html?m=earth", ".node.now"),
                          ("/mission-planet.html?w=earth", ".node")):
            ctx = br.new_context(viewport={"width": 390, "height": 844},
                                 is_mobile=True, has_touch=True,
                                 device_scale_factor=3)
            pg, errs = newpage(ctx, STEPS[:3])
            pg.goto(BASE + path, wait_until="load")
            pg.wait_for_selector(sel, timeout=15000)
            chk(no_overflow(pg), f"{path}: khong tran ngang")
            cut = pg.evaluate("""() => [...document.querySelectorAll('.wrap *')]
                .filter(e => e.children.length === 0 && e.textContent.trim())
                .filter(e => e.scrollWidth > e.clientWidth + 1)
                .map(e => e.textContent.trim().slice(0,24)).slice(0,4)""")
            chk(not cut, f"{path}: khong cat chu", str(cut))
            chk(not errs, f"{path}: 0 loi trang", str(errs[:2]))
            ctx.close()

        # ── Bong bóng trên màn hẹp cũng không được đè ──
        head("[6b] Dien thoai: bong bong ten van khong de len chang tren")
        ctx = br.new_context(viewport={"width": 390, "height": 844},
                             is_mobile=True, has_touch=True, device_scale_factor=3)
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-tree.html?m=earth", wait_until="load")
        pg.wait_for_selector(".node.now", timeout=15000)
        ov3 = pg.evaluate("""() => {
            const bub = document.querySelector('.bub');
            const nodes = [...document.querySelectorAll('.node')];
            const now = document.querySelector('.node.now');
            const prev = nodes[nodes.indexOf(now) - 1];
            const a = bub.getBoundingClientRect(), b = prev.getBoundingClientRect();
            const w = Math.max(0, Math.min(a.right,b.right) - Math.max(a.left,b.left));
            const h = Math.max(0, Math.min(a.bottom,b.bottom) - Math.max(a.top,b.top));
            return Math.round(w*h);
        }""")
        chk(ov3 == 0, "390px: bong bong khong de len chang tren", f"{ov3}px²")
        # Bong bóng phải nằm TRỌN trong khung — nút lệch 56px, bong bóng 250px.
        inb = pg.evaluate("""() => {
            const r = document.querySelector('.bub').getBoundingClientRect();
            return r.left >= -1 && r.right <= window.innerWidth + 1;
        }""")
        chk(inb, "390px: bong bong nam tron trong khung")
        chk(not errs, "0 loi trang", str(errs[:2]))
        ctx.close()

        # ══════════════════════════════════════════════════════════════
        head("[7] Vung cham >= 48px o moi tang")
        for path, sel in (("/missions.html", "#resume:not([hidden])"),
                          ("/mission-map.html", ".body.open"),
                          ("/mission-tree.html?m=earth", ".node.now"),
                          ("/mission-planet.html?w=earth", ".node")):
            ctx = br.new_context(viewport={"width": 390, "height": 844},
                                 is_mobile=True, has_touch=True, device_scale_factor=3)
            pg, errs = newpage(ctx, STEPS[:3])
            pg.goto(BASE + path, wait_until="load")
            pg.wait_for_selector(sel, timeout=15000)
            # ⚠️ ĐO VÙNG CHẠM HIỆU DỤNG, KHÔNG ĐO HỘP CỦA PHẦN TỬ. Đĩa hành tinh trên
            #    bản đồ cố ý vẽ nhỏ (9 thiên thể trong 330px) và nới vùng chạm bằng
            #    một lớp `::after` trong suốt — hit-test tính cho phần tử cha. Đo hộp
            #    thôi thì phép kiểm báo hỏng một thứ ĐANG ĐÚNG, và một phép kiểm hay
            #    báo oan thì sớm muộn bị bỏ qua (bài học `.seg button`, 05/08/2026).
            small = pg.evaluate("""() => [...document.querySelectorAll(
                  'button:not([disabled]), a[href]')]
                .filter(e => e.offsetParent !== null)
                .map(e => {
                  const r = e.getBoundingClientRect();
                  const af = getComputedStyle(e, '::after');
                  const aw = af.content !== 'none' ? parseFloat(af.width)  || 0 : 0;
                  const ah = af.content !== 'none' ? parseFloat(af.height) || 0 : 0;
                  return { t: (e.textContent||e.getAttribute('aria-label')||'?').trim().slice(0,20),
                           w: Math.round(Math.max(r.width, aw)),
                           h: Math.round(Math.max(r.height, ah)) };
                })
                .filter(o => o.h < 44 || o.w < 44)""")
            chk(not small, f"{path}: moi nut deu >= 44px", str(small[:3]))
            ctx.close()

        # ⚠️ CÂU HỎI THẬT KHÔNG PHẢI "NÚT CÓ TO KHÔNG" MÀ LÀ "CHẠM VÀO GIỮA ĐĨA THÌ
        #    TRÚNG CÁI GÌ". Vùng chạm 48px của Trái Đất và của Mặt Trăng CHỒNG NHAU
        #    trên màn hẹp (hai tâm chỉ cách ~25px), nên phép đo kích cỡ một mình không
        #    đủ — chỉ `elementFromPoint` mới trả lời. Cùng lối đo đã bắt được lỗi
        #    `#loader` nuốt cú bấm ở explorer.html.
        head("[7b] Cham vao TAM tung dia thi trung dung thien the do")
        for w, h in ((390, 844), (1440, 900)):
            ctx = br.new_context(viewport={"width": w, "height": h})
            pg, errs = newpage(ctx, STEPS[:5], unlocked=["earth", "moon"])
            pg.goto(BASE + "/mission-map.html", wait_until="load")
            pg.wait_for_selector(".body.open", timeout=15000)
            # ⚠️ PHẢI CUỘN BẢN ĐỒ VÀO KHUNG NHÌN TRƯỚC. `elementFromPoint` làm việc
            #    trên toạ độ KHUNG NHÌN: bản đồ nằm dưới màn thì mọi toạ độ đều nằm
            #    ngoài và hàm trả `null` — phép kiểm báo hỏng cả 9 thiên thể trong khi
            #    sản phẩm không sai gì. Đây là lỗi của PHÉP ĐO, không phải của trang.
            pg.evaluate("document.getElementById('map')"
                        ".scrollIntoView({block:'center'})")
            pg.wait_for_timeout(120)
            miss = pg.evaluate("""() => {
                const bad = [];
                document.querySelectorAll('.body').forEach(b => {
                  const r = b.getBoundingClientRect();
                  const el = document.elementFromPoint(r.left + r.width/2,
                                                      r.top + r.height/2);
                  const hit = el && el.closest ? el.closest('.body') : null;
                  if (!hit || hit.dataset.id !== b.dataset.id) {
                    bad.push(b.dataset.id + ' -> ' + (hit ? hit.dataset.id : '?'));
                  }
                });
                return bad;
            }""")
            chk(not miss, f"{w}px: tam moi dia deu tra ve dung thien the", str(miss))
            ctx.close()

        # ══════════════════════════════════════════════════════════════
        # ⚠️ NUT NOI "VE CHO DANG CHOI" — chi hien khi chang dang mo RA KHOI khung
        #    nhin. Hien thuong truc la mot cai nut luon o do ma phan lon thoi gian bam
        #    vao khong doi gi. Doc CSS khong tra loi duoc cau nay: phai cuon that.
        #    Muc nay cung la CHO DUY NHAT doc `window.__tree` — mot be mat test khai ra
        #    ma 0 cho doc thi chinh no la mot loi khai sai (bai hoc `lv`/`AstroQRanks.ALL`).
        #    ⚠️⚠️ ĐO Ở MÀN THẤP (390×500), VÀ ĐÂY LÀ SỐ ĐO CHỨ KHÔNG PHẢI TUỲ HỨNG.
        #       Đo được: với 7 chặng thì trang cao **1158px** ở khổ 390, tức trên
        #       1440×900 (và cả 390×844) cả đường đi nằm gọn một màn — cuộn lên đỉnh
        #       thì chặng đang mở VẪN trong khung, nút nhảy ẩn là ĐÚNG, và một phép
        #       kiểm đo ở đó chỉ báo hỏng oan. Nút này chỉ có việc để làm khi đường đi
        #       dài hơn màn hình: điện thoại xoay ngang, cửa sổ thấp, hoặc nhiệm vụ
        #       nhiều chặng hơn. Đó cũng là lý do nó ĐƯỢC GIỮ dù hôm nay hiếm khi hiện.
        head("[8] Cay chang: nut 've cho dang choi' + mot dinh nghia 'dang nhin thay'")
        ctx = br.new_context(viewport={"width": 390, "height": 500},
                             is_mobile=True, has_touch=True)
        pg, errs = newpage(ctx, STEPS[:3])
        pg.goto(BASE + "/mission-tree.html?m=earth", wait_until="load")
        pg.wait_for_selector(".node.now", timeout=15000)
        st = pg.evaluate("() => ({at: __tree.at, done: __tree.complete, known: __tree.known})")
        chk(st == {"at": 3, "done": False, "known": True},
            "be mat test noi dung trang thai", str(st))
        chk(pg.evaluate("() => __tree.curInView()"),
            "mo trang la da cuon toi chang dang mo")
        chk(not pg.evaluate("() => __tree.jumpVisible"),
            "chang dang mo con trong khung -> AN nut nhay")

        pg.evaluate("window.scrollTo(0, 0)")
        pg.wait_for_timeout(400)
        chk(not pg.evaluate("() => __tree.curInView()"), "cuon len dinh: chang ra khoi khung")
        chk(pg.evaluate("() => __tree.jumpVisible"), "luc do nut nhay HIEN ra")
        pg.click("#jump")
        pg.wait_for_timeout(900)
        chk(pg.evaluate("() => __tree.curInView()"), "bam nut nhay: chang tro lai khung")
        chk(not pg.evaluate("() => __tree.jumpVisible"), "ve toi noi thi nut tu AN")
        chk(not errs, "0 loi trang", str(errs[:2]))
        ctx.close()

        br.close()

    print(f"\n=== KET QUA: {ok} dat / {fail} hong ===")
    if FAILS:
        print("Hong:")
        for f in FAILS:
            print("  ·", f)
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
