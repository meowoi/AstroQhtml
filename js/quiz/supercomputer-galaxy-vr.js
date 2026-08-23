/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "supercomputer-galaxy-vr",
  topic: { vi: "BAY QUA TRUNG TÂM NGÂN HÀ",
           en: "FLYING THROUGH THE GALACTIC CENTRE" },
  q: { vi: "Hình ảnh hoá thực tế ảo của NASA cho bay quanh Sgr A* bao trùm một vùng rộng khoảng bao nhiêu?",
       en: "About how large a region does NASA's virtual-reality visualisation around Sgr A* cover?" },
  opts: [
    { vi: "Khoảng 3 ki-lô-mét",
      en: "About 3 kilometres" },
    { vi: "Khoảng 3 năm ánh sáng",
      en: "About 3 light years" },
    { vi: "Khoảng 3 nghìn năm ánh sáng",
      en: "About 3 thousand light years" },
    { vi: "Khoảng 3 triệu năm ánh sáng",
      en: "About 3 million light years" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA ghi: <b>hình ảnh hoá này bao trùm khoảng 3 năm ánh sáng, tức chừng 18 nghìn tỷ dặm, quanh Sgr A*</b> — cái lỗ đen khổng lồ ở trung tâm Ngân Hà. Đây là chỗ tin học gặp thiên văn: máy tính không chỉ trả ra con số, nó trả ra <b>một nơi bạn có thể đi vào</b>.",
       en: "Yes! NASA records that <b>the visualization covers about 3 light years, or about 18 trillion miles, around Sgr A*</b> - the supermassive black hole at the centre of the Milky Way. This is where computing meets astronomy: the machine returns not just numbers but <b>a place you can walk into</b>." },
  no: { vi: "Chưa đúng! Con số NASA đưa ra là <b>khoảng 3 năm ánh sáng</b> (chừng 18 nghìn tỷ dặm). Nghe nhỏ so với cả thiên hà, nhưng đó vẫn là một vùng không ai đi tới được — nên phải dựng nó bằng mô phỏng.",
       en: "Not quite! NASA's figure is <b>about 3 light years</b> (some 18 trillion miles). That sounds small next to a whole galaxy, but it is still a region nobody can visit - which is why it has to be simulated." },
  hint: { vi: "Năm ánh sáng là một KHOẢNG CÁCH. Con số này chỉ có một chữ số.",
         en: "A light year is a DISTANCE. This figure is a single digit." },
  lv: 2,
  src: "superComputing",
  srcQuote: "The visualization covers about 3 light years, or about 18 trillion miles, around Sgr A*.",
  srcChecked: "2026-08-23"
};
