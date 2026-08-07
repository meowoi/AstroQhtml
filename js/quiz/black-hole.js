/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "black-hole",
  topic: { vi: "LỖ ĐEN",
           en: "BLACK HOLE" },
  q: { vi: "Đường biên của lỗ đen — nơi không gì thoát ra được nữa — gọi là gì?",
       en: "What is the boundary of a black hole, beyond which nothing can escape, called?" },
  opts: [
    { vi: "Vành đai Kuiper",
      en: "The Kuiper Belt" },
    { vi: "Chân trời sự kiện",
      en: "The event horizon" },
    { vi: "Ranh giới ngày/đêm",
      en: "The day–night terminator" },
    { vi: "Quầng khí quyển",
      en: "The atmospheric halo" }
  ],
  a: 1,
  ok: { vi: "Chính xác! NASA gọi đường biên đó là <b>chân trời sự kiện</b>. Nó <b>không phải một mặt đất</b> — đó là đường biên chứa toàn bộ vật chất làm nên lỗ đen.",
        en: "Correct! NASA calls that boundary the <b>event horizon</b>. It is <b>not a surface</b> like Earth's — it is a boundary containing all the matter that makes up the black hole." },
  no: { vi: "Chưa đúng! Đường biên đó là <b>chân trời sự kiện</b>. Qua nó thì không gì thoát ra được, kể cả ánh sáng.",
        en: "Not quite! That boundary is the <b>event horizon</b>. Past it, nothing escapes — not even light." },
  hint: { vi: "Nó nghe như một <b>đường chân trời</b>: qua khỏi vạch đó là không quay lại được.",
          en: "It sounds like a <b>horizon</b>: cross that line and there is no coming back." },
  src: "bh"
};
