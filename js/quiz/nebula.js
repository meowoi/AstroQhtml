/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "nebula",
  topic: { vi: "TINH VÂN",
           en: "NEBULA" },
  q: { vi: "Các ngôi sao được sinh ra ở đâu?",
       en: "Where are stars born?" },
  opts: [
    { vi: "Trong vành đai tiểu hành tinh",
      en: "In the asteroid belt" },
    { vi: "Trong những đám mây khí và bụi khổng lồ",
      en: "In large clouds of gas and dust" },
    { vi: "Trong lõi của một hành tinh",
      en: "Inside a planet's core" },
    { vi: "Trong đuôi của sao chổi",
      en: "In the tail of a comet" }
  ],
  a: 1,
  ok: { vi: "Chính xác! NASA cho biết các ngôi sao hình thành trong những <b>đám mây khí và bụi khổng lồ</b> gọi là mây phân tử. Mây đầy cụm sao mới sinh còn được gọi là “vườn trẻ của các ngôi sao”.",
        en: "Correct! NASA says stars form in <b>large clouds of gas and dust</b> called molecular clouds. Clouds full of newly formed clusters are called stellar nurseries." },
  no: { vi: "Chưa đúng! Ngôi sao sinh ra trong <b>đám mây khí và bụi</b>, không phải trong đá hay trong lõi hành tinh.",
        en: "Not quite! Stars are born in <b>clouds of gas and dust</b>, not in rock or inside planets." },
  hint: { vi: "Muốn nặn một quả cầu khí khổng lồ thì trước hết phải có… rất nhiều <b>khí</b>.",
          en: "To build a giant ball of gas, you first need a great deal of… <b>gas</b>." },
  src: "star"
};
