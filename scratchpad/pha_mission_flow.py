# -*- coding: utf-8 -*-
"""
pha_mission_flow.py — PHÉP THỬ PHÁ HOẠI cho mục [20] của check_pages.py.

    set PYTHONIOENCODING=utf-8
    python scratchpad/pha_mission_flow.py

⚠️ VÌ SAO CÓ FILE NÀY. Một phép kiểm "đạt" chưa chứng minh gì — dự án đã nhiều lần
   phát hiện phép kiểm ĐẠT MỘT CÁCH RỖNG (quét `idx[0]` thay vì cả mục lục · miễn trừ
   theo phạm vi cả tài liệu · `try/catch` nuốt lỗi rồi vẫn báo xanh). Cách duy nhất
   biết một phép kiểm có RĂNG là cố tình làm hỏng đúng thứ nó canh rồi xem nó có đỏ.

⚠️ SAO LƯU VÀ KHÔI PHỤC TRONG CÙNG MỘT TIẾN TRÌNH PYTHON. Bài học 02/08/2026: `/tmp`
   của Git Bash và `/tmp` của Python là hai chỗ khác nhau, và một lần khôi phục hụt đã
   để lại repo ở trạng thái đã bị phá. `finally` ở đây luôn trả file về nguyên trạng.
"""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = os.path.join(ROOT, "scratchpad", "check_pages.py")

CASES = [
    # (nhãn, file, chuỗi cũ, chuỗi mới, số phép kiểm PHẢI đỏ ít nhất)
    ("bo mot chang khoi danh muc",
     "js/mission-catalog.js",
     '        { id: "eco", ic: "♻️",',
     '        { id: "eco-XX", ic: "♻️",', 1),

    ("nhet con so thuong vao danh muc",
     "js/mission-catalog.js",
     '      id: "earth", world: "earth", file: "mission-earth.html", ic: "🌍",',
     '      id: "earth", world: "earth", file: "mission-earth.html", ic: "🌍", tt: 20,', 1),

    ("nhiem vu tro toi mot trang choi khong ton tai",
     "js/mission-catalog.js",
     'file: "mission-earth.html"',
     'file: "mission-mars.html"', 1),

    ("nhet Mat Trang vao js/planets.js (world-id lan sang planet-id)",
     "js/planets.js",
     '    { id:"mars",    vi:"Sao Hoả",  en:"Mars",    c:"#d6603a", c2:"#7a3320" },',
     '    { id:"mars",    vi:"Sao Hoả",  en:"Mars",    c:"#d6603a", c2:"#7a3320" },\n'
     '    { id:"moon",    vi:"Mặt Trăng", en:"Moon",   c:"#d3cfc4", c2:"#74706a" },', 1),

    # WARN MOC NAY DA CHUYEN SANG VO 15/08/2026 — `afterStep` nay nam trong
    #   `js/mission-stage.js`. De nguyen duong dan cu thi phep pha "khong pha dung cho",
    #   va script TU BAO dieu do thay vi im lang bao "6/7 bi bat" — do la ly do no lo ra.
    #   Mot phep pha khong pha trung cho thi ket qua cua no khong dung de ket luan gi.
    ("bo chan chang cuoi -> hop hoi mo ca o chang cuoi",
     "js/mission-stage.js",
     "      if (last) return false;\n",
     "      if (false && last) return false;\n", 1),

    ("cho ban do tu tinh nguong cong thay vi hoi AstroQGate",
     "mission-map.html",
     "    var can = !window.AstroQGate || AstroQGate.canVisit(id);",
     "    var can = Math.ceil(7 * 0.7) <= 3;", 1),

    ("cay chang thoi doc danh muc (go lai ten chang)",
     "mission-tree.html",
     "  var M = AstroQCatalog.find(MID);",
     "  var M = { id:'earth', world:'earth', file:'mission-earth.html', ic:'🌍',\n"
     "            vi:{nm:'X',tag:'X'}, en:{nm:'X',tag:'X'}, steps:[] };", 1),
]


def run_check():
    # ⚠️ ĐỌC BYTE RỒI TỰ GIẢI MÃ UTF-8. `text=True` để Python dùng codec MẶC ĐỊNH của
    #    máy (cp1252 trên Windows), và một ký tự tiếng Việt trong output là
    #    `UnicodeDecodeError` NÉM TỪ MỘT LUỒNG NỀN — `r.stdout` thành `None` và lỗi
    #    thật bị che sau một `TypeError` khó đọc. Cùng họ với bẫy `PYTHONIOENCODING`
    #    đã ghi ở quy tắc mục 6.
    r = subprocess.run([sys.executable, CHECK], cwd=ROOT, capture_output=True,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    out = (r.stdout or b"").decode("utf-8", "replace") + \
          (r.stderr or b"").decode("utf-8", "replace")
    # ⚠️ Dem dong bat dau bang `[HONG]`, KHONG dem chuoi "HONG" tron: nhan `[OK]` cua
    #    mot phep kiem co the chua chu "KHONG" va lam phep dem sai (bai hoc 31/07).
    return sum(1 for ln in out.splitlines() if ln.strip().startswith("[HONG]"))


def main():
    base = run_check()
    print(f"Nen: {base} phep kiem dang hong (phai la 0)\n")
    if base != 0:
        print("  [!] Dang co phep kiem hong san — sua truoc roi hay pha.")
        sys.exit(1)

    ok = 0
    for label, rel, old, new, need in CASES:
        p = os.path.join(ROOT, rel)
        orig = io.open(p, encoding="utf-8").read()
        if orig.count(old) < 1:
            print(f"  [!] {label}: KHONG tim thay moc trong {rel} — phep pha nay khong "
                  f"pha dung cho, ket qua khong dung de ket luan.")
            continue
        try:
            # WARN `newline=""` LA BAT BUOC. Thieu no thi tren Windows Python doi moi
            #   dau xuong dong LF thanh CRLF khi ghi, nen file KHOI PHUC xong giong het
            #   ve NOI DUNG ma khac ve KIEU XUONG DONG — git bao CA FILE bi sua (435
            #   dong o `mission-map.html`), va mot lan chay bo pha hoai lam ban ca commit.
            #   Loi im lang: bo do van bao "khoi phuc xong, 0 hong".
            io.open(p, "w", encoding="utf-8", newline="").write(orig.replace(old, new, 1))
            n = run_check()
        finally:
            io.open(p, "w", encoding="utf-8", newline="").write(orig)
        got = n - base
        if got >= need:
            ok += 1
            print(f"  [BAT DUOC] {label} -> {got} phep kiem bao hong")
        else:
            print(f"  [LOT]      {label} -> chi {got} phep kiem bao hong (can >= {need})")

    print(f"\n=== {ok}/{len(CASES)} phep pha bi BAT ===")
    # Kiem lai: moi file da tro ve nguyen trang
    end = run_check()
    print(f"Sau khi khoi phuc: {end} phep kiem hong (phai la 0)")
    sys.exit(0 if ok == len(CASES) and end == 0 else 1)


if __name__ == "__main__":
    main()
