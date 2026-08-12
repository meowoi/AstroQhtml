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
             "mission-tree.html"):
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
EXTRA_SRC = {"mission-earth.html": ["js/mission-engine.js"]}
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
_me_src = me + rd("js/mission-engine.js")
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
check("man tong ket co khoi 'viec tiep theo' dan di duoc THAT",
      "win-missions" in _me_code and "missions.html" in _me_code)
check("nut viec tiep theo KHONG bi disabled (missions.html co that)",
      not _re.search(r"win-missions'\)\.disabled\s*=\s*true", _me_code)
      and 'id="win-missions"' in me and 'id="win-missions" disabled' not in me)
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
_earth = mi_cs.split('new("earth", "earth",', 1)[1].split("], DoneMeteors", 1)[0]
sv_steps = _re.findall(r'new\("([a-z]+)",\s*\d+,\s*\d+,\s*(null|"[a-z0-9,-]+")\)', _earth)
sv_ids = [s[0] for s in sv_steps]
_cl = _re.search(r"const STEP_IDS = \[([^\]]*)\]", me)
cl_ids = _re.findall(r"'([a-z]+)'", _cl.group(1)) if _cl else []
check("STEP_IDS cua trang KHOP dung thu tu voi Missions.cs",
      sv_ids == cl_ids, f"server={sv_ids} client={cl_ids}")
# ⚠️ KHONG GAN CUNG SO BUOC. Truoc 02/08/2026 dong nay ghi `== 8`, va khi bo buoc
#    `rotation` (docs/decisions/005) thi no bao hong DUNG LUC code lam dung — cung
#    mot ho voi loi "gan cung con so ma noi khac moi la nguon su that" du an da gap
#    nhieu lan (14 icon · 14 thuat ngu · 25 cau · 20 mau vat · 5 buoc).
#    Nguon su that la `Missions.cs`. O day chi doi: doc duoc, va khop client.
check("doc duoc danh sach buoc tu Missions.cs", len(sv_ids) >= 5, str(len(sv_ids)))
check("KHONG con buoc `rotation` (bo 02/08/2026, docs/decisions/005)",
      "rotation" not in sv_ids, str(sv_ids))
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
# ⚠️ THEM 02/08/2026 — LOI THAT DA XAY RA. Bo buoc `rotation` lam mat mot entry
#    codex, nhung `codexTotal` o mission-earth.html van la 9, nen man tong ket ghi
#    **"8/9 mau du lieu"**: noi voi tre rang no bo sot mot mau KHONG TON TAI, o dung
#    man khen thuong. `smoke_mission_earth` bat duoc (no choi that toi man tong ket),
#    con muc [3c] thi khong — vi truoc do khong co phep kiem nao noi hai con so nay.
_ct = _re.search(r"codexTotal:\s*(\d+)", me)
check("mission-earth.html: `codexTotal` du phong khop so entry earth_codex.json",
      bool(_ct) and int(_ct.group(1)) == len(cx_ids),
      f'codexTotal={_ct.group(1) if _ct else "?"} entries={len(cx_ids)}')
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
_me3g = strip_comments(me)
_css3g = strip_comments(rd("css/mission-earth.css"))

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
_sc = _me3g.split("function showCard(", 1)[1].split(chr(10) + "function ", 1)[0]
check("`showCard` goi `liftCard()` TRUOC khi hien the",
      "liftCard();" in _sc and
      _sc.index("liftCard();") < _sc.index("classList.add('show')"))

print("\n=== [3e] Nhiem Vu 01 sau `005`: 0 vung toi · 0 qua cau · noi dung co nguon ===")
# Chot 02/08/2026, `docs/decisions/005`. Muc nay canh nhung RANG BUOC "tu nay" cua no —
# thu ma doc code khong thay sai, chi thay sai khi chieu lai quyet dinh.
_me_code = strip_comments(me)          # bo ghi chu: chinh chu thich GIAI THICH vi sao
_me_css_raw = strip_comments(rd("css/mission-earth.css"))

# --- (1) KHONG con vung toi nao tren ban do phang ---
# ⚠️ Chu du an choi that roi BAC bang anh chup: gradient `.e2-terminator` trong nhu mot
#    buc tuong den. Bai hoc ngay/dem da chuyen sang qua cau 3D o explorer.html.
check("KHONG con `.e2-terminator` trong CSS (bo han, 005 muc 2)",
      "e2-terminator" not in _me_css_raw)
check("KHONG con `.e2-terminator` trong mission-earth.html",
      "e2-terminator" not in _me_code)
check("KHONG con `.e2-view::after` (gradient vung toi mac dinh)",
      "e2-view::after" not in _me_css_raw)
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
allowed = {"dashboard.html", "achievements.html", "profile.html", "landing-app.html",
           "specimen-vault.html", "missions.html", "codex.html", "parent.html",
           "admin-report.html", "checkout.html", "mission-tree.html"}
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
_soon_cards = dash_nc.count(" soon\">")
check("dashboard.html: 0 card 'soon' (moi khu deu co trang that)",
      _soon_cards == 0, "con %d card khoa" % _soon_cards)
# Neu ngay nao co card khoa tro lai thi ba luat cu song lai NGUYEN VEN:
if _soon_cards:
    check("dashboard.html: nut card 'soon' BAM DUOC (khong disabled)",
          "disabled" not in dash_nc,
          "con `disabled`" if "disabled" in dash_nc else "ok")
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
check("dashboard.html: MOD-05 dan sang lab.html",
      'location.href="lab.html"' in dash_nc.replace(" ", ""))
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

# --- (a) id honeypot phai khop hai ben, va JS phai doc an toan ---
_hp_ids = set(re.findall(r'id="(wl-[a-z-]+)"[^>]*class="hp"', _wl_html))
_hp_ids |= set(re.findall(r'class="hp"[^>]*id="(wl-[a-z-]+)"', _wl_html))
check("markup co dung 1 o bay bot", len(_hp_ids) == 1, _hp_ids)
_hp_id = next(iter(_hp_ids), "")
check("JS doc dung id bay bot cua markup",
      bool(_hp_id) and f'$("{_hp_id}")' in _wl_code, _hp_id)
check("JS KHONG goi thang .value tren ket qua $() cua bay bot "
      "(null la giet ca ham gui form)",
      re.search(r'\$\("wl-[a-z-]+"\)\.value', _wl_code) is None,
      re.findall(r'\$\("wl-[a-z-]+"\)\.value', _wl_code))
# moi id ma JS tra cuu deu phai co that trong markup
_page_ids = ids_in(_wl_html)
_miss = sorted({i for i in re.findall(r'\$\("([a-z0-9-]+)"\)', _wl_code)} - _page_ids)
check("moi $(\"id\") cua js/index.js deu ton tai trong index.html", not _miss, _miss)

# --- (b) khong con dau vet dich vu form ben thu ba ---
for _rel in ("index.html", "js/index.js", "css/index.css"):
    check(f"{_rel} khong con dau vet dich vu form ben thu ba",
          "formspree" not in rd(_rel).lower())
check("form KHONG con action tro ra ngoai",
      re.search(r'<form[^>]*id="wl-form"[^>]*action=', _wl_html) is None)
check("khong con truong an kieu _subject/_gotcha cua dich vu cu",
      not re.search(r'name="_(subject|gotcha|replyto|next)"', _wl_html))

# --- day noi client ---
check("client goi POST /waitlist", '"/waitlist"' in _wl_code)
# ⚠️ Doi 07/08/2026: truoc day phep kiem ghim nguyen van `import("./api.js")`.
#    Chuoi do khong con dung ke tu khi trang chu tach lam HAI URL (`/` va `/en/`):
#    day la script CO DIEN nen `import()` giai theo URL cua TAI LIEU, tuc
#    `./api.js` se thanh `/en/api.js` va 404 — form waitlist chet cam, dung loai
#    loi da giet chinh form nay suot 6 ngay (02/08/2026). Nay duong dan suy tu
#    `document.currentScript` (JS_DIR).
#    Phep kiem gio hoi DIEU CAN BIET, khong ghim mot chuoi: (a) van la import
#    DONG, (b) duong dan KHONG con la hang chuoi cung o goc.
check("client nap js/api.js bang import DONG (trang chu dang toi uu SEO)",
      re.search(r'import\(\s*JS_DIR\s*\+\s*"api\.js"\s*\)', _wl_code) is not None)
check("duong dan api.js suy tu currentScript, KHONG phai hang cung",
      "document.currentScript" in _wl_code and 'import("./api.js")' not in _wl_code)
check("index.html KHONG dat the <script> cho api.js",
      "js/api.js" not in _wl_html)
check("payload gui du email + lang + bay bot",
      all(k in _wl_code for k in ("email:", "lang:", "hp:")))

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

# --- SES hong thi KHONG hua "kiem tra hom thu" ---
_vi, _en = i18n_dicts(_wl_js)          # tra ve TAP KHOA, khong phai gia tri
check("co khoa done_body_nomail o CA vi va en",
      "done_body_nomail" in (_vi or set()) and "done_body_nomail" in (_en or set()))
_nomail = re.findall(r"done_body_nomail\s*:\s*(['\"])(.*?)\1", _wl_code, re.S)
check("doc duoc ca hai ban cua done_body_nomail", len(_nomail) == 2, len(_nomail))
check("cau 'chua gui duoc thu' KHONG bao kiem tra hom thu",
      all("Kiểm tra hòm thư" not in v and "Check your inbox" not in v for _q, v in _nomail),
      [v[:40] for _q, v in _nomail])
check("cau do van giu o dien ten email", all('id="wl-done-mail"' in v for _q, v in _nomail))
check("client chon cau theo mailSent cua server", "mailSent" in _wl_code)

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

# --- (f3) BANG PHI HANH GIA o dashboard: 3 duong vao, khong bia so ---
_db_html = rd("dashboard.html")
_db_code = _no_comments(inline_js(_db_html))
_db_css = rd("css/dashboard.css")
check("dashboard co bang phi hanh gia (.ptiles)", 'class="ptiles"' in _db_html)
for _href, _cls in (("profile.html", "pt-profile"), ("achievements.html", "pt-awards"),
                    ("specimen-vault.html", "pt-vault")):
    check(f"co o dan sang {_href}",
          bool(re.search(r'class="ptile %s"[^>]*href="%s"' % (_cls, _href), _db_html)
               or re.search(r'class="ptile %s" href="%s"' % (_cls, _href), _db_html)))
check("2 nut chu xep doc cua ban cu da bo han",
      "sh-link" not in _no_comments(_db_html) and "sh-link" not in _no_comments(_db_css))
# ⚠️ Hang FULL-WIDTH, khong nam trong cot phai: do duoc trong cot phai moi o chi
#    124px va bi cat chu ca o ban VI lan EN.
check("bang phi hanh gia la hang FULL-WIDTH cua panel",
      bool(re.search(r"\.ptiles\{[^}]*grid-column:\s*1\s*/\s*-1", _db_css)))
# ⚠️ ĐỪNG dùng `[^:]*` giữa `?` và `:` — hai nhánh nay co ternary LONG BEN TRONG
#    (`window.AstroQRanks ? ... : ""`) nen `[^:]*` dung som va phep kiem bao hong oan.
#    Dem so nhanh else tra ve dau "—" trong chinh than renderStats.
_rs = _db_code.split("function renderStats", 1)[-1].split("\n  function ", 1)[0]
check("KHONG bia so khi chua doc duoc server (dung dau '—')",
      _rs.count(': "—"') >= 2 and "known" in _rs, _rs.count(': "—"'))
# ⚠️ So mau vat nam o GET /me/specimens ma dashboard khong goi -> o do KHONG co so,
#    va tuyet doi khong go cung tong so mau (server moi la nguon su that).
check("o Mau vat KHONG go cung tong so mau",
      not re.search(r"/2[01]\b", _db_code.split("ptiles")[-1][:2000] if "ptiles" in _db_code
                    else ""))
check("dashboard KHONG goi them route chi de lay so mau vat",
      "getSpecimens" not in _db_code and "/me/specimens" not in _db_code)
check("ten bac o o Ho so dung ranks.js (short), khong go tay",
      "AstroQRanks.short(" in _db_code)
for _k in ("pt_profile", "pt_awards", "pt_vault", "pt_vault_sub", "pt_badges_unit"):
    _dvi, _den = i18n_dicts(inline_js(_db_html))
    check(f"khoa i18n '{_k}' co o CA vi va en",
          _k in (_dvi or set()) and _k in (_den or set()))
check("vung cham >= 48px tren thiet bi cam ung",
      bool(re.search(r"\.ptile\{min-height:4[89]px", _db_css)))
check("man hep thi 3 o xep DOC (khong bop con ~95px)",
      bool(re.search(r"max-width:520px\)\s*\{\s*\.ptiles\{grid-template-columns:1fr", _db_css)))
# data-tour phai TON TAI dung mot cho — thieu la Comet chieu sang vao khoang khong
# ⚠️ Dem tren ban DA BOC COMMENT: chinh chu thich giai thich viec doi data-tour
#    cung chua chuoi do -> dem tren van ban tho la bao hong oan (loi "dem ca chu
#    trong ghi chu cua chinh minh", lan thu 14).
#    Dung `strip_comments()` (bo CA comment HTML) chu khong `_no_comments()` — ham
#    kia chi bo comment JS nen `<!-- ... data-tour="awards" ... -->` van con.
_db_nc = strip_comments(_db_html)
check("data-tour='awards' ton tai dung MOT lan",
      _db_nc.count('data-tour="awards"') == 1, _db_nc.count('data-tour="awards"'))
check("data-tour='awards' nam tren o Thanh tich",
      bool(re.search(r'class="ptile pt-awards"[^>]*data-tour="awards"', _db_html)))

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

# ── `STEP_IDS` cua trang choi == danh muc ──
_me_src = rd("mission-earth.html")
_m_step_ids = re.search(r"const STEP_IDS = \[([^\]]+)\]", _me_src)
_me_steps = re.findall(r"'([a-z0-9-]+)'", _m_step_ids.group(1)) if _m_step_ids else []
check("[20] STEP_IDS cua mission-earth == danh muc chang cua 'earth'",
      _me_steps == _cat_steps("earth"),
      f"STEP_IDS={_me_steps} catalog={_cat_steps('earth')}")

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
_me_js = strip_comments(inline_js(_me_src))
check("[20] mission-earth doc `?step=` va mo dung chang do",
      "q.get('step')" in _me_js and "RUN.openAt(" in _me_js)
check("[20] khai moc onStepDone cho trinh dieu phoi",
      "onStepDone: afterStep" in _me_js)
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
check("[20] duong ve cua trang choi la cay chang",
      "function treeUrl()" in _me_js and "mission-tree.html?m=earth" in _me_js)
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
SIC_IDLE = {"globe", "map", "lock", "wave", "leaf", "rock"}
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

print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
sys.exit(0 if bad_n == 0 else 1)
