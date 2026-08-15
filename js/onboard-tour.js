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

   ⚠️ 6 BƯỚC (15/08/2026, trước đó 7). Bước "Kho Thành Tích" và bước "Hồ sơ Phi
   Hành Gia" đã GỘP làm một: cả sáu đường vào "xem lại mình" nay nằm trong MỘT
   menu thả sau ảnh đại diện, nên hai bước liên tiếp chiếu vào cùng một cái nút
   là nói lại một điều hai lần. Chi tiết ở chính bước `profile` trong `STEPS`.

   ⚠️ Dashboard có 6 card nhưng ba card thêm 29/07/2026 KHÔNG có `data-tour`, và
   đó là quyết định có chủ ý:
     · Phòng Nghiên Cứu chưa có trang → dẫn trẻ tới rồi nói "chưa mở đâu" thì
       thà đừng dẫn;
     · Trung Tâm Nhiệm Vụ và Sổ Tay Thuật Ngữ (thẻ MOD-06 từ 04/08/2026, thay
       chỗ "Thư Viện Thiên Văn" chưa có trang) thì đã có thật, nhưng thêm bước là phải đo
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

  /* ─────────── DÙNG LẠI ENGINE NÀY CHO MÀN CHỈ ĐƯỜNG KHÁC ───────────
     Thêm 30/07/2026. Comet chúc mừng xong chuỗi nhiệm vụ Trái Đất cần ĐÚNG bộ máy
     này: ô sáng tự làm tối cả trang, box thoại có nhánh đặt sang bên, lớp chặn bấm,
     ảnh linh vật to. Viết lại lần thứ hai là bỏ luôn cả 4 bài học đã trả giá ở đây.
     Nên `start()` nhận thêm:
       · `steps`   — bộ bước riêng cho lượt này (mặc định: 7 bước dẫn tham quan)
       · `onSeen`  — hàm ghi cờ "đã xem" của lượt này (mặc định: ghi `tourSeen`)
       · `pulse`   — true thì ô sáng nhấp nháy để hút mắt vào thẻ đích
     ⚠️ `steps` và `onSeen` PHẢI đi cùng nhau. Truyền bộ bước khác mà để nguyên
        `onSeen` mặc định thì lượt chỉ-đường sẽ ghi `tourSeen = true`, và một phi
        hành gia mới bị MẤT LUÔN màn dẫn tham quan mà không ai hiểu vì sao. */
  var activeSteps = null;   // null = dùng STEPS mặc định
  var onSeen = null;        // null = ghi cờ tourSeen như cũ

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
      vi: { title: "Trạm Tri Thức",
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
      /* ⚠️ GỘP HAI BƯỚC LÀM MỘT (15/08/2026, 7 → 6 bước). Trước đó có bước
         "Kho Thành Tích" (`[data-tour="awards"]`) và bước "Hồ sơ Phi Hành Gia"
         riêng, vì hai khu đó là hai ô nằm rời trên trang. Nay cả sáu đường vào
         "xem lại mình" (hồ sơ · thành tích · mẫu vật · kho trang trí · bảng bố
         mẹ · báo cáo hệ thống) nằm trong MỘT menu thả sau ảnh đại diện — xem lý
         do đo được ở đầu js/user-menu.js.
         ⚠️ KHÔNG chiếu vào từng mục bên trong menu: chúng nằm trong tấm thả đang
            `hidden`, mà `.tour-hole` khoét theo `getBoundingClientRect()` — phần
            tử ẩn cho ra khung 0×0 và Comet chiếu sáng vào khoảng không. Thứ cần
            dạy trẻ ở bước này cũng đúng là CÁI CỬA, không phải từng ngăn tủ. */
      key: "profile", target: '[data-tour="profile"]', icon: "👨‍🚀",
      vi: { title: "Mọi thứ của riêng bạn",
            body: "Bấm vào <b>ảnh của bạn</b> ở góc trên là mở ra tất cả: hồ sơ, huy hiệu, " +
                  "kho mẫu vật, kho trang trí — và cả bảng dành cho bố mẹ nữa." },
      en: { title: "Everything that's yours",
            body: "Tap <b>your picture</b> in the top corner to open it all: your profile, badges, " +
                  "specimen vault, decoration deck — and the board for your parents too." }
    },
    {
      /* ⚠️ LỜI THOẠI ĐỔI 01/08/2026 CÙNG LÚC TOUR DỜI XUỐNG SAU NHIỆM VỤ 1
         (docs/decisions/003). Câu cũ là *"Nếu đã sẵn sàng, hãy khởi động động cơ
         thôi!"* + nút *"Khởi động động cơ 🚀"* — nó đúng khi tour chạy TRƯỚC nhiệm vụ
         và dẫn thẳng sang màn loading Luna rời bến. Giờ tour chạy SAU khi trẻ đã bay
         tới Trái Đất và làm xong 8 bước, nên bảo nó "khởi động động cơ" là nói một
         việc đã xảy ra từ lâu. Câu mới hướng về việc TIẾP THEO. */
      key: "ready", target: null,
      vi: { title: "Con tàu là của bạn! 🚀",
            body: "Giờ bạn đã biết đường trong tàu rồi. " +
                  "Hãy <b>chọn khu tiếp theo</b> để khám phá nhé!" },
      en: { title: "The ship is yours! 🚀",
            body: "Now you know your way around. " +
                  "<b>Pick your next area</b> and keep exploring!" }
    }
  ];

  /* Nhãn nút giữ NGẮN: "Bỏ qua phần giới thiệu" xuống 2 dòng trên điện thoại
     390px và bóp méo cả hàng chân box (đã thấy trên ảnh chụp). */
  var UI = {
    vi: { who: "Comet", role: "Bạn đồng hành", skip: "Bỏ qua",
          next: "Tiếp tục", first: "Bắt đầu tham quan", go: "Khám phá thôi! 🚀" },
    en: { who: "Comet", role: "Your companion", skip: "Skip",
          next: "Next", first: "Start the tour", go: "Let's explore! 🚀" }
  };

  /* ------------------------------------------------------------ */
  var lang = "vi", pilotName = "", idx = 0, open = false, onFinish = null;
  var root = null, hole = null, bubble = null, els = null;

  function txt(step) { return step[lang] || step.vi; }
  function ui(k) { return (UI[lang] || UI.vi)[k]; }

  /* ---------------- Cờ "đã xem" ---------------- */
  /** Bộ bước của lượt đang chạy. Mọi chỗ đọc `STEPS` phải đi qua đây. */
  function stepsNow() { return activeSteps || STEPS; }

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
    /* Lượt dùng lại engine có cờ RIÊNG — gọi hàm của nó, đừng ghi `tourSeen`. */
    if (onSeen) { onSeen(); return; }
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
      '<div class="aq-say tour-bubble none">' +
        '<div class="tour-who">' +
          '<span class="aq-ava glow float"><img src="img/m1.png" alt="Comet" /></span>' +
          '<span><span class="aq-nm"></span><span class="aq-tag"></span></span>' +
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
      who:   root.querySelector(".tour-who .aq-nm"),
      role:  root.querySelector(".tour-who .aq-tag"),
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
    var ST = stepsNow();
    var s = ST[idx], d = txt(s);
    els.who.textContent  = ui("who");
    els.role.textContent = ui("role");
    els.title.innerHTML  = (s.icon ? '<span class="ic">' + s.icon + "</span>" : "") +
                           "<span>" + d.title.replace("{name}", esc(pilotName)) + "</span>";
    els.body.innerHTML   = d.body;
    els.next.textContent = idx === 0 ? ui("first")
                         : idx === ST.length - 1 ? ui("go") : ui("next");
    els.next.classList.toggle("go", idx === ST.length - 1);
    els.skip.textContent = ui("skip");
    els.skip.style.display = idx === ST.length - 1 ? "none" : "";

    var dots = "";
    /* Một bước duy nhất thì KHÔNG vẽ chấm: một chấm đơn độc đọc ra thành "còn
       nhiều bước nữa mà bị lỗi", chứ không ra "chỉ có một bước". */
    for (var i = 0; ST.length > 1 && i < ST.length; i++) dots += '<span class="' + (i === idx ? "on" : "") + '"></span>';
    els.dots.innerHTML = dots;

    var el = s.target ? document.querySelector(s.target) : null;
    if (el && typeof el.scrollIntoView === "function") {
      // Cuộn cho khu vực nằm gọn trong màn hình TRƯỚC khi đo, không thì ô sáng
      // trỏ đúng vào chỗ… ngoài khung nhìn.
      /* ⚠️ THẺ CAO THÌ CUỘN LÊN ĐẦU, KHÔNG CUỘN VÀO GIỮA.
         `block:"center"` cho thẻ cao là tự tay tạo ra thế bí: thẻ HUD cao 343px
         nằm giữa màn 844px chỉ để lại ~250px trên và ~250px dưới, mà box thoại
         cao 254px — không nhánh nào (dưới/trên/phải/trái) vừa, engine rơi về
         nhánh "giữa" và ĐÈ 74% lên chính thẻ đang được giới thiệu. Đo được trên
         điện thoại 390×844 với thẻ MOD-04.
         Cuộn lên đầu thì 343 + 254 + lề = 633px < 844px → nhánh "dưới" vừa chỗ.
         Ngưỡng 40% chiều cao khung nhìn: dưới mức đó thì cuộn vào giữa vẫn còn
         chỗ, mà canh giữa dễ nhìn hơn. */
      var tall = el.getBoundingClientRect().height > global.innerHeight * 0.4;
      try {
        el.scrollIntoView({ block: tall ? "start" : "center",
                            behavior: reduced() ? "auto" : "smooth" });
      } catch (e2) { el.scrollIntoView(); }
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
    var s = stepsNow()[idx];
    var el = s.target ? document.querySelector(s.target) : null;
    var vw = global.innerWidth, vh = global.innerHeight;

    if (!el) {
      // Bước mở đầu / kết thúc: tối cả màn hình, box thoại ra giữa.
      hole.classList.add("blank");
      hole.style.top = (vh / 2) + "px";
      hole.style.left = (vw / 2) + "px";
      hole.style.width = "0px";
      hole.style.height = "0px";
      bubble.className = "aq-say tour-bubble none";
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

    bubble.className = "aq-say tour-bubble " + dir;
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
    if (idx >= stepsNow().length - 1) { finish("done"); return; }
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
    /**
     * Mở tour ngay, không hỏi cờ đã xem.
     * opts: {name, lang, onFinish(reason), steps, onSeen, pulse}
     * `steps`/`onSeen`/`pulse` chỉ dùng khi DÙNG LẠI engine cho màn chỉ đường khác
     * — xem ghi chú ở khai báo `activeSteps` đầu file.
     */
    start: function (opts) {
      opts = opts || {};
      lang = opts.lang === "en" ? "en" : "vi";
      pilotName = opts.name || "";
      onFinish = typeof opts.onFinish === "function" ? opts.onFinish : null;
      activeSteps = (opts.steps && opts.steps.length) ? opts.steps : null;
      onSeen = typeof opts.onSeen === "function" ? opts.onSeen : null;
      build();
      // Vòng nhấp nháy quanh ô sáng — chỉ bật khi được yêu cầu, vì ở màn dẫn tham
      // quan 7 bước thì nhấp nháy liên tục 7 lần là quá nhiều kích thích.
      root.classList.toggle("pulse", opts.pulse === true);
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

    isOpen: function () { return open; },

    /**
     * MÀN CHỈ ĐƯỜNG MỘT BƯỚC — dùng lại toàn bộ bộ máy của tour.
     * `AstroQTour.guide({ lang, target, icon, vi:{title,body}, en:{…}, onSeen, onFinish })`
     *
     * ⚠️ `onSeen` là BẮT BUỘC (không có thì hàm không chạy). Thiếu nó thì `markSeen()`
     *    rơi về nhánh mặc định và ghi `tourSeen = true` — một phi hành gia mới sẽ
     *    MẤT LUÔN màn dẫn tham quan vì một lời chúc mừng.
     */
    guide: function (opts) {
      opts = opts || {};
      if (typeof opts.onSeen !== "function") return false;
      return AstroQTour.start({
        lang: opts.lang,
        name: opts.name,
        pulse: opts.pulse !== false,   // màn chỉ đường thì mặc định CÓ nhấp nháy
        onSeen: opts.onSeen,
        onFinish: opts.onFinish,
        steps: [{
          key: opts.key || "guide",
          target: opts.target || null,
          icon: opts.icon || "",
          vi: opts.vi, en: opts.en
        }]
      });
    }
  };

  global.AstroQTour = AstroQTour;
})(window);
