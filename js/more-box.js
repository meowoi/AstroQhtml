/* ============================================================
   js/more-box.js — KHỐI "MỞ RỘNG" trong trình đọc bài.

   Một bài đọc có hai tầng: thân bài (ai cũng đọc được) và `more` — phần đào
   sâu hơn cho trẻ muốn đi tiếp. Module này lo phần thứ hai, cho CẢ HAI trình
   đọc (`library.html` và `learn.html`).

   ⚠️ VÌ SAO LÀ MODULE DÙNG CHUNG CHỨ KHÔNG PHẢI 25 DÒNG CHÉP HAI LẦN:
      hai trình đọc đó đã có tiền lệ xấu — trước 09/08/2026 chúng giữ HAI mảng
      `ARTICLES` riêng, trùng chủ đề, và sửa nội dung phải sửa hai nơi. Khối này
      mang cả bậc độ sâu, trạng thái gấp/mở, nhãn song ngữ và việc vẽ lại khi đổi
      ngôn ngữ — bốn thứ, đúng loại sẽ trôi khỏi nhau sau vài lần sửa. Cùng khuôn
      `js/weeklog.js` và `js/daily.js`: module tự mang chuỗi của mình.

   ⚠️⚠️ BẬC ĐỘ SÂU CHỈ QUYẾT CÁI MẶC ĐỊNH, KHÔNG KHOÁ GÌ — luật đã chốt ở
      `js/depth.js` ngày 12/08/2026 và nhắc lại ở đây vì đây là người dùng THỨ HAI
      của nó (trước chỉ có `lab.html`):
        · `senior` (11+) → phần Mở rộng MỞ SẴN
        · `junior` (8–10) → GẤP LẠI
        · **nút bấm LUÔN CÓ Ở CẢ HAI BẬC** — máy đoán sai tuổi thì trẻ sửa bằng
          một cú bấm. Ẩn hẳn nút ở một bậc là máy chốt hộ trẻ, đúng thứ cơ chế
          này sinh ra để tránh.
      Chưa khai bậc → `AstroQDepth.get()` tự lùi về `junior` (fail-safe: thà nói
      đơn giản với một đứa 15 tuổi hơn nói khó với một đứa 8 tuổi).

   ⚠️ KHÔNG CÓ MODULE `js/depth.js` THÌ VẪN CHẠY — coi như `junior`. Trang đọc
      không được vỡ chỉ vì thiếu một file phụ.

   Dùng:
     AstroQMore.mount(hostEl, article, lang)   // article.more = {vi:[…], en:[…]}
     AstroQMore.setLang(lang)                  // vẽ lại nhãn khi đổi VI/EN
   ============================================================ */
(function (global) {
  "use strict";

  var TXT = {
    vi: {
      h: "Mở rộng",
      open: "Tìm hiểu thêm",
      close: "Thu gọn",
      note: "Phần này dành cho bạn nào muốn đi sâu hơn."
    },
    en: {
      h: "Go deeper",
      open: "Learn more",
      close: "Show less",
      note: "This part is for anyone who wants to dig deeper."
    }
  };

  function L(l) { return l === "en" ? "en" : "vi"; }
  function tx(l, k) { return TXT[L(l)][k]; }

  /* Thoát chuỗi trước khi vào innerHTML. Thân bài của dự án CÓ chứa thẻ `<b>` do
     người viết đặt (xem `term.text`), nhưng phần `more` thì KHÔNG được phép — nó
     là văn xuôi thuần. Thoát hết là chốt chặn rẻ nhất cho điều đó. */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  var host = null, open = false, lang = "vi";

  function senior() {
    try { return !!(global.AstroQDepth && global.AstroQDepth.isSenior()); }
    catch (e) { return false; }
  }

  function paint() {
    if (!host || host.hidden) return;
    var btn = host.querySelector(".mb-btn");
    var box = host.querySelector(".mb-body");
    if (!btn || !box) return;
    btn.textContent = tx(lang, open ? "close" : "open") + (open ? " ↑" : " ↓");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    /* ⚠️ `hidden` KHÔNG đủ một mình: `.mb-body` khai `display` trong CSS, mà
       `display` của tác giả THẮNG `display:none` mà trình duyệt áp cho `[hidden]`.
       Dự án đã trả giá bẫy này chín lần (`#time-ok` · `.lk-btn` · `.pt-empty` ·
       `.co-steps` · `#wl-done` · `.exp-ctl` · `.brag` · `.deskrow` · `.sess`);
       `css/page-shell.css` vì thế khai lại `.mb-body[hidden]{display:none}`. */
    box.hidden = !open;
    host.querySelector(".mb-h").textContent = tx(lang, "h");
    var note = host.querySelector(".mb-note");
    if (note) note.textContent = tx(lang, "note");
  }

  /** Gắn khối Mở rộng vào `el`. Bài không có `more` thì ẩn hẳn — một tiêu đề
      "Mở rộng" trống đọc ra như chỗ bị lỗi. */
  function mount(el, art, l) {
    host = el;
    if (!host) return;
    lang = L(l);
    var list = art && art.more && (art.more[lang] || art.more.vi);
    if (!list || !list.length) { host.hidden = true; host.innerHTML = ""; return; }

    /* Mặc định theo bậc — nhưng đây CHỈ là mặc định, nút vẫn có ở cả hai bậc. */
    open = senior();
    host.hidden = false;
    host.innerHTML =
      '<div class="mb-top">' +
        '<h3 class="mb-h"></h3>' +
        '<button type="button" class="mb-btn" aria-expanded="false"></button>' +
      "</div>" +
      '<div class="mb-body">' +
        list.map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("") +
        '<p class="mb-note"></p>' +
      "</div>";

    host.querySelector(".mb-btn").addEventListener("click", function () {
      open = !open;
      paint();
    });
    paint();
  }

  function setLang(l) { lang = L(l); paint(); }

  /** Đóng lại khi trình đọc đóng — mở bài kế tiếp phải bắt đầu từ mặc định của
      bậc, không thừa hưởng trạng thái của bài trước. */
  function reset() { host = null; open = false; }

  global.AstroQMore = { mount: mount, setLang: setLang, reset: reset, t: tx };
})(window);
