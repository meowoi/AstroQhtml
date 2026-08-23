/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "four-forces-on-a-rocket",
  topic: { vi: "BỐN LỰC",
           en: "FOUR FORCES" },
  q: { vi: "Khi đang bay, một tên lửa chịu bốn lực nào?",
       en: "In flight, which four forces act on a rocket?" },
  opts: [
    { vi: "Từ trường, điện, nhiệt, âm thanh",
      en: "Magnetism, electricity, heat, sound" },
    { vi: "Lực hút, lực đẩy, lực xoáy, lực nén",
      en: "Attraction, repulsion, torsion, compression" },
    { vi: "Chỉ có lực đẩy và trọng lượng",
      en: "Only thrust and weight" },
    { vi: "Trọng lượng, lực đẩy, lực nâng và lực cản",
      en: "Weight, thrust, lift and drag" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! Bốn lực là <b>trọng lượng</b>, <b>lực đẩy</b>, và hai lực khí động: <b>lực nâng</b> và <b>lực cản</b>. NASA ví tương quan giữa chúng với sợi dây trong một cuộc <b>kéo co</b>.",
        en: "Right! The four are <b>weight</b>, <b>thrust</b>, and the aerodynamic forces <b>lift</b> and <b>drag</b>. NASA compares their interplay to the rope in a <b>tug-of-war</b>." },
  no: { vi: "Chưa đúng! Đúng bốn lực: <b>trọng lượng · lực đẩy · lực nâng · lực cản</b> — hai cái sau là lực khí động.",
        en: "Not quite! Exactly four: <b>weight · thrust · lift · drag</b> - the last two are aerodynamic." },
  hint: { vi: "Máy bay cũng chịu đúng bốn lực ấy. Khác nhau là ở chỗ lực nào dùng để thắng trọng lượng.",
          en: "An airplane feels the same four. The difference is which one is used to overcome weight." },
  lv: 1,
  src: "fourRocketForces",
  srcQuote: "a rocket is subjected to four forces; weight, thrust, and the aerodynamic forces, lift and drag",
  srcChecked: "2026-08-22"
};
