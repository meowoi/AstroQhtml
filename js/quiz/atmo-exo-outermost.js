/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-exo-outermost",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng nào là tầng ngoài cùng của bầu khí quyển Trái Đất, nơi hầu hết các vệ tinh quỹ đạo hoạt động?",
       en: "Which layer is the outermost layer of Earth's atmosphere, where most satellites orbit?" },
  opts: [
    { vi: "Tầng ngoại lưu (Exosphere)",
      en: "Exosphere" },
    { vi: "Tầng nhiệt",
      en: "Thermosphere" },
    { vi: "Tầng trung lưu",
      en: "Mesosphere" },
    { vi: "Tầng bình lưu",
      en: "Stratosphere" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tầng ngoại lưu (Exosphere) là tầng khí quyển ngoài cùng tiếp giáp vũ trụ.",
        en: "Correct! The exosphere is the outermost layer merging into space." },
  no: { vi: "Chưa đúng. Tầng ngoại lưu (Exosphere) mới là tầng ngoài cùng của khí quyển Trái Đất.",
        en: "Incorrect. The exosphere is the outermost layer of Earth's atmosphere." },
  hint: { vi: "Tiền tố 'Exo-' ám chỉ vị trí ngoài cùng.",
          en: "The prefix 'Exo-' signifies the outermost position." },
  lv: 1,
  src: "nasaGeneralAtmosphere",
  srcQuote: "The exosphere is the outermost layer of the Earth's atmosphere, where most satellites orbit.",
  srcChecked: "2026-08-06"
};
