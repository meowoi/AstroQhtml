/* ============================================================
   badges.js — TÊN + MÔ TẢ + ICON của huy hiệu, song ngữ VI/EN.

   PHÂN CÔNG RÕ RÀNG, đọc trước khi thêm huy hiệu mới:
     · SERVER (AstroqSV/Services/Achievements.cs) giữ **mốc và điều kiện**
       (`goal`, `metric`, `group`) và là nơi DUY NHẤT quyết huy hiệu đã mở.
     · FILE NÀY chỉ giữ phần **hiển thị**: tên, mô tả, emoji.

   Vì sao chia thế: mốc nằm hai nơi thì sớm muộn lệch nhau, mà bên client thì
   ai cũng sửa được bằng DevTools. Ngược lại, tên huy hiệu phải dịch VI/EN nên
   để ở client là hợp lý — server không cần biết ngôn ngữ nào.

   THÊM HUY HIỆU MỚI: thêm dòng vào `Achievements.All` ở server, rồi thêm khoá
   cùng id vào đây. Thiếu ở đây thì trang vẫn chạy và hiện chính id — không vỡ.

     <script src="js/badges.js"></script>
     AstroQBadges.name("first-quiz", "vi")   → "Tân Binh Hiếu Học"
   ============================================================ */
(function (global) {
  "use strict";

  var B = {
    /* ---- Học tập ---- */
    "first-quiz":      { ic:"🎓", vi:{ n:"Tân Binh Hiếu Học", d:"Hoàn thành lượt Quiz đầu tiên." },
                                  en:{ n:"Eager Rookie", d:"Finish your first quiz." } },
    "quiz-correct-10": { ic:"💡", vi:{ n:"Đầu Sáng", d:"Trả lời đúng 10 câu hỏi." },
                                  en:{ n:"Bright Spark", d:"Answer 10 questions correctly." } },
    "quiz-correct-50": { ic:"🧠", vi:{ n:"Bộ Não Thiên Hà", d:"Trả lời đúng 50 câu hỏi." },
                                  en:{ n:"Galaxy Brain", d:"Answer 50 questions correctly." } },
    "quiz-perfect":    { ic:"🎯", vi:{ n:"Không Trượt Phát Nào", d:"Đúng toàn bộ câu trong một lượt Quiz." },
                                  en:{ n:"Flawless Run", d:"Get every question right in one quiz." } },
    "reader-5":        { ic:"📖", vi:{ n:"Người Đọc Sao", d:"Đọc xong 5 bài ở Trạm Tri Thức." },
                                  en:{ n:"Star Reader", d:"Read 5 articles at the Knowledge Station." } },
    "reader-20":       { ic:"📚", vi:{ n:"Thủ Thư Vũ Trụ", d:"Đọc xong 20 bài." },
                                  en:{ n:"Cosmic Librarian", d:"Read 20 articles." } },

    /* ---- Huấn luyện ---- */
    "first-game":      { ic:"🕹️", vi:{ n:"Lần Đầu Ra Trận", d:"Chơi xong một lượt ở Khu Huấn Luyện." },
                                  en:{ n:"First Sortie", d:"Finish one run in the Training Simulator." } },
    "game-10":         { ic:"🎮", vi:{ n:"Học Viên Chăm Chỉ", d:"Chơi 10 lượt huấn luyện." },
                                  en:{ n:"Diligent Cadet", d:"Play 10 training runs." } },
    "game-50":         { ic:"🏅", vi:{ n:"Kỳ Cựu Sân Tập", d:"Chơi 50 lượt huấn luyện." },
                                  en:{ n:"Training Veteran", d:"Play 50 training runs." } },
    "dodge-300":       { ic:"☄️", vi:{ n:"Tay Lái Lụa", d:"Đạt 300 điểm ở Né Thiên Thạch." },
                                  en:{ n:"Silky Pilot", d:"Score 300 in Asteroid Dodge." } },
    "defender-500":    { ic:"🛡️", vi:{ n:"Lá Chắn Sống", d:"Đạt 500 điểm ở Space Defender." },
                                  en:{ n:"Living Shield", d:"Score 500 in Space Defender." } },
    "constellation-1": { ic:"✨", vi:{ n:"Người Vẽ Trời", d:"Ghép xong một chòm sao." },
                                  en:{ n:"Sky Tracer", d:"Complete one constellation." } },

    /* ---- Khám phá ---- */
    "planet-1":        { ic:"🚀", vi:{ n:"Bước Chân Đầu Tiên", d:"Ghé thăm hành tinh đầu tiên." },
                                  en:{ n:"First Steps", d:"Visit your first planet." } },
    "planet-3":        { ic:"🪐", vi:{ n:"Lữ Khách", d:"Ghé thăm 3 hành tinh." },
                                  en:{ n:"Wayfarer", d:"Visit 3 planets." } },
    "planet-8":        { ic:"🌌", vi:{ n:"Đi Khắp Hệ Mặt Trời", d:"Ghé thăm cả 8 hành tinh." },
                                  en:{ n:"Solar System Tourer", d:"Visit all 8 planets." } },
    "collector-100":   { ic:"💜", vi:{ n:"Nhà Sưu Tầm", d:"Thu được 100 Thiên thạch tím." },
                                  en:{ n:"Collector", d:"Collect 100 Purple Meteors." } },
    "collector-500":   { ic:"👑", vi:{ n:"Ông Chủ Mỏ Tím", d:"Thu được 500 Thiên thạch tím." },
                                  en:{ n:"Purple Tycoon", d:"Collect 500 Purple Meteors." } },

    /* ---- Nhiệm vụ ---- */
    "rookie-astronaut":{ ic:"🎖️", vi:{ n:"Phi Hành Gia Tập Sự", d:"Hoàn thành Nhiệm Vụ 01: Hành Tinh Xanh." },
                                  en:{ n:"Rookie Astronaut", d:"Complete Mission 01: The Blue Planet." } },
    "eco-warrior":     { ic:"🌱", vi:{ n:"Chiến Binh Xanh", d:"Phân loại đúng cả 7 hành động NÊN / KHÔNG NÊN làm ở bước Eco-Hero." },
                                  en:{ n:"Eco-Warrior", d:"Sort all 7 Do / Don't actions correctly in the Eco-Hero step." } },

    /* ---- Cấp độ ---- */
    "level-5":         { ic:"⭐", vi:{ n:"Phi Hành Gia Cấp 5", d:"Đạt cấp 5." },
                                  en:{ n:"Level 5 Astronaut", d:"Reach level 5." } },
    "level-10":        { ic:"🌟", vi:{ n:"Phi Công Kỳ Cựu", d:"Đạt cấp 10." },
                                  en:{ n:"Seasoned Pilot", d:"Reach level 10." } },
    "level-20":        { ic:"🏆", vi:{ n:"Thuyền Trưởng Luna", d:"Đạt cấp 20." },
                                  en:{ n:"Captain of Luna", d:"Reach level 20." } }
  };

  /* Nhóm — dùng cho bộ lọc ở achievements.html. Khoá phải khớp `group`
     trong Achievements.All ở server. */
  var GROUPS = {
    learn:   { ic:"📚", vi:"Học tập",    en:"Learning" },
    train:   { ic:"🎮", vi:"Huấn luyện", en:"Training" },
    explore: { ic:"🗺️", vi:"Khám phá",   en:"Exploring" },
    mission: { ic:"🚀", vi:"Nhiệm vụ",   en:"Missions" },
    level:   { ic:"⭐", vi:"Cấp độ",     en:"Levels" }
  };

  function pick(id, lang) {
    var b = B[id];
    if (!b) return null;
    return (lang === "en" ? b.en : b.vi) || b.vi;
  }

  global.AstroQBadges = {
    /** Tên huy hiệu; huy hiệu server có mà đây chưa có tên → trả chính id. */
    name: function (id, lang) { var d = pick(id, lang); return d ? d.n : id; },
    /** Mô tả điều kiện; không có thì chuỗi rỗng (trang vẫn vẽ được). */
    desc: function (id, lang) { var d = pick(id, lang); return d ? d.d : ""; },
    icon: function (id) { return (B[id] && B[id].ic) || "🎖️"; },

    groups: GROUPS,
    groupName: function (key, lang) {
      var g = GROUPS[key];
      return g ? (lang === "en" ? g.en : g.vi) : key;
    },
    groupIcon: function (key) { return (GROUPS[key] && GROUPS[key].ic) || "🎖️"; },

    /** Có tên cho id này chưa — script kiểm thử dùng để soi thiếu/thừa. */
    has: function (id) { return Object.prototype.hasOwnProperty.call(B, id); },
    ids: function () { return Object.keys(B); }
  };
})(window);
