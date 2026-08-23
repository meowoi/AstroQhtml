# -*- coding: utf-8 -*-
"""
probe_visit_beacon.py — BEACON ĐẾM LƯỢT ĐẾN: đo TỚI TẬN DynamoDB, không chỉ tới mép mạng.

    cd AstroqSV/src/AstroqSV.Api && dotnet run
    python scratchpad/probe_visit_beacon.py

⚠️⚠️ VÌ SAO PHẢI ĐO ĐẾN DB, VÀ ĐÂY LÀ BÀI HỌC ĐÃ TRẢ GIÁ NGAY LÚC VIẾT:
   Bản đầu của bộ đo này chạy máy chủ tĩnh ở cổng **8132** và chỉ kiểm "có bắn ra 1
   request /visit". Nó XANH — trong khi **0 bản ghi** vào được DynamoDB. Lý do:
   `ALLOWED_ORIGINS` không có cổng 8132, nên preflight bị CORS chặn và POST thật
   không bao giờ đi. Một phép kiểm đếm request ở phía TRÌNH DUYỆT không chứng minh
   được server có nhận; nó chỉ chứng minh client có gọi.
   ⇒ Bộ này chạy ở **cổng 8000** (cổng CÓ trong `ALLOWED_ORIGINS`) và mọi phép kiểm
     đều đối chiếu **con số trong DynamoDB**, cộng thêm mã phản hồi 204.

⚠️ NHÃN TEST `zzbeacon/...`, TUYỆT ĐỐI KHÔNG DÙNG NHÃN THẬT. Bản đầu dùng luôn
   `facebook/paid/aug2026` — tức nhãn của chiến dịch đang đốt tiền thật. May là CORS
   chặn nên không có gì bẩn, nhưng nếu cổng đúng thì nó đã cộng lượt test vào số liệu
   marketing thật. `finally` xoá bản ghi test.

⚠️ MÁY CHẠY Ở NHÀ VẪN DÙNG DYNAMODB THẬT (appsettings.Development.json ghi rõ).

Sáu điều bộ này giữ:
  ① khách MANG NHÃN → đúng 1 request, server 204, bộ đếm DB +1
  ② khách VÀO THẲNG → 0 request (giữ lời hứa "0 request" ở đầu js/utm.js)
  ③ cùng một khách nạp lại → KHÔNG đếm đôi (đếm khách mới, không đếm lượt bấm)
  ④ link QUÊN GẮN NHÃN nhưng có `fbclid` → vẫn đếm, nhãn `facebook/fbclid`
  ⑤ `fbclid` KHÔNG được tự nhận là `paid` — nó có cả ở bài đăng thường
  ⑥ đến bằng TRANG SÂU (không phải trang chủ) → vẫn bắt được nhãn và vẫn đếm
"""
import sys, os, threading, http.server, socketserver, functools, datetime
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
import boto3
ROOT=os.getcwd(); TABLE="astroq-main"
DAY=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
LABEL="zzbeacon/paid/probe"          # NHAN TEST, khong dung nhan that
QS="?utm_source=zzbeacon&utm_medium=paid&utm_campaign=probe"
ddb=boto3.client("dynamodb")
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
class Q(socketserver.TCPServer): allow_reuse_address=True
srv=Q(("127.0.0.1",8000),functools.partial(H,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()
BASE="http://127.0.0.1:8000"; API="http://localhost:5080"
ok=bad=0
def check(l,c,d=""):
    global ok,bad
    if c: ok+=1; print("  [OK]   %s%s"%(l,"  (%s)"%d if d else ""))
    else: bad+=1; print("  [HONG] %s%s"%(l,"  (%s)"%d if d else ""))
def count_of(label):
    r=ddb.get_item(TableName=TABLE,Key={"PK":{"S":"VISIT#"+DAY},"SK":{"S":"SRC#"+label}})
    it=r.get("Item")
    return 0 if not it else int(it["n"]["N"])

def count():
    return count_of(LABEL)
try:
    with sync_playwright() as p:
        b=p.chromium.launch()
        def go(url):
            ctx=b.new_context(); pg=ctx.new_page()
            reqs=[]; resp=[]; errs=[]
            pg.on("request", lambda r: reqs.append(r.url) if "/visit" in r.url else None)
            pg.on("response", lambda r: resp.append(r.status) if "/visit" in r.url else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.add_init_script("try{localStorage.setItem('astroq-api','%s')}catch(e){}"%API)
            pg.goto(url, wait_until="load"); pg.wait_for_timeout(2000)
            ctx.close(); return reqs,resp,errs

        n0=count()
        print("\n=== [1] Khach MANG NHAN: request DEN DUOC server va DB cong len ===")
        r,rs,e=go(BASE+"/index.html"+QS)
        check("gui dung 1 request /visit", len(r)==1, "%d request"%len(r))
        check("server tra 204 (khong bi CORS chan)", rs==[204], "ma phan hoi=%s"%rs)
        n1=count()
        check("bo dem trong DynamoDB cong dung 1", n1==n0+1, "%d -> %d"%(n0,n1))
        check("0 loi trang", not e, str(e[:1]))

        print("\n=== [2] Khach VAO THANG: 0 request, DB khong doi ===")
        r,rs,e=go(BASE+"/index.html")
        check("KHONG gui request nao", len(r)==0, "%d request"%len(r))
        check("bo dem KHONG doi", count()==n1, "van %d"%count())
        check("0 loi trang", not e, str(e[:1]))

        print("\n=== [3] Cung mot khach nap lai: khong dem doi ===")
        ctx=b.new_context(); pg=ctx.new_page()
        rq=[]
        pg.on("request", lambda x: rq.append(x.url) if "/visit" in x.url else None)
        pg.add_init_script("try{localStorage.setItem('astroq-api','%s')}catch(e){}"%API)
        pg.goto(BASE+"/index.html"+QS, wait_until="load"); pg.wait_for_timeout(1500)
        a=len(rq)
        pg.goto(BASE+"/index.html"+QS, wait_until="load"); pg.wait_for_timeout(1500)
        check("nap lan 2 khong gui them", a==1 and len(rq)==1, "lan1=%d tong=%d"%(a,len(rq)))
        check("bo dem chi cong 1 cho khach nay", count()==n1+1, "= %d"%count())
        # ═══════════ [4] LUOI DO fbclid: link quen gan nhan ═══════════
        print("\n=== [4] Link QUEN gan nhan nhung co fbclid ===")
        LB_FB = "facebook/fbclid"
        n_fb0 = count_of(LB_FB)
        ctx = b.new_context(); pg = ctx.new_page()
        rq = []; rs = []
        pg.on("request", lambda x: rq.append(x.url) if "/visit" in x.url else None)
        pg.on("response", lambda x: rs.append(x.status) if "/visit" in x.url else None)
        pg.add_init_script("try{localStorage.setItem('astroq-api','%s')}catch(e){}" % API)
        pg.goto(BASE + "/index.html?fbclid=IwAR_khong_co_utm_123", wait_until="load")
        pg.wait_for_timeout(2000)
        lbl = pg.evaluate("()=>window.AstroQUtm.get()")
        check("nhan doc ra 'facebook/fbclid'", lbl == LB_FB, repr(lbl))
        check("van gui 1 request", len(rq) == 1, "%d" % len(rq))
        check("server 204", rs == [204], str(rs))
        check("bo dem DB cong 1", count_of(LB_FB) == n_fb0 + 1,
              "%d -> %d" % (n_fb0, count_of(LB_FB)))
        # ⚠️ fbclid KHONG duoc tu nhan la `paid`: no co ca o bai dang thuong.
        check("KHONG tu nhan la paid", "paid" not in (lbl or ""), repr(lbl))
        ctx.close()

        print("\n=== [5] utm_source co san thi fbclid KHONG duoc de len ===")
        ctx = b.new_context(); pg = ctx.new_page()
        pg.add_init_script("try{localStorage.setItem('astroq-api','%s')}catch(e){}" % API)
        pg.goto(BASE + "/index.html" + QS + "&fbclid=IwAR_test", wait_until="load")
        pg.wait_for_timeout(1500)
        got = pg.evaluate("()=>window.AstroQUtm.get()")
        check("nhan tu dat thang fbclid", got == LABEL, repr(got))
        ctx.close()

        print("\n=== [6] Den bang TRANG SAU (khong phai trang chu) ===")
        LB_D = "zzdeep/paid/probe"
        n_d0 = count_of(LB_D)
        ctx = b.new_context(); pg = ctx.new_page()
        rq2 = []
        pg.on("request", lambda x: rq2.append(x.url) if "/visit" in x.url else None)
        pg.add_init_script("try{localStorage.setItem('astroq-api','%s')}catch(e){}" % API)
        pg.goto(BASE + "/pricing.html?utm_source=zzdeep&utm_medium=paid&utm_campaign=probe",
                wait_until="load")
        pg.wait_for_timeout(2500)
        check("pricing.html bat duoc nhan", pg.evaluate("()=>window.AstroQUtm.get()") == LB_D)
        check("pricing.html gui 1 request", len(rq2) == 1, "%d" % len(rq2))
        check("bo dem DB cong 1", count_of(LB_D) == n_d0 + 1,
              "%d -> %d" % (n_d0, count_of(LB_D)))
        ctx.close()

        # ═══════════ [7] POST HONG -> giu co, luot sau BAO BU ═══════════
        # ⚠️ PHEP KIEM DANG GIA NHAT: truoc khi co co ben, POST hong la MAT LUOT
        #    vinh vien. Chan mang o luot dau, mo lai o luot sau, doi DB len dung 1.
        print("\n=== [7] POST hong -> khong mat luot, lan sau bao bu ===")
        LB_R = "zzretry/paid/probe"
        n_r0 = count_of(LB_R)
        ctx = b.new_context(); pg = ctx.new_page()
        pg.route("**/visit", lambda r: r.abort())          # chan: POST khong den duoc
        pg.add_init_script("try{localStorage.setItem('astroq-api','%s')}catch(e){}" % API)
        pg.goto(BASE + "/index.html?utm_source=zzretry&utm_medium=paid&utm_campaign=probe",
                wait_until="load")
        pg.wait_for_timeout(2000)
        check("mang hong -> DB KHONG cong", count_of(LB_R) == n_r0, "= %d" % count_of(LB_R))
        check("co van la CHUA BAO", pg.evaluate("()=>window.AstroQUtm.pending()") == LB_R)
        pg.unroute("**/visit")                              # mo mang lai
        pg.goto(BASE + "/library.html", wait_until="load")  # trang KHAC, khong co utm
        pg.wait_for_timeout(2500)
        check("luot sau BAO BU duoc", count_of(LB_R) == n_r0 + 1,
              "%d -> %d" % (n_r0, count_of(LB_R)))
        check("bao xong thi co tat", pg.evaluate("()=>window.AstroQUtm.pending()") == "")
        ctx.close()
        b.close()
finally:
    srv.shutdown()
    # ⚠️ Don MOI nhan bo nay tao ra, ke ca `facebook/fbclid` — no KHONG mang tien to
    #    zz* vi phai la nhan THAT ma luoi do sinh ra, nen de sot nhat.
    _rac = ["SRC#" + LABEL, "SRC#facebook/fbclid",
            "SRC#zzdeep/paid/probe", "SRC#zzretry/paid/probe"]
    for _sk in _rac:
        ddb.delete_item(TableName=TABLE, Key={"PK":{"S":"VISIT#"+DAY},"SK":{"S":_sk}})
    _left=[i["SK"]["S"] for i in ddb.query(TableName=TABLE,
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={":pk":{"S":"VISIT#"+DAY}}).get("Items",[])
        if i["SK"]["S"] in _rac]
    check("da don sach moi ban ghi test", not _left, str(_left))
    print("\n=== KET QUA: %d dat / %d hong ==="%(ok,bad))
    sys.exit(1 if bad else 0)
