/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "loop",
  topic: { vi: "THUẬT TOÁN",
           en: "ALGORITHMS" },
  q: { vi: "Byte cần nhặt 3 tinh thể giống nhau. Nên dùng cấu trúc nào?",
       en: "Byte must collect 3 identical crystals. Which structure fits best?" },
  opts: [
    { vi: "Repeat / Vòng lặp",
      en: "Repeat / Loop" },
    { vi: "If / Nếu",
      en: "If" },
    { vi: "Print / In ra",
      en: "Print" },
    { vi: "Delete / Xoá",
      en: "Delete" }
  ],
  a: 0,
  ok: { vi: "Tuyệt! <b>Vòng lặp Repeat</b> giúp lặp lại một việc nhiều lần mà không viết lại lệnh.",
        en: "Great! A <b>Repeat loop</b> runs the same action many times without rewriting it." },
  no: { vi: "Chưa đúng! Để làm lặp lại một việc, ta dùng <b>vòng lặp</b> chứ không phải lệnh này.",
        en: "Not quite! To repeat an action, use a <b>loop</b>, not this command." },
  hint: { vi: "Làm đi làm lại cùng một việc — cấu trúc nào hợp nhất nhỉ?",
          en: "Doing the same thing over and over — which structure fits?" }
};
