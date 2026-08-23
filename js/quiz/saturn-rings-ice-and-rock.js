/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "saturn-rings-ice-and-rock",
  topic: { vi: "SAO THỔ & TÀU CASSINI",
           en: "SATURN AND CASSINI" },
  q: { vi: "Vành đai Sao Thổ làm từ gì?",
       en: "What are Saturn's rings made of?" },
  opts: [
    { vi: "Một tấm kim loại liền khối",
        en: "One solid sheet of metal" },
    { vi: "Khí nóng phát sáng",
        en: "Glowing hot gas" },
    { vi: "Hàng tỉ mảnh băng và đá nhỏ",
        en: "Billions of small chunks of ice and rock" },
    { vi: "Nước lỏng",
        en: "Liquid water" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! NASA ghi vành đai được tạo nên từ <b>hàng tỉ mảnh băng và đá nhỏ</b>, phủ thêm bụi.",
        en: "Right! NASA says the rings are made of <b>billions of small chunks of ice and rock</b>, coated with dust." },
  no: { vi: "Chưa đúng! Vành đai không phải một khối liền — nó gồm <b>hàng tỉ mảnh băng và đá</b> cùng bay quanh Sao Thổ.",
        en: "Not quite! The rings are not solid - they are <b>billions of chunks of ice and rock</b> orbiting Saturn together." },
  hint: { vi: "Nếu là một khối liền thì các phần của vành đai không thể bay quanh với tốc độ khác nhau được.",
          en: "If it were one solid piece, different parts could not orbit at different speeds." },
  lv: 1,
  src: "saturnFacts",
  srcQuote: "They are made of billions of small chunks of ice and rock coated with other materials such as dust.",
  srcChecked: "2026-08-22"
};
