/* ============================================================
   constellations.js — 4 chòm sao, tên song ngữ. CHỖ DUY NHẤT khai báo tên.

   `key` PHẢI khớp `cons.key` trong mảng `SKY` của game-constellation.html, vì đó
   là khoá dùng ở CẢ ba nơi: `PROGRESS.consts` trên server, `astroq-constellation-best`
   trong máy, và điều kiện `const:<key>` của Services/Specimens.cs.

   ⚠️ Bản đầu của achievements.html dùng TÊN TIẾNG VIỆT làm khoá ("Đại Hùng") nên
   bộ sưu tập luôn hiện 0/4 với người chơi thật. Đừng lặp lại: khoá là id.

   Tách ra file riêng (29/07/2026) khi trang Kho Mẫu Vật cần tên chòm sao thứ ba —
   copy 4 dòng dữ liệu sang trang thứ ba là chắc chắn có ngày ba bên lệch nhau.

     <script src="js/constellations.js"></script>
     AstroQConsts.all()  ·  AstroQConsts.name("orion", "vi")   → "Lạp Hộ"
   ============================================================ */
(function (global) {
  "use strict";

  var CONSTS = [
    { key: "ursa-major", vi: "Đại Hùng",  en: "Ursa Major" },
    { key: "cassiopeia", vi: "Thiên Hậu", en: "Cassiopeia" },
    { key: "orion",      vi: "Lạp Hộ",    en: "Orion" },
    { key: "scorpius",   vi: "Bọ Cạp",    en: "Scorpius" }
  ];

  global.AstroQConsts = {
    all: function () { return CONSTS.slice(); },
    count: CONSTS.length,
    /** Chòm sao lạ (dữ liệu cũ) → trả chính key, không vỡ trang. */
    name: function (key, lang) {
      for (var i = 0; i < CONSTS.length; i++) {
        if (CONSTS[i].key === key) return lang === "en" ? CONSTS[i].en : CONSTS[i].vi;
      }
      return key;
    }
  };
})(window);
