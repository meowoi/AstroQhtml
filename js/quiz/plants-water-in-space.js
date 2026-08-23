/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "plants-water-in-space",
  topic: { vi: "TRỒNG CÂY TRONG KHÔNG GIAN",
           en: "PLANTS IN SPACE" },
  q: { vi: "Vì sao tưới cây trên trạm vũ trụ lại khó, theo NASA?",
       en: "Why is watering plants on the space station hard, according to NASA?" },
  opts: [
    { vi: "Vì nước đóng băng ngay lập tức",
      en: "Because water freezes instantly" },
    { vi: "Vì không có nước trên trạm",
      en: "Because there is no water on the station" },
    { vi: "Vì chất lỏng tụ thành bong bóng, rễ có thể chết đuối HOẶC bị bọc kín trong không khí",
      en: "Because fluids form bubbles, so roots can either drown or be engulfed by air" },
    { vi: "Vì cây không cần nước trong không gian",
      en: "Because plants need no water in space" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! Trong không gian chất lỏng <b>tụ thành bong bóng</b>, nên rễ cây có thể <b>chết đuối trong nước</b> hoặc <b>bị bọc kín trong không khí</b> — hai kiểu chết trái ngược nhau, cùng một nguyên nhân.",
        en: "Right! In space fluids <b>form bubbles</b>, so roots can either <b>drown in water</b> or <b>be engulfed by air</b> - two opposite failures from one cause." },
  no: { vi: "Chưa đúng! Nước có sẵn trên trạm. Vấn đề là nó <b>không tự chảy xuống</b> mà tụ thành bong bóng quanh rễ.",
        en: "Not quite! There is water on the station. The problem is it <b>does not flow downward</b> - it clumps into bubbles around the roots." },
  hint: { vi: "Ở Trái Đất cái gì làm nước chảy xuống qua đất? Bỏ thứ đó đi thì nước làm gì?",
          en: "On Earth, what pulls water down through soil? Remove that, and what does water do?" },
  lv: 3,
  src: "plantsInSpace",
  srcQuote: "the roots would either drown in water or be engulfed by air because of the way fluids in space tend to form bubbles",
  srcChecked: "2026-08-22"
};
