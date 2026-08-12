# -*- coding: utf-8 -*-
"""
test_billing.py — kiem thu API duong THANH TOAN, doc lap voi giao dien
(quy tac 4 muc 6 CLAUDE.md: test API dat het roi moi tich hop vao client).

    # o may:  cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/test_billing.py                     # http://localhost:5080
    python scratchpad/test_billing.py --prod              # ban that AWS

TRONG TAM — thu de lam mat tien / mat don:
  1. CLIENT KHONG DUOC QUYET SO TIEN. Gui `amount` len phai bi bo qua hoan toan.
  2. `paid` CHI dat duoc bang WEBHOOK CO CHU KY DUNG. Chu ky sai -> 400, don khong doi.
  3. Bam "Thanh toan" hai lan (cung opId) -> DUNG MOT don, khong phai hai.
  4. Webhook gui lai lan hai (cong that luon lam vay) -> khong lat trang thai.
  5. Khong doc duoc don cua nguoi khac.
  6. SALE_OPEN dong -> `sale-closed` VA khong ghi mot dong nao vao DB.

⚠️ Nhan cua chk() PHAI KHONG DAU — console Windows mac dinh cp1252, in chu co dau
   la UnicodeEncodeError nem GIUA LUC CHAY va bo do moi phep kiem phia sau.
"""
import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
import uuid
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _fbtest  # noqa: E402  (mint ID token da xac minh)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROD = "--prod" in sys.argv
BASE = ("https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com"
        if PROD else "http://localhost:5080")
TABLE = "astroq-main"
# Phai khop PAY_WEBHOOK_SECRET cua appsettings.Development.json
SECRET = os.environ.get("PAY_WEBHOOK_SECRET", "mock-secret-chi-dung-o-may-local")

ok_n = bad_n = 0
made_orders = []      # don da tao -> don o cuoi
made_uids = []        # uid tam -> don o cuoi
made_tokens = []      # ID token de xoa tai khoan Firebase tam


def new_account():
    """
    Tai khoan tam co ID token DA XAC MINH (nhom /me doi email_verified).
    ⚠️ `_fbtest.make_verified` nhan EMAIL va tra ve TUPLE (uid, token, pw) —
       nhat ky du an da mot lan mat mot luot chay vi doc no nhu mot dict.
    """
    email = f"billtest-{uuid.uuid4().hex[:10]}@simulator.amazonses.com"
    uid, token, _pw = _fbtest.make_verified(email)
    made_uids.append(uid)
    made_tokens.append(token)
    return uid, token


def chk(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def call(method, path, body=None, token=None, headers=None, raw_body=None):
    """Tra ve (status, dict|str). Khong bao gio nem — nhanh hong cung la mot phep kiem."""
    data = None
    if raw_body is not None:
        data = raw_body.encode("utf-8")
    elif body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    for k, v in (headers or {}).items():
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            txt = r.read().decode("utf-8")
            try:
                return r.status, json.loads(txt)
            except json.JSONDecodeError:
                return r.status, txt
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt)
        except json.JSONDecodeError:
            return e.code, txt
    except Exception as e:
        return 0, str(e)


def sign(body_str):
    return hmac.new(SECRET.encode("utf-8"), body_str.encode("utf-8"),
                    hashlib.sha256).hexdigest().upper()


def ddb(args):
    """aws dynamodb ... — doc/xoa truc tiep de xac minh thu server THAT SU ghi gi."""
    r = subprocess.run(["aws", "dynamodb"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {}
    except json.JSONDecodeError:
        return None


def get_item(pk, sk):
    return ddb(["get-item", "--table-name", TABLE, "--key",
                json.dumps({"PK": {"S": pk}, "SK": {"S": sk}}), "--output", "json"])


def main():
    print(f"\n=== test_billing.py -> {BASE} ===")

    # ══════════════ [1] Bang gia — cong khai ══════════════
    print("\n[1] GET /billing/catalog (cong khai)")
    st, d = call("GET", "/billing/catalog")
    chk("catalog tra 200 khong can token", st == 200, str(st))
    offers = (d or {}).get("offers") or []
    chk("co du 5 muc ban", len(offers) == 5, str(len(offers)))
    by = {(o["plan"], o["cycle"]): o for o in offers}
    chk("astro:month = 99000 VND", by[("astro", "month")]["amount"] == 99000,
        str(by[("astro", "month")]["amount"]))
    chk("astro:year = 790000 VND", by[("astro", "year")]["amount"] == 790000)
    chk("crew:month = 169000 VND", by[("crew", "month")]["amount"] == 169000)
    chk("crew:year = 1290000 VND", by[("crew", "year")]["amount"] == 1290000)
    chk("found:once = 1490000 VND", by[("found", "once")]["amount"] == 1490000)
    # ⚠️ Goi mien phi KHONG duoc co trong bang gia — mot muc gia 0 la mot don 0d
    #    tao duoc, tuc mot duong mo goi ma khong tra tien.
    chk("KHONG co muc nao cho goi 'free'",
        not any(o["plan"] == "free" for o in offers))
    chk("trialDays do SERVER tra (client khong go cung)", (d or {}).get("trialDays") == 14,
        str((d or {}).get("trialDays")))

    st, d = call("GET", "/billing/catalog?cur=USD")
    usd = {(o["plan"], o["cycle"]): o for o in (d.get("offers") or [])}
    chk("USD: astro:month = 4.99", abs(usd[("astro", "month")]["amount"] - 4.99) < 1e-9)
    chk("USD: found:once = 69.99", abs(usd[("found", "once")]["amount"] - 69.99) < 1e-9)
    chk("cur la la -> ve VND", call("GET", "/billing/catalog?cur=XYZ")[1]["currency"] == "VND")

    sale_open = bool((d or {}).get("saleOpen"))
    provider = (d or {}).get("provider")
    print(f"       saleOpen={sale_open} provider={provider}")

    # ══════════════ [2] Chua dang nhap thi khong mo duoc don ══════════════
    print("\n[2] Chan truy cap khi khong co token")
    for m, p in (("POST", "/me/billing/checkout"),
                 ("GET", "/me/billing/orders"),
                 ("GET", "/me/billing/order/ord_deadbeef")):
        st, _ = call(m, p, body={} if m == "POST" else None)
        chk(f"{m} {p} -> 401 khi thieu token", st == 401, str(st))
    st, _ = call("POST", "/me/billing/checkout", body={"plan": "astro"}, token="rac.rac.rac")
    chk("token rac -> 401", st == 401, str(st))

    # ══════════════ Tai khoan tam de thu duong that ══════════════
    print("\n[3] Tao tai khoan tam (ID token da xac minh)")
    uid, tok = new_account()
    chk("co ID token va uid", bool(tok) and bool(uid), uid[:10] + "...")

    if not sale_open:
        # ⚠️ Day la trang thai DUNG cua ban that hom nay: chua chon cong thanh toan.
        print("\n[4] SALE_OPEN dang DONG -> kiem dung nhanh do")
        st, d = call("POST", "/me/billing/checkout", token=tok,
                     body={"plan": "astro", "cycle": "year", "opId": "op-test-closed-1"})
        chk("checkout tra sale-closed", st == 200 and d.get("reason") == "sale-closed",
            f"{st} {d}")
        chk("KHONG tra payUrl", not (d or {}).get("payUrl"))
        # Va quan trong nhat: khong ghi mot dong nao
        it = get_item(f"USER#{uid}", "ORDERKEY#op-test-closed-1")
        chk("KHONG ghi ban ghi chong trung nao vao DB",
            it is not None and not it.get("Item"), str(bool((it or {}).get("Item"))))
        st, d = call("GET", "/me/billing/orders", token=tok)
        chk("danh sach don van rong", st == 200 and len(d.get("orders") or []) == 0,
            str(len((d or {}).get("orders") or [])))
        print("\n  → Bo qua muc [5]-[9] (can SALE_OPEN=true + PAY_PROVIDER=mock, chi bat o may).")
        return finish()

    # ══════════════ [4] Body sai ══════════════
    print("\n[4] Body khong hop le")
    for body, why in (
        ({"plan": "khong-co", "cycle": "year", "opId": "op-bad-1"}, "goi khong ton tai"),
        ({"plan": "astro", "cycle": "decade", "opId": "op-bad-2"}, "chu ky khong ton tai"),
        ({"plan": "found", "cycle": "month", "opId": "op-bad-3"}, "found chi ban 'once'"),
        ({"plan": "free", "cycle": "month", "opId": "op-bad-4"}, "goi mien phi khong ban"),
        ({"plan": "astro", "cycle": "year", "opId": "x"}, "opId qua ngan"),
        ({"plan": "astro", "cycle": "year"}, "thieu opId"),
    ):
        st, d = call("POST", "/me/billing/checkout", token=tok, body=body)
        chk(f"400 khi {why}", st == 400, f"{st} {(d or {}).get('reason')}")

    # ══════════════ [5] SO TIEN DO SERVER QUYET ══════════════
    print("\n[5] Client KHONG duoc quyet so tien")
    st, d = call("POST", "/me/billing/checkout", token=tok, body={
        "plan": "astro", "cycle": "year", "currency": "VND",
        "opId": "op-amount-hack-1",
        # Moi truong duoi day la thu client co the co gang nhet vao
        "amount": 1, "Amount": 1, "price": 1, "total": 1, "amountVnd": 1
    })
    chk("checkout thanh cong", st == 200 and d.get("ok"), f"{st} {d}")
    o = (d or {}).get("order") or {}
    made_orders.append(o.get("orderId"))
    chk("so tien la 790000 (bang gia server), KHONG phai 1",
        o.get("amount") == 790000, str(o.get("amount")))
    chk("trang thai khoi tao la pending", o.get("status") == "pending", str(o.get("status")))
    chk("co payUrl de sang cong", bool((d or {}).get("payUrl")))
    chk("server tra firstChargeAt (client khong tu tinh)",
        bool((d or {}).get("firstChargeAt")), str((d or {}).get("firstChargeAt"))[:19])
    chk("goi nam co nextChargeAt", bool((d or {}).get("nextChargeAt")))
    # Doc thang DB: so tien trong ban ghi cung phai la 790000
    it = get_item(f"ORDER#{o.get('orderId')}", "ORDER")
    amt = (((it or {}).get("Item") or {}).get("amount") or {}).get("N")
    chk("DB luu dung 790000", amt == "790000", str(amt))
    chk("ban ghi don KHONG co ttl (don hang la chung tu tien)",
        "ttl" not in ((it or {}).get("Item") or {}), str(list(((it or {}).get("Item") or {}).keys())))
    chk("DB luu uid cua nguoi mua",
        (((it or {}).get("Item") or {}).get("uid") or {}).get("S") == uid)

    order_id = o.get("orderId")

    # ══════════════ [6] Bam hai lan -> mot don ══════════════
    print("\n[6] Bam 'Thanh toan' hai lan (cung opId)")
    st, d2 = call("POST", "/me/billing/checkout", token=tok, body={
        "plan": "astro", "cycle": "year", "opId": "op-amount-hack-1"})
    chk("lan hai tra 200", st == 200, str(st))
    chk("tra ve DUNG don cu, khong tao don moi",
        (d2.get("order") or {}).get("orderId") == order_id,
        f"{(d2.get('order') or {}).get('orderId')} vs {order_id}")
    chk("co co `reused` de client biet", d2.get("reused") is True, str(d2.get("reused")))
    st, dl = call("GET", "/me/billing/orders", token=tok)
    chk("danh sach chi co DUNG 1 don", len(dl.get("orders") or []) == 1,
        str(len(dl.get("orders") or [])))

    # ══════════════ [7] Webhook: chu ky ══════════════
    print("\n[7] Webhook — chu ky la thu duy nhat quyet dinh")
    body = json.dumps({"orderId": order_id, "status": "paid", "ref": "tx_test_1"})

    st, d = call("POST", "/billing/webhook/mock", raw_body=body)
    chk("thieu chu ky -> 400", st == 400, f"{st} {(d or {}).get('reason')}")

    st, d = call("POST", "/billing/webhook/mock", raw_body=body,
                 headers={"X-Astroq-Signature": "00" * 32})
    chk("chu ky sai -> 400", st == 400, f"{st} {(d or {}).get('reason')}")

    st, d = call("POST", "/billing/webhook/mock", raw_body=body,
                 headers={"X-Astroq-Signature": "khong-phai-hex"})
    chk("chu ky khong phai hex -> 400 (khong 500)", st == 400, str(st))

    # Chu ky dung nhung ky trên MOT than KHAC -> phai bi tu choi
    st, d = call("POST", "/billing/webhook/mock", raw_body=body,
                 headers={"X-Astroq-Signature": sign(body + " ")})
    chk("chu ky ky tren than khac -> 400", st == 400, str(st))

    st, d = call("GET", f"/me/billing/order/{order_id}", token=tok)
    chk("sau 4 lan chu ky sai, don VAN pending",
        (d.get("order") or {}).get("status") == "pending",
        str((d.get("order") or {}).get("status")))

    st, d = call("POST", "/billing/webhook/mock", raw_body=body,
                 headers={"X-Astroq-Signature": sign(body)})
    chk("chu ky DUNG -> 200 va changed=true", st == 200 and d.get("changed") is True,
        f"{st} {d}")

    st, d = call("GET", f"/me/billing/order/{order_id}", token=tok)
    o = d.get("order") or {}
    chk("don da chuyen sang paid", o.get("status") == "paid", str(o.get("status")))
    chk("co paidAt", bool(o.get("paidAt")), str(o.get("paidAt"))[:19])
    it = get_item(f"ORDER#{order_id}", "ORDER")
    chk("DB luu providerRef de doi soat",
        (((it or {}).get("Item") or {}).get("providerRef") or {}).get("S") == "tx_test_1")

    # ══════════════ [8] Webhook gui lai / lat trang thai ══════════════
    print("\n[8] Webhook gui lai va co lat trang thai")
    st, d = call("POST", "/billing/webhook/mock", raw_body=body,
                 headers={"X-Astroq-Signature": sign(body)})
    chk("gui lai lan hai -> 200 (khong bat cong gui mai) va changed=false",
        st == 200 and d.get("changed") is False, f"{st} {d}")

    # ⚠️ Phep kiem quan trong: mot webhook den muon KHONG duoc lat don da paid
    late = json.dumps({"orderId": order_id, "status": "cancelled", "ref": "tx_late"})
    st, d = call("POST", "/billing/webhook/mock", raw_body=late,
                 headers={"X-Astroq-Signature": sign(late)})
    chk("webhook 'cancelled' den muon -> changed=false", d.get("changed") is False, str(d))
    st, d = call("GET", f"/me/billing/order/{order_id}", token=tok)
    chk("don VAN la paid (khong bi lat)", (d.get("order") or {}).get("status") == "paid",
        str((d.get("order") or {}).get("status")))

    # Trang thai la -> tu choi
    weird = json.dumps({"orderId": order_id, "status": "refunded-hehe"})
    st, d = call("POST", "/billing/webhook/mock", raw_body=weird,
                 headers={"X-Astroq-Signature": sign(weird)})
    chk("trang thai khong thuoc bo cho phep -> 400", st == 400, str(st))

    # Don khong ton tai -> 200 changed=false (khong 500)
    ghost = json.dumps({"orderId": "ord_khongcothat", "status": "paid"})
    st, d = call("POST", "/billing/webhook/mock", raw_body=ghost,
                 headers={"X-Astroq-Signature": sign(ghost)})
    chk("don khong ton tai -> 200 changed=false", st == 200 and d.get("changed") is False,
        f"{st} {d}")

    # Cong khong dung ten -> 404
    st, d = call("POST", "/billing/webhook/vnpay", raw_body=body,
                 headers={"X-Astroq-Signature": sign(body)})
    chk("webhook cua cong khac -> 404", st == 404, str(st))

    # ══════════════ [9] Khong doc duoc don cua nguoi khac ══════════════
    print("\n[9] Don cua nguoi khac")
    _uid2, tok2 = new_account()
    st, d = call("GET", f"/me/billing/order/{order_id}", token=tok2)
    # ⚠️ 404 chu KHONG phai 403: 403 noi rang ma don do co that, tuc mot duong do
    #    xem ai da mua gi.
    chk("nguoi khac doc don -> 404 (khong phai 403)", st == 404, str(st))
    st, d = call("GET", "/me/billing/orders", token=tok2)
    chk("danh sach cua nguoi khac rong", len(d.get("orders") or []) == 0)

    # ══════════════ [10] Don da chot thi khong mo lai cong ══════════════
    print("\n[10] Don da chot thi khong mo lai lu[o]t thanh toan")
    st, d = call("POST", "/me/billing/checkout", token=tok, body={
        "plan": "astro", "cycle": "year", "opId": "op-amount-hack-1"})
    chk("khong tra payUrl cho don da paid", not (d or {}).get("payUrl"), str((d or {}).get("payUrl")))
    chk("van tra ve don de client dieu huong dung cho",
        (d.get("order") or {}).get("status") == "paid")

    # ══════════════ [11] returnUrl phai thuoc allowlist ══════════════
    print("\n[11] returnUrl — chong open redirect")
    for url, why in (("https://astroq.org.evil.co/x", "ten mien gia mao"),
                     ("javascript:alert(1)", "khong phai http(s)"),
                     ("http://ke-khac.example/thanks", "ngoai allowlist")):
        st, d = call("POST", "/me/billing/checkout", token=tok, body={
            "plan": "crew", "cycle": "month", "opId": f"op-ret-{abs(hash(url)) % 99999}",
            "returnUrl": url})
        pay = (d or {}).get("payUrl") or ""
        if (d or {}).get("order"):
            made_orders.append(d["order"].get("orderId"))
        chk(f"khong dua {why} vao payUrl", url.split("//")[-1].split("/")[0] not in pay,
            pay[:70])

    # ══════════════ [12] Cong gia lap: di het duong that ══════════════
    print("\n[12] Cong GIA LAP — tao don, sang cong, cong goi webhook ve")
    st, d = call("POST", "/me/billing/checkout", token=tok, body={
        "plan": "crew", "cycle": "year", "currency": "VND", "opId": "op-e2e-1",
        "returnUrl": "http://localhost:8000/checkout.html"})
    oid2 = (d.get("order") or {}).get("orderId")
    made_orders.append(oid2)
    pay = d.get("payUrl")
    chk("mo duoc lu[o]t thanh toan", bool(pay), str(pay)[:60])
    # Di theo payUrl nhu trinh duyet, KHONG tu goi webhook
    st, _ = call("GET", pay.replace(BASE, "") if pay.startswith(BASE) else pay)
    time.sleep(1.0)
    st, d = call("GET", f"/me/billing/order/{oid2}", token=tok)
    chk("sau khi di qua cong gia lap, don la paid",
        (d.get("order") or {}).get("status") == "paid",
        str((d.get("order") or {}).get("status")))
    chk("so tien dung 1290000", (d.get("order") or {}).get("amount") == 1290000,
        str((d.get("order") or {}).get("amount")))

    return finish()


def finish():
    # ══════════════ Don sach ══════════════
    print("\n[dọn] Xoa du lieu test")
    for oid in [o for o in made_orders if o]:
        ddb(["delete-item", "--table-name", TABLE, "--key",
             json.dumps({"PK": {"S": f"ORDER#{oid}"}, "SK": {"S": "ORDER"}})])
    for uid in made_uids:
        # Con tro + khoa chong trung nam duoi PK cua user
        q = ddb(["query", "--table-name", TABLE,
                 "--key-condition-expression", "PK = :pk",
                 "--expression-attribute-values", json.dumps({":pk": {"S": f"USER#{uid}"}}),
                 "--output", "json"])
        for item in (q or {}).get("Items", []):
            ddb(["delete-item", "--table-name", TABLE, "--key",
                 json.dumps({"PK": item["PK"], "SK": item["SK"]})])
    n = sum(1 for t in made_tokens if _fbtest.delete(t))
    print(f"  da xoa {len([o for o in made_orders if o])} don, "
          f"{len(made_uids)} ban ghi user, {n}/{len(made_tokens)} tai khoan Firebase")

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
