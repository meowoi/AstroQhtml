/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-color-temp-determine",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Yếu tố nào của ngôi sao quyết định màu sắc ánh sáng mà nó phát ra?",
       en: "What property of a star determines the color of light it emits?" },
  opts: [
    { vi: "Nhiệt độ bề mặt của ngôi sao",
      en: "The surface temperature of the star" },
    { vi: "Khoảng cách từ sao tới Trái Đất",
      en: "The distance from the star to Earth" },
    { vi: "Số lượng hành tinh quay quanh sao",
      en: "The number of planets orbiting the star" },
    { vi: "Tốc độ di chuyển của sao",
      en: "The speed at which the star moves" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Nhiệt độ bề mặt ngôi sao trực tiếp quyết định màu sắc ánh sáng phát ra.",
        en: "Correct! A star's surface temperature directly determines its emitted light color." },
  no: { vi: "Chưa đúng. Khoảng cách hay hành tinh không làm đổi màu sao; chính nhiệt độ bề mặt quyết định màu sắc.",
        en: "Incorrect. Distance or planets don't change color; surface temperature determines the color." },
  hint: { vi: "Hãy nghĩ đến nhiệt độ nóng hay nguội của bề mặt ngôi sao.",
          en: "Think about how hot or cool the star's surface is." },
  lv: 1,
  src: "lcoStarColors",
  srcQuote: "The surface temperature of a star determines the color of light it emits.",
  srcChecked: "2026-08-06"
};
