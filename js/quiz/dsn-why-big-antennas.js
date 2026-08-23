/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "dsn-why-big-antennas",
  topic: { vi: "NGHE TÍN HIỆU TỪ XA",
           en: "LISTENING ACROSS SPACE" },
  q: { vi: "Vì sao ăng-ten của Mạng Không Gian Sâu trên Trái Đất phải làm thật lớn?",
       en: "Why must the Deep Space Network's antennas on Earth be so large?" },
  opts: [
    { vi: "Vì tàu vũ trụ chỉ có ăng-ten nhỏ nên tín hiệu về tới đây rất yếu",
      en: "Because spacecraft carry only small antennas, so their signals arrive very weak" },
    { vi: "Vì cần đủ khoẻ để chịu được gió bão trên mặt đất",
      en: "Because they must survive strong winds on the ground" },
    { vi: "Vì ăng-ten lớn thì gửi tín hiệu đi nhanh hơn",
      en: "Because a bigger antenna sends signals faster" },
    { vi: "Vì phải nhìn thấy được tàu vũ trụ bằng mắt thường",
      en: "Because the spacecraft must be visible to the naked eye" }
  ],
  a: 0,
  ok: { vi: "Đúng! NASA nói rõ: <b>ăng-ten nhỏ trên tàu vũ trụ chỉ phát được những tín hiệu vô tuyến yếu về Trái Đất</b>, và <b>tàu càng ở xa thì càng cần ăng-ten lớn hơn để bắt được tín hiệu</b>. Nên phần khó không nằm ở việc GỬI, mà ở việc NGHE — ăng-ten lớn nhất ở mỗi trạm rộng 70 mét.",
       en: "Yes! NASA is explicit: <b>small antennas on the spacecraft can beam weak radio signals back to Earth</b>, and <b>the farther away a spacecraft is, the larger the antenna you need to detect its signal</b>. The hard part is not SENDING but LISTENING — the largest antenna at each site is 70 metres across." },
  no: { vi: "Chưa đúng! Lý do là <b>độ yếu của tín hiệu</b>: tàu vũ trụ mang được ăng-ten nhỏ thôi, nên tín hiệu về tới đây rất yếu — và càng xa thì càng cần ăng-ten thu lớn hơn.",
       en: "Not quite! The reason is <b>signal weakness</b>: a spacecraft can only carry a small antenna, so its signal arrives very weak — and the farther it is, the bigger the receiving dish has to be." },
  hint: { vi: "Nghĩ xem đầu nào mang được ăng-ten to: con tàu, hay Trái Đất?",
         en: "Which end can afford a huge dish: the spacecraft, or Earth?" },
  lv: 3,
  src: "dsnAntennas",
  srcQuote: "Small antennas on the spacecraft can beam weak radio signals back to Earth. The farther away a spacecraft is, the larger the antenna you need to detect its signal.",
  srcChecked: "2026-08-23"
};
