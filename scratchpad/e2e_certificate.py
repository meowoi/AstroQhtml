# -*- coding: utf-8 -*-
"""e2e_certificate.py — CHỨNG NHẬN VỚI MỘT TÀI KHOẢN ĐÃ LÊN BẬC THẬT.

`smoke_certificate.py` đo được mọi thứ TRỪ một điều: nút chứng nhận có thật sự hiện ra
khi trẻ đã hoàn thành một chặng hay không — nó chạy khi chưa đăng nhập nên 0 bậc `done`
và 0 nút, tức phép kiểm "số nút = số bậc đã xong" xanh một cách rỗng (0 = 0).

Bộ này dựng một tài khoản THẬT, đặt XP đủ để hoàn thành hai chặng đầu, rồi ĐĂNG NHẬP
THẬT trên trang và đọc những gì trẻ nhìn thấy.

⚠️ ĐẶT XP THẲNG VÀO BẢNG. Không farm XP qua API vì hạn mức 5 lượt Quiz/ngày (vừa dựng
   hôm nay) sẽ chặn — và đó là hành vi ĐÚNG. Ở đây tôi gieo TRẠNG THÁI để đo giao diện,
   không phải đi vòng qua một luật sản phẩm.

⚠️ Tự dọn: mọi dòng DynamoDB + tài khoản Firebase tạm.

  python scratchpad/e2e_certificate.py
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, "scratchpad")
import _fbtest

from playwright.sync_api import sync_playwright

# ⚠️ CONG 8000, KHONG PHAI 8123. `ALLOWED_ORIGINS` cua server khong co 8123 nen moi
#    loi goi API bi CORS chan, va `AstroQProgress.achievements()` tra `reason:"net"` —
#    trang khong doc duoc cap do, khong bac nao `done`, va bo do bao hong OAN. Lan chay
#    dau toi mat mot vong vi dung 8123; luat nay da ghi trong CLAUDE.md cho smoke_waitlist.
SITE = "http://127.0.0.1:8000"
API = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
TABLE = "astroq-main"
NAME = "Trần Khánh Linh"

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True)


def rows(pk):
    # ⚠️⚠️ CHI LAY `PK,SK`. Ban dau khong khai projection nen `aws` phai in ca truong
    #    `name` — va voi mot cai ten tieng Viet ("Tran Khanh Linh") thi CLI chet o
    #    cp1252: `'charmap' codec can't encode character '\u1ea7'`. Khi do phep dem
    #    duoi day tra [] va phan don in ra "da xoa 0 dong, con lai 0" — tuc BAO THANH
    #    CONG trong khi bon tai khoan test nam lai trong bang that (do duoc 19/08/2026).
    #    Dat PYTHONIOENCODING cho tien trinh con KHONG cuu duoc; bo truong do ra thi cuu.
    r = aws("dynamodb", "query", "--table-name", TABLE, "--consistent-read",
            "--key-condition-expression", "PK = :p",
            "--expression-attribute-values", json.dumps({":p": {"S": pk}}),
            # `type` la TU KHOA DU TRU cua DynamoDB nen phai di qua `#t`. Giu lai
            # truong nay vi phep kiem nhat ky dem theo no; con `name` (cho co dau
            # tieng Viet lam `aws` chet o cp1252) thi KHONG lay.
            "--projection-expression", "PK,SK,#t",
            "--expression-attribute-names", json.dumps({"#t": "type"}),
            "--output", "json")
    if r.returncode != 0:
        # ⚠️ NOI RA, dung tra [] cho xong. Mot phep do noi doi theo huong an tam la
        #    thu te nhat trong ca bo do.
        print("      ⚠️ TRUY VAN HONG cho %s: %s" % (pk, (r.stderr or "").strip()[:120]))
        raise RuntimeError("khong doc duoc bang de don du lieu test")
    if not r.stdout.strip():
        return []
    return json.loads(r.stdout).get("Items", [])


def call(method, path, token=None):
    req = urllib.request.Request(API + path, method=method)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, {}


uid = tok = pw = None
email = "cert-e2e-%s@astroq-test.invalid" % uuid.uuid4().hex[:10]
try:
    print("\n=== [1] Dựng một đứa trẻ đã hoàn thành hai chặng đầu ===")
    uid, tok, pw = _fbtest.make_verified(email)
    aws("dynamodb", "put-item", "--table-name", TABLE, "--item",
        json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": {"S": "PROFILE"},
                    "uid": {"S": uid}, "email": {"S": email},
                    "name": {"S": NAME},
                    "createdAt": {"S": "2026-08-19T00:00:00.000Z"}}))
    # XP đủ cao để vượt qua bậc 1 và bậc 2 (mỗi bậc 5 cấp).
    aws("dynamodb", "put-item", "--table-name", TABLE, "--item",
        json.dumps({"PK": {"S": "USER#%s" % uid}, "SK": {"S": "PROGRESS"},
                    "xp": {"N": "20000"}}))
    st, d = call("GET", "/me/profile", tok)
    lv = ((d or {}).get("level") or {}).get("level")
    check("server nói trẻ đang ở cấp %s" % lv, st == 200 and (lv or 0) >= 11,
          "cap %s" % lv)

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 1000}, locale="vi-VN")
        ctx.add_init_script("try{localStorage.setItem('astroq-lang','vi');"
                            "localStorage.setItem('astroq-tour-seen','1')}catch(e){}")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        print("\n=== [2] Đăng nhập thật ===")
        pg.goto(SITE + "/landing-app.html", wait_until="load")
        pg.wait_for_selector("#btn-try", timeout=25000)
        pg.click("#btn-try")
        pg.wait_for_selector("#to-login", state="visible", timeout=25000)
        pg.click("#to-login")
        pg.wait_for_selector("#login-email", state="visible", timeout=25000)
        pg.fill("#login-email", email)
        pg.fill("#login-pass", pw)
        pg.click("#auth-login button.auth-submit")
        for _ in range(40):
            try:
                if pg.evaluate("()=>!!(window.AstroQ&&AstroQ.getUser&&AstroQ.getUser())"):
                    break
            except Exception:
                pass
            pg.wait_for_timeout(500)
        check("đăng nhập thành công", pg.evaluate("()=>!!AstroQ.getUser()"))

        print("\n=== [3] Kho Thành Tích: nút chứng nhận CÓ hiện ===")
        pg.goto(SITE + "/achievements.html", wait_until="load")
        # ⚠️ CHỜ THEO ĐIỀU KIỆN, không theo đồng hồ. Trang phải nạp SDK Firebase rồi
        #    gọi `/me/achievements`; một con số giây cố định là phép đo phụ thuộc mạng
        #    — lần chạy đầu 5 giây không đủ và bộ đo báo hỏng OAN.
        for _ in range(40):
            if pg.locator(".rk.done").count() > 0:
                break
            pg.wait_for_timeout(500)
        n_done = pg.locator(".rk.done").count()
        if n_done == 0:
            print("      [chan doan] cap trang doc duoc: %s"
                  % pg.evaluate("()=>{const e=document.querySelector('#ld-count');"
                                "return e?e.innerText:'?'}"))
        n_cert = pg.locator(".rk-cert").count()
        n_now = pg.locator(".rk.now .rk-cert").count()
        check("có bậc đã hoàn thành (không còn 0 = 0 rỗng)", n_done >= 2,
              "%d bậc done" % n_done)
        check("số nút chứng nhận = số bậc đã hoàn thành", n_cert == n_done,
              "cert=%d done=%d" % (n_cert, n_done))
        check("bậc ĐANG ĐI không có nút", n_now == 0, str(n_now))
        first = pg.locator(".rk-cert").first
        check("nút nhìn thấy được thật (không bị display:none)", first.is_visible())
        href = first.get_attribute("href")
        check("nút trỏ certificate.html?rank=…", (href or "").startswith("certificate.html?rank="),
              str(href))

        print("\n=== [4] Tờ chứng nhận THẬT: tên lấy từ server ===")
        pg.goto(SITE + "/" + href, wait_until="load")
        pg.wait_for_timeout(5000)
        g = lambda s: (pg.locator(s).first.inner_text() or "").strip()
        check("tên trên tờ giấy = tên trong hồ sơ (không phải từ URL)",
              g("#c-name") == NAME, g("#c-name"))
        check("KHÔNG có dấu MẪU (đây là tờ thật)",
              pg.eval_on_selector("#c-sample", "e=>e.hidden"))
        check("nút Xuất PDF BẬT", not pg.eval_on_selector("#btn-print", "e=>e.disabled"))
        check("có tên bậc", g("#c-rank") not in ("", "—"), g("#c-rank"))
        check("có mã chứng nhận", g("#c-code").startswith("AQ-"), g("#c-code"))
        body = g("#c-body")
        check("thân bài nói 'hoàn thành chặng huấn luyện'",
              "hoàn thành" in body and "chặng" in body, body[:70])

        print("\n=== [5] KHÔNG in được chứng nhận của chặng CHƯA xong ===")
        # ⚠️ Đây là hàng rào chính của chế độ thật: sửa một chữ trên URL không được
        #    biến thành tờ giấy "Huyền Thoại".
        pg.goto(SITE + "/certificate.html?rank=legend", wait_until="load")
        pg.wait_for_timeout(5000)
        check("yêu cầu bậc 'legend' KHÔNG cho ra chứng nhận Huyền Thoại",
              "Huyền Thoại" not in g("#c-rank"), g("#c-rank"))
        check("và trang NÓI RA rằng chặng đó chưa hoàn thành",
              "chưa hoàn thành" in g("#cert-note").lower(), g("#cert-note")[:80])
        check("0 lỗi trang suốt cả luồng", not errs, str(errs[:2]))
        ctx.close()
        b.close()

finally:
    print("\n=== [6] Dọn dữ liệu test ===")
    n = 0
    if uid:
        for it in rows("USER#%s" % uid):
            aws("dynamodb", "delete-item", "--table-name", TABLE,
                "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
            n += 1
    for pk in ("EMAIL#%s" % email, "PENDING#%s" % email):
        for it in rows(pk):
            aws("dynamodb", "delete-item", "--table-name", TABLE,
                "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
            n += 1
    print("      đã xoá %d dòng, còn lại %d" % (n, len(rows("USER#%s" % uid)) if uid else 0))
    try:
        if tok:
            _fbtest.delete(tok)
            print("      đã xoá tài khoản Firebase tạm")
    except Exception as e:
        print("      ⚠️ chưa xoá được: %s" % str(e)[:60])

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
