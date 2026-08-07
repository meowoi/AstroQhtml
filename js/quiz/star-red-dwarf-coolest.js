/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-red-dwarf-coolest",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Đặc điểm về kích thước và nhiệt độ bề mặt của các sao lùn đỏ (Red dwarfs) là gì?",
       en: "What are the characteristics of red dwarfs regarding size and temperature?" },
  opts: [
    { vi: "Là những sao dãy chính nhỏ nhất và nguội nhất",
      en: "They are the smallest main sequence stars and the coolest" },
    { vi: "Là những sao lớn nhất và nóng nhất vũ trụ",
      en: "They are the largest and hottest stars in the universe" },
    { vi: "Là những ngôi sao không tỏa nhiệt",
      en: "They are stars that emit no heat" },
    { vi: "Là những sao màu xanh dương cực nóng",
      en: "They are extremely hot blue stars" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Sao lùn đỏ có kích thước nhỏ và nhiệt độ bề mặt nguội nhất trong dải sao chính.",
        en: "Correct! Red dwarfs are the smallest and coolest main sequence stars." },
  no: { vi: "Chưa đúng. Sao lùn đỏ là những ngôi sao nhỏ bé và có nhiệt độ bề mặt nguội nhất.",
        en: "Incorrect. Red dwarfs are small stars with the coolest surface temperatures." },
  hint: { vi: "Các ngôi sao màu đỏ nằm ở nhóm nhiệt độ thấp nhất trên biểu đồ.",
          en: "Red stars occupy the lowest temperature group on the scale." },
  lv: 1,
  src: "nasaStarTypes",
  srcQuote: "Red dwarfs are the smallest main sequence stars – just a fraction of the Sun's size and mass. They're also the coolest",
  srcChecked: "2026-08-06"
};
