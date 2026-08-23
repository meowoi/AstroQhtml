# -*- coding: utf-8 -*-
"""Do tren BAN THAT (astroq.org) rang dot noi dung AI/chatbot 23/08 len duoc that.

⚠️ DO SO BAN DUNG TRUOC MOI THU KHAC. Neu Pages con dung ban cu thi moi phep
   kiem phia sau deu do BAN CU — no se bao xanh cho mot thu chua len, va do la
   kieu bao xanh oan te nhat.

⚠️ 31 FILE MOI DEU LA ES MODULE nap DONG. `js/quiz/*.js` va `js/article/*.js`
   khong duoc trang nao tham chieu tinh, nen mot file thieu KHONG lam trang do
   — no chi lam mot the So Tay mo ra rong. Vi vay phai do CA HAI tang:
     ① tang mang: file tra 200 + MIME la javascript (GitHub Pages tra
        `text/plain` cho duoi la thi `import` bi tu choi im lang)
     ② tang trang: mo the ra, cau hien ra that
"""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "https://astroq.org"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
dat = hong = 0


def check(label, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s  %s" % (label, info))
    else:
        hong += 1
        print("  [HONG] %s  %s" % (label, info))


def get(path):
    """Tra (ma, mime, noi dung). Cache-buster de khong doc ban CDN cu."""
    req = urllib.request.Request(BASE + path + "?cb=0823x", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", 0), "", ""


# ═══════════ [0] SO BAN DUNG — do TRUOC moi thu khac ═══════════
print("=== [0] So ban dung (do TRUOC moi thu khac) ===")
st, _, ui = get("/js/ui-common.js")
check("js/ui-common.js tra 200", st == 200, "ma %s" % st)
check("ban tren mang LA 2026.08.23.9 (khong phai ban cu)",
      "2026.08.23.9" in ui,
      re.search(r"2026\.\d\d\.\d\d\.\d+", ui).group(0) if re.search(r"2026\.\d\d\.\d\d\.\d+", ui) else "khong thay so nao")
if "2026.08.23.9" not in ui:
    print("\n!!! DUNG SOM: Pages con dung ban cu. Moi phep kiem phia sau se do BAN CU.")
    sys.exit(1)

# ═══════════ [1] 31 file moi: 200 + MIME javascript ═══════════
print("\n=== [1] File moi tra 200 va MIME la javascript ===")
MOI_QUIZ = ["chatbot-does-not-remember", "chatbot-confidently-wrong", "llm-not-fully-understood",
            "ai-perceives-with-sensors", "ai-see-hear-achievement", "ai-training-data-from-people",
            "ai-does-not-think-like-human", "ai-language-limited",
            "ai-already-around-you", "ai-binary-stars", "ai-counts-tarps", "ai-maps-dark-craters",
            "ai-metadata-eases-load", "ai-surya-two-hours", "canadarm2-two-hands",
            "curiosity-mission-goal", "dsn-three-stations", "dsn-why-big-antennas",
            "ingenuity-first-flight", "opportunity-distance", "quantum-superposition",
            "qubit-superposition", "robonaut-first-humanoid", "robots-free-crew-time",
            "sojourner-first-rover", "supercomputer-galaxy-vr", "supercomputer-year-long-run",
            "voyager-weak-signal"]
MOI_BAI = ["art-chatbot-does-not-remember", "art-chatbot-confidently-wrong",
           "art-nobody-fully-understands-llm"]

_xau = []
for t in MOI_QUIZ:
    st, mime, body = get("/js/quiz/%s.js" % t)
    if st != 200 or "javascript" not in mime or "export default" not in body:
        _xau.append("%s(%s,%s)" % (t, st, mime.split(";")[0]))
check("28 file cau moi: 200 + MIME javascript + co `export default`",
      not _xau, "%d/28 dat%s" % (28 - len(_xau), "" if not _xau else " · xau: " + ", ".join(_xau[:3])))

_xau = []
for a in MOI_BAI:
    st, mime, body = get("/js/article/%s.js" % a)
    if st != 200 or "javascript" not in mime or "export default" not in body:
        _xau.append("%s(%s,%s)" % (a, st, mime.split(";")[0]))
check("3 file bai doc moi: 200 + MIME javascript",
      not _xau, "%d/3 dat%s" % (3 - len(_xau), "" if not _xau else " · xau: " + ", ".join(_xau)))

# ═══════════ [2] muc luc + bang nguon + the + icon tren ban that ═══════════
print("\n=== [2] Muc luc / nguon / the / icon tren ban that ===")
st, _, qidx = get("/js/quiz-index.js")
check("js/quiz-index.js tra 200", st == 200, "ma %s" % st)
thieu = [t for t in MOI_QUIZ if '"%s"' % t not in qidx and "'%s'" % t not in qidx]
check("28 slug cau moi deu co trong muc luc", not thieu, "thieu: %s" % thieu[:3])

st, _, aidx = get("/js/articles-index.js")
thieu = [a for a in MOI_BAI if a not in aidx]
check("3 bai moi deu co trong muc luc bai doc", not thieu, "thieu: %s" % thieu)

st, _, srcs = get("/js/quiz-sources.js")
check("js/quiz-sources.js co 3 khoa nguon MIT moi",
      all(k in srcs for k in ("mitLlmMemory", "mitLlmConfident", "mitLlmMechanism")))

st, _, codex = get("/js/codex-terms.js")
check("js/codex-terms.js co the `term_chatbot`", "term_chatbot" in codex)
# ⚠️ Bang SRC cua codex-terms LA BAN THU HAI — bo qua thi `src` cua the ra
#    `[undefined]`: khong loi, khong canh bao, chi la the mat dong nguon.
check("bang SRC ben trong codex-terms.js CUNG co 3 khoa MIT (ban thu hai)",
      all(k in codex for k in ("mitLlmMemory", "mitLlmConfident", "mitLlmMechanism")))

st, _, ic = get("/js/icons.js")
check("js/icons.js co icon `cx-chatbot`", "cx-chatbot" in ic)

# ═══════════ [3] tang trang: mo the ra, cau hien ra that ═══════════
print("\n=== [3] Tang trang: the So Tay va cau hien ra that ===")
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi')")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

    pg.goto(BASE + "/codex.html", wait_until="load", timeout=60000)
    pg.wait_for_timeout(4000)
    check("codex.html: 0 loi trang", not errs, str(errs[:2]))

    # ⚠️ SELECTOR THAT la `.cx-item[data-id]` trong `#grid`; `.cx-card` chi la MOT
    #    khung boc duy nhat, va khong co thuoc tinh `data-term` nao — ban dau toi
    #    do `.cx-card, [data-term]` va no dem ra 1, tuc bao HONG OAN cho mot the
    #    ve ra dung. Doc `codex.html:230` moi ra ten that.
    n = pg.evaluate("document.querySelectorAll('#grid .cx-item[data-id]').length")
    check("codex.html ve ra >= 26 the", n >= 26, "%d the" % n)

    # Icon nam NGAY TRONG the o luoi (`<span class="cx-i-ic">`+lic(x.ic)+...),
    # khong phai chi trong hop thoai — nen do duoc ma khong can mo the.
    co_svg = pg.evaluate(
        "!!document.querySelector('#grid .cx-item[data-id=\"term_chatbot\"] "
        ".cx-i-ic svg')")
    check("the term_chatbot co icon SVG ve ra trong luoi", co_svg)

    # ⚠️ Do CAU HIEN RA, khong do `terms` khai gi — mot slug sai chinh ta trong
    #    `terms` van khai dung y do ma mo ra bang trang.
    pg.goto(BASE + "/quiz.html?terms=chatbot-does-not-remember,chatbot-confidently-wrong,"
            "llm-not-fully-understood", wait_until="load", timeout=60000)
    pg.wait_for_timeout(5000)
    txt = pg.inner_text("body")
    check("quiz.html?terms=3 cau chatbot: 0 loi trang", not errs, str(errs[:2]))
    check("cau hien ra co chu ve chatbot/AI", len(txt.strip()) > 80, "%d ky tu" % len(txt.strip()))
    n_opt = pg.evaluate("document.querySelectorAll('.opt, [data-opt], button.answer').length")
    check("ve ra 4 dap an", n_opt >= 4, "%d o" % n_opt)

    # bai doc moi mo duoc
    pg.goto(BASE + "/library.html?a=art-chatbot-does-not-remember",
            wait_until="load", timeout=60000)
    pg.wait_for_timeout(4000)
    t2 = pg.inner_text("body")
    check("library.html mo bai art-chatbot-does-not-remember", len(t2.strip()) > 200,
          "%d ky tu" % len(t2.strip()))
    br.close()

print("\n=== %d dat / %d hong ===" % (dat, hong))
sys.exit(1 if hong else 0)
