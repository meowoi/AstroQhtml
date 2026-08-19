# -*- coding: utf-8 -*-
"""smoke_quiz_lv.py — DO KHO TU DIEU CHINH ("vai 2") tren `quiz.html` THAT.

`check_quiz_split.py` muc [9] da do LUAT CHON (`pickKeys(n, lv)`). Bo do nay do
DAY NOI: cache `astroq-quiz-lv` -> `quiz.html` -> cau thuc su duoc tai. Hai thu
khac nhau: luat dung ma trang khong doc cache thi `lv` van la mot tham so bi bo
qua, dung cai bay chu thich `split_quiz_bank.py` canh bao tu 07/08/2026.

CACH DO — KHONG GOI HAM TRONG TRANG:
  `QUESTIONS` va `drawRound()` nam trong IIFE cua `quiz.html` nen ngoai khong voi
  tơi (da tra gia cho chuyen nay o `shot_sprites.py` 19/08/2026: `ReferenceError`).
  Nen o day doc DUONG MANG: moi cau la mot file `js/quiz/<khoa>.js`, nen danh sach
  request chinh la danh sach khoa da rut. Do that, khong doan.

  python scratchpad/smoke_quiz_lv.py
"""
import functools
import http.server
import io
import os
import socketserver
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8137
ROUNDS = 40          # 40 luot x 5 cau = 200 cau moi cap, du de phan bo on dinh

ok_n = bad_n = 0


def check(label, cond, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % (extra,)) if extra else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % (extra,)) if extra else ""))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    h = functools.partial(Quiet, directory=ROOT)
    srv = socketserver.TCPServer(("127.0.0.1", PORT), h)
    srv.allow_reuse_address = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    srv = serve()
    url = "http://127.0.0.1:%d/quiz.html" % PORT
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()

            def do_round(seed, n=ROUNDS):
                """Mo `quiz.html` n lan voi cache da gieo; tra ve (khoa da tai, loi)."""
                ctx = b.new_context(viewport={"width": 1440, "height": 900})
                ctx.add_init_script(
                    "try{localStorage.setItem('astroq-lang','vi');" +
                    (("localStorage.setItem('astroq-quiz-lv',%s);" % seed) if seed
                     else "localStorage.removeItem('astroq-quiz-lv');") +
                    "}catch(e){}")
                pg = ctx.new_page()
                keys, errs = [], []
                pg.on("request", lambda r: keys.append(
                    r.url.rsplit("/", 1)[-1][:-3]) if "/js/quiz/" in r.url else None)
                pg.on("console",
                      lambda m: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                for _ in range(n):
                    pg.goto(url, wait_until="load")
                    pg.wait_for_selector(".q-text", timeout=15000)
                lv_of = pg.evaluate("() => AstroQQuestions.LV")
                ctx.close()
                return keys, errs, lv_of

            def dist(keys, lv_of):
                d = {1: 0, 2: 0, 3: 0, 0: 0}
                for k in keys:
                    d[lv_of.get(k) or 0] += 1
                tot = sum(d.values()) or 1
                return d, tot

            # ══════════ [1] Chua co cache -> van chay, khong doan cap ══════════
            print("\n=== [1] May sach (chua tung doc duoc server) ===")
            keys0, errs0, lv_of = do_round(None, 12)
            check("van rut duoc de (%d cau / 12 luot)" % len(keys0), len(keys0) == 60,
                  "%d cau" % len(keys0))
            check("0 loi console / pageerror", not errs0, str(errs0[:2]))
            d0, t0 = dist(keys0, lv_of)
            print("      phan bo khi KHONG biet cap: lv1 %.0f%% lv2 %.0f%% lv3 %.0f%%"
                  % (100.0 * d0[1] / t0, 100.0 * d0[2] / t0, 100.0 * d0[3] / t0))
            # ⚠️ KHONG doi phan bo nao o day. Dieu muon bao ve la "khong doan cap",
            #    va do duoc bang cach so voi cap 1 o duoi (phai KHAC).

            # ══════════ [2] Cache cua DUA TRE KHAC phai bi bo qua ══════════
            print("\n=== [2] Cache dong dau uid khac -> bo qua, khong dung ===")
            keys_x, errs_x, _ = do_round(
                "JSON.stringify({uid:'be-khac-999',lv:3})", 12)
            dx, tx = dist(keys_x, lv_of)
            check("van rut duoc de", len(keys_x) == 60, "%d cau" % len(keys_x))
            check("0 loi console / pageerror", not errs_x, str(errs_x[:2]))
            # Chua dang nhap thi `uidNow()` tra rong; cache dong dau uid khac PHAI bi
            # loai, nen phan bo phai giong "khong biet cap" chu khong giong cap 3.
            check("KHONG bi keo len cap 3 (lv3 duoi 45%)",
                  100.0 * dx[3] / tx < 45.0, "%.0f%% lv3" % (100.0 * dx[3] / tx))

            # ══════════ [3] Gieo tung cap -> de PHAI doi ══════════
            print("\n=== [3] Gieo cache tung cap (uid rong = chua dang nhap) ===")
            got = {}
            for lv in (1, 2, 3):
                ks, es, _ = do_round("JSON.stringify({uid:'',lv:%d})" % lv)
                d, t = dist(ks, lv_of)
                got[lv] = (d, t)
                print("      cap %d -> lv1 %4.1f%%  lv2 %4.1f%%  lv3 %4.1f%%  (%d cau)"
                      % (lv, 100.0 * d[1] / t, 100.0 * d[2] / t, 100.0 * d[3] / t, t))
                check("cap %d: du %d cau, 0 loi trang" % (lv, ROUNDS * 5),
                      t == ROUNDS * 5 and not es, "%d cau; %s" % (t, es[:1]))

            pc = lambda lv, k: 100.0 * got[lv][0][k] / got[lv][1]
            check("cap 1 ra nhieu cau lv1 hon cap 3", pc(1, 1) > pc(3, 1),
                  "%.0f%% vs %.0f%%" % (pc(1, 1), pc(3, 1)))
            check("cap 3 ra nhieu cau lv3 hon cap 1", pc(3, 3) > pc(1, 3),
                  "%.0f%% vs %.0f%%" % (pc(3, 3), pc(1, 3)))
            check("cap 1: tre moi gan nhu khong gap cau giai thich co che (<15%)",
                  pc(1, 3) < 15.0, "%.1f%%" % pc(1, 3))
            # Day la phep kiem chong "tham so bi bo qua": neu `quiz.html` khong doc
            # cache thi ba cap cho ra CUNG mot phan bo.
            check("ba cap KHONG cho ra cung mot phan bo (cache co duoc doc that)",
                  abs(pc(1, 1) - pc(3, 1)) > 20.0,
                  "lech %.0f diem" % abs(pc(1, 1) - pc(3, 1)))

            # ══════════ [4] Cap rac trong cache -> khong duoc lam vo ══════════
            print("\n=== [4] Cache rac -> roi ve 'chua biet', khong vo ===")
            for nhan, seed in (("lv = 0", "JSON.stringify({uid:'',lv:0})"),
                               ("lv = 9 (ngoai tran)", "JSON.stringify({uid:'',lv:9})"),
                               ("lv la chu", "JSON.stringify({uid:'',lv:'ba'})"),
                               ("khong phai JSON", "'{['")):
                ks, es, _ = do_round(seed, 6)
                check("%s: van rut du 30 cau, 0 loi" % nhan,
                      len(ks) == 30 and not es, "%d cau; %s" % (len(ks), es[:1]))

            # ══════════ [5] Duong `?terms=` KHONG bi cap do thay de ══════════
            print("\n=== [5] Duong tu bai doc giu nguyen khoa duoc yeu cau ===")
            # Doc bai xong phai duoc hoi DUNG thu vua doc. `black-hole` la lv2 va
            # `black-hole-light` cung lv2 — chon `cmb`(1) + `cmb-when`(3) de neu cap
            # do co chen vao thi thay ngay.
            ctx = b.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                                "localStorage.setItem('astroq-quiz-lv',"
                                "JSON.stringify({uid:'',lv:3}))}catch(e){}")
            pg = ctx.new_page()
            tk, te = [], []
            pg.on("request", lambda r: tk.append(r.url.rsplit("/", 1)[-1][:-3])
                  if "/js/quiz/" in r.url else None)
            pg.on("console", lambda m: te.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: te.append(str(e)))
            pg.goto(url + "?terms=cmb,cmb-when", wait_until="load")
            pg.wait_for_selector(".q-text", timeout=15000)
            check("dang o cap 3 nhung VAN tai dung ca hai khoa bai doc yeu cau",
                  "cmb" in tk and "cmb-when" in tk, str(sorted(set(tk))))
            check("van bu cho du 5 cau", len(tk) == 5, "%d cau" % len(tk))
            check("0 loi console / pageerror", not te, str(te[:2]))
            ctx.close()

            b.close()
    finally:
        srv.shutdown()

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
    sys.exit(1 if bad_n else 0)


if __name__ == "__main__":
    main()
