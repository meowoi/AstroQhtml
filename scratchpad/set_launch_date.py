"""Doi NGAY RA MAT cua trang chu — sua MOI CHO cung mot luot.

    python scratchpad/set_launch_date.py 2026-08-20
    python scratchpad/set_launch_date.py 2026-08-20 --dry      (chi xem, khong ghi)

⚠️⚠️ VI SAO PHAI CO SCRIPT NAY, dung go tay: ngay ra mat nam o **15 CHO trong 5 FILE**,
     trong do co MOT chO o BACKEND (`AstroqSV/.../WaitlistEndpoints.cs`, in nguyen van vao
     thu chao mung — client khong voi tOi duoc). Go tay thi som muon lech, ma JSON-LD lech
     voi phan hien thi la Google coi nhu du lieu sai, con thu SES lech la noi sai voi khach
     da dang ky. Cung ly le voi `stamp_version.py`.

     CLAUDE.md tung ghi "7 cho" roi "17 cho" — dem lai 12/08/2026 ra **9**. Con so trong tai lieu
     da duoc sua theo.

BA DANG VIET cua cung mot ngay, moi dang mot muc dich:
     09/08/2026     ban VI hien ra + LaunchDateVi (thu SES tieng Viet)
     2026-08-09     LAUNCH_AT (dong ho dem nguoc) + datePublished cua JSON-LD
     9 August 2026  ban EN hien ra + LaunchDateEn

⚠️ DANG THU TU `9 Aug 2026` DA THANH MO COI tu 18/08/2026: no chi dung o <title>
   ban EN, ma tieu de da bo ngay di co chu dich (bo mat bi bat thu ba CACHE khong
   duoc mang loi hua se het han — xem scratchpad/set_launch_copy.py). `forms()` van
   tra ve `en_short` nhung KHONG job nao dung; giu lai de khoi pha ham dung chung,
   va de neu co cho moi can dang do thi da co san.

⚠️ SAU KHI CHAY, BAT BUOC hai buoc:
     1. python scratchpad/gen_home_en.py     (sinh lai en/index.html — DUNG sua tay)
     2. python scratchpad/check_pages.py     (muc [16] doi chieu backend <-> LAUNCH_AT)
   Va nho DEPLOY backend, khong thi thu chao mung van in ngay CU.

Script dat MOC SO LUONG cho tung phep thay: lech mot cai la DUNG va khong ghi file nao.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SV = os.path.join(os.path.dirname(ROOT), "AstroqSV", "src", "AstroqSV.Api")

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def forms(iso):
    """iso 'YYYY-MM-DD' -> bon dang viet dung trong du an."""
    y, mo, d = iso.split("-")
    mon = MONTHS[int(mo) - 1]
    return {
        "vi": "%s/%s/%s" % (d, mo, y),                 # 20/08/2026
        "iso": iso,                                     # 2026-08-20
        "en_long": "%d %s %s" % (int(d), mon, y),       # 20 August 2026
        "en_short": "%d %s %s" % (int(d), mon[:3], y),  # 20 Aug 2026
    }


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def current_iso():
    """Ngay dang chay, doc tu LAUNCH_AT — nguon su that duy nhat."""
    js = read(os.path.join(ROOT, "js", "index.js"))
    m = re.search(r'LAUNCH_AT\s*=\s*new Date\("(\d{4}-\d{2}-\d{2})', js)
    if not m:
        print("[HONG] khong doc duoc LAUNCH_AT o js/index.js")
        sys.exit(1)
    return m.group(1)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    if len(args) != 1 or not re.match(r"^\d{4}-\d{2}-\d{2}$", args[0]):
        print(__doc__)
        sys.exit(2)
    new_iso = args[0]
    old_iso = current_iso()
    if old_iso == new_iso:
        print("[BO QUA] ngay ra mat da la %s roi." % new_iso)
        return
    o, n = forms(old_iso), forms(new_iso)
    print("  %s  ->  %s\n" % (old_iso, new_iso))

    # (duong dan, [(cu, moi, so lan PHAI khop, muc dich)])
    jobs = [
        (os.path.join(ROOT, "index.html"), [
            (o["vi"], n["vi"], 2, "FAQ JSON-LD . a5"),
            (o["iso"], n["iso"], 1, "datePublished cua JSON-LD"),
        ]),
        (os.path.join(ROOT, "js", "index.js"), [
            ('new Date("%sT00:00:00+07:00")' % o["iso"],
             'new Date("%sT00:00:00+07:00")' % n["iso"], 1, "LAUNCH_AT (dong ho dem nguoc)"),
            (o["vi"], n["vi"], 1, "tu dien vi: a5"),
            (o["en_long"], n["en_long"], 1, "tu dien en: a5"),
        ]),
        (os.path.join(HERE, "gen_home_en.py"), [
            (o["iso"], n["iso"], 1, "EN_APP_JSONLD datePublished"),
        ]),
        (os.path.join(SV, "Endpoints", "WaitlistEndpoints.cs"), [
            (o["vi"], n["vi"], 1, "LaunchDateVi (thu SES tieng Viet)"),
            (o["en_long"], n["en_long"], 1, "LaunchDateEn (thu SES tieng Anh)"),
        ]),
    ]

    bad, plans, total = [], [], 0
    for path, subs in jobs:
        if not os.path.isfile(path):
            bad.append("KHONG THAY FILE: %s" % path)
            continue
        src = read(path)
        out = src
        for old, new, want, why in subs:
            got = out.count(old)
            if got != want:
                bad.append("%s :: %r khop %d lan, doi %d  (%s)"
                           % (os.path.basename(path), old, got, want, why))
                continue
            out = out.replace(old, new)
            total += want
            print("    [%2d] %-26s %s" % (want, os.path.basename(path), why))
        plans.append((path, src, out))

    if bad:
        print("\nDUNG - khong ghi file nao:")
        for b in bad:
            print("  [HONG] " + b)
        sys.exit(1)

    print("\n  tong: %d cho" % total)
    if dry:
        print("  --dry: khong ghi gi.")
        return
    for path, src, out in plans:
        if src == out:
            continue
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(out)
        print("  [OK] %s" % path)

    print("\nBAT BUOC lam tiep:")
    print("  1. python scratchpad/gen_home_en.py     # sinh lai en/index.html")
    print("  2. python scratchpad/check_pages.py     # muc [16] doi chieu backend")
    print("  3. deploy backend, khong thi thu SES van in ngay CU")


if __name__ == "__main__":
    main()
