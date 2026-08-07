/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-tropo-mass",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng đối lưu chứa khoảng bao nhiêu phần khối lượng của toàn bộ bầu khí quyển?",
       en: "About how much of the total atmospheric mass is contained in the troposphere?" },
  opts: [
    { vi: "Chỉ 10% khối lượng",
      en: "Only 10% of mass" },
    { vi: "Một nửa (50%) khối lượng",
      en: "Half (50%) of mass" },
    { vi: "Ba phần tư (75%) khối lượng",
      en: "Three-quarters (75%) of mass" },
    { vi: "100% khối lượng",
      en: "100% of mass" }
  ],
  a: 2,
  ok: { vi: "Chính xác! Tầng đối lưu chứa khoảng 3/4 (75%) tổng khối lượng khí quyển Trái Đất.",
        en: "Correct! The troposphere holds roughly three-quarters (75%) of total atmospheric mass." },
  no: { vi: "Chưa đúng. Nhiều người nghĩ không khí chia đều, nhưng trọng lực làm 3/4 khối lượng khí tập trung ở tầng đối lưu.",
        en: "Incorrect. Gravity concentrates roughly three-quarters of atmospheric mass in the troposphere." },
  hint: { vi: "Trọng lực hút hầu hết phân tử khí về gần bề mặt Trái Đất.",
          en: "Gravity pulls most air molecules close to Earth's surface." },
  lv: 2,
  src: "nasaSpaceplaceTropo",
  srcQuote: "In fact, the troposphere contains three-quarters of the mass of the entire atmosphere.",
  srcChecked: "2026-08-06"
};
