/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "qubit-superposition",
  topic: { vi: "QUBIT LÀ GÌ",
           en: "WHAT A QUBIT IS" },
  q: { vi: "Theo NASA, một qubit biểu diễn được những gì?",
       en: "According to NASA, what can a single qubit represent?" },
  opts: [
    { vi: "Chỉ 0 hoặc 1, y như một bit thường",
      en: "Only a 0 or a 1, just like an ordinary bit" },
    { vi: "Một số 0, một số 1, hoặc một chồng chập của cả hai giá trị",
      en: "A zero, a one, or a superposition of both values" },
    { vi: "Vừa là 0 vừa là 1 cùng một lúc",
      en: "Both a 0 and a 1 at the same time" },
    { vi: "Bất cứ số nào từ 0 tới 1",
      en: "Any number between 0 and 1" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA viết: không như máy tính truyền thống nơi các bit buộc phải mang giá trị 0 hoặc 1, <b>một qubit có thể biểu diễn một số 0, một số 1, hoặc một chồng chập của cả hai giá trị</b>. Hãy để ý ba chữ cuối: NASA nói <b>một chồng chập</b>, chứ <b>không</b> nói \"vừa là 0 vừa là 1\".",
       en: "Yes! NASA writes that unlike traditional computers, in which bits must have a value of either zero or one, <b>a qubit can represent a zero, a one, or a superposition of both values</b>. Note the last words: NASA says <b>a superposition</b>, <b>not</b> \"both a 0 and a 1\"." },
  no: { vi: "Chưa đúng! Cách nói bạn hay gặp là \"qubit vừa là 0 vừa là 1\", nhưng NASA <b>không</b> viết vậy — NASA viết đó là <b>một chồng chập của cả hai giá trị</b>. Không phải bắt bẻ chữ nghĩa: \"vừa cái này vừa cái kia\" nghe như hai thứ nằm cạnh nhau, còn <b>chồng chập là MỘT trạng thái</b>.",
       en: "Not quite! The phrasing you often meet is \"a qubit is both 0 and 1\", but NASA does <b>not</b> write that - NASA writes it is <b>a superposition of both values</b>. This is not nitpicking: \"both this and that\" sounds like two things side by side, whereas <b>a superposition is ONE state</b>." },
  hint: { vi: "Ba lựa chọn nghe rất giống nhau. Chọn đúng cách NASA viết.",
         en: "Three options sound alike. Pick the wording NASA actually uses." },
  lv: 2,
  src: "quail",
  srcQuote: "Unlike traditional computers, in which bits must have a value of either zero or one, a qubit can represent a zero, a one, or a superposition of both values.",
  srcChecked: "2026-08-23"
};
