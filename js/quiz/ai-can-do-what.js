/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-can-do-what",
  topic: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
  q: { vi: "NASA nói các thiết bị dùng AI có thể làm những việc nào?",
       en: "NASA says devices using AI can do which of these?" },
  opts: [
    { vi: "Học từ ngữ và khái niệm, nhận ra vật thể, thấy được các mẫu, hoặc đưa ra dự đoán",
      en: "Learn words and concepts, recognize objects, see patterns, or make predictions" },
    { vi: "Chỉ làm đúng những việc đã được viết thành luật sẵn",
      en: "Only carry out rules written for them in advance" },
    { vi: "Cảm nhận được cảm xúc như con người",
      en: "Feel emotions the way people do" },
    { vi: "Tự sửa mọi lỗi của chính nó mà không cần ai kiểm",
      en: "Fix every one of their own mistakes with nobody checking" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! Bốn việc đó nghe rời rạc nhưng có một điểm chung: đều <b>dễ với người mà rất khó viết thành luật</b>. Bạn nhận ra khuôn mặt bạn mình ngay — nhưng thử viết ra thành các bước xem!",
        en: "Right! Those four sound unrelated but share one thing: each is <b>easy for people and very hard to write as rules</b>. You recognise a friend's face instantly — now try writing that out as steps!" },
  no: { vi: "Chưa đúng. NASA liệt kê: <b>học từ ngữ và khái niệm, nhận ra vật thể, thấy được các mẫu, hoặc đưa ra dự đoán</b>. Còn “chỉ làm theo luật viết sẵn” là mô tả một chương trình thông thường, không phải AI.",
        en: "Not quite. NASA lists: <b>learn words and concepts, recognize objects, see patterns, or make predictions</b>. “Only following pre-written rules” describes an ordinary program, not AI." },
  hint: { vi: "Cái nào là việc con người làm dễ mà viết thành luật thì rất khó?",
          en: "Which one is easy for humans yet very hard to write as rules?" },
  lv: 2,
  src: "nasaWhatIsAi",
  srcQuote: "Devices using AI can learn words and concepts, recognize objects, see patterns, or make predictions.",
  srcChecked: "2026-08-09"
};
