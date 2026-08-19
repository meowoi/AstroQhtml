/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "nebula-planetary",
  topic: { vi: "TINH VÂN",
           en: "NEBULA" },
  q: { vi: "“Tinh vân hành tinh” (planetary nebula) thực ra là gì?",
       en: "What is a “planetary nebula” actually?" },
  opts: [
    { vi: "Đám mây khí bụi do một ngôi sao già thổi các lớp ngoài của mình bay ra",
      en: "The cloud of gas and dust an aging star blows off from its outer layers" },
    { vi: "Một đám mây đang tạo ra các hành tinh mới",
      en: "A cloud that is making new planets" },
    { vi: "Vành đai bụi quanh một hành tinh",
      en: "A dust ring around a planet" },
    { vi: "Một hành tinh lớn bị bao trong sương mù",
      en: "A large planet wrapped in fog" }
  ],
  a: 0,
  ok: { vi: "Đúng — và đây là cái tên gây hiểu lầm bậc nhất trong thiên văn! NASA cho biết cuối đời một ngôi sao, <b>toàn bộ các lớp ngoài của nó bay đi, tạo thành một đám mây khí bụi đang giãn ra gọi là tinh vân hành tinh</b>. Nó <b>chẳng liên quan gì tới hành tinh</b> — chỉ vì qua kính thời xưa nó trông tròn như một hành tinh.",
          en: "Yes — and it's astronomy's most misleading name! NASA says that at the end of a star's life <b>all its outer layers blow away, creating an expanding cloud of dust and gas called a planetary nebula</b>. It has <b>nothing to do with planets</b> — early telescopes just made it look round like one." },
  no: { vi: "Chưa đúng! Cái tên rất dễ lừa: tinh vân hành tinh <b>không tạo ra hành tinh nào</b>. Đó là <b>các lớp ngoài mà một ngôi sao sắp tàn thổi bay ra</b>.",
          en: "Not quite! The name is a trap: a planetary nebula <b>makes no planets</b>. It is <b>the outer layers a dying star has blown away</b>." },
  hint: { vi: "Đừng tin cái tên — hãy hỏi ngôi sao đang ở giai đoạn nào của đời mình.",
            en: "Don't trust the name — ask what stage of life the star is in." },
  lv: 2,
  src: "star",
  srcQuote: "Eventually, all the star's outer layers blow away, creating an expanding cloud of dust and gas called a planetary nebula.",
  srcChecked: "2026-08-19"
};
