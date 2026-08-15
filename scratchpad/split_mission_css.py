# -*- coding: utf-8 -*-
"""Tach `css/mission-earth.css` thanh BA file theo VAI TRO cua tung khoi.

    css/mission-stage.css  vo dung chung cho MOI nhiem vu (header, bang muc tieu,
                           box thoai, the noi dung, khung .me-board, keo-tha,
                           bang cau do, man tong ket, hop hoi, toast, man cho)
    css/earth2d.css        CANH 2D (`js/earth2d.js`) — dung chung cho moi nhiem vu
                           dien ra tren ban do Trai Dat
    css/mission-earth.css  chi con cac BANG rieng cua Nhiem vu 01

⚠️ PHAN LOAI THEO SELECTOR, KHONG CAT THEO SO DONG. Cat theo so dong la thu se
   sai ngay lan sua tiep theo; phan loai theo selector thi chay lai luc nao cung
   cho cung ket qua.

⚠️ `@media` PHAI DUOC CHIA NHO: mot khoi media co the chua ca rule chung lan rule
   rieng (vi du khoi `pointer:coarse` vua chinh `.me-top .back` vua chinh
   `.me-era-node`). Giu nguyen ca khoi la mot trong hai file nhan rule khong phai
   cua no. Script tach tung rule con roi phat lai toi da 3 khoi media.

Chay:  python scratchpad/split_mission_css.py            (xem truoc)
       python scratchpad/split_mission_css.py --write    (ghi that)
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "css", "mission-earth.css")

# Selector cua NHIEM VU 01 — cac bang noi dung rieng cua no.
MISSION = (
    "me-time", "me-era-node", "era-fig", "era-illus", "era-txt", "era-live",
    "era-ghost", "era-act", "era-body", "me-era", "me-energy", "me-smog",
    "me-eco", "me-bucket", "me-chip", "me-xsec", "xsec-", "me-core",
    "me-fileline", "era-magma", "era-ocean", "era-life", "era-dino",
    "e2-stack", "mePuff", "meSmog",
)
# Selector cua CANH 2D.
SCENE = ("e2", "stage")


def kind(sel):
    """'mission' | 'scene' | 'stage' cho mot selector."""
    s = sel.strip()
    for w in MISSION:
        if w in s:
            return "mission"
    # `.e2`, `.e2-*`, `#stage` — nhung `#stage.era-*` da bi bat o tren
    for part in re.split(r"\s*,\s*", s):
        p = part.strip()
        if p.startswith(".e2") or p.startswith("#stage"):
            return "scene"
    return "stage"


def split_top_level(css):
    """Cat CSS thanh danh sach (kieu, selector, text-day-du).

    kieu: 'rule' | 'at' (media/supports co khoi con) | 'raw' (comment, @keyframes...)
    """
    out, i, n = [], 0, len(css)
    buf = []
    while i < n:
        ch = css[i]
        # comment
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            j = n if j < 0 else j + 2
            buf.append(css[i:j])
            i = j
            continue
        if ch == "{":
            sel = "".join(buf)
            depth, j = 1, i + 1
            while j < n and depth:
                if css.startswith("/*", j):
                    k = css.find("*/", j + 2)
                    j = n if k < 0 else k + 2
                    continue
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            body = css[i:j]
            out.append((sel, body))
            buf = []
            i = j
            continue
        buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        out.append((tail, ""))
    return out


def lead_comment(sel):
    """Tach phan comment/khoang trang dan truoc khoi selector that."""
    m = re.match(r"^(?P<lead>(?:\s|/\*.*?\*/)*)(?P<sel>.*)$", sel, re.S)
    return m.group("lead"), m.group("sel")


def main():
    css = io.open(SRC, encoding="utf-8").read()
    parts = split_top_level(css)

    bucket = {"stage": [], "scene": [], "mission": []}

    for sel, body in parts:
        lead, real = lead_comment(sel)
        real_s = real.strip()

        # Khoi khong co than (comment cuoi file...)
        if not body:
            if real_s:
                bucket["stage"].append(sel)
            continue

        # @media / @supports: chia nho tung rule con
        if real_s.startswith("@media") or real_s.startswith("@supports"):
            inner = body[1:-1]
            sub = split_top_level(inner)
            groups = {"stage": [], "scene": [], "mission": []}
            for s2, b2 in sub:
                l2, r2 = lead_comment(s2)
                if not b2:
                    continue
                groups[kind(r2)].append((l2 + r2).rstrip() + b2)
            for k, items in groups.items():
                if items:
                    head = (lead if k == "stage" else "") + real_s
                    bucket[k].append(head + " {\n" + "\n".join(items) + "\n}")
            continue

        # @keyframes / :root / rule thuong
        if real_s.startswith("@keyframes"):
            nm = real_s.split()[1] if len(real_s.split()) > 1 else ""
            k = kind(nm)
        elif real_s.startswith(":root"):
            k = "stage"
        else:
            k = kind(real_s)
        bucket[k].append((lead + real).rstrip() + body)

    for k in bucket:
        print("%-8s %3d khoi" % (k, len(bucket[k])))

    if "--write" not in sys.argv:
        print("\n(xem truoc — them --write de ghi)")
        for k in ("scene", "mission"):
            print("\n--- %s ---" % k)
            for b in bucket[k][:60]:
                print("   ", b.split("{")[0].strip().replace("\n", " ")[:96])
        return

    def write(path, header, blocks):
        with io.open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="\n") as f:
            f.write(header.rstrip() + "\n\n")
            f.write("\n\n".join(b.strip() for b in blocks) + "\n")
        print("da ghi", path)

    write("css/mission-stage.css", HEAD_STAGE, bucket["stage"])
    write("css/earth2d.css", HEAD_SCENE, bucket["scene"])
    write("css/mission-earth.css", HEAD_MISSION, bucket["mission"])


HEAD_STAGE = u"""/* ============================================================
   css/mission-stage.css — VO MAN CHOI, dung chung cho MOI nhiem vu.

   Nap giua `css/mascot.css` va `css/<nhiem-vu>.css`:
     common.css -> mascot.css -> pick-place.css -> brag.css
     -> mission-stage.css -> earth2d.css -> mission-<ten>.css

   Markup tuong ung do `js/mission-stage.js` dung. Trang nhiem vu chi con khai
   cac `.me-board` mang noi dung buoc cua rieng no.

   ⚠️ TACH RA 15/08/2026 khi Trai Dat co nhiem vu thu hai. Truoc do toan bo khoi
      nay nam trong `css/mission-earth.css`, nen nhiem vu thu hai chi con hai
      duong: chep ~430 dong CSS, hoac tach. Quy tac 2 muc 6 cua CLAUDE.md:
      *thu dung chung thi tach ra dung lai, khong copy-paste giua cac trang.*

   ⚠️ BIEN MAU (`:root`) O DAY LA CUA CA HAI NHIEM VU. Doi mot bien la doi ca
      hai man choi — do la y muon: chung phai trong nhu MOT con tau.
   ============================================================ */"""

HEAD_SCENE = u"""/* ============================================================
   css/earth2d.css — CANH BAN DO TRAI DAT 2D (`js/earth2d.js`).

   Tach khoi `css/mission-earth.css` ngay 15/08/2026: canh nay khong thuoc rieng
   Nhiem vu 01. Nhiem vu 02 ("Mat Than Tren Quy Dao") dien ra tren dung tam ban
   do do, va moi nhiem vu Trai Dat sau nay cung vay.

   ⚠️ File JS va file CSS cua canh phai di CUNG NHAU. Nap `js/earth2d.js` ma
      quen file nay thi canh van dung duoc nhung khong mot marker nao nhin thay
      — mot loi IM LANG, khong ngoai le, khong canh bao.
   ============================================================ */"""

HEAD_MISSION = u"""/* ============================================================
   css/mission-earth.css — PHAN RIENG cua NHIEM VU 01 "Hanh Tinh Xanh".

   Vo dung chung o `css/mission-stage.css`; canh ban do o `css/earth2d.css`.
   Con lai o day dung 5 bang noi dung: dong thoi gian · nang luong sach ·
   Eco-Hero · lat cat Trai Dat · Ho So Trai Dat, cong hai lop phu canh
   (`.me-era` doi tong theo moc thoi gian, `.me-smog` khoi).
   ============================================================ */"""


if __name__ == "__main__":
    main()
