/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-definition-moon-between",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Hiện tượng nhật thực (solar eclipse) xảy ra khi nào?",
       en: "When does a solar eclipse happen?" },
  opts: [
    { vi: "Khi Mặt Trăng đi vào giữa Mặt Trời và Trái Đất, đổ bóng lên Trái Đất",
      en: "When the Moon passes between the Sun and Earth, casting a shadow on Earth" },
    { vi: "Khi Trái Đất đi vào giữa Mặt Trời và Mặt Trăng",
      en: "When Earth passes between the Sun and Moon" },
    { vi: "Khi Mặt Trời biến mất vào ban đêm",
      en: "When the Sun vanishes at night" },
    { vi: "Khi một sao băng đâm vào Mặt Trăng",
      en: "When a meteor crashes into the Moon" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Nhật thực xảy ra khi Mặt Trăng di chuyển vào giữa Mặt Trời và Trái Đất, đổ bóng che khuất ánh sáng.",
        en: "Correct! A solar eclipse occurs when the Moon passes between the Sun and Earth, casting its shadow." },
  no: { vi: "Chưa đúng. Vị trí chính xác là Mặt Trăng nằm ở giữa Mặt Trời và Trái Đất.",
        en: "Incorrect. The exact alignment is the Moon positioned between the Sun and Earth." },
  hint: { vi: "Mặt Trăng là vật thể chắn ngang đường đi của ánh sáng Mặt Trời chiếu tới Trái Đất.",
          en: "The Moon is the body that blocks sunlight traveling from the Sun to Earth." },
  lv: 1,
  src: "nasaEclipseTypes",
  srcQuote: "A solar eclipse happens when the Moon passes between the Sun and Earth, casting a shadow on Earth that either fully or partially blocks the Sun's light in some areas.",
  srcChecked: "2026-08-06"
};
