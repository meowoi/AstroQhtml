/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "moon-largest",
  topic: { vi: "VỆ TINH TỰ NHIÊN",
           en: "NATURAL SATELLITE" },
  q: { vi: "Vệ tinh lớn nhất trong hệ Mặt Trời là vệ tinh nào?",
       en: "Which is the largest moon in the solar system?" },
  opts: [
    { vi: "Mặt Trăng của Trái Đất",
      en: "Earth's Moon" },
    { vi: "Europa (Sao Mộc)",
      en: "Europa (Jupiter)" },
    { vi: "Titan (Sao Thổ)",
      en: "Titan (Saturn)" },
    { vi: "Ganymede (Sao Mộc)",
      en: "Ganymede (Jupiter)" }
  ],
  a: 3,
  ok: { vi: "Đúng! <b>Ganymede</b> của Sao Mộc là vệ tinh lớn nhất hệ Mặt Trời — theo NASA nó còn <b>lớn hơn cả hành tinh Sao Thuỷ</b>, và là vệ tinh duy nhất có từ trường riêng.",
        en: "Correct! Jupiter's <b>Ganymede</b> is the largest moon in the solar system — NASA notes it is <b>even bigger than the planet Mercury</b>, and it's the only moon with its own magnetic field." },
  no: { vi: "Chưa đúng! Đó là <b>Ganymede</b>, một vệ tinh của Sao Mộc, thậm chí lớn hơn cả Sao Thuỷ.",
        en: "Not quite! It's <b>Ganymede</b>, a moon of Jupiter — larger even than the planet Mercury." },
  hint: { vi: "Nó thuộc Sao Mộc, và to hơn cả <b>một hành tinh</b> thật sự.",
          en: "It belongs to Jupiter — and it's bigger than an actual <b>planet</b>." },
  src: "ganym"
};
