/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "exoplanet",
  topic: { vi: "NGOẠI HÀNH TINH",
           en: "EXOPLANET" },
  q: { vi: "Ngoại hành tinh (exoplanet) là gì?",
       en: "What is an exoplanet?" },
  opts: [
    { vi: "Hành tinh nằm ngoài hệ Mặt Trời của chúng ta",
      en: "A planet beyond our solar system" },
    { vi: "Hành tinh ở rìa ngoài cùng hệ Mặt Trời",
      en: "A planet at the outer edge of our solar system" },
    { vi: "Hành tinh lùn chưa được đặt tên",
      en: "A dwarf planet that hasn't been named yet" },
    { vi: "Vệ tinh của một hành tinh khác",
      en: "A moon belonging to another planet" }
  ],
  a: 0,
  ok: { vi: "Chuẩn! Ngoại hành tinh là <b>hành tinh nằm ngoài hệ Mặt Trời</b>. Phần lớn quay quanh một ngôi sao khác, nhưng cũng có “hành tinh lang thang” không thuộc ngôi sao nào. NASA đã xác nhận <b>hơn 6.000</b> ngoại hành tinh.",
        en: "Exactly! An exoplanet is <b>any planet beyond our solar system</b>. Most orbit other stars, though some free-floating “rogue planets” belong to no star at all. NASA has confirmed <b>more than 6,000</b> of them." },
  no: { vi: "Chưa đúng! Tiền tố “exo-” nghĩa là <b>bên ngoài</b>: đó là hành tinh <b>ngoài hệ Mặt Trời</b> của chúng ta.",
        en: "Not quite! The prefix “exo-” means <b>outside</b>: it's a planet <b>outside our solar system</b>." },
  hint: { vi: "Tiền tố “exo-” trong tiếng Hy Lạp nghĩa là <b>bên ngoài</b>.",
          en: "The Greek prefix “exo-” means <b>outside</b>." },
  lv: 1,
  src: "exo"
};
