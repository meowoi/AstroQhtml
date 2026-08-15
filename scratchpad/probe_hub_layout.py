# -*- coding: utf-8 -*-
"""
probe_hub_layout.py — ĐO chỗ đứng của "phần để chơi" trên Trung Tâm Điều Hướng.

Câu hỏi DUY NHẤT nó trả lời: **trẻ phải kéo bao nhiêu pixel mới nhìn thấy một
thẻ khu vực (MOD) đầu tiên?** Mọi tranh luận về bố cục ở đây đều quy về con số
đó — "chiếm hết lên trên" là một phép đo, không phải một cảm giác.

Chạy:  python -m http.server 8123   (trong AstroQhtml/)
       python scratchpad/probe_hub_layout.py

⚠️ Nhãn print KHÔNG DẤU (console Windows cp1252 — quy tắc đã ghi ở CLAUDE.md).
"""
import sys, io, json
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

URL = "http://127.0.0.1:8123/dashboard.html"

# Bản giả AstroQAuth: dashboard chờ SDK để đọc tiến độ. Không gieo thì trang
# ngồi chờ 2,5s rồi mới vẽ, và phép đo rơi vào trạng thái chưa có số.
STUB = """
localStorage.setItem('astroq-lang','vi');
localStorage.setItem('astroq-user', JSON.stringify({name:'Bi',uid:'u-test',avatar:'ava/luna.png'}));
localStorage.setItem('astroq-tour-seen','1');
localStorage.setItem('astroq-map01-seen','1');
Object.defineProperty(window,'AstroQAuth',{configurable:true,
  get:function(){return {
    idToken:function(){return Promise.resolve(null);},
    getOnboarding:function(){return Promise.resolve({ok:true,tourSeen:true,intro01Seen:true,earth1Greeted:true,map01Seen:true});},
    setOnboarding:function(){return Promise.resolve({ok:true});},
    getAchievements:function(){return Promise.resolve({ok:false,reason:'net'});},
    getMissions:function(){return Promise.resolve({ok:false,reason:'net'});},
    postProgress:function(){return Promise.resolve({ok:false});},
    verifyAdmin:function(){return Promise.resolve(false);},
    logout:function(){return Promise.resolve();}
  };},
  set:function(){}});
"""

SIZES = [("desktop", 1440, 900), ("ipad-doc", 820, 1180), ("dt-390", 390, 844)]


def probe(pg, w, h):
    return pg.evaluate("""() => {
      const r = s => { const e = document.querySelector(s); if(!e) return null;
        const b = e.getBoundingClientRect();
        return {top: Math.round(b.top + scrollY), h: Math.round(b.height), vis: b.height > 0}; };
      const cards = document.querySelectorAll('.cards .hud');
      const first = cards[0] ? cards[0].getBoundingClientRect() : null;
      return {
        vh: innerHeight,
        docH: Math.round(document.documentElement.scrollHeight),
        header: r('.statusbar'), hero: r('.hero'), stats: r('.stats-hud'),
        cards: r('.cards'), console: r('.console-row'),
        firstCardTop: first ? Math.round(first.top + scrollY) : null,
        nCards: cards.length,
        overflowX: document.documentElement.scrollWidth > innerWidth
      };
    }""")


def main():
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name, w, h in SIZES:
            ctx = br.new_context(viewport={"width": w, "height": h},
                                 locale="vi-VN", timezone_id="Asia/Ho_Chi_Minh")
            ctx.add_init_script(STUB)
            pg = ctx.new_page()
            pg.goto(URL, wait_until="load")
            pg.wait_for_timeout(1200)
            d = probe(pg, w, h)
            top = d["firstCardTop"]
            print(f"\n--- {name} ({w}x{h}) ---")
            print(f"  cao trang        : {d['docH']}px   (khung nhin {d['vh']}px)")
            print(f"  header           : top {d['header']['top']:>4} cao {d['header']['h']}")
            print(f"  hero             : top {d['hero']['top']:>4} cao {d['hero']['h']}")
            print(f"  stats-hud        : top {d['stats']['top']:>4} cao {d['stats']['h']}")
            print(f"  cards ({d['nCards']} the)     : top {d['cards']['top']:>4} cao {d['cards']['h']}")
            print(f"  console-row      : top {d['console']['top']:>4} cao {d['console']['h']}")
            need = max(0, top - d["vh"] + 40)
            print(f"  >> THE MOD DAU TIEN o y={top}px  ->  phai keo {need}px moi thay")
            print(f"  tran ngang       : {'CO (LOI)' if d['overflowX'] else 'khong'}")
            ctx.close()
        br.close()


if __name__ == "__main__":
    main()
