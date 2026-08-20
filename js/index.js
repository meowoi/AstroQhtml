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
      lede:"Nền tảng học tập tương tác chủ đề Vũ trụ, AI & Vật lý Lượng tử dành cho các nhà khám phá trẻ. Biến lý thuyết phức tạp thành các nhiệm vụ vũ trụ kỳ thú.",
      cd_label:"HỆ THỐNG MỞ CỬA SAU", cd_d:"ngày", cd_h:"giờ", cd_m:"phút", cd_s:"giây",
      cd_live:"HỆ THỐNG ĐÃ MỞ CỬA",
      hero_cta:"Nhận 100 Purple Meteors 🚀", hero_cta2:"astroQ.org là gì?",
      /* Chỉ hiện sau khi đồng hồ về 0 — xem `renderCountdown`. */
      hero_live:"Vào chơi ngay 🚀",
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
      mob_title:"Trải nghiệm tốt nhất trên máy tính",
      mob_body:"astroQ có bản đồ thiên hà 3D và mini-game cần màn hình rộng. Bạn vẫn xem được trang này trên điện thoại, nhưng hãy mở bằng <b>laptop hoặc PC</b> để chơi trọn vẹn nhé!",
      mob_aria:"Khuyến nghị thiết bị", mob_close:"Đã hiểu, đóng",
      // Dùng khi server nhận được đăng ký nhưng SES chưa gửi được thư. Đừng bảo
      // "kiểm tra hòm thư" về một lá thư chưa đi.


      aeo_h2:"astroQ.org là gì?",
      aeo_answer:"astroQ.org là nền tảng giáo dục STEM gamification tương tác 3D, giúp trẻ em và người mới bắt đầu học Thiên văn học, Vật lý Lượng tử, AI và Robotics thông qua giao diện khoang lái phi thuyền và các nhiệm vụ khám phá ngân hà.",
      p1_t:"Thiên văn học", p1_d:"Hệ Mặt Trời, các vì sao và bản đồ ngân hà 3D.",
      p2_t:"Trí tuệ nhân tạo", p2_d:"Máy học nghĩ như thế nào, giải thích cho trẻ em.",
      p3_t:"Vật lý Lượng tử", p3_d:"Hạt, sóng và những điều kỳ lạ nhất của vũ trụ.",
      p4_t:"Robotics", p4_d:"Robot cảm nhận, di chuyển và ra quyết định ra sao.",

      faq_h:"Câu hỏi thường gặp",
      q1:"astroQ.org là gì?",
      a1:"astroQ.org là nền tảng giáo dục STEM gamification tương tác 3D, giúp trẻ em và người mới bắt đầu học Thiên văn học, Vật lý Lượng tử, AI và Robotics thông qua giao diện khoang lái phi thuyền và các nhiệm vụ khám phá ngân hà.",
      q2:"astroQ.org dành cho ai?",
      a2:"astroQ.org dành cho trẻ em và người mới bắt đầu muốn tiếp cận Thiên văn học, AI và Vật lý Lượng tử theo cách trực quan. Người học điều khiển khoang lái phi thuyền, nhận nhiệm vụ và khám phá từng hành tinh thay vì đọc lý thuyết khô khan.",
      q3:"astroQ.org có những chủ đề nào?",
      a3:"Bốn nhóm chủ đề chính: Thiên văn học và Hệ Mặt Trời, Trí tuệ nhân tạo, Vật lý Lượng tử, và Robotics. Mỗi chủ đề được chia thành các nhiệm vụ ngắn kèm quiz, bài đọc và mô phỏng 3D để người học tiến bộ theo cấp độ.",
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
      lede:"An interactive learning platform on Space, AI & Quantum Physics for young explorers. We turn complex theory into thrilling cosmic missions.",
      cd_label:"SYSTEM GOES LIVE IN", cd_d:"days", cd_h:"hours", cd_m:"mins", cd_s:"secs",
      cd_live:"SYSTEM IS LIVE",
      hero_cta:"Get 100 Purple Meteors 🚀", hero_cta2:"What is astroQ.org?",
      hero_live:"Play now 🚀",
      crew_comet:"Space-pilot cat — guides you planet by planet and hands out exploration missions.",
      crew_byte:"AI assistant robot — explains hard terms in kid-friendly language and grades your quizzes.",

      wl_tag:"STARTER GIFT · 100 PURPLE METEORS",
      wl_title:"Create An Account, Get 100 Purple Meteors!",
      wl_desc:"Create a free account and <b>100 PURPLE METEORS</b> land in your wallet right away (the reward currency on astroQ.org) — spend them upgrading your ship &amp; unlocking planets.", wl_cta:"Create an account 🚀",
      wl_hint:"Free. Just an email and a password.",
      mob_title:"Best experienced on a computer",
      mob_body:"astroQ has a 3D galaxy map and mini-games that need a wide screen. You can still browse this page on a phone, but open it on a <b>laptop or PC</b> for the full ride!",
      mob_aria:"Device recommendation", mob_close:"Got it, dismiss",


      aeo_h2:"What is astroQ.org?",
      aeo_answer:"astroQ.org is an interactive 3D gamified STEM education platform that helps children and beginners learn Astronomy, Quantum Physics, AI and Robotics through a spaceship-cockpit interface and galaxy exploration missions.",
      p1_t:"Astronomy", p1_d:"The Solar System, the stars and a 3D galaxy map.",
      p2_t:"Artificial Intelligence", p2_d:"How machines learn to think, explained for kids.",
      p3_t:"Quantum Physics", p3_d:"Particles, waves and the strangest rules of the universe.",
      p4_t:"Robotics", p4_d:"How robots sense, move and make decisions.",

      faq_h:"Frequently asked questions",
      q1:"What is astroQ.org?",
      a1:"astroQ.org is an interactive 3D gamified STEM education platform that helps children and beginners learn Astronomy, Quantum Physics, AI and Robotics through a spaceship-cockpit interface and galaxy exploration missions.",
      q2:"Who is astroQ.org for?",
      a2:"astroQ.org is for children and beginners who want a visual way into Astronomy, AI and Quantum Physics. Learners fly a spaceship cockpit, take on missions and explore planet by planet instead of reading dry theory.",
      q3:"Which topics does astroQ.org cover?",
      a3:"Four core tracks: Astronomy and the Solar System, Artificial Intelligence, Quantum Physics, and Robotics. Each track is split into short missions with quizzes, readings and 3D simulations so learners progress level by level.",
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
    var map = { "ic-astro":"telescope", "ic-ai":"cpu", "ic-quantum":"atom", "ic-robot":"bot" };
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

  /* ============================================================
     KHUYẾN NGHỊ DÙNG MÁY TÍNH — chỉ trên thiết bị cảm ứng màn hình nhỏ.

     ⚠️ NHẬN DIỆN BẰNG `pointer: coarse` CỘNG BỀ RỘNG, KHÔNG CHỈ BỀ RỘNG.
        Chỉ xét bề rộng thì một cửa sổ Chrome kéo hẹp trên laptop cũng bị nhắc
        "hãy dùng laptop" — vô nghĩa và làm người dùng mất tin. Chỉ xét cảm ứng thì
        laptop màn hình chạm (Windows 2-trong-1) và iPad Pro 12,9" cũng bị nhắc, dù
        chúng dư sức chạy. Hai điều kiện cùng lúc mới ra đúng "điện thoại / tablet nhỏ".

     ⚠️ CHỈ NHẮC MỘT LẦN MỖI MÁY. Nhắc lại mỗi lần vào là quấy rối, và người dùng sẽ
        học cách bấm X mà không đọc. Cờ ở localStorage; bị chặn thì im lặng bỏ qua.

     ⚠️ KHÔNG khoá cuộn, KHÔNG bẫy tiêu điểm. Xem ghi chú ở markup: trang này đã
        go-live và Google lập chỉ mục theo mobile-first — lớp phủ chắn nội dung trên
        điện thoại bị xếp vào "intrusive interstitial" và ăn phạt xếp hạng.
     ============================================================ */
  var MOB_KEY = "astroq-mob-note";

  function mobNoteSeen(){
    try { return localStorage.getItem(MOB_KEY) === "1"; } catch(e){ return false; }
  }
  function markMobNoteSeen(){
    try { localStorage.setItem(MOB_KEY, "1"); } catch(e){}
  }
  function isSmallTouch(){
    try {
      return window.matchMedia &&
             window.matchMedia("(max-width: 860px) and (pointer: coarse)").matches;
    } catch(e){ return false; }
  }

  function initMobNote(){
    var box = document.getElementById("mob-note");
    if(!box) return;
    var x = document.getElementById("mob-x");
    if(x) x.addEventListener("click", function(){
      box.classList.remove("show");
      markMobNoteSeen();
      // Chờ hiệu ứng mờ xong mới ẩn hẳn, không thì nó biến mất cụt ngủn.
      setTimeout(function(){ box.hidden = true; }, 260);
    });
    if(!isSmallTouch() || mobNoteSeen()) return;
    /* Chờ một nhịp để dải không bật lên giữa lúc trang đang dựng — nó là lời nhắc,
       không phải thứ đầu tiên người dùng phải xử lý. */
    setTimeout(function(){ box.hidden = false; box.classList.add("show"); }, 900);
  }

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
      /* Hai dải cùng neo đáy sẽ chồng nhau — khách quốc tế vào bằng điện thoại
         là ca hoàn toàn có thật. Đo dải kia rồi nâng dải này lên trên. */
      var mob = document.getElementById("mob-note");
      if(mob && !mob.hidden){
        var h = Math.round(mob.getBoundingClientRect().height);
        if(h > 0) box.style.setProperty("--ln-lift", (h + 10) + "px");
      }
      box.hidden = false; box.classList.add("show");
    }, 1200);
  }

  initMobNote();
  initLangNote();

})();
