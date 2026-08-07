/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-red-dwarf-faint",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Tại sao các nhà quan sát bầu trời không thể dùng mắt thường để nhìn thấy các sao lùn đỏ?",
       en: "Why can't stargazers see red dwarfs with the unaided eye?" },
  opts: [
    { vi: "Vì chúng quá mờ đối với mắt thường",
      en: "Because red dwarfs are too faint to see with the unaided eye" },
    { vi: "Vì sao lùn đỏ hoàn toàn không tỏa ra ánh sáng",
      en: "Because red dwarfs emit zero light" },
    { vi: "Vì sao lùn đỏ nấp đằng sau Mặt Trăng ban đêm",
      en: "Because red dwarfs hide behind the Moon" },
    { vi: "Vì bầu khí quyển Trái Đất hấp thụ toàn bộ ánh sáng đỏ",
      en: "Because the atmosphere absorbs all red light" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Mặc dù chiếm đa số trong thiên hà, sao lùn đỏ quá mờ để mắt thường nhìn thấy.",
        en: "Correct! Though most numerous in galaxy, red dwarfs are too faint for eyes." },
  no: { vi: "Chưa đúng. Sao lùn đỏ phát độ sáng rất nhỏ nên cường độ ánh sáng quá mờ so với mắt người.",
        en: "Incorrect. Red dwarfs produce low luminosity, making them too dim for naked eyes." },
  hint: { vi: "Độ sáng phát ra của chúng rất nhỏ so với các sao lớn.",
          en: "Their emitted brightness is very low compared to large stars." },
  lv: 3,
  src: "nasaStarTypes",
  srcQuote: "For Stargazers: Red dwarfs are too faint to see with the unaided eye.",
  srcChecked: "2026-08-06"
};
