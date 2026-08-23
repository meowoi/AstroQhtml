/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "andromeda-nearest-large-galaxy",
  topic: { vi: "THIÊN HÀ",
           en: "GALAXIES" },
  q: { vi: "Thiên hà Tiên Nữ là gì so với Dải Ngân Hà của chúng ta?",
       en: "What is the Andromeda galaxy compared with our Milky Way?" },
  opts: [
    { vi: "Một ngôi sao nằm trong Dải Ngân Hà",
        en: "A star inside the Milky Way" },
    { vi: "Một mặt trăng của Trái Đất",
        en: "A moon of Earth" },
    { vi: "Thiên hà xa nhất từng quan sát được",
        en: "The most distant galaxy ever observed" },
    { vi: "Thiên hà lớn gần Dải Ngân Hà nhất",
        en: "The nearest large galaxy to our own" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! NASA ghi Tiên Nữ là <b>thiên hà lớn gần chúng ta nhất</b>, và cũng là thiên hà nặng nhất trong nhóm thiên hà quanh ta.",
        en: "Right! NASA says Andromeda is <b>the nearest large galaxy to our own</b>, and the most massive in our local group of galaxies." },
  no: { vi: "Chưa đúng! Tiên Nữ không phải ngôi sao hay mặt trăng, và cũng không phải thiên hà xa nhất — nó là <b>thiên hà lớn gần ta nhất</b>.",
        en: "Not quite! Andromeda is neither a star nor a moon, nor the most distant galaxy - it is <b>the nearest large galaxy to ours</b>." },
  hint: { vi: "Nó là một thiên hà, và trong số các thiên hà LỚN thì nó là cái gần chúng ta nhất.",
          en: "It is a galaxy, and among the LARGE galaxies it is the closest one to us." },
  lv: 2,
  src: "andromeda",
  srcQuote: "Andromeda is the nearest large galaxy to our own.",
  srcChecked: "2026-08-22"
};
