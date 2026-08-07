/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-definition-earth-shadow",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Hiện tượng nguyệt thực (lunar eclipse) xảy ra khi nào?",
       en: "When does a lunar eclipse happen?" },
  opts: [
    { vi: "Khi bóng của Trái Đất che khuất Mặt Trăng",
      en: "When Earth's shadow obscures the Moon" },
    { vi: "Khi bóng của Mặt Trăng che khuất Mặt Trời",
      en: "When the Moon's shadow blocks the Sun" },
    { vi: "Khi Mặt Trăng rơi xuống Trái Đất",
      en: "When the Moon falls onto Earth" },
    { vi: "Khi Mặt Trời ngừng phát sáng",
      en: "When the Sun stops shining" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Nguyệt thực xảy ra khi Trái Đất cản ánh sáng Mặt Trời và đổ bóng lên Mặt Trăng.",
        en: "Correct! A lunar eclipse happens when Earth's shadow obscures the Moon." },
  no: { vi: "Chưa đúng. Nguyệt thực là do bóng của Trái Đất che khuất Mặt Trăng — còn bóng Mặt Trăng che Mặt Trời thì là NHẬT thực.",
        en: "Incorrect. A lunar eclipse is Earth's shadow on the Moon — the Moon's shadow on the Sun is a SOLAR eclipse." },
  hint: { vi: "Trái Đất đóng vai trò làm vật cản ánh sáng chiếu đến Mặt Trăng.",
          en: "Earth acts as the blocking body casting a shadow on the Moon." },
  lv: 1,
  src: "nasaMoonEclipses",
  srcQuote: "During a lunar eclipse, Earth's shadow obscures the Moon.",
  srcChecked: "2026-08-06"
};
