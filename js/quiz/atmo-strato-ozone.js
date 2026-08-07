/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-strato-ozone",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Lớp ôzôn (Ozone layer) bảo vệ sự sống nằm ở tầng khí quyển nào?",
       en: "In which atmospheric layer will you find the vital ozone layer?" },
  opts: [
    { vi: "Tầng bình lưu (Stratosphere)",
      en: "Stratosphere" },
    { vi: "Tầng đối lưu",
      en: "Troposphere" },
    { vi: "Tầng trung lưu",
      en: "Mesosphere" },
    { vi: "Tầng ngoại lưu",
      en: "Exosphere" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Lớp ôzôn tập trung ở tầng bình lưu (Stratosphere).",
        en: "Correct! The protective ozone layer resides in the stratosphere." },
  no: { vi: "Chưa đúng. Nhiều người nghĩ ôzôn ở sát mặt đất, nhưng lớp ôzôn bảo vệ thực sự nằm ở tầng bình lưu.",
        en: "Incorrect. While surface ozone is a pollutant, the protective ozone layer is in the stratosphere." },
  hint: { vi: "Đây là tầng khí quyển ngay phía trên tầng đối lưu.",
          en: "This is the atmospheric layer directly above the troposphere." },
  lv: 1,
  src: "nasaSpaceplaceStrato",
  srcQuote: "The stratosphere is where you'll find the very important ozone layer.",
  srcChecked: "2026-08-06"
};
