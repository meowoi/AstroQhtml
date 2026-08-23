/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "solid-engine-propellant-mixed",
  topic: { vi: "ĐỘNG CƠ TÊN LỬA",
           en: "ROCKET ENGINES" },
  q: { vi: "Ở một động cơ tên lửa RẮN, nhiên liệu và chất oxy hoá được chứa thế nào?",
       en: "In a SOLID rocket engine, how are the fuel and oxidizer stored?" },
  opts: [
    { vi: "Chứa riêng trong hai bình rồi bơm vào",
      en: "Separately in two tanks, then pumped in" },
    { vi: "Chỉ có nhiên liệu, không có chất oxy hoá",
      en: "Only fuel, with no oxidizer at all" },
    { vi: "Trộn sẵn thành một khối thuốc phóng đóng trong một ống",
      en: "Mixed together into a solid propellant packed into a cylinder" },
    { vi: "Ở dạng khí nén trong một quả cầu",
      en: "As compressed gas inside a sphere" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! Ở động cơ rắn, hai thứ đã <b>trộn sẵn thành một khối thuốc phóng</b> đóng trong ống. Còn ở động cơ <b>lỏng</b> thì chúng chứa <b>riêng</b> rồi được <b>bơm</b> vào buồng đốt.",
        en: "Right! In a solid engine the two are <b>mixed into one solid propellant</b> packed in a cylinder. In a <b>liquid</b> engine they are stored <b>separately</b> and <b>pumped</b> into the chamber." },
  no: { vi: "Chưa đúng! Chứa riêng rồi bơm vào là <b>động cơ lỏng</b>. Động cơ <b>rắn</b> thì hai thứ đã trộn sẵn thành một khối.",
        en: "Not quite! Stored separately and pumped is the <b>liquid</b> engine. In a <b>solid</b> engine they are premixed into one block." },
  hint: { vi: "NASA chia động cơ tên lửa thành đúng hai loại chính. Khác nhau cơ bản nhất là ở chỗ hai thứ ấy gặp nhau lúc nào.",
          en: "NASA splits rocket engines into exactly two main kinds. The core difference is when those two things meet." },
  lv: 2,
  src: "modelSolidEngine",
  srcQuote: "In a solid rocket, the fuel and oxidizer are mixed together into a solid propellant which is packed into a solid cylinder.",
  srcChecked: "2026-08-22"
};
