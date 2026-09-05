# -*- coding: utf-8 -*-
"""
probe_engaged_beacon.py -- BEACON "O LAI DU LAU": do TOI TAN DynamoDB, khong chi toi mep mang.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/probe_engaged_beacon.py

VIEC 4 CUA BAN PHAN TICH 04/09/2026
-----------------------------------
14 ngay do duoc **828 khach mang nhan va 4 luot dang ky** -- ~99,6% mat TRUOC form.
Voi mot con so `n` duy nhat thi *"mo ra roi dong ngay"* va *"co doc ma van khong dang
ky"* doc ra Y HET nhau, ma cai thu nhat phai sua QUANG CAO con cai thu hai phai sua
TRANG. Su kien `ev="engaged"` la cho ranh gioi do duoc ghi lai.

⚠️⚠️ DO DEN DB, KHONG DO DEN MEP MANG. Bai hoc da tra gia o `probe_visit_beacon.py`:
   ban dau cua bo do do chay cong 8132 va chi kiem "co ban ra 1 request" -- no XANH
   trong khi **0 ban ghi** vao duoc DynamoDB, vi `ALLOWED_ORIGINS` khong co cong do
   nen preflight bi CORS chan. Bo nay chay cong **8000** va moi phep kiem doi chieu
   con so THAT trong DynamoDB.

⚠️ NHAN TEST `zzeng*`, TUYET DOI KHONG DUNG NHAN THAT. `finally` xoa ban ghi test.

⚠️ MAY CHAY O NHA VAN DUNG DYNAMODB THAT (appsettings.Development.json ghi ro).

Bay dieu bo nay giu:
  ① khach mang nhan o lai 10 giay  -> ban `engaged`, DB co CA `n` LAN `e`
  ② cuon qua man dau               -> ban SOM, khong doi het 10 giay
  ③ tin hieu tab AN (mo phong)     -> KHONG ban; quay lai thi CONG DON, khong dat lai
  ④ khach vao thang (khong nhan)   -> 0 request, ke ca sau 12 giay
  ⑤ khach da bao roi, nap lai      -> KHONG dem doi
  ⑥ client CU (khong gui `ev`)     -> server van cong `n`, khong loi
  ⑦ ban ghi chi co luot mo trang   -> KHONG co thuoc tinh `e` (= "chua do", khac 0)
"""
import sys, os, threading, http.server, socketserver, functools, datetime, time
sys.stdout.reconfigure(encoding="utf-8")
import json, urllib.request
from playwright.sync_api import sync_playwright
import boto3

ROOT = os.getcwd()
TABLE = "astroq-main"
DAY = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
ddb = boto3.client("dynamodb")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


class Q(socketserver.TCPServer):
    allow_reuse_address = True


srv = Q(("127.0.0.1", 8000), functools.partial(H, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:8000"
API = "http://localhost:5080"

ok = bad = 0
LABELS = []          # nhan test da dung -> don o `finally`


def check(l, c, d=""):
    global ok, bad
    if c:
        ok += 1; print("  [OK]   %s%s" % (l, "  (%s)" % d if d else ""))
    else:
        bad += 1; print("  [HONG] %s%s" % (l, "  (%s)" % d if d else ""))


def item_of(label):
    """Ban ghi bo dem cua (hom nay x nhan), hoac None khi chua co."""
    r = ddb.get_item(TableName=TABLE,
                     Key={"PK": {"S": "VISIT#" + DAY}, "SK": {"S": "SRC#" + label}})
    return r.get("Item")


def nums(label):
    """(n, e) -- `None` nghia la THUOC TINH KHONG CO, khac han 0. Ranh gioi nay
       chinh la thu muc [7] do, va la ly do trang bao cao in '—' chu khong in '0'."""
    it = item_of(label)
    if not it:
        return (None, None)
    g = lambda k: int(it[k]["N"]) if k in it else None
    return (g("n"), g("e"))


def label_of(tag):
    lb = "zzeng%s/paid/probe" % tag
    if lb not in LABELS:
        LABELS.append(lb)
    return lb


def qs(tag):
    return "?utm_source=zzeng%s&utm_medium=paid&utm_campaign=probe" % tag


def new_page(b, ctx=None):
    ctx = ctx or b.new_context()
    pg = ctx.new_page()
    pg.add_init_script("try{localStorage.setItem('astroq-api','%s')}catch(e){}" % API)
    return ctx, pg


def watch(pg):
    """Ghi lai moi request /visit KEM THAN cua no -- phai biet lo nao la `engaged`."""
    seen = []
    def on_req(r):
        if "/visit" not in r.url or r.method != "POST":
            return
        try:
            seen.append(json.loads(r.post_data or "{}"))
        except Exception:
            seen.append({})
    pg.on("request", on_req)
    return seen


try:
    with sync_playwright() as p:
        b = p.chromium.launch()

        # ═══════════ [1] O LAI 10 GIAY -> ban `engaged` ═══════════
        print("\n=== [1] Khach mang nhan O LAI 10 giay: DB co CA `n` LAN `e` ===")
        LB = label_of("stay")
        n0, e0 = nums(LB)
        ctx, pg = new_page(b)
        seen = watch(pg)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        codes = []
        pg.on("response", lambda r: codes.append(r.status) if "/visit" in r.url else None)
        pg.goto(BASE + "/index.html" + qs("stay"), wait_until="load")
        pg.wait_for_timeout(3000)
        early = len(seen)
        check("chua du 10 giay thi CHUA ban `engaged`",
              early == 1 and seen[0].get("ev") is None,
              "%d request, than=%s" % (early, seen))
        pg.wait_for_timeout(9000)                       # tong ~12 giay
        check("du 10 giay thi ban dung 1 lan nua", len(seen) == 2,
              "%d request" % len(seen))
        check("lo thu hai mang ev='engaged'",
              len(seen) == 2 and seen[1].get("ev") == "engaged", str(seen[-1:]))
        check("server tra 204 ca hai lo (khong bi CORS chan)",
              codes == [204, 204], "ma phan hoi=%s" % codes)
        n1, e1 = nums(LB)
        # ⚠️ CA HAI CON SO TREN CUNG MOT BAN GHI. Tach thanh hai ban ghi la nhan doi
        #    so item roi phai ghep lai luc doc, va moi cho doc thieu mot ben hong im lang.
        check("DB: `n` cong 1", n1 == (n0 or 0) + 1, "%s -> %s" % (n0, n1))
        check("DB: `e` cong 1", e1 == (e0 or 0) + 1, "%s -> %s" % (e0, e1))
        check("0 loi trang", not errs, str(errs[:1]))
        ctx.close()

        # ═══════════ [2] CUON QUA MAN DAU -> ban SOM ═══════════
        # ⚠️ HAI DIEU KIEN, LAY CAI NAO TOI TRUOC. Chi do thoi gian thi nguoi doc luot
        #    nhanh roi cuon xuong bi bo sot; day la nhanh con lai.
        print("\n=== [2] Cuon qua man dau: ban SOM, khong doi het 10 giay ===")
        LB = label_of("scroll")
        n0, e0 = nums(LB)
        ctx, pg = new_page(b)
        seen = watch(pg)
        pg.goto(BASE + "/index.html" + qs("scroll"), wait_until="load")
        pg.wait_for_timeout(1200)
        check("truoc khi cuon: chua ban `engaged`",
              not any(x.get("ev") == "engaged" for x in seen), str(seen))
        pg.evaluate("()=>window.scrollTo(0, window.innerHeight)")
        pg.wait_for_timeout(2500)                        # van chua toi 10 giay
        check("cuon xong la ban ngay (khong doi 10 giay)",
              any(x.get("ev") == "engaged" for x in seen), str(seen))
        n1, e1 = nums(LB)
        check("DB: `e` cong 1", e1 == (e0 or 0) + 1, "%s -> %s" % (e0, e1))
        ctx.close()

        # ═══════════ [3] TAB AN -> dong ho dung ═══════════
        # ⚠⚠ PHEP KIEM DANG GIA NHAT CUA BO NAY. Link mo trong tab nen (bam giua chuot,
        #    hoac trinh duyet tai truoc) se du 10 giay ma KHONG AI NHIN -- tuc bom thang
        #    vao dung con so dung de ket luan "trang giu duoc nguoi". Thieu phep kiem nay
        #    thi hong hoan toan im lang: con so van len, chi la len sai.
        #
        # ⚠⚠ DAY LA MO PHONG TIN HIEU, KHONG PHAI TAB AN THAT -- va phai noi ro ra.
        #    Da thu CA HAI duong an tab that va CA HAI deu khong dung duoc:
        #      · `Emulation.setPageVisibilityOverride` -- CDP da BO lenh nay
        #        ("'Emulation.setPageVisibilityOverride' wasn't found");
        #      · mo mot tab khac roi `bring_to_front()` -- Playwright CO Y giu moi trang
        #        o trang thai visible de chung khong bi trinh duyet ham, nen trang bi che
        #        VAN bao `visibilityState = "visible"` (do duoc o ca headless lan headed).
        #    Nen bo nay ghi de `document.hidden` / `visibilityState` roi phat dung su kien
        #    `visibilitychange` -- tuc do DUNG HAI THU MA MA NGUON DOC. No chung minh
        #    duoc: dong ho dung khi tin hieu bao an, chay tiep khi bao hien, va cong don
        #    phan da xem. No KHONG chung minh duoc trinh duyet that phat tin hieu do dung
        #    luc; phan ay dua vao hop dong Page Visibility API.
        print("\n=== [3] Tab AN (mo phong tin hieu): dong ho dung khi khong ai nhin ===")
        LB = label_of("hidden")
        ctx = b.new_context()
        pg = ctx.new_page()
        pg.add_init_script("try{localStorage.setItem(\'astroq-api\',\'%s\')}catch(e){}" % API)
        pg.add_init_script("""(function(){
          var h = false;
          Object.defineProperty(Document.prototype, 'hidden', {
            configurable: true, get: function(){ return h; } });
          Object.defineProperty(Document.prototype, 'visibilityState', {
            configurable: true, get: function(){ return h ? 'hidden' : 'visible'; } });
          window.__setHidden = function(v){
            h = !!v;
            document.dispatchEvent(new Event('visibilitychange'));
          };
        })();""")
        seen = watch(pg)
        pg.goto(BASE + "/index.html" + qs("hidden"), wait_until="load")
        pg.wait_for_timeout(1500)
        pg.evaluate("()=>window.__setHidden(true)")
        check("tin hieu bao tab dang an", pg.evaluate("()=>document.visibilityState") == "hidden",
              pg.evaluate("()=>document.visibilityState"))
        pg.wait_for_timeout(14000)                  # qua han 10 giay MA DANG AN
        check("KHONG ban `engaged` trong suot 14 giay tab an",
              not any(x.get("ev") == "engaged" for x in seen), str(seen))
        _n, _e = nums(LB)
        check("DB: `e` van CHUA CO (chua do, khac han 0)", _e is None, "e=%s" % _e)

        # ⚠ VA PHAI CHAY TIEP KHI QUAY LAI, khong phai chet han: nguoi mo tab nen roi
        #    vai phut sau moi doc la mot khach that, va bo sot ho la lech dung chieu
        #    nguoc lai.
        # ⚠⚠ CONG DON PHAN DA XEM, KHONG DAT LAI DONG HO. Da xem 1,5 giay truoc khi an
        #    nen chi con ~8,5 giay; do o day bang cach doi 11 giay roi doi chieu -- neu ma
        #    nguon dat lai dong ho tu dau thi van kip, nhung phep kiem thoi gian ngay duoi
        #    moi la cho bat duoc.
        pg.evaluate("()=>window.__setHidden(false)")
        t0 = time.monotonic()
        for _ in range(120):
            if any(x.get("ev") == "engaged" for x in seen):
                break
            pg.wait_for_timeout(250)
        waited = time.monotonic() - t0
        check("quay lai tab thi dong ho chay tiep va ban duoc",
              any(x.get("ev") == "engaged" for x in seen), "sau %.1f giay" % waited)
        # ⚠ NGUOI CHUYEN TAB QUA LAI VAI LAN MA LAN NAO CUNG DAT LAI DONG HO thi khong
        #    bao gio toi dich -- tuc moi khach vua doc vua lam viec khac deu roi khoi phep
        #    do. Da xem 1,5 giay thi phan con lai phai < 10 giay, va do duoc la 9,x.
        check("cong don phan da xem (khong dat lai du 10 giay)", waited < 9.5,
              "%.1f giay < 9,5" % waited)
        _n, _e = nums(LB)
        check("DB: `e` cong 1 sau khi quay lai", _e == 1, "e=%s" % _e)
        ctx.close()

        # ═══════════ [4] KHACH VAO THANG -> 0 request ═══════════
        # ⚠️ DIEU KIEN DE THEM PHEP DO NAY MA KHONG PHA LOI HUA O DAU js/utm.js:
        #    "0 byte tai them, 0 request, 0 cookie, 0 ben thu ba" cho khach khong nhan.
        print("\n=== [4] Khach VAO THANG: 0 request ke ca sau 12 giay ===")
        ctx, pg = new_page(b)
        seen = watch(pg)
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.evaluate("()=>window.scrollTo(0, window.innerHeight)")
        pg.wait_for_timeout(12000)
        check("KHONG gui request nao", len(seen) == 0, "%d request" % len(seen))
        ctx.close()

        # ═══════════ [5] DA BAO ROI -> khong dem doi ═══════════
        # ⚠️ DEM KHACH, KHONG DEM PHIEN. Co nam trong `localStorage` cung ban ghi
        #    cham-dau-tien (60 ngay), nen mot nguoi doc ky ba lan trong ba ngay van chi
        #    duoc dem MOT -- dung don vi cua `n` de `e/n` la mot ti le co nghia.
        print("\n=== [5] Cung mot khach nap lai: khong dem doi ===")
        LB = label_of("twice")
        ctx = b.new_context()
        _, pg = new_page(b, ctx)
        seen = watch(pg)
        pg.goto(BASE + "/index.html" + qs("twice"), wait_until="load")
        pg.evaluate("()=>window.scrollTo(0, window.innerHeight)")
        pg.wait_for_timeout(2500)
        first = len(seen)
        pg.goto(BASE + "/index.html" + qs("twice"), wait_until="load")
        pg.evaluate("()=>window.scrollTo(0, window.innerHeight)")
        pg.wait_for_timeout(2500)
        check("nap lan 2 KHONG gui them", len(seen) == first,
              "lan1=%d tong=%d" % (first, len(seen)))
        n1, e1 = nums(LB)
        check("DB: `n`=1 va `e`=1 (khong phai 2)", (n1, e1) == (1, 1),
              "n=%s e=%s" % (n1, e1))
        ctx.close()
        b.close()

    # ═══════════ [6] CLIENT CU (khong gui `ev`) ═══════════
    # ⚠️ Ban cu con nam trong may nguoi dung va service worker con giu cache. Tra 400
    #    cho no la bien mot ban cache cu thanh mot dong do trong console.
    print("\n=== [6] Client CU khong gui `ev`: van cong `n`, khong loi ===")
    LB = label_of("old")
    n0, e0 = nums(LB)
    req = urllib.request.Request(
        API + "/visit",
        data=json.dumps({"src": LB}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Origin": BASE},
        method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        code = r.status
    check("server tra 204 cho than KHONG co `ev`", code == 204, str(code))
    n1, e1 = nums(LB)
    check("DB: `n` cong 1", n1 == (n0 or 0) + 1, "%s -> %s" % (n0, n1))

    # ═══════════ [7] "CHUA DO" KHAC HAN "BANG 0" ═══════════
    # ⚠️⚠️ Viet `ADD n :one, e :zero` cho gon thi moi luot mo trang se TAO RA `e = 0`,
    #    va ban ghi co `e = 0` khong con phan biet duoc voi ban ghi CHUA DO -- tuc xoa
    #    mat dung cai ranh gioi "—" o trang bao cao. Moi nhan chay truoc 05/09/2026 deu
    #    thuoc ve nhom "chua do".
    check("ban ghi chi co luot mo trang thi KHONG co thuoc tinh `e`", e1 is None,
          "e=%s" % e1)

    # ⚠️ VA `ev` LA MOT TU KHOA CUA GIAO THUC, khong phai nhan do nguoi dat: mot chuoi
    #    rac khong duoc roi trung nhanh `engaged`.
    LB2 = label_of("junk")
    req = urllib.request.Request(
        API + "/visit",
        data=json.dumps({"src": LB2, "ev": "ENGAGED  "}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Origin": BASE},
        method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        code = r.status
    n2, e2 = nums(LB2)
    check("`ev` la chuoi khac ('ENGAGED  ') thi tinh la luot MO TRANG",
          code == 204 and n2 == 1 and e2 is None, "n=%s e=%s" % (n2, e2))

finally:
    srv.shutdown()
    # ⚠️ CHI XOA NHAN `zzeng*` do chinh bo nay bia ra. Bai hoc `probe_visit_beacon.py`:
    #    ban dau no `delete_item` luon ca `facebook/fbclid` -- mot NHAN THAT -- tuc
    #    **xoa mat luot cua khach that** moi lan chay do.
    for _lb in LABELS:
        try:
            ddb.delete_item(TableName=TABLE,
                            Key={"PK": {"S": "VISIT#" + DAY}, "SK": {"S": "SRC#" + _lb}})
        except Exception as _e:
            print("  [!] chua don duoc %s: %s" % (_lb, _e))
    print("\n=== KET QUA: %d dat / %d hong ===" % (ok, bad))
    sys.exit(0 if bad == 0 else 1)
