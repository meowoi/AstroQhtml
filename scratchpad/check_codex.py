# -*- coding: utf-8 -*-
"""
check_codex.py — soi TĨNH bộ Astronaut Codex ở `../react/astronaut-codex/`.

VÌ SAO CẦN SCRIPT NÀY: repo không có `package.json`/`tsconfig.json`/`node_modules`
và máy không có Node, nên `tsc` KHÔNG chạy được — mọi thứ `satisfies` /
`Record<TermIconKey, …>` đáng lẽ bắt lúc biên dịch thì ở đây không ai bắt. Script
này làm thay đúng những phép kiểm đó, cộng thêm phép kiểm mà TypeScript KHÔNG
làm được: đối chiếu `quizBankTerms` với `term` thật trong js/quiz-questions.js.

    cd AstroQhtml
    set PYTHONIOENCODING=utf-8 & python scratchpad/check_codex.py

⚠️ Nhãn của check() PHẢI KHÔNG DẤU (console Windows cp1252 -> UnicodeEncodeError
   ném giữa lúc chạy và bỏ dở mọi phép kiểm phía sau).
"""
import io
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))            # AstroQhtml/
CODEX = os.path.abspath(os.path.join(ROOT, "..", "react", "astronaut-codex"))
LIB = os.path.abspath(os.path.join(ROOT, "..", "react", "astronomy-library"))
OFFLINE = "--offline" in sys.argv

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def rd(path):
    return io.open(path, encoding="utf-8").read()


def strip_block_comments(s):
    """Bỏ /* … */ để không đếm chữ trong ghi chú (vd ví dụ đã comment)."""
    return re.sub(r"/\*.*?\*/", " ", s, flags=re.S)


def code_only(s):
    """
    Bỏ MỌI ghi chú (khối + dòng + JSX `{/* */}`) rồi mới đi tìm.
    ⚠️ Bắt buộc cho các phép kiểm dạng "không được dùng X": ba ghi chú trong bộ
    này GIẢI THÍCH vì sao không dùng `dangerouslySetInnerHTML`, `grayscale`,
    `auto-fill minmax` — tìm trên văn bản thô thì chính lời cảnh báo bị tính là
    vi phạm, và phép kiểm báo hỏng đúng vào code đang làm đúng.
    """
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"^\s*//[^\n]*", " ", s, flags=re.M)
    return s


# ══════════════════════════════════════════════════════════════
print("=== [1] File du + doc duoc ===")
FILES = [
    "termsData.ts",
    "useTermStore.ts",
    "TermIcons.tsx",
    "TermIllustration.tsx",
    "TermCard.tsx",
    "TermCodexModal.tsx",
    "AstronautCodex.tsx",
    "AstronautCodex.astro",
    "astronaut-codex.css",
    "index.ts",
]
src = {}
for f in FILES:
    p = os.path.join(CODEX, f)
    exists = os.path.exists(p)
    check(f"co file {f}", exists)
    if exists:
        src[f] = rd(p)
if len(src) != len(FILES):
    print("\nDung som: thieu file.")
    sys.exit(1)

data_ts = src["termsData.ts"]
data_clean = strip_block_comments(data_ts)

# ══════════════════════════════════════════════════════════════
print("\n=== [2] Ngoac can o moi file ===")


def brace_errors(s):
    """
    Quét từng ký tự, có hiểu chuỗi/ký tự thoát/comment, và kiểm ĐÚNG CẶP
    (`{` không được đóng bằng `)`).

    ⚠️ BẢN ĐẦU CHỈ ĐẾM `s.count("{") == s.count("}")` SAU KHI XOÁ CHUỖI BẰNG
    REGEX, VÀ NÓ BÁO HỎNG OAN `termsData.ts` (36 mở / 34 đóng) trong khi file
    hoàn toàn cân. Lý do: regex xoá chuỗi một-dòng ghép cặp sai khi gặp nhiều
    chuỗi nối bằng `+` trên các dòng liền nhau, và việc thu khối comment nhiều
    dòng về một khoảng trắng làm số dòng báo ra vô nghĩa. Đếm thì nhanh, nhưng
    một phép kiểm hay báo oan thì người ta sẽ bỏ qua nó — tức là mất luôn.
    """
    BS, NL = chr(92), chr(10)
    pairs = {"{": "}", "(": ")", "[": "]"}
    closers = set(pairs.values())
    out, stack, i, n, line = [], [], 0, len(s), 1
    while i < n:
        c = s[i]
        if c == NL:
            line += 1
            i += 1
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "*":
            j = s.find("*/", i + 2)
            line += s.count(NL, i, j if j > 0 else n)
            i = (j + 2) if j > 0 else n
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "/":
            j = s.find(NL, i)
            i = j if j > 0 else n
            continue
        if c in ('"', "'", "`"):
            q = c
            i += 1
            while i < n and s[i] != q:
                if s[i] == BS:
                    i += 1
                elif s[i] == NL:
                    line += 1
                i += 1
            i += 1
            continue
        if c in pairs:
            stack.append((c, line))
        elif c in closers:
            if not stack:
                out.append(f"dong thua '{c}' dong {line}")
            else:
                op, ln = stack.pop()
                if pairs[op] != c:
                    out.append(f"'{op}' dong {ln} bi dong bang '{c}' dong {line}")
        i += 1
    out += [f"chua dong '{op}' mo o dong {ln}" for op, ln in stack]
    return out


for f, s in src.items():
    if f.endswith(".astro"):
        continue
    errs = brace_errors(s)
    check(f"{f}: ngoac can va dung cap", not errs, "; ".join(errs[:3]))

# ══════════════════════════════════════════════════════════════
print("\n=== [3] TermIconKey <-> TERM_ICONS (thay cho `satisfies`) ===")
m = re.search(r"export type TermIconKey =(.*?);", data_clean, re.S)
check("doc duoc union TermIconKey", bool(m))
declared_keys = set(re.findall(r"'([^']+)'", m.group(1))) if m else set()

icons_ts = strip_block_comments(src["TermIcons.tsx"])
m2 = re.search(r"export const TERM_ICONS = \{(.*?)\} satisfies", icons_ts, re.S)
check("TERM_ICONS co menh de `satisfies Record<TermIconKey, …>`", bool(m2))
registry_keys = set()
if m2:
    for line in m2.group(1).splitlines():
        km = re.match(r"\s*'?([A-Za-z0-9-]+)'?\s*:", line)
        if km:
            registry_keys.add(km.group(1))

check("moi khoa trong TermIconKey deu co ban ve", declared_keys <= registry_keys,
      f"thieu ban ve: {sorted(declared_keys - registry_keys)}")
check("TERM_ICONS khong ve thua khoa la", registry_keys <= declared_keys,
      f"khoa la: {sorted(registry_keys - declared_keys)}")
# ⚠️ KHONG GAN CUNG SO ICON. Truoc day cho nay doi dung 14, va them 5 icon cho
#    Thu vien Thien van la no bao hong trong khi khong co gi sai. Cung bai hoc da
#    ghi trong CLAUDE.md voi `smoke_vault.py` ("20 mau vat" gan cung 8 cho):
#    phep kiem phai hoi DIEU MINH MUON BIET. Dieu muon biet o day la "hai ben khop
#    nhau" (da co 2 phep kiem tren) va "khong bi xoa bot", nen chi can mot san.
check("co it nhat 14 icon (bo goc khong bi xoa bot)", len(declared_keys) >= 14,
      f"{len(declared_keys)}")

# Mỗi icon phải thật sự là một component có <svg>
n_svg = len(re.findall(r": TermIconComponent = \(\{ className \}\) => \(", icons_ts))
check("moi icon la mot TermIconComponent", n_svg == len(registry_keys),
      f"{n_svg}/{len(registry_keys)}")
check("moi icon dung currentColor (doi mau bang class ben ngoai)",
      "stroke: 'currentColor'" in icons_ts)
check("khong dung dangerouslySetInnerHTML o bat ky file nao",
      not any("dangerouslySetInnerHTML" in code_only(s) for s in src.values()))

# ══════════════════════════════════════════════════════════════
print("\n=== [4] Cau truc tung thuat ngu ===")
# Khối thuật ngữ thụt 2 space (`  {`), trường thụt 4 space (`    id:`).
blocks = re.split(r"\n\s{2}\{\s*\n(?=\s{4}id:)", "\n" + data_clean)
terms = []
for b in blocks[1:]:
    def one(field):
        mm = re.search(rf"\b{field}:\s*'((?:[^'\\]|\\.)*)'", b)
        return mm.group(1) if mm else None

    def arr(field):
        mm = re.search(rf"\b{field}:\s*\[(.*?)\]", b, re.S)
        if not mm:
            return None
        return re.findall(r"'((?:[^'\\]|\\.)*)'", mm.group(1))

    tid = one("id")
    if not tid:
        continue
    terms.append({
        "id": tid,
        "title": one("title"),
        "titleEn": one("titleEn"),
        "analogy": one("analogy"),
        "category": one("category"),
        "summary": one("summary"),
        "requiredQuizId": one("requiredQuizId"),
        "iconSvg": one("iconSvg"),
        "diagram": arr("diagram"),
        "quizBankTerms": arr("quizBankTerms"),
        "has_description": bool(re.search(r"\bdescription:\s*\n?\s*'", b)),
        "has_grounded": bool(re.search(r"\bgrounded:\s*\n?\s*'", b)),
        "has_source": "sources: [NASA." in b,
        "reviewed": "reviewed: true" in b,
        "has_illustration": bool(re.search(r"^\s{4}illustration:", b, re.M)),
    })

# ⚠️ HOI DUNG CAU: "bo phan tich co doc DU so thuat ngu KHAI TRONG FILE khong?"
#    chu khong phai "co dung 14 thuat ngu khong?". So 14 gan cung o day tung lam
#    bo kiem bao hong khi them 5 thuat ngu moi — trong khi loi that ma phep kiem
#    nay sinh ra de bat la "regex tach khoi bi lech thut le nen doc ra 0 thuat ngu
#    va 8 phep kiem sau do DAT MOT CACH RONG" (da xay ra, ghi trong CLAUDE.md).
declared_ids = re.findall(r"^\s{4}id: '([a-z_0-9]+)'", data_clean, re.M)
check("doc duoc DU so thuat ngu khai trong TERMS",
      len(terms) == len(declared_ids), f"doc {len(terms)} / khai {len(declared_ids)}")
check("co it nhat 14 thuat ngu (bo goc khong bi xoa bot)", len(terms) >= 14, f"{len(terms)}")

# ⚠️ Doc khong ra thi DUNG NGAY. Khong dung thi moi phep kiem duoi day chay tren
# danh sach rong va DAT HET — dat mot cach rong con te hon bao hong, vi no bao
# rang du lieu da duoc kiem trong khi khong cai nao duoc so.
if len(terms) == 0 or len(terms) != len(declared_ids):
    print("\nDung som: bo phan tich khong doc ra du thuat ngu, moi phep kiem "
          "sau day se dat mot cach VO NGHIA.")
    sys.exit(1)

missing = []
for t in terms:
    for f in ("title", "titleEn", "analogy", "category", "summary", "requiredQuizId", "iconSvg"):
        if not t[f]:
            missing.append(f"{t['id']}.{f}")
    if not t["has_description"]:
        missing.append(f"{t['id']}.description")
    if not t["has_grounded"]:
        missing.append(f"{t['id']}.grounded")
    if not t["diagram"]:
        missing.append(f"{t['id']}.diagram")
    if t["quizBankTerms"] is None:
        missing.append(f"{t['id']}.quizBankTerms")
check("moi thuat ngu du truong bat buoc", not missing, f"thieu: {missing[:6]}")

ids = [t["id"] for t in terms]
check("id khong trung nhau", len(set(ids)) == len(ids),
      f"trung: {sorted({i for i in ids if ids.count(i) > 1})}")
check("moi id theo dung khuon `term_<slug>`",
      all(re.fullmatch(r"term_[a-z0-9_]+", i) for i in ids),
      f"sai khuon: {[i for i in ids if not re.fullmatch(r'term_[a-z0-9_]+', i)]}")

quiz_ids = [t["requiredQuizId"] for t in terms]
check("moi requiredQuizId theo khuon `quiz_<slug>_nn`",
      all(re.fullmatch(r"quiz_[a-z0-9_]+_\d+", q) for q in quiz_ids),
      f"sai khuon: {[q for q in quiz_ids if not re.fullmatch(r'quiz_[a-z0-9_]+_[0-9]+', q)]}")

bad_icon = [t["id"] for t in terms if t["iconSvg"] not in declared_keys]
check("moi iconSvg tro vao mot khoa co that", not bad_icon, f"{bad_icon}")

bad_cat = [t["id"] for t in terms if t["category"] not in {"space", "ai", "quantum"}]
check("moi category thuoc space/ai/quantum", not bad_cat, f"{bad_cat}")

# summary hiện trên thẻ ở lưới 2 cột trên điện thoại → dài là tràn
too_long = [(t["id"], len(t["summary"])) for t in terms if len(t["summary"]) > 90]
check("summary <= 90 ky tu (khong tran the o luoi)", not too_long, f"{too_long}")

few_diag = [t["id"] for t in terms if len(t["diagram"]) < 2 or len(t["diagram"]) > 3]
check("diagram co 2-3 nhan chu thich", not few_diag, f"{few_diag}")

# ══════════════════════════════════════════════════════════════
print("\n=== [5] Nguon + co ra soat (khong nhan bua la da kiem) ===")
reviewed = [t for t in terms if t["reviewed"]]
draft = [t for t in terms if not t["reviewed"]]
# Dieu muon biet: "moi thuat ngu da danh dau da ra soat thi phai thuoc nhom space"
# (nhom ai/quantum van la ban nhap). KHONG gan cung so 10 — them thuat ngu space
# moi la con so doi, ma khong co gi sai.
check("moi thuat ngu reviewed:true deu thuoc nhom space",
      len(reviewed) > 0 and all(t["category"] == "space" for t in reviewed),
      f"{len(reviewed)} thuat ngu")
check("moi thuat ngu reviewed:true deu CO source",
      all(t["has_source"] for t in reviewed),
      f"thieu source: {[t['id'] for t in reviewed if not t['has_source']]}")
check("moi thuat ngu reviewed:false deu KHONG gan source (khong nhan bua)",
      all(not t["has_source"] for t in draft),
      f"gan sai: {[t['id'] for t in draft if t['has_source']]}")
check("4 thuat ngu nhap thuoc ai/quantum",
      len(draft) == 4 and all(t["category"] in {"ai", "quantum"} for t in draft),
      f"{[t['id'] for t in draft]}")

urls = set(re.findall(r"url: '([^']+)'", data_clean))
# ⚠️ DA NOI RONG TU `science.nasa.gov` SANG "ten mien CUA NASA" (30/07/2026), va
#    chi noi rong DUNG hai ten mien duoi day — khong phai mo cho moi URL.
#    Ly do: thuat ngu `term_gravity` dan **NASA Space Place**
#    (`spaceplace.nasa.gov/what-is-gravity/en/`), la trang NASA viet CHO TRE EM —
#    dung do tuoi 8–15 cua app — va `science.nasa.gov` khong co trang dinh nghia
#    hap dan tuong duong. Van la NASA, van la nguon chinh thuc.
NASA_HOSTS = ("https://science.nasa.gov/", "https://spaceplace.nasa.gov/")
check("moi URL nguon thuoc ten mien NASA (science hoac spaceplace)",
      all(u.startswith(NASA_HOSTS) for u in urls),
      f"la: {[u for u in urls if not u.startswith(NASA_HOSTS)]}")
check("co it nhat 9 trang nguon NASA (bo goc khong bi xoa bot)", len(urls) >= 9,
      f"{len(urls)}")
check("thuat ngu dan so lieu tu 2 trang thi ghi CA HAI nguon",
      len(re.findall(r"sources: \[NASA\.[a-z]+, NASA\.[a-z]+\]", data_clean)) == 2,
      "term_planet (Planets+Dwarf) va term_moon (Moons+Ganymede)")

# ⚠️ PHEP KIEM NAY DA DOI HINH, NHUNG KHONG DOI DIEU NO BAO DAM.
#    Truoc: doi bo nguon Codex TRUNG KHOP tuyet doi bo nguon o `js/quiz-questions.js`
#    (bo do da curl kiem 200). Muc dich thuc su la: "Codex khong duoc dan mot URL
#    chua ai kiem". Tu 30/07/2026 Codex co 5 thuat ngu KHONG co cau hoi tuong ung
#    trong bank (lo den, hap dan, tinh van, sieu tan tinh, buc xa nen), nen bat
#    trung khop tuyet doi la sai — bo 2 phep kiem thi mat luon bao dam.
#    Nen: (a) moi nguon cua bank PHAI con trong Codex (khong duoc mat nguon da kiem),
#    (b) nguon CHI RIENG Codex thi script tu kiem 200 ngay tai day.
bank = rd(os.path.join(ROOT, "js", "quiz-questions.js"))
bank_urls = set(re.findall(r'url: "([^"]+)"', bank))
check("khong mat nguon nao da kiem 200 o quiz-questions.js",
      bank_urls <= urls, f"mat: {sorted(bank_urls - urls)}")

codex_only = sorted(urls - bank_urls)
if OFFLINE:
    print(f"  [..]   bo qua kiem 200 cho {len(codex_only)} URL rieng cua Codex (--offline)")
else:
    for u in codex_only:
        code = 0
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                code = r.status
        except Exception as e:  # noqa: BLE001
            code = f"loi: {type(e).__name__}"
        check(f"200: ...{u[-44:]}", code == 200, f"{code}")

# ══════════════════════════════════════════════════════════════
print("\n=== [6] DAY NOI THAT: quizBankTerms <-> term o js/quiz-questions.js ===")
bank_terms = set(re.findall(r'\bterm:\s*"([^"]+)"', bank))
check("doc duoc khoa term trong bank cau hoi", len(bank_terms) == 25, f"{len(bank_terms)}")

mapped = {}
dangling = []
for t in terms:
    for k in t["quizBankTerms"]:
        if k not in bank_terms:
            dangling.append(f"{t['id']} -> '{k}'")
        mapped.setdefault(k, []).append(t["id"])
check("moi quizBankTerms tro vao mot `term` CO THAT trong bank", not dangling,
      f"tro hong: {dangling}")

dup_map = {k: v for k, v in mapped.items() if len(v) > 1}
check("mot khoa bank khong bi hai thuat ngu cung nhan", not dup_map, f"{dup_map}")

# 20 câu thiên văn của bank phải được thuật ngữ nào đó nhận
astro_bank = set(re.findall(r'\bterm:\s*"([^"]+)"[\s\S]{0,4000}?src:\s*S\.', bank))
covered = set(mapped)
space_terms = [t for t in terms if t["category"] == "space"]
space_keys = {k for t in space_terms for k in t["quizBankTerms"]}
check("phu dung 20 khoa cau hoi thien van cua bank",
      len(space_keys) == 20, f"{len(space_keys)} khoa")

# ⚠️ CHIA HAI NHOM, VA DAY LA MOT LOI THAT DUOC GHI LAI CHU KHONG PHAI NOI LONG:
#    `js/quiz-questions.js` chi co cau hoi cho 10 thuat ngu thien van. 5 thuat ngu
#    them ngay 30/07/2026 (lo den · hap dan · tinh van · sieu tan tinh · buc xa nen)
#    CHUA CO CAU HOI NAO trong bank, nen `quizBankTerms: []` la trung thuc.
#    HE QUA PHAI BIET: `requiredQuizId` cua chung (`quiz_black_hole_01`…) chua ton
#    tai o dau ca -> 5 the nay se **khoa vinh vien** cho toi khi bank co cau hoi.
#    Dung y het loi da ghi trong CLAUDE.md o `js/specimens.js`: "dung viet 'Mo khoa
#    tai Mission 02' — nhiem vu DO chua ton tai nen mau se khoa vinh vien".
#    Phep kiem vi the DIEM DANH dung 5 id do: them thuat ngu khoa vinh vien thu 6
#    ma khong khai o day thi bao hong, va noi lai duoc mot mapping cu thi cung
#    bao hong (danh sach ngan lai).
PENDING_BANK = {
    "term_black_hole", "term_gravity", "term_nebula", "term_supernova", "term_cmb",
}
no_bank = {t["id"] for t in space_terms if not t["quizBankTerms"]}
check("dung 5 thuat ngu space CHUA co cau hoi trong bank (danh sach da biet)",
      no_bank == PENDING_BANK,
      f"them: {sorted(no_bank - PENDING_BANK)} · da noi day: {sorted(PENDING_BANK - no_bank)}")
check("thuat ngu space DA noi bank thi nhan dung 2 khoa",
      all(len(t["quizBankTerms"]) == 2 for t in space_terms if t["quizBankTerms"]),
      f"lech: {[(t['id'], len(t['quizBankTerms'])) for t in space_terms if t['quizBankTerms'] and len(t['quizBankTerms']) != 2]}")
prog_keys = {"algorithm", "loop", "condition", "sensor", "sequence"}
check("5 cau lap trinh cua bank khong bi thuat ngu space nhan bua",
      not (space_keys & prog_keys), f"{sorted(space_keys & prog_keys)}")

# ══════════════════════════════════════════════════════════════
print("\n=== [7] CSS: class `ac-` dung <-> khai (hai chieu) ===")
css = src["astronaut-codex.css"]
defined = set(re.findall(r"\.(ac-[a-z0-9-]+)", css))
# ⚠️ CHI quet trong className. `ac-codex-title` va `ac-lqip-blur` la ID
# (aria-labelledby va filter SVG) chu khong phai class — quet ca file thi hai cai
# do bi bao "thieu CSS" oan, va phep kiem mat tac dung vi ai cung phai bo qua no.
used = set()
for f, s in src.items():
    if not f.endswith((".tsx", ".astro")):
        continue
    for a, b in re.findall(r'className=(?:"([^"]*)"|\{`([^`]*)`\})', s):
        used |= set(re.findall(r"\b(ac-[a-z0-9-]+)", f"{a} {b}"))
    # className={[ … ].join(' ')} — bắt các chuỗi bên trong mảng
    for arr in re.findall(r"className=\{\[(.*?)\]\.join", s, re.S):
        used |= set(re.findall(r"\b(ac-[a-z0-9-]+)", arr))
check("moi class ac- dung trong tsx deu co CSS", used <= defined,
      f"thieu CSS: {sorted(used - defined)}")
check("khong co rule ac- bo khong", defined <= used,
      f"bo khong: {sorted(defined - used)}")
check("co @media prefers-reduced-motion", "prefers-reduced-motion" in css)
for anim in ("ac-scan", "ac-blink"):
    check(f"animation vo han `{anim}` bi tat khi giam chuyen dong",
          re.search(rf"@media[^{{]*prefers-reduced-motion[\s\S]*animation: none", css) is not None
          and anim in css)
check("KHONG dung filter grayscale de lam mo (bai hoc CLAUDE.md)",
      not any("grayscale" in code_only(s) for s in src.values()))

# ══════════════════════════════════════════════════════════════
print("\n=== [8] Yeu cau chuc nang cua de bai ===")
modal = src["TermCodexModal.tsx"]
card = src["TermCard.tsx"]
illus = src["TermIllustration.tsx"]
store = src["useTermStore.ts"]

check("modal co dung chu '🔒 Chưa giải mã'", "🔒 Chưa giải mã" in modal)
check("modal co dung chu '🔓 Đã giải mã'", "🔓 Đã giải mã" in modal)
check("modal co role=dialog + aria-modal", 'role="dialog"' in modal and 'aria-modal="true"' in modal)
check("modal dong bang Escape", "'Escape'" in modal)
check("modal chan cuon trang duoi", "document.body.style.overflow" in modal)
check("modal khoa tieu diem (bat Tab)", "'Tab'" in modal)
check("modal TRA tieu diem ve the vua bam", "opener?.focus" in modal)
check("KHONG co quiz trong modal (khong render cau hoi/dap an)",
      not re.search(r"\b(opts|answer|correctAnswer|onAnswer)\b", modal))
check("modal chi DAN sang Quest module", "onStartQuest" in modal)

check("the o luoi la <button> that", "<button" in card and "type=\"button\"" in card)
check("the khoa VAN bam duoc (khong disabled)", "disabled" not in card)
check("the hien badge phan loai", "meta.badge" in card)
check("the hien badge trang thai", "ĐÃ GIẢI MÃ" in card and "CHƯA GIẢI MÃ" in card)
check("the hien ten khoa hoc + ten vi von", "term.titleEn" in card and "term.analogy" in card)

check("anh dung loading=lazy", 'loading="lazy"' in illus)
check("anh dung decoding=async", 'decoding="async"' in illus)
check("co <picture> voi AVIF + WebP",
      "image/avif" in illus and "image/webp" in illus and "<picture>" in illus)
check("co placeholder mo bang SVG (feGaussianBlur)", "feGaussianBlur" in illus)
check("anh loi thi quay ve so do, khong de o anh vo", "onError" in illus and "setFailed" in illus)
check("mang yeu / saveData thi KHONG tai anh",
      "saveData" in illus and "slow-2g" in illus and "lowBandwidth" in illus)
check("khai width/height cho anh (chan CLS)",
      "width={image.width}" in illus and "height={image.height}" in illus)
check("khong thuat ngu nao tro vao anh chua ton tai",
      not any(t["has_illustration"] for t in terms),
      f"tro vao anh: {[t['id'] for t in terms if t['has_illustration']]}")

check("store dung useSyncExternalStore (dung chung giua cac island Astro)",
      "useSyncExternalStore" in store)
check("store co getServerSnapshot (khong vo hydration khi Astro SSR)",
      "getServerSnapshot" in store)
check("store nghe su kien `storage` (dong bo giua cac tab)",
      "'storage'" in store)
check("moi ham GHI deu ensureHydrated truoc (khong xoa tien do cu)",
      store.count("ensureHydrated();") >= 5, f"{store.count('ensureHydrated();')} lan goi")
check("co syncFromServer (server thang cache — quy tac 2 muc 6)",
      "syncFromServer" in store)
check("doc/ghi localStorage co try/catch (Safari rieng tu khong lam vo trang)",
      store.count("try {") >= 3, f"{store.count('try {')} khoi try")
check("khoa localStorage thuoc ho `astroq-`", "'astroq-codex-quizzes'" in store)
check("markQuizCompleted tra ve thuat ngu VUA mo (de hien toast)",
      "readonly CodexTerm[]" in store and "termsUnlockedBy" in store)

grid = src["AstronautCodex.tsx"]
grid_code = code_only(grid)
check("luoi dung so cot co dinh, KHONG auto-fill minmax (bai hoc 390px)",
      "grid-cols-2" in grid_code and "auto-fill" not in grid_code
      and "minmax(" not in grid_code)
check("KHONG dung display:contents cho <li> (mat ngu nghia danh sach)",
      'className="contents"' not in grid_code)
check("toast chi ban khi co thay doi THAT sau khi nap cache",
      "baselineRef" in grid and "snapshot.hydrated" in grid)
check("co thanh tien do co role=progressbar", 'role="progressbar"' in grid)

# ══════════════════════════════════════════════════════════════
print("\n=== [9] THU VIEN THIEN VAN: vo ngoai 5 tab ===")
# ⚠️ THEM CA THU MUC MOI VAO BO SOI. File khong nam trong bo kiem la DIEM MU —
#    dung bai hoc vua tra gia o `check_earth2d.py`: `CometGuidance.tsx` khong co
#    trong `FILES` nen 8 class thieu hoan toan CSS ma bo kiem van bao 81/83 dat.
LIB_FILES = ["AstronomyLibrary.tsx", "libraryTabs.ts", "astronomy-library.css", "index.ts"]
lib = {}
for f in LIB_FILES:
    p = os.path.join(LIB, f)
    check(f"co file {f}", os.path.exists(p))
    if os.path.exists(p):
        lib[f] = rd(p)
if len(lib) != len(LIB_FILES):
    print("\nDung som: thieu file cua Thu vien Thien van.")
    sys.exit(1)

for f, s in lib.items():
    errs = brace_errors(s)
    check(f"{f}: ngoac can va dung cap", not errs, "; ".join(errs[:3]))

shell = lib["AstronomyLibrary.tsx"]
shell_code = code_only(shell)
tabs_src = lib["libraryTabs.ts"]
tabs_code = code_only(tabs_src)

# --- 5 tab dung nhu de bai, So tay la MAC DINH ---
tab_ids = re.findall(r"^    id: '([a-z-]+)',", tabs_code, re.M)
check("khai dung 5 tab", len(tab_ids) == 5, f"{tab_ids}")
check("dung 5 id tab nhu de bai",
      tab_ids == ["codex", "cosmic-map", "lab", "events", "scale"], f"{tab_ids}")
check("tab MAC DINH la So tay (codex)", "DEFAULT_TAB: LibraryTabId = 'codex'" in tabs_code)
# ⚠️ DEM DANG CO DAU PHAY (`status: 'ready',`) — DANG DU LIEU. Dem chuoi tran thi
#    trung ca dong khai kieu `status: 'ready' | 'soon';` trong interface va bao 2.
check("chi tab codex la 'ready'", tabs_code.count("status: 'ready',") == 1,
      f"{tabs_code.count(chr(39).join(['status: ', 'ready', ',']))}")
check("4 tab con lai la 'soon' (noi that, khong dung UI gia)",
      tabs_code.count("status: 'soon',") == 4)
# Cung ly do: dem `label: '` chu khong phai `label:` (interface cung co `label: string;`).
check("moi tab co nhan vi + en",
      tabs_code.count("label: '") == tabs_code.count("labelEn: '") == 5,
      f"vi={tabs_code.count(chr(39).join(['label: ', '']))} en={tabs_code.count(chr(39).join(['labelEn: ', '']))}")
check("moi tab co mo ta vi + en",
      tabs_code.count("blurb: '") == tabs_code.count("blurbEn: '") == 5,
      f"vi={tabs_code.count(chr(39).join(['blurb: ', '']))} en={tabs_code.count(chr(39).join(['blurbEn: ', '']))}")

# --- Tab chua lam thi PHAI bam khong duoc ---
check("tab 'soon' bi disabled THAT, khong chi to mo",
      "disabled={soon}" in shell_code and "aria-disabled={soon}" in shell_code)
# ⚠️ Chan o CA hai cho: chi chan o cho ve nut thi go `?tab=lab` la vao duoc tab trong.
check("chan tab chua mo o CA cho doi tab, khong chi o cho ve nut",
      shell_code.count("isTabOpen(") >= 2, f"{shell_code.count('isTabOpen(')} cho")
check("KHONG dung filter grayscale de lam mo tab chua mo",
      "grayscale" not in shell_code and "grayscale" not in code_only(lib["astronomy-library.css"]))
check("co nhan SYS.STANDBY nhu 2 card 'sap ra mat' o dashboard",
      "SYS.STANDBY" in shell_code)

# --- De bai: KHONG audio, KHONG quiz trong thu vien ---
# ⚠️ Tim tren CODE DA BOC COMMENT: ghi chu cua toi GIAI THICH "khong co audio va
#    khong co quiz", tim tren van ban tho thi chinh loi canh bao bi tinh la vi pham
#    (lan thu SAU cung loai loi nay trong du an).
for pat, label in ((r"<audio", "<audio"), (r"new Audio\(", "new Audio()"),
                   (r"AudioContext", "AudioContext"), (r"AstroQSfx", "AstroQSfx")):
    hits = [f for f, s in lib.items() if re.search(pat, code_only(s))]
    check(f"KHONG co giong noi / am thanh: `{label}`", not hits, f"{hits}")
for pat, label in ((r"\bopts\s*:", "opts[] cua cau hoi"), (r"correctAnswer|isCorrect", "cham diem")):
    hits = [f for f, s in lib.items() if re.search(pat, code_only(s))]
    check(f"KHONG nhung quiz vao thu vien: `{label}`", not hits, f"{hits}")

# --- DUNG LAI So tay, khong viet ban thu hai ---
check("tab So tay DUNG LAI AstronautCodex co san",
      "AstronautCodex" in shell_code and "from '../astronaut-codex'" in shell_code)
check("KHONG dung file TermCodex.tsx thu hai (chi la bi danh o barrel)",
      not os.path.exists(os.path.join(CODEX, "TermCodex.tsx"))
      and not os.path.exists(os.path.join(LIB, "TermCodex.tsx")))
check("ten `TermCodex` de bai dung duoc, qua bi danh o barrel Codex",
      "export { default as TermCodex }" in src["index.ts"])
check("vo ngoai KHONG giu ban sao trang thai giai ma",
      "useState" in shell_code and "completedQuizIds" not in shell_code)

# --- class `al-` hai chieu ---
lib_css = lib["astronomy-library.css"]
al_defined = set(re.findall(r"\.(al-[a-z0-9-]+)", lib_css))
# ⚠️ PHAI TRU RA CAC ID. `al-panel-${id}` va `al-tab-${id}` la ID phan tu (dung cho
#    aria-controls / aria-labelledby / focus), KHONG phai class — de nguyen thi bo
#    kiem bao thieu CSS cho `al-panel-` va `al-tab-`, hai thu khong bao gio la class.
#    Dung bai hoc `em-win-title` o `check_earth2d.py` muc [10].
al_used = set(re.findall(r"\b(al-[a-z0-9-]+)", shell_code))
al_ids = set(re.findall(r"(?:id|aria-controls|aria-labelledby)=\{?`?(al-[a-z0-9-]+)", shell_code))
al_ids |= set(re.findall(r'getElementById\(`(al-[a-z0-9-]+)', shell_code))
al_used -= al_ids
check("phan biet duoc class voi id (al-tab-/al-panel- la id)",
      {"al-tab-", "al-panel-"} <= al_ids, f"{sorted(al_ids)}")
check("moi class al- dung trong tsx deu co CSS", al_used <= al_defined,
      f"thieu CSS: {sorted(al_used - al_defined)}")
check("khong co rule al- bo khong", al_defined <= al_used,
      f"bo khong: {sorted(al_defined - al_used)}")
check("co @media prefers-reduced-motion", "prefers-reduced-motion" in lib_css)
# Bai hoc `.hub-tag`: flex item co overflow:hidden bi bop con `[ …` o man 390px.
check("nhan header co min-width:max-content (bai hoc .hub-tag 390px)",
      "min-width: max-content" in lib_css)

# --- Tab la bo tab THAT (ban phim di duoc) ---
check("dung role tablist/tab/tabpanel",
      'role="tablist"' in shell_code and 'role="tab"' in shell_code
      and 'role="tabpanel"' in shell_code)
check("di giua cac tab bang mui trai/phai",
      "ArrowRight" in shell_code and "ArrowLeft" in shell_code)
check("roving tabIndex (chi tab dang mo nhan Tab tu ngoai)",
      "tabIndex={active ? 0 : -1}" in shell_code)

# --- Skeleton blur-up ---
card = src["TermCard.tsx"]
card_code = code_only(card)
check("co the giu cho blur-up (TermCardSkeleton)", "TermCardSkeleton" in card_code)
check("skeleton dung gradient CSS, 0 byte tai them",
      ".ac-skeleton" in src["astronaut-codex.css"]
      and "ac-shimmer" in src["astronaut-codex.css"])
# ⚠️ Luoi skeleton phai khop TUNG breakpoint voi luoi that, khong thi luc du lieu
#    ve so cot doi va ca luoi nhay — dung thu skeleton sinh ra de tranh.
real_grid = re.search(r'className="(grid grid-cols-2[^"]*)"', grid)
skel_grid = re.search(r'className="(grid grid-cols-2[^"]*)"', card)
check("luoi skeleton khop tung breakpoint voi luoi that",
      bool(real_grid) and bool(skel_grid) and real_grid.group(1) == skel_grid.group(1),
      f"that={real_grid.group(1) if real_grid else None} · skeleton={skel_grid.group(1) if skel_grid else None}")
check("skeleton la aria-hidden, bao 'dang tai' MOT lan o cap luoi",
      'aria-hidden="true"' in card_code and 'aria-busy="true"' in card_code)
check("skeleton tat hieu ung khi giam chuyen dong",
      ".ac-skeleton::after" in src["astronaut-codex.css"].split("prefers-reduced-motion", 1)[1])
check("mac dinh KHONG bat loading (du lieu nam san trong bundle)",
      "loading = false" in shell_code)

# --- unlockTermByQuiz + duong mo khoa phu ---
store = src["useTermStore.ts"]
store_code = code_only(store)
check("co ham `unlockTermByQuiz` dung ten de bai", "unlockTermByQuiz(" in store_code)
check("`unlockTermByQuiz` chi la vo mong, KHONG cai dat lai logic",
      re.search(r"unlockTermByQuiz\(completedQuizId: string\)[^}]*?"
                r"return codexStore\.markQuizCompleted\(completedQuizId\);", store_code, re.S)
      is not None)
check("co `quizIdsUnlocking` + `isTermUnlockedBy` gom hai field lam mot",
      "quizIdsUnlocking" in data_clean and "isTermUnlockedBy" in data_clean)
# ⚠️ Doc le `requiredQuizId` trong store la thuat ngu mo bang quiz phu se hien
#    "da giai ma" o man nay ma "chua giai ma" o man kia.
check("store KHONG con doc le `requiredQuizId` (moi cho di qua isTermUnlockedBy)",
      "requiredQuizId" not in store_code, "con doc le")
check("bao 'vua giai ma' phai so voi trang thai TRUOC khi ghi (khong toast trung)",
      "isTermUnlockedBy(t, before)" in store_code)

print(f"\n===== {ok_n} dat / {bad_n} hong =====")
sys.exit(1 if bad_n else 0)
