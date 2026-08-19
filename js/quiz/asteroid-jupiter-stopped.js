/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "asteroid-jupiter-stopped",
  topic: { vi: "TIỂU HÀNH TINH",
           en: "ASTEROID" },
  q: { vi: "Vì sao đám vật thể ở vành đai tiểu hành tinh không gộp lại thành một hành tinh?",
       en: "Why did the bodies in the asteroid belt never come together into a planet?" },
  opts: [
    { vi: "Vì chỗ đó quá lạnh để đá dính được vào nhau",
      en: "Because it is too cold there for rock to stick together" },
    { vi: "Vì lực hấp dẫn của Sao Mộc vừa hình thành đã chặn lại",
      en: "Because the gravity of newly formed Jupiter put a stop to it" },
    { vi: "Vì tổng khối lượng ở đó lớn quá",
      en: "Because there is far too much total mass there" },
    { vi: "Vì Mặt Trời hút hết vật chất về phía mình",
      en: "Because the Sun pulled all the material inward" }
  ],
  a: 1,
  ok: { vi: "Chính xác! NASA cho biết ngay thời kỳ đầu của hệ Mặt Trời, <b>lực hấp dẫn của Sao Mộc vừa hình thành đã chấm dứt việc tạo hành tinh ở vùng đó</b>, đồng thời làm các vật thể nhỏ va vào nhau và vỡ ra thành những tiểu hành tinh ta thấy hôm nay.",
          en: "Exactly! NASA says that early in the solar system's history, <b>the gravity of newly formed Jupiter brought an end to planet formation in that region</b> and made the small bodies collide, fragmenting them into the asteroids we see today." },
  no: { vi: "Chưa đúng! Nguyên nhân là <b>lực hấp dẫn của Sao Mộc</b>. Ngược lại, tổng khối lượng ở vành đai rất NHỎ — cộng hết tiểu hành tinh lại vẫn nhẹ hơn Mặt Trăng của Trái Đất.",
          en: "Not quite! The cause is <b>Jupiter's gravity</b>. In fact the belt's total mass is tiny — all the asteroids combined weigh less than Earth's Moon." },
  hint: { vi: "Hành tinh lớn nhất hệ Mặt Trời nằm ngay sát vành đai ấy.",
            en: "The largest planet in the solar system sits right next to that belt." },
  lv: 3,
  src: "aster",
  srcQuote: "Early in the history of the solar system, the gravity of newly formed Jupiter brought an end to the formation of planetary bodies in this region and caused the small bodies to collide with one another, fragmenting them into the asteroids we observe today.",
  srcChecked: "2026-08-19"
};
