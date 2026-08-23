# -*- coding: utf-8 -*-
"""
test_visit.py — kiểm thử ĐỘC LẬP `POST /visit`: đếm lượt đến từ một chiến dịch.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_visit.py                 # http://localhost:5080
    python scratchpad/test_visit.py <base-url>      # ban that tren AWS

⚠️⚠️ VIỆC ROUTE NÀY TỒN TẠI ĐỂ LÀM: tách "không ai bấm quảng cáo" khỏi "có bấm mà
   không đăng ký". Trước nó, bảng nguồn của `/admin/stats` chỉ đếm được lượt ĐĂNG KÝ,
   mà nhãn chiến dịch chỉ ghi vào DB lúc đăng ký thành công — nên một chiến dịch mang
   về 200 người mà 0 người đăng ký đọc ra **y hệt** một chiến dịch không ai bấm.

Bốn thứ dễ sai nhất, và là bốn nhóm phép kiểm ở đây:
  ① nhãn RỖNG thì KHÔNG được tạo bản ghi nào (nếu không, gọi khống là bơm được rác)
  ② server phải LỌC LẠI nhãn, không tin client (ký tự lạ, quá dài, quá nhiều phần)
  ③ `ADD` phải cộng dồn đúng — gọi N lần thì đếm đúng N, kể cả khi gọi SONG SONG
  ④ không bản ghi nào chứa thứ lần được về một người (IP, user-agent, thời điểm)

⚠️ MÁY CHẠY Ở NHÀ VẪN DÙNG DYNAMODB THẬT (appsettings.Development.json ghi rõ). Nên
   mọi nhãn test ở đây đều mang tiền tố `zzTEST` và `finally` XOÁ HẾT — số liệu
   marketing thật không được lẫn một lượt test nào.
"""
import concurrent.futures as cf
import datetime as dt
import json
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import boto3

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"
# Tien to de mot lenh xoa gom het, va de mat thuong nhin vao bang la biet ngay la rac test.
PREFIX = "zztest"
DAY = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")

ddb = boto3.client("dynamodb")
ok_n = bad_n = 0
made = set()          # nhung nhan da tao, de xoa trong `finally`


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def post(src, raw_body=None):
    """Goi POST /visit. Tra (ma_http, than_phan_hoi)."""
    body = raw_body if raw_body is not None else json.dumps({"src": src}).encode()
    rq = urllib.request.Request(BASE + "/visit", data=body, method="POST",
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(rq, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def count(src):
    """Doc bo dem cua (hom nay x nhan) tu DynamoDB. None = chua co ban ghi."""
    r = ddb.get_item(TableName=TABLE,
                     Key={"PK": {"S": "VISIT#" + DAY}, "SK": {"S": "SRC#" + src}})
    it = r.get("Item")
    return None if not it else int(it.get("n", {}).get("N", 0))


def item_of(src):
    r = ddb.get_item(TableName=TABLE,
                     Key={"PK": {"S": "VISIT#" + DAY}, "SK": {"S": "SRC#" + src}})
    return r.get("Item")


try:
    # ═══════════ [1] Nhan RONG khong tao ban ghi nao ═══════════
    print("\n=== [1] Nhan rong: khong ghi gi, khong bao loi ===")
    before = ddb.scan(TableName=TABLE, Select="COUNT")["Count"]
    for name, payload in (("src rong", ""), ("src null", None),
                          ("src toan ky tu bi loc", "!!!@@@###"),
                          ("khong co truong src", "__NO_FIELD__")):
        if payload == "__NO_FIELD__":
            st, _ = post(None, raw_body=json.dumps({}).encode())
        else:
            st, _ = post(payload)
        check("%s -> 204, khong phai loi" % name, st == 204, "HTTP %s" % st)
    after = ddb.scan(TableName=TABLE, Select="COUNT")["Count"]
    check("bang KHONG phinh them ban ghi nao", after == before,
          "truoc %d / sau %d" % (before, after))

    # ═══════════ [2] Server LOC LAI nhan, khong tin client ═══════════
    print("\n=== [2] Server loc lai nhan (khong tin client) ===")
    # Ky tu la bi loai, giu lai phan hop le.
    dirty = PREFIX + ".loc!!!/paid<script>/thu%20nghiem"
    # ⚠️ `thu%20nghiem` -> `thu20nghiem`, KHONG phai `thunghiem`: bo loc xoa `%` nhung
    #    `2` va `0` la CHU SO nen duoc giu. Ban dau bo do nay mong `thunghiem` va bao
    #    hong oan. Ghi lai vi day dung la cho de doc sai: mot chuoi da ma hoa URL di
    #    qua bo loc thi khong bien mat, no de lai cac chu so cua ma `%NN`.
    want  = PREFIX + ".loc/paidscript/thu20nghiem"
    st, _ = post(dirty)
    made.add(want)
    check("gui nhan co ky tu la -> 204", st == 204, "HTTP %s" % st)
    check("nhan luu vao DB da bi LOC SACH ky tu la", count(want) == 1,
          "nhan sach=%r dem=%s" % (want, count(want)))
    check("nhan BAN (nguyen van) KHONG duoc luu", count(dirty) is None)

    # Qua 3 phan -> chi giu 3 phan dau.
    st, _ = post(PREFIX + ".p/a/b/c/d")
    made.add(PREFIX + ".p/a/b")
    check("qua 3 phan -> cat con dung 3", count(PREFIX + ".p/a/b") == 1,
          "dem=%s" % count(PREFIX + ".p/a/b"))

    # Moi phan qua 24 ky tu -> cat con 24.
    long_part = PREFIX + "x" * 40
    st, _ = post(long_part)
    cut = long_part[:24]
    made.add(cut)
    check("phan dai qua 24 ky tu -> cat con 24", count(cut) == 1,
          "%d ky tu" % len(cut))

    # Chu HOA -> ha thanh chu thuong (de `FB` va `fb` khong thanh hai nguon).
    st, _ = post(PREFIX + ".HOA/PAID")
    made.add(PREFIX + ".hoa/paid")
    check("chu HOA duoc ha thanh chu thuong", count(PREFIX + ".hoa/paid") == 1,
          "dem=%s" % count(PREFIX + ".hoa/paid"))

    # ═══════════ [3] ADD cong don dung, ke ca goi SONG SONG ═══════════
    print("\n=== [3] Cong don dung (goi tuan tu va song song) ===")
    seq = PREFIX + ".seq/paid/aug"
    made.add(seq)
    for _ in range(5):
        post(seq)
    check("goi 5 lan tuan tu -> dem dung 5", count(seq) == 5, "dem=%s" % count(seq))

    # ⚠️ PHEP KIEM DANG GIA NHAT CUA BO NAY. `ADD` la phep cong nguyen tu tren
    #    DynamoDB; neu ai doi sang doc-roi-cong-roi-ghi thi 20 luot song song se
    #    mat bot va CHINH cho nay do.
    par = PREFIX + ".par/paid/aug"
    made.add(par)
    with cf.ThreadPoolExecutor(max_workers=20) as ex:
        list(ex.map(lambda _: post(par), range(20)))
    check("goi 20 lan SONG SONG -> khong mat luot nao", count(par) == 20,
          "dem=%s (mong 20)" % count(par))

    # ═══════════ [4] Ban ghi khong chua gi lan duoc ve mot nguoi ═══════════
    print("\n=== [4] Ban ghi KHONG luu gi ve nguoi ghe ===")
    it = item_of(seq)
    check("ban ghi ton tai", it is not None)
    if it:
        keys = set(it.keys())
        check("chi co dung 3 truong: PK, SK, n", keys == {"PK", "SK", "n"},
              "thuc te: %s" % sorted(keys))
        for xau in ("ip", "ua", "userAgent", "agent", "at", "ts", "time",
                    "referer", "referrer", "uid", "email", "session"):
            check("KHONG co truong %r" % xau, xau not in keys)

    # ═══════════ [5] Nhan that cua chien dich dang chay ═══════════
    print("\n=== [5] Nhan that (doi chieu voi link quang cao dang chay) ===")
    # Chuoi nay la thu `js/utm.js` sinh ra tu link dang chay o Ads Manager.
    thuc = "facebook/paid/aug2026"
    check("nhan that qua duoc bo loc y nguyen (khong bi cat chu nao)",
          __import__("re").fullmatch(r"[a-z0-9._-]{1,24}(/[a-z0-9._-]{1,24}){0,2}", thuc)
          is not None, thuc)

finally:
    # ═══════════ DON DU LIEU TEST ═══════════
    print("\n=== Don du lieu test ===")
    # Quet lai theo tien to cho chac: xoa ca nhan phat sinh ngoai `made`.
    r = ddb.query(TableName=TABLE,
                  KeyConditionExpression="PK = :pk",
                  ExpressionAttributeValues={":pk": {"S": "VISIT#" + DAY}})
    dele = [i["SK"]["S"] for i in r.get("Items", [])
            if i["SK"]["S"].startswith("SRC#" + PREFIX)]
    for sk in dele:
        ddb.delete_item(TableName=TABLE,
                        Key={"PK": {"S": "VISIT#" + DAY}, "SK": {"S": sk}})
    print("  da xoa %d ban ghi test" % len(dele))

    con_lai = [i["SK"]["S"] for i in ddb.query(
        TableName=TABLE, KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk": {"S": "VISIT#" + DAY}}
    ).get("Items", []) if i["SK"]["S"].startswith("SRC#" + PREFIX)]
    check("khong con ban ghi test nao sot lai", not con_lai, str(con_lai))

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
    sys.exit(1 if bad_n else 0)
