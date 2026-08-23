/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "orbits-are-ellipses",
  topic: { vi: "QUỸ ĐẠO",
           en: "ORBITS" },
  q: { vi: "Theo NASA, mọi quỹ đạo có hình gì?",
       en: "According to NASA, what shape is every orbit?" },
  opts: [
    { vi: "Hình vuông",
      en: "A square" },
    { vi: "Hình elip (bầu dục)",
      en: "An ellipse (an oval)" },
    { vi: "Đường thẳng",
      en: "A straight line" },
    { vi: "Hình xoắn ốc",
      en: "A spiral" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! NASA nói <b>mọi quỹ đạo đều là hình elip</b>. Vòng tròn hoàn hảo chỉ là một trường hợp riêng — với các hành tinh thì quỹ đạo <b>gần</b> tròn, chứ không tròn hẳn.",
        en: "Right! NASA says <b>all orbits are elliptical</b>. A perfect circle is just a special case - for the planets the orbits are <b>almost</b> circular, not exactly." },
  no: { vi: "Chưa đúng! Sách hay vẽ vòng tròn cho gọn, nhưng NASA nói rõ mọi quỹ đạo là <b>hình elip</b>.",
        en: "Not quite! Textbooks draw circles for simplicity, but NASA is clear that all orbits are <b>ellipses</b>." },
  hint: { vi: "Vòng tròn có phải một hình elip đặc biệt không? Nếu có thì câu \"mọi quỹ đạo là elip\" vẫn đúng cả với quỹ đạo trông như tròn.",
          en: "Is a circle a special ellipse? If so, \"all orbits are ellipses\" still holds even for near-circular ones." },
  lv: 1,
  src: "whatIsAnOrbit",
  srcQuote: "All orbits are elliptical",
  srcChecked: "2026-08-22"
};
