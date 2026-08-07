/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-sirius-brightest",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Ngôi sao nào sáng nhất trên bầu trời đêm mà con người có thể quan sát bằng mắt thường?",
       en: "Which star is the brightest star in the night sky visible to the unaided eye?" },
  opts: [
    { vi: "Sao Sirius (Sao Thiên Lang)",
      en: "Sirius" },
    { vi: "Sao Proxima Centauri",
      en: "Proxima Centauri" },
    { vi: "Sao Arcturus",
      en: "Arcturus" },
    { vi: "Sao Procyon B",
      en: "Procyon B" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Sirius là ngôi sao sáng nhất trên bầu trời đêm thuộc chòm sao Đại Khuyển.",
        en: "Correct! Sirius is the brightest star in the night sky, located in Canis Major." },
  no: { vi: "Chưa đúng. Sirius (Sao Thiên Lang) mới là ngôi sao tỏa sáng rực rỡ nhất bầu trời đêm.",
        en: "Incorrect. Sirius is the brightest glowing star in our nighttime sky." },
  hint: { vi: "Ngôi sao này tỏa ánh sáng màu trắng xanh rực rỡ.",
          en: "This star shines with a brilliant blue-white light." },
  lv: 1,
  src: "nasaStarTypes",
  srcQuote: "Sirius – the brightest star in the night sky – in the northern constellation Canis Major.",
  srcChecked: "2026-08-06"
};
