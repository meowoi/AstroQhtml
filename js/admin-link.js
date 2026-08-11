/* ============================================================
   admin-link.js — chèn đường vào TRANG BÁO CÁO HỆ THỐNG cho tài khoản admin.

   Dùng:  <script src="js/admin-link.js"></script>
          rồi đặt một ô trống ở nơi muốn link xuất hiện:
            <div data-admin-link></div>

   Trang KHÔNG phải biết gì về admin, chỉ khai CHỖ ĐẶT. Nhãn, biểu tượng, đường dẫn
   và điều kiện hiện đều nằm ở file này — thêm trang thứ ba chỉ cần một thẻ div, và
   đổi nhãn thì sửa đúng một nơi.

   ── VÌ SAO ĐỌC `AstroQ.getUser().admin` CHỨ KHÔNG HỎI FIREBASE ──────────────
   Cờ này do `login()` đóng dấu MỘT LẦN vào hồ sơ trong máy (xem `readAdminClaim`
   ở js/firebase-auth.js). Nhờ vậy:
     · không tốn thêm lời gọi nào, không chờ `onAuthStateChanged`;
     · `select.html` — trang CỐ Ý không nạp SDK Firebase — vẫn dùng được.

   ⚠️ ĐÂY LÀ GỢI Ý GIAO DIỆN, KHÔNG PHẢI QUYỀN. Ai cũng sửa được localStorage bằng
      DevTools để cái link hiện ra; bấm vào thì `/admin/stats` trả 403 vì cổng thật
      là allowlist `ADMIN_EMAILS` ở server (Services/AdminAuth.cs). Cùng đúng nguyên
      tắc `js/route-gate.js` đã ghi: "cổng là lời dẫn đường, không phải hàng rào an
      ninh". Một cái link hiện ra không làm lộ dữ liệu nào.
   ⚠️ ĐỪNG dùng cờ này để ẩn/hiện DỮ LIỆU — chỉ để chọn đường đi.
   ============================================================ */
(function (global) {
  "use strict";

  var TXT = {
    vi: { label: "Báo cáo hệ thống", hint: "Chỉ số sức khoẻ dự án & hành vi người dùng" },
    en: { label: "System report",    hint: "Project health & user behaviour metrics" }
  };

  function isAdmin() {
    try {
      var u = global.AstroQ && AstroQ.getUser();
      return !!(u && u.admin === true);
    } catch (e) { return false; }
  }

  function mount() {
    if (!isAdmin()) return;                 // không phải admin → không chèn gì

    var lang = (global.AstroQ && AstroQ.getLang()) || "vi";
    var t = TXT[lang] || TXT.vi;
    var slots = global.document.querySelectorAll("[data-admin-link]");

    Array.prototype.forEach.call(slots, function (slot) {
      if (slot.querySelector(".admin-link")) return;   // đã chèn rồi (đổi ngôn ngữ)

      var a = global.document.createElement("a");
      a.className = "admin-link";
      a.href = "admin-report.html";

      var ic = global.document.createElement("span");
      ic.setAttribute("aria-hidden", "true");
      ic.textContent = "🛰️";
      a.appendChild(ic);

      var b = global.document.createElement("span");
      b.className = "al-b";
      var l1 = global.document.createElement("b");
      l1.textContent = t.label;
      b.appendChild(l1);
      var l2 = global.document.createElement("span");
      l2.textContent = t.hint;
      b.appendChild(l2);
      a.appendChild(b);

      var ar = global.document.createElement("span");
      ar.className = "ar";
      ar.setAttribute("aria-hidden", "true");
      ar.textContent = "›";
      a.appendChild(ar);

      slot.appendChild(a);
      slot.hidden = false;                  // ô để `hidden` sẵn nên không chiếm chỗ
    });
  }

  /* ══════════════ BÙ CỜ CHO PHIÊN CŨ ══════════════
     Cờ `admin` chỉ được `login()` đóng dấu. Nên một phiên đã đăng nhập TỪ TRƯỚC khi
     có tính năng này (hoặc trước khi được cấp quyền admin) sẽ không có cờ, và cái link
     không bao giờ hiện — trong khi cách sửa duy nhất là "đăng xuất rồi vào lại", một
     câu người dùng không có cách nào tự đoán ra.

     Nên: hồ sơ có `uid` (tức ĐANG đăng nhập) mà CHƯA TỪNG được kiểm cờ (khoá `admin`
     không tồn tại) thì hỏi lại một lần ở nền, rồi vẽ lại.

     ⚠️ Phân biệt `"admin" in u` với `u.admin`: đã kiểm và ra FALSE thì cũng là đã
        kiểm — không hỏi lại mỗi lần mở trang.
     ⚠️ CHẠY Ở NỀN, KHÔNG AI CHỜ NÓ. `refreshAdminFlag()` đi qua `onAuthStateChanged`
        và đo được là có thể không bao giờ resolve khi không có phiên — vô hại ở đây
        vì không có lần chuyển trang nào phụ thuộc nó (đúng bài học đã trả giá khi đặt
        một lời gọi như vậy vào giữa đường đăng nhập).
     ⚠️ `AstroQAuth` do một ES module gắn lên window, mà module luôn chạy SAU script
        thường — nên phải chờ nó xuất hiện. Chờ CÓ TRẦN (2 giây) để không quay vòng
        vô hạn ở những trang cố ý không nạp SDK. */
  function backfill(tries) {
    var u;
    try { u = global.AstroQ && AstroQ.getUser(); } catch (e) { return; }
    if (!u || !u.uid) return;                 // chưa đăng nhập → không có gì để hỏi
    if ("admin" in u) return;                 // đã kiểm rồi (kể cả false)

    var A = global.AstroQAuth;
    if (!A || !A.refreshAdminFlag) {
      if ((tries || 0) >= 20) return;         // 20 × 100ms = 2s rồi thôi
      global.setTimeout(function () { backfill((tries || 0) + 1); }, 100);
      return;
    }
    A.refreshAdminFlag().then(function () { mount(); }).catch(function () {});
  }

  /* Đổi ngôn ngữ thì vẽ lại nhãn. Không có hàm đăng ký sự kiện ngôn ngữ dùng chung
     nên phơi `mount` ra để trang tự gọi lại nếu cần. */
  function relabel() {
    Array.prototype.forEach.call(
      global.document.querySelectorAll("[data-admin-link] .admin-link"),
      function (a) { a.remove(); });
    mount();
  }

  function start() { mount(); backfill(0); }

  if (global.document.readyState === "loading")
    global.document.addEventListener("DOMContentLoaded", start);
  else start();

  global.AstroQAdminLink = {
    mount: mount, relabel: relabel, isAdmin: isAdmin, backfill: backfill
  };
})(window);
