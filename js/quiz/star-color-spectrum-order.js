/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-color-spectrum-order",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Thứ tự dải màu sắc của các ngôi sao từ NÓNG NHẤT đến NGUỘI NHẤT xếp theo chiều nào?",
       en: "What is the correct order of star colors from HOTTEST to COOLEST?" },
  opts: [
    { vi: "Sao xanh dương → Sao vàng → Sao đỏ",
      en: "Blue stars → Yellow stars → Red stars" },
    { vi: "Sao đỏ → Sao vàng → Sao xanh dương",
      en: "Red stars → Yellow stars → Blue stars" },
    { vi: "Sao vàng → Sao đỏ → Sao xanh dương",
      en: "Yellow stars → Red stars → Blue stars" },
    { vi: "Sao đỏ → Sao xanh dương → Sao vàng",
      en: "Red stars → Blue stars → Yellow stars" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Thứ tự giảm dần nhiệt độ là Sao xanh dương (nóng nhất) → Sao vàng (trung bình) → Sao đỏ (nguội nhất).",
        en: "Correct! Temperature decreases from Blue stars (hottest) → Yellow stars (moderate) → Red stars (coolest)." },
  no: { vi: "Chưa đúng. Sao xanh dương nóng nhất, tiếp đến sao vàng và nguội nhất là sao đỏ.",
        en: "Incorrect. Blue stars are hottest, followed by yellow stars, and red stars are coolest." },
  hint: { vi: "Sao xanh dương có nhiệt độ cao nhất và sao đỏ có nhiệt độ thấp nhất.",
          en: "Blue stars have the highest temperature and red stars the lowest." },
  lv: 1,
  src: "lcoStarColors",
  srcQuote: "Blue stars are hotter than yellow stars, which are hotter than red stars.",
  srcChecked: "2026-08-06"
};
