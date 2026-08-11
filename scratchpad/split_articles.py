# -*- coding: utf-8 -*-
"""Chia kho bai doc thanh MOT FILE MOI BAI + sinh lai muc luc.

    python -m http.server 8123          (trong AstroQhtml/)
    PYTHONIOENCODING=utf-8 python scratchpad/split_articles.py

VI SAO CHIA (do 09/08/2026, khong doan):
  `js/articles.js` mot-file la **52,3 KB gzip cho 39 bai = 52% duong tai cua
  library.html**, ma tre chi doc **1 bai** moi luot. Do la DUNG nguong da buoc du an
  chia ngan hang cau hoi ngay 07/08/2026 (43,6 KB = 51% duong tai cua quiz.html,
  dung 5/100 cau). Tach ra thi phan NHE con **3,7 KB** va phan NANG (than bai) la
  **43,4 KB = 92%** — tuc gan nhu toan bo trong luong nam o thu khong ai doc.

DON VI CHIA LA TUNG BAI, khong phai tung chu de: mot luot doc dung mot bai, nen
tai theo bai thi con so KHONG TANG khi kho lon len. Chia theo chu de thi mo mot bai
thien van van keo ve ca 19 bai thien van.

RANH GIOI NHE / NANG — suy ra tu chinh cho VE:
  MUC LUC (`js/articles-index.js`): id · src · cat · em · c[3] · img · title
      => du cho luoi the (`cardHtml`), 3 o cua khoi noi bat, bo loc nguon/chu de.
  FILE BAI (`js/article/<id>.js`): + url · credit · body · term · terms
      => chi trinh doc can, va o noi bat thi chi CAI THE LON can (doan mo dau).

⚠️ FILE BAI LA NGUON SU THAT VA CHUA DU MOI TRUONG. Muc luc chi la BAN CHIEU sinh ra
   tu chung — nho vay chay lai script bao nhieu lan cung ra dung muc luc do, va them
   bai = them mot file roi chay lai. ⛔ DUNG SUA `js/articles-index.js` BANG TAY.

⚠️ DOC DU LIEU QUA CHROMIUM, KHONG PARSE JS BANG REGEX. `js/articles.js` long nhieu
   muc va co chuoi chua dau `{`; parse tay la doan ranh gioi tung object — dung ly do
   phep kiem cau truc kho bai doc phai o bo smoke chu khong o `check_pages`.

HAI CHE DO:
  · CHIA (con `js/articles.js`): doc `AstroQArticles.all()` -> ghi files + muc luc.
  · SINH LAI (het `js/articles.js`): `import()` moi `js/article/*.js` trong Chromium
    -> ghi lai MOT MINH muc luc. Dung sau khi them/sua mot file bai.
"""
import glob
import io
import json
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "http://127.0.0.1:8123"
OLD = os.path.join(ROOT, "js", "articles.js")
DIR = os.path.join(ROOT, "js", "article")
INDEX = os.path.join(ROOT, "js", "articles-index.js")

# ⚠️ `ord` PHAI o ca hai: no la THU TU CURATION, va `featured()` chon "bai chua doc
#    dau tien theo THU TU MUC LUC" — nen muc luc sai thu tu la doi HAN the lon.
LIGHT = ("ord", "id", "src", "cat", "em", "c", "img", "title")
ORDER = ("ord", "id", "src", "cat", "em", "c", "img", "credit", "url",
         "title", "body", "term", "terms")


def js(v):
    return json.dumps(v, ensure_ascii=False)


def emit(o, ind=2):
    """In object literal doc duoc: khoa khong ngoac, chuoi qua json.dumps."""
    p = " " * ind
    out = []
    for k in ORDER:
        if k not in o:
            continue
        v = o[k]
        if k == "body" and isinstance(v, dict):
            parts = []
            for lang in ("vi", "en"):
                arr = v.get(lang) or []
                inner = (",\n" + p + " " * 9).join(js(x) for x in arr)
                parts.append(f"{lang}: [{inner}]")
            out.append(f"{p}body: {{\n{p}  " + (f",\n{p}  ".join(parts)) + f"\n{p}}}")
        elif k == "term" and isinstance(v, dict):
            w, tx = v.get("word") or {}, v.get("text") or {}
            out.append(
                f"{p}term: {{ who: {js(v.get('who'))},\n"
                f"{p}         word: {{ vi: {js(w.get('vi'))},\n"
                f"{p}                 en: {js(w.get('en'))} }},\n"
                f"{p}         text: {{ vi: {js(tx.get('vi'))},\n"
                f"{p}                 en: {js(tx.get('en'))} }} }}")
        elif isinstance(v, dict) and set(v) <= {"vi", "en"}:
            out.append(f"{p}{k}: {{ vi: {js(v.get('vi'))},\n"
                       f"{p}{' ' * len(k)}   en: {js(v.get('en'))} }}")
        else:
            out.append(f"{p}{k}: {js(v)}")
    return ",\n".join(out)


ART_HEAD = """/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do.
   ⚠️ HEADER CO Y CHI 2 DONG: header 6 dong x 39 file lam tong phinh ~8 KB gzip cho
      phan khong ai doc luc chay — dung bai hoc da ghi khi chia ngan hang cau hoi
      (07/08/2026: header 1 KB x 100 file day 175 -> 240 KB). Luat day du o muc luc. */
export default {
"""


def read_via_browser():
    """Tra ve (arts, che_do)."""
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_context().new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        if os.path.exists(OLD):
            pg.goto(BASE + "/library.html", wait_until="load")
            pg.wait_for_selector(".card", timeout=15000)
            arts = pg.evaluate("()=>AstroQArticles.all()")
            mode = "CHIA"
        else:
            ids = sorted(os.path.splitext(os.path.basename(f))[0]
                         for f in glob.glob(os.path.join(DIR, "*.js")))
            pg.goto(BASE + "/library.html", wait_until="load")
            pg.wait_for_selector(".card", timeout=15000)
            arts = pg.evaluate(
                # ⚠️ Duong TUYET DOI: `import()` trong `page.evaluate` giai theo URL cua TAI LIEU
            #    (/library.html), nen './article/' thanh '/article/' -> 404. Do da do.
            "ids => Promise.all(ids.map(i => import('/js/article/'+i+'.js')"
                ".then(m => m.default)))", ids)
            mode = "SINH LAI"
        br.close()
    if errs:
        print("  [!] pageerror:", errs[:2])
    return arts, mode


def main():
    arts, mode = read_via_browser()
    if not arts:
        print("[HONG] doc ra 0 bai — dung ghi gi ca")
        sys.exit(1)
    print(f"che do: {mode} · doc duoc {len(arts)} bai")

    # ⚠️⚠️ SAP THEO `ord`, KHONG theo thu tu glob. Che do SINH LAI doc file bang
    #    `glob` (xep theo bang chu cai), va lan dau chay no da AM THAM doi thu tu
    #    muc luc tu "khai bao" sang "a-b-c" — the lon o khoi noi bat nhay tu `jwst`
    #    sang `art-ai-already-around-you`. Khong bo kiem nao bat, vi moi phep kiem
    #    deu SUY thu tu tu du lieu. Bai nao thieu `ord` thi xuong cuoi.
    arts.sort(key=lambda a: (a.get("ord") is None, a.get("ord") or 0, a["id"]))
    _noord = [a["id"] for a in arts if a.get("ord") is None]
    if _noord:
        print(f"  [!] {len(_noord)} bai thieu `ord`, xep xuong cuoi: {_noord[:3]}")
    ids = [a["id"] for a in arts]
    if len(set(ids)) != len(ids):
        print("[HONG] id trung — dung lai")
        sys.exit(1)

    if mode == "CHIA":
        os.makedirs(DIR, exist_ok=True)
        for a in arts:
            body = ART_HEAD + emit(a) + "\n};\n"
            io.open(os.path.join(DIR, a["id"] + ".js"), "w",
                    encoding="utf-8", newline="\n").write(body)
        print(f"  da ghi {len(arts)} file vao js/article/")

    # ── MUC LUC ─────────────────────────────────────────────────────────
    rows = []
    for a in arts:
        e = {k: a[k] for k in LIGHT if k in a}
        rows.append("    { " + ", ".join(
            f"{k}: {js(e[k])}" for k in LIGHT if k in e) + " }")
    idx_src = HEAD + "  var IDX = [\n" + ",\n".join(rows) + "\n  ];\n" + TAIL
    io.open(INDEX, "w", encoding="utf-8", newline="\n").write(idx_src)
    print(f"  da sinh js/articles-index.js ({len(idx_src)/1024:.1f} KB tho)")

    if mode == "CHIA":
        print("\n⚠️ CON PHAI LAM TAY:")
        print("   1. doi <script src> o library.html + learn.html sang articles-index.js")
        print("   2. `openReader` thanh KHONG DONG BO (AstroQArticles.load)")
        print("   3. xoa js/articles.js")


HEAD = '''/* js/articles-index.js — MUC LUC KHO BAI DOC + BO NAP.

   ⚠️⚠️ FILE NAY SINH RA BANG SCRIPT — DUNG SUA BANG TAY.
        Nguon su that la `js/article/<id>.js` (MOT BAI MOI FILE, chua DU moi truong).
        Them bai = them file roi chay:  python scratchpad/split_articles.py

   VI SAO KHONG CON MOT FILE `js/articles.js` — do 09/08/2026, khong doan:
     mot-file la **52,3 KB gzip cho 39 bai = 52% duong tai cua library.html**, ma tre
     chi doc **1 bai** moi luot. Dung nguong da buoc chia ngan hang cau hoi ngay
     07/08/2026 (43,6 KB = 51% duong tai quiz.html, dung 5/100 cau). Tach ra: phan
     nhe **3,7 KB**, phan nang (than bai) **43,4 KB = 92%**. Con so nay KHONG TANG
     khi kho lon len — do la ca ly do chon don vi chia la TUNG BAI.

   MUC LUC GIU GI: id · src · cat · em · c[3] · img · title — dung du cho luoi the,
   3 o cua khoi noi bat, va bo loc nguon/chu de. `body`/`term`/`url`/`credit`/`terms`
   nam trong file bai, tai khi CAN:
     · mo trinh doc            -> load(id)
     · doan mo dau cua THE LON o khoi noi bat -> load(id) cua dung mot bai
     · tim kiem toan van       -> loadAll(), goi khi tre bat dau tim

   LUAT NOI DUNG (cho bai moi — bo kiem `smoke_library_featured.py` muc [8] canh):
     · `url` phai tra 200 va thuoc nguon tin cay (NASA · ESA · NOAA · USGS · NPS ·
       MIT · Exploratorium · LCO · UCAR). MIT vao danh sach 09/08/2026 vi NASA gan
       nhu khong co noi dung ve AI trong DOI SONG; bo `wiki/` da dan MIT tu truoc.
     · moi con so trong than bai phai TRICH DUOC nguyen van tu trang nguon.
     · `body.vi` va `body.en` phai CUNG SO DOAN.
     · `terms` phai la khoa cau CO THAT (co file `js/quiz/<khoa>.js`) — sai mot chu
       la day noi sang Dau Truong dut IM LANG.
     · `img` la `null` hoac URL https; ⛔ dung doan duong dan anh NASA theo mau —
       da do: `~large` KHONG ton tai voi moi anh.
     · ⛔ dung viet "doc xong nhan Thien thach tim" — doc bai KHONG con thuong tu
       30/07/2026 (`Wallet.MaxPerLesson = 0`).
*/
window.AstroQArticles = (function () {
  "use strict";

'''

TAIL = '''
  /* Bai cu ↔ bai da gop. Chi dung de DOC LAI lich su; bai moi khong them vao day. */
  var OLD_ID = { "gaia": "lib-gaia", "eht": "lib-blackhole", "exo-ai": "lib-exoplanet" };

  /* ───────── Trang thai da doc — DUNG CHUNG cho ca hai trang ─────────
     ⚠️ Ba ham nay tung duoc chep y het o `learn.html` va `library.html`. Chung phai
        giong nhau tung chu, khong thi loi "doc o trang nay, trang kia bao chua doc"
        quay lai — nen chung thuoc ve day, khong thuoc ve tung trang. */
  var READ_KEY = "astroq-read";

  function readSet() {
    try { return JSON.parse(localStorage.getItem(READ_KEY) || "[]"); } catch (e) { return []; }
  }
  function isRead(id) {
    var s = readSet();
    if (s.indexOf(id) >= 0) return true;
    for (var k in OLD_ID) if (OLD_ID[k] === id && s.indexOf(k) >= 0) return true;
    return false;
  }
  function markRead(id) {
    var s = readSet();
    if (s.indexOf(id) < 0) {
      s.push(id);
      try { localStorage.setItem(READ_KEY, JSON.stringify(s)); } catch (e) {}
    }
  }

  /* ───────── Chon bai noi bat — DUNG CHUNG ─────────
     Uu tien bai CHUA DOC (giu thu tu khai bao), thieu thi lay them bai da doc cho du n
     — nen con so n khong bao gio hut ke ca khi tre da doc het.
     ⚠️ Cho goi phai tinh MOT LAN luc mo trang. Tinh lai sau moi lan danh dau da doc thi
        bai vua doc bien khoi khoi noi bat ngay duoi tay tre va ca khoi nhay cho. */
  function featured(n) {
    var unread = [], seen = [];
    for (var i = 0; i < IDX.length; i++) {
      (isRead(IDX[i].id) ? seen : unread).push(IDX[i]);
    }
    return unread.concat(seen).slice(0, Math.min(n, IDX.length));
  }

  function byId(id) {
    for (var i = 0; i < IDX.length; i++) if (IDX[i].id === id) return IDX[i];
    return null;
  }

  /* ───────── Bo nap than bai ─────────
     ⚠️ MOT FILE HONG KHONG DUOC GIET CA TRANG: `import()` co `.catch` rieng tung
        file, bai hong tra `null`. Cho goi phai chiu duoc `null` — tha khong mo duoc
        MOT bai con hon mot trang trang. Cung luat da dung cho `js/quiz/`. */
  var CACHE = {}, ALL_P = null;

  /* ⚠️⚠️ `file://` CHAN `import()` MODULE — va do la mot LY DO KHAC HAN "mat mang".
     Do duoc 09/08/2026 tren Chromium: mo library.html tu dia thi muc luc nap binh
     thuong (no la script CO DIEN) nhung moi lan `import()` file bai deu bi tu choi:
       Access to script at 'file:///.../js/article/jwst.js' from origin 'null'
       has been blocked by CORS policy
     Neu de trang noi "kiem tra ket noi" thi no NOI SAI NGUYEN NHAN: mang khong lien
     quan gi, va nguoi doc se di sua dung thu khong hong. Nen bo nap phai noi ra
     duoc su khac biet, va trang chon cau theo do.
     ⚠️ Day la HE QUA cua viec chia kho (09/08/2026): truoc do ca kho nam trong mot
        script co dien nen xem bang file:// van doc duoc bai. Tu nay library.html va
        learn.html vao cung nhom voi quiz/codex/explorer/dashboard — deu can may chu.
        Nguoi dung THAT khong bi anh huong: GitHub Pages phuc vu qua https. */
  function needsServer() {
    try { return location.protocol === "file:"; } catch (e) { return false; }
  }

  /* ⚠️ CHOT DUONG DAN BANG `currentScript`, KHONG viet "./article/". Do duoc: trong
     Chromium thi `import()` o mot script CO DIEN giai theo URL CUA SCRIPT, nen
     "./article/x.js" ra dung /js/article/x.js. NHUNG du an da tra gia mot lan vi dung
     lop loi nay — `import("./api.js")` o `js/index.js` (07/08/2026): tu /en/ no thanh
     /en/api.js va form waitlist chet cam. Suy tu URL cua chinh file nay thi dung o moi
     noi dat trang, khong phu thuoc trang nam o thu muc nao. */
  var SELF = (document.currentScript && document.currentScript.src) || "";
  var ART_DIR = SELF ? SELF.replace(/[^/]*$/, "") + "article/" : "js/article/";

  function load(id) {
    if (CACHE[id]) return Promise.resolve(CACHE[id]);
    if (!byId(id)) return Promise.resolve(null);
    return import(ART_DIR + id + ".js")
      .then(function (m) { CACHE[id] = m["default"]; return CACHE[id]; })
      .catch(function (e) {
        if (window.console) console.warn("[articles] khong tai duoc bai " + id, e);
        return null;
      });
  }

  /* Tai HET than bai — chi dung cho TIM KIEM TOAN VAN, va chi goi khi tre bat dau
     tim. Nho vay duong tai luc MO TRANG khong he chua thu nay. Ket qua nho lai. */
  function loadAll() {
    if (!ALL_P) {
      ALL_P = Promise.all(IDX.map(function (e) { return load(e.id); }))
        .then(function (a) { return a.filter(Boolean); });
    }
    return ALL_P;
  }

  /* Than bai da nam trong bo nho chua? Cho tim kiem doc ma KHONG phai cho mang. */
  function loaded(id) { return CACHE[id] || null; }

  window.AstroQArticles = {
    all: function () { return IDX.slice(); },
    featured: featured,
    byId: byId,
    load: load,
    loadAll: loadAll,
    loaded: loaded,
    needsServer: needsServer,
    readSet: readSet,
    isRead: isRead,
    markRead: markRead,
    READ_KEY: READ_KEY
  };
  return window.AstroQArticles;
})();
'''

if __name__ == "__main__":
    main()
