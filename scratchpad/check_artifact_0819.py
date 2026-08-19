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

NEW = r"C:\lambda-build\deploy0819b.zip"   # luot 2: qua danh sach cho
OLD = r"C:\lambda-build\deploy0819.zip"     # goi DANG CHAY (luot 1: vai (2))
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

print("\n=== [2] VAI (2) — nay la DOI CHUNG: phai co o CA HAI goi ===")
# ⚠️ Luot deploy dau (sang 19/08) da mang vai (2) len AWS, nen tu luot NAY tro di
#    `Adapt`/`quizLv` khong con la "dau hieu moi" — chung thanh doi chung chung minh
#    goi moi KHONG lam mat viec vua deploy.
for s in ("Adapt", "QuizLevel", "MaxQuizLevel", "WarmUpAnswers", "Level3Ratio"):
    chk(has_u8(new, s) and has_u8(old, s), "vai (2): `%s` con o ca hai goi" % s)
chk(has_u16(new, "quizLv") and has_u16(old, "quizLv"),
    "vai (2): truong `quizLv` con o ca hai goi")

print("\n=== [2b] QUA DANH SACH CHO — chi duoc co o goi MOI ===")
for s in ("WaitlistBonus", "ClaimWaitlistBonusAsync", "bonusMeteors"):
    chk(has_u8(new, s), "goi moi CO `%s`" % s)
    chk(not has_u8(old, s), "goi dang chay KHONG co `%s` (dau hieu that su moi)" % s)
# Ten thuoc tinh ghi vao DynamoDB la chuoi literal -> #US heap UTF-16LE.
for s in ("bonusAt", "bonusAmount"):
    chk(has_u16(new, s), "goi moi CO thuoc tinh `%s`" % s)
    chk(not has_u16(old, s), "goi dang chay KHONG co `%s`" % s)

# ⚠️ MUC [3] DA BO 19/08/2026. No tung do "no nhan nguon `src` tu 18/08 co trong goi
#    khong", nhung da xac minh xong: `Campaign`/`MaxParts` co san trong ban dang chay,
#    va `test_utm` 28/0 tren ban that. Giu lai mot muc luon in "da co tu truoc" chi lam
#    ket qua dai ra ma khong bao ve dieu gi.
_pending = []

print("\n=== [4] KHONG mat thu gi dang co ===")
# Moi thu quan trong cua ban dang chay phai con nguyen o goi moi.
for s, how in (("SendWaitlistWelcomeAsync", has_u8), ("PutWaitlistAsync", has_u8),
               ("XpLadder", has_u8), ("DeskOf", has_u8),
               ("/waitlist", has_u16), ("/daily", has_u16),
               ("GetWaitlistAsync", has_u8), ("CreditWalletAsync", has_u8)):
    chk(how(new, s), "goi moi VAN co `%s`" % s)

print("\n===== %d dat / %d hong =====" % (ok, bad))
if _pending:
    print("⚠️ Goi nay KHONG chi mang thay doi hom nay: %s" % ", ".join(_pending))
sys.exit(1 if bad else 0)
