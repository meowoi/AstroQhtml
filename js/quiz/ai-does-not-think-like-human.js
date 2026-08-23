/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-does-not-think-like-human",
  topic: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
  q: { vi: "Một hệ AI giải được những bài toán rất phức tạp. Vậy có phải nó suy nghĩ giống con người?",
       en: "An AI system can work through very complex problems. Does that mean it thinks like a human?" },
  opts: [
    { vi: "Có, vì bên trong nó cũng có nơ-ron y như não người",
      en: "Yes — inside it has neurons just like a human brain" },
    { vi: "Có, miễn là nó trả lời được mọi câu hỏi mình đặt ra",
      en: "Yes, as long as it can answer any question you ask" },
    { vi: "Không — nó suy luận được vấn đề rất phức tạp, nhưng KHÔNG nghĩ theo cách con người nghĩ",
      en: "No — it can reason about very complex problems, but it does NOT think the way a human does" },
    { vi: "Không, vì nó chỉ làm được toán chứ không làm được gì khác",
      en: "No, because it can only do arithmetic and nothing else" }
  ],
  a: 2,
  ok: { vi: "Chính xác, và đây là chỗ rất dễ hiểu sai. AI dựng nên <b>biểu diễn</b> của thế giới rồi chạy các bước suy luận trên đó. Giải được bài khó <b>không</b> có nghĩa là nó nghĩ giống mình — <i>làm được cùng một việc</i> khác với <i>làm theo cùng một cách</i>.",
        en: "Exactly, and this is easy to get wrong. An AI builds <b>representations</b> of the world and runs reasoning steps over them. Solving hard problems does <b>not</b> mean it thinks as we do — <i>same result</i> is not <i>same method</i>." },
  no: { vi: "Chưa đúng. AI4K12 nói rõ: AI suy luận được vấn đề rất phức tạp, <b>nhưng không nghĩ theo cách con người nghĩ</b>. “Nơ-ron” trong máy chỉ là <i>phép tính đặt tên theo</i> nơ-ron thật, không phải cùng một thứ.",
        en: "Not quite. AI4K12 is explicit: AI can reason about very complex problems, <b>but it does not think the way a human does</b>. A machine “neuron” is only a <i>calculation named after</i> a real one, not the same thing." },
  hint: { vi: "Giải được cùng một bài có bắt buộc phải giải theo cùng một cách không?",
          en: "Does solving the same problem require solving it the same way?" },
  lv: 3,
  src: "ai4k12Reasoning",
  srcQuote: "While AI agents can reason about very complex problems, they do not think the way a human does.",
  srcChecked: "2026-08-23"
};
