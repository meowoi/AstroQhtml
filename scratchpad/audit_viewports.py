# -*- coding: utf-8 -*-
"""
audit_viewports.py — rà TƯƠNG THÍCH KÍCH CỠ / UI trên iPad · MacBook · Windows.

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/audit_viewports.py

ĐO GÌ (những thứ chỉ đo mới thấy, đọc CSS không thấy):
  1. TRÀN NGANG — `scrollWidth > clientWidth`. Trang có thanh cuộn ngang là lỗi bố
     cục, không phải chuyện thẩm mỹ: trên tablet nó làm cả trang trượt khi trẻ vuốt.
  2. CHỮ BỊ CẮT — `scrollWidth > clientWidth` trên từng phần tử chữ. Bài học đã ghi
     trong CLAUDE.md: nhãn ô thống kê từng ra "LƯỢT HUẤN LUY…" ở desktop, và
     `.hub-tag` bị bóp còn "[ …" ở màn 390px.
  3. VÙNG CHẠM QUÁ NHỎ — nút/link dưới 44×44px trên thiết bị cảm ứng (mốc WCAG
     2.5.5 / hướng dẫn Apple). Chỉ tính trên iPad, vì chuột thì 44px là quá khắt khe.
  4. PHẦN TỬ CHÌA RA NGOÀI khung nhìn theo chiều ngang.
  5. LỖI CONSOLE + asset 404 ở từng cỡ màn.

⚠️ CHỈ ĐO TRANG, KHÔNG ĐOÁN. Không có phép kiểm nào ở đây dựa vào việc đọc CSS.

⚠️ Nhãn của check() PHẢI KHÔNG DẤU — console Windows mặc định cp1252, in chữ có dấu
   là UnicodeEncodeError ném GIỮA LÚC CHẠY và bỏ dở mọi phép kiểm phía sau.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"

USER = {"name": "Bi", "pilotName": "Bi", "character": "raica",
        "avatar": "ava/avaraica.png", "uid": "audit-uid",
        "selectedCharacter": "raica"}

# (ten, w, h, cam ung, dpr)
# Cỡ thật, không phải cỡ tròn cho đẹp:
#   · iPad mini 8,3"      768×1024 (dọc) / 1024×768 (ngang)
#   · iPad Pro 12,9"      1024×1366 (dọc)
#   · MacBook Air 13" M2  1470×956 (khung nhìn CSS)
#   · MacBook Pro 14"     1512×982
#   · Windows pho bien    1366×768  (còn rất nhiều máy học sinh)
#   · Windows Full HD     1920×1080
DEVICES = [
    ("iPad-mini-doc",    768, 1024, True,  2),
    ("iPad-mini-ngang", 1024,  768, True,  2),
    ("iPad-Pro-doc",    1024, 1366, True,  2),
    ("MacBook-Air-13",  1470,  956, False, 2),
    ("MacBook-Pro-14",  1512,  982, False, 2),
    ("Win-1366x768",    1366,  768, False, 1),
    ("Win-FullHD",      1920, 1080, False, 1),
]

PAGES = [
    "index.html", "landing-app.html", "select.html", "dashboard.html",
    "learn.html", "library.html", "codex.html", "quiz.html",
    "games.html", "missions.html", "profile.html", "achievements.html",
    "specimen-vault.html",
    # pricing.html them 09/08/2026 — bang gia co luoi `auto-fit` va bang so sanh
    # 3 cot, hai thu de tran ngang nhat tren man hep.
    "pricing.html",
    "parent.html",
    # checkout.html them 11/08/2026 — trang thanh toan, bo cuc 2 cot + o nhap
    "checkout.html",
    # Mini-game + 2 trang 3D: sân chơi khoá theo `aspect-ratio` nên đây là chỗ
    # dễ tràn ngang nhất khi màn thấp (Win 1366x768, iPad ngang).
    "game-dodge.html", "game-defender.html", "game-constellation.html",
    "game-catch.html", "game-maze.html", "game-racer.html",
    "explorer.html", "mission-earth.html", "mission-orbit.html",
]

ok_n = bad_n = 0
findings = []
ell = []   # chu thu gon bang ellipsis co y — chi bao cao, khong tinh hong

# Chay nhanh mot tap nho khi can (dung cho phep thu pha hoai):
#   python scratchpad/audit_viewports.py --dev iPad-mini-doc --only explorer.html
if "--dev" in sys.argv:
    want = sys.argv[sys.argv.index("--dev") + 1]
    DEVICES = [d for d in DEVICES if d[0] == want]
    assert DEVICES, f"khong co thiet bi {want}"
if "--only" in sys.argv:
    PAGES = sys.argv[sys.argv.index("--only") + 1].split(",")


def check(cond, label, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
    else:
        bad_n += 1
        findings.append((label, detail))
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


PROBE = """
() => {
  const de = document.documentElement;
  const out = {
    sw: de.scrollWidth, cw: de.clientWidth,
    clipped: [], ellip: [], tiny: [], outside: []
  };
  const vw = de.clientWidth;

  for (const e of document.querySelectorAll(
        'h1,h2,h3,h4,button,a,span,p,div,label,strong,b,td,th')) {
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const cs = getComputedStyle(e);
    if (cs.visibility === 'hidden' || cs.display === 'none' || cs.opacity === '0') continue;
    // Chi xet phan tu co chu TRUC TIEP (khong tinh the bao ngoai)
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) continue;
    const cls = (e.className || '').toString();
    const rec = { t: (e.textContent||'').trim().slice(0,34),
                  sw: e.scrollWidth, cw: e.clientWidth, cls: cls.slice(0,26) };

    // (2) Chu khong vua o chua. TACH HAI LOAI, vi chung khac han nhau ve muc do:
    //   · co `text-overflow: ellipsis`  -> thu gon CO Y, hien dau "…"
    //   · khong co                      -> chu bi CHAT ngang giua net chu
    if (e.scrollWidth > e.clientWidth + 1 && cs.overflowX !== 'auto'
        && cs.overflowX !== 'scroll') {
      if (cs.textOverflow === 'ellipsis') {
        // Ellipsis chi chap nhan duoc voi CAU MO TA PHU. Voi TIEU DE thi khong:
        // "Vung lan can Mat Tro…" khong con la mot cai ten.
        const heading = /^h[1-4]$/.test(e.tagName.toLowerCase()) ||
                        /title|name|\\bnm\\b|label|heading/i.test(cls);
        (heading ? out.clipped : out.ellip).push(rec);
      } else {
        out.clipped.push(rec);
      }
    }

    // (4) CHIA RA NGOAI khung nhin. ⚠️ Chi tinh phan tu VUA TRONG VUA NGOAI (bi
    // cat doi o mep man hinh) — do moi la loi bo cuc. Phan tu NAM HAN ngoai khung
    // la bang keo dang dong (explorer do bang thong tin dang dong ra ngoai mep
    // phai, va phep kiem "khong tran ngang" da chung minh no khong sinh cuon
    // ngang). Ban dau toi tinh ca hai va no bao hong 7 lan tren mot thiet ke dung.
    // ⚠️ MIEN TRU lop `#labels` cua explorer: do la nhan ten thien the do
    // CSS2DRenderer cua three.js dat theo VI TRI HANH TINH TREN QUY DAO, khong
    // phai bo cuc CSS. Hanh tinh o mep phai thi nhan bi mep man hinh cat mot
    // nua — do la du lieu, khong phai loi can sua, va lop do co
    // `pointer-events:none` nen khong sinh cuon ngang. Ke ca muon sua cung khong
    // sua duoc bang CSS; phai doc getBoundingClientRect moi khung hinh cho tung
    // nhan, tuc la ep trinh duyet tinh lai bo cuc 60 lan/giay.
    const inScene = e.closest && e.closest('#labels');
    const straddleR = r.left < vw - 2 && r.right > vw + 2;
    const straddleL = r.right > 2 && r.left < -2;
    if (!inScene && (straddleR || straddleL)) {
      out.outside.push({ t:(e.textContent||'').trim().slice(0,28),
                         l:Math.round(r.left), rr:Math.round(r.right),
                         cls: cls.slice(0,26) });
    }
  }

  // (3) Vung cham qua nho. Ngoai le WCAG 2.5.5 giai thich o `audit_taps.py`.
  for (const e of document.querySelectorAll('button, a, input, select, [role=button]')) {
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const cs = getComputedStyle(e);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (r.width >= 44 && r.height >= 44) continue;
    if (cs.opacity === '0' || r.top < -200 || r.left < -200 ||
        cs.clipPath === 'inset(50%)' || e.getAttribute('aria-hidden') === 'true') continue;
    const p = e.parentElement;
    if (p && cs.display.indexOf('inline') === 0 &&
        [...p.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    // Ngoai le thu hai: mot <input> BOC TRONG <label> thi vung cham THAT SU la ca
    // cai label (bam vao chu cung bat/tat duoc o danh dau) — do rieng cai input la
    // do mot thu khong phai target. Chi mien khi CHINH cai label du 44px.
    const lab = e.closest && e.closest('label');
    if (lab && lab !== e) {
      const lr = lab.getBoundingClientRect();
      if (lr.width >= 44 && lr.height >= 44) continue;
    }
    out.tiny.push({ t:(e.textContent||e.getAttribute('aria-label')||
                       e.getAttribute('placeholder')||'').trim().slice(0,26),
                    w:Math.round(r.width), h:Math.round(r.height),
                    cls:(e.className||'').toString().slice(0,26) });
  }
  // Bo trung
  const uniq = a => { const s=new Set(), o=[]; for(const x of a){
      const k=JSON.stringify(x); if(!s.has(k)){s.add(k);o.push(x);} } return o; };
  out.clipped = uniq(out.clipped).slice(0, 6);
  out.ellip = uniq(out.ellip).slice(0, 6);
  out.tiny = uniq(out.tiny).slice(0, 8);
  out.outside = uniq(out.outside).slice(0, 6);
  return out;
}
"""

with sync_playwright() as p:
    br = p.chromium.launch()
    for name, w, h, touch, dpr in DEVICES:
        print(f"\n=== {name}  {w}x{h}  {'cam ung' if touch else 'chuot'} ===")
        kw = {"viewport": {"width": w, "height": h}, "locale": "vi-VN",
              "device_scale_factor": dpr}
        if touch:
            kw["has_touch"] = True
        ctx = br.new_context(**kw)
        ctx.add_init_script(
            f"localStorage.setItem('astroq-user', {json.dumps(json.dumps(USER))});"
            "localStorage.setItem('astroq-lang','vi');"
            "localStorage.setItem('astroq-asteroids','120');"
            # Tắt các màn onboarding để đo được chính trang, không đo lớp phủ
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-mission01-intro-seen','1');"
            "localStorage.setItem('astroq-mob-note','1');"
        )
        for page in PAGES:
            pg = ctx.new_page()
            # ⚠️ CHAN MOI LOI GOI API VA TRA MOT PHAN HOI CO DINH.
            #    Bo do nay do BO CUC, khong do ket noi. Hai ly do phai chan:
            #    ① Bo do chay o cong 8123, KHONG nam trong ALLOWED_ORIGINS, nen moi
            #      loi goi that deu bi CORS chan va trinh duyet TU GHI mot dong do
            #      vao console — khong `catch` nao chan duoc — lam phep kiem
            #      "0 loi console" bao hong oan.
            #    ② De trang goi API that la de ket qua bo do phu thuoc vao viec
            #      Lambda co song hay khong. Mot phep do bo cuc khong duoc phep do.
            #    `saleOpen:false` la trang thai THAT cua hom nay, nen trang van ve
            #    ra dung thu nguoi dung dang thay.
            pg.route("**/billing/catalog*", lambda r: r.fulfill(
                status=200, content_type="application/json",
                headers={"access-control-allow-origin": "*"},
                body='{"ok":true,"saleOpen":false,"provider":"none","currency":"VND",'
                     '"trialDays":14,"graceDays":7,"offers":['
                     '{"plan":"astro","cycle":"month","currency":"VND","amount":99000},'
                     '{"plan":"astro","cycle":"year","currency":"VND","amount":790000},'
                     '{"plan":"crew","cycle":"month","currency":"VND","amount":169000},'
                     '{"plan":"crew","cycle":"year","currency":"VND","amount":1290000},'
                     '{"plan":"found","cycle":"once","currency":"VND","amount":1490000}]}'))
            errs, bad404 = [], []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("response",
                  lambda r: bad404.append(r.url.split("/")[-1]) if r.status >= 400 else None)
            try:
                pg.goto(f"{BASE}/{page}", wait_until="load", timeout=25000)
            except Exception as e:  # noqa: BLE001
                check(False, f"{name} · {page}: tai duoc trang", str(e)[:60])
                pg.close()
                continue
            pg.wait_for_timeout(1400)
            r = pg.evaluate(PROBE)

            check(r["sw"] <= r["cw"] + 1, f"{name} · {page}: KHONG tran ngang",
                  f"scrollWidth {r['sw']} > clientWidth {r['cw']}")
            check(not r["clipped"], f"{name} · {page}: khong co chu bi cat",
                  json.dumps(r["clipped"], ensure_ascii=False)[:190])
            check(not r["outside"], f"{name} · {page}: khong co phan tu chia ra ngoai",
                  json.dumps(r["outside"], ensure_ascii=False)[:190])
            if touch:
                check(not r["tiny"], f"{name} · {page}: vung cham >= 44px",
                      json.dumps(r["tiny"], ensure_ascii=False)[:220])
            check(not errs, f"{name} · {page}: 0 loi console", str(errs[:1])[:120])
            check(not bad404, f"{name} · {page}: 0 asset 404", str(bad404[:3]))
            if r["ellip"]:
                # Khong tinh la hong: day la thu gon CO Y bang "…" tren cau mo ta
                # phu. Nhung PHAI in ra, vi mot cai bang co y thu gon 9/10 dong
                # chu thi ve mat nguoi dung khong khac gi bi cat.
                ell.append((f"{name} · {page}", r["ellip"]))
            pg.close()
        ctx.close()
    br.close()

print(f"\n===== {ok_n} dat / {bad_n} hong =====")

# ⚠️ IN KHONG DIEU KIEN. Ban dau toi de `if ell:` va muc nay im lang, nen toi
# tuong "khong con chu nao bi thu gon" — trong khi that ra khoi print chua duoc
# chen vao file. Mot muc bao cao chi hien khi co van de thi khong the phan biet
# "sach" voi "khong chay".
print(f"\n--- Chu THU GON BANG ELLIPSIS (co y, khong tinh hong): "
      f"{len(ell)} trang ---")
for where, items in ell:
    print(f"  {where}: " +
          ", ".join(f"{i['cls'] or '?'}({i['sw']}>{i['cw']}px) {i['t']!r}"
                    for i in items))

if findings:
    print(f"\n--- {len(findings)} phat hien, gom theo loai ---")
    from collections import Counter
    kinds = Counter(l.split(": ", 1)[1] for l, _ in findings)
    for k, n in kinds.most_common():
        print(f"  {n:>3}x  {k}")
sys.exit(1 if bad_n else 0)
