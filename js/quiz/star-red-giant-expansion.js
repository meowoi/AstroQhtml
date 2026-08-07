/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-red-giant-expansion",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Khi phản ứng tổng hợp hydro chuyển ra các lớp vỏ ngoài của ngôi sao, hiện tượng gì sẽ xảy ra?",
       en: "When hydrogen fusion moves into a star's outer layers, what occurs as a result?" },
  opts: [
    { vi: "Làm các lớp vỏ ngoài giãn nở ra và tạo thành sao khổng lồ đỏ",
      en: "Causes outer layers to expand, resulting in a red giant" },
    { vi: "Làm ngôi sao thu nhỏ lại thành lỗ đen ngay lập tức",
      en: "Causes the star to instantly shrink into a black hole" },
    { vi: "Làm ngôi sao nổ tung không để lại vết tích",
      en: "Causes the star to explode leaving zero trace" },
    { vi: "Làm ngôi sao biến thành sao băng đá",
      en: "Turns the star into an icy meteor" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Sự di chuyển phản ứng ra vỏ ngoài khiến ngôi sao giãn nở thành sao khổng lồ đỏ.",
        en: "Correct! Fusion moving outward causes outer layers to expand into a red giant." },
  no: { vi: "Chưa đúng. Phản ứng hạt nhân ở lớp vỏ ngoài làm cho ngôi sao giãn nở lớn ra thành sao khổng lồ đỏ.",
        en: "Incorrect. Outer shell fusion causes the star's layers to expand into a red giant." },
  hint: { vi: "Quá trình này làm kích thước ngôi sao tăng lên gấp nhiều lần.",
          en: "This process causes the star's physical size to expand dramatically." },
  lv: 2,
  src: "nasaStarTypes",
  srcQuote: "Hydrogen fusion begins moving into the star's outer layers, causing them to expand. The result is a red giant",
  srcChecked: "2026-08-06"
};
