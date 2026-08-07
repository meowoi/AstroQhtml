/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-tropo-density",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Mật độ không khí có đặc điểm gì ở tầng thấp nhất (tầng đối lưu)?",
       en: "What is the characteristic of air density in the lowest layer (troposphere)?" },
  opts: [
    { vi: "Không khí đặc nhất ở tầng thấp nhất này",
      en: "The air is densest in this lowest layer" },
    { vi: "Không khí loãng nhất so với tất cả các tầng",
      en: "Air is thinner than all other layers" },
    { vi: "Hoàn toàn không có không khí",
      en: "Complete absence of air" },
    { vi: "Mật độ không khí biến đổi ngẫu nhiên mỗi giây",
      en: "Density changes randomly every second" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Do lực hấp dẫn hút khí về bề mặt, không khí đặc nhất ở tầng đối lưu.",
        en: "Correct! Gravity pulls air molecules down, making air densest in the troposphere." },
  no: { vi: "Chưa đúng. Càng lên cao không khí càng loãng; không khí đặc nhất chính là ở tầng đối lưu sát mặt đất.",
        en: "Incorrect. Air gets thinner as you go up; air is densest in the lowest troposphere layer." },
  hint: { vi: "Trọng lực hút hầu hết phân tử không khí dồn xuống sát bề mặt Trái Đất.",
          en: "Gravity pulls most air molecules down towards Earth's surface." },
  lv: 3,
  src: "nasaSpaceplaceTropo",
  srcQuote: "The air is densest in this lowest layer.",
  srcChecked: "2026-08-06"
};
