/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "asteroid-belt",
  topic: { vi: "TIỂU HÀNH TINH",
           en: "ASTEROID" },
  q: { vi: "Vành đai tiểu hành tinh chính nằm ở đâu?",
       en: "Where is the main asteroid belt?" },
  opts: [
    { vi: "Giữa Trái Đất và Sao Hoả",
      en: "Between Earth and Mars" },
    { vi: "Giữa Sao Hoả và Sao Mộc",
      en: "Between Mars and Jupiter" },
    { vi: "Bên ngoài Sao Hải Vương",
      en: "Beyond Neptune" },
    { vi: "Ngay quanh Mặt Trăng",
      en: "Right around the Moon" }
  ],
  a: 1,
  ok: { vi: "Chính xác! Vành đai chính nằm <b>giữa Sao Hoả và Sao Mộc</b>. NASA ước tính ở đó có khoảng <b>1,1–1,9 triệu</b> tiểu hành tinh lớn hơn 1 km.",
        en: "Exactly! The main belt orbits <b>between Mars and Jupiter</b>. NASA estimates it holds roughly <b>1.1 to 1.9 million</b> asteroids larger than 1 km." },
  no: { vi: "Chưa đúng! Vành đai chính ở <b>giữa Sao Hoả và Sao Mộc</b>. Vùng bên ngoài Sao Hải Vương là vành đai Kuiper — nơi của các vật thể băng.",
        en: "Not quite! The main belt lies <b>between Mars and Jupiter</b>. The region beyond Neptune is the Kuiper Belt, home to icy bodies." },
  hint: { vi: "Nó ngăn giữa hành tinh đỏ và hành tinh khổng lồ nhất.",
          en: "It sits between the red planet and the biggest giant." },
  lv: 2,
  src: "aster"
};
