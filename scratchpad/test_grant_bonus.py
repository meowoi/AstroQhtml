# -*- coding: utf-8 -*-
"""
test_grant_bonus.py — bộ kiểm cho `grant_starter_bonus.py`.

    python scratchpad/test_grant_bonus.py

⚠️⚠️ VÌ SAO PHẢI CÓ. `grant_starter_bonus.py` là script CẤP TIỀN chạy thẳng trên bảng
   thật, và nó sẽ được chạy đúng một lần cho mỗi người. Không có bộ kiểm thì lượt chạy
   đầu tiên trong đời script CHÍNH LÀ lượt chạy trên ví người dùng thật — sai thì không
   có nút hoàn lại. Bộ này gieo một tài khoản GIẢ (email `success@simulator.amazonses.com`
   theo luật của dự án, dù ở đây không gửi thư nào) rồi dọn sạch.

⚠️ Điều đáng đo nhất KHÔNG phải "cấp một lần có chạy không" mà là **cấp hai lần có
   thành hai lần tiền không**. Ca thứ nhất luôn xanh; ca thứ hai mới là ca chết người.

⚠️ Cũng đo hai cửa từ chối — chúng là phần dễ bị bỏ nhất:
   · email CHƯA có tài khoản: cấp bây giờ là cộng hai lần (họ vẫn nhận lúc kích hoạt),
     và dấu đóng ở đây còn CHẶN luôn phần quà đúng luật của họ sau này;
   · không có bản ghi ví: dừng, đừng đoán ra một cái ví.
"""
import sys
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import grant_starter_bonus as G

OK = FAIL = 0


def check(label, cond, detail=""):
    global OK, FAIL
    if cond:
        OK += 1
        print("  [OK]   " + label + (("  " + str(detail)) if detail else ""))
    else:
        FAIL += 1
        print("  [HONG] " + label + "  " + str(detail))


def quiet(*a, **k):
    """Nuốt phần in của `grant` — bộ kiểm tự nói, khỏi lẫn hai giọng."""
    pass


def seed(email, uid, meteors):
    G.tbl().put_item(Item={"PK": "EMAIL#" + email, "SK": "ACCOUNT",
                           "email": email, "uid": uid,
                           "note": "dong gieo boi test_grant_bonus.py"})
    G.tbl().put_item(Item={"PK": "USER#" + uid, "SK": "WALLET",
                           "meteors": meteors, "diamonds": 0})


def wipe(email, uid):
    n = 0
    for pk, sk in (("EMAIL#" + email, "ACCOUNT"),
                   ("USER#" + uid, "WALLET"),
                   ("BONUS#" + email, "STARTER")):
        if G.get(pk, sk) is not None:
            G.tbl().delete_item(Key={"PK": pk, "SK": sk})
            n += 1
    return n


def main():
    tag = uuid.uuid4().hex[:8]
    email = "success+grant-%s@simulator.amazonses.com" % tag
    uid = "aqtest" + tag
    print("")
    print("  BO KIEM `grant_starter_bonus.py` — bang " + G.TABLE)
    print("=" * 70)
    print("  tai khoan gieo: " + email)

    try:
        # ── [1] Email chưa có tài khoản: PHẢI từ chối, và không để lại dấu ──
        print("")
        print("=== [1] Email CHUA co tai khoan -> tu choi ===")
        r = G.grant(email, 100, "kiem thu", go=True, out=quiet)
        check("tu choi vi chua co tai khoan", r["skip"] == "chua-co-tai-khoan", r["skip"])
        check("khong cong tien", r["wrote"] is False)
        check("KHONG de lai dau BONUS# (neu de thi chan luon qua dung luat sau nay)",
              G.marker_of(email) is None)

        # ── [2] Có tài khoản nhưng KHÔNG có ví: dừng, đừng đoán ──
        print("")
        print("=== [2] Co tai khoan nhung KHONG co vi -> dung ===")
        G.tbl().put_item(Item={"PK": "EMAIL#" + email, "SK": "ACCOUNT",
                               "email": email, "uid": uid,
                               "note": "dong gieo boi test_grant_bonus.py"})
        r = G.grant(email, 100, "kiem thu", go=True, out=quiet)
        check("tu choi vi khong co ban ghi vi", r["skip"] == "khong-co-vi", r["skip"])
        check("khong de lai dau BONUS#", G.marker_of(email) is None)

        # ── [3] Cấp thật ──
        print("")
        print("=== [3] Cap that: 100 tt vao vi dang co 30 tt ===")
        G.tbl().put_item(Item={"PK": "USER#" + uid, "SK": "WALLET",
                               "meteors": 30, "diamonds": 0})
        r = G.grant(email, 100, "kiem thu lan mot", go=True, out=quiet)
        check("da ghi", r["wrote"] is True)
        check("gianh duoc dau", r["claimed"] is True)
        check("so du = 30 + 100", r["after"] == 130, r["after"])
        check("doc LAI bang: vi dung 130", G.wallet_of(uid) == 130, G.wallet_of(uid))
        mk = G.marker_of(email) or {}
        check("dau nam o BONUS#/STARTER", "bonusAt" in mk, sorted(mk.keys()))
        check("dau ghi dung so tien", G._num(mk.get("bonusAmount")) == 100,
              mk.get("bonusAmount"))
        check("dau ghi ro do NGUOI cap bu, khong phai server",
              mk.get("bonusBy") == "cap-bu-bang-tay", mk.get("bonusBy"))
        check("dau mang ly do (ban ghi tien phai tu giai thich duoc)",
              mk.get("bonusWhy") == "kiem thu lan mot", mk.get("bonusWhy"))
        check("dau KHONG co ttl (dau vinh vien, chong xoa-tk-roi-dang-ky-lai)",
              "ttl" not in mk, sorted(mk.keys()))

        # ── [4] Chạy LẠI: đây là ca chết người ──
        print("")
        print("=== [4] Chay LAI cung mot email -> KHONG duoc thanh hai lan tien ===")
        r2 = G.grant(email, 100, "kiem thu lan hai", go=True, out=quiet)
        check("khong ghi gi", r2["wrote"] is False)
        check("bao la DA cap roi", r2["claimed"] is False, r2["claimed"])
        check("VI KHONG TANG — van 130 tt", G.wallet_of(uid) == 130, G.wallet_of(uid))
        mk2 = G.marker_of(email) or {}
        check("dau KHONG bi ghi de (ly do lan mot con nguyen)",
              mk2.get("bonusWhy") == "kiem thu lan mot", mk2.get("bonusWhy"))

        # ── [5] `claim` trực tiếp lần hai cũng phải thua ──
        print("")
        print("=== [5] Goi thang `claim()` lan hai -> phai THUA dieu kien ghi ===")
        check("claim() lan hai tra False",
              G.claim(email, 100, "co tinh") is False)
        check("va vi VAN 130 tt", G.wallet_of(uid) == 130, G.wallet_of(uid))

        # ── [6] Chế độ THỬ không được ghi gì ──
        print("")
        print("=== [6] Che do THU (khong --go) KHONG duoc ghi gi ===")
        email2 = "success+grant2-%s@simulator.amazonses.com" % tag
        uid2 = "aqtest2" + tag
        seed(email2, uid2, 7)
        r3 = G.grant(email2, 500, "kiem thu che do thu", go=False, out=quiet)
        check("khong ghi gi", r3["wrote"] is False)
        check("vi VAN 7 tt", G.wallet_of(uid2) == 7, G.wallet_of(uid2))
        check("KHONG tao dau BONUS#", G.marker_of(email2) is None)
        # rồi cấp thật để chắc chế độ thử không làm hỏng lượt sau
        r4 = G.grant(email2, 500, "kiem thu sau che do thu", go=True, out=quiet)
        check("sau do cap that van duoc (che do thu khong dot chay luot cap)",
              r4["wrote"] is True and G.wallet_of(uid2) == 507, G.wallet_of(uid2))

        # ── [7] Số không dương ──
        print("")
        print("=== [7] So tt khong duong -> tu choi ===")
        email3 = "success+grant3-%s@simulator.amazonses.com" % tag
        uid3 = "aqtest3" + tag
        seed(email3, uid3, 5)
        r5 = G.grant(email3, 0, "kiem thu", go=True, out=quiet)
        check("tu choi 0 tt", r5["skip"] == "so-tt-khong-duong", r5["skip"])
        r6 = G.grant(email3, -100, "kiem thu", go=True, out=quiet)
        check("tu choi so am", r6["skip"] == "so-tt-khong-duong", r6["skip"])
        check("vi VAN 5 tt", G.wallet_of(uid3) == 5, G.wallet_of(uid3))
        check("KHONG tao dau BONUS#", G.marker_of(email3) is None)

        # ── [8] `verify` phải BẮT được sai lệch, không chỉ nói "khớp" ──
        print("")
        print("=== [8] `verify()` co that su BAT duoc sai lech khong ===")
        good = {"wrote": True, "uid": uid, "email": email,
                "before": 30, "amount": 100}
        check("verify() dat voi so dung", G.verify(good, out=quiet) is True)
        bad = dict(good, amount=999)
        check("verify() BAT duoc so sai (khong phai lam chung im lang)",
              G.verify(bad, out=quiet) is False)
    finally:
        print("")
        print("=== [9] Don du lieu gieo ===")
        n = 0
        for e, u in ((email, uid),
                     ("success+grant2-%s@simulator.amazonses.com" % tag, "aqtest2" + tag),
                     ("success+grant3-%s@simulator.amazonses.com" % tag, "aqtest3" + tag)):
            n += wipe(e, u)
        print("      da xoa %d dong" % n)
        left = [e for e in (email,
                            "success+grant2-%s@simulator.amazonses.com" % tag,
                            "success+grant3-%s@simulator.amazonses.com" % tag)
                if G.get("EMAIL#" + e, "ACCOUNT") is not None
                or G.marker_of(e) is not None]
        check("khong con dong test nao trong bang that", not left, str(left))

    print("")
    print("=== KET QUA: %d dat / %d hong ===" % (OK, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
