# -*- coding: utf-8 -*-
"""
probe_step1_new.py — do buoc 1 sau khi viet lai theo `docs/decisions/004`.

    cd AstroQhtml
    python -m http.server 8123
    set PYTHONIOENCODING=utf-8 & python scratchpad/probe_step1_new.py

Do DUNG NHUNG DIEU MA 004 HUA, khong do lai nhung thu check_pages da soi:
  1. KHONG doi hinh: `world.map` la 'flat' tu dau den cuoi buoc 1
  2. Canh mo man SANG: >= 80 (moc 87,0 cua anh qua cau nhu no tung chay)
  3. CA BA dom trong khung (truoc day phep kiem chi doi 2/3)
  4. KHONG con day keo/zoom: khong co hand 'drag'/'zoom', va setControls tat ca hai
  5. Ban tay CHI vao dom chua cham, va no DOI CHO sau moi cu cham
  6. Cham dom -> hien THE NOI DUNG co so lieu NASA
  7. Cham du 3 -> xong buoc
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from smoke_mission_earth import BASE, boot, pix, say_through  # noqa: E402

MID = (0.3, 0.3, 0.4, 0.4)
ok = fail = 0
bad = []


def chk(cond, label, note=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  [OK]   {label}" + (f"  ({note})" if note else ""))
    else:
        fail += 1
        bad.append(label)
        print(f"  [HONG] {label}" + (f"  ({note})" if note else ""))


def main():
    from playwright.sync_api import sync_playwright

    errs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

        # theo doi class cua #hand qua thoi gian: ban tay 'drag' chi song 1,4s nen
        # doc mot lan bang evaluate la do mot khoanh khac ngau nhien
        page.add_init_script("""
          window.__handLog = [];
          new MutationObserver(() => {
            const h = document.getElementById('hand');
            if (h) window.__handLog.push(h.className + '|' + (window.__mission?.world?.map || '?'));
          }).observe(document.documentElement, {subtree:true, attributes:true,
                                                attributeFilter:['class']});
        """)

        boot(page, lang="vi")
        print("\n=== [1] Truoc cu bam 'Tiep tuc' dau tien ===")
        m0 = page.evaluate("() => window.__mission.world.map")
        chk(m0 == "flat", "mo man DA LA ban do phang (khong con anh qua cau)", m0)

        say_through(page)
        page.wait_for_timeout(900)

        print("\n=== [2] Khong doi hinh, canh du sang ===")
        m1 = page.evaluate("() => window.__mission.world.map")
        chk(m1 == "flat", "sau loi thoai VAN la ban do phang -> 0 lan doi hinh", m1)
        avg = pix(page, MID)["avg"]
        chk(avg >= 80, "canh mo man SANG (moc 87,0 cua anh qua cau nhu tung chay)",
            f"{avg:.1f}")

        print("\n=== [3] Ca ba dom trong khung ===")
        vis = page.evaluate("""() => {
            const w = window.__mission.world;
            return w.markers.map(m => {
              const s = w.screenOf('marker', m.id);
              return { id: m.id, vis: !!(s && s.visible) };
            });
        }""")
        n_vis = sum(1 for v in vis if v["vis"])
        chk(n_vis == 3, "CA BA dom nhin thay duoc (truoc day phep kiem chi doi 2/3)",
            f"{n_vis}/3 — " + ", ".join(f"{v['id']}={'v' if v['vis'] else 'X'}" for v in vis))
        chk([v["id"] for v in vis] == ["air", "sea", "land"],
            "dung 3 id noi dung air/sea/land", str([v["id"] for v in vis]))

        print("\n=== [4] Khong con day keo / zoom ===")
        hlog = page.evaluate("() => window.__handLog || []")
        chk(not any("drag" in s for s in hlog), "KHONG bao gio hien ban tay KEO",
            str([s for s in hlog if "drag" in s][:3]))
        chk(not any("zoom" in s for s in hlog), "KHONG bao gio hien ban tay ZOOM",
            str([s for s in hlog if "zoom" in s][:3]))
        ctl = page.evaluate("""() => {
            const el = document.querySelector('.e2-view');
            const before = getComputedStyle(el).cursor;
            return before;
        }""")
        # keo that: doi facing roi xem anh co dich khong
        moved = page.evaluate("""() => {
            const v = document.querySelector('.e2-view');
            const r = v.getBoundingClientRect();
            const x0 = r.left + r.width/2, y0 = r.top + r.height/2;
            const lay = document.querySelector('.e2-layer');
            const t0 = lay.style.transform;
            v.dispatchEvent(new PointerEvent('pointerdown',{clientX:x0,clientY:y0,pointerId:1,bubbles:true}));
            v.dispatchEvent(new PointerEvent('pointermove',{clientX:x0-300,clientY:y0,pointerId:1,bubbles:true}));
            v.dispatchEvent(new PointerEvent('pointerup',{pointerId:1,bubbles:true}));
            return { before: t0, after: lay.style.transform };
        }""")
        chk(moved["before"] == moved["after"],
            "KEO 300px KHONG lam anh dich mot pixel (da tat dragRotate)",
            f"{moved['after'][:38]}")

        print("\n=== [5] Ban tay chi vao dom, va doi cho sau moi cu cham ===")
        pos = []
        for i in range(3):
            page.wait_for_timeout(350)
            h = page.evaluate("""() => { const e=document.getElementById('hand');
                return { cls:e.className, l:e.style.left, t:e.style.top }; }""")
            pos.append(h)
            tgt = page.evaluate("""() => {
                const w = window.__mission.world;
                const left = w.markers.filter(m => !m.done);
                if (!left.length) return null;
                return w.screenOf('marker', left[0].id);
            }""")
            if i == 0:
                chk("tap" in h["cls"], "ban tay o che do CHI TRO (tap)", h["cls"])
            if tgt:
                dx = abs(float(h["l"].replace("px", "")) + 19 - tgt["x"])
                dy = abs(float(h["t"].replace("px", "")) - 16 - tgt["y"])
                chk(dx < 3 and dy < 3, f"ban tay tro DUNG dom chua cham (luot {i+1})",
                    f"lech {dx:.1f},{dy:.1f}px")
            # cham dom dang duoc chi
            page.evaluate("""() => {
                const w = window.__mission.world;
                const left = w.markers.filter(m => !m.done);
                if (left.length) window.__mission.pick({type:'marker', id:left[0].id});
            }""")
            page.wait_for_timeout(500)
            if i < 2:
                card = page.evaluate("""() => {
                    const c = document.getElementById('card');
                    return { show: c.classList.contains('show'),
                             nm: (document.getElementById('card-nm')||{}).textContent,
                             fact: (document.getElementById('card-fact')||{}).textContent };
                }""")
                chk(card["show"], f"cham dom {i+1} -> HIEN the noi dung", card["nm"])
                chk(any(k in (card["fact"] or "") for k in ("78%", "71%", "29%")),
                    f"the noi dung co SO LIEU NASA (luot {i+1})",
                    (card["fact"] or "")[:56])
            page.wait_for_timeout(3400 if i < 2 else 800)

        chk(len(set((p["l"], p["t"]) for p in pos)) >= 2,
            "ban tay DOI CHO giua cac luot (khong dung mot cho)",
            str([(p["l"], p["t"]) for p in pos]))

        print("\n=== [6] Xong buoc ===")
        page.wait_for_timeout(2500)
        done = page.evaluate("() => window.__mission.done.includes('scan')")
        chk(done, "cham du 3 dom -> buoc scan XONG")

        chk(not errs, "0 loi console", str(errs[:2]))
        b.close()

    print(f"\n=== KET QUA: {ok} dat / {fail} hong ===")
    for f in bad:
        print("  -", f)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
