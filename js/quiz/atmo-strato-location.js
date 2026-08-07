/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-strato-location",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng bình lưu (Stratosphere) là tầng thứ mấy của bầu khí quyển khi đi từ dưới mặt đất lên?",
       en: "Which layer is the stratosphere as you go upward from ground level?" },
  opts: [
    { vi: "Là tầng thứ hai (nằm trên tầng đối lưu)",
      en: "Second layer as you go upward" },
    { vi: "Là tầng đầu tiên sát mặt đất",
      en: "First layer closest to ground" },
    { vi: "Là tầng cao nhất tiếp giáp vũ trụ",
      en: "Highest layer touching space" },
    { vi: "Là tầng ranh giới ngoài cùng",
      en: "Outermost boundary layer" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tầng bình lưu là tầng thứ hai tính từ mặt đất lên, nằm ngay trên tầng đối lưu.",
        en: "Correct! The stratosphere is the second layer going upward, sitting above troposphere." },
  no: { vi: "Chưa đúng. Tầng đối lưu mới là tầng thứ nhất; tầng bình lưu là tầng thứ hai tính từ mặt đất lên.",
        en: "Incorrect. The troposphere is the first layer; the stratosphere is the second layer going up." },
  hint: { vi: "Tầng này nằm ngay phía trên tầng đối lưu nơi có mây mưa.",
          en: "This layer sits directly above the troposphere where rain clouds form." },
  lv: 3,
  src: "ucarStratosphere",
  srcQuote: "The stratosphere is a layer of Earth's atmosphere. It is the second layer of the atmosphere as you go upward.",
  srcChecked: "2026-08-06"
};
