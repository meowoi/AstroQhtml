/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-strato-uv",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Lớp ôzôn ở tầng bình lưu bảo vệ con người và sinh vật khỏi tác hại của yếu tố nào?",
       en: "What does the ozone layer in the stratosphere protect living things from?" },
  opts: [
    { vi: "Bức xạ cực tím (UV) từ Mặt Trời",
      en: "Ultraviolet radiation (UV) from the sun" },
    { vi: "Ánh sáng nhìn thấy ban ngày",
      en: "Visible daylight" },
    { vi: "Tất cả các loại mây mưa",
      en: "All rain clouds" },
    { vi: "Gió và không khí lạnh",
      en: "Wind and cold air" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Lớp ôzôn giúp hấp thụ hầu hết tia cực tím (UV) có hại từ Mặt Trời.",
        en: "Correct! The ozone layer protects us by absorbing harmful UV radiation from the sun." },
  no: { vi: "Chưa đúng. Lớp ôzôn cản trở bức xạ cực tím (UV) chứ không cản ánh sáng nhìn thấy.",
        en: "Incorrect. The ozone layer blocks harmful UV radiation, not visible light." },
  hint: { vi: "Đây là loại tia bức xạ gây bỏng da và tổn thương mắt nếu không có ôzôn bảo vệ.",
          en: "This radiation type causes sunburns and eye damage without ozone shielding." },
  lv: 2,
  src: "nasaSpaceplaceStrato",
  srcQuote: "The ozone layer helps protect us from ultraviolet radiation (UV) from the sun.",
  srcChecked: "2026-08-06"
};
