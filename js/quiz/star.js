/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star",
  topic: { vi: "NGÔI SAO",
           en: "STAR" },
  q: { vi: "Ngôi sao là gì?",
       en: "What is a star?" },
  opts: [
    { vi: "Quả cầu khí nóng khổng lồ, tự phát ra ánh sáng",
      en: "A giant ball of hot gas that makes its own light" },
    { vi: "Khối đá lạnh quay quanh một hành tinh",
      en: "A cold rock orbiting a planet" },
    { vi: "Cục băng lẫn bụi, có đuôi dài",
      en: "A lump of ice and dust with a long tail" },
    { vi: "Hòn đá đang cháy trong khí quyển",
      en: "A rock burning up in the atmosphere" }
  ],
  a: 0,
  ok: { vi: "Chính xác! NASA cho biết ngôi sao là <b>quả cầu khí nóng khổng lồ</b> — phần lớn là hydro, kèm một ít heli. Mặt Trời chính là một ngôi sao.",
        en: "Correct! NASA describes a star as a <b>giant ball of hot gas</b> — mostly hydrogen with some helium. Our Sun is a star." },
  no: { vi: "Chưa đúng! Ngôi sao là <b>quả cầu khí nóng tự phát sáng</b>, không phải đá cũng không phải băng.",
        en: "Not quite! A star is a <b>ball of hot gas that shines on its own</b> — not rock, not ice." },
  hint: { vi: "Mặt Trời là một ngôi sao. Nó nóng, nó sáng, và nó <b>không hề rắn</b>.",
          en: "The Sun is a star. It's hot, it's bright, and it is <b>not solid</b>." },
  lv: 1,
  src: "star"
};
