/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-meso-meteors",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Các thiên thạch (meteors) bị bốc cháy tạo vệt sao băng ở tầng khí quyển nào?",
       en: "In which atmospheric layer do meteors burn up and streak across the sky?" },
  opts: [
    { vi: "Tầng đối lưu",
      en: "Troposphere" },
    { vi: "Tầng trung lưu (Mesosphere)",
      en: "Mesosphere" },
    { vi: "Tầng ngoại lưu",
      en: "Exosphere" },
    { vi: "Tầng nhiệt",
      en: "Thermosphere" }
  ],
  a: 1,
  ok: { vi: "Chính xác! Hầu hết các thiên thạch bốc cháy trong tầng trung lưu (Mesosphere).",
        en: "Correct! Most meteors burn up in the mesosphere." },
  no: { vi: "Chưa đúng. Dù ta nhìn thấy sao băng từ mặt đất, hiện tượng bốc cháy thực sự diễn ra ở tầng trung lưu.",
        en: "Incorrect. Though visible from ground, meteors actually burn up in the mesosphere." },
  hint: { vi: "Tầng này nằm ở giữa cấu trúc các tầng khí quyển.",
          en: "This layer occupies the middle region of atmospheric layers." },
  lv: 1,
  src: "nasaSpaceplaceMeso",
  srcQuote: "Those meteors are burning up in the mesosphere.",
  srcChecked: "2026-08-06"
};
