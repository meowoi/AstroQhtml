# -*- coding: utf-8 -*-
"""
check_quiz_bank.py — soi NGÂN HÀNG CÂU HỎI (js/quiz-questions.js) + màn Quiz thật.

Chạy trên Chromium thật chứ không đọc chuỗi trong file: dữ liệu là JS nên
cách duy nhất chứng minh nó đúng cấu trúc là để trình duyệt nạp rồi hỏi lại.

  cd AstroQhtml
  python -m http.server 8123
  set PYTHONIOENCODING=utf-8 & python scratchpad/check_quiz_bank.py

⚠️ Nhãn của check() PHẢI KHÔNG DẤU (console Windows cp1252 -> UnicodeEncodeError
   ném giữa lúc chạy và bỏ dở mọi phép kiểm phía sau). Chữ có dấu chỉ nằm trong
   ĐIỀU KIỆN.
"""
import os
import sys
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8123"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

ok_n, bad_n = 0, 0

# 10 thuật ngữ người dùng yêu cầu — mỗi thuật ngữ phải có >= 2 câu trong bank.
NEEDED = {
    "star":       ["star", "star-fusion"],
    "planet":     ["planet", "planet-count"],
    "dwarf":      ["dwarf", "dwarf-ceres"],
    "moon":       ["moon", "moon-largest"],
    "asteroid":   ["asteroid-belt", "asteroid-what"],
    "comet":      ["comet-what", "comet-tail"],
    "meteoroid":  ["meteoroid", "meteoroid-chain"],
    "meteor":     ["meteor", "meteor-fireball"],
    "meteorite":  ["meteorite", "meteorite-survive"],
    "exoplanet":  ["exoplanet", "exoplanet-transit"],
    # 5 thuat ngu them 30/07/2026 — de 5 the trong So Tay Thuat Ngu giai ma duoc.
    # Truoc do chung o trang thai "sap co" vi bank khong co cau nao ve chung.
    "black-hole": ["black-hole", "black-hole-light"],
    "gravity":    ["gravity", "gravity-distance"],
    "nebula":     ["nebula", "nebula-gas"],
    "supernova":  ["supernova", "supernova-elements"],
    "cmb":        ["cmb", "cmb-when"],
}


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        errs = []
        ctx.on("weberror", lambda e: errs.append(str(e.error)))
        pg = ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        # ⚠️ Ghim ngôn ngu: AstroQ.getLang() lui ve navigator.language, ma Chromium
        # cua Playwright mac dinh en-US -> phan "tieng Viet" cua bo test se lang le
        # chay bang tieng Anh (bai hoc ghi trong CLAUDE.md).
        pg.add_init_script("try{localStorage.setItem('astroq-lang','vi');}catch(e){}")
        pg.goto(f"{BASE}/quiz.html", wait_until="load")
        pg.wait_for_timeout(400)

        print("=== [1] Bank nap duoc + cau truc tung cau ===")
        # ⚠️ BANK NAY LA NHIEU FILE (doi 07/08/2026): muc luc `js/quiz-index.js` +
        #    mot file moi cau trong `js/quiz/`. Khong con `AstroQQuestions.ALL`.
        #    Nap HET de soi cau truc — day la cho DUY NHAT trong du an tai ca bank,
        #    va no la bo kiem chu khong phai trang cua tre.
        bank = pg.evaluate("""async () => {
            if (!window.AstroQQuestions || !AstroQQuestions.load) return null;
            return await AstroQQuestions.load(AstroQQuestions.terms());
        }""")
        check("js/quiz-index.js nap duoc, tai duoc moi cau qua load()", bool(bank),
              f"{len(bank or [])} cau")
        if not bank:
            br.close()
            print("\nDung som: khong doc duoc bank.")
            sys.exit(1)

        # ⚠️ KHONG GAN CUNG SO CAU. Cho nay tung doi dung 25 va bao hong khi them 10
        #    cau moi — trong khi khong co gi sai. Dieu muon biet la "moi thuat ngu
        #    trong NEEDED du 2 cau" (muc [2] lo viec do) va "bo goc khong bi xoa bot".
        check("bank co it nhat 25 cau (bo goc khong bi xoa bot)", len(bank) >= 25,
              f"{len(bank)}")
        # ⚠️ VA NGAY DUOI CHU THICH "KHONG GAN CUNG SO CAU" thi dong ke tiep lai gan
        #    cung `len(bank) == len(NEEDED)*2 + 5`. No dung khi bank co 35 cau, roi
        #    bao HONG ngay khi Dot 1 them 65 cau — trong khi khong co gi sai. Da sua
        #    06/08/2026. Bai hoc lap lai lan thu 7: **phep kiem phai hoi DIEU MINH
        #    MUON BIET, dung gan cung con so ma noi khac moi la nguon su that.**
        #    Dieu muon biet o day: 15 thuat ngu nen KHONG bi nhan doi ngoai y muon.
        _base = {k for keys in NEEDED.values() for k in keys}
        _n_base = sum(1 for it in bank if it["term"] in _base)
        check("15 thuat ngu nen van dung 2 cau moi thuat ngu (khong bi nhan doi)",
              _n_base == len(NEEDED) * 2, f"{_n_base} vs {len(NEEDED) * 2}")

        bad_shape = []
        for i, it in enumerate(bank):
            tag = it.get("term") or f"#{i}"
            if not isinstance(it.get("term"), str) or not it["term"]:
                bad_shape.append(f"{tag}: thieu term")
            for f in ("topic", "q", "ok", "no", "hint"):
                v = it.get(f)
                if not isinstance(v, dict) or not v.get("vi") or not v.get("en"):
                    bad_shape.append(f"{tag}: {f} thieu vi/en")
            o = it.get("opts")
            if not isinstance(o, list) or len(o) != 4:
                bad_shape.append(f"{tag}: opts khong phai 4 lua chon")
            else:
                for j, op in enumerate(o):
                    if not isinstance(op, dict) or not op.get("vi") or not op.get("en"):
                        bad_shape.append(f"{tag}: opts[{j}] thieu vi/en")
            a = it.get("a")
            if not isinstance(a, int) or a < 0 or a > 3:
                bad_shape.append(f"{tag}: a={a} ngoai 0..3")
        check("moi cau du term/topic/q/opts4/a/ok/no/hint o CA vi va en",
              not bad_shape, "; ".join(bad_shape[:6]))

        terms = [it["term"] for it in bank]
        dup = sorted({t for t in terms if terms.count(t) > 1})
        check("khong co term trung nhau", not dup, f"trung: {dup}")

        # Lựa chọn trong cùng một câu không được trùng chữ (trẻ sẽ thấy 2 đáp án y nhau)
        dup_opt = []
        for it in bank:
            for lang in ("vi", "en"):
                vals = [o[lang].strip() for o in it["opts"]]
                if len(set(vals)) != 4:
                    dup_opt.append(f"{it['term']}/{lang}")
        check("khong cau nao co 2 lua chon trung chu", not dup_opt, f"{dup_opt}")

        print("\n=== [2] Phu du 10 thuat ngu duoc yeu cau ===")
        have = set(terms)
        for label, keys in NEEDED.items():
            miss = [k for k in keys if k not in have]
            check(f"thuat ngu '{label}' co du 2 cau", not miss, f"thieu: {miss}")

        print("\n=== [3] Vi tri dap an — luat 'rai deu' DA NGHI HUU ===")
        # ⚠️⚠️ HAI PHEP KIEM "RAI DEU A/B/C/D" DA BO, 06/08/2026 — VA DAY LA MOT
        #    QUYET DINH, KHONG PHAI NOI LONG CHO DU LIEU MOI LOT QUA.
        #
        #    Luat "rai deu dap an" ton tai de tre khong hoc meo "cu chon B". No chet
        #    tu 31/07/2026, khi `quiz.html` them `shuffleOptions()` goi trong
        #    `renderQuestion()`: 4 lua chon duoc TRON LAI MOI LAN HIEN CAU, nen thu tu
        #    khai bao trong bank **khong bao gio toi nguoi choi**. Rai deu mot thu
        #    khong ai nhin thay la do mot thu khong ton tai.
        #
        #    Chinh CLAUDE.md da ghi: luat nay "**da tieu tron mot vong phoi hop** khi
        #    mot model duoc yeu cau di rai lai dap an cho 25 cau" — cong viec do khong
        #    tao ra gia tri nao. Giu phep kiem lai la hen ngay lap lai dung viec do.
        #
        #    Thu THAY THE no la muc [7]: "thu tu 4 dap an KHAC thu tu khai bao o phan
        #    lon cac luot" — tuc la do CHINH viec tron co xay ra hay khong. Do la dieu
        #    that su bao ve dua tre, va no manh hon: neu ai do go `shuffleOptions()`
        #    thi muc [7] do ngay, con phep kiem rai deu thi van xanh.
        dist = [sum(1 for it in bank if it["a"] == k) for k in range(4)]
        print(f"    (ghi nhan, khong phai tieu chi: A={dist[0]} B={dist[1]} "
              f"C={dist[2]} D={dist[3]} — thu tu nay bi tron truoc khi toi nguoi choi)")
        check("`shuffleOptions` van con trong quiz.html (thu bao ve tre THAT SU)",
              "shuffleOptions" in open("quiz.html", encoding="utf-8").read(),
              "— go no di thi luat rai deu song lai, xem muc [7]")

        print("\n=== [4] Nguon tham chieu ===")
        srcs = {}
        no_src = []
        for it in bank:
            s = it.get("src")
            if not s:
                no_src.append(it["term"])
                continue
            if not s.get("url") or not s.get("name"):
                no_src.append(it["term"] + " (src thieu url/name)")
            else:
                srcs.setdefault(s["url"], set()).add(it["term"])
        check("moi cau thien van deu co src (chi 5 cau lap trinh khong co)",
              sorted(no_src) == ["algorithm", "condition", "loop", "sensor", "sequence"],
              f"khong co src: {sorted(no_src)}")
        # ⚠️ DANH SACH TEN MIEN LA MOT QUYET DINH NOI DUNG, KHONG PHAI DON DEP.
        #    Moi lan noi rong deu ghi ly do o day, va chi noi rong DUNG ten mien can:
        #      · science.nasa.gov   — nguon goc cua bank 30/07/2026
        #      · spaceplace.nasa.gov — trang NASA viet CHO TRE EM, dung do tuoi 8-15;
        #                             `gravity` dan no vi science.nasa.gov khong co trang
        #                             dinh nghia luc hap dan tuong duong
        #      · www.nasa.gov       — (06/08/2026) ten mien CHINH cua NASA. `what-is-earths-
        #                             atmosphere` la trang mo ta tung tang khi quyen, khong
        #                             co ban tuong duong ben science.
        #      · lco.global         — (06/08/2026) Las Cumbres Observatory. Doi quan sat
        #                             that; la trang DUY NHAT tim duoc noi thang "mau sao
        #                             do nhiet do be mat". Da quet 8 trang NASA ung vien:
        #                             KHONG trang nao co noi dung mau sac sao.
        #      · scied.ucar.edu     — (06/08/2026) UCAR/NCAR, Learning Zone viet cho hoc sinh.
        #                             Dung khi NOAA doi duong dan (URL JetStream 404).
        #      · exploratorium.edu  — (06/08/2026) bao tang khoa hoc San Francisco. Giu ty le
        #                             400x cua nhat thuc va bai "eclipse in a cup".
        #    ⛔ Them ten mien moi thi PHAI ghi mot dong ly do o day. Danh sach khong ly do
        #       la danh sach se bi noi rong tuy tien cho tien viec.
        # ⚠️ `media.mit.edu` them 09/08/2026 cho the `term_algorithm` — KHONG phai noi
        #    long chinh sach nguon: MIT da la nguon tin cay cua du an (bo `wiki/` dan
        #    `media.mit.edu` · `scratch.mit.edu` · `appinventor.mit.edu`, muc 2 CLAUDE.md
        #    ghi nguon wiki la "NASA/ESA/MIT"). Can no vi NASA gan nhu khong co noi dung
        #    ve AI trong DOI SONG (thuat toan de xuat, thien lech) — thu tre gap moi ngay.
        OK_HOSTS = ("https://science.nasa.gov/", "https://spaceplace.nasa.gov/",
                    "https://www.nasa.gov/", "https://lco.global/",
                    "https://scied.ucar.edu/", "https://www.exploratorium.edu/",
                    "https://www.media.mit.edu/")
        bad_host = sorted(u for u in srcs if not u.startswith(OK_HOSTS))
        check("moi URL nguon thuoc danh sach ten mien da duyet, qua https",
              not bad_host, f"{bad_host}")

        # ⚠️ USER-AGENT PHAI LA CHUOI CHROME DAY DU, KHONG PHAI "Mozilla/5.0" TRON.
        #    Do 06/08/2026 tren exploratorium.edu: "Mozilla/5.0" -> 403, chuoi Chrome
        #    day du -> 200. Trang van song, chi la no chan bot theo User-Agent. De chuoi
        #    ngan thi phep kiem bao mot URL SONG la CHET — va mot phep kiem hay bao oan
        #    thi som muon bi bo qua, do moi la cai gia that.
        UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        for url in sorted(srcs):
            code = 0
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                           "Accept": "text/html"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    code = r.status
            except Exception as e:  # noqa: BLE001
                code = f"loi: {e}"
            check(f"URL tra 200: {url}", code == 200, f"{code}")

        print("\n=== [5] pickKeys: dung so cau, khong trung THE ===")
        # ⚠️ DOI TU `pickRound` SANG `pickKeys` (07/08/2026) va phep chong trung nay
        #    DOI PHAT BIEU — no khong con la "khong trung `term`" ma la "khong trung
        #    THE So Tay". Ly do: `term` la khoa cua CAU (moi cau mot khoa rieng:
        #    `star`, `star-fusion`), do duoc 100/100 khoa la duy nhat, nen phep loc
        #    theo `term` CHUA BAO GIO chan duoc gi ke tu khi no duoc viet. Y dinh ghi
        #    trong chu thich cu ("mot luot 5 cau co the hoi Sao choi hai lan") chi
        #    thanh that khi loc theo THE. Sau Dot 2 no moi that su quan trong: 15 the
        #    len ~20 cau/the, khong loc thi mot luot co the toan cau ve nhat thuc.
        res = pg.evaluate("""() => {
          const out = {rounds: 0, badLen: 0, dupCard: 0, dupKey: 0, seen: {}};
          for (let i = 0; i < 400; i++) {
            const ks = AstroQQuestions.pickKeys(5);
            out.rounds++;
            if (ks.length !== 5) out.badLen++;
            if (new Set(ks).size !== 5) out.dupKey++;
            const cards = ks.map(k => { const g = AstroQQuestions.groupOf(k);
                                        return g ? (g.c || k) : k; });
            if (new Set(cards).size !== 5) out.dupCard++;
            ks.forEach(t => out.seen[t] = (out.seen[t] || 0) + 1);
          }
          return out;
        }""")
        check("400 luot deu ra dung 5 cau", res["badLen"] == 0, f"lech: {res['badLen']}")
        check("khong luot nao trung KHOA cau", res["dupKey"] == 0, f"trung: {res['dupKey']}")
        check("khong luot nao trung THE So Tay", res["dupCard"] == 0,
              f"trung: {res['dupCard']}")
        never = sorted(t for t in terms if t not in res["seen"])
        check("sau 400 luot moi cau trong bank deu tung duoc rut", not never, f"chua ra: {never}")
        # Tron tai cho mang G/LV la loi im lang -> kiem thu tu khai bao con nguyen
        after = pg.evaluate("() => AstroQQuestions.terms()")
        check("pickKeys KHONG tron tai cho muc luc", after == terms,
              "" if after == terms else "thu tu khoa da bi doi")

        print("\n=== [6] Chay that: tra loi, popup, nguon, ngon ngu ===")
        by_q_vi = {it["q"]["vi"]: it for it in bank}
        by_q_en = {it["q"]["en"]: it for it in bank}

        def find_cur():
            txt = pg.eval_on_selector("#q-text", "e => e.innerHTML").strip()
            return by_q_vi.get(txt) or by_q_en.get(txt)

        def click_correct(page, item):
            """Bam vao dap an DUNG bang cach DOC CHU, khong dua vao chi so o.

            ⚠️ Tu 31/07/2026 `quiz.html` TRON thu tu 4 dap an moi lan hien cau, nen
               `.opt` thu `item["a"]` khong con la dap an dung. Bam theo chi so o thi
               bo test tra loi SAI ma khong biet: no bao "5/5 dung" thanh "1/5".
            ⚠️ Bam theo chu cung dung la viec tre THAT SU lam — doc noi dung roi
               chon, khong ai chon theo vi tri o. Nen cach do nay vua dung hon vua
               ben hon truoc moi lan doi cach hien thi.
            """
            want = {item["opts"][item["a"]]["vi"], item["opts"][item["a"]]["en"]}
            shown = page.eval_on_selector_all(
                "#q-options .opt .txt", "es => es.map(e => e.textContent.trim())")
            hit = [i for i, t in enumerate(shown) if t in want]
            assert len(hit) == 1, (
                f"khong tim ra dap an dung tren man: muon={want} co={shown}")
            page.locator("#q-options .opt").nth(hit[0]).click()
            return hit[0]


        check("badge tong so cau = 5", pg.inner_text("#q-total").strip() == "5")

        seen_src, seen_nosrc = 0, 0
        seen_terms_ui = set()
        wrong_topic, wrong_opts, bad_srcline = [], [], []
        for load in range(6):
            if load:
                pg.reload(wait_until="load")
                pg.wait_for_timeout(350)
            for _ in range(5):
                it = find_cur()
                if not it:
                    bad_srcline.append("khong nhan ra cau hoi dang hien")
                    break
                seen_terms_ui.add(it["term"])
                # ⚠️ SO KHONG PHAN BIET HOA-THUONG. `.q-badge` co `text-transform:
                #    uppercase`, nen badge LUON hien chu hoa du du lieu viet kieu gi.
                #    So nguyen van la bat du lieu phai gan cung chu HOA — dung cai
                #    phan kieu du an da ghi thanh luat o `games.html` ngay 27/07/2026:
                #    "viet chu thuong trong du lieu vi CSS da uppercase san, dung
                #    hardcode chu hoa". Dieu muon biet la badge hien DUNG CHU DE,
                #    khong phai no hien dung kieu chu.
                if pg.inner_text("#q-topic").strip().upper() != it["topic"]["vi"].upper():
                    wrong_topic.append(it["term"])
                ui_opts = pg.eval_on_selector_all(
                    "#q-options .opt .txt", "els => els.map(e => e.textContent)")
                # ⚠️ So TAP HOP, khong so THU TU: quiz.html tron 4 dap an moi
                #    lan hien cau (31/07/2026). Doi dung thu tu la khang dinh
                #    lai dung hanh vi vua sua.
                if sorted(ui_opts) != sorted(o["vi"] for o in it["opts"]):
                    wrong_opts.append(it["term"])
                click_correct(pg, it)
                pg.click("#engage")
                pg.wait_for_selector(".sheet.show", timeout=4000)
                pg.wait_for_timeout(120)
                shown = pg.eval_on_selector(
                    "#sheet-src", "e => !e.classList.contains('hide')")
                if it.get("src"):
                    seen_src += 1
                    href = pg.eval_on_selector(
                        "#sheet-src a", "e => e && e.getAttribute('href')") if shown else None
                    if not shown or href != it["src"]["url"]:
                        bad_srcline.append(f"{it['term']}: shown={shown} href={href}")
                    label = pg.inner_text("#sheet-src")
                    if not label.startswith("Nguồn:"):
                        bad_srcline.append(f"{it['term']}: nhan '{label[:20]}'")
                else:
                    seen_nosrc += 1
                    if shown:
                        bad_srcline.append(f"{it['term']}: cau khong co nguon ma van hien dong nguon")
                if pg.eval_on_selector("#sheet-title", "e => e.textContent").strip() != "CHÍNH XÁC!":
                    bad_srcline.append(f"{it['term']}: tra loi dung ma popup khong bao CHINH XAC")
                pg.click("#next-btn")
                pg.wait_for_timeout(420)
                if pg.eval_on_selector("#summary", "e => e.classList.contains('show')"):
                    break
            if seen_src and seen_nosrc:
                break

        check("nhan ra duoc cau hoi dang hien + popup dung + dong nguon dung",
              not bad_srcline, "; ".join(bad_srcline[:4]))
        check("badge chu de khop du lieu", not wrong_topic, f"lech: {set(wrong_topic)}")
        check("4 lua chon tren man khop du lieu (mot phep hoan vi)", not wrong_opts,
              f"lech: {set(wrong_opts)}")
        check("da gap CA cau co nguon VA cau khong co nguon",
              seen_src > 0 and seen_nosrc > 0, f"co nguon={seen_src} khong={seen_nosrc}")
        # ⚠️ Vong lap tren THOAT SOM ngay khi gap du ca hai loai cau, nen so thuat
        # ngu no thay duoc khong noi len dieu gi ve do da dang cua de. Do rieng:
        # tai lai trang nhieu lan roi xem cau DAU TIEN co doi khong.
        first_terms = []
        for _ in range(8):
            pg.reload(wait_until="load")
            pg.wait_for_timeout(320)
            cur = find_cur()
            if cur:
                first_terms.append(cur["term"])
        check("8 luot tai trang ra >= 4 de mo dau khac nhau",
              len(set(first_terms)) >= 4, f"{len(set(first_terms))} khac nhau: {set(first_terms)}")
        check("man Quiz da chay qua nhieu thuat ngu khac nhau",
              len(seen_terms_ui | set(first_terms)) >= 8,
              f"{len(seen_terms_ui | set(first_terms))} thuat ngu")

        # --- Tron thu tu 4 dap an: PHAI dang xay ra ---
        # ⚠️ PHEP KIEM NAY BAT BUOC PHAI CO: phep kiem cu ("4 lua chon khop dung
        #    thu tu du lieu") da doi sang so TAP HOP, ma so tap hop van dat khi
        #    khong tron gi ca. Bo `shuffleOptions()` di thi phai co cai gi bao.
        #
        # ⚠️ BAN DAU TOI DO SAI VA PHEP KIEM DAT RONG: toi ghi lai "o ma dap an
        #    DUNG roi vao" qua nhieu luot roi doi >=3 o khac nhau. Nhung bank CO Y
        #    rai dap an dung khap A/B/C/D (co phep kiem rieng cho viec do), nen qua
        #    CAC CAU KHAC NHAU no von da roi vao ca 4 o du KHONG tron gi. Thu phep
        #    pha hoai chung minh dieu do: bo tron -> van "66/66 dat".
        # Cach do DUNG: so THU TU HIEN RA voi THU TU KHAI BAO cua CHINH cau do.
        #    khong tron -> giong y nguyen 100% cac luot
        #    co tron    -> mot phep hoan vi ngau nhien cua 4 phan tu chi trung
        #                  thu tu goc 1/24 lan (~4%)
        n_meas = n_perm = 0
        for _ in range(16):
            pg.reload(wait_until="load")
            pg.wait_for_timeout(300)
            cur = find_cur()
            if not cur:
                continue
            decl = [o["vi"] for o in cur["opts"]]
            shown = pg.eval_on_selector_all(
                "#q-options .opt .txt", "es => es.map(e => e.textContent.trim())")
            if sorted(shown) != sorted(decl):
                continue                      # cau tieng Anh / doc khong khop
            n_meas += 1
            if shown != decl:
                n_perm += 1
        check("do duoc du so luot (phep kiem khong dat rong)", n_meas >= 10,
              f"{n_meas}/16 luot doc duoc")
        # Nguong 50%: neu KHONG tron thi con so nay la 0 tuyet doi, con neu tron
        # that thi ky vong ~96% — 50% la khoang giua rat rong, khong the "dat oan".
        check("thu tu 4 dap an KHAC thu tu khai bao o phan lon cac luot (tuc la co tron)",
              n_meas > 0 and n_perm >= n_meas * 0.5,
              f"{n_perm}/{n_meas} luot da bi tron")


        def play_round(page):
            """Tra loi DUNG het luot dang mo, de lai bang tong ket dang hien."""
            for _ in range(20):
                cur = by_q_vi.get(page.eval_on_selector("#q-text", "e => e.innerHTML").strip())
                if not cur:
                    return False
                click_correct(page, cur)
                page.click("#engage")
                page.wait_for_selector(".sheet.show", timeout=4000)
                page.click("#next-btn")
                page.wait_for_timeout(400)
                if page.eval_on_selector("#summary", "e => e.classList.contains('show')"):
                    return True
            return False

        # Vong tai-lai o tren de trang o dau mot luot moi -> choi cho xong de muc [7]
        # co bang tong ket ma soi.
        check("choi tron mot luot sau khi tai lai trang", play_round(pg))

        print("\n=== [7] Bang tong ket + lam lai ra de moi ===")
        pg.wait_for_selector("#summary.show", timeout=6000)
        check("tra loi dung het thi ket qua 5/5", pg.inner_text("#sum-score").strip() == "5/5",
              pg.inner_text("#sum-score").strip())
        check("do chinh xac 100%", pg.inner_text("#sum-acc").strip() == "100%",
              pg.inner_text("#sum-acc").strip())
        q_before = pg.eval_on_selector("#q-text", "e => e.innerHTML")
        diff = 0
        for _ in range(8):
            pg.click("#act-retry")
            pg.wait_for_timeout(260)
            if pg.eval_on_selector("#q-text", "e => e.innerHTML") != q_before:
                diff += 1
            # chơi cho xong để bấm "Làm lại" được lần nữa
            for _ in range(5):
                it = find_cur()
                if not it:
                    break
                click_correct(pg, it)
                pg.click("#engage")
                pg.wait_for_selector(".sheet.show", timeout=4000)
                pg.click("#next-btn")
                pg.wait_for_timeout(400)
            pg.wait_for_selector("#summary.show", timeout=6000)
        check("bam 'Lam lai' thi de doi (khong lap y nguyen)", diff >= 6, f"{diff}/8 luot doi de")
        check("khong loi console trong suot bai kiem", not errs, "; ".join(errs[:3]))

        # Ảnh chụp để soi mắt phần dòng nguồn
        pg.click("#act-retry")
        pg.wait_for_timeout(260)
        it = find_cur()
        while it and not it.get("src"):
            pg.locator("#q-options .opt").nth(it["a"]).click()
            pg.click("#engage")
            pg.wait_for_selector(".sheet.show", timeout=4000)
            pg.click("#next-btn")
            pg.wait_for_timeout(400)
            it = find_cur()
        if it:
            pg.locator("#q-options .opt").nth(it["a"]).click()
            pg.click("#engage")
            pg.wait_for_selector(".sheet.show", timeout=4000)
            pg.wait_for_timeout(300)
            pg.screenshot(path=os.path.join(HERE, "qb-01-sheet-src.png"))

        print("\n=== [8] Ban tieng Anh ===")
        pg2 = ctx.new_page()
        pg2.on("console", lambda m: errs.append("EN:" + m.text) if m.type == "error" else None)
        pg2.add_init_script("try{localStorage.setItem('astroq-lang','en');}catch(e){}")
        # ⚠️ TAI LAI CHO TOI KHI GAP MOT CAU CO NGUON. Truoc day khoi nay lay
        #    "cau nao ra thi lay cau do", nen phep kiem nhan nguon 'Source:' ben
        #    duoi nam trong `if it.get("src")` va CO LUOT KHONG CHAY. Doi de la
        #    ngau nhien (moi luot 5 cau rut tu 35) thi mot phep kiem co dieu kien
        #    nhu vay se im lang bien mat ma tong so van "dat het" — dung loai loi
        #    da ghi trong CLAUDE.md.
        it = None
        for _try in range(12):
            pg2.goto(f"{BASE}/quiz.html", wait_until="load")
            pg2.wait_for_timeout(400)
            qtxt = pg2.eval_on_selector("#q-text", "e => e.innerHTML").strip()
            cand = by_q_en.get(qtxt)
            if cand and cand.get("src"):
                it = cand
                break
            it = it or cand
        check("cau hoi hien bang tieng Anh", bool(it), f"'{qtxt[:40]}'")
        check("da gap duoc mot cau EN CO nguon de kiem nhan 'Source:'",
              bool(it and it.get("src")), f"sau {_try+1} luot tai lai")
        if it:
            en_opts = pg2.eval_on_selector_all(
                "#q-options .opt .txt", "els => els.map(e => e.textContent)")
            check("4 lua chon tieng Anh khop du lieu (khong ke thu tu)",
                  sorted(en_opts) == sorted(o["en"] for o in it["opts"]),
                  f"{en_opts}")
            click_correct(pg2, it)   # bam theo CHU, xem ghi chu o click_correct
            pg2.click("#engage")
            pg2.wait_for_selector(".sheet.show", timeout=4000)
            pg2.wait_for_timeout(150)
            check("popup tieng Anh: tieu de CORRECT!",
                  pg2.inner_text("#sheet-title").strip() == "CORRECT!")
            if it.get("src"):
                check("nhan nguon tieng Anh la 'Source:'",
                      pg2.inner_text("#sheet-src").startswith("Source:"),
                      pg2.inner_text("#sheet-src")[:24])
            pg2.screenshot(path=os.path.join(HERE, "qb-02-sheet-en.png"))

        print("\n=== [9] Dien thoai 390x844 ===")
        ctx3 = br.new_context(viewport={"width": 390, "height": 844})
        pg3 = ctx3.new_page()
        pg3.on("console", lambda m: errs.append("MB:" + m.text) if m.type == "error" else None)
        pg3.add_init_script("try{localStorage.setItem('astroq-lang','vi');}catch(e){}")
        pg3.goto(f"{BASE}/quiz.html", wait_until="load")
        pg3.wait_for_timeout(400)
        # ⚠️ PHAI do dung mot cau CO nguon. Cau khong co nguon thi dong nguon dang
        # `hide` -> moi so do bang 0 va phep kiem "khong tran" dat mot cach VO NGHIA.
        it = by_q_vi.get(pg3.eval_on_selector("#q-text", "e => e.innerHTML").strip())
        for _ in range(12):
            if it and it.get("src"):
                break
            if not it:
                break
            pg3.locator("#q-options .opt").nth(it["a"]).click()
            pg3.click("#engage")
            pg3.wait_for_selector(".sheet.show", timeout=4000)
            pg3.click("#next-btn")
            pg3.wait_for_timeout(420)
            if pg3.eval_on_selector("#summary", "e => e.classList.contains('show')"):
                pg3.click("#act-retry")
                pg3.wait_for_timeout(300)
            it = by_q_vi.get(pg3.eval_on_selector("#q-text", "e => e.innerHTML").strip())
        check("tim duoc mot cau CO nguon de do tren dien thoai",
              bool(it and it.get("src")), it["term"] if it else "khong tim ra")
        if it and it.get("src"):
            pg3.locator("#q-options .opt").nth(it["a"]).click()
            pg3.click("#engage")
            pg3.wait_for_selector(".sheet.show", timeout=4000)
            pg3.wait_for_timeout(250)
            box = pg3.eval_on_selector("#sheet-src", """e => {
              const r = e.getBoundingClientRect();
              const c = e.closest('.sheet-card').getBoundingClientRect();
              return {w: r.width, cw: c.width, over: r.right - c.right, sw: e.scrollWidth,
                      cwid: e.clientWidth, hid: e.classList.contains('hide')};
            }""")
            check("dong nguon HIEN va khong tran ra ngoai the popup tren dien thoai",
                  (not box["hid"]) and box["over"] <= 1 and box["sw"] <= box["cwid"] + 1,
                  f"{box}")
            body = pg3.eval_on_selector("body", "e => e.scrollWidth <= window.innerWidth + 1")
            check("trang khong tran ngang tren dien thoai", body)
            pg3.screenshot(path=os.path.join(HERE, "qb-03-mobile.png"))

        check("khong loi console o ban EN va dien thoai",
              not [e for e in errs if e.startswith(("EN:", "MB:"))],
              "; ".join(errs[:3]))
        br.close()

    print(f"\n===== {ok_n} dat / {bad_n} hong =====")
    sys.exit(1 if bad_n else 0)


if __name__ == "__main__":
    main()
