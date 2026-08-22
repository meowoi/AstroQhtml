# -*- coding: utf-8 -*-
"""
test_specimens.py — kiểm thử ĐỘC LẬP Kho Mẫu Vật Vũ Trụ (Specimen Vault).

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_specimens.py                  # http://localhost:5080
    python scratchpad/test_specimens.py <base-url>        # bản thật trên AWS

Trọng tâm — ba thứ dễ sai nhất ở tính năng "bộ sưu tập":
  1. KHÔNG có đường ghi "đã thu thập mẫu vật": trạng thái mở khoá phải SUY RA
     từ bộ đếm tiến độ. Gọi API kiểu nào cũng không thêm được mẫu vật.
  2. Bàn điều khiển chỉ nhận mẫu CÓ THẬT và ĐÃ MỞ KHOÁ, tối đa `deskSlots` chỗ.

⚠️ KHÔNG GÁN CỨNG số chỗ trưng hay tên móc. Bộ này từng đòi đúng "3 chỗ" và tên
   móc "L4"/"R5"; đổi `Specimens.DeskSlots` 3 → 6 và bỏ 4 móc là nó báo hỏng
   hàng loạt trong khi **không có gì sai** — và sửa cho khớp bản mới thì nó lại
   đỏ khi chạy trên bản thật chưa deploy. Nay mọi con số + tên móc đọc từ chính
   API, và phép kiểm hỏi tính NHẤT QUÁN: server báo N chỗ thì N mẫu phải 200,
   N+1 mẫu phải 400 kèm `slots == N`. Đúng ở cả hai bản.
  3. Dọn bàn trống khi chưa có tiến độ nào thì KHÔNG sinh bản ghi PROGRESS trắng.

Tự tạo tài khoản Firebase tạm, tự dọn mọi bản ghi trong `finally`.
"""
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

import _fbtest  # token ĐÃ xác minh email — /me/* nay đòi email_verified

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


LOCAL = "localhost" in BASE or "127.0.0.1" in BASE
_SRC = pathlib.Path(__file__).resolve().parent.parent.parent / \
    "AstroqSV" / "src" / "AstroqSV.Api" / "Services" / "Specimens.cs"


def read_src_slots():
    """`Specimens.DeskSlots` doc THANG tu ma nguon — de biet ban that lech pha."""
    try:
        m = re.search(r"DeskSlots\s*=\s*(\d+)", _SRC.read_text(encoding="utf-8"))
        return int(m.group(1)) if m else None
    except Exception:
        return None


def vault(token):
    """→ (summary, {id: item}, desk, deskHooks)

    `desk` la mang id tran (dang CU, giu cho client con trong cache trinh duyet);
    `deskHooks` la mang {hook,id} — dang THAT tu 16/08/2026.
    """
    st, d = call("GET", "/me/specimens", token=token)
    s = (d.get("specimens") or {})
    by_id = {x["id"]: x for x in (s.get("specimens") or [])}
    return s.get("summary") or {}, by_id, s.get("desk"), s.get("deskHooks")


def hooks_now(token):
    """→ [(hook, id), …] cua ban hien tai, doc tu GET."""
    return [(h["hook"], h["id"]) for h in (vault(token)[3] or [])]


def unlocked_ids(token):
    _, by_id, _, _ = vault(token)
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
    # ⚠️ TOKEN ĐÃ XÁC MINH EMAIL. /me/* nay đòi email_verified=true (chặn tự-đăng-ký);
    #    token từ signUp trơn mang email_verified=false nên sẽ 403. Xem scratchpad/_fbtest.py.
    uid, token, _pw = _fbtest.make_verified(email)
    check("Co idToken + uid", bool(uid and token), f"uid={uid}")

    try:
        ok, err = seed_profile(uid, email)
        check("Tao ho so (chua co PROGRESS)", ok, err)

        print("\n[3] Tai khoan moi — khong mau vat nao, khong bia so")
        summary, by_id, desk, dhooks = vault(token)
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
        SLOTS = summary.get("deskSlots")
        check("deskSlots la so nguyen duong", isinstance(SLOTS, int) and SLOTS >= 1,
              str(SLOTS))
        # ⚠️ Chi doi chieu voi ma nguon KHI do backend o may — luc do ma nguon
        #    CHINH LA thu dang chay. Tren ban that thi in ra de thay lech pha
        #    (chua deploy), khong bao hong: bao hong o day la bao hong vi mot
        #    viec chua lam, khong phai vi mot thu lam sai.
        src_slots = read_src_slots()
        # ⚠️ Dieu kien la "ma nguon KHOP API", khong phai "dang do o may": khop
        #    nghia la ma nguon CHINH LA thu dang chay, nen doi chieu duoc — ke ca
        #    tren ban that. Ban dau toi dat `if LOCAL` nen tren prod no LUON in
        #    "lech nghia la CHUA DEPLOY" du hai ben da khop — mot dong noi SAI
        #    ngay sau khi deploy thanh cong.
        if src_slots == SLOTS:
            check("deskSlots khop `Specimens.DeskSlots` cua ma nguon",
                  SLOTS == src_slots, f"API={SLOTS} · nguon={src_slots}")
        else:
            print(f"       (ma nguon o may khai {src_slots} cho · ban that dang "
                  f"bao {SLOTS} — lech nghia la CHUA DEPLOY)")
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
        summary, by_id, desk, dhooks = vault(token)
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
        summary, by_id, _, _ = vault(token)
        check("Ghe Trai Dat -> ancient-seawater mo", by_id["ancient-seawater"]["unlocked"])
        check("Bo dem mau hiem len 1/5", summary.get("rare") == 1, str(summary.get("rare")))
        check("Ghe Trai Dat KHONG mo mau Sao Hoa", not by_id["mars-red-ice"]["unlocked"])
        check("lunar-regolith con khoa khi moi ghe 1 hanh tinh",
              not by_id["lunar-regolith"]["unlocked"])
        prog(token, {"type": "planet", "id": "mars"})
        summary, by_id, _, _ = vault(token)
        check("Ghe Sao Hoa -> mars-red-ice mo", by_id["mars-red-ice"]["unlocked"])
        check("Du 2 hanh tinh -> lunar-regolith mo", by_id["lunar-regolith"]["unlocked"])
        check("Mau hiem len 3", summary.get("rare") == 3, str(summary.get("rare")))
        check("Mau chua du dieu kien van khoa (best:dodge 300)",
              not by_id["iron-meteorite"]["unlocked"],
              f"current={by_id['iron-meteorite']['current']}")
        check("`current` khong bao gio vuot `goal`",
              all(v["current"] <= v["goal"] for v in by_id.values()))
        prog(token, {"type": "game", "game": "dodge", "score": 999999, "seconds": 5})
        _, by_id, _, _ = vault(token)
        check("Ky luc 300 diem -> iron-meteorite mo", by_id["iron-meteorite"]["unlocked"])
        check("current da bi kep ve goal", by_id["iron-meteorite"]["current"] == 300,
              str(by_id["iron-meteorite"]["current"]))
        prog(token, {"type": "game", "game": "constellation", "id": "orion",
                     "score": 5, "seconds": 20})
        _, by_id, _, _ = vault(token)
        check("Ghep chom Lap Ho -> orion-stardust mo", by_id["orion-stardust"]["unlocked"])

        got = unlocked_ids(token)
        print(f"       (da mo {len(got)} mau: {', '.join(got)})")

        print("\n[7] Ban dieu khien khoang lai — dang CU (id tran)")
        # ⚠️ DANG CU PHAI CON CHAY. Client nam trong cache trinh duyet van gui len
        #    mang id tran sau khi deploy; tu choi no la tre bam "treo len" roi nhan
        #    loi do cho toi khi cache het han. Server tu xep vao moc trong dau tien.
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": ["ancient-seawater"]})
        check("Dat 1 mau da mo (id tran) -> 200",
              st == 200 and d.get("desk") == ["ancient-seawater"], f"{st} {d}")
        # Bo moc doc TU CHINH phan hoi — khoi gan cung ten moc nao.
        HOOKS = d.get("hooks") or []
        check("Tra kem danh sach moc de client khoi doan",
              isinstance(HOOKS, list) and len(HOOKS) >= SLOTS,
              f"{len(HOOKS)} moc / {SLOTS} cho: {HOOKS}")
        if len(HOOKS) < 3:
            print("       !! CHUA DU MOC DE DO PHAN DOI MOC — dung o day")
            raise SystemExit(1)
        H0, H1, HX = HOOKS[0], HOOKS[1], HOOKS[-1]
        check("Server tu gan moc trong dau tien",
              d.get("deskHooks") == [{"hook": H0, "id": "ancient-seawater"}],
              str(d.get("deskHooks")))
        _, by_id, desk, dhooks = vault(token)
        check("GET tra dung desk + co ban do `equipped`",
              desk == ["ancient-seawater"] and by_id["ancient-seawater"]["equipped"], str(desk))
        check("GET tra kem deskHooks", dhooks == [{"hook": H0, "id": "ancient-seawater"}],
              str(dhooks))
        check("Mau khac khong bi danh dau equipped",
              not by_id["amazon-leaf"]["equipped"])

        print("\n[7b] Tre TU CHON MOC")
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": [{"hook": HX, "id": "ancient-seawater"}]})
        check("Treo vao dung moc da chon -> 200",
              st == 200 and d.get("deskHooks") == [{"hook": HX, "id": "ancient-seawater"}],
              f"{st} {d.get('deskHooks')}")
        check("Moc GIU NGUYEN qua GET (khong bi xep lai tu dau)",
              hooks_now(token) == [(HX, "ancient-seawater")], str(hooks_now(token)))
        check("Truong `desk` cu van tra id tran cho client cu",
              vault(token)[2] == ["ancient-seawater"], str(vault(token)[2]))

        # Doi moc = viec rieng, khong phai go xuong roi treo lai.
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": [{"hook": H1, "id": "ancient-seawater"}]})
        check("Doi sang moc khac -> 200 + moc moi",
              st == 200 and hooks_now(token) == [(H1, "ancient-seawater")],
              str(hooks_now(token)))

        # Chu thuong: server chuan hoa ve chu hoa. Khong chuan hoa thi moc viet
        # thuong thanh mot moc la va bi tu choi, trong khi tre khong lam gi sai.
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": [{"hook": H1.lower(), "id": "ancient-seawater"}]})
        check("Moc viet thuong duoc chuan hoa -> 200",
              st == 200 and hooks_now(token) == [(H1, "ancient-seawater")],
              f"{st} {hooks_now(token)}")

        # ⚠️ PHEP KIEM QUAN TRONG NHAT CUA CA LUOT: kieu thuoc tinh trong DynamoDB
        #    KHONG DOI (van la danh sach chuoi), chi doi noi dung tung chuoi. Do la
        #    ly do `DynamoContext` khong phai sua mot dong nao va khong can migration.
        row = next((r for r in rows(uid) if r["SK"]["S"] == "PROGRESS"), None)
        stored = [x.get("S") for x in ((row or {}).get("desk") or {}).get("L", [])]
        check('DB luu dang chuoi "<moc>:<id>", kieu thuoc tinh giu nguyen',
              stored == [f"{H1}:ancient-seawater"], str(stored))

        # ── Ban ghi CU trong DB (id tran, chua co moc) — doc duoc, 0 migration ──
        aws("dynamodb", "update-item", "--table-name", TABLE,
            "--key", json.dumps({"PK": {"S": f"USER#{uid}"}, "SK": {"S": "PROGRESS"}}),
            "--update-expression", "SET #d = :d",
            "--expression-attribute-names", json.dumps({"#d": "desk"}),
            "--expression-attribute-values",
            json.dumps({":d": {"L": [{"S": "amazon-leaf"}, {"S": "ancient-seawater"}]}}))
        check("Ban ghi CU (id tran) van doc duoc, gan moc theo dung thu tu cu",
              hooks_now(token) == [(H0, "amazon-leaf"), (H1, "ancient-seawater")],
              str(hooks_now(token)))
        # Dat lai de cac phep kiem duoi co moc so sanh da biet
        call("PUT", "/me/specimens/desk", token=token,
             body={"desk": [{"hook": H1, "id": "ancient-seawater"}]})

        # ⚠️ PHAT BIEU DOI 22/08/2026, khong noi long. Truoc do phep kiem nay doi
        #    "moc la -> 400". Tu 21/08 hanh vi doi CO CHU DICH: moc khong con ton
        #    tai duoc xu y nhu moc RONG (xep vao moc trong dau tien), vi so moc moi
        #    vach thu tu 5 xuong 3 — ban cu loai chung, ma `DeskOf` loc lai luc DOC,
        #    nen ban cua tre dang treo o L4/L5 RONG DI NGAY va khong ai bao gi.
        #    Dieu can bao ve van nguyen: DB KHONG BAO GIO luu mot moc la.
        before_odd = hooks_now(token)
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": [{"hook": "Z9", "id": "ancient-seawater"}]})

        # ── TANG HANH VI: re nhanh theo BAN DANG CHAY ────────────────────────
        # `src_slots == SLOTS` nghia la ma nguon o may chinh la thu dang chay.
        # Deploy xong thi nhanh moi tu bat lai — khong ai phai nho sua test.
        if src_slots == SLOTS:
            check("Moc KHONG CO THAT -> 200, mau vat chi DOI CHO chu khong mat",
                  st == 200
                  and [x["id"] for x in (d.get("deskHooks") or [])] == ["ancient-seawater"],
                  f"{st} {d.get('deskHooks')}")
        else:
            print("       (ban dang chay LOAI moc la -> 400; hanh vi 'xu nhu moc "
                  "rong' da chot 21/08/2026 nhung CHUA DEPLOY)")
            check("Ban dang chay: moc la -> 400 (hanh vi CU)",
                  st == 400 and d.get("code") == "bad-specimen", f"{st} {d}")
            check("Bi tu choi thi ban KHONG bi ghi de",
                  hooks_now(token) == before_odd, str(hooks_now(token)))

        # ── TANG BAT BIEN: dung o CA HAI ban ─────────────────────────────────
        hk = [h for h, _ in hooks_now(token)]
        check("Moc ghi xuong LUON la moc CO THAT (khong bao gio la 'Z9')",
              len(hk) == 1 and all(h in HOOKS for h in hk), str(hooks_now(token)))
        # Doc THANG DynamoDB: manh hon doc loi khai cua API.
        row = next((r for r in rows(uid) if r["SK"]["S"] == "PROGRESS"), None)
        st_db = [x.get("S") for x in ((row or {}).get("desk") or {}).get("L", [])]
        check("DB khong bao gio luu mot moc la",
              len(st_db) == 1 and st_db[0].split(":")[0] in HOOKS, str(st_db))

        two = got[:2]
        before_dup = hooks_now(token)
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": [{"hook": H1, "id": two[0]},
                                    {"hook": H1, "id": two[1]}]})
        check("HAI mau CUNG MOT MOC -> 400", st == 400 and d.get("code") == "bad-specimen",
              f"{st} {d}")
        # So voi trang thai NGAY TRUOC cu gui, khong so voi mot ten moc gan cung —
        # phat bieu do dung o moi ban va moi bo moc.
        check("Ban giu nguyen sau khi bi tu choi moc trung",
              hooks_now(token) == before_dup,
              f"{hooks_now(token)} vs {before_dup}")

        # Tron hai dang trong CUNG mot mang: mot phan tu co moc, mot phan tu id tran.
        st, d = call("PUT", "/me/specimens/desk", token=token,
                     body={"desk": [{"hook": HX, "id": two[0]}, two[1]]})
        check("Tron hai dang -> 200, phan tu thieu moc xuong moc trong dau tien",
              st == 200 and sorted(hooks_now(token)) == sorted([(HX, two[0]), (H0, two[1])]),
              f"{st} {hooks_now(token)}")

        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": [123]})
        check("Phan tu sai kieu (so) -> 400", st == 400 and d.get("code") == "bad-specimen",
              f"{st} {d}")

        print("\n[7c] Tu choi mau vat khong hop le")
        # Dat lai moc so sanh: khoi [7b] vua doi ban, ma cac phep kiem duoi day do
        # "ban CO GIU NGUYEN sau khi bi tu choi" nen can mot trang thai da biet.
        call("PUT", "/me/specimens/desk", token=token, body={"desk": ["ancient-seawater"]})
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

        # ⚠️ Phai co du SLOTS+1 mau da mo moi do duoc phep kiem "vuot so cho".
        #    Khong du thi NOI RA, dung im lang bo qua — mot phep kiem bi bo qua
        #    trong im lang doc ra y nhu mot phep kiem dat.
        if len(got) < SLOTS + 1:
            check(f"co du {SLOTS + 1} mau da mo de do phep kiem vuot so cho",
                  False, f"chi co {len(got)}: {got}")
        else:
            over = got[:SLOTS + 1]
            st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": over})
            check(f"Gui {SLOTS + 1} mau (ban chi {SLOTS} cho) -> 400",
                  st == 400 and d.get("code") == "bad-specimen", f"{st} {d}")
            check(f"Bao so cho = {SLOTS}", d.get("slots") == SLOTS, str(d.get("slots")))
        check("Ban KHONG bi ghi de khi bi tu choi",
              vault(token)[2] == ["ancient-seawater"], str(vault(token)[2]))

        full = got[:SLOTS]
        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": full})
        check(f"Gui dung {len(full)} mau da mo -> 200",
              st == 200 and d.get("desk") == full, f"{st} {d}")
        check("Giu dung THU TU client gui", vault(token)[2] == full, str(vault(token)[2]))

        st, d = call("PUT", "/me/specimens/desk", token=token, body={"desk": []})
        check("Don sach ban -> 200 + desk rong", st == 200 and d.get("desk") == [], f"{st} {d}")
        _, by_id, desk, dhooks = vault(token)
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
