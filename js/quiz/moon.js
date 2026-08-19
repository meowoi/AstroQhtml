/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "moon",
  topic: { vi: "VỆ TINH TỰ NHIÊN",
           en: "NATURAL SATELLITE" },
  q: { vi: "Vệ tinh tự nhiên (moon) là gì?",
       en: "What is a moon, or natural satellite?" },
  opts: [
    { vi: "Thiết bị do con người phóng lên quỹ đạo",
      en: "A device humans launched into orbit" },
    { vi: "Vật thể hình thành tự nhiên, quay quanh một hành tinh",
      en: "A naturally-formed body that orbits a planet" },
    { vi: "Một ngôi sao nhỏ quay quanh ngôi sao lớn",
      en: "A small star orbiting a bigger star" },
    { vi: "Hòn đá đã rơi xuống mặt đất",
      en: "A rock that has landed on the ground" }
  ],
  a: 1,
  ok: { vi: "Chuẩn! NASA gọi <b>vật thể hình thành tự nhiên quay quanh hành tinh</b> là mặt trăng (moon) hay vệ tinh tự nhiên. Thứ do con người chế tạo rồi phóng lên thì gọi là <b>vệ tinh nhân tạo</b>.",
        en: "Exactly! NASA calls <b>naturally-formed bodies that orbit planets</b> moons, or planetary satellites. Something humans built and launched is an <b>artificial satellite</b>." },
  no: { vi: "Chưa đúng! Vệ tinh tự nhiên là <b>vật thể tự nhiên quay quanh một hành tinh</b> — chữ “tự nhiên” chính là chỗ khác với vệ tinh nhân tạo.",
        en: "Not quite! A natural satellite is a <b>natural body orbiting a planet</b> — the word “natural” is exactly what sets it apart from an artificial one." },
  hint: { vi: "Chữ quan trọng nhất trong câu hỏi là <b>“tự nhiên”</b>.",
          en: "The key word in the question is <b>“natural”</b>." },
  lv: 1,
  src: "moon"
};
