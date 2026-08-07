/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "supernova-elements",
  topic: { vi: "SIÊU TÂN TINH",
           en: "SUPERNOVA" },
  q: { vi: "Vật chất bị siêu tân tinh bắn vào không gian sẽ đi đâu?",
       en: "What happens to the material a supernova throws into space?" },
  opts: [
    { vi: "Làm giàu cho các mây phân tử, rồi thành thế hệ ngôi sao kế tiếp",
      en: "It enriches molecular clouds and becomes the next generation of stars" },
    { vi: "Biến mất hoàn toàn khỏi vũ trụ",
      en: "It vanishes from the universe completely" },
    { vi: "Rơi hết trở lại vào lỗ đen ngay lập tức",
      en: "It falls straight back into a black hole" },
    { vi: "Đông lại thành một hành tinh duy nhất",
      en: "It freezes into one single planet" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! NASA cho biết vật chất bị vụ nổ bắn ra sẽ <b>làm giàu cho các mây phân tử sau này</b>, rồi đi vào thành phần của <b>thế hệ ngôi sao kế tiếp</b>. Gạch của căn nhà cũ được dùng lại để xây nhà mới.",
        en: "Right! NASA says material cast into the cosmos <b>enriches future molecular clouds</b> and becomes part of the <b>next generation of stars</b>. The old bricks get reused to build new houses." },
  no: { vi: "Chưa đúng! Vật chất không mất đi — nó <b>làm giàu cho mây phân tử</b> và trở thành nguyên liệu của các ngôi sao sinh sau.",
        en: "Not quite! The material isn't lost — it <b>enriches molecular clouds</b> and becomes raw material for later stars." },
  hint: { vi: "Nhớ lại câu hỏi về tinh vân: ngôi sao được sinh ra từ <b>mây khí và bụi</b>.",
          en: "Recall the nebula question: stars are born from <b>clouds of gas and dust</b>." },
  src: "star"
};
