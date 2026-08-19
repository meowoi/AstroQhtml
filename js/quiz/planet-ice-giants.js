/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "planet-ice-giants",
  topic: { vi: "HÀNH TINH",
           en: "PLANET" },
  q: { vi: "Sao Mộc và Sao Thổ được gọi là hành tinh khí khổng lồ. Còn Sao Thiên Vương và Sao Hải Vương thì NASA gọi là gì?",
       en: "Jupiter and Saturn are called gas giants. So what does NASA call Uranus and Neptune?" },
  opts: [
    { vi: "Hành tinh đá",
      en: "Rocky planets" },
    { vi: "Hành tinh băng khổng lồ",
      en: "Ice giants" },
    { vi: "Hành tinh lùn",
      en: "Dwarf planets" },
    { vi: "Cũng là hành tinh khí khổng lồ",
      en: "Gas giants as well" }
  ],
  a: 1,
  ok: { vi: "Chính xác! <b>Sao Mộc và Sao Thổ là hành tinh khí khổng lồ; Sao Thiên Vương và Sao Hải Vương là hành tinh băng khổng lồ.</b> Cả bốn đều không có bề mặt rắn để đứng lên — chỉ là khí xoáy trên một lõi.",
          en: "Exactly! <b>Jupiter and Saturn are gas giants; Uranus and Neptune are ice giants.</b> None of the four has a hard surface to stand on — just swirling gases above a core." },
  no: { vi: "Chưa đúng! Bốn hành tinh ngoài đều khổng lồ và đều không có mặt đất rắn, nhưng NASA chia làm hai loại: <b>khí</b> (Sao Mộc, Sao Thổ) và <b>băng</b> (Sao Thiên Vương, Sao Hải Vương).",
          en: "Not quite! All four outer planets are giants without hard surfaces, but NASA splits them in two: <b>gas</b> (Jupiter, Saturn) and <b>ice</b> (Uranus, Neptune)." },
  hint: { vi: "Hai hành tinh xa nhất thì lạnh nhất — tên loại của chúng cũng lạnh.",
            en: "The two farthest planets are the coldest — and their group name is cold too." },
  lv: 2,
  src: "planet",
  srcQuote: "Jupiter and Saturn are gas giants. Uranus and Neptune are ice giants.",
  srcChecked: "2026-08-19"
};
