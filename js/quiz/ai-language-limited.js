/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-language-limited",
  topic: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
  q: { vi: "So về khả năng trò chuyện và suy luận chung, theo AI4K12 thì hệ AI ngày nay đứng ở đâu?",
       en: "On general reasoning and conversation, where does AI4K12 place today’s AI systems?" },
  opts: [
    { vi: "Ngang một người trưởng thành",
      en: "On a par with an adult" },
    { vi: "Hơn hẳn con người ở mọi mặt",
      en: "Far beyond humans in every way" },
    { vi: "Không dùng được ngôn ngữ nào cả",
      en: "Cannot use language at all" },
    { vi: "Dùng được ngôn ngữ ở mức hạn chế, còn thiếu khả năng suy luận chung và trò chuyện của cả một đứa trẻ",
      en: "Can use language to a limited extent, but lack the general reasoning and conversation of even a child" }
  ],
  a: 3,
  ok: { vi: "Đúng! Máy trả lời trôi chảy <b>không</b> đồng nghĩa với hiểu. Để trò chuyện thật tự nhiên còn cần đọc nét mặt, hiểu cảm xúc, biết phong tục và đoán được ý người khác — AI4K12 gọi tất cả những việc đó là <b>khó</b>.",
        en: "Yes! Answering fluently is <b>not</b> the same as understanding. Truly natural conversation also needs reading faces, feeling emotions, knowing customs and inferring intentions — AI4K12 calls all of these <b>hard</b>." },
  no: { vi: "Chưa đúng. AI4K12 nói AI hôm nay dùng ngôn ngữ <b>ở mức hạn chế</b>, và còn thiếu khả năng suy luận chung cùng khả năng trò chuyện <b>của cả một đứa trẻ</b>. Nói mượt là một chuyện, hiểu là chuyện khác.",
        en: "Not quite. AI4K12 says today’s AI uses language <b>to a limited extent</b> and lacks the general reasoning and conversational ability <b>of even a child</b>. Speaking smoothly is one thing; understanding is another." },
  hint: { vi: "Một câu trả lời nghe trôi chảy có chứng minh được là đã hiểu không?",
          en: "Does a fluent answer prove understanding?" },
  lv: 3,
  src: "ai4k12Interaction",
  srcQuote: "Today’s AI systems can use language to a limited extent, but lack the general reasoning and conversational capabilities of even a child.",
  srcChecked: "2026-08-23"
};
