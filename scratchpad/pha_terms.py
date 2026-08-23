# -*- coding: utf-8 -*-
"""PHA HOAI muc [2] cua probe_article_quiz.py: ba loi CO Y, ca ba phai bi bat.

VI SAO CAN BO NAY: muc [2] vua duoc siet vi ban cu BAO XANH OAN cho 24 bai
`terms: []` (no tim `terms\\s*:\\s*\\[` — mau do khop ca mang rong). Mot phep kiem
vua sua xong thi phai chung minh no co RANG, khong thi chi doi mot cai mu bang
mot cai mu khac.

BA DOT BIEN, ba phep kiem khac nhau phai do:
  ① bai NGOAI danh sach mien tru bi lam rong `terms`  -> "moi bai NGOAI MIEN_TERMS..."
  ② bai TRONG danh sach mien tru duoc noi `terms`      -> "`MIEN_TERMS` con DUNG..."
  ③ them mot slug KHONG TON TAI vao MIEN_TERMS         -> "khong chua slug khong ton tai"
Ba dot bien khong dinh nhau (ba nhanh doc lap trong ma), nen chay MOT luot.

⚠️ Chon bai o (1) ngoai ca `CO_TERMS` de dot bien khong lam do lay muc [1] —
   muc [1] mo trinh doc that nen mot bai vo o day la them ~15s cho ho.
⚠️ Khoi phuc roi doi chieu BYTE (sha256), khong tin vao "da ghi lai la xong".

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/pha_terms.py
"""
import hashlib
import io
import os
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROBE = os.path.join(HERE, "probe_article_quiz.py")

# (1) ngoai MIEN_TERMS, va CO Y ngoai CO_TERMS de khong lam do lay muc [1]
A_NGOAI = os.path.join(ROOT, "js", "article", "art-algorithmic-bias.js")
# (2) trong MIEN_TERMS
A_MIEN = os.path.join(ROOT, "js", "article", "lib-qubit.js")

FILES = [A_NGOAI, A_MIEN, PROBE]


def bam(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def doc(p):
    return io.open(p, encoding="utf-8", newline="").read()


def ghi(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


goc = dict((p, doc(p)) for p in FILES)
bam_goc = dict((p, bam(p)) for p in FILES)
print("=== BAM GOC ===")
for p in FILES:
    print("  %s  %s" % (bam_goc[p][:16], os.path.basename(p)))

try:
    # --- Dot bien ① ---
    s = goc[A_NGOAI]
    i = s.index("terms:")
    j = s.index("]", i) + 1
    cu = s[i:j]
    ghi(A_NGOAI, s[:i] + "terms: []" + s[j:])
    print("\n① %s: %s -> terms: []" % (os.path.basename(A_NGOAI), cu[:52]))

    # --- Dot bien ② ---
    s = goc[A_MIEN]
    if "terms: []" not in s:
        raise SystemExit("!!! %s khong con `terms: []` — sua lai bo pha hoai"
                         % os.path.basename(A_MIEN))
    ghi(A_MIEN, s.replace("terms: []", 'terms: ["loop"]'))
    print('② %s: terms: [] -> terms: ["loop"]' % os.path.basename(A_MIEN))

    # --- Dot bien ③ ---
    s = goc[PROBE]
    moc = '    "art-what-is-ai-nasa", "lib-qubit",\n'
    if s.count(moc) != 1:
        raise SystemExit("!!! khong tim thay moc duy nhat trong MIEN_TERMS (%d)"
                         % s.count(moc))
    ghi(PROBE, s.replace(moc, moc + '    "zz-bai-khong-ton-tai",\n'))
    print('③ MIEN_TERMS += "zz-bai-khong-ton-tai"')

    print("\n=== CHAY probe_article_quiz.py (chi doc muc [2]) ===")
    r = subprocess.run([sys.executable, PROBE], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    out = (r.stdout or "") + (r.returncode and "\n[exit %d]" % r.returncode or "")
    trong_muc2 = False
    dong2 = []
    for ln in out.splitlines():
        if "[2] Bat bien" in ln:
            trong_muc2 = True
        elif "[2b]" in ln:
            trong_muc2 = False
        if trong_muc2:
            dong2.append(ln)
    print("\n".join(dong2) if dong2 else "!!! KHONG DOC DUOC MUC [2]:\n" + out[-800:])

    bat = {
        "① bai ngoai ds bi lam rong":
            any("NGOAI `MIEN_TERMS`" in l and "[HONG]" in l for l in dong2),
        "② bai trong ds da duoc noi":
            any("con DUNG" in l and "[HONG]" in l for l in dong2),
        "③ slug khong ton tai trong ds":
            any("khong ton tai" in l and "[HONG]" in l for l in dong2),
    }
    print("\n=== KET QUA PHA HOAI ===")
    for k, v in bat.items():
        print("  %s  %s" % ("[BAT DUOC]" if v else "[LOT !!! ]", k))
    ma = 0 if all(bat.values()) else 1
finally:
    for p in FILES:
        ghi(p, goc[p])
    print("\n=== KHOI PHUC: doi chieu BYTE ===")
    xau = 0
    for p in FILES:
        ok = bam(p) == bam_goc[p]
        xau += 0 if ok else 1
        print("  %s %s  %s" % ("[KHOP]" if ok else "[LECH]", bam(p)[:16],
                               os.path.basename(p)))
    if xau:
        print("!!! CO FILE KHONG KHOI PHUC DUOC — kiem tay ngay")

print("\n=== %s ===" % ("CA BA LOI DEU BI BAT" if ma == 0 else "CO LOI LOT"))
sys.exit(ma if not xau else 2)
