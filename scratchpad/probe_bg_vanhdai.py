# -*- coding: utf-8 -*-
"""
probe_bg_vanhdai.py — GẮN THỬ nền `vanhdai` vào dashboard THẬT rồi đo, 5 khổ màn.

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/probe_bg_vanhdai.py

⚠️ KHÔNG SỬA `dashboard.html`. Nền được thay ngay trong trang bằng JS — đúng cách
   loại món `bg` sẽ hoạt động sau này (JS sinh srcset theo món đang đeo), nên phép
   đo này đo đúng cơ chế thật chứ không đo một bản chép tay.

ĐO GÌ (những thứ chỉ đo mới thấy):
  1. ẢNH NÀO THẬT SỰ ĐƯỢC TẢI — `currentSrc`. Bộ biến thể mới là 1536/1024 trong khi
     bản cũ là 1920/1280; gõ nhầm một chữ trong srcset là trình duyệt lặng lẽ lùi về
     `<img src>` và mọi kết luận phía sau đều sai.
  2. KHUNG BUỒNG LÁI CÒN LẠI BAO NHIÊU sau `object-fit:cover` — đây là câu hỏi đã
     làm rớt ảnh có khung chỉ ở mép dưới. Đo bằng cách đọc pixel ở 4 mép của ảnh
     ĐANG HIỂN THỊ, không phải của file gốc.
  3. ĐỘ SÁNG NGAY DƯỚI CHỮ HERO — chữ hero màu TRẮNG. Lớp phủ `.bg-photo::after`
     chỉ rgba(6,12,34,.28) ở dải giữa nên nó KHÔNG cứu được nền sáng.
  4. Tràn ngang · lỗi console · asset 404 ở từng cỡ.
"""
import io
import json
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
OUT = "scratchpad"

USER = {"name": "Bi", "pilotName": "Bi", "character": "raica",
        "avatar": "ava/avaraica.png", "uid": "probe-bg-uid",
        "selectedCharacter": "raica"}

# (ten, w, h) — cỡ thật, chọn để phủ cả hai kiểu cắt của cover.
VIEWS = [("dienthoai", 390, 844), ("tablet", 820, 1180), ("laptop", 1440, 900),
         ("manrong", 1920, 900), ("m16x9", 1920, 1080)]

# Thay nền ngay trong trang, đúng cách JS của loại món `bg` sẽ làm.
SWAP = """(slug) => {
  const p = document.querySelector('.bg-photo picture');
  if (!p) return 'KHONG THAY .bg-photo picture';
  const ws = [1024, 1536];
  p.querySelectorAll('source').forEach(s => {
    const t = s.type === 'image/avif' ? 'avif' : 'webp';
    s.srcset = ws.map(w => `background/${slug}-${w}.${t} ${w}w`).join(', ');
  });
  const img = p.querySelector('img');
  img.width = 1536; img.height = 1003;
  img.src = `background/${slug}-1536.webp`;
  return 'ok';
}"""

_pass = _fail = 0


def check(label, ok, detail=""):
    global _pass, _fail
    if ok:
        _pass += 1
        print("  [DAT ] %s %s" % (label, detail))
    else:
        _fail += 1
        print("  [HONG] %s %s" % (label, detail))


def edge_brightness(png_bytes, w, h):
    """Độ sáng 4 mép + dải chữ hero, đọc từ ẢNH CHỤP THẬT của khung nhìn."""
    im = Image.open(io.BytesIO(png_bytes)).convert("L")
    iw, ih = im.size

    def band(box):
        px = list(im.crop(box).getdata())
        return sum(px) / len(px)

    t = int(ih * 0.04)
    return {
        "trai": band((0, int(ih * .3), int(iw * .06), int(ih * .8))),
        "phai": band((int(iw * .94), int(ih * .3), iw, int(ih * .8))),
        "duoi": band((int(iw * .2), ih - t, int(iw * .8), ih)),
        "hero": band((int(iw * .06), int(ih * .28), int(iw * .6), int(ih * .5))),
    }


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "vanhdai"
    print("Gan thu nen '%s' vao dashboard that\n" % slug)

    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for name, w, h in VIEWS:
            ctx = br.new_context(viewport={"width": w, "height": h},
                                 device_scale_factor=1)
            # ⚠️ Phải tắt tour Comet, không thì hộp thoại phủ kín giữa màn và mọi
            #    phép đo độ sáng nền đọc phải cái hộp chứ không phải ảnh nền.
            ctx.add_init_script(
                "localStorage.setItem('astroq-user', %s);"
                "localStorage.setItem('astroq-tour-seen', '1');"
                % json.dumps(json.dumps(USER)))
            pg = ctx.new_page()
            errs, bad = [], []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("response", lambda r: bad.append("%d %s" % (r.status, r.url))
                  if r.status >= 400 else None)

            pg.goto(BASE + "/dashboard.html", wait_until="networkidle")
            r = pg.evaluate(SWAP, slug)
            print("%s  %dx%d  (swap: %s)" % (name, w, h, r))
            pg.wait_for_timeout(700)

            cur = pg.evaluate("() => document.querySelector('.bg-photo img').currentSrc")
            check("tai dung bo bien the moi", slug in cur and "-19" not in cur,
                  cur.split("/")[-1])

            ov = pg.evaluate("() => document.documentElement.scrollWidth - "
                             "document.documentElement.clientWidth")
            check("khong tran ngang", ov <= 0, "lech %dpx" % ov)

            shot = pg.screenshot()
            b = edge_brightness(shot, w, h)
            # ⚠️ PHÉP KIỂM NÀY CHỈ ĐO MÉP CÓ TỐI KHÔNG — NÓ KHÔNG CHỨNG MINH ĐƯỢC
            #    CÒN CẤU TRÚC BUỒNG LÁI. Đã thử: ảnh vũ trụ TRẦN (không buồng lái)
            #    cũng ĐẠT ở 56,1/68,2 vì một góc trời tối thì cũng dưới ngưỡng.
            #    Giữ nó vì cái nó thật sự đo vẫn đáng đo (mép sáng thì card và chữ
            #    ở rìa mất tương phản), nhưng ĐỪNG đọc nó thành "khung còn nguyên"
            #    — muốn thế thì phải so khớp hình dạng, không so độ sáng.
            check("mep trai/phai du toi",
                  b["trai"] < 70 and b["phai"] < 70,
                  "trai %.1f phai %.1f" % (b["trai"], b["phai"]))
            check("dai chu hero du toi (<70)", b["hero"] < 70,
                  "hero %.1f" % b["hero"])
            check("0 loi console", not errs, "; ".join(errs[:2]))
            check("0 asset hong", not bad, "; ".join(bad[:2]))

            with open("%s/bg_%s_%s.png" % (OUT, slug, name), "wb") as f:
                f.write(shot)
            ctx.close()
            print()
        br.close()

    print("KET QUA: %d dat, %d hong" % (_pass, _fail))
    return 1 if _fail else 0


if __name__ == "__main__":
    sys.exit(main())
