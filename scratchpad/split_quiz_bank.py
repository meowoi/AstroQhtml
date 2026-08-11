# -*- coding: utf-8 -*-
"""split_quiz_bank.py — CHIA NGAN HANG CAU HOI THANH MOT FILE MOI CAU.

Sinh ra:
  · js/quiz-index.js        — muc luc + bang nguon S + bo nap (classic script)
  · js/quiz/<khoa-cau>.js   — MOT cau hoi moi file (ES module, `export default`)

VI SAO CHIA (do duoc, 07/08/2026): `js/quiz-questions.js` = 175,4 KB tho /
43,6 KB gzip cho 100 cau = 51% duong tai cua quiz.html (85,9 KB gzip). Mot luot
chi dung 5/100 cau. Dot 2 them 270 cau -> bank ~161 KB gzip [Suy luan]. Chia
theo tung CAU thi mot luot tai ~5 KB va con so do KHONG tang khi bank lon len.

DON VI CHIA LA TUNG CAU, khong phai tung the — chu du an chot 07/08/2026 sau khi
doi chieu ba duong. Chia theo the (~20 cau/file) thi mot luot tron 5 thuat ngu
van keo ve 100 cau ~50 KB va con so do khong giam khi bank lon len.

CHAY LAI KHI NAO: sau moi dot nop cau moi, de muc luc bat kip. Script doc
`js/quiz/*.js` lam NGUON SU THAT roi sinh lai muc luc — nen them cau = them file
roi chay lai, khong sua muc luc bang tay.

  python scratchpad/split_quiz_bank.py            # sinh lai muc luc tu js/quiz/
  python scratchpad/split_quiz_bank.py --from-old # lan dau: cat js/quiz-questions.js

⚠️ CHAY CHROMIUM cho nhanh `--from-old`: du lieu cu la JS, khong phai JSON. Doc
   bang regex la doan; de trinh duyet nap roi hoi lai moi chac. Cung tien le da
   ghi cho check_quiz_bank.py.
"""
import argparse, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = os.path.join(ROOT, "js", "quiz-questions.js")
QDIR = os.path.join(ROOT, "js", "quiz")
INDEX = os.path.join(ROOT, "js", "quiz-index.js")
PORT = 8129

# Thu tu truong trong file cau hoi — giu dung thu tu cua bank cu de doc quen mat.
ORDER = ["term", "topic", "q", "opts", "a", "ok", "no", "hint", "lv",
         "src", "srcQuote", "srcChecked"]


# ────────────────────────────── serialize ──────────────────────────────
def jstr(s):
    """Chuoi JS. json.dumps lo dau nhay + backslash; U+2028/2029 phai escape
    bang tay vi JSON coi chung la ky tu thuong con JS coi la XUONG DONG —
    de nguyen la file vo cu phap, va loi do im lang."""
    out = json.dumps(s, ensure_ascii=False)
    return out.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def bil(o, ind):
    """Object song ngu {vi,en} — vi mot dong, en mot dong cho de doi chieu."""
    p = " " * ind
    return "{ vi: %s,\n%s  en: %s }" % (jstr(o["vi"]), p, jstr(o["en"]))


def q_file_body(q):
    L = []
    for k in ORDER:
        if k not in q or q[k] is None:
            continue
        v = q[k]
        if k in ("topic", "q", "ok", "no", "hint"):
            L.append("  %s: %s" % (k, bil(v, 2 + len(k) + 2)))
        elif k == "opts":
            inner = ",\n".join("    " + bil(o, 4) for o in v)
            L.append("  opts: [\n%s\n  ]" % inner)
        elif k in ("a", "lv"):
            L.append("  %s: %d" % (k, v))
        else:
            L.append("  %s: %s" % (k, jstr(v)))
    return ",\n".join(L)


# ⚠️ HEADER PHAI NGAN — MOI BYTE O DAY BI NHAN VOI SO CAU.
# Ban dau toi viet mot khoi 12 dong giai thich du luat vao day; do lai thi
# js/quiz/ phinh tu 175 KB len 240 KB, tuc ~1 KB chu giai lap 100 lan (se la
# 870 lan sau Dot 5) va moi luot tai nang them ~35% cho phan khong ai doc luc
# choi. Dung cai bay copy-paste ma CLAUDE.md muc 2 quy tac 2 cam. Luat day du
# nam MOT CHO: khoi chu thich dau js/quiz-index.js.
HDR_Q = """/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
%(body)s
};
"""


# ─────────────────────── doc bank cu (Chromium) ───────────────────────
def dump_old():
    """Nap js/quiz-questions.js + js/codex-terms.js trong Chromium, tra ve
    (danh sach cau, map url->object nguon, map khoa cau -> id the)."""
    from playwright.sync_api import sync_playwright
    import http.server, socketserver, threading, functools

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    tmp = os.path.join(ROOT, "_split_tmp.html")
    io.open(tmp, "w", encoding="utf-8").write(
        '<!doctype html><meta charset="utf-8">\n'
        '<script src="/js/quiz-questions.js"></script>\n'
        '<script src="/js/codex-terms.js"></script>\n')
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto("http://127.0.0.1:%d/_split_tmp.html" % PORT, wait_until="load")
            data = pg.evaluate("""() => ({
                all: window.AstroQQuestions.ALL,
                codex: window.AstroQCodex.all().map(x => ({ id: x.id, q: x.q || [] }))
            })""")
            b.close()
        if errs:
            sys.exit("HONG: loi khi nap bank cu: %s" % errs[:3])
    finally:
        os.remove(tmp)
        srv.shutdown()

    card = {}
    for c in data["codex"]:
        for k in c["q"]:
            if k in card:
                sys.exit("HONG: khoa cau %r bi HAI the nhan: %s + %s"
                         % (k, card[k], c["id"]))
            card[k] = c["id"]
    return data["all"], card


SRC_FILE = os.path.join(ROOT, "js", "quiz-sources.js")


def parse_sources():
    """Doc bang nguon. Tra ve {khoa: {name, url}}.

    ⚠️ TRUOC 09/08/2026 ham nay doc `js/quiz-questions.js` — file mot-bank DA BI XOA
       ngay 07/08 khi chia ngan hang. Tu hom do script NEM FileNotFoundError, tuc
       khong ai them duoc mot cau hoi nao, va loi do im lang 2 ngay vi khong ai chay
       script. Nay ban nguon la `js/quiz-sources.js` (sua bang tay), con bank cu chi
       dung o che do `--from-old`."""
    path = OLD if os.path.exists(OLD) else SRC_FILE
    if not os.path.exists(path):
        sys.exit("HONG: khong thay bang nguon %s" % SRC_FILE)
    src = io.open(path, encoding="utf-8").read()
    out = {}
    pat = r'(?:^\s*|S\.)([A-Za-z][A-Za-z0-9]*)\s*[:=]\s*\{\s*name:\s*"([^"]*)"\s*,\s*url:\s*"([^"]*)"\s*\}'
    for m in re.finditer(pat, src, re.M):
        out[m.group(1)] = {"name": m.group(2), "url": m.group(3)}
    urls = [v["url"] for v in out.values()]
    if len(set(urls)) != len(urls):
        sys.exit("HONG: hai khoa trong S tro cung mot URL — khong suy nguoc duoc")
    return out


# ─────────────────────── doc js/quiz/*.js (nguon su that) ───────────────────────
def read_split():
    """Nap moi file trong js/quiz/ bang Chromium roi tra ve danh sach cau.
    Cu phap `export default` khong doc duoc bang regex mot cach dang tin."""
    from playwright.sync_api import sync_playwright
    import http.server, socketserver, threading, functools

    keys = sorted(os.path.splitext(f)[0] for f in os.listdir(QDIR)
                  if f.endswith(".js"))
    if not keys:
        sys.exit("HONG: js/quiz/ rong — chay --from-old truoc")

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = os.path.join(ROOT, "_split_tmp.html")
    io.open(tmp, "w", encoding="utf-8").write('<!doctype html><meta charset="utf-8">')
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto("http://127.0.0.1:%d/_split_tmp.html" % PORT, wait_until="load")
            got = pg.evaluate("""async (keys) => {
                const out = [], bad = [];
                for (const k of keys) {
                  try { const m = await import("/js/quiz/" + k + ".js");
                        out.push([k, m.default]); }
                  catch (e) { bad.push([k, String(e)]); }
                }
                return { out, bad };
            }""", keys)
            b.close()
        if errs or got["bad"]:
            for k, e in got["bad"][:5]:
                print("  HONG nap %s: %s" % (k, e))
            sys.exit("HONG: %d file khong nap duoc" % len(got["bad"]))
    finally:
        os.remove(tmp)
        srv.shutdown()

    qs = []
    for k, q in got["out"]:
        if q.get("term") != k:
            sys.exit("HONG: %s.js khai term=%r — term PHAI bang ten file"
                     % (k, q.get("term")))
        qs.append(q)
    return qs


# ────────────────────────────── sinh muc luc ──────────────────────────────
HDR_INDEX = """/* js/quiz-index.js — MUC LUC NGAN HANG CAU HOI + BANG NGUON + BO NAP.

   ⚠️⚠️ FILE NAY SINH RA BANG SCRIPT — DUNG SUA BANG TAY.
        Nguon su that la `js/quiz/<khoa-cau>.js` (mot cau moi file). Them cau =
        them file roi chay:  python scratchpad/split_quiz_bank.py

   VI SAO KHONG CON MOT FILE BANK: do 07/08/2026 — `js/quiz-questions.js` la
   43,6 KB gzip cho 100 cau, tuc 51%% duong tai cua quiz.html, ma mot luot chi
   dung 5 cau. Dot 2 (+270 cau) se day bank len ~161 KB gzip [Suy luan]. Nay
   trang tai MUC LUC (nho) roi tai dung 5 file cau — con so nay khong tang khi
   bank lon len toi 1.000 cau.

   BA THU TRONG FILE NAY
     S      bang nguon dung chung. Cau hoi tro vao day bang KHOA (`src: "star"`),
            khong viet URL — 870 cau viet URL thang la ~870 ban sao cua ~40 dia chi.
     G      cac NHOM. Mot nhom = mot THE So Tay (`js/codex-terms.js`), hoac mot
            cau le chua the nao nhan. `t` = topic hien o badge [ CHU DE · CAU n/m ].
     LV     do kho 1/2/3, chi khai cho cau DA co. %(nolv)d/%(total)d cau chua khai —
            ⚠️ HIEN CHUA AI DOC `lv`. Chu du an chot 07/08/2026: GIU truong nay,
            cho duong "server tinh cap do roi client rut de theo cap do". Muon noi
            day thi quiz.html can doc duoc cap do cua tre, ma trang do CO Y khong
            nap SDK Firebase (233 KB) nen khong co token — phai them mot cache do
            dashboard ghi, dung khuon `astroq-route-gate`. Dung noi lai ma chua lam
            cai cache do; va dung xoa `lv` — de bai Dot 2-5 van yeu cau Gemini khai.

   ⚠️ `pickKeys()` CHONG TRUNG THEO THE, KHONG THEO `term` — sua 07/08/2026.
      Ban cu loc bang `pool[i].term`, nhung `term` la khoa cua CAU (moi cau mot
      khoa rieng: `star`, `star-fusion`), nen phep loc do CHUA BAO GIO chan duoc
      gi: do duoc 100/100 khoa la duy nhat. Y dinh ghi trong chu thich cu ("mot
      luot 5 cau co the hoi Sao choi hai lan") chi thanh that khi loc theo THE.
      Sau Dot 2 no moi that su quan trong: 15 the len ~20 cau/the, khong loc thi
      mot luot 5 cau co the toan la cau ve nhat thuc. */
"""

TAIL_INDEX = r"""
  /* Tron mot BAN SAO — tron tai cho thi luot sau thu tu G/LV da bi doi, va moi
     phep kiem dua vao thu tu khai bao se hong mot cach kho hieu. */
  function shuffled(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var r = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[r]; a[r] = t;
    }
    return a;
  }

  /* Nhom cua mot khoa cau (de gan `topic` sau khi tai). */
  var GOF = {};
  G.forEach(function (g) { g.q.forEach(function (k) { GOF[k] = g; }); });

  function terms() { return Object.keys(GOF); }
  function has(k) { return !!GOF[k]; }

  /* Chon n khoa cho mot luot. CHONG TRUNG THEO THE (xem canh bao dau file):
     rut nhom truoc, moi nhom mot cau. Het nhom moi lay bu cau thu hai. */
  function pickKeys(n) {
    var gs = shuffled(G), out = [], spare = [], i;
    for (i = 0; i < gs.length && out.length < n; i++) {
      var ks = shuffled(gs[i].q);
      out.push(ks[0]);
      for (var j = 1; j < ks.length; j++) spare.push(ks[j]);
    }
    spare = shuffled(spare);
    for (i = 0; out.length < n && i < spare.length; i++) out.push(spare[i]);
    return out.slice(0, n);
  }

  /* Loc khoa theo danh sach (duong vao `quiz.html?terms=a,b,c` tu bai doc). */
  function keysOfTerms(list) {
    if (!list || !list.length) return [];
    return list.filter(has);
  }

  /* Bu cho du n khoa, khong trung khoa da co va uu tien the khac. */
  function fill(keys, n) {
    var have = {}, out = keys.slice();
    out.forEach(function (k) { have[k] = 1; });
    var usedG = {};
    out.forEach(function (k) { if (GOF[k]) usedG[GOF[k].c || k] = 1; });
    var pool = shuffled(G), i, j;
    for (i = 0; i < pool.length && out.length < n; i++) {
      var g = pool[i], gid = g.c || g.q[0];
      if (usedG[gid]) continue;
      var ks = shuffled(g.q);
      for (j = 0; j < ks.length; j++) {
        if (!have[ks[j]]) { have[ks[j]] = 1; usedG[gid] = 1; out.push(ks[j]); break; }
      }
    }
    for (i = 0; i < pool.length && out.length < n; i++) {   /* het the moi trung the */
      var kk = shuffled(pool[i].q);
      for (j = 0; j < kk.length && out.length < n; j++) {
        if (!have[kk[j]]) { have[kk[j]] = 1; out.push(kk[j]); }
      }
    }
    return out.slice(0, n);
  }

  /* Gan lai phan khai o MUC LUC (topic, lv) va doi `src` tu KHOA sang object.
     Nho vay quiz.html nhan duoc cau co hinh dang y NHU bank mot-file cu. */
  function hydrate(k, raw) {
    if (!raw) return null;
    var q = {}, p;
    for (p in raw) if (Object.prototype.hasOwnProperty.call(raw, p)) q[p] = raw[p];
    q.term = k;
    var g = GOF[k];
    if (g && !q.topic) q.topic = g.t;
    if (LV[k] != null && q.lv == null) q.lv = LV[k];
    if (typeof q.src === "string") q.src = S[q.src] || null;
    return q;
  }

  /* Tai dung nhung cau duoc yeu cau. MOT FILE HONG KHONG DUOC GIET CA LUOT:
     `import()` co `.catch` rieng tung file, cau hong tra `null` roi bi loc ra —
     quiz.html se thay it cau hon chu khong thay mot trang trang. */
  function load(keys) {
    return Promise.all(keys.map(function (k) {
      return import("./quiz/" + k + ".js")
        .then(function (m) { return hydrate(k, m["default"]); })
        .catch(function (e) {
          if (window.console) console.warn("[quiz] khong tai duoc cau " + k, e);
          return null;
        });
    })).then(function (a) {
      return a.filter(function (x) { return !!x; });
    });
  }

  /* Mot luot binh thuong: rut n khoa roi tai. Neu co file hong thi bu them
     mot lan cho du n — de tre khong bi mot luot ngan hon vi loi mang. */
  function round(n) {
    var keys = pickKeys(n);
    return load(keys).then(function (qs) {
      if (qs.length >= n) return qs;
      var more = fill(qs.map(function (q) { return q.term; }), n)
                   .filter(function (k) {
                     return keys.indexOf(k) < 0;
                   });
      if (!more.length) return qs;
      return load(more).then(function (extra) {
        return qs.concat(extra).slice(0, n);
      });
    });
  }

  /* Duong vao tu bai doc: uu tien dung cac khoa duoc yeu cau, bu cho du n. */
  function byTerms(list, n) {
    var keys = shuffled(keysOfTerms(list)).slice(0, n);
    if (!keys.length) return Promise.resolve([]);
    if (keys.length < n) keys = fill(keys, n);
    return load(keys);
  }

  return {
    S: S, G: G, LV: LV,
    terms: terms, has: has, groupOf: function (k) { return GOF[k] || null; },
    shuffled: shuffled, pickKeys: pickKeys, keysOfTerms: keysOfTerms, fill: fill,
    load: load, round: round, byTerms: byTerms
  };
})();
"""


def write_index(qs, card, card_order=None, card_q=None):
    """`card_order` = danh sach the theo THU TU KHAI BAO trong codex-terms.js.
    `card_q`       = {the: [khoa cau theo thu tu the khai]}.

    ⚠️⚠️ VI SAO CAN HAI THAM SO NAY: `qs` den tu `glob` (xep a-b-c), nen khong truyen
       thu tu vao thi muc luc sinh ra xep nhom theo BANG CHU CAI — khac han ban 07/08
       (xep theo thu tu khai bao the: NGOI SAO, HANH TINH, HANH TINH LUN...). Do la mot
       thay doi AM THAM: file sinh ra khac hoan toan ma khong phep kiem nao noi gi, va
       moi lan chay lai se sinh ra mot dien mao khac tuy ai dat ten file the nao.
       Cung lop loi da gap o kho bai doc cung ngay (thu tu curation -> a-b-c)."""
    pos = {c: i for i, c in enumerate(card_order or [])}
    # nhom theo the; cau khong the nao nhan thi thanh nhom rieng (moi cau mot
    # khai niem — `algorithm`, `loop`… la 5 thu khac nhau, gop lam mot nhom thi
    # phep chong trung se coi chung la cung mot khai niem).
    groups, order = {}, []
    for q in qs:
        cid = card.get(q["term"])
        gid = cid or ("_" + q["term"])
        if gid not in groups:
            groups[gid] = {"c": cid, "t": q["topic"], "q": []}
            order.append(gid)
        g = groups[gid]
        if json.dumps(g["t"], sort_keys=True) != json.dumps(q["topic"], sort_keys=True):
            sys.exit("HONG: the %s co HAI topic khac nhau (%s vs %s) — topic phai "
                     "hang so trong mot the" % (gid, g["t"], q["topic"]))
        g["q"].append(q["term"])

    # Xep NHOM theo thu tu khai bao the; nhom cau le xuong cuoi, giu thu tu gap.
    if pos:
        _seen = {gid: i for i, gid in enumerate(order)}
        order.sort(key=lambda g: (0, pos[g]) if g in pos else (1, _seen[g]))
    # Xep CAU trong moi nhom theo thu tu the khai `q`; cau la khong co trong `q` thi
    # xuong cuoi (giu thu tu file) — nho vay muc luc doc ra cung mot mach voi the.
    if card_q:
        for gid, g in groups.items():
            want = card_q.get(gid) or []
            rank = {k: i for i, k in enumerate(want)}
            g["q"].sort(key=lambda k: (rank.get(k, len(rank)), k))

    used = set()
    for q in qs:
        if isinstance(q.get("src"), str):
            used.add(q["src"])
    S = parse_sources()
    miss = used - set(S)
    if miss:
        sys.exit("HONG: cau tro vao khoa nguon khong co trong S: %s" % sorted(miss))

    L = []
    nolv = sum(1 for q in qs if q.get("lv") is None)
    L.append(HDR_INDEX % {"nolv": nolv, "total": len(qs)})
    L.append("window.AstroQQuestions = (function () {\n  \"use strict\";\n")

    L.append("  /* ── BANG NGUON. Chi giu nguon CO CAU DANG DUNG; them nguon moi thi\n"
             "     them vao file cau roi chay lai script, dung sua o day. */")
    L.append("  var S = {")
    rows = []
    w = max(len(k) for k in sorted(used)) if used else 4
    for k in sorted(used):
        rows.append("    %-*s { name: %s, url: %s }"
                    % (w + 1, k + ":", jstr(S[k]["name"]), jstr(S[k]["url"])))
    L.append(",\n".join(rows))
    L.append("  };\n")

    L.append("  /* ── NHOM = MOT THE So Tay. `c` = id the (null = chua the nao nhan),\n"
             "     `t` = topic, `q` = cac khoa cau (chinh la ten file trong js/quiz/). */")
    L.append("  var G = [")
    grows = []
    for gid in order:
        g = groups[gid]
        c = jstr(g["c"]) if g["c"] else "null"
        ks = ", ".join(jstr(k) for k in g["q"])
        grows.append("    { c: %s,\n      t: %s,\n      q: [%s] }"
                     % (c, bil(g["t"], 9), ks))
    L.append(",\n".join(grows))
    L.append("  ];\n")

    L.append("  /* ── DO KHO. Chi khai cho cau DA co `lv`. Xem canh bao dau file. */")
    have = [q for q in qs if q.get("lv") is not None]
    if have:
        L.append("  var LV = {")
        lrows, line = [], "   "
        for q in have:
            piece = " %s: %d," % (jstr(q["term"]), q["lv"])
            if len(line) + len(piece) > 96:
                lrows.append(line); line = "   "
            line += piece
        if line.strip():
            lrows.append(line)
        L.append("\n".join(lrows).rstrip(","))
        L.append("  };")
    else:
        L.append("  var LV = {};")
    L.append(TAIL_INDEX)

    io.open(INDEX, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    return groups, order, nolv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-old", action="store_true",
                    help="cat js/quiz-questions.js thanh js/quiz/*.js (chi lan dau)")
    a = ap.parse_args()

    if a.from_old:
        if not os.path.exists(OLD):
            sys.exit("HONG: khong con %s — bo --from-old di" % OLD)
        qs, card = dump_old()
        S = parse_sources()
        by_url = {v["url"]: k for k, v in S.items()}
        os.makedirs(QDIR, exist_ok=True)
        conv = []
        for q in qs:
            k = q["term"]
            if not re.match(r"^[a-z0-9][a-z0-9-]*$", k):
                sys.exit("HONG: khoa cau %r khong dung dang kebab-case — no la TEN FILE" % k)
            out = {p: q[p] for p in ORDER if p in q and q[p] is not None}
            if q.get("src"):
                u = q["src"]["url"]
                if u not in by_url:
                    sys.exit("HONG: khong suy nguoc duoc khoa nguon cho URL %s" % u)
                out["src"] = by_url[u]
            io.open(os.path.join(QDIR, k + ".js"), "w", encoding="utf-8",
                    newline="\n").write(HDR_Q % {"key": k, "body": q_file_body(out)})
            conv.append(out)
        # ⚠️ PHAI TRUYEN BAN DA DOI `src` SANG KHOA cho write_index. Ban dau toi
        # truyen `qs` (ban tu Chromium, `src` con la OBJECT) nen `used` rong va
        # bang S trong muc luc sinh ra RONG — moi cau mat nguon, im lang.
        qs = conv
        print("Da sinh %d file trong js/quiz/" % len(conv))
    else:
        card_src = os.path.join(ROOT, "js", "codex-terms.js")
        if not os.path.exists(card_src):
            sys.exit("HONG: khong thay js/codex-terms.js")
        qs = read_split()
        # map khoa -> the, doc tu codex-terms.js bang Chromium o read_split? khong —
        # doc lai bang regex o day thi du: `q: ["a", "b"]` la mang chuoi phang.
        txt = io.open(card_src, encoding="utf-8").read()
        # ⚠️⚠️ CAT THEO `id:`, KHONG dung lookahead doi `};` hay `, {` NGAY SAU khoi.
        #    Ban cu doi dieu do va no BO DUNG MOT THE: `term_earth_atmosphere` — the co
        #    20 cau — vi sau khoi do co mot COMMENT chen vao truoc `{` ke tiep nen
        #    lookahead truot. Hau qua: 20 cau atmo mat the, moi cau thanh MOT nhom
        #    `c: null`, badge doi tu "TRAI DAT & KHI QUYEN" sang nhom le. Loi IM LANG.
        #    ⚠️ Nhanh nay CHUA TUNG chay thanh cong truoc 09/08/2026: lan chia 07/08 dung
        #       `--from-old` (card dung tu dump_old), con o nhanh nay `parse_sources()`
        #       nem FileNotFoundError truoc khi toi day. Khong chay thi khong ai thay.
        _ids = re.findall(r'id:\s*"(term_[a-z0-9_]+)"', txt)
        _blocks = re.split(r'id:\s*"term_[a-z0-9_]+"', txt)[1:]
        card, card_q, _with_q = {}, {}, 0
        for cid, body in zip(_ids, _blocks):
            qm = re.search(r'\bq:\s*\[([^\]]*)\]', body, re.S)
            if not qm:
                continue
            keys = re.findall(r'"([a-z0-9][a-z0-9-]*)"', qm.group(1))
            if keys:
                _with_q += 1
            for k in keys:
                card[k] = cid
            card_q[cid] = keys
        # ⛔ HANG RAO: so THE map duoc phai bang so the CO khai `q` khong rong. Thieu mot
        #    the la mat ca nhom cau cua no, ma muc luc van sinh ra "thanh cong".
        _n_decl = sum(1 for b in _blocks if re.search(r'\bq:\s*\[\s*"', b, re.S))
        if _with_q != _n_decl:
            sys.exit("HONG: map duoc %d/%d the co khai `q` — mot the bi bo, dung sinh "
                     "muc luc" % (_with_q, _n_decl))
        print("  the map duoc     : %d/%d (khoa cau: %d)" % (_with_q, _n_decl, len(card)))

    groups, order, nolv = write_index(
        qs, card,
        card_order=locals().get("_ids"), card_q=locals().get("card_q"))

    print("=== KET QUA ===")
    print("  cau              : %d" % len(qs))
    print("  nhom (the)       : %d  (trong do %d nhom cau le chua the)"
          % (len(order), sum(1 for g in groups.values() if not g["c"])))
    print("  nguon dung       : %d" % len({q["src"] for q in qs if isinstance(q.get("src"), str)}))
    print("  cau chua khai lv : %d" % nolv)
    tot = sum(os.path.getsize(os.path.join(QDIR, f)) for f in os.listdir(QDIR)
              if f.endswith(".js"))
    print("  js/quiz/ tong    : %.1f KB tho" % (tot / 1024.0))
    print("  js/quiz-index.js : %.1f KB tho" % (os.path.getsize(INDEX) / 1024.0))


if __name__ == "__main__":
    main()
