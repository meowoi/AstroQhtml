/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-atmosphere-dust-redder",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Mức độ bụi hoặc mây trong khí quyển Trái Đất ảnh hưởng như thế nào đến màu sắc Mặt Trăng trong kỳ nguyệt thực?",
       en: "How does dust or clouds in Earth's atmosphere affect the Moon's color during an eclipse?" },
  opts: [
    { vi: "Càng nhiều bụi hoặc mây thì Mặt Trăng càng xuất hiện màu đỏ đậm hơn",
      en: "The more dust or clouds in Earth's atmosphere, the redder the Moon appears" },
    { vi: "Càng nhiều bụi thì Mặt Trăng biến thành màu xanh lục",
      en: "More dust turns the Moon green" },
    { vi: "Bụi và mây làm Mặt Trăng biến mất hoàn toàn vĩnh viễn",
      en: "Dust and clouds make the Moon vanish forever" },
    { vi: "Không có bất kỳ ảnh hưởng nào",
      en: "It has zero effect on color" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Bụi mịn và mây trong khí quyển Trái Đất làm tăng khả năng lọc ánh sáng, khiến đĩa Trăng đỏ sẫm hơn.",
        en: "Correct! Atmospheric dust and cloud particles enhance filtering, making the Moon appear redder." },
  no: { vi: "Chưa đúng. Càng nhiều hạt bụi trong bầu khí quyển thì sắc đỏ của Mặt Trăng càng trở nên đậm hơn.",
        en: "Incorrect. More particles in Earth's atmosphere deepen the reddish hue on the Moon." },
  hint: { vi: "Bụi khí quyển lọc bớt các dải màu khác khiến chỉ còn gam màu đỏ thẫm.",
          en: "Atmospheric dust scatters other colors out, leaving deeper red tones." },
  lv: 2,
  src: "nasaMoonEclipses",
  srcQuote: "The more dust or clouds in Earth's atmosphere during the eclipse, the redder the Moon appears.",
  srcChecked: "2026-08-06"
};
