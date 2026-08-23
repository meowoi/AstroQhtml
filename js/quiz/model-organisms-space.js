/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "model-organisms-space",
  topic: { vi: "SINH HỌC KHÔNG GIAN",
           en: "SPACE BIOLOGY" },
  q: { vi: "Ngoài con người, sinh học không gian thường nghiên cứu những sinh vật nào?",
       en: "Besides humans, which organisms does space biology most commonly study?" },
  opts: [
    { vi: "Chuột cống, chuột nhắt, và các loài không xương sống như giun tròn và côn trùng",
      en: "Rats and mice, plus invertebrates such as nematodes and insects" },
    { vi: "Chỉ nghiên cứu cá voi",
      en: "Only whales" },
    { vi: "Chỉ nghiên cứu khủng long hoá thạch",
      en: "Only dinosaur fossils" },
    { vi: "Không nghiên cứu sinh vật nào khác",
      en: "No other organisms at all" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! NASA nêu <b>chuột cống và chuột nhắt</b>, cùng các loài <b>không xương sống</b> như <b>giun tròn và côn trùng</b> — chúng có vòng đời ngắn nên quan sát được nhiều thế hệ trong một chuyến bay.",
        en: "Right! NASA names <b>rats and mice</b>, plus <b>invertebrates</b> like <b>nematodes and insects</b> - short life cycles mean many generations fit inside one flight." },
  no: { vi: "Chưa đúng! Ngành này xem cả cây cối, vi khuẩn và động vật — hay dùng nhất là <b>chuột</b> cùng <b>giun tròn và côn trùng</b>.",
        en: "Not quite! The field studies plants, microbes and animals - most commonly <b>rodents</b> plus <b>nematodes and insects</b>." },
  hint: { vi: "Muốn biết một thay đổi có truyền sang đời sau không thì phải có đời sau để mà nhìn.",
          en: "To learn whether a change passes to the next generation, you need a next generation to look at." },
  lv: 1,
  src: "spaceBiology",
  srcQuote: "rodents, both rats and mice, and a variety of invertebrate species, e.g., nematodes and insects",
  srcChecked: "2026-08-22"
};
