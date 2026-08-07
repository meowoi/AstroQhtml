/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-prism-wavelengths",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Lăng kính (prism) có tác dụng gì khi ánh sáng trắng đi xuyên qua nó?",
       en: "What does a prism do when white light passes through it?" },
  opts: [
    { vi: "Tách ánh sáng trắng thành các bước sóng màu sắc khác nhau",
      en: "Separates white light into its different wavelengths" },
    { vi: "Hấp thụ hoàn toàn ánh sáng chiếu vào",
      en: "Absorbs all incoming light completely" },
    { vi: "Biến ánh sáng thành nguồn điện năng",
      en: "Turns light directly into electrical power" },
    { vi: "Làm ánh sáng biến mất không vết tích",
      en: "Makes light vanish leaving no trace" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Lăng kính phân tách ánh sáng trắng thành dải cầu vồng các bước sóng màu sắc.",
        en: "Correct! A prism separates white light into a rainbow spectrum of wavelengths." },
  no: { vi: "Chưa đúng. Lăng kính giúp tán sắc, tách ánh sáng trắng thành các dải bước sóng màu sắc.",
        en: "Incorrect. A prism disperses white light into its component color wavelengths." },
  hint: { vi: "Kết quả tạo nên dải màu cầu vồng khi ánh sáng trắng đi qua lăng kính.",
          en: "This creates a rainbow band when white light enters the prism." },
  lv: 2,
  src: "nasaSpaceplaceMagic",
  srcQuote: "A prism separates white light into its different wavelengths.",
  srcChecked: "2026-08-06"
};
