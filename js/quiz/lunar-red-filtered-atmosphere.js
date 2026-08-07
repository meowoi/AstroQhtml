/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-red-filtered-atmosphere",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Tại sao Mặt Trăng lại chuyển sang màu đỏ hoặc cam rực rỡ trong kỳ nguyệt thực toàn phần?",
       en: "Why does the Moon appear red or orange during a total lunar eclipse?" },
  opts: [
    { vi: "Vì ánh sáng Mặt Trời được lọc qua một lớp dày khí quyển Trái Đất trước khi tới Mặt Trăng",
      en: "Because any sunlight that's not blocked by our planet is filtered through a thick slice of Earth's atmosphere on its way to the lunar surface" },
    { vi: "Vì Mặt Trăng bị thiêu rụi bởi lửa",
      en: "Because the Moon burns in fire" },
    { vi: "Vì Mặt Trăng đổi sang màu sơn đỏ",
      en: "Because the Moon changes its paint color" },
    { vi: "Vì Mặt Trời sơn màu đỏ lên vũ trụ",
      en: "Because the Sun paints space red" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Ánh sáng Mặt Trời khúc xạ qua lớp khí quyển Trái Đất được lọc giữ lại dải đỏ cam chiếu lên đĩa Trăng.",
        en: "Correct! Sunlight refracts and filters through Earth's thick atmosphere onto the Moon." },
  no: { vi: "Chưa đúng. Khí quyển Trái Đất đóng vai trò bộ lọc, tán xạ sắc xanh và bẻ cong dải ánh sáng đỏ.",
        en: "Incorrect. Earth's atmosphere acts as a filter scattering blue and bending red light." },
  hint: { vi: "Chính bầu khí quyển Trái Đất lọc ánh sáng trước khi nó rọi tới Mặt Trăng.",
          en: "Earth's atmospheric layer filters the light traveling toward the Moon." },
  lv: 2,
  src: "nasaMoonEclipses",
  srcQuote: "During a lunar eclipse, the Moon appears red or orange because any sunlight that's not blocked by our planet is filtered through a thick slice of Earth's atmosphere on its way to the lunar surface.",
  srcChecked: "2026-08-06"
};
