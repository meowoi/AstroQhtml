/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "chatbot-confidently-wrong",
  topic: { vi: "CHATBOT",
           en: "CHATBOTS" },
  q: { vi: "Hỏi cùng một câu nhiều lần và chatbot luôn trả lời giống nhau. Điều đó chứng minh được gì?",
       en: "You ask the same question several times and the chatbot always answers the same. What does that prove?" },
  opts: [
    { vi: "Chứng minh câu trả lời là đúng",
      en: "It proves the answer is correct" },
    { vi: "Chỉ cho biết nó TỰ TIN vào câu đó — mô hình giỏi nhất vẫn có thể sai một cách rất tự tin",
      en: "Only that it is CONFIDENT — even the best model might be confidently wrong" },
    { vi: "Chứng minh nó đã kiểm lại trên Internet",
      en: "It proves the model checked on the Internet" },
    { vi: "Không chứng minh gì, vì nó trả lời ngẫu nhiên",
      en: "Nothing, because its answers are random" }
  ],
  a: 1,
  ok: { vi: "Chính xác. Cách hỏi lặp lại chỉ đo <b>độ tự tin của chính nó</b>, không đo đúng-sai. MIT viết rằng mô hình ngôn ngữ lớn có thể tạo ra câu trả lời <b>nghe đáng tin nhưng không chính xác</b> — nên giọng chắc chắn không phải bằng chứng.",
        en: "Exactly. Repeating the question measures its <b>own self-confidence</b>, not correctness. MIT writes that LLMs can produce <b>credible but inaccurate</b> answers — so a confident tone is not evidence." },
  no: { vi: "Chưa đúng. Trả lời giống nhau nhiều lần chỉ nghĩa là nó <b>tự tin</b>. Đó là lý do MIT đi tìm cách đo một loại bất định khác — vì <i>ngay cả mô hình giỏi nhất cũng có thể sai một cách rất tự tin</i>.",
        en: "Not quite. Repeating the same answer only means it is <b>confident</b>. That is why MIT looked for a different kind of uncertainty to measure — because <i>even the most impressive model might be confidently wrong</i>." },
  hint: { vi: "Tự tin và đúng có phải là một thứ không?",
          en: "Are confidence and correctness the same thing?" },
  lv: 2,
  src: "mitLlmConfident",
  srcQuote: "Even the most impressive LLM might be confidently wrong.",
  srcChecked: "2026-08-23"
};
