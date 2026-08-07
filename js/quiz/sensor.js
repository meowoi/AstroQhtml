/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "sensor",
  topic: { vi: "CẢM BIẾN",
           en: "SENSORS" },
  q: { vi: "Byte dùng bộ phận nào để “nhìn thấy” thiên thạch phía trước?",
       en: "Which part does Byte use to 'see' the asteroid ahead?" },
  opts: [
    { vi: "Bánh xe",
      en: "Wheels" },
    { vi: "Pin năng lượng",
      en: "Battery" },
    { vi: "Cảm biến (Sensor)",
      en: "Sensor" },
    { vi: "Loa phát",
      en: "Speaker" }
  ],
  a: 2,
  ok: { vi: "Chuẩn! <b>Cảm biến</b> giúp robot thu thập thông tin về môi trường xung quanh.",
        en: "Exactly! A <b>sensor</b> lets a robot gather information about its surroundings." },
  no: { vi: "Chưa đúng! Robot “nhìn” bằng <b>cảm biến</b>, không phải bộ phận này.",
        en: "Not quite! A robot 'sees' with a <b>sensor</b>, not this part." },
  hint: { vi: "Bộ phận nào giúp robot <b>thu thập thông tin</b> xung quanh?",
          en: "Which part helps a robot <b>gather info</b> around it?" }
};
