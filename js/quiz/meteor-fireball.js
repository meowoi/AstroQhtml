/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteor-fireball",
  topic: { vi: "SAO BĂNG",
           en: "METEOR" },
  q: { vi: "Một sao băng sáng hơn cả Sao Kim thì được NASA gọi là gì?",
       en: "What does NASA call a meteor that shines brighter than Venus?" },
  opts: [
    { vi: "Sao chổi",
      en: "A comet" },
    { vi: "Siêu tân tinh",
      en: "A supernova" },
    { vi: "Nhật thực",
      en: "A solar eclipse" },
    { vi: "Quả cầu lửa (fireball)",
      en: "A fireball" }
  ],
  a: 3,
  ok: { vi: "Chuẩn! NASA gọi những sao băng <b>sáng hơn Sao Kim</b> là <b>quả cầu lửa (fireball)</b>. Chúng sáng đến mức có thể thấy được cả lúc trời còn chưa tối hẳn.",
        en: "Exactly! NASA calls meteors <b>brighter than Venus</b> <b>fireballs</b>. They can be bright enough to spot before the sky is fully dark." },
  no: { vi: "Chưa đúng! Đó là <b>quả cầu lửa (fireball)</b> — vẫn là một sao băng, chỉ là sáng khác thường.",
        en: "Not quite! It's a <b>fireball</b> — still a meteor, just an unusually bright one." },
  hint: { vi: "Tên gọi rất “nóng”, và nó vẫn thuộc họ sao băng.",
          en: "The name sounds hot — and it's still a meteor." },
  lv: 3,
  src: "meteor"
};
