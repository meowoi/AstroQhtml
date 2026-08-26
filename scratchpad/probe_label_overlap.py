# -*- coding: utf-8 -*-
r"""probe_label_overlap.py — NHAN THIEN THE O `explorer.html` CO BI CHE KHONG?
Do bang `elementFromPoint` tai TAM tung nhan, khong doc CSS.

    python scratchpad/probe_label_overlap.py

⚠️⚠️ VI SAO CAN. Viec treo tu 02/08/2026 (`docs/decisions/005` muc 1: *"nhan Mat
   Trang de nhan Trai Dat"*) chua ai DO ra con so. Bo do nay do, va truoc khi sua:
   **6/6 luot** co nhan bi nhan khac de o chinh tam — `earth` 3/6, `moon` 3/6,
   khong luot nao ca hai (chung THAY NHAU de, tuy cai nao giành duoc `z-index`).
   Hau qua: tre bam vao giua chu "Mat Trang" thi `selectBody` mo ra Trai Dat.

⚠️ DUNG LAY `probe_globe_daynight.py` LAM BANG CHUNG cho loi nay. Bo do do phai di
   duong lui vi Playwright doi *"element to be visible, enabled and stable"* ma
   nhan thi bam theo hanh tinh nen khong bao gio dung yen — mot rang buoc cua BO
   DO, khong phai cua san pham. Toi da tung viet nguoc lai o day va do lai thi sai.

⚠️ DO BANG `elementFromPoint`, KHONG DOC `z-index` HAY KHUNG BAO. Hai nhan long
   nhau tren giay van co the khong chan nhau (phan giao roi vao cho trong), va
   nguoc lai. Chi phep hoi "tai diem nay, phan tu TREN CUNG la ai" moi tra loi
   duoc cau *"tre bam vao day thi trung cai gi"*. `elementFromPoint` cung bo qua
   phan tu co `pointer-events:none` — dung nhu cu bam that, nen `#labels` (lop
   chua, khong nhan chuot) khong bi tinh oan.

⚠️ GHI CA PHAN TU TREN CUNG, KHONG CHI THIEN THE SO HUU NO. Nhan bi NHAN KHAC de
   la mot loi; nhan bi BANG TRAI hay khung tin che la loi KHAC — hai loi do sua o
   hai cho khac nhau, nen bo do phai phan biet duoc chung.

⚠️ NHAN BAM THEO HANH TINH TUNG KHUNG HINH (`CSS2DRenderer`), nen ket qua DOI theo
   thoi diem chay. Bo do vi the chay NHIEU LUOT roi bao ca khoang, khong bao mot
   con so don le roi noi nhu the no co dinh.
"""
import http.server
import os
import socketserver
import sys
import threading

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PORT = 8139
ROUNDS = 6

JS = r"""() => {
  const who = (e) => {
    if (!e) return "(khong co gi)";
    const id = e.id ? '#' + e.id : '';
    const cl = (e.className && typeof e.className === 'string')
      ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return e.tagName.toLowerCase() + id + cl;
  };
  const out = [];
  for (const l of document.querySelectorAll('#labels [data-body-id]')) {
    const r = l.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;                 // nhan dang an
    const cx = Math.round(r.left + r.width / 2);
    const cy = Math.round(r.top + r.height / 2);
    if (cx < 0 || cy < 0 || cx > innerWidth || cy > innerHeight) continue;
    const top = document.elementFromPoint(cx, cy);
    const owner = top ? top.closest('[data-body-id]') : null;
    out.push({
      id: l.getAttribute('data-body-id'),
      text: (l.textContent || '').trim(),
      hit: owner ? owner.getAttribute('data-body-id') : null,
      topEl: who(top),
      // ⚠️ `visibility:hidden` VAN CO khung bao va van co kich thuoc, nen mot nhan
      //    da bi lop dan nhan AN DI van doc ra "bi che" neu khong hoi rieng. Do la
      //    hai chuyen khac nhau: bi che thi tre bam ra sai thien the, con bi an thi
      //    tre khong thay gi ca — mat mot duong vao, nhung khong bi lua.
      vis: getComputedStyle(l).visibility,
      x: cx, y: cy
    });
  }
  return out;
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    ok = bad = 0

    def chk(label, cond, detail=""):
        nonlocal ok, bad
        if cond:
            ok += 1
            print("  [OK]   %s%s" % (label, "  (%s)" % detail if detail else ""))
        else:
            bad += 1
            print("  [HONG] %s%s" % (label, "  (%s)" % detail if detail else ""))

    rounds = []
    seen_pairs = {}
    hidden_ids = {}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for rd in range(ROUNDS):
                ctx = b.new_context(viewport={"width": 1440, "height": 900},
                                    locale="vi-VN")
                ctx.add_init_script(
                    "try{localStorage.setItem('astroq-lang','vi');"
                    "localStorage.setItem('astroq-map01-seen','1')}catch(e){}")
                pg = ctx.new_page()
                pg.goto("http://localhost:%d/explorer.html" % PORT,
                        wait_until="load", timeout=60000)
                try:
                    pg.wait_for_function("() => window.__solarReady === true",
                                         timeout=30000)
                except Exception:
                    pass
                pg.wait_for_timeout(3400)      # #loader co transition .8s
                rows = pg.evaluate(JS)
                shown = [r for r in rows if r["vis"] != "hidden"]
                hid = [r for r in rows if r["vis"] == "hidden"]
                bad_rows = [r for r in shown if r["hit"] != r["id"]]
                rounds.append((len(shown), len(bad_rows), len(hid)))
                for r in bad_rows:
                    k = (r["id"], r["topEl"])
                    seen_pairs[k] = seen_pairs.get(k, 0) + 1
                for r in hid:
                    hidden_ids[r["id"]] = hidden_ids.get(r["id"], 0) + 1
                print("  luot %d: %d nhan hien - %d nhan BI CHE o tam - %d nhan bi lop dan AN%s"
                      % (rd + 1, len(shown), len(bad_rows), len(hid),
                         " (" + ", ".join(r["id"] for r in hid) + ")" if hid else ""))
                for r in bad_rows:
                    print("            %-9s (%4d,%4d) -> %s"
                          % (r["id"], r["x"], r["y"], r["topEl"]))
                ctx.close()
            b.close()
    finally:
        httpd.shutdown()

    tot = sum(n for n, _k, _h in rounds)
    blk = sum(k for _n, k, _h in rounds)
    with_blk = sum(1 for _n, k, _h in rounds if k)
    hid_n = sum(h for _n, _k, h in rounds)
    print("\n=== Tong: %d luot - %d/%d nhan bi che - %d/%d luot CO nhan bi che ==="
          % (ROUNDS, blk, tot, with_blk, ROUNDS))
    if seen_pairs:
        print("  cap bi che (nhan -> phan tu nam tren):")
        for (a, h), n in sorted(seen_pairs.items(), key=lambda kv: -kv[1]):
            print("    %-10s -> %-30s %d/%d luot" % (a, h, n, ROUNDS))

    # ⚠️⚠️ CHI MOT TRONG HAI LOAI CHE LA PHEP KIEM. Ban dau bo do bat CA "moi nhan
    #    deu bam duoc", va no HONG vinh vien vi `saturn`/`uranus` nam sau `#deck`
    #    5/6 luot — mot phep kiem khong bao gio dat thi som muon nguoi ta bo qua no
    #    (dung cai bay da go o `probe_globe_daynight` hom nay). Nen:
    #      · nhan de nhan  -> LOI, vi tre bam vao chu nay ra thien the khac;
    #      · bang trai che -> KHONG phai loi, vi bang che kin thi tre khong thay
    #        nhan nen khong bi lua, va bang trai van liet ke du thien the.
    #    Do van dem ca hai, chi khac cho: mot cai bao HONG, mot cai bao SO.
    lbl_on_lbl = {k: v for k, v in seen_pairs.items() if ".body-lbl" in k[1]}
    chk("KHONG nhan nao bi mot NHAN KHAC de len (tre bam ra sai thien the)",
        not lbl_on_lbl, str(sorted(lbl_on_lbl.items())))
    by_ui = blk - sum(lbl_on_lbl.values())
    print("  [SO]   nhan nam sau bang giao dien: %d/%d luot-nhan "
          "(KHONG tinh la loi — xem chu thich)" % (by_ui, tot))
    print("  [SO]   nhan bi lop dan AN vi day het %d buoc van chong: %d luot-nhan%s"
          % (3, hid_n,
             "  " + str(sorted(hidden_ids.items(), key=lambda kv: -kv[1])) if hidden_ids else ""))

    print("\n=== KET QUA: %d dat / %d hong ===" % (ok, bad))
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
