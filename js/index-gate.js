/* ============================================================================
   js/index-gate.js — ĐẨY NGƯỜI ĐÃ ĐĂNG NHẬP TỪ TRANG CHỦ SANG CỬA VÀO APP.

   Chỉ dùng ở TRANG CHỦ (`index.html` và bản sinh ra `en/index.html`).

   ⚠️⚠️ VÌ SAO KHÔNG CHUYỂN HƯỚNG CẢ `/`:
      `/` là URL **duy nhất được lập chỉ mục** ở gốc — 36/37 trang .html trong
      thư mục này là `noindex`. Riêng nó mang `canonical`, ba thẻ `hreflang`
      (vi/en/x-default), hai khối JSON-LD (`EducationalApplication` + `FAQPage`),
      khối AEO "astroQ.org là gì?" và là mục đầu của `sitemap.xml`. Đích đến
      `landing-app.html` thì `noindex,follow` — CÓ CHỦ Ý, quyết định lại ngày
      18/08/2026 (lý do đầy đủ ở đầu file đó). Chuyển hướng cả `/` sang một trang
      `noindex` là bảo Google gỡ astroq.org khỏi kết quả tìm kiếm, và giết luôn
      form waitlist đang thu lead.

      Nên cổng này hỏi đúng MỘT câu: *"người này đã có phiên chưa?"*. Khách lạ và
      crawler không bao giờ chạm vào nhánh đẩy — họ vẫn thấy nguyên trang tiếp thị.

   ⚠️ ĐẶT SAU `js/utm.js` TRONG <head>. Sau vì `utm.js` phải kịp ghi "người này
      đến từ đâu" TRƯỚC khi ta rời trang — đẩy sớm hơn là mất dấu chiến dịch của
      đúng nhóm khách đến từ link fanpage. Trong <head> vì đẩy sau khi <body> đã
      vẽ thì người dùng thấy trang chủ nháy lên rồi mới nhảy.

   ⚠️ KHÔNG tự quyết "người này nên vào dashboard hay select". `landing-app.html`
      đã giữ luật đó (biến `authed` của nó, khoảng dòng 500). Chép điều kiện sang
      đây là hai nơi cùng giữ một luật, và bản ở đây sẽ nói cái cũ vào đúng ngày
      luật kia đổi — đúng loại lỗi dự án đã trả giá nhiều lần (xem `js/badges.js`,
      `js/route-gate.js`, `js/mission-catalog.js`). Cổng này chỉ đưa người tới cửa.
   ============================================================================ */
(function () {
  "use strict";

  try {
    /* ---- 1. Phải là PHIÊN THẬT ---------------------------------------------
       `uid` do Firebase cấp. Hồ sơ thời demo (`js/firebase-auth-ui.js`:
       `demoLogin`/`demoRegister`) ghi `astroq-user` KHÔNG có `uid` — chỉ cần
       localStorage còn sót là đã đẩy người chưa đăng nhập vào cửa app. Cùng phép
       thử mà `landing-app.html` dùng cho biến `authed`. */
    if (!window.AstroQ || !AstroQ.getUser) return;    // ui-common.js chưa nạp
    var u = AstroQ.getUser();
    if (!u || !u.uid) return;

    /* ---- 2. Có neo `#` = người đến để đọc một mục cụ thể --------------------
       `#waitlist`, `#what-is`, `#faq`… đều là link người khác gửi cho nhau. Đẩy
       họ đi là nuốt mất đúng thứ họ được mời tới xem. */
    if (location.hash) return;

    /* ---- 3. Cửa thoát thủ công: `?stay` ------------------------------------ */
    if (/[?&]stay(?:[=&]|$)/.test(location.search)) return;

    /* ---- 4. Đến từ CHÍNH SITE NÀY = chủ động quay về trang chủ --------------
       `pricing.html`, `crew.html`, `checkout.html` đều có nút `href="/"`, nút
       chuyển ngữ VI/EN cũng là `href="/"` ↔ `href="/en/"`, và người dùng bấm
       logo để về trang chủ. Không có luật này thì cả nhóm đó bị bật ngược lại —
       trang chủ thành nơi KHÔNG THỂ tới được với người đã đăng nhập. */
    var ref = document.referrer;
    if (ref) {
      var a = document.createElement("a");
      a.href = ref;
      if (a.host === location.host) return;
    }

    /* ---- 5. Đích suy từ chính thẻ <script> đang chạy ------------------------
       ⚠️ BẮT BUỘC, KHÔNG ĐƯỢC GÕ CỨNG "landing-app.html". Trang chủ có HAI bản ở
          HAI ĐỘ SÂU (`/` và `/en/`), nên một hằng chuỗi sẽ phân giải thành
          `/en/landing-app.html` → **404** ở đúng một trong hai. Đó là lỗi thật đã
          xảy ra với nút "Vào chơi ngay" và chỉ lộ ra ngày 20/08/2026 (xem ghi chú
          dài trong `scratchpad/gen_home_en.py`). File này luôn nằm ở
          `<gốc>/js/index-gate.js` nên `../landing-app.html` tính từ src của nó ra
          `<gốc>/landing-app.html` cho CẢ HAI bản. Cùng idiom với `JS_DIR` trong
          `js/index.js`.
       ⚠️ Suy không ra thì THÔI, đừng đoán: ở lại trang chủ là hỏng nhẹ, nhảy sai
          chỗ là trang trắng. */
    var here = document.currentScript && document.currentScript.src;
    if (!here) return;

    /* `replace` chứ không phải `href`: trang chủ không được nằm lại trong lịch
       sử, không thì bấm Quay-lại từ cửa app sẽ về trang chủ → cổng đẩy tiếp →
       kẹt trong bẫy.
       ⚠️ ĐO ĐƯỢC 20/08/2026: ở ĐÚNG chỗ này hai cách cho kết quả **y hệt**
          (`history.length` 3, Quay-lại về đúng trang trước đó) — Chrome coi mọi
          cú điều hướng phát ra khi trang **còn đang tải** là một phép thay thế,
          bất kể viết gì. Vẫn dùng `replace` vì nó nói đúng ý định và không dựa
          vào một chi tiết của trình duyệt; dời lời gọi này xuống sau `load` là
          khác biệt đó thành THẬT. */
    location.replace(new URL("../landing-app.html", here).href);
  } catch (e) {
    /* Trang chủ là trang duy nhất được lập chỉ mục — không bao giờ để nó chết vì
       cái cổng này. Ném lỗi ở <head> là dừng luôn phần <script> còn lại. */
  }
})();
