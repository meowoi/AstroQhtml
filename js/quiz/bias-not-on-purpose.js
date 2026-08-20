/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "bias-not-on-purpose",
  topic: { vi: "THIÊN LỆCH THUẬT TOÁN",
           en: "ALGORITHMIC BIAS" },
  q: { vi: "Ở chương trình của MIT, thiên lệch thuật toán được nêu ra như là gì?",
       en: "In MIT's programme, algorithmic bias is presented as what?" },
  opts: [
    { vi: "Một môn học riêng, học sau khi đã học xong phần kỹ thuật",
      en: "A separate subject, studied after finishing the technical part" },
    { vi: "Một lỗi lập trình có thể sửa bằng một dòng lệnh",
      en: "A coding bug fixable with one line of code" },
    { vi: "Một hệ quả về đạo đức do chính các khái niệm kỹ thuật kéo theo",
      en: "An ethical implication entailed by the technical concepts themselves" },
    { vi: "Một chuyện chỉ xảy ra khi người viết cố tình làm vậy",
      en: "Something that only happens when the author does it on purpose" }
  ],
  a: 2,
  ok: { vi: "Đúng! MIT dạy các khái niệm kỹ thuật <b>cùng với</b> những hệ quả đạo đức mà chính chúng kéo theo, ví dụ như thiên lệch thuật toán. Nghĩa là không có chỗ nào để tách ra: bạn dạy máy bằng cách cho nó xem ví dụ, và những ví dụ bạn chọn đã là một lựa chọn rồi.",
        en: "Yes! MIT teaches technical concepts <b>together with</b> the ethical implications they entail, such as algorithmic bias. So there is no place to separate them: you teach a machine by showing it examples, and the examples you pick are already a choice." },
  no: { vi: "Chưa đúng. MIT nêu thiên lệch thuật toán như một <b>hệ quả đạo đức do chính phần kỹ thuật kéo theo</b>, không phải một môn học riêng dạy sau. Và nó không cần ai cố ý: máy học đúng thứ nó được cho xem.",
        en: "Not quite. MIT presents algorithmic bias as an <b>ethical implication entailed by the technical part itself</b>, not a separate subject taught afterwards. And it needs nobody's intent: a machine learns exactly what it was shown." },
  hint: { vi: "Nếu phải cố ý thì mới thiên lệch, thì một cái máy vô tri sao lại thiên lệch được?",
          en: "If bias required intent, how could a mindless machine ever be biased?" },
  lv: 3,
  src: "mitAlgorithms",
  srcQuote: "such as algorithmic bias",
  srcChecked: "2026-08-20"
};
