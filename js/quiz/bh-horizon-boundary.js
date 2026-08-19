/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "bh-horizon-boundary",
  topic: { vi: "LỖ ĐEN",
           en: "BLACK HOLE" },
  q: { vi: "Chân trời sự kiện KHÔNG phải một bề mặt rắn như mặt đất của Trái Đất hay bề mặt Mặt Trời. Vậy nó là gì?",
       en: "The event horizon is NOT a solid surface like Earth's or the Sun's. So what is it?" },
  opts: [
    { vi: "Một lớp vỏ đá bao quanh lỗ đen",
      en: "A rocky shell around the black hole" },
    { vi: "Một đường biên chứa toàn bộ vật chất làm nên lỗ đen",
      en: "A boundary that contains all the matter making up the black hole" },
    { vi: "Một luồng khí nóng đang xoáy",
      en: "A swirling jet of hot gas" },
    { vi: "Chỗ để hướng kính viễn vọng vào quan sát",
      en: "The spot telescopes are aimed at" }
  ],
  a: 1,
  ok: { vi: "Chính xác! NASA nói chân trời sự kiện <b>không phải một bề mặt</b> — nó là <b>một đường biên chứa toàn bộ vật chất làm nên lỗ đen</b>. Vượt qua đường biên ấy thì không gì, kể cả ánh sáng, quay ra được nữa.",
          en: "Exactly! NASA says the event horizon <b>isn't a surface</b> — it is <b>a boundary that contains all the matter that makes up the black hole</b>. Past that line nothing, not even light, gets back out." },
  no: { vi: "Chưa đúng! Đó không phải vật rắn nào cả: chân trời sự kiện là <b>một đường biên</b> — ranh giới bao lấy toàn bộ vật chất của lỗ đen, cũng là chỗ ánh sáng không thoát ra được.",
          en: "Not quite! It isn't a solid thing at all: the event horizon is <b>a boundary</b> — the line enclosing all the black hole's matter, and the line light cannot cross outward." },
  hint: { vi: "Nó là một ranh giới, không phải một thứ ta có thể đứng lên.",
            en: "It's a line, not something you could stand on." },
  lv: 3,
  src: "bh",
  srcQuote: "The event horizon isn't a surface like Earth's or even the Sun's. It's a boundary that contains all the matter that makes up the black hole.",
  srcChecked: "2026-08-19"
};
