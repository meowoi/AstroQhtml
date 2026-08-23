/* ============================================================
   utm-beacon.js — ĐẾM MỘT LƯỢT ĐẾN, cho khách đi vào bằng link CÓ NHÃN.

   Dùng:  <script type="module" defer src="js/utm-beacon.js"></script>
          (kèm `js/utm.js` nạp trước — file này đọc `AstroQUtm.takeFresh()`)

   ══════════════ VÌ SAO LÀ MỘT FILE RIÊNG, KHÔNG NHÉT VÀO utm.js ══════════════
   `js/utm.js` là script cổ điển (IIFE), chạy NGAY lúc nạp và trước cả DOM — nó phải
   như thế vì trẻ có thể bấm đăng ký trước khi trang vẽ xong. Còn địa chỉ API thì chỉ
   `js/api.js` biết, mà `api.js` là ES module. Nhét lời gọi mạng vào `utm.js` buộc
   phải CHÉP LẠI hằng số `PROD_API` sang đó — tức hai nguồn sự thật cho một địa chỉ,
   và cái chép sẽ trôi khỏi bản gốc đúng vào ngày đổi stack AWS.
   ⇒ Tách ra: `utm.js` giữ nhãn (không mạng), file này gọi mạng (không giữ nhãn).

   ⚠️⚠️ KHÔNG BAO GIỜ CHẶN, KHÔNG BAO GIỜ VỠ TRANG. Đây là một bộ đếm marketing đặt
      trên trang chủ của một app cho trẻ con. Mọi nhánh hỏng — API chưa cấu hình, mất
      mạng, server 500, người dùng chặn request — đều phải đi qua trong im lặng. Một
      dòng đỏ trong console vì một con số thống kê là cái giá không đáng trả.

   ⚠️ ĐẾM KHÁCH MỚI, KHÔNG ĐẾM LƯỢT BẤM. `takeFresh()` chỉ trả nhãn ở lượt nạp ghi
      chạm-đầu-tiên. Người bấm quảng cáo hai lần chỉ được đếm một. Số của Meta ("link
      clicks") vì thế LUÔN ≥ số này, và chênh lệch là chuyện bình thường: Meta đếm cả
      lượt bấm lặp, lượt bot, và lượt bấm rồi thoát trước khi trang tải xong.
   ============================================================ */
import { apiPost, isApiConfigured } from "./api.js";

(function () {
  "use strict";

  /* API chưa cấu hình (API_BASE rỗng) thì lùi im lặng — cùng nguyên tắc với
     js/api.js và js/firebase-config.js: trang không bao giờ vỡ vì thiếu cấu hình. */
  if (!isApiConfigured) return;

  var utm = window.AstroQUtm;
  if (!utm || typeof utm.pending !== "function") return;     // utm.js chưa nạp

  var src = "";
  try { src = utm.pending(); } catch (e) { return; }
  if (!src) return;      // không có nhãn, hoặc đã báo rồi → 0 request

  /* ⚠️⚠️ CHỈ `markSent()` KHI SERVER ĐÃ NHẬN. Đánh dấu lạc quan ngay lúc bắn
     request là mất lượt mỗi khi mạng hỏng — đúng lỗi mà cờ bền sinh ra để chữa.
     Hỏng thì KHÔNG đánh dấu, và lượt sau mở trang bất kỳ sẽ báo bù.
     `catch` rỗng là CÓ Ý: xem cảnh báo đầu file. */
  try {
    Promise.resolve(apiPost("/visit", { src: src }))
      .then(function (r) {
        /* ⚠️ `apiCall` KHÔNG BAO GIỜ NÉM — nó nuốt mọi lỗi và trả
           `{ ok:false, status:0, netError:true }` khi mất mạng/CORS/quá hạn, hoặc
           `{ notConfigured:true }` khi API_BASE rỗng. Nên căn cứ duy nhất đúng là
           `r.ok` (204 nằm trong 2xx). Bản đầu của tôi xét "không phải
           notConfigured" — tức coi cả lỗi mạng là thành công, và đánh dấu đã báo
           một lượt chưa hề tới server. Đó đúng là thứ cờ bền sinh ra để chữa. */
        if (r && r.ok) { try { utm.markSent(); } catch (e) {} }
      })
      .catch(function () { /* để nguyên cờ chưa-báo, lượt sau thử lại */ });
  } catch (e) { /* im lặng */ }
})();
