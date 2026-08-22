# -*- coding: utf-8 -*-
"""pha_char_sync.py — PHEP THU PHA HOAI cho check_char_sync.py.

Gay tung loi CO Y roi doi bo do bao hong. Mot phep kiem khong do duoc
khi ta pha dung cho no canh thi no dang "dat mot cach RONG".

Sao luu / khoi phuc lam TRONG CUNG MOT tien trinh Python — /tmp cua Git Bash
va cua Python la hai cho khac nhau (bai hoc 02/08/2026).

  python scratchpad/pha_char_sync.py
"""
import io
import pathlib
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SV = ROOT.parent / "AstroqSV" / "src" / "AstroqSV.Api"

# (nhan, duong dan, chuoi cu, chuoi moi)
CASES = [
    ("[A] login() KHONG cho hydrateProfile (bo chay nen)",
     ROOT / "js" / "firebase-auth.js",
     "      await hydrateProfile(this);",
     "      hydrateProfile(this);"),

    ("[B] sync(): 'server luon thang' (nhanh keo ve dung truoc)",
     ROOT / "js" / "characters.js",
     "    if (pendingUp(uid)) return syncUp(auth, uid);                                    // ②\n"
     "    absorb(serverChar, serverAvatar);                                                // ③",
     "    absorb(serverChar, serverAvatar);\n"
     "    if (pendingUp(uid)) return syncUp(auth, uid);"),

    ("[C] select.html thoi danh dau 'lua chon chua gui'",
     ROOT / "js" / "auth-flow.js",
     "    if(window.AstroQChars && AstroQChars.touch) AstroQChars.touch();",
     "    /* da bo */"),

    ("[D] server thoi tra `character` o /me/achievements",
     SV / "Endpoints" / "MeEndpoints.cs",
     '                character = prof is null ? "" : Str(prof, "character"),',
     '                charX     = prof is null ? "" : Str(prof, "character"),'),

    ("[E] progress.js thoi noi day (bo mot loi goi syncIdentity)",
     ROOT / "js" / "progress.js",
     "            syncIdentity(a, r.data);\n",
     ""),

    ("[G] select.html nem CA tre cu vao man onboarding (bo returning())",
     ROOT / "js" / "auth-flow.js",
     "    var skipIntro = admin || returning();",
     "    var skipIntro = admin;"),

    ("[H] hydrate thoi keo co onboarding ve cache",
     ROOT / "js" / "firebase-auth.js",
     '    try{ if(p.map01Seen === true) localStorage.setItem("astroq-map01-seen", "1"); }catch(e){}',
     '    /* da bo */'),

    ("[F] characters.js thoi dong dau theo uid",
     ROOT / "js" / "characters.js",
     'var LS_SYNC = "astroq-char-synced";',
     'var LS_SYNC = "astroq-char-synced-x";'),
]


def run_checker():
    r = subprocess.run(
        [sys.executable, str(HERE / "check_char_sync.py")],
        capture_output=True, cwd=str(ROOT),
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )
    out = (r.stdout or b"").decode("utf-8", "replace")
    return sum(1 for l in out.splitlines() if l.lstrip().startswith("[HONG]")), out


def main():
    print("--- moc: chay bo do khi mã con nguyen ---")
    base_ng, out = run_checker()
    tail = [l for l in out.splitlines() if "KET QUA" in l]
    print("   " + (tail[-1] if tail else "(khong doc duoc dong ket qua)"))
    if base_ng:
        print("[X] Moc khong sach (%d hong) — sua truoc khi pha." % base_ng)
        return 1

    caught = 0
    for label, path, old, new in CASES:
        enc = "utf-8-sig" if path.suffix == ".cs" else "utf-8"
        src = io.open(path, encoding=enc).read()
        if old not in src:
            print("  [X] %s -> KHONG tim thay moc de pha (bo do KHONG chung minh duoc gi)"
                  % label)
            continue
        try:
            io.open(path, "w", encoding=enc).write(src.replace(old, new, 1))
            ng, _ = run_checker()
            if ng > 0:
                print("  [BAT DUOC] %s  (%d phep kiem bao hong)" % (label, ng))
                caught += 1
            else:
                print("  [LOT]      %s  <-- phep kiem MU, phai siet lai" % label)
        finally:
            io.open(path, "w", encoding=enc).write(src)   # khoi phuc NGAY

    print("\n--- kiem lai sau khi khoi phuc ---")
    ng, out = run_checker()
    tail = [l for l in out.splitlines() if "KET QUA" in l]
    print("   " + (tail[-1] if tail else "?"))
    print("\n=== BAT DUOC %d/%d loi co y ===" % (caught, len(CASES)))
    return 0 if (caught == len(CASES) and ng == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
