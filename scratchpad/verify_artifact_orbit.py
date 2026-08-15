# -*- coding: utf-8 -*-
"""Kiem GOI TRUOC KHI DEPLOY, va SO VOI GOI DANG CHAY.

`aws lambda update-function-code` KHONG tu phat hien goi sai — bai hoc 29/07/2026:
`sam build` chet giua chung, `sam deploy` dong goi dung thu muc rong, Lambda tra
"Uploaded file must be a non-empty zip" va CloudFormation rollback.

⚠️ HAI HEAP KHAC NHAU TRONG DLL .NET:
   · chuoi LITERAL ("mission:orbit", "satellite-eyes")  -> #US heap, UTF-16LE
   · ten field/method/type ("GateMissionOfPlace")       -> #Strings heap, UTF-8
   Tim nham heap la bao "THIEU" oan. Script nay tim ca hai kieu.

⚠️ CO DOI CHUNG: mot vai chuoi phai co o CA HAI goi (cu va moi). Neu chung cung
   "khong thay" thi phep tim dang chay sai, chu khong phai goi thieu.
"""
import io, os, sys, zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

NEW_DIR = r"C:\lambda-build\publish"
OLD_ZIP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "..", "AstroqSV", "ROLLBACK-AstroqSV-20260815b.zip")
DLL = "AstroqSV.Api.dll"

# (chuoi, phai co o goi MOI, phai co o goi CU)
CASES = [
    # ⚠️ ĐỪNG dùng `"orbit"` trần làm dấu hiệu: nó là CHUỖI CON nên trúng cả gói CŨ
    #    (do lot vao mot chuoi khac trong DLL). Do do lan chay dau bao "hong" trong khi
    #    goi hoan toan dung — ky vong SAI, khong phai goi sai. Dung chuoi CHINH XAC.
    ("mission:orbit",        True,  False),   # metric huy hieu, chi co o goi moi
    ("earth-observer",       True,  False),   # huy hieu moi
    ("satellite-eyes",       True,  False),   # mau codex
    ("night-lights",         True,  False),
    ("read-image",           True,  False),
    ("GateMissionOfPlace",   True,  False),   # ten method (doi ten 15/08)
    ("MissionsOfPlace",      True,  False),
    # --- DOI CHUNG: phai co o CA HAI, de biet phep tim dang chay dung ---
    ("earth",                True,  True),
    ("rookie-astronaut",     True,  True),
    ("UnlockedPlaces",       True,  True),
]


def blob(path_or_zip):
    if os.path.isdir(path_or_zip):
        with open(os.path.join(path_or_zip, DLL), "rb") as f:
            return f.read()
    z = zipfile.ZipFile(path_or_zip)
    name = next(n for n in z.namelist() if n.endswith(DLL))
    return z.read(name)


def has(data, s):
    """Tim ca o #US heap (UTF-16LE) lan #Strings heap (UTF-8)."""
    return (s.encode("utf-16-le") in data) or (s.encode("utf-8") in data)


dat = hong = 0


def check(nhan, dk, ct=""):
    global dat, hong
    if dk:
        dat += 1
        print("  [OK]   " + nhan + (("  " + ct) if ct else ""))
    else:
        hong += 1
        print("  [HONG] " + nhan + (("  " + ct) if ct else ""))


print("=== Goi MOI: %s ===" % NEW_DIR)
files = os.listdir(NEW_DIR)
check("goi khong rong", len(files) > 0, "%d file" % len(files))
check("co %s" % DLL, DLL in files)
check("co AstroqSV.Api.deps.json", "AstroqSV.Api.deps.json" in files)
check("so file >= 30 (goi dang chay co 39)", len(files) >= 30, str(len(files)))

new = blob(NEW_DIR)
old = blob(os.path.abspath(OLD_ZIP))
print("\n=== Doi chieu chuoi: goi MOI vs goi DANG CHAY ===")
for s, want_new, want_old in CASES:
    n, o = has(new, s), has(old, s)
    ok = (n == want_new) and (o == want_old)
    check("%-22s moi=%-5s cu=%-5s" % (s, n, o), ok,
          "" if ok else "(mong doi moi=%s cu=%s)" % (want_new, want_old))

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(1 if hong else 0)
