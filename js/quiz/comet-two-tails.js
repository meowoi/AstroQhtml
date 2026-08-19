/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "comet-two-tails",
  topic: { vi: "SAO CHỔI",
           en: "COMET" },
  q: { vi: "Một sao chổi thực ra có mấy cái đuôi?",
       en: "How many tails does a comet actually have?" },
  opts: [
    { vi: "Một đuôi duy nhất",
      en: "Just one" },
    { vi: "Hai đuôi: một đuôi bụi và một đuôi ion (khí)",
      en: "Two: a dust tail and an ion (gas) tail" },
    { vi: "Ba đuôi",
      en: "Three" },
    { vi: "Không có đuôi nào — đó chỉ là ảo giác",
      en: "None — the tail is an illusion" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA nói sao chổi thực ra có <b>hai đuôi: một đuôi bụi và một đuôi ion (khí)</b>. Trong những bức ảnh đẹp, đôi khi ta thấy rõ hai vệt riêng hơi lệch nhau.",
          en: "Yes! NASA says comets actually have <b>two tails — a dust tail and an ion (gas) tail</b>. In good photographs you can sometimes make out two separate streaks at slightly different angles." },
  no: { vi: "Chưa đúng! Sao chổi có <b>hai</b> đuôi — <b>đuôi bụi</b> và <b>đuôi ion (khí)</b>.",
          en: "Not quite! A comet has <b>two</b> tails — a <b>dust tail</b> and an <b>ion (gas) tail</b>." },
  hint: { vi: "Bụi và khí bay theo hai kiểu khác nhau, nên chúng không nằm chồng lên nhau.",
            en: "Dust and gas get pushed in different ways, so they don't lie on top of each other." },
  lv: 2,
  src: "comet",
  srcQuote: "Comets actually have two tails – a dust tail and an ion (gas) tail.",
  srcChecked: "2026-08-19"
};
