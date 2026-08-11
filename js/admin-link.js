/* ============================================================
   admin-link.js — chèn đường vào TRANG BÁO CÁO HỆ THỐNG cho tài khoản admin.

   Dùng:  <script src="js/admin-link.js"></script>
          rồi đặt một ô trống ở nơi muốn link xuất hiện:
            <div data-admin-link hidden></div>

   Trang KHÔNG phải biết gì về admin, chỉ khai CHỖ ĐẶT. Nhãn, biểu tượng, đường dẫn
   và điều kiện hiện đều nằm ở file này — thêm trang thứ ba chỉ cần một thẻ div, và
   đổi nhãn thì sửa đúng một nơi.

   ══════════════ LUẬT QUAN TRỌNG NHẤT CỦA FILE NÀY ══════════════
   **CHỈ HIỆN SAU KHI XÁC MINH CLAIM TỪ ID TOKEN. KHÔNG BAO GIỜ HIỆN THEO
   `localStorage`.**

   Bản đầu đọc `AstroQ.getUser().admin` cho nhanh (cờ do `login()` đóng dấu). Nhưng hồ
   sơ trong máy là dữ liệu ai cũng sửa được bằng DevTools, nên một tài khoản THƯỜNG chỉ
   cần đổi một dòng JSON là mục quản trị hiện ra. Bấm vào thì server trả 403 — cổng thật
   là allowlist `ADMIN_EMAILS` (Services/AdminAuth.cs) — nên KHÔNG lộ dữ liệu nào. Nhưng
   yêu cầu là "chỉ tài khoản được cấp phép mới thấy mục này", và một lời hứa phá được
   bằng cách sửa một dòng JSON thì không phải lời hứa.

   Claim `admin` nằm trong JWT do Google ký và SDK tự đối chiếu, nên `AstroQAuth
   .verifyAdmin()` là câu trả lời không giả được bằng localStorage. Nó đọc token ĐÃ
   CACHE (không gọi mạng) nên gần như miễn phí.

   ⚠️ HỆ QUẢ CÓ Ý THỨC: link xuất hiện CHẬM một nhịp sau khi trang tải, vì phải chờ
      SDK và phiên. Đánh đổi đúng: thà chậm một nhịp còn hơn hiện cho người không được
      phép. Không có phiên / hết hạn chờ → không hiện gì.
   ⚠️ CỜ TRONG HỒ SƠ MÁY VẪN CÒN GIÁ TRỊ, nhưng cho việc KHÁC: `select.html` cố ý không
      nạp SDK Firebase (64 KB gzip trên đúng đường onboarding của trẻ) nên `auth-flow.js`
      đọc cờ đó để biết có bỏ màn giới thiệu hay không. Sửa cờ đó thì chỉ bỏ được màn
      giới thiệu của CHÍNH MÌNH — không phải thứ cần bảo vệ.
   ============================================================ */
(function (global) {
  "use strict";

  var TXT = {
    vi: { label: "Báo cáo hệ thống", hint: "Chỉ số sức khoẻ dự án & hành vi người dùng" },
    en: { label: "System report",    hint: "Project health & user behaviour metrics" }
  };

  /* Kết quả xác minh. `null` = CHƯA biết (chưa xác minh xong) — khác hẳn `false`
     (đã xác minh, không phải admin). Chưa biết thì KHÔNG vẽ gì. */
  var verified = null;

  /* Chờ SDK: `AstroQAuth` do một ES module gắn lên window, mà module luôn chạy SAU
     script thường. Chờ CÓ TRẦN để không quay vòng vô hạn ở trang không nạp SDK. */
  var WAIT_TRIES = 25, WAIT_MS = 100;      // 25 × 100ms = 2,5 giây

  function draw() {
    if (verified !== true) return;          // chỉ vẽ khi ĐÃ xác minh là admin

    var lang = (global.AstroQ && AstroQ.getLang()) || "vi";
    var t = TXT[lang] || TXT.vi;

    Array.prototype.forEach.call(
      global.document.querySelectorAll("[data-admin-link]"),
      function (slot) {
        if (slot.querySelector(".admin-link")) return;    // đã vẽ rồi

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
        slot.hidden = false;                // ô để `hidden` sẵn nên không chiếm chỗ
      });
  }

  /* Gỡ link đã vẽ — dùng khi xác minh ra KHÔNG phải admin, hoặc khi đổi ngôn ngữ. */
  function clear() {
    Array.prototype.forEach.call(
      global.document.querySelectorAll("[data-admin-link]"),
      function (slot) {
        var a = slot.querySelector(".admin-link");
        if (a) a.remove();
        slot.hidden = true;
      });
  }

  /**
   * Xác minh rồi vẽ. `force` = buộc lấy token mới, dùng khi quyền vừa được cấp mà
   * người dùng chưa đăng nhập lại (token sống ~1 giờ).
   *
   * ⚠️ CHẠY Ở NỀN, KHÔNG AI CHỜ NÓ. `verifyAdmin()` đi qua `onAuthStateChanged` và đo
   *    được là có thể không bao giờ resolve khi không có phiên — vô hại ở đây vì không
   *    có lần chuyển trang nào phụ thuộc nó (đúng bài học đã trả giá khi đặt một lời
   *    gọi như vậy vào giữa đường đăng nhập).
   */
  function check(force, tries) {
    var A = global.AstroQAuth;
    if (!A || !A.verifyAdmin) {
      if ((tries || 0) >= WAIT_TRIES) return;      // trang không có SDK → thôi
      global.setTimeout(function () { check(force, (tries || 0) + 1); }, WAIT_MS);
      return;
    }
    A.verifyAdmin(force).then(function (ok) {
      verified = !!ok;
      if (verified) draw(); else clear();
    }).catch(function () { /* hỏng thì coi như không phải admin: không vẽ gì */ });
  }

  if (global.document.readyState === "loading")
    global.document.addEventListener("DOMContentLoaded", function () { check(false, 0); });
  else check(false, 0);

  global.AstroQAdminLink = {
    /** Vẽ lại nhãn sau khi đổi ngôn ngữ. KHÔNG xác minh lại (đã xác minh rồi). */
    relabel: function () { clear(); draw(); },
    /** Xác minh lại, buộc lấy token mới. Dùng khi vừa được cấp quyền admin. */
    recheck: function () { check(true, 0); },
    /** true | false | null (chưa xác minh xong). */
    state: function () { return verified; }
  };
})(window);
