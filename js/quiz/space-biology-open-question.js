/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "space-biology-open-question",
  topic: { vi: "SINH HỌC KHÔNG GIAN",
           en: "SPACE BIOLOGY" },
  q: { vi: "Đây là một câu mà NASA công bố rằng ngành sinh học không gian CHƯA trả lời xong. Câu nào?",
       en: "Here is a question NASA openly says space biology has NOT finished answering. Which one?" },
  opts: [
    { vi: "Trạm Vũ trụ Quốc tế nặng bao nhiêu?",
      en: "How much does the International Space Station weigh?" },
    { vi: "Có bao nhiêu ngôi sao trong Ngân Hà?",
      en: "How many stars are in the Milky Way?" },
    { vi: "Sao Hoả có bao nhiêu vệ tinh?",
      en: "How many moons does Mars have?" },
    { vi: "Những thay đổi do bay dài là vĩnh viễn, hay giảm dần rồi biến mất khi về Trái Đất?",
      en: "Are the effects of spaceflight permanent, or do they decrease and vanish after return?" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! NASA hỏi thẳng: những thay đổi ấy <b>vĩnh viễn</b>, hay <b>giảm dần rồi biến mất</b> khi về? Để ý cách hỏi — nó chừa chỗ cho cả hai câu trả lời.",
        en: "Right! NASA asks it plainly: are those changes <b>permanent</b>, or do they <b>decrease and vanish</b> after return? Notice the wording - it leaves room for both answers." },
  no: { vi: "Chưa đúng! Ba câu kia đều đã có câu trả lời. Câu NASA còn để mở là về việc những thay đổi khi bay dài có <b>vĩnh viễn</b> hay không.",
        en: "Not quite! The other three are already answered. NASA's open question is whether spaceflight changes are <b>permanent</b>." },
  hint: { vi: "Một câu hỏi khoa học tử tế thì chừa chỗ cho câu trả lời làm mình bất ngờ.",
          en: "A well-posed scientific question leaves room to be surprised by the answer." },
  lv: 2,
  src: "spaceBiology",
  srcQuote: "Are the effects of spaceflight exposure permanent or do they decrease and/or vanish with time upon return?",
  srcChecked: "2026-08-22"
};
