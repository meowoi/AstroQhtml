/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "earth-eight-light-minutes",
  topic: { vi: "NĂM ÁNH SÁNG",
           en: "THE LIGHT-YEAR" },
  q: { vi: "Đo bằng thước ánh sáng, Trái Đất cách Mặt Trời khoảng bao nhiêu?",
       en: "Measured in light-travel time, how far is Earth from the Sun?" },
  opts: [
    { vi: "Khoảng tám giây ánh sáng",
      en: "About eight light seconds" },
    { vi: "Khoảng tám phút ánh sáng",
      en: "About eight light minutes" },
    { vi: "Khoảng tám giờ ánh sáng",
      en: "About eight light hours" },
    { vi: "Khoảng tám năm ánh sáng",
      en: "About eight light years" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! <b>Khoảng tám phút ánh sáng</b>. Nghĩa là ánh nắng em thấy lúc này đã rời Mặt Trời từ tám phút trước.",
        en: "Right! <b>About eight light minutes</b>. The sunlight you see right now left the Sun eight minutes ago." },
  no: { vi: "Chưa đúng! NASA cho con số <b>khoảng tám phút ánh sáng</b> — còn ngôi sao gần nhất thì hơn <b>bốn NĂM</b> ánh sáng.",
        en: "Not quite! NASA gives <b>about eight light minutes</b> - while the nearest star is over <b>four YEARS</b> away in light." },
  hint: { vi: "Đặt nó cạnh Proxima Centauri (4,25 năm ánh sáng) thì em thấy ngay hệ Mặt Trời nhỏ thế nào.",
          en: "Set it beside Proxima Centauri (4.25 light-years) and you see how small our solar system is." },
  lv: 2,
  src: "lightYear",
  srcQuote: "Earth is about eight light minutes from the Sun.",
  srcChecked: "2026-08-22"
};
