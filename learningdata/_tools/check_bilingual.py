#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AstroQ — Kiểm bản song ngữ của các file `level_xx.json`.

Vì sao: tiếng Anh nằm ở trường anh em `*_en` trong CÙNG file. File này canh
tính ĐẦY ĐỦ và tính NHẤT QUÁN CẤU TRÚC: đủ cặp VI/EN, đủ 4 lựa chọn, id A–D
đúng thứ tự, `count` khớp, không lựa chọn nào trùng nhau.

⚠️ **Thứ file này KHÔNG kiểm được — và không công cụ cấu trúc nào kiểm được:**
hai `text_en` bị HOÁN VỊ cho nhau. Sau khi hoán vị, cả 4 chuỗi EN vẫn còn đủ,
vẫn khác nhau, JSON vẫn hợp lệ — không còn dấu vết nào để bám. Muốn bắt ca đó
thì phải đọc nghĩa, tức là việc của người rà.

Hàng rào thật cho ca đó nằm ở chỗ khác: `rebalance_answers.py` đổi chỗ **cả
object lựa chọn**, nên công cụ duy nhất có quyền xáo thứ tự không thể tách cặp.
Rủi ro còn lại chỉ đến từ sửa tay.

Không sửa file, chỉ báo. Trả mã thoát 1 nếu có lỗi.

Dùng:
    python check_bilingual.py ../ai/level_01.json ../ai/level_02.json
    python check_bilingual.py "../**/level_*.json"
"""
import sys, glob, json

# Trường VI (gốc) -> trường EN bắt buộc đi kèm.
Q_PAIRS = ["topic", "grade_target", "mascot_dialog", "question_text", "explanation"]
W_PAIRS = ["topic", "grade_target"]
LETTERS = ["A", "B", "C", "D"]


def check_file(path):
    errs = []
    try:
        data = json.loads(open(path, encoding="utf-8").read())
    except Exception as e:
        return [f"{path}: khong doc duoc JSON — {e}"]

    qs = data.get("questions", [])
    if data.get("count") != len(qs):
        errs.append(f"{path}: `count`={data.get('count')} khac so cau thuc te {len(qs)}")

    for k in W_PAIRS:
        if data.get(k) and not str(data.get(k + "_en", "")).strip():
            errs.append(f"{path}: bao ngoai thieu `{k}_en`")

    for q in qs:
        qid = q.get("id", "<khong co id>")
        for k in Q_PAIRS:
            if q.get(k) and not str(q.get(k + "_en", "")).strip():
                errs.append(f"{path} {qid}: thieu `{k}_en`")

        opts = q.get("options", [])
        if len(opts) != 4:
            errs.append(f"{path} {qid}: co {len(opts)} lua chon, phai la 4")
            continue
        if [o.get("id") for o in opts] != LETTERS:
            errs.append(f"{path} {qid}: id lua chon phai la A,B,C,D theo thu tu")
        if q.get("correct_option_id") not in LETTERS:
            errs.append(f"{path} {qid}: `correct_option_id` khong hop le")

        vi = [o.get("text", "") for o in opts]
        en = [o.get("text_en", "") for o in opts]
        if not all(str(t).strip() for t in vi):
            errs.append(f"{path} {qid}: co lua chon thieu `text`")
        if any(str(t).strip() for t in en):          # da bat dau co EN thi phai du 4
            if not all(str(t).strip() for t in en):
                errs.append(f"{path} {qid}: co lua chon thieu `text_en` (dang do dang)")
            elif len(set(en)) != 4:
                # Bat duoc ca CHEP DE (mot `text_en` bi dan de len cai khac).
                # KHONG bat duoc ca HOAN VI — xem canh bao o dau file.
                errs.append(f"{path} {qid}: hai lua chon EN trung nhau")
        if len(set(vi)) != 4:
            errs.append(f"{path} {qid}: hai lua chon VI trung nhau")

    return errs


def main(argv):
    files = []
    for pat in argv:
        files.extend(glob.glob(pat, recursive=True))
    if not files:
        print("Khong tim thay file .json nao khop.", file=sys.stderr)
        return 1

    total = 0
    for path in sorted(set(files)):
        errs = check_file(path)
        total += len(errs)
        if errs:
            for e in errs:
                print("  LOI " + e)
        else:
            n = len(json.loads(open(path, encoding="utf-8").read()).get("questions", []))
            print(f"  ok  {path}: {n} cau, VI/EN du truong + cau truc hop le "
                  f"(nghia cua ban dich KHONG kiem duoc bang may)")
    print(f"\n{'DAT' if not total else str(total) + ' LOI'}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
