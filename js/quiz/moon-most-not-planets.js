/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "moon-most-not-planets",
  topic: { vi: "VỆ TINH TỰ NHIÊN",
           en: "NATURAL SATELLITE" },
  q: { vi: "NASA đếm được 421 vệ tinh quay quanh các hành tinh, và hơn 470 vệ tinh quay quanh hành tinh lùn, tiểu hành tinh và các vật thể ngoài Sao Hải Vương. Vậy điều nào đúng?",
       en: "NASA counts 421 moons orbiting planets, and more than 470 moons orbiting dwarf planets, asteroids and trans-Neptunian objects. So which statement is true?" },
  opts: [
    { vi: "Phần lớn vệ tinh quay quanh các hành tinh",
      en: "Most moons orbit planets" },
    { vi: "Phần lớn vệ tinh KHÔNG quay quanh hành tinh nào",
      en: "Most moons do NOT orbit a planet" },
    { vi: "Chỉ hành tinh mới có vệ tinh",
      en: "Only planets can have moons" },
    { vi: "Hai con số đó bằng nhau",
      en: "The two counts are equal" }
  ],
  a: 1,
  ok: { vi: "Đúng! Hơn 470 nhiều hơn 421, nên <b>quá nửa số vệ tinh đã xác nhận lại quay quanh những thứ không phải hành tinh</b> — hành tinh lùn, tiểu hành tinh và các vật thể ngoài Sao Hải Vương. Có vệ tinh không phải đặc quyền của hành tinh.",
          en: "Yes! More than 470 beats 421, so <b>over half of all confirmed moons orbit things that are not planets</b> — dwarf planets, asteroids and trans-Neptunian objects. Having moons is not a planets-only privilege." },
  no: { vi: "Chưa đúng! Cứ so hai con số: 421 quay quanh hành tinh, <b>hơn 470</b> quay quanh các vật thể khác — vậy phần lớn vệ tinh <b>không</b> thuộc về hành tinh nào.",
          en: "Not quite! Just compare: 421 orbit planets, <b>more than 470</b> orbit other bodies — so most moons <b>don't</b> belong to a planet." },
  hint: { vi: "Đọc kỹ hai con số trong câu hỏi rồi xem bên nào lớn hơn.",
            en: "Read the two numbers in the question, then see which is bigger." },
  lv: 3,
  src: "moon",
  srcQuote: "Of those, 421 moons are orbiting planets (including Pluto). More than 470 moons are orbiting other dwarf planets, asteroids and trans-Neptunian objects (TNOs).",
  srcChecked: "2026-08-19"
};
