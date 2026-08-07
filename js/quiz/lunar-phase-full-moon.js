/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-phase-full-moon",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Nguyệt thực chỉ có thể diễn ra vào pha Trăng nào trong tháng?",
       en: "During which Moon phase can a lunar eclipse exclusively occur?" },
  opts: [
    { vi: "Pha Trăng tròn (Trăng rằm)",
      en: "At the full Moon phase" },
    { vi: "Pha Trăng mới (Trăng non)",
      en: "At the new moon phase" },
    { vi: "Pha Trăng lưỡi liềm",
      en: "At the crescent moon phase" },
    { vi: "Bất kỳ pha Trăng nào",
      en: "At any moon phase" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Nguyệt thực chỉ xảy ra vào pha Trăng tròn khi Mặt Trăng nằm đối diện Mặt Trời qua Trái Đất.",
        en: "Correct! Lunar eclipses occur exclusively during the full Moon phase." },
  no: { vi: "Chưa đúng. Nhật thực diễn ra vào Trăng mới, còn nguyệt thực xảy ra vào pha Trăng tròn.",
        en: "Incorrect. Solar eclipses occur at new moon; lunar eclipses occur at full moon." },
  hint: { vi: "Đây là thời điểm Mặt Trăng tròn và sáng nhất trên bầu trời đêm.",
          en: "This is when the Moon is fully illuminated and round in the night sky." },
  lv: 1,
  src: "nasaMoonEclipses",
  srcQuote: "Lunar eclipses occur at the full Moon phase.",
  srcChecked: "2026-08-06"
};
