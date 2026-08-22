# -*- coding: utf-8 -*-
"""check_constellation.py — kiem TINH cho `game-constellation.html` (ARCADE-04).

⚠️ DUNG LAI 22/08/2026. Ban goc (nhat ky 28/07/2026 ghi 56/56) **khong con tren
   may** — cung canh `gen_wiki_data*.py` va `play_constellation.py`: script kiem
   thu chi nam o may thi mat la mat. Tu 28/07 den 22/08 game nay la game DUY
   NHAT trong 10 game khong co bo do nao gac, va chinh trong quang do no da
   mang mot loi that: man brief hua mot chom sao roi vao luot lai ra chom khac
   (3/4 luot lech).

Bo nay do THU MA `play_constellation.py` (choi that) khong hoi duoc:
  · cau truc du lieu `SKY` — them mot chom sao la phai dung khuon
  · rang buoc HINH HOC: moi cap sao phai cach nhau > `hitR` x 2, khong thi bam
    vao mot ngoi sao lai trung ngoi sao ben canh
  · i18n khop vi/en, `$("id")` co that, class co CSS — hai chieu
  · man brief phai giu loi hua (`briefKey`), va ky luc phai di qua
    `js/constellations.js` chu khong `JSON.parse` tai cho

  python scratchpad/check_constellation.py        # khong can may chu, khong can mang
"""
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = io.open(os.path.join(ROOT, "game-constellation.html"), encoding="utf-8").read()
CSS_FILES = ["css/common.css", "css/game-shell.css", "css/game-constellation.css"]
CSS = "\n".join(io.open(os.path.join(ROOT, f), encoding="utf-8").read()
                for f in CSS_FILES)

dat = 0
hong = 0


def chk(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   " + name + (("  (" + str(info) + ")") if info else ""))
    else:
        hong += 1
        print("  [HONG] " + name + (("  -> " + str(info)) if info else ""))


def strip_js(s):
    """Bo comment (giu chuoi) — moi phep kiem dang "khong duoc chua X" phai chay
    tren ban da boc comment, khong thi chinh GHI CHU giai thich "vi sao khong
    dung X" bi tinh la vi pham. Loi nay da lap ~19 lan trong du an."""
    out = []
    i, n = 0, len(s)
    q = None
    while i < n:
        c = s[i]
        if q:
            out.append(c)
            if c == "\\":
                if i + 1 < n:
                    out.append(s[i + 1])
                i += 2
                continue
            if c == q:
                q = None
            i += 1
            continue
        if c in "\"'`":
            q = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "*":
            j = s.find("*/", i + 2)
            i = (j + 2) if j >= 0 else n
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "/":
            j = s.find("\n", i)
            i = (j) if j >= 0 else n
            continue
        out.append(c)
        i += 1
    return "".join(out)


CLEAN = strip_js(HTML)


def script_body():
    m = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", HTML, re.S)
    return "\n".join(m)


JS = strip_js(script_body())


# ══════════════════════════════════════════════════════════════════════════════
def parse_sky():
    """Doc mang `SKY` — id/toa do tung ngoi sao, ten song ngu, cau `fact`.

    ⚠️ Doc bang regex chu KHONG bang cach chay JS: bo nay co y KHONG can trinh
       duyet (chay duoc ca khi khong co Playwright). Bu lai no phai tu bao khi
       doc ra 0 chom sao — mot bo phan tich doc ra rong thi moi phep kiem sau do
       "dat" mot cach RONG (bai hoc `check_codex.py` 30/07).
    """
    m = re.search(r"var SKY\s*=\s*\[(.*?)\n  \];", HTML, re.S)
    if not m:
        return []
    body = m.group(1)
    out = []
    for blk in re.findall(r"\{\s*\n\s*key:(.*?)(?=\n    \},|\n    \}\s*$)", body, re.S):
        key = re.search(r'\s*"([a-z0-9-]+)"', blk)
        stars = [(int(a), int(b), int(c)) for a, b, c in
                 re.findall(r"\{id:\s*(\d+),\s*x:\s*(\d+),\s*y:\s*(\d+)", blk)]
        out.append({
            "key": key.group(1) if key else None,
            "stars": stars,
            "has_vi_name": bool(re.search(r'name:\s*\{\s*vi:\s*"', blk)),
            "has_en_name": bool(re.search(r'en:\s*"', blk)),
            "has_sketch": "sketch:" in blk,
            "has_fact": "fact:" in blk,
            "blk": blk,
        })
    return out


def num(pat, src=HTML, cast=int):
    m = re.search(pat, src)
    return cast(m.group(1)) if m else None


def main():
    print("=== [1] DU LIEU CHOM SAO: cau truc ===")
    SKY = parse_sky()
    chk("doc duoc mang SKY", len(SKY) >= 1, "%d chom sao" % len(SKY))
    if not SKY:
        print("!! khong doc duoc chom sao nao — DUNG, khong de cac phep kiem sau"
              " 'dat' mot cach rong")
        sys.exit(1)

    # So chom sao khai o `SKY` phai bang so chom khai o js/constellations.js —
    # do la khoa dung o CA `PROGRESS.consts` tren server, `astroq-constellation-
    # best` trong may, va dieu kien `const:<key>` cua Specimens.cs.
    CONS = io.open(os.path.join(ROOT, "js", "constellations.js"),
                   encoding="utf-8").read()
    keys_cons = set(re.findall(r'key:\s*"([a-z0-9-]+)"', CONS))
    keys_sky = {c["key"] for c in SKY}
    chk("moi chom sao trong SKY co ten o js/constellations.js",
        keys_sky <= keys_cons, "thieu: %s" % sorted(keys_sky - keys_cons))
    chk("khong co ten chom sao mo coi o js/constellations.js",
        keys_cons <= keys_sky, "mo coi: %s" % sorted(keys_cons - keys_sky))

    for c in SKY:
        k = c["key"]
        chk("%s: khai du ten vi+en" % k, c["has_vi_name"] and c["has_en_name"])
        chk("%s: co sketch + fact" % k, c["has_sketch"] and c["has_fact"])
        ids = [s[0] for s in c["stars"]]
        chk("%s: id sao chay 1..n lien tuc" % k,
            ids == list(range(1, len(ids) + 1)), str(ids))

    print("\n=== [2] RANG BUOC HINH HOC (dieu kien de bam dung ngoi sao) ===")
    VW = num(r"VW:\s*(\d+)")
    VH = num(r"VH:\s*(\d+)")
    hitR = num(r"hitR:\s*(\d+)")
    chk("doc duoc VW/VH/hitR tu CONFIG", None not in (VW, VH, hitR),
        "%sx%s hitR=%s" % (VW, VH, hitR))

    for c in SKY:
        k = c["key"]
        out = [(i, x, y) for i, x, y in c["stars"]
               if not (0 <= x <= VW and 0 <= y <= VH)]
        chk("%s: moi ngoi sao nam trong san" % k, not out, str(out))
        # ⚠️ Moi CAP sao phai cach nhau > hitR (ban kinh bam). Gan hon thi mot cu
        #    bam vao ngoi sao A cung nam trong ban kinh cua B, va `pick()` chon
        #    theo khoang cach nen tre bam dung sao van co the noi sai cap.
        worst = None
        for i in range(len(c["stars"])):
            for j in range(i + 1, len(c["stars"])):
                _, x1, y1 = c["stars"][i]
                _, x2, y2 = c["stars"][j]
                d = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                if worst is None or d < worst[0]:
                    worst = (d, c["stars"][i][0], c["stars"][j][0])
        chk("%s: cap sao gan nhat cach > hitR (%s)" % (k, hitR),
            worst is not None and worst[0] > hitR,
            "sao %s-%s cach %.1f" % (worst[1], worst[2], worst[0]) if worst else "")

    print("\n=== [3] MAN BRIEF LA MOT LOI HUA ===")
    # Loi that 22/08/2026: man brief boc mot chom lam hinh nen VA dat ten no len
    # chip HUD, roi `startRound()` boc mot chom KHAC — do duoc 3/4 luot lech.
    chk("co bien briefKey", "briefKey" in JS)
    chk("startRound giu chom cua man brief",
        re.search(r"briefKey\s*&&\s*cons\s*&&\s*cons\.key\s*===\s*briefKey", JS)
        is not None,
        "phai kiem cons.key === briefKey truoc khi boc chom moi")
    chk("xong luot thi briefKey ve null (\"Choi lai\" van ra chom KHAC)",
        re.search(r"briefKey\s*=\s*null", JS) is not None)

    print("\n=== [4] KY LUC DI QUA js/constellations.js ===")
    # Ba trang doc cung mot ham thay vi ba ban `JSON.parse` rieng, va ban ghi co
    # dong dau `uid` — xem js/constellations.js.
    chk("nap js/constellations.js",
        re.search(r'<script src="js/constellations\.js"></script>', HTML) is not None)
    chk("doc ky luc qua AstroQConsts.localBests()",
        "AstroQConsts.localBests()" in JS)
    chk("ghi ky luc qua AstroQConsts.saveLocalBest()",
        "AstroQConsts.saveLocalBest(" in JS)
    chk("KHONG con JSON.parse khoa ky luc tai cho",
        "astroq-constellation-best" not in JS,
        "khoa nay chi duoc xuat hien o js/constellations.js")

    print("\n=== [5] i18n: moi khoa co o CA vi va en ===")
    # ⚠️ TU DIEN KHAI NHIEU KHOA TREN MOT DONG (`title:"…", back:"…"`), nen
    #    quet theo DONG la bo sot: ban dau cua bo nay doc ra 21 khoa trong
    #    khi that su co 33. Lap lai dung loi da ghi 07/08/2026 ("parser tu
    #    dien quet theo dong -> bo sot 11 khoa khai chung dong").
    dicts = {}
    m_all = re.search(r"var I18N\s*=\s*\{(.*?)\n  \};", JS, re.S)
    blob = m_all.group(1) if m_all else ""
    parts = re.split(r"\n\s{4}(vi|en):\s*\{", blob)
    for i in range(1, len(parts) - 1, 2):
        lang, body = parts[i], parts[i + 1]
        dicts[lang] = set(re.findall(r'(?:^|[{,\s])([a-z0-9_]+)\s*:\s*"', body))
    dicts.setdefault("vi", set())
    dicts.setdefault("en", set())
    chk("doc duoc ca hai tu dien", bool(dicts["vi"]) and bool(dicts["en"]),
        "vi=%d en=%d" % (len(dicts["vi"]), len(dicts["en"])))
    if dicts["vi"] and dicts["en"]:
        chk("vi va en cung tap khoa", dicts["vi"] == dicts["en"],
            "chi vi: %s · chi en: %s" % (sorted(dicts["vi"] - dicts["en"]),
                                         sorted(dicts["en"] - dicts["vi"])))
        # ⚠️ NEO TRUOC `t(`: khong neo thi `getContext("2d")` cung khop (phan
        #    cuoi `getContex` + `t(`) va bo do bao thieu mot khoa ten "2d".
        #    Lop loi "khop CHU thay vi khop HINH DANG cua code".
        used = set(re.findall(r'(?<![A-Za-z0-9_$.])t\("([a-z0-9_]+)"\)', JS))
        used |= set(re.findall(r'data-i18n(?:-html|-title|-aria|-alt|-ph)?="([a-z0-9_]+)"',
                              HTML))
        chk("moi khoa dung deu duoc khai", used <= dicts["vi"],
            "thieu: %s" % sorted(used - dicts["vi"]))

    print("\n=== [6] $(\"id\") va class ===")
    ids_html = set(re.findall(r'id="([A-Za-z0-9_-]+)"', HTML))
    ids_js = set(re.findall(r'\$\("([A-Za-z0-9_-]+)"\)', JS))
    chk("moi $(\"id\") deu co phan tu", ids_js <= ids_html,
        "thieu: %s" % sorted(ids_js - ids_html))

    cls_html = set()
    for v in re.findall(r'class="([^"]+)"', HTML):
        cls_html |= set(v.split())
    for v in re.findall(r'classList\.(?:add|remove|toggle)\("([A-Za-z0-9_-]+)"', JS):
        cls_html.add(v)
    cls_css = set(re.findall(r"\.([a-z][a-z0-9-]+)", CSS))
    own = {c for c in cls_html if c.startswith("cx-") or c.startswith("cons")}
    chk("class rieng cua game deu co CSS", own <= cls_css,
        "thieu CSS: %s" % sorted(own - cls_css))

    print("\n=== [7] KHONG BIA SO, KHONG TU QUYET THUONG ===")
    chk("thuong tinh bang cong thuc, khong Math.random",
        not re.search(r"reward\s*=[^;]*Math\.random", JS),
        "phan thuong phai giai thich duoc cho tre")
    chk("bao tien do qua AstroQProgress.game",
        "AstroQProgress.game(" in JS)
    chk("tru phi qua Economy.spend", "Economy.spend(" in JS)

    print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
    sys.exit(1 if hong else 0)


if __name__ == "__main__":
    main()
