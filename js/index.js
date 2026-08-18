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
  var LS_WAITLIST = "astroq-waitlist";      // bản sao dự phòng trên máy khách: [{ email, ts, lang, sent }]
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
      hero_cta:"Nhận 500 Purple Meteors 🚀", hero_cta2:"astroQ.org là gì?",
      /* Chỉ hiện sau khi đồng hồ về 0 — xem `renderCountdown`. */
      hero_live:"Vào chơi ngay 🚀",
      crew_comet:"Mèo phi công vũ trụ — dẫn đường qua từng hành tinh và giao nhiệm vụ khám phá cho bạn.",
      crew_byte:"Robot trợ lý AI — giải thích thuật ngữ khó bằng ngôn ngữ của trẻ em và chấm bài quiz.",

      wl_tag:"BOARDING PASS · EARLY ACCESS",
      wl_title:"Đăng Ký Nhận Vé Mời Sớm & Nhận Quà Khởi Đầu!",
      wl_desc:"Đăng ký ngay hôm nay để nhận ngay <b>500 PURPLE METEORS</b> (đơn vị tiền thưởng trên astroQ.org) dùng để nâng cấp phi thuyền &amp; mở khóa hành tinh ngay khi hệ thống ra mắt!",
      wl_label:"Địa chỉ email", wl_ph:"phihanhgia@astroq.org",
      wl_cta:"Nhận 500 Purple Meteors 🚀",
      wl_sending:"Đang gửi...",
      wl_hint:"Không spam. Chỉ một thư chào mừng.",
      mob_title:"Trải nghiệm tốt nhất trên máy tính",
      mob_body:"astroQ có bản đồ thiên hà 3D và mini-game cần màn hình rộng. Bạn vẫn xem được trang này trên điện thoại, nhưng hãy mở bằng <b>laptop hoặc PC</b> để chơi trọn vẹn nhé!",
      mob_aria:"Khuyến nghị thiết bị", mob_close:"Đã hiểu, đóng",
      done_title:"🚀 Đã giữ chỗ & 500 Purple Meteors thành công!",
      done_body:'Kiểm tra hòm thư của bạn nhé — chỗ của <b id="wl-done-mail">bạn</b> đã được giữ. 500 Purple Meteors sẽ nằm sẵn trong khoang khi bạn vào.',
      // Dùng khi server nhận được đăng ký nhưng SES chưa gửi được thư. Đừng bảo
      // "kiểm tra hòm thư" về một lá thư chưa đi.
      done_body_nomail:'Đã ghi nhận email của <b id="wl-done-mail">bạn</b>. Thư xác nhận đang gặp trục trặc nên có thể chưa tới, nhưng chỗ của bạn vẫn được giữ.',
      done_again:"Đăng ký email khác",

      err_empty:"Nhập email của bạn để nhận 500 Purple Meteors nhé!",
      err_format:"Email chưa đúng định dạng — kiểm tra lại giúp Byte nhé.",
      ok_short:"Ghi danh thành công! 500 {tt} đang chờ bạn.",
      ok_dup:"Email này đã có trong phi hành đoàn — đã cập nhật lại!",
      err_send:"Trạm mặt đất chưa nhận được tín hiệu. Kiểm tra lại email rồi thử lần nữa nhé.",
      err_net:"Mất kết nối tới trạm. Email đã được giữ tạm trên máy bạn — thử lại sau vài giây nhé.",

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
      q3:"astroQ.org dạy những chủ đề nào?",
      a3:"Bốn nhóm chủ đề chính: Thiên văn học và Hệ Mặt Trời, Trí tuệ nhân tạo, Vật lý Lượng tử, và Robotics. Mỗi chủ đề được chia thành các nhiệm vụ ngắn kèm quiz, bài đọc và mô phỏng 3D để người học tiến bộ theo cấp độ.",
      q4:"Purple Meteors là gì?",
      a4:"Purple Meteors (Thiên thạch tím) là đơn vị phần thưởng trong astroQ.org. Người học kiếm Purple Meteors khi hoàn thành quiz, đọc bài và chơi mini-game, rồi dùng để nâng cấp phi thuyền và mở khóa hành tinh mới.",
      q5:"Khi nào astroQ.org ra mắt?",
      a5:"astroQ.org mở cửa ngày 20/08/2026. Người đăng ký bằng email nhận 500 Purple Meteors khởi đầu.",

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
      hero_cta:"Get 500 Purple Meteors 🚀", hero_cta2:"What is astroQ.org?",
      hero_live:"Play now 🚀",
      crew_comet:"Space-pilot cat — guides you planet by planet and hands out exploration missions.",
      crew_byte:"AI assistant robot — explains hard terms in kid-friendly language and grades your quizzes.",

      wl_tag:"BOARDING PASS · EARLY ACCESS",
      wl_title:"Join the Waitlist & Claim Your Starter Gift!",
      wl_desc:"Sign up today and get <b>500 PURPLE METEORS</b> (the reward currency on astroQ.org) to upgrade your ship &amp; unlock planets the moment we launch!",
      wl_label:"Email address", wl_ph:"astronaut@astroq.org",
      wl_cta:"Claim 500 Purple Meteors 🚀",
      wl_sending:"Sending...",
      wl_hint:"No spam. Just one welcome email.",
      mob_title:"Best experienced on a computer",
      mob_body:"astroQ has a 3D galaxy map and mini-games that need a wide screen. You can still browse this page on a phone, but open it on a <b>laptop or PC</b> for the full ride!",
      mob_aria:"Device recommendation", mob_close:"Got it, dismiss",
      done_title:"🚀 Your spot & 500 Purple Meteors are secured!",
      done_body:'Check your inbox — your spot is saved for <b id="wl-done-mail">you</b>. 500 Purple Meteors will be waiting in your cockpit when you log in.',
      done_body_nomail:'We saved the spot for <b id="wl-done-mail">you</b>. The confirmation email hit a snag and may not arrive, but your spot is held.',
      done_again:"Use another email",

      err_empty:"Enter your email to grab 500 Purple Meteors!",
      err_format:"That email looks off — mind double-checking it for Byte?",
      ok_short:"You're in! 500 {tt} are waiting for you.",
      ok_dup:"This email was already on the crew list — record updated!",
      err_send:"Ground control didn't get that. Double-check the address and try once more.",
      err_net:"Lost contact with the station. Your email is saved locally — try again in a moment.",

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
      q3:"Which topics does astroQ.org teach?",
      a3:"Four core tracks: Astronomy and the Solar System, Artificial Intelligence, Quantum Physics, and Robotics. Each track is split into short missions with quizzes, readings and 3D simulations so learners progress level by level.",
      q4:"What are Purple Meteors?",
      a4:"Purple Meteors are the reward currency inside astroQ.org. Learners earn them by finishing quizzes, reading articles and playing mini-games, then spend them to upgrade their ship and unlock new planets.",
      q5:"When does astroQ.org launch?",
      a5:"astroQ.org opens on 20 August 2026. Everyone who signs up by email gets 500 starter Purple Meteors.",

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
    paintErr();                        // lời báo lỗi đang hiện phải dịch theo, không đứng lại ở tiếng cũ
    if(joined) paintDone(joined, joinedMailed);  // giữ nguyên trạng thái đã đăng ký khi đổi ngôn ngữ
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
    var live = $("hero-live"), wl = $("hero-wl");
    if(live) live.hidden = false;
    if(wl){ wl.classList.remove("btn-primary"); wl.classList.add("btn-ghost"); }
  }

  /* ============================ Kho waitlist (localStorage) ============================ */
  function readList(){
    try{
      var raw = JSON.parse(localStorage.getItem(LS_WAITLIST) || "[]");
      return Array.isArray(raw) ? raw : [];
    }catch(e){ return []; }
  }
  function writeList(list){
    try{ localStorage.setItem(LS_WAITLIST, JSON.stringify(list)); }catch(e){}
  }

  /* Lưu bản sao vào máy khách. Luôn chạy dù server nhận được hay không, để
     không mất lead khi mạng hỏng — cờ "sent" cho biết đã lên server hay chưa. */
  /* ⚠️ `mailed` PHẢI được lưu cùng — lỗi có sẵn, sửa 07/08/2026.
     Trước đó bản ghi chỉ có `sent`, nên lúc mở lại trang (F5, hay bấm sang bản
     ngôn ngữ kia) thẻ "đã đăng ký" luôn dựng lại bằng câu MẶC ĐỊNH
     *"Kiểm tra hòm thư của bạn nhé"* — kể cả khi SES vừa báo gửi hỏng. Đó đúng
     là lời hứa hão mà cả lượt việc 02/08/2026 sinh ra để bỏ: thư không đi mà
     vẫn bảo người ta đi xem hòm thư. */
  function backup(email, sent, mailed){
    var list = readList();
    var rec = { email: email, ts: new Date().toISOString(), lang: LANG,
                sent: !!sent, mailed: (mailed !== false) }, dup = false;
    for(var i = 0; i < list.length; i++){
      if(list[i] && list[i].email === email){ list[i] = rec; dup = true; break; }
    }
    if(!dup) list.push(rec);
    writeList(list);
    return dup;                                      // true = email này đã đăng ký trước đó
  }

  /* ============================ Gửi lên backend ============================
     POST /waitlist của AstroqSV: lưu vào DynamoDB rồi gửi thư chào mừng qua SES.
     Trả { ok, dup, mailSent }.

     ⚠️ NẠP `js/api.js` BẰNG IMPORT ĐỘNG, không đặt thẻ <script> ở index.html.
     Trang chủ là trang DUY NHẤT được lập chỉ mục và đang tối ưu SEO/AEO — nó cố ý
     không nạp SDK Firebase (233 KB) vì lý do đó. `js/api.js` chỉ ~4 KB nhưng vẫn là
     một lượt tải mà 99% khách ghé qua không cần: chỉ người thật sự bấm gửi mới cần.
     Cùng lối `js/firebase-auth.js` đã dùng. Nhớ module lại để bấm lần hai không tải lại. */
  var apiMod = null;
  function api(){
    if(apiMod) return apiMod;
    apiMod = import(JS_DIR + "api.js");   /* xem JS_DIR: trang chu co 2 do sau thu muc */
    return apiMod;
  }

  function submitWaitlist(email){
    return api().then(function(m){
      return m.apiPost("/waitlist", {
        email: email,
        lang:  LANG,                                 // để biết gửi thư bản VI hay EN
        hp:    ($("wl-gotcha") || {}).value || "",    // bẫy bot, server lọc lại lần nữa
        // Nhan chien dich, de biet bai fanpage nao ra nguoi that. Rong khi khong co.
        src:   (window.AstroQUtm ? AstroQUtm.get() : "")
      });
    }).then(function(r){
      // apiPost không bao giờ ném lỗi — luôn trả { ok, status, data, netError? }.
      if(r.netError || r.notConfigured) return { ok:false, net:true };
      if(!r.ok) return { ok:false, status:r.status, code:(r.data && r.data.code) || "" };
      return { ok:true, dup:!!(r.data && r.data.dup), mailSent:(r.data && r.data.mailSent) !== false };
    });
  }

  /* ============================ Form ============================ */
  var form = $("wl-form"), input = $("wl-email"), submitBtn = $("wl-submit"),
      doneBox = $("wl-done"), errBox = $("wl-err"), joined = null, joinedMailed = true;

  /* ---------- Lời báo lỗi NGAY DƯỚI ô nhập ----------
     Không chỉ dựa vào toast: toast neo ở đỉnh khung nhìn (`.toast{top:22px}` trong
     css/index.css) nên khi người dùng đang ở khối waitlist cuối trang thì nó cách
     ô email ~465px — đo ngày 02/08/2026 — tức nằm ngoài chỗ họ đang nhìn đúng lúc
     cần đọc nhất. Bấm nút mà chỉ có viền đỏ thì không ai biết mình thiếu gì.
     Giữ KHOÁ i18n chứ không giữ chuỗi, để đổi VI/EN giữa chừng thì câu dịch theo. */
  var errKey = null;
  var ERR_IC = '<svg class="lic" viewBox="0 0 24 24" aria-hidden="true">' +
               '<circle cx="12" cy="12" r="9"/><path d="M12 7.4v5.2"/><path d="M12 16.3h.01"/></svg>';

  function paintErr(){
    if(!errBox) return;
    if(!errKey){ errBox.hidden = true; errBox.textContent = ""; return; }
    errBox.innerHTML = ERR_IC + "<span>" + AstroQ.esc(t(errKey)) + "</span>";
    errBox.hidden = false;
  }
  function showErr(key){
    errKey = key;
    input.classList.add("invalid");
    input.setAttribute("aria-invalid", "true");
    paintErr();
    input.focus();
    toast(t(key), "bad");
  }
  function clearErr(){
    errKey = null;
    input.classList.remove("invalid");
    input.removeAttribute("aria-invalid");
    paintErr();
  }

  /* ⚠️ `mailed` KHÔNG phải chi tiết thừa. Thẻ thành công mặc định viết "Kiểm tra hòm
     thư của bạn nhé" — câu đó chỉ đúng khi SES đã nhận thư. SES hỏng mà vẫn nói vậy là
     bắt trẻ ngồi chờ một lá thư không bao giờ tới; khi đó dùng câu `done_body_nomail`
     nói thật rằng chỗ đã giữ nhưng thư đang trục trặc.
     Đổi luôn `data-i18n-html` để lần đổi VI/EN sau vẫn ra đúng câu. */
  function paintDone(email, mailed){
    joined = email;
    joinedMailed = (mailed !== false);
    form.hidden = true;
    doneBox.hidden = false;
    var msgEl = $("wl-done-msg");
    if(msgEl){
      var key = joinedMailed ? "done_body" : "done_body_nomail";
      msgEl.setAttribute("data-i18n-html", key);
      msgEl.innerHTML = t(key);
    }
    var slot = $("wl-done-mail");                     // do data-i18n-html render lại nên tìm mỗi lần
    if(slot) slot.textContent = email;
  }

  function resetForm(){
    joined = null;
    doneBox.hidden = true;
    form.hidden = false;
    input.value = "";
    clearErr();
    input.focus();
  }

  function setLoading(on){
    submitBtn.disabled = on;
    submitBtn.textContent = on ? t("wl_sending") : t("wl_cta");
  }

  form.addEventListener("submit", function(e){
    e.preventDefault();
    /* ⚠️ BẪY BOT: id PHẢI khớp markup (`wl-gotcha`), và phải đọc ra biến rồi mới
       kiểm. Trước 02/08/2026 dòng này gọi thẳng `$("wl-company").value` — không có
       id đó trong index.html nên nó ném TypeError NGAY SAU `preventDefault()` và
       giết cả hàm gửi form: không lời nhắc khi bỏ trống, không gọi server,
       không thẻ "đã đăng ký". Trang trông như còn sống vì lỗi chỉ nằm ở console. */
    var hp = $("wl-gotcha");
    if(hp && hp.value) return;                        // bot điền bẫy → bỏ qua im lặng

    var email = input.value.trim().toLowerCase();
    if(!email)                return showErr("err_empty");
    if(!EMAIL_RE.test(email)) return showErr("err_format");
    clearErr();

    setLoading(true);
    submitWaitlist(email).then(function(res){
      setLoading(false);
      if(!res.ok){
        backup(email, false);                        // vẫn giữ lead trên máy khách
        if(window.console) console.warn("[waitlist] /waitlist", res.status || 0, res.code || "");
        // Mất mạng thì nói mất mạng (thử lại là được); server từ chối thì bảo xem lại email.
        return showErr(res.net ? "err_net" : "err_send");
      }
      // Server mới là nơi biết email này đã có trong danh sách chưa — bản sao trong
      // máy chỉ biết chuyện của MÁY NÀY, nên đổi máy là nó báo "mới" cho một địa chỉ cũ.
      backup(email, true, res.mailSent);
      input.value = "";                              // reset ô nhập
      clearErr();
      paintDone(email, res.mailSent);
      toast(res.dup ? t("ok_dup") : t("ok_short"), "ok");
      doneBox.scrollIntoView({ behavior:"smooth", block:"center" });
    }).catch(function(){                             // import("./api.js") hỏng, hoặc lỗi bất ngờ
      setLoading(false);
      backup(email, false);
      showErr("err_net");
    });
  });

  input.addEventListener("input", clearErr);
  $("wl-again").addEventListener("click", resetForm);

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

  /* Nếu máy này đã đăng ký trước đó thì hiện luôn trạng thái thành công.
     Chỉ tính bản ghi đã LÊN ĐƯỢC server (`sent`): bản ghi `sent:false` là lượt gửi
     hỏng, hiện thẻ "đã đăng ký" cho nó là nói với người ta rằng họ đã có chỗ trong
     khi server chưa biết gì — và họ sẽ không thử lại nữa. */
  var saved = readList().filter(function(r){ return r && r.sent; });
  if(saved.length){
    var last = saved[saved.length - 1];
    /* `mailed !== false` chứ không phải `!!last.mailed`: bản ghi CŨ (lưu trước
       07/08/2026) không có trường này, và với chúng thì "đã gửi được" là phỏng
       đoán đúng hơn — chúng được lưu ở thời mà mọi lượt gửi hỏng đều `sent:false`. */
    paintDone(last.email, last.mailed !== false);
  }

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
