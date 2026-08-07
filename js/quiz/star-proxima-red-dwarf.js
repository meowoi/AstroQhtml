/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-proxima-red-dwarf",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Ngôi sao hàng xóm gần Trái Đất nhất ngoài Mặt Trời — Proxima Centauri — thuộc loại sao nào?",
       en: "What type of star is Proxima Centauri, our closest stellar neighbor?" },
  opts: [
    { vi: "Sao lùn đỏ (Red dwarf)",
      en: "Red dwarf" },
    { vi: "Sao khổng lồ xanh",
      en: "Blue giant" },
    { vi: "Sao siêu tân tinh",
      en: "Supernova" },
    { vi: "Lỗ đen",
      en: "Black hole" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Proxima Centauri cách Trái Đất hơn 4 năm ánh sáng là một sao lùn đỏ.",
        en: "Correct! Proxima Centauri, just over 4 light-years away, is a red dwarf." },
  no: { vi: "Chưa đúng. Proxima Centauri là một sao lùn đỏ nhỏ bé nằm ở chòm sao Bán Nhân Mã.",
        en: "Incorrect. Proxima Centauri is a small red dwarf in the Centaurus constellation." },
  hint: { vi: "Đây là loại sao màu đỏ nguội có số lượng đông đảo nhất vũ trụ.",
          en: "This is the most abundant type of cool red star in the universe." },
  lv: 1,
  src: "nasaStarTypes",
  srcQuote: "Our closest stellar neighbor, shown here in this Hubble image, is the red dwarf Proxima Centauri.",
  srcChecked: "2026-08-06"
};
