/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-night-side-visibility",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Ai trên Trái Đất có thể quan sát được hiện tượng nguyệt thực khi nó diễn ra?",
       en: "Who on Earth can see a lunar eclipse when it occurs?" },
  opts: [
    { vi: "Bất kỳ ai ở nửa bán cầu đang là ban đêm của Trái Đất, với bầu trời quang mây",
      en: "Anyone on the night side of Earth with clear skies at the right time" },
    { vi: "Chỉ duy nhất một người ở xích đạo",
      en: "Only one single person at the equator" },
    { vi: "Chỉ những người ở cực Bắc vào ban ngày",
      en: "Only people at the North Pole during daytime" },
    { vi: "Không ai trên Trái Đất có thể nhìn thấy",
      en: "Nobody on Earth can see it" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Khác với nhật thực chỉ nhìn được trên một dải hẹp, nguyệt thực quan sát được từ toàn bộ nửa cầu ban đêm.",
        en: "Correct! Unlike narrow solar eclipse paths, lunar eclipses are visible from the entire night hemisphere." },
  no: { vi: "Chưa đúng. Toàn bộ những người nằm ở nửa cầu đang là ban đêm đều có thể ngắm nguyệt thực.",
        en: "Incorrect. Everyone on the night-side half of the globe can view a lunar eclipse." },
  hint: { vi: "Toàn bộ nửa cầu Trái Đất đang là ban đêm có thể quan sát sự kiện này.",
          en: "The entire night-side hemisphere of Earth gets a view of the event." },
  lv: 3,
  src: "exploratoriumCup",
  srcQuote: "You can see a lunar eclipse if you're on the night side of Earth with clear skies at the right time of the event.",
  srcChecked: "2026-08-06"
};
