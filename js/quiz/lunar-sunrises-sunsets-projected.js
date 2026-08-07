/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-sunrises-sunsets-projected",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Ánh sáng màu đỏ cam chiếu lên Mặt Trăng khi nguyệt thực được ví như hình ảnh nào?",
       en: "How is the reddish light projected onto the Moon during a lunar eclipse described?" },
  opts: [
    { vi: "Giống như tất cả các bình minh và hoàng hôn trên Trái Đất cùng chiếu lên Mặt Trăng",
      en: "It's as if all the world's sunrises and sunsets are projected onto the Moon" },
    { vi: "Giống như ánh đèn laser nhân tạo",
      en: "Like artificial laser beams" },
    { vi: "Giống như ngọn đèn đường ban đêm",
      en: "Like a street light at night" },
    { vi: "Giống như ánh sáng từ chiếc gương soi",
      en: "Like light reflecting off a mirror" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Sắc đỏ nguyệt thực chính là tổng hòa ánh sáng hoàng hôn và bình minh từ khắp vòng quanh Trái Đất.",
        en: "Correct! The reddish glow represents the combined light of all Earth's sunrises and sunsets." },
  no: { vi: "Chưa đúng. Ánh sáng đỏ lọc qua rìa khí quyển Trái Đất tương tự như ánh hoàng hôn đỏ thắm.",
        en: "Incorrect. Red light filtered around Earth's limb mirrors the glow of sunset and sunrise." },
  hint: { vi: "Hãy nghĩ đến màu đỏ cam đẹp đẽ của buổi chiều tà hoàng hôn.",
          en: "Think of the rich reddish-orange colors seen at sunset and sunrise." },
  lv: 3,
  src: "nasaMoonEclipses",
  srcQuote: "It's as if all the world's sunrises and sunsets are projected onto the Moon.",
  srcChecked: "2026-08-06"
};
