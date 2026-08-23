# -*- coding: utf-8 -*-
"""PHA HOAI muc [2] cua probe_article_quiz.py: bon loi CO Y, ca bon phai bi bat.

VI SAO CAN BO NAY: muc [2] tung BAO XANH OAN cho 24 bai `terms: []` (ban cu tim
`terms\\s*:\\s*\\[` — mau do khop ca mang RONG). Mot phep kiem vua sua xong thi
phai chung minh no co RANG, khong thi chi doi mot cai mu bang mot cai mu khac.

BON DOT BIEN, bon phep kiem khac nhau phai do:
  ① lam rong `terms` cua mot bai        -> "moi bai NGOAI MIEN_TERMS co terms..."
  ② xoa han khai bao `terms` cua mot bai -> "moi bai doc deu KHAI `terms`"
  ③ them vao MIEN_TERMS mot slug DA CO terms -> "`MIEN_TERMS` con DUNG..."
  ④ them mot slug KHONG TON TAI vao MIEN_TERMS -> "khong chua slug khong ton tai"

⚠️ ② LA DOT BIEN QUAN TRONG NHAT: phep kiem no do CHUA TUNG bi thu, va no la
   phep kiem duy nhat bat duoc ca "bai moi them ma quen khai `terms`".
⚠️ ③ va ④ khac nhau: ③ la danh sach MUC RA (noi roi ma khong xoa khoi ds), ④ la
   danh sach GO SAI. Hai kieu hong khac nhau, hai phep kiem khac nhau.
⚠️ Chon bai cho ① ② NGOAI ca `CO_TERMS` — muc [1] mo trinh doc THAT nen mot bai
   vo o day la them ~15s cho ho, va lam do lay mot muc khong lien quan.
⚠️ Khoi phuc roi doi chieu BYTE (sha256), khong tin vao "da ghi lai la xong".

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/pha_terms.py
"""
import hashlib
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROBE = os.path.join(HERE, "probe_article_quiz.py")
ART = os.path.join(ROOT, "js", "article")

# Hai bai CO Y ngoai `CO_TERMS` (xem ⚠️ o docstring)
A_RONG = os.path.join(ART, "art-algorithmic-bias.js")        # ① lam rong
A_XOA = os.path.join(ART, "art-ai-tags-nasa-data.js")        # ② xoa han khai bao
# Bai DA CO terms, dem nhet vao MIEN_TERMS o ③
SLUG_DA_CO = "lib-qubit"

FILES = [A_RONG, A_XOA, PROBE]


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

ma = 1
xau = 0
try:
    # --- ① lam rong `terms` ---
    s = goc[A_RONG]
    i = s.index("terms:")
    j = s.index("]", i) + 1
    print("\n① %s: %s -> terms: []" % (os.path.basename(A_RONG), s[i:j][:52]))
    ghi(A_RONG, s[:i] + "terms: []" + s[j:])

    # --- ② xoa han khai bao `terms` ---
    s = goc[A_XOA]
    m = re.search(r"[ \t]*terms\s*:\s*\[[^\]]*\]\s*,?\s*\n", s)
    if not m:
        raise SystemExit("!!! khong tim thay khai bao `terms` o %s"
                         % os.path.basename(A_XOA))
    print("② %s: XOA HAN %r" % (os.path.basename(A_XOA), m.group(0).strip()))
    ghi(A_XOA, s[:m.start()] + s[m.end():])

    # --- ③ + ④ nhet hai slug vao MIEN_TERMS ---
    s = goc[PROBE]
    moc = "MIEN_TERMS = {\n"
    if s.count(moc) != 1:
        raise SystemExit("!!! khong tim thay moc DUY NHAT `MIEN_TERMS = {` (%d)"
                         % s.count(moc))
    ghi(PROBE, s.replace(moc, moc
                         + '    "%s",\n' % SLUG_DA_CO
                         + '    "zz-bai-khong-ton-tai",\n', 1))
    print('③ MIEN_TERMS += "%s"  (bai DA CO terms)' % SLUG_DA_CO)
    print('④ MIEN_TERMS += "zz-bai-khong-ton-tai"')

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
    print("\n".join(dong2) if dong2 else "!!! KHONG DOC DUOC MUC [2]:\n" + out[-900:])

    bat = {
        "① bai bi lam rong `terms`":
            any("NGOAI `MIEN_TERMS`" in l and "[HONG]" in l for l in dong2),
        "② bai bi XOA HAN khai bao `terms`":
            any("KHAI `terms`" in l and "[HONG]" in l for l in dong2),
        "③ ds mien tru MUC RA (slug da co terms)":
            any("con DUNG" in l and "[HONG]" in l for l in dong2),
        "④ ds mien tru co slug KHONG TON TAI":
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
    for p in FILES:
        ok = bam(p) == bam_goc[p]
        xau += 0 if ok else 1
        print("  %s %s  %s" % ("[KHOP]" if ok else "[LECH]", bam(p)[:16],
                               os.path.basename(p)))
    if xau:
        print("!!! CO FILE KHONG KHOI PHUC DUOC — kiem tay ngay")

print("\n=== %s ===" % ("CA BON LOI DEU BI BAT" if ma == 0 else "CO LOI LOT"))
sys.exit(ma if not xau else 2)
