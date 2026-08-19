/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-mass-life",
  topic: { vi: "NGÔI SAO",
           en: "STAR" },
  q: { vi: "Hai ngôi sao cùng sinh ra một lúc, nhưng một ngôi nặng gấp nhiều lần ngôi kia. Ngôi NẶNG hơn sẽ sống lâu hơn hay ngắn hơn?",
       en: "Two stars are born at the same time, but one is many times heavier than the other. Will the HEAVIER one live longer or shorter?" },
  opts: [
    { vi: "Lâu hơn, vì nó có nhiều nhiên liệu hơn",
      en: "Longer, because it has more fuel" },
    { vi: "Ngắn hơn, vì nó đốt nhiên liệu nhanh hơn rất nhiều",
      en: "Shorter, because it burns through its fuel far faster" },
    { vi: "Bằng nhau — khối lượng không liên quan",
      en: "The same — mass has nothing to do with it" },
    { vi: "Lâu hơn, vì nó nóng hơn",
      en: "Longer, because it is hotter" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! Khối lượng quyết định ngôi sao <b>đốt hết nhiên liệu nhanh cỡ nào</b>. Sao nhẹ cháy <b>lâu hơn, mờ hơn và mát hơn</b>; sao rất nặng thì sáng chói nhưng tiêu hết nhiên liệu rất nhanh — nhiều nhiên liệu mà đốt quá nhanh thì vẫn hết sớm.",
          en: "Right! Mass decides <b>how fast a star runs through its fuel</b>. Low-mass stars burn <b>longer, dimmer and cooler</b>; very massive stars blaze bright but use up their supply fast — plenty of fuel burned far too quickly still runs out sooner." },
  no: { vi: "Chưa đúng! Sao nặng <b>có</b> nhiều nhiên liệu hơn thật, nhưng nó phải đốt nhanh hơn nhiều để không sụp xuống dưới sức nặng của chính mình. NASA cho biết sao nhẹ cháy <b>lâu hơn, mờ hơn, mát hơn</b>.",
          en: "Not quite! A massive star <b>does</b> have more fuel, but it must burn it far faster to keep from collapsing under its own weight. NASA says lower-mass stars burn <b>longer, dimmer and cooler</b>." },
  hint: { vi: "Nhiều nhiên liệu nhưng đốt cực nhanh — nghĩ tới cây nến to bị thắp <b>hai đầu</b>.",
            en: "Lots of fuel but burning very fast — think of a big candle lit at <b>both ends</b>." },
  lv: 3,
  src: "star",
  srcQuote: "A star's gas provides its fuel, and its mass determines how rapidly it runs through its supply, with lower-mass stars burning longer, dimmer, and cooler than very massive stars.",
  srcChecked: "2026-08-19"
};
