/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-comp-nitrogen",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Khí nào chiếm tỉ lệ thể tích lớn nhất trong bầu khí quyển Trái Đất?",
       en: "Which gas makes up the largest volume percentage of Earth's atmosphere?" },
  opts: [
    { vi: "Khí Oxy",
      en: "Oxygen" },
    { vi: "Khí Nitơ",
      en: "Nitrogen" },
    { vi: "Khí Carbon dioxide",
      en: "Carbon dioxide" },
    { vi: "Khí Argon",
      en: "Argon" }
  ],
  a: 1,
  ok: { vi: "Chính xác! Khí Nitơ chiếm 78% thể tích không khí Trái Đất.",
        en: "Correct! Nitrogen gas makes up 78% of Earth's atmosphere by volume." },
  no: { vi: "Chưa đúng. Tuy con người cần thở oxy, nhưng khí Nitơ mới chiếm tỉ lệ lớn nhất (78%).",
        en: "Incorrect. Though humans breathe oxygen, nitrogen is the most abundant gas (78%)." },
  hint: { vi: "Khí này chiếm tới hơn 3/4 thể tích bầu khí quyển.",
          en: "This gas accounts for more than three-quarters of the atmosphere." },
  lv: 1,
  src: "nasaEarthFacts",
  srcQuote: "Earth's atmosphere is 78% nitrogen, 21% oxygen and 1% other ingredients.",
  srcChecked: "2026-08-06"
};
