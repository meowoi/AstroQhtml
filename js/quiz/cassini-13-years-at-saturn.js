/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "cassini-13-years-at-saturn",
  topic: { vi: "SAO THỔ & TÀU CASSINI",
           en: "SATURN AND CASSINI" },
  q: { vi: "Tàu Cassini ở lại hệ Sao Thổ trong bao lâu?",
       en: "How long did the Cassini spacecraft stay in the Saturn system?" },
  opts: [
    { vi: "13 ngày",
        en: "13 days" },
    { vi: "13 tuần",
        en: "13 weeks" },
    { vi: "13 tháng",
        en: "13 months" },
    { vi: "13 năm",
        en: "13 years" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! NASA ghi hệ Sao Thổ là <b>nhà của Cassini trong 13 năm</b> — đủ lâu để theo dõi cả những thay đổi mùa của hành tinh.",
        en: "Right! NASA says the Saturn system was <b>Cassini's home for 13 years</b> - long enough to watch the planet's seasons change." },
  no: { vi: "Chưa đúng! Cassini ở đó <b>13 năm</b>, không phải 13 ngày hay 13 tháng.",
        en: "Not quite! Cassini was there for <b>13 years</b>, not 13 days or 13 months." },
  hint: { vi: "Sao Thổ ở rất xa. Một chuyến vài tuần thì còn chưa bay tới nơi.",
          en: "Saturn is very far away. A trip of a few weeks would not even get you there." },
  lv: 2,
  src: "cassini",
  srcQuote: "The Saturn system was Cassini's home for 13 years.",
  srcChecked: "2026-08-22"
};
