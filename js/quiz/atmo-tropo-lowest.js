/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-tropo-lowest",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng khí quyển nào thấp nhất, tiếp giáp trực tiếp với bề mặt Trái Đất?",
       en: "Which layer of the atmosphere is the lowest, right next to Earth's surface?" },
  opts: [
    { vi: "Tầng bình lưu",
      en: "Stratosphere" },
    { vi: "Tầng đối lưu (Troposphere)",
      en: "Troposphere" },
    { vi: "Tầng trung lưu",
      en: "Mesosphere" },
    { vi: "Tầng nhiệt",
      en: "Thermosphere" }
  ],
  a: 1,
  ok: { vi: "Chính xác! Tầng đối lưu (Troposphere) là tầng khí quyển thấp nhất sát mặt đất.",
        en: "Correct! The troposphere is the lowest atmospheric layer nearest the ground." },
  no: { vi: "Chưa đúng. Tầng đối lưu (Troposphere) mới là tầng thấp nhất nơi con người sinh sống.",
        en: "Incorrect. The troposphere is the lowest layer where humans live." },
  hint: { vi: "Đây là tầng khí quyển nơi các đám mây hình thành.",
          en: "This is the atmospheric layer where clouds form." },
  lv: 1,
  src: "ucarTroposphere",
  srcQuote: "The troposphere is the lowest layer of Earth's atmosphere.",
  srcChecked: "2026-08-06"
};
