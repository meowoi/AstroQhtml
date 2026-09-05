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

    /* KỸ THUẬT HỆ THỐNG — lớp quyết định, khuôn LƯỚI-NỐI (26/08/2026).
       ⚠️⚠️ MỘT CHƯƠNG TRÌNH, CHỖ CHO HAI KHOÁ — và đó là lý do nó không tên là
          "Dẫn tuyến". `docs/proposals/2026-08-26-khuon-luoi-noi-tram-dan-tuyen.md`
          mục 6c: cơ chế "kéo đường nối hai đầu cùng loại" là CÙNG một khuôn với
          Trạm Dẫn Tuyến, nên nếu làm thì nó vào đây làm **khoá thứ hai**, không
          mở chương trình thứ mười một. Có tiền lệ: `reaction` = dodge + catch, và
          luật *cấp chương trình = cấp THẤP NHẤT của các khoá* buộc trẻ phải giỏi
          CẢ nhận quan hệ lẫn dựng tuyến.
       ⚠️ KHÁC "Quản lý tài nguyên" (Đường Đua) và "Giữ mạng sống" (Trạm Tuần
          Hoàn): hai bên kia là CHIA một lượng có hạn; bên này là làm cho một
          tuyến LIỀN — thiếu một mắt là cả tuyến chết, không có "gần đủ". */
    systems: {
      ic: "🔌",
      name: { vi: "Kỹ thuật hệ thống", en: "Systems engineering" },
      skill: { vi: "Nhìn ra cả đường đi của một thứ, và biết thiếu một mắt thì cả tuyến chết",
               en: "See the whole path something travels — and know that one missing link kills all of it" }
    },

    /* ⚠️ CHƯƠNG TRÌNH MỚI, KHÔNG thêm khoá vào một chương trình đang có — cấp
       của một chương trình là cấp THẤP NHẤT trong các khoá, nên thêm khoá là **hạ
       cấp của mọi người đã đạt nó**. Luật đầy đủ ghi ở `Services/Training.cs`.
       ⚠️ KỸ NĂNG Ở ĐÂY KHÁC HẴN "Kiểm chứng dữ liệu" (Trạm Đối Chiếu): bên kia
          là soi một bảng đã có sẵn xem ai ghi sai; bên này là hiểu rằng một cỗ máy
          chỉ biết đúng bằng thứ người ta cho nó xem. */
    mlearn: {
      ic: "🤖",
      name: { vi: "Dạy máy học", en: "Teaching machines" },
      skill: { vi: "Hiểu rằng máy chỉ biết đúng bằng những ví dụ con đã cho nó xem",
               en: "Understand that a machine only knows as much as the examples you showed it" }
    },

    survival: {
      ic: "🛟",
      name: { vi: "Sinh tồn", en: "Survival" },
      skill: { vi: "Biết thứ gì giữ được mạng sống, và thứ gì chỉ để cho vui",
               en: "Know what keeps people alive — and what is just nice to have" }
    }
  };

  /* ============================================================
     MỐC KẾ TIẾP NÓI BẰNG LỜI, KHÔNG PHẢI MỘT CON SỐ TRƠ.

     ⚠️⚠️ VÌ SAO CÓ BẢNG NÀY (21/08/2026): thẻ game trước đây in
     *"Còn 1 nữa lên Cấp 2"* — và chủ dự án bác đúng: *"rất khó hiểu, ko biết là
     1 trận, 4 trận hay điểm?"*. Con số `next` do server trả **không mang đơn vị
     nào**, mà mỗi khoá học đo một thứ khác hẳn: dodge đo MÉT, defender đo ĐIỂM,
     maze đo CẤP SÂN, constellation đo **số chòm sao KHÁC NHAU**, units đo SỐ
     BẢNG. Một con số không có danh từ đi kèm thì trẻ đoán, và đoán sai thì nó
     luyện sai chỗ.

     ⚠️ BẢNG KHOÁ THEO **GAME**, không theo chương trình: một chương trình có thể
     gồm hai khoá đo hai thứ khác nhau (Phản xạ = dodge mét + catch điểm).

     ⚠️ KHÔNG ĐƯỢC CHỨA MỘT CON SỐ MỐC NÀO — token `{n}` do server điền
     (`courses[].next`). Có phép kiểm canh (check_pages mục [27]).

     ⚠️ Câu của `constellation` cố ý viết **KHÁC NHAU** in đậm nghĩa: mốc đó đếm
     `consts` = số chòm sao khác nhau, nên ghép lại đúng chòm vừa ghép thì KHÔNG
     lên cấp. Không nói ra thì trẻ chơi mãi một chòm và tưởng hệ thống hỏng —
     chính hiện tượng đã được báo cùng ngày.
     ============================================================ */
  var GOAL = {
    dodge:         { vi: "bay được {n} m",                   en: "fly {n} m" },
    catch:         { vi: "đạt {n} điểm",                     en: "score {n} points" },
    defender:      { vi: "đạt {n} điểm",                     en: "score {n} points" },
    maze:          { vi: "giải xong mê cung cấp {n}",        en: "clear maze tier {n}" },
    racer:         { vi: "đi được {n} m đường đua",          en: "cover {n} m of the race" },
    constellation: { vi: "ghép đủ {n} chòm sao KHÁC NHAU",   en: "match {n} different constellations" },
    survival:      { vi: "chọn đúng {n} lần trong một lượt", en: "make {n} correct choices in one run" },
    comms:         { vi: "xếp đúng {n} lệnh",                en: "get {n} commands in the right order" },
    recycle:       { vi: "đạt {n} điểm giữ hệ",              en: "reach {n} life-support points" },
    units:         { vi: "duyệt đúng {n} bảng",              en: "clear {n} sheets correctly" },
    route:         { vi: "nối xong {n} tuyến trong một lượt", en: "complete {n} runs in one game" },
    classify:      { vi: "dạy máy qua {n} vòng không gán sai nhãn nào",
                     en: "teach the machine through {n} rounds with no wrong label" }
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

    /**
     * Mốc kế tiếp của MỘT KHOÁ HỌC, nói bằng lời: `goalText("dodge", 500, "vi")`
     * → "bay được 500 m". Chưa khai câu thì trả về chính con số — xấu, nhưng
     * không vỡ, và cái xấu đó nói cho người sửa biết là còn thiếu gì (đúng lối
     * `name()` ở trên).
     */
    goalText: function (game, n, lang) {
      var g = GOAL[game], num = String(n == null ? "" : n);
      return g ? pick(g, lang).replace("{n}", num) : num;
    },

    /** Mọi khoá đã khai tên — dùng cho phép kiểm, không dùng để vẽ. */
    keys: function () { return Object.keys(T); },

    /** Mọi game đã khai câu mốc — dùng cho phép kiểm, không dùng để vẽ. */
    goalKeys: function () { return Object.keys(GOAL); }
  };
})(window);
