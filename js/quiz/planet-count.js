/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "planet-count",
  topic: { vi: "HÀNH TINH",
           en: "PLANET" },
  q: { vi: "Hệ Mặt Trời của chúng ta có bao nhiêu hành tinh?",
       en: "How many planets are in our solar system?" },
  opts: [
    { vi: "7 hành tinh",
      en: "7 planets" },
    { vi: "8 hành tinh",
      en: "8 planets" },
    { vi: "9 hành tinh",
      en: "9 planets" },
    { vi: "12 hành tinh",
      en: "12 planets" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA ghi rõ hệ Mặt Trời có <b>8 hành tinh</b>: Sao Thuỷ, Sao Kim, Trái Đất, Sao Hoả, Sao Mộc, Sao Thổ, Sao Thiên Vương và Sao Hải Vương.",
        en: "Correct! NASA states our solar system has <b>8 planets</b>: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus and Neptune." },
  no: { vi: "Chưa đúng! Có <b>8 hành tinh</b>. Sao Diêm Vương từng được xem là hành tinh thứ chín, nhưng năm 2006 IAU xếp lại nó thành <b>hành tinh lùn</b>.",
        en: "Not quite! There are <b>8 planets</b>. Pluto was once counted as the ninth, but in 2006 the IAU reclassified it as a <b>dwarf planet</b>." },
  hint: { vi: "Đếm từ Sao Thuỷ ra tới Sao Hải Vương — và nhớ rằng Sao Diêm Vương đã “đổi nghề”.",
          en: "Count from Mercury out to Neptune — and remember Pluto changed job title." },
  lv: 1,
  src: "planet"
};
