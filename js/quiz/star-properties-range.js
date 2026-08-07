/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-properties-range",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Các ngôi sao trên bầu trời dao động trong dải phạm vi đa dạng ở những yếu tố nào?",
       en: "In what range of properties do stars in the universe vary?" },
  opts: [
    { vi: "Độ sáng, màu sắc và kích thước",
      en: "Luminosity, color, and size" },
    { vi: "Chỉ khác nhau về hình dạng vuông hay tròn",
      en: "Only differ in square or round shape" },
    { vi: "Tất cả các sao đều giống hệt nhau mọi thông số",
      en: "All stars are identical in every parameter" },
    { vi: "Chỉ khác nhau về số lượng vệ tinh",
      en: "Only differ in number of moons" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Các ngôi sao rất đa dạng về độ sáng, màu sắc và kích thước từ nhỏ đến khổng lồ.",
        en: "Correct! Stars vary widely in luminosity, color, and physical size." },
  no: { vi: "Chưa đúng. Ngôi sao trong vũ trụ có sự chênh lệch lớn về độ sáng, màu sắc và kích cỡ.",
        en: "Incorrect. Cosmos stars vary greatly in brightness, color hue, and scale." },
  hint: { vi: "Ba đặc tính quan trọng nhất khi nhìn vào một ngôi sao trên bầu trời.",
          en: "The three most key observational features of stars." },
  lv: 2,
  src: "nasaStarTypes",
  srcQuote: "They range in luminosity, color, and size – from a tenth to 200 times the Sun's mass",
  srcChecked: "2026-08-06"
};
