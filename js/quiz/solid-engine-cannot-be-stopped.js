/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "solid-engine-cannot-be-stopped",
  topic: { vi: "ĐỘNG CƠ TÊN LỬA",
           en: "ROCKET ENGINES" },
  q: { vi: "Theo NASA, muốn DỪNG một động cơ tên lửa rắn đang cháy thì phải làm gì?",
       en: "According to NASA, what must you do to STOP a burning solid rocket engine?" },
  opts: [
    { vi: "Đóng một cái van",
      en: "Close a valve" },
    { vi: "Ngắt dòng nhiên liệu",
      en: "Shut off the fuel flow" },
    { vi: "Bấm nút tắt trên bộ điều khiển",
      en: "Press the off switch on the controller" },
    { vi: "Phá vỏ động cơ",
      en: "Destroy the casing" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! NASA nói rõ: với động cơ rắn, <b>phải phá vỏ</b> mới dừng được. Ở động cơ lỏng thì chỉ cần <b>ngắt dòng</b> nhiên liệu hoặc chất oxy hoá — vì hai thứ đó còn chảy qua một cái bơm.",
        en: "Right! NASA is explicit: with a solid rocket you <b>must destroy the casing</b> to stop it. With a liquid rocket you simply <b>shut off the flow</b> of fuel or oxidizer - because those still pass through a pump." },
  no: { vi: "Chưa đúng! Không có van hay nút nào. Thuốc phóng đã trộn sẵn và nằm ngay trong vỏ, nên <b>một khi đã cháy thì nó cháy tới hết</b> — muốn dừng thì phải phá vỏ.",
        en: "Not quite! There is no valve or switch. The propellant is premixed and sits inside the casing, so <b>once lit it burns to the end</b> - stopping it means destroying the casing." },
  hint: { vi: "Ở động cơ lỏng, cái gì đứng giữa bình chứa và buồng đốt? Động cơ rắn có thứ đó không?",
          en: "In a liquid engine, what sits between the tanks and the chamber? Does a solid engine have one?" },
  lv: 3,
  src: "modelSolidEngine",
  srcQuote: "with a solid rocket, you must destroy the casing to stop the engine",
  srcChecked: "2026-08-22"
};
