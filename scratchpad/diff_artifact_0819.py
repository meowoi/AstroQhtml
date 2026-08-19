# -*- coding: utf-8 -*-
"""GOI NAY MANG GI SO VOI BAN DANG CHAY — diff tap ky hieu, khong doan ten.

Vi sao can: bo kiem `check_artifact_0819.py` do TUNG dau hieu toi nghi ra, nen no
chi tra loi duoc cau "cai X co khong". Cau that su can tra loi truoc khi deploy la
**"gói này đổi những gì"** — mà cau do khong doan duoc, phai diff.

Cach lam: rut moi chuoi giong DINH DANH (ten lop / ten phuong thuc / ten truong)
tu #Strings heap (UTF-8) va moi chuoi literal tu #US heap (UTF-16LE) cua ca hai
DLL, roi lay hieu hai tap.

⚠️ KET QUA CO THE CO ANH GIA — da bat duoc mot ca 19/08/2026: `x10000` hien ra o
   danh sach "chi co o goi moi", nhung dem lai thi no xuat hien **0 lan** o CA HAI
   ma hoa trong CA HAI goi. Nguyen nhan: buoc `decode("utf-16-le","ignore")` roi
   `encode("ascii","ignore")` o duoi **tu sinh ra** nhung chuoi khong co that. No
   qua duoc bo loc vi ma nguon co `0x10000` (chua chuoi con `x10000`).
   => Ky hieu nao dang gia thi phai DEM LAI bang `bytes.count()` trong ca hai goi,
      dung tin danh sach nay mot minh.

⚠️ Day khong phai bo doc metadata dung nghia — no quet tho ca file. Nen ket qua co
   the lan nhung manh khong phai dinh danh; du dung cho viec "co gi moi/mat gi",
   khong du de ket luan mot ky hieu KHONG duoc dung o dau.

  python scratchpad/diff_artifact_0819.py
"""
import io
import os
import re
import sys
import zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

NEW = r"C:\lambda-build\deploy0819.zip"
OLD = r"C:\lambda-build\rb0819\ROLLBACK-AstroqSV-20260819pre.zip"
DLL = "AstroqSV.Api.dll"

ID = re.compile(rb"[A-Za-z_][A-Za-z0-9_]{4,63}")


def syms(path):
    b = zipfile.ZipFile(path).read(DLL)
    u8 = set(m.group(0).decode("ascii") for m in ID.finditer(b))
    # #US heap: UTF-16LE -> giai ma bang cach bo byte 0 xen ke
    try:
        u16 = set(m.group(0).decode("ascii")
                  for m in ID.finditer(b.decode("utf-16-le", "ignore").encode("ascii", "ignore")))
    except Exception:
        u16 = set()
    return u8 | u16


a, b = syms(OLD), syms(NEW)
them = sorted(x for x in (b - a))
mat = sorted(x for x in (a - b))

# ⚠️ LOC RAC BANG MA NGUON THAT, khong bang hinh dang chuoi. Ban loc dau tien
#    ("co ca chu hoa va chu thuong") de lot 40+ chuoi nhu `A2I2f6`, `BABkB` —
#    do la MVID/hash/ten resource do trinh bien dich sinh. Cach dut khoat: mot ky
#    hieu la CUA DU AN khi va chi khi no xuat hien trong `AstroqSV/src/**/*.cs`.
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "..", "AstroqSV", "src")
_code = []
for root, _dirs, files in os.walk(SRC):
    if "bin" in root or "obj" in root:
        continue
    for f in files:
        if f.endswith(".cs"):
            _code.append(io.open(os.path.join(root, f), encoding="utf-8",
                                 errors="replace").read())
CODE = "\n".join(_code)


def coi_duoc(s):
    # `get_quizLv` la ten accessor do C# sinh cho property/thuoc tinh -> tra ve goc.
    goc = s[4:] if s.startswith("get_") or s.startswith("set_") else s
    return goc in CODE

them_r = [x for x in them if coi_duoc(x)]
mat_r = [x for x in mat if coi_duoc(x)]

print("=== KY HIEU CHI CO O GOI MOI (%d, sau khi loc %d) ===" % (len(them), len(them_r)))
for x in them_r:
    print("  + %s" % x)

print("\n=== KY HIEU MAT SO VOI BAN DANG CHAY (%d, sau khi loc %d) ===" % (len(mat), len(mat_r)))
if not mat_r:
    print("  (khong mat ky hieu nao — dung dieu mong doi)")
for x in mat_r:
    print("  - %s" % x)

print("\n⚠️ Doc ket qua: moi dong `+` phai GIAI THICH DUOC bang mot thay doi ma nguon"
      " co that. Mot dong khong giai thich duoc nghia la goi mang theo thu toi khong"
      " biet — DUNG DEPLOY truoc khi hieu no.")
