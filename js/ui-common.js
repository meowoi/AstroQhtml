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

  /* Dịch toàn bộ nội dung + THUỘC TÍNH trong trang theo hàm tra từ `t`.
     Gọi một lần trong applyLang của mỗi trang, thay cho việc tự viết vòng lặp.

       data-i18n="key"        → textContent
       data-i18n-html="key"   → innerHTML   (dùng khi chuỗi có <b>, <br/>…)
       data-i18n-ph="key"     → placeholder
       data-i18n-title="key"  → title       (tooltip)
       data-i18n-aria="key"   → aria-label  (trình đọc màn hình)
       data-i18n-alt="key"    → alt         (ảnh)                              */
  var I18N_ATTR = { ph:"placeholder", title:"title", aria:"aria-label", alt:"alt" };
  function applyTexts(t, root){
    var r = root || document;
    r.querySelectorAll("[data-i18n]").forEach(function(el){
      el.textContent = t(el.getAttribute("data-i18n"));
    });
    r.querySelectorAll("[data-i18n-html]").forEach(function(el){
      el.innerHTML = t(el.getAttribute("data-i18n-html"));
    });
    for(var k in I18N_ATTR){
      if(!I18N_ATTR.hasOwnProperty(k)) continue;
      (function(attr, sel){
        r.querySelectorAll("[data-i18n-" + sel + "]").forEach(function(el){
          el.setAttribute(attr, t(el.getAttribute("data-i18n-" + sel)));
        });
      })(I18N_ATTR[k], k);
    }
  }

  /* Bật/tắt trạng thái active của nút đổi ngôn ngữ. */
  function markLangButtons(lang, sel){
    document.querySelectorAll(sel||".lang-switch button").forEach(function(b){
      b.classList.toggle("active", b.getAttribute("data-lang")===lang);
    });
  }

  /* Đồng bộ thuộc tính `lang` của <html> với ngôn ngữ đang hiển thị.
     ⚠️ Thêm 31/07/2026 vì TRƯỚC ĐÓ KHÔNG TRANG NÀO LÀM VIỆC NÀY: `explorer.html`
        ghi cứng `<html lang="en">` rồi hiển thị toàn bộ nội dung tiếng Việt.
        Sai `lang` không phải chuyện hình thức — trình đọc màn hình chọn giọng và
        quy tắc phát âm theo nó (đọc tiếng Việt bằng giọng Anh là không hiểu
        được), và Google dùng nó để biết trang viết bằng tiếng gì.
     ⚠️ Đặt ở ĐÂY, trong hàm dùng chung, chứ không sửa 16 trang: `initLang` là
        thứ mọi trang có nút đổi ngôn ngữ đều gọi. Gọi ngay một lần theo ngôn ngữ
        đang lưu (vì phần lớn trang gọi `applyLang(LANG)` TRỰC TIẾP chứ không qua
        đây), rồi bọc `applyLang` để mọi lần đổi sau cũng cập nhật theo. */
  function setDocLang(lang){
    try{ document.documentElement.setAttribute("lang", lang==="en" ? "en" : "vi"); }
    catch(e){}
  }

  /* Gắn nút .lang-switch + đồng bộ khi tab/trang khác đổi ngôn ngữ.
     applyLang do từng trang tự cài (mỗi trang render nội dung khác nhau). */
  function initLang(applyLang, sel){
    setDocLang(getLang());
    function apply(l){ setDocLang(l); applyLang(l); }
    document.querySelectorAll(sel||".lang-switch button").forEach(function(b){
      b.addEventListener("click", function(){
        var l=b.getAttribute("data-lang"); setLang(l); apply(l);
      });
    });
    global.addEventListener("storage", function(e){
      if(e.key===LS_LANG && (e.newValue==="en"||e.newValue==="vi")) apply(e.newValue);
    });
  }

  /* ---------------- Toast ----------------
     makeToast(el|id, ms) -> toast(msg, type)
     · "{tt}" trong msg  → ảnh Thiên thạch tím (img/tt.png)
     · type "ok"/"bad"   → icon check/cross phát sáng ở đầu toast   */
  /* Ảnh Thiên thạch tím chèn vào toast qua token {tt}. alt đổi theo ngôn ngữ đang chọn
     — hàm chứ không phải hằng, vì người dùng có thể đổi ngôn ngữ giữa chừng. */
  function ttImg(){
    return '<img class="tt-inline" src="img/tt.png" alt="' +
           (getLang() === "en" ? "Purple Meteor" : "Thiên thạch tím") + '" />';
  }
  var TOAST_IC = {
    ok:'<svg class="toast-ic ok" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M7.5 12.4l3 3 6-6.4"/></svg>',
    bad:'<svg class="toast-ic bad" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8.5 8.5l7 7M15.5 8.5l-7 7"/></svg>'
  };
  function makeToast(el, ms){
    var timer=null; ms = ms || 2400;
    return function(msg, type){
      var node = (typeof el==="string") ? $(el) : el;
      if(!node) return;
      var body = String(msg).replace(/\{tt\}/g, ttImg());
      node.innerHTML = (TOAST_IC[type]||"") + '<span class="toast-msg">'+body+'</span>';
      node.classList.add("show");
      clearTimeout(timer);
      timer = setTimeout(function(){ node.classList.remove("show"); }, ms);
    };
  }

  /* ═══════════ CHẾ ĐỘ GIẢM CẤU HÌNH — MỘT KHOÁ CHO CẢ APP ═══════════
     Thêm 02/08/2026 (`docs/decisions/005` mục 6).

     ⚠️ TRƯỚC ĐÓ NÓ CHỈ LÀ MỘT CÁI CÔNG TẮC TRONG BẢNG TRÁI CỦA `explorer.html`,
        không lưu và không dùng chung: tải lại trang là mất, và trang khác không
        biết gì. Nay theo đúng khuôn `astroq-sfx` / `astroq-lang` (quy tắc 2 mục 2
        của CLAUDE.md): một khoá, mọi trang đọc chung, đổi ở tab này thì tab kia
        nghe được qua sự kiện `storage`.

     ⚠️ NÓ CHỈ HẠ CHẤT LƯỢNG CẢNH, KHÔNG CẮT BYTE TẢI VỀ. Thứ nặng thật ở
        `explorer.html` là three.js kéo từ `unpkg.com`. Muốn cắt byte thì phải bỏ hẳn
        cảnh 3D — và đó chính là lý do `005` mục 5 chốt quả cầu là **PHẦN THÊM**:
        mọi bài học BẮT BUỘC nằm trong 7 bước của `mission-earth.html`, vốn đã 2D.

     ⚠️ TỰ PHÁT HIỆN KHÔNG ĐỦ, ĐỪNG TIN NÓ MỘT MÌNH. [Chưa kiểm chứng] Network
        Information API (`saveData` / `effectiveType`) **Safari/iOS không hỗ trợ**,
        mà iPad lại là thiết bị hay chơi nhiệm vụ này nhất. Nên `slowLink()` chỉ là
        lớp (a); lớp (b) chắc chắn hơn là mốc chờ 12 giây đã có ở `js/map-onboard.js`. */
  var LS_PERF = "astroq-perf";
  function getPerf(){
    try{ return localStorage.getItem(LS_PERF) === "1"; }catch(e){ return false; }
  }
  function setPerf(on){
    try{
      if(on) localStorage.setItem(LS_PERF, "1");
      else localStorage.removeItem(LS_PERF);
    }catch(e){}
  }
  /** Đường truyền có dấu hiệu yếu không. `false` cũng có nghĩa "không biết". */
  function slowLink(){
    try{
      var c = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      if(!c) return false;
      if(c.saveData) return true;
      return c.effectiveType === "slow-2g" || c.effectiveType === "2g";
    }catch(e){ return false; }
  }

  var API = { $:$, esc:esc, getUser:getUser, setUser:setUser, clearUser:clearUser,
              getLang:getLang, setLang:setLang, markLangButtons:markLangButtons,
              initLang:initLang, setDocLang:setDocLang,
              applyTexts:applyTexts, makeToast:makeToast, ttImg:ttImg,
              getPerf:getPerf, setPerf:setPerf, slowLink:slowLink,
              LS_USER:LS_USER, LS_LANG:LS_LANG, LS_PERF:LS_PERF };

  global.AstroQ = global.AstroQ || {};
  for(var k in API){ if(API.hasOwnProperty(k)) global.AstroQ[k] = API[k]; }
  if(!global.$) global.$ = $;
})(window);
