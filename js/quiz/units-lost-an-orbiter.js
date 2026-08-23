/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "units-lost-an-orbiter",
  topic: { vi: "ĐƠN VỊ ĐO",
           en: "UNITS OF MEASURE" },
  q: { vi: "Tàu Mars Climate Orbiter mất vì lý do gì?",
       en: "Why was the Mars Climate Orbiter lost?" },
  opts: [
    { vi: "Một thiên thạch đâm vào nó",
      en: "A meteoroid struck it" },
    { vi: "Hết nhiên liệu giữa đường",
      en: "It ran out of fuel on the way" },
    { vi: "Một con ốc bị lỏng",
      en: "A bolt came loose" },
    { vi: "Phần mềm dưới mặt đất dùng hệ đơn vị Anh, phần mềm trên tàu dùng hệ mét",
      en: "Ground software used English units while onboard software worked in metric" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! <b>Phần mềm dưới mặt đất dùng hệ Anh, phần mềm trên tàu dùng hệ mét.</b> Cả hai bên đều tính ĐÚNG — thứ sai là hai bên không nói cùng một thứ tiếng về những con số.",
        en: "Right! <b>Ground software used English units; onboard software used metric.</b> Both sides computed correctly - what failed was that they were not speaking the same language about numbers." },
  no: { vi: "Chưa đúng! Không có va chạm hay hỏng hóc nào. Hai phần mềm dùng <b>hai hệ đơn vị khác nhau</b>, và sai số đó đưa tàu tới quá gần Sao Hoả.",
        en: "Not quite! There was no collision or breakdown. Two pieces of software used <b>two different unit systems</b>, and that error sent the craft too close to Mars." },
  hint: { vi: "Một con số trần trụi như \"5\" không nói được gì: 5 mét hay 5 dặm?",
          en: "A bare number like \"5\" says nothing on its own: 5 meters or 5 miles?" },
  lv: 2,
  src: "marsClimateOrbiter",
  srcQuote: "Ground software used English units, while onboard software worked in metric.",
  srcChecked: "2026-08-22"
};
