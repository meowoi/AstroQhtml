/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-rayleigh-scattering-red-light",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Tại sao các chùm ánh sáng màu đỏ và cam lại đi tới được bề mặt Mặt Trăng trong kỳ nguyệt thực?",
       en: "Why do red and orange light wavelengths reach the Moon's surface during a lunar eclipse?" },
  opts: [
    { vi: "Vì ánh sáng bước sóng ngắn (xanh, tím) bị tán xạ dễ dàng, còn bước sóng dài (đỏ, cam) truyền qua khí quyển",
      en: "Colors with shorter wavelengths (blues, violets) scatter more easily than colors with longer wavelengths (red, orange)" },
    { vi: "Vì Mặt Trăng tự bùng phát ngọn lửa màu đỏ",
      en: "Because the Moon naturally bursts into flame" },
    { vi: "Vì bề mặt Mặt Trăng làm bằng đồng đỏ",
      en: "Because the lunar surface is made of copper" },
    { vi: "Vì Trái Đất sơn màu đỏ cho Mặt Trăng",
      en: "Because Earth paints the Moon red" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Ánh sáng bước sóng ngắn bị khí quyển Trái Đất tán xạ đi, chỉ có bước sóng dài (đỏ) xuyên qua chiếu tới Mặt Trăng.",
        en: "Correct! Shorter blue wavelengths scatter away while longer red wavelengths travel directly through." },
  no: { vi: "Chưa đúng. Hiện tượng tán xạ trong khí quyển giữ lại ánh sáng xanh và cho ánh sáng đỏ truyền qua.",
        en: "Incorrect. Atmospheric scattering filters blue light while transmitting longer red wavelengths." },
  hint: { vi: "Ánh sáng đỏ có bước sóng dài nên ít bị tán xạ khi đi qua tầng khí quyển.",
          en: "Red light has longer wavelengths that travel more directly through air." },
  lv: 2,
  src: "nasaMoonEclipses",
  srcQuote: "Colors with shorter wavelengths ― the blues and violets ― scatter more easily than colors with longer wavelengths, like red and orange.",
  srcChecked: "2026-08-06"
};
