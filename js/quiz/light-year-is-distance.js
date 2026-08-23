/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "light-year-is-distance",
  topic: { vi: "NĂM ÁNH SÁNG",
           en: "THE LIGHT-YEAR" },
  q: { vi: "Một năm ánh sáng đo cái gì?",
       en: "What does a light-year measure?" },
  opts: [
    { vi: "Một khoảng thời gian",
      en: "A span of time" },
    { vi: "Độ sáng của một ngôi sao",
      en: "The brightness of a star" },
    { vi: "Một khoảng cách",
      en: "A distance" },
    { vi: "Tuổi của một ngôi sao",
      en: "The age of a star" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! NASA nói rõ: năm ánh sáng là <b>quãng đường</b> ánh sáng đi được trong một năm. Cái tên có chữ \"năm\" nên rất dễ tưởng nó đo thời gian.",
        en: "Right! NASA is explicit: a light-year is the <b>distance</b> light travels in one year. The word \"year\" makes it easy to mistake for time." },
  no: { vi: "Chưa đúng! Dù trong tên có chữ \"năm\", nó là một <b>khoảng cách</b> — quãng đường ánh sáng đi trong một năm.",
        en: "Not quite! Despite the word \"year\", it is a <b>distance</b> - how far light travels in one year." },
  hint: { vi: "Nếu ai đó nói \"nhà tôi cách đây mười phút\", họ đang nói về thời gian hay quãng đường?",
          en: "If someone says \"my house is ten minutes away\", are they telling you a time or a distance?" },
  lv: 1,
  src: "lightYear",
  srcQuote: "Light-year is the distance light travels in one year.",
  srcChecked: "2026-08-22"
};
