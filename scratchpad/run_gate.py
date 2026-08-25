# -*- coding: utf-8 -*-
"""Chay TUAN TU mot danh sach bo kiem truoc khi push (quy tac 11 muc 6).

Chay TUAN TU chu khong song song: Chrome ham `setInterval` o tab khong co tieu
diem, nen chay chong nhau lam nhieu bo bao hong mot cach chap chon (quy tac 9).

Dung:  python scratchpad/run_gate.py <ten-bo> [<ten-bo> ...]
In ra mot dong moi bo: TEN | dat/hong | ma thoat | giay.

⚠️⚠️ BON NHOM TUYET DOI KHONG DUA VAO CONG PUSH — khong phai "cho nhanh", ma vi
   chung KHONG PHAI phep kiem, hoac vi chung DUNG VAO DU LIEU THAT:
     1. `test_*`, `e2e_certificate`, `e2e_char_login`, `probe_char_e2e`,
        `probe_visit_beacon` — can backend (AWS hoac `dotnet run`) va/hoac TAO
        TAI KHOAN FIREBASE + DONG DynamoDB THAT. Cong day du 25/08/2026 da de
        `e2e_certificate` lot vao: no chet o `goto` vi thieu may chu tinh cong
        8000, con luot chay lai (co may chu) thi tao roi tu don du lieu that.
        ⚠️ Mot bo cong PHAI khong duoc dung vao du lieu nguoi dung.
     2. `verify_*`, `perf_prod_return` — do tren BAN THAT, chay SAU khi push.
     3. `perf_ab`, `sync_font_preload`, `gen_*`, `split_*`, `make_*`, `stamp_*`,
        `bundle_*` — bo SINH: chung GHI FILE vao repo.
     4. `perf_*` (con lai), `measure_shell`, `gap_lv`, `probe_globe_daynight`,
        `probe_earth_flat`, `probe_flat_*`, `probe_field_*`, `probe_warp_*` — bo
        DO, khong co pass/fail; chung in ra so lieu roi thoi, nen `exit 1` cua
        chung khong noi len dieu gi ve san pham.
   ⚠️ Cac bo `pha_*` thi chay RIENG (chung sua file nguon roi khoi phuc); dong
      tong ket cua chung duoc doc theo mau "n/m loi co y bi bat" o duoi.
"""
import subprocess, sys, time, re, os, io

os.environ["PYTHONIOENCODING"] = "utf-8"
NUM = re.compile(r"(\d+)\s*(?:dat|đạt|PASS|pass)\D+?(\d+)\s*(?:hong|hỏng|FAIL|fail)")
# Bo LIET KE khong in "n dat / m hong" ma in mot con so PHAT HIEN. Hai mau
# duoi day cho con so do hien ra thay vi "?" — `probe_chip_label` in "TONG SO
# NHAN BI CAT/TRAN: n", `audit_taps` in "n nhom CAN SUA".
FOUND = [re.compile(r"TONG SO[^:]*:\s*(\d+)"),
         re.compile(r"===\s*(\d+)\s+nhom CAN SUA")]
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
    # Bo LIET KE: in mot con so PHAT HIEN thay vi "n dat / m hong".
    for rx in FOUND:
        m = rx.search(out)
        if m:
            return "-", m.group(1)
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
    # ⚠️⚠️ BO `pha_*` DO MOT THU KHAC HAN, VA DOC NHAM LA BAO OAN MOI LUOT.
    #   Mot bo pha hoai gay tung loi co y roi chay lai bo do; dong "n dat / m hong"
    #   CUOI cung la ket qua cua LUOT DOT BIEN, tuc `m > 0` la ket qua MONG MUON
    #   (loi co y da bi bat). Doc no nhu mot bo thuong thi `pha_sw` 3/3 van bi gan
    #   co `<<< XEM LAI`. Can cu dung: dong "n/m loi co y bi bat" + ma thoat.
    if os.path.basename(p).startswith("pha_"):
        m = re.search(r"(\d+)\s*/\s*(\d+)\s*loi co y bi bat", out)
        if m:
            a = "%s/%s bat" % (m.group(1), m.group(2))
            b = "0" if m.group(1) == m.group(2) else str(int(m.group(2)) - int(m.group(1)))
        elif r.returncode == 0:
            a, b = "sach(exit)", "0"
    # ⚠️⚠️ KHONG DOC RA SO MA MA THOAT = 0 THI COI LA SACH. `check_idents` va
    #   `e2e_tree_stamp` bieu dat ket qua bang MA THOAT chu khong bang mot dong
    #   dem — va chinh ghi chu tren dau ham `counts` da ghi 'Can cu duyet chinh
    #   la MA THOAT'. Truoc day chung bi gan co `<<< XEM LAI` o MOI luot chay,
    #   tuc cai cong tu day nguoi doc den cho bo qua no.
    #   ⚠️ Van in 'sach(exit)' chu khong in mot con so, de khong ai doc thanh
    #      mot con so THAT.
    if (a, b) == ("?", "?") and r.returncode == 0:
        a, b = "sach(exit)", "0"
    rows.append((name, a, b, r.returncode, dt))
    flag = "" if (r.returncode == 0 and b in ("0",)) else "   <<< XEM LAI"
    print("%-26s | %5s dat / %-4s hong | exit %-3s | %5.1fs%s"
          % (name, a, b, r.returncode, dt, flag), flush=True)
    if flag:
        # ⚠️ IN DONG `[HONG]` TRUOC. Truoc day cho nay chi in 12 dong CUOI, ma voi
        #    cac bo dung `http.server` thi 12 dong cuoi hay la traceback
        #    `ConnectionAbortedError` (tieng on vo hai) — no de het dong hong that,
        #    nen cong bao dong ma khong chan doan duoc gi.
        hong = [l for l in out.splitlines() if "[HONG]" in l]
        for ln in hong[:14]:
            print("      " + ln.strip()[:170], flush=True)
        if not hong:
            for ln in out.strip().splitlines()[-12:]:
                print("      " + ln[:170], flush=True)
        elif len(hong) > 14:
            print("      … con %d dong [HONG] nua" % (len(hong) - 14), flush=True)

bad = [r for r in rows if r[3] != 0 or r[2] not in ("0",)]
print()
print("=== %d bo chay, %d bo CAN XEM LAI ===" % (len(rows), len(bad)), flush=True)
sys.exit(1 if bad else 0)
