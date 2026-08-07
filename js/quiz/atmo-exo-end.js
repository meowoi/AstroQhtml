/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-exo-end",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng ngoại lưu (Exosphere) đánh dấu điều gì và có giới hạn độ cao đỉnh cố định hay không?",
       en: "What does the exosphere denote, and does it have a definitive top altitude?" },
  opts: [
    { vi: "Đánh dấu điểm kết thúc của khí quyển và bắt đầu vũ trụ, không có độ cao đỉnh cố định",
      en: "Denotes the end of our atmosphere and beginning of outer space, with no definitive top altitude" },
    { vi: "Kết thúc bằng một ranh giới nhiệt độ đóng băng cố định ở độ cao 100 km",
      en: "Ends at a fixed freezing temperature boundary at 100 km altitude" },
    { vi: "Được ngăn cách bằng một lớp mây dày đặc cố định",
      en: "Separated by a permanent thick cloud barrier" },
    { vi: "Kết thúc đột ngột do trọng lực Trái Đất biến mất hoàn toàn",
      en: "Ends abruptly where Earth's gravity disappears completely" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tầng ngoại lưu đánh dấu sự kết thúc của khí quyển và bắt đầu của vũ trụ nhưng không có độ cao đỉnh cố định.",
        en: "Correct! The exosphere denotes the end of atmosphere and start of space without a definitive top altitude." },
  no: { vi: "Chưa đúng. Khí quyển không có ranh giới cứng, tầng ngoại lưu chuyển tiếp dần vào vũ trụ mà không có độ cao đỉnh cố định.",
        en: "Incorrect. The atmosphere lacks a hard boundary; the exosphere fades into space without a fixed top altitude." },
  hint: { vi: "Khí quyển mờ nhạt dần chứ không kết thúc tại một độ cao cố định.",
          en: "The atmosphere thins out gradually rather than ending at a fixed height." },
  lv: 3,
  src: "nasaGeneralAtmosphere",
  srcQuote: "The exosphere denotes the end of our atmosphere and the beginning of outer space, though there is not a definitive top altitude where the exosphere ends.",
  srcChecked: "2026-08-06"
};
