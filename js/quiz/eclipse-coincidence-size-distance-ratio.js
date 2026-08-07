/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-coincidence-size-distance-ratio",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Sự trùng hợp ngẫu nhiên nào về kích thước và khoảng cách giúp Mặt Trăng che vừa vặn Mặt Trời trên bầu trời Trái Đất?",
       en: "What coincidence of size and distance ratio allows the Moon to appear the same size as the Sun in Earth's sky?" },
  opts: [
    { vi: "Mặt Trời có đường kính lớn gấp 400 lần Mặt Trăng nhưng cũng ở xa gấp 400 lần",
      en: "The Sun is 400 times the diameter of the Moon, but also 400 times farther away" },
    { vi: "Mặt Trời nhỏ hơn Mặt Trăng 100 lần nhưng ở gần hơn",
      en: "The Sun is 100 times smaller than the Moon but closer" },
    { vi: "Mặt Trăng và Mặt Trời có kích thước thực tế hệt như nhau",
      en: "The Sun and Moon are physically identical in size" },
    { vi: "Mặt Trời cách Trái Đất 10 km",
      en: "The Sun is 10 km from Earth" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tỷ lệ kỳ diệu 400 lần kích thước đi kèm 400 lần khoảng cách khiến đĩa hai thiên thể bằng nhau trên bầu trời.",
        en: "Correct! The 400x size paired with 400x distance makes their angular diameters equal." },
  no: { vi: "Chưa đúng. Tỷ lệ 400 lần đường kính đi cùng 400 lần khoảng cách tạo nên sự trùng hợp này.",
        en: "Incorrect. The twin 400x factors of diameter and distance create this cosmic match." },
  hint: { vi: "Con số kỳ diệu lặp lại ở cả kích thước và khoảng cách là 400.",
          en: "The magic number for both scale and distance factor is 400." },
  lv: 3,
  src: "exploratoriumEclipse",
  srcQuote: "the Sun is 400 times the diameter of the moon. But it's also 400 times farther away from us, and this relationship between size and distance makes the Sun and the moon appear the same size in the sky.",
  srcChecked: "2026-08-06"
};
