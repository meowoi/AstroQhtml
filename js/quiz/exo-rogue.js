/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "exo-rogue",
  topic: { vi: "NGOẠI HÀNH TINH",
           en: "EXOPLANET" },
  q: { vi: "Hầu hết ngoại hành tinh đều quay quanh một ngôi sao. Nhưng có loại không thuộc về ngôi sao nào cả — NASA gọi chúng là gì?",
       en: "Most exoplanets orbit a star. But some belong to no star at all — what does NASA call those?" },
  opts: [
    { vi: "Hành tinh lùn",
      en: "Dwarf planets" },
    { vi: "Hành tinh lang thang (rogue planet)",
      en: "Rogue planets" },
    { vi: "Sao chổi khổng lồ",
      en: "Giant comets" },
    { vi: "Chúng không được coi là ngoại hành tinh",
      en: "They don't count as exoplanets" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA gọi chúng là <b>rogue planet — hành tinh lang thang</b>: bay tự do, <b>không bị ràng vào ngôi sao nào</b>. Và chúng <b>vẫn</b> được tính là ngoại hành tinh, vì định nghĩa chỉ đòi “ở ngoài hệ Mặt Trời của chúng ta”.",
          en: "Yes! NASA calls them <b>rogue planets</b>: free-floating and <b>untethered to any star</b>. They still <b>do</b> count as exoplanets, because the definition only asks that they lie beyond our solar system." },
  no: { vi: "Chưa đúng! Chúng là <b>hành tinh lang thang (rogue planet)</b>. Điểm hay là chúng vẫn được coi là ngoại hành tinh — định nghĩa của NASA là “bất kỳ hành tinh nào ở ngoài hệ Mặt Trời”, không đòi phải có sao chủ.",
          en: "Not quite! They are <b>rogue planets</b>. The neat part: they still count as exoplanets — NASA's definition is “any planet beyond our solar system”, with no host star required." },
  hint: { vi: "Một từ tiếng Anh chỉ kẻ đi lang thang, không theo ai.",
            en: "An English word for a wanderer who follows nobody." },
  lv: 3,
  src: "exo",
  srcQuote: "An exoplanet is any planet beyond our solar system. Most of them orbit other stars, but some free-floating exoplanets, called rogue planets, are untethered to any star.",
  srcChecked: "2026-08-19"
};
