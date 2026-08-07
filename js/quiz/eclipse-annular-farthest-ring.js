/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-annular-farthest-ring",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Hiện tượng nhật thực hình khuyên (annular solar eclipse) xảy ra khi nào?",
       en: "When does an annular solar eclipse happen?" },
  opts: [
    { vi: "Khi Mặt Trăng ở điểm xa Trái Đất nhất nên trông nhỏ hơn Mặt Trời, tạo thành vòng lửa xung quanh",
      en: "When the Moon is at or near its farthest point from Earth, creating a bright ring around it" },
    { vi: "Khi Mặt Trăng tiến cực gần Trái Đất che kín hoàn toàn Mặt Trời",
      en: "When the Moon is extremely close to Earth completely covering the Sun" },
    { vi: "Khi Mặt Trăng biến thành màu đỏ thẫm",
      en: "When the Moon turns deep red" },
    { vi: "Khi Trái Đất che khuất hoàn toàn Mặt Trăng",
      en: "When Earth fully blocks the Moon" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Do Mặt Trăng ở xa Trái Đất nên đường kính biểu kiến nhỏ hơn, tạo ra dải vành lửa xung quanh.",
        en: "Correct! Because the Moon is farther, it appears smaller than the Sun, creating a ring of fire." },
  no: { vi: "Chưa đúng. Nhật thực hình khuyên xuất hiện khi Mặt Trăng ở xa Trái Đất nên không che hết đĩa Mặt Trời.",
        en: "Incorrect. An annular eclipse happens when the Moon is farther away, leaving a visible outer ring." },
  hint: { vi: "Khoảng cách xa khiến đĩa Mặt Trăng trông nhỏ hơn đĩa Mặt Trời.",
          en: "Greater distance makes the Moon's disk appear smaller than the Sun's disk." },
  lv: 1,
  src: "nasaEclipseTypes",
  srcQuote: "An annular solar eclipse happens when the Moon passes between the Sun and Earth, but when it is at or near its farthest point from Earth.",
  srcChecked: "2026-08-06"
};
