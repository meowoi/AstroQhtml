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
        bank = pg.evaluate("window.AstroQQuestions ? AstroQQuestions.ALL : null")
        check("js/quiz-questions.js nap duoc, co AstroQQuestions.ALL", bool(bank),
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
        check("so cau khop dung so thuat ngu khai o NEEDED (2 cau/thuat ngu) + 5 cau lap trinh",
              len(bank) == len(NEEDED) * 2 + 5,
              f"{len(bank)} vs {len(NEEDED) * 2 + 5}")

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

        print("\n=== [3] Dap an rai deu A/B/C/D ===")
        dist = [sum(1 for it in bank if it["a"] == k) for k in range(4)]
        check("moi vi tri A/B/C/D deu duoc dung it nhat 4 lan", min(dist) >= 4,
              f"A={dist[0]} B={dist[1]} C={dist[2]} D={dist[3]}")
        check("khong vi tri nao chiem qua 40% bank", max(dist) <= len(bank) * 0.4,
              f"cao nhat {max(dist)}/{len(bank)}")
        astro = [it for it in bank if it.get("src")]
        adist = [sum(1 for it in astro if it["a"] == k) for k in range(4)]
        # ⚠️ SUY RA THAY VI GAN CUNG "5/5/5/5". Voi 30 cau thien van thi khong chia
        #    het cho 4, nen doi phan bo TUYET DOI deu la doi mot dieu bat kha thi.
        #    Dieu muon biet: khong vi tri nao bi bo qua, va khong vi tri nao bi lam
        #    dung — tre hoc "cu chon B" thi bai kiem tra mat tac dung.
        _n = len(astro)
        _lo, _hi = _n // 4 - 1, _n // 4 + 2
        check("cau thien van rai deu moi vi tri A/B/C/D",
              all(_lo <= x <= _hi for x in adist),
              f"{adist} (moi vi tri phai trong [{_lo},{_hi}] voi {_n} cau)")

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
        # ⚠️ DA NOI RONG SANG "ten mien CUA NASA", va chi noi rong DUNG hai ten mien.
        #    `gravity` dan NASA Space Place (`spaceplace.nasa.gov`) — trang NASA viet
        #    CHO TRE EM, dung do tuoi 8-15, va science.nasa.gov khong co trang dinh
        #    nghia luc hap dan tuong duong. Van la nguon NASA chinh thuc, khong phai
        #    mo cho URL bat ky.
        NASA_HOSTS = ("https://science.nasa.gov/", "https://spaceplace.nasa.gov/")
        bad_host = sorted(u for u in srcs if not u.startswith(NASA_HOSTS))
        check("moi URL nguon thuoc ten mien NASA qua https", not bad_host, f"{bad_host}")

        for url in sorted(srcs):
            code = 0
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    code = r.status
            except Exception as e:  # noqa: BLE001
                code = f"loi: {e}"
            check(f"URL tra 200: {url}", code == 200, f"{code}")

        print("\n=== [5] pickRound: dung so cau, khong trung thuat ngu ===")
        res = pg.evaluate("""() => {
          const out = {rounds: 0, badLen: 0, dupTerm: 0, dupItem: 0, seen: {}};
          for (let i = 0; i < 400; i++) {
            const r = AstroQQuestions.pickRound(5);
            out.rounds++;
            if (r.length !== 5) out.badLen++;
            const ts = r.map(x => x.term);
            if (new Set(ts).size !== 5) out.dupTerm++;
            if (new Set(r).size !== 5) out.dupItem++;
            ts.forEach(t => out.seen[t] = (out.seen[t] || 0) + 1);
          }
          return out;
        }""")
        check("400 luot deu ra dung 5 cau", res["badLen"] == 0, f"lech: {res['badLen']}")
        check("khong luot nao trung thuat ngu", res["dupTerm"] == 0, f"trung: {res['dupTerm']}")
        check("khong luot nao trung cau hoi", res["dupItem"] == 0, f"trung: {res['dupItem']}")
        never = sorted(t for t in terms if t not in res["seen"])
        check("sau 400 luot moi cau trong bank deu tung duoc rut", not never, f"chua ra: {never}")
        # pickRound doi thu tu ALL tai cho la loi im lang -> kiem thu tu con nguyen
        after = pg.evaluate("AstroQQuestions.ALL.map(x => x.term)")
        check("pickRound KHONG tron tai cho mang ALL", after == terms)

        print("\n=== [6] Chay that: tra loi, popup, nguon, ngon ngu ===")
        by_q_vi = {it["q"]["vi"]: it for it in bank}
        by_q_en = {it["q"]["en"]: it for it in bank}

        def find_cur():
            txt = pg.eval_on_selector("#q-text", "e => e.innerHTML").strip()
            return by_q_vi.get(txt) or by_q_en.get(txt)

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
                if pg.inner_text("#q-topic").strip() != it["topic"]["vi"]:
                    wrong_topic.append(it["term"])
                ui_opts = pg.eval_on_selector_all(
                    "#q-options .opt .txt", "els => els.map(e => e.textContent)")
                if ui_opts != [o["vi"] for o in it["opts"]]:
                    wrong_opts.append(it["term"])
                pg.locator("#q-options .opt").nth(it["a"]).click()
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
        check("4 lua chon tren man khop du lieu (dung thu tu)", not wrong_opts,
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

        def play_round(page):
            """Tra loi DUNG het luot dang mo, de lai bang tong ket dang hien."""
            for _ in range(20):
                cur = by_q_vi.get(page.eval_on_selector("#q-text", "e => e.innerHTML").strip())
                if not cur:
                    return False
                page.locator("#q-options .opt").nth(cur["a"]).click()
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
                pg.locator("#q-options .opt").nth(it["a"]).click()
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
        pg2.goto(f"{BASE}/quiz.html", wait_until="load")
        pg2.wait_for_timeout(400)
        qtxt = pg2.eval_on_selector("#q-text", "e => e.innerHTML").strip()
        it = by_q_en.get(qtxt)
        check("cau hoi hien bang tieng Anh", bool(it), f"'{qtxt[:40]}'")
        if it:
            en_opts = pg2.eval_on_selector_all(
                "#q-options .opt .txt", "els => els.map(e => e.textContent)")
            check("4 lua chon tieng Anh khop du lieu", en_opts == [o["en"] for o in it["opts"]])
            pg2.locator("#q-options .opt").nth(it["a"]).click()
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
