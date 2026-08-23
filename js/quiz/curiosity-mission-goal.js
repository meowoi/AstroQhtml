/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "curiosity-mission-goal",
  topic: { vi: "NHIỆM VỤ CỦA CURIOSITY",
           en: "CURIOSITY'S MISSION" },
  q: { vi: "Mục tiêu nhiệm vụ của rover Curiosity trên Sao Hoả là gì?",
       en: "What is the mission objective of the Curiosity rover on Mars?" },
  opts: [
    { vi: "Tìm người Sao Hoả đang sống ở đó",
      en: "Find Martians living there now" },
    { vi: "Mang mẫu đất đá về Trái Đất",
      en: "Bring rock samples back to Earth" },
    { vi: "Xác định xem Sao Hoả có bao giờ từng nuôi được sự sống vi sinh hay không",
      en: "Determine if Mars was ever able to support microbial life" },
    { vi: "Dựng một căn cứ cho phi hành gia tới sau",
      en: "Build a base for astronauts arriving later" }
  ],
  a: 2,
  ok: { vi: "Đúng! NASA ghi mục tiêu chỉ trong một dòng: <b>xác định xem Sao Hoả có bao giờ từng có khả năng nuôi được sự sống vi sinh hay không</b>. Không phải tìm người Sao Hoả — mà là hỏi xem hành tinh này có bao giờ là <b>nơi ở được</b> không.",
       en: "Yes! NASA states the objective in one line: <b>determine if Mars was ever able to support microbial life</b>. Not finding Martians — asking whether this planet was ever <b>habitable</b>." },
  no: { vi: "Chưa đúng! Câu hỏi Curiosity được gửi đi để trả lời là: <b>Sao Hoả có bao giờ từng nuôi được sự sống vi sinh không</b>. Chú ý hai chữ <b>từng</b> và <b>vi sinh</b> — không phải sự sống bây giờ, và không phải sinh vật lớn.",
       en: "Not quite! The question Curiosity was sent to answer is: <b>was Mars ever able to support microbial life</b>. Note <b>ever</b> and <b>microbial</b> — not life today, and not large creatures." },
  hint: { vi: "Câu trả lời nói về quá khứ, và về những sinh vật rất nhỏ.",
         en: "The answer is about the past, and about very small living things." },
  lv: 1,
  src: "curiosity",
  srcQuote: "Determine if Mars was ever able to support microbial life",
  srcChecked: "2026-08-23"
};
