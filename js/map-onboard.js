/* ============================================================================
   js/map-onboard.js — COMET DẪN ĐƯỜNG Ở BẢN ĐỒ THIÊN HÀ, lượt onboarding.
   (bước ①–④ của `docs/decisions/003`)

   Nhịp: màn warp "ĐANG DU HÀNH TỚI · Hệ Mặt Trời" → Comet giới thiệu ở ĐÁY màn
   hình → trẻ chạm Trái Đất → bảng thông tin mở → **sau ít nhất 10 giây** Comet hỏi
   "sẵn sàng chưa?" → nút OK → `mission-earth.html`.

   ⚠️ FILE NÀY KHÔNG BIẾT GÌ VỀ three.js. Nó nhận đúng những gì cần qua `init()`
      (`warpShow` · `warpHide` · `ready` · `t` · `regionName` · `onGo`), nên `explorer.html`
      không phình thêm và bộ test lái được bằng cách gọi thẳng vào đây.

   ⚠️ 10 GIÂY LÀ **SÀN**, KHÔNG PHẢI HẠN. Câu hỏi của Comet hiện ra *cạnh* bảng thông
      tin và **không đóng nó**; trẻ tự đóng khi đọc xong. Dự án đã trả giá đúng chỗ này
      với đường về tự động 5 giây: *"trẻ đọc chậm hơn người lớn nhiều, một màn thưởng tự
      biến mất sau 5 giây là màn thưởng bị lấy đi giữa lúc đang đọc."* Vì là SÀN nên
      tương tác KHÔNG huỷ đồng hồ — ngược với đường về tự động, nơi tương tác phải tắt nó.

   ⚠️ ĐỒNG HỒ CHỈ CHẠY KHI BẢNG THÔNG TIN ĐÃ MỞ THẬT. Bấm vào hành tinh thì camera
      bay 1,6s rồi bảng mới mở; đếm từ lúc bấm là trẻ mất gần 2 giây đọc.

   Xem lại để thử: mở `explorer.html?onboard=1`.
   ============================================================================ */
(function (global) {
  "use strict";

  var TXT = {
    vi: {
      nm: "Comet", tag: "HOA TIÊU",
      l1: "Đây là <b>Hệ Mặt Trời</b> của chúng ta — nơi có rất nhiều thứ để khám phá!",
      l2: "Hãy bắt đầu từ <b>Trái Đất</b>, hành tinh xanh của chúng ta nhé. " +
          "Chạm vào Trái Đất để xem thông tin!",
      ask: "Bạn đã sẵn sàng bắt đầu hành trình với <b>nhiệm vụ đầu tiên</b> tại Trái Đất chưa?",
      next: "Tiếp tục ›", ok: "OK, bắt đầu! 🚀"
    },
    en: {
      nm: "Comet", tag: "NAVIGATOR",
      l1: "This is our <b>Solar System</b> — there is so much to explore here!",
      l2: "Let's start with <b>Earth</b>, our blue planet. Tap Earth to read about it!",
      ask: "Are you ready to begin your <b>first mission</b> here on Earth?",
      next: "Next ›", ok: "OK, let's go! 🚀"
    }
  };

  /* Mốc thời gian. `READ_MS` là con số chủ dự án chốt (10 giây). */
  var READ_MS = 10000;
  var WARP_MIN_MS = 1800;      // màn warp phải sống đủ lâu để đọc được tên vùng
  var WARP_MAX_MS = 12000;     // cảnh 3D không dựng được thì cũng phải nhả ra
  var TYPE_MS = 22;            // ms mỗi ký tự

  /* ⚠️ CACHE "ĐÃ ĐI QUA BẢN ĐỒ" — BẮT BUỘC, KHÔNG PHẢI TỐI ƯU.
     `explorer.html` **cố ý không nạp** `js/firebase-auth.js` (233 KB) nên nó KHÔNG có
     token để ghi cờ `map01Seen` lên server. Mà `dashboard.html` lại dựa vào cờ đó để
     quyết có đẩy trẻ sang bản đồ hay không. Thiếu cầu nối này thì:
        dashboard (cờ vẫn false) → bản đồ → nhiệm vụ → dashboard (cờ VẪN false) → …
     tức **trẻ bị đẩy lại bản đồ mỗi lần mở dashboard**. Nên: ở đây ghi cache trong máy,
     `dashboard.html` đọc cache trước rồi mới đẩy cờ thật lên server.
     Đúng khuôn `astroq-tour-seen` đã dùng cho `tourSeen`. */
  var SEEN_KEY = "astroq-map01-seen";

  function markSeen() {
    try { global.localStorage.setItem(SEEN_KEY, "1"); } catch (e) {}
  }

  var A = null;                // các hàm do explorer.html truyền vào
  var lang = "vi";
  var el = {};
  var reduced = false;
  var timer = null, typing = null;
  var state = "idle";          // idle · warp · intro · waitEarth · reading · ask · done

  function t(k) { return (TXT[lang] || TXT.vi)[k]; }

  function $(id) { return global.document.getElementById(id); }

  function cache() {
    el.say = $("mo-say"); el.line = $("mo-line"); el.next = $("mo-next");
    el.nm = $("mo-nm"); el.tag = $("mo-tag");
    return !!(el.say && el.line && el.next);
  }

  function show(on) {
    if (!el.say) return;
    el.say.classList.toggle("show", on !== false);
    el.say.setAttribute("aria-hidden", on === false ? "true" : "false");
  }

  /* Gõ từng chữ. Chuỗi có thẻ `<b>` nên KHÔNG gõ theo ký tự của HTML thô —
     làm vậy thì giữa lúc gõ sẽ lộ ra chữ "<b" trên màn hình. Gõ theo VĂN BẢN rồi
     mới dựng lại thẻ ở cuối. */
  function say(html, done) {
    if (typing) { clearInterval(typing); typing = null; }
    if (!el.line) return;
    if (reduced) { el.line.innerHTML = html; if (done) done(); return; }
    var plain = html.replace(/<[^>]+>/g, "");
    var i = 0;
    el.line.textContent = "";
    typing = setInterval(function () {
      i++;
      el.line.textContent = plain.slice(0, i);
      if (i >= plain.length) {
        clearInterval(typing); typing = null;
        el.line.innerHTML = html;      // dựng lại <b> sau khi gõ xong
        if (done) done();
      }
    }, TYPE_MS);
  }

  function button(label, onClick) {
    if (!el.next) return;
    if (!label) { el.next.classList.add("hide"); el.next.onclick = null; return; }
    el.next.textContent = label;
    el.next.classList.remove("hide");
    el.next.onclick = onClick;
  }

  /* ─────────────────── ① màn warp lúc vào trang ─────────────────── */
  function warp() {
    state = "warp";
    A.warpShow();
    var t0 = Date.now ? Date.now() : new Date().getTime();
    var min = reduced ? 400 : WARP_MIN_MS;
    (function wait() {
      var dt = (Date.now ? Date.now() : new Date().getTime()) - t0;

      /* ⑧ ĐƯỜNG LÙI KHI CẢNH 3D KHÔNG DỰNG ĐƯỢC (docs/decisions/003).
         ⚠️ `explorer.html` giờ nằm trên luồng onboarding **BẮT BUỘC**, mà nó nạp
            three.js + OrbitControls + EffectComposer + UnrealBloomPass + CSS2DRenderer
            từ **`unpkg.com`** — một tên miền không ai trong dự án kiểm soát. Không có
            nhánh này thì mất mạng / CDN lỗi = phi hành gia mới **không đi qua được
            onboarding**, trong khi trước lượt đổi luồng họ vẫn tới được dashboard.
         Trẻ mất màn phim, KHÔNG mất nhiệm vụ: `mission-earth.html` đã là 2D
         (`js/earth2d.js`), không cần tên miền ngoài nào. */
      if (dt >= WARP_MAX_MS && !A.ready()) {
        state = "fallback";
        /* ⚠️ ĐÁNH DẤU ĐÃ ĐI QUA KỂ CẢ Ở ĐƯỜNG LÙI, dù trẻ chưa thật sự thấy bản đồ.
           Không đánh dấu thì mỗi lần mở dashboard nó lại bị đẩy sang đây, lại lỗi, lại
           rơi vào nhiệm vụ — tức là **không bao giờ dùng được dashboard** khi mạng yếu.
           Bản đồ vẫn tới được bất cứ lúc nào từ thẻ MOD-03. */
        markSeen();
        if (A.onSceneFail) { A.onSceneFail(); return; }
        // Không khai `onSceneFail` thì thà đi tiếp nhịp phim còn hơn treo mãi ở màn warp.
        A.warpHide(); intro(); return;
      }

      if (dt >= min && A.ready()) { A.warpHide(); intro(); return; }
      setTimeout(wait, 120);
    })();
  }

  /* ─────────────────── ② + ③ Comet giới thiệu ─────────────────── */
  function intro() {
    state = "intro";
    if (!cache()) return;
    el.nm.textContent = t("nm"); el.tag.textContent = t("tag");
    button(null);
    show(true);
    say(t("l1"), function () {
      button(t("next"), function () {
        button(null);
        say(t("l2"), function () { waitEarth(); });
      });
    });
  }

  /* ─────────────────── ④ chờ trẻ chạm Trái Đất ─────────────────── */
  function waitEarth() {
    state = "waitEarth";
    var info = $("info");
    if (!info) return;

    /* Nghe THAY ĐỔI CLASS của bảng thông tin thay vì móc vào `selectBody`.
       Nhờ vậy file này không phụ thuộc nội tạng của cảnh 3D, và mọi đường mở bảng
       (chạm quả cầu · bấm nhãn · danh sách bảng trái) đều được tính. */
    var mo = new global.MutationObserver(function () {
      if (state !== "waitEarth") return;
      if (!info.classList.contains("open")) return;
      if (A.selectedId() !== "earth") return;      // mở hành tinh khác thì chưa tính
      mo.disconnect();
      reading();
    });
    mo.observe(info, { attributes: true, attributeFilter: ["class"] });

    // Đã mở sẵn từ trước (trẻ bấm nhanh hơn lời thoại) thì tính luôn.
    if (info.classList.contains("open") && A.selectedId() === "earth") {
      mo.disconnect(); reading();
    }
  }

  /* Bảng thông tin đã mở → đếm SÀN 10 giây rồi mới hỏi. */
  function reading() {
    state = "reading";
    show(false);                                   // nhường chỗ cho trẻ đọc bảng
    if (timer) clearTimeout(timer);
    timer = setTimeout(ask, reduced ? 1200 : READ_MS);
  }

  function ask() {
    state = "ask";
    if (!cache()) return;
    show(true);
    say(t("ask"), function () {
      button(t("ok"), function () {
        state = "done";
        button(null);
        markSeen();          // ghi cache TRƯỚC khi rời trang — xem SEEN_KEY ở trên
        A.onGo();
      });
    });
  }

  global.AstroQMapOnboard = {
    /** Nhịp phim chạy được thì trả true. Thiếu hàm nào là không chạy, không nửa vời. */
    init: function (api) {
      if (!api || !api.warpShow || !api.warpHide || !api.ready ||
          !api.selectedId || !api.onGo) return false;
      A = api;
      lang = api.lang === "en" ? "en" : "vi";
      try { reduced = global.matchMedia("(prefers-reduced-motion: reduce)").matches; }
      catch (e) { reduced = false; }
      if (!cache()) return false;
      warp();
      return true;
    },

    /** Đổi ngôn ngữ giữa chừng (tab khác bấm VI/EN) — dịch lại đúng câu đang hiện. */
    setLang: function (l) {
      lang = l === "en" ? "en" : "vi";
      if (!cache() || state === "idle" || state === "done") return;
      el.nm.textContent = t("nm"); el.tag.textContent = t("tag");
      if (state === "ask") { el.line.innerHTML = t("ask"); button(t("ok"), el.next.onclick); }
      else if (state === "intro" || state === "waitEarth") { el.line.innerHTML = t("l2"); }
    },

    /** Bề mặt cho bộ test: đọc trạng thái + rút ngắn mốc chờ. */
    _state: function () { return state; },
    _setReadMs: function (ms) { READ_MS = Math.max(0, ms | 0); },
    /** Rút hạn chờ cảnh 3D — để test đo được đường lùi mà không phải ngồi 12 giây. */
    _setWarpMaxMs: function (ms) { WARP_MAX_MS = Math.max(0, ms | 0); },
    READ_MS: READ_MS,
    WARP_MAX_MS: WARP_MAX_MS,

    /** Xem lại nhịp phim: Console gõ `AstroQMapOnboard.reset()` rồi mở
     *  `explorer.html?onboard=1`. Chỉ xoá CACHE trong máy — cờ thật ở server thì
     *  dùng `AstroQAuth.setOnboarding({ map01Seen:false })` trên một trang có token. */
    reset: function () {
      try { global.localStorage.removeItem(SEEN_KEY); } catch (e) {}
    },
    SEEN_KEY: SEEN_KEY
  };
})(window);
