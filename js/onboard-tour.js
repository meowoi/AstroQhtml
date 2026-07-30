/* ============================================================
   onboard-tour.js — Comet dẫn phi hành gia mới tham quan khoang tàu Luna.

   Chạy MỘT LẦN cho mỗi tài khoản, ngay sau khi chọn nhân vật xong
   (select.html đóng dấu APPROVED → dashboard.html).

   NGUỒN SỰ THẬT LÀ SERVER, không phải localStorage: cờ `tourSeen` nằm trên
   bản ghi PROFILE trong DynamoDB, đọc/ghi qua GET|PUT /me/onboarding.
   localStorage chỉ là cache để không phải chờ mạng ở những lần vào sau.
   Chưa đăng nhập / mất mạng / chưa cấu hình Firebase → tự lùi về cache,
   trang không bao giờ vỡ vì việc này.

   Nạp SAU js/ui-common.js. Không phụ thuộc dashboard: mọi khu vực được chỉ
   tới bằng thuộc tính `data-tour="<key>"` trong HTML, nên đổi bố cục trang
   thì không phải sửa file này.

   ⚠️ VẪN 7 BƯỚC dù dashboard đã lên 6 card (29/07/2026). Ba card thêm vào
   KHÔNG có `data-tour`, và đó là quyết định có chủ ý:
     · Phòng Nghiên Cứu và Thư Viện Thiên Văn chưa có trang → dẫn trẻ tới rồi
       nói "chưa mở đâu" thì thà đừng dẫn;
     · Trung Tâm Nhiệm Vụ thì đã có thật, nhưng thêm một bước nữa là phải đo
       lại chỗ đặt box thoại: thẻ HUD cao ~375px cộng box ~245px đã vượt màn
       hình 900px, nhánh "đặt sang BÊN" mới cứu được — thêm bước mà không đo
       lại là box rơi vào giữa và đè lên chính khu vực đang giới thiệu.
   Muốn thêm: gắn `data-tour="mission"` vào card rồi thêm một phần tử vào
   `STEPS`, sau đó CHỤP ẢNH màn 390px và 1440px để kiểm chỗ đặt box thoại.

     <link rel="stylesheet" href="css/onboard-tour.css" />
     <script src="js/onboard-tour.js"></script>

   Dùng:
     AstroQTour.autoStart({ name:"Bi", lang:"vi", onFinish:function(reason){} });
     AstroQTour.setLang("en");   // đổi ngôn ngữ giữa lúc đang mở
   ============================================================ */
(function (global) {
  "use strict";

  /* Cache của cờ tourSeen. Nguồn thật là DynamoDB (/me/onboarding). */
  var LS_SEEN = "astroq-tour-seen";

  /* Chờ tối đa bao lâu để server trả lời trước khi quyết định có chạy tour.
     Có hạn vì mạng yếu thì thà chạy tour lần nữa còn hơn để trẻ ngồi nhìn
     màn hình đứng im — nhưng cũng không quá ngắn, kẻo người đã xem ở máy
     khác lại phải xem lại. */
  var SERVER_WAIT_MS = 1800;

  /* ------------------------------------------------------------
     NỘI DUNG — thứ tự đúng như lời Comet dẫn tham quan.
     `target` là CSS selector; null = box thoại đứng giữa màn hình.
     ------------------------------------------------------------ */
  var STEPS = [
    {
      key: "hello", target: null,
      /* Câu chào PHẢI gọi đúng tên khu đang đứng. Mọi trang khác đều có nút "Về
         Trung Tâm Điều Hướng" trỏ về đây, nên nếu Comet gọi nó bằng một tên khác
         thì trẻ không nối được hai thứ đó lại với nhau. */
      vi: { title: "Chào mừng, {name}! 🚀",
            body: "Bạn đã chính thức gia nhập <b>Đội Biệt Kích Vũ Trụ</b>!<br/>" +
                  "Mình là <b>Comet</b>, người bạn sẽ đồng hành cùng bạn trên mọi chuyến phiêu lưu.<br/>" +
                  "Bạn đang ở <b>Trung Tâm Điều Hướng</b> của tàu <b>Luna</b> — để mình dẫn đi một vòng nhé!" },
      en: { title: "Welcome, {name}! 🚀",
            body: "You have officially joined the <b>Space Commando Squad</b>!<br/>" +
                  "I'm <b>Comet</b>, the friend who'll travel with you on every adventure.<br/>" +
                  "You're in the <b>Navigation Hub</b> of the ship <b>Luna</b> — let me show you around!" }
    },
    {
      key: "map", target: '[data-tour="map"]', icon: "🗺️",
      vi: { title: "Bản đồ Thiên Hà",
            body: "Đây là nơi chúng ta chọn hành tinh để khám phá. Càng hoàn thành nhiều nhiệm vụ, " +
                  "bạn sẽ mở khoá càng nhiều thế giới mới!" },
      en: { title: "Galaxy Map",
            body: "This is where we pick a planet to explore. The more missions you finish, " +
                  "the more new worlds you unlock!" }
    },
    {
      key: "learn", target: '[data-tour="learn"]', icon: "📚",
      vi: { title: "Tri Thức",
            body: "Học những điều thú vị về vũ trụ, robot và AI qua các bài học ngắn cùng hình ảnh sinh động." },
      en: { title: "Knowledge Station",
            body: "Learn fascinating things about space, robots and AI through short lessons with lively pictures." }
    },
    {
      key: "train", target: '[data-tour="train"]', icon: "🎮",
      vi: { title: "Khu Huấn Luyện",
            body: "Chơi mini game để rèn kỹ năng, kiếm điểm và nhận thật nhiều huy hiệu." },
      en: { title: "Training Simulator",
            body: "Play mini games to sharpen your skills, earn points and collect plenty of badges." }
    },
    {
      key: "awards", target: '[data-tour="awards"]', icon: "🏆",
      vi: { title: "Kho Thành Tích",
            body: "Đây là nơi lưu giữ huy hiệu, bộ sưu tập và những thành tích bạn đã chinh phục." },
      en: { title: "Trophy Hold",
            body: "This is where your badges, collections and every achievement you've conquered are kept." }
    },
    {
      key: "profile", target: '[data-tour="profile"]', icon: "👨‍🚀",
      vi: { title: "Hồ sơ Phi Hành Gia",
            body: "Theo dõi cấp độ, trang phục và hành trình khám phá của riêng bạn." },
      en: { title: "Astronaut Profile",
            body: "Track your level, your outfit and your very own journey of discovery." }
    },
    {
      key: "ready", target: null,
      vi: { title: "Sẵn sàng chưa? 🚀",
            body: "Nếu đã sẵn sàng, hãy <b>khởi động động cơ</b> thôi!" },
      en: { title: "All set? 🚀",
            body: "If you're ready, let's <b>fire up the engines</b>!" }
    }
  ];

  /* Nhãn nút giữ NGẮN: "Bỏ qua phần giới thiệu" xuống 2 dòng trên điện thoại
     390px và bóp méo cả hàng chân box (đã thấy trên ảnh chụp). */
  var UI = {
    vi: { who: "Comet", role: "Bạn đồng hành", skip: "Bỏ qua",
          next: "Tiếp tục", first: "Bắt đầu tham quan", go: "Khởi động động cơ 🚀" },
    en: { who: "Comet", role: "Your companion", skip: "Skip",
          next: "Next", first: "Start the tour", go: "Fire up the engines 🚀" }
  };

  /* ------------------------------------------------------------ */
  var lang = "vi", pilotName = "", idx = 0, open = false, onFinish = null;
  var root = null, hole = null, bubble = null, els = null;

  function txt(step) { return step[lang] || step.vi; }
  function ui(k) { return (UI[lang] || UI.vi)[k]; }

  /* ---------------- Cờ "đã xem" ---------------- */
  function localSeen() {
    try { return localStorage.getItem(LS_SEEN) === "1"; } catch (e) { return false; }
  }
  function setLocalSeen(v) {
    try {
      if (v) localStorage.setItem(LS_SEEN, "1");
      else localStorage.removeItem(LS_SEEN);
    } catch (e) {}
  }

  /* Chờ module ES `js/firebase-auth.js` xuất hiện. Nó là <script type="module">
     nên luôn chạy SAU file này — không chờ thì lần nào cũng tưởng là chưa đăng nhập. */
  function waitAuth(ms) {
    if (global.AstroQAuth) return Promise.resolve(global.AstroQAuth);
    return new Promise(function (resolve) {
      var t0 = Date.now();
      var timer = setInterval(function () {
        if (global.AstroQAuth || Date.now() - t0 > ms) {
          clearInterval(timer);
          resolve(global.AstroQAuth || null);
        }
      }, 60);
    });
  }

  /** Ghi cờ đã xem: cache trước cho nhanh, rồi mới đẩy lên server. */
  function markSeen() {
    setLocalSeen(true);
    waitAuth(SERVER_WAIT_MS).then(function (auth) {
      if (auth && auth.setOnboarding) auth.setOnboarding(true);
    });
  }

  /* ---------------- Dựng DOM (chỉ một lần) ---------------- */
  function build() {
    if (root) return;
    root = document.createElement("div");
    root.className = "tour";
    root.id = "tour";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-modal", "true");
    root.setAttribute("aria-hidden", "true");
    root.innerHTML =
      '<div class="tour-block"></div>' +
      '<div class="tour-hole"><span class="ring"></span></div>' +
      '<div class="tour-bubble none">' +
        '<div class="tour-who">' +
          '<span class="tour-ava"><img src="img/m1.png" alt="Comet" /></span>' +
          '<span><span class="nm"></span><span class="tag"></span></span>' +
        '</div>' +
        '<h2 class="tour-title"></h2>' +
        '<p class="tour-body"></p>' +
        '<div class="tour-foot">' +
          '<span class="tour-dots"></span>' +
          '<button type="button" class="tour-skip"></button>' +
          '<button type="button" class="tour-next"></button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(root);

    hole   = root.querySelector(".tour-hole");
    bubble = root.querySelector(".tour-bubble");
    els = {
      who:   root.querySelector(".tour-who .nm"),
      role:  root.querySelector(".tour-who .tag"),
      title: root.querySelector(".tour-title"),
      body:  root.querySelector(".tour-body"),
      dots:  root.querySelector(".tour-dots"),
      skip:  root.querySelector(".tour-skip"),
      next:  root.querySelector(".tour-next")
    };

    els.next.addEventListener("click", next);
    els.skip.addEventListener("click", function () { finish("skip"); });
    global.addEventListener("resize", place);
    // scroll ở capture để bắt cả khi trang con cuộn
    global.addEventListener("scroll", place, true);
    document.addEventListener("keydown", onKey);
  }

  function onKey(e) {
    if (!open) return;
    if (e.key === "Escape") { e.preventDefault(); finish("skip"); }
    else if (e.key === "Enter" || e.key === " " || e.key === "ArrowRight") {
      // Enter/Space đang focus vào nút thì để nút tự xử lý, kẻo nhảy 2 bước một lúc.
      if (document.activeElement && document.activeElement.tagName === "BUTTON") return;
      e.preventDefault(); next();
    }
  }

  /* ---------------- Vẽ một bước ---------------- */
  function paint() {
    var s = STEPS[idx], d = txt(s);
    els.who.textContent  = ui("who");
    els.role.textContent = ui("role");
    els.title.innerHTML  = (s.icon ? '<span class="ic">' + s.icon + "</span>" : "") +
                           "<span>" + d.title.replace("{name}", esc(pilotName)) + "</span>";
    els.body.innerHTML   = d.body;
    els.next.textContent = idx === 0 ? ui("first")
                         : idx === STEPS.length - 1 ? ui("go") : ui("next");
    els.next.classList.toggle("go", idx === STEPS.length - 1);
    els.skip.textContent = ui("skip");
    els.skip.style.display = idx === STEPS.length - 1 ? "none" : "";

    var dots = "";
    for (var i = 0; i < STEPS.length; i++) dots += '<span class="' + (i === idx ? "on" : "") + '"></span>';
    els.dots.innerHTML = dots;

    var el = s.target ? document.querySelector(s.target) : null;
    if (el && typeof el.scrollIntoView === "function") {
      // Cuộn cho khu vực nằm gọn trong màn hình TRƯỚC khi đo, không thì ô sáng
      // trỏ đúng vào chỗ… ngoài khung nhìn.
      try { el.scrollIntoView({ block: "center", behavior: reduced() ? "auto" : "smooth" }); }
      catch (e2) { el.scrollIntoView(); }
    }
    // Đo sau khi cuộn xong. Cuộn mượt mất ~300ms nên đo 2 lần: ngay và sau đó.
    place();
    setTimeout(place, reduced() ? 30 : 340);
  }

  function reduced() {
    try { return global.matchMedia("(prefers-reduced-motion: reduce)").matches; }
    catch (e) { return false; }
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* Đặt ô sáng + box thoại theo vị trí THẬT của khu vực đang nói tới. */
  function place() {
    if (!open) return;
    var s = STEPS[idx];
    var el = s.target ? document.querySelector(s.target) : null;
    var vw = global.innerWidth, vh = global.innerHeight;

    if (!el) {
      // Bước mở đầu / kết thúc: tối cả màn hình, box thoại ra giữa.
      hole.classList.add("blank");
      hole.style.top = (vh / 2) + "px";
      hole.style.left = (vw / 2) + "px";
      hole.style.width = "0px";
      hole.style.height = "0px";
      bubble.className = "tour-bubble none";
      var bw0 = bubble.offsetWidth, bh0 = bubble.offsetHeight;
      bubble.style.left = Math.round((vw - bw0) / 2) + "px";
      bubble.style.top = Math.round(Math.max(12, (vh - bh0) / 2)) + "px";
      return;
    }

    hole.classList.remove("blank");
    var r = el.getBoundingClientRect();
    var pad = 8;
    var hx = r.left - pad, hy = r.top - pad, hw = r.width + pad * 2, hh = r.height + pad * 2;
    hole.style.top = hy + "px";
    hole.style.left = hx + "px";
    hole.style.width = hw + "px";
    hole.style.height = hh + "px";
    // Bo góc theo chính phần tử được chiếu, +pad để đường bo song song với nó
    var br = parseFloat(getComputedStyle(el).borderRadius) || 14;
    hole.style.borderRadius = Math.min(br + pad, 999) + "px";

    var bw = bubble.offsetWidth, bh = bubble.offsetHeight;
    var gap = 18, m = 10;                                // m = lề tối thiểu với mép màn hình

    /* Chọn chỗ đặt box theo thứ tự: dưới → trên → bên phải → bên trái.
       Phải có nhánh ĐẶT SANG BÊN: thẻ HUD cao ~375px, cộng box thoại ~245px là
       vượt màn hình 900px, nên nếu chỉ có trên/dưới thì box rơi vào giữa và ĐÈ
       LÊN chính khu vực đang được chỉ — che mất thứ Comet đang giới thiệu. */
    var dir, top, left;
    if (hy + hh + gap + bh <= vh - m) {                  // dưới còn chỗ
      dir = "up";  top = hy + hh + gap;
    } else if (hy - gap - bh >= m) {                     // trên còn chỗ
      dir = "down"; top = hy - gap - bh;
    } else if (hx + hw + gap + bw <= vw - m) {           // bên phải còn chỗ
      dir = "left"; left = hx + hw + gap;
    } else if (hx - gap - bw >= m) {                     // bên trái còn chỗ
      dir = "right"; left = hx - gap - bw;
    } else {
      dir = "none";
    }

    if (dir === "up" || dir === "down") {
      left = hx + hw / 2 - bw / 2;                       // canh giữa theo khu vực
    } else if (dir === "left" || dir === "right") {
      top = hy + hh / 2 - bh / 2;
    } else {
      left = (vw - bw) / 2; top = (vh - bh) / 2;
    }
    left = Math.max(m, Math.min(left, vw - bw - m));
    top  = Math.max(m, Math.min(top,  vh - bh - m));

    bubble.className = "tour-bubble " + dir;
    bubble.style.left = Math.round(left) + "px";
    bubble.style.top = Math.round(top) + "px";
    // Mũi nhọn bám tâm khu vực, kể cả khi box đã bị kẹp lệch đi
    var ax = Math.max(16, Math.min(hx + hw / 2 - left - 7, bw - 30));
    var ay = Math.max(16, Math.min(hy + hh / 2 - top - 7, bh - 30));
    bubble.style.setProperty("--ax", Math.round(ax) + "px");
    bubble.style.setProperty("--ay", Math.round(ay) + "px");
  }

  function next() {
    if (!open) return;
    if (idx >= STEPS.length - 1) { finish("done"); return; }
    idx++;
    paint();
  }

  function finish(reason) {
    if (!open) return;
    open = false;
    root.classList.remove("show");
    root.setAttribute("aria-hidden", "true");
    markSeen();
    var cb = onFinish; onFinish = null;
    if (cb) cb(reason);
  }

  /* ---------------- API công khai ---------------- */
  var AstroQTour = {
    /** Mở tour ngay, không hỏi cờ đã xem. opts: {name, lang, onFinish(reason)} */
    start: function (opts) {
      opts = opts || {};
      lang = opts.lang === "en" ? "en" : "vi";
      pilotName = opts.name || "";
      onFinish = typeof opts.onFinish === "function" ? opts.onFinish : null;
      build();
      idx = 0; open = true;
      root.classList.add("show");
      root.setAttribute("aria-hidden", "false");
      paint();
      // Cho trẻ dùng bàn phím / trình đọc màn hình bắt được ngay nút chính
      setTimeout(function () { if (open) els.next.focus(); }, 120);
      return true;
    },

    /** Đã xem chưa (theo cache trong máy — chưa hỏi server). */
    isSeen: localSeen,

    /** Xoá cờ ở CẢ hai nơi để xem lại màn giới thiệu (dùng khi thử nghiệm). */
    reset: function () {
      setLocalSeen(false);
      return waitAuth(SERVER_WAIT_MS).then(function (auth) {
        return auth && auth.setOnboarding ? auth.setOnboarding(false) : { ok: false };
      });
    },

    /**
     * Hỏi cờ rồi mới quyết định có chạy. Cache nói "đã xem" → bỏ qua ngay, không
     * chờ mạng. Cache nói "chưa" → hỏi server (có hạn chờ) để người đã xem ở máy
     * khác không phải xem lại.
     * → Promise<boolean> (có chạy tour hay không)
     */
    autoStart: function (opts) {
      opts = opts || {};
      if (localSeen()) return Promise.resolve(false);

      return waitAuth(SERVER_WAIT_MS).then(function (auth) {
        if (!auth || !auth.getOnboarding) return null;
        return auth.getOnboarding();
      }).catch(function () {
        return null;   // hỏi server hỏng thì coi như không biết, xử như dưới
      }).then(function (r) {
        if (r && r.ok && r.tourSeen) { setLocalSeen(true); return false; }
        // r không ok (chưa đăng nhập / mất mạng / chưa cấu hình) → vẫn chạy tour.
        // Chào một phi hành gia mới hai lần thì phiền, còn không chào lần nào
        // thì họ không biết trên tàu có những gì.
        AstroQTour.start(opts);
        return true;
      });
    },

    /** Đổi ngôn ngữ giữa lúc đang mở. */
    setLang: function (l) {
      lang = l === "en" ? "en" : "vi";
      if (open) paint();
    },

    /** Đổi tên hiển thị (hồ sơ về muộn hơn lúc mở tour). */
    setName: function (n) {
      pilotName = n || "";
      if (open) paint();
    },

    isOpen: function () { return open; }
  };

  global.AstroQTour = AstroQTour;
})(window);
