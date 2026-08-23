/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "gaia-3d-map-of-galaxy",
  topic: { vi: "TÀU GAIA",
           en: "THE GAIA MISSION" },
  q: { vi: "Tàu Gaia của ESA làm việc gì?",
       en: "What did ESA's Gaia spacecraft do?" },
  opts: [
    { vi: "Hạ cánh xuống Sao Hoả",
        en: "Land on Mars" },
    { vi: "Chở người lên Mặt Trăng",
        en: "Carry people to the Moon" },
    { vi: "Dựng bản đồ ba chiều của thiên hà từ gần hai tỉ vật thể",
        en: "Build a three-dimensional map of our Galaxy from nearly two billion objects" },
    { vi: "Đo mực nước biển của Trái Đất",
        en: "Measure Earth's sea level" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! ESA ghi Gaia đã dựng <b>tấm bản đồ ba chiều lớn nhất và chính xác nhất</b> về thiên hà của chúng ta, bằng cách khảo sát gần hai tỉ vật thể.",
        en: "Right! ESA says Gaia built <b>the largest, most precise three-dimensional map</b> of our Galaxy by surveying nearly two billion objects." },
  no: { vi: "Chưa đúng! Gaia không hạ cánh ở đâu cả — nó ở trong không gian và <b>dựng bản đồ ba chiều</b> của thiên hà.",
        en: "Not quite! Gaia never landed anywhere - it stayed in space and <b>mapped our Galaxy in three dimensions</b>." },
  hint: { vi: "Biệt danh của nhiệm vụ này là \"người khảo sát một tỉ ngôi sao\".",
          en: "This mission's nickname is \"the billion star surveyor\"." },
  lv: 1,
  src: "gaia",
  srcQuote: "Gaia built the largest, most precise three-dimensional map of our Galaxy by surveying nearly two billion objects.",
  srcChecked: "2026-08-22"
};
