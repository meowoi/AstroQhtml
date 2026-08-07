/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-meso-friction",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Yếu tố nào ở tầng trung lưu khiến thiên thạch bốc cháy khi đâm vào tầng này?",
       en: "What causes meteors to burn up when hitting the mesosphere?" },
  opts: [
    { vi: "Lượng phân tử khí đủ nhiều để tạo ra ma sát và nhiệt lượng",
      en: "Enough gases to cause friction and create heat" },
    { vi: "Do tầng trung lưu ở cao hơn nên gần Mặt Trời hơn và nóng hơn",
      en: "Because higher layers are closer to the Sun and thus hotter" },
    { vi: "Tia lửa điện tự phát từ vũ trụ",
      en: "Spontaneous electric sparks from space" },
    { vi: "Tốc độ thiên thạch tự dưng dừng lại",
      en: "Meteors suddenly stopping" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Mật độ khí ở tầng trung lưu đủ để tạo ra ma sát cực mạnh thiêu rụi thiên thạch.",
        en: "Correct! Gas molecules in the mesosphere generate friction and heat that burns meteors." },
  no: { vi: "Chưa đúng — và đây là chỗ rất dễ nhầm: lên cao KHÔNG làm ta gần Mặt Trời hơn đáng kể. Thứ đốt cháy thiên thạch là MA SÁT với các phân tử khí, không phải nhiệt từ Mặt Trời.",
        en: "Incorrect — and this is a common trap: going higher does not meaningfully bring you closer to the Sun. What burns meteors is FRICTION with gas molecules, not solar heat." },
  hint: { vi: "Khi hai vật cọ xát với tốc độ cực lớn sẽ sinh ra nhiệt năng rất cao.",
          en: "Extreme speed friction between objects generates high thermal heat." },
  lv: 2,
  src: "nasaSpaceplaceMeso",
  srcQuote: "But when they hit the mesosphere, there are enough gases to cause friction and create heat.",
  srcChecked: "2026-08-06"
};
