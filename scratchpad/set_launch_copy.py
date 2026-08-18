# -*- coding: utf-8 -*-
"""
set_launch_copy.py — BỎ LỜI HỨA SẼ HẾT HẠN KHỎI CÁC BỀ MẶT BỊ CACHE.

Chạy MỘT LẦN (18/08/2026). Giữ lại vì nó ghi ra CHÍNH XÁC những chuỗi đã đổi —
đọc lại rẻ hơn nhiều so với đi đọc diff của 4 file.

═══════════════════════ VÌ SAO ═══════════════════════
`<title>`, `meta description` và `og:*` là thứ **BÊN THỨ BA GIỮ BẢN SAO**:
Facebook cache thẻ OG theo URL, Google cache tiêu đề/mô tả. Một khi đã cache thì
**KHÔNG un-cache được** — mà JS thì không cứu được: trình thu thập của Facebook
không chạy JS đáng tin cậy, nên `document.title = t("title")` chỉ đổi thứ người
dùng thấy, không đổi thứ Facebook đã lưu.

⇒ LUẬT: **bề mặt bị bên thứ ba cache không được mang một lời hứa sẽ hết hạn.**

Ngày 20/08/2026 những câu này thành SAI, và bài fanpage đầu tiên sẽ đóng băng
đúng cái sai đó trong bản xem trước:
    "| Sắp Ra Mắt 20/08/2026"          -> hết hạn sau 2 ngày
    "vé mời sớm trước ngày ra mắt"     -> hết hạn
    "Đăng ký sớm / Đăng ký waitlist"   -> hết hạn (mở cửa rồi thì không còn "sớm")
    "dự kiến ra mắt chính thức"        -> hết hạn

⚠️ KHÔNG ĐỔI NGÀY. `20/08/2026` vẫn là ngày mở cửa; thứ bỏ đi là cái KHUNG THỜI
   GIAN quanh nó ("sắp", "trước ngày", "dự kiến"). Đồng hồ đếm ngược, nút mở cửa
   và `LAUNCH_AT` giữ nguyên — chúng nằm trong thân trang, do JS lo, và
   `openDoor()` đã tự lật ở mốc `LAUNCH_AT` từ lượt việc trước.

⚠️⚠️ FAQ HIỂN THỊ VÀ KHỐI JSON-LD PHẢI KHỚP 1-1 (luật đã ghi ở CLAUDE.md mục 2).
   Nên `a5` đổi ở CẢ HAI chỗ bằng cùng một phép thay — đó cũng là lý do không
   chọn cách "cho JS lật câu chữ sau khi mở cửa": JSON-LD là tĩnh, lật một bên
   là hai bên lệch nhau, mà Google coi JSON-LD lệch nội dung là dữ liệu sai.

⚠️ KHÔNG THAY BẰNG MỘT LỜI HỨA HẾT HẠN KHÁC. Đã cân nhắc rồi bỏ chữ "miễn phí":
   hôm nay đúng, nhưng `docs/decisions/009` còn đang mở về việc mở bán — viết vào
   một bề mặt bị cache là tự đặt lại đúng cái bẫy vừa gỡ.

⚠️ SAU KHI CHẠY, BẮT BUỘC:
     1. python scratchpad/gen_home_en.py     (sinh lại en/index.html — ĐỪNG sửa tay)
     2. python scratchpad/check_pages.py     (mục [16] đối chiếu backend <-> LAUNCH_AT)
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

# (đường dẫn, [(cũ, mới, số lần PHẢI khớp, mục đích)])
JOBS = [
    (os.path.join(ROOT, "index.html"), [
        ("<title>astroQ.org — Khám Phá Ngân Hà Tri Thức | Sắp Ra Mắt 20/08/2026</title>",
         "<title>astroQ.org — Khám Phá Ngân Hà Tri Thức | Vũ Trụ · AI · Lượng Tử</title>",
         1, "title: bo 'Sap Ra Mat', thay bang tu khoa khong het han"),

        ("Đăng ký waitlist nhận 500 Purple Meteors & vé mời sớm trước ngày ra mắt 20/08/2026.",
         "Đăng ký bằng email để nhận 500 Purple Meteors khởi đầu.",
         1, "meta description"),

        ("Đăng ký sớm nhận 500 Purple Meteors.",
         "Đăng ký nhận 500 Purple Meteors khởi đầu.",
         1, "og:description"),

        ("Đăng ký waitlist nhận 500 Purple Meteors.",
         "Đăng ký nhận 500 Purple Meteors khởi đầu.",
         1, "twitter:description"),

        # ⚠️ 2 lan: khoi JSON-LD va doan FAQ hien ra. Phai doi CUNG LUC.
        ("astroQ.org dự kiến ra mắt chính thức vào ngày 20/08/2026. Người đăng ký waitlist "
         "bằng email sẽ nhận vé mời sớm cùng 500 Purple Meteors khởi đầu ngay khi hệ thống mở cửa.",
         "astroQ.org mở cửa ngày 20/08/2026. Người đăng ký bằng email nhận 500 Purple "
         "Meteors khởi đầu.",
         2, "a5: FAQ JSON-LD + doan FAQ hien ra (phai khop 1-1)"),

        ("Không spam. Nhận thông báo ra mắt chính thức vào ngày 20/08/2026.",
         "Không spam. Chỉ một thư chào mừng.",
         1, "wl_hint trong markup"),
    ]),

    (os.path.join(ROOT, "js", "index.js"), [
        ('title:"astroQ.org — Khám Phá Ngân Hà Tri Thức | Sắp Ra Mắt 20/08/2026"',
         'title:"astroQ.org — Khám Phá Ngân Hà Tri Thức | Vũ Trụ · AI · Lượng Tử"',
         1, "tu dien vi: title (phai khop <title> tinh)"),

        ('wl_hint:"Không spam. Nhận thông báo ra mắt chính thức vào ngày 20/08/2026."',
         'wl_hint:"Không spam. Chỉ một thư chào mừng."',
         1, "tu dien vi: wl_hint"),

        ('a5:"astroQ.org dự kiến ra mắt chính thức vào ngày 20/08/2026. Người đăng ký waitlist '
         'bằng email sẽ nhận vé mời sớm cùng 500 Purple Meteors khởi đầu ngay khi hệ thống mở cửa."',
         'a5:"astroQ.org mở cửa ngày 20/08/2026. Người đăng ký bằng email nhận 500 Purple '
         'Meteors khởi đầu."',
         1, "tu dien vi: a5"),

        ('title:"astroQ.org — Explore the Galaxy of Knowledge | Launching 20 Aug 2026"',
         'title:"astroQ.org — Explore the Galaxy of Knowledge | Space · AI · Quantum"',
         1, "tu dien en: title"),

        ('wl_hint:"No spam. You\'ll only hear from us at the official launch on 20 August 2026."',
         'wl_hint:"No spam. Just one welcome email."',
         1, "tu dien en: wl_hint"),

        ('a5:"astroQ.org is scheduled to launch on 20 August 2026. Everyone on the email '
         'waitlist gets an early-access pass plus 500 starter Purple Meteors the moment the '
         'system opens."',
         'a5:"astroQ.org opens on 20 August 2026. Everyone who signs up by email gets 500 '
         'starter Purple Meteors."',
         1, "tu dien en: a5"),
    ]),

    (os.path.join(HERE, "gen_home_en.py"), [
        ('"waitlist to get 500 Purple Meteors and an early-access pass before "\n'
         '                   "the 20 August 2026 launch."',
         '"by email to get 500 starter Purple Meteors."',
         1, "EN_META description"),

        ('"for young explorers. Join early and get 500 Purple Meteors."',
         '"for young explorers. Sign up by email for 500 starter Purple Meteors."',
         1, "EN_META og_description"),

        ('"Join the waitlist for 500 Purple Meteors."',
         '"Sign up for 500 starter Purple Meteors."',
         1, "EN_META tw_description"),

        ('"the robot, with 500 Purple Meteors for early sign-ups."',
         '"the robot, with 500 starter Purple Meteors for new sign-ups."',
         1, "EN_META img_alt (alt cua anh OG - cung bi cache)"),
    ]),
]


def main():
    dry = "--dry" in sys.argv
    bad, plans, total = [], [], 0

    for path, subs in JOBS:
        if not os.path.isfile(path):
            bad.append("KHONG THAY FILE: %s" % path)
            continue
        src = io.open(path, encoding="utf-8").read()
        out = src
        for old, new, want, why in subs:
            got = out.count(old)
            if got != want:
                bad.append("%s :: khop %d lan, doi %d  (%s)"
                           % (os.path.basename(path), got, want, why))
                continue
            out = out.replace(old, new)
            total += want
            print("    [%d] %-16s %s" % (want, os.path.basename(path), why))
        plans.append((path, src, out))

    # ⚠️ Lech mot cai la DUNG va KHONG ghi file nao — sua nua voi 4 file nay thi
    #    FAQ hien ra va JSON-LD se noi hai dieu khac nhau.
    if bad:
        print("")
        print("DUNG - khong ghi file nao:")
        for b in bad:
            print("  [HONG] " + b)
        return 1

    print("")
    print("  tong: %d cho" % total)
    if dry:
        print("  --dry: khong ghi gi.")
        return 0
    for path, src, out in plans:
        if src != out:
            io.open(path, "w", encoding="utf-8", newline="").write(out)
    print("  da ghi. NHO chay: gen_home_en.py  roi  check_pages.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
