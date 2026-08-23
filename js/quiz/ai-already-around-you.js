/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-already-around-you",
  topic: { vi: "AI TRONG ĐỜI SỐNG",
           en: "AI IN EVERYDAY LIFE" },
  q: { vi: "MIT News nêu ba ví dụ nào để nói rằng trí tuệ nhân tạo đã thành một phần của đời sống?",
       en: "Which three examples does MIT News give to say artificial intelligence has become a way of life?" },
  opts: [
    { vi: "Robot trong nhà máy, xe tự lái và tàu vũ trụ",
      en: "Factory robots, self-driving cars and spacecraft" },
    { vi: "Máy tính chơi cờ, siêu máy tính và người máy",
      en: "Chess computers, supercomputers and androids" },
    { vi: "Alexa, các gợi ý của YouTube và những danh sách phát của Spotify",
      en: "Alexa, YouTube recommendations and Spotify playlists" },
    { vi: "Kính thiên văn Hubble, rover Sao Hoả và Mạng Không Gian Sâu",
      en: "The Hubble telescope, Mars rovers and the Deep Space Network" }
  ],
  a: 2,
  ok: { vi: "Đúng! MIT News mở đầu bằng đúng ba thứ đó: <b>Alexa, gợi ý của YouTube và danh sách phát của Spotify</b>. Điều đáng chú ý là <b>không cái nào trông giống một con robot</b> — nhưng cả ba đều đang <b>chọn hộ bạn</b> một thứ gì đó.",
       en: "Yes! MIT News opens with exactly those three: <b>Alexa, YouTube recommendations and Spotify playlists</b>. What matters is that <b>none of them looks like a robot</b> — yet all three are <b>choosing something for you</b>." },
  no: { vi: "Chưa đúng! MIT News cố ý chọn những thứ <b>rất quen</b> chứ không phải robot hay tàu vũ trụ: <b>Alexa, gợi ý của YouTube, danh sách phát của Spotify</b>. Đó chính là ý của bài — AI đã ở quanh bạn từ trước khi bạn nghe tới từ đó.",
       en: "Not quite! MIT News deliberately picks <b>everyday</b> things rather than robots or spacecraft: <b>Alexa, YouTube recommendations, Spotify playlists</b>. That is the point — AI was already around you before you heard the word." },
  hint: { vi: "Thử nghĩ tới những thứ tự chọn hộ bạn bài hát hoặc video tiếp theo.",
         en: "Think of things that pick your next song or video for you." },
  lv: 1,
  src: "mitAiMiddleSchool",
  srcQuote: "In the age of Alexa, YouTube recommendations, and Spotify playlists, artificial intelligence has become a way of life",
  srcChecked: "2026-08-23"
};
