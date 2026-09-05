# -*- coding: utf-8 -*-
"""Kiem GOI SAP DEPLOY, va SO voi goi DANG CHAY.

⚠️ `aws lambda update-function-code` KHONG tu phat hien goi sai -- 29/07/2026 da
   mot lan deploy dung mot thu muc RONG. Nen phai dem file + tim dau hieu TRUOC.

⚠️⚠️ PHAI CO CHUOI DOI CHUNG. Mot phep tim luon bao "co" trong ca hai goi thi
   khong phan biet duoc goi moi voi goi cu -- doi chung la thu cho biet phep tim
   dang chay dung.

⚠️ Chuoi literal cua .NET nam o #US heap ma hoa UTF-16LE; ten method/field o
   #Strings heap UTF-8. Tim nham heap la bao "THIEU" oan (bai hoc 02/08/2026).
"""
import io
import os
import sys
import zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

NEW_DIR = r"C:\lambda-build\publish-0905"
OLD_ZIP = r"C:\lambda-build\rb0905\ROLLBACK-AstroqSV-20260905.zip"
DLL = "AstroqSV.Api.dll"

n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


files = os.listdir(NEW_DIR)
print("[1] GOI MOI")
chk("du 39 file nhu goi dang chay", len(files) == 39, "%d file" % len(files))
chk("co %s" % DLL, DLL in files)
chk("co AstroqSV.Api.deps.json", "AstroqSV.Api.deps.json" in files)

dep = io.open(os.path.join(NEW_DIR, "AstroqSV.Api.deps.json"), encoding="utf-8").read()
chk("deps.json khai linux-arm64 (Lambda chay Graviton)", "linux-arm64" in dep)

new = io.open(os.path.join(NEW_DIR, DLL), "rb").read()
old = zipfile.ZipFile(OLD_ZIP).read(DLL)
print("      dll moi %d byte | dll cu %d byte" % (len(new), len(old)))


def has(blob, s):
    """Tim ca hai heap: #US (UTF-16LE) va #Strings (UTF-8)."""
    return (s.encode("utf-16-le") in blob) or (s.encode("utf-8") in blob)


# Dau hieu cua ba viec -- phai CO o goi moi, KHONG o goi cu.
MOI = [
    # ⚠ KHONG dung "/claim" tran: no la CHUOI CON cua URI schema claim identity
    #    (.../identity/claims/emailaddress) nen goi CU cung co -> khong phan biet duoc.
    ("Đã lưu tiến độ của con", "viec 3: loi nhan cua nut Luu tien do"),
    ("CreateCustomTokenAsync",  "viec 3: duc custom token"),
    ("customToken",             "viec 3: truong tra ve cho client"),
    ("CreateAccountAsync",      "viec 3: ham tao tai khoan dung chung"),
    ("ImportUserAsync",         "viec 2: tao tai khoan chua xac minh"),
    ("MarkEmailVerifiedAsync",  "viec 2: bat co luc bam link"),
    ("RequireProfile",          "viec 2: cong /me doi CO HO SO"),
    ("email-unverified",        "viec 2: ma loi cho cong muon"),
    ("engaged",                 "viec 4: beacon 'co vao nhung khong dang ky'"),
]
# Doi chung -- phai co o CA HAI goi.
# ⚠ Route khai TRONG nhom MapGroup("/auth") nen literal that la "/register",
#    khong phai "/auth/register" -- bai hoc 16/08/2026 voi "/me/profile".
DOI_CHUNG = ["/register", "/activate", "BONUS#", "WAITLIST#", "/visit"]

print("\n[2] DAU HIEU CUA BA VIEC (phai CO o moi, KHONG o cu)")
for s, why in MOI:
    a, b = has(new, s), has(old, s)
    chk("%-24s %s" % (s, why), a and not b,
        "moi=%s cu=%s" % ("co" if a else "khong", "co" if b else "khong"))

print("\n[3] DOI CHUNG (phai co o CA HAI -- neu khong thi phep tim dang hong)")
for s in DOI_CHUNG:
    a, b = has(new, s), has(old, s)
    chk("%-20s co o ca hai goi" % s, a and b,
        "moi=%s cu=%s" % ("co" if a else "khong", "co" if b else "khong"))

print("\n===== %d OK - %d HONG =====" % (n["ok"], n["ng"]))
sys.exit(1 if n["ng"] else 0)
