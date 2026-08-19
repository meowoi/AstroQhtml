/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteorite-survive",
  topic: { vi: "THIÊN THẠCH",
           en: "METEORITE" },
  q: { vi: "Theo NASA, phần khối lượng của một vật thể lao vào khí quyển mà tới được mặt đất thường là bao nhiêu?",
       en: "According to NASA, how much of an object entering the atmosphere usually makes it to the ground?" },
  opts: [
    { vi: "Gần như toàn bộ",
      en: "Almost all of it" },
    { vi: "Khoảng một nửa",
      en: "About half" },
    { vi: "Đúng 25%",
      en: "Exactly 25%" },
    { vi: "Thường dưới 5%",
      en: "Usually less than 5%" }
  ],
  a: 3,
  ok: { vi: "Đúng! NASA cho biết <b>thường dưới 5%</b> khối lượng ban đầu tới được mặt đất — phần còn lại cháy hết trên đường. Mỗi ngày có khoảng <b>48,5 tấn</b> vật chất thiên thạch rơi xuống Trái Đất.",
        en: "Correct! NASA says <b>less than 5%</b> of the original object usually reaches the ground — the rest burns away. About <b>48.5 tons</b> of meteoritic material falls on Earth every day." },
  no: { vi: "Chưa đúng! <b>Dưới 5%</b> thôi. Khí quyển Trái Đất là một tấm khiên rất hiệu quả.",
        en: "Not quite! <b>Less than 5%</b>. Earth's atmosphere is a remarkably good shield." },
  hint: { vi: "Khí quyển bảo vệ chúng ta rất tốt — nên con số này <b>rất nhỏ</b>.",
          en: "The atmosphere protects us well — so this number is <b>very small</b>." },
  lv: 3,
  src: "meteor"
};
