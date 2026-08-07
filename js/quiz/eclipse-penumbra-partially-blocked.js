/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-penumbra-partially-blocked",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Người quan sát đứng trong vùng bóng nửa tối rộng hơn (penumbra) sẽ quan sát được hiện tượng gì?",
       en: "What do observers within the larger penumbra witness during a solar eclipse?" },
  opts: [
    { vi: "Mặt Trời chỉ bị che khuất một phần",
      en: "The Sun is only partially blocked" },
    { vi: "Mặt Trời bị che khuất hoàn toàn",
      en: "The Sun is completely blocked" },
    { vi: "Mặt Trăng biến mất khỏi bầu trời",
      en: "The Moon vanishes from the sky" },
    { vi: "Trái Đất ngừng quay",
      en: "Earth stops rotating" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Vùng penumbra rộng lớn bên ngoài chỉ nhìn thấy nhật thực một phần.",
        en: "Correct! Inside the larger outer penumbra, only a partial eclipse is seen." },
  no: { vi: "Chưa đúng. Vùng penumbra nhận được một phần ánh sáng nên chỉ thấy Mặt Trời bị che một phần.",
        en: "Incorrect. The penumbral shadow only causes partial obscuration of the Sun." },
  hint: { vi: "Vùng bóng mờ bên ngoài vẫn nhận được một phần ánh sáng.",
          en: "The outer lighter shadow area still receives partial sunlight." },
  lv: 2,
  src: "nasaEclipseGeometry",
  srcQuote: "Within the larger penumbra, the Sun is only partially blocked.",
  srcChecked: "2026-08-06"
};
