/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteor",
  topic: { vi: "SAO BĂNG",
           en: "METEOR" },
  q: { vi: "“Sao băng” mà ta thấy trên trời đêm thực chất là gì?",
       en: "What is a “shooting star” really?" },
  opts: [
    { vi: "Một ngôi sao đang rơi khỏi trời",
      en: "A star falling out of the sky" },
    { vi: "Một vệ tinh nhân tạo đang bay qua",
      en: "An artificial satellite passing by" },
    { vi: "Ánh sáng phản chiếu từ Mặt Trăng",
      en: "Light reflecting off the Moon" },
    { vi: "Vệt sáng do đá không gian lao vào khí quyển và cháy lên",
      en: "The streak of light as a space rock enters the atmosphere and burns up" }
  ],
  a: 3,
  ok: { vi: "Đúng! Sao băng chẳng phải ngôi sao nào cả: đó là <b>vệt sáng</b> khi đá không gian lao vào khí quyển với tốc độ cực nhanh rồi <b>cháy lên</b>. Tiếng Anh gọi vui là “shooting star”.",
        en: "Correct! A shooting star is no star at all: it's the <b>streak of light</b> made when a space rock hits the atmosphere at huge speed and <b>burns up</b>." },
  no: { vi: "Chưa đúng! Ngôi sao thì to hơn Trái Đất rất nhiều và ở cách ta hàng nghìn tỉ km. Sao băng chỉ là <b>đá không gian đang cháy trong khí quyển</b>.",
        en: "Not quite! Stars are vastly bigger than Earth and unimaginably far away. A meteor is just <b>a space rock burning up in the atmosphere</b>." },
  hint: { vi: "Nếu nó thật là ngôi sao thì trời đã hết sao từ lâu rồi…",
          en: "If those really were stars, the sky would have run out long ago…" },
  src: "meteor"
};
