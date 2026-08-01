/* ⚠️⚠️ ĐÃ NGHỈ HƯU 01/08/2026 — KHÔNG TRANG NÀO NẠP FILE NÀY NỮA.
   Lý do (docs/decisions/003 bước ⑦): màn này làm ĐÚNG CÙNG MỘT NHỊP với
   `js/map-onboard.js` — Comet giới thiệu rồi hỏi "sẵn sàng chưa?". Giữ cả hai là
   trẻ nghe Comet giao nhiệm vụ HAI LẦN liền nhau.
   CHƯA XOÁ vì file còn thay đổi chưa commit (đợt gom `css/mascot.css`) — xoá là
   mất vĩnh viễn. Xoá được sau khi đã commit; đó là việc riêng, chủ dự án quyết.
   Cờ `intro01Seen` ở server GIỮ NGUYÊN, cố ý: không cần migration. */

/* ============================================================
   mission-intro.js — MÀN MỞ ĐẦU NHIỆM VỤ 01 "HÀNH TINH XANH".

   Chạy ngay sau màn loading Luna (js/warp-screen.js), tức sau khi Comet dẫn
   tham quan xong và tàu đã tới Trái Đất. Chỉ chạy MỘT LẦN cho mỗi tài khoản.

   Nhịp phim (~30 giây nếu trẻ đọc bình thường; bấm "Bỏ qua" được bất cứ lúc nào):

     0,0–1,4s   khoang lái mờ dần → không gian sâu; Trái Đất ở góc trên-phải,
                Luna bay vào từ ngoài khung bên trái
     1,4–6,4s   Luna vòng vào QUỸ ĐẠO Trái Đất, mũi tàu tiếp tuyến với đường bay
     2,2s→      box thoại Comet gõ từng chữ; xong thì hiện nút "Tiếp tục"
     bấm tiếp   pop-up HUD "MISSION 01: HÀNH TINH XANH" + nút kích hoạt sứ mệnh

   Âm thanh: động cơ rầm rì + bip radar, tôn trọng lựa chọn tắt tiếng dùng chung
   `localStorage["astroq-sfx"]` của các mini-game.

   ⚠️ PHẦN VẼ (sao, Trái Đất, tàu) dùng **js/space-scene.js** — nạp TRƯỚC file này.
   Không vẽ lại Trái Đất ở đây: người chơi vừa nhìn nó ở màn loading xong, hai cảnh
   khác nhau một chút là thấy ngay.

     <link rel="stylesheet" href="css/mission-intro.css" />
     <script src="js/space-scene.js"></script>
     <script src="js/mission-intro.js"></script>

     AstroQMissionIntro.autoStart({ lang:"vi", onActivate:function(){ … } });
   ============================================================ */
(function (global) {
  "use strict";

  /* Cờ "đã xem màn mở đầu Nhiệm Vụ 01". Cache trong máy; nguồn sự thật là
     `intro01Seen` trên bản ghi PROFILE, đọc/ghi qua GET|PUT /me/onboarding. */
  var LS_SEEN = "astroq-mission01-intro-seen";
  var LS_SFX  = "astroq-sfx";              // dùng chung với các mini-game
  var SERVER_WAIT_MS = 1800;

  var CONFIG = {
    tOrbitIn:  1.4,     // giây: bắt đầu vòng vào quỹ đạo
    tOrbitEnd: 6.4,     // giây: đã vào quỹ đạo, bắt đầu bay vòng chậm
    tSay:      2.2,     // giây: box thoại hiện ra
    typeMs:    26,      // ms mỗi ký tự khi gõ chữ
    orbitR:    1.34,    // bán kính quỹ đạo, theo bán kính Trái Đất
    orbitSpin: 0.16     // rad/giây khi đã vào quỹ đạo
  };

  var TXT = {
    vi: {
      who: "Comet", role: "Phi công trưởng",
      line: "Đây là Trái Đất — ngôi nhà của chúng ta! Nhưng trước khi được phép bay " +
            "đến những hành tinh khác, mọi thành viên của Đội Biệt Kích Vũ Trụ đều " +
            "phải hoàn thành nhiệm vụ đầu tiên!",
      lineHtml: "Đây là <b>Trái Đất</b> — ngôi nhà của chúng ta! Nhưng trước khi được " +
                "phép bay đến những hành tinh khác, mọi thành viên của <b>Đội Biệt Kích " +
                "Vũ Trụ</b> đều phải hoàn thành <b>nhiệm vụ đầu tiên</b>!",
      next: "Tiếp tục",
      code: "Nhiệm vụ được giao",
      title: "MISSION 01: HÀNH TINH XANH",
      sub: "Hoàn thành sứ mệnh đầu tiên ngay tại Trái Đất để mở khoá đường bay tới các hành tinh khác.",
      go: "[ Nhấn để kích hoạt sứ mệnh ]",
      skip: "Bỏ qua ›"
    },
    en: {
      who: "Comet", role: "Chief Pilot",
      line: "This is Earth — our home! But before you are cleared to fly to other " +
            "planets, every member of the Space Commando Squad must complete their " +
            "very first mission!",
      lineHtml: "This is <b>Earth</b> — our home! But before you are cleared to fly to " +
                "other planets, every member of the <b>Space Commando Squad</b> must " +
                "complete their <b>very first mission</b>!",
      next: "Continue",
      code: "Mission assigned",
      title: "MISSION 01: THE BLUE PLANET",
      sub: "Complete your first mission right here on Earth to unlock flight routes to the other planets.",
      go: "[ Press to activate mission ]",
      skip: "Skip ›"
    }
  };

  /* ---------------- Âm thanh ----------------
     Động cơ = tiếng rầm rì tần số thấp; radar = bip ngắn cao. Cả hai dựng bằng
     WebAudio nên không phải tải file. Bọc try/catch toàn bộ: trình duyệt chặn
     autoplay hay không có WebAudio thì màn phim vẫn chạy, chỉ là im tiếng. */
  var AC = null, engineNodes = null, beepTimer = 0;

  function sfxOn() {
    try { return localStorage.getItem(LS_SFX) !== "off"; } catch (e) { return true; }
  }
  function ac() {
    if (AC) return AC;
    try {
      var C = global.AudioContext || global.webkitAudioContext;
      if (!C) return null;
      AC = new C();
    } catch (e) { AC = null; }
    return AC;
  }

  function engineStart() {
    if (!sfxOn() || engineNodes) return;
    var c = ac(); if (!c) return;
    try {
      if (c.state === "suspended") c.resume();
      // Hai dao động rất thấp lệch nhau vài Hz → nghe "rầm rì" chứ không phải một nốt
      var g = c.createGain(); g.gain.value = 0;
      var o1 = c.createOscillator(); o1.type = "sawtooth"; o1.frequency.value = 52;
      var o2 = c.createOscillator(); o2.type = "sine";     o2.frequency.value = 47;
      var lp = c.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 240;
      o1.connect(lp); o2.connect(lp); lp.connect(g); g.connect(c.destination);
      o1.start(); o2.start();
      g.gain.linearRampToValueAtTime(0.055, c.currentTime + 1.2);   // vào từ từ, không giật
      engineNodes = { g: g, o1: o1, o2: o2 };
    } catch (e) { engineNodes = null; }
  }
  function engineStop() {
    if (!engineNodes) return;
    var c = AC, n = engineNodes; engineNodes = null;
    try {
      n.g.gain.linearRampToValueAtTime(0, c.currentTime + 0.4);
      setTimeout(function () {
        try { n.o1.stop(); n.o2.stop(); } catch (e) {}
      }, 520);
    } catch (e) {}
  }
  function beep() {
    if (!sfxOn()) return;
    var c = ac(); if (!c) return;
    try {
      var g = c.createGain(), o = c.createOscillator();
      o.type = "sine"; o.frequency.value = 1180;
      g.gain.value = 0;
      o.connect(g); g.connect(c.destination);
      var t = c.currentTime;
      g.gain.linearRampToValueAtTime(0.05, t + 0.012);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.16);
      o.start(t); o.stop(t + 0.18);
    } catch (e) {}
  }
  function beepsStart() {
    if (beepTimer) return;
    beepTimer = setInterval(beep, 1500);
  }
  function beepsStop() {
    if (beepTimer) { clearInterval(beepTimer); beepTimer = 0; }
  }

  /* ---------------- Trạng thái ---------------- */
  var root = null, cv = null, scene = null, els = null;
  var raf = 0, t0 = 0, lastT = 0, running = false, done = false;
  var lang = "vi", reduced = false, onActivate = null;
  var typeTimer = 0, typed = 0, sayShown = false, popShown = false;

  function txt(k) { return (TXT[lang] || TXT.vi)[k]; }

  /* ---------------- Cờ đã xem ---------------- */
  function localSeen() {
    try { return localStorage.getItem(LS_SEEN) === "1"; } catch (e) { return false; }
  }
  function setLocalSeen(v) {
    try {
      if (v) localStorage.setItem(LS_SEEN, "1");
      else localStorage.removeItem(LS_SEEN);
    } catch (e) {}
  }
  /* js/firebase-auth.js là ES module nên chạy SAU file này — chờ có hạn rồi mới
     kết luận là chưa đăng nhập (đúng bẫy đã gặp ở js/onboard-tour.js). */
  function waitAuth(ms) {
    if (global.AstroQAuth) return Promise.resolve(global.AstroQAuth);
    return new Promise(function (resolve) {
      var t = Date.now();
      var timer = setInterval(function () {
        if (global.AstroQAuth || Date.now() - t > ms) {
          clearInterval(timer); resolve(global.AstroQAuth || null);
        }
      }, 60);
    });
  }
  /**
   * Ghi "đã xem màn mở đầu": cache trong máy ngay, rồi PUT lên server.
   * @returns Promise — resolve khi PUT xong HOẶC hết hạn chờ.
   *
   * ⚠️ Phải trả về Promise vì nút kích hoạt **điều hướng sang trang nhiệm vụ**.
   * Bản đầu chỉ bắn PUT rồi 500ms sau `location.href` — điều hướng huỷ luôn
   * request đang bay, nên cờ `intro01Seen` không lên tới DynamoDB và lần sau
   * đăng nhập ở máy khác là xem lại cả màn phim. Cache trong máy che mất lỗi
   * này nên chỉ thấy khi đổi máy.
   */
  function markSeen() {
    setLocalSeen(true);
    var put = waitAuth(SERVER_WAIT_MS).then(function (a) {
      if (a && a.setOnboarding) return a.setOnboarding({ intro01Seen: true });
      return null;
    }).catch(function () { return null; });
    // Chờ có hạn: mạng chậm thì vẫn phải cho trẻ đi tiếp, không đứng chờ mãi
    return Promise.race([
      put,
      new Promise(function (res) { setTimeout(res, 1400); })
    ]);
  }

  /* ---------------- Dựng DOM ---------------- */
  function build() {
    if (root) return;
    root = document.createElement("div");
    root.className = "mi";
    root.id = "mission-intro";
    root.setAttribute("aria-hidden", "true");
    root.innerHTML =
      '<canvas></canvas>' +
      '<button type="button" class="mi-skip"></button>' +
      '<div class="aq-say mi-say" role="status" aria-live="polite">' +
        '<span class="aq-ava glow float"><img src="img/m1.png" alt="Comet" /></span>' +
        '<span class="mi-body">' +
          '<span class="mi-who"><span class="aq-nm"></span><span class="aq-tag"></span></span>' +
          '<p class="mi-line"></p>' +
        '</span>' +
        '<button type="button" class="mi-next hide"></button>' +
      '</div>' +
      '<div class="mi-pop" role="dialog" aria-modal="true" aria-hidden="true">' +
        '<span class="code"></span>' +
        '<h2><span class="cm" aria-hidden="true">☄️</span><span class="ttl"></span>' +
            '<span class="cm" aria-hidden="true">☄️</span></h2>' +
        '<p class="sub"></p>' +
        '<button type="button" class="mi-go"></button>' +
      '</div>';
    document.body.appendChild(root);

    cv = root.querySelector("canvas");
    scene = AstroQSpace.create(cv, { stars: 120, stillStars: 130, warpSpeed: 2 });
    els = {
      skip: root.querySelector(".mi-skip"),
      say:  root.querySelector(".mi-say"),
      who:  root.querySelector(".mi-who .aq-nm"),
      role: root.querySelector(".mi-who .aq-tag"),
      line: root.querySelector(".mi-line"),
      next: root.querySelector(".mi-next"),
      pop:  root.querySelector(".mi-pop"),
      code: root.querySelector(".mi-pop .code"),
      ttl:  root.querySelector(".mi-pop .ttl"),
      sub:  root.querySelector(".mi-pop .sub"),
      go:   root.querySelector(".mi-go")
    };

    els.skip.addEventListener("click", function () { showPop(); });
    els.next.addEventListener("click", function () { showPop(); });
    els.go.addEventListener("click", activate);
    global.addEventListener("resize", function () { if (scene) scene.resize(); });
    document.addEventListener("keydown", onKey);
  }

  function onKey(e) {
    if (!running) return;
    if (e.key === "Escape") { e.preventDefault(); showPop(); return; }
    if (e.key === "Enter" || e.key === " ") {
      if (document.activeElement && document.activeElement.tagName === "BUTTON") return;
      e.preventDefault();
      if (popShown) activate(); else showPop();
    }
  }

  /* ---------------- Bố cục cảnh ----------------
     Trái Đất ở góc trên-phải để box thoại dưới đáy không che nó. */
  function earthAt() {
    var W = scene.W, H = scene.H, portrait = H > W;
    return {
      x: W * (portrait ? 0.60 : 0.70),
      y: H * (portrait ? 0.34 : 0.42),
      R: Math.min(W, H) * (portrait ? 0.28 : 0.25)
    };
  }

  /** Vị trí + hướng của Luna theo thời gian. */
  function shipAt(t) {
    var e = earthAt();
    var W = scene.W, H = scene.H;
    var h = Math.max(24, Math.min(W, H) * 0.068);
    var w = h * scene.shipRatio;
    var orbR = e.R * CONFIG.orbitR + h * 0.5;

    /* Điểm vào quỹ đạo: phía dưới-trái Trái Đất (góc ~145°). Chọn góc này vì
       tàu bay vào từ mép trái, vòng lên là đường ngắn và tự nhiên nhất. */
    var a0 = Math.PI * 0.82;

    function onOrbit(ang) {
      // Bay theo chiều kim đồng hồ → mũi tàu tiếp tuyến, tức lệch 90° so với bán kính
      return {
        x: e.x + Math.cos(ang) * orbR,
        y: e.y + Math.sin(ang) * orbR,
        w: w, h: h,
        rot: ang - Math.PI / 2,
        thrust: 0.2
      };
    }

    if (reduced) return onOrbit(a0);

    if (t < CONFIG.tOrbitIn) {                       // bay vào từ ngoài khung bên trái
      var k = AstroQSpace.easeOut(AstroQSpace.clamp01(t / CONFIG.tOrbitIn));
      var sx = -w, sy = H * 0.74;
      var tx = e.x + Math.cos(a0) * orbR * 1.9, ty = e.y + Math.sin(a0) * orbR * 1.9;
      return { x: sx + (tx - sx) * k, y: sy + (ty - sy) * k, w: w, h: h,
               rot: -0.10 * k, thrust: 1 };
    }
    if (t < CONFIG.tOrbitEnd) {                      // vòng vào quỹ đạo
      var q = AstroQSpace.easeInOut(
        AstroQSpace.clamp01((t - CONFIG.tOrbitIn) / (CONFIG.tOrbitEnd - CONFIG.tOrbitIn)));
      var fromR = orbR * 1.9, r = fromR + (orbR - fromR) * q;
      var ang = a0 - 0.55 * q;                        // hơi trượt theo quỹ đạo khi vào
      return {
        x: e.x + Math.cos(ang) * r,
        y: e.y + Math.sin(ang) * r,
        w: w, h: h,
        rot: (ang - Math.PI / 2) * q + (-0.10) * (1 - q),
        thrust: 1 - q * 0.78
      };
    }
    // Đã vào quỹ đạo: bay vòng chậm quanh hành tinh
    return onOrbit(a0 - 0.55 - (t - CONFIG.tOrbitEnd) * CONFIG.orbitSpin);
  }

  /* ---------------- Gõ chữ ---------------- */
  function startTyping() {
    if (sayShown) return;
    sayShown = true;
    els.say.classList.add("show");
    beepsStart();

    var full = txt("line");
    typed = 0;
    if (reduced) { finishTyping(); return; }
    typeTimer = setInterval(function () {
      typed += 1;
      if (typed >= full.length) { finishTyping(); return; }
      els.line.innerHTML = AstroQ.esc(full.slice(0, typed)) + '<span class="cur">▌</span>';
    }, CONFIG.typeMs);
  }
  function finishTyping() {
    if (typeTimer) { clearInterval(typeTimer); typeTimer = 0; }
    // Chỉ tới đây mới dùng innerHTML có <b>: gõ từng ký tự trên chuỗi có thẻ HTML
    // sẽ hiện ra "<b>Trái" giữa câu.
    els.line.innerHTML = txt("lineHtml");
    els.next.classList.remove("hide");
    if (running) els.next.focus();
  }

  /* ---------------- Pop-up sứ mệnh ---------------- */
  function showPop() {
    if (popShown) return;
    popShown = true;
    finishTyping();
    if (!sayShown) { sayShown = true; els.say.classList.add("show"); }
    beepsStop();
    els.pop.classList.add("show");
    els.pop.setAttribute("aria-hidden", "false");
    /* Ẩn cả "Bỏ qua" và "Tiếp tục": pop-up đã là đích, để hai nút cũ lại thì trẻ
       không biết phải bấm cái nào (thấy trên ảnh chụp). Box thoại vẫn để nguyên
       làm nền — đọc lại lời Comet trong lúc quyết định là điều nên có. */
    els.skip.style.display = "none";
    els.next.classList.add("hide");
    setTimeout(function () { if (running) els.go.focus(); }, 120);
  }

  function activate() {
    if (done) return;
    done = true;
    running = false;
    if (raf) { global.cancelAnimationFrame(raf); raf = 0; }
    beepsStop(); engineStop();
    if (typeTimer) { clearInterval(typeTimer); typeTimer = 0; }
    root.classList.remove("show");
    root.setAttribute("aria-hidden", "true");
    var cb = onActivate; onActivate = null;
    /* Ghi cờ XONG rồi mới gọi tiếp: `onActivate` ở dashboard điều hướng sang
       mission-earth.html, mà điều hướng thì huỷ request đang bay.
       Vẫn giữ 500ms tối thiểu để lớp phủ tan hết, trang dưới không "nhảy" ra
       giữa lúc còn mờ. */
    Promise.all([
      markSeen(),
      new Promise(function (res) { setTimeout(res, 500); })
    ]).then(function () { if (cb) cb(); });
  }

  /* ---------------- Vòng lặp ---------------- */
  function frame(now) {
    if (!running) return;
    if (!t0) { t0 = now; lastT = now; }
    var t = (now - t0) / 1000;
    var dt = Math.min((now - lastT) / 1000, 0.05);
    lastT = now;

    var e = earthAt();
    scene.clear();
    /* Điểm tụ đặt ở tâm Trái Đất giống màn loading, nhưng speed rất nhỏ (0,06):
       sao chỉ trôi lừ đừ — tàu đang bay quanh quỹ đạo, không còn lao đi. */
    scene.stars(t, dt, reduced ? 0 : 0.06, { x: e.x, y: e.y });
    scene.earth(t, e.x, e.y, e.R);
    scene.ship(shipAt(t));

    if (!sayShown && t >= CONFIG.tSay) startTyping();

    raf = global.requestAnimationFrame(frame);
  }

  /* ---------------- Ngôn ngữ ---------------- */
  function paintTexts() {
    if (!els) return;
    els.skip.textContent = txt("skip");
    els.who.textContent = txt("who");
    els.role.textContent = txt("role");
    els.next.textContent = txt("next");
    els.code.textContent = txt("code");
    els.ttl.textContent = txt("title");
    els.sub.textContent = txt("sub");
    els.go.textContent = txt("go");
    // Đang gõ giữa câu thì để nguyên; gõ xong rồi mới dịch lại cả câu
    if (sayShown && !typeTimer) els.line.innerHTML = txt("lineHtml");
  }

  var AstroQMissionIntro = {
    CONFIG: CONFIG,

    /** Mở màn phim ngay, không hỏi cờ đã xem. opts: {lang, onActivate} */
    start: function (opts) {
      opts = opts || {};
      lang = opts.lang === "en" ? "en" : "vi";
      onActivate = typeof opts.onActivate === "function" ? opts.onActivate : null;
      reduced = AstroQSpace.isReduced();
      build();
      scene.resize();
      paintTexts();
      els.line.textContent = "";
      els.next.classList.add("hide");
      els.pop.classList.remove("show");
      els.pop.setAttribute("aria-hidden", "true");
      els.skip.style.display = "";
      sayShown = false; popShown = false; done = false;
      t0 = 0; lastT = 0; running = true;
      root.classList.add("show");
      root.setAttribute("aria-hidden", "false");
      engineStart();
      raf = global.requestAnimationFrame(frame);
      // Bớt chuyển động: không có đoạn bay vào, hiện thoại + pop-up gần như ngay
      if (reduced) setTimeout(function () { if (running) startTyping(); }, 250);
      return true;
    },

    /** Đã xem chưa (theo cache trong máy — chưa hỏi server). */
    isSeen: localSeen,

    /** Xoá cờ ở CẢ hai nơi để xem lại (dùng khi thử nghiệm). */
    reset: function () {
      setLocalSeen(false);
      return waitAuth(SERVER_WAIT_MS).then(function (a) {
        return a && a.setOnboarding ? a.setOnboarding({ intro01Seen: false }) : { ok: false };
      });
    },

    /**
     * Hỏi cờ rồi mới quyết có chạy. Cùng cách làm với js/onboard-tour.js: cache
     * nói "đã xem" → bỏ qua ngay; cache rỗng → hỏi server (có hạn chờ) để người
     * đã xem ở máy khác không phải xem lại; server không trả lời được → vẫn chạy.
     * → Promise<boolean>
     */
    autoStart: function (opts) {
      opts = opts || {};
      if (localSeen()) return Promise.resolve(false);
      return waitAuth(SERVER_WAIT_MS).then(function (a) {
        if (!a || !a.getOnboarding) return null;
        return a.getOnboarding();
      }).catch(function () { return null; }).then(function (r) {
        if (r && r.ok && r.intro01Seen) { setLocalSeen(true); return false; }
        AstroQMissionIntro.start(opts);
        return true;
      });
    },

    /** Đổi ngôn ngữ giữa lúc đang chạy. */
    setLang: function (l) {
      lang = l === "en" ? "en" : "vi";
      paintTexts();
    },

    /** Nhảy thẳng tới pop-up (giống bấm "Bỏ qua"). */
    skip: showPop,

    isOpen: function () { return running; }
  };

  global.AstroQMissionIntro = AstroQMissionIntro;
})(window);
