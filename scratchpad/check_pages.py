# -*- coding: utf-8 -*-
"""
check_pages.py — soi TĨNH các trang mới + các trang vừa nối điểm sinh dữ liệu.

Bắt những lỗi mà mở trình duyệt chưa chắc thấy ngay:
  · ngoặc JS không cân (lỗi cú pháp im lặng ở nhánh chưa chạy tới)
  · `$("id")` trỏ vào id không tồn tại
  · khoá i18n lệch giữa vi và en, hoặc khai mà không dùng
  · class dùng trong HTML/JS mà CSS không có (và ngược lại: CSS bỏ không)
  · asset (ảnh/css/js) trỏ vào file không có
  · huy hiệu server khai mà js/badges.js chưa có tên

    python scratchpad/check_pages.py
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SV = os.path.abspath(os.path.join(ROOT, "..", "AstroqSV"))

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def rd(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


def rd_abs(path):
    """Doc file NGOAI repo AstroQhtml (ma nguon backend o ../AstroqSV/)."""
    return io.open(path, encoding="utf-8").read()


def strip_js(s):
    """Bỏ chuỗi + comment để đếm ngoặc và tìm tên không bị nhiễu."""
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c == "/" and i + 1 < n and s[i + 1] == "*":
            j = s.find("*/", i + 2); i = (j + 2) if j >= 0 else n; continue
        if c == "/" and i + 1 < n and s[i + 1] == "/":
            j = s.find("\n", i); i = j if j >= 0 else n; continue
        if c in "\"'`":
            q = c; i += 1
            while i < n and s[i] != q:
                if s[i] == "\\": i += 1
                i += 1
            i += 1; out.append(' "" '); continue
        out.append(c); i += 1
    return "".join(out)


def inline_js(html):
    parts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
    return "\n".join(parts)


def balanced(js):
    js = strip_js(js)
    bad = []
    for o, c in (("(", ")"), ("{", "}"), ("[", "]")):
        if js.count(o) != js.count(c):
            bad.append(f"{o}{c}: {js.count(o)}/{js.count(c)}")
    return bad


def ids_in(html):
    return set(re.findall(r'\bid="([^"]+)"', html))


def i18n_dicts(js):
    """Lấy các khoá trong 2 từ điển vi/en của I18N (cách khai báo chung của dự án).

    ⚠️ Phải BỎ CHUỖI trước rồi mới tìm `khoa:`, và không được neo vào đầu dòng:
    dự án viết nhiều khoá trên cùng một dòng (`a_lang:"…", tt_name:"…", back:"…"`),
    bản đầu của script này neo `^\\s*(\\w+):` nên chỉ thấy khoá ĐẦU mỗi dòng và
    báo hỏng oan gần 30 khoá.
    """
    m = re.search(r"var\s+I18N\s*=\s*\{(.*?)\n  \};", js, re.S)
    if not m:
        return None, None
    body = m.group(1)

    def keys_of(lang):
        mm = re.search(lang + r"\s*:\s*\{(.*?)\n    \}", body, re.S)
        if not mm:
            return set()
        # strip_js đổi mọi chuỗi thành ' "" ' → chỉ còn lại đúng phần tên khoá
        return set(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*:', strip_js(mm.group(1))))
    return keys_of("vi"), keys_of("en")


def strip_comments(html):
    """Bỏ chú thích HTML + JS. Cần cho các phép kiểm 'không còn dấu vết X':
    chú thích ghi lại LỊCH SỬ ('tên cũ là …') là điều nên có, không phải lỗi."""
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"/\*.*?\*/", " ", html, flags=re.S)
    html = re.sub(r"(?m)^\s*//.*$", " ", html)
    return html


def css_classes(*rels):
    s = ""
    for r in rels:
        s += rd(r)
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    return set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", s))


def clean_token(c):
    """Chỉ giữ token là TÊN CLASS thật.

    Markup do JS sinh có dạng `class="stop'+(on?" on":"")+'"` — cắt theo khoảng
    trắng sẽ ra những mảnh như `stop'+(on?` . Bản đầu của script này đếm cả
    những mảnh đó và báo 'thiếu CSS' oan.
    """
    return c if re.fullmatch(r"-?[_a-zA-Z][\w-]*", c or "") else None


def used_classes(html):
    used = set()
    for v in re.findall(r'class=\\?["\']([^"\']*)', html):
        for c in v.split():
            t = clean_token(c)
            if t:
                used.add(t)
    for v in re.findall(r'classList\.(?:add|remove|toggle)\("([^"]+)"', html):
        for c in v.split():
            t = clean_token(c)
            if t:
                used.add(t)
    return used


def assets(html):
    out = set()
    for m in re.findall(r'(?:src|href)="([^"#?]+)"', html):
        if m.startswith(("http", "//", "mailto:", "data:")):
            continue
        if m.endswith((".html", "/")):
            continue
        # Đường dẫn do JS ghép (`src="'+c.ava+'"`) không phải asset tĩnh
        if any(ch in m for ch in "'+\"()"):
            continue
        out.add(m)
    return out


# ══════════════════════════════════════════════════════════════
print("=== [1] Trang moi: cu phap + id + i18n + asset ===")
for page, css in (("profile.html", ["css/common.css", "css/page-shell.css", "css/profile.css"]),
                  ("achievements.html", ["css/common.css", "css/page-shell.css", "css/achievements.css"]),
                  # missions.html them 29/07/2026 — cung khuon page-shell nen soi
                  # duoc bang dung bo phep kiem nay, khong phai viet rieng.
                  ("missions.html", ["css/common.css", "css/page-shell.css", "css/missions.css"]),
                  # codex.html them 30/07/2026 — cung khuon page-shell nen soi duoc
                  # bang dung bo phep kiem nay (i18n vi/en khop · moi $("id") ton tai
                  # · moi class co CSS · asset khong hong).
                  ("codex.html", ["css/common.css", "css/page-shell.css", "css/codex.css"])):
    html = rd(page)
    js = inline_js(html)
    bad = balanced(js)
    check(f"{page}: ngoac JS can", not bad, "; ".join(bad))

    have = ids_in(html)
    refs = set(re.findall(r'\$\("([^"]+)"\)', js))
    missing = sorted(refs - have)
    check(f"{page}: moi $(\"id\") deu ton tai", not missing,
          f"thieu: {missing}" if missing else f"{len(refs)} id")

    vi, en = i18n_dicts(js)
    check(f"{page}: co tu dien I18N vi+en", bool(vi) and bool(en),
          f"vi={len(vi or [])} en={len(en or [])}")
    if vi and en:
        check(f"{page}: khoa i18n khop vi/en", vi == en,
              f"chi vi: {sorted(vi-en)} · chi en: {sorted(en-vi)}")
        # khoá nào khai mà không dùng ở đâu
        used = set(re.findall(r'data-i18n(?:-[a-z]+)?="([^"]+)"', html))
        # ⚠️ `t\(` KHÔNG được để trơn: nó khớp cả phần đuôi của `closest(".play-btn")`
        # (…closes + t(" ) và báo hỏng oan một khoá i18n tên `.play-btn`. Chặn bằng
        # cách đòi ký tự trước `t` không phải chữ/số/`_`/`.`.
        # ⚠️ QUÉT TRÊN CODE ĐÃ BÓC COMMENT. Ghi chú GIẢI THÍCH cách dùng `t()` là
        #    thứ nên có, nhưng nếu quét cả comment thì một ghi chú viết `t("…")` bị
        #    tính là một khoá i18n đang dùng, và phép kiểm báo "chưa khai" oan. Đây
        #    là lần thứ TÁM cùng loại lỗi này trong dự án (xem check_codex.py và
        #    check_earth2d.py) — phép kiểm phải khớp HÌNH DẠNG CỦA CODE, đừng khớp chữ.
        used |= set(re.findall(r'(?<![A-Za-z0-9_$.])t\("([^"]+)"\)', strip_comments(js)))
        # Khoá GHÉP ĐỘNG (`t("m_"+m.key+"_tag")`) không bắt được bằng cách tìm chuỗi
        # nguyên. Trang nào có thì khai họ khoá ở đây, và phải có một phép kiểm RIÊNG
        # chứng minh đủ bộ (xem mục [7c] cho missions.html) — bỏ qua mà không kiểm bù
        # thì mất luôn tác dụng canh thiếu khoá.
        DYN = {"missions.html": [r"^m_[a-z]+_(tag|name|desc)$"]}
        dyn_pat = DYN.get(page, [])
        unused = sorted(k for k in (vi - used)
                        if not any(re.match(p, k) for p in dyn_pat))
        check(f"{page}: khong co khoa i18n bo khong", not unused, f"bo khong: {unused}")
        undefined = sorted(used - vi)
        check(f"{page}: moi khoa dung deu duoc khai", not undefined, f"chua khai: {undefined}")

    miss_a = sorted(a for a in assets(html) if not os.path.exists(os.path.join(ROOT, a)))
    check(f"{page}: asset day du", not miss_a, f"thieu: {miss_a}")

    have_css = css_classes(*css)
    used_c = used_classes(html)
    # class chỉ để đọc màn hình / do trang khác dùng thì bỏ qua
    skip = {"sr-only", "nebula", "starfield", "toast", "modal", "lic", "tt-inline"}
    no_css = sorted(c for c in used_c - have_css - skip if not c.startswith("data-"))
    check(f"{page}: moi class deu co CSS", not no_css, f"thieu CSS: {no_css}")

# ══════════════════════════════════════════════════════════════
print("\n=== [2] Trang vua noi diem sinh du lieu: cu phap ===")
for page in ("dashboard.html", "quiz.html", "learn.html", "library.html",
             "game-dodge.html", "game-defender.html", "game-constellation.html",
             "explorer.html", "select.html", "specimen-vault.html",
             "mission-earth.html", "codex.html"):
    html = rd(page)
    js = inline_js(html)
    bad = balanced(js)
    check(f"{page}: ngoac JS can", not bad, "; ".join(bad))

# ══════════════════════════════════════════════════════════════
print("\n=== [3] Diem sinh du lieu co day du khong ===")
WIRED = {
    "quiz.html":                ("AstroQProgress.quiz(",   "js/progress.js"),
    "learn.html":               ("AstroQProgress.lesson(", "js/progress.js"),
    "library.html":             ("AstroQProgress.lesson(", "js/progress.js"),
    "game-dodge.html":          ('game:"dodge"',           "js/progress.js"),
    "game-defender.html":       ('game:"defender"',        "js/progress.js"),
    "game-constellation.html":  ('game:"constellation"',   "js/progress.js"),
    "explorer.html":            ("AstroQProgress.planet(", "js/progress.js"),
    "mission-earth.html":       ("AstroQProgress.missionStep(", "js/progress.js"),
}
for page, (call, dep) in WIRED.items():
    html = rd(page)
    check(f"{page}: co goi {call}…", call in html)
    check(f"{page}: co nap {dep}", f'src="{dep}"' in html)

# ══════════════════════════════════════════════════════════════
print("\n=== [3b] Trang nhiem vu: khong tu quyet phan thuong ===")
me = rd("mission-earth.html")
check("mission-earth.html nap js/sfx.js (am thanh dung chung)", 'src="js/sfx.js"' in me)
check("mission-earth.html KHONG nap firebase-auth.js (SDK 233 KB)",
      'src="js/firebase-auth.js"' not in me)
# Bảng luật ở AstroqSV/Services/Missions.cs — client chỉ gửi {mission, step}.
# Bất kỳ con số thưởng nào lọt vào đây là dấu hiệu client tự tính lại.
import re as _re
_bad = [k for k in ("addAsteroids", "Economy.add") if k in me]
# `reward.meteors += r.data.awarded` là ĐÚNG — cộng đúng con số SERVER trả về.
# Chỉ sai khi cộng một số viết cứng trong trang.
_bad += _re.findall(r"reward\.(?:meteors|xp|codex)\s*\+?=\s*[0-9]", me)
check("mission-earth.html KHONG tu cong tt/XP bang so viet cung", not _bad, str(_bad))
check("mission-earth.html chi doc thuong tu phan hoi server",
      "r.data.awarded" in me and "r.data.xpGained" in me)
_mv = _re.search(r"missionStep\(([^)]*)\)", me)
check("missionStep chi gui {mission, step}", bool(_mv) and "meteors" not in _mv.group(1),
      _mv.group(0) if _mv else "khong thay")

# ⚠️ MAN TONG KET: KHONG CON DAU VET MAT TRANG NAO (chot 30/07/2026).
#    Truoc do trang co han mot khoi "HANH TINH MOI DA MO KHOA 🌙 MAT TRANG" kem nut
#    `win-moon` de `disabled`. Nhiem vu do CHUA TON TAI (`Missions.All` chi co
#    `earth`, khong co mission-moon.html), nen mot nut bam khong duoc van la mot loi
#    hua ve thu khong co. Server VAN giu `Unlocks: "moon"` — do la du lieu cua
#    server, khong phai giao dien.
#    Bo kiem nay tung KHONG TON TAI, va do la ly do loi song sot: yeu cau bo Mat
#    Trang duoc lam o ban React (khong trang nao nap) trong khi trang THAT con nguyen.
#    ⚠️ Quet tren code DA BOC COMMENT: ghi chu trong trang GHI LAI lich su "truoc day
#       o day co nut Mat Trang" — do la thu nen co, khong phai vi pham.
_me_code = strip_comments(me)
_moon = _re.findall(r"win-moon|win_moon|🌙|MẶT TRĂNG|Mặt Trăng|THE MOON", _me_code)
check("man tong ket KHONG con dau vet Mat Trang nao", not _moon, f"{sorted(set(_moon))}")
# Va phai CO thu thay the: bo trang khong thi man tong ket thanh duong cut.
check("man tong ket co khoi 'viec tiep theo' dan di duoc THAT",
      "win-missions" in _me_code and "missions.html" in _me_code)
check("nut viec tiep theo KHONG bi disabled (missions.html co that)",
      not _re.search(r"win-missions'\)\.disabled\s*=\s*true", _me_code)
      and 'id="win-missions"' in me and 'id="win-missions" disabled' not in me)
for k in ("win_next_k", "win_next", "win_missions"):
    check(f"mission-earth.html: khoa i18n `{k}` co o CA vi va en",
          me.count(k + ":") == 2, f"{me.count(k + ':')} lan")

# ══════════════════════════════════════════════════════════════
print("\n=== [3c] Nhiem Vu 01: 8 buoc khop server + codex + i18n ===")
# Ba chỗ phải nói cùng một câu chuyện, và không chỗ nào suy ra được từ chỗ kia:
#   · Missions.cs   : có những bước nào, thứ tự chơi, mẫu codex nào mở ở bước nào
#   · mission-earth.html : STEP_IDS (thứ tự thật khi chơi)
#   · earth_codex.json   : nội dung đọc của từng mẫu codex
# Lệch nhau thì lỗi rất khó thấy: bước client gửi mà server không biết → `counted:false`
# nên KHÔNG có thưởng và cũng KHÔNG có lỗi nào hiện ra.
mi_cs = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"),
                encoding="utf-8").read()
_earth = mi_cs.split('new("earth", "earth",', 1)[1].split("], DoneMeteors", 1)[0]
sv_steps = _re.findall(r'new\("([a-z]+)",\s*\d+,\s*\d+,\s*(null|"[a-z0-9,-]+")\)', _earth)
sv_ids = [s[0] for s in sv_steps]
_cl = _re.search(r"const STEP_IDS = \[([^\]]*)\]", me)
cl_ids = _re.findall(r"'([a-z]+)'", _cl.group(1)) if _cl else []
check("STEP_IDS cua trang KHOP dung thu tu voi Missions.cs",
      sv_ids == cl_ids, f"server={sv_ids} client={cl_ids}")
check("Nhiem Vu 01 co 8 buoc", len(sv_ids) == 8, str(len(sv_ids)))
check("Moi buoc co object xu ly trong trang",
      all(_re.search(r"^  " + s + r": \{", me, _re.M) for s in sv_ids),
      str([s for s in sv_ids if not _re.search(r"^  " + s + r": \{", me, _re.M)]))

# Mẫu codex server khai ↔ entry trong earth_codex.json
sv_codex = []
for _s in sv_steps:
    if _s[1] != "null":
        sv_codex += _s[1].strip('"').split(",")
_cx = json.loads(rd("learningdata/astronomy/earth_codex.json"))
cx_ids = [e["id"] for e in _cx["entries"]]
check("Moi mau codex server khai deu co bai doc o earth_codex.json",
      set(sv_codex) <= set(cx_ids), str(sorted(set(sv_codex) - set(cx_ids))))
check("earth_codex.json khong co bai doc la",
      set(cx_ids) <= set(sv_codex), str(sorted(set(cx_ids) - set(sv_codex))))
check("earth_codex.json: `count` khop so entry",
      _cx["count"] == len(cx_ids), f'count={_cx["count"]} entries={len(cx_ids)}')
check("earth_codex.json: moi entry co tieu de vi+en",
      all(e.get("title", {}).get("vi") and e.get("title", {}).get("en") for e in _cx["entries"]),
      str([e["id"] for e in _cx["entries"] if not e.get("title", {}).get("en")]))
check("earth_codex.json: moi entry co nguon tham chieu",
      all(e.get("source_reference", {}).get("url") for e in _cx["entries"]),
      str([e["id"] for e in _cx["entries"] if not e.get("source_reference", {}).get("url")]))
# Nội dung chưa qua rà soát chuyên môn thì phải TỰ KHAI, y như learningdata/README.md
check("earth_codex.json: moi entry tu khai da qua ra soat chua",
      all("reviewed_by_teacher" in e for e in _cx["entries"]),
      str([e["id"] for e in _cx["entries"] if "reviewed_by_teacher" not in e]))

# i18n: trang này dùng dấu nháy ĐƠN (khác profile/achievements ở mục [1]) nên phải
# tìm bằng regex riêng. Chỉ so vi ↔ en — không soi "khoá bỏ không" vì trang ghép khoá
# động (`'era_' + e.id + '_y'`, `'eco_' + c.id`…) sẽ báo hỏng oan cả loạt.
# `i18n_dicts()` của mục [1] neo vào `var I18N` + thụt 2 dấu cách; trang này khai
# `const I18N` ở top-level của <script type="module"> nên thụt khác — tự tách ở đây
# thay vì nới regex dùng chung (nới rộng là dễ bắt lẫn thứ khác ở 2 trang kia).
_me_js = inline_js(me)
_me_i18n = _re.search(r"const I18N = \{(.*?)\n\};", strip_js(_me_js), _re.S)


def _me_keys(lang):
    if not _me_i18n:
        return set()
    mm = _re.search(r"\b" + lang + r"\s*:\s*\{(.*?)\n  \}", _me_i18n.group(1), _re.S)
    return set(_re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", mm.group(1))) if mm else set()


_vi, _en = _me_keys("vi"), _me_keys("en")
check("mission-earth.html: co tu dien I18N vi+en", bool(_vi) and bool(_en),
      f"vi={len(_vi)} en={len(_en)}")
if _vi and _en:
    check("mission-earth.html: khoa i18n khop vi/en", _vi == _en,
          f"chi vi: {sorted(_vi - _en)} · chi en: {sorted(_en - _vi)}")
    # Khoá GHÉP ĐỘNG (`'era_' + e.id + '_y'`…) không bắt được bằng cách tìm t('...'),
    # nên soi theo họ: mỗi phần tử dữ liệu phải có đủ bộ khoá của nó. Thiếu một cái là
    # trên màn hình hiện thẳng tên khoá (`era_dino_n`) chứ không vỡ trang — rất dễ lọt.
    def _dyn(name, block_re, suffixes):
        mm = _re.search(block_re, me, _re.S)
        ids = _re.findall(r"id: '([a-z0-9]+)'", mm.group(1)) if mm else []
        want = {f"{p}{i}{s}" for i in ids for p, s in suffixes}
        check(f"mission-earth.html: du khoa i18n ghep dong cho {name}",
              bool(ids) and want <= _vi, str(sorted(want - _vi)))

    _dyn("ERAS", r"const ERAS = \[(.*?)\n\];", [("era_", "_y"), ("era_", "_n"), ("era_", "_p")])
    _dyn("ENERGY", r"const ENERGY = \[(.*?)\n\];", [("ce_", "")])
    _dyn("ECO", r"const ECO = \[(.*?)\n\];", [("eco_", "")])
# `$('id')` nháy đơn — id nào gọi trong JS mà HTML không có là lỗi im lặng (null.textContent)
_me_ids = ids_in(me)
_me_refs = set(_re.findall(r"\$\('([^']+)'\)", _me_js))
check("mission-earth.html: moi $('id') deu ton tai",
      _me_refs <= _me_ids, f"thieu: {sorted(_me_refs - _me_ids)}")
# Class dùng trong markup phải có CSS (bốn bảng kéo-thả mới dễ quên khai)
_me_css = css_classes("css/common.css", "css/mission-earth.css")
_me_used = used_classes(me)
_me_skip = {"sr-only", "nebula", "starfield", "toast", "modal", "lic", "tt-inline", "hit"}
check("mission-earth.html: moi class deu co CSS",
      not sorted(_me_used - _me_css - _me_skip),
      f"thieu CSS: {sorted(_me_used - _me_css - _me_skip)}")

# ══════════════════════════════════════════════════════════════
print("\n=== [3d] LUAT THUONG: doc bai KHONG thuong, quiz phai DAT ===")
# Chot 30/07/2026. Hai luat nay chi dung khi CLIENT va SERVER noi cung mot thu, nen
# muc nay doi chieu hai ben chu khong chi doc mot ben.
_wallet = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/Wallet.cs"))
_ep = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Endpoints/MeEndpoints.cs"))
_quiz = rd("quiz.html")
_learn = rd("learn.html")
_lib = rd("library.html")
_eco = rd("economy.js")

# --- (1) Doc bai khong thuong ---
check("server: tran thuong doc bai = 0 (cho chan THAT)",
      re.search(r"MaxPerLesson\s*=\s*0\b", _wallet) is not None)
for name, src_ in (("learn.html", _learn), ("library.html", _lib)):
    # ⚠️ Quet tren CODE DA BOC COMMENT: ghi chu o hai file GIAI THICH vi sao khong
    #    goi `addAsteroids` — tim tren van ban tho thi chinh loi canh bao bi tinh la
    #    vi pham (lan thu bay cung loai loi nay trong du an).
    body = strip_comments(src_)
    check(f"{name}: KHONG cong tt khi doc bai", "addAsteroids" not in body,
          "con goi addAsteroids")
    check(f"{name}: VAN ghi tien do doc bai (bo tien, khong bo ghi nhan)",
          "AstroQProgress.lesson(" in body)
    check(f"{name}: KHONG con nhan '+N tt' tren nut/the doc bai",
          "reward" not in body, "con chu 'reward'")

# --- (2) Quiz phai dat ---
m_ratio = re.search(r"QuizPassRatio\s*=\s*([\d.]+)", _wallet)
check("server: co nguong dat QuizPassRatio", bool(m_ratio), f"{m_ratio}")
m_pct = re.search(r"var PASS_PCT\s*=\s*(\d+)", _quiz)
check("quiz.html: co ban sao nguong dat PASS_PCT", bool(m_pct), f"{m_pct}")
if m_ratio and m_pct:
    # ⚠️ PHEP KIEM QUAN TRONG NHAT CUA MUC NAY: hai ben giu cung mot con so.
    #    Lech thi tre doc nguong cua client nhung nhan tien theo nguong cua server.
    check("nguong dat CLIENT khop SERVER",
          abs(float(m_ratio.group(1)) * 100 - int(m_pct.group(1))) < 0.001,
          f"server={m_ratio.group(1)} client={m_pct.group(1)}%")
check("server: quiz di qua AwardQuiz (co cong 'dat'), khong phai Award tron",
      "Wallet.AwardQuiz(" in _ep)
check("server: tra ve quizPassed cho client khoi tu quyet", "quizPassed" in _ep)
_quiz_body = strip_comments(_quiz)
# Cong tt PHAI o man tong ket, KHONG o cho tra loi tung cau.
check("quiz.html: chi cong tt MOT lan, o man tong ket",
      _quiz_body.count("Economy.addAsteroids(") == 1,
      f"{_quiz_body.count('Economy.addAsteroids(')} cho")
check("quiz.html: cong tt co dieu kien DAT", "if(passed && gain>0)" in _quiz_body)
check("quiz.html: chua dat thi gui meteors = so THAT (gain), khong phai earned",
      "meteors: gain" in _quiz_body)
check("quiz.html: noi ro can bao nhieu cau dung khi chua dat",
      "fail_note" in _quiz_body and "PASS_MIN" in _quiz_body)
for lang_key in ("pass_note", "fail_note"):
    check(f"quiz.html: khoa i18n `{lang_key}` co o CA vi va en",
          _quiz.count(lang_key + ":") == 2, f"{_quiz.count(lang_key + ':')} lan")

# --- (3) So du khoi tao khop vi server ---
m_def = re.search(r"var DEFAULT_BALANCE\s*=\s*(\d+)", _eco)
check("economy.js: so du khoi tao = 0, khop vi server (khong con 50 tt ao)",
      bool(m_def) and m_def.group(1) == "0", f"{m_def.group(1) if m_def else None}")

# --- (4) meteorsEarned cong bang so THAT ---
# ⚠️ Truoc day `deltas["meteorsEarned"]` duoc cong bang so CLIENT KHAI, truoc khi
#    kep tran -> huy hieu "nha suu tam" mo bang tien chua bao gio ton tai.
check("server: meteorsEarned cong bang `award` (so that), khong phai so client khai",
      re.search(r'if \(award > 0\) deltas\["meteorsEarned"\] = award;', _ep) is not None)

# Trang nao duoc phep nap SDK Firebase (nang 233 KB)
print("\n=== [4] Chi cac trang noi dung duoc nap SDK Firebase ===")
# specimen-vault.html thêm 29/07/2026: là trang nội dung (không phải game) và bắt
# buộc cần token để gọi GET /me/specimens. Game/quiz/learn/library/explorer vẫn
# KHÔNG được nạp — SDK 233 KB, những trang đó cần mượt.
# codex.html thêm 30/07/2026: cùng lý do specimen-vault — là trang nội dung và
# bắt buộc cần token để đọc `progress.terms` (thuật ngữ đã trả lời đúng). Không có
# token thì trang phải hiện MỌI thẻ ở trạng thái chưa giải mã, nên nạp SDK ở đây là
# đánh đổi có ý thức chứ không phải quên.
allowed = {"dashboard.html", "achievements.html", "profile.html", "landing-app.html",
           "specimen-vault.html", "missions.html", "codex.html"}
for f in sorted(os.listdir(ROOT)):
    if not f.endswith(".html"):
        continue
    if 'src="js/firebase-auth.js"' in rd(f):
        check(f"{f}: nap firebase-auth.js", f in allowed,
              "khong nen nap o day" if f not in allowed else "")

# ══════════════════════════════════════════════════════════════
print("\n=== [5] Huy hieu: server khai vs js/badges.js co ten ===")
ach = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Achievements.cs"),
              encoding="utf-8").read()
server_ids = re.findall(r'new\("([a-z0-9-]+)",\s*"([a-z]+)"', ach)
badges_js = rd("js/badges.js")
client_ids = set(re.findall(r'"([a-z0-9-]+)":\s*\{\s*ic:', badges_js))
client_groups = set(re.findall(r'^\s{4}([a-z]+):\s*\{\s*ic:', badges_js, re.M))

check("Server khai >= 20 huy hieu", len(server_ids) >= 20, f"{len(server_ids)}")
missing_name = sorted({i for i, _ in server_ids} - client_ids)
check("Moi huy hieu server deu co ten o js/badges.js", not missing_name,
      f"thieu ten: {missing_name}")
extra_name = sorted(client_ids - {i for i, _ in server_ids})
check("js/badges.js khong co ten mo coi", not extra_name, f"mo coi: {extra_name}")
server_groups = {g for _, g in server_ids}
check("Nhom huy hieu khop hai ben", server_groups <= client_groups,
      f"server: {sorted(server_groups)} · client: {sorted(client_groups)}")

# ══════════════════════════════════════════════════════════════
print("\n=== [6] Roster nhan vat chi khai o MOT cho ===")
chars = rd("js/characters.js")
n_chars = len(re.findall(r'\{\s*id:"', chars))
check("js/characters.js khai 10 nhan vat", n_chars == 10, f"{n_chars}")
af = rd("js/auth-flow.js")
check("js/auth-flow.js dung AstroQChars.all(), khong copy lai",
      "AstroQChars.all()" in af and 'model:"3d/' not in af)
sel = rd("select.html")
check("select.html nap js/characters.js truoc auth-flow.js",
      sel.index('src="js/characters.js"') < sel.index('src="js/auth-flow.js"'))
prof = rd("profile.html")
check("profile.html dung AstroQChars, khong copy roster",
      "AstroQChars.all()" in prof and 'model:"3d/' not in prof)

# ══════════════════════════════════════════════════════════════
print("\n=== [7] Doi ten Khu Huan Luyen ===")
# Kiem tra tren ban DA BO CHU THICH: chu thich ghi "ten cu la Phong Trai Luc"
# la ghi lai lich su, khong phai chu con sot tren giao dien.
for f in sorted(os.listdir(ROOT)):
    if f.endswith(".html"):
        s = strip_comments(rd(f))
        check(f"{f}: khong con 'Phong Trai Luc'", "Phòng Trái Lực" not in s)
        check(f"{f}: khong con 'Gravity Room'", "Gravity Room" not in s)
dash = rd("dashboard.html")
dash_nc = strip_comments(dash)
check("dashboard.html: co 'Khu Huan Luyen'", "Khu Huấn Luyện" in dash)
# EN "Training Bay" → "Training Simulator" (29/07/2026)
check("dashboard.html: co 'Training Simulator' (EN)", "Training Simulator" in dash)
check("dashboard.html: khong con 'Training Bay' (ten cu)", "Training Bay" not in dash_nc)

# Tên trang dashboard: "Khoang Lái" → "Trung Tâm Điều Hướng" / "Navigation Hub".
# CỐ Ý KHÔNG cấm chữ "khoang lái" nói chung: buồng lái của con tàu vẫn là buồng lái
# (bàn trưng mẫu vật ở specimen-vault.html, lời SEO ở index.html). Chỉ cấm những
# CHUỖI dùng nó làm TÊN TRANG.
OLD_PAGE_NAME = ['Về Khoang Lái', 'Back to Cockpit', 'Return to Cockpit',
                 'home_btn:"Khoang Lái"', 'home_btn:"Cockpit"']
for f in sorted(os.listdir(ROOT)):
    if not f.endswith(".html"):
        continue
    s_nc = strip_comments(rd(f))
    left = [k for k in OLD_PAGE_NAME if k in s_nc]
    check(f"{f}: khong con ten trang cu 'Khoang Lai'", not left, str(left))
check("dashboard.html: tu goi minh la 'Trung Tam Dieu Huong'",
      "Trung Tâm Điều Hướng" in dash)
check("dashboard.html: co ten EN 'Navigation Hub'", "Navigation Hub" in dash)

# --- Ten khu Tri Thuc: PHAI la "Trạm Tri Thức", khong duoc de "Tri Thức" tron ---
# ⚠️ Truoc 31/07/2026 KHONG CO phep kiem nao cho ten khu nay, va do la ly do lan
#    doi ten bo sot mot cho: `learn.html` con chu TINH "TRI THỨC & DỮ LIỆU VŨ TRỤ"
#    trong markup (JS ghi de nen do tren trinh duyet khong thay).
# ⚠️ PHAI so bang casefold() CUA PYTHON, khong dung `grep -i`: grep -i KHONG
#    case-fold duoc ky tu co dau tieng Viet (Ứ vs ứ), nen lan quet dau tien cua
#    toi bao "khong con cho nao" trong khi con dung mot cho — chu do viet HOA.
_KNOW_OK_PREFIX = ("trạm ", "ngân hà ")   # "Ngân Hà Tri Thức" la cau van o index
_know_bad = []
for _f in sorted(os.listdir(ROOT)):
    if not (_f.endswith(".html")):
        continue
    _s = strip_comments(rd(_f))
    _lo = _s.casefold()
    for _m in re.finditer("tri thức", _lo):
        _ctx = _lo[max(0, _m.start() - 14):_m.start()]
        if not any(p in _ctx for p in _KNOW_OK_PREFIX):
            _know_bad.append(f"{_f}:{_s[max(0,_m.start()-24):_m.start()+12].strip()!r}")
for _f in sorted(os.listdir(os.path.join(ROOT, "js"))):
    if not _f.endswith(".js"):
        continue
    _s = strip_comments(rd(os.path.join("js", _f)))
    _lo = _s.casefold()
    for _m in re.finditer("tri thức", _lo):
        _ctx = _lo[max(0, _m.start() - 14):_m.start()]
        if not any(p in _ctx for p in _KNOW_OK_PREFIX):
            _know_bad.append(f"js/{_f}:{_s[max(0,_m.start()-24):_m.start()+12].strip()!r}")
check("khong con 'Tri Thuc' tron (phai la 'Tram Tri Thuc')", not _know_bad,
      str(_know_bad[:3]))
check("dashboard.html: the MOD-01 goi dung 'Tram Tri Thuc'",
      "Trạm Tri Thức" in dash)
check("learn.html: tu goi minh la 'Tram Tri Thuc'", "Trạm Tri Thức" in rd("learn.html"))

# Mọi trang có nút quay lại đều phải trỏ về ĐÚNG một cái tên
for f in sorted(os.listdir(ROOT)):
    if not f.endswith(".html"):
        continue
    s_nc = strip_comments(rd(f))
    if 'data-i18n="back"' not in s_nc and 'data-i18n="home_btn"' not in s_nc:
        continue
    # library.html va codex.html deu la trang CON cua khu Tri Thuc (mo tu learn.html)
    # nen nut quay lai tro ve do, khong ve hub — di mot buoc len cha la dung hon la
    # nhay hai buoc ve goc.
    if f in ("library.html", "codex.html"):
        continue
    check(f"{f}: nut quay lai goi dung ten hub",
          "Trung Tâm Điều Hướng" in s_nc and "Navigation Hub" in s_nc)

# 3 khu moi tren dashboard
# ⚠️ NHAN CUA check() PHAI KHONG DAU. Console Windows mac dinh cp1252, in mot chu co
# dau la UnicodeEncodeError NEM GIUA LUC CHAY va bo do script — mat luon moi phep
# kiem phia sau, ma nhin output thi tuong la "chay xong". Chu co dau chi duoc nam
# trong DIEU KIEN, khong nam trong nhan.
print("\n=== [7b] Dashboard: 6 card, 3 khu moi ===")
for key, mod in (("mission_title", "MOD-04"), ("lab_title", "MOD-05"),
                 ("archive_title", "MOD-06")):
    check(f"dashboard.html: co khoa i18n '{key}'", key in dash)
    check(f"dashboard.html: co so hieu {mod}", mod in dash_nc)
for label, nm in (("Trung Tam Nhiem Vu", "Trung Tâm Nhiệm Vụ"),
                  ("Mission Control", "Mission Control"),
                  ("Phong Nghien Cuu", "Phòng Nghiên Cứu"),
                  ("Research Lab", "Research Lab"),
                  ("Thu Vien Thien Van", "Thư Viện Thiên Văn"),
                  ("Star Archive", "Star Archive")):
    check(f"dashboard.html: co ten '{label}'", nm in dash)
# So hieu MOD cu KHONG duoc danh lai (tai lieu + cach nguoi dung goi ten bam vao no)
for mod in ("MOD-01", "MOD-02", "MOD-03"):
    check(f"dashboard.html: giu nguyen {mod}", mod in dash_nc)
# Hai khu chua co trang thi PHAI noi that: nut disabled, khong dan di dau
check("dashboard.html: 2 card 'soon' co nut disabled",
      dash_nc.count('data-i18n="soon_btn" disabled') == 2,
      str(dash_nc.count('data-i18n="soon_btn" disabled')))
check("dashboard.html: card 'soon' KHONG dan sang trang khong ton tai",
      'href="research-lab.html"' not in dash and 'href="star-archive.html"' not in dash)
check("dashboard.html: card Mission Control dan sang missions.html",
      'href="missions.html"' in dash)

# ══════════════════════════════════════════════════════════════
print("\n=== [7c] Sanh Nhiem Vu: khop server + khong bia tien do ===")
mis = rd("missions.html")
mis_js = inline_js(mis)
# `key` cua MISSIONS phai la id nhiem vu THAT o server (hoac nhiem vu chua co =
# status "soon"). Dat key sai thi GET /me/missions tra ve khong co khoa do → trang
# im lang hien 0/8 nhu the nguoi choi chua lam gi.
mis_keys = re.findall(r'\{\s*key:"([a-z]+)"[^}]*status:"(ready|soon)"', mis_js, re.S)
mi_cs2 = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"),
                 encoding="utf-8").read()
sv_mission_ids = set(re.findall(r'new\("([a-z]+)",\s*"[a-z]+",\s*\[', mi_cs2))
ready_keys = {k for k, st in mis_keys if st == "ready"}
check("missions.html: co ca 2 nhiem vu (earth + moon)", len(mis_keys) == 2, str(mis_keys))
check("missions.html: moi nhiem vu 'ready' deu co that o Missions.cs",
      ready_keys <= sv_mission_ids, str(sorted(ready_keys - sv_mission_ids)))
check("missions.html: nhiem vu server co ma sanh chua liet ke",
      sv_mission_ids <= {k for k, _ in mis_keys},
      str(sorted(sv_mission_ids - {k for k, _ in mis_keys})))
# Du bo khoa i18n cho tung nhiem vu (khoa ghep dong, xem ghi chu o muc [1])
mis_vi, _mis_en = i18n_dicts(mis_js)
if mis_vi:
    want_keys = {f"m_{k}_{sfx}" for k, _ in mis_keys for sfx in ("tag", "name", "desc")}
    check("missions.html: du khoa i18n ghep dong cho tung nhiem vu",
          want_keys <= mis_vi, str(sorted(want_keys - mis_vi)))
# Mat mang / chua dang nhap → hien dau "—", KHONG hien 0/8 (0/8 la mot loi khang
# dinh SAI ve tien do cua nguoi choi). Cung nguyen tac achievements/specimen-vault.
check("missions.html: co dai nhac khi khong doc duoc tien do", 'id="offline"' in mis)
check("missions.html: dung dau gach ngang thay vi 0 khi chua co du lieu",
      'DASH = "—"' in mis_js and "VIEW.ok ?" in mis_js)
check("missions.html: KHONG tu tinh phan thuong",
      "addAsteroids" not in mis_js and "Economy.spend" not in mis_js)
check("missions.html: doc tien do qua AstroQProgress.missions()",
      "AstroQProgress.missions()" in mis_js)

# ══════════════════════════════════════════════════════════════
print("\n=== [8] Dashboard khong con so bia ===")
FAKE = ["Nhà Du Hành", "Voyager", "streakDays", "flightHours: 12.5",
        "quizAccuracy: 88", "earned:12", "+120 XP"]
for f in FAKE:
    check(f"dashboard.html: da bo '{f}'", f not in dash_nc)
check("dashboard.html: goi loadStats()", "loadStats()" in dash)
check("dashboard.html: co duong vao achievements.html", 'href="achievements.html"' in dash)
check("dashboard.html: co duong vao profile.html", 'href="profile.html"' in dash)

# ══════════════════════════════════════════════════════════════
print("\n=== [9] Vi Thien thach tim: PHI do server quyet ===")
# Không trang nào được tự trừ tiền nữa — phải đi qua Economy.spend(<ten game>),
# hàm này chỉ gửi TÊN GAME lên server.
for page, game in (("game-dodge.html", "dodge"),
                   ("game-defender.html", "defender"),
                   ("game-constellation.html", "constellation")):
    s = rd(page)
    check(f"{page}: dung Economy.spend(\"{game}\")", f'Economy.spend("{game}")' in s)
    check(f"{page}: KHONG con tu tru bang useAsteroids(COST)",
          "Economy.useAsteroids(CONFIG.COST)" not in s)

eco = rd("economy.js")
check("economy.js co setFromServer (server ghi de cache)", "setFromServer" in eco)
check("economy.js co bang phi (chi de hien so + chan tai cho)", "var FEES" in eco)
prog = rd("js/progress.js")
check("js/progress.js sinh opId chong trung", "newOpId" in prog)
check("js/progress.js day so du server vao Economy", "Economy.setFromServer" in prog)
check("js/progress.js xep ca viec 'spend' vao hang cho", '"spend"' in prog)
fa = rd("js/firebase-auth.js")
check("firebase-auth.js co spendWallet + getWallet",
      "spendWallet" in fa and "getWallet" in fa)
check("Client KHONG bao gio gui so tien can tru len server",
      not re.search(r'spendWallet\([^)]*(amount|fee|cost)\s*:', fa + prog + eco))

# Bang phi phai khop giua client va server
wal = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Wallet.cs"), encoding="utf-8").read()
sv_fees = dict((m[0], int(m[1])) for m in re.findall(r'\["([a-z-]+)"\]\s*=\s*(\d+)', wal))
cl_fees = dict((m[0], int(m[1])) for m in
               re.findall(r'(\w+):\s*(\d+)', re.search(r"var FEES = \{([^}]*)\}", eco).group(1)))
check("Bang phi khop client/server", sv_fees == cl_fees, f"server={sv_fees} client={cl_fees}")
# ...va khop ca badge phi hien o games.html
hub_fees = dict((m[1], int(m[0])) for m in
                re.findall(r'cost:(\d+)[^}]*?file:"game-([a-z]+)\.html"', rd("games.html")))
hub_fees = {("constellation" if k == "constellation" else k): v for k, v in hub_fees.items()}
check("Phi hien o games.html khop bang phi server",
      all(sv_fees.get(k) == v for k, v in hub_fees.items()),
      f"hub={hub_fees} server={sv_fees}")

print("\n=== [10] Chom sao: khoa phai la id trong SKY ===")
sky = re.findall(r'key:"([a-z-]+)"', rd("game-constellation.html"))
# Tên chòm sao đã tách sang js/constellations.js (29/07/2026) — CHỖ DUY NHẤT khai
# báo, dùng chung bởi achievements.html và specimen-vault.html. Đối chiếu với đó.
cj_keys = re.findall(r'key:\s*"([a-z-]+)"', rd("js/constellations.js"))
check("game-constellation.html khai 4 chom sao", len(sky) == 4, str(sky))
check("js/constellations.js dung DUNG khoa cua SKY (khong phai ten tieng Viet)",
      set(cj_keys) == set(sky), f"constellations.js={cj_keys} sky={sky}")
for _pg in ("achievements.html", "specimen-vault.html"):
    check(f"{_pg} lay ten chom sao tu js/constellations.js (khong copy)",
          'src="js/constellations.js"' in rd(_pg)
          and not re.search(r'\{\s*key:"[a-z-]+"\s*,\s*vi:', rd(_pg)))
check("game-constellation.html bao id chom sao len server",
      "id:consKey" in rd("game-constellation.html"))
check("achievements.html doc chom sao tu server truoc, may sau",
      "VIEW.consts" in rd("achievements.html"))
check("profile.html dem so chom sao tu constsDone", "constsDone" in rd("profile.html"))

print("\n=== [11] Mau vat: server khai vs js/specimens.js co ten ===")
# Cùng phân công như huy hiệu ở mục [5]: server giữ điều kiện mở khoá, client giữ
# tên/mô tả song ngữ. Thêm mẫu ở server mà quên thêm tên là trang hiện chính id.
spc = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Specimens.cs"),
              encoding="utf-8").read()
sv_spec = re.findall(r'new\("([a-z0-9-]+)",\s*"([a-z]+)",\s*"([a-z]+)",\s*"([a-z0-9-]+)"', spc)
spec_js = rd("js/specimens.js")
# Chỉ lấy khoá trong object `S` (mẫu vật). Cắt trước `var CATS` vì ORIGINS/CATS
# cũng thụt 4 dấu cách nên regex bắt lẫn cả tên nơi lấy mẫu ("earth-ocean"…).
s_block = spec_js.split("var S = {", 1)[1].split("var CATS", 1)[0]
cl_spec = set(re.findall(r'^\s{4}"([a-z0-9-]+)":\s*\{', s_block, re.M))
check("Server khai 21 mau vat", len(sv_spec) == 21, str(len(sv_spec)))
check("Moi mau server khai deu co ten o js/specimens.js",
      {s[0] for s in sv_spec} <= cl_spec, str(sorted({s[0] for s in sv_spec} - cl_spec)))
check("js/specimens.js KHONG co mau la",
      cl_spec <= {s[0] for s in sv_spec}, str(sorted(cl_spec - {s[0] for s in sv_spec})))
# 6 từ 29/07/2026 (thêm `ancient-lava-rock`). Client đọc `rareTotal` từ API nên không
# phải sửa gì ở giao diện — phép kiểm này chỉ để việc thêm mẫu hiếm luôn là quyết định
# CÓ Ý THỨC, vì con số đó hiện thẳng trên thanh "Mẫu vật hiếm: n/6".
check("Dung 6 mau hang hiem (con so hien tren thanh tien do)",
      sum(1 for s in sv_spec if s[2] in ("rare", "legendary")) == 6,
      str(sum(1 for s in sv_spec if s[2] in ("rare", "legendary"))))
check("Moi `origin` cua server co ten o js/specimens.js",
      all(f'"{s[3]}":' in spec_js for s in sv_spec),
      str([s[3] for s in sv_spec if f'"{s[3]}":' not in spec_js]))
me_cs = io.open(os.path.join(SV, "src/AstroqSV.Api/Endpoints/MeEndpoints.cs"),
                encoding="utf-8").read()
check("Chi co 2 route /me/specimens (GET + PUT desk), khong co route 'collect'",
      me_cs.count('MapGet("/specimens"') == 1
      and me_cs.count('MapPut("/specimens/desk"') == 1
      and "collect" not in me_cs)
check("Client KHONG tu quyet mau nao da mo khoa",
      "unlocked =" not in rd("specimen-vault.html")
      and "unlocked=" not in rd("specimen-vault.html"))
# Chỉ soi trong từ điển HINT — ghi chú ở đầu file CÓ chứa chữ "Mission 02" đúng
# để cảnh báo đừng dùng, quét cả file thì tự báo hỏng chính lời cảnh báo đó.
hint_block = spec_js.split("var HINT = {", 1)[1].split("\n  };", 1)[0]
# Từ 29/07/2026 phép kiểm đổi cách hỏi: KHÔNG cấm nhắc nhiệm vụ nữa (Nhiệm Vụ 01 có
# thật ở mission-earth.html, hứa với trẻ là hứa được), mà cấm nhắc nhiệm vụ CHƯA CÓ.
# Cách hỏi cũ "không có chữ Nhiệm vụ + số" sẽ chặn luôn cả câu nhắc đúng.
MISSIONS_LIVE = {"earth"}                      # nhiệm vụ đã có trang chơi thật
hint_mission_keys = set(re.findall(r'"(mission:[a-z0-9:-]+)"\s*:', hint_block))
hinted_missions = {k.split(":")[1] for k in hint_mission_keys}
check("Cau nhac mo khoa chi nhac nhiem vu DA CO trang choi",
      hinted_missions <= MISSIONS_LIVE, str(sorted(hinted_missions - MISSIONS_LIVE)))
# Mẫu vật mở bằng một bước nhiệm vụ thì phải có câu nhắc riêng, không thì rơi về câu
# chung "Tiếp tục khám phá để mở khoá" — trẻ không biết phải làm gì để có nó.
spec_mission_metrics = set(re.findall(r'"(mission:[a-z0-9:-]+)"', spc))
check("Moi dieu kien mission: cua mau vat deu co cau nhac rieng",
      spec_mission_metrics <= hint_mission_keys,
      str(sorted(spec_mission_metrics - hint_mission_keys)))
check("Cau nhac co ca vi va en", '"vi"' not in hint_block and "vi: {" in hint_block
      or "vi:" in hint_block and "en:" in hint_block)

# ══════════════════════════════════════════════════════════════
print("\n=== [12] SO TAY THUAT NGU: day noi that quiz -> server -> codex ===")
# Chot 30/07/2026. Truoc do co ca mot bo React 2.920 dong cho tinh nang nay ma
# KHONG trang nao nap, va `quiz.html` khong gui `terms` nen khong the giai ma.
_cx = rd("js/codex-terms.js")
_cxp = rd("codex.html")
_bank = rd("js/quiz-questions.js")
_icons = rd("js/icons.js")
_qz = strip_comments(rd("quiz.html"))
_prog = strip_comments(rd("js/progress.js"))
_dyn = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Data/DynamoContext.cs"))
_mep = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Endpoints/MeEndpoints.cs"))

# --- (1) doc du 15 thuat ngu, moi cai du 2 ngon ngu ---
_ids = re.findall(r'^      id: "(term_[a-z_0-9]+)"', _cx, re.M)
check("doc duoc danh sach thuat ngu", len(_ids) > 0, f"{len(_ids)}")
check("co it nhat 15 thuat ngu (bo goc khong bi xoa bot)", len(_ids) >= 15, f"{len(_ids)}")
if not _ids:
    print("\nDung som: khong doc ra thuat ngu nao, moi phep kiem sau se DAT MOT CACH RONG.")
    sys.exit(1)
check("khong co id trung", len(set(_ids)) == len(_ids),
      f"trung: {[x for x in set(_ids) if _ids.count(x) > 1]}")
# Song ngu: dem so khoi `vi: {` phai bang so khoi `en: {` va bang so thuat ngu
check("moi thuat ngu du CA vi va en",
      _cx.count("      vi: {") == _cx.count("      en: {") == len(_ids),
      f"vi={_cx.count('      vi: {')} en={_cx.count('      en: {')} ids={len(_ids)}")
for f in ("t:", "an:", "sum:", "def:", "gr:", "dg:"):
    n = len(re.findall(r"\b" + re.escape(f), _cx))
    check(f"moi ban ngu du truong `{f}`", n == len(_ids) * 2, f"{n} / can {len(_ids) * 2}")

# --- (2) DAY NOI: moi khoa `q` phai co THAT trong bank cau hoi ---
_bank_terms = set(re.findall(r'\bterm:\s*"([^"]+)"', _bank))
check("doc duoc khoa term trong bank", len(_bank_terms) > 0, f"{len(_bank_terms)}")
_blocks = re.split(r'\n    \{\n(?=      id: "term_)', "\n" + _cx)
_qmap, _dangling, _noq = {}, [], []
for b in _blocks[1:]:
    tid = re.search(r'id: "(term_[a-z_0-9]+)"', b).group(1)
    qm = re.search(r"q: \[(.*?)\]", b, re.S)
    keys = re.findall(r'"([^"]+)"', qm.group(1)) if qm else []
    if not keys:
        _noq.append(tid)
    for k in keys:
        if k not in _bank_terms:
            _dangling.append(f"{tid} -> '{k}'")
        _qmap.setdefault(k, []).append(tid)
check("moi khoa `q` tro vao mot `term` CO THAT trong bank", not _dangling,
      f"tro hong: {_dangling}")
check("mot khoa bank khong bi hai thuat ngu cung nhan",
      not {k: v for k, v in _qmap.items() if len(v) > 1},
      f"{ {k: v for k, v in _qmap.items() if len(v) > 1} }")
# ⚠️ 5 thuat ngu CHUA co cau hoi — giao dien phai noi "sap co", KHONG hua nhiem vu
#    khong ton tai (bai hoc js/specimens.js). Diem danh dung 5 id do.
# ✅ 30/07/2026: da them 10 cau cho 5 thuat ngu con lai -> danh sach nay GIO RONG.
#    Giu phep kiem: them thuat ngu ma quen them cau hoi thi no khoa vinh vien.
PENDING = set()
check("khong thuat ngu nao con thieu cau hoi trong bank", set(_noq) == PENDING,
      f"thieu cau hoi: {sorted(set(_noq))}" if _noq else "")

# ⚠️ HAI PHEP KIEM DUOI DAY CHUYEN TU `check_codex.py` SANG (30/07/2026), truoc khi
#    xoa bo React da bi thay the. Chung canh CODE DANG CHAY nen khong duoc mat.
# (a) 5 cau lap trinh cua bank la cau KHAI NIEM, khong co `src`, va khong thuoc thuat
#     ngu thien van nao. Thuat ngu nhan bua mot trong 5 khoa do la giai ma sai bang
#     mot cau khong lien quan.
PROG_KEYS = {"algorithm", "loop", "condition", "sensor", "sequence"}
check("5 cau lap trinh KHONG bi thuat ngu nao nhan bua",
      not (set(_qmap) & PROG_KEYS), f"{sorted(set(_qmap) & PROG_KEYS)}")
check("codex.html co trang thai thu BA cho thuat ngu chua co cau hoi",
      '"soon"' in _cxp and "soon_hint" in _cxp)
check("codex.html KHONG dan sang Quiz khi chua co cau hoi",
      'hidden = st==="soon"' in _cxp or '$("m-quiz").hidden = st==="soon"' in _cxp)

# --- (3) icon: moi khoa `ic` phai co ban ve ---
_ic_used = set(re.findall(r'ic: "(cx-[a-z-]+)"', _cx))
_ic_have = set(re.findall(r"'(cx-[a-z-]+)':", _icons))
check("moi khoa icon `cx-` deu co ban ve trong js/icons.js", _ic_used <= _ic_have,
      f"thieu: {sorted(_ic_used - _ic_have)}")
check("khong co ban ve `cx-` bo khong", _ic_have <= _ic_used,
      f"bo khong: {sorted(_ic_have - _ic_used)}")

# --- (4) quiz.html -> server: co GUI terms khong ---
check("quiz.html gom khoa thuat ngu tra loi DUNG", "okTerms.push(it.term)" in _qz)
check("quiz.html gui `terms` len server", "terms: okTerms" in _qz)
check("quiz.html xoa danh sach khi lam lai (khong cong don qua nhieu luot)",
      "okTerms=[]" in _qz)
# ⚠️ Gui terms KE CA khi chua dat: cong "dat" chi chi phoi THIEN THACH TIM.
check("js/progress.js chuyen tiep `terms`", "ev.terms = o.terms.slice()" in _prog)
check("js/progress.js CHI gui khi co (SS cua DynamoDB khong nhan tap rong)",
      "if (o.terms && o.terms.length)" in _prog)

# --- (5) server: nhan, loc, luu, tra ve ---
check("server: ProgressRequest nhan `Terms`", "string[]? Terms," in _mep)
check("server: LOC khoa bang Clean (du lieu client khong tin duoc)",
      "Clean(t, 40)" in _mep)
check("server: KEP so khoa theo so cau DUNG (1 cau dung khong mo ca so tay)",
      "Math.Min(correct, MaxTermsPerQuiz)" in _mep)
check("server: truyen terms vao BumpProgressAsync",
      "constellation, okTerms)" in _mep)
check("server: luu bang ADD tren string set (hop, khong trung, khong mat khi song song)",
      'adds.Add("#terms :terms")' in _dyn)
check("server: chan tap rong truoc khi ghi SS", "terms.Count > 0" in _dyn)
check("server: tra `terms` ve trong snapshot", "terms          = p.Terms," in _mep)

# --- (6) codex.html KHONG bia trang thai giai ma ---
check("codex.html doc `progress.terms` tu SERVER", "p.terms" in _cxp)
check("codex.html chua doc duoc thi hien dai nhac, KHONG bia da giai ma",
      "b_auth" in _cxp and "b_net" in _cxp and "var done = null" in _cxp)
check("codex.html KHONG dung filter grayscale de lam mo the khoa",
      "grayscale" not in strip_comments(_cxp)
      and "grayscale" not in re.sub(r"/\*.*?\*/", " ", rd("css/codex.css"), flags=re.S))
check("codex.html: the chua giai ma VAN bam duoc (che noi dung, khong che duong vao)",
      "cx-i-red" in _cxp)
check("codex.html co nguon NASA cho tung thuat ngu", "src_lbl" in _cxp and "x.src" in _cxp)
check("js/codex-terms.js: moi thuat ngu co nguon", _cx.count("src: [") == len(_ids),
      f"{_cx.count('src: [')} / {len(_ids)}")
# URL nguon phai thuoc ten mien NASA (science.nasa.gov hoac spaceplace.nasa.gov)
_cx_urls = set(re.findall(r'url: "([^"]+)"', _cx))
check("moi URL nguon thuoc ten mien NASA",
      all(u.startswith(("https://science.nasa.gov/", "https://spaceplace.nasa.gov/"))
          for u in _cx_urls),
      f"la: {[u for u in _cx_urls if not u.startswith(('https://science.nasa.gov/', 'https://spaceplace.nasa.gov/'))]}")
# (b) Bo nguon cua so tay phai TRUNG KHOP bo nguon cua bank. Nho vay 12 URL do duoc
#     `check_quiz_bank.py` kiem 200 THAT tren Chromium cung chinh la bo so tay dung —
#     khong phai kiem 200 lan thu hai o day.
_bank_urls = set(re.findall(r'url: "([^"]+)"', _bank))
check("bo nguon so tay TRUNG KHOP bo nguon bank (de duoc kiem 200 mot lan)",
      _cx_urls == _bank_urls,
      f"chi so tay: {sorted(_cx_urls - _bank_urls)} · chi bank: {sorted(_bank_urls - _cx_urls)}")

# --- (7) duong vao tu learn.html + khong con loi hua thuong doc bai ---
_learn = rd("learn.html")
check("learn.html co the MOD-C dan sang codex.html",
      'id="btn-codex"' in _learn and 'location.href="codex.html"' in strip_comments(_learn))
for key in ("cx_tag", "cx_title", "cx_desc", "cx_btn"):
    check(f"learn.html: khoa `{key}` co o CA vi va en", _learn.count(key + ":") == 2,
          f"{_learn.count(key + ':')} lan")
# ⚠️ Doc bai khong con thuong tt (chot cung ngay) — cau chu quang cao phai theo.
check("learn.html KHONG con hua 'doc xong nhan Thien thach tim'",
      "Đọc xong nhận Thiên thạch tím" not in _learn
      and "Earn Purple Meteors when you finish" not in _learn)

# ══════════════════════════════════════════════════════════════
print("\n=== [13] LUONG HAU-NHIEM-VU: ve 5 giay + Comet chi duong ===")
_me2 = strip_comments(rd("mission-earth.html"))
_dash2 = strip_comments(rd("dashboard.html"))
_tour = strip_comments(rd("js/onboard-tour.js"))
_tcss = rd("css/onboard-tour.css")
_dyn2 = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Data/DynamoContext.cs"))
_ep2 = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Endpoints/MeEndpoints.cs"))

# --- (1) Duong ve tu dong 5 giay ---
check("man tong ket co duong ve tu dong 5 giay",
      re.search(r"AUTO_RETURN_SECS\s*=\s*5\b", _me2) is not None)
# ⚠️ Dem gio phai bat SAU khi bao xong len server. Bat dam bao bang THU TU GOI:
#    finishStep() lam `await reportStep(id)` roi moi toi showWin().
check("`startAuto` goi trong showWin (tuc SAU await reportStep)", "startAuto();" in _me2)
check("moi tuong tac TAT dem (khong phai tam dung)",
      all(ev in _me2 for ev in ("pointerdown", "keydown", "mouseenter", "touchstart"))
      and "cancelAuto" in _me2)
# ⚠️ KHONG bat `focus`: nut chinh duoc focus() cho nguoi dung ban phim, bat focus la
#    dem bi tat ngay luc mo modal va tinh nang thanh vo nghia.
check("KHONG bat su kien focus de tat dem",
      not re.search(r"addEventListener\(\s*['\"]focus", _me2))
check("het dem thi ve dashboard (khong phai trang khac)",
      re.search(r"autoLeft <= 0.*?dashboard\.html", _me2, re.S) is not None)
_meraw = rd("mission-earth.html")
check("mission-earth.html: khoa i18n `win_auto` co o CA vi va en",
      _meraw.count("win_auto:") == 2, f"{_meraw.count('win_auto:')} lan")

# --- (2) DUNG LAI engine tour, khong viet overlay thu hai ---
check("dashboard DUNG LAI AstroQTour.guide, khong tu ve overlay",
      "AstroQTour.guide(" in _dash2)
check("engine tour nhan bo buoc rieng (`steps`) + co rieng (`onSeen`)",
      "activeSteps" in _tour and "onSeen" in _tour and "stepsNow()" in _tour)
# ⚠️ Doc le STEPS o bat ky dau la luot dung lai se ve buoc CUA MAN TOUR.
check("moi cho doc bo buoc di qua stepsNow()", "STEPS[idx]" not in _tour,
      "con doc STEPS[idx] truc tiep")
# ⚠️ Thieu onSeen thi markSeen() roi ve nhanh mac dinh va ghi `tourSeen` — mot phi
#    hanh gia moi MAT LUON man dan tham quan vi mot loi chuc mung.
check("guide() BAT BUOC co onSeen, khong thi khong chay",
      'typeof opts.onSeen !== "function"' in _tour)
check("markSeen ton trong onSeen cua luot dung lai",
      "if (onSeen) { onSeen(); return; }" in _tour)

# --- (3) Vong nhap nhay: dung gia tri de bai yeu cau ---
check("co vong nhap nhay `.tour.pulse`", ".tour.pulse .tour-hole" in _tcss)
check("dung dung gia tri bong do de bai yeu cau",
      "0 0 20px rgba(56,189,248,.8)" in _tcss)
# ⚠️ Bong do phai CONG VAO lop toa 9999px; thay the thi mat luon phan lam toi trang.
# ⚠️ KIEM TRONG CHINH KHOI KEYFRAMES. Ban dau dem "9999px" tren CA FILE, nen khi
#    keyframes bi doi thanh `box-shadow:0 0 22px …` (thay the thay vi cong vao) thi
#    ca file van con 9999px o cho khac va phep kiem van "dat" — dat mot cach rong.
_kf = re.search(r"@keyframes tourPulse\{(.*?)^\}", _tcss, re.S | re.M)
check("co keyframes tourPulse", bool(_kf))
check("MOI khung cua tourPulse GIU lop lam toi 9999px",
      bool(_kf) and _kf.group(1).count("9999px") == 2,
      f"{_kf.group(1).count('9999px') if _kf else 0} / can 2 khung")
_rm = _tcss.split("prefers-reduced-motion", 1)[1]
check("giam chuyen dong: tat animation nhung GIU bong do tinh",
      "tour.pulse" in _rm and "9999px" in _rm)
# ⚠️ The cao thi phai cuon LEN DAU, khong cuon vao giua — cuon vao giua thi ca tren
#    va duoi deu thieu cho va box thoai de len chinh the dang gioi thieu (do duoc
#    che 74% o man 390x844 truoc khi sua).
check("the cao thi cuon len dau, khong cuon vao giua",
      'block: tall ? "start" : "center"' in _tour)

# --- (4) Dieu kien chao: hoi SERVER ca hai, khong doan ---
check("hoi server chuoi xong chua (/me/missions), khong luu ban sao o may",
      "AstroQProgress.missions()" in _dash2 and "e.done !== true" in _dash2)
check("hoi server da chao chua (co earth1Greeted)",
      "earth1Greeted" in _dash2 and "getOnboarding()" in _dash2)
# ⚠️ Khac han man dan tham quan: o do "tha chao hai lan hon khong chao lan nao".
#    O day chao sai la chuc mung mot viec tre CHUA lam.
# ⚠️ DOI DU CA VE GUARD. Ban dau chi tim "o.earth1Greeted) return" — chuoi do van
#    con trong ban da bi bo `!o || !o.ok`, nen phep kiem KHONG bat duoc (da thu).
check("khong doc duoc co -> KHONG chao (du ca ve guard)",
      "!o || !o.ok || o.earth1Greeted) return" in _dash2)
check('the MOD-04 co data-tour="missions" (so nhieu, da chot)',
      'data-tour="missions"' in _dash2)
# ⚠️ CHI DEM THUOC TINH HTML, khong dem SELECTOR. Ban dau dem chuoi tran nen no
#    tinh ca `target: '[data-tour="missions"]'` trong JS va bao 2 the — trong khi
#    chi co dung 1 the. Chan bang cach doi ky tu truoc khong phai `[`.
_attr = re.findall(r'(?<!\[)data-tour="missions"', _dash2)
check("chi MOT the mang thuoc tinh data-tour=missions", len(_attr) == 1,
      f"{len(_attr)} the")
check("ghi RIENG co earth1Greeted, khong dung tourSeen",
      "setOnboarding({ earth1Greeted: true })" in _dash2)
check("khong chao khi man khac dang mo (hai lop toi chong nhau)",
      "AstroQTour.isOpen()" in _dash2)

# --- (5) Server: co thu ba, doc lap voi hai co kia ---
check("server: record Onboarding co Earth1Greeted", "Earth1Greeted" in _dyn2)
check("server: SetOnboardingAsync nhan earth1Greeted", "bool? earth1Greeted" in _dyn2)
check("server: ghi RIENG co duoc truyen vao (null = khong dung toi)",
      'sets.Add("earth1Greeted = :g, earth1GreetedAt = :t")' in _dyn2)
check("server: DTO tra ve earth1Greeted", "earth1Greeted   = o.Earth1Greeted" in _ep2)
# ⚠️ Dieu kien "body rong -> tourSeen true" phai loai TRU ca co moi; thieu no thi
#    goi {earth1Greeted:true} se dong thoi bat luon tourSeen.
check("server: body rong -> tourSeen true, nhung co moi KHONG kich hoat no",
      "tour is null && intro1 is null && greeted is null) tour = true" in _ep2)


# ============================================================
# [14] QUY UOC TOAN SITE — hai phep kiem chan dung LOAI LOI da xay ra:
#      "mot trang tu tach khoi quy uoc chung ma khong ai biet".
# ============================================================
print("\n=== [14] Quy uoc toan site: nut doi ngon ngu + script ten mien ngoai ===")

_html_pages = sorted(f for f in os.listdir(ROOT)
                     if f.endswith(".html") and os.path.isfile(os.path.join(ROOT, f)))

# --- (1) Trang nao GOI initLang thi PHAI co markup nut doi ngon ngu ---
# ⚠️ Phep kiem nay sinh ra tu mot loi that: `explorer.html` goi
#    `initLang(applyLanguage, '.lang-btn')`, `css/explorer.css` co du 3 rule
#    `.lang-btn`, nhung MARKUP thi khong co phan tu nao — nen trang do KHONG CO
#    nut doi ngon ngu suot nhieu thang ma khong gi bao loi. CSS co rule va JS co
#    lenh deu KHONG chung minh duoc rang nguoi dung BAM DUOC.
_calls, _missing, _partial = [], [], []
for _f in _html_pages:
    _h = rd(_f)
    if "initLang" not in _h:
        continue
    _calls.append(_f)
    _langs = set(re.findall(r'data-lang="([a-z]{2})"', _h))
    if not _langs:
        _missing.append(_f)
    elif not {"vi", "en"} <= _langs:
        _partial.append((_f, sorted(_langs)))

check("co trang nao goi initLang (phep kiem khong dat rong)", len(_calls) >= 10,
      f"{len(_calls)} trang")
check("MOI trang goi initLang deu co markup data-lang", not _missing, str(_missing))
check("moi trang do co DU ca 'vi' va 'en'", not _partial, str(_partial))

# Truyen selector RIENG cho initLang la duong quay lai dung cai bay tren: dat ten
# khac `.lang-switch` thi khung dung chung o css/common.css khong ap vao nua.
_own_sel = [_f for _f in _calls
            if re.search(r"initLang\([^)]*,\s*['\"]", rd(_f))]
check("khong trang nao truyen selector RIENG cho initLang", not _own_sel, str(_own_sel))

# --- (2) Khong trang nao nap script tu TEN MIEN NGOAI ---
# ⚠️ Du an da tra gia de bo 2 ket noi ngoai (tu host font: 621 KB -> 101 KB) va co
#    y KHONG nap SDK Firebase o trang can muot. Nhung `explorer.html` va
#    `mission-earth.html` van keo three.js tu unpkg.com — do duoc 257 KB gzip, tu
#    mot ten mien khong ai kiem soat, nam tren duong onboarding BAT BUOC.
#    Phep kiem nay KHONG doi 0 ngay mot: no GHIM danh sach hien tai lai, de them
#    trang thu ba la biet ngay. Bo three.js xong thi xoa ten khoi _KNOWN_CDN va
#    phep kiem thu hai se doi danh sach phai RONG.
_KNOWN_CDN = {"explorer.html", "mission-earth.html"}
_ext = {}
for _f in _html_pages:
    _h = rd(_f)
    _hosts = set(re.findall(r'"(?:https?:)?//([a-z0-9.-]+)/[^"]*\.m?js"', _h))
    _hosts |= set(re.findall(r'<script[^>]+src="(?:https?:)?//([a-z0-9.-]+)', _h))
    if _hosts:
        _ext[_f] = sorted(_hosts)
check("khong co trang MOI nao nap script tu ten mien ngoai",
      set(_ext) <= _KNOWN_CDN,
      str({k: v for k, v in _ext.items() if k not in _KNOWN_CDN}))
check("danh sach trang con phu thuoc CDN dung nhu da ghi",
      set(_ext) == _KNOWN_CDN,
      f"dang co {sorted(_ext)}, da ghi {sorted(_KNOWN_CDN)}")

print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
sys.exit(0 if bad_n == 0 else 1)
