# -*- coding: utf-8 -*-
"""Sinh 6 anh BAN DONG HANH cho console phai cua khung game.

    python scratchpad/make_mate_assets.py            # sinh
    python scratchpad/make_mate_assets.py --do       # chi DO, khong ghi

Nguon la art goc da co san trong `img/` — SAU cai da nam trong danh sach "chua ai
dung" tu dot toi uu anh 26/07/2026. Khong ve moi cai nao.

⚠️⚠️ MOI ANH DUOC DUA VE CUNG MOT KHUNG VUONG. Sau tu the co ti le rat khac nhau
   (Comet bay thi NGANG, Comet dung thi DOC; Byte cam khien rong hon Byte deo kinh).
   Tha thang vao mot o `object-fit:contain` thi moi lan doi bieu cam nhan vat NHAY
   CO — dung cai loi "so tren HUD nhay" da phai chua bang `tabular-nums`. Dua ve
   cung khung, cung le, thi doi anh chi doi HINH chu khong doi CO.

⚠️ Ti le trong khung lay theo CHIEU CAO cua duong bao alpha, tru tu the bay cua
   Comet (`m1`) — no nam CHEO nen do theo chieu cao se ra mot con meo to gap ruoi
   may tu the kia. Rieng no lay theo canh dai.

⚠️ Co 208 = 2x cua o hien thi 104px, du net cho man DPR 2. Nen PNG bang mau 256
   (FASTOCTREE, GIU alpha) — dung `convert("P", palette=ADAPTIVE)` la lam phang
   alpha thanh trong-suot-nhi-phan, tuc chat het vien mem quanh nhan vat (bai hoc
   da ghi o dot toi uu 26/07).
"""
import os
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "img")
OUT = os.path.join(ROOT, "img", "mate")
BOX = 208                 # 2x cua o 104px
MARGIN = 6                # le trong khung, de vien mem khong cham mep
DRY = "--do" in sys.argv

# (ten file ra, anh nguon, do theo canh dai thay vi chieu cao?)
JOBS = [
    ("comet-idle.png",  "m1.png", True),   # bay, cam ban do — tu the CHEO
    ("comet-cheer.png", "m4.png", False),  # gio ngon cai, mat quyet tam
    ("comet-oops.png",  "m2.png", False),  # ngac nhien, tay dua len dau
    ("byte-idle.png",   "b2.png", False),  # chieu qua dia cau — "dang lam viec"
    ("byte-cheer.png",  "b4.png", False),  # deo kinh ram, khoanh tay
    ("byte-oops.png",   "b3.png", False),  # man hinh ERROR 404, ang-ten boc khoi
]


def build(src_name, by_long_side):
    im = Image.open(os.path.join(SRC, src_name)).convert("RGBA")
    bb = im.getbbox()
    if not bb:
        raise SystemExit(f"{src_name}: anh rong")
    im = im.crop(bb)
    room = BOX - 2 * MARGIN
    ref = max(im.width, im.height) if by_long_side else im.height
    k = room / ref
    w, h = max(1, round(im.width * k)), max(1, round(im.height * k))
    if w > room:                       # tu the qua ngang thi ep theo be rong
        k = room / im.width
        w, h = room, max(1, round(im.height * k))
    im = im.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (BOX, BOX), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((BOX - w) // 2, (BOX - h) // 2))
    return canvas


def main():
    if not DRY:
        os.makedirs(OUT, exist_ok=True)
    total = 0
    print(f"{'file ra':22} {'nguon':10} {'hinh trong khung':18} {'byte':>8}")
    for out_name, src_name, by_long in JOBS:
        img = build(src_name, by_long)
        bb = img.getbbox()
        shape = f"{bb[2]-bb[0]}x{bb[3]-bb[1]}"
        path = os.path.join(OUT, out_name)
        # ⚠️ `quantize` chu KHONG phai `convert("P")` — xem ghi chu dau file.
        q = img.quantize(colors=256, method=Image.FASTOCTREE)
        if DRY:
            import io
            buf = io.BytesIO()
            q.save(buf, "PNG", optimize=True)
            n = buf.tell()
        else:
            q.save(path, "PNG", optimize=True)
            n = os.path.getsize(path)
        total += n
        print(f"{out_name:22} {src_name:10} {shape:18} {n:>8,}")

    print(f"\ntong: {total:,} byte" + ("  (CHI DO, khong ghi)" if DRY else
                                       f"  -> {OUT}"))
    # Cung mot khung thi moi anh phai cung kich thuoc file-vuong — kiem lai cho chac.
    if not DRY:
        sizes = {Image.open(os.path.join(OUT, n)).size for n, _, _ in JOBS}
        assert sizes == {(BOX, BOX)}, f"khung khong dong deu: {sizes}"
        print(f"moi anh deu {BOX}x{BOX} — doi bieu cam se khong lam nhan vat nhay co")


if __name__ == "__main__":
    main()
