/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "parallax-two-viewings",
  topic: { vi: "ĐO BẰNG GÓC",
           en: "MEASURING BY ANGLES" },
  q: { vi: "Muốn đo khoảng cách tới một ngôi sao gần bằng thị sai, phải quan sát nó thế nào?",
       en: "To measure a nearby star's distance by parallax, how must you observe it?" },
  opts: [
    { vi: "Hai lần, vào lúc Trái Đất ở hai phía đối diện của Mặt Trời",
      en: "Twice, when Earth is at opposite sides of the Sun" },
    { vi: "Một lần duy nhất, vào đúng giữa trưa",
      en: "Once only, exactly at noon" },
    { vi: "Liên tục suốt một đêm",
      en: "Continuously through one night" },
    { vi: "Từ hai kính thiên văn đặt cạnh nhau",
      en: "From two telescopes side by side" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! Phải xem <b>hai lần</b>, khi Trái Đất ở <b>hai phía đối diện</b> Mặt Trời — hai vị trí ấy chính là \"hai con mắt\" cách nhau bằng cả đường kính quỹ đạo.",
        en: "Right! You need <b>two viewings</b>, with Earth on <b>opposite sides</b> of the Sun - those two spots are the \"two eyes\", separated by the whole orbital diameter." },
  no: { vi: "Chưa đúng! Một lần xem thì không có gì để so. Cần <b>hai lần</b>, ở <b>hai phía đối diện</b> Mặt Trời, để ngôi sao có vẻ nhích đi so với nền trời.",
        en: "Not quite! One viewing gives nothing to compare. You need <b>two</b>, from <b>opposite sides</b> of the Sun, so the star appears to shift against the background." },
  hint: { vi: "Giơ một ngón tay lên, nhắm mắt trái rồi đổi sang mắt phải. Vì sao ngón tay như nhảy sang bên?",
          en: "Hold up a finger, close your left eye, then switch to the right. Why does it seem to jump?" },
  lv: 2,
  src: "stellarParallax",
  srcQuote: "This requires viewing the star on two occasions, when Earth is at opposite sides of the Sun",
  srcChecked: "2026-08-22"
};
