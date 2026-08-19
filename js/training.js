/* ============================================================
   training.js — TÊN các chương trình của TRUNG TÂM ĐÀO TẠO PHI HÀNH GIA.

   <script src="js/training.js"></script>   (sau js/ui-common.js)

   ⚠️⚠️ PHÂN CÔNG, giống hệt js/badges.js và js/specimens.js:
     · SERVER (`Services/Training.cs`) giữ **MỐC ĐẠT** và việc chương trình nào
       gồm những khoá học nào.
     · FILE NÀY chỉ giữ **TÊN + KỸ NĂNG + BÀI ĐỌC GỢI Ý**, song ngữ.

   Mốc để hai nơi thì sớm muộn lệch, mà client thì ai cũng sửa được bằng DevTools.
   Ngược lại tên phải dịch VI/EN nên để ở client là đúng chỗ — server không cần
   biết ngôn ngữ nào.

   ⚠️ FILE NÀY KHÔNG ĐƯỢC CHỨA MỘT CON SỐ MỐC NÀO. Có phép kiểm canh
   (check_pages mục [27]): thấy một con số goal ở đây là báo hỏng.

   ⚠️ CHƯƠNG TRÌNH KHÔNG CÓ TÊN THÌ VẪN VẼ, hiện chính khoá của nó — thêm chương
   trình ở server mà quên thêm tên ở đây thì trang xấu chứ không vỡ, và cái xấu
   đó nói cho người sửa biết là còn thiếu gì. Đúng lối `js/badges.js` đã dùng.

   ============================================================ */
(function (global) {
  "use strict";

  var T = {
    /* PHẢN XẠ — hai khoá học (Né Thiên Thạch + Bắt Sao Băng). */
    reaction: {
      ic: "⚡",
      name: { vi: "Phản xạ", en: "Reaction" },
      skill: { vi: "Phản xạ thần tốc — nhìn thấy, quyết định, xử lý xong trong chưa đầy một giây",
               en: "Lightning reflexes — see it, decide, deal with it, all in under a second" }
    },

    /* NHẬN THỨC KHÔNG GIAN — đây chính là thứ lấy được từ khoá T-38 mà không cần
       mô phỏng một chiếc máy bay nào: phản xạ + nhận thức không gian + quyết định
       nhanh, cả ba trong một sân 360°. */
    spatial: {
      ic: "🧭",
      name: { vi: "Nhận thức không gian", en: "Spatial awareness" },
      skill: { vi: "Cảnh giác cực cao — nhận ra ngay nguy hiểm đến từ hướng nào, kể cả sau lưng",
               en: "Razor-sharp awareness — spot instantly where danger is coming from, even behind you" }
    },

    /* ĐỊNH HƯỚNG */
    navigation: {
      ic: "🗺️",
      name: { vi: "Định hướng", en: "Navigation" },
      skill: { vi: "Đầu óc siêu trí tuệ — tự vẽ bản đồ trong đầu để tìm đường thoát nhanh nhất",
               en: "A mind like a map — draw the maze in your head and find the fastest way out" }
    },

    /* QUẢN LÝ TÀI NGUYÊN */
    resource: {
      ic: "🔋",
      name: { vi: "Quản lý tài nguyên", en: "Resource management" },
      skill: { vi: "Lái siêu đỉnh — vừa đua nhanh vừa căn nhiên liệu chuẩn chỉnh để về đích",
               en: "Ace piloting — race hard and ration your fuel well enough to reach the finish" }
    },

    /* QUAN SÁT THIÊN VĂN — chương trình duy nhất dạy kiến thức bầu trời thật. */
    observation: {
      ic: "🔭",
      name: { vi: "Quan sát thiên văn", en: "Sky observation" },
      skill: { vi: "Mắt thần quan sát — nhận ra hình dáng thật của các chòm sao trên bầu trời đêm",
               en: "Eagle eyes — recognise the real shapes of the constellations in the night sky" }
    },

    /* SINH TỒN — chương trình LỚP QUYẾT ĐỊNH đầu tiên (16/08/2026). Khác năm
       chương trình trên ở chỗ nó không đo tay nhanh mắt tinh mà đo việc CHỌN
       ĐÚNG: kỹ năng thật của phi hành gia phần lớn là ra quyết định đúng dưới
       áp lực, không phải bấm nhanh (`docs/proposals/2026-08-14-…` mục 3). */
    /* KIỂM CHỨNG DỮ LIỆU — lớp quyết định, khuôn soi lỗi trong bảng (16/08/2026).
       ⚠️ Đây là chương trình duy nhất mà trẻ KHÔNG dựng ra thứ gì — nó kiểm một
          bảng người khác đã dựng. Xem lý do tách hẳn ở `Services/Training.cs`. */
    datacheck: {
      ic: "📏",
      name: { vi: "Kiểm chứng dữ liệu", en: "Data checking" },
      skill: { vi: "Soi một bảng số liệu và tìm ra chỗ hai bên không nói cùng một thứ",
               en: "Read a data sheet and spot where the two sides do not mean the same thing" }
    },

    /* GIỮ MẠNG SỐNG — lớp quyết định, khuôn chia ngân sách (16/08/2026).
       ⚠️ KHÁC "Quản lý tài nguyên" (Đường Đua): bên kia là cân nhiên liệu để đi
          xa, bên này là giữ một vòng tuần hoàn không đứt. Lý do tách hẳn thành
          chương trình riêng ghi ở `Services/Training.cs`. */
    lifesupport: {
      ic: "♻️",
      name: { vi: "Giữ mạng sống", en: "Life support" },
      skill: { vi: "Chia một nguồn có hạn cho những thứ đều cần, và thấy được cái vòng nối chúng",
               en: "Split a limited supply between things that all need it — and see the loop that links them" }
    },

    /* LIÊN LẠC — lớp quyết định, khuôn xếp thứ tự (16/08/2026). */
    communication: {
      ic: "📡",
      name: { vi: "Liên lạc", en: "Communication" },
      skill: { vi: "Nghĩ trọn cả dãy trước khi bấm, vì lệnh đi rồi thì không gọi lại được",
               en: "Think the whole sequence through first — once sent, it cannot be called back" }
    },

    survival: {
      ic: "🛟",
      name: { vi: "Sinh tồn", en: "Survival" },
      skill: { vi: "Biết thứ gì giữ được mạng sống, và thứ gì chỉ để cho vui",
               en: "Know what keeps people alive — and what is just nice to have" }
    }
  };

  function pick(o, lang) {
    if (!o) return "";
    return lang === "en" ? (o.en != null ? o.en : o.vi) : o.vi;
  }

  global.AstroQTraining = {
    /** Thông tin hiển thị của một chương trình; null nếu chưa khai tên. */
    info: function (key) { return T[key] || null; },

    /** Tên chương trình theo ngôn ngữ; chưa khai thì trả chính khoá (xem đầu file). */
    name: function (key, lang) {
      var x = T[key];
      return x ? pick(x.name, lang) : String(key || "");
    },
    skill: function (key, lang) { var x = T[key]; return x ? pick(x.skill, lang) : ""; },
    icon:  function (key)       { var x = T[key]; return x ? x.ic : "🎯"; },

    /** → {id, topic} hoặc null. `topic` đã dịch sẵn. */

    /** Mọi khoá đã khai tên — dùng cho phép kiểm, không dùng để vẽ. */
    keys: function () { return Object.keys(T); }
  };
})(window);
