/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-safety-totality-viewing",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Thời điểm duy nhất nào người quan sát có thể nhìn trực tiếp Mặt Trời mà không cần kính bảo vệ?",
       en: "When is the only brief period observers can look directly at the Sun without protective eclipse glasses?" },
  opts: [
    { vi: "Chỉ duy nhất trong giai đoạn toàn phần khi Mặt Trăng che kín hoàn toàn Mặt Trời",
      en: "Only during the brief period of totality when the Moon completely obscures the Sun's bright face" },
    { vi: "Lúc bắt đầu nhật thực một phần",
      en: "During the start of a partial eclipse" },
    { vi: "Bất kỳ lúc nào ban ngày",
      en: "At any time during daytime" },
    { vi: "Khi Mặt Trời mọc buổi sáng",
      en: "When the Sun rises in the morning" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Chỉ khi đĩa Mặt Trời bị che khuất hoàn toàn trong kỳ toàn phần mới an toàn để nhìn bằng mắt thường.",
        en: "Correct! Only during exact totality, when the bright face is fully hidden, is direct viewing safe." },
  no: { vi: "Chưa đúng. Mọi giai đoạn khác dù chỉ lộ ra một sợi ánh sáng Mặt Trời cũng nguy hại cho mắt nếu nhìn trực tiếp.",
        en: "Incorrect. Any partial phase exposing even a sliver of sunlight demands protective eyewear." },
  hint: { vi: "Giai đoạn này gọi là totality — khi đĩa Mặt Trời hoàn toàn bị che lấp.",
          en: "This brief window is called totality." },
  lv: 2,
  src: "nasaEclipseSafety",
  srcQuote: "You can view the eclipse directly without proper eye protection only when the Moon completely obscures the Sun's bright face – during the brief and spectacular period known as totality.",
  srcChecked: "2026-08-06"
};
