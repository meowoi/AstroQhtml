# -*- coding: utf-8 -*-
"""Phép thử phá hoại cho check_pages mục [21].
⚠️ Sao lưu và khôi phục PHẢI trong cùng một tiến trình Python — bài học 02/08/2026:
   `/tmp` của Git Bash và của Python là hai chỗ khác nhau, khôi phục hụt là để lại
   repo ở trạng thái đã bị phá."""
import io, os, subprocess, sys

ROOT = r"c:\Users\ADMIN\OneDrive\Desktop\astroq\AstroQhtml"
sys.stdout.reconfigure(encoding="utf-8")


def rd(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


def wr(rel, s):
    io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="").write(s)


def run():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-u", "scratchpad/check_pages.py"],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    bad = [l.strip() for l in r.stdout.split("\n") if l.lstrip().startswith("[HONG]")]
    return bad


CASES = [
    # (nhãn, file, phép biến đổi)
    ("tro data-sic vao mot icon KHONG ton tai", "dashboard.html",
     lambda s: s.replace('data-sic="target"', 'data-sic="khong-co-icon-nay"', 1)),
    ("dung mot icon dang trong danh sach NGU (khong cap nhat danh sach)", "dashboard.html",
     lambda s: s.replace('data-sic="target"', 'data-sic="lock"', 1)),
    ("nap bo icon o mot trang KHONG dung no", "profile.html",
     lambda s: s.replace('<script src="js/ui-common.js"></script>',
                         '<script src="js/sticker-icons.js"></script>\n'
                         '<script src="js/ui-common.js"></script>', 1)),
    ("bo net navy ngoai cung (sticker mat vien tren nen sang)", "js/sticker-icons.js",
     lambda s: s.replace("'<g class=\"sic-edge\">' + d.body + '</g>' +", "", 1)),
    ("tra `.badge.off .medal` ve filter:grayscale", "css/achievements.css",
     lambda s: s.replace(".badge.off .medal{opacity:.72;}",
                         ".badge.off .medal{filter:grayscale(1);opacity:.4;}", 1)),
    ("bo truong `sic` cua mot huy hieu", "js/badges.js",
     lambda s: s.replace(' sic:"grad",', "", 1)),
]

base = run()
print("nen truoc khi pha: %d hong %s" % (len(base), base or ""))
print()
for label, rel, fn in CASES:
    orig = rd(rel)
    try:
        broken = fn(orig)
        assert broken != orig, "phep bien doi KHONG khop moc — phep thu nay rong!"
        wr(rel, broken)
        bad = run()
        new = [b for b in bad if b not in base]
        print("%-62s -> %d phep kiem bao hong" % (label, len(new)))
        for b in new[:3]:
            print("        " + b[:118])
        if not new:
            print("        !! LOT — phep kiem mu voi loi nay")
    finally:
        wr(rel, orig)

after = run()
print()
print("sau khi khoi phuc: %d hong (phai bang nen)" % len(after))
