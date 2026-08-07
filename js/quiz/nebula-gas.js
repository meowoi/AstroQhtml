/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "nebula-gas",
  topic: { vi: "TINH VÂN",
           en: "NEBULA" },
  q: { vi: "Điều gì làm phần giữa một đám mây khí co lại và nóng lên đủ để một ngôi sao ra đời?",
       en: "What makes the middle of a gas cloud collapse and heat up until a star is born?" },
  opts: [
    { vi: "Gió Mặt Trời thổi mây lại",
      en: "The solar wind squeezing the cloud" },
    { vi: "Từ trường của thiên hà",
      en: "The galaxy's magnetic field" },
    { vi: "Va chạm với một tiểu hành tinh",
      en: "A collision with an asteroid" },
    { vi: "Lực hấp dẫn hút thêm vật chất về chỗ đặc",
      en: "Gravity pulling more matter into the dense clumps" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! Ở những chỗ mây đặc lại, <b>lực hấp dẫn hút thêm vật chất về</b>; phần giữa bị ép ngày càng chặt và nóng lên — đủ nóng để phản ứng nhiệt hạch khởi động, và một ngôi sao ra đời.",
        en: "Right! Where the cloud grows denser, <b>gravity attracts additional matter</b>; the middle is squeezed ever tighter and heats up — hot enough for nuclear fusion to start, and a star is born." },
  no: { vi: "Chưa đúng! Chính <b>lực hấp dẫn</b> làm chỗ đặc co lại và nóng lên, chứ không phải gió hay va chạm.",
        en: "Not quite! It is <b>gravity</b> that makes the dense clumps collapse and heat up — not wind or collisions." },
  hint: { vi: "Cùng một lực giữ em không bay khỏi mặt đất, nhưng ở đây nó bóp cả một đám mây.",
          en: "The same force that keeps you on the ground — here it squeezes an entire cloud." },
  src: "star"
};
