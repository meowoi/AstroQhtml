# -*- coding: utf-8 -*-
"""
vendor_deps.py — TẢI three.js + Firebase SDK VỀ REPO, cắt hẳn hai tên miền ngoài.

    python scratchpad/vendor_deps.py            # tải + ghi vào vendor/
    python scratchpad/vendor_deps.py --check    # chỉ kiểm, không ghi gì

VÌ SAO CÓ FILE NÀY
------------------
Trước 07/08/2026 dự án kéo hai thư viện từ hai tên miền KHÔNG AI TRONG DỰ ÁN
KIỂM SOÁT:
  · three.js  ← unpkg.com   (explorer.html, importmap)
  · Firebase  ← gstatic.com (js/firebase-auth.js, import động)

Ba cái giá đo được:
  ① Không bao giờ chạy offline được. Service worker KHÔNG cache đàng hoàng
     được phản hồi cross-origin không CORS (chỉ nhận opaque response). Tự host
     là điều kiện TIÊN QUYẾT của PWA, không phải việc dọn dẹp cho đẹp.
  ② unpkg hỏng / bị chặn = màn onboarding BẮT BUỘC của mọi phi hành gia mới
     rơi vào đường lùi 12 giây (js/map-onboard.js). Một tên miền ngoài nằm trên
     đường đi bắt buộc là một điểm hỏng ta không sửa được.
  ③ Bản đang kéo về là bản KHÔNG rút gọn. Đo được: 256.686 gzip, trong khi
     r160 CÓ SẴN `three.module.min.js` chỉ 166.302 gzip — **cắt 35%** trên đúng
     trang nặng nhất của dự án, không đổi một dòng mã nào.

Đây là đúng lối dự án đã đi ngày 26/07/2026 với Google Fonts (621 KB → 101 KB,
bỏ 2 kết nối tới domain ngoài).

⚠️⚠️ HAI CÁI BẪY, cả hai đều làm "tải file về" KHÔNG ĐỦ
--------------------------------------------------------
① **`firebase-auth.js` nhúng URL TUYỆT ĐỐI tới gstatic BÊN TRONG NÓ**
   (`import ... from "https://www.gstatic.com/firebasejs/12.16.0/firebase-app.js"`).
   Tải hai file về rồi chỉ đổi hằng `SDK` ở js/firebase-auth.js thì bản local
   VẪN tự đi kéo firebase-app.js từ gstatic — tức là phụ thuộc **chưa hề bị gỡ**,
   mà đọc mã của dự án thì không thấy gì sai. Script này viết lại URL đó thành
   `./firebase-app.js` và có phép kiểm đòi 0 chuỗi `gstatic.com` còn sót.

② **Addon của three.js import lẫn nhau bằng đường dẫn TƯƠNG ĐỐI**
   (`./Pass.js`, `../shaders/CopyShader.js`). Tải đúng 6 file mà explorer.html
   `import` là thiếu — phải đi ĐỆ QUY và **giữ nguyên cấu trúc thư mục**, không
   thì `EffectComposer.js` tìm `./Pass.js` bên cạnh nó và trả 404 giữa lúc dựng
   cảnh. Đo được: 6 file gốc kéo theo 8 file nữa.

VÌ SAO GIỮ IMPORTMAP thay vì sửa 6 dòng `import`
------------------------------------------------
Addon dùng **bare specifier** `from 'three'` ở bên trong. Importmap giải nó ở
tầng trình duyệt nên đổi 2 URL trong map là xong; bỏ importmap thì phải sửa cả
6 dòng import Ở TRANG *và* mọi dòng `from 'three'` bên trong 14 file addon —
tức là sửa mã của thư viện, và lần nâng cấp sau phải sửa lại từ đầu.

⚠️ VERSION NẰM TRONG ĐƯỜNG DẪN (`vendor/three/0.160.0/…`) — CỐ Ý.
   Nâng cấp = thư mục mới = URL mới = cache cũ chết tự nhiên, không phải nhớ
   xoá gì. Dự án đã trả giá một lần vì cache (06/08/2026, astroq.org đứng ở bản
   04/08 gần một ngày), và service worker sắp tới sẽ làm cache dai hơn nữa.
"""

import gzip
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THREE_VER = "0.160.0"
FB_VER = "12.16.0"

THREE_CDN = "https://unpkg.com/three@%s/" % THREE_VER
FB_CDN = "https://www.gstatic.com/firebasejs/%s/" % FB_VER

THREE_DIR = os.path.join(ROOT, "vendor", "three", THREE_VER)
FB_DIR = os.path.join(ROOT, "vendor", "firebase", FB_VER)

# 6 addon mà explorer.html import thẳng. Phần còn lại script tự lần ra.
THREE_ENTRIES = [
    "controls/OrbitControls.js",
    "postprocessing/EffectComposer.js",
    "postprocessing/RenderPass.js",
    "postprocessing/UnrealBloomPass.js",
    "postprocessing/OutputPass.js",
    "renderers/CSS2DRenderer.js",
]

# Mọi lệnh import/export ... from "..." — kể cả import động import("...").
RE_FROM = re.compile(r"""(?:from|import)\s*\(?\s*["']([^"']+)["']""")

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


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read()


def gz(b):
    return len(gzip.compress(b, 9))


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def norm(base_rel, spec):
    """Giải đường dẫn tương đối của addon về đường dẫn tính từ gốc addons/."""
    base_dir = os.path.dirname(base_rel)
    return os.path.normpath(os.path.join(base_dir, spec)).replace("\\", "/")


def do_three(write_files):
    print("\n[1] three.js %s" % THREE_VER)

    core = fetch(THREE_CDN + "build/three.module.min.js")
    # Bản rút gọn phải là ESM THẬT — có `export{...}` ở cuối. Bản UMD/CJS tải
    # nhầm sẽ im lặng cho ra `THREE is undefined` giữa lúc dựng cảnh.
    check(b"export{" in core or b"export {" in core,
          "three.module.min.js la ESM that (co export)")
    check(len(core) > 400_000, "three.module.min.js du lon", "(%d byte)" % len(core))
    if write_files:
        write(os.path.join(THREE_DIR, "three.module.min.js"), core)
    print("       core: %s tho / %s gzip" % (f"{len(core):,}", f"{gz(core):,}"))

    # ---- addons: đi đệ quy ----
    seen, queue, total = {}, list(THREE_ENTRIES), 0
    while queue:
        rel = queue.pop(0)
        if rel in seen:
            continue
        data = fetch(THREE_CDN + "examples/jsm/" + rel)
        seen[rel] = data
        total += len(data)
        if write_files:
            write(os.path.join(THREE_DIR, "addons", rel), data)
        for spec in RE_FROM.findall(data.decode("utf-8", "replace")):
            if spec.startswith("."):
                nxt = norm(rel, spec)
                if nxt not in seen:
                    queue.append(nxt)
            elif spec != "three" and not spec.startswith("three/"):
                # Addon kéo thêm một thư viện thứ ba (vd. meshopt) — phải biết
                # ngay, không thì nó lại là một tên miền ngoài nữa lọt vào.
                check(False, "addon %s keo phu thuoc la" % rel, "-> %s" % spec)

    extra = sorted(set(seen) - set(THREE_ENTRIES))
    print("       addons: %d file (%d goc + %d keo theo), %s tho"
          % (len(seen), len(THREE_ENTRIES), len(extra), f"{total:,}"))
    for r in extra:
        print("               + %s" % r)

    check(len(seen) >= len(THREE_ENTRIES), "tai du 6 addon goc")
    # Nếu phép đệ quy hỏng thì `seen` chỉ có 6 file và mọi thứ vẫn "đạt" một
    # cách rỗng — nên đòi tường minh rằng nó CÓ lần ra file phụ thuộc.
    check(len(extra) > 0, "phep de quy that su chay (co file keo theo)")

    for rel, data in seen.items():
        for spec in RE_FROM.findall(data.decode("utf-8", "replace")):
            if spec.startswith("."):
                check(norm(rel, spec) in seen,
                      "%s -> %s da co mat" % (rel, spec))
    return len(core) + total


def do_firebase(write_files):
    print("\n[2] Firebase SDK %s" % FB_VER)
    out = {}
    for name in ("firebase-app.js", "firebase-auth.js"):
        raw = fetch(FB_CDN + name).decode("utf-8")

        # ⚠️⚠️ CHỈ VIẾT LẠI URL NẰM TRONG LỆNH IMPORT, KHÔNG THAY BỪA CẢ FILE.
        #    Bản đầu của script này dùng `raw.replace(FB_CDN, "./")` và nó đụng
        #    nhầm **2 chuỗi trong firebase-app.js vốn KHÔNG phải import**:
        #      const name$q = "https://…/firebase-app.js";   ← TÊN COMPONENT
        #      const logger = new Logger('https://…/firebase-app.js');  ← nhãn log
        #    Đó là sổ đăng ký nội bộ của Firebase. Sửa nội tạng thư viện mà không
        #    có lý do là loại thay đổi không ai rà lại được ở lần nâng cấp sau.
        fixed, n = RE_FROM.subn(
            lambda m: m.group(0).replace(FB_CDN, "./"), raw)
        # subn đếm cả lệnh import không đụng gstatic, nên đếm lại cho đúng.
        n = len(re.findall(r"""(?:from|import)\s*\(?\s*["']%s""" % re.escape(FB_CDN), raw))
        print("       %s: viet lai %d URL gstatic trong lenh import" % (name, n))

        specs = RE_FROM.findall(fixed)
        for spec in specs:
            check(spec.startswith("."),
                  "%s: import '%s' la duong dan tuong doi" % (name, spec))
        check(not specs or n > 0 or all(s.startswith(".") for s in specs),
              "%s: khong con import ra mang ngoai" % name)

        # Chuỗi gstatic còn lại PHẢI là nhãn, không phải import — nói ra con số
        # để lần nâng cấp sau nhìn thấy nó chứ không tưởng script bỏ sót.
        left = fixed.count("gstatic.com")
        if left:
            print("       %s: con %d chuoi gstatic (nhan noi bo, khong tai ve)"
                  % (name, left))

        out[name] = fixed.encode("utf-8")
        if write_files:
            write(os.path.join(FB_DIR, name), out[name])

    check(b"firebase-app.js" in out["firebase-auth.js"],
          "firebase-auth.js van tro toi firebase-app.js")
    tot = sum(len(v) for v in out.values())
    print("       tong: %s tho / %s gzip"
          % (f"{tot:,}", f"{sum(gz(v) for v in out.values()):,}"))
    return tot


def main():
    write_files = "--check" not in sys.argv
    print("=" * 66)
    print("  TAI PHU THUOC VE REPO  (%s)" % ("GHI FILE" if write_files else "CHI KIEM"))
    print("=" * 66)

    a = do_three(write_files)
    b = do_firebase(write_files)

    print("\n" + "-" * 66)
    print("  Them vao repo: %s byte tho (~%.2f MB)" % (f"{a + b:,}", (a + b) / 1048576))
    print("  KET QUA: %d dat / %d hong" % (_ok, _bad))
    print("-" * 66)
    return 1 if _bad else 0


if __name__ == "__main__":
    sys.exit(main())
