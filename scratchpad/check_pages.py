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
import glob
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


def page_css(rel_html):
    """Danh sach CSS mot trang THUC SU nap, doc tu chinh the <link> cua no.

    ⚠️ Truoc 31/07/2026 phep kiem "moi class deu co CSS" GAN CUNG danh sach file
       CSS. Tach `.aq-say/.aq-ava/.aq-nm` ra `css/mascot.css` la phep kiem bao
       thieu CSS ngay, du trang da nap dung file — no khong biet co file moi.
       Phep kiem gan cung danh sach thi moi lan them stylesheet lai phai sua
       phep kiem, va nguoi sua se chon cach de hon la them ten vao `skip`.
       Doc tu <link> thi no tu dung mai mai.
    """
    return re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="(css/[^"]+)"', rd(rel_html))


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
# ⚠️ DANH SACH CSS SUY TU CHINH THE <link> CUA TRANG (page_css), KHONG GAN CUNG.
#    Truoc 09/08/2026 muc nay gan cung ["common","page-shell","<trang>"] — dung cai
#    anti-pattern ma docstring cua `page_css()` da dat ten tu 31/07 nhung chi moi ap
#    cho mission-earth.html. Hau qua that: them css/locks.css vao missions.html la
#    phep kiem bao "thieu CSS: ['lk-badge']" trong khi trang nap dung file. Doc tu
#    <link> thi them stylesheet KHONG BAO GIO phai sua phep kiem nua.
for page in ("profile.html",
             "achievements.html",
             # missions.html them 29/07/2026 — cung khuon page-shell nen soi
             # duoc bang dung bo phep kiem nay, khong phai viet rieng.
             "missions.html",
             # codex.html them 30/07/2026 — cung khuon page-shell nen soi duoc
             # bang dung bo phep kiem nay (i18n vi/en khop · moi $("id") ton tai
             # · moi class co CSS · asset khong hong).
             "codex.html",
             # pricing.html them 09/08/2026 — trang Goi & Uu dai.
             "pricing.html",
             # parent.html them 09/08/2026 — bang theo doi cho bo me.
             "parent.html",
             # checkout.html them 11/08/2026 — trang thanh toan.
             "checkout.html",
             # Ba tang cua khu nhiem vu, them 12/08/2026 (`docs/decisions/008`):
             # ban do (chon NOI) → hanh tinh (chon NHIEM VU) → cay chang (chon CHANG).
             # Cung khuon page-shell nen soi duoc bang dung bo phep kiem nay.
             "mission-map.html",
             "mission-planet.html",
             "mission-tree.html",
             # crew.html them 16/08/2026 — Phi Hanh Doan Dau Tien (muc C3).
             "crew.html"):
    css = page_css(page)
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
        # Khoá ghép động HỢP LỆ — dự án ưu tiên khoá literal (xem `cat_*` ở
        # codex.html, `tier1..5` ở game-dodge), nhưng khi khoá do MỘT MẢNG DỮ LIỆU
        # sinh ra thì viết literal nghĩa là chép lại chính mảng đó. Danh sách này
        # phải HẸP: một mẫu quá rộng là phép kiểm thôi bắt được khoá gõ sai.
        DYN = {
            "missions.html": [r"^m_[a-z]+_(tag|name|desc)$"],
            # pricing.html: giá/so sánh/quyền lợi/ưu đãi/FAQ đều đổ từ PLANS, CMP,
            # WHO, PERKS, FAQ — xem chính các mảng đó trong trang.
            # parent.html: nhan chon tuan sinh tu vong lap `t("w_"+i)`, va tieu de
            # o so lieu doi theo tuan dang xem `t("sum_h"+WEEK)`.
            "parent.html": [r"^w_[0-9]$", r"^sum_h[0-9]$"],
            # checkout.html: ten goi / chu ky / trang thai don deu ghep tu du lieu
            # server tra ve (`t("pl_"+plan)`, `t("cyc_"+cycle)`, `t("st_"+status)`),
            # va bo loi bao loi tra qua bang `key` trong ham fail().
            "checkout.html": [r"^pl_(free|astro|crew|found)$",
                              r"^for_(free|astro|crew|found)$",
                              r"^cyc_(month|year|once)(_sub)?$",
                              r"^st_(paid|pending|failed|cancelled|expired)$",
                              r"^res_(failed|cancelled|expired)_[hp]$",
                              r"^err_[a-z]+$",
                              r"^term_(trial|cycle|once|cancel)$"],
            "pricing.html": [r"^pl_(free|astro|crew|found)_[nd]$",
                             r"^c_[a-z0-9]+$",
                             r"^w_[kp][0-9]+$",
                             r"^who_(kid|parent)$",
                             r"^p_[a-z]+$",
                             r"^q_[a-z]+$",
                             r"^badge_(popular|limited)$",
                             r"^st_(have|soon)$"],
        }
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
# ⚠️ Vai trang da tach logic ra file rieng, nen loi goi khong con nam trong HTML.
#    Khai RO file phu o day thay vi quet bua moi js/*.js trang nap: `js/progress.js`
#    co dinh nghia `missionStep` nen quet bua la phep kiem tu dat (trang nao nap
#    progress.js cung "co goi missionStep").
EXTRA_SRC = {"mission-earth.html": ["js/mission-engine.js", "js/mission-stage.js"]}
for page, (call, dep) in WIRED.items():
    html = rd(page)
    src = html + "".join(rd(f) for f in EXTRA_SRC.get(page, []))
    check(f"{page}: co goi {call}…", call in src)
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
# ⚠️ QUET CA `js/mission-engine.js` (tach ra 31/07/2026): phan cong don thuong da
#    chuyen sang do. Chi quet HTML thi ba phep kiem duoi day tu dat ma khong con
#    canh gi — dung loai "phep kiem con xanh vi nhin nham cho".
_me_src = me + rd("js/mission-engine.js") + rd("js/mission-stage.js")
_bad = [k for k in ("addAsteroids", "Economy.add") if k in _me_src]
# `reward.meteors += r.data.awarded` là ĐÚNG — cộng đúng con số SERVER trả về.
# Chỉ sai khi cộng một số viết cứng.
_bad += _re.findall(r"reward\.(?:meteors|xp|codex)\s*\+?=\s*[0-9]", _me_src)
check("mission-earth.html KHONG tu cong tt/XP bang so viet cung", not _bad, str(_bad))
check("mission-earth.html chi doc thuong tu phan hoi server",
      "r.data.awarded" in _me_src and "r.data.xpGained" in _me_src)
_mv = _re.search(r"missionStep\(([^)]*)\)", _me_src)
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
# ⚠️ Markup man tong ket nay do `js/mission-stage.js` DUNG (tach 15/08/2026), khong
#    con viet trong HTML. Doi phep kiem sang soi dung cho — de nguyen la no bao hong
#    dung luc san pham lam dung, dung loai loi "phep kiem bao ve trang thai cu".
_stage_src = rd("js/mission-stage.js")
check("man tong ket co khoi 'viec tiep theo' dan di duoc THAT",
      "win-missions" in _stage_src and "missions.html" in _stage_src)
check("nut viec tiep theo KHONG bi disabled (missions.html co that)",
      not _re.search(r"win-missions\"\)\.disabled\s*=\s*true", _stage_src)
      and 'id="win-missions"' in _stage_src
      and 'id="win-missions" disabled' not in _stage_src)
for k in ("win_next_k", "win_next", "win_missions"):
    check(f"mission-earth.html: khoa i18n `{k}` co o CA vi va en",
          me.count(k + ":") == 2, f"{me.count(k + ':')} lan")

# ══════════════════════════════════════════════════════════════
print("\n=== [3c] Nhiem Vu 01: buoc khop server + codex + i18n ===")
# Ba chỗ phải nói cùng một câu chuyện, và không chỗ nào suy ra được từ chỗ kia:
#   · Missions.cs   : có những bước nào, thứ tự chơi, mẫu codex nào mở ở bước nào
#   · mission-earth.html : STEP_IDS (thứ tự thật khi chơi)
#   · earth_codex.json   : nội dung đọc của từng mẫu codex
# Lệch nhau thì lỗi rất khó thấy: bước client gửi mà server không biết → `counted:false`
# nên KHÔNG có thưởng và cũng KHÔNG có lỗi nào hiện ra.
mi_cs = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"),
                encoding="utf-8").read()
# ══════════════════ MOI NHIEM VU, KHONG CHI NHIEM VU 01 ══════════════════
# WARN Truoc 15/08/2026 khoi nay cat rieng `new("earth", "earth",` roi chi soi
#   `mission-earth.html` + `earth_codex.json`. Khi Trai Dat co nhiem vu thu hai
#   ("orbit"), nhiem vu do khong co MOT phep kiem nao: STEP_IDS lech thu tu, thieu
#   object xu ly cho mot chang, hay thieu bai doc codex deu la LOI IM LANG — chang
#   client gui ma server khong biet thi tra `counted:false`, tuc KHONG thuong va
#   cung KHONG bao loi. Nay lap qua tung nhiem vu server khai.
_sv_missions = _re.findall(
    r'new\("([a-z0-9-]+)", "([a-z0-9-]+)",\s*\[(.*?)\],\s*DoneMeteors', mi_cs, _re.S)
check("doc duoc it nhat 1 nhiem vu tu Missions.cs", len(_sv_missions) >= 1,
      str([m[0] for m in _sv_missions]))

# Ban do id nhiem vu -> trang choi, lay tu danh muc client (chỗ DUY NHAT khai `file`)
_cat_raw = strip_comments(rd("js/mission-catalog.js"))
_cat_file = dict(_re.findall(r'id: "([a-z0-9-]+)", world: "[a-z0-9-]+", file: "([^"]+)"',
                             _cat_raw))

for _mid, _place, _body in _sv_missions:
    _steps = _re.findall(r'new\("([a-z0-9-]+)",\s*\d+,\s*\d+,\s*(null|"[a-z0-9,-]+")\)', _body)
    _ids = [x[0] for x in _steps]
    _pg = _cat_file.get(_mid)
    check(f"[{_mid}] co trang choi khai trong danh muc", bool(_pg), str(_cat_file))
    if not _pg or not os.path.exists(os.path.join(ROOT, _pg)):
        check(f"[{_mid}] trang choi ton tai tren dia", False, str(_pg))
        continue
    _psrc = rd(_pg)

    _cl = _re.search(r"const STEP_IDS = \[([^\]]*)\]", _psrc)
    _clids = _re.findall(r"'([a-z0-9-]+)'", _cl.group(1)) if _cl else []
    check(f"[{_mid}] STEP_IDS cua trang KHOP dung thu tu voi Missions.cs",
          _ids == _clids, f"server={_ids} client={_clids}")
    check(f"[{_mid}] doc duoc danh sach buoc", len(_ids) >= 4, str(len(_ids)))
    check(f"[{_mid}] moi buoc co object xu ly trong trang",
          all(_re.search(r"^  " + _s + r": \{", _psrc, _re.M) for _s in _ids),
          str([_s for _s in _ids if not _re.search(r"^  " + _s + r": \{", _psrc, _re.M)]))

    # WARN 5 CHANG LA MAC DINH TU NHIEM VU 02 TRO DI (chu du an chot 15/08/2026).
    #   Nhiem vu 01 GIU 7 chang co chu dich: doi so chang cua no la pha tuong thich —
    #   ban ghi `missions.earth.<buoc>` trong DynamoDB dung chinh id buoc, nguoi da
    #   choi xong se thay nhiem vu tu chuyen ve "chua hoan thanh". Them nhiem vu MOI
    #   thi khong co cai gia do. Day la mot QUYET DINH SAN PHAM, nen no co phep kiem.
    if _mid != "earth":
        check(f"[{_mid}] dung 5 chang (mac dinh tu nhiem vu 02 tro di)",
              len(_ids) == 5, f"{len(_ids)} chang: {_ids}")

    # Mau codex server khai ↔ bai doc. Moi nhiem vu MOT file `<id>_codex.json`.
    _svcx = []
    for _x in _steps:
        if _x[1] != "null":
            _svcx += _x[1].strip('"').split(",")
    _cxp = "learningdata/astronomy/%s_codex.json" % _mid
    if not os.path.exists(os.path.join(ROOT, _cxp)):
        check(f"[{_mid}] co file bai doc codex {_cxp}", not _svcx,
              f"server khai {len(_svcx)} mau ma khong co file")
        continue
    _cx = json.loads(rd(_cxp))
    _cxids = [e["id"] for e in _cx["entries"]]
    check(f"[{_mid}] moi mau codex server khai deu co bai doc",
          set(_svcx) <= set(_cxids), str(sorted(set(_svcx) - set(_cxids))))
    check(f"[{_mid}] {_cxp} khong co bai doc la",
          set(_cxids) <= set(_svcx), str(sorted(set(_cxids) - set(_svcx))))
    check(f"[{_mid}] `count` khop so entry",
          _cx["count"] == len(_cxids), f'count={_cx["count"]} entries={len(_cxids)}')
    # WARN THEM 02/08/2026 — LOI THAT DA XAY RA. Bo buoc `rotation` lam mat mot entry
    #   codex, nhung `codexTotal` o trang van la 9, nen man tong ket ghi "8/9 mau du
    #   lieu": noi voi tre rang no bo sot mot mau KHONG TON TAI, o dung man khen thuong.
    _ct = _re.search(r"codexTotal:\s*(\d+)", _psrc)
    check(f"[{_mid}] `codexTotal` du phong khop so entry codex",
          bool(_ct) and int(_ct.group(1)) == len(_cxids),
          f'codexTotal={_ct.group(1) if _ct else "?"} entries={len(_cxids)}')
    check(f"[{_mid}] moi entry codex co tieu de vi+en",
          all(e.get("title", {}).get("vi") and e.get("title", {}).get("en")
              for e in _cx["entries"]),
          str([e["id"] for e in _cx["entries"] if not e.get("title", {}).get("en")]))
    check(f"[{_mid}] moi entry codex co nguon tham chieu",
          all(e.get("source_reference", {}).get("url") for e in _cx["entries"]),
          str([e["id"] for e in _cx["entries"]
               if not e.get("source_reference", {}).get("url")]))
    # Noi dung chua qua ra soat chuyen mon thi phai TU KHAI, y như learningdata/README.md
    check(f"[{_mid}] moi entry codex tu khai da qua ra soat chua",
          all("reviewed_by_teacher" in e for e in _cx["entries"]),
          str([e["id"] for e in _cx["entries"] if "reviewed_by_teacher" not in e]))

# --- Rieng Nhiem vu 01: buoc `rotation` da bo han (docs/decisions/005) ---
_earth_ids = next((([x[0] for x in _re.findall(
    r'new\("([a-z0-9-]+)",\s*\d+,\s*\d+,', b)]) for i2, p2, b in _sv_missions
    if i2 == "earth"), [])
check("KHONG con buoc `rotation` (bo 02/08/2026, docs/decisions/005)",
      "rotation" not in _earth_ids, str(_earth_ids))
sv_ids = _earth_ids

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
# ⚠️ CONG CA ID DO VO DUNG RA. `js/mission-stage.js` chen header / bang muc tieu /
#    box thoai / the noi dung / man cho / man tong ket / hop hoi / toast luc chay, nen
#    chung KHONG co trong HTML tinh. Chi doc HTML thi phep kiem bao thieu oan.
_me_ids = ids_in(me) | ids_in(rd("js/mission-stage.js"))
# ⚠️ QUET TREN MA DA BOC CHU THICH. Bay "dem ca chu trong ghi chu cua chinh minh" da
#    lap lai ~18 lan trong du an nay: mot dong ghi chu viet `$('id')` de GIAI THICH
#    luat la du lam phep kiem bao thieu mot id ten "id". Sua o BO KIEM, dung viet lai
#    ghi chu de ne.
_me_refs = set(_re.findall(r"\$\('([^']+)'\)", strip_js(_me_js)))
check("mission-earth.html: moi $('id') deu ton tai",
      _me_refs <= _me_ids, f"thieu: {sorted(_me_refs - _me_ids)}")
# Class dùng trong markup phải có CSS (bốn bảng kéo-thả mới dễ quên khai)
_me_css = css_classes(*page_css("mission-earth.html"))
_me_used = used_classes(me)
_me_skip = {"sr-only", "nebula", "starfield", "toast", "modal", "lic", "tt-inline", "hit"}
check("mission-earth.html: moi class deu co CSS",
      not sorted(_me_used - _me_css - _me_skip),
      f"thieu CSS: {sorted(_me_used - _me_css - _me_skip)}")

# ══════════════════════════════════════════════════════════════
print("\n=== [3f] Buoc (5) `life`: LAT CAT TRAI DAT — ngan sach khuon + 2 nguon ===")
# Chot 02/08/2026, `docs/decisions/006`. Muc nay canh dung MOT thu: buoc (5) khong duoc
# quay ve dung lai mot khuon DA DAY. Do la ly do no bi viet lai, va la loai loi doc code
# khong thay — chi thay khi chieu lai quyet dinh roi DEM.
_me_code_f = strip_comments(me)

# --- (1) NGAN SACH KHUON — dem loi goi HAM, khong dem cam nhan ---
# ⚠️ `docs/decisions/002` dong 120: mot nhiem vu khong dung cung mot khuon qua 2 lan.
#    Hai engine keo-tha va cau do DA DAY o (4)(6) va (1)(3). Buoc (5) vi the phai co ma
#    rieng (~90 dong khong dung lai duoc). Neu ai do "don dep" bang cach cho no dung lai
#    mot trong hai thi con so duoi day len 3 va muc nay bao hong — dung luc do.
_n_drag = len(_re.findall(r"\bdragDrop\(\{", _me_code_f))
_n_ask = len(_re.findall(r"\bbuildAsk\(\{", _me_code_f))
check("dragDrop dung DUNG 2 lan (4 energy + 6 eco), khong hon", _n_drag == 2, _n_drag)
check("buildAsk dung DUNG 2 lan (1 scan + 3 sun), khong hon", _n_ask == 2, _n_ask)

# --- (2) Buoc (5) khong con cham marker de mo the ---
# ⚠️ Marker VAN GIU va camera VAN BAY TOI: tre phai thay noi do nam dau tren anh ve tinh
#    thi cau hoi do cao moi co can cu. Chi cu BAM la doi xuong cot. Neu `steps.life` co
#    lai ham `pick` thi co nguoi da dung lai signal_scan lan thu 3.
_life_blk = _re.search(r"\n  life: \{(.*?)\n  \},", _me_code_f, _re.S)
check("doc duoc khoi `steps.life`", _life_blk is not None)
if _life_blk:
    _lb = _life_blk.group(1)
    check("buoc (5) KHONG con ham pick() (khong cham marker de mo the)",
          not _re.search(r"\n\s+(async\s+)?pick\s*\(", _lb))
    check("buoc (5) co onRung() — tre chon nac tren lat cat", "onRung" in _lb)
    check("buoc (5) van goi focusMarker (camera van bay toi toa do that)",
          "focusMarker" in _lb)

# --- (3) Thu tu di tham KHONG don dieu ---
# ⚠️ Neu rank theo `LIFE_ORDER` tang hoac giam dan thi sau hai noi dau tre doan duoc not
#    bang quy luat "cai sau cao hon cai truoc", va cu bat ngo o Nam Cuc mat sach.
_ord = _re.search(r"const LIFE_ORDER = \[(.*?)\];", _me_code_f, _re.S)
_rk = dict(_re.findall(r"\{ id: '(\w+)',.*?rank: (\d)", _me_code_f))
check("doc duoc LIFE_ORDER va rank cua 4 noi", bool(_ord) and len(_rk) == 4, _rk)
if _ord and len(_rk) == 4:
    _seq = [int(_rk[x]) for x in _re.findall(r"'(\w+)'", _ord.group(1))]
    _mono = (all(a < b for a, b in zip(_seq, _seq[1:]))
             or all(a > b for a, b in zip(_seq, _seq[1:])))
    check("thu tu di tham KHONG don dieu (khong doan duoc bang quy luat)", not _mono, _seq)
    check("4 noi phu du 4 nac 1..4", sorted(_seq) == [1, 2, 3, 4], _seq)

# --- (4) HAI CON SO CO NGUON, va khong noi rong hon nguon ---
# ⚠️ NASA noi NGUYEN VAN "up to 4,000 meters above sea level" cho Nam Cuc. Trang do
#    KHONG noi "Nam Cuc la chau luc cao nhat" — cac trang pho thong deu noi the va con so
#    trung binh moi nguon mot khac (2.200 / 2.300 / 2.500 m). Da doc lai toan trang.
check("cau Nam Cuc dung con so NASA 4.000 m", "4.000 m" in _me_code_f)
check("cau day dai duong dung con so NOAA 3.682 m", "3.682" in _me_code_f)
# ⚠️ NOAA noi ve DAI DUONG NOI CHUNG, khong rieng Dai Tay Duong — gan con so cho rieng
#    Dai Tay Duong la dan nguon cho mot cau nguon khong noi.
_alt_w = _re.search(r"id: 'water'.*?alt: \{ vi: '([^']*)'", _me_code_f, _re.S)
check("KHONG gan con so NOAA cho rieng Dai Tay Duong",
      bool(_alt_w) and "3.682" in _alt_w.group(1)
      and "Đại Tây Dương" not in _alt_w.group(1),
      _alt_w and _alt_w.group(1)[:60])

# --- (5) Nhan 4 nac KHONG goi ten dia hinh ---
# ⚠️ Ban nhap dau dung ten dia hinh ("dinh nui", "day bien") va no TU TRA LOI HO tre:
#    "Himalaya -> dinh nui" thi khong con gi de nghi. Nhan theo DAI DO CAO thi Nam Cuc
#    moi thanh cau hoi that — va Nam Cuc la ca duy nhat dang hoi trong bon noi nay.
_rl = [_re.search(r"rung_%d: '([^']*)'" % k, _me_code_f) for k in (1, 2, 3, 4)]
check("doc duoc 4 nhan nac", all(_rl))
if all(_rl):
    _j = " ".join(m.group(1).lower() for m in _rl)
    check("nhan 4 nac KHONG goi ten dia hinh (nui / day bien / cao nguyen / rung)",
          not any(w in _j for w in ("núi", "đáy biển",
                                    "cao nguyên", "rừng")), _j[:70])
    check("ca 4 nhan deu neo vao 'muc nuoc bien'",
          _j.count("mực nước biển") == 4, _j[:70])

print("\n=== [3g] Nhiem Vu 01 - 3 loi choi that 03/08/2026 (`docs/decisions/007`) ===")
# Ba loi chu du an bat duoc khi choi that. Ca ba deu "hien ra dung nhu binh thuong" nen
# doc code khong thay - chi thay khi chieu lai chinh cai quyet dinh da chot.
_e2 = strip_comments(rd("js/earth2d.js"))
_me3g = strip_comments(me + rd("js/mission-stage.js"))
_css3g = strip_comments(rd("css/mission-stage.css") + rd("css/mission-earth.css"))

# --- (1) DIA MAT TROI: rac con sot cua mot quyet dinh da chot tu 02/08 ---
# WARN Loi thoai buoc 3 da viet lai tu 02/08/2026 de noi ro Mat Troi KHONG nam tren tam
#   ban do (co phep kiem o muc [3e]), va chinh chu thich cua phep kiem do ghi "sau khi
#   bo nut `.e2-sun`" - nhung THE DOM thi khong ai xoa. Nen no van ve mot dia sang mo o
#   goc tren-phai trong MOI buoc, va chu du an hoi lai: "van con hinh mat troi o day?
#   bo di". Cung ho voi `.e2-terminator` va vanh tron cu cua `.e2-shield`.
check("KHONG con dung `.e2-sun` trong js/earth2d.js (bo han 03/08/2026)",
      "e2-sun" not in _e2)
check("KHONG con rule `.e2-sun` trong CSS", "e2-sun" not in _css3g)
# WARN Hai cho nay tung song sot sau khi bien `sun` bi xoa - mot ReferenceError NAM CHO
#   nguoi goi dau tien, va cai thu nhat thi giet ca trang ngay luc dung canh.
check("KHONG con `sun.addEventListener` (ReferenceError giet ca trang)",
      "sun.addEventListener" not in _e2)
check("KHONG con nhanh `screenOf('sun')` tro vao bien da xoa",
      'kind === "sun"' not in _e2 and "kind === 'sun'" not in _e2)
check("KHONG con `pick({type:'sun'})` o trang nhiem vu",
      "type: 'sun'" not in _me3g and 'type:"sun"' not in _me3g)
# `igniteSun`/`dimSun` PHAI con - bai hoc buoc 3 nam o do (ca ban do toi di roi sang lai)
check("VAN con `igniteSun`/`dimSun` (bai hoc buoc 3 khong bi bo theo)",
      "igniteSun" in _e2 and "dimSun" in _e2)
check("`igniteSun`/`dimSun` van doi `.e2-night`", _e2.count("e2-night") >= 4)

# --- (2) BAN TAY phai DI THEO TRE, khong theo thu tu khai bao ---
# WARN Hai luat DUNG nhung NGUOC NHAU tung nam canh nhau: thiet ke cho "cham dom nao
#   truoc cung duoc" (`004`), nhung ban tay lai chi vao dom DAU TIEN CHUA CHAM theo thu
#   tu khai bao. Tre cham tu giua ra thi dom so 0 chua cham mai va tay DUNG NGUYEN mot
#   cho suot nhieu cu cham lien - tai hien duoc: 5 cu cham lien, tay khong nhich 1 pixel.
check("`nextLeft` nhan `fromId` (dom vua cham) chu khong chi (list, gotIds)",
      "function nextLeft(list, gotIds, fromId)" in _me3g)
check("buoc 1 truyen dom VUA CHAM vao `nextLeft`",
      "nextLeft(CONTINENTS, this.gotIds, p.id)" in _me3g)
check("buoc 3 truyen dom VUA CHAM vao `nextLeft`",
      "nextLeft(ZONES, this.got, z.id)" in _me3g)
# WARN `dlon` phai goi ve +-180: khong goi thi `oceania`(135) va `namerica`(-100) do ra
#   235 do trong khi duong that qua Thai Binh Duong chi 125 do - tay se chi sai dom.
check("do khoang cach co GOI kinh do ve +-180 (khong thi chon sai dom gan nhat)",
      "360 - d : d" in _me3g)
# WARN Khong co be mat nay thi phep kiem chi do duoc *co ban tay hay khong*, chu khong do
#   duoc no chi vao DUNG dom nao - ma loi vua sua la ban tay hien ro rang, chi la sai cho.
check("co be mat test `__mission.handTarget` de do ban tay chi vao DAU",
      "get handTarget()" in _me3g)

# --- (3) THE NOI DUNG khong duoc chong len BANG DAY ---
# WARN The la role=dialog aria-modal=true nhung nam TRUOC moi `.me-board` trong DOM va ca
#   hai deu khong khai z-index -> bang ve DE LEN the. Nut "Da hieu!" bi cat mat nua duoi,
#   ma do la duong DUY NHAT dong the (moc tu dong 3,4 giay da bo 02/08/2026).
check("`.me-card` co z-index cao hon `.me-board`", "z-index:20" in _css3g)
check("co class `.me-card.lift` canh giua phan khung con lai", ".me-card.lift{" in _css3g)
check("`.me-card.lift` dung lai bien `--board-h` cua `.me-say.lift` (mot co che)",
      _css3g.count("--board-h") >= 2)
# WARN San `max(..., 8px)`: tren dien thoai doc bang lat cat chiem phan lon khung, khong
#   co san thi `top` ra so AM va the troi len ngoai mep tren, tieu de bi cat.
check("`.me-card.lift` co SAN 8px (khong de `top` ra so am tren dien thoai doc)",
      "max(8px" in _css3g)
check("`liftCard()` do chieu cao bang NGAY LUC MO THE (bang cao dan theo so the xep)",
      "function liftCard()" in _me3g and ".me-board.show" in _me3g)
# WARN Phai do TRONG than `showCard`, khong do tren ca file: `classList.add('show')` xuat
#   hien o ca chuc cho khac (bang muc tieu, cac `.me-board`...) nen `index()` tren ca file
#   se bat dung cai dau tien va bao hong oan. Ban dau tien cua phep kiem nay hong dung
#   vi ly do do.
# WARN Vo viet theo loi ES5 (nhay KEP), trang nhiem vu viet nhay DON. Ghim mot kieu
#   nhay la phep kiem bao hong khi ma chuyen file ma khong doi mot chut hanh vi nao —
#   dung loai "phep kiem bao ve dinh dang thay vi bao ve hanh vi". Chuan hoa truoc.
_sc = _me3g.split("function showCard(", 1)[1].split(chr(10) + "function ", 1)[0]
_sc = _sc.replace('"', "'")
check("`showCard` goi `liftCard()` TRUOC khi hien the",
      "liftCard();" in _sc and
      _sc.index("liftCard();") < _sc.index("classList.add('show')"))

print("\n=== [3e] Nhiem Vu 01 sau `005`: 0 vung toi · 0 qua cau · noi dung co nguon ===")
# Chot 02/08/2026, `docs/decisions/005`. Muc nay canh nhung RANG BUOC "tu nay" cua no —
# thu ma doc code khong thay sai, chi thay sai khi chieu lai quyet dinh.
_me_code = strip_comments(me)          # bo ghi chu: chinh chu thich GIAI THICH vi sao
# WARN CSS CANH (`.e2-*`) DA TACH SANG `css/earth2d.css` ngay 15/08/2026 — canh ban
#   do khong thuoc rieng Nhiem vu 01; nhiem vu thu hai dien ra tren dung tam ban do
#   do. Doc CA HAI file: chi doc mot la nhung phep kiem duoi day bao hong dung luc
#   ma nguon dang dung.
_me_css_raw = strip_comments(rd("css/mission-earth.css")) + rd("css/earth2d.css")

# --- (1) KHONG con vung toi nao tren ban do phang ---
# ⚠️ Chu du an choi that roi BAC bang anh chup: gradient `.e2-terminator` trong nhu mot
#    buc tuong den. Bai hoc ngay/dem da chuyen sang qua cau 3D o explorer.html.
_me_css_bare = strip_comments(_me_css_raw)
check("KHONG con `.e2-terminator` trong CSS (bo han, 005 muc 2)",
      "e2-terminator" not in _me_css_bare)
check("KHONG con `.e2-terminator` trong mission-earth.html",
      "e2-terminator" not in _me_code)
check("KHONG con `.e2-view::after` (gradient vung toi mac dinh)",
      "e2-view::after" not in _me_css_bare)
# `.e2-night` thi GIU — ca hanh tinh toi di vi Mat Troi chua chay, khac han mot dai
# toi vat ngang ban do. Doi nham hai thu nay la bo mat khoanh khac cua buoc ③.
check("`.e2-night` VAN con (mat nang khac han vung toi)", "e2-night" in _me_css_raw)

# --- (1b) Lop ban do phang phai CAN GIUA, khong duoc neo mep trai ---
# ⚠️ LOI CO SAN, sua 02/08/2026. `inset:0 + margin:auto + width` la QUA RANG BUOC, va CSS
#    xu hai truc khac nhau: truc doc chia deu margin (can giua), truc ngang o `ltr` thi
#    BO QUA `right` nen lop neo MEP TRAI. Hai hau qua: diem o `facing` roi vao 62,5% be
#    rong khung (lech 36° tren 1440×900), va — nang hon — **moi kinh do dong hon ~83°
#    KHONG THE dua vao khung tren dien thoai doc**, vi marker chi ve tren ban anh THAT.
#    Tuc day Himalaya (lon 87) cua buoc ⑤ `life` chua bao gio nhin thay duoc tren may
#    tinh bang doc. Phep kiem nay de khong ai vo tinh go ba thuoc tinh do ra.
_flat_layer = re.search(r"\.e2\.e2-flat \.e2-layer\{([^}]*)\}", _me_css_raw)
check("lop ban do phang CAN GIUA (khong neo mep trai)",
      bool(_flat_layer) and "left:50%" in _flat_layer.group(1)
      and "right:auto" in _flat_layer.group(1)
      and "margin-left:" in _flat_layer.group(1),
      str(_flat_layer and _flat_layer.group(1))[:120])
# `centerOn` khong duoc mang lai so hang bu cua thoi neo-mep-trai.
_e2 = rd("js/earth2d.js")
check("js/earth2d.js co `centerOn`", "centerOn: function" in _e2)
# ⚠️ LOI CO SAN THU HAI, sua 02/08/2026. `.e2-layer` doi CO theo che do ban do (qua cau
#    `min(100vw,100vh)` vs phang `max(50vw,100vh)`), nhung `measure()` chi chay MOT LAN
#    luc dung (khi map con la `globe`) va khi `resize` — nen `lyH` giu mai chieu cao cua
#    anh QUA CAU. Tren 1440×900 hai so trung nhau (900) nen khong ai thay; tren dien
#    thoai doc 390×844 thi lech 390 vs 844 → `maxPyPct()` ra 0 → phep dich DOC bi kep ve
#    0 → **khong dua duoc vi do cao vao khung**. Do duoc: Nam Cuc (lat −75) o `dist:3,1`
#    roi xuong y = 921 tren khung cao 844. `probe_map_cover` KHONG bat duoc vi kep py ve
#    0 lam MAT kha nang dich doc chu khong lam HO khung.
check("setMap() do lai bo cuc (lop doi co theo che do ban do)",
      re.search(r'stage\.classList\.toggle\("e2-flat"[^\n]*\);(?:[^}]*?)\bmeasure\(\);',
                strip_comments(_e2), re.S) is not None)
check("centerOn KHONG con so hang bu `180 * vpW / lyW` (chi con z*lon)",
      "180 * vpW / lyW" not in strip_comments(_e2))

# --- (2) Nhiem vu KHONG BAO GIO dung anh qua cau ---
check("KHONG goi setMap('globe') o trang nhiem vu (qua cau chi o explorer.html)",
      "setMap('globe')" not in _me_code and 'setMap("globe")' not in _me_code)
_setmaps = re.findall(r"setMap\('(\w+)'\)", _me_code)
check("moi loi goi setMap deu la 'flat'", set(_setmaps) == {"flat"}, str(sorted(set(_setmaps))))
# `setMap` la trang thai THUA HUONG — buoc nao khong khai thi nhan map cua buoc truoc,
# ma buoc truoc doi luc nao cung duoc. Doi MOI buoc tu khai.
check("moi buoc deu khai setMap tuong minh", len(_setmaps) >= len(sv_ids),
      f"{len(_setmaps)} loi goi / {len(sv_ids)} buoc")

# --- (3) Buoc ① — 7 chau luc + cau do bien/dat ---
_ct_blk = re.search(r"const CONTINENTS = \[(.*?)\n\];", me, re.S)
_ct_ids = re.findall(r"id: '([a-z]+)'", _ct_blk.group(1)) if _ct_blk else []
check("buoc ①: co dung 7 chau luc", len(_ct_ids) == 7, str(_ct_ids))
check("buoc ①: moi chau luc co ten vi+en",
      _ct_blk is not None and len(re.findall(r"nm: \{ vi:", _ct_blk.group(1))) == 7 and
      len(re.findall(r"en: '", _ct_blk.group(1))) >= 7)
check("buoc ①: KHONG con ba dom `SCAN_POINTS` cu", "SCAN_POINTS" not in _me_code)
for _k in ("s1_ask_q", "s1_ask_water", "s1_ask_land", "s1_ans_fact",
           "s1_ans_right", "s1_ans_wrong"):
    check(f"buoc ①: khoa cau do '{_k}' co o CA vi va en", _k in _vi and _k in _en)
# ⚠️ 71%, KHONG phai 70% — cung mot nhiem vu tung noi hai con so cho mot su that
#    (`004` da phai di sua 5 cho). Va "29%" luon phai duoc goi la PHAN CON LAI.
check("buoc ①: dap an noi 71% (khong phai 70%)",
      "71%" in _me_code and "70% bề mặt" not in _me_code)
check("buoc ①: dap an goi 29% la PHAN CON LAI (khong gan cho NASA)",
      "phần còn lại" in _me_code and "the rest" in _me_code)
# Doan sai KHONG phat: ca hai nhanh deu di tiep, khong co trang thai thua.
check("buoc ①: doan sai KHONG phat (ca hai nhanh cung goi finishStep)",
      "s1_ans_wrong" in _me_code and re.search(r"onAnswer\(pick\)", _me_code) is not None)

# --- (4) Buoc ② — 5 moc, moi con so co nguon ---
_er = re.search(r"const ERAS = \[(.*?)\n\];", me, re.S)
_er_ids = re.findall(r"id: '([a-z]+)'", _er.group(1)) if _er else []
check("buoc ②: co dung 5 moc", len(_er_ids) == 5, str(_er_ids))
check("buoc ②: co moc `life` (lap 92% lich su ma ban 4 moc nhay qua)",
      "life" in _er_ids, str(_er_ids))
check("buoc ②: `era-life` co tong mau rieng trong CSS",
      "#stage.era-life" in _me_css_raw and ".me-era.era-life" in _me_css_raw)
# ⛔ BON CAI BAY cua `005`. Ba cai kiem duoc bang chu; cai thu tu (cay len can TRUOC)
#    kiem bang viec cau van phai nhac ca hai ky rieng ra.
# ⚠️ QUET TREN `_me_code` (DA BOC COMMENT), khong tren `me`. Chinh khoi chu thich cua
#    `ERAS`/`ZONES` LIET KE cac con so bi cam ("số 4,3 tỷ đã BỎ", "đừng viết 'vùng cực
#    lúc nào cũng nhận ít nắng hơn'") — quet van ban tho la cau canh bao bi tinh la vi
#    pham. Day la lan thu MUOI cung loai loi nay trong du an, va lan nay chinh phep
#    kiem moi viet ra da bao hong ngay lan chay dau.
check("bay 1: su song 3,8 ty — KHONG phai 3,7",
      "3,8 tỷ" in _me_code and "3,7 tỷ" not in _me_code)
check("bay 2: khung long 233 trieu — KHONG phai 230",
      "233 triệu" in _me_code and "230 triệu" not in _me_code)
check("bay 3: thu xuat hien CUNG THOI khung long, khong phai sau",
      "cũng xuất hiện đúng thời đó" in _me_code and "same period" in _me_code)
check("bay 4: cay len can (Silur) TRUOC, con vat (Devon) THEO SAU",
      all(s in _me_code for s in ("Silur", "Devon", "Silurian", "Devonian")))
check("buoc ②: dai duong 4,4 ty (zircon), KHONG con 3,8 ty cho dai duong",
      "4,4 tỷ" in _me_code and "4.4 billion" in _me_code)
check("buoc ②: KHONG dung so 4,3 ty (trang NASA doc duoc khong phat bieu no)",
      "4,3 tỷ" not in _me_code and "4.3 billion" not in _me_code)

# --- (4b) Tranh minh hoa (`005` muc ⑩ -> `006` diem 11, 02/08/2026) ---
# ⚠️ MOI MOC PHAI CO TRANH, ke ca "now". Truoc 02/08/2026 phep kiem nay DOI moc `now`
#    KHONG co tranh, va ly le nghe rat vung: thu trung thuc nhat dang nam ngay sau lung
#    bang — chinh buc anh ve tinh THAT. Ly le do van dung ve NOI DUNG, nhung chu du an
#    choi that va chi ra thu no bo qua: **4 moc co tranh roi moc thu 5 trong thi tre doc
#    ra nhu mot cho BI THIEU**, khong nhu mot quyet dinh. Phep kiem cu vi the dang BAO VE
#    dung cai bat nhat do — sua cho dung la no bao hong. Cung loai viec da lam voi nut
#    Mat Trang va 6 phep kiem cua `004`.
# ⚠️ DEM THEO `ERAS`, DUNG GAN CUNG TEN. Gan cung la them buc thu sau phai sua o day —
#    dung bai hoc `make_era_assets.py` vua mac (script do gan cung 4 ten nen im lang bo
#    qua `now.png` khi chu du an dat vao).
_era_ids = re.findall(r"\{ id: '(\w+)'", _er.group(1)) if _er else []
_era_imgs = re.findall(r"img: '(\w+)'", _er.group(1)) if _er else []
check("buoc ②: MOI moc deu co tranh (ke ca 'now')",
      len(_era_ids) >= 5 and _era_imgs == _era_ids,
      "ids=%s imgs=%s" % (_era_ids, _era_imgs))
for _n in _era_imgs:
    for _w in (700, 1120):
        for _ext in ("avif", "webp"):
            _f = f"img/era/{_n}-{_w}.{_ext}"
            check(f"co asset {_f}", os.path.exists(os.path.join(ROOT, _f)))
# ⛔ NHAN "MINH HOA" LA BAT BUOC: khong ton tai anh chup Trai Dat 4,5 ty / 4,4 ty /
#    3,8 ty / 233 trieu nam truoc. De tre tuong do la anh that la day mot dieu sai.
check("buoc ②: co nhan MINH HOA o ca vi va en",
      "era_illus" in _vi and "era_illus" in _en
      and "MINH HOẠ" in _me_code and "ARTIST" in _me_code.upper())
# Nhan o goc anh la thu trinh doc man hinh khong voi toi -> `alt` phai noi lai.
check("buoc ②: `alt` cung noi ro day la TRANH DUNG",
      "era_alt" in _vi and "era_alt" in _en
      and "Tranh minh hoạ" in _me_code and "Artist’s impression" in _me_code)
# ⚠️ Anh nap LUOI: mang yeu thi bai hoc van chay, chi thieu tranh.
check("buoc ②: anh nap luoi + giai ma bat dong bo",
      'loading="lazy"' in me and 'decoding="async"' in me)
# ⚠️ Khai cho trong TRUOC khi anh ve, khong thi ca bang nhay len mot nhip luc anh tai xong.
check("buoc ②: co khai cho trong cho anh (chan nhay bo cuc)",
      "aspect-ratio:3/2" in _me_css_raw and 'width="700"' in me)
# ⚠️ Ban goc 8,99 MB KHONG duoc commit; asset .avif/.webp thi PHAI duoc commit.
_gi = rd(".gitignore")
check("ban goc img/era/*.png bi chan khoi git", "img/era/*.png" in _gi)
check("KHONG chan ca thu muc img/era (asset phai vao git)",
      not re.search(r"^img/era/\s*$", _gi, re.M))
# ⚠️⚠️ HAI PHEP KIEM DUOI DAY CANH HAI LOI DA XAY RA THAT, do duoc bang Chromium:
# (a) `sizes` chi dat tren `<img>` → trong `<picture>` no KHONG ap cho `<source>`, nen
#     trinh duyet mac dinh 100vw va keo ban 1120 thay vi 700 — nang gap doi tren dung
#     nhom mang yeu ma viec nay sinh ra de phuc vu. Bang chung: `naturalWidth` bao 1440
#     cho mot file 1120×747.
check("buoc ②: `sizes` dat tren TUNG <source>, khong chi tren <img>",
      len(re.findall(r"<source[^>]*sizes=", me)) >= 2)
# (b) Anh rong het bang thi tren 1366×768 bang chiem 84,5% khung, chi con 30px ban do —
#     ma buoc nay doi TONG MAU ca hanh tinh, va `004` chot do la NOI DUNG bai hoc.
check("buoc ②: anh co tran be rong theo chieu cao khung (de con thay ban do)",
      re.search(r"\.era-fig\{[^}]*max-width:min\(100%,\s*\d+vh\)", _me_css_raw, re.S) is not None)

# --- (5) Buoc ③ — ba vung khi hau, va VI SAO ---
_zn = re.search(r"const ZONES = \[(.*?)\n\];", me, re.S)
_zn_ids = re.findall(r"id: '([a-z]+)'", _zn.group(1)) if _zn else []
check("buoc ③: co dung 3 vung khi hau", len(_zn_ids) == 3, str(_zn_ids))
check("buoc ③: du xich dao · on doi · cuc",
      set(_zn_ids) == {"equator", "temperate", "polar"}, str(sorted(_zn_ids)))
for _k in ("s2b_h", "s2b_p", "s2b_say1", "s2b_card", "s2b_say2"):
    check(f"buoc ③: khoa '{_k}' co o CA vi va en", _k in _vi and _k in _en)
# ⛔ QUAN NIEM SAI PHO BIEN NHAT ve chu de nay. Cau ket PHAI bac no ra mat chu khong
#    chi tranh khong nhac — tre den day voi san mot cach giai thich sai trong dau.
check("buoc ③: cau ket BAC HAN 'vi gan Mat Troi hon'",
      "Không phải</b> vì vùng cực ở xa Mặt Trời hơn" in _me_code and
      "not</b> because the poles are farther from the Sun" in _me_code)
check("buoc ③: giai thich bang GOC CHIEU",
      "góc chiếu" in _me_code and "angle" in _me_code)
# ⚠️ THEM 02/08/2026 — chu du an choi that: *"'ngoi sao dang len'? tre hieu rang Mat Troi
#    nam tren Trai Dat. Van vo ly."* Sau khi bo nut `.e2-sun`, thu tre THAT SU thay chi
#    la ban do toi di roi sang lai — khong co vat the Mat Troi nao hien ra. Loi thoai vi
#    the KHONG duoc mo ta mot cu "moc len", va PHAI noi ro Mat Troi o ngoai khong gian.
#    Cung mot ho voi loi *"keo de xoay Trai Dat"* ma `004` da di sua.
check("buoc ③: KHONG mo ta Mat Troi nhu dang MOC LEN tren ban do",
      "đang lên" not in _me_code and "is rising" not in _me_code)
check("buoc ③: noi ro Mat Troi o NGOAI KHONG GIAN, khong nam tren ban do",
      "không nằm trên tấm bản đồ này" in _me_code and "not on this map" in _me_code)
# ⚠️ THEM 02/08/2026 — chu du an chot: cu toi/sang phai la HE QUA cua mot viec tre vua
#    lam, khong phai hieu ung roi tu tren troi. Hai ban truoc deu hong o cho nay (bat di
#    TIM nut Mat Troi khong the tim ra · roi "ngoi sao dang len" ma khong co gi hien ra).
check("buoc ③: tre TU DOAN truoc, roi moi tat Mat Troi",
      "s2_ask_q" in _vi and "onAnswer" in _me_code
      and _me_code.index("buildAsk({\n        k: t('s2_ask_k')") < _me_code.index("dimSun"))
# CA BA lua chon deu dung — khong co nhanh "doan sai" o mot buoc dang day kien thuc moi.
for _k in ("s2_opt_cold", "s2_opt_plant", "s2_opt_rain",
           "s2_role_heat", "s2_role_plant", "s2_role_rain", "s2_ans"):
    check(f"buoc ③: khoa '{_k}' co o CA vi va en", _k in _vi and _k in _en)
check("buoc ③: day du BA vai tro cua Mat Troi (nhiet · quang hop · vong tuan hoan nuoc)",
      "thể lỏng" in _me_code and "chuỗi thức ăn" in _me_code
      and "vòng tuần hoàn của nước" in _me_code)
# Buoc ③ KHONG duoc phat bieu ve tong nang luong ca nam: chinh trang NASA dang dan
# viet rang vi do cao vao mua he nhan nhieu nang luong hon TRONG MOT NGAY.
check("buoc ③: KHONG phat bieu 'vung cuc luc nao cung nhan it nang luong hon'",
      "lúc nào cũng nhận ít" not in _me_code and "always receives less" not in _me_code)

# --- (5b) Buoc ④ — ba nha may NEO TREN BAN DO, khong nam trong bang ---
# Chu du an: *"nen rai 3 ong khoi tai 3 vung khac nhau len ban do 2D de tre keo nang
# luong xanh vao. Truoc khi keo thi hinh anh trai dat tai cac vung do bi mo, sau khi keo
# thi sang lai."*
_st = re.search(r"const STACKS = \[(.*?)\n\];", me, re.S)
_st_ids = re.findall(r"id: '(\w+)'", _st.group(1)) if _st else []
check("buoc ④: 3 nha may co TOA DO THAT (khong con la 3 o trong bang)",
      len(_st_ids) == 3 and _st.group(1).count("lat:") == 3 and _st.group(1).count("lon:") == 3,
      str(_st_ids))
# ⚠️ Keo-tha doi khay the VA o dich cung nam tren man hinh mot luc, ma man doc 390×844
#    o san phong chi thay ~83° kinh do. Ba nha may trai qua rong la KHONG KEO DUOC.
_st_lons = [int(x) for x in re.findall(r"lon:\s*(-?\d+)", _st.group(1))] if _st else []
check("buoc ④: 3 nha may trai duoi 83° kinh do (khong thi man doc khong keo-tha duoc)",
      bool(_st_lons) and (max(_st_lons) - min(_st_lons)) < 83,
      f"trai {max(_st_lons) - min(_st_lons) if _st_lons else '?'}°")
check("buoc ④: nha may la MARKER cua canh (paint() lo vi tri + chong-phong)",
      "cls: 'e2-stack'" in _me_code and "e2-stack" in _me_css_raw)
check("buoc ④: vung quanh nha may BI MO, va SANG LAI khi da thay nguon",
      re.search(r"\.e2-mk\.e2-stack\{[^}]*box-shadow[^}]*\}", _me_css_raw, re.S) is not None
      and re.search(r"\.e2-mk\.e2-stack\.ok\{[^}]*box-shadow", _me_css_raw, re.S) is not None)
# ⚠️ Co y KHONG gan ten dia danh nao cho nha may: "cho nay o nhiem" la phat bieu ve the
#    gioi that ma du an khong co nguon de dung sau, va khong nen dat vao mieng mot nhan
#    vat cho tre em. `STACKS` vi the chi co id + lat + lon, KHONG co truong ten.
# ⚠️ PHEP KIEM NAY TUNG QUET CA FILE VA BAO OAN NGAY LAN CHAY DAU: no bat "Ấn Độ Dương"
#    (ten dai duong) va "Bắc Mỹ" (ten CHAU LUC — chinh la noi dung buoc ①). Dieu muon
#    biet chi lien quan toi KHOI `STACKS`, nen soi dung khoi do. Mot phep kiem hay bao
#    oan thi nguoi ta se bo qua no, tuc la mat luon.
check("buoc ④: `STACKS` KHONG gan ten dia danh nao cho nha may",
      bool(_st) and not re.search(r"\b(nm|name|label)\s*:", _st.group(1)),
      str(_st and _st.group(1).strip()[:80]))
check("buoc ④ → ⑥: co cau noi 'thay nang luong thoi CHUA DU'",
      "chưa đủ</b> đâu" in _me_code and "not enough</b>" in _me_code)

# --- (6) Buoc ⑦ core — giong ON TAP ---
# ⚠️ VIET LAI 02/08/2026: buoc ⑦ khong con keo 3 vien ngoc ma la MAN CHOT HO SO.
#    Chu du an choi that: *"bo nhiem vu keo vien ngoc di, khong logic"* — ba "vien ngoc"
#    la vat the BIA, khong co trong bat cu thu gi nhiem vu day, trong khi ca nhiem vu
#    dung tren anh ve tinh THAT voi toa do THAT.
check("buoc ⑦: KHONG con vien ngoc / mach nang luong su song",
      not any(k in _me_code for k in ("gem_sun", "slot_heat", "MẠCH NĂNG LƯỢNG",
                                      "LIFE ENERGY CIRCUIT", "buildCore")))
# Ba dong ho so PHAI la ba thu nhiem vu DA day — them dong thu tu ma khong co buoc nao
# day no la nhoi kien thuc moi vao dung man tong ket.
for _k in ("file_water", "file_heat", "file_air", "s5_stamp"):
    check(f"buoc ⑦: khoa ho so '{_k}' co o CA vi va en", _k in _vi and _k in _en)
check("buoc ⑦: ba dong ho so khop ba thu da day (71% · goc chieu · oxy)",
      "71%" in _me_code and "góc chiếu của nắng" in _me_code and "oxy để thở" in _me_code)
check("buoc ⑦: chi MOT cu bam, khong phai mot cua chan truoc man thuong",
      "onStamp" in _me_code and "me-stamp" in _me_code)

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
# parent.html them 09/08/2026: bao cao tuan doc `GET /me/report` nen BAT BUOC co
# token. Cung danh doi co y thuc nhu specimen-vault/codex — day la trang noi dung
# cho PHU HUYNH doc, khong phai man choi can muot.
# admin-report.html them 11/08/2026: doc `GET /admin/stats` nen BAT BUOC co token.
# Day la trang QUAN TRI, chi mot nguoi doc va khong nam tren luong choi nao — 233 KB
# o day khong lam cham trai nghiem cua tre. Trang cung `noindex,nofollow` va khong
# duoc noi tu dau ca (vao bang duong dan hoac muc trong trang Ho so).
#   ⚠️ Phep kiem nay da BAT DUOC dung viec no sinh ra de bat: `admin-report.html`
#      duoc them va push 5 lan ma khong ai them vao danh sach nay. Danh sach trang
#      khong tu suy ra duoc — no la QUYET DINH, nen phai viet ra.
# checkout.html them 11/08/2026: mo mot don thanh toan phai co token — don gan voi
# TAI KHOAN, va server lay uid TU TOKEN chu khong bao gio tu than request. Day cung
# la trang cho NGUOI LON doc, khong nam tren luong choi nao.
# mission-tree.html them 12/08/2026: no la CHO TU CHUA cua ca luong nhiem vu.
# `mission-earth.html` co y KHONG nap SDK, nen MOI buoc no choi deu nam trong HANG
# CHO cua js/progress.js; cay chang la man tre quay lai ngay sau khi choi, va no phai
# doc duoc `GET /me/missions` de (a) gui not hang cho, (b) ve dung chang dang mo.
# Khong co token o day thi tre choi xong mot chang, quay lai va van thay dung chang
# vua choi dang sang — mot loi IM LANG. Ban do va man hanh tinh thi KHONG nap: chung
# doc cache ma trang nay vua ghi.
# shop.html them 12/08/2026: mua mot mon la TRU VI THAT, va server la noi tra gia
# (AstroqSV/Services/Cosmetics.cs). Khong co token thi khong tru duoc tien cua ai —
# va cung khong duoc phep tru. Day la trang thu hai co duong tieu Thien thach tim,
# canh 3 mini-game (chung tru phi qua economy.js, khong can SDK vi js/progress.js
# xep hang cho).
# certificate.html them 19/08/2026: to chung nhan phai lay TEN va CAP DO tu SERVER.
# Doc hai thu do tu URL hoac tu localStorage la bien trang nay thanh mot cai may in
# chung nhan mang ten bat ky — mot to giay trong nhu that ma khong chung nhan gi. Che
# do `?preview=1` van cho truyen ten qua URL nhung BAT BUOC in kem dau "MAU", va dau
# do nam TRONG `.cert` nen no di ca vao ban in.
allowed = {"dashboard.html", "achievements.html", "profile.html", "landing-app.html",
           "specimen-vault.html", "missions.html", "codex.html", "parent.html",
           "admin-report.html", "checkout.html", "mission-tree.html", "shop.html",
           "certificate.html"}
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

# ⚠️ MOI TRANG PHAI GOI DUNG TEN CHA CUA NO — khong phai "cha nao cung duoc".
#    Truoc 12/08/2026 muc nay chi co MOT ngoai le (library.html) va moi trang con lai
#    deu phai noi "Trung Tam Dieu Huong". Khu nhiem vu nay co 5 tang
#      Trung Tam Nhiem Vu -> ban do -> (hanh tinh) -> cay chang -> man choi
#    nen nut quay lai o do lui DUNG MOT TANG; nhay thang ve dashboard la bo qua ba
#    tang va tre mat luon cho nhin thay minh vua di duoc toi dau.
#    ⚠️ Khai bang BANG chu khong bang `continue`: bo qua thi khong con phep kiem nao
#       canh, ma cai can canh (nut quay lai noi dung ten noi no se toi) van nguyen.
BACK_PARENT = {
    # library.html la trang CON cua khu Tri Thuc (mo tu learn.html) nen nut quay lai
    # tro ve do. ⚠️ codex.html DA RA KHOI danh sach nay (04/08/2026): So Tay mo tu the
    # MOD-06 o dashboard, nen "mot buoc len cha" CHINH LA hub.
    "library.html":        ("Tri Thức", "Knowledge"),
    "mission-map.html":    ("Trung Tâm Nhiệm Vụ", "Mission Control"),
    "mission-planet.html": ("bản đồ nhiệm vụ", "mission map"),
    "mission-tree.html":   ("Về bản đồ", "Back to map"),
    "mission-earth.html":  ("Về đường đi", "Back to the path"),
}

# Mọi trang có nút quay lại đều phải trỏ về ĐÚNG một cái tên
for f in sorted(os.listdir(ROOT)):
    if not f.endswith(".html"):
        continue
    s_nc = strip_comments(rd(f))
    if 'data-i18n="back"' not in s_nc and 'data-i18n="home_btn"' not in s_nc:
        continue
    # library.html la trang CON cua khu Tri Thuc (mo tu learn.html) nen nut quay lai
    # tro ve do, khong ve hub — di mot buoc len cha la dung hon la nhay hai buoc ve
    # goc. ⚠️ codex.html DA RA KHOI danh sach nay (04/08/2026): So Tay nay mo tu the
    # MOD-06 o dashboard, nen "mot buoc len cha" CHINH LA hub.
    want = BACK_PARENT.get(f)
    if want:
        check(f"{f}: nut quay lai goi dung ten CHA cua no",
              all(w in s_nc for w in want), str(want))
        continue
    check(f"{f}: nut quay lai goi dung ten hub",
          "Trung Tâm Điều Hướng" in s_nc and "Navigation Hub" in s_nc)

# 3 khu moi tren dashboard
# ⚠️ NHAN CUA check() PHAI KHONG DAU. Console Windows mac dinh cp1252, in mot chu co
# dau la UnicodeEncodeError NEM GIUA LUC CHAY va bo do script — mat luon moi phep
# kiem phia sau, ma nhin output thi tuong la "chay xong". Chu co dau chi duoc nam
# trong DIEU KIEN, khong nam trong nhan.
print("\n=== [7b] Dashboard: 6 card, 3 khu moi ===")

# ⚠️ BANG THONG KE PHAI TU DAT `text-align`, vi no NAM TRONG `.hero` — noi khai
#    `text-align:center`, va chu thi thua huong. Thieu mot dong nay thi MOI khoi hai
#    dong (so tren, nhan duoi) canh giua theo dong DAI HON, tuc moi khoi mot mep trai.
#    Do duoc truoc khi sua: o "0%" lech 37px · o "Ho so" +25px · o "Thanh tich" -31px
#    · khoi XP -33px. Sau khi sua: ca bay khoi lech 0px (do o desktop + 390px + EN).
#    Phep kiem tinh nay chi canh dung mot dong de nguoi don dep sau khong go no.
_dash_css = strip_comments(rd("css/dashboard.css"))
_sh_rule = re.search(r'\.stats-hud\{[^}]*\}', _dash_css)
check("[7b] bang Thong Ke tu dat text-align (vi nam trong .hero canh giua)",
      bool(_sh_rule) and "text-align:left" in _sh_rule.group(0),
      (_sh_rule.group(0)[:70] if _sh_rule else "khong thay rule .stats-hud"))
check("[7b] .hero VAN canh giua (khong pha lay)",
      bool(re.search(r'\.hero\{[^}]*text-align:center', _dash_css)))
for key, mod in (("mission_title", "MOD-04"), ("lab_title", "MOD-05"),
                 ("codex_title", "MOD-06")):
    check(f"dashboard.html: co khoa i18n '{key}'", key in dash)
    check(f"dashboard.html: co so hieu {mod}", mod in dash_nc)
for label, nm in (("Trung Tam Nhiem Vu", "Trung Tâm Nhiệm Vụ"),
                  ("Mission Control", "Mission Control"),
                  ("Phong Nghien Cuu", "Phòng Nghiên Cứu"),
                  ("Research Lab", "Research Lab"),
                  ("So Tay Thuat Ngu", "Sổ Tay Thuật Ngữ"),
                  ("Terminology Codex", "Terminology Codex")):
    check(f"dashboard.html: co ten '{label}'", nm in dash)
# So hieu MOD cu KHONG duoc danh lai (tai lieu + cach nguoi dung goi ten bam vao no)
for mod in ("MOD-01", "MOD-02", "MOD-03"):
    check(f"dashboard.html: giu nguyen {mod}", mod in dash_nc)
# ⚠️ CHI CON MOT khu chua co trang (Phong Nghien Cuu) — MOD-06 doi tu "Thu Vien
# Thien Van" (chua co trang) sang So Tay Thuat Ngu (codex.html, da chay that) ngay
# 04/08/2026. Con so 1 nay la phep kiem CO RANG: them mot card khoa nua ma khong
# ghi vao day thi no bao hong.
# ⚠️ PHEP KIEM NAY DA DOI PHAT BIEU 09/08/2026 — no tung doi nut cua card 'soon'
#    phai `disabled`, nen no bao hong DUNG LUC san pham lam dung. Nguyen tac cu
#    ("nut bam duoc thi phai co gi do xay ra") KHONG bi noi long: nut nay nay MO
#    MODAL noi vi sao khoa + khi mo se duoc gi, tuc co xay ra that. Nut `disabled`
#    la mot ngo cut — tre bam khong an va chi tuong minh bam truot.
# ⚠️⚠️ DOI PHAT BIEU 12/08/2026 — MOD-05 DA MO KHOA (lab.html co that), nen ba
#    phep kiem cu ("dung 1 card soon" · "nut cua card soon bam duoc" · "noi vao
#    AstroQLocks") khang dinh dung trang thai CU va bao hong dung luc san pham lam
#    dung. Dieu chung bao ve — *dashboard noi that ve khu nao chua dung xong* —
#    KHONG doi, chi doi cach hoi. Va ban moi MANH HON: no doi moi card MOD dan sang
#    mot FILE CO THAT, tuc bat duoc ca ca "mo khoa mot khu ma tro vao trang khong
#    ton tai" — thu ma ban cu khong he hoi toi.
# ⚠️⚠️ DOI PHAT BIEU 19/08/2026 — chu du an chot KHOA LAI Phong Nghien Cuu
#    (MOD-05), nen phep kiem "0 card soon" khang dinh dung trang thai CU va bao
#    hong dung luc san pham lam dung. Dieu can bao ve KHONG doi: *dashboard noi
#    that ve khu nao chua vao duoc*. Con so 1 la phep kiem CO RANG theo ca hai
#    chieu: mo khoa mot khu ma quen sua day, hoac khoa them mot khu nua, deu bao.
_soon_cards = dash_nc.count(" soon\">")
check("dashboard.html: dung 1 card 'soon' (Phong Nghien Cuu)",
      _soon_cards == 1, "co %d card khoa" % _soon_cards)
# Neu ngay nao co card khoa tro lai thi ba luat cu song lai NGUYEN VEN:
if _soon_cards:
    # ⚠️ SOI MARKUP, KHONG QUET CA FILE. Ban cu doi chuoi "disabled" khong xuat
    #    hien o BAT KY dau trong dashboard.html — nen mot dong JS hoan toan hop le
    #    (`logoutBtn.disabled = true` chan bam Dang xuat hai lan, them 20/08/2026)
    #    cung lam no bao hong. Dieu can bao ve la THUOC TINH `disabled` tren nut
    #    cua the khoa, khong phai chu "disabled" noi chung.
    _dash_markup = strip_js(dash_nc)
    _bad_attr = re.findall(r"<button[^>]*\sdisabled", _dash_markup)
    check("dashboard.html: nut card 'soon' BAM DUOC (khong disabled)",
          not _bad_attr, str(_bad_attr[:2]))
    check("dashboard.html: card 'soon' noi vao AstroQLocks",
          "AstroQLocks.wire(" in dash_nc)
    check("dashboard.html: huy hieu khoa suy tu state, khong go cung",
          '+ it.state' in dash_nc)
else:
    # 0 card khoa => khong duoc con di tich cua co che khoa dashboard, khong thi
    # do la ma chet: mot huy hieu khong bao gio duoc dien chu, hoac mot loi goi
    # wire() tro vao mot khoa da bi xoa khoi js/locks.js (tra null, im lang).
    check("dashboard.html: KHONG con huy hieu khoa rong",
          'id="lab-badge"' not in dash_nc)
    check("dashboard.html: KHONG con wire() tro vao khoa da xoa",
          'AstroQLocks.wire($("lab-btn"), "lab")' not in dash_nc)
    check("dashboard.html: khoa 'lab' da bo khoi js/locks.js",
          '"lab":' not in strip_comments(rd("js/locks.js")))
    # ⚠️ Khong con muc khoa nao thi THOI NAP locks.js/locks.css — ~7 KB khong lam
    #    gi ca. Cung ly le da cat bo icon sticker khoi 4 trang khong dung (12/08).
    # ⚠️ SOI THE, KHONG SOI VAN BAN: `dash` con nhac "js/locks.js" trong GHI CHU
    #    lich su (giai thich vi sao mo khoa), nen `"js/locks.js" not in dash` la
    #    dem ca chu trong ghi chu cua chinh minh — loi da lap nhieu lan trong du an.
    _tags_js = re.findall(r'<script[^>]+src="([^"]+)"', dash)
    _tags_css = re.findall(r'<link[^>]+href="([^"]+\.css)"', dash)
    check("dashboard.html: thoi nap locks.js va locks.css (khong con muc khoa)",
          "js/locks.js" not in _tags_js and "css/locks.css" not in _tags_css,
          "js=%s css=%s" % ([x for x in _tags_js if "locks" in x],
                            [x for x in _tags_css if "locks" in x]))

# ⚠️ MOI CARD MOD PHAI DAN SANG MOT FILE CO THAT. Mot nut bam duoc ma tro vao 404
#    la ngo cut te hon ca mot nut `disabled` — tre khong hieu vi sao trang trong.
_dests = set(re.findall(r'location\.href\s*=\s*"([a-z0-9-]+\.html)"', dash_nc))
_dests |= set(re.findall(r'href="([a-z0-9-]+\.html)"', dash_nc))
for _d in sorted(_dests):
    check("dashboard.html: dich '%s' co that tren dia" % _d,
          os.path.isfile(os.path.join(ROOT, _d)))
# ⚠️ MOD-05 dang khoa (19/08/2026): no MO MODAL chu KHONG dieu huong. Dua tre sang
#    mot khu dang khoa la de no vao roi moi biet chua co gi.
check("dashboard.html: MOD-05 khong dieu huong sang lab.html",
      'location.href="lab.html"' not in dash_nc.replace(" ", ""))
check("dashboard.html: MOD-05 noi vao AstroQLocks (bam la mo modal)",
      'AstroQLocks.wire($("lab-btn"), "lab")' in dash_nc)
# ⚠️ `lab.html` PHAI CON TREN DIA: khoa la dong DUONG VAO, khong phai xoa khu. Xoa
#    trang di thi mo lai la dung lai tu dau, va `smoke_lab` mat luon doi tuong do.
check("lab.html van con tren dia (khoa duong vao, khong xoa khu)",
      os.path.isfile(os.path.join(ROOT, "lab.html")))
# ⚠️ Huy hieu la SAP RA MAT, KHONG phai TRA PHI: Phong Nghien Cuu chua co noi dung,
#    gan nhan tra phi la hua rang tra tien se mo duoc. Xem ba trang thai o js/locks.js.
# ⚠️ Huy hieu phai SUY TU `state` chu khong go cung `badge_soon`: go cung thi ngay
#    bat co sang `pro`, the van ghi "SAP RA MAT" trong khi modal noi "thuoc goi ..."
#    — hai thong diep nguoc nhau, dung luc co che nay duoc dung toi. Phep thu pha
#    hoai 09/08/2026 da lo ra dung cho nay.
check("dashboard.html: card 'soon' KHONG dan sang trang khong ton tai",
      'href="research-lab.html"' not in dash and 'href="star-archive.html"' not in dash)
# MOD-06 phai la duong vao THAT su bam duoc, khong con la o "sap ra mat"
check("dashboard.html: card MOD-06 dan sang codex.html",
      'href="codex.html"' in dash_nc)
check("dashboard.html: KHONG con ten khu chua ton tai 'Thu Vien Thien Van'",
      "Thư Viện Thiên Văn" not in strip_comments(dash)
      and "Star Archive" not in strip_comments(dash))
check("dashboard.html: card Mission Control dan sang missions.html",
      'href="missions.html"' in dash)

# ══════════════════════════════════════════════════════════════
print("\n=== [7c] Sanh Nhiem Vu: khop server + khong bia tien do ===")
mis = rd("missions.html")
mis_js = inline_js(mis)
# ⚠️ DOI PHAT BIEU 12/08/2026 (`docs/decisions/008`, viec con treo so 1).
#    Truoc do trang nay la mot LUOI THE NHIEM VU va muc [7c] doi `MISSIONS` khai du
#    2 nhiem vu (earth + moon) khop `Missions.cs`. Nay luoi the da chuyen xuong dung
#    tang cua no (`mission-planet.html`), con trang nay la CUA TRUOC dan sang ban do.
#    Dieu can bao ve KHONG doi va nay do muc [20] canh CHAT HON: danh muc nhiem vu o
#    client phai khop `Missions.cs` — chi la no doc `js/mission-catalog.js` thay vi
#    doc mot mang nam trong HTML.
check("missions.html: KHONG con luoi the nhiem vu (mot duong vao, khong hai)",
      "mcard" not in strip_comments(mis))
check("missions.html: dan sang ban do nhiem vu", 'href="mission-map.html"' in mis)
check("missions.html: co dong 'Choi tiep' va mac dinh AN",
      'id="resume"' in mis and re.search(r'id="resume"[^>]*\shidden', mis) is not None)
check("missions.html: doc danh muc tu js/mission-catalog.js",
      'src="js/mission-catalog.js"' in mis and "AstroQCatalog.missions()" in mis_js)
# Mat mang / chua dang nhap → hien dau "—", KHONG hien 0/7 (0/7 la mot loi khang
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

# ══════ PHI SUY TU DO KHO, va phai khop o BON noi ══════
# ⚠️ DOI PHAT BIEU 15/08/2026. Truoc do `Wallet.Fees` la 6 con so gan tay va `diff`
#    la mot nhan gan tay KHAC, hai thu khong lien quan gi toi nhau — do duoc: Ne
#    Thien Thach gan nhan "De" ma thu 5 tt, Me Cung "Vua" thu 4, Phong Thu "Kho"
#    cung 5. Nay co LUAT: do kho do bang "mat bao nhieu thi het luot", va phi suy
#    ra tu do kho (De 3 / Vua 4 / Kho 5).
# ⚠️ Va muc nay nay canh BON noi chu khong phai ba: `CONFIG.COST` trong TUNG game
#    truoc gio KHONG ai doi chieu — mot game de lech thi tre thay mot con so o sanh
#    roi bi tru mot con so khac, va khong phep kiem nao noi gi.
wal = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Wallet.cs"), encoding="utf-8").read()

_m_fbd = re.search(r"FeeByDiff = new\(\)\s*\{(.*?)\};", wal, re.S)
check("server: co bang FeeByDiff (phi theo do kho)", bool(_m_fbd))
# ⚠️ Chan dau tu: "Diff = new()" la CHUOI CON cua "FeeByDiff = new()", ma FeeByDiff
#    khai TRUOC -> re.search bat trung bang kia va sv_diff ra rong (loi im lang).
_m_diff = re.search(r"(?<![A-Za-z])Diff = new\(\)\s*\{(.*?)\};", wal, re.S)
check("server: co bang Diff (do kho tung game)", bool(_m_diff))
check("server: Fees SINH RA tu Diff, khong con go tay 6 con so",
      "Diff.ToDictionary" in wal and not re.search(r'Fees = new\(\)', wal))

fee_by_diff = dict((m[0], int(m[1]))
                   for m in re.findall(r'\["([a-z]+)"\]\s*=\s*(\d+)',
                                       _m_fbd.group(1) if _m_fbd else ""))
sv_diff = dict(re.findall(r'\["([a-z-]+)"\]\s*=\s*"([a-z]+)"',
                          _m_diff.group(1) if _m_diff else ""))
sv_fees = {g: fee_by_diff[d] for g, d in sv_diff.items() if d in fee_by_diff}
check("suy ra duoc phi cua MOI game server khai",
      len(sv_fees) > 0 and len(sv_fees) == len(sv_diff), str(sv_fees))
check("chi co dung 3 muc do kho", sorted(fee_by_diff) == ["easy", "hard", "medium"],
      str(sorted(fee_by_diff)))
check("kho hon thi dat hon (phi tang theo do kho)",
      fee_by_diff.get("easy", 9) < fee_by_diff.get("medium", 0) < fee_by_diff.get("hard", 0),
      str(fee_by_diff))

# (1) economy.js
cl_fees = dict((m[0], int(m[1])) for m in
               re.findall(r'(\w+):\s*(\d+)', re.search(r"var FEES = \{([^}]*)\}", eco).group(1)))
check("Bang phi khop client/server", sv_fees == cl_fees, f"server={sv_fees} client={cl_fees}")

# (2) badge phi + (3) nhan do kho o games.html
_hub = rd("games.html")
hub_fees = dict((m[1], int(m[0])) for m in
                re.findall(r'cost:(\d+)[^}]*?file:"game-([a-z]+)\.html"', _hub))
check("Phi hien o games.html khop bang phi server",
      all(sv_fees.get(k) == v for k, v in hub_fees.items()),
      f"hub={hub_fees} server={sv_fees}")
hub_diff = dict((m[1], m[0]) for m in
                re.findall(r'diff:"([a-z]+)"[^}]*?file:"game-([a-z]+)\.html"', _hub))
check("Nhan do kho o games.html khop bang Diff cua server",
      all(sv_diff.get(k) == v for k, v in hub_diff.items()),
      f"hub={hub_diff} server={sv_diff}")

# (4) CONFIG.COST trong TUNG trang game
# ⚠️ SUY TU MANG `GAMES` o games.html, KHONG gan cung. Ban cu liet ke tay 6 game,
#    nen them game thu 7 la no AM THAM khong kiem `CONFIG.COST` cua game do — mot
#    lo hong im lang, khong phai mot phep kiem bao hong. Cung lop loi "gan cung con
#    so" da lap nhieu lan (14 icon · 25 cau · 20 mau vat · 5 buoc · 6 game).
_GAME_FILE = dict(re.findall(r'key:"([a-z]+)"[^}]*?file:"([a-z-]+\.html)"', _hub))
check("Doc duoc file cua MOI game co phi tu games.html",
      set(_GAME_FILE) == set(sv_fees),
      f"hub={sorted(_GAME_FILE)} server={sorted(sv_fees)}")
_bad_cost = []
for _g, _f in _GAME_FILE.items():
    _m = re.search(r"COST:\s*(\d+)", rd(_f))
    if not _m or int(_m.group(1)) != sv_fees.get(_g):
        _bad_cost.append(f"{_f}={_m.group(1) if _m else '?'} (can {sv_fees.get(_g)})")
check("CONFIG.COST cua TUNG game khop bang phi server", not _bad_cost, str(_bad_cost))

# Con so phi HIEN RA cho tre (`<b>n</b>` trong cost_line) phai la chinh phi do —
# thay doi phi ma quen sua chuoi la the noi mot dang, vi tru mot dang.
_bad_lbl = []
for _g, _f in _GAME_FILE.items():
    _src = rd(_f)
    for _m in re.finditer(r'cost_line:"[^"]*?<b>(\d+)</b>', _src):
        if int(_m.group(1)) != sv_fees.get(_g):
            _bad_lbl.append(f"{_f}: hien {_m.group(1)}, tru {sv_fees.get(_g)}")
check("chu 'Moi luot: n' trong tung game khop phi that", not _bad_lbl, str(_bad_lbl))

# ══════ TY LE HOC/CHOI: tran quiz phai khop AWARD o quiz.html ══════
# ⚠️ Chot 15/08/2026 (chu du an: *"can doi lai phan thien thach nhan khi hoc de tre
#    khong roi vao trang thai hoc it ma van thoai mai choi"*). Tran o server =
#    ROUND_SIZE × AWARD × 2 (nhan 2 vi vat pham Dong co X2). Lech thi tre thay mot
#    con so o man tong ket roi vi cong mot con so khac.
_q = rd("quiz.html")
_m_aw = re.search(r"var AWARD = (\d+)", _q)
_m_rs = re.search(r"var ROUND_SIZE = (\d+)", _q)
_m_mq = re.search(r"MaxPerQuiz\s*=\s*(\d+)", wal)
check("doc duoc AWARD/ROUND_SIZE/MaxPerQuiz", all([_m_aw, _m_rs, _m_mq]),
      f"{_m_aw} {_m_rs} {_m_mq}")
if _m_aw and _m_rs and _m_mq:
    _need = int(_m_aw.group(1)) * int(_m_rs.group(1)) * 2
    check("tran thuong quiz o server khop AWARD x ROUND_SIZE x 2",
          int(_m_mq.group(1)) == _need,
          f"server={_m_mq.group(1)} can={_need} (AWARD={_m_aw.group(1)})")
    # Ty le muc tieu: MOT luot quiz DAT ~ 5 luot choi. Kiem bang chinh cac con so.
    _pass_min = -(-int(_m_rs.group(1)) * 60 // 100)          # ceil(60% cua ROUND_SIZE)
    _min_earn = _pass_min * int(_m_aw.group(1))
    _avg_fee = sum(sv_fees.values()) / max(1, len(sv_fees))
    _plays = _min_earn / _avg_fee
    check("mot luot quiz DAT toi thieu doi duoc 3-8 luot choi",
          3 <= _plays <= 8,
          f"{_min_earn} tt / phi TB {_avg_fee:.1f} = {_plays:.1f} luot")

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

# ── MÓC TREO: server giu LUAT (gia tri nao ghi duoc), client giu HINH + TEN ──
# Lech hai ben la mot lop loi IM LANG theo ca hai chieu: mot moc chi co o client
# thi tre chon duoc roi nhan 400; mot moc chi co o server thi khong bao gio ve ra.
sv_hooks = re.search(r"Hooks\s*=\s*\n?\s*\[([^\]]+)\]", spc)
sv_hook_ids = re.findall(r'"([A-Z0-9]+)"', sv_hooks.group(1)) if sv_hooks else []
cl_hooks = re.search(r"var HOOKS\s*=\s*\[([^\]]+)\]", spec_js)
cl_hook_ids = re.findall(r'"([A-Z0-9]+)"', cl_hooks.group(1)) if cl_hooks else []
check("Doc duoc danh sach moc o CA hai ben", len(sv_hook_ids) > 0 and len(cl_hook_ids) > 0,
      f"server={len(sv_hook_ids)} client={len(cl_hook_ids)}")
check("Danh sach moc client == server (ke ca THU TU)", sv_hook_ids == cl_hook_ids,
      f"{sv_hook_ids} vs {cl_hook_ids}")
# Dau ':' la ky tu ngan cua dang luu "<moc>:<id mau vat>" — moc chua ':' la
# `ParseStored` cat sai va mau vat bien mat khoi ban ma khong bao gi.
check("Khong id moc nao chua dau ':'", all(":" not in h for h in sv_hook_ids))
# So moc phai NHIEU HON so cho trung, khong thi "tre tu chon moc" la mot lua chon
# gia — moi mau vat chi con dung mot cho de vao.
sv_slots = int(re.search(r"DeskSlots\s*=\s*(\d+)", spc).group(1))
check("So moc nhieu hon so cho trung", len(sv_hook_ids) > sv_slots,
      f"{len(sv_hook_ids)} moc / {sv_slots} cho")
# Moi moc phai co o CA hai vach de bang do khong lech mot ben.
check("Hai vach L/R deu co moc",
      len([h for h in sv_hook_ids if h[0] == "L"]) > 0
      and len([h for h in sv_hook_ids if h[0] == "R"]) > 0)
# `css/dashboard.css` xep moc bang flex theo thu tu DOM, va bu lech pha bang
# `:nth-child`. Thieu mot nhanh nth-child la moc cuoi cung nhap nho cung pha voi
# moc dau — doc ra nhu ca cot dang rung.
dcss = rd("css/dashboard.css")
per_wall = max(len([h for h in sv_hook_ids if h[0] == "L"]),
               len([h for h in sv_hook_ids if h[0] == "R"]))
check("css/dashboard.css khai du nhip lech pha cho moi moc tren vach",
      all(f":nth-child({i})" in dcss for i in range(1, per_wall + 1)),
      str([i for i in range(1, per_wall + 1) if f":nth-child({i})" not in dcss]))
# Cai kep theo CHIEU CAO moi la cai giu 5 moc khong de len nhau — xem ghi chu o
# `.desk-float`. Bo no di thi mot man 1600x720 cho ra cot cao hon ca khung nhin.
check("Co moc bi kep theo CHIEU CAO khung nhin, khong chi be rong",
      "100vh" in dcss.split(".desk-float", 1)[1].split(".dfw", 1)[0])
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
# ⚠️ NGAN HANG CAU HOI NAY LA NHIEU FILE (doi 07/08/2026): `js/quiz-index.js` +
#    `js/quiz/<khoa-cau>.js`, MOT CAU MOI FILE. Noi lai thanh MOT chuoi `_bank` de
#    moi phep kiem regex duoi day chay nguyen — chung soi NOI DUNG (term, srcQuote,
#    url), khong soi so file. Ten file la nguon su that cua tap khoa.
_qdir = os.path.join(ROOT, "js", "quiz")
_qfiles = sorted(f for f in os.listdir(_qdir) if f.endswith(".js")) \
    if os.path.isdir(_qdir) else []
_bank = rd("js/quiz-index.js") + "\n" + "\n".join(
    rd("js/quiz/" + f) for f in _qfiles)
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

# --- (2a) BANK CHIA THEO FILE: ten file LA khoa cau ---
# Do 07/08/2026: bank mot-file la 43,6 KB gzip cho 100 cau = 51% duong tai cua
# quiz.html, ma mot luot chi dung 5 cau. Nay muc luc + 5 file = 10,2 KB.
_file_keys = {os.path.splitext(f)[0] for f in _qfiles}
check("co thu muc js/quiz/ voi cac file cau", len(_file_keys) >= 100,
      f"{len(_file_keys)} file")
check("khoa `term` trong file KHOP dung ten file (ten file la khoa)",
      _file_keys == _bank_terms,
      f"chi co file: {sorted(_file_keys - _bank_terms)[:5]} · "
      f"chi khai trong file: {sorted(_bank_terms - _file_keys)[:5]}")
# ⚠️ URL CHI DUOC O MUC LUC. De bai muc 2a: `src` la KHOA tro vao bang `S`, khong
#    phai URL — 870 cau viet URL thang la ~870 ban sao cua ~40 dia chi, va ngay
#    NASA doi mot duong dan thi phai sua hang tram file.
_url_in_q = [f for f in _qfiles if "http" in rd("js/quiz/" + f)]
check("KHONG file cau nao viet URL thang (src la KHOA vao bang S)",
      not _url_in_q, f"{len(_url_in_q)} file: {_url_in_q[:5]}")
# Muc luc phai liet ke dung tap file — lech la cau co that ma khong bao gio duoc rut
_ix = rd("js/quiz-index.js")
_ix_keys = set()
for _m in re.finditer(r"\bq:\s*\[([^\]]*)\]", _ix):
    _ix_keys |= set(re.findall(r'"([a-z0-9][a-z0-9-]*)"', _m.group(1)))
check("muc luc js/quiz-index.js liet ke dung tap file trong js/quiz/",
      _ix_keys == _file_keys,
      f"chi muc luc: {sorted(_ix_keys - _file_keys)[:5]} · "
      f"chi file: {sorted(_file_keys - _ix_keys)[:5]}")
# ⚠️ QUET TREN CODE DA BOC COMMENT. Lan dau phep kiem nay bao hong OAN: chinh khoi
#    chu thich cua quiz.html giai thich "truoc day bank nam o js/quiz-questions.js"
#    — va do la ghi chu NEN CO (no ke lai vi sao code co hinh dang nay). Day la lan
#    thu 11 du an mac dung loi "dem ca chu trong ghi chu cua chinh minh"; moi phep
#    kiem dang "khong duoc chua X" phai quet tren `strip_comments()`.
check("quiz.html nap MUC LUC, khong nap bank mot-file cu",
      'src="js/quiz-index.js"' in rd("quiz.html")
      and "quiz-questions.js" not in strip_comments(rd("quiz.html")))
# ⚠️ `lv` VAN LA TRUONG NGU — chu du an chot 07/08/2026 GIU no, cho duong "server
#    tinh cap do roi client rut de theo cap do" (quiz.html co y khong nap SDK
#    Firebase nen chua co token doc cap do). Phep kiem canh no khong bi xoa am tham
#    va cung khong bi noi vao nua voi.
check("muc luc con giu bang LV (truong `lv` chua bi xoa)", "var LV = {" in _ix)
check("`lv` chua co nguoi doc — chua ai nap cap do vao quiz.html",
      "AstroQQuestions.LV" not in strip_comments(rd("quiz.html")))
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

# --- (2b) NHAN PHAN LOAI: `cat` phai co NGUOI DOC ---
# Truoc 07/08/2026 `cat` duoc khai o moi the ma KHONG file nao doc — mot truong khai
# ma khong ai doc la mot loi khai sai. Nay codex.html hien nhan phan loai tren the.
# CHUA co bo loc phan loai, co y: 18 the `space` + 1 the `earth` thi mot chip chua
# dung MOT the — de Dot 3 (thêm ~10 the Trai Dat + ~5 the dung cu) roi tai dung khuon
# sidebar-dem-so cua library.html.
_cats = set(re.findall(r'cat:\s*"([a-z-]+)"', strip_comments(_cx)))
check("doc duoc gia tri `cat` cua cac the", len(_cats) > 0, f"{sorted(_cats)}")
_cxp_code = strip_comments(_cxp)
check("codex.html CO doc `cat` (nhan phan loai tren the)",
      "catLabel(" in _cxp_code and "cx-i-cat" in _cxp_code)
# ⚠️ MOI gia tri `cat` phai co MOT NHANH LITERAL trong catLabel — ghep dong
#    `t("cat_" + x.cat)` thi phep kiem i18n duoi day bao 3 khoa nay "khai ma khong
#    dung", va loi do im lang. Cung bai hoc voi `s1_hit1/2/3` o mission-earth.html.
_miss_cat = [c for c in _cats if f'"{c}"' not in _cxp_code
             or f'cat_{c}' not in _cxp_code]
check("moi gia tri `cat` co mot nhanh literal trong catLabel()",
      not _miss_cat, f"thieu nhanh: {sorted(_miss_cat)}")
check("co luoi an toan `cat_other` cho gia tri `cat` moi",
      'cat_other' in _cxp_code)
for _k in ("cat_space", "cat_earth", "cat_other"):
    check(f"khoa i18n `{_k}` co o CA vi va en", _cxp.count(_k + ":") == 2,
          f"{_cxp.count(_k + ':')} lan")
check("codex.html CHUA co bo loc phan loai (co y, doi Dot 3)",
      "seg-cat" not in _cxp_code)

# ⚠️ HAI PHEP KIEM DUOI DAY CHUYEN TU `check_codex.py` SANG (30/07/2026), truoc khi
#    xoa bo React da bi thay the. Chung canh CODE DANG CHAY nen khong duoc mat.
# (a) 5 cau lap trinh cua bank la cau KHAI NIEM, khong co `src`, va khong thuoc thuat
#     ngu thien van nao. Thuat ngu nhan bua mot trong 5 khoa do la giai ma sai bang
#     mot cau khong lien quan.
# ⚠️⚠️ PHEP KIEM NAY DA DOI PHAT BIEU 09/08/2026, va day la mot doi CO LY DO chu khong
#     phai noi long. Ban cu doi 5 khoa do KHONG the nao nhan — dung khi chua co the AI/
#     Robot nao, vi luc do the duy nhat co the nhan chung la mot the thien van, tuc giai
#     ma sai bang mot cau khong lien quan. Nay `term_algorithm` va `term_sensor` nhan
#     chung MOT CACH CO CHU DICH: `def`/`gr` cua hai the do day dung trinh tu / vong lap
#     / dieu kien / cam bien. Dieu can bao ve KHONG doi: chung khong duoc roi vao mot the
#     KHONG day chung. Nen nay canh DUNG THE thay vi canh "khong the nao".
PROG_OWNER = {"algorithm": "term_algorithm", "sequence": "term_algorithm",
              "loop": "term_algorithm", "condition": "term_algorithm",
              "sensor": "term_sensor"}
# ⚠️ `_qmap[k]` la mot LIST (no dung de bat mot khoa bi HAI the nhan), khong phai chuoi
#    — ban dau toi so thang voi chuoi nen phep kiem bao hong oan het 5 khoa.
_prog_bad = {k: _qmap.get(k) for k, want in PROG_OWNER.items()
             if _qmap.get(k) != [want]}
check("5 cau lap trinh thuoc DUNG the day chung (algorithm/sensor), khong the nao khac",
      not _prog_bad, f"lech: {_prog_bad}")
# ⛔ Va khong the THIEN VAN nao duoc nhan chung — do van la giai ma sai.
_astro_grab = sorted(k for k, v in _qmap.items()
                     if k in PROG_OWNER
                     and any(t not in ("term_algorithm", "term_sensor") for t in v))
check("khong the thien van nao nhan cau lap trinh", not _astro_grab, f"{_astro_grab}")
check("codex.html co trang thai thu BA cho thuat ngu chua co cau hoi",
      '"soon"' in _cxp and "soon_hint" in _cxp)
check("codex.html KHONG dan sang Quiz khi chua co cau hoi",
      'hidden = st==="soon"' in _cxp or '$("m-quiz").hidden = st==="soon"' in _cxp)

# --- (2c) ID BAI DOC: kebab-case + duy nhat (them 06/08/2026) ---
# ⚠️ `astroq-read` trong localStorage VA ban ghi `READ#<id>` tren server deu khoa theo
#    id nay. Doi kieu dat ten giua chung la:
#      · id cu va id moi khong bao gio gap nhau -> tre doc lai bai da doc
#      · `AstroQProgress.lesson(id)` gui hai dang khoa cho cung mot kho
#    Bank cu dung kebab (`lib-nebula`); dot noi dung moi de nghi `article_x_y` (gach
#    duoi). Chot MOT kieu roi canh bang may.
# ⚠️ KHO BAI DOC DA CHIA 09/08/2026 — `js/articles.js` khong con. Nguon su that la
#    `js/article/<id>.js` (mot bai mot file), muc luc `js/articles-index.js` SINH RA.
#    Nen id bai doc nay doc tu TEN FILE, chac chan hon regex tren mot file gop.
_afiles = sorted(glob.glob(os.path.join(ROOT, "js", "article", "*.js")))
check("doc duoc kho bai doc da chia", len(_afiles) >= 39, f"{len(_afiles)} file")
_art = "\n".join(rd("js/article/" + os.path.basename(p)) for p in _afiles)
_aids = [os.path.splitext(os.path.basename(p))[0] for p in _afiles]
# ⛔ Muc luc phai la BAN CHIEU cua cac file — lech nghia la ai do sua tay muc luc
#    hoac quen chay lai bo sinh, va bai do se KHONG hien ra o luoi.
_aidx = rd("js/articles-index.js")
_missing = [i for i in _aids if '"%s"' % i not in _aidx]
check("moi file bai deu co trong muc luc (chay lai split_articles.py neu lech)",
      not _missing, f"thieu: {_missing[:4]}")
check("khong con js/articles.js mot-file",
      not os.path.exists(os.path.join(ROOT, "js", "articles.js")))
_bad_id = [i for i in _aids if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", i)]
check("id bai doc deu la kebab-case (khong gach duoi, khong chu hoa)",
      not _bad_id, f"sai kieu: {_bad_id}")
check("id bai doc khong trung", len(set(_aids)) == len(_aids),
      f"trung: {sorted({i for i in _aids if _aids.count(i) > 1})}")

# --- (2b) BA LO HONG TIM RA KHI RA SOAT DOT 1 CUA Gemini (06/08/2026) ---
# Ca ba deu la loi IM LANG: khong ngoai le, khong console, chi la du lieu sai nam do.

# (i) `term` TRUNG trong bank.
# ⚠️ `_bank_terms` o tren la mot SET nen no NUOT trung lap — hai cau cung khoa thi
#    set chi con mot, va moi phep kiem dua vao no van xanh. Phai dem tren DANH SACH.
#    Hau qua that: hai cau de len nhau trong `PROGRESS.terms` cua tre; tra loi dung
#    cau nay thi cau kia cung tinh la da lam.
_bank_list = re.findall(r'term:\s*"([^"]+)"', _bank)
_dup_terms = sorted({t for t in _bank_list if _bank_list.count(t) > 1})
check("khong co `term` TRUNG trong bank cau hoi", not _dup_terms,
      f"trung: {_dup_terms}")

# (ii) Hai id thuat ngu khac nhau CHI BOI HAU TO.
# ⚠️ `term_exoplanet` canh `term_exoplanets` CHAY EM: So Tay hien hai the gan giong
#    nhau, tre mo duoc the nay ma the kia van khoa, va nguoi sua sau doc luot tuong
#    la mot. Trung id han thi loi no ra ngay; gan trung thi khong.
#    Cung ho voi ca `"map01Seen"` la TIEN TO cua `map01SeenAt` (01/08/2026).
_near = sorted({f"{a} ~ {b}" for a in _ids for b in _ids
                if a != b and b.startswith(a) and len(b) - len(a) <= 2})
check("khong hai thuat ngu khac nhau chi boi hau to (vd `...planet` vs `...planets`)",
      not _near, f"{_near}")

# (iii) `srcQuote` — truong moi tu 06/08/2026, chua cau cu nao co nen chi kiem cau CO.
# ⚠️ Cau trich RONG con te hon khong co: no bao rang da kiem chung trong khi khong.
_q_pairs = re.findall(r'srcQuote:\s*"([^"]*)"', _bank)
_empty_q = [i for i, q in enumerate(_q_pairs) if not q.strip()]
check("khong co `srcQuote` rong", not _empty_q, f"{len(_empty_q)} cau rong")
# Co cau trich thi phai co URL de doi chieu — nguoc lai la mot loi khang dinh khong
# kiem duoc.
check("moi `srcQuote` deu di kem mot `src`",
      _bank.count("srcQuote:") <= _bank.count("src:"),
      f"srcQuote={_bank.count('srcQuote:')} src={_bank.count('src:')}")

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
# ⚠️ PHAT BIEU LAI 09/08/2026: phep kiem cu ghim nguyen van
#    `Math.Min(correct, MaxTermsPerQuiz)`, nen khi hai duong loc (dung / sai) duoc
#    gom vao ham `CleanTerms(src, cap, exclude)` thi no bao hong dung luc code lam
#    dung. Nay hoi DIEU MUON BIET: tran cua danh sach DUNG la `correct`.
check("server: KEP so khoa theo so cau DUNG (1 cau dung khong mo ca so tay)",
      "CleanTerms(req.Terms, correct, null)" in _mep
      and "Math.Min(Math.Max(cap, 0), MaxTermsPerQuiz)" in _mep)
check("server: truyen terms vao BumpProgressAsync",
      "constellation, okTerms)" in _mep)
check("server: luu bang ADD tren string set (hop, khong trung, khong mat khi song song)",
      'adds.Add("#terms :terms")' in _dyn)
check("server: chan tap rong truoc khi ghi SS", "terms.Count > 0" in _dyn)
check("server: tra `terms` ve trong snapshot", "terms          = p.Terms," in _mep)

# ══════════ (5b) CAU SAI -> cot "con vuong chu de nao" (09/08/2026) ══════════
# Truoc do cau SAI khong duoc luu o dau ca: `PROGRESS.terms` chi nhan cau DUNG (no la
# chia khoa mo So Tay), con bo dem thi chi co tong so. Nen loi hua o `pricing.html`
# ("Thay ro con vung chu de nao, con vuong cho nao") khong co nguyen lieu de tra loi.
print("\n[12b] Cau SAI -> bao cao chu de cho phu huynh")
_rep_cs = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/Report.cs"))
_mail_cs = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/EmailService.cs"))
_par = strip_comments(rd("parent.html"))
_parcss = re.sub(r"/\*.*?\*/", " ", rd("css/parent.css"), flags=re.S)

check("quiz.html gom khoa tra loi SAI", "noTerms.push(it.term)" in _qz)
# ⚠️ Ghi CA khi het gio va ca khi Khien Tim giu chuoi: khien chi cuu CHUOI, khong
#    doi viec tre chua nam duoc cau do. Nhanh `else` cua `reveal` phu ca hai ca.
check("quiz.html gui `wrong` len server", "wrong: noTerms" in _qz)
check("quiz.html xoa danh sach SAI khi lam lai", "noTerms=[]" in _qz)
check("js/progress.js chuyen tiep `wrong`", "ev.wrong = o.wrong.slice()" in _prog)
check("js/progress.js CHI gui `wrong` khi co", "if (o.wrong && o.wrong.length)" in _prog)

check("server: ProgressRequest nhan `Wrong`", "string[]? Wrong," in _mep)
# ⚠️ Sai khong the nhieu hon so cau KHONG dung — thieu chot nay thi
#    `{correct:5,total:5,wrong:[…20 khoa…]}` ve ra mot tuan bet bat cho dua tre lam
#    dung het.
check("server: KEP so khoa SAI theo `total - correct`",
      "CleanTerms(req.Wrong, total - correct, okTerms)" in _mep)
# ⚠⚠ PHEP KIEM QUAN TRONG NHAT CUA MUC NAY: cau SAI KHONG duoc di vao
#    `PROGRESS.terms` — tap do la chia khoa mo So Tay Thuat Ngu, nhet cau sai vao la
#    giai ma mot the bang mot cau tra loi SAI.
# ⚠️ LAY CA CAU LENH (toi `);`), KHONG dung `\([^)]*\)`. Ban dau toi viet
#    `[^)]*` va phep pha hoai `(okTerms ?? []).Concat(wrongTerms ?? [])` LOT qua —
#    regex dung o dau `)` dau tien nen doan cat ra khong he chua chu "wrongTerms".
#    Mot phep kiem cat nham pham vi thi no dang do mot cau lenh khong ton tai.
_bump = re.search(r"BumpProgressAsync\(.*?\);", _mep, re.S)
check("server: cau SAI KHONG di vao BumpProgressAsync (khong mo So Tay bang cau sai)",
      _bump is not None and "wrongTerms" not in _bump.group(0),
      _bump.group(0) if _bump else "khong tim thay loi goi")
check("server: truyen ca hai danh sach vao NHAT KY",
      "okTerms: okTerms" in _mep and "wrongTerms: wrongTerms" in _mep)
check("server: chan tap rong truoc khi ghi SS `wrong` (SS rong lam hong CA dong)",
      "wrongTerms is { Count: > 0 }" in _dyn and "okTerms    is { Count: > 0 }" in _dyn)
check("server: doc lai `ok`/`wrong` khi query nhat ky",
      'SS("ok"), SS("wrong")' in _dyn)

check("Report gom dung/sai theo TUNG KHOA cau", "termOk" in _rep_cs and "termNo" in _rep_cs)
check("Report tra `Terms` + `WeakCount`",
      "Terms: terms, WeakCount:" in _rep_cs)
# Cau sai nhieu nhat len truoc — do la thu phu huynh mo bao cao de tim.
check("Report xep chu de CAN LUYEN len truoc",
      "OrderByDescending(t => t.Wrong)" in _rep_cs)

# ⚠️⚠️ SERVER KHONG DUOC GIU TEN CHU DE. Ten song ngu nam o `js/quiz-index.js`
#    (server giu moc, client giu ten). Chep sang server la ban sao thu hai cua mot
#    bang ten, va no se lech dung vao ngay ai do doi ten mot the — tuc la thu noi
#    SAI ten bai hoc cua mot dua tre.
_topic_names = re.findall(r't:\s*\{\s*vi:\s*"([^"]+)"', rd("js/quiz-index.js"))
check("doc duoc bang ten chu de o client", len(_topic_names) >= 10,
      f"{len(_topic_names)} chu de")
# ⚠️ QUET TREN BAN DA BOC CHU THICH — lan chay dau bao hong vi tieu de mot khoi
#    comment o MeEndpoints viet "VI THIEN THACH TIM" (ten TIEN TE), trung voi ten
#    chu de "THIEN THACH" cua the `term_meteorite`. Day la loi "dem ca chu trong ghi
#    chu cua chinh minh" — da lap lai nhieu lan trong du an, moi phep kiem dang
#    "khong duoc chua X" deu phai boc comment truoc.
def _no_cs_comments(src):
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"//[^\n]*", " ", src)

_leak = [n for n in _topic_names
         if n in _no_cs_comments(_rep_cs) or n in _no_cs_comments(_mail_cs)
         or n in _no_cs_comments(_mep)]
check("server KHONG chep ten chu de nao (client giu ten)", not _leak, str(_leak[:3]))
# Email vi the dem chu de chu khong goi ten, va co duong dan sang trang phu huynh.
check("email dem so chu de can luyen", "cur.WeakCount > 0" in _mail_cs)
check("email co duong dan sang trang phu huynh (cho DUY NHAT goi duoc ten)",
      "/parent.html" in _mail_cs)

check("parent.html nap muc luc ngan hang cau hoi de lay TEN chu de",
      'src="js/quiz-index.js"' in rd("parent.html"))
check("parent.html gom khoa cau thanh the bang groupOf()",
      "AstroQQuestions.groupOf(x.term)" in _par)
check("parent.html KHONG go cung ten chu de nao",
      not [n for n in _topic_names if n in _par],
      str([n for n in _topic_names if n in _par][:3]))
# Khoa khong con trong bank (cau da bi go) van phai hien: bo qua no la am tham nuot
# mat mot phan ket qua cua tre.
check("parent.html van hien khoa khong con trong bank", "g ? (g.c || g.q[0]) : x.term" in _par)
check("parent.html xep chu de CAN LUYEN len truoc", "(b.no - a.no)" in _par)
# ⚠️ HO PHACH, KHONG PHAI DO. Day la bao cao hoc tap cua mot dua tre; mau do doc ra
#    thanh "con ban sai roi". Cung ly do da chot cho `.sum-note` va cho xu huong GIAM.
_weak_css = re.search(r"\.pt-topic\.weak[^}]*\}", _parcss)
check("chu de 'can luyen' to HO PHACH, khong to do",
      _weak_css is not None and "255,207,107" in _weak_css.group(0)
      and "ff8a8a" not in _weak_css.group(0),
      _weak_css.group(0)[:60] if _weak_css else "khong co rule")

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
# ⚠️ DANH SACH TEN MIEN DOC TU `check_quiz_bank.py`, KHONG CHEP LAI. Day tung la
#    BAN SAO THU BA cua cung mot luat (check_quiz_bank + check_srcquote + o day), va
#    ngay 06/08/2026 no bao hong vi hai file kia da noi rong con file nay thi chua.
#    Mot luat nam o ba cho la mot luat se lech o hai cho. Ly do CUA TUNG ten mien ghi
#    o `check_quiz_bank.py` — them ten mien moi thi them o do, khong them o day.
_ok_hosts_src = rd("scratchpad/check_quiz_bank.py")
OK_HOSTS = tuple(re.findall(
    r'"(https://[^"]+/)"',
    _ok_hosts_src[_ok_hosts_src.index("OK_HOSTS"):_ok_hosts_src.index("bad_host")]))
check("doc duoc danh sach ten mien tu check_quiz_bank.py (khong chep lai)",
      len(OK_HOSTS) >= 2, f"{len(OK_HOSTS)} ten mien")
_cx_urls = set(re.findall(r'url: "([^"]+)"', _cx))
check("moi URL nguon cua so tay thuoc danh sach ten mien da duyet",
      all(u.startswith(OK_HOSTS) for u in _cx_urls),
      f"la: {sorted(u for u in _cx_urls if not u.startswith(OK_HOSTS))}")
# ⚠️ (b) DOI MOT CHIEU, KHONG DOI TRUNG KHOP — sua 06/08/2026.
#     Ban cu doi `_cx_urls == _bank_urls`. Dung khi so tay va bank cung dan 12 URL,
#     nhung tu Dot 1 thi MOT THE chi liet 2–3 nguon TIEU BIEU trong khi 20 cau cua no
#     dan toi 8 trang — doi trung khop la doi the phai liet het moi trang, tuc bat the
#     phinh ra vo ich. Dieu THAT SU muon bao dam van nguyen: **moi URL cua so tay phai
#     co trong bank**, nho vay no da duoc `check_quiz_bank.py` kiem 200 that tren
#     Chromium, khong phai kiem 200 lan thu hai o day. Chieu nguoc lai khong can.
_bank_urls = set(re.findall(r'url: "([^"]+)"', _bank))
check("moi URL cua so tay deu co trong bank (de duoc kiem 200 mot lan)",
      _cx_urls <= _bank_urls,
      f"chi so tay, chua ai kiem 200: {sorted(_cx_urls - _bank_urls)}")

# ── (c) BAY CHUOI CAM CUA DOT 1 — CHO MU CUA MOI BO KIEM KHAC ────────────────
# ⚠️⚠️ VI SAO MUC NAY TON TAI. `check_srcquote.py` doi chieu 65 cau trich voi trang
#    nguon that, nhung no chi doc chuoi TIENG ANH — no **khong bao giờ** biet mot ban
#    va bang TIENG VIET da duoc ap hay chua. Bay dong duoi day la bay chinh sua noi
#    dung da phai yeu cau Gemini lam trong 10 vong ra soat (06/08/2026); moi dong la
#    mot loi CO THAT tung nam trong du lieu. Khong co phep kiem nay thi ai do "don
#    dep" hay dan de mot ban cu la chung lang le quay lai.
_VI_CAM = [
    ("biểu ảo",                  "khong phai thuat ngu — phai la 'bieu kien' (apparent)"),
    ("acting như",               "sot chu tieng Anh giua cau tieng Viet"),
    ("gần 4 lần",                "con so khong co trong cau trich nao"),
    ("hàng triệu năm ánh sáng",  "sai: cac sao duoc nhac ten deu duoi 1.000 nam anh sang"),
    ("dung nham",                "dap an nham — da thay bang hieu lam CO THAT"),
    ("dây mây",                  "dich sai 'metal rod' — phai la 'thanh sat'"),
    ("Bóng tối Trái Đất",        "SAI KHOA HOC o the NHAT thuc: do la bong MAT TRANG"),
]
# ⚠️ Quet tren code DA BOC COMMENT — chinh khoi ghi chu giai thich "vi sao khong dung
#    X" se bi dem la vi pham. Du an da mac loi nay 10 lan.
_dot1_src = strip_comments(_bank) + "\n" + strip_comments(_cx) + "\n" + strip_comments(_art)
for _c, _ly in _VI_CAM:
    check(f"khong con chuoi \"{_c}\" trong bank/so tay/bai doc",
          _c.lower() not in _dot1_src.lower(), f"— {_ly}")

# --- (7) duong vao + khong con loi hua thuong doc bai ---
# ⚠️ DUONG VAO DOI CHO 04/08/2026: So Tay khong con la the MOD-C trong learn.html,
# no la the MOD-06 tren dashboard (thay cho "Thu Vien Thien Van" chua co trang).
# Hai phep kiem duoi canh dung MOT duong vao — them lai the o learn.html thi bao
# hong, vi hai duong vao cho cung mot khu la hai cho phai sua moi lan doi ten.
_learn = rd("learn.html")
_dash_cx = strip_comments(rd("dashboard.html"))
check("dashboard.html co the MOD-06 dan sang codex.html",
      'href="codex.html"' in _dash_cx and "MOD-06" in _dash_cx)
for key in ("codex_tag", "codex_title", "codex_desc", "codex_btn"):
    check(f"dashboard.html: khoa `{key}` co o CA vi va en",
          rd("dashboard.html").count(key + ":") == 2,
          f"{rd('dashboard.html').count(key + ':')} lan")
check("learn.html KHONG con duong vao thu hai cho So Tay",
      "codex.html" not in strip_comments(_learn))
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
# WARN Duong ve tu dong, `startAuto`, `cancelAuto` nay do `js/mission-stage.js` giu
#   (tach 15/08/2026): chung la VO, khong phai noi dung nhiem vu.
_me2 = _me2 + rd("js/mission-stage.js")
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
_meraw = rd("js/mission-stage.js")
check("khoa i18n `win_auto` cua vo co o CA vi va en",
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
# ⚠️ SUY RA danh sách cờ, KHÔNG GHIM CHUỖI. Bản trước ghim nguyên văn
#    `"tour is null && intro1 is null && greeted is null) tour = true"`, nên khi thêm
#    cờ thứ tư (`map01Seen`, 01/08/2026) nó báo hỏng **đúng lúc code làm đúng** — cùng
#    loại lỗi "gán cứng" đã trả giá 6 lần. Nay: đếm số biến cờ khai trong handler rồi
#    đòi điều kiện phải liệt kê ĐỦ số đó.
_put_vars = set(re.findall(r"var (tour|intro1|greeted|map1)\s*=\s*req\?\.", _ep2))
_put_cond = re.search(r"if \((tour is null(?:[^)]*?))\)\s*\n?\s*tour = true", _ep2)
check("server: tim thay nhanh 'body rong -> tourSeen true'", bool(_put_cond))
check("server: nhanh do loai tru DU MOI co (them co moi khong lam vo no)",
      bool(_put_cond) and all(v + " is null" in _put_cond.group(1) for v in _put_vars),
      f"co: {sorted(_put_vars)} · dieu kien: {_put_cond.group(1) if _put_cond else '—'}")


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
# ⚠️ NOI DUNG 15/08/2026, VA NOI RO VI SAO. `dashboard.html` nay dung MENU THA:
#    hai nut VI/EN do `js/user-menu.js` dung tu bang `LANGS` (them mot ngon ngu
#    thi sua MOT cho). Neu cu doi markup tinh thi hoac phai chep bang do vao HTML
#    (hai nguon su that), hoac phai bo phep kiem nay — ca hai deu te hon.
#    ⇒ Trang thoa mot trong HAI duong, va duong thu hai co dieu kien RIENG:
#      · markup co `data-lang` du vi+en, HOAC
#      · nap `js/user-menu.js`, VA file do khai ca vi lan en la `ready:true`.
#    Va dieu bo cu that su bao ve — *nguoi dung BAM DUOC* — nay do
#    `smoke_lang_switch.py` chung minh tren Chromium o TUNG trang (no mo menu roi
#    moi do). Phep kiem tinh o day chi chan cai bay cu: mot trang tu tach khoi quy
#    uoc chung ma khong ai biet.
_um_src = strip_comments(rd("js/user-menu.js"))   # `_no_comments` chua khai o doan nay
_um_ready = set(re.findall(r'\{\s*code:\s*"([a-z]{2})",[^}]*ready:\s*true', _um_src))
check("js/user-menu.js khai DU 'vi' va 'en' la ngon ngu da co noi dung",
      {"vi", "en"} <= _um_ready, str(sorted(_um_ready)))

_calls, _missing, _partial = [], [], []
for _f in _html_pages:
    _h = rd(_f)
    if "initLang" not in _h:
        continue
    _calls.append(_f)
    if 'src="js/user-menu.js"' in _h:
        continue                      # danh sach do module dung — da kiem o tren
    # WARN Trang nhiem vu: `js/mission-stage.js` dung ca header, ke ca nut VI/EN. Cung
    #   ca voi user-menu.js o tren. VAN CON RANG: file vo phai khai du ca hai ngon ngu.
    if 'src="js/mission-stage.js"' in _h:
        if {"vi", "en"} <= set(re.findall(r'data-lang="([a-z]{2})"',
                                          rd("js/mission-stage.js"))):
            continue
    _langs = set(re.findall(r'data-lang="([a-z]{2})"', _h))
    if not _langs:
        _missing.append(_f)
    elif not {"vi", "en"} <= _langs:
        _partial.append((_f, sorted(_langs)))

check("co trang nao goi initLang (phep kiem khong dat rong)", len(_calls) >= 10,
      f"{len(_calls)} trang")
check("MOI trang goi initLang deu co markup data-lang", not _missing, str(_missing))
check("moi trang do co DU ca 'vi' va 'en'", not _partial, str(_partial))
# ⚠️ Ngon ngu CHUA co noi dung phai nam NGOAI `.lang-switch`: `initLang` gan su
#    kien cho MOI `.lang-switch button`, nen de chung vao trong la bam mot ngon
#    ngu chua co la ghi mot ma khong ton tai vao `astroq-lang` — va tu do trang
#    lang le quay ve tieng Viet ma khong ai hieu vi sao.
#    ⚠️ Doi DUNG hinh dang nhanh re, khong chi doi "co chuoi data-lang-soon":
#       phep kiem dau cua toi chi hoi chuoi, va phep thu pha hoai cho thay no MU —
#       gan `data-lang` cho ca hai loai van "dat". Chi bo smoke bat duoc. Nay hoi
#       dung hai nhanh: `ready` -> data-lang, con lai -> data-lang-soon.
check("ngon ngu 'sap co' KHONG mang thuoc tinh data-lang",
      bool(re.search(r'if\s*\(l\.ready\)\s*b\.setAttribute\("data-lang",\s*l\.code\);\s*'
                     r'else\s*b\.setAttribute\("data-lang-soon",\s*l\.code\);', _um_src)),
      "phai la hai nhanh re: ready -> data-lang, con lai -> data-lang-soon")

# Truyen selector RIENG cho initLang la duong quay lai dung cai bay tren: dat ten
# khac `.lang-switch` thi khung dung chung o css/common.css khong ap vao nua.
_own_sel = [_f for _f in _calls
            if re.search(r"initLang\([^)]*,\s*['\"]", rd(_f))]
check("khong trang nao truyen selector RIENG cho initLang", not _own_sel, str(_own_sel))

# --- (2) Khong trang nao nap script tu TEN MIEN NGOAI ---
# ⚠️ Du an da tra gia de bo 2 ket noi ngoai (tu host font: 621 KB -> 101 KB) va co
#    y KHONG nap SDK Firebase o trang can muot.
#    Phep kiem nay KHONG doi 0 ngay mot: no GHIM danh sach hien tai lai, de them
#    trang thu ba la biet ngay, va TU THAT LAI khi bo dan phu thuoc ngoai.
# 31/07/2026: `mission-earth.html` đã bỏ three.js (bậc 5) nên rời khỏi danh sách.
# 07/08/2026: `explorer.html` cũng rời — three.js + SDK Firebase nay TU HOST ở
#   `vendor/` (xem `scratchpad/vendor_deps.py`). Danh sách nay RỖNG, và phép kiểm
#   thứ hai biến nó thành hàng rào vĩnh viễn: **không trang nào được nạp script
#   từ tên miền ngoài nữa**.
#   ⚠️ ĐỪNG NỚI LẠI. Ba cái giá đã đo được: ① service worker KHÔNG cache đàng
#      hoàng được phản hồi cross-origin không CORS, nên một tên miền ngoài là
#      **đóng cửa hẳn đường PWA**; ② `explorer.html` nằm trên luồng onboarding
#      BẮT BUỘC, unpkg hỏng = trẻ mới rơi vào đường lùi 12 giây; ③ bản `.min`
#      tự host còn nhẹ hơn bản CDN đang dùng 90 KB gzip.
#   Có phép kiểm chạy thật trên Chromium canh cùng chuyện này (`smoke_vendor.py`,
#   chặn cứng 4 tên miền rồi đòi app vẫn dựng đủ cảnh) — phép kiểm ở đây chỉ
#   soi văn bản, nên hai cái bổ cho nhau.
_KNOWN_CDN = set()
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

# ══════════════════════════════════════════════════════════════
print("\n=== [15] Cong lo trinh: server giu luat, client chi doc"
      " (docs/decisions/003) ===")
_mis_cs = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"),
                  encoding="utf-8").read()
_gate_js = rd("js/route-gate.js")
_exp = rd("explorer.html")

# --- Server PHAI co du bo luat ---
for _sym in ("UnlockRatio", "UnlockGate", "GateMet", "Route", "UnlockedPlaces"):
    check(f"Missions.cs co {_sym}", _sym in _mis_cs)

_m = re.search(r"UnlockRatio\s*=\s*([\d.]+)", _mis_cs)
check("UnlockRatio la mot hang so doc duoc", bool(_m), str(_m and _m.group(1)))
_ratio = float(_m.group(1)) if _m else 0
check("UnlockRatio nam trong khoang hop ly (0,5..1)", 0.5 <= _ratio <= 1.0,
      str(_ratio))

_m = re.search(r"Route\s*=\s*\[([^\]]*)\]", _mis_cs)
_route = re.findall(r'"(\w+)"', _m.group(1)) if _m else []
check("Missions.Route doc duoc va khong rong", len(_route) >= 1, str(_route))

# --- CLIENT KHONG DUOC TU TINH LUAT ---
# ⚠️ Day la phep kiem quan trong nhat cua muc nay. Client giu ban sao cua ti le thi
#    som muon lech, va ben lech se la ben NOI VOI TRE.
# ⚠️ PHAI BOC CHU THICH TRUOC KHI TIM. Lan chay dau tien phep kiem nay bao hong vi
#    chinh doan ghi chu GIAI THICH luat co chu "70%" — dung cai bay "dem ca chu trong
#    ghi chu cua chinh minh" da gap 8 lan trong du an. Ghi chu noi ro luat la thu NEN
#    co; thu phai kiem la CODE.
_gate_code = strip_comments(_gate_js)
_nums = set(re.findall(r"\b0?\.\d+\b|\b\d+\b", _gate_code))
check("js/route-gate.js KHONG chua ti le cong trong CODE (khong tu tinh)",
      str(_ratio) not in _nums and f"{_ratio:.2f}" not in _nums
      and str(int(_ratio * 100)) not in _nums,
      f"cac so trong code: {sorted(_nums)}")
check("js/route-gate.js KHONG tu tinh ceil/floor/round cho cong",
      not re.search(r"Math\.(ceil|floor|round)", _gate_code))
check("js/route-gate.js doc unlockedPlaces do server tra",
      "unlockedPlaces" in _gate_js)
check("explorer.html KHONG gan cung danh sach hanh tinh mo khoa",
      "unlockedPlaces =" not in _exp and "unlockedPlaces=[" not in _exp)

# --- Diem den dau tien: ban sao duy nhat o client PHAI khop server ---
# ⚠️ `FIRST_PLACE` la mot con so client giu trong khi server moi la nguon su that —
#    dung thu du an da tra gia 6 lan. Khong bo duoc (may sach + chua dang nhap thi
#    khong hoi duoc server), nen PHAI co phep kiem doi chieu.
_m = re.search(r'FIRST_PLACE\s*=\s*"(\w+)"', _gate_js)
check("route-gate.js khai FIRST_PLACE", bool(_m), str(_m and _m.group(1)))
check("FIRST_PLACE khop Missions.Route[0] cua server",
      bool(_m) and bool(_route) and _m.group(1) == _route[0],
      f"client={_m and _m.group(1)} server={_route[0] if _route else None}")

# --- Cong phai nam TRONG selectBody, khong o _pick ---
# 6 duong vao selectBody: raycast, nhan ten, nut Fly to Sun, danh sach bang trai,
# Prev/Next, dieu huong vung. Chan o mot duong la de ho nam duong.
_sel = re.search(r"\n  selectBody\(body\)\{(.*?)\n  \}", _exp, re.S)
check("tim thay than ham selectBody", bool(_sel))
check("cong nam TRONG selectBody",
      bool(_sel) and "AstroQGate" in _sel.group(1) and "canVisit" in _sel.group(1))
_pick = re.search(r"\n  _pick\(e\)\{(.*?)\n  \}", _exp, re.S)
check("cong KHONG dat o _pick (de khong ho 5 duong con lai)",
      bool(_pick) and "canVisit" not in _pick.group(1))
check("bam vao cho khoa thi NOI RO, khong im lang",
      bool(_sel) and "explain" in _sel.group(1))

# --- Bam vao hanh tinh khoa phai co loi giai thich + duong di tiep ---
check("explorer dang ky onBlocked de mo modal giai thich",
      "AstroQGate.onBlocked" in _exp)
check("modal khoa dan sang mission-earth.html (co viec lam duoc)",
      "gateGo" in _exp and "mission-earth.html" in _exp)
# ⚠️ Khong doc duoc tien do thi phai noi DUNG ly do, dung noi "con n buoc nua" —
#    luc ay con so do la bia (gate = 0 vi chua hoi duoc server).
check("khong doc duoc tien do -> dung cau rieng theo g.known (KHONG theo g.live)",
      "gateMsgOffline" in _exp and "g.known" in _exp)

# --- i18n: du ca vi va en ---
for _k in ("gateTitle", "gateMsg", "gateMsgOffline", "gateGo", "gateStart"):
    check(f"khoa i18n {_k} co o CA vi va en", _exp.count(_k + ":") == 2,
          f"{_exp.count(_k + ':')} lan")

# --- Duong ghi/doc cache: explorer khong co token nen phai co trang ghi ho ---
check("explorer.html VAN khong nap firebase-auth.js (SDK 233 KB)",
      'src="js/firebase-auth.js"' not in _exp)
_dash = rd("dashboard.html")
check("dashboard.html lam moi cache cong lo trinh", "AstroQGate.feed" in _dash)
# ⚠️ VÀ CHỈ GỌI `/me/missions` MỘT LẦN cho cả trang. Hai chỗ cần cùng câu trả lời
#    (cổng lộ trình + màn Comet chúc mừng); gọi riêng là hai lượt mạng —
#    `smoke_earth_done.py` canh con số đó, ở đây canh CÁCH LÀM.
check("dashboard.html dung CHUNG mot loi goi /me/missions (missionsShared)",
      "missionsShared" in _dash and _dash.count("AstroQProgress.missions()") == 1,
      f"{_dash.count('AstroQProgress.missions()')} cho goi truc tiep")
check("missions.html rot ket qua san co vao cache (khong goi API lan hai)",
      "AstroQGate.feed" in rd("missions.html"))
for _f in ("explorer.html", "dashboard.html", "missions.html"):
    check(f"{_f}: nap js/route-gate.js", 'src="js/route-gate.js"' in rd(_f))

# --- Cong mac dinh TAT: bat vinh vien se khoa vinh vien 7 mau vat + 2 huy hieu ---
# Xem ghi chu trong explorer.html va docs/decisions/003.
check("cong mac dinh TAT (setActive khong bat vo dieu kien)",
      "onboard" in _exp and "AstroQGate.setActive(true)" in _exp)
_spec_cs = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Specimens.cs"),
                   encoding="utf-8").read()
_planet_specs = set(re.findall(r'"planet:(\w+)"', _spec_cs))
_orphan = sorted(_planet_specs - set(_route))
check("neu bat cong VINH VIEN thi se co mau vat khoa vinh vien"
      " -> ghi chu phai noi ro so luong",
      not _orphan or str(len(_orphan)) in _exp,
      f"{len(_orphan)} mau vat ngoai Route: {_orphan}")

# ══════════════════════════════════════════════════════════════
print("\n=== [15b] Nhip phim Comet dan duong o ban do (buoc 1-4 cua 003) ===")
_mo = rd("js/map-onboard.js")
_mocode = strip_comments(_mo)
_ecss = rd("css/explorer.css")

check("explorer.html nap js/map-onboard.js", 'src="js/map-onboard.js"' in _exp)
check("explorer.html nap css/mascot.css (box thoai dung chung)",
      'href="css/mascot.css"' in _exp)
check("box thoai dung class chung .aq-say, khong ve lai vo box",
      'class="aq-say mo-say"' in _exp)

# --- ① Man warp: PHAI buoc nhanh `traveling`, khong di qua travelTo() ---
# `travelTo` chon chu bang `region.id === currentRegion.id`, ma luc vao trang
# currentRegion DA LA solar-system -> no se in "Dang toi" chu khong phai "Dang du hanh toi".
_gw = re.search(r"function gateWarpShow\(\)\{(.*?)\n  \}", _exp, re.S)
check("co ham rieng dung man warp cho luot vao", bool(_gw))
check("man warp luot vao buoc nhanh T('traveling')",
      bool(_gw) and "T('traveling')" in _gw.group(1))
check("man warp luot vao KHONG goi travelTo (no tu dat transitioning + doi vung)",
      bool(_gw) and "travelTo" not in _gw.group(1))
check("dung lai phan VE cua man warp co san (startWarp/stopWarp)",
      "startWarp()" in (_gw.group(1) if _gw else "") and "stopWarp" in _exp)

# --- Nhip phim phai khoi dong SAU applyLanguage ---
# ⚠️ Loi that da gap: `T()` doc `window.LANG`, ma bien do chi duoc dat trong
#    applyLanguage(). Khoi dong som -> tre Viet thay man warp bang tieng Anh.
_i_start = _exp.find("startMapOnboard();")
_i_lang = _exp.find("applyLanguage((savedLang")
check("goi startMapOnboard() SAU applyLanguage (khong thi warp ra tieng Anh)",
      _i_start > 0 and _i_lang > 0 and _i_start > _i_lang,
      f"startMapOnboard@{_i_start} applyLanguage@{_i_lang}")

# --- ② Lam noi Trai Dat: dung NHAN da co, khong khoet o sang kieu tour ---
check("to nhan qua #labels [data-body-id] (nhan bam theo hanh tinh moi khung hinh)",
      "#labels [data-body-id]" in _exp and "paintGateLabels" in _exp)
# ⚠️ BỐN PHÉP KIỂM DƯỚI ĐÂY SOI **CODE**, KHÔNG SOI CHỮ. Lần chạy đầu cả ba đều báo
#    hỏng vì chính đoạn ghi chú GIẢI THÍCH *"không dùng .tour-hole"* / *"không dùng
#    filter:grayscale"* / *"trước đây nằm inline trong style.cssText"*. Đây là lần thứ
#    CHÍN dự án gặp lỗi "đếm cả chữ trong ghi chú của mình". Ghi chú nói rõ vì sao
#    KHÔNG làm một việc là thứ NÊN CÓ; thứ phải kiểm là code.
_expcode = strip_comments(_exp)
_ecsscode = re.sub(r"/\*.*?\*/", " ", _ecss, flags=re.S)
check("KHONG dung .tour-hole cho ban do (o sang tinh, hanh tinh thi dang bay)",
      "tour-hole" not in _expcode)
check("KHONG dung filter:grayscale de lam mo nhan khoa",
      "grayscale" not in _ecsscode)
check("nhan hanh tinh dung class .body-lbl + co CSS that",
      "el.className='body-lbl'" in _expcode and ".body-lbl{" in _ecsscode)
# ⚠️ Chỉ soi TRONG `_makeLabel`, không quét cả file: `style.cssText` còn được dùng
#    hợp lệ ở chỗ khác (`explorer.html:1712` đặt vị trí cho container của
#    CSS2DRenderer vùng lân cận). Quét cả file là báo oan một chỗ đúng.
_mk = re.search(r"_makeLabel\(cfg, onClick\)\{(.*?)\n  \}", _expcode, re.S)
check("tim thay than ham _makeLabel", bool(_mk))
check("_makeLabel KHONG con style inline / handler mau inline",
      bool(_mk) and "cssText" not in _mk.group(1)
      and "onmouseenter" not in _mk.group(1))
# Vong sang phai o rule GOC, khong chi trong keyframes — tat animation thi phai con.
_gs = re.search(r"\.body-lbl\.gate-start\{([^}]*)\}", _ecss)
check("vong sang cua nhan 'bat dau' nam o rule GOC (con lai khi tat animation)",
      bool(_gs) and "box-shadow" in _gs.group(1))

# --- ③ Box thoai: neo day, chu to, khong de len bang thong tin ---
_ms = re.search(r"\.mo-say\{([^}]*)\}", _ecss)
check("box thoai neo DAY man hinh", bool(_ms) and "bottom:" in _ms.group(1))
_ml = re.search(r"\.mo-line\{([^}]*)\}", _ecss)
_fs = re.search(r"font-size:([\d.]+)px", _ml.group(1) if _ml else "")
check("co chu >= 16,5px (yeu cau 'chu to, ro rang, de doc')",
      bool(_fs) and float(_fs.group(1)) >= 16.5, str(_fs and _fs.group(1)))
check("bang thong tin mo thi box doi cho (khong de nhau)",
      "#info.open ~ .mo-say" in _ecss)
# ⚠️ Ban dau toi `visibility:hidden` box o man hep — cau hoi + nut OK nam TRONG box,
#    an no la tre tren dien thoai khong thay duong di tiep va KET CUNG.
_narrow = re.search(r"@media \(max-width:720px\)\{[^{]*#info\.open ~ \.mo-say\{([^}]*)\}",
                    _ecss)
check("man hep: box DOI CHO chu KHONG bi an (an la tre ket cung)",
      bool(_narrow) and "hidden" not in _narrow.group(1),
      str(_narrow and _narrow.group(1)))
# ⚠️ `--info-w` = 400px, nen tren man 390px thi calc() ra AM -> box co ve 0.
check("rule doi cho gioi han o min-width:721px (khong thi be rong ra so AM)",
      re.search(r"@media \(min-width:721px\)\{\s*#info\.open ~ \.mo-say", _ecss)
      is not None)

# --- ④ Bam la sang NGAY, khong con moc cho ---
# ⛔ `READ_MS` DA BO HAN 02/08/2026. `003` chot "10 giay la SAN", `005` noi len 15 —
#    nhung cai san do sinh ra khi nhip phim CHUA co nhip 0: Comet noi xong la box tu an,
#    khong co nut nao, nen phai co dong ho moi biet khi nao hoi tiep. Nay nhip 0 ket bang
#    mot NUT do tre chu dong bam, ma mot cai nut ten "Tiep tuc" roi bat ngoi doi them 15
#    giay trong im lang thi chinh no la loi. Chu du an choi that va chot: bam la sang ngay.
#    Phep kiem nay giu de khong ai dung lai cai dong ho do.
check("KHONG con moc cho `READ_MS` nao",
      re.search(r"READ_MS\s*=\s*\d+", _mocode) is None)
check("KHONG con `setTimeout(ask` (bam la hoi ngay)",
      "setTimeout(ask" not in _mocode)
check("nut cuoi nhip 0 goi thang `ask()`",
      "button(null); ask(); }" in _mocode)
check("hoi xong KHONG dong bang thong tin (moc doc la SAN, khong phai han)",
      "_closeInfo" not in _mocode and "classList.remove('open')" not in _mocode)
check("dong ho chi chay khi bang thong tin DA MO (khong dem luc camera con bay)",
      "MutationObserver" in _mocode and "reading" in _mocode)
check("chi tinh khi mo dung TRAI DAT, khong tinh hanh tinh khac",
      "selectedId() !== \"earth\"" in _mocode or "selectedId() !== 'earth'" in _mocode)
check("bam OK thi sang mission-earth.html",
      "mission-earth.html" in _exp and "onGo" in _mocode)

# --- i18n cua nhip phim: du ca vi va en ---
# `l3`/`l3b`/`l4` la NHIP 0, them 02/08/2026 (`docs/decisions/005`).
for _k in ("l1", "l2", "l3", "l3b", "l4", "ask", "next", "ok", "nm", "tag"):
    check(f"khoa thoai '{_k}' co o CA vi va en",
          len(re.findall(r"\b" + _k + r":", _mo)) == 2,
          f"{len(re.findall(chr(92) + 'b' + _k + ':', _mo))} lan")
check("doi ngon ngu giua chung thi dich lai loi Comet",
      "AstroQMapOnboard.setLang" in _exp and "setLang:" in _mo)
# ⚠️ setLang PHAI biet ca hai trang thai moi. Thieu mot cai thi doi VI/EN giua nhip 0
#    la cau do dung nguyen tieng cu tren man hinh — loi im lang.
check("setLang xu ly ca trang thai 'atmo' va 'spin' cua nhip 0",
      '"atmo"' in _mocode and '"spin"' in _mocode)

# --- NHIP 0: khi quyen -> moi xoay -> ngay/dem (`005` muc 1) ---
_mo_code = strip_comments(_mo)
check("nhip 0: Comet chi bau KHI QUYEN (khop dong 'Khi quyen: Nito + oxy' cua bang)",
      "khí quyển" in _mo_code and "atmosphere" in _mo_code)
# ⚠️ Vanh khi quyen trong canh dang duoc ve DAY GAP ~2 LAN ban kinh hanh tinh. Chi vao
#    do ma khong noi gi la DAY SAI MO HINH TU DUY. Duong re hon va trung thuc hon la
#    Comet noi thang ra — va do la mot RANG BUOC cua `005`, khong phai mot cau van tuy y.
check("nhip 0: NOI THAT rang vanh khi quyen dang ve day qua",
      "mỏng hơn thế rất nhiều" in _mo_code and "far thinner" in _mo_code)
check("nhip 0: MOI tre XOAY de ngam ngay/dem",
      "xoay quanh Trái Đất" in _mo_code and "spin around Earth" in _mo_code)
# ⚠️ THEM 02/08/2026 — chu du an choi that va bao: *"sau do khong hien gi tiep de biet
#    la cho hay lam gi?"*. Nhip 0 co mot moc SAN roi moi hoi "san sang chua?", va trong
#    khoang do box thoai TU AN de nhuong cho ngam — im lang thi doc ra nhu trang bi treo.
check("nhip 0: NOI RO bam gi de di tiep (khong de tre ngoi doi trong im lang)",
      "bấm <b>Tiếp tục</b>" in _mo_code and "hit <b>Next</b>" in _mo_code)
check("nhip 0: noi ro mot nua NGAY mot nua DEM",
      "ban ngày" in _mo_code and "ban đêm" in _mo_code)
# ⛔ QUA CAU 3D KHONG BAO GIO DUOC MANG DIEU KIEN THANG (`005` rang buoc tu nay).
#    Dieu kien thang do tren camera-orbit chinh la loi da lam buoc `rotation` ban 3D
#    KHONG THE HOAN THANH va treo vinh vien o che do giam chuyen dong.
check("nhip 0 KHONG co dieu kien thang (chi la cho QUAN SAT)",
      "finishStep" not in _mo_code and "onWin" not in _mo_code)

# --- Duong lui 12 giay: NOI MOT CAU roi hay di (`005` muc 5) ---
check("duong lui KHONG con `location.replace` IM LANG",
      "showPerfNote('fail')" in _exp)
check("duong lui co cau giai thich o CA vi va en",
      len(re.findall(r"\bsceneFailNote:", _exp)) == 2)
check("duong lui VAN tu di tiep (khong dung them mot cua chan khi mang yeu)",
      re.search(r"showPerfNote\('fail'\);\s*setTimeout", _exp) is not None)

# --- perfMode: MOT khoa dung chung cho ca app (`005` muc 6) ---
_uic = rd("js/ui-common.js")
check("ui-common khai khoa dung chung `astroq-perf`", '"astroq-perf"' in _uic)
check("ui-common xuat getPerf/setPerf/slowLink",
      all(k in _uic for k in ("getPerf:getPerf", "setPerf:setPerf", "slowLink:slowLink")))
check("explorer DOC lai lua chon giam cau hinh luc vao trang",
      "AstroQ.getPerf()" in _exp)
check("explorer GHI lai lua chon khi bam cong tac", "AstroQ.setPerf(" in _exp)
check("doi o tab khac thi tab nay theo (nghe su kien storage)",
      re.search(r"e\.key !== AstroQ\.LS_PERF", _exp) is not None)
# ⚠️ Tu phat hien KHONG DU: [Chua kiem chung] Network Information API Safari/iOS khong
#    ho tro, ma iPad la thiet bi hay choi nhiem vu nay nhat. Nen no chi la lop (a).
check("dai nhac mang kem chi MOI khi CHUA bat va CHUA tung bo qua",
      "AstroQ.slowLink() && !AstroQ.getPerf()" in _exp)
check("dai nhac giu KHOA i18n chu khong giu chuoi (doi VI/EN thi dich theo)",
      "perfNoteKind" in _exp and "paintPerfNote()" in _exp)
for _k in ("perfNote", "perfNoteGo", "perfNoteX", "sceneFailNote", "sceneFailGo"):
    check(f"khoa dai nhac '{_k}' co o CA vi va en",
          len(re.findall(r"\b" + _k + r":", _exp)) == 2)

# --- Nhip phim KHONG chay khi khong co ?onboard=1 ---
check("nhip phim chi chay khi cong BAT (khong pha lan vao ban do binh thuong)",
      "AstroQGate.active()" in _exp and "startMapOnboard" in _exp)

# ══════════════════════════════════════════════════════════════
print("\n=== [15c] Doi luong onboarding: ban do TRUOC, tour SAU (buoc 7-8 cua 003) ===")
_dashcode = strip_comments(_dash)
_af = rd("js/auth-flow.js")
_tour = rd("js/onboard-tour.js")

# --- ⑦ Duong vao: select -> ban do, KHONG qua dashboard ---
check("select.html (auth-flow) dan sang explorer.html?onboard=1",
      "explorer.html?onboard=1" in _af)
check("auth-flow KHONG con dan thang sang dashboard sau khi chon nhan vat",
      'href="dashboard.html"' not in strip_comments(_af))
check("dashboard co luoi an toan mapFirst() cho duong DANG NHAP",
      "mapFirst" in _dashcode and "explorer.html?onboard=1" in _dashcode)

# --- Chong vong lap: dashboard PHAI doc cache truoc khi day ---
# ⚠️ explorer.html khong co token nen khong ghi duoc co len server; thieu cache thi
#    dashboard -> ban do -> nhiem vu -> dashboard -> ban do -> ... vinh vien.
check("map-onboard ghi cache 'da di qua ban do'",
      "astroq-map01-seen" in _mo)
check("dashboard DOC cache truoc khi day sang ban do (chong vong lap)",
      "astroq-map01-seen" in _dashcode)
_mf = re.search(r"function mapFirst\(\)\{(.*?)\n  \}", _dashcode, re.S)
check("tim thay than ham mapFirst", bool(_mf))
check("mapFirst doc cache TRUOC khi goi getOnboarding",
      bool(_mf) and _mf.group(1).index("astroq-map01-seen")
                   < _mf.group(1).index("getOnboarding"))
check("mapFirst khong doc duoc co thi KHONG day (khong nem tre da hoc xong ve lai)",
      bool(_mf) and re.search(r"!o\s*\|\|\s*!o\.ok", _mf.group(1)) is not None)
check("cache ghi o CA duong OK lan duong lui (khong thi tre ket vong lap khi mang yeu)",
      strip_comments(_mo).count("markSeen()") >= 2)

# --- ⑦ Tour doi xuong sau nhiem vu 1, xep sau man chuc mung ---
check("dashboard KHONG con goi AstroQTour.autoStart o luc boot",
      "tourThen" in _dashcode)
check("man chuc mung nhan callback va goi tour SAU do",
      "earthDoneGuide(tourThen)" in _dashcode)
_edg = re.search(r"function earthDoneGuide\(next\)\{(.*?)\n  \}\n", _dashcode, re.S)
check("tim thay than ham earthDoneGuide", bool(_edg))
# ⚠️ Nhanh nao `return` ma quen goi `next()` la TRE MAT LUON MAN DAN THAM QUAN,
#    va mat im lang. Moi loi ra phai di qua `done()`.
check("MOI nhanh ra cua earthDoneGuide deu goi done() (khong lam mat tour)",
      bool(_edg) and "return;" not in _edg.group(1),
      "con nhanh 'return;' tran khong goi done()")
check("tourThen kiem AstroQTour.isOpen (hai overlay cung mo = den kit)",
      "AstroQTour.isOpen()" in _dashcode)

# --- ⑦ mission-intro nghi huu ---
check("dashboard KHONG con nap js/mission-intro.js",
      'src="js/mission-intro.js"' not in _dash)
check("dashboard KHONG con nap css/mission-intro.css",
      'href="css/mission-intro.css"' not in _dash)
# ⚠️ VÀ BA FILE ĐÓ ĐÃ XOÁ HẲN (01/08/2026, sau khi commit nên tra lại được:
#    `git show 1515e9c:js/mission-intro.js`). Phép kiểm này chặn đúng một kiểu tai nạn:
#    một lượt làm việc sau tạo lại file mà KHÔNG nối vào trang nào — lúc đó dự án có
#    thêm một nhánh chết, và nhánh chết là thứ đã bắt dự án sửa `termsData.ts` HAI LẦN.
for _f in ("js/mission-intro.js", "css/mission-intro.css",
           "scratchpad/smoke_mission_intro.py"):
    check(f"{_f} da xoa han (khong de lai nhanh chet)",
          not os.path.exists(os.path.join(ROOT, _f)))
check("dashboard KHONG con goi AstroQMissionIntro",
      "AstroQMissionIntro" not in _dashcode)

# --- ⑦ Loi thoai buoc 7 cua tour da viet lai, CA vi va en ---
# ⚠️ Cau cu "hay khoi dong dong co thoi!" noi mot viec da xay ra tu lau khi tour
#    chay SAU nhiem vu. Bao gom ca nhan nut.
_tcode = strip_comments(_tour)
check("tour: bo loi thoai 'khoi dong dong co' (vo nghia khi tour chay sau nhiem vu)",
      "khởi động động cơ" not in _tcode.lower())
check("tour: bo nhan nut 'fire up the engines' o ban EN",
      "fire up the engines" not in _tcode.lower())
_ready = re.search(r'key:\s*"ready".*?\n    \}', _tcode, re.S)
check("tour: buoc cuoi co lo thoai moi o CA vi va en",
      bool(_ready) and "vi:" in _ready.group(0) and "en:" in _ready.group(0))

# --- ⑧ Duong lui khi three.js khong nap duoc ---
check("map-onboard co nhanh onSceneFail khi canh 3D khong dung duoc",
      "onSceneFail" in _mo and "WARP_MAX_MS" in _mo)
check("explorer khai onSceneFail -> di thang vao nhiem vu (trang 2D, khong can CDN)",
      "onSceneFail" in _exp and "mission-earth.html" in _exp)
_wm = re.search(r"WARP_MAX_MS\s*=\s*(\d+)", strip_comments(_mo))
check("han cho canh 3D nam trong khoang hop ly (8-15s)",
      bool(_wm) and 8000 <= int(_wm.group(1)) <= 15000, str(_wm and _wm.group(1)))

# --- Bon co onboarding: client PHAI doc lai DU nhung gi server tra ---
# ⚠️ LOI THAT DA GAP: lop boc bo roi `earth1Greeted`, nen `earthDoneGuide` doc ra
#    undefined va Comet chuc mung LAI moi lan mo dashboard. Co van duoc GHI len server
#    day du, chi la khong ai DOC lai. Bo smoke khong bat duoc vi no gia lap chinh
#    `AstroQAuth`. Phep kiem nay doi chieu hai ben.
_fa = rd("js/firebase-auth.js")
_me_cs = io.open(os.path.join(SV, "src/AstroqSV.Api/Endpoints/MeEndpoints.cs"),
                 encoding="utf-8").read()
_dto = re.search(r"OnboardingDto\(DynamoContext\.Onboarding o\) => new\s*\{(.*?)\n    \};",
                 _me_cs, re.S)
check("tim thay OnboardingDto cua server", bool(_dto))
_flags = set(re.findall(r"^\s*(\w+)\s*=", _dto.group(1), re.M)) if _dto else set()
_flags = {f for f in _flags if not f.endswith("At")}     # bỏ mốc thời gian
# ⚠️ SOI TRONG ĐÚNG KHỐI `return` CỦA `getOnboarding`, KHÔNG QUÉT CẢ FILE. Lần thử phá
#    hoại cho thấy quét cả file là VÔ DỤNG: bỏ `map01Seen` khỏi `getOnboarding` thì tên
#    đó vẫn còn ở `setOnboarding` và trong chú thích, nên phép kiểm vẫn "đạt" trong khi
#    lỗi thật (đọc ra `undefined`) vẫn nguyên — đúng cái đã xảy ra với `earth1Greeted`.
_go = re.search(r"async getOnboarding\(\)\{(.*?)\n  \},", _fa, re.S)
_so = re.search(r"async setOnboarding\(patch\)\{(.*?)\n  \},", _fa, re.S)
check("tim thay than getOnboarding + setOnboarding o client", bool(_go) and bool(_so))
# ⚠️ KHỚP THEO **KHOÁ THUỘC TÍNH** (`map01Seen:`), KHÔNG KHỚP CHUỖI TRẦN. Lần thử phá
#    hoại thứ hai vẫn lọt: xoá dòng `map01Seen: …` mà để lại `map01SeenAt: …` thì chuỗi
#    trần `"map01Seen"` VẪN khớp (nó là tiền tố của `map01SeenAt`). Đúng bài học
#    `em-spotlight`/`em-spotlightXX` đã ghi ngày 30/07: một phép thử phá hoại không làm
#    phép kiểm đỏ có thể nghĩa là PHÉP KIỂM mù, không phải sản phẩm đúng.
for _nm, _blk in (("getOnboarding", _go), ("setOnboarding", _so)):
    _body = _blk.group(1) if _blk else ""
    _miss = sorted(f for f in _flags if (f + ":") not in _body)
    check(f"client {_nm}() DOC LAI du moi co server tra ve",
          not _miss, f"thieu: {_miss}")
for _f in ("map01Seen", "earth1Greeted"):
    check(f"server: SetOnboardingAsync nhan {_f}",
          _f in io.open(os.path.join(SV, "src/AstroqSV.Api/Data/DynamoContext.cs"),
                        encoding="utf-8").read())
# ⚠️ Nhanh "body rong = tourSeen true" phai loai tru DU CA BON co.
_put = re.search(r"if \(tour is null && intro1 is null[^)]*\)", _me_cs)
check("nhanh 'body rong = tourSeen true' loai tru DU CA BON co",
      bool(_put) and "map1 is null" in _put.group(0) and "greeted is null" in _put.group(0),
      str(_put and _put.group(0)))

# ══════════════════════════════════════════════════════════════
print("\n=== [15d] Man loading Luna: chuyen canh dashboard -> Ban Do Thien Ha ===")
# Việc MỚI của js/warp-screen.js (chốt 01/08/2026). Nó SUÝT mất hết người gọi khi tour
# dời xuống sau nhiệm vụ 1 và mission-intro nghỉ hưu; chủ dự án chốt cho việc mới.
_ws = rd("js/warp-screen.js")
check("dashboard VAN nap warp-screen + space-scene",
      'src="js/warp-screen.js"' in _dash and 'src="js/space-scene.js"' in _dash)
check("dashboard CO goi AstroQWarp.play (module khong con mo coi)",
      "AstroQWarp.play(" in _dashcode)
_mw = re.search(r"mapLink\.addEventListener\(\"click\", function\(e\)\{(.*?)\n  \}\);",
                _dashcode, re.S)
check("tim thay handler chuyen canh o the MOD-03", bool(_mw))
# ⚠️ Chặn hết cách mở của trình duyệt là lấy đi một hành vi người dùng KHÔNG hiểu vì
#    sao mất. Ctrl/Cmd-click = tab mới, Shift = cửa sổ mới, chuột giữa = tab mới.
for _k in ("metaKey", "ctrlKey", "shiftKey", "altKey", "e.button"):
    check(f"ton trong {_k} (khong chan cach mo khac cua trinh duyet)",
          bool(_mw) and _k in _mw.group(1))
check("module khong nap duoc -> de link chay nhu thuong (khong preventDefault)",
      bool(_mw) and "!window.AstroQWarp" in _mw.group(1)
      and _mw.group(1).index("!window.AstroQWarp") < _mw.group(1).index("preventDefault"))
check("man loading xong thi DI TOI explorer.html",
      bool(_mw) and "explorer.html" in _mw.group(1) and "onDone" in _mw.group(1))
# ⚠️ Không kèm ?onboard=1: đây là lượt vào bản đồ BÌNH THƯỜNG, cổng phải TẮT.
check("KHONG bat cong lo trinh o luot vao binh thuong",
      bool(_mw) and "onboard=1" not in _mw.group(1))

# --- Lời phủ riêng: bộ mặc định nói sai đích cho cú mở bản đồ ---
check("warp-screen nhan loi phu qua play({texts})", "texts" in _ws and "over" in _ws)
check("loi phu dat lai MOI luot (khong dinh sang luot sau)",
      re.search(r"over\s*=\s*\(opts\.texts", _ws) is not None)
# Phủ THEO TỪNG KHOÁ — phủ cả bảng thì nút "Bỏ qua ›" hiện ra rỗng.
check("phu THEO TUNG KHOA, khong thay ca bang (nut 'Bo qua' khong rong)",
      re.search(r"if \(o && o\[k\] != null\) return o\[k\];", _ws) is not None)
check("loi phu cua dashboard co DU ca vi va en",
      bool(_mw) and "vi:" in _mw.group(1) and "en:" in _mw.group(1))
check("loi phu KHONG dung lai 'quy dao Trai Dat' (sai dich cho cu mo ban do)",
      bool(_mw) and "quỹ đạo Trái Đất" not in _mw.group(1))

# ══════════════════════════════════════════════════════════════════════════
# [16] WAITLIST TRANG CHU — day noi client -> POST /waitlist -> SES
#
# Ba loai loi that da xay ra, moi phep kiem chan dung mot loai:
#   a) id honeypot o markup va o JS lech nhau -> ném TypeError ngay sau
#      preventDefault, GIET ca ham gui form. Im lang hoan toan voi nguoi dung.
#   b) sot lai dau vet dich vu form ben thu ba sau khi chu du an chot dung SES.
#   c) ngay ra mat o backend lech voi LAUNCH_AT o client -> thu chao mung hen
#      mot ngay, trang hen mot ngay khac.
# ══════════════════════════════════════════════════════════════════════════
print("\n=== [16] Waitlist: client -> POST /waitlist -> SES ===")

_wl_html = rd("index.html")
_wl_js   = rd("js/index.js")


def _no_comments(js):
    """Bỏ comment nhưng GIỮ chuỗi.

    ⚠️ `strip_js()` có sẵn thì bỏ cả chuỗi — đúng cho việc đếm ngoặc, nhưng ở đây
    mọi thứ cần tìm (`$("wl-gotcha")`, `"/waitlist"`, `import("./api.js")`) đều
    NẰM TRONG chuỗi, dùng nó là phép kiểm nào cũng báo hỏng oan. Vẫn phải bỏ
    comment: dự án đã 9 lần dính lỗi "đếm cả chữ trong ghi chú của chính mình".
    """
    out, i, n = [], 0, len(js)
    while i < n:
        c = js[i]
        if c == "/" and i + 1 < n and js[i + 1] == "*":
            j = js.find("*/", i + 2); i = (j + 2) if j >= 0 else n; continue
        if c == "/" and i + 1 < n and js[i + 1] == "/":
            j = js.find("\n", i); i = j if j >= 0 else n; continue
        if c in "\"'`":
            q = c; out.append(c); i += 1
            while i < n and js[i] != q:
                if js[i] == "\\":
                    out.append(js[i]); i += 1
                if i < n:
                    out.append(js[i]); i += 1
            if i < n:
                out.append(js[i]); i += 1
            continue
        out.append(c); i += 1
    return "".join(out)


_wl_code = _no_comments(_wl_js)
_wl_ep   = rd_abs(os.path.join(ROOT, "..", "AstroqSV", "src", "AstroqSV.Api",
                               "Endpoints", "WaitlistEndpoints.cs"))
_wl_em   = rd_abs(os.path.join(ROOT, "..", "AstroqSV", "src", "AstroqSV.Api",
                               "Services", "EmailService.cs"))
_wl_prog = rd_abs(os.path.join(ROOT, "..", "AstroqSV", "src", "AstroqSV.Api", "Program.cs"))

# ⚠️⚠️ DOI PHAT BIEU 20/08/2026 — FORM WAITLIST DA BO HAN (duong B: qua khoi dau
#    chuyen vao chinh buoc dang ky tai khoan). Khoi cu khang dinh "co dung 1 o bay
#    bot", "JS doc dung id bay bot", "payload gui du email+lang+hp"… tuc no BAO VE su
#    ton tai cua cai form; giu nguyen thi no bao hong dung luc san pham lam dung.
# ⚠️ Cho nay tung la nguon cua mot loi THAT (02/08/2026): id bay bot lech giua markup
#    va JS lam ca ham gui form chet cam suot 6 ngay. Bo form la bo luon lop loi do.
check("trang chu KHONG con form waitlist nao",
      re.search(r'<form[^>]*id="wl-form"', _wl_html) is None)
check("khong con o bay bot (khong con form thi khong co gi de bay)",
      'class="hp"' not in _wl_html and 'id="wl-gotcha"' not in _wl_html)
check("khong con truong an kieu _subject/_gotcha cua dich vu cu",
      not re.search(r'name="_(subject|gotcha|replyto|next)"', _wl_html))
check("khoi CTA dan sang trang dang ky",
      'href="landing-app.html"' in _wl_html and 'data-i18n="wl_cta"' in _wl_html)
# ⚠️ La <a href> chu khong phai <button>: crawler di duoc, va `gen_home_en.py` tu lui
#    no thanh `../landing-app.html` cho ban EN (ban EN nam sau them mot cap).
check("CTA la the <a>, khong phai <button>",
      re.search(r'<button[^>]*data-i18n="wl_cta"', _wl_html) is None)

# --- day noi client ---
# ⚠️ Route `/waitlist` o BACKEND van GIU (phan server ngay duoi) — no la nguon cua
#    ban ghi `WAITLIST#`, thu dang quyet muc qua 500 (nguoi ghi danh truoc mo cua) vs
#    100 (moi nguoi khac). Bo route la nguoi da ghi danh mat luon muc 500.
check("trang chu KHONG con goi POST /waitlist", '"/waitlist"' not in _wl_code)
check("trang chu KHONG con nap js/api.js (khong con loi goi mang nao)",
      "api.js" not in _wl_code and "js/api.js" not in _wl_html)

# --- server ---
check("Program.cs co dang ky MapWaitlistEndpoints", "MapWaitlistEndpoints()" in _wl_prog)
check("route /waitlist ton tai o backend", 'MapPost("/waitlist"' in _wl_ep)
check("server gui thu qua SES", "SendWaitlistWelcomeAsync" in _wl_ep and
                                "SendWaitlistWelcomeAsync" in _wl_em)
check("route /waitlist KHONG doi token (khach chua co tai khoan)",
      "RequireAuthorization" not in _wl_ep)
check("co cooldown chan bom thu theo dich", "SendCooldownSeconds" in _wl_ep)
check("server loc lai bay bot", "req.Hp" in _wl_ep or "Hp)" in _wl_ep)
check("ban ghi waitlist KHONG dat ttl (phai song toi ngay ra mat)",
      re.search(r'PutWaitlistAsync.*?\["ttl"\]',
                rd_abs(os.path.join(ROOT, "..", "AstroqSV", "src", "AstroqSV.Api",
                                    "Data", "DynamoContext.cs")), re.S | re.M) is None
      or '["ttl"]' not in re.search(
          r'public async Task PutWaitlistAsync.*?\n    \}',
          rd_abs(os.path.join(ROOT, "..", "AstroqSV", "src", "AstroqSV.Api",
                              "Data", "DynamoContext.cs")), re.S).group(0))

# --- khoa i18n cua form: da bo het, khong de lai khoa chet ---
# ⚠️ DOI PHAT BIEU: 13 khoa (`wl_label`/`wl_ph`/`wl_sending`/`done_*`/`err_*`/`ok_*`)
#    da bo cung cai form. Khoi cu doi chung PHAI CO nen giu la bao hong oan. Chieu
#    can canh nay la nguoc lai: chung khong con sot lai lam khoa chet.
_vi, _en = i18n_dicts(_wl_js)          # tra ve TAP KHOA, khong phai gia tri
_dead_wl = ("wl_label", "wl_ph", "wl_sending", "done_title", "done_body",
            "done_body_nomail", "done_again", "err_empty", "err_format",
            "ok_short", "ok_dup", "err_send", "err_net")
_left = [k for k in _dead_wl if k in (_vi or set()) or k in (_en or set())]
check("13 khoa i18n cua form da bo het (khong de lai khoa chet)", not _left, _left)
check("5 khoa CON DUNG van co du o ca vi va en",
      all(k in (_vi or set()) and k in (_en or set())
          for k in ("wl_tag", "wl_title", "wl_desc", "wl_cta", "wl_hint")))
check("khong con nhac `mailSent` (khong con luot gui thu nao tu trang chu)",
      "mailSent" not in _wl_code)

# --- (c) ngay ra mat o backend khop client ---
_m_at = re.search(r'LAUNCH_AT\s*=\s*new Date\("(\d{4})-(\d{2})-(\d{2})', _wl_js)
_m_vi = re.search(r'LaunchDateVi\s*=\s*"(\d{2})/(\d{2})/(\d{4})"', _wl_ep)
check("doc duoc ngay ra mat o ca hai ben", bool(_m_at) and bool(_m_vi),
      (_m_at and _m_at.group(0), _m_vi and _m_vi.group(0)))
if _m_at and _m_vi:
    _cli = (_m_at.group(3), _m_at.group(2), _m_at.group(1))       # dd, mm, yyyy
    _srv = (_m_vi.group(1), _m_vi.group(2), _m_vi.group(3))
    check("ngay ra mat trong thu SES khop LAUNCH_AT cua trang chu",
          _cli == _srv, f"client {_cli} vs server {_srv}")

# ============================================================================
# [17] LO TRINH HUAN LUYEN — server giu MOC, client giu TEN
#
# Khoi "Lo trinh huan luyen" o achievements.html la cho DUY NHAT trong app cho
# xem CA thang cap bac (dashboard/profile chi hien bac hien tai). Muc nay canh
# dung mot loai loi da xay ra 5 lan trong du an: HAI NOI CUNG GIU MOT LUAT.
#
# ⚠️ Truoc 08/08/2026 KHONG co phep kiem nao doi chieu `MAX_LEVEL` cua
#    js/ranks.js voi `Achievements.MaxLevel` cua server, du chinh chu thich trong
#    ranks.js ghi "co phep kiem doi chieu". Con so 50 dung canh server 8 ngay ma
#    khong ai canh.
# ============================================================================
print("\n=== [17] Lo trinh huan luyen: server giu moc, client giu ten ===")

_ach_sv = rd_abs(os.path.join(SV, "src", "AstroqSV.Api", "Services", "Achievements.cs"))
_me_sv = rd_abs(os.path.join(SV, "src", "AstroqSV.Api", "Endpoints", "MeEndpoints.cs"))
_rk_js = rd("js/ranks.js")
_aw_html = rd("achievements.html")
_aw_code = _no_comments(inline_js(_aw_html))

# --- (a) MAX_LEVEL client == MaxLevel server ---
_m_cli = re.search(r"var\s+MAX_LEVEL\s*=\s*(\d+)", _rk_js)
_m_srv = re.search(r"MaxLevel\s*=\s*(\d+)", _ach_sv)
check("doc duoc so cap toi da o CA hai ben", bool(_m_cli) and bool(_m_srv),
      (_m_cli and _m_cli.group(1), _m_srv and _m_srv.group(1)))
if _m_cli and _m_srv:
    check("MAX_LEVEL cua js/ranks.js khop Achievements.MaxLevel cua server",
          _m_cli.group(1) == _m_srv.group(1),
          f"client={_m_cli.group(1)} server={_m_srv.group(1)}")

# --- (b) 10 bac, moi bac du vi + en + icon ---
_rk_block = _rk_js.split("var R = [", 1)[1].split("\n  ];", 1)[0]
_rk_rows = re.findall(r'\{\s*key:\s*"([a-z-]+)",\s*vi:\s*"([^"]+)",\s*en:\s*"([^"]+)",\s*ic:\s*"([^"]+)"',
                      _rk_block)
check("doc duoc danh sach bac huan luyen", len(_rk_rows) > 0, len(_rk_rows))
if _rk_rows:
    check("moi bac du ca ten VI, ten EN va icon",
          all(all(x.strip() for x in r) for r in _rk_rows),
          str([r[0] for r in _rk_rows if not all(x.strip() for x in r)]))
    check("khoa bac khong trung nhau",
          len({r[0] for r in _rk_rows}) == len(_rk_rows), len(_rk_rows))
    # Bac chia DEU thi hang cuoi moi phu het thang cap. 50/10 = 5; neu doi
    # MAX_LEVEL hoac them mot bac thu 11 ma khong chia het thi bang lo trinh se
    # co mot bac dai/ngan hon han cac bac khac ma khong ai noi ra.
    if _m_cli:
        check("so cap chia DEU cho so bac (khong con bac le)",
              int(_m_cli.group(1)) % len(_rk_rows) == 0,
              f"{_m_cli.group(1)} / {len(_rk_rows)}")

# --- (c) client KHONG nhan ban cong thuc XP ---
# Cong thuc `100·(n-1)·n/2` la LUAT CHOI cua server. Chep sang JS la ngay doi do
# kho thi bang o client noi con so cu — tuc noi SAI voi phu huynh.
check("server co ham tra ca bang moc XP (XpLadder)", "XpLadder" in _ach_sv)
check("GET /me/achievements tra bang moc XP cho client",
      bool(re.search(r"levels\s*=\s*new\s*\{[^}]*XpLadder", _me_sv, re.S)))
check("achievements.html doc bang moc tu server (d.levels.xp)",
      "levels" in _aw_code and "ladder" in _aw_code)
for _bad in ("100 *", "100*", "(lv - 1) * lv", "(lv-1)*lv", "XpForLevel"):
    check(f"achievements.html KHONG tu tinh moc XP ({_bad!r})", _bad not in _aw_code)
check("js/ranks.js KHONG chua cong thuc XP nao",
      not re.search(r"100\s*\*\s*\(", _no_comments(_rk_js)))

# --- (d) client khong gan cung so cap moi bac ---
# `PER_RANK` suy ra tu MAX_LEVEL; go so 5 vao trang la mot ban sao thu hai.
check("achievements.html doc PER_RANK/levelOf thay vi go so cap moi bac",
      ("levelOf" in _aw_code) and ("PER_RANK" in _aw_code or "MAX_LEVEL" in _aw_code))

# --- (e) khong bia bac khi chua doc duoc cap do ---
# Cung nguyen tac da ghi cho missions.html / specimen-vault.html: chua dang nhap
# thi hien dau "—", KHONG hien 0. O day: khong danh dau bac nao la cua nguoi xem.
check("VIEW.level mac dinh null (chua biet), khong phai 1",
      bool(re.search(r"level\s*:\s*null", _aw_code)))
check("nhanh mat mang/chua dang nhap dat lai level = null",
      bool(re.search(r"VIEW\.level\s*=\s*null", _aw_code)))
check("chua biet cap do thi KHONG danh dau bac 'now'",
      bool(re.search(r"cur\s*===?\s*0\s*\?\s*[\"']off[\"']", _aw_code)))
_i18n_vi, _i18n_en = i18n_dicts(inline_js(_aw_html))
for _k in ("tag_ladder", "ladder_h", "ladder_p", "ld_count", "ld_range",
           "ld_xp", "ld_here", "ld_unknown"):
    check(f"khoa i18n '{_k}' co o CA vi va en",
          _k in (_i18n_vi or set()) and _k in (_i18n_en or set()))

# --- (f) trang thuc su nap ranks.js VA thuc su ve khoi do ---
check("achievements.html nap js/ranks.js",
      'src="js/ranks.js"' in _aw_html)
# ⚠️ Phep kiem nay sinh ra tu mot phep thu pha hoai BI LOT: bo `renderLadder()`
#    khoi `render()` thi HTML, CSS, i18n va ca 10 bac van con nguyen — chi co bang
#    la RONG, va khong phep kiem tinh nao noi gi. Mot khoi khai day du ma khong ai
#    goi la dung loai loi da lam `AstroQRanks.ALL/levelOf/next` ngu 8 ngay.
check("render() thuc su goi renderLadder()",
      bool(re.search(r"function\s+render\s*\(\s*\)\s*\{[^}]*renderLadder\s*\(", _aw_code, re.S)))
check("applyLang() ve lai khoi lo trinh (doi VI/EN phai dich theo)",
      bool(re.search(r"function\s+applyLang[^}]*?\brender\s*\(\s*\)", _aw_code, re.S)))

# --- (f2) profile.html noi ra DICH BAC ke tiep, khong chi "len cap k" ---
# Truoc 08/08/2026 trang chi noi "Con n XP nua len cap 8" — mot con so khong noi len
# dieu gi voi tre, vi cai no muon la CAI TEN cua bac ke tiep.
_pf_html = rd("profile.html")
_pf_code = _no_comments(inline_js(_pf_html))
check("profile.html nap js/ranks.js", 'src="js/ranks.js"' in _pf_html)
check("profile.html dung AstroQRanks.next() cho dich bac",
      "AstroQRanks.next(" in _pf_code)
check("ten bac lay tu ranks.js, KHONG go lai o profile.html",
      not any(x in _pf_code for x in ("Chuyên Gia", "Specialist", "Hoa Tiêu", "Navigator")))
check("moc cap ke tiep KHONG go cung (dung nx.level)",
      "nx.level" in _pf_code)
_pf_vi, _pf_en = i18n_dicts(inline_js(_pf_html))
for _k in ("rank_next", "rank_soon"):
    check(f"khoa i18n '{_k}' co o CA vi va en",
          _k in (_pf_vi or set()) and _k in (_pf_en or set()))
check("bac cuoi thi AN dong dich (khong hua bac khong ton tai)",
      bool(re.search(r"else\s*\{[^}]*rank-goal|goal\.style\.display\s*=\s*[\"']none[\"']",
                     _pf_code, re.S)))
check("co CSS cho .xp .goal va trang thai .soon",
      ".goal" in _aw_css_pf_marker if (_aw_css_pf_marker := rd("css/profile.css")) else False)
check("co CSS cho trang thai '.goal.soon'", ".goal.soon" in _aw_css_pf_marker)

# --- (f3) MENU THA SAU AVATAR o dashboard: 6 duong vao, khong bia so ---
# ⚠️ DOI PHAT BIEU 15/08/2026. Truoc do muc nay doi mot LUOI 3 O (`.ptiles`) nam
#    trong bang Thong Ke. Nay ca sau duong vao "xem lai minh" (ho so · thanh tich ·
#    mau vat · kho trang tri · bang bo me · bao cao he thong) + nut Dang xuat nam
#    trong MOT menu tha sau anh dai dien, va bang Thong Ke da xuong duoi 6 the khu
#    vuc. Ly do do duoc: the khu vuc dau tien tung nam o y=1269px tren 390x844.
#    DIEU CAN BAO VE KHONG DOI va o day con SIET HON: du duong vao · khong bia so
#    · vung cham 48px · va them mot dieu bo cu khong hoi toi — HAI LOAI NGUOI DUNG
#    (tre / nguoi lon) phai phan biet duoc bang mat.
_db_html = rd("dashboard.html")
_db_code = _no_comments(inline_js(_db_html))
_db_css = rd("css/dashboard.css")
_um_css = rd("css/user-menu.css")
_um_js = rd("js/user-menu.js")

check("dashboard nap khung menu tha dung chung",
      'href="css/user-menu.css"' in _db_html and 'src="js/user-menu.js"' in _db_html)
check("dashboard co menu tha sau avatar",
      'class="um user-menu"' in _db_html and "data-menu-pop" in _db_html)
for _href, _cls in (("profile.html", "um-profile"), ("achievements.html", "um-awards"),
                    ("specimen-vault.html", "um-vault"), ("shop.html", "um-shop"),
                    ("parent.html", "um-parent")):
    check(f"menu co muc dan sang {_href}",
          bool(re.search(r'class="um-item %s" href="%s"' % (_cls, _href), _db_html)))
check("o admin (chi hien voi admin) nam TRONG menu",
      "data-admin-link" in _db_html.split('class="um user-menu"', 1)[-1]
      .split("</header>", 1)[0])
check("nut Dang xuat nam TRONG menu",
      'id="logout"' in _db_html.split('class="um user-menu"', 1)[-1].split("</header>", 1)[0])
check("2 nut chu xep doc cua ban cu da bo han",
      "sh-link" not in _no_comments(_db_html) and "sh-link" not in _no_comments(_db_css))
# ⚠️ Luoi `.ptiles` + hai dong `.pt-row` da XOA HAN, ke ca CSS. Rule khong con ai
#    dung la bay cho nguoi sua sau (ho se tuong luoi do van con va di sua no).
for _dead in ("ptiles", "ptile", "pt-row"):
    check(f"da bo han '{_dead}' khoi dashboard (HTML + CSS)",
          _dead not in _no_comments(_db_html) and _dead not in _no_comments(_db_css))
# ⚠️ ĐỪNG dùng `[^:]*` giữa `?` và `:` — hai nhánh nay co ternary LONG BEN TRONG
#    (`window.AstroQRanks ? ... : ""`) nen `[^:]*` dung som va phep kiem bao hong oan.
#    Dem so nhanh else tra ve dau "—" trong chinh than renderStats.
_rs = _db_code.split("function renderStats", 1)[-1].split("\n  function ", 1)[0]
check("KHONG bia so khi chua doc duoc server (dung dau '—')",
      _rs.count(': "—"') >= 2 and "known" in _rs, _rs.count(': "—"'))
# ⚠️ So mau vat nam o GET /me/specimens ma dashboard khong goi -> muc do KHONG co so,
#    va tuyet doi khong go cung tong so mau (server moi la nguon su that).
check("muc Mau vat KHONG go cung tong so mau",
      not re.search(r"/2[01]\b", _db_html.split("um-vault", 1)[-1][:600]))
check("dashboard KHONG goi them route chi de lay so mau vat",
      "getSpecimens" not in _db_code and "/me/specimens" not in _db_code)
check("ten bac o muc Ho so dung ranks.js (short), khong go tay",
      "AstroQRanks.short(" in _db_code)
for _k in ("pt_profile", "pt_awards", "pt_vault", "pt_vault_sub", "pt_badges_unit",
           "pt_shop_nm", "pt_shop_sub", "pt_parent_nm", "pt_parent_sub",
           "a_menu", "menu_me", "menu_grown"):
    _dvi, _den = i18n_dicts(inline_js(_db_html))
    check(f"khoa i18n '{_k}' co o CA vi va en",
          _k in (_dvi or set()) and _k in (_den or set()))
check("vung cham >= 48px tren thiet bi cam ung",
      bool(re.search(r"\.um-item\{[^}]*min-height:48px", _um_css))
      and bool(re.search(r"\.um-btn\{min-height:48px", _um_css)))
# ⚠️ HAI LOAI NGUOI DUNG PHAI PHAN BIET DUOC BANG MAT. Bo cu dat khu phu huynh o
#    mot dong net DUT, khac han ba o cua tre — de mat tre khong nham la cho minh
#    can bam. Menu moi giu dung y do (`.um-parent` net dut) va them mot tieu de
#    nhom rieng. Mat dieu nay la sau muc tron thanh mot danh sach deu tap.
check("khu cua NGUOI LON van khac han ve ngoai (net dut)",
      bool(re.search(r"\.um-item\.um-parent\{[^}]*border-style:dashed", _um_css)))
check("menu co tieu de nhom tach tre / nguoi lon",
      'data-i18n="menu_me"' in _db_html and 'data-i18n="menu_grown"' in _db_html)
# ⚠️ Bay `[hidden]`: `display` cua tac gia THANG `display:none` cua trinh duyet.
#    Thieu dong nay la menu bung ra san ngay khi tai trang (lan thu 12 trong du an).
check("tam tha co khai lai `[hidden]{display:none}`",
      ".um-pop[hidden]{display:none;}" in _um_css)
# data-tour phai TON TAI dung mot cho — thieu la Comet chieu sang vao khoang khong
# ⚠️ Dem tren ban DA BOC COMMENT (ca comment HTML): chinh chu thich giai thich
#    viec doi data-tour cung chua chuoi do (loi "dem ca chu trong ghi chu cua
#    chinh minh", lan thu 14).
_db_nc = strip_comments(_db_html)
check("data-tour='profile' ton tai dung MOT lan",
      _db_nc.count('data-tour="profile"') == 1, _db_nc.count('data-tour="profile"'))
# ⚠️ Muc trong tam tha dang `hidden` cho ra khung 0x0, nen `.tour-hole` chieu vao
#    khoang khong. Buoc "awards" da GOP vao buoc "profile" va chieu vao ca menu.
#    (quet tren ban da boc comment o CA hai file — chinh chu thich giai thich viec
#     gop hai buoc cung nhac lai chuoi do)
check("KHONG con data-tour tro vao muc nam trong tam tha",
      'data-tour="awards"' not in _db_nc
      and 'data-tour="awards"' not in _no_comments(rd("js/onboard-tour.js")))
check("data-tour='profile' nam tren CA menu, khong tren mot muc ben trong",
      bool(re.search(r'class="um user-menu" data-menu data-tour="profile"', _db_html)))

# --- (g) bac chua toi KHONG lam mo bang grayscale ---
# Bai hoc da ghi 3 lan trong CLAUDE.md: tren nen gradient sang, `grayscale()` cho
# ra khoi xam SANG HON hang binh thuong — hut mat vao dung thu chua dat duoc.
_aw_css = rd("css/achievements.css")
# ⚠️ BO COMMENT TRUOC ROI MOI CAT KHOI — dung cat theo tieu de comment.
#    Ban dau muc nay cat tu chuoi "LO TRINH HUAN LUYEN" (nam TRONG mot comment),
#    nen doan con lai bat dau o GIUA comment do: khong con `/*` mo cap voi `*/`
#    dong, `re.sub` khong khop, va chu "grayscale" trong chinh loi canh bao
#    "KHONG dung grayscale" bi tinh la vi pham. Loi "dem ca chu trong ghi chu cua
#    chinh minh" — lan thu 13 trong du an. Nay lay khoi bang SELECTOR.
_aw_css_nc = re.sub(r"/\*.*?\*/", " ", _aw_css, flags=re.S)
_rk_rules = re.findall(r"(?m)^(\.(?:rk|ranks|ladder|ld-note)[^{]*)\{([^}]*)\}", _aw_css_nc)
check("doc duoc cac rule CSS cua khoi lo trinh", len(_rk_rules) >= 8, len(_rk_rules))
_rk_css_body = "\n".join(sel + "{" + body + "}" for sel, body in _rk_rules)
check("khoi lo trinh KHONG dung filter:grayscale",
      "grayscale" not in _rk_css_body,
      str([s for s, b in _rk_rules if "grayscale" in b]))
for _cls in (".rk.now", ".rk.done", ".rk.off", ".ranks", ".ld-note"):
    check(f"co CSS cho {_cls}", _cls in _rk_css_body)

# --- (h) inline style tinh da don sach ---
check("achievements.html khong con inline style tinh flex:none;margin-left:auto",
      "flex:none;margin-left:auto" not in _aw_html)
check("co class .h2-count thay the", ".h2-count" in _aw_css)

# ══════════════════════════════════════════════════════════════
print("\n=== [18] Radar ky nang: CHIEU QUET (thanh dam di truoc) ===")
# ⚠️⚠️ CHIEU QUAY va DAU CUA DINH DUOI LA MOT CAP — doi mot cai ma quen cai kia thi loi
#    09/08/2026 quay tro lai: quat quay ma thanh dam bi keo THEO SAU.
#    Trong SVG truc y huong XUONG nen `rotate(+deg)` la quay theo chieu kim dong ho, va
#    canh DI TRUOC la canh co goc LON HON. Thanh sang o -90 deg (dinh 12h), nen dinh duoi
#    PHAI o goc NHO HON -90 => chi so am trong `polar(cx,cy,R,-0.5,n)`.
#    Ban cu dung `+0.5` (= -54 deg) nen mep mo dan dau.
#    ⚠️ Phep kiem nay chi doc VAN BAN. Thu do that su chieu quet la `smoke_radar.py`
#       (doc DOMMatrix dang chay tren Chromium, 16 phep kiem).
_dash = rd("dashboard.html")
_dash_js = strip_comments(inline_js(_dash))
_dcss = rd("css/dashboard.css")

_m_rot = re.search(r"@keyframes\s+radarSweep\s*\{([^}]*\}[^}]*)\}", _dcss)
check("doc duoc @keyframes radarSweep", bool(_m_rot))
_cw = bool(_m_rot) and "rotate(-" not in _m_rot.group(1)
check("radarSweep quay THEO chieu kim dong ho (khong co rotate(-...))", _cw,
      _m_rot.group(1).strip() if _m_rot else "")

_m_tail = re.search(r"var\s+tail\s*=\s*polar\(\s*cx\s*,\s*cy\s*,\s*R\s*,\s*(-?[\d.]+)\s*,\s*n\s*\)",
                    _dash_js)
check("buildRadar khai dinh DUOI cua quat (var tail=polar(...))", bool(_m_tail))
if _m_tail:
    _sign = float(_m_tail.group(1))
    # quay thuan chieu kim dong ho <=> dinh duoi phai o phia NGUOC lai, tuc chi so AM
    check("dinh duoi nam NGUOC chieu quay (thanh dam di truoc)",
          (_sign < 0) if _cw else (_sign > 0),
          f"tail index = {_sign}, chieu quay = {'CW' if _cw else 'CCW'}")

_m_line = re.search(r'class="rr-sweep"(.{0,160}?)/></g>', _dash_js, re.S)
check("doc duoc the <line class=rr-sweep>", bool(_m_line))
check("thanh sang ket thuc o canh DAN DAU (`lead`), khong gan cung toa do",
      bool(_m_line) and "lead" in _m_line.group(1),
      (_m_line.group(1).strip()[:70] if _m_line else ""))
# ⚠️ Duoi phai MO DAN — `fill` phang thi "dam truoc mo sau" chi dung tren giay.
check("duoi quat to bang gradient #rr-tail", "fill:url(#rr-tail)" in _dcss.replace(" ", ""))
check("gradient #rr-tail duoc dung trong buildRadar", 'id="rr-tail"' in _dash_js)

# ══════════════════════════════════════════════════════════════
print("\n=== [19] Duong thanh toan: gia · quyen · chu ky · cong tac ban ===")
# ⚠️ GIA NAM O BA NOI: docs/decisions/009 (quyet dinh) · Services/Billing.cs (so tien
#    server THAT SU thu) · pricing.html (con so phu huynh DOC). 009 la van ban nen
#    khong doi chieu tu dong duoc, nhung hai noi CHAY thi phai khop tuyet doi — lech
#    nghia la trang noi mot dang va thu mot neo. Cung khuon doi chieu
#    `Wallet.Fees` <-> `economy.js FEES` o muc [9].
_bill_cs = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/Billing.cs"))
_pay_cs  = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/Payments.cs"))
_bep_cs  = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Endpoints/BillingEndpoints.cs"))
_ord_cs  = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Data/DynamoContext.Orders.cs"))
_tmpl    = rd_abs(os.path.join(SV, "template.yaml"))
_co      = rd("checkout.html")
_co_js   = inline_js(_co)
_pr_js   = inline_js(rd("pricing.html"))
_bep_nc  = strip_comments(_bep_cs)
_bep_1l  = re.sub(r"\s+", " ", _bep_cs)

# Bang gia server: ["astro:month"] = (99_000, 4.99m)
_sv_price = {}
for _m in re.finditer(r'\["([a-z]+):([a-z]+)"\]\s*=\s*\(([0-9_]+),\s*([0-9.]+)m\)', _bill_cs):
    _sv_price[(_m.group(1), _m.group(2))] = (int(_m.group(3).replace("_", "")), float(_m.group(4)))

# Bang gia client: { key:"astro", vnd:{m:99000, y:790000}, usd:{m:4.99, y:39.99} }
def _money_pairs(s):
    return dict((k, float(v)) for k, v in re.findall(r'(\w+):\s*([0-9.]+)', s))

_cl_price = {}
for _m in re.finditer(r'\{\s*key:"([a-z]+)"[^}]*?vnd:\{([^}]*)\}[^}]*?usd:\{([^}]*)\}', _pr_js):
    _v, _u = _money_pairs(_m.group(2)), _money_pairs(_m.group(3))
    for _short, _cycle in (("m", "month"), ("y", "year"), ("once", "once")):
        if _short in _v and _short in _u:
            _cl_price[(_m.group(1), _cycle)] = (int(_v[_short]), _u[_short])

check("doc duoc bang gia cua server", len(_sv_price) == 5, str(len(_sv_price)))
check("doc duoc bang gia cua pricing.html", len(_cl_price) >= 5, str(len(_cl_price)))
# Goi `free` co o client (de ve cot mien phi) nhung KHONG duoc co o server — mot muc
# gia 0 ben server la mot don 0d tao duoc, tuc mot duong mo goi ma khong tra tien.
check("server KHONG co muc gia nao cho goi 'free'",
      not any(k[0] == "free" for k in _sv_price))
_paid_cl = dict((k, v) for k, v in _cl_price.items() if k[0] != "free")
check("gia client == gia server (ca VND lan USD)", _paid_cl == _sv_price,
      f"client={_paid_cl} server={_sv_price}")

# ── Cong tac ban: mac dinh DONG, va o SERVER ──
check("Billing.SaleOpen doc tu cau hinh (khong phai hang so bien dich)",
      'cfg["SALE_OPEN"]' in _bill_cs)
check("SALE_OPEN vang mat = DONG (so bang 'true', khong phai != 'false')",
      'Equals(cfg["SALE_OPEN"], "true"' in _bill_cs)
# ⚠️ template.yaml quyet dinh bien nao co tren AWS. Khai SALE_OPEN=true o do la mo
#    ban that. Day la chot chan cuoi cung truoc khi tien that chay.
# ⚠️ Do "co DAT bien khong", khong do "co nhac ten khong" — template.yaml PHAI duoc
#    phep ghi chu ve hai bien nay (nguoi mo ban can biet bat o dau), nhung KHONG
#    duoc dat gia tri cho chung.
check("template.yaml KHONG dat SALE_OPEN (ban that phai dong)",
      re.search(r"^\s*SALE_OPEN\s*:", _tmpl, re.M) is None)
check("template.yaml KHONG dat PAY_PROVIDER (chua chon cong)",
      re.search(r"^\s*PAY_PROVIDER\s*:", _tmpl, re.M) is None)
check("template.yaml KHONG dat PAY_WEBHOOK_SECRET (khoa phai o Secrets Manager)",
      re.search(r"^\s*PAY_WEBHOOK_SECRET\s*:", _tmpl, re.M) is None)

# ── Quyen ──
check("nhom /me/billing doi dang nhap DA XAC MINH email",
      'MapGroup("/me/billing").RequireAuthorization("verified")' in _bep_cs)
check("uid lay TU TOKEN, khong tu than request",
      'u.FindFirst("user_id")' in _bep_cs and "req.Uid" not in _bep_cs)
# ⚠️ 404 chu KHONG phai 403: 403 noi rang ma don do CO THAT, tuc mot duong do xem
#    ai da mua gi.
check("don cua nguoi khac -> 404, khong phai 403",
      "o.Uid != uid) return Results.NotFound" in _bep_1l)

# ── So tien do server quyet ──
check("CheckoutRequest KHONG co truong so tien",
      not re.search(r'record CheckoutRequest\([^)]*(Amount|Price|Total)', _bep_nc, re.S))
check("so tien lay tu Billing.Find (bang gia server)", "offer.Amount, provider.Name" in _bep_nc)
check("client KHONG gui so tien len",
      not re.search(r'startCheckout\(\{[^}]*amount', _co_js, re.I | re.S))

# ── `paid` chi dat duoc bang webhook ──
check("webhook doc THAN THO (chu ky ky tren chuoi byte goc)",
      "new StreamReader(ctx.Request.Body)" in _bep_nc)
check("chu ky sai -> 400 va KHONG xu ly tiep",
      "ev is null" in _bep_nc and '"bad-signature"' in _bep_nc)
check("so chu ky bang FixedTimeEquals (khong so bang ==)",
      "CryptographicOperations.FixedTimeEquals" in _pay_cs)
# ⚠️ Duong DUY NHAT ghi "paid". Co cho thu hai ghi trang thai nay thi phep kiem duoi
#    day bao hong — va do dung la luc phai dung lai ma doc lai.
check("chi MOT cho ghi trang thai don (SettleOrderAsync)",
      _ord_cs.count("public async Task<bool> SettleOrderAsync") == 1)
check("chot don CHI di tu 'pending' (webhook gui lai khong lat trang thai)",
      "#s = :p" in _ord_cs and '[":p"]   = S("pending")' in _ord_cs)
check("checkout.html hoi lai SERVER thay vi doc trang thai tu URL", "a.getOrder(" in _co_js)
check("checkout.html KHONG lay trang thai tu query string",
      not re.search(r'(status|paid|success)\s*=\s*Q\.get\(', _co_js))

# ── Don hang la chung tu tien: khong TTL ──
# Cung bai hoc voi ban ghi WAITLIST# ("dat nham TTL vao day la DynamoDB am tham xoa
# mat khach"); o day thu bi xoa la mot khoan tien da thu.
check("ban ghi don KHONG dat ttl", '"ttl"' not in _ord_cs)
# ⚠️ QUET TREN CODE DA BOC COMMENT. Chinh ghi chu trong file do GIAI THICH vi sao
#    KHONG dung `TryBeginOpAsync`, nen quet ca comment la bao vi pham oan. Day la
#    lan thu MUOI LAM cung loai loi nay trong du an — moi phep kiem dang "khong
#    duoc chua X" deu phai boc comment truoc.
check("chong trung don KHONG dung TryBeginOpAsync (ham do co ttl 7 ngay)",
      "TryBeginOpAsync" not in strip_comments(_ord_cs))
check("chong trung bang ban ghi ORDERKEY co dieu kien",
      "ORDERKEY#" in _ord_cs and "attribute_not_exists(PK)" in _ord_cs)

# ── Khong co form the ──
# ⚠️ Moi cong ma 009 de xuat (payOS/SePay/VNPay/MoMo/Paddle) deu nhan the tren trang
#    cua CHINH CONG. Dung form the o day la keo ca du an vao pham vi PCI-DSS.
_co_low = _co.lower()
for _w in ("card-number", "cardnumber", "cvv", "cvc", 'autocomplete="cc-'):
    check(f"checkout.html KHONG co truong the ({_w})", _w not in _co_low)
check("checkout.html noi ro cong thanh toan giu the",
      "không lưu số thẻ" in _co and "never stores card" in _co)

# ── Cong gia lap chi song khi duoc chon ──
check("duong sandbox chi mount khi PAY_PROVIDER=mock", "is MockPaymentProvider" in _bep_nc)
check("cong mac dinh la `none` (khong khai PAY_PROVIDER -> khong ban duoc)",
      'cfg["PAY_PROVIDER"] ?? "none"' in _pay_cs)
check("cong `none` khong bao gio Ready", "Ready => false;" in _pay_cs)

# ── returnUrl: chong open redirect ──
check("returnUrl doi chieu allowlist origin",
      "Origins.IsAllowed" in _bep_cs and "IsAllowedReturn" in _bep_cs)
check("so theo ORIGIN, khong phai StartsWith tren chuoi", "u.Authority" in _bep_cs)

# ── pricing.html: nut dan di dau do SERVER quyet ──
check("pricing.html hoi /billing/catalog", "/billing/catalog" in _pr_js)
check("pricing.html mac dinh DONG (mang hong thi giu hanh vi hom nay)",
      "var SALE = { open:false }" in _pr_js)
check("pricing.html chi dan sang checkout khi SALE.open",
      re.search(r'SALE\.open\)\s*\{[^}]*checkout\.html', _pr_js, re.S) is not None)
check("pricing.html dung import DONG cho api.js (khong them the <script>)",
      'import(new URL("js/api.js"' in _pr_js)

# ══════════════════════════════════════════════════════════════
# [20] KHU NHIEM VU 4 TANG — danh muc client PHAI khop luat server
#      (`docs/decisions/008`, viec con treo so 1, dung that 12/08/2026)
#
#      Trung Tam Nhiem Vu → ban do → (hanh tinh) → cay chang → man choi
#
# ⚠️ MUC NAY THAY CHO PHAN "MISSIONS array" CU CUA [7c] VA CHAT HON NO: truoc day
#    chi mot mang trong `missions.html` phai khop `Missions.cs`; nay CA DANH MUC
#    (`js/mission-catalog.js`) phai khop, va `STEP_IDS` cua trang choi phai khop
#    danh muc. Ba noi, mot su that.
print("\n=== [20] Khu nhiem vu: danh muc client khop Missions.cs ===")

_cat_src = rd("js/mission-catalog.js")
_cat = strip_comments(_cat_src)
_mi_cs = io.open(os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"),
                 encoding="utf-8").read()

# ── Server: id nhiem vu + id buoc, DUNG THU TU ──
_sv_ids = re.findall(r'new\("([a-z0-9-]+)",\s*"[a-z0-9-]+",\s*\[', _mi_cs)
_sv_steps = re.findall(r'new\("([a-z0-9-]+)",\s*\d+,\s*\d+,', _mi_cs)

# ── Client: danh muc ──
_cat_ids = re.findall(r'^\s{6}id: "([a-z0-9-]+)", world: "([a-z0-9-]+)", file: "([^"]+)"',
                      _cat, re.M)
_cat_mids = [m[0] for m in _cat_ids]
check("[20] danh muc doc ra duoc it nhat 1 nhiem vu", len(_cat_mids) > 0,
      str(_cat_mids))
check("[20] id nhiem vu client == server", _cat_mids == _sv_ids,
      f"client={_cat_mids} server={_sv_ids}")

# Buoc cua tung nhiem vu: cat doan tu id nhiem vu nay toi id nhiem vu ke tiep
def _cat_steps(mid):
    i = _cat.find('id: "%s", world:' % mid)
    if i < 0:
        return []
    j = len(_cat)
    for other in _cat_mids:
        if other == mid:
            continue
        k = _cat.find('id: "%s", world:' % other)
        if i < k < j:
            j = k
    return re.findall(r'\{ id: "([a-z0-9-]+)", ic:', _cat[i:j])

_all_cat_steps = []
for _m in _cat_mids:
    _all_cat_steps += _cat_steps(_m)
check("[20] id chang client == id buoc server, DUNG THU TU",
      _all_cat_steps == _sv_steps,
      f"client={_all_cat_steps} server={_sv_steps}")

# ── `STEP_IDS` cua trang choi == danh muc, VOI MOI NHIEM VU ──
# WARN Truoc 15/08/2026 phep kiem nay ghim `mission-earth.html` va `'earth'`. Khi
#   Trai Dat co nhiem vu thu hai, trang choi cua no khong duoc doi chieu voi danh
#   muc — ma lech o day la cay chang ve mot chang trang choi khong biet, hoac nguoc
#   lai. Lap qua tung nhiem vu, lay ten trang tu chinh danh muc.
_me_src = rd("mission-earth.html")
for _mid2, _wid2, _file2 in _cat_ids:
    if not os.path.exists(os.path.join(ROOT, _file2)):
        continue                       # da co phep kiem rieng o duoi cho ca nay
    _psrc2 = rd(_file2)
    _msi = re.search(r"const STEP_IDS = \[([^\]]+)\]", _psrc2)
    _pst = re.findall(r"'([a-z0-9-]+)'", _msi.group(1)) if _msi else []
    check(f"[20] STEP_IDS cua {_file2} == danh muc chang cua '{_mid2}'",
          _pst == _cat_steps(_mid2),
          f"STEP_IDS={_pst} catalog={_cat_steps(_mid2)}")

# ⚠️⚠️ DANH MUC KHONG DUOC CHUA MOT CON SO THUONG NAO.
#    `GET /me/missions` khong tra thuong theo tung buoc, nen ve duoc day chip
#    "+20 tt · +30 XP" thi phai CHEP bang thuong cua `Services/Missions.cs` vao
#    client — hai noi giu mot luat, va ban o client se noi con so cu vao dung ngay
#    server doi. Cung phan cong da dung cho huy hieu / mau vat / bac: server giu
#    MOC, client giu TEN.
_pay = [w for w in ("tt:", "xp:", "meteors", "reward", "codex:")
        if w in _cat]
check("[20] danh muc KHONG chua con so thuong nao", not _pay, str(_pay))

# ── Nhiem vu khai ra thi PHAI co trang choi that ──
_no_file = [f for _, _, f in _cat_ids if not os.path.exists(os.path.join(ROOT, f))]
check("[20] moi nhiem vu trong danh muc deu co trang choi that", not _no_file,
      str(_no_file))

# ── WORLD-ID KHAC PLANET-ID: Mat Trang KHONG duoc lot vao js/planets.js ──
#    `js/planets.js` la cho ghi "da ghe hanh tinh nao" cho ho so + huy hieu
#    (`planet-3`/`planet-8`). Nhet Mat Trang vao do la ho so dem sai va hai huy hieu
#    kia thanh bat kha thi.
_planets = set(re.findall(r'\{ id:"([a-z]+)"', rd("js/planets.js")))
# ⚠️ `\s+` chu khong phai mot dau cach: bang khai bao co CAN COT nen giua dau phay va
#    `planet:` co the la 1..5 dau cach. Ban dau muc nay doi dung mot dau cach va no
#    doc ra 3/9 diem den roi bao "Mat Trang khong khai planet:null" — mot phep kiem
#    BAO OAN vi no doc thieu du lieu, khong phai vi san pham sai.
_cat_worlds = re.findall(r'\{ id: "([a-z0-9-]+)",\s+planet: (null|"[a-z0-9-]+")', _cat)
_bad_planet = [w for w, p in _cat_worlds
               if p != "null" and p.strip('"') not in _planets]
check("[20] moi `planet` cua diem den deu co that trong js/planets.js",
      not _bad_planet, str(_bad_planet))
check("[20] Mat Trang KHONG nam trong js/planets.js (world-id != planet-id)",
      "moon" not in _planets)
check("[20] Mat Trang khai `planet: null`",
      ("moon", "null") in _cat_worlds, str(_cat_worlds))
# Moi noi nhiem vu tro toi phai la mot diem den co that tren ban do
_wids = {w for w, _ in _cat_worlds}
_bad_w = [w for _, w, _ in _cat_ids if w not in _wids]
check("[20] moi nhiem vu tro toi mot diem den co that", not _bad_w, str(_bad_w))

# ── Song ngu day du ──
_n_mis, _n_step = len(_cat_mids), len(_all_cat_steps)
check("[20] du khoi `vi`/`en` cho moi nhiem vu va moi chang",
      _cat.count("vi: {") == _n_mis + _n_step
      and _cat.count("en: {") == _n_mis + _n_step,
      f"vi={_cat.count('vi: {')} en={_cat.count('en: {')} can={_n_mis + _n_step}")

# ── Ban do: cong lo trinh do SERVER quyet, client khong tu tinh ──
_map_src = rd("mission-map.html")
_map_js = strip_comments(inline_js(_map_src))
check("[20] ban do doc cong qua AstroQGate (khong tu tinh ti le)",
      "AstroQGate.canVisit(" in _map_js and "AstroQGate.load()" in _map_js)
check("[20] ban do KHONG tu tinh nguong cong",
      "0.7" not in _map_js and "Math.ceil" not in _map_js)
check("[20] ban do KHONG nap SDK Firebase (doc cache)",
      'src="js/firebase-auth.js"' not in _map_src)
# `mission:moon` khai o js/locks.js phai co NGUOI DOC — mot muc khai ma 0 cho doc la
# mot loi khai sai (bai hoc `lv` / `AstroQRanks.ALL`).
check("[20] ban do dung js/locks.js cho noi 'sap co nhiem vu'",
      'AstroQLocks.open("mission:" + id' in _map_js)

# ── Cay chang ──
_tr_src = rd("mission-tree.html")
_tr_js = strip_comments(inline_js(_tr_src))
check("[20] cay chang doc danh muc, khong go lai ten chang",
      "AstroQCatalog.find(" in _tr_js and 'src="js/mission-catalog.js"' in _tr_src)
check("[20] cay chang doc tien do that qua AstroQProgress.missions()",
      "AstroQProgress.missions()" in _tr_js)
# Chan hAN o chinh cai nut, khong chan bang mot cau `if` — chan bang `if` thi nut van
# nhan tieu diem ban phim va van bao voi trinh doc man hinh rang no bam duoc.
check("[20] chang chua mo bi chan bang `disabled` o chinh cai nut",
      "st === \"lock\" ? \" disabled\" : \"\"" in _tr_js)
# Chan hAN thi phai tra lai cho noi ly do — bo bang chi tiet ma khong thay bang gi la
# dung bay cua cong lo trinh (*"im lang thi tre chi tuong minh bam truot"*).
check("[20] co cau noi ra dieu kien mo, doc duoc ma khong phai cham vao dau",
      'id="rule"' in _tr_src and 'data-i18n="rule"' in _tr_src)
check("[20] cay chang KHONG tu cong thuong",
      "addAsteroids" not in _tr_js)

# ── Man hanh tinh ──
_pl_src = rd("mission-planet.html")
_pl_js = strip_comments(inline_js(_pl_src))
check("[20] man hanh tinh doc danh muc theo noi",
      "AstroQCatalog.byWorld(" in _pl_js)
check("[20] noi chua co nhiem vu thi noi that mot cau, khong ve danh sach rong",
      'id="empty"' in _pl_src and 'data-i18n="emp_h"' in _pl_src)

# ── Trang choi: `?step=` + hop "tiep hay dung" ──
# WARN VO (`js/mission-stage.js`) giu: `?step=`, hop "tiep hay dung", dong ho ve tu
#   dong, duong ve cay chang. Trang nhiem vu chi con NOI vao. Soi ca hai — de nguyen
#   la phep kiem bao hong dung luc san pham lam dung.
_me_js = strip_comments(inline_js(_me_src)) + strip_comments(rd("js/mission-stage.js"))
_me_js = _me_js.replace(chr(34), "'")   # vo viet nhay KEP, trang viet nhay DON
check("[20] trang choi doc `?step=` va mo dung chang do",
      "q.get('step')" in _me_js and "RUN.openAt(" in _me_js)
check("[20] khai moc onStepDone cho trinh dieu phoi",
      "onStepDone: ST.afterStep" in _me_js)
# ⚠️ DIEU KIEN CUA `008`: "tat dong ho ve tu dong 5 giay khi con chang sau".
#    No duoc thoa BANG CAU TRUC: dong ho chi song trong man tong ket, ma man tong ket
#    chi mo khi HET chang (`afterStep` tra `false` dung o chang cuoi). Hai phep kiem
#    duoi day canh dung hai chan do.
check("[20] hop hoi KHONG mo o chang cuoi (de man tong ket mo)",
      re.search(r"if \(last\) return false;", _me_js) is not None)
# ⚠️ Dem LOI GOI, khong dem so lan xuat hien: `function startAuto() {` cung chua
#    chuoi `startAuto()`, nen dem tho ra 2 va phep kiem bao hong oan.
check("[20] dong ho ve tu dong chi khoi dong tu man tong ket",
      len(re.findall(r"(?<!function )startAuto\(\)", _me_js)) == 1,
      str(re.findall(r".{22}startAuto\(\)", _me_js)))
# WARN Truoc 15/08/2026 phep kiem nay ghim nguyen van `mission-tree.html?m=earth`. Vo
#   dung chung dung URL TU ID NHIEM VU (`?m=` + encodeURIComponent(mission)), nen ghim
#   mot ten nhiem vu la phep kiem chi dung cho Trai Dat va se bao hong o nhiem vu thu
#   hai — trong khi hanh vi thi dung hon truoc. Hoi dieu MUON BIET: duong ve la cay
#   chang CUA CHINH nhiem vu dang choi, khong phai mot trang gan cung.
check("[20] duong ve cua trang choi la cay chang cua CHINH no",
      "function treeUrl()" in _me_js
      and "mission-tree.html?m=" in _me_js
      and "encodeURIComponent(mission)" in _me_js)
check("[20] on lai mot chang cu thi NOI RO khong co thuong them",
      "serverDone.has(id)" in _me_js and "replayed" in _me_js)

# ── Dong "Choi tiep" dung chung, khong chep hai ban ──
check("[20] dong 'Choi tiep' o mot file CSS dung chung",
      os.path.exists(os.path.join(ROOT, "css/resume.css"))
      and 'href="css/resume.css"' in rd("missions.html")
      and 'href="css/resume.css"' in _map_src)
check("[20] bang chi tiet o mot file CSS dung chung",
      'href="css/mission-sheet.css"' in _map_src
      and 'href="css/mission-sheet.css"' in _tr_src)

# ══════════════════════════════════════════════════════════════════════════════
print("\n=== [21] Bo icon sticker: hai chieu + danh sach icon ngu ===")
# ⚠️ VI SAO CAN: `sic(name)` tra ve chuoi RONG khi ten sai — icon thieu thi ra mot
#    o SVG trong, KHONG loi, KHONG canh bao. Day dung ly do phep kiem hai chieu cua
#    bo `cx-*` da ton tai; bo nay can y nguyen.
_sic_js  = rd("js/sticker-icons.js")
_sic_css = rd("css/sticker-icons.css")
_sic_code = strip_comments(_sic_js)

SIC_NAMES = set(re.findall(r'^\s{4}([A-Za-z_][\w]*):\s*\{', _sic_code, re.M))
check("[21] doc duoc bo icon sticker", len(SIC_NAMES) >= 20, str(len(SIC_NAMES)) + " icon")
if not SIC_NAMES:
    print("  !! khong boc duoc icon nao — cac phep kiem duoi day se dat MOT CACH RONG")
    sys.exit(1)

# Ten icon dang duoc goi tu moi noi: `data-sic="x"` trong HTML, `sic("x")` trong JS,
# truong `sic:"x"` cua js/badges.js, va `icon:"x"` cua bang GAMES.
_sic_pages = sorted(f for f in os.listdir(ROOT)
                    if f.endswith(".html") and 'js/sticker-icons.js' in rd(f))
USED = set()
for _f in _sic_pages:
    _src = strip_comments(rd(_f))
    USED |= set(re.findall(r'data-sic="([a-z-]+)"', _src))
    USED |= set(re.findall(r'sic\("([a-z-]+)"', _src))
_badges_code = strip_comments(rd("js/badges.js"))
BADGE_SIC = dict(re.findall(r'"([\w-]+)":\s*\{\s*ic:"[^"]*",\s*sic:"([a-z-]+)"', _badges_code))
USED |= set(BADGE_SIC.values())
USED |= set(re.findall(r'icon:"([a-z-]+)"', strip_comments(rd("games.html"))))
# `sicName()` lui ve icon nay khi huy hieu chua khai — nen no luon la ten dang dung.
USED |= set(re.findall(r'B\[id\]\.sic\) \|\| "([a-z-]+)"', _badges_code))

check("[21] moi ten icon duoc goi deu CO ban ve", not (USED - SIC_NAMES),
      str(sorted(USED - SIC_NAMES)))

# ⚠️ DANH SACH ICON NGU LA MOT DANH SACH KIN, ghim y nhu `LEGACY_SRC`/`PENDING_BANK`:
#    ve them mot icon roi de do la them mot mang ma chet, ma du an da tra gia nhieu
#    lan cho chuyen do. Ly do tung cai ghi trong `js/sticker-icons.js`.
# ⚠️ `leaf` RA KHOI danh sach 16/08/2026 — ARCADE-09 dung no cho the Tram Tuan
#    Hoan. Danh sach nay la mot DANH SACH KIN dung de bat moi lan dung/thoi dung
#    mot icon phai la quyet dinh CO Y THUC; no da lam dung viec do o luot nay.
SIC_IDLE = {"globe", "map", "lock", "wave", "rock"}
check("[21] tap icon CHUA ai dung dung bang danh sach da ghim",
      (SIC_NAMES - USED) == SIC_IDLE,
      "ngu=" + str(sorted(SIC_NAMES - USED)) + " ghim=" + str(sorted(SIC_IDLE)))

# Moi huy hieu phai co ca `ic` (emoji, cho cho chi nhan van ban) va `sic`.
_bids = set(re.findall(r'^\s{4}"([\w-]+)":\s*\{\s*ic:', _badges_code, re.M))
check("[21] moi huy hieu khai du ca `ic` lan `sic`",
      bool(_bids) and set(BADGE_SIC) == _bids,
      "thieu sic=" + str(sorted(_bids - set(BADGE_SIC))))
# ⚠️ Emoji KHONG duoc bo: js/viz.js dat nhan bang textContent (co y), nen
#    js/admin-report.js nhet SVG vao la in ra nguyen chuoi <svg…> cho nguoi doc thay.
check("[21] js/viz.js van dat nhan bang textContent (ly do giu emoji)",
      ".textContent" in rd("js/viz.js"))
check("[21] admin-report + parent van dung emoji, KHONG dung sic()",
      "AstroQBadges.icon(" in rd("js/admin-report.js")
      and "AstroQBadges.icon(" in rd("parent.html")
      and "sicName" not in rd("js/admin-report.js"))

# Lop ve va lop mau: hai chieu voi CSS.
_f_used = set(re.findall(r'class=\\?"(f-[a-z]+)\\?"', _sic_code))
_f_have = set(re.findall(r'\.sic-ink \.(f-[a-z]+)', _sic_css))
# ⚠️ BANG MAU (`sic--<ten>`) PHAI CANH HAI CHIEU — thieu phep kiem nay nen 5 bang mau
#    (`cyan`/`gold`/`lime`/`mag`/`slate`) da khai o css/sticker-icons.css tu 12/08/2026
#    ma **chua mot cho nao dung**: moi icon tren dashboard, 6 the game va 22 me day deu
#    roi ve tim mac dinh. Chu du an bat duoc: "sao lai toan 1 mau tim the? tre con se
#    thay don dieu". `sic(name, cls)` nhan bang mau la mot CHUOI TU DO nen sai ten thi
#    im lang tuyet doi — dung ho voi loi `sic()` tra chuoi rong khi ten icon sai.
_pal_css = set(re.findall(r'\.sic--([a-z]+)\s*\{', _sic_css))
_pal_used = set()
for _f in sorted(f for f in os.listdir(ROOT) if f.endswith(".html")):
    _pal_used |= set(re.findall(r'sic--([a-z]+)', _no_comments(rd(_f))))
check("[21] doc duoc bang mau cua bo icon", len(_pal_css) >= 5, str(sorted(_pal_css)))
check("[21] moi bang mau duoc dung deu CO CSS", not (_pal_used - _pal_css),
      str(sorted(_pal_used - _pal_css)))
check("[21] khong bang mau nao BO KHONG", not (_pal_css - _pal_used),
      "khai ma khong ai dung: " + str(sorted(_pal_css - _pal_used)))
# Man hinh tre nhin nhieu nhat khong duoc don sac: 6 card MOD phai co it nhat 4 mau
# khac nhau (5 bang + tim mac dinh, hai card duoc phep dung chung mot mau).
_dash_pals = set(re.findall(r'data-sic-cls="(sic--[a-z]+)"', _no_comments(rd("dashboard.html"))))
check("[21] dashboard KHONG don sac (>=4 bang mau khac nhau)", len(_dash_pals) >= 4,
      "%d bang: %s" % (len(_dash_pals), sorted(_dash_pals)))

check("[21] moi lop mau `f-*` deu co CSS", not (_f_used - _f_have), str(sorted(_f_used - _f_have)))
check("[21] khong lop mau `f-*` nao bo khong", not (_f_have - _f_used), str(sorted(_f_have - _f_used)))
_lay_used = set(re.findall(r'class="(sic-[a-z]+)"', _sic_code))
_lay_have = set(re.findall(r'\.(sic-[a-z]+)\s*\{', _sic_css))
check("[21] du 5 lop ve", len(_lay_used) == 5, str(sorted(_lay_used)))
check("[21] moi lop ve deu co CSS", not (_lay_used - _lay_have), str(sorted(_lay_used - _lay_have)))

# ⚠️ Lop ngoai cung la thu lam sticker doc duoc tren nen SANG — xem ghi chu dau file.
check("[21] con lop `sic-edge` (net navy NGOAI ria trang)",
      "sic-edge" in _sic_code and ".sic-edge" in _sic_css
      and _sic_code.index("sic-edge") < _sic_code.index("sic-rim"))
# viewBox phai noi rong: 3 net ve ra ngoai duong bao (13 + 9 + 4).
check("[21] viewBox noi rong cho 3 net ve ra ngoai", 'viewBox="-8 -8 80 80"' in _sic_code)

# Trang nao goi sic() thi phai nap CA css lan js — thieu css la 5 lop mat mau.
for _f in _sic_pages:
    _src = rd(_f)
    check("[21] " + _f + " nap ca css lan js cua bo icon",
          'href="css/sticker-icons.css"' in _src and 'src="js/sticker-icons.js"' in _src)

# ⚠️ VA CHIEU NGUOC LAI: trang KHONG dung thi KHONG duoc nap. Bo nay ~9 KB (js+css)
#    va no khong lam gi ca neu khong co `data-sic` hay loi goi `sic(...)` — dung loai
#    byte chet ma du an da cat nhieu lan (font 621→101 KB, anh nen 6,9 MB→99 KB).
for _f in sorted(f for f in os.listdir(ROOT) if f.endswith(".html")):
    _src = rd(_f)
    _loads = 'src="js/sticker-icons.js"' in _src
    # ⚠️ Phai bat CA loi goi khong-phai-chuoi-tho: `achievements.html` goi
    #    `sic(AstroQBadges.sicName(id), …)` va `games.html` goi `sic(g.icon, …)`.
    #    Chi do `sic("` thi hai trang do bi doc thanh "khong dung" — phep kiem bao
    #    hong dung luc trang lam dung. Lookbehind loai `.sic`/`sicName`/`sicPaint`.
    _uses = bool(re.search(r'data-sic="|\bAstroQ\.sic\(|(?<![A-Za-z0-9_.$])sic\(',
                           strip_comments(_src)))
    check("[21] " + _f + ": nap bo icon <=> co dung no",
          _loads == _uses, "nap=" + str(_loads) + " dung=" + str(_uses))

# ⚠️ Me day o achievements.html KHONG duoc quay lai `filter:grayscale()` — bai hoc da
#    tra gia 3 lan; trang thai chua mo do bang mau `sic--off` lo.
# ⚠️ Phai cat DUNG rule `.badge.off .medal`, dung `split(".badge.off")[-1]`: co nhieu
#    rule bat dau bang `.badge.off` (`.nm`, `.prog`…) nen cua so roi vao rule CUOI va
#    phep kiem tro nen MU — phep thu pha hoai da lot dung o day mot lan.
_ach_css = strip_comments(rd("css/achievements.css"))
_medal_off = re.search(r'\.badge\.off\s+\.medal\s*\{([^}]*)\}', _ach_css)
check("[21] con rule `.badge.off .medal`", bool(_medal_off))
check("[21] me day chua mo dung `sic--off`, khong dung grayscale",
      "sic--off" in strip_comments(rd("achievements.html"))
      and bool(_medal_off) and "grayscale" not in _medal_off.group(1),
      _medal_off.group(1).strip() if _medal_off else "khong tim thay rule")

# ═══════════════════════════════════════════════════════════════════════════
# [22] HAI DO SAU LOI GIAI THICH (js/depth.js) — client khop server
#
# Dai tuoi cua du an la 8–15 va no VAT QUA moc ~11 tuoi (xem js/depth.js). Bo nay
# canh 4 thu, moi thu la mot loi da tra gia o cho khac:
#   a) hai bac khai o client PHAI khop danh sach validation o server;
#   b) do sau KHONG duoc suy tu `level` — level do THOI GIAN CHOI, khong do tuoi;
#   c) trang nao dung `AstroQDepth` thi phai NAP js/depth.js (hai chieu, nhu [21]);
#   d) nut "Tim hieu them" phai con o CA HAI bac — bac chi quyet cai MAC DINH.
# ═══════════════════════════════════════════════════════════════════════════
print("\n=== [22] Hai do sau loi giai thich: client khop server ===")

_dep_js  = rd("js/depth.js")
_dep_src = _no_comments(_dep_js)
_me_cs   = _no_cs_comments(rd_abs(os.path.join(SV, "src", "AstroqSV.Api", "Endpoints", "MeEndpoints.cs")))

# (a) Hai bac, dung hai chuoi, va server liet ke DUNG hai chuoi do.
# ⚠️ Hai bac khai TRONG MOT cau `var JUNIOR = "junior", SENIOR = "senior";` nen dung
#    doi `var` truoc SENIOR — bat theo TEN HANG, khong bat theo tu khoa `var`.
_bands_cl = set(re.findall(r'\b(?:JUNIOR|SENIOR)\s*=\s*"([a-z]+)"', _dep_src))
check("[22] js/depth.js khai dung 2 bac", _bands_cl == {"junior", "senior"}, str(sorted(_bands_cl)))

_depth_guard = re.search(r'depth\s+is\s+not\s+\(([^)]*)\)', _me_cs)
_bands_sv = set(re.findall(r'"([a-z]+)"', _depth_guard.group(1))) if _depth_guard else set()
check("[22] server liet ke dung 2 bac (bad-depth)", _bands_sv == _bands_cl,
      "server=" + str(sorted(_bands_sv)) + " client=" + str(sorted(_bands_cl)))

# ⚠️ `nothing-to-do` PHAI tinh ca `depth`: thieu no thi PUT chi co depth se bi tu
#    choi 400 va viec dong bo bac tu select.html am tham khong bao gio chay.
_nothing = re.search(r'if\s*\(name is null[^)]*\)', _me_cs)
check("[22] `nothing-to-do` co tinh ca depth",
      bool(_nothing) and "depth is null" in _nothing.group(0),
      _nothing.group(0) if _nothing else "khong tim thay dieu kien")

# GET /me/profile va GET /me/achievements deu phai TRA bac — dashboard doc bac tu
# achievements (no la trang co token ma tre di qua truoc khi vao Phong Nghien Cuu).
check('[22] GET tra `depth` (profile + achievements)',
      _me_cs.count('depth     = Str(profile, "depth")') >= 1
      and 'depth    = prof is null ? "" : Str(prof, "depth")' in _me_cs,
      "profile=" + str(_me_cs.count('depth     = Str(profile, "depth")')))

# (b) KHONG suy bac tu level — bay da duoc ghi thanh canh bao o dau js/depth.js.
check("[22] js/depth.js khong doc level/AstroQRanks",
      "AstroQRanks" not in _dep_src and not re.search(r'\.level\b', _dep_src),
      "co doc level trong depth.js")

# (c) Hai chieu: dung thi phai nap, khong dung thi khong nap.
# ⚠️ PHAI SOI CA SCRIPT RIENG CUA TRANG, khong chi soi HTML. `select.html` nap
#    depth.js nhung noi DUNG no la `js/auth-flow.js` — chi doc HTML thi phep kiem
#    bao hong dung luc trang lam dung. (Khac muc [21]: o do loi goi `sic(` nam
#    ngay trong HTML.)
for _f in sorted(f for f in os.listdir(ROOT) if f.endswith(".html")):
    _src2 = rd(_f)
    _l = 'src="js/depth.js"' in _src2
    _u = "AstroQDepth" in strip_comments(_src2)
    if not _u:
        for _js in re.findall(r'<script src="(js/[^"]+\.js)"', _src2):
            if _js == "js/depth.js":
                continue
            try:
                if "AstroQDepth" in _no_comments(rd(_js)):
                    _u = True
                    break
            except OSError:
                pass
    check("[22] " + _f + ": nap js/depth.js <=> co dung no", _l == _u,
          "nap=" + str(_l) + " dung=" + str(_u))

# (d) Nut "Tim hieu them" con o CA HAI bac: `more-wrap` chi duoc an/hien theo tien
#     trinh thi nghiem, KHONG theo bac. Neu mot bac lam mat han nut do thi tre bi
#     may chot ho, dung cai ma `js/depth.js` sinh ra de tranh.
_lab = _no_comments(rd("lab.html"))
check("[22] lab.html: bac chi doi `more-box`, khong an `more-wrap`",
      not re.search(r'more-wrap"\)\.hidden\s*=\s*[^;]*(isSenior|AstroQDepth)', _lab),
      "co nhanh an ca khoi theo bac")
check("[22] lab.html: `more-box` mo san khi la senior",
      bool(re.search(r'more-box"\)\.hidden\s*=\s*!\(window\.AstroQDepth\s*&&\s*AstroQDepth\.isSenior\(\)\)', _lab)))

# select.html phai co dung hai nut, dung hai gia tri bac.
_sel = strip_comments(rd("select.html"))
_sel_bands = set(re.findall(r'data-band="([a-z]+)"', _sel))
check("[22] select.html co 2 nut tuoi, dung 2 bac", _sel_bands == _bands_cl, str(sorted(_sel_bands)))

# ═══════════════════════════════════════════════════════════════════════════
# [23] CUA HANG TRANG TRI — client khop server, va BA DIEU CAM
#
# Bo nay canh dung mot phan cong: **server giu GIA, client giu TEN** (giong
# Wallet.Fees / Achievements.XpLadder). Cong ba dieu cam cua Services/Cosmetics.cs:
# khong ban loi the · khong hop ngau nhien · khong khan hiem gia.
# ═══════════════════════════════════════════════════════════════════════════
print("\n=== [23] Cua hang trang tri: client khop server ===")

_cos_cs = _no_cs_comments(rd_abs(os.path.join(SV, "src", "AstroqSV.Api", "Services", "Cosmetics.cs")))
_cos_js = _no_comments(rd("js/cosmetics.js"))
_shop   = strip_comments(rd("shop.html"))
_ck_css = strip_comments(rd("css/cockpit.css"))

# Bang mon o server: new("<id>", "<kind>", <price>)
_items = re.findall(r'new\("([a-z0-9-]+)",\s*"([a-z]+)",\s*(\d+)\)', _cos_cs)
check("[23] doc ra duoc bang mon o server", len(_items) >= 4, f"{len(_items)} mon")

# ⚠️ ĐỌC BẢNG `Kinds` CỦA SERVER, ĐỪNG GÕ CỨNG TÊN LOẠI. Ban dau cac phep kiem duoi
#    day ghim `(theme|frame)` va `len(...) == 2`, nen them loai mon thu ba la chung
#    **bao hong dung luc san pham lam dung** — dung loai loi "phep kiem bao ve trang
#    thai cu" da lap nhieu lan trong du an. Nay danh sach loai suy tu chinh
#    `Cosmetics.Kinds`, va dieu can canh (hai ben khop nhau) thi giu nguyen.
_kinds_sv = re.search(r'Kinds\s*=\s*\[([^\]]*)\]', _cos_cs)
_kinds_sv = sorted(re.findall(r'"([a-z]+)"', _kinds_sv.group(1))) if _kinds_sv else []
check("[23] doc ra duoc danh sach loai mon o server", len(_kinds_sv) >= 2, str(_kinds_sv))

# ⚠️ PHEP KIEM QUAN TRONG NHAT: client KHONG duoc co mot con so gia nao.
# Chep gia sang JS la hai noi giu mot luat, va ngay doi gia thi ban o client noi
# con so cu — tuc noi SAI voi tre ngay cho no quyet dinh tieu tien.
_prices = {p for _, _, p in _items if p != "0"}
_leak = sorted(p for p in _prices if re.search(r'\b' + p + r'\b', _cos_js))
check("[23] js/cosmetics.js KHONG chua con so gia nao", not _leak, str(_leak))
check("[23] shop.html KHONG gui so tien len server",
      not re.search(r'(price|amount|cost)\s*:', _shop), "co gui so tien")

# ⚠️ THIEN THACH TIM HIEN BANG ANH `img/tt.png`, KHONG BANG EMOJI ☄️.
# Du an chot dieu nay tu 25/07/2026 (bo ca chu "tt" trong toast, thay bang anh), the
# ma hang gia o cua hang van ghep emoji — tren Windows no ve ra mot vet cam va chu du
# an doc khong ra ("mua bang thien thach tim ma sao thanh cai gi the?"). Day la TIEN TE
# cua ca app, hien sai bieu tuong o dung cho tre quyet dinh tieu tien la noi sai.
# ⚠️ Quet tren `_shop` (da boc chu thich) — chinh ghi chu giai thich vi sao KHONG dung
#    emoji cung chua emoji do; day la loi "dem ca chu trong ghi chu cua minh" da tra
#    gia 16 lan.
check("[23] shop.html KHONG dung emoji ☄️ cho Thien thach tim",
      "☄" not in _shop, "con emoji trong code")
check("[23] hang gia dung anh qua AstroQ.ttImg()", "AstroQ.ttImg()" in _shop)
# Token {tt} cua toast phai co o CA vi va en — thieu mot ben la mot ngon ngu hien
# thieu bieu tuong tien te.
check("[23] toast 'thieu tien' dung token {tt} o ca vi va en",
      _shop.count("{tt}") >= 2, "%d cho" % _shop.count("{tt}"))

# Ten (ca vi va en) + o xem truoc: hai chieu.
_ids = [i for i, _, _ in _items]
_no_name = [i for i in _ids if _cos_js.count('"%s":' % i) < 2]
check("[23] moi mon co TEN o ca vi va en", not _no_name, str(_no_name))
_no_sw = [i for i in _ids if (".cos-sw--" + i) not in _ck_css]
check("[23] moi mon co o xem truoc trong css/cockpit.css", not _no_sw, str(_no_sw))
_sw_extra = sorted(set(re.findall(r'\.cos-sw--([a-z0-9-]+)', _ck_css)) - set(_ids))
check("[23] khong co o xem truoc bo khong", not _sw_extra, str(_sw_extra))

# ⚠️ MOI LOAI PHAI CO MOT CHO DE HIEN RA. Day la phep kiem quan trong nhat cua lan
#    them loai mon: thieu no thi mon co that, mua duoc, tru tien duoc, ma **khong
#    hien ra gi** — loi im lang tuyet doi, va tre da tra tien cho no.
_attr_cl = dict(re.findall(r'(\w+):\s*"(data-[a-z-]+)"', _cos_js))
_no_attr = [k for k in _kinds_sv if k not in _attr_cl]
check("[23] moi loai co thuoc tinh gan len <html> (ATTR)", not _no_attr, str(_no_attr))
for _k in _kinds_sv:
    _a = _attr_cl.get(_k)
    if not _a:
        continue
    check("[23] css/cockpit.css ve theo `%s`" % _a, ("[%s=" % _a) in _ck_css,
          "khong co selector nao doc " + _a)
# Hinh dan can mot the that trong DOM de ve len; hai loai kia ap vao phan tu co san.
check("[23] dashboard.html co the .decal cho hinh dan",
      'class="decal"' in rd("dashboard.html") and ".decal{" in _ck_css)
# ⚠️ Lop trang tri nam CHONG len mep bang stats, ma ngay duoi la hang ba o bam duoc
#    (Bang Phi Hanh Gia). Thieu `pointer-events:none` la no nuot cu bam — cung bai
#    hoc `.ver-badge` va `#loader`.
_decal_rule = re.search(r'\.decal\{[^}]*\}', _ck_css)
check("[23] .decal khong nuot cu bam", bool(_decal_rule) and "pointer-events:none" in _decal_rule.group(0),
      _decal_rule.group(0)[:90] if _decal_rule else "khong thay rule")

# Mon mac dinh phai khop hai ben — lech thi tre "dang dung" mot mon khong ton tai.
_def_sv = dict(re.findall(r'\["([a-z]+)"\]\s*=\s*"([a-z0-9-]+)"', _cos_cs))
# ⚠️ CAT LAY DUNG KHOI `DEFAULTS` ROI MOI DOC. Quet ca file thi bang `ATTR`
#    (`theme: "data-cockpit"`) cung khop dung khuon `<loai>: "<chuoi>"` va **de len**
#    ket qua — phep kiem bao hong trong khi hai ben khop nhau. Cung bai hoc "gioi han
#    pham vi dung bang khoi chua no" da tra gia o `showCard` va `.badge.off`.
_def_blk = re.search(r'var DEFAULTS\s*=\s*\{([^}]*)\}', _cos_js)
check("[23] doc ra duoc khoi DEFAULTS o client", bool(_def_blk))
_def_cl = dict(re.findall(r'(%s):\s*"([a-z0-9-]+)"' % "|".join(_kinds_sv or ["theme"]),
                          _def_blk.group(1) if _def_blk else ""))
check("[23] mon mac dinh khop client <-> server",
      _def_sv == _def_cl and sorted(_def_sv) == _kinds_sv,
      f"server={_def_sv} client={_def_cl} kinds={_kinds_sv}")
# Moi loai PHAI co mon mac dinh gia 0 — thieu la tre mua roi khong co duong ve.
check("[23] moi loai co mon mac dinh", sorted(_def_sv) == _kinds_sv, str(sorted(_def_sv)))
check("[23] mon mac dinh deu co gia 0",
      all(p == "0" for i, _, p in _items if i in _def_sv.values()))

# ⚠️ THU TU CO CHU Y: ghi-kho TRUOC, tru-tien SAU. Nguoc lai thi khi ghi kho hong
#    la tre MAT TIEN MA KHONG CO MON — hong theo huong te hon.
_me_cs2 = _no_cs_comments(rd_abs(os.path.join(SV, "src", "AstroqSV.Api", "Endpoints", "MeEndpoints.cs")))
_buy = re.search(r'MapPost\("/shop/buy".*?MapPut\("/shop/equip"', _me_cs2, re.S)
_buy_src = _buy.group(0) if _buy else ""
check("[23] co route /shop/buy", bool(_buy_src))
if _buy_src:
    _i_add = _buy_src.find("TryAddCosmeticAsync")
    _i_pay = _buy_src.find("TrySpendWalletAsync")
    check("[23] ghi kho TRUOC tru tien", 0 <= _i_add < _i_pay, f"add@{_i_add} pay@{_i_pay}")
    check("[23] tru tien hong thi HOAN TAC mon", "RemoveCosmeticAsync" in _buy_src)
    check("[23] gui lai cung opId thi khong tru hai lan", 'TryBeginOpAsync(uid, "buy-"' in _buy_src)
    check("[23] mon gia 0 thi khong ban", '"free-item"' in _buy_src)

# ⚠️ Cua so phai chay tu route NAY toi route KE TIEP. Dung `.*?\}\);` thi no dung
#    ngay o `Results.BadRequest(new {…});` dau tien va cua so KHONG chua CanEquip —
#    phep kiem bao hong dung luc code lam dung (loi cua phep do, khong cua san pham).
_eq = re.search(r'MapPut\("/shop/equip".*?(?=g\.Map|\Z)', _me_cs2, re.S)
check("[23] deo mon: server kiem quyen deo (khong tin client)",
      bool(_eq) and "Cosmetics.CanEquip" in _eq.group(0))

# BA DIEU CAM
check("[23] KHONG hop ngau nhien / gacha (server)",
      not re.search(r'\b(Random|Shuffle|gacha|lootbox)\b', _cos_cs, re.I))
check("[23] KHONG hop ngau nhien / gacha (client)",
      not re.search(r'Math\.random|gacha|lootbox', _cos_js + _shop, re.I)
      or "opId" in _shop,   # Math.random CHI duoc dung de sinh opId
      "co chon mon bang ngau nhien")
# ⚠️ Khong khan hiem gia: khong dem nguoc, khong "chi con hom nay".
# ⚠️ BAN DAU PHEP KIEM NAY CAM CA CHU `setInterval`, va no bao hong ngay khi
#    `whenAuth()` dung mot dong ho de CHO SDK NAP — mot phep kiem bao oan la mot phep
#    kiem som muon bi bo qua. Thu that su tao suc ep thoi gian la CHU HIEN RA, nen
#    phan chu giu nguyen; con dong ho thi doi sang phat bieu dung: cua hang duoc co
#    DUNG MOT cai, va no phai nam trong `whenAuth`. Them cai thu hai la phai giai
#    trinh, dung tinh than "khong khan hiem gia" cua Services/Cosmetics.cs.
check("[23] KHONG khan hiem gia o cua hang (chu)",
      not re.search(r'countdown|hết hạn|sắp hết|chỉ còn|còn lại', _shop, re.I))
_ivals = _shop.count("setInterval(")
_wa = re.search(r'function whenAuth\([^)]*\)\s*\{.*?\n  \}', _shop, re.S)
check("[23] cua hang chi co MOT dong ho, va no de CHO SDK",
      _ivals <= 1 and bool(_wa) and "setInterval(" in _wa.group(0),
      f"{_ivals} setInterval · trong whenAuth={bool(_wa) and 'setInterval(' in _wa.group(0)}")
# Khong ban loi the: moi mon phai thuoc dung hai loai trang tri.
_kinds = sorted({k for _, k, _ in _items})
# ⚠️ DANH SACH TRANG (`DECOR_KINDS`) LA HANG RAO THAT: no khong suy tu `Kinds` cua
#    server, vi neu suy thi ai them `new("xp-boost","boost",50)` cung tu dong "dat".
#    Them mot loai mon moi thi PHAI sua danh sach nay bang tay — tuc phai tra loi
#    cau "mon nay co ban loi the khong" mot lan nua, dung dieu cam so 1 cua
#    Services/Cosmetics.cs.
DECOR_KINDS = ["decal", "frame", "theme"]
check("[23] moi mon la do TRANG TRI (%s)" % "/".join(DECOR_KINDS),
      set(_kinds) <= set(DECOR_KINDS) and set(_kinds_sv) <= set(DECOR_KINDS),
      f"mon={_kinds} kinds={_kinds_sv}")
# Moi loai khai o server phai co it nhat mot mon — mot loai rong thi cua hang ve ra
# mot khoi trong, doc ra thanh "app hong".
check("[23] khong loai nao rong", set(_kinds_sv) <= set(_kinds), f"thieu mon: {sorted(set(_kinds_sv)-set(_kinds))}")
# Ten LOAI mon phai co o ca vi va en (`kind_<loai>`) — thieu la lươi mon hien khoa tho.
_no_kn = [k for k in _kinds_sv if _cos_js.count("kind_%s:" % k) < 2]
check("[23] moi loai co ten o ca vi va en", not _no_kn, str(_no_kn))

# ===========================================================================
# [24] THE "CHO BO ME XEM" (js/brag.js) — KHONG GUI GI RA NGOAI
#
# Ca ly do tinh nang nay ton tai la lay phan lon gia tri cua "khoe" ma KHONG mo
# cua chat / ket ban / tai len. Bo nay canh dung cai cua do van dong:
#   a) khong `fetch` / `XMLHttpRequest` / `navigator.share` / form upload;
#   b) trang nao dung `AstroQBrag` thi phai nap CA js/brag.js VA css/brag.css;
#   c) `.brag[hidden]{display:none}` phai co — bay `[hidden]` da tra gia 6 lan;
#   d) cho khoe o Kho Thanh Tich phai CHAN khi chua doc duoc so lieu (khong bia so).
# ===========================================================================
print("\n=== [24] The 'Cho bo me xem': khong gui gi ra ngoai ===")

_brag_js  = _no_comments(rd("js/brag.js"))
_brag_css = strip_comments(rd("css/brag.css"))

for _bad in ["navigator.share", "fetch(", "XMLHttpRequest", "FormData",
             "new Image(", "enctype", "action="]:
    check("[24] js/brag.js KHONG dung `%s`" % _bad, _bad not in _brag_js)
check("[24] the ve bang canvas (mot nguon su that cho bo cuc)",
      "getContext" in _brag_js and "toDataURL" in _brag_js)
check("[24] cho font xong moi ve (chu khong ra font he thong)",
      "document.fonts" in _brag_js)
check("[24] tra tieu diem ve nut vua bam khi dong",
      "lastFocus" in _brag_js and "Escape" in _brag_js)
# Bay `[hidden]`: `display` cua tac gia THANG `display:none` ma trinh duyet ap.
# `.brag` khai `display:grid` nen no BAT BUOC phai khai lai `[hidden]`.
check("[24] `.brag[hidden]` khai lai display:none",
      bool(re.search(r'\.brag\[hidden\]\s*\{[^}]*display\s*:\s*none', _brag_css)))

for _f in sorted(f for f in os.listdir(ROOT) if f.endswith(".html")):
    _src3 = rd(_f)
    # WARN Trang nhiem vu goi AstroQBrag QUA VO (`js/mission-stage.js`) — no van la
    #   trang "dung" the khoe, nen van phai nap du js + css.
    _u = "AstroQBrag" in strip_comments(_src3) or (
        'src="js/mission-stage.js"' in _src3
        and "AstroQBrag" in strip_comments(rd("js/mission-stage.js")))
    _lj = 'src="js/brag.js"' in _src3
    _lc = 'href="css/brag.css"' in _src3
    check("[24] " + _f + ": dung AstroQBrag <=> nap ca js va css",
          (_u == _lj) and (_u == _lc), "dung=%s js=%s css=%s" % (_u, _lj, _lc))

# (d) Kho Thanh Tich: chua doc duoc so lieu thi KHONG dung the.
_ach24 = _no_comments(rd("achievements.html"))
_openb = re.search(r'function openBrag\(\)\s*\{(.*?)\n  \}', _ach24, re.S)
check("[24] achievements: chan khi chua co so lieu (khong bia so)",
      bool(_openb) and "VIEW.ok" in _openb.group(1) and "VIEW.level" in _openb.group(1),
      "khong tim thay chot chan" if not _openb else "")

# ===========================================================================
# [25] VIEC HANG NGAY + CHUOI NGAY (Services/Daily.cs · js/daily.js)
#
# Nam dieu kien da chot TRUOC khi viet dong nao (xem dau Daily.cs):
#   ① 2 ngay an han/tuan  ② chuoi khong ve 0 (ky luc giu vinh vien)
#   ③ khong dem nguoc     ④ khong giuc     ⑤ noi truoc luat
#
# Muc nay canh nhung dieu DOC DUOC TU MA NGUON; phan phai render moi thay (khong to
# do, vung cham 48px, dich VI/EN, dau "—" khi mat mang) nam o smoke_daily.py, va phan
# server tinh dung nam o test_daily.py.
# ===========================================================================
print("\n=== [25] Viec hang ngay + chuoi ngay ===")

_dl_cs  = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/Daily.cs"))
_dlx_cs = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Data/DynamoContext.Daily.cs"))
_dl_js  = rd("js/daily.js")
_dl_js_code = _no_comments(_dl_js)

# ── Bang viec: doc tu server ──
_dl_tasks = re.findall(r'new\("([a-z]+)",\s*(\d+),\s*(\d+)\)', _dl_cs)
check("[25] doc duoc bang viec o Daily.cs", len(_dl_tasks) >= 3, f"{len(_dl_tasks)} viec")

_dl_ids = [t[0] for t in _dl_tasks]
check("[25] khong co id viec nao bi trung", len(set(_dl_ids)) == len(_dl_ids), str(_dl_ids))

# ⚠️ MOI VIEC PHAI LAM LAI DUOC VO HAN. `lesson` / `planet` / `mission` chi tinh LAN
#    DAU (49 bai, 8 hanh tinh, 7 chang) nen chung SE CAN — mot viec hang ngay khong
#    bao gio hoan thanh duoc nua la mot loi hua vinh vien khong giu duoc. Cung cai bay
#    da ghi o js/specimens.js ("dung viet Mo khoa tai Mission 02").
check("[25] khong viec nao dua tren su kien CHI TINH LAN DAU",
      not ({"lesson", "planet", "mission"} & set(_dl_ids)), str(_dl_ids))

# ⚠️ Thuong phai LON HON phi vao cua game dat nhat, khong thi "viec hang ngay" la mot
#    viec LAM MAT TIEN va tre hoc duoc dung mot dieu: dung lam viec hang ngay.
_dl_fees = [int(m.group(1)) for m in re.finditer(r'\["[a-z]+"\]\s*=\s*(\d+)', _wallet)]
_dl_play = next((int(t[2]) for t in _dl_tasks if t[0] == "play"), 0)
check("[25] thuong viec 'play' > phi game dat nhat",
      _dl_play > max(_dl_fees or [0]), f"{_dl_play} > {max(_dl_fees or [0])}")

# ⚠️ Tran la HANG RAO O PHEP KIEM, khong phai phep kep luc chay (xem Wallet.cs): kep
#    tong luc chay thi server danh dau "da tra" cho ca ba viec ma chi cong tien toi
#    tran, tuc tre mat phan chenh va khong co duong nao lay lai.
_dl_total = sum(int(t[2]) for t in _dl_tasks)
_dl_cap = re.search(r"MaxPerDailyAll\s*=\s*(\d+)", _wallet)
check("[25] tong thuong mot ngay <= MaxPerDailyAll",
      bool(_dl_cap) and _dl_total <= int(_dl_cap.group(1)),
      f"{_dl_total} <= {_dl_cap.group(1) if _dl_cap else '?'}")

# ⚠️ CO'Y KHONG dua "daily" vao Wallet.MaxRewardFor: ham do phuc vu POST /me/progress
#    noi `type` la chuoi CLIENT gui len, nen mot nhanh "daily" o do la mot cua de goi
#    {type:"daily", meteors:19} va tu tra thuong ma khong lam viec nao.
_mrf = re.search(r"MaxRewardFor\(string type\)\s*=>\s*type switch\s*\{(.*?)\};",
                 _no_comments(_wallet), re.S)
check("[25] `daily` KHONG co nhanh trong Wallet.MaxRewardFor",
      bool(_mrf) and '"daily"' not in _mrf.group(1),
      "khong doc duoc MaxRewardFor" if not _mrf else "")

# ── Hai chieu: server giu MOC, client giu TEN ──
# ⚠️ CHI SOI TRONG KHOI `var T = {…}`. Quet ca file thi regex bat luon
#    `vi: {` va `en: {` cua tu dien TXT — bao "thua 2 viec" oan.
_dl_T = re.search(r"var T = \{(.*?)\n  \};", _dl_js, re.S)
_dl_js_ids = re.findall(r"^\s{4}([a-z]+):\s*\{\s*$",
                        _dl_T.group(1) if _dl_T else "", re.M)
check("[25] doc duoc bang ten o js/daily.js", bool(_dl_T) and len(_dl_js_ids) >= 3,
      f"{len(_dl_js_ids)} ten")
check("[25] moi viec cua server co TEN o js/daily.js",
      set(_dl_ids) <= set(_dl_js_ids), f"thieu: {sorted(set(_dl_ids) - set(_dl_js_ids))}")
check("[25] js/daily.js khong khai ten cho viec khong co that",
      set(_dl_js_ids) <= set(_dl_ids), f"thua: {sorted(set(_dl_js_ids) - set(_dl_ids))}")

# ⚠️ CLIENT KHONG DUOC CHUA MOT CON SO LUAT NAO. Go "5 cau" hay "+6 tt" vao chuoi
#    tieng Viet la hai noi cung giu mot con so, va ban o client se noi con so cu vao
#    dung ngay server doi do kho. Chuoi phai dung token {n} roi thay bang `goal`.
_dl_nums = sorted({t[1] for t in _dl_tasks} | {t[2] for t in _dl_tasks})
_dl_bad_nums = [n for n in _dl_nums
                if int(n) > 1 and re.search(r"(?<![\w-])" + n + r"(?![\w-])", _dl_js_code)]
check("[25] js/daily.js khong gan cung moc/thuong cua server",
      not _dl_bad_nums, f"tim thay: {_dl_bad_nums}")
check("[25] ten viec dung token {n} cho moc", _dl_js_code.count("{n}") >= len(_dl_ids),
      f"{_dl_js_code.count('{n}')} token")

# ── ③ KHONG DEM NGUOC, o CA HAI phia ──
# ⚠️ QUET TREN BAN DA BOC GHI CHU. Lan dau toi quet van ban tho va no bao hong
#    ngay: chinh loi canh bao *"dung them expiresAt vao day"* trong Daily.cs
#    chua chu do. Loi "dem ca chu trong ghi chu cua chinh minh" — da lap lai
#    du nhieu lan de thanh phan xa: MOI phep kiem dang "khong duoc chua X"
#    phai chay tren code da boc comment.
_dl_cs_code = _no_comments(_dl_cs)
for _bad in ["expiresAt", "resetAt", "secondsLeft", "deadline", "endsAt"]:
    check(f"[25] ③ Daily.cs khong tra ve '{_bad}'", _bad not in _dl_cs_code)
for _bad in ["setInterval", "setTimeout", "expiresAt", "countdown", "Date.now"]:
    check(f"[25] ③ js/daily.js khong dung '{_bad}'", _bad not in _dl_js_code)

# ⚠️ ② BAN GHI STREAK KHONG DUOC CO `ttl`. No giu KY LUC — thu tre da dat duoc thi
#    khong ai lay lai, ke ca mot co che don rac. Ban ghi WAITLIST# da day bai nay.
_st_blk = re.search(r"TrySetStreakAsync\(.*?\n    \}", _dlx_cs, re.S)
check("[25] ② phep ghi chuoi khong dat ttl",
      bool(_st_blk) and "ttl" not in _st_blk.group(0),
      "khong doc duoc TrySetStreakAsync" if not _st_blk else "")
# Nguoc lai: ban ghi ngay THI PHAI co ttl (chi can cho hom nay, don duoc).
_pay_blk = re.search(r"TryPayDailyAsync\(.*?\n    \}", _dlx_cs, re.S)
check("[25] ban ghi DAILY# CO dat ttl",
      bool(_pay_blk) and "ttl" in _pay_blk.group(0),
      "khong doc duoc TryPayDailyAsync" if not _pay_blk else "")
# ⚠️ Chot chong tra thuong hai lan phai la phep ghi CO DIEU KIEN cua DynamoDB, khong
#    phai mot phep so o tang ung dung: hai loi goi song song deu thay "chua tra".
#    Phep thu pha hoai da chung minh dieu nay (xem pha_daily.py).
check("[25] chot chong tra hai lan la ConditionExpression NOT contains",
      bool(_pay_blk) and "NOT contains(paid" in _pay_blk.group(0))

# ── Khong co route "nhan thuong" ──
# Mot cai nut nhan thuong la mot cach de MAT: quen bam truoc nua dem la mat cong suc
# da bo ra, va no sinh ra dung thu ap luc ma dieu ③④ dang cam.
_me_cs = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Endpoints/MeEndpoints.cs"))
check("[25] khong co route /daily/claim", "/daily/claim" not in _me_cs)
check("[25] co dung MOT route GET /daily",
      len(re.findall(r'MapGet\("/daily"', _me_cs)) == 1)
check("[25] khong co MapPost/MapPut cho /daily",
      not re.search(r'Map(Post|Put)\("/daily', _me_cs))

# ── Hai chieu: trang dung AstroQDaily thi phai nap CA js va css ──
for _f in sorted(f for f in os.listdir(ROOT) if f.endswith(".html")):
    _src = rd(_f)
    _u = "AstroQDaily" in strip_comments(_src)
    _lj = 'src="js/daily.js"' in _src
    _lc = 'href="css/daily.css"' in _src
    check("[25] " + _f + ": dung AstroQDaily <=> nap ca js va css",
          (_u == _lj) and (_u == _lc), "dung=%s js=%s css=%s" % (_u, _lj, _lc))

# ⚠️ `renderDaily` phai nam trong `paintAll`, khong chi goi luc du lieu ve: `applyLang`
#    cung goi `paintAll`, ma chu tren bang do JS sinh nen doi VI/EN o tab khac thi no
#    phai dich theo. Thieu cho nay la bang dung lai o tieng cu — dung loi da tra gia
#    voi nhan ong khoi o buoc ④ cua nhiem vu Trai Dat.
_mis = _no_comments(rd("missions.html"))
_pa = re.search(r"function paintAll\(\)\s*\{(.*?)\}", _mis, re.S)
check("[25] missions.html: paintAll co goi renderDaily",
      bool(_pa) and "renderDaily" in _pa.group(1),
      "khong tim thay paintAll" if not _pa else "")

# ===========================================================================
# [26] NHAT KY TUAN — SO VOI CHINH MINH (js/weeklog.js · Services/Report.cs)
#
# Muc A2 cua de xuat 12/08/2026. Hai dieu phai gac bang phep kiem, vi ca hai deu la
# thu de len vao ma khong ai thay:
#   ① KHONG BAO GIO so voi tre khac. De xuat da bac bang xep hang (muc 5), va day la
#      cho de nhat de no quay lai duoi dang "gioi hon 70% cac ban".
#   ② GIAM KHONG TO DO. Day la nhat ky mot dua tre doc ve CHINH NO; to do dong
#      "it hon 6 cau" la bien mot phep do thanh mot loi phan xet.
# Phan phai render moi thay (mau hieu dung, vung cham, dich VI/EN) o smoke_weeklog.py.
# ===========================================================================
print("\n=== [26] Nhat ky tuan: so voi chinh minh ===")

_wl_js   = rd("js/weeklog.js")
_wl_code = _no_comments(_wl_js)
_wl_css  = strip_comments(rd("css/weeklog.css"))
_rep_cs  = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/Report.cs"))
_pro     = rd("profile.html")
_pro_code = _no_comments(_pro)

# ── ① Khong so voi tre khac ──
# ⚠️ QUET TREN BAN DA BOC GHI CHU: chinh loi canh bao "khong bao gio so voi tre khac"
#    cung chua nhung chu nay. Loi "dem ca chu trong ghi chu cua chinh minh" da lap lai
#    16 lan trong du an.
for _bad in ["leaderboard", "percentile", "xếp hạng", "giỏi hơn", "bạn khác",
             "trung bình của"]:
    check("[26] ① js/weeklog.js khong nhac '%s'" % _bad,
          _bad.lower() not in _wl_code.lower())
# Server cung khong duoc mo mot duong lay du lieu cua tre khac.
check("[26] ① Report.cs khong co khai niem xep hang giua cac tre",
      not re.search(r"(?i)(rank|leaderboard|percentile)", _no_comments(_rep_cs)))

# ── ② Giam khong to do ──
# Bat moi mau trong file roi doi 0 mau nao "do troi" (r nhieu hon g va b ro rang).
def _reddish_hex(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return False
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r > 120 and r > g * 1.8 and r > b * 1.8

_wl_hex = re.findall(r"#[0-9a-fA-F]{3,6}\b", _wl_css)
_wl_red = [h for h in _wl_hex if _reddish_hex(h)]
check("[26] ② css/weeklog.css khong co mot mau do nao", not _wl_red, str(_wl_red))
# ⚠️ Va `.wl-down` phai dung CHUNG khai bao voi `.wl-same` — tach ra la mo duong cho
#    ai do cho no mot mau rieng, tuc mot phan xet rieng.
check("[26] ② `.wl-down` khai CHUNG mot rule voi `.wl-same`",
      bool(re.search(r"\.wl-down\s*,\s*\.wl-same\s*\{", _wl_css)))
check("[26] ② khong animation nao trong css/weeklog.css",
      "animation" not in _wl_css and "@keyframes" not in _wl_css)

# ⚠️ "BANG ky luc", KHONG PHAI "ky luc MOI". Diem tuan bang ky luc ca doi thi chi chac
#    chan duoc rang no BANG — ky luc co the da lap tu tuan truoc. Noi "moi" la mot suy
#    luan khong co can cu trong du lieu.
# ⚠️⚠️ DUNG BAN BOC COMMENT RIENG, KHONG DUNG `_no_comments` CHO PHEP KIEM NAY —
#    va day la mot PHAT HIEN dang ghi lai: `_no_comments()` quet tung ky tu va coi moi
#    dau nhay la mo dau mot CHUOI, nen no bi mot REGEX LITERAL chua dau nhay lam lech.
#    `js/weeklog.js` (va `js/daily.js`) deu co `replace(/[&<>"']/g, …)`: gap dau `"`
#    trong regex do, ham tuong minh dang o trong chuoi va an qua luon ca khoi comment
#    phia sau — nen chinh loi canh bao *"BANG ky luc, KHONG PHAI ky luc MOI"* bi tinh la
#    van ban code. Lan dau chay muc nay no bao hong dung vi vay.
#    O day chi can bo comment nen mot phep the regex la du va khong bi bay do.
_wl_nc = re.sub(r"/\*.*?\*/", "", _wl_js, flags=re.S)
_wl_nc = re.sub(r"(?m)^\s*//.*$", "", _wl_nc)
check("[26] khong noi 'ky luc moi' (suy luan khong co can cu)",
      not re.search(r"(?i)(kỷ lục mới|new record|record mới)", _wl_nc))

# ── Bay `[hidden]` — lan thu 8 trong du an ──
check("[26] `.wl-detail[hidden]` khai lai display:none",
      bool(re.search(r"\.wl-detail\[hidden\]\s*\{[^}]*display\s*:\s*none", _wl_css)))

# ── Server giu MOC, client giu TEN: weeklog KHONG duoc chua ten game ──
# Ten game nam o tung trang (`GAMES` cua games.html, `rec_*` cua profile.html); khai
# them mot ban thu ba o js/weeklog.js la chac chan co ngay ba ban noi ba ten.
for _nm in ["Né Thiên Thạch", "Ghép Chòm Sao", "Bắt Sao Băng", "Mê Cung",
            "Đường Đua", "Asteroid Dodge", "Star Catcher"]:
    check("[26] js/weeklog.js khong khai ten game '%s'" % _nm, _nm not in _wl_js)
check("[26] ten game do TRANG truyen vao qua gameName()", "gameName" in _wl_code)

# ── Server tra ve CA HAI: diem tuan + ky luc ca doi ──
check("[26] Report.WeekStats co truong Bests", "Bests" in _rep_cs)
check("[26] endpoint tra ve lifetime.bests",
      bool(re.search(r"lifetime\s*=\s*new\s*\{[^}]*bests\s*=", _no_comments(_me_cs), re.S)))

# ── Hai chieu: trang dung AstroQWeekLog thi phai nap CA js va css ──
for _f in sorted(f for f in os.listdir(ROOT) if f.endswith(".html")):
    _src = rd(_f)
    _u = "AstroQWeekLog" in strip_comments(_src)
    _lj = 'src="js/weeklog.js"' in _src
    _lc = 'href="css/weeklog.css"' in _src
    check("[26] " + _f + ": dung AstroQWeekLog <=> nap ca js va css",
          (_u == _lj) and (_u == _lc), "dung=%s js=%s css=%s" % (_u, _lj, _lc))

# ⚠️ `renderWeek` phai nam trong `render()`: `applyLang` cung goi `render()`, ma chu
#    tren bang do JS sinh nen doi VI/EN o tab khac thi no phai dich theo.
_pr = re.search(r"function render\(\)\s*\{(.*?)\n  \}", _pro_code, re.S)
check("[26] profile.html: render() co goi renderWeek",
      bool(_pr) and "renderWeek" in _pr.group(1),
      "khong tim thay render()" if not _pr else "")

# ══════════════════════════════════════════════════════════════════════════
# ⚠️⚠️ PHEP KIEM DANG GIA NHAT CUA MUC NAY: MOI GAME CO PHI PHAI CO O KY LUC.
#    Truoc 12/08/2026 bang ky luc o profile.html chi co 3 game, trong khi
#    `Wallet.Fees` da co 6 — nghia la ky luc CO THAT trong `PROGRESS.bests` cua ba
#    game moi KHONG HIEN RA DAU CA: tre lap ky luc ma khong bao gio thay no. Loi im
#    lang, khong phep kiem nao hoi toi. Tu nay them game moi ma quen o ky luc thi
#    day bao ngay.
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ Doc tu bang `Diff` (ten game -> do kho), KHONG doc so viet thang: tu 15/08/2026
#    `Wallet.Fees` la dictionary DAN XUAT tu `FeeByDiff` + `Diff`, nen quet `["x"] = <so>`
#    se bat trung `FeeByDiff` (["easy"]=3...) va cho ra ba "game" ten easy/medium/hard.
_m_diff26 = re.search(r"(?<![A-Za-z])Diff = new\(\)\s*\{(.*?)\};", _wallet, re.S)
_fee_keys = set(re.findall(r'\["([a-z]+)"\]\s*=\s*"[a-z]+"',
                           _m_diff26.group(1) if _m_diff26 else ""))
_rec_keys = set(re.findall(r'\{\s*key:"([a-z]+)"', _pro_code))
check("[26] doc duoc bang phi va bang ky luc",
      len(_fee_keys) >= 3 and len(_rec_keys) >= 3,
      "phi=%s recs=%s" % (sorted(_fee_keys), sorted(_rec_keys)))
check("[26] MOI game co phi deu co o ky luc o profile.html",
      _fee_keys <= _rec_keys, "thieu: %s" % sorted(_fee_keys - _rec_keys))
check("[26] khong o ky luc nao cho game khong co that",
      _rec_keys <= _fee_keys, "thua: %s" % sorted(_rec_keys - _fee_keys))
# Va moi o phai co TEN song ngu (thieu thi o hien khoa tho).
_vi_keys, _en_keys = i18n_dicts(_pro_code)
for _k in sorted(_rec_keys):
    check("[26] ten game '%s' co o CA vi va en" % _k,
          ("rec_" + _k) in _vi_keys and ("rec_" + _k) in _en_keys)


# ══════════════════════════════════════════════════════════════════════════
print("\n=== [27] Trung Tam Dao Tao: games.html ↔ Training.cs ↔ training.js ===")
# ══════════════════════════════════════════════════════════════════════════
# Mot the game tro vao mot chuong trinh KHONG CO o server thi huy hieu "DA DAT"
# khong bao gio hien ra — trang van dep, khong loi console, chi la mot tinh nang
# cham chet. Do la lop hong IM LANG ma phep kiem tinh la cach duy nhat bat duoc.
#
# ⚠️ PHAN CONG (giong badges/specimens): SERVER giu MOC, CLIENT giu TEN.
_trn_cs = rd_abs(os.path.join(SV, "src", "AstroqSV.Api", "Services", "Training.cs"))
_trn_js = rd("js/training.js")
_gam_html = rd("games.html")

if True:
    _cs_nc = _no_cs_comments(_trn_cs)
    # Chuong trinh + khoa hoc khai o server
    _srv_progs = re.findall(r'new\("([a-z]+)",\s*new\[\]', _cs_nc)
    _srv_games = re.findall(r'new Course\("([a-z-]+)",\s*"([^"]+)",\s*(\d+)\)', _cs_nc)
    check("[27] boc duoc chuong trinh tu Training.cs", len(_srv_progs) > 0, str(_srv_progs))

    # Ten khai o client
    _cli_progs = re.findall(r"\n    ([a-z]+): \{\n      ic:", _trn_js)
    check("[27] boc duoc ten chuong trinh tu js/training.js",
          len(_cli_progs) > 0, str(_cli_progs))

    # (a) Moi chuong trinh o server phai co TEN o client — thieu thi the hien
    #     khoa tho ("reaction") truoc mat tre.
    check("[27] moi chuong trinh cua server co ten o js/training.js",
          set(_srv_progs) <= set(_cli_progs),
          "thieu ten: %s" % sorted(set(_srv_progs) - set(_cli_progs)))

    # (b) Va nguoc lai: ten khai o client ma server khong co la ten chet.
    check("[27] khong ten chuong trinh nao o client ma server khong co",
          set(_cli_progs) <= set(_srv_progs),
          "thua: %s" % sorted(set(_cli_progs) - set(_srv_progs)))

    # (c) Moi `prog:` o games.html phai la chuong trinh CO THAT o server.
    _card_progs = set(re.findall(r'prog:"([a-z]+)"', _gam_html))
    check("[27] moi the game tro vao chuong trinh co that",
          _card_progs <= set(_srv_progs),
          "khong co o server: %s" % sorted(_card_progs - set(_srv_progs)))

    # (d) Moi khoa hoc cua server phai la game CO THAT trong games.html.
    _card_keys = set(re.findall(r'\{ key:"([a-z]+)",', _gam_html))
    _srv_gkeys = set(g for g, _, _ in _srv_games)
    check("[27] moi khoa hoc cua server tro vao game co that",
          _srv_gkeys <= _card_keys,
          "khong co the: %s" % sorted(_srv_gkeys - _card_keys))

    # (e) Va moi game co phi (tuc choi duoc) phai thuoc mot chuong trinh — khong
    #     thi no la mot game khong dat duoc chung chi nao, tu dung nam ngoai he.
    check("[27] moi game trong games.html deu thuoc mot chuong trinh",
          _card_keys <= set(re.findall(r'key:"([a-z]+)", prog:"', _gam_html)),
          "thieu prog: %s" % sorted(_card_keys - set(re.findall(r'key:"([a-z]+)", prog:"', _gam_html))))

    # (f) ⚠️⚠️ CLIENT KHONG DUOC GIU MOT CON SO MOC NAO. Moc la LUAT CHOI; hai noi
    #     giu mot luat thi ngay doi do kho, ban o client van noi con so cu.
    _goals = set(str(g) for _, _, g in _srv_games)
    _js_nc = re.sub(r"/\*.*?\*/", " ", _trn_js, flags=re.S)
    _js_nc = re.sub(r"//[^\n]*", " ", _js_nc)
    _leak = sorted(g for g in _goals if len(g) >= 2 and re.search(r"\b" + g + r"\b", _js_nc))
    check("[27] js/training.js KHONG chua con so moc nao cua server",
          not _leak, "lo moc: %s" % _leak)

    # (g) Bai doc goi y phai la bai CO THAT — id sai thi `library.html?a=` lang
    #     le khong mo gi, va tre bam vao mot duong dan cut.
    _read_ids = re.findall(r'read: \{ id: "([a-z0-9-]+)"', _trn_js)
    _idx = rd("js/articles-index.js")
    _bad_read = [a for a in _read_ids if ('id: "%s"' % a) not in _idx]
    check("[27] moi bai doc goi y co that trong articles-index",
          not _bad_read, "khong co bai: %s" % _bad_read)

    # (h) library.html phai HIEU duoc `?a=` — thieu thi moi duong doc bai o tren
    #     deu do tre vao luoi 67 bai roi bat tu tim.
    _lib = rd("library.html")
    check("[27] library.html mo duoc mot bai theo `?a=`",
          'get("a")' in _lib and "openReader(want)" in _lib)

# ═════════════════════════ [28] THE CHIA SE (Open Graph) ═════════════════════════
# ⚠️ VI SAO CAN PHEP KIEM NAY: `og:image` tro vao mot tep KHONG TON TAI thi
#    Facebook dung the xem truoc RONG — va **khong co gi bao loi**: trang van mo
#    binh thuong, console sach, chi nguoi la nhin thay mot o xam. Day dung lop loi
#    im lang ma du an da tra gia (`sic()` tra chuoi rong khi ten icon sai).
# ⚠️ Va no doi chieu TIEU DE the voi `games.html` — the chia se la chuoi NGUOI LA
#    doc dau tien, lech mot ten game o day con te hon lech trong app.
print("")
print("=== [28] The chia se: anh co that, tieu de khop games.html ===")

_OGM = "<!-- OG:BEGIN"
_og_pages = {}
_gsrc = rd("games.html")
_gblk = re.search(r"var GAMES\s*=\s*\[(.*?)\n\s*\];", _gsrc, re.S)
if _gblk:
    for _m in re.finditer(r"\{(.*?)\}\s*\}\s*,?", _gblk.group(1), re.S):
        _b = _m.group(1)
        _f = re.search(r'file\s*:\s*"([^"]*)"', _b)
        _n = re.search(r'name\s*:\s*\{\s*vi\s*:\s*"([^"]*)"', _b)
        if _f and _n:
            _og_pages[_f.group(1)] = _n.group(1)

check("[28] doc duoc >= 10 game tu games.html", len(_og_pages) >= 10,
      "doc duoc %d" % len(_og_pages))

_og_extra = ["games.html", "lab.html", "crew.html",
             "mission-earth.html", "mission-orbit.html"]
_all_og = sorted(set(list(_og_pages) + _og_extra))

_miss_block, _miss_img, _bad_title, _bad_dim, _rel_url = [], [], [], [], []
for _pg in _all_og:
    _path = os.path.join(ROOT, _pg)
    if not os.path.exists(_path):
        _miss_block.append(_pg + " (thieu trang)")
        continue
    _src = io.open(_path, encoding="utf-8").read()
    if _OGM not in _src:
        _miss_block.append(_pg)
        continue

    _im = re.search(r'property="og:image" content="https://astroq\.org(/[^"]+)"', _src)
    if not _im:
        _miss_img.append(_pg + " (thieu the og:image)")
    else:
        _rel = _im.group(1).lstrip("/")
        if not os.path.exists(os.path.join(ROOT, _rel)):
            _miss_img.append("%s -> %s" % (_pg, _rel))

    if _pg in _og_pages:
        _t = re.search(r'property="og:title" content="([^"]*)"', _src)
        if not _t or _og_pages[_pg] not in _t.group(1):
            _bad_title.append("%s: the=%r games.html=%r"
                              % (_pg, _t.group(1) if _t else "?", _og_pages[_pg]))

    if 'content="1200"' not in _src or 'content="630"' not in _src:
        _bad_dim.append(_pg)

    # ⚠️ `og:url` phai TUYET DOI: the nay duoc doc tren may chu cua Facebook,
    #    khong co ngu canh trang — duong dan tuong doi la mot the vo nghia.
    if 'property="og:url" content="https://' not in _src:
        _rel_url.append(_pg)

check("[28] moi trang dang fanpage deu co khoi OG", not _miss_block,
      "thieu: %s" % _miss_block[:4])
check("[28] moi `og:image` tro vao tep CO THAT", not _miss_img,
      "hong: %s" % _miss_img[:4])
check("[28] tieu de OG mang dung ten game cua games.html", not _bad_title,
      "lech: %s" % _bad_title[:3])
check("[28] the khai dung 1200x630", not _bad_dim, "sai: %s" % _bad_dim[:4])
check("[28] moi `og:url` la duong dan tuyet doi", not _rel_url, "hong: %s" % _rel_url[:4])

# ⚠️ Anh phai DUNG 1200x630 THAT, khong chi khai trong the — khai mot dang ma tep
#    mot neo thi Facebook cat xen theo TEP, va the xem truoc met mo.
_og_dir = os.path.join(ROOT, "img", "og")
_wrong_size = []
_have_pil = True
try:
    from PIL import Image as _PILImage
except ImportError:
    _have_pil = False

if _have_pil and os.path.isdir(_og_dir):
    for _f in sorted(os.listdir(_og_dir)):
        if _f.endswith(".jpg"):
            with _PILImage.open(os.path.join(_og_dir, _f)) as _i:
                if _i.size != (1200, 630):
                    _wrong_size.append("%s=%s" % (_f, _i.size))

check("[28] moi anh trong img/og/ dung 1200x630" if _have_pil
      else "[28] anh OG dung co (bo qua: khong co Pillow)",
      not _wrong_size, "sai co: %s" % _wrong_size[:4])

# ⚠️ Khoi OG SINH RA bang script; sua tay la lan chay sau mat. Phep kiem nay chi
#    doi khoi con nguyen hai moc — no khong doc duoc "ai da sua tay", nhung no
#    chan duoc ca xoa moc lan cat doi khoi.
_broken = [p for p in _all_og
           if os.path.exists(os.path.join(ROOT, p))
           and (io.open(os.path.join(ROOT, p), encoding="utf-8").read().count(_OGM)
                != io.open(os.path.join(ROOT, p), encoding="utf-8").read().count("<!-- OG:END -->"))]
check("[28] khoi OG con du ca hai moc BEGIN/END", not _broken, "hong: %s" % _broken[:4])

# ═════════════════════ [29] QUY NGUON (UTM) ═════════════════════
# ⚠️ VI SAO CAN: chuoi nay do CLIENT gui len, ma no di thang vao DynamoDB roi hien
#    ra o trang bao cao admin. `js/utm.js` loc mot lan cho gon giao dien; hang rao
#    THAT la `Services/Campaign.cs`. Hai ben LECH LUAT thi client hien mot dang ma
#    DB luu mot neo, va nguoi doc bao cao khong doi chieu duoc voi link da dang.
# ⚠️ Va no canh mot chuyen quan trong hon: trang chu la trang DUY NHAT duoc lap chi
#    muc, no co y khong nap SDK Firebase (64 KB) va khong nap trinh theo doi nao.
#    Mot `fetch` len trong `js/utm.js` la mo lai dung canh cua da dong.
print("")
print("=== [29] Quy nguon: client va server cung mot luat ===")

def rd_sv(rel):
    """Doc ma nguon backend (nam NGOAI repo, o ../AstroqSV/)."""
    return rd_abs(os.path.join(SV, "src/AstroqSV.Api", rel))


_UTM_PAGES = sorted([os.path.basename(f) for f in glob.glob(os.path.join(ROOT, "*.html"))]
                    + ["en/index.html"])

_utm = rd("js/utm.js")
_cam = rd_sv("Services/Campaign.cs")
_utm_code = strip_comments(_utm)

# --- luat loc phai khop hai ben ---
_m1 = re.search(r"MAX_AGE_DAYS\s*=\s*(\d+)", _utm)
_m2 = re.search(r"MAX_PART\s*=\s*(\d+)", _utm)
_s1 = re.search(r"MaxPart\s*=\s*(\d+)", _cam)
_s2 = re.search(r"MaxParts\s*=\s*(\d+)", _cam)
check("[29] client khai duoc tran do dai moi phan", bool(_m2), _m2 and _m2.group(1))
check("[29] server khai duoc tran do dai moi phan", bool(_s1), _s1 and _s1.group(1))
check("[29] tran do dai KHOP hai ben", bool(_m2 and _s1) and _m2.group(1) == _s1.group(1),
      "client=%s server=%s" % (_m2 and _m2.group(1), _s1 and _s1.group(1)))
check("[29] server chi nhan toi da 3 phan", bool(_s2) and _s2.group(1) == "3",
      _s2 and _s2.group(1))
check("[29] client cung ghep toi da 3 phan (source/medium/campaign)",
      _utm_code.count("o.source") >= 1 and "o.medium" in _utm_code and "o.campaign" in _utm_code)
check("[29] han luu co that va > 0 ngay", bool(_m1) and int(_m1.group(1)) > 0,
      _m1 and _m1.group(1))

# ⚠️ Bo ky tu phai giong nhau. Client dung regex, server duyet tung ky tu - khong so
#    duoc bang chuoi, nen doi DUNG bon loai duoc phep xuat hien o ca hai ben.
check("[29] client chi nhan a-z 0-9 . _ -", "[^a-z0-9._-]" in _utm_code, )
check("[29] server cung chi nhan a-z 0-9 . _ -",
      all(t in _cam for t in ("'a'", "'z'", "'0'", "'9'", "'.'", "'_'", "'-'")))

# --- 0 byte ra ngoai ---
# ⚠️ Do tren ma DA BOC CHU THICH: chinh doan giai thich "vi sao khong dung Google
#    Analytics" co chua chu `fetch`/`request`. Bai hoc lap lai lan thu ~19.
for _bad in ("fetch(", "XMLHttpRequest", "sendBeacon", "new Image(", "document.cookie",
             "googletagmanager", "google-analytics"):
    check("[29] js/utm.js khong dung `%s`" % _bad, _bad not in _utm_code)

# --- da nap o dung ba trang, va KHONG nap o trang khac ---
# ⚠️ Nap thua o 15 trang khac la ~1 KB chet moi trang cho mot thu khong ai doc:
#    nhan chi duoc BAT o cua vao (trang chu / landing) va DOC o hai cho gui form.
_utm_want = {"index.html", "en/index.html", "landing-app.html"}
_utm_has = set()
for _pg in _UTM_PAGES:
    _p = os.path.join(ROOT, _pg)
    if os.path.exists(_p) and re.search(r'src="[^"]*js/utm\.js"',
                                        io.open(_p, encoding="utf-8").read()):
        _utm_has.add(_pg)
check("[29] nap js/utm.js o dung ba cua vao", _utm_has == _utm_want,
      "thua: %s  thieu: %s" % (sorted(_utm_has - _utm_want), sorted(_utm_want - _utm_has)))

# --- hai cho gui phai mang nhan di ---
# ⚠️ DOI PHAT BIEU 20/08/2026: form waitlist da bo, nen trang chu khong con cho nao
#    gui nhan nguon. Duong duy nhat con lai la `/auth/register` (phep kiem ngay duoi).
#    Chieu can canh: trang chu khong con loi goi mang nao — mai nay co lai thi phai
#    mang nhan nguon theo, khong thi mat quy nguon ma khong ai biet.
check("[29] trang chu khong con loi goi mang nao (nen khong con cho gui nhan)",
      "apiPost" not in strip_comments(rd("js/index.js")))
check("[29] dang ky tai khoan gui kem `src`",
      "AstroQUtm" in strip_comments(rd("js/firebase-auth.js"))
      and re.search(r'apiPost\("/auth/register",\s*\{[^}]*src',
                    strip_comments(rd("js/firebase-auth.js"))) is not None)

# --- server loc lai o CA HAI cua ---
_wep = rd_sv("Endpoints/WaitlistEndpoints.cs")
_aep = rd_sv("Endpoints/AuthEndpoints.cs")
check("[29] /waitlist loc lai bang Campaign.Clean", "Campaign.Clean(req.Src)" in _wep)
check("[29] /auth/register loc lai bang Campaign.Clean", "Campaign.Clean(req?.Src)" in _aep)

# ⚠️ GIU LUOT CHAM DAU TIEN. Cau hoi la "cai gi mang nguoi nay toi" - do la lan DAU.
#    Ghi de theo luot cuoi thi cong cua bai dang bien mat va moi bai deu trong nhu
#    vo dung; con o duong dang ky no la mot lo hong nho (nguoi thu hai dang ky de len
#    mot dia chi dang cho se viet lai duoc nguon cua nan nhan).
check("[29] waitlist giu nhan cua luot DAU", "IsNullOrEmpty(existing?.Src)" in _wep)
check("[29] dang ky giu nhan cua luot DAU",
      re.search(r"effSrc\s*=\s*resend\s*&&\s*!string\.IsNullOrEmpty\(existing!?\.Src\)", _aep)
      is not None)
check("[29] nhan di tiep sang HO SO luc kich hoat", "CreateUserAsync(uid, email, p.Name, p.Src)" in _aep)

# ⚠️ `source` (header Origin) la TRUONG KHAC. Ghi de no la vua mat du lieu cu vua tron
#    hai nghia vao mot cho - va Origin thi luon la "https://astroq.org", vo dung cho
#    viec quy nguon. Hai truong, hai cau hoi.
check("[29] `source` (Origin) van duoc ghi rieng, khong bi `src` ghi de",
      "Source:     ctx.Request.Headers.Origin" in _wep)
_dyn = rd_sv("Data/DynamoContext.cs")
check("[29] ban ghi waitlist luu ca hai truong",
      '["source"]     = S(w.Source)' in _dyn and '["src"]        = S(w.Src)' in _dyn)
check("[29] ban ghi cho luu `src`", '["src"]         = S(p.Src)' in _dyn)
check("[29] ho so luu `src`", '["src"]       = S(src)' in _dyn)

# --- bao cao admin phai co cho HIEN RA ---
# ⚠️ Thieu phep kiem nay thi nhan co that, luu that, ma khong hien ra o dau - dung
#    lop loi im lang da tra gia o lan them loai mon thu ba cho cua hang.
_ins = rd_sv("Services/Insights.cs")
_adm = rd("js/admin-report.js")
check("[29] server tra bang nguon", "SrcRow(" in _ins and "Sources: sources" in _ins)
check("[29] bang nguon co ca hang cho lan tai khoan",
      re.search(r"SrcRow\(string Src, long Waitlist, long Signups, long Active7, long EarthDone\)",
                _ins) is not None)
check("[29] client co the `sources`", 'sources: {' in _adm and '"p-src"' in _adm)
check("[29] trang bao cao co o ve `p-src`", 'id="p-src"' in rd("admin-report.html"))
# ⚠️ MOI KY TU TRONG NHAN DO CLIENT SINH PHAI NAM TRONG SUBSET FONT TU HOST.
#    Font cua du an chi co latin + vietnamese (cat 621->101 KB ngay 26/07/2026), nen
#    mot ky hieu ngoai subset se lui ve font he thong va render ra GLYPH KHAC HAN -
#    da gap that voi "↳" (U+21B3) o nhan hang con cua bang nguon. Doc CSS thi khong
#    thay; chi render moi thay. Phep kiem nay chan duong quay lai.
_ranges = []
for _m in re.finditer(r"unicode-range:\s*([^;]+);", rd("css/fonts.css")):
    for _part in _m.group(1).split(","):
        _part = _part.strip().upper().replace("U+", "")
        if "-" in _part:
            _a, _b = _part.split("-"); _ranges.append((int(_a, 16), int(_b, 16)))
        elif _part:
            _ranges.append((int(_part.replace("?", "0"), 16),
                            int(_part.replace("?", "F"), 16)))
check("[29] doc duoc unicode-range cua font tu host", len(_ranges) >= 2, len(_ranges))

def _in_font(ch):
    return any(a <= ord(ch) <= b for a, b in _ranges)

_labels = re.findall(r'label:\s*"([^"]*)"', _adm) + re.findall(r'name:\s*x\.src \? x\.src : "([^"]*)"', _adm)
_out_font = sorted({ch for lab in _labels for ch in lab if not _in_font(ch)})
check("[29] moi ky tu trong nhan do admin-report sinh deu co trong font tu host",
      not _out_font, "ngoai subset: %s" % [(c, hex(ord(c))) for c in _out_font])

check("[29] nhan rong duoc doi ra chu, khong de o trong",
      "không rõ nguồn" in _adm)


# ═════════ [30] BOX THOAI KHONG DUOC DE LEN BANG DAY (loi 19/08/2026) ═════════
# Chu du an choi that chang (1) `mission-orbit.html` va gui anh: bang "HE THONG QUAN
# SAT" de kin box thoai, che luon nut OK — duong DUY NHAT di tiep. Nguyen nhan: viec
# nhac box nam o `boardSay()`, tuc MOI CHO GOI phai tu nho dung ham nao, ma chang (1)
# goi `say()` thang. Nay `say()` tu do bang dang mo. Bon phep kiem duoi giu dung bon
# dieu de loi do khong quay lai duoi mot cai ten khac.
print("\n=== [30] Box thoai nhac len khoi bang day ===")
_st30 = io.open(os.path.join(ROOT, "js", "mission-stage.js"), encoding="utf-8").read()

_say30 = re.search(r"function say\(who, html, opt\) \{(.*?)\n    \}", _st30, re.S)
check("[30] doc duoc than ham `say()`", bool(_say30))
check("[30] `say()` TU nhac box len khoi bang day (khong doi cho goi nho)",
      bool(_say30) and "liftAboveBoards(el)" in _say30.group(1))

# Mot phep do dung cho CA the lan box thoai — hai cho do la hai con so som muon lech nhau.
check("[30] `liftCard` dung lai chinh phep do do (`liftAboveBoards`)",
      re.search(r'function liftCard\(\)\s*\{\s*liftAboveBoards\(\$\("card"\)\);\s*\}', _st30) is not None)

# `boardSay` da bo: con mot cho goi ten cu la loi runtime ngay lan tha sai dau tien.
# ⚠️ BOC COMMENT TRUOC (dung lai `_no_cs_comments`): khoi ghi chu cua chinh ban sua nay
#    CO NHAC ten `boardSay()` de ke lai loi cu, va dem ca chu trong ghi chu cua minh la
#    kieu loi du an nay da mac vai lan.
_bs30 = []
for _f30 in ["js/mission-stage.js", "mission-earth.html", "mission-orbit.html",
             "mission-planet.html", "mission-tree.html", "mission-map.html"]:
    _fp30 = os.path.join(ROOT, _f30)
    if os.path.exists(_fp30) and "boardSay" in _no_cs_comments(
            io.open(_fp30, encoding="utf-8").read()):
        _bs30.append(_f30)
check("[30] khong con cho nao goi `boardSay` (ham da bo)", not _bs30, "con o: %s" % _bs30)

# ⚠️ `nudge(hintId, wrongText, hintText)` — 3 tham so. Chu ky CU co `boardId` dung dau;
#    sot mot cho goi 4 tham so thi cau khich le bi ghi vao THE BANG (id bang) con dong
#    nhac khong doi — bang van trong DUNG, khong ai thay: dung kieu loi im lang.
_nud_bad, _nud_id = [], []
for _f30 in ["mission-earth.html", "mission-orbit.html"]:
    _src30 = io.open(os.path.join(ROOT, _f30), encoding="utf-8").read()
    for _m30 in re.finditer(r"(?<![\w.])nudge\(([^)]*)\)", _src30):
        _args30 = [a.strip() for a in _m30.group(1).split(",")]
        if len(_args30) != 3:
            _nud_bad.append("%s: nudge(%s)" % (_f30, _m30.group(1)))
            continue
        _first30 = _args30[0].strip("'\"")
        # Chi soi loi goi THAT (tham so dau la chuoi); vo bao boc truyen bien thi bo qua.
        if _args30[0][:1] in "'\"":
            if not _first30.endswith("-hint"):
                _nud_id.append("%s: %s" % (_f30, _first30))
            elif ('id="%s"' % _first30) not in _src30:
                _nud_id.append("%s: %s (khong co id nay trong trang)" % (_f30, _first30))
check("[30] moi cho goi `nudge` dung chu ky 3 tham so", not _nud_bad, "%s" % _nud_bad[:3])
check("[30] tham so dau cua `nudge` la id DONG NHAC co that", not _nud_id, "%s" % _nud_id[:3])


print("\n=== [31] DO KHO TU DIEU CHINH: server va client cung mot bo moc ===")
# Chot 19/08/2026 ("vai (2)"). Cap do do SERVER tinh (Services/Adapt.cs), client chi
# doc lai. Muc nay doi chieu HAI BEN — cung ly do voi [3d]: mot ben doi mot ben khong
# thi tre doc con so cua client nhung nhan de bai theo con so cua server.
_adapt = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/Adapt.cs"))
_prog = rd("js/progress.js")
_qidx = rd("js/quiz-index.js")
_quiz31 = rd("quiz.html")

check("server: co Services/Adapt.cs", bool(_adapt.strip()))

# --- (1) Tran cap do: server khai 3, client kep 3, bank co toi 3 ---
m_max = re.search(r"MaxQuizLevel\s*=\s*(\d+)", _adapt)
check("server: khai MaxQuizLevel", bool(m_max), str(m_max))
# Bank: doc bang LV cua muc luc (SINH RA tu js/quiz/*.js) roi lay gia tri lon nhat.
_lvs = [int(x) for x in re.findall(r'"[^"]+":\s*(\d+)',
        _qidx.split("var LV = {")[1].split("};")[0])] if "var LV = {" in _qidx else []
check("muc luc co bang LV va khong rong", len(_lvs) > 0, "%d cau khai lv" % len(_lvs))
if m_max and _lvs:
    check("tran cap do cua server = cap lon nhat bank THAT SU co",
          int(m_max.group(1)) == max(_lvs),
          "server %s vs bank %d" % (m_max.group(1), max(_lvs)))
    # ⚠️ Client kep [1..3] o `absorbQuizLv` va `quizLvCache`. Kep chat hon server thi
    #    cap cao nhat khong bao gio den duoc tay tre; long hon thi Quiz di tim mot cap
    #    khong ton tai. Hai cho, dem ca hai.
    # ⚠️ Quet CA HAI dang viet. Ban dau chi tim `lv > N) return` nen bo sot cho thu
    #    hai (`box.lv < 1 || box.lv > 3` nam trong mot dieu kien ghep) va bao hong OAN.
    _clamps = re.findall(r"(?:box\.)?lv\s*>\s*(\d+)", _prog)
    check("js/progress.js kep tran cap do o dung 2 cho (ghi + doc)",
          len(_clamps) == 2, str(_clamps))
    check("tran kep o client = tran cua server",
          all(c == m_max.group(1) for c in _clamps),
          "client %s vs server %s" % (_clamps, m_max.group(1)))

# --- (2) Moc len cap 2 KHONG duoc go lai bang so ---
# `Adapt.Level2Ratio` phai TRO vao `Wallet.QuizPassRatio`, khong phai mot ban sao:
# "dat mot luot" va "du suc lam cau phan biet" la cung mot moc.
check("server: moc cap 2 tro vao Wallet.QuizPassRatio, khong go lai so",
      re.search(r"Level2Ratio\s*=\s*Wallet\.QuizPassRatio", _adapt) is not None)

# --- (3) Client KHONG duoc tu tinh cap do ---
# Day la dieu de vo nhat: `quizAccuracy` nam ngay trong cung cau tra loi, rat de bi
# dem ra tinh lai o client — roi hai noi cho hai ket qua khac nhau cho cung mot tre.
for _n, _c in (("quiz.html", strip_comments(_quiz31)),
               ("js/progress.js", strip_comments(_prog))):
    check("%s: KHONG tu tinh cap do tu quizAccuracy" % _n,
          "quizAccuracy" not in _c, "con dung quizAccuracy")
check("quiz.html: doc cap do qua AstroQProgress.quizLv()",
      "AstroQProgress.quizLv" in strip_comments(_quiz31))
check("js/progress.js: cache cap do co DONG DAU uid",
      re.search(r"write\(LS_QUIZLV,\s*\{\s*uid:\s*uidNow\(\)", _prog) is not None)
# ⚠️⚠️ DOI PHAT BIEU 20/08/2026. Ban cu doi `removeItem(LS_QUIZLV)` co trong
#    js/progress.js — tuc ghim vao `AstroQProgress.clearLocal()`, mot ham co DUNG 0
#    NGUOI GOI ke tu luc duoc viet. Nghia la phep kiem nay xanh trong khi dang xuat
#    KHONG he don cache nao: do duoc tren ban that 20/08/2026, sau khi dang xuat con
#    7 khoa `astroq-*` cua tre vua dung. Mot phep kiem canh mot ham khong ai goi thi
#    no canh mot y dinh, khong canh mot hanh vi.
#    Nay viec do la `AstroQ.clearAccountData()` (don theo TIEN TO + danh sach giu
#    lai), va phep kiem doi DUNG ba chan: ham ton tai · danh sach giu lai khong chua
#    khoa per-tre nao · `logout()` co goi no.
_uicnc = strip_comments(rd("js/ui-common.js"))
_fba = strip_comments(rd("js/firebase-auth.js"))
check("js/ui-common.js: co AstroQ.clearAccountData()",
      "function clearAccountData(" in _uicnc and "clearAccountData: clearAccountData" in _uicnc)
check("clearAccountData don theo TIEN TO astroq- (khoa moi tu duoc don)",
      'indexOf("astroq-") === 0' in _uicnc)
_keep_m = re.search(r"var KEEP = \[(.*?)\];", _uicnc, re.S)
_keep = set(re.findall(r'"([^"]+)"', _keep_m.group(1))) if _keep_m else set()
_per_child = ["astroq-user", "astroq-quiz-lv", "astroq-progress", "astroq-asteroids",
              "astroq-route-gate", "astroq-mission-steps", "astroq-training",
              "astroq-tour-seen", "astroq-map01-seen", "astroq-read",
              "astroq-quiz-left", "astroq-progress-queue"]
_leak = [k for k in _per_child if k in _keep]
check("danh sach giu lai KHONG chua khoa nao cua tre (%d khoa)" % len(_keep),
      not _leak, "lot: " + str(_leak))
check("firebase-auth.logout() goi clearAccountData",
      "clearAccountData" in _fba)
# ⚠️ THU TU LA CA BAN SUA: xoa cuc bo TRUOC khi cho mang. Ban cu `await boot()`
#    truoc, nen SDK tai cham la `logout()` khong bao gio resolve va nut Dang xuat
#    thanh nut chet, im lang (tai hien duoc tren ban that 20/08/2026).
_lg = _fba[_fba.index("async logout()"):]
_lg = _lg[:_lg.index("return {")]
check("logout(): xoa cuc bo TRUOC khi cho mang",
      _lg.index("clearAccountData") < _lg.index("await"),
      "clear o %d, await o %d" % (_lg.index("clearAccountData"), _lg.index("await")))
check("logout(): co HAN CHO cho signOut (khong treo vo han)",
      "SIGNOUT_MS" in _fba and "Promise.race" in _lg)
# ⚠️ `verifyAdmin` KHONG duoc hoi sinh ho so: `js/admin-link.js` goi no o NEN tren
#    dashboard/profile, nen phien Firebase con song sau khi dang xuat la no AM THAM
#    dang nhap lai cho tre.
_va = _fba[_fba.index("async verifyAdmin("):]
_va = _va[:_va.index("return admin;")]
check("verifyAdmin() chi CAP NHAT ho so dang co, khong dung ho so moi",
      "AstroQ.getUser()" in _va and "syncProfile" in _va)

# --- (4) Server phai THUC SU tra `quizLv` ra ngoai ---
check("server: Snapshot() tra `quizLv`",
      re.search(r"quizLv\s*=\s*Adapt\.QuizLevel\(p\)", _ep) is not None)

# --- (5) `pickKeys` phai co duong lui, va bang LV la SINH RA ---
check("muc luc: pickKeys nhan tham so cap do",
      "function pickKeys(n, lv)" in _qidx)
check("muc luc: co duong lui noi sang cap lan can (`nearest`)",
      "function nearest(ks, lv)" in _qidx)

print("\n=== [34] HAN MUC LUOT QUIZ: trang gia noi dung con so server ap ===")
# Chot 19/08/2026 (chu du an: "gioi han 5 luot/ngay o server").
# ⚠️ Truoc luot nay trang gia quang cao "3 luot/ngay" ma server KHONG gioi han gi —
#    tuc ban mien phi that ra choi khong han che. Muc nay chan lop loi do lap lai.
_qa = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Services/QuizAccess.cs"))
_pr34 = rd("pricing.html")

check("server: co Services/QuizAccess.cs", bool(_qa.strip()))
m34 = re.search(r"FreeRoundsPerDay\s*=\s*(\d+)", _qa)
check("server: khai FreeRoundsPerDay", bool(m34), str(m34))

if m34:
    _n = m34.group(1)
    # Trang gia mo ta con so nay o `c_quiz_lim`, CA HAI ngon ngu.
    _lims = re.findall(r'c_quiz_lim:"([^"]*)"', _pr34)
    check("pricing.html khai `c_quiz_lim` o ca hai ngon ngu", len(_lims) == 2, str(_lims))
    _bad34 = [x for x in _lims if _n not in x]
    check("moi ban dich cua `c_quiz_lim` deu dung con so server (%s)" % _n,
          not _bad34, "lech: %s" % _bad34)
    # Va khong duoc con con so CU nao lang vang tren trang.
    for _old in ("3 lượt/ngày", "3 rounds/day"):
        check("pricing.html KHONG con con so cu '%s'" % _old, _old not in _pr34)

# --- Cong phai la PHEP GHI CO DIEU KIEN, khong phai phep so o tang ung dung ---
# ⚠️⚠️ Ban dau (19/08/2026) dem so dong `HIST#` cua hom nay roi so voi tran o tang
#    ung dung — tuc DOC-ROI-SO-ROI-GHI. Do duoc 20/08/2026: **12 luot gui SONG SONG
#    ghi duoc 9 dong trong khi tran la 5**, vi ca 12 loi goi deu doc thay "con suat".
#    Muc nay chan dung duong quay lai do.
_dyd = rd_abs(os.path.join(SV, "src/AstroqSV.Api/Data/DynamoContext.Daily.cs"))
check("server: co TryClaimQuizRoundAsync", "TryClaimQuizRoundAsync" in _dyd)
_iclaim = _dyd.find("TryClaimQuizRoundAsync")
_body = _dyd[_iclaim:_iclaim + 2600] if _iclaim >= 0 else ""
check("server: cong la phep ghi CO DIEU KIEN tren bo dem `quizRounds`",
      "ConditionExpression" in _body and "quizRounds < :cap" in _body)
check("server: cong bang phep cong NGUYEN TU (`ADD`), khong phai `SET` so da doc",
      "ADD quizRounds :one" in _body)
check("server: tra ve suat vua gianh (UPDATED_NEW) de khoi dem lai nhat ky",
      "ReturnValue.UPDATED_NEW" in _body)
check("server: POST /me/progress goi TryClaimQuizRoundAsync",
      "TryClaimQuizRoundAsync(" in _ep)
check("server: het luot thi tra `counted:false` + reason (khong tra 4xx)",
      'reason = "quiz-daily-limit"' in _ep)
# ⚠️ KHONG duoc quay lai cach dem nhat ky de gac — dem bao nhieu lan cung khong
#    gac duoc ca goi song song.
for _dead in ("QuizAccess.RoundsToday", "QuizAccess.Allowed"):
    check("server: KHONG con `%s` (phep so o tang ung dung)" % _dead,
          _dead not in _ep and _dead not in _qa)
# ⚠️ Gianh suat TRUOC khi ghi nhat ky (ghi truoc thi cong dem ca chinh luot dang nop),
#    va SAU phep kiem du lieu vao (gianh suat la MOT CHIEU — mot loi goi rac ma tieu
#    mat mot suat cua tre la hong; ban cu dat truoc `switch` nen ca `total = 0` luc da
#    het luot tra 200 `counted:false` thay vi 400).
_i_gate = _ep.find("TryClaimQuizRoundAsync(")
_i_hist = _ep.find("await db.AddHistoryAsync(")
_i_bad  = _ep.find('code = "bad-quiz"')
check("server: gianh suat TRUOC khi ghi nhat ky", 0 < _i_gate < _i_hist,
      "gate@%d hist@%d" % (_i_gate, _i_hist))
check("server: gianh suat SAU phep kiem du lieu vao", 0 < _i_bad < _i_gate,
      "bad-quiz@%d gate@%d" % (_i_bad, _i_gate))
# ⚠️ `/me/daily` phai doc CHINH bo dem. Dem lai nhat ky o do la hai nguon su that
#    cho mot con so, va ben lech se la ben noi voi tre con may luot.
check("server: /me/daily doc bo dem (GetQuizRoundsAsync), khong dem nhat ky",
      "GetQuizRoundsAsync(" in _ep)
# ⚠️ Bo do reset phai xoa CA bo dem. Thieu no thi 4 bo do can ban >5 luot/ngay
#    (test_wallet · test_report · test_quizlv · test_history) do BI AN.
_fb = rd("scratchpad/_fbtest.py")
check("reset_quiz_day xoa ca thuoc tinh `quizRounds`",
      "REMOVE quizRounds" in _fb)
# ⚠️ Va bo do phai CON muc do SONG SONG — ca tuan tu luon xanh ke ca voi ban da hong.
_tql = rd("scratchpad/test_quiz_limit.py")
check("test_quiz_limit con muc do SONG SONG",
      "ThreadPoolExecutor" in _tql and "song song" in _tql)
# --- So luot con lai phai ra duoc ngoai cho client doc ---
check("server: tra `quizRoundsLeft` ra client", "quizRoundsLeft" in _ep)
check("server: GET /me/daily cung tra so luot con lai",
      _ep.count("quizRoundsLeft") >= 3, "%d cho" % _ep.count("quizRoundsLeft"))

# --- Dem MOI luot, khong chi luot DAT ---
# ⚠️ `Daily.Build` dem `quizPassed` (chi luot DAT) vi do la VIEC HANG NGAY co thuong.
#    Han muc thi phai dem moi luot. Hai phep dem khac nhau, dung gop.
# Sau khi cong thanh bo dem (20/08/2026), cho bao dam khong con o QuizAccess ma o
# chinh loi goi gianh suat: no nam TRUOC moi phep tinh "dat hay khong".
_pre = _ep[max(0, _i_gate - 700):_i_gate] if _i_gate > 0 else "QuizPassed"
check("server: han muc dem MOI luot (gianh suat KHONG xet dat hay khong)",
      "QuizPassed" not in _pre and "QuizPassed" not in _qa,
      "co QuizPassed ngay truoc cho gianh suat")
check("server: 'ngay' lay tu Daily, khong khai lai mui gio",
      "TzOffsetHours" not in _qa and "AddHours" not in _qa)

print("\n=== [35] astroQ KHONG khai la ben DAY hoc ===")
# Chu du an chot 20/08/2026: *"astroQ ko day nhe, ko nen dung tu day vi chung ta ko
# phai to chuc giao duc duoc cap phep"*. Day la loi khai ve TU CACH, nen no phai bi
# chan o CA phan hien ra, CA du lieu co cau truc, va CA ban EN sinh ra.
#
# ⚠️ CHI cam khi CHU NGU la astroQ. Nhung cau nhu "MIT Media Lab day hoc sinh…" hay
#    "Thien van hoc day con nguoi…" la noi ve BEN KHAC va dung su that — cam bua o
#    day la sua 22 trang wiki + meta description dang bi Google cache vi mot cau
#    khong he khai gi ve astroQ.
_home = [("index.html", rd("index.html")),
         ("en/index.html", rd("en/index.html")),
         ("js/index.js", rd("js/index.js")),
         ("llms.txt", rd("llms.txt"))]
for _f, _t in _home:
    for _claim in ("astroQ.org dạy", "astroQ dạy",
                   "astroQ.org teach", "astroQ teaches"):
        check("%s KHONG khai '%s'" % (_f, _claim), _claim not in _t)
# ⚠️ `teaches` cua schema.org la loi khai MAY DOC DUOC va manh nhat trong so ca ba.
#    Thay bang `about` (chu de cua noi dung) — giu duoc tin hieu chu de ma khong khai
#    minh la ben day.
for _f, _t in _home[:2]:
    check("%s: JSON-LD dung `about` chu khong phai `teaches`" % _f,
          '"teaches"' not in _t and '"about"' in _t)
# ⚠️ Va generator phai sua theo, khong thi lan sinh sau ghi loi khai tro lai.
_gen = rd("scratchpad/gen_home_en.py")
check("gen_home_en.py: KHONG sinh lai `teaches`", '"teaches"' not in _gen)
check("gen_home_en.py: sinh `about`", '"about"' in _gen)
# Cau hoi FAQ phai khop 1-1 giua phan hien ra va JSON-LD (luat cu cua trang chu).
for _f, _lang in (("index.html", "có những chủ đề nào?"),
                  ("en/index.html", "cover?")):
    _t = rd(_f)
    check("%s: cau hoi chu de xuat hien dung 2 lan (hien ra + JSON-LD)" % _f,
          _t.count(_lang) == 2, "%d lan" % _t.count(_lang))

print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
sys.exit(0 if bad_n == 0 else 1)
