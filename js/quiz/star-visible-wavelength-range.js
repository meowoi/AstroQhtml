/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-visible-wavelength-range",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Trong dải ánh sáng nhìn thấy, màu sắc nào có bước sóng dài nhất và màu sắc nào có bước sóng ngắn nhất?",
       en: "In the visible light range, which color has the longest wavelength and which has the shortest?" },
  opts: [
    { vi: "Màu đỏ có bước sóng dài nhất, màu tím có bước sóng ngắn nhất",
      en: "Red has the longest wavelength, while violet has the shortest" },
    { vi: "Màu xanh có bước sóng dài nhất, màu đỏ ngắn nhất",
      en: "Blue has the longest wavelength, red has the shortest" },
    { vi: "Tất cả các màu đều có bước sóng bằng nhau",
      en: "All colors have identical wavelengths" },
    { vi: "Màu vàng có bước sóng ngắn nhất",
      en: "Yellow has the shortest wavelength" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Trong dải quang phổ nhìn thấy, ánh sáng đỏ có bước sóng dài nhất còn tím có bước sóng ngắn nhất.",
        en: "Correct! In visible spectrum, red light has the longest wavelength and violet the shortest." },
  no: { vi: "Chưa đúng. Màu đỏ có bước sóng dài nhất và màu tím có bước sóng ngắn nhất trong dải quang phổ.",
        en: "Incorrect. Red light holds the longest wavelength and violet the shortest in the visible spectrum." },
  hint: { vi: "Màu đỏ nằm ở đầu sóng dài và màu tím ở đầu sóng ngắn.",
          en: "Red sits at the long-wavelength end and violet at the short-wavelength end." },
  lv: 2,
  src: "nasaSpaceplaceMagic",
  srcQuote: "In the visible range, red has the longest wavelength, while violet has the shortest.",
  srcChecked: "2026-08-06"
};
