# -*- coding: utf-8 -*-
"""verify_prod_0813b.py — ĐO TRÊN BẢN THẬT sau lượt push 13/08/2026 (bản dựng .2):
sửa lỗi cửa hàng rỗng + thêm loại món hình dán.

    python scratchpad/verify_prod_0813b.py

Vì sao cần dù đã có ~30 bộ kiểm chạy ở máy: chúng chạy trên `127.0.0.1:8123`, tức
trên THƯ MỤC LÀM VIỆC. Bộ này trả lời một câu khác hẳn — **người dùng thật có nhận
được không**.

⚠️ Đo TRƯỚC khi Pages build xong thì mọi kết luận đều sai (06/08/2026 bản thật đứng
   ở bản cũ gần một ngày), nên nó kiểm số hiệu bản dựng TRƯỚC MỌI THỨ KHÁC.

⚠️ PHÉP ĐO QUAN TRỌNG NHẤT là mục [4]: mở CHÍNH `astroq.org/shop.html` rồi gieo
   `AstroQAuth` MUỘN (trong một `<script type="module">` thật) — đúng nhịp của
   `js/firebase-auth.js`. Đó là thứ tự đã làm cửa hàng rỗng với mọi người đã đăng
   nhập, và là thứ tự mà bộ `smoke_shop.py` cũ không bao giờ đo tới.
"""
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

SITE = "https://astroq.org"
WANT_VER = "2026.08.13.2"
DECALS = ["decal-comet", "decal-orbit", "decal-ringed", "decal-stars"]
ok_n, bad_n = 0, 0
FAILS = []

ITEMS = """[
  {id:"cockpit-cyan",kind:"theme",price:0},{id:"cockpit-amber",kind:"theme",price:60},
  {id:"cockpit-violet",kind:"theme",price:90},{id:"cockpit-mint",kind:"theme",price:120},
  {id:"cockpit-rose",kind:"theme",price:150},
  {id:"frame-steel",kind:"frame",price:0},{id:"frame-gold",kind:"frame",price:40},
  {id:"frame-nebula",kind:"frame",price:70},{id:"frame-ice",kind:"frame",price:100},
  {id:"decal-none",kind:"decal",price:0},{id:"decal-comet",kind:"decal",price:40},
  {id:"decal-orbit",kind:"decal",price:60},{id:"decal-ringed",kind:"decal",price:80},
  {id:"decal-stars",kind:"decal",price:110}
]"""

LATE_STUB = """
window.__A = {
  getShop: function(){ return Promise.resolve({ ok:true, data:{
    kinds:["theme","frame","decal"], items: %s, owned:["decal-comet"],
    equipped:{theme:"cockpit-cyan",frame:"frame-steel",decal:"decal-none"}, ship:"",
    wallet:{meteors:636} }}); },
  buyCosmetic:function(){return Promise.resolve({ok:false});},
  equipCosmetic:function(){return Promise.resolve({ok:false});},
  updateProfile:function(){return Promise.resolve({ok:false});}
};
var s=document.createElement('script'); s.type='module';
s.textContent="Object.defineProperty(window,'AstroQAuth',{configurable:true,get:function(){return window.__A;},set:function(){}});";
document.addEventListener('readystatechange',function(){
  if(document.readyState==='interactive' && !window.__inj){ window.__inj=true; document.head.appendChild(s); }
});
""" % ITEMS


def chk(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [ok]   {name}" + (f"  ({extra})" if extra else ""))
    else:
        bad_n += 1
        FAILS.append(name)
        print(f"  [HONG] {name}" + (f"  ({extra})" if extra else ""))


def head(t):
    print(f"\n=== {t} ===")


def fetch(path):
    req = urllib.request.Request(SITE + path, method="GET")
    req.add_header("User-Agent", "astroq-verify/1.0")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), b""
    except Exception as e:
        return 0, str(e), b""


def seed(decal):
    return ("localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-asteroids','636');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1');"
            "localStorage.setItem('astroq-user', JSON.stringify({"
            "  name:'Test', pilotName:'Test', uid:'u-test',"
            "  equipped:{theme:'cockpit-cyan',frame:'frame-steel',decal:'%s'},"
            "  ship:'Luna Mot'}));" % decal)


def main():
    head("[1] So hieu ban dung — do TRUOC moi thu khac")
    st, _, body = fetch("/js/ui-common.js")
    ver = ""
    if st == 200:
        m = re.search(rb'var VERSION = "([^"]+)"', body)
        ver = m.group(1).decode() if m else ""
    chk(ver == WANT_VER, f"ban that dang o ban dung {WANT_VER}", ver or f"status={st}")
    if ver != WANT_VER:
        print("\n  Pages CHUA build xong — dung lai, moi ket luan sau day deu vo nghia.")
        return 1

    head("[2] Ban sua LOI CUA HANG RONG co that tren Pages")
    st, ct, shop_src = fetch("/shop.html")
    chk(st == 200, "/shop.html tra 200", f"status={st}")
    s = shop_src.decode("utf-8", "replace")
    chk("function whenAuth(" in s, "shop.html co `whenAuth()` (cho SDK roi moi ket luan)")
    chk("whenAuth(2500" in s, "han cho la 2,5s, khong bi rut ngan")
    # Loi cu: hoi mot lan roi ket luan ngay.
    chk(not re.search(r'function load\(\)\{?\s*\n\s*var a = auth\(\);', s),
        "KHONG con nhanh hoi dong bo roi ket luan ngay")
    chk('loading:"' in s and 'empty:"' in s,
        "co ca hai cau noi that: dang tai / kho rong")

    head("[3] File cua hinh dan co that + MIME dung")
    for p in ["/css/cockpit.css", "/css/shop.css", "/js/cosmetics.js"]:
        st, ct, raw = fetch(p)
        chk(st == 200, f"{p} tra 200", f"status={st}")
        # ⚠️ MIME phai dung: ES module bi tu choi neu server tra text/plain; CSS sai
        #    MIME thi trinh duyet bo qua ca file. Day la thu PHAI DO, khong duoc doan.
        want = "css" if p.endswith(".css") else "javascript"
        chk(want in ct.lower(), f"{p} MIME dung ({want})", ct)
        txt = raw.decode("utf-8", "replace")
        if p == "/css/cockpit.css":
            miss = [d for d in DECALS if f'.cos-sw--{d}' not in txt]
            chk(not miss, "co o xem truoc cho ca 4 hinh dan", str(miss))
            miss2 = [d for d in DECALS if f'[data-decal="{d}"]' not in txt]
            chk(not miss2, "co ban ve cho ca 4 hinh dan", str(miss2))
            chk("pointer-events:none" in re.search(r'\.decal\{[^}]*\}', txt).group(0),
                ".decal khong nuot cu bam")
        if p == "/js/cosmetics.js":
            miss3 = [d for d in DECALS + ["decal-none"] if f'"{d}"' not in txt]
            chk(not miss3, "co TEN cho ca 5 mon", str(miss3))
            # Phan cong: server giu GIA, client giu TEN.
            chk(not re.search(r'\b(40|60|80|110)\b', txt),
                "js/cosmetics.js KHONG lo con so gia nao")

    with sync_playwright() as pw:
        br = pw.chromium.launch()

        head("[4] MO CHINH astroq.org/shop.html, gieo SDK MUON — phai hien du 14 mon")
        ctx = br.new_context(viewport={"width": 1440, "height": 1000})
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        pg.on("response", lambda r: errs.append("http %d %s" % (r.status, r.url))
              if r.status >= 400 else None)
        pg.add_init_script(seed("decal-none"))
        pg.add_init_script(LATE_STUB)
        pg.goto(SITE + "/shop.html", wait_until="load")
        try:
            pg.wait_for_selector("#kinds .citem", timeout=15000)
        except Exception:
            st2 = pg.evaluate("() => ({auth: !!window.AstroQAuth,"
                              " txt: ((document.getElementById('offline-txt')||{}).textContent||'')})")
            chk(False, "cua hang hien mon voi SDK nap muon",
                "0 mon sau 15s · AstroQAuth=%s · %r" % (st2["auth"], st2["txt"][:60]))
            ctx.close(); br.close()
            print(f"\nKET QUA TREN BAN THAT: {ok_n} dat / {bad_n} hong")
            return 1
        n_it = pg.locator("#kinds .citem").count()
        n_sec = pg.locator("#kinds section").count()
        chk(n_it == 14, "hien du 14 mon (LOI CUA HANG RONG DA HET)", f"{n_it} mon")
        chk(n_sec == 3, "du 3 khoi loai mon", f"{n_sec} khoi")
        chk(not pg.locator("#offline").is_visible(), "KHONG con dai 'can dang nhap'")
        names = pg.eval_on_selector_all("#kinds .cnm", "e=>e.map(x=>x.textContent)")
        for nm in ["Chưa dán gì", "Sao Chổi Bay", "Vòng Quỹ Đạo",
                   "Hành Tinh Có Vành", "Chùm Sao Nhỏ"]:
            chk(nm in names, f"co mon '{nm}'")
        drawn = pg.evaluate("""() => {
          const out = {};
          document.querySelectorAll('[class*="cos-sw--decal-"]').forEach(el => {
            const id = [...el.classList].find(c => c.startsWith('cos-sw--decal-'));
            const px = s => parseFloat(s)||0;
            const b = getComputedStyle(el,'::before'), a = getComputedStyle(el,'::after');
            out[id] = Math.round(px(b.width)*px(b.height) + px(a.width)*px(a.height));
          });
          return out;
        }""")
        for d in DECALS:
            chk(drawn.get("cos-sw--" + d, 0) > 200, f"o xem truoc {d} VE RA THAT",
                f"{drawn.get('cos-sw--' + d, 0)} px2")
        chk(drawn.get("cos-sw--decal-none", -1) == 0, "o 'chua dan gi' de trong")
        chk(not errs, "/shop.html: 0 loi, 0 asset hong", "; ".join(errs[:2])[:120])
        ctx.close()

        head("[5] Hinh dan HIEN RA o buong lai (dashboard) tren ban that")
        for dec in ["decal-none"] + DECALS:
            ctx = br.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            errs2 = []
            pg.on("pageerror", lambda e: errs2.append(str(e)))
            pg.add_init_script(seed(dec))
            pg.goto(SITE + "/dashboard.html", wait_until="load")
            pg.wait_for_selector(".statusbar", timeout=20000)
            pg.wait_for_timeout(900)
            r = pg.evaluate("""() => {
              const d = document.querySelector('.decal');
              if (!d) return {err:'khong co .decal'};
              const cs = getComputedStyle(d), b = d.getBoundingClientRect();
              const px = s => parseFloat(s)||0;
              const pb = getComputedStyle(d,'::before'), pa = getComputedStyle(d,'::after');
              const hit = b.width ? document.elementFromPoint(b.left+b.width/2, b.top+b.height/2) : null;
              return { display: cs.display, w: Math.round(b.width),
                       drawn: Math.round(px(pb.width)*px(pb.height) + px(pa.width)*px(pa.height)),
                       hitIsDecal: !!(hit && hit.classList && hit.classList.contains('decal')),
                       overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth) };
            }""")
            if r.get("err"):
                chk(False, f"{dec}: co the .decal", r["err"]); ctx.close(); continue
            if dec == "decal-none":
                chk(r["display"] == "none" and r["w"] == 0,
                    "chua dan gi: KHONG chiem cho nao", f"display={r['display']}")
            else:
                chk(r["display"] != "none" and r["w"] >= 20 and r["drawn"] > 100,
                    f"{dec}: hien ra + co ve hinh", f"{r['w']}px · ve {r['drawn']}px2")
            chk(not r["hitIsDecal"], f"{dec}: khong nuot cu bam")
            chk(r["overflow"] == 0, f"{dec}: trang khong tran ngang", f"{r['overflow']}px")
            chk(not errs2, f"{dec}: 0 loi trang", "; ".join(errs2[:1])[:100])
            ctx.close()

        br.close()

    print("\n" + "=" * 58)
    print(f"KET QUA TREN BAN THAT: {ok_n} dat / {bad_n} hong")
    for f in FAILS:
        print("  - " + f)
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
