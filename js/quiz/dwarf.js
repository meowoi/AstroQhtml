/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "dwarf",
  topic: { vi: "HÀNH TINH LÙN",
           en: "DWARF PLANET" },
  q: { vi: "Hành tinh lùn cũng quay quanh Mặt Trời và cũng gần tròn. Vậy nó THIẾU điều gì so với hành tinh?",
       en: "A dwarf planet orbits the Sun and is nearly round too. So what is it MISSING compared with a planet?" },
  opts: [
    { vi: "Nó không có vệ tinh nào",
      en: "It has no moons at all" },
    { vi: "Nó không tự quay quanh trục",
      en: "It doesn't spin on its axis" },
    { vi: "Nó chưa dọn sạch vùng quỹ đạo của mình",
      en: "It hasn't cleared its orbital neighbourhood" },
    { vi: "Nó không phải vật thể rắn",
      en: "It isn't a solid body" }
  ],
  a: 2,
  ok: { vi: "Chính xác! Hành tinh lùn <b>chưa dọn sạch vùng quỹ đạo</b> — quanh nó vẫn còn rất nhiều vật thể khác. Sao Diêm Vương chia sẻ vùng của mình với vô số vật thể ở vành đai Kuiper, dù bản thân nó vẫn có vệ tinh riêng.",
        en: "Exactly! A dwarf planet <b>hasn't cleared its orbit of debris</b> — plenty of other bodies still share its lane. Pluto shares its neighbourhood with countless Kuiper Belt objects, even though it does have moons of its own." },
  no: { vi: "Chưa đúng! Điều còn thiếu là <b>dọn sạch vùng quỹ đạo</b>. Hành tinh lùn vẫn có thể có vệ tinh và vẫn tự quay bình thường.",
        en: "Not quite! What's missing is <b>clearing the orbital neighbourhood</b>. A dwarf planet can still have moons and still spin normally." },
  hint: { vi: "Cùng một câu chuyện “dọn sân” — nhưng lần này là <b>chưa dọn xong</b>.",
          en: "Same “sweep the yard” story — except this time the yard <b>isn't swept</b>." },
  lv: 3,
  src: "dwarf"
};
