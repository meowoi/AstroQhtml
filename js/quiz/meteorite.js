/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteorite",
  topic: { vi: "THIÊN THẠCH",
           en: "METEORITE" },
  q: { vi: "Khi nào một hòn đá không gian được gọi là meteorite (thiên thạch)?",
       en: "When does a space rock earn the name meteorite?" },
  opts: [
    { vi: "Khi nó bắt đầu cháy trong khí quyển",
      en: "When it starts burning in the atmosphere" },
    { vi: "Khi nó bay ngang qua Mặt Trăng",
      en: "When it passes the Moon" },
    { vi: "Khi nó sống sót qua khí quyển và chạm tới mặt đất",
      en: "When it survives the atmosphere and reaches the ground" },
    { vi: "Khi nó lớn hơn 1 km",
      en: "When it is larger than 1 km" }
  ],
  a: 2,
  ok: { vi: "Chính xác! Meteoroid nào <b>sống sót qua khí quyển và rơi xuống đất</b> thì được gọi là <b>meteorite</b>. NASA cho biết phần lớn thiên thạch tìm được chỉ to bằng viên sỏi đến nắm tay.",
        en: "Exactly! A meteoroid that <b>survives its trip through the atmosphere and hits the ground</b> is a <b>meteorite</b>. NASA notes most are pebble to fist sized." },
  no: { vi: "Chưa đúng! Lúc còn đang cháy trên trời thì nó là <b>meteor</b>. Chỉ khi <b>chạm được mặt đất</b> nó mới là <b>meteorite</b>.",
        en: "Not quite! While it's still blazing overhead it's a <b>meteor</b>. Only once it <b>reaches the ground</b> is it a <b>meteorite</b>." },
  hint: { vi: "Đây là cái tên dành cho hòn đá mà con người có thể <b>cầm lên tay</b>.",
          en: "This is the name for the rock you could actually <b>pick up</b>." },
  lv: 2,
  src: "meteor"
};
