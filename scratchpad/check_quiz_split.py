# -*- coding: utf-8 -*-
"""check_quiz_split.py — NGAN HANG CAU HOI CHIA THEO FILE: dung va KHONG MAT GI.

Chay tren Chromium that vi du lieu la JS (`export default`), khong phai JSON —
doc bang regex la doan. Cung tien le da ghi cho check_quiz_bank.py.

PHEP KIEM DANG GIA NHAT LA [2] ROUND-TRIP: nap lai ca 100 file qua bo nap moi roi
so TUNG TRUONG voi bank mot-file cu. Do la thu duy nhat chung minh viec cat file
khong lam roi mot chu nao. Phep kiem do TU TAT khi `js/quiz-questions.js` bi xoa
(no da lam xong viec) — va no NOI RA rang minh tu tat, khong im lang bo qua.

  python scratchpad/check_quiz_split.py
"""
import functools, gzip, io, json, os, sys, threading
import http.server, socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "js", "quiz")
OLD = os.path.join(ROOT, "js", "quiz-questions.js")
PORT = 8131

ok_n = bad_n = 0


def check(label, cond, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % (extra,)) if extra else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % (extra,)) if extra else ""))


def gz(path):
    b = io.open(path, "rb").read()
    return len(gzip.compress(b, 9)) / 1024.0


def main():
    global bad_n
    if not os.path.isdir(QDIR):
        sys.exit("HONG: khong thay js/quiz/ — chay scratchpad/split_quiz_bank.py truoc")
    files = sorted(os.path.splitext(f)[0] for f in os.listdir(QDIR) if f.endswith(".js"))

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    srv.RequestHandlerClass.log_message = lambda *a, **k: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    # ⚠️ THU TU NAP QUAN TRONG: bank cu VA muc luc moi dung CUNG mot ten bien
    # `window.AstroQQuestions`. Ban dau toi nap muc luc truoc roi bank cu sau ->
    # bank cu GHI DE muc luc, va 8 phep kiem "bo nap co ham X" bao hong OAN trong
    # khi san pham dung. Nap bank cu TRUOC, giu lai vao `__OLDBANK`, roi moi nap
    # muc luc — muc luc thang, va ban cu van con de doi chieu.
    page = os.path.join(ROOT, "_split_check.html")
    io.open(page, "w", encoding="utf-8").write(
        '<!doctype html><meta charset="utf-8">\n'
        + ('<script src="/js/quiz-questions.js"></script>\n'
           '<script>window.__OLDBANK = window.AstroQQuestions.ALL;</script>\n'
           if os.path.exists(OLD) else '')
        + '<script src="/js/quiz-index.js"></script>\n')

    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append("console:" + m.text)
                  if m.type == "error" else None)
            pg.goto("http://127.0.0.1:%d/_split_check.html" % PORT, wait_until="load")

            print("\n=== [1] Muc luc khop dung tap file trong js/quiz/ ===")
            api = pg.evaluate("() => window.AstroQQuestions ? "
                              "Object.keys(window.AstroQQuestions).sort() : null")
            check("js/quiz-index.js nap duoc, co window.AstroQQuestions", bool(api))
            if not api:
                print("  -> dung o day, moi phep kiem sau se vo nghia")
                b.close(); sys.exit(1)
            for fn in ("load", "round", "pickKeys", "byTerms", "shuffled",
                       "terms", "has", "keysOfTerms", "fill", "groupOf"):
                check("bo nap co %s()" % fn, fn in api)

            idx = pg.evaluate("() => AstroQQuestions.terms().sort()")
            check("muc luc liet ke dung so file", len(idx) == len(files),
                  "muc luc %d vs file %d" % (len(idx), len(files)))
            check("khong co khoa trong muc luc MA THIEU file",
                  not (set(idx) - set(files)), sorted(set(idx) - set(files))[:6])
            check("khong co file MA THIEU trong muc luc",
                  not (set(files) - set(idx)), sorted(set(files) - set(idx))[:6])

            print("\n=== [2] ROUND-TRIP: nap lai 100 file, so voi bank mot-file cu ===")
            if not os.path.exists(OLD):
                print("  [ ]    js/quiz-questions.js da xoa — phep kiem nay TU TAT.")
                print("         (No da lam xong viec: chung minh luot cat khong mat gi.")
                print("          Muon chay lai thi lay bank cu ra: git show <ref>:js/quiz-questions.js)")
            else:
                got = pg.evaluate("""async () => {
                    const keys = AstroQQuestions.terms();
                    const qs = await AstroQQuestions.load(keys);
                    return { n: keys.length, qs: qs };
                }""")
                old = pg.evaluate("() => window.__OLDBANK || null")
                check("doc duoc bank cu de doi chieu", bool(old),
                      "%d cau" % (len(old) if old else 0))
                if old:
                    new = {q["term"]: q for q in got["qs"]}
                    oldm = {q["term"]: q for q in old}
                    check("so cau khop", len(new) == len(oldm),
                          "moi %d vs cu %d" % (len(new), len(oldm)))
                    check("tap khoa khop", set(new) == set(oldm),
                          "lech: %s" % sorted(set(new) ^ set(oldm))[:6])
                    diffs = []
                    for k in sorted(set(new) & set(oldm)):
                        a, c = new[k], oldm[k]
                        for f in ("term", "topic", "q", "opts", "a", "ok", "no",
                                  "hint", "lv", "srcQuote", "srcChecked"):
                            if json.dumps(a.get(f), ensure_ascii=False, sort_keys=True) != \
                               json.dumps(c.get(f), ensure_ascii=False, sort_keys=True):
                                diffs.append("%s.%s" % (k, f))
                        sa = a.get("src") or {}
                        sc = c.get("src") or {}
                        if (sa.get("url"), sa.get("name")) != (sc.get("url"), sc.get("name")):
                            diffs.append("%s.src" % k)
                    check("MOI TRUONG cua MOI cau giong het bank cu", not diffs,
                          "lech %d: %s" % (len(diffs), diffs[:8]))

            print("\n=== [3] `src` la KHOA trong file, thanh OBJECT sau khi nap ===")
            raw = pg.evaluate("""async () => {
                const m = await import("/js/quiz/star.js");
                return typeof m.default.src;
            }""")
            check("file cau khai src bang chuoi (khoa), khong phai object",
                  raw == "string", "typeof = %s" % raw)
            sres = pg.evaluate("""async () => {
                const keys = AstroQQuestions.terms();
                const qs = await AstroQQuestions.load(keys);
                const withSrc = qs.filter(q => q.src);
                return {
                  n: withSrc.length,
                  bad: withSrc.filter(q => !q.src.url || !q.src.name).map(q => q.term),
                  noSrc: qs.filter(q => !q.src).map(q => q.term)
                };
            }""")
            check("moi cau co src deu giai ra duoc name + url", not sres["bad"],
                  sres["bad"][:6])
            check("cau khong co src dung la 5 cau lap trinh",
                  sorted(sres["noSrc"]) == ["algorithm", "condition", "loop",
                                            "sensor", "sequence"],
                  sorted(sres["noSrc"]))

            print("\n=== [4] topic trong file cau KHOP topic cua nhom o muc luc ===")
            # Day la lop chan cho cai bay "hai noi giu mot gia tri": muc luc SINH RA
            # tu cac file, nen lech nghia la co ai sua tay mot ben.
            tres = pg.evaluate("""async () => {
                const bad = [];
                for (const k of AstroQQuestions.terms()) {
                  const m = await import("/js/quiz/" + k + ".js");
                  const g = AstroQQuestions.groupOf(k);
                  const a = JSON.stringify(m.default.topic || null);
                  const b = JSON.stringify(g ? g.t : null);
                  if (a !== b) bad.push(k);
                }
                return bad;
            }""")
            check("khong file nao lech topic voi muc luc", not tres, tres[:8])

            print("\n=== [5] pickKeys: KHONG hai cau cung mot THE trong mot luot ===")
            # Ban cu loc bang `term` — do duoc la vo tac dung (100/100 khoa duy nhat).
            pres = pg.evaluate("""() => {
                let clash = 0, sizes = {};
                for (let i = 0; i < 400; i++) {
                  const ks = AstroQQuestions.pickKeys(5);
                  sizes[ks.length] = 1;
                  const seen = new Set();
                  for (const k of ks) {
                    const g = AstroQQuestions.groupOf(k);
                    const id = g ? (g.c || k) : k;
                    if (seen.has(id)) { clash++; break; }
                    seen.add(id);
                  }
                }
                return { clash, sizes: Object.keys(sizes) };
            }""")
            check("400 luot deu rut dung 5 khoa", pres["sizes"] == ["5"], pres["sizes"])
            check("400 luot, 0 luot co hai cau cung mot the", pres["clash"] == 0,
                  "%d luot trung" % pres["clash"])

            # ⚠️ CHOT "0 loi console" O DAY, TRUOC cac buoc pha hoai co y duoi day.
            # Buoc [6] tu tay chan mang va tu tay goi mot khoa khong co file, nen no
            # SINH RA `net::ERR_FAILED` va `404` — do la bang chung phep chan chay
            # dung, khong phai loi san pham. Do ca luot roi doi 0 loi la tu bao hong.
            clean_errs = list(errs)
            check("0 loi console / pageerror trong van hanh binh thuong",
                  not clean_errs, clean_errs[:3])

            print("\n=== [6] Mot file HONG khong duoc giet ca luot ===")
            print("      (tu day tro xuong console CO loi — do la loi toi co y gay ra)")
            # ⚠️ PHAI TAI LAI TRANG TRUOC KHI CHAN. Cac buoc tren da `import()` het
            # 100 file, ma module da giai quyet thi nam trong MODULE MAP cua trang —
            # `route(...).abort()` khong go duoc no ra, nen lan dau phep kiem nay bao
            # hong OAN: `star` van ve du da bi chan. Tai lai = module map sach.
            pg.goto("http://127.0.0.1:%d/_split_check.html" % PORT, wait_until="load")
            pg.route("**/js/quiz/star.js", lambda r: r.abort())
            fres = pg.evaluate("""async () => {
                try {
                  const qs = await AstroQQuestions.load(["star", "planet", "moon"]);
                  return { n: qs.length, keys: qs.map(q => q.term) };
                } catch (e) { return { threw: String(e) }; }
            }""")
            check("load() KHONG nem loi khi mot file mat mang",
                  not fres.get("threw"), fres.get("threw", ""))
            check("load() tra ve dung cac cau con lai", fres.get("n") == 2,
                  "%s" % (fres.get("keys"),))
            # Duong thu hai: khoa khong co file nao (404 that), khong phai chan mang.
            nres = pg.evaluate("""async () => {
                const qs = await AstroQQuestions.load(["khong-co-file", "moon"]);
                return qs.map(q => q.term);
            }""")
            check("load() bo qua khoa khong co file (404) va giu phan con lai",
                  nres == ["moon"], nres)
            rres = pg.evaluate("""async () => {
                for (let i = 0; i < 12; i++) {
                  const qs = await AstroQQuestions.round(5);
                  if (qs.length !== 5) return { bad: qs.length, i };
                }
                return { ok: true };
            }""")
            check("round(5) VAN du 5 cau du mot file hong (co bu)",
                  rres.get("ok"),
                  "" if rres.get("ok") else "chi ra %s cau o luot %s"
                  % (rres.get("bad"), rres.get("i")))
            pg.unroute("**/js/quiz/star.js")

            print("\n=== [7] byTerms: duong vao tu bai doc ===")
            # ⚠️ PHAI TAI LAI TRANG LAN NUA. `unroute` khong du: mot module nap HONG
            # cung bi trinh duyet NHO trong module map, nen `import("./quiz/star.js")`
            # sau do tra lai dung cai promise da bi tu choi — `star` khong bao gio nap
            # duoc nua trong trang do. Lan dau phep kiem [7] bao hong OAN vi vay.
            pg.goto("http://127.0.0.1:%d/_split_check.html" % PORT, wait_until="load")
            bres = pg.evaluate("""async () => {
                const qs = await AstroQQuestions.byTerms(["star", "moon"], 5);
                const only = await AstroQQuestions.byTerms(["khong-ton-tai"], 5);
                return { n: qs.length, has: qs.map(q => q.term),
                         ghost: only.length };
            }""")
            check("byTerms bu cho du 5 cau", bres["n"] == 5, bres["has"])
            check("byTerms co dung 2 khoa duoc yeu cau",
                  "star" in bres["has"] and "moon" in bres["has"], bres["has"])
            check("byTerms voi khoa khong ton tai tra ve rong (de trang roi ve pickKeys)",
                  bres["ghost"] == 0, bres["ghost"])

            b.close()
    finally:
        os.remove(page)
        srv.shutdown()

    print("\n=== [8] DUONG TAI: do that, khong doan ===")
    ix = gz(os.path.join(ROOT, "js", "quiz-index.js"))
    per = sorted(gz(os.path.join(QDIR, f + ".js")) for f in files)
    avg = sum(per) / len(per)
    five = ix + avg * 5
    print("  muc luc            : %6.1f KB gzip" % ix)
    print("  mot file cau (TB)  : %6.1f KB gzip  (nho nhat %.1f · lon nhat %.1f)"
          % (avg, per[0], per[-1]))
    print("  MOT LUOT 5 cau     : %6.1f KB gzip  = muc luc + 5 file" % five)
    if os.path.exists(OLD):
        oldg = gz(OLD)
        print("  bank mot-file cu   : %6.1f KB gzip" % oldg)
        check("mot luot nhe hon bank cu", five < oldg,
              "%.1f vs %.1f KB — cat %.0f%%" % (five, oldg, 100 * (1 - five / oldg)))
        print("  luot THU HAI tro di: %6.1f KB gzip  (muc luc da cache)" % (avg * 5))
    tot = sum(per)
    print("  ca %d file cong lai: %6.1f KB gzip  (chi tai het neu bo kiem doi)"
          % (len(files), tot))

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
    sys.exit(1 if bad_n else 0)


if __name__ == "__main__":
    main()
