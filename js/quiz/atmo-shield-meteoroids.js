/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-shield-meteoroids",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Bầu khí quyển bảo vệ Trái Đất khỏi các thiên thạch bay vào như thế nào?",
       en: "How does our atmosphere protect us from incoming meteoroids?" },
  opts: [
    { vi: "Hầu hết thiên thạch bị vỡ vụn trong khí quyển trước khi đâm xuống bề mặt",
      en: "Most break up in our atmosphere before they can strike the surface" },
    { vi: "Khí quyển thổi thiên thạch bay ngược lại vũ trụ",
      en: "Atmosphere blows meteoroids back to space" },
    { vi: "Khí quyển biến thiên thạch thành mây mưa",
      en: "Atmosphere turns meteoroids into rain clouds" },
    { vi: "Khí quyển đóng băng hoàn toàn thiên thạch",
      en: "Atmosphere freezes meteoroids solid" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Ma sát và sức nén khí quyển làm hầu hết thiên thạch vỡ tan trước khi va chạm mặt đất.",
        en: "Correct! Atmospheric pressure and friction break up most meteoroids before surface impact." },
  no: { vi: "Chưa đúng. Khí quyển hoạt động như chiếc khiên làm vỡ vụn và thiêu rụi thiên thạch va chạm.",
        en: "Incorrect. The atmosphere acts as a shield, breaking up and burning incoming meteoroids." },
  hint: { vi: "Nhờ đó bề mặt Trái Đất không bị dày đặc hố thiên thạch như Mặt Trăng.",
          en: "This shields Earth's surface from becoming heavily cratered like the Moon." },
  lv: 2,
  src: "nasaEarthFacts",
  srcQuote: "Our atmosphere protects us from incoming meteoroids, most of which break up in our atmosphere before they can strike the surface.",
  srcChecked: "2026-08-06"
};
