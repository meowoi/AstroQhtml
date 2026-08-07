/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-tropo-weather",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng đối lưu (Troposphere) có đặc điểm nổi bật gì về hiện tượng tự nhiên?",
       en: "What prominent natural phenomenon occurs constantly in the troposphere?" },
  opts: [
    { vi: "Thời tiết liên tục thay đổi và xáo động không khí",
      en: "Weather that is constantly changing and mixing up gases" },
    { vi: "Hoàn toàn không có mây hay gió",
      en: "Complete absence of clouds and wind" },
    { vi: "Không khí đứng yên không di chuyển",
      en: "Air stands completely still" },
    { vi: "Chỉ có tuyết rơi quanh năm",
      en: "Snow falls constantly year-round" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tên gọi Troposphere bắt nguồn từ đặc tính thời tiết luôn xáo động và thay đổi.",
        en: "Correct! The name troposphere comes from weather constantly changing and mixing." },
  no: { vi: "Chưa đúng. Tầng đối lưu là nơi các hiện tượng thời tiết như mây, mưa, gió diễn ra liên tục.",
        en: "Incorrect. The troposphere is where weather events like rain and wind occur constantly." },
  hint: { vi: "Từ 'Tropos' có nghĩa là sự thay đổi, xáo trộn.",
          en: "The word 'Tropos' relates to change and mixing." },
  lv: 1,
  src: "nasaSpaceplaceTropo",
  srcQuote: "This layer gets its name from the weather that is constantly changing and mixing up the gases in this part of our atmosphere.",
  srcChecked: "2026-08-06"
};
