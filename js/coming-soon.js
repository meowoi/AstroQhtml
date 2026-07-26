/* ============================================================
   coming-soon.js — Landing page waitlist của astroQ.org
   Dùng lại: js/ui-common.js ($, getLang/setLang/initLang/markLangButtons,
   makeToast, esc) và js/icons.js (lic).
   Không backend: email lưu vào localStorage["astroq-waitlist"] và
   submitWaitlist() mô phỏng một lời gọi API (đổi sang fetch thật ở 1 chỗ).
   ============================================================ */
(function(){
  "use strict";

  /* Ngày mở cửa chính thức (giờ Việt Nam, UTC+7) — dùng cho đồng hồ đếm ngược */
  var LAUNCH_AT = new Date("2026-08-01T00:00:00+07:00").getTime();
  var LS_WAITLIST = "astroq-waitlist";      // [{ email, ts, lang }]
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  /* ============================ i18n ============================ */
  var I18N = {
    vi:{
      title:"astroQ.org — Khám Phá Ngân Hà Tri Thức | Sắp Ra Mắt 8/2026",
      status:"TRẠM ĐANG KHỞI ĐỘNG",
      eyebrow:"PRE-LAUNCH · MISSION 001",
      h1:"Khám Phá Ngân Hà Tri Thức Cùng astroQ.org",
      lede:"Nền tảng học tập tương tác chủ đề Vũ trụ, AI & Vật lý Lượng tử dành cho các nhà khám phá trẻ. Biến lý thuyết phức tạp thành các nhiệm vụ vũ trụ kỳ thú.",
      cd_label:"HỆ THỐNG MỞ CỬA SAU", cd_d:"ngày", cd_h:"giờ", cd_m:"phút", cd_s:"giây",
      cd_live:"HỆ THỐNG ĐÃ MỞ CỬA",
      hero_cta:"Nhận vé mời sớm 🚀", hero_cta2:"astroQ.org là gì?",
      crew_comet:"Mèo phi công vũ trụ — dẫn đường qua từng hành tinh và giao nhiệm vụ khám phá cho bạn.",
      crew_byte:"Robot trợ lý AI — giải thích thuật ngữ khó bằng ngôn ngữ của trẻ em và chấm bài quiz.",

      wl_tag:"BOARDING PASS · EARLY ACCESS",
      wl_title:"Đăng Ký Nhận Vé Mời Sớm & Nhận Quà Khởi Đầu!",
      wl_desc:"Đăng ký ngay hôm nay để nhận ngay <b>500 PURPLE METEORS</b> (đơn vị tiền thưởng trên astroQ.org) dùng để nâng cấp phi thuyền &amp; mở khóa hành tinh ngay khi hệ thống ra mắt!",
      wl_label:"Địa chỉ email", wl_ph:"phihanhgia@astroq.org",
      wl_cta:"Nhận 500 Purple Meteors & Vé Sớm 🚀",
      wl_sending:"Đang gửi tín hiệu…",
      wl_hint:"Không spam. Nhận thông báo ra mắt chính thức vào đầu tháng 8/2026.",
      done_title:"Đã ghi danh vào phi hành đoàn!",
      done_body:'Vé mời sớm đã được giữ cho <b id="wl-done-mail">bạn</b>. 500 Purple Meteors sẽ nằm sẵn trong khoang khi astroQ.org mở cửa.',
      done_again:"Đăng ký email khác",

      err_empty:"Nhập email của bạn để nhận vé mời sớm nhé!",
      err_format:"Email chưa đúng định dạng — kiểm tra lại giúp Byte nhé.",
      ok_new:"Ghi danh thành công! 500 {tt} đang chờ bạn.",
      ok_dup:"Email này đã có trong phi hành đoàn rồi!",
      err_net:"Tín hiệu bị nhiễu, thử lại sau vài giây nhé.",

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
      a5:"astroQ.org dự kiến ra mắt chính thức vào đầu tháng 8 năm 2026. Người đăng ký waitlist bằng email sẽ nhận vé mời sớm cùng 500 Purple Meteors khởi đầu ngay khi hệ thống mở cửa.",

      foot_note:"Nền tảng học STEM tương tác cho nhà khám phá trẻ"
    },
    en:{
      title:"astroQ.org — Explore the Galaxy of Knowledge | Launching Aug 2026",
      status:"STATION WARMING UP",
      eyebrow:"PRE-LAUNCH · MISSION 001",
      h1:"Explore the Galaxy of Knowledge with astroQ.org",
      lede:"An interactive learning platform on Space, AI & Quantum Physics for young explorers. We turn complex theory into thrilling cosmic missions.",
      cd_label:"SYSTEM GOES LIVE IN", cd_d:"days", cd_h:"hours", cd_m:"mins", cd_s:"secs",
      cd_live:"SYSTEM IS LIVE",
      hero_cta:"Get early access 🚀", hero_cta2:"What is astroQ.org?",
      crew_comet:"Space-pilot cat — guides you planet by planet and hands out exploration missions.",
      crew_byte:"AI assistant robot — explains hard terms in kid-friendly language and grades your quizzes.",

      wl_tag:"BOARDING PASS · EARLY ACCESS",
      wl_title:"Join the Waitlist & Claim Your Starter Gift!",
      wl_desc:"Sign up today and get <b>500 PURPLE METEORS</b> (the reward currency on astroQ.org) to upgrade your ship &amp; unlock planets the moment we launch!",
      wl_label:"Email address", wl_ph:"astronaut@astroq.org",
      wl_cta:"Claim 500 Purple Meteors & Early Access 🚀",
      wl_sending:"Sending signal…",
      wl_hint:"No spam. You'll only hear from us at the official launch in early August 2026.",
      done_title:"You're on the crew list!",
      done_body:'Your early-access pass is reserved for <b id="wl-done-mail">you</b>. 500 Purple Meteors will be waiting in your cockpit when astroQ.org opens.',
      done_again:"Use another email",

      err_empty:"Enter your email to grab an early-access pass!",
      err_format:"That email looks off — mind double-checking it for Byte?",
      ok_new:"You're in! 500 {tt} are waiting for you.",
      ok_dup:"This email is already on the crew list!",
      err_net:"Signal interference, please try again in a moment.",

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
      a5:"astroQ.org is scheduled to launch in early August 2026. Everyone on the email waitlist gets an early-access pass plus 500 starter Purple Meteors the moment the system opens.",

      foot_note:"Interactive STEM learning for young explorers"
    }
  };

  var LANG = AstroQ.getLang();
  function t(k){ var d = I18N[LANG] || I18N.vi; return d[k] != null ? d[k] : k; }

  var toast = AstroQ.makeToast("toast", 2800);

  /* ============================ Ngôn ngữ ============================ */
  function applyLang(lang){
    if(lang === "en" || lang === "vi") LANG = lang;
    document.documentElement.lang = LANG;
    document.title = t("title");
    document.querySelectorAll("[data-i18n]").forEach(function(el){
      el.textContent = t(el.getAttribute("data-i18n"));
    });
    document.querySelectorAll("[data-i18n-html]").forEach(function(el){
      el.innerHTML = t(el.getAttribute("data-i18n-html"));
    });
    document.querySelectorAll("[data-i18n-ph]").forEach(function(el){
      el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph")));
    });
    AstroQ.markLangButtons(LANG);
    renderCountdown();
    if(joined) paintDone(joined);      // giữ nguyên trạng thái đã đăng ký khi đổi ngôn ngữ
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
      return false;                                  // dừng vòng lặp
    }
    var s = Math.floor(left / 1000);
    $("cd-d").textContent = pad(Math.floor(s / 86400));
    $("cd-h").textContent = pad(Math.floor(s % 86400 / 3600));
    $("cd-m").textContent = pad(Math.floor(s % 3600 / 60));
    $("cd-s").textContent = pad(s % 60);
    return true;
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

  /* Mô phỏng gọi API — đổi sang backend thật chỉ cần thay thân hàm này bằng:
     return fetch("/api/waitlist", {method:"POST", headers:{"Content-Type":"application/json"},
       body: JSON.stringify({email: email})}).then(function(r){ return r.json(); });        */
  function submitWaitlist(email){
    return new Promise(function(resolve){
      setTimeout(function(){
        var list = readList();
        var dup = list.some(function(x){ return x && x.email === email; });
        if(!dup){
          list.push({ email: email, ts: new Date().toISOString(), lang: LANG });
          writeList(list);
        }
        resolve({ ok: true, duplicated: dup, position: list.length });
      }, 900);                                        // giả lập độ trễ mạng
    });
  }

  /* ============================ Form ============================ */
  var form = $("wl-form"), input = $("wl-email"), submitBtn = $("wl-submit"),
      doneBox = $("wl-done"), joined = null;

  function paintDone(email){
    joined = email;
    form.hidden = true;
    doneBox.hidden = false;
    var slot = $("wl-done-mail");                     // do data-i18n-html render lại nên tìm mỗi lần
    if(slot) slot.textContent = email;
  }

  function resetForm(){
    joined = null;
    doneBox.hidden = true;
    form.hidden = false;
    input.value = "";
    input.classList.remove("invalid");
    input.focus();
  }

  function setLoading(on){
    submitBtn.disabled = on;
    submitBtn.textContent = on ? t("wl_sending") : t("wl_cta");
  }

  form.addEventListener("submit", function(e){
    e.preventDefault();
    if($("wl-company").value) return;                 // bot điền bẫy → bỏ qua im lặng

    var email = input.value.trim().toLowerCase();
    if(!email){ input.classList.add("invalid"); input.focus(); return toast(t("err_empty"), "bad"); }
    if(!EMAIL_RE.test(email)){ input.classList.add("invalid"); input.focus(); return toast(t("err_format"), "bad"); }
    input.classList.remove("invalid");

    setLoading(true);
    submitWaitlist(email).then(function(res){
      setLoading(false);
      if(!res || !res.ok) return toast(t("err_net"), "bad");
      paintDone(email);
      toast(res.duplicated ? t("ok_dup") : t("ok_new"), "ok");
      doneBox.scrollIntoView({ behavior:"smooth", block:"center" });
    }).catch(function(){
      setLoading(false);
      toast(t("err_net"), "bad");
    });
  });

  input.addEventListener("input", function(){ input.classList.remove("invalid"); });
  $("wl-again").addEventListener("click", resetForm);

  /* ============================ Khởi tạo ============================ */
  $("year").textContent = String(new Date().getFullYear());
  paintIcons();
  applyLang(LANG);
  AstroQ.initLang(applyLang);

  var ticker = setInterval(function(){
    if(!renderCountdown()) clearInterval(ticker);
  }, 1000);

  /* Nếu máy này đã đăng ký trước đó thì hiện luôn trạng thái thành công */
  var saved = readList();
  if(saved.length) paintDone(saved[saved.length - 1].email);
})();
