/* ============================================================
   utm.js — GHI NHỚ "NGƯỜI NÀY ĐẾN TỪ ĐÂU", để biết bài đăng nào ra người thật.

   Dùng:  <script src="js/utm.js"></script>   (trước script riêng của trang)
   API:   AstroQUtm.get()    → "fb/post/ra-mat-20-08" | ""   (chuỗi gửi lên server)
          AstroQUtm.raw()    → { source, medium, campaign, at } | null
          AstroQUtm.clear()  → xoá (dùng khi test)
          AstroQUtm.pending()   → nhãn NẾU lượt đến này chưa báo được về server
          AstroQUtm.markSent()  → đánh dấu đã báo (chỉ gọi khi server đã nhận)
          AstroQUtm.pendingEngaged() → nhãn NẾU chưa báo được lượt "ở lại đủ lâu"
          AstroQUtm.markEngaged()    → đánh dấu đã báo lượt đó
                                  Bốn hàm trên là của `js/utm-beacon.js`.

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

   ⚠️⚠️ TỪ 23/08/2026 CÓ REQUEST, VÀ CHỈ CHO KHÁCH MANG NHÃN (05/09/2026: NHIỀU NHẤT HAI).
   `js/utm-beacon.js` gọi `POST /visit` một lần khi lượt nạp này là chạm-đầu-tiên MỚI.
   Vì sao phải có: bảng báo cáo trước đây chỉ đếm được lượt ĐĂNG KÝ, mà nhãn chỉ ghi
   vào DB lúc đăng ký thành công — nên một chiến dịch mang về 200 người mà 0 người
   đăng ký đọc ra Y HỆT một chiến dịch không ai bấm. Hai chuyện đó phải xử lý khác hẳn.
   ⚠️ Người vào thẳng `astroq.org` (không nhãn, không `fbclid`) thì **vẫn 0 request**
      như trước — `pending()` trả "" nên beacon không gửi gì. Đó là điều kiện để thêm
      phép đo này mà không đổi cái giá người dùng thường phải trả.

   ⚠️⚠️ REQUEST THỨ HAI THÊM 05/09/2026 (việc 4 của bản phân tích 04/09) — `ev:"engaged"`,
      bắn khi khách **ở lại 10 giây HOẶC cuộn qua màn hình đầu**. Lý do bằng số: 14 ngày
      đo được **828 khách mang nhãn và 4 lượt đăng ký**, tức ~99,6% mất TRƯỚC form. Với
      một con số `n` duy nhất thì "mở ra rồi đóng ngay" và "có đọc mà vẫn không đăng ký"
      đọc ra y hệt nhau — mà cái thứ nhất phải sửa QUẢNG CÁO còn cái thứ hai phải sửa
      TRANG. Sự kiện thứ hai là chỗ ranh giới đó được ghi lại.
   ⚠️ CÙNG ĐIỀU KIỆN RIÊNG TƯ, KHÔNG NỚI MỘT LY: chỉ khách mang nhãn, chỉ một lần cho
      mỗi chạm-đầu-tiên, và thân request vẫn đúng hai trường (`src` + `ev`) — không mốc
      thời gian, không độ sâu cuộn, không `fbclid`. Bản ghi phía server vẫn là bộ đếm
      cộng dồn theo (ngày × nhãn), thêm đúng một con số.
   ⚠️ NẠP Ở CẢ 37 TRANG (23/08/2026), không chỉ trang chủ: quảng cáo trỏ vào trang
      nào thì trang đó phải bắt được nhãn. Trước đó chỉ `index.html` và
      `landing-app.html` có, nên một quảng cáo trỏ vào `pricing.html` là mất sạch số
      mà không có dấu hiệu gì.
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

  /* ⚠️⚠️ BỘ LỌC RIÊNG CHO `fbclid` — ĐỪNG DÙNG `clean()` CHO NÓ. Đã trả giá đúng một
     lần (26/08/2026): bản đầu tôi cho `fbclid` đi qua `clean()`, và `smoke_utm` mục
     [5] bắt ngay lúc chạy — `IwAR_TEST_abc123` đọc ra `iwar_test_abc123`.
     Hai thứ `clean()` làm mà ở đây là PHÁ HOẠI:
       · `toLowerCase()` — `fbclid` là token PHÂN BIỆT CHỮ HOA/THƯỜNG;
       · `slice(0, 24)` — `fbclid` thật dài ~100+ ký tự, cắt còn 24 là mất hẳn.
     Và cả hai đều hỏng IM LẶNG: Meta vẫn nhận sự kiện, trả 200, rồi không khớp được
     lượt bấm nào. Không có bộ đo lúc chạy thì không ai thấy.
     ⚠️ Vẫn phải LỌC, không nhận thô: đây là chuỗi từ địa chỉ, tức người khác đặt được.
        Giữ đúng bộ ký tự base64url mà Meta dùng, và chặn độ dài để không ai nhét được
        một chuỗi khổng lồ vào `localStorage` rồi vào thân request đăng ký. */
  var MAX_ID = 255;

  function cleanId(v) {
    return String(v == null ? "" : v)
      .trim()
      .replace(/[^A-Za-z0-9._-]/g, "")
      .slice(0, MAX_ID);
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

  /* Đọc tham số từ địa chỉ hiện tại. `utm_source` là nhãn MÌNH TỰ ĐẶT nên nó
     được ưu tiên tuyệt đối; không có nó thì còn một lưới đỡ, xem dưới. */
  function fromUrl() {
    var q;
    try { q = new global.URLSearchParams(global.location.search); }
    catch (e) { return null; }

    /* ⚠️⚠️ GIỮ `fbclid` THÔ Ở CẢ HAI NHÁNH (thêm 26/08/2026). Trước đó file này chỉ
       dùng SỰ CÓ MẶT của `fbclid` để suy ra nhãn `facebook/fbclid` rồi bỏ giá trị đi.
       Nay đường Conversions API cần chính giá trị đó: `AstroqSV` dựng
       `fb.1.{ms}.{fbclid}` và chuyển tiếp cho Meta đúng MỘT LẦN lúc tạo tài khoản.
       ⚠️ Phải giữ ở CẢ nhánh `utm_source` nữa, không chỉ nhánh lưới đỡ: link quảng cáo
          gắn nhãn ĐÚNG thì Meta VẪN thêm `fbclid` vào, và đó chính là nhóm link ta
          quan tâm nhất. Chỉ giữ ở nhánh lưới đỡ là chỉ đo được đúng những link mình
          quên gắn nhãn — ngược hẳn ý muốn.
       ⚠️ CHỈ NẰM TRONG `localStorage` CỦA MÁY NGƯỜI DÙNG, và chỉ rời khỏi máy MỘT LẦN
          khi người ta bấm "Tạo tài khoản". `POST /visit` KHÔNG mang nó — lời hứa
          "không dấu vết lần được về một người" của route đó giữ nguyên. */
    var fbclid = cleanId(q.get("fbclid"));   // ⚠️ cleanId, KHONG clean — xem trên

    var source = clean(q.get("utm_source"));
    if (source) {
      return {
        source: source,
        medium: clean(q.get("utm_medium")),
        campaign: clean(q.get("utm_campaign")),
        fbclid: fbclid,
        at: Date.now(), sent: false
      };
    }

    /* ⚠️⚠️ LƯỚI ĐỠ `fbclid` — cho những link QUÊN GẮN NHÃN.
       Meta tự thêm `fbclid` vào MỌI link nó phát đi (cả Facebook lẫn Instagram).
       Nó không phải nhãn của mình, nhưng nó chứng minh được đúng một điều: người
       này tới từ một link Meta. Trước lưới này, một quảng cáo quên gắn `utm_source`
       là mất số HOÀN TOÀN — mà quên thì không ai báo, nó chỉ lặng lẽ đếm 0.

       ⚠️ MEDIUM GHI `fbclid`, TUYỆT ĐỐI KHÔNG GHI `paid`. `fbclid` có mặt ở cả
          link quảng cáo TRẢ TIỀN lẫn bài đăng thường lẫn link người ta chia sẻ
          tay — nên viết `paid` là bịa ra một điều mình không biết, và tệ hơn là
          nó sẽ trộn vào đúng con số dùng để tính hiệu quả đồng tiền quảng cáo.
          Ghi `fbclid` thì người đọc báo cáo thấy ngay "cái này tới từ Meta nhưng
          link chưa gắn nhãn" — tức bản thân dòng đó là lời nhắc đi sửa link.

       ⚠️ CHỈ LÀ LƯỚI ĐỠ, KHÔNG THAY THẾ VIỆC GẮN NHÃN. Nó không tách được chiến
          dịch nào ra chiến dịch nào: mọi link Meta quên nhãn đều dồn vào một dòng
          `facebook/fbclid`. Thấy dòng đó lớn lên là dấu hiệu phải đi sửa link. */
    if (fbclid) {
      return {
        source: "facebook", medium: "fbclid", campaign: "",
        fbclid: fbclid,
        at: Date.now(), sent: false
      };
    }

    return null;
  }

  /* ⚠️ CHẠY NGAY LÚC NẠP FILE, không đợi DOM: người dùng có thể bấm nút đăng ký
     trước khi trang vẽ xong, và lúc đó nhãn phải đã nằm sẵn trong máy. */
  var incoming = fromUrl();
  /* ⚠️ CHỈ GHI KHI CHƯA CÓ BẢN GHI CÒN HẠN — giữ chạm-đầu-tiên. Người bấm quảng
     cáo hôm nay rồi mai bấm lại: lượt sau KHÔNG ghi đè, nên cũng KHÔNG đếm lại.
     Con số đếm được vì thế là **số khách MỚI mang nhãn**, không phải số lượt bấm;
     Meta đếm lượt bấm nên số của Meta luôn ≥ số này. Đừng trừ hai số đó cho nhau. */
  if (incoming && !read()) save(incoming);

  var API = {
    raw: function () { return read(); },

    /**
     * Nhãn NẾU lượt đến này CHƯA báo được về server; "" nếu đã báo (hoặc không có nhãn).
     *
     * ⚠️⚠️ CỜ NẰM TRONG localStorage, KHÔNG PHẢI TRONG BIẾN CỦA LƯỢT NẠP. Bản đầu
     *    dùng một biến `fresh` sống đúng một lượt nạp, nên **POST hỏng là mất lượt
     *    vĩnh viễn** — mất mạng, server 500, hay người dùng đóng tab trước khi
     *    request đi xong, đều biến thành một lượt đến không bao giờ được đếm. Cờ
     *    bền thì lượt sau mở trang bất kỳ là báo bù được.
     * ⚠️ Vì thế `markSent()` chỉ được gọi khi server ĐÃ NHẬN. Gọi lạc quan ngay lúc
     *    bắn request là quay lại đúng lỗi vừa sửa.
     */
    pending: function () {
      var o = read();
      return (o && !o.sent) ? API.get() : "";
    },

    /** Đánh dấu đã báo được về server. Chỉ gọi khi server đã nhận (204). */
    markSent: function () {
      var o = read();
      if (!o || o.sent) return;
      o.sent = true;
      save(o);
    },

    /**
     * Nhãn NẾU lượt đến này CHƯA báo được sự kiện "ở lại đủ lâu"; "" nếu đã báo
     * (hoặc không có nhãn).
     *
     * ⚠️⚠️ CỜ RIÊNG (`eng`), KHÔNG DÙNG CHUNG `sent`. Hai sự kiện độc lập nhau và
     *    thứ tự tới server KHÔNG bảo đảm: người mở trang lúc mất sóng rồi đọc mười
     *    giây, tới lúc bắn `engaged` thì mạng đã về — dùng chung một cờ thì hoặc mất
     *    lượt "ở lại", hoặc đánh dấu khống lượt "mở trang" chưa bao giờ tới nơi.
     * ⚠️ ĐẾM KHÁCH, KHÔNG ĐẾM PHIÊN. Cờ nằm trong `localStorage` cùng bản ghi
     *    chạm-đầu-tiên (60 ngày), nên một người đọc kỹ ba lần trong ba ngày vẫn chỉ
     *    được đếm MỘT — đúng đơn vị của `n` để `e/n` là một tỉ lệ có nghĩa. Đổi sang
     *    `sessionStorage` là lặng lẽ đổi mẫu số của phép chia.
     */
    pendingEngaged: function () {
      var o = read();
      return (o && !o.eng) ? API.get() : "";
    },

    /** Đánh dấu đã báo được lượt "ở lại đủ lâu". Chỉ gọi khi server đã nhận (204). */
    markEngaged: function () {
      var o = read();
      if (!o || o.eng) return;
      o.eng = true;
      save(o);
    },

    /**
     * Mã lượt bấm quảng cáo Meta THÔ + mốc chạm đầu tiên, cho đường Conversions API.
     * Trả `null` khi lượt đến này không tới từ một link Meta.
     *
     * ⚠️ TRẢ THÔ, KHÔNG DỰNG KHUÔN `fb.1.{ms}.{fbclid}` Ở ĐÂY. Khuôn đó là luật của
     *    Meta và nó thuộc về server (`MetaCapi.BuildFbc`) — dựng ở client là hai nơi
     *    cùng giữ một luật, và bản ở client sẽ nói cái cũ vào đúng ngày Meta đổi
     *    khuôn. Cùng phân công với giá đồ trang trí (`js/cosmetics.js`) và bảng huy
     *    hiệu (`js/badges.js`): client giữ CHỮ, server giữ LUẬT.
     */
    click: function () {
      var o = read();
      if (!o || !o.fbclid) return null;
      return { fbclid: o.fbclid, at: o.at || 0 };
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
