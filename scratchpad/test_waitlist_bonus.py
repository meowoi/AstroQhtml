# -*- coding: utf-8 -*-
"""test_waitlist_bonus.py — QUÀ 500 tt: chỉ người trong danh sách chờ, và ĐÚNG MỘT LẦN.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_waitlist_bonus.py               # http://localhost:5080
    python scratchpad/test_waitlist_bonus.py --prod        # bản thật trên AWS

⚠️⚠️ VÌ SAO BỘ NÀY TỒN TẠI. Đo được 19/08/2026: con số "500 Purple Meteors" được hứa ở
   17 file (trang chủ VI+EN, thẻ OG/Twitter, JSON-LD, nút CTA, email kích hoạt, 22
   trang wiki) mà **không một dòng mã nào cấp nó** — ví tài khoản mới tạo với 0. Đó là
   một lời hứa hệ thống không giữ, và nó sống được 23 ngày vì **không có phép kiểm nào
   đối chiếu lời quảng cáo với hành vi của server**. Bộ này là phép kiểm đó.

⚠️ KHÔNG ĐO BẰNG LỜI KHAI CỦA API. Số dư đọc từ `GET /me/wallet`, và dấu đã-cấp đọc
   THẲNG từ DynamoDB — cùng lý do `test_auth_pending.py` đọc `pwdHash` từ bảng: một cờ
   trong JSON có thể đúng trong khi bản ghi thì không, mà bản ghi mới là tiền thật.

⚠️ DÙNG ĐỊA CHỈ GIẢ LẬP CỦA SES (`success@simulator.amazonses.com`) cho MỌI email có
   thể sinh ra thư: gửi vào địa chỉ không tồn tại là sinh bounce, và tỉ lệ bounce cao
   thì AWS khoá quyền gửi của CẢ TÀI KHOẢN (luật đã ghi trong CLAUDE.md).
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

PROD = "--prod" in sys.argv
BASE = ("https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com" if PROD
        else "http://localhost:5080")
TABLE = "astroq-main"
WL_BONUS = 500       # bản sao của Wallet.WaitlistBonus  — người đã ghi danh
ST_BONUS = 100       # bản sao của Wallet.StarterBonus   — mọi tài khoản khác
BONUS = WL_BONUS     # giữ tên cũ cho phần đã viết theo mức 500

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read().decode() or "{}"
            try:
                return r.status, json.loads(raw)
            except Exception:
                return r.status, {"_raw": raw[:200]}
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def aws(*a):
    return subprocess.run(["aws"] + list(a), capture_output=True, text=True)


def item(pk, sk):
    r = aws("dynamodb", "get-item", "--table-name", TABLE, "--consistent-read",
            "--key", json.dumps({"PK": {"S": pk}, "SK": {"S": sk}}), "--output", "json")
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return json.loads(r.stdout).get("Item")


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


def wipe(pk):
    n = 0
    for it in rows(pk):
        aws("dynamodb", "delete-item", "--table-name", TABLE,
            "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
        n += 1
    return n


def activate_link_of(email):
    """Lấy token kích hoạt từ bản ghi PENDING — thư đi tới hộp giả lập nên không đọc được."""
    it = item("PENDING#%s" % email, "SIGNUP")
    return it


emails = []
uids = []
bonus_keys = []   # BONUS#<email>/STARTER - dau vinh vien, phai don sau test
try:
    print("\n=== [0] Hằng số ở server và bản sao trong bộ đo phải khớp ===")
    import io
    import os
    import re
    wp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "..", "AstroqSV", "src", "AstroqSV.Api", "Services", "Wallet.cs")
    wsrc = io.open(wp, encoding="utf-8").read()
    m = re.search(r"WaitlistBonus\s*=\s*(\d+)", wsrc)
    m2 = re.search(r"StarterBonus\s*=\s*(\d+)", wsrc)
    check("Wallet.WaitlistBonus tồn tại", bool(m), str(m))
    check("Wallet.StarterBonus tồn tại", bool(m2), str(m2))
    if m:
        check("ban sao WL_BONUS khop hang so server", int(m.group(1)) == WL_BONUS,
              "server %s vs bo do %d" % (m.group(1), WL_BONUS))
    if m2:
        check("ban sao ST_BONUS khop hang so server", int(m2.group(1)) == ST_BONUS,
              "server %s vs bo do %d" % (m2.group(1), ST_BONUS))
    # ⚠️ CHỖ DUY NHẤT quyết mức phải là StarterBonusFor — hai đường gửi thư và
    #    đường cấp tiền đều gọi nó, không chọn hằng số tại chỗ.
    check("co ham StarterBonusFor(bool) quyet muc", "StarterBonusFor(bool onWaitlist)" in wsrc)
    check("qua khoi dau LON HON phi vao cua game dat nhat",
          ST_BONUS > 5, "%d vs 5" % ST_BONUS)

    st, h = call("GET", "/health")
    check("/health 200", st == 200, json.dumps(h)[:70])

    # ═════════ [1] NGƯỜI TỰ ĐĂNG KÝ, KHÔNG ghi danh → KHÔNG có quà ═════════
    # ⚠️ ĐỔI PHÁT BIỂU 20/08/2026 (đường B). Trước đó mục này khẳng định
    #    "tự đăng ký thì ví = 0" — nay MỌI tài khoản đều có quà, nên phát biểu
    #    cũ sẽ báo hỏng đúng lúc sản phẩm làm đúng. Điều cần bảo vệ KHÔNG đổi:
    #    người chưa ghi danh nhận MỨC THẤP, không nhận mức của người ghi danh.
    print("\n=== [1] Tu dang ky ma chua ghi danh -> co qua MUC THAP (%d tt) ===" % ST_BONUS)
    e1 = "success+nowl-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
    emails.append(e1)
    st, d = call("POST", "/auth/register",
                 {"email": e1, "password": "Astroq!2026", "name": "Khong Ghi Danh"})
    # ⚠️ 202, KHÔNG phải 200 — và 202 là ĐÚNG: tài khoản chưa được tạo, mới chỉ nhận
    #    việc và gửi thư. Lần chạy đầu tôi đòi 200 nên bộ đo báo hỏng oan.
    check("đăng ký nhận 202 (đã nhận, chờ kích hoạt)", st == 202,
          "%s %s" % (st, json.dumps(d)[:90]))
    pend = item("PENDING#%s" % e1, "SIGNUP")
    check("có bản ghi chờ kích hoạt", pend is not None)
    check("KHÔNG có bản ghi WAITLIST# cho email này",
          item("WAITLIST#%s" % e1, "SIGNUP") is None)

    # ═════════ [2] NGƯỜI ĐÃ GHI DANH → có quà ═════════
    print("\n=== [2] Ghi danh trước rồi mới tạo tài khoản -> CÓ quà ===")
    e2 = "success+wl-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
    emails.append(e2)
    st, d = call("POST", "/waitlist", {"email": e2, "lang": "vi"})
    check("ghi danh danh sách chờ nhận 202", st == 202, "%s %s" % (st, json.dumps(d)[:80]))
    wl = item("WAITLIST#%s" % e2, "SIGNUP")
    check("có bản ghi WAITLIST#", wl is not None)
    check("bản ghi chờ CHƯA có dấu đã-cấp (`bonusAt`)",
          wl is not None and "bonusAt" not in wl, str(list((wl or {}).keys())))

    # ═════════ [3] Ghi có điều kiện: gọi hai lần chỉ thắng một ═════════
    print("\n=== [3] Giành dấu quà: hai lượt song song chỉ MỘT lượt thắng ===")
    # ⚠️ Đo THẲNG hành vi của DynamoDB thay vì tin chú thích. Điều kiện nay chỉ còn
    #    `attribute_not_exists(bonusAt)` (bỏ `attribute_exists(PK)`) và dấu nằm ở bản
    #    ghi RIÊNG `BONUS#<email>/STARTER` — xem `ClaimStarterBonusAsync`.
    def claim(email, amount=None):
        r = aws("dynamodb", "update-item", "--table-name", TABLE,
                "--key", json.dumps({"PK": {"S": "BONUS#%s" % email},
                                     "SK": {"S": "STARTER"}}),
                "--condition-expression", "attribute_not_exists(bonusAt)",
                "--update-expression", "SET bonusAt = :t, bonusAmount = :a",
                "--expression-attribute-values",
                json.dumps({":t": {"S": "2026-08-20T00:00:00Z"},
                            ":a": {"N": str(amount if amount is not None else BONUS)}}))
        return r.returncode == 0

    e3 = "success+claim-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
    emails.append(e3)
    call("POST", "/waitlist", {"email": e3, "lang": "vi"})
    first = claim(e3)
    second = claim(e3)
    check("lượt đầu giành được dấu", first is True, str(first))
    check("lượt thứ hai KHÔNG giành được (chống cấp hai lần)", second is False, str(second))
    # ⚠️ ĐỔI PHÁT BIỂU: email chưa ghi danh NAY giành được dấu (ai cũng có quà),
    #    và bản ghi `BONUS#` vừa tạo CHÍNH LÀ dấu vĩnh viễn theo email. Nhưng phải
    #    canh nó KHÔNG tạo ra bản ghi `WAITLIST#` nào — làm thế là bức tường Phi Hành
    #    Đoàn (`GetCrewRawAsync` quét WAITLIST#/SIGNUP) đếm cả người chưa ghi danh.
    e4 = "success+ghost-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
    bonus_keys.append(e4)
    ghost = claim(e4, ST_BONUS)
    check("email CHUA ghi danh: VAN gianh duoc dau (ai cung co qua)", ghost is True, str(ghost))
    check("gianh lan hai thi khong duoc nua", claim(e4, ST_BONUS) is False)
    check("va KHONG sinh ra ban ghi WAITLIST# nao (khoi lam sai buc tuong Phi Hanh Doan)",
          item("WAITLIST#%s" % e4, "SIGNUP") is None)

    # ═════════ [4] Email kích hoạt chỉ hứa quà khi thật sự có quà ═════════
    print("\n=== [4] Nội dung thư nói đúng sự thật cho từng người ===")
    ep = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "..", "AstroqSV", "src", "AstroqSV.Api", "Services", "EmailService.cs")
    es = io.open(ep, encoding="utf-8").read()
    check("thư KHÔNG còn gõ cứng '500 Purple Meteors' trong phần kích hoạt",
          "500 Purple Meteors</b> khởi đầu" not in es)
    check("thư dựng câu quà từ tham số `bonusMeteors`",
          "bonusMeteors > 0" in es and "{bonusMeteors} Purple Meteors" in es)
    ap = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "..", "AstroqSV", "src", "AstroqSV.Api", "Endpoints", "AuthEndpoints.cs")
    asrc = io.open(ap, encoding="utf-8").read()
    check("ca BA cho deu di qua StarterBonusFor (khong chon hang so tai cho)",
          asrc.count("Wallet.StarterBonusFor(") >= 3,
          "%d cho" % asrc.count("Wallet.StarterBonusFor("))
    check("cho gui thu CHI DOC ban ghi cho, khong gianh dau",
          "GetWaitlistAsync(email)" in asrc)
    check("gianh dau nam o duong kich hoat",
          "ClaimStarterBonusAsync(email, amount)" in asrc)
    check("khong con goi ClaimWaitlistBonusAsync (ma chet)",
          "ClaimWaitlistBonusAsync" not in asrc)

    # ═════════ [5] Quà hỏng không được làm kích hoạt hỏng ═════════
    print("\n=== [5] Quà nằm trong try riêng (mất quà còn hơn chặn tài khoản) ===")
    i_create = asrc.index("await db.CreateUserAsync(uid, email, p.Name, p.Src);")
    i_claim = asrc.index("ClaimStarterBonusAsync")
    i_ok = asrc.index('activated=1&reason=ok')
    check("cấp quà đặt SAU khi tài khoản đã tạo xong", i_create < i_claim)
    check("và TRƯỚC khi chuyển hướng báo thành công", i_claim < i_ok)
    seg = asrc[i_claim - 400:i_ok]
    check("khối quà có `catch` riêng", "catch (Exception bex)" in seg or "catch (Exception cex)" in seg)
    check("cộng tiền hỏng thì log ở mức ERROR kèm chỉ dẫn cấp bù",
          "CẤP BÙ BẰNG TAY" in asrc)

    # ═════════ [7] KÍCH HOẠT THẬT, RỒI ĐỌC VÍ ═════════
    print("\n=== [7] Kích hoạt THẬT qua /auth/activate rồi đọc ví ===")
    # ⚠️⚠️ ĐÂY LÀ PHÉP KIỂM QUYẾT ĐỊNH CỦA CẢ BỘ. Mọi mục trên chỉ chứng minh từng
    #    mảnh: hằng số có, ghi có điều kiện chặn đúng, thư nói đúng. Không mục nào
    #    chứng minh **tiền thật sự vào ví** — mà đó chính là lời hứa đang nợ.
    #
    # ⚠️ Cách lấy link kích hoạt: thư đi tới hộp giả lập SES nên không đọc lại được, và
    #    bản ghi chờ chỉ lưu `tokenHash`. Nên thay `tokenHash` bằng băm của MỘT token do
    #    tôi tự sinh — `HashToken` là `base64(SHA256(utf8(token)))`, dựng lại được y
    #    nguyên. Vẫn đi qua **đúng endpoint thật**, không giả lập bước nào.
    import base64
    import hashlib

    def hash_token(tok):
        return base64.b64encode(hashlib.sha256(tok.encode("utf-8")).digest()).decode()

    def put_token(email, tok):
        """Đổi tokenHash của bản ghi chờ sang băm của `tok`; giữ nguyên mọi thứ khác."""
        it = item("PENDING#%s" % email, "SIGNUP")
        if it is None:
            return False
        it["tokenHash"] = {"S": hash_token(tok)}
        r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(it))
        return r.returncode == 0

    def wallet_of(uid):
        it = item("USER#%s" % uid, "WALLET")
        if it is None:
            return None
        return int(it.get("meteors", {}).get("N", "0"))

    def uid_of(email):
        # SK la "ACCOUNT" (DynamoContext.LinkEmailAsync) — do doc code, khong doan.
        it = item("EMAIL#%s" % email, "ACCOUNT")
        return None if it is None else it.get("uid", {}).get("S")

    import urllib.parse

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        """Chặn việc tự đi theo redirect."""
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    def activate(email, tok):
        """Gọi /auth/activate và trả (status, dich-chuyen-huong-toi).

        ⚠️ KHÔNG ĐI THEO REDIRECT. Endpoint này kết thúc bằng 302 về trang landing
           (`continueUrl`), mà ở máy đó là một địa chỉ KHÔNG chạy — lần chạy đầu
           urllib tự đi theo rồi nổ `ConnectionRefusedError`, làm bộ đo chết giữa
           đường **sau khi đã tạo tài khoản thật**, nên phần dọn chưa biết uid và để
           sót 2 dòng + 1 tài khoản Firebase (đã dọn tay). Thứ cần đo là *server làm
           gì*, không phải *trang đích có mở được không*.
        """
        opener = urllib.request.build_opener(NoRedirect)
        req = urllib.request.Request(
            BASE + "/auth/activate?e=%s&t=%s" % (urllib.parse.quote(email), tok))
        try:
            with opener.open(req, timeout=45) as r:
                return r.status, r.headers.get("Location", "")
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Location", "")

    # ── (a) Người ĐÃ ghi danh: kích hoạt xong ví phải có đúng 500 ──
    ew = "success+e2ewl-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
    emails.append(ew)
    call("POST", "/waitlist", {"email": ew, "lang": "vi"})
    call("POST", "/auth/register", {"email": ew, "password": "Astroq!2026", "name": "Co Ghi Danh"})
    tok = uuid.uuid4().hex + uuid.uuid4().hex
    check("[a] đặt được token kích hoạt của mình vào bản ghi chờ", put_token(ew, tok))
    st, loc = activate(ew, tok)
    check("[a] /auth/activate chuyển hướng", st in (301, 302, 303), "%s -> %s" % (st, loc[:70]))
    check("[a] đích chuyển hướng báo kích hoạt THÀNH CÔNG",
          "activated=1" in loc and "reason=ok" in loc, loc[:90])
    uw = uid_of(ew)
    uids.append((uw, ew))
    check("[a] tài khoản đã được tạo (tra được uid từ EMAIL#)", bool(uw), str(uw))
    if uw:
        bal = wallet_of(uw)
        check("[a] VÍ CÓ ĐÚNG %d tt — lời hứa đã được giữ" % BONUS, bal == BONUS,
              "số dư %s" % bal)
        wl2 = item("WAITLIST#%s" % ew, "SIGNUP")
        # ⚠️ ĐỔI CHỖ ĐO: dấu nay ở bản ghi RIÊNG, không đóng lên bản ghi waitlist.
        bk2 = item("BONUS#%s" % ew, "STARTER")
        check("[a] dau da-cap nam o BONUS#/STARTER",
              bk2 is not None and "bonusAt" in bk2, str(list((bk2 or {}).keys())))
        check("[a] ban ghi WAITLIST# KHONG bi dong dau (giu nguyen nghia)",
              wl2 is not None and "bonusAt" not in wl2, str(list((wl2 or {}).keys())))
        check("[a] dấu ghi đúng số tiền đã cấp",
              bk2 is not None and bk2.get("bonusAmount", {}).get("N") == str(BONUS),
              str((bk2 or {}).get("bonusAmount")))

        # ── (b) Bấm lại link lần hai: KHÔNG được cộng thêm ──
        st2, loc2 = activate(ew, tok)
        bal2 = wallet_of(uw)
        check("[b] bấm lại link kích hoạt: ví KHÔNG tăng thêm", bal2 == BONUS,
              "%s -> %s" % (bal, bal2))
        check("[b] và trang đích nói là 'đã kích hoạt rồi', không kêu lỗi",
              "activated=1" in loc2, "%s -> %s" % (st2, loc2[:80]))

    # ── (c) Người KHÔNG ghi danh: ví phải là 0 ──
    en = "success+e2enowl-%s@simulator.amazonses.com" % uuid.uuid4().hex[:8]
    emails.append(en)
    call("POST", "/auth/register", {"email": en, "password": "Astroq!2026", "name": "Khong Ghi Danh"})
    tok2 = uuid.uuid4().hex + uuid.uuid4().hex
    check("[c] đặt được token cho tài khoản không ghi danh", put_token(en, tok2))
    activate(en, tok2)   # bo qua ket qua, do bang vi ben duoi
    un = uid_of(en)
    uids.append((un, en))
    check("[c] tài khoản đã được tạo", bool(un), str(un))
    if un:
        baln = wallet_of(un)
        check("[c] vi = %d (khong ghi danh thi nhan muc thap)" % ST_BONUS,
              baln == ST_BONUS, "so du %s" % baln)
        check("[c] muc thap NHO HON muc cua nguoi ghi danh", ST_BONUS < WL_BONUS)
        bk = item("BONUS#%s" % en, "STARTER")
        check("[c] dau da-cap nam o BONUS#/STARTER voi dung so tien",
              bk is not None and bk.get("bonusAmount", {}).get("N") == str(ST_BONUS),
              str(bk))
        check("[c] KHÔNG sinh ra bản ghi WAITLIST# nào cho email đó",
              item("WAITLIST#%s" % en, "SIGNUP") is None)

finally:
    print("\n=== [6] Dọn dữ liệu test ===")
    n = 0
    for e in emails:
        for pk in ("WAITLIST#%s" % e, "PENDING#%s" % e, "EMAIL#%s" % e,
                   "BONUS#%s" % e):
            n += wipe(pk)
    # ⚠️ Mục [7] tạo TÀI KHOẢN THẬT (Firebase + mọi dòng USER#), nên phải dọn cả hai.
    #    Bỏ sót thì lần sau email đó đã "bị giữ chỗ" và bộ đo hỏng một cách khó hiểu.
    for e in bonus_keys:
        n += wipe("BONUS#%s" % e)
    for uid, em in uids:
        if uid:
            n += wipe("USER#%s" % uid)
    try:
        sys.path.insert(0, "scratchpad")
        import _fbtest
        for _uid, em in uids:
            try:
                tk = _fbtest.signin(em, "Astroq!2026")
                _fbtest.delete(tk)
                print("      đã xoá tài khoản Firebase %s" % em)
            except Exception as e:
                print("      ⚠️ chưa xoá được tài khoản Firebase %s: %s" % (em, str(e)[:60]))
    except Exception as e:
        print("      ⚠️ không nạp được _fbtest: %s" % str(e)[:60])
    left = sum(len(rows("WAITLIST#%s" % e)) + len(rows("PENDING#%s" % e)) +
               len(rows("EMAIL#%s" % e)) for e in emails)
    print("      đã xoá %d dòng, còn lại %d" % (n, left))
    if left:
        print("      ⚠️ CÒN SÓT %d dòng — kiểm lại bằng tay" % left)

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
