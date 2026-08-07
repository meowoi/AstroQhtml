/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-surface-temp-color",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Yếu tố cốt lõi nào quyết định màu sắc chủ đạo của ngôi sao mà các kính thiên văn quan sát được?",
       en: "What core factor determines the primary color of a star observed by telescopes?" },
  opts: [
    { vi: "Nhiệt độ bề mặt của ngôi sao",
      en: "The surface temperature of the star" },
    { vi: "Nhiệt độ không ảnh hưởng đến màu sắc",
      en: "Temperature has zero effect on color" },
    { vi: "Nhiệt độ làm sao đổi màu liên tục mỗi giây",
      en: "Temperature causes color to shift every second" },
    { vi: "Nhiệt độ khiến sao biến thành màu xanh lục thuần túy",
      en: "Temperature turns stars pure green" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Nhiệt độ bề mặt quyết định dải bước sóng bức xạ phát ra mạnh nhất.",
        en: "Correct! Surface temperature dictates the peak radiation wavelength emitted." },
  no: { vi: "Chưa đúng. Nhiệt độ bề mặt là yếu tố cốt lõi quyết định màu sắc ngôi sao.",
        en: "Incorrect. Surface temperature is the fundamental factor dictating star color." },
  hint: { vi: "Quy luật bức xạ vật đen gắn liền nhiệt độ với đỉnh màu sắc phát ra.",
          en: "Blackbody radiation laws link temperature to peak color emission." },
  lv: 3,
  src: "lcoStarColors",
  srcQuote: "The surface temperature of a star determines the color of light it emits.",
  srcChecked: "2026-08-06"
};
