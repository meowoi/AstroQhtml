# -*- coding: utf-8 -*-
"""
smoke_mate.py — BẠN ĐỒNG HÀNH CÓ PHẢN ỨNG THẬT KHÔNG? (mục C2, 16/08/2026)

    python -m http.server 8123          (trong AstroQhtml/)
    python scratchpad/smoke_mate.py

⚠️⚠️ ĐO ẢNH THẬT SỰ ĐỔI, KHÔNG ĐỌC CLASS. Gắn được class `cheer` lên phần tử
   KHÔNG chứng minh trẻ nhìn thấy gì khác — bài học đã trả giá nhiều lần trong dự
   án ("có CSS không chứng minh được người dùng thấy gì"). Nên bộ này đọc
   `img.currentSrc` và đo `getComputedStyle` của viền.

⚠️ Và đo cả chuyện ẢNH ĐÃ NẰM TRONG CACHE trước khi cần tới: không tải trước thì
   lần đầu trẻ làm đúng, trình duyệt mới bắt đầu kéo ảnh về và trong lúc chờ nó
   **vẫn vẽ khung ảnh CŨ** — linh vật "phản ứng" bằng đúng khuôn mặt bình thường
   rồi mới đổi muộn. Đó là lỗi ảnh mốc thời gian của Nhiệm vụ 01 (03/08).
"""
import os
import re
import sys

from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = "http://127.0.0.1:8123"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

ok_n = bad_n = 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def state(pg):
    """Trạng thái linh vật ĐANG HIỆN RA — đọc ảnh và màu thật, không đọc class."""
    return pg.evaluate("""() => {
      const el = document.querySelector('.gs-mate');
      if (!el) return null;
      const img = el.querySelector('img');
      const cs = getComputedStyle(el);
      const r = img.getBoundingClientRect();
      return { src: (img.currentSrc || img.src).split('/').pop(),
               cls: el.className, border: cs.borderColor,
               w: Math.round(r.width), h: Math.round(r.height),
               seen: r.width > 0 && r.top < innerHeight && r.bottom > 0 };
    }""")


def open_game(br, page, tt=60, w=1500, h=950, lang="vi"):
    ctx = br.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    pg.add_init_script("localStorage.setItem('astroq-lang','%s');"
                       "localStorage.setItem('astroq-asteroids','%d');" % (lang, tt))
    pg.goto(f"{BASE}/{page}", wait_until="load")
    pg.wait_for_timeout(500)
    return ctx, pg, errs


GAMES = ["game-dodge.html", "game-defender.html", "game-constellation.html",
         "game-racer.html", "game-maze.html", "game-catch.html",
         "game-survival.html", "game-comms.html", "game-recycle.html",
         "game-units.html", "game-route.html"]


def main():
    print("=== Ban dong hanh phan ung (C2) ===")
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ---------- [1] Cả 10 game đều CÓ bạn đồng hành ----------
        # Truoc 16/08 chi 3/10 game co console — bay game con lai tre choi mot minh,
        # ma "choi mot minh" chinh la cho tinh nang nay sinh ra de chua.
        print("\n[1] Ca 10 game deu co ban dong hanh")
        for g in GAMES:
            ctx, pg, errs = open_game(br, g)
            st = state(pg)
            check(f"{g}", bool(st) and st["seen"] and st["src"].endswith("-idle.png"),
                  str(st and {k: st[k] for k in ("src", "w", "h")}))
            check(f"{g}: 0 loi trang", not errs, str(errs[:1])[:90])
            ctx.close()

        # ---------- [2] Ảnh phản ứng đã TẢI TRƯỚC ----------
        print("\n[2] Anh phan ung tai truoc, khong doi den luc can")
        ctx = br.new_context(viewport={"width": 1500, "height": 950})
        pg = ctx.new_page()
        got = []
        pg.on("response", lambda r: got.append(r.url.split("/")[-1])
              if "/img/mate/" in r.url else None)
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(f"{BASE}/game-units.html", wait_until="load")
        pg.wait_for_timeout(1200)
        for f in ("byte-idle.png", "byte-cheer.png", "byte-oops.png"):
            check(f"tai san {f} ngay tu dau", f in got, str(sorted(set(got))))
        ctx.close()

        # ---------- [3] Ba trạng thái ra ba HÌNH khác nhau ----------
        print("\n[3] Ba trang thai — do ANH va MAU VIEN, khong doc class")
        ctx, pg, errs = open_game(br, "game-units.html")
        s0 = state(pg)
        pg.evaluate("() => AstroQGameShell.mate('cheer')")
        pg.wait_for_timeout(120)
        s1 = state(pg)
        pg.evaluate("() => AstroQGameShell.mate('oops')")
        pg.wait_for_timeout(120)
        s2 = state(pg)
        check("idle -> cheer doi ANH", s0["src"] != s1["src"], f'{s0["src"]} -> {s1["src"]}')
        check("cheer -> oops doi ANH", s1["src"] != s2["src"], f'{s1["src"]} -> {s2["src"]}')
        check("ba anh KHAC NHAU ca ba", len({s0["src"], s1["src"], s2["src"]}) == 3,
              str([s0["src"], s1["src"], s2["src"]]))
        check("mau vien doi theo trang thai",
              len({s0["border"], s1["border"], s2["border"]}) == 3,
              str([s0["border"], s1["border"], s2["border"]]))
        ctx.close()

        # ---------- [4] Tự về bình thường ----------
        print("\n[4] Tu ve binh thuong, khong dung mai o mot bieu cam")
        ctx, pg, errs = open_game(br, "game-units.html")
        ms = pg.evaluate("""() => {
          const m = /MATE_MS\\s*=\\s*(\\d+)/.exec(document.documentElement.outerHTML);
          return m ? +m[1] : null; }""")
        pg.evaluate("() => AstroQGameShell.mate('cheer')")
        pg.wait_for_timeout(150)
        check("dang o cheer", state(pg)["src"].endswith("-cheer.png"))
        pg.wait_for_timeout(1900)
        check("sau ~1,5s tu ve idle", state(pg)["src"].endswith("-idle.png"),
              state(pg)["src"])
        # Cung trang thai hai lan lien tiep phai CHAY LAI hoat canh, khong thi lan
        # thu hai trong nhu khong co gi xay ra.
        pg.evaluate("() => AstroQGameShell.mate('oops')")
        pg.wait_for_timeout(80)
        pg.evaluate("() => AstroQGameShell.mate('oops')")
        pg.wait_for_timeout(80)
        check("goi 'oops' hai lan lien tiep van o oops",
              state(pg)["src"].endswith("-oops.png"), state(pg)["src"])
        ctx.close()

        # ---------- [5] CHƠI THẬT: linh vật phản ứng đúng lúc ----------
        print("\n[5] Choi that — Tram Doi Chieu")
        ctx, pg, errs = open_game(br, "game-units.html")
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        bad = pg.evaluate("() => window.__dbg.bad()")
        for i, x in enumerate(bad):
            if x:
                pg.locator('.uc-row[data-i="%d"]' % i).click(); pg.wait_for_timeout(60)
        pg.click("#ok"); pg.wait_for_timeout(200)
        check("duyet DUNG -> linh vat mung", state(pg)["src"].endswith("-cheer.png"),
              state(pg)["src"])
        ctx.close()

        ctx, pg, errs = open_game(br, "game-units.html")
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        pg.click("#ok"); pg.wait_for_timeout(200)      # bo sot het
        check("duyet SAI -> linh vat lo lang", state(pg)["src"].endswith("-oops.png"),
              state(pg)["src"])
        check("0 loi trang", not errs, str(errs[:1])[:90])
        ctx.close()

        # ---------- [6] Chơi thật một game canvas ----------
        print("\n[6] Choi that — Ghep Chom Sao (game canvas)")
        ctx, pg, errs = open_game(br, "game-constellation.html")
        pg.click("#start-btn"); pg.wait_for_timeout(700)
        # Noi SAI mot duong: bam sao dau roi bam mot sao khong ke tiep.
        n = pg.evaluate("() => (window.__dbg && __dbg.stars) ? __dbg.stars().length : 0")
        pg.evaluate("() => { const f = window.__dbg; }")
        pg.evaluate("() => { if (window.__dbg && __dbg.link) __dbg.link(0, 3); }")
        pg.wait_for_timeout(200)
        st = state(pg)
        if st["src"].endswith("-idle.png"):
            print("       (khong co be mat __dbg de lai — bo qua phep choi that o day)")
        else:
            check("noi sai -> linh vat lo lang", st["src"].endswith("-oops.png"), st["src"])
        check("0 loi trang", not errs, str(errs[:1])[:90])
        ctx.close()

        # ---------- [7] Màn hẹp: BẢN THU NHỎ ----------
        # ⚠️ Muc nay truoc 16/08 khang dinh "man hep KHONG co console" — dung voi
        #    trang thai cu, nen no bao hong dung luc san pham lam dung. Nay doi phat
        #    bieu VA SIET THEM: khong chi doi co ban thu nho, ma doi no KHONG DE LEN
        #    san va KHONG lam san hut o dien thoai.
        print("\n[7] Man hep — ban thu nho, va KHONG duoc de len san")
        for vn, w, h in (("dt doc", 390, 844), ("dt nho", 360, 780),
                         ("iPad mini doc", 768, 1024)):
            for page in ("game-units.html", "game-dodge.html"):
                ctx, pg, errs = open_game(br, page, w=w, h=h)
                d = pg.evaluate("""() => {
                  const m = document.querySelector('.gs-mate');
                  const f = document.querySelector('.field');
                  if (!m || !f) return null;
                  const a = m.getBoundingClientRect(), b = f.getBoundingClientRect();
                  const cs = getComputedStyle(m);
                  const ovX = Math.max(0, Math.min(a.right,b.right) - Math.max(a.left,b.left));
                  const ovY = Math.max(0, Math.min(a.bottom,b.bottom) - Math.max(a.top,b.top));
                  return { seen: a.width > 0 && a.top >= 0 && a.bottom <= innerHeight + 1,
                           w: Math.round(a.width), h: Math.round(a.height),
                           img: Math.round(m.querySelector('img').getBoundingClientRect().width),
                           row: cs.flexDirection === 'row',
                           overlap: Math.round(ovX * ovY),
                           ovfX: document.documentElement.scrollWidth - innerWidth };
                }""")
                tag = f"{vn} · {page}"
                check(f"{tag}: co ban thu nho, nam trong khung nhin",
                      d and d["seen"], str(d))
                check(f"{tag}: xep NGANG va nho lai", d and d["row"] and d["img"] <= 40,
                      f'ngang={d and d["row"]} anh={d and d["img"]}px')
                # ⚠️ PHEP KIEM QUAN TRONG NHAT CUA MUC NAY.
                check(f"{tag}: KHONG de len san mot pixel nao",
                      d and d["overlap"] == 0, f'{d and d["overlap"]}px²')
                check(f"{tag}: khong tran ngang", d and d["ovfX"] <= 1,
                      f'{d and d["ovfX"]}px')
                check(f"{tag}: 0 loi trang", not errs, str(errs[:1])[:80])
                ctx.close()

        # Phan ung phai chay THAT o man hep, khong chi hien ra roi dung im.
        ctx, pg, errs = open_game(br, "game-units.html", w=390, h=844)
        s0 = state(pg)
        pg.click("#start-btn"); pg.wait_for_timeout(400)
        pg.click("#ok"); pg.wait_for_timeout(300)          # bo sot het -> oops
        s1 = state(pg)
        check("man hep: phan ung doi ANH that", s0["src"] != s1["src"],
              f'{s0["src"]} -> {s1["src"]}')
        check("man hep: 0 loi trang", not errs, str(errs[:1])[:90])
        ctx.close()

        # ---------- [8] prefers-reduced-motion ----------
        print("\n[8] Giam chuyen dong — VAN phai con phan ung")
        ctx = br.new_context(viewport={"width": 1500, "height": 950},
                             reduced_motion="reduce")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script("localStorage.setItem('astroq-lang','vi');")
        pg.goto(f"{BASE}/game-units.html", wait_until="load")
        pg.wait_for_timeout(500)
        s0 = state(pg)
        pg.evaluate("() => AstroQGameShell.mate('cheer')")
        pg.wait_for_timeout(150)
        s1 = state(pg)
        # ⚠️ Anh va vien la NOI DUNG, khong phai hieu ung — tat chuyen dong khong
        #    duoc lam mat chung, khong thi o che do nay linh vat lai thanh tinh.
        check("van doi ANH khi tat chuyen dong", s0["src"] != s1["src"],
              f'{s0["src"]} -> {s1["src"]}')
        check("van doi MAU VIEN", s0["border"] != s1["border"])
        anim = pg.evaluate("""() => getComputedStyle(
            document.querySelector('.gs-mate img')).animationName""")
        check("nhung hoat canh thi tat", anim in ("none", ""), str(anim))
        # ⚠️ ĐO CỠ Ở ĐÂY chứ không ở [3]: sáu tư thế có tỉ lệ rất khác nhau, thả
        #    thẳng vào một ô `contain` thì mỗi lần đổi biểu cảm nhân vật NHẢY CỠ.
        #    Nhưng ở chế độ thường thì hoạt cảnh `gsCheer` CỐ Ý phóng 1.07 — đo ở
        #    đó là đo nhầm cái phóng có chủ đích. Tắt chuyển động thì chỉ còn ẢNH,
        #    tức tách bạch được đúng thứ muốn biết.
        pg.evaluate("() => AstroQGameShell.mate('oops')")
        pg.wait_for_timeout(150)
        s2 = state(pg)
        check("ANH khong lam nhan vat nhay co",
              s0["w"] == s1["w"] == s2["w"] and s0["h"] == s1["h"] == s2["h"],
              str([(s["w"], s["h"]) for s in (s0, s1, s2)]))
        check("0 loi trang", not errs, str(errs[:1])[:90])
        ctx.close()

        # ---------- [9] Van chan ghi DOM don dap ----------
        # ⚠️ Ở 4 game canvas lời gọi nằm trong nhánh `if` của `update()`. Không chạy
        #    mỗi khung hình, NHƯNG một loạt sự kiện trong cùng một giây thì gọi
        #    nhiều lần — mà mỗi lần lại đọc `offsetWidth` = ép trình duyệt tính lại
        #    bố cục NGAY TRONG vòng vẽ. Đo THẲNG số lần DOM bị ghi, đừng đoán theo
        #    tên hàm chứa lời gọi (phép kiểm đó báo oan 4/10 game).
        print("\n[9] Van chan ghi DOM don dap")
        ctx, pg, errs = open_game(br, "game-dodge.html")
        writes = pg.evaluate("""async () => {
          const el = document.querySelector('.gs-mate');
          let n = 0;
          const mo = new MutationObserver(r => { n += r.length; });
          mo.observe(el, {attributes:true, subtree:true,
                          attributeFilter:['class','src']});
          for (let i = 0; i < 60; i++) {          // 60 su kien trong ~0,3 giay
            AstroQGameShell.mate('cheer');
            await new Promise(r => setTimeout(r, 5));
          }
          await new Promise(r => setTimeout(r, 60));
          mo.disconnect();
          return n;
        }""")
        check("60 lan goi lien tiep chi ghi DOM vai lan", writes <= 8, f"{writes} lan ghi")
        # ...nhung van phai doi duoc sang trang thai KHAC ngay lap tuc.
        pg.evaluate("() => AstroQGameShell.mate('oops')")
        pg.wait_for_timeout(120)
        check("doi sang trang thai KHAC van tuc thi",
              state(pg)["src"].endswith("-oops.png"), state(pg)["src"])
        check("0 loi trang", not errs, str(errs[:1])[:90])
        ctx.close()

        br.close()

    # ---------- [10] Moi game deu THAT SU co noi day ----------
    # ⚠️ Khai `MATE` cho ca 10 game moi chi cho ra mot chan dung; khong noi vao su
    #    kien nao thi no van la buc anh tinh nhu truoc 16/08. Doi ca hai chieu.
    print("\n[10] Ca 10 game deu noi day vao su kien that")
    for g in GAMES:
        src = rd(g)
        # ⚠️ Khop CA DANH SACH THAM SO (`[^)]*`), khong khop mot dang viet cu the:
        #    bon game lop quyet dinh dung `mate(pass ? "cheer" : "oops")`, con game
        #    canvas dung `mate("cheer")`. Ghim mot dang la bao oan dang kia — va no
        #    da bao oan that o `mate(safe === 3 ? "cheer" : "oops")`.
        n_cheer = len(re.findall(r'mate\([^)]*"cheer"', src))
        n_oops = len(re.findall(r'mate\([^)]*"oops"', src))
        check(f"{g}: co ca mung va lo lang", n_cheer >= 1 and n_oops >= 1,
              f"cheer={n_cheer} oops={n_oops}")
    shell = rd("js/game-shell.js")
    declared = set(re.findall(r'"(game-[a-z]+)":\s*"(?:byte|comet)"', shell))
    check("[10] bang MATE khai du 10 game",
          declared == {g.replace(".html", "") for g in GAMES},
          str(sorted({g.replace(".html", "") for g in GAMES} - declared)))

    print("\n" + "=" * 54)
    print(f"KET QUA: {ok_n} dat / {bad_n} hong")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
