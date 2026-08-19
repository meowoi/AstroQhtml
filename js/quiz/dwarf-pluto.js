/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "dwarf-pluto",
  topic: { vi: "HÀNH TINH LÙN",
           en: "DWARF PLANET" },
  q: { vi: "Sao Diêm Vương (Pluto) hiện được xếp vào nhóm nào?",
       en: "What group is Pluto classified in today?" },
  opts: [
    { vi: "Hành tinh",
      en: "A planet" },
    { vi: "Hành tinh lùn",
      en: "A dwarf planet" },
    { vi: "Vệ tinh của Sao Hải Vương",
      en: "A moon of Neptune" },
    { vi: "Sao chổi",
      en: "A comet" }
  ],
  a: 1,
  ok: { vi: "Đúng! Pluto là một trong <b>năm hành tinh lùn</b> mà IAU đã công nhận. Tính từ Mặt Trời ra, năm cái đó là <b>Ceres, Pluto, Haumea, Makemake và Eris</b>.",
          en: "Yes! Pluto is one of the <b>five dwarf planets</b> the IAU recognises. In order of distance from the Sun they are <b>Ceres, Pluto, Haumea, Makemake and Eris</b>." },
  no: { vi: "Chưa đúng! Pluto là <b>hành tinh lùn</b>, cùng nhóm với Ceres, Haumea, Makemake và Eris.",
          en: "Not quite! Pluto is a <b>dwarf planet</b>, in the same group as Ceres, Haumea, Makemake and Eris." },
  hint: { vi: "Nó gần thành hành tinh — chỉ thiếu đúng một bước.",
            en: "It almost qualifies as a planet — it just misses one step." },
  lv: 1,
  src: "dwarf",
  srcQuote: "In order of distance from the Sun they are: Ceres, Pluto, Haumea, Makemake, and Eris.",
  srcChecked: "2026-08-19"
};
