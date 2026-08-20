/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-ethics-governance",
  topic: { vi: "ĐẠO ĐỨC AI",
           en: "AI ETHICS" },
  q: { vi: "Theo NASA, việc sử dụng AI phải đi kèm với thứ gì?",
       en: "According to NASA, what must the use of AI come with?" },
  opts: [
    { vi: "Sự quản trị và các biện pháp bảo vệ, vì lợi ích của tất cả mọi người",
      en: "Governance and protections, for the benefit of all" },
    { vi: "Một chiếc máy tính mạnh hơn mỗi năm",
      en: "A more powerful computer every year" },
    { vi: "Lời hứa rằng máy sẽ không bao giờ sai",
      en: "A promise that the machine will never be wrong" },
    { vi: "Việc giữ bí mật hoàn toàn cách hệ thống hoạt động",
      en: "Keeping how the system works completely secret" }
  ],
  a: 0,
  ok: { vi: "Chính xác! NASA viết rằng việc sử dụng AI phải đi kèm <b>sự quản trị và các biện pháp bảo vệ, vì lợi ích của tất cả mọi người</b>. Hai chữ cuối đáng để ý: không phải vì lợi ích của người làm ra nó, mà của <i>tất cả</i> — kể cả những người không hề chọn dùng nó.",
        en: "Exactly! NASA writes that the use of AI must come with <b>governance and protections for the benefit of all</b>. Note those last two words: not for the benefit of whoever built it, but of <i>all</i> — including people who never chose to use it." },
  no: { vi: "Chưa đúng. NASA viết rằng việc sử dụng AI phải đi kèm <b>sự quản trị và các biện pháp bảo vệ, vì lợi ích của tất cả mọi người</b>. Máy mạnh hơn không làm nó công bằng hơn, và không hệ thống nào hứa được là mình không bao giờ sai.",
        en: "Not quite. NASA writes that the use of AI must come with <b>governance and protections for the benefit of all</b>. A more powerful machine is not a fairer one, and no system can promise never to be wrong." },
  hint: { vi: "Một công cụ mạnh mà không ai trông coi thì ai chịu trách nhiệm khi nó sai?",
          en: "If a powerful tool has nobody overseeing it, who answers for its mistakes?" },
  lv: 3,
  src: "nasaAiEthics",
  srcQuote: "NASA understands that usage must come with governance and protections for the benefit of all",
  srcChecked: "2026-08-20"
};
