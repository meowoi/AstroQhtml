/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclss-three-systems",
  topic: { vi: "HỆ GIỮ MẠNG SỐNG",
           en: "LIFE SUPPORT" },
  q: { vi: "Hệ thống ECLSS trên Trạm Vũ trụ Quốc tế gồm ba bộ phận chính nào?",
       en: "Which three key components make up the space station's ECLSS?" },
  opts: [
    { vi: "Hệ thu hồi nước, hệ làm mới không khí, hệ sinh oxy",
      en: "Water Recovery, Air Revitalization, and Oxygen Generation" },
    { vi: "Hệ radar, hệ liên lạc, hệ dẫn đường",
      en: "Radar, communications, and navigation" },
    { vi: "Hệ pin mặt trời, hệ ắc quy, hệ dây điện",
      en: "Solar arrays, batteries, and wiring" },
    { vi: "Hệ nhà bếp, hệ giường ngủ, hệ phòng tập",
      en: "Galley, sleeping quarters, and gym" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! Ba bộ phận: <b>hệ thu hồi nước</b>, <b>hệ làm mới không khí</b> và <b>hệ sinh oxy</b>. Chú ý ba hệ nối vào nhau thành một VÒNG: hơi ẩm thở ra được hứng lại thành nước, nước lại bị tách ra để lấy oxy.",
        en: "Right! Three components: <b>Water Recovery</b>, <b>Air Revitalization</b> and <b>Oxygen Generation</b>. Notice how they close a LOOP: exhaled moisture is captured as water, and water is split to yield oxygen." },
  no: { vi: "Chưa đúng! ECLSS lo <b>không khí và nước</b>, không lo liên lạc hay điện. Ba bộ phận là thu hồi nước · làm mới không khí · sinh oxy.",
        en: "Not quite! ECLSS handles <b>air and water</b>, not comms or power. The three are water recovery, air revitalization and oxygen generation." },
  hint: { vi: "Ở Trái Đất nước chảy vào từ vòi và chảy ra cống. Trên trạm không có hai đầu ấy — nên phải làm gì với đầu ra?",
          en: "On Earth water flows in from a tap and out to a drain. The station has neither - so what must happen to the output?" },
  lv: 1,
  src: "eclss",
  srcQuote: "ECLSS includes three key components - the Water Recovery System, the Air Revitalization System and the Oxygen Generation System.",
  srcChecked: "2026-08-22"
};
