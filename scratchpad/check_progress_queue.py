# -*- coding: utf-8 -*-
"""check_progress_queue.py — HANG CHO cua js/progress.js co giu duoc viec tre vua lam.

VI SAO CO BO DO NAY (21/08/2026)
--------------------------------
Chu du an choi that roi bao hai chuyen:
  1. "Choi xong chang thu 1 khong thay dong dau chang 1 du da xong" (cay chang).
  2. "Xong quiz khong cong thien thach ngay, vi sao bi cham".

Doc code ra hai lo hong o CUNG mot cho — hang cho trong `js/progress.js`:

  [A] `report()` chi `enqueue()` SAU khi `waitAuth(2500)` tra ve tay khong.
      Ma `quiz.html` / `games.html` / cac trang game CO Y khong nap
      `js/firebase-auth.js`, nen o do `waitAuth` LUON chay het 2,5 giay. Tre bam
      "Choi lai" / "Ve" trong khoang do la trang unload truoc khi hen gio no
      => ca luot choi bien mat (khong thien thach, khong XP, khong thuat ngu).

  [B] Trang CO token chay HAI loi goi song song: `flush()` (POST viec vua choi)
      va mot route doc (GET tien do). GET thuong ve TRUOC POST => trang ve dung
      trang thai TRUOC khi choi, va ve xong thi khong ve lai nua.

  [C] `flush()` chup danh sach hang cho luc bat dau roi ghi de `[]` luc xong —
      xoa thang viec duoc xep vao GIUA duong. Voi [A] da sua thi duong nay tro
      thanh duong chinh, nen phai sua cung luc.

Bo do nay do CA BA, tren chinh `js/progress.js` that (khong ban sao), bang cach
gia lap `AstroQAuth` voi do tre mang tu chon — tuc do dung cai thu tu ma bug can.

  python scratchpad/check_progress_queue.py
"""
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

HARNESS = pathlib.Path(__file__).with_name("_progress_queue_harness.html").resolve()


def main():
    if not HARNESS.exists():
        print("[X] Khong thay " + HARNESS.name)
        return 1

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(HARNESS.as_uri())
        pg.wait_for_function("document.getElementById('out').textContent.indexOf('END') >= 0",
                             timeout=30000)
        out = pg.inner_text("#out")
        b.close()

    lines = [l for l in out.splitlines() if re.match(r"^(PASS|FAIL)\s", l)]
    for l in lines:
        print("  " + l)
    for e in errs:
        print("  FAIL  loi JS: " + e)

    bad = [l for l in lines if l.startswith("FAIL")] + errs
    print()
    print("=== KET QUA: %d dat / %d hong ===" % (len(lines) - len(bad) + 0, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
