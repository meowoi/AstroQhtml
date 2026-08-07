/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-earth-between-sun-moon",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Vị trí của Trái Đất, Mặt Trời và Mặt Trăng như thế nào khi xảy ra nguyệt thực?",
       en: "How are Earth, the Sun, and the Moon aligned during a lunar eclipse?" },
  opts: [
    { vi: "Trái Đất nằm chính giữa Mặt Trời và Mặt Trăng, đổ bóng lên bề mặt Mặt Trăng",
      en: "Earth is positioned precisely between the Moon and Sun, casting its shadow on the Moon" },
    { vi: "Mặt Trăng nằm ở giữa Mặt Trời và Trái Đất",
      en: "The Moon is positioned between the Sun and Earth" },
    { vi: "Mặt Trời nằm ở giữa Trái Đất và Mặt Trăng",
      en: "The Sun is positioned between Earth and Moon" },
    { vi: "Cả ba nằm vuông góc 90 độ",
      en: "All three form a 90-degree right angle" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Trái Đất nằm chính giữa hai thiên thể còn lại, làm bóng Trái Đất phủ lên Mặt Trăng.",
        en: "Correct! Earth sits precisely between the Sun and Moon, casting its shadow on the Moon." },
  no: { vi: "Chưa đúng. Trong nguyệt thực, Trái Đất là thiên thể đứng ở vị trí giữa.",
        en: "Incorrect. In a lunar eclipse, Earth is the central body in alignment." },
  hint: { vi: "Hành tinh của chúng ta đứng ở giữa chắn ánh sáng chiếu tới Mặt Trăng.",
          en: "Our home planet is in the middle blocking light from hitting the Moon." },
  lv: 1,
  src: "nasaMoonEclipses",
  srcQuote: "When Earth is positioned precisely between the Moon and Sun, Earth's shadow falls upon the surface of the Moon, dimming it and sometimes turning the lunar surface a striking red over the course of a few hours.",
  srcChecked: "2026-08-06"
};
