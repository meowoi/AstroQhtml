/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-partial-imperfect-alignment",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Hiện tượng nguyệt thực một phần (partial lunar eclipse) diễn ra khi nào?",
       en: "When does a partial lunar eclipse happen?" },
  opts: [
    { vi: "Khi sự thẳng hàng giữa Mặt Trời, Trái Đất và Mặt Trăng không hoàn hảo, làm Mặt Trăng chỉ đi qua một phần bóng umbra",
      en: "An imperfect alignment of Sun, Earth and Moon results in the Moon passing through only part of Earth's umbra" },
    { vi: "Khi Mặt Trăng bị nứt làm đôi",
      en: "When the Moon splits in half" },
    { vi: "Khi Trái Đất thu nhỏ kích thước",
      en: "When Earth shrinks in volume" },
    { vi: "Khi Mặt Trời tắt đi một nửa",
      en: "When the Sun turns off half its light" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Do sự thẳng hàng không tuyệt đối, đĩa Mặt Trăng chỉ lướt qua một phần của vùng bóng umbra.",
        en: "Correct! Imperfect alignment causes the Moon to cross only a portion of Earth's umbra." },
  no: { vi: "Chưa đúng. Nguyệt thực một phần xảy ra do ba thiên thể không xếp thẳng hàng hoàn hảo.",
        en: "Incorrect. Imperfect spatial alignment means only part of the Moon enters the umbra." },
  hint: { vi: "Sự thẳng hàng không hoàn hảo khiến chỉ một phần đĩa Trăng chìm vào bóng tối.",
          en: "Non-ideal positioning means only a segment of the lunar disk dips into shadow." },
  lv: 2,
  src: "nasaMoonEclipses",
  srcQuote: "An imperfect alignment of Sun, Earth and Moon results in the Moon passing through only part of Earth's umbra.",
  srcChecked: "2026-08-06"
};
