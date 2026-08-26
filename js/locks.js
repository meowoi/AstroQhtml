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
      lời mời mua gì cả. Mini-game luôn thuộc nhóm này: docs/decisions/009 không xếp
      mini-game vào phần trả phí.
      ⚠️⚠️ **Nhánh này có 0 NGƯỜI DÙNG từ 26/08/2026** (mở bốn game lớp quyết định).
         Lý do giữ lại và điều kiện xoá: xem khối "Mini-game" trong bảng `ITEMS`.

   ⚠️ CÓ MỘT BIẾN THỂ THỨ TƯ ("pro nhưng CHƯA MỞ BÁN") đã dựng rồi BỎ HẲN trong
      cùng ngày 12/08/2026. Chủ dự án chốt: *"coi như nó đã mở bán rồi, làm lại thông
      báo đi — tránh việc mất công thay đổi khi mở bản thật, cũng chưa có ai vào mà."*
      Nên lời văn của thẻ `pro` là bản CHÍNH THỨC, không phải bản tạm.
      ⚠️ Bỏ HẲN chứ không để lại rồi bật cờ: giữ lại thì hôm nay nó là MÃ CHẾT, và dự
        án đã trả giá nhiều lần cho mã chết (`termsData.ts` phải sửa hai lần ·
        `AstroQRanks.ALL` ngủ 8 ngày · trường `lv` khai ở 71 file với 0 chỗ đọc).
        Cần lấy lại thì nó nằm trong lịch sử git.
      ⚠️ CHỖ KHÔNG ĐỒNG BỘ CÒN LẠI, ĐÃ BIẾT VÀ ĐÃ CHỌN: `pricing.html` và
        `/billing/catalog` vẫn nói "chưa mở bán", nên nút "Xem các gói" dẫn tới một
        trang nói chưa bán được. Mở bán thật thì sửa ở ĐÓ, không phải ở đây.

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
    /* ⚠️ Mục `"lab"` (cả KHU Phòng Nghiên Cứu bị khoá) ĐÃ BỎ 12/08/2026 — khu đó
       nay có trang thật `lab.html`, nên thẻ MOD-05 ở dashboard không còn khoá.
       Thay vào đó là khoá theo TỪNG THẺ hoạt động bên trong. Nhờ vậy dashboard
       còn 0 card khoá; `check_pages` mục [7b] đã đổi phát biểu theo.
       LAB-01 KHÔNG có mục ở đây: nó là thẻ miễn phí để trải nghiệm. */
    /* ⚠️⚠️ BỐN THẺ `lab:float` · `lab:weigh` · `lab:sky` · `lab:drops` ĐÃ BỎ KHỎI
       BẢNG NÀY 18/08/2026 — chúng nay MIỄN PHÍ (vắng mặt ở `ITEMS` = `free`).

       Vì sao: bốn thẻ đó là **toàn bộ** nội dung `pro` của cả app. Bán bốn hoạt
       động Phòng Nghiên Cứu với giá 99.000₫/tháng là một lời chào mời không đứng
       vững, và ngày mở cửa thì người đầu tiên bước vào gặp ngay bức tường ấy.
       Chủ dự án chốt 18/08/2026: mở miễn phí trước để đo người dùng thật — đo được
       rồi mới bàn chuyện thu tiền (`docs/decisions/009` mục "Điều kiện bật Pha 1"
       vẫn chưa đạt: 2/3 nhiệm vụ · 126/300 câu quiz · D30 không có gì để đo).

       ⚠️ ĐƯỜNG KẺ MỚI: **miễn phí hết Trái Đất, bức tường đặt ở Mặt Trăng.** Nên
          `mission:moon` bên dưới vẫn là `soon` — và đó là trạng thái ĐÚNG: nhiệm vụ
          đó chưa dựng, nên app đang nói thật rằng chưa có gì để bán.

       ⚠️ HỆ QUẢ: HÔM NAY **KHÔNG CÒN MỤC `pro` NÀO**, tức nhánh vẽ `pro` (nhãn
          `badge_pro`, tiêu đề `title_pro`, thân `body_pro`, `plan_*`, nút sang trang
          giá, `founder_note`) tạm thời KHÔNG có ai dùng.
          ⚠️ GIỮ LẠI CÓ CHỦ ĐÍCH, và đây là ngoại lệ CÓ ĐIỀU KIỆN với luật "đừng để
             mã chết" mà file này viện dẫn ở đầu. Khác với các ca mã chết dự án đã
             trả giá (`AstroQRanks.ALL` ngủ 8 ngày · `lv` khai ở 71 file với 0 chỗ
             đọc), nhánh này **đã chạy thật, đã có bộ đo**, và có một mốc kích hoạt
             ĐÃ ĐẶT TÊN: ngày `mission:moon` dựng xong thì nó đổi `soon` → `pro` và
             nhánh này sống lại nguyên vẹn.
             ⛔ Nếu tới lúc đó hướng đi đã đổi (không bán nữa, hoặc bán theo cách
                khác) thì **XOÁ HẲN** nhánh `pro` — đừng để nó nằm thêm một vòng nữa
                với lý do "sắp dùng tới". */
    /* ⚠️ KHOÁ LẠI THẺ MOD-05 19/08/2026 (chủ dự án chốt). `lab.html` vẫn còn trên
       đĩa; đây là mục khoá cho ĐƯỜNG VÀO ở dashboard. Ba mục `lab:*` ngay dưới là
       khoá cho từng thí nghiệm BÊN TRONG lab — hai tầng khác nhau, đừng gộp. */
    "lab": {
      state: "soon", plan: "astronaut", ic: "🔬",
      /* `nm` = tên khu, `bd` = thân bài riêng. Xem chú thích đầu bảng chữ: popup
         này dùng chung, nên lời văn riêng phải khai theo TỪNG MỤC. */
      nm: "nm_lab", bd: "bd_lab",
      feats: ["f_lab_1", "f_lab_2", "f_lab_3"]
    },
    "lab:throw": { state: "soon", plan: "astronaut", ic: "🎯" },
    "lab:tide":  { state: "soon", plan: "astronaut", ic: "🌊" },
    "lab:mix":   { state: "soon", plan: "astronaut", ic: "⚗️" },
    "mission:moon": {
      state: "soon", plan: "astronaut", ic: "🌙",
      feats: ["f_moon_1", "f_moon_2", "f_moon_3"]
    },
    /* ── Mini-game: HÔM NAY KHÔNG CÒN MỤC NÀO ──────────────────────────────
       ⚠️⚠️ BỐN GAME LỚP QUYẾT ĐỊNH ĐÃ MỞ 26/08/2026 (chủ dự án chốt) — `game:survival`
          · `game:comms` · `game:recycle` · `game:units` gỡ khỏi bảng này, và thẻ ở
          `games.html` đổi `status` về `"ready"`. Trước đó chúng bị khoá từ 19/08/2026
          trong khi **mã game đã chạy được và bộ đo đã xanh** (`play_survival` ·
          `play_comms` · `play_recycle` · `play_units`) — tức dự án có 10 game mà trẻ
          chỉ chơi được 6. Lý do mở ghi ở `docs/proposals/2026-08-26-khuon-luoi-noi-
          tram-dan-tuyen.md` mục 7 (đợt 0).
       ⚠️ KHOÁ MỘT GAME LUÔN LÀ HAI CHÂN: mục ở bảng này **và** `status:"soon"` ở
          `games.html`. Thiếu một chân thì hoặc trẻ bấm vào một trang không mở được,
          hoặc một game đã chạy được vẫn bị nói là chưa mở. `smoke_locks` mục [3] đối
          chiếu SỐ thẻ `soon` với SỐ mục `game:*` — nay cả hai bên đều là **0**.
          ⚠️⚠️ VIẾT `game:*` CHỨ KHÔNG VIẾT NGUYÊN VĂN KHOÁ CÓ DẤU NGOẶC KÉP: phép
             kiểm đếm bằng `locks_src.count(...)` trên chính file này, nên một chuỗi
             như thế **trong lời chú thích** cũng bị đếm là một mục — bảng rỗng mà
             đếm ra 1 thì phép kiểm báo hỏng oan.
       ⚠️ `game:racer` · `game:maze` · `game:catch` ĐÃ BỎ 12/08/2026 vì cùng lý do:
          giữ mục khoá cho một game đã chơi được là nói với trẻ rằng nó chưa mở.
       ⚠️⚠️ HỆ QUẢ PHẢI BIẾT: `plan: null` (*"sắp ra mắt và SẼ MIỄN PHÍ"*) nay có
          **0 NGƯỜI DÙNG** — bốn mục vừa gỡ là toàn bộ khách hàng của nhánh đó
          (`lab:*` và `mission:moon` đều `plan:"astronaut"`). Nhánh mã **giữ lại** vì
          game khoá lần sau sẽ cần đúng nó, nhưng ghi ra ở đây để không ai đọc thành
          *"đã dựng sẵn, chờ dùng"* — đúng bài học `orientation_align` của
          `docs/decisions/002` (khuôn thứ 5 có 0 người dùng mà đề bài viết là "đang
          trống", và ChatGPT tiêu nó 9 lần / 5 nhiệm vụ). */
  };

  var T = {
    vi: {
      badge_soon: "SẮP RA MẮT",
      badge_pro: "CHƯA MỞ KHOÁ",
      /* Tên khu — chỉ khai cho mục CÓ lời văn riêng. Mục không khai thì mọi câu rơi
         về bản chung, và đó là hành vi ĐÚNG (bốn thẻ game trước 26/08/2026 cố ý
         không khai). Xem chú thích ở `nm` trong bảng ITEMS. */
      nm_lab: "Phòng Nghiên Cứu",
      /* ⚠️ Câu chữ ở đây phải đọc được cho CẢ một khu (Phòng Nghiên Cứu) và một
         NHIỆM VỤ (Mặt Trăng) — cùng một bảng chữ phục vụ hai loại. Vì thế không
         gọi tên loại ("khu này" cho một nhiệm vụ là câu sai). */
      title_soon: "Đang được xây, sắp xong rồi",
      /* Bản CÓ TÊN — dùng khi mục khai `nm`. Mục không khai thì rơi về câu trên. */
      title_soon_nm: "{name} đang được hoàn thiện",
      title_pro: "Khu vực này thuộc hành trình nâng cao",

      /* ⚠️ Câu `soon` KHÔNG được hứa mở bằng tiền — nó chưa tồn tại. */
      body_soon_plan: "Bọn mình đang dựng nốt. Xong rồi thì nó nằm trong gói {plan}.",
      body_soon_free: "Bọn mình đang dựng nốt. Xong rồi thì ai cũng chơi được — không mất phí.",
      /* Thân bài riêng của Phòng Nghiên Cứu (chủ dự án gửi 19/08/2026). */
      bd_lab: "Một khu vực mới đang được xây dựng để con có thể tự khám phá các hiện tượng khoa học qua những hoạt động và thí nghiệm tương tác.",
      body_pro: "Nội dung đã có sẵn, nhưng cần gói AstroQ phù hợp để truy cập.",
      /* ⚠️⚠️ CÂU NÀY PHỤ THUỘC TRẠNG THÁI MỞ BÁN, mà `js/locks.js` KHÔNG hỏi server.
         Nó đúng vì `Billing.SALE_OPEN` mặc định ĐÓNG. Ngày bật bán thì câu này thành
         nói sai — nên `check_pages` mục [33] buộc hai bên đi cùng nhau: còn chuỗi này
         thì `SALE_OPEN` phải còn mặc định `false`. */
      body_pro_closed: "Các gói hiện chưa mở bán. Khi chính thức ra mắt, bố mẹ có thể đăng ký để mở khoá khu vực này cho con.",

      will_get: "Trong này sẽ có:",
      will_get_nm: "Trong {name} sẽ có:",
      parent_note: "Chuyện gói và giá là việc của người lớn — rủ bố mẹ xem cùng nhé.",
      founder_note: "Gia đình sở hữu Vé Sáng Lập sẽ được mở quyền sử dụng ngay khi tính năng này hoàn thành.",
      plan_note_nm: "{name} sẽ nằm trong gói {plan} khi chính thức ra mắt.",

      cta_pricing: "Xem các gói",
      cta_close: "Tiếp tục khám phá",

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
      f_lab_1: "Vì sao phi hành gia có thể lơ lửng trong không gian?",
      f_lab_2: "Cân nặng của chúng ta sẽ thay đổi thế nào trên Mặt Trăng, Sao Thuỷ hay Sao Mộc?",
      f_lab_3: "Mỗi chủ đề có phần giải thích ngắn gọn và phần Khám phá sâu hơn dành cho những bạn muốn tìm hiểu thêm.",
      f_moon_1: "Cả một nhiệm vụ dài trên Mặt Trăng",
      f_moon_2: "Mẫu vật và huy hiệu chỉ Mặt Trăng mới có",
      f_moon_3: "Mở đường bay tới hành tinh kế tiếp"
    },
    en: {
      badge_soon: "COMING SOON",
      badge_pro: "NOT UNLOCKED YET",
      nm_lab: "The Research Lab",
      title_soon: "Still being built — almost there",
      title_soon_nm: "{name} is being finished",
      title_pro: "This area is part of the advanced journey",

      body_soon_plan: "We're still putting this together. Once it lands, it comes with the {plan} plan.",
      body_soon_free: "We're still putting this together. Once it lands, everyone can play — free.",
      bd_lab: "A new area is being built where your child can explore science for themselves through hands-on, interactive experiments.",
      body_pro: "The content is ready, but it needs the right AstroQ plan to open.",
      body_pro_closed: "Plans are not on sale yet. When they open, a parent can subscribe to unlock this area.",

      will_get: "Inside you'll find:",
      will_get_nm: "{name} will include:",
      parent_note: "Plans and prices are a grown-up thing — ask a parent to look with you.",
      founder_note: "Families with the Founder Pass get access the moment this feature is finished.",
      plan_note_nm: "{name} will be part of the {plan} plan when it launches.",

      cta_pricing: "See the plans",
      cta_close: "Keep exploring",

      plan_astronaut: "Astronaut",
      plan_crew: "Crew",

      f_lab_1: "Why can astronauts float in space?",
      f_lab_2: "How would your weight change on the Moon, Mercury or Jupiter?",
      f_lab_3: "Every topic has a short explanation plus a Go deeper section for those who want more.",
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

    el.querySelector("#lk-ic").textContent = it.ic || "🔒";
    el.querySelector("#lk-badge").textContent = t(isSoon ? "badge_soon" : "badge_pro", L);
    el.querySelector("#lk-badge").className = "lk-badge" + (isSoon ? " soon" : " pro");

    /* Tên khu: chỉ mục nào KHAI `nm` mới có. Không khai thì mọi câu rơi về bản
       chung — đó là hành vi ĐÚNG, không phải chỗ còn thiếu (bốn thẻ game trước
       26/08/2026 cố ý không khai). Xem chú thích ở bảng ITEMS. */
    var areaName = it.nm ? t(it.nm, L) : "";

    var ttl = isSoon
      ? (it.nm ? t("title_soon_nm", L).replace("{name}", areaName) : t("title_soon", L))
      : t("title_pro", L);
    el.querySelector("#lk-title").textContent = ttl.replace("{plan}", planName);

    /* ⚠️ Trạng thái `pro` gồm HAI câu: cái gì đang bị khoá, và vì sao chưa mở được
       ngay hôm nay. Nhập chúng thành một chuỗi thì ngày bật bán phải sửa cả câu đầu;
       tách ra thì chỉ cần bỏ câu thứ hai. */
    var body = !it.plan ? t("body_soon_free", L)
             : isSoon   ? (it.bd ? t(it.bd, L) : t("body_soon_plan", L))
             :            t("body_pro", L) + " " + t("body_pro_closed", L);
    el.querySelector("#lk-body").textContent = body.replace("{plan}", planName);

    // Danh sách quyền lợi — chỉ khi có gói VÀ có khai `feats`
    var wrap = el.querySelector("#lk-feats");
    if (it.plan && it.feats && it.feats.length) {
      el.querySelector("#lk-feats-h").textContent = it.nm
        ? t("will_get_nm", L).replace("{name}", areaName)
        : t("will_get", L);
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
      /* Mục CÓ tên thì nói rõ nó thuộc gói nào; mục không tên giữ câu chung về
         "chuyện gói giá là việc người lớn". */
      note.textContent = it.nm
        ? t("plan_note_nm", L).replace("{name}", areaName).replace("{plan}", planName) +
          (isSoon ? " " + t("founder_note", L) : "")
        : (isSoon ? t("founder_note", L) + " " : "") + t("parent_note", L);
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

  window.AstroQLocks = {
    get: get, state: state, all: all,
    open: open, close: close, wire: wire,
    text: t, PRICING: PRICING
  };
})();
