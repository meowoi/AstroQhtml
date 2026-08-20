#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AstroQ — Rebalance correct-answer positions across A/B/C/D.

Vì sao: nếu đáp án đúng luôn rơi vào cùng một vị trí (vd toàn "A"),
người học sẽ đoán mẹo. Script này phân bố lại vị trí đáp án đúng một cách
*tất định* (theo mã md5 của id câu hỏi) — chạy lại cho kết quả giống nhau,
giữ nguyên nội dung MỌI NGÔN NGỮ (`text`, `text_en`, …) và định dạng JSON dễ đọc.

Dùng:
    python rebalance_answers.py <file_or_glob> [<more> ...]
    python rebalance_answers.py ../ai/level_01.json ../ai/level_02.json
    python rebalance_answers.py "../**/level_*.json"
"""
import sys, glob, json, hashlib
from collections import Counter

LETTERS = ["A", "B", "C", "D"]

def target_slot(qid: str) -> int:
    return int(hashlib.md5(qid.encode("utf-8")).hexdigest(), 16) % 4

def rebalance_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", [])
    for i, q in enumerate(questions):
        opts = q["options"]
        # ⚠️ Đổi chỗ TOÀN BỘ nội dung lựa chọn, không riêng `text`. Từ khi có
        # `text_en`, một lựa chọn mang NHIỀU trường; đổi mỗi `text` thì bản EN
        # đứng yên còn bản VI dịch đi — đáp án đúng ở hai ngôn ngữ trỏ vào hai ô
        # khác nhau, và không có gì báo lỗi. Giữ `id` cố định A/B/C/D theo vị trí.
        bodies = [{k: v for k, v in o.items() if k != "id"} for o in opts]
        cur = LETTERS.index(q["correct_option_id"])
        tgt = target_slot(q["id"])
        bodies[cur], bodies[tgt] = bodies[tgt], bodies[cur]  # đổi chỗ đáp án đúng
        for k in range(4):
            opts[k].clear()
            opts[k]["id"] = LETTERS[k]
            opts[k].update(bodies[k])
        q["correct_option_id"] = LETTERS[tgt]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    dist = Counter(q["correct_option_id"] for q in questions)
    return f"{path}: n={len(questions)}  A={dist['A']} B={dist['B']} C={dist['C']} D={dist['D']}"

def main(argv):
    files = []
    for pat in argv:
        files.extend(glob.glob(pat, recursive=True))
    if not files:
        print("Khong tim thay file .json nao khop.", file=sys.stderr); return 1
    for path in sorted(set(files)):
        print(rebalance_file(path))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
