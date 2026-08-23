/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "rollout-arrays-augment",
  topic: { vi: "ĐIỆN TRÊN TRẠM",
           en: "POWER ON THE STATION" },
  q: { vi: "Những tấm pin mặt trời cuộn được lắp thêm lên Trạm Vũ trụ Quốc tế làm gì với tám tấm pin chính?",
       en: "What do the roll-out solar arrays do to the space station's eight main arrays?" },
  opts: [
    { vi: "THÊM VÀO tám tấm cũ, không thay thế chúng",
      en: "They AUGMENT the eight main arrays rather than replacing them" },
    { vi: "Thay thế hoàn toàn tám tấm cũ",
      en: "They replace all eight completely" },
    { vi: "Che kín tám tấm cũ để bảo vệ",
      en: "They cover the eight to protect them" },
    { vi: "Không liên quan gì tới tám tấm cũ",
      en: "They have nothing to do with the eight" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! Chúng <b>THÊM VÀO</b> tám tấm chính, sinh <b>hơn 20 kilowatt</b> và giúp trạm tăng <b>30% sản lượng điện</b>. Thêm vào thì không có khoảnh khắc nào trạm yếu điện — mà máy lọc nước, lọc không khí và sinh oxy đều cần điện.",
        en: "Right! They <b>AUGMENT</b> the eight main arrays, producing <b>more than 20 kilowatts</b> and enabling a <b>30% increase</b> in power. Augmenting means no moment of reduced power - and the water, air and oxygen systems all need power." },
  no: { vi: "Chưa đúng! Chúng <b>thêm vào</b> chứ không thay thế. Muốn thay thì phải tháo cái cũ ra trước, và quãng thiếu điện đó là thứ không ai muốn trên một con tàu có người ở.",
        en: "Not quite! They <b>augment</b> rather than replace. Replacing would mean removing the old first - and a gap in power is not something you want on a crewed vehicle." },
  hint: { vi: "Ngoài quỹ đạo không có xưởng nào để kéo con tàu về. Vậy sửa một cỗ máy không dừng lại được thì phải nghĩ thế nào?",
          en: "There is no workshop in orbit to tow the station to. So how do you upgrade a machine that cannot stop?" },
  lv: 2,
  src: "issAssembly",
  srcQuote: "The roll-out solar arrays augment the International Space Station's eight main solar arrays.",
  srcChecked: "2026-08-22"
};
