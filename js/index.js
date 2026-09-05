/* ============================================================
   index.js — Trang chủ astroQ.org: landing "Sắp ra mắt" + waitlist
   Dùng lại: js/ui-common.js ($, getLang/setLang/initLang/markLangButtons,
   makeToast, esc) và js/icons.js (lic).
   Waitlist đi qua backend AstroqSV: POST /waitlist → DynamoDB + thư chào mừng
   bằng SES. localStorage["astroq-waitlist"] CHỈ là bản sao dự phòng khi mất mạng.
   ============================================================ */
(function(){
  "use strict";

  /* Ngày mở cửa chính thức (giờ Việt Nam, UTC+7) — dùng cho đồng hồ đếm ngược */
  var LAUNCH_AT = new Date("2026-08-20T00:00:00+07:00").getTime();
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  /* ============================ i18n ============================ */
  var I18N = {
    vi:{
      wiki_link:"Đọc thêm 10 bài kiến thức nền tảng trong astroQ.org Wiki →",
      foot_wiki:"Wiki",
      a_lang:"Ngôn ngữ",
      a_crew:"Phi hành đoàn đồng hành",
      a_comet:"Mèo Comet — phi công vũ trụ, linh vật của astroQ.org",
      a_byte:"Robot Byte — trợ lý AI, linh vật của astroQ.org",
      title:"astroQ.org — Khám Phá Ngân Hà Tri Thức | Vũ Trụ · AI · Lượng Tử",
      status:"TRẠM ASTROQ",
      eyebrow:"MISSION 001",
      h1:"Khám Phá Ngân Hà Tri Thức Cùng astroQ.org",
      lede:"Nền tảng học tập tương tác chủ đề Vũ trụ, AI & tư duy khoa học dành cho các nhà khám phá trẻ. Biến lý thuyết phức tạp thành các nhiệm vụ vũ trụ kỳ thú.",
      cd_label:"HỆ THỐNG MỞ CỬA SAU", cd_d:"ngày", cd_h:"giờ", cd_m:"phút", cd_s:"giây",
      cd_live:"HỆ THỐNG ĐÃ MỞ CỬA",
      hero_cta:"Nhận 100 Purple Meteors 🚀", hero_cta2:"astroQ.org là gì?",
      /* Chỉ hiện sau khi đồng hồ về 0 — xem `renderCountdown`. */
      hero_live:"Tìm hiểu ngay 🚀",
      crew_comet:"Mèo phi công vũ trụ — dẫn đường qua từng hành tinh và giao nhiệm vụ khám phá cho bạn.",
      crew_byte:"Robot trợ lý AI — giải thích thuật ngữ khó bằng ngôn ngữ của trẻ em và chấm bài quiz.",

      /* ⚠️ ĐÃ MỞ CỬA 20/08/2026 — chữ ở đây KHÔNG còn được nói theo thì tương lai.
         "Vé mời sớm" / "EARLY ACCESS" / "khi hệ thống ra mắt" đều đã hết nghĩa.
         ⚠️⚠️ VÀ PHẢI NÓI ĐÚNG CƠ CHẾ: `POST /waitlist` KHÔNG cộng tiền cho ai —
            nó chỉ ghi một bản ghi `WAITLIST#<email>`. 500 tt vào ví ở bước KHÁC:
            `GET /auth/activate` (AstroqSV) gọi `ClaimWaitlistBonusAsync` khi tài
            khoản được tạo, và CHỈ khi email tạo tài khoản TRÙNG email đã ghi danh.
            Câu cũ "nhận ngay 500" là hứa một thứ không xảy ra ở bước đó — người
            để lại email rồi ngồi đợi sẽ không bao giờ thấy tiền. */
      wl_tag:"QUÀ KHỞI ĐẦU · 100 PURPLE METEORS",
      wl_title:"Tạo Tài Khoản, Nhận 100 Purple Meteors!",
      wl_desc:"Tạo tài khoản miễn phí là có ngay <b>100 PURPLE METEORS</b> trong ví (đơn vị tiền thưởng trên astroQ.org) — dùng để nâng cấp phi thuyền &amp; mở khóa hành tinh.", wl_cta:"Tạo tài khoản 🚀",
      wl_hint:"Miễn phí. Chỉ cần email và mật khẩu.",
      // ⚠️ 4 khoá `mob_*` đã bỏ 29/08/2026 cùng dải khuyến nghị dùng máy tính; chữ
      //    nay nằm ở `explorer.html` (khoá `wideNote`/`wideNoteX`). Giữ lại ở đây là
      //    khoá khai mà không dùng — `check_pages` mục [1] bắt ngay.
      // Dùng khi server nhận được đăng ký nhưng SES chưa gửi được thư. Đừng bảo
      // "kiểm tra hòm thư" về một lá thư chưa đi.


      aeo_h2:"astroQ.org là gì?",
      aeo_answer:"astroQ.org là nền tảng giáo dục STEM gamification tương tác 3D, giúp trẻ em và người mới bắt đầu học Thiên văn học, Trí tuệ nhân tạo, Robotics và tư duy khoa học thông qua giao diện khoang lái phi thuyền và các nhiệm vụ khám phá ngân hà.",
      p1_t:"Thiên văn học", p1_d:"Hệ Mặt Trời, các vì sao và bản đồ ngân hà 3D.",
      p2_t:"Trí tuệ nhân tạo", p2_d:"Máy học nghĩ như thế nào, giải thích cho trẻ em.",
      p3_t:"Tư duy khoa học", p3_d:"Quan sát, đặt câu hỏi và kiểm chứng bằng nguồn thật.",
      p4_t:"Robotics", p4_d:"Robot cảm nhận, di chuyển và ra quyết định ra sao.",

      faq_h:"Câu hỏi thường gặp",
      q1:"astroQ.org là gì?",
      a1:"astroQ.org là nền tảng giáo dục STEM gamification tương tác 3D, giúp trẻ em và người mới bắt đầu học Thiên văn học, Trí tuệ nhân tạo, Robotics và tư duy khoa học thông qua giao diện khoang lái phi thuyền và các nhiệm vụ khám phá ngân hà.",
      q2:"astroQ.org dành cho ai?",
      a2:"astroQ.org dành cho trẻ em và người mới bắt đầu muốn tiếp cận Thiên văn học, AI và tư duy khoa học theo cách trực quan. Người học điều khiển khoang lái phi thuyền, nhận nhiệm vụ và khám phá từng hành tinh thay vì đọc lý thuyết khô khan.",
      q3:"astroQ.org có những chủ đề nào?",
      a3:"Bốn nhóm chủ đề chính: Thiên văn học và Hệ Mặt Trời, Trí tuệ nhân tạo, Tư duy khoa học, và Robotics. Mỗi chủ đề được chia thành các nhiệm vụ ngắn kèm quiz, bài đọc và mô phỏng 3D để người học tiến bộ theo cấp độ.",
      q4:"Purple Meteors là gì?",
      a4:"Purple Meteors (Thiên thạch tím) là đơn vị phần thưởng trong astroQ.org. Người học kiếm Purple Meteors khi hoàn thành quiz, đọc bài và chơi mini-game, rồi dùng để nâng cấp phi thuyền và mở khóa hành tinh mới.",
      q5:"astroQ.org đã mở cửa chưa?",
      a5:"astroQ.org đã mở cửa từ ngày 20/08/2026, vào chơi được ngay. Mỗi tài khoản tạo mới nhận 100 Purple Meteors khởi đầu, cộng vào ví ngay khi kích hoạt tài khoản qua email.",

      /* Dải mời sang bản ngôn ngữ kia. Chữ này hiện trên trang TIẾNG ANH cho
         khách được đoán là người Việt — nên nó viết bằng tiếng Việt. */
      ln_body:"Trang này đang hiển thị bằng tiếng Anh.",
      ln_cta:"Xem bản tiếng Việt →",
      ln_aria:"Gợi ý ngôn ngữ",
      ln_close:"Đóng gợi ý ngôn ngữ",
      foot_note:"Nền tảng học STEM tương tác cho nhà khám phá trẻ"
    },
    en:{
      wiki_link:"Read 10 foundational explainers in the astroQ.org Wiki →",
      foot_wiki:"Wiki",
      a_lang:"Language",
      a_crew:"Your companion crew",
      a_comet:"Comet the cat — space pilot, astroQ.org mascot",
      a_byte:"Byte the robot — AI assistant, astroQ.org mascot",
      title:"astroQ.org — Explore the Galaxy of Knowledge | Space · AI · Quantum",
      status:"ASTROQ STATION",
      eyebrow:"MISSION 001",
      h1:"Explore the Galaxy of Knowledge with astroQ.org",
      lede:"An interactive learning platform on Space, AI & scientific thinking for young explorers. We turn complex theory into thrilling cosmic missions.",
      cd_label:"SYSTEM GOES LIVE IN", cd_d:"days", cd_h:"hours", cd_m:"mins", cd_s:"secs",
      cd_live:"SYSTEM IS LIVE",
      hero_cta:"Get 100 Purple Meteors 🚀", hero_cta2:"What is astroQ.org?",
      hero_live:"Find out more 🚀",
      crew_comet:"Space-pilot cat — guides you planet by planet and hands out exploration missions.",
      crew_byte:"AI assistant robot — explains hard terms in kid-friendly language and grades your quizzes.",

      wl_tag:"STARTER GIFT · 100 PURPLE METEORS",
      wl_title:"Create An Account, Get 100 Purple Meteors!",
      wl_desc:"Create a free account and <b>100 PURPLE METEORS</b> land in your wallet right away (the reward currency on astroQ.org) — spend them upgrading your ship &amp; unlocking planets.", wl_cta:"Create an account 🚀",
      wl_hint:"Free. Just an email and a password.",
      // (4 khoá `mob_*` đã bỏ — xem ghi chú ở từ điển `vi`.)


      aeo_h2:"What is astroQ.org?",
      aeo_answer:"astroQ.org is an interactive 3D gamified STEM education platform that helps children and beginners learn Astronomy, Artificial Intelligence, Robotics and scientific thinking through a spaceship-cockpit interface and galaxy exploration missions.",
      p1_t:"Astronomy", p1_d:"The Solar System, the stars and a 3D galaxy map.",
      p2_t:"Artificial Intelligence", p2_d:"How machines learn to think, explained for kids.",
      p3_t:"Scientific Thinking", p3_d:"Observe, ask questions and check against real sources.",
      p4_t:"Robotics", p4_d:"How robots sense, move and make decisions.",

      faq_h:"Frequently asked questions",
      q1:"What is astroQ.org?",
      a1:"astroQ.org is an interactive 3D gamified STEM education platform that helps children and beginners learn Astronomy, Artificial Intelligence, Robotics and scientific thinking through a spaceship-cockpit interface and galaxy exploration missions.",
      q2:"Who is astroQ.org for?",
      a2:"astroQ.org is for children and beginners who want a visual way into Astronomy, AI and scientific thinking. Learners fly a spaceship cockpit, take on missions and explore planet by planet instead of reading dry theory.",
      q3:"Which topics does astroQ.org cover?",
      a3:"Four core tracks: Astronomy and the Solar System, Artificial Intelligence, Scientific Thinking, and Robotics. Each track is split into short missions with quizzes, readings and 3D simulations so learners progress level by level.",
      q4:"What are Purple Meteors?",
      a4:"Purple Meteors are the reward currency inside astroQ.org. Learners earn them by finishing quizzes, reading articles and playing mini-games, then spend them to upgrade their ship and unlock new planets.",
      q5:"Is astroQ.org open yet?",
      a5:"astroQ.org has been open since 20 August 2026 — you can start playing right away. Every new account gets 100 starter Purple Meteors, credited to the wallet as soon as the account is activated by email.",

      /* Hiện trên trang TIẾNG VIỆT cho khách quốc tế — nên viết bằng tiếng Anh.
         Mời một người Nhật sang bản tiếng Anh bằng một câu tiếng Việt thì dải
         này vô dụng đúng với người nó sinh ra để phục vụ. */
      ln_body:"This page is in Vietnamese.",
      ln_cta:"Read it in English →",
      ln_aria:"Language suggestion",
      ln_close:"Dismiss language suggestion",
      foot_note:"Interactive STEM learning for young explorers"
    }
  };

  /* ⚠️⚠️ NGÔN NGỮ CỦA TRANG CHỦ LẤY TỪ `<html lang>`, KHÔNG PHẢI TỪ `getLang()`.
     Đổi 07/08/2026 cùng lúc với việc tách `/en/`. Trang chủ nay có HAI URL TĨNH
     — `/` là tiếng Việt, `/en/` là tiếng Anh — nên ngôn ngữ là thuộc tính CỦA
     TRANG, không phải một phán đoán chạy lúc tải.
     ⚠️ Đây là điều kiện để bỏ được lỗi cũ: khi một URL phục vụ cả hai ngôn ngữ,
        `<title>` và chữ đổi sang tiếng Anh nhưng **2 khối JSON-LD mãi là tiếng
        Việt** — Google thấy dữ liệu có cấu trúc lệch nội dung, trên đúng trang
        DUY NHẤT được lập chỉ mục. Đừng gọi lại `getLang()` ở đây.
     `guessLang()` vẫn còn tác dụng, nhưng chỉ để CHỌN DẢI MỜI (xem initLangNote)
     và cho 17 trang app — chúng đều `noindex` nên không có rủi ro SEO nào. */
  var LANG = (document.documentElement.lang === "en") ? "en" : "vi";
  function t(k){ var d = I18N[LANG] || I18N.vi; return d[k] != null ? d[k] : k; }

  /* Thư mục `js/` suy từ chính thẻ <script> đang chạy.
     ⚠️ BẮT BUỘC: trang chủ có hai bản ở HAI ĐỘ SÂU thư mục, nên `import("./api.js")`
        — vốn giải theo URL của TÀI LIỆU vì đây là script cổ điển, không phải
        module — sẽ trỏ `/en/api.js` và 404. Form waitlist chết câm, đúng loại
        lỗi đã giết chính form này suốt 6 ngày (02/08/2026). */
  var JS_DIR = (function(){
    try{
      var s = document.currentScript && document.currentScript.src;
      if(s) return s.replace(/[^/]*$/, "");
    }catch(e){}
    return "js/";
  })();

  var toast = AstroQ.makeToast("toast", 2800);

  /* ============================ Ngôn ngữ ============================
     Không còn đổi ngôn ngữ TẠI CHỖ — nút VI/EN nay là <a href> sang URL kia.
     Hàm này chỉ đổ lại chữ từ từ điển (một phép kiểm chéo với HTML tĩnh) và vẽ
     những thứ do JS sinh ra: đồng hồ đếm ngược, lời báo lỗi, thẻ đã đăng ký. */
  function applyLang(lang){
    if(lang === "en" || lang === "vi") LANG = lang;
    document.documentElement.lang = LANG;
    document.title = t("title");
    AstroQ.applyTexts(t);            // nội dung + placeholder/title/aria-label/alt
    renderCountdown();
  }

  /* ============================ Icon 4 trụ kiến thức ============================ */
  function paintIcons(){
    /* ⚠️ `ic-think` -> `search` (kính lúp): trụ 3 đổi từ "Vật lý Lượng tử" sang "Tư duy
       khoa học" ngày 26/08/2026 — lý do đầy đủ ở chú thích khối `.pillars` trong
       index.html. Id ở HTML và khoá ở đây phải đổi CÙNG LÚC, lệch một bên là ô icon
       trống trơn mà không có lỗi nào báo. */
    var map = { "ic-astro":"telescope", "ic-ai":"cpu", "ic-think":"search", "ic-robot":"bot" };
    Object.keys(map).forEach(function(id){
      var el = $(id); if(el) el.innerHTML = lic(map[id]);
    });
  }

  /* ============================ Đếm ngược ============================ */
  function pad(n){ return (n < 10 ? "0" : "") + n; }
  function renderCountdown(){
    var left = LAUNCH_AT - Date.now();
    var lbl = $("cd-label");
    if(left <= 0){
      if(lbl) lbl.textContent = t("cd_live");
      ["cd-d","cd-h","cd-m","cd-s"].forEach(function(id){ $(id).textContent = "00"; });
      openDoor();
      return false;                                  // dừng vòng lặp
    }
    /* ⚠️⚠️ ĐÓNG CỬA LẠI — nhánh này MỚI (25/08/2026) và nó là nửa còn lại của việc
       đổi mặc định trong `index.html` sang trạng thái "đã mở cửa". Trước đây HTML
       xuất xưởng ở trạng thái ĐANG ĐẾM nên nhánh này không cần làm gì; nay HTML
       xuất xưởng ở trạng thái ĐÃ MỞ, nên nếu `LAUNCH_AT` là tương lai thì phải
       đóng lại, không thì trang chủ nói "đã mở cửa" trong khi chưa. Lý do đổi mặc
       định (cú nhảy bố cục 64px mỗi lượt nạp + nút vào chơi đến muộn 1,5s trên
       mạng chậm) ghi ở khối chú thích cạnh `#countdown` trong `index.html`.
       ⚠️ Bất biến theo số lần gọi, đúng như `openDoor()`: `classList.remove` và
          `hidden = true` chịu được gọi lại nhiều lần. */
    closeDoor();
    if(lbl) lbl.textContent = t("cd_label");
    var s = Math.floor(left / 1000);
    $("cd-d").textContent = pad(Math.floor(s / 86400));
    $("cd-h").textContent = pad(Math.floor(s % 86400 / 3600));
    $("cd-m").textContent = pad(Math.floor(s % 3600 / 60));
    $("cd-s").textContent = pad(s % 60);
    return true;
  }

  /* ============================ Mở cửa vào app ============================
     Gỡ `hidden` khỏi nút "Vào chơi ngay" và hạ nút waitlist xuống hạng phụ.

     ⚠️ BẤT BIẾN THEO SỐ LẦN GỌI. `renderCountdown()` chạy cả trong `applyLang()`
        (mỗi lần đổi ngôn ngữ) lẫn trong `ticker`, nên hàm này bị gọi lại nhiều
        lần sau khi đã mở — phải cho ra đúng một kết quả, không cộng dồn class.

     ⚠️ KHÔNG đụng chữ trong nút: `applyLang` đã lo phần đó qua `data-i18n`.
        Ghi chữ ở đây là dựng bản sao thứ hai của một chuỗi, và bản sao sẽ không
        đổi theo ngôn ngữ. */
  function openDoor(){
    var live = $("hero-live"), wl = $("hero-wl"), cd = $("countdown");
    if(live) live.hidden = false;
    if(wl){ wl.classList.remove("btn-primary"); wl.classList.add("btn-ghost"); }
    /* Thu 4 ô số lại, chỉ giữ huy hiệu "ĐÃ MỞ CỬA" — kiểu dáng ở
       `css/index.css`, mục "Đã mở cửa". Đếm ngược xong thì bốn ô đứng ở
       `00 00 00 00` vĩnh viễn, đọc ra như một cái đồng hồ hỏng.
       `classList.add` chịu được gọi nhiều lần, đúng bất biến đã ghi ở trên. */
    if(cd) cd.classList.add("live");
  }

  /* Nghịch đảo của `openDoor()` — dùng khi `LAUNCH_AT` còn ở tương lai. Giữ đúng
     ba thứ mà `openDoor` đổi, không nhiều hơn: nút vào chơi, hạng của nút waitlist,
     và lớp `live` của đồng hồ. ⚠️ KHÔNG đụng chữ trong nút — `applyLang` lo qua
     `data-i18n`, y như ghi chú ở `openDoor()`. */
  function closeDoor(){
    var live = $("hero-live"), wl = $("hero-wl"), cd = $("countdown");
    if(live) live.hidden = true;
    if(wl){ wl.classList.remove("btn-ghost"); wl.classList.add("btn-primary"); }
    if(cd) cd.classList.remove("live");
  }

  /* ============================ Khởi tạo ============================ */
  $("year").textContent = String(new Date().getFullYear());
  paintIcons();
  applyLang(LANG);
  /* ⚠️ KHÔNG gọi `AstroQ.initLang` ở trang chủ nữa (bỏ 07/08/2026).
     `initLang` gắn nút đổi ngôn ngữ TẠI CHỖ và tự đoán lại ngôn ngữ — cả hai
     đều sai với trang chủ từ khi tách `/` và `/en/`: nút nay là <a href> sang
     URL kia (crawler đi được, đó là nửa còn lại của hreflang), còn ngôn ngữ thì
     do chính URL quyết. Gọi lại nó là đưa về đúng cái lỗi JSON-LD lệch nội dung.
     17 trang app vẫn dùng `initLang` như cũ — chúng `noindex`, một URL một trang. */

  var ticker = setInterval(function(){
    if(!renderCountdown()) clearInterval(ticker);
  }, 1000);

  /* ⚠️⚠️ KHUYẾN NGHỊ DÙNG MÁY TÍNH ĐÃ BỎ KHỎI TRANG CHỦ (29/08/2026) — ĐỪNG DỰNG LẠI
     Ở ĐÂY. Chủ dự án chốt đặt lời khuyên đó "ở phần cần nó nhất", và nay nó là kind
     `wide` của dải `#perf-note` trong `explorer.html` (bản đồ 3D — thứ THẬT SỰ cần
     màn rộng). Lý do đầy đủ + số đo ghi ở khối markup đã bỏ trong `index.html`.
     ⚠️ Ba bài học của dải cũ KHÔNG mất, chúng đi theo sang `explorer.html`: nhận diện
        bằng `(max-width:860px) and (pointer:coarse)` chứ không chỉ bề rộng · chỉ nhắc
        một lần mỗi máy · không khoá cuộn, không bẫy tiêu điểm.
     ⚠️ `isSmallTouch()` và `MOB_KEY` xoá theo vì hết người gọi — một hàm không ai gọi
        là mã chết, thứ dự án đã trả giá nhiều lần (`termsData.ts` phải sửa hai lần,
        `AstroQRanks.ALL` ngủ 8 ngày). Bản dùng thật nay nằm ở `explorer.html`. */

  /* ============================================================
     DẢI MỜI SANG BẢN NGÔN NGỮ KIA
     ⚠️ Chữ lấy từ từ điển của NGÔN NGỮ KIA, không phải của trang. Xem lý do ở
        khối markup `#lang-note` trong index.html.
     ⚠️ Chỉ hiện khi phán đoán KHÁC ngôn ngữ của trang VÀ người dùng chưa từng
        tự chọn (`astroq-lang` còn trống). Đã tự chọn rồi mà vẫn mời là cãi lại
        một quyết định họ đã đưa ra.
     ============================================================ */
  var LN_KEY = "astroq-lang-note";

  function initLangNote(){
    var box = document.getElementById("lang-note");
    if(!box) return;
    var x = document.getElementById("ln-x");

    var other = (LANG === "en") ? "vi" : "en";
    var d = I18N[other] || {};
    var txt = document.getElementById("ln-txt");
    var go  = document.getElementById("ln-go");
    if(txt) txt.textContent = d.ln_body || "";
    if(go){
      go.textContent = d.ln_cta || "";
      go.setAttribute("href", other === "en" ? "/en/" : "/");
      go.setAttribute("hreflang", other);
    }
    box.setAttribute("aria-label", d.ln_aria || "Language");
    if(x) x.setAttribute("aria-label", d.ln_close || "Dismiss");

    function hide(){
      box.classList.remove("show");
      try{ localStorage.setItem(LN_KEY, "1"); }catch(e){}
      setTimeout(function(){ box.hidden = true; }, 260);
    }
    if(x) x.addEventListener("click", hide);

    var seen = false, chosen = null;
    try{ seen = localStorage.getItem(LN_KEY) === "1"; }catch(e){}
    try{ chosen = localStorage.getItem("astroq-lang"); }catch(e){}
    if(seen || chosen) return;

    var guess = (AstroQ.guessLang ? AstroQ.guessLang() : LANG);
    if(guess === LANG) return;              /* đang ở đúng bản rồi */

    setTimeout(function(){
      /* ⚠️ Khối đo `--ln-lift` đã bỏ 29/08/2026 cùng dải `.mob-note`: nó dựng ra để
         hai dải cùng neo đáy khỏi chồng nhau, mà nay trang chủ chỉ còn MỘT dải đáy
         nên không còn gì để tránh. Thêm dải đáy thứ hai thì phải dựng lại nó. */
      box.hidden = false; box.classList.add("show");
    }, 1200);
  }

  initLangNote();

})();
