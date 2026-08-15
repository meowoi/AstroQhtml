# -*- coding: utf-8 -*-
"""Do TRUNG TAM DAO TAO tren Chromium that.

  python -m http.server 8123     (trong AstroQhtml/)
  py -3 scratchpad/smoke_training.py

Do thu NGUOI DUNG THAY, khong doc code:
  · nhan tren the la TEN CHUONG TRINH (khong con nhan the loai kieu sanh game)
  · dong ky nang + duong sang bai doc co that va BAM DUOC
  · duong doc bai KHONG khoa nut Choi ngay
  · chua doc duoc ho so → dau `—`, KHONG hien 0/5
  · doc duoc → dung so server gieo, ke ca khi gieo so LECH HAN mac dinh
  · doi VI/EN dich ca ten chuong trinh lan dong ky nang
"""
import os, re, sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent
BASE = "http://127.0.0.1:8123"
ok = bad = 0
def ck(n, c, d=""):
    global ok, bad
    if c: ok += 1; print(f"  [OK]   {n}" + (f"  ({d})" if d else ""))
    else: bad += 1; print(f"  [HONG] {n}  {d}")

UID = "u-test-training"
def seed(ctx, training=None):
    js = "localStorage.setItem('astroq-lang','vi');"
    js += "localStorage.setItem('astroq-user',%s);" % json.dumps(json.dumps(
        {"uid": UID, "name": "Tester", "character": "raica"}))
    if training is not None:
        js += "localStorage.setItem('astroq-training',%s);" % json.dumps(
            json.dumps(dict(training, uid=UID)))
    else:
        js += "localStorage.removeItem('astroq-training');"
    ctx.add_init_script(js)

# Doc DANH SACH CHUONG TRINH tu js/training.js (client giu TEN) — khong go tay
tj = (ROOT / "js" / "training.js").read_text(encoding="utf-8")
PROG_KEYS = re.findall(r"\n    ([a-z]+): \{\n      ic:", tj)
IDX = (ROOT / "js" / "articles-index.js").read_text(encoding="utf-8")

with sync_playwright() as p:
    br = p.chromium.launch()

    # ═══════ [1] KHONG CON duong 'doc them' o the game ═══════
    #
    # ⚠️ DOI PHAT BIEU 15/08/2026 (chu du an chot: *"bo phan doc them o cac tro
    #    choi"*). Truoc do muc nay canh "moi chuong trinh co mot bai doc goi y va
    #    id do co that". Nay canh chieu NGUOC LAI — khong con dau vet nao — vi mot
    #    tinh nang da bo ma con nua bo du lieu o lai la cai bay cho nguoi sua sau.
    print("\n[1] Da bo han duong 'doc them' (du lieu + API + markup)")
    ck("boc duoc chuong trinh tu js/training.js", len(PROG_KEYS) >= 5, str(PROG_KEYS))
    ck("js/training.js KHONG con du lieu `read`", "read:" not in tj,
       "con: " + tj[tj.find("read:"):tj.find("read:") + 40] if "read:" in tj else "")
    ck("js/training.js KHONG con API `read()`", "read: function" not in tj)
    # ⚠️ QUET TREN BAN DA BOC CHU THICH — chinh doan ghi chu giai thich viec gỡ
    #    cung nhac lai `AstroQTraining.read()`, va ghi chu do la thu NEN co. Day la
    #    lan thu 16 du an dinh loi "dem ca chu trong ghi chu cua chinh minh".
    _gh = re.sub(r"<!--.*?-->|/\*.*?\*/", " ",
                 (ROOT / "games.html").read_text(encoding="utf-8"), flags=re.S)
    ck("games.html KHONG con goi AstroQTraining.read", "AstroQTraining.read" not in _gh)
    ck("games.html KHONG con khoa i18n read_lb", "read_lb" not in _gh)

    # ═══════ [2] Chua doc duoc ho so → `—`, KHONG hien 0/5 ═══════
    print("\n[2] Chua doc duoc ho so → dau `—`")
    ctx = br.new_context(viewport={"width": 1440, "height": 900}); seed(ctx)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/games.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".gcard", timeout=8000)
    rec = pg.inner_text("#record")
    ck("hien dau `—`", "—" in pg.inner_text("#rec-n"), pg.inner_text("#rec-n"))
    ck("KHONG hien 0/5 hay 0 chuong trinh", not re.search(r"\b0\s*/\s*\d", rec), rec[:70])
    ck("co cau noi that ly do", pg.locator("#rec-note").is_visible())
    ck("KHONG the nao hien cap", pg.locator(".gcard .cert").count() == 0)
    ck("0 loi trang", not errs, str(errs[:2]))

    # ═══════ [3] Nhan the = TEN CHUONG TRINH ═══════
    print("\n[3] Nhan tren the la ten chuong trinh, khong phai the loai game")
    tags = pg.eval_on_selector_all(".gcard .tag", "e=>e.map(x=>x.textContent.trim())")
    ck("moi the co nhan", len(tags) == 6, str(len(tags)))
    # ⚠️ CHI liet ke nhan the loai KHONG trung ten chuong trinh nao. Ban dau toi
    #    de ca "Phản xạ" vao day — nhung do cung la TEN CHUONG TRINH moi, nen phep
    #    kiem khong bao gio xanh duoc du san pham lam dung. Phep kiem hong, khong
    #    phai san pham hong.
    old = ["Giải đố", "Đua tốc độ", "Phòng thủ 360°", "Bay ngang"]
    ck("KHONG con nhan the loai kieu sanh game",
       not any(o in " | ".join(tags) for o in old), " | ".join(tags))
    ck("nhan la ten chuong trinh (co Phan xa · Nhan thuc khong gian)",
       any("Phản xạ" in x for x in tags) and any("Nhận thức không gian" in x for x in tags),
       " | ".join(tags))
    # Hai game cung chuong trinh thi mang cung mot nhan → do la cach GOM nhom
    ck("2 game cung chuong trinh mang cung nhan",
       sum(1 for x in tags if "Phản xạ" in x) == 2, " | ".join(tags))

    # ═══════ [4] Dong ky nang + duong doc bai ═══════
    print("\n[4] Dong ky nang va duong sang bai doc")
    ck("moi the co dong ky nang", pg.locator(".gcard .skill").count() == 6,
       str(pg.locator(".gcard .skill").count()))
    ck("KHONG con duong doc bai tren the", pg.locator(".gcard .readlink").count() == 0,
       str(pg.locator(".gcard .readlink").count()))
    # Nut Choi ngay van bam duoc va khong `disabled`
    dis = pg.eval_on_selector_all(".gcard:not(.soon) .play-btn", "e=>e.map(x=>x.disabled)")
    ck("nut Choi ngay bam duoc", not any(dis), str(dis))

    # ⚠️ KHOI [5] cu ("bam duong doc bai -> library.html mo dung bai") DA BO cung
    #    voi tinh nang do. `library.html?a=<id>` VAN CHAY — no la duong mo thang
    #    mot bai, chi la khong con the game nao tro toi nua.
    ctx.close()

    # ═══════ [6] Doc duoc ho so — GIEO SO LECH HAN mac dinh ═══════
    # Day la phep do DUY NHAT phan biet duoc "doc server" voi "tu tinh o client":
    # gieo 2/7 (that la 2/5) va mot chuong trinh la → trang phai hien DUNG so gieo.
    print("\n[6] Doc duoc ho so — gieo so LECH HAN de chac la doc server")
    # ⚠️ SO GIEO LECH HAN mac dinh: 9/21 (that la ?/20) va bay chuong trinh trong
    #    khi server chi co nam — hai chuong trinh cuoi CHUA khai ten o client.
    #    Day la cach duy nhat phan biet "doc server" voi "tu tinh o client".
    fake = {
        "levels": 9, "maxLevels": 21, "total": 7,
        "programs": [
            {"key": "reaction", "level": 4, "maxLevel": 4, "courses": [
                {"game": "dodge", "level": 4, "maxLevel": 4, "current": 1350, "next": None, "best": 1600},
                {"game": "catch", "level": 4, "maxLevel": 4, "current": 850,  "next": None, "best": 900}]},
            {"key": "spatial", "level": 2, "maxLevel": 4, "courses": [
                {"game": "defender", "level": 2, "maxLevel": 4, "current": 640, "next": 800, "best": 640}]},
            {"key": "navigation", "level": 3, "maxLevel": 4, "courses": [
                {"game": "maze", "level": 3, "maxLevel": 4, "current": 4, "next": 5, "best": 4}]},
            {"key": "resource", "level": 0, "maxLevel": 4, "courses": [
                {"game": "racer", "level": 0, "maxLevel": 4, "current": 900, "next": 3500, "best": 900}]},
            {"key": "observation", "level": 0, "maxLevel": 4, "courses": [
                {"game": "constellation", "level": 0, "maxLevel": 4, "current": 0, "next": 1, "best": 0}]},
            {"key": "docking", "level": 0, "maxLevel": 4, "courses": []},
            {"key": "eva",     "level": 0, "maxLevel": 4, "courses": []},
        ],
    }
    ctx = br.new_context(viewport={"width": 1440, "height": 900}); seed(ctx, fake)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/games.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".gcard", timeout=8000)
    n = pg.inner_text("#rec-n")
    ck("hien DUNG so server gieo (9/21, khong phai 0/20)", "9" in n and "21" in n, n)
    ck("ve du 7 thanh theo so chuong trinh server tra",
       pg.locator("#rec-dots .rd").count() == 7, str(pg.locator("#rec-dots .rd").count()))
    ck("khong con cau 'chua doc duoc'", not pg.locator("#rec-note").is_visible())
    ck("chuong trinh chua khai ten KHONG lam vo trang", not errs, str(errs[:2]))

    certs = pg.eval_on_selector_all(".gcard .cert", "e=>e.map(x=>x.textContent.trim())")
    # ⚠️⚠️ TUYET DOI KHONG CON CHU "DA DAT" — do la mot dau cham het bao tre rang
    #    o day het viec, dung thu ma ca lan sua nay di bo.
    ck("KHONG con huy hieu 'DA DAT'", not any("ĐÃ ĐẠT" in c for c in certs), str(certs))
    # ⚠️ So `casefold()`: the o Cap 0 hien "Chưa có cấp" (chu thuong) nen kiem
    #    `"Cấp" in c` truot — loi cua phep kiem, khong phai san pham. Day la lan
    #    thu n cua bai hoc "dung ghim mot cach viet hoa" (quy tac 8 muc 6).
    ck("moi the hien mot CAP", all("cấp" in c.casefold() for c in certs), str(certs))
    ck("the o cap toi da hien Cap 4/4", any("Cấp 4/4" in c for c in certs), str(certs))
    ck("the chua co cap hien 'Chua co cap'", any("Chưa có cấp" in c for c in certs), str(certs))

    # ── Thu quan trong nhat: LUON CO MOT MOC KE TIEP ──
    goals = pg.eval_on_selector_all(".gcard .nextgoal", "e=>e.map(x=>x.textContent.trim())")
    ck("moi the deu noi ra viec tiep theo", len(goals) == 6, str(len(goals)))
    ck("the chua toi da noi 'Con ... nua len Cap ...'",
       any("Còn" in g and "lên Cấp" in g for g in goals), str(goals[:2]))
    ck("the da toi da MOI PHA KY LUC, khong noi 'xong'",
       any("phá kỷ lục" in g for g in goals), str(goals))
    ck("KHONG the nao noi mot cau doc ra thanh 'het viec'",
       not any(w in " ".join(goals).lower() for w in ["hoàn tất", "đã xong", "kết thúc"]),
       str(goals))
    # Thanh tien do phai co va rong dung ti le
    bars = pg.eval_on_selector_all(".gcard .lvbar i", "e=>e.map(x=>x.style.width)")
    ck("the chua toi da co thanh tien do", len(bars) >= 3, str(bars))
    ck("thanh tien do khong bao gio vuot 100%",
       all(int(b.replace("%","") or 0) <= 100 for b in bars), str(bars))

    # ═══════ [7] Ho so cua NGUOI KHAC khong duoc hien ═══════
    print("\n[7] Cache cua uid khac → coi nhu chua biet")
    ctx.close()
    # ⚠️ CONTEXT MOI, gieo thang cache mang uid nguoi khac. KHONG sua bang
    #    pg.evaluate roi reload: `add_init_script` GIEO LAI SAU MOI LAN DIEU HUONG
    #    nen no ghi de dung cai vua sua — bay nay CLAUDE.md da ghi 4 lan, va toi
    #    vua mac lai lan thu 5.
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    seed(ctx, fake)
    ctx.add_init_script("""(() => {
      const b = JSON.parse(localStorage.getItem('astroq-training') || '{}');
      b.uid = 'u-nguoi-khac';
      localStorage.setItem('astroq-training', JSON.stringify(b));
    })()""")
    pg = ctx.new_page()
    pg.goto(f"{BASE}/games.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".gcard", timeout=8000)
    ck("ho so nguoi khac KHONG hien", "—" in pg.inner_text("#rec-n"), pg.inner_text("#rec-n"))
    ck("va khong hien cap cua the nao", pg.locator(".gcard .cert").count() == 0)
    ctx.close()

    # ═══════ [8] Ban EN ═══════
    print("\n[8] Ban tieng Anh")
    ctx = br.new_context(viewport={"width": 1440, "height": 900}); seed(ctx, fake)
    ctx.add_init_script("localStorage.setItem('astroq-lang','en')")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/games.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".gcard", timeout=8000)
    tags_en = pg.eval_on_selector_all(".gcard .tag", "e=>e.map(x=>x.textContent.trim())")
    ck("ten chuong trinh dich sang EN",
       any("Reaction" in x for x in tags_en) and not any("Phản xạ" in x for x in tags_en),
       " | ".join(tags_en))
    sk_en = pg.eval_on_selector_all(".gcard .skill", "e=>e.map(x=>x.textContent.trim())")
    ck("dong ky nang dich sang EN", any("Skill:" in x for x in sk_en), str(sk_en[:1]))
    ck("ho so dich sang EN", "level" in pg.inner_text("#rec-n").lower(),
       pg.inner_text("#rec-n"))
    g_en = pg.eval_on_selector_all(".gcard .nextgoal", "e=>e.map(x=>x.textContent.trim())")
    ck("cau moc ke tiep dich sang EN",
       any("Level" in g for g in g_en) and not any("Cấp" in g for g in g_en), str(g_en[:2]))
    ck("0 loi trang o ban EN", not errs, str(errs[:2]))
    ctx.close()

    # ═══════ [9] Dien thoai 390x844 ═══════
    print("\n[9] Dien thoai 390x844")
    ctx = br.new_context(viewport={"width": 390, "height": 844},
                         has_touch=True, is_mobile=True); seed(ctx, fake)
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/games.html", wait_until="domcontentloaded")
    pg.wait_for_selector(".gcard", timeout=8000)
    over = pg.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
    ck("khong tran ngang", over <= 0, f"tran {over}px")
    cut = pg.eval_on_selector_all(".gcard .skill, .gcard .readlink, .gcard .nextgoal, #rec-n",
                                  "e=>e.filter(x=>x.scrollWidth>x.clientWidth+1).length")
    ck("khong chu nao bi cat", cut == 0, str(cut))
    ck("0 loi trang tren dien thoai", not errs, str(errs[:2]))
    ctx.close()

    br.close()

print(f"\n===== {ok} dat / {bad} hong =====")
sys.exit(1 if bad else 0)
