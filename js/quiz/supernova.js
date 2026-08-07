/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "supernova",
  topic: { vi: "SIÊU TÂN TINH",
           en: "SUPERNOVA" },
  q: { vi: "Siêu tân tinh xảy ra khi nào?",
       en: "When does a supernova happen?" },
  opts: [
    { vi: "Khi hai hành tinh đâm vào nhau",
      en: "When two planets crash into each other" },
    { vi: "Khi một sao chổi lao vào Mặt Trời",
      en: "When a comet dives into the Sun" },
    { vi: "Khi một ngôi sao khối lượng lớn cạn nhiên liệu và lõi sụp xuống",
      en: "When a massive star runs out of fuel and its core collapses" },
    { vi: "Mỗi lần một ngôi sao mọc lên ở chân trời",
      en: "Every time a star rises over the horizon" }
  ],
  a: 2,
  ok: { vi: "Chính xác! Ngôi sao khối lượng lớn cạn nhiên liệu thì <b>lõi sắt sụp xuống</b> cho tới lúc lực giữa các hạt nhân “đạp phanh”, rồi <b>nảy trở lại</b> — cú nảy đó tạo sóng xung kích và một vụ nổ khổng lồ.",
        en: "Correct! When a high-mass star runs out of fuel its <b>iron core collapses</b> until forces between the nuclei push the brakes, then it <b>rebounds</b> — creating a shock wave and a huge explosion." },
  no: { vi: "Chưa đúng! Siêu tân tinh là lúc một <b>ngôi sao rất lớn</b> kết thúc cuộc đời, không phải chuyện hành tinh hay sao chổi.",
        en: "Not quite! A supernova is how a <b>very massive star</b> ends its life — not a planet or comet event." },
  hint: { vi: "Nó là <b>cái chết</b> của một ngôi sao rất lớn, không phải một vụ đâm nhau.",
          en: "It is the <b>death</b> of a very massive star, not a crash." },
  src: "star"
};
