/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "cmb",
  topic: { vi: "BỨC XẠ NỀN VŨ TRỤ",
           en: "COSMIC MICROWAVE BACKGROUND" },
  q: { vi: "Bức xạ nền vũ trụ là gì?",
       en: "What is the cosmic microwave background?" },
  opts: [
    { vi: "Ánh sáng của ngôi sao gần Trái Đất nhất",
      en: "Light from the star nearest to Earth" },
    { vi: "Ánh sáng CỔ NHẤT mà ta quan sát được",
      en: "The OLDEST light we can observe" },
    { vi: "Sóng vô tuyến do các kính thiên văn phát ra",
      en: "Radio waves sent out by telescopes" },
    { vi: "Ánh sáng phản chiếu từ bụi trong Ngân Hà",
      en: "Light reflected off dust in the Milky Way" }
  ],
  a: 1,
  ok: { vi: "Chính xác! NASA gọi nó là <b>ánh sáng cổ nhất ta quan sát được</b> — vẫn còn đo được tới hôm nay. Bản đồ của nó cho thấy những chênh lệch nhiệt độ <b>13,8 tỉ năm tuổi</b>, chính là mầm mống lớn dần thành các thiên hà.",
        en: "Correct! NASA calls it the <b>oldest light we can observe</b> — still detectable today. Its map shows <b>13.8-billion-year-old</b> temperature fluctuations: the seeds that grew into galaxies." },
  no: { vi: "Chưa đúng! Đó là <b>ánh sáng cổ nhất</b> ta quan sát được, còn lại từ thuở vũ trụ sơ sinh — không phải ánh sáng của một ngôi sao nào.",
        en: "Not quite! It is the <b>oldest light</b> we can observe, left over from the infant universe — not light from any one star." },
  hint: { vi: "Hãy nghĩ nó như <b>tấm ảnh sơ sinh</b> của cả vũ trụ.",
          en: "Think of it as the universe's <b>newborn photo</b>." },
  lv: 1,
  src: "cosmos"
};
