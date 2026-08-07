/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-comp-ratio",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tỉ lệ thành phần không khí của bầu khí quyển Trái Đất gồm những gì?",
       en: "What is the exact composition breakdown of Earth's atmosphere?" },
  opts: [
    { vi: "78% nitơ, 21% oxy và 1% các thành phần khác",
      en: "78% nitrogen, 21% oxygen and 1% other ingredients" },
    { vi: "78% oxy, 21% nitơ và 1% các khí khác",
      en: "78% oxygen, 21% nitrogen and 1% other ingredients" },
    { vi: "50% oxy, 50% nitơ",
      en: "50% oxygen, 50% nitrogen" },
    { vi: "99% carbon dioxide và 1% oxy",
      en: "99% carbon dioxide and 1% oxygen" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Khí quyển Trái Đất gồm 78% nitơ, 21% oxy và 1% các khí vết.",
        en: "Correct! Earth's atmosphere consists of 78% nitrogen, 21% oxygen and 1% trace gases." },
  no: { vi: "Chưa đúng. Nhiều người hay nhầm oxy chiếm 78%, nhưng thực tế Nitơ mới chiếm 78% và Oxy chiếm 21%.",
        en: "Incorrect. Many confuse the ratio: Nitrogen is actually 78% and Oxygen is 21%." },
  hint: { vi: "Nitơ luôn chiếm tỉ lệ áp đảo lớn hơn Oxy.",
          en: "Nitrogen always holds a far larger majority than oxygen." },
  lv: 1,
  src: "nasaEarthFacts",
  srcQuote: "Earth's atmosphere is 78% nitrogen, 21% oxygen and 1% other ingredients.",
  srcChecked: "2026-08-06"
};
