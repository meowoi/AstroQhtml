# -*- coding: utf-8 -*-
"""
test_shop.py — kiểm thử ĐỘC LẬP /me/shop, /me/shop/buy, /me/shop/equip.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_shop.py                 # http://localhost:5080
    python scratchpad/test_shop.py <base-url>       # bản thật trên AWS

Trọng tâm: **CLIENT KHÔNG BAO GIỜ QUYẾT GIÁ.** Có kịch bản client gửi kèm
`price`/`amount`/`free`, mua món chưa đủ tiền, mua hai lần, đeo món chưa mua,
gửi lại cùng `opId`, và bắn 5 lời gọi mua SONG SONG cho cùng một món.

⚠️ Tự tạo tài khoản Firebase tạm (token ĐÃ xác minh email) và tự dọn mọi bản ghi
   DynamoDB trong `finally` — kể cả khi hỏng giữa chừng.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

import _fbtest

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
TABLE = "astroq-main"

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode() or "{}"
            return r.status, json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode() or "{}"
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw}
    except Exception as e:                       # noqa: BLE001
        return 0, {"_err": str(e)}


def aws(*args):
    return subprocess.run(["aws", *args], capture_output=True, text=True, encoding="utf-8")


def put_item(item):
    aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(item))


def rows(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :p",
            "--expression-attribute-values", json.dumps({":p": {"S": f"USER#{uid}"}}))
    try:
        return json.loads(r.stdout).get("Items", [])
    except Exception:                            # noqa: BLE001
        return []


def wipe(uid):
    n = 0
    for it in rows(uid):
        aws("dynamodb", "delete-item", "--table-name", TABLE,
            "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
        n += 1
    return n


def main():
    print(f"=== /me/shop @ {BASE} ===\n")
    email = f"shop-{uuid.uuid4().hex[:8]}@simulator.amazonses.com"
    acc = _fbtest.make_verified(email)
    uid, token = acc[0], acc[1]

    try:
        # Hồ sơ + ví: 200 tt để mua được món đắt nhất (150) mà vẫn còn tiền.
        put_item({"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
                  "name": {"S": "Nhi"}, "email": {"S": email},
                  "character": {"S": "m"}, "avatar": {"S": "ava/avam.png"},
                  "createdAt": {"S": "2026-08-01T00:00:00Z"}})
        put_item({"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
                  "meteors": {"N": "200"}})

        print("[1] Khong token thi khong vao duoc")
        for m, p in [("GET", "/me/shop"), ("POST", "/me/shop/buy"), ("PUT", "/me/shop/equip")]:
            st, _ = call(m, p, body={} if m != "GET" else None)
            check(f"{m} {p} khong token → 401", st == 401, f"{st}")
        st, _ = call("GET", "/me/shop", token="rac.rac.rac")
        check("token rac → 401", st == 401, f"{st}")

        print("\n[2] GET /me/shop — SERVER tra gia")
        st, d = call("GET", "/me/shop", token=token)
        check("200", st == 200, f"{st}")
        items = d.get("items") or []
        check("tra bang mon kem GIA", len(items) >= 4 and all("price" in i for i in items),
              f"{len(items)} mon")
        # ⚠️ DANH SACH LOAI DO TRANG TRI GHI TAY, KHONG suy tu `d["kinds"]`.
        #    Suy tu server thi bat ky loai moi nao cung tu dong "dat", ke ca mot loai
        #    ban loi the (`boost`) — tuc phep kiem mat rang. Them loai mon moi thi
        #    phai sua dong nay bang tay, dung dieu cam so 1 cua Services/Cosmetics.cs.
        #    (Ban dau dong nay ghim ("theme","frame") nen no bao hong ngay khi them
        #    loai `decal` — phep kiem bao ve trang thai cu, loi da lap nhieu lan.)
        DECOR_KINDS = ("theme", "frame", "decal")
        check("moi mon la do TRANG TRI (%s)" % "/".join(DECOR_KINDS),
              all(i.get("kind") in DECOR_KINDS for i in items)
              and set(d.get("kinds") or []) <= set(DECOR_KINDS),
              f"kinds={d.get('kinds')}")
        # Moi loai phai co it nhat mot mon — mot loai rong thi cua hang ve khoi trong.
        _by_kind = {}
        for i in items:
            _by_kind.setdefault(i.get("kind"), []).append(i)
        check("khong loai nao rong",
              all(_by_kind.get(k) for k in (d.get("kinds") or [])),
              str({k: len(v) for k, v in _by_kind.items()}))
        # Moi loai phai co DUNG MOT mon gia 0 — thieu la khong co duong ve, nhieu hon
        # mot thi "mac dinh" khong con nghia gi.
        for k, v in sorted(_by_kind.items()):
            _free = [i["id"] for i in v if i.get("price") == 0]
            check(f"loai '{k}' co dung 1 mon gia 0", len(_free) == 1, str(_free))
        check("kho do rong luc dau", (d.get("owned") or []) == [], str(d.get("owned")))
        check("tra kem mon mac dinh", bool(d.get("defaults")), str(d.get("defaults")))
        check("tra kem so du vi", (d.get("wallet") or {}).get("meteors") == 200,
              str(d.get("wallet")))
        check("ten tau rong luc dau", (d.get("ship") or "") == "")

        paid = [i for i in items if i["price"] > 0]
        free = [i for i in items if i["price"] == 0]
        cheap = min(paid, key=lambda i: i["price"])
        pricey = max(paid, key=lambda i: i["price"])

        print("\n[3] Mua mot mon — client KHONG quyet gia")
        # ⚠️ Gui kem gia/so tien: server phai BO QUA hoan toan.
        st, d = call("POST", "/me/shop/buy", token=token,
                     body={"itemId": cheap["id"], "opId": "op-a",
                           "price": 1, "amount": 1, "free": True, "meteors": 0})
        check("mua duoc → 200", st == 200, f"{st}")
        check("tru DUNG gia cua server, khong phai so client gui",
              d.get("meteors") == 200 - cheap["price"],
              f"{d.get('meteors')} (gia {cheap['price']})")
        check("mon vao kho do", cheap["id"] in (d.get("owned") or []), str(d.get("owned")))
        check("mua roi DEO LUON", (d.get("equipped") or {}).get(cheap["kind"]) == cheap["id"],
              str(d.get("equipped")))

        print("\n[4] Gui lai cung opId thi KHONG tru hai lan")
        bal_before = d.get("meteors")
        st, d2 = call("POST", "/me/shop/buy", token=token,
                      body={"itemId": cheap["id"], "opId": "op-a"})
        check("gui lai → 200 va bought=false", st == 200 and d2.get("bought") is False,
              f"{st} {d2.get('bought')}")
        check("so du KHONG doi", d2.get("meteors") == bal_before,
              f"{bal_before} → {d2.get('meteors')}")

        print("\n[5] Mua lai mon DA CO (opId khac) → 409, khong tru tien")
        st, d3 = call("POST", "/me/shop/buy", token=token,
                      body={"itemId": cheap["id"], "opId": "op-b"})
        check("→ 409 owned", st == 409 and d3.get("code") == "owned", f"{st} {d3.get('code')}")
        st, d4 = call("GET", "/me/shop", token=token)
        check("so du van nguyen", (d4.get("wallet") or {}).get("meteors") == bal_before,
              str((d4.get('wallet') or {}).get('meteors')))

        print("\n[6] Mon gia 0 KHONG ban")
        st, d5 = call("POST", "/me/shop/buy", token=token,
                      body={"itemId": free[0]["id"], "opId": "op-c"})
        check("→ 400 free-item", st == 400 and d5.get("code") == "free-item",
              f"{st} {d5.get('code')}")

        print("\n[7] id mon la → 400, khong tru gi")
        for bad in ["khong-co-mon-nay", "", "  ", "cockpit-cyan; drop", "../../etc"]:
            st, dd = call("POST", "/me/shop/buy", token=token, body={"itemId": bad, "opId": "x"})
            check(f"'{bad}' → 400", st == 400 and dd.get("code") == "bad-item",
                  f"{st} {dd.get('code')}")

        print("\n[8] Deo mon CHUA MUA → 409 (server khong tin client)")
        not_mine = next(i for i in paid if i["id"] != cheap["id"])
        st, d6 = call("PUT", "/me/shop/equip", token=token, body={"itemId": not_mine["id"]})
        check("→ 409 not-owned", st == 409 and d6.get("code") == "not-owned",
              f"{st} {d6.get('code')}")
        st, d7 = call("GET", "/me/shop", token=token)
        check("mon dang deo KHONG doi",
              (d7.get("equipped") or {}).get(cheap["kind"]) == cheap["id"],
              str(d7.get("equipped")))

        print("\n[9] Deo lai mon MAC DINH (gia 0) — luon duoc")
        same_kind_default = d7["defaults"][cheap["kind"]]
        st, d8 = call("PUT", "/me/shop/equip", token=token, body={"itemId": same_kind_default})
        check("deo mon mac dinh → 200", st == 200, f"{st}")
        check("co duong VE tong goc",
              (d8.get("equipped") or {}).get(cheap["kind"]) == same_kind_default,
              str(d8.get("equipped")))
        # rồi đeo lại món đã mua
        call("PUT", "/me/shop/equip", token=token, body={"itemId": cheap["id"]})

        print("\n[10] Khong du tien → 409, KHONG duoc mon")
        # ⚠️ PHAI HA VI XUONG TRUOC. Lan dau bo do lay "mon dat nhat" roi doi no vuot
        #    so du — nhung sau khi mua mon re nhat, so du con 160 con mon dat nhat chi
        #    150, nen KHONG con mon nao mua khong noi va phep kiem bao hong OAN.
        #    Gieo vi 10 tt thi kich ban "khong du tien" moi ton tai.
        put_item({"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
                  "meteors": {"N": "10"}})
        st, d9 = call("GET", "/me/shop", token=token)
        owned_now = d9.get("owned") or []
        it = next((i for i in paid if i["id"] not in owned_now and i["price"] > 10), None)
        check("co mon dat hon so du de thu", it is not None, str(owned_now))
        if it:
            st, dA = call("POST", "/me/shop/buy", token=token,
                          body={"itemId": it["id"], "opId": "op-poor"})
            check("→ 409 insufficient", st == 409 and dA.get("code") == "insufficient",
                  f"{st} {dA.get('code')}")
            st, dB = call("GET", "/me/shop", token=token)
            check("KHONG duoc mon (hoan tac chay dung)",
                  it["id"] not in (dB.get("owned") or []), str(dB.get("owned")))
            check("so du KHONG bi tru", (dB.get("wallet") or {}).get("meteors") == 10,
                  str((dB.get("wallet") or {}).get("meteors")))

        # Nap lai vi cho muc [11]
        put_item({"PK": {"S": f"USER#{uid}"}, "SK": {"S": "WALLET"},
                  "meteors": {"N": "200"}})

        print("\n[11] 5 loi goi mua SONG SONG cho cung mot mon → chi 1 lan tru tien")
        st, dC = call("GET", "/me/shop", token=token)
        bal0 = (dC.get("wallet") or {}).get("meteors")
        target = next((i for i in paid
                       if i["id"] not in (dC.get("owned") or []) and i["price"] <= bal0), None)
        if target:
            with ThreadPoolExecutor(max_workers=5) as ex:
                res = list(ex.map(
                    lambda k: call("POST", "/me/shop/buy", token=token,
                                   body={"itemId": target["id"], "opId": f"par-{k}"}),
                    range(5)))
            won = [r for r in res if r[0] == 200 and r[1].get("bought") is True]
            check("dung 1 lan mua thanh cong", len(won) == 1,
                  f"{len(won)} thanh cong / 5 loi goi")
            st, dD = call("GET", "/me/shop", token=token)
            check("chi tru tien MOT lan",
                  (dD.get("wallet") or {}).get("meteors") == bal0 - target["price"],
                  f"{bal0} → {(dD.get('wallet') or {}).get('meteors')} (gia {target['price']})")
        else:
            check("co mon de thu song song", False, "khong con mon mua noi")

        print("\n[12] Ten phi thuyen (PUT /me/profile)")
        st, dE = call("PUT", "/me/profile", token=token, body={"ship": "Luna Mot"})
        check("dat ten tau → 200", st == 200, f"{st}")
        check("PUT tra lai ten tau", dE.get("profile", {}).get("ship") == "Luna Mot",
              str(dE.get("profile", {}).get("ship")))
        st, dF = call("GET", "/me/shop", token=token)
        check("GET /me/shop doc lai ten tau", dF.get("ship") == "Luna Mot", str(dF.get("ship")))
        st, dG = call("PUT", "/me/profile", token=token, body={"ship": "x" * 25})
        check("ten tau > 24 ky tu → 400", st == 400 and dG.get("code") == "ship-too-long",
              f"{st} {dG.get('code')}")
        st, dH = call("PUT", "/me/profile", token=token, body={"ship": ""})
        check("ten tau RONG duoc (bo ten di)", st == 200, f"{st}")

        print("\n[13] /me/achievements tra kem mon dang deo + ten tau")
        call("PUT", "/me/profile", token=token, body={"ship": "Luna Mot"})
        st, dI = call("GET", "/me/achievements", token=token)
        check("tra `equipped`", isinstance(dI.get("equipped"), dict), str(dI.get("equipped")))
        check("tra `ship`", dI.get("ship") == "Luna Mot", str(dI.get("ship")))

        print("\n[14] uid trong body/query bi bo qua")
        st, _ = call("POST", "/me/shop/buy?uid=nguoi-khac", token=token,
                     body={"itemId": free[0]["id"], "uid": "nguoi-khac"})
        check("khong sinh ban ghi cho uid khac", len(rows("nguoi-khac")) == 0)

    finally:
        print("\n[don] Xoa du lieu test")
        n = wipe(uid)
        check("Xoa het ban ghi DynamoDB", n > 0, f"{n} dong")
        try:
            _fbtest.delete(token)
            check("Xoa tai khoan Firebase tam", True)
        except Exception as e:                    # noqa: BLE001
            check("Xoa tai khoan Firebase tam", False, str(e))
        check("Khong con ban ghi nao cua uid", len(rows(uid)) == 0)

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
