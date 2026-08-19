/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteor-where",
  topic: { vi: "SAO BĂNG",
           en: "METEOR" },
  q: { vi: "Hiện tượng meteor (sao băng) xảy ra ở đâu?",
       en: "Where does a meteor happen?" },
  opts: [
    { vi: "Ngoài không gian, giữa các hành tinh",
      en: "Out in space, between the planets" },
    { vi: "Trong khí quyển",
      en: "In the atmosphere" },
    { vi: "Trên mặt đất",
      en: "On the ground" },
    { vi: "Trong lõi Mặt Trời",
      en: "Inside the Sun's core" }
  ],
  a: 1,
  ok: { vi: "Đúng! Chỉ khi hòn đá không gian <b>lao vào khí quyển</b> và cháy lên thì nó mới được gọi là <b>meteor</b>. Lúc còn bay ngoài không gian nó là <b>meteoroid</b>.",
          en: "Yes! Only when a space rock <b>enters the atmosphere</b> and burns up is it called a <b>meteor</b>. While still out in space it is a <b>meteoroid</b>." },
  no: { vi: "Chưa đúng! Meteor là chuyện xảy ra <b>trong khí quyển</b> — đó chính là lúc hòn đá cháy sáng thành một vệt.",
          en: "Not quite! A meteor happens <b>in the atmosphere</b> — that's the moment the rock burns into a streak of light." },
  hint: { vi: "Ta ngắm sao băng từ mặt đất bằng mắt thường, nên nó phải cháy ở tầng khí ngay trên đầu ta.",
            en: "We watch meteors from the ground with the naked eye, so they must burn in the air above us." },
  lv: 1,
  src: "meteor",
  srcQuote: "When meteoroids enter Earth's atmosphere, or that of another planet, at high speed and burn up, they're called meteors.",
  srcChecked: "2026-08-19"
};
