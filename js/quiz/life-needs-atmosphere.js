/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "life-needs-atmosphere",
  topic: { vi: "SỰ SỐNG CẦN GÌ",
           en: "WHAT LIFE NEEDS" },
  q: { vi: "Theo NASA, một bầu khí quyển bảo vệ giúp sự sống che chắn khỏi thứ gì?",
       en: "According to NASA, what does a protective atmosphere shield life from?" },
  opts: [
    { vi: "Thiên thạch nhỏ",
      en: "Small meteoroids" },
    { vi: "Tiếng ồn từ không gian",
      en: "Noise from space" },
    { vi: "Cái lạnh của ban đêm",
      en: "The cold of night" },
    { vi: "Tia cực tím từ ngôi sao mẹ",
      en: "UV radiation from its host star" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! Khí quyển che chắn khỏi <b>tia cực tím</b> phát ra từ ngôi sao mẹ — vì quá nhiều bức xạ sẽ <b>làm hỏng DNA</b>.",
        en: "Right! The atmosphere shields against <b>UV radiation</b> from the host star - too much radiation <b>damages DNA</b>." },
  no: { vi: "Chưa đúng! Thứ NASA nêu là <b>tia cực tím từ ngôi sao mẹ</b>, vì bức xạ quá nhiều làm hỏng DNA.",
        en: "Not quite! NASA names <b>UV radiation from the host star</b>, because too much radiation damages DNA." },
  hint: { vi: "Danh sách của NASA chỉ có ba thứ: nước, nguồn năng lượng, và một thứ để CHE CHẮN.",
          en: "NASA's list has just three items: water, energy sources, and something that SHIELDS." },
  lv: 2,
  src: "lifeNeeds",
  srcQuote: "A protective atmosphere is also needed for life to survive in order to protect it from UV radiation from its host star.",
  srcChecked: "2026-08-22"
};
