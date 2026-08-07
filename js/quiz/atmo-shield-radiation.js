/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-shield-radiation",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Các phân tử ôzôn và oxy ở tầng bình lưu cùng nhau hấp thụ khoảng bao nhiêu bức xạ cực tím từ Mặt Trời?",
       en: "How much solar ultraviolet radiation do ozone and oxygen molecules together absorb?" },
  opts: [
    { vi: "Hấp thụ từ 95% đến 99.9% bức xạ cực tím",
      en: "Absorb 95 to 99.9% of ultraviolet radiation" },
    { vi: "Chỉ hấp thụ 10% bức xạ",
      en: "Absorb only 10% of radiation" },
    { vi: "Không hấp thụ bức xạ nào",
      en: "Absorb zero radiation" },
    { vi: "Hấp thụ 100% ánh sáng nhìn thấy",
      en: "Absorb 100% of visible light" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Ôzôn và oxy phối hợp hấp thụ từ 95% đến 99.9% tia UV nguy hiểm.",
        en: "Correct! Ozone and oxygen together absorb 95 to 99.9% of harmful UV radiation." },
  no: { vi: "Chưa đúng. Nhờ có phân tử ôzôn và oxy, 95% đến 99.9% tia UV độc hại bị ngăn chặn trước khi chạm mặt đất.",
        en: "Incorrect. Together ozone and oxygen block 95% to 99.9% of dangerous UV rays from hitting ground." },
  hint: { vi: "Tỉ lệ che chắn này gần như tuyệt đối, bảo vệ tế bào sinh vật khỏi bị hủy hoại.",
          en: "This near-total absorption shields biological cells from destruction." },
  lv: 3,
  src: "ucarOzoneLayer",
  srcQuote: "Together, ozone and oxygen molecules are able to absorb 95 to 99.9% of the ultraviolet radiation that gets to our planet.",
  srcChecked: "2026-08-06"
};
