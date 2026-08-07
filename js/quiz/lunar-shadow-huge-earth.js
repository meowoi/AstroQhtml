/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-shadow-huge-earth",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Đặc điểm kích thước bóng của Trái Đất đổ lên Mặt Trăng khi xảy ra nguyệt thực là gì?",
       en: "What is the size characteristic of Earth's shadow cast onto the Moon during a lunar eclipse?" },
  opts: [
    { vi: "Bóng của Trái Đất đổ lên Mặt Trăng rất khổng lồ",
      en: "The shadow cast by the earth onto the moon is huge!" },
    { vi: "Bóng của Trái Đất nhỏ như một hạt cát",
      en: "The shadow is as small as a grain of sand" },
    { vi: "Bóng của Trái Đất có hình tam giác nhỏ",
      en: "The shadow is a small triangle" },
    { vi: "Trái Đất không tạo ra bóng nào cả",
      en: "Earth casts no shadow at all" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Vì Trái Đất lớn hơn Mặt Trăng rất nhiều, bóng Trái Đất đổ vào không gian vô cùng rộng lớn.",
        en: "Correct! Because Earth is much larger than the Moon, its shadow in space is huge." },
  no: { vi: "Chưa đúng. Trái Đất có kích thước lớn nên nón bóng tối đổ ra không gian vô cùng khổng lồ.",
        en: "Incorrect. Earth's large physical size produces a massive shadow cone in space." },
  hint: { vi: "Trái Đất lớn hơn Mặt Trăng rất nhiều.",
          en: "Earth is much larger than the Moon." },
  lv: 3,
  src: "exploratoriumCup",
  srcQuote: "The shadow cast by the earth onto the moon is huge!",
  srcChecked: "2026-08-06"
};
