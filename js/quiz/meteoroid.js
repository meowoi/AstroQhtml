/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteoroid",
  topic: { vi: "THIÊN THẠCH NHỎ",
           en: "METEOROID" },
  q: { vi: "Meteoroid (thiên thạch nhỏ) là gì?",
       en: "What is a meteoroid?" },
  opts: [
    { vi: "Vệt sáng vụt qua trời đêm",
      en: "A streak of light flashing across the night sky" },
    { vi: "Hòn đá đang bay trong không gian, từ hạt bụi tới tiểu hành tinh nhỏ",
      en: "A rock travelling in space, from a dust grain up to a small asteroid" },
    { vi: "Hòn đá đã rơi xuống và nằm trên mặt đất",
      en: "A rock that has landed and lies on the ground" },
    { vi: "Một hành tinh lùn ở vành đai Kuiper",
      en: "A dwarf planet in the Kuiper Belt" }
  ],
  a: 1,
  ok: { vi: "Chuẩn! NASA định nghĩa meteoroid là <b>“đá không gian” có cỡ từ hạt bụi tới tiểu hành tinh nhỏ</b> — điểm quan trọng nhất là nó vẫn <b>đang ở trong không gian</b>.",
        en: "Exactly! NASA defines meteoroids as <b>space rocks ranging from dust grains to small asteroids</b> — the key point is that they are still <b>out in space</b>." },
  no: { vi: "Chưa đúng! Meteoroid vẫn đang <b>trong không gian</b>. Vệt sáng trên trời là <b>meteor</b>, còn hòn đá nằm trên đất là <b>meteorite</b>.",
        en: "Not quite! A meteoroid is still <b>in space</b>. The streak in the sky is a <b>meteor</b>; the rock on the ground is a <b>meteorite</b>." },
  hint: { vi: "Cả ba từ meteoroid / meteor / meteorite chỉ khác nhau ở <b>nơi</b> hòn đá đang ở.",
          en: "Meteoroid / meteor / meteorite differ only by <b>where</b> the rock is." },
  lv: 1,
  src: "meteor"
};
