/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteorite-name",
  topic: { vi: "THIÊN THẠCH",
           en: "METEORITE" },
  q: { vi: "Một hòn đá từ không gian đã rơi xuống và đang nằm trên mặt đất thì gọi là gì?",
       en: "What do we call a space rock that has landed and is lying on the ground?" },
  opts: [
    { vi: "Meteoroid",
      en: "A meteoroid" },
    { vi: "Meteor",
      en: "A meteor" },
    { vi: "Meteorite (thiên thạch)",
      en: "A meteorite" },
    { vi: "Tiểu hành tinh",
      en: "An asteroid" }
  ],
  a: 2,
  ok: { vi: "Chính xác! Hòn đá <b>đi hết được khí quyển và tới mặt đất</b> thì mang tên <b>meteorite</b> — đây là loại duy nhất trong ba loại mà con người có thể <b>cầm lên tay</b>.",
          en: "Exactly! A rock that <b>survives the atmosphere and hits the ground</b> is a <b>meteorite</b> — the only one of the three you can actually <b>hold in your hand</b>." },
  no: { vi: "Chưa đúng! Ngoài không gian nó là <b>meteoroid</b>, đang cháy trên trời là <b>meteor</b>, còn nằm trên mặt đất là <b>meteorite</b>.",
          en: "Not quite! In space it's a <b>meteoroid</b>, burning in the sky it's a <b>meteor</b>, and on the ground it's a <b>meteorite</b>." },
  hint: { vi: "Chỉ một trong ba cái tên đó chỉ hòn đá đã hạ cánh.",
            en: "Only one of the three names belongs to a rock that has landed." },
  lv: 1,
  src: "meteor",
  srcQuote: "When a meteoroid survives its trip through the atmosphere and hits the ground, it's called a meteorite.",
  srcChecked: "2026-08-19"
};
