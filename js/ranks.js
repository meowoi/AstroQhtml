/* ============================================================
   js/ranks.js — 10 BẬC HUẤN LUYỆN PHI HÀNH GIA, CHỖ DUY NHẤT khai báo tên.
   Thêm 31/07/2026. Dùng bởi dashboard.html · profile.html (bậc HIỆN TẠI, qua
   `name()`) · achievements.html (khối "Lộ trình huấn luyện" — CẢ 10 bậc, qua
   `ALL`/`levelOf`/`PER_RANK`) — nạp SAU js/ui-common.js.

   ⚠️ Chú thích này từng ghi "achievements.html (bảng xếp hạng)" từ 31/07/2026 tới
      08/08/2026 trong khi khối đó CHƯA TỒN TẠI — grep `AstroQRanks` ở trang đó ra
      0 kết quả suốt 8 ngày. Hệ quả thật: `ALL`, `levelOf`, `next`, `icon`, `short`
      được export mà **không một chỗ nào gọi**, nên trẻ chỉ thấy bậc mình đang ở và
      không có cách nào biết phía trước còn bậc nào. Một chú thích nói về thứ chưa
      làm đọc ra y như thứ đã làm.

   Tên bậc lấy theo thang huấn luyện thật của phi hành đoàn, do người dùng chốt:
     Rookie · Cadet · Explorer · Navigator · Specialist ·
     Pilot · Commander · Captain · Elite Commander · Legend

   HIỂN THỊ (đã chốt): bản tiếng Việt hiện "Hoa Tiêu (Navigator)", bản tiếng Anh
   chỉ hiện "Navigator". Trẻ 8–15 đọc được nghĩa mà vẫn học được từ gốc tiếng Anh.

   ⚠️ MỐC CẤP ĐỘ SUY RA TỪ MỘT CON SỐ, không gõ cứng 10 mốc. Dự án đã bốn lần trả
      giá cho lỗi "gán cứng con số mà nơi khác mới là nguồn sự thật" (14 icon, 14
      thuật ngữ, 25 câu, 20 mẫu vật). `MAX_LEVEL` phải khớp `Achievements.MaxLevel`
      ở server — `check_pages.py` mục [17] đối chiếu hai bên (phép kiểm đó chỉ có
      từ 08/08/2026; chú thích này ghi "có phép kiểm đối chiếu" từ 31/07 trong khi
      grep `MAX_LEVEL` trong `scratchpad/*.py` ra 0 kết quả — tức con số 50 đã đứng
      cạnh server suốt 8 ngày mà không ai canh).
   ⚠️ MỐC XP TỪNG CẤP KHÔNG NẰM Ở ĐÂY, cố ý. Công thức `100·(n−1)·n/2` là luật chơi
      của `Achievements.XpForLevel`; server trả sẵn cả bảng trong `GET /me/achievements`
      (`levels.xp`). Chép công thức sang đây là hai nơi cùng giữ một luật.
   ⚠️ ĐÂY CHỈ LÀ TÊN. Cấp độ do SERVER tính (`Achievements.Level(xp)`), client
      không tự suy XP → cấp. Cùng phân công như `js/badges.js`: server giữ mốc,
      client giữ tên.
   ============================================================ */
(function (global) {
  "use strict";

  var MAX_LEVEL = 50;                   // khớp Achievements.MaxLevel ở server

  /* Thứ tự trong mảng LÀ thứ tự bậc, từ thấp lên cao. */
  var R = [
    { key: "rookie",          vi: "Tân Binh",           en: "Rookie",          ic: "🌱" },
    { key: "cadet",           vi: "Học Viên",            en: "Cadet",           ic: "🎓" },
    { key: "explorer",        vi: "Nhà Thám Hiểm",       en: "Explorer",        ic: "🧭" },
    { key: "navigator",       vi: "Hoa Tiêu",            en: "Navigator",       ic: "🗺️" },
    { key: "specialist",      vi: "Chuyên Gia",          en: "Specialist",      ic: "🔬" },
    { key: "pilot",           vi: "Phi Công",            en: "Pilot",           ic: "🛩️" },
    { key: "commander",       vi: "Chỉ Huy",             en: "Commander",       ic: "🎖️" },
    { key: "captain",         vi: "Thuyền Trưởng",       en: "Captain",         ic: "⚓" },
    { key: "elite-commander", vi: "Chỉ Huy Tinh Nhuệ",   en: "Elite Commander", ic: "🏅" },
    { key: "legend",          vi: "Huyền Thoại",         en: "Legend",          ic: "👑" }
  ];

  /* Số cấp cho mỗi bậc — CHIA ĐỀU, suy ra chứ không gõ. 50 cấp / 10 bậc = 5. */
  var PER = Math.max(1, Math.round(MAX_LEVEL / R.length));

  /** Cấp thấp nhất của một bậc (bậc 0 luôn bắt đầu ở cấp 1). */
  function levelOf(i) { return i <= 0 ? 1 : i * PER + 1; }

  /** Chỉ số bậc của một cấp độ. Kẹp hai đầu để cấp lạ không làm vỡ trang. */
  function indexOf(level) {
    var lv = Math.max(1, Math.floor(Number(level) || 1));
    var i = Math.floor((lv - 1) / PER);
    return Math.min(R.length - 1, Math.max(0, i));
  }

  function at(level) { return R[indexOf(level)]; }

  /**
   * Tên bậc để HIỆN RA.
   * · lang "vi" → "Hoa Tiêu (Navigator)"
   * · lang "en" → "Navigator"
   * Bản VI ghép cả hai vì đó là quyết định đã chốt; đừng tách thành hai chuỗi i18n
   * riêng, không thì hai nơi sẽ lệch nhau.
   */
  function name(level, lang) {
    var r = at(level);
    return lang === "en" ? r.en : r.vi + " (" + r.en + ")";
  }

  /** Tên NGẮN, cho chỗ hẹp (dòng bảng xếp hạng trên điện thoại). */
  function short(level, lang) {
    var r = at(level);
    return lang === "en" ? r.en : r.vi;
  }

  function icon(level) { return at(level).ic; }

  /** Bậc kế tiếp + cấp cần đạt. Trả null khi đã ở bậc cuối. */
  function next(level) {
    var i = indexOf(level);
    if (i >= R.length - 1) return null;
    return { rank: R[i + 1], level: levelOf(i + 1) };
  }

  global.AstroQRanks = {
    ALL: R, MAX_LEVEL: MAX_LEVEL, PER_RANK: PER,
    at: at, indexOf: indexOf, levelOf: levelOf,
    name: name, short: short, icon: icon, next: next
  };
})(window);
