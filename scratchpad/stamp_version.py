# -*- coding: utf-8 -*-
r"""Đóng dấu số hiệu bản dựng vào `js/ui-common.js`. CHẠY TRƯỚC MỖI LẦN PUSH.

    python scratchpad/stamp_version.py          → tăng số hiệu
    python scratchpad/stamp_version.py --xem    → chỉ in ra, không sửa

⚠️ VÌ SAO PHẢI CÓ SCRIPT, KHÔNG GÕ TAY. Số hiệu gõ tay là số hiệu sẽ quên bump —
   và một số hiệu đứng yên còn tệ hơn không có số hiệu nào, vì nó nói SAI rằng
   người dùng đang ở bản mới. Ngày 06/08/2026 bản thật đứng ở bản 04/08 gần một
   ngày do deploy hết giờ hai lần liên tiếp; đúng loại tình huống mà một con số
   sai sẽ dẫn người đi sửa sai chỗ.

⚠️ ĐỊNH DẠNG `YYYY.MM.DD.n` CỐ Ý KHÔNG MANG MÃ COMMIT. Mã commit của chính lần
   commit chứa dấu này chưa tồn tại lúc đóng dấu, nên mọi cách nhét SHA vào đều
   lệch đúng một commit — một con số gần đúng ở chỗ này là con số dẫn người đọc
   tới sai commit. Ngày + số thứ tự trong ngày thì luôn đúng, và `git log --since`
   đủ để lần ra commit tương ứng.

⚠️ VIẾT THÀNH FILE, KHÔNG CHẠY QUA HEREDOC — heredoc của shell ăn mất dấu `\` trong
   regex. Bài học đã ghi trong CLAUDE.md và đã mắc lại ba lần trong phiên 06/08.
"""
import datetime
import io
import re
import sys

FILE = "js/ui-common.js"
# Bám ĐÚNG dòng khai báo, không bám chuỗi trần — chuỗi "2026.08.07.1" có thể xuất
# hiện ở chỗ khác (ghi chú, ví dụ) và sửa nhầm thì lỗi rất khó thấy.
PAT = re.compile(r'(var VERSION = ")(\d{4}\.\d{2}\.\d{2}\.\d+)(";)')


def main():
    s = io.open(FILE, encoding="utf-8").read()
    m = PAT.search(s)
    if not m:
        print("*** không tìm thấy dòng `var VERSION = \"…\";` trong " + FILE)
        print("    Nếu vừa đổi tên biến thì sửa PAT ở đầu script này.")
        sys.exit(1)

    cu = m.group(2)
    hom_nay = datetime.date.today().strftime("%Y.%m.%d")
    ngay_cu, so_cu = cu.rsplit(".", 1)
    moi = hom_nay + ".1" if ngay_cu != hom_nay else hom_nay + "." + str(int(so_cu) + 1)

    if "--xem" in sys.argv:
        print(f"  hiện tại : {cu}")
        print(f"  sẽ thành : {moi}   (chạy không kèm --xem để ghi)")
        return

    io.open(FILE, "w", encoding="utf-8").write(PAT.sub(r"\g<1>" + moi + r"\g<3>", s, count=1))
    print(f"  {cu}  →  {moi}")
    print(f"  đã ghi vào {FILE}. Nhớ commit file này cùng lượt push.")


if __name__ == "__main__":
    main()
