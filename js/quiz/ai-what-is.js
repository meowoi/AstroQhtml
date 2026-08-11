/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-what-is",
  topic: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
  q: { vi: "Theo NASA, trí tuệ nhân tạo (AI) là gì?",
       en: "According to NASA, what is artificial intelligence (AI)?" },
  opts: [
    { vi: "Một loại robot có hình dáng giống người",
      en: "A kind of robot shaped like a person" },
    { vi: "Một loại công nghệ giúp máy móc và máy tính có khả năng “suy nghĩ” giống con người",
      en: "A type of technology that helps machines and computers have “thinking” abilities similar to humans" },
    { vi: "Một chương trình chỉ chạy được trên máy tính lượng tử",
      en: "A program that only runs on a quantum computer" },
    { vi: "Một cách gọi khác của Internet",
      en: "Another name for the Internet" }
  ],
  a: 1,
  ok: { vi: "Chính xác! NASA định nghĩa AI là <b>công nghệ</b>, không phải một cái máy cụ thể. Vì thế AI có thể nằm trong một rover, trong điện thoại, hay trong một chương trình xử lý ảnh — không cần hình dáng nào cả.",
        en: "Correct! NASA defines AI as a <b>technology</b>, not a particular machine. So AI can live inside a rover, a phone, or an image-processing program — no body required." },
  no: { vi: "Chưa đúng. AI là một <b>loại công nghệ</b> giúp máy có khả năng “suy nghĩ” giống con người. Robot là cái <i>thân</i>; AI là phần <i>quyết định</i> — nhiều robot không có AI, và rất nhiều AI không có robot nào.",
        en: "Not quite. AI is a <b>type of technology</b> giving machines human-like “thinking” abilities. A robot is the <i>body</i>; AI is the <i>deciding</i> part — many robots have no AI, and most AI has no robot." },
  hint: { vi: "Hỏi xem nó là một CÁI MÁY hay một CÁCH LÀM.",
          en: "Ask whether it is a MACHINE or a METHOD." },
  lv: 1,
  src: "nasaWhatIsAi",
  srcQuote: "Artificial intelligence, or AI, is a type of technology that helps machines and computers have “thinking” abilities similar to humans.",
  srcChecked: "2026-08-09"
};
