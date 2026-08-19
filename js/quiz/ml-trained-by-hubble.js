/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ml-trained-by-hubble",
  topic: { vi: "HỌC MÁY",
           en: "MACHINE LEARNING" },
  q: { vi: "Để AI biết nhận ra hình dạng các thiên hà, người ta đã cho nó học từ cái gì?",
       en: "To teach an AI to recognise galaxy shapes, what was it trained on?" },
  opts: [
    { vi: "Ảnh hàng nghìn thiên hà do Hubble quan sát",
      en: "Hubble observations of thousands of galaxies" },
    { vi: "Sách giáo khoa thiên văn",
      en: "Astronomy textbooks" },
    { vi: "Bản đồ Trái Đất",
      en: "Maps of Earth" },
    { vi: "Không cần học gì — AI tự biết",
      en: "Nothing — the AI just knows" }
  ],
  a: 0,
  ok: { vi: "Đúng! <b>Ảnh hàng nghìn thiên hà của Hubble đã được dùng để huấn luyện các chương trình AI</b> nhận ra cấu trúc và hình dạng thiên hà — có lúc xét đến từng điểm ảnh. Học máy luôn cần <b>ví dụ</b> để học.",
          en: "Yes! <b>Hubble observations of thousands of galaxies helped train AI programs</b> to identify galaxy structures and forms — sometimes pixel by pixel. Machine learning always needs <b>examples</b>." },
  no: { vi: "Chưa đúng! Học máy không tự biết gì: nó học từ <b>ví dụ</b>. Ở đây ví dụ chính là <b>ảnh hàng nghìn thiên hà do Hubble quan sát</b>.",
          en: "Not quite! Machine learning knows nothing on its own: it learns from <b>examples</b>. Here the examples were <b>Hubble observations of thousands of galaxies</b>." },
  hint: { vi: "Muốn dạy ai nhận ra một thứ, ta phải cho họ xem thật nhiều thứ đó.",
            en: "To teach anyone to recognise something, you show them a great many of it." },
  lv: 1,
  src: "aiHubble",
  srcQuote: "Hubble observations of thousands of galaxies helped train AI programs to identify galaxy structures and forms – sometimes on a pixel-by-pixel basis.",
  srcChecked: "2026-08-19"
};
