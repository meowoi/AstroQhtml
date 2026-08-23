/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-counts-tarps",
  topic: { vi: "AI SAU THIÊN TAI",
           en: "AI AFTER DISASTERS" },
  q: { vi: "Theo NASA, sau một cơn bão thì AI đo mức thiệt hại bằng cách đếm thứ gì trong ảnh vệ tinh?",
       en: "According to NASA, what does AI count in satellite images to measure damage after a storm?" },
  opts: [
    { vi: "Những tấm bạt phủ trên mái nhà",
      en: "Tarps on roofs" },
    { vi: "Số xe cứu hộ đang chạy trên đường",
      en: "Rescue vehicles on the roads" },
    { vi: "Số cây bị đổ trong thành phố",
      en: "Fallen trees across the city" },
    { vi: "Diện tích vùng bị ngập nước",
      en: "The area covered by floodwater" }
  ],
  a: 0,
  ok: { vi: "Đúng! NASA nêu đúng ví dụ đó: <b>AI có thể đếm những tấm bạt trên mái nhà trong ảnh vệ tinh để đo mức thiệt hại sau một cơn bão</b>. Ý hay ở đây không phải công nghệ, mà là cách nghĩ: <b>chọn một thứ máy nhìn được để thay cho thứ mình muốn biết</b>.",
       en: "Yes! That is NASA's own example: <b>AI can count tarps on roofs in satellite images to measure damage after a storm</b>. The clever part is not the technology but the idea: <b>pick something a machine can see to stand in for what you want to know</b>." },
  no: { vi: "Chưa đúng! NASA nói tới <b>những tấm bạt trên mái nhà</b>: nhà bị vỡ mái thì người ta căng bạt lên, nên đếm bạt là đếm nhà bị hỏng — một thứ <b>máy nhìn được từ trên cao</b>.",
       en: "Not quite! NASA mentions <b>tarps on roofs</b>: a damaged roof gets covered with a tarp, so counting tarps counts damaged homes — something <b>a machine can see from above</b>." },
  hint: { vi: "Mái nhà bị vỡ thì người ta phủ tạm cái gì lên?",
         en: "What do people put over a roof that has been torn open?" },
  lv: 2,
  src: "nasaWhatIsAi",
  srcQuote: "For example, AI can count tarps on roofs in satellite images to measure damage after a storm.",
  srcChecked: "2026-08-23"
};
