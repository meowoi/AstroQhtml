/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "asteroid-what",
  topic: { vi: "TIỂU HÀNH TINH",
           en: "ASTEROID" },
  q: { vi: "Tiểu hành tinh thực chất là gì?",
       en: "What is an asteroid, really?" },
  opts: [
    { vi: "Mảnh đá còn sót lại từ thời hệ Mặt Trời mới hình thành",
      en: "A rocky leftover from when the solar system formed" },
    { vi: "Cục băng bốc hơi thành đuôi dài khi gần Mặt Trời",
      en: "An icy lump that grows a long tail near the Sun" },
    { vi: "Một quả cầu khí nóng cỡ nhỏ",
      en: "A small ball of hot gas" },
    { vi: "Vệ tinh nhân tạo đã hỏng",
      en: "A broken-down artificial satellite" }
  ],
  a: 0,
  ok: { vi: "Đúng! NASA gọi tiểu hành tinh là <b>mảnh đá còn sót lại</b> từ lúc hệ Mặt Trời hình thành khoảng <b>4,6 tỉ năm</b> trước. Chúng đôi khi còn được gọi là “tiểu hành tinh” (minor planets).",
        en: "Correct! NASA describes asteroids as <b>rocky remnants</b> left over from the formation of the solar system about <b>4.6 billion years</b> ago. They're sometimes called minor planets." },
  no: { vi: "Chưa đúng! Đó là <b>mảnh đá</b> còn sót lại từ thời hệ Mặt Trời hình thành. Cục băng có đuôi dài là <b>sao chổi</b>, không phải tiểu hành tinh.",
        en: "Not quite! It's a <b>rocky leftover</b> from the solar system's formation. The icy one with a tail is a <b>comet</b>, not an asteroid." },
  hint: { vi: "Từ khoá là <b>đá</b> — băng thì thuộc về một loại vật thể khác.",
          en: "The key word is <b>rock</b> — ice belongs to a different kind of object." },
  lv: 1,
  src: "aster"
};
