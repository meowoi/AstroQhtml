/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-thermo-iss",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Trạm Vũ trụ Quốc tế (ISS) bay quanh Trái Đất ở tầng khí quyển nào?",
       en: "Which atmospheric layer is notable for being home to the International Space Station?" },
  opts: [
    { vi: "Tầng nhiệt (Thermosphere)",
      en: "Thermosphere" },
    { vi: "Tầng đối lưu sát mặt đất",
      en: "Troposphere near ground" },
    { vi: "Tầng bình lưu",
      en: "Stratosphere" },
    { vi: "Tầng trung lưu",
      en: "Mesosphere" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Trạm Vũ trụ Quốc tế (ISS) hoạt động ở quỹ đạo thuộc tầng nhiệt.",
        en: "Correct! The International Space Station orbits Earth within the thermosphere." },
  no: { vi: "Chưa đúng. Mặc dù ISS ở ngoài không gian gần Trái Đất, nó hoạt động ở độ cao thuộc tầng nhiệt.",
        en: "Incorrect. Though in low Earth orbit, the ISS operates within the thermosphere layer." },
  hint: { vi: "Tầng này có không khí cực kỳ loãng ở độ cao rất lớn.",
          en: "This layer features extremely thin air at very high altitude." },
  lv: 2,
  src: "nasaGeneralAtmosphere",
  srcQuote: "This layer is notable for being home to the International Space Station and other low-Earth-orbit satellites.",
  srcChecked: "2026-08-06"
};
