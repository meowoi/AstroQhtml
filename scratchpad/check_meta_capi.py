# -*- coding: utf-8 -*-
r"""check_meta_capi.py — CANH DUONG CONVERSIONS API (Meta) khong bi noi rong am tham.

    python scratchpad/check_meta_capi.py

⚠️⚠️ VI SAO PHAI CO BO NAY. Duong nay (26/08/2026) co bon bat bien, va **ca bon deu
   hong EM**: noi ra mot cai thi khong co gi bao loi, khong test nao do, trang van
   chay dung, chi co dieu du an vua lang le pha mot loi hua cua chinh no.
     ① CHI gui `fbc`. Them `client_ip_address` hay `client_user_agent` la nang duoc
        "ti le khop" trong bang cua Meta — tuc co dong luc THAT de them — nhung do
        dung la thu `POST /visit` da co y tu choi luu.
     ② Cong tac TAT la `META_DATASET_ID` rong. Con `META_SECRET_ID` **khong duoc**
        rong: quyen IAM dung ARN tu bien do, de rong thi thanh `:secret:-*`, tuc
        Lambda doc duoc MOI secret trong tai khoan.
     ③ `fbc` dung MILLI-giay con `event_time` dung GIAY. Viet lan thi Meta van tra
        200 roi am tham khong khop duoc luot bam nao.
     ④ KHONG BAO GIO log ca duong URL — no mang access token.

⚠️ Bo nay soi VAN BAN, khong goi mang. No khong the chung minh Meta nhan duoc su
   kien; viec do phai lam bang "Test Events" trong Events Manager voi token that.
   Hai thu bo cho nhau: bo nay canh cai KHONG DUOC DOI, con Test Events canh cai
   CO CHAY.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SV = os.path.join(os.path.dirname(ROOT), "AstroqSV")

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
    else:
        bad_n += 1
        print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))


def rd(p):
    return io.open(p, encoding="utf-8").read()


# ⚠️⚠️ BO CHU THICH TRUOC KHI KHANG DINH "KHONG CO X". Ba phep kiem cua bo nay tung
#    BAO HONG OAN vi chung grep van ban tho va khop vao chinh CHU THICH cua minh —
#    chu thich noi "dung dung `client_ip_address`" thi phep kiem doc ra la "co dung".
#    `check_pages.py` da co dung ho ham nay va da tra gia mot lan cho no. Ba dieu:
#      · CHI dung cho phep kiem PHU DINH ("khong duoc co"); phep kiem KHANG DINH
#        ("phai co") thi doc van ban tho, vi noi dung can tim co the nam trong mot
#        chuoi ma ham nay khong nen dung tay vao;
#      · YAML dung `#`, C#/JS dung `//` va `/* */` — ba kieu khac nhau;
#      · ham nay THO: no khong hieu `//` nam trong chuoi. Cho muc dich "khong duoc
#        co ten truong X" thi tho la du, va tho theo huong AN TOAN (bo nhieu hon).
def no_cmt(src, kind):
    if kind == "yaml":
        return "\n".join(re.sub(r"#.*$", "", l) for l in src.splitlines())
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)      # /* ... */
    return "\n".join(re.sub(r"//.*$", "", l) for l in src.splitlines())


CAPI = rd(os.path.join(SV, "src/AstroqSV.Api/Services/MetaCapi.cs"))
TPL = rd(os.path.join(SV, "template.yaml"))
AUTH = rd(os.path.join(SV, "src/AstroqSV.Api/Endpoints/AuthEndpoints.cs"))
VISIT = rd(os.path.join(SV, "src/AstroqSV.Api/Endpoints/VisitEndpoints.cs"))
UTM = rd(os.path.join(ROOT, "js/utm.js"))
FBA = rd(os.path.join(ROOT, "js/firebase-auth.js"))

# Ban da bo chu thich — CHI dung cho phep kiem phu dinh (xem `no_cmt`).
CAPI_NC = no_cmt(CAPI, "cs")
TPL_NC = no_cmt(TPL, "yaml")
AUTH_NC = no_cmt(AUTH, "cs")
VISIT_NC = no_cmt(VISIT, "cs")
UTM_NC = no_cmt(UTM, "js")

# ── ① Chi gui `fbc` ─────────────────────────────────────────────────────────
print("=== [1] user_data CHI duoc mang `fbc` ===")
_ud = re.search(r"user_data\s*=\s*new\s*\{([^}]*)\}", CAPI)
check("[1] doc duoc khoi `user_data`", _ud is not None,
      "" if _ud else "mau khong khop — SUA BIEU THUC, dung bo qua")
if _ud:
    fields = [f.strip() for f in _ud.group(1).split(",") if f.strip()]
    check("[1] user_data co DUNG 1 truong, va la `fbc`", fields == ["fbc"], str(fields))

# ⚠️ Quet CA FILE, khong chi khoi user_data: mot lan goi `_ = ctx.Connection.RemoteIpAddress`
#    o cho khac roi nhet vao payload cung la vi pham, ma bieu thuc tren khong thay.
BANNED = ["client_ip_address", "client_user_agent", "RemoteIpAddress", "User-Agent",
          "UserAgent", '"em"', '"ph"', "external_id", "advanced_matching"]
for b in BANNED:
    check("[1] KHONG co dau vet `%s`" % b, b not in CAPI_NC)

# ── ② Cong tac tat, va cai bay IAM ─────────────────────────────────────────
print("\n=== [2] Cong tac TAT + quyen IAM ===")
check("[2] IsConfigured doi CA HAI bien",
      re.search(r"IsConfigured\s*=>\s*DatasetId is not null && SecretId is not null",
                CAPI) is not None)
check("[2] khong du cau hinh thi KHONG gui",
      "if (!IsConfigured || string.IsNullOrWhiteSpace(fbc)) return false;" in CAPI)

_ds = re.search(r"MetaDatasetId:\s*\n\s*Type:\s*String\s*\n\s*Default:\s*('' |''|\"\")",
                TPL)
check("[2] template: MetaDatasetId mac dinh RONG (= tat han)", _ds is not None,
      "" if _ds else "mac dinh phai la '' — do la cong tac tat")

_sec = re.search(r"MetaSecretId:\s*\n\s*Type:\s*String\s*\n\s*Default:\s*(\S+)", TPL)
_secdef = _sec.group(1) if _sec else "?"
check("[2]⚠️ template: MetaSecretId mac dinh KHONG duoc rong (bay IAM)",
      _sec is not None and _secdef not in ("''", '""'), "dang la %r" % _secdef)
check("[2] quyen IAM ghim dung MOT secret cua Meta",
      "${MetaSecretId}-*" in TPL)
# ⚠️ SOI DUNG CAC DONG `SecretArn:`, khong soi ca file. Ban dau phep kiem nay quet
#    toan bo `template.yaml` va khop vao chinh khoi `Description:` dang GIAI THICH cai
#    bay (`... ARN thanh ':secret:-*' ...`) — tuc no bao hong vi tai lieu NOI DUNG.
#    `no_cmt` khong cuu duoc o day: do la NOI DUNG cua YAML, khong phai chu thich `#`.
_arns = [l.strip() for l in TPL.splitlines() if "SecretArn:" in l]
check("[2] co it nhat 2 dong SecretArn (Firebase + Meta)", len(_arns) >= 2,
      "%d dong" % len(_arns))
check("[2] khong dong SecretArn nao mo ra MOI secret",
      not any(":secret:-*" in a or ":secret:*" in a for a in _arns),
      str([a for a in _arns if ":secret:-*" in a or ":secret:*" in a]))

# ── ③ Don vi thoi gian ─────────────────────────────────────────────────────
print("\n=== [3] fbc dung MILLI, event_time dung GIAY ===")
check("[3] fbc lay ToUnixTimeMilliseconds", "ToUnixTimeMilliseconds()" in CAPI)
check("[3] event_time lay ToUnixTimeSeconds",
      re.search(r"event_time\s*=\s*DateTimeOffset\.UtcNow\.ToUnixTimeSeconds\(\)",
                CAPI) is not None)
check("[3] khuon fbc la `fb.1.{ms}.{fbclid}`", 'return $"fb.1.{ms}.{fbclid}";' in CAPI)

# ── ④ Khong lo token ra log ────────────────────────────────────────────────
print("\n=== [4] Khong lo access token ===")
_logs = re.findall(r"log\.Log\w+\(([^;]*)\);", CAPI, re.S)
check("[4] khong co lenh log nao mang bien `url`",
      not any(re.search(r"\burl\b", l) for l in _logs),
      str([l[:60] for l in _logs if re.search(r"\burl\b", l)]))
check("[4] token duoc escape khi ghep vao duong",
      "Uri.EscapeDataString(token)" in CAPI)

# ── ⑤ Moc dung cho, va `/visit` KHONG bi keo vao ───────────────────────────
print("\n=== [5] Moc o dung cho ===")
check("[5] goi SAU khi tai khoan da tao (trong nhanh activate)",
      re.search(r"await db\.CreateUserAsync\([^;]*\);(.|\n)*?"
                r"await capi\.TrackRegistrationAsync\(p\.Fbc, home\);", AUTH) is not None)
# ⚠️ Dem LOI GOI THAT (`await capi.`), khong dem moi lan ten ham xuat hien: chu
#    thich cung nhac ten no, va ban dau phep kiem nay dem ca chu thich roi bao oan.
_calls = AUTH_NC.count("capi.TrackRegistrationAsync")
check("[5] KHONG goi tu /auth/register (do chi la gui thu, chua co tai khoan)",
      _calls == 1, "%d loi goi that" % _calls)
# ⚠️ Loi hua cua `POST /visit` phai con nguyen van.
check("[5] `/visit` KHONG mang fbclid/fbc", "fbc" not in VISIT_NC.lower())
check("[5] `/visit` van giu loi hua 'khong luu gi ve nguoi ghe'",
      "KHÔNG LƯU GÌ VỀ NGƯỜI GHÉ" in VISIT)

# ── ⑥ Client: giu fbclid o CA HAI nhanh, va khong dung khuon o client ──────
print("\n=== [6] Client ===")
check("[6] utm.js giu `fbclid` tho", "fbclid: fbclid," in UTM)
check("[6] giu o CA HAI nhanh (utm_source VA luoi do)",
      UTM.count("fbclid: fbclid,") == 2, "%d cho" % UTM.count("fbclid: fbclid,"))
check("[6] lo ra `click()` tra tho", re.search(r"click:\s*function\s*\(\)", UTM) is not None)
# ⚠️ Client KHONG duoc dung khuon `fb.1.` — luat do thuoc server.
check("[6]⚠️ client KHONG dung khuon `fb.1.`", "fb.1." not in UTM_NC)
check("[6] luc dang ky co gui fbclid + fbclidAt",
      "fbclid: click ? click.fbclid : undefined" in FBA
      and "fbclidAt: click ? click.at : undefined" in FBA)

print("\n=== KET QUA: %d dat / %d hong ===" % (ok_n, bad_n))
sys.exit(0 if bad_n == 0 else 1)
