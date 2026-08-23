/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "dsn-three-stations",
  topic: { vi: "BA TRẠM CÁCH NHAU 120 ĐỘ",
           en: "THREE STATIONS, 120 DEGREES APART" },
  q: { vi: "Vì sao Mạng Không Gian Sâu phải có ba trạm đặt cách nhau khoảng 120 độ kinh tuyến quanh thế giới?",
       en: "Why does the Deep Space Network need three sites about 120 degrees apart in longitude?" },
  opts: [
    { vi: "Để chia đều chi phí cho ba quốc gia",
      en: "To share the cost between three countries" },
    { vi: "Để mỗi trạm nghe một loại tàu vũ trụ khác nhau",
      en: "So each site listens to a different kind of spacecraft" },
    { vi: "Để liên lạc được liên tục trong khi Trái Đất quay",
      en: "To permit constant communication as our planet rotates" },
    { vi: "Để tránh mây và mưa làm nhiễu tín hiệu vô tuyến",
      en: "To avoid clouds and rain disturbing the radio signals" }
  ],
  a: 2,
  ok: { vi: "Đúng! NASA nói rõ cái được: <b>cách đặt đó cho phép liên lạc liên tục với tàu vũ trụ trong khi hành tinh của chúng ta quay</b>. Trái Đất quay nên một ăng-ten chỉ nhìn được một con tàu trong một phần của ngày — <b>trước khi tàu lặn xuống chân trời ở trạm này thì trạm khác đã bắt được tín hiệu</b>.",
       en: "Yes! NASA states the benefit plainly: <b>the strategic placement of these sites permits constant communication with spacecraft as our planet rotates</b>. Earth turns, so one antenna can only see a spacecraft for part of the day - <b>before it sinks below the horizon at one site, another has already picked it up</b>." },
  no: { vi: "Chưa đúng! Lý do là <b>Trái Đất QUAY</b>. Một trạm duy nhất thì hết phần ngày của nó là mất dấu con tàu. Ba trạm cách nhau đều nhau quanh thế giới (Goldstone ở California, gần Madrid, và gần Canberra) thì lúc nào cũng có một trạm đang nhìn thấy.",
       en: "Not quite! The reason is that <b>Earth ROTATES</b>. A single site loses the spacecraft when its part of the day ends. Three sites spaced evenly around the world (Goldstone in California, near Madrid, and near Canberra) means one of them is always in view." },
  hint: { vi: "Nghĩ về chuyện gì xảy ra với một ăng-ten ở California sau 12 giờ.",
         en: "Think about what happens to an antenna in California 12 hours later." },
  lv: 3,
  src: "deepSpaceNetwork",
  srcQuote: "The strategic placement of these sites permits constant communication with spacecraft as our planet rotates",
  srcChecked: "2026-08-23"
};
