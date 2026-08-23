/* ============================================================
   utm.js — GHI NHỚ "NGƯỜI NÀY ĐẾN TỪ ĐÂU", để biết bài đăng nào ra người thật.

   Dùng:  <script src="js/utm.js"></script>   (trước script riêng của trang)
   API:   AstroQUtm.get()    → "fb/post/ra-mat-20-08" | ""   (chuỗi gửi lên server)
          AstroQUtm.raw()    → { source, medium, campaign, at } | null
          AstroQUtm.clear()  → xoá (dùng khi test)
          AstroQUtm.takeFresh() → nhãn NẾU lượt nạp này là chạm-đầu-tiên MỚI, rồi
                                  tự xoá cờ. `js/utm-beacon.js` dùng để đếm lượt đến.

   Gắn link ở fanpage:
       https://astroq.org/?utm_source=facebook&utm_medium=post&utm_campaign=ra-mat-20-08
   ⚠️ Nguồn Facebook viết `facebook`, KHÔNG viết `fb` — chiến dịch trả tiền đang chạy
      từ 22/08/2026 dùng `facebook`, và hai cách viết sẽ thành HAI nguồn khác nhau
      trong bảng báo cáo. Tên nguồn không được chuẩn hoá ở đâu cả (cố ý: `Campaign.Clean`
      chỉ lọc ký tự, không đổi chữ), nên nhất quán là việc của người đặt link.

   ══════════════ VÌ SAO TỰ LÀM THAY VÌ GẮN GOOGLE ANALYTICS ══════════════
   Câu hỏi cần trả lời rất hẹp: *"bài đăng nào mang người tới, và trong số đó
   bao nhiêu người thật sự đăng ký"*. Một trình theo dõi bên thứ ba trả lời được
   câu đó, nhưng kèm theo ba thứ dự án đã cố ý từ chối:
     · một tên miền ngoài trên đường tải (07/08/2026 vừa gỡ sạch `unpkg` và
       `gstatic` để mở đường PWA — service worker không cache đàng hoàng được
       phản hồi cross-origin);
     · ~50 KB script và một vòng mạng cho mọi lượt ghé;
     · gửi hành vi duyệt web của TỪNG ĐỨA TRẺ cho một công ty khác — đúng lý do
       `js/firebase-config.js` cố ý không bật `measurementId`.
   Cách này: **0 byte tải thêm, 0 cookie, 0 bên thứ ba**, và thứ duy nhất rời khỏi
   máy là NHÃN CHIẾN DỊCH do chính mình đặt trong link của mình.

   ⚠️⚠️ TỪ 23/08/2026 CÓ ĐÚNG MỘT REQUEST, VÀ CHỈ CHO KHÁCH MANG NHÃN.
   `js/utm-beacon.js` gọi `POST /visit` một lần khi lượt nạp này là chạm-đầu-tiên MỚI.
   Vì sao phải có: bảng báo cáo trước đây chỉ đếm được lượt ĐĂNG KÝ, mà nhãn chỉ ghi
   vào DB lúc đăng ký thành công — nên một chiến dịch mang về 200 người mà 0 người
   đăng ký đọc ra Y HỆT một chiến dịch không ai bấm. Hai chuyện đó phải xử lý khác hẳn.
   ⚠️ Người vào thẳng `astroq.org` (không có `utm_source`) thì **vẫn 0 request** như
      trước — `takeFresh()` trả "" nên beacon không gửi gì. Đó là điều kiện để thêm
      phép đo này mà không đổi cái giá người dùng thường phải trả.
   ⚠️ Bản ghi phía server là BỘ ĐẾM: cộng 1 vào (ngày × nhãn), không IP, không
      user-agent, không thời điểm từng lượt. Xem `DynamoContext.Visits.cs`.

   ⚠️⚠️ GIỮ LƯỢT CHẠM ĐẦU TIÊN, KHÔNG GHI ĐÈ BẰNG LƯỢT SAU.
   Câu hỏi là *"cái gì mang người này tới"* — đó là lần đầu. Trẻ vào từ bài
   Facebook hôm nay, ba hôm sau tự gõ địa chỉ rồi mới đăng ký: ghi đè theo lượt
   cuối thì công của bài đăng biến mất và mọi bài đều trông như vô dụng. Vì thế
   `save()` KHÔNG ghi khi đã có bản ghi còn hạn.

   ⚠️ CÓ HẠN 60 NGÀY. Không có hạn thì một cú bấm từ tháng trước vẫn được tính
   công cho một lượt đăng ký hôm nay — con số đẹp nhưng sai. 60 ngày đủ rộng cho
   nhịp "thấy bài → vài hôm sau mới rủ được bố mẹ ngồi cùng".

   ⚠️ CHUỖI GỬI LÊN BỊ CHẶN ĐỘ DÀI VÀ BỘ KÝ TỰ NGAY TẠI ĐÂY, và server **lọc lại
   lần nữa** — client là thứ ai cũng sửa được bằng DevTools, mà chuỗi này đi vào
   DynamoDB rồi hiện ra ở trang báo cáo admin. Cùng khuôn `Clean()` của
   MeEndpoints: chỉ `a–z 0–9 - _ .`, mỗi phần tối đa 24 ký tự.
   ============================================================ */
(function (global) {
  "use strict";

  var KEY = "astroq-utm";
  var MAX_AGE_DAYS = 60;
  var MAX_PART = 24;

  /* Chỉ nhận ký tự an toàn, hạ chữ thường, cắt độ dài. Trả "" nếu không còn gì. */
  function clean(v) {
    return String(v == null ? "" : v)
      .trim().toLowerCase()
      .replace(/[^a-z0-9._-]/g, "")
      .slice(0, MAX_PART);
  }

  function read() {
    try {
      var o = JSON.parse(global.localStorage.getItem(KEY) || "null");
      if (!o || !o.at) return null;
      var days = (Date.now() - o.at) / 86400000;
      if (days < 0 || days > MAX_AGE_DAYS) return null;   // hết hạn (hoặc đồng hồ máy chạy lùi)
      return o;
    } catch (e) { return null; }                          // chế độ riêng tư chặn localStorage
  }

  function save(o) {
    try { global.localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {}
  }

  /* Đọc tham số từ địa chỉ hiện tại. `utm_source` là thứ duy nhất bắt buộc —
     không có nó thì coi như lượt ghé không mang nhãn nào. */
  function fromUrl() {
    var q;
    try { q = new global.URLSearchParams(global.location.search); }
    catch (e) { return null; }

    var source = clean(q.get("utm_source"));
    if (!source) return null;
    return {
      source: source,
      medium: clean(q.get("utm_medium")),
      campaign: clean(q.get("utm_campaign")),
      at: Date.now()
    };
  }

  /* ⚠️ CHẠY NGAY LÚC NẠP FILE, không đợi DOM: người dùng có thể bấm nút đăng ký
     trước khi trang vẽ xong, và lúc đó nhãn phải đã nằm sẵn trong máy. */
  var incoming = fromUrl();
  /* ⚠️ `fresh` CHỈ BẬT KHI THẬT SỰ GHI MỚI, tức đúng những lượt là chạm-đầu-tiên.
     Người bấm quảng cáo hôm nay rồi mai bấm lại: lượt thứ hai KHÔNG ghi (giữ chạm
     đầu) nên cũng KHÔNG đếm lại. Nghĩa là con số đếm được là **số khách MỚI mang
     nhãn**, không phải số lượt bấm — Meta đếm lượt bấm nên số của Meta luôn ≥ số này.
     Đừng đem hai con số đó ra trừ nhau rồi kết luận ai sai. */
  var fresh = false;
  if (incoming && !read()) { save(incoming); fresh = true; }

  var API = {
    raw: function () { return read(); },

    /**
     * Nhãn NẾU lượt nạp này vừa ghi một chạm-đầu-tiên mới; "" nếu không. Gọi xong là
     * cờ tắt, nên gọi lần hai trong cùng lượt nạp trả "" — để hai script cùng gọi
     * cũng không đếm đôi.
     */
    takeFresh: function () {
      if (!fresh) return "";
      fresh = false;
      return API.get();
    },

    /** Chuỗi gọn gửi lên server: "nguồn/kênh/chiến-dịch", bỏ phần rỗng. */
    get: function () {
      var o = read();
      if (!o) return "";
      return [o.source, o.medium, o.campaign].filter(Boolean).join("/");
    },

    clear: function () {
      try { global.localStorage.removeItem(KEY); } catch (e) {}
    }
  };

  global.AstroQUtm = API;
})(window);
