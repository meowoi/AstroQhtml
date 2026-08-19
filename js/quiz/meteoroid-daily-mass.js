/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteoroid-daily-mass",
  topic: { vi: "THIÊN THẠCH NHỎ",
           en: "METEOROID" },
  q: { vi: "Các nhà khoa học ước tính mỗi NGÀY có khoảng bao nhiêu vật chất từ không gian rơi xuống Trái Đất?",
       en: "Scientists estimate roughly how much space material falls on Earth each DAY?" },
  opts: [
    { vi: "Khoảng 1 kg",
      en: "About 1 kilogram" },
    { vi: "Khoảng 48,5 tấn (44.000 kg)",
      en: "About 48.5 tons (44,000 kilograms)" },
    { vi: "Khoảng 5 triệu tấn",
      en: "About 5 million tons" },
    { vi: "Gần như không có gì",
      en: "Almost nothing at all" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA ước tính khoảng <b>48,5 tấn (44.000 kg)</b> vật chất từ không gian rơi xuống Trái Đất <b>mỗi ngày</b> — phần lớn là hạt bụi cháy hết trên cao nên ta không hề hay biết.",
          en: "Yes! NASA estimates about <b>48.5 tons (44,000 kilograms)</b> of meteoritic material falls on Earth <b>every day</b> — mostly dust grains that burn up high above us, unnoticed." },
  no: { vi: "Chưa đúng! Con số NASA đưa ra là khoảng <b>48,5 tấn mỗi ngày</b>. Nghe nhiều, nhưng gần hết là bụi mịn tan trong khí quyển.",
          en: "Not quite! NASA's figure is about <b>48.5 tons per day</b>. It sounds like a lot, but nearly all of it is fine dust that burns up in the atmosphere." },
  hint: { vi: "Nặng hơn một con voi, nhẹ hơn một toà nhà — và là mỗi ngày.",
            en: "Heavier than an elephant, lighter than a building — and that's per day." },
  lv: 2,
  src: "meteor",
  srcQuote: "Scientists estimate that about 48.5 tons (44,000 kilograms) of meteoritic material falls on Earth each day.",
  srcChecked: "2026-08-19"
};
