/* ============================================================
   js/depth.js — HAI ĐỘ SÂU LỜI GIẢI THÍCH. Chỗ DUY NHẤT khai hai bậc.

   Nạp như script thường:
     <script src="js/depth.js"></script>
     AstroQDepth.get() · .set(band) · .isSenior() · .label(band, lang)

   ⚠️⚠️ VÌ SAO CÓ FILE NÀY: dải tuổi của dự án là 8–15, và nó VẮT QUA đúng chỗ
   trẻ đổi kiểu chơi. Hai đường độc lập chỉ vào cùng một mốc ~11 tuổi:
     · NASA xuất bản CÙNG một chủ đề (Microgravity) thành HAI bản — K-4 và 5-8;
     · nghiên cứu thiết kế game cho trẻ: *"personal challenge is specifically
       preferred over social competition during middle childhood (7-11)"* và
       *"social competition has shown to become pleasantly engaging from the
       age of 11"*.
   Nên một nội dung, HAI độ sâu — rẻ hơn hẳn làm hai nội dung.

   ⚠️⚠️ ĐỘ SÂU SUY TỪ TUỔI KHAI BÁO, TUYỆT ĐỐI KHÔNG SUY TỪ `level`.
   `level` đo THỜI GIAN ĐÃ CHƠI, không đo tuổi: một đứa 15 tuổi vừa đăng ký là
   cấp 1 và sẽ nhận bản viết cho trẻ 8 tuổi; một đứa 8 tuổi chơi ba tháng là cấp
   20 và nhận bản sâu. Ngược hẳn ý muốn. (Cảnh báo này đã ghi ở
   `docs/proposals/2026-08-12-de-xuat-phong-nghien-cuu-hap-dan.md` mục 18.2.)

   ⚠️ CHỈ LƯU BẬC, KHÔNG LƯU TUỔI. Câu hỏi ở `select.html` hỏi tuổi nhưng thứ
   được ghi xuống là `"junior"` / `"senior"` — dữ liệu cá nhân của một đứa trẻ
   thì lấy đúng phần dùng tới, không lấy thừa. Đây cũng là lý do không có ô nhập
   ngày sinh.

   ⚠️ MẶC ĐỊNH LÀ `junior`, CÓ CHỦ Ý. Chưa biết tuổi thì nói đơn giản: thà nói
   đơn giản với một đứa 15 tuổi (nó bấm "Tìm hiểu thêm" là xong) hơn là nói khó
   với một đứa 8 tuổi (nó đóng trang). Cùng nguyên tắc fail-closed của cổng lộ
   trình và của `SALE_OPEN`.

   ⚠️ NÚT "TÌM HIỂU THÊM" VẪN CÒN Ở CẢ HAI BẬC. Bậc chỉ quyết cái MẶC ĐỊNH, nó
   không khoá gì cả — trẻ nào cũng lật được sang bản kia. Máy đoán sai tuổi thì
   trẻ sửa được bằng một cú bấm, và lựa chọn đó được nhớ.

   ⚠️ CACHE Ở `astroq-user.depth`, NGUỒN SỰ THẬT Ở HỒ SƠ TRÊN SERVER.
   `lab.html` và `select.html` CỐ Ý không nạp SDK Firebase (64,2 KB gzip) nên
   chúng không có token để hỏi server — chúng đọc cache, đúng khuôn
   `astroq-route-gate` / `astroq-map01-seen` đã dựng. Trang CÓ token
   (`dashboard.html`, `profile.html`) lo việc đẩy lên và kéo về.
   ============================================================ */
(function (global) {
  "use strict";

  var JUNIOR = "junior", SENIOR = "senior";
  var BANDS  = [JUNIOR, SENIOR];

  /* Đóng dấu uid: hai đứa trẻ dùng chung một máy thì bậc của đứa trước không
     được đẩy lên hồ sơ của đứa sau. Cùng lý do `astroq-mission-steps` đóng dấu. */
  var LS_SYNC = "astroq-depth-synced";

  var T = {
    vi: {
      ask_h:      "Bạn bao nhiêu tuổi?",
      ask_p:      "Để Comet biết nên giải thích ngắn gọn hay sâu hơn. Đổi lại lúc nào cũng được.",
      band_junior:"8–10 tuổi",
      band_senior:"11 tuổi trở lên",
      lbl_junior: "Giải thích ngắn gọn",
      lbl_senior: "Giải thích sâu hơn",
      hint_junior:"Câu ngắn, ít số. Muốn đọc kỹ thì bấm “Tìm hiểu thêm”.",
      hint_senior:"Phần giải thích dài mở sẵn, kèm số liệu và nguồn."
    },
    en: {
      ask_h:      "How old are you?",
      ask_p:      "So Comet knows whether to keep it short or go deeper. You can change it any time.",
      band_junior:"8–10 years old",
      band_senior:"11 or older",
      lbl_junior: "Short explanations",
      lbl_senior: "Deeper explanations",
      hint_junior:"Short sentences, few numbers. Tap “Learn more” to read further.",
      hint_senior:"The long explanation opens by default, with figures and sources."
    }
  };

  function lang(l) {
    if (l === "en" || l === "vi") return l;
    return (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
  }
  function t(k, l) { return (T[lang(l)] || T.vi)[k] || k; }

  /** Chuẩn hoá về đúng một trong hai bậc. Giá trị lạ → mặc định `junior`. */
  function norm(v) { return v === SENIOR ? SENIOR : JUNIOR; }

  function user() {
    try { return (global.AstroQ && AstroQ.getUser && AstroQ.getUser()) || null; }
    catch (e) { return null; }
  }

  /** Bậc đang dùng. Chưa khai bao giờ → `junior` (xem cảnh báo đầu file). */
  function get() {
    var u = user();
    return norm(u && u.depth);
  }

  /** Đã KHAI bao giờ chưa — khác với "đang ở bậc nào". `select.html` cần phân biệt. */
  function declared() {
    var u = user();
    return !!(u && (u.depth === JUNIOR || u.depth === SENIOR));
  }

  /** Ghi bậc vào hồ sơ trong máy. Trả về bậc đã chuẩn hoá. */
  function set(band) {
    var b = norm(band);
    var u = user() || {};
    u.depth = b;
    try { if (global.AstroQ && AstroQ.setUser) AstroQ.setUser(u); } catch (e) {}
    /* Đổi bậc thì phải đẩy lại lên server, nên xoá dấu đã-đồng-bộ. */
    try { localStorage.removeItem(LS_SYNC); } catch (e) {}
    return b;
  }

  /** Nhận bậc do SERVER trả về (nguồn sự thật) rồi ghi xuống cache. */
  function absorb(serverDepth) {
    if (serverDepth !== JUNIOR && serverDepth !== SENIOR) return get();
    var u = user() || {};
    if (u.depth === serverDepth) return serverDepth;
    u.depth = serverDepth;
    try { if (global.AstroQ && AstroQ.setUser) AstroQ.setUser(u); } catch (e) {}
    return serverDepth;
  }

  /* ── ĐẨY LÊN SERVER MỘT LẦN, gọi từ trang CÓ token ──
     ⚠️ `select.html` ghi bậc nhưng KHÔNG gửi được (không có SDK). Thiếu hàm này
        thì bậc chỉ sống trong một máy, và đổi máy là trẻ 15 tuổi lại nhận bản
        viết cho trẻ 8 tuổi.
     ⚠️ Không bao giờ ném lỗi, không bao giờ chặn giao diện — cùng hợp đồng với
        `js/progress.js`. Hỏng thì lần mở trang sau thử lại. */
  function syncUp(auth, uid) {
    try {
      if (!auth || !auth.updateProfile || !declared()) return Promise.resolve(false);
      var stamp = uid ? String(uid) : "";
      var done = "";
      try { done = localStorage.getItem(LS_SYNC) || ""; } catch (e) {}
      if (done && done === stamp) return Promise.resolve(false);
      var band = get();
      return auth.updateProfile({ depth: band }).then(function (r) {
        if (r && r.ok) { try { localStorage.setItem(LS_SYNC, stamp); } catch (e) {} return true; }
        return false;
      })["catch"](function () { return false; });
    } catch (e) { return Promise.resolve(false); }
  }

  global.AstroQDepth = {
    JUNIOR: JUNIOR, SENIOR: SENIOR,
    all: function () { return BANDS.slice(); },
    norm: norm,
    get: get,
    set: set,
    declared: declared,
    absorb: absorb,
    syncUp: syncUp,
    isSenior: function () { return get() === SENIOR; },
    /** Nhãn bậc để hiện ra ("Giải thích ngắn gọn" / "Giải thích sâu hơn"). */
    label: function (band, l) { return t("lbl_" + norm(band), l); },
    /** Khoảng tuổi của bậc, dùng ở câu hỏi lúc cấp thẻ ID. */
    ageLabel: function (band, l) { return t("band_" + norm(band), l); },
    /** Một câu nói rõ bậc này đổi cái gì — đừng để trẻ đoán. */
    hint: function (band, l) { return t("hint_" + norm(band), l); },
    t: t
  };
})(window);
