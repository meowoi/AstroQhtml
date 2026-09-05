# -*- coding: utf-8 -*-
"""check_mail_events.py — DUONG THU KICH HOAT CO TOI HOM THU KHONG, DO BANG SO.

    python scratchpad/check_mail_events.py             # doc 14 ngay gan nhat
    python scratchpad/check_mail_events.py --days 3
    python scratchpad/check_mail_events.py --send-test  # gui 1 thu that qua SES simulator

VI SAO CAN BO DO NAY (04/09/2026)
---------------------------------
Doc CloudWatch 14 ngay ra dung **3 luot dang ky bang email that cua nguoi ngoai**,
va **2 trong 3 khong bao gio bam link kich hoat**:

    23/08 12:49  tongthilap2k@gmail.com          thu da gui -> KHONG bam
    30/08 11:29  mocquehoa@gmail.com             thu da gui -> KHONG bam
    30/08 11:30  daothicuc.td@pgdhalong.edu.vn   thu da gui -> bam sau 23 GIAY

Buoc mat 2/3 nguoi do la buoc DUY NHAT cua ca he thong khong co phep do nao:
`ses.SendEmailAsync` tra ve la het dau vet. Vao Inbox, vao Spam, hay bi chan la
ba chuyen khac han nhau, va truoc hom nay ca ba don vao MOT o trong — dung cai
loi ma `/visit` da sinh ra de chua cho luu luong quang cao.

Bo do nay tra loi bang so:
  [1] Log group su kien thu co ton tai va co ai ghi vao khong.
  [2] Configuration set `astroq-auth` co dich EventBridge va co BAT khong.
  [3] DNS cua astroq.org: DKIM, SPF, DMARC, MAIL FROM rieng.
  [4] MOI thu kich hoat da gui co mot su kien `delivery` HOAC `bounce` di kem
      khong. Thieu = thu roi vao khoang toi, va do la loi phai bao.
  [5] Phieu: gui -> toi hom thu -> bam link.

⚠️ `aws` CLI cung la Python: khong dat PYTHONIOENCODING thi CHINH NO chet o chu
   Viet (charmap codec khong ma hoa duoc) va tra ve JSON CUT GIUA CHUNG. Bai hoc
   da ghi o `scratchpad/read_logs.py`; dung bo khi copy doan goi lenh.
"""
import json
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

APP_LOG = "/aws/lambda/AstroqSV"
MAIL_LOG = "/astroq/ses-auth-mail"
CONF_SET = "astroq-auth"
RULE = "astroq-ses-auth-mail"
DOMAIN = "astroq.org"
# Dia chi gia lap cua SES: luon nhan thanh cong, khong ai doc, khong ton hai
# danh tieng cua ten mien. Dung cho `--send-test`.
SIM_OK = "success@simulator.amazonses.com"

_n = {"ok": 0, "ng": 0}
# ⚠️ MOC BAT DAU DO, doc tu creationTime cua log group o buoc [1]. De trong list
#    de cac ham duoi doc duoc ma khong phai chuyen tay qua 4 tang tham so; 0 =
#    chua doc duoc, va khi do buoc [4] KHONG duoc phep ket toi thu nao ca.
since = [0]
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")


def iso(ms):
    """Doi moc thoi gian mili-giay cua CloudWatch ra chuoi gio UTC.

    ⚠️ CloudWatch tra ve MILI-giay, khong phai giay: khong chia 1000 thi ra nam
       nam chuc nghin.
    ⚠️⚠️ UTC CHU KHONG PHAI GIO MAY. Moi moc thoi gian khac trong bo do nay den
       tu Logs Insights, ma Insights tra `@timestamp` bang UTC. Tron hai dong ho
       vao mot bang thi phep so sanh o buoc [4] lech dung 7 gio va bo do se ket
       toi nham nhung thu gui ngay sat moc. Mot dong ho cho ca bo do.
    """
    if not ms:
        return ""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ms / 1000))


def chk(name, cond, extra=""):
    _n["ok" if cond else "ng"] += 1
    print(("  [OK]   " if cond else "  [!!]   ") + name + (("  " + str(extra)) if extra else ""))


def aws(args, allow_fail=False):
    """Goi `aws` CLI, tra ve JSON da phan tich (hoac None khi that bai)."""
    p = subprocess.run(["aws"] + args + ["--output", "json", "--no-cli-pager"],
                       capture_output=True, text=False, shell=True, env=ENV)
    raw = p.stdout.decode("utf-8", "replace").strip()
    if p.returncode != 0 or not raw:
        if not allow_fail:
            print("  [..]   lenh aws that bai: " + " ".join(args[:3]))
            print("         " + p.stderr.decode("utf-8", "replace").strip()[:300])
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def insights(group, query, days):
    """Chay mot cau Logs Insights, tra ve list cac dong da phang hoa."""
    end = int(time.time())
    start = end - days * 86400
    got = aws(["logs", "start-query", "--log-group-name", group,
               "--start-time", str(start), "--end-time", str(end),
               "--query-string", query])
    if not got:
        return None
    qid = got if isinstance(got, str) else got.get("queryId")
    for _ in range(40):
        r = aws(["logs", "get-query-results", "--query-id", qid])
        if not r:
            return None
        if r["status"] not in ("Running", "Scheduled"):
            return [{f["field"]: f["value"] for f in row if f["field"] != "@ptr"}
                    for row in r["results"]]
        time.sleep(1)
    return None


def dns(name, rtype="TXT"):
    """Doc mot ban ghi DNS qua nslookup + 8.8.8.8, khoi phu thuoc resolver may."""
    p = subprocess.run(["nslookup", "-type=" + rtype, name, "8.8.8.8"],
                       capture_output=True, text=False, shell=True, env=ENV)
    return p.stdout.decode("utf-8", "replace")


def metric(name, hours=24):
    """Tong mot chi so cua rule EventBridge trong `hours` gio gan nhat."""
    end = time.time()
    r = aws(["cloudwatch", "get-metric-statistics",
             "--namespace", "AWS/Events", "--metric-name", name,
             "--dimensions", "Name=RuleName,Value=" + RULE,
             "--start-time", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end - hours * 3600)),
             "--end-time", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end)),
             "--period", "3600", "--statistics", "Sum"], allow_fail=True)
    return int(sum(p["Sum"] for p in (r or {}).get("Datapoints", [])))


def emails_in(rows):
    """Rut dia chi dau tien khoi moi dong log."""
    out = []
    for r in rows:
        for tok in (r.get("@message") or "").split():
            if "@" in tok and "." in tok:
                out.append((r.get("@timestamp", ""), tok.strip(".,;()")))
                break
    return out


# ══════════════════════════════════════════════════════════════════════════
def main():
    days = 14
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])

    test_id = send_test() if "--send-test" in sys.argv else None

    print("\n[1] LOG GROUP SU KIEN THU")
    lg = aws(["logs", "describe-log-groups", "--log-group-name-prefix", MAIL_LOG])
    found = [g for g in (lg or {}).get("logGroups", []) if g["logGroupName"] == MAIL_LOG]
    chk("log group %s ton tai" % MAIL_LOG, bool(found),
        "" if found else "-> chua deploy template.yaml (khoi MailEventLogGroup)")
    live = False
    if found:
        chk("giu 90 ngay (dai hon 14 ngay cua log Lambda)",
            found[0].get("retentionInDays") == 90,
            "hien: %s" % found[0].get("retentionInDays"))
        # ⚠️⚠️ ĐỪNG DÙNG `storedBytes` ĐỂ BIẾT CÓ AI GHI VÀO CHƯA — đã trả giá
        #    đúng một lần (04/09/2026, ngay lượt chạy đầu). Trường đó CẬP NHẬT
        #    TRỄ: sự kiện đã vào log group, EventBridge đã báo 2 Invocations và 0
        #    FailedInvocations, mà `storedBytes` vẫn là 0 -> bộ đo bảo một hệ
        #    thống ĐANG CHẠY là hỏng. Nguồn đúng là DANH SÁCH LOG STREAM.
        st = aws(["logs", "describe-log-streams", "--log-group-name", MAIL_LOG,
                  "--order-by", "LastEventTime", "--descending", "--max-items", "5"])
        streams = (st or {}).get("logStreams", [])
        live = bool(streams)
        last = max((s.get("lastEventTimestamp") or 0) for s in streams) if streams else 0
        chk("da co su kien duoc ghi vao", live,
            ("su kien moi nhat: " + iso(last)) if last else "chua co log stream nao")
        # ⚠️⚠️ MOC BAT DAU DO — thu gui TRUOC moc nay KHONG THE co su kien, va do
        #    KHONG phai loi. Bo do ban dau cua toi thieu moc nay va bao 4 thu cua
        #    23-30/08 la "roi vao khoang toi", tuc doi mot he thong tra loi ve
        #    qua khu no chua he quan sat. Doc tu chinh log group thay vi go tay
        #    ngay deploy: mot hang so gan tay se sai vao dung ngay dung lai stack.
        since[0] = found[0].get("creationTime") or 0
        print("      moc bat dau do: %s UTC" % (iso(since[0]) or "?"))

    print("\n[1b] RULE EVENTBRIDGE")
    inv = metric("Invocations")
    fail = metric("FailedInvocations")
    chk("rule co duoc goi (24h)", inv > 0, "%d luot" % inv)
    # ⚠️ Day la phep kiem CHONG HONG IM LANG: thieu resource policy tren log
    #    group thi rule van khop su kien nhung KHONG ghi duoc dong nao, va no
    #    hien ra o dung con so nay.
    chk("khong co luot goi that bai (24h)", fail == 0, "%d luot hong" % fail)

    if test_id:
        hit = insights(MAIL_LOG,
                       'fields @timestamp, detail.eventType '
                       '| filter @message like "%s" | limit 10' % test_id, 1) or []
        kinds = {(r.get("detail.eventType") or "").upper() for r in hit}
        chk("thu thu nghiem co su kien Send", "SEND" in kinds, ",".join(sorted(kinds)))
        chk("thu thu nghiem co su kien Delivery", "DELIVERY" in kinds)

    print("\n[2] CONFIGURATION SET")
    cs = aws(["sesv2", "get-configuration-set", "--configuration-set-name", CONF_SET],
             allow_fail=True)
    chk("configuration set %s ton tai" % CONF_SET, cs is not None)
    if cs is not None:
        chk("dang duoc phep gui",
            cs.get("SendingOptions", {}).get("SendingEnabled") is not False)
        chk("bat chi so danh tieng rieng cho astroQ",
            cs.get("ReputationOptions", {}).get("ReputationMetricsEnabled") is True)
    ds = aws(["sesv2", "get-configuration-set-event-destinations",
              "--configuration-set-name", CONF_SET], allow_fail=True)
    eb = [d for d in (ds or {}).get("EventDestinations", []) if "EventBridgeDestination" in d]
    chk("co dich EventBridge", bool(eb))
    if eb:
        d = eb[0]
        chk("dich dang BAT", d.get("Enabled") is True)
        types = {t.upper() for t in d.get("MatchingEventTypes", [])}
        for need in ("SEND", "DELIVERY", "BOUNCE", "REJECT"):
            chk("theo doi su kien %s" % need, need in types)
        # ⚠️ OPEN/CLICK phai KHONG co: bat chung la de SES nhung mot anh 1x1 va
        #    VIET LAI moi link trong thu — ke ca chinh LINK KICH HOAT. Xem khoi
        #    AuthMailEvents trong template.yaml.
        chk("KHONG bat open/click (khong de SES viet lai link kich hoat)",
            not ({"OPEN", "CLICK"} & types))

    print("\n[3] DNS CUA %s" % DOMAIN)
    spf, dmarc = dns(DOMAIN), dns("_dmarc." + DOMAIN)
    mf_txt, mf_mx = dns("mail." + DOMAIN), dns("mail." + DOMAIN, "MX")
    ident = aws(["sesv2", "get-email-identity", "--email-identity", DOMAIN], allow_fail=True)
    dkim = (ident or {}).get("DkimAttributes", {})
    chk("DKIM da xac thuc", dkim.get("Status") == "SUCCESS", dkim.get("Status"))
    chk("DKIM dang ky ten", dkim.get("SigningEnabled") is True)
    chk("co ban ghi SPF", "v=spf1" in spf,
        "" if "v=spf1" in spf else "-> them TXT: v=spf1 include:amazonses.com ~all")
    chk("co ban ghi DMARC", "v=DMARC1" in dmarc,
        "" if "v=DMARC1" in dmarc else "-> them TXT _dmarc: v=DMARC1; p=none; rua=mailto:...")
    mf = (ident or {}).get("MailFromAttributes", {})
    chk("co MAIL FROM rieng (de SPF thang hang voi %s)" % DOMAIN,
        bool(mf.get("MailFromDomain")),
        mf.get("MailFromDomain") or "-> chua dat; envelope-from van la amazonses.com")
    if mf.get("MailFromDomain"):
        chk("MAIL FROM da xac thuc", mf.get("MailFromDomainStatus") == "SUCCESS",
            mf.get("MailFromDomainStatus"))
        chk("mail.%s co MX cua SES" % DOMAIN, "feedback-smtp" in mf_mx)
        chk("mail.%s co SPF" % DOMAIN, "v=spf1" in mf_txt)

    print("\n[4] GHEP: MOI THU DA GUI CO SU KIEN DI KEM KHONG (%d ngay)" % days)
    sent = insights(APP_LOG,
                    "fields @timestamp, @message "
                    "| filter @message like /email kich hoat toi|email kích hoạt tới/ "
                    "| sort @timestamp asc | limit 500", days) or []
    clicked = insights(APP_LOG,
                       "fields @timestamp, @message "
                       "| filter @message like /Kich hoat xong|Kích hoạt xong/ "
                       "| sort @timestamp asc | limit 500", days) or []
    click_e = {e for _, e in emails_in(clicked)}

    ev = []
    if found:
        ev = insights(MAIL_LOG,
                      "fields @timestamp, detail.eventType, detail.mail.destination.0, "
                      "detail.delivery.smtpResponse, detail.bounce.bounceType "
                      "| sort @timestamp asc | limit 1000", days) or []
    by_mail, why = {}, {}
    for r in ev:
        addr = r.get("detail.mail.destination.0") or ""
        by_mail.setdefault(addr, []).append((r.get("detail.eventType") or "?").upper())
        # Cau tra loi that nam o day: "250 Ok" la may ben kia DA NHAN thu; mot ma
        # 5xx hoac mot bounceType la ly do bang chu, khong phai suy dien.
        note = r.get("detail.delivery.smtpResponse") or r.get("detail.bounce.bounceType")
        if note:
            why[addr] = note

    all_sent = emails_in(sent)
    real = [(t, e) for t, e in all_sent if "simulator.amazonses.com" not in e]
    # ⚠️⚠️ CAT DOI THEO MOC BAT DAU DO. `@timestamp` cua Insights la chuoi UTC
    #    "YYYY-MM-DD HH:MM:SS.mmm", con `iso()` cung tra UTC dung khuon do, nen so
    #    sanh CHUOI o day la du — khong phai phan tich ngay thang, va nho vay khong
    #    con cho nao cho lech mui gio chui vao.
    #    Moc rong (chua doc duoc creationTime) = KHONG ket toi ai. Bo do thieu du
    #    lieu thi phai im, khong duoc doan bua.
    mark = iso(since[0])
    trong_tam = [(t, e) for t, e in real if mark and t[:19] >= mark]
    truoc_moc = len(real) - len(trong_tam)

    print("      thu kich hoat da gui: %d (nguoi that: %d, gui sau moc do: %d)"
          % (len(all_sent), len(real), len(trong_tam)))
    if real:
        print("      %-19s  %-34s  %-24s %-9s %s"
              % ("luc gui (UTC)", "email", "su kien SES", "bam link", "may ben kia noi gi"))
        for t, e in real:
            trong = bool(mark) and t[:19] >= mark
            evs = ",".join(by_mail.get(e, [])) or ("-- KHONG CO --" if trong
                                                   else "(gui truoc moc do)")
            print("      %-19s  %-34s  %-24s %-9s %s"
                  % (t[:19], e[:34], evs, "co" if e in click_e else "KHONG",
                     why.get(e, "")))

    # ⚠️⚠️ CHI XET THU GUI SAU MOC. Ban dau bo do ket toi ca 4 thu cua 23-30/08
    #    la "roi vao khoang toi", tuc doi mot he thong tra loi ve quang thoi gian
    #    no chua he quan sat. Mot cao buoc sai, va sai theo kieu lam mat long tin
    #    vao chinh bo do.
    holes = [e for _, e in trong_tam
             if not ({"DELIVERY", "BOUNCE", "REJECT"} & set(by_mail.get(e, [])))]
    if not live:
        print("  [..]   chua co su kien nao -> chua deploy, hoac chua gui thu nao sau deploy")
    elif not trong_tam:
        print("  [..]   chua co thu that nao gui sau moc do (%d thu deu truoc moc)"
              % truoc_moc)
    else:
        chk("khong con thu nao roi vao khoang toi", not holes,
            ("thieu su kien: " + ", ".join(holes)) if holes
            else "%d/%d thu sau moc deu co su kien" % (len(trong_tam), len(trong_tam)))

    print("\n[5] PHIEU  (chi tinh %d thu gui sau moc do; %d thu cu khong do duoc)"
          % (len(trong_tam), truoc_moc))
    print("      gui         %d" % len(trong_tam))
    print("      toi hom thu %s"
          % (len([e for _, e in trong_tam if "DELIVERY" in by_mail.get(e, [])]) if live
             else "chua do duoc"))
    print("      bam link    %d" % len([e for _, e in trong_tam if e in click_e]))

    print("\n===== %d OK · %d HONG =====" % (_n["ok"], _n["ng"]))
    sys.exit(1 if _n["ng"] else 0)


def send_test():
    """Gui MOT thu that qua configuration set, de chung minh duong su kien song."""
    print("\n[0] GUI THU THU NGHIEM QUA %s" % CONF_SET)
    content = json.dumps({"Simple": {
        "Subject": {"Data": "astroQ mail-event probe", "Charset": "UTF-8"},
        "Body": {"Text": {"Data": "probe " + str(int(time.time())), "Charset": "UTF-8"}}}})
    r = aws(["sesv2", "send-email",
             "--from-email-address", "no-reply@" + DOMAIN,
             "--destination", json.dumps({"ToAddresses": [SIM_OK]}),
             "--content", content,
             "--configuration-set-name", CONF_SET,
             "--email-tags", json.dumps([{"Name": "astroq-mail", "Value": "probe"}])])
    mid = (r or {}).get("MessageId", "")
    chk("SES nhan thu thu nghiem", bool(mid), mid)
    if mid:
        # ⚠️ Do that: su kien Send va Delivery cung ve trong ~1 giay, nhung Logs
        #    Insights can them chut nua de INDEX xong moi tim thay.
        print("      cho 45s de su kien di qua EventBridge va vao chi muc...")
        time.sleep(45)
    return mid


if __name__ == "__main__":
    main()
