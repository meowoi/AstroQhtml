/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-penumbral-faint-outer-shadow",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Trong kỳ nguyệt thực nửa tối (penumbral eclipse), Mặt Trăng di chuyển qua vùng nào?",
       en: "During a penumbral lunar eclipse, where does the Moon travel?" },
  opts: [
    { vi: "Qua vùng penumbra — dải bóng mờ phía ngoài cùng của Trái Đất",
      en: "The Moon travels through Earth's penumbra, or the faint outer part of its shadow" },
    { vi: "Vào lõi Trái Đất",
      en: "Travels inside Earth's core" },
    { vi: "Ra bên ngoài Dải Ngân Hà",
      en: "Travels outside the Milky Way" },
    { vi: "Vào bầu khí quyển Mặt Trời",
      en: "Travels into the solar atmosphere" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Mặt Trăng đi qua vùng bóng nửa tối mờ nhạt nên độ sáng chỉ giảm nhẹ, khó nhận biết.",
        en: "Correct! Passing through the faint outer penumbra causes a barely noticeable dimming." },
  no: { vi: "Chưa đúng. Vùng bóng phía ngoài mờ nhạt của Trái Đất được gọi là penumbra.",
        en: "Incorrect. The faint outer fringe of Earth's shadow is called the penumbra." },
  hint: { vi: "Hiện tượng này khiến Mặt Trăng chỉ tối đi rất nhẹ.",
          en: "This eclipse type causes only a slight, subtle darkening of the Moon." },
  lv: 2,
  src: "nasaMoonEclipses",
  srcQuote: "The Moon travels through Earth's penumbra, or the faint outer part of its shadow.",
  srcChecked: "2026-08-06"
};
