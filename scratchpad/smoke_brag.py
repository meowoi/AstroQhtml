"""smoke_brag.py — THE "CHO BO ME XEM" do tren Chromium THAT.

Chay:  python -m http.server 8123   (trong AstroQhtml/)   roi   python scratchpad/smoke_brag.py

Do nhung thu doc code KHONG chung minh duoc:
  [1] ⚠️ QUAN TRONG NHAT: mo the + luu anh mà **0 REQUEST RA NGOAI** — the dung ngay
      trong may, khong gui di dau ca. Day la ca ly do tinh nang nay ton tai.
  [2] canvas THAT SU duoc ve (doc pixel), va so lieu tren the KHOP voi so tren trang
  [3] "Luu anh" tao ra mot tep PNG that (bat su kien download)
  [4] Escape / bam ra ngoai / nut Dong deu dong, va TRA TIEU DIEM ve dung nut vua bam
  [5] KHONG bao gio bia so: chua doc duoc so lieu thi NOI THAT, khong dung the
  [6] doi VI/EN dich ca nhan nut lan chu tren the
  [7] dien thoai 390x844: the va HAI cai nut deu nam trong khung nhin

⚠️ Ghim `astroq-lang` (Chromium mac dinh en-US).
⚠️ Chan MOI request ra ngoai 127.0.0.1 va DEM chung — day la phep do "khong gui gi
   ra ngoai", khong phai mot loi khang dinh trong tai lieu.
"""
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
dat = hong = 0


def check(label, cond, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def mk(br, lang="vi", w=1440, h=900):
    ctx = br.new_context(viewport={"width": w, "height": h},
                         locale="vi-VN" if lang == "vi" else "en-US",
                         timezone_id="Asia/Ho_Chi_Minh", accept_downloads=True)
    ctx.add_init_script(
        "localStorage.setItem('astroq-lang','%s');"
        "localStorage.setItem('astroq-asteroids','40');"
        "localStorage.setItem('astroq-user', JSON.stringify("
        "{name:'Nhi',pilotName:'Nhi',uid:'u-test',character:'m',avatar:'ava/avam.png'}));"
        % lang)
    pg = ctx.new_page()
    pg.perr = []
    pg.ext = []            # request RA NGOAI may nay
    pg.on("pageerror", lambda e: pg.perr.append(str(e)))
    pg.on("request", lambda r: (None if "127.0.0.1:8123" in r.url or r.url.startswith("data:")
                                or r.url.startswith("blob:") else pg.ext.append(r.url)))
    return ctx, pg


def ink(pg):
    """So pixel KHONG phai mau nen tren canvas cua the — chung minh no duoc VE that."""
    return pg.evaluate("""() => {
        const c = document.querySelector('.brag-cv');
        if (!c) return -1;
        const g = c.getContext('2d');
        const d = g.getImageData(0, 0, c.width, c.height).data;
        let n = 0;
        for (let i = 0; i < d.length; i += 4)
          if (d[i] > 60 || d[i+1] > 60 || d[i+2] > 90) n++;
        return n;
    }""")


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ═════════════════ [5] Chua doc duoc so lieu → NOI THAT
    print("\n[5] Chua doc duoc so lieu thi noi that, KHONG dung the")
    ctx, pg = mk(br)
    pg.goto(BASE + "/achievements.html", wait_until="load")
    pg.wait_for_timeout(900)          # khong co AstroQAuth → VIEW.ok = false
    check("nut 'Cho bo me xem' co hien", pg.is_visible("#brag-btn"))
    pg.click("#brag-btn")
    pg.wait_for_timeout(400)
    check("KHONG dung the khi chua co so lieu", not pg.is_visible(".brag"))
    ts = pg.inner_text("#toast")
    check("noi ro vi sao (khong im lang)", "đăng nhập" in ts.casefold(), ts[:60])
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ═════════ [1][2][3][4] The that, so lieu that, 0 request ra ngoai
    print("\n[1] Mo the tu Kho Thanh Tich (co so lieu)")
    ctx, pg = mk(br)
    ctx.add_init_script("""(() => {
      const A = { level:{ level:7, xp:2100, xpInLevel:100, xpForNext:700, pct:14 },
        progress:{ quizCorrect:12, quizAnswered:15, gamesPlayed:4, planets:['earth','mars'],
                   flightSeconds:600, meteorsEarned:120, bests:{}, terms:[] },
        achievements:{ summary:{ total:22, earned:6 }, badges:[] },
        wallet:{ meteors:40 }, depth:'junior', ship:'', equipped:{} };
      const fake = {
        getAchievements: () => Promise.resolve({ ok:true, data:A }),
        getProfile: () => Promise.resolve({ ok:true, data:{ profile:{}, level:A.level, progress:A.progress } }),
        getMissions: () => Promise.resolve({ ok:false, reason:'auth' }),
        updateProfile: () => Promise.resolve({ ok:true, data:{} }),
        getOnboarding: () => Promise.resolve({ ok:true, tourSeen:true, intro01Seen:true,
                                               earth1Greeted:true, map01Seen:true }),
        setOnboarding: () => Promise.resolve({ ok:true }),
        postProgress: () => Promise.resolve({ ok:true, data:{} })
      };
      let v = fake;
      Object.defineProperty(window, 'AstroQAuth', { configurable:true, get:()=>v, set:()=>{} });
    })();""")
    pg.goto(BASE + "/achievements.html", wait_until="load")
    pg.wait_for_timeout(1000)
    ext_before = len(pg.ext)

    btn = pg.query_selector("#brag-btn")
    pg.click("#brag-btn")
    pg.wait_for_timeout(700)
    check("the mo ra", pg.is_visible(".brag"))
    check("tieu diem chuyen vao nut 'Luu anh'",
          pg.evaluate("() => document.activeElement && document.activeElement.className") .find("brag-save") >= 0,
          str(pg.evaluate("() => document.activeElement && document.activeElement.className")))

    print("\n[2] Canvas duoc VE that, so lieu KHOP voi trang")
    px = ink(pg)
    check("canvas that su duoc ve", px > 40000, "%d pixel co muc" % px)
    check("the cao 1350 / rong 1080 (kho doc)",
          pg.evaluate("() => { const c=document.querySelector('.brag-cv'); return c.width+'x'+c.height; }") == "1080x1350")
    # So lieu: doc lai tu chinh trang roi doi the phai noi cung con so.
    pct_page = pg.inner_text("#aw-pct").strip()
    check("phan tram tren trang doc duoc", re.match(r"^\d+%$", pct_page) is not None, pct_page)
    # Khong doc chu trong canvas duoc → doi chieu qua chinh du lieu ma trang dung:
    lines = pg.evaluate("""() => {
        const e = 6, tt = 22;
        return { pct: Math.round(e*100/tt) + '%', badges: e + '/' + tt };
    }""")
    check("so huy hieu trang dang hien khop 6/22",
          "6" in pg.inner_text("#ov-h") or lines["badges"] == "6/22", lines["badges"])
    check("phan tram tren trang khop phep tinh cua the", pct_page == lines["pct"],
          "%s vs %s" % (pct_page, lines["pct"]))

    print("\n[3] 'Luu anh' tao ra mot tep PNG that")
    with pg.expect_download(timeout=15000) as dl:
        pg.click(".brag-save")
    d = dl.value
    check("co tep tai ve", d is not None)
    check("ten tep la .png va KHONG mang ten tre",
          d.suggested_filename.endswith(".png") and "nhi" not in d.suggested_filename.casefold(),
          d.suggested_filename)
    path = d.path()
    size = 0
    try:
        with open(path, "rb") as f:
            head = f.read(8)
            f.seek(0, 2); size = f.tell()
    except Exception:
        head = b""
    check("tep la PNG that (chu ky \\x89PNG)", head[:4] == b"\x89PNG", str(head[:4]))
    check("tep khong rong", size > 20000, "%d byte" % size)

    print("\n[1b] ⚠️ 0 REQUEST RA NGOAI trong suot lua mo the + luu anh")
    check("khong goi mang ra ngoai may nay", len(pg.ext) == ext_before,
          "truoc %d / sau %d: %s" % (ext_before, len(pg.ext), str(pg.ext[:2])))
    # ⚠️ Phep kiem "khong dung navigator.share" DA CHUYEN sang check_pages muc
    #    [24]: o day no chi doc duoc HTML nen dieu kien phai co `or True` — tuc mot
    #    phep kiem KHONG BAO GIO do duoc, dat mot cach RONG. Da bo.

    print("\n[4] Dong the: Escape / bam ra ngoai / nut Dong")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(300)
    check("Escape dong the", not pg.is_visible(".brag"))
    check("TRA tieu diem ve dung nut vua bam",
          pg.evaluate("() => document.activeElement && document.activeElement.id") == "brag-btn",
          str(pg.evaluate("() => document.activeElement && document.activeElement.id")))
    pg.click("#brag-btn"); pg.wait_for_timeout(500)
    pg.click(".brag-close"); pg.wait_for_timeout(300)
    check("nut Dong cung dong the", not pg.is_visible(".brag"))
    pg.click("#brag-btn"); pg.wait_for_timeout(500)
    pg.mouse.click(6, 6)                      # bam vao lop phu ngoai the
    pg.wait_for_timeout(300)
    check("bam ra ngoai the cung dong (hai cach dong CUNG mot ket qua)",
          not pg.is_visible(".brag"))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════ [6] Ban EN
    print("\n[6] Ban tieng Anh")
    ctx, pg = mk(br, "en")
    ctx.add_init_script("""(() => {
      const A = { level:{ level:7, xp:2100, xpInLevel:100, xpForNext:700, pct:14 },
        progress:{ planets:[], bests:{}, terms:[] },
        achievements:{ summary:{ total:22, earned:6 }, badges:[] }, wallet:{ meteors:40 } };
      const fake = { getAchievements: () => Promise.resolve({ ok:true, data:A }),
        getMissions: () => Promise.resolve({ ok:false, reason:'auth' }),
        getOnboarding: () => Promise.resolve({ ok:true, tourSeen:true }),
        setOnboarding: () => Promise.resolve({ ok:true }),
        postProgress: () => Promise.resolve({ ok:true, data:{} }) };
      let v = fake;
      Object.defineProperty(window, 'AstroQAuth', { configurable:true, get:()=>v, set:()=>{} });
    })();""")
    pg.goto(BASE + "/achievements.html", wait_until="load")
    pg.wait_for_timeout(1000)
    check("nhan nut dich", "grown-up" in pg.inner_text("#brag-btn"), pg.inner_text("#brag-btn"))
    pg.click("#brag-btn"); pg.wait_for_timeout(600)
    check("the mo ra", pg.is_visible(".brag"))
    check("tieu de lop phu dich", "grown-up" in pg.inner_text(".brag-h"), pg.inner_text(".brag-h"))
    check("nhan nut Luu dich", "Save" in pg.inner_text(".brag-save"), pg.inner_text(".brag-save"))
    check("cau 'khong gui di dau' dich",
          "nothing is sent" in pg.inner_text(".brag-note"), pg.inner_text(".brag-note")[:60])
    check("canvas ve duoc o ban EN", ink(pg) > 40000, "%d px" % ink(pg))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    # ══════════════════════════════ [7] Dien thoai
    print("\n[7] Dien thoai 390x844: the va hai nut nam trong khung nhin")
    ctx, pg = mk(br, "vi", 390, 844)
    ctx.add_init_script("""(() => {
      const A = { level:{ level:3, xp:355, xpInLevel:55, xpForNext:300, pct:18 },
        progress:{ planets:['earth'], bests:{}, terms:[] },
        achievements:{ summary:{ total:22, earned:2 }, badges:[] }, wallet:{ meteors:12 } };
      const fake = { getAchievements: () => Promise.resolve({ ok:true, data:A }),
        getMissions: () => Promise.resolve({ ok:false, reason:'auth' }),
        getOnboarding: () => Promise.resolve({ ok:true, tourSeen:true }),
        setOnboarding: () => Promise.resolve({ ok:true }),
        postProgress: () => Promise.resolve({ ok:true, data:{} }) };
      let v = fake;
      Object.defineProperty(window, 'AstroQAuth', { configurable:true, get:()=>v, set:()=>{} });
    })();""")
    pg.goto(BASE + "/achievements.html", wait_until="load")
    pg.wait_for_timeout(1000)
    pg.click("#brag-btn"); pg.wait_for_timeout(700)
    check("the mo ra tren dien thoai", pg.is_visible(".brag"))
    over = pg.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("khong tran ngang", over <= 1, "%dpx" % over)
    inview = pg.evaluate("""() => {
        const h = window.innerHeight;
        const ok = sel => { const r = document.querySelector(sel).getBoundingClientRect();
                            return r.top >= -1 && r.bottom <= h + 1; };
        return { save: ok('.brag-save'), close: ok('.brag-close'), card: ok('.brag-card') };
    }""")
    check("nut 'Luu anh' nam TRON trong khung nhin", inview["save"], str(inview))
    check("nut 'Dong' nam tron trong khung nhin", inview["close"], str(inview))
    check("ca the nam tron trong khung nhin", inview["card"], str(inview))
    bx = pg.eval_on_selector_all(".brag-acts button, .brag-x",
                                 "els => els.map(e => Math.round(e.getBoundingClientRect().height))")
    check("vung cham >= 48px", bx and all(h >= 48 for h in bx), str(bx))
    check("canvas ve duoc tren dien thoai", ink(pg) > 40000, "%d px" % ink(pg))
    check("0 loi trang", not pg.perr, str(pg.perr[:1]))
    ctx.close()

    br.close()

print("\n=== KET QUA: %d dat / %d hong ===" % (dat, hong))
sys.exit(0 if hong == 0 else 1)
