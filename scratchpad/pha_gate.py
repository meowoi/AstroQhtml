# -*- coding: utf-8 -*-
"""Phep thu pha hoai cho HAI bo do vua duoc cho `sys.exit` (22/08/2026).

VI SAO CAN: `probe_chip_label` va `audit_taps` truoc day **khong he goi
`sys.exit`**, nen chung LUON thoat 0 — tim ra 9 nhan chip bi cat hay mot vung
cham tut xuong duoi 44px thi cua push VAN XANH. Mot bo do khong bao gio do duoc
la mot bo do da chet. Sau khi cho chung thoat 1, phai CHUNG MINH chung do duoc —
lam mot bo do "trong xanh" ma khong chung minh no do duoc thi khong chung minh
duoc gi.

Chay:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/pha_gate.py

Ket qua do duoc 22/08/2026:
  [A] bo CA HAI dong hang rao  -> probe_chip_label exit=1, 3 nhan bi cat  BAT DUOC
  [B] bop `.back-btn` con 20px -> audit_taps       exit=1, 1 nhom can sua BAT DUOC

⚠️⚠️ SAO LUU/KHOI PHUC LAM BANG **BYTE**, KHONG BANG VAN BAN DA GIAI MA.
   Ban dau cua bo nay doc bang `io.open(..., encoding="utf-8")` roi ghi lai cung
   kieu, tuc Python doi LF -> CRLF (newline=None tren Windows). No bao "khoi phuc
   OK" — vi no so VAN BAN, ma van ban thi giong het — trong khi `git status` bao
   `css/common.css` DA DOI (244 dong tu LF thanh CRLF). Mot phep kiem khoi phuc
   mu voi ky tu xuong dong la mot phep kiem se de lai repo o trang thai da doi
   ma van bao sach. Nay doc/ghi bang `"rb"`/`"wb"`.
⚠️ Sao luu va khoi phuc lam TRONG CUNG MOT TIEN TRINH Python — bai hoc 02/08:
   `/tmp` cua Git Bash va cua Python la hai cho khac nhau.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "css" / "game-shell.css"
COMMON = ROOT / "css" / "common.css"

bak = {p: p.read_bytes() for p in (CSS, COMMON)}


def gate(name):
    r = subprocess.run([sys.executable, "-u", str(ROOT / "scratchpad" / (name + ".py"))],
                       cwd=str(ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def dong(out, moc):
    for ln in out.splitlines():
        if moc in ln:
            return ln.strip()
    return "(khong thay dong tong ket)"


try:
    # ── [A] probe_chip_label: bo hang rao cho nhan chip ─────────────────────
    # ⚠️ Bai hoc 22/08: bo `flex:1 0 100%` MOT MINH thi nhan chi xuong 2-3 dong
    #    va VAN doc du chu — tuc loi co y ay khong phai loi. Hang rao THAT la
    #    `flex-wrap:wrap`; phai tra CA HAI ve moi tai tao duoc nhan bi cat.
    s = bak[CSS].replace(b"flex-wrap:wrap;row-gap:2px;", b"")
    assert s != bak[CSS], "khong tim thay `flex-wrap:wrap;row-gap:2px;`"
    s2 = s.replace(b"flex:1 0 100%;", b"")
    assert s2 != s, "khong tim thay `flex:1 0 100%;`"
    CSS.write_bytes(s2)
    code, out = gate("probe_chip_label")
    print("[A] bo CA HAI dong hang rao -> probe_chip_label exit=%d | %s"
          % (code, dong(out, "TONG SO NHAN")))
    print("    %s" % ("BAT DUOC" if code != 0 else "⚠️ LOT — phep kiem MU"))
    CSS.write_bytes(bak[CSS])

    # ── [B] audit_taps: bop mot vung cham xuong duoi 44px ───────────────────
    # `.back-btn` la nut "Ve Trung Tam Dieu Huong" — bam truot dung nut do nghia
    # la tre mac ket trong trang, tuc dung thu bo do nay sinh ra de canh.
    s = bak[COMMON].replace(b".back-btn{",
                            b".back-btn{min-height:20px !important;height:20px !important;", 1)
    assert s != bak[COMMON], "khong tim thay `.back-btn{`"
    COMMON.write_bytes(s)
    code, out = gate("audit_taps")
    print("[B] bop `.back-btn` con 20px -> audit_taps exit=%d | %s"
          % (code, dong(out, "nhom CAN SUA")))
    print("    %s" % ("BAT DUOC" if code != 0 else "⚠️ LOT — phep kiem MU"))
finally:
    for p, b in bak.items():
        p.write_bytes(b)
    sai = [p.name for p, b in bak.items() if p.read_bytes() != b]
    print("khoi phuc %d file CSS (so bang BYTE): %s"
          % (len(bak), "OK" if not sai else "⚠️ HONG: %s — KIEM TAY NGAY" % sai))
