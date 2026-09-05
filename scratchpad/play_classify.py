# -*- coding: utf-8 -*-
"""
play_classify.py — CHƠI THẬT Trạm Phân Loại (ARCADE-12) trên Chromium.

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/play_classify.py

Khuôn DẠY MÁY MỘT KHÁI NIỆM, nên bộ đo hỏi những câu năm game lớp B kia không
có — và câu quan trọng nhất KHÔNG phải "bấm có chạy không":

  · ⚠️⚠️ **THIÊN LỆCH PHẢI THẬT SỰ XẢY RA Ở VÒNG ①.** Cả game chỉ có nghĩa nếu
    dạy thiếu thì máy đoán SAI. Mục [3] chơi thật vòng ① rồi đòi ít nhất một ô
    kết quả `got != truth`. Nếu vùng mẫu bị chỉnh cho "đẹp" thì bài học trung
    tâm biến mất trong im lặng — trang vẫn chạy, chỉ là không dạy gì nữa.
    (Engine đã có `check_teach_engine.py` canh ở tầng dữ liệu; ở đây canh trên
    thứ TRẺ THẬT SỰ NHÌN THẤY.)
  · ⚠️ **VÀ CHIỀU ĐỐI CHỨNG:** vòng ② bổ sung đúng vùng đó thì máy phải đoán
    ĐÚNG. Thiếu chiều này thì một bản "máy luôn sai" cũng qua được mục [3], mà
    lúc đó bài học *"dữ liệu chính là bài học"* mới là thứ chết.
  · ⚠️ **`bright` KHÔNG ĐƯỢC ẢNH HƯỞNG** — vòng ③ có tia vũ trụ rất sáng nhưng
    là NHIỄU; nếu độ sáng lọt vào phép tính thì bẫy đó hỏng.
  · Gán nhãn SAI thì NÓI RA, xoá đúng mấy ô sai, và vòng đó THÔI TÍNH ĐIỂM —
    lặng lẽ dùng nhãn sai thì bộ dạy lệch, lặng lẽ sửa hộ thì trẻ không biết.
  · Thưởng chốt ĐÚNG MỘT LẦN ở cuối lượt, phí trừ đúng một lần (luật `game-run`).
  · Nhãn MÔ PHỎNG phải hiện — đây là bộ phân loại đồ chơi, không phải mô hình
    NASA dùng thật (cùng luật với game-recycle · game-units · mission-orbit).
"""
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
URL = BASE + "/game-classify.html"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def open_page(br, lang="vi", tt=40, w=1440, h=900, touch=False):
    ctx = br.new_context(viewport={"width": w, "height": h},
                         has_touch=touch, is_mobile=touch)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    pg.add_init_script("localStorage.setItem('astroq-lang','%s');"
                       "localStorage.setItem('astroq-asteroids','%d');"
                       "localStorage.removeItem('astroq-classify-best');" % (lang, tt))
    pg.goto(URL, wait_until="load")
    pg.wait_for_selector("#ov-start.show", timeout=8000)
    return ctx, pg, errs


def start(pg):
    pg.click("#start-btn")
    pg.wait_for_selector("#teach:not([hidden])", timeout=8000)


def play_round(pg, right=True):
    """Gán nhãn rồi bấm Huấn luyện. `right=False` = cố ý gán sai hết."""
    pg.evaluate("(r)=>window.__dbg.labelAll(r)", right)
    pg.click("#train")


def go_next(pg):
    pg.click("#next")
    pg.wait_for_timeout(120)


def bal(pg):
    return int(pg.eval_on_selector("#bal", "e=>e.textContent.trim()"))


def main():
    global bad_n
    with sync_playwright() as p:
        br = p.chromium.launch()

        # ── [1] Màn brief · phí vào cửa · nhãn MÔ PHỎNG ───────────────────────
        print("\n[1] Man brief + phi vao cua")
        ctx, pg, errs = open_page(br)
        cfg = pg.evaluate("window.__dbg.cfg()")
        check("COST = 3 (khop Wallet.Fees[classify] va cost o GAMES)",
              cfg["cost"] == 3, str(cfg["cost"]))
        check("thuong toi da >= 3x phi vao cua",
              cfg["ttPerRound"] * cfg["rounds"] >= 3 * cfg["cost"],
              f"{cfg['ttPerRound']}x{cfg['rounds']} vs {cfg['cost']}")
        check("4 vong", cfg["rounds"] == 4, str(cfg["rounds"]))
        b0 = bal(pg)
        check("vi bat dau = 40", b0 == 40, str(b0))
        sim = pg.eval_on_selector(".cl-sim", "e=>e.textContent.trim()")
        check("nhan MO PHONG hien tren san", "MÔ PHỎNG" in sim.upper() or "SIMULAT" in sim.upper(), sim)

        start(pg)
        b1 = bal(pg)
        check("bat dau lot -> tru dung 3 tt", b1 == b0 - 3, f"{b0} -> {b1}")

        # ── [2] Vong ①: kho mau + gan nhan ────────────────────────────────────
        print("\n[2] Vong (1) — kho mau va gan nhan")
        tray = pg.evaluate("window.__dbg.tray()")
        check("vong 1 co 8 mau (curved_bright + dots)", len(tray) == 8, str(len(tray)))
        check("moi mau co nhan dung/sai khai san",
              all(s["truth"] in ("ast", "noise") for s in tray))
        n_cell = pg.eval_on_selector_all("#teach-grid .cl-cell", "es=>es.length")
        check("luoi ve dung so o", n_cell == len(tray), str(n_cell))
        n_svg = pg.eval_on_selector_all("#teach-grid .cl-shot svg", "es=>es.length")
        check("moi o co mot anh quet ve bang SVG (0 file tai them)",
              n_svg == len(tray), str(n_svg))
        # ⚠️ ĐỔI PHÁT BIỂU (không nới lỏng): bản đầu đòi nút Huấn luyện bị KHOÁ
        #    khi chưa gán hết. Nhưng vùng cuộn chỉ ~317px trên lưới 740px nên ô
        #    còn trống thường nằm NGOÀI tầm nhìn — một cái nút xám im lặng ở đó
        #    chỉ làm trẻ tưởng game lỗi. Nay đòi ba điều MẠNH HƠN: nút bấm được ·
        #    bấm khi thiếu thì KHÔNG sang màn kiểm · và nó NÓI RA còn mấy ô.
        dis = pg.eval_on_selector("#train", "e=>e.disabled")
        check("nut Huan luyen bam duoc (khong khoa im lang)", dis is False, str(dis))
        pg.click("#train")
        pg.wait_for_timeout(250)
        still_teach = pg.eval_on_selector("#teach", "e=>!e.hidden")
        tst = pg.eval_on_selector(".toast", "e=>e.textContent.trim()") \
            if pg.query_selector(".toast") else ""
        check("chua gan het thi KHONG sang man kiem", still_teach is True)
        check("va NOI RA con may o chua gan", len(tst) > 3, tst[:60])
        seen = pg.evaluate("""()=>{
            const body=document.querySelector('.dg-body');
            const cells=[...document.querySelectorAll('#teach-grid .cl-cell')];
            const i=cells.findIndex((c,k)=>!c.classList.contains('done'));
            if(i<0) return null;
            const b=body.getBoundingClientRect(), c=cells[i].getBoundingClientRect();
            return c.bottom>b.top && c.top<b.bottom;}""")
        check("o con thieu duoc cuon vao tam nhin", seen is True, str(seen))

        # ⚠️⚠️ PHÉP KIỂM ĐẮT GIÁ NHẤT CỦA MỤC NÀY, và nó bắt được một lỗi thật:
        #    ở màn RỘNG 1440×900 ô mẫu cao 365px trong vùng cuộn chỉ 317px, nên
        #    trẻ thấy ảnh + nút "Tiểu hành tinh" mà **không thấy nút "Nhiễu"** —
        #    một nửa hành động chính nằm dưới mép, không dấu hiệu nào báo. Đọc
        #    CSS thì mọi dòng đều hợp lệ; chỉ đo mới thấy. Đòi: TRỌN ô đầu tiên
        #    (cả hai nút) nằm trong phần nhìn thấy của `.dg-body`.
        fit = pg.evaluate("""()=>{
            const body = document.querySelector('.dg-body');
            const cell = document.querySelector('#teach-grid .cl-cell');
            const btns = cell.querySelectorAll('.cl-lb');
            const b = body.getBoundingClientRect(), c = cell.getBoundingClientRect();
            const last = btns[btns.length-1].getBoundingClientRect();
            return { cellH:Math.round(c.height), viewH:Math.round(b.height),
                     nBtn:btns.length,
                     fits: c.top >= b.top - 1 && last.bottom <= b.bottom + 1 };
        }""")
        check("moi o co DU hai nut nhan", fit["nBtn"] == 2, str(fit["nBtn"]))
        check("⚠️ thay TRON o mau dau tien (ca hai nut) khong phai cuon",
              fit["fits"], f"o {fit['cellH']}px / vung nhin {fit['viewH']}px")

        # bấm THẬT một nút nhãn, không chỉ dùng labelAll
        pg.click("#teach-grid .cl-cell:first-child .cl-lb.ast")
        pr = pg.evaluate("window.__dbg.picks()")
        pressed = pg.eval_on_selector(
            "#teach-grid .cl-cell:first-child .cl-lb.ast", "e=>e.getAttribute('aria-pressed')")
        check("bam nut nhan thi ghi lai lua chon", pr[0] == "ast", str(pr[0]))
        check("aria-pressed lat theo lua chon (trinh doc man hinh biet)",
              pressed == "true", str(pressed))

        # ── [3] THIEN LECH PHAI XAY RA ────────────────────────────────────────
        print("\n[3] Vong (1) — day thieu thi may PHAI doan sai")
        play_round(pg, True)
        pg.wait_for_selector("#test:not([hidden])", timeout=8000)
        res = pg.evaluate("window.__dbg.results()")
        miss = [r for r in res if r["got"] != r["truth"]]
        check("co ket qua kiem", res is not None and len(res) > 0, str(len(res or [])))
        # ⚠️⚠️ ĐÒI ĐÚNG CHỖ THIÊN LỆCH, KHÔNG ĐÒI "ít nhất một ô sai". Bản đầu viết
        #    `len(miss) > 0` và phép thử phá hoại cho thấy nó KHÔNG CÓ RĂNG: dời
        #    vùng `curved_short` về chỗ cũ (0.30, 0.72) thì nó đoán đúng, nhưng
        #    `curved_mid` vẫn sai nên phép kiểm vẫn xanh — tức bài học *"máy chỉ
        #    biết bằng thứ nó được xem"* mất một nửa mà không ai biết. Nay đòi
        #    ĐÍCH DANH: mọi vệt cong NGẮN (`cs*`) phải bị máy xếp nhầm là NHIỄU.
        short = [r for r in res if r["id"].startswith("cs")]
        check("vong 1 co dem vet cong NGAN ra kiem", len(short) > 0, str(len(short)))
        check("⚠️ THIEN LECH XAY RA: moi vet cong ngan bi xep nham la NHIEU",
              len(short) > 0 and all(r["got"] == "noise" and r["truth"] == "ast"
                                     for r in short),
              str([(r["id"], r["got"]) for r in short]))
        check("va no thuc su tinh la sai tren man hinh",
              len(miss) >= len(short), f"{len(miss)}/{len(res)} sai")
        bad_cells = pg.eval_on_selector_all("#test-grid .cl-cell.res.bad", "es=>es.length")
        check("o sai to bang class .bad (thay duoc tren man hinh)",
              bad_cells == len(miss), f"{bad_cells} vs {len(miss)}")
        marks = pg.eval_on_selector_all("#test-grid .cl-mark", "es=>es.map(e=>e.textContent.trim())")
        check("o dung va o sai khac CA DAU chu khong chi khac mau",
              any(m.startswith("✔") for m in marks) and any(m.startswith("✘") for m in marks),
              str(marks[:4]))
        les = pg.eval_on_selector("#lesson", "e=>e.textContent.trim()")
        check("hop bai hoc noi ra so o sai", str(len(miss)) in les, les[:70])
        # ⚠️⚠️ VÀ NÓ PHẢI NHÌN THẤY NGAY, KHÔNG PHẢI CUỘN TỚI. Bản đầu đặt hộp
        #    này ở ĐÁY lưới; trên điện thoại vùng cuộn 289px còn lưới kết quả
        #    950–1540px, tức trẻ phải cuộn qua 6–12 ô mới đọc được câu DUY NHẤT
        #    giải thích vì sao máy sai — mất trọng tâm của cả game. Chỉ soi ảnh
        #    chụp mới thấy; đọc CSS thì mọi dòng đều hợp lệ.
        vis = pg.evaluate("""()=>{
            const b=document.querySelector('.dg-body').getBoundingClientRect();
            const l=document.querySelector('#lesson').getBoundingClientRect();
            return l.top >= b.top - 1 && l.top < b.bottom;}""")
        check("⚠️ hop bai hoc nhin thay NGAY khi sang man kiem", vis is True)
        unsure = pg.eval_on_selector_all("#test-grid .cl-unsure", "es=>es.length")
        check("may danh dau nhung o no CHUA CHAC (isFar)", unsure > 0, str(unsure))

        # ── [4] Vong ②: bo sung dung vung do -> may doan DUNG ─────────────────
        print("\n[4] Vong (2) — bo sung thi may khá len (chieu doi chung)")
        go_next(pg)
        r2 = pg.evaluate("window.__dbg.round()")
        check("sang vong 2", r2 == 1, str(r2))
        play_round(pg, True)
        pg.wait_for_selector("#test:not([hidden])", timeout=8000)
        res2 = pg.evaluate("window.__dbg.results()")
        miss2 = [r for r in res2 if r["got"] != r["truth"]]
        check("⚠️ DOI CHUNG: bo sung xong thi may doan DUNG HET",
              len(miss2) == 0, f"{len(miss2)}/{len(res2)} sai")

        # ── [5] Vong ③: tia vu tru rat sang nhung la NHIEU ────────────────────
        print("\n[5] Vong (3) — do sang khong duoc anh huong")
        go_next(pg)
        play_round(pg, True)
        pg.wait_for_selector("#test:not([hidden])", timeout=8000)
        res3 = pg.evaluate("window.__dbg.results()")
        rays = [r for r in res3 if r["id"].startswith("r")]
        check("vong 3 co mau tia vu tru", len(rays) > 0, str(len(rays)))
        check("tre nhin thay tia vu tru duoc xep la NHIEU",
              all(r["got"] == "noise" for r in rays),
              str([(r["id"], r["got"]) for r in rays]))

        # ⚠️⚠️ PHÉP KIỂM TRÊN KHÔNG CHỨNG MINH `bright` BỊ BỎ QUA, và phép thử phá
        #    hoại đã chỉ ra: vòng ③ DẠY chính `rays` rồi mới đem `rays` ra kiểm,
        #    nên k-NN trả về đúng nhãn bất kể bộ đặc trưng gồm những gì — nó đạt
        #    một cách RỖNG. Chỗ chốt thật là đây: hỏi thẳng engine mà TRANG ĐANG
        #    NẠP, lấy một mẫu rồi chỉ đổi mỗi độ sáng. Kết quả phải y hệt.
        # ⚠️ `pool(name)` nhận MỘT tên vùng và trả mảng MẪU; `train` nhận
        #    [{sample,label}]. Bản đầu tôi đoán chữ ký (truyền mảng tên, đưa
        #    thẳng mẫu vào train) → `predict` trả `null` và bộ đo chết. Đọc
        #    `js/teach-machine.js` rồi hãy gọi, đừng đoán.
        eq = pg.evaluate("""()=>{
            const T = window.AstroQTeach;
            const lab = [];
            ["curved_bright","dots"].forEach(g =>
              T.pool(g).forEach(s => lab.push({ sample:s, label:s.truth })));
            const model = T.train(lab);
            const s = T.pool("curved_mid")[0];
            const dark  = Object.assign({}, s, { bright: 0.02 });
            const light = Object.assign({}, s, { bright: 0.99 });
            const a = T.predict(model, dark), b = T.predict(model, light);
            return { same: a.label === b.label && Math.abs(a.gap - b.gap) < 1e-9,
                     a: a.label, b: b.label };
        }""")
        check("⚠️ doi MOI do sang thi ket qua KHONG DOI (`bright` bi bo qua)",
              eq["same"], f"toi={eq['a']} sang={eq['b']}")

        # ── [6] Vong ④ + ket lut: thuong chot MOT lan ─────────────────────────
        print("\n[6] Vong (4) va man ket qua")
        go_next(pg)
        play_round(pg, True)
        pg.wait_for_selector("#test:not([hidden])", timeout=8000)
        go_next(pg)
        pg.wait_for_selector("#ov-over.show", timeout=8000)
        sc = int(pg.eval_on_selector("#r-score", "e=>e.textContent.trim()"))
        mx = int(pg.eval_on_selector("#r-max", "e=>e.textContent.trim()"))
        paid = int(pg.eval_on_selector("#r-mtr", "e=>e.textContent.trim()"))
        b2 = bal(pg)
        check("choi sach ca 4 vong -> dat 4/4", sc == 4 and mx == 4, f"{sc}/{mx}")
        check("thuong = 4 vong x 3 tt", paid == 12, str(paid))
        check("vi = 40 - 3 (phi) + 12 (thuong)", b2 == 40 - 3 + 12, str(b2))
        best = pg.evaluate("localStorage.getItem('astroq-classify-best')")
        check("ky luc luu vao may", best == "4", str(best))

        # phí KHÔNG bị trừ lần hai khi chơi lại
        pg.click("#again-btn")
        pg.wait_for_selector("#teach:not([hidden])", timeout=8000)
        b3 = bal(pg)
        check("choi lai tru dung MOT lan phi (khong tru hai lan)",
              b3 == b2 - 3, f"{b2} -> {b3}")
        check("0 loi trang o luot choi day du", not errs, str(errs[:2]))
        ctx.close()

        # ── [7] Gan nhan SAI thi noi ra va cho sua ────────────────────────────
        print("\n[7] Gan nhan SAI — noi ra, cho sua, thoi tinh diem")
        ctx, pg, errs = open_page(br)
        start(pg)
        play_round(pg, right=False)          # cố ý gán sai hết
        pg.wait_for_timeout(200)
        still = pg.eval_on_selector("#teach", "e=>!e.hidden")
        picks = pg.evaluate("window.__dbg.picks()")
        clean = pg.evaluate("window.__dbg.clean()")
        toast = pg.eval_on_selector(".toast", "e=>e.textContent.trim()") if \
            pg.query_selector(".toast") else ""
        check("gan sai thi KHONG sang man kiem", still is True)
        check("cac o sai bi xoa nhan de sua lai",
              picks.count(None) > 0, f"{picks.count(None)} o trong")
        check("vong nay THOI TINH DIEM (clean=false)", clean is False, str(clean))
        check("noi ra bang toast, khong im lang", len(toast) > 3, toast[:60])
        # sửa lại cho đúng rồi huấn luyện — vẫn đi tiếp được, chỉ không tính điểm
        # ⚠️ BỌC LẠI ĐỂ BỘ ĐO TỰ KHAI TRẠNG THÁI KHI HỎNG (quy tắc 6 mục 6). Phép
        #    thử phá hoại [C] làm nhánh này chết giữa đường ở `wait_for_selector`
        #    và script dừng KHÔNG in dòng tổng kết nào — đọc ra y như "bộ đo không
        #    chạy" chứ không phải "sản phẩm hỏng".
        try:
            if not pg.eval_on_selector("#test", "e=>!e.hidden"):
                play_round(pg, True)
                pg.wait_for_selector("#test:not([hidden])", timeout=8000)
            for _ in range(3):
                go_next(pg); play_round(pg, True)
                pg.wait_for_selector("#test:not([hidden])", timeout=8000)
            go_next(pg)
            pg.wait_for_selector("#ov-over.show", timeout=8000)
            sc2 = int(pg.eval_on_selector("#r-score", "e=>e.textContent.trim()"))
            paid2 = int(pg.eval_on_selector("#r-mtr", "e=>e.textContent.trim()"))
        except Exception as e:
            sc2 = paid2 = -1
            print(f"  [!] khong choi het luot: {type(e).__name__} · "
                  f"round={pg.evaluate('window.__dbg.round()')} "
                  f"clean={pg.evaluate('window.__dbg.clean()')}")
        check("dat 3/4 vi mot vong da gan sai", sc2 == 3, str(sc2))
        check("thuong theo so vong SACH (3x3)", paid2 == 9, str(paid2))
        check("0 loi trang o nhanh gan sai", not errs, str(errs[:2]))
        ctx.close()

        # ── [8] Thieu tt thi KHONG tru tien ───────────────────────────────────
        print("\n[8] Thieu tt")
        ctx, pg, errs = open_page(br, tt=2)
        pg.click("#start-btn")
        pg.wait_for_selector("#ov-need.show", timeout=8000)
        b = bal(pg)
        check("thieu tt -> hien man can tt", True)
        check("thieu tt -> KHONG tru tien", b == 2, str(b))
        body = pg.eval_on_selector("#need-body", "e=>e.textContent")
        check("noi ro can bao nhieu va dang co bao nhieu",
              "3" in body and "2" in body, body[:80])
        ctx.close()

        # ── [9] Ban EN ────────────────────────────────────────────────────────
        print("\n[9] Ban tieng Anh")
        ctx, pg, errs = open_page(br, lang="en")
        start(pg)
        lb = pg.eval_on_selector("#teach-grid .cl-lb.ast", "e=>e.textContent.trim()")
        brief = pg.eval_on_selector("#brief", "e=>e.textContent")
        check("nhan nut dich sang EN", not re.search(r"[ăâđêôơư]", lb, re.I), lb)
        check("loi brief dich sang EN",
              not re.search(r"[ăâđêôơưạảấầệốớứ]", brief, re.I), brief[:60])
        play_round(pg, True)
        pg.wait_for_selector("#test:not([hidden])", timeout=8000)
        les_en = pg.eval_on_selector("#lesson", "e=>e.textContent")
        check("hop bai hoc dich sang EN",
              not re.search(r"[ăâđêôơưạảấầệốớứ]", les_en, re.I), les_en[:60])
        check("0 loi trang o ban EN", not errs, str(errs[:2]))
        ctx.close()

        # ── [10] Dien thoai doc ───────────────────────────────────────────────
        print("\n[10] Dien thoai 390x844")
        ctx, pg, errs = open_page(br, w=390, h=844, touch=True)
        start(pg)
        # ⚠️ NGƯỠNG +1 LÀ NGƯỠNG CỦA BỘ CHUẨN `audit_viewports.py`, không phải nới
        #    lỏng cho vừa: đo ở 390×844 thì CẢ BỐN game lớp quyết định (classify ·
        #    route · units · recycle) đều ra `scrollWidth 391 / clientWidth 390`,
        #    và phép quét từng phần tử trả về **0 phần tử nào chìa ra ngoài** — đó
        #    là làm tròn sub-pixel của khung dùng chung, không phải thanh cuộn.
        over = pg.evaluate("document.documentElement.scrollWidth - "
                           "document.documentElement.clientWidth")
        wide = pg.evaluate("""()=>{const W=document.documentElement.clientWidth;let n=0;
            document.querySelectorAll('*').forEach(e=>{const b=e.getBoundingClientRect();
              if(b.right>W+0.5&&b.width>0)n++;});return n;}""")
        check("khong tran ngang", over <= 1, str(over))
        check("0 phan tu chia ra ngoai mep phai", wide == 0, str(wide))
        cols = pg.eval_on_selector(
            "#teach-grid", "e=>getComputedStyle(e).gridTemplateColumns.split(' ').length")
        check("luoi con 2 cot o man hep (khong roi ve 1 cot)", cols == 2, str(cols))
        tap = pg.eval_on_selector_all(
            "#teach-grid .cl-lb",
            "es=>es.map(e=>Math.round(e.getBoundingClientRect().height))")
        check("vung cham nhan >= 48px (san cua du an, khong phai 44)",
              tap and min(tap) >= 48, f"min={min(tap) if tap else 0}")
        # chạm thật để chắc đường cảm ứng chạy
        pg.tap("#teach-grid .cl-cell:first-child .cl-lb.ast")
        pr = pg.evaluate("window.__dbg.picks()")
        check("cham thuc su gan duoc nhan", pr[0] == "ast", str(pr[0]))
        check("0 loi trang o dien thoai", not errs, str(errs[:2]))
        ctx.close()

        br.close()

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    sys.exit(1 if bad_n else 0)


if __name__ == "__main__":
    main()
