# -*- coding: utf-8 -*-
"""Do MAU VAT TRUNG TRONG BUONG LAI tren dashboard.

Cau hoi goc (29/07): tre chon mau vat o specimen-vault roi thi buong lai co VE RA
khong — truoc do dashboard co 0 cho nhac `desk`, tuc app hua mot cho trung bay roi
khong trung gi ca.

16/08/2026 DOI HAN cach trung, qua HAI buoc:
  1. Chu du an bac ban "hang chip co ten" vi no doc ra la mot BANG KIEM KE chu khong
     phai do trang tri: *"trang tri thi chi co hinh, ko co ten di kem"* + *"lo lung
     nhu trong khong gian... kich thuoc lon hon"*.
  2. Roi bo HAN ca khoi do khoi bang Thong Ke: *"bo phan nay di, toi ko muon no xuat
     hien o day"*.
Nen nay chi con MOT lop: `#desk-float` — khoang tha noi o le trai/phai cua noi dung,
va no chi song tu 1280px tro len (duoi nguong lan trong chi ~77px, khong chua noi mot
khoang 92px). DUOI 1280px KHONG HIEN MAU VAT O DAU CA — cho MAT co y thuc, khong phai
bo sot; co phep kiem [5] canh dung dieu do.

⚠️ BA PHEP KIEM QUAN TRONG NHAT o day KHONG phai dem so khoang:
  (a) KHONG ten nao ve ra tren mat tranh (ten chi duoc nam o title/aria-label —
      van doc duoc bang trinh doc man hinh, chi khong nam tren tranh),
  (b) khoang khong de len MOT CHU nao cua giao dien,
  (c) `#desk-float` khong nam trong to tien co `backdrop-filter`/`transform` —
      to tien nhu the bien thanh KHOI CHUA cua moi con `position:fixed`, tuc
      "tha noi giua buong lai" hoa ra tha noi trong cai bang thong ke. Bay nay da
      tra gia that voi tam tha cua menu avatar (15/08/2026).
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
# Tu 16/08/2026 tre TU CHON moc treo, nen ban thu phai dung moc RAI RAC — de day
# du ba mau vao L1/L2/L3 thi khong phan biet duoc "ve dung moc da chon" voi "ve
# theo thu tu trong mang", tuc phep kiem dat mot cach rong.
DESK = [{"hook": "L1", "id": "ancient-seawater"},
        {"hook": "R4", "id": "mars-red-ice"},
        {"hook": "L3", "id": "amazon-leaf"}]

ok = bad = 0


def chk(name, cond, extra=""):
    global ok, bad
    if cond:
        ok += 1; print(f"  [OK]   {name}" + (f"  ({extra})" if extra else ""))
    else:
        bad += 1; print(f"  [HONG] {name}" + (f"  ({extra})" if extra else ""))


def stub(desk, lang="vi", known=True):
    """known=False: server khong tra loi duoc — dashboard CHUA BIET tre trung gi.
    Khac han "biet la chua trung gi": chua biet thi dung ve cho de danh moi goi."""
    import json
    if not known:
        return """
window.__A = {
  getAchievements: function(){ return Promise.resolve({ ok:false, reason:'auth' }); },
  getMissions:function(){ return Promise.resolve({ok:false,reason:'auth'}); },
  getOnboarding:function(){ return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,
                                                    earth1Greeted:true,map01Seen:true}); },
  setOnboarding:function(){ return Promise.resolve({ok:true}); },
  postProgress:function(){ return Promise.resolve({ok:true,data:{}}); },
  getShop:function(){ return Promise.resolve({ok:false,reason:'auth'}); }
};
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return window.__A;},set:function(){}});
"""
    return """
window.__A = {
  getAchievements: function(){ return Promise.resolve({ ok:true, data:{
    depth:'junior', ship:'LUNA MOT',
    equipped:{theme:'cockpit-cyan',frame:'frame-steel',decal:'decal-none'},
    level:{level:7,xp:1355,xpInLevel:155,xpForNext:700,pct:22},
    progress:{quizCorrect:24,quizAnswered:30,gamesPlayed:6,planets:[],
              flightSeconds:4800,meteorsEarned:100,bests:{},terms:[],
              desk: %s, deskHooks: %s},
    achievements:{summary:{total:22,earned:6},badges:[]},
    wallet:{meteors:1021} }}); },
  getMissions:function(){ return Promise.resolve({ok:false,reason:'auth'}); },
  getOnboarding:function(){ return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,
                                                    earth1Greeted:true,map01Seen:true}); },
  setOnboarding:function(){ return Promise.resolve({ok:true}); },
  postProgress:function(){ return Promise.resolve({ok:true,data:{}}); },
  getShop:function(){ return Promise.resolve({ok:false,reason:'auth'}); }
};
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return window.__A;},set:function(){}});
""" % (json.dumps([d["id"] for d in desk]), json.dumps(desk))


def seed(lang="vi"):
    return ("localStorage.setItem('astroq-lang','%s');"
            "localStorage.setItem('astroq-tour-seen','1');"
            "localStorage.setItem('astroq-map01-seen','1');"
            "localStorage.setItem('astroq-user', JSON.stringify({name:'Bin',pilotName:'Bin',"
            "uid:'u',equipped:{theme:'cockpit-cyan',frame:'frame-steel',decal:'decal-none'},"
            "ship:'LUNA MOT'}));" % lang)


JS = """
() => {
  const flo = document.getElementById('desk-float');
  if (!flo) return {err:'thieu #desk-float'};
  const vis = e => getComputedStyle(e).display !== 'none' && !e.hasAttribute('hidden');
  const floOn = vis(flo);
  const pods = [...flo.querySelectorAll('.dfp')];
  /* Bang Thong Ke phai SACH: khong con mot dau vet nao cua hang mau vat cu. */
  const trongBang = document.querySelectorAll(
    '.stats-hud #deskrow, .stats-hud .dpod, .stats-hud .dk-shelf, .stats-hud .dk-tag').length;
  const full  = pods.filter(p => !p.className.includes('--empty'));
  const empty = pods.filter(p =>  p.className.includes('--empty'));

  /* (a) Ten LO RA. ⚠️ Bien tuong KHONG PHAI ten — no chinh la mon do trang tri.
     Ban dau lay `p.textContent` nen no dem ca emoji roi bao hong voi '💧💎🌿';
     phep kiem do dang do THU NO SINH RA DE BAO VE. Nay bo cac nut mang bien tuong
     (`.dp-sp`) va dau '+' (`.dp-plus`) roi moi doc chu con lai. */
  const loRa = pods.map(p => {
    const c = p.cloneNode(true);
    c.querySelectorAll('.dp-sp, .dp-plus').forEach(x => x.remove());
    return c.textContent.trim();
  }).join('');

  /* (b) Chong lan voi moi phan tu co chu RIENG trong main.
     ⚠️ BO QUA phan tu NAM TRONG chinh khoang — khong thi `.dp-sp` (bien tuong) bi
     tinh la "khoang de len chu", tuc khoang de len chinh no: do duoc 1236px2 oan. */
  let worst = 0, who = '';
  document.querySelectorAll('main *').forEach(e => {
    if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
    const q = e.getBoundingClientRect();
    pods.forEach(pd => {
      if (pd.contains(e)) return;
      const r = pd.getBoundingClientRect();
      const w = Math.max(0, Math.min(r.right, q.right) - Math.max(r.left, q.left));
      const h = Math.max(0, Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top));
      if (w * h > worst) { worst = w * h; who = e.className || e.tagName; }
    });
  });

  /* (c) To tien nao bien #desk-float thanh khoi chua cua `position:fixed` */
  let trap = '';
  for (let n = flo.parentElement; n && n !== document.documentElement; n = n.parentElement) {
    const s = getComputedStyle(n);
    if (s.transform !== 'none' || s.filter !== 'none' || s.backdropFilter !== 'none')
      trap = n.tagName + '.' + n.className;
  }

  /* ── HÌNH HỌC HAI VÁCH ─────────────────────────────────────────────────────
     Đây là phần THÊM 16/08/2026, và là thứ duy nhất trả lời được câu "5 móc mỗi
     vách có thật sự vừa không". Đo TRÊN Ô THẬT (kể cả ô vô hình giữ chỗ) chứ
     không tính lại công thức CSS — tính lại là đo chính giả định của mình. */
  const walls = [...flo.querySelectorAll('.dfw')].map(w => {
    const cells = [...w.children].map(c => {
      const r = c.getBoundingClientRect();
      return { pod: c.classList.contains('dfp'),
               empty: c.classList.contains('dfp--empty'),
               top: Math.round(r.top), bottom: Math.round(r.bottom),
               left: Math.round(r.left), right: Math.round(r.right),
               h: Math.round(r.height) };
    });
    let worstGap = 1e9, cross = 0;           // khe nhỏ nhất giữa hai ô liền nhau
    for (let i = 1; i < cells.length; i++) {
      const g = cells[i].top - cells[i - 1].bottom;
      if (g < worstGap) worstGap = g;
      if (g < 0) cross++;                    // ĐÈ NHAU — lỗi nặng nhất của bố cục này
    }
    return {
      side: w.className.indexOf('dfw--L') >= 0 ? 'L' : 'R',
      n: cells.length, cells, cross,
      gap: cells.length > 1 ? worstGap : 0,
      top: cells.length ? cells[0].top : 0,
      bottom: cells.length ? cells[cells.length - 1].bottom : 0,
      /* Chỉ số ô ĐANG CÓ MẪU VẬT. Vì `paintDesk` dựng ô theo đúng thứ tự danh
         sách móc, chỉ số này CHÍNH LÀ số thứ tự móc — nên nó chứng minh được
         "treo đúng móc trẻ chọn", không chỉ "có vẽ ra". */
      full: cells.map((c, i) => (c.pod && !c.empty) ? i : -1).filter(i => i >= 0),
      emptyAt: cells.map((c, i) => (c.pod && c.empty) ? i : -1).filter(i => i >= 0)
    };
  });

  const rs = pods.map(p => p.getBoundingClientRect());
  /* "Gan vao vach": khoang phai AP SAT mep man (mep trai cho khoang trai, mep phai
     cho khoang phai). Do bang khoang cach nho nhat toi mep tuong ung. */
  const flush = rs.length ? Math.round(Math.max(...rs.map(
    r => r.left < innerWidth / 2 ? r.left : innerWidth - r.right))) : -1;
  /* Bong benh phai o MAU VAT, khong o VO KHOANG — mot khoang bat vit vao vach ma
     tu nhun nhay la sai vat ly. */
  const animVo = pods.length ? getComputedStyle(pods[0]).animationName : '';
  const sp0 = flo.querySelector('.dfp .dp-sp');
  const animTrong = sp0 ? getComputedStyle(sp0).animationName : '';
  return {
    walls,
    layer: floOn ? 'float' : 'none', floOn, trongBang, flush, animVo, animTrong,
    n: full.length, slots: pods.length, empty: empty.length,
    loRa,
    labels: pods.map(p => p.getAttribute('title') || p.getAttribute('aria-label') || ''),
    href: pods.length > 0 && pods.every(p => (p.getAttribute('href')||'').includes('specimen-vault')),
    trap,
    size: rs.length ? Math.round(Math.min(...rs.map(r => Math.min(r.width, r.height)))) : 0,
    inView: rs.every(r => r.top >= 0 && r.bottom <= innerHeight),
    overlap: Math.round(worst), who: String(who).slice(0, 26),
    overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth)
  };
}
"""


def run(br, desk, lang="vi", w=1440, h=900, known=True):
    ctx = br.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(seed(lang))
    pg.add_init_script(stub(desk, lang, known))
    pg.goto(BASE + "/dashboard.html", wait_until="load")
    pg.wait_for_selector(".stats-hud", timeout=9000)
    pg.wait_for_timeout(1200)
    d = pg.evaluate(JS)
    d["errs"] = errs
    ctx.close()
    return d


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        print("=== [1] Man 1440 — 3 mau vat THA NOI, chi hinh ===")
        d = run(br, DESK)
        chk("dung lop THA NOI", d["layer"] == "float", d["layer"])
        chk("bang Thong Ke KHONG con dau vet nao cua hang mau vat cu",
            d["trongBang"] == 0, "%d phan tu" % d["trongBang"])
        chk("ve dung 3 khoang, 0 cho de danh",
            d["n"] == 3 and d["empty"] == 0, "%d mau / %d trong" % (d["n"], d["empty"]))
        chk("KHONG ten nao ve ra tren mat tranh", d["loRa"] == "", repr(d["loRa"])[:60])
        chk("ten VAN doc duoc bang trinh doc man hinh",
            all(x.strip() for x in d["labels"]), " · ".join(d["labels"])[:66])
        chk("khoang to (>=92px o kho nay)", d["size"] >= 92, "%dpx" % d["size"])
        chk("GAN VAO VACH: ap sat mep man", d["flush"] == 0, "%dpx" % d["flush"])
        # Chu du an: *"no bong benh nhung gan vao khung"* — hai ve, va ve thu hai chi
        # dung khi cai bong benh nam o MAU VAT chu khong o vo khoang.
        chk("vo khoang KHONG tu nhun nhay", d["animVo"] == "none", d["animVo"])
        chk("mau vat BEN TRONG thi bong benh", d["animTrong"] == "dfpFloat", d["animTrong"])
        chk("khoang la duong di that", d["href"])
        chk("KHONG to tien nao nuot `position:fixed`", d["trap"] == "", d["trap"][:40])
        chk("khong de len mot chu nao", d["overlap"] == 0,
            "de %dpx2 boi %s" % (d["overlap"], d["who"]))
        chk("ca 3 khoang nam trong khung nhin", d["inView"])
        chk("trang khong tran ngang", d["overflow"] == 0, "%dpx" % d["overflow"])
        chk("0 loi trang", not d["errs"], str(d["errs"][:1])[:90])

        # ⚠️ PHEP KIEM QUAN TRONG NHAT CUA LUOT 16/08: mau vat treo o DUNG MOC tre
        #    chon, khong phai "ve theo thu tu trong mang". DESK dat o L1/L3/R4 nen
        #    ba con so nay khac han thu tu 0,1,2 — dat mot cach rong la khong duoc.
        wl = {w["side"]: w for w in d["walls"]}
        chk("dung HAI vach", sorted(wl.keys()) == ["L", "R"], str(sorted(wl.keys())))
        chk("vach trai: mau vat o dung moc 1 va 3",
            wl["L"]["full"] == [0, 2], str(wl["L"]["full"]))
        chk("vach phai: mau vat o dung moc 4",
            wl["R"]["full"] == [3], str(wl["R"]["full"]))
        chk("moi vach du 5 o (o trong van GIU CHO)",
            wl["L"]["n"] == 5 and wl["R"]["n"] == 5,
            "L=%d R=%d" % (wl["L"]["n"], wl["R"]["n"]))
        chk("vach trai nam ben trai, vach phai nam ben phai",
            wl["L"]["cells"][0]["left"] == 0
            and wl["R"]["cells"][0]["right"] == 1440,
            "L.left=%d R.right=%d" % (wl["L"]["cells"][0]["left"],
                                      wl["R"]["cells"][0]["right"]))

        print("\n=== [2] BIET la chua trung gi — dung MOT vong de danh ===")
        d0 = run(br, [])
        chk("lop tha noi van hien", d0["layer"] == "float", d0["layer"])
        chk("dung 1 cho de danh (khong phai 3 vong rong)",
            d0["slots"] == 1 and d0["empty"] == 1,
            "%d khoang / %d trong" % (d0["slots"], d0["empty"]))
        chk("cho de danh bam duoc", d0["href"])
        chk("khong de len chu", d0["overlap"] == 0, "de %dpx2" % d0["overlap"])
        chk("0 loi trang", not d0["errs"], str(d0["errs"][:1])[:90])

        print("\n=== [2b] CHUA doc duoc server — an CA HAI lop ===")
        dn = run(br, [], known=False)
        chk("khong ve gi", dn["layer"] == "none", dn["layer"])
        chk("0 khoang", dn["slots"] == 0, "%d" % dn["slots"])

        print("\n=== [3] Ban EN — nhan tro nang phai dich ===")
        de = run(br, DESK, lang="en")
        chk("ve du 3 khoang", de["n"] == 3, "%d" % de["n"])
        chk("KHONG ten nao ve ra", de["loRa"] == "")
        chk("nhan KHAC ban tieng Viet", de["labels"] != d["labels"],
            " · ".join(de["labels"])[:66])

        print("\n=== [4] Man 1920 — le rong gap doi, khoang van khong cham chu ===")
        dw = run(br, DESK, w=1920, h=1080)
        chk("van la lop tha noi", dw["layer"] == "float")
        chk("khong de len chu", dw["overlap"] == 0, "de %dpx2" % dw["overlap"])
        chk("khong tran ngang", dw["overflow"] == 0, "%dpx" % dw["overflow"])

        # 16/08/2026: nguong ha 1280 -> 1180 (khoang toi thieu 92 -> 64px) de them
        # iPad Air NAM NGANG. Kho 1180 la cho hep nhat con lam duoc — do ra khoang
        # cach chu dung 13px.
        print("\n=== [5] Tablet nam ngang — 1366 (iPad Pro) va 1180 (iPad Air) ===")
        for w, h, ten in ((1366, 1024, "iPad Pro ngang"), (1180, 820, "iPad Air ngang")):
            dt = run(br, DESK, w=w, h=h)
            chk("%s: co hien" % ten, dt["layer"] == "float", dt["layer"])
            chk("%s: ap sat vach" % ten, dt["flush"] == 0, "%dpx" % dt["flush"])
            chk("%s: khong de len chu" % ten, dt["overlap"] == 0,
                "de %dpx2 boi %s" % (dt["overlap"], dt["who"]))
            chk("%s: khong tran ngang" % ten, dt["overflow"] == 0, "%dpx" % dt["overflow"])

        # 16/08/2026 DOI PHAT BIEU: truoc doi "lui ve hang trong bang". Chu du an da
        # bo han khoi do, nen duoi nguong KHONG hien o dau — va phep kiem phai noi
        # dung dieu do thay vi doi mot duong lui khong con ton tai.
        # ⚠️ HAI CA NAY LA CHO MAT CO Y THUC, khong phai bo sot:
        #   · 1024 (iPad mini ngang / iPad Pro DOC): le that chi 41px, khoang 64px se
        #     de len chu 23px.
        #   · 390 (dien thoai): chu du an chot *"co nhung tinh nang minh se ko the
        #     hien duoc o mobile"*.
        # Tablet DOC con mot ly do nang hon, nam o chinh buc anh: o ti le 0.75 thi
        # `object-fit:cover` chi giu 26%..74% be rong, tuc HAI COT KHUNG BUONG LAI
        # BI CAT MAT — khong co "hai ben" nao de ma gan vao.
        print("\n=== [6] Duoi nguong (1024 va dien thoai 390) — KHONG hien o dau ===")
        for w, h in ((1024, 768), (390, 844)):
            dm = run(br, DESK, w=w, h=h)
            # ⚠️ KHONG dem so nut trong DOM: duoi nguong chung van nam do, chi bi
            # `display:none`. Cau phai hoi la "co gi HIEN RA khong" — do bang khung
            # bao thuc te (phan tu `display:none` cho ra khung 0x0).
            chk("%dpx: khong co gi hien ra" % w, dm["layer"] == "none" and dm["size"] == 0,
                "%s / khung %dpx" % (dm["layer"], dm["size"]))
            chk("%dpx: bang Thong Ke van sach" % w, dm["trongBang"] == 0,
                "%d phan tu" % dm["trongBang"])
            chk("%dpx: khong tran ngang" % w, dm["overflow"] == 0, "%dpx" % dm["overflow"])

        print("\n=== [7] Mau vat la id la (server co, client chua co ten) ===")
        dx = run(br, [{"hook": "R2", "id": "mau-vat-khong-ton-tai"}])
        chk("van ve ra (khong an mat thu tre da chon)", dx["n"] == 1, "%d" % dx["n"])
        chk("con lai dung 1 cho de danh", dx["empty"] == 1, "%d" % dx["empty"])
        chk("van treo dung moc da chon du chua co ten",
            [w for w in dx["walls"] if w["side"] == "R"][0]["full"] == [1],
            str([w for w in dx["walls"] if w["side"] == "R"][0]["full"]))
        chk("0 loi trang", not dx["errs"], str(dx["errs"][:1])[:90])

        # ⚠️⚠️ MUC NAY LA SO DO DUNG SAU CON SO "5 MOC MOI VACH". Cai kep theo CHIEU
        #      CAO khung nhin (`css/dashboard.css`, bien `--dfw`) sinh ra dung de
        #      chan ca nay: mot man RONG ma THAP cho moc 148px, 5 moc + khe = 796px
        #      tren khung 720px, tuc hai moc cuoi tran ra ngoai. Do o kho rong nhat
        #      va kho THAP nhat con hien tinh nang nay.
        #      Do TREN O THAT ke ca o vo hinh giu cho — o vo hinh van chiem cho, nen
        #      chi dem `.dfp` la bo sot dung cai co the de len nhau.
        print("\n=== [8] 5 moc moi vach: khong de nhau, khong tran khung ===")
        for w, h, ten in ((1920, 1080, "Full HD"), (1600, 720, "rong ma THAP"),
                          (1440, 900, "laptop 1440"), (1366, 768, "iPad Pro ngang"),
                          (1280, 720, "laptop 1280"), (1180, 820, "iPad Air ngang")):
            dg = run(br, DESK, w=w, h=h)
            ws = dg["walls"]
            chk("%s (%dx%d): moi vach du 5 o" % (ten, w, h),
                len(ws) == 2 and all(x["n"] == 5 for x in ws),
                str([x["n"] for x in ws]))
            chk("%s: 0 cap moc DE LEN NHAU" % ten,
                all(x["cross"] == 0 for x in ws),
                "khe nho nhat %s px" % [x["gap"] for x in ws])
            chk("%s: ca cot nam trong khung nhin" % ten,
                all(x["top"] >= 0 and x["bottom"] <= h for x in ws),
                "top=%s bottom=%s / h=%d" % ([x["top"] for x in ws],
                                             [x["bottom"] for x in ws], h))
            chk("%s: khong de len chu" % ten, dg["overlap"] == 0,
                "de %dpx2 boi %s" % (dg["overlap"], dg["who"]))

        br.close()

    print("\n" + "=" * 58)
    print(f"KET QUA: {ok} dat / {bad} hong")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
