# -*- coding: utf-8 -*-
"""
grant_starter_bonus.py — CẤP BÙ quà khởi đầu bằng tay cho một email ĐÃ kích hoạt.

    python scratchpad/grant_starter_bonus.py <email> <so_tt> --why "ly do"        # THỬ
    python scratchpad/grant_starter_bonus.py <email> <so_tt> --why "ly do" --go   # GHI THẬT

⚠️⚠️ VÌ SAO CÓ FILE NÀY. Đường cấp quà nằm ở `/auth/activate` và chỉ chạy MỘT lần cho
   mỗi email (`ClaimStarterBonusAsync` ghi có điều kiện). Ai đã kích hoạt xong TRƯỚC khi
   luật quà hiện hành được deploy thì **không bao giờ đi qua đường đó lần nữa** — đúng
   thiết kế, nhưng nghĩa là phần bù phải cấp bằng tay. Chính `AuthEndpoints.cs` đã tính
   tới việc này: khi cộng tiền hỏng sau khi đã giành dấu, nó log "CẤP BÙ BẰNG TAY". Đây
   là công cụ để làm đúng việc đó, thay cho một lệnh `aws dynamodb update-item` gõ tay.

⚠️ GIỮ NGUYÊN NGỮ NGHĨA CỦA SERVER, KHÔNG PHÁT MINH CƠ CHẾ THỨ HAI:
   · Dấu vẫn là `BONUS#<email>` / `STARTER`, vẫn ghi `bonusAt`, `bonusAmount`, `email`.
   · Vẫn `ConditionExpression = attribute_not_exists(bonusAt)`. Nhờ vậy công cụ này và
     server **không thể cùng cấp**: ai ghi trước thì bên sau thua điều kiện. Chạy lại
     script hai lần cũng vậy — lần hai không cộng gì. Một script cấp tiền mà chạy hai
     lần thành hai lần tiền là loại lỗi không sửa được bằng cách chạy tiếp.
   · Vẫn GIÀNH DẤU TRƯỚC, CỘNG TIỀN SAU. Ngược lại thì một lỗi giữa hai bước sinh ra
     khả năng cộng hai lần, mà nhân đôi tiền nặng hơn hẳn mất quà.
   · KHÔNG cộng vào `meteorsEarned` và KHÔNG đi qua `Award()` — quà một lần không phải
     tiền kiếm được từ một lượt chơi, để huy hiệu `collector-*` vẫn đo đúng nỗ lực học
     (lý do đã ghi ở `Wallet.WaitlistBonus`).
   · KHÔNG ghi dòng `HIST#`: đường cấp quà của server cũng không ghi. Thêm ở đây là làm
     nhật ký của hai đường lệch nhau.

⚠️ MẶC ĐỊNH LÀ THỬ, PHẢI CÓ `--go` MỚI GHI. Đây là tiền của người dùng thật; gõ nhầm
   email hay nhầm số thì không có nút hoàn lại.

⚠️ DÙNG boto3 CHỨ KHÔNG DÙNG `aws` CLI — cố ý. `aws` CLI trên máy này in ra cp1252 và
   ĐÃ chết thật với một cái tên tiếng Việt (ghi ở đầu `test_waitlist_bonus.py`: lỗi
   charmap ở ký tự â có dấu); khi đó tiến trình con trả rỗng và script gọi nó **báo
   thành công trong khi không làm gì**. Với script cấp tiền thì im lặng-mà-sai là hỏng
   nặng nhất, nên bỏ hẳn tầng văn bản đó.

Bộ kiểm: `scratchpad/test_grant_bonus.py` (gieo một tài khoản giả trong bảng thật rồi
dọn sạch — không đụng tài khoản người dùng, không sinh email nào).
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import datetime as dt
import decimal
import json

import boto3
from botocore.exceptions import ClientError

TABLE = "astroq-main"
REGION = "ap-southeast-1"


def now_iso():
    """Mốc thời gian ĐÚNG DẠNG SERVER ĐANG GHI — `DateTime.UtcNow.ToString("o")`
    của .NET: 7 chữ số phần giây và kết thúc bằng `Z`.

    ⚠️ `datetime.isoformat()` cho `...+00:00` và 6 chữ số — cùng một thời điểm,
       nhưng KHÁC HÌNH. Hiện không dòng mã nào phân tích cột này (đo 20/08/2026:
       `updatedAt` của ví không ai đọc, của PROGRESS thì đọc ra chuỗi thô), nên
       hai dạng lẫn nhau chưa hỏng gì HÔM NAY. Nó hỏng vào ngày ai đó viết bộ
       đọc và thử nó trên vài dòng đầu — cùng khuôn bẫy `casefold` và CRLF đã
       trả giá nhiều lần: một cột chỉ nên có MỘT hình.
    """
    t = dt.datetime.now(dt.timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + ("%06d0Z" % t.microsecond)


_dyn = None


def tbl():
    global _dyn
    if _dyn is None:
        _dyn = boto3.resource("dynamodb", region_name=REGION).Table(TABLE)
    return _dyn


def _num(v):
    """Số của DynamoDB về int — boto3 trả `Decimal`, so sánh trực tiếp là bẫy."""
    if v is None:
        return None
    if isinstance(v, decimal.Decimal):
        return int(v)
    return int(v)


def get(pk, sk):
    """Đọc NHẤT QUÁN. Đọc thường có thể trả bản cũ, mà ở đây bản cũ nghĩa là
    "chưa cấp" cho một người vừa được cấp — tức cộng hai lần."""
    r = tbl().get_item(Key={"PK": pk, "SK": sk}, ConsistentRead=True)
    return r.get("Item")


def uid_of(email):
    it = get("EMAIL#" + email, "ACCOUNT")
    return (it or {}).get("uid")


def wallet_of(uid):
    it = get("USER#" + uid, "WALLET")
    if it is None:
        return None
    return _num(it.get("meteors", 0))


def marker_of(email):
    return get("BONUS#" + email, "STARTER")


def claim(email, amount, why, actor="cap-bu-bang-tay"):
    """Giành dấu đã-cấp. `True` = lời gọi NÀY thắng và phải cộng tiền tiếp.

    `False` = đã có ai cấp rồi (server, hoặc một lượt chạy trước) ⇒ KHÔNG cộng gì.
    """
    try:
        tbl().update_item(
            Key={"PK": "BONUS#" + email, "SK": "STARTER"},
            ConditionExpression="attribute_not_exists(bonusAt)",
            UpdateExpression=("SET bonusAt = :t, bonusAmount = :a, email = :e, "
                              "bonusBy = :by, bonusWhy = :why"),
            ExpressionAttributeValues={
                ":t": now_iso(),
                ":a": amount,
                ":e": email,
                # Hai trường DƯỚI ĐÂY server không ghi — cố ý thêm, để về sau còn
                # phân biệt dòng nào do máy cấp và dòng nào do người cấp bù, kèm lý
                # do. Một bản ghi TIỀN mà không tự giải thích được thì nửa năm sau
                # không ai dám sửa nó.
                ":by": actor,
                ":why": why,
            })
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


def credit(uid, amount):
    """Cộng ví. Cùng biểu thức với `DynamoContext.CreditWalletAsync`."""
    r = tbl().update_item(
        Key={"PK": "USER#" + uid, "SK": "WALLET"},
        UpdateExpression="ADD meteors :n SET updatedAt = :t",
        ExpressionAttributeValues={
            ":n": amount,
            ":t": now_iso(),
        },
        ReturnValues="ALL_NEW")
    return _num(r["Attributes"].get("meteors", 0))


def grant(email, amount, why, go=False, out=print):
    """Cấp bù cho một email. Trả dict kể lại đã làm gì — người gọi tự khẳng định.

    `go=False` (mặc định) chỉ đọc và in dự kiến, KHÔNG ghi gì.
    """
    res = {"email": email, "amount": amount, "wrote": False, "claimed": None,
           "before": None, "after": None, "uid": None, "skip": None}

    if amount <= 0:
        res["skip"] = "so-tt-khong-duong"
        out("  ✗ số tt phải > 0 — không làm gì")
        return res

    uid = uid_of(email)
    if not uid:
        # ⚠️ KHÔNG cấp cho email chưa có tài khoản. Họ VẪN sẽ đi qua đường cấp quà
        #    lúc kích hoạt, nên cấp bù bây giờ là cộng hai lần — và tệ hơn: cái dấu
        #    ta đóng ở đây CHẶN luôn phần quà đúng luật của họ sau này.
        res["skip"] = "chua-co-tai-khoan"
        out("  ✗ %s CHƯA có tài khoản (không có EMAIL#…/ACCOUNT)." % email)
        out("    Bỏ qua: họ vẫn nhận quà tự động khi kích hoạt. Cấp bù ở đây là cộng hai lần.")
        return res
    res["uid"] = uid

    before = wallet_of(uid)
    if before is None:
        res["skip"] = "khong-co-vi"
        out("  ✗ không có bản ghi ví (USER#%s / WALLET) — dừng, không đoán." % uid)
        return res
    res["before"] = before

    mk = marker_of(email)
    if mk is not None and "bonusAt" in mk:
        res["claimed"] = False
        res["after"] = before
        out("  = %s ĐÃ nhận %s tt lúc %s (%s) — không cộng gì."
            % (email, _num(mk.get("bonusAmount")), mk.get("bonusAt"),
               mk.get("bonusBy", "server")))
        return res

    out("  → %s  uid %s" % (email, uid))
    out("    ví hiện tại %d tt  →  dự kiến %d tt  (+%d)"
        % (before, before + amount, amount))
    out("    lý do: " + why)
    if not go:
        out("    (THỬ — chưa ghi gì. Thêm `--go` để cấp thật.)")
        return res

    if not claim(email, amount, why):
        # Có lượt cấp khác xen vào giữa lệnh đọc và lệnh ghi. Đúng việc mà điều kiện
        # ghi sinh ra để chặn, và nó vừa chặn.
        res["claimed"] = False
        res["after"] = wallet_of(uid)
        out("    ! lượt cấp khác vừa thắng — KHÔNG cộng tiền (điều kiện ghi đang làm việc)")
        return res
    res["claimed"] = True

    try:
        res["after"] = credit(uid, amount)
        res["wrote"] = True
        out("    ✓ đã cấp %d tt — số dư %d tt" % (amount, res["after"]))
    except Exception as ex:
        # ⚠️ Đã giành dấu mà cộng hỏng: nói TO, kèm đủ số để sửa tay. Im lặng ở đây
        #    là một người mất quà VĨNH VIỄN vì dấu đã đóng.
        out("    ✗✗ ĐÃ GIÀNH DẤU NHƯNG CỘNG %d tt HỎNG cho %s (uid %s): %s"
            % (amount, email, uid, ex))
        out("       Sửa tay: cộng %d tt vào USER#%s / WALLET, hoặc xoá dấu "
            "BONUS#%s / STARTER rồi chạy lại." % (amount, uid, email))
        raise
    return res


def verify(res, out=print):
    """Đọc LẠI bảng và khẳng định. Không tin giá trị trả về của chính lệnh ghi."""
    if not res.get("wrote"):
        return True
    ok = True
    bal = wallet_of(res["uid"])
    if bal != res["before"] + res["amount"]:
        ok = False
        out("    ✗ đọc lại ví: %s, đáng lẽ %d" % (bal, res["before"] + res["amount"]))
    mk = marker_of(res["email"]) or {}
    if _num(mk.get("bonusAmount")) != res["amount"]:
        ok = False
        out("    ✗ dấu ghi %s tt, đáng lẽ %d" % (mk.get("bonusAmount"), res["amount"]))
    if ok:
        out("    ✓ đọc lại bảng: ví %d tt, dấu %d tt — khớp" % (bal, res["amount"]))
    return ok


def main(argv):
    go = "--go" in argv
    why = ""
    rest = list(argv[1:])
    if "--why" in rest:
        i = rest.index("--why")
        if i + 1 < len(rest):
            why = rest[i + 1]
            del rest[i:i + 2]
    args = [a for a in rest if not a.startswith("--")]
    if len(args) != 2 or not why:
        print(__doc__)
        print('  ✗ cần: <email> <so_tt> --why "ly do"  [--go]')
        return 2
    email, amount = args[0], int(args[1])
    print("")
    print("  CẤP BÙ QUÀ KHỞI ĐẦU — bảng %s%s" % (TABLE, "" if go else "   (THỬ)"))
    print("=" * 70)
    res = grant(email, amount, why, go=go)
    if not verify(res):
        return 1
    print("")
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
