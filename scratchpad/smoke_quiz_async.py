# -*- coding: utf-8 -*-
"""smoke_quiz_async.py — quiz.html sau khi cau hoi chuyen sang TAI KHONG DONG BO.

Tu 07/08/2026 `quiz.html` khong con nap ca bank bang `<script src>`; no nap muc luc
roi `import()` dung 5 file cau. Bo nay do TREN TRANG nhung thu doc code khong thay:

  · man cho co chu, khong phai o trong
  · cau hoi that su hien ra, du 4 lua chon, bam duoc
  · doi VI/EN GIUA LUC DANG TAI khong giet trang (loi that de xay ra nhat)
  · mat mang -> hien hop thoai noi that + nut Thu lai, KHONG de trang trong
  · "Lam lai" rut de MOI chu khong lap y nguyen
  · dien thoai 390x844

  python -m http.server 8123     (trong AstroQhtml/)
  python scratchpad/smoke_quiz_async.py
"""
import functools, io, os, sys, threading
import http.server, socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8133
# ⚠️⚠️ `?nosw=1` — TAT SERVICE WORKER CHO BO DO NAY, VA DAY LA VIEC BAT BUOC CHU
#    KHONG PHAI CHO CHAC. Muc [3] gia lap MAT MANG bang `pg.route("**/js/quiz/*.js")`
#    roi doi hop thoai "chua tai duoc cau hoi". Nhung `pg.route` KHONG chan fetch
#    phat ra tu SERVICE WORKER — nen khi sw kip gianh quyen dieu khien trang, no tu
#    lay file quiz ve, trang vao luot binh thuong, va hop thoai khong bao gio hien:
#    bo do treo o `wait_for_selector("#load-modal.show")` roi chet giua duong.
#    ⚠️ Do duoc 26/08/2026, chay MOT MINH khong co gi khac chay cung: **1/3 luot
#       hong** (8 dat / exit 1) — tuc ghi chep cu ("chay mot minh thi 23/0") dua
#       tren qua it luot. Sau khi them `?nosw=1`: **12/12 luot sach**. Neu ti le hong
#       van la 1/3 thi 12 luot sach lien tiep chi co xac suat **0,77%** — nen day la
#       bang chung du manh, du van la [Inference]: to chua CHUNG MINH duoc service
#       worker la nguyen nhan, chi thay tat no di thi cai chap chon bien mat, va co
#       che thi khop (log server cho thay `GET /sw.js` + `GET /offline.html` chay
#       ngay trong luc bo do dang do).
#    ⚠️ `?nosw=1` la cong tac CO SAN cua `js/ui-common.js`, dung cho dung viec nay
#       ("can cho luc do" — chu thich o chinh file do). KHONG phai ta bia them mot
#       duong ri cho san pham de bo do de chay.
#    ⚠️ Doi lai: bo do nay KHONG con noi gi ve hanh vi cua trang KHI CO service
#       worker. Do la viec cua `probe_sw_fast` va `smoke_sw`, khong phai cua no.
URL = "http://127.0.0.1:%d/quiz.html?nosw=1" % PORT

ok_n = bad_n = 0


def check(label, cond, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % (extra,)) if extra else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % (extra,)) if extra else ""))


def co_dau_viet(s):
    """Co ky tu tieng Viet co dau khong. ⚠️ ĐU CA HAI KIEU CHU — du an da tra gia
    BA LAN vi go mot nhum ky tu: lan 3 nhum chi co chu THUONG ma chuoi kiem la chu
    HOA, nen phep kiem DAT trong khi san pham sai. Xem CLAUDE.md muc 6 quy tac 8."""
    low = ("ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩị"
           "òóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ")
    return any(c in low or c in low.upper() for c in s)


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    srv.RequestHandlerClass.log_message = lambda *a, **k: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def new_page(b, lang="vi", vp=None):
    ctx = b.new_context(viewport=vp or {"width": 1440, "height": 900})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror:" + str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text)
          if m.type == "error" else None)
    ctx.add_init_script("localStorage.setItem('astroq-lang', %r);" % lang)
    return ctx, pg, errs


def q_ready(pg):
    """Cho toi khi cau hoi THAT hien ra (4 lua chon co chu)."""
    pg.wait_for_function(
        """() => {
             const o = document.querySelectorAll('#q-options .opt, #q-options button');
             const t = document.getElementById('q-text');
             return o.length === 4 && t && t.textContent.trim().length > 8;
           }""", timeout=15000)


def main():
    global bad_n
    srv = serve()
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()

            print("\n=== [1] Man cho: co chu, khong phai o trong ===")
            ctx, pg, errs = new_page(b)
            # Ham mang cham lai de bat duoc man cho — khong lam cham thi tren may
            # nay 5 file ve trong ~20ms va khong bao gio thay trang thai cho.
            pg.route("**/js/quiz/*.js", lambda r: (pg.wait_for_timeout(1),
                                                   r.continue_()) and None)
            pg.goto(URL, wait_until="commit")
            txt = ""
            for _ in range(80):
                txt = pg.evaluate("() => (document.getElementById('q-text')||{}).textContent || ''")
                if txt.strip() and txt.strip() != "…":
                    break
                pg.wait_for_timeout(25)
            check("luc dang tai, #q-text co chu (khong bo trong)",
                  len(txt.strip()) > 3 and txt.strip() != "…", repr(txt.strip()[:40]))
            check("chu man cho la TIENG VIET (da chon vi)", co_dau_viet(txt), repr(txt.strip()[:40]))
            q_ready(pg)
            check("cau hoi that hien ra sau khi tai xong", True)
            n = pg.evaluate("() => document.querySelectorAll('#q-options button').length")
            check("du 4 lua chon", n == 4, n)
            check("0 loi console/pageerror", not errs, errs[:3])
            ctx.close()

            print("\n=== [2] Doi VI/EN GIUA LUC DANG TAI ===")
            # Day la loi that de xay ra nhat: `AstroQ.initLang` goi `applyLang`, ma
            # `applyLang` cu doc thang `QUESTIONS[idx].topic` -> TypeError khi chua
            # co cau nao, va no giet CA TRANG chu khong chi hut mot nhan.
            ctx, pg, errs = new_page(b, "vi")
            pg.route("**/js/quiz/*.js", lambda r: (pg.wait_for_timeout(300),
                                                   r.continue_()) and None)
            pg.goto(URL, wait_until="commit")
            pg.wait_for_timeout(120)
            pg.evaluate("""() => {
                localStorage.setItem('astroq-lang', 'en');
                window.dispatchEvent(new StorageEvent('storage',
                  { key: 'astroq-lang', newValue: 'en' }));
            }""")
            hard = [e for e in errs if e.startswith("pageerror")]
            check("doi ngon ngu luc dang tai KHONG nem loi", not hard, hard[:2])
            q_ready(pg)
            en = pg.evaluate("() => document.getElementById('q-text').textContent")
            check("sau khi tai xong, cau hoi hien ra binh thuong",
                  len(en.strip()) > 8, repr(en[:40]))
            check("0 loi console/pageerror", not errs, errs[:3])
            ctx.close()

            print("\n=== [3] Mat mang: noi that, KHONG de trang trong ===")
            ctx, pg, errs = new_page(b)
            pg.route("**/js/quiz/*.js", lambda r: r.abort())
            pg.goto(URL, wait_until="load")
            # ⚠️ MOC 30 GIAY, KHONG PHAI 15 — noi rong 25/08/2026 khi bo nay chet
            #    giua duong o dung day trong cong day du (8 dat / exit 1).
            # ⚠️⚠️ NHUNG NOI RONG MOC KHONG PHAI LA CHUA, VA GHI CHEP CU O DAY DA SAI.
            #    Ngay 25/08 toi ghi la "chay MOT MINH thi 23/0, tuc chap chon theo tai
            #    may". Do lai 26/08 voi nhieu luot hon: chay mot minh, KHONG co gi
            #    khac chay cung, van **hong 1/3 luot**. Tuc ket luan "tai may" dua
            #    tren qua it luot, va cai moc 30 giay chi lam cai chap chon thua ra
            #    it hon chu khong bo duoc no.
            #    Nguyen nhan (va cach chua) o `?nosw=1` — xem khoi chu thich dai o
            #    dong khai `URL` dau file. Giu moc 30 giay: no vo hai (nhanh DAT khong
            #    bao gio cho het moc) va no la luoi do neu co nguyen nhan thu hai.
            pg.wait_for_selector("#load-modal.show", timeout=30000)
            check("hien hop thoai 'chua tai duoc cau hoi'", True)
            vis = pg.evaluate("""() => {
                const m = document.querySelector('#load-modal.show');
                if (!m) return null;
                const r = m.getBoundingClientRect();
                const btn = document.getElementById('load-retry');
                const b = btn.getBoundingClientRect();
                const mid = document.elementFromPoint(b.x + b.width/2, b.y + b.height/2);
                return { w: r.width, txt: m.innerText,
                         btnH: b.height, hit: mid === btn || btn.contains(mid) };
            }""")
            check("hop thoai co chu giai thich", len(vis["txt"].strip()) > 20,
                  repr(vis["txt"][:60].replace("\n", " | ")))
            check("chu bang tieng Viet", co_dau_viet(vis["txt"]))
            check("nut 'Thu lai' bam duoc that (khong bi lop khac phu)", vis["hit"])
            # ⚠️ DOI >= 48, KHONG PHAI >= 44. Lan dau do ra dung 44,0px — tuc ngay
            # tren nguong WCAG, khong con bien an toan, va du an da co mot ca test
            # chap chon that vi the (CLAUDE.md muc 6 quy tac 10). Da nang
            # `.modal-actions button` len min-height:48px o css/quiz.css.
            check("vung cham nut >= 48px (san cua du an, khong phai muc WCAG 44)",
                  vis["btnH"] >= 48, "%.1fpx" % vis["btnH"])
            # Thu lai khi mang da hoi phuc -> phai vao duoc lu
            pg.unroute("**/js/quiz/*.js")
            pg.click("#load-retry")
            q_ready(pg)
            check("bam 'Thu lai' sau khi mang hoi phuc thi vao duoc luot", True)
            gone = pg.evaluate("() => !document.querySelector('#load-modal.show')")
            check("hop thoai loi da dong", gone)
            ctx.close()

            print("\n=== [4] Mot file hong: luot VAN du 5 cau ===")
            ctx, pg, errs = new_page(b)
            # Chan DUNG MOT file cu the — con lai ve binh thuong.
            pg.route("**/js/quiz/star.js", lambda r: r.abort())
            pg.goto(URL, wait_until="load")
            q_ready(pg)
            tot = pg.evaluate("() => document.getElementById('q-total').textContent")
            check("vao duoc luot du mot file bi chan", True)
            # `round()` phai BU cho du — de tre mat mot cau vi loi mang thi moc DAT
            # (>=60%) va bang tong ket thanh hai thuoc do khac nhau giua cac luot.
            check("luot VAN du 5 cau (co bu khi mot file hong)", tot == "5",
                  "#q-total = %s" % tot)
            ctx.close()

            print("\n=== [5] 'Lam lai' rut de MOI ===")
            ctx, pg, errs = new_page(b)
            pg.goto(URL, wait_until="load")
            q_ready(pg)
            first = pg.evaluate("() => document.getElementById('q-text').textContent")
            diff = 0
            for _ in range(6):
                pg.evaluate("() => window.__quizRestart && window.__quizRestart()")
                pg.wait_for_timeout(60)
                try:
                    q_ready(pg)
                except Exception:
                    break
                now = pg.evaluate("() => document.getElementById('q-text').textContent")
                if now != first:
                    diff += 1
            check("co be mat test de lai 'Lam lai' (window.__quizRestart)",
                  pg.evaluate("() => typeof window.__quizRestart === 'function'"))
            check("6 lan lam lai co ra de khac", diff >= 4, "%d/6 khac" % diff)
            check("0 loi console/pageerror", not errs, errs[:3])
            ctx.close()

            print("\n=== [6] Dien thoai 390x844 ===")
            ctx, pg, errs = new_page(b, "vi", {"width": 390, "height": 844})
            pg.goto(URL, wait_until="load")
            q_ready(pg)
            ov = pg.evaluate("""() => ({
                scrollX: document.documentElement.scrollWidth >
                         document.documentElement.clientWidth + 1,
                opts: document.querySelectorAll('#q-options button').length
            })""")
            check("khong tran ngang", not ov["scrollX"])
            check("du 4 lua chon tren dien thoai", ov["opts"] == 4, ov["opts"])
            check("0 loi console/pageerror", not errs, errs[:3])
            ctx.close()

            b.close()
    finally:
        srv.shutdown()

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
    sys.exit(1 if bad_n else 0)


if __name__ == "__main__":
    main()
