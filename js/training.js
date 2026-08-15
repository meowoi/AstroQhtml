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
      skill: { vi: "Nhìn thấy — quyết định — làm, trong chưa tới một giây",
               en: "See it, decide, act — in under a second" }
    },

    /* NHẬN THỨC KHÔNG GIAN — đây chính là thứ lấy được từ khoá T-38 mà không cần
       mô phỏng một chiếc máy bay nào: phản xạ + nhận thức không gian + quyết định
       nhanh, cả ba trong một sân 360°. */
    spatial: {
      ic: "🧭",
      name: { vi: "Nhận thức không gian", en: "Spatial awareness" },
      skill: { vi: "Biết cái gì đang tới từ hướng nào, kể cả sau lưng",
               en: "Know what is coming from where — including behind you" }
    },

    /* ĐỊNH HƯỚNG */
    navigation: {
      ic: "🗺️",
      name: { vi: "Định hướng", en: "Navigation" },
      skill: { vi: "Dựng bản đồ trong đầu rồi tìm đường ra",
               en: "Build a map in your head, then find the way out" }
    },

    /* QUẢN LÝ TÀI NGUYÊN */
    resource: {
      ic: "🔋",
      name: { vi: "Quản lý tài nguyên", en: "Resource management" },
      skill: { vi: "Cân giữa đi nhanh và giữ đủ nhiên liệu để về đích",
               en: "Balance going fast against keeping enough fuel to finish" }
    },

    /* QUAN SÁT THIÊN VĂN — chương trình duy nhất dạy kiến thức bầu trời thật. */
    observation: {
      ic: "🔭",
      name: { vi: "Quan sát thiên văn", en: "Sky observation" },
      skill: { vi: "Nhận ra hình dạng thật của bầu trời đêm",
               en: "Recognise the real shapes of the night sky" }
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
