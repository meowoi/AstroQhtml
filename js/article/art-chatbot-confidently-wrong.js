/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 3130,
  id: "art-chatbot-confidently-wrong",
  src: "AI & Tech",
  cat: "ai",
  em: "🎭",
  c: ["#ffe0d8", "#d9614a", "#3d1108"],
  img: null,
  credit: null,
  url: "https://news.mit.edu/2026/better-method-identifying-overconfident-large-language-models-0319",
  title: { vi: "Chatbot có thể nói sai mà nghe vẫn rất đáng tin",
          en: "A chatbot can be wrong and still sound convincing" },
  body: {
    vi: ["Khi một người không chắc, thường ta nghe ra được: họ ngập ngừng, họ nói “mình nghĩ là…”. Với chatbot thì dấu hiệu đó không có.",
           "MIT viết rằng mô hình ngôn ngữ lớn <b>có thể tạo ra câu trả lời nghe đáng tin nhưng không chính xác</b>, và <i>ngay cả mô hình giỏi nhất cũng có thể sai một cách rất tự tin</i>. Một cách người ta hay dùng để thử là hỏi cùng một câu nhiều lần xem nó có trả lời giống nhau không — nhưng cách đó chỉ đo <b>độ tự tin của chính nó</b>, chứ không đo đúng-sai. Nên nghe mượt không phải bằng chứng."],
    en: ["When a person is unsure, you can usually hear it: they hesitate, they say “I think…”. With a chatbot that signal is missing.",
           "MIT writes that large language models <b>can generate credible but inaccurate responses</b>, and that <i>even the most impressive one might be confidently wrong</i>. A popular way to test it is asking the same question several times to see whether the answer stays the same — but that only measures <b>its own self-confidence</b>, not whether it is right. Sounding smooth is not evidence."]
  },
  term: { who: "comet",
           word: { vi: "Tự tin ≠ đúng",
                   en: "Confident ≠ correct" },
           text: { vi: "Giọng chắc chắn <b>không</b> phải bằng chứng. Điều gì quan trọng thì đi kiểm ở một nguồn khác — đúng như bọn mình làm với mọi con số trong astroQ. ☄️",
                   en: "A confident tone is <b>not</b> evidence. If it matters, check it against another source — exactly what we do with every number in astroQ. ☄️" } },
  terms: ["chatbot-confidently-wrong"]
};
