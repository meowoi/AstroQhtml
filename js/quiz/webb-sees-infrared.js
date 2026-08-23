/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "webb-sees-infrared",
  topic: { vi: "KÍNH WEBB",
           en: "THE WEBB TELESCOPE" },
  q: { vi: "Vì sao kính Webb thấy được ngôi sao đang nằm trong một đám mây bụi dày?",
       en: "Why can the Webb telescope see a star hidden inside a thick cloud of dust?" },
  opts: [
    { vi: "Vì nó bay tới sát đám mây bụi đó",
        en: "Because it flies right up to that dust cloud" },
    { vi: "Vì nó dò tia hồng ngoại, không chỉ ánh sáng thường",
        en: "Because it detects infrared light, not just visible light" },
    { vi: "Vì nó thổi đám bụi ra xa",
        en: "Because it blows the dust away" },
    { vi: "Vì bụi trong suốt với mọi loại ánh sáng",
        en: "Because dust is transparent to every kind of light" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! NASA ghi công nghệ <b>dò hồng ngoại</b> của Webb hé lộ phần vũ trụ đang bị che khuất — trong đó có những ngôi sao bọc kín trong mây bụi.",
        en: "Right! NASA says Webb's <b>infrared-detecting</b> technology reveals the hidden universe - including stars shrouded in clouds of dust." },
  no: { vi: "Chưa đúng! Webb không bay tới gần và cũng không dọn được đám bụi. Nó dò <b>tia hồng ngoại</b> — loại ánh sáng đi qua được mây bụi.",
        en: "Not quite! Webb neither flies close nor clears the dust away. It detects <b>infrared light</b>, which gets through dust clouds." },
  hint: { vi: "Bụi che được ánh sáng thường, nhưng có một loại ánh sáng khác lọt qua được. Webb dò loại nào?",
          en: "Dust blocks visible light, but another kind of light gets through. Which kind does Webb detect?" },
  lv: 3,
  src: "webbSci",
  srcQuote: "Webb's infrared-detecting technology reveals the hidden universe to our eyes: stars shrouded in clouds of dust",
  srcChecked: "2026-08-22"
};
