# -*- coding: utf-8 -*-
"""
smoke_checkout.py — do THAT tren Chromium: trang thanh toan `checkout.html`.

    python -m http.server 8123        (trong AstroQhtml/)
    python scratchpad/smoke_checkout.py

TRONG TAM — thu de lam mat tien / noi sai voi phu huynh:
  1. CHUA MO BAN -> KHONG co nut thanh toan nao, va noi ro la chua mo.
  2. Cong phu huynh chan truoc khi thay bat cu loi moi tra tien nao.
  3. Quay ve tu cong -> trang KHONG tin query string, phai hoi lai server.
     `?order=…&status=paid` gia mao KHONG duoc lam trang bao "da thanh toan".
  4. Body gui len KHONG chua so tien.
  5. Bam hai lan / tai lai trang -> VAN mot opId (khong tao hai don).

⚠️ Nhan cua chk() PHAI KHONG DAU — console Windows mac dinh cp1252; in chu co dau
   la UnicodeEncodeError nem GIUA LUC CHAY va bo do moi phep kiem phia sau.
"""
import json
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123").rstrip("/")
ok_n = bad_n = 0

VND_OFFERS = [
    {"plan": "astro", "cycle": "month", "currency": "VND", "amount": 99000},
    {"plan": "astro", "cycle": "year",  "currency": "VND", "amount": 790000},
    {"plan": "crew",  "cycle": "month", "currency": "VND", "amount": 169000},
    {"plan": "crew",  "cycle": "year",  "currency": "VND", "amount": 1290000},
    {"plan": "found", "cycle": "once",  "currency": "VND", "amount": 1490000},
]
USD_OFFERS = [
    {"plan": "astro", "cycle": "month", "currency": "USD", "amount": 4.99},
    {"plan": "astro", "cycle": "year",  "currency": "USD", "amount": 39.99},
]


def chk(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def seed(ctx, lang="vi", sale_open=False, order=None, checkout=None, usd=False):
    """
    Ho so trong may + ban GIA cua `window.AstroQAuth` — lop DUY NHAT ma
    checkout.html goi ra ngoai.

    ⚠️ VI SAO GIA LAP O TANG NAY chu khong chan HTTP: `startCheckout`/`getOrder` di
       qua `_authed()`, ma ham do doi mot PHIEN FIREBASE THAT. Khong dang nhap thi
       no tra ve ngay va KHONG he goi mang — nen chan HTTP la do mot loi goi khong
       bao gio xay ra, va moi phep kiem se "dat" mot cach RONG. Lan chay dau cua bo
       do nay dinh dung bay do: 9 phep kiem hong vi khong co request nao.

    ⚠️ `Object.defineProperty` co setter NUOT loi gan: `js/firebase-auth.js` la ES
       module nen no chay SAU script co dien va se ghi de ban gia neu gan thuong.
       Bay nay da ghi trong nhat ky (smoke_mission_intro.py, smoke_onboard.py).

    ⚠️ `add_init_script` gieo lai sau MOI lan dieu huong — nen ban ghi cua muc [5]
       (bam · tai lai trang · bam tiep) phai luu vao `sessionStorage` chu khong phai
       mot bien window; nguoc lai thi tai lai trang la mat sach. Cung bay do, lan
       thu tu trong du an.
    """
    cat = {"ok": True, "saleOpen": sale_open,
           "provider": "mock" if sale_open else "none",
           "currency": "USD" if usd else "VND",
           "trialDays": 14, "graceDays": 7,
           "offers": USD_OFFERS if usd else VND_OFFERS}

    ctx.add_init_script(
        "localStorage.setItem('astroq-user', JSON.stringify("
        "{name:'Test',pilotName:'Test',uid:'u-test',character:'m',avatar:'ava/avam.png'}));"
        f"localStorage.setItem('astroq-lang','{lang}');")

    ctx.add_init_script("""(() => {
      const CAT = %s, ORDER = %s, CO = %s;
      const push = b => {
        let a = [];
        try { a = JSON.parse(sessionStorage.getItem('__sent') || '[]'); } catch(e){}
        a.push(b);
        try { sessionStorage.setItem('__sent', JSON.stringify(a)); } catch(e){}
      };
      const fake = {
        getCatalog:    () => Promise.resolve({ ok:true, data:CAT }),
        startCheckout: b  => { push(b); return Promise.resolve({ ok:true, data:CO }); },
        getOrder:      () => Promise.resolve({ ok:true, data:{ ok:true, order:ORDER } }),
        getOrders:     () => Promise.resolve({ ok:true, data:{ ok:true, orders:[] } })
      };
      let v = fake;
      Object.defineProperty(window, 'AstroQAuth', {
        configurable: true, get: () => v, set: () => {}
      });
    })();""" % (json.dumps(cat),
                json.dumps(order or {}),
                json.dumps(checkout or {"ok": False, "reason": "sale-closed"})))


def seed_dead(ctx, lang="vi"):
    """Khong co AstroQAuth nao ca — do nhanh 'mat mang / API im lang'."""
    ctx.add_init_script(
        "localStorage.setItem('astroq-user', JSON.stringify("
        "{name:'Test',uid:'u-test',character:'m',avatar:'ava/avam.png'}));"
        f"localStorage.setItem('astroq-lang','{lang}');")


def sent(pg):
    return pg.evaluate("JSON.parse(sessionStorage.getItem('__sent') || '[]')")


def errors(pg):
    bag = []
    pg.on("pageerror", lambda e: bag.append(str(e)))
    pg.on("console", lambda m: bag.append(m.text) if m.type == "error" else None)
    return bag


def pass_gate(pg):
    """Giai phep tinh o cong phu huynh — doc de bai TU CHINH TRANG, khong go cung."""
    q = pg.inner_text("#gate-q")
    m = re.match(r"\s*(\d+)\s*×\s*(\d+)", q)
    assert m, f"khong doc duoc phep tinh: {q}"
    pg.fill("#gate-a", str(int(m.group(1)) * int(m.group(2))))
    pg.check("#gate-ok")
    pg.click("#gate-go")
    pg.wait_for_timeout(300)


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        BIG = {"width": 1440, "height": 1000}

        # ══════════ [1] CHUA MO BAN — trang thai THAT cua hom nay ══════════
        print("\n[1] Chua mo ban (saleOpen=false)")
        ctx = br.new_context(viewport=BIG); seed(ctx, sale_open=False)
        pg = ctx.new_page(); errs = errors(pg)
        pg.goto(f"{BASE}/checkout.html", wait_until="load")
        pg.wait_for_timeout(900)

        chk("Dai 'chua mo ban' HIEN RA THAT", pg.locator("#closed").is_visible())
        chk("Noi ro chua mo ban", "chưa mở bán" in pg.inner_text("#closed"))
        # ⚠️ Phep kiem quan trong nhat cua muc nay
        chk("KHONG co nut thanh toan nao", not pg.locator("#pay-go").is_visible())
        chk("Co duong ra that (bao khi mo cua), khong phai nut chet",
            pg.locator("#wait-go").is_visible())
        chk("Nut do dan ve form waitlist", pg.get_attribute("#wait-go", "href") == "/")
        # ⚠️ CHUA MO BAN THI KHONG BAT GIAI PHEP TINH. Cong phu huynh ton tai de
        #    khong dat mot loi chao moi tra tien truoc mat TRE (009 muc 5) — luc
        #    chua ban thi khong co loi chao moi nao de chan, nen giu no lai chi la
        #    bat bo me giai toan truoc khi duoc nhin thay cai nut duy nhat bam duoc.
        chk("KHONG bat qua cong phu huynh khi chua mo ban",
            not pg.locator("#card-gate").is_visible())
        chk("Van cho xem tom tat goi (gia von da cong khai o pricing.html)",
            pg.locator("#card-review").is_visible())
        chk("An dai 3 buoc (khong co luong thanh toan nao de chi)",
            not pg.locator("#steps").is_visible())
        chk("Ba dong 'noi that' AN khi chua mo ban (khong co gi de noi that ve)",
            not pg.locator("#terms-box").is_visible())
        chk("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # ══════════ [2] Cong phu huynh — CHI khi da mo ban ══════════
        print("\n[2] Cong phu huynh (saleOpen=true)")
        ctx = br.new_context(viewport=BIG); seed(ctx, sale_open=True)
        pg = ctx.new_page()
        pg.goto(f"{BASE}/checkout.html?plan=astro&cycle=year", wait_until="load")
        pg.wait_for_timeout(900)
        chk("Da mo ban -> cong phu huynh mo truoc", pg.locator("#card-gate").is_visible())
        chk("Chua qua cong thi CHUA thay khoi chon goi",
            not pg.locator("#card-review").is_visible())
        chk("Buoc 1 dang sang",
            "on" in (pg.get_attribute('#steps .st[data-step="gate"]', "class") or ""))
        pg.fill("#gate-a", "1")
        pg.click("#gate-go"); pg.wait_for_timeout(200)
        chk("Sai phep tinh -> bao va O LAI",
            pg.locator("#gate-err").is_visible() and pg.locator("#card-gate").is_visible())

        m = re.match(r"\s*(\d+)\s*×\s*(\d+)", pg.inner_text("#gate-q"))
        pg.fill("#gate-a", str(int(m.group(1)) * int(m.group(2))))
        pg.click("#gate-go"); pg.wait_for_timeout(200)
        chk("Dung phep tinh nhung CHUA cam ket tuoi -> VAN chan",
            pg.locator("#card-gate").is_visible())

        pg.check("#gate-ok")
        pg.click("#gate-go"); pg.wait_for_timeout(300)
        chk("Du ca hai -> qua cong", pg.locator("#card-review").is_visible())
        chk("Da mo ban -> ba dong 'noi that' HIEN RA", pg.locator("#terms-box").is_visible())
        ctx.close()

        # ══════════ [3] DA MO BAN — tom tat don ══════════
        print("\n[3] Da mo ban: tom tat don + doi chu ky")
        ctx = br.new_context(viewport=BIG)
        seed(ctx, sale_open=True,
             checkout={"ok": True,
                       "order": {"orderId": "ord_test1", "plan": "astro", "cycle": "year",
                                 "currency": "VND", "amount": 790000, "status": "pending"},
                       "payUrl": "http://127.0.0.1:8123/checkout.html?order=ord_test1",
                       "trialDays": 14})
        pg = ctx.new_page(); errs = errors(pg)
        pg.goto(f"{BASE}/checkout.html?plan=astro&cycle=year", wait_until="load")
        pg.wait_for_timeout(900); pass_gate(pg)

        chk("KHONG con dai 'chua mo ban'", not pg.locator("#closed").is_visible())
        chk("Co nut thanh toan", pg.locator("#pay-go").is_visible())
        chk("Ten goi dung", "Phi Hành Gia" in pg.inner_text("#sum-name"))
        chk("Gia hien la 790.000₫ (so cua SERVER)", "790.000₫" in pg.inner_text("#sum-total"),
            pg.inner_text("#sum-total"))
        # ⚠️ `trialDays` phai den TU SERVER — go 14 vao client la mot ban sao cua mot
        #    con so ve TIEN; ngay doi thoi gian dung thu thi trang noi sai ngay thu.
        chk("Dung thu 14 ngay (server tra)", "14" in pg.inner_text("#sum-trial"),
            pg.inner_text("#sum-trial"))
        chk("Co ngay thu dau tien (khong de trong)",
            pg.inner_text("#sum-first").strip() not in ("", "—"), pg.inner_text("#sum-first"))
        # 009 muc 6: ghi ro chu ky + ngay thu + cach huy NGAY TAI cho mua
        tb = pg.inner_text("#terms-box")
        chk("Noi ro: hom nay chua tru tien", "chưa trừ tiền" in tb)
        chk("Noi ro: sau do thu bao nhieu, moi bao lau", "790.000₫" in tb and "năm" in tb)
        chk("Noi ro: huy the nao", "uỷ" in tb)

        pg.click('.co-cyc[data-cycle="month"]'); pg.wait_for_timeout(250)
        chk("Doi chu ky -> gia doi theo", "99.000₫" in pg.inner_text("#sum-total"),
            pg.inner_text("#sum-total"))
        chk("Goi nam co nhan tiet kiem %", "%" in pg.inner_text('.co-cyc[data-cycle="year"]'))
        pg.click('.co-cyc[data-cycle="year"]'); pg.wait_for_timeout(250)

        # ══════════ [4] Body gui len server ══════════
        print("\n[4] Body gui len server")
        pg.click("#pay-go"); pg.wait_for_timeout(700)
        body = (sent(pg) or [{}])[0]
        chk("Co gui plan + cycle", body.get("plan") == "astro" and body.get("cycle") == "year",
            str(body))
        # ⚠️ CHOT CHAN QUAN TRONG NHAT: cho client gui so tien la ai cung mua goi nam
        #    bang 1d. Cung bai hoc da ghi o `Wallet.Fees`.
        chk("KHONG gui so tien len",
            not any(k.lower() in ("amount", "price", "total") for k in body), str(list(body)))
        chk("Co opId de chong tao hai don", len(str(body.get("opId") or "")) >= 6,
            str(body.get("opId")))
        chk("Co returnUrl tro ve chinh trang nay",
            "checkout.html" in (body.get("returnUrl") or ""), str(body.get("returnUrl")))
        chk("0 loi console", not errs, str(errs[:2]))
        ctx.close()

        # ══════════ [5] Bam hai lan / tai lai trang -> MOT opId ══════════
        print("\n[5] Bam hai lan / tai lai trang -> VAN mot opId")
        ctx = br.new_context(viewport=BIG)
        # Cong bao hong -> o lai trang, bam duoc tiep
        seed(ctx, sale_open=True, checkout={"ok": False, "reason": "provider-error"})
        pg = ctx.new_page()
        pg.goto(f"{BASE}/checkout.html?plan=crew&cycle=month", wait_until="load")
        pg.wait_for_timeout(900); pass_gate(pg)
        pg.click("#pay-go"); pg.wait_for_timeout(500)
        pg.click("#pay-go"); pg.wait_for_timeout(500)
        pg.reload(wait_until="load"); pg.wait_for_timeout(900)
        pg.click("#pay-go"); pg.wait_for_timeout(500)
        ops = [b.get("opId") for b in sent(pg)]
        chk("3 luot bam (co ca sau khi tai lai) dung MOT opId",
            len(ops) >= 3 and len(set(ops)) == 1, str(ops))
        ctx.close()

        # ══════════ [6] Quay ve tu cong ══════════
        print("\n[6] Quay ve tu cong — trang KHONG tin query string")
        # ⚠️ PHEP KIEM QUAN TRONG NHAT CA BO: URL noi "paid" nhung SERVER noi
        #    "pending" -> trang PHAI theo server. URL quay ve la thu ai cung go lai
        #    duoc, tin no la mo goi mien phi cho bat cu ai biet dan mot dia chi.
        ctx = br.new_context(viewport=BIG)
        seed(ctx, sale_open=True,
             order={"orderId": "ord_x", "plan": "astro", "cycle": "year",
                    "currency": "VND", "amount": 790000, "status": "pending"})
        pg = ctx.new_page()
        pg.goto(f"{BASE}/checkout.html?order=ord_x&status=paid&success=1", wait_until="load")
        pg.wait_for_timeout(1200)
        chk("URL noi 'paid' nhung trang KHONG bao da xong",
            not pg.locator("#res-ok").is_visible())
        chk("Hien 'dang xac nhan' theo dung trang thai server",
            pg.locator("#res-wait").is_visible())
        ctx.close()

        ctx = br.new_context(viewport=BIG)
        seed(ctx, sale_open=True,
             order={"orderId": "ord_y", "plan": "astro", "cycle": "year",
                    "currency": "VND", "amount": 790000, "status": "paid",
                    "paidAt": "2026-08-11T10:00:00Z"})
        pg = ctx.new_page()
        pg.goto(f"{BASE}/checkout.html?order=ord_y", wait_until="load")
        pg.wait_for_timeout(1200)
        chk("Server noi paid -> bao da kich hoat", pg.locator("#res-ok").is_visible())
        chk("Co duong di tiep", pg.locator("#res-acts a").count() >= 1,
            str(pg.locator("#res-acts a").count()))
        ctx.close()

        ctx = br.new_context(viewport=BIG)
        seed(ctx, sale_open=True,
             order={"orderId": "ord_z", "plan": "crew", "cycle": "month",
                    "currency": "VND", "amount": 169000, "status": "cancelled"})
        pg = ctx.new_page()
        pg.goto(f"{BASE}/checkout.html?order=ord_z", wait_until="load")
        pg.wait_for_timeout(1200)
        txt = pg.inner_text("#res-bad")
        chk("Huy giua chung -> noi ro CHUA TRU TIEN", "chưa có khoản nào bị trừ" in txt.lower(),
            txt.replace("\n", " ")[:70])
        # ⚠️ Ho phach chu KHONG do choi: day la trang bo me dang lo ve tien cua minh,
        #    do doc ra thanh "da mat tien" trong khi phan lon ca la chua tru gi.
        bc = pg.evaluate("getComputedStyle(document.getElementById('res-bad')).borderTopColor")
        chk("To ho phach, khong to do", "255, 207" in bc, bc)
        chk("Co nut thu lai", pg.locator("#res-acts a").count() >= 1)
        ctx.close()

        # ══════════ [7] Ban EN + dien thoai ══════════
        print("\n[7] Ban EN va dien thoai")
        ctx = br.new_context(viewport=BIG); seed(ctx, "en", sale_open=True, usd=True)
        pg = ctx.new_page()
        pg.goto(f"{BASE}/checkout.html?plan=astro&cycle=year", wait_until="load")
        pg.wait_for_timeout(900)
        chk("EN: cong phu huynh dich", "grown-up" in pg.inner_text("#card-gate").lower())
        pass_gate(pg)
        chk("EN: hien USD", "$39.99" in pg.inner_text("#sum-total"), pg.inner_text("#sum-total"))
        chk("EN: KHONG con VND", "₫" not in pg.inner_text("#summary"))
        pg.click('.lang-switch button[data-lang="vi"]'); pg.wait_for_timeout(400)
        chk("Doi sang VI giua chung -> tom tat dich theo",
            "Phi Hành Gia" in pg.inner_text("#sum-name"))
        ctx.close()

        ctx = br.new_context(viewport={"width": 390, "height": 844})
        seed(ctx, sale_open=True)
        pg = ctx.new_page(); errs = errors(pg)
        pg.goto(f"{BASE}/checkout.html?plan=crew&cycle=year", wait_until="load")
        pg.wait_for_timeout(900); pass_gate(pg)
        ow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        chk("Dien thoai 390px: khong tran ngang", ow <= 0, f"tran {ow}px")
        bb = pg.locator("#pay-go").bounding_box()
        chk("Nut thanh toan >= 44px", bb and bb["height"] >= 44,
            f'{bb["height"]:.0f}px' if bb else "?")
        chk("0 loi console tren dien thoai", not errs, str(errs[:2]))
        ctx.close()

        # ══════════ [8] API im lang ══════════
        print("\n[8] API im lang / chua dang nhap")
        ctx = br.new_context(viewport=BIG); seed_dead(ctx)
        pg = ctx.new_page()
        pg.route("**/billing/**", lambda r: r.abort())
        pg.goto(f"{BASE}/checkout.html?plan=astro&cycle=year", wait_until="load")
        pg.wait_for_timeout(4200)   # `auth()` cho toi 3 giay roi moi ket luan
        # ⚠️ Khong doc duoc trang thai ban -> NGHIENG VE PHIA DONG. Mo mot nut thanh
        #    toan ma chua chac ban duoc la huong nghieng sai.
        chk("KHONG hien nut thanh toan", not pg.locator("#pay-go").is_visible())
        chk("Van noi ro chua mo ban", pg.locator("#closed").is_visible())
        chk("Trang khong vo (van ve ra khoi tom tat don)",
            pg.locator("#card-review").is_visible())
        ctx.close()

        br.close()

    print(f"\n=== KET QUA: {ok_n} dat / {bad_n} hong ===")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
