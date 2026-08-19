/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "algorithm",
  topic: { vi: "THUẬT TOÁN",
           en: "ALGORITHMS" },
  q: { vi: "Thuật toán nào giúp Byte rẽ trái để né thiên thạch?",
       en: "Which command turns Byte left to dodge the asteroid?" },
  opts: [
    { vi: "MoveForward()",
      en: "MoveForward()" },
    { vi: "TurnLeft()",
      en: "TurnLeft()" },
    { vi: "Jump()",
      en: "Jump()" },
    { vi: "Stop()",
      en: "Stop()" }
  ],
  a: 1,
  ok: { vi: "Chính xác! Thuật toán <b>TurnLeft()</b> giúp Byte đổi hướng sang trái!",
        en: "Correct! <b>TurnLeft()</b> steers Byte to the left!" },
  no: { vi: "Rất tiếc! <b>MoveForward()</b> sẽ làm Byte đâm thẳng vào thiên thạch đấy. Hãy thử lại!",
        en: "Oops! <b>MoveForward()</b> would crash Byte into the asteroid. Try again!" },
  hint: { vi: "Suy nghĩ kỹ nhé! Thuật toán nào giúp tớ <b>rẽ trái</b>?",
          en: "Think carefully! Which command turns me <b>left</b>?" },
  lv: 2
};
