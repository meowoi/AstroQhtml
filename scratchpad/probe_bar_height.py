# -*- coding: utf-8 -*-
"""Moi THANH DO trong game phai co chieu cao THAT dung bang chieu cao KHAI trong CSS.

⚠️⚠️ VI SAO BO DO NAY TON TAI — mot lop loi da tai dien BA LAN:
   1. 30/07/2026 `.prog`/`.bar` cua achievements.html: `<span>` nen `height:6px` bi bo
      qua, thanh tien do KHONG HIEN mot chut nao.
   2. 30/08/2026 `.rc-bar` cua Tram Tuan Hoan: cung `<span>`, thanh phinh tu 7px len
      **23px**, tran khoi the va DE LEN dong chu ngay duoi (663-1920px2 tren 4 kho man).
   3. 30/08/2026 `.cm-bar` cua Tram Lien Lac: render ra **0x0** — vo hinh hoan toan,
      trong khi chinh no dien ta do tre 7 phut, tuc bai hoc trung tam cua ARCADE-08.
   Ca ba deu IM LANG: doc CSS thay `height` khai dung, doc HTML thay the hop le,
   `grep` khong noi gi. Chi RENDER roi DO moi thay.

⚠️ `width`/`height` KHONG ap cho phan tu `display:inline`, va `position:relative`
   KHONG blockify no (chi `absolute`/`fixed` moi lam the). Thanh nao co cha la flex
   thi song sot nho duoc blockify TU DONG — tuc no dung nho MAY, khong nho thiet ke.
   Vi vay luat la: khai `display` ngay TREN THANH, dung dua vao cha.

⚠️ BANG `BARS` PHAI PHU HET — bo do tu quet css/game-*.css tim moi rule dat `height`
   bang pixel co dinh cho mot class ten dang `*bar*`, roi doi bang nay liet ke du.
   Them mot thanh moi ma quen khai o day thi bo do BAO HONG, khong im lang bo qua.
"""
import io, os, re, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "http://127.0.0.1:8123/"

# (trang, selector, chieu cao KHAI, co can bo an cha khong)
BARS = [
    ("game-recycle.html",  ".rc-bar",   7,  None),
    ("game-comms.html",    ".cm-bar",   6,  "#wait"),
    ("game-defender.html", ".hullbar",  10, None),
    ("game-racer.html",    ".chip.fuel .bar", 4, None),
]
# Thanh do khung chung: dung `<div>` nen khong dinh bay, van do de chac.
BARS += [("game-dodge.html", ".gs-track", 8, None),
         ("game-defender.html", ".chargebar", 3, None)]

ok = hong = 0
def chk(name, cond, info=""):
    global ok, hong
    if cond: ok += 1; print("  [OK]   %s" % name)
    else:    hong += 1; print("  [HONG] %s%s" % (name, ("  | " + info) if info else ""))

# ---- [1] Bang BARS phai phu het cac thanh khai trong CSS ----------------------
print("[1] Bang BARS co bo sot thanh nao khong")
declared = set()
for fn in sorted(os.listdir(os.path.join(ROOT, "css"))):
    if not fn.startswith("game-") or not fn.endswith(".css"): continue
    src = io.open(os.path.join(ROOT, "css", fn), encoding="utf-8").read()
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)          # bo chu thich
    for m in re.finditer(r"(^|\})\s*([^{}@]*?bar[^{}]*?)\{([^{}]*)\}", src, re.I | re.M):
        sel, body = m.group(2).strip(), m.group(3)
        if re.search(r"(^|[;\s])height\s*:\s*\d+px", body) and " i" not in sel.split(",")[0][-3:]:
            key = sel.split(",")[0].strip()
            if key.endswith(" i") or "::" in key: continue
            declared.add(key)
listed = set(s for _, s, _, _ in BARS)
missing = sorted(d for d in declared if not any(d.endswith(l.split()[-1]) or l.endswith(d.split()[-1]) for l in listed))
chk("moi thanh khai height px deu co trong bang BARS", not missing,
    "chua khai: %s (tim thay: %s)" % (missing, sorted(declared)))

# ---- [2] Do chieu cao THAT tren trinh duyet ----------------------------------
print("[2] Chieu cao THAT == chieu cao KHAI")
with sync_playwright() as p:
    b = p.chromium.launch()
    for page_url, sel, want, unhide in BARS:
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                            "localStorage.setItem('astroq-asteroids','99');}catch(e){}")
        pg = ctx.new_page()
        try:
            pg.goto(BASE + page_url, wait_until="networkidle", timeout=20000)
        except Exception as e:
            chk("%s tai duoc" % page_url, False, str(e)[:80]); ctx.close(); continue
        for s in [".dg-btn.primary", "#start-btn", ".acts .primary"]:
            try: pg.click(s, timeout=2500); break
            except Exception: pass
        pg.wait_for_timeout(1300)
        if unhide:
            pg.evaluate("(s)=>{const e=document.querySelector(s); if(e) e.hidden=false;}", unhide)
            pg.wait_for_timeout(150)
        r = pg.evaluate("""(sel)=>{const el=document.querySelector(sel); if(!el) return null;
            const b=el.getBoundingClientRect(), cs=getComputedStyle(el);
            return {h:Math.round(b.height*10)/10, w:Math.round(b.width), disp:cs.display};}""", sel)
        if r is None:
            chk("%s  %s ton tai" % (page_url, sel), False, "khong tim thay phan tu")
        else:
            chk("%-20s %-18s cao %s (khai %s)" % (page_url, sel, r["h"], want),
                abs(r["h"] - want) <= 1.5 and r["w"] > 0,
                "display=%s rong=%s" % (r["disp"], r["w"]))
        ctx.close()
    b.close()

print("\nKET QUA: %d dat / %d hong" % (ok, hong))
sys.exit(1 if hong else 0)
