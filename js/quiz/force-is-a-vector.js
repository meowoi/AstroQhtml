/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "force-is-a-vector",
  topic: { vi: "BỐN LỰC",
           en: "FOUR FORCES" },
  q: { vi: "NASA gọi lực là một đại lượng vectơ. Nghĩa là lực có những gì?",
       en: "NASA calls force a vector quantity. What does that mean force has?" },
  opts: [
    { vi: "Có cả độ lớn và hướng",
      en: "Both a magnitude and a direction" },
    { vi: "Chỉ có độ lớn",
      en: "Only a magnitude" },
    { vi: "Chỉ có hướng",
      en: "Only a direction" },
    { vi: "Chỉ có màu sắc",
      en: "Only a colour" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! Vectơ nghĩa là có <b>cả độ lớn lẫn hướng</b> — nên nói \"lực 100 đơn vị\" mà không nói hướng thì mới nói được một nửa.",
        en: "Right! A vector has <b>both magnitude and direction</b> - so saying \"a force of 100\" without a direction tells only half the story." },
  no: { vi: "Chưa đúng! Vectơ có <b>cả hai</b>: độ lớn VÀ hướng. Một lực 100 hướng lên và một lực 100 hướng xuống là hai chuyện khác nhau.",
        en: "Not quite! A vector has <b>both</b>: magnitude AND direction. 100 up and 100 down are entirely different things." },
  hint: { vi: "Hai người kéo một sợi dây, mỗi người 100 đơn vị. Sợi dây đi đâu? Câu trả lời phụ thuộc điều gì?",
          en: "Two people pull a rope with 100 units each. Where does the rope go? What does that depend on?" },
  lv: 2,
  src: "fourRocketForces",
  srcQuote: "Forces are vector quantities having both a magnitude and a direction.",
  srcChecked: "2026-08-22"
};
