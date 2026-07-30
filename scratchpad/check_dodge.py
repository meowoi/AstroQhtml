import re, sys, io, json
import os
_here = os.path.dirname(os.path.abspath(__file__))
p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_here, "..", "game-dodge.html")
src = io.open(p, encoding="utf-8").read()

fails = []
def ok(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond: fails.append(msg)

# ---- 1. tach script cuoi trang
m = re.findall(r"<script>(.*?)</script>", src, re.S)
ok(len(m) == 1, "co dung 1 khoi <script> inline (%d)" % len(m))
js = m[0]

# ---- 2. can bang ngoac (bo qua chuoi va comment)
def strip_js(s):
    out = []; i = 0; n = len(s)
    while i < n:
        c = s[i]
        if c == "/" and i+1 < n and s[i+1] == "*":
            j = s.find("*/", i+2); i = (j+2) if j >= 0 else n; continue
        if c == "/" and i+1 < n and s[i+1] == "/":
            j = s.find("\n", i); i = (j) if j >= 0 else n; continue
        if c in "\"'":
            q = c; i += 1
            while i < n and s[i] != q:
                if s[i] == "\\": i += 1
                i += 1
            i += 1; out.append('""'); continue
        out.append(c); i += 1
    return "".join(out)

clean = strip_js(js)
for a, b, name in [("{","}","{}"), ("(",")","()"), ("[","]","[]")]:
    ok(clean.count(a) == clean.count(b), "can bang %s  (%d vs %d)" % (name, clean.count(a), clean.count(b)))

# ---- 3. moi $("id") deu co phan tu trong HTML
html_ids = set(re.findall(r'id="([^"]+)"', src))
used = set(re.findall(r'\$\("([^"]+)"\)', js))
missing = sorted(used - html_ids)
ok(not missing, "moi $(\"id\") deu ton tai (thieu: %s)" % missing)
print("      id dung trong JS:", len(used), "| id trong HTML:", len(html_ids))

# ---- 4. i18n: 2 tu dien can bang + moi data-i18n* co khoa
def dict_keys(name):
    i = js.index(name + ":{")
    depth = 0; j = i + len(name) + 1
    start = j
    while True:
        if js[j] == "{": depth += 1
        elif js[j] == "}":
            depth -= 1
            if depth == 0: break
        j += 1
    body = js[start:j+1]
    # khoa co the nam giua dong: tach theo dau , hoac { dung truoc
    return set(re.findall(r'[{,]\s*([A-Za-z_][\w]*)\s*:', body)), body

vi, vibody = dict_keys("vi")
en, enbody = dict_keys("en")
ok(vi == en, "vi/en cung bo khoa (chi vi: %s | chi en: %s)" % (sorted(vi-en), sorted(en-vi)))
print("      so khoa:", len(vi))

attr_keys = set()
for a in ["i18n", "i18n-html", "i18n-ph", "i18n-title", "i18n-aria", "i18n-alt"]:
    attr_keys |= set(re.findall(r'data-%s="([^"]+)"' % a, src))
ok(attr_keys <= vi, "moi data-i18n* co trong tu dien (thieu: %s)" % sorted(attr_keys - vi))

js_keys = set(re.findall(r'(?<![\w$.])t\("([^"]+)"\)', js))   # tranh khop getContext("2d")
ok(js_keys <= vi, "moi t(\"key\") co trong tu dien (thieu: %s)" % sorted(js_keys - vi))
unused = sorted(vi - attr_keys - js_keys)
print("      khoa khong dung o dau:", unused)

# ---- 5. token {tt}/{n} khong bi sot
for k in ["reward_toast", "paid_lbl"]:
    ok(("{n}" in vibody.split(k+":")[1][:200]) and ("{n}" in enbody.split(k+":")[1][:200]), "%s co token {n} o ca 2 ngon ngu" % k)

# ---- 6. asset tham chieu ton tai
import os
base = os.path.dirname(p)
assets = set(re.findall(r'(?:src|href)=["\']([^"\':#?]+)["\']', src)) | set(re.findall(r"src='([^']+)'", js))
bad = [a for a in assets if not a.startswith(("http", "//")) and not a.endswith(".html") and not os.path.exists(os.path.join(base, a))]
ok(not bad, "moi asset ton tai (thieu: %s)" % bad)

# ---- 7. ham duoc dinh nghia truoc khi goi o top-level init
for fn in ["fit", "initStars", "applyLang", "frame", "paintBalance", "startRound", "gameOver", "onFinishGame", "syncBtns", "paintPaid"]:
    ok(("function %s(" % fn) in js, "co ham %s()" % fn)

# ---- 8. CSS: moi class dung trong HTML co trong css nao do (chi kiem class rieng cua trang)
# doc DUNG cac file css ma trang nay <link> vao (game-shell.css, css rieng cua game...)
sheets = re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', src)
css = ""
for sh in sheets:
    fp = os.path.join(base, sh)
    if os.path.exists(fp): css += io.open(fp, encoding="utf-8").read() + "\n"
print("      css da nap:", ", ".join(sheets))
common = ""
cls = set()
for grp in re.findall(r'class="([^"]+)"', src): cls |= set(grp.split())
for grp in re.findall(r"class='([^']+)'", js): cls |= set(grp.split())
nocss = sorted(c for c in cls if ("." + c) not in css and ("." + c) not in common)
ok(not nocss, "moi class co CSS (thieu: %s)" % nocss)

print()
print("=== KET QUA: %d dat / %d hong ===" % (0, len(fails)) if fails else "=== TAT CA DAT ===")
if fails:
    for f in fails: print(" - " + f)
    sys.exit(1)
