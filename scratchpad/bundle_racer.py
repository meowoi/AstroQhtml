# -*- coding: utf-8 -*-
r"""Đóng `game-racer.html` thành MỘT file tự chứa để chủ dự án bấm là chơi.

⚠️⚠️ ĐÂY LÀ BẢN THỬ, KHÔNG PHẢI BẢN THẬT — và phải nói ra điều đó trên chính trang.
   Nó là một BẢN SAO đã gộp: CSS/JS nhúng thẳng, ảnh và phông thành data URI, ví
   Thiên thạch tím nạp sẵn, và các nút đi sang trang khác bị chặn (trong bản gộp
   không có `games.html` hay `dashboard.html` nào để đi tới). Ba thứ đó KHÔNG có ở
   bản thật, nên một bản gộp không thể dùng để kết luận về bản thật — muốn xem
   đúng thứ người dùng chạy thì mở `http://127.0.0.1:8123/game-racer.html`.

⚠️ KHÔNG SỬA MỘT DÒNG LUẬT CHƠI NÀO. Bộ này chỉ làm năm việc: nhúng phụ thuộc ·
   nạp ví · chặn các nút điều hướng · dán một dải nhãn · và VÁ HAI CHỖ SUY RA
   TỪ ĐƯỜNG DẪN TRANG (`mateUrl` và `var key` của `js/game-shell.js`) — bản gộp
   không nằm ở `game-racer.html` nên hai chỗ đó tự hỏng câm. Mọi thứ khác lấy
   nguyên văn từ file game, nên bản thử và bản thật vẽ ra cùng một sân.

⚠️ HỆ HÌNH LÀ HỆ CÓ SẴN CỦA DỰ ÁN (`CLAUDE.md` mục 1: buồng lái sci-fi, nền deep
   space, neon cyan #38bdf8, tím #8f7bff, sun #ffcf6b; phông Space Grotesk + Inter
   + Share Tech Mono tự host). Dải nhãn dùng đúng tông HỔ PHÁCH mà dự án đã dùng
   cho mọi thứ "không phải bản thật" (`.standby` · nhãn "MÔ PHỎNG" của
   `game-recycle`/`game-units`/`mission-orbit`) — không đặt ra một bảng màu thứ hai.
"""
import base64
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SRC = "game-racer.html"
OUT = os.path.join("scratchpad", "racer-test-build.html")
WALLET = 240          # đủ 60 lượt — người thử không phải nghĩ về ví

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp",
        ".woff2": "font/woff2"}

ASSETS = ["img/tt.png", "img/luna-side.png",
          "img/racer/rival-blaze.png", "img/racer/rival-ember.png",
          "img/racer/rival-dust.png", "img/racer/rock.png",
          "img/racer/fuel-can.png",
          "img/mate/comet-idle.png", "img/mate/comet-cheer.png",
          "img/mate/comet-oops.png"]
# Ảnh nhúng bằng phép tìm-thế đường dẫn (không đi qua bảng `__TESTASSET`).
# ⚠️ Thiếu một file ở đây thì bản gộp xin nó qua mạng và CSP của Artifact chặn —
#    hàng rào `stray` ở mục 7 bắt được, đừng bỏ hàng rào đó.
INLINE = ["img/tt.png", "img/luna-side.png",
          "img/racer/rival-blaze.png", "img/racer/rival-ember.png",
          "img/racer/rival-dust.png", "img/racer/rock.png",
          "img/racer/fuel-can.png"]


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    raw = io.open(path, "rb").read()
    return "data:%s;base64,%s" % (MIME[ext], base64.b64encode(raw).decode("ascii"))


def read(path):
    return io.open(path, encoding="utf-8", newline=None).read()


html = read(SRC)

# ── 1. Nhúng phông vào css/fonts.css ────────────────────────────────
fonts_css = read("css/fonts.css")
# ⚠️ `css/fonts.css` viết `url("../fonts/x.woff2")` CÓ DẤU NHÁY. Bản đầu của bộ
#    này khớp `url\(\.\./…\)` không nháy nên nhúng được 0 phông mà vẫn chạy tiếp
#    — bản gộp khi đó xin phông từ đường dẫn tương đối và CSP của Artifact chặn
#    hẳn, tức cả trang rơi về phông hệ thống mà không có gì báo lỗi. Nay có
#    hàng rào đếm số phông ở dưới.
n_font = 0
for m in sorted(set(re.findall(r'url\(\s*["\']?\.\./(fonts/[^)"\']+\.woff2)',
                               fonts_css))):
    fonts_css = re.sub(r'url\(\s*["\']?\.\./' + re.escape(m) + r'["\']?\s*\)',
                       "url(%s)" % data_uri(m), fonts_css)
    n_font += 1
print("  phong nhung: %d file" % n_font)
assert n_font >= 5, "chi nhung duoc %d phong — kiem lai css/fonts.css" % n_font
assert "../fonts/" not in fonts_css, "van con duong dan phong ben ngoai"

# ── 2. Nhúng CSS theo ĐÚNG thứ tự thẻ <link> ───────────────────────
def css_repl(m):
    href = m.group(1)
    body = fonts_css if href == "css/fonts.css" else read(href)
    # Cùng cái bẫy của <script> (xem `js_repl`): `</style>` trong một chú thích
    # CSS cũng đóng khối. Hôm nay 4 file không có chỗ nào, nhưng chặn sẵn.
    body = body.replace("</style", "<\\/style")
    return "<style>\n/* ==== %s ==== */\n%s\n</style>" % (href, body)


html, n_css = re.subn(r'<link rel="stylesheet" href="(css/[^"]+)"\s*/?>',
                      css_repl, html)
print("  CSS nhung: %d file" % n_css)

# ── 3. Nhúng JS theo ĐÚNG thứ tự thẻ <script src> ──────────────────
def js_repl(m):
    src = m.group(1)
    body = read(src)
    # ⚠️⚠️ BỘ PHÂN TÍCH HTML ĐÓNG KHỐI <script> Ở CHUỖI `</script>` ĐẦU TIÊN,
    #    KỂ CẢ KHI NÓ NẰM TRONG CHÚ THÍCH HAY TRONG MỘT CHUỖI JS. Bốn file nhúng
    #    có 5 chỗ như thế (chú thích đầu `js/ui-common.js` ghi lại thứ tự nạp
    #    `<script src="js/icons.js"></script>`), nên bản gộp đầu tiên VỠ THẬT:
    #    khối script đóng ngay giữa chú thích, dòng `<script src="js/ui-common.js">`
    #    thành một thẻ THẬT và bị 404, phần mã còn lại bị đọc như văn bản HTML
    #    → `SyntaxError: Invalid or unexpected token`, ví hiện 0 tt, `window.__racer`
    #    không bao giờ tồn tại. Chỉ mở trên trình duyệt mới thấy; phép quét tĩnh
    #    của bộ này thì không.
    #    `<\/script` là cách viết an toàn ở mọi ngữ cảnh: trong chú thích nó vô
    #    hại, trong chuỗi JS thì `\/` chính là `/`.
    body = body.replace("</script", r"<\/script")
    return "<script>\n/* ==== %s ==== */\n%s\n</script>" % (src, body)


html, n_js = re.subn(r'<script src="((?:js/)?[^"]+\.js)"></script>', js_repl, html)
print("  JS nhung:  %d file" % n_js)

# ── 4. Ảnh → data URI ──────────────────────────────────────────────
uri = {}
for a in ASSETS:
    uri[a] = data_uri(a)
for a in INLINE:
    html = html.replace(a, uri[a])
print("  anh nhung: %d file" % len(ASSETS))

# Linh vật: `mateUrl` GHÉP chuỗi (`dir + state + ".png"`) nên không thay được bằng
# tìm-thế. Trỏ nó vào một bảng tra — đây là chỗ duy nhất mã bị viết lại.
old_mate = 'function mateUrl(kind, state) { return MASCOT[kind].dir + state + ".png"; }'
assert html.count(old_mate) == 1, "khong tim thay mateUrl"
html = html.replace(old_mate,
                    'function mateUrl(kind, state) {\n'
                    '    var p = MASCOT[kind].dir + state + ".png";\n'
                    '    return (window.__TESTASSET && window.__TESTASSET[p]) || p;\n'
                    '  }', 1)

# ⚠️⚠️ `js/game-shell.js` SUY TÊN GAME TỪ ĐƯỜNG DẪN TRANG
#    (`location.pathname.split("/").pop().replace(".html","")` → tra bảng `MATE`).
#    Bản gộp không nằm ở `game-racer.html` — trên Artifact đường dẫn là một URL
#    hoàn toàn khác — nên `MATE[key]` là `undefined`, `mountSide()` thoát sớm và
#    **cả console phải với Comet không được dựng**. Không lỗi, không cảnh báo:
#    người thử chỉ thấy thiếu hẳn linh vật, tức thiếu đúng thứ vừa làm hôm nay
#    (C2 — linh vật phản ứng). Chỉ mở trên trình duyệt mới phát hiện.
old_key = ('var key = (location.pathname.split("/").pop() || "")'
           '.replace(".html", "");')
assert html.count(old_key) == 2, "khong tim thay 2 cho suy ten game (%d)" % \
    html.count(old_key)
html = html.replace(old_key, 'var key = window.__TESTGAME || '
                    '(location.pathname.split("/").pop() || "")'
                    '.replace(".html", "");')

# ── 5. Bỏ vỏ tài liệu — Artifact tự bọc <!doctype>/<head>/<body> ───
title = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
# Bỏ tiền tố thương hiệu: tên artifact phải là TÊN của chính trang, và trong một
# thư viện nhiều artifact thì "AstroQ — …" ở mọi tiêu đề là phần không phân biệt.
title = re.sub(r"^AstroQ\s*[—\-–]\s*", "", title)
inner = html
for pat in (r"<!DOCTYPE[^>]*>", r"</?html[^>]*>", r"</?head>", r"</?body[^>]*>",
            r"<meta[^>]*>", r"<link[^>]*>", r"<title>.*?</title>"):
    inner = re.sub(pat, "", inner, flags=re.S)
inner = inner.strip()

# ── 6. Lớp bọc bản thử: nạp ví TRƯỚC economy.js ────────────────────
PRE = """<title>%s</title>
<script>
/* ⚠️ NẠP VÍ TRƯỚC `economy.js`. Ví của một trình duyệt mới là 0 tt (đúng thiết kế:
   `Economy.DEFAULT_BALANCE` phải bằng 0 cho khớp ví server), mà một lượt tốn 4 tt
   — nên bản thử không nạp sẵn thì mở lên chỉ thấy màn "Chưa đủ Thiên thạch tím".
   ⚠️ CHỈ nạp khi khoá còn TRỐNG: ghi đè mỗi lần tải là xoá mất số dư người thử
      vừa kiếm được trong chính bản thử này. */
try{
  if(localStorage.getItem("astroq-asteroids") === null)
    localStorage.setItem("astroq-asteroids", "%d");
}catch(e){}
/* Tên game cho `js/game-shell.js` — xem lý do ở phần vá `var key` trong bộ gộp. */
window.__TESTGAME = "game-racer";
window.__TESTASSET = %s;
</script>
""" % (title, WALLET, "{" + ",".join(
    '"%s":"%s"' % (k, v) for k, v in uri.items() if k.startswith("img/mate/")) + "}")

BANNER = """
<div class="tb-note" role="note">
  <span class="tb-tag">BẢN THỬ</span>
  <span>Bản gộp để chơi thử Đường Đua Sao Chổi — ví Thiên thạch tím đã nạp sẵn,
        không cần đăng nhập. Đây <b>không phải</b> bản thật trên astroq.org.</span>
</div>
"""

POST = """
<style>
/* ==== lớp bọc bản thử ====
   Dùng đúng tông HỔ PHÁCH mà dự án đã dành cho mọi thứ "không phải bản thật"
   (`.standby` ở dashboard · nhãn "MÔ PHỎNG" ở game-recycle/game-units) và đúng
   phông mono của hệ (`--font-mono`), nên nó đọc ra như một phần của app chứ không
   như một cái nhãn dán ngoài. Cố ý mỏng và neo ĐÁY: sân game là thứ đang được
   xem, một dải trên đầu sẽ đẩy cả bố cục xuống và làm hỏng đúng thứ cần thử. */
.tb-note{
  position:fixed;left:12px;right:12px;bottom:10px;z-index:80;
  display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;
  margin:0 auto;max-width:760px;padding:8px 14px;
  border:1px dashed rgba(255,207,107,.55);border-radius:12px;
  background:rgba(14,20,44,.9);backdrop-filter:blur(8px);
  font-family:var(--font-body,system-ui),system-ui,sans-serif;
  font-size:12.5px;line-height:1.45;color:var(--ink-soft,#c8d4f2);
  text-align:center;pointer-events:none;
}
.tb-tag{
  flex:none;font-family:var(--font-mono,ui-monospace),ui-monospace,monospace;
  font-size:10px;letter-spacing:.14em;color:#ffcf6b;
  border:1px solid rgba(255,207,107,.5);border-radius:6px;padding:2px 7px;
}
.tb-note b{color:#ffcf6b;font-weight:600;}
@media (max-width:560px){ .tb-note{font-size:11.5px;bottom:6px;} }
</style>
<script>
/* ⚠️ CHẶN BA NÚT ĐI SANG TRANG KHÁC. Bản gộp chỉ có một trang, nên `games.html`
   và `dashboard.html` không tồn tại — để nguyên thì người thử bấm vào và rơi vào
   một trang trắng, tưởng game vỡ. Bắt ở pha CAPTURE + `stopPropagation` để chặn
   trước handler mà trang tự gắn (handler đó ở pha bubble), và NÓI RA lý do thay vì
   im lặng: một cái nút bấm không có gì xảy ra thì người dùng tưởng là lỗi. */
(function(){
  var DEAD = ["back","hub-btn","home-btn","pause-hub","need-hub","need-quiz"];
  document.addEventListener("click", function(e){
    var b = e.target.closest ? e.target.closest("button,a") : null;
    if(!b || DEAD.indexOf(b.id) < 0) return;
    e.preventDefault(); e.stopPropagation();
    if(window.AstroQ && AstroQ.makeToast) {
      var t = document.getElementById("toast");
      if(t) AstroQ.makeToast(t)("Bản thử chỉ có màn đua này — mở bản thật để đi sang khu khác.", "bad");
    }
  }, true);
})();
</script>
"""

out = PRE + inner + BANNER + POST
io.open(OUT, "w", encoding="utf-8", newline="\n").write(out)

# ── 7. Hàng rào: bản gộp KHÔNG được còn phụ thuộc ngoài ────────────
# ⚠️ QUÉT THEO CẤU TẠO CỦA MARKUP/CSS, ĐỪNG QUÉT `src=` TRÊN VĂN BẢN THÔ.
#    Bản đầu của bộ này tìm mọi `src=|href=` trong cả file gộp, nên nó bắt luôn
#    hai dòng trong KHỐI GHI CHÚ ở đầu `js/ui-common.js` (chúng ghi lại thứ tự
#    nạp `<script src="js/icons.js">`) và báo "còn phụ thuộc ngoài" oan — đúng
#    lớp lỗi "đếm cả chữ trong ghi chú của chính mình" mà CLAUDE.md đã ghi nhiều
#    lần. Nó cũng cắt sai ở `'<img … src="' + SITE + 'img/tt.png"'`: phép ghép
#    chuỗi làm khớp bắt đầu ở `' + SITE + '` nên chuỗi `data:` không được loại
#    trừ, và nó in ra cả một data URI 19 KB.
#    ⚠️ VÀ ĐỪNG CHỮA BẰNG CÁCH BÓC `/* … */` TRÊN CẢ FILE GỘP: đã thử, không
#    chạy được. Một dấu `*/` nằm trong CHUỖI ở đâu đó làm lệch cặp ngoặc chú
#    thích, nên `re.sub(r"/\*.*?\*/")` cắt sai chỗ và mấy thẻ `<script src=…>`
#    trong chú thích vẫn sống sót (đã đo: `js/icons.js` ở dòng 890 của bản gộp
#    nằm TRONG một khối chú thích mà vẫn bị bắt). Đó cũng là điểm mù của
#    `_no_comments` mà CLAUDE.md đã ghi.
# ⇒ Quét theo PHẠM VI thay vì theo chú thích: phần MARKUP của tài liệu là phần
#   nằm NGOÀI mọi khối <script>/<style>, nên bỏ hẳn ruột hai loại khối đó rồi
#   mới tìm thẻ. Chú thích của các file nhúng đều nằm bên trong ruột đó.
# ⚠️ Đây chỉ là hàng rào TĨNH. Bằng chứng thật là mở bản gộp trên Chromium rồi
#   đếm số request KHÔNG phải `data:` — xem `scratchpad/probe_racer_bundle.py`.
doc = re.sub(r"<script\b[^>]*>.*?</script>", " ", out, flags=re.S | re.I)
doc = re.sub(r"<style\b[^>]*>.*?</style>", " ", doc, flags=re.S | re.I)
doc = re.sub(r"<!--.*?-->", " ", doc, flags=re.S)


def _real(v):
    """Bỏ khớp là phép ghép chuỗi JS (giá trị thật chỉ có lúc chạy)."""
    return bool(v) and not v.startswith("#") and "+" not in v and "(" not in v


tags = [x for x in re.findall(
    r'<(?:script|link|img|source|video|audio|iframe)\b[^>]*?'
    r'(?:src|href|srcset)="((?!data:|https://fonts\.)[^"]*)"', doc, re.I)
    if _real(x)]
urls = [u for u in re.findall(
    r'url\(\s*["\']?((?!data:|https://fonts\.)[^)"\']+)', doc) if _real(u)]
# Hàng rào thêm: markup của tài liệu không còn một đường dẫn ảnh tương đối nào.
stray = [m for m in re.findall(
    r'''["'\(]((?:img|3d|ava|background|fonts)/[^"'\)]+)''', doc)]
assert not stray, "con duong dan anh tuong doi trong markup: %s" % stray[:5]
left = sorted(set(tags + urls))
print("\n  co %d ky tu (%.0f KB)" % (len(out), len(out) / 1024))
print("  phu thuoc ngoai con lai: %s"
      % ([x[:60] for x in left[:5]] if left else "KHONG"))
assert not left, "van con phu thuoc ngoai: %s" % [x[:60] for x in left[:5]]
for bad in ("<!DOCTYPE", "<html", "<head>", "<body"):
    assert bad not in out, "con vo tai lieu: " + bad
print("  -> %s" % OUT)
