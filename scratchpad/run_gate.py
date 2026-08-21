# -*- coding: utf-8 -*-
"""Chay TUAN TU mot danh sach bo kiem truoc khi push (quy tac 11 muc 6).

Chay TUAN TU chu khong song song: Chrome ham `setInterval` o tab khong co tieu
diem, nen chay chong nhau lam nhieu bo bao hong mot cach chap chon (quy tac 9).

Dung:  python scratchpad/run_gate.py <ten-bo> [<ten-bo> ...]
In ra mot dong moi bo: TEN | dat/hong | ma thoat | giay.
"""
import subprocess, sys, time, re, os, io

os.environ["PYTHONIOENCODING"] = "utf-8"
NUM = re.compile(r"(\d+)\s*(?:dat|đạt|PASS|pass)\D+?(\d+)\s*(?:hong|hỏng|FAIL|fail)")
ALT = re.compile(r"(?:KET QUA|ket qua|KẲT QUẢ|kết quả)[^0-9]*(\d+)[^0-9]+?(\d+)")

# CANH BAO: moi bo do in ket qua mot kieu. Ban dau cua ham nay do "n dat / m hong"
#   tren CA output, nen no bat nham mot cum chu trong than log: shoot_dodge KET
#   THUC bang "TAT CA KIEM TRA DAT" + "0 loi console" ma bi bao la "6 dat / 1
#   hong". Mot BO CHAY hay bao oan thi cung vo dung y nhu mot phep kiem hay bao
#   oan — nguoi ta se bo qua no. Nay: chi doc dong TONG KET (dong CUOI khop mau),
#   va coi "TAT CA ... DAT" la sach. Can cu duyet chinh la MA THOAT.
def counts(out):
    # ⚠⚠ DAU HIEU "TAT CA ... DAT" PHAI XET TRUOC MOI THU.
    #   `shoot_dodge` va `shoot_defender` khong in dong "n dat / m hong":
    #   chung in nhan PASS/FAIL tren TUNG dong roi ket bang
    #   "=== TAT CA KIEM TRA DAT ===". Ban 20/08 da sua ham nay nhung de
    #   nhanh do XUONG CUOI, nen no roi vao nhanh dem `findall("FAIL")` va
    #   doc ra "214 dat / 174 hong" cho mot bo DAT (exit 0) — chu "FAIL"
    #   nam trong chinh cac nhan in ra. Mot BO CHAY bao oan thi cung vo dung
    #   y nhu mot phep kiem bao oan: nguoi ta se bo qua no.
    if re.search(r"TAT CA[^0-9]*DAT", out):
        n_fail = len(re.findall(r"^\s*FAIL\b", out, re.M))
        if n_fail == 0:
            n_ok = len(re.findall(r"^\s*PASS\b", out, re.M))
            return (str(n_ok) if n_ok else "sach"), "0"
    lines = out.strip().splitlines()
    for ln in reversed(lines[-40:]):
        m = NUM.search(ln) or ALT.search(ln)
        if m:
            return m.group(1), m.group(2)
    if re.search(r"TAT CA[^0-9]*DAT", out):
        ok = len(re.findall(r"PASS|\[OK\]", out))
        return (str(ok) if ok else "sach"), "0"
    ok = len(re.findall(r"\[OK\]|PASS", out))
    bad = len(re.findall(r"\[HONG\]|FAIL", out))
    if ok or bad:
        return str(ok), str(bad)
    return "?", "?"

rows = []
for name in sys.argv[1:]:
    p = "scratchpad/%s.py" % name
    if not os.path.exists(p):
        print("%-26s | THIEU FILE" % name, flush=True)
        rows.append((name, "?", "?", -1, 0.0))
        continue
    t0 = time.time()
    r = subprocess.run([sys.executable, "-u", p], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    dt = time.time() - t0
    out = (r.stdout or "") + (r.stderr or "")
    a, b = counts(out)
    rows.append((name, a, b, r.returncode, dt))
    flag = "" if (r.returncode == 0 and b in ("0",)) else "   <<< XEM LAI"
    print("%-26s | %5s dat / %-4s hong | exit %-3s | %5.1fs%s"
          % (name, a, b, r.returncode, dt, flag), flush=True)
    if flag:
        tail = out.strip().splitlines()[-12:]
        for ln in tail:
            print("      " + ln[:170], flush=True)

bad = [r for r in rows if r[3] != 0 or r[2] not in ("0",)]
print()
print("=== %d bo chay, %d bo CAN XEM LAI ===" % (len(rows), len(bad)), flush=True)
sys.exit(1 if bad else 0)
