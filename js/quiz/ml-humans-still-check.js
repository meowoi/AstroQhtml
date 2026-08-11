/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ml-humans-still-check",
  topic: { vi: "HỌC MÁY",
           en: "MACHINE LEARNING" },
  q: { vi: "Trong dự án tìm tiểu hành tinh trên ảnh Hubble, ngoài AI còn có gì góp phần vào kết quả?",
       en: "In the project that found asteroids in Hubble images, what else contributed to the result?" },
  opts: [
    { vi: "Không có gì — AI làm hết một mình",
      en: "Nothing — the AI did it all alone" },
    { vi: "Công sức của khoảng 11.000 tình nguyện viên là người thường",
      en: "The efforts of some 11,000 citizen scientist volunteers" },
    { vi: "Một kính thiên văn thứ hai đặt trên Sao Hoả",
      en: "A second telescope placed on Mars" },
    { vi: "Một máy tính lượng tử",
      en: "A quantum computer" }
  ],
  a: 1,
  ok: { vi: "Đúng! Máy làm phần <b>nhìn</b> rất nhanh, con người vẫn <b>kiểm và xác nhận</b>. AI ở đây không thay thế ai — nó khiến một việc bất khả thi trở thành việc làm được.",
        en: "Yes! The machine did the <b>looking</b>, fast; people still <b>checked and confirmed</b>. The AI replaced nobody — it turned an impossible job into a possible one." },
  no: { vi: "Chưa đúng. Kết quả 1.031 tiểu hành tinh đến từ AI <b>cộng với công sức của khoảng 11.000 tình nguyện viên</b>. Đó là điều đáng nhớ hơn cả con số: AI làm nhanh phần nhìn, người vẫn phải kiểm.",
        en: "Not quite. Those 1,031 asteroids came from AI <b>combined with the efforts of some 11,000 citizen scientist volunteers</b>. That matters more than the number: AI looks fast, people still check." },
  hint: { vi: "Một cỗ máy đoán rất nhanh thì vẫn cần ai đó nói “đúng rồi”.",
          en: "A machine that guesses fast still needs someone to say “yes, that's right”." },
  lv: 3,
  src: "aiHubble",
  srcQuote: "Combined with the efforts of some 11,000 citizen scientist volunteers, the project revealed 1,031 previously undiscovered asteroids",
  srcChecked: "2026-08-09"
};
