# -*- coding: utf-8 -*-
"""probe_defender_bank.py — cau do cua PHONG THU KHONG GIAN lay tu KHO CHUNG.

Do dung ba dieu ma chu du an bao (22/08/2026):
  [A] cau do KHONG con lay tu mang 8 cau rieng, ma tu CA KHO chung (so cau doc tu dia, khong go cung),
  [B] choi NHIEU LAN van khong gap lai cau da hoi (nho QUA CAC LUOT),
  [C] khong tai duoc kho (`file://`, mat mang) thi VAN co cau do — duong lui.

⚠️ Phep kiem [A] phai hoi bang `from == "bank"`, khong hoi bang "co cau do
   khong": duong lui CUNG cho ra mot cau do, nen mot phep do chi hoi "co hien
   cau nao khong" se DAT ca khi kho chung chua bao gio chay.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/probe_defender_bank.py
"""
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"

dat = 0
hong = 0


def sj(seq):
    """Ghep danh sach thanh chuoi. ⚠️ Phai chiu duoc `None` — cau cua DUONG
       LUI khong co `term`, va mot bo do CHET giua duong thi doc ra y nhu san
       pham hong (quy tac 6 muc 6)."""
    return " · ".join("(khong ten)" if x is None else str(x) for x in seq)


def chk(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   " + name + (("  (" + str(info) + ")") if info else ""))
    else:
        hong += 1
        print("  [HONG] " + name + (("  -> " + str(info)) if info else ""))


# ── Doc luat tu chinh ma nguon / tu dia, khong go cung con so ────────
DEF = (ROOT / "game-defender.html").read_text(encoding="utf-8")
BANK_N = len(list((ROOT / "js" / "quiz").glob("*.js")))
_fb = DEF.split("var QUIZ_FALLBACK=[")[1].split("\n  ];")[0]
FB_N = len(re.findall(r"\{\s*q:", _fb))


def game(pg, seed=None):
    """Vao mot luot choi. `seed` = noi dung gieo vao localStorage truoc khi choi."""
    pg.goto(BASE + "/game-defender.html", wait_until="load")
    pg.wait_for_selector("#start-btn", timeout=8000)
    pg.evaluate("() => localStorage.setItem('astroq-asteroids','999')")
    if seed:
        pg.evaluate("(v) => localStorage.setItem('astroq-defender-asked', v)",
                    json.dumps(seed))
    pg.reload(wait_until="load")
    pg.wait_for_selector("#start-btn", timeout=8000)
    pg.click("#start-btn")
    pg.wait_for_function("() => window.__dbg && __dbg.state === 'play'", timeout=8000)


def draw(pg, n):
    """Mo n cau do lien tiep (tra loi that de ve trang thai 'play')."""
    out = []
    for _ in range(n):
        pg.wait_for_function("() => __dbg.state === 'play'", timeout=8000)
        pg.evaluate("() => __dbg.openQuiz()")
        pg.wait_for_function("() => __dbg.quiz !== null && __dbg.state === 'quiz'",
                             timeout=8000)
        out.append(pg.evaluate("() => __dbg.quiz"))
        pg.click("#q-opts button >> nth=0")
        pg.wait_for_function("() => __dbg.state === 'play'", timeout=9000)
    return out


def newctx(br, lang="vi"):
    ctx = br.new_context(
        locale="vi-VN" if lang == "vi" else "en-US",
        timezone_id="Asia/Ho_Chi_Minh" if lang == "vi" else "America/New_York",
        viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('astroq-lang','" + lang + "');")
    return ctx


def main():
    print("kho tren dia: %d cau · duong lui: %d cau" % (BANK_N, FB_N))
    with sync_playwright() as p:
        br = p.chromium.launch()

        # ═════════════ [1] Kho chung THAT SU duoc dung ═════════════
        print("\n=== [1] CAU DO DEN TU KHO CHUNG (khong phai mang 8 cau) ===")
        ctx = newctx(br)
        pg = ctx.new_page()
        perr = []
        pg.on("pageerror", lambda e: perr.append(str(e)))
        game(pg)
        qs = draw(pg, 12)
        srcs = [q["from"] for q in qs]
        chk("12/12 cau den tu KHO CHUNG", srcs.count("bank") == 12,
            "bank=%d fallback=%d" % (srcs.count("bank"), srcs.count("fallback")))
        chk("moi cau co khoa `term` that", all(q["term"] for q in qs))
        chk("moi cau co dung 4 dap an", all(q["opts"] == 4 for q in qs))
        chk("chi so dap an dung nam trong 0..3", all(0 <= q["a"] <= 3 for q in qs))
        chk("0 loi trang", not perr, "; ".join(perr[:2]))

        # ═════════════ [2] Bo cau rong ra ngoai thien van ═════════════
        print("\n=== [2] BO CAU DA RONG RA NGOAI THIEN VAN ===")
        topics = sorted(set(q["topic"] for q in qs if q["topic"]))
        chk("nhieu linh vuc khac nhau trong 12 luot", len(topics) >= 5,
            "%d linh vuc: %s" % (len(topics), sj(topics[:8])))
        pg.evaluate("() => __dbg.openQuiz()")
        pg.wait_for_function("() => __dbg.quiz !== null", timeout=8000)
        tag = pg.inner_text("#q-tag")
        cur = pg.evaluate("() => __dbg.quiz")
        chk("nhan tren man hinh NOI TEN LINH VUC cua cau dang hoi",
            bool(cur["topic"]) and cur["topic"].casefold() in tag.casefold(),
            "nhan=%r topic=%r" % (tag, cur["topic"]))
        chk("nhan KHONG con la chuoi co dinh ASTRO_QUIZ",
            "astro_quiz" not in tag.casefold(), tag)
        pg.click("#q-opts button >> nth=0")
        pg.wait_for_function("() => __dbg.state === 'play'", timeout=9000)

        # ═════════════ [3] Khong lap trong cung mot luot ═════════════
        print("\n=== [3] KHONG HOI LAI CAU DA HOI — trong cung mot luot ===")
        terms = [q["term"] for q in qs] + [cur["term"]]
        chk("13 cau lien tiep, 0 cau bi hoi lai",
            len(set(terms)) == len(terms),
            "%d/%d duy nhat" % (len(set(terms)), len(terms)))
        asked = pg.evaluate("() => __dbg.quizAsked")
        chk("danh sach `da hoi` duoc ghi vao localStorage",
            len(asked) >= len(terms), "%d khoa" % len(asked))
        chk("moi cau da hien deu nam trong danh sach `da hoi`",
            all(t in asked for t in terms))
        allterms = pg.evaluate("() => AstroQQuestions.terms()")
        chk("kho chung khai dung so cau co tren dia",
            len(allterms) == BANK_N, "%d khoa / %d file" % (len(allterms), BANK_N))
        ctx.close()

        # ═════════════ [4] Khong lap QUA CAC LUOT ═════════════
        print("\n=== [4] KHONG HOI LAI CAU DA HOI — QUA CAC LUOT ===")
        ctx = newctx(br)
        pg = ctx.new_page()
        perr2 = []
        pg.on("pageerror", lambda e: perr2.append(str(e)))
        rest = allterms[BANK_N - 4:]
        game(pg, seed={"uid": "", "k": allterms[:BANK_N - 4]})
        left = draw(pg, 4)
        lterms = [q["term"] for q in left]
        chk("4 cau con lai deu la cau CHUA hoi",
            all(t not in allterms[:BANK_N - 4] for t in lterms), sj(lterms))
        chk("va chung dung la 4 khoa con lai cua kho",
            set(lterms) == set(rest), sj(sorted(lterms, key=str)))
        nxt = draw(pg, 1)[0]
        chk("het ca kho -> mo VONG MOI (van co cau, khong dung im)",
            nxt["from"] == "bank" and bool(nxt["term"]), nxt["term"])
        after = pg.evaluate("() => __dbg.quizAsked")
        chk("danh sach `da hoi` da duoc xoa de bat dau vong moi",
            len(after) <= 4, "%d khoa" % len(after))
        chk("0 loi trang", not perr2, "; ".join(perr2[:2]))
        ctx.close()

        # ═════════════ [5] Dong dau theo uid ═════════════
        print("\n=== [5] DANH SACH `da hoi` DONG DAU THEO uid ===")
        ctx = newctx(br)
        pg = ctx.new_page()
        pg.goto(BASE + "/game-defender.html", wait_until="load")
        pg.wait_for_selector("#start-btn", timeout=8000)
        pg.evaluate("""() => {
          localStorage.setItem('astroq-asteroids','999');
          localStorage.setItem('astroq-user', JSON.stringify({uid:'tre-B'}));
          localStorage.setItem('astroq-defender-asked',
            JSON.stringify({uid:'tre-A', k:['star','comet','meteor']}));
        }""")
        pg.reload(wait_until="load")
        pg.wait_for_selector("#start-btn", timeout=8000)
        pg.click("#start-btn")
        pg.wait_for_function("() => window.__dbg && __dbg.state === 'play'", timeout=8000)
        seen_other = pg.evaluate("() => __dbg.quizAsked")
        chk("dau cua tre KHAC uid bi bo qua", len(seen_other) == 0, seen_other)
        q1 = draw(pg, 1)[0]
        chk("nen tre nay VAN duoc hoi nhung cau do", bool(q1["term"]), q1["term"])
        ctx.close()

        # ═════════════ [6] Duong lui ═════════════
        print("\n=== [6] DUONG LUI: chan file cau -> VAN co cau do ===")
        ctx = newctx(br)
        # ⚠️ Tra 404 chu KHONG abort(): abort lam trinh duyet TU ghi mot dong do
        #    vao console, va phep kiem "0 loi trang" se bao oan.
        ctx.route(re.compile(r".*/js/quiz/.*\.js$"),
                  lambda r: r.fulfill(status=404, body=""))
        pg = ctx.new_page()
        perr3 = []
        pg.on("pageerror", lambda e: perr3.append(str(e)))
        game(pg)
        fqs = draw(pg, 3)
        chk("chan kho -> van mo duoc cau do (khong phai hop rong)",
            all(q["opts"] == 4 for q in fqs), [q["from"] for q in fqs])
        chk("va chung den tu DUONG LUI",
            all(q["from"] == "fallback" for q in fqs), [q["from"] for q in fqs])
        chk("duong lui khong lap trong mot vong",
            len(set(q["q"] for q in fqs)) == 3)
        chk("0 loi trang (chan kho)", not perr3, "; ".join(perr3[:2]))
        ctx.close()

        # ═════════════ [7] Ban EN ═════════════
        print("\n=== [7] BAN TIENG ANH ===")
        ctx = newctx(br, "en")
        pg = ctx.new_page()
        perr4 = []
        pg.on("pageerror", lambda e: perr4.append(str(e)))
        game(pg)
        pg.evaluate("() => __dbg.openQuiz()")
        pg.wait_for_function("() => __dbg.quiz !== null", timeout=8000)
        shown = {"tag": pg.inner_text("#q-tag"), "q": pg.inner_text("#q-text")}
        raw = pg.evaluate("() => __dbg.quiz")
        chk("cau hoi hien ban EN (khac ban VI)",
            bool(shown["q"]) and shown["q"] != raw["q"], shown["q"][:48])
        chk("nhan linh vuc cung dich sang EN",
            bool(shown["tag"]) and raw["topic"].casefold() not in shown["tag"].casefold(),
            "%r vs vi=%r" % (shown["tag"], raw["topic"]))
        chk("0 loi trang (EN)", not perr4, "; ".join(perr4[:2]))
        ctx.close()

        br.close()

    print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
    sys.exit(1 if hong else 0)


if __name__ == "__main__":
    main()
