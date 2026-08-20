/* ============================================================================
   js/pw-toggle.js — NÚT ẨN/HIỆN MẬT KHẨU (dùng chung mọi trang)

   Vì sao có: người dùng gõ mật khẩu vào một ô toàn dấu tròn, bấm Đăng nhập, rồi
   nhận đúng một câu "sai email hoặc mật khẩu" — không có cách nào biết mình gõ
   sai, bật CapsLock, hay để sót một ký tự. Cho họ TỰ NHÌN là cách rẻ nhất để
   loại bỏ phần lớn số ca "đăng nhập không được", và nó không làm yếu đi thứ gì:
   mật khẩu vẫn chỉ hiện trên máy của chính họ, do chính họ bấm.

   Cách dùng — KHÔNG cần gọi hàm nào, chỉ cần markup (nạp file này là xong):
     <div class="pw-wrap">
       <input id="login-pass" type="password" ... />
       <button type="button" class="pw-eye" data-pw-toggle="login-pass" aria-pressed="false">
         <svg class="pw-ic-on"  …>…</svg>
         <svg class="pw-ic-off" …>…</svg>
         <span class="pw-lbl pw-lbl-show" data-i18n="auth_pw_show">Hiện mật khẩu</span>
         <span class="pw-lbl pw-lbl-hide" data-i18n="auth_pw_hide">Ẩn mật khẩu</span>
       </button>
     </div>
   Kiểu dáng ở `css/common.css`, mục "NÚT ẨN/HIỆN MẬT KHẨU".

   ⚠️ KHÔNG có `aria-label` và file này KHÔNG chứa chuỗi tiếng Việt/Anh nào. Tên
      trợ năng của nút là CHỮ BÊN TRONG nó, và hai nhãn đó do từ điển của trang
      dịch qua `data-i18n` (`applyTexts` của `js/ui-common.js`) — CSS chọn nhãn
      nào đang có hiệu lực theo `aria-pressed`. Cách khác là ghi `aria-label`
      trong JS, và như vậy là dựng bản sao thứ hai của một chuỗi đã có trong từ
      điển; bản sao đó sẽ không đổi khi người dùng bấm VI/EN. Cùng phân công như
      `js/route-gate.js`: file dùng chung giữ HÀNH VI, trang giữ CHỮ.

   ⚠️ BẮT SỰ KIỆN Ở `document`, không gắn vào từng nút lúc nạp. Hai ô mật khẩu ở
      `landing-app.html` nằm trong lớp phủ có pane `hidden`, và trang sau có thể
      dựng biểu mẫu bằng JS. Gắn một lần lúc nạp là bỏ sót mọi nút sinh ra sau —
      đúng loại lỗi im lặng chỉ khách gặp.

   ⚠️ `type="button"` là BẮT BUỘC ở markup. Thiếu nó thì trong <form> đây là nút
      submit, và bấm "xem mật khẩu" hoá ra gửi luôn biểu mẫu. `preventDefault`
      dưới đây là lớp chắn thứ hai, không phải lý do để bỏ thuộc tính.

   ⚠️ KHÔNG BAO GIỜ tự đưa ô về `password` sau một khoảng thời gian. Đây là lựa
      chọn của người dùng; ô tự đổi lại giữa lúc đang gõ là vừa vô lý vừa dễ làm
      mất chữ. Muốn dọn thì gọi `AstroQPwToggle.reset(root)` lúc ĐÓNG lớp phủ.

   ⚠️ GIỮ NGUYÊN VỊ TRÍ CON TRỎ. Đổi `type` làm nhiều trình duyệt nhảy con trỏ về
      cuối chuỗi; ai đang sửa ký tự thứ 3 sẽ gõ tiếp vào cuối mà không hiểu vì sao.
   ============================================================================ */
(function (global) {
  "use strict";

  function fieldOf(btn) {
    var id = btn.getAttribute("data-pw-toggle");
    if (id) {
      var byId = document.getElementById(id);
      if (byId) return byId;
    }
    /* Dự phòng: lấy ô nhập cùng bọc. Có ích cho biểu mẫu dựng động, nhưng khai
       id vẫn là cách nên dùng — nó cũng là tài liệu cho người đọc markup. */
    var wrap = btn.closest(".pw-wrap");
    return wrap ? wrap.querySelector("input") : null;
  }

  /* Đặt trạng thái cho MỘT nút. `show` = true là để mật khẩu đọc được.
     ⚠️ BẤT BIẾN THEO SỐ LẦN GỌI: `reset()` gọi hàm này cho cả những nút đang ở
        đúng trạng thái rồi, nên nó phải cho ra một kết quả, không lật qua lại. */
  function paint(btn, show) {
    var f = fieldOf(btn);
    if (!f) return;

    var want = show ? "text" : "password";
    if (f.type !== want) {
      var s = f.selectionStart, e = f.selectionEnd,
          focused = document.activeElement === f;
      f.type = want;
      /* Chỉ đặt lại khi ô ĐANG được focus — nếu không thì việc bấm nút sẽ tự kéo
         con trỏ vào một ô người ta chưa gõ tới. `setSelectionRange` ném lỗi trên
         vài kiểu input nên bọc try. */
      if (focused && s !== null) { try { f.setSelectionRange(s, e); } catch (err) {} }
    }
    btn.setAttribute("aria-pressed", show ? "true" : "false");
  }

  document.addEventListener("click", function (ev) {
    var t = ev.target;
    var btn = t && t.closest ? t.closest("[data-pw-toggle]") : null;
    if (!btn) return;
    ev.preventDefault();
    paint(btn, btn.getAttribute("aria-pressed") !== "true");
  });

  /* Đưa mọi ô trong `root` (mặc định cả trang) về trạng thái ẩn. Gọi khi ĐÓNG lớp
     phủ đăng nhập: mở lại mà mật khẩu vẫn hiện nguyên là để mật khẩu người trước
     nằm trên màn hình cho người sau đọc — máy tính chung trong nhà, phòng máy
     trường học, đúng nhóm người dùng của trang này. */
  function reset(root) {
    var list = (root || document).querySelectorAll("[data-pw-toggle]");
    Array.prototype.forEach.call(list, function (b) { paint(b, false); });
  }

  global.AstroQPwToggle = { reset: reset };
})(window);
