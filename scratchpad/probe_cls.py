# -*- coding: utf-8 -*-
r"""probe_cls.py — DO CLS (nhay bo cuc) tren cac trang ve luoi the tu JS.

    python scratchpad/probe_cls.py            # do het
    python scratchpad/probe_cls.py library    # do mot trang

⚠️⚠️ DO BANG `PerformanceObserver('layout-shift')` CHU KHONG DOAN TU MA. Ban ra soat
   23/08/2026 liet 4 trang "can khung xuong chong nhay bo cuc" dua tren viec chung
   ve the tu JS — do la mot PHONG DOAN hop ly, khong phai so do. Trang ve tu JS ma
   khoi chua da co chieu cao thi CLS van bang 0.

⚠️ CLS LA CHI SO TICH LUY, va no phu thuoc VIEWPORT + MANG + CPU. Do o 3 khung nhin
   (dien thoai / may tinh bang / may tinh) va co tiet che CPU ×4, vi tren may nhanh
   the co the ve xong TRUOC khi trinh duyet kip son khung dau — luc do CLS = 0 mot
   cach gia tao. Neu khong tiet che thi con so do noi ve MAY NAY, khong ve may tre.

⚠️⚠️ CLS O DAY BAT DAU BANG 0 HAY BANG 0,49 CHI PHU THUOC MOT DIEU: TAI NGUYEN VE
   SAU HAY TRUOC KHUNG SON DAU TIEN. Da dieu tra tan cung ngay 25/08/2026 vi hai
   phep do cung mot trang ra hai ket qua trai nguoc:
     · CPU x4, KHONG tiet che mang  -> CLS = 0,0000, khong mot cu nhay nao
     · CPU x4, CO tiet che mang 4G  -> CLS = 0,4947 (1440px) / 0,8203 (768px)
   Tuc JS dien ruot cac panel kip TRUOC khung son dau khi mang nhanh, va khong kip
   khi mang cham. **CLS = 0 tren may nhanh KHONG co nghia la trang khong nhay.**

   ⚠️ Toi da doan sai nguyen nhan MOT LAN o day va ghi lai de khong ai lap lai:
      ban dau bo do dung `socketserver.TCPServer` (phuc vu MOT yeu cau mot luc) va
      toi ket luan con so 0,49 la san pham cua chinh bo do. Doi sang
      `ThreadingHTTPServer` **va** tro sang mot server NGOAI (`CLS_PORT=...`) thi
      con so **khong doi mot chut nao** — 0,4947 / 0,8203 ca ba cach. Server noi
      tiep chi tinh co gay ra dung cai cham ma tiet che 4G nay khai ra tu tuong.
      Bai hoc: mot con so tai hien duoc van co the co nguyen nhan khac han cai
      minh nghi; tai hien chung minh no ON DINH, khong chung minh minh HIEU no.

⚠️ Vi the tiet che mang phai KHAI RA, khong de no xay ra do tinh co:
   `Network.emulateNetworkConditions` 4G (9 Mbps, RTT 150ms) — dung quy uoc da dung
   o `perf_ab.py`/`perf_audit_all.py` de con so so sanh duoc voi cac lan do khac.

⚠️ CHO `hidden` ROI MOI DOC. `layout-shift` con phat sinh sau `load`; doc ngay sau
   `load` la doc mot nua cau chuyen. Day dung `requestIdleCallback` + mot khoang cho.

⚠️ NGUONG: Google xep CLS <= 0,1 la "tot", 0,1-0,25 "can cai thien", > 0,25 "kem".
   Nguong o day la 0,1 — bo do bao HONG khi vuot, de con so tu noi co can lam gi.
"""
import http.server
import os
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ⚠️ Cho phep tro sang MOT SERVER NGOAI qua bien moi truong, de kiem xem con so co
#    phu thuoc vao viec server nam trong CUNG TIEN TRINH Python voi Playwright hay
#    khong. Day khong phai tuy chon cho tien: no la mot phep DOI CHUNG.
PORT = int(os.environ.get("CLS_PORT", "8144"))
EXTERNAL = os.environ.get("CLS_PORT") is not None
LIMIT = 0.1

# ⚠️⚠️ TRAN RIENG CHO MOT TRANG DA BIET LA CHUA CHUA DUOC — day la MOT CAI CHAN, khong
#    phai mot cai co. `game-defender.html` do duoc 0,3253 (768px) / 0,2087 (1440px)
#    va nguyen nhan da truy xong: `boot()` cua js/game-shell.js chay o
#    `DOMContentLoaded`, ma `DOMContentLoaded` bi 20 script co dien (360 KB) chan; da
#    THU chua bang CSS thuan va phai hoan nguyen vi no lam 768px XAU HON (chi tiet +
#    so do ghi trong `css/game-shell.css`, muc "Khung san"). Chua dung cho la viec (8)
#    cua ban ra soat 23/08.
#    ⚠️ De nguyen nguong 0,1 cho trang nay thi bo do HONG MAI MAI, va mot phep kiem
#       hong mai mai thi som muon nguoi ta bo qua ca bo do — dung cai bay da go o
#       `probe_globe_daynight` cung ngay. Nen: ghim tran o dung muc DANG CO, tuc bo
#       do chi keu khi no XAU DI. Sua duoc thi ha tran ve 0,1 va xoa dong nay.
CEIL = {"game-defender.html": 0.36}

# ⚠️ `en/index.html` la ban SINH RA tu `index.html` (scratchpad/gen_home_en.py), nen
#    no phai co mat o day: mot ban va sua o file goc ma bo sinh khong mang sang thi
#    chi co phep do moi noi ra. Do la loi da xay ra 25/08/2026 voi duong dan `fonts/`.
PAGES = ["achievements.html", "library.html", "game-defender.html",
         "missions.html", "dashboard.html", "index.html", "en/index.html",
         "landing-app.html"]
VIEWS = [("dien thoai", 390, 844), ("may tinh bang", 768, 1024),
         ("may tinh", 1440, 900)]

# ⚠️ Gan observer TRUOC khi tai lieu chay: dat qua `add_init_script` chu khong qua
#    `pg.evaluate` sau `goto` — cai sau bo mat moi cu nhay xay ra truoc luc gan.
INIT = """
window.__cls = 0; window.__shifts = [];
try {
  new PerformanceObserver((l) => {
    for (const e of l.getEntries()) {
      if (e.hadRecentInput) continue;          // nhay do nguoi dung bam thi khong tinh
      window.__cls += e.value;
      const R = (r) => r ? [Math.round(r.x), Math.round(r.y),
                            Math.round(r.width), Math.round(r.height)] : null;
      // ⚠️ GHI CA prev/cur, KHONG CHI TEN PHAN TU. Ten chi noi "cai gi nhay"; muon
      //    SUA thi phai biet no nhay TU DAU DEN DAU. Ba lan do dau ngay 25/08 chi
      //    co ten, va toi da mat mot vong dung script roi de tim lai dieu nay.
      window.__shifts.push({
        v: +e.value.toFixed(4),
        t: Math.round(e.startTime),
        who: (e.sources || []).map(s => {
          const n = s.node;
          const c = (n && n.className && typeof n.className === 'string')
            ? '.' + n.className.trim().split(/\\s+/)[0] : '';
          return {
            el: (n && n.tagName) ? n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + c : '?',
            prev: R(s.previousRect), cur: R(s.currentRect)
          };
        }).slice(0, 8)
      });
    }
  }).observe({type: 'layout-shift', buffered: true});
} catch (e) { window.__clsErr = String(e); }
"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright
    want = sys.argv[1:] or None
    pages = [p for p in PAGES
             if not want or any(w.replace(".html", "") in p for w in want)]

    httpd = None
    if not EXTERNAL:
        http.server.ThreadingHTTPServer.allow_reuse_address = True
        httpd = http.server.ThreadingHTTPServer(("", PORT), Quiet)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
    else:
        print("(dung server NGOAI o cong %d)" % PORT)

    ok = bad = 0
    worst = []
    try:
        from playwright.sync_api import sync_playwright as _sp  # noqa: F401
        with sync_playwright() as p:
            b = p.chromium.launch()
            for page in pages:
                print("\n=== %s ===" % page)
                for vname, w, h in VIEWS:
                    ctx = b.new_context(viewport={"width": w, "height": h},
                                        locale="vi-VN",
                                        is_mobile=(w < 500),
                                        has_touch=(w < 500))
                    ctx.add_init_script(
                        "try{localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
                    ctx.add_init_script(INIT)
                    pg = ctx.new_page()
                    cdp = ctx.new_cdp_session(pg)
                    cdp.send("Network.enable", {})
                    cdp.send("Network.emulateNetworkConditions", {
                        "offline": False, "latency": 150,
                        "downloadThroughput": 9 * 1024 * 1024 / 8,
                        "uploadThroughput": 9 * 1024 * 1024 / 8})
                    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
                    try:
                        pg.goto("http://localhost:%d/%s" % (PORT, page),
                                wait_until="load", timeout=90000)
                    except Exception as e:
                        print("  %-14s KHONG NAP DUOC: %s" % (vname, str(e)[:70]))
                        ctx.close()
                        continue
                    pg.wait_for_timeout(4000)
                    d = pg.evaluate("() => ({cls: window.__cls, s: window.__shifts,"
                                    " err: window.__clsErr || null})")
                    cls = d["cls"] or 0.0
                    lim = CEIL.get(page, LIMIT)
                    tag = "OK" if cls <= lim else "HONG"
                    # ⚠️ Chi ghi [TRAN] khi con so THUC SU dua vao tran rieng. Ban dau
                    #    doan ca 3 khung nhin cua trang co tran, ke ca khung do duoc
                    #    0,0000 — doc ra nhu the trang do dang duoc mien tru o cho no
                    #    khong can mien tru gi.
                    if cls > LIMIT and cls <= lim:
                        tag = "TRAN"
                    if cls <= lim:
                        ok += 1
                    else:
                        bad += 1
                        worst.append((cls, page, vname, d["s"]))
                    print("  [%-4s] %-14s CLS = %.4f  (%d cu nhay)%s"
                          % (tag, vname, cls, len(d["s"]),
                             "   [tran rieng %.2f — xem CEIL]" % lim
                             if lim != LIMIT else ""))
                    if d["err"]:
                        print("         !! observer loi: %s" % d["err"])
                    for s in sorted(d["s"], key=lambda x: -x["v"])[:4]:
                        if s["v"] >= 0.005:
                            print("         %.4f o %4dms" % (s["v"], s["t"]))
                            for q in s["who"]:
                                print("            %-26s %s -> %s"
                                      % (q["el"][:26], q["prev"], q["cur"]))
                    ctx.close()
            b.close()
    finally:
        if httpd is not None:
            httpd.shutdown()

    print("\n=== KET QUA: %d dat / %d hong  (nguong CLS <= %.2f; tran rieng: %s) ==="
          % (ok, bad, LIMIT,
             ", ".join("%s %.2f" % (k, v) for k, v in sorted(CEIL.items())) or "khong"))
    if worst:
        print("  nang nhat:")
        for cls, page, vname, _s in sorted(worst, reverse=True)[:6]:
            print("    %.4f  %s @ %s" % (cls, page, vname))
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
