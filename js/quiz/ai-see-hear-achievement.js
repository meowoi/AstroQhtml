/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-see-hear-achievement",
  topic: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
  q: { vi: "Theo AI4K12, điều nào dưới đây là một trong những thành tựu LỚN NHẤT của AI cho tới nay?",
       en: "According to AI4K12, which of these is one of the most significant achievements of AI to date?" },
  opts: [
    { vi: "AI đã thắng con người ở mọi môn thể thao",
      en: "AI has beaten humans at every sport" },
    { vi: "AI tự viết ra chính nó, không cần con người nữa",
      en: "AI now writes itself with no human involved" },
    { vi: "AI làm ra những máy tính không bao giờ tính sai",
      en: "AI has produced computers that never make mistakes" },
    { vi: "Làm cho máy tính “thấy” và “nghe” đủ tốt để dùng được vào việc thật",
      en: "Making computers “see” and “hear” well enough for practical use" }
  ],
  a: 3,
  ok: { vi: "Chính xác! Nghe thì tưởng nhỏ, nhưng “thấy” và “nghe” là hai việc con người làm mà <b>không cần nghĩ</b>, còn máy thì mất mấy chục năm mới làm tạm được. Chữ quan trọng nhất là <b>“đủ tốt để dùng được vào việc thật”</b>.",
        en: "Exactly! It sounds modest, but “seeing” and “hearing” are things people do <b>without thinking</b>, while machines needed decades to do them at all. The key words are <b>“well enough for practical use”</b>." },
  no: { vi: "Chưa đúng — và ba đáp án kia đều là những điều AI <b>chưa</b> làm được. Thành tựu mà AI4K12 nêu ra là việc máy “thấy” và “nghe” đủ tốt để <b>dùng được vào việc thật</b>.",
        en: "Not quite — the other three are all things AI <b>cannot</b> do. The achievement AI4K12 names is machines “seeing” and “hearing” well enough <b>for practical use</b>." },
  hint: { vi: "Chọn điều đã XẢY RA rồi, đừng chọn điều nghe oai nhất.",
          en: "Pick what has actually HAPPENED, not what sounds grandest." },
  lv: 2,
  src: "ai4k12Perception",
  srcQuote: "Making computers “see” and “hear” well enough for practical use is one of the most significant achievements of AI to date.",
  srcChecked: "2026-08-23"
};
