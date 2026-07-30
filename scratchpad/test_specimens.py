# -*- coding: utf-8 -*-
"""
test_specimens.py — kiểm thử ĐỘC LẬP Kho Mẫu Vật Vũ Trụ (Specimen Vault).

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_specimens.py                  # http://localhost:5080
    python scratchpad/test_specimens.py <base-url>        # bản thật trên AWS

Trọng tâm — ba thứ dễ sai nhất ở tính năng "bộ sưu tập":
  1. KHÔNG có đường ghi "đã thu thập mẫu vật": trạng thái mở khoá phải SUY RA
     từ bộ đếm tiến độ. Gọi API kiểu nào cũng không thêm được mẫu vật.
  2. Bàn điều khiển chỉ nhận mẫu CÓ THẬT và ĐÃ MỞ KHOÁ, tối đa 3 chỗ.
  3. Dọn bàn trống khi chưa có tiến độ nào thì KHÔNG sinh bản ghi PROGRESS trắng.

Tự tạo tài khoản Firebase tạm, tự dọn mọi bản ghi trong `finally`.
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

# Console Windows mặc định cp1252 nên in thông báo lỗi tiếng Việt do server trả về
# là UnicodeEncodeError giữa bài test — mất luôn phần dọn dữ liệu ở `finally`.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
API_KEY = "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A"
IDP = "https://identitytoolkit.googleapis.com/v1/accounts"
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
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, {"_raw": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode() or "{}"
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw}
    except Exception as e:
        return 0, {"_err": str(e)}


def idp(action, payload):
    req = urllib.request.Request(f"{IDP}:{action}?key={API_KEY}",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def aws(*args):
    return subprocess.run(["aws"] + list(args), capture_output=True, text=True, timeout=60)


def seed_profile(uid, email):
    item = {
        "PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROFILE"},
        "uid": {"S": uid}, "email": {"S": email}, "name": {"S": "Vault Test"},
        "createdAt": {"S": "2026-07-29T00:00:00.000Z"},
    }
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(item))
    return r.returncode == 0, r.stderr.strip()


def rows(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": f"USER#{uid}"}}),
            "--consistent-read")
    return [] if r.returncode != 0 else json.loads(r.stdout or "{}").get("Items", [])


def wipe(uid):
    n = 0
    for it in rows(uid):
        if aws("dynamodb", "delete-item", "--table-name", TABLE,
               "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]})).returncode == 0:
            n += 1
    return n


def vault(token):
    """→ (summary, {id: item}, desk)"""
    st, d = call("GET", "/me/specimens", token=token)
    s = (d.get("specimens") or {})
    by_id = {x["id"]: x for x in (s.get("specimens") or [])}
    return s.get("summary") or {}, by_id, s.get("desk")


def unlocked_ids(token):
    _, by_id, _ = vault(token)
    return sorted(k for k, v in by_id.items() if v["unlocked"])


def prog(token, body):
    return call("POST", "/me/progress", token=token, body=dict(body, opId=uuid.uuid4().hex))


def main():
    print(f"=== Kho Mau Vat Vu Tru @ {BASE} ===\n")
    st, _ = call("GET", "/health")
    check("/health tra 200", st == 200, f"status={st}")
    if st != 200:
        print("\nBackend chua bat — dung lai.")
        return 1

    print("\n[1] Khong co token / token rac")
    st, _ = call("GET", "/me/specimens")
    check("GET /me/specimens -> 401", st == 401, f"status={st}")
    st, _ = call("PUT", "/me/specimens/desk", body={"desk": []})
    check("PUT /me/specimens/desk -> 401", st == 401, f"status={st}")
    st, _ = call("GET", "/me/specimens", token="rac.rac.rac")
    check("Token rac -> 401", st == 401, f"status={st}")

    email = f"vault-test-{uuid.uuid4().hex[:10]}@astroq-test.invalid"
    print(f"\n[2] Tao tai khoan tam: {email}")
    acc = idp("signUp", {"email": email, "password": "Test" + uuid.uuid4().hex[:8],
                         "returnSecureToken": True})
    uid, token = acc["localId"], acc["idToken"]
    check("Co idToken + uid", bool(uid and token), f"uid={uid}")

    try:
        ok, err = seed_profile(uid, email)
        check("Tao ho so (chua co PROGRESS)", ok, err)

        print("\n[3] Tai khoan moi — khong mau vat nao, khong bia so")
        summary, by_id, desk = vault(token)
        # ⚠️ KHONG GAN CUNG SO MAU. Test nay tung doi dung 20 mau va bao hong khi
        #    mau thu 21 duoc them — trong khi khong co gi sai. Hoi DIEU MUON BIET:
        #    "API bao dung bang so mau NO DANG CO", va "bo goc khong bi xoa bot".
        #    Cung bai hoc `smoke_vault.py` da ghi trong CLAUDE.md (gan cung "20 mau
        #    vat" o 8 cho); bo do doc thang danh muc tu `Specimens.cs`.
        check("summary.total khop dung so mau API tra ve",
              summary.get("total") == len(by_id), f"total={summary.get('total')} · {len(by_id)} mau")
        check("co it nhat 20 mau (bo goc khong bi xoa bot)", len(by_id) >= 20, f"{len(by_id)} mau")
        check("Da thu thap = 0", summary.get("collected") == 0, str(summary.get("collected")))
        n_rare = sum(1 for v in by_id.values() if v["rarity"] in ("rare", "legendary"))
        check("Chua mo mau nao thi rare = 0", summary.get("rare") == 0, f"{summary.get('rare')}")
        check("rareTotal khop so mau hang hiem trong danh muc",
              summary.get("rareTotal") == n_rare, f"{summary.get('rareTotal')} vs {n_rare}")
        check("deskSlots = 3", summary.get("deskSlots") == 3, str(summary.get("deskSlots")))
        check("Ban dieu khien rong", desk == [], str(desk))
        check("Moi mau deu dang khoa", all(not v["unlocked"] for v in by_id.values()))
        check("4 nhom dung ten", {v["category"] for v in by_id.values()}
              == {"hydro", "bio", "litho", "cosmic"},
              str(sorted({v["category"] for v in by_id.values()})))
        check("Do hiem chi 3 gia tri", {v["rarity"] for v in by_id.values()}
              <= {"common", "rare", "legendary"})
        check("Mau nao cung co metric + goal >= 1",
              all(v.get("metric") and v.get("goal", 0) >= 1 for v in by_id.values()))
        check("co it nhat 5 mau hang hiem (bo goc khong bi xoa bot)", n_rare >= 5, f"{n_rare}")
        check("GET /me/specimens kem so du vi",
              isinstance(call("GET", "/me/specimens", token=token)[1]
                         .get("wallet", {}).get("meteors"), int))

        print("\n[4] Don ban trong khi chua co tien do -> KHONG sinh PROGRESS trang")
        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": []})
        check("PUT desk [] -> 200", st == 200 and d.get("desk") == [], f"{st} {d}")
        check("Khong co ban ghi PROGRESS nao",
              not any(r["SK"]["S"] == "PROGRESS" for r in rows(uid)),
              str([r["SK"]["S"] for r in rows(uid)]))

        print("\n[5] Khong the tu them mau vat bang cach goi API")
        st, d = prog(token, {"type": "quiz", "correct": 0, "total": 1,
                             "specimens": ["europa-brine", "neptune-diamond-dust"],
                             "desk": ["europa-brine"], "unlocked": True})
        check("POST /me/progress nhan 200", st == 200, f"{st} {d}")
        summary, by_id, desk = vault(token)
        check("Truong `specimens` gui kem BI BO QUA",
              not by_id["europa-brine"]["unlocked"] and not by_id["neptune-diamond-dust"]["unlocked"])
        check("Truong `desk` gui kem BI BO QUA", desk == [], str(desk))
        check("Chi mo dung mau theo dieu kien that (quizTaken>=1)",
              unlocked_ids(token) == ["himalaya-crystal"], str(unlocked_ids(token)))

        print("\n[6] Mo khoa suy ra tu bo dem tien do")
        prog(token, {"type": "lesson", "id": "bai-1"})
        check("Doc 1 bai -> amazon-leaf mo", "amazon-leaf" in unlocked_ids(token))
        prog(token, {"type": "game", "game": "dodge", "score": 10, "seconds": 5})
        check("Choi 1 luot -> penguin-feather mo", "penguin-feather" in unlocked_ids(token))
        prog(token, {"type": "planet", "id": "earth"})
        summary, by_id, _ = vault(token)
        check("Ghe Trai Dat -> ancient-seawater mo", by_id["ancient-seawater"]["unlocked"])
        check("Bo dem mau hiem len 1/5", summary.get("rare") == 1, str(summary.get("rare")))
        check("Ghe Trai Dat KHONG mo mau Sao Hoa", not by_id["mars-red-ice"]["unlocked"])
        check("lunar-regolith con khoa khi moi ghe 1 hanh tinh",
              not by_id["lunar-regolith"]["unlocked"])
        prog(token, {"type": "planet", "id": "mars"})
        summary, by_id, _ = vault(token)
        check("Ghe Sao Hoa -> mars-red-ice mo", by_id["mars-red-ice"]["unlocked"])
        check("Du 2 hanh tinh -> lunar-regolith mo", by_id["lunar-regolith"]["unlocked"])
        check("Mau hiem len 3/5", summary.get("rare") == 3, str(summary.get("rare")))
        check("Mau chua du dieu kien van khoa (best:dodge 300)",
              not by_id["iron-meteorite"]["unlocked"],
              f"current={by_id['iron-meteorite']['current']}")
        check("`current` khong bao gio vuot `goal`",
              all(v["current"] <= v["goal"] for v in by_id.values()))
        prog(token, {"type": "game", "game": "dodge", "score": 999999, "seconds": 5})
        _, by_id, _ = vault(token)
        check("Ky luc 300 diem -> iron-meteorite mo", by_id["iron-meteorite"]["unlocked"])
        check("current da bi kep ve goal", by_id["iron-meteorite"]["current"] == 300,
              str(by_id["iron-meteorite"]["current"]))
        prog(token, {"type": "game", "game": "constellation", "id": "orion",
                     "score": 5, "seconds": 20})
        _, by_id, _ = vault(token)
        check("Ghep chom Lap Ho -> orion-stardust mo", by_id["orion-stardust"]["unlocked"])

        got = unlocked_ids(token)
        print(f"       (da mo {len(got)} mau: {', '.join(got)})")

        print("\n[7] Ban dieu khien khoang lai")
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": ["ancient-seawater"]})
        check("Dat 1 mau da mo -> 200", st == 200 and d.get("desk") == ["ancient-seawater"],
              f"{st} {d}")
        _, by_id, desk = vault(token)
        check("GET tra dung desk + co ban do `equipped`",
              desk == ["ancient-seawater"] and by_id["ancient-seawater"]["equipped"], str(desk))
        check("Mau khac khong bi danh dau equipped",
              not by_id["amazon-leaf"]["equipped"])

        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": ["europa-brine"]})
        check("Dat mau CHUA MO KHOA -> 400 bad-specimen",
              st == 400 and d.get("code") == "bad-specimen", f"{st} {d}")
        check("Bao ro id bi tu choi", d.get("rejected") == ["europa-brine"], str(d.get("rejected")))
        check("Ban giu nguyen mau cu sau khi bi tu choi",
              vault(token)[2] == ["ancient-seawater"], str(vault(token)[2]))

        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": ["khong-co-mau-nay"]})
        check("Dat id khong ton tai -> 400", st == 400 and d.get("code") == "bad-specimen",
              f"{st} {d}")
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": ["amazon-leaf", "amazon-leaf"]})
        check("Gui id TRUNG NHAU -> 400", st == 400 and d.get("code") == "bad-specimen", f"{st} {d}")

        four = got[:4]
        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": four})
        check("Gui 4 mau (ban chi 3 cho) -> 400",
              st == 400 and d.get("code") == "bad-specimen", f"{st} {d}")
        check("Bao so cho = 3", d.get("slots") == 3, str(d.get("slots")))
        check("Ban KHONG bi ghi de khi bi tu choi",
              vault(token)[2] == ["ancient-seawater"], str(vault(token)[2]))

        three = got[:3]
        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": three})
        check("Gui dung 3 mau da mo -> 200", st == 200 and d.get("desk") == three, f"{st} {d}")
        check("Giu dung THU TU client gui", vault(token)[2] == three, str(vault(token)[2]))

        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": []})
        check("Don sach ban -> 200 + desk rong", st == 200 and d.get("desk") == [], f"{st} {d}")
        _, by_id, desk = vault(token)
        check("Khong con mau nao equipped",
              desk == [] and not any(v["equipped"] for v in by_id.values()))

        print("\n[8] Than request khong hop le")
        st, d = call("PUT", "/me/specimens/desk", token=token, body={})
        check("Thieu truong desk -> 400 no-desk", st == 400 and d.get("code") == "no-desk",
              f"{st} {d}")
        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": None})
        check("desk: null -> 400 no-desk", st == 400 and d.get("code") == "no-desk", f"{st} {d}")
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": ["amazon-leaf"] * 40})
        check("Mang 40 phan tu -> 400 desk-too-long",
              st == 400 and d.get("code") == "desk-too-long", f"{st} {d}")
        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": ["  "]})
        check("id toan khoang trang -> 400", st == 400, f"{st} {d}")

        print("\n[9] uid trong query/body BI BO QUA (lay tu token)")
        # Mốc so sánh phải đọc LẠI ngay đây: `summary` ở mục [6] đã cũ vì sau đó còn
        # mở thêm mẫu vật, so với nó thì báo hỏng oan.
        base_collected = vault(token)[0]["collected"]
        st, d = call("GET", "/me/specimens?uid=nguoi-khac", token=token)
        check("uid trong query bi bo qua",
              st == 200 and d["specimens"]["summary"]["collected"] == base_collected,
              f"{st} collected={d.get('specimens', {}).get('summary', {}).get('collected')}")
        st, d = call("PUT", "/me/specimens/desk?uid=nguoi-khac", token=token,
                     body={"desk": ["amazon-leaf"], "uid": "nguoi-khac"})
        check("uid trong body bi bo qua, ghi vao dung tai khoan minh",
              st == 200 and vault(token)[2] == ["amazon-leaf"], f"{st} {d}")
        check("Khong sinh ban ghi cho uid la",
              len(rows("nguoi-khac")) == 0, str(len(rows("nguoi-khac"))))

        print("\n[10] Phuong thuc khong ho tro")
        st, _ = call("DELETE", "/me/specimens/desk", token=token)
        check("DELETE /me/specimens/desk -> 404/405", st in (404, 405), f"status={st}")
        st, _ = call("POST", "/me/specimens", token=token, body={})
        check("POST /me/specimens -> 404/405", st in (404, 405), f"status={st}")

    finally:
        print("\n[don] Xoa du lieu test")
        n = wipe(uid)
        check("Xoa het ban ghi DynamoDB", n > 0, f"{n} dong")
        try:
            idp("delete", {"idToken": token})
            check("Xoa tai khoan Firebase tam", True)
        except Exception as e:
            check("Xoa tai khoan Firebase tam", False, str(e))
        check("Khong con ban ghi nao", len(rows(uid)) == 0)

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
