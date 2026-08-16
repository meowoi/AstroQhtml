# -*- coding: utf-8 -*-
"""
smoke_vault.py — soi specimen-vault.html bằng Chromium thật (Playwright).

    python scratchpad/smoke_vault.py

Tự bật `python -m http.server` trong AstroQhtml/ rồi mở trang.

ĐO TRÊN TRANG, KHÔNG ĐỌC CODE. Trọng tâm:
  1. Danh mục ở client (js/specimens.js) KHỚP danh mục ở server (Services/Specimens.cs)
     — đọc thẳng file .cs, không gieo tay, nên client/server lệch là bắt được.
  2. Chưa đăng nhập → hiện dải nhắc, MỌI khoang đều KHOÁ, KHÔNG bịa số nào.
  3. Câu nhắc mở khoá không được hứa thứ không tồn tại ("Mission 02"…).
  4. Thanh tiến độ phải có CHIỀU CAO THẬT (bẫy <span> inline đã gặp ở achievements.css).
  5. Bàn điều khiển: đặt/lấy đúng, đầy 3 chỗ thì chặn, server từ chối thì trả lại trạng thái cũ.
"""
import io
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CS = ROOT.parent / "AstroqSV" / "src" / "AstroqSV.Api" / "Services" / "Specimens.cs"
PORT = 8123
URL = f"http://127.0.0.1:{PORT}/specimen-vault.html"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def server_catalog():
    """Đọc danh mục mẫu vật THẲNG TỪ Services/Specimens.cs (không gieo tay)."""
    src = io.open(CS, encoding="utf-8").read()
    body = src.split("public static readonly Specimen[] All", 1)[1].split("];", 1)[0]
    rows = re.findall(
        r'new\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*\)',
        body)
    return [{"id": a, "category": b, "rarity": c, "origin": d, "metric": e, "goal": int(f)}
            for a, b, c, d, e, f in rows]


CAT = server_catalog()
# SỐ MẪU suy ra từ chính Services/Specimens.cs — KHÔNG gán cứng. Trước 29/07/2026
# con số 20 nằm rải rác 8 chỗ trong file này, nên thêm một mẫu vật ở server là bộ
# test báo hỏng 8 lần trong khi trang vẫn đúng.
N = len(CAT)
UNLOCK_N = 8            # số mẫu cho "đã thu thập" trong bản giả


def fake_payload(unlocked_ids, desk):
    items = []
    for s in CAT:
        on = s["id"] in unlocked_ids
        items.append(dict(s, current=s["goal"] if on else 0,
                          unlocked=on, equipped=s["id"] in {d["id"] for d in desk}))
    rare_total = sum(1 for s in CAT if s["rarity"] in ("rare", "legendary"))
    rare_got = sum(1 for s in CAT if s["rarity"] in ("rare", "legendary") and s["id"] in unlocked_ids)
    return {
        "specimens": {
            "summary": {"collected": len(unlocked_ids), "total": len(CAT),
                        "rare": rare_got, "rareTotal": rare_total, "deskSlots": 3},
            # `desk` = dang CU (id tran) van tra ve cho client con trong cache;
            # `deskHooks` la dang THAT tu 16/08/2026. Ban gia phai tra CA HAI de
            # no giong het server that — tra thieu la do mot thu khong ton tai.
            "desk": [d["id"] for d in desk],
            "deskHooks": [dict(d) for d in desk],
            "specimens": items,
        },
        "wallet": {"meteors": 42},
    }


# ⚠️ Bản giả PHẢI cài bằng Object.defineProperty có setter nuốt lời gán: module ES
# js/firebase-auth.js chạy SAU script cổ điển và sẽ ghi đè window.AstroQAuth
# (bài học đã ghi trong CLAUDE.md ngày 29/07).
STUB = """
(payload) => {
  window.__deskCalls = [];
  window.__rejectDesk = false;
  const stub = {
    postProgress: async () => ({ ok: true, data: {} }),
    getWallet:    async () => ({ ok: true, data: { meteors: 42 } }),
    getSpecimens: async () => ({ ok: true, data: window.__payload }),
    setSpecimenDesk: async (items) => {
      // Luu nguyen ca {hook,id} — rut ra mang id la bo mat chinh thu dang do.
      window.__deskCalls.push(items.map(x => ({ hook: x.hook, id: x.id })));
      if (window.__rejectDesk) return { ok: false, reason: "http", code: "bad-specimen" };
      window.__payload.specimens.desk = items.map(x => x.id);
      window.__payload.specimens.deskHooks = items.map(x => ({ hook: x.hook, id: x.id }));
      return { ok: true, data: { desk: items.map(x => x.id),
                                 deskHooks: items.map(x => ({ hook: x.hook, id: x.id })),
                                 slots: 3 } };
    }
  };
  window.__payload = payload;
  Object.defineProperty(window, "AstroQAuth", {
    configurable: true, get: () => stub, set: () => {}
  });
}
"""


def main():
    from playwright.sync_api import sync_playwright

    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)],
                           cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.4)
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            errs = []

            def open_page(width=1440, height=900, stub=None):
                # locale vi-VN BẮT BUỘC: AstroQ.getLang() lùi về ngôn ngữ trình duyệt khi
                # localStorage rỗng, mà Chromium mặc định en-US → trang ra tiếng Anh và
                # mọi phép so với chữ Việt báo hỏng oan.
                pg = br.new_page(viewport={"width": width, "height": height}, locale="vi-VN")
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                if stub is not None:
                    pg.add_init_script("(" + STUB + ")(" + repr(stub).replace("'", '"')
                                       .replace("True", "true").replace("False", "false") + ")")
                pg.goto(URL, wait_until="networkidle")
                return pg

            print(f"=== specimen-vault.html @ {URL} ===")
            print(f"\n[0] Danh muc server (Services/Specimens.cs): {len(CAT)} mau")
            check("Doc duoc danh muc tu file .cs", len(CAT) >= 20, f"{len(CAT)} dong")

            # ---------- [1] Chưa đăng nhập ----------
            print("\n[1] Chua dang nhap — khong bia so nao")
            pg = br.new_page(viewport={"width": 1440, "height": 900}, locale="vi-VN")
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(URL, wait_until="networkidle")
            pg.wait_for_timeout(3200)          # chờ waitAuth(2500) hết hạn

            check("Dai nhac hien ra", pg.is_visible("#offline.show"))
            msg = pg.inner_text("#offline-msg")
            check("Dung cau 'chua dang nhap'", "đăng nhập" in msg.lower(), msg[:60])
            check("Tien do hien '—/n' chu khong bia 0",
                  pg.inner_text("#prog-v").startswith(f"—/{N}"), pg.inner_text("#prog-v"))
            check("Mau hiem hien dau '—' chu KHONG bia 0/0",
                  pg.inner_text("#rare-v") == "—", pg.inner_text("#rare-v"))
            check("Ban dieu khien '—/3'", pg.inner_text("#desk-v") == "—/3", pg.inner_text("#desk-v"))
            n_pods = pg.locator(".pod").count()
            check("Van du khoang (khong de trang)", n_pods == N, f"{n_pods}/{N} khoang")
            check("Moi khoang deu KHOA", pg.locator(".pod.off").count() == N,
                  f"{pg.locator('.pod.off').count()}/{N} khoa")
            check("Khoang khoa khong bam duoc", pg.locator(".pod[disabled]").count() == N)
            check("Khoang khoa hien o khoa", pg.locator(".pod .lock").count() == N)
            check("Ten mau vat bi che (???)",
                  pg.locator(".pod .nm").first.inner_text().strip() == "???")

            # ---------- [2] Câu nhắc mở khoá ----------
            print("\n[2] Cau nhac mo khoa")
            hints = [pg.locator(".pod .why").nth(i).inner_text() for i in range(n_pods)]
            check("Khoang nao cung co cau nhac", all(h.strip() for h in hints))
            check("KHONG hua thu khong ton tai ('Mission')",
                  not any(re.search(r"mission|nhiệm vụ 0", h, re.I) for h in hints))
            check("Khong con placeholder chua dich",
                  not any(("{n}" in h or "{name}" in h or h.strip() == "🔒") for h in hints))
            # metric/goal là LUẬT, nằm ở server — chưa đăng nhập thì client không có.
            # Nên đúng đắn là hiện MỘT câu chung, chứ không bịa điều kiện cụ thể.
            check("Chua co server thi KHONG bia dieu kien cu the (chi 1 cau chung)",
                  len({h.strip() for h in hints}) == 1, str({h.strip() for h in hints})[:80])

            # ---------- [3] Bẫy <span> inline: thanh tiến độ phải có chiều cao ----------
            print("\n[3] Thanh tien do phai co CHIEU CAO THAT")
            h_bar = pg.eval_on_selector("#pbar", "e => e.getBoundingClientRect().height")
            h_fill = pg.eval_on_selector("#pfill", "e => e.getBoundingClientRect().height")
            check("#pbar cao > 0", h_bar >= 8, f"{h_bar}px")
            check("#pfill cao > 0", h_fill >= 8, f"{h_fill}px")
            hs = pg.eval_on_selector_all(".pbar, .slot, .pod .glass",
                                         "els => els.map(e => e.getBoundingClientRect().height)")
            check("Khong phan tu nao cao 0px", all(v > 0 for v in hs), f"min={min(hs):.1f}px")
            pg.close()

            # ---------- [4] Đã đăng nhập (bản giả) ----------
            print("\n[4] Da dang nhap — 8 mau da thu thap")
            unlocked = [s["id"] for s in CAT][:UNLOCK_N]
            pg = open_page(stub=fake_payload(unlocked, []))
            pg.wait_for_selector(".pod.on", timeout=8000)
            check("Dai nhac AN khi goi duoc server", not pg.is_visible("#offline.show"))
            got = pg.locator(".pod.on").count()
            check(f"Dung {UNLOCK_N} khoang da mo", got == UNLOCK_N, f"{got}")
            check("Con lai van khoa", pg.locator(".pod.off").count() == N - UNLOCK_N)
            check("Tien do khop bo dem", pg.inner_text("#prog-v").startswith(f"{UNLOCK_N}/{N}"),
                  pg.inner_text("#prog-v"))
            pct = pg.eval_on_selector("#pfill", "e => e.style.width")
            check("Be rong thanh tien do dung %", pct == f"{round(UNLOCK_N/N*100)}%", pct)
            check("So du vi lay tu server (42)", pg.inner_text("#bal") == "42",
                  pg.inner_text("#bal"))
            hints4 = [pg.locator(".pod.off .why").nth(i).inner_text()
                      for i in range(pg.locator(".pod.off .why").count())]
            check("Co server thi cau nhac ghi RO dieu kien tung mau",
                  len({h.strip() for h in hints4}) >= 5,
                  f"{len(set(hints4))} cau khac nhau")
            # KHÔNG chốt cứng "Sao Hoả": mars-red-ice nằm trong nhóm ĐÃ MỞ của bản giả
            # nên câu nhắc của nó không có trong danh sách khoang khoá.
            PL = ("Trái Đất", "Sao Thuỷ", "Sao Kim", "Sao Hoả", "Sao Mộc",
                  "Sao Thổ", "Sao Thiên Vương", "Sao Hải Vương")
            hp = [h for h in hints4 if "Bay tới" in h and any(p in h for p in PL)]
            check("Cau nhac ghe hanh tinh dich dung ten hanh tinh", len(hp) > 0,
                  " ".join(hp[0].split()) if hp else "")
            check("Cau nhac ghep chom sao dich dung ten chom sao",
                  any("Lạp Hộ" in h for h in hints4), [h for h in hints4 if "Lạp" in h][:1])
            check("Cau nhac co so muc tieu that tu server (300 diem)",
                  any("300" in h for h in hints4), [h for h in hints4 if "300" in h][:1])
            check("Khong cau nhac nao con placeholder",
                  not any(("{n}" in h or "{name}" in h) for h in hints4))
            check("Khoang da mo len TRUOC khoang khoa",
                  pg.eval_on_selector_all(".pod", "els => els.slice(0, %d)"
                                          ".every(e => e.classList.contains('on'))" % UNLOCK_N))

            # Lọc theo nhóm
            print("\n[5] Loc theo nhom")
            tabs = pg.locator("#f-cat button").count()
            check("5 tab (Tat ca + 4 nhom)", tabs == 5, f"{tabs} tab")
            for i, key in enumerate(["hydro", "bio", "litho", "cosmic"], start=1):
                pg.locator("#f-cat button").nth(i).click()
                pg.wait_for_timeout(120)
                want = sum(1 for s in CAT if s["category"] == key)
                have = pg.locator(".pod").count()
                check(f"Nhom {key}: {want} khoang", have == want, f"hien {have}")
            pg.locator("#f-cat button").nth(0).click()
            pg.wait_for_timeout(120)
            check("Ve 'Tat ca' thi lai du het", pg.locator(".pod").count() == N)

            # ---------- [6] Màn soi chi tiết ----------
            print("\n[6] Man soi chi tiet (kinh hien vi)")
            pg.locator(".pod.on").first.click()
            pg.wait_for_selector("#insp.show", timeout=5000)
            check("Modal mo ra", pg.is_visible("#insp.show"))
            check("Co nhan MICROSCOPE SCANNER 10X", "10X" in pg.inner_text(".insp-top .tag"),
                  pg.inner_text(".insp-top .tag"))
            check("Co ten + phan loai khoa hoc",
                  bool(pg.inner_text("#insp-name").strip()) and
                  bool(pg.inner_text(".insp-cls").strip()), pg.inner_text(".insp-cls")[:40])
            check("Co loi linh vat (Comet/Byte)",
                  any(w in pg.inner_text(".box.say") for w in ("COMET", "BYTE")),
                  pg.inner_text(".box.say .lbl"))
            check("Co fun fact", len(pg.inner_text(".box.fact p:not(.lbl)").strip()) > 40)
            href = pg.get_attribute(".box.fact .src", "href")
            check("Link nguon la NASA/NOAA + mo tab moi",
                  href and ("nasa.gov" in href or "noaa.gov" in href)
                  and pg.get_attribute(".box.fact .src", "rel") == "noopener noreferrer", href)
            check("2 nut hanh dong", pg.is_visible("#zoom") and pg.is_visible("#desk-btn"))

            sp0 = pg.eval_on_selector(".scope .sp", "e => parseFloat(getComputedStyle(e).fontSize)")
            pg.click("#zoom")
            pg.wait_for_timeout(600)
            sp1 = pg.eval_on_selector(".scope .sp", "e => parseFloat(getComputedStyle(e).fontSize)")
            check("Zoom lam mau vat TO THAT len", sp1 > sp0 * 1.4, f"{sp0:.0f}px -> {sp1:.0f}px")
            check("Nhan doi thanh 40X", "40X" in pg.inner_text(".insp-top .tag"),
                  pg.inner_text(".insp-top .tag"))
            pg.click("#zoom")
            pg.wait_for_timeout(500)
            check("Bam lan nua thu nho lai",
                  abs(pg.eval_on_selector(".scope .sp",
                      "e => parseFloat(getComputedStyle(e).fontSize)") - sp0) < 1)

            # ---------- [7] Treo len vach: TRE tu chon moc ----------
            print("\n[7] Treo len vach — tre TU CHON moc")
            id0 = pg.locator(".pod.on").first.get_attribute("data-id")
            pg.click("#desk-btn")
            pg.wait_for_timeout(400)
            # Bam "treo len" ma LUU NGAY la dung thu tinh nang nay bo di. Kiem CA HAI
            # ve: bang chon hien ra VA chua co loi goi nao len server.
            check("Bam 'treo len' KHONG luu ngay, ma mo bang chon moc",
                  pg.locator(".hk-grid").count() == 1
                  and pg.evaluate("() => window.__deskCalls.length") == 0,
                  str(pg.evaluate("() => window.__deskCalls")))
            check("Bang chon du 10 moc, chia hai vach",
                  pg.locator(".hk").count() == 10 and pg.locator(".hk-wall").count() == 2,
                  "%d moc / %d vach" % (pg.locator(".hk").count(),
                                        pg.locator(".hk-wall").count()))
            check("Moi moc >=48px (WCAG 2.5.5 + bien an toan)",
                  pg.eval_on_selector_all(
                      ".hk", "es => es.every(e => e.getBoundingClientRect().height >= 47.5)"))
            pg.click('.hk[data-hook="R3"]')
            pg.wait_for_timeout(700)
            calls = pg.evaluate("() => window.__deskCalls")
            check("Goi PUT dung 1 lan, KEM moc tre da chon",
                  calls == [[{"hook": "R3", "id": id0}]], str(calls))
            check("Ban dieu khien len 1/3", pg.inner_text("#desk-v") == "1/3",
                  pg.inner_text("#desk-v"))
            check("Ban do vach: dung 1 moc co mau vat", pg.locator(".slot.full").count() == 1)
            # Ban do phai ve DU 10 o. Chi ve cho da treo thi no khong tra loi duoc cau
            # "con treo duoc o dau", ma do la ca ly do bang nay ton tai.
            check("Ban do vach ve du 10 moc / 2 vach",
                  pg.locator("#shelf .slot").count() == 10
                  and pg.locator("#shelf .wm-wall").count() == 2,
                  "%d o / %d vach" % (pg.locator("#shelf .slot").count(),
                                      pg.locator("#shelf .wm-wall").count()))
            full_at = ("w => [...w.querySelectorAll('.slot')]"
                       ".findIndex(s => s.classList.contains('full'))")
            check("Mau vat nam o VACH PHAI, dung o thu 3",
                  pg.eval_on_selector("#shelf .wm-wall:nth-child(2)", full_at) == 2,
                  str(pg.eval_on_selector("#shelf .wm-wall:nth-child(2)", full_at)))
            check("Nut doi thanh 'lay xuong'",
                  pg.get_attribute("#desk-btn", "aria-pressed") == "true")
            check("Toast bao da treo len", pg.is_visible("#toast.show"))

            print("\n[7b] Doi moc")
            check("Da treo roi thi co nut 'doi moc'", pg.is_visible("#move-btn"))
            pg.click("#move-btn")
            pg.wait_for_timeout(350)
            check("Moc dang treo duoc danh dau la CUA MINH",
                  pg.locator(".hk.mine").count() == 1
                  and pg.get_attribute('.hk[data-hook="R3"]', "aria-pressed") == "true",
                  str(pg.locator(".hk.mine").count()))
            pg.click('.hk[data-hook="L2"]')
            pg.wait_for_timeout(700)
            calls = pg.evaluate("() => window.__deskCalls")
            check("Doi moc -> PUT lan 2 voi moc MOI",
                  len(calls) == 2 and calls[1] == [{"hook": "L2", "id": id0}], str(calls[-1:]))
            check("Van la 1/3 (doi cho chu khong phai them mau)",
                  pg.inner_text("#desk-v") == "1/3", pg.inner_text("#desk-v"))
            check("Ban do: nay o VACH TRAI, o thu 2",
                  pg.eval_on_selector("#shelf .wm-wall:nth-child(1)", full_at) == 1,
                  str(pg.eval_on_selector("#shelf .wm-wall:nth-child(1)", full_at)))
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(350)
            check("Escape dong modal", not pg.is_visible("#insp.show"))
            check("The khoang co huy hieu 'dang trung'", pg.locator(".pod .eq").count() == 1)
            check("Tieu diem tra ve dung khoang vua xem",
                  pg.evaluate("() => document.activeElement.classList.contains('pod')"))

            # đầy 3 chỗ
            for i, hk in ((1, "L5"), (2, "R1")):
                pg.locator(".pod.on").nth(i).click()
                pg.wait_for_selector("#insp.show")
                pg.click("#desk-btn")
                pg.wait_for_timeout(300)
                # Moc dang co mau KHAC phai bi chan o CHINH CAI NUT, khong chan bang
                # mot cau `if` — chan bang `if` thi nut van nhan tieu diem ban phim va
                # van bao voi trinh doc man hinh rang no bam duoc.
                check("Moc da co mau khac thi khong bam duoc (buoc %s)" % hk,
                      pg.get_attribute('.hk[data-hook="L2"]', "disabled") is not None
                      and "busy" in (pg.get_attribute('.hk[data-hook="L2"]', "class") or ""),
                      str(pg.get_attribute('.hk[data-hook="L2"]', "class")))
                pg.click('.hk[data-hook="%s"]' % hk)
                pg.wait_for_timeout(600)
                pg.keyboard.press("Escape")
                pg.wait_for_timeout(300)
            check("Day 3 cho", pg.inner_text("#desk-v") == "3/3", pg.inner_text("#desk-v"))
            pg.locator(".pod.on").nth(3).click()
            pg.wait_for_selector("#insp.show")
            check("Ban day -> nut bi vo hieu", pg.get_attribute("#desk-btn", "disabled") is not None)
            check("Ban day -> co cau giai thich", pg.is_visible(".insp-note"))
            note = pg.inner_text(".insp-note").lower()
            check("KHONG im lang: cau noi ro het cho VA phai lam gi",
                  ("đầy" in note or "đủ" in note) and "lấy" in note, note)
            check("Cau do neu dung so cho lay tu server (khong gan cung)",
                  "3" in note, note)
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(300)

            # server từ chối → trả lại trạng thái cũ
            print("\n[8] Server tu choi -> tra lai trang thai cu, khong im lang")
            before = pg.inner_text("#desk-v")
            pg.evaluate("() => { window.__rejectDesk = true; }")
            pg.locator(".pod .eq").first.click()          # mở một mẫu đang trên bàn
            pg.wait_for_selector("#insp.show")
            pg.click("#desk-btn")
            pg.wait_for_timeout(800)
            check("Bo dem ban ve dung so cu", pg.inner_text("#desk-v") == before,
                  f"{before} -> {pg.inner_text('#desk-v')}")
            check("Co toast bao loi", pg.is_visible("#toast.show"))
            check("Nut ve dung trang thai 'dang tren ban'",
                  pg.get_attribute("#desk-btn", "aria-pressed") == "true")
            pg.keyboard.press("Escape")
            pg.evaluate("() => { window.__rejectDesk = false; }")

            # ---------- [9] Tiếng Anh ----------
            print("\n[9] Tieng Anh")
            pg.click('.lang-switch button[data-lang="en"]')
            pg.wait_for_timeout(400)
            check("Tieu de trang doi sang EN", "Specimen Vault" in pg.title(), pg.title())
            check("Hero doi sang EN", "museum" in pg.inner_text("h1").lower(),
                  pg.inner_text("h1"))
            check("Nhan bo loc doi sang EN",
                  "Hydrosphere" in pg.inner_text("#f-cat"), pg.inner_text("#f-cat")[:60])
            check("Cau nhac mo khoa do JS sinh CUNG doi sang EN",
                  any(w in pg.inner_text("#pods") for w in ("Fly to", "Complete", "Answer",
                                                            "Play", "Score", "Visit")),
                  "")
            check("Khong con chu Viet sot trong luoi khoang",
                  not re.search(r"[ăâđêôơư]", pg.inner_text("#pods")),
                  re.findall(r"\S*[ăâđêôơư]\S*", pg.inner_text("#pods"))[:3])
            pg.locator(".pod.on").first.click()
            pg.wait_for_selector("#insp.show")
            btn_en = pg.inner_text("#desk-btn")
            check("Modal EN: nut treo/lay xuong dich dung",
                  ("cockpit wall" in btn_en.lower() or "hanging" in btn_en.lower())
                  and not re.search(r"[ăâđêôơư]", btn_en), btn_en)
            check("Modal EN: fun fact dich dung",
                  not re.search(r"[ăâđêôơư]", pg.inner_text(".box.fact")),
                  pg.inner_text(".box.fact")[:60])
            pg.keyboard.press("Escape")
            pg.click('.lang-switch button[data-lang="vi"]')
            pg.wait_for_timeout(300)
            pg.close()

            # ---------- [10] Điện thoại 390x844 ----------
            print("\n[10] Dien thoai 390x844")
            pg = open_page(390, 844, stub=fake_payload(unlocked, [{"hook": "R2", "id": unlocked[0]}]))
            pg.wait_for_selector(".pod.on", timeout=8000)
            sw = pg.evaluate("() => document.documentElement.scrollWidth")
            check("Khong tran ngang", sw <= 391, f"scrollWidth={sw}")
            check("Nhan header khong bi bop mat chu",
                  pg.eval_on_selector(".hub-tag",
                      "e => e.scrollWidth <= e.clientWidth + 1"),
                  pg.eval_on_selector(".hub-tag", "e => e.scrollWidth+'/'+e.clientWidth"))
            cols = pg.eval_on_selector("#pods",
                "e => new Set([...e.children].map(c => c.getBoundingClientRect().left)).size")
            check("Luoi khoang 2 cot tren dien thoai", cols == 2, f"{cols} cot")
            check("Ten mau vat khong bi cat duoi",
                  pg.eval_on_selector_all(".pod .nm",
                      "els => els.every(e => e.scrollHeight <= e.clientHeight + 2)"))
            pg.locator(".pod.on").first.click()
            pg.wait_for_selector("#insp.show")
            check("Modal khong tran ngang tren dien thoai",
                  pg.eval_on_selector(".insp-card",
                      "e => e.getBoundingClientRect().width <= 390"),
                  pg.eval_on_selector(".insp-card", "e => e.getBoundingClientRect().width"))
            check("Modal 1 cot tren dien thoai",
                  pg.eval_on_selector(".insp-body",
                      "e => getComputedStyle(e).gridTemplateColumns.split(' ').length === 1"),
                  pg.eval_on_selector(".insp-body", "e => getComputedStyle(e).gridTemplateColumns"))
            pg.close()

            # ---------- [11] prefers-reduced-motion ----------
            print("\n[11] prefers-reduced-motion")
            pg = br.new_page(viewport={"width": 1280, "height": 800},
                             reduced_motion="reduce", locale="vi-VN")
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.add_init_script("(" + STUB + ")(" + repr(fake_payload(unlocked, []))
                              .replace("'", '"').replace("True", "true")
                              .replace("False", "false") + ")")
            pg.goto(URL, wait_until="networkidle")
            pg.wait_for_selector(".pod.on", timeout=8000)
            anims = pg.eval_on_selector_all(".pod .halo, .pod .sp, .pod .lock",
                "els => els.map(e => getComputedStyle(e).animationName)")
            check("Bo het hieu ung chay vo han", all(a == "none" for a in anims), str(set(anims)))
            check("Trang van dung duoc (khoang van bam mo duoc)",
                  pg.locator(".pod.on").count() == UNLOCK_N)
            pg.close()

            # ---------- [12] Đối chiếu client ↔ server ----------
            print("\n[12] Doi chieu js/specimens.js <-> Services/Specimens.cs")
            pg = open_page(stub=fake_payload(unlocked, []))
            ids_client = set(pg.evaluate("() => AstroQSpecimens.ids()"))
            ids_server = {s["id"] for s in CAT}
            check("Client co du ten cho MOI mau server khai bao",
                  ids_server <= ids_client, str(sorted(ids_server - ids_client)))
            check("Client KHONG co mau la (server khong khai bao)",
                  ids_client <= ids_server, str(sorted(ids_client - ids_server)))
            miss = pg.evaluate("""() => AstroQSpecimens.ids().filter(id =>
                !AstroQSpecimens.name(id,'vi') || AstroQSpecimens.name(id,'vi') === id ||
                !AstroQSpecimens.name(id,'en') || AstroQSpecimens.name(id,'en') === id ||
                !AstroQSpecimens.fact(id,'vi') || !AstroQSpecimens.fact(id,'en') ||
                !AstroQSpecimens.classification(id) || !AstroQSpecimens.source(id) ||
                !AstroQSpecimens.mascot(id,'vi') || !AstroQSpecimens.mascot(id,'en'))""")
            check("Mau nao cung du ten/fact/nguon/loi linh vat o CA 2 ngon ngu",
                  miss == [], str(miss))
            cats_s = {s["category"] for s in CAT}
            cats_c = set(pg.evaluate("() => Object.keys(AstroQSpecimens.cats)"))
            check("Nhom khop hai ben", cats_s == cats_c, f"{sorted(cats_s)} vs {sorted(cats_c)}")
            orig_miss = [s["origin"] for s in CAT
                         if pg.evaluate("k => AstroQSpecimens.originName(k,'vi')", s["origin"])
                         == s["origin"]]
            check("Moi `origin` cua server deu co ten tieng Viet", orig_miss == [], str(orig_miss))
            # khoá i18n phải đủ ở cả 2 từ điển
            bad_keys = pg.evaluate("""() => {
                const src = [...document.querySelectorAll('script:not([src])')]
                  .map(s => s.textContent).join('\\n');
                const m = src.match(/var I18N = \\{([\\s\\S]*?)\\n  \\};/);
                if(!m) return ['khong tim thay I18N'];
                const keys = t => [...t.matchAll(/^\\s{6}([a-z0-9_]+):/gm)].map(x => x[1]);
                const parts = m[1].split(/\\n    en:\\{/);
                const vi = new Set(keys(parts[0])), en = new Set(keys(parts[1] || ''));
                return [...new Set([...[...vi].filter(k => !en.has(k)),
                                    ...[...en].filter(k => !vi.has(k))])];
            }""")
            check("Moi khoa i18n co o CA vi va en", bad_keys == [], str(bad_keys))
            pg.close()

            print("\n[13] Loi console")
            check("0 loi console tren moi luot", len(errs) == 0, str(errs[:3]))
            br.close()
    finally:
        srv.terminate()

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
