# -*- coding: utf-8 -*-
"""check_teach_engine.py — ĐO RIÊNG bộ phân loại `js/teach-machine.js`.

    python scratchpad/check_teach_engine.py

Chạy TRƯỚC khi dựng `game-classify.html`, theo quy tắc 4 mục 6: *test cho đạt
hết rồi mới tích hợp vào giao diện*. Nạp file JS vào một trang trắng nên KHÔNG
cần server, KHÔNG cần backend — hợp lệ để đưa vào cổng push.

⚠️⚠️ PHÉP KIỂM QUAN TRỌNG NHẤT Ở ĐÂY KHÔNG PHẢI "MÁY ĐOÁN ĐÚNG" MÀ LÀ
   **"MÁY ĐOÁN SAI ĐÚNG CHỖ CẦN SAI"**. Cả bài học của ARCADE-12 dựng trên việc
   một bộ dạy thiếu vùng thì máy PHẢI trượt ở vùng đó — nếu nó *tình cờ* đoán
   đúng, trẻ đọc màn hình ra thành "máy giỏi" và bài học *dữ liệu chính là bài
   học* biến mất không dấu vết. Đây là thứ chỉ đo được, không suy được: cùng
   một ý tưởng thiết kế mà đổi k hoặc đổi toạ độ mẫu một chút là kết quả lật.

⚠️ Và phép kiểm ĐỐI CHỨNG đi kèm cũng bắt buộc: cùng bộ dạy thiếu đó, máy phải
   ĐÚNG ở các vùng đã dạy. Một mẻ mà máy sai hết thì thông điệp đọc ra là "máy
   hỏng", không ra "bộ dạy của con thiếu".
"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "js", "teach-machine.js")

_ok = _bad = 0


def check(cond, label, extra=""):
    global _ok, _bad
    if cond:
        _ok += 1
        print("  [OK]   %s" % label)
    else:
        _bad += 1
        print("  [HONG] %s %s" % (label, extra))
    return bool(cond)


if not os.path.exists(SRC):
    print("[HONG] khong thay %s" % SRC)
    sys.exit(2)

try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    print("[HONG] khong co Playwright: %s" % e)
    sys.exit(2)

JS = open(SRC, encoding="utf-8").read()

# ── Hàm dùng chung trong trang: dạy bằng NHÃN ĐÚNG của các vùng cho trước,
#    rồi đoán một vùng khác. Trả về danh sách (id, nhãn máy đoán, nhãn đúng).
HELPER = """
window.__run = function (trainZones, testZone, flipRay) {
  var T = window.AstroQTeach, lab = [];
  trainZones.forEach(function (z) {
    T.pool(z).forEach(function (s) {
      // `flipRay`: mo phong tre gan nhan SAI cho tia vu tru (thay no sang nen
      // tuong la tieu hanh tinh). Day la mot loi NGUOI day, khong phai loi may.
      var y = (flipRay && s.why === 'ray') ? T.AST : s.truth;
      lab.push({ sample: s, label: y });
    });
  });
  var m = T.train(lab);
  return T.pool(testZone).map(function (s) {
    var r = T.predict(m, s);
    return { id: s.id, got: r.label, truth: s.truth, gap: r.gap,
             far: T.isFar(r), votes: r.votes, of: r.of };
  });
};
"""


def run(pg, train_zones, test_zone, flip_ray=False):
    return pg.evaluate("([a,b,c]) => window.__run(a,b,c)",
                       [train_zones, test_zone, flip_ray])


def n_wrong(rows):
    return sum(1 for r in rows if r["got"] != r["truth"])


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_context().new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text)
          if m.type == "error" else None)
    pg.goto("about:blank")
    pg.add_script_tag(content=JS)
    pg.add_script_tag(content=HELPER)

    # ═══════════ [1] Nạp được, không lỗi, xuất đúng API ═══════════
    print("\n=== [1] Nap file va be mat API ===")
    check(not errs, "0 loi khi nap teach-machine.js", str(errs[:2]))
    api = pg.evaluate(
        "() => Object.keys(window.AstroQTeach || {}).sort()")
    for k in ("AST", "NOISE", "POOL", "dist", "isFar", "pool",
              "predict", "svg", "train"):
        check(k in api, "xuat AstroQTeach.%s" % k, str(api))

    # Kho mẫu phải đủ 6 vùng và mọi mẫu có nhãn đúng hợp lệ.
    zones = pg.evaluate("() => Object.keys(window.AstroQTeach.POOL)")
    check(len(zones) == 6, "kho co 6 vung", str(zones))
    bad_field = pg.evaluate("""() => {
      var T = window.AstroQTeach, bad = [];
      Object.keys(T.POOL).forEach(function (z) {
        T.POOL[z].forEach(function (s) {
          if (s.truth !== T.AST && s.truth !== T.NOISE) bad.push(s.id + ':truth');
          ['len','curve','bright'].forEach(function (f) {
            if (typeof s[f] !== 'number' || s[f] < 0 || s[f] > 1)
              bad.push(s.id + ':' + f);
          });
        });
      });
      return bad;
    }""")
    check(not bad_field, "moi mau co truth hop le va 3 dac trung trong [0,1]",
          str(bad_field[:4]))

    ids = pg.evaluate("""() => {
      var T = window.AstroQTeach, a = [];
      Object.keys(T.POOL).forEach(function (z) {
        T.POOL[z].forEach(function (s) { a.push(s.id); }); });
      return a;
    }""")
    check(len(ids) == len(set(ids)), "moi id mau la duy nhat",
          str([i for i in ids if ids.count(i) > 1][:4]))

    # ═══════════ [2] TẤT ĐỊNH ═══════════
    # Không có Math.random() nào trong đường phân loại. Chập chờn thì cả bộ đo
    # này lẫn phần giải thích "vì sao máy sai" đều mất nghĩa.
    print("\n=== [2] Tat dinh (chay lai ra y het) ===")
    a1 = run(pg, ["curved_bright", "dots"], "curved_short")
    a2 = run(pg, ["curved_bright", "dots"], "curved_short")
    check(json.dumps(a1, sort_keys=True) == json.dumps(a2, sort_keys=True),
          "cung bo day + cung mau -> cung ket qua")

    # ═══════════ [3] ⚠️ THIÊN LỆCH PHẢI XẢY RA — TRÁI TIM CỦA TRÒ CHƠI ═══════
    print("\n=== [3] Bo day THIEU vung -> may PHAI sai o dung vung do ===")
    biased = run(pg, ["curved_bright", "dots"], "curved_short")
    w = n_wrong(biased)
    check(w == len(biased),
          "day 'cong+DAI' & 'cham NGAN' -> sai TAT CA %d mau 'cong+NGAN'" % len(biased),
          str(biased))
    check(all(r["got"] == "noise" for r in biased),
          "va sai theo dung kieu du doan: goi tieu hanh tinh la NHIEU",
          str([r["got"] for r in biased]))
    # Máy phải nói được "tớ chưa từng thấy cái nào giống thế này" — và câu đó
    # phải đúng chứ không phải một câu an ủi dán bừa.
    check(all(r["far"] for r in biased),
          "isFar()=true o ca %d mau chua tung duoc day" % len(biased),
          str([round(r["gap"], 3) for r in biased]))

    # ⚠️⚠️ CHIỀU ĐỐI CHỨNG — THIẾU NÓ THÌ NGƯỠNG 999 CŨNG "ĐẠT".
    # Phép kiểm trên một mình chỉ đòi cờ BẬT; một hàm `isFar` luôn trả true sẽ
    # đi qua nó. Chiều này đòi cờ TẮT ở vùng máy đã được dạy tử tế, nên hai
    # chiều cộng lại mới ghim được ngưỡng vào đúng khoảng trống đo được.
    for z in ("curved_bright", "dots", "curved_faint"):
        rows = run(pg, ["curved_bright", "dots"], z)
        check(not any(r["far"] for r in rows),
              "doi chung: isFar()=false o vung DA DAY '%s'" % z,
              str([round(r["gap"], 3) for r in rows]))

    print("\n=== [3b] DOI CHUNG: cung bo day thieu do, may van DUNG o vung da day ===")
    for z in ("curved_bright", "dots", "curved_mid"):
        rows = run(pg, ["curved_bright", "dots"], z)
        check(n_wrong(rows) == 0,
              "vung '%s': dung %d/%d" % (z, len(rows) - n_wrong(rows), len(rows)),
              str([(r["id"], r["got"]) for r in rows if r["got"] != r["truth"]]))

    # ═══════════ [4] BỔ SUNG DỮ LIỆU -> MÁY KHÁ LÊN ═══════════
    # Nếu phép kiểm này hỏng thì câu "dữ liệu chính là bài học" (trích nguyên văn
    # từ `art-ai-tags-nasa-data`) thành lời nói suông trên màn hình.
    print("\n=== [4] Bo sung dung vung thieu -> may DUNG ===")
    fixed = run(pg, ["curved_bright", "dots", "curved_short"], "curved_short")
    check(n_wrong(fixed) == 0,
          "them 'cong+NGAN' vao bo day -> dung %d/%d" % (
              len(fixed) - n_wrong(fixed), len(fixed)),
          str([(r["id"], r["got"]) for r in fixed if r["got"] != r["truth"]]))
    check(w > n_wrong(fixed), "so mau sai GIAM han (%d -> %d)" % (w, n_wrong(fixed)))
    # Và bổ sung KHÔNG được phá thứ máy vốn đã đúng.
    for z in ("curved_bright", "dots", "curved_mid", "curved_faint"):
        rows = run(pg, ["curved_bright", "dots", "curved_short"], z)
        check(n_wrong(rows) == 0,
              "sau khi bo sung, '%s' van dung %d/%d" % (
                  z, len(rows) - n_wrong(rows), len(rows)),
              str([(r["id"], r["got"]) for r in rows if r["got"] != r["truth"]]))

    # ═══════════ [5] ĐẶC TRƯNG GÂY NHIỄU đúng là gây nhiễu ═══════════
    # `bright` hiện trên màn hình nhưng KHÔNG nằm trong phép tính. Nếu nó lọt vào,
    # bẫy vòng ③ (tia vũ trụ rất sáng) hỏng.
    print("\n=== [5] `bright` KHONG anh huong ket qua ===")
    same = pg.evaluate("""() => {
      var T = window.AstroQTeach;
      function lab(z) { return T.pool(z).map(function (s) {
        return { sample: s, label: s.truth }; }); }
      var tr = lab('curved_bright').concat(lab('dots'));
      var m = T.train(tr);
      var base = T.pool('curved_mid').map(function (s) {
        return T.predict(m, s).label; });
      // Dao nguoc do sang cua MOI mau, ca ben day lan ben kiem.
      function flip(s) { return { id: s.id, len: s.len, curve: s.curve,
                                  bright: 1 - s.bright, truth: s.truth }; }
      var m2 = T.train(tr.map(function (L) {
        return { sample: flip(L.sample), label: L.label }; }));
      var alt = T.pool('curved_mid').map(function (s) {
        return T.predict(m2, flip(s)).label; });
      return JSON.stringify(base) === JSON.stringify(alt);
    }""")
    check(same, "dao nguoc `bright` cua moi mau -> ket qua KHONG doi")

    # ═══════════ [6] NGƯỜI dạy sai -> MÁY học sai (loi cua nguoi) ═══════════
    print("\n=== [6] Gan nhan SAI cho tia vu tru -> may hoc sai theo ===")
    honest = run(pg, ["curved_bright", "dots", "rays"], "rays")
    check(n_wrong(honest) == 0,
          "day dung: 4 tia vu tru -> deu goi la NHIEU",
          str([(r["id"], r["got"]) for r in honest if r["got"] != r["truth"]]))
    lied = run(pg, ["curved_bright", "dots", "rays"], "rays", flip_ray=True)
    check(n_wrong(lied) == len(lied),
          "day sai (tia = tieu hanh tinh): may goi CA 4 tia la tieu hanh tinh",
          str([(r["id"], r["got"]) for r in lied]))

    # ═══════════ [7] Chiến lược MÙ phải thua ═══════════
    # Cùng luật cân bằng đã áp cho `play_recycle` (21 to hop) va `play_units`:
    # khong duoc co mot cach bam nhu may nao qua duoc.
    print("\n=== [7] Khong chien luoc MU nao qua duoc ===")
    blind = pg.evaluate("""() => {
      var T = window.AstroQTeach, out = {};
      var TRAIN = ['curved_bright','dots'], TEST = ['curved_mid','dots','rays'];
      [T.AST, T.NOISE].forEach(function (fixed) {
        var lab = [];
        TRAIN.forEach(function (z) { T.pool(z).forEach(function (s) {
          lab.push({ sample: s, label: fixed }); }); });
        var m = T.train(lab), wrong = 0, tot = 0;
        TEST.forEach(function (z) { T.pool(z).forEach(function (s) {
          tot++; if (T.predict(m, s).label !== s.truth) wrong++; }); });
        out[fixed] = [wrong, tot];
      });
      return out;
    }""")
    for lbl, (wr, tot) in blind.items():
        check(wr > 0, "gan nhan '%s' cho TAT CA -> sai %d/%d mau kiem"
              % (lbl, wr, tot))

    # ═══════════ [8] SVG ═══════════
    print("\n=== [8] Ve anh quet ===")
    shots = pg.evaluate("""() => {
      var T = window.AstroQTeach, a = [];
      ['curved_bright','dots','rays','curved_short'].forEach(function (z) {
        T.pool(z).forEach(function (s) { a.push(T.svg(s)); }); });
      return a;
    }""")
    import re as _re
    gids = [g for s in shots for g in _re.findall(r'id="(tmg\d+)"', s)]
    check(len(gids) == len(set(gids)),
          "id gradient DUY NHAT trong ca me (%d anh)" % len(shots),
          str([g for g in gids if gids.count(g) > 1][:3]))
    check(all(s.startswith("<svg") and s.endswith("</svg>") for s in shots),
          "moi anh la mot the <svg> hoan chinh")
    check(all('role="img"' in s for s in shots), "moi anh co role=img")

    # Chấm (len nhỏ) vẽ bằng <circle>; vệt vẽ bằng <path>. Vẽ chấm bằng một đoạn
    # cực ngắn thì o co nho no doc ra thanh vet ban, khong ra mot ngoi sao.
    dot_svg = pg.evaluate(
        "() => window.AstroQTeach.svg(window.AstroQTeach.POOL.dots[0])")
    trail_svg = pg.evaluate(
        "() => window.AstroQTeach.svg(window.AstroQTeach.POOL.curved_bright[0])")
    check("<path" not in dot_svg, "mau CHAM ve bang circle, khong dung path")
    check("<path" in trail_svg, "mau VET ve bang path")

    # Tất định: cùng mẫu vẽ 2 lần ra y hệt (trừ số thứ tự id).
    two = pg.evaluate("""() => {
      var T = window.AstroQTeach, s = T.POOL.curved_bright[1];
      var a = T.svg(s).replace(/tmg\\d+/g, 'X');
      var b = T.svg(s).replace(/tmg\\d+/g, 'X');
      return a === b;
    }""")
    check(two, "cung mot mau ve 2 lan ra y het (sao nen tat dinh theo id)")

    check(not errs, "van 0 loi trang sau moi phep do", str(errs[:2]))
    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (_ok, _bad))
sys.exit(1 if _bad else 0)
