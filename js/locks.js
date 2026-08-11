/* ══════════════════════════════════════════════════════════════════════════
   AstroQLocks — CHỖ DUY NHẤT khai trạng thái khoá của các khu/nhiệm vụ,
   và modal giải thích "vì sao khoá · cần làm gì để mở".

   Dùng chung bởi dashboard.html · missions.html · games.html.
   Nạp SAU js/ui-common.js (cần AstroQ.getLang/esc) và cần css/locks.css.

   ⚠️⚠️ BA TRẠNG THÁI, KHÔNG PHẢI HAI. Đây là chốt chặn quan trọng nhất của file:

     free — mở, không khoá.
     soon — CHƯA CÓ NỘI DUNG. Nói thật là đang phát triển.
     pro  — CÓ nội dung thật, cần gói trả phí mới vào được.

   ⛔ TUYỆT ĐỐI KHÔNG gắn `pro` cho thứ chưa dựng xong. Gắn `pro` là nói với phụ
      huynh "trả tiền sẽ mở được"; trả tiền xong mà bên trong rỗng thì đó là một
      lời hứa hệ thống không giữ được — và lần này nó gắn với một giao dịch.
      Dự án đã đặt tên cái bẫy này hai lần:
        · js/specimens.js — "đừng viết 'Mở khoá tại Mission 02': nhiệm vụ ĐÓ chưa
          tồn tại nên mẫu sẽ khoá vĩnh viễn";
        · codex.html — phải tách riêng trạng thái `soon` cho thẻ chưa có câu hỏi,
          và ở trạng thái đó thì KHÔNG dẫn sang Quiz.
      Ở đây cũng vậy: `soon` thì KHÔNG có nút "Mở khoá ngay".

   ⚠️ `plan: null` nghĩa là "sắp ra mắt và sẽ MIỄN PHÍ" — modal của nó không có
      lời mời mua gì cả. Ba mini-game chưa dựng nằm nhóm này: docs/decisions/009
      không xếp mini-game vào phần trả phí.

   ⚠️ TRẺ LÀ NGƯỜI ĐỌC MODAL NÀY, PHỤ HUYNH MỚI LÀ NGƯỜI TRẢ TIỀN (009, mục Hệ
      quả). Nên: không hối thúc, không đếm ngược, không "chỉ còn hôm nay"; câu
      dẫn sang trang giá luôn kèm "nhờ bố mẹ xem giúp".

   Thêm một khu bị khoá: thêm một dòng vào ITEMS + khoá chữ vào CẢ `vi` và `en`.
   ══════════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var PRICING = "pricing.html";

  /* state: "soon" | "pro"   ·   plan: "astronaut" | "crew" | null (miễn phí)
     feats: khoá chữ liệt kê trong modal (tối đa 3 — dài hơn thì trẻ không đọc) */
  var ITEMS = {
    "lab": {
      state: "soon", plan: "astronaut", ic: "🔬",
      feats: ["f_lab_1", "f_lab_2", "f_lab_3"]
    },
    "mission:moon": {
      state: "soon", plan: "astronaut", ic: "🌙",
      feats: ["f_moon_1", "f_moon_2", "f_moon_3"]
    },
    /* Ba mini-game: sắp ra mắt và SẼ MIỄN PHÍ → không mời mua. */
    "game:racer": { state: "soon", plan: null, ic: "☄️" },
    "game:maze":  { state: "soon", plan: null, ic: "🌀" },
    "game:catch": { state: "soon", plan: null, ic: "🌟" }
  };

  var T = {
    vi: {
      badge_soon: "SẮP RA MẮT",
      badge_pro: "GÓI TRẢ PHÍ",
      title_soon: "Khu này đang được xây",
      title_pro: "Khu này thuộc gói {plan}",

      /* ⚠️ Câu `soon` KHÔNG được hứa mở bằng tiền — nó chưa tồn tại. */
      body_soon_plan: "Đội ngũ astroQ đang dựng khu này. Khi xong, nó sẽ nằm trong gói {plan}.",
      body_soon_free: "Đội ngũ astroQ đang dựng trò này. Khi xong, ai cũng chơi được — không mất phí.",
      body_pro: "Bạn cần gói {plan} để vào khu này.",

      will_get: "Khi mở, bạn sẽ được:",
      parent_note: "Việc mua gói là của người lớn — bạn nhờ bố mẹ xem giúp trang này nhé.",
      founder_note: "Bố mẹ đăng ký Vé Sáng Lập bây giờ thì có sẵn khu này ngay ngày nó mở.",

      cta_pricing: "Xem các gói",
      cta_close: "Đã hiểu",

      plan_astronaut: "Phi Hành Gia",
      plan_crew: "Phi Hành Đoàn",

      f_lab_1: "Tự tay làm thí nghiệm trộn nguyên tố",
      f_lab_2: "Thả rơi vật thể ở trọng lực của 8 hành tinh",
      f_lab_3: "Ghi kết quả vào sổ nghiên cứu riêng",
      f_moon_1: "Nhiệm vụ nhiều bước ở Mặt Trăng",
      f_moon_2: "Mẫu vật và huy hiệu chỉ có ở đây",
      f_moon_3: "Mở tiếp đường bay tới hành tinh sau"
    },
    en: {
      badge_soon: "COMING SOON",
      badge_pro: "PAID PLAN",
      title_soon: "This area is being built",
      title_pro: "This area is part of {plan}",

      body_soon_plan: "The astroQ team is building this area. When it lands, it will be part of {plan}.",
      body_soon_free: "The astroQ team is building this game. When it lands, everyone can play — free.",
      body_pro: "You need the {plan} plan to enter this area.",

      will_get: "When it opens, you get:",
      parent_note: "Buying a plan is a grown-up job — ask a parent to look at this page with you.",
      founder_note: "If a parent gets the Founder Pass now, this area is included the day it opens.",

      cta_pricing: "See the plans",
      cta_close: "Got it",

      plan_astronaut: "Astronaut",
      plan_crew: "Crew",

      f_lab_1: "Run your own element-mixing experiments",
      f_lab_2: "Drop objects at the gravity of all 8 planets",
      f_lab_3: "Record results in your own research log",
      f_moon_1: "A multi-step mission on the Moon",
      f_moon_2: "Specimens and badges found only here",
      f_moon_3: "Unlocks the route to the next planet"
    }
  };

  function lang() {
    return (window.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
  }

  function t(k, L) {
    var d = T[L || lang()];
    return (d && d[k] != null) ? d[k] : k;
  }

  function esc(s) {
    return (window.AstroQ && AstroQ.esc) ? AstroQ.esc(s) : String(s);
  }

  /* ── Modal: dựng LƯỜI, một lần cho cả trang ──
     Dùng lại `.modal` / `.modal.show` của css/common.css cho phần định vị và
     ẩn/hiện; phần ruột là `.lk-*` riêng ở css/locks.css.
     ⚠️ KHÔNG chép `.modal-card`/`.m-btn` — ba bản của chúng đã nằm rải ở
        dashboard.css / games.css / quiz.css và KHÔNG giống hệt nhau, nên chép
        thêm bản thứ tư là sớm muộn bốn cái trôi khỏi nhau. */
  var el = null, lastFocus = null;

  function build() {
    if (el) return el;
    el = document.createElement("div");
    el.className = "modal lk-modal";
    el.id = "aq-lock";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-modal", "true");
    el.setAttribute("aria-hidden", "true");
    el.setAttribute("aria-labelledby", "lk-title");
    el.innerHTML =
      '<div class="lk-card">' +
        '<div class="lk-ic" id="lk-ic" aria-hidden="true">🔒</div>' +
        '<span class="lk-badge" id="lk-badge"></span>' +
        '<h3 id="lk-title"></h3>' +
        '<p class="lk-body" id="lk-body"></p>' +
        '<div class="lk-feats" id="lk-feats" hidden>' +
          '<span class="lk-feats-h" id="lk-feats-h"></span>' +
          '<ul id="lk-list"></ul>' +
        '</div>' +
        '<p class="lk-note" id="lk-note" hidden></p>' +
        '<div class="lk-acts">' +
          '<a class="lk-btn primary" id="lk-go" href="' + PRICING + '"></a>' +
          '<button class="lk-btn" id="lk-close" type="button"></button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(el);

    el.querySelector("#lk-close").addEventListener("click", close);
    // Bấm ra nền thì đóng — nhưng chỉ khi bấm ĐÚNG lớp phủ, không phải thẻ con.
    el.addEventListener("click", function (e) { if (e.target === el) close(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && el.classList.contains("show")) close();
    });
    return el;
  }

  function open(key, trigger) {
    var it = ITEMS[key];
    if (!it) return false;
    var L = lang();
    build();

    var planName = it.plan ? t("plan_" + it.plan, L) : "";
    var isSoon = it.state === "soon";

    el.querySelector("#lk-ic").textContent = it.ic || "🔒";
    el.querySelector("#lk-badge").textContent = t(isSoon ? "badge_soon" : "badge_pro", L);
    el.querySelector("#lk-badge").className = "lk-badge" + (isSoon ? " soon" : " pro");

    el.querySelector("#lk-title").textContent =
      (isSoon ? t("title_soon", L) : t("title_pro", L)).replace("{plan}", planName);

    var body = !it.plan ? t("body_soon_free", L)
             : isSoon   ? t("body_soon_plan", L)
             :            t("body_pro", L);
    el.querySelector("#lk-body").textContent = body.replace("{plan}", planName);

    // Danh sách quyền lợi — chỉ khi có gói VÀ có khai `feats`
    var wrap = el.querySelector("#lk-feats");
    if (it.plan && it.feats && it.feats.length) {
      el.querySelector("#lk-feats-h").textContent = t("will_get", L);
      el.querySelector("#lk-list").innerHTML =
        it.feats.map(function (k) { return "<li>" + esc(t(k, L)) + "</li>"; }).join("");
      wrap.hidden = false;
    } else {
      wrap.hidden = true;
    }

    /* Ghi chú: chỉ hiện khi CÓ mời xem gói. Trò miễn phí thì không có gì để mời,
       thêm một dòng nói về tiền vào đó là quảng cáo chen vào chỗ không cần. */
    var note = el.querySelector("#lk-note");
    if (it.plan) {
      note.textContent = (isSoon ? t("founder_note", L) + " " : "") + t("parent_note", L);
      note.hidden = false;
    } else {
      note.hidden = true;
    }

    var go = el.querySelector("#lk-go");
    go.textContent = t("cta_pricing", L);
    go.hidden = !it.plan;              // miễn phí → không có nút dẫn sang trang giá
    el.querySelector("#lk-close").textContent = t("cta_close", L);

    lastFocus = trigger || document.activeElement;
    el.classList.add("show");
    el.setAttribute("aria-hidden", "false");
    // Tiêu điểm về nút đầu tiên đang hiện, để bàn phím dùng được ngay
    (it.plan ? go : el.querySelector("#lk-close")).focus();
    return true;
  }

  function close() {
    if (!el) return;
    el.classList.remove("show");
    el.setAttribute("aria-hidden", "true");
    /* Trả tiêu điểm về đúng chỗ vừa bấm — ném về <body> là người dùng bàn phím
       mất chỗ đang đứng. Cùng cách specimen-vault.html đã làm. */
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    lastFocus = null;
  }

  /* Gắn vào một phần tử: bấm là mở modal. Trả về true nếu key có thật. */
  function wire(node, key) {
    if (!node || !ITEMS[key]) return false;
    node.addEventListener("click", function (e) {
      e.preventDefault();
      open(key, node);
    });
    return true;
  }

  function get(key) { return ITEMS[key] || null; }
  function state(key) { return ITEMS[key] ? ITEMS[key].state : "free"; }
  function all() { return Object.keys(ITEMS); }

  window.AstroQLocks = {
    get: get, state: state, all: all,
    open: open, close: close, wire: wire,
    text: t, PRICING: PRICING
  };
})();
