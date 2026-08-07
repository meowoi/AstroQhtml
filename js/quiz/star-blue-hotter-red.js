/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-blue-hotter-red",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "So sánh giữa các ngôi sao màu xanh, sao màu vàng và sao màu đỏ, sao nào có nhiệt độ bề mặt nóng nhất?",
       en: "Comparing blue, yellow, and red stars, which stars have the hottest surface temperature?" },
  opts: [
    { vi: "Sao màu xanh dương nóng hơn sao màu vàng và sao màu đỏ",
      en: "Blue stars are hotter than yellow stars, which are hotter than red stars" },
    { vi: "Sao màu đỏ nóng hơn sao màu xanh",
      en: "Red stars are hotter than blue stars" },
    { vi: "Tất cả các sao màu có nhiệt độ hệt như nhau",
      en: "All star colors have identical temperatures" },
    { vi: "Sao màu vàng nóng nhất",
      en: "Yellow stars are the hottest" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Ngược với ngọn lửa thông thường, trong vũ trụ sao màu xanh dương nóng hơn sao màu vàng và sao màu đỏ.",
        en: "Correct! Unlike campfire intuition, in space blue stars are hotter than yellow and red stars." },
  no: { vi: "Chưa đúng. Nhiều người nghĩ màu đỏ nóng nhất, nhưng trong thiên văn học sao màu xanh dương mới là sao nóng nhất.",
        en: "Incorrect. Many think red is hottest, but in astronomy blue stars are the hottest." },
  hint: { vi: "Sao tỏa năng lượng bức xạ ở dải màu xanh nóng hơn nhiều so với màu đỏ.",
          en: "Stars emitting blue radiation burn much hotter than red ones." },
  lv: 1,
  src: "lcoStarColors",
  srcQuote: "Blue stars are hotter than yellow stars, which are hotter than red stars.",
  srcChecked: "2026-08-06"
};
