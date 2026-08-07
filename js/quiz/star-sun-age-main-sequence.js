/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-sun-age-main-sequence",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Mặt Trời của chúng ta hiện nay ước tính bao nhiêu tuổi và thuộc nhóm sao nào?",
       en: "How old is our Sun estimated to be, and what group of stars does it belong to?" },
  opts: [
    { vi: "Khoảng 4,6 tỷ năm tuổi, là một sao thuộc dải sao chính",
      en: "About 4.6 billion years old, a main sequence star" },
    { vi: "Khoảng 100 triệu năm tuổi, là sao khổng lồ đỏ",
      en: "About 100 million years old, a red giant" },
    { vi: "Khoảng 1.000 năm tuổi, là sao lùn trắng",
      en: "About 1,000 years old, a white dwarf" },
    { vi: "Mới sinh ra được 1 ngày",
      en: "Formed just 1 day ago" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Mặt Trời khoảng 4,6 tỷ năm tuổi và đang là một ngôi sao thuộc dải sao chính.",
        en: "Correct! Our Sun is ~4.6 billion years old and currently a main sequence star." },
  no: { vi: "Chưa đúng. Mặt Trời là một sao thuộc dải sao chính với tuổi hiện tại khoảng 4,6 tỷ năm.",
        en: "Incorrect. Our Sun is a main sequence star with a current age of 4.6 billion years." },
  hint: { vi: "Mặt Trời đã tồn tại được hơn 4,5 tỷ năm.",
          en: "Our Sun has existed for more than 4.5 billion years." },
  lv: 1,
  src: "nasaStarTypes",
  srcQuote: "NASA's Solar Dynamics Observatory captured this image of our 4.6-billion-year-old Sun, a main sequence star.",
  srcChecked: "2026-08-06"
};
