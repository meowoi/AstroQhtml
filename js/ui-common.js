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
  /* Thoát chuỗi trước khi nhét vào innerHTML.
     ⚠️ PHẢI THOÁT CẢ `"` VÀ `'`, KHÔNG CHỈ `&` VÀ `<`. Bản cũ chỉ thoát hai ký tự đầu,
     đủ cho phần chữ nhưng KHÔNG đủ cho THUỘC TÍNH — mà `esc()` đang được gọi bên trong
     thuộc tính ở 6 chỗ (`title=`, `alt=`, `aria-label=` ở profile/pricing/explorer/
     specimen-vault). Hôm nay mọi giá trị ở đó đều là chuỗi tĩnh của client nên chưa
     thành lỗ hổng; nhưng một hàm thoát chuỗi mà chỉ đúng ở một loại ngữ cảnh là cái bẫy
     đặt sẵn cho lần đầu tiên ai đó nội suy dữ liệu từ server vào một thuộc tính.
     Thoát dư ở ngữ cảnh chữ là vô hại: trình duyệt vẽ lại đúng ký tự gốc. */
  function esc(s){
    return String(s == null ? "" : s).replace(/[&<>"']/g, function(c){
      return { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c];
    });
  }

  /* ---------------- Hồ sơ phi hành gia ---------------- */
  function getUser(){ try{ return JSON.parse(localStorage.getItem(LS_USER)||"null"); }catch(e){ return null; } }
  function setUser(u){ try{ localStorage.setItem(LS_USER, JSON.stringify(u)); }catch(e){} }
  function clearUser(){ try{ localStorage.removeItem(LS_USER); }catch(e){} }

  /* ---------------- Ngôn ngữ (VI/EN) ----------------
     Thứ tự quyết định ngôn ngữ cho lượt vào trang ĐẦU TIÊN:
       ① Lựa chọn đã lưu (`astroq-lang`)      → LUÔN THẮNG
       ② Múi giờ thiết bị là Việt Nam          → vi   ("truy cập từ Việt Nam")
       ③ Ngôn ngữ trình duyệt là tiếng Việt    → vi   (người Việt ở nước ngoài)
       ④ Còn lại                               → en   (khách quốc tế)

     ⚠️⚠️ ĐỔI 07/08/2026 — LỖI CŨ: CẢ THẾ GIỚI TRỪ NGƯỜI NÓI TIẾNG ANH ĐỀU
        THẤY TIẾNG VIỆT. Điều kiện cũ là `navigator.language.indexOf("en")===0`
        rồi mặc định `vi`, nên **chỉ trình duyệt tiếng Anh mới ra tiếng Anh**.
        Đo được trên Chromium: `ja-JP` → tiếng Việt · `fr-FR` → tiếng Việt.
        Một trang song ngữ Việt–Anh mà khách Nhật/Pháp/Hàn/Trung đọc ra tiếng
        Việt thì bản EN gần như không ai thấy. Nay `en` là **lưới an toàn quốc
        tế**, còn `vi` phải có căn cứ (múi giờ HOẶC ngôn ngữ trình duyệt).

     ⚠️ DÙNG MÚI GIỜ, KHÔNG DÙNG DỊCH VỤ TRA IP. Ba lý do, không phải chuộng
        đơn giản: ① tra IP là **một request ra tên miền ngoài** — đúng thứ dự
        án vừa gỡ sạch ngày 07/08/2026, và nó đóng lại đường PWA (service
        worker không cache đàng hoàng được cross-origin không CORS); ② nó **trễ
        khung hình đầu**: trang phải đứng chờ mạng, hoặc hiện tiếng Việt rồi
        nhảy sang tiếng Anh trước mắt khách; ③ nó **gửi IP của từng đứa trẻ cho
        một bên thứ ba** — dự án đã từ chối Google Analytics đúng vì lý do này.
        Múi giờ thì đọc tức thì, 0 byte, không qua mạng, không lộ gì.
     ⚠️ [Suy luận] Múi giờ là chỉ dấu vị trí, KHÔNG phải vị trí: người dùng VPN,
        người đang đi công tác, hay máy đặt sai giờ sẽ bị đoán nhầm. Chấp nhận
        được vì bấm nút VI/EN một lần là ghi vào `astroq-lang` và từ đó ① thắng
        vĩnh viễn — sai lầm chỉ tồn tại đúng một cú bấm.
     ⚠️ CHỈ khớp hai id CỦA RIÊNG VIỆT NAM. `Asia/Bangkok` cũng UTC+7 nhưng là
        Thái Lan; khớp theo múi giờ ±7 là gán tiếng Việt cho cả Thái, Lào,
        Campuchia, Indonesia. `Asia/Saigon` là bí danh cũ [Chưa kiểm chứng: một
        số hệ máy cũ vẫn trả về nó], giữ cho chắc.
     ⚠️ `wiki/` KHÔNG chịu ảnh hưởng của hàm này — đó là trang tĩnh thuần không
        nạp JS, và nó đã có URL riêng cho từng ngôn ngữ + 3 thẻ `hreflang`, tức
        Google tự chọn bản đúng. Đừng "thống nhất" hai cơ chế đó làm một. */
  var VN_TZ = { "Asia/Ho_Chi_Minh":1, "Asia/Saigon":1 };
  var _guess = null;                     /* nhớ trong một lượt tải trang */

  function guessLang(){
    if(_guess) return _guess;
    _guess = "en";
    try{
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if(tz && VN_TZ[tz]) return (_guess = "vi");
    }catch(e){}
    /* Chỉ xét ngôn ngữ CHÍNH. Người khai ["en-US","vi-VN"] là ưu tiên tiếng
       Anh — quét cả danh sách thì họ bị đẩy sang tiếng Việt. */
    try{
      if((navigator.language||"").toLowerCase().indexOf("vi")===0) return (_guess = "vi");
    }catch(e){}
    return _guess;
  }

  function getLang(){
    try{ var sv=localStorage.getItem(LS_LANG); if(sv==="en"||sv==="vi") return sv; }catch(e){}
    return guessLang();
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
  /* Ai cần vẽ lại khi đổi ngôn ngữ thì đăng ký ở đây (`AstroQ.onLang(fn)`).
     ⚠️ Có sổ đăng ký để KHÔNG phải nhét thêm lời gọi vào `setDocLang` mỗi lần có
        một thứ dùng chung cần dịch — `paintVersion` đang là lời gọi gõ cứng như thế,
        và cái thứ hai (lời nhắc xoay ngang của `js/game-shell.js`) là lúc đúng để
        dựng sổ. Chuỗi dịch nằm ở phía đăng ký, không phải ở đây.
     ⚠️ Callback hỏng thì KHÔNG được làm chết cả chuỗi đổi ngôn ngữ — một thứ phụ
        không dịch được còn hơn cả trang đứng lại ở tiếng cũ. */
  var LANG_CBS = [];
  function onLang(fn){ if(typeof fn === "function") LANG_CBS.push(fn); }

  function setDocLang(lang){
    try{ document.documentElement.setAttribute("lang", lang==="en" ? "en" : "vi"); }
    catch(e){}
    paintVersion(lang);
    for(var i=0;i<LANG_CBS.length;i++){
      try{ LANG_CBS[i](lang); }catch(e){}
    }
  }

  /* ---------------- Số hiệu bản dựng ----------------
     Mục đích DUY NHẤT: khi ai đó báo lỗi, biết họ đang xem bản nào. Cùng một
     trang có thể đang là hai bản khác nhau ở hai máy, vì trình duyệt giữ cache
     và GitHub Pages có lúc deploy chậm — chuyện đã xảy ra thật ngày 06/08/2026,
     khi hai lần deploy liên tiếp hết giờ và bản thật đứng yên ở bản 04/08 gần
     một ngày. Lúc đó không có cách nào nhìn màn hình mà biết là bản nào.

     ⚠️ VERSION LÀ CHỖ DUY NHẤT KHAI. `scratchpad/stamp_version.py` sửa đúng dòng
        dưới đây bằng máy — đừng gõ tay, và đừng chép giá trị này sang chỗ khác.
     ⚠️ Định dạng `YYYY.MM.DD.n` cố ý KHÔNG mang mã commit: mã commit của chính
        lần commit chứa nó thì chưa tồn tại lúc đóng dấu, nên mọi cách nhét SHA
        vào đây đều lệch một commit. Ngày + số thứ tự trong ngày thì luôn đúng,
        và đủ để đối chiếu với lịch sử git. */
  var VERSION = "2026.08.14.7";   /* stamp_version.py sửa dòng này */

  var VER_LBL = { vi: "Phiên bản", en: "Version" };

  function paintVersion(lang){
    var el = document.querySelector(".ver-badge");
    if(!el) return;
    var l = VER_LBL[lang === "en" ? "en" : "vi"];
    el.setAttribute("aria-label", l + " " + VERSION);
    el.setAttribute("title", l + " " + VERSION);
  }

  /* Dựng huy hiệu ở góc dưới-PHẢI. Góc dưới-trái đã có `.env-badge` của
     js/firebase-auth-ui.js — hai cái chồng nhau thì không đọc được cái nào. */
  function mountVersion(){
    if(document.querySelector(".ver-badge")) return;
    var el = document.createElement("div");
    el.className = "ver-badge";
    el.textContent = "v" + VERSION;
    document.body.appendChild(el);
    paintVersion(getLang());   /* sau khi gắn — paintVersion tìm phần tử qua DOM */
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
  /* Gốc site, suy từ chính thẻ <script> đang nạp file này.
     ⚠️ BẮT BUỘC từ 07/08/2026: trang chủ nay có HAI bản ở HAI ĐỘ SÂU thư mục
        (`/` và `/en/`), nên chuỗi cứng `img/tt.png` sẽ thành `/en/img/tt.png`
        và **404** — ảnh vỡ ngay trong toast "You're in! 500 ☄️ are waiting",
        tức đúng khoảnh khắc khách quốc tế vừa đăng ký thành công.
     ⚠️ KHÔNG dùng đường dẫn tuyệt đối `/img/…`: nó phá cách xem bằng `file://`
        và khoá dự án vào việc phải nằm ở gốc tên miền. Suy từ `currentScript`
        thì đúng ở mọi độ sâu và mọi cách phục vụ. */
  var SITE = (function(){
    try{
      var s = document.currentScript && document.currentScript.src;
      if(s) return s.replace(/js\/ui-common\.js.*$/, "");
    }catch(e){}
    return "";                      /* đường lùi: giữ nguyên hành vi cũ */
  })();

  function ttImg(){
    return '<img class="tt-inline" src="' + SITE + 'img/tt.png" alt="' +
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
        `explorer.html` là three.js — **183 KB gzip**, nay tự host ở `vendor/`
        (07/08/2026; trước đó kéo từ `unpkg.com` và là bản không rút gọn, 274 KB).
        Tự host cắt được 33% và bỏ một tên miền ngoài, nhưng **vẫn không cứu được
        máy yếu**: 183 KB vẫn phải tải, texture vẫn phải dựng, shader bloom vẫn
        phải biên dịch. Muốn cắt byte thật thì phải bỏ hẳn cảnh 3D — và đó chính
        là lý do `005` mục 5 chốt quả cầu là **PHẦN THÊM**: mọi bài học BẮT BUỘC
        nằm trong 7 bước của `mission-earth.html`, vốn đã 2D.

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
              getLang:getLang, guessLang:guessLang, setLang:setLang, markLangButtons:markLangButtons,
              initLang:initLang, setDocLang:setDocLang, onLang:onLang,
              applyTexts:applyTexts, makeToast:makeToast, ttImg:ttImg,
              getPerf:getPerf, setPerf:setPerf, slowLink:slowLink,
              VERSION:VERSION,
              LS_USER:LS_USER, LS_LANG:LS_LANG, LS_PERF:LS_PERF };

  global.AstroQ = global.AstroQ || {};
  for(var k in API){ if(API.hasOwnProperty(k)) global.AstroQ[k] = API[k]; }
  if(!global.$) global.$ = $;

  /* Dựng huy hiệu bản dựng trên MỌI trang nạp file này (18 trang) — không phải
     đi sửa từng trang, đúng quy tắc 2 mục 6 của CLAUDE.md.
     ⚠️ Chờ `DOMContentLoaded` vì phần lớn trang nạp script này trong <head>,
        lúc đó `document.body` còn chưa tồn tại. */
  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", mountVersion);
  } else { mountVersion(); }
})(window);
