/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-shadow-umbra-penumbra",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Bóng của Mặt Trăng đổ xuống Trái Đất trong kỳ nhật thực bao gồm hai vùng nón nào?",
       en: "What two concentric shadow cones are cast by the Moon during an eclipse?" },
  opts: [
    { vi: "Vùng bóng tối trong cùng (umbra) và vùng bóng nửa tối bên ngoài (penumbra)",
      en: "A dark inner shadow called the umbra and a lighter outer shadow called the penumbra" },
    { vi: "Vùng màu xanh và vùng màu đỏ",
      en: "A blue region and a red region" },
    { vi: "Vùng khí nóng và vùng khí lạnh",
      en: "A hot gas region and a cold gas region" },
    { vi: "Vùng đại dương và vùng đất liền",
      en: "An ocean region and a land region" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Bóng Mặt Trăng gồm vùng bóng tối chính tâm (umbra) và vùng bóng nửa tối (penumbra).",
        en: "Correct! The Moon's shadow consists of an inner umbra and outer penumbra." },
  no: { vi: "Chưa đúng. Thuật ngữ thiên văn gọi hai vùng bóng này là umbra (bóng tối) và penumbra (bóng nửa tối).",
        en: "Incorrect. Astronomical terms for these two shadow cones are umbra and penumbra." },
  hint: { vi: "Tên tiếng Anh của hai vùng bóng này bắt đầu bằng chữ U và chữ P.",
          en: "The terms for these shadow regions begin with U and P." },
  lv: 1,
  src: "nasaEclipseGeometry",
  srcQuote: "The shadow comprises two concentric cones, a dark inner shadow called the umbra and a lighter outer shadow called the penumbra.",
  srcChecked: "2026-08-06"
};
