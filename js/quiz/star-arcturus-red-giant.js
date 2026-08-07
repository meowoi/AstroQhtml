/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-arcturus-red-giant",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Ngôi sao Arcturus trong chòm sao Mục Phu (Boötes) thuộc loại sao nào có thể nhìn thấy bằng mắt thường?",
       en: "Which type of star visible to the unaided eye is Arcturus in Boötes?" },
  opts: [
    { vi: "Sao khổng lồ đỏ (Red giant)",
      en: "Red giant" },
    { vi: "Sao lùn trắng",
      en: "White dwarf" },
    { vi: "Sao neutron",
      en: "Neutron star" },
    { vi: "Sao lùn nâu",
      en: "Brown dwarf" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Arcturus là một sao khổng lồ đỏ tỏa sáng rõ rệt trên bầu trời đêm.",
        en: "Correct! Arcturus is a prominent red giant visible in the night sky." },
  no: { vi: "Chưa đúng. Arcturus là một ngôi sao khổng lồ đỏ đã mở rộng kích thước ở cuối vòng đời.",
        en: "Incorrect. Arcturus is a red giant star that expanded late in its lifecycle." },
  hint: { vi: "Đây là ngôi sao đã giãn nở lớn ra và bề mặt nguội đi chuyển màu đỏ.",
          en: "This star expanded in size and cooled down into a reddish hue." },
  lv: 2,
  src: "nasaStarTypes",
  srcQuote: "Arcturus in the northern constellation Boötes and Gamma Crucis in the southern constellation Crux (the Southern Cross) are red giants visible to the unaided eye.",
  srcChecked: "2026-08-06"
};
