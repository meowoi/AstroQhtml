# -*- coding: utf-8 -*-
"""probe_char_e2e.py — DO DAU-CUOI duong nhan vat qua API THAT.

Phep kiem quan trong nhat cua ca lan sua: `GET /me/achievements` co tra ve
`character` khong. Neu khong thi cau noi o client (`syncIdentity`) doc ra rong
va cho ra ket luan SAI la "server chua co nhan vat" => day len mot lan vo nghia
moi luot mo trang.

Tao tai khoan tam that, tu don sach trong `finally`.

  python scratchpad/probe_char_e2e.py [http://localhost:5080]
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parent.as_posix())
import _fbtest  # noqa: E402

API = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5080").rstrip("/")
_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [HONG] ") + name
          + (("  [" + str(extra) + "]") if extra else ""))


TABLE = "astroq-main"


def aws(*args):
    return subprocess.run(["aws"] + list(args), capture_output=True, text=True, timeout=60)


def put_profile(uid, email, name="Bin"):
    """Server CO Y khong am tham dung ho so rong, nen phai gieo PROFILE truoc."""
    item = {
        "PK": {"S": "USER#" + uid}, "SK": {"S": "PROFILE"},
        "uid": {"S": uid}, "email": {"S": email}, "name": {"S": name},
        "createdAt": {"S": "2026-08-22T00:00:00.000Z"},
    }
    r = aws("dynamodb", "put-item", "--table-name", TABLE, "--item", json.dumps(item))
    return r.returncode == 0, r.stderr.strip()


def purge(uid):
    r = aws("dynamodb", "query", "--table-name", TABLE,
            "--key-condition-expression", "PK = :pk",
            "--expression-attribute-values", json.dumps({":pk": {"S": "USER#" + uid}}),
            "--projection-expression", "PK,SK", "--consistent-read")
    if r.returncode != 0:
        return 0
    items = json.loads(r.stdout or "{}").get("Items", [])
    for it in items:
        aws("dynamodb", "delete-item", "--table-name", TABLE,
            "--key", json.dumps({"PK": it["PK"], "SK": it["SK"]}))
    return len(items)


def call(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}


def main():
    email = "chare2e-%d@simulator.amazonses.com" % int(time.time())
    uid, token, _pw = _fbtest.make_verified(email)
    print("uid = " + uid)
    try:
        # Ho so phai ton tai truoc: server CO Y khong am tham dung ho so rong
        # (`attribute_exists(PK)`), nen thieu buoc nay la PUT tra 404.
        made, err = put_profile(uid, email)
        chk("gieo duoc ho so PROFILE", made, err)

        st, d = call("GET", "/me/achievements", token)
        chk("GET /me/achievements -> 200", st == 200, st)
        chk("response CO khoa `character`", "character" in d, sorted(d.keys()))
        chk("response CO khoa `avatar`", "avatar" in d)
        chk("response CO khoa `name`", "name" in d)
        chk("chua chon gi -> character rong (KHONG bia)", d.get("character") == "",
            repr(d.get("character")))

        st, _ = call("PUT", "/me/profile", token,
                     {"character": "cua", "avatar": "ava/avacua.png", "name": "Bin"})
        chk("PUT /me/profile -> 200", st == 200, st)

        st, d = call("GET", "/me/achievements", token)
        chk("sau khi ghi: achievements tra dung nhan vat", d.get("character") == "cua",
            repr(d.get("character")))
        chk("sau khi ghi: tra dung avatar", d.get("avatar") == "ava/avacua.png",
            repr(d.get("avatar")))
        chk("sau khi ghi: tra dung ten", d.get("name") == "Bin", repr(d.get("name")))

        st, d2 = call("GET", "/me/profile", token)
        chk("hai route noi CUNG mot nhan vat",
            (d2.get("profile") or {}).get("character") == d.get("character"),
            "%r vs %r" % ((d2.get("profile") or {}).get("character"), d.get("character")))
    finally:
        try:
            n = purge(uid)
            print("  (don %d dong DynamoDB)" % n)
        except Exception as e:
            print("  (!) don du lieu: " + str(e))
        try:
            tok = _fbtest.signin(email, _pw)
            _fbtest.delete(tok)
        except Exception:
            pass

    print("\n=== KET QUA: %d dat / %d hong ===" % (_n["ok"], _n["ng"]))
    return 1 if _n["ng"] else 0


if __name__ == "__main__":
    sys.exit(main())
