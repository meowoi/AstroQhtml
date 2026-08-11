/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "algorithm-is-an-opinion",
  topic: { vi: "THUẬT TOÁN",
           en: "ALGORITHMS" },
  q: { vi: "MIT Media Lab dạy học sinh trung học cơ sở nghĩ về thuật toán như là gì?",
       en: "MIT Media Lab teaches middle school students to think of algorithms as what?" },
  opts: [
    { vi: "Như những sự thật không thể tranh luận",
      en: "As facts that cannot be argued with" },
    { vi: "Như những ý kiến",
      en: "As opinions" },
    { vi: "Như những phép tính luôn cho ra một đáp án duy nhất",
      en: "As sums that always give one single answer" },
    { vi: "Như những bí mật không ai được biết",
      en: "As secrets nobody may know" }
  ],
  a: 1,
  ok: { vi: "Chính xác! MIT dạy học sinh nghĩ về thuật toán như <b>những ý kiến</b>. Vì mỗi thuật toán đều do người viết, và người viết phải chọn: cái gì quan trọng, xếp cái nào lên trước. Một ý kiến thì luôn là ý kiến CỦA AI ĐÓ — và luôn có thể khác đi.",
        en: "Exactly! MIT teaches students to think of algorithms as <b>opinions</b>. Because every algorithm is written by people, and those people must choose: what counts as important, what gets ranked first. An opinion always belongs to SOMEONE — and could always have been otherwise." },
  no: { vi: "Chưa đúng. MIT dạy học sinh nghĩ về thuật toán như <b>những ý kiến</b>. Nghe lạ, nhưng thử nghĩ: thuật toán gợi ý video nên phục vụ ai — người xem, người làm video, hay công ty? Ba câu trả lời cho ra ba thuật toán khác nhau.",
        en: "Not quite. MIT teaches students to think of algorithms as <b>opinions</b>. It sounds odd, but consider: who should a video recommendation serve — the viewer, the creator, or the company? Three answers give three different algorithms." },
  hint: { vi: "Máy tính thì khách quan, nhưng ai quyết định máy làm gì?",
          en: "A computer is objective — but who decides what it does?" },
  lv: 3,
  src: "mitAlgorithms",
  srcQuote: "students learn to think of algorithms as opinions",
  srcChecked: "2026-08-09"
};
