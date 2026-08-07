/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-coolest-star-temperature",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Trong số các loại sao thuộc dải sao chính, loại sao nào có nhiệt độ bề mặt nguội nhất?",
       en: "Among main sequence stars, which type has the coolest surface temperature?" },
  opts: [
    { vi: "Các sao lùn đỏ (Red dwarfs)",
      en: "Red dwarfs" },
    { vi: "Các sao khổng lồ xanh",
      en: "Blue giants" },
    { vi: "Các sao lùn vàng",
      en: "Yellow dwarfs" },
    { vi: "Các sao siêu tân tinh",
      en: "Supernovas" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Sao lùn đỏ là những sao dải chính nhỏ nhất và có nhiệt độ nguội nhất.",
        en: "Correct! Red dwarfs are the smallest main sequence stars and the coolest." },
  no: { vi: "Chưa đúng. Các sao lùn đỏ chính là những ngôi sao nhỏ nhất và nguội nhất dải chính.",
        en: "Incorrect. Red dwarfs are the smallest and coolest stars on the main sequence." },
  hint: { vi: "Đây là loại sao lùn tỏa ra ánh sáng màu đỏ mờ.",
          en: "This is a dwarf star emitting dim reddish light." },
  lv: 3,
  src: "nasaStarTypes",
  srcQuote: "Red dwarfs are the smallest main sequence stars – just a fraction of the Sun's size and mass. They're also the coolest",
  srcChecked: "2026-08-06"
};
