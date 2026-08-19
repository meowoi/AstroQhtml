/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "supernova-what",
  topic: { vi: "SIÊU TÂN TINH",
           en: "SUPERNOVA" },
  q: { vi: "Siêu tân tinh (supernova) là gì?",
       en: "What is a supernova?" },
  opts: [
    { vi: "Một ngôi sao vừa mới sinh ra",
      en: "A brand-new star that has just been born" },
    { vi: "Một vụ nổ khổng lồ",
      en: "A huge explosion" },
    { vi: "Một hành tinh rất sáng",
      en: "A very bright planet" },
    { vi: "Một loại kính viễn vọng",
      en: "A kind of telescope" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA gọi kết cục ấy đúng bằng một câu: <b>một vụ nổ khổng lồ gọi là siêu tân tinh</b>. Cái tên nghe như “ngôi sao mới”, nhưng thực ra đó là lúc một ngôi sao lớn kết thúc.",
          en: "Yes! NASA names it in one line: <b>a huge explosion called a supernova</b>. The name sounds like “new star”, but it marks the end of a massive one." },
  no: { vi: "Chưa đúng! Siêu tân tinh là <b>một vụ nổ khổng lồ</b> — tên nghe như “ngôi sao mới”, nhưng nó là dấu chấm hết của một ngôi sao lớn.",
          en: "Not quite! A supernova is <b>a huge explosion</b> — the name sounds like “new star”, but it is a massive star's final moment." },
  hint: { vi: "Chuyện xảy ra khi một ngôi sao rất nặng cạn nhiên liệu.",
            en: "It's what happens when a very massive star runs out of fuel." },
  lv: 1,
  src: "star",
  srcQuote: "The result is a huge explosion called a supernova.",
  srcChecked: "2026-08-19"
};
