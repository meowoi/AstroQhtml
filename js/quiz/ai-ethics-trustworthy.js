/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-ethics-trustworthy",
  topic: { vi: "ĐẠO ĐỨC AI",
           en: "AI ETHICS" },
  q: { vi: "NASA nói dùng AI theo cách nào là điều quan trọng với họ?",
       en: "NASA says using AI in what manner is important to them?" },
  opts: [
    { vi: "Theo cách nhanh nhất và rẻ nhất",
      en: "In the fastest and cheapest way" },
    { vi: "Theo cách đáng tin cậy và có đạo đức",
      en: "In a trustworthy and ethical manner" },
    { vi: "Theo cách không ai bên ngoài biết được",
      en: "In a way nobody outside can find out about" },
    { vi: "Theo cách thay thế được càng nhiều người càng tốt",
      en: "In a way that replaces as many people as possible" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! NASA viết rằng dùng AI theo cách <b>đáng tin cậy và có đạo đức</b> là điều quan trọng với họ. Để ý: đây là một cơ quan vũ trụ chứ không phải một lớp học đạo đức — vậy mà họ vẫn viết câu đó ra. Vì AI của họ giúp quyết định những việc thật, nên cách dùng nó cũng là việc thật.",
        en: "Right! NASA writes that using AI in a <b>trustworthy and ethical</b> manner is important to them. Notice: this is a space agency, not an ethics class — and they still wrote it down. Their AI helps decide real things, so how it is used is a real matter too." },
  no: { vi: "Chưa đúng. NASA viết rằng dùng AI theo cách <b>đáng tin cậy và có đạo đức</b> là điều quan trọng với họ. Nhanh và rẻ là chuyện khác — một hệ thống chạy nhanh mà không ai tin được thì không dùng vào việc gì được.",
        en: "Not quite. NASA writes that using AI in a <b>trustworthy and ethical</b> manner is important to them. Fast and cheap is a different matter — a system that runs fast but nobody can trust is of no use." },
  hint: { vi: "Nếu bạn không tin một cái máy, bạn có dám dùng kết quả của nó không?",
          en: "If you did not trust a machine, would you dare use its answer?" },
  lv: 2,
  src: "nasaAiEthics",
  srcQuote: "Using AI in a trustworthy and ethical manner is important to us",
  srcChecked: "2026-08-20"
};
