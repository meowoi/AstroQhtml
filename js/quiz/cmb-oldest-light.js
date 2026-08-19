/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "cmb-oldest-light",
  topic: { vi: "BỨC XẠ NỀN VŨ TRỤ",
           en: "COSMIC MICROWAVE BACKGROUND" },
  q: { vi: "Bức xạ nền vũ trụ giữ “kỷ lục” gì trong mọi thứ ta quan sát được?",
       en: "What “record” does the cosmic microwave background hold among everything we can observe?" },
  opts: [
    { vi: "Là ánh sáng CỔ NHẤT ta quan sát được",
      en: "It is the OLDEST light we can observe" },
    { vi: "Là ánh sáng sáng nhất trên trời",
      en: "It is the brightest light in the sky" },
    { vi: "Là ánh sáng gần Trái Đất nhất",
      en: "It is the closest light to Earth" },
    { vi: "Là ánh sáng nóng nhất từng đo được",
      en: "It is the hottest light ever measured" }
  ],
  a: 0,
  ok: { vi: "Đúng! NASA nói bức xạ nền vũ trụ là <b>ánh sáng cổ nhất mà ta quan sát được trong vũ trụ</b> — thứ ánh sáng ấy lên đường từ khi vũ trụ còn rất trẻ, và đến nay vẫn còn dò được.",
          en: "Yes! NASA says the cosmic microwave background is <b>the oldest light we can observe in the universe</b> — light that set out when the universe was very young, and is still detectable today." },
  no: { vi: "Chưa đúng! Nó không phải sáng nhất hay nóng nhất, mà là <b>cổ nhất</b>: ánh sáng xưa nhất ta quan sát được trong vũ trụ.",
          en: "Not quite! It isn't the brightest or hottest — it is the <b>oldest</b>: the most ancient light we can observe in the universe." },
  hint: { vi: "Nghĩ về TUỔI của ánh sáng, không phải độ sáng của nó.",
            en: "Think about the light's AGE, not its brightness." },
  lv: 2,
  src: "cosmos",
  srcQuote: "This glow, still detectable today, is called the cosmic microwave background. It is the oldest light we can observe in the universe.",
  srcChecked: "2026-08-19"
};
