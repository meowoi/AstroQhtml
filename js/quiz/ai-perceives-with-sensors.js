/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-perceives-with-sensors",
  topic: { vi: "CẢM BIẾN",
           en: "SENSORS" },
  q: { vi: "Theo khung dạy AI cho trường học AI4K12, máy tính “cảm nhận” được thế giới bên ngoài nhờ cái gì?",
       en: "In the AI4K12 framework for schools, what lets a computer perceive the world around it?" },
  opts: [
    { vi: "Nhờ đoán từ những gì đã có sẵn trong bộ nhớ",
      en: "By guessing from what is already stored in its memory" },
    { vi: "Nhờ hỏi người dùng mỗi lần cần biết",
      en: "By asking the user every time it needs to know" },
    { vi: "Nhờ cảm biến",
      en: "Using sensors" },
    { vi: "Nhờ nối vào Internet",
      en: "By connecting to the Internet" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! Máy tính không tự biết gì về thế giới bên ngoài — nó chỉ biết những gì <b>cảm biến</b> đưa vào. Camera là mắt, micro là tai. Rồi việc “hiểu” tín hiệu đó nghĩa là gì mới là phần AI làm.",
        en: "Right! A computer knows nothing about the outside world on its own — only what its <b>sensors</b> feed in. A camera is an eye, a microphone an ear. Making sense of those signals is the AI part." },
  no: { vi: "Chưa đúng. Máy tính “cảm nhận” thế giới bằng <b>cảm biến</b>. Nối Internet chỉ mang về dữ liệu người khác đã thu; hỏi người dùng thì không phải máy tự cảm nhận. Không có cảm biến thì máy mù và điếc.",
        en: "Not quite. A computer perceives the world through <b>sensors</b>. The Internet only brings data someone else collected; asking the user is not the machine sensing. With no sensors, a machine is blind and deaf." },
  hint: { vi: "Rover trên Sao Hoả biết phía trước có tảng đá nhờ thứ gì?",
          en: "How does a Mars rover know there is a rock ahead?" },
  lv: 1,
  src: "ai4k12Perception",
  srcQuote: "Computers perceive the world using sensors.",
  srcChecked: "2026-08-23"
};
