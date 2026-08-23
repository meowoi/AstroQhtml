/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-binary-stars",
  topic: { vi: "AI TÌM SAO ĐÔI",
           en: "AI FINDING BINARY STARS" },
  q: { vi: "AI đã giúp các nhà khoa học tình nguyện tìm ra hơn bao nhiêu cặp sao đôi?",
       en: "AI has helped citizen scientists find more than how many pairs of binary stars?" },
  opts: [
    { vi: "Hơn 100 cặp",
      en: "More than 100 pairs" },
    { vi: "Hơn 10.000 cặp",
      en: "More than 10,000 pairs" },
    { vi: "Hơn 10 triệu cặp",
      en: "More than 10 million pairs" },
    { vi: "Đúng 1.031 cặp",
      en: "Exactly 1,031 pairs" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA cho biết <b>AI đã giúp các nhà khoa học tình nguyện tìm ra hơn 10.000 cặp sao đôi</b>. Hãy để ý cách nói: <b>AI GIÚP họ</b> — máy lọc bớt phần khổng lồ để con người chỉ phải xem phần đáng xem.",
       en: "Yes! NASA says <b>AI has helped citizen scientists find over 10,000 pairs of binary stars</b>. Note the wording: <b>AI HELPED them</b> — the machine narrows the huge pile so people only look at what is worth looking at." },
  no: { vi: "Chưa đúng! Con số NASA đưa ra là <b>hơn 10.000 cặp</b>. (1.031 là số tiểu hành tinh tìm được trong kho ảnh Hubble — một dự án khác.)",
       en: "Not quite! NASA's figure is <b>over 10,000 pairs</b>. (1,031 is the number of asteroids found in the Hubble archive — a different project.)" },
  hint: { vi: "Con số này lớn hơn một nghìn nhưng nhỏ hơn một triệu.",
         en: "The figure is above a thousand but below a million." },
  lv: 1,
  src: "nasaWhatIsAi",
  srcQuote: "For example, AI has helped citizen scientists find over 10,000 pairs of binary stars.",
  srcChecked: "2026-08-23"
};
