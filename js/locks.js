/* ══════════════════════════════════════════════════════════════════════════
   AstroQLocks — CHỖ DUY NHẤT khai trạng thái khoá của các khu/nhiệm vụ,
   và modal giải thích "vì sao khoá · cần làm gì để mở".

   Dùng chung bởi dashboard.html · mission-map.html · games.html.
   ⚠️ `mission:moon` ĐỔI CHỖ ĐỌC 12/08/2026: Mặt Trăng không còn là một THẺ ở
      `missions.html` (trang đó nay là cửa trước, không còn lưới thẻ) mà là một
      ĐIỂM ĐẾN trên bản đồ nhiệm vụ. Mục khai ở đây giữ nguyên — chỉ người đọc đổi.
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

   ⚠️⚠️ VÀ MỘT BIẾN THỂ THỨ TƯ CỦA LỜI VĂN, thêm 12/08/2026: `pro` KHI CHƯA MỞ BÁN.
      Đây không phải trạng thái thứ tư (`state` vẫn là `pro`) mà là một cách NÓI
      khác, quyết bởi cờ `SALE_OPEN` do trang truyền vào.
      Vì sao bắt buộc phải có: hôm nay `SALE_OPEN` KHÔNG khai trong `template.yaml`
      (chủ đích) nên `/checkout` trả `sale-closed` và `pricing.html` nói "chưa mở
      bán". Một thẻ `pro` mà không có biến thể này thì đường đi của trẻ là:
         thẻ → "Dành cho gói Phi Hành Gia" → [Xem các gói] → "chưa mở bán" → HẾT.
      Tức câu `body_pro` ("Mở gói {plan} là vào được ngay") là một câu SAI, và
      trẻ gặp một ngõ cụt. Cùng nguyên tắc đã chốt cho `checkout.html`: *chưa mở
      bán thì BỎ HẲN cổng phụ huynh — một ngày thu cụ thể cho một giao dịch không
      thể xảy ra là một câu nói sai dù phép tính đúng.*
      ⇒ Biến thể này nói thật là đã làm xong nhưng chưa bán, và **KHÔNG có nút dẫn
        sang trang giá**, cũng không có dòng mời bố mẹ (không có gì để mời).

   ⚠️ `SALE_OPEN` MẶC ĐỊNH `false` — fail-closed. Đọc không được `/billing/catalog`
      thì nghiêng về "chưa mở bán", tức KHÔNG BAO GIỜ mời mua khi chưa biết chắc.
      Trang nào KHÔNG có mục `pro` nào thì đừng gọi `setSaleOpen` — thêm một vòng
      mạng chỉ để lấy một cờ mà không ai đọc là đi ngược đúng bài học `missionsShared()`.

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
  /* ⚠️ Cờ "đã mở bán chưa" — mặc định false (fail-closed), trang tự truyền vào.
     Chỉ `lab.html` gọi `setSaleOpen()` vì hôm nay chỉ nó có mục `pro`. */
  var SALE_OPEN = false;

  var ITEMS = {
    /* ⚠️ Mục `"lab"` (cả KHU Phòng Nghiên Cứu bị khoá) ĐÃ BỎ 12/08/2026 — khu đó
       nay có trang thật `lab.html`, nên thẻ MOD-05 ở dashboard không còn khoá.
       Thay vào đó là khoá theo TỪNG THẺ hoạt động bên trong. Nhờ vậy dashboard
       còn 0 card khoá; `check_pages` mục [7b] đã đổi phát biểu theo.
       LAB-01 KHÔNG có mục ở đây: nó là thẻ miễn phí để trải nghiệm. */
    "lab:float": {
      state: "pro", plan: "astronaut", ic: "🧑‍🚀",
      feats: ["f_lab_1", "f_lab_2", "f_lab_3"]
    },
    "lab:weigh": {
      state: "pro", plan: "astronaut", ic: "⚖️",
      feats: ["f_lab_1", "f_lab_2", "f_lab_3"]
    },
    /* Ba thẻ chưa dựng xong → `soon`, KHÔNG phải `pro`. Gắn `pro` cho thứ chưa
       tồn tại là nói với phụ huynh "trả tiền sẽ mở được" — xem cảnh báo đầu file. */
    /* LAB-07 + LAB-08: DA DUNG XONG, nen `pro` chu khong `soon`. Xem canh bao dau
       file: gan `pro` cho thu chua dung xong moi la loi. */
    "lab:sky":   { state: "pro", plan: "astronaut", ic: "🌇",
                   feats: ["f_lab_1", "f_lab_2", "f_lab_3"] },
    "lab:drops": { state: "pro", plan: "astronaut", ic: "💧",
                   feats: ["f_lab_1", "f_lab_2", "f_lab_3"] },
    "lab:throw": { state: "soon", plan: "astronaut", ic: "🎯" },
    "lab:tide":  { state: "soon", plan: "astronaut", ic: "🌊" },
    "lab:mix":   { state: "soon", plan: "astronaut", ic: "⚗️" },
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
      badge_pro: "GÓI PHI HÀNH GIA",
      /* ⚠️ Câu chữ ở đây phải đọc được cho CẢ một khu (Phòng Nghiên Cứu) và một
         NHIỆM VỤ (Mặt Trăng) — cùng một bảng chữ phục vụ hai loại. Vì thế không
         gọi tên loại ("khu này" cho một nhiệm vụ là câu sai). */
      title_soon: "Đang được xây, sắp xong rồi",
      title_pro: "Dành cho gói {plan}",

      /* ⚠️ Câu `soon` KHÔNG được hứa mở bằng tiền — nó chưa tồn tại. */
      body_soon_plan: "Bọn mình đang dựng nốt. Xong rồi thì nó nằm trong gói {plan}.",
      body_soon_free: "Bọn mình đang dựng nốt. Xong rồi thì ai cũng chơi được — không mất phí.",
      body_pro: "Mở gói {plan} là vào được ngay.",

      /* ⚠️ Biến thể `pro` KHI CHƯA MỞ BÁN. Nó phải nói đủ hai điều mà ba câu kia
         không nói được: thứ này ĐÃ LÀM XONG (khác `soon`), và HÔM NAY KHÔNG MUA
         ĐƯỢC (khác `pro`). Bỏ một trong hai là hoặc hứa hão, hoặc dẫn vào ngõ cụt. */
      title_notyet: "Sắp mở — dành cho gói {plan}",
      body_notyet: "Thí nghiệm này bọn mình làm xong rồi, nhưng gói {plan} chưa mở bán nên chưa mời bạn mua gì cả. Sắp có nhé!",

      will_get: "Trong này sẽ có:",
      parent_note: "Chuyện gói và giá là việc của người lớn — rủ bố mẹ xem cùng nhé.",
      founder_note: "Bố mẹ lấy Vé Sáng Lập từ bây giờ là có sẵn ngay hôm mở cửa.",

      cta_pricing: "Xem các gói",
      cta_close: "Đã hiểu",

      plan_astronaut: "Phi Hành Gia",
      plan_crew: "Phi Hành Đoàn",

      /* ⚠️ VIẾT LẠI 12/08/2026. Ba dòng cũ đều hứa thứ CHƯA CÓ, không chỉ riêng
         dòng thứ hai: "Trộn nguyên tố" là LAB-06 với 0 dữ liệu 0 nguồn, và "sổ
         nghiên cứu riêng" là một bộ sưu tập thứ tư mà đề xuất cố ý không làm
         (dự án đã có ba: Hồ sơ hành tinh · Sổ Tay · Kho Mẫu Vật).
         ⚠️⚠️ DÒNG 2 KỂ ĐÚNG BA NƠI CÓ NGUỒN, VÀ SAO HOẢ KHÔNG PHẢI MỘT TRONG BA.
         Trang Space Place chỉ nhắc Sao Hoả khi nói về KHỐI LƯỢNG, không cho tỉ lệ
         cân nặng nào — kể Sao Hoả ở đây là bịa một con số trong một lời chào mời.
         Đổi số nơi thật sự ship thì phải đổi dòng này; `check_pages` canh hai bên. */
      f_lab_1: "Vì sao phi hành gia trôi trong không gian",
      f_lab_2: "Cân của em ở Mặt Trăng, Sao Thuỷ, Sao Mộc",
      f_lab_3: "Lời giải thích có hai độ sâu, lớn thêm là đọc sâu thêm",
      f_moon_1: "Cả một nhiệm vụ dài trên Mặt Trăng",
      f_moon_2: "Mẫu vật và huy hiệu chỉ Mặt Trăng mới có",
      f_moon_3: "Mở đường bay tới hành tinh kế tiếp"
    },
    en: {
      badge_soon: "COMING SOON",
      badge_pro: "ASTRONAUT PLAN",
      title_soon: "Still being built — almost there",
      title_pro: "Part of the {plan} plan",

      body_soon_plan: "We're still putting this together. Once it lands, it comes with the {plan} plan.",
      body_soon_free: "We're still putting this together. Once it lands, everyone can play — free.",
      body_pro: "Open the {plan} plan and you're straight in.",

      title_notyet: "Opening soon — part of the {plan} plan",
      body_notyet: "This experiment is finished and waiting, but the {plan} plan is not on sale yet, so there's nothing for you to buy right now. Soon!",

      will_get: "Inside you'll find:",
      parent_note: "Plans and prices are a grown-up thing — ask a parent to look with you.",
      founder_note: "If a parent grabs the Founder Pass now, it's included the day it opens.",

      cta_pricing: "See the plans",
      cta_close: "Got it",

      plan_astronaut: "Astronaut",
      plan_crew: "Crew",

      f_lab_1: "Why astronauts float in space",
      f_lab_2: "Your weight on the Moon, Mercury and Jupiter",
      f_lab_3: "Two depths of explanation — read deeper as you grow",
      f_moon_1: "A whole mission up on the Moon",
      f_moon_2: "Specimens and badges only the Moon has",
      f_moon_3: "Opens the route to the next planet"
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
    /* Da lam xong (pro) NHUNG chua ban duoc -> noi that, va khong moi mua gi. */
    var notYet = (it.state === "pro" && !SALE_OPEN);

    el.querySelector("#lk-ic").textContent = it.ic || "🔒";
    el.querySelector("#lk-badge").textContent = t(isSoon ? "badge_soon" : "badge_pro", L);
    el.querySelector("#lk-badge").className = "lk-badge" + (isSoon ? " soon" : " pro");

    el.querySelector("#lk-title").textContent =
      (isSoon ? t("title_soon", L)
       : notYet ? t("title_notyet", L)
       : t("title_pro", L)).replace("{plan}", planName);

    var body = !it.plan ? t("body_soon_free", L)
             : isSoon   ? t("body_soon_plan", L)
             : notYet   ? t("body_notyet", L)
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
    /* ⚠️ Chua mo ban thi AN HAN dong nay: no moi bo me di xem gia, ma trang gia
       dang noi "chua mo ban". Moi nguoi ta xem mot thu khong co la phien vo ich. */
    if (it.plan && !notYet) {
      note.textContent = (isSoon ? t("founder_note", L) + " " : "") + t("parent_note", L);
      note.hidden = false;
    } else {
      note.hidden = true;
    }

    var go = el.querySelector("#lk-go");
    go.textContent = t("cta_pricing", L);
    /* An nut khi: mien phi (khong co gi de mua) HOAC chua mo ban (khong mua duoc).
       ⚠️ Day la chot chan cua duong (c) — mot nut dan tOi trang noi "chua mo ban"
          la mot ngo cut, te hon la khong co nut. */
    go.hidden = (!it.plan || notYet);
    el.querySelector("#lk-close").textContent = t("cta_close", L);

    lastFocus = trigger || document.activeElement;
    el.classList.add("show");
    el.setAttribute("aria-hidden", "false");
    // Tiêu điểm về nút đầu tiên đang hiện, để bàn phím dùng được ngay
    (go.hidden ? el.querySelector("#lk-close") : go).focus();
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

  /* Trang co muc `pro` goi cai nay sau khi doc GET /billing/catalog.
     Khong goi -> giu false -> khong bao gio moi mua. */
  function setSaleOpen(v) { SALE_OPEN = (v === true); }
  function saleOpen() { return SALE_OPEN; }

  window.AstroQLocks = {
    get: get, state: state, all: all,
    open: open, close: close, wire: wire,
    setSaleOpen: setSaleOpen, saleOpen: saleOpen,
    text: t, PRICING: PRICING
  };
})();
