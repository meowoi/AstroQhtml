# -*- coding: utf-8 -*-
import pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright
OUT = pathlib.Path(__file__).resolve().parent
HTML = """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="/css/common.css">
<script src="/js/specimens.js"></script>
<script src="/js/specimen-art.js"></script>
<style>
 body{background:#0d1322;color:#e8eefc;font-family:system-ui;margin:0;padding:18px}
 .row{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}
 .cell{background:linear-gradient(180deg,rgba(192,132,252,.13),rgba(13,19,34,.8) 55%,rgba(56,189,248,.11));
   border:1px solid rgba(192,132,252,.5);border-radius:14px;padding:10px;text-align:center}
 .big{font-size:96px;line-height:1;filter:drop-shadow(0 0 20px rgba(192,132,252,.75))}
 .mid{font-size:46px;line-height:1}
 .sm{font-size:19px;line-height:1}
 .nm{font-size:11px;margin-top:6px;opacity:.85}
 h3{font:600 13px system-ui;margin:16px 0 8px;color:#7dd3fc}
</style>
<div id="a"></div><div id="b"></div><div id="c"></div>
<script>
var ids = AstroQSpecimenArt.ids();
function draw(box, cls){
  document.getElementById(box).innerHTML = '<h3>'+cls+'</h3><div class="row">' +
    ids.map(function(id){
      return '<div class="cell"><div class="'+cls+'">'+AstroQSpecimens.icon(id)+'</div>'+
             '<div class="nm">'+AstroQSpecimens.name(id,"vi")+'</div></div>';
    }).join('') + '</div>';
}
draw('a','big'); draw('b','mid'); draw('c','sm');
document.title = 'ok:' + ids.length;
</script>"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1500,"height":600})
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/__art.html", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=HTML))
    pg.goto("http://127.0.0.1:8123/__art.html")
    pg.wait_for_timeout(900)
    print("  title:", pg.title())
    n = pg.eval_on_selector_all(".big svg.spart", "e=>e.length")
    print("  so svg .spart o co lon:", n)
    box = pg.evaluate("(function(){var e=document.querySelector('.big svg');var r=e.getBoundingClientRect();return {w:r.width,h:r.height};})()")
    print("  co mot tranh o 96px:", box)
    pg.locator("#a").screenshot(path=str(OUT/"art-96.png"))
    pg.locator("#b").screenshot(path=str(OUT/"art-46.png"))
    pg.locator("#c").screenshot(path=str(OUT/"art-19.png"))
    for e in errs: print("  JS ERROR:", e)
    b.close()
