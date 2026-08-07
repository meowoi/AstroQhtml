/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-hybrid-annular-total",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Hiện tượng nhật thực lai (hybrid solar eclipse) là gì?",
       en: "What is a hybrid solar eclipse?" },
  opts: [
    { vi: "Nhật thực chuyển đổi giữa hình khuyên và toàn phần do độ cong bề mặt Trái Đất",
      en: "An eclipse shifting between annular and total as the shadow moves across Earth's curved surface" },
    { vi: "Nhật thực diễn ra đồng thời với nguyệt thực",
      en: "An eclipse occurring simultaneously with a lunar eclipse" },
    { vi: "Nhật thực chỉ kéo dài đúng 1 giây",
      en: "An eclipse lasting exactly 1 second" },
    { vi: "Nhật thực xuất hiện cùng lúc ở hai hành tinh",
      en: "An eclipse appearing on two planets at once" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Do bề mặt Trái Đất cong, bóng Mặt Trăng di chuyển làm nhật thực đổi giữa dạng hình khuyên và toàn phần.",
        en: "Correct! Earth's curvature causes the eclipse to transition between annular and total along its path." },
  no: { vi: "Chưa đúng. Nhật thực lai là sự chuyển đổi giữa nhật thực toàn phần và nhật thực hình khuyên.",
        en: "Incorrect. A hybrid eclipse shifts between annular and total along its track." },
  hint: { vi: "Độ cong của Trái Đất làm thay đổi khoảng cách từ bóng Mặt Trăng tới bề mặt.",
          en: "Earth's spherical curve changes the distance to the Moon's shadow tip." },
  lv: 2,
  src: "nasaEclipseTypes",
  srcQuote: "Because Earth's surface is curved, sometimes an eclipse can shift between annular and total as the Moon's shadow moves across the globe. This is called a hybrid solar eclipse.",
  srcChecked: "2026-08-06"
};
