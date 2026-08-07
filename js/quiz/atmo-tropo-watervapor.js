/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-tropo-watervapor",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tại sao các hiện tượng thời tiết như mây, mưa, tuyết lại diễn ra chủ yếu ở tầng đối lưu mà không có ở các tầng cao hơn?",
       en: "Why do weather events like clouds and rain occur almost entirely in the troposphere?" },
  opts: [
    { vi: "Vì đây là nơi tập trung phần lớn khối lượng khí quyển, bao gồm hầu hết lượng hơi nước",
      en: "Because it is where much of the atmospheric mass, including most of the water vapor, is found" },
    { vi: "Vì các tầng cao hơn gần Mặt Trời hơn nên hơi nước bị bốc cháy hết",
      en: "Because higher layers are closer to the Sun so water vapor burns away" },
    { vi: "Vì khí ôzôn ở tầng bình lưu đẩy tất cả các đám mây xuống dưới",
      en: "Because ozone in the stratosphere pushes all clouds downward" },
    { vi: "Vì nhiệt độ ở tầng bình lưu luôn cố định ở 0°C",
      en: "Because stratosphere temperature is fixed at 0°C" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Thời tiết diễn ra ở tầng đối lưu vì tầng này tập trung phần lớn khối lượng không khí và hầu hết hơi nước.",
        en: "Correct! Weather occurs in the troposphere because it contains much of the atmospheric mass and most water vapor." },
  no: { vi: "Chưa đúng. Tầng đối lưu chứa phần lớn khối lượng không khí và hầu hết hơi nước, nên mây mưa chỉ hình thành ở tầng này.",
        en: "Incorrect. The troposphere contains much of the air mass and most water vapor, so weather forms here." },
  hint: { vi: "Hơi nước là nguyên liệu cốt lõi để tạo nên mây và mưa.",
          en: "Water vapor is the core ingredient needed to form clouds and rain." },
  lv: 2,
  src: "nasaGeneralAtmosphere",
  srcQuote: "Earth's weather occurs in this layer, as it is where much of the atmospheric mass, including most of the water vapor, is found.",
  srcChecked: "2026-08-06"
};
