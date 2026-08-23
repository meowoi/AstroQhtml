/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "gaia-measures-position-and-motion",
  topic: { vi: "TÀU GAIA",
           en: "THE GAIA MISSION" },
  q: { vi: "Gaia ghi lại những gì về mỗi ngôi sao?",
       en: "What did Gaia record about each star?" },
  opts: [
    { vi: "Vị trí, khoảng cách, chuyển động và độ sáng thay đổi",
        en: "Its position, distance, movement and changes in brightness" },
    { vi: "Chỉ màu sắc của nó",
        en: "Only its colour" },
    { vi: "Chỉ tên của nó",
        en: "Only its name" },
    { vi: "Chỉ khoảng cách tới Trái Đất",
        en: "Only its distance from Earth" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! ESA ghi Gaia đo chính xác <b>vị trí, khoảng cách, chuyển động và độ sáng thay đổi</b> của từng ngôi sao — có đủ bốn thứ đó mới dựng được bản đồ ba chiều.",
        en: "Right! ESA says Gaia precisely charted each star's <b>position, distance, movement and changes in brightness</b> - all four are needed to build a 3D map." },
  no: { vi: "Chưa đúng! Chỉ một con số thì không dựng nổi bản đồ ba chiều. Gaia đo <b>vị trí, khoảng cách, chuyển động và độ sáng</b>.",
        en: "Not quite! One number alone cannot build a 3D map. Gaia measured <b>position, distance, movement and brightness</b>." },
  hint: { vi: "Muốn biết một ngôi sao nằm ở đâu trong không gian ba chiều, biết hướng thôi có đủ chưa?",
          en: "To know where a star sits in three-dimensional space, is knowing its direction enough?" },
  lv: 2,
  src: "gaia",
  srcQuote: "It precisely charted their positions, distances, movements, and changes in brightness.",
  srcChecked: "2026-08-22"
};
