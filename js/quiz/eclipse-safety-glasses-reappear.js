/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-safety-glasses-reappear",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Ngay khi một tia ánh sáng Mặt Trời nhỏ nhất xuất hiện trở lại sau pha toàn phần, bạn phải làm gì?",
       en: "What must you do immediately as soon as even a small piece of bright Sun reappears after totality?" },
  opts: [
    { vi: "Đeo ngay kính xem nhật thực chuyên dụng trở lại để bảo vệ mắt",
      en: "Immediately put your eclipse glasses back on or use a handheld solar viewer" },
    { vi: "Tháo kính ra và nhìn chằm chằm vào Mặt Trời",
      en: "Take off your glasses and stare at the Sun" },
    { vi: "Nhắm mắt ngủ trong 2 tiếng",
      en: "Close your eyes and sleep for 2 hours" },
    { vi: "Dùng kính râm thông thường để nhìn",
      en: "Use regular sunglasses to look" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Ngay khi pha toàn phần kết thúc và ánh sáng xuất hiện, phải lập tức đeo lại kính chuyên dụng.",
        en: "Correct! The moment totality ends, specialized solar filters must be worn again instantly." },
  no: { vi: "Chưa đúng. Kính râm thông thường không đủ an toàn; phải dùng kính lọc nhật thực đạt chuẩn.",
        en: "Incorrect. Regular sunglasses are unsafe; certified solar filters are strictly required." },
  hint: { vi: "Ánh sáng Mặt Trời trực tiếp ló ra sau pha toàn phần rất mạnh đối với võng mạc.",
          en: "Direct sunlight emerging post-totality carries intense radiation." },
  lv: 2,
  src: "nasaEclipseSafety",
  srcQuote: "As soon as you see even a little bit of the bright Sun reappear after totality, immediately put your eclipse glasses back on or use a handheld solar viewer to look at the Sun.",
  srcChecked: "2026-08-06"
};
