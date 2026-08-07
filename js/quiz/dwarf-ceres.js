/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "dwarf-ceres",
  topic: { vi: "HÀNH TINH LÙN",
           en: "DWARF PLANET" },
  q: { vi: "Hành tinh lùn nào nằm trong vành đai tiểu hành tinh, giữa Sao Hoả và Sao Mộc?",
       en: "Which dwarf planet sits in the asteroid belt between Mars and Jupiter?" },
  opts: [
    { vi: "Ceres",
      en: "Ceres" },
    { vi: "Sao Diêm Vương (Pluto)",
      en: "Pluto" },
    { vi: "Eris",
      en: "Eris" },
    { vi: "Makemake",
      en: "Makemake" }
  ],
  a: 0,
  ok: { vi: "Đúng! <b>Ceres</b> là vật thể lớn nhất trong vành đai tiểu hành tinh và là hành tinh lùn duy nhất ở vùng trong hệ Mặt Trời. Bốn hành tinh lùn còn lại — Pluto, Haumea, Makemake, Eris — đều nằm xa hơn Sao Hải Vương.",
        en: "Correct! <b>Ceres</b> is the largest object in the asteroid belt and the only dwarf planet in the inner solar system. The other four — Pluto, Haumea, Makemake and Eris — all lie beyond Neptune." },
  no: { vi: "Chưa đúng! Đó là <b>Ceres</b>. Pluto, Haumea, Makemake và Eris đều ở xa hơn Sao Hải Vương, ngoài vành đai Kuiper.",
        en: "Not quite! It's <b>Ceres</b>. Pluto, Haumea, Makemake and Eris are all far beyond Neptune, out in the Kuiper Belt." },
  hint: { vi: "Nó là <b>vật thể lớn nhất</b> trong vành đai tiểu hành tinh — tàu Dawn của NASA đã bay tới đó.",
          en: "It's the <b>largest object</b> in the asteroid belt — NASA's Dawn spacecraft visited it." },
  src: "dwarf"
};
