# -*- coding: utf-8 -*-
"""Kiem goi MOI vs goi DANG CHAY truoc khi deploy. Nhan print KHONG DAU.
CANH BAO: chuoi literal nam o #US heap (UTF-16LE), ten field/method o #Strings (UTF-8).
Tim nham heap la bao 'THIEU' oan.
"""
import io, zipfile

NEW = r"C:\lambda-build\out\AstroqSV.Api.dll"
OLD_ZIP = r"C:\lambda-build\rollback.zip"

new = io.open(NEW, "rb").read()
old = zipfile.ZipFile(OLD_ZIP).read("AstroqSV.Api.dll")


def has_lit(b, s):          # chuoi literal -> UTF-16LE
    return s.encode("utf-16-le") in b


def has_name(b, s):         # ten field/method -> UTF-8
    return s.encode("utf-8") in b


print("co DLL moi: %d byte | DLL cu: %d byte" % (len(new), len(old)))
print()
print("%-28s %-8s %-8s %s" % ("dau hieu", "goi MOI", "goi CU", "ket luan"))
print("-" * 66)

# (nhan, ham do, mong doi o goi moi, mong doi o goi cu)
CHECKS = [
    ("FeeByDiff (ten field)", has_name, "FeeByDiff", True, False),
    ("Diff (ten field)",      has_name, "get_Diff", None, None),
    ('literal "easy"',        has_lit,  "easy", True, False),
    ('literal "medium"',      has_lit,  "medium", True, False),
    ('literal "hard"',        has_lit,  "hard", True, False),
    # doi chung: phai co o CA HAI goi -> chung minh phep tim dang chay dung
    ('literal "maze"',        has_lit,  "maze", True, True),
    ('literal "dodge"',       has_lit,  "dodge", True, True),
    ("MaxPerQuiz (ten field)", has_name, "MaxPerQuiz", True, True),
]

bad = 0
for label, fn, needle, exp_new, exp_old in CHECKS:
    n = fn(new, needle)
    o = fn(old, needle)
    if exp_new is None:
        verdict = "(chi ghi nhan)"
    else:
        ok = (n == exp_new) and (o == exp_old)
        verdict = "OK" if ok else "!! LECH MONG DOI"
        if not ok:
            bad += 1
    print("%-28s %-8s %-8s %s" % (label, "CO" if n else "khong",
                                  "CO" if o else "khong", verdict))

print()
print("=> %s" % ("SAN SANG DEPLOY" if bad == 0 else "DUNG LAI: %d dau hieu lech" % bad))
