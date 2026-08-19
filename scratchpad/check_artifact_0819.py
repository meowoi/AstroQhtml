# -*- coding: utf-8 -*-
"""KIEM GOI TRUOC KHI DEPLOY — luot 19/08/2026 (vai (2) + no dong lai tu 18/08).

⚠️ BAI HOC 30/07/2026, DUNG HAI LAN: chuoi ky tu trong DLL .NET nam o **#US heap
   ma hoa UTF-16LE**, nen `grep`/`strings` kieu ASCII bao "THIEU" OAN. Ten phuong
   thuc / ten lop thi o **#Strings heap UTF-8** nen grep thuong thay duoc.
   => Moi dau hieu phai noi ro no thuoc loai nao va tim bang dung ma hoa do.

⚠️ PHAI CO CHUOI DOI CHUNG. Mot bo kiem chi tim dau hieu MOI se "dat" ca khi toi
   tro nham vao chinh goi cu (vi luc do... no khong dat — nhung neu regex sai thi
   khong phan biet duoc "khong co" voi "tim sai"). Chuoi doi chung CO o CA HAI goi
   chung minh cach tim la dung.

  python scratchpad/check_artifact_0819.py
"""
import io
import sys
import zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

NEW = r"C:\lambda-build\deploy0819.zip"
OLD = r"C:\lambda-build\rb0819\ROLLBACK-AstroqSV-20260819pre.zip"
DLL = "AstroqSV.Api.dll"

ok = bad = 0


def chk(cond, nhan, extra=""):
    global ok, bad
    if cond:
        ok += 1
        print("  [OK]   %s%s" % (nhan, ("  (%s)" % extra) if extra else ""))
    else:
        bad += 1
        print("  [HONG] %s%s" % (nhan, ("  (%s)" % extra) if extra else ""))


def dll(path):
    z = zipfile.ZipFile(path)
    return z.read(DLL), z.namelist()


new, nlist = dll(NEW)
old, olist = dll(OLD)


def has_u8(b, s):
    """Ten lop / ten phuong thuc / ten truong: #Strings heap, UTF-8."""
    return s.encode("utf-8") in b


def has_u16(b, s):
    """Chuoi literal trong ma nguon: #US heap, UTF-16LE."""
    return s.encode("utf-16-le") in b


print("\n=== [0] Hinh dang goi ===")
chk(len(nlist) == len(olist) == 39, "ca hai goi deu 39 file",
    "moi %d / cu %d" % (len(nlist), len(olist)))
chk(sorted(nlist) == sorted(olist), "danh sach file GIONG NHAU (khong them/bot phu thuoc)")

print("\n=== [1] Chuoi DOI CHUNG — phai co o CA HAI goi ===")
# Neu mot trong nhung cai nay thieu o goi cu thi cach tim cua toi sai, va moi ket
# luan ben duoi vo nghia.
for s, how in (("QuizPassed", has_u8), ("AwardQuiz", has_u8),
               ("BumpProgressAsync", has_u8), ("quizAnswered", has_u16),
               ("quizAccuracy", has_u16)):
    chk(how(new, s) and how(old, s), "doi chung `%s` co o ca hai goi" % s)

print("\n=== [2] VAI (2) — chi duoc co o goi MOI ===")
# Ten lop + ten phuong thuc: #Strings heap.
for s in ("Adapt", "QuizLevel", "MaxQuizLevel", "WarmUpAnswers", "Level3Ratio"):
    chk(has_u8(new, s), "goi moi CO `%s`" % s)
chk(not has_u8(old, "MaxQuizLevel"), "goi cu KHONG co `MaxQuizLevel` (dau hieu that su moi)")
chk(not has_u8(old, "WarmUpAnswers"), "goi cu KHONG co `WarmUpAnswers`")
# Ten truong cua object tra ve trong Snapshot() la chuoi literal -> #US heap.
chk(has_u16(new, "quizLv"), "goi moi CO truong `quizLv` (chuoi, #US heap UTF-16LE)")
chk(not has_u16(old, "quizLv"), "goi cu KHONG co truong `quizLv`")

print("\n=== [3] NO TU 18/08 — goi nay MANG THEO, phai biet minh dang chuyen gi ===")
# ⚠️ Luot 18/08 sua `Campaign.cs`/`Insights.cs`/`DynamoContext.cs` de luu nhan
#    NGUON (`src`) cua nguoi ghi danh, nhung KHONG deploy duoc. Goi hom nay mang
#    theo ca thay do — day la dieu TOT (moi ngay tri hoan la mot ngay du lieu
#    nguon khong lay lai duoc), nhung phai NOI RA chu khong de no di lau.
_pending = []
# ⚠️ TEN THAT, khong phai `utm*`: phia C# goi la `Campaign.Clean` va luu vao
#    truong DynamoDB ten `src`. Ban do dau tien cua toi tim "utmSource" nen bao
#    "khong tim thay o ca hai goi" — do la TOI DO SAI TEN, khong phai goi thieu.
for s, how, nhan in (("Campaign", has_u8, "lop `Campaign` (loc nhan nguon)"),
                     ("MaxParts", has_u8, "tran so phan cua nhan nguon"),
                     ("srcIn", has_u8, "bien `srcIn` o duong dang ky")):
    if how(new, s) and not how(old, s):
        _pending.append(nhan)
        print("  [MOI]  goi nay mang theo %s (no dong lai tu 18/08)" % nhan)
    elif how(new, s) and how(old, s):
        print("  [ ]    %s da co tu truoc" % nhan)
    else:
        print("  [ ]    khong tim thay %s o ca hai goi" % nhan)

print("\n=== [4] KHONG mat thu gi dang co ===")
# Moi thu quan trong cua ban dang chay phai con nguyen o goi moi.
for s, how in (("SendWaitlistWelcomeAsync", has_u8), ("PutWaitlistAsync", has_u8),
               ("XpLadder", has_u8), ("DeskOf", has_u8),
               ("/waitlist", has_u16), ("/daily", has_u16)):
    chk(how(new, s), "goi moi VAN co `%s`" % s)

print("\n===== %d dat / %d hong =====" % (ok, bad))
if _pending:
    print("⚠️ Goi nay KHONG chi mang thay doi hom nay: %s" % ", ".join(_pending))
sys.exit(1 if bad else 0)
