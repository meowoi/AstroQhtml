/* ============================================================
   ui-common.js — tiện ích UI dùng chung cho mọi trang AstroQ.
   Vanilla, không build. Nạp TRƯỚC script riêng của từng trang:
     <script src="js/icons.js"></script>
     <script src="js/ui-common.js"></script>
   Cung cấp: $ , esc, getUser/setUser/clearUser,
             getLang/setLang/markLangButtons/initLang,
             makeToast (toast có token {tt} + icon ok/bad).
   ============================================================ */
(function(global){
  "use strict";

  var LS_USER = "astroq-user", LS_LANG = "astroq-lang";

  function $(id){ return document.getElementById(id); }
  function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;"); }

  /* ---------------- Hồ sơ phi hành gia ---------------- */
  function getUser(){ try{ return JSON.parse(localStorage.getItem(LS_USER)||"null"); }catch(e){ return null; } }
  function setUser(u){ try{ localStorage.setItem(LS_USER, JSON.stringify(u)); }catch(e){} }
  function clearUser(){ try{ localStorage.removeItem(LS_USER); }catch(e){} }

  /* ---------------- Ngôn ngữ (VI/EN) ----------------
     Ưu tiên lựa chọn đã lưu, sau đó ngôn ngữ trình duyệt, mặc định VI. */
  function getLang(){
    try{ var sv=localStorage.getItem(LS_LANG); if(sv==="en"||sv==="vi") return sv; }catch(e){}
    try{ if((navigator.language||"vi").toLowerCase().indexOf("en")===0) return "en"; }catch(e){}
    return "vi";
  }
  function setLang(lang){ try{ localStorage.setItem(LS_LANG, lang); }catch(e){} }

  /* Bật/tắt trạng thái active của nút đổi ngôn ngữ. */
  function markLangButtons(lang, sel){
    document.querySelectorAll(sel||".lang-switch button").forEach(function(b){
      b.classList.toggle("active", b.getAttribute("data-lang")===lang);
    });
  }

  /* Gắn nút .lang-switch + đồng bộ khi tab/trang khác đổi ngôn ngữ.
     applyLang do từng trang tự cài (mỗi trang render nội dung khác nhau). */
  function initLang(applyLang, sel){
    document.querySelectorAll(sel||".lang-switch button").forEach(function(b){
      b.addEventListener("click", function(){
        var l=b.getAttribute("data-lang"); setLang(l); applyLang(l);
      });
    });
    global.addEventListener("storage", function(e){
      if(e.key===LS_LANG && (e.newValue==="en"||e.newValue==="vi")) applyLang(e.newValue);
    });
  }

  /* ---------------- Toast ----------------
     makeToast(el|id, ms) -> toast(msg, type)
     · "{tt}" trong msg  → ảnh Thiên thạch tím (img/tt.png)
     · type "ok"/"bad"   → icon check/cross phát sáng ở đầu toast   */
  var TT_IMG = '<img class="tt-inline" src="img/tt.png" alt="Thiên thạch tím" />';
  var TOAST_IC = {
    ok:'<svg class="toast-ic ok" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M7.5 12.4l3 3 6-6.4"/></svg>',
    bad:'<svg class="toast-ic bad" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8.5 8.5l7 7M15.5 8.5l-7 7"/></svg>'
  };
  function makeToast(el, ms){
    var timer=null; ms = ms || 2400;
    return function(msg, type){
      var node = (typeof el==="string") ? $(el) : el;
      if(!node) return;
      var body = String(msg).replace(/\{tt\}/g, TT_IMG);
      node.innerHTML = (TOAST_IC[type]||"") + '<span class="toast-msg">'+body+'</span>';
      node.classList.add("show");
      clearTimeout(timer);
      timer = setTimeout(function(){ node.classList.remove("show"); }, ms);
    };
  }

  var API = { $:$, esc:esc, getUser:getUser, setUser:setUser, clearUser:clearUser,
              getLang:getLang, setLang:setLang, markLangButtons:markLangButtons,
              initLang:initLang, makeToast:makeToast, TT_IMG:TT_IMG,
              LS_USER:LS_USER, LS_LANG:LS_LANG };

  global.AstroQ = global.AstroQ || {};
  for(var k in API){ if(API.hasOwnProperty(k)) global.AstroQ[k] = API[k]; }
  if(!global.$) global.$ = $;
})(window);
