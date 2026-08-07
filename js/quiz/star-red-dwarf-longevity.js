/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-red-dwarf-longevity",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Tại sao các sao lùn đỏ lại có thể tồn tại và cháy ổn định hàng nghìn tỷ năm?",
       en: "Why can red dwarfs steadily burn through their hydrogen for trillions of years?" },
  opts: [
    { vi: "Sự cuộn đảo đối lưu liên tục mang nguồn hydro mới vào lõi giúp sao cháy rất chậm và ổn định",
      en: "Constant churning brings fresh hydrogen to the core, burning steadily over trillions of years" },
    { vi: "Vì chúng lấy nhiên liệu từ các hành tinh xung quanh",
      en: "Because they draw fuel from surrounding planets" },
    { vi: "Vì chúng không xảy ra phản ứng hạt nhân",
      en: "Because no nuclear fusion occurs inside them" },
    { vi: "Vì chúng được sưởi ấm từ các sao khác",
      en: "Because they are heated by other stars" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Sự cuộn chảy đối lưu mang hydro liên tục vào lõi giúp sao lùn đỏ duy trì sự sống hàng nghìn tỷ năm.",
        en: "Correct! Convective churning brings fresh hydrogen fuel into the core over trillions of years." },
  no: { vi: "Chưa đúng. Sự cuộn đảo vật chất giúp sao lùn đỏ sử dụng cạn kiệt hydro rất chậm rãi.",
        en: "Incorrect. Material churning allows red dwarfs to consume hydrogen fuel very slowly." },
  hint: { vi: "Dòng đối lưu vật chất liên tục cung cấp nhiên liệu hydro mới cho lõi sao.",
          en: "Convective material currents constantly supply fresh hydrogen to the core." },
  lv: 3,
  src: "nasaStarTypes",
  srcQuote: "Because of this constant churning, red dwarfs can steadily burn through their entire supply of hydrogen over trillions of years without changing their internal structures",
  srcChecked: "2026-08-06"
};
