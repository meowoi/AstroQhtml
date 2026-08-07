/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-umbra-inner-shadow",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Trong nguyệt thực toàn phần, Mặt Trăng đi vào dải bóng nào của Trái Đất?",
       en: "During a total lunar eclipse, the Moon moves into which part of Earth's shadow?" },
  opts: [
    { vi: "Vùng bóng tối bên trong (umbra)",
      en: "The inner part of Earth's shadow, or the umbra" },
    { vi: "Vùng khí quyển Mặt Trời",
      en: "The solar atmosphere region" },
    { vi: "Vùng vành đai bão từ",
      en: "The magnetic storm belt" },
    { vi: "Vùng bóng màu xanh",
      en: "The blue shadow region" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Khi đi vào vùng bóng tối đậm nhất umbra của Trái Đất, nguyệt thực toàn phần xảy ra.",
        en: "Correct! Moving into Earth's dark inner umbral cone creates a total lunar eclipse." },
  no: { vi: "Chưa đúng. Vùng bóng tối thẫm bên trong lòng bóng Trái Đất gọi là umbra.",
        en: "Incorrect. The dark central core of Earth's shadow is called the umbra." },
  hint: { vi: "Tên tiếng Anh của vùng bóng tối thẫm này là umbra.",
          en: "The name for this central dark shadow cone is umbra." },
  lv: 1,
  src: "nasaMoonEclipses",
  srcQuote: "The Moon moves into the inner part of Earth's shadow, or the umbra.",
  srcChecked: "2026-08-06"
};
