# -*- coding: utf-8 -*-
"""probe_racer_end.py — HAI LOI O CUOI LUOT DUONG DUA SAO CHOM (22/08/2026).

Chu du an choi that roi bao:
  [A] *"khi doi thu ve dich truoc thi bat dau lai van co tieng bi thua, trong
      duong dua cung the"* — `SFX.dry()` goi `AstroQSfx.rumble()` roi VUT hàm
      dung nó tra ve; `rumble()` khong tu tat, nen tieng u chay MAI: qua bang ket
      qua, qua cu bam "Dua lai", suot ca luot sau. Moi lan thua cong them mot
      tieng nua.
  [B] *"luc tang toc de ve dich thi an giu 1 luc lau la bat dau lai ngay lap
      tuc"* — Space vua la TANG TOC (dang choi) vua la BAT DAU LUOT (man ket
      qua). Giu Space thi ban phim tu lap `keydown`; dung khung hinh luot ket
      thuc, cu lap KE TIEP mo luot moi va tru phi truoc khi tre kip doc.

⚠️ [A] do bang cach DEM BO DAO DONG SONG, khong nghe tieng: Chromium headless
   khong phat am. Va va `createOscillator` de dem `start`/`stop` — mot bo dao dong
   da `start` ma chua `stop` la mot tieng dang chay.
⚠️ [B] phai ban `KeyboardEvent` co `repeat:true`. `keyboard.down()` cua Playwright
   KHONG tu lap, nen no khong tai hien duoc cai ma ban phim that lam.

  python -m http.server 8123        # trong AstroQhtml/
  python scratchpad/probe_racer_end.py
"""
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8123"
SRC = (ROOT / "game-racer.html").read_text(encoding="utf-8")
SFX = (ROOT / "js" / "sfx.js").read_text(encoding="utf-8")
COST = int(re.search(r"COST:\s*(\d+)", SRC).group(1))

dat = 0
hong = 0


def chk(name, cond, info=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   " + name + (("  (" + str(info) + ")") if info else ""))
    else:
        hong += 1
        print("  [HONG] " + name + (("  -> " + str(info)) if info else ""))


# ── Va `createOscillator` TRUOC khi trang chay ───────────────────────
HOOK = """(() => {
  window.__osc = { made:0, stopped:0 };
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;
  const orig = AC.prototype.createOscillator;
  AC.prototype.createOscillator = function(){
    const o = orig.apply(this, arguments);
    window.__osc.made++;
    const st = o.stop.bind(o);
    let done = false;
    o.stop = function(){ if(!done){ done = true; window.__osc.stopped++; } return st.apply(o, arguments); };
    return o;
  };
})();"""


def live(pg):
    """So bo dao dong DANG CHAY (da `start`, chua `stop`)."""
    return pg.evaluate("() => window.__osc.made - window.__osc.stopped")


def made(pg):
    """So bo dao dong DA TAO tu dau lan chay.

    ⚠️ "Co phat tieng khong" phai hoi bang con so NAY, khong hoi bang `live()`:
       tieng ve nhi la hai not rat ngan (0,20s va 0,26s), nen do `live()` muon
       mot chut la thay 0 va phep kiem bao hong oan.
    """
    return pg.evaluate("() => window.__osc.made")


# ⚠️ Ham dung cua `rumble` ha am luong roi moi goi `o1.stop()` SAU 520ms (de khong
#    nghe mot cu "cach"), nen bo dem `stopped` chi tang sau moc do. Moi phep kiem
#    "tieng da tat chua" phai cho lau hon con so nay.
STOP_MS = 800


def newpage(br, sfx_on=True):
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, locale="vi-VN",
                         timezone_id="Asia/Ho_Chi_Minh")
    ctx.add_init_script("localStorage.setItem('astroq-lang','vi');"
                        "localStorage.setItem('astroq-asteroids','300');"
                        "localStorage.setItem('astroq-sfx','%s');"
                        % ("on" if sfx_on else "off"))
    ctx.add_init_script(HOOK)
    pg = ctx.new_page()
    pg.perr = []
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.goto(BASE + "/game-racer.html", wait_until="load", timeout=30000)
    pg.wait_for_selector("#start-btn", timeout=8000)
    pg.wait_for_timeout(400)
    if pg.locator(".ov.rot.show").count():
        pg.locator(".ov.rot.show .rot-ok").click()
    return ctx, pg


def start(pg):
    pg.click("#start-btn")
    pg.wait_for_function("() => window.__racer && __racer.state === 'play'", timeout=8000)
    # Mot cu cham vao canvas de WebAudio duoc "wake" (chinh sach tu dong phat).
    pg.mouse.click(700, 500)
    pg.wait_for_timeout(120)


def main():
    print("=== [0] LUAT DOC TU MA NGUON ===")
    chk("js/sfx.js: `rumble` co duong TU TAT (`ms`)",
        "ms == null ? 1200" in SFX or "o.ms" in SFX)
    chk("js/sfx.js: co `hush()` de tat moi tieng u dang song",
        "function hush()" in SFX and "hush: hush" in SFX)
    chk("game-racer: `dry` truyen `ms` (khong con goi rumble() tran)",
        re.search(r"dry:\s*function\(\)\{[^}]*rumble\(\{ms:", SRC) is not None)
    chk("game-racer: `lostRace` co tieng RIENG, khac tieng can nhien lieu",
        "lostRace ? SFX.lost()" in SRC or "else if(lostRace) SFX.lost()" in SRC)
    chk("game-racer: `startRound` tat tieng cua luot truoc",
        "SFX.hush()" in SRC.split("function startRound()")[1].split("function endRound")[0])
    chk("game-racer: nhanh Space-bat-dau-luot doi mot cu bam MOI (`e.repeat`)",
        "if(e.repeat) return;" in SRC)

    with sync_playwright() as p:
        br = p.chromium.launch()

        # ═══════════ [1] Ve nhi: tieng thua phai TAT ═══════════
        print("\n=== [1] VE NHI: tieng thua TAT, khong u sang luot sau ===")
        ctx, pg = newpage(br)
        start(pg)
        base, made0 = live(pg), made(pg)
        rid = pg.evaluate("() => __racer.rivalNearFinish()")
        pg.wait_for_function("() => __racer.state === 'over'", timeout=8000)
        chk("doi thu ve dich truoc -> ket cuc VE NHI", pg.evaluate("() => __racer.lostRace"),
            "doi thu %s · state=%s" % (rid, pg.evaluate("() => __racer.state")))
        pg.wait_for_timeout(250)
        rang = made(pg)
        pg.wait_for_timeout(STOP_MS + 900)
        after = live(pg)
        chk("co phat tieng thua that", rang > made0,
            "so bo dao dong da tao: %d -> %d" % (made0, rang))
        chk("het tieng: 0 bo dao dong con chay",
            after == 0, "con %d bo dang chay" % after)

        # Bat dau lai NGAY: khong duoc mang tieng cua luot truoc sang
        pg.evaluate("() => __racer.rivalNearFinish && 0")
        pg.click("#again-btn")
        pg.wait_for_function("() => __racer.state === 'play'", timeout=8000)
        pg.wait_for_timeout(STOP_MS)
        chk("bam 'Dua lai' -> luot moi khong con tieng u nao cua luot truoc",
            live(pg) <= base, "con %d tieng song" % live(pg))
        chk("0 loi trang", not pg.perr, "; ".join(pg.perr[:2]))
        ctx.close()

        # ═══════════ [2] Bam 'Dua lai' NGAY khi tieng con dang u ═══════════
        print("\n=== [2] BAM 'DUA LAI' NGAY khi tieng thua con dang u ===")
        ctx, pg = newpage(br)
        start(pg)
        base = live(pg)
        pg.evaluate("() => __racer.rivalNearFinish()")
        pg.wait_for_function("() => __racer.state === 'over'", timeout=8000)
        # ⚠ Tieng ve nhi la hai not RAT NGAN, nen o moc +150ms thuong da tat va
        #   phep kiem "khong u sang luot sau" DAT MOT CACH RONG. De do that dieu
        #   `startRound` phai lam, gieo mot tieng u VO HAN (dung ca thu ma ban cu
        #   cua `SFX.dry` tao ra) roi moi bam "Dua lai".
        pg.evaluate("() => { if(window.AstroQSfx) AstroQSfx.rumble({ms:0}); }")
        pg.wait_for_timeout(150)
        mid = live(pg)
        chk("gieo duoc mot tieng u dang chay de co cai ma tat", mid > base,
            "%d -> %d" % (base, mid))
        pg.click("#again-btn")
        pg.wait_for_function("() => __racer.state === 'play'", timeout=8000)
        pg.wait_for_timeout(STOP_MS)
        chk("tieng u bi tat NGAY khi luot moi mo (khong u xuyen vao luot sau)",
            live(pg) <= base,
            "dang u %d -> sau khi bam %d (nen %d)" % (mid, live(pg), base))
        ctx.close()

        # ═══════════ [3] Can nhien lieu: cung phai tat ═══════════
        print("\n=== [3] CAN NHIEN LIEU: tieng u cung phai tat ===")
        ctx, pg = newpage(br)
        start(pg)
        base = live(pg)
        pg.evaluate("() => { __racer.clear(); }")
        # Chay cho het nhien lieu thi lau; bam tang toc lien tuc de dot nhanh hon
        # KHONG duoc — thanh nap chua day. Dung `nearFinish` nguoc lai: cho doi thu
        # ve dich thi da do o [1]. O day do TRUC TIEP tieng `dry`.
        pg.evaluate("() => { if(window.AstroQSfx) AstroQSfx.rumble({ms:900}); }")
        pg.wait_for_timeout(200)
        chk("goi rumble({ms:900}) -> co tieng", live(pg) > base,
            "%d -> %d" % (base, live(pg)))
        pg.wait_for_timeout(900 + STOP_MS)
        chk("het `ms`: tieng da TU tat", live(pg) <= base, "con %d" % live(pg))
        pg.evaluate("() => { if(window.AstroQSfx) AstroQSfx.rumble({ms:0}); }")
        pg.wait_for_timeout(200)
        n_endless = live(pg)
        pg.evaluate("() => { if(window.AstroQSfx) AstroQSfx.hush(); }")
        pg.wait_for_timeout(STOP_MS)
        chk("hush() tat duoc ca tieng u VO HAN (`ms:0`)",
            n_endless > base and live(pg) <= base,
            "vo han %d -> sau hush %d" % (n_endless, live(pg)))
        ctx.close()

        # ═══════════ [4] Giu Space khong tu bat dau lai ═══════════
        print("\n=== [4] GIU SPACE KHONG TU BAT DAU LUOT MOI ===")
        ctx, pg = newpage(br)
        bal0 = int(pg.inner_text("#bal"))
        start(pg)
        bal1 = int(pg.inner_text("#bal"))
        chk("vao luot -> tru dung mot lan phi", bal1 == bal0 - COST,
            "%d -> %d (phi %d)" % (bal0, bal1, COST))
        pg.evaluate("() => __racer.rivalNearFinish()")
        pg.wait_for_function("() => __racer.state === 'over'", timeout=8000)
        # ⚠ Ban dung thu ban phim THAT sinh ra khi giu phim: `repeat:true`.
        pg.evaluate("""() => {
          for (let i = 0; i < 6; i++) {
            document.dispatchEvent(new KeyboardEvent('keydown',
              { key:' ', code:'Space', repeat:true, bubbles:true, cancelable:true }));
          }
        }""")
        pg.wait_for_timeout(300)
        chk("giu Space o man ket qua -> KHONG mo luot moi",
            pg.evaluate("() => __racer.state") == "over",
            "state=%s" % pg.evaluate("() => __racer.state"))
        chk("va KHONG bi tru phi luot moi", int(pg.inner_text("#bal")) == bal1,
            "vi %s (phai la %d)" % (pg.inner_text("#bal"), bal1))
        # Nha roi bam LAI thi phai vao duoc luot moi — khong duoc chan luon
        pg.evaluate("""() => {
          document.dispatchEvent(new KeyboardEvent('keyup', { key:' ', code:'Space', bubbles:true }));
          document.dispatchEvent(new KeyboardEvent('keydown',
            { key:' ', code:'Space', repeat:false, bubbles:true, cancelable:true }));
        }""")
        pg.wait_for_function("() => __racer.state === 'play'", timeout=8000)
        chk("nha roi bam LAI thi van vao duoc luot moi (khong chan luon)",
            pg.evaluate("() => __racer.state") == "play")
        chk("0 loi trang", not pg.perr, "; ".join(pg.perr[:2]))
        ctx.close()

        br.close()

    print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
    sys.exit(1 if hong else 0)


if __name__ == "__main__":
    main()
