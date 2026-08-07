/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-partial-crescent-shape",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Khi xảy ra nhật thực một phần (partial solar eclipse), Mặt Trời có hình dạng như thế nào?",
       en: "What shape does the Sun appear to have during a partial solar eclipse?" },
  opts: [
    { vi: "Mặt Trời có hình lưỡi liềm",
      en: "The Sun appears to have a crescent shape" },
    { vi: "Mặt Trời có hình ngôi sao năm cánh",
      en: "The Sun turns into a five-pointed star" },
    { vi: "Mặt Trời hoàn toàn biến mất trong bóng tối đen thẫm",
      en: "The Sun vanishes completely in total darkness" },
    { vi: "Mặt Trời biến thành hình vuông",
      en: "The Sun turns into a square" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Do ba thiên thể không thẳng hàng tuyệt đối, phần Mặt Trời còn lộ ra tạo thành hình lưỡi liềm.",
        en: "Correct! Because alignment is not perfect, the unblocked part of the Sun looks like a crescent." },
  no: { vi: "Chưa đúng. Nhật thực một phần chỉ che khuất một góc, làm Mặt Trời có hình lưỡi liềm khuyết.",
        en: "Incorrect. A partial eclipse covers only a section, giving the Sun a crescent shape." },
  hint: { vi: "Hình dạng khuyết hệt như hình dáng Mặt Trăng đầu tháng.",
          en: "The shape resembles a crescent moon." },
  lv: 1,
  src: "nasaEclipseTypes",
  srcQuote: "Only a part of the Sun will appear to be covered, giving it a crescent shape.",
  srcChecked: "2026-08-06"
};
