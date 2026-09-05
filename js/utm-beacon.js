/* ============================================================
   utm-beacon.js — ĐẾM MỘT LƯỢT ĐẾN, cho khách đi vào bằng link CÓ NHÃN.

   Dùng:  <script type="module" defer src="js/utm-beacon.js"></script>
          (kèm `js/utm.js` nạp trước — file này đọc `pending()` / `pendingEngaged()`)

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

   ⚠️ ĐẾM KHÁCH MỚI, KHÔNG ĐẾM LƯỢT BẤM. `pending()` chỉ trả nhãn khi lượt đến này
      chưa báo được. Người bấm quảng cáo hai lần chỉ được đếm một. Số của Meta ("link
      clicks") vì thế LUÔN ≥ số này, và chênh lệch là chuyện bình thường: Meta đếm cả
      lượt bấm lặp, lượt bot, và lượt bấm rồi thoát trước khi trang tải xong.
   ══════════ SỰ KIỆN THỨ HAI: "Ở LẠI ĐỦ LÂU" (05/09/2026, việc 4) ══════════
   ⚠️⚠️ VÌ SAO. 14 ngày đo được **828 khách mang nhãn, 4 lượt đăng ký** — ~99,6% mất
      TRƯỚC form. Với một con số duy nhất thì *"mở ra rồi đóng ngay"* và *"có đọc mà
      vẫn không đăng ký"* đọc ra y hệt nhau, trong khi cái thứ nhất phải sửa QUẢNG CÁO
      còn cái thứ hai phải sửa TRANG.

   ⚠️ HAI ĐIỀU KIỆN, LẤY CÁI NÀO TỚI TRƯỚC — 10 GIÂY **HOẶC** CUỘN QUA MÀN HÌNH ĐẦU.
      Chỉ đo thời gian thì tab mở nền cũng tính là "có đọc"; chỉ đo cuộn thì người đọc
      kỹ đúng màn hero trên điện thoại (nơi hero đã chiếm gần trọn màn) không bao giờ
      được tính. Mỗi phép đo một mù riêng, và hai mù đó không chồng lên nhau.

   ⚠️ ĐỒNG HỒ DỪNG KHI TAB ẨN, và đây KHÔNG phải chuyện làm cho đẹp: link mở trong tab
      nền (bấm giữa chuột, hoặc trình duyệt tải trước) sẽ đủ 10 giây mà **không ai
      nhìn** — tức bơm thẳng vào đúng con số dùng để kết luận "trang giữ được người".
      `visibilitychange` cộng dồn phần thời gian THẤY ĐƯỢC.

   ⚠️ NGƯỠNG CUỘN LÀ 60% CHIỀU CAO KHUNG NHÌN, không phải 100%: đủ để chắc chắn người
      ta đã kéo trang có chủ đích, mà không đòi họ vượt hẳn một màn — trên máy tính để
      bàn màn hình cao, "một màn" có thể là gần hai nghìn pixel.
   ============================================================ */
import { apiPost, isApiConfigured } from "./api.js";

(function () {
  "use strict";

  /* API chưa cấu hình (API_BASE rỗng) thì lùi im lặng — cùng nguyên tắc với
     js/api.js và js/firebase-config.js: trang không bao giờ vỡ vì thiếu cấu hình. */
  if (!isApiConfigured) return;

  var utm = window.AstroQUtm;
  if (!utm || typeof utm.pending !== "function") return;     // utm.js chưa nạp

  /* ⚠️⚠️ CHỈ ĐÁNH DẤU KHI SERVER ĐÃ NHẬN. Đánh dấu lạc quan ngay lúc bắn request là
     mất lượt mỗi khi mạng hỏng — đúng lỗi mà cờ bền sinh ra để chữa. Hỏng thì KHÔNG
     đánh dấu, và lượt sau mở trang bất kỳ sẽ báo bù.
     ⚠️ `apiCall` KHÔNG BAO GIỜ NÉM — nó nuốt mọi lỗi và trả
        `{ ok:false, status:0, netError:true }` khi mất mạng/CORS/quá hạn, hoặc
        `{ notConfigured:true }` khi API_BASE rỗng. Nên căn cứ duy nhất đúng là `r.ok`
        (204 nằm trong 2xx). Bản đầu của tôi xét "không phải notConfigured" — tức coi
        cả lỗi mạng là thành công, và đánh dấu đã báo một lượt chưa hề tới server.
     `catch` rỗng là CÓ Ý: xem cảnh báo đầu file. */
  function report(body, mark) {
    try {
      Promise.resolve(apiPost("/visit", body))
        .then(function (r) {
          if (r && r.ok) { try { mark(); } catch (e) {} }
        })
        .catch(function () { /* để nguyên cờ chưa-báo, lượt sau thử lại */ });
    } catch (e) { /* im lặng */ }
  }

  /* ───────── ① LƯỢT MỞ TRANG (từ 23/08/2026) ───────── */
  var src = "";
  try { src = utm.pending(); } catch (e) { src = ""; }
  if (src) report({ src: src }, utm.markSent);

  /* ───────── ② Ở LẠI ĐỦ LÂU (từ 05/09/2026) ─────────
     ⚠️ HỎI NHÃN LẦN NỮA, KHÔNG DÙNG LẠI `src` Ở TRÊN. `src` rỗng nghĩa là lượt MỞ
        TRANG đã báo xong từ một lượt nạp trước — người đó vẫn có thể chưa bao giờ
        báo được lượt "ở lại". Dùng lại biến kia là im lặng bỏ qua đúng nhóm khách
        quay lại, tức nhóm đáng quan tâm nhất. */
  var engSrc = "";
  try { engSrc = utm.pendingEngaged(); } catch (e) { engSrc = ""; }
  if (!engSrc) return;               // không có nhãn, hoặc đã báo rồi → 0 request

  var STAY_MS  = 10000;              // 10 giây THẤY ĐƯỢC
  var SCROLL_R = 0.6;                // 60% chiều cao khung nhìn
  var seen  = 0;                     // ms đã cộng dồn ở trạng thái thấy được
  var since = 0;                     // mốc bắt đầu quãng thấy được hiện tại
  var timer = 0;
  var done  = false;

  function fire() {
    if (done) return;
    done = true;
    stopClock();
    window.removeEventListener("scroll", onScroll);
    document.removeEventListener("visibilitychange", onVis);
    report({ src: engSrc, ev: "engaged" }, utm.markEngaged);
  }

  function stopClock() {
    if (timer) { clearTimeout(timer); timer = 0; }
    if (since) { seen += Date.now() - since; since = 0; }
  }

  function startClock() {
    if (done || since) return;
    since = Date.now();
    /* ⚠️ HẸN PHẦN CÒN LẠI, KHÔNG HẸN LẠI ĐỦ 10 GIÂY. Người chuyển tab qua lại vài
       lần mà lần nào cũng đặt lại đồng hồ thì không bao giờ tới đích — tức mọi khách
       vừa đọc vừa làm việc khác đều rơi khỏi phép đo. */
    timer = setTimeout(fire, Math.max(0, STAY_MS - seen));
  }

  function onVis() {
    if (document.hidden) stopClock(); else startClock();
  }

  /* ⚠️ `passive:true` LÀ BẮT BUỘC Ở ĐÂY. Trình duyệt phải đợi listener chạy xong mới
     biết có `preventDefault()` không, nên một listener cuộn không passive làm khụng đúng
     cái thao tác nó đang đo. Một bộ đếm marketing không được phép làm giật trang cuộn
     của một đứa trẻ. */
  function onScroll() {
    var y = window.pageYOffset || document.documentElement.scrollTop || 0;
    if (y > (window.innerHeight || 0) * SCROLL_R) fire();
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  document.addEventListener("visibilitychange", onVis);
  /* Trang mở sẵn ở tab nền thì `document.hidden` đã true ngay từ đầu — đồng hồ chỉ
     chạy khi nào người ta thật sự nhìn tới. */
  if (!document.hidden) startClock();
})();
