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

   ─────────────────── BÀI ĐỌC GỢI Ý (`read`) ───────────────────
   ⚠️ `read.topic` KHÔNG PHẢI tiêu đề bài. Tiêu đề là của `js/articles-index.js`
      và chỉ được sống ở đó — chép sang đây là hai nơi giữ một cái tên, và bên
      lệch sẽ là bên nói với trẻ. Ở đây chỉ ghi **chủ đề** bằng vài chữ, đúng cả
      khi bài được đặt lại tên.
   ⚠️ KHÔNG KHOÁ (chủ dự án chốt 14/08/2026): đây là **gợi ý**, không phải điều
      kiện. Bắt đọc xong mới cho huấn luyện là dựng một cổng lộ trình thứ hai, mà
      `js/route-gate.js` đã dạy một bài đắt về chuyện đó (cổng bật vĩnh viễn thì
      khoá chết 7 mẫu vật và 2 huy hiệu).
   ⚠️ `read.id` phải là bài CÓ THẬT trong `js/articles-index.js` — id sai thì
      `library.html?a=` lặng lẽ không mở gì. Có phép kiểm đối chiếu.
   ============================================================ */
(function (global) {
  "use strict";

  var T = {
    /* PHẢN XẠ — hai khoá học (Né Thiên Thạch + Bắt Sao Băng). */
    reaction: {
      ic: "⚡",
      name: { vi: "Phản xạ", en: "Reaction" },
      skill: { vi: "Nhìn thấy — quyết định — làm, trong chưa tới một giây",
               en: "See it, decide, act — in under a second" },
      read: { id: "art-microgravity-is-falling",
              topic: { vi: "vì sao trên trạm mọi thứ đều đang rơi",
                       en: "why everything on the station is falling" } }
    },

    /* NHẬN THỨC KHÔNG GIAN — đây chính là thứ lấy được từ khoá T-38 mà không cần
       mô phỏng một chiếc máy bay nào: phản xạ + nhận thức không gian + quyết định
       nhanh, cả ba trong một sân 360°. */
    spatial: {
      ic: "🧭",
      name: { vi: "Nhận thức không gian", en: "Spatial awareness" },
      skill: { vi: "Biết cái gì đang tới từ hướng nào, kể cả sau lưng",
               en: "Know what is coming from where — including behind you" },
      read: { id: "art-four-forces-tug-of-war",
              topic: { vi: "bốn lực kéo co trên một tên lửa",
                       en: "the four-way tug-of-war on a rocket" } }
    },

    /* ĐỊNH HƯỚNG */
    navigation: {
      ic: "🗺️",
      name: { vi: "Định hướng", en: "Navigation" },
      skill: { vi: "Dựng bản đồ trong đầu rồi tìm đường ra",
               en: "Build a map in your head, then find the way out" },
      read: { id: "art-orbit-is-a-balance",
              topic: { vi: "quỹ đạo là một thế cân bằng",
                       en: "an orbit is a balance" } }
    },

    /* QUẢN LÝ TÀI NGUYÊN */
    resource: {
      ic: "🔋",
      name: { vi: "Quản lý tài nguyên", en: "Resource management" },
      skill: { vi: "Cân giữa đi nhanh và giữ đủ nhiên liệu để về đích",
               en: "Balance going fast against keeping enough fuel to finish" },
      read: { id: "art-life-support-recycles-water",
              topic: { vi: "cỗ máy giữ mạng sống trên trạm",
                       en: "the machine that keeps you alive" } }
    },

    /* QUAN SÁT THIÊN VĂN — chương trình duy nhất dạy kiến thức bầu trời thật. */
    observation: {
      ic: "🔭",
      name: { vi: "Quan sát thiên văn", en: "Sky observation" },
      skill: { vi: "Nhận ra hình dạng thật của bầu trời đêm",
               en: "Recognise the real shapes of the night sky" },
      read: { id: "art-measuring-stars-with-angles",
              topic: { vi: "đo sao bằng góc",
                       en: "measuring stars with angles" } }
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
    read: function (key, lang) {
      var x = T[key];
      if (!x || !x.read) return null;
      return { id: x.read.id, topic: pick(x.read.topic, lang) };
    },

    /** Mọi khoá đã khai tên — dùng cho phép kiểm, không dùng để vẽ. */
    keys: function () { return Object.keys(T); }
  };
})(window);
