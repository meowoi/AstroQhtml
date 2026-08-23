/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "rocket-thrust-in-vacuum",
  topic: { vi: "LỰC ĐẨY TÊN LỬA",
           en: "ROCKET THRUST" },
  q: { vi: "Vì sao một tên lửa vẫn sinh được lực đẩy trong chân không, nơi không có oxy?",
       en: "Why can a rocket still produce thrust in a vacuum, where there is no oxygen?" },
  opts: [
    { vi: "Vì nó đẩy vào ánh sáng Mặt Trời",
      en: "Because it pushes against sunlight" },
    { vi: "Vì chân không tự đẩy nó đi",
      en: "Because a vacuum pushes it along" },
    { vi: "Vì chất oxy hoá được mang sẵn trên tàu",
      en: "Because the oxidizer is carried onboard" },
    { vi: "Vì nó đẩy vào từ trường Trái Đất",
      en: "Because it pushes against Earth's magnetic field" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! <b>Chất oxy hoá được mang sẵn trên tàu</b>, nên tên lửa không cần mượn oxy từ không khí. Trong phương trình lực đẩy còn <b>không có số hạng nào cho không khí bên ngoài</b> — vì không có không khí nào được lấy vào.",
        en: "Right! The <b>oxidizer is carried onboard</b>, so a rocket borrows no oxygen from the air. The thrust equation has <b>no free-stream air term at all</b> - because no outside air is taken in." },
  no: { vi: "Chưa đúng! Tên lửa không đẩy vào thứ gì bên ngoài. Nó mang sẵn <b>chất oxy hoá</b>, nên đám cháy vẫn xảy ra ở nơi không có một phân tử không khí nào.",
        en: "Not quite! A rocket pushes against nothing outside. It carries its own <b>oxidizer</b>, so combustion still happens where there is no air at all." },
  hint: { vi: "Muốn cháy thì cần hai thứ: chất đốt và một chất cung cấp oxy. Cây nến trong phòng lấy oxy từ đâu?",
          en: "Burning needs two things: fuel and something to supply oxygen. Where does a candle get its oxygen?" },
  lv: 3,
  src: "rocketThrust",
  srcQuote: "Since the oxidizer is carried onboard the rocket, rockets can generate thrust in a vacuum where there is no other source of oxygen.",
  srcChecked: "2026-08-22"
};
