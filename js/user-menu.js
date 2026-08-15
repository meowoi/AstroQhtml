/* ============================================================
   user-menu.js — MENU THẢ (dropdown) dùng chung: menu avatar + bộ chọn ngôn ngữ.

   Dùng:
     <script src="js/user-menu.js"></script>
     … markup có `data-menu` / `data-menu-btn` / `data-menu-pop` …
     AstroQUserMenu.init({ onSoon: function(l){ … } });   // gọi SAU khi DOM xong

   ⚠️ PHẢI GỌI `init()` TRƯỚC `AstroQ.initLang(applyLang)`. `initLang` gắn sự kiện
      cho `.lang-switch button` MỘT LẦN lúc chạy; danh sách ngôn ngữ do file này
      dựng ra, nên dựng sau là các nút đó **không có ai nghe** — bấm không ăn, và
      im lặng tuyệt đối. Dashboard gọi đúng thứ tự đó ở cuối script trang.

   ══════════════ VÌ SAO CÓ FILE NÀY ══════════════
   Trung Tâm Điều Hướng là màn hình đầu tiên trẻ nhìn thấy. Trước 15/08/2026 nó
   xếp 6 đường vào "xem lại mình" (hồ sơ · thành tích · mẫu vật · kho trang trí ·
   bảng bố mẹ · báo cáo hệ thống) + nút đăng xuất **ở NỬA TRÊN trang**, đẩy 6 thẻ
   khu vực chơi/học xuống dưới: đo được trên điện thoại 390×844 thì thẻ khu vực
   đầu tiên nằm ở **y = 1269px**, tức trẻ phải kéo 465px mới thấy thứ nó vào đây
   để làm. Gom cả cụm đó vào một menu sau ảnh đại diện là khuôn quen thuộc của
   game/app cho trẻ (Duolingo · Prodigy · Roblox đều đặt hồ sơ + cài đặt + khu
   phụ huynh sau avatar), và nó trả lại nửa trên màn hình cho việc chơi.

   ⚠️ HÀNH VI ở đây, NỘI DUNG ở trang. File này không giữ một chuỗi tiếng Việt nào
      của menu avatar — trang khai `data-i18n` như mọi chỗ khác. Ngoại lệ DUY NHẤT
      là **tên ngôn ngữ**: chúng viết bằng chính tiếng đó (endonym) nên không dịch,
      và giữ một bảng ở đây là để thêm ngôn ngữ chỉ phải sửa MỘT chỗ.
   ============================================================ */
(function (global) {
  "use strict";

  var doc = global.document;

  /* ------------------------------------------------------------
     BẢNG NGÔN NGỮ — CHỖ DUY NHẤT KHAI.

     `ready:true` = ĐÃ có nội dung, chọn được ngay. Không có cờ = đang dịch.

     ⚠️ ĐỪNG bật `ready` chỉ bằng cách sửa dòng ở đây. Một ngôn ngữ chỉ thật sự
        dùng được khi làm đủ BA việc: ① thêm từ điển cho ngôn ngữ đó ở TỪNG trang
        (mỗi trang một `I18N`); ② nới `getLang`/`setLang`/`setDocLang` ở
        `js/ui-common.js` — hôm nay chúng chỉ nhận đúng "vi"/"en" nên mọi giá trị
        khác bị bỏ qua và trang lặng lẽ quay về tiếng Việt; ③ mới bật `ready`.
        Bật trước hai bước kia là trẻ chọn một thứ không xảy ra gì cả.
     ⚠️ KHÔNG dùng emoji cờ. Windows không có glyph cờ quốc gia nên `🇯🇵` hiện ra
        thành hai chữ "JP" — tức là một biểu tượng mà nửa số máy đọc ra thứ khác.
        Chip hai chữ cái thì mọi máy vẽ giống nhau, và nó cũng là thứ trẻ thấy
        trên nút thu gọn nên hai chỗ khớp nhau.
     ------------------------------------------------------------ */
  var LANGS = [
    { code: "vi", name: "Tiếng Việt", ready: true },
    { code: "en", name: "English",    ready: true },
    { code: "zh", name: "中文" },
    { code: "ja", name: "日本語" },
    { code: "ko", name: "한국어" },
    { code: "es", name: "Español" },
    { code: "fr", name: "Français" },
    { code: "th", name: "ไทย" }
  ];

  var opts = {};
  var openRoot = null;      // menu đang mở (chỉ một tại một thời điểm)

  function el(tag, cls) {
    var e = doc.createElement(tag);
    if (cls) e.className = cls;
    return e;
  }

  /* ---------------- Đóng / mở ----------------

     ⚠️⚠️ KHÔNG CÓ LỚP PHỦ (veil), VÀ TẤM THẢ KHÔNG DÙNG `position:fixed`. Bản đầu
     làm cả hai và cả hai đều HỎNG — chỉ render thật mới thấy, đọc CSS thì không:
       ① `.statusbar` của dashboard khai `backdrop-filter:blur(14px)`, mà một
          ancestor có `filter`/`backdrop-filter`/`transform` thì nó trở thành KHỐI
          CHỨA của mọi con `position:fixed`. Nên "tấm trượt neo đáy màn hình"
          (`position:fixed;bottom:0`) thật ra neo vào ĐÁY CỦA HEADER — đo được nó
          hiện ra ở mép trên màn 390px, cắt cụt, chỉ thấy ba ngôn ngữ cuối.
       ② Cùng lý do đó, header tự tạo một stacking context ở `z-index:30`, nên
          KHÔNG con nào của nó vượt lên trên được một lớp phủ `z-index:70` gắn ở
          `<body>` — lớp phủ tối đè lên chính cái menu nó phục vụ.
     ⇒ Tấm thả nay là dropdown `position:absolute` neo theo nút (ở màn hẹp thì trải
       gần hết bề rộng), và cú bấm ra ngoài bắt bằng một listener ở `document`.
       Muốn quay lại kiểu tấm trượt thì phải chuyển hẳn nút DOM sang `<body>` lúc
       mở — đừng chỉ đổi CSS, hai cái bẫy trên sẽ quay lại y nguyên. */

  function popOf(root) { return root.querySelector("[data-menu-pop]"); }
  function btnOf(root) { return root.querySelector("[data-menu-btn]"); }

  function open(root) {
    if (openRoot && openRoot !== root) closeAll(true);
    var pop = popOf(root), btn = btnOf(root);
    if (!pop || !btn) return;
    pop.hidden = false;
    root.classList.add("um-on");
    btn.setAttribute("aria-expanded", "true");
    fit(root, pop);
    openRoot = root;
  }

  /* Kéo tấm thả vào trong khung nhìn nếu nó thò ra ngoài.
     ⚠️ ĐÂY LÀ MỘT LỖI ĐO ĐƯỢC, không phải phòng xa: tấm thả neo mép PHẢI của nút,
        mà ở màn 390px nó rộng gần hết bề rộng — với nút Ngôn ngữ (không nằm sát mép
        phải, vì còn nút avatar bên cạnh) thì mép trái rơi ra **x = −78px** và hai
        chữ đầu của mọi dòng bị cắt cụt. CSS thuần không diễn đạt được "rộng hết
        mức nhưng đừng ra khỏi màn": bề rộng khả dụng phụ thuộc chỗ đứng của nút.
     ⚠️ Dịch bằng `left`, KHÔNG bằng `transform`: `transform` vừa đá nhau với
        animation `umDrop`, vừa biến tấm thả thành khối chứa cho con `fixed`. */
  function fit(root, pop) {
    pop.style.left = "";
    pop.style.right = "";
    var pad = 8, host = root.getBoundingClientRect(), r = pop.getBoundingClientRect();
    if (r.left < pad) {
      pop.style.right = "auto";
      pop.style.left = (pad - host.left) + "px";
    } else if (r.right > global.innerWidth - pad) {
      pop.style.right = "auto";
      pop.style.left = (global.innerWidth - pad - r.width - host.left) + "px";
    }
  }

  /** `keepFocus` = đóng vì mở cái khác, đừng cướp tiêu điểm về nút cũ. */
  function closeAll(keepFocus) {
    if (!openRoot) return;
    var root = openRoot, pop = popOf(root), btn = btnOf(root);
    openRoot = null;
    if (pop) pop.hidden = true;
    root.classList.remove("um-on");
    if (btn) {
      btn.setAttribute("aria-expanded", "false");
      /* Trả tiêu điểm về đúng nút vừa bấm — không trả thì người dùng bàn phím rơi
         về `<body>` và phải Tab lại từ đầu trang. */
      if (!keepFocus && pop && pop.contains(doc.activeElement)) btn.focus();
    }
  }

  /* Đi giữa các mục bằng ↑ ↓ — menu của trẻ thường dài hơn màn hình, và bàn phím
     là đường duy nhất cho người không dùng được chuột. */
  function items(pop) {
    return Array.prototype.filter.call(
      pop.querySelectorAll("a,button"),
      function (n) { return !n.disabled && n.offsetParent !== null; });
  }
  function move(pop, delta) {
    var list = items(pop);
    if (!list.length) return;
    var i = list.indexOf(doc.activeElement);
    i = i < 0 ? (delta > 0 ? 0 : list.length - 1) : (i + delta + list.length) % list.length;
    list[i].focus();
  }

  function wire(root) {
    if (root.getAttribute("data-menu-wired")) return;
    root.setAttribute("data-menu-wired", "1");
    var btn = btnOf(root), pop = popOf(root);
    if (!btn || !pop) return;

    btn.setAttribute("aria-expanded", "false");
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      if (openRoot === root) closeAll(); else { open(root); }
    });
    btn.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        open(root);
        move(pop, e.key === "ArrowDown" ? 1 : -1);
      }
    });
    pop.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(pop, 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(pop, -1); }
    });
    /* Chọn xong thì đóng — trừ nút "ngôn ngữ chưa có", nó tự lo lời nhắn rồi giữ
       menu mở để trẻ chọn tiếp thứ khác. */
    pop.addEventListener("click", function (e) {
      var n = e.target.closest ? e.target.closest("a,button") : null;
      if (!n || n.hasAttribute("data-lang-soon")) return;
      closeAll(true);
    });
  }

  /* ---------------- Bộ chọn ngôn ngữ ---------------- */

  function chip(code) {
    var c = el("span", "um-code");
    c.textContent = code.toUpperCase();
    return c;
  }

  function buildLangs() {
    var ready = doc.querySelector("[data-lang-list]");
    var soon = doc.querySelector("[data-lang-soon-list]");
    if (!ready && !soon) return;

    LANGS.forEach(function (l) {
      var b = el("button", "um-item" + (l.ready ? "" : " um-soon"));
      b.type = "button";
      if (l.ready) b.setAttribute("data-lang", l.code);
      else b.setAttribute("data-lang-soon", l.code);
      b.appendChild(chip(l.code));

      var nm = el("span", "um-nm");
      nm.textContent = l.name;
      b.appendChild(nm);

      if (l.ready) {
        /* Dấu tích của mục đang chọn. `markLangButtons` chỉ gắn class `.active`,
           nên phần hiện ra là việc của CSS — dấu này luôn nằm trong DOM. */
        var tk = el("span", "um-tick");
        tk.setAttribute("aria-hidden", "true");
        tk.textContent = "✓";
        b.appendChild(tk);
        if (ready) ready.appendChild(b);
      } else {
        /* Nhãn "sắp có": chữ do TRANG khai (`data-i18n`), file này chỉ đặt chỗ. */
        var tg = el("span", "um-tag");
        tg.setAttribute("data-i18n", "lang_soon_tag");
        tg.textContent = "…";
        b.appendChild(tg);
        b.addEventListener("click", function () {
          if (typeof opts.onSoon === "function") opts.onSoon({ code: l.code, name: l.name });
        });
        if (soon) soon.appendChild(b);
      }
    });
  }

  /* Nút thu gọn hiện MÃ ngôn ngữ đang dùng. Móc vào `AstroQ.onLang` nên đổi ngôn
     ngữ ở tab khác cũng cập nhật theo. */
  function paintTrigger(lang) {
    var code = doc.querySelector("[data-lang-code]");
    if (code) code.textContent = String(lang || "vi").toUpperCase();
  }

  /* ---------------- Khởi tạo ---------------- */

  function init(o) {
    opts = o || {};
    buildLangs();
    Array.prototype.forEach.call(doc.querySelectorAll("[data-menu]"), wire);

    if (global.AstroQ && AstroQ.onLang) AstroQ.onLang(paintTrigger);
    paintTrigger(global.AstroQ ? AstroQ.getLang() : "vi");

    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && openRoot) closeAll();
    });
    /* Bấm ra ngoài thì đóng. Nghe ở pha BẮT (capture) để cú bấm vẫn tới đích của
       nó — người dùng bấm thẳng vào một nút khác trên trang thì nút đó phải chạy,
       menu chỉ đóng theo.
       ⚠️ Dùng `pointerdown` chứ không `click`: trên máy cảm ứng, `click` tới sau
          ~300ms và trong khoảng đó menu vẫn che mất chỗ trẻ vừa chạm. */
    doc.addEventListener("pointerdown", function (e) {
      if (!openRoot) return;
      if (!openRoot.contains(e.target)) closeAll(true);
    }, true);
  }

  global.AstroQUserMenu = {
    init: init,
    open: open,
    close: function () { closeAll(); },
    isOpen: function () { return !!openRoot; },
    /** Bản sao danh sách ngôn ngữ — cho phép kiểm đọc, không cho sửa tại chỗ. */
    langs: function () { return LANGS.map(function (l) { return { code: l.code, name: l.name, ready: !!l.ready }; }); }
  };
})(window);
