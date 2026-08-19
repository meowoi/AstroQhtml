/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "sensor-fans-move",
  topic: { vi: "CẢM BIẾN",
           en: "SENSORS" },
  q: { vi: "Robot Astrobee dùng quạt điện để làm gì?",
       en: "What do Astrobee robots use their electric fans for?" },
  opts: [
    { vi: "Để “nhìn” xung quanh",
      en: "To “see” their surroundings" },
    { vi: "Để bay đi trong môi trường vi trọng lực của trạm",
      en: "To fly through the station's microgravity" },
    { vi: "Để làm mát cho các phi hành gia",
      en: "To cool the astronauts down" },
    { vi: "Để gửi tín hiệu về Trái Đất",
      en: "To send signals back to Earth" }
  ],
  a: 1,
  ok: { vi: "Đúng! Astrobee <b>dùng quạt điện làm hệ đẩy để bay tự do trong môi trường vi trọng lực</b> của trạm. Còn việc “nhìn” và định hướng là phần của <b>camera và cảm biến</b> — hai bộ phận, hai việc khác nhau.",
          en: "Yes! Astrobee <b>uses electric fans as a propulsion system to fly freely through the station's microgravity</b>. “Seeing” and navigating is the job of its <b>cameras and sensors</b> — different parts, different jobs." },
  no: { vi: "Chưa đúng! Quạt điện là để <b>di chuyển</b>. Để “nhìn” và tìm đường thì Astrobee dùng <b>camera và cảm biến</b>.",
          en: "Not quite! The fans are for <b>moving</b>. For “seeing” and finding its way, Astrobee uses <b>cameras and sensors</b>." },
  hint: { vi: "Trong không gian không có mặt đất để đạp chân — muốn đi thì phải đẩy không khí.",
            en: "In space there's no floor to push off — to move, you push air." },
  lv: 2,
  src: "astrobee",
  srcQuote: "The robots use electric fans as a propulsion system that allows them to fly freely through the microgravity environment of the station.",
  srcChecked: "2026-08-19"
};
