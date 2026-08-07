/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-phase-new-moon",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Nhật thực chỉ có thể xảy ra trong pha Trăng nào của chu kỳ Mặt Trăng?",
       en: "During which Moon phase can a solar eclipse exclusively occur?" },
  opts: [
    { vi: "Pha Trăng mới (Trăng non)",
      en: "The new moon phase" },
    { vi: "Pha Trăng tròn (Trăng rằm)",
      en: "The full moon phase" },
    { vi: "Pha Trăng bán nguyệt",
      en: "The half moon phase" },
    { vi: "Bất kỳ pha Trăng nào",
      en: "Any moon phase" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Nhật thực chỉ xảy ra ở pha Trăng mới, khi Mặt Trăng nằm về phía Mặt Trời.",
        en: "Correct! Solar eclipses occur exclusively during the new moon phase when aligned toward the Sun." },
  no: { vi: "Chưa đúng. Pha Trăng tròn là thời điểm xảy ra NGUYỆT thực; nhật thực diễn ra ở pha Trăng mới.",
        en: "Incorrect. Full moon is for LUNAR eclipses; solar eclipses require the new moon phase." },
  hint: { vi: "Pha Trăng này là lúc mặt hướng về Trái Đất của Mặt Trăng không được chiếu sáng.",
          en: "In this phase the Moon's Earth-facing side is unlit." },
  lv: 3,
  src: "nasaEclipsesMain",
  srcQuote: "Lunar eclipses occur during the full moon phase, and solar eclipses occur during the new moon phase.",
  srcChecked: "2026-08-06"
};
