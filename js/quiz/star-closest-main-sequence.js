/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-closest-main-sequence",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Ngôi sao dải chính nào gần Trái Đất nhất mà con người có thể nhìn thấy bằng mắt thường?",
       en: "Which main sequence star is the closest to Earth that can be seen with the unaided eye?" },
  opts: [
    { vi: "Rigil Kentaurus (Alpha Centauri)",
      en: "Rigil Kentaurus (better known as Alpha Centauri)" },
    { vi: "Sao Sirius",
      en: "Sirius" },
    { vi: "Sao Polaris",
      en: "Polaris" },
    { vi: "Sao Betelgeuse",
      en: "Betelgeuse" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Rigil Kentaurus (Alpha Centauri) thuộc chòm sao Bán Nhân Mã là sao dải chính gần nhất quan sát được bằng mắt thường.",
        en: "Correct! Rigil Kentaurus (Alpha Centauri) is the closest main sequence star visible to unaided eyes." },
  no: { vi: "Chưa đúng. Rigil Kentaurus (Alpha Centauri) chính là ngôi sao dải chính gần nhất nhìn thấy bằng mắt thường.",
        en: "Incorrect. Rigil Kentaurus (Alpha Centauri) is the closest main sequence star seen with naked eyes." },
  hint: { vi: "Ngôi sao này nằm ở chòm sao Bán Nhân Mã thuộc bầu trời phương Nam.",
          en: "This star is located in the southern constellation Centaurus." },
  lv: 2,
  src: "nasaStarTypes",
  srcQuote: "Rigil Kentaurus (better known as Alpha Centauri) in the southern constellation Centaurus is the closest main sequence star that can be seen with the unaided eye.",
  srcChecked: "2026-08-06"
};
