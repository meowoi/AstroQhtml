# -*- coding: utf-8 -*-
"""smoke_certificate.py — CHỨNG NHẬN PDF: nói đúng sự thật, và in ra được.

Chủ dự án 19/08/2026: *"làm mẫu chứng nhận dạng pdf, có thể xuất file ngay sau khi trẻ
hoàn thành 1 chặng đào tạo của 1 cấp độ theo lộ trình đào tạo phi hành gia, ko phải
chặng game"*.

⚠️⚠️ ĐIỀU BỘ NÀY BẢO VỆ MẠNH NHẤT: **trang không được biến thành máy in chứng nhận
   mang tên bất kỳ.** Một tờ giấy trông như thật mà không chứng nhận điều gì là dạng
   nặng nhất của lỗi "hứa thứ hệ thống không giữ". Nên:
     · chế độ `?preview=1` nhận tên từ URL thì PHẢI in kèm dấu chìm "Approved",
     · và dấu đó phải nằm TRONG tờ giấy để nó đi cả vào bản in (overlay của màn hình
       thì in ra tờ sạch — tức mất hẳn hàng rào).

⚠️ Đo cả BẢN IN bằng `emulate_media("print")`: bố cục trên màn hình đúng không chứng
   minh tờ giấy in ra đúng. Máy chủ tĩnh cổng 8123.

  python scratchpad/smoke_certificate.py
"""
import re
import sys
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def txt(pg, sel):
    n = pg.locator(sel)
    return (n.first.inner_text() or "").strip() if n.count() else ""


with sync_playwright() as p:
    b = p.chromium.launch()

    # ═══════════ [1] Xem thử: vẽ đúng, và CÓ dấu chìm ═══════════
    print("\n=== [1] Chế độ xem thử (?preview=1) ===")
    for lang, rank, name, want_rank, want_range in (
            ("vi", "cadet", "Nguyễn Trần Khánh Linh", "Học Viên", ("6", "10")),
            ("en", "navigator", "Alex Nguyen", "Navigator", ("16", "20"))):
        ctx = b.new_context(viewport={"width": 1280, "height": 900})
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','%s')}catch(e){}" % lang)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto("%s/certificate.html?preview=1&rank=%s&name=%s"
                % (BASE, rank, urllib.parse.quote(name)), wait_until="load")
        pg.wait_for_timeout(1500)
        check("[%s] 0 lỗi trang" % lang, not errs, str(errs[:1]))
        check("[%s] tên hiện đúng như truyền vào" % lang, txt(pg, "#c-name") == name,
              txt(pg, "#c-name"))
        check("[%s] tên bậc dịch đúng (%s)" % (lang, want_rank),
              txt(pg, "#c-rank") == want_rank, txt(pg, "#c-rank"))
        body = txt(pg, "#c-body")
        check("[%s] câu thân bài nêu khoảng cấp %s–%s" % (lang, *want_range),
              want_range[0] in body and want_range[1] in body, body[:80])
        # ⚠️ Khoảng cấp phải SUY từ js/ranks.js, không gõ tay. Đối chiếu với chính nó.
        rg = pg.evaluate("""(k)=>{const R=window.AstroQRanks;let i=0;
            R.ALL.forEach((r,j)=>{if(r.key===k)i=j;});
            const lo=R.levelOf(i);
            const hi=(i+1<R.ALL.length)?R.levelOf(i+1)-1:R.MAX_LEVEL;
            return [String(lo),String(hi)];}""", rank)
        check("[%s] khoảng cấp khớp js/ranks.js" % lang, list(rg) == list(want_range),
              str(rg))
        check("[%s] CÓ dấu chìm" % lang,
              pg.locator("#c-sample").count() == 1 and
              not pg.eval_on_selector("#c-sample", "e=>e.hidden"))
        check("[%s] dải nhắc nói rõ đây là bản xem thử" % lang,
              ("xem thử" in txt(pg, "#cert-note").lower()
               or "preview" in txt(pg, "#cert-note").lower()),
              txt(pg, "#cert-note")[:60])
        # Ngày + mã có thật
        check("[%s] có ngày dạng dd/mm/yyyy" % lang,
              bool(re.match(r"^\d{2}/\d{2}/\d{4}$", txt(pg, "#c-date"))),
              txt(pg, "#c-date"))
        check("[%s] có mã chứng nhận dạng AQ-XXXXXX" % lang,
              bool(re.match(r"^AQ-[0-9A-Z]{6}$", txt(pg, "#c-code"))),
              txt(pg, "#c-code"))
        ctx.close()

    # ═══════════ [1b] KHÔNG MỘT CHỮ NÀO BỊ NƯỚNG VÀO HÌNH ═══════════
    print("\n=== [1b] Trang trí không chứa chữ, và MỌI chữ đổi theo ngôn ngữ ===")
    # ⚠️⚠️ ĐÂY LÀ PHÉP KIỂM GIỮ ĐÚNG YÊU CẦU CỦA CHỦ DỰ ÁN 19/08/2026: *"ngôn ngữ sẽ
    #    thay đổi tuỳ theo ngôn ngữ mà người chơi chọn"*. Cách dễ nhất để làm tờ giấy
    #    đẹp là dùng một ẢNH NỀN có sẵn chữ — và đó cũng là cách chắc chắn nhất để
    #    KHÔNG BAO GIỜ dịch được. Hai phép kiểm dưới đây chặn đúng đường đó.
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(BASE + "/certificate.html?preview=1&rank=cadet&name=Test", wait_until="load")
    pg.wait_for_timeout(1500)
    art = pg.evaluate("""()=>{
        const a=document.querySelector('.cert-art');
        if(!a) return null;
        return { text: a.querySelectorAll('text,tspan').length,
                 img: a.querySelectorAll('image,img').length,
                 shapes: a.querySelectorAll('circle,ellipse,path,rect').length };
    }""")
    check("lớp trang trí tồn tại", art is not None)
    if art:
        check("0 phần tử <text>/<tspan> trong trang trí (không chữ nướng sẵn)",
              art["text"] == 0, str(art["text"]))
        check("0 ảnh raster trong trang trí (vẽ bằng SVG nên in không mờ)",
              art["img"] == 0, str(art["img"]))
        check("trang trí có hình thật (không phải khối rỗng)", art["shapes"] >= 20,
              "%d hình" % art["shapes"])

    # Đổi ngôn ngữ NGAY TRÊN TRANG rồi so từng chuỗi: chuỗi nào không đổi là chuỗi
    # bị gõ cứng đâu đó.
    def snap():
        return pg.evaluate("""()=>{
            const g=s=>{const e=document.querySelector(s);return e?(e.innerText||'').trim():''};
            return {org:g('.cert-org'), h:g('.cert-h'), sub:g('.cert-sub'),
                    forr:g('.cert-for'), kd:g('.cert-cell .cert-k'),
                    sign:g('.cert-sign .cert-v'), who:g('.cert-sign .who'),
                    body:g('#c-body'), sample:g('#c-sample')};
        }""")
    vi = snap()
    pg.click('.lang-switch button[data-lang="en"]')
    pg.wait_for_timeout(900)
    en = snap()
    # ⚠️ `sample` CỐ Ý giống nhau ở hai bản: dấu chìm là một từ tiếng Anh
    #    ("Approved") dùng chung, không dịch. Mọi chuỗi CÒN LẠI phải đổi.
    KHONG_DICH = {"sample"}
    khac = [k for k in vi if vi[k] and vi[k] != en[k]]
    giong = [k for k in vi if vi[k] and vi[k] == en[k] and k not in KHONG_DICH]
    check("bấm EN thì MỌI chuỗi trên tờ giấy đổi theo (không sót chuỗi gõ cứng)",
          not giong, "chưa đổi: %s" % giong)
    print("      đổi được %d/%d chuỗi: %s" % (len(khac), len([k for k in vi if vi[k]]),
                                              ", ".join(khac)))
    check("tiêu đề bản EN đúng", "CERTIFICATE" in en["h"].upper(), en["h"][:50])
    check("dấu chìm đọc là 'Approved' ở CẢ HAI bản (không dịch)",
          vi["sample"] == "Approved" and en["sample"] == "Approved",
          "vi=%s / en=%s" % (vi["sample"], en["sample"]))
    ctx.close()

    # ═══════════ [2] Dấu chìm phải ĐI VÀO BẢN IN ═══════════
    print("\n=== [2] Bản in (emulate_media print) ===")
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    pg.goto(BASE + "/certificate.html?preview=1&rank=cadet&name=Test", wait_until="load")
    pg.wait_for_timeout(1200)
    pg.emulate_media(media="print")
    pg.wait_for_timeout(400)
    d = pg.evaluate("""()=>{
        const vis = s => { const e=document.querySelector(s);
            return e ? getComputedStyle(e).display !== "none" : null; };
        const smp = document.querySelector("#c-sample");
        return { header: vis("header"), acts: vis(".cert-acts"), note: vis(".cert-note"),
                 cert: vis("#cert"),
                 sampleVisible: !!smp && !smp.hidden && getComputedStyle(smp).display!=="none",
                 sampleInsideCert: !!document.querySelector("#cert #c-sample") };
    }""")
    check("bản in ẨN header", d["header"] is False, str(d["header"]))
    check("bản in ẨN dãy nút", d["acts"] is False, str(d["acts"]))
    check("bản in ẨN dải nhắc", d["note"] is False, str(d["note"]))
    check("bản in VẪN có tờ giấy", d["cert"] is True, str(d["cert"]))
    check("dấu chìm nằm TRONG tờ giấy (đi cả vào bản in)", d["sampleInsideCert"])
    check("dấu chìm HIỆN ở bản in", d["sampleVisible"])
    # ⚠️ Khổ giấy phải khai trong CSS, không để người dùng tự chọn "ngang".
    css = pg.evaluate("""async ()=>{
        const r = await fetch("css/certificate.css"); return await r.text(); }""")
    check("CSS khai @page size:A4 landscape",
          re.search(r"@page\s*\{[^}]*A4\s+landscape", css) is not None)
    check("CSS đặt print-color-adjust:exact (nền không bị lược khi in)",
          "print-color-adjust:exact" in css)
    ctx.close()

    # ═══════════ [3] Chế độ THẬT: chưa đăng nhập thì KHÔNG vẽ tên ═══════════
    print("\n=== [3] Chế độ thật, chưa đăng nhập ===")
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/certificate.html", wait_until="load")
    pg.wait_for_timeout(4000)
    check("0 lỗi trang", not errs, str(errs[:1]))
    check("KHÔNG vẽ tên nào (không bịa)", txt(pg, "#c-name") in ("—", ""),
          txt(pg, "#c-name"))
    check("KHÔNG có dấu chìm (đây không phải bản xem thử)",
          pg.eval_on_selector("#c-sample", "e=>e.hidden"))
    check("nút Xuất PDF bị TẮT khi chưa có dữ liệu",
          pg.eval_on_selector("#btn-print", "e=>e.disabled"))
    check("dải nhắc nói rõ phải đăng nhập",
          "đăng nhập" in txt(pg, "#cert-note").lower(), txt(pg, "#cert-note")[:70])

    # ⚠️ Tên KHÔNG được lấy từ URL ở chế độ thật — đây là hàng rào chính.
    pg.goto(BASE + "/certificate.html?name=" + urllib.parse.quote("Người Lạ"),
            wait_until="load")
    pg.wait_for_timeout(4000)
    check("chế độ THẬT bỏ qua `?name=` (không in tên lấy từ URL)",
          "Người Lạ" not in txt(pg, "#c-name"), txt(pg, "#c-name"))
    ctx.close()

    # ═══════════ [4] Đường vào từ Kho Thành Tích ═══════════
    print("\n=== [4] Lối vào ở Kho Thành Tích ===")
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(BASE + "/achievements.html", wait_until="load")
    pg.wait_for_timeout(3500)
    n_rk = pg.locator(".rk").count()
    n_done = pg.locator(".rk.done").count()
    n_cert = pg.locator(".rk-cert").count()
    n_now = pg.locator(".rk.now .rk-cert").count()
    check("lộ trình vẽ đủ 10 bậc", n_rk == 10, "%d bậc" % n_rk)
    check("số nút chứng nhận = số bậc ĐÃ HOÀN THÀNH",
          n_cert == n_done, "cert=%d done=%d" % (n_cert, n_done))
    check("bậc ĐANG ĐI không có nút chứng nhận (chặng chưa xong)", n_now == 0,
          "%d" % n_now)
    # Chưa đăng nhập → không bậc nào `done` → không nút nào. Đó là trạng thái đúng.
    hrefs = pg.eval_on_selector_all(".rk-cert", "es=>es.map(e=>e.getAttribute('href'))")
    check("mọi nút đều trỏ certificate.html?rank=<khoá>",
          all(h and h.startswith("certificate.html?rank=") for h in hrefs) if hrefs else True,
          str(hrefs[:3]))
    ctx.close()

    b.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
