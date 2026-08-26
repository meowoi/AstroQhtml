# -*- coding: utf-8 -*-
"""
PROBE B — quả cầu Trái Đất ở explorer.html có ranh giới ngày/đêm ĐỌC ĐƯỢC không?

`005` chốt dạy ngày/đêm trên quả cầu 3D. Mã cho thấy cơ chế ĐÚNG:
  · MeshStandardMaterial (explorer.html:1138) -> an sang that
  · PointLight(0xfff0d0, 3.4, 0, 0.12) gan VAO chinh this.sun (:1322)
Nhung cung co nhieu anh sang NEN:
  · AmbientLight(0x8090c0, 0.55)   (:1323)
  · HemisphereLight(0x9fb8ff, 0x101838, 0.35)  (:1324)
=> Gia thuyet phai kiem: nen ~0,9 lam SANG CA NUA TOI, ranh gioi nhat, va cau
   "em thay nua toi chua?" thanh loi hua suong.

Do gi: quet mot dai ngang qua dia hanh tinh, tim bien dia, roi so do sang nua
sang vs nua toi. KHONG doc code roi ket luan.

Chay:  PYTHONIOENCODING=utf-8 python scratchpad/probe_globe_daynight.py
       (tu dung server o cong 8143 — khong can chay `http.server` truoc)

Nhan print KHONG DAU (console Windows cp1252).
"""
import http.server
import io
import os
import socketserver
import sys
import threading
from playwright.sync_api import sync_playwright
from PIL import Image

# ⚠️⚠️ TU DUNG SERVER, DUNG DOI NGUOI CHAY `python -m http.server` TRUOC. Truoc day
#    bo do nay ghi trong huong dan la "chay server o cong 8123 roi chay toi" — mot
#    bo do phu thuoc vao viec nguoi ta nho lam mot buoc thu cong thi som muon se bi
#    chay khi khong co server, va luc do no bao HONG oan (goto that bai -> check
#    false -> exit 1) chu khong noi "thieu server". Nay no tu mo cong rieng, nen
#    dua vao cong day du duoc.
PORT = 8143
BASE = "http://127.0.0.1:%d" % PORT
PASS = 0
FAIL = 0


def check(label, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print("   [OK]   " + label + ("  " + detail if detail else ""))
    else:
        FAIL += 1
        print("   [HONG] " + label + ("  " + detail if detail else ""))


def lum(px):
    return 0.2126 * px[0] + 0.7152 * px[1] + 0.0722 * px[2]


def find_disc(im, box, thr=55.0):
    """
    Tim dia HANH TINH bang cach quet CA VUNG, khong quet mot hang.

    ⚠️ Ban dau probe nay quet DUNG MOT hang ngang qua vi tri nhan ten, ra "dia"
       rong 759px voi moi gia tri 12-54 — tuc no do NEN TROI, khong do hanh tinh.
       Nhan ten nam PHIA TREN hanh tinh, va nguong 12 thi sao nen cung vuot.
       Chi nhin anh chup moi thay. Nen: nguong 55 + tim vung lien thong.

    Tra ve (cx, cy, r, diem[]) — diem la list (x, y, lum) ben trong dia.
    """
    x0, y0, x1, y1 = box
    pts = []
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            L = lum(im.getpixel((x, y)))
            if L >= thr:
                pts.append((x, y, L))
    if len(pts) < 200:
        return None
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    # ban kinh = phan vi 92% khoang cach toi tam (bo duoi cac diem le nhu nhan/mat trang)
    d = sorted(((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5 for p in pts)
    r = d[int(len(d) * 0.92)]
    inside = [p for p in pts
              if ((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5 <= r * 0.93]
    return (cx, cy, r, inside)


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900},
                             device_scale_factor=1)
        ctx.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        print("\n== nap explorer.html (three.js tu unpkg — can mang) ==")
        pg.goto(BASE + "/explorer.html", wait_until="domcontentloaded")
        try:
            pg.wait_for_function("() => window.__solarReady === true", timeout=45000)
        except Exception as e:
            check("canh 3D dung xong (__solarReady)", False,
                  "het han 45s — kiem mang / unpkg.com. " + str(e)[:120])
            print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
            return 1
        check("canh 3D dung xong (__solarReady)", True)

        # ⚠️ #loader co transition .8s va tung NUOT CU BAM (bai hoc 31/07/2026).
        #    Cho no thuc su khong con nhan chuot.
        pg.wait_for_timeout(3200)

        # Chon Trai Dat bang chinh nhan tren ban do — dung duong nguoi dung di.
        lbl = pg.query_selector('#labels [data-body-id="earth"]')
        check("tim thay nhan Trai Dat tren ban do", lbl is not None)
        if lbl is None:
            print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
            return 1
        # ⚠️⚠️ CU BAM VAO NHAN TREN BAN DO GAN NHU LUON THAT BAI, VA LY DO KHONG PHAI
        #    "BI CHE". Ban dau o day ghi la nhan bi nhan hanh tinh khac de len — that
        #    ra hom 25/08/2026 co MOT lan Playwright bao dung the ("<div class=body-lbl
        #    ...>Sao Kim</div> intercepts pointer events"), va tu do suy ra nguyen nhan
        #    cho MOI lan. Do lai moi thay suy the la sai: `scratchpad/probe_label_overlap.py`
        #    hoi `elementFromPoint` o chinh tam nhan Trai Dat, 6 luot × 2 loai tre, va
        #    lan nao phan tu tren cung CUNG LA chinh nhan do — tuc tam nhan BAM DUOC.
        #    Nguyen nhan that in ra o dong duoi day; giu nguyen van loi cua Playwright
        #    thay vi doan, vi day dung la cho da doan sai mot lan.
        #    ⛔ KHONG chua bang `force=True`: neu that su co luc bi nhan khac de, cu bam
        #       do se chon SAI hanh tinh va bo do van bao "dat" — te hon han mot lan chet.
        #    Duong lui la BANG TRAI: `selectBody` co 6 duong vao (CLAUDE.md 01/08),
        #    va muc trong bang trai la mot `<button>` that, dung yen, khong bi che.
        used = "nhan tren ban do"
        why = ""
        try:
            lbl.click(timeout=6000)
        except Exception as e:
            why = " ".join(str(e).split())[:150]
            used = "muc Trai Dat o bang trai (bam nhan tren ban do that bai)"
            it = pg.query_selector('.loc-item[data-body-id="earth"]') \
                or pg.query_selector('#deck .loc-item:has-text("Trái Đất")')
            if it is None:
                check("chon duoc Trai Dat (nhan bi che, bang trai cung khong thay)",
                      False)
                print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
                return 1
            it.click(timeout=6000)
        # ⚠️ IN RA duong nao da dung — doi duong am tham thi lan sau khong ai biet
        #    con so do duoc do o ngu canh nao.
        print("      chon Trai Dat qua: %s" % used)
        if why:
            print("      ly do Playwright bo cu bam nhan: %s" % why)
        # Camera bay ~1,6s roi bang thong tin moi mo (map-onboard.js ghi vay).
        pg.wait_for_timeout(3000)

        pos = pg.evaluate("""() => {
            const l = document.querySelector('#labels [data-body-id="earth"]');
            const r = l.getBoundingClientRect();
            return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};
        }""")
        print("      nhan Trai Dat o (%d, %d)" % (pos["x"], pos["y"]))

        shot = pg.screenshot()
        im = Image.open(io.BytesIO(shot)).convert("RGB")
        im.save("scratchpad/globe-daynight-1440.png")
        print("      da luu scratchpad/globe-daynight-1440.png")

        # Chi do vung GIUA: bang trai (~x<380) va bang thong tin (~x>1010) khong
        # phai canh 3D. Doc be rong that tu DOM chu khong gan cung.
        bounds = pg.evaluate("""() => {
            const deck = document.getElementById('deck');
            const info = document.getElementById('info');
            const dr = deck ? deck.getBoundingClientRect().right : 0;
            const il = info ? info.getBoundingClientRect().left : window.innerWidth;
            return {left: Math.round(dr) + 12, right: Math.round(il) - 12,
                    h: window.innerHeight};
        }""")
        box = (max(0, bounds["left"]), 60,
               min(im.size[0], bounds["right"]), min(im.size[1], bounds["h"] - 80))
        print("      vung do canh 3D: x %d..%d  y %d..%d"
              % (box[0], box[2], box[1], box[3]))

        disc = find_disc(im, box)
        if disc is None:
            check("tim thay dia hanh tinh tren anh chup", False,
                  "khong du diem sang >= 55 trong vung canh 3D")
            print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
            return 1
        cx, cy, r, inside = disc
        check("tim thay dia hanh tinh tren anh chup", r >= 25,
              "tam (%.0f, %.0f)  ban kinh %.0f px  %d diem do"
              % (cx, cy, r, len(inside)))

        vals = sorted(p[2] for p in inside)
        n = len(vals)
        mean_all = sum(vals) / n
        vmax, vmin = vals[-1], vals[0]
        # Decile: 10% sang nhat vs 10% toi nhat — ben vung hon max/min don le
        d_hi = sum(vals[int(n * 0.9):]) / max(1, n - int(n * 0.9))
        d_lo = sum(vals[:max(1, int(n * 0.1))]) / max(1, int(n * 0.1))
        contrast = d_hi - d_lo
        ratio = (d_hi / d_lo) if d_lo > 0.5 else 999.0

        print("      dia: TB %.1f | max %.1f | min %.1f" % (mean_all, vmax, vmin))
        print("      decile sang nhat %.1f  vs  decile toi nhat %.1f  -> chenh %.1f"
              % (d_hi, d_lo, contrast))

        # 8 khu vuc quanh tam -> lo ra HUONG cua ranh gioi ngay/dem
        import math
        print("      do sang theo 8 huong quanh tam (lo ra huong ranh gioi):")
        for k in range(8):
            a0, a1 = k * math.pi / 4, (k + 1) * math.pi / 4
            seg = [p[2] for p in inside
                   if a0 <= (math.atan2(p[1] - cy, p[0] - cx) % (2 * math.pi)) < a1]
            if seg:
                print("        huong %d (%3d-%3d do): TB %.1f  (%d diem)"
                      % (k + 1, int(math.degrees(a0)), int(math.degrees(a1)),
                         sum(seg) / len(seg), len(seg)))

        # NGUONG: hai nua phai chenh du de MAT tre nhan ra. Lay 25 diem do sang
        # (~10% thang 255) lam moc "nhin thay ro". Duoi 12 diem la khong doc duoc.
        check("hai nua dia chenh >= 25 diem do sang (ranh gioi doc duoc)",
              contrast >= 25.0, "chenh do duoc %.1f" % contrast)
        check("hai nua dia chenh >= 12 diem (toi thieu nhan ra duoc)",
              contrast >= 12.0, "chenh do duoc %.1f" % contrast)
        # ⚠️⚠️ PHEP KIEM CU O DAY LA `vmin < 40` VA NO CHUA BAO GIO DAT — do lai
        #    25/08/2026 tren CA ban HEAD thi `min` deu ra dung 55.0. Hai cai sai:
        #      · no doc MOT pixel toi nhat, trong khi chinh file nay da ghi ngay
        #        tren rang "decile ben vung hon max/min don le" — hai phep kiem
        #        chenh lech thi dung decile, rieng no thi khong;
        #      · nguong 40 la mot con so tuyet doi, ma vanh khi quyen + anh sang moi
        #        truong lam pixel toi nhat TRONG dia khong bao gio xuong duoi ~55.
        #    Va no lam bo do "bao oan" moi luot chay, tuc som muon nguoi ta bo qua.
        #    ⇒ DOI PHAT BIEU sang TI SO decile — dung y "co nua toi that", nhung
        #      BAT BIEN theo do phong/khung nhin (do duoc: chenh dao dong 101–171
        #      diem giua cac luot vi hanh tinh dang bay, con ti so thi 2,58–3,43).
        #    ⚠️ KHONG PHAI NOI LONG: ti so la phep kiem MOI, va no bat duoc dung ca
        #       hong that ma `vmin < 40` nham vao — anh sang moi truong bi keo len
        #       den muc hai nua bang nhau thi ti so -> 1.
        #    Moc 2,0 lay tu so do thap nhat (2,58) tru bien; ghi chu 02/08/2026 ghi
        #    "ti so 2,94x" va chot "khong can chinh den", tuc san pham o muc nay la
        #    muc DA DUOC DUYET.
        check("nua toi TOI HON nua sang it nhat 2 lan (ti so decile)",
              ratio >= 2.0, "ti so do duoc %.2f" % ratio)
        # In `min` de tham khao, KHONG lam phep kiem — xem ly do ngay tren.
        print("      ti so decile sang/toi = %.2f | pixel toi nhat %.1f (chi tham khao)"
              % (ratio, vmin))

        check("0 loi console/pageerror", len(errs) == 0, "; ".join(errs[:2]))
        ctx.close()
        br.close()

    print("\nKET QUA: %d dat / %d hong" % (PASS, FAIL))
    return 1 if FAIL else 0


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    socketserver.TCPServer.allow_reuse_address = True
    _srv = socketserver.TCPServer(("", PORT), _Quiet)
    threading.Thread(target=_srv.serve_forever, daemon=True).start()
    try:
        _rc = main()
    finally:
        _srv.shutdown()
    sys.exit(_rc)
