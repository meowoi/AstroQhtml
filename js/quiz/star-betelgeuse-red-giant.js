/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-betelgeuse-red-giant",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Trong các tài liệu minh họa của NASA, những ngôi sao như Betelgeuse hay Antares được miêu tả là loại sao nào?",
       en: "In NASA illustrations, stars like Betelgeuse or Antares depict what type of star?" },
  opts: [
    { vi: "Một ngôi sao khổng lồ đỏ (Red giant star)",
      en: "A red giant star" },
    { vi: "Một sao lùn trắng cực nhỏ",
      en: "An extremely small white dwarf" },
    { vi: "Một trạm vũ trụ nhân tạo",
      en: "An artificial space station" },
    { vi: "Một hành tinh đá khô hạn",
      en: "A dry rocky planet" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Betelgeuse và Antares là những ví dụ minh họa điển hình về sao khổng lồ đỏ.",
        en: "Correct! Betelgeuse and Antares are prime illustrative examples of red giant stars." },
  no: { vi: "Chưa đúng. Betelgeuse và Antares đại diện cho loại sao khổng lồ đỏ có màu sắc rực rỡ.",
        en: "Incorrect. Betelgeuse and Antares represent vividly colored red giant stars." },
  hint: { vi: "Đây là loại sao lớn màu đỏ xuất hiện ở giai đoạn sau của tiến hóa sao.",
          en: "This represents large reddish stars in late stellar evolution." },
  lv: 2,
  src: "nasaStarTypes",
  srcQuote: "This illustration depicts a red giant star, like Betelgeuse or Antares.",
  srcChecked: "2026-08-06"
};
