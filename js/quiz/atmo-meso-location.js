/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-meso-location",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng trung lưu (Mesosphere) nằm ở vị trí nào trong cấu trúc khí quyển?",
       en: "Where is the mesosphere located within Earth's atmospheric structure?" },
  opts: [
    { vi: "Nằm giữa tầng bình lưu và tầng nhiệt",
      en: "Middle layer between the stratosphere and the thermosphere" },
    { vi: "Nằm ngay dưới tầng đối lưu sát mực nước biển",
      en: "Located directly below the troposphere at sea level" },
    { vi: "Nằm ngoài cùng ranh giới vũ trụ",
      en: "Outermost boundary in space" },
    { vi: "Nằm bên trong lớp ôzôn",
      en: "Inside the ozone layer" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tầng trung lưu nằm ở giữa tầng bình lưu và tầng nhiệt.",
        en: "Correct! The mesosphere is the middle layer between stratosphere and thermosphere." },
  no: { vi: "Chưa đúng. Từ 'Meso' có nghĩa là ở giữa: tầng trung lưu nằm giữa tầng bình lưu và tầng nhiệt.",
        en: "Incorrect. 'Meso' means middle: the mesosphere is between stratosphere and thermosphere." },
  hint: { vi: "Tên gọi 'Meso' có nguồn gốc từ từ có nghĩa là ở giữa.",
          en: "The name 'Meso' originates from a word meaning middle." },
  lv: 2,
  src: "nasaGeneralAtmosphere",
  srcQuote: "The mesosphere is the middle layer between the stratosphere and the thermosphere.",
  srcChecked: "2026-08-06"
};
